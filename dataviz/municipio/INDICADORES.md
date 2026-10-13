# Painel municipal do Rodado — os 594 indicadores

Inventário gerado em 2026-10-13 a partir de `dataviz/municipio/data/nova_friburgo.json` (Nova Friburgo, RJ) e do extrator `extract_municipio.py`. Painel: https://xn--2dk.xyz/dataviz/municipio/ · Dados: espelho da Base dos Dados em [rodado.xyz](https://rodado.xyz).

**Critério de contagem** (o mesmo do rodapé do painel): cada número não nulo ou cada série/ranking não vazio dentro de `secoes`, sem metadados (fonte, ano, referência) e sem blocos que vieram com erro ou sem dado. Outros municípios têm contagem diferente: fontes como ISP (só RJ), PRODES ou CFEM só aparecem onde há dado.

**Datasets de origem**: tabelas `<dataset>.<tabela>` lidas pela função do extrator que produz o indicador.

| Tema | Indicadores |
|---|---:|
| Geografia | 7 |
| Demografia | 17 |
| Economia e finanças | 46 |
| Empresas | 9 |
| Educação | 70 |
| Saúde | 77 |
| Segurança | 90 |
| Infraestrutura e energia | 51 |
| Meio ambiente | 28 |
| Conectividade | 6 |
| Política | 45 |
| Transparência e gestão | 31 |
| Social e cultura | 21 |
| Comércio exterior | 6 |
| Trabalho | 17 |
| Agropecuária | 17 |
| Benefícios sociais | 55 |
| Vizinhança | 1 |
| **Total** | **594** |

## Geografia (7)

| # | Indicador | O que mede | Tipo | Datasets de origem |
|---:|---|---|---|---|
| 1 | `sede_municipal.lat` | Latitude da sede municipal | valor | `br_geobr_mapas.municipio`<br>`br_geobr_mapas.sede_municipal`<br>`br_geobr_mapas.arranjo_populacional`<br>`br_geobr_mapas.regiao_metropolitana_2017`<br>`br_geobr_mapas.bioma`<br>`br_geobr_mapas.unidade_conservacao`<br>+1 |
| 2 | `sede_municipal.lon` | Longitude da sede municipal | valor | `br_geobr_mapas.municipio`<br>`br_geobr_mapas.sede_municipal`<br>`br_geobr_mapas.arranjo_populacional`<br>`br_geobr_mapas.regiao_metropolitana_2017`<br>`br_geobr_mapas.bioma`<br>`br_geobr_mapas.unidade_conservacao`<br>+1 |
| 3 | `semiarido` | Se o município está na delimitação oficial do Semiárido | valor | `br_geobr_mapas.municipio`<br>`br_geobr_mapas.sede_municipal`<br>`br_geobr_mapas.arranjo_populacional`<br>`br_geobr_mapas.regiao_metropolitana_2017`<br>`br_geobr_mapas.bioma`<br>`br_geobr_mapas.unidade_conservacao`<br>+1 |
| 4 | `biomas` | Biomas que cobrem o território municipal | série/ranking | `br_geobr_mapas.municipio`<br>`br_geobr_mapas.sede_municipal`<br>`br_geobr_mapas.arranjo_populacional`<br>`br_geobr_mapas.regiao_metropolitana_2017`<br>`br_geobr_mapas.bioma`<br>`br_geobr_mapas.unidade_conservacao`<br>+1 |
| 5 | `unidades_conservacao.total` | Número de unidades de conservação que tocam o município | valor | `br_geobr_mapas.municipio`<br>`br_geobr_mapas.sede_municipal`<br>`br_geobr_mapas.arranjo_populacional`<br>`br_geobr_mapas.regiao_metropolitana_2017`<br>`br_geobr_mapas.bioma`<br>`br_geobr_mapas.unidade_conservacao`<br>+1 |
| 6 | `unidades_conservacao.por_categoria` | Unidades de conservação por categoria (parque, APA, reserva…) | série/ranking | `br_geobr_mapas.municipio`<br>`br_geobr_mapas.sede_municipal`<br>`br_geobr_mapas.arranjo_populacional`<br>`br_geobr_mapas.regiao_metropolitana_2017`<br>`br_geobr_mapas.bioma`<br>`br_geobr_mapas.unidade_conservacao`<br>+1 |
| 7 | `unidades_conservacao.lista` | Nome, categoria e esfera de cada unidade de conservação | série/ranking | `br_geobr_mapas.municipio`<br>`br_geobr_mapas.sede_municipal`<br>`br_geobr_mapas.arranjo_populacional`<br>`br_geobr_mapas.regiao_metropolitana_2017`<br>`br_geobr_mapas.bioma`<br>`br_geobr_mapas.unidade_conservacao`<br>+1 |

## Demografia (17)

| # | Indicador | O que mede | Tipo | Datasets de origem |
|---:|---|---|---|---|
| 8 | `populacao_serie` | População estimada pelo IBGE ano a ano | série/ranking | `br_ibge_populacao.municipio`<br>`br_ibge_censo_2022.municipio`<br>`br_ibge_censo_2022.populacao_grupo_idade_sexo_raca` |
| 9 | `censo_2022.populacao` | População recenseada no Censo 2022 | valor | `br_ibge_populacao.municipio`<br>`br_ibge_censo_2022.municipio`<br>`br_ibge_censo_2022.populacao_grupo_idade_sexo_raca` |
| 10 | `censo_2022.domicilios` | Domicílios particulares ocupados no Censo 2022 | valor | `br_ibge_populacao.municipio`<br>`br_ibge_censo_2022.municipio`<br>`br_ibge_censo_2022.populacao_grupo_idade_sexo_raca` |
| 11 | `censo_2022.area_km2` | Área territorial em km² | valor | `br_ibge_populacao.municipio`<br>`br_ibge_censo_2022.municipio`<br>`br_ibge_censo_2022.populacao_grupo_idade_sexo_raca` |
| 12 | `censo_2022.taxa_alfabetizacao` | Proporção de pessoas de 15+ anos alfabetizadas (Censo 2022) | valor | `br_ibge_populacao.municipio`<br>`br_ibge_censo_2022.municipio`<br>`br_ibge_censo_2022.populacao_grupo_idade_sexo_raca` |
| 13 | `censo_2022.idade_mediana` | Idade mediana da população (Censo 2022) | valor | `br_ibge_populacao.municipio`<br>`br_ibge_censo_2022.municipio`<br>`br_ibge_censo_2022.populacao_grupo_idade_sexo_raca` |
| 14 | `censo_2022.razao_sexo` | Homens para cada 100 mulheres (Censo 2022) | valor | `br_ibge_populacao.municipio`<br>`br_ibge_censo_2022.municipio`<br>`br_ibge_censo_2022.populacao_grupo_idade_sexo_raca` |
| 15 | `censo_2022.indice_envelhecimento` | Idosos de 65+ para cada 100 jovens de 0–14 anos | valor | `br_ibge_populacao.municipio`<br>`br_ibge_censo_2022.municipio`<br>`br_ibge_censo_2022.populacao_grupo_idade_sexo_raca` |
| 16 | `piramide_etaria_2022.grupos` | Faixas etárias de 5 anos da pirâmide de 2022 | série/ranking | `br_ibge_populacao.municipio`<br>`br_ibge_censo_2022.municipio`<br>`br_ibge_censo_2022.populacao_grupo_idade_sexo_raca` |
| 17 | `piramide_etaria_2022.homens` | Homens por faixa etária (Censo 2022) | série/ranking | `br_ibge_populacao.municipio`<br>`br_ibge_censo_2022.municipio`<br>`br_ibge_censo_2022.populacao_grupo_idade_sexo_raca` |
| 18 | `piramide_etaria_2022.mulheres` | Mulheres por faixa etária (Censo 2022) | série/ranking | `br_ibge_populacao.municipio`<br>`br_ibge_censo_2022.municipio`<br>`br_ibge_censo_2022.populacao_grupo_idade_sexo_raca` |
| 19 | `censo_extra.cor_raca.2010` | População por cor ou raça no Censo 2010 | série/ranking | `br_ibge_censo_2022.populacao_grupo_idade_sexo_raca`<br>`br_ibge_censo_2022.alfabetizacao_grupo_idade_sexo_raca`<br>`br_ibge_censo2022_religiao.populacao_religiao` |
| 20 | `censo_extra.cor_raca.2022` | População por cor ou raça no Censo 2022 | série/ranking | `br_ibge_censo_2022.populacao_grupo_idade_sexo_raca`<br>`br_ibge_censo_2022.alfabetizacao_grupo_idade_sexo_raca`<br>`br_ibge_censo2022_religiao.populacao_religiao` |
| 21 | `censo_extra.alfabetizacao_por_raca` | Taxa de alfabetização por cor ou raça (2022) | série/ranking | `br_ibge_censo_2022.populacao_grupo_idade_sexo_raca`<br>`br_ibge_censo_2022.alfabetizacao_grupo_idade_sexo_raca`<br>`br_ibge_censo2022_religiao.populacao_religiao` |
| 22 | `censo_extra.religiao.total_10_anos_ou_mais` | Pessoas de 10+ anos na base do quesito religião | valor | `br_ibge_censo_2022.populacao_grupo_idade_sexo_raca`<br>`br_ibge_censo_2022.alfabetizacao_grupo_idade_sexo_raca`<br>`br_ibge_censo2022_religiao.populacao_religiao` |
| 23 | `censo_extra.religiao.grupos` | Pessoas por grupo religioso (Censo 2022) | série/ranking | `br_ibge_censo_2022.populacao_grupo_idade_sexo_raca`<br>`br_ibge_censo_2022.alfabetizacao_grupo_idade_sexo_raca`<br>`br_ibge_censo2022_religiao.populacao_religiao` |
| 24 | `nomes.top` | Os 15 nomes mais registrados entre nascidos até 2010 | série/ranking | `br_ibge_nomes_brasil.quantidade_municipio_nome_2010` |

## Economia e finanças (46)

| # | Indicador | O que mede | Tipo | Datasets de origem |
|---:|---|---|---|---|
| 25 | `pib.serie` | PIB municipal e valor adicionado por setor, ano a ano | série/ranking | `br_ibge_pib.municipio`<br>`br_ibge_populacao.municipio`<br>`br_bd_diretorios_brasil.municipio`<br>`br_ibge_populacao.brasil`<br>`br_ibge_populacao.uf` |
| 26 | `pib.pib_per_capita.valor` | PIB per capita do município | valor | `br_ibge_pib.municipio`<br>`br_ibge_populacao.municipio`<br>`br_bd_diretorios_brasil.municipio`<br>`br_ibge_populacao.brasil`<br>`br_ibge_populacao.uf` |
| 27 | `pib.pib_per_capita.uf` | PIB per capita médio da UF, para comparação | valor | `br_ibge_pib.municipio`<br>`br_ibge_populacao.municipio`<br>`br_bd_diretorios_brasil.municipio`<br>`br_ibge_populacao.brasil`<br>`br_ibge_populacao.uf` |
| 28 | `pib.pib_per_capita.brasil` | PIB per capita do Brasil, para comparação | valor | `br_ibge_pib.municipio`<br>`br_ibge_populacao.municipio`<br>`br_bd_diretorios_brasil.municipio`<br>`br_ibge_populacao.brasil`<br>`br_ibge_populacao.uf` |
| 29 | `pib.ranking_uf.posicao` | Posição do PIB do município entre os da UF | valor | `br_ibge_pib.municipio`<br>`br_ibge_populacao.municipio`<br>`br_bd_diretorios_brasil.municipio`<br>`br_ibge_populacao.brasil`<br>`br_ibge_populacao.uf` |
| 30 | `pib.ranking_uf.total` | Número de municípios da UF no ranking do PIB | valor | `br_ibge_pib.municipio`<br>`br_ibge_populacao.municipio`<br>`br_bd_diretorios_brasil.municipio`<br>`br_ibge_populacao.brasil`<br>`br_ibge_populacao.uf` |
| 31 | `financas_publicas.receitas.total` | Receita orçamentária total da prefeitura no ano | valor | `br_me_siconfi.municipio_receitas_orcamentarias`<br>`br_me_siconfi.municipio_despesas_funcao` |
| 32 | `financas_publicas.receitas.receitas_correntes` | Receitas correntes da prefeitura (impostos, transferências, serviços) | valor | `br_me_siconfi.municipio_receitas_orcamentarias`<br>`br_me_siconfi.municipio_despesas_funcao` |
| 33 | `financas_publicas.receitas.receitas_capital` | Receitas de capital (operações de crédito, alienações, convênios) | valor | `br_me_siconfi.municipio_receitas_orcamentarias`<br>`br_me_siconfi.municipio_despesas_funcao` |
| 34 | `financas_publicas.receitas.impostos` | Arrecadação própria de impostos, taxas e contribuições | valor | `br_me_siconfi.municipio_receitas_orcamentarias`<br>`br_me_siconfi.municipio_despesas_funcao` |
| 35 | `financas_publicas.receitas.fpm` | Repasses do Fundo de Participação dos Municípios | valor | `br_me_siconfi.municipio_receitas_orcamentarias`<br>`br_me_siconfi.municipio_despesas_funcao` |
| 36 | `financas_publicas.receitas.icms` | Cota-parte do ICMS recebida do estado | valor | `br_me_siconfi.municipio_receitas_orcamentarias`<br>`br_me_siconfi.municipio_despesas_funcao` |
| 37 | `financas_publicas.receitas.iptu` | Arrecadação de IPTU | valor | `br_me_siconfi.municipio_receitas_orcamentarias`<br>`br_me_siconfi.municipio_despesas_funcao` |
| 38 | `financas_publicas.receitas.iss` | Arrecadação de ISS | valor | `br_me_siconfi.municipio_receitas_orcamentarias`<br>`br_me_siconfi.municipio_despesas_funcao` |
| 39 | `financas_publicas.receitas.fundeb` | Receitas do Fundeb | valor | `br_me_siconfi.municipio_receitas_orcamentarias`<br>`br_me_siconfi.municipio_despesas_funcao` |
| 40 | `financas_publicas.receitas.sus` | Transferências do SUS para a saúde municipal | valor | `br_me_siconfi.municipio_receitas_orcamentarias`<br>`br_me_siconfi.municipio_despesas_funcao` |
| 41 | `financas_publicas.despesas_funcao` | Despesa empenhada por função de governo (saúde, educação…) | série/ranking | `br_me_siconfi.municipio_receitas_orcamentarias`<br>`br_me_siconfi.municipio_despesas_funcao` |
| 42 | `financas_publicas.despesas_total_empenhado` | Total da despesa empenhada no ano | valor | `br_me_siconfi.municipio_receitas_orcamentarias`<br>`br_me_siconfi.municipio_despesas_funcao` |
| 43 | `bancario.mes` | Mês de referência do balancete bancário | valor | `br_bcb_estban.municipio`<br>`br_bcb_estban.dicionario` |
| 44 | `bancario.agencias` | Agências bancárias no município | valor | `br_bcb_estban.municipio`<br>`br_bcb_estban.dicionario` |
| 45 | `bancario.depositos_totais` | Saldo de depósitos nas agências do município | valor | `br_bcb_estban.municipio`<br>`br_bcb_estban.dicionario` |
| 46 | `bancario.operacoes_credito` | Saldo de operações de crédito das agências locais | valor | `br_bcb_estban.municipio`<br>`br_bcb_estban.dicionario` |
| 47 | `bancario.verbetes.depositos` | Depósitos por tipo (à vista, poupança, a prazo) | série/ranking | `br_bcb_estban.municipio`<br>`br_bcb_estban.dicionario` |
| 48 | `bancario.verbetes.credito` | Crédito por modalidade nas agências locais | valor | `br_bcb_estban.municipio`<br>`br_bcb_estban.dicionario` |
| 49 | `inpc_brasil.mes` | Mês de referência do INPC nacional | valor | `br_ibge_inpc.mes_brasil` |
| 50 | `inpc_brasil.variacao_mensal` | Variação do INPC no mês (Brasil) | valor | `br_ibge_inpc.mes_brasil` |
| 51 | `inpc_brasil.variacao_anual` | Variação do INPC acumulada no ano (Brasil) | valor | `br_ibge_inpc.mes_brasil` |
| 52 | `inpc_brasil.variacao_doze_meses` | Variação do INPC em 12 meses (Brasil) | valor | `br_ibge_inpc.mes_brasil` |
| 53 | `combustiveis.janela_dias` | Janela em dias das coletas de preço de combustível | valor | `br_anp_combustiveis.precos` |
| 54 | `combustiveis.produtos` | Preço médio de revenda por combustível no município | série/ranking | `br_anp_combustiveis.precos` |
| 55 | `pix.valor_pago` | Valor pago por Pix por pessoas e empresas do município no mês | valor | `br_bcb_pix_municipio.transacoes`<br>`br_ibge_populacao.municipio` |
| 56 | `pix.valor_recebido` | Valor recebido por Pix no município no mês | valor | `br_bcb_pix_municipio.transacoes`<br>`br_ibge_populacao.municipio` |
| 57 | `pix.transacoes_pagas` | Quantidade de transações Pix pagas no mês | valor | `br_bcb_pix_municipio.transacoes`<br>`br_ibge_populacao.municipio` |
| 58 | `pix.transacoes_recebidas` | Quantidade de transações Pix recebidas no mês | valor | `br_bcb_pix_municipio.transacoes`<br>`br_ibge_populacao.municipio` |
| 59 | `pix.pagadores_pf` | Pessoas físicas que pagaram com Pix no mês | valor | `br_bcb_pix_municipio.transacoes`<br>`br_ibge_populacao.municipio` |
| 60 | `pix.pagadores_pj` | Empresas que pagaram com Pix no mês | valor | `br_bcb_pix_municipio.transacoes`<br>`br_ibge_populacao.municipio` |
| 61 | `pix.pagadores_pf_por_hab` | Pagadores pessoa física de Pix por habitante | valor | `br_bcb_pix_municipio.transacoes`<br>`br_ibge_populacao.municipio` |
| 62 | `pix.serie` | Valores pagos e recebidos por Pix nos últimos 36 meses | série/ranking | `br_bcb_pix_municipio.transacoes`<br>`br_ibge_populacao.municipio` |
| 63 | `bndes.serie_indiretas` | Operações e desembolsos BNDES via bancos repassadores, por ano | série/ranking | `br_bndes_operacoes_contratadas.operacoes_indiretas_automaticas`<br>`br_bndes_operacoes_contratadas.operacoes_nao_automaticas`<br>`br_bndes_operacoes_contratadas.operacoes_administracao_publica` |
| 64 | `bndes.porte_5a` | Desembolsos BNDES por porte do cliente (5 anos) | série/ranking | `br_bndes_operacoes_contratadas.operacoes_indiretas_automaticas`<br>`br_bndes_operacoes_contratadas.operacoes_nao_automaticas`<br>`br_bndes_operacoes_contratadas.operacoes_administracao_publica` |
| 65 | `bndes.setor_5a` | Desembolsos BNDES por setor (5 anos) | série/ranking | `br_bndes_operacoes_contratadas.operacoes_indiretas_automaticas`<br>`br_bndes_operacoes_contratadas.operacoes_nao_automaticas`<br>`br_bndes_operacoes_contratadas.operacoes_administracao_publica` |
| 66 | `bndes.nao_automaticas` | Operações diretas do BNDES com clientes do município | série/ranking | `br_bndes_operacoes_contratadas.operacoes_indiretas_automaticas`<br>`br_bndes_operacoes_contratadas.operacoes_nao_automaticas`<br>`br_bndes_operacoes_contratadas.operacoes_administracao_publica` |
| 67 | `bndes.administracao_publica` | Financiamentos do BNDES à prefeitura | série/ranking | `br_bndes_operacoes_contratadas.operacoes_indiretas_automaticas`<br>`br_bndes_operacoes_contratadas.operacoes_nao_automaticas`<br>`br_bndes_operacoes_contratadas.operacoes_administracao_publica` |
| 68 | `mineracao_cfem.valor_ano` | CFEM (royalties da mineração) recolhida no último ano completo | valor | `br_anm.cfem_cfem_arrecadacao` |
| 69 | `mineracao_cfem.serie` | CFEM recolhida e número de pagadores por ano | série/ranking | `br_anm.cfem_cfem_arrecadacao` |
| 70 | `mineracao_cfem.substancias` | CFEM por substância mineral no ano | série/ranking | `br_anm.cfem_cfem_arrecadacao` |

