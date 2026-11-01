"""Coordenada de cada local de votação, conferida contra o polígono do próprio município.

O TSE georreferencia os locais, mas não todos e nem sempre certo: há escola de Minduri (MG) no
centro de Belo Horizonte, a 194 km, e local geocodificado em Bangladesh. Antes valia qualquer
ponto a até 250 km do centroide do município, o que deixava passar esses erros. Agora o ponto
precisa cair dentro do polígono do município (br_geobr_mapas.municipio), com TOL_KM de folga para
a divisa simplificada, e a coordenada é a primeira que passa, nesta ordem:

  1. 'TSE 2026'      a do próprio arquivo de locais do turno, se não é a mesma de REPETIDA ou
                     mais locais do município (a sede no lugar da escola rural: essa fica por
                     último, como 'TSE 2026, coordenada repetida', se nada abaixo der certo)
  2. 'TSE <ano>'     o mesmo local (município, zona, número) no cadastro do 1º turno de 2026, de
                     2024 ou de 2022, se o nome é parecido ou o endereço é o mesmo
  3. 'TSE endereço'  outro local do mesmo município no mesmo endereço, em 2022–2026
  4. 'CNEFE ...'     estimativa pelo cadastro de endereços do Censo 2022: escola de mesmo nome no
                     município, centro do CEP ou centro do bairro/povoado. Primeiro a tabela
                     br_rodado_eleicoes.local_2026_coord_cnefe (os locais sem coordenada do 1º
                     turno); o que ainda falta vai numa consulta ao CNEFE no beelink, com o mesmo
                     método (scripts/eleicoes_setor/local_2026_coord_cnefe.sql, no repo rodado)
  5. nenhuma         o local cai no ponto da sua zona, como antes

Município sem polígono (Boa Esperança do Norte, MT, criado depois da malha) mantém a regra antiga
dos MAX_KM do centroide.

Arquivos em raw/ (fora do git), exportados do beelink uma vez:
  mun_geobr.parquet               id_municipio, wkb
  locais_tse_antigos.parquet      perfil_eleitorado_local_votacao, 1º turno de 2022, 2024 e 2026,
                                  com coordenada
  local_2026_coord_cnefe.parquet  a tabela do item 4
  cnefe_extra_<turno>.json        cache da consulta ao CNEFE do item 4
"""
import csv, io, json, math, os, re, subprocess, unicodedata

from collections import defaultdict

import pyarrow.parquet as pq
from shapely import wkb as shp_wkb
from shapely.geometry import Point
from shapely.prepared import prep

HERE = os.path.dirname(os.path.abspath(__file__))
RAW = os.path.join(HERE, 'raw')
TOL_KM = 2.0     # divisa do geobr é simplificada: 556 locais caíam a menos de 1 km do lado de fora
MAX_KM = 250     # só para município sem polígono
REPETIDA = 3     # locais do mesmo município na mesma coordenada do TSE
BEELINK = os.environ.get('BEELINK_HOST', 'beelink')


def norm(s):
    s = unicodedata.normalize('NFKD', (s or '').upper()).encode('ascii', 'ignore').decode()
    return ' '.join(re.findall(r'[A-Z0-9]+', s))


def km_centroide(a, b):
    dy = (a[0] - b[0]) * 111.2
    dx = (a[1] - b[1]) * 111.2 * math.cos(math.radians((a[0] + b[0]) / 2))
    return math.hypot(dx, dy)


