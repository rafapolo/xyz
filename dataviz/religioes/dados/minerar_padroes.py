"""
Minera padroes nas descricoes SEM classificacao do CNEFE e propoe novas linhas
para cnefe-descricao-vertente.csv.

PROBLEMA. 282.505 dos 765.591 templos (36,9%) ficam sem vertente porque o
dicionario curado so casa a grafia canonica. Sao dois buracos distintos:
descricoes com sinal denominacional claro fora do formato esperado
("COMUNIDADE BATISTA", "MISSAO BATISTA", "IGREIJA BATISTA" - o caso que
motivou este script) e descricoes que de fato nao tem sinal ("IGREJA", "SEM
NOME": 82 mil so na primeira). Alem disso o desempate por comprimento do
gerador deixa fallbacks genericos roubarem denominacao especifica.

METODO. Nao adivinhamos: o proprio corpo ja classificado e' a evidencia. Mas
a evidencia ingenua se auto-confirma - o n-grama "DE DEUS" parece 93%
Assembleia de Deus so porque o padrao "ASSEMBLEIA DE DEUS" o contem. Por isso
toda estatistica aqui usa EVIDENCIA HONESTA: ao avaliar um trecho g so contam
as linhas classificadas cujo rotulo veio de um padrao que NAO contem g. Se o
sinal sobrevive a isso, ele e' independente.

O dicionario ganha uma coluna `prioridade`; o gerador passa a ordenar por
(prioridade desc, comprimento desc) em vez de so comprimento.

  democao  (prio 10) - fallback generico rebaixado. "IGREJA EVANGELICA" ->
      Evangelica nao determinada tem 17 caracteres e por isso vencia "IGREJA
      BATISTA" (14): "IGREJA EVANGELICA QUADRANGULAR" estava como nao
      determinada. Detectamos esses casos comparando, em cada descricao,
      quem venceu contra quem tambem casava, e rebaixamos o guarda-chuva.

  marcador (prio 20) - token denominacional derivado do proprio dicionario
      curado (token que so aparece em padroes de uma unica vertente). Aceito
      quando sua DISCORDANCIA e' baixa: entre as linhas classificadas que o
      contem mas foram rotuladas por outro sinal, poucas apontam pra vertente
      diferente. Resolve BATISTA (contaminacao quase toda do idiomatismo
      catolico "SAO JOAO BATISTA") e rejeita PARA, BELEM, SOCIEDADE,
      MISSIONARIA (49% a 99% de discordancia). Um marcador reprovado ainda e'
      resgatado se as excecoes mineradas explicarem a discordancia dele.

  ngrama   (prio 40) - propagacao livre por co-ocorrencia, mesma evidencia
      honesta, pra nomes de denominacao que nao viraram marcador.

  excecao  (prio 60) - o contexto onde o marcador mente, minerado da propria
      discordancia que o aprovou: "SAO JOAO BATISTA" -> catolica ganha do
      marcador BATISTA por ter prioridade maior.

  grafia   (prio 90) - erro de digitacao. Corrige o token por similaridade
      contra o vocabulario canonico, roda o casador no texto corrigido e, se
      casar, propoe a grafia ERRADA como padrao. Protegido por um guarda de
      palavra-real (token frequente no corpus nao e' typo), senao "ESPIRITO"
      viraria "ESPIRITA" e o catolico "DIVINO ESPIRITO SANTO" iria pra
      espirita.

Os padroes curados ficam em 100. A simulacao final roda o dicionario inteiro
na ordem do gerador e DESCARTA qualquer candidato que reclassifique linha ja
rotulada - as unicas mudancas de rotulo permitidas sao as das democoes, que
sao correcoes de bug e saem listadas pra conferencia.

Nada e' aplicado sozinho: a saida e' candidatos_padroes.csv pra revisao, mais
residuo_sem_classificacao.csv com o que sobra (curadoria manual). `--aplicar`
grava o dicionario com democoes e candidatos.

Uso:
    python3 minerar_padroes.py                          # minera, escreve os CSVs
    python3 minerar_padroes.py --max-discordancia 0.05  # marcadores so muito limpos
    python3 minerar_padroes.py --aplicar                # grava no dicionario
"""

import argparse
import csv
import difflib
import re
from collections import Counter, defaultdict
from pathlib import Path

import duckdb

HERE = Path(__file__).parent
PADROES_CSV = HERE / "cnefe-descricao-vertente.csv"
VERTENTES_CSV = HERE / "vertentes-religiosas.csv"
PARQUET = HERE / "igrejas_geolocalizadas.parquet"
CANDIDATOS_CSV = HERE / "candidatos_padroes.csv"
RESIDUO_CSV = HERE / "residuo_sem_classificacao.csv"

PRIO_CURADO = 100
# marcador acima de ngrama: o marcador sai do dicionario curado e passa por
# teste de discordancia; o n-grama livre inclui hagionimos (JOSE, SEBASTIAO,
# LUZIA), que indicam catolica por padrao mas sao usados igual por casa
# sincretica. Com ngrama por cima, "TENDA DE SAO SEBASTIAO" virava catolica
# em vez de umbanda.
PRIO = {"democao": 95, "grafia": 90, "excecao": 60, "marcador": 50,
        "ngrama": 40, "fallback": 30, "hagionimo": 20}

