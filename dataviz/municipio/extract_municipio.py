#!/usr/bin/env python3
"""Extrai os data points do dashboard municipal a partir dos parquet locais
(basedosdados espelhada em ~/rodado) e emite um JSON por município.

Roda NO beelink:  python3 extract_municipio.py 3303401 > nova_friburgo.json
Do mac:           ./extract_municipio.sh 3303401 nova_friburgo

Cada seção é independente: falha vira {"erro": ...} sem derrubar o resto,
então municípios com cobertura parcial (ex.: ISP só existe para RJ) geram
JSON válido do mesmo jeito.
"""
import json
import os
import re
import subprocess
import sys
from datetime import date

DUCKDB = os.path.expanduser("~/bin/duckdb")
ROOT = os.path.expanduser("~/rodado")
SETTINGS = ("SET threads=8; SET memory_limit='20GB'; SET temp_directory='/dev/shm/duckdb_tmp'; "
            "INSTALL spatial; LOAD spatial; ")


def q(sql):
    """Executa SQL e devolve list[dict]."""
    out = subprocess.run(
        [DUCKDB, "-init", "/dev/null", "-json", "-c", SETTINGS + sql],
        capture_output=True, text=True, timeout=1800,
    )
    if out.returncode != 0:
        raise RuntimeError(out.stderr.strip()[-500:])
    body = out.stdout.strip()
    return json.loads(body) if body else []


def one(sql):
    rows = q(sql)
    return rows[0] if rows else None


def p(dataset, table):
    """Caminho read_parquet, ignorando restos tmp*/._* quando houver arquivo bom."""
    d = os.path.join(ROOT, dataset, table)
    files = [f for f in os.listdir(d) if f.endswith(".parquet") and not f.startswith("._")]
    good = [f for f in files if not f.startswith("tmp")]
    use = good if good else files
    if len(use) > 20:
        if use == files:
            return f"read_parquet('{d}/*.parquet')"
        if all(f.startswith("0") for f in use):
            return f"read_parquet('{d}/0*.parquet')"
    lst = ", ".join(f"'{os.path.join(d, f)}'" for f in sorted(use))
    return f"read_parquet([{lst}])"


def num(v):
    if v is None or isinstance(v, bool):
        return v
    if isinstance(v, float):
        return int(v) if v.is_integer() else v
    if isinstance(v, str):
        try:
            return int(v)
        except ValueError:
            try:
                return float(v)
            except ValueError:
                return v
    return v


MOJIBAKE = {"a£": "ã", "a§": "ç", "a©": "é", "a\u00ad": "í", "a³": "ó", "aª": "ê",
            "a¡": "á", "aº": "ú", "a¢": "â", "aµ": "õ", "a´": "ô", "a\u00a0": "à"}


def demojibake(txt):
    """Algumas fontes (ANS) gravam UTF-8 lido como latin-1 e depois sem acento:
    'Adesão' vira 'Adesa£o'. Desfaz o par a+símbolo."""
    if not isinstance(txt, str):
        return txt
    for ruim, bom in MOJIBAKE.items():
        txt = txt.replace(ruim, bom)
    return txt


def section(fn):
    """Decora seções: captura exceção como {'erro': ...}."""
    def wrap(*a, **k):
        try:
            return fn(*a, **k)
        except Exception as e:  # noqa: BLE001
            return {"erro": str(e)[:300]}
    return wrap


# -------------------------------------------------------------- geografia
@section
def geografia(mid):
    sede = one(f"""SELECT ano, ST_Y(ST_Centroid(geometria)) lat, ST_X(ST_Centroid(geometria)) lon
        FROM {p('br_geobr_mapas','sede_municipal')} WHERE id_municipio='{mid}' ORDER BY ano DESC LIMIT 1""")

    arranjo = one(f"SELECT arranjo_populacional, populacao_2010 FROM {p('br_geobr_mapas','arranjo_populacional')} WHERE id_municipio='{mid}'")
    semiarido_n = one(f"SELECT count(*) n FROM {p('br_geobr_mapas','semiarido')} WHERE id_municipio='{mid}'")["n"]
    rm = one(f"SELECT nome_regiao_metropolitana, tipo FROM {p('br_geobr_mapas','regiao_metropolitana_2017')} WHERE id_municipio='{mid}'")

    t_muni = p("br_geobr_mapas", "municipio")
    biomas = q(f"""
        WITH muni AS (SELECT geometria FROM {t_muni} WHERE id_municipio='{mid}')
        SELECT DISTINCT b.nome_bioma,
            ST_Area(ST_Intersection(b.geometria, muni.geometria)) / ST_Area(muni.geometria) * 100 pct
        FROM {p('br_geobr_mapas','bioma')} b, muni WHERE ST_Intersects(b.geometria, muni.geometria)
        ORDER BY 2 DESC""")

    ucs = q(f"""
        WITH muni AS (SELECT geometria FROM {t_muni} WHERE id_municipio='{mid}')
        SELECT uc.unidade_conservacao, uc.categoria, uc.esfera, uc.organizacao_orgao, uc.ano_criacao
        FROM {p('br_geobr_mapas','unidade_conservacao')} uc, muni WHERE ST_Intersects(uc.geometria, muni.geometria)
        ORDER BY uc.categoria, uc.unidade_conservacao""")
    por_cat = {}
    for r in ucs:
        k = (r["categoria"], r["esfera"])
        por_cat[k] = por_cat.get(k, 0) + 1
    resumo_ucs = sorted(
        [{"categoria": k[0], "esfera": k[1], "quantidade": v} for k, v in por_cat.items()],
        key=lambda r: -r["quantidade"])

    return {
        "fonte": "br_geobr_mapas (sede_municipal, arranjo_populacional, semiarido, regiao_metropolitana_2017, bioma, unidade_conservacao)",
        "sede_municipal": sede and {"ano": sede["ano"], "lat": sede["lat"], "lon": sede["lon"]},
        "arranjo_populacional": arranjo and {"nome": arranjo["arranjo_populacional"], "populacao_2010": num(arranjo["populacao_2010"])},
        "semiarido": semiarido_n > 0,
        "regiao_metropolitana": rm and {"nome": rm["nome_regiao_metropolitana"], "tipo": rm["tipo"]},
        "biomas": [{"nome": r["nome_bioma"], "pct_area": r["pct"]} for r in biomas],
        "unidades_conservacao": {"total": len(ucs), "por_categoria": resumo_ucs, "lista": ucs},
    }


# ---------------------------------------------------------------- perfil
@section
def perfil(mid):
    row = one(f"SELECT * FROM {p('br_bd_diretorios_brasil','municipio')} WHERE id_municipio='{mid}'")
    if not row:
        raise RuntimeError(f"município {mid} não encontrado no diretório")
    censo = one(f"SELECT area FROM {p('br_ibge_censo_2022','municipio')} WHERE id_municipio='{mid}'")
    return {
        "fonte": "br_bd_diretorios_brasil.municipio · br_ibge_censo_2022.municipio",
        "id_municipio": row["id_municipio"],
        "id_municipio_tse": row["id_municipio_tse"],
        "id_municipio_rf": row["id_municipio_rf"],
        "id_municipio_bcb": row["id_municipio_bcb"],
        "nome": row["nome"],
        "sigla_uf": row["sigla_uf"],
        "nome_uf": row["nome_uf"],
        "regiao": row["nome_regiao"],
        "mesorregiao": row["nome_mesorregiao"],
        "microrregiao": row["nome_microrregiao"],
        "regiao_imediata": row["nome_regiao_imediata"],
        "regiao_intermediaria": row["nome_regiao_intermediaria"],
        "regiao_metropolitana": row["nome_regiao_metropolitana"],
        "regiao_saude": row["nome_regiao_saude"],
        "id_comarca": row["id_comarca"],
        "ddd": row["ddd"],
        "capital_uf": bool(int(row["capital_uf"])) if row.get("capital_uf") is not None else None,
        "amazonia_legal": bool(int(row["amazonia_legal"])) if row.get("amazonia_legal") is not None else None,
        "area_km2": censo and censo.get("area"),
    }


# ------------------------------------------------------------ demografia
@section
def demografia(mid):
    serie = q(f"SELECT ano, populacao FROM {p('br_ibge_populacao','municipio')} WHERE id_municipio='{mid}' ORDER BY ano")
    censo = one(f"SELECT * FROM {p('br_ibge_censo_2022','municipio')} WHERE id_municipio='{mid}'")
    pir = q(f"""
        SELECT grupo_idade, sexo, sum(populacao) AS populacao
        FROM {p('br_ibge_censo_2022','populacao_grupo_idade_sexo_raca')}
        WHERE id_municipio='{mid}' GROUP BY 1,2""")
    ordem = ["0 a 4 anos","5 a 9 anos","10 a 14 anos","15 a 19 anos","20 a 24 anos","25 a 29 anos",
             "30 a 34 anos","35 a 39 anos","40 a 44 anos","45 a 49 anos","50 a 54 anos","55 a 59 anos",
             "60 a 64 anos","65 a 69 anos","70 a 74 anos","75 a 79 anos","80 a 84 anos","85 a 89 anos",
             "90 a 94 anos","95 a 99 anos","100 anos ou mais"]
    m = {(r["grupo_idade"], r["sexo"]): int(r["populacao"]) for r in pir}
    return {
        "fonte": "br_ibge_populacao.municipio · br_ibge_censo_2022",
        "populacao_serie": [{"ano": r["ano"], "populacao": r["populacao"]} for r in serie],
        "censo_2022": censo and {
            "populacao": censo["populacao"], "domicilios": censo["domicilios"],
            "area_km2": censo["area"], "taxa_alfabetizacao": censo["taxa_alfabetizacao"],
            "idade_mediana": censo["idade_mediana"], "razao_sexo": censo["razao_sexo"],
            "indice_envelhecimento": censo["indice_envelhecimento"],
        },
        "piramide_etaria_2022": {
            "grupos": ordem,
            "homens": [m.get((g, "Homens"), 0) for g in ordem],
            "mulheres": [m.get((g, "Mulheres"), 0) for g in ordem],
        },
    }


# -------------------------------------------------------------- economia
@section
def economia_pib(mid, uf):
    serie = q(f"SELECT * FROM {p('br_ibge_pib','municipio')} WHERE id_municipio='{mid}' ORDER BY ano DESC LIMIT 12")
    if not serie:
        raise RuntimeError("sem PIB")
    ano = serie[0]["ano"]
    pop = one(f"SELECT populacao FROM {p('br_ibge_populacao','municipio')} WHERE id_municipio='{mid}' AND ano={ano}")
    ref = one(f"""
        WITH pibs AS (
          SELECT d.sigla_uf, sum(m.pib) pib
          FROM {p('br_ibge_pib','municipio')} m
          JOIN {p('br_bd_diretorios_brasil','municipio')} d USING (id_municipio)
          WHERE m.ano={ano} GROUP BY 1)
        SELECT
          (SELECT sum(pib) FROM pibs) / (SELECT populacao FROM {p('br_ibge_populacao','brasil')} WHERE ano={ano}) AS pc_brasil,
          (SELECT pib FROM pibs WHERE sigla_uf='{uf}') / (SELECT populacao FROM {p('br_ibge_populacao','uf')} WHERE ano={ano} AND sigla_uf='{uf}') AS pc_uf""")
    rank = one(f"""
        WITH uf_pib AS (
          SELECT m.id_municipio, m.pib
          FROM {p('br_ibge_pib','municipio')} m
          JOIN {p('br_bd_diretorios_brasil','municipio')} d USING (id_municipio)
          WHERE m.ano={ano} AND d.sigla_uf='{uf}')
        SELECT count(*) AS pos, (SELECT count(*) FROM uf_pib) AS total
        FROM uf_pib WHERE pib >= (SELECT pib FROM uf_pib WHERE id_municipio='{mid}')""")
    return {
        "fonte": "br_ibge_pib.municipio",
        "serie": [{k: num(r[k]) for k in ("ano","pib","impostos_liquidos","va","va_agropecuaria","va_industria","va_servicos","va_adespss")} for r in reversed(serie)],
        "pib_per_capita": {"ano": ano, "valor": pop and serie[0]["pib"] / pop["populacao"],
                           "uf": ref and ref["pc_uf"], "brasil": ref and ref["pc_brasil"]},
        "ranking_uf": rank and {"posicao": rank["pos"], "total": rank["total"], "ano": ano},
    }


FUNCOES = ["Saúde","Educação","Administração","Urbanismo","Previdência Social","Assistência Social",
           "Segurança Pública","Saneamento","Transporte","Cultura","Gestão Ambiental","Desporto e Lazer",
           "Legislativa","Encargos Especiais","Agricultura","Habitação","Comércio e Serviços","Ciência e Tecnologia"]
CONTAS_RECEITA = {
    "total": "TOTAL DAS RECEITAS (III) = (I + II)",
    "receitas_correntes": "Receitas Correntes",
    "receitas_capital": "Receitas de Capital",
    "impostos": "Impostos",
    "fpm": "Cota-Parte do Fundo de Participação dos Municípios - FPM",
    "icms": "Cota-Parte do ICMS",
    "iptu": "Imposto sobre a Propriedade Predial e Territorial Urbana - IPTU",
    "iss": "Imposto sobre Serviços de Qualquer Natureza - ISSQN",
    "fundeb": "Transferências de Recursos do Fundo de Manutenção e Desenvolvimento da Educação Básica e de Valorização dos Profissionais da Educação - FUNDEB",
    "sus": "Transferências de Recursos do Sistema Único de Saúde - SUS",
}


