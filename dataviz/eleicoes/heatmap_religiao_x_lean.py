"""Heatmap do cruzamento perfil religioso (Censo 2022) x inclinacao/polarizacao
das prefeituras 2024.

Reconstroi a juncao usada em results/religiao_x_polarizacao.md e gera duas figuras:

  results/heatmap_religiao_x_lean.png         associacao religiao x eixo esq<->dir
  results/heatmap_religiao_x_polarizacao.png  o achado nulo (religiao x racha)

A cor de cada celula e o *residuo padronizado* (obs - esp)/sqrt(esp) sob
independencia, nao a contagem: um heatmap de densidade cru mostraria so a
distribuicao marginal de lean (unimodal em 5,5-6,5) e esconderia a associacao.
"""

import json
import textwrap
import unicodedata
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import polars as pl
from matplotlib.colors import LinearSegmentedColormap, Normalize

HERE = Path(__file__).parent
RELIGIOES_DATA = HERE.parent / "religioes" / "data.json"
PREFEITOS_DATA = HERE / "dados" / "prefeitos_2024_raw.json"
OUT_DIR = HERE / "results"

# colunas posicionais de religioes/data.json (ver religioes/mapa_estatico_conversao.py)
RELIGIOES_COLUMNS = [
    "uf", "municipio", "lat", "lon", "population",
    "catolica", "evangelicas", "espirita", "umbanda", "semreligiao", "bin",
]

REGIAO_POR_UF = {
    "AC": "Norte", "AP": "Norte", "AM": "Norte", "PA": "Norte",
    "RO": "Norte", "RR": "Norte", "TO": "Norte",
    "AL": "Nordeste", "BA": "Nordeste", "CE": "Nordeste", "MA": "Nordeste",
    "PB": "Nordeste", "PE": "Nordeste", "PI": "Nordeste", "RN": "Nordeste",
    "SE": "Nordeste",
    "DF": "Centro-Oeste", "GO": "Centro-Oeste", "MT": "Centro-Oeste",
    "MS": "Centro-Oeste",
    "ES": "Sudeste", "MG": "Sudeste", "RJ": "Sudeste", "SP": "Sudeste",
    "PR": "Sul", "RS": "Sul", "SC": "Sul",
}
REGIOES = ["Norte", "Nordeste", "Centro-Oeste", "Sudeste", "Sul"]

EVANG_BINS = [0, 15, 20, 25, 30, 35, 90]
LEAN_BINS = [2.5, 4.5, 5.0, 5.5, 6.0, 6.5, 7.0, 8.6]
POLAR_BINS = [0.0, 0.5, 0.75, 0.95, 1.15, 1.45, 3.3]

# Os paineis regionais usam bins grossos: com n regional, uma grade 6x7 vira campo
# de ruido ilegivel num painel de 3cm. Em 3x3 cada celula tem massa suficiente para
# o residuo ser estavel, e o gradiente (ou a ausencia dele) le de relance.
EVANG_BINS_REG = [0, 20, 30, 90]
LEAN_BINS_REG = [2.5, 5.5, 6.5, 8.6]
POLAR_BINS_REG = [0.0, 0.8, 1.15, 3.3]

MIN_ESPERADO = 5.0  # celulas com esperado abaixo disso saem hachuradas, sem cor
ZONA_MORTA = 1.3  # |z| abaixo disso e ruido amostral: fica cinza, sem cor

# paleta divergente azul<->vermelho com meio cinza neutro, passos para fundo escuro
DIVERGENTE = LinearSegmentedColormap.from_list(
    "residuo",
    ["#b7d3f6", "#5598e7", "#256abf", "#383835", "#b03e3d", "#e34948", "#ef8b89"],
)
DIVERGENTE.set_bad("#1e1e1e")


class NormaResiduo(Normalize):
    """Escala divergente com zona morta: |z| < ZONA_MORTA nao recebe cor.

    Sem isso, ruido amostral (|z| ~ 2) nos paineis regionais fica tao colorido
    quanto associacao real, e o painel do Sul - que e ruido - parece um padrao.
    """

    def __init__(self, vmax: float, morta: float = ZONA_MORTA, gama: float = 0.8):
        super().__init__(vmin=-vmax, vmax=vmax, clip=False)
        self.morta = morta
        self.gama = gama

    def __call__(self, value, clip=None):
        v = np.ma.asarray(value, dtype=float)
        forca = np.ma.clip((np.abs(v) - self.morta) / (self.vmax - self.morta), 0, 1)
        return np.ma.masked_array(
            (np.sign(v) * forca ** self.gama + 1) / 2, mask=np.ma.getmask(v)
        )

    def inverse(self, value):
        x = 2 * np.asarray(value, dtype=float) - 1
        return np.sign(x) * (np.abs(x) ** (1 / self.gama) * (self.vmax - self.morta)
                             + self.morta)

