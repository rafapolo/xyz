# Polarização nas Eleições Municipais 2024 — Metodologia

## O que o mapa mostra

Um ponto por município (5.557 com voto e centroide válidos), colorido pela **distribuição
do voto para prefeito no 1º turno de 2024** — deliberadamente **não** pela sigla de quem
venceu. Dois modos alternáveis:

- **Inclinação** (diverging vermelho↔azul): posição ideológica média do voto. Vermelho =
  município que votou mais à esquerda, azul = mais à direita, pálido = centro.
- **Polarização** (sequencial plasma): quão disperso ideologicamente foi o voto. Escuro =
  consenso (voto concentrado num ponto do espectro), claro/amarelo = voto rachado entre
  esquerda e direita.

## Por que não colorir pelo vencedor

Colorir pela sigla do prefeito eleito trata 51×49 e 90×10 como idênticos e joga fora
justamente o sinal de polarização. Além disso, a legenda partidária municipal é um sinal
ideológico fraco: o "centrão" (MDB, PSD, União, PP, Republicanos) elege a maioria das
prefeituras e é localmente fluido. Por isso agregamos **todo** o voto ponderando cada
candidato pela ideologia do seu partido.

## Nota ideológica dos partidos (0 = esquerda, 10 = direita)

Base: survey de especialistas de **Bolognesi, Ribeiro & Codato**, "A New Ideological
Mapping of Brazilian Parties" — posições médias atribuídas por cientistas políticos.
Partidos novos/pequenos fora do survey (PRD, MOBILIZA, PMB, AGIR, DC, UP) foram
posicionados por continuidade com as siglas de origem e por padrão de coligação; estão
marcados com `*` e pesam pouco no total (voto marginal).

**Override do PL → 8.5 (nota `†`):** o survey foi aplicado em 2018, *antes* de Jair
Bolsonaro migrar para o PL (2021). A nota original o colocava como centro-direita
fisiológico. De 2022 em diante o PL passou a ser o veículo eleitoral do bolsonarismo — a
legenda-nave da direita radical — então é reposicionado acima do NOVO (direita liberal,
8.2) como o partido mais à direita do espectro. É o maior partido em votos (15,6M), então
o override afeta o mapa de forma perceptível.

| Partido | Nota | | Partido | Nota |
|---|---|---|---|---|
| PCO | 0.3 | | PSD | 5.9 |
| PCB | 0.5 | | AGIR* | 6.0 |
| UP* | 0.5 | | PSDB | 6.0 |
| PSTU | 0.6 | | PRD* | 6.8 |
| PSOL | 1.3 | | UNIÃO | 6.9 |
| PC do B | 1.7 | | PP | 7.0 |
| PT | 2.5 | | REPUBLICANOS | 7.2 |
| REDE | 3.3 | | DC* | 7.5 |
| PDT | 3.3 | | PRTB | 8.0 |
| PSB | 3.7 | | NOVO | 8.2 |
| PV | 4.1 | | PL† | 8.5 |
| CIDADANIA | 4.6 | | | |
| SOLIDARIEDADE | 5.4 | | | |
| MDB / PODE | 5.7 | | | |
| AVANTE | 5.6 | | | |
| PMB* / MOBILIZA* | 5.5 | | | |

## Cálculo por município

Para cada município, sobre os votos de prefeito no 1º turno de 2024:

- **Inclinação (lean)** = média dos scores ponderada pelos votos:
  `Σ(votos_p · score_p) / Σ votos_p`
- **Polarização** = desvio-padrão dos scores ponderado pelos votos:
  `sqrt( Σ(votos_p · score_p²)/Σvotos_p − lean² )`
  Alto quando o voto se divide entre extremos (ex.: PT vs PL); baixo quando se concentra
  num ponto do espectro, mesmo numa disputa apertada.
- **Blocos** (tooltip): esquerda = score < 4.0; centro = 4.0–6.0; direita > 6.0.
- **Margem 1º–2º**: diferença percentual entre os dois candidatos mais votados
  (competitividade da disputa, distinta da polarização ideológica).

## Ressalvas importantes

1. **Polarização ≠ disputa apertada.** Um município onde MDB e PSD (ambos centro) fazem
   50×50 tem margem apertada mas polarização ideológica **baixa** — corretamente. A
   polarização mede distância no espectro, não competitividade. A margem 1º–2º cobre o
   segundo conceito no tooltip.
2. **1º turno** é usado sempre (mesmo em capitais com 2º turno), porque contém o leque
   completo de candidatos — necessário para medir a dispersão real do voto.
3. **Scores são de especialistas, não uma verdade objetiva.** Refletem o posicionamento
   médio percebido de cada legenda nacionalmente; um mesmo partido pode ser mais à
   esquerda ou à direita localmente. Todas as notas ficam auditáveis na tabela acima.
4. **Município ≠ candidato.** A nota herda do partido, não da biografia do candidato.

## Fontes e reprodução

- Votos: TSE via basedosdados `br_tse_eleicoes.resultados_candidato_municipio`
  (ano 2024, cargo `prefeito`, turno 1), espelhada localmente em parquet.
- Centroides: `br_bd_diretorios_brasil.municipio` (coluna `centroide`, GEOMETRY).
- A query completa (CTE de scores + agregação ponderada + join de centroide) está
  versionada; regenerar `data.json` a partir dela reproduz o mapa.

---

# Presidente 2026 — 1º turno (04/10/2026)

O seletor **Eleição** abre o mesmo mapa com o voto para presidente
(`?eleicao=presidente-2026`, o padrão; `?eleicao=prefeitos-2024` para o mapa acima).

