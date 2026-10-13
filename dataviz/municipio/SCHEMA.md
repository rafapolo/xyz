# rodado_indicadores_municipais

Todos os indicadores do painel municipal num único Parquet em formato longo: cada linha é um valor de um indicador de um município. São 12.382.056 linhas, 5.571 municípios e 992 indicadores, gerados em 2026-10-13.

- **Arquivo:** `rodado_indicadores_municipais.parquet` (56 MB, zstd), ordenado por `secao`, `indicador`, `sigla_uf`, `id_municipio`.
- **No db.rodado.xyz e no beelink:** `br_rodado_indicadores_municipais.municipio`.
- **Origem:** os JSONs do painel (`extract_lote.py`), achatados por `gera_llm.py`. O JSON continua sendo a fonte; este arquivo é derivado e se regenera com `python3 gera_llm.py ~/painel_lote/json --saida ~/painel_lote/llm`.

## Colunas

coluna|tipo|o que é
---|---|---
id_municipio|texto|código IBGE de 7 dígitos
nome|texto|nome do município
sigla_uf|texto|UF
secao|texto|tema do painel (demografia, saude, …); `municipio` traz o cadastro (regiao, regiao_saude, area_km2…)
indicador|texto|caminho do dado dentro da seção, com pontos (ex.: pib.serie.pib)
ano|inteiro|ano do dado; vazio quando o bloco não informa
mes|inteiro|mês (1 a 12), só em séries mensais
dimensao|texto|recorte da linha, `chave=valor; chave=valor` (ex.: cor_raca=Parda)
valor|decimal|o número, na unidade da fonte original
texto|texto|valor não numérico (nomes, situações, motivos de ausência)

## Convenções

- Os números estão na unidade da fonte original; o arquivo não tem coluna de unidade.
- `ano` vem da própria linha ou, se ela não tiver, do bloco que a contém (heurística; blocos `ano_anterior` recebem o ano de referência menos um).
- Linhas sem `valor` nem `texto` são itens de lista: o conteúdo está em `dimensao`.
- Ausência de dado aparece como texto em indicadores terminados em `erro` ou `motivo`.

## Exemplo

Ranking de um indicador dentro de uma UF:
```sql
SELECT nome, valor FROM br_rodado_indicadores_municipais.municipio
WHERE secao = 'saude' AND indicador = 'cnes.leitos.sus' AND sigla_uf = 'RJ' ORDER BY valor DESC LIMIT 10;
```

## Indicadores

Por seção, uma linha por bloco: `bloco: folhas [anos] por <chaves de dimensao>`. O indicador é `bloco.folha` (só `folha` quando o bloco é `-`). `*` marca folha de texto. `(N mun.)` aparece quando nem todos têm o dado.


### agropecuaria
- aquicultura: disponivel, motivo*, valor_total [2013-2025] (4267 mun.)
- aquicultura.produtos: quantidade, valor [2013-2025] por produto (4267 mun.)
- assentamentos: area_ha, capacidade, familias, total
- assentamentos.projetos: area_ha, capacidade, familias por codigo, nome, fase, criacao, obtencao (2013 mun.)
- credito_rural: disponivel, motivo* (26 mun.)
- credito_rural.serie: contratos, contratos_pronaf, ultimo_mes, valor, valor_pronaf [2016-2026] (5545 mun.)
- -: erro* (3 mun.)
- extracao_silvicultura.extracao_vegetal.produtos: quantidade, valor [1989-2024] por produto, unidade (5178 mun.)
- extracao_silvicultura.extracao_vegetal: valor_total [1989-2024] (5178 mun.)
- extracao_silvicultura.silvicultura.produtos: quantidade, valor [1991-2024] por produto, unidade (3433 mun.)
- extracao_silvicultura.silvicultura: valor_total [1991-2024] (3433 mun.)
- imoveis_rurais.cafir: area_1000ha_mais, area_ha, area_mediana_ha, data_referencia*, imoveis, imoveis_1000ha_mais (5547 mun.)
- imoveis_rurais.itr: valor [2017-2024] (5570 mun.)
- lavouras_top: area_colhida, quantidade_produzida, valor_producao [1989-2024] por tipo, produto (5556 mun.)
- origem_animal.produtos: quantidade, valor [1984-2025] por produto, unidade (5568 mun.)
- rebanhos.efetivos: quantidade [1990-2025] por tipo_rebanho (5568 mun.)

