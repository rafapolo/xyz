import csv
import json
import subprocess
from pathlib import Path

HERE = Path(__file__).parent
VERTENTES_CSV = HERE / "vertentes-religiosas.csv"
PADROES_CSV = HERE / "cnefe-descricao-vertente.csv"
PARQUET_OUT = HERE / "igrejas_geolocalizadas.parquet"
JSON_OUT = HERE.parent / "igrejas" / "data.json"

CNEFE_PATH = "/home/polo/rodado/br_ibge_censo_2022/cadastro_enderecos/*.parquet"
CNPJ_ESTAB_PATH = "/home/polo/rodado/br_me_cnpj/estabelecimentos/*.parquet"

# termos-raiz usados só pra decidir se um endereço é candidato a templo;
# a vertente em si vem do casamento mais especifico contra PADROES_CSV
TERMOS_CANDIDATOS = [
    "IGREJA", "TEMPLO", "CAPELA", "PAROQUIA", "CATEDRAL", "SANTUARIO", "DIOCESE",
    "CONGREGACAO", "ASSEMBLEIA", "MINISTERIO", "TERREIRO", "CANDOMBLE", "UMBANDA",
    "ESPIRITA", "SINAGOGA", "BUDISTA", "SANTOS DOS ULTIMOS DIAS",
    "TESTEMUNHA", "SALAO DO REINO", "KARDECISTA",
    # "MESQUITA" sozinho é sobrenome/homonimo comum (bar, mercado, advocacia
    # "Mesquita") - so entram como candidatas as grafias que de fato indicam
    # mesquita/centro islamico (revisao_fable, verificado contra os dados: de
    # 1205 linhas com "MESQUITA", so ~20-30 sao mesquitas reais)
    "MESQUITA ISLAMICA", "MESQUITA MUCULMANA", "MESQUITA MUSSULMANA",
    "MESQUITA ARABE", "MESQUITA AL HUDA", "MESQUITA DA PAZ", "MESQUITA SUNITA",
    "CENTRO ISLAMICO", "SOCIEDADE ISLAMICA", "MUSSALLA",
]


def carregar_padroes():
    with open(PADROES_CSV, encoding="utf-8") as f:
        rows = list(csv.DictReader(f))
    positivos = [r for r in rows if r["excluir"] != "true"]
    exclusoes = [r for r in rows if r["excluir"] == "true"]
    # mais especifico (string mais longa) primeiro
    positivos.sort(key=lambda r: len(r["padrao"]), reverse=True)
    return positivos, exclusoes


def sql_literal(s):
    return s.replace("'", "''")


