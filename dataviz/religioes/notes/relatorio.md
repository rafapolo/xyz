# Relatório — Templos Religiosos do Brasil por Vertente

Achados da investigação de `dados/igrejas_geolocalizadas.parquet` (765.591 templos — ver `../metodologia.md` para a construção completa do dataset). Este documento cobre análises que não couberam no mapa em si: distribuição por UF, série temporal de fundação (via CNPJ), formalização por vertente, e perguntas em aberto.

## 1. Vertente por UF

% Católica e % Evangélica pentecostal por estado (rollup de vertente, as duas maiores categorias — total de templos entre parênteses):

| UF | Total | % Católica | % Pentecostal |
|---|---:|---:|---:|
| SP | 124.424 | 9,5% | 32,1% |
| MG | 80.535 | 17,2% | 28,8% |
| RJ | 78.481 | 4,9% | 32,3% |
| BA | 68.012 | 14,3% | 30,1% |
| PA | 46.305 | 11,7% | 40,2% |
| RS | 38.098 | 13,0% | 22,5% |
| PR | 35.733 | 16,2% | 27,6% |
| CE | 31.464 | 17,6% | 31,4% |
| PE | 30.835 | 15,0% | 34,5% |
| MA | 30.394 | 19,1% | 34,2% |
| GO | 27.141 | 8,8% | 40,5% |
| AM | 21.326 | 11,2% | 35,3% |
| SC | 21.279 | 15,3% | 26,0% |
| ES | 21.275 | 12,6% | 39,6% |
| PB | 14.281 | 24,3% | 28,8% |
| MT | 13.680 | 13,8% | 31,9% |
| PI | 12.660 | 24,6% | 29,8% |
| MS | 11.256 | 9,4% | 31,7% |
| RN | 11.089 | 18,3% | 31,7% |
| AL | 10.880 | 15,1% | 36,0% |
| RO | 10.498 | 12,6% | 34,1% |
| SE | 7.447 | 17,0% | 29,0% |
| TO | 6.576 | 12,0% | 41,7% |
| AC | 5.347 | 7,6% | 41,1% |
| AP | 3.885 | 9,5% | 37,2% |
| RR | 2.690 | 9,8% | 35,7% |

**Padrão notável**: RJ tem a menor % católica do país (4,9%) — bem abaixo até de SP (9,5%). Norte (PA, TO, AC, AP, RR, AM) tem consistentemente a maior % pentecostal (35–42%), enquanto Nordeste tradicional (PB, PI) mantém % católica mais alta (24%+), destoando do resto do país. Vale cruzar isso com o mapa de conversão evangélica 2010→2022 já existente no projeto (`../mapa_conversao_evangelica_2010_2022.png`) — a hipótese óbvia é que o Norte, sendo fronteira de povoamento mais recente, teve penetração pentecostal mais forte que o Nordeste católico tradicional, mas isso não foi testado formalmente aqui.

## 2. Série temporal de fundação (via CNPJ)

CNEFE não tem data de fundação do templo. A única fonte de data que temos é `data_inicio_atividade` do CNPJ (Receita Federal) — então isto é um proxy limitado ao **subconjunto formalizado** (154.792 templos, 20,2% do total), não ao universo completo. Contagem de registros ativos de CNAE 9491-0/00 por ano de abertura, agregada por década:

| Década | Novos registros | % do total formalizado |
|---|---:|---:|
| até 1959 | 66 | 0,0% |
| 1960–1969 | 790 | 0,4% |
| 1970–1979 | 13.070 | 6,2% |
| 1980–1989 | 15.569 | 7,3% |
| 1990–1999 | 24.145 | 11,4% |
| 2000–2009 | 40.855 | 19,2% |
| 2010–2019 | 71.672 | 33,7% |
| 2020–2025* | 46.316 | 21,8% |

\* parcial — só até a safra mais recente disponível (2025-09), não é uma década completa.

