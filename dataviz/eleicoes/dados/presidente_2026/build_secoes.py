"""Presidente 2026, 1º turno, por local de votação e por seção: TSE -> ../../secoes/.

O recorte "Seções" do mapa. Afastado, um ponto por local de votação (a escola), com o
voto somado das suas seções; de perto, um ponto por seção, em espiral em volta do local
(todas as seções de um local têm a mesma coordenada).

  secoes/locais.json  colunar, um item por local, para caber em ~1 MB comprimido:
                      {"c": [[nome, partido], ...]   candidatos, na ordem dos votos
                       "ufs": [uf, ...], "muns": [municipio, ...]
                       "u", "z", "lv", "n": uf (índice), zona, número do local, nº de seções
                       "m", "lat", "lon": município (índice), lat e lon × 1e5 — em delta
                       "v": [[votos do candidato 1 em cada local], ...]}
  secoes/<uf>.json    [[zona, local, nome do local, [[secao, v1..v12], ...]], ...]
                      (o nome fica aqui, e não em locais.json, porque pesa quase metade dele)

v1..v12 são os votos válidos de cada candidato de "c". O navegador calcula o resto
(inclinação, polarização, vencedor) com as mesmas notas de build.py. O votável 28 fica
de fora: candidatura indeferida, os votos não contam como válidos — sem ele a soma das
seções fecha voto a voto com a divulgação (118.969.906).

- votos: votacao_secao_2026_BR.zip (dados abertos do TSE; o _BR é o de presidente)
- coordenada e nome do local: eleitorado_local_votacao_2026 (o mesmo de build_zonas.py),
  com o mesmo descarte de geocodificação a mais de MAX_KM do município; sem coordenada
  válida o local cai no ponto da sua zona naquele município (data_presidente_2026_zonas.json)

    python3 dataviz/eleicoes/dados/presidente_2026/build_secoes.py
"""
import json, os
from collections import defaultdict

from build import BASE, CENTROIDE_CORRIGIDO, NOMES, centroides, get
from build_zonas import MAX_KM, baixa_zip, km, le_csv, ZIPS, CDN

ZIPS['secao'] = f'{CDN}/votacao_secao/votacao_secao_2026_BR.zip'
HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, '..', '..', 'secoes')
ZONAS = os.path.join(HERE, '..', '..', 'data_presidente_2026_zonas.json')
FORA = {'95', '96', '28'}  # branco, nulo, candidatura indeferida
CANDIDATOS = {
    '13': ('LULA', 'PT'), '14': ('RENAN SANTOS', 'MISSÃO'), '16': ('HERTZ DIAS', 'PSTU'),
    '21': ('EDMILSON COSTA', 'PCB'), '22': ('FLAVIO BOLSONARO', 'PL'), '27': ('CLARIANA BARAO', 'DC'),
    '29': ('RUI COSTA PIMENTA', 'PCO'), '30': ('ZEMA', 'NOVO'), '35': ('VETERINÁRIO WILSON GRASSI', 'DEMOCRATA'),
    '55': ('RONALDO CAIADO', 'PSD'), '70': ('ESCRITOR AUGUSTO CURY', 'AVANTE'), '80': ('SAMARA', 'UP'),
}


