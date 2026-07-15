# Microempresas no Simples Nacional com Contratos Federais Bilionários

Empresas cadastradas no Simples Nacional — regime tributário destinado a micro e pequenas empresas com faturamento anual de até R$4,8M (ME) ou R$78M (EPP) — que acumularam volumes bilionários em contratos federais. A Lei 123/2006 concede às empresas do Simples preferência em licitações com itens até R$80k, além de benefícios fiscais. A permanência no regime enquanto se faturam bilhões em contratos públicos configura potencial irregularidade fiscal e vantagem indevida em licitações.

**Fonte**: `br_me_cnpj.simples` + `br_me_cnpj.empresas` + `br_cgu_licitacao_contrato.licitacao_item`  
**Período**: 2018–2023  
**Filtro**: `opcao_simples = 1`; total de contratos acima de R$10M

---

## Resultados (ordenados por volume de contratos)

| Empresa | CNPJ | Data opção Simples | Contratos (R$) | Itens | Período |
|---|---|---|---|---|---|
| F L SOARES PECAS | 21550006000102 | 2026-01-01¹ | 7.347.650.310 | 2.655 | 2018–2020 |
| R MORAES AGENCIA DE TURISMO LTDA | 06955770000174 | 2017-01-01 | 7.317.008.541 | 2.436 | 2018–2023 |
| G4 SERVICO E COMERCIO DE PRODUTOS INDUSTRIAIS, AUTOMOTIVOS E AGRICOLAS LTDA | 13754000000129 | 2026-01-01¹ | 6.919.638.437 | 66.195 | 2018–2023 |
| MIRANDA TURISMO E REPRESENTACOES LTDA | 24929614000110 | 2013-01-01 | 6.890.385.804 | 1.260 | 2018–2023 |
| SUPER ESTAGIOS LTDA | 11320576000152 | 2026-01-01¹ | 6.136.905.151 | 4.635 | 2018–2023 |
| SCOTT SERVICOS, COMERCIO E DISTRIBUICAO LTDA | 13378981000157 | 2019-01-01 | 5.944.420.459 | 15.435 | 2019–2023 |
| IDEIAS TURISMO LTDA | 02676310000156 | 2007-07-01 | 5.106.702.125 | 2.240 | 2018–2023 |
| IMPERIOGN COMERCIO DE MAQUINAS EQUIPAMENTOS E SERVICOS LTDA | 37912700000162 | 2020-07-30 | 4.259.395.793 | 2.240 | 2020–2023 |
| TRICAT PECAS PARA TRATORES LTDA | 13611894000106 | 2013-01-01 | 3.994.659.837 | 6.840 | 2018–2021 |
| PECAZERO COMERCIO E SERVICOS DE VEICULOS LTDA | 13699398000148 | 2011-05-23 | 3.990.933.080 | 12.215 | 2018–2023 |
| ALIMENTARES SERVICOS DE TRANSPORTES E COMERCIAL LTDA | 07523398000190 | 2026-01-01¹ | 3.881.786.397 | 13.125 | 2018–2023 |
| MAX ROYAL COMERCIO E SERVICOS LTDA | 05056594000176 | 2025-01-01¹ | 3.849.578.302 | 27.990 | 2018–2023 |
| BRASIL & BRASIL LTDA | 08530790000129 | 2007-07-01 | 3.723.888.846 | 20.340 | 2018–2023 |
| CITEL COMERCIO E INDUSTRIA TEXTIL LTDA | 07527821000120 | 2025-01-01¹ | 3.689.685.265 | 585 | 2018–2023 |
| FLAVIO MACEDO & CIA LTDA | 15456283000158 | 2012-05-02 | 3.534.547.833 | 34.560 | 2018–2022 |
| REAL CENTER MATERIAIS DE CONSTRUCAO LTDA | 15658667000153 | 2017-01-01 | 3.330.245.477 | 38.070 | 2018–2023 |
| SHOWCASE PRO TECNOLOGIA LTDA | 05411789000197 | 2024-01-01¹ | 3.268.766.237 | 3.510 | 2021–2022 |
| DELTA COMERCIAL E SERVICOS LTDA | 34263393000148 | 2019-07-19 | 3.265.242.663 | 3.116 | 2022–2023 |
| MECANICA NOVA WGD LTDA | 07582357000174 | 2007-07-01 | 3.261.432.344 | 46.665 | 2018–2023 |
| APOLO AGENCIA DE VIAGENS E TURISMO LTDA | 26423228000188 | 2007-07-01 | 3.209.067.746 | 1.755 | 2018–2023 |
| TORRES E NOIA LTDA | 23111763000105 | 2024-01-01¹ | 3.181.276.226 | 528 | 2021–2022 |
| EQUILIBRIO COMERCIO DE PRODUTOS FARMACEUTICOS EIRELI | 05215461000103 | 2025-01-01¹ | 3.151.837.574 | 130 | 2018–2023 |

> ¹ Data de opção no futuro (2024–2026): provavelmente artefato de dados na tabela `br_me_cnpj.simples` — pode representar renovação automática ou data de atualização do cadastro, não necessariamente indicando que a empresa estava no Simples durante todo o período de contratos.

---

## Padrões e alertas

- **Agências de turismo com bilhões**: R Moraes, Miranda Turismo, Ideias Turismo, Apolo Agência somam mais de R$22B em contratos. Agências de viagens do governo federal contratam passagens e hospedagem para servidores via SISG/SIASG — volumes grandes são possíveis, mas o porte de Simples Nacional para agências com esse faturamento é incompatível com o regime.

- **G4 SERVICO E COMERCIO (66.195 itens)**: O maior número de itens da lista, somando R$6.9B com 66 mil itens individuais entre 2018–2023 em peças industriais, automotivos e agrícolas. Escala incompatível com microempresa.

- **FLAVIO MACEDO & CIA LTDA (34.560 itens)**: Já aparece no relatório de fracionamento de contratos com Comando da Marinha. Aqui confirma o perfil: empresa no Simples Nacional com R$3.5B acumulados e dezenas de milhares de itens.

- **REAL CENTER MATERIAIS DE CONSTRUCAO (38.070 itens)**: Também aparece no relatório de fracionamento (Comando do Exército). R$3.3B acumulados com 38 mil itens de construção.

---

## Metodologia e Limitações

- **Tabelas**: `br_me_cnpj.simples` (campo `opcao_simples`), `br_me_cnpj.empresas`, `br_cgu_licitacao_contrato.licitacao_item`
- **Join key**: `cnpj_basico` (8 dígitos base do CNPJ)
- **Período**: 2018–2023 para contratos (anos com dados mais completos)
- **Limitações críticas**:
  1. `data_opcao_simples` com valores no futuro (2024–2026) indica problemas de qualidade na tabela — não se pode confirmar que as empresas estavam no Simples durante o período de contratação
  2. Agências de turismo e gerenciadoras de estágio podem ter volumes legítimos elevados por natureza do serviço (passagens aéreas, pagamentos de bolsas)
  3. O `cnpj_basico` (8 dígitos) pode ter colisões — um mesmo basico pode corresponder a múltiplos CNPJs completos (matriz + filiais) com somas acumuladas
  4. Não foi verificado se a empresa estava efetivamente no Simples Nacional na data de cada contrato — apenas se está inscrita atualmente
