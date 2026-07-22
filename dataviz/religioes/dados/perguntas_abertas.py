"""
Responde as perguntas 1, 2, 3, 4, 5 e 8 da secao 5 de notes/relatorio.md,
usando so os arquivos ja existentes no projeto (parquet + resultante.csv +
../racas/data.json). Nao depende de acesso remoto (beelink) - ver
consulta_cnpj_vertente_tempo.py para as perguntas 7 e 9, que exigem isso.

Uso: python3 perguntas_abertas.py
"""
import json
import re
import unicodedata
from pathlib import Path

import pandas as pd

HERE = Path(__file__).parent
PARQUET = HERE / "igrejas_geolocalizadas.parquet"
RESULTANTE_CSV = HERE / "resultante.csv"
MUNICIPIOS_CSV = HERE / "municipios.csv"
VERTENTES_CSV = HERE / "vertentes-religiosas.csv"
RACAS_JSON = HERE.parent.parent / "racas" / "data.json"

# rollup do vertente_id (folha, especifico) ate um dos 4 baldes que o Censo
# 2022 (resultante.csv) reporta - o resto de classificado que nao cai nesses
# 4 vai pra "outras"; nao_classificado fica de fora da correlacao (ver §4.1 e
# §8.1 de metodologia.md: nao classificado nao deve ser redistribuido)
TOPO_PARA_BALDE = {
    2800: "catolica-apostolica-romana",
    95263: "catolica-apostolica-romana",
    100430: "catolica-apostolica-romana",
    2803: "catolica-apostolica-romana",
    95277: "evangelicas",
    2812: "evangelicas",
    2821: "evangelicas",
    2822: "evangelicas",
    2824: "evangelicas",  # Testemunhas de Jeova - sem balde proprio no Censo 2022
    2826: "espirita",
    2827: "umbanda-e-candomble",
}


def normaliza_nome(s):
    s = unicodedata.normalize("NFKD", str(s)).encode("ascii", "ignore").decode()
    s = re.sub(r"[^a-z0-9]+", " ", s.lower()).strip()
    return s


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


def q1_coordenadas_duplicadas(df):
    print("\n=== Q1: templos com lat/lon idênticos ===")
    dup = df.groupby(["lat", "lon"]).size()
    dup = dup[dup > 1]
    print(f"Grupos de coordenada duplicada: {len(dup)}")
    print(f"Templos envolvidos: {int(dup.sum())} ({dup.sum() / len(df):.1%} do total)")
    maiores = dup.sort_values(ascending=False).head(10)
    print("Top 10 maiores grupos (lat, lon, n):")
    print(maiores)


def q3_qualidade_coordenada_por_uf(df):
    print("\n=== Q3: nível de geocodificação por UF ===")
    tab = pd.crosstab(df["sigla_uf"], df["nivel_geocodificacao_coordenadas"], normalize="index") * 100
    tab = tab.round(1)
    print(tab.sort_values(tab.columns[0]))


def q5_nao_classificados(df):
    print("\n=== Q5: templos sem vertente atribuída ===")
    nc = df[df["vertente_id"].isna()]
    print(f"Total não classificado: {len(nc)} ({len(nc) / len(df):.1%} do total)")
    print(f"Nomes (descricao_estabelecimento) únicos entre eles: {nc['descricao_estabelecimento'].nunique()}")
    top = nc["descricao_estabelecimento"].value_counts().head(20)
    print("Top 20 nomes mais frequentes fora do dicionário:")
    print(top)


def carrega_municipios():
    # nota: no CSV a coluna "uf" traz o codigo numerico (11) e "uf_code" traz
    # a sigla (RO) - nomes trocados na fonte, usamos uf_code como sigla real
    m = pd.read_csv(MUNICIPIOS_CSV)
    m["chave"] = m["uf_code"].astype(str) + "|" + m["name"].map(normaliza_nome)
    m = m[["municipio", "uf_code", "name", "pop_21", "chave"]].rename(
        columns={"municipio": "id_municipio", "uf_code": "uf"}
    )
    m["id_municipio"] = m["id_municipio"].astype(str)
    return m


def carrega_resultante():
    r = pd.read_csv(RESULTANTE_CSV, sep=";")
    r["chave"] = r["uf"].astype(str) + "|" + r["municipio"].map(normaliza_nome)
    return r


def q8_per_capita(df, municipios, resultante):
    print("\n=== Q8: templos por habitante ===")
    por_mun = df.groupby("id_municipio").size().rename("n_templos").reset_index()
    por_mun["id_municipio"] = por_mun["id_municipio"].astype(str)
    j = por_mun.merge(municipios, on="id_municipio", how="left")
    j = j.merge(resultante[["chave", "population"]], on="chave", how="left")
    sem_pop = j["population"].isna().sum()
    print(f"Municípios sem população encontrada (join falhou): {sem_pop} de {len(j)}")
    j = j.dropna(subset=["population"])
    j["templos_por_100k"] = j["n_templos"] / j["population"] * 100_000

    print("\n-- Ranking por UF (templos / 100 mil hab.) --")
    por_uf = j.groupby("uf").agg(templos=("n_templos", "sum"), populacao=("population", "sum"))
    por_uf["templos_por_100k"] = por_uf["templos"] / por_uf["populacao"] * 100_000
    print(por_uf.sort_values("templos_por_100k", ascending=False).round(1))

    print("\n-- Top 15 municípios (pop. mínima 20 mil, evita outlier de cidade pequena) --")
    grandes = j[j["population"] >= 20_000]
    print(
        grandes.sort_values("templos_por_100k", ascending=False)
        [["name", "uf", "population", "n_templos", "templos_por_100k"]]
        .head(15).round(1).to_string(index=False)
    )

    print("\n-- Bottom 15 municípios (mesma pop. mínima) --")
    print(
        grandes.sort_values("templos_por_100k")
        [["name", "uf", "population", "n_templos", "templos_por_100k"]]
        .head(15).round(1).to_string(index=False)
    )