class Geo:
    def __init__(self, tse2ibge, cent):
        self.tse2ibge, self.cent = tse2ibge, cent
        t = pq.read_table(os.path.join(RAW, 'mun_geobr.parquet')).to_pylist()
        self.geom = {r['id_municipio']: shp_wkb.loads(r['wkb']) for r in t}
        self.prep = {k: prep(g) for k, g in self.geom.items()}
        self._cache = {}

    def dist_km(self, uf, cd, lat, lon):
        """0 dentro do município; fora, distância aproximada até a divisa; None sem polígono"""
        cdi = self.tse2ibge[(uf, cd)]
        k = (cdi, lat, lon)
        if k not in self._cache:
            if cdi not in self.geom:
                self._cache[k] = None
            else:
                p = Point(lon, lat)
                self._cache[k] = 0.0 if self.prep[cdi].contains(p) else self.geom[cdi].distance(p) * 111.2
        return self._cache[k]

    def ok(self, uf, cd, lat, lon):
        if lat is None or lon is None or lat in (-1, 0) or lon in (-1, 0):
            return False
        d = self.dist_km(uf, cd, lat, lon)
        if d is None:
            c = self.cent[self.tse2ibge[(uf, cd)]]
            return km_centroide((lat, lon), (float(c['lat']), float(c['lon']))) <= MAX_KM
        return d <= TOL_KM

    def resolve(self, locais, turno, mesmo_local):
        """locais: {(uf, zona, cd, lv): {nome, endereco, bairro, cep, lat, lon}} -> {chave: (lat, lon, origem)}"""
        antigos, por_end = {}, {}
        rows = pq.read_table(os.path.join(RAW, 'locais_tse_antigos.parquet')).to_pylist()
        for r in sorted(rows, key=lambda r: r['ano']):  # o mais recente sobrescreve
            antigos.setdefault((r['cd'], int(r['zona']), int(r['numero'])), {})[r['ano']] = r
            if r['endereco']:
                por_end[(r['cd'], norm(r['endereco']))] = r
        cnefe = {(r['id_municipio_tse'], int(r['zona']), int(r['numero'])): r for r in
                 pq.read_table(os.path.join(RAW, 'local_2026_coord_cnefe.parquet')).to_pylist()}

        # a mesma coordenada do TSE em REPETIDA ou mais locais do município é, quase sempre, a sede
        # posta no lugar da escola rural: fica para o fim, depois das outras origens
        rep = defaultdict(int)
        for (uf, zona, cd, lv), l in locais.items():
            rep[(cd, l['lat'], l['lon'])] += 1
        coord, falta, suspeita = {}, [], {}
        for k, l in locais.items():
            uf, zona, cd, lv = k
            cands = []
            if rep[(cd, l['lat'], l['lon'])] >= REPETIDA:
                if self.ok(uf, cd, l['lat'], l['lon']):
                    suspeita[k] = (l['lat'], l['lon'], 'TSE 2026, coordenada repetida')
            else:
                cands.append((l['lat'], l['lon'], 'TSE 2026'))
            for ano, r in sorted(antigos.get((cd, zona, lv), {}).items(), reverse=True):
                if mesmo_local(r['nome'] or '', l['nome']) or (l['endereco'] and norm(r['endereco']) == norm(l['endereco'])):
                    cands.append((r['lat'], r['lon'], f'TSE {ano}'))
            r = por_end.get((cd, norm(l['endereco']))) if norm(l['endereco']) else None
            if r:
                cands.append((r['lat'], r['lon'], 'TSE endereço'))
            r = cnefe.get((cd, zona, lv))
            if r:
                cands.append((r['latitude'], r['longitude'], r['origem_coord']))
            for lat, lon, origem in cands:
                if self.ok(uf, cd, lat, lon):
                    coord[k] = (lat, lon, origem)
                    break
            else:
                falta.append(k)

        for k, (lat, lon, origem) in self.cnefe_extra(falta, locais, turno).items():
            if self.ok(k[0], k[2], lat, lon):
                coord[k] = (lat, lon, origem)
        for k, c in suspeita.items():
            coord.setdefault(k, c)
        return coord

    def cnefe_extra(self, chaves, locais, turno):
        """estimativa pelo CNEFE dos locais que ainda não têm coordenada válida (cache em raw/)"""
        cache = os.path.join(RAW, f'cnefe_extra_{turno}.json')
        pedidas = sorted('|'.join(map(str, k)) for k in chaves)
        if os.path.exists(cache):
            c = json.load(open(cache))
            if set(pedidas) <= set(c['pedidas']):
                return {tuple(int(x) if i in (1, 3) else x for i, x in enumerate(s.split('|'))): tuple(v)
                        for s, v in c['res'].items() if s in set(pedidas)}
        buf = io.StringIO()
        w = csv.writer(buf)
        w.writerow(['chave', 'id_municipio', 'nome', 'cep', 'bairro', 'endereco'])
        for k in chaves:
            l = locais[k]
            w.writerow(['|'.join(map(str, k)), self.tse2ibge[(k[0], k[2])], l['nome'], l['cep'], l['bairro'], l['endereco']])
        tmp = f'~/duckdb_tmp/cnefe_falta_{turno}.csv'
        subprocess.run(['ssh', BEELINK, f'cat > {tmp}'], input=buf.getvalue(), text=True, check=True)
        out = subprocess.run(['ssh', BEELINK, '~/bin/duckdb -readonly -csv ~/rodado/basedosdados.duckdb'],
                             input=SQL_CNEFE.replace('{TMP}', tmp), capture_output=True, text=True, check=True).stdout
        res = {r['chave']: (float(r['lat']), float(r['lon']), r['origem']) for r in csv.DictReader(io.StringIO(out))}
        json.dump({'pedidas': pedidas, 'res': res}, open(cache, 'w'), ensure_ascii=False)
        return {tuple(int(x) if i in (1, 3) else x for i, x in enumerate(s.split('|'))): v for s, v in res.items()}


