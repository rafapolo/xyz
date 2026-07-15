# Empresas Estreantes em Contratos Federais com Contratos Milionários no 1º Ano

CNPJs sem histórico de contratação federal anterior a 2020 que surgiram em 2021 com volumes acima de R$80M. Empresa sem historial que debuta com contratos de centenas de milhões sugere criação instrumental — edital direcionado, empresa de prateleira ativada, ou consórcio montado para capturar uma licitação específica.

**Fonte**: `br_cgu_licitacao_contrato.licitacao_item` + `br_me_cnpj.empresas`  
**Período de referência**: 2018–2021 (sem registros 2018–2019; primeiro registro em 2021)  
**Filtro**: ≥R$80M em contratos no ano de estreia

---

## Resultados (95 estreantes em 2021, top 20 por valor)

| Empresa | CNPJ Básico | Porte | Capital Social (R$) | Total Contratos 2021 (R$) |
|---|---|---|---|---|
| ON-HIGHWAY BRASIL LTDA. | 36519422 | Grande | 2.139.329.212 | 562.361.000 |
| **NOVA SB COMUNICACAO S.A.** | 57118929 | Grande | **1.040.461** | **532.437.500** |
| VAN OORD SERVICOS DE OPERACOES MARITIMAS | 30276927 | Grande | 381.029.642 | 387.980.000 |
| CELLTRION HEALTHCARE DISTRIBUICAO | 05452889 | Grande | 14.692.902 | 282.397.885 |
| PTC FARMACEUTICA DO BRASIL LTDA. | 25210463 | Grande | 6.617.558 | 246.691.190 |
| **CONSORCIO R.E.S. CENTRO DE PESQUISAS** | 43679576 | Grande | **0** | **206.966.877** |
| TAMASA ENGENHARIA SA | 18823724 | Grande | 70.100.000 | 206.440.934 |
| MULTILAB IND. E COMERCIO DE PROD. FARMAC | 92265552 | Grande | 190.238.099 | 177.603.990 |
| **NSA DISTRIBUIDORA DE MEDICAMENTOS LTDA** | 34729047 | Grande | **99.800** | **133.559.652** |
| FORTALEZA SERVICOS EMPRESARIAIS LTDA | 38054508 | Média | 1.500.000 | 133.057.431 |
| CONSTRUMASTER CONSTRUCOES E LOCACAO | 12463759 | Grande | 10.000.000 | 124.810.266 |
| COESA CONSTRUCAO E MONTAGENS *(RJ)* | 18738697 | Grande | 301.104.784 | 118.825.577 |
| SOBRADO CONSTRUCAO LTDA | 01419308 | Grande | 15.010.000 | 118.491.001 |
| AMBIPAR FLYONE SERVICO AEREO ESPECIALIZADO | 03945337 | Grande | 15.000.000 | 117.262.541 |
| PPSA - PRÉ-SAL PETRÓLEO S.A. | 18738727 | Grande | 93.333.141 | 104.061.893 |
| TAKEDA DISTRIBUIDORA LTDA. | 11635171 | Grande | 139.718.369 | 103.845.000 |
| HOSPITAL ANCHIETA S.A | 02560878 | Grande | 451.290.539 | 100.600.000 |
| ECO SUL BRASIL CONSTRUTORA LTDA | 05939484 | Grande | 11.000.000 | 88.631.967 |
| BARRETO SERVICOS DE PERFURACAO DE POCO | 09068173 | Grande | 10.000.000 | 86.981.864 |
| IMPERIOGN COMERCIO DE MAQUINAS *(ME)* | 37912700 | Micro | 355.000 | 85.817.409 |

---

## Casos de destaque

### Anomalias de capital vs. contratos

**NOVA SB COMUNICAÇÃO S.A.** — R$1M de capital social, R$532M em contratos federais no ano de estreia.  
A Nova SB é uma empresa de comunicação que surgiu no radar federal em 2021 com meio bilhão em contratos. Capital irrisório para o volume contratado. Merece investigação sobre o objeto dos contratos e o processo licitatório.