@section
def economia_siconfi(mid):
    t_rec = p("br_me_siconfi", "municipio_receitas_orcamentarias")
    t_desp = p("br_me_siconfi", "municipio_despesas_funcao")
    ano = one(f"SELECT max(ano) a FROM {t_rec} WHERE id_municipio='{mid}'")["a"]
    contas = "', '".join(CONTAS_RECEITA.values())
    rec = q(f"""SELECT conta_bd, max(valor) valor FROM {t_rec}
        WHERE id_municipio='{mid}' AND ano={ano} AND estagio_bd='Receitas Brutas Realizadas'
        AND conta_bd IN ('{contas}') GROUP BY 1""")
    rec_map = {r["conta_bd"]: r["valor"] for r in rec}
    funcs = "', '".join(FUNCOES)
    desp = q(f"""SELECT conta_bd, sum(valor) valor FROM {t_desp}
        WHERE id_municipio='{mid}' AND ano={ano} AND estagio_bd='Despesas Empenhadas'
        AND conta_bd IN ('{funcs}') GROUP BY 1 ORDER BY 2 DESC""")
    total_desp = one(f"""SELECT sum(valor) v FROM {t_desp}
        WHERE id_municipio='{mid}' AND ano={ano} AND estagio_bd='Despesas Empenhadas'
        AND conta_bd IN ('Despesas Exceto Intraorçamentárias','Despesas Intraorçamentárias')""")
    return {
        "fonte": "br_me_siconfi", "ano": ano,
        "receitas": {k: rec_map.get(v) for k, v in CONTAS_RECEITA.items()},
        "despesas_funcao": [{"funcao": r["conta_bd"], "valor": r["valor"]} for r in desp],
        "despesas_total_empenhado": total_desp and total_desp["v"],
    }


@section
def economia_estban(mid):
    t = p("br_bcb_estban", "municipio")
    dic = q(f"SELECT chave, valor FROM {p('br_bcb_estban','dicionario')} WHERE nome_coluna='id_verbete'")
    def find(*terms):
        for r in dic:
            v = (r["valor"] or "").upper()
            if all(t in v for t in terms):
                return r["chave"]
        return None
    v_deps = [r["chave"] for r in dic if "DEP" in (r["valor"] or "").upper() and "SITO" in (r["valor"] or "").upper()]
    v_cred = find("OPERAÇÕES DE CRÉDITO") or find("OPERACOES DE CREDITO")
    am = one(f"SELECT max(ano*100+mes) am FROM {t} WHERE id_municipio='{mid}'")["am"]
    ano, mes = am // 100, am % 100
    def total(verbetes):
        if not verbetes:
            return None
        lst = "', '".join(verbetes)
        r = one(f"SELECT sum(valor) v FROM {t} WHERE id_municipio='{mid}' AND ano={ano} AND mes={mes} AND id_verbete IN ('{lst}')")
        return r and r["v"]
    ag = one(f"""SELECT sum(a) n FROM (
        SELECT max(agencias_processadas) a FROM {t}
        WHERE id_municipio='{mid}' AND ano={ano} AND mes={mes} GROUP BY cnpj_basico)""")
    return {"fonte": "br_bcb_estban", "ano": ano, "mes": mes,
            "agencias": ag and num(ag["n"]), "depositos_totais": total(v_deps),
            "operacoes_credito": total([v_cred] if v_cred else None),
            "verbetes": {"depositos": v_deps, "credito": v_cred}}


@section
def economia_inpc():
    r = one(f"SELECT * FROM {p('br_ibge_inpc','mes_brasil')} ORDER BY ano DESC, mes DESC LIMIT 1")
    return {"fonte": "br_ibge_inpc.mes_brasil (Brasil)", "ano": r["ano"], "mes": r["mes"],
            "variacao_mensal": r["variacao_mensal"], "variacao_anual": r["variacao_anual"],
            "variacao_doze_meses": r["variacao_doze_meses"]}


# -------------------------------------------------------------- educação
@section
def educacao_ideb(mid, uf):
    t = p("br_inep_ideb", "municipio")
    rows = q(f"""SELECT ano, anos_escolares, taxa_aprovacao, nota_saeb_media_padronizada, ideb, projecao
        FROM {t} WHERE id_municipio='{mid}' AND rede='publica' AND ensino='fundamental' ORDER BY ano""")
    out = {"fonte": "br_inep_ideb.municipio (rede pública)", "iniciais": [], "finais": []}
    for r in rows:
        key = "iniciais" if "iniciais" in r["anos_escolares"] else "finais"
        out[key].append({"ano": r["ano"], "ideb": r["ideb"], "meta": r["projecao"],
                         "taxa_aprovacao": r["taxa_aprovacao"]})
    for tbl, key in (("uf", "uf"), ("brasil", "brasil")):
        try:
            flt = f"sigla_uf='{uf}' AND" if key == "uf" else ""
            ref = q(f"""SELECT anos_escolares, ideb FROM {p('br_inep_ideb', tbl)}
                WHERE {flt} rede='publica' AND ensino='fundamental'
                AND ano=(SELECT max(ano) FROM {p('br_inep_ideb', tbl)})""")
            out[f"referencia_{key}"] = {("iniciais" if "iniciais" in r["anos_escolares"] else "finais"): r["ideb"] for r in ref}
        except Exception:  # noqa: BLE001
            pass
    return out


@section
def educacao_saeb(mid):
    t = p("br_inep_saeb", "municipio")
    ano = one(f"SELECT max(ano) a FROM {t} WHERE id_municipio='{mid}'")["a"]
    rows = q(f"""SELECT disciplina, serie, media,
            nivel_0, nivel_1, nivel_2, nivel_3, nivel_4, nivel_5, nivel_6, nivel_7, nivel_8, nivel_9, nivel_10
        FROM {t} WHERE id_municipio='{mid}' AND ano={ano}
        AND rede='total - estadual e municipal' AND localizacao='total' AND serie IN (5, 9)""")
    out = {"fonte": "br_inep_saeb.municipio (rede pública, total)", "ano": ano, "provas": []}
    for r in rows:
        niveis = [r[f"nivel_{i}"] for i in range(11)]
        niveis = [n for n in niveis if n is not None]
        out["provas"].append({"disciplina": r["disciplina"], "serie": r["serie"],
                              "media": r["media"], "distribuicao_niveis_pct": niveis})
    return out


@section
def educacao_indicadores(mid):
    t = p("br_inep_indicadores_educacionais", "municipio")
    ano = one(f"SELECT max(ano) a FROM {t} WHERE id_municipio='{mid}'")["a"]
    row = one(f"""SELECT * FROM {t} WHERE id_municipio='{mid}' AND ano={ano}
        AND localizacao='total' AND rede IN ('publica','total') ORDER BY rede DESC LIMIT 1""")
    ev = one(f"""SELECT taxa_evasao_ef, taxa_evasao_em FROM {p('br_inep_indicadores_educacionais','municipio_taxa_transicao')}
        WHERE id_municipio='{mid}' AND localizacao='total' AND rede IN ('publica','total')
        ORDER BY ano DESC LIMIT 1""")
    keys = ["atu_ei_creche", "atu_ei_pre_escola", "atu_ef_anos_iniciais", "atu_ef_anos_finais", "atu_em"]
    return {"fonte": "br_inep_indicadores_educacionais.municipio", "ano": ano, "rede": row and row["rede"],
            "alunos_por_turma": row and {k: row.get(k) for k in keys},
            "taxa_evasao_ef": ev and ev.get("taxa_evasao_ef"), "taxa_evasao_em": ev and ev.get("taxa_evasao_em")}


@section
def educacao_enem(mid):
    t = p("br_inep_enem", "microdados")
    ano = one(f"SELECT max(ano) a FROM {t}")["a"]
    r = one(f"""SELECT count(*) inscritos, count(nota_matematica) presentes,
            avg(nota_redacao) redacao, avg(nota_linguagens_codigos) linguagens,
            avg(nota_matematica) matematica, avg(nota_ciencias_humanas) humanas,
            avg(nota_ciencias_natureza) natureza,
            avg((nota_linguagens_codigos+nota_matematica+nota_ciencias_humanas+nota_ciencias_natureza+nota_redacao)/5) media_geral
        FROM {t} WHERE ano={ano} AND id_municipio_prova='{mid}'""")
    return {"fonte": "br_inep_enem.microdados (local de prova)", "ano": ano, **{k: num(r[k]) for k in r}}


# ----------------------------------------------------------------- saúde
@section
def saude_cnes(mid):
    am = one(f"SELECT max(ano*100+mes) am FROM {p('br_ms_cnes','estabelecimento')} WHERE id_municipio='{mid}'")["am"]
    ano, mes = am // 100, am % 100
    est = one(f"SELECT count(DISTINCT id_estabelecimento_cnes) n FROM {p('br_ms_cnes','estabelecimento')} WHERE id_municipio='{mid}' AND ano={ano} AND mes={mes}")
    lam = one(f"SELECT max(ano*100+mes) am FROM {p('br_ms_cnes','leito')} WHERE id_municipio='{mid}'")["am"]
    leito = one(f"SELECT sum(quantidade_total) n, sum(quantidade_sus) sus FROM {p('br_ms_cnes','leito')} WHERE id_municipio='{mid}' AND ano={lam//100} AND mes={lam%100}")
    pam = one(f"SELECT max(ano*100+mes) am FROM {p('br_ms_cnes','profissional')} WHERE id_municipio='{mid}'")["am"]
    prof = one(f"SELECT count(*) vinculos FROM {p('br_ms_cnes','profissional')} WHERE id_municipio='{mid}' AND ano={pam//100} AND mes={pam%100}")
    eam = one(f"SELECT max(ano*100+mes) am FROM {p('br_ms_cnes','equipe')} WHERE id_municipio='{mid}'")["am"]
    eq = one(f"SELECT count(*) n FROM {p('br_ms_cnes','equipe')} WHERE id_municipio='{mid}' AND ano={eam//100} AND mes={eam%100}")
    return {"fonte": "br_ms_cnes", "competencia": f"{ano}-{mes:02d}",
            "estabelecimentos": est and est["n"],
            "leitos": leito and {"competencia": f"{lam//100}-{lam%100:02d}", "total": num(leito["n"]), "sus": num(leito["sus"])},
            "profissionais": prof and {"competencia": f"{pam//100}-{pam%100:02d}", "vinculos": num(prof["vinculos"])},
            "equipes": eq and {"competencia": f"{eam//100}-{eam%100:02d}", "total": eq["n"]}}


@section
def saude_sinasc(mid):
    t = p("br_ms_sinasc", "microdados")
    anos = q(f"SELECT ano, count(*) n FROM {t} WHERE id_municipio_residencia='{mid}' GROUP BY 1 ORDER BY 1 DESC LIMIT 3")
    ano = anos[0]["ano"]
    if len(anos) > 1 and int(anos[0]["n"]) < 0.7 * int(anos[1]["n"]):
        ano = anos[1]["ano"]  # último ano parece parcial; usa o anterior
    dist = q(f"SELECT tipo_parto, count(*) n FROM {t} WHERE id_municipio_residencia='{mid}' AND ano={ano} GROUP BY 1")
    pre = q(f"SELECT pre_natal_agr, count(*) n FROM {t} WHERE id_municipio_residencia='{mid}' AND ano={ano} GROUP BY 1")
    r = one(f"""SELECT count(*) total,
            sum(CASE WHEN try_cast(peso AS DOUBLE) < 2500 THEN 1 ELSE 0 END) baixo_peso
        FROM {t} WHERE id_municipio_residencia='{mid}' AND ano={ano}""")
    total = int(r["total"] or 0)
    baixo = int(r["baixo_peso"] or 0)
    ces = sum(int(d["n"]) for d in dist if d["tipo_parto"] and ("2" == str(d["tipo_parto"]) or "ces" in str(d["tipo_parto"]).lower()))
    return {"fonte": "br_ms_sinasc.microdados (residência)", "ano": ano, "nascidos_vivos": total,
            "pct_cesareo": ces / total * 100 if total else None,
            "pct_baixo_peso": baixo / total * 100 if total else None,
            "pre_natal_distribuicao": {str(d["pre_natal_agr"]): d["n"] for d in pre}}


@section
def saude_dengue(mid):
    t = p("br_ms_sinan", "microdados_dengue")
    ano = one(f"SELECT max(ano) a FROM {t} WHERE id_municipio_residencia='{mid}'")["a"]
    cls = q(f"""SELECT classificacao_final, evolucao_caso, count(*) n FROM {t}
        WHERE id_municipio_residencia='{mid}' AND ano={ano} GROUP BY 1,2""")
    prev = one(f"SELECT count(*) n FROM {t} WHERE id_municipio_residencia='{mid}' AND ano={ano-1}")
    total = sum(r["n"] for r in cls)
    def is_conf(v):
        s = str(v or "").lower()
        return v is not None and "descart" not in s and s not in ("", "none", "8")
    confirmados = sum(r["n"] for r in cls if is_conf(r["classificacao_final"]))
    graves = sum(r["n"] for r in cls if str(r["classificacao_final"] or "") in ("11", "12") or "grave" in str(r["classificacao_final"] or "").lower())
    obitos = sum(r["n"] for r in cls if str(r["evolucao_caso"] or "") == "2" or "óbito pelo agravo" in str(r["evolucao_caso"] or "").lower())
    return {"fonte": "br_ms_sinan.microdados_dengue (residência)", "ano": ano,
            "notificados": total, "confirmados": confirmados, "graves": graves, "obitos": obitos,
            "notificados_ano_anterior": prev and prev["n"],
            "classificacao_bruta": {f"{r['classificacao_final']}|{r['evolucao_caso']}": r["n"] for r in cls}}


@section
def saude_sisvan(mid):
    t = p("br_ms_sisvan", "microdados")
    ano = one(f"SELECT max(ano) a FROM {t} WHERE id_municipio='{mid}'")["a"]
    rows = q(f"""SELECT estado_nutricional_peso_idade_crianca e_peso, estado_nutricional_imc_idade_crianca e_imc, count(*) n
        FROM {t} WHERE id_municipio='{mid}' AND ano={ano} AND fase_vida ILIKE '%crian%' GROUP BY 1,2""")
    total = sum(r["n"] for r in rows)
    baixo = sum(r["n"] for r in rows if "baixo" in str(r["e_peso"] or "").lower())
    excesso = sum(r["n"] for r in rows if any(k in str(r["e_imc"] or "").lower() for k in ("obesidade", "sobrepeso", "elevado")))
    return {"fonte": "br_ms_sisvan.microdados (crianças acompanhadas)", "ano": ano,
            "criancas_acompanhadas": total,
            "pct_baixo_peso": baixo / total * 100 if total else None,
            "pct_excesso_peso": excesso / total * 100 if total else None}


