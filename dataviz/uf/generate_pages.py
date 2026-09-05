#!/usr/bin/env python3
"""Regenerate dataviz/uf/<uf>/index.html config pages from data/meta.json.

Run after data/meta.json changes (new UFs added, re-extraction). Pure
stdlib, no network access — reads meta.json, writes one tiny config page
per UF present in it.

Usage: python3 dataviz/uf/generate_pages.py
"""

import json
from pathlib import Path

ROOT = Path(__file__).parent
META_PATH = ROOT / "data" / "meta.json"

PAGE_TEMPLATE = """<!doctype html>
<html lang="pt-br">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>{title}</title>

  <!-- deck.gl + MapLibre only — same visual config (dark basemap, additive
       blending, color/radius/opacity/pitch) reverse-engineered from
       dataviz/rio/ibge-map.js, without kepler.gl's React/Redux/UI weight -->
  <link href="https://unpkg.com/maplibre-gl@3.4.0/dist/maplibre-gl.css" rel="stylesheet">
  <script src="https://unpkg.com/maplibre-gl@3.4.0/dist/maplibre-gl.js"></script>
  <script src="https://unpkg.com/deck.gl@9.0.0/dist.min.js"></script>

  <link rel="stylesheet" href="../map.css">
</head>
<body>
  <div id="map"></div>
  <div id="hud" class="uf-hud"></div>
  <div class="uf-brightness">
    <div class="uf-slider-row">
      <label for="opacity">opacidade</label>
      <input type="range" id="opacity" min="0.05" max="1" step="0.01" value="0.8">
    </div>
    <div class="uf-slider-row">
      <label for="brightness">brilho</label>
      <input type="range" id="brightness" min="0.02" max="2.5" step="0.01" value="1">
    </div>
    <div class="uf-slider-row">
      <label for="dotsize">tamanho</label>
      <input type="range" id="dotsize" min="0.1" max="2.5" step="0.01" value="1">
    </div>
    <div class="uf-zoom-row">zoom: <span id="zoomval">-</span></div>
  </div>
  <div id="loading" class="uf-loading"></div>
  <script>window.UF_CONFIG = {{ uf: "{uf}", title: "{title}" }};</script>
  <script src="../map.js"></script>
</body>
</html>
"""


def main():
    meta = json.loads(META_PATH.read_text())
    for uf in sorted(meta):
        label = "Brasil" if uf == "BR" else uf
        title = f"{label} · cada ponto é um CNPJ"
        out_dir = ROOT / uf.lower()
        out_dir.mkdir(exist_ok=True)
        (out_dir / "index.html").write_text(PAGE_TEMPLATE.format(uf=uf, title=title))
        print(f"  {out_dir}/index.html")
    print(f"Generated {len(meta)} state pages.")


if __name__ == "__main__":
    main()
