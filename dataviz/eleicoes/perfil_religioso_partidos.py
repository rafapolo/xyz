#!/usr/bin/env python3
"""Terreno religioso dos partidos que ganharam prefeitura em 2024. Quatro figuras.

  religiao-x-partido-amplitude.png
      Para cada partido, a % de evangelicos dos municipios onde ele elegeu
      prefeito: o menos e o mais evangelico, a faixa onde ficam 80% das suas
      prefeituras (10o ao 90o percentil), a mediana e a media. Ordenado pela
      mediana.

  religiao-x-partido-perfil.png
      Mapa de calor: para cada partido, que fatia das suas prefeituras cai em
      cada faixa de 5 pontos de % evangelica. Mostra o formato da distribuicao,
      nao so a posicao — o que separa PL e UNIAO do PT nao e so a mediana, e a
      cauda direita.

  religiao-x-partido-excedente.png
      O controle. Troca a % bruta pelo excedente regional (% do municipio menos
      a mediana da sua regiao). O gradiente de 10 pontos da primeira figura
      encolhe para ~2: quase tudo era geografia, nao religiao.

  religiao-x-partido-confrontos.png
      Matriz simetrica partido x partido: para cada par que ficou em 1o e 2o
      lugar, a mediana de % evangelica dos municipios onde aquilo aconteceu.
      Ordenada pela nota ideologica, a matriz escurece de canto a canto. O
      achado: fixado o vencedor, o adversario ainda move o terreno em 8 a 12
      pontos — o par carrega mais informacao (r=+0,73) que o vencedor (r=+0,70).

POR QUE O EIXO E O PARTIDO, E NAO O `lean`
O resto do relatorio trata a eleicao como escalar continuo (`lean`, media
ponderada do score ideologico dos votos). Aqui a unidade e o partido que
efetivamente ganhou a prefeitura (`w1`) — dimensao categorica que nenhuma
figura do artigo usava. A pergunta muda de "religiao prediz inclinacao?" para
"em que terreno religioso cada partido vence?".

CUIDADO COM O r=0,70 DA FIGURA 1
Aquela correlacao e entre 18 medianas partidarias, nao entre municipios.
Agregar remove ruido e infla r por construcao — nao e comparavel ao r=0,214
municipal do §1 do relatorio. A figura 3 existe justamente para impedir a
leitura ingenua.

Fontes: Censo 2022 (IBGE/SIDRA 9537) para religiao; TSE, eleicao de prefeito de
2024, 1o turno, para o partido vencedor; scores ideologicos de Bolognesi,
Ribeiro & Codato (2018), com o PL ajustado para 8,5 (ver dados/query.sql e
metodologia.md). Estilo herdado de rodado/scripts/plot_cancer_idade.py.
"""
import collections
import json
import math
import statistics as st

import matplotlib.pyplot as plt
import numpy as np
import polars as pl
from matplotlib.colors import LinearSegmentedColormap, Normalize
from matplotlib.lines import Line2D

from heatmap_religiao_x_lean import (
    OUT_DIR,
    RELIGIOES_COLUMNS,
    RELIGIOES_DATA,
    carregar,
    normalizar,
)

# espelha o CTE scores(sigla, score) de dados/query.sql e PARTY_SCORES de
# index.html — nao ha arquivo canonico, o mecanismo e manter os tres iguais
SCORE_PARTIDO = {
    "PCO": 0.3, "PCB": 0.5, "UP": 0.5, "PSTU": 0.6, "PSOL": 1.3, "PC do B": 1.7,
    "PT": 2.5, "REDE": 3.3, "PDT": 3.3, "PSB": 3.7, "PV": 4.1, "CIDADANIA": 4.6,
    "SOLIDARIEDADE": 5.4, "PMB": 5.5, "MOBILIZA": 5.5, "AVANTE": 5.6, "MDB": 5.7,
    "PODE": 5.7, "PSD": 5.9, "AGIR": 6.0, "PSDB": 6.0, "PRD": 6.8, "UNIÃO": 6.9,
    "PP": 7.0, "REPUBLICANOS": 7.2, "DC": 7.5, "PRTB": 8.0, "NOVO": 8.2, "PL": 8.5,
}