## Empresas (9)

| # | Indicador | O que mede | Tipo | Datasets de origem |
|---:|---|---|---|---|
| 71 | `ativas` | Empresas (estabelecimentos) ativas com sede no município | valor | `br_me_cnpj.estabelecimentos`<br>`br_bd_diretorios_brasil.cnae_2` |
| 72 | `baixadas` | Estabelecimentos baixados no cadastro CNPJ | valor | `br_me_cnpj.estabelecimentos`<br>`br_bd_diretorios_brasil.cnae_2` |
| 73 | `matrizes` | Estabelecimentos ativos que são matriz | valor | `br_me_cnpj.estabelecimentos`<br>`br_bd_diretorios_brasil.cnae_2` |
| 74 | `filiais` | Estabelecimentos ativos que são filial | valor | `br_me_cnpj.estabelecimentos`<br>`br_bd_diretorios_brasil.cnae_2` |
| 75 | `registradas` | Total de estabelecimentos já registrados no município | valor | `br_me_cnpj.estabelecimentos`<br>`br_bd_diretorios_brasil.cnae_2` |
| 76 | `idade_media_anos` | Idade média das empresas ativas, em anos | valor | `br_me_cnpj.estabelecimentos`<br>`br_bd_diretorios_brasil.cnae_2` |
| 77 | `por_secao_cnae` | Empresas ativas por seção da CNAE | série/ranking | `br_me_cnpj.estabelecimentos`<br>`br_bd_diretorios_brasil.cnae_2` |
| 78 | `top_atividades` | Atividades econômicas (CNAE) com mais empresas ativas | série/ranking | `br_me_cnpj.estabelecimentos`<br>`br_bd_diretorios_brasil.cnae_2` |
| 79 | `demografia_empresarial` | Aberturas e fechamentos de empresas por ano | série/ranking | `br_me_cnpj.estabelecimentos`<br>`br_bd_diretorios_brasil.cnae_2` |

## Educação (70)

| # | Indicador | O que mede | Tipo | Datasets de origem |
|---:|---|---|---|---|
| 80 | `ideb.iniciais` | IDEB dos anos iniciais do fundamental, série histórica | série/ranking | `br_inep_ideb.municipio` |
| 81 | `ideb.finais` | IDEB dos anos finais do fundamental, série histórica | série/ranking | `br_inep_ideb.municipio` |
| 82 | `ideb.referencia_uf.iniciais` | IDEB anos iniciais da UF, para comparação | valor | `br_inep_ideb.municipio` |
| 83 | `ideb.referencia_uf.finais` | IDEB anos finais da UF, para comparação | valor | `br_inep_ideb.municipio` |
| 84 | `ideb.referencia_brasil.finais` | IDEB anos finais do Brasil, para comparação | valor | `br_inep_ideb.municipio` |
| 85 | `ideb.referencia_brasil.iniciais` | IDEB anos iniciais do Brasil, para comparação | valor | `br_inep_ideb.municipio` |
| 86 | `saeb.provas` | Proficiência média no Saeb por série e disciplina | série/ranking | `br_inep_saeb.municipio` |
| 87 | `enem.inscritos` | Inscritos no ENEM residentes no município | valor | `br_inep_enem.microdados` |
| 88 | `enem.presentes` | Participantes presentes nas provas do ENEM | valor | `br_inep_enem.microdados` |
| 89 | `enem.redacao` | Nota média de redação no ENEM | valor | `br_inep_enem.microdados` |
| 90 | `enem.linguagens` | Nota média em Linguagens no ENEM | valor | `br_inep_enem.microdados` |
| 91 | `enem.matematica` | Nota média em Matemática no ENEM | valor | `br_inep_enem.microdados` |
| 92 | `enem.humanas` | Nota média em Ciências Humanas no ENEM | valor | `br_inep_enem.microdados` |
| 93 | `enem.natureza` | Nota média em Ciências da Natureza no ENEM | valor | `br_inep_enem.microdados` |
| 94 | `enem.media_geral` | Média geral das cinco notas do ENEM | valor | `br_inep_enem.microdados` |
| 95 | `censo_escolar.escolas` | Escolas de educação básica em atividade | valor | `br_inep_censo_escolar.escola` |
| 96 | `censo_escolar.matriculas` | Matrículas na educação básica | valor | `br_inep_censo_escolar.escola` |
| 97 | `censo_escolar.docentes` | Docentes da educação básica | valor | `br_inep_censo_escolar.escola` |
| 98 | `censo_escolar.turmas` | Turmas da educação básica | valor | `br_inep_censo_escolar.escola` |
| 99 | `censo_escolar.escolas_rurais` | Escolas em área rural | valor | `br_inep_censo_escolar.escola` |
| 100 | `censo_escolar.com_internet` | Escolas com acesso à internet | valor | `br_inep_censo_escolar.escola` |
| 101 | `censo_escolar.com_biblioteca` | Escolas com biblioteca | valor | `br_inep_censo_escolar.escola` |
| 102 | `censo_escolar.com_quadra` | Escolas com quadra de esportes | valor | `br_inep_censo_escolar.escola` |
| 103 | `censo_escolar.com_laboratorio` | Escolas com laboratório (informática ou ciências) | valor | `br_inep_censo_escolar.escola` |
| 104 | `censo_escolar.com_esgoto_rede` | Escolas ligadas à rede pública de esgoto | valor | `br_inep_censo_escolar.escola` |
| 105 | `censo_escolar.com_rampa_acessibilidade` | Escolas com rampa de acessibilidade | valor | `br_inep_censo_escolar.escola` |
| 106 | `censo_escolar.matriculas_infantil` | Matrículas na educação infantil | valor | `br_inep_censo_escolar.escola` |
| 107 | `censo_escolar.matriculas_fundamental` | Matrículas no ensino fundamental | valor | `br_inep_censo_escolar.escola` |
| 108 | `censo_escolar.matriculas_medio` | Matrículas no ensino médio | valor | `br_inep_censo_escolar.escola` |
| 109 | `censo_escolar.matriculas_eja` | Matrículas na educação de jovens e adultos | valor | `br_inep_censo_escolar.escola` |
| 110 | `censo_escolar.matriculas_especial` | Matrículas na educação especial | valor | `br_inep_censo_escolar.escola` |
| 111 | `censo_escolar.matriculas_transporte` | Alunos que usam transporte escolar público | valor | `br_inep_censo_escolar.escola` |
| 112 | `censo_escolar.por_rede` | Escolas e matrículas por rede (municipal, estadual, privada…) | série/ranking | `br_inep_censo_escolar.escola` |
| 113 | `censo_escolar.serie` | Escolas e matrículas ao longo dos anos | série/ranking | `br_inep_censo_escolar.escola` |
| 114 | `sisu.serie` | Vagas e inscrições do SISU em instituições do município, por ano | série/ranking | `br_mec_sisu.microdados` |
| 115 | `sisu.top_cursos` | Cursos com mais vagas no SISU no município | série/ranking | `br_mec_sisu.microdados` |
| 116 | `alfabetizacao.taxa` | Alunos do 2º ano alfabetizados na rede pública (Criança Alfabetizada) | valor | `br_inep_avaliacao_alfabetizacao.municipio`<br>`br_inep_avaliacao_alfabetizacao.meta_alfabetizacao_municipio` |
| 117 | `alfabetizacao.media_municipios_uf` | Média da taxa de alfabetização dos municípios da UF | valor | `br_inep_avaliacao_alfabetizacao.municipio`<br>`br_inep_avaliacao_alfabetizacao.meta_alfabetizacao_municipio` |
| 118 | `alfabetizacao.serie` | Taxa de alfabetização no 2º ano, ano a ano | série/ranking | `br_inep_avaliacao_alfabetizacao.municipio`<br>`br_inep_avaliacao_alfabetizacao.meta_alfabetizacao_municipio` |
| 119 | `alfabetizacao.metas` | Metas pactuadas de alfabetização até 2030 | série/ranking | `br_inep_avaliacao_alfabetizacao.municipio`<br>`br_inep_avaliacao_alfabetizacao.meta_alfabetizacao_municipio` |
| 120 | `inse.inse` | Nível socioeconômico médio dos alunos (escala 1–8) | valor | `br_inep_indicador_nivel_socioeconomico.municipio` |
| 121 | `inse.alunos` | Alunos considerados no cálculo do INSE | valor | `br_inep_indicador_nivel_socioeconomico.municipio` |
| 122 | `inse.media_municipios_uf` | INSE médio dos municípios da UF | valor | `br_inep_indicador_nivel_socioeconomico.municipio` |
| 123 | `inse.media_municipios_br` | INSE médio dos municípios do Brasil | valor | `br_inep_indicador_nivel_socioeconomico.municipio` |
| 124 | `inse.niveis_pct` | Distribuição dos alunos pelos 8 níveis do INSE | série/ranking | `br_inep_indicador_nivel_socioeconomico.municipio` |
| 125 | `superior.cursos` | Cursos de graduação ofertados (presenciais e polos EaD) | valor | `br_inep_censo_educacao_superior.curso` |
| 126 | `superior.ies` | Instituições de ensino superior com oferta no município | valor | `br_inep_censo_educacao_superior.curso` |
| 127 | `superior.vagas` | Vagas oferecidas na graduação | valor | `br_inep_censo_educacao_superior.curso` |
| 128 | `superior.ingressantes` | Ingressantes na graduação no ano | valor | `br_inep_censo_educacao_superior.curso` |
| 129 | `superior.matriculas` | Matrículas na graduação | valor | `br_inep_censo_educacao_superior.curso` |
| 130 | `superior.concluintes` | Concluintes da graduação no ano | valor | `br_inep_censo_educacao_superior.curso` |
| 131 | `superior.cursos_presenciais` | Cursos de graduação presenciais | valor | `br_inep_censo_educacao_superior.curso` |
| 132 | `superior.matriculas_presenciais` | Matrículas em cursos presenciais | valor | `br_inep_censo_educacao_superior.curso` |
| 133 | `superior.matriculas_ead` | Matrículas em cursos a distância (polos) | valor | `br_inep_censo_educacao_superior.curso` |
| 134 | `superior.por_rede` | Matrículas na graduação por rede pública e privada | série/ranking | `br_inep_censo_educacao_superior.curso` |
| 135 | `superior.por_area` | Matrículas na graduação por área do conhecimento | série/ranking | `br_inep_censo_educacao_superior.curso` |
| 136 | `superior.serie_matriculas` | Matrículas na graduação ao longo dos anos | série/ranking | `br_inep_censo_educacao_superior.curso` |
| 137 | `conectada.escolas` | Escolas públicas no levantamento Educação Conectada | valor | `br_simet_educacao_conectada.escola` |
| 138 | `conectada.com_internet` | Escolas públicas com internet | valor | `br_simet_educacao_conectada.escola` |
| 139 | `conectada.internet_aprendizagem` | Escolas que usam a internet para aprendizagem | valor | `br_simet_educacao_conectada.escola` |
| 140 | `conectada.laboratorio` | Escolas públicas com laboratório de informática | valor | `br_simet_educacao_conectada.escola` |
| 141 | `conectada.medidas` | Escolas com medidor de velocidade instalado | valor | `br_simet_educacao_conectada.escola` |
| 142 | `conectada.download_mediano` | Velocidade de download mediana medida nas escolas (Mbps) | valor | `br_simet_educacao_conectada.escola` |
| 143 | `conectada.adequadas` | Escolas com velocidade igual ou acima da necessária | valor | `br_simet_educacao_conectada.escola` |
| 144 | `conectada.por_faixa` | Escolas por faixa de velocidade de internet | série/ranking | `br_simet_educacao_conectada.escola` |
| 145 | `especial.por_tipo` | Matrículas da educação especial por tipo de deficiência | série/ranking | `br_inep_educacao_especial.tipo_deficiencia` |
| 146 | `especial.por_classe` | Matrículas da educação especial em classe comum ou exclusiva | série/ranking | `br_inep_educacao_especial.tipo_deficiencia` |
| 147 | `cnpq.serie` | Bolsas e auxílios do CNPq com destino no município, por ano | série/ranking | `br_cnpq_bolsas.microdados` |
| 148 | `cnpq.por_modalidade` | Bolsas do CNPq por modalidade no último ano | série/ranking | `br_cnpq_bolsas.microdados` |
| 149 | `cnpq.por_instituicao` | Bolsas do CNPq por instituição de destino | série/ranking | `br_cnpq_bolsas.microdados` |

## Saúde (77)

