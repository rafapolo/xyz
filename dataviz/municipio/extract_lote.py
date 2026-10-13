#!/usr/bin/env python3
"""Painel municipal em lote: gera o JSON de todos os municípios de uma vez.

Roda NO beelink, ao lado do extract_municipio.py:
    python3 extract_lote.py                      # todas as seções, todos os municípios
    python3 extract_lote.py --so 3303401,2514107 # calcula o país, grava só esses dois
    python3 extract_lote.py --secoes saude_cnes --refaz

Não reescreve as seções. Cada seção do extract_municipio.py roda para todos os
municípios com um `q()` que não executa nada: devolve o que já está em cache ou
levanta `Falta(sql)`. As consultas que faltaram na rodada têm o mesmo molde e só
diferem nos literais (o código do município, o ano escolhido…); o molde vira uma
consulta só, com os literais numa tabela de parâmetros e `LATERAL`, e o DuckDB lê
cada tabela uma vez para o país inteiro. Repete até a seção fechar para todos.

O que não generaliza (erro de bind, tempo esgotado) cai para a execução uma a
uma, que é o método antigo sobre a mesma conexão. Fica registrado em log.jsonl.
"""
import argparse
import datetime as dt
import decimal
import json
import multiprocessing as mp
import os
import re
import sys
import threading
import time

import duckdb

import extract_municipio as E

BASE = os.path.expanduser("~/painel_lote")
LIT = re.compile(r"'(?:[^']|'')*'|(?<![\w.\"])\d+(?:\.\d+)?(?![\w.])")
DATA = re.compile(r"^'\d{4}-\d{2}-\d{2}'$")
MOMENTO = re.compile(r"^'\d{4}-\d{2}-\d{2}[ T]\d{2}:\d{2}:\d{2}(\.\d+)?'$")
# seções mais caras primeiro, para os workers não terminarem com uma só rodando
PESO = {"geografia": 99, "empresas_cnpj": 40, "saude_cnes": 38, "trabalho_rais": 36, "beneficios_inss": 24,
        "saude_internacoes": 22, "transp_compras_federais": 22, "beneficios": 21, "comex": 18, "saude_planos": 16,
        "politica": 13, "ambiente_car": 13, "saude_mortalidade": 11, "beneficios_programas_cgu": 11,
        "energia_continuidade": 30, "agro_assentamentos": 20, "trabalho_top_empregadores": 15,
        "trabalho_top_empregadores_publicos": 15, "educacao_sisu": 15, "educacao_enem": 12}


class Falta(BaseException):
    """Consulta ainda não resolvida. BaseException para atravessar o `except Exception`
    do decorador @section e dos try/except internos das seções."""

    def __init__(self, sql):
        self.sql = sql


class Erro:
    def __init__(self, msg):
        self.msg = msg


CON = None
CACHE = {}
MUNS = []
STATS = {}
CFG = {"timeout": 1500}


def conecta(threads, mem_gb, tmp):
    global CON
    os.makedirs(tmp, exist_ok=True)
    CON = duckdb.connect()
    CON.execute(f"SET threads={threads}; SET memory_limit='{mem_gb}GB'; SET temp_directory='{tmp}'; "
                "SET preserve_insertion_order=true; LOAD spatial")


def norm(v):
    """Mesmo valor que o `-json` do CLI entregava depois do json.loads."""
    if v is None or isinstance(v, (bool, int, str, float)):
        return v
    if isinstance(v, decimal.Decimal):
        return float(v)
    if isinstance(v, dt.datetime):
        return str(v)
    if isinstance(v, dt.date):
        return v.isoformat()
    if isinstance(v, (list, tuple)):
        return [norm(x) for x in v]
    if isinstance(v, dict):
        return {k: norm(x) for k, x in v.items()}
    return str(v)


def q_lote(sql):
    try:
        r = CACHE[sql]
    except KeyError:
        raise Falta(sql) from None
    if isinstance(r, Erro):
        raise RuntimeError(r.msg)
    return r


def executa(sql, timeout=None):
    """Roda no DuckDB com teto de tempo; devolve (colunas, linhas cruas)."""
    timer = threading.Timer(timeout or CFG["timeout"], CON.interrupt)
    timer.start()
    try:
        cur = CON.execute(sql)
        return [d[0] for d in cur.description], cur.fetchall()
    finally:
        timer.cancel()


