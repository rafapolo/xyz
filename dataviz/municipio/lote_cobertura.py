"""Cobertura do lote por seção: em quantos municípios cada seção saiu com `erro` ou
com `disponivel: false`, e os motivos mais comuns.

Roda em ~/painel_lote (beelink), depois de `extract_lote.py`:
    python3 lote_cobertura.py                 # só as seções com falha
    python3 lote_cobertura.py todas           # todas as seções
    python3 lote_cobertura.py --json cobertura.json   # relatório completo, para publicar
"""
import collections
import glob
import json
import os
import sys
from datetime import date


def main():
    args = sys.argv[1:]
    saida = args[args.index("--json") + 1] if "--json" in args else None
    todas = "todas" in args or saida is not None
    rel = []
    for f in sorted(glob.glob("secoes/*.jsonl")):
        nome = os.path.basename(f)[:-6]
        erros, motivos_ind, ind, tot = collections.Counter(), collections.Counter(), 0, 0
        for linha in open(f, encoding="utf-8"):
            d = json.loads(linha)
            tot += 1
            if not isinstance(d, dict):
                continue
            if "erro" in d:
                erros[" ".join(str(d["erro"]).split())[:110]] += 1
            elif d.get("disponivel") is False:
                ind += 1
                motivos_ind[" ".join(str(d.get("motivo") or "sem motivo").split())[:110]] += 1
        e = sum(erros.values())
        rel.append({"secao": nome, "municipios": tot, "com_dado": tot - e - ind, "erro": e, "indisponivel": ind,
                    "pct_com_dado": round(100 * (tot - e - ind) / tot, 1) if tot else None,
                    "motivos": [{"n": n, "motivo": m} for m, n in (erros + motivos_ind).most_common(3)]})
    if saida:
        with open(saida, "w", encoding="utf-8") as fh:
            json.dump({"gerado_em": date.today().isoformat(), "secoes": rel}, fh, ensure_ascii=False, indent=1)
        print(f"{saida}: {len(rel)} seções")
    for r in rel:
        if r["erro"] or r["indisponivel"] or todas:
            print(f"{r['secao']:34s} erro={r['erro']:5d} indisp={r['indisponivel']:5d} de {r['municipios']}")
            for m in r["motivos"]:
                print(f"      {m['n']:5d}  {m['motivo']}")


if __name__ == "__main__":
    main()