# Um padrao rebaixado por democao fica logo ABAIXO do curado: ele so precisa
# perder pro padrao especifico que estava sendo roubado. "TERREIRO" cai na
# democao (perde pra "TERREIRO DE UMBANDA", correto), mas se fosse pro fundo
# passaria a perder tambem pros hagionimos e "TERREIRO SAO SEBASTIAO" viraria
# catolica.
#
# Estes aqui sao diferentes: nao sao termo primario de nada, sao a convencao
# de "e' evangelica e nao sabemos qual". Precisam perder pra qualquer sinal
# denominacional de verdade, entao vao pro 30 - abaixo das camadas mineradas,
# acima so dos hagionimos.
FALLBACKS_FRACOS = {
    "IGREJA EVANGELICA", "IGREJA PENTECOSTAL", "IGREJA EVANGELICA PENTECOSTAL",
    "IGREJA PENTENCOSTAL", "IGREJA PETENCOSTAL", "IGREJA MISSIONARIA PENTECOSTAL",
    "IGREJA MISSIONARIA PETENCOSTAL", "ASSEMBLEIA", "IGREJA APOSTOLICA",
}

# Nome de santo/invocacao mariana e' a evidencia mais fraca do conjunto: indica
# catolica so na AUSENCIA de qualquer outro sinal, porque casa de umbanda e
# centro espirita usam os mesmos nomes (sincretismo). Por isso qualquer
# candidato catolico que nao traga um termo institucional junto vai pro fundo
# da ordem, atras ate' dos fallbacks.
INSTITUCIONAL_CATOLICO = {
    "IGREJA", "PAROQUIA", "CAPELA", "CATEDRAL", "SANTUARIO", "DIOCESE",
    "MATRIZ", "CATOLICA", "CATOLICO", "ROMANA", "MOSTEIRO", "CONVENTO",
    "PASTORAL", "COMUNIDADE", "CRUZEIRO",
}


def eh_hagionimo(proposta):
    return (proposta["vertente_id"] == "95263"
            and not any(t in INSTITUCIONAL_CATOLICO
                        for t in proposta["padrao"].split()))

NGRAMA_MAX = 4

# baldes guarda-chuva: quando um padrao que aponta pra ca vence um padrao que
# aponta pra denominacao especifica, o vencedor e' fallback e deve ser rebaixado
BALDES_GENERICOS = {
    "121096",  # Evangelica nao determinada
    "95265",   # Evangelicas de origem pentecostal (guarda-chuva)
    "99743",   # Evangelicas de Missao - outras
    "99748",   # Evangelicas de origem pentecostal - outras
    "2827",    # Umbanda e Candomble (guarda-chuva)
    "95264", "95266", "95267",
}

# tokens sem poder discriminante: n-grama feito so deles nao vira candidato e
# eles nunca viram marcador ("CASA DE ORACAO" ainda vira, ORACAO nao esta aqui)
GENERICOS = {
    "IGREJA", "IGREJAS", "TEMPLO", "COMUNIDADE", "MINISTERIO", "CONGREGACAO",
    "CASA", "CENTRO", "SALAO", "SEDE", "MISSAO", "OBRA", "PONTO", "GRUPO",
    "DE", "DA", "DO", "DAS", "DOS", "E", "EM", "A", "O", "AS", "OS", "NO",
    "NA", "COM", "PARA", "SEM", "NOME", "SN", "S", "N", "VAGO", "NAO", "TEM",
    "DEUS", "JESUS", "CRISTO", "SENHOR", "BRASIL", "EVANGELICA", "EVANGELICO",
    "CRISTA", "CRISTAO", "REINO", "DIA", "GRACA", "PODER", "AMOR", "FE",
    "VIDA", "NOVA", "NOVO", "PRIMEIRA", "SEGUNDA", "CENTRAL", "MUNDIAL",
    "1", "2", "3", "4", "5", "7", "I", "II", "III",
}

# um trecho com isso nao vira padrao de vertente: mesmo quando a evidencia
# aponta forte pra catolica (cemiterio de igreja), o que ele identifica e' o
# tipo de equipamento, nao a religiao de quem congrega ali
NAO_TEMPLO = {"CEMITERIO", "VELORIO", "MORTUARIA", "JAZIGO", "CREMATORIO",
              "FUNERARIA", "OSSARIO", "SEPULTAMENTO"}

# descricoes que nao sao templo ou que nunca terao sinal - saem do residuo
# pra ele ficar util pra curadoria
RUIDO = re.compile(
    r"^(IGREJA|IGREJINHA|IGREIJA|IGREJAS|CAPELINHA|SEM NOME|SEM DENOMINACAO|"
    r"VAGO|NAO TEM|NAO TEM NOME|SN|S/N|CEMITERIO|BARRACAO|CENTRO|CONGREGACAO|"
    r"EM CONSTRUCAO|IGREJA SEM NOME|IGREJA SEM DENOMINACAO|CASA|TEMPLO|SALAO|"
    r"CULTO|CRENTE|CRENTES|IGREJA EVANGELICA SEM NOME)$"
)


