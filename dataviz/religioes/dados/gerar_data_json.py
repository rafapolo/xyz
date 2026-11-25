import colorsys
import gzip
import hashlib
import json
from pathlib import Path

import numpy as np
import pandas as pd

HERE = Path(__file__).parent
PARQUET = HERE / "igrejas_geolocalizadas.parquet"
VERTENTES_CSV = HERE / "vertentes-religiosas.csv"
OUT_DIR = HERE.parent / "igrejas"
# o mapa baixa 3 arquivos: meta.json (legendas, totais, versões), pontos.bin.gz
# (posição + categorias, o necessário pra desenhar) e nomes.bin.gz (texto anotado
# em campo, só usado no tooltip — baixado depois que o mapa já está desenhado).
# Formato binário descrito em escrever_binarios().

# categorias "ancora" do legend grosso (nivel exibido por padrao no mapa) -
# mantidas identicas ao data.json ja publicado, pra nao regredir nada
COARSE_ANCHORS = [
    {"id": 95265, "nome": "Evangélica de origem pentecostal", "cor": "#2a78d6"},
    {"id": 95263, "nome": "Católica Apostólica Romana", "cor": "#eb6834"},
    {"id": 95264, "nome": "Evangélica de Missão", "cor": "#1baf7a"},
    {"id": 121096, "nome": "Evangélica não determinada", "cor": "#eda100"},
    {"id": 2826, "nome": "Espírita", "cor": "#e87ba4"},
    {"id": 2827, "nome": "Umbanda e Candomblé", "cor": "#008300"},
    {"id": 2824, "nome": "Testemunhas de Jeová", "cor": "#4a3aa7"},
]
OUTRAS_IDS = {100423, 100428, 95269, 95268, 95271}  # Mórmon, Messiânica, Budismo, Judaica, Islâmica
OUTRAS = {"id": -1, "nome": "Outras (Islâmica, Judaica, Budismo, Mórmon, Novas religiões orientais)", "cor": "#e34948"}
NAO_CLASSIFICADO = {"id": 0, "nome": "Não classificado", "cor": "#8a8a86"}


def carregar_vertentes():
    df = pd.read_csv(VERTENTES_CSV)
    by_id = {}
    for _, r in df.iterrows():
        pai = r["id_pai"]
        by_id[int(r["id"])] = {
            "nome": r["nome"],
            "id_pai": None if pd.isna(pai) else int(pai),
        }
    return by_id


def coarse_bucket(vertente_id, by_id):
    if vertente_id is None:
        return "NAO_CLASSIFICADO"
    anchors = {a["id"] for a in COARSE_ANCHORS}
    cur = int(vertente_id)
    seen = set()
    while cur is not None and cur not in seen:
        if cur in anchors:
            return cur
        seen.add(cur)
        node = by_id.get(cur)
        cur = node["id_pai"] if node else None
    if int(vertente_id) in OUTRAS_IDS:
        return "OUTRAS"
    return "OUTRAS"  # fallback de seguranca; nao deveria disparar (cobertura verificada manualmente)


def nome_fino(vertente_id, by_id):
    node = by_id.get(int(vertente_id))
    nome = node["nome"] if node else str(vertente_id)
    if " - " in nome:
        nome = nome.split(" - ", 1)[1]
    return nome


def hex_to_hsl(hex_color):
    v = int(hex_color[1:], 16)
    r, g, b = (v >> 16 & 255) / 255, (v >> 8 & 255) / 255, (v & 255) / 255
    h, l, s = colorsys.rgb_to_hls(r, g, b)
    return h, s, l


def hsl_to_hex(h, s, l):
    r, g, b = colorsys.hls_to_rgb(h % 1.0, max(0, min(1, l)), max(0, min(1, s)))
    return "#%02x%02x%02x" % (round(r * 255), round(g * 255), round(b * 255))


def van_der_corput(k, base=2):
    """Sequencia de baixa discrepancia: os primeiros valores ja saem bem
    espalhados em [0,1) (0, 0.5, 0.25, 0.75, 0.125...), ao contrario de uma
    rampa linear onde os indices vizinhos (ex. os dois maiores membros de uma
    familia, i=0 e i=1) saem quase identicos."""
    vdc, denom = 0.0, 1.0
    while k > 0:
        k, rem = divmod(k, base)
        denom *= base
        vdc += rem / denom
    return vdc


