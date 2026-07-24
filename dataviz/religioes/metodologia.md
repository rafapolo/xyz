# Metodologia — Mapa de Templos Religiosos do Brasil por Vertente

Documento de metodologia para replicação e revisão por pares. Descreve como `dados/igrejas_geolocalizadas.parquet` e `igrejas/index.html` foram construídos, as decisões tomadas, os erros encontrados e corrigidos ao longo do processo, e as limitações conhecidas do resultado final.

## 1. Objetivo

Geolocalizar todos os templos religiosos do Brasil (igreja, templo, terreiro, sinagoga, etc.) e classificá-los por vertente/denominação, para visualização em mapa. Não existe uma base pública pronta que já faça isso — foi construída a partir do cruzamento de três fontes públicas do IBGE e da Receita Federal.

## 2. Fontes de dados

| Fonte | O que fornece | Acesso |
|---|---|---|
| **CNEFE** — Cadastro Nacional de Endereços para Fins Estatísticos, Censo 2022 (`br_ibge_censo_2022.cadastro_enderecos`) | Um registro por endereço/edificação no Brasil, com latitude/longitude reais (capturadas em campo pelo recenseador), um campo estruturado de tipo de estabelecimento, e um campo de texto livre (`descricao_estabelecimento`) anotado pelo recenseador | Mirror local em `~/rodado` (basedosdados), acessado via `ssh beelink` + DuckDB |
| **IBGE SIDRA, tabela 137** (Censo 2010) | A taxonomia oficial completa de religião no Brasil: 75 categorias em até 3 níveis (ex. Evangélica → de Missão / de origem pentecostal → denominação nomeada) | `https://servicodados.ibge.gov.br/api/v3/agregados/137/metadados` — copiada para `dados/vertentes-religiosas.csv` |
| **IBGE SIDRA, tabela 9537** (Censo 2022) | Percentual de católicos/evangélicos/etc. por município — só o nível agregado "Evangélicas", sem subdivisão por denominação (ver §7) | `dados/ibge_sidra_tabela_9537.csv`, usado no mapa `../index.html`, não no mapa de templos |
| **CNPJ / Receita Federal** (`br_me_cnpj.estabelecimentos`) | Registro formal de organizações religiosas (CNAE 9491-0/00) — usado só como sinal complementar de confiança, não como fonte de geolocalização principal (ver §6) | Mirror local em `~/rodado` |

## 3. Critério de presença: o que conta como "templo"

### 3.1 Tentativa inicial (texto livre) — abandonada

A primeira versão selecionava candidatos por busca textual em `descricao_estabelecimento` (termos como "IGREJA", "TEMPLO", "TERREIRO", "PAROQUIA" etc.), com uma lista de exclusões manual pra remover falsos positivos óbvios (ex. "TERREIRO DE CAFE" = área de secar café, não terreiro de Candomblé). Essa abordagem chegou a 570–700 mil linhas em iterações sucessivas, sempre girando ~17–20% acima do número oficial do IBGE (579.800 estabelecimentos religiosos, divulgado no Censo 2022).

### 3.2 Critério final: campo estruturado oficial do CNEFE

O CNEFE tem um campo `tipo_especie`, preenchido pelo recenseador em campo (não é inferência nossa), com 8 valores possíveis — um deles é **`8 = "Estabelecimento religioso"`**. Nacionalmente, `tipo_especie='8'` retorna **574.369** linhas — a **1,6%** do número oficial do IBGE (579.800). É, para todos os efeitos, o mesmo critério que gera a estatística publicada pelo Censo.

**Decisão**: usar `tipo_especie='8'` como único critério de presença (é ou não é templo). O dicionário de texto livre (§4) deixou de decidir *se* uma linha entra no dataset — só decide *qual vertente* atribuir a ela.

Comparação que motivou a mudança (nacional):
- **488.433** linhas batiam nos dois critérios (tipo_especie=8 E texto livre) — núcleo de alta confiança.
- **85.931** linhas eram `tipo_especie='8'` mas **não** batiam em nenhum padrão de texto — templos reais com nome incomum, sigla, ou erro de digitação, que uma busca por palavra-chave perde.
- **215.688** linhas batiam em texto livre mas **não** eram `tipo_especie='8'` — bar, depósito, fazenda, sítio vago que só coincidia de ter uma palavra parecida na descrição. Essa era a origem da maior parte do excesso de 17–20%.

