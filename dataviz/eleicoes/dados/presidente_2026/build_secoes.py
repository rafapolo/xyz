"""Presidente 2026, 1º turno, por local de votação e por seção: TSE -> ../../secoes/.

O recorte "Seções" do mapa. Afastado, um ponto por local de votação (a escola), com o
voto somado das suas seções; de perto, um ponto por seção, em espiral em volta do local
(todas as seções de um local têm a mesma coordenada).

  secoes/locais.json  colunar, um item por local, para caber em ~1 MB comprimido:
                      {"c": [[nome, partido], ...]   candidatos, na ordem dos votos
                       "ufs": [uf, ...], "muns": [municipio, ...]
                       "u", "z", "lv", "n": uf (índice), zona, número do local, nº de seções
                                    (o número do local só é único dentro do município: a chave
                                    de um local é uf + zona + município + número)
                       "m", "lat", "lon": município (índice), lat e lon × 1e5 — em delta
                       "v": [[votos do candidato 1 em cada local], ...]}
                       "l22", "b22": Lula e Bolsonaro no 1º turno de 2022, % dos válidos × 100,
                                    ou null (ver "2022" abaixo)
  secoes/<uf>.json    [[zona, local, município (índice), nome do local, [[secao, v1..v12, l22, b22], ...]], ...]
                      (o nome fica aqui, e não em locais.json, porque pesa quase metade dele)

v1..v12 são os votos válidos de cada candidato de "c". O navegador calcula o resto
(inclinação, polarização, vencedor) com as mesmas notas de build.py. O votável 28 fica
de fora: candidatura indeferida, os votos não contam como válidos — sem ele a soma das
seções fecha voto a voto com a divulgação (118.969.906).

- votos: votacao_secao_2026_BR.zip (dados abertos do TSE; o _BR é o de presidente)
- coordenada e nome do local: eleitorado_local_votacao_2026 (o mesmo de build_zonas.py),
  com o mesmo descarte de geocodificação a mais de MAX_KM do município; sem coordenada
  válida o local cai no ponto da sua zona naquele município (data_presidente_2026_zonas.json)

- 2022: br_tse_eleicoes.resultados_candidato_secao (votos) + perfil_eleitorado_local_votacao
  (local de cada seção) no beelink. O TSE renumera seções e remaneja eleitores entre
  elas, então uma seção só se compara quando é a mesma urna: mesmo município, zona,
  número e local, nome do local parecido (a escola muda de nome, "EMEF" -> "EMEB", mas
  o número de local às vezes passa para outro prédio) e voto válido que variou como o
  do próprio local (RAZAO_OK, como nas zonas, mais larga: seção é pequena). O local de votação, afastado, compara a
  soma só das suas seções comparáveis, e só quando elas são a maior parte do seu voto

    python3 dataviz/eleicoes/dados/presidente_2026/build_secoes.py
"""
import csv, io, json, os, re, subprocess, unicodedata
from collections import defaultdict

from build import BASE, CENTROIDE_CORRIGIDO, NOMES, centroides, get
from build_zonas import MAX_KM, baixa_zip, km, le_csv, ZIPS, CDN

ZIPS['secao'] = f'{CDN}/votacao_secao/votacao_secao_2026_BR.zip'
HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, '..', '..', 'secoes')
ZONAS = os.path.join(HERE, '..', '..', 'data_presidente_2026_zonas.json')
FORA = {'95', '96', '28'}  # branco, nulo, candidatura indeferida
# variação do voto da seção ÷ a do seu local: 90% das urnas ficam entre 0,91 e 1,09; o que passa
# da faixa é a cauda das que receberam ou perderam eleitores (P99 = 1,42)
RAZAO_OK = (0.8, 1.25)
LOCAL_MIN = 0.8  # fração do voto de 2026 do local que precisa vir de seções comparáveis
# palavras que todo nome de escola tem; o que sobra (o patrono, o bairro) é o que identifica
GENERICO = set('ESCOLA ESTADUAL MUNICIPAL COLEGIO CENTRO EDUCACAO INFANTIL ENSINO FUNDAMENTAL MEDIO '
               'DE DA DO DAS DOS E EM EMEF EMEI EMEIF CMEI EE UNIDADE ESC PROF PROFA PROFESSOR '
               'PROFESSORA CRECHE INSTITUTO UE EST MUN ESCOLAR GRUPO'.split())