**Leitura**: crescimento nítido e acelerado a partir dos anos 2000, com a década 2010–2019 sozinha respondendo por mais de um terço de todos os registros formais já feitos. Isso é consistente com o boom evangélico bem documentado no Brasil nesse período — mas atenção: **isto mede taxa de formalização/abertura de CNPJ, não taxa de fundação de igrejas**. Uma igreja fundada em 1985 mas formalizada só em 2015 aparece como "2015" aqui. Não dá pra distinguir os dois efeitos com os dados que temos.

Ano a ano completo está disponível se for útil pra um gráfico de verdade (não extraído aqui, só as somas por década) — os dados brutos estão no comando usado nesta sessão, reprodutível via `br_me_cnpj.estabelecimentos` filtrado por `cnae_fiscal_principal='9491000'`.

## 3. % com CNPJ vs. sem, por vertente

| Vertente | Total | Com CNPJ | % |
|---|---:|---:|---:|
| Mórmon | 525 | 254 | **48,4%** |
| Judaica | 116 | 48 | 41,4% |
| Islâmica | 27 | 11 | 40,7% |
| Novas religiões orientais | 262 | 83 | 31,7% |
| Budismo | 178 | 54 | 30,3% |
| Espírita | 21.521 | 6.059 | 28,2% |
| Testemunhas de Jeová | 7.516 | 1.838 | 24,5% |
| Evangélica não determinada | 37.319 | 9.034 | 24,2% |
| Evangélica de Missão | 60.405 | 14.564 | 24,1% |
| Não classificado | 282.505 | 60.389 | 21,4% |
| Umbanda e Candomblé | 9.868 | 2.109 | 21,4% |
| Evangélica pentecostal | 245.669 | 49.638 | 20,2% |
| **Católica Apostólica Romana** | **99.680** | **10.711** | **10,7%** |

**Achado contraintuitivo**: Católica tem a *menor* taxa de formalização de todas, quase metade da média geral. Hipótese mais provável (não confirmada diretamente, mas coerente com a estrutura institucional conhecida da Igreja Católica no Brasil): a **Diocese** é o CNPJ, não cada capela/paróquia — uma diocese registra um único CNPJ que cobre dezenas de templos físicos, então nosso cruzamento por CEP (que exige um CNPJ religioso *no mesmo CEP* do templo) sistematicamente não encontra match para capelas que ficam fisicamente distantes da sede administrativa da diocese. Isso significa que o número de 10,7% **subestima** a formalização católica por um artefato metodológico, não reflete informalidade real maior que as outras vertentes. Mórmon, Judaica e Islâmica formalizam mais (cada congregação/sinagoga/mesquita tende a ter registro próprio), mas são grupos pequenos — a diferença percentual ali é estatisticamente mais frágil.

## 4. Por que o governo não fecha as "não oficiais"?

Isto é análise, não um achado extraído dos dados — baseado em conhecimento geral sobre o arcabouço legal brasileiro, não verificado linha a linha nesta sessão:

- **Liberdade religiosa é direito constitucional** (Art. 5º, VI da Constituição) — o culto e a reunião religiosa em si não dependem de registro em nenhum órgão pra serem legais. CNPJ é necessário só pra atividades acessórias: abrir conta bancária, contratar funcionário formalmente, emitir recibo de doação dedutível, ter imóvel em nome da entidade.
- **Imunidade tributária de "templos de qualquer culto"** (Art. 150, VI, "b") é uma garantia constitucional sobre o patrimônio/renda do templo, não algo condicionado a CNPJ — reforça que o Estado brasileiro trata a existência do templo como presumida, não como algo a ser autorizado.
- **Não há ilícito em reunião religiosa informal** — abrir uma "igreja" numa sala alugada não é análogo a abrir um comércio sem alvará; a fiscalização municipal (quando existe) tende a mirar segurança/zoneamento de edificações em geral, não a natureza religiosa do uso.
- **Capacidade fiscalizatória é finita e direcionada**: Receita Federal e Ministério Público de fato atuam contra organizações religiosas — mas contra as que *têm* CNPJ e são suspeitas de fraude fiscal/lavagem (casos de grandes denominações neopentecostais na imprensa), não contra a informalidade de congregações pequenas, que não geram sonegação relevante por não movimentarem valor tributável formalmente.
- **Custo político**: o bloco evangélico é grande e politicamente organizado no Brasil; não há incentivo político pra uma cruzada de formalização compulsória de igrejas pequenas.

