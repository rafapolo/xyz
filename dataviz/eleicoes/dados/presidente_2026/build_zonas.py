"""Presidente 2026, 1º turno, por zona eleitoral: TSE -> ../../data_presidente_2026_zonas.json.

Mesmo layout de data_presidente_2026.json (ver build.py), um registro por par
município × zona — o grão do arquivo do TSE: todo município aparece, uma capital se
parte nas suas zonas, e uma zona que cobre vários municípios pequenos vira um ponto
em cada um. Um campo a mais no fim:

  [uf, municipio, lat, lon, tot, lean, polar, ncand, w1, w1pct, w2, w2pct,
   pesq, pcen, pdir, plula, pflavio, plula22, pbolso22,
   [zona, zonas_no_municipio, outros_municipios_da_zona]]

plula/pflavio/plula22/pbolso22 com 2 casas (o resto com 1)

- votos: votacao_candidato_munzona_2026 (dados abertos do TSE, arquivo _BR = presidente)
- ponto: mediana, ponderada pelo eleitorado da seção, das coordenadas dos locais de
  votação do município naquela zona (eleitorado_local_votacao_2026); seções a mais de MAX_KM do
  centroide do próprio município são descartadas (há local geocodificado em
  Bangladesh). O corte é largo porque município da Amazônia tem seção rural a 200 km
  da sede; a mediana cuida do resto
- 2022: br_tse_eleicoes.resultados_candidato_municipio_zona no beelink. Houve
  rezoneamento, e uma zona que ganhou ou perdeu seções mostraria virada que é só
  mudança de território. Só entra quando o par (município, zona) existe em 2022 e
  o crescimento do voto dele ficou a RAZAO_OK do crescimento do município — assim
  cidade que só cresceu (Sorriso, Sinop) não cai junto com zona de capital que
  trocou seções com a vizinha

    python3 dataviz/eleicoes/dados/presidente_2026/build_zonas.py
"""
import csv, io, json, math, os, subprocess, urllib.request, zipfile
from collections import defaultdict

from build import BASE, CENTROIDE_CORRIGIDO, NOMES, RAW, SCORES, centroides, get

OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..', 'data_presidente_2026_zonas.json')
CDN = 'https://cdn.tse.jus.br/estatistica/sead/odsele'
ZIPS = {
    'munzona': f'{CDN}/votacao_candidato_munzona/votacao_candidato_munzona_2026.zip',
    'locais': f'{CDN}/eleitorado_locais_votacao/eleitorado_local_votacao_2026.zip',
}
MAX_KM = 250
RAZAO_OK = (0.9, 1.1)


def baixa_zip(nome):
    path = os.path.join(RAW, f'{nome}_2026.zip')
    if not os.path.exists(path):
        os.makedirs(RAW, exist_ok=True)
        urllib.request.urlretrieve(ZIPS[nome], path + '.part')
        os.rename(path + '.part', path)
    return path


def le_csv(zip_path, membro):
    with zipfile.ZipFile(zip_path) as z, z.open(membro) as f:
        yield from csv.DictReader(io.TextIOWrapper(f, encoding='latin-1'), delimiter=';')


def votos2022():
    sql = """SET enable_progress_bar=false;
SELECT sigla_uf uf, ltrim(id_municipio_tse,'0') cd, ltrim(zona,'0') zona, sum(votos) tot,
  sum(votos) FILTER (WHERE numero_candidato='13') lula,
  sum(votos) FILTER (WHERE numero_candidato='22') bolso
FROM read_parquet('~/rodado/br_tse_eleicoes/resultados_candidato_municipio_zona/*.parquet')
WHERE ano=2022 AND cargo='presidente' AND turno=1 GROUP BY ALL;"""
    out = subprocess.run(['ssh', os.environ.get('BEELINK_HOST', 'beelink'),
                          '~/bin/duckdb -readonly -csv ~/rodado/basedosdados.duckdb'],
                         input=sql, capture_output=True, text=True, check=True).stdout
    return {(r['uf'], r['cd'], r['zona']): (int(r['tot']), int(r['lula'] or 0), int(r['bolso'] or 0))
            for r in csv.DictReader(io.StringIO(out))}