BG = "#0b0b0b"
INK = "#eeeeee"
INK_DIM = "#cccccc"
INK_FAINT = "#8a8a8a"
MONO = "JetBrains Mono"


def normalizar(nome: str) -> str:
    ascii_ = unicodedata.normalize("NFKD", nome).encode("ascii", "ignore").decode()
    return "".join(c for c in ascii_.lower() if c.isalnum())


def carregar() -> pl.DataFrame:
    """Junta censo religioso e eleicao por UF + nome normalizado."""
    religioes = json.loads(RELIGIOES_DATA.read_text(encoding="utf-8"))["2022"]
    rel = pl.DataFrame(religioes, schema=RELIGIOES_COLUMNS, orient="row").select(
        "uf", "municipio", "population", "catolica", "evangelicas",
        "espirita", "umbanda", "semreligiao",
    )
    rel = rel.with_columns(
        pl.col("municipio").map_elements(normalizar, return_dtype=pl.Utf8).alias("chave")
    )

    prefeitos = json.loads(PREFEITOS_DATA.read_text(encoding="utf-8"))
    ele = pl.DataFrame(prefeitos).select(
        "uf", "nome", "lean", "polar", "ncand", "pesq", "pcen", "pdir",
    )
    ele = ele.with_columns(
        pl.col("nome").map_elements(normalizar, return_dtype=pl.Utf8).alias("chave")
    )

    junto = ele.join(rel.drop("municipio"), on=["uf", "chave"], how="inner")
    junto = junto.with_columns(
        pl.col("uf").replace_strict(REGIAO_POR_UF).alias("regiao")
    )
    print(f"matched {junto.height}, missed {ele.height - junto.height}")
    return junto


def correlacoes(df: pl.DataFrame) -> None:
    """Reconfere os numeros publicados em §1 e §3 do relatorio."""
    print("\n§1 correlacoes nacionais (n={}):".format(df.height))
    for col in ["evangelicas", "catolica", "espirita", "semreligiao", "umbanda"]:
        r_lean = df.select(pl.corr(col, "lean")).item()
        r_polar = df.select(pl.corr(col, "polar")).item()
        print(f"  {col:<14} lean {r_lean:+.3f}   polar {r_polar:+.3f}")

    print("\n§3 r(evangelicas, lean) por regiao:")
    for regiao in REGIOES:
        sub = df.filter(pl.col("regiao") == regiao)
        print(f"  {regiao:<14} {sub.select(pl.corr('evangelicas', 'lean')).item():+.3f}"
              f"   (n={sub.height})")

    print("\n§6 correlacoes com polarizacao:")
    for col, expr in [
        ("ncand", pl.col("ncand").cast(pl.Float64)),
        ("log(pop)", pl.col("population").cast(pl.Float64).log()),
    ]:
        r = df.select(pl.corr(expr, pl.col("polar"))).item()
        print(f"  {col:<14} {r:+.3f}")


def tabela_residuos(df: pl.DataFrame, coluna_x: str, bins_x: list[float],
                    bins_y: list[float] | None = None):
    """Retorna (residuos, pct_linha, contagens) para o cruzamento evangelicas x coluna_x.

    residuos vem como masked array: celulas com esperado < MIN_ESPERADO ficam
    mascaradas para nao virarem cor forte em cima de ruido amostral.
    """
    y = np.asarray(df["evangelicas"])
    x = np.asarray(df[coluna_x])
    contagens, _, _ = np.histogram2d(y, x, bins=[bins_y or EVANG_BINS, bins_x])

    n = contagens.sum()
    linhas = contagens.sum(axis=1, keepdims=True)
    colunas = contagens.sum(axis=0, keepdims=True)
    esperado = linhas * colunas / n

    with np.errstate(divide="ignore", invalid="ignore"):
        residuos = (contagens - esperado) / np.sqrt(esperado)
        pct_linha = 100 * contagens / linhas
    residuos = np.ma.masked_where(esperado < MIN_ESPERADO, np.nan_to_num(residuos))
    pct_linha = np.nan_to_num(pct_linha)
    return residuos, pct_linha, contagens