# -------------------------------------------------------------- segurança
@section
def seguranca_isp(mid, uf):
    if uf != "RJ":
        return {"disponivel": False, "motivo": "ISP cobre apenas municípios do RJ"}
    t_tax = p("br_rj_isp_estatisticas_seguranca", "taxa_evolucao_anual_municipio")
    t_mes = p("br_rj_isp_estatisticas_seguranca", "evolucao_mensal_municipio")
    ano = one(f"SELECT max(ano) a FROM {t_mes} WHERE id_municipio='{mid}' AND mes=12")["a"]
    ano_tax = one(f"SELECT max(ano) a FROM {t_tax} WHERE id_municipio='{mid}'")["a"]
    taxas = one(f"SELECT * FROM {t_tax} WHERE id_municipio='{mid}' AND ano={ano_tax}")
    taxas_uf = one(f"SELECT * FROM {p('br_rj_isp_estatisticas_seguranca','taxa_evolucao_anual_uf')} WHERE ano={ano_tax}")
    tot = one(f"""SELECT sum(quantidade_homicidio_doloso) homicidio_doloso,
            sum(quantidade_letalidade_violenta) letalidade_violenta,
            sum(quantidade_crimes_violentos_letais_intencionais) cvli,
            sum(quantidade_latrocinio) latrocinio,
            sum(quantidade_lesao_corporal_morte) lesao_corporal_morte,
            sum(quantidade_tentativa_homicidio) tentativa_homicidio,
            sum(quantidade_homicidio_intervencao_policial) intervencao_policial,
            sum(quantidade_estupro) estupro, sum(quantidade_roubo_veiculo) roubo_veiculo
        FROM {t_mes} WHERE id_municipio='{mid}' AND ano={ano}""")
    tot_prev = one(f"SELECT sum(quantidade_homicidio_doloso) h FROM {t_mes} WHERE id_municipio='{mid}' AND ano={ano-1}")
    mensal = q(f"""SELECT mes, quantidade_homicidio_doloso h, quantidade_letalidade_violenta lv
        FROM {t_mes} WHERE id_municipio='{mid}' AND ano={ano} ORDER BY mes""")
    keys = ["taxa_homicidio_doloso", "taxa_latrocinio", "taxa_lesao_corporal_morte", "taxa_letalidade_violenta",
            "taxa_tentativa_homicidio", "taxa_estupro", "taxa_roubo_veiculo", "taxa_homicidio_intervencao_policial"]
    return {"fonte": "br_rj_isp_estatisticas_seguranca", "ano": ano,
            "ocorrencias": {k: num(v) for k, v in (tot or {}).items()},
            "homicidio_doloso_ano_anterior": tot_prev and num(tot_prev["h"]),
            "taxas_100k": taxas and {"ano": ano_tax, **{k: taxas.get(k) for k in keys}},
            "taxas_100k_uf": taxas_uf and {"ano": ano_tax, **{k: taxas_uf.get(k) for k in keys}},
            "mensal": [{"mes": r["mes"], "homicidio_doloso": num(r["h"]), "letalidade_violenta": num(r["lv"])} for r in mensal]}


@section
def seguranca_fbsp(mid):
    t = p("br_fbsp_absp", "municipio")
    ano = one(f"SELECT max(ano) a FROM {t} WHERE id_municipio='{mid}'")["a"]
    if ano is None:
        return {"disponivel": False, "motivo": "município fora da amostra do anuário FBSP"}
    row = one(f"SELECT * FROM {t} WHERE id_municipio='{mid}' AND ano={ano}")
    keep = {k: num(v) for k, v in row.items() if k.startswith(("quantidade_", "proporcao_")) and v is not None}
    return {"fonte": "br_fbsp_absp.municipio", "ano": ano, **keep}


# ---------------------------------------------------------- infraestrutura
@section
def infra_snis(mid):
    t = p("br_mdr_snis", "municipio_agua_esgoto")
    ano = one(f"SELECT max(ano) a FROM {t} WHERE id_municipio='{mid}'")["a"]
    r = one(f"""SELECT ano, populacao_atendida_agua, populacao_atentida_esgoto,
            indice_atendimento_total_agua, indice_atendimento_urbano_agua,
            indice_coleta_esgoto, indice_tratamento_esgoto, indice_atendimento_esgoto_esgoto,
            indice_perda_distribuicao_agua, extensao_rede_agua, extensao_rede_esgoto,
            volume_agua_consumido, volume_esgoto_coletado, volume_esgoto_tratado, despesa_total_servico
        FROM {t} WHERE id_municipio='{mid}' AND ano={ano}""")
    prev = one(f"""SELECT indice_atendimento_total_agua a, indice_coleta_esgoto c, indice_tratamento_esgoto t
        FROM {t} WHERE id_municipio='{mid}' AND ano={ano-1}""")
    return {"fonte": "br_mdr_snis.municipio_agua_esgoto", **{k: num(v) for k, v in r.items()},
            "ano_anterior": prev and {k: num(v) for k, v in prev.items()}}


@section
def infra_ana(mid):
    r = one(f"""SELECT populacao_urbana_2013, populacao_urbana_2035, prestador_servico_esgotamento_sanitario,
            indice_sem_atendimento_sem_coleta_sem_tratamento, indice_atendimento_solucao_individual,
            indice_atendimento_com_coleta_sem_tratamento, indice_atendimento_com_coleta_com_tratamento,
            investimento_coleta, investimento_tratamento, investimento_coleta_tratatamento
        FROM {p('br_ana_atlas_esgotos','municipio')} WHERE id_municipio='{mid}'""")
    return {"fonte": "br_ana_atlas_esgotos.municipio", "ano_referencia": 2013, **{k: num(v) for k, v in r.items()}}


# ------------------------------------------------------------ meio ambiente
@section
def ambiente_prodes(mid):
    t = p("br_inpe_prodes", "municipio_bioma")
    rows = q(f"SELECT ano, bioma, area_total, desmatado, vegetacao_natural FROM {t} WHERE id_municipio='{mid}' ORDER BY ano DESC, bioma")
    if not rows:
        raise RuntimeError("sem PRODES")
    ultimo_ano = rows[0]["ano"]
    biomas_recentes = [r for r in rows if r["ano"] >= ultimo_ano - 1]
    # série anual (bioma dominante por área, para municípios com mais de um bioma)
    por_ano = {}
    for r in rows:
        cur = por_ano.get(r["ano"])
        if cur is None or (r["area_total"] or 0) > (cur["area_total"] or 0):
            por_ano[r["ano"]] = r
    serie = [por_ano[a] for a in sorted(por_ano)]
    return {"fonte": "br_inpe_prodes.municipio_bioma", "biomas": biomas_recentes, "serie": serie}


@section
def ambiente_queimadas(mid):
    t = p("br_inpe_queimadas", "microdados")
    rows = q(f"""SELECT ano, count(*) focos, avg(potencia_radiativa_fogo) frp_medio, max(potencia_radiativa_fogo) frp_max
        FROM {t} WHERE id_municipio='{mid}' GROUP BY 1 ORDER BY 1""")
    return {"fonte": "br_inpe_queimadas.microdados",
            "serie": [{"ano": r["ano"], "focos": num(r["focos"]), "frp_medio": r["frp_medio"], "frp_max": r["frp_max"]} for r in rows]}


@section
def ambiente_sisam(mid):
    t = p("br_inpe_sisam", "microdados")
    rows = q(f"""SELECT extract(year FROM data_hora) AS ano, avg(pm25_ugm3) pm25, avg(co_ppb) co
        FROM {t} WHERE id_municipio='{mid}' GROUP BY 1 ORDER BY 1""")
    return {"fonte": "br_inpe_sisam.microdados",
            "serie": [{"ano": num(r["ano"]), "pm25_ugm3": r["pm25"], "co_ppb": r["co"]} for r in rows]}


@section
def ambiente_mapbiomas(mid):
    t = p("br_mapbiomas_estatisticas", "transicao_municipio_de_para_decenal")
    tc = p("br_mapbiomas_estatisticas", "classe")
    rows = q(f"""
        WITH tr AS (
          SELECT ano, id_classe_de, id_classe_para, sum(area) area
          FROM {t} WHERE id_municipio='{mid}' AND ano IN (2010, 2020) AND id_classe_de != id_classe_para
          GROUP BY 1, 2, 3)
        SELECT tr.ano, cde.valor_pt de, cpa.valor_pt para, tr.area
        FROM tr
        LEFT JOIN {tc} cde ON cde.chave = tr.id_classe_de
        LEFT JOIN {tc} cpa ON cpa.chave = tr.id_classe_para
        ORDER BY tr.ano, tr.area DESC""")

    def clean(nome):
        return re.sub(r"^[\d.]+\s*", "", nome) if nome else nome

    por_ano = {}
    for r in rows:
        por_ano.setdefault(r["ano"], []).append(r)
    top_chaves, seen = [], set()
    for ano in (2010, 2020):
        for r in por_ano.get(ano, [])[:6]:
            k = (r["de"], r["para"])
            if k not in seen:
                seen.add(k)
                top_chaves.append(k)

    def valor(ano, de, para):
        return next((r["area"] for r in por_ano.get(ano, []) if r["de"] == de and r["para"] == para), 0)

    transicoes = [{"de": clean(de), "para": clean(para),
                   "area_2010": valor(2010, de, para), "area_2020": valor(2020, de, para)}
                  for de, para in top_chaves[:6]]
    return {"fonte": "br_mapbiomas_estatisticas.transicao_municipio_de_para_decenal", "anos": [2010, 2020], "transicoes": transicoes}


@section
def ambiente_seeg(mid):
    base = os.path.join(ROOT, "br_seeg_emissoes")
    dic = {}
    if os.path.isdir(os.path.join(base, "dicionario")):
        rows = q(f"SELECT * FROM {p('br_seeg_emissoes','dicionario')}")
        if rows:
            ks = rows[0].keys()
            col = next((k for k in ks if "coluna" in k), None)
            chave = next((k for k in ks if "chave" in k), None)
            val = next((k for k in ks if k == "valor"), None)
            if col and chave and val:
                for r in rows:
                    dic.setdefault(r[col], {})[str(r[chave])] = r[val]
    t = p("br_seeg_emissoes", "municipio")
    ano = one(f"SELECT max(ano) a FROM {t} WHERE id_municipio='{mid}'")["a"]
    gas_map = dic.get("gas", {})
    gas_code = next((k for k, v in gas_map.items() if "co2e" in str(v).lower() and ("ar5" in str(v).lower() or "gwp" in str(v).lower())), None)
    tipo_map = dic.get("tipo", {})
    tipo_code = next((k for k, v in tipo_map.items() if str(v).lower().startswith("emiss")), None)
    flt = f"AND gas='{gas_code}'" if gas_code else ""
    flt += f" AND tipo='{tipo_code}'" if tipo_code else ""
    rows = q(f"""SELECT setor, sum(coalesce(emissao_ar5, emissao_ar6, emissao_ar4, emissao_ar2)) emissao
        FROM {t} WHERE id_municipio='{mid}' AND ano={ano} {flt} GROUP BY 1 ORDER BY 2 DESC""")
    setor_map = dic.get("setor", {})
    return {"fonte": "br_seeg_emissoes.municipio", "ano": ano,
            "gas": gas_map.get(gas_code, gas_code), "tipo": tipo_map.get(tipo_code, tipo_code),
            "por_setor": [{"setor": setor_map.get(str(r["setor"]), str(r["setor"])), "emissao_tco2e": r["emissao"]} for r in rows],
            "total_tco2e": sum(r["emissao"] or 0 for r in rows)}


# ------------------------------------------------------------ conectividade
@section
def conectividade(mid):
    t = p("br_anatel_banda_larga_fixa", "densidade_municipio")
    am = one(f"SELECT max(ano*100+mes) am FROM {t} WHERE id_municipio='{mid}'")["am"]
    dens = one(f"SELECT densidade FROM {t} WHERE id_municipio='{mid}' AND ano={am//100} AND mes={am%100}")
    dens_br = one(f"""SELECT densidade FROM {p('br_anatel_banda_larga_fixa','densidade_brasil')}
        WHERE ano={am//100} AND mes={am%100}""")
    t2 = p("br_anatel_indice_brasileiro_conectividade", "municipio")
    ibc = one(f"SELECT * FROM {t2} WHERE id_municipio='{mid}' ORDER BY ano DESC LIMIT 1")
    ibc_med = ibc and one(f"SELECT avg(ibc) m FROM {t2} WHERE ano={ibc['ano']}")
    return {"fonte": "br_anatel_banda_larga_fixa · br_anatel_indice_brasileiro_conectividade",
            "banda_larga": {"competencia": f"{am//100}-{am%100:02d}", "densidade_100hab": dens and dens["densidade"],
                            "densidade_brasil": dens_br and dens_br["densidade"]},
            "ibc": ibc and {"ano": ibc["ano"], "ibc": ibc["ibc"], "media_brasil": ibc_med and ibc_med["m"],
                            "cobertura_pop_4g5g": ibc.get("cobertura_pop_4g5g"), "fibra": ibc.get("fibra")}}