### beneficios
- bolsa_familia: familias, repasse_mensal, valor_medio [2025] (5570 mun.)
- bpc: beneficiarios, repasse_mensal [2025] (5570 mun.)
- cadastro_unico: erro*, familias_cadastradas, familias_pbf, pct_populacao, pessoas_cadastradas [2020] (5570 mun.)
- cadunico_mds.atualizacao: atualizadas, taxa [2026]
- cadunico_mds.esgoto: familias [2026] por forma
- cadunico_mds.familias: acima_meio_sm, baixa_renda, pobreza, total [2026]
- cadunico_mds.grupos_especificos.lista: familias [2026] por grupo (5504 mun.)
- cadunico_mds.grupos_especificos: total [2026]
- cadunico_mds.local: rural, urbano [2026]
- cadunico_mds.pessoas: acima_meio_sm, baixa_renda, pobreza, total [2026]
- cadunico_mds.raca_cor: pessoas [2026] por raca
- cadunico_mds.responsavel_sexo: feminino, masculino [2026]
- cadunico_mds.saida_pobreza_pbf: permanecem, saem [2026]
- cadunico_mds.serie_familias: familias [2012-2026] por ref
- cadunico_mds.situacao_rua: familias, pct_atendimento, pessoas [2026]
- cadunico_mds.trabalho_infantil: pessoas [2023-2026] (3322 mun.)
- -: erro* (1 mun.)
- garantia_safra: familias, repasse [2013-2026] (1322 mun.)
- inss: beneficios, disponivel, motivo*, valor_medio, valor_mensal [2026] (5569 mun.)
- inss.bpc_por_tipo: idoso, pcd [2026] (5569 mun.)
- inss.concedidos: beneficios, meses, valor [2012-2026] (5569 mun.)
- inss.por_1000hab: ano_populacao, brasil, municipio, uf [2026] (5569 mun.)
- inss.por_categoria: n, valor [2026] por k (5569 mun.)
- inss.por_clientela: n [2026] por k (5569 mun.)
- inss.por_faixa_etaria: n [2026] por k (5569 mun.)
- inss.por_sexo: n [2026] por k (5569 mun.)
- inss.serie: beneficios, valor_mensal [2021-2026] (5569 mun.)
- programas_cgu: erro* (1 mun.)
- programas_cgu.gas_do_povo: pessoas, valor [2026] (4568 mun.)
- programas_cgu.gas_do_povo.serie_12m: pessoas, valor [2025-2026] (4568 mun.)
- programas_cgu.pe_de_meia: pessoas, valor [2026] (4567 mun.)
- programas_cgu.pe_de_meia.serie_12m: pessoas, valor [2025-2026] (4567 mun.)
- programas_cgu.seguro_defeso: pessoas, valor [2013-2026] (3092 mun.)
- programas_cgu.seguro_defeso.serie_12m: pessoas, valor [2013-2026] (3092 mun.)

### comercio_exterior
- exportacoes: ano_anterior_fob_usd*, top_paises*, top_sh4*, total_fob_usd* [1997-2025] por pais_iso3, valor_fob_usd, id_sh4 (2933 mun.)
- importacoes: ano_anterior_fob_usd*, top_paises*, top_sh4*, total_fob_usd* [1997-2025] por pais_iso3, valor_fob_usd, id_sh4 (2735 mun.)

### conectividade
- banda_larga: densidade_100hab, densidade_brasil [2025] (5570 mun.)
- -: erro* (1 mun.)
- ibc: cobertura_pop_4g5g, fibra*, ibc, media_brasil [2024] (5570 mun.)

### demografia
- censo_2022: area_km2, domicilios, idade_mediana, indice_envelhecimento, populacao, razao_sexo, taxa_alfabetizacao (5570 mun.)
- censo_extra: alfabetizacao_por_raca*, cor_raca* [2010-2022] por cor_raca (1648 mun.)
- censo_extra.alfabetizacao_por_raca: alfabetizadas, taxa, total por cor_raca (5570 mun.)
- censo_extra.cor_raca: populacao [2010-2022] por cor_raca (5570 mun.)
- censo_extra.religiao: grupos*, total_10_anos_ou_mais por religiao (5570 mun.)
- censo_extra.religiao.grupos: pct, populacao por religiao (5570 mun.)
- nomes.top: pessoas por nome (5565 mun.)
- piramide_etaria_2022: homens, mulheres por grupos
- populacao_serie: populacao [1991-2025] (5570 mun.)