def rotulos_y(bins: list[float] | None = None) -> list[str]:
    bins = bins or EVANG_BINS
    fim = len(bins) - 1
    return [
        f"{bins[i]}-{bins[i + 1]}%" if i < fim - 1 else f"{bins[i]}%+"
        for i in range(fim)
    ]


def rotulos_x(bins: list[float], casas: int = 1) -> list[str]:
    fim = len(bins) - 1
    fmt = lambda v: f"{v:.{casas}f}".replace(".", ",")
    saida = []
    for i in range(fim):
        if i == 0:
            saida.append(f"<{fmt(bins[1])}")
        elif i == fim - 1:
            saida.append(f"{fmt(bins[i])}+")
        else:
            saida.append(f"{fmt(bins[i])}-{fmt(bins[i + 1])}")
    return saida


def desenhar_painel(ax, residuos, norma, titulo, subtitulo=None, pct=None,
                    rot_x=None, rot_y=None, tam_rotulo=8, tam_titulo=11,
                    dy_titulo=0.075):
    ax.set_facecolor("#151515")
    im = ax.imshow(
        residuos, cmap=DIVERGENTE, norm=norma,
        origin="lower", aspect="auto", interpolation="nearest",
    )
    # celulas mascaradas: hachura discreta, sinalizando "n insuficiente"
    for (i, j), _ in np.ndenumerate(residuos):
        if np.ma.is_masked(residuos[i, j]):
            ax.add_patch(plt.Rectangle(
                (j - 0.5, i - 0.5), 1, 1, fill=False, hatch="////",
                edgecolor="#3a3a3a", linewidth=0,
            ))

    nlinhas, ncols = residuos.shape
    ax.set_xticks(range(ncols))
    ax.set_yticks(range(nlinhas))
    ax.set_xticklabels(rot_x if rot_x is not None else [], fontsize=tam_rotulo,
                       color=INK_DIM, fontfamily=MONO)
    ax.set_yticklabels(rot_y if rot_y is not None else [], fontsize=tam_rotulo,
                       color=INK_DIM, fontfamily=MONO)
    ax.tick_params(length=0, pad=4)
    for spine in ax.spines.values():
        spine.set_visible(False)
    # separador de 1px entre celulas, no tom do fundo
    ax.set_xticks(np.arange(-0.5, ncols, 1), minor=True)
    ax.set_yticks(np.arange(-0.5, nlinhas, 1), minor=True)
    ax.grid(which="minor", color=BG, linewidth=1.4)
    ax.tick_params(which="minor", length=0)

    if pct is not None:
        for (i, j), valor in np.ndenumerate(pct):
            if np.ma.is_masked(residuos[i, j]):
                continue
            forte = abs(norma(residuos[i, j]) - 0.5) > 0.28
            ax.text(j, i, f"{valor:.0f}", ha="center", va="center",
                    fontsize=8.5, fontfamily=MONO,
                    color="#ffffff" if forte else INK_FAINT)

    ax.text(0, 1 + dy_titulo, titulo, transform=ax.transAxes, color=INK,
            fontsize=tam_titulo, va="baseline")
    if subtitulo:
        ax.text(1, 1 + dy_titulo, subtitulo, transform=ax.transAxes,
                color=INK_FAINT, fontsize=tam_rotulo, fontfamily=MONO,
                va="baseline", ha="right")
    return im


def barra_de_cor(fig, im, retangulo, ticks, rotulo, tam=8.2):
    cax = fig.add_axes(retangulo)
    cb = fig.colorbar(im, cax=cax, orientation="horizontal", extend="both",
                      ticks=ticks)
    cb.ax.tick_params(color=INK_FAINT, labelcolor=INK_FAINT, labelsize=7.5,
                      length=0, pad=3)
    for rot in cb.ax.get_xticklabels():
        rot.set_fontfamily(MONO)
    cb.outline.set_visible(False)
    # rotulo como texto solto e alinhado a esquerda: set_label centraliza no eixo
    # e transborda a barra quando tem mais de uma linha
    fig.text(retangulo[0], retangulo[1] - 0.032, rotulo, color=INK_DIM,
             fontsize=tam, va="top", linespacing=1.55)
    return cb