MIN_PREFEITURAS = 15  # abaixo disso os percentis viram anedota
PASSO = 5             # largura das faixas de % evangelica, em pontos percentuais
N_FAIXAS = 14         # 0-5, 5-10, … 60-65, 65 ou mais
REGIOES = ["Norte", "Nordeste", "Centro-Oeste", "Sudeste", "Sul"]

SURFACE, FIG_BG = "#fcfcfb", "#f7f7f5"
TXT, TXT2, TXT3 = "#111111", "#555555", "#7b7b76"
ACENTO, FAIXA, EXTREMO, GRID = "#d1453b", "#e79c92", "#c9c9c2", "#e6e6e2"
MEDIA_TRACO = "#8f5049"


def vg(v, casas=1):
    return f"{v:.{casas}f}".replace(".", ",")


def mil(v):
    return f"{v:,}".replace(",", ".")


def sinal(v, casas=1):
    """Numero com sinal e o menos tipografico, nao o hifen."""
    return f"{v:+.{casas}f}".replace(".", ",").replace("-", "−")


def correlacao(a, b):
    ma, mb = st.mean(a), st.mean(b)
    cov = sum((x - ma) * (y - mb) for x, y in zip(a, b))
    var = sum((x - ma) ** 2 for x in a) * sum((y - mb) ** 2 for y in b)
    return cov / math.sqrt(var)


def evangelicas_2010() -> pl.DataFrame:
    """So para o controle de velocidade de conversao (§7 do relatorio)."""
    dados = json.loads(RELIGIOES_DATA.read_text(encoding="utf-8"))["2010"]
    rel = pl.DataFrame(dados, schema=RELIGIOES_COLUMNS, orient="row")
    return rel.select(
        "uf",
        pl.col("municipio").map_elements(normalizar, return_dtype=pl.Utf8).alias("chave"),
        pl.col("evangelicas").alias("evang_2010"),
    )


def preparar():
    """Junta tudo e devolve (df dos municipios, dict de estatisticas por partido)."""
    df = carregar().join(evangelicas_2010(), on=["uf", "chave"], how="left")

    # excedente regional: quanto o municipio tem de evangelicos acima ou abaixo
    # da mediana da propria regiao. e o controle geografico da figura 3.
    df = df.with_columns(
        (pl.col("evangelicas") - pl.col("evangelicas").median().over("regiao"))
        .alias("excedente"),
        (pl.col("evangelicas") - pl.col("evang_2010")).alias("delta"),
    )

    total = df.height
    grandes = (
        df.group_by("w1").len()
        .filter(pl.col("len") >= MIN_PREFEITURAS)
        .get_column("w1").to_list()
    )
    df = df.filter(pl.col("w1").is_in(grandes))

    stats = {}
    for partido in grandes:
        sub = df.filter(pl.col("w1") == partido)
        ev = np.sort(sub.get_column("evangelicas").to_numpy())
        ex = sub.get_column("excedente").to_numpy()
        delta = sub.get_column("delta").drop_nulls().to_numpy()
        stats[partido] = dict(
            n=len(ev),
            media=float(ev.mean()),
            mediana=float(np.median(ev)),
            minimo=float(ev[0]),
            maximo=float(ev[-1]),
            p10=float(np.percentile(ev, 10)),
            p90=float(np.percentile(ev, 90)),
            ex_p25=float(np.percentile(ex, 25)),
            ex_mediana=float(np.median(ex)),
            ex_p75=float(np.percentile(ex, 75)),
            delta=float(np.median(delta)),
            regiao_top=sub.group_by("regiao").len().sort("len", descending=True)
                          .row(0),
            hist=np.histogram(
                np.clip(ev, 0, N_FAIXAS * PASSO - 0.001),
                bins=np.arange(0, (N_FAIXAS + 1) * PASSO, PASSO),
            )[0],
        )
    return df, stats, total