| # | Indicador | O que mede | Tipo | Datasets de origem |
|---:|---|---|---|---|
| 150 | `cnes.estabelecimentos` | Estabelecimentos de saúde cadastrados, por tipo | valor | `br_ms_cnes.estabelecimento`<br>`br_ms_cnes.leito`<br>`br_ms_cnes.profissional`<br>`br_ms_cnes.equipe` |
| 151 | `cnes.leitos.total` | Leitos hospitalares existentes | valor | `br_ms_cnes.estabelecimento`<br>`br_ms_cnes.leito`<br>`br_ms_cnes.profissional`<br>`br_ms_cnes.equipe` |
| 152 | `cnes.leitos.sus` | Leitos hospitalares disponíveis ao SUS | valor | `br_ms_cnes.estabelecimento`<br>`br_ms_cnes.leito`<br>`br_ms_cnes.profissional`<br>`br_ms_cnes.equipe` |
| 153 | `cnes.profissionais.vinculos` | Vínculos de profissionais de saúde cadastrados | valor | `br_ms_cnes.estabelecimento`<br>`br_ms_cnes.leito`<br>`br_ms_cnes.profissional`<br>`br_ms_cnes.equipe` |
| 154 | `cnes.equipes.total` | Equipes de saúde cadastradas (ESF, saúde bucal…) | valor | `br_ms_cnes.estabelecimento`<br>`br_ms_cnes.leito`<br>`br_ms_cnes.profissional`<br>`br_ms_cnes.equipe` |
| 155 | `nascidos_vivos.nascidos_vivos` | Nascidos vivos de mães residentes no ano | valor | `br_ms_sinasc.microdados` |
| 156 | `nascidos_vivos.pct_cesareo` | Proporção de partos cesáreos | valor | `br_ms_sinasc.microdados` |
| 157 | `nascidos_vivos.pct_baixo_peso` | Proporção de nascidos com menos de 2,5 kg | valor | `br_ms_sinasc.microdados` |
| 158 | `nascidos_vivos.pre_natal_distribuicao.2` | Nascidos vivos com 1 a 3 consultas de pré-natal | valor | `br_ms_sinasc.microdados` |
| 159 | `nascidos_vivos.pre_natal_distribuicao.1` | Nascidos vivos com nenhuma consulta de pré-natal | valor | `br_ms_sinasc.microdados` |
| 160 | `nascidos_vivos.pre_natal_distribuicao.9` | Nascidos vivos com consultas ignoradas de pré-natal | valor | `br_ms_sinasc.microdados` |
| 161 | `nascidos_vivos.pre_natal_distribuicao.3` | Nascidos vivos com 4 a 6 consultas de pré-natal | valor | `br_ms_sinasc.microdados` |
| 162 | `nascidos_vivos.pre_natal_distribuicao.4` | Nascidos vivos com 7 ou mais consultas de pré-natal | valor | `br_ms_sinasc.microdados` |
| 163 | `dengue.notificados` | Casos de dengue notificados no ano | valor | `br_ms_sinan.microdados_dengue` |
| 164 | `dengue.confirmados` | Casos de dengue confirmados | valor | `br_ms_sinan.microdados_dengue` |
| 165 | `dengue.graves` | Casos de dengue grave ou com sinais de alarme | valor | `br_ms_sinan.microdados_dengue` |
| 166 | `dengue.obitos` | Óbitos por dengue | valor | `br_ms_sinan.microdados_dengue` |
| 167 | `dengue.notificados_ano_anterior` | Casos de dengue notificados no ano anterior | valor | `br_ms_sinan.microdados_dengue` |
| 168 | `dengue.classificacao_bruta.10/9` | Casos classificados como dengue com evolução ignorada | valor | `br_ms_sinan.microdados_dengue` |
| 169 | `dengue.classificacao_bruta.10/1` | Casos classificados como dengue que evoluíram para cura | valor | `br_ms_sinan.microdados_dengue` |
| 170 | `dengue.classificacao_bruta.10/None` | Casos classificados como dengue sem evolução informada | valor | `br_ms_sinan.microdados_dengue` |
| 171 | `dengue.classificacao_bruta.12/1` | Casos classificados como dengue grave que evoluíram para cura | valor | `br_ms_sinan.microdados_dengue` |
| 172 | `dengue.classificacao_bruta.8 /None` | Casos classificados como inconclusivos sem evolução informada | valor | `br_ms_sinan.microdados_dengue` |
| 173 | `dengue.classificacao_bruta.11/1` | Casos classificados como dengue com sinais de alarme que evoluíram para cura | valor | `br_ms_sinan.microdados_dengue` |
| 174 | `sisvan.criancas_acompanhadas` | Crianças com estado nutricional acompanhado no SISVAN | valor | `br_ms_sisvan.microdados` |
| 175 | `mortalidade.obitos` | Óbitos de residentes no ano | valor | `br_ms_sim.microdados`<br>`br_datasus_cid10.capitulos`<br>`br_datasus_cid10.subcategorias`<br>`br_ibge_populacao.municipio`<br>`br_ms_sinasc.microdados` |
| 176 | `mortalidade.obitos_infantis` | Óbitos de menores de 1 ano | valor | `br_ms_sim.microdados`<br>`br_datasus_cid10.capitulos`<br>`br_datasus_cid10.subcategorias`<br>`br_ibge_populacao.municipio`<br>`br_ms_sinasc.microdados` |
| 177 | `mortalidade.obitos_neonatais` | Óbitos de bebês com até 27 dias | valor | `br_ms_sim.microdados`<br>`br_datasus_cid10.capitulos`<br>`br_datasus_cid10.subcategorias`<br>`br_ibge_populacao.municipio`<br>`br_ms_sinasc.microdados` |
| 178 | `mortalidade.idade_media_obito` | Idade média ao morrer | valor | `br_ms_sim.microdados`<br>`br_datasus_cid10.capitulos`<br>`br_datasus_cid10.subcategorias`<br>`br_ibge_populacao.municipio`<br>`br_ms_sinasc.microdados` |
| 179 | `mortalidade.homens` | Óbitos de homens | valor | `br_ms_sim.microdados`<br>`br_datasus_cid10.capitulos`<br>`br_datasus_cid10.subcategorias`<br>`br_ibge_populacao.municipio`<br>`br_ms_sinasc.microdados` |
| 180 | `mortalidade.mulheres` | Óbitos de mulheres | valor | `br_ms_sim.microdados`<br>`br_datasus_cid10.capitulos`<br>`br_datasus_cid10.subcategorias`<br>`br_ibge_populacao.municipio`<br>`br_ms_sinasc.microdados` |
| 181 | `mortalidade.causas_externas` | Óbitos por causas externas (violência, acidentes) | valor | `br_ms_sim.microdados`<br>`br_datasus_cid10.capitulos`<br>`br_datasus_cid10.subcategorias`<br>`br_ibge_populacao.municipio`<br>`br_ms_sinasc.microdados` |
| 182 | `mortalidade.suicidios` | Óbitos por suicídio | valor | `br_ms_sim.microdados`<br>`br_datasus_cid10.capitulos`<br>`br_datasus_cid10.subcategorias`<br>`br_ibge_populacao.municipio`<br>`br_ms_sinasc.microdados` |
| 183 | `mortalidade.agressoes` | Óbitos por agressão (homicídios) | valor | `br_ms_sim.microdados`<br>`br_datasus_cid10.capitulos`<br>`br_datasus_cid10.subcategorias`<br>`br_ibge_populacao.municipio`<br>`br_ms_sinasc.microdados` |
| 184 | `mortalidade.transporte` | Óbitos em acidentes de transporte | valor | `br_ms_sim.microdados`<br>`br_datasus_cid10.capitulos`<br>`br_datasus_cid10.subcategorias`<br>`br_ibge_populacao.municipio`<br>`br_ms_sinasc.microdados` |
| 185 | `mortalidade.maternas` | Óbitos maternos | valor | `br_ms_sim.microdados`<br>`br_datasus_cid10.capitulos`<br>`br_datasus_cid10.subcategorias`<br>`br_ibge_populacao.municipio`<br>`br_ms_sinasc.microdados` |
| 186 | `mortalidade.mal_definidas` | Óbitos com causa mal definida (qualidade do registro) | valor | `br_ms_sim.microdados`<br>`br_datasus_cid10.capitulos`<br>`br_datasus_cid10.subcategorias`<br>`br_ibge_populacao.municipio`<br>`br_ms_sinasc.microdados` |
| 187 | `mortalidade.nascidos_vivos` | Nascidos vivos usados como base da mortalidade infantil | valor | `br_ms_sim.microdados`<br>`br_datasus_cid10.capitulos`<br>`br_datasus_cid10.subcategorias`<br>`br_ibge_populacao.municipio`<br>`br_ms_sinasc.microdados` |
| 188 | `mortalidade.por_capitulo` | Óbitos por capítulo da CID-10 | série/ranking | `br_ms_sim.microdados`<br>`br_datasus_cid10.capitulos`<br>`br_datasus_cid10.subcategorias`<br>`br_ibge_populacao.municipio`<br>`br_ms_sinasc.microdados` |
| 189 | `mortalidade.top_causas` | Causas básicas de óbito mais frequentes | série/ranking | `br_ms_sim.microdados`<br>`br_datasus_cid10.capitulos`<br>`br_datasus_cid10.subcategorias`<br>`br_ibge_populacao.municipio`<br>`br_ms_sinasc.microdados` |
| 190 | `mortalidade.serie` | Óbitos totais e infantis ao longo dos anos | série/ranking | `br_ms_sim.microdados`<br>`br_datasus_cid10.capitulos`<br>`br_datasus_cid10.subcategorias`<br>`br_ibge_populacao.municipio`<br>`br_ms_sinasc.microdados` |
| 191 | `internacoes.internacoes` | Internações pelo SUS de residentes no ano | valor | `br_ms_sih.aihs_reduzidas`<br>`br_datasus_cid10.capitulos` |
| 192 | `internacoes.valor_total` | Valor pago pelo SUS pelas internações | valor | `br_ms_sih.aihs_reduzidas`<br>`br_datasus_cid10.capitulos` |
| 193 | `internacoes.obitos_hospitalares` | Óbitos durante a internação | valor | `br_ms_sih.aihs_reduzidas`<br>`br_datasus_cid10.capitulos` |
| 194 | `internacoes.permanencia_media` | Dias médios de permanência por internação | valor | `br_ms_sih.aihs_reduzidas`<br>`br_datasus_cid10.capitulos` |
| 195 | `internacoes.diarias_uti` | Diárias de UTI | valor | `br_ms_sih.aihs_reduzidas`<br>`br_datasus_cid10.capitulos` |
| 196 | `internacoes.no_municipio` | Internações feitas no próprio município | valor | `br_ms_sih.aihs_reduzidas`<br>`br_datasus_cid10.capitulos` |
| 197 | `internacoes.urgencia` | Internações de urgência | valor | `br_ms_sih.aihs_reduzidas`<br>`br_datasus_cid10.capitulos` |
| 198 | `internacoes.valor_medio_aih` | Valor médio pago por internação (AIH) | valor | `br_ms_sih.aihs_reduzidas`<br>`br_datasus_cid10.capitulos` |
| 199 | `internacoes.taxa_mortalidade_hospitalar` | Óbitos por 100 internações | valor | `br_ms_sih.aihs_reduzidas`<br>`br_datasus_cid10.capitulos` |
| 200 | `internacoes.pct_no_municipio` | Proporção das internações feitas no próprio município | valor | `br_ms_sih.aihs_reduzidas`<br>`br_datasus_cid10.capitulos` |
| 201 | `internacoes.por_capitulo` | Internações por capítulo da CID-10 | série/ranking | `br_ms_sih.aihs_reduzidas`<br>`br_datasus_cid10.capitulos` |
| 202 | `internacoes.serie` | Internações e valor pago ao longo dos anos | série/ranking | `br_ms_sih.aihs_reduzidas`<br>`br_datasus_cid10.capitulos` |
| 203 | `ieps.indicadores.cobertura_esf` | Cobertura da Estratégia Saúde da Família (IEPS) | valor | `br_ieps_saude.municipio` |
| 204 | `ieps.indicadores.cobertura_atencao_basica` | Cobertura da atenção básica (IEPS) | valor | `br_ieps_saude.municipio` |
| 205 | `ieps.indicadores.cobertura_plano_privado` | Proporção da população com plano de saúde | valor | `br_ieps_saude.municipio` |
| 206 | `ieps.indicadores.medicos_1000hab` | Médicos por mil habitantes | valor | `br_ieps_saude.municipio` |
| 207 | `ieps.indicadores.enfermeiros_1000hab` | Enfermeiros por mil habitantes | valor | `br_ieps_saude.municipio` |
| 208 | `ieps.indicadores.leitos_sus_100k` | Leitos SUS por 100 mil habitantes | valor | `br_ieps_saude.municipio` |
| 209 | `ieps.indicadores.leitos_uti_sus_100k` | Leitos de UTI SUS por 100 mil habitantes | valor | `br_ieps_saude.municipio` |
| 210 | `ieps.indicadores.despesa_saude_per_capita` | Gasto municipal em saúde por habitante | valor | `br_ieps_saude.municipio` |
| 211 | `ieps.indicadores.pct_receita_propria_saude` | Parcela da receita própria aplicada em saúde | valor | `br_ieps_saude.municipio` |
| 212 | `ieps.indicadores.taxa_mortalidade_evitavel_100k` | Óbitos por causas evitáveis por 100 mil hab. | valor | `br_ieps_saude.municipio` |
| 213 | `ieps.indicadores.taxa_internacao_csap_100k` | Internações sensíveis à atenção primária por 100 mil hab. | valor | `br_ieps_saude.municipio` |
| 214 | `ieps.indicadores.pct_prenatal_adequado` | Nascidos com pré-natal adequado (7+ consultas) | valor | `br_ieps_saude.municipio` |
| 215 | `ieps.indicadores.pct_prenatal_zero` | Nascidos sem nenhuma consulta de pré-natal | valor | `br_ieps_saude.municipio` |
| 216 | `imunizacao.serie` | Cobertura vacinal por vacina e ano | série/ranking | `br_ms_imunizacoes.municipio` |
| 217 | `planos_privados.beneficiarios_total` | Beneficiários de planos privados de saúde | valor | `br_ans_beneficiario.informacao_consolidada`<br>`br_ibge_populacao.municipio` |
| 218 | `planos_privados.medico_hospitalar` | Beneficiários de planos médico-hospitalares | valor | `br_ans_beneficiario.informacao_consolidada`<br>`br_ibge_populacao.municipio` |
| 219 | `planos_privados.odontologico` | Beneficiários de planos exclusivamente odontológicos | valor | `br_ans_beneficiario.informacao_consolidada`<br>`br_ibge_populacao.municipio` |
| 220 | `planos_privados.cobertura_pct` | Proporção da população com plano médico-hospitalar | valor | `br_ans_beneficiario.informacao_consolidada`<br>`br_ibge_populacao.municipio` |
| 221 | `planos_privados.por_contratacao` | Beneficiários por tipo de contratação (individual, coletivo…) | série/ranking | `br_ans_beneficiario.informacao_consolidada`<br>`br_ibge_populacao.municipio` |
| 222 | `farmacia_popular.estabelecimentos_credenciados` | Farmácias credenciadas no Farmácia Popular | valor | `br_saude_farmaciapopular.estabelecimentos` |
| 223 | `atencao_basica.cobertura_ab` | Cobertura da atenção básica em dez/2020 (e-Gestor) | valor | `br_ms_atencao_basica.municipio` |
| 224 | `atencao_basica.cobertura_esf` | Cobertura da Estratégia Saúde da Família em dez/2020 | valor | `br_ms_atencao_basica.municipio` |
| 225 | `atencao_basica.equipes` | Equipes de atenção básica em dez/2020 | valor | `br_ms_atencao_basica.municipio` |
| 226 | `atencao_basica.serie` | Cobertura da atenção básica e da ESF, 2007–2020 | série/ranking | `br_ms_atencao_basica.municipio` |

## Segurança (90)