# ---------------------------------------------------------------- política
@section
def politica(mid):
    t_perf = p("br_tse_eleicoes", "perfil_eleitorado_municipio_zona")
    ano = one(f"SELECT max(ano) a FROM {t_perf} WHERE id_municipio='{mid}'")["a"]
    tot = one(f"""SELECT sum(try_cast(eleitores AS BIGINT)) eleitores, sum(try_cast(eleitores_biometria AS BIGINT)) biometria,
            count(DISTINCT zona) zonas FROM {t_perf} WHERE id_municipio='{mid}' AND ano={ano}""")
    gen = q(f"SELECT genero, sum(try_cast(eleitores AS BIGINT)) n FROM {t_perf} WHERE id_municipio='{mid}' AND ano={ano} GROUP BY 1")
    ins = q(f"SELECT instrucao, sum(try_cast(eleitores AS BIGINT)) n FROM {t_perf} WHERE id_municipio='{mid}' AND ano={ano} GROUP BY 1 ORDER BY 2 DESC")
    det = one(f"""SELECT * FROM {p('br_tse_eleicoes','detalhes_votacao_municipio')}
        WHERE id_municipio='{mid}' AND ano={ano} AND cargo='prefeito' AND turno=(
          SELECT max(turno) FROM {p('br_tse_eleicoes','detalhes_votacao_municipio')} WHERE id_municipio='{mid}' AND ano={ano} AND cargo='prefeito')""")
    win = one(f"""SELECT r.sigla_partido, r.votos, r.turno, c.nome_urna
        FROM {p('br_tse_eleicoes','resultados_candidato_municipio')} r
        LEFT JOIN {p('br_tse_eleicoes','candidatos')} c
          ON c.ano=r.ano AND c.sequencial=r.sequencial_candidato AND c.sigla_uf=r.sigla_uf
        WHERE r.id_municipio='{mid}' AND r.ano={ano} AND r.cargo='prefeito' AND r.resultado LIKE 'eleito%'
        ORDER BY r.turno DESC LIMIT 1""")
    return {"fonte": "br_tse_eleicoes", "ano": ano,
            "eleitorado": tot and {"aptos": num(tot["eleitores"]), "biometria": num(tot["biometria"]), "zonas": tot["zonas"]},
            "genero": {r["genero"]: num(r["n"]) for r in gen},
            "instrucao": {r["instrucao"]: num(r["n"]) for r in ins},
            "prefeito": det and {
                "turno": det["turno"], "aptos": num(det["aptos"]), "secoes": num(det["secoes"]),
                "comparecimento": num(det["comparecimento"]), "abstencoes": num(det["abstencoes"]),
                "votos_nominais": num(det["votos_nominais"]), "votos_brancos": num(det["votos_brancos"]),
                "votos_nulos": num(det["votos_nulos"]),
                "eleito": win and {"nome_urna": win["nome_urna"], "partido": win["sigla_partido"],
                                    "votos": num(win["votos"]), "turno": win["turno"]}}}


# ------------------------------------------------------------ transparência
@section
def transparencia(mid):
    ebt = q(f"SELECT ano, nota, ranking FROM {p('br_cgu_ebt','municipio')} WHERE id_municipio='{mid}' ORDER BY ano")
    t = p("br_clp_ranking_competitividade", "nota_geral_municipio")
    ano = one(f"SELECT max(ano) a FROM {t} WHERE id_municipio='{mid}'")
    clp = ano and q(f"SELECT pilar_dimensao, nota_geral, colocacao FROM {t} WHERE id_municipio='{mid}' AND ano={ano['a']} ORDER BY pilar_dimensao")
    return {"fonte": "br_cgu_ebt.municipio · br_clp_ranking_competitividade",
            "ebt": [{k: num(r[k]) for k in ("ano", "nota", "ranking")} for r in ebt],
            "clp": ano and {"ano": ano["a"], "pilares": clp}}


# ---------------------------------------------------------------- social
@section
def social(mid):
    row = one(f"""SELECT * FROM {p('br_ipea_avs','municipio')} WHERE id_municipio='{mid}'
        AND raca_cor='total' AND sexo='total' AND localizacao='total' ORDER BY ano DESC LIMIT 1""")
    oca = one(f"SELECT * FROM {p('br_abrinq_oca','municipio_primeira_infancia')} WHERE id_municipio='{mid}' ORDER BY ano DESC LIMIT 1")
    return {"fonte": "br_ipea_avs.municipio · br_abrinq_oca",
            "avs": row and {"ano": row["ano"], "ivs": row["ivs"],
                            "ivs_infraestrutura_urbana": row["ivs_infraestrutura_urbana"],
                            "ivs_capital_humano": row["ivs_capital_humano"],
                            "ivs_renda_trabalho": row["ivs_renda_trabalho"],
                            "idhm": row["idhm"], "idhm_longevidade": row["idhm_l"],
                            "idhm_educacao": row["idhm_e"], "idhm_renda": row["idhm_r"]},
            "primeira_infancia": oca and {"ano": oca["ano"],
                                          "taxa_bruta_pre_escola": oca["taxa_bruta_matricula_pre_escola"],
                                          "taxa_liquida_pre_escola": oca["taxa_liquida_matricula_pre_escola"],
                                          "matriculas_pre_escola": num(oca["numero_absoluto_bruto_matricula_pre_escola"])}}


# ----------------------------------------------------------------- comex
@section
def comex(mid):
    out = {"fonte": "br_me_comex_stat"}
    for flow, tbl in (("exportacoes", "municipio_exportacao"), ("importacoes", "municipio_importacao")):
        t = p("br_me_comex_stat", tbl)
        ano = one(f"SELECT max(ano) a FROM {t} WHERE id_municipio='{mid}' AND mes=12")["a"]
        total = one(f"SELECT sum(valor_fob_dolar) v FROM {t} WHERE id_municipio='{mid}' AND ano={ano}")
        prev = one(f"SELECT sum(valor_fob_dolar) v FROM {t} WHERE id_municipio='{mid}' AND ano={ano-1}")
        sh4 = q(f"""SELECT id_sh4, sum(valor_fob_dolar) v FROM {t}
            WHERE id_municipio='{mid}' AND ano={ano} GROUP BY 1 ORDER BY 2 DESC LIMIT 6""")
        pais = q(f"""SELECT sigla_pais_iso3, sum(valor_fob_dolar) v FROM {t}
            WHERE id_municipio='{mid}' AND ano={ano} GROUP BY 1 ORDER BY 2 DESC LIMIT 6""")
        out[flow] = {"ano": ano, "total_fob_usd": total and total["v"], "ano_anterior_fob_usd": prev and prev["v"],
                     "top_sh4": [{"id_sh4": r["id_sh4"], "valor_fob_usd": r["v"]} for r in sh4],
                     "top_paises": [{"pais_iso3": r["sigla_pais_iso3"], "valor_fob_usd": r["v"]} for r in pais]}
    return out


# --------------------------------------------------------------- trabalho
@section
def trabalho_rais(mid):
    t = p("br_me_rais", "microdados_vinculos")
    ano = one(f"SELECT max(ano) a FROM {t} WHERE id_municipio='{mid}'")["a"]
    r = one(f"""SELECT count(*) FILTER (WHERE vinculo_ativo_3112='1') vinculos_ativos,
            avg(valor_remuneracao_media) FILTER (WHERE vinculo_ativo_3112='1' AND valor_remuneracao_media>0) remuneracao_media
        FROM {t} WHERE id_municipio='{mid}' AND ano={ano}""")
    prev = one(f"""SELECT count(*) FILTER (WHERE vinculo_ativo_3112='1') v
        FROM {t} WHERE id_municipio='{mid}' AND ano={ano-1}""")
    est = one(f"""SELECT count(*) n FROM {p('br_me_rais','microdados_estabelecimentos')}
        WHERE id_municipio='{mid}' AND ano={ano}""")
    return {"fonte": "br_me_rais.microdados", "ano": ano,
            "vinculos_ativos_3112": num(r["vinculos_ativos"]),
            "vinculos_ativos_ano_anterior": prev and num(prev["v"]),
            "remuneracao_media": r["remuneracao_media"],
            "estabelecimentos": est and est["n"]}


@section
def trabalho_top_empregadores(mid):
    """br_me_rais_identificada tem razão social (RAIS padrão não identifica empresa).
    Agrupa por CNPJ básico (uma empresa pode ter matriz + filiais) e filtra só
    empresas privadas de fato: exclui natureza jurídica pública (1xxx) e
    cooperativas/associações/fundações (mantém só natureza_juridica LIKE '2%',
    excluindo cooperativas 2143/2330)."""
    t = p("br_me_rais_identificada", "estabelecimentos")
    ano = one(f"SELECT max(ano) a FROM {t} WHERE id_municipio='{mid}'")["a"]
    cnae = p("br_bd_diretorios_brasil", "cnae_2")
    nat = p("br_bd_diretorios_brasil", "natureza_juridica")
    rows = q(f"""
        SELECT e.cnpj_basico, any_value(e.razao_social) razao_social,
               any_value(n.descricao) natureza, any_value(c.descricao_secao) setor,
               sum(e.quantidade_vinculos_ativos) vinculos_ativos
        FROM {t} e
        LEFT JOIN {cnae} c ON c.subclasse = e.cnae_fiscal_principal
        LEFT JOIN {nat} n ON n.id_natureza_juridica = e.natureza_juridica
        WHERE e.id_municipio='{mid}' AND e.ano={ano}
          AND e.natureza_juridica LIKE '2%' AND e.natureza_juridica NOT IN ('2143', '2330')
          AND e.quantidade_vinculos_ativos > 0
        GROUP BY e.cnpj_basico
        ORDER BY vinculos_ativos DESC LIMIT 10""")
    return {
        "fonte": "br_me_rais_identificada.estabelecimentos · br_bd_diretorios_brasil (cnae_2, natureza_juridica) — só empresas privadas (exclui setor público e cooperativas)",
        "ano": ano,
        "top": [{"empresa": r["razao_social"], "setor": r["setor"], "natureza": r["natureza"],
                 "vinculos_ativos": num(r["vinculos_ativos"])} for r in rows],
    }


@section
def trabalho_top_empregadores_publicos(mid):
    """Mesma base (br_me_rais_identificada), mas natureza_juridica LIKE '1%'
    (administração pública direta/indireta) — prefeitura, câmara, autarquias,
    fundações públicas etc."""
    t = p("br_me_rais_identificada", "estabelecimentos")
    ano = one(f"SELECT max(ano) a FROM {t} WHERE id_municipio='{mid}'")["a"]
    nat = p("br_bd_diretorios_brasil", "natureza_juridica")
    rows = q(f"""
        SELECT e.cnpj_basico, any_value(e.razao_social) razao_social,
               any_value(n.descricao) natureza, sum(e.quantidade_vinculos_ativos) vinculos_ativos
        FROM {t} e
        LEFT JOIN {nat} n ON n.id_natureza_juridica = e.natureza_juridica
        WHERE e.id_municipio='{mid}' AND e.ano={ano}
          AND e.natureza_juridica LIKE '1%' AND e.quantidade_vinculos_ativos > 0
        GROUP BY e.cnpj_basico
        ORDER BY vinculos_ativos DESC LIMIT 10""")
    return {
        "fonte": "br_me_rais_identificada.estabelecimentos · br_bd_diretorios_brasil (natureza_juridica) — administração pública direta e indireta",
        "ano": ano,
        "top": [{"empresa": r["razao_social"], "natureza": r["natureza"],
                 "vinculos_ativos": num(r["vinculos_ativos"])} for r in rows],
    }


@section
def trabalho_caged(mid):
    t = p("br_me_caged", "microdados_movimentacao")
    ano = one(f"SELECT max(ano) a FROM {t} WHERE id_municipio='{mid}' AND mes=12")["a"]
    r = one(f"""SELECT sum(CASE WHEN saldo_movimentacao>0 THEN 1 ELSE 0 END) admissoes,
            sum(CASE WHEN saldo_movimentacao<0 THEN 1 ELSE 0 END) desligamentos,
            sum(saldo_movimentacao) saldo,
            avg(salario_mensal) FILTER (WHERE saldo_movimentacao>0 AND salario_mensal>0 AND salario_mensal<200000) salario_medio_admissao
        FROM {t} WHERE id_municipio='{mid}' AND ano={ano}""")
    return {"fonte": "br_me_caged.microdados_movimentacao", "ano": ano,
            "admissoes": num(r["admissoes"]), "desligamentos": num(r["desligamentos"]),
            "saldo": num(r["saldo"]), "salario_medio_admissao": r["salario_medio_admissao"]}


# ------------------------------------------------------------ agropecuária
@section
def agropecuaria(mid):
    out = {"fonte": "br_ibge_pam · br_ibge_ppm"}
    lav = []
    for tbl, tipo in (("lavoura_permanente", "permanente"), ("lavoura_temporaria", "temporária")):
        t = p("br_ibge_pam", tbl)
        ano = one(f"SELECT max(ano) a FROM {t} WHERE id_municipio='{mid}' AND valor_producao IS NOT NULL")
        if not ano or ano["a"] is None:
            continue
        rows = q(f"""SELECT produto, area_colhida, quantidade_produzida, valor_producao FROM {t}
            WHERE id_municipio='{mid}' AND ano={ano['a']} AND valor_producao>0 ORDER BY valor_producao DESC LIMIT 6""")
        lav += [{"tipo": tipo, "ano": ano["a"], **{k: num(v) for k, v in r.items()}} for r in rows]
    lav.sort(key=lambda r: -(r.get("valor_producao") or 0))
    out["lavouras_top"] = lav[:8]
    t = p("br_ibge_ppm", "efetivo_rebanhos")
    ano = one(f"SELECT max(ano) a FROM {t} WHERE id_municipio='{mid}'")["a"]
    out["rebanhos"] = {"ano": ano, "efetivos": q(f"""SELECT tipo_rebanho, quantidade FROM {t}
        WHERE id_municipio='{mid}' AND ano={ano} ORDER BY quantidade DESC LIMIT 8""")}
    t = p("br_ibge_ppm", "producao_origem_animal")
    ano = one(f"SELECT max(ano) a FROM {t} WHERE id_municipio='{mid}'")["a"]
    out["origem_animal"] = {"ano": ano, "produtos": q(f"""SELECT produto, unidade, quantidade, valor FROM {t}
        WHERE id_municipio='{mid}' AND ano={ano} AND quantidade IS NOT NULL ORDER BY valor DESC NULLS LAST LIMIT 6""")}
    return out