Isso é raciocínio, não uma citação de lei específica verificada — se for usar isso em algo formal, vale confirmar as referências legais exatas antes de publicar.

## 5. Dez perguntas em aberto

Coisas que a investigação levantou mas não deu tempo/dado pra responder:

1. **Templos duplicados no mesmo endereço exato** — quantos `lat`/`lon` idênticos aparecem mais de uma vez no dataset? Pode ser templo que trocou de denominação ao longo do tempo (registro antigo não removido) ou erro de duplicação do CNEFE. → respondida em §6.1
2. **Correlação com densidade demográfica de fiéis declarados** — a proporção de templos islâmicos/budistas/judaicos bate com a proporção de fiéis dessas religiões no Censo demográfico (tabela 9537)? Não cruzamos os dois datasets do projeto (`igrejas_geolocalizadas.parquet` vs `resultante.csv`/`ibge_sidra_tabela_9537.csv`). → respondida em §6.2
3. **Qualidade da coordenada por região** — `nivel_geocodificacao_coordenadas` (99,5% nível 1 nacionalmente) varia por UF? Se templos em áreas rurais/pobres tiverem coordenada pior sistematicamente, isso introduz viés espacial nas análises de densidade que não foi testado. → respondida em §6.3
4. **Sobreposição geográfica com dados de raça/cor** — o projeto irmão (`../../racas/`) já mapeia raça/cor por município; terreiros de Umbanda/Candomblé se concentram em áreas de maior população afrodescendente ou quilombola? Não cruzado. → respondida em §6.4
5. **Quantas "marcas" de igreja independente ainda não catalogadas existem?** Dos 194.627 nomes únicos em `descricao_estabelecimento`, só uma fração pequena bate no dicionário de ~115 padrões (`cnefe-descricao-vertente.csv`). Não sabemos quantas denominações reais e nomeáveis ainda estão dentro do bolo de "não classificado" (282.505) esperando um padrão novo. → respondida em §6.5
6. **Por que `tipo_especie=6` é tão mais comum que `tipo_especie=8` pra descrever igreja?** 195.163 casos onde o recenseador reconheceu "estabelecimento" mas não marcou "religioso" mesmo com o nome dizendo claramente. É ambiguidade do manual de campo, uso misto do espaço (comercial + religioso), ou outro motivo? Não investigado com o IBGE nem contra a metodologia do Censo. **Continua em aberto** — ver nota em §6.
7. **Padrão etário por vertente** — dá pra construir um "gráfico geracional" cruzando `data_inicio_atividade` (CNPJ, só pro subconjunto formalizado) com vertente, pra ver se pentecostal é sistematicamente mais recente que missão/católica? A tabela da seção 2 é nacional agregada; não foi quebrada por vertente. → respondida em §6.6
8. **Templos por habitante, não só templos absolutos** — o ranking da seção 1 é por contagem bruta; não normalizamos por população municipal/estadual. SP lidera em volume só por ser o estado mais populoso — o ranking por templo per capita provavelmente muda a ordem. → respondida em §6.7
9. **Taxa de "sobrevivência" institucional** — dá pra saber quantos templos com CNPJ aberto há 20+ anos ainda estão `situacao_cadastral='2'` (ativos) vs. quantos abriram e fecharam? Isso mediria rotatividade/instabilidade institucional por vertente, não só crescimento bruto. → respondida em §6.8
10. **Por que Rio de Janeiro tem a menor % católica do Brasil (4,9%)?** Chamou atenção na seção 1 mas não foi investigado — é padrão histórico de colonização, efeito de fronteira metropolitana, ou artefato da nossa classificação (RJ tem particularidade de nomenclatura de templo que o dicionário classifica pior)? **Continua em aberto** — ver nota em §6.

