#!/usr/bin/env python3
"""Gera o índice estático dos 5.571 municípios e o sitemap deles.

Entrada: data/municipios.json (id, nome, uf), o mesmo que vai ao bucket (a recoleta do
lote o produz), e data/<id>.json de cada município, para o resumo. Saída, versionada:
  index.html                 HTML puro, agrupado por UF, um <a href="<id>/"> por município; o
                             ?id= antigo redireciona para /dataviz/municipios/<id>/
  <id>/index.html            a página de cada município: título, descrição, canonical e um
                             resumo em HTML puro (o que o Google lê), e depois troca o documento
                             pelo painel.html, mantendo o próprio bloco <!-- painel:seo -->.
                             O GitHub Pages ignora a query string: com ?id= os 5.571 endereços
                             recebiam o mesmo HTML e o Search Console os marcava como cópias.
  ../../sitemap-municipios.xml   as 5.571 URLs /dataviz/municipios/<id>/ (robots.txt aponta
                                  para ele, via scripts/gera_seo.ts)
Uso: python3 dataviz/municipios/gera_indice.py [municipios.json]
"""
import json
import re
import sys
import unicodedata
from datetime import date
from html import escape
from pathlib import Path

AQUI = Path(__file__).resolve().parent
RAIZ = AQUI.parent.parent
BASE = "https://xn--2dk.xyz"
BUCKET = "https://xyz-municipio.hel1.your-objectstorage.com/"
UFS = {"AC": "Acre", "AL": "Alagoas", "AM": "Amazonas", "AP": "Amapá", "BA": "Bahia", "CE": "Ceará",
       "DF": "Distrito Federal", "ES": "Espírito Santo", "GO": "Goiás", "MA": "Maranhão", "MG": "Minas Gerais",
       "MS": "Mato Grosso do Sul", "MT": "Mato Grosso", "PA": "Pará", "PB": "Paraíba", "PE": "Pernambuco",
       "PI": "Piauí", "PR": "Paraná", "RJ": "Rio de Janeiro", "RN": "Rio Grande do Norte", "RO": "Rondônia",
       "RR": "Roraima", "RS": "Rio Grande do Sul", "SC": "Santa Catarina", "SE": "Sergipe", "SP": "São Paulo",
       "TO": "Tocantins"}


def chave(t):
    return unicodedata.normalize("NFD", t).encode("ascii", "ignore").decode().lower()


def num(n, casas=0):
    return f"{n:,.{casas}f}".replace(",", "X").replace(".", ",").replace("X", ".")


def reais(v):
    for lim, nome in ((1e12, "trilhão" if v < 2e12 else "trilhões"), (1e9, "bilhão" if v < 2e9 else "bilhões"),
                      (1e6, "milhão" if v < 2e6 else "milhões")):
        if v >= lim:
            return f"R$ {num(v / lim, 1 if v / lim < 100 else 0)} {nome}"
    return f"R$ {num(v)}"


def ld(obj):
    return json.dumps(obj, ensure_ascii=False, separators=(",", ":")).replace("</", "<\\/")


def resumo(m, D):
    """Os fatos do resumo estático, todos do mesmo JSON que o painel lê."""
    mun = (D or {}).get("municipio") or {}
    sec = (D or {}).get("secoes") or {}
    f = {"nome": m["nome"], "uf": m["uf"], "nome_uf": mun.get("nome_uf") or UFS[m["uf"]],
         "regiao": mun.get("regiao"), "meso": mun.get("mesorregiao"), "capital": mun.get("capital_uf"),
         "area": mun.get("area_km2"), "ddd": mun.get("ddd")}
    serie = [s for s in ((sec.get("demografia") or {}).get("populacao_serie") or []) if s.get("populacao")]
    if serie:
        f["pop"], f["pop_ano"] = serie[-1]["populacao"], serie[-1]["ano"]
    pib = [s for s in (((sec.get("economia") or {}).get("pib") or {}).get("serie") or []) if s.get("pib")]
    if pib:
        f["pib"], f["pib_ano"] = pib[-1]["pib"], pib[-1]["ano"]
    pol = sec.get("politica") or {}
    el = (pol.get("prefeito") or {}).get("eleito") or {}
    if el.get("nome_urna"):
        f["prefeito"] = f'{el["nome_urna"]} ({el["partido"]})' if el.get("partido") else el["nome_urna"]
        f["prefeito_ano"] = (pol.get("prefeito") or {}).get("ano") or pol.get("ano_prefeito")
    f["eleitores"] = ((pol.get("eleitorado") or {}).get("aptos"))
    f["vizinhos"] = [v for v in ((sec.get("vizinhanca") or {}).get("municipios") or [])
                     if re.fullmatch(r"\d{7}", str(v.get("id_municipio", "")))]
    sede = (sec.get("geografia") or {}).get("sede_municipal") or {}
    f["geo"] = (sede.get("lat"), sede.get("lon")) if sede.get("lat") is not None else None
    return f


