"""Presidente 2026, 1º turno (04/10/2026): TSE -> ../../data_presidente_2026.json.

Baixa o resultado de cada município do site de divulgação do TSE
(resultados.tse.jus.br, eleição 6257), junta com o centroide de
br_bd_diretorios_brasil.municipio no beelink e grava um registro por município
no mesmo layout de data.json (prefeitos 2024), com dois campos a mais:

  [uf, nome, lat, lon, tot, lean, polar, ncand, w1, w1pct, w2, w2pct,
   pesq, pcen, pdir, plula, pflavio, plula22, pbolso22]

plula22/pbolso22 são os votos de Lula e Bolsonaro no 1º turno de 2022 (% dos votos
válidos, br_tse_eleicoes.resultados_candidato_municipio), para achar quem trocou de lado.

O exterior (zz) fica de fora. Os JSON brutos vão para raw/ (fora do git);
rodar de novo pula o que já foi baixado.

    python3 dataviz/eleicoes/dados/presidente_2026/build.py
"""
import csv, io, json, os, subprocess, urllib.request
from concurrent.futures import ThreadPoolExecutor

HERE = os.path.dirname(os.path.abspath(__file__))
RAW = os.path.join(HERE, 'raw')
OUT = os.path.join(HERE, '..', '..', 'data_presidente_2026.json')
BASE = 'https://resultados.tse.jus.br/oficial/ele2026/6257'

# mesmas notas de query.sql (Bolognesi, Ribeiro & Codato; PL -> 8.5), mais as
# siglas que só aparecem em 2026 — ver metodologia.md
SCORES = {
    'PCO': 0.3, 'PCB': 0.5, 'UP': 0.5, 'PSTU': 0.6, 'PSOL': 1.3, 'PC do B': 1.7,
    'PT': 2.5, 'REDE': 3.3, 'PDT': 3.3, 'PSB': 3.7, 'PV': 4.1, 'CIDADANIA': 4.6,
    'SOLIDARIEDADE': 5.4, 'PMB': 5.5, 'MOBILIZA': 5.5, 'AVANTE': 5.6, 'MDB': 5.7,
    'PODE': 5.7, 'PSD': 5.9, 'AGIR': 6.0, 'PSDB': 6.0, 'PRD': 6.8, 'UNIÃO': 6.9,
    'PP': 7.0, 'REPUBLICANOS': 7.2, 'DC': 7.5, 'PRTB': 8.0, 'NOVO': 8.2, 'PL': 8.5,
    'MISSÃO': 7.8, 'DEMOCRATA': 5.0,
}

NOMES = {
    'FLAVIO BOLSONARO': 'Flávio Bolsonaro', 'LULA': 'Lula',
    'ESCRITOR AUGUSTO CURY': 'Augusto Cury', 'RENAN SANTOS': 'Renan Santos',
    'RONALDO CAIADO': 'Ronaldo Caiado', 'ZEMA': 'Zema', 'SAMARA': 'Samara',
    'HERTZ DIAS': 'Hertz Dias', 'CLARIANA BARAO': 'Clariana Barão',
    'EDMILSON COSTA': 'Edmilson Costa', 'VETERINÁRIO WILSON GRASSI': 'Wilson Grassi',
    'RUI COSTA PIMENTA': 'Rui Costa Pimenta',
}


# o centroide do IBGE de Vitória (ES) inclui Trindade e Martim Vaz, a ~1.200 km da costa, e cai
# no mar (lon -39,18); usa-se a coordenada da cidade, na ilha de Vitória
CENTROIDE_CORRIGIDO = {'3205309': (-20.3155, -40.3128)}


def get(url):
    err = None
    for _ in range(4):
        try:
            with urllib.request.urlopen(url, timeout=60) as r:
                return json.load(r)
        except Exception as e:
            err = e
    raise err


def baixa():
    os.makedirs(RAW, exist_ok=True)
    cm = get(f'{BASE}/config/mun-e006257-cm.json')
    jobs = [(uf['cd'], m['cd'], m['cdi']) for uf in cm['abr'] if uf['cd'] != 'zz' for m in uf['mu']]

    def um(job):
        uf, cd, _ = job
        path = os.path.join(RAW, f'{uf}{cd}.json')
        if not os.path.exists(path):
            with open(path, 'w') as f:
                json.dump(get(f'{BASE}/dados/{uf}/{uf}{cd}-c0001-e006257-u.json'), f)

    with ThreadPoolExecutor(16) as ex:
        list(ex.map(um, jobs))
    return jobs


