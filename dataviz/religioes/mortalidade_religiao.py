#!/usr/bin/env python3
"""Mortalidade por causa em municipios com mais de 20% de evangelicos, 2022.

Nao produz figura: imprime as tabelas. A conclusao e majoritariamente
negativa, e negativa e o resultado — quase toda diferenca aparente entre os
dois grupos de municipios desaparece quando se controla idade, regiao e porte.

O QUE SOBREVIVE AOS TRES CONTROLES
  Transtornos mentais por alcool (F10), suicidio (X60-X84) e doenca alcoolica
  do figado (K70) sao consistentemente MENOS frequentes onde ha mais
  evangelicos, em todos os estratos de porte. Sao as causas com mecanismo
  comportamental documentado (temperanca).
  Tuberculose e mais frequente, mas a razao cai de 1,61 para 1,05 conforme a
  cidade cresce — indicio de confundimento residual por aglomeracao.

O QUE NAO SOBREVIVE — E daria manchete errada
  HIV/aids parece 40% mais frequente no agregado nacional e INVERTE para 0,49
  nas cidades de 300 mil+. Homicidio e Alzheimer fazem o mesmo. O numero
  nacional desses tres e composicao, nao efeito.

POR QUE O CORTE DE 20% ENGANA SOZINHO
  Municipios com >20% de evangelicos concentram 80% da populacao do pais
  (163M de 203M), porque cidade grande e mais evangelica: o corte pega 95% da
  populacao nas cidades de 300 mil+ e so 49% nos municipios de menos de 10
  mil. No topo ele e quase um sinonimo de "cidade grande", entao qualquer
  doenca urbana aparece como "doenca de municipio evangelico" se o porte nao
  entrar no modelo.

FALACIA ECOLOGICA
  Isto compara LUGARES, nao PESSOAS. Municipio mais evangelico com menos
  obitos por alcool nao autoriza concluir que evangelico bebe menos — os
  obitos nao sao dos evangelicos daquele municipio, sao de todo mundo que mora
  la. E a diferenca F10 x K70 pode ser pratica de codificacao, nao incidencia:
  K70 nao sobrevive ao controle regional (mediana intrarregional 1,06) apesar
  de sobreviver ao de porte.

Fontes: MS/SIM 2022 (obitos por causa basica, municipio de residencia, idade
em anos completos, descartados os 2,4% sem idade e os registros acima de 115
anos); IBGE Censo 2022 para religiao (pergunta feita a partir dos 10 anos) e
para a populacao por faixa quinquenal. Agregados por dados/query_mortalidade_religiao.sql.
"""
import collections
import json
from pathlib import Path

DADOS = Path(__file__).parent / "dados" / "mortalidade_religiao_2022.json"

REGIOES = ["Norte", "Nordeste", "Centro-Oeste", "Sudeste", "Sul"]
PORTES = [("P", "< 10 mil"), ("M", "10-50 mil"), ("G", "50-300 mil"), ("XG", "300 mil +")]
MIN_TAXA = 0.5  # causas mais raras que isso por 100 mil nao sustentam a razao


def carregar():
    linhas = json.loads(DADOS.read_text(encoding="utf-8"))
    pop, obitos, causas = collections.Counter(), collections.Counter(), set()
    for r in linhas:
        if r["t"] == "p":
            pop[(r["r"], r["p"], r["g"], r["f"])] += r["v"]
        else:
            obitos[(r["r"], r["p"], r["g"], r["f"], r["c"])] += r["v"]
            causas.add(r["c"])
    faixas = sorted({k[3] for k in pop})
    # populacao padrao = estrutura etaria nacional de 2022 (padronizacao direta)
    padrao = {f: sum(v for k, v in pop.items() if k[3] == f) for f in faixas}
    return pop, obitos, sorted(causas), faixas, padrao