def km(a, b):
    dy = (a[0] - b[0]) * 111.2
    dx = (a[1] - b[1]) * 111.2 * math.cos(math.radians((a[0] + b[0]) / 2))
    return math.hypot(dx, dy)


def mediana(pares):
    """mediana ponderada de [(valor, peso)]"""
    pares = sorted(pares)
    meio, acc = sum(p for _, p in pares) / 2, 0
    for v, p in pares:
        acc += p
        if acc >= meio:
            return v


def main():
    # TSE -> IBGE pelo mesmo arquivo de configuração que build.py usa
    cm = get(f'{BASE}/config/mun-e006257-cm.json')
    tse2ibge = {(uf['cd'].upper(), m['cd'].lstrip('0')): m['cdi'] for uf in cm['abr'] if uf['cd'] != 'zz' for m in uf['mu']}
    cent = centroides()
    for cdi, (lat, lon) in CENTROIDE_CORRIGIDO.items():
        cent[cdi] = dict(cent[cdi], lat=lat, lon=lon)
    v22 = votos2022()

    # votos por (município, zona)
    mz_cand = defaultdict(lambda: defaultdict(int))     # (uf, cd_tse, zona) -> nr -> votos
    info = {}                                           # nr -> (nome, partido)
    for r in le_csv(baixa_zip('munzona'), 'votacao_candidato_munzona_2026_BR.csv'):
        if r['SG_UF'] == 'ZZ' or r['NR_TURNO'] != '1':
            continue
        assert r['ST_VOTO_EM_TRANSITO'] == 'N' and r['NM_TIPO_DESTINACAO_VOTOS'] == 'Válido'
        k = (r['SG_UF'], r['CD_MUNICIPIO'].lstrip('0'), r['NR_ZONA'].lstrip('0'))
        mz_cand[k][r['NR_CANDIDATO']] += int(r['QT_VOTOS_NOMINAIS_VALIDOS'])
        info[r['NR_CANDIDATO']] = (NOMES[r['NM_URNA_CANDIDATO']], r['SG_PARTIDO'])
    nome = lambda uf, cd: cent[tse2ibge[(uf, cd)]]['nome']

    mun26, mun22 = defaultdict(int), defaultdict(int)
    zonas_mun, muns_zona = defaultdict(list), defaultdict(list)
    for (uf, cd, zona), cands in mz_cand.items():
        mun26[(uf, cd)] += sum(cands.values())
        zonas_mun[(uf, cd)].append(zona)
        muns_zona[(uf, zona)].append(cd)
    for (uf, cd, _), (t, _, _) in v22.items():
        mun22[(uf, cd)] += t

    # confere com o mapa por município (divulgação do TSE)
    por_mun = {(uf, nome(uf, cd)): t for (uf, cd), t in mun26.items()}
    mun = {(r[0], r[1]): r[4] for r in json.load(open(os.path.join(os.path.dirname(OUT), 'data_presidente_2026.json')))}
    difs = [(k, por_mun.get(k), t) for k, t in mun.items() if por_mun.get(k) != t]
    assert not difs, f'{len(difs)} municípios não batem com a divulgação: {difs[:5]}'

    # ponto: locais de votação do município naquela zona
    secoes = defaultdict(list)  # (uf, cd_tse, zona) -> [(lat, lon, eleitores)]
    descartadas = 0
    for r in le_csv(baixa_zip('locais'), 'eleitorado_local_votacao_2026_BRASIL.csv'):
        if r['NR_TURNO'] != '1' or r['SG_UF'] == 'ZZ':
            continue
        lat, lon = float(r['NR_LATITUDE'].replace(',', '.')), float(r['NR_LONGITUDE'].replace(',', '.'))
        if lat == -1 or lon == -1:
            continue
        cd = r['CD_MUNICIPIO'].lstrip('0')
        c = cent[tse2ibge[(r['SG_UF'], cd)]]
        if km((lat, lon), (float(c['lat']), float(c['lon']))) > MAX_KM:
            descartadas += 1
            continue
        secoes[(r['SG_UF'], cd, r['NR_ZONA'].lstrip('0'))].append((lat, lon, int(r['QT_ELEITOR_SECAO']) or 1))

    recs, sem_coord, sem22 = [], 0, []
    for (uf, cd, zona), cands in mz_cand.items():
        tot = sum(cands.values())
        if not tot:
            continue
        s = secoes.get((uf, cd, zona))
        if s:
            lat, lon = mediana([(a, p) for a, _, p in s]), mediana([(b, p) for _, b, p in s])
        else:
            sem_coord += 1
            c = cent[tse2ibge[(uf, cd)]]
            lat, lon = float(c['lat']), float(c['lon'])

        sc = [(SCORES[info[nr][1]], v) for nr, v in cands.items()]
        lean = sum(s_ * v for s_, v in sc) / tot
        polar = max(0.0, sum(s_ * s_ * v for s_, v in sc) / tot - lean ** 2) ** 0.5
        top = sorted(cands.items(), key=lambda x: -x[1])
        pct = lambda v, n=1: round(100 * v / tot, n)
        lab = lambda nr: f'{info[nr][0]} ({info[nr][1]})'

        # 2022 só se o pedaço (município, zona) tem o mesmo território: mesmo par em 2022 e
        # crescimento do voto a RAZAO_OK do crescimento do município
        p22 = v22.get((uf, cd, zona))
        l22 = b22 = None
        if p22:
            r_ = (tot / p22[0]) / (mun26[(uf, cd)] / mun22[(uf, cd)])
            if RAZAO_OK[0] <= r_ <= RAZAO_OK[1]:
                l22, b22 = round(100 * p22[1] / p22[0], 2), round(100 * p22[2] / p22[0], 2)
            else:
                sem22.append((uf, nome(uf, cd), zona, 'território mudou', round(r_, 2)))
        else:
            sem22.append((uf, nome(uf, cd), zona, 'zona nova ou recomposta', None))

        recs.append([
            uf, nome(uf, cd), round(lat, 4), round(lon, 4), tot,
            round(lean, 3), round(polar, 3), sum(1 for v in cands.values() if v),
            lab(top[0][0]), pct(top[0][1]), lab(top[1][0]), pct(top[1][1]),
            pct(sum(v for s_, v in sc if s_ < 4.0)),
            pct(sum(v for s_, v in sc if 4.0 <= s_ <= 6.0)),
            pct(sum(v for s_, v in sc if s_ > 6.0)),
            # 2 casas: com 1, Canutama (AM) empata e Flávio venceu por 2 votos
            pct(cands.get('13', 0), 2), pct(cands.get('22', 0), 2), l22, b22,
            [int(zona), len(zonas_mun[(uf, cd)]),
             sorted(nome(uf, o) for o in muns_zona[(uf, zona)] if o != cd)],
        ])
    recs.sort(key=lambda r: (r[0], r[1], r[19][0]))
    with open(OUT, 'w') as f:
        f.write('[\n' + ',\n'.join(json.dumps(r, ensure_ascii=False, separators=(',', ':')) for r in recs) + '\n]\n')

    print(len(recs), 'pares município × zona ->', os.path.relpath(OUT))
    print(f'{descartadas} seções descartadas por estarem a mais de {MAX_KM} km do município; '
          f'{sem_coord} pares sem coordenada (centroide do município)')
    print(f'{len(sem22)} pares sem comparação com 2022:')
    for z in sem22:
        print('  ', *z)

if __name__ == '__main__':
    main()
