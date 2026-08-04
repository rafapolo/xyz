-- Governador 2022, 1o turno, por municipio: inclinacao ideologica do voto.
-- Mesma logica e as mesmas notas de dados/query.sql, trocando o cargo.
--
-- Gera dados/governador_2022_raw.json com uma linha por municipio:
--   uf, nome, lean (media dos scores ponderada por votos), tot (votos validos),
--   eleito (sigla do governador efetivamente eleito naquela UF)
--
-- POR QUE ESTE RECORTE EXISTE
-- Na eleicao de prefeito cada municipio tem candidatos diferentes, entao a
-- correlacao entre religiao e voto mistura o efeito do eleitorado com o da
-- oferta de candidatos. Na de governador, todos os municipios de um estado
-- escolhem entre os MESMOS candidatos — o que permite medir o efeito do
-- eleitorado com os candidatos mantidos constantes. Ver §12 do relatorio.
--
-- Rodar no beelink, onde estao os parquets:
--   ssh beelink '~/bin/duckdb -json' < query_governador.sql > /tmp/gov.json

WITH scores(sigla, score) AS (
  VALUES ('PCB',0.5),('PCO',0.3),('PSTU',0.6),('UP',0.5),('PSOL',1.3),
  ('PC do B',1.7),('PT',2.5),('REDE',3.3),('PDT',3.3),('PSB',3.7),
  ('PV',4.1),('CIDADANIA',4.6),('SOLIDARIEDADE',5.4),('MDB',5.7),('PSD',5.9),
  ('AVANTE',5.6),('PODE',5.7),('MOBILIZA',5.5),('PMB',5.5),('AGIR',6.0),
  ('PSDB',6.0),('PRD',6.8),('UNIÃO',6.9),('PP',7.0),('REPUBLICANOS',7.2),
  ('DC',7.5),('PL',8.5),('PRTB',8.0),('NOVO',8.2)
),
gov AS (
  SELECT r.id_municipio, any_value(r.sigla_uf) AS uf,
         r.sigla_partido AS sigla, SUM(r.votos) AS votos
  FROM read_parquet('/home/polo/rodado/br_tse_eleicoes/resultados_candidato_municipio/*.parquet') r
  WHERE r.ano = 2022 AND r.cargo = 'governador' AND r.turno = 1
  GROUP BY r.id_municipio, r.sigla_partido
),
-- o diretorio traz varias versoes por municipio; sem o GROUP BY a juncao duplica
nomes AS (
  SELECT id_municipio, any_value(nome) AS nome
  FROM read_parquet('/home/polo/rodado/br_bd_diretorios_brasil/municipio/*.parquet')
  GROUP BY id_municipio
),
-- governador eleito: partido mais votado no ultimo turno que a UF teve
totais AS (
  SELECT sigla_uf AS uf, turno, sigla_partido AS sigla, SUM(votos) AS v
  FROM read_parquet('/home/polo/rodado/br_tse_eleicoes/resultados_candidato_municipio/*.parquet')
  WHERE ano = 2022 AND cargo = 'governador'
  GROUP BY 1, 2, 3
),
ultimo AS (SELECT uf, MAX(turno) AS t FROM totais GROUP BY uf),
eleitos AS (
  SELECT t.uf, t.sigla AS eleito
  FROM totais t JOIN ultimo u ON u.uf = t.uf AND u.t = t.turno
  QUALIFY ROW_NUMBER() OVER (PARTITION BY t.uf ORDER BY t.v DESC) = 1
)
SELECT g.uf, n.nome AS nome,
       ROUND(SUM(g.votos * COALESCE(s.score, 5.0)) / NULLIF(SUM(g.votos), 0), 4) AS lean,
       SUM(g.votos) AS tot,
       any_value(e.eleito) AS eleito
FROM gov g
LEFT JOIN scores s ON s.sigla = g.sigla
JOIN nomes n ON n.id_municipio = g.id_municipio
JOIN eleitos e ON e.uf = g.uf
GROUP BY g.uf, n.nome
ORDER BY 1, 2;
