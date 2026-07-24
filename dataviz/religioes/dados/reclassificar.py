"""
Reaplica cnefe-descricao-vertente.csv sobre igrejas_geolocalizadas.parquet, no
local, sem reconsultar o CNEFE.

A vertente e' funcao pura de descricao_estabelecimento, entao mexer no
dicionario nao exige rodar gerar_igrejas_geolocalizadas.py de novo (que precisa
do beelink e le' 60 GB de parquet). Este script so reescreve a coluna
vertente_id. A geolocalizacao, o com_cnae e a presenca ficam intactos.

Uso:
    python3 reclassificar.py            # reescreve o parquet e mostra o diff
    python3 reclassificar.py --dry-run  # so mostra o diff
"""

import argparse
import csv
from collections import Counter
from pathlib import Path

import pandas as pd

HERE = Path(__file__).parent
PADROES_CSV = HERE / "cnefe-descricao-vertente.csv"
VERTENTES_CSV = HERE / "vertentes-religiosas.csv"
PARQUET = HERE / "igrejas_geolocalizadas.parquet"


def carregar_regras():
    with open(PADROES_CSV, encoding="utf-8") as f:
        rows = [r for r in csv.DictReader(f) if r["excluir"] != "true"]
    # mesma ordem do gerador: prioridade desc, comprimento desc
    rows.sort(key=lambda r: (int(r.get("prioridade") or 100), len(r["padrao"])),
              reverse=True)
    return [(r["padrao"], int(r["vertente_id"])) for r in rows]


def carregar_nomes():
    with open(VERTENTES_CSV, encoding="utf-8") as f:
        return {int(r["id"]): r["nome"] for r in csv.DictReader(f)}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--dry-run", action="store_true")
    args = ap.parse_args()

    regras = carregar_regras()
    nomes = carregar_nomes()
    df = pd.read_parquet(PARQUET)

    # classifica por descricao distinta, nao por linha: 195 mil chaves em vez
    # de 765 mil linhas, com o mesmo resultado
    def classificar(texto):
        for padrao, vid in regras:
            if padrao in texto:
                return vid
        return None

    unicos = df["descricao_estabelecimento"].fillna("").unique()
    mapa = {d: classificar(d) for d in unicos}
    novo = df["descricao_estabelecimento"].fillna("").map(mapa)

    antigo = df["vertente_id"]
    ganhou = int((antigo.isna() & novo.notna()).sum())
    perdeu = int((antigo.notna() & novo.isna()).sum())
    mudou = antigo.notna() & novo.notna() & (antigo != novo)

    print(f"linhas: {len(df):,}")
    print(f"sem classe: {int(antigo.isna().sum()):,} -> {int(novo.isna().sum()):,}")
    print(f"  +{ganhou:,} classificados   -{perdeu:,} perdidos   "
          f"~{int(mudou.sum()):,} trocaram de vertente")

    if mudou.any():
        trocas = Counter(zip(antigo[mudou].astype(int), novo[mudou].astype(int)))
        print("\n  trocas de vertente:")
        for (a, b), n in trocas.most_common(12):
            print(f"    {n:>6}  {nomes.get(a, a)[:38]:<38} -> {nomes.get(b, b)[:38]}")

    if args.dry_run:
        print("\ndry-run: parquet nao foi tocado")
        return

    df["vertente_id"] = novo.astype("Int32")
    df.to_parquet(PARQUET, index=False)
    print(f"\ngravado em {PARQUET.name} - rode gerar_data_json.py pra propagar")


if __name__ == "__main__":
    main()