# ----------------------------------------------------------------- entradas

def carregar_padroes():
    with open(PADROES_CSV, encoding="utf-8") as f:
        rows = list(csv.DictReader(f))
    for r in rows:
        r["vertente_id"] = str(r["vertente_id"])
        if not r.get("prioridade"):
            r["prioridade"] = str(PRIO_CURADO)
    repetidos = [p for p, c in Counter(r["padrao"] for r in rows).items() if c > 1]
    if repetidos:
        raise SystemExit(
            f"padrao duplicado em {PADROES_CSV.name} (o desempate viraria sorte "
            f"da ordem do arquivo): {', '.join(sorted(repetidos)[:10])}")
    return rows, [r for r in rows if r["excluir"] != "true"]


def carregar_vertentes():
    with open(VERTENTES_CSV, encoding="utf-8") as f:
        return {r["id"]: r["nome"] for r in csv.DictReader(f)}


def fazer_casador(regras):
    """Mesma semantica do gerador: substring, ordenado por (prioridade desc,
    comprimento desc)."""
    pares = sorted(
        ((r["padrao"], str(r["vertente_id"]), int(r.get("prioridade") or PRIO_CURADO))
         for r in regras),
        key=lambda x: (-x[2], -len(x[0])),
    )
    pares = [(p, v) for p, v, _ in pares]

    def casar(texto):
        for padrao, vid in pares:
            if padrao in texto:
                return padrao, vid
        return None, None

    return casar


def carregar_corpus():
    con = duckdb.connect()
    linhas = con.execute(
        f"""
        SELECT descricao_estabelecimento AS d, count(*) AS n
        FROM read_parquet('{PARQUET}')
        WHERE descricao_estabelecimento IS NOT NULL
        GROUP BY 1
        """
    ).fetchall()
    con.close()
    return linhas


def indexar(corpus, casar):
    """(descricao, ocorrencias, vertente_id, padrao_que_rotulou) - o padrao e'
    o que torna possivel medir evidencia honesta."""
    return [(d, n) + casar(d)[::-1] for d, n in corpus]


def ngramas(texto, contendo=None):
    toks = texto.split()
    saida = set()
    for tam in range(1, NGRAMA_MAX + 1):
        for i in range(len(toks) - tam + 1):
            janela = toks[i:i + tam]
            if all(t in GENERICOS for t in janela):
                continue
            if any(t in NAO_TEMPLO for t in janela):
                continue
            if contendo and contendo not in janela:
                continue
            g = " ".join(janela)
            if len(g) >= 4:
                saida.add(g)
    return saida


def construir_evidencia(idx, min_suporte):
    """Indice invertido n-grama -> {vertente: ocorrencias}, so com evidencia
    honesta. Duas passadas: a primeira poda por suporte pra segunda nao
    materializar milhoes de Counters."""
    bruto = Counter()
    for d, n, vid, padrao in idx:
        if vid is None:
            continue
        for g in ngramas(d):
            bruto[g] += n
    vivos = {g for g, c in bruto.items() if c >= min_suporte}

    evid = defaultdict(Counter)
    for d, n, vid, padrao in idx:
        if vid is None:
            continue
        for g in ngramas(d):
            if g in vivos and g not in padrao:
                evid[g][vid] += n
    return evid


def perfil_sem_classe(idx):
    """n-grama -> (ocorrencias sem classe, exemplos)."""
    ganho = Counter()
    exemplos = defaultdict(list)
    for d, n, vid, _ in idx:
        if vid is not None:
            continue
        for g in ngramas(d):
            ganho[g] += n
            if len(exemplos[g]) < 3:
                exemplos[g].append(d)
    return ganho, exemplos


# ----------------------------------------------- camada 0: demover fallbacks

def detectar_democoes(idx, positivos):
    """Fallback generico que so venceu por ser mais comprido que o padrao
    especifico que tambem casava."""
    especificos = [(r["padrao"], r["vertente_id"]) for r in positivos
                   if r["vertente_id"] not in BALDES_GENERICOS]
    peso = Counter()
    exemplos = defaultdict(list)

    for d, n, vid, padrao in idx:
        if vid not in BALDES_GENERICOS or not padrao:
            continue
        perdedores = {v for p, v in especificos if p in d and p != padrao}
        if perdedores:
            peso[padrao] += n
            if len(exemplos[padrao]) < 3:
                exemplos[padrao].append(d)

    return [{"padrao": p, "peso": c, "exemplos": exemplos[p]}
            for p, c in peso.most_common()]


# ----------------------------------------------------- camada 1: marcadores

def derivar_marcadores(positivos):
    """Token que so aparece em padroes de uma unica vertente. Nao inventamos
    marcador: ele sai do dicionario ja curado a mao."""
    tok2v = defaultdict(set)
    for p in positivos:
        for t in p["padrao"].split():
            if t not in GENERICOS and len(t) >= 4:
                tok2v[t].add(p["vertente_id"])
    return {t: next(iter(vs)) for t, vs in tok2v.items() if len(vs) == 1}