### economia
- bancario: agencias, depositos_totais, erro*, operacoes_credito [1988-2023] (4168 mun.)
- bancario.verbetes: credito*, depositos* [1988-2023] por i (4168 mun.)
- bndes.administracao_publica: desembolsado, valor [1995-2026] por ente, programa, projeto, situacao (1653 mun.)
- bndes.nao_automaticas: desembolsado, valor por contratacao, cliente, projeto, produto, situacao (1141 mun.)
- bndes.porte_5a: desembolsado, operacoes por porte (4622 mun.)
- bndes.serie_indiretas: desembolsado, operacoes [2002-2026] (5456 mun.)
- bndes: setor_5a* por setor (274 mun.)
- bndes.setor_5a: desembolsado por setor (4563 mun.)
- combustiveis: erro*, janela_dias (5155 mun.)
- combustiveis.produtos: postos, preco_brasil, preco_municipio, preco_uf por produto, ultima_coleta (416 mun.)
- financas_publicas.despesas_funcao: valor [2022-2025] por funcao (5569 mun.)
- financas_publicas: despesas_total_empenhado, erro* [2022-2025] (5569 mun.)
- financas_publicas.receitas: fpm, fundeb, icms, impostos, iptu, iss, receitas_capital, receitas_correntes, sus, total [2022-2025] (5569 mun.)
- inpc_brasil: variacao_anual, variacao_doze_meses, variacao_mensal [2026]
- mineracao_cfem: disponivel, motivo*, valor_ano [2003-2026] (3967 mun.)
- mineracao_cfem.serie: pagadores, valor [2002-2026] (3967 mun.)
- mineracao_cfem.substancias: valor [2003-2026] por substancia (3967 mun.)
- pib: erro* (1 mun.)
- pib.pib_per_capita: brasil, uf, valor [2023] (5570 mun.)
- pib.ranking_uf: posicao, total [2023] (5570 mun.)
- pib.serie: impostos_liquidos, pib, va, va_adespss, va_agropecuaria, va_industria, va_servicos [2012-2023] (5570 mun.)
- pix: pagadores_pf, pagadores_pf_por_hab, pagadores_pj, transacoes_pagas, transacoes_recebidas, valor_pago, valor_recebido [2026]
- pix.serie: pago, recebido [2023-2026]

### educacao
- alfabetizacao: disponivel, media_municipios_uf, motivo*, taxa [2023-2024] (5547 mun.)
- alfabetizacao.metas: meta_alfabetizacao_2024, meta_alfabetizacao_2025, meta_alfabetizacao_2026, meta_alfabetizacao_2027, meta_alfabetizacao_2028, meta_alfabetizacao_2029, meta_alfabetizacao_2030, nivel_alfabetizacao, percentual_participacao, taxa_alfabetizacao [2023-2024] por id_municipio, rede (5352 mun.)
- alfabetizacao.serie: taxa_alfabetizacao [2023-2024] (5547 mun.)
- censo_escolar: com_biblioteca, com_esgoto_rede, com_internet, com_laboratorio, com_quadra, com_rampa_acessibilidade, docentes, escolas, escolas_rurais, matriculas, matriculas_eja, matriculas_especial, matriculas_fundamental, matriculas_infantil, matriculas_medio, matriculas_transporte, turmas [2025]
- censo_escolar.por_rede: docentes, escolas, matriculas [2025] por rede
- censo_escolar.serie: escolas, matriculas [2016-2025]
- cnpq: disponivel, motivo* (4954 mun.)
- cnpq.por_instituicao: processos [2004-2022] por instituicao (617 mun.)
- cnpq.por_modalidade: processos [2004-2022] por modalidade (617 mun.)
- cnpq.serie: processos, valor [2002-2022] (617 mun.)
- conectada: adequadas, com_internet, disponivel, download_mediano, escolas, internet_aprendizagem, laboratorio, medidas, motivo* [2023] (5570 mun.)
- conectada.por_faixa: escolas [2023] por faixa (5570 mun.)
- enem: humanas, inscritos, linguagens, matematica, media_geral, natureza, presentes, redacao [2023]
- especial: disponivel, motivo* (1 mun.)
- especial.por_classe: matriculas [2024] por classe (5570 mun.)
- especial.por_tipo: matriculas [2024] por tipo (5570 mun.)
- ideb.finais: ideb, meta, taxa_aprovacao [2005-2025] (5569 mun.)
- ideb.iniciais: ideb, meta, taxa_aprovacao [2005-2025] (5568 mun.)
- ideb.referencia_brasil: finais, iniciais
- ideb.referencia_uf: finais, iniciais
- indicadores: erro* (1 mun.)
- inse: alunos, disponivel, inse, media_municipios_br, media_municipios_uf, motivo* [2019-2021] (5569 mun.)
- inse.niveis_pct: nivel, pct [2019-2021] (5569 mun.)
- saeb: erro* (1 mun.)
- saeb.provas: distribuicao_niveis_pct, media [2021-2023] por disciplina, serie, i (5562 mun.)
- sisu: erro* (4 mun.)
- sisu.serie: aprovados, candidatos, matriculados, nota_media [2017-2022] (5567 mun.)
- sisu.top_cursos: matriculados [2018-2022] por curso, ies (4846 mun.)
- sisu.vagas_no_municipio: ampla, cotas, total [2021-2022] (551 mun.)
- superior: concluintes, cursos, cursos_presenciais, disponivel, ies, ingressantes, matriculas, matriculas_ead, matriculas_presenciais, motivo*, vagas [2009-2024] (3826 mun.)
- superior.por_area: matriculas [2009-2024] por area (3826 mun.)
- superior.por_rede: matriculas [2009-2024] por rede (3826 mun.)
- superior.serie_matriculas: matriculas [2009-2024] (3826 mun.)

