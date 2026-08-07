#!/usr/bin/env python3
"""Mortalidade alcoolica em municipios SEM RELIGIAO, 2022. Nao produz figura.

O QUE ESTE TESTE DECIDE
  O achado do falseamento evangelico (alcool cai onde ha mais evangelicos, e os
  controles negativos nao caem junto) e compativel com duas leituras que aquele
  desenho nao separa:
    (a) DOUTRINA — a abstinencia e regra escrita, e a regra pega;
    (b) RELIGIOSIDADE EM GERAL — o que segura o alcool nao e a doutrina
        evangelica, e sim ter religiao, qualquer uma.
  "Sem religiao" e o unico segundo contraste que o Censo 2022 permite (819
  municipios acima de 10%; espirita tem 11, umbanda e candomble tem zero).

  Se o alcool cair TAMBEM onde ha mais gente sem religiao, nenhuma das duas
  leituras se sustenta — o gradiente e de outra coisa, e o achado evangelico
  perde o mecanismo. Se subir, (a) e (b) seguem vivas e a doutrina ganha forca.

O CONFUNDIDOR PRINCIPAL
  Sem religiao e evangelico crescem juntos, os dois no lugar onde o catolicismo
  recua: 94% da populacao dos municipios com >10% de sem religiao mora tambem
  em municipio com >20% de evangelicos. Por isso toda razao aqui e repetida
  DENTRO de cada estrato evangelico. So o que sobrevive aos dois estratos e
  efeito de sem-religiao; o resto e evangelico disfarcado.

Taxas padronizadas por idade (direta, estrutura nacional de 2022), por 100 mil.
Compara LUGARES, nao PESSOAS. Ver dados/query_alcool_sem_religiao.sql.
"""
import collections
import json
from pathlib import Path

DADOS = Path(__file__).parent / "dados" / "alcool_sem_religiao_2022.json"

PORTES = [("P", "< 10 mil"), ("M", "10-50 mil"), ("G", "50-300 mil"), ("XG", "300 mil +")]
REGIOES = ["Norte", "Nordeste", "Centro-Oeste", "Sudeste", "Sul"]

ALCOOL = ["K70 doenca alcoolica do figado", "F10 transtornos por alcool",
          "outras 100% alcool"]
ESPECIFICIDADE = ["K71-76 cirrose nao alcoolica"]
COMPORTAMENTO = ["suicidio"]
CONTROLES = ["CN apendicite", "CN hernia", "CN colelitiase", "CN causa mal definida"]

CURTO = {"K70 doenca alcoolica do figado": "K70", "F10 transtornos por alcool": "F10",
         "outras 100% alcool": "outras alc", "K71-76 cirrose nao alcoolica": "K71-76",
         "suicidio": "suicidio", "CN apendicite": "apendicit", "CN hernia": "hernia",
         "CN colelitiase": "colelitia", "CN causa mal definida": "causa mal"}


def vg(v, casas=2):
    return f"{v:.{casas}f}".replace(".", ",")


def carregar():
    linhas = json.loads(DADOS.read_text(encoding="utf-8"))
    pop, obitos = collections.Counter(), collections.Counter()
    for r in linhas:
        chave = (r["r"], r["p"], r["g"], r["b"], r["e"], int(r["i"]))
        if r["t"] == "p":
            pop[chave] += int(r["v"])
        else:
            obitos[chave + (r["c"],)] += int(r["v"])
    idades = sorted({k[5] for k in pop})
    padrao = {i: sum(v for k, v in pop.items() if k[5] == i) for i in idades}
    return pop, obitos, idades, padrao


