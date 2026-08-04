-- Mortalidade por causa x perfil religioso do municipio, 2022.
-- Gera dados/mortalidade_religiao_2022.json, consumido por mortalidade_religiao.py.
--
-- DESENHO
-- Compara municipios com mais de 20% de evangelicos contra o resto, em taxas
-- padronizadas por idade. Devolve as contagens cruas (obitos e populacao por
-- faixa quinquenal); a padronizacao direta e feita no script, para que o
-- estrato de comparacao possa ser trocado sem refazer a consulta.
--
-- OS DOIS CONFUNDIDORES QUE OBRIGAM A ESTRATIFICAR
-- 1. Idade. Municipios evangelicos sao mais jovens (ver
--    rodado/scripts/plot_estrutura_etaria_religiao_2010_2022.py), e idade
--    domina qualquer causa de morte. Dai a padronizacao.
-- 2. Porte. O corte de >20% pega 95% da populacao nas cidades de 300 mil+ e
--    so 49% nos municipios de menos de 10 mil — no topo ele e quase sinonimo
--    de "cidade grande". Sem estratificar por porte, toda doenca urbana
--    (tuberculose, HIV) aparece como "doenca de municipio evangelico".
-- A regiao entra pelo mesmo motivo do §10 do relatorio de polarizacao.
--
-- LEITURA
-- Isto compara LUGARES, nao PESSOAS. Municipio mais evangelico com menos
-- obitos por alcool nao autoriza dizer que evangelico bebe menos: e falacia
-- ecologica. O Censo so pergunta religiao a partir dos 10 anos, entao o
-- percentual e sobre a populacao de 10+.
--
-- Rodar no beelink, onde estao os parquets:
--   ssh beelink '~/bin/duckdb -json' < query_mortalidade_religiao.sql \
--     > mortalidade_religiao_2022.json