# -------------------------------------------------------------- benefícios
@section
def beneficios(mid):
    out = {"fonte": "br_cgu_beneficios_cidadao"}
    t = p("br_cgu_beneficios_cidadao", "novo_bolsa_familia")
    am = one(f"SELECT max(ano_competencia*100+mes_competencia) am FROM {t} WHERE id_municipio='{mid}'")["am"]
    bf = one(f"""SELECT count(DISTINCT nis_favorecido) familias, sum(valor_parcela) repasse, avg(valor_parcela) valor_medio
        FROM {t} WHERE id_municipio='{mid}' AND ano_competencia={am//100} AND mes_competencia={am%100}""")
    out["bolsa_familia"] = {"competencia": f"{am//100}-{am%100:02d}", "familias": num(bf["familias"]),
                            "repasse_mensal": bf["repasse"], "valor_medio": bf["valor_medio"]}
    t = p("br_cgu_beneficios_cidadao", "bpc")
    am = one(f"SELECT max(ano_competencia*100+mes_competencia) am FROM {t} WHERE id_municipio='{mid}'")["am"]
    bpc = one(f"""SELECT count(DISTINCT coalesce(nis_favorecido, numero_beneficio)) beneficiarios, sum(valor_parcela) repasse
        FROM {t} WHERE id_municipio='{mid}' AND ano_competencia={am//100} AND mes_competencia={am%100}""")
    out["bpc"] = {"competencia": f"{am//100}-{am%100:02d}", "beneficiarios": num(bpc["beneficiarios"]), "repasse_mensal": bpc["repasse"]}
    t = p("br_cgu_beneficios_cidadao", "garantia_safra")
    am = one(f"SELECT max(ano_referencia*100+mes_referencia) am FROM {t} WHERE id_municipio='{mid}'")
    if am and am["am"]:
        gs = one(f"""SELECT count(DISTINCT nis_favorecido) familias, sum(valor_parcela) repasse
            FROM {t} WHERE id_municipio='{mid}' AND ano_referencia={am['am']//100} AND mes_referencia={am['am']%100}""")
        out["garantia_safra"] = {"competencia": f"{am['am']//100}-{am['am']%100:02d}", "familias": num(gs["familias"]), "repasse": gs["repasse"]}
    else:
        out["garantia_safra"] = None
    return out


# -------------------------------------------------------- saúde (ampliada)
@section
def saude_mortalidade(mid):
    """SIM — óbitos por residência. `idade` já vem em anos fracionários no espelho
    (0,07 = ~25 dias), não no código DATASUS de 4 dígitos, então `idade < 1` é
    mortalidade infantil de verdade. Capítulo CID-10 sai do range CATINIC..CATFIM
    de br_datasus_cid10.capitulos — comparação de string, sem tabela de-para."""
    t = p("br_ms_sim", "microdados")
    cap = p("br_datasus_cid10", "capitulos")
    sub = p("br_datasus_cid10", "subcategorias")
    ano = one(f"SELECT max(ano) a FROM {t} WHERE id_municipio_residencia='{mid}'")["a"]
    if ano is None:
        raise RuntimeError("sem SIM para o município")
    r = one(f"""SELECT count(*) obitos,
            count(*) FILTER (WHERE idade < 1) obitos_infantis,
            count(*) FILTER (WHERE idade < 28.0/365) obitos_neonatais,
            avg(idade) FILTER (WHERE idade <= 110) idade_media_obito,
            count(*) FILTER (WHERE sexo='1') homens,
            count(*) FILTER (WHERE sexo='2') mulheres,
            count(*) FILTER (WHERE causa_basica >= 'V01' AND causa_basica < 'Z00') causas_externas,
            count(*) FILTER (WHERE causa_basica >= 'X60' AND causa_basica < 'X85') suicidios,
            count(*) FILTER (WHERE causa_basica >= 'X85' AND causa_basica < 'Y10') agressoes,
            count(*) FILTER (WHERE causa_basica >= 'V01' AND causa_basica < 'V99') transporte,
            count(*) FILTER (WHERE substr(causa_basica,1,3) BETWEEN 'O00' AND 'O99') maternas,
            count(*) FILTER (WHERE substr(causa_basica,1,3) BETWEEN 'R00' AND 'R99') mal_definidas
        FROM {t} WHERE id_municipio_residencia='{mid}' AND ano={ano}""")
    pop = one(f"SELECT populacao FROM {p('br_ibge_populacao','municipio')} WHERE id_municipio='{mid}' AND ano={ano}")
    nv = one(f"SELECT count(*) n FROM {p('br_ms_sinasc','microdados')} WHERE id_municipio_residencia='{mid}' AND ano={ano}")
    caps = q(f"""SELECT c.DESCRABREV capitulo, count(*) n
        FROM {t} s LEFT JOIN {cap} c ON substr(s.causa_basica,1,3) BETWEEN c.CATINIC AND c.CATFIM
        WHERE s.id_municipio_residencia='{mid}' AND s.ano={ano}
        GROUP BY 1 ORDER BY 2 DESC LIMIT 8""")
    top = q(f"""SELECT s.causa_basica, any_value(d.DESCRICAO) descricao, count(*) n
        FROM {t} s LEFT JOIN {sub} d ON d.SUBCAT = s.causa_basica
        WHERE s.id_municipio_residencia='{mid}' AND s.ano={ano} AND s.causa_basica IS NOT NULL
        GROUP BY 1 ORDER BY 3 DESC LIMIT 8""")
    serie = q(f"""SELECT ano, count(*) obitos, count(*) FILTER (WHERE idade < 1) infantis
        FROM {t} WHERE id_municipio_residencia='{mid}' AND ano >= {ano - 11} GROUP BY 1 ORDER BY 1""")
    total = int(r["obitos"] or 0)
    nasc = nv and int(nv["n"] or 0)
    populacao = pop and num(pop["populacao"])
    return {
        "fonte": "br_ms_sim.microdados (residência) · br_datasus_cid10",
        "ano": ano, "populacao_referencia": populacao,
        **{k: num(v) for k, v in r.items()},
        "taxa_mortalidade_1000hab": total / populacao * 1000 if populacao else None,
        "nascidos_vivos": nasc,
        "taxa_mortalidade_infantil_1000nv": (int(r["obitos_infantis"] or 0) / nasc * 1000) if nasc else None,
        "por_capitulo": [{"capitulo": (c["capitulo"] or "Não classificado"), "obitos": num(c["n"])} for c in caps],
        "top_causas": [{"cid": c["causa_basica"], "descricao": c["descricao"], "obitos": num(c["n"])} for c in top],
        "serie": [{"ano": s["ano"], "obitos": num(s["obitos"]), "infantis": num(s["infantis"])} for s in serie],
    }


@section
def saude_internacoes(mid):
    """SIH/AIH. Atenção: as três colunas de município aqui são de 6 dígitos
    (`id_municipio_paciente`, `_estabelecimento`, `_gestor`) — juntar pelo código
    de 7 dígitos devolve zero linha em silêncio. Usa o último ano com 12 meses."""
    mid6 = mid[:6]
    t = p("br_ms_sih", "aihs_reduzidas")
    cap = p("br_datasus_cid10", "capitulos")
    ano = one(f"""SELECT max(ano) a FROM (
        SELECT ano FROM {t} WHERE id_municipio_paciente='{mid6}' GROUP BY ano HAVING count(DISTINCT mes)=12)""")["a"]
    if ano is None:
        raise RuntimeError("sem SIH para o município")
    r = one(f"""SELECT count(*) internacoes, sum(valor_aih) valor_total,
            sum(indicador_obito) obitos_hospitalares,
            avg(quantidade_dias_permanencia) permanencia_media,
            sum(quantidade_dias_uti_mes) diarias_uti,
            count(*) FILTER (WHERE id_municipio_estabelecimento='{mid6}') no_municipio,
            count(*) FILTER (WHERE carater_internacao='2') urgencia
        FROM {t} WHERE id_municipio_paciente='{mid6}' AND ano={ano}""")
    prev = one(f"SELECT count(*) n, sum(valor_aih) v FROM {t} WHERE id_municipio_paciente='{mid6}' AND ano={ano-1}")
    caps = q(f"""SELECT c.DESCRABREV capitulo, count(*) n, sum(s.valor_aih) valor
        FROM {t} s LEFT JOIN {cap} c
          ON coalesce(s.cid_principal_categoria, substr(s.cid_principal_subcategoria,1,3)) BETWEEN c.CATINIC AND c.CATFIM
        WHERE s.id_municipio_paciente='{mid6}' AND s.ano={ano}
        GROUP BY 1 ORDER BY 2 DESC LIMIT 8""")
    serie = q(f"""SELECT ano, count(*) internacoes, sum(valor_aih) valor
        FROM {t} WHERE id_municipio_paciente='{mid6}' AND ano >= {ano - 9} AND ano <= {ano}
        GROUP BY 1 ORDER BY 1""")
    total = int(r["internacoes"] or 0)
    return {
        "fonte": "br_ms_sih.aihs_reduzidas (residência do paciente, id_municipio_6)",
        "ano": ano, **{k: num(v) for k, v in r.items()},
        "valor_medio_aih": (r["valor_total"] / total) if total and r["valor_total"] else None,
        "taxa_mortalidade_hospitalar": (int(r["obitos_hospitalares"] or 0) / total * 100) if total else None,
        "pct_no_municipio": (int(r["no_municipio"] or 0) / total * 100) if total else None,
        "ano_anterior": prev and {"internacoes": num(prev["n"]), "valor_total": prev["v"]},
        "por_capitulo": [{"capitulo": (c["capitulo"] or "Não classificado"),
                          "internacoes": num(c["n"]), "valor": c["valor"]} for c in caps],
        "serie": [{"ano": s["ano"], "internacoes": num(s["internacoes"]), "valor": s["valor"]} for s in serie],
    }


IEPS_CAMPOS = {
    "cobertura_esf": "cob_esf", "cobertura_atencao_basica": "cob_ab",
    "cobertura_plano_privado": "cob_priv", "medicos_1000hab": "tx_med",
    "enfermeiros_1000hab": "tx_enf", "leitos_sus_100k": "tx_leito_sus",
    "leitos_uti_sus_100k": "tx_leitouti_sus", "despesa_saude_per_capita": "desp_tot_saude_pc_mun",
    "despesa_saude_per_capita_uf": "desp_tot_saude_pc_uf",
    "pct_receita_propria_saude": "pct_desp_recp_saude_mun",
    "taxa_mortalidade_evitavel_100k": "tx_mort_evit",
    "taxa_internacao_csap_100k": "tx_hosp_csap",
    "pct_prenatal_adequado": "pct_prenatal_adeq", "pct_prenatal_zero": "pct_prenatal_zero",
}


@section
def saude_ieps(mid):
    """IEPS Data — indicadores de saúde já calculados por município. Cada campo
    tem cobertura temporal própria, então pega o último ano NÃO nulo campo a campo
    em vez de um único max(ano) que traria uma linha cheia de NULL."""
    t = p("br_ieps_saude", "municipio")
    rows = q(f"SELECT * FROM {t} WHERE id_municipio='{mid}' ORDER BY ano DESC")
    if not rows:
        raise RuntimeError("município fora do IEPS")
    out, anos = {}, {}
    for nome, col in IEPS_CAMPOS.items():
        for row in rows:
            if row.get(col) is not None:
                out[nome] = num(row[col])
                anos[nome] = row["ano"]
                break
    return {"fonte": "br_ieps_saude.municipio (IEPS Data)",
            "ano_max": rows[0]["ano"], "indicadores": out, "ano_por_indicador": anos}


@section
def saude_imunizacao(mid):
    t = p("br_ms_imunizacoes", "municipio")
    serie = q(f"""SELECT ano, cobertura_total, cobertura_triplice_viral_d1, cobertura_poliomielite,
            cobertura_bcg, cobertura_penta, cobertura_hepatite_b
        FROM {t} WHERE id_municipio='{mid}' AND ano >= 2010 ORDER BY ano""")
    if not serie:
        raise RuntimeError("sem imunizações")
    return {"fonte": "br_ms_imunizacoes.municipio (cobertura vacinal, %)",
            "ano": serie[-1]["ano"],
            "serie": [{k: num(v) for k, v in s.items()} for s in serie]}


@section
def saude_planos(mid):
    """ANS — beneficiários de plano privado. A segmentação puramente odontológica
    não é assistência médica: separar as duas ou a cobertura sai inflada."""
    t = p("br_ans_beneficiario", "informacao_consolidada")
    am = one(f"SELECT max(ano*100+mes) am FROM {t} WHERE id_municipio='{mid}'")["am"]
    if am is None:
        raise RuntimeError("sem ANS")
    ano, mes = am // 100, am % 100
    r = one(f"""SELECT sum(quantidade_beneficiario_ativo) total,
            sum(quantidade_beneficiario_ativo) FILTER (WHERE segmentacao_beneficiario NOT ILIKE 'Odonto%') medico_hospitalar,
            sum(quantidade_beneficiario_ativo) FILTER (WHERE segmentacao_beneficiario ILIKE 'Odonto%') odontologico
        FROM {t} WHERE id_municipio='{mid}' AND ano={ano} AND mes={mes}""")
    contr = q(f"""SELECT contratacao_beneficiario tipo, sum(quantidade_beneficiario_ativo) n
        FROM {t} WHERE id_municipio='{mid}' AND ano={ano} AND mes={mes} GROUP BY 1 ORDER BY 2 DESC LIMIT 4""")
    pop = one(f"""SELECT populacao FROM {p('br_ibge_populacao','municipio')}
        WHERE id_municipio='{mid}' ORDER BY ano DESC LIMIT 1""")
    med = num(r["medico_hospitalar"]) if r else None
    return {"fonte": "br_ans_beneficiario.informacao_consolidada",
            "competencia": f"{ano}-{mes:02d}",
            "beneficiarios_total": r and num(r["total"]),
            "medico_hospitalar": med, "odontologico": r and num(r["odontologico"]),
            "cobertura_pct": (med / pop["populacao"] * 100) if med and pop and pop["populacao"] else None,
            "por_contratacao": [{"tipo": demojibake(c["tipo"]), "beneficiarios": num(c["n"])} for c in contr]}