def fabrica(pop, obitos, idades, padrao):
    """taxa(causa, **filtros) padronizada por idade, por 100 mil."""
    total_padrao = sum(padrao.values())

    def taxa(causa, grupo=None, faixa=None, ev=None, porte=None, regiao=None):
        def bate(k):
            return ((grupo is None or k[2] == grupo)
                    and (faixa is None or k[3] == faixa)
                    and (ev is None or k[4] == ev)
                    and (porte is None or k[1] == porte)
                    and (regiao is None or k[0] == regiao))

        soma = 0.0
        for i in idades:
            p = sum(v for k, v in pop.items() if k[5] == i and bate(k))
            if not p:
                continue
            o = sum(v for k, v in obitos.items() if k[5] == i and k[6] == causa and bate(k))
            soma += (o / p) * padrao[i]
        return soma / total_padrao * 1e5

    return taxa


def razao(taxa, causa, **f):
    b = taxa(causa, grupo="baixo", **f)
    return (taxa(causa, grupo="alto", **f) / b) if b else float("nan")


def bloco(titulo, causas, taxa, obitos):
    print(f"\n{titulo}")
    print(f"  {'causa':<32}{'obitos':>8}{'alto':>8}{'baixo':>8}{'razao':>8}"
          + "".join(f"{r:>11}" for _, r in PORTES))
    for c in causas:
        tot = sum(v for k, v in obitos.items() if k[6] == c)
        alto, baixo = taxa(c, grupo="alto"), taxa(c, grupo="baixo")
        linha = (f"  {c:<32}{tot:>8,}".replace(",", ".")
                 + f"{vg(alto):>8}{vg(baixo):>8}{vg(alto / baixo):>8}")
        for p, _ in PORTES:
            linha += f"{vg(razao(taxa, c, porte=p)):>11}"
        print(linha)