| # | Indicador | O que mede | Tipo | Datasets de origem |
|---:|---|---|---|---|
| 227 | `isp_rj.ocorrencias.homicidio_doloso` | Ocorrências de homicídio doloso no ano (ISP-RJ) | valor | `br_rj_isp_estatisticas_seguranca.taxa_evolucao_anual_municipio`<br>`br_rj_isp_estatisticas_seguranca.evolucao_mensal_municipio`<br>`br_rj_isp_estatisticas_seguranca.taxa_evolucao_anual_uf` |
| 228 | `isp_rj.ocorrencias.letalidade_violenta` | Ocorrências de letalidade violenta no ano (ISP-RJ) | valor | `br_rj_isp_estatisticas_seguranca.taxa_evolucao_anual_municipio`<br>`br_rj_isp_estatisticas_seguranca.evolucao_mensal_municipio`<br>`br_rj_isp_estatisticas_seguranca.taxa_evolucao_anual_uf` |
| 229 | `isp_rj.ocorrencias.cvli` | Ocorrências de crimes violentos letais intencionais no ano (ISP-RJ) | valor | `br_rj_isp_estatisticas_seguranca.taxa_evolucao_anual_municipio`<br>`br_rj_isp_estatisticas_seguranca.evolucao_mensal_municipio`<br>`br_rj_isp_estatisticas_seguranca.taxa_evolucao_anual_uf` |
| 230 | `isp_rj.ocorrencias.latrocinio` | Ocorrências de latrocínio no ano (ISP-RJ) | valor | `br_rj_isp_estatisticas_seguranca.taxa_evolucao_anual_municipio`<br>`br_rj_isp_estatisticas_seguranca.evolucao_mensal_municipio`<br>`br_rj_isp_estatisticas_seguranca.taxa_evolucao_anual_uf` |
| 231 | `isp_rj.ocorrencias.lesao_corporal_morte` | Ocorrências de lesão corporal seguida de morte no ano (ISP-RJ) | valor | `br_rj_isp_estatisticas_seguranca.taxa_evolucao_anual_municipio`<br>`br_rj_isp_estatisticas_seguranca.evolucao_mensal_municipio`<br>`br_rj_isp_estatisticas_seguranca.taxa_evolucao_anual_uf` |
| 232 | `isp_rj.ocorrencias.tentativa_homicidio` | Ocorrências de tentativa de homicídio no ano (ISP-RJ) | valor | `br_rj_isp_estatisticas_seguranca.taxa_evolucao_anual_municipio`<br>`br_rj_isp_estatisticas_seguranca.evolucao_mensal_municipio`<br>`br_rj_isp_estatisticas_seguranca.taxa_evolucao_anual_uf` |
| 233 | `isp_rj.ocorrencias.intervencao_policial` | Ocorrências de mortes por intervenção policial no ano (ISP-RJ) | valor | `br_rj_isp_estatisticas_seguranca.taxa_evolucao_anual_municipio`<br>`br_rj_isp_estatisticas_seguranca.evolucao_mensal_municipio`<br>`br_rj_isp_estatisticas_seguranca.taxa_evolucao_anual_uf` |
| 234 | `isp_rj.ocorrencias.estupro` | Ocorrências de estupro no ano (ISP-RJ) | valor | `br_rj_isp_estatisticas_seguranca.taxa_evolucao_anual_municipio`<br>`br_rj_isp_estatisticas_seguranca.evolucao_mensal_municipio`<br>`br_rj_isp_estatisticas_seguranca.taxa_evolucao_anual_uf` |
| 235 | `isp_rj.ocorrencias.roubo_veiculo` | Ocorrências de roubo de veículo no ano (ISP-RJ) | valor | `br_rj_isp_estatisticas_seguranca.taxa_evolucao_anual_municipio`<br>`br_rj_isp_estatisticas_seguranca.evolucao_mensal_municipio`<br>`br_rj_isp_estatisticas_seguranca.taxa_evolucao_anual_uf` |
| 236 | `isp_rj.homicidio_doloso_ano_anterior` | Homicídios dolosos no ano anterior (ISP-RJ) | valor | `br_rj_isp_estatisticas_seguranca.taxa_evolucao_anual_municipio`<br>`br_rj_isp_estatisticas_seguranca.evolucao_mensal_municipio`<br>`br_rj_isp_estatisticas_seguranca.taxa_evolucao_anual_uf` |
| 237 | `isp_rj.taxas_100k.taxa_homicidio_doloso` | Taxa de homicídio doloso por 100 mil hab. no município | valor | `br_rj_isp_estatisticas_seguranca.taxa_evolucao_anual_municipio`<br>`br_rj_isp_estatisticas_seguranca.evolucao_mensal_municipio`<br>`br_rj_isp_estatisticas_seguranca.taxa_evolucao_anual_uf` |
| 238 | `isp_rj.taxas_100k.taxa_latrocinio` | Taxa de latrocínio por 100 mil hab. no município | valor | `br_rj_isp_estatisticas_seguranca.taxa_evolucao_anual_municipio`<br>`br_rj_isp_estatisticas_seguranca.evolucao_mensal_municipio`<br>`br_rj_isp_estatisticas_seguranca.taxa_evolucao_anual_uf` |
| 239 | `isp_rj.taxas_100k.taxa_lesao_corporal_morte` | Taxa de lesão corporal seguida de morte por 100 mil hab. no município | valor | `br_rj_isp_estatisticas_seguranca.taxa_evolucao_anual_municipio`<br>`br_rj_isp_estatisticas_seguranca.evolucao_mensal_municipio`<br>`br_rj_isp_estatisticas_seguranca.taxa_evolucao_anual_uf` |
| 240 | `isp_rj.taxas_100k.taxa_letalidade_violenta` | Taxa de letalidade violenta por 100 mil hab. no município | valor | `br_rj_isp_estatisticas_seguranca.taxa_evolucao_anual_municipio`<br>`br_rj_isp_estatisticas_seguranca.evolucao_mensal_municipio`<br>`br_rj_isp_estatisticas_seguranca.taxa_evolucao_anual_uf` |
| 241 | `isp_rj.taxas_100k.taxa_tentativa_homicidio` | Taxa de tentativa de homicídio por 100 mil hab. no município | valor | `br_rj_isp_estatisticas_seguranca.taxa_evolucao_anual_municipio`<br>`br_rj_isp_estatisticas_seguranca.evolucao_mensal_municipio`<br>`br_rj_isp_estatisticas_seguranca.taxa_evolucao_anual_uf` |
| 242 | `isp_rj.taxas_100k.taxa_estupro` | Taxa de estupro por 100 mil hab. no município | valor | `br_rj_isp_estatisticas_seguranca.taxa_evolucao_anual_municipio`<br>`br_rj_isp_estatisticas_seguranca.evolucao_mensal_municipio`<br>`br_rj_isp_estatisticas_seguranca.taxa_evolucao_anual_uf` |
| 243 | `isp_rj.taxas_100k.taxa_homicidio_intervencao_policial` | Taxa de mortes por intervenção policial por 100 mil hab. no município | valor | `br_rj_isp_estatisticas_seguranca.taxa_evolucao_anual_municipio`<br>`br_rj_isp_estatisticas_seguranca.evolucao_mensal_municipio`<br>`br_rj_isp_estatisticas_seguranca.taxa_evolucao_anual_uf` |
| 244 | `isp_rj.taxas_100k_uf.taxa_homicidio_doloso` | Taxa de homicídio doloso por 100 mil hab. na UF | valor | `br_rj_isp_estatisticas_seguranca.taxa_evolucao_anual_municipio`<br>`br_rj_isp_estatisticas_seguranca.evolucao_mensal_municipio`<br>`br_rj_isp_estatisticas_seguranca.taxa_evolucao_anual_uf` |
| 245 | `isp_rj.taxas_100k_uf.taxa_latrocinio` | Taxa de latrocínio por 100 mil hab. na UF | valor | `br_rj_isp_estatisticas_seguranca.taxa_evolucao_anual_municipio`<br>`br_rj_isp_estatisticas_seguranca.evolucao_mensal_municipio`<br>`br_rj_isp_estatisticas_seguranca.taxa_evolucao_anual_uf` |
| 246 | `isp_rj.taxas_100k_uf.taxa_lesao_corporal_morte` | Taxa de lesão corporal seguida de morte por 100 mil hab. na UF | valor | `br_rj_isp_estatisticas_seguranca.taxa_evolucao_anual_municipio`<br>`br_rj_isp_estatisticas_seguranca.evolucao_mensal_municipio`<br>`br_rj_isp_estatisticas_seguranca.taxa_evolucao_anual_uf` |
| 247 | `isp_rj.taxas_100k_uf.taxa_letalidade_violenta` | Taxa de letalidade violenta por 100 mil hab. na UF | valor | `br_rj_isp_estatisticas_seguranca.taxa_evolucao_anual_municipio`<br>`br_rj_isp_estatisticas_seguranca.evolucao_mensal_municipio`<br>`br_rj_isp_estatisticas_seguranca.taxa_evolucao_anual_uf` |
| 248 | `isp_rj.taxas_100k_uf.taxa_tentativa_homicidio` | Taxa de tentativa de homicídio por 100 mil hab. na UF | valor | `br_rj_isp_estatisticas_seguranca.taxa_evolucao_anual_municipio`<br>`br_rj_isp_estatisticas_seguranca.evolucao_mensal_municipio`<br>`br_rj_isp_estatisticas_seguranca.taxa_evolucao_anual_uf` |
| 249 | `isp_rj.taxas_100k_uf.taxa_estupro` | Taxa de estupro por 100 mil hab. na UF | valor | `br_rj_isp_estatisticas_seguranca.taxa_evolucao_anual_municipio`<br>`br_rj_isp_estatisticas_seguranca.evolucao_mensal_municipio`<br>`br_rj_isp_estatisticas_seguranca.taxa_evolucao_anual_uf` |
| 250 | `isp_rj.taxas_100k_uf.taxa_roubo_veiculo` | Taxa de roubo de veículo por 100 mil hab. na UF | valor | `br_rj_isp_estatisticas_seguranca.taxa_evolucao_anual_municipio`<br>`br_rj_isp_estatisticas_seguranca.evolucao_mensal_municipio`<br>`br_rj_isp_estatisticas_seguranca.taxa_evolucao_anual_uf` |
| 251 | `isp_rj.taxas_100k_uf.taxa_homicidio_intervencao_policial` | Taxa de mortes por intervenção policial por 100 mil hab. na UF | valor | `br_rj_isp_estatisticas_seguranca.taxa_evolucao_anual_municipio`<br>`br_rj_isp_estatisticas_seguranca.evolucao_mensal_municipio`<br>`br_rj_isp_estatisticas_seguranca.taxa_evolucao_anual_uf` |
| 252 | `isp_rj.mensal` | Ocorrências mensais por tipo de crime (ISP-RJ) | série/ranking | `br_rj_isp_estatisticas_seguranca.taxa_evolucao_anual_municipio`<br>`br_rj_isp_estatisticas_seguranca.evolucao_mensal_municipio`<br>`br_rj_isp_estatisticas_seguranca.taxa_evolucao_anual_uf` |
| 253 | `violencia_sinan.notificacoes` | Notificações de violência interpessoal e autoprovocada (SINAN) | valor | `br_ms_sinan_violencia.microdados_violencia` |
| 254 | `violencia_sinan.feminino` | Notificações de violência contra mulheres | valor | `br_ms_sinan_violencia.microdados_violencia` |
| 255 | `violencia_sinan.masculino` | Notificações de violência contra homens | valor | `br_ms_sinan_violencia.microdados_violencia` |
| 256 | `violencia_sinan.negros` | Notificações com vítima preta ou parda | valor | `br_ms_sinan_violencia.microdados_violencia` |
| 257 | `violencia_sinan.brancos` | Notificações com vítima branca | valor | `br_ms_sinan_violencia.microdados_violencia` |
| 258 | `violencia_sinan.raca_ignorada` | Notificações sem raça/cor informada | valor | `br_ms_sinan_violencia.microdados_violencia` |
| 259 | `violencia_sinan.autoprovocadas` | Notificações de lesão autoprovocada | valor | `br_ms_sinan_violencia.microdados_violencia` |
| 260 | `violencia_sinan.arma_fogo` | Notificações com uso de arma de fogo | valor | `br_ms_sinan_violencia.microdados_violencia` |
| 261 | `violencia_sinan.fisica` | Notificações de violência física | valor | `br_ms_sinan_violencia.microdados_violencia` |
| 262 | `violencia_sinan.psicologica` | Notificações de violência psicológica | valor | `br_ms_sinan_violencia.microdados_violencia` |
| 263 | `violencia_sinan.sexual` | Notificações de violência sexual | valor | `br_ms_sinan_violencia.microdados_violencia` |
| 264 | `violencia_sinan.negligencia` | Notificações de negligência ou abandono | valor | `br_ms_sinan_violencia.microdados_violencia` |
| 265 | `violencia_sinan.financeira` | Notificações de violência financeira | valor | `br_ms_sinan_violencia.microdados_violencia` |
| 266 | `violencia_sinan.tortura` | Notificações de tortura | valor | `br_ms_sinan_violencia.microdados_violencia` |
| 267 | `violencia_sinan.trafico_humano` | Notificações de tráfico de pessoas | valor | `br_ms_sinan_violencia.microdados_violencia` |
| 268 | `violencia_sinan.infantil_trabalho` | Notificações de trabalho infantil | valor | `br_ms_sinan_violencia.microdados_violencia` |
| 269 | `violencia_sinan.pct_feminino` | Parcela das notificações com vítima mulher | valor | `br_ms_sinan_violencia.microdados_violencia` |
| 270 | `violencia_sinan.pct_negros` | Parcela das notificações com vítima negra | valor | `br_ms_sinan_violencia.microdados_violencia` |
| 271 | `violencia_sinan.nota_raca` | Nota sobre a qualidade do campo raça/cor | valor | `br_ms_sinan_violencia.microdados_violencia` |
| 272 | `violencia_sinan.por_local` | Notificações por local de ocorrência | série/ranking | `br_ms_sinan_violencia.microdados_violencia` |
| 273 | `violencia_sinan.por_ciclo_vida` | Notificações por ciclo de vida da vítima | série/ranking | `br_ms_sinan_violencia.microdados_violencia` |
| 274 | `violencia_sinan.serie` | Notificações de violência ao longo dos anos | série/ranking | `br_ms_sinan_violencia.microdados_violencia` |
| 275 | `sinesp.por_tipo.feminicidio.vitimas` | Vítimas de feminicídio (SINESP) | valor | `br_mj_sinesp.municipio_mes`<br>`br_ibge_populacao.municipio` |
| 276 | `sinesp.por_tipo.feminicidio.vitimas_feminino` | Vítimas mulheres de feminicídio (SINESP) | valor | `br_mj_sinesp.municipio_mes`<br>`br_ibge_populacao.municipio` |
| 277 | `sinesp.por_tipo.feminicidio.meses` | Meses com dado reportado para feminicídio | valor | `br_mj_sinesp.municipio_mes`<br>`br_ibge_populacao.municipio` |
| 278 | `sinesp.por_tipo.homicidio_doloso.vitimas` | Vítimas de homicídio doloso (SINESP) | valor | `br_mj_sinesp.municipio_mes`<br>`br_ibge_populacao.municipio` |
| 279 | `sinesp.por_tipo.homicidio_doloso.vitimas_feminino` | Vítimas mulheres de homicídio doloso (SINESP) | valor | `br_mj_sinesp.municipio_mes`<br>`br_ibge_populacao.municipio` |
| 280 | `sinesp.por_tipo.homicidio_doloso.meses` | Meses com dado reportado para homicídio doloso | valor | `br_mj_sinesp.municipio_mes`<br>`br_ibge_populacao.municipio` |
| 281 | `sinesp.por_tipo.latrocinio.vitimas` | Vítimas de latrocínio (SINESP) | valor | `br_mj_sinesp.municipio_mes`<br>`br_ibge_populacao.municipio` |
| 282 | `sinesp.por_tipo.latrocinio.vitimas_feminino` | Vítimas mulheres de latrocínio (SINESP) | valor | `br_mj_sinesp.municipio_mes`<br>`br_ibge_populacao.municipio` |
| 283 | `sinesp.por_tipo.latrocinio.meses` | Meses com dado reportado para latrocínio | valor | `br_mj_sinesp.municipio_mes`<br>`br_ibge_populacao.municipio` |
| 284 | `sinesp.por_tipo.lesao_corporal_seguida_de_morte.vitimas` | Vítimas de lesão corporal seguida de morte (SINESP) | valor | `br_mj_sinesp.municipio_mes`<br>`br_ibge_populacao.municipio` |
| 285 | `sinesp.por_tipo.lesao_corporal_seguida_de_morte.vitimas_feminino` | Vítimas mulheres de lesão corporal seguida de morte (SINESP) | valor | `br_mj_sinesp.municipio_mes`<br>`br_ibge_populacao.municipio` |
| 286 | `sinesp.por_tipo.lesao_corporal_seguida_de_morte.meses` | Meses com dado reportado para lesão corporal seguida de morte | valor | `br_mj_sinesp.municipio_mes`<br>`br_ibge_populacao.municipio` |
| 287 | `sinesp.por_tipo.mandado_de_prisao_cumprido.ocorrencias` | Ocorrências de mandado de prisão cumprido (SINESP) | valor | `br_mj_sinesp.municipio_mes`<br>`br_ibge_populacao.municipio` |
| 288 | `sinesp.por_tipo.mandado_de_prisao_cumprido.meses` | Meses com dado reportado para mandado de prisão cumprido | valor | `br_mj_sinesp.municipio_mes`<br>`br_ibge_populacao.municipio` |
| 289 | `sinesp.por_tipo.morte_a_esclarecer.vitimas` | Vítimas de morte a esclarecer (SINESP) | valor | `br_mj_sinesp.municipio_mes`<br>`br_ibge_populacao.municipio` |
| 290 | `sinesp.por_tipo.morte_a_esclarecer.vitimas_feminino` | Vítimas mulheres de morte a esclarecer (SINESP) | valor | `br_mj_sinesp.municipio_mes`<br>`br_ibge_populacao.municipio` |
| 291 | `sinesp.por_tipo.morte_a_esclarecer.meses` | Meses com dado reportado para morte a esclarecer | valor | `br_mj_sinesp.municipio_mes`<br>`br_ibge_populacao.municipio` |
| 292 | `sinesp.por_tipo.morte_no_transito_exceto_homicidio_doloso.vitimas` | Vítimas de morte no trânsito (SINESP) | valor | `br_mj_sinesp.municipio_mes`<br>`br_ibge_populacao.municipio` |
| 293 | `sinesp.por_tipo.morte_no_transito_exceto_homicidio_doloso.vitimas_feminino` | Vítimas mulheres de morte no trânsito (SINESP) | valor | `br_mj_sinesp.municipio_mes`<br>`br_ibge_populacao.municipio` |
| 294 | `sinesp.por_tipo.morte_no_transito_exceto_homicidio_doloso.meses` | Meses com dado reportado para morte no trânsito | valor | `br_mj_sinesp.municipio_mes`<br>`br_ibge_populacao.municipio` |
| 295 | `sinesp.por_tipo.suicidio.vitimas` | Vítimas de suicídio (SINESP) | valor | `br_mj_sinesp.municipio_mes`<br>`br_ibge_populacao.municipio` |
| 296 | `sinesp.por_tipo.suicidio.vitimas_feminino` | Vítimas mulheres de suicídio (SINESP) | valor | `br_mj_sinesp.municipio_mes`<br>`br_ibge_populacao.municipio` |
| 297 | `sinesp.por_tipo.suicidio.meses` | Meses com dado reportado para suicídio | valor | `br_mj_sinesp.municipio_mes`<br>`br_ibge_populacao.municipio` |
| 298 | `sinesp.por_tipo.tentativa_de_feminicidio.vitimas` | Vítimas de tentativa de feminicídio (SINESP) | valor | `br_mj_sinesp.municipio_mes`<br>`br_ibge_populacao.municipio` |
| 299 | `sinesp.por_tipo.tentativa_de_feminicidio.vitimas_feminino` | Vítimas mulheres de tentativa de feminicídio (SINESP) | valor | `br_mj_sinesp.municipio_mes`<br>`br_ibge_populacao.municipio` |
| 300 | `sinesp.por_tipo.tentativa_de_feminicidio.meses` | Meses com dado reportado para tentativa de feminicídio | valor | `br_mj_sinesp.municipio_mes`<br>`br_ibge_populacao.municipio` |
| 301 | `sinesp.por_tipo.tentativa_de_homicidio.vitimas` | Vítimas de tentativa de homicídio (SINESP) | valor | `br_mj_sinesp.municipio_mes`<br>`br_ibge_populacao.municipio` |
| 302 | `sinesp.por_tipo.tentativa_de_homicidio.vitimas_feminino` | Vítimas mulheres de tentativa de homicídio (SINESP) | valor | `br_mj_sinesp.municipio_mes`<br>`br_ibge_populacao.municipio` |
| 303 | `sinesp.por_tipo.tentativa_de_homicidio.meses` | Meses com dado reportado para tentativa de homicídio | valor | `br_mj_sinesp.municipio_mes`<br>`br_ibge_populacao.municipio` |
| 304 | `sinesp.taxa_homicidio_doloso_100k.municipio` | Vítimas de homicídio doloso por 100 mil hab. (SINESP) | valor | `br_mj_sinesp.municipio_mes`<br>`br_ibge_populacao.municipio` |
| 305 | `sinesp.taxa_homicidio_doloso_100k.uf` | Taxa de homicídio doloso da UF (SINESP) | valor | `br_mj_sinesp.municipio_mes`<br>`br_ibge_populacao.municipio` |
| 306 | `sinesp.taxa_homicidio_doloso_100k.brasil` | Taxa de homicídio doloso do Brasil (SINESP) | valor | `br_mj_sinesp.municipio_mes`<br>`br_ibge_populacao.municipio` |
| 307 | `sinesp.serie` | Vítimas por tipo de crime, ano a ano (SINESP) | série/ranking | `br_mj_sinesp.municipio_mes`<br>`br_ibge_populacao.municipio` |
| 308 | `prf.desde` | Início do período de acidentes da PRF considerado | valor | `br_prf_acidentes.ocorrencia` |
| 309 | `prf.ate` | Fim do período de acidentes da PRF considerado | valor | `br_prf_acidentes.ocorrencia` |
| 310 | `prf.acidentes` | Acidentes em rodovias federais no município (PRF) | valor | `br_prf_acidentes.ocorrencia` |
| 311 | `prf.mortos` | Mortos em acidentes nas rodovias federais | valor | `br_prf_acidentes.ocorrencia` |
| 312 | `prf.feridos_graves` | Feridos graves em acidentes nas rodovias federais | valor | `br_prf_acidentes.ocorrencia` |
| 313 | `prf.por_ano` | Acidentes e mortes nas rodovias federais por ano | série/ranking | `br_prf_acidentes.ocorrencia` |
| 314 | `prf.por_rodovia` | Acidentes por rodovia federal (BR) | série/ranking | `br_prf_acidentes.ocorrencia` |
| 315 | `prf.por_causa` | Acidentes por causa apontada pela PRF | série/ranking | `br_prf_acidentes.ocorrencia` |
| 316 | `prf.por_tipo` | Acidentes por tipo (colisão, saída de pista…) | série/ranking | `br_prf_acidentes.ocorrencia` |