# o mesmo método de scripts/eleicoes_setor/local_2026_coord_cnefe.sql (repo rodado), sobre a lista enviada
_GEN = ("'ESCOLA','ESC','EE','EM','EMEF','EMEI','EMEIEF','EEF','EEEF','EEEFM','EEFM','CEI','CMEI','COLEGIO','COL',"
        "'MUNICIPAL','MUN','ESTADUAL','EST','ENSINO','FUNDAMENTAL','FUND','MEDIO','INFANTIL','EDUCACAO','EDUCACIONAL',"
        "'EDUC','CENTRO','DE','DA','DO','DAS','DOS','PROF','PROFESSOR','PROFESSORA','PROFA','UNIDADE','ESCOLAR','PREDIO',"
        "'INTEGRAL','TEMPO','CRECHE','INSTITUTO','GRUPO','REUNIDAS','REUNIDA','NUCLEO','FEDERAL','UE','ETI','CIVICO',"
        "'MILITAR','MUNIC','ESTAD','ED','DR','DONA','DOM','SAO','SANTA','SANTO','EMR','EMEB','EEB','EB','CE','CIEP','UNID','ESCOLAS'")
_NL = lambda col: (f"array_to_string(list_filter(string_split(trim(regexp_replace(strip_accents(upper(coalesce({col}, ''))), "
                   f"'[^A-Z0-9]+', ' ', 'g')), ' '), lambda t: length(t) > 1 AND t NOT IN ({_GEN})), ' ')")
_REDE = lambda col: (f"CASE WHEN regexp_matches(strip_accents(upper({col})), '\\b(MUNICIPAL|MUN|EMEF|EMEI|EM|CMEI|EMEB)\\b') THEN 'M' "
                     f"WHEN regexp_matches(strip_accents(upper({col})), '\\b(ESTADUAL|EST|EE|EEEF|EEEFM|EEFM|CE)\\b') THEN 'E' END")
_LOC = lambda col: (f"trim(regexp_replace(regexp_replace(strip_accents(upper(coalesce({col}, ''))), '[^A-Z0-9]+', ' ', 'g'), "
                    f"'^(POVOADO|POV|DISTRITO|DIST|VILA|LOCALIDADE|COMUNIDADE|SITIO|FAZENDA|ASSENTAMENTO) (DE |DO |DA |DOS |DAS )?', ''))")