def uma_a_uma(sqls):
    for sql in sqls:
        try:
            cols, rows = executa(sql, 600)
            CACHE[sql] = [dict(zip(cols, map(norm, r))) for r in rows]
        except Exception as e:  # noqa: BLE001
            CACHE[sql] = Erro(str(e).strip()[-500:])


# ------------------------------------------------------------- ORDER BY
def _plano(sql):
    """Cópia do SQL com tudo que está entre parênteses ou aspas trocado por 'x':
    o que sobra é o nível de cima, nas mesmas posições do original."""
    out, depth, i, n = [], 0, 0, len(sql)
    while i < n:
        ch = sql[i]
        if ch in "'\"":
            j = i + 1
            while True:
                j = sql.index(ch, j)
                if ch == "'" and sql[j + 1:j + 2] == "'":
                    j += 2
                    continue
                break
            out.append("x" * (j - i + 1))
            i = j + 1
            continue
        if ch == "(":
            depth += 1
            out.append("x")
        elif ch == ")":
            depth -= 1
            out.append("x")
        else:
            out.append(ch if depth == 0 else "x")
        i += 1
    return "".join(out)


def ordenacao(tmpl, insere_tudo):
    """Lê o ORDER BY final do molde. Devolve (molde com as chaves de ordenação
    acrescentadas como colunas _oN, [(chave, desc, nulos_primeiro)]), onde chave é
    um índice de coluna (posicional), um nome de coluna de saída ou '_oN'."""
    flat = _plano(tmpl)
    if re.search(r"\b(union|intersect|except)\b", flat, re.I):
        raise ValueError("operação de conjunto no nível de cima")
    ms = list(re.finditer(r"\border\s+by\b", flat, re.I))
    if not ms:
        return tmpl, []
    ini = ms[-1].end()
    fim = re.search(r"\b(limit|offset)\b", flat[ini:], re.I)
    fim = ini + fim.start() if fim else len(flat)
    cortes = [ini] + [ini + m.start() for m in re.finditer(",", flat[ini:fim])] + [fim]
    itens = [tmpl[a + (1 if k else 0):b] for k, (a, b) in enumerate(zip(cortes, cortes[1:]))]
    sels = [m for m in re.finditer(r"\bselect\b", flat, re.I) if m.start() < ms[-1].start()]
    lista_ini = sels[-1].end()
    frm = re.search(r"\bfrom\b", flat[lista_ini:], re.I)
    lista = tmpl[lista_ini:lista_ini + frm.start()] if frm else ""
    chaves, extras = [], []
    for it in itens:
        m = re.match(r"^\s*(.*?)(?:\s+(asc|desc))?(?:\s+nulls\s+(first|last))?\s*$", it, re.I | re.S)
        expr, desc, nulos = m.group(1), (m.group(2) or "").lower() == "desc", (m.group(3) or "last").lower() == "first"
        if expr.isdigit():
            chaves.append((int(expr) - 1, desc, nulos))
        elif (not insere_tudo and re.fullmatch(r"\w+", expr)
              and ("*" in _plano(lista) or re.search(rf"\b{expr}\b", lista, re.I))):
            chaves.append((expr.lower(), desc, nulos))
        else:
            nome = f"_o{len(extras)}"
            extras.append(f"{expr} AS {nome}")
            chaves.append((nome, desc, nulos))
    if extras:
        if not frm:
            raise ValueError("ORDER BY por expressão sem FROM no nível de cima")
        pos = lista_ini + frm.start()
        tmpl = tmpl[:pos] + ", " + ", ".join(extras) + " " + tmpl[pos:]
    return tmpl, chaves


def ordena(linhas, cols, chaves):
    """Reordena as linhas de um município como o ORDER BY do DuckDB faria
    (nulos por último, salvo NULLS FIRST). Estável, da última chave para a primeira."""
    nomes = [c.lower() for c in cols]
    for chave, desc, nulos_primeiro in reversed(chaves):
        i = chave if isinstance(chave, int) else nomes.index(chave)
        com = [r for r in linhas if r[i] is not None]
        sem = [r for r in linhas if r[i] is None]
        com.sort(key=lambda r: r[i], reverse=desc)
        linhas = sem + com if nulos_primeiro else com + sem
    return linhas


