"""Sensibilidade à ordem das linhas. Roda em ~/painel_lote: python3 lote_ordem.py <id> [<id>…]"""
# Sensibilidade à ordem das linhas: roda cada seção com o resultado das consultas SEM
# ORDER BY embaralhado e compara com a rodada normal.
import json, os, random, re, sys
import duckdb
import extract_municipio as E
import extract_lote as L
from compara_json import igual
con = duckdb.connect(); con.execute(f"SET threads=6; SET memory_limit='4GB'; SET temp_directory='{os.path.expanduser('~/duckdb_tmp/ordem')}'; LOAD spatial")
MEMO = {}
def base(sql):
    if sql not in MEMO:
        try:
            cur = con.execute(sql); cols = [d[0] for d in cur.description]
            MEMO[sql] = [dict(zip(cols, map(L.norm, r))) for r in cur.fetchall()]
        except Exception as e:
            MEMO[sql] = RuntimeError(str(e)[-300:])
    r = MEMO[sql]
    if isinstance(r, Exception): raise r
    return r
def embaralha(sql):
    rows = base(sql)
    flat = L._plano(sql)
    if re.search(r"\border\s+by\b", flat, re.I): return rows
    rows = list(rows); random.Random(len(sql)).shuffle(rows); return rows
for mid in sys.argv[1:]:
    E.q = base
    prof = E.perfil(mid); ctx = E.contexto(mid, prof)
    sens = []
    for nome in E.SECOES:
        if nome in ("perfil", "geografia"): continue
        E.q = base; a = E.SECOES[nome](**E.args_secao(nome, ctx))
        E.q = embaralha; b = E.SECOES[nome](**E.args_secao(nome, ctx))
        if not igual(a, b): sens.append(nome)
    print(mid, "sensíveis à ordem:", sens)