def paragrafos(texto: str, largura: int) -> str:
    """Reflui cada paragrafo, preservando as linhas em branco entre eles."""
    return "\n\n".join(
        textwrap.fill(p, largura) for p in texto.split("\n\n")
    )


def figura(df: pl.DataFrame, coluna_x: str, bins_x: list[float],
           bins_reg_x: list[float], casas_x: int,
           titulo: str, subtitulo: str, rotulo_eixo: str, seta_esq: str,
           seta_dir: str, nota: str, rodape: str, vmax_br: float, vmax_reg: float,
           ticks_br: list[float], ticks_reg: list[float], destino: Path) -> None:
    plt.rcParams["font.family"] = "DejaVu Sans"
    fig = plt.figure(figsize=(14.0, 9.6), dpi=200)
    fig.patch.set_facecolor(BG)

    rot_x = rotulos_x(bins_x, casas_x)
    rot_x_reg = rotulos_x(bins_reg_x, casas_x)
    norma_br = NormaResiduo(vmax_br)
    norma_reg = NormaResiduo(vmax_reg)

    fig.text(0.055, 0.965, titulo, color=INK, fontsize=18, va="top")
    fig.text(0.055, 0.922, subtitulo, color=INK_FAINT, fontsize=10, va="top")

    # --- painel Brasil -----------------------------------------------------
    ax_br = fig.add_axes([0.055, 0.500, 0.415, 0.355])
    res_br, pct_br, cont_br = tabela_residuos(df, coluna_x, bins_x)
    im_br = desenhar_painel(
        ax_br, res_br, norma_br, "Brasil",
        subtitulo="{:,} municípios".format(int(cont_br.sum())).replace(",", "."),
        pct=pct_br, rot_x=rot_x, rot_y=rotulos_y(), tam_rotulo=8.5,
        tam_titulo=12.5, dy_titulo=0.04,
    )
    ax_br.set_ylabel("% evangélica no município (Censo 2022)", color=INK_DIM,
                     fontsize=9.5, labelpad=8)
    ax_br.text(0.5, -0.135, f"{seta_esq}   ·   {rotulo_eixo}   ·   {seta_dir}",
               transform=ax_br.transAxes, color=INK_DIM, fontsize=9.5,
               ha="center", va="top")

    barra_de_cor(
        fig, im_br, [0.525, 0.470, 0.28, 0.013], ticks_br,
        "resíduo padronizado: municípios a mais (vermelho)\n"
        "ou a menos (azul) que o esperado sob independência\n"
        f"|z| < {ZONA_MORTA:g} fica cinza — ruído amostral, não associação",
    )

    # --- bloco de texto ----------------------------------------------------
    fig.text(0.525, 0.855, paragrafos(nota, 66), color=INK_DIM, fontsize=9.5,
             va="top", linespacing=1.7)

    # --- painéis regionais -------------------------------------------------
    fig.text(0.055, 0.348, "Por região", color=INK, fontsize=13, va="baseline")
    fig.text(0.145, 0.348,
             "— mesma escala nos cinco painéis, nunca reescalada individualmente · "
             "faixas mais largas porque o n regional não sustenta a grade fina",
             color=INK_FAINT, fontsize=8.8, va="baseline")

    largura = (0.92 - 4 * 0.021) / 5
    im_reg = None
    for k, regiao in enumerate(REGIOES):
        ax = fig.add_axes([0.055 + k * (largura + 0.021), 0.178, largura, 0.135])
        sub = df.filter(pl.col("regiao") == regiao)
        res, pct, cont = tabela_residuos(sub, coluna_x, bins_reg_x, EVANG_BINS_REG)
        im_reg = desenhar_painel(
            ax, res, norma_reg, regiao,
            subtitulo="n={:,}".format(int(cont.sum())).replace(",", "."),
            pct=pct, rot_x=rot_x_reg,
            rot_y=rotulos_y(EVANG_BINS_REG) if k == 0 else None,
            tam_rotulo=7, tam_titulo=10.5, dy_titulo=0.075,
        )
        ax.text(0, -0.32, seta_esq, transform=ax.transAxes, color=INK_FAINT,
                fontsize=6.5, fontfamily=MONO, ha="left", va="top")
        ax.text(1, -0.32, seta_dir, transform=ax.transAxes, color=INK_FAINT,
                fontsize=6.5, fontfamily=MONO, ha="right", va="top")

    barra_de_cor(
        fig, im_reg, [0.055, 0.078, 0.24, 0.013], ticks_reg,
        "um painel sem cor é ausência de associação,\nnão falta de dados",
        tam=7.8,
    )
    fig.text(0.36, 0.070, rodape, color=INK_FAINT, fontsize=8.2, va="top",
             linespacing=1.65)

    fig.savefig(destino, facecolor=BG)
    plt.close(fig)
    print(f"saved {destino}")