def resumo(df, stats, ordem, total):
    """Imprime os numeros que sustentam os lides — nada de estimativa."""
    cobertos = sum(s["n"] for s in stats.values())
    print(f"\n{len(stats)} partidos com >= {MIN_PREFEITURAS} prefeituras cobrem "
          f"{cobertos} dos {total} municipios "
          f"({total - cobertos} ficam com os partidos pequenos)")

    print(f"\n{'partido':<15}{'n':>5}{'mediana':>9}{'media':>8}{'p10':>7}{'p90':>7}"
          f"{'min':>7}{'max':>7}{'excedente':>11}{'delta':>8}{'score':>7}  regiao dominante")
    for p in ordem:
        s = stats[p]
        reg, qtd = s["regiao_top"]
        print(f"{p:<15}{s['n']:>5}{s['mediana']:>9.1f}{s['media']:>8.1f}{s['p10']:>7.1f}"
              f"{s['p90']:>7.1f}{s['minimo']:>7.1f}{s['maximo']:>7.1f}"
              f"{s['ex_mediana']:>+11.1f}{s['delta']:>8.1f}"
              f"{SCORE_PARTIDO.get(p, 5.0):>7.1f}  {reg} ({100 * qtd / s['n']:.0f}%)")

    scores = [SCORE_PARTIDO.get(p, 5.0) for p in ordem]
    print(f"\ncorr(score ideologico, mediana evangelica)  = "
          f"{correlacao(scores, [stats[p]['mediana'] for p in ordem]):+.3f}   (k={len(ordem)})")
    print(f"corr(score ideologico, excedente regional) = "
          f"{correlacao(scores, [stats[p]['ex_mediana'] for p in ordem]):+.3f}")

    print("\nmediana evangelica por regiao:")
    for reg in REGIOES:
        sub = df.filter(pl.col("regiao") == reg)
        print(f"  {reg:<14}{sub.get_column('evangelicas').median():>6.1f}   (n={sub.height})")

    print("\ndentro de cada regiao, corr(score, mediana evangelica do partido):")
    intra = {}
    for reg in REGIOES:
        sub = df.filter(pl.col("regiao") == reg)
        a, b = [], []
        for p in ordem:
            v = sub.filter(pl.col("w1") == p).get_column("evangelicas")
            if len(v) >= MIN_PREFEITURAS:
                a.append(SCORE_PARTIDO.get(p, 5.0))
                b.append(float(v.median()))
        intra[reg] = correlacao(a, b)
        print(f"  {reg:<14}{intra[reg]:>+7.3f}   (k={len(a)} partidos)")
    return intra