## 6. Perguntas respondidas

As oito perguntas abaixo (das dez da seção 5) foram respondidas cruzando arquivos que já existiam no projeto — nenhuma delas exigiu nova coleta de dado, só nova consulta. Duas ferramentas novas, reproduzíveis, foram escritas para isso:

- `dados/perguntas_abertas.py` — roda localmente (`igrejas_geolocalizadas.parquet` + `resultante.csv` + `../racas/data.json`), responde §6.1 a §6.5 e §6.7.
- `dados/consulta_cnpj_vertente_tempo.py` — exige `ssh beelink` + DuckDB (mesmo acesso remoto de `gerar_igrejas_geolocalizadas.py`), responde §6.6 e §6.8, reclassificando `razao_social` do CNPJ com o mesmo dicionário de vertente (`cnefe-descricao-vertente.csv`), já que o parquet local só guarda o booleano `com_cnae`, não a data de abertura. Esse método é o mesmo do NT20 (Araújo/CEM) — ver `../notes/nt20-araujo-analise.md`.

Duas das dez perguntas (6 e 10) permanecem sem resposta: são questão de metodologia de campo do IBGE e questão causal/histórica, respectivamente — nenhum cruzamento de dado que já temos resolve isso (ver nota ao final desta seção).

### 6.1 — Coordenadas duplicadas

2.538 pares de `lat`/`lon` aparecem mais de uma vez no dataset, envolvendo 5.253 templos (0,7% do total) — proporção pequena, não é um problema estrutural. Os dois maiores grupos têm 9 templos cada, na mesma coordenada, em Goiânia-GO e em Portel-PA. Não investigamos linha a linha se são denominações que trocaram de nome no mesmo endereço ou duplicação genuína do CNEFE, mas a escala (0,7%) não muda nenhuma leitura agregada deste relatório.

### 6.2 — Correlação templos × fiéis declarados (Censo 2022)

Corresponde à Fig. 6/Apêndice B do NT20 — mas o NT20 só validou 2010, só evangélica, e só por UF. Aqui: por vertente (Católica, Evangélica, Espírita, Umbanda e Candomblé), por município e por UF, contra o Censo **2022**, correlacionando templos/100 mil hab. com % de fiéis declarados (mesma métrica do NT20 — normalizar por população nos dois lados é essencial, ao contrário de comparar contagem bruta, que só mediria tamanho de cidade):

| Vertente | r (município, n=5.569) | r (UF, n=26)* |
|---|---:|---:|
| Evangélica | 0,537 | **0,839** |
| Espírita | 0,638 | 0,787 |
| Umbanda e Candomblé | 0,302 | 0,602 |
| Católica | 0,362 | 0,411 |

\* DF sai da base — zero templos no parquet, mesmo gap de fonte do CNEFE já registrado pra `docs/viz-uf` (ver `../notes/nt20-araujo-analise.md`, item 1).

**Leitura**: a correlação é mais forte agregada por UF do que por município (esperado — ruído de classificação/geocodificação de cada templo individual se cancela na agregação). Evangélica é a vertente com correlação mais forte por UF (0,839), muito próxima do que o NT20 relatou pra 2010 — sinal de que a heurística de classificação (texto do CNEFE, não CNAE) é tão válida quanto o método original. Católica tem a correlação mais fraca das quatro (0,411 por UF) — consistente com o achado da seção 3 deste relatório: templo católico com CNPJ raramente fica no mesmo CEP da capela (diocese centraliza o registro), então a contagem de templos por município provavelmente subrepresenta presença católica de forma desigual pelo país, atenuando a correlação com o Censo.

