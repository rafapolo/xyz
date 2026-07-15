# Candidatos Derrotados com Empresas Vencedoras de Licitações Federais

Políticos que perderam suas últimas eleições mas cujas empresas — das quais são ou foram sócios — continuaram vencendo contratos federais. A influência política não requer vitória eleitoral: contatos, cargos anteriores e redes de relacionamento sustentam o fluxo de contratos mesmo após a derrota nas urnas.

**Fonte**: `br_tse_eleicoes.candidatos` + `resultados_candidato` + `br_me_cnpj.socios` + `br_cgu_licitacao_contrato.licitacao_item`  
**Período de contratos**: 2013–2023  
**Filtro**: `valor_item` entre R$10.001 e R$500M; CNPJ vencedor válido (14 dígitos); total acima de R$5M por empresa/órgão

---

## Resultados (ordenados por valor total)

| Político | Cargo | Partido | UF | Último pleito | Empresa (CNPJ) | Órgão contratante | Primeiro | Último | Itens | Total (R$) |
|---|---|---|---|---|---|---|---|---|---|---|
| CARLOS MARTINS MARQUES DE SANTANA | Dep. Federal | PT | BA | 2018 | 34164319000506 | Polícia Federal | 2015 | 2022 | 10 | 614.458.947 |
| CARLOS RONALDO VIEIRA FERNANDES | Vereador | PT | RS | 2008 | CEEE-D – 08467115000100 | Univ. Federal do Rio Grande do Sul | 2013 | 2023 | 11 | 603.023.883 |
| EDUARDO MARAFON SILVA / LINDOLFO LUIZ SILVA JUNIOR | Vereador / Dep. Estadual | PSDB / PTC | PR | 2008 / 2010 | 77964393000188 | Ministério da Saúde | 2015 | 2022 | 8 | 557.777.596 |
| JOSE CARLOS OLIVEIRA | Vereador | DEM | SP | 2008 | 42422253000101 | Fundo de Amparo ao Trabalhador | 2016 | 2018 | 13 | 518.824.236 |
| SANDOVAL PEDRO DE ANDRADE | Dep. Estadual | PRP | RO | 2010 | 05659781000144 | DNIT | 2013 | 2023 | 21 | 514.578.157 |
| URBANO DO VALE COELHO | Dep. Federal | PDT | RJ | 2010 | 60444437000146 | Univ. Federal do Rio de Janeiro | 2013 | 2021 | 13 | 447.889.692 |
| LUIS CESAR BUENO E FREITAS | Dep. Estadual | PT | GO | 2022 | 33683111000107 | DNIT | 2014 | 2022 | 16 | 438.230.759 |
| JOSE PEDRO DE AMENGOL FILHO | Dep. Federal | PT | MA | 2022 | 34028316000707 | DNIT | 2014 | 2020 | 7 | 436.210.753 |
| MARIA DO CARMO LARA PERPETUO | Dep. Estadual / Prefeita | PT | MG | 2018 | 34028316000707 | Instituto Nac. Estudos e Pesquisas Educacionais | 2013 | 2022 | 8 | 411.927.608 |

---

## Padrões identificados

- **Sandoval Pedro De Andrade (DNIT/RO)**: Ex-deputado estadual por Rondônia, último pleito em 2010. A empresa com CNPJ 05659781000144 continuou a vencer contratos com o DNIT até 2023 — 13 anos após o último mandato.
- **Luis Cesar Bueno (DNIT/GO)**: Candidatou-se em 2022 e perdeu. Sua empresa acumulou R$438M no DNIT incluindo contratos no ano eleitoral e nos anteriores — a derrota não interrompeu o fluxo.
- **CNPJ 34028316000707 com dois políticos**: Jose Pedro (PT/MA) e Maria Do Carmo (PT/MG) aparecem como sócios da mesma empresa, que acumulou contratos com DNIT e INEP. A empresa beneficiou sócios em dois estados diferentes.
- **Carlos Ronaldo Vieira Fernandes / CEEE-D**: Já aparecia no relatório de parlamentares eleitos (vereador eleito em 2000). Aqui aparece porque também candidatou-se em 2008 e perdeu. A CEEE-D (empresa pública gaúcha) tem contratos com UFRGS que persistem independentemente da trajetória eleitoral.

---

## Metodologia e Limitações

- **Tabelas**: `br_tse_eleicoes.candidatos`, `br_tse_eleicoes.resultados_candidato`, `br_me_cnpj.socios`, `br_cgu_licitacao_contrato.licitacao_item`
- **Definição de "derrotado"**: candidatos cujo resultado em `resultados_candidato` não inclui "eleito", "eleito por qp" ou "eleito por media" — filtrando pelo último pleito registrado por CPF.
- **Limitações**:
  1. O mesmo político pode ter sido eleito anteriormente e perdido depois — "derrotado" aqui significa que o último resultado registrado foi derrota, não que nunca foi eleito
  2. A sociedade na empresa pode ter sido encerrada antes dos contratos — o quadro societário da Receita Federal é histórico, não tem data de saída explícita
  3. Mesmos falsos positivos do relatório original se aplicam: nomes homônimos com CPF de 6 dígitos coincidindo
  4. Empresas públicas estaduais (CEEE-D) não foram excluídas neste filtro