### empresas
- -: ativas, baixadas, erro*, filiais, idade_media_anos, matrizes, mei, registradas [2026] (5570 mun.)
- demografia_empresarial: aberturas, baixas, saldo [2016-2026] (5570 mun.)
- por_secao_cnae: ativas [2026] por secao (5570 mun.)
- top_atividades: ativas [2026] por atividade (5570 mun.)

### geografia
- arranjo_populacional: nome*, populacao_2010 (953 mun.)
- biomas: pct_area por nome (5570 mun.)
- regiao_metropolitana: nome*, tipo* (1384 mun.)
- sede_municipal: lat, lon [2010] (5565 mun.)
- -: semiarido
- unidades_conservacao: lista*, total por unidade_conservacao, categoria, esfera, organizacao_orgao, ano_criacao
- unidades_conservacao.por_categoria: quantidade por categoria, esfera (1922 mun.)

### infraestrutura
- atlas_esgotos: ano_referencia, erro*, indice_atendimento_com_coleta_com_tratamento, indice_atendimento_com_coleta_sem_tratamento, indice_atendimento_solucao_individual, indice_sem_atendimento_sem_coleta_sem_tratamento, investimento_coleta, investimento_coleta_tratatamento, investimento_tratamento, populacao_urbana_2013, populacao_urbana_2035, prestador_servico_esgotamento_sanitario* (5570 mun.)
- censo_domicilios.agua.categorias: pct, populacao por categoria (5570 mun.)
- censo_domicilios.agua: total (5570 mun.)
- censo_domicilios: domicilios_recenseados* por especie (2631 mun.)
- censo_domicilios.domicilios_recenseados: domicilios por especie (5570 mun.)
- censo_domicilios.esgotamento.categorias: pct, populacao por categoria (5570 mun.)
- censo_domicilios.esgotamento: total (5570 mun.)
- censo_domicilios.lixo.categorias: pct, populacao por categoria (5570 mun.)
- censo_domicilios.lixo: total (5570 mun.)
- censo_domicilios.tipo_domicilio.categorias: pct, populacao por categoria (5570 mun.)
- censo_domicilios.tipo_domicilio: total (5570 mun.)
- energia_continuidade: conjuntos*, erro* por nome, agente (3714 mun.)
- energia_continuidade.serie: dec_horas, fec_vezes, limite_dec, limite_fec, unidades [2014-2025] (1838 mun.)
- energia_gd: data_base*, erro*, instalacoes, potencia_mw, ucs_recebem_credito, w_por_habitante (5567 mun.)
- energia_gd.por_ano_cadastro: instalacoes, kw [1900-2026] (5567 mun.)
- energia_gd.por_classe: instalacoes, kw por classe (5567 mun.)
- energia_gd.por_fonte: instalacoes, kw por fonte (5567 mun.)
- frota.por_tipo: quantidade [2026] por tipo
- frota.serie: total [2013-2026]
- frota: total [2026]
- frota.veiculos_1000hab: ano_populacao, brasil, municipio, uf [2026]
- obras_cno: data_extracao*, disponivel, motivo*, obras (5568 mun.)
- obras_cno.iniciadas_por_ano: area_m2, obras [2016-2025] (5564 mun.)
- obras_cno.por_situacao: obras por situacao (5568 mun.)
- outorgas_agua: disponivel, maiores*, motivo*, outorgas, vazao_total por responsavel (4796 mun.)
- outorgas_agua.maiores: vazao por responsavel (4610 mun.)
- outorgas_agua.por_esfera: outorgas, vazao por esfera (4796 mun.)
- snis.ano_anterior: a, c, t [2007-2021] (5353 mun.)
- snis: despesa_total_servico, erro*, extensao_rede_agua, extensao_rede_esgoto, indice_atendimento_esgoto_esgoto, indice_atendimento_total_agua, indice_atendimento_urbano_agua, indice_coleta_esgoto, indice_perda_distribuicao_agua, indice_tratamento_esgoto, populacao_atendida_agua, populacao_atentida_esgoto, volume_agua_consumido, volume_esgoto_coletado, volume_esgoto_tratado [2000-2022] (5542 mun.)