@section
def saude_farmacia_popular(mid):
    r = one(f"""SELECT count(*) n FROM {p('br_saude_farmaciapopular','estabelecimentos')}
        WHERE CAST(codigo_municipio AS VARCHAR)='{mid[:6]}'""")
    return {"fonte": "br_saude_farmaciapopular.estabelecimentos (id_municipio_6)",
            "estabelecimentos_credenciados": r and num(r["n"])}


# ------------------------------------------------- violência (SINAN VIVA)
VIOL_TIPOS = [("fisica", "VIOL_FISIC"), ("psicologica", "VIOL_PSICO"), ("sexual", "VIOL_SEXU"),
              ("negligencia", "VIOL_NEGLI"), ("financeira", "VIOL_FINAN"), ("tortura", "VIOL_TORT"),
              ("trafico_humano", "VIOL_TRAF"), ("infantil_trabalho", "VIOL_INFAN")]
VIOL_LOCAL = {"01": "Residência", "02": "Habitação coletiva", "03": "Escola", "04": "Local de prática esportiva",
              "05": "Bar ou similar", "06": "Via pública", "07": "Comércio/serviços", "08": "Indústria",
              "09": "Outro", "99": "Ignorado"}
VIOL_CICLO = {"1": "Criança (0-9)", "2": "Adolescente (10-19)", "3": "Jovem (20-24)",
              "4": "Adulto (25-59)", "5": "Idoso (60+)", "9": "Ignorado"}


@section
def seguranca_violencia(mid):
    """SINAN violência interpessoal/autoprovocada. Duas armadilhas conhecidas:
    (1) o município vem em código de 6 dígitos; (2) `NU_ANO` está em branco no lote
    inteiro de 2020 — o ano confiável é `ano_sinan`. Raça: "negro" é preto+pardo
    (CS_RACA 2 e 4); filtrar só '2' subestima em ~5x."""
    mid6 = mid[:6]
    t = p("br_ms_sinan_violencia", "microdados_violencia")
    ano = one(f"""SELECT max(ano_sinan) a FROM {t}
        WHERE CAST("ID_MN_RESI" AS VARCHAR)='{mid6}'""")["a"]
    if ano is None:
        raise RuntimeError("sem notificações de violência")
    tipos = ", ".join(f"""count(*) FILTER (WHERE "{c}"='1') {k}""" for k, c in VIOL_TIPOS)
    r = one(f"""SELECT count(*) notificacoes,
            count(*) FILTER (WHERE "CS_SEXO"='F') feminino,
            count(*) FILTER (WHERE "CS_SEXO"='M') masculino,
            count(*) FILTER (WHERE "CS_RACA" IN ('2','4')) negros,
            count(*) FILTER (WHERE "CS_RACA"='1') brancos,
            count(*) FILTER (WHERE "CS_RACA" NOT IN ('1','2','3','4','5') OR "CS_RACA" IS NULL) raca_ignorada,
            count(*) FILTER (WHERE "LES_AUTOP"='1') autoprovocadas,
            count(*) FILTER (WHERE "AG_FOGO"='1') arma_fogo,
            {tipos}
        FROM {t} WHERE CAST("ID_MN_RESI" AS VARCHAR)='{mid6}' AND ano_sinan={ano}""")
    local = q(f"""SELECT "LOCAL_OCOR" cod, count(*) n FROM {t}
        WHERE CAST("ID_MN_RESI" AS VARCHAR)='{mid6}' AND ano_sinan={ano}
        GROUP BY 1 ORDER BY 2 DESC LIMIT 6""")
    ciclo = q(f"""SELECT "CICL_VID" cod, count(*) n FROM {t}
        WHERE CAST("ID_MN_RESI" AS VARCHAR)='{mid6}' AND ano_sinan={ano} GROUP BY 1 ORDER BY 1""")
    serie = q(f"""SELECT ano_sinan ano, count(*) n,
            count(*) FILTER (WHERE "LES_AUTOP"='1') autoprovocadas
        FROM {t} WHERE CAST("ID_MN_RESI" AS VARCHAR)='{mid6}' AND ano_sinan >= {ano - 9}
        GROUP BY 1 ORDER BY 1""")
    total = int(r["notificacoes"] or 0)
    return {
        "fonte": "br_ms_sinan_violencia.microdados_violencia (residência da vítima, id_municipio_6; ano = ano_sinan)",
        "ano": ano, **{k: num(v) for k, v in r.items()},
        "pct_feminino": (int(r["feminino"] or 0) / total * 100) if total else None,
        "pct_negros": (int(r["negros"] or 0) / total * 100) if total else None,
        "nota_raca": "negro = preto + pardo (CS_RACA 2 e 4), convenção IBGE",
        "por_local": [{"local": VIOL_LOCAL.get((l["cod"] or "").strip(), "Ignorado"), "n": num(l["n"])} for l in local],
        "por_ciclo_vida": [{"ciclo": VIOL_CICLO.get((c["cod"] or "").strip(), "Ignorado"), "n": num(c["n"])} for c in ciclo],
        "serie": [{"ano": s["ano"], "notificacoes": num(s["n"]), "autoprovocadas": num(s["autoprovocadas"])} for s in serie],
    }


# --------------------------------------------------- transparência (ampliada)
@section
def transp_emendas(mid):
    t = p("br_cgu_emendas_parlamentares", "microdados")
    serie = q(f"""SELECT ano_emenda ano, count(*) emendas, sum(valor_empenhado) empenhado,
            sum(valor_pago) pago FROM {t} WHERE id_municipio_gasto='{mid}'
        GROUP BY 1 ORDER BY 1 DESC LIMIT 12""")
    if not serie:
        raise RuntimeError("sem emendas para o município")
    ano = serie[0]["ano"]
    autores = q(f"""SELECT nome_autor_emenda autor, count(*) emendas, sum(valor_pago) pago
        FROM {t} WHERE id_municipio_gasto='{mid}' AND ano_emenda >= {ano - 5}
        GROUP BY 1 ORDER BY 3 DESC NULLS LAST LIMIT 8""")
    funcoes = q(f"""SELECT nome_funcao funcao, sum(valor_pago) pago
        FROM {t} WHERE id_municipio_gasto='{mid}' AND ano_emenda >= {ano - 5}
        GROUP BY 1 HAVING sum(valor_pago) > 0 ORDER BY 2 DESC LIMIT 6""")
    return {"fonte": "br_cgu_emendas_parlamentares.microdados (id_municipio_gasto)",
            "ano": ano, "janela_autores": f"{ano - 5}–{ano}",
            "serie": [{k: num(v) for k, v in s.items()} for s in reversed(serie)],
            "top_autores": [{"autor": a["autor"], "emendas": num(a["emendas"]), "pago": a["pago"]} for a in autores],
            "por_funcao": [{"funcao": f["funcao"], "pago": f["pago"]} for f in funcoes]}


@section
def transp_compras_federais(mid, rf):
    """Duas pontas distintas: licitações federais *realizadas no* município
    (`br_cgu_licitacao_contrato.licitacao.id_municipio`) e contratos federais
    *ganhos por* empresas sediadas nele (CNPJ → id_municipio_rf, 4 dígitos)."""
    t_lic = p("br_cgu_licitacao_contrato", "licitacao")
    t_con = p("br_cgu_licitacao_contrato", "contrato_compra")
    t_est = p("br_me_cnpj", "estabelecimentos")
    lic = q(f"""SELECT ano, count(*) licitacoes, sum(valor_licitacao) valor
        FROM {t_lic} WHERE id_municipio='{mid}' GROUP BY 1 ORDER BY 1 DESC LIMIT 8""")
    orgaos = q(f"""SELECT nome_orgao orgao, count(*) n, sum(valor_licitacao) valor
        FROM {t_lic} WHERE id_municipio='{mid}' GROUP BY 1 ORDER BY 3 DESC NULLS LAST LIMIT 5""")
    out = {"fonte": "br_cgu_licitacao_contrato (licitação por município · contrato por CNPJ local) · br_me_cnpj",
           "licitacoes_no_municipio": {
               "serie": [{k: num(v) for k, v in r.items()} for r in reversed(lic)],
               "por_orgao": [{"orgao": o["orgao"], "licitacoes": num(o["n"]), "valor": o["valor"]} for o in orgaos]}}
    if not rf:
        out["fornecedores_locais"] = None
        return out
    am = one(f"SELECT max(ano*100+mes) am FROM {t_est}")["am"]
    loc = f"""(SELECT DISTINCT cnpj FROM {t_est}
              WHERE ano={am // 100} AND mes={am % 100} AND id_municipio_rf='{rf}')"""
    serie = q(f"""SELECT c.ano, count(*) contratos, sum(c.valor_final_compra) valor
        FROM {t_con} c JOIN {loc} l ON regexp_replace(c.cpf_cnpj_contratado, '[^0-9]', '', 'g') = l.cnpj
        GROUP BY 1 ORDER BY 1 DESC LIMIT 8""")
    top = q(f"""SELECT c.nome_contratado empresa, count(*) contratos, sum(c.valor_final_compra) valor
        FROM {t_con} c JOIN {loc} l ON regexp_replace(c.cpf_cnpj_contratado, '[^0-9]', '', 'g') = l.cnpj
        GROUP BY 1 ORDER BY 3 DESC NULLS LAST LIMIT 8""")
    out["fornecedores_locais"] = {
        "snapshot_cnpj": f"{am // 100}-{am % 100:02d}",
        "serie": [{k: num(v) for k, v in r.items()} for r in reversed(serie)],
        "top": [{"empresa": r["empresa"], "contratos": num(r["contratos"]), "valor": r["valor"]} for r in top]}
    return out


@section
def transp_diarios(mid):
    t = p("br_ok_queridodiario", "diarios")
    serie = q(f"""SELECT substr(CAST(date AS VARCHAR),1,4) ano, count(*) edicoes,
            count(*) FILTER (WHERE is_extra_edition) extras
        FROM {t} WHERE CAST(territory_id AS VARCHAR)='{mid}' GROUP BY 1 ORDER BY 1""")
    if not serie:
        raise RuntimeError("município não coberto pelo Querido Diário")
    ult = one(f"SELECT max(date) d, count(*) n FROM {t} WHERE CAST(territory_id AS VARCHAR)='{mid}'")
    return {"fonte": "br_ok_queridodiario.diarios (territory_id)",
            "total_edicoes": ult and num(ult["n"]), "ultima_edicao": ult and str(ult["d"]),
            "serie": [{"ano": num(s["ano"]), "edicoes": num(s["edicoes"]), "extras": num(s["extras"])} for s in serie]}


@section
def transp_fiscal(mid):
    """FIRJAN IFGF (gestão fiscal, 0–1) + CAPAG do Tesouro (notas A–D).
    CAPAG='n.d.' quando o município não entregou a DCA — as notas parciais
    continuam válidas e são o que sobra de informação."""
    ifgf = q(f"""SELECT ano, indice_firjan_gestao_fiscal indice, ranking_estadual, ranking_nacional
        FROM {p('br_firjan_ifgf','ranking')} WHERE id_municipio='{mid}' ORDER BY ano""")
    capag = one(f"""SELECT "CAPAG" capag, "Nota 1" nota_endividamento, "Nota 2" nota_poupanca_corrente,
            "Nota 3" nota_liquidez, "ICF" icf
        FROM {p('br_tesouro_capag','municipios')}
        WHERE CAST("Código Município Completo" AS VARCHAR)='{mid}' LIMIT 1""")
    return {"fonte": "br_firjan_ifgf.ranking · br_tesouro_capag.municipios",
            "ifgf": [{k: num(v) for k, v in r.items()} for r in ifgf],
            "capag": capag and {k: (v if v not in ("n.d.", "") else None) for k, v in capag.items()}}


@section
def transp_consumidor(mid, nome, uf):
    """consumidor.gov.br — só tem nome de cidade + UF, sem código IBGE.
    `Ano Abertura` mistura int e float ('2021.0'), então normaliza antes de agrupar."""
    t = p("br_mj_consumidorgovbr", "reclamacoes")
    nome_sql = nome.replace("'", "''")
    flt = (f"""upper(strip_accents("Cidade"))=upper(strip_accents('{nome_sql}')) AND "UF"='{uf}'""")
    serie = q(f"""SELECT CAST(TRY_CAST("Ano Abertura" AS DOUBLE) AS BIGINT) ano, count(*) reclamacoes,
            avg(TRY_CAST("Nota do Consumidor" AS DOUBLE)) nota_media,
            avg(CASE WHEN "Respondida"='S' THEN 100.0 WHEN "Respondida"='N' THEN 0.0 END) pct_respondida
        FROM {t} WHERE {flt} GROUP BY 1 HAVING ano IS NOT NULL ORDER BY 1""")
    if not serie:
        raise RuntimeError("sem reclamações para o município")
    ano = serie[-1]["ano"]
    if len(serie) > 1 and int(serie[-1]["reclamacoes"]) < 0.5 * int(serie[-2]["reclamacoes"]):
        ano = serie[-2]["ano"]  # último ano parece parcial; usa o anterior
    seg = q(f"""SELECT "Segmento de Mercado" segmento, count(*) n FROM {t}
        WHERE {flt} AND CAST(TRY_CAST("Ano Abertura" AS DOUBLE) AS BIGINT)={ano}
        GROUP BY 1 ORDER BY 2 DESC LIMIT 6""")
    emp = q(f"""SELECT "Nome Fantasia" empresa, count(*) n FROM {t}
        WHERE {flt} AND CAST(TRY_CAST("Ano Abertura" AS DOUBLE) AS BIGINT)={ano}
        GROUP BY 1 ORDER BY 2 DESC LIMIT 6""")
    return {"fonte": "br_mj_consumidorgovbr.reclamacoes (nome da cidade + UF)",
            "ano": ano,
            "serie": [{k: num(v) for k, v in s.items()} for s in serie],
            "top_segmentos": [{"segmento": s["segmento"], "reclamacoes": num(s["n"])} for s in seg],
            "top_empresas": [{"empresa": e["empresa"], "reclamacoes": num(e["n"])} for e in emp]}


