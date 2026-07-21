# Fonte dos dados

- Religião: [IBGE Sidra, tabela 9537](https://sidra.ibge.gov.br/tabela/9537) (2022) e tabela 137 (2010, via apisidra.ibge.gov.br)
- Cor ou raça: [IBGE Sidra, tabela 9605](https://sidra.ibge.gov.br/tabela/9605) (2010 e 2022), agregados de `br_ibge_censo_2022.populacao_grupo_idade_sexo_raca` (rodado/basedosdados.duckdb)
- `municipios.csv`: localização (lat/lon) e códigos IBGE por município

`resultante.csv` e `resultante_raca*.csv` são as tabelas já mescladas/derivadas (percentuais por município) usadas para gerar `../index.html` e `../../racas/index.html`.