def main() -> None:
    df = carregar()
    correlacoes(df)
    OUT_DIR.mkdir(exist_ok=True)

    figura(
        df, "lean", LEAN_BINS, LEAN_BINS_REG, 1,
        titulo="Religião move o município no eixo esquerda↔direita",
        subtitulo="Censo 2022 (% evangélica) × prefeituras 2024, 1º turno · "
                  "cor = resíduo · número = % da faixa",
        rotulo_eixo="inclinação ideológica do voto (nota média ponderada dos partidos)",
        seta_esq="← esquerda", seta_dir="direita →",
        nota=(
            "Como ler: a cor não é quantidade de municípios — é o quanto a célula "
            "foge do esperado sob independência. Um heatmap de contagem crua só "
            "mostraria que quase todo município fica entre 5,5 e 6,5.\n\n"
            "O número é o dado literal: % dos municípios daquela faixa evangélica "
            "que caem naquela faixa de inclinação. Cada linha soma 100.\n\n"
            "A diagonal vermelha do canto inferior-esquerdo ao superior-direito é a "
            "associação: pouco evangélico → mais à esquerda que o esperado; muito "
            "evangélico → mais à direita.\n\n"
            "Nos painéis regionais ela sobrevive só no Nordeste (e fraca no Sudeste). "
            "Sul, Centro-Oeste e Norte saem sem cor: lá católicos e evangélicos "
            "votam igualmente à direita."
        ),
        rodape=(
            "Fontes: IBGE, Censo 2022 · TSE, resultados por município (prefeito, 1º turno).\n"
            "Inclinação = média das notas ideológicas dos partidos ponderada pelos votos "
            "(survey Bolognesi, Ribeiro & Codato; PL ajustado para 8,5).\n"
            "Os 225 municípios com candidato único (4%) ficam cravados na nota do partido; "
            "excluí-los não muda o padrão (+9,0/+3,7 → +9,0/+4,0)."
        ),
        vmax_br=8.0, vmax_reg=4.0,
        ticks_br=[-8, -4, -2, 0, 2, 4, 8], ticks_reg=[-4, -3, -2, 0, 2, 3, 4],
        destino=OUT_DIR / "heatmap_religiao_x_lean.png",
    )

    figura(
        df, "polar", POLAR_BINS, POLAR_BINS_REG, 2,
        titulo="A mesma religião não prevê o grau de racha ideológico",
        subtitulo="Censo 2022 (% evangélica) × polarização das prefeituras 2024 · "
                  "o painel de controle: aqui não há diagonal",
        rotulo_eixo="polarização (desvio-padrão ideológico dos votos do município)",
        seta_esq="← consenso", seta_dir="racha →",
        nota=(
            "Mesmo cruzamento, mesma escala de cor, trocando o eixo horizontal: "
            "em vez de para onde o município pende, o quanto ele está dividido.\n\n"
            "O padrão desaparece. Nenhuma diagonal, nenhum canto saturado — "
            "coerente com r ≈ 0 entre composição religiosa e polarização.\n\n"
            "É o achado negativo mais limpo do conjunto: religião desloca o "
            "município no espectro, mas não o racha. O que racha é número de "
            "candidatos, população e competitividade — fenômeno de cidade grande, "
            "não de igreja."
        ),
        rodape=(
            "Fontes: IBGE, Censo 2022 · TSE, resultados por município (prefeito, 1º turno).\n"
            "Polarização = desvio-padrão das notas ideológicas dos partidos ponderado "
            "pelos votos do município.\n"
            "Correlações com polarização: nº de candidatos +0,32 · população (log) +0,24 · "
            "% evangélica −0,01."
        ),
        vmax_br=8.0, vmax_reg=4.0,
        ticks_br=[-8, -4, -2, 0, 2, 4, 8], ticks_reg=[-4, -3, -2, 0, 2, 3, 4],
        destino=OUT_DIR / "heatmap_religiao_x_polarizacao.png",
    )


if __name__ == "__main__":
    main()