@section
def transp_servidores(mid):
    t = p("br_ibge_munic", "recursos_humanos")
    row = one(f"""SELECT * FROM {t} WHERE id_municipio='{mid}' AND adm_direta IS NOT NULL
        ORDER BY ano DESC LIMIT 1""")
    if not row:
        raise RuntimeError("sem MUNIC/recursos humanos")
    keys = ["adm_direta", "adm_indireta", "estatutario_adm_direta", "clt_adm_direta",
            "comissionado_adm_direta", "estagio_adm_direta", "sem_vinculo_permanente_adm_direta",
            "adm_direta_ensino_superior", "adm_direta_pos_graduacao"]
    return {"fonte": "br_ibge_munic.recursos_humanos (Pesquisa MUNIC/IBGE)",
            "ano": row["ano"], **{k: num(row.get(k)) for k in keys}}


# --------------------------------------------------------------- empresas
@section
def empresas_cnpj(mid, rf):
    """Base CNPJ da Receita. `situacao_cadastral` é '2' (ativa) / '8' (baixada) —
    sem zero à esquerda no espelho. O snapshot é mensal e cumulativo: filtrar
    ano+mes é obrigatório ou cada estabelecimento entra dezenas de vezes."""
    if not rf:
        raise RuntimeError("município sem código da Receita Federal")
    t = p("br_me_cnpj", "estabelecimentos")
    cnae = p("br_bd_diretorios_brasil", "cnae_2")
    am = one(f"SELECT max(ano*100+mes) am FROM {t}")["am"]
    ano, mes = am // 100, am % 100
    base = f"{t} WHERE ano={ano} AND mes={mes} AND id_municipio_rf='{rf}'"
    r = one(f"""SELECT count(*) FILTER (WHERE situacao_cadastral='2') ativas,
            count(*) FILTER (WHERE situacao_cadastral='8') baixadas,
            count(*) FILTER (WHERE situacao_cadastral='2' AND identificador_matriz_filial='1') matrizes,
            count(*) FILTER (WHERE situacao_cadastral='2' AND identificador_matriz_filial='2') filiais,
            count(*) registradas,
            avg(date_diff('year', data_inicio_atividade, CURRENT_DATE)) FILTER (WHERE situacao_cadastral='2') idade_media_anos
        FROM {base}""")
    secoes = q(f"""SELECT c.descricao_secao secao, count(*) n
        FROM {t} e LEFT JOIN (SELECT DISTINCT subclasse, descricao_secao FROM {cnae}) c
          ON c.subclasse = e.cnae_fiscal_principal
        WHERE e.ano={ano} AND e.mes={mes} AND e.id_municipio_rf='{rf}' AND e.situacao_cadastral='2'
        GROUP BY 1 ORDER BY 2 DESC LIMIT 8""")
    top_cnae = q(f"""SELECT any_value(c.descricao_subclasse) atividade, count(*) n
        FROM {t} e LEFT JOIN (SELECT DISTINCT subclasse, descricao_subclasse FROM {cnae}) c
          ON c.subclasse = e.cnae_fiscal_principal
        WHERE e.ano={ano} AND e.mes={mes} AND e.id_municipio_rf='{rf}' AND e.situacao_cadastral='2'
          AND c.descricao_subclasse IS NOT NULL
        GROUP BY e.cnae_fiscal_principal ORDER BY 2 DESC LIMIT 8""")
    aberturas = q(f"""SELECT extract(year FROM data_inicio_atividade) ano, count(*) n
        FROM {base} AND extract(year FROM data_inicio_atividade) BETWEEN {ano - 10} AND {ano}
        GROUP BY 1 ORDER BY 1""")
    baixas = q(f"""SELECT extract(year FROM data_situacao_cadastral) ano, count(*) n
        FROM {base} AND situacao_cadastral='8'
          AND extract(year FROM data_situacao_cadastral) BETWEEN {ano - 10} AND {ano}
        GROUP BY 1 ORDER BY 1""")
    ab = {int(a["ano"]): num(a["n"]) for a in aberturas}
    ba = {int(b["ano"]): num(b["n"]) for b in baixas}
    anos = sorted(set(ab) | set(ba))
    return {"fonte": "br_me_cnpj.estabelecimentos (id_municipio_rf) · br_bd_diretorios_brasil.cnae_2",
            "competencia": f"{ano}-{mes:02d}",
            **{k: num(v) for k, v in r.items()},
            "por_secao_cnae": [{"secao": s["secao"] or "Não informado", "ativas": num(s["n"])} for s in secoes],
            "top_atividades": [{"atividade": c["atividade"], "ativas": num(c["n"])} for c in top_cnae],
            "demografia_empresarial": [{"ano": a, "aberturas": ab.get(a, 0), "baixas": ba.get(a, 0),
                                        "saldo": ab.get(a, 0) - ba.get(a, 0)} for a in anos]}


# ---------------------------------------------------------- combustíveis
@section
def economia_combustiveis(mid, nome, nome_uf):
    """ANP: não há código de município, só nome em caixa alta sem acento + o nome
    do estado por extenso. Janela de 60 dias a partir da última coleta da base."""
    t = p("br_anp_combustiveis", "precos")
    nome_sql = nome.replace("'", "''")
    uf_sql = nome_uf.replace("'", "''")
    rows = q(f"""
        WITH b AS (SELECT municipio, estado, cnpj, produto,
                          TRY_CAST(preco_revenda AS DOUBLE) preco,
                          TRY_CAST(data_coleta AS TIMESTAMP) d
                   FROM {t}),
             ult AS (SELECT max(d) m FROM b),
             janela AS (SELECT * FROM b, ult WHERE d >= m - INTERVAL 60 DAY),
             mun AS (SELECT * FROM janela
                     WHERE upper(strip_accents(municipio))=upper(strip_accents('{nome_sql}'))
                       AND upper(strip_accents(estado))=upper(strip_accents('{uf_sql}')))
        SELECT j.produto,
               (SELECT avg(preco) FROM mun WHERE mun.produto=j.produto) preco_municipio,
               (SELECT count(DISTINCT cnpj) FROM mun WHERE mun.produto=j.produto) postos,
               (SELECT max(d) FROM mun WHERE mun.produto=j.produto) ultima_coleta,
               avg(j.preco) FILTER (WHERE upper(strip_accents(j.estado))=upper(strip_accents('{uf_sql}'))) preco_uf,
               avg(j.preco) preco_brasil
        FROM janela j GROUP BY j.produto ORDER BY j.produto""")
    produtos = [{"produto": r["produto"], "preco_municipio": r["preco_municipio"],
                 "preco_uf": r["preco_uf"], "preco_brasil": r["preco_brasil"],
                 "postos": num(r["postos"]), "ultima_coleta": r["ultima_coleta"] and str(r["ultima_coleta"])[:10]}
                for r in rows if r["preco_municipio"] is not None]
    if not produtos:
        raise RuntimeError("sem coleta da ANP no município nos últimos 60 dias")
    return {"fonte": "br_anp_combustiveis.precos (nome do município + estado)",
            "janela_dias": 60, "produtos": produtos}


# ------------------------------------------------- censo 2022 (ampliado)
DOM_TOPO = {
    "esgotamento": ("caracteristica_domicilio_grupo_idade_raca_esgotamento_sanitario", "tipo_esgotamento_sanitario",
                    ["Rede geral, rede pluvial ou fossa ligada à rede", "Fossa séptica ou fossa filtro não ligada à rede",
                     "Fossa rudimentar ou buraco", "Rio, lago, córrego ou mar", "Vala", "Outra forma",
                     "Não tinham banheiro nem sanitário"]),
    "agua": ("caracteristica_domicilio_grupo_idade_raca_ligacao_abastecimento_agua", "tipo_ligacao_rede_geral",
             ["Possui ligação à rede geral e a utiliza como forma principal",
              "Possui ligação à rede geral, mas utiliza principalmente outra forma",
              "Não possui ligação com a rede geral"]),
    "lixo": ("caracteristica_domicilio_grupo_idade_raca_destino_lixo", "tipo_destino_lixo",
             ["Coletado", "Queimado na propriedade", "Enterrado na propriedade",
              "Jogado em terreno baldio, encosta ou área pública", "Outro destino"]),
    "tipo_domicilio": ("caracteristica_domicilio_grupo_idade_raca_tipo_domicilio", "tipo_domicilio", None),
}


@section
def demografia_censo_extra(mid):
    """Censo 2022, além do básico. Duas armadilhas: (1)
    `populacao_grupo_idade_sexo_raca` guarda 2010 E 2022 na mesma tabela — sem
    `WHERE ano` o total quase dobra; (2) as tabelas de característica do domicílio
    são hierárquicas: 'Rede geral ou pluvial' está DENTRO de 'Rede geral, rede
    pluvial ou fossa ligada à rede'. Somar tudo conta duas vezes."""
    out = {"fonte": "br_ibge_censo_2022 · br_ibge_censo2022_religiao.populacao_religiao"}

    raca = q(f"""SELECT ano, cor_raca, sum(populacao) populacao
        FROM {p('br_ibge_censo_2022','populacao_grupo_idade_sexo_raca')}
        WHERE id_municipio='{mid}' GROUP BY 1,2 ORDER BY 1, 3 DESC""")
    por_ano = {}
    for r in raca:
        por_ano.setdefault(r["ano"], []).append({"cor_raca": r["cor_raca"], "populacao": num(r["populacao"])})
    out["cor_raca"] = {str(a): v for a, v in sorted(por_ano.items())}

    alf = q(f"""SELECT cor_raca,
            sum(populacao) FILTER (WHERE alfabetizacao='Alfabetizadas') alfabetizadas,
            sum(populacao) total
        FROM {p('br_ibge_censo_2022','alfabetizacao_grupo_idade_sexo_raca')}
        WHERE id_municipio='{mid}' GROUP BY 1 ORDER BY 3 DESC""")
    def _taxa(parte, todo):
        parte, todo = num(parte), num(todo)
        return (parte / todo * 100) if parte is not None and todo else None
    out["alfabetizacao_por_raca"] = [
        {"cor_raca": a["cor_raca"], "alfabetizadas": num(a["alfabetizadas"]), "total": num(a["total"]),
         "taxa": _taxa(a["alfabetizadas"], a["total"])} for a in alf]

    rel = q(f"""SELECT religiao, populacao_10_mais populacao
        FROM {p('br_ibge_censo2022_religiao','populacao_religiao')}
        WHERE nivel='municipio' AND CAST(id_localidade AS VARCHAR)='{mid}'
        ORDER BY populacao_10_mais DESC""")
    total_rel = next((num(r["populacao"]) for r in rel if r["religiao"] == "Total"), None)
    out["religiao"] = {
        "total_10_anos_ou_mais": total_rel,
        "grupos": [{"religiao": r["religiao"], "populacao": num(r["populacao"]),
                    "pct": _taxa(r["populacao"], total_rel)}
                   for r in rel if r["religiao"] != "Total"]}
    return out


@section
def infra_censo_domicilios(mid):
    out = {"fonte": "br_ibge_censo_2022.caracteristica_domicilio_* (população residente, autodeclarado)"}
    for chave, (tabela, coluna, topo) in DOM_TOPO.items():
        rows = q(f"""SELECT {coluna} categoria, sum(populacao) populacao
            FROM {p('br_ibge_censo_2022', tabela)} WHERE id_municipio='{mid}'
            GROUP BY 1 ORDER BY 2 DESC NULLS LAST""")
        if topo:
            rows = [r for r in rows if r["categoria"] in topo]
        rows = [{"categoria": r["categoria"], "populacao": num(r["populacao"])} for r in rows if r["populacao"]]
        total = sum(int(r["populacao"]) for r in rows) or None
        out[chave] = {"total": total,
                      "categorias": [{"categoria": r["categoria"], "populacao": r["populacao"],
                                      "pct": (r["populacao"] / total * 100) if total else None} for r in rows]}
    dom = q(f"""SELECT especie, domicilios FROM {p('br_ibge_censo_2022','domicilio_recenseado')}
        WHERE id_municipio='{mid}' ORDER BY domicilios DESC""")
    out["domicilios_recenseados"] = [{"especie": d["especie"], "domicilios": num(d["domicilios"])} for d in dom]
    return out


# ------------------------------------------------------ educação (ampliada)
REDE_CENSO = {"1": "Federal", "2": "Estadual", "3": "Municipal", "4": "Privada"}


