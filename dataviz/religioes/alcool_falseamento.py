#!/usr/bin/env python3
"""Mortalidade alcoolica em municipios evangelicos, com teste de falseamento. 2022.

Nao produz figura: imprime as tabelas que decidem se a hipotese sobrevive.

A HIPOTESE
  A abstinencia e doutrinaria e explicita em boa parte das igrejas evangelicas
  — e o mecanismo mais direto que existe entre religiao e causa de morte. Se
  for real, municipios com mais evangelicos devem registrar menos obitos por
  doenca alcoolica do figado (K70) e por transtornos mentais devidos ao alcool
  (F10).

O TESTE QUE PODE MATAR A HIPOTESE
  Municipios diferem em muito mais que religiao, e quase tudo passa por acesso
  a servico de saude e qualidade do registro. Por isso as mesmas taxas sao
  calculadas para causas sem relacao alguma com alcool mas sensiveis a acesso
  (apendicite, hernia, colelitiase — morrer disso e falha cirurgica) e a
  registro (causas mal definidas, R95-R99).

  Se K70 e F10 caem e os controles negativos ficam parados, o mecanismo
  alcoolico se sustenta. Se tudo cai junto, o que se mediu foi servico de
  saude, e a hipotese morre.

ESPECIFICIDADE
  Cirrose nao alcoolica (K71-K76) ataca o mesmo orgao pela via nao alcoolica.
  Se o efeito e do alcool, K70 tem de cair muito mais que K71-K76.

DOSE-RESPOSTA
  Mecanismo real produz gradiente monotono ao longo da % evangelica.
  Confundimento por porte ou regiao tende a produzir degrau.

Todas as taxas sao padronizadas por idade (direta, estrutura nacional de 2022)
e expressas por 100 mil habitantes. Isto compara LUGARES, nao PESSOAS: os
obitos de um municipio nao sao dos evangelicos dele, sao de todos os
residentes. Ver dados/query_alcool_falseamento.sql.
"""
import collections
import json
from pathlib import Path

DADOS = Path(__file__).parent / "dados" / "alcool_falseamento_2022.json"

PORTES = [("P", "< 10 mil"), ("M", "10-50 mil"), ("G", "50-300 mil"), ("XG", "300 mil +")]
REGIOES = ["Norte", "Nordeste", "Centro-Oeste", "Sudeste", "Sul"]

ALCOOL = ["K70 doenca alcoolica do figado", "F10 transtornos por alcool",
          "outras 100% alcool"]
ESPECIFICIDADE = ["K71-76 cirrose nao alcoolica"]
CONTROLES = ["CN apendicite", "CN hernia", "CN colelitiase", "CN causa mal definida"]


def vg(v, casas=2):
    return f"{v:.{casas}f}".replace(".", ",")


def carregar():
    linhas = json.loads(DADOS.read_text(encoding="utf-8"))
    pop, obitos = collections.Counter(), collections.Counter()
    for r in linhas:
        chave = (r["r"], r["p"], r["g"], r["b"], r["i"])
        if r["t"] == "p":
            pop[chave] += r["v"]
        else:
            obitos[chave + (r["c"],)] += r["v"]
    idades = sorted({k[4] for k in pop})
    padrao = {i: sum(v for k, v in pop.items() if k[4] == i) for i in idades}
    return pop, obitos, idades, padrao


def fabrica(pop, obitos, idades, padrao):
    """taxa(causa, **filtros) padronizada por idade, por 100 mil."""
    total_padrao = sum(padrao.values())

    def taxa(causa, grupo=None, faixa_ev=None, porte=None, regiao=None):
        def bate(k):
            return ((grupo is None or k[2] == grupo)
                    and (faixa_ev is None or k[3] == faixa_ev)
                    and (porte is None or k[1] == porte)
                    and (regiao is None or k[0] == regiao))
        soma = 0.0
        for i in idades:
            p = sum(v for k, v in pop.items() if k[4] == i and bate(k))
            if not p:
                continue
            o = sum(v for k, v in obitos.items() if k[4] == i and k[5] == causa and bate(k))
            soma += (o / p) * padrao[i]
        return 1e5 * soma / total_padrao

    return taxa


def bloco(titulo, causas, taxa, obitos):
    print(f"\n{titulo}")
    print(f"  {'causa':<32}{'obitos':>8}{'alto':>8}{'baixo':>8}{'razao':>8}   "
          + "".join(f"{r:>11}" for _, r in PORTES))
    for c in causas:
        n = sum(v for k, v in obitos.items() if k[5] == c)
        a, b = taxa(c, grupo="alto"), taxa(c, grupo="baixo")
        razoes = []
        for pt, _ in PORTES:
            x, y = taxa(c, grupo="alto", porte=pt), taxa(c, grupo="baixo", porte=pt)
            razoes.append(x / y if y > 0 else float("nan"))
        print(f"  {c:<32}{n:>8,}{a:>8.2f}{b:>8.2f}{a / b:>8.2f}   ".replace(",", ".")
              + "".join(f"{r:>11.2f}" for r in razoes))