def pagina(m, D):
    f = resumo(m, D)
    nome, uf, id_ = f["nome"], f["uf"], m["id"]
    url = f"{BASE}/dataviz/municipios/{id_}/"
    titulo = f"{nome}, {uf} — Painel municipal — Rodado"
    partes = []
    if f.get("pop"):
        partes.append(f"{num(f['pop'])} habitantes ({f['pop_ano']})")
    if f.get("pib"):
        partes.append(f"PIB de {reais(f['pib'])} ({f['pib_ano']})")
    if f.get("area"):
        partes.append(f"{num(f['area'])} km²")
    onde = f"{'capital de ' if f['capital'] else ''}{f['nome_uf']}"
    desc = (f"{nome} ({onde})" + (": " + ", ".join(partes) if partes else "") +
            ". Painel com centenas de indicadores de dados públicos oficiais: saúde, educação, economia, segurança, meio ambiente, política e contas públicas.")
    og_desc = f"{nome}, {uf}" + (": " + ", ".join(partes) if partes else "") + ". Centenas de indicadores de dados públicos oficiais num só painel."
    lugar = {"@type": "City", "name": nome, "identifier": id_,
             "containedInPlace": {"@type": "State", "name": f["nome_uf"]}}
    if f["geo"]:
        lugar["geo"] = {"@type": "GeoCoordinates", "latitude": round(f["geo"][0], 5), "longitude": round(f["geo"][1], 5)}
    if f.get("pop"):
        lugar["additionalProperty"] = {"@type": "PropertyValue", "name": f"População estimada ({f['pop_ano']})", "value": f["pop"]}
    jsonld = {"@context": "https://schema.org", "@type": "WebPage", "@id": url, "url": url,
              "name": f"{nome}, {uf} — Painel municipal", "description": desc, "inLanguage": "pt-BR",
              "about": lugar,
              "isPartOf": {"@type": "WebSite", "name": "ミ.xyz", "url": BASE + "/"},
              "breadcrumb": {"@type": "BreadcrumbList", "itemListElement": [
                  {"@type": "ListItem", "position": 1, "name": "ミ.xyz", "item": BASE + "/"},
                  {"@type": "ListItem", "position": 2, "name": "Municípios", "item": BASE + "/dataviz/municipios/"},
                  {"@type": "ListItem", "position": 3, "name": f["nome_uf"], "item": f"{BASE}/dataviz/municipios/#{uf.lower()}"},
                  {"@type": "ListItem", "position": 4, "name": nome, "item": url}]}}
    e = escape
    fatos = [("Estado", f"{f['nome_uf']} ({uf})" + (" — capital" if f["capital"] else ""))]
    if f.get("regiao"):
        fatos.append(("Região", f["regiao"] + (f" · mesorregião {f['meso']}" if f.get("meso") else "")))
    if f.get("pop"):
        fatos.append((f"População ({f['pop_ano']})", num(f["pop"])))
    if f.get("area"):
        fatos.append(("Área", f"{num(f['area'])} km²"))
    if f.get("pib"):
        fatos.append((f"PIB ({f['pib_ano']})", reais(f["pib"])))
    if f.get("prefeito"):
        fatos.append((f"Prefeitura (eleição de {f['prefeito_ano']})" if f.get("prefeito_ano") else "Prefeitura", f["prefeito"]))
    if f.get("eleitores"):
        fatos.append(("Eleitorado", num(f["eleitores"])))
    if f.get("ddd"):
        fatos.append(("DDD", f["ddd"]))
    fatos.append(("Código IBGE", id_))
    dl = "\n".join(f"<dt>{e(k)}</dt><dd>{e(str(v))}</dd>" for k, v in fatos)
    viz = ""
    if f["vizinhos"]:
        viz = ("<h2>Municípios vizinhos</h2>\n<ul class=\"viz\">\n" +
               "\n".join(f'<li><a href="../{v["id_municipio"]}/">{e(v["nome"])}, {e(v.get("sigla_uf") or "")}</a></li>'
                         for v in f["vizinhos"]) + "\n</ul>")
    return f"""<!doctype html>
<html lang="pt-BR">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<!-- painel:seo (gerado por gera_indice.py; o painel.html entra com este bloco no lugar do seu) -->
<title id="pageTitle">{e(titulo)}</title>
<meta name="description" content="{e(desc)}">
<link rel="canonical" href="{url}">
<meta property="og:type" content="website">
<meta property="og:site_name" content="Rodado">
<meta property="og:locale" content="pt_BR">
<meta property="og:title" content="{e(nome)}, {uf}: o município inteiro em um painel">
<meta property="og:description" content="{e(og_desc)}">
<meta property="og:url" content="{url}">
<meta property="og:image" content="{BASE}/dataviz/municipios/og.png">
<meta property="og:image:width" content="1200">
<meta property="og:image:height" content="630">
<meta name="twitter:card" content="summary_large_image">
<meta name="twitter:title" content="{e(nome)}, {uf}: o município inteiro em um painel">
<meta name="twitter:description" content="{e(og_desc)}">
<meta name="twitter:image" content="{BASE}/dataviz/municipios/og.png">
<script type="application/ld+json">{ld(jsonld)}</script>
<!-- /painel:seo -->
<script>window.ID_MUN_FIXO = '{id_}';</script>
<script src="/dataviz/municipios/pagina.js?v=1"></script>
<style>body{{margin:0 auto;max-width:48rem;padding:1.5rem 16px;font:16px/1.5 system-ui,sans-serif}}dt{{font-weight:600}}</style>
</head>
<body>
<main>
<nav><a href="../">Municípios</a> › <a href="../#{uf.lower()}">{e(f['nome_uf'])}</a></nav>
<h1>{e(nome)}, {uf}</h1>
<p>{e(desc)}</p>
<dl>
{dl}
</dl>
{viz}
<p><a href="../">Todos os municípios do Brasil</a></p>
</main>
</body>
</html>
"""


