# Políticos com Bens Modestos que Pagaram Empresas em Campanha — Mesmas Empresas Ganham Licitações

Políticos eleitos com patrimônio declarado ao TSE abaixo de R$3M que, durante campanhas eleitorais, pagaram acima de R$50k a empresas que também detêm contratos federais milionários. O duplo vínculo (financiamento de campanha + licitação federal) documenta uma relação comercial entre o político e a empresa — mesmo sem registro societário formal.

**Fonte**: `br_tse_eleicoes.bens_candidato` + `candidatos` + `resultados_candidato` + `despesas_candidato` + `br_cgu_licitacao_contrato.licitacao_item`  
**Filtro patrimônio**: bens declarados < R$3M  
**Filtro campanha**: pagamento de campanha >R$50k para o mesmo CNPJ  
**Filtro contratos**: empresa com >R$5M em licitações federais

---

## Resultados (59 casos, top 20 por valor de licitações)

| Político | Partido/UF | Empresa | Bens TSE (R$) | Total Campanha (R$) | Total Licitações (R$) | Ratio |
|---|---|---|---|---|---|---|
| Aloizio Mercadante | PT/SP | SODEXO PASS DO BRASIL | 1.215.113 | 60.925 | 1.548.979.064 | 1.275x |
| Luiz Lindbergh Farias | PT/RJ | SODEXO PASS DO BRASIL | 1.052.374 | 50.003 | 1.548.979.064 | 1.472x |
| Jose Aldo Rebelo | PC do B/SP | SODEXO PASS DO BRASIL | 2.202.933 | 50.729 | 1.548.979.064 | 703x |
| Ana Maria Rosseto | PT/SP | SODEXO PASS DO BRASIL | 2.380.027 | 57.481 | 1.548.979.064 | 651x |
| **Sergio Cabral** | PMDB/RJ | **LIGHT SERVIÇOS DE ELETRICIDADE** | 1.490.970 | **104.395** | **761.498.886** | **511x** |
| Sebastião Almeida | PT/SP | TELEFONICA BRASIL S.A. | 1.080.582 | 52.064 | 626.736.421 | 580x |
| Aloizio Mercadante | PT/SP | TELEFONICA BRASIL S.A. | 1.215.113 | 99.993 | 626.736.421 | 516x |
| Fernando Haddad | PT/SP | TELEFONICA BRASIL S.A. | 1.520.787 | 84.637 | 626.736.421 | 412x |
| Geraldo Alckmin | PSDB/SP | TELEFONICA BRASIL S.A. | 2.787.126 | 64.829 | 626.736.421 | 225x |
| **Rafael Tajra Fonteles** | PT/PI | **PRIME CONSULTORIA E ASSESSORIA** | 1.649.200 | **85.050** | **597.483.977** | **362x** |
| **Sergio Cabral** | PMDB/RJ | **CESAN (ÁGUAS E ESGOTOS)** | 1.490.970 | **69.859** | **273.482.328** | **183x** |
| Cesar Borges | PFL/BA | BANCO BRADESCO S.A. | 2.607.534 | 750.861 | 223.278.628 | 86x |
| Ana Júlia Carepa | PT/PA | TAM LINHAS AEREAS | 1.572.942 | 51.483 | 207.696.576 | 132x |
| Cristovam Buarque | PT/DF | TAM LINHAS AEREAS | 2.340.320 | 66.875 | 207.696.576 | 89x |

---

## Análise dos casos relevantes

### Casos estruturais (baixo valor investigativo individual)
- **Sodexo Pass**: Empresa de vale-refeição/benefícios. Pagamentos de campanha provavelmente cobriram alimentação de voluntários/funcionários. A empresa tem R$1,5B em contratos federais por ser fornecedora de benefícios a servidores — relação não é suspeita individualmente.
- **Telefonica/Vivo**: Empresa de telecomunicações usada para serviços de telefonia durante campanhas. Contratos federais igualmente estruturais.
- **Banco Bradesco**: Pagamentos bancários de campanha. Contratos federais estruturais.
- **TAM Linhas Aéreas**: Passagens para equipe de campanha. Contratos governamentais de transporte aéreo.

### Casos com interesse investigativo adicional

**Sergio Cabral (PMDB/RJ) → LIGHT Serviços de Eletricidade**  
Cabral (ex-governador do RJ, condenado por corrupção) pagou R$104k para a concessionária de energia elétrica do Rio durante campanha. LIGHT tem R$761M em contratos federais (2018–2023). O pagamento de campanha para uma concessionária monopolista de infraestrutura — e não uma empresa de publicidade ou serviços eleitorais — é atípico.

**Sergio Cabral (PMDB/RJ) → CESAN (Companhia Estadual de Águas e Esgotos)**  
Cabral pagou R$69k para a empresa pública de saneamento do ES via campanha. CESAN tem R$273M em contratos federais. Empresa pública recebendo pagamento de campanha de político é juridicamente questionável.

**Rafael Tajra Fonteles (PT/PI) → PRIME CONSULTORIA E ASSESSORIA**  
Fonteles (hoje Ministro da Fazenda) pagou R$85k para a PRIME durante campanha. PRIME acumula R$597M em contratos federais (2018–2023). A PRIME é uma consultoria de Brasília — não uma grande multinacional. O volume de contratos é desproporcional ao porte esperado de uma consultoria típica de campanha eleitoral. Merece investigação.

---

## Metodologia

```sql
WITH eleitos_baixo_pat AS (
  SELECT DISTINCT c.titulo_eleitoral, c.nome, c.cargo, c.sigla_partido, c.sigla_uf,
         MAX(c.ano) AS ultimo_mandato, b.bens_declarados
  FROM basedosdados."br_tse_eleicoes"."candidatos" c
  JOIN basedosdados."br_tse_eleicoes"."resultados_candidato" rc
    ON rc.titulo_eleitoral_candidato = c.titulo_eleitoral AND rc.ano = c.ano
  JOIN (
    SELECT titulo_eleitoral_candidato, SUM(valor_item) AS bens_declarados
    FROM basedosdados."br_tse_eleicoes"."bens_candidato"
    GROUP BY 1 HAVING SUM(valor_item) < 3000000
  ) b ON b.titulo_eleitoral_candidato = c.titulo_eleitoral
  WHERE rc.resultado IN ('eleito','eleito por qp','eleito por media')
  GROUP BY 1,2,3,4,5,7
),
cnpjs_campanha AS (
  SELECT REGEXP_REPLACE(d.cpf_cnpj_fornecedor, '[^0-9]', '', 'g') AS cnpj14, ...
  FROM eleitos_baixo_pat e
  JOIN basedosdados."br_tse_eleicoes"."despesas_candidato" d
    ON d.titulo_eleitoral_candidato = e.titulo_eleitoral
  HAVING SUM(d.valor_despesa) > 50000
)
-- JOIN com licitacao_item (ano filter) + empresas
```

---

## Limitações

1. **Proxy de vínculo**: Pagamento de campanha indica relação comercial documentada, mas não equivale a participação societária (socios). Empresas grandes recebem pagamentos de muitos candidatos sem relação privilegiada.
2. **Duplicatas**: O mesmo político aparece múltiplas vezes por eleição (mesma pessoa em anos/cargos diferentes na tabela TSE).
3. **Sodexo/grandes empresas**: Dominam o resultado por volume — são fornecedores universais tanto de campanhas quanto do governo. Não indicam favorecimento individual.
4. **Período desconexo**: Pagamento de campanha e contratos federais podem ter ocorrido em períodos sem relação — um deputado que pagou à Telefonica em 2014 não influenciou contratos Telefonica de 2023.
