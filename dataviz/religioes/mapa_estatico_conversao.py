import gzip
import json
import tempfile
from pathlib import Path

import geopandas as gpd
import matplotlib.pyplot as plt
import pandas as pd
from matplotlib.colors import LinearSegmentedColormap

HERE = Path(__file__).parent
DATA_PATH = HERE / "data.json"
MUNICIPIOS_GEOJSON_GZ = HERE.parent / "rais" / "mapa" / "dados" / "municipios.geojson.gz"
OUTPUT_PATH = HERE / "mapa_conversao_evangelica_2010_2022.png"

COLUMNS = [
    "uf", "municipio", "lat", "lon", "population",
    "catolica", "evangelicas", "espirita", "umbanda", "semreligiao", "bin",
]

MIN_DELTA = 10.0


def load_data_by_year():
    data = json.loads(DATA_PATH.read_text(encoding="utf-8"))
    frames = {}
    for year, records in data.items():
        df = pd.DataFrame(records, columns=COLUMNS)
        frames[year] = df
    return frames


def load_brazil_outline():
    with gzip.open(MUNICIPIOS_GEOJSON_GZ, "rb") as f_in:
        raw = f_in.read()
    with tempfile.NamedTemporaryFile(suffix=".geojson", delete=False) as tmp:
        tmp.write(raw)
        tmp_path = tmp.name
    return gpd.read_file(tmp_path)


def build_delta_frame(frames):
    df2010 = frames["2010"][["uf", "municipio", "evangelicas"]].rename(
        columns={"evangelicas": "evangelicas_2010"}
    )
    df2022 = frames["2022"][["uf", "municipio", "lat", "lon", "evangelicas"]].rename(
        columns={"evangelicas": "evangelicas_2022"}
    )
    merged = df2022.merge(df2010, on=["uf", "municipio"], how="inner")
    merged["delta"] = merged["evangelicas_2022"] - merged["evangelicas_2010"]
    merged = merged[merged["delta"] > MIN_DELTA]
    return merged.sort_values("delta", ascending=True)


def make_red_cmap():
    return LinearSegmentedColormap.from_list(
        "conversao_evangelica",
        ["#3a2a2a", "#7a1f1f", "#c81e1e", "#ff5a36", "#ffb347"],
    )


def plot(merged, brazil_outline):
    fig, ax = plt.subplots(figsize=(10, 11), dpi=200)
    fig.patch.set_facecolor("#0b0b0b")
    ax.set_facecolor("#0b0b0b")

    brazil_outline.plot(
        ax=ax, facecolor="#1a1a1a", edgecolor="#1a1a1a", linewidth=0.3, zorder=1
    )

    cmap = make_red_cmap()
    vmax = merged["delta"].max()
    sc = ax.scatter(
        merged["lon"], merged["lat"],
        c=merged["delta"], cmap=cmap, vmin=MIN_DELTA, vmax=vmax,
        s=6, linewidths=0, zorder=2,
    )

    ax.set_aspect("equal")
    ax.set_xticks([])
    ax.set_yticks([])
    for spine in ax.spines.values():
        spine.set_visible(False)

    cbar = fig.colorbar(sc, ax=ax, shrink=0.5, pad=0.02)
    cbar.set_label(
        "Crescimento da % Evangélica, 2010→2022 (p.p.)",
        color="#cccccc", fontsize=9,
    )
    cbar.ax.yaxis.set_tick_params(color="#cccccc", labelcolor="#cccccc")
    cbar.outline.set_edgecolor("#3a3a3a")

    ax.set_title(
        f"Municípios onde a % Evangélica cresceu mais de {MIN_DELTA:g} p.p. (2010–2022)",
        color="#eeeeee", fontsize=13, pad=14,
    )

    fig.tight_layout()
    fig.savefig(OUTPUT_PATH, facecolor=fig.get_facecolor())
    print(f"saved to {OUTPUT_PATH}")


def main():
    frames = load_data_by_year()
    merged = build_delta_frame(frames)
    brazil_outline = load_brazil_outline()
    plot(merged, brazil_outline)


if __name__ == "__main__":
    main()