# ============================================================ figura 1
def figura_amplitude(stats, ordem, total):
    """Amplitude: traco fino = min→max, barra grossa = 10o ao 90o percentil,
    ponto = mediana, risco = media."""
    fig = plt.figure(figsize=(12.4, 10.1), dpi=200, facecolor=FIG_BG)
    ax = fig.add_axes((0.245, 0.168, 0.735, 0.515))
    ax.set_facecolor(SURFACE)

    for i, partido in enumerate(ordem):
        s = stats[partido]
        y = len(ordem) - 1 - i
        ax.plot([s["minimo"], s["maximo"]], [y, y], color=EXTREMO, lw=1.6,
                solid_capstyle="round", zorder=2)
        for x in (s["minimo"], s["maximo"]):
            ax.plot([x, x], [y - 0.24, y + 0.24], color=EXTREMO, lw=1.6, zorder=2)
        ax.plot([s["p10"], s["p90"]], [y, y], color=FAIXA, lw=8.5,
                solid_capstyle="round", zorder=3)
        ax.plot([s["media"], s["media"]], [y - 0.2, y + 0.2], color=MEDIA_TRACO,
                lw=1.8, zorder=4)
        ax.scatter([s["mediana"]], [y], s=78, color=ACENTO, edgecolors=SURFACE,
                   linewidths=1.6, zorder=5)

    ax.set_yticks(range(len(ordem)))
    ax.set_yticklabels(list(reversed(ordem)), fontsize=11, color=TXT2)
    ax.set_ylim(-1.3, len(ordem) - 0.2)  # folga extra embaixo para o rotulo do ultimo
    ax.set_xlim(0, 92)
    ax.set_xticks(range(0, 91, 10))
    ax.xaxis.set_major_formatter(lambda v, _: f"{v:g}%")
    ax.grid(axis="x", color=GRID, lw=0.8)
    ax.set_axisbelow(True)
    for sp in ax.spines.values():
        sp.set_visible(False)
    ax.tick_params(colors=TXT3, labelsize=11.5, length=0)
    ax.set_xlabel("% de evangélicos do município onde o partido elegeu prefeito",
                  fontsize=12.5, color=TXT2, labelpad=10)

    # o primeiro da lista sai por cima, o ultimo por baixo: nao ha vizinho para colidir
    for partido, dx, dy, ha in ((ordem[0], 5, 0.85, "left"),
                                (ordem[-1], 5, -0.85, "left")):
        y = len(ordem) - 1 - ordem.index(partido)
        ax.annotate(f"mediana {vg(stats[partido]['mediana'])}%",
                    xy=(stats[partido]["mediana"], y),
                    xytext=(stats[partido]["mediana"] + dx, y + dy),
                    fontsize=10.5, color=TXT, fontweight="bold", ha=ha,
                    arrowprops=dict(arrowstyle="-", color=TXT3, lw=0.9))

    leg = [Line2D([], [], color=EXTREMO, lw=1.6, label="município menos → mais evangélico"),
           Line2D([], [], color=FAIXA, lw=8.5, label="onde estão 80% das prefeituras"),
           Line2D([], [], color=ACENTO, marker="o", ls="", markersize=8.5,
                  markeredgecolor=SURFACE, label="mediana"),
           Line2D([], [], color=MEDIA_TRACO, lw=1.8, label="média")]
    ax.legend(handles=leg, loc="lower left", bbox_to_anchor=(-0.005, 1.012), ncol=4,
              frameon=False, fontsize=10.5, labelcolor=TXT2, handletextpad=0.9,
              columnspacing=2.2, borderpad=0.0, handlelength=1.9)

    fig.text(0.082, 0.944, "Cada partido ganha num Brasil religioso diferente",
             ha="left", va="top", fontsize=25, fontweight="bold", color=TXT)
    fig.text(0.082, 0.893,
             "% de evangélicos dos municípios onde cada partido elegeu prefeito em 2024, ordenado pela mediana",
             ha="left", va="top", fontsize=13, color=TXT2)
    fig.text(0.082, 0.848,
             f"O PT elege prefeito onde os evangélicos são {vg(stats[ordem[0]]['mediana'])}% da população; o UNIÃO, onde são "
             f"{vg(stats[ordem[-1]]['mediana'])}% — dez pontos entre\n"
             "as duas pontas da lista, e a ordem dos partidos no meio acompanha de perto a escala esquerda-direita.\n"
             "Mas repare na barra clara: todos os partidos vencem em municípios de quase todo tipo de terreno religioso.\n"
             "A diferença está em onde cada um se concentra, não em território exclusivo.",
             ha="left", va="top", fontsize=13.5, color=TXT, linespacing=1.6)

    cobertos = sum(s["n"] for s in stats.values())
    fig.text(0.082, 0.072,
             "Fontes: IBGE, Censo 2022 (tabela SIDRA 9537), % da população residente por religião; TSE, eleição para prefeito de 2024, 1º turno, partido do vencedor.\n"
             f"{mil(total)} municípios têm os dois dados. Entram só os {len(ordem)} partidos com {MIN_PREFEITURAS} prefeituras ou mais, que cobrem {mil(cobertos)} deles — os 6 partidos\n"
             f"restantes somam {total - cobertos} municípios ({vg(100 * (total - cobertos) / total)}%). Mínimo e máximo são municípios isolados; a leitura confiável é a barra dos 80%.",
             ha="left", va="top", fontsize=9.5, color=TXT3, linespacing=1.6)

    saida = OUT_DIR / "religiao-x-partido-amplitude.png"
    fig.savefig(saida, facecolor=fig.get_facecolor())
    print("ok:", saida)


