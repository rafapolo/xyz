# Fonte dos dados

- Religião: [IBGE Sidra, tabela 9537](https://sidra.ibge.gov.br/tabela/9537) (2022) e tabela 137 (2010, via apisidra.ibge.gov.br)
- Cor ou raça: [IBGE Sidra, tabela 9605](https://sidra.ibge.gov.br/tabela/9605) (2010 e 2022), agregados de `br_ibge_censo_2022.populacao_grupo_idade_sexo_raca` (rodado/basedosdados.duckdb)
- `municipios.csv`: localização (lat/lon) e códigos IBGE por município
- `vertentes-religiosas.csv`: as 75 categorias oficiais da classificação "Religião" (tabela 137, IBGE SIDRA) — árvore completa em `../treeview-religioes.txt`
- `cnefe-descricao-vertente.csv`: dicionário heurístico (nosso, não oficial) que casa `descricao_estabelecimento` do CNEFE com uma vertente do arquivo acima — cresce por uso, ver coluna `fonte`
- `igrejas_geolocalizadas.parquet`: 570.428 templos religiosos do Brasil — presença decidida pelo campo oficial `tipo_especie='8'` do CNEFE (mesmo critério do número publicado pelo IBGE, 579.800, diferença de 1,6%), geolocalizados no endereço real de campo (não CEP agregado), classificados por vertente via `cnefe-descricao-vertente.csv`, e com a coluna `com_cnae` (~4,6% do total) indicando se o endereço bate com um CNPJ ativo de CNAE 9491-0/00 em `br_me_cnpj/estabelecimentos`. Gerado por `gerar_igrejas_geolocalizadas.py`, usado em `../igrejas/index.html`. **Ver `../metodologia.md` para a metodologia completa, decisões e limitações conhecidas.**

`resultante.csv` e `resultante_raca*.csv` são as tabelas já mescladas/derivadas (percentuais por município) usadas para gerar `../index.html` e `../../racas/index.html`.
