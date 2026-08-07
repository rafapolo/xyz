-- Mortalidade alcoolica x municipios SEM RELIGIAO, com teste de falseamento. 2022.
-- Gera dados/alcool_sem_religiao_2022.json, consumido por alcool_sem_religiao.py.
--
-- POR QUE ESTA CONSULTA EXISTE
-- O achado do alcool em municipios evangelicos (ver query_alcool_falseamento.sql)
-- e compativel com duas explicacoes que os dados de la nao separam:
--   (a) DOUTRINA — a abstinencia e regra escrita, e a regra e obedecida;
--   (b) SECULARIZACAO INVERSA — o que cai nao e o alcool por causa da igreja,
--       e sim algo que acompanha o mundo religioso em geral, seja ele qual for.
-- "Sem religiao" e o contraste que separa as duas. Se o alcool cair TAMBEM onde
-- ha mais gente sem religiao, a doutrina nao explica — o gradiente e de outra
-- coisa. Se subir, a leitura doutrinaria ganha forca.
--
-- POR QUE O CORTE E 10% E NAO 20%
-- Sem religiao e 9,28% do pais e tem mediana municipal de 4,21%. Acima de 20%
-- so ha 98 municipios, poucos demais. Acima de 10% ha 819, o bastante.
-- Nenhuma outra religiao do Censo 2022 permite sequer isso: espirita tem 11
-- municipios acima de 10%, umbanda e candomble tem ZERO (maximo nacional 9,32%).
--
-- O CONFUNDIDOR QUE ESTA CONSULTA PRECISA MATAR
-- Sem religiao e evangelico nao sao independentes: os dois crescem onde o
-- catolicismo recua. Sem separar, o efeito de um vaza no outro. Por isso a
-- consulta emite tambem o grupo evangelico (campo "e"), o que permite medir o
-- gradiente de sem-religiao DENTRO de cada estrato evangelico — se ele
-- sobreviver aos dois estratos, nao e o evangelico disfarcado.
--
-- O resto do desenho e identico ao do falseamento evangelico: mesmas causas,
-- mesmos controles negativos (acesso cirurgico e qualidade do registro),
-- mesma especificidade (cirrose nao alcoolica), contagens cruas por faixa
-- quinquenal para que a padronizacao direta seja feita no script.
--
-- LEITURA
-- Compara LUGARES, nao PESSOAS. O Censo so pergunta religiao a partir dos 10
-- anos, entao o percentual e sobre a populacao de 10+.
--
-- Rodar no beelink, onde estao os parquets:
--   ssh beelink '~/bin/duckdb -json' < query_alcool_sem_religiao.sql \
--     > alcool_sem_religiao_2022.json

WITH rel AS (
  SELECT id_localidade AS id_municipio,
         SUM(CASE WHEN religiao = 'Sem religião' THEN populacao_10_mais END) * 100.0
           / SUM(CASE WHEN religiao = 'Total' THEN populacao_10_mais END) AS pct_sr,
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
         CASE WHEN r.pct_sr > 10 THEN 'alto' ELSE 'baixo' END AS grupo,
         CASE WHEN r.pct_sr <  2.5 THEN '1. <2,5%'    WHEN r.pct_sr <  5 THEN '2. 2,5-5%'
              WHEN r.pct_sr <  7.5 THEN '3. 5-7,5%'   WHEN r.pct_sr < 10 THEN '4. 7,5-10%'
              WHEN r.pct_sr < 15   THEN '5. 10-15%'   WHEN r.pct_sr < 20 THEN '6. 15-20%'
              ELSE '7. 20%+' END AS faixa_sr,
         CASE WHEN r.pct_ev > 20 THEN 'ev_alto' ELSE 'ev_baixo' END AS grupo_ev,
         CASE WHEN r.pop10 <  10000 THEN 'P'  WHEN r.pop10 <  50000 THEN 'M'
              WHEN r.pop10 < 300000 THEN 'G'  ELSE 'XG' END AS porte
  FROM geo g JOIN rel r ON r.id_municipio = g.id_municipio
),
pop AS (
  SELECT m.regiao, m.porte, m.grupo, m.faixa_sr, m.grupo_ev,
         CAST(regexp_extract(p.grupo_idade, '^\d+') AS INT) AS idade,
         SUM(p.populacao) AS valor
  FROM read_parquet('/home/polo/rodado/br_ibge_censo_2022/populacao_grupo_idade_sexo_raca/*.parquet') p
  JOIN mun m ON m.id_municipio = p.id_municipio
  WHERE p.ano = 2022 AND p.populacao IS NOT NULL
  GROUP BY 1,2,3,4,5,6
),
ob AS (
  SELECT m.regiao, m.porte, m.grupo, m.faixa_sr, m.grupo_ev,
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
           -- ---- suicidio: o candidato que nunca passou por controle negativo ----
           WHEN SUBSTR(s.causa_basica,1,1) = 'X'
            AND TRY_CAST(SUBSTR(s.causa_basica,2,2) AS INT) BETWEEN 60 AND 84 THEN 'suicidio'
           ELSE 'zz' END AS causa,
         COUNT(*) AS valor
  FROM read_parquet('/home/polo/rodado/br_ms_sim/microdados/*.parquet') s
  JOIN mun m ON m.id_municipio = s.id_municipio_residencia
  WHERE s.ano = 2022 AND s.idade IS NOT NULL AND s.idade <= 115
  GROUP BY 1,2,3,4,5,6,7
)
SELECT 'o' AS t, regiao AS r, porte AS p, grupo AS g, faixa_sr AS b,
       grupo_ev AS e, idade AS i, causa AS c, valor AS v
FROM ob WHERE causa <> 'zz'
UNION ALL
SELECT 'p', regiao, porte, grupo, faixa_sr, grupo_ev, idade, NULL, valor FROM pop;