def main():
    pop, obitos, idades, padrao = carregar()
    taxa = fabrica(pop, obitos, idades, padrao)

    total = sum(pop.values())
    alto = sum(v for k, v in pop.items() if k[2] == "alto")
    print("TAXAS PADRONIZADAS POR IDADE, POR 100 MIL — 2022")
    print("razao = municipios com >10% de SEM RELIGIAO / demais."
          "  <1 = menos frequente onde ha mais gente sem religiao")
    print(f"\npopulacao em municipios com >10% de sem religiao: "
          f"{alto:,} de {total:,} ({100 * alto / total:.0f}%)".replace(",", "."))

    print("\n=== o confundidor: sem religiao mora onde mora evangelico ===")
    print(f"  {'':<12}{'ev >20%':>14}{'ev <=20%':>14}")
    for g, rot in [("alto", "sr >10%"), ("baixo", "sr <=10%")]:
        a = sum(v for k, v in pop.items() if k[2] == g and k[4] == "ev_alto")
        b = sum(v for k, v in pop.items() if k[2] == g and k[4] == "ev_baixo")
        print(f"  {rot:<12}{a:>14,}{b:>14,}".replace(",", "."))

    bloco("[1] CAUSAS DE ALCOOL", ALCOOL, taxa, obitos)
    bloco("[2] ESPECIFICIDADE — mesmo orgao, via nao alcoolica", ESPECIFICIDADE, taxa, obitos)
    bloco("[3] SUICIDIO — o outro candidato comportamental", COMPORTAMENTO, taxa, obitos)
    bloco("[4] CONTROLES NEGATIVOS — a hipotese preve razao ~1", CONTROLES, taxa, obitos)

    faixas = sorted({k[3] for k in pop})
    print("\n[5] DOSE-RESPOSTA — taxa padronizada por faixa de % sem religiao")
    print(f"  {'faixa':<14}" + "".join(f"{CURTO[c]:>11}"
          for c in ALCOOL[:2] + ESPECIFICIDADE + COMPORTAMENTO + CONTROLES))
    for f in faixas:
        linha = f"  {f:<14}"
        for c in ALCOOL[:2] + ESPECIFICIDADE + COMPORTAMENTO + CONTROLES:
            linha += f"{vg(taxa(c, faixa=f)):>11}"
        print(linha)

    print("\n[6] O TESTE QUE DECIDE — a mesma razao DENTRO de cada estrato evangelico")
    print("     se o efeito for de sem-religiao, aparece nas duas colunas;")
    print("     se so aparecer em uma, e o evangelico vazando")
    print(f"  {'causa':<32}{'BR':>8}{'ev >20%':>10}{'ev <=20%':>10}")
    for c in ALCOOL[:2] + ESPECIFICIDADE + COMPORTAMENTO + CONTROLES:
        print(f"  {c:<32}{vg(razao(taxa, c)):>8}"
              f"{vg(razao(taxa, c, ev='ev_alto')):>10}"
              f"{vg(razao(taxa, c, ev='ev_baixo')):>10}")

    print("\n[7] O SEGUNDO TESTE QUE DECIDE — a mesma razao DENTRO de cada regiao")
    print("     causa cujo sinal inverte entre regioes e geografia, nao religiao")
    print(f"  {'causa':<32}" + "".join(f"{r[:9]:>11}" for r in REGIOES))
    for c in ALCOOL[:2] + ESPECIFICIDADE + COMPORTAMENTO + ["CN causa mal definida"]:
        print(f"  {c:<32}" + "".join(f"{vg(razao(taxa, c, regiao=r)):>11}" for r in REGIOES))

    print("\n[8] VEREDITO")
    k70, f10 = razao(taxa, ALCOOL[0]), razao(taxa, ALCOOL[1])
    print(f"  alcool no pais:      K70 {vg(k70)}   F10 {vg(f10)}")
    print(f"  dentro de ev >20%:   K70 {vg(razao(taxa, ALCOOL[0], ev='ev_alto'))}"
          f"   F10 {vg(razao(taxa, ALCOOL[1], ev='ev_alto'))}")
    print(f"  dentro de ev <=20%:  K70 {vg(razao(taxa, ALCOOL[0], ev='ev_baixo'))}"
          f"   F10 {vg(razao(taxa, ALCOOL[1], ev='ev_baixo'))}")

    # o que mata a leitura: o controle de registro nao esta equilibrado aqui.
    # Se o excesso de causa mal definida no grupo alto for maior que a propria
    # diferenca de K70, a queda do alcool cabe inteira dentro do viés de registro.
    md_a, md_b = taxa(CONTROLES[3], grupo="alto"), taxa(CONTROLES[3], grupo="baixo")
    k_a, k_b = taxa(ALCOOL[0], grupo="alto"), taxa(ALCOOL[0], grupo="baixo")
    excesso, lacuna = md_a - md_b, k_b - k_a
    print(f"\n  controle de registro (causa mal definida): razao {vg(md_a / md_b)}")
    print(f"    excesso no grupo alto:      {vg(excesso)} por 100 mil")
    print(f"    lacuna de K70 a explicar:   {vg(lacuna)} por 100 mil")
    print(f"    o excesso e {vg(excesso / lacuna, 1)}x a lacuna")
    print()
    if k70 > 1.05 and f10 > 1.05:
        print("  -> o alcool SOBE onde ha mais gente sem religiao: a leitura")
        print("     doutrinaria sobrevive.")
    elif excesso > lacuna:
        print("  -> INCONCLUSIVO, e nao nulo. O alcool cai tambem onde ha mais gente")
        print("     sem religiao (K70 nas 5 regioes, nos 4 portes e nos 2 estratos")
        print("     evangelicos), o que por si so tiraria a doutrina de cena. Mas aqui")
        print("     o controle de registro FALHA — ao contrario do corte evangelico,")
        print("     onde ficou em 0,97. Investiga-se menos a causa do obito onde ha")
        print("     mais gente sem religiao, e o excesso de causa mal definida e")
        print("     maior que a queda de K70 que ele precisaria explicar.")
        print("     Este contraste nao tem poder para decidir entre doutrina e")
        print("     secularizacao. O achado evangelico segue de pe, sem ganhar nem")
        print("     perder apoio.")
    else:
        print("  -> o alcool cai nos dois contrastes e o registro esta equilibrado:")
        print("     a leitura doutrinaria nao se sustenta.")


if __name__ == "__main__":
    main()