# ----------------------------------------------------------------- lote
def em_lote(sqls):
    """Resolve consultas de mesmo molde numa execução só. Levanta exceção se o
    molde não generaliza; quem chama cai para uma a uma."""
    toks = [LIT.findall(s) for s in sqls]
    var = [j for j in range(len(toks[0])) if any(t[j] != toks[0][j] for t in toks)]
    idx = {j: n for n, j in enumerate(var)}
    params, chave = {}, {}
    for s, t in zip(sqls, toks):
        tup = tuple(t[j] for j in var)
        chave[s] = params.setdefault(tup, len(params))
    vals = ", ".join("(" + ", ".join([str(k), *tup]) + ")" for tup, k in params.items())
    nomes = ", ".join(["_k"] + [f"a{n}" for n in range(len(var))])
    CON.execute(f"CREATE OR REPLACE TEMP TABLE _prm AS SELECT * FROM (VALUES {vals}) t({nomes})")

    def molde(com_data):
        pos = iter(range(len(toks[0])))

        def troca(m):
            j = next(pos)
            if j not in idx:
                return m.group(0)
            ref = f"_prm.a{idx[j]}"
            if com_data and all(DATA.match(t[j]) for t in toks):
                return f"CAST({ref} AS DATE)"
            if com_data and all(MOMENTO.match(t[j]) for t in toks):
                return f"CAST({ref} AS TIMESTAMP)"
            return ref
        return LIT.sub(troca, sqls[0])

    ultimo = None
    for com_data in (False, True):
        for insere_tudo in (False, True):
            try:
                tmpl, chaves = ordenacao(molde(com_data), insere_tudo)
                cols, rows = executa(f"SELECT _prm._k, _s.* FROM _prm, LATERAL ({tmpl}) _s")
                cols = cols[1:]
                por = {}
                for r in rows:
                    por.setdefault(r[0], []).append(r[1:])
                guarda = [i for i, c in enumerate(cols) if not re.fullmatch(r"_o\d+", c)]
                saida = {}
                for k, linhas in por.items():
                    if chaves:
                        linhas = ordena(linhas, cols, chaves)
                    saida[k] = [{cols[i]: norm(r[i]) for i in guarda} for r in linhas]
                for s in sqls:
                    CACHE[s] = saida.get(chave[s], [])
                return len(params)
            except duckdb.InterruptException:
                raise
            except Exception as e:  # noqa: BLE001
                ultimo = e
    raise ultimo


def resolve(sqls, stats):
    grupos = {}
    for s in sqls:
        grupos.setdefault(LIT.sub("?", s), []).append(s)
    for forma, grupo in grupos.items():
        t0 = time.time()
        if len(grupo) == 1:
            uma_a_uma(grupo)
            stats["unicas"] += 1
        else:
            try:
                em_lote(grupo)
                stats["lotes"] += 1
            except BaseException as e:  # noqa: BLE001
                if isinstance(e, (KeyboardInterrupt, SystemExit)):
                    raise
                uma_a_uma(grupo)
                stats["quedas"].append({"n": len(grupo), "s": round(time.time() - t0, 1),
                                        "erro": str(e)[:300], "sql": " ".join(grupo[0].split())[:400]})
        stats["lentas"].append((round(time.time() - t0, 1), len(grupo), " ".join(forma.split())[:160]))


def roda_secao(nome):
    """Calcula uma seção para todos os municípios e grava secoes/<nome>.jsonl,
    uma linha por município, na ordem de MUNS."""
    t0 = time.time()
    E.q = q_lote
    fn = E.SECOES[nome]
    stats = {"secao": nome, "lotes": 0, "unicas": 0, "quedas": [], "lentas": [], "rodadas": 0}
    res, pend = {}, list(MUNS)
    while pend:
        faltas, prox = {}, []
        for ctx in pend:
            try:
                res[ctx["mid"]] = fn(**E.args_secao(nome, ctx))
            except Falta as f:
                faltas[f.sql] = None
                prox.append(ctx)
        if faltas:
            stats["rodadas"] += 1
            resolve(list(faltas), stats)
        pend = prox
    CACHE.clear()
    E._ano_fechado.cache_clear()
    dest = os.path.join(BASE, "secoes", nome + ".jsonl")
    with open(dest + ".tmp", "w") as f:
        for ctx in MUNS:
            f.write(json.dumps(res[ctx["mid"]], ensure_ascii=False, default=str) + "\n")
    os.replace(dest + ".tmp", dest)
    stats["s"] = round(time.time() - t0, 1)
    stats["com_erro"] = sum(1 for v in res.values() if isinstance(v, dict) and "erro" in v)
    stats["lentas"] = sorted(stats["lentas"], reverse=True)[:4]
    return stats


