# Mapas — migração CartoDB → OpenFreeMap

Em 2026-09 a CARTO descontinuou seus tiles gratuitos anônimos (`basemaps.cartocdn.com`):
as requisições continuam devolvendo HTTP 200, mas com um watermark de "api key required"
embutido no tile. Todo mapa do `dataviz/` que dependia desses tiles foi migrado para
[OpenFreeMap](https://openfreemap.org) (vetorial, dado OSM, sem API key, sem rate limit),
mesmo fix já aplicado no [swissviz](https://github.com/rafapolo/swissviz) (`d78df54`).

| Página | URL | O que é |
|---|---|---|
| [eleicoes](../dataviz/eleicoes/) | `/dataviz/eleicoes/` | Inclinação e polarização ideológica do voto por município (prefeitos 2024) — Leaflet + estilo `dark` do OpenFreeMap via `maplibre-gl-leaflet` |
| [religioes](../dataviz/religioes/) | `/dataviz/religioes/` | Perfil religioso dominante por município (Censo IBGE 2010/2022) — mesma ponte Leaflet/OpenFreeMap |
| [religioes/igrejas](../dataviz/religioes/igrejas/) | `/dataviz/religioes/igrejas/` | 765 mil templos religiosos do CNEFE por vertente — MapLibre puro, estilo `dark` trocado direto (era raster CartoDB inline) |
| [racas](../dataviz/racas/) | `/dataviz/racas/` | Cor/raça autodeclarada dominante por município — estilo `positron` (claro) do OpenFreeMap, mantém o filtro CSS duotone azul |
| [uf/{estado}](../dataviz/uf/) | `/dataviz/uf/{uf}/` (28 páginas + `br`) | Cada CNPJ ativo como ponto, por UF — basemap removido de vez: só pintava tudo de preto mesmo, agora é fundo sólido sem fetch externo |
| [rais/mapa](../dataviz/rais/mapa/) | `/dataviz/rais/mapa/` | Atlas salarial (RAIS 2020–2024) por município, coroplético — estilo `dark` do OpenFreeMap, tint por camada corrigido (checava `type:'raster'` contra um estilo vetorial, nunca rodava) |
| [rio/ibge](../dataviz/rio/ibge.html) | `/dataviz/rio/ibge.html` | Estabelecimentos do Rio de Janeiro por CNAE (IBGE) — export kepler.gl, URL de estilo trocada dentro do bundle minificado |
| [rio/confeccoes](../dataviz/rio/confeccoes.html) | `/dataviz/rio/confeccoes.html` | Confecções ativas no Rio de Janeiro — mesmo export kepler.gl, mesma troca de URL |
| [friba/friba-igrejas](../dataviz/friba/friba-igrejas.html) | `/dataviz/friba/friba-igrejas.html` | Templos religiosos de Nova Friburgo por denominação — export kepler.gl |
| [friba/friba-madeiras](../dataviz/friba/friba-madeiras.html) | `/dataviz/friba/friba-madeiras.html` | Madeireiras/serrarias de Nova Friburgo — export kepler.gl |
| [friba/pop_3d](../dataviz/friba/pop_3d.html) | `/dataviz/friba/pop_3d.html` | População de Nova Friburgo em colunas 3D — export kepler.gl |
| [friba/friburgo-confeccoes-ativas](../dataviz/friba/friburgo-confeccoes-ativas.html) | `/dataviz/friba/friburgo-confeccoes-ativas.html` | Confecções ativas em Nova Friburgo — export kepler.gl |

## Fora do escopo (não usam basemap)

`rodado/pages/analises` (repo irmão) não tem mapa interativo nenhum — "mapa" nos títulos
(`mapa-da-saude-mental`) é figura de linguagem, e as imagens com "mapa" no nome são PNG/JPG
estáticos sem Leaflet/MapLibre/CartoDB envolvido.

## Detalhes técnicos

- Commit: `fix: replace deprecated cartodb basemap tiles with openfreemap` (`xyz@d330333`)
- `eleicoes`, `religioes`, `racas` (Leaflet): ponte via `@maplibre/maplibre-gl-leaflet`
  para não reescrever markers/tooltips/controles existentes
- `religioes/igrejas`, `rais/mapa` (MapLibre nativo): troca direta de `style:`
- `uf/map.js`: único caso sem basemap nenhum — a pedido, já que só existia pra ser
  achatado em preto sólido pelo `hideRoads()`
- `rio/*.js`, `friba/*.html`: exports kepler.gl de 11–57MB sem fonte separada,
  patch feito com `sed` nas 6 URLs de estilo embutidas no bundle minificado
- Variantes "nolabels" do CartoDB (`dark-matter-nolabels`, `positron-nolabels`,
  `voyager-nolabels`) caem no estilo com label — OpenFreeMap não publica versão sem label
- `voyager` (CartoDB) mapeado para `bright` (OpenFreeMap), aproximação mais próxima disponível