def paleta_familia(cor_base, n):
    """Gera n variantes de uma cor-ancora: o maior membro da familia fica
    exatamente na cor-ancora (continuidade visual com o modo grosso); os
    demais se espalham em luminosidade/matiz/saturacao via sequencias de Van
    der Corput (bases distintas por eixo, pra nao correlacionar) em vez de uma
    rampa linear, que colapsava indices vizinhos em cores quase iguais."""
    h, s, l = hex_to_hsl(cor_base)
    if n == 1:
        return [cor_base]
    cores = [cor_base]
    for i in range(1, n):
        lig = 0.30 + 0.46 * van_der_corput(i, 2)
        hue = h + (van_der_corput(i, 3) - 0.5) * 0.11
        sat = min(1, s * (0.82 + 0.30 * van_der_corput(i, 5)))
        cores.append(hsl_to_hex(hue, sat, lig))
    return cores


def main():
    df = pd.read_parquet(PARQUET)
    by_id = carregar_vertentes()

    # --- categoria grossa (legend atual, 9 categorias) ---
    coarse_index = {a["id"]: i for i, a in enumerate(COARSE_ANCHORS)}
    coarse_index["OUTRAS"] = len(COARSE_ANCHORS)
    coarse_index["NAO_CLASSIFICADO"] = len(COARSE_ANCHORS) + 1
    coarse_legend_meta = COARSE_ANCHORS + [OUTRAS, NAO_CLASSIFICADO]

    def coarse_bucket_row(v):
        if pd.isna(v):
            return "NAO_CLASSIFICADO"
        return coarse_bucket(v, by_id)

    df["coarse_key"] = df["vertente_id"].map(coarse_bucket_row)
    df["coarse_idx"] = df["coarse_key"].map(coarse_index)

    coarse_counts = df["coarse_key"].value_counts()

    def key_for_anchor(a, i):
        return a["id"] if i < len(COARSE_ANCHORS) else ("OUTRAS" if a is OUTRAS else "NAO_CLASSIFICADO")

    legend_coarse = []
    for i, a in enumerate(coarse_legend_meta):
        key = key_for_anchor(a, i)
        legend_coarse.append({
            "idx": i, "id": a["id"], "nome": a["nome"], "cor": a["cor"],
            "n": int(coarse_counts.get(key, 0)),
        })

    # --- categoria fina (denominacao especifica, nomenclatura censo 2010) ---
    df["fina_key"] = df["vertente_id"].apply(lambda v: "NAO_CLASSIFICADO" if pd.isna(v) else int(v))
    fina_counts = df["fina_key"].value_counts()

    # agrupa ids finos por familia (ancora grossa) pra gerar paleta coerente
    familia_de_id = {}
    for vid in fina_counts.index:
        if vid == "NAO_CLASSIFICADO":
            continue
        familia_de_id[vid] = coarse_bucket(vid, by_id)

    from collections import defaultdict
    membros_por_familia = defaultdict(list)
    for vid, fam in familia_de_id.items():
        membros_por_familia[fam].append(vid)

    cor_por_id = {}
    for fam, membros in membros_por_familia.items():
        membros.sort(key=lambda v: -fina_counts[v])
        cor_ancora = next((a["cor"] for a in COARSE_ANCHORS if a["id"] == fam), OUTRAS["cor"] if fam == "OUTRAS" else "#999999")
        cores = paleta_familia(cor_ancora, len(membros))
        for vid, cor in zip(membros, cores):
            cor_por_id[vid] = cor

    fina_ids_ordenados = sorted(
        [k for k in fina_counts.index if k != "NAO_CLASSIFICADO"],
        key=lambda v: -fina_counts[v],
    )
    fina_index = {}
    legend_fina = []
    for i, vid in enumerate(fina_ids_ordenados):
        fina_index[vid] = i
        legend_fina.append({
            "idx": i, "id": int(vid), "nome": nome_fino(vid, by_id),
            "cor": cor_por_id[vid], "n": int(fina_counts[vid]),
            "coarseIdx": coarse_index[familia_de_id[vid]] if familia_de_id[vid] != "OUTRAS" else coarse_index["OUTRAS"],
        })
    fina_index["NAO_CLASSIFICADO"] = len(legend_fina)
    legend_fina.append({
        "idx": len(legend_fina), "id": 0, "nome": "Não classificado", "cor": "#8a8a86",
        "n": int(fina_counts.get("NAO_CLASSIFICADO", 0)),
        "coarseIdx": coarse_index["NAO_CLASSIFICADO"],
    })

    df["fina_idx"] = df["fina_key"].map(fina_index)

    totais = {
        "comCnaeTotal": int(df["com_cnae"].sum()),
        "oficialTotal": int((df["presenca"] == "oficial").sum()),
        "textoLivreTotal": int((df["presenca"] == "texto_livre").sum()),
    }
    escrever_binarios(df, legend_coarse, legend_fina, totais)

    print("coarse:", [(l["nome"], l["n"]) for l in legend_coarse])
    print()
    print("fina (top 15):", [(l["nome"], l["n"]) for l in legend_fina[:15]])
    print()
    print("total pontos:", len(df))