def main():
    cm = get(f'{BASE}/config/mun-e006257-cm.json')
    tse2ibge = {(uf['cd'].upper(), m['cd'].lstrip('0')): m['cdi'] for uf in cm['abr'] if uf['cd'] != 'zz' for m in uf['mu']}
    cent = centroides()
    for cdi, (lat, lon) in CENTROIDE_CORRIGIDO.items():
        cent[cdi] = dict(cent[cdi], lat=lat, lon=lon)
    nome_mun = lambda uf, cd: cent[tse2ibge[(uf, cd)]]['nome']

    # votos por seção
    secao = defaultdict(lambda: defaultdict(int))   # (uf, zona, secao) -> nr -> votos
    local_de = {}                                   # (uf, zona, secao) -> (cd, local)
    nm_local = {}
    for r in le_csv(baixa_zip('secao'), 'votacao_secao_2026_BR.csv'):
        if r['CD_CARGO'] != '1' or r['NR_TURNO'] != '1' or r['SG_UF'] == 'ZZ' or r['NR_VOTAVEL'] in FORA:
            continue
        k = (r['SG_UF'], int(r['NR_ZONA']), int(r['NR_SECAO']))
        secao[k][r['NR_VOTAVEL']] += int(r['QT_VOTOS'])
        cd, lv = r['CD_MUNICIPIO'].lstrip('0'), int(r['NR_LOCAL_VOTACAO'])
        assert local_de.setdefault(k, (cd, lv)) == (cd, lv), f'seção em dois locais: {k}'
        nm_local.setdefault((k[0], k[1], lv), r['NM_LOCAL_VOTACAO'].strip())
    total = sum(sum(v.values()) for v in secao.values())
    assert total == 118969906, f'soma das seções {total} não fecha com a divulgação'

    # candidatos na ordem dos votos (número -> nome de urna e partido, como no munzona)
    zonas = json.load(open(ZONAS))
    por_nr = defaultdict(int)
    for v in secao.values():
        for nr, q in v.items():
            por_nr[nr] += q
    ordem = sorted(por_nr, key=lambda nr: -por_nr[nr])
    meta = [[NOMES[CANDIDATOS[nr][0]], CANDIDATOS[nr][1]] for nr in ordem]

    # coordenadas dos locais
    coord = {}
    for r in le_csv(baixa_zip('locais'), 'eleitorado_local_votacao_2026_BRASIL.csv'):
        if r['NR_TURNO'] != '1' or r['SG_UF'] == 'ZZ':
            continue
        k = (r['SG_UF'], int(r['NR_ZONA']), int(r['NR_LOCAL_VOTACAO']))
        if k in coord:
            continue
        lat, lon = float(r['NR_LATITUDE'].replace(',', '.')), float(r['NR_LONGITUDE'].replace(',', '.'))
        c = cent[tse2ibge[(r['SG_UF'], r['CD_MUNICIPIO'].lstrip('0'))]]
        if lat != -1 and lon != -1 and km((lat, lon), (float(c['lat']), float(c['lon']))) <= MAX_KM:
            coord[k] = (lat, lon)
    ponto_zona = {(r[0], r[1], r[19][0]): (r[2], r[3]) for r in zonas}

    # agrupa seções por local
    locais = defaultdict(list)  # (uf, zona, local) -> [(secao, votos)]
    mun_do_local = {}
    for (uf, zona, sec), v in secao.items():
        cd, lv = local_de[(uf, zona, sec)]
        locais[(uf, zona, lv)].append((sec, [v.get(nr, 0) for nr in ordem]))
        mun_do_local[(uf, zona, lv)] = cd

    muns, mi, ufs = [], {}, sorted({k[0] for k in locais})
    out_l, out_uf, sem_coord = [], defaultdict(list), 0
    for k in sorted(locais):
        uf, zona, lv = k
        secs = sorted(locais[k])
        nm = nome_mun(uf, mun_do_local[k])
        if (uf, nm) not in mi:
            mi[(uf, nm)] = len(muns)
            muns.append(nm)
        if k in coord:
            lat, lon = coord[k]
        else:
            sem_coord += 1
            lat, lon = ponto_zona[(uf, nm, zona)]
        soma = [sum(s[1][i] for s in secs) for i in range(len(ordem))]
        out_l.append([ufs.index(uf), mi[(uf, nm)], zona, lv, round(lat * 1e5), round(lon * 1e5), len(secs), soma])
        out_uf[uf].append([zona, lv, nm_local[k], [[s] + v for s, v in secs]])

    delta = lambda a: [a[0]] + [a[i] - a[i - 1] for i in range(1, len(a))]
    col = lambda i: [l[i] for l in out_l]
    os.makedirs(OUT, exist_ok=True)
    dump = lambda o: json.dumps(o, ensure_ascii=False, separators=(',', ':'))
    with open(os.path.join(OUT, 'locais.json'), 'w') as f:
        f.write(dump({'c': meta, 'ufs': ufs, 'muns': muns, 'u': col(0), 'm': delta(col(1)), 'z': col(2),
                      'lv': col(3), 'lat': delta(col(4)), 'lon': delta(col(5)), 'n': col(6),
                      'v': [[l[7][i] for l in out_l] for i in range(len(ordem))]}) + '\n')
    for uf, ls in out_uf.items():
        with open(os.path.join(OUT, f'{uf}.json'), 'w') as f:
            f.write('[\n' + ',\n'.join(dump(l) for l in ls) + '\n]\n')
    print(f'{len(out_l)} locais, {len(secao)} seções, {len(out_uf)} UFs -> {os.path.relpath(OUT)}; '
          f'{sem_coord} locais sem coordenada (ponto da zona)')


if __name__ == '__main__':
    main()