SQL_CNEFE = f"""SET enable_progress_bar=false;
WITH falta AS (
  SELECT chave, id_municipio::VARCHAR id_municipio, nome, cep::VARCHAR cep,
         {_NL('nome')} AS nl, {_REDE('nome')} AS rede, {_LOC('bairro')} AS lb,
         {_LOC("regexp_replace(endereco, ' - ZONA (RURAL|URBANA)$', '')")} AS le
  FROM read_csv('{{TMP}}', all_varchar=true)
),
cnefe AS NOT MATERIALIZED (
  SELECT COD_MUNICIPIO AS id_municipio, CEP AS cep, COD_ESPECIE AS esp, DSC_ESTABELECIMENTO AS dsc,
         DSC_LOCALIDADE AS localidade, LATITUDE::DOUBLE AS lat, LONGITUDE::DOUBLE AS lon
  FROM br_ibge_cnefe.enderecos WHERE COD_MUNICIPIO IN (SELECT id_municipio FROM falta)
),
est AS (
  SELECT id_municipio, cep, esp, lat, lon, {_NL('dsc')} AS nc, {_REDE('dsc')} AS rede
  FROM cnefe WHERE dsc IS NOT NULL AND esp IN ('2', '4', '5', '6', '8')
),
por_nome AS (
  SELECT f.chave,
         arg_max(e.lat, (e.cep = f.cep)::INT * 4 + (e.esp = '4')::INT * 2 + jaro_winkler_similarity(f.nl, e.nc)) AS lat,
         arg_max(e.lon, (e.cep = f.cep)::INT * 4 + (e.esp = '4')::INT * 2 + jaro_winkler_similarity(f.nl, e.nc)) AS lon,
         count(*) AS n, bool_or(e.cep = f.cep) AS mesmo_cep,
         max(e.lat) - min(e.lat) + max(e.lon) - min(e.lon) AS espalhamento
  FROM falta f JOIN est e ON e.id_municipio = f.id_municipio
  WHERE length(f.nl) >= 4 AND length(e.nc) >= least(4, length(f.nl))
    AND jaro_winkler_similarity(f.nl, e.nc) >= 0.95 AND coalesce(f.rede = e.rede, true)
  GROUP BY ALL HAVING n = 1 OR mesmo_cep OR espalhamento < 0.01
),
por_cep AS (
  SELECT cep, median(lat) AS lat, median(lon) AS lon
  FROM cnefe WHERE cep NOT LIKE '%000' AND cep IN (SELECT cep FROM falta) GROUP BY ALL
),
loc_alvo AS (
  SELECT id_municipio, localidade, l FROM (
    SELECT id_municipio, localidade, {_LOC('localidade')} AS l
    FROM (SELECT DISTINCT id_municipio, localidade FROM cnefe WHERE localidade IS NOT NULL))
  WHERE (id_municipio, l) IN (SELECT id_municipio, lb FROM falta WHERE length(lb) >= 4
                              UNION SELECT id_municipio, le FROM falta WHERE length(le) >= 4)
),
por_localidade AS (
  SELECT c.id_municipio, a.l, median(c.lat) AS lat, median(c.lon) AS lon
  FROM cnefe c JOIN loc_alvo a ON a.id_municipio = c.id_municipio AND a.localidade = c.localidade GROUP BY 1, 2
)
SELECT f.chave, round(coalesce(n.lat, c.lat, lb.lat, le.lat), 6) AS lat, round(coalesce(n.lon, c.lon, lb.lon, le.lon), 6) AS lon,
       CASE WHEN n.lat IS NOT NULL THEN 'CNEFE estabelecimento' WHEN c.lat IS NOT NULL THEN 'CNEFE centro do CEP'
            ELSE 'CNEFE centro do bairro/povoado' END AS origem
FROM falta f
LEFT JOIN por_nome n USING (chave)
LEFT JOIN por_cep c ON c.cep = f.cep
LEFT JOIN por_localidade lb ON lb.id_municipio = f.id_municipio AND lb.l = f.lb
LEFT JOIN por_localidade le ON le.id_municipio = f.id_municipio AND le.l = f.le
WHERE coalesce(n.lat, c.lat, lb.lat, le.lat) IS NOT NULL;"""