def avaliar_marcadores(idx, marcadores, fracos=frozenset()):
    """Para cada marcador: suporte, ganho, e as linhas classificadas onde ele
    discorda (rotulo veio de outro sinal e aponta pra outra vertente).

    Rotulo posto por padrao fraco (prioridade abaixo da cheia: fallback
    guarda-chuva, democao) nao conta como discordancia. Ele nao e' uma
    afirmacao sobre a igreja, e' o dicionario dizendo "nao sei" - e cobrar
    coerencia com isso reprovava ASEMBLEIA/ASSENBLEIA, cuja discordancia era
    quase toda "IGREJA EVANGELICA ASEMBLEIA DE DEUS -> nao determinada"."""
    total = Counter()
    ganho = Counter()
    discordantes = defaultdict(list)

    for d, n, vid, padrao in idx:
        hits = [m for m in marcadores if m in d.split()]
        if not hits:
            continue
        for m in hits:
            if vid is None:
                ganho[m] += n
            else:
                total[m] += n
                if m not in padrao and vid != marcadores[m] and padrao not in fracos:
                    discordantes[m].append((d, n, vid))

    return {
        m: {
            "padrao": m, "vertente_id": v, "camada": "marcador",
            "prioridade": PRIO["marcador"], "ganho": ganho[m],
            "suporte": total[m], "exemplos": "",
            "discordantes": discordantes[m],
            "discordancia": (sum(n for _, n, _ in discordantes[m]) / total[m]
                             if total[m] else 1.0),
        }
        for m, v in marcadores.items()
    }


def excecoes_do_marcador(mk, evid, ganho_sc, exemplos_sc, args):
    """Contextos que contradizem o marcador. Candidatos saem das linhas onde
    ele comprovadamente erra; o rotulo sai da evidencia honesta."""
    m, v_marcador = mk["padrao"], mk["vertente_id"]
    cand = Counter()
    for d, n, _ in mk["discordantes"]:
        for g in ngramas(d, contendo=m):
            if g != m:
                cand[g] += n

    saida = []
    for g in cand:
        dist = evid.get(g)
        if not dist:
            continue
        suporte = sum(dist.values())
        if suporte < args.min_suporte_excecao:
            continue
        vid, dom = dist.most_common(1)[0]
        pureza = dom / suporte
        if vid == v_marcador or pureza < args.min_pureza:
            continue
        # excecao so vale pra corrigir a vertente, nunca pra apagar
        # especificidade. "EVANGELICA BATISTA" -> Evangelica nao determinada
        # tinha 99,8% de pureza, mas so porque o fallback "IGREJA EVANGELICA"
        # e' que estava rotulando essas linhas - aprender isso e' aprender o
        # bug. Uma igreja que se diz batista e' batista.
        if vid in BALDES_GENERICOS and v_marcador not in BALDES_GENERICOS:
            continue
        saida.append({
            "padrao": g, "vertente_id": vid, "camada": "excecao",
            "prioridade": PRIO["excecao"], "ganho": ganho_sc.get(g, 0),
            "pureza": round(pureza, 4), "suporte": suporte,
            "exemplos": " | ".join(exemplos_sc.get(g, [])),
        })
    return dedup_por_cobertura(saida)


def discordancia_residual(mk, excecoes):
    """Quanto da discordancia sobra depois que as excecoes cobrem o contexto
    culpado. E' o teste que resgata marcadores como SANTO e CATEDRAL."""
    if not mk["suporte"]:
        return 1.0
    coberto = {(p["padrao"], p["vertente_id"]) for p in excecoes}
    resta = 0
    for d, n, vid in mk["discordantes"]:
        if not any(p in d and v == vid for p, v in coberto):
            resta += n
    return resta / mk["suporte"]


# ------------------------------------------------- camada 2: n-gramas livres

def minerar_ngramas(evid, ganho_sc, exemplos_sc, ja_usados, args):
    propostas = []
    for g, gan in ganho_sc.items():
        if gan < args.min_ganho or g in ja_usados:
            continue
        dist = evid.get(g)
        if not dist:
            continue
        suporte = sum(dist.values())
        if suporte < args.min_suporte:
            continue
        vid, dom = dist.most_common(1)[0]
        pureza = dom / suporte
        if pureza < args.min_pureza:
            continue
        propostas.append({
            "padrao": g, "vertente_id": vid, "camada": "ngrama",
            "prioridade": PRIO["ngrama"], "ganho": gan,
            "pureza": round(pureza, 4), "suporte": suporte,
            "exemplos": " | ".join(exemplos_sc[g]),
        })
    return dedup_por_cobertura(propostas)


def dedup_por_cobertura(propostas):
    """Padrao mais curto que ja cobre outro, com a mesma vertente, torna o
    mais longo redundante ("BATISTA" cobre "COMUNIDADE BATISTA")."""
    propostas.sort(key=lambda p: (len(p["padrao"]), -p["ganho"]))
    aceitos = []
    for p in propostas:
        if any(a["padrao"] in p["padrao"] and a["vertente_id"] == p["vertente_id"]
               for a in aceitos):
            continue
        aceitos.append(p)
    return aceitos