def gera_paginas(muns):
    sem = []
    for m in muns:
        arq = AQUI / "data" / f"{m['id']}.json"
        D = json.loads(arq.read_text(encoding="utf-8")) if arq.exists() else None
        if D is None:
            sem.append(m["id"])
        d = AQUI / m["id"]
        d.mkdir(exist_ok=True)
        (d / "index.html").write_text(pagina(m, D), encoding="utf-8")
    return sem


def main():
    origem = Path(sys.argv[1]) if len(sys.argv) > 1 else AQUI / "data" / "municipios.json"
    muns = json.loads(origem.read_text(encoding="utf-8"))
    por_uf = {}
    for m in muns:
        por_uf.setdefault(m["uf"], []).append(m)
    ufs = sorted(por_uf, key=lambda u: chave(UFS[u]))
    n = len(muns)
    nav = " · ".join(f'<a href="#{u.lower()}">{u}</a>' for u in ufs)
    secoes = []
    for u in ufs:
        lis = "\n".join(f'<li><a href="{m["id"]}/">{escape(m["nome"])}</a></li>'
                        for m in sorted(por_uf[u], key=lambda m: (chave(m["nome"]), m["id"])))
        secoes.append(f'<section id="{u.lower()}"><h2>{UFS[u]} <small>({len(por_uf[u])})</small></h2>\n<ul>\n{lis}\n</ul></section>')
    desc = f"Os {n:,} municípios do Brasil, por estado, cada um com o seu painel de indicadores de dados públicos oficiais.".replace(",", ".")
    html = f'''<!doctype html>
<html lang="pt-BR">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Todos os municípios do Brasil — Painel municipal — Rodado</title>
<script>
// cada município tem o seu endereço, /dataviz/municipios/<id>/; o ?id=<código IBGE> antigo vai para lá.
// Um id que não é código IBGE (?id=_teste_vazio&dados=local, desenvolvimento) troca este documento pelo painel.
(function () {{
  if (!new URLSearchParams(location.search).get('id')) return;
  var q = new URLSearchParams(location.search), id = q.get('id').trim();
  if (/^\d{{7}}$/.test(id)) {{
    q.delete('id');
    location.replace('/dataviz/municipios/' + id + '/' + (q.toString() ? '?' + q : '') + location.hash);
    return;
  }}
  // o JSON do município sai já agora, junto com o painel, em vez de esperar o painel.html chegar
  if (/^\\d{{7}}$/.test(id) && q.get('dados') !== 'local') window.DADOS_PREFETCH = fetch('https://xyz-municipio.hel1.your-objectstorage.com/' + id + '.json');
  ['vendor/chart-4.4.7.umd.min.js', 'app.js?v=4'].forEach(function (u) {{
    var l = document.createElement('link'); l.rel = 'preload'; l.as = 'script'; l.href = u; document.head.appendChild(l);
  }});
  document.documentElement.style.visibility = 'hidden';
  fetch('painel.html', {{ cache: 'no-cache' }}).then(function (r) {{ return r.text(); }}).then(function (t) {{
    document.open(); document.write(t); document.close();
  }});
  window.PAINEL_TROCA = true;
}})();
</script>
<meta name="description" content="{desc}">
<link rel="canonical" href="{BASE}/dataviz/municipios/">
<meta property="og:type" content="website">
<meta property="og:site_name" content="Rodado">
<meta property="og:locale" content="pt_BR">
<meta property="og:title" content="Todos os municípios do Brasil">
<meta property="og:description" content="{desc}">
<meta property="og:url" content="{BASE}/dataviz/municipios/">
<meta property="og:image" content="{BASE}/dataviz/municipios/og.png">
<meta property="og:image:width" content="1200">
<meta property="og:image:height" content="630">
<meta name="twitter:card" content="summary_large_image">
<meta name="twitter:title" content="Todos os municípios do Brasil">
<meta name="twitter:description" content="{desc}">
<meta name="twitter:image" content="{BASE}/dataviz/municipios/og.png">
<script type="application/ld+json">
{json.dumps({
  "@context": "https://schema.org",
  "@graph": [
    {"@type": "CollectionPage", "@id": BASE + "/dataviz/municipios/", "url": BASE + "/dataviz/municipios/",
     "name": "Todos os municípios do Brasil", "description": desc, "inLanguage": "pt-BR",
     "isPartOf": {"@type": "WebSite", "name": "ミ.xyz", "url": BASE + "/"},
     "breadcrumb": {"@type": "BreadcrumbList", "itemListElement": [
       {"@type": "ListItem", "position": 1, "name": "ミ.xyz", "item": BASE + "/"},
       {"@type": "ListItem", "position": 2, "name": "DataViz", "item": BASE + "/dataviz/"},
       {"@type": "ListItem", "position": 3, "name": "Municípios", "item": BASE + "/dataviz/municipios/"}]}},
    {"@type": "Dataset", "name": "Painel municipal: indicadores dos 5.571 municípios do Brasil",
     "description": "Centenas de indicadores por município (demografia, economia, saúde, educação, segurança, meio ambiente, política e contas públicas) de mais de 80 fontes públicas oficiais, como IBGE, DATASUS, INEP, TSE, CGU e Receita Federal.",
     "url": BASE + "/dataviz/municipios/", "inLanguage": "pt-BR", "isAccessibleForFree": True,
     "spatialCoverage": {"@type": "Place", "name": "Brasil"},
     "keywords": ["municípios", "IBGE", "indicadores municipais", "dados públicos", "Brasil"],
     "creator": {"@type": "Organization", "name": "Rodado", "url": "https://rodado.xyz"},
     "distribution": {"@type": "DataDownload", "encodingFormat": "application/json",
                      "contentUrl": "https://xyz-municipio.hel1.your-objectstorage.com/municipios.json"}}]
}, ensure_ascii=False, indent=1)}
</script>
<style>
:root{{--bg:#0b0d14;--surface:#151821;--border:#282d3f;--text:#e2e5f0;--text2:#7a8099;--accent:#7b9bff;--accent-rgb:123,155,255;--shadow:0 6px 24px rgba(0,0,0,.4);--radius-sm:6px}}
@media (prefers-color-scheme:light){{:root{{--bg:#f9f9f7;--surface:#fcfcfb;--border:#e1e0d9;--text:#0b0b0b;--text2:#52514e;--accent:#2a78d6;--accent-rgb:42,120,214;--shadow:0 6px 24px rgba(0,0,0,.12)}}}}
body{{margin:0;background:var(--bg);color:var(--text);font:16px/1.5 system-ui,sans-serif}}
main{{max-width:70rem;margin:0 auto;padding:1.5rem 16px 4rem}}
a{{color:var(--accent);text-decoration:none}}a:hover{{text-decoration:underline}}
h1{{margin:.2rem 0 .4rem;font-size:1.8rem}}p.lede{{color:var(--text2);margin:0 0 1rem}}
nav.ufs{{margin:1rem 0 1.5rem;line-height:2;color:var(--text2)}}
.busca{{position:relative;max-width:26rem;margin:1rem 0}}
.busca input{{width:100%;box-sizing:border-box;padding:.6rem .8rem;font:inherit;color:var(--text);background:var(--surface);border:1px solid var(--border);border-radius:var(--radius-sm)}}
.busca input:focus{{outline:none;border-color:var(--accent)}}
.busca ul{{position:absolute;left:0;right:0;top:calc(100% + 4px);z-index:5;max-height:18rem;overflow-y:auto;margin:0;padding:.25rem;list-style:none;background:var(--surface);border:1px solid var(--border);border-radius:var(--radius-sm);box-shadow:var(--shadow)}}
.busca li{{display:flex;justify-content:space-between;padding:.45rem .6rem;cursor:pointer;border-radius:4px}}
.busca li small{{color:var(--text2)}}.busca li[aria-selected="true"],.busca li:hover{{background:rgba(var(--accent-rgb),.14)}}
section{{margin-top:2rem}}h2{{font-size:1.15rem;border-bottom:1px solid var(--border);padding-bottom:.3rem}}h2 small{{color:var(--text2);font-weight:400}}
section ul{{columns:15rem;column-gap:1.5rem;list-style:none;margin:0;padding:0}}section li{{break-inside:avoid;padding:.1rem 0}}
</style>
<script>if (!window.PAINEL_TROCA) {{ var s = document.createElement('script'); s.src = 'busca.js'; s.defer = true; document.head.appendChild(s); }}</script>
<script>window.BUSCA_INDICE = 'https://xyz-municipio.hel1.your-objectstorage.com/municipios.json'; window.BUSCA_PAINEL = '';</script>
</head>
<body>
<main>
<h1>Todos os municípios do Brasil</h1>
<p class="lede">{n:,} municípios, por estado. Cada um abre o seu painel: demografia, economia, saúde, educação, segurança, meio ambiente, política e contas públicas, de dados públicos oficiais.</p>
<div class="busca" role="search">
<input id="buscaMun" type="search" placeholder="Buscar município…" aria-label="Buscar município" autocomplete="off" spellcheck="false" role="combobox" aria-expanded="false" aria-controls="buscaLista" aria-autocomplete="list">
<ul id="buscaLista" role="listbox" aria-label="Municípios encontrados" hidden></ul>
</div>
<nav class="ufs" aria-label="Estados">{nav}</nav>
{chr(10).join(secoes)}
</main>
</body>
</html>
'''.replace(f"{n:,} municípios", f"{n:,} municípios".replace(",", "."))
    (AQUI / "index.html").write_text(html, encoding="utf-8")
    hoje = date.today().isoformat()
    urls = "\n".join(f"  <url><loc>{BASE}/dataviz/municipios/{m['id']}/</loc><lastmod>{hoje}</lastmod><priority>0.4</priority></url>"
                     for m in sorted(muns, key=lambda m: m["id"]))
    (RAIZ / "sitemap-municipios.xml").write_text(
        f'<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n{urls}\n</urlset>\n', encoding="utf-8")
    sem = gera_paginas(muns)
    print(f"{n} municípios em {len(ufs)} UFs: index.html, <id>/index.html e sitemap-municipios.xml"
          + (f" ({len(sem)} sem data/<id>.json, com página só de nome: {', '.join(sem[:5])})" if sem else ""))


if __name__ == "__main__":
    main()