def _morton(x, y):
    """Intercala os bits de x e y: pontos vizinhos no mapa ficam vizinhos no
    arquivo, o que deixa os deltas pequenos e o gzip eficiente."""
    def spread(v):
        v = v.astype(np.uint64) & np.uint64(0xFFFFFFFF)
        for sh, m in ((16, 0x0000FFFF0000FFFF), (8, 0x00FF00FF00FF00FF), (4, 0x0F0F0F0F0F0F0F0F),
                      (2, 0x3333333333333333), (1, 0x5555555555555555)):
            v = (v | (v << np.uint64(sh))) & np.uint64(m)
        return v
    return spread(x) | (spread(y) << np.uint64(1))


def _zigzag_delta(a):
    d = np.diff(a.astype(np.int64), prepend=0).astype(np.int32)
    return ((d << 1) ^ (d >> 31)).view(np.uint32)


def _planos(a):
    """Byte-shuffle: todos os bytes 0, depois todos os bytes 1... — os bytes
    altos dos deltas são quase sempre zero e o gzip os comprime a quase nada."""
    return a.view(np.uint8).reshape(-1, a.itemsize).T.tobytes()


def _gz(b):
    return gzip.compress(b, compresslevel=9, mtime=0)


def escrever_binarios(df, legend_coarse, legend_fina, totais):
    """pontos.bin.gz (n = meta.n), tudo little-endian:
         dlat  4n bytes  delta zigzag de round(lat*1e5), em planos de byte
         dlon  4n bytes  idem para lon
         coarse n bytes, fina n bytes, flags n bytes (bit0 = com_cnae, bit1 = oficial)
       nomes.bin.gz:
         idx   4n bytes  índice em `nomes` (uint32, em planos de byte), mesma ordem
         texto utf-8 com os nomes únicos (ordem alfabética) separados por \\n
       Ordem dos pontos = ordem de desenho: categoria grossa da maior pra menor
       (as menores ficam por cima) e Morton dentro de cada categoria."""
    lat = np.round(df["lat"].to_numpy(dtype=np.float64) * 1e5).astype(np.int64)
    lon = np.round(df["lon"].to_numpy(dtype=np.float64) * 1e5).astype(np.int64)
    coarse = df["coarse_idx"].to_numpy().astype(np.uint8)
    fina = df["fina_idx"].to_numpy().astype(np.uint8)
    flags = (df["com_cnae"].eq(True).to_numpy().astype(np.uint8)
             | ((df["presenca"] == "oficial").to_numpy().astype(np.uint8) << 1))

    rank = np.empty(len(legend_coarse), dtype=np.int64)
    for r, l in enumerate(sorted(legend_coarse, key=lambda l: -l["n"])):
        rank[l["idx"]] = r
    ordem = np.lexsort((_morton(lon - lon.min(), lat - lat.min()), rank[coarse]))

    nomes_brutos = df["descricao_estabelecimento"].fillna("").to_numpy()
    nomes = sorted(set(nomes_brutos.tolist()))
    assert not any("\n" in s for s in nomes)
    pos_nome = {s: i for i, s in enumerate(nomes)}
    idx_nome = np.fromiter((pos_nome[s] for s in nomes_brutos), dtype=np.uint32, count=len(nomes_brutos))

    pontos = _gz(_planos(_zigzag_delta(lat[ordem])) + _planos(_zigzag_delta(lon[ordem]))
                 + coarse[ordem].tobytes() + fina[ordem].tobytes() + flags[ordem].tobytes())
    nomes_gz = _gz(_planos(idx_nome[ordem]) + "\n".join(nomes).encode("utf-8"))

    versao = lambda b: hashlib.sha1(b).hexdigest()[:10]
    (OUT_DIR / "pontos.bin.gz").write_bytes(pontos)
    (OUT_DIR / "nomes.bin.gz").write_bytes(nomes_gz)
    meta = {
        "n": int(len(df)),
        "legend": legend_coarse,
        "legendFina": legend_fina,
        **totais,
        "v": {"pontos": versao(pontos), "nomes": versao(nomes_gz)},
    }
    with open(OUT_DIR / "meta.json", "w", encoding="utf-8") as f:
        json.dump(meta, f, ensure_ascii=False, separators=(",", ":"))
    print(f"pontos.bin.gz {len(pontos):,} B | nomes.bin.gz {len(nomes_gz):,} B | nomes únicos {len(nomes):,}")


if __name__ == "__main__":
    main()