# ============================================================ figura 2
def figura_perfil(stats, ordem):
    """Mapa de calor: fatia das prefeituras de cada partido em cada faixa."""
    RAMPA = LinearSegmentedColormap.from_list("rodado_seq", [
        "#fdf6f4", "#f9dfd9", "#f2bdb2", "#e8968a", "#dc6c5f", "#c9402f", "#96271d"])

    fig = plt.figure(figsize=(12.4, 10.2), dpi=200, facecolor=FIG_BG)
    ax = fig.add_axes((0.245, 0.284, 0.70, 0.422))
    ax.set_facecolor(SURFACE)

    matriz = np.array([100 * stats[p]["hist"] / stats[p]["hist"].sum() for p in ordem])
    assert np.allclose(matriz.sum(axis=1), 100), "cada linha tem de somar 100%"

    im = ax.imshow(matriz, aspect="auto", cmap=RAMPA,
                   norm=Normalize(0, matriz.max()), interpolation="nearest")

    # risco branco na mediana — ancora esta figura na anterior
    for i, partido in enumerate(ordem):
        x = min(stats[partido]["mediana"] / PASSO, N_FAIXAS - 0.5) - 0.5
        ax.plot([x, x], [i - 0.45, i + 0.45], color="#ffffff", lw=2.4,
                solid_capstyle="butt", zorder=3)

    ax.set_yticks(range(len(ordem)))
    ax.set_yticklabels(ordem, fontsize=11, color=TXT2)
    ax.set_xticks(range(0, N_FAIXAS, 2))
    ax.set_xticklabels([f"{g * PASSO}%" for g in range(0, N_FAIXAS, 2)],
                       fontsize=11.5, color=TXT3)
    ax.tick_params(length=0)
    for sp in ax.spines.values():
        sp.set_visible(False)
    ax.set_xlabel("% de evangélicos do município  ·  última coluna = 65% ou mais",
                  fontsize=12.5, color=TXT2, labelpad=10)

    # barra de cor em retangulo proprio: com `pad` relativo ela subia por cima
    # do rotulo do eixo x, porque este eixo e mais baixo que o do script do cancer
    cax = fig.add_axes((0.305, 0.196, 0.58, 0.014))
    cb = fig.colorbar(im, cax=cax, orientation="horizontal")
    cb.outline.set_visible(False)
    cb.ax.tick_params(colors=TXT3, labelsize=10.5, length=0)
    cb.set_label("fatia das prefeituras daquele partido que cai na faixa  ·  cada linha soma 100%",
                 fontsize=10.5, color=TXT3, labelpad=9)
    cb.ax.xaxis.set_major_formatter(lambda v, _: f"{v:g}%".replace(".", ","))

    cauda = {p: 100 * stats[p]["hist"][8:].sum() / stats[p]["hist"].sum() for p in ordem}
    fig.text(0.082, 0.953, "O mapa evangélico dos partidos, sigla por sigla",
             ha="left", va="top", fontsize=25, fontweight="bold", color=TXT)
    fig.text(0.082, 0.911,
             "Cada linha é um partido e soma 100%: quanto mais escura a célula, mais prefeituras dele naquele terreno",
             ha="left", va="top", fontsize=13, color=TXT2)
    fig.text(0.082, 0.873,
             "A mancha desce da esquerda para a direita porque a lista segue a ordem da figura anterior, da menor mediana\n"
             "para a maior — o traço branco marca onde ela cai. O que separa as pontas não é só a posição da mancha, é a\n"
             f"cauda: {vg(cauda['PL'])}% das prefeituras do PL e {vg(cauda['UNIÃO'])}% das do UNIÃO estão em municípios com 40% ou mais de\n"
             f"evangélicos, contra {vg(cauda['PT'])}% das do PT.",
             ha="left", va="top", fontsize=13.5, color=TXT, linespacing=1.6)

    fig.text(0.082, 0.120,
             "Fontes: IBGE, Censo 2022 (tabela SIDRA 9537); TSE, eleição para prefeito de 2024, 1º turno, partido do vencedor. Mesmo recorte da figura de amplitude.\n"
             "Percentuais dentro de cada partido, não entre partidos — a cor compara terrenos de um mesmo partido, nunca o tamanho de um partido contra o outro.\n"
             "As linhas dos partidos pequenos são mais manchadas por aritmética, não por concentração: com 18 prefeituras, o NOVO joga 5,6% da sua linha em cada município\n"
             "que ganha, contra 0,1% do PSD, que ganhou 884. Compare a posição e a largura da mancha entre as linhas, não o contraste de uma célula isolada.",
             ha="left", va="top", fontsize=9.5, color=TXT3, linespacing=1.6)

    saida = OUT_DIR / "religiao-x-partido-perfil.png"
    fig.savefig(saida, facecolor=fig.get_facecolor())
    print("ok:", saida)


