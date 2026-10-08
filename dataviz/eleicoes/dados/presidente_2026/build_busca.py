"""Índice de busca por local de votação: secoes/locais.json + secoes/<uf>.json -> secoes/busca.json.

O nome da escola só vem nos arquivos por UF (build_secoes.py os separa porque pesam metade do
locais.json). A busca do mapa precisa dos nomes de todo o país sem baixar os 27 estados, então
este arquivo junta só o que ela usa, na mesma ordem de locais.json:
  {"ufs": [...], "muns": [...], "n": [nome do local], "u": [uf], "m": [município, em delta],
   "la", "lo": lat e lon × 1e5, em delta}
Roda depois de build_secoes.py, sem tocar no TSE:  python3 dataviz/eleicoes/dados/presidente_2026/build_busca.py
"""
import json, os
HERE = os.path.dirname(os.path.abspath(__file__))
S = os.path.join(HERE, '..', '..', 'secoes')
d = json.load(open(os.path.join(S, 'locais.json')))
nomes = {}
for uf in d['ufs']:
    for z, lv, m, nome, _ in json.load(open(os.path.join(S, uf + '.json'))):
        nomes[(uf, z, m, lv)] = nome
m = 0; n = []
for i in range(len(d['u'])):
    m += d['m'][i]
    n.append(nomes.get((d['ufs'][d['u'][i]], d['z'][i], m, d['lv'][i]), ''))
out = {'ufs': d['ufs'], 'muns': d['muns'], 'n': n, 'u': d['u'], 'm': d['m'], 'la': d['lat'], 'lo': d['lon']}
with open(os.path.join(S, 'busca.json'), 'w') as f:
    json.dump(out, f, ensure_ascii=False, separators=(',', ':'))
print(len(n), 'locais,', sum(1 for x in n if not x), 'sem nome,', round(os.path.getsize(os.path.join(S, 'busca.json')) / 1e6, 1), 'MB')