# --------------------------------------------------------- camada 3: grafia

def minerar_grafia(idx, positivos, casar, args):
    vocab = sorted({t for p in positivos for t in p["padrao"].split() if len(t) >= 5})
    vocab_set = set(vocab)

    # guarda de palavra-real: token frequente no corpus e' palavra legitima,
    # nao typo. Sem ele ESPIRITO vira ESPIRITA e o catolico "DIVINO ESPIRITO
    # SANTO" cai em espirita.
    freq = Counter()
    for d, n, _, _ in idx:
        for t in set(d.split()):
            freq[t] += n
    protegidos = {t for t, c in freq.items() if c >= args.min_freq_palavra_real}

    cache = {}

    def corrigir(tok):
        if tok not in cache:
            alvo = None
            if tok not in vocab_set and tok not in protegidos and len(tok) >= 5:
                perto = difflib.get_close_matches(
                    tok, vocab, n=1, cutoff=args.min_similaridade)
                if perto:
                    alvo = perto[0]
            cache[tok] = alvo
        return cache[tok]

    agregado = defaultdict(lambda: {"ganho": 0, "exemplos": []})
    for d, n, vid, _ in idx:
        if vid is not None:
            continue
        toks = d.split()
        corrigidos, trocas = [], 0
        for t in toks:
            alvo = corrigir(t)
            corrigidos.append(alvo or t)
            trocas += 1 if alvo else 0
        if not trocas or trocas > args.max_trocas:
            continue
        padrao, novo = casar(" ".join(corrigidos))
        if not novo:
            continue
        # quem vira regra e' a grafia como esta' no dado bruto, nao a corrigida
        p_toks = padrao.split()
        janela = None
        for i in range(len(corrigidos) - len(p_toks) + 1):
            if corrigidos[i:i + len(p_toks)] == p_toks:
                janela = " ".join(toks[i:i + len(p_toks)])
                break
        # truncagem nao e' erro de digitacao. "IGREJA EVANGELIC" e' prefixo de
        # "IGREJA EVANGELICA", e entrando em prio 90 passava na frente do
        # curado "IGREJA EVANGELICA PENTECOSTAL": 1.563 templos pentecostais
        # caiam em "nao determinada". Grafia so vale quando a janela e' de
        # fato uma variante, nao um pedaco.
        if janela is None or janela in padrao or padrao in janela:
            continue
        info = agregado[(janela, novo)]
        info["ganho"] += n
        if len(info["exemplos"]) < 3:
            info["exemplos"].append(d)

    return [
        {"padrao": p, "vertente_id": v, "camada": "grafia",
         "prioridade": PRIO["grafia"], "ganho": i["ganho"], "pureza": 1.0,
         "suporte": 0, "exemplos": " | ".join(i["exemplos"])}
        for (p, v), i in agregado.items() if i["ganho"] >= args.min_ganho_grafia
    ]


# ------------------------------------------------------------- simulacao

def simular(idx_base, positivos, propostas, demovidos=frozenset()):
    """idx_base ja tem as democoes aplicadas. Descarta candidato que mude
    rotulo vindo de padrao curado em prioridade cheia; devolve o conjunto
    limpo. Mudanca sobre rotulo de fallback REBAIXADO nao conta - e' o efeito
    pretendido da democao (era ela que estava roubando a denominacao)."""
    def rodar(cands):
        casar = fazer_casador(positivos + cands)
        ganhos, refinados, culpados = 0, 0, Counter()
        for d, n, vid, origem in idx_base:
            padrao, novo = casar(d)
            if vid is None and novo is not None:
                ganhos += n
            elif vid is not None and novo is not None and novo != vid:
                if origem in demovidos:
                    refinados += n
                else:
                    culpados[padrao] += n
        return ganhos, refinados, culpados

    descartados, atuais = [], list(propostas)
    for _ in range(6):
        _, _, culpados = rodar(atuais)
        if not culpados:
            break
        ruins = set(culpados)
        for p in atuais:
            if p["padrao"] in ruins:
                p["motivo"] = f"reclassificaria {culpados[p['padrao']]} templos"
                descartados.append(p)
        atuais = [p for p in atuais if p["padrao"] not in ruins]

    ganhos, refinados, culpados = rodar(atuais)
    return atuais, descartados, ganhos, refinados, culpados


# ---------------------------------------------------------------- saidas

def escrever_residuo(idx_base, positivos, propostas, limite=500):
    casar = fazer_casador(positivos + propostas)
    sobra = [(d, n) for d, n, vid, _ in idx_base
             if vid is None and casar(d)[1] is None and not RUIDO.match(d)]
    sobra.sort(key=lambda x: -x[1])
    with open(RESIDUO_CSV, "w", encoding="utf-8", newline="") as f:
        w = csv.writer(f)
        w.writerow(["descricao", "ocorrencias"])
        w.writerows(sobra[:limite])
    return len(sobra), sum(n for _, n in sobra)