### 6.3 — Qualidade de coordenada por UF

`nivel_geocodificacao_coordenadas=1` (GPS real de campo) varia pouco: de 98,6% (RJ) a 100,0% (SE, PI, TO). RJ e AP são as únicas UFs abaixo de 99%. Não há um padrão evidente de "UF pobre/rural = coordenada pior" — RJ é justamente uma das UFs mais urbanizadas do país e ainda assim tem a pior taxa, então o viés espacial que a pergunta original temia (áreas rurais penalizadas) não aparece nos dados; a variação entre UFs (98,6%–100%) é pequena demais pra distorcer qualquer análise de densidade deste relatório.

### 6.4 — Sobreposição Umbanda/Candomblé × raça/cor

Cruzando terreiros/100 mil hab. por município (`igrejas_geolocalizadas.parquet`) com % preta+parda (`../racas/data.json`, Censo 2022), em 1.382 municípios com pelo menos um terreiro contado: **r = 0,127** — correlação positiva, mas fraca. Não confirma a hipótese "terreiro se concentra onde há mais população afrodescendente" com a força que se poderia esperar. Uma leitura possível: a formalização de Umbanda/Candomblé (seção 3 deste relatório, 21,4% com CNPJ) e a geocodificação por CNEFE têm suas próprias distorções regionais que competem com o sinal demográfico — não isolamos os dois efeitos aqui.

### 6.5 — Nomes fora do dicionário

282.505 templos (36,9% do total) ficam sem vertente atribuída, com 100.683 descrições únicas entre eles. Mas a distribuição é extremamente concentrada: **81.948 (29% dos não classificados) são literalmente só "IGREJA"**, sem nenhum outro qualificador — não há padrão de texto possível de extrair daí, é uma limitação de informação na fonte, não do dicionário. Depois disso, o resto já é cauda longa (nenhum outro nome único passa de 2.305 ocorrências — "SEM NOME"). Conclusão prática: não há uma nova leva grande de denominações nomeáveis esperando ser adicionada ao dicionário — o "não classificado" é estruturalmente irredutível na maior parte, não um dicionário incompleto.

### 6.6 — Padrão etário por vertente

Corresponde à Fig. 1/2 e Apêndice A do NT20. Reclassificando `razao_social` do CNPJ (não `descricao_estabelecimento` do CNEFE) com o mesmo dicionário, CNAE 9491-0/00 ativos, por década:

| Década | Católica | Evangélica | Espírita | Umbanda e Candomblé | Outras |
|---|---:|---:|---:|---:|---:|
| até 1969 | 32 | 139 | 144 | 2 | 4 |
| 1970–1979 | 1.657 | 5.599 | 1.098 | 41 | 286 |
| 1980–1989 | 898 | 9.136 | 1.169 | 62 | 281 |
| 1990–1999 | 1.485 | 13.678 | 1.746 | 126 | 283 |
| 2000–2009 | 1.827 | 24.813 | 1.644 | 263 | 732 |
| 2010–2019 | 1.770 | 47.462 | 1.592 | 704 | 358 |
| 2020–2025* | 662 | 24.771 | 1.010 | 1.098 | 72 |

\* parcial, mesma safra usada na seção 2. 69,0% dos 212.482 CNPJ religiosos ativos bateram no dicionário (taxa de match sobre razão social, comparável aos 63,1% de classificação sobre `descricao_estabelecimento` no CNEFE).

**Leitura**: a expansão evangélica pós-2000 (seção 2 deste relatório) é quase inteiramente puxada pela própria Evangélica — Católica e Espírita ficam praticamente estáveis em volume absoluto de novos CNPJs desde os anos 1980. O dado mais chamativo é Umbanda e Candomblé: cresce pouco até 2010, mas a década de 2020 (parcial) já supera 2010–2019 inteira em registros novos — sinal de formalização recente acelerada, não necessariamente de mais terreiros abrindo (pode ser terreiro antigo se formalizando agora).

