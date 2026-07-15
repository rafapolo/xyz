# Concentração Monopólica em Órgãos Federais

Órgãos federais onde um único fornecedor venceu mais de 60% do valor total licitado (2021–2023). Alta concentração em um único CNPJ é sinal de direcionamento de licitação, dispensa irregular ou ausência de competição real.

**Fonte**: `br_cgu_licitacao_contrato.licitacao_item`  
**Período**: 2021–2023  
**Filtro**: valor_item R$10.001–R$500M; CNPJ válido; valor total do órgão > R$10M; participação do fornecedor > 60%

---

## Resultados (ordenados por valor do fornecedor)

| Órgão | Fornecedor | CNPJ | Valor Fornecedor (R$) | Total Órgão (R$) | Concentração |
|---|---|---|---|---|---|
| Instituto Federal de Sergipe | DIAS DISTRIBUIDORA DE LIVROS LTDA | 07341940000193 | 1.055.000.000 | 1.421.650.886 | 74,2% |
| Universidade Federal de Minas Gerais | FUNDACAO DE DESENVOLVIMENTO DA PESQUISA | 18720938000141 | 675.607.508 | 969.803.527 | 69,7% |
| Ministério do Trabalho e Emprego | CAIXA ECONOMICA FEDERAL | 00360305000104 | 418.427.557 | 633.798.416 | 66,0%¹ |
| Ministério dos Direitos Humanos e Cidadania | FCA FIAT CHRYSLER AUTOMOVEIS BRASIL LTDA. | 16701716000156 | 267.051.535 | 417.832.620 | 63,9% |
| Caixa de Construções de Casas para o Pessoal | PAULO OCTAVIO INVESTIMENTOS IMOBILIARIOS LTDA | 00475251000122 | 44.783.873 | 50.029.209 | 89,5% |
| Fundo Nacional de Aviação Civil | INFRAERO | 00352294000110 | 32.031.090 | 32.031.090 | 100,0%¹ |
| Ministério do Desenvolvimento Agrário | R7 FACILITIES - MANUTENCAO E SERVICOS LTDA | 11162311000173 | 22.429.180 | 26.235.750 | 85,5% |
| Superintendência de Desenvolvimento do Centro-Oeste | CAIXA ECONOMICA FEDERAL | 00360305000104 | 15.000.000 | 21.345.784 | 70,3%¹ |
| Amazônia Azul Tecnologia de Defesa S.A. | G4F SOLUCOES CORPORATIVAS LTDA | 07094346000145 | 12.198.000 | 16.344.595 | 74,6% |

> ¹ Possível falso positivo: Caixa Econômica Federal como agente pagador do MTE (FGTS/seguro-desemprego) e Infraero recebendo do FNAC são relações contratuais estruturais, não licitações competitivas.

---

## Casos de destaque

- **Instituto Federal de Sergipe / DIAS DISTRIBUIDORA DE LIVROS**: R$1,05B em 3 anos para um único distribuidor de livros é valor desproporcional para uma instituição de ensino de porte médio. O total contratado (R$1,4B) supera o orçamento anual de vários institutos federais maiores.
- **UFMG / FUNDACAO DE DESENVOLVIMENTO DA PESQUISA (FUNDEP)**: A FUNDEP é a fundação de apoio da própria UFMG — relação institucional que pode configurar conflito de interesses estrutural, dado que a fundação recebe quase 70% de toda a contratação da universidade.
- **Ministério dos Direitos Humanos / FIAT**: R$267M em veículos para um ministério de orçamento reduzido sugere compras centralizadas de toda a administração ou reclassificação de unidades gestoras.
- **Caixa de Construções / PAULO OCTAVIO**: Construtora privada do DF com 89,5% dos contratos de uma entidade habitacional federal — alta concentração sem competição aparente.

---

## Metodologia e Limitações

- **Tabelas**: `br_cgu_licitacao_contrato.licitacao_item`
- **Período**: 2021–2023 (anos com dados completos)
- **Limitações**:
  1. Alguns órgãos têm por natureza um único fornecedor possível (p.ex. Infraero para fundo de aviação civil)
  2. Fundações de apoio universitárias (FUNDEP, FAPEMIG) aparecem por design — relação não é licitação competitiva padrão
  3. Ministérios com unidades gestoras fragmentadas podem parecer concentrados por distribuição contábil
  4. Período de 3 anos pode incluir contratos plurianuais que distorcem a concentração aparente