## Infraestrutura e energia (51)

| # | Indicador | O que mede | Tipo | Datasets de origem |
|---:|---|---|---|---|
| 317 | `snis.populacao_atendida_agua` | População atendida com abastecimento de água (SNIS) | valor | `br_mdr_snis.municipio_agua_esgoto` |
| 318 | `snis.populacao_atentida_esgoto` | População atendida com esgotamento sanitário (SNIS) | valor | `br_mdr_snis.municipio_agua_esgoto` |
| 319 | `snis.indice_atendimento_total_agua` | Índice de atendimento total de água (%) | valor | `br_mdr_snis.municipio_agua_esgoto` |
| 320 | `snis.indice_coleta_esgoto` | Índice de coleta de esgoto (%) | valor | `br_mdr_snis.municipio_agua_esgoto` |
| 321 | `snis.indice_tratamento_esgoto` | Parcela do esgoto coletado que é tratada (%) | valor | `br_mdr_snis.municipio_agua_esgoto` |
| 322 | `snis.indice_perda_distribuicao_agua` | Perdas na distribuição de água (%) | valor | `br_mdr_snis.municipio_agua_esgoto` |
| 323 | `snis.extensao_rede_agua` | Extensão da rede de água (km) | valor | `br_mdr_snis.municipio_agua_esgoto` |
| 324 | `snis.extensao_rede_esgoto` | Extensão da rede de esgoto (km) | valor | `br_mdr_snis.municipio_agua_esgoto` |
| 325 | `snis.volume_agua_consumido` | Volume de água consumido no ano (mil m³) | valor | `br_mdr_snis.municipio_agua_esgoto` |
| 326 | `snis.volume_esgoto_coletado` | Volume de esgoto coletado (mil m³) | valor | `br_mdr_snis.municipio_agua_esgoto` |
| 327 | `snis.volume_esgoto_tratado` | Volume de esgoto tratado (mil m³) | valor | `br_mdr_snis.municipio_agua_esgoto` |
| 328 | `snis.despesa_total_servico` | Despesa total com os serviços de água e esgoto | valor | `br_mdr_snis.municipio_agua_esgoto` |
| 329 | `atlas_esgotos.populacao_urbana_2013` | População urbana em 2013 (Atlas Esgotos) | valor | `br_ana_atlas_esgotos.municipio` |
| 330 | `atlas_esgotos.populacao_urbana_2035` | População urbana projetada para 2035 | valor | `br_ana_atlas_esgotos.municipio` |
| 331 | `atlas_esgotos.prestador_servico_esgotamento_sanitario` | Prestador do serviço de esgoto | valor | `br_ana_atlas_esgotos.municipio` |
| 332 | `atlas_esgotos.indice_sem_atendimento_sem_coleta_sem_tratamento` | População sem coleta nem tratamento de esgoto (%) | valor | `br_ana_atlas_esgotos.municipio` |
| 333 | `atlas_esgotos.indice_atendimento_solucao_individual` | População atendida por fossa/solução individual (%) | valor | `br_ana_atlas_esgotos.municipio` |
| 334 | `atlas_esgotos.indice_atendimento_com_coleta_sem_tratamento` | População com coleta mas sem tratamento (%) | valor | `br_ana_atlas_esgotos.municipio` |
| 335 | `atlas_esgotos.indice_atendimento_com_coleta_com_tratamento` | População com coleta e tratamento (%) | valor | `br_ana_atlas_esgotos.municipio` |
| 336 | `atlas_esgotos.investimento_coleta` | Investimento estimado em coleta de esgoto até 2035 | valor | `br_ana_atlas_esgotos.municipio` |
| 337 | `atlas_esgotos.investimento_tratamento` | Investimento estimado em tratamento de esgoto até 2035 | valor | `br_ana_atlas_esgotos.municipio` |
| 338 | `atlas_esgotos.investimento_coleta_tratatamento` | Investimento total estimado em coleta e tratamento | valor | `br_ana_atlas_esgotos.municipio` |
| 339 | `censo_domicilios.esgotamento.total` | Moradores na base do quesito esgotamento (Censo 2022) | valor | `br_ibge_censo_2022.domicilio_recenseado` |
| 340 | `censo_domicilios.esgotamento.categorias` | Moradores por forma de esgotamento sanitário | série/ranking | `br_ibge_censo_2022.domicilio_recenseado` |
| 341 | `censo_domicilios.agua.total` | Moradores na base do quesito abastecimento de água | valor | `br_ibge_censo_2022.domicilio_recenseado` |
| 342 | `censo_domicilios.agua.categorias` | Moradores por forma de abastecimento de água | série/ranking | `br_ibge_censo_2022.domicilio_recenseado` |
| 343 | `censo_domicilios.lixo.total` | Moradores na base do quesito destino do lixo | valor | `br_ibge_censo_2022.domicilio_recenseado` |
| 344 | `censo_domicilios.lixo.categorias` | Moradores por destino do lixo | série/ranking | `br_ibge_censo_2022.domicilio_recenseado` |
| 345 | `censo_domicilios.tipo_domicilio.total` | Domicílios na base do quesito tipo de domicílio | valor | `br_ibge_censo_2022.domicilio_recenseado` |
| 346 | `censo_domicilios.tipo_domicilio.categorias` | Domicílios por tipo (casa, apartamento, vila…) | série/ranking | `br_ibge_censo_2022.domicilio_recenseado` |
| 347 | `censo_domicilios.domicilios_recenseados` | Domicílios recenseados no Censo 2022 | série/ranking | `br_ibge_censo_2022.domicilio_recenseado` |
| 348 | `frota.total` | Veículos registrados no município | valor | `br_ibge_populacao.municipio` |
| 349 | `frota.por_tipo` | Frota por tipo de veículo | série/ranking | `br_ibge_populacao.municipio` |
| 350 | `frota.veiculos_1000hab.municipio` | Veículos por mil habitantes no município | valor | `br_ibge_populacao.municipio` |
| 351 | `frota.veiculos_1000hab.uf` | Veículos por mil habitantes na UF | valor | `br_ibge_populacao.municipio` |
| 352 | `frota.veiculos_1000hab.brasil` | Veículos por mil habitantes no Brasil | valor | `br_ibge_populacao.municipio` |
| 353 | `frota.serie` | Frota total ao longo dos anos | série/ranking | `br_ibge_populacao.municipio` |
| 354 | `energia_gd.instalacoes` | Instalações de geração distribuída (solar etc.) | valor | `br_aneel_dadosabertos.empreendimento_geracao_distribuida`<br>`br_ibge_populacao.municipio` |
| 355 | `energia_gd.potencia_mw` | Potência instalada de geração distribuída (MW) | valor | `br_aneel_dadosabertos.empreendimento_geracao_distribuida`<br>`br_ibge_populacao.municipio` |
| 356 | `energia_gd.ucs_recebem_credito` | Unidades consumidoras que recebem créditos de GD | valor | `br_aneel_dadosabertos.empreendimento_geracao_distribuida`<br>`br_ibge_populacao.municipio` |
| 357 | `energia_gd.w_por_habitante` | Potência de GD por habitante (W) | valor | `br_aneel_dadosabertos.empreendimento_geracao_distribuida`<br>`br_ibge_populacao.municipio` |
| 358 | `energia_gd.por_classe` | GD por classe de consumo (residencial, comercial…) | série/ranking | `br_aneel_dadosabertos.empreendimento_geracao_distribuida`<br>`br_ibge_populacao.municipio` |
| 359 | `energia_gd.por_fonte` | GD por fonte de energia | série/ranking | `br_aneel_dadosabertos.empreendimento_geracao_distribuida`<br>`br_ibge_populacao.municipio` |
| 360 | `energia_gd.por_ano_cadastro` | Novas instalações de GD por ano | série/ranking | `br_aneel_dadosabertos.empreendimento_geracao_distribuida`<br>`br_ibge_populacao.municipio` |
| 361 | `obras_cno.obras` | Obras de construção civil registradas na Receita (CNO) | valor | `br_rf_cno.microdados` |
| 362 | `obras_cno.por_situacao` | Obras por situação (ativa, paralisada, encerrada…) | série/ranking | `br_rf_cno.microdados` |
| 363 | `obras_cno.iniciadas_por_ano` | Obras iniciadas e área construída por ano | série/ranking | `br_rf_cno.microdados` |
| 364 | `outorgas_agua.outorgas` | Outorgas de captação de água no município | valor | `br_ana_outorgas.captacoes` |
| 365 | `outorgas_agua.vazao_total` | Vazão média somada das captações outorgadas (m³/h) | valor | `br_ana_outorgas.captacoes` |
| 366 | `outorgas_agua.por_esfera` | Outorgas por esfera (federal ou estadual) | série/ranking | `br_ana_outorgas.captacoes` |
| 367 | `outorgas_agua.maiores` | Maiores captações outorgadas por responsável | série/ranking | `br_ana_outorgas.captacoes` |

## Meio ambiente (28)