- **Lula × Flávio** (modo padrão): diferença, em pontos percentuais dos votos válidos,
  entre Lula (PT) e Flávio Bolsonaro (PL), os dois que vão ao 2º turno de 25/10.
  Vermelho = Lula à frente, azul = Flávio à frente, satura em ±40 pontos.
- **Inclinação** e **Polarização**: o mesmo cálculo de 2024, sobre os 12 candidatos, com a
  nota do partido de cada um. Duas siglas que não existiam no survey nem em 2024:
  **MISSÃO\*** (Renan Santos, 2,2%) → 7,8, direita liberal de origem no MBL, entre
  REPUBLICANOS e NOVO; **DEMOCRATA\*** (Wilson Grassi, 0,01%) → 5,0, neutro por falta de
  posição conhecida — o voto é desprezível.
- **A polarização aqui não é um sinal independente.** PT (2,5) e PL (8,5) somam 92% do voto,
  então todo município fica entre 2,2 e 3,0 e a dispersão é quase só função da margem entre
  os dois. A escala de cor usa esse intervalo (em 2024, 0 a 2,0).

## Fonte

- Votos: site de divulgação do TSE, `https://resultados.tse.jus.br/oficial/ele2026/6257/`
  (eleição 6257, cargo 1), um arquivo por município
  (`dados/<uf>/<uf><cod_tse>-c0001-e006257-u.json`), baixado em 06/10/2026 com 100% das
  seções totalizadas. O código TSE vira IBGE pelo `config/mun-e006257-cm.json`.
- 5.571 municípios; o exterior (`zz`, ~331 mil votos válidos) fica fora do mapa. A soma
  municipal (118.969.906 válidos) + exterior fecha com o total nacional (119.300.788).
- Centroides: `br_bd_diretorios_brasil.municipio`, como em 2024.
- `dados/presidente_2026/build.py` refaz `data_presidente_2026.json` (baixa o que falta,
  junta com os centroides no beelink). Os JSON brutos ficam em `raw/`, fora do git.

## Recorte por zona eleitoral

O seletor **Recorte** (`&recorte=zonas`) troca o ponto por município por um ponto por par
**município × zona eleitoral**, o grão do arquivo do TSE: 6.106 pontos, com as mesmas três
métricas e o mesmo filtro de vira-casacas.

- Todo município aparece. Os 190 que têm mais de uma zona se partem nelas (São Paulo em 57, o
  Rio em 49), e uma zona que cobre vários municípios pequenos vira um ponto em cada um. O
  tooltip diz quantas zonas o município tem e que outros municípios a zona cobre.
- **Votos:** `votacao_candidato_munzona_2026` dos dados abertos do TSE (arquivo `_BR`, o de
  presidente, gerado em 07/10/2026). A soma por município fecha voto a voto com o mapa por
  município; o gerador para se não fechar. Lula e Flávio vão com 2 casas: com 1, Canutama
  (AM), onde Flávio venceu por 2 votos, aparece empatada.
- **Ponto:** não há polígono de zona. O ponto é a mediana, ponderada pelo eleitorado de cada
  seção, das coordenadas dos locais de votação do município naquela zona
  (`eleitorado_local_votacao_2026`). Seções a mais de 250 km do centroide do próprio município
  são descartadas (762 de 514 mil; há local geocodificado em Bangladesh). Por isso o ponto cai
  onde se vota, e não no centroide do município: Almeirim (PA) fica na sede, à beira do
  Amazonas.
- **2022:** `br_tse_eleicoes.resultados_candidato_municipio_zona`. Houve rezoneamento, e um
  pedaço que ganhou ou perdeu seções mostraria virada que é só mudança de território. A
  comparação só entra quando o par (município, zona) existe em 2022 e o crescimento do voto
  dele ficou a ±10% do crescimento do município. Ficam de fora **72 pares**, quase todos em
  capitais e cidades grandes (São Paulo, Rio, Campinas, Joinville, Palhoça) e zonas novas.
- `dados/presidente_2026/build_zonas.py` refaz `data_presidente_2026_zonas.json` (1,1 MB,
  ~330 KB comprimido, só baixado ao abrir o recorte); os dois zips do TSE (~600 MB) ficam em
  `raw/`, fora do git.

## Recorte por seção eleitoral

O terceiro botão do **Recorte** (`&recorte=secoes`) desce até a urna.

- **Afastado**, um ponto por **local de votação** (77.932), com o voto somado das suas seções.
  **De perto** (a partir do zoom 12), cada local se abre nas suas **seções** (497.897), em
  espiral em volta da escola: todas as seções de um local têm a mesma coordenada, então a
  espiral é só para dar para ver e apontar cada uma. As seções de um estado baixam quando ele
  entra na tela a partir do zoom 8.
- **Votos:** `votacao_secao_2026_BR.zip` dos dados abertos do TSE (o `_BR` é o de presidente;
  os arquivos por UF trazem só os cargos estaduais). Fica de fora o votável 28 (Leonardo Alves
  de Araujo, candidatura indeferida, 5.246 votos que não entram como válidos); sem ele a soma das
  seções fecha voto a voto com a divulgação (118.969.906).
- **Coordenada e nome do local:** `eleitorado_local_votacao_2026`, com o mesmo descarte de
  geocodificação a mais de 250 km do município. 1.121 locais sem coordenada válida caem no ponto
  da sua zona naquele município.
- **Sem comparação com 2022:** o TSE renumera e redistribui seções entre eleições.
- `dados/presidente_2026/build_secoes.py` gera `secoes/locais.json` (colunar e em delta, ~1,1 MB
  comprimido) e um `secoes/<UF>.json` por estado (São Paulo, o maior, ~1,1 MB comprimido). O
  navegador calcula inclinação, polarização e vencedor a partir dos votos de cada candidato.