def fabrica(pop, obitos, faixas, padrao):
    """Devolve taxa(grupo, causa, regioes, portes) padronizada por idade, por 100 mil."""
    def t(grupo, causa, regioes=REGIOES, portes=None):
        portes = portes or [p for p, _ in PORTES]
        total = 0.0
        for f in faixas:
            p = sum(pop[(rg, pt, grupo, f)] for rg in regioes for pt in portes)
            if p:
                o = sum(obitos[(rg, pt, grupo, f, causa)] for rg in regioes for pt in portes)
                total += (o / p) * padrao[f]
        return 1e5 * total / sum(padrao.values())
    return t


def vg(v, casas=2):
    return f"{v:.{casas}f}".replace(".", ",")


def main():
    pop, obitos, causas, faixas, padrao = carregar()
    t = fabrica(pop, obitos, faixas, padrao)

    alto = sum(v for k, v in pop.items() if k[2] == "alto")
    baixo = sum(v for k, v in pop.items() if k[2] == "baixo")
    print(f"populacao em municipios com >20% de evangelicos: {alto:,} de {alto + baixo:,} "
          f"({100 * alto / (alto + baixo):.0f}%)".replace(",", "."))

    print("\n=== o corte de 20% e, no topo, um sinonimo de cidade grande ===")
    print(f"  {'porte':<12}{'alto':>10}{'baixo':>10}{'% alto':>9}")
    for pt, rot in PORTES:
        a = sum(v for k, v in pop.items() if k[1] == pt and k[2] == "alto")
        b = sum(v for k, v in pop.items() if k[1] == pt and k[2] == "baixo")
        print(f"  {rot:<12}{a / 1e6:>9.1f}M{b / 1e6:>9.1f}M{100 * a / (a + b):>8.0f}%")

    print("\n=== taxas padronizadas por idade, por 100 mil, e razao alto/baixo ===")
    print(f"  {'causa':<28}{'alto':>8}{'baixo':>8}{'razao':>7}   "
          + "".join(f"{r:>11}" for _, r in PORTES) + "   por regiao")
    linhas = []
    for c in causas:
        a, b = t("alto", c), t("baixo", c)
        if b <= 0 or a + b < MIN_TAXA:
            continue
        por_porte = [t("alto", c, portes=[pt]) / t("baixo", c, portes=[pt])
                     if t("baixo", c, portes=[pt]) > 0 else float("nan")
                     for pt, _ in PORTES]
        por_regiao = [t("alto", c, regioes=[rg]) / t("baixo", c, regioes=[rg])
                      for rg in REGIOES if t("baixo", c, regioes=[rg]) > 0]
        linhas.append((a / b, c, a, b, por_porte, por_regiao))

    for razao, c, a, b, pp, pr in sorted(linhas, reverse=True):
        acima = sum(1 for r in pr if r > 1)
        print(f"  {c:<28}{a:>8.1f}{b:>8.1f}{razao:>7.2f}   "
              + "".join(f"{r:>11.2f}" for r in pp)
              + f"   {acima}/{len(pr)} regioes > 1")

    print("\n=== o que sobrevive: mesma direcao nos quatro estratos de porte ===")
    for razao, c, a, b, pp, pr in sorted(linhas):
        if all(r < 1 for r in pp):
            print(f"  ↓ {c:<28} razao BR {vg(razao)}  "
                  f"(porte: {' · '.join(vg(r) for r in pp)})")
    for razao, c, a, b, pp, pr in sorted(linhas, reverse=True):
        if all(r > 1 for r in pp):
            print(f"  ↑ {c:<28} razao BR {vg(razao)}  "
                  f"(porte: {' · '.join(vg(r) for r in pp)})")

    print("\n=== o que NAO sobrevive: inverte de sinal entre os estratos ===")
    for razao, c, a, b, pp, pr in sorted(linhas, reverse=True):
        if min(pp) < 1 < max(pp):
            print(f"  ! {c:<28} razao BR {vg(razao)}  "
                  f"(porte: {' · '.join(vg(r) for r in pp)})")


if __name__ == "__main__":
    main()
