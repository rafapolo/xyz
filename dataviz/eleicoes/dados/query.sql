INSTALL spatial; LOAD spatial;
SET threads=8; SET memory_limit='18GB';
WITH scores(sigla, score) AS (
  VALUES ('PCB',0.5),('PCO',0.3),('PSTU',0.6),('UP',0.5),('PSOL',1.3),
  ('PC do B',1.7),('PT',2.5),('REDE',3.3),('PDT',3.3),('PSB',3.7),
  ('PV',4.1),('CIDADANIA',4.6),('SOLIDARIEDADE',5.4),('MDB',5.7),('PSD',5.9),
  ('AVANTE',5.6),('PODE',5.7),('MOBILIZA',5.5),('PMB',5.5),('AGIR',6.0),
  ('PSDB',6.0),('PRD',6.8),('UNIÃO',6.9),('PP',7.0),('REPUBLICANOS',7.2),
  ('DC',7.5),('PL',8.5),('PRTB',8.0),('NOVO',8.2)
),
base AS (
  SELECT r.id_municipio, any_value(r.sigla_uf) AS uf, r.sigla_partido AS sigla,
         SUM(r.votos) AS votos
  FROM read_parquet('/home/polo/rodado/br_tse_eleicoes/resultados_candidato_municipio/*.parquet') r
  WHERE r.ano=2024 AND r.cargo='prefeito' AND r.turno=1
  GROUP BY r.id_municipio, r.sigla_partido
),
j AS (
  SELECT b.id_municipio, b.uf, b.sigla, b.votos, COALESCE(s.score,5.0) AS score
  FROM base b LEFT JOIN scores s ON s.sigla=b.sigla
),
ranked AS (
  SELECT *, row_number() OVER (PARTITION BY id_municipio ORDER BY votos DESC) rn FROM j
),
agg AS (
  SELECT id_municipio, any_value(uf) uf, SUM(votos) tot,
    SUM(votos*score)/SUM(votos) lean,
    sqrt(greatest(0, SUM(votos*score*score)/SUM(votos) - pow(SUM(votos*score)/SUM(votos),2))) polar,
    COUNT(*) ncand,
    SUM(CASE WHEN score<4.0 THEN votos ELSE 0 END) v_esq,
    SUM(CASE WHEN score>=4.0 AND score<=6.0 THEN votos ELSE 0 END) v_cen,
    SUM(CASE WHEN score>6.0 THEN votos ELSE 0 END) v_dir
  FROM j GROUP BY id_municipio
),
w AS (
  SELECT id_municipio,
    MAX(CASE WHEN rn=1 THEN sigla END) w1, MAX(CASE WHEN rn=1 THEN votos END) w1v,
    MAX(CASE WHEN rn=2 THEN sigla END) w2, MAX(CASE WHEN rn=2 THEN votos END) w2v
  FROM ranked WHERE rn<=2 GROUP BY id_municipio
)
SELECT a.uf uf, m.nome nome,
  round(ST_Y(m.centroide),4) lat, round(ST_X(m.centroide),4) lon,
  a.tot tot, round(a.lean,3) lean, round(a.polar,3) polar, a.ncand,
  w.w1 w1, round(100.0*w.w1v/a.tot,1) w1pct,
  w.w2 w2, round(100.0*COALESCE(w.w2v,0)/a.tot,1) w2pct,
  round(100.0*a.v_esq/a.tot,1) pesq, round(100.0*a.v_cen/a.tot,1) pcen, round(100.0*a.v_dir/a.tot,1) pdir
FROM agg a JOIN w USING(id_municipio)
JOIN read_parquet('/home/polo/rodado/br_bd_diretorios_brasil/municipio/000000000000.parquet') m
  ON m.id_municipio=a.id_municipio
WHERE a.tot>0 ORDER BY a.uf, m.nome;
