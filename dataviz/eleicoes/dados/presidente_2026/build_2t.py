"""Presidente 2026, 2º turno (25/10/2026): beelink -> ../../data_presidente_2026_2t.json,
../../data_presidente_2026_2t_zonas.json e ../../secoes_2t/.

Os três recortes nos mesmos layouts de build.py, build_zonas.py e build_secoes.py, e com o
mesmo código, trocando a origem:

- votos: br_tse_eleicoes.resultados_candidato_{municipio,municipio_zona,secao}, ano 2026,
  turno 2, que a Base dos Dados publicou em 28/10 e que fecham entre si e com a divulgação
- local de cada seção e coordenada: eleitorado_local_votacao_2026 do TSE, NR_TURNO 2 (regerado
  em 25/10: há seções que votaram noutro local no 2º turno, e o arquivo do espelho só tem o 1º)
- 2022: o 2º turno de 2022 (Lula × Bolsonaro), para comparar turno decisivo com turno decisivo

O exterior (ZZ) fica de fora do mapa, mas entra na conferência dos totais nacionais.

    python3 dataviz/eleicoes/dados/presidente_2026/build_2t.py
    python3 dataviz/eleicoes/dados/presidente_2026/build_busca.py secoes_2t
"""
import csv, io, os, subprocess
from collections import defaultdict

import build, build_secoes, build_zonas
from build import CENTROIDE_CORRIGIDO, centroides, registro, votos2022
from build_secoes import CANDIDATOS
from build_zonas import CDN, ZIPS, baixa_zip, le_csv

HERE = os.path.dirname(os.path.abspath(__file__))
OUT_MUN = os.path.join(HERE, '..', '..', 'data_presidente_2026_2t.json')
OUT_ZONAS = os.path.join(HERE, '..', '..', 'data_presidente_2026_2t_zonas.json')
OUT_SECOES = os.path.join(HERE, '..', '..', 'secoes_2t')
# baixado de novo: o zip de raw/ usado no 1º turno é de antes do 2º
ZIPS['locais2t'] = f'{CDN}/eleitorado_locais_votacao/eleitorado_local_votacao_2026.zip'
OFICIAL = {'13': 64256232, '22': 59826041}  # divulgação do TSE, com o exterior
VALIDOS = 124082273


def sql(tabela, chaves):
    q = f"""SET enable_progress_bar=false;
SELECT {chaves}, numero_candidato nr, sum(votos) v
FROM read_parquet('~/rodado/br_tse_eleicoes/{tabela}/*.parquet')
WHERE ano=2026 AND turno=2 AND cargo='presidente' GROUP BY ALL;"""
    out = subprocess.run(['ssh', os.environ.get('BEELINK_HOST', 'beelink'),
                          '~/bin/duckdb -readonly -csv ~/rodado/basedosdados.duckdb'],
                         input=q, capture_output=True, text=True, check=True).stdout
    rows = list(csv.DictReader(io.StringIO(out)))
    total = defaultdict(int)
    for r in rows:
        r['v'] = int(r['v'])
        total[r['nr']] += r['v']
    assert dict(total) == OFICIAL and sum(total.values()) == VALIDOS, f'{tabela} não fecha com a divulgação: {dict(total)}'
    print(f'{tabela}: Lula {total["13"]:,} Flávio {total["22"]:,} válidos {sum(total.values()):,} (com o exterior)')
    return [r for r in rows if r['uf'] != 'ZZ']


def main():
    cent = centroides()
    for cdi, (lat, lon) in CENTROIDE_CORRIGIDO.items():
        cent[cdi] = dict(cent[cdi], lat=lat, lon=lon)
    info = {nr: (build.NOMES[CANDIDATOS[nr][0]], CANDIDATOS[nr][1]) for nr in OFICIAL}

    # município
    por_mun = defaultdict(dict)
    for r in sql('resultados_candidato_municipio', 'sigla_uf uf, id_municipio cdi'):
        por_mun[(r['uf'], r['cdi'])][r['nr']] = r['v']
    v22 = votos2022(2)
    recs = []  # 2 casas em Lula e Flávio: com 1, municípios decididos por poucos votos empatam
    for (uf, cdi), votos in por_mun.items():
        cands = [(*info[nr], votos.get(nr, 0)) for nr in OFICIAL]
        p = v22.get(cdi)
        recs.append(registro(uf, cent[cdi], cands, float(p['lula']) if p else None, float(p['bolso']) if p else None, casas=2))
    build.escreve(recs, OUT_MUN)

    # município × zona
    tse2ibge = {}
    mz_cand = defaultdict(lambda: defaultdict(int))
    for r in sql('resultados_candidato_municipio_zona', "sigla_uf uf, id_municipio cdi, ltrim(id_municipio_tse,'0') cd, ltrim(zona,'0') zona"):
        tse2ibge[(r['uf'], r['cd'])] = r['cdi']
        mz_cand[(r['uf'], r['cd'], r['zona'])][r['nr']] += r['v']
    build_zonas.escreve(mz_cand, info, tse2ibge, cent, build_zonas.votos2022(2), 'locais2t', '2', OUT_ZONAS,
                        mun_json=os.path.basename(OUT_MUN))

    # seção: o local vem do arquivo do 2º turno
    onde = {}
    for r in le_csv(baixa_zip('locais2t'), 'eleitorado_local_votacao_2026_BRASIL.csv'):
        if r['NR_TURNO'] == '2' and r['SG_UF'] != 'ZZ':
            onde[(r['SG_UF'], int(r['NR_ZONA']), int(r['NR_SECAO']))] = (
                r['CD_MUNICIPIO'].lstrip('0'), int(r['NR_LOCAL_VOTACAO']), r['NM_LOCAL_VOTACAO'].strip())
    secao = defaultdict(lambda: defaultdict(int))
    local_de, nm_local = {}, {}
    for r in sql('resultados_candidato_secao', "sigla_uf uf, ltrim(id_municipio_tse,'0') cd, CAST(zona AS INT) zona, CAST(secao AS INT) secao"):
        k = (r['uf'], int(r['zona']), int(r['secao']))
        secao[k][r['nr']] += r['v']
        cd, lv, nm = onde[k]
        assert cd == r['cd'], f'seção em outro município: {k}'
        local_de[k] = (cd, lv)
        nm_local.setdefault((k[0], k[1], cd, lv), nm)
    build_secoes.escreve(secao, local_de, nm_local, tse2ibge, cent, 'locais2t', '2', OUT_ZONAS, OUT_SECOES)


if __name__ == '__main__':
    main()