| # | Indicador | O que mede | Tipo | Datasets de origem |
|---:|---|---|---|---|
| 368 | `prodes.biomas` | Biomas monitorados pelo PRODES no município | série/ranking | `br_inpe_prodes.municipio_bioma` |
| 369 | `prodes.serie` | Desmatamento anual detectado pelo PRODES (km²) | série/ranking | `br_inpe_prodes.municipio_bioma` |
| 370 | `seeg.gas` | Gás considerado na estimativa de emissões | valor | `br_seeg_emissoes.municipio`<br>`br_seeg_emissoes.dicionario` |
| 371 | `seeg.tipo` | Tipo de emissão considerado (bruta/líquida) | valor | `br_seeg_emissoes.municipio`<br>`br_seeg_emissoes.dicionario` |
| 372 | `seeg.por_setor` | Emissões de gases de efeito estufa por setor (SEEG) | série/ranking | `br_seeg_emissoes.municipio`<br>`br_seeg_emissoes.dicionario` |
| 373 | `seeg.total_tco2e` | Emissões totais em toneladas de CO₂ equivalente | valor | `br_seeg_emissoes.municipio`<br>`br_seeg_emissoes.dicionario` |
| 374 | `queimadas.serie` | Focos de calor detectados por satélite, por ano | série/ranking | `br_inpe_queimadas.microdados` |
| 375 | `sisam.serie` | Concentração de poluentes do ar estimada, por ano | série/ranking | `br_inpe_sisam.microdados` |
| 376 | `mapbiomas.transicoes` | Transições de uso e cobertura da terra (MapBiomas) | série/ranking | `br_mapbiomas_estatisticas.transicao_municipio_de_para_decenal`<br>`br_mapbiomas_estatisticas.classe` |
| 377 | `car.imoveis` | Imóveis no Cadastro Ambiental Rural (sem cancelados) | valor | `br_sfb_sicar.area_imovel` |
| 378 | `car.area_ha` | Área total dos imóveis no CAR (ha) | valor | `br_sfb_sicar.area_imovel` |
| 379 | `car.pendentes` | Cadastros do CAR com status pendente | valor | `br_sfb_sicar.area_imovel` |
| 380 | `car.suspensos` | Cadastros do CAR suspensos | valor | `br_sfb_sicar.area_imovel` |
| 381 | `car.por_tipo` | Imóveis do CAR por tipo (rural, assentamento, terra indígena…) | série/ranking | `br_sfb_sicar.area_imovel` |
| 382 | `car.por_condicao` | Imóveis do CAR por etapa de análise | série/ranking | `br_sfb_sicar.area_imovel` |
| 383 | `car.camadas_ha.reserva_legal` | Área declarada de reserva legal (ha) | valor | `br_sfb_sicar.area_imovel` |
| 384 | `car.camadas_ha.app` | Área declarada de preservação permanente (ha) | valor | `br_sfb_sicar.area_imovel` |
| 385 | `car.camadas_ha.vegetacao_nativa` | Área declarada de vegetação nativa (ha) | valor | `br_sfb_sicar.area_imovel` |
| 386 | `car.camadas_ha.area_consolidada` | Área rural consolidada declarada (ha) | valor | `br_sfb_sicar.area_imovel` |
| 387 | `car.camadas_ha.uso_restrito` | Área de uso restrito declarada (ha) | valor | `br_sfb_sicar.area_imovel` |
| 388 | `ibama.autos_total` | Autos de infração ambiental do IBAMA no município | valor | `br_ibama_autos.auto_infracao`<br>`br_ibama_embargos_novo.termo_embargo` |
| 389 | `ibama.valor_total` | Valor somado das multas do IBAMA | valor | `br_ibama_autos.auto_infracao`<br>`br_ibama_embargos_novo.termo_embargo` |
| 390 | `ibama.serie` | Autos de infração e multas do IBAMA por ano | série/ranking | `br_ibama_autos.auto_infracao`<br>`br_ibama_embargos_novo.termo_embargo` |
| 391 | `ibama.tipos_10a` | Autos do IBAMA por tipo de infração (10 anos) | série/ranking | `br_ibama_autos.auto_infracao`<br>`br_ibama_embargos_novo.termo_embargo` |
| 392 | `ibama.embargos` | Áreas embargadas pelo IBAMA | valor | `br_ibama_autos.auto_infracao`<br>`br_ibama_embargos_novo.termo_embargo` |
| 393 | `ibama.embargos_5a` | Embargos do IBAMA nos últimos 5 anos | valor | `br_ibama_autos.auto_infracao`<br>`br_ibama_embargos_novo.termo_embargo` |
| 394 | `desastres.municipios_uf_com_reconhecimento` | Municípios da UF com emergência ou calamidade vigente | valor | `br_sedec_desastres.reconhecimentos_vigentes` |
| 395 | `estacoes_inmet.estacoes` | Estações meteorológicas automáticas do INMET | série/ranking | `br_inmet_bdmep.estacao` |

## Conectividade (6)

| # | Indicador | O que mede | Tipo | Datasets de origem |
|---:|---|---|---|---|
| 396 | `banda_larga.densidade_100hab` | Acessos de banda larga fixa por 100 habitantes | valor | `br_anatel_banda_larga_fixa.densidade_municipio`<br>`br_anatel_indice_brasileiro_conectividade.municipio`<br>`br_anatel_banda_larga_fixa.densidade_brasil` |
| 397 | `banda_larga.densidade_brasil` | Densidade de banda larga fixa no Brasil | valor | `br_anatel_banda_larga_fixa.densidade_municipio`<br>`br_anatel_indice_brasileiro_conectividade.municipio`<br>`br_anatel_banda_larga_fixa.densidade_brasil` |
| 398 | `ibc.ibc` | Índice Brasileiro de Conectividade da Anatel (0–100) | valor | `br_anatel_banda_larga_fixa.densidade_municipio`<br>`br_anatel_indice_brasileiro_conectividade.municipio`<br>`br_anatel_banda_larga_fixa.densidade_brasil` |
| 399 | `ibc.media_brasil` | IBC médio do Brasil | valor | `br_anatel_banda_larga_fixa.densidade_municipio`<br>`br_anatel_indice_brasileiro_conectividade.municipio`<br>`br_anatel_banda_larga_fixa.densidade_brasil` |
| 400 | `ibc.cobertura_pop_4g5g` | População coberta por 4G/5G (%) | valor | `br_anatel_banda_larga_fixa.densidade_municipio`<br>`br_anatel_indice_brasileiro_conectividade.municipio`<br>`br_anatel_banda_larga_fixa.densidade_brasil` |
| 401 | `ibc.fibra` | Presença de backhaul de fibra óptica | valor | `br_anatel_banda_larga_fixa.densidade_municipio`<br>`br_anatel_indice_brasileiro_conectividade.municipio`<br>`br_anatel_banda_larga_fixa.densidade_brasil` |

## Política (45)

| # | Indicador | O que mede | Tipo | Datasets de origem |
|---:|---|---|---|---|
| 402 | `eleitorado.aptos` | Eleitores aptos a votar | valor | `br_tse_eleicoes.perfil_eleitorado_municipio_zona`<br>`br_tse_eleicoes.detalhes_votacao_municipio`<br>`br_tse_eleicoes.resultados_candidato_municipio`<br>`br_tse_eleicoes.candidatos` |
| 403 | `eleitorado.biometria` | Eleitores com biometria cadastrada | valor | `br_tse_eleicoes.perfil_eleitorado_municipio_zona`<br>`br_tse_eleicoes.detalhes_votacao_municipio`<br>`br_tse_eleicoes.resultados_candidato_municipio`<br>`br_tse_eleicoes.candidatos` |
| 404 | `eleitorado.zonas` | Zonas eleitorais no município | valor | `br_tse_eleicoes.perfil_eleitorado_municipio_zona`<br>`br_tse_eleicoes.detalhes_votacao_municipio`<br>`br_tse_eleicoes.resultados_candidato_municipio`<br>`br_tse_eleicoes.candidatos` |
| 405 | `genero.4` | Eleitores mulheres | valor | `br_tse_eleicoes.perfil_eleitorado_municipio_zona`<br>`br_tse_eleicoes.detalhes_votacao_municipio`<br>`br_tse_eleicoes.resultados_candidato_municipio`<br>`br_tse_eleicoes.candidatos` |
| 406 | `genero.0` | Eleitores sem gênero informado | valor | `br_tse_eleicoes.perfil_eleitorado_municipio_zona`<br>`br_tse_eleicoes.detalhes_votacao_municipio`<br>`br_tse_eleicoes.resultados_candidato_municipio`<br>`br_tse_eleicoes.candidatos` |
| 407 | `genero.2` | Eleitores homens | valor | `br_tse_eleicoes.perfil_eleitorado_municipio_zona`<br>`br_tse_eleicoes.detalhes_votacao_municipio`<br>`br_tse_eleicoes.resultados_candidato_municipio`<br>`br_tse_eleicoes.candidatos` |
| 408 | `instrucao.3` | Eleitores com fundamental incompleto | valor | `br_tse_eleicoes.perfil_eleitorado_municipio_zona`<br>`br_tse_eleicoes.detalhes_votacao_municipio`<br>`br_tse_eleicoes.resultados_candidato_municipio`<br>`br_tse_eleicoes.candidatos` |
| 409 | `instrucao.5` | Eleitores com médio incompleto | valor | `br_tse_eleicoes.perfil_eleitorado_municipio_zona`<br>`br_tse_eleicoes.detalhes_votacao_municipio`<br>`br_tse_eleicoes.resultados_candidato_municipio`<br>`br_tse_eleicoes.candidatos` |
| 410 | `instrucao.6` | Eleitores com médio completo | valor | `br_tse_eleicoes.perfil_eleitorado_municipio_zona`<br>`br_tse_eleicoes.detalhes_votacao_municipio`<br>`br_tse_eleicoes.resultados_candidato_municipio`<br>`br_tse_eleicoes.candidatos` |
| 411 | `instrucao.4` | Eleitores com fundamental completo | valor | `br_tse_eleicoes.perfil_eleitorado_municipio_zona`<br>`br_tse_eleicoes.detalhes_votacao_municipio`<br>`br_tse_eleicoes.resultados_candidato_municipio`<br>`br_tse_eleicoes.candidatos` |
| 412 | `instrucao.8` | Eleitores com superior completo | valor | `br_tse_eleicoes.perfil_eleitorado_municipio_zona`<br>`br_tse_eleicoes.detalhes_votacao_municipio`<br>`br_tse_eleicoes.resultados_candidato_municipio`<br>`br_tse_eleicoes.candidatos` |
| 413 | `instrucao.2` | Eleitores que leem e escrevem | valor | `br_tse_eleicoes.perfil_eleitorado_municipio_zona`<br>`br_tse_eleicoes.detalhes_votacao_municipio`<br>`br_tse_eleicoes.resultados_candidato_municipio`<br>`br_tse_eleicoes.candidatos` |
| 414 | `instrucao.7` | Eleitores com superior incompleto | valor | `br_tse_eleicoes.perfil_eleitorado_municipio_zona`<br>`br_tse_eleicoes.detalhes_votacao_municipio`<br>`br_tse_eleicoes.resultados_candidato_municipio`<br>`br_tse_eleicoes.candidatos` |
| 415 | `instrucao.1` | Eleitores analfabetos | valor | `br_tse_eleicoes.perfil_eleitorado_municipio_zona`<br>`br_tse_eleicoes.detalhes_votacao_municipio`<br>`br_tse_eleicoes.resultados_candidato_municipio`<br>`br_tse_eleicoes.candidatos` |
| 416 | `instrucao.0` | Eleitores sem escolaridade informada | valor | `br_tse_eleicoes.perfil_eleitorado_municipio_zona`<br>`br_tse_eleicoes.detalhes_votacao_municipio`<br>`br_tse_eleicoes.resultados_candidato_municipio`<br>`br_tse_eleicoes.candidatos` |
| 417 | `prefeito.turno` | Turno que decidiu a eleição para prefeito | valor | `br_tse_eleicoes.perfil_eleitorado_municipio_zona`<br>`br_tse_eleicoes.detalhes_votacao_municipio`<br>`br_tse_eleicoes.resultados_candidato_municipio`<br>`br_tse_eleicoes.candidatos` |
| 418 | `prefeito.aptos` | Eleitores aptos na eleição para prefeito | valor | `br_tse_eleicoes.perfil_eleitorado_municipio_zona`<br>`br_tse_eleicoes.detalhes_votacao_municipio`<br>`br_tse_eleicoes.resultados_candidato_municipio`<br>`br_tse_eleicoes.candidatos` |
| 419 | `prefeito.secoes` | Seções eleitorais | valor | `br_tse_eleicoes.perfil_eleitorado_municipio_zona`<br>`br_tse_eleicoes.detalhes_votacao_municipio`<br>`br_tse_eleicoes.resultados_candidato_municipio`<br>`br_tse_eleicoes.candidatos` |
| 420 | `prefeito.comparecimento` | Eleitores que votaram para prefeito | valor | `br_tse_eleicoes.perfil_eleitorado_municipio_zona`<br>`br_tse_eleicoes.detalhes_votacao_municipio`<br>`br_tse_eleicoes.resultados_candidato_municipio`<br>`br_tse_eleicoes.candidatos` |
| 421 | `prefeito.abstencoes` | Abstenções na eleição para prefeito | valor | `br_tse_eleicoes.perfil_eleitorado_municipio_zona`<br>`br_tse_eleicoes.detalhes_votacao_municipio`<br>`br_tse_eleicoes.resultados_candidato_municipio`<br>`br_tse_eleicoes.candidatos` |
| 422 | `prefeito.votos_nominais` | Votos válidos em candidatos a prefeito | valor | `br_tse_eleicoes.perfil_eleitorado_municipio_zona`<br>`br_tse_eleicoes.detalhes_votacao_municipio`<br>`br_tse_eleicoes.resultados_candidato_municipio`<br>`br_tse_eleicoes.candidatos` |
| 423 | `prefeito.votos_brancos` | Votos em branco para prefeito | valor | `br_tse_eleicoes.perfil_eleitorado_municipio_zona`<br>`br_tse_eleicoes.detalhes_votacao_municipio`<br>`br_tse_eleicoes.resultados_candidato_municipio`<br>`br_tse_eleicoes.candidatos` |
| 424 | `prefeito.votos_nulos` | Votos nulos para prefeito | valor | `br_tse_eleicoes.perfil_eleitorado_municipio_zona`<br>`br_tse_eleicoes.detalhes_votacao_municipio`<br>`br_tse_eleicoes.resultados_candidato_municipio`<br>`br_tse_eleicoes.candidatos` |
| 425 | `prefeito.eleito.nome_urna` | Nome de urna do prefeito eleito | valor | `br_tse_eleicoes.perfil_eleitorado_municipio_zona`<br>`br_tse_eleicoes.detalhes_votacao_municipio`<br>`br_tse_eleicoes.resultados_candidato_municipio`<br>`br_tse_eleicoes.candidatos` |
| 426 | `prefeito.eleito.partido` | Partido do prefeito eleito | valor | `br_tse_eleicoes.perfil_eleitorado_municipio_zona`<br>`br_tse_eleicoes.detalhes_votacao_municipio`<br>`br_tse_eleicoes.resultados_candidato_municipio`<br>`br_tse_eleicoes.candidatos` |
| 427 | `prefeito.eleito.votos` | Votos do prefeito eleito | valor | `br_tse_eleicoes.perfil_eleitorado_municipio_zona`<br>`br_tse_eleicoes.detalhes_votacao_municipio`<br>`br_tse_eleicoes.resultados_candidato_municipio`<br>`br_tse_eleicoes.candidatos` |
| 428 | `prefeito.eleito.turno` | Turno em que o prefeito foi eleito | valor | `br_tse_eleicoes.perfil_eleitorado_municipio_zona`<br>`br_tse_eleicoes.detalhes_votacao_municipio`<br>`br_tse_eleicoes.resultados_candidato_municipio`<br>`br_tse_eleicoes.candidatos` |
| 429 | `camara_municipal.cadeiras_total` | Cadeiras na Câmara Municipal | valor | `br_tse_eleicoes.resultados_candidato_municipio`<br>`br_tse_eleicoes.candidatos`<br>`br_tse_eleicoes.receitas_candidato` |
| 430 | `camara_municipal.bancadas` | Vereadores eleitos por partido | série/ranking | `br_tse_eleicoes.resultados_candidato_municipio`<br>`br_tse_eleicoes.candidatos`<br>`br_tse_eleicoes.receitas_candidato` |
| 431 | `camara_municipal.perfil_candidatos.candidatos` | Candidaturas a vereador | valor | `br_tse_eleicoes.resultados_candidato_municipio`<br>`br_tse_eleicoes.candidatos`<br>`br_tse_eleicoes.receitas_candidato` |
| 432 | `camara_municipal.perfil_candidatos.feminino` | Candidatas mulheres a vereador | valor | `br_tse_eleicoes.resultados_candidato_municipio`<br>`br_tse_eleicoes.candidatos`<br>`br_tse_eleicoes.receitas_candidato` |
| 433 | `camara_municipal.perfil_candidatos.masculino` | Candidatos homens a vereador | valor | `br_tse_eleicoes.resultados_candidato_municipio`<br>`br_tse_eleicoes.candidatos`<br>`br_tse_eleicoes.receitas_candidato` |
| 434 | `camara_municipal.perfil_candidatos.negros` | Candidaturas pretas ou pardas a vereador | valor | `br_tse_eleicoes.resultados_candidato_municipio`<br>`br_tse_eleicoes.candidatos`<br>`br_tse_eleicoes.receitas_candidato` |
| 435 | `camara_municipal.perfil_candidatos.brancos` | Candidaturas brancas a vereador | valor | `br_tse_eleicoes.resultados_candidato_municipio`<br>`br_tse_eleicoes.candidatos`<br>`br_tse_eleicoes.receitas_candidato` |
| 436 | `camara_municipal.perfil_candidatos.idade_media` | Idade média das candidaturas a vereador | valor | `br_tse_eleicoes.resultados_candidato_municipio`<br>`br_tse_eleicoes.candidatos`<br>`br_tse_eleicoes.receitas_candidato` |
| 437 | `camara_municipal.financiamento` | Receitas das campanhas a vereador por origem | série/ranking | `br_tse_eleicoes.resultados_candidato_municipio`<br>`br_tse_eleicoes.candidatos`<br>`br_tse_eleicoes.receitas_candidato` |
| 438 | `deputados_nascidos.total` | Deputados federais nascidos no município | valor | `br_camara_dados_abertos.deputado` |
| 439 | `deputados_nascidos.deputados` | Nome, partido e legislatura dos deputados nascidos aqui | série/ranking | `br_camara_dados_abertos.deputado` |
| 440 | `filiados.filiados` | Filiados a partidos com registro regular | valor | `br_tse_filiacao_partidaria.microdados` |
| 441 | `filiados.por_partido` | Filiados regulares por partido | série/ranking | `br_tse_filiacao_partidaria.microdados` |
| 442 | `filiados.por_sexo` | Filiados regulares por sexo | série/ranking | `br_tse_filiacao_partidaria.microdados` |
| 443 | `financas_campanha.receitas_por_cargo` | Receitas das campanhas por cargo (prefeito, vereador) | série/ranking | `br_tse_eleicoes.receitas_candidato`<br>`br_tse_eleicoes.despesas_candidato` |
| 444 | `financas_campanha.receitas_por_origem` | Receitas das campanhas por origem (partido, pessoa física…) | série/ranking | `br_tse_eleicoes.receitas_candidato`<br>`br_tse_eleicoes.despesas_candidato` |
| 445 | `financas_campanha.despesas_por_cargo` | Gastos das campanhas por cargo | série/ranking | `br_tse_eleicoes.receitas_candidato`<br>`br_tse_eleicoes.despesas_candidato` |
| 446 | `financas_campanha.despesas_por_tipo` | Gastos das campanhas por tipo de despesa | série/ranking | `br_tse_eleicoes.receitas_candidato`<br>`br_tse_eleicoes.despesas_candidato` |