### meio_ambiente
- car: area_ha, data_extracao*, disponivel, imoveis, motivo*, pendentes, suspensos (5564 mun.)
- car.camadas_ha: app, area_consolidada, reserva_legal, uso_restrito, vegetacao_nativa (5561 mun.)
- car.por_condicao: imoveis por condicao (5563 mun.)
- car.por_tipo: area_ha, imoveis por tipo (5563 mun.)
- desastres: data_extracao*, municipios_uf_com_reconhecimento, vigentes* por desastre, situacao, ocorrencia, vigencia
- estacoes_inmet: estacoes* por id_estacao, estacao, fundacao (1 mun.)
- estacoes_inmet.estacoes: altitude por id_estacao, estacao, fundacao (607 mun.)
- ibama: autos_total, embargos, embargos_5a, valor_total
- ibama.serie: autos, valor [1981-2026] (5462 mun.)
- ibama.tipos_10a: autos por tipo (4296 mun.)
- mapbiomas: anos por i
- mapbiomas.transicoes: area_2010, area_2020 por de, para (5566 mun.)
- prodes.biomas: area_total, desmatado, vegetacao_natural [2022-2023] por bioma (5570 mun.)
- prodes: erro* (1 mun.)
- prodes.serie: area_total, desmatado, vegetacao_natural [2000-2023] por bioma (5570 mun.)
- queimadas.serie: focos, frp_max, frp_medio [2003-2026] (5568 mun.)
- seeg: erro*, gas*, tipo*, total_tco2e [2024] (5570 mun.)
- seeg.por_setor: emissao_tco2e [2024] por setor (5570 mun.)
- sisam.serie: co_ppb, pm25_ugm3 [2000-2019] (5570 mun.)

### municipio
- -: amazonia_legal, area_km2, capital_uf, ddd*, id_comarca*, id_municipio*, id_municipio_bcb*, id_municipio_rf*, id_municipio_tse*, mesorregiao*, microrregiao*, nome*, nome_uf*, regiao*, regiao_imediata*, regiao_intermediaria*, regiao_metropolitana*, regiao_saude*, sigla_uf*

### politica
- -: ano_prefeito, erro* [2026] (5570 mun.)
- camara_municipal.bancadas: cadeiras, votos [2020-2024] por partido (5568 mun.)
- camara_municipal: cadeiras_total, erro* [2020-2026] (5568 mun.)
- camara_municipal.financiamento: candidatos, receita [2020-2024] por cargo (5568 mun.)
- camara_municipal.perfil_candidatos: brancos, candidatos, feminino, idade_media, masculino, negros [2020-2024] (5568 mun.)
- deputados_nascidos: deputados*, total [2026] por nome, nascimento, falecido
- eleitorado: aptos, biometria, zonas [2026] (5570 mun.)
- filiados: data_extracao*, disponivel, filiados, motivo* [2026] (5570 mun.)
- filiados.por_partido: filiados [2026] por partido (5570 mun.)
- filiados.por_sexo: filiados [2026] por sexo (5570 mun.)
- financas_campanha.despesas_por_cargo: valor [2024-2026] por cargo (5569 mun.)
- financas_campanha.despesas_por_tipo: valor [2024-2026] (5569 mun.)
- financas_campanha: disponivel, motivo* [2026] (2 mun.)
- financas_campanha.receitas_por_cargo: candidatos, valor [2024-2026] por cargo (5569 mun.)
- financas_campanha.receitas_por_origem: valor [2024-2026] por origem (5569 mun.)
- genero: 0, 2, 4 [2026] (5570 mun.)
- instrucao: 0, 1, 2, 3, 4, 5, 6, 7, 8 [2026] (5570 mun.)
- prefeito: abstencoes, aptos, comparecimento, secoes, turno, votos_brancos, votos_nominais, votos_nulos [2024] (5568 mun.)
- prefeito.eleito: nome_urna*, partido*, turno, votos [2024] (5518 mun.)