Uma pequena lista de exclusões (`excluir=true` em `dados/cnefe-descricao-vertente.csv`) ainda é aplicada por cima de `tipo_especie='8'`, como rede de segurança contra possível erro de campo do próprio recenseador (ex. maçonaria classificada como estabelecimento religioso, mas não é uma denominação da taxonomia do IBGE).

## 4. Classificação por vertente (heurística)

`tipo_especie='8'` diz *que* é um templo, mas não diz qual denominação — esse campo não existe no CNEFE. A vertente é inferida por casamento de substring entre `descricao_estabelecimento` e um dicionário curado manualmente: `dados/cnefe-descricao-vertente.csv`.

**Mecânica** (em `gerar_igrejas_geolocalizadas.py`):
1. Padrões (`excluir=false`) são ordenados por **(prioridade desc, comprimento desc)** e viram uma cadeia `CASE WHEN ... ILIKE '%padrao%' THEN vertente_id` em SQL — o primeiro que bater decide o `vertente_id`.
2. Padrões de exclusão (`excluir=true`) são checados primeiro; se baterem, a linha é descartada mesmo tendo `tipo_especie='8'`.
3. Se nenhum padrão positivo bater, `vertente_id` fica `NULL` ("não classificado") — a linha continua no dataset como presença confirmada de templo, só sem denominação atribuída. **Nunca se força uma classificação sem evidência textual.**

**Colunas do dicionário**: `padrao, vertente_id, fonte, confianca, excluir, prioridade`.
- `vertente_id` referencia sempre um `id` de `dados/vertentes-religiosas.csv` (a taxonomia oficial do IBGE) — nunca um código inventado.
- `fonte` documenta de onde veio a certeza: `censo2010_nomenclatura` (nome já é literal numa categoria oficial do IBGE), `pesquisa_web` (confirmado via busca), `inferencia_nome` (só o padrão do nome, sem fonte externa), `revisao_fable` (correção/adição feita na auditoria de segunda opinião, §5), `mineracao_*` (§4.2).
- Regra seguida durante a curadoria: **toda denominação cujo nome não é autoexplicativo foi pesquisada antes de classificar** — ex. "Igreja Adventista da Promessa" parece família Adventista/Missão pelo nome, mas é historicamente pentecostal (confirmado via busca); o mesmo padrão de erro apareceu depois com "Igreja Missionária X" (nome sugere família Missão, mas é nomenclatura pentecostal/neopentecostal — corrigido na auditoria).

**Por que `prioridade` existe.** Desempatar só por comprimento tinha um efeito perverso: `IGREJA EVANGELICA` → "Evangélica não determinada" tem 17 caracteres e ganhava de `IGREJA BATISTA` (14), então `IGREJA EVANGELICA QUADRANGULAR` era publicada como *não determinada*. Eram 1.932 templos com denominação declarada no próprio nome caindo no balde genérico. A prioridade separa **quão confiável** é o padrão de **quão comprido** ele é:

| prioridade | camada | o que é |
|---|---|---|
| 100 | curado | escrito à mão, com `fonte` |
| 95 | demoção | curado que perdia pra um irmão mais específico (`TERREIRO` vs `TERREIRO DE UMBANDA`) |
| 90 | grafia | erro de digitação (§4.2) |
| 60 | exceção | contexto que contradiz um marcador |
| 50 | marcador | token denominacional |
| 40 | n-grama | propagação por co-ocorrência |
| 30 | fallback | guarda-chuva "é evangélica e não sabemos qual" |
| 20 | hagiônimo | nome de santo |

Hagiônimo no fundo é a decisão de conteúdo mais importante da tabela: `SAO SEBASTIAO`, `SANTA BARBARA`, `NOSSA SENHORA` indicam católica **só na ausência de qualquer outro sinal**, porque terreiro de umbanda e centro espírita usam exatamente os mesmos nomes (sincretismo). Com hagiônimo acima de `TERREIRO`, "TERREIRO SAO SEBASTIAO" virava católica — subnotificando justamente a religião de menor volume e maior sensibilidade.