WITH rel AS (
  SELECT id_localidade AS id_municipio,
         SUM(CASE WHEN religiao = 'Evangélicas' THEN populacao_10_mais END) * 100.0
           / SUM(CASE WHEN religiao = 'Total' THEN populacao_10_mais END) AS pct_ev,
         SUM(CASE WHEN religiao = 'Total' THEN populacao_10_mais END) AS pop10
  FROM read_parquet('/home/polo/rodado/br_ibge_censo2022_religiao/populacao_religiao/*.parquet')
  WHERE ano = 2022 AND LENGTH(id_localidade) = 7   -- 7 digitos = municipio
  GROUP BY 1
),
geo AS (
  SELECT id_municipio,
    CASE WHEN any_value(sigla_uf) IN ('AC','AP','AM','PA','RO','RR','TO') THEN 'Norte'
         WHEN any_value(sigla_uf) IN ('AL','BA','CE','MA','PB','PE','PI','RN','SE') THEN 'Nordeste'
         WHEN any_value(sigla_uf) IN ('DF','GO','MT','MS') THEN 'Centro-Oeste'
         WHEN any_value(sigla_uf) IN ('ES','MG','RJ','SP') THEN 'Sudeste'
         ELSE 'Sul' END AS regiao
  FROM read_parquet('/home/polo/rodado/br_bd_diretorios_brasil/municipio/*.parquet')
  GROUP BY 1
),
mun AS (
  SELECT g.id_municipio, g.regiao,
         CASE WHEN r.pct_ev > 20 THEN 'alto' ELSE 'baixo' END AS grupo,
         CASE WHEN r.pop10 <  10000 THEN 'P'
              WHEN r.pop10 <  50000 THEN 'M'
              WHEN r.pop10 < 300000 THEN 'G'
              ELSE 'XG' END AS porte
  FROM geo g JOIN rel r ON r.id_municipio = g.id_municipio
),
pop AS (
  SELECT m.regiao, m.porte, m.grupo,
         CAST(regexp_extract(p.grupo_idade, '^\d+') AS INT) AS faixa,
         SUM(p.populacao) AS valor
  FROM read_parquet('/home/polo/rodado/br_ibge_censo_2022/populacao_grupo_idade_sexo_raca/*.parquet') p
  JOIN mun m ON m.id_municipio = p.id_municipio
  WHERE p.ano = 2022 AND p.populacao IS NOT NULL
  GROUP BY 1,2,3,4
),
ob AS (
  -- idade > 115 e erro de decodificacao do campo do SIM, nao idade real
  -- (mesma limpeza de rodado/scripts/plot_cancer_idade.py)
  SELECT m.regiao, m.porte, m.grupo,
         LEAST(FLOOR(s.idade / 5) * 5, 100) AS faixa,
         CASE
           WHEN SUBSTR(s.causa_basica,1,1)='A' AND TRY_CAST(SUBSTR(s.causa_basica,2,2) AS INT) BETWEEN 15 AND 19 THEN 'Tuberculose'
           WHEN SUBSTR(s.causa_basica,1,1)='B' AND TRY_CAST(SUBSTR(s.causa_basica,2,2) AS INT) BETWEEN 20 AND 24 THEN 'HIV/aids'
           WHEN SUBSTR(s.causa_basica,1,1)='B' AND TRY_CAST(SUBSTR(s.causa_basica,2,2) AS INT) BETWEEN 50 AND 54 THEN 'Malaria'
           WHEN SUBSTR(s.causa_basica,1,1)='U' THEN 'Covid'
           WHEN SUBSTR(s.causa_basica,1,1) IN ('A','B') THEN 'Infecciosas (resto)'
           WHEN SUBSTR(s.causa_basica,1,1)='C' AND TRY_CAST(SUBSTR(s.causa_basica,2,2) AS INT) BETWEEN 33 AND 34 THEN 'Cancer de pulmao'
           WHEN SUBSTR(s.causa_basica,1,3)='C53' THEN 'Cancer de colo do utero'
           WHEN SUBSTR(s.causa_basica,1,1)='C' THEN 'Neoplasias (resto)'
           WHEN SUBSTR(s.causa_basica,1,1)='E' AND TRY_CAST(SUBSTR(s.causa_basica,2,2) AS INT) BETWEEN 10 AND 14 THEN 'Diabetes'
           WHEN SUBSTR(s.causa_basica,1,3)='F10' THEN 'Transtornos por alcool'
           WHEN SUBSTR(s.causa_basica,1,3)='G30' OR SUBSTR(s.causa_basica,1,3) IN ('F00','F01','F02','F03') THEN 'Alzheimer/demencia'
           WHEN SUBSTR(s.causa_basica,1,1)='I' THEN 'Circulatorio'
           WHEN SUBSTR(s.causa_basica,1,1)='J' THEN 'Respiratorio'
           WHEN SUBSTR(s.causa_basica,1,3)='K70' THEN 'Doenca alcoolica do figado'
           WHEN SUBSTR(s.causa_basica,1,1)='K' AND TRY_CAST(SUBSTR(s.causa_basica,2,2) AS INT) BETWEEN 71 AND 76 THEN 'Cirrose (nao alcoolica)'
           WHEN SUBSTR(s.causa_basica,1,1)='O' THEN 'Materna'
           WHEN SUBSTR(s.causa_basica,1,1)='P' THEN 'Perinatal'
           WHEN SUBSTR(s.causa_basica,1,1)='X' AND TRY_CAST(SUBSTR(s.causa_basica,2,2) AS INT) BETWEEN 60 AND 84 THEN 'Suicidio'
           WHEN (SUBSTR(s.causa_basica,1,1)='X' AND TRY_CAST(SUBSTR(s.causa_basica,2,2) AS INT) BETWEEN 85 AND 99)
             OR (SUBSTR(s.causa_basica,1,1)='Y' AND TRY_CAST(SUBSTR(s.causa_basica,2,2) AS INT) BETWEEN  0 AND  9) THEN 'Homicidio'
           WHEN SUBSTR(s.causa_basica,1,1)='V' THEN 'Transporte'
           ELSE 'Outras' END AS causa,
         COUNT(*) AS valor
  FROM read_parquet('/home/polo/rodado/br_ms_sim/microdados/*.parquet') s
  JOIN mun m ON m.id_municipio = s.id_municipio_residencia
  WHERE s.ano = 2022 AND s.idade IS NOT NULL AND s.idade <= 115
  GROUP BY 1,2,3,4,5
)
SELECT 'obito' AS tipo, regiao, porte, grupo, faixa, causa, valor FROM ob
UNION ALL
SELECT 'pop', regiao, porte, grupo, faixa, NULL, valor FROM pop;
