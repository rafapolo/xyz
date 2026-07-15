# Sócios Pós-Eleição: Políticos que Entram em Empresas Contratadas Após Ser Eleitos

Políticos eleitos que ingressaram no quadro societário de empresas **depois** da vitória eleitoral — e essas empresas continuaram ou passaram a vencer contratos federais. Padrão de "porta giratória de entrada": a empresa recompensa o acesso político via participação societária após a vitória.

**Fonte**: `br_tse_eleicoes.candidatos` + `resultados_candidato` + `br_me_cnpj.socios` + `br_cgu_licitacao_contrato.licitacao_item`  
**Período de contratos**: 2013–2023  
**Filtro**: `data_entrada_sociedade` posterior ao `ano_eleicao`; total acima de R$1M

---

## Resultados (ordenados por valor total)

| Político | Cargo | Partido | UF | Ano eleição | Data entrada como sócio | Empresa (CNPJ) | Órgão contratante | Primeiro | Último | Itens | Total (R$) |
|---|---|---|---|---|---|---|---|---|---|---|---|
| LUIS CESAR BUENO E FREITAS | Dep. Estadual | PT | GO | 2010 | 2023-07-17 | 33683111000107 | DNIT | 2014 | 2022 | 16 | 438.230.759 |
| LUIS CESAR BUENO E FREITAS | Dep. Estadual | PT | GO | 2010 | 2023-07-17 | 33683111000107 | Ministério Desenvolvimento e Assistência Social | 2013 | 2022 | 14 | 139.526.930 |
| LUIS CESAR BUENO E FREITAS | Dep. Estadual | PT | GO | 2010 | 2023-07-17 | 33683111000107 | Fundo Nac. Segurança e Educação Trânsito | 2014 | 2017 | 2 | 224.844.908 |
| LUIS CESAR BUENO E FREITAS | Dep. Estadual | PT | GO | 2010 | 2023-07-17 | 33683111000107 | Instituto Nac. Colonização e Reforma Agrária | 2014 | 2020 | 23 | 93.050.449 |
| FRANCISCO BELLO GALINDO FILHO | Dep. Estadual | PTB | MT | 2006 | 2022-04-28 | 01865426000170 (UNIDAS CONSTRUTORA LTDA) | DNIT | 2013 | 2018 | 11 | 170.824.189 |
| ALOIZIO MERCADANTE OLIVA | Senador / Dep. Federal | PT | SP | 2002 / 1998 | 2023-03-22 | 33657248000189 | Ministério dos Transportes | 2020 | 2020 | 2 | 142.726.654 |
| ALOIZIO MERCADANTE OLIVA | Senador / Dep. Federal | PT | SP | 2002 | 2023-03-22 | 33657248000189 | Instituto de Pesquisa Econômica Aplicada (IPEA) | 2013 | 2022 | 6 | 113.879.598 |
| ANA JULIA DE VASCONCELOS CAREPA | Governadora | PT | PA | 2006 | 2024-02-16 | 04740876000125 | Empresa de Proc. de Dados da Previdência | 2015 | 2015 | 1 | 104.789.612 |
| FRANCISCO LIMA LEITE | Vereador | PR | PE | 2012 | 2018-09-27 | 08439201000100 | DNIT | 2020 | 2022 | 7 | 96.620.825 |

---

## Casos de destaque

- **Luis Cesar Bueno E Freitas (PT/GO)**: Eleito deputado estadual em 2010, ingressou como sócio da empresa em julho de 2023 — 13 anos após a eleição. A empresa já acumulava centenas de milhões em contratos com DNIT, FNSET e INCRA durante todo esse período. Sugere que a entrada formal no quadro societário foi tardia, mas a relação econômica com o grupo pode ser anterior.

- **Aloizio Mercadante Oliva (PT/SP)**: Ex-ministro (Ciência e Tecnologia, Educação) e senador, ingressou como sócio em março de 2023 — após mais de duas décadas no poder. A empresa tem contratos com Ministério dos Transportes e IPEA que abrangem o período em que Mercadante ocupava cargos no governo federal (2011–2014).

- **Francisco Bello Galindo Filho (PTB/MT)**: Eleito deputado estadual em 2006. Ingressou na UNIDAS CONSTRUTORA LTDA em abril de 2022, empresa que já havia acumulado R$170M em contratos com o DNIT entre 2013 e 2018.

- **Ana Julia de Vasconcelos Carepa (PT/PA)**: Governadora do Pará entre 2007 e 2011. Ingressou como sócia de empresa contratada pela DATAPREV em fevereiro de 2024 — contrato de R$104M firmado em 2015, quando Carepa já estava fora do cargo mas ainda com influência na rede petista.

---

## Metodologia e Limitações

- **Tabelas**: `br_tse_eleicoes.candidatos`, `br_tse_eleicoes.resultados_candidato`, `br_me_cnpj.socios`, `br_cgu_licitacao_contrato.licitacao_item`
- **Critério de entrada pós-eleição**: `data_entrada_sociedade` (Receita Federal) posterior ao `ano_eleicao` (TSE) do primeiro mandato identificado
- **Limitações**:
  1. `data_entrada_sociedade` pode registrar a data de uma alteração contratual, não a entrada efetiva no grupo controlador
  2. A empresa pode ter sido controlada informalmente antes da entrada formal no quadro — a participação societária pode ser a formalização de uma relação preexistente
  3. Não distingue se o político entrou como sócio minoritário simbólico ou controlador
  4. Empresas públicas (DATAPREV, etc.) não foram filtradas — a empresa contratante pode ser pública mesmo que a empresa vencedora seja privada
  5. Resultados duplicados por mesmo CNPJ com múltiplas cargos históricos do político
