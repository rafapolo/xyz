#!/usr/bin/env bun
/**
 * SEO de ミ.xyz: cartão de compartilhamento nas páginas que vêm sem ele,
 * sitemap.xml e robots.txt.
 *
 * - Cartão (Open Graph + Twitter): só nas páginas listadas em CARTOES e só se
 *   a página não tiver og:title escrito à mão (religioes/, eleicoes/,
 *   municipio/ e os índices já têm o seu, que fica como está). O bloco vai
 *   entre sentinelas, então rodar de novo reescreve em vez de duplicar.
 * - sitemap.xml: todo HTML versionado, menos o que está em FORA (fonte de
 *   build, redirecionamento, layout).
 *
 * Página nova: acrescente uma linha em CARTOES (ou dê a ela og:title próprio)
 * e rode `bun scripts/gera_seo.ts`. `--checa` só confere: sai 1 se houver
 * página sem cartão ou fora do sitemap.
 */
import { existsSync, readFileSync, writeFileSync } from "node:fs";
import { join } from "node:path";

const RAIZ = join(import.meta.dir, "..");
const BASE = "https://xn--2dk.xyz";
const SITE = "ミ.xyz";
const IMG_PADRAO = `${BASE}/images/image1.png`;
const checa = process.argv.includes("--checa");

const OPEN = "<!-- seo:start (gerado por scripts/gera_seo.ts — não editar à mão) -->";
const CLOSE = "<!-- seo:end -->";

// fora do sitemap: não são páginas para o leitor chegar por busca
const FORA = new Set([
  "_layouts/default.html",
  "dataviz/eleicoes/src/index.html", // fonte do build; o publicado é dataviz/eleicoes/
  "municipio.html", // redireciona para dataviz/municipio/
]);
const FORA_PREFIXO = ["tasks/", ".claude/", "docs/"];

type Cartao = { titulo?: string; desc: string; img?: string };

const UFS: Record<string, string> = {
  ac: "Acre", al: "Alagoas", am: "Amazonas", ap: "Amapá", ba: "Bahia",
  ce: "Ceará", es: "Espírito Santo", go: "Goiás", ma: "Maranhão",
  mg: "Minas Gerais", ms: "Mato Grosso do Sul", mt: "Mato Grosso", pa: "Pará",
  pb: "Paraíba", pe: "Pernambuco", pi: "Piauí", pr: "Paraná",
  rj: "Rio de Janeiro", rn: "Rio Grande do Norte", ro: "Rondônia",
  rr: "Roraima", rs: "Rio Grande do Sul", sc: "Santa Catarina", se: "Sergipe",
  sp: "São Paulo", to: "Tocantins",
};

