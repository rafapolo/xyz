"""
Responde as perguntas 7 e 9 da secao 5 de notes/relatorio.md - exige acesso
remoto (ssh beelink + DuckDB), porque o parquet local (igrejas_geolocalizadas)
so guarda o booleano com_cnae, nao a data de abertura do CNPJ casado.

Metodo (equivalente ao NT20/Araujo, Fig. 1/2 e Apendice A): reclassifica
razao_social (tabela empresas, nao descricao_estabelecimento do CNEFE) com o
mesmo dicionario de vertente usado no pipeline principal
(cnefe-descricao-vertente.csv), sobre todo CNPJ ativo de CNAE 9491-0/00,
cruzando com data_inicio_atividade e situacao_cadastral (tabela
estabelecimentos). So SELECT - nenhuma escrita no host remoto.

Uso: python3 consulta_cnpj_vertente_tempo.py
"""
import json
import subprocess
from pathlib import Path

import pandas as pd

from gerar_igrejas_geolocalizadas import carregar_padroes, sql_literal

HERE = Path(__file__).parent
VERTENTES_CSV = HERE / "vertentes-religiosas.csv"

EMPRESAS_PATH = "/home/polo/rodado/br_me_cnpj/empresas/*.parquet"
ESTAB_PATH = "/home/polo/rodado/br_me_cnpj/estabelecimentos/*.parquet"


def build_sql():
    positivos, _exclusoes = carregar_padroes()
    case_lines = "\n    ".join(
        f"WHEN razao_social ILIKE '%{sql_literal(r['padrao'])}%' THEN {r['vertente_id']}"
        for r in positivos
    )
    return f"""
CREATE TEMP TABLE emp AS
  SELECT cnpj_basico, razao_social
  FROM read_parquet('{EMPRESAS_PATH}')
  WHERE (ano * 100 + mes) = (SELECT MAX(ano * 100 + mes) FROM read_parquet('{EMPRESAS_PATH}'));

CREATE TEMP TABLE estab AS
  SELECT cnpj_basico, data_inicio_atividade, situacao_cadastral
  FROM read_parquet('{ESTAB_PATH}')
  WHERE cnae_fiscal_principal = '9491000'
    AND (ano * 100 + mes) = (SELECT MAX(ano * 100 + mes) FROM read_parquet('{ESTAB_PATH}'));

SELECT
  YEAR(e.data_inicio_atividade) AS ano_abertura,
  e.situacao_cadastral,
  CASE
    {case_lines}
    ELSE NULL
  END AS vertente_id,
  COUNT(*) AS n
FROM estab e
JOIN emp m USING (cnpj_basico)
GROUP BY 1, 2, 3
ORDER BY 1;
"""


def rodar_remoto(sql):
    script_path = "/tmp/consulta_cnpj_vertente_tempo.sql"
    subprocess.run(["ssh", "beelink", f"cat > {script_path}"], input=sql, text=True, check=True)
    result = subprocess.run(
        ["ssh", "beelink", f"~/bin/duckdb -json -c \".read {script_path}\""],
        capture_output=True, text=True, check=True,
    )
    linhas = [l for l in result.stdout.splitlines() if l.strip()[:1] in ("[", "{", "]")]
    return json.loads("\n".join(linhas))


def carrega_topo_por_vertente():
    v = pd.read_csv(VERTENTES_CSV)
    id_pai = dict(zip(v["id"], v["id_pai"]))

    def topo(vid):
        visto = set()
        while vid in id_pai and id_pai[vid] not in (0, None) and id_pai[vid] not in visto:
            visto.add(vid)
            vid = id_pai[vid]
        return vid

    return {row.id: topo(row.id) for row in v.itertuples()}


NOME_TOPO = {
    2800: "Católica", 95263: "Católica", 100430: "Católica", 2803: "Católica",
    95277: "Evangélica", 2812: "Evangélica", 2821: "Evangélica", 2822: "Evangélica",
    2824: "Testemunhas de Jeová", 2826: "Espírita", 2827: "Umbanda e Candomblé",
}


def q7_padrao_etario(df, topo_por_vertente):
    print("\n=== Q7: padrão etário (data_inicio_atividade) por vertente, CNPJ ativos ===")
    d = df[(df["situacao_cadastral"] == "2") & df["vertente_id"].notna() & df["ano_abertura"].notna()].copy()
    d["topo"] = d["vertente_id"].map(topo_por_vertente)
    d["vertente_nome"] = d["topo"].map(NOME_TOPO).fillna("Outras")
    d["decada"] = (d["ano_abertura"].astype(int) // 10) * 10
    d.loc[d["decada"] < 1970, "decada"] = 1969  # "ate 1969"

    tab = d.groupby(["decada", "vertente_nome"])["n"].sum().unstack(fill_value=0)
    print(tab)

    total_classificado = d["n"].sum()
    total_geral = df[df["situacao_cadastral"] == "2"]["n"].sum()
    print(f"\nTotal CNPJ religioso ativo (todas décadas): {total_geral}")
    print(f"Classificado por vertente (razão social bateu no dicionário): {total_classificado} ({total_classificado/total_geral:.1%})")


def q9_taxa_sobrevivencia(df, topo_por_vertente):
    print("\n=== Q9: taxa de sobrevivência institucional (CNPJ aberto até 2005, 20+ anos) ===")
    d = df[df["ano_abertura"].notna() & (df["ano_abertura"] <= 2005) & df["vertente_id"].notna()].copy()
    d["topo"] = d["vertente_id"].map(topo_por_vertente)
    d["vertente_nome"] = d["topo"].map(NOME_TOPO).fillna("Outras")
    d["status"] = d["situacao_cadastral"].map({"2": "ativa", "8": "baixada"}).fillna("outra")

    tab = d.groupby(["vertente_nome", "status"])["n"].sum().unstack(fill_value=0)
    tab["total"] = tab.sum(axis=1)
    tab["%_ativa"] = (tab.get("ativa", 0) / tab["total"] * 100).round(1)
    print(tab.sort_values("%_ativa", ascending=False))

    geral = d.groupby("status")["n"].sum()
    total = geral.sum()
    print(f"\nGeral (todas vertentes, CNPJ aberto até 2005): {total} registros, {geral.get('ativa', 0)/total:.1%} ainda ativos")


def main():
    sql = build_sql()
    dados = rodar_remoto(sql)
    df = pd.DataFrame(dados)
    df["vertente_id"] = pd.to_numeric(df["vertente_id"], errors="coerce")
    df["ano_abertura"] = pd.to_numeric(df["ano_abertura"], errors="coerce")

    topo_por_vertente = carrega_topo_por_vertente()
    q7_padrao_etario(df, topo_por_vertente)
    q9_taxa_sobrevivencia(df, topo_por_vertente)


if __name__ == "__main__":
    main()