### 4.2 Mineração de padrões (`minerar_padroes.py`)

Os ~265 padrões escritos à mão deixavam **37% dos templos sem classificação**. Boa parte não era falta de sinal, e sim sinal fora do formato canônico: `COMUNIDADE BATISTA`, `MISSAO BATISTA`, `IGREIJA BATISTA` — 2.562 templos com "BATIST" no nome e sem vertente. `minerar_padroes.py` propõe padrões novos usando o **corpo já classificado como evidência**.

**Evidência honesta.** A estatística ingênua se auto-confirma: o n-grama `DE DEUS` parece 93% Assembleia de Deus, mas só porque o padrão `ASSEMBLEIA DE DEUS` o contém — não há informação nova ali. Então, ao avaliar um trecho `g`, só contam as linhas classificadas cujo rótulo veio de um padrão que **não contém** `g`. Se o sinal sobrevive a isso, ele é independente. É esse teste que faz `SAO JOAO BATISTA` sair como **católica**: as linhas classificadas que o contêm foram rotuladas por `IGREJA SAO`, não por um padrão batista.

As quatro camadas (marcador, exceção, n-grama, grafia) estão documentadas no docstring do script. A que mais rende é o **marcador**: um token que, no dicionário curado, só aparece em padrões de uma única vertente. Ele é aceito conforme a **discordância** — entre as linhas classificadas que o contêm mas foram rotuladas por outro sinal, quantas apontam pra vertente diferente. `BATISTA` fica em 6,4%, quase toda do idiomatismo católico "São João Batista", que a camada de exceção então isola e cobre; `PARA`, `BELEM`, `SOCIEDADE`, `MISSIONARIA` ficam entre 49% e 99% e são rejeitados.

Nada é aplicado automaticamente. A saída é `candidatos_padroes.csv` (com ganho, pureza, suporte e exemplos por padrão) e `residuo_sem_classificacao.csv` (o que sobra, pra curadoria manual); `--aplicar` grava no dicionário. Antes de gravar, uma simulação roda o dicionário inteiro e **descarta qualquer candidato que reclassifique linha já rotulada** por padrão curado em prioridade cheia.

**Validação.** `--validar` esconde 30% dos padrões curados *de denominação específica* (fallback genérico fora do sorteio: reproduzir a convenção "não determinada" não testaria nada), remineração com o dicionário mutilado, e compara com o rótulo do dicionário inteiro. Isso simula a condição real de produção — texto com sinal denominacional que o dicionário não cobre. Em 6 sementes: **97–99,8% de precisão quando a mineração se compromete com uma denominação**, com duas exceções (59% e 71%) em que o sorteio removeu *todo* o vocabulário de uma religião (espírita, adventista) e não sobrou nada de onde inferir — situação que não ocorre em produção, onde os padrões curados estão todos presentes.

**Resultado**: "não classificado" caiu de 282.505 (36,9%) para **200.901 (26,2%)**, mais 4.705 templos que saíram de balde genérico pra denominação específica. Umbanda e Candomblé cresceu 38% (9.868 → 13.625) — o efeito combinado da mineração e da correção do sincretismo. O que resta é majoritariamente irrecuperável: 82 mil templos cujo nome anotado é literalmente "IGREJA", mais "SEM NOME", "CAPELINHA", "VAGO".

**Reaplicar o dicionário sem reconsultar o CNEFE**: a vertente é função pura de `descricao_estabelecimento`, então `reclassificar.py` reescreve só a coluna `vertente_id` no parquet local — não precisa do beelink nem reler 60 GB.

### 4.1 Agrupamento pra exibição (rollup)

A taxonomia oficial tem até 30+ subcategorias só dentro de "Evangélicas" (denominações nomeadas). Pra virar uma legenda de mapa utilizável, o script que gera `igrejas/data.json` agrupa (rollup) cada `vertente_id` até:
- o nível 2 mais próximo, se o pai for "Evangélicas" (id 95277) — preserva a distinção Missão / Pentecostal / não determinada, que é o eixo mais importante da análise;
- o nível 1 mais próximo, pra qualquer outra árvore (ex. Umbanda e Candomblé agrega suas subcategorias Umbanda/Candomblé/outras).