def centroides():
    sql = """LOAD spatial; SET enable_progress_bar=false;
SELECT id_municipio, nome, round(ST_Y(centroide),4) lat, round(ST_X(centroide),4) lon
FROM read_parquet('~/rodado/br_bd_diretorios_brasil/municipio/*.parquet');"""
    out = subprocess.run(['ssh', os.environ.get('BEELINK_HOST', 'beelink'),
                          '~/bin/duckdb -readonly -csv ~/rodado/basedosdados.duckdb'],
                         input=sql, capture_output=True, text=True, check=True).stdout
    return {r['id_municipio']: r for r in csv.DictReader(io.StringIO(out))}


def votos2022():
    sql = """SET enable_progress_bar=false;
WITH t AS (SELECT id_municipio, sum(votos) tot,
  sum(votos) FILTER (WHERE numero_candidato='13') lula,
  sum(votos) FILTER (WHERE numero_candidato='22') bolso
  FROM read_parquet('~/rodado/br_tse_eleicoes/resultados_candidato_municipio/*.parquet')
  WHERE ano=2022 AND cargo='presidente' AND turno=1 GROUP BY id_municipio)
SELECT id_municipio, round(100.0*lula/tot,1) lula, round(100.0*bolso/tot,1) bolso FROM t WHERE tot>0;"""
    out = subprocess.run(['ssh', os.environ.get('BEELINK_HOST', 'beelink'),
                          '~/bin/duckdb -readonly -csv ~/rodado/basedosdados.duckdb'],
                         input=sql, capture_output=True, text=True, check=True).stdout
    return {r['id_municipio']: r for r in csv.DictReader(io.StringIO(out))}


def main():
    jobs = baixa()
    cent = centroides()
    v22 = votos2022()
    recs = []
    for uf, cd, cdi in jobs:
        d = json.load(open(os.path.join(RAW, f'{uf}{cd}.json')))
        assert d['s']['pst'] == '100,00', f'{uf}{cd} com seções por totalizar'
        cands = [(NOMES[c['nmu']], p['sg'], int(c['vap']))
                 for ag in d['carg'][0]['agr'] for p in ag['par'] for c in p['cand']]
        tot = sum(v for _, _, v in cands)
        if not tot:
            continue
        sc = [(SCORES[sg], v) for _, sg, v in cands]
        lean = sum(s * v for s, v in sc) / tot
        polar = max(0.0, sum(s * s * v for s, v in sc) / tot - lean ** 2) ** 0.5
        cands.sort(key=lambda c: -c[2])
        pct = lambda v: round(100 * v / tot, 1)
        voto = {n: v for n, _, v in cands}
        m = dict(cent[cdi])
        if cdi in CENTROIDE_CORRIGIDO:
            m['lat'], m['lon'] = CENTROIDE_CORRIGIDO[cdi]
        recs.append([
            uf.upper(), m['nome'], float(m['lat']), float(m['lon']), tot,
            round(lean, 3), round(polar, 3), sum(1 for c in cands if c[2]),
            f'{cands[0][0]} ({cands[0][1]})', pct(cands[0][2]),
            f'{cands[1][0]} ({cands[1][1]})', pct(cands[1][2]),
            pct(sum(v for s, v in sc if s < 4.0)),
            pct(sum(v for s, v in sc if 4.0 <= s <= 6.0)),
            pct(sum(v for s, v in sc if s > 6.0)),
            pct(voto['Lula']), pct(voto['Flávio Bolsonaro']),
            float(v22[cdi]['lula']) if cdi in v22 else None, float(v22[cdi]['bolso']) if cdi in v22 else None,
        ])
    recs.sort(key=lambda r: (r[0], r[1]))
    with open(OUT, 'w') as f:
        f.write('[\n' + ',\n'.join(json.dumps(r, ensure_ascii=False, separators=(',', ':')) for r in recs) + '\n]\n')
    print(len(recs), 'municípios ->', os.path.relpath(OUT))


if __name__ == '__main__':
    main()