CANDIDATOS = {
    '13': ('LULA', 'PT'), '14': ('RENAN SANTOS', 'MISSÃO'), '16': ('HERTZ DIAS', 'PSTU'),
    '21': ('EDMILSON COSTA', 'PCB'), '22': ('FLAVIO BOLSONARO', 'PL'), '27': ('CLARIANA BARAO', 'DC'),
    '29': ('RUI COSTA PIMENTA', 'PCO'), '30': ('ZEMA', 'NOVO'), '35': ('VETERINÁRIO WILSON GRASSI', 'DEMOCRATA'),
    '55': ('RONALDO CAIADO', 'PSD'), '70': ('ESCRITOR AUGUSTO CURY', 'AVANTE'), '80': ('SAMARA', 'UP'),
}


def palavras(nome):
    nome = unicodedata.normalize('NFKD', nome.upper()).encode('ascii', 'ignore').decode()
    return {t for t in re.findall(r'[A-Z0-9]+', nome) if t not in GENERICO and len(t) > 2}


def mesmo_local(a, b):
    a, b = palavras(a), palavras(b)
    if not a or not b:
        return not a and not b
    return len(a & b) / min(len(a), len(b)) >= 0.5


def votos2022():
    """(uf, cd, zona, secao) -> (local, nome do local, válidos, lula, bolsonaro), 1º turno de 2022"""
    sql = """SET enable_progress_bar=false;
WITH v AS (
  SELECT sigla_uf uf, ltrim(id_municipio_tse,'0') cd, CAST(zona AS INT) zona, CAST(secao AS INT) secao,
    sum(votos) tot, coalesce(sum(votos) FILTER (WHERE numero_candidato='13'), 0) lula,
    coalesce(sum(votos) FILTER (WHERE numero_candidato='22'), 0) bolso
  FROM read_parquet('~/rodado/br_tse_eleicoes/resultados_candidato_secao/*.parquet')
  WHERE ano=2022 AND cargo='presidente' AND turno=1 AND sigla_uf<>'ZZ' GROUP BY ALL),
l AS (
  SELECT DISTINCT sigla_uf uf, ltrim(id_municipio_tse,'0') cd, CAST(zona AS INT) zona, CAST(secao AS INT) secao,
    CAST(numero AS INT) lv, nome
  FROM read_parquet('~/rodado/br_tse_eleicoes/perfil_eleitorado_local_votacao/*.parquet')
  WHERE ano=2022 AND turno=1)
SELECT v.*, l.lv, l.nome FROM v JOIN l USING (uf, cd, zona, secao);"""
    out = subprocess.run(['ssh', os.environ.get('BEELINK_HOST', 'beelink'),
                          '~/bin/duckdb -readonly -csv ~/rodado/basedosdados.duckdb'],
                         input=sql, capture_output=True, text=True, check=True).stdout
    v22 = {(r['uf'], r['cd'], int(r['zona']), int(r['secao'])): (int(r['lv']), r['nome'], int(r['tot']), int(r['lula']), int(r['bolso']))
           for r in csv.DictReader(io.StringIO(out))}
    assert sum(x[2] for x in v22.values()) > 117_000_000, 'votos de 2022 por seção incompletos'
    return v22


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
        # o número do local se repete entre municípios da mesma zona: o local é (uf, zona, município, nº)
        nm_local.setdefault((k[0], k[1], cd, lv), r['NM_LOCAL_VOTACAO'].strip())
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
        k = (r['SG_UF'], int(r['NR_ZONA']), r['CD_MUNICIPIO'].lstrip('0'), int(r['NR_LOCAL_VOTACAO']))
        if k in coord:
            continue
        lat, lon = float(r['NR_LATITUDE'].replace(',', '.')), float(r['NR_LONGITUDE'].replace(',', '.'))
        c = cent[tse2ibge[(r['SG_UF'], r['CD_MUNICIPIO'].lstrip('0'))]]
        if lat != -1 and lon != -1 and km((lat, lon), (float(c['lat']), float(c['lon']))) <= MAX_KM:
            coord[k] = (lat, lon)
    ponto_zona = {(r[0], r[1], r[19][0]): (r[2], r[3]) for r in zonas}

    # 2022: candidata = mesma urna no mesmo local; depois o voto tem que ter variado como o do local
    v22 = votos2022()
    cand = {}
    for (uf, zona, sec), (cd, lv) in local_de.items():
        p = v22.get((uf, cd, zona, sec))
        if p and p[0] == lv and mesmo_local(p[1], nm_local[(uf, zona, cd, lv)]):
            cand[(uf, zona, sec)] = p
    t26, t22 = defaultdict(int), defaultdict(int)
    for k, p in cand.items():
        lk = (k[0], k[1]) + local_de[k]
        t26[lk] += sum(secao[k].values()); t22[lk] += p[2]
    comp = {}
    for k, p in cand.items():
        lk = (k[0], k[1]) + local_de[k]
        tot = sum(secao[k].values())
        if p[2] and tot and RAZAO_OK[0] <= (tot / p[2]) / (t26[lk] / t22[lk]) <= RAZAO_OK[1]:
            comp[k] = p
    pct22 = lambda p: (round(10000 * p[3] / p[2]), round(10000 * p[4] / p[2]))

    # agrupa seções por local
    locais = defaultdict(list)  # (uf, zona, cd, local) -> [(secao, votos + [l22, b22])]
    for (uf, zona, sec), v in secao.items():
        p = comp.get((uf, zona, sec))
        locais[(uf, zona) + local_de[(uf, zona, sec)]].append(
            (sec, [v.get(nr, 0) for nr in ordem] + (list(pct22(p)) if p else [None, None])))

    muns, mi, ufs = [], {}, sorted({k[0] for k in locais})
    out_l, out_uf, sem_coord, locais_comp = [], defaultdict(list), 0, 0
    for k in sorted(locais):
        uf, zona, cd, lv = k
        secs = sorted(locais[k])
        nm = nome_mun(uf, cd)
        if (uf, nm) not in mi:
            mi[(uf, nm)] = len(muns)
            muns.append(nm)
        if k in coord:
            lat, lon = coord[k]
        else:
            sem_coord += 1
            lat, lon = ponto_zona[(uf, nm, zona)]
        soma = [sum(s[1][i] for s in secs) for i in range(len(ordem))]
        # o local compara a soma das suas seções comparáveis, se elas são a maior parte do voto
        cs = [comp[(uf, zona, s)] for s, v in secs if (uf, zona, s) in comp]
        v_cs = sum(sum(v[:len(ordem)]) for s, v in secs if (uf, zona, s) in comp)
        l22 = b22 = None
        if cs and v_cs >= LOCAL_MIN * sum(soma):
            l22, b22 = pct22((None, None, sum(p[2] for p in cs), sum(p[3] for p in cs), sum(p[4] for p in cs)))
            locais_comp += 1
        out_l.append([ufs.index(uf), mi[(uf, nm)], zona, lv, round(lat * 1e5), round(lon * 1e5), len(secs), soma, l22, b22])
        out_uf[uf].append([zona, lv, mi[(uf, nm)], nm_local[k], [[s] + v for s, v in secs]])

    delta = lambda a: [a[0]] + [a[i] - a[i - 1] for i in range(1, len(a))]
    col = lambda i: [l[i] for l in out_l]
    os.makedirs(OUT, exist_ok=True)
    dump = lambda o: json.dumps(o, ensure_ascii=False, separators=(',', ':'))
    with open(os.path.join(OUT, 'locais.json'), 'w') as f:
        f.write(dump({'c': meta, 'ufs': ufs, 'muns': muns, 'u': col(0), 'm': delta(col(1)), 'z': col(2),
                      'lv': col(3), 'lat': delta(col(4)), 'lon': delta(col(5)), 'n': col(6),
                      'v': [[l[7][i] for l in out_l] for i in range(len(ordem))],
                      'l22': col(8), 'b22': col(9)}) + '\n')
    for uf, ls in out_uf.items():
        with open(os.path.join(OUT, f'{uf}.json'), 'w') as f:
            f.write('[\n' + ',\n'.join(dump(l) for l in ls) + '\n]\n')
    print(f'{len(out_l)} locais, {len(secao)} seções, {len(out_uf)} UFs -> {os.path.relpath(OUT)}; '
          f'{sem_coord} locais sem coordenada (ponto da zona)')
    # vira-casaca (Lula 2022 -> Flávio 2026) e o inverso, na mesma regra do mapa
    vira = lambda v, p: ('lost' if p[3] > p[4] and v.get('22', 0) > v.get('13', 0) else
                         'won' if p[4] > p[3] and v.get('13', 0) > v.get('22', 0) else None)
    n = defaultdict(int)
    for k, p in comp.items():
        n[vira(secao[k], p)] += 1
    print(f'2022: {len(comp)} seções comparáveis de {len(secao)} ({len(cand) - len(comp)} fora de RAZAO_OK, '
          f'{len(secao) - len(cand)} sem a mesma urna no mesmo local); {locais_comp} de {len(out_l)} locais comparáveis; '
          f'seções Lula -> Flávio: {n["lost"]}, Bolsonaro -> Lula: {n["won"]}')


if __name__ == '__main__':
    main()