As 5 categorias minoritárias de menor volume (Islâmica, Mórmon, Novas religiões orientais, Budismo, Judaica) são agrupadas em "Outras" só pra visualização — o `vertente_id` fino continua no parquet.

## 5. Auditoria de segunda opinião

Depois da primeira versão do dicionário (texto livre, ~110 padrões), foi feita uma auditoria independente (modelo Fable, com acesso de leitura ao código e à base, sem poder de edição — só relatório) com o mandato explícito de achar erros em ambas as direções: falso positivo (não é templo) e falso positivo de vertente (é templo, denominação errada). Achados aplicados:

- **"MESQUITA" como termo-candidato genérico**: de 1.205 linhas nacionais contendo "MESQUITA", só ~20–37 eram mesquitas reais — o resto era o sobrenome "Mesquita" (mercadinho, bar, escritório de advocacia, sítio). Verificado manualmente antes de corrigir (a auditoria pode alucinar contagens específicas mesmo com acesso à base — toda alegação de contagem foi reconferida por consulta direta antes de virar edição). Corrigido tirando "MESQUITA" solto da lista de termos e trocando por grafias específicas de mesquita/centro islâmico.
- **Anexos paroquiais contados como templo católico**: `SALAO PAROQUIAL` (3.557), `CASA PAROQUIAL` (1.540), `SECRETARIA PAROQUIAL` (1.154) — escritório/residência/salão social da paróquia, não o templo. Movidos pra exclusão.
- **"CATEDRAL"/"SANTUARIO" genéricos**: nomes de igreja neopentecostal independente ("Catedral da Fé", "Santuário dos Milagres") estavam sendo classificados como Católica só pelo substantivo. Restrito a variantes com nome de santo (`CATEDRAL SAO`, `SANTUARIO NOSSA SENHORA` etc.).
- Diversos padrões novos recuperando denominações reais não cobertas antes (Sara Nossa Terra, Verbo da Vida, variantes de typo de "Assembleia"/"Pentecostal"/"Madureira").

Nenhuma edição da auditoria foi aplicada sem essa reconferência manual — o relatório é insumo, não fonte de verdade automática.

## 6. Atributo "oficial" vs. "encontrado pelo Censo": `com_cnae`

O dataset distingue explicitamente dois conceitos, que não são a mesma coisa:
- **Presença** (todos os 570.428 registros): decidida pelo campo oficial do IBGE, `tipo_especie='8'` — é um templo porque o recenseador observou e classificou assim em campo, com ou sem registro formal.
- **Formalização jurídica** (coluna `com_cnae`, booleana): o templo *também* tem um CNPJ ativo de organização religiosa (CNAE 9491-0/00) na Receita Federal, no mesmo CEP.

Isso é intencional, não um efeito colateral: é sabido que existem muito mais templos no Brasil do que os formalmente registrados — a maioria das congregações, principalmente pentecostais/independentes e terreiros, nunca abre CNPJ próprio. O objetivo do atributo é deixar essa diferença **visível e mensurável** no dado, não escondê-la nem tentar reconciliar os dois números como se devessem bater.

### 6.1 Como o cruzamento é feito (e por que não é por endereço completo)

Tentativa 1: `id_municipio + cep + numero + nome_logradouro` (endereço completo, igualdade exata de string). Resultado: só **30,5%** dos 206.617 CNPJs religiosos ativos do Brasil achavam qualquer correspondência no CNEFE. Investigação dos casos que batiam em `cep+numero` mas não em `logradouro` mostrou que **não é diferença de grafia** (abreviação/acento) — são ruas genuinamente diferentes que colidem em CEP+número por coincidência (comum em loteamentos com "Rua 1", "Rua 2", "Rua 3"...). Normalizar o nome da rua não resolveria isso, porque o problema não é formatação — reintroduzir uma correspondência mais frouxa nesse eixo (numero sem logradouro) já tinha sido tentado antes e gerava exatamente esse tipo de falso positivo (bar/depósito/fazenda casando com CNPJ religioso por coincidência de número).