# ============================================================ figura 3
def figura_excedente(stats, intra):
    """O controle: excedente regional em vez de % bruta."""
    ordem = sorted(stats, key=lambda p: stats[p]["ex_mediana"])

    # mais alta que a figura 1: a nota de rodape aqui tem quatro linhas
    fig = plt.figure(figsize=(12.4, 10.6), dpi=200, facecolor=FIG_BG)
    ax = fig.add_axes((0.245, 0.193, 0.735, 0.491))
    ax.set_facecolor(SURFACE)

    ax.axvline(0, color=TXT3, lw=1.2, zorder=2)
    for i, partido in enumerate(ordem):
        s = stats[partido]
        y = len(ordem) - 1 - i
        ax.plot([s["ex_p25"], s["ex_p75"]], [y, y], color=FAIXA, lw=8.5,
                solid_capstyle="round", zorder=3)
        ax.scatter([s["ex_mediana"]], [y], s=78, color=ACENTO, edgecolors=SURFACE,
                   linewidths=1.6, zorder=5)

    ax.set_yticks(range(len(ordem)))
    ax.set_yticklabels(list(reversed(ordem)), fontsize=11, color=TXT2)
    ax.set_ylim(-0.8, len(ordem) - 0.2)
    ax.set_xlim(-13, 13)
    ax.set_xticks(range(-12, 13, 3))
    ax.xaxis.set_major_formatter(
        lambda v, _: "0" if v == 0 else f"{v:+g}".replace("-", "−"))
    ax.grid(axis="x", color=GRID, lw=0.8)
    ax.set_axisbelow(True)
    for sp in ax.spines.values():
        sp.set_visible(False)
    ax.tick_params(colors=TXT3, labelsize=11.5, length=0)
    ax.set_xlabel("pontos percentuais de evangélicos acima ou abaixo da mediana da própria região",
                  fontsize=12.5, color=TXT2, labelpad=10)

    # anota os dois lados da disputa, nao os extremos brutos: o mais negativo e o
    # MOBILIZA, com 21 prefeituras, cujo excedente e ruido amostral
    for partido, dx, dy, ha in (("PT", -2.2, -0.6, "right"), ("PL", 2.4, 0.55, "left")):
        y = len(ordem) - 1 - ordem.index(partido)
        ax.annotate(f"{partido}  {sinal(stats[partido]['ex_mediana'])} p.p.",
                    xy=(stats[partido]["ex_mediana"], y),
                    xytext=(stats[partido]["ex_mediana"] + dx, y + dy),
                    fontsize=10.5, color=TXT, fontweight="bold", ha=ha,
                    arrowprops=dict(arrowstyle="-", color=TXT3, lw=0.9))

    leg = [Line2D([], [], color=FAIXA, lw=8.5, label="metade do meio das prefeituras (p25 a p75)"),
           Line2D([], [], color=ACENTO, marker="o", ls="", markersize=8.5,
                  markeredgecolor=SURFACE, label="mediana do excedente")]
    ax.legend(handles=leg, loc="lower left", bbox_to_anchor=(-0.005, 1.012), ncol=2,
              frameon=False, fontsize=10.5, labelcolor=TXT2, handletextpad=0.9,
              columnspacing=2.2, borderpad=0.0, handlelength=1.9)

    intra_txt = "  ·  ".join(f"{r} {vg(v, 2)}" for r, v in intra.items())

    fig.text(0.082, 0.9465, "Quase tudo era geografia — sobrou o PL",
             ha="left", va="top", fontsize=25, fontweight="bold", color=TXT)
    fig.text(0.082, 0.8977,
             "Mesmos partidos, agora medidos contra os vizinhos: % evangélica do município menos a mediana da sua região",
             ha="left", va="top", fontsize=13, color=TXT2)
    fig.text(0.082, 0.855,
             "O PT ganha onde há poucos evangélicos porque ganha no Nordeste, a região menos evangélica do país (15,9%);\n"
             "o UNIÃO ganha onde há muitos porque ganha no Norte e no Centro-Oeste (34,2% e 29,7%). Medido contra os\n"
             "vizinhos, o gradiente de dez pontos vira dois, e a correlação com a escala ideológica cai de 0,70 para 0,15.\n"
             "Sobra o PL, único claramente acima da própria região — e, entre os grandes, o PT, o mais abaixo dela.",
             ha="left", va="top", fontsize=13.5, color=TXT, linespacing=1.6)

    fig.text(0.082, 0.098,
             "Fontes: IBGE, Censo 2022 (tabela SIDRA 9537); TSE, eleição para prefeito de 2024, 1º turno, partido do vencedor. Mesmo recorte das figuras anteriores.\n"
             f"Dentro de cada região a correlação segue positiva nas cinco: {intra_txt}.\n"
             "As correlações são entre 18 medianas partidárias, não entre municípios: agregar remove ruído e infla r por construção — não são comparáveis ao r de 0,214\n"
             "medido município a município. A velocidade de conversão não separa os partidos: a mediana do crescimento evangélico 2010→2022 fica entre 4,7 e 6,4 p.p. em todos.",
             ha="left", va="top", fontsize=9.5, color=TXT3, linespacing=1.6)

    saida = OUT_DIR / "religiao-x-partido-excedente.png"
    fig.savefig(saida, facecolor=fig.get_facecolor())
    print("ok:", saida)