## Transparência e gestão (31)

| # | Indicador | O que mede | Tipo | Datasets de origem |
|---:|---|---|---|---|
| 447 | `ebt` | Nota da Escala Brasil Transparente (CGU) por edição | série/ranking | `br_clp_ranking_competitividade.nota_geral_municipio`<br>`br_cgu_ebt.municipio` |
| 448 | `clp.pilares` | Notas do Ranking de Competitividade dos Municípios (CLP) por pilar | série/ranking | `br_clp_ranking_competitividade.nota_geral_municipio`<br>`br_cgu_ebt.municipio` |
| 449 | `emendas.janela_autores` | Período considerado no ranking de autores de emendas | valor | `br_cgu_emendas_parlamentares.microdados` |
| 450 | `emendas.serie` | Emendas parlamentares pagas ao município, por ano | série/ranking | `br_cgu_emendas_parlamentares.microdados` |
| 451 | `emendas.top_autores` | Parlamentares que mais destinaram emendas ao município | série/ranking | `br_cgu_emendas_parlamentares.microdados` |
| 452 | `emendas.por_funcao` | Emendas por função de governo | série/ranking | `br_cgu_emendas_parlamentares.microdados` |
| 453 | `compras_federais.licitacoes_no_municipio.serie` | Licitações federais realizadas no município, por ano | série/ranking | `br_cgu_licitacao_contrato.licitacao`<br>`br_cgu_licitacao_contrato.contrato_compra`<br>`br_me_cnpj.estabelecimentos` |
| 454 | `compras_federais.licitacoes_no_municipio.por_orgao` | Licitações federais no município por órgão | série/ranking | `br_cgu_licitacao_contrato.licitacao`<br>`br_cgu_licitacao_contrato.contrato_compra`<br>`br_me_cnpj.estabelecimentos` |
| 455 | `compras_federais.fornecedores_locais.snapshot_cnpj` | Data do cadastro CNPJ usado para achar fornecedores locais | valor | `br_cgu_licitacao_contrato.licitacao`<br>`br_cgu_licitacao_contrato.contrato_compra`<br>`br_me_cnpj.estabelecimentos` |
| 456 | `compras_federais.fornecedores_locais.serie` | Contratos federais com empresas locais, por ano | série/ranking | `br_cgu_licitacao_contrato.licitacao`<br>`br_cgu_licitacao_contrato.contrato_compra`<br>`br_me_cnpj.estabelecimentos` |
| 457 | `compras_federais.fornecedores_locais.top` | Empresas locais que mais venderam ao governo federal | série/ranking | `br_cgu_licitacao_contrato.licitacao`<br>`br_cgu_licitacao_contrato.contrato_compra`<br>`br_me_cnpj.estabelecimentos` |
| 458 | `diarios_oficiais.total_edicoes` | Edições do diário oficial municipal indexadas (Querido Diário) | valor | `br_ok_queridodiario.diarios` |
| 459 | `diarios_oficiais.ultima_edicao` | Data da última edição do diário oficial indexada | valor | `br_ok_queridodiario.diarios` |
| 460 | `diarios_oficiais.serie` | Edições do diário oficial por ano | série/ranking | `br_ok_queridodiario.diarios` |
| 461 | `fiscal.ifgf` | Índice Firjan de Gestão Fiscal e componentes | série/ranking | `br_firjan_ifgf.ranking`<br>`br_tesouro_capag.municipios` |
| 462 | `consumidor.serie` | Reclamações no consumidor.gov.br por ano | série/ranking | `br_mj_consumidorgovbr.reclamacoes` |
| 463 | `consumidor.top_segmentos` | Segmentos com mais reclamações de consumidores | série/ranking | `br_mj_consumidorgovbr.reclamacoes` |
| 464 | `consumidor.top_empresas` | Empresas com mais reclamações de consumidores locais | série/ranking | `br_mj_consumidorgovbr.reclamacoes` |
| 465 | `servidores.adm_direta` | Servidores da administração direta (MUNIC) | valor | `br_ibge_munic.recursos_humanos` |
| 466 | `servidores.adm_indireta` | Servidores da administração indireta | valor | `br_ibge_munic.recursos_humanos` |
| 467 | `servidores.estatutario_adm_direta` | Servidores estatutários | valor | `br_ibge_munic.recursos_humanos` |
| 468 | `servidores.clt_adm_direta` | Servidores celetistas | valor | `br_ibge_munic.recursos_humanos` |
| 469 | `servidores.comissionado_adm_direta` | Servidores só comissionados | valor | `br_ibge_munic.recursos_humanos` |
| 470 | `servidores.estagio_adm_direta` | Estagiários na administração direta | valor | `br_ibge_munic.recursos_humanos` |
| 471 | `servidores.sem_vinculo_permanente_adm_direta` | Servidores sem vínculo permanente | valor | `br_ibge_munic.recursos_humanos` |
| 472 | `cauc.itens` | Requisitos fiscais do CAUC avaliados | valor | `br_tesouro_cauc.situacao_municipios`<br>`br_tesouro_cauc.legenda_itens` |
| 473 | `cauc.regulares` | Requisitos do CAUC comprovados | valor | `br_tesouro_cauc.situacao_municipios`<br>`br_tesouro_cauc.legenda_itens` |
| 474 | `cauc.pendencias` | Pendências no CAUC que travam transferências voluntárias | valor | `br_tesouro_cauc.situacao_municipios`<br>`br_tesouro_cauc.legenda_itens` |
| 475 | `cauc.itens_pendentes` | Quais requisitos do CAUC estão pendentes | série/ranking | `br_tesouro_cauc.situacao_municipios`<br>`br_tesouro_cauc.legenda_itens` |
| 476 | `cauc.lista` | Situação de cada requisito do CAUC | série/ranking | `br_tesouro_cauc.situacao_municipios`<br>`br_tesouro_cauc.legenda_itens` |
| 477 | `fiscalizacao_cgu.sorteios` | Sorteios de fiscalização da CGU em que o município saiu | série/ranking | `br_cgu_fef.municipios_sorteados` |

## Social e cultura (21)

| # | Indicador | O que mede | Tipo | Datasets de origem |
|---:|---|---|---|---|
| 478 | `avs.ivs` | Índice de Vulnerabilidade Social (0–1, menor é melhor) | valor | `br_ipea_avs.municipio`<br>`br_abrinq_oca.municipio_primeira_infancia` |
| 479 | `avs.ivs_infraestrutura_urbana` | IVS — dimensão infraestrutura urbana | valor | `br_ipea_avs.municipio`<br>`br_abrinq_oca.municipio_primeira_infancia` |
| 480 | `avs.ivs_capital_humano` | IVS — dimensão capital humano | valor | `br_ipea_avs.municipio`<br>`br_abrinq_oca.municipio_primeira_infancia` |
| 481 | `avs.ivs_renda_trabalho` | IVS — dimensão renda e trabalho | valor | `br_ipea_avs.municipio`<br>`br_abrinq_oca.municipio_primeira_infancia` |
| 482 | `avs.idhm` | Índice de Desenvolvimento Humano Municipal | valor | `br_ipea_avs.municipio`<br>`br_abrinq_oca.municipio_primeira_infancia` |
| 483 | `avs.idhm_longevidade` | IDHM — longevidade | valor | `br_ipea_avs.municipio`<br>`br_abrinq_oca.municipio_primeira_infancia` |
| 484 | `avs.idhm_educacao` | IDHM — educação | valor | `br_ipea_avs.municipio`<br>`br_abrinq_oca.municipio_primeira_infancia` |
| 485 | `avs.idhm_renda` | IDHM — renda | valor | `br_ipea_avs.municipio`<br>`br_abrinq_oca.municipio_primeira_infancia` |
| 486 | `primeira_infancia.taxa_bruta_pre_escola` | Taxa bruta de matrícula na pré-escola | valor | `br_ipea_avs.municipio`<br>`br_abrinq_oca.municipio_primeira_infancia` |
| 487 | `primeira_infancia.taxa_liquida_pre_escola` | Taxa líquida de matrícula na pré-escola | valor | `br_ipea_avs.municipio`<br>`br_abrinq_oca.municipio_primeira_infancia` |
| 488 | `primeira_infancia.matriculas_pre_escola` | Matrículas na pré-escola | valor | `br_ipea_avs.municipio`<br>`br_abrinq_oca.municipio_primeira_infancia` |
| 489 | `sinpatinhas.animais` | Cães e gatos no cadastro nacional SinPatinhas | valor | `br_mma_sinpatinhas.microdados`<br>`br_ibge_populacao.municipio` |
| 490 | `sinpatinhas.por_especie` | Animais cadastrados por espécie | série/ranking | `br_mma_sinpatinhas.microdados`<br>`br_ibge_populacao.municipio` |
| 491 | `sinpatinhas.por_1000hab.municipio` | Animais cadastrados por mil habitantes no município | valor | `br_mma_sinpatinhas.microdados`<br>`br_ibge_populacao.municipio` |
| 492 | `sinpatinhas.por_1000hab.uf` | Animais cadastrados por mil habitantes na UF | valor | `br_mma_sinpatinhas.microdados`<br>`br_ibge_populacao.municipio` |
| 493 | `sinpatinhas.por_1000hab.brasil` | Animais cadastrados por mil habitantes no Brasil | valor | `br_mma_sinpatinhas.microdados`<br>`br_ibge_populacao.municipio` |
| 494 | `rouanet.entidades` | Entidades com sede no município no SALIC (Lei Rouanet) | valor | `br_minc_salic.entidades` |
| 495 | `rouanet.proponentes` | Proponentes de projetos culturais na Lei Rouanet | valor | `br_minc_salic.entidades` |
| 496 | `rouanet.projetos` | Projetos culturais apresentados por entidades locais | valor | `br_minc_salic.entidades` |
| 497 | `rouanet.valor_projetos` | Valor dos projetos culturais aprovados para captação | valor | `br_minc_salic.entidades` |
| 498 | `rouanet.top_proponentes` | Proponentes locais com maior valor aprovado | série/ranking | `br_minc_salic.entidades` |

## Comércio exterior (6)

| # | Indicador | O que mede | Tipo | Datasets de origem |
|---:|---|---|---|---|
| 499 | `exportacoes.total_fob_usd` | Exportações de empresas do município (US$ FOB) | valor | `br_me_comex_stat` |
| 500 | `exportacoes.top_sh4` | Produtos mais exportados (SH4) | série/ranking | `br_me_comex_stat` |
| 501 | `exportacoes.top_paises` | Principais destinos das exportações | série/ranking | `br_me_comex_stat` |
| 502 | `importacoes.total_fob_usd` | Importações de empresas do município (US$ FOB) | valor | `br_me_comex_stat` |
| 503 | `importacoes.top_sh4` | Produtos mais importados (SH4) | série/ranking | `br_me_comex_stat` |
| 504 | `importacoes.top_paises` | Principais origens das importações | série/ranking | `br_me_comex_stat` |

## Trabalho (17)

| # | Indicador | O que mede | Tipo | Datasets de origem |
|---:|---|---|---|---|
| 505 | `rais.vinculos_ativos_3112` | Empregos formais ativos em 31/12 (RAIS) | valor | `br_me_rais.microdados_vinculos`<br>`br_me_rais.microdados_estabelecimentos` |
| 506 | `rais.vinculos_ativos_ano_anterior` | Empregos formais ativos no ano anterior | valor | `br_me_rais.microdados_vinculos`<br>`br_me_rais.microdados_estabelecimentos` |
| 507 | `rais.remuneracao_media` | Remuneração média dos vínculos formais | valor | `br_me_rais.microdados_vinculos`<br>`br_me_rais.microdados_estabelecimentos` |
| 508 | `rais.estabelecimentos` | Estabelecimentos empregadores na RAIS | valor | `br_me_rais.microdados_vinculos`<br>`br_me_rais.microdados_estabelecimentos` |
| 509 | `caged.admissoes` | Admissões com carteira assinada no ano (CAGED) | valor | `br_me_caged.microdados_movimentacao` |
| 510 | `caged.desligamentos` | Desligamentos de empregos formais no ano | valor | `br_me_caged.microdados_movimentacao` |
| 511 | `caged.saldo` | Saldo de empregos formais (admissões − desligamentos) | valor | `br_me_caged.microdados_movimentacao` |
| 512 | `caged.salario_medio_admissao` | Salário médio de admissão | valor | `br_me_caged.microdados_movimentacao` |
| 513 | `top_empregadores.top` | Maiores empregadores privados por número de vínculos | série/ranking | `br_me_rais_identificada.estabelecimentos`<br>`br_bd_diretorios_brasil.cnae_2`<br>`br_bd_diretorios_brasil.natureza_juridica` |
| 514 | `top_empregadores_publicos.top` | Maiores empregadores públicos por número de vínculos | série/ranking | `br_me_rais_identificada.estabelecimentos`<br>`br_bd_diretorios_brasil.natureza_juridica` |
| 515 | `lista_suja.total` | Empregadores do município na lista suja do trabalho escravo | valor | `br_mte_listasuja.empregadores`<br>`br_bd_diretorios_brasil.cnae_2` |
| 516 | `lista_suja.trabalhadores` | Trabalhadores resgatados nesses empregadores | valor | `br_mte_listasuja.empregadores`<br>`br_bd_diretorios_brasil.cnae_2` |
| 517 | `lista_suja.uf.empregadores` | Empregadores da UF na lista suja | valor | `br_mte_listasuja.empregadores`<br>`br_bd_diretorios_brasil.cnae_2` |
| 518 | `lista_suja.uf.trabalhadores` | Trabalhadores resgatados na UF | valor | `br_mte_listasuja.empregadores`<br>`br_bd_diretorios_brasil.cnae_2` |
| 519 | `lista_suja.brasil.empregadores` | Empregadores no Brasil na lista suja | valor | `br_mte_listasuja.empregadores`<br>`br_bd_diretorios_brasil.cnae_2` |
| 520 | `lista_suja.brasil.trabalhadores` | Trabalhadores resgatados no Brasil | valor | `br_mte_listasuja.empregadores`<br>`br_bd_diretorios_brasil.cnae_2` |
| 521 | `lista_suja.empregadores` | Detalhe de cada empregador local na lista suja | série/ranking | `br_mte_listasuja.empregadores`<br>`br_bd_diretorios_brasil.cnae_2` |

