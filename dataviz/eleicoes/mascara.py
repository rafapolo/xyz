"""Gera mascara.geojson: o "mundo menos o Brasil" que o mapa pinta por cima do basemap.

    ogr2ogr / mapshaper  ->  contorno simplificado do IBGE (GeoJSON)  ->  python mascara.py contorno.json

Contorno: malha BR_Pais_2022 do IBGE (geoftp.ibge.gov.br, malhas_municipais/municipio_2022/Brasil/BR),
simplificada com `mapshaper BR_Pais_2022.shp -simplify interval=60 keep-shapes -clean -o precision=0.0001`.

A máscara sai em pedaços sem furo: um polígono só, com o Brasil como furo, quebra a triangulação do
MapLibre nos tiles em que o litoral entra e sai várias vezes (a baía de Guanabara virava um retângulo
chapado). Primeiro uma grade de 2°, depois um corte vertical por dentro de cada ilha que sobrou como furo.
Os cortes são artificiais e o mapa precisa tirá-los do fio do contorno: os da grade caem em coordenadas
inteiras, os das ilhas na 5ª casa decimal (o contorno real só tem 4).
"""
import json, sys
from shapely.geometry import shape, box, Polygon

CELULA = 2
X0, X1, Y0, Y1 = -76, -28, -36, 6          # caixa em volta do país, alinhada à grade
MUNDO = (-179, -85, 179, 85)

g = json.load(open(sys.argv[1]))
brasil = shape(g.get('geometry', g)).buffer(0)

def partes(g): return [p for p in getattr(g, 'geoms', [g]) if p.geom_type == 'Polygon' and not p.is_empty]

def sem_furos(p):
    if not p.interiors: return [p]
    x0, y0, x1, y1 = p.bounds
    xc = round(Polygon(p.interiors[0]).centroid.x, 4) + 0.00005
    return [q for lado in (box(x0 - 1, y0 - 1, xc, y1 + 1), box(xc, y0 - 1, x1 + 1, y1 + 1))
            for parte in partes(p.intersection(lado)) for q in sem_furos(parte)]

pecas = [box(MUNDO[0], MUNDO[1], X0, MUNDO[3]), box(X1, MUNDO[1], MUNDO[2], MUNDO[3]),
         box(X0, MUNDO[1], X1, Y0), box(X0, Y1, X1, MUNDO[3])]
for x in range(X0, X1, CELULA):
    for y in range(Y0, Y1, CELULA):
        for p in partes(box(x, y, x + CELULA, y + CELULA).difference(brasil)):
            pecas += sem_furos(p)

coords = [[[[round(x, 5), round(y, 5)] for x, y in p.exterior.coords]] for p in pecas]
json.dump({'type': 'MultiPolygon', 'coordinates': coords}, open('mascara.geojson', 'w'), separators=(',', ':'))
print(len(coords), 'polígonos,', sum(len(a) for p in coords for a in p), 'vértices')