# ============================================================ figura 4
MIN_CONFRONTOS = 20  # pares com menos duelos que isso saem vazios
MIN_ADVERSARIOS = 4  # partido precisa aparecer em 4 pares cheios para virar linha


def matriz_confrontos(df):
    """Mediana de % evangelica dos municipios onde cada par disputou o 1o e o 2o
    lugar. Par nao ordenado: o que importa e quem estava em campo, nao quem venceu."""
    duelos = df.filter(pl.col("w2").is_not_null()).with_columns(
        pl.min_horizontal("w1", "w2").alias("a"),
        pl.max_horizontal("w1", "w2").alias("b"),
    )
    pares = {
        (r["a"], r["b"]): (r["n"], r["ev"])
        for r in duelos.group_by("a", "b")
        .agg(pl.len().alias("n"), pl.col("evangelicas").median().alias("ev"))
        .to_dicts()
        if r["n"] >= MIN_CONFRONTOS
    }

    graus = collections.Counter()
    for a, b in pares:
        graus[a] += 1
        graus[b] += 1
    partidos = sorted((p for p, k in graus.items() if k >= MIN_ADVERSARIOS),
                      key=lambda p: (SCORE_PARTIDO.get(p, 5.0), p))

    m = np.full((len(partidos), len(partidos)), np.nan)
    for i, a in enumerate(partidos):
        for j, b in enumerate(partidos):
            if i != j and (par := pares.get(tuple(sorted((a, b))))):
                m[i, j] = par[1]
    return partidos, m, pares, duelos