def q2_correlacao_templos_fieis(df, municipios, resultante, topo_por_vertente):
    print("\n=== Q2: correlação templos × fiéis declarados (Censo 2022), por vertente ===")
    d = df.dropna(subset=["vertente_id"]).copy()
    d["topo"] = d["vertente_id"].map(topo_por_vertente)
    d["balde"] = d["topo"].map(TOPO_PARA_BALDE)
    d = d.dropna(subset=["balde"])

    baldes = ["catolica-apostolica-romana", "evangelicas", "espirita", "umbanda-e-candomble"]

    contagem = d.groupby(["id_municipio", "balde"]).size().unstack(fill_value=0).reset_index()
    contagem["id_municipio"] = contagem["id_municipio"].astype(str)
    for b in baldes:
        if b not in contagem.columns:
            contagem[b] = 0
    contagem = contagem.merge(municipios[["id_municipio", "chave", "uf"]], on="id_municipio", how="left")
    censo = resultante[["chave", "population"] + baldes].rename(columns={b: f"{b}_censo" for b in baldes})
    contagem = contagem.merge(censo, on="chave", how="left")
    contagem = contagem.dropna(subset=["population"])

    # normalizar os dois lados por populacao (templos/100k hab. vs % fieis
    # declarados) - e' o metodo do NT20 (igrejas/100mil hab. x % evangelicos),
    # nao a fatia do total nacional de templos, que so mediria tamanho de
    # cidade (SP tem mais de tudo por ser a maior populacao, nao por
    # densidade religiosa diferente)
    for b in baldes:
        contagem[f"{b}_por100k"] = contagem[b] / contagem["population"] * 100_000

    print("\n-- Correlação de Pearson, nível município (n={}) --".format(len(contagem)))
    for b in baldes:
        r = contagem[f"{b}_por100k"].corr(contagem[f"{b}_censo"])
        print(f"{b}: r = {r:.3f}")

    print("\n-- Correlação de Pearson, nível UF --")
    for b in baldes:
        contagem[f"{b}_fieis_abs"] = contagem[f"{b}_censo"] / 100 * contagem["population"]
    agg = {f"{b}_fieis_abs": "sum" for b in baldes}
    agg.update({b: "sum" for b in baldes})
    agg["population"] = "sum"
    uf_agg = contagem.groupby("uf").agg(agg)
    for b in baldes:
        pct_templo_uf = uf_agg[b] / uf_agg["population"] * 100_000
        pct_fieis_uf = uf_agg[f"{b}_fieis_abs"] / uf_agg["population"] * 100
        r = pct_templo_uf.corr(pct_fieis_uf)
        print(f"{b}: r = {r:.3f} (n={len(uf_agg)} UFs)")


def q4_racas(df, municipios, topo_por_vertente):
    print("\n=== Q4: Umbanda/Candomblé × % preta+parda (Censo 2022, via ../racas) ===")
    if not RACAS_JSON.exists():
        print(f"AVISO: {RACAS_JSON} não encontrado, pulando.")
        return
    with open(RACAS_JSON) as f:
        racas = json.load(f)["2022"]
    cols = ["uf", "municipio", "lat", "lon", "population", "branca", "preta", "parda", "amarela", "indigena", "cluster"]
    racas_df = pd.DataFrame(racas, columns=cols[: len(racas[0])])
    racas_df["chave"] = racas_df["uf"].astype(str) + "|" + racas_df["municipio"].map(normaliza_nome)
    racas_df["pct_negra"] = racas_df["preta"] + racas_df["parda"]

    # rollup ate o topo (2827 = Umbanda e Candomble) - usar so vertente_id==2827
    # direto perderia os 7.095 templos classificados nos sub-nos (Umbanda,
    # Candomble, outras) - ver §4.1 metodologia.md
    topo = df["vertente_id"].map(topo_por_vertente)
    umbanda = df[topo == 2827]
    por_mun = umbanda.groupby("id_municipio").size().rename("n_terreiros").reset_index()
    por_mun["id_municipio"] = por_mun["id_municipio"].astype(str)
    j = por_mun.merge(municipios, on="id_municipio", how="left")
    j = j.merge(racas_df[["chave", "population", "pct_negra"]], on="chave", how="left")
    j = j.dropna(subset=["population"])
    j["terreiros_por_100k"] = j["n_terreiros"] / j["population"] * 100_000

    r = j["terreiros_por_100k"].corr(j["pct_negra"])
    print(f"Municípios com pelo menos 1 terreiro contado: {len(j)}")
    print(f"Correlação terreiros/100k hab. × % preta+parda: r = {r:.3f}")


def main():
    df = pd.read_parquet(PARQUET)
    municipios = carrega_municipios()
    resultante = carrega_resultante()
    topo_por_vertente = carrega_topo_por_vertente()

    q1_coordenadas_duplicadas(df)
    q3_qualidade_coordenada_por_uf(df)
    q5_nao_classificados(df)
    q8_per_capita(df, municipios, resultante)
    q2_correlacao_templos_fieis(df, municipios, resultante, topo_por_vertente)
    q4_racas(df, municipios, topo_por_vertente)


if __name__ == "__main__":
    main()
