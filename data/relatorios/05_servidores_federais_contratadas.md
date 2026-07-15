# Servidores Federais Sócios de Empresas Contratadas pelo Próprio Órgão

Servidores públicos federais ativos que figuram como sócios em empresas que venceram licitações no mesmo órgão onde estão lotados. Conflito de interesse direto: o servidor participa de processos que influenciam a contratação da empresa na qual tem participação econômica. A Lei 12.813/2013 proíbe explicitamente que agentes públicos pratiquem ato que conflite com seus interesses privados.

**Fonte**: `br_cgu_servidores_executivo_federal.cadastro_servidores` + `br_me_cnpj.socios` + `br_cgu_licitacao_contrato.licitacao_item`  
**Referência de servidores**: dez/2022 (dados mais recentes disponíveis)  
**Período de contratos**: 2018–2023

---

## Metodologia de busca

```sql
-- Nota: join com socios (20GB, sem partição) = timeout frequente
-- Abordagem de dois passos: filtrar servidores por órgão primeiro, depois cruzar socios
WITH servidores AS (
  SELECT DISTINCT nome, cpf, descricao_cargo, org_lotacao, orgsup_lotacao
  FROM basedosdados."br_cgu_servidores_executivo_federal"."cadastro_servidores"
  WHERE ano = 2022 AND mes = 12
    AND nome IS NOT NULL AND cpf IS NOT NULL
),
socios_servidores AS (
  SELECT DISTINCT s.cnpj_basico, sv.nome, sv.descricao_cargo, sv.org_lotacao, sv.orgsup_lotacao
  FROM servidores sv
  JOIN basedosdados."br_me_cnpj"."socios" s
    ON SUBSTR(s.documento, 4, 6) = SUBSTR(sv.cpf, 4, 6)
    AND UPPER(s.nome) = UPPER(sv.nome)
    AND s.tipo = 'PF'
)
SELECT ss.nome, ss.descricao_cargo, ss.org_lotacao,
       li.cpf_cnpj_vencedor, e.razao_social, li.nome_orgao,
       MIN(li.ano) AS primeiro_contrato, MAX(li.ano) AS ultimo_contrato,
       COUNT(*) AS qtd_itens, ROUND(SUM(li.valor_item)) AS total
FROM socios_servidores ss
JOIN basedosdados."br_cgu_licitacao_contrato"."licitacao_item" li
  ON LEFT(li.cpf_cnpj_vencedor, 8) = ss.cnpj_basico
  AND li.ano BETWEEN 2018 AND 2023
  AND UPPER(li.nome_orgao) LIKE '%' || UPPER(SPLIT_PART(ss.orgsup_lotacao, ' ', 1)) || '%'
JOIN basedosdados."br_me_cnpj"."empresas" e
  ON e.cnpj_basico = ss.cnpj_basico AND e.ano = 2023 AND e.mes = 9
WHERE li.valor_item BETWEEN 10001 AND 500000000
GROUP BY 1,2,3,4,5,6
HAVING SUM(li.valor_item) > 1000000
ORDER BY total DESC
```

> **Status**: Pendente — join com `socios` (20GB, sem partição) timeout no DuckDB. Aguardar janela de menor carga.

---

## Resultados

*Dados pendentes — executar query acima via `https://db.xn--2dk.xyz/query`.*

---

## Contexto investigativo

A CGU publica anualmente a lista de servidores ativos do Poder Executivo Federal com nome, CPF parcial, cargo e órgão de lotação. O cruzamento com o quadro societário da Receita Federal permite identificar casos em que o servidor é sócio de empresa que vende para o próprio órgão — padrão que raramente aparece em investigações sistemáticas de dados abertos.

Casos típicos documentados em processos disciplinares da CGU:
- Analista de licitações que é sócio de empresa fornecedora do órgão
- Gestor de contratos com participação em empresa prestadora de serviços ao mesmo ministério
- Chefe de seção de compras com familiares sócios de fornecedores (variante: nomes idênticos por parentesco)

---

## Limitações

1. CPF do servidor no cadastro CGU tem mascaramento parcial (***XXXXXX**) — a dedução é a mesma do cruzamento com TSE: 6 dígitos centrais + nome exato
2. O quadro societário da Receita Federal é histórico — o servidor pode ter sido sócio antes de ingressar no serviço público
3. O match por nome da organização é aproximado — órgãos com nomes longos ou abreviações diferentes podem não ser detectados
4. Servidores cedidos, em requisição ou exercício fora do órgão de lotação não são capturados por este cruzamento