## Agropecuária (17)

| # | Indicador | O que mede | Tipo | Datasets de origem |
|---:|---|---|---|---|
| 522 | `lavouras_top` | Principais lavouras por valor da produção (PAM) | série/ranking | `br_ibge_ppm.efetivo_rebanhos`<br>`br_ibge_ppm.producao_origem_animal` |
| 523 | `rebanhos.efetivos` | Efetivo dos rebanhos por espécie (PPM) | série/ranking | `br_ibge_ppm.efetivo_rebanhos`<br>`br_ibge_ppm.producao_origem_animal` |
| 524 | `origem_animal.produtos` | Produção de origem animal (leite, ovos, mel…) | série/ranking | `br_ibge_ppm.efetivo_rebanhos`<br>`br_ibge_ppm.producao_origem_animal` |
| 525 | `assentamentos.total` | Assentamentos da reforma agrária (INCRA) | valor | `br_incra_acervo.assentamentos`<br>`br_geobr_mapas.municipio` |
| 526 | `assentamentos.familias` | Famílias assentadas | valor | `br_incra_acervo.assentamentos`<br>`br_geobr_mapas.municipio` |
| 527 | `assentamentos.capacidade` | Capacidade de famílias dos assentamentos | valor | `br_incra_acervo.assentamentos`<br>`br_geobr_mapas.municipio` |
| 528 | `assentamentos.area_ha` | Área dos assentamentos (ha) | valor | `br_incra_acervo.assentamentos`<br>`br_geobr_mapas.municipio` |
| 529 | `aquicultura.valor_total` | Valor da produção da aquicultura (mil R$) | valor | `br_ibge_ppm.producao_aquicultura` |
| 530 | `aquicultura.produtos` | Produção da aquicultura por espécie | série/ranking | `br_ibge_ppm.producao_aquicultura` |
| 531 | `extracao_silvicultura.silvicultura.valor_total` | Valor da produção da silvicultura (mil R$) | valor | `br_ibge_pevs.producao_extracao_vegetal · producao_silvicultura` |
| 532 | `extracao_silvicultura.silvicultura.produtos` | Produtos da silvicultura (madeira, lenha…) | série/ranking | `br_ibge_pevs.producao_extracao_vegetal · producao_silvicultura` |
| 533 | `imoveis_rurais.cafir.imoveis` | Imóveis rurais ativos no cadastro da Receita (CAFIR) | valor | `br_rf_cafir.imoveis_rurais`<br>`br_rf_arrecadacao.itr` |
| 534 | `imoveis_rurais.cafir.area_ha` | Área dos imóveis rurais ativos (ha) | valor | `br_rf_cafir.imoveis_rurais`<br>`br_rf_arrecadacao.itr` |
| 535 | `imoveis_rurais.cafir.area_mediana_ha` | Área mediana dos imóveis rurais (ha) | valor | `br_rf_cafir.imoveis_rurais`<br>`br_rf_arrecadacao.itr` |
| 536 | `imoveis_rurais.cafir.imoveis_1000ha_mais` | Imóveis rurais com 1.000 ha ou mais | valor | `br_rf_cafir.imoveis_rurais`<br>`br_rf_arrecadacao.itr` |
| 537 | `imoveis_rurais.cafir.area_1000ha_mais` | Área somada dos imóveis com 1.000 ha ou mais | valor | `br_rf_cafir.imoveis_rurais`<br>`br_rf_arrecadacao.itr` |
| 538 | `imoveis_rurais.itr` | ITR arrecadado por ano | série/ranking | `br_rf_cafir.imoveis_rurais`<br>`br_rf_arrecadacao.itr` |

## Benefícios sociais (55)

| # | Indicador | O que mede | Tipo | Datasets de origem |
|---:|---|---|---|---|
| 539 | `bolsa_familia.familias` | Famílias que receberam Bolsa Família no mês | valor | `br_cgu_beneficios_cidadao.novo_bolsa_familia`<br>`br_cgu_beneficios_cidadao.bpc`<br>`br_cgu_beneficios_cidadao.garantia_safra` |
| 540 | `bolsa_familia.repasse_mensal` | Valor transferido pelo Bolsa Família no mês | valor | `br_cgu_beneficios_cidadao.novo_bolsa_familia`<br>`br_cgu_beneficios_cidadao.bpc`<br>`br_cgu_beneficios_cidadao.garantia_safra` |
| 541 | `bolsa_familia.valor_medio` | Valor médio por família no Bolsa Família | valor | `br_cgu_beneficios_cidadao.novo_bolsa_familia`<br>`br_cgu_beneficios_cidadao.bpc`<br>`br_cgu_beneficios_cidadao.garantia_safra` |
| 542 | `bpc.beneficiarios` | Beneficiários do BPC (idosos e pessoas com deficiência) | valor | `br_cgu_beneficios_cidadao.novo_bolsa_familia`<br>`br_cgu_beneficios_cidadao.bpc`<br>`br_cgu_beneficios_cidadao.garantia_safra` |
| 543 | `bpc.repasse_mensal` | Valor pago pelo BPC no mês | valor | `br_cgu_beneficios_cidadao.novo_bolsa_familia`<br>`br_cgu_beneficios_cidadao.bpc`<br>`br_cgu_beneficios_cidadao.garantia_safra` |
| 544 | `cadastro_unico.pessoas_cadastradas` | Pessoas no Cadastro Único | valor | `br_mc_indicadores.transferencias_municipio`<br>`br_ibge_populacao.municipio` |
| 545 | `cadastro_unico.familias_cadastradas` | Famílias no Cadastro Único | valor | `br_mc_indicadores.transferencias_municipio`<br>`br_ibge_populacao.municipio` |
| 546 | `cadastro_unico.familias_pbf` | Famílias do CadÚnico que recebem Bolsa Família | valor | `br_mc_indicadores.transferencias_municipio`<br>`br_ibge_populacao.municipio` |
| 547 | `cadastro_unico.pct_populacao` | Parcela da população no Cadastro Único | valor | `br_mc_indicadores.transferencias_municipio`<br>`br_ibge_populacao.municipio` |
| 548 | `cadunico_mds.familias.pobreza` | Famílias do CadÚnico em pobreza | valor | `br_mds_cadunico.indicadores_municipio` |
| 549 | `cadunico_mds.familias.baixa_renda` | Famílias do CadÚnico de baixa renda | valor | `br_mds_cadunico.indicadores_municipio` |
| 550 | `cadunico_mds.familias.acima_meio_sm` | Famílias do CadÚnico com renda acima de ½ salário mínimo per capita | valor | `br_mds_cadunico.indicadores_municipio` |
| 551 | `cadunico_mds.familias.total` | Total de famílias no CadÚnico (MDS) | valor | `br_mds_cadunico.indicadores_municipio` |
| 552 | `cadunico_mds.pessoas.pobreza` | Pessoas do CadÚnico em pobreza | valor | `br_mds_cadunico.indicadores_municipio` |
| 553 | `cadunico_mds.pessoas.baixa_renda` | Pessoas do CadÚnico de baixa renda | valor | `br_mds_cadunico.indicadores_municipio` |
| 554 | `cadunico_mds.pessoas.acima_meio_sm` | Pessoas do CadÚnico acima de ½ salário mínimo per capita | valor | `br_mds_cadunico.indicadores_municipio` |
| 555 | `cadunico_mds.pessoas.total` | Total de pessoas no CadÚnico (MDS) | valor | `br_mds_cadunico.indicadores_municipio` |
| 556 | `cadunico_mds.atualizacao.taxa` | Taxa de atualização cadastral do CadÚnico | valor | `br_mds_cadunico.indicadores_municipio` |
| 557 | `cadunico_mds.atualizacao.atualizadas` | Famílias com cadastro atualizado | valor | `br_mds_cadunico.indicadores_municipio` |
| 558 | `cadunico_mds.responsavel_sexo.feminino` | Famílias com responsável mulher | valor | `br_mds_cadunico.indicadores_municipio` |
| 559 | `cadunico_mds.responsavel_sexo.masculino` | Famílias com responsável homem | valor | `br_mds_cadunico.indicadores_municipio` |
| 560 | `cadunico_mds.raca_cor` | Pessoas do CadÚnico por cor ou raça | série/ranking | `br_mds_cadunico.indicadores_municipio` |
| 561 | `cadunico_mds.grupos_especificos.total` | Famílias de grupos tradicionais e específicos | valor | `br_mds_cadunico.indicadores_municipio` |
| 562 | `cadunico_mds.grupos_especificos.lista` | Famílias por grupo específico (quilombola, catador…) | série/ranking | `br_mds_cadunico.indicadores_municipio` |
| 563 | `cadunico_mds.situacao_rua.familias` | Famílias em situação de rua no CadÚnico | valor | `br_mds_cadunico.indicadores_municipio` |
| 564 | `cadunico_mds.situacao_rua.pessoas` | Pessoas em situação de rua no CadÚnico | valor | `br_mds_cadunico.indicadores_municipio` |
| 565 | `cadunico_mds.situacao_rua.pct_atendimento` | Parcela da população de rua atendida pelo Bolsa Família | valor | `br_mds_cadunico.indicadores_municipio` |
| 566 | `cadunico_mds.local.urbano` | Famílias do CadÚnico em área urbana | valor | `br_mds_cadunico.indicadores_municipio` |
| 567 | `cadunico_mds.local.rural` | Famílias do CadÚnico em área rural | valor | `br_mds_cadunico.indicadores_municipio` |
| 568 | `cadunico_mds.esgoto` | Famílias do CadÚnico por forma de esgotamento | série/ranking | `br_mds_cadunico.indicadores_municipio` |
| 569 | `cadunico_mds.saida_pobreza_pbf.saem` | Famílias que saem da pobreza com o Bolsa Família | valor | `br_mds_cadunico.indicadores_municipio` |
| 570 | `cadunico_mds.saida_pobreza_pbf.permanecem` | Famílias que seguem na pobreza mesmo com o benefício | valor | `br_mds_cadunico.indicadores_municipio` |
| 571 | `cadunico_mds.trabalho_infantil.pessoas` | Pessoas com marcação de trabalho infantil no CadÚnico | valor | `br_mds_cadunico.indicadores_municipio` |
| 572 | `cadunico_mds.serie_familias` | Famílias no CadÚnico ao longo do tempo | série/ranking | `br_mds_cadunico.indicadores_municipio` |
| 573 | `inss.beneficios` | Benefícios do INSS pagos a residentes | valor | `br_mps_beneficios.beneficio_mantido_municipio_mes`<br>`br_mps_beneficios.beneficio_concedido_municipio_mes`<br>`br_ibge_populacao.municipio` |
| 574 | `inss.valor_mensal` | Valor mensal pago pelo INSS no município | valor | `br_mps_beneficios.beneficio_mantido_municipio_mes`<br>`br_mps_beneficios.beneficio_concedido_municipio_mes`<br>`br_ibge_populacao.municipio` |
| 575 | `inss.valor_medio` | Valor médio dos benefícios do INSS | valor | `br_mps_beneficios.beneficio_mantido_municipio_mes`<br>`br_mps_beneficios.beneficio_concedido_municipio_mes`<br>`br_ibge_populacao.municipio` |
| 576 | `inss.por_1000hab.municipio` | Benefícios do INSS por mil habitantes no município | valor | `br_mps_beneficios.beneficio_mantido_municipio_mes`<br>`br_mps_beneficios.beneficio_concedido_municipio_mes`<br>`br_ibge_populacao.municipio` |
| 577 | `inss.por_1000hab.uf` | Benefícios do INSS por mil habitantes na UF | valor | `br_mps_beneficios.beneficio_mantido_municipio_mes`<br>`br_mps_beneficios.beneficio_concedido_municipio_mes`<br>`br_ibge_populacao.municipio` |
| 578 | `inss.por_1000hab.brasil` | Benefícios do INSS por mil habitantes no Brasil | valor | `br_mps_beneficios.beneficio_mantido_municipio_mes`<br>`br_mps_beneficios.beneficio_concedido_municipio_mes`<br>`br_ibge_populacao.municipio` |
| 579 | `inss.por_categoria` | Benefícios do INSS por espécie (aposentadoria, pensão…) | série/ranking | `br_mps_beneficios.beneficio_mantido_municipio_mes`<br>`br_mps_beneficios.beneficio_concedido_municipio_mes`<br>`br_ibge_populacao.municipio` |
| 580 | `inss.por_clientela` | Benefícios do INSS urbanos e rurais | série/ranking | `br_mps_beneficios.beneficio_mantido_municipio_mes`<br>`br_mps_beneficios.beneficio_concedido_municipio_mes`<br>`br_ibge_populacao.municipio` |
| 581 | `inss.por_sexo` | Benefícios do INSS por sexo | série/ranking | `br_mps_beneficios.beneficio_mantido_municipio_mes`<br>`br_mps_beneficios.beneficio_concedido_municipio_mes`<br>`br_ibge_populacao.municipio` |
| 582 | `inss.por_faixa_etaria` | Benefícios do INSS por faixa etária | série/ranking | `br_mps_beneficios.beneficio_mantido_municipio_mes`<br>`br_mps_beneficios.beneficio_concedido_municipio_mes`<br>`br_ibge_populacao.municipio` |
| 583 | `inss.serie` | Benefícios do INSS ao longo do tempo | série/ranking | `br_mps_beneficios.beneficio_mantido_municipio_mes`<br>`br_mps_beneficios.beneficio_concedido_municipio_mes`<br>`br_ibge_populacao.municipio` |
| 584 | `inss.concedidos` | Benefícios do INSS concedidos no período | série/ranking | `br_mps_beneficios.beneficio_mantido_municipio_mes`<br>`br_mps_beneficios.beneficio_concedido_municipio_mes`<br>`br_ibge_populacao.municipio` |
| 585 | `programas_cgu.gas_do_povo.pessoas` | Famílias que retiraram o vale Gás do Povo no mês | valor | `br_cgu_gas_do_povo · br_cgu_pe_de_meia · br_cgu_seguro_defeso` |
| 586 | `programas_cgu.gas_do_povo.valor` | Valor dos vales Gás do Povo no mês | valor | `br_cgu_gas_do_povo · br_cgu_pe_de_meia · br_cgu_seguro_defeso` |
| 587 | `programas_cgu.gas_do_povo.serie_12m` | Gás do Povo: famílias e valor nos últimos 12 meses | série/ranking | `br_cgu_gas_do_povo · br_cgu_pe_de_meia · br_cgu_seguro_defeso` |
| 588 | `programas_cgu.pe_de_meia.pessoas` | Estudantes que receberam Pé-de-Meia no mês | valor | `br_cgu_gas_do_povo · br_cgu_pe_de_meia · br_cgu_seguro_defeso` |
| 589 | `programas_cgu.pe_de_meia.valor` | Valor pago pelo Pé-de-Meia no mês | valor | `br_cgu_gas_do_povo · br_cgu_pe_de_meia · br_cgu_seguro_defeso` |
| 590 | `programas_cgu.pe_de_meia.serie_12m` | Pé-de-Meia: estudantes e valor nos últimos 12 meses | série/ranking | `br_cgu_gas_do_povo · br_cgu_pe_de_meia · br_cgu_seguro_defeso` |
| 591 | `programas_cgu.seguro_defeso.pessoas` | Pescadores com Seguro Defeso no mês | valor | `br_cgu_gas_do_povo · br_cgu_pe_de_meia · br_cgu_seguro_defeso` |
| 592 | `programas_cgu.seguro_defeso.valor` | Valor pago pelo Seguro Defeso no mês | valor | `br_cgu_gas_do_povo · br_cgu_pe_de_meia · br_cgu_seguro_defeso` |
| 593 | `programas_cgu.seguro_defeso.serie_12m` | Seguro Defeso: pescadores e valor nos últimos 12 meses | série/ranking | `br_cgu_gas_do_povo · br_cgu_pe_de_meia · br_cgu_seguro_defeso` |

## Vizinhança (1)

| # | Indicador | O que mede | Tipo | Datasets de origem |
|---:|---|---|---|---|
| 594 | `municipios` | Municípios vizinhos com população, PIB e indicadores para comparação | série/ranking | `br_ibge_populacao.municipio`<br>`br_ibge_pib.municipio`<br>`br_bd_vizinhanca.municipio`<br>`br_bd_diretorios_brasil.municipio` |