const CARTOES: Record<string, Cartao> = {
  "brasiliana/index.html": {
    desc: "Um mural navegável do acervo da Brasiliana Fotográfica (Biblioteca Nacional): milhares de fotografias históricas do Brasil, com filtro por período, instituição e busca livre.",
  },
  "data/relatorios/parlamentares_empresas_licitacoes.html": {
    desc: "Parlamentares eleitos que são sócios de empresas vencedoras de licitações federais: candidatos do TSE cruzados com o quadro societário da Receita e as compras da CGU.",
  },
  "dataviz/encarceramento_homicidio.html": {
    desc: "Entre 2016 e 2022 o Brasil prendeu 18% mais e viu o homicídio cair 26%. Estado por estado, as duas curvas contam outra história.",
    img: `${BASE}/dataviz/og-encarceramento.png`,
  },
  "dataviz/polis/index.html": {
    titulo: "polis",
    desc: "Caderno interativo (marimo) de exploração de dados políticos brasileiros, rodando no navegador.",
  },
  "dataviz/pt-2026/index.html": {
    desc: "Mapa das eleições de 2026 em Portugal, cada localidade colorida pela distribuição dos votos. Clique numa freguesia para ver o resultado.",
  },
  "dataviz/racas/index.html": {
    desc: "Os 5.570 municípios brasileiros coloridos pela cor ou raça autodeclarada que predomina na população, segundo o Censo do IBGE de 2010 e 2022.",
  },
  "dataviz/rais/index.html": {
    titulo: "As 500 empresas com mais vínculos de emprego no Brasil",
    desc: "Os 500 maiores empregadores formais do país pela RAIS, separados entre órgãos públicos, autarquias, Judiciário e empresas privadas.",
  },
  "dataviz/rais/por_uf.html": {
    titulo: "Empresas com mais de 1.000 vínculos, por UF",
    desc: "Os grandes empregadores formais de cada estado, pela RAIS: quem tem mais de mil vínculos de emprego em cada UF.",
  },
  "dataviz/rais/mapa/index.html": {
    titulo: "Atlas Salarial do Brasil",
    desc: "Quanto paga o emprego formal em cada um dos 5.570 municípios, pela RAIS de 2020 a 2024, no setor privado, no público e no total.",
  },
  "dataviz/rais/mapa/salarios.html": {
    titulo: "Salário médio da RAIS por município: análise dos dados",
    desc: "Médias, medianas e quartis do salário formal nos 5.570 municípios, por ano e setor, com os extremos e os vínculos por trás de cada número.",
  },
  "dataviz/religioes/igrejas/index.html": {
    desc: "Os 765 mil pontos religiosos do Cadastro Nacional de Endereços (CNEFE, Censo 2022) no mapa, coloridos por vertente: evangélicos, católicos, espíritas, umbanda e candomblé e mais.",
  },
  "dataviz/religioes/notes/relatorio.html": {
    titulo: "Templos religiosos do Brasil por vertente: relatório",
    desc: "765 mil templos geolocalizados: distribuição por UF, série de fundação, formalização por vertente e dez perguntas em aberto.",
    img: "https://xn--2dk.xyz/dataviz/religioes/igrejas/og.png",
  },
  "dataviz/rio/confeccoes.html": {
    titulo: "Confecções no estado do Rio de Janeiro",
    desc: "Onde estão as confecções do estado do Rio de Janeiro: cada empresa ativa do setor com CNPJ, um ponto no mapa.",
  },
  "dataviz/rio/ibge.html": {
    titulo: "O estado do Rio de Janeiro nos dados do IBGE",
    desc: "Mapa do estado do Rio de Janeiro com os indicadores do IBGE por município e setor censitário.",
  },
  "dataviz/swiss/index.html": {
    titulo: "helvetiscan: os domínios .ch e seus servidores de nome",
    desc: "Análise de todos os domínios suíços e dos servidores de nome que os atendem, em rede navegável.",
  },
  "dataviz/uf/index.html": {
    titulo: "Brasil: cada ponto é um CNPJ",
    desc: "18 milhões de estabelecimentos ativos com CNPJ no mapa, um ponto por endereço geolocalizado, pelo cadastro da Receita Federal. Escolha um estado.",
  },
  "dataviz/uf/br/index.html": {
    titulo: "Brasil: cada ponto é um CNPJ",
    desc: "18 milhões de estabelecimentos ativos com CNPJ no mapa, um ponto por endereço geolocalizado, pelo cadastro da Receita Federal.",
  },
  "malafaia/index.html": {
    titulo: "O império de Silas Malafaia (1971–2025)",
    desc: "As empresas, igrejas e entidades ligadas a Silas Malafaia ano a ano, de 1971 a 2025, pelo quadro societário da Receita Federal.",
    img: "https://rodado.xyz/plataformas/img/og-malafaia.png",
  },
};
for (const [uf, nome] of Object.entries(UFS)) {
  CARTOES[`dataviz/uf/${uf}/index.html`] = {
    titulo: `${nome}: cada ponto é um CNPJ`,
    desc: `Os estabelecimentos ativos com CNPJ de ${nome} no mapa, um ponto por endereço geolocalizado, pelo cadastro da Receita Federal.`,
  };
}

