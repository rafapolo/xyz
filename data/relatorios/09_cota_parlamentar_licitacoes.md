# Cota Parlamentar para Empresas que Também Ganham Licitações Federais

Deputados federais que usaram a Cota para Exercício da Atividade Parlamentar (CEAP) para pagar empresas que, simultaneamente, venciam contratos federais milionários. O fluxo duplo — cota parlamentar de um lado, licitação federal do outro — documenta uma relação comercial ativa entre o parlamentar e a empresa contratada pelo Executivo.

**Fonte**: `br_camara_dados_abertos.despesa` + `br_me_cnpj.empresas` + `br_cgu_licitacao_contrato.licitacao_item`  
**Período cota**: 2019–2023  
**Filtro**: CNPJ recebendo >R$80k em cota parlamentar E >R$1M em contratos federais no mesmo período

---

## Resultados (13 empresas com duplo fluxo cota + licitação)

| Empresa | CNPJ | Parlamentar Principal | Partido/UF | Categoria Cota | Total Cota (R$) | Total Licitações (R$) |
|---|---|---|---|---|---|---|
| TAM LINHAS AEREAS S/A. | 02012862000160 | Átila Lins | PSD/AM | PASSAGEM AÉREA | 643.962 | 207.696.576 |
| GOL LINHAS AEREAS S.A. | 07575651000159 | Celso Russomanno | REPUBLICANOS/SP | PASSAGEM AÉREA | 362.330 | 138.856.699 |
| AZUL LINHAS AEREAS BRASILEIRAS S.A. | 09296295000160 | Reginaldo Lopes | PT/MG | PASSAGEM AÉREA | 454.415 | 103.782.523 |
| AMAZONAVES TAXI AEREO LTDA | 03090756000167 | Átila Lins | PSD/AM | LOC. DE AERONAVES | 367.650 | 67.145.856 |
| CTA - CLEITON TAXI AEREO LTDA | 04984400000130 | Sidney Leite | PSD/AM | LOC. DE AERONAVES | 1.008.425 | 31.023.870 |
| ATLANTICO TRANSPORTES LTDA | 08380889000191 | Arthur Oliveira Maia | UNIÃO/BA | LOC. DE VEÍCULOS | 633.856 | 18.216.579 |
| NORAUTO RENT A CAR LTDA | 83368837000115 | Paulo Bengtson | PTB/PA | LOC. DE VEÍCULOS | 429.570 | 8.877.570 |
| HORIZONTE 16 LOCADORA DE VEICULOS LTDA | 21921129000102 | Otoni De Paula | MDB/RJ | LOC. DE VEÍCULOS | 384.000 | 6.553.453 |
| PANTANAL-VEICULOS LTDA | 07319323000191 | Alex Santana | REPUBLICANOS/BA | LOC. DE VEÍCULOS | 799.208 | 5.842.322 |
| PARVI LOCADORA S.A | 08228146000109 | Pedro Campos | PSB/PE | LOC. DE VEÍCULOS | 389.944 | 3.466.122 |
| PONTUAL LOC CAR LTDA | 12305622000107 | Lincoln Portela | PL/MG | LOC. DE VEÍCULOS | 812.770 | 3.423.624 |
| INFORGRAF LTDA | 22056515000146 | Gilberto Abramo | REPUBLICANOS/MG | DIVULGAÇÃO PARL. | 475.936 | 2.131.982 |
| BRASAO VIGILANCIA E SEGURANCA LTDA | 19923146000137 | Flávio Nogueira | PT/PI | SEGURANÇA ESPECIAL | 661.247 | 1.470.527 |

---

## Casos de destaque

### Casos estruturais (baixo valor investigativo)
**Companhias aéreas (TAM, GOL, AZUL) e táxis aéreos (AMAZONAVES, CTA CLEITON)**: O sobreposição é esperada — parlamentares usam aviação comercial via CEAP e o governo compra passagens aéreas e serviços de táxi aéreo para deslocamento de servidores. Deputados do Amazonas (Átila Lins, Sidney Leite) com altos valores em táxi aéreo refletem a necessidade estrutural de aviação em um estado sem rodovias inter-municipais.