Como o CNPJ não tem latitude/longitude (só endereço em texto), uma correspondência por proximidade geográfica real não é possível diretamente. A solução adotada: cruzar só por **`id_municipio + cep`** (sem número nem nome de rua), com uma salvaguarda contra CEPs muito grandes/rurais — um CEP só conta como confirmação se tiver no máximo 15 templos oficiais (`tipo_especie='8'`) naquele CEP (`MAX_TEMPLOS_POR_CEP` em `gerar_igrejas_geolocalizadas.py`). Mediana de 2 templos por CEP com CNPJ religioso — seletivo o suficiente pra ser informativo, sem a armadilha da cauda de CEPs enormes (até ~1.000 templos observados no mesmo CEP em municípios pequenos, onde um CEP cobre a cidade inteira).

Resultado: **116.887 templos (20,5%)** com confirmação de CNPJ no mesmo CEP — mais realista que os 4,6% da tentativa por endereço completo (que subestimava por falha de correspondência, não por informalidade real) e mais confiável que os ~54% da primeira tentativa ingênua (só CEP+número, sem essa salvaguarda), que misturava correspondência real com colisão de numeração.

**Ainda assim, `com_cnae=false` não prova informalidade** — só significa "não achamos confirmação nesse CEP dentro do limite de seletividade". A leitura correta do número é: no mínimo 20,5% dos templos do Brasil têm registro formal encontrável por este método; o resto pode ser informal, pode ter CNPJ não encontrado (CEP grande demais, excluído pela salvaguarda), ou pode ter CNPJ registrado em endereço administrativo diferente do templo físico.

## 6.1 Segunda camada de presença: templos "não oficiais" (`presenca='texto_livre'`)

Quando o critério virou `tipo_especie='8'` (§3.2), os 215.688 endereços que batiam em texto livre mas não em `tipo_especie='8'` foram descartados. Investigação posterior mostrou que **98,4%** desses (212.302) são `tipo_especie='6'` — "Estabelecimento de outras finalidades": o recenseador reconheceu como estabelecimento (não como domicílio comum), só não marcou a categoria específica "religioso", mesmo com o nome anotado dizendo claramente "IGREJA X"/"TEMPLO Y". Amostragem manual confirma nomes reais e reconhecíveis (Assembleia de Deus, Congregação Cristã, Testemunhas de Jeová, Espírita), não ruído.

Decisão: **mapear também essa camada, separada e identificada** (`presenca='texto_livre'`), aplicando o mesmo dicionário de vertente e a mesma lista de exclusão do §3–4. No mapa, esses pontos aparecem com opacidade reduzida (não escondidos por padrão) e um toggle deixa incluir/excluir. Nunca são somados aos 570.428 "oficiais" sem essa distinção visível — a coluna `presenca` no parquet permite recompor os dois totais separadamente a qualquer momento.

Resultado nacional:
| `presenca` | total | com CNPJ (`com_cnae`) |
|---|---:|---:|
| `oficial` (tipo_especie=8) | 570.428 | 116.887 (20,5%) |
| `texto_livre` (não oficial) | 195.163 | 37.905 (19,4%) |
| **Total** | **765.591** | 154.792 |

`tipo_especie IN (2,3,4,5,6)` compõem essa segunda camada (domicílio coletivo, agropecuário, ensino, saúde, outras finalidades) — `tipo_especie=1` (domicílio particular) fica de fora porque o campo `descricao_estabelecimento` estruturalmente não é preenchido pra residência comum, não há texto pra usar como sinal ali.

## 7. Por que a classificação de vertente é do Censo 2010, não 2022

O Censo 2022 recolheu religião com uma pergunta mais genérica que 2010, e o IBGE relatou dificuldade — e eventualmente não conseguiu — desmembrar "evangélica" em subcategorias (missão/pentecostal/etc.) nos dados de 2022, porque as respostas ficaram mais vagas ("só evangélico", sem citar a igreja) do que em censos anteriores. Por isso a taxonomia de referência (`vertentes-religiosas.csv`) vem da tabela 137, Censo 2010 — é a única fonte pública do IBGE com esse nível de detalhe por denominação. Isso é uma limitação herdada, não introduzida por este pipeline: não existe fonte 2022 oficial com esse detalhe pra comparar.