def build_sql(uf_filtro=None):
    positivos, exclusoes = carregar_padroes()

    # NAO usamos mais TERMOS_CANDIDATOS pra decidir presenca de templo: o
    # CNEFE tem um campo estruturado oficial, tipo_especie='8' ("Estabelecimento
    # religioso"), preenchido pelo proprio recenseador em campo - e' o mesmo
    # criterio que da o numero oficial do IBGE (574.369 nacional vs 579.800
    # publicado, ~99% de match). Testamos cruzar com o filtro de texto livre
    # antigo: 85.931 templos que o IBGE marca como religioso nao batiam em
    # nenhum padrao de nome (sigla/nome incomum), e 215.688 que batiam em
    # texto NAO eram tipo_especie=8 (bar/deposito/fazenda/vago que so
    # coincidia ter "IGREJA" ou termo parecido no texto). Por isso viramos a
    # logica: tipo_especie='8' decide QUEM ENTRA; o dicionario de padroes so
    # decide EM QUAL VERTENTE, aplicado a todos os 574 mil, nao so aos que
    # batem em nome.
    exclusao_clause = " OR ".join(
        f"descricao_estabelecimento ILIKE '%{sql_literal(r['padrao'])}%'" for r in exclusoes
    ) or "FALSE"

    case_lines = "\n    ".join(
        f"WHEN descricao_estabelecimento ILIKE '%{sql_literal(r['padrao'])}%' THEN {r['vertente_id']}"
        for r in positivos
    )

    # Segunda camada, separada e identificada (`presenca='texto_livre'`):
    # enderecos com tipo_especie != 8 (nao confirmados oficialmente como
    # religiosos pelo IBGE) mas cujo texto livre bate num termo candidato -
    # descartados quando trocamos pro criterio oficial (ver nota acima), mas
    # sao um sinal real de templo informal. Decompondo os 215.688 que caem
    # aqui: 98,4% sao tipo_especie=6 "Estabelecimento de outras finalidades"
    # (o recenseador reconheceu como estabelecimento, so nao marcou
    # religioso mesmo com "IGREJA X" no texto). tipo_especie=1 (domicilio
    # particular) fica de fora: o campo descricao_estabelecimento
    # estruturalmente nao se aplica a residencia, entao nao ha sinal de
    # texto pra usar ali mesmo se quisessemos.
    candidato_clause = " OR ".join(
        f"descricao_estabelecimento ILIKE '%{sql_literal(t)}%'" for t in TERMOS_CANDIDATOS
    )

    uf_where = f"AND sigla_uf = '{uf_filtro}'" if uf_filtro else ""

    # Testamos casar por endereco completo (cep+numero+logradouro) e achamos
    # que, quando o logradouro NAO bate, na maioria das vezes e' porque sao
    # ruas de fato diferentes que coincidem em cep+numero (loteamentos com
    # "Rua 1", "Rua 2", "Rua 3"...), não diferenca de grafia - normalizar
    # nao resolveria e reintroduziria o mesmo falso-positivo que motivou
    # exigir o logradouro em primeiro lugar. Sem lat/lon no cadastro de CNPJ,
    # a alternativa e' relaxar pra "mesmo CEP" (sem exigir numero/logradouro):
    # mediana de 2 templos tipo_especie=8 por CEP que tem CNPJ religioso (bom
    # sinal de localidade), mas com cauda de CEPs muito grandes/rurais (ate
    # ~1000 templos no mesmo CEP) que dariam falsa confirmacao em massa - por
    # isso so contam CEPs com no maximo MAX_TEMPLOS_POR_CEP templos oficiais.
    MAX_TEMPLOS_POR_CEP = 15

    return f"""
INSTALL spatial; LOAD spatial;
CREATE TEMP TABLE cnae_religioso AS
  SELECT DISTINCT id_municipio, cep
  FROM read_parquet('{CNPJ_ESTAB_PATH}')
  WHERE cnae_fiscal_principal = '9491000'
    AND situacao_cadastral = '2'
    AND (ano * 100 + mes) = (SELECT MAX(ano * 100 + mes) FROM read_parquet('{CNPJ_ESTAB_PATH}'))
    AND cep IS NOT NULL;

CREATE TEMP TABLE templos_base AS
  SELECT *, 'oficial' AS presenca
  FROM read_parquet('{CNEFE_PATH}')
  WHERE tipo_especie = '8'
    AND latitude IS NOT NULL AND longitude IS NOT NULL
    {uf_where}
  UNION ALL BY NAME
  SELECT *, 'texto_livre' AS presenca
  FROM read_parquet('{CNEFE_PATH}')
  WHERE tipo_especie != '8'
    AND tipo_especie IS NOT NULL
    AND ({candidato_clause})
    AND latitude IS NOT NULL AND longitude IS NOT NULL
    {uf_where};

CREATE TEMP TABLE cep_templo_count AS
  SELECT id_municipio, cep, COUNT(*) n
  FROM templos_base
  WHERE presenca = 'oficial'
  GROUP BY 1, 2;

COPY (
  SELECT
    c.sigla_uf,
    c.id_municipio,
    TRY_CAST(c.latitude AS DOUBLE) AS lat,
    TRY_CAST(c.longitude AS DOUBLE) AS lon,
    c.nivel_geocodificacao_coordenadas,
    c.descricao_estabelecimento,
    c.tipo_especie,
    c.presenca,
    CASE
    {case_lines}
    ELSE NULL
    END AS vertente_id,
    (cn.cep IS NOT NULL AND ct.n <= {MAX_TEMPLOS_POR_CEP}) AS com_cnae
  FROM templos_base c
  LEFT JOIN cnae_religioso cn
    ON cn.id_municipio = c.id_municipio AND cn.cep = c.cep
  LEFT JOIN cep_templo_count ct
    ON ct.id_municipio = c.id_municipio AND ct.cep = c.cep
  WHERE NOT ({exclusao_clause})
) TO '/tmp/igrejas_geolocalizadas.parquet' (FORMAT PARQUET);
SELECT
  presenca,
  COUNT(*) AS total,
  SUM(CASE WHEN com_cnae THEN 1 ELSE 0 END) AS com_cnae
FROM read_parquet('/tmp/igrejas_geolocalizadas.parquet')
GROUP BY 1;
"""


def rodar_remoto(sql):
    script_path = "/tmp/gerar_igrejas.sql"
    subprocess.run(
        ["ssh", "beelink", f"cat > {script_path}"], input=sql, text=True, check=True
    )
    result = subprocess.run(
        ["ssh", "beelink", f"~/bin/duckdb -json -c \".read {script_path}\""],
        capture_output=True, text=True, check=True,
    )
    print(result.stdout)
    print(result.stderr[-2000:])


def main(uf_filtro=None):
    sql = build_sql(uf_filtro)
    rodar_remoto(sql)


if __name__ == "__main__":
    import sys
    uf = sys.argv[1] if len(sys.argv) > 1 else None
    main(uf)
