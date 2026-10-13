#!/usr/bin/env python3
"""Compara dois JSON do painel (método antigo × lote), seção por seção.

    python3 compara_json.py ref/3303401.json json/3303401.json [-v]

Número bate com tolerância relativa de 1e-9 (a soma em ponto flutuante muda no
último dígito entre duas rodadas); o resto tem de ser idêntico. Lista com os
mesmos elementos em outra ordem sai como ORDEM, separada de VALOR.
"""
import json
import sys


def num(v):
    return isinstance(v, (int, float)) and not isinstance(v, bool)


def igual(a, b):
    if num(a) and num(b):
        return a == b or abs(a - b) <= 1e-9 * max(abs(a), abs(b))
    if type(a) is not type(b):
        return False
    if isinstance(a, dict):
        return a.keys() == b.keys() and all(igual(a[k], b[k]) for k in a)
    if isinstance(a, list):
        return len(a) == len(b) and all(igual(x, y) for x, y in zip(a, b))
    return a == b


def canon(v):
    if num(v):
        return float(f"{v:.9g}")
    if isinstance(v, dict):
        return {k: canon(x) for k, x in v.items()}
    if isinstance(v, list):
        return [canon(x) for x in v]
    return v


def difs(a, b, p, out):
    if igual(a, b):
        return
    if isinstance(a, dict) and isinstance(b, dict):
        if "erro" in a and "erro" in b:
            out.append(("ERRO-TEXTO", p, a["erro"][:80], b["erro"][:80]))
            return
        for k in sorted(set(a) | set(b)):
            if k not in a:
                out.append(("SO-NOVO", f"{p}.{k}", None, json.dumps(b[k], ensure_ascii=False)[:80]))
            elif k not in b:
                out.append(("SO-ANTIGO", f"{p}.{k}", json.dumps(a[k], ensure_ascii=False)[:80], None))
            else:
                difs(a[k], b[k], f"{p}.{k}", out)
    elif isinstance(a, list) and isinstance(b, list):
        ca = sorted(json.dumps(canon(x), sort_keys=True, ensure_ascii=False) for x in a)
        cb = sorted(json.dumps(canon(x), sort_keys=True, ensure_ascii=False) for x in b)
        if ca == cb:
            out.append(("ORDEM", p, f"{len(a)} itens", ""))
        elif len(a) != len(b):
            out.append(("TAMANHO", p, len(a), len(b)))
        else:
            for i, (x, y) in enumerate(zip(a, b)):
                difs(x, y, f"{p}[{i}]", out)
    else:
        out.append(("VALOR", p, json.dumps(a, ensure_ascii=False)[:80], json.dumps(b, ensure_ascii=False)[:80]))


def main():
    a, b = (json.load(open(f)) for f in sys.argv[1:3])
    verboso = "-v" in sys.argv
    out = []
    difs({k: v for k, v in a.items() if k != "gerado_em"}, {k: v for k, v in b.items() if k != "gerado_em"}, "", out)
    por = {}
    for d in out:
        sec = ".".join(d[1].split(".")[:4]).split("[")[0]
        por.setdefault(sec, []).append(d)
    for sec, ds in sorted(por.items()):
        tipos = sorted({d[0] for d in ds})
        print(f"{sec}: {len(ds)} diferença(s) [{', '.join(tipos)}]")
        for d in ds[: 40 if verboso else 3]:
            print(f"    {d[0]} {d[1]}: {d[2]!r} -> {d[3]!r}")
    print(f"{sys.argv[2]}: {len(out)} diferença(s) em {len(por)} bloco(s)")
    sys.exit(1 if out else 0)


if __name__ == "__main__":
    main()