**NSA DISTRIBUIDORA DE MEDICAMENTOS LTDA** — R$99.8k de capital social, R$133M em contratos federais no ano de estreia.  
Uma distribuidora de medicamentos com capital de R$100k vencendo contratos de R$133M em 2021. Muito provavelmente relacionado com as compras emergenciais de COVID-19, mas o desbalanço capital/contrato é extremo.

**CONSÓRCIO R.E.S. CENTRO DE PESQUISAS** — R$0 de capital social (consórcio), R$206M em contratos.  
Consórcios não têm capital social próprio — a capacidade econômica está nas empresas consorciadas. Mas a ausência de qualquer histórico antes de 2021 + R$206M no ano de estreia levanta questões sobre habilitação técnica e econômica.

**IMPERIOGN COMERCIO DE MAQUINAS** (`37912700`) — porte MICRO, R$85M em contratos.  
Microempresa faturando R$85M em contratos federais em seu ano de estreia. Empresas de pequeno porte têm preferência em licitações, mas o volume é desproporcional ao porte declarado.

### Contexto COVID (casos com explicação estrutural)

**CELLTRION HEALTHCARE, PTC FARMACÊUTICA, MULTILAB, TAKEDA**: Empresas farmacêuticas/distribuidoras que provavelmente forneceram medicamentos, vacinas ou insumos durante a pandemia. O governo federal fez compras emergenciais volumosas em 2020-2021 — o debut abrupto de fornecedores no setor farmacêutico neste período tem contexto explicativo.

**COESA CONSTRUÇÃO (Em Recuperação Judicial)**: Empresa em recuperação judicial recebendo R$118M em contratos federais. A legislação proíbe contratação com empresas em RJ em algumas modalidades — requer verificação da modalidade licitatória.

---

## Metodologia (abordagem de dois passos)

A ausência de `data_inicio_atividade` consultável via DuckDB (tabela `estabelecimentos` de 130GB = timeout) levou ao uso de **"estreia nos registros de licitação federal"** como proxy de empresa nova.

**Passo 1** — CNPJs com grandes contratos em 2021 que não existiam em 2018-2019:
```sql
-- Passo 1a: CNPJs com >R$3M em 2021
SELECT LEFT(cpf_cnpj_vencedor, 8) AS cnpj8, SUM(valor_item) AS total_2021
FROM basedosdados."br_cgu_licitacao_contrato"."licitacao_item"
WHERE ano = 2021 AND LENGTH(cpf_cnpj_vencedor) = 14
  AND valor_item BETWEEN 10001 AND 500000000
GROUP BY 1 HAVING SUM(valor_item) > 3000000

-- Passo 1b: quais desses aparecem também em 2018-2019?
SELECT DISTINCT LEFT(cpf_cnpj_vencedor, 8) AS cnpj8
FROM basedosdados."br_cgu_licitacao_contrato"."licitacao_item"
WHERE ano IN (2018, 2019) AND LEFT(cpf_cnpj_vencedor, 8) IN (<lista_passo1a>)

-- Estreantes = passo1a MINUS passo1b
```

---

## Limitações

1. **"Estreante no federal" ≠ "empresa nova"**: Uma empresa fundada em 2005 que nunca contratou com o governo federal aparece como "estreante" aqui. O filtro detecta _novos entrantes no mercado federal_, não empresas recém-criadas
2. **Janela de 2 anos (2018-2019)**: Empresas sem contratos federais antes de 2018 mas com longa história estadual/municipal não são detectadas como veteranas
3. **COVID distorce 2021**: Compras emergenciais da pandemia trouxeram novos fornecedores legítimos — nem todo estreante de 2021 é suspeito
4. **Granularidade**: Sem o descritivo dos contratos (apenas valor total), não é possível confirmar o objeto da licitação automaticamente