## 8. Limitações conhecidas (pra revisão por pares)

1. **~26% "não classificado"** (era 37% antes da mineração, §4.2) — templo confirmado (`tipo_especie='8'`), mas sem denominação atribuída porque o nome no CNEFE não dá informação suficiente: 82 mil são literalmente "IGREJA", o resto é "SEM NOME", "CAPELINHA", sigla ou nome próprio sem marca denominacional. Isso é uma proporção honesta, não um erro: não se deve interpretar as proporções entre vertentes *classificadas* como estimativa não-enviesada da proporção nacional real, porque denominações com marca consistente (Testemunhas de Jeová, Assembleia de Deus) são classificadas a uma taxa muito maior que igrejas independentes de nome genérico. Qualquer análise publicada deve reportar "não classificado" como categoria própria, não redistribuir/ignorar essa fatia.

   A mineração **reduz** esse viés mas não o elimina, e o desloca um pouco: como ela aprende do que já estava classificado, denominações já bem representadas ganham mais padrões novos que as sub-representadas. O grupo com maior ganho relativo foi Umbanda e Candomblé (+38%), mas por outro motivo — a correção de precedência do sincretismo (§4), não a mineração em si.

2. **A classificação de ~760 dos ~1.030 padrões é estatística, não documental.** Os padrões `mineracao_*` no dicionário não têm fonte externa: a evidência deles é o próprio corpus (coluna `fonte`, `confianca` derivada da pureza). São auditáveis linha a linha em `candidatos_padroes.csv`, que guarda ganho, pureza, suporte e exemplos reais de cada um. Quem quiser só o dicionário documental pode filtrar `fonte NOT LIKE 'mineracao_%'` e reaplicar com `reclassificar.py`.
3. **Vertente é heurística de texto, presença não é.** A distinção importa: um templo aparecer no dataset é garantido pelo critério oficial do IBGE; a denominação atribuída a ele é inferência nossa, auditável linha a linha em `cnefe-descricao-vertente.csv` (coluna `fonte`/`confianca`), mas não é um dado oficial.
4. **Diferença residual de 1,6% vs. o número oficial do IBGE** (570.428 vs. 579.800) não foi decomposta até a última unidade — pode ser efeito residual da lista de exclusões (que ainda opera por cima de `tipo_especie='8'`) ou diferença de metodologia/data de corte entre a extração local e a publicação oficial do IBGE.
5. **`com_cnae` mede formalização jurídica, não existência física** — um templo sem CNPJ é igualmente real; o selo só informa se *também* tem registro formal encontrável pelo endereço.
6. **Coordenadas**: 99,5% das linhas religiosas do CNEFE têm `nivel_geocodificacao_coordenadas=1` ("coordenada original do Censo 2022", GPS real de campo) — o restante usa coordenada estimada/interpolada (face de quadra, localidade, ou setor censitário), reportado por linha no parquet (`nivel_geocodificacao_coordenadas`), não descartado.

## 9. Estrutura de arquivos e reprodução

```
dataviz/religioes/
├── metodologia.md                       este arquivo
├── treeview-religioes.txt               taxonomia oficial (tabela 137) em árvore, leitura humana
├── dados/
│   ├── vertentes-religiosas.csv         taxonomia oficial (75 categorias, id/nivel/nome/id_pai)
│   ├── cnefe-descricao-vertente.csv     dicionário (padrão de texto → vertente_id | exclusão), ~1.030 linhas
│   ├── gerar_igrejas_geolocalizadas.py  pipeline de extração (roda via ssh beelink + DuckDB)
│   ├── minerar_padroes.py               minera padrões novos do que ficou sem classificação (§4.2)
│   ├── reclassificar.py                 reaplica o dicionário no parquet local, sem reconsultar o CNEFE
│   ├── gerar_data_json.py               rollup + paleta + legenda → igrejas/data.json
│   ├── candidatos_padroes.csv           saída de auditoria: cada padrão minerado com ganho/pureza/exemplos
│   ├── residuo_sem_classificacao.csv    saída de curadoria: o que sobrou sem proposta, por volume
│   ├── igrejas_geolocalizadas.parquet   dataset final (765.591 linhas), cópia local do output remoto
│   └── readme.md                        índice de todas as fontes de dados do projeto (não só templos)
└── igrejas/
    ├── index.html                       mapa Leaflet (camada canvas customizada, ~570k pontos)
    └── data.json                        extrato leve do parquet pro mapa (legenda + pontos + com_cnae)
```