def _init(muns, threads, mem, n):
    global MUNS
    MUNS = muns
    conecta(threads, mem, os.path.expanduser(f"~/duckdb_tmp/lote_{os.getpid()}"))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--secoes", help="só estas seções (vírgula)")
    ap.add_argument("--so", help="grava só estes municípios (o cálculo é sempre o país inteiro)")
    ap.add_argument("--refaz", action="store_true", help="recalcula seções que já têm arquivo")
    ap.add_argument("--workers", type=int, default=4)
    ap.add_argument("--threads", type=int, default=6)
    ap.add_argument("--mem", type=int, default=5, help="GB por worker")
    ap.add_argument("--out", default=os.path.join(BASE, "json"))
    ap.add_argument("--sem-montar", action="store_true")
    a = ap.parse_args()
    os.makedirs(os.path.join(BASE, "secoes"), exist_ok=True)
    os.makedirs(a.out, exist_ok=True)
    t0 = time.time()

    # perfil primeiro: é dele que saem uf, nome e código da Receita das outras seções
    global MUNS
    conecta(a.threads, a.mem, os.path.expanduser("~/duckdb_tmp/lote_main"))
    ids = [r[0] for r in CON.execute(
        f"SELECT DISTINCT id_municipio FROM {E.p('br_bd_diretorios_brasil', 'municipio')} ORDER BY 1").fetchall()]
    MUNS = [{"mid": i} for i in ids]
    st = roda_secao("perfil")
    print(f"perfil: {len(ids)} municípios em {st['s']} s", file=sys.stderr)
    with open(os.path.join(BASE, "secoes", "perfil.jsonl")) as f:
        perfis = [json.loads(l) for l in f]
    muns = [E.contexto(i, prof) for i, prof in zip(ids, perfis)]
    CON.close()  # os workers abrem a própria conexão depois do fork

    nomes = [n for n in E.SECOES if n != "perfil"]
    if a.secoes:
        nomes = [n for n in nomes if n in a.secoes.split(",")]
    fazer = [n for n in nomes if a.refaz or not os.path.exists(os.path.join(BASE, "secoes", n + ".jsonl"))]
    fazer.sort(key=lambda n: -PESO.get(n, 1))
    print(f"{len(fazer)} seções a calcular, {len(nomes) - len(fazer)} já prontas", file=sys.stderr)
    if fazer:
        with mp.get_context("fork").Pool(a.workers, _init, (muns, a.threads, a.mem, 0), maxtasksperchild=1) as pool, \
                open(os.path.join(BASE, "log.jsonl"), "a") as log:
            for st in pool.imap_unordered(roda_secao, fazer, chunksize=1):
                log.write(json.dumps(st, ensure_ascii=False) + "\n")
                log.flush()
                print(f"{st['secao']:36s} {st['s']:7.1f} s  rodadas={st['rodadas']:2d} lotes={st['lotes']:2d} "
                      f"quedas={len(st['quedas'])} erro={st['com_erro']}", file=sys.stderr)
                for qd in st["quedas"]:
                    print(f"    QUEDA n={qd['n']} {qd['s']} s: {qd['erro'][:160]} || {qd['sql'][:140]}", file=sys.stderr)
    print(f"seções prontas em {time.time() - t0:.0f} s", file=sys.stderr)
    if a.sem_montar:
        return

    # monta os documentos lendo as seções em paralelo, linha a linha
    so = set(a.so.split(",")) if a.so else None
    todas = [n for n in E.SECOES if n != "perfil"]
    arqs = {n: open(os.path.join(BASE, "secoes", n + ".jsonl")) for n in todas}
    indice, n_grav = [], 0
    for i, prof in zip(ids, perfis):
        linhas = {n: f.readline() for n, f in arqs.items()}
        indice.append({"id": i, "nome": prof.get("nome"), "uf": prof.get("sigla_uf")})
        if so and i not in so:
            continue
        doc = E.monta(prof, lambda nome: json.loads(linhas[nome]))
        dest = os.path.join(a.out, i + ".json")
        with open(dest + ".tmp", "w") as f:
            json.dump(doc, f, ensure_ascii=False, indent=1, default=str)
        os.replace(dest + ".tmp", dest)
        n_grav += 1
    with open(os.path.join(a.out, "municipios.json"), "w") as f:
        json.dump(indice, f, ensure_ascii=False, separators=(",", ":"))
    print(f"{n_grav} JSON gravados em {a.out}; total {time.time() - t0:.0f} s", file=sys.stderr)


if __name__ == "__main__":
    main()
