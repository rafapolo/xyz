-- Mortalidade por alcool x perfil religioso do municipio, com controle negativo. 2022.
-- Gera dados/alcool_falseamento_2022.json, consumido por alcool_falseamento.py.
--
-- A HIPOTESE
-- A abstinencia alcoolica e doutrinaria e explicita em boa parte das igrejas
-- evangelicas — e o mecanismo mais direto que existe entre religiao e causa de
-- morte. Se ele for real, municipios com mais evangelicos devem ter menos
-- obitos por doenca alcoolica do figado (K70) e por transtornos mentais
-- devidos ao alcool (F10).
--
-- O TESTE DE FALSEAMENTO
-- O problema e que municipios diferem em muita coisa alem de religiao, e quase
-- tudo passa por acesso a servico de saude e qualidade do registro de obito.
-- Por isso a consulta traz tambem causas que NAO tem relacao com alcool mas
-- TEM com acesso e registro:
--
--   apendicite, hernia, colelitiase  -> morte por doenca cirurgicamente curavel.
--       Morrer disso e falha de acesso, nao de comportamento.
--   causas mal definidas (R95-R99)   -> indicador classico de qualidade do
--       registro: onde se investiga pouco, muita morte vira "causa mal definida".
--
-- Fratura de femur foi tentada e descartada: S72 quase nunca aparece como
-- causa BASICA no SIM (a queda, W00-W19, e que fica como causa basica e a
-- fratura vai para causa consequencial), entao o controle sairia vazio.
--
-- Se a diferenca aparecer em K70 e F10 mas NAO nesses, o mecanismo alcoolico
-- se sustenta. Se aparecer em tudo na mesma direcao, o que se mediu foi
-- servico de saude, nao doutrina — e a analise morre aqui.
--
-- CONTROLE DE ESPECIFICIDADE
-- Cirrose nao alcoolica (K71-K76) atinge o mesmo orgao pela via nao alcoolica.
-- Se o efeito for do alcool, K70 deve cair bem mais que K71-K76. Se os dois
-- cairem igual, e doenca hepatica em geral — provavelmente acesso outra vez.
--
-- DOSE-RESPOSTA
-- Em vez do corte binario de 20%, a consulta devolve faixas de % evangelica.
-- Mecanismo real produz gradiente monotono; confundimento por porte ou regiao
-- costuma produzir degrau.
--
-- Rodar no beelink:
--   ssh beelink '~/bin/duckdb -json' < query_alcool_falseamento.sql \
--     > alcool_falseamento_2022.json

WITH rel AS (
  SELECT id_localidade AS id_municipio,
         SUM(CASE WHEN religiao = 'Evangélicas' THEN populacao_10_mais END) * 100.0
           / SUM(CASE WHEN religiao = 'Total' THEN populacao_10_mais END) AS pct_ev,
         SUM(CASE WHEN religiao = 'Total' THEN populacao_10_mais END) AS pop10
  FROM read_parquet('/home/polo/rodado/br_ibge_censo2022_religiao/populacao_religiao/*.parquet')
  WHERE ano = 2022 AND LENGTH(id_localidade) = 7
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
         CASE WHEN r.pct_ev < 10 THEN '1. <10%'   WHEN r.pct_ev < 15 THEN '2. 10-15%'
              WHEN r.pct_ev < 20 THEN '3. 15-20%' WHEN r.pct_ev < 25 THEN '4. 20-25%'
              WHEN r.pct_ev < 30 THEN '5. 25-30%' WHEN r.pct_ev < 40 THEN '6. 30-40%'
              ELSE '7. 40%+' END AS faixa_ev,
         CASE WHEN r.pop10 <  10000 THEN 'P'  WHEN r.pop10 <  50000 THEN 'M'
              WHEN r.pop10 < 300000 THEN 'G'  ELSE 'XG' END AS porte
  FROM geo g JOIN rel r ON r.id_municipio = g.id_municipio
),
pop AS (
  SELECT m.regiao, m.porte, m.grupo, m.faixa_ev,
         CAST(regexp_extract(p.grupo_idade, '^\d+') AS INT) AS idade,
         SUM(p.populacao) AS valor
  FROM read_parquet('/home/polo/rodado/br_ibge_censo_2022/populacao_grupo_idade_sexo_raca/*.parquet') p
  JOIN mun m ON m.id_municipio = p.id_municipio
  WHERE p.ano = 2022 AND p.populacao IS NOT NULL
  GROUP BY 1,2,3,4,5
),
ob AS (
  SELECT m.regiao, m.porte, m.grupo, m.faixa_ev,
         LEAST(FLOOR(s.idade / 5) * 5, 100) AS idade,
         CASE
           -- ---- alcool: causas 100% atribuiveis ----
           WHEN SUBSTR(s.causa_basica,1,3) = 'K70' THEN 'K70 doenca alcoolica do figado'
           WHEN SUBSTR(s.causa_basica,1,3) = 'F10' THEN 'F10 transtornos por alcool'
           WHEN SUBSTR(s.causa_basica,1,4) IN ('K860','G312','G621','I426','K292','E244')
             OR SUBSTR(s.causa_basica,1,3) IN ('X45','X65','Y15','T51') THEN 'outras 100% alcool'
           -- ---- especificidade: mesmo orgao, via nao alcoolica ----
           WHEN SUBSTR(s.causa_basica,1,1) = 'K'
            AND TRY_CAST(SUBSTR(s.causa_basica,2,2) AS INT) BETWEEN 71 AND 76 THEN 'K71-76 cirrose nao alcoolica'
           -- ---- controles negativos: acesso a servico ----
           WHEN SUBSTR(s.causa_basica,1,1) = 'K'
            AND TRY_CAST(SUBSTR(s.causa_basica,2,2) AS INT) BETWEEN 35 AND 38 THEN 'CN apendicite'
           WHEN SUBSTR(s.causa_basica,1,1) = 'K'
            AND TRY_CAST(SUBSTR(s.causa_basica,2,2) AS INT) BETWEEN 40 AND 46 THEN 'CN hernia'
           WHEN SUBSTR(s.causa_basica,1,1) = 'K'
            AND TRY_CAST(SUBSTR(s.causa_basica,2,2) AS INT) BETWEEN 80 AND 81 THEN 'CN colelitiase'
           -- ---- controle negativo: qualidade do registro ----
           WHEN SUBSTR(s.causa_basica,1,1) = 'R'
            AND TRY_CAST(SUBSTR(s.causa_basica,2,2) AS INT) BETWEEN 95 AND 99 THEN 'CN causa mal definida'
           ELSE 'zz' END AS causa,
         COUNT(*) AS valor
  FROM read_parquet('/home/polo/rodado/br_ms_sim/microdados/*.parquet') s
  JOIN mun m ON m.id_municipio = s.id_municipio_residencia
  WHERE s.ano = 2022 AND s.idade IS NOT NULL AND s.idade <= 115
  GROUP BY 1,2,3,4,5,6
)
SELECT 'obito' AS tipo, regiao, porte, grupo, faixa_ev, idade, causa, valor
FROM ob WHERE causa <> 'zz'
UNION ALL
SELECT 'pop', regiao, porte, grupo, faixa_ev, idade, NULL, valor FROM pop;
