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