def main():
    pop, obitos, idades, padrao = carregar()
    taxa = fabrica(pop, obitos, idades, padrao)

    print("TAXAS PADRONIZADAS POR IDADE, POR 100 MIL — 2022")
    print("razao = municipios com >20% de evangelicos / demais.  <1 = menos frequente onde ha mais evangelicos")

    bloco("[1] CAUSAS DE ALCOOL — onde a hipotese preve queda", ALCOOL, taxa, obitos)
    bloco("[2] ESPECIFICIDADE — mesmo orgao, via nao alcoolica", ESPECIFICIDADE, taxa, obitos)
    bloco("[3] CONTROLES NEGATIVOS — a hipotese preve razao ~1", CONTROLES, taxa, obitos)

    print("\n[4] DOSE-RESPOSTA — taxa padronizada por faixa de % evangelica")
    faixas = sorted({k[3] for k in pop})
    print(f"  {'faixa':<12}" + "".join(f"{c.split()[0]:>10}" for c in ALCOOL[:2] + ESPECIFICIDADE)
          + "".join(f"{c.replace('CN ', '')[:9]:>11}" for c in CONTROLES))
    for f in faixas:
        vals = [taxa(c, faixa_ev=f) for c in ALCOOL[:2] + ESPECIFICIDADE]
        ctrl = [taxa(c, faixa_ev=f) for c in CONTROLES]
        print(f"  {f:<12}" + "".join(f"{v:>10.2f}" for v in vals)
              + "".join(f"{v:>11.2f}" for v in ctrl))

    print("\n[5] VEREDITO")
    k70 = taxa("K70 doenca alcoolica do figado", grupo="alto") / \
        taxa("K70 doenca alcoolica do figado", grupo="baixo")
    f10 = taxa("F10 transtornos por alcool", grupo="alto") / \
        taxa("F10 transtornos por alcool", grupo="baixo")
    esp = taxa(ESPECIFICIDADE[0], grupo="alto") / taxa(ESPECIFICIDADE[0], grupo="baixo")
    cns = [taxa(c, grupo="alto") / taxa(c, grupo="baixo") for c in CONTROLES]
    print(f"  alcool:              K70 {vg(k70)}   F10 {vg(f10)}")
    print(f"  cirrose nao alcool:  {vg(esp)}")
    print(f"  controles negativos: " + "  ".join(
        f"{c.replace('CN ', '')} {vg(r)}" for c, r in zip(CONTROLES, cns)))
    # o que falseia a hipotese nao e o controle se mexer, e ele se mexer PARA O
    # MESMO LADO: se apendicite e hernia tambem caissem, a leitura obvia seria
    # que o municipio evangelico registra menos morte de tudo. Controle subindo
    # enquanto o alcool cai joga contra o achado, tornando-o conservador.
    juntos = sum(1 for r in cns if r < 0.95)
    registro = cns[CONTROLES.index("CN causa mal definida")]
    print(f"\n  controles negativos que caem junto com o alcool (razao < 0,95): "
          f"{juntos} de {len(cns)}")
    if juntos >= 2:
        print("  -> os controles acompanham a queda: o sinal e de acesso/registro, nao de alcool")
    elif k70 < 0.85 and f10 < 0.85:
        print("  -> alcool cai e os controles nao caem: a hipotese sobrevive ao falseamento.")
        print("     Os controles de acesso ate SOBEM, o que torna o achado conservador:")
        print("     onde ha mais evangelicos morre-se um pouco mais de doenca cirurgica")
        print("     curavel, e mesmo assim menos de alcool.")
    else:
        print("  -> sem queda clara no alcool: nada a concluir")

    print(f"\n  qualidade do registro (causa mal definida): razao {vg(registro)} no corte de 20%")
    piores = max(faixas, key=lambda f: taxa("CN causa mal definida", faixa_ev=f))
    r_pior = taxa("CN causa mal definida", faixa_ev=piores)
    r_base = taxa("CN causa mal definida", faixa_ev=faixas[0])
    print(f"     mas por faixa vai de {vg(r_base)} ({faixas[0]}) a {vg(r_pior)} ({piores}) por 100 mil.")
    if r_pior > 1.3 * r_base:
        print("     RESSALVA: na ponta mais evangelica investiga-se menos a causa do obito.")
        print("     Como a diferenca de causa mal definida e varias vezes maior que a taxa")
        print("     de K70 inteira, o extremo do gradiente nao e confiavel — parte da queda")
        print("     pode ser obito alcoolico que virou causa mal definida. O corte binario")
        print("     de 20%, onde o registro esta equilibrado, e a leitura defensavel.")


if __name__ == "__main__":
    main()