### saude
- atencao_basica: cobertura_ab, cobertura_esf, disponivel, equipes, motivo*, referencia* (5570 mun.)
- atencao_basica.serie: cobertura_ab, cobertura_esf, equipes [2007-2020] (5570 mun.)
- cnes.agentes: ace, acs [2024-2025] (5570 mun.)
- cnes.equipes.por_tipo: n [2026] por tipo (5569 mun.)
- cnes.equipes: total [2026] (5570 mun.)
- cnes: erro*, estabelecimentos [2025] (5570 mun.)
- cnes.leitos: sus, total [2005-2026] (4040 mun.)
- cnes.profissionais: vinculos [2024-2025] (5570 mun.)
- cnes.unidades: caps, samu, ubs, upa [2025] (5570 mun.)
- dengue.classificacao_bruta: 10|1, 10|2, 10|3, 10|4, 10|9, 10|None, 11|1, 11|2, 11|3, 11|4, 11|9, 11|None, 12|1, 12|2, 12|3, 12|4, 12|9, 12|None, 5 |1, 5 |None, 5|1, 8 |1, 8 |2, 8 |3, 8 |4, 8 |9, 8 |None, None|1, None|3, None|4, None|9, None|None [2005-2026] (4150 mun.)
- dengue: confirmados, erro*, graves, notificados, notificados_ano_anterior, obitos [2005-2026] (5566 mun.)
- farmacia_popular: estabelecimentos_credenciados
- ieps: ano_max, erro* (5570 mun.)
- ieps.ano_por_indicador: cobertura_atencao_basica, cobertura_esf, cobertura_plano_privado, despesa_saude_per_capita, enfermeiros_1000hab, leitos_sus_100k, leitos_uti_sus_100k, medicos_1000hab, pct_prenatal_adequado, pct_prenatal_zero, pct_receita_propria_saude, taxa_internacao_csap_100k, taxa_mortalidade_evitavel_100k (5570 mun.)
- ieps.indicadores: cobertura_atencao_basica, cobertura_esf, cobertura_plano_privado, despesa_saude_per_capita, enfermeiros_1000hab, leitos_sus_100k, leitos_uti_sus_100k, medicos_1000hab, pct_prenatal_adequado, pct_prenatal_zero, pct_receita_propria_saude, taxa_internacao_csap_100k, taxa_mortalidade_evitavel_100k (5570 mun.)
- imunizacao: erro* (1 mun.)
- imunizacao.serie: cobertura_bcg, cobertura_hepatite_b, cobertura_penta, cobertura_poliomielite, cobertura_total, cobertura_triplice_viral_d1 [2010-2021] (5570 mun.)
- internacoes.ano_anterior: internacoes, valor_total [2021-2023] (5570 mun.)
- internacoes: diarias_uti, erro*, internacoes, no_municipio, obitos_hospitalares, pct_no_municipio, permanencia_media, taxa_mortalidade_hospitalar, urgencia, valor_medio_aih, valor_total [2022-2024] (5570 mun.)
- internacoes.por_capitulo: internacoes, valor [2022-2024] por capitulo (5570 mun.)
- internacoes.serie: internacoes, valor [2013-2024] (5570 mun.)
- mortalidade: agressoes, causas_externas, erro*, homens, idade_media_obito, mal_definidas, maternas, mulheres, obitos, obitos_infantis, obitos_neonatais, populacao_referencia, suicidios, taxa_mortalidade_1000hab, transporte [2025] (5570 mun.)
- mortalidade.ano_parcial: ate_mes, infantis, obitos [2026] (5559 mun.)
- mortalidade.infantil: nascidos_vivos, neonatais, obitos, taxa_1000nv [2022] (5570 mun.)
- mortalidade.por_capitulo: obitos [2025] por capitulo (5570 mun.)
- mortalidade.serie: infantis, obitos [2014-2025] (5570 mun.)
- mortalidade.top_causas: obitos [2025] por cid, descricao (5570 mun.)
- nascidos_vivos: erro*, nascidos_vivos, pct_baixo_peso, pct_cesareo [2022] (5570 mun.)
- nascidos_vivos.pre_natal_distribuicao: 1, 2, 3, 4, 9, None [2022] (5570 mun.)
- planos_privados: beneficiarios_total, cobertura_pct, erro*, medico_hospitalar, odontologico [2025] (5570 mun.)
- planos_privados.por_contratacao: beneficiarios [2025] por tipo (5570 mun.)
- sisvan: criancas_acompanhadas, erro* [2023] (5570 mun.)