const esc = (s: string) =>
  s.replace(/&/g, "&amp;").replace(/"/g, "&quot;").replace(/</g, "&lt;").replace(/>/g, "&gt;");

const url = (rel: string) => `${BASE}/${rel.replace(/(^|\/)index\.html$/, "$1")}`;

function bloco(rel: string, html: string, c: Cartao): string {
  const titulo = c.titulo ?? (html.match(/<title>([^<]*)<\/title>/i)?.[1] ?? "").trim();
  const img = c.img ?? (existsSync(join(RAIZ, rel, "..", "og.png")) ? url(rel.replace(/[^/]+$/, "og.png")) : IMG_PADRAO);
  const u = url(rel);
  return [
    OPEN,
    /rel=["']canonical["']/i.test(html) ? "" : `<link rel="canonical" href="${esc(u)}">`,
    /name=["']description["']/i.test(html) ? "" : `<meta name="description" content="${esc(c.desc)}">`,
    '<meta property="og:type" content="website">',
    `<meta property="og:site_name" content="${SITE}">`,
    '<meta property="og:locale" content="pt_BR">',
    `<meta property="og:url" content="${esc(u)}">`,
    `<meta property="og:title" content="${esc(titulo)}">`,
    `<meta property="og:description" content="${esc(c.desc)}">`,
    `<meta property="og:image" content="${esc(img)}">`,
    `<meta property="og:image:alt" content="${esc(titulo)}">`,
    '<meta name="twitter:card" content="summary_large_image">',
    `<meta name="twitter:title" content="${esc(titulo)}">`,
    `<meta name="twitter:description" content="${esc(c.desc)}">`,
    `<meta name="twitter:image" content="${esc(img)}">`,
    CLOSE,
  ].filter(Boolean).join("\n");
}

function injeta(html: string, b: string): string | null {
  // o bloco entra sempre seguido de "\n", e é isso que a limpeza tira junto:
  // assim rodar de novo devolve o mesmo arquivo, byte a byte
  if (/<\/head>/i.test(html)) return html.replace(/<\/head>/i, `${b}\n</head>`);
  if (/<\/title>/i.test(html)) return html.replace(/<\/title>/i, (t) => `${t}${b}\n`);
  return null;
}

const versionados = (await Bun.$`git -C ${RAIZ} ls-files '*.html'`.text())
  .split("\n").filter(Boolean);
const publicas = versionados.filter(
  (r) => !FORA.has(r) && !FORA_PREFIXO.some((p) => r.startsWith(p)),
);

let problemas = 0;
let escritas = 0;
for (const rel of publicas) {
  const arq = join(RAIZ, rel);
  let html = readFileSync(arq, "utf8");
  const sentinela = new RegExp(`${OPEN.replace(/[.*+?^${}()|[\]\\]/g, "\\$&")}[\\s\\S]*?${CLOSE}\\n`);
  const limpo = html.replace(sentinela, "");
  const temProprio = /property=["']og:title["']/i.test(limpo);
  const c = CARTOES[rel];
  if (temProprio) {
    // cartão à mão: só confere que tem os três campos que o checa_seo.ts
    // do rodado exige no ar
    const faltam = ["og:image", "twitter:card"].filter((p) => !limpo.includes(p));
    if (faltam.length) {
      problemas++;
      console.log(`  ! ${rel}: og:title à mão, mas sem ${faltam.join(", ")}`);
    }
    continue;
  }
  if (!c) {
    problemas++;
    console.log(`  ! ${rel}: sem og:title e sem linha em CARTOES`);
    continue;
  }
  const novo = injeta(limpo, bloco(rel, limpo, c));
  if (novo === null) {
    problemas++;
    console.log(`  ! ${rel}: sem </head> nem </title>, não deu para injetar`);
    continue;
  }
  if (novo !== html) {
    if (checa) {
      problemas++;
      console.log(`  ! ${rel}: cartão desatualizado`);
    } else {
      writeFileSync(arq, novo);
      escritas++;
    }
  }
}

const hoje = new Date().toISOString().slice(0, 10);
const sitemap = [
  '<?xml version="1.0" encoding="UTF-8"?>',
  '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">',
  ...publicas.map((rel) =>
    `  <url><loc>${esc(url(rel))}</loc><lastmod>${hoje}</lastmod>` +
    `<priority>${rel === "index.html" ? "1.0" : rel.split("/").length <= 2 ? "0.8" : "0.6"}</priority></url>`),
  "</urlset>",
  "",
].join("\n");
const robots = `User-agent: *\nAllow: /\n\nSitemap: ${BASE}/sitemap.xml\n`;

if (checa) {
  const atual = existsSync(join(RAIZ, "sitemap.xml")) ? readFileSync(join(RAIZ, "sitemap.xml"), "utf8") : "";
  const locs = (s: string) => [...s.matchAll(/<loc>([^<]*)<\/loc>/g)].map((m) => m[1]).sort().join("\n");
  if (locs(atual) !== locs(sitemap)) {
    problemas++;
    console.log("  ! sitemap.xml não bate com as páginas versionadas");
  }
  console.log(problemas ? `${problemas} problemas` : "ok: todas as páginas com cartão e no sitemap");
  process.exit(problemas ? 1 : 0);
}

writeFileSync(join(RAIZ, "sitemap.xml"), sitemap);
writeFileSync(join(RAIZ, "robots.txt"), robots);
console.log(`${escritas} páginas com cartão novo · sitemap.xml com ${publicas.length} URLs · robots.txt`);
if (problemas) process.exit(1);