### 6.7 — Templos por habitante

Corresponde à Fig. 3/4/5 do NT20 (ele fez isso só pra Pentecostal por UF em 2019; aqui é todas as vertentes juntas, por UF e por município, 2022):

**Por UF** — AC lidera (781,6 templos/100 mil hab.), SP é a lanterna (317,7/100 mil) apesar de ter o maior volume absoluto (124.424 templos) da seção 1 — confirma a suspeita da pergunta original: o ranking por volume bruto (seção 1) é puramente um efeito de tamanho populacional, não densidade religiosa. Norte e Nordeste dominam o topo do ranking per capita (AC, RO, PA, AM, AP, ES, RJ, BA, MA, RR, TO nas 11 primeiras posições).

**Por município** (pop. mínima 20 mil): topo é dominado por município do Pará/Amazonas (Careiro-AM, 1.519/100 mil; Acará-PA, 1.454/100 mil); o fundo é dominado por cidade de Santa Catarina/litoral (Balneário Camboriú-SC, 158,3/100 mil; Blumenau-SC, 161,1/100 mil) — mesmo padrão regional do ranking por UF, replicado em escala municipal.

### 6.8 — Taxa de sobrevivência institucional (CNPJ aberto até 2005)

Entre os 84.617 CNPJ religiosos ativos abertos até 2005 (20+ anos atrás), a proporção que continua `situacao_cadastral='2'` (ativa) hoje varia muito por vertente:

| Vertente | Ativa | Baixada | Outra | Total | % ativa |
|---|---:|---:|---:|---:|---:|
| Católica | 5.130 | 1.118 | 255 | 6.503 | **78,9%** |
| Evangélica | 42.186 | 15.185 | 8.359 | 65.730 | 64,2% |
| Espírita | 5.115 | 2.615 | 1.345 | 9.075 | 56,4% |
| Umbanda e Candomblé | 353 | 1.072 | 339 | 1.764 | **20,0%** |

**Leitura**: Católica tem, de longe, a maior taxa de sobrevivência institucional (quase 79%) — plausível dado que o CNPJ católico costuma ser da Diocese (seção 3 deste relatório), uma entidade administrativa estável, não a capela individual. Umbanda e Candomblé tem a menor taxa (20%) por uma margem grande — mas a base é pequena (1.764 registros) e a seção 3 já mostra que só 21,4% dos terreiros têm CNPJ pra começo de conversa, então este número mede rotatividade entre os poucos terreiros que já formalizaram, não a estabilidade do universo real de terreiros.

### Perguntas que continuam sem resposta

- **Pergunta 6** (por que `tipo_especie=6` é mais comum que `tipo_especie=8`): é uma questão sobre o manual de campo do recenseador do IBGE. Não há como decidir isso cruzando dados que já temos — precisaria da documentação oficial do Censo 2022 ou contato direto com o IBGE.
- **Pergunta 10** (por que RJ tem a menor % católica do Brasil): é uma questão causal/histórica (colonização, migração, urbanização). Os dados agregados deste relatório descrevem o padrão mas não têm poder explicativo sobre a causa — precisaria de pesquisa histórica/bibliográfica, não de mais cruzamento de dataset.

## Fontes desta análise

Seções 1 e 3: `dados/igrejas_geolocalizadas.parquet`. Seção 2: `br_me_cnpj.estabelecimentos` via `ssh beelink` + DuckDB, consulta não persistida como script (reproduzir exige reescrever o SQL a partir da descrição da seção). Seção 6: `dados/perguntas_abertas.py` (§6.1–6.5, 6.7) e `dados/consulta_cnpj_vertente_tempo.py` (§6.6, 6.8) — ambos persistidos no repo e reprodutíveis diretamente (`python3 dados/perguntas_abertas.py`; o segundo exige acesso `ssh beelink`).