### seguranca
- fbsp: disponivel, motivo*, proporcao_mortes_intenvencao_policial_x_mortes_violentas_intencionais, quantidade_estupro, quantidade_feminicidio, quantidade_furto_veiculos, quantidade_homicidio_doloso, quantidade_latrocinio, quantidade_lesao_corporal_dolosa_violencia_domestica, quantidade_lesao_corporal_morte, quantidade_mortes_intervencao_policial, quantidade_mortes_policiais_confronto, quantidade_mortes_violentas_intencionais, quantidade_porte_ilegal_arma_de_fogo, quantidade_posse_ilegal_arma_de_fogo, quantidade_posse_ilegal_porte_ilegal_arma_de_fogo, quantidade_posse_uso_entorpecente, quantidade_roubo_furto_veiculos, quantidade_roubo_veiculos, quantidade_trafico_entorpecente [2021] (5544 mun.)
- isp_rj: disponivel, homicidio_doloso_ano_anterior, motivo* [2025] (5479 mun.)
- isp_rj.mensal: homicidio_doloso, letalidade_violenta [2025] (92 mun.)
- isp_rj.ocorrencias: cvli, estupro, homicidio_doloso, intervencao_policial, latrocinio, lesao_corporal_morte, letalidade_violenta, roubo_veiculo, tentativa_homicidio [2025] (92 mun.)
- isp_rj.taxas_100k: taxa_estupro, taxa_homicidio_doloso, taxa_homicidio_intervencao_policial, taxa_latrocinio, taxa_lesao_corporal_morte, taxa_letalidade_violenta, taxa_tentativa_homicidio [2020] (38 mun.)
- isp_rj.taxas_100k_uf: taxa_estupro, taxa_homicidio_doloso, taxa_homicidio_intervencao_policial, taxa_latrocinio, taxa_lesao_corporal_morte, taxa_letalidade_violenta, taxa_roubo_veiculo, taxa_tentativa_homicidio [2020] (92 mun.)
- prf: acidentes, ate, desde, disponivel, feridos_graves, mortos, motivo*
- prf.por_ano: acidentes, feridos, feridos_graves, mortos [2021-2026] (2143 mun.)
- prf.por_causa: n por k (2143 mun.)
- prf.por_rodovia: n por k (2143 mun.)
- prf.por_tipo: n por k (2143 mun.)
- sinesp.ano_parcial: ate_mes [2026] (5570 mun.)
- sinesp.ano_parcial.por_tipo.feminicidio: meses, vitimas, vitimas_feminino [2026] (5570 mun.)
- sinesp.ano_parcial.por_tipo.homicidio_doloso: meses, vitimas, vitimas_feminino [2026] (5570 mun.)
- sinesp.ano_parcial.por_tipo.latrocinio: meses, vitimas, vitimas_feminino [2026] (5570 mun.)
- sinesp.ano_parcial.por_tipo.lesao_corporal_seguida_de_morte: meses, vitimas, vitimas_feminino [2026] (5570 mun.)
- sinesp.ano_parcial.por_tipo.mandado_de_prisao_cumprido: meses, ocorrencias [2026] (5570 mun.)
- sinesp.ano_parcial.por_tipo.morte_a_esclarecer: meses, vitimas, vitimas_feminino [2026] (4359 mun.)
- sinesp.ano_parcial.por_tipo.morte_no_transito_exceto_homicidio_doloso: meses, vitimas, vitimas_feminino [2026] (5570 mun.)
- sinesp.ano_parcial.por_tipo.suicidio: meses, vitimas, vitimas_feminino [2026] (5570 mun.)
- sinesp.ano_parcial.por_tipo.tentativa_de_feminicidio: meses, vitimas, vitimas_feminino [2026] (5570 mun.)
- sinesp.ano_parcial.por_tipo.tentativa_de_homicidio: meses, vitimas, vitimas_feminino [2026] (5570 mun.)
- sinesp: disponivel, motivo* (1 mun.)
- sinesp.por_tipo.feminicidio: meses, vitimas, vitimas_feminino [2025] (5570 mun.)
- sinesp.por_tipo.homicidio_doloso: meses, vitimas, vitimas_feminino [2025] (5570 mun.)
- sinesp.por_tipo.latrocinio: meses, vitimas, vitimas_feminino [2025] (5570 mun.)
- sinesp.por_tipo.lesao_corporal_seguida_de_morte: meses, vitimas, vitimas_feminino [2025] (5570 mun.)
- sinesp.por_tipo.mandado_de_prisao_cumprido: meses, ocorrencias [2025] (5570 mun.)
- sinesp.por_tipo.morte_a_esclarecer: meses, vitimas, vitimas_feminino [2025] (4421 mun.)
- sinesp.por_tipo.morte_no_transito_exceto_homicidio_doloso: meses, vitimas, vitimas_feminino [2025] (5570 mun.)
- sinesp.por_tipo.suicidio: meses, vitimas, vitimas_feminino [2025] (5570 mun.)
- sinesp.por_tipo.tentativa_de_feminicidio: meses, vitimas, vitimas_feminino [2025] (5570 mun.)
- sinesp.por_tipo.tentativa_de_homicidio: meses, vitimas, vitimas_feminino [2025] (5570 mun.)
- sinesp.serie: homicidio_doloso, meses [2015-2026] (5570 mun.)
- sinesp.taxa_homicidio_doloso_100k: ano_populacao, brasil, municipio, uf [2025] (5570 mun.)
- sisdepen: capacidade, competencia*, disponivel, faixa_etaria*, lista*, motivo*, mulheres, populacao, provisorios, raca_cor*, taxa_ocupacao, unidades por k, nome (4407 mun.)
- sisdepen.faixa_etaria: n por k (1101 mun.)
- sisdepen.lista: capacidade por nome (1164 mun.)
- sisdepen.por_regime: n por k (1164 mun.)
- sisdepen.raca_cor: n por k (1102 mun.)
- sisdepen.serie: populacao por periodo (1164 mun.)
- violencia_sinan: arma_fogo, autoprovocadas, brancos, erro*, feminino, financeira, fisica, infantil_trabalho, masculino, negligencia, negros, nota_raca*, notificacoes, pct_feminino, pct_negros, psicologica, raca_ignorada, sexual, tortura, trafico_humano [2020-2025] (5569 mun.)
- violencia_sinan.por_ciclo_vida: n [2020-2025] por ciclo (5569 mun.)
- violencia_sinan.por_local: n [2020-2025] por local (5569 mun.)
- violencia_sinan.serie: autoprovocadas, notificacoes [2011-2025] (5569 mun.)

