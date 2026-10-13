"""Censo do lote: por seção, quantos municípios saíram com `erro` ou `disponivel: false`.
Roda em ~/painel_lote no beelink: python3 lote_cobertura.py [todas]"""
import json,collections,glob,os,sys
N=None
for f in sorted(glob.glob("secoes/*.jsonl")):
    n=os.path.basename(f)[:-6]; c=collections.Counter(); ind=0; tot=0
    for l in open(f):
        d=json.loads(l); tot+=1
        if isinstance(d,dict):
            if "erro" in d: c[" ".join(d["erro"].split())[:110]]+=1
            elif d.get("disponivel") is False: ind+=1
    e=sum(c.values())
    if e or len(sys.argv)>1:
        print(f"{n:34s} erro={e:5d} indisp={ind:5d} de {tot}")
        for m,k in c.most_common(3): print(f"      {k:5d}  {m}")