**Locadoras de veículos**: Seis empresas (ATLANTICO, NORAUTO, HORIZONTE, PANTANAL, PARVI, PONTUAL) com contratos de locação. A PANTANAL-VEICULOS é usada por 8 deputados de partidos e estados diferentes, o que indica uma empresa de abrangência regional ou nacional — o overlap é estrutural, não indica favorecimento particular.

### Casos com interesse investigativo adicional

**BRASÃO VIGILÂNCIA E SEGURANÇA LTDA** | Flávio Nogueira (PT/PI)  
R$661.247 em CEAP (categoria: "SERVIÇO DE SEGURANÇA PRESTADO POR EMPRESA ESPECIAL") + R$1.470.527 em contratos federais (2019–2020). A relação é dupla: um deputado contratando segurança particular via verba pública, sendo que a mesma empresa que cuida da sua segurança também vende contratos ao governo federal no mesmo período. Requer verificação: o mesmo CNPJ estava ativo em ambos os estados (PI + federal)?

**INFORGRAF LTDA** | Gilberto Abramo (REPUBLICANOS/MG)  
R$475.936 em CEAP (categoria: "DIVULGAÇÃO DA ATIVIDADE PARLAMENTAR") + R$2.131.982 em contratos federais (2022–2023). Empresa de serviços gráficos/publicidade serve tanto a comunicação parlamentar quanto contratos de impressão governamentais. A concentração (um único deputado sendo o maior usuário via CEAP) sugere relação comercial privilegiada.

---

## Metodologia

**Passo 1** — Agregar gastos de cota por CNPJ e parlamentar (2019–2023), filtrar CNPJs com >R$80k:
```sql
SELECT REGEXP_REPLACE(cnpj_cpf_fornecedor, '[^0-9]', '', 'g') AS cnpj14,
       nome_parlamentar, sigla_uf, sigla_partido, fornecedor, categoria_despesa,
       ROUND(SUM(valor_liquido)) AS total_cota
FROM basedosdados."br_camara_dados_abertos"."despesa"
WHERE ano_competencia >= 2019
  AND LENGTH(REGEXP_REPLACE(cnpj_cpf_fornecedor, '[^0-9]', '', 'g')) = 14
GROUP BY 1,2,3,4,5,6 HAVING SUM(valor_liquido) > 80000
```

**Passo 2** — Filtrar quais desses CNPJs também venceram licitações federais:
```sql
SELECT li.cpf_cnpj_vencedor AS cnpj14, em.razao_social,
       ROUND(SUM(li.valor_item)) AS total_licitacoes
FROM basedosdados."br_cgu_licitacao_contrato"."licitacao_item" li
JOIN basedosdados."br_me_cnpj"."empresas" em ...
WHERE li.cpf_cnpj_vencedor IN ('<lista_cnpjs_passo1>')
  AND li.ano BETWEEN 2019 AND 2023
  AND li.valor_item BETWEEN 10001 AND 500000000
GROUP BY 1,2 HAVING SUM(li.valor_item) > 1000000
```

---

## Limitações

1. A CEAP não financia contratos diretamente — é um indicador de relação comercial, não de irregularidade
2. Empresas de setores de transporte e segurança naturalmente atendem parlamentares (CEAP) e governo (licitações) por natureza do setor — falsos positivos estruturais
3. O "parlamentar principal" na tabela é o que mais gastou com aquele CNPJ via CEAP — outros deputados também usaram as mesmas empresas (ex: PANTANAL-VEICULOS: 8 deputados)
4. Período de cota e período de contratos sobrepostos (2019–2023) — é possível que um deputado tenha deixado o cargo antes de os contratos serem firmados, ou vice-versa