### social
- avs: idhm, idhm_educacao, idhm_longevidade, idhm_renda, ivs, ivs_capital_humano, ivs_infraestrutura_urbana, ivs_renda_trabalho [2010] (5565 mun.)
- primeira_infancia: matriculas_pre_escola, taxa_bruta_pre_escola, taxa_liquida_pre_escola [2019] (5570 mun.)
- rouanet: disponivel, entidades, motivo*, projetos, proponentes, valor_projetos (4417 mun.)
- rouanet.top_proponentes: projetos, valor por nome (4311 mun.)
- sinpatinhas: animais, disponivel, motivo* (5397 mun.)
- sinpatinhas.periodo: ate*, de* (5397 mun.)
- sinpatinhas.por_1000hab: ano_populacao, brasil, municipio, uf (5397 mun.)
- sinpatinhas.por_especie: n por k (5397 mun.)

### trabalho
- caged: admissoes, desligamentos, erro*, salario_medio_admissao, saldo [2020-2025] (5562 mun.)
- lista_suja.brasil: empregadores, trabalhadores
- lista_suja: data_coleta*, total, trabalhadores
- lista_suja.empregadores: ano_acao_fiscal, trabalhadores por empregador, documento, atividade, local, inclusao (325 mun.)
- lista_suja.uf: empregadores, trabalhadores
- rais: estabelecimentos, remuneracao_media, vinculos_ativos_3112, vinculos_ativos_ano_anterior [2025]
- top_empregadores: erro* (1 mun.)
- top_empregadores.top: vinculos_ativos [2021] por empresa, setor, natureza (5564 mun.)
- top_empregadores_publicos: erro* (1 mun.)
- top_empregadores_publicos.top: vinculos_ativos [2021] por empresa, natureza (5556 mun.)

### transparencia
- cauc: data_pesquisa*, disponivel, itens, itens_pendentes*, lista*, motivo*, pendencias, regulares por item, descricao, situacao (5569 mun.)
- clp.pilares: colocacao, nota_geral [2022] por pilar_dimensao (415 mun.)
- compras_federais.fornecedores_locais.serie: contratos, valor [2013-2026] (2932 mun.)
- compras_federais.fornecedores_locais: snapshot_cnpj* (5570 mun.)
- compras_federais.fornecedores_locais.top: contratos, valor por empresa (2932 mun.)
- compras_federais.licitacoes_no_municipio.por_orgao: licitacoes, valor por orgao (609 mun.)
- compras_federais.licitacoes_no_municipio.serie: licitacoes, valor [2013-2023] (609 mun.)
- consumidor: erro* (8 mun.)
- consumidor.serie: nota_media, pct_respondida, reclamacoes [2014-2025] (5563 mun.)
- consumidor.top_empresas: reclamacoes [2016-2025] por empresa (5563 mun.)
- consumidor.top_segmentos: reclamacoes [2016-2025] por segmento (5563 mun.)
- diarios_oficiais: erro*, total_edicoes, ultima_edicao* (5047 mun.)
- diarios_oficiais.serie: edicoes, extras [2023-2026] (524 mun.)
- ebt: nota, ranking [2020-2021] (665 mun.)
- emendas: erro*, janela_autores* [2014-2025] (5418 mun.)
- emendas.por_funcao: pago [2014-2025] por funcao (3694 mun.)
- emendas.serie: emendas, empenhado, pago [2014-2025] (5418 mun.)
- emendas.top_autores: emendas, pago [2014-2025] por autor (5418 mun.)
- fiscal.ifgf: indice, ranking_estadual, ranking_nacional [2013-2022] (5566 mun.)
- fiscalizacao_cgu: sorteios por i (1949 mun.)
- servidores: adm_direta, adm_indireta, clt_adm_direta, comissionado_adm_direta, erro*, estagio_adm_direta, estatutario_adm_direta, sem_vinculo_permanente_adm_direta [2020-2023] (5570 mun.)

### vizinhanca
- -: erro* (1 mun.)
- municipios: pib_per_capita, populacao por id_municipio, nome, sigla_uf (5568 mun.)
- referencia: pib_ano, pib_per_capita, populacao, populacao_ano (5570 mun.)