def figura_confrontos(df):
    partidos, m, pares, duelos = matriz_confrontos(df)
    centro = float(df.get_column("evangelicas").median())
    alcance = float(np.nanmax(np.abs(m - centro)))

    # divergente claro: catolico (azul) ↔ mediana nacional (papel) ↔ evangelico (vermelho)
    DIVERGENTE = LinearSegmentedColormap.from_list("rodado_div", [
        "#26596f", "#5b8ea6", "#a3c1d0", "#dfe9ed", SURFACE,
        "#f6dbd4", "#eaa294", "#d75f50", "#96271d"])
    DIVERGENTE.set_bad(FIG_BG)

    # alta o bastante para os rotulos de coluna a 45º caberem entre o lide e a
    # matriz sem encostar no texto — "REPUBLICANOS" e o que dita a folga
    fig = plt.figure(figsize=(12.4, 13.4), dpi=200, facecolor=FIG_BG)
    ax = fig.add_axes((0.245, 0.187, 0.545, 0.518))
    ax.set_facecolor(FIG_BG)

    norma = Normalize(centro - alcance, centro + alcance)
    im = ax.imshow(m, cmap=DIVERGENTE, norm=norma, interpolation="nearest")

    for i in range(len(partidos)):
        for j in range(len(partidos)):
            if np.isnan(m[i, j]):
                continue
            forte = abs(m[i, j] - centro) > 0.62 * alcance
            ax.text(j, i, vg(m[i, j]), ha="center", va="center", fontsize=9,
                    color=SURFACE if forte else TXT2)

    ax.set_xticks(range(len(partidos)))
    ax.set_yticks(range(len(partidos)))
    ax.xaxis.tick_top()
    ax.set_xticklabels(partidos, fontsize=10, color=TXT2, rotation=45,
                       ha="left", rotation_mode="anchor")
    ax.set_yticklabels(partidos, fontsize=10, color=TXT2)
    ax.set_xticks(np.arange(-0.5, len(partidos), 1), minor=True)
    ax.set_yticks(np.arange(-0.5, len(partidos), 1), minor=True)
    ax.grid(which="minor", color=FIG_BG, lw=2.5)
    ax.tick_params(length=0)
    ax.tick_params(which="minor", length=0)
    for sp in ax.spines.values():
        sp.set_visible(False)

    cax = fig.add_axes((0.305, 0.120, 0.42, 0.012))
    cb = fig.colorbar(im, cax=cax, orientation="horizontal")
    cb.outline.set_visible(False)
    cb.ax.tick_params(colors=TXT3, labelsize=10, length=0)
    cb.set_label(f"mediana de % evangélica dos municípios onde os dois se enfrentaram  ·  "
                 f"centro = mediana nacional, {vg(centro)}%",
                 fontsize=10, color=TXT3, labelpad=9)
    cb.ax.xaxis.set_major_formatter(lambda v, _: f"{v:g}%".replace(".", ","))

    fig.text(0.082, 0.9577, "Não é quem vence, é quem estava no páreo",
             ha="left", va="top", fontsize=25, fontweight="bold", color=TXT)
    fig.text(0.082, 0.9191,
             "Para cada par de partidos que ficou em 1º e 2º lugar, a % evangélica típica do município onde isso aconteceu",
             ha="left", va="top", fontsize=13, color=TXT2)
    fig.text(0.082, 0.8853,
             "PSB contra PT é uma disputa de município católico (14,0% de evangélicos); PL contra UNIÃO, de município\n"
             "evangélico (30,7%) — e a matriz escurece do canto de cima para o de baixo porque as siglas estão ordenadas\n"
             "pela nota ideológica. O adversário informa tanto quanto o vencedor: onde o MDB ganha do PSB o terreno tem\n"
             "16,6% de evangélicos, e onde ganha do PL, 25,1% — oito pontos de diferença para o mesmo partido vencedor.",
             ha="left", va="top", fontsize=13.5, color=TXT, linespacing=1.6)

    fig.text(0.082, 0.072,
             "Fontes: IBGE, Censo 2022 (tabela SIDRA 9537); TSE, eleição para prefeito de 2024, 1º turno, os dois partidos mais votados de cada município.\n"
             f"Linhas e colunas ordenadas pela nota ideológica do partido. O par não é ordenado — a matriz é simétrica, e a diagonal fica vazia porque dois candidatos\n"
             f"do mesmo partido não disputam entre si. Células em branco são pares com menos de {MIN_CONFRONTOS} municípios; entram as {len(partidos)} siglas com {MIN_ADVERSARIOS} adversários ou mais.",
             ha="left", va="top", fontsize=9.5, color=TXT3, linespacing=1.6)

    saida = OUT_DIR / "religiao-x-partido-confrontos.png"
    fig.savefig(saida, facecolor=fig.get_facecolor())
    print("ok:", saida)

    scores = [(SCORE_PARTIDO.get(a, 5.0) + SCORE_PARTIDO.get(b, 5.0)) / 2 for a, b in pares]
    print(f"   r(nota média do par, terreno do confronto) = "
          f"{correlacao(scores, [v[1] for v in pares.values()]):+.3f}  "
          f"(k={len(pares)} pares, {sum(v[0] for v in pares.values())} municípios)")
    print("   com o vencedor fixo, o terreno muda conforme o adversário:")
    for w in ["MDB", "PSD", "PP", "PL", "UNIÃO", "PT"]:
        sub = (duelos.filter(pl.col("w1") == w).group_by("w2")
               .agg(pl.len().alias("n"), pl.col("evangelicas").median().alias("ev"))
               .filter(pl.col("n") >= MIN_CONFRONTOS).sort("ev").to_dicts())
        if len(sub) >= 3:
            print(f"     {w:<13} vs {sub[0]['w2']:<14}{sub[0]['ev']:5.1f}  →  "
                  f"vs {sub[-1]['w2']:<14}{sub[-1]['ev']:5.1f}   "
                  f"amplitude {sub[-1]['ev'] - sub[0]['ev']:+.1f} p.p.")


def main():
    df, stats, total = preparar()
    ordem = sorted(stats, key=lambda p: (stats[p]["mediana"], stats[p]["media"]))
    intra = resumo(df, stats, ordem, total)
    print()
    figura_amplitude(stats, ordem, total)
    figura_perfil(stats, ordem)
    figura_excedente(stats, intra)
    figura_confrontos(df)


if __name__ == "__main__":
    main()