**Para reproduzir do zero:**
1. `python3 dados/gerar_igrejas_geolocalizadas.py` (sem argumento = nacional; passe uma sigla de UF, ex. `SP`, pra rodar num recorte de teste primeiro) — requer acesso SSH ao host `beelink` com o mirror local da basedosdados em `~/rodado` e DuckDB com a extensão `spatial`.
2. `scp beelink:/tmp/igrejas_geolocalizadas.parquet dados/igrejas_geolocalizadas.parquet`
3. `python3 dados/gerar_data_json.py` (rollup + paleta + legenda → `igrejas/data.json`).
4. Abrir `igrejas/index.html` (servido por qualquer HTTP server estático — não funciona em `file://` por causa do `fetch('data.json')`).

**Para alterar a classificação de vertente**: editar `dados/cnefe-descricao-vertente.csv` diretamente (é um CSV comum, git-diffável), depois `python3 dados/reclassificar.py && python3 dados/gerar_data_json.py` — não precisa refazer o passo 1, que é caro e depende do beelink. `reclassificar.py --dry-run` mostra o diff (quantos entram, quantos trocam de vertente) antes de gravar. Regra de ouro: toda linha nova deve citar `fonte` real (não adicionar padrão sem saber de onde veio a certeza) e, se a denominação não for autoexplicativa pelo nome, pesquisar antes de classificar.

**Para propor padrões novos a partir do que ficou sem classificação**: `python3 dados/minerar_padroes.py` escreve `candidatos_padroes.csv` sem tocar em nada; revise e rode com `--aplicar`. `--validar` mede a precisão por holdout (§4.2).

## 10. Resumo do histórico (para quem for revisar o diff)

1. Primeira versão: geolocalização via CNPJ (CEP → centroide), classificação por CNAE + nome — abandonada por baixa cobertura de coordenada por CEP (90,8%) e granularidade grosseira.
2. Trocado pra CNEFE (endereço real, GPS de campo) — cobertura de coordenada foi a 100% dos candidatos.
3. Seleção de candidatos por texto livre, ~700k linhas, ~20% acima do IBGE oficial.
4. Duas rodadas de exclusão manual de falsos positivos (café, cemitério, prédio de governo, anexo de igreja) — reduziu mas não fechou o gap.
5. Auditoria de segunda opinião (Fable) — achou contaminação de "Mesquita"/sobrenome e anexo paroquial contado como templo; aplicado após reconferência manual.
6. Descoberta do campo oficial `tipo_especie='8'` do CNEFE — trocado como critério único de presença; gap caiu de ~17% para 1,6%. Dicionário de texto passou a servir só pra classificar vertente, não mais pra selecionar quem entra.
7. `com_cnae` corrigido (exigindo também nome do logradouro no join) depois de descoberto que o join anterior (só CEP+número) gerava falso match em endereço rural.
8. Investigado por que só 4,6% batiam: descoberto que só 30,5% dos CNPJs religiosos do país acham qualquer correspondência de endereço completo no CNEFE — não por diferença de grafia (ruas genuinamente diferentes colidindo em CEP+número), então normalização de string não ajudaria. Trocado pra correspondência por CEP com salvaguarda contra CEPs-outlier (máx. 15 templos por CEP contam como confirmação) — subiu pra 20,5% (116.887), mais realista.
9. Reincorporados os 195.163 templos "não oficiais" descartados no passo 6 (98,4% deles são `tipo_especie=6`, não uma categoria qualquer) como segunda camada explícita (`presenca='texto_livre'`), visualmente distinta no mapa, nunca somada aos oficiais sem essa distinção.