CAMPOS = ["padrao", "vertente_id", "vertente_nome", "camada", "prioridade",
          "ganho", "pureza", "suporte", "exemplos"]


def escrever_candidatos(propostas, nomes):
    propostas.sort(key=lambda p: (-p["prioridade"], -p["ganho"]))
    with open(CANDIDATOS_CSV, "w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=CAMPOS, extrasaction="ignore")
        w.writeheader()
        for p in propostas:
            w.writerow({**p, "vertente_nome": nomes.get(p["vertente_id"], "")})


COLUNAS_DICT = ["padrao", "vertente_id", "fonte", "confianca", "excluir", "prioridade"]


def aplicar(propostas, todas_linhas):
    with open(PADROES_CSV, "w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=COLUNAS_DICT, extrasaction="ignore")
        w.writeheader()
        for r in todas_linhas:
            w.writerow(r)
        for p in sorted(propostas, key=lambda p: (-p["prioridade"], -p["ganho"])):
            w.writerow({
                "padrao": p["padrao"], "vertente_id": p["vertente_id"],
                "fonte": f"mineracao_{p['camada']}",
                "confianca": "alta" if p.get("pureza", 1) >= 0.97 else "media",
                "excluir": "false", "prioridade": p["prioridade"],
            })


# ------------------------------------------------------------------ pipeline

def minerar(idx, positivos, casar, args, verboso=True):
    """As quatro camadas sobre um indice ja construido. Isolado de main pra
    que --validar possa rodar o mesmo pipeline so com a metade de treino."""
    evid = construir_evidencia(idx, args.min_suporte_excecao)
    ganho_sc, exemplos_sc = perfil_sem_classe(idx)

    fracos = {r["padrao"] for r in positivos
              if int(r.get("prioridade") or PRIO_CURADO) < PRIO_CURADO}
    marcadores = derivar_marcadores(positivos)
    avaliados = avaliar_marcadores(idx, marcadores, fracos)
    mk_ok, mk_no, excecoes = [], [], []
    for mk in avaliados.values():
        exc = excecoes_do_marcador(mk, evid, ganho_sc, exemplos_sc, args)
        residual = discordancia_residual(mk, exc)
        mk["pureza"] = round(1 - residual, 4)
        if mk["suporte"] < args.min_suporte or mk["ganho"] < args.min_ganho:
            mk["motivo"] = f"suporte {mk['suporte']}, ganho {mk['ganho']}"
            mk_no.append(mk)
        elif residual > args.max_discordancia:
            mk["motivo"] = (f"discordancia {mk['discordancia']:.1%}"
                            + (f" ({residual:.1%} apos {len(exc)} excecoes)" if exc else ""))
            mk_no.append(mk)
        else:
            mk_ok.append(mk)
            excecoes.extend(exc)
    excecoes = dedup_por_cobertura(excecoes)

    if verboso:
        print(f"marcadores: {len(mk_ok)} aceitos, {len(mk_no)} rejeitados "
              f"(de {len(marcadores)} derivados do dicionario)")
        for m in sorted(mk_ok, key=lambda x: -x["ganho"])[:14]:
            print(f"  + {m['padrao']:<16} {m['vertente_id']:>7}  ganho {m['ganho']:>6}  "
                  f"discordancia {m['discordancia']:>5.1%} -> {1 - m['pureza']:>5.1%}")
        for m in sorted(mk_no, key=lambda x: -x["ganho"])[:8]:
            print(f"  - {m['padrao']:<16} {m['vertente_id']:>7}  "
                  f"ganho {m['ganho']:>6}  {m['motivo']}")
        print(f"\nexcecoes: {len(excecoes)}")
        for p in sorted(excecoes, key=lambda x: -x["ganho"])[:8]:
            print(f"  ! {p['padrao']:<32} -> {p['vertente_id']:>7}  "
                  f"ganho {p['ganho']:>5}  pureza {p['pureza']:.1%}")

    ja = {p["padrao"] for p in mk_ok + excecoes}
    ng = minerar_ngramas(evid, ganho_sc, exemplos_sc, ja, args)
    gr = [p for p in minerar_grafia(idx, positivos, casar, args)
          if p["padrao"] not in ja | {x["padrao"] for x in ng}]
    if verboso:
        print(f"\nn-gramas: {len(ng)}   grafia: {len(gr)}")

    propostas = mk_ok + excecoes + ng + gr
    for p in propostas:
        p.pop("discordantes", None)
        # excecao fica de fora: "JOAO BATISTA" e' hagionimo, sim, mas existe
        # exatamente pra ganhar do marcador BATISTA. Rebaixa-la pro fundo
        # devolvia "IGREJA DE SAO JOAO BATISTA" pra batista.
        if p["camada"] != "excecao" and eh_hagionimo(p):
            p["camada"], p["prioridade"] = "hagionimo", PRIO["hagionimo"]
    return propostas


def carregar_arvore():
    """id -> id_pai, pra medir acerto tambem no nivel grosso (as 9 categorias
    que o mapa mostra por padrao)."""
    with open(VERTENTES_CSV, encoding="utf-8") as f:
        return {r["id"]: (r["id_pai"] or None) for r in csv.DictReader(f)}


ANCORAS_GROSSAS = {"95265", "95263", "95264", "121096", "2826", "2827", "2824"}


def grossa(vid, arvore):
    cur, visto = vid, set()
    while cur and cur not in visto:
        if cur in ANCORAS_GROSSAS:
            return cur
        visto.add(cur)
        cur = arvore.get(cur)
    return "OUTRAS"


def validar(idx, positivos, args, nomes):
    """Holdout POR PADRAO CURADO, nao por descricao.

    Esconder descricoes aleatorias mede a coisa errada: uma unica string
    gigante ("ASSEMBLEIA DE DEUS", dezenas de milhares de templos) caindo no
    teste domina a metrica e o resultado vira ruido de sorteio. E o que
    queremos saber e' outra coisa - quando o dicionario TEM UMA LACUNA, a
    mineracao a preenche corretamente?

    Entao removemos 30% dos padroes curados. As linhas que eles rotulavam
    voltam a ser "sem classificacao", que e' exatamente a situacao de
    producao: texto com sinal denominacional real que o dicionario nao cobre.
    Mineramos com o dicionario mutilado e conferimos contra o rotulo do
    dicionario inteiro.

    So entram no sorteio padroes de DENOMINACAO ESPECIFICA. Esconder um
    fallback ("IGREJA EVANGELICA" -> Evangelica nao determinada) nao testa
    nada: o rotulo dele nao e' um fato sobre a igreja, e' a convencao de onde
    o dicionario joga o que nao reconhece. Cobrar isso da mineracao mediria a
    capacidade de adivinhar a nossa propria convencao, nao a de acertar a
    denominacao."""
    import random
    rnd = random.Random(args.semente)
    sorteaveis = [p for p in positivos if p["vertente_id"] not in BALDES_GENERICOS]
    escondidos = {p["padrao"] for p in sorteaveis if rnd.random() < 0.30}
    parciais = [p for p in positivos if p["padrao"] not in escondidos]

    corpus = [(d, n) for d, n, _, _ in idx]
    verdade = {d: v for d, _, v, _ in idx}
    casar_parcial = fazer_casador(parciais)
    idx_treino = indexar(corpus, casar_parcial)

    propostas = minerar(idx_treino, parciais, casar_parcial, args, verboso=False)
    casar_prod = fazer_casador(parciais + propostas)   # como rodaria em producao
    arvore = carregar_arvore()

    acertos = erros = vagos = sem_palpite = acertos_grossos = 0
    piores = Counter()
    for (d, n, vid_parcial, _) in idx_treino:
        real = verdade[d]
        if real is None or vid_parcial is not None:
            continue          # so interessa o que a lacuna deixou sem rotulo
        _, palpite = casar_prod(d)
        if palpite is None:
            sem_palpite += n
        elif palpite == real:
            acertos += n
            acertos_grossos += n
        elif palpite in BALDES_GENERICOS and real not in BALDES_GENERICOS:
            # cair no guarda-chuva quando a verdade e' uma denominacao dele
            # nao e' errar, e' nao se comprometer - o mesmo que o dicionario
            # curado faz quando so reconhece "IGREJA EVANGELICA"
            vagos += n
            if grossa(palpite, arvore) == grossa(real, arvore):
                acertos_grossos += n
        else:
            erros += n
            if grossa(palpite, arvore) == grossa(real, arvore):
                acertos_grossos += n
            piores[(real, palpite)] += n

    coberto = acertos + erros + vagos
    alvo = coberto + sem_palpite
    if not alvo:
        print("holdout nao criou lacuna nenhuma")
        return
    print(f"validacao holdout por padrao (semente {args.semente}): "
          f"{len(escondidos)} dos {len(sorteaveis)} padroes de denominacao escondidos")
    print(f"  lacuna criada: {alvo:,} templos que perderam o rotulo")
    print(f"  cobertura: {coberto / alvo:.1%} recebem palpite da mineracao")
    if coberto:
        decisivo = acertos + erros
        print(f"  dos que recebem palpite: {acertos / coberto:.1%} exatos, "
              f"{vagos / coberto:.1%} no balde generico, {erros / coberto:.1%} errados")
        if decisivo:
            print(f"  precisao quando se compromete: {acertos / decisivo:.1%}")
        print(f"  acerto na categoria grossa (o que o mapa mostra): "
              f"{acertos_grossos / coberto:.1%}")
    if piores:
        print("\n  piores confusoes (verdade -> palpite):")
        for (v, p), n in piores.most_common(6):
            print(f"    {n:>6}  {nomes.get(v, v)[:34]:<34} -> {nomes.get(p, p)[:34]}")


# ------------------------------------------------------------------- main

def main():
    ap = argparse.ArgumentParser(
        description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--min-ganho", type=int, default=20,
                    help="minimo de templos sem classe que o padrao destrava")
    ap.add_argument("--min-suporte", type=int, default=30,
                    help="minimo de templos classificados como evidencia honesta")
    ap.add_argument("--min-pureza", type=float, default=0.90,
                    help="fracao da vertente dominante na evidencia honesta")
    ap.add_argument("--max-discordancia", type=float, default=0.10,
                    help="teto de contaminacao pra aceitar um marcador")
    ap.add_argument("--min-suporte-excecao", type=int, default=20)
    ap.add_argument("--min-similaridade", type=float, default=0.86)
    ap.add_argument("--max-trocas", type=int, default=2)
    ap.add_argument("--min-ganho-grafia", type=int, default=5)
    ap.add_argument("--min-freq-palavra-real", type=int, default=300,
                    help="acima disso o token e' palavra legitima, nunca typo")
    ap.add_argument("--sem-democoes", action="store_true",
                    help="nao rebaixa os fallbacks genericos")
    ap.add_argument("--validar", action="store_true",
                    help="holdout 70/30: mede a precisao dos padroes minerados")
    ap.add_argument("--semente", type=int, default=7)
    ap.add_argument("--aplicar", action="store_true")
    args = ap.parse_args()

    todas, positivos = carregar_padroes()
    nomes = carregar_vertentes()
    corpus = carregar_corpus()
    idx = indexar(corpus, fazer_casador(positivos))

    total = sum(n for _, n in corpus)
    sem0 = sum(n for _, n, v, _ in idx if v is None)
    print(f"corpus: {total:,} templos, {len(corpus):,} descricoes distintas")
    print(f"sem classificacao: {sem0:,} ({sem0 / total:.1%})\n")

    # --- camada 0
    democoes = [] if args.sem_democoes else detectar_democoes(idx, positivos)
    if democoes:
        print(f"fallbacks a rebaixar ({len(democoes)}): guarda-chuva vencendo "
              f"denominacao especifica so por ser mais comprido")
        for d in democoes[:6]:
            print(f"  v {d['padrao']:<22} {d['peso']:>6} templos  ex: {d['exemplos'][0]}")
        alvo = {d["padrao"] for d in democoes} | FALLBACKS_FRACOS
        for r in todas:
            if r["padrao"] in alvo:
                r["prioridade"] = str(PRIO["fallback"] if r["padrao"] in FALLBACKS_FRACOS
                                      else PRIO["democao"])
        positivos = [r for r in todas if r["excluir"] != "true"]
        casar = fazer_casador(positivos)
        idx = indexar(corpus, casar)
        corrigidos = sum(n for (d, n, v0, _), (_, _, v1, _) in
                         zip(indexar(corpus, fazer_casador(
                             [dict(r, prioridade=str(PRIO_CURADO)) for r in positivos])), idx)
                         if v0 != v1 and v0 is not None)
        print(f"  -> {corrigidos:,} templos corrigidos de vertente\n")
    casar = fazer_casador(positivos)

    if args.validar:
        validar(idx, positivos, args, nomes)
        return

    propostas = minerar(idx, positivos, casar, args)

    # qualquer padrao deixado abaixo da prioridade cheia esta' declarado como
    # sobrepujavel - por democao automatica ou porque o curador o marcou fraco
    demovidos = {r["padrao"] for r in positivos
                 if int(r.get("prioridade") or PRIO_CURADO) < PRIO_CURADO}
    propostas, descartados, ganhos, refinados, culpados = simular(
        idx, positivos, propostas, demovidos)
    if descartados:
        print(f"\ndescartados na simulacao ({len(descartados)}):")
        for p in sorted(descartados, key=lambda x: -x["ganho"])[:10]:
            print(f"  x {p['padrao']:<32} {p['camada']:<9} {p['motivo']}")
    assert not culpados, f"sobrou reclassificacao: {culpados.most_common(5)}"

    sem1 = sum(n for _, n, v, _ in idx if v is None)
    print(f"\nresultado: +{ganhos:,} templos classificados "
          f"({ganhos / sem1:.1%} do que faltava)")
    print(f"           sem classe cai de {sem0:,} ({sem0 / total:.1%}) "
          f"para {sem1 - ganhos:,} ({(sem1 - ganhos) / total:.1%})")
    if refinados:
        print(f"           + {refinados:,} templos saem de balde generico "
              f"pra denominacao especifica")

    n_res, peso_res = escrever_residuo(idx, positivos, propostas)
    escrever_candidatos(propostas, nomes)
    print(f"\ncandidatos -> {CANDIDATOS_CSV.name} ({len(propostas)} padroes)")
    print(f"residuo    -> {RESIDUO_CSV.name} "
          f"({n_res:,} descricoes, {peso_res:,} templos, ja sem o ruido)")

    if args.aplicar:
        aplicar(propostas, todas)
        print(f"\naplicado: {len(propostas)} linhas + {len(democoes)} democoes "
              f"em {PADROES_CSV.name}")
        print("rode gerar_igrejas_geolocalizadas.py e gerar_data_json.py pra propagar")
    else:
        print("\nrevise o CSV e rode com --aplicar pra gravar no dicionario")


if __name__ == "__main__":
    main()