@section
def educacao_censo_escolar(mid):
    """Censo Escolar por escola. `tipo_situacao_funcionamento='1'` = em atividade;
    sem esse filtro entram escolas paralisadas/extintas. `rede` é código (1-4),
    `tipo_localizacao` 1=urbana / 2=rural."""
    t = p("br_inep_censo_escolar", "escola")
    ano = one(f"SELECT max(ano) a FROM {t} WHERE id_municipio='{mid}'")["a"]
    base = f"{t} WHERE id_municipio='{mid}' AND ano={ano} AND CAST(tipo_situacao_funcionamento AS VARCHAR)='1'"
    r = one(f"""SELECT count(*) escolas,
            sum(quantidade_matricula_educacao_basica) matriculas,
            sum(quantidade_docente_educacao_basica) docentes,
            sum(quantidade_turma_educacao_basica) turmas,
            count(*) FILTER (WHERE CAST(tipo_localizacao AS VARCHAR)='2') escolas_rurais,
            count(*) FILTER (WHERE CAST(internet AS VARCHAR) IN ('1','Sim')) com_internet,
            count(*) FILTER (WHERE CAST(biblioteca AS VARCHAR) IN ('1','Sim')) com_biblioteca,
            count(*) FILTER (WHERE CAST(quadra_esportes AS VARCHAR) IN ('1','Sim')) com_quadra,
            count(*) FILTER (WHERE CAST(laboratorio_informatica AS VARCHAR) IN ('1','Sim')) com_laboratorio,
            count(*) FILTER (WHERE CAST(esgoto_rede_publica AS VARCHAR) IN ('1','Sim')) com_esgoto_rede,
            count(*) FILTER (WHERE CAST(acessibilidade_rampas AS VARCHAR) IN ('1','Sim')) com_rampa_acessibilidade,
            sum(quantidade_matricula_infantil) matriculas_infantil,
            sum(quantidade_matricula_fundamental) matriculas_fundamental,
            sum(quantidade_matricula_medio) matriculas_medio,
            sum(quantidade_matricula_eja) matriculas_eja,
            sum(quantidade_matricula_especial) matriculas_especial,
            sum(quantidade_matricula_utiliza_transporte_publico) matriculas_transporte
        FROM {base}""")
    redes = q(f"""SELECT CAST(rede AS VARCHAR) rede, count(*) escolas,
            sum(quantidade_matricula_educacao_basica) matriculas,
            sum(quantidade_docente_educacao_basica) docentes
        FROM {base} GROUP BY 1 ORDER BY 3 DESC NULLS LAST""")
    serie = q(f"""SELECT ano, count(*) escolas, sum(quantidade_matricula_educacao_basica) matriculas
        FROM {t} WHERE id_municipio='{mid}' AND ano >= {ano - 9}
          AND CAST(tipo_situacao_funcionamento AS VARCHAR)='1' GROUP BY 1 ORDER BY 1""")
    return {"fonte": "br_inep_censo_escolar.escola (escolas em atividade)", "ano": ano,
            **{k: num(v) for k, v in r.items()},
            "por_rede": [{"rede": REDE_CENSO.get(x["rede"], x["rede"]), "escolas": num(x["escolas"]),
                          "matriculas": num(x["matriculas"]), "docentes": num(x["docentes"])} for x in redes],
            "serie": [{"ano": s["ano"], "escolas": num(s["escolas"]), "matriculas": num(s["matriculas"])} for s in serie]}


@section
def educacao_sisu(mid):
    """SISU pelo município de residência do candidato (`id_municipio_candidato`).
    Um candidato pode ser aprovado em mais de uma chamada — conta CPF distinto."""
    t = p("br_mec_sisu", "microdados")
    serie = q(f"""SELECT ano, count(DISTINCT cpf) candidatos,
            count(DISTINCT CASE WHEN CAST(status_aprovado AS VARCHAR) IN ('true','1') THEN cpf END) aprovados,
            count(DISTINCT CASE WHEN status_matricula='Efetivada' THEN cpf END) matriculados,
            avg(TRY_CAST(nota_candidato AS DOUBLE)) nota_media
        FROM {t} WHERE id_municipio_candidato='{mid}' GROUP BY 1 ORDER BY 1""")
    if not serie:
        raise RuntimeError("sem candidatos do município no SISU")
    ano = serie[-1]["ano"]
    cursos = q(f"""SELECT nome_curso curso, any_value(sigla_ies) ies, count(DISTINCT cpf) matriculados
        FROM {t} WHERE id_municipio_candidato='{mid}' AND ano={ano} AND status_matricula='Efetivada'
        GROUP BY 1 ORDER BY 3 DESC LIMIT 6""")
    return {"fonte": "br_mec_sisu.microdados (residência do candidato; matrícula efetivada, não só aprovação)",
            "ano": ano,
            "serie": [{k: num(v) for k, v in s.items()} for s in serie],
            "top_cursos": [{"curso": c["curso"], "ies": c["ies"], "matriculados": num(c["matriculados"])} for c in cursos]}


# ------------------------------------------------------- política (ampliada)
@section
def politica_camara(mid):
    """Câmara municipal e perfil de quem se candidatou. `resultado` do TSE nunca
    deve ser filtrado com ILIKE '%eleito%' — isso casa 'nao eleito' também."""
    t_res = p("br_tse_eleicoes", "resultados_candidato_municipio")
    t_can = p("br_tse_eleicoes", "candidatos")
    t_rec = p("br_tse_eleicoes", "receitas_candidato")
    ano = one(f"SELECT max(ano) a FROM {t_res} WHERE id_municipio='{mid}' AND cargo='vereador'")["a"]
    if ano is None:
        raise RuntimeError("sem eleição municipal")
    eleitos = q(f"""SELECT sigla_partido partido, count(*) cadeiras, sum(votos) votos
        FROM {t_res} WHERE id_municipio='{mid}' AND ano={ano} AND cargo='vereador'
          AND resultado IN ('eleito','eleito por qp','eleito por media')
        GROUP BY 1 ORDER BY 2 DESC, 3 DESC""")
    perfil = one(f"""SELECT count(*) candidatos,
            count(*) FILTER (WHERE genero='feminino') feminino,
            count(*) FILTER (WHERE genero='masculino') masculino,
            count(*) FILTER (WHERE raca IN ('preta','parda')) negros,
            count(*) FILTER (WHERE raca='branca') brancos,
            avg(idade) idade_media
        FROM {t_can} WHERE id_municipio='{mid}' AND ano={ano}""")
    financ = q(f"""SELECT cargo, count(DISTINCT sequencial_candidato) candidatos, sum(valor_receita) receita
        FROM {t_rec} WHERE id_municipio='{mid}' AND ano={ano} GROUP BY 1 ORDER BY 3 DESC""")
    return {"fonte": "br_tse_eleicoes (resultados_candidato_municipio, candidatos, receitas_candidato)",
            "ano": ano,
            "cadeiras_total": sum(int(e["cadeiras"]) for e in eleitos),
            "bancadas": [{"partido": e["partido"], "cadeiras": num(e["cadeiras"]), "votos": num(e["votos"])} for e in eleitos],
            "perfil_candidatos": perfil and {k: num(v) for k, v in perfil.items()},
            "financiamento": [{"cargo": f["cargo"], "candidatos": num(f["candidatos"]), "receita": f["receita"]} for f in financ]}


@section
def politica_deputados_nascidos(mid):
    t = p("br_camara_dados_abertos", "deputado")
    rows = q(f"""SELECT nome, data_nascimento, data_falecimento
        FROM {t} WHERE CAST(id_municipio_nascimento AS VARCHAR)='{mid}'
        ORDER BY data_nascimento DESC""")
    return {"fonte": "br_camara_dados_abertos.deputado (id_municipio_nascimento)",
            "total": len(rows),
            "deputados": [{"nome": r["nome"], "nascimento": r["data_nascimento"] and str(r["data_nascimento"]),
                           "falecido": bool(r["data_falecimento"])} for r in rows[:10]]}


# ---------------------------------------------------- benefícios (ampliada)
@section
def beneficios_cadunico(mid):
    t = p("br_mc_indicadores", "transferencias_municipio")
    am = one(f"""SELECT max(ano*100+mes) am FROM {t}
        WHERE id_municipio='{mid}' AND pessoas_cadastradas_cu IS NOT NULL""")["am"]
    if am is None:
        raise RuntimeError("sem CadÚnico")
    ano, mes = am // 100, am % 100
    r = one(f"""SELECT pessoas_cadastradas_cu, familias_cadastradas_cu, familias_beneficiarias_pbf
        FROM {t} WHERE id_municipio='{mid}' AND ano={ano} AND mes={mes}""")
    pop = one(f"""SELECT populacao FROM {p('br_ibge_populacao','municipio')}
        WHERE id_municipio='{mid}' AND ano={ano}""")
    pessoas = r and num(r["pessoas_cadastradas_cu"])
    return {"fonte": "br_mc_indicadores.transferencias_municipio (CadÚnico)",
            "competencia": f"{ano}-{mes:02d}",
            "pessoas_cadastradas": pessoas,
            "familias_cadastradas": r and num(r["familias_cadastradas_cu"]),
            "familias_pbf": r and num(r["familias_beneficiarias_pbf"]),
            "pct_populacao": (pessoas / pop["populacao"] * 100) if pessoas and pop and pop["populacao"] else None}


# -------------------------------------------------------------- vizinhança
@section
def vizinhanca(mid):
    rows = q(f"""SELECT v.id_municipio_2 id_municipio, d.nome, d.sigla_uf
        FROM {p('br_bd_vizinhanca','municipio')} v
        LEFT JOIN {p('br_bd_diretorios_brasil','municipio')} d ON d.id_municipio=v.id_municipio_2
        WHERE v.id_municipio_1='{mid}' AND v.ano=(SELECT max(ano) FROM {p('br_bd_vizinhanca','municipio')})
        ORDER BY d.nome""")
    ids = [mid] + [r["id_municipio"] for r in rows]
    ids_sql = "', '".join(ids)

    t_pop = p("br_ibge_populacao", "municipio")
    ano_pop = one(f"SELECT max(ano) a FROM {t_pop} WHERE id_municipio IN ('{ids_sql}')")["a"]
    pop_map = {r["id_municipio"]: num(r["populacao"])
               for r in q(f"SELECT id_municipio, populacao FROM {t_pop} WHERE id_municipio IN ('{ids_sql}') AND ano={ano_pop}")}

    t_pib = p("br_ibge_pib", "municipio")
    ano_pib = one(f"SELECT max(ano) a FROM {t_pib} WHERE id_municipio IN ('{ids_sql}')")["a"]
    pib_map = {r["id_municipio"]: num(r["pib"])
               for r in q(f"SELECT id_municipio, pib FROM {t_pib} WHERE id_municipio IN ('{ids_sql}') AND ano={ano_pib}")}

    def pib_pc(id_):
        pib, pop = pib_map.get(id_), pop_map.get(id_)
        return pib / pop if pib and pop else None

    municipios = [{"id_municipio": r["id_municipio"], "nome": r["nome"], "sigla_uf": r["sigla_uf"],
                   "populacao": pop_map.get(r["id_municipio"]), "pib_per_capita": pib_pc(r["id_municipio"])} for r in rows]
    municipios.sort(key=lambda m: -(m["populacao"] or 0))

    return {"fonte": "br_bd_vizinhanca.municipio · br_ibge_populacao · br_ibge_pib",
            "municipios": municipios,
            "referencia": {"populacao_ano": ano_pop, "pib_ano": ano_pib,
                           "populacao": pop_map.get(mid), "pib_per_capita": pib_pc(mid)}}


def main():
    if len(sys.argv) < 2:
        sys.exit("uso: extract_municipio.py <id_municipio>")
    mid = sys.argv[1]
    prof = perfil(mid)
    uf = prof.get("sigla_uf")
    nome = prof.get("nome") or ""
    nome_uf = prof.get("nome_uf") or ""
    rf = prof.get("id_municipio_rf")
    doc = {
        "schema_version": 1,
        "gerado_em": date.today().isoformat(),
        "gerador": "rodado",
        "municipio": prof,
        "secoes": {
            "geografia": geografia(mid),
            "demografia": {**demografia(mid), "censo_extra": demografia_censo_extra(mid)},
            "economia": {
                "pib": economia_pib(mid, uf),
                "financas_publicas": economia_siconfi(mid),
                "bancario": economia_estban(mid),
                "inpc_brasil": economia_inpc(),
                "combustiveis": economia_combustiveis(mid, nome, nome_uf),
            },
            "empresas": empresas_cnpj(mid, rf),
            "educacao": {
                "ideb": educacao_ideb(mid, uf),
                "saeb": educacao_saeb(mid),
                "indicadores": educacao_indicadores(mid),
                "enem": educacao_enem(mid),
                "censo_escolar": educacao_censo_escolar(mid),
                "sisu": educacao_sisu(mid),
            },
            "saude": {
                "cnes": saude_cnes(mid),
                "nascidos_vivos": saude_sinasc(mid),
                "dengue": saude_dengue(mid),
                "sisvan": saude_sisvan(mid),
                "mortalidade": saude_mortalidade(mid),
                "internacoes": saude_internacoes(mid),
                "ieps": saude_ieps(mid),
                "imunizacao": saude_imunizacao(mid),
                "planos_privados": saude_planos(mid),
                "farmacia_popular": saude_farmacia_popular(mid),
            },
            "seguranca": {"isp_rj": seguranca_isp(mid, uf), "fbsp": seguranca_fbsp(mid),
                          "violencia_sinan": seguranca_violencia(mid)},
            "infraestrutura": {"snis": infra_snis(mid), "atlas_esgotos": infra_ana(mid),
                               "censo_domicilios": infra_censo_domicilios(mid)},
            "meio_ambiente": {
                "prodes": ambiente_prodes(mid), "seeg": ambiente_seeg(mid),
                "queimadas": ambiente_queimadas(mid), "sisam": ambiente_sisam(mid),
                "mapbiomas": ambiente_mapbiomas(mid),
            },
            "conectividade": conectividade(mid),
            "politica": {**politica(mid),
                         "camara_municipal": politica_camara(mid),
                         "deputados_nascidos": politica_deputados_nascidos(mid)},
            "transparencia": {**transparencia(mid),
                              "emendas": transp_emendas(mid),
                              "compras_federais": transp_compras_federais(mid, rf),
                              "diarios_oficiais": transp_diarios(mid),
                              "fiscal": transp_fiscal(mid),
                              "consumidor": transp_consumidor(mid, nome, uf),
                              "servidores": transp_servidores(mid)},
            "social": social(mid),
            "comercio_exterior": comex(mid),
            "trabalho": {"rais": trabalho_rais(mid), "caged": trabalho_caged(mid),
                         "top_empregadores": trabalho_top_empregadores(mid),
                         "top_empregadores_publicos": trabalho_top_empregadores_publicos(mid)},
            "agropecuaria": agropecuaria(mid),
            "beneficios": {**beneficios(mid), "cadastro_unico": beneficios_cadunico(mid)},
            "vizinhanca": vizinhanca(mid),
        },
    }
    json.dump(doc, sys.stdout, ensure_ascii=False, indent=1, default=str)


if __name__ == "__main__":
    main()
