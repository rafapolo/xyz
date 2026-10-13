let THEME = document.documentElement.getAttribute('data-theme') === 'light' ? 'light' : 'dark';
const PALETTES = {
  dark: {
    s1: '#3987e5', s2: '#008300', s3: '#d55181', s4: '#c98500',
    s5: '#199e70', s6: '#d95926', s7: '#9085e9', s8: '#e66767',
    s1fill: 'rgba(57,135,229,.10)', s2fill: 'rgba(0,131,0,.10)',
    s3fill: 'rgba(213,81,129,.10)', s4fill: 'rgba(201,133,0,.10)',
    surface: '#151821', surface2: '#1e2230', grid: 'rgba(40,45,63,.5)', tick: '#7a8099', muted: '#545a75',
    ordinal4: ['#b7d3f6', '#6da7ec', '#2a78d6', '#184f95'],
    tooltipBg: '#1e2230', tooltipTitle: '#e2e5f0', tooltipBody: '#7a8099', tooltipBorder: '#282d3f',
  },
  light: {
    s1: '#2a78d6', s2: '#008300', s3: '#e87ba4', s4: '#eda100',
    s5: '#1baf7a', s6: '#eb6834', s7: '#4a3aa7', s8: '#e34948',
    s1fill: 'rgba(42,120,214,.10)', s2fill: 'rgba(0,131,0,.10)',
    s3fill: 'rgba(232,123,164,.10)', s4fill: 'rgba(237,161,0,.10)',
    surface: '#fcfcfb', surface2: '#f2f1ed', grid: 'rgba(225,224,217,.7)', tick: '#52514e', muted: '#898781',
    ordinal4: ['#86b6ef', '#5598e7', '#2a78d7', '#184f95'],
    tooltipBg: '#f2f1ed', tooltipTitle: '#0b0b0b', tooltipBody: '#52514e', tooltipBorder: '#e1e0d9',
  },
};
const PALETAS_ORIG = JSON.parse(JSON.stringify(PALETTES));
const C = PALETTES[THEME];
const ordinal4 = C.ordinal4;
const chartOpts = {
  responsive: true, maintainAspectRatio: false,
  plugins: {
    legend: { position: 'top', labels: { color: C.tick, usePointStyle: true, pointStyle: 'circle', padding: 12 } },
    tooltip: {
      backgroundColor: C.tooltipBg, titleColor: C.tooltipTitle, bodyColor: C.tooltipBody,
      borderColor: C.tooltipBorder, borderWidth: 1, padding: 10, cornerRadius: 8, boxPadding: 6, usePointStyle: true,
    }
  },
  scales: {
    x: { ticks: { color: C.muted }, grid: { color: C.grid } },
    y: { ticks: { color: C.muted }, grid: { color: C.grid } },
  }
};
const noLegend = { ...chartOpts.plugins, legend: { display: false } };
const lineStyle = { borderWidth: 2, tension: .3, pointRadius: 4, pointBorderColor: C.surface, pointBorderWidth: 2 };

// Todo gráfico nasce aqui. O registro guarda a configuração de cada um: é o que
// permite trocar de tema sem recarregar, descrever o gráfico para leitor de tela e
// marcar o ano em curso.
const GRAFICOS = [];
let ANO_EM_CURSO = null, MES_EXTRACAO = '';
function criaGrafico(cv, cfg) {
  if (!cv) return null;
  marcaAnoEmCurso(cv, cfg);
  descreveGrafico(cv, cfg);
  const chart = new Chart(cv, cfg);
  GRAFICOS.push({ cv, cfg, chart });
  return chart;
}

// Série anual que termina no ano da extração: o último ponto ainda está em aberto.
// Ele ganha um asterisco, fica esmaecido (barra) ou tracejado (linha) e uma nota no cartão.
function marcaAnoEmCurso(cv, cfg) {
  const labels = cfg.data && cfg.data.labels;
  if (!ANO_EM_CURSO || !Array.isArray(labels) || labels.length < 2) return;
  if (!labels.every(l => /^\d{4}$/.test(String(l)))) return;
  const ult = labels.length - 1;
  if (Number(labels[ult]) !== ANO_EM_CURSO) return;
  labels[ult] = ANO_EM_CURSO + '*';
  (cfg.data.datasets || []).forEach(ds => {
    const tipo = ds.type || cfg.type;
    if (tipo === 'bar' && typeof ds.backgroundColor === 'string' && /^#[0-9a-f]{6}$/i.test(ds.backgroundColor)) {
      ds.backgroundColor = labels.map((_, i) => ds.backgroundColor + (i === ult ? '66' : ''));
    } else if (tipo === 'line') {
      ds.segment = { ...(ds.segment || {}), borderDash: ctx => ctx.p1DataIndex === ult ? [4, 4] : undefined };
    }
  });
  const card = cv.closest('.card');
  if (card && !card.querySelector('.chart-note')) {
    card.insertAdjacentHTML('beforeend', '<div class="chart-note">* ' + ANO_EM_CURSO +
      ' é o ano em curso: dado até a extração' + (MES_EXTRACAO ? ' (' + MES_EXTRACAO + ')' : '') + '</div>');
  }
}

// <canvas> é opaco para leitor de tela: o título do cartão e um resumo dos dados
// viram o texto alternativo.
function descreveGrafico(cv, cfg) {
  const card = cv.closest('.card'), h3 = card && card.querySelector('h3');
  const txt = l => [].concat(l).join(' ');
  const labels = ((cfg.data && cfg.data.labels) || []).map(txt);
  const sets = ((cfg.data && cfg.data.datasets) || []).filter(d => Array.isArray(d.data));
  const partes = ['Gráfico' + (h3 ? ': ' + h3.textContent.replace(/\s+/g, ' ').trim() : '')];
  const num = v => typeof v === 'number' ? fNum(Math.round(v * 10) / 10) : null;
  if (sets.length === 1 && labels.length && labels.length <= 8) {
    partes.push(labels.map((l, i) => num(sets[0].data[i]) != null ? l + ': ' + num(sets[0].data[i]) : null).filter(Boolean).join('; '));
  } else if (labels.length) {
    partes.push(labels.length + ' pontos, de ' + labels[0] + ' a ' + labels[labels.length - 1]);
    sets.slice(0, 4).forEach(d => {
      const vs = d.data.filter(v => typeof v === 'number');
      if (!vs.length) return;
      partes.push((d.label ? d.label + ': ' : '') + 'de ' + num(vs[0]) + ' a ' + num(vs[vs.length - 1]) +
        ' (mín. ' + num(Math.min(...vs)) + ', máx. ' + num(Math.max(...vs)) + ')');
    });
  }
  cv.setAttribute('role', 'img');
  cv.setAttribute('aria-label', partes.filter(Boolean).join('. '));
}

// Alternância de tema sem recarregar: cada cor da paleta atual é trocada pela
// correspondente da outra — na paleta viva (C), nas configurações dos gráficos e
// nas cores escritas direto no HTML (barras, sparklines, mapa).
function trocaTema() {
  const novo = THEME === 'light' ? 'dark' : 'light';
  const de = PALETAS_ORIG[THEME], para = PALETAS_ORIG[novo], mapa = {};
  Object.keys(de).forEach(k => [].concat(de[k]).forEach((cor, i) => { mapa[cor.toLowerCase()] = [].concat(para[k])[i]; }));
  const re = new RegExp(Object.keys(mapa).map(c => c.replace(/[.*+?^${}()|[\]\\]/g, '\\$&')).join('|'), 'gi');
  const troca = t => t.replace(re, m => mapa[m.toLowerCase()]);
  const vistos = new WeakSet();
  const percorre = o => {
    if (!o || typeof o !== 'object' || vistos.has(o)) return;
    const proto = Object.getPrototypeOf(o);
    if (!Array.isArray(o) && proto !== Object.prototype && proto !== null) return;
    vistos.add(o);
    Object.keys(o).forEach(k => {
      if (typeof o[k] === 'string') o[k] = troca(o[k]);
      else percorre(o[k]);
    });
  };
  [C, chartOpts, noLegend, lineStyle].forEach(percorre);
  GRAFICOS.forEach(g => percorre(g.cfg));
  document.querySelectorAll('.main [style], .main svg [fill], .main svg [stroke]').forEach(e => {
    ['style', 'fill', 'stroke'].forEach(a => { const v = e.getAttribute(a); if (v) { const n = troca(v); if (n !== v) e.setAttribute(a, n); } });
  });
  THEME = novo;
  if (novo === 'light') document.documentElement.setAttribute('data-theme', 'light');
  else document.documentElement.removeAttribute('data-theme');
  localStorage.setItem('rodado-theme', novo);
  document.querySelectorAll('.theme-toggle').forEach(b => { b.textContent = novo === 'light' ? '☀️' : '🌙'; });
  GRAFICOS.forEach(g => g.chart.update('none'));
}
document.querySelectorAll('.theme-toggle').forEach(b => {
  b.textContent = THEME === 'light' ? '☀️' : '🌙';
  b.addEventListener('click', trocaTema);
});
const fNum = n => n == null ? '' : Number(n).toLocaleString('pt-BR');
const fNum1 = n => n == null ? '' : Number(n).toLocaleString('pt-BR', {minimumFractionDigits: 1, maximumFractionDigits: 1});
const fPct = n => n == null ? '' : (Number(n) * 100).toFixed(1).replace('.', ',') + '%';
const fReal = n => n == null ? '' : 'R$ ' + Math.round(Number(n)).toLocaleString('pt-BR');

function g(D, path) {
  if (!D) return null;
  return path.split('.').reduce((o, k) => (o && o[k] !== undefined && o[k] !== null) ? o[k] : null, D);
}

// ---- Estado vazio ----------------------------------------------------------
// Toda seção do extrator vira {"erro": ...} quando a fonte falha, e várias
// voltam legitimamente zeradas para municípios fora da amostra. `ok()` filtra
// as duas coisas; os `vazio*` desenham um "sem dados" limpo no lugar do cartão
// em branco ou do Chart.js estourando com array vazio.
const SEM_DADO = 'Sem dados para este município';
const ok = o => (o && typeof o === 'object' && !o.erro) ? o : null;
const el_ = id => document.getElementById(id);
function setTxt(id, txt) { const e = el_(id); if (e) e.textContent = txt; }
function setHtml(id, html) { const e = el_(id); if (e) e.innerHTML = html; }
function setCls(id, cls) { const e = el_(id); if (e) e.className = cls; }
function vazioLista(id, msg) {
  setHtml(id, '<li style="border-bottom:none;display:block"><span class="empty">' + (msg || SEM_DADO) + '</span></li>');
}
function vazioTabela(id, cols, msg) {
  setHtml(id, '<tr><td colspan="' + (cols || 3) + '" style="border-bottom:none;width:auto"><span class="empty">' + (msg || SEM_DADO) + '</span></td></tr>');
}
function vazioGrafico(id, msg) {
  const cv = el_(id); if (!cv) return;
  const box = cv.closest('.chart-container') || cv.parentElement;
  if (box) box.innerHTML = '<div class="empty">' + (msg || SEM_DADO) + '</div>';
}
function vazioValor(id) {
  const e = el_(id); if (!e) return;
  e.textContent = '—'; e.classList.add('empty-val'); e.title = SEM_DADO;
  // No cartão, o traço sozinho não diz nada: uma linha explica a ausência.
  const card = e.classList.contains('value') && e.closest('.card');
  if (card && !card.querySelector('.empty-note')) {
    e.insertAdjacentHTML('afterend', '<div class="empty-note">' + SEM_DADO + '</div>');
  }
}
function vazioValores(...ids) { ids.forEach(vazioValor); }
// Os semáforos vinham escritos à mão no HTML com o veredito de Nova Friburgo — em
// qualquer outro município eles mentiriam calados. `pill()` reescreve cada um a
// partir do próprio dado; sem dado, o selo some em vez de afirmar algo não conferido.
function pill(id, cls, txt) {
  const e = el_(id); if (!e) return;
  if (!cls) { e.style.display = 'none'; return; }
  e.style.display = '';
  e.className = 'status ' + cls;
  e.textContent = txt;
}
// Compara com uma referência onde MAIOR é melhor (ou pior, com `maiorEhPior`)
function pillVs(id, valor, ref, rotulos, maiorEhPior) {
  if (valor == null || ref == null || !isFinite(valor) || !isFinite(ref)) { pill(id, null); return; }
  const razao = valor / ref;
  const bom = maiorEhPior ? razao <= 1 : razao >= 1;
  if (bom) { pill(id, 'st-good', '✓ ' + rotulos[0]); return; }
  const desvio = Math.abs(1 - razao);
  pill(id, desvio <= 0.15 ? 'st-warn' : (desvio <= 0.4 ? 'st-serious' : 'st-crit'), '! ' + rotulos[1]);
}
// Soma entradas repetidas de um mesmo rótulo (o SINAN devolve "Ignorado" duas vezes)
function agrupa(arr, chave, valor) {
  const m = new Map();
  (arr || []).forEach(r => m.set(r[chave], (m.get(r[chave]) || 0) + (Number(r[valor]) || 0)));
  return [...m.entries()].map(([k, v]) => ({ k, v })).sort((a, b) => b.v - a.v);
}
const pctDe = (n, t) => t ? (Number(n) / t * 100) : 0;
const liRow = (a, b) => '<li><span>' + a + '</span><span>' + b + '</span></li>';
// Barras proporcionais (.bench-bars) para recortes categóricos em cartão estreito,
// onde um canvas do Chart.js sobraria: mesma leitura visual, sem eixo nem legenda.
// `linhas` é a saída de agrupa(): [{k, v}]. A escala é o maior valor do próprio
// recorte — a % ao lado é sobre o total informado, não sobre esse máximo.
function barrasCategoria(id, linhas, total, cor, opts) {
  const o = opts || {};
  const alvo = el_(id); if (!alvo) return;
  if (!linhas || !linhas.length) { alvo.innerHTML = '<div class="empty">' + (o.msgVazio || SEM_DADO) + '</div>'; return; }
  // `escalaMax` fixa o topo da barra (índices 0–1 querem 1, não o maior da lista)
  const max = o.escalaMax != null ? o.escalaMax : Math.max(...linhas.map(r => r.v), 1);
  const rotulo = r => o.fmtValor ? o.fmtValor(r.v)
    : o.soPct ? fNum1(pctDe(r.v, total)) + '%'
    : fNum(r.v) + (total ? ' · ' + fNum1(pctDe(r.v, total)) + '%' : '');
  alvo.innerHTML = linhas.map(r =>
    '<div class="row"><span title="' + (r.titulo || r.k) + '">' + r.k + '</span>' +
    '<div class="track"><div class="fill" style="width:' + (r.v / max * 100).toFixed(1) + '%' +
    (cor ? ';background:' + cor : '') + '"></div></div>' +
    '<span>' + rotulo(r) + '</span></div>'
  ).join('');
}
// Corta no espaço mais próximo em vez de no meio da palavra, e sinaliza o corte
function truncaPalavra(s, n) {
  const t = String(s || '');
  if (t.length <= n) return t;
  const corte = t.slice(0, n);
  const esp = corte.lastIndexOf(' ');
  return (esp > n * 0.6 ? corte.slice(0, esp) : corte).replace(/[ ,;.]+$/, '') + '…';
}
// O DATASUS grava o capítulo do CID-10 abreviado a ponto de ficar ilegível num eixo
// ("Sint sinais e achad anorm ex clín e laborat"). O algarismo romano é estável entre
// municípios e anos, então o rótulo sai daqui; o texto original fica no tooltip.
const CAPITULO_CID = {
  I: 'Doenças infecciosas e parasitárias', II: 'Neoplasias (tumores)',
  III: 'Doenças do sangue e imunitárias', IV: 'Doenças endócrinas e metabólicas',
  V: 'Transtornos mentais e comportamentais', VI: 'Doenças do sistema nervoso',
  VII: 'Doenças do olho e anexos', VIII: 'Doenças do ouvido',
  IX: 'Doenças do aparelho circulatório', X: 'Doenças do aparelho respiratório',
  XI: 'Doenças do aparelho digestivo', XII: 'Doenças da pele',
  XIII: 'Doenças osteomusculares', XIV: 'Doenças do aparelho geniturinário',
  XV: 'Gravidez, parto e puerpério', XVI: 'Afecções do período perinatal',
  XVII: 'Malformações congênitas', XVIII: 'Sintomas e achados mal definidos',
  XIX: 'Lesões e envenenamentos', XX: 'Causas externas',
  XXI: 'Contatos com serviços de saúde', XXII: 'Códigos de propósito especial',
};
function capituloCurto(s) {
  const m = /^([IVXL]+)\s*\.?\s*/.exec(String(s || ''));
  if (m && CAPITULO_CID[m[1]]) return CAPITULO_CID[m[1]];
  return truncaPalavra(String(s || '').replace(/^[IVXL]+\s*\.?\s*/, ''), 38);
}
// Fontes federais gravam nome próprio em CAIXA ALTA; minúsculo puro fica pior ainda
const MINUSCULAS = new Set(['de', 'da', 'do', 'das', 'dos', 'e', 'em', 'a', 'o', 'para', 'por', 'com']);
// Alguns registros do Compras.gov trazem o rótulo do campo colado na razão social
// ("Contratado : FULANO LTDA") — a etiqueta não é parte do nome da empresa
const limpaRazao = s => String(s || '').replace(/^\s*contratad[oa]\s*:\s*/i, '').trim();
// Siglas e códigos que perdem sentido em caixa de título ("Filo Sa", "Ferragens 3f")
const SIGLAS = new Set(['sa', 's/a', 'me', 'epp', 'eireli', 'cnpj', 'cpf', 'ii', 'iii', 'iv']);
const titulo = s => limpaRazao(s).toLowerCase().split(/(\s+|-)/).map((w, i) => {
  if (!/\w/.test(w)) return w;
  if (i > 0 && MINUSCULAS.has(w)) return w;
  if (SIGLAS.has(w) || (w.length <= 3 && /\d/.test(w))) return w.toUpperCase();
  return w.charAt(0).toUpperCase() + w.slice(1);
}).join('');

async function init() {
  const D = await loadData();
  if (!D) return;
  const ger = String(g(D, 'gerado_em') || '');
  ANO_EM_CURSO = Number(ger.slice(0, 4)) || null;
  const mesGer = Number(ger.slice(5, 7));
  MES_EXTRACAO = mesGer ? ['jan', 'fev', 'mar', 'abr', 'mai', 'jun', 'jul', 'ago', 'set', 'out', 'nov', 'dez'][mesGer - 1] + '/' + ger.slice(0, 4) : '';

  // Page title
  document.getElementById('pageTitle').textContent = g(D, 'municipio.nome') + ', ' + g(D, 'municipio.sigla_uf') + ' — Dashboard Municipal';

  // data-path elements
  renderDataPaths(D);

  // O rodapé nomeia o arquivo que alimentou a página
  setTxt('footerJson', JSON_PATH);

  // Rodapé da barra lateral: conta os indicadores que este JSON de fato traz. Um
  // indicador é cada número não nulo ou cada série/ranking não vazio dentro de
  // `secoes`, sem contar metadados (fonte, ano, referência…) nem blocos com erro
  // ou "disponivel: false" — o mesmo critério para qualquer município.
  const META = /^(fonte|fontes|ano|anos|referencia|competencia|periodo|nota|notas|motivo|disponivel|erro|data_.*|gerado_em|ano_.*|unidade|id_.*)$/;
  const contaInd = o => {
    if (Array.isArray(o)) return o.length ? 1 : 0;
    if (o && typeof o === 'object') {
      if (o.erro || o.disponivel === false) return 0;
      return Object.entries(o).reduce((n, [k, v]) => n + (META.test(k) ? 0 : contaInd(v)), 0);
    }
    return (o === null || o === undefined || o === '') ? 0 : 1;
  };
  const nInd = fNum(contaInd(g(D, 'secoes')));
  setTxt('nIndicadores', nInd);
  setTxt('nIndicadoresHero', nInd);
  setTxt('nTemas', document.querySelectorAll('.sidebar-nav .sidebar-item').length - 1);

  // Helper: find item in array by {key: val}
  function find(arr, key, val) {
    if (!arr) return null;
    return arr.find(d => String(d[key]) === String(val)) || null;
  }

  // Demo — density
  const area = g(D, 'municipio.area_km2') || 935;
  const pop2022 = g(D, 'secoes.demografia.censo_2022.populacao') || 0;
  const popSerie = g(D, 'secoes.demografia.populacao_serie') || [];
  const pop2024item = find(popSerie, 'ano', 2024);
  const pop2024 = pop2024item ? pop2024item.populacao : pop2022;
  document.getElementById('popVal').innerHTML = fNum(pop2024) + ' <span class="unit">hab</span>';
  if (document.getElementById('popVal2')) document.getElementById('popVal2').innerHTML = fNum(pop2024) + ' <span class="unit">hab</span>';
  document.getElementById('densVal').innerHTML = Math.round(pop2024 / area) + ' <span class="unit">hab/km²</span>';
  const dDemo = (pop2024 / pop2022 - 1) * 100;
  setCls('demoPopDelta', 'delta ' + (dDemo >= 0 ? 'up' : 'down'));
  setHtml('demoPopDelta', (dDemo >= 0 ? '▲ +' : '▼ −') + Math.abs(dDemo).toFixed(1).replace('.', ',') + '% <span class="vs">vs censo 2022</span>');

  const censoAnterior = find(popSerie, 'ano', 2010);
  if (censoAnterior) {
    const dCenso = (pop2022 / censoAnterior.populacao - 1) * 100;
    setCls('censoDelta', 'delta ' + (dCenso >= 0 ? 'up' : 'down'));
    setHtml('censoDelta', (dCenso >= 0 ? '▲ +' : '▼ −') + Math.abs(dCenso).toFixed(1).replace('.', ',') + '% <span class="vs">vs censo 2010</span>');
  }

  document.getElementById('domicSub').textContent = (pop2022 / (g(D, 'secoes.demografia.censo_2022.domicilios') || 1)).toFixed(1).replace('.', ',') + ' moradores/domicílio';

  // Pop evolution list
  const popEvolList = document.getElementById('popEvolList');
  if (popEvolList) {
    const selYears = [1991, 2000, 2010, 2022];
    popEvolList.innerHTML = selYears.map(y => {
      const it = find(popSerie, 'ano', y);
      return '<li><span>' + y + '</span><span>' + (it ? Math.round(it.populacao / 1000) + 'k' : '-') + '</span></li>';
    }).join('');
  }

  // Envelhecimento
  const env = g(D, 'secoes.demografia.censo_2022.indice_envelhecimento');
  document.getElementById('envVal').textContent = env != null ? fNum1(env) : '';

  // Pop evolution chart
  if (document.getElementById('popEvolChart')) {
    const selYears = [1991, 2000, 2010, 2022];
    document.getElementById('popEvolAno').textContent = selYears[0] + '–' + selYears[selYears.length - 1] + ' (censos)';
    const yearLabels = selYears.map(String);
    const popData = selYears.map(y => { const it = find(popSerie, 'ano', y); return it ? it.populacao : 0; });
    criaGrafico(document.getElementById('popEvolChart'), {
      type: 'line', data: {
        labels: yearLabels,
        datasets: [{ label: 'População', data: popData, borderColor: C.s1, backgroundColor: C.s1fill, fill: true, pointBackgroundColor: C.s1, ...lineStyle }]
      },
      options: { ...chartOpts, plugins: noLegend,
        scales: { y: { ticks: { callback: v => fNum(v) } } } }
    });
  }

  // Age pyramid
  if (document.getElementById('popAgeChart')) {
    const piramide = g(D, 'secoes.demografia.piramide_etaria_2022');
    if (piramide) {
      const groups = piramide.grupos || [];
      const labels = groups.map(g => g.replace(' anos', '').replace(' ou mais', '+'));
      const menData = (piramide.homens || []).map(v => -v);
      const womenData = piramide.mulheres || [];
      criaGrafico(document.getElementById('popAgeChart'), {
        type: 'bar', data: {
          labels,
          datasets: [
            { label: 'Homens', data: menData, backgroundColor: C.s1, maxBarThickness: 12, borderRadius: 3, borderSkipped: 'start' },
            { label: 'Mulheres', data: womenData, backgroundColor: C.s2, maxBarThickness: 12, borderRadius: 3, borderSkipped: 'start' },
          ]
        },
        options: {
          ...chartOpts, indexAxis: 'y',
          plugins: { ...chartOpts.plugins, tooltip: { ...chartOpts.plugins.tooltip,
            callbacks: { label: ctx => ctx.dataset.label + ': ' + fNum(Math.abs(ctx.parsed.x)) } } },
          scales: {
            x: { stacked: true, ticks: { color: C.muted, callback: v => fNum(Math.abs(v)) }, grid: { color: C.grid } },
            y: { stacked: true, ticks: { color: C.muted, autoSkip: false, font: { size: 10 } }, grid: { display: false } },
          }
        }
      });
    }
  }

  // Geografia
  const geo = g(D, 'secoes.geografia');
  if (geo) {
    const sede = geo.sede_municipal;
    if (sede) {
      document.getElementById('geoSedeAno').textContent = sede.ano || '';
      document.getElementById('geoSedeVal').textContent = Math.abs(sede.lat).toFixed(3).replace('.', ',') + '° S, ' + Math.abs(sede.lon).toFixed(3).replace('.', ',') + '° O';
    }

    const biomas = geo.biomas || [];
    document.getElementById('geoBiomaList').innerHTML = biomas.length
      ? biomas.map(b => '<li><span>' + b.nome + '</span><span>' + b.pct_area.toFixed(1).replace('.', ',') + '% da área</span></li>').join('')
      : '<li><span>Sem dado</span><span>—</span></li>';

    document.getElementById('geoSemiaridoVal').textContent = geo.semiarido ? 'Sim' : 'Não';

    const arranjo = geo.arranjo_populacional;
    if (arranjo) {
      document.getElementById('geoArranjoVal').textContent = arranjo.nome;
      document.getElementById('geoArranjoSub').textContent = 'População (2010): ' + fNum(arranjo.populacao_2010 || 0);
    } else {
      document.getElementById('geoArranjoVal').textContent = 'Isolado';
      document.getElementById('geoArranjoSub').textContent = 'Não integra arranjo populacional (IBGE)';
    }

    const rm = geo.regiao_metropolitana;
    if (rm) {
      document.getElementById('geoRmVal').textContent = rm.nome;
      document.getElementById('geoRmSub').textContent = rm.tipo || '';
    } else {
      document.getElementById('geoRmVal').textContent = 'Não integra';
      document.getElementById('geoRmSub').textContent = '';
    }

    const ucs = geo.unidades_conservacao;
    if (ucs) {
      document.getElementById('geoUcTotal').textContent = '· ' + ucs.total;
      document.getElementById('geoUcCatList').innerHTML = (ucs.por_categoria || []).map(c =>
        '<li><span>' + c.categoria + ' (' + c.esfera + ')</span><span>' + c.quantidade + '</span></li>'
      ).join('');
      document.getElementById('geoUcListaDet').innerHTML = (ucs.lista || []).map(u =>
        '<li><span>' + u.unidade_conservacao + '</span><span>' + (u.ano_criacao || '—') + '</span></li>'
      ).join('');
    }
  }

  // PRODES
  const prodesArr = g(D, 'secoes.meio_ambiente.prodes.biomas') || [];
  const prodes = prodesArr[0];
  if (prodes) {
    document.getElementById('prodesAno').textContent = prodes.ano || '';
    const total = prodes.area_total || 0;
    const veg = prodes.vegetacao_natural || 0;
    const desm = prodes.desmatado || 0;
    const vegPct = total > 0 ? veg / total * 100 : 0;
    el_('prodesMeter').style.width = vegPct.toFixed(1) + '%';
    setTxt('prodesVegPct', fNum1(vegPct) + '%');
    setTxt('prodesAreaTotal', 'Área do bioma: ' + fNum(Math.round(total * 100)) + ' ha');
    // `desmatado` do PRODES é a área acumulada, não a perda do ano: veg + desmatado = total.
    // A perda anual é o incremento, que o gráfico ao lado calcula a partir da série.
    setHtml('prodesList',
      liRow('Vegetação natural', fNum(Math.round(veg * 100)) + ' ha') +
      liRow('Desmatado (acumulado)', fNum(Math.round(desm * 100)) + ' ha (' + fNum1(total > 0 ? desm / total * 100 : 0) + '%)'));
  } else {
    setTxt('prodesVegPct', '—'); setTxt('prodesAreaTotal', '');
    vazioLista('prodesList');
  }

  // SEEG chart
  if (document.getElementById('seegChart')) {
    const seeg = g(D, 'secoes.meio_ambiente.seeg');
    if (seeg) {
      document.getElementById('seegAno').textContent = seeg.ano || '';
      document.getElementById('seegTotal').textContent = '· ' + fNum(Math.round(seeg.total_tco2e || 0)) + ' tCO₂e';
      const setores = (seeg.por_setor || []).filter(s => s.emissao_tco2e > 0);
      const sLabels = setores.map(s => s.setor.replace('Mudança de Uso da Terra e Floresta', 'Uso da Terra'));
      const sData = setores.map(s => Math.round(s.emissao_tco2e));
      criaGrafico(document.getElementById('seegChart'), {
        type: 'bar', data: {
          labels: sLabels,
          datasets: [{ data: sData, backgroundColor: C.s1, maxBarThickness: 16, borderRadius: 4, borderSkipped: 'start' }]
        },
        options: { ...chartOpts, indexAxis: 'y',
          plugins: { ...noLegend, tooltip: { ...chartOpts.plugins.tooltip,
            callbacks: { label: ctx => fNum(ctx.parsed.x) + ' tCO₂e' } } },
          scales: { x: { ticks: { color: C.muted, callback: v => fNum(v) }, grid: { color: C.grid } },
                    y: { ticks: { color: C.tick, autoSkip: false, font: { size: 11 } }, grid: { display: false } } }
        }
      });
    }
  }

  // PRODES — incremento anual de desmatamento (km² perdidos a cada ano, não o acumulado)
  if (document.getElementById('prodesChart')) {
    const serie = g(D, 'secoes.meio_ambiente.prodes.serie') || [];
    if (serie.length > 1) {
      const incrementos = serie.slice(1).map((r, i) => ({ ano: r.ano, incremento: r.desmatado - serie[i].desmatado }));
      document.getElementById('prodesSerieAno').textContent = incrementos[0].ano + '–' + incrementos[incrementos.length - 1].ano;
      criaGrafico(document.getElementById('prodesChart'), {
        type: 'bar', data: {
          labels: incrementos.map(r => r.ano),
          datasets: [
            { label: 'Área desmatada no ano (km²)', data: incrementos.map(r => r.incremento), backgroundColor: C.s6, maxBarThickness: 22, borderRadius: 3 },
          ]
        },
        options: { ...chartOpts,
          plugins: { ...noLegend, tooltip: { ...chartOpts.plugins.tooltip,
            callbacks: { label: ctx => 'Perda: ' + fNum1(ctx.parsed.y) + ' km²' } } },
          scales: { x: { ticks: { color: C.muted }, grid: { color: C.grid } },
                    y: { ticks: { color: C.muted, callback: v => fNum1(v) + ' km²' }, grid: { color: C.grid } } }
        }
      });
    }
  }

  // Queimadas — focos por ano, coloridos por intensidade
  if (document.getElementById('queimadasChart')) {
    const serie = g(D, 'secoes.meio_ambiente.queimadas.serie') || [];
    if (serie.length) {
      document.getElementById('queimadasAno').textContent = serie[0].ano + '–' + serie[serie.length - 1].ano;
      const maxFocos = Math.max(...serie.map(r => r.focos || 0), 1);
      const intensityColor = t => {
        const c1 = [250, 178, 25], c2 = [208, 59, 59];
        const mix = i => Math.round(c1[i] + (c2[i] - c1[i]) * t);
        return `rgb(${mix(0)},${mix(1)},${mix(2)})`;
      };
      const colors = serie.map(r => intensityColor((r.focos || 0) / maxFocos));
      criaGrafico(document.getElementById('queimadasChart'), {
        type: 'bar', data: {
          labels: serie.map(r => r.ano),
          datasets: [{ label: 'Focos', data: serie.map(r => r.focos), backgroundColor: colors, maxBarThickness: 22, borderRadius: 3 }]
        },
        options: { ...chartOpts, plugins: { ...noLegend, tooltip: { ...chartOpts.plugins.tooltip,
              callbacks: { label: ctx => {
                const r = serie[ctx.dataIndex];
                return r.frp_medio != null ? fNum(r.focos) + ' focos (FRP médio ' + fNum1(r.frp_medio) + ')' : fNum(r.focos) + ' focos';
              } } } },
          scales: { ...chartOpts.scales, y: { ticks: { color: C.muted, callback: v => fNum(v) }, grid: { color: C.grid } } } }
      });
    }
  }

  // SISAM — qualidade do ar (dual-axis PM2.5 + CO)
  if (document.getElementById('sisamChart')) {
    const serie = g(D, 'secoes.meio_ambiente.sisam.serie') || [];
    if (serie.length) {
      document.getElementById('sisamAno').textContent = serie[0].ano + '–' + serie[serie.length - 1].ano;
      criaGrafico(document.getElementById('sisamChart'), {
        type: 'line', data: {
          labels: serie.map(r => r.ano),
          datasets: [
            { label: 'PM2.5 (µg/m³)', data: serie.map(r => r.pm25_ugm3), borderColor: C.s3, backgroundColor: C.s3, yAxisID: 'y', pointBackgroundColor: C.s3, ...lineStyle, fill: false },
            { label: 'CO (ppb)', data: serie.map(r => r.co_ppb), borderColor: C.s1, backgroundColor: C.s1, yAxisID: 'y1', pointBackgroundColor: C.s1, ...lineStyle, fill: false },
          ]
        },
        options: { ...chartOpts,
          scales: {
            x: { ticks: { color: C.muted }, grid: { color: C.grid } },
            y: { position: 'left', ticks: { color: C.s3, callback: v => fNum1(v) }, grid: { color: C.grid }, title: { display: true, text: 'PM2.5 (µg/m³)', color: C.s3 } },
            y1: { position: 'right', ticks: { color: C.s1, callback: v => fNum1(v) }, grid: { display: false }, title: { display: true, text: 'CO (ppb)', color: C.s1 } },
          }
        }
      });
    }
  }

  // MapBiomas — principais transições de uso do solo (2010 vs 2020)
  if (document.getElementById('mapbiomasChart')) {
    const mb = g(D, 'secoes.meio_ambiente.mapbiomas');
    const trans = (mb && mb.transicoes) || [];
    if (trans.length) {
      const mbEstreito = matchMedia('(max-width: 768px)').matches;
      // duas linhas por rótulo pedem mais altura, senão eles se sobrepõem
      if (mbEstreito) document.getElementById('mapbiomasChart').parentElement.style.minHeight = (trans.length * 46 + 70) + 'px';
      criaGrafico(document.getElementById('mapbiomasChart'), {
        type: 'bar', data: {
          // no celular o eixo corta rótulos longos: quebra em duas linhas
          labels: trans.map(t => mbEstreito ? [t.de + ' →', t.para] : t.de + ' → ' + t.para),
          datasets: [
            { label: '2010', data: trans.map(t => t.area_2010), backgroundColor: C.s1, maxBarThickness: 16, borderRadius: 3 },
            { label: '2020', data: trans.map(t => t.area_2020), backgroundColor: C.s5, maxBarThickness: 16, borderRadius: 3 },
          ]
        },
        options: { ...chartOpts, indexAxis: 'y',
          plugins: { ...chartOpts.plugins, tooltip: { ...chartOpts.plugins.tooltip,
            callbacks: { title: items => [].concat(items[0].label).join(' ').replace(/,/g, ' '),
                         label: ctx => ctx.dataset.label + ': ' + fNum1(ctx.parsed.x) + ' km²' } } },
          scales: { x: { ticks: { color: C.muted, callback: v => fNum(v) + ' km²' }, grid: { color: C.grid } },
                    y: { ticks: { color: C.tick, autoSkip: false, font: { size: 10 } }, grid: { display: false } } }
        }
      });
    }
  }

  // SNIS
  const snis = g(D, 'secoes.infraestrutura.snis');
  if (snis) {
    const ano = snis.ano || '';
    document.getElementById('snisAno').textContent = ano;
    document.getElementById('snisAno2').textContent = ano;
    document.getElementById('snisAno3').textContent = ano;
    document.getElementById('snisAno4').textContent = ano;
    document.getElementById('aguaVal').innerHTML = (snis.indice_atendimento_total_agua || 0).toFixed(1).replace('.', ',') + ' <span class="unit">%</span>';
    document.getElementById('esgCVal').innerHTML = (snis.indice_coleta_esgoto || 0).toFixed(1).replace('.', ',') + ' <span class="unit">%</span>';
    document.getElementById('esgTVal').innerHTML = (snis.indice_tratamento_esgoto || 0).toFixed(1).replace('.', ',') + ' <span class="unit">%</span>';
    if (snis.ano_anterior) {
      const aa = snis.ano_anterior;
      // Sinal e cor têm que seguir o dado: antes ficava sempre "▲ +" e verde, gerando "+-1,8 pp"
      const ppDelta = (id, atual, anterior) => {
        const d = (atual || 0) - (anterior || 0);
        const e = document.getElementById(id);
        const seta = Math.abs(d) < 0.05 ? '=' : (d > 0 ? '▲ +' : '▼ −');
        e.className = 'delta ' + (Math.abs(d) < 0.05 ? 'flat' : (d > 0 ? 'up' : 'down'));
        e.innerHTML = seta + ' ' + Math.abs(d).toFixed(1).replace('.', ',') + ' pp <span class="vs">vs ' + (ano - 1) + '</span>';
      };
      ppDelta('aguaDelta', snis.indice_atendimento_total_agua, aa.a);
      ppDelta('esgCDelta', snis.indice_coleta_esgoto, aa.c);
    }
    // O SNIS publica POPULAÇÃO atendida, não número de ligações: a linha "ligações de
    // esgoto" era essa população multiplicada por 0,3 — um número inventado. Mostrar o
    // que a fonte de fato traz, com o rótulo certo.
    const mm3 = v => v ? fNum1(v / 1e3) + ' mi m³' : '—';
    document.getElementById('snisList').innerHTML =
      liRow('População atendida com água', fNum(snis.populacao_atendida_agua || 0)) +
      liRow('População atendida com esgoto', fNum(snis.populacao_atentida_esgoto || 0)) +
      liRow('Perdas na distribuição de água', snis.indice_perda_distribuicao_agua != null
        ? fNum1(snis.indice_perda_distribuicao_agua) + '%' : '—') +
      liRow('Despesa total do serviço', snis.despesa_total_servico
        ? 'R$ ' + Math.round(snis.despesa_total_servico / 1e6).toLocaleString('pt-BR') + ' mi' : '—');
    document.getElementById('snisDetList').innerHTML =
      liRow('Volume de água consumido', mm3(snis.volume_agua_consumido)) +
      liRow('Volume de esgoto coletado', mm3(snis.volume_esgoto_coletado)) +
      liRow('Volume de esgoto tratado', mm3(snis.volume_esgoto_tratado)) +
      liRow('Extensão da rede de água', fNum(Math.round(snis.extensao_rede_agua || 0)) + ' km') +
      liRow('Extensão da rede de esgoto', fNum(Math.round(snis.extensao_rede_esgoto || 0)) + ' km');
  } else {
    vazioValores('aguaVal', 'esgCVal', 'esgTVal');
    vazioLista('snisList'); vazioLista('snisDetList');
  }

  // Atlas esgotos
  const atlas = g(D, 'secoes.infraestrutura.atlas_esgotos');
  if (atlas) {
    document.getElementById('atlasInvest').textContent = (atlas.investimento_coleta_tratatamento ? 'R$ ' + Math.round(atlas.investimento_coleta_tratatamento / 1e6).toLocaleString('pt-BR') + ' mi' : '');
    document.getElementById('atlasCom').textContent = (atlas.indice_atendimento_com_coleta_com_tratamento != null ? (atlas.indice_atendimento_com_coleta_com_tratamento * 100).toFixed(1).replace('.', ',') + '%' : '');
    document.getElementById('atlasSem').textContent = (atlas.indice_sem_atendimento_sem_coleta_sem_tratamento != null ? (atlas.indice_sem_atendimento_sem_coleta_sem_tratamento * 100).toFixed(1).replace('.', ',') + '%' : '');
    document.getElementById('atlasPop2013').textContent = fNum(atlas.populacao_urbana_2013 || 0);
    document.getElementById('atlasPop2035').textContent = fNum(atlas.populacao_urbana_2035 || 0);
    document.getElementById('atlasSol').textContent = (atlas.indice_atendimento_solucao_individual != null ? (atlas.indice_atendimento_solucao_individual * 100).toFixed(1).replace('.', ',') + '%' : '');
  }

  // PIB
  const pibSerie = g(D, 'secoes.economia.pib.serie') || [];
  const pibUlt = pibSerie.length > 0 ? pibSerie[pibSerie.length - 1] : null;
  if (pibUlt) {
    document.getElementById('pibAno').textContent = pibUlt.ano || '';
    document.getElementById('pibVal').innerHTML = 'R$ ' + fNum1(pibUlt.pib / 1e9) + ' <span class="unit">bi</span>';
    if (pibSerie.length > 1) {
      const pibAnt = pibSerie[pibSerie.length - 2];
      // A seta vinha fixa em "▲ +" — em ano de queda saía "▲ +-3,1%"
      const dPib = pibAnt ? (pibUlt.pib / pibAnt.pib - 1) * 100 : 0;
      setCls('pibDelta', 'delta ' + (dPib >= 0 ? 'up' : 'down'));
      setHtml('pibDelta', (dPib >= 0 ? '▲ +' : '▼ −') + Math.abs(dPib).toFixed(1).replace('.', ',') +
        '% <span class="vs">vs ' + pibAnt.ano + ' (nominal)</span>');
    }
    // O ano mais recente do PIB costuma sair sem a abertura (impostos, VA por setor):
    // esses cartões usam o último ano que a traz, em vez de mostrar "R$ 0".
    const pibDet = [...pibSerie].reverse().find(r => r.va != null) || null;
    if (!pibDet) { vazioValores('liqImpVal', 'vaTotal'); vazioGrafico('vaChart'); vazioLista('vaComp'); }
    else {
    document.getElementById('impAno').textContent = pibDet.ano || '';
    if (pibDet.impostos_liquidos != null) document.getElementById('liqImpVal').innerHTML = 'R$ ' + fNum(Math.round(pibDet.impostos_liquidos / 1e6)) + ' <span class="unit">mi</span>';
    else vazioValor('liqImpVal');
    document.getElementById('impSub').textContent = (pibDet.impostos_liquidos && pibDet.pib) ? (pibDet.impostos_liquidos / pibDet.pib * 100).toFixed(1).replace('.', ',') + '% do PIB' : '';
    document.getElementById('vaAno').textContent = pibDet.ano || '';
    document.getElementById('vaTotal').innerHTML = 'R$ ' + fNum1(pibDet.va / 1e9) + ' <span class="unit">bi</span>';
    const vaServ = (pibDet.va_servicos || 0) + (pibDet.va_adespss || 0);
    const vaTotal = pibDet.va || 1;
    // Antes dizia "Serviços lideram (84%)" — os 84% eram serviços + adm. pública,
    // e o cartão ao lado mostrava serviços em 56%. Nomear a conta resolve a contradição.
    setTxt('vaSub', 'Serviços e adm. pública somam ' + (vaServ / vaTotal * 100).toFixed(0) + '% do valor adicionado');

    // VA chart
    if (document.getElementById('vaChart')) {
      document.getElementById('vaSetorAno').textContent = pibDet.ano || '';
      const vaLabels = ['Serviços', 'Indústria', 'Adm. Pública', 'Agropecuária'];
      const vaData = [
        Math.round((pibDet.va_servicos || 0) / 1e6),
        Math.round((pibDet.va_industria || 0) / 1e6),
        Math.round((pibDet.va_adespss || 0) / 1e6),
        Math.round((pibDet.va_agropecuaria || 0) / 1e6)
      ];
      criaGrafico(document.getElementById('vaChart'), {
        type: 'doughnut', data: {
          labels: vaLabels,
          datasets: [{ data: vaData, backgroundColor: [C.s1, C.s2, C.s3, C.s4], borderColor: C.surface, borderWidth: 2 }]
        },
        options: {
          responsive: true, maintainAspectRatio: false, cutout: '60%',
          plugins: {
            legend: { position: 'bottom', labels: { color: C.tick, padding: 10, usePointStyle: true } },
            tooltip: { ...chartOpts.plugins.tooltip,
              callbacks: { label: ctx => ctx.label + ': R$ ' + fNum(ctx.parsed) + ' mi' } }
          }
        }
      });
    }

    // VA composition
    document.getElementById('vaComp').innerHTML =
      '<li><span>Serviços</span><span>R$ ' + fNum1((pibDet.va_servicos || 0) / 1e9) + ' bi · ' + ((pibDet.va_servicos || 0) / vaTotal * 100).toFixed(1).replace('.', ',') + '%</span></li>' +
      '<li><span>Indústria</span><span>R$ ' + fNum1((pibDet.va_industria || 0) / 1e9) + ' bi · ' + ((pibDet.va_industria || 0) / vaTotal * 100).toFixed(1).replace('.', ',') + '%</span></li>' +
      '<li><span>Adm. Pública</span><span>R$ ' + fNum1((pibDet.va_adespss || 0) / 1e9) + ' bi · ' + ((pibDet.va_adespss || 0) / vaTotal * 100).toFixed(1).replace('.', ',') + '%</span></li>' +
      '<li><span>Agropecuária</span><span>R$ ' + fNum1((pibDet.va_agropecuaria || 0) / 1e9) + ' bi · ' + ((pibDet.va_agropecuaria || 0) / vaTotal * 100).toFixed(1).replace('.', ',') + '%</span></li>';
    }
  }

  // PIB per capita ranking
  const ranking = g(D, 'secoes.economia.pib.ranking_uf');
  if (ranking) {
    document.getElementById('pibRank').textContent = ranking.posicao + 'º entre ' + ranking.total + ' municípios do RJ';
  }

  // PIB per capita bars
  const pibPc = g(D, 'secoes.economia.pib.pib_per_capita');
  if (pibPc) {
    document.getElementById('pibPcAno').textContent = pibPc.ano || '';
    const maxVal = Math.max(pibPc.uf || 0, pibPc.brasil || 0, pibPc.valor || 1);
    const pctMe = (pibPc.valor / maxVal * 100).toFixed(0);
    const pctBr = (pibPc.brasil / maxVal * 100).toFixed(0);
    const pctUf = (pibPc.uf / maxVal * 100).toFixed(0);
    document.getElementById('pibPcBars').innerHTML =
      '<div class="row me"><span>' + g(D, 'municipio.nome') + '</span><div class="track"><div class="fill" style="width:' + pctMe + '%"></div></div><span>' + Math.round(pibPc.valor / 1000) + 'k</span></div>' +
      '<div class="row"><span>Brasil</span><div class="track"><div class="fill" style="width:' + pctBr + '%"></div></div><span>' + Math.round(pibPc.brasil / 1000) + 'k</span></div>' +
      '<div class="row"><span>' + g(D, 'municipio.sigla_uf') + '</span><div class="track"><div class="fill" style="width:' + pctUf + '%"></div></div><span>' + Math.round(pibPc.uf / 1000) + 'k</span></div>';
  }

  // PIB per capita delta
  if (pibSerie && pibSerie.length > 1) {
    const pibPcUlt = pibSerie[pibSerie.length - 1];
    const pibPcAnt = pibSerie.length > 1 ? pibSerie[pibSerie.length - 2] : null;
    if (pibPcUlt && pibPcAnt && pibPcUlt.pib && pibPcAnt.pib) {
      const pibPopUlt = find(popSerie, 'ano', pibPcUlt.ano);
      const pibPopAnt = find(popSerie, 'ano', pibPcAnt.ano);
      if (pibPopUlt && pibPopAnt) {
        const pcUlt = pibPcUlt.pib / pibPopUlt.populacao;
        const pcAnt = pibPcAnt.pib / pibPopAnt.populacao;
        const dPc = (pcUlt / pcAnt - 1) * 100;
        setCls('pibPcDelta', 'delta ' + (dPc >= 0 ? 'up' : 'down'));
        setHtml('pibPcDelta', (dPc >= 0 ? '▲ +' : '▼ −') + Math.abs(dPc).toFixed(1).replace('.', ',') +
          '% <span class="vs">vs ' + pibPcAnt.ano + ' (nominal)</span>');
      }
    }
  }

  // Finances
  const fin = g(D, 'secoes.economia.financas_publicas');
  if (fin) {
    document.getElementById('finAno').textContent = fin.ano || '';
    document.getElementById('finAno2').textContent = fin.ano || '';
    document.getElementById('recTotal').textContent = '· total R$ ' + fNum1((fin.receitas ? fin.receitas.total : 0) / 1e9) + ' bi';
    document.getElementById('despTotal').textContent = '· total R$ ' + fNum1((fin.despesas_total_empenhado || 0) / 1e9) + ' bi';

    if (fin.receitas) {
      const r = fin.receitas;
      const recLabels = ['ICMS', 'Outras correntes', 'FPM', 'ISS', 'IPTU', 'Capital'];
      const recData = [
        Math.round((r.icms || 0) / 1e6),
        Math.round(((r.receitas_correntes || 0) - (r.icms || 0) - (r.fpm || 0) - (r.iss || 0) - (r.iptu || 0)) / 1e6),
        Math.round((r.fpm || 0) / 1e6),
        Math.round((r.iss || 0) / 1e6),
        Math.round((r.iptu || 0) / 1e6),
        Math.round((r.receitas_capital || 0) / 1e6),
      ];
      // do maior para o menor
      const recOrd = recLabels.map((k, i) => [k, recData[i]]).sort((a, b) => b[1] - a[1]);
      recOrd.forEach(([k, v], i) => { recLabels[i] = k; recData[i] = v; });
      criaGrafico(document.getElementById('recChart'), {
        type: 'bar', data: { labels: recLabels, datasets: [{ data: recData, backgroundColor: C.s1, maxBarThickness: 16, borderRadius: 4, borderSkipped: 'start' }] },
        options: { ...chartOpts, indexAxis: 'y',
          plugins: { ...noLegend, tooltip: { ...chartOpts.plugins.tooltip, callbacks: { label: ctx => 'R$ ' + fNum(ctx.parsed.x) + ' mi' } } },
          scales: { x: { ticks: { color: C.muted, callback: v => 'R$ ' + fNum(v) + ' mi' }, grid: { color: C.grid } },
                    y: { ticks: { color: C.tick, autoSkip: false, font: { size: 11 } }, grid: { display: false } } } }
      });
    }

    // Despesas chart
    const desps = fin.despesas_funcao || [];
    const despTop = desps.slice(0, 7);
    const despLabels = despTop.map(d => d.funcao);
    const despData = despTop.map(d => Math.round(d.valor / 1e6));
    criaGrafico(document.getElementById('despChart'), {
      type: 'bar', data: { labels: despLabels, datasets: [{ data: despData, backgroundColor: C.s1, maxBarThickness: 16, borderRadius: 4, borderSkipped: 'start' }] },
      options: { ...chartOpts, indexAxis: 'y',
        plugins: { ...noLegend, tooltip: { ...chartOpts.plugins.tooltip, callbacks: { label: ctx => 'R$ ' + fNum(ctx.parsed.x) + ' mi' } } },
        scales: { x: { ticks: { color: C.muted, callback: v => 'R$ ' + fNum(v) + ' mi' }, grid: { color: C.grid } },
                  y: { ticks: { color: C.tick, autoSkip: false, font: { size: 11 } }, grid: { display: false } } } }
    });
  }

  // Banking
  const bc = g(D, 'secoes.economia.bancario');
  if (bc) {
    document.getElementById('bcAno').textContent = (bc.ano || '') + '/' + String(bc.mes || '').padStart(2, '0');
    document.getElementById('bcList').innerHTML =
      '<li><span>Agências</span><span>' + (bc.agencias || 0) + '</span></li>' +
      '<li><span>Depósitos totais</span><span>R$ ' + fNum1((bc.depositos_totais || 0) / 1e9) + ' bi</span></li>' +
      '<li><span>Operações de crédito</span><span>R$ ' + fNum1((bc.operacoes_credito || 0) / 1e9) + ' bi</span></li>';
  }

  // INPC
  const inpc = g(D, 'secoes.economia.inpc_brasil');
  if (inpc) {
    document.getElementById('inpcAno').textContent = (inpc.ano || '') + '/' + String(inpc.mes || '').padStart(2, '0');
    document.getElementById('inpcList').innerHTML =
      '<li><span>Mensal</span><span>' + (inpc.variacao_mensal != null ? (inpc.variacao_mensal > 0 ? '+' : '') + inpc.variacao_mensal.toFixed(2).replace('.', ',') + '%' : '') + '</span></li>' +
      '<li><span>Acumulado 12 meses</span><span>' + (inpc.variacao_doze_meses != null ? inpc.variacao_doze_meses.toFixed(2).replace('.', ',') + '%' : '') + '</span></li>';
  }

  // IDEB overview
  const idebIni = g(D, 'secoes.educacao.ideb.iniciais') || [];
  const idebFin = g(D, 'secoes.educacao.ideb.finais') || [];
  const ideb2023Ini = find(idebIni, 'ano', 2023);
  const ideb2023Fin = find(idebFin, 'ano', 2023);
  const ideb2021Ini = find(idebIni, 'ano', 2021);
  const ideb2021Fin = find(idebFin, 'ano', 2021);

  // As metas do PNE pararam em 2019 (2021 e 2023 vêm nulas) — não afirmar
  // "acima da meta" quando não há meta pactuada; comparar com Brasil e RJ.
  function pintaCartaoIdeb(cardEl, valor, refBrasil) {
    if (!cardEl || valor == null || refBrasil == null) return;
    cardEl.classList.remove('st-good-b', 'st-warn-b', 'st-serious-b');
    cardEl.classList.add(valor >= refBrasil ? 'st-good-b' : (valor >= refBrasil * 0.95 ? 'st-warn-b' : 'st-serious-b'));
  }
  function benchIdeb(id, br, uf, ultimaMeta) {
    document.getElementById(id).innerHTML =
      '<span><b>Brasil:</b> ' + fNum1(br || 0) + '</span>' +
      '<span><b>RJ:</b> ' + fNum1(uf || 0) + '</span>' +
      (ultimaMeta ? '<span><b>Última meta PNE (' + ultimaMeta.ano + '):</b> ' + fNum1(ultimaMeta.meta) + '</span>' : '');
  }
  const ultMetaIni = [...idebIni].reverse().find(d => d.meta != null) || null;
  const ultMetaFin = [...idebFin].reverse().find(d => d.meta != null) || null;
  const brIni = g(D, 'secoes.educacao.ideb.referencia_brasil.iniciais');
  const brFin = g(D, 'secoes.educacao.ideb.referencia_brasil.finais');

  if (ideb2023Ini) {
    document.getElementById('idebAno').textContent = String(ideb2023Ini.ano);
    document.getElementById('idebInitVal').textContent = fNum1(ideb2023Ini.ideb);
    const d2021Ini = ideb2021Ini ? ideb2023Ini.ideb - ideb2021Ini.ideb : 0;
    const elIni = document.getElementById('idebInitDelta');
    elIni.className = 'delta ' + (d2021Ini >= 0 ? 'up' : 'down');
    elIni.innerHTML = (d2021Ini >= 0 ? '▲ +' : '▼ ') + Math.abs(d2021Ini).toFixed(1).replace('.', ',') + ' <span class="vs">vs 2021</span>';
    benchIdeb('idebInitBench', brIni, g(D, 'secoes.educacao.ideb.referencia_uf.iniciais'), ultMetaIni);
    pintaCartaoIdeb(elIni.closest('.card'), ideb2023Ini.ideb, brIni);
  }
  if (ideb2023Fin) {
    document.getElementById('idebAno2').textContent = String(ideb2023Fin.ano);
    document.getElementById('idebFinalVal').textContent = fNum1(ideb2023Fin.ideb);
    const d2021Fin = ideb2021Fin ? ideb2023Fin.ideb - ideb2021Fin.ideb : 0;
    const elFin = document.getElementById('idebFinalDelta');
    elFin.className = 'delta ' + (d2021Fin >= 0 ? 'up' : 'down');
    elFin.innerHTML = (d2021Fin >= 0 ? '▲ +' : '▼ ') + Math.abs(d2021Fin).toFixed(1).replace('.', ',') + ' <span class="vs">vs 2021</span>';
    benchIdeb('idebFinalBench', brFin, g(D, 'secoes.educacao.ideb.referencia_uf.finais'), ultMetaFin);
    pintaCartaoIdeb(elFin.closest('.card'), ideb2023Fin.ideb, brFin);
  }

  // Aprovação
  if (ideb2023Ini && ideb2023Fin) {
    document.getElementById('aproAno').textContent = String(ideb2023Ini.ano);
    document.getElementById('aproVal').innerHTML = fNum1((ideb2023Ini.taxa_aprovacao + ideb2023Fin.taxa_aprovacao) / 2) + ' <span class="unit">%</span>';
  }

  // SAEB
  const saebData = g(D, 'secoes.educacao.saeb');
  if (saebData) {
    document.getElementById('saebAno').textContent = saebData.ano || '';
    document.getElementById('saebAno2').textContent = saebData.ano || '';
    const provaLP5 = (saebData.provas || []).find(p => p.disciplina === 'LP' && p.serie === 5);
    if (provaLP5) {
      document.getElementById('saebPortVal').textContent = fNum1(provaLP5.media);
      document.getElementById('saebBench').innerHTML = '<span>Prova Brasil/SAEB — 5º ano EF</span>';
    }

    // SAEB chart (LP 5º ano)
    if (document.getElementById('saebChart')) {
      const prova = (saebData.provas || []).find(p => p.disciplina === 'LP' && p.serie === 5);
      if (prova && prova.distribuicao_niveis_pct) {
        const n4 = prova.distribuicao_niveis_pct;
        // Aggregate into 4 levels
        const agg = [0, 0, 0, 0];
        const step = Math.ceil(n4.length / 4);
        n4.forEach((v, i) => { const idx = Math.min(Math.floor(i / step), 3); agg[idx] += v; });
        criaGrafico(document.getElementById('saebChart'), {
          type: 'bar', data: {
            labels: ['Nível 0', 'Nível 1', 'Nível 2', 'Nível 3'],
            datasets: [{ data: agg, backgroundColor: ordinal4, maxBarThickness: 24, borderRadius: 4, borderSkipped: 'start' }]
          },
          options: { ...chartOpts, plugins: { ...noLegend, tooltip: { ...chartOpts.plugins.tooltip,
            callbacks: { label: ctx => ctx.parsed.y.toFixed(1).replace('.', ',') + '% dos alunos' } } },
            scales: { x: { ticks: { color: C.muted }, grid: { display: false } },
                      y: { ticks: { color: C.muted, callback: v => v + '%' }, grid: { color: C.grid } } } }
        });
      }
    }
  }

  // IDEB evolution chart
  if (document.getElementById('idebChart')) {
    const iniYears = idebIni.map(d => String(d.ano));
    const iniData = idebIni.map(d => d.ideb);
    const finData = idebFin.map(d => d.ideb);
    const iniMeta = idebIni.map(d => d.meta);
    const finMeta = idebFin.map(d => d.meta);
    const lastIni = ideb2023Ini;
    const lastFin = ideb2023Fin;
    // As metas pactuadas do PNE só existem até 2019 — dizer isso em vez de exibir "—"
    document.getElementById('idebMetasSub').textContent = lastIni && lastFin
      ? (ultMetaIni
          ? 'O INEP não pactuou meta para ' + lastIni.ano + ' — a última foi a de ' + ultMetaIni.ano +
            ' (iniciais ' + fNum1(ultMetaIni.meta) + (ultMetaFin ? ', finais ' + fNum1(ultMetaFin.meta) : '') + '). '
          : '') +
        'Em ' + lastIni.ano + ': iniciais ' + fNum1(lastIni.ideb) + ' (Brasil ' + fNum1(brIni || 0) + ') · finais ' +
        fNum1(lastFin.ideb) + ' (Brasil ' + fNum1(brFin || 0) + ').'
      : '';
    criaGrafico(document.getElementById('idebChart'), {
      type: 'line', data: {
        labels: iniYears,
        datasets: [
          { label: 'Anos iniciais', data: iniData, borderColor: C.s1, backgroundColor: C.s1fill, fill: true, pointBackgroundColor: C.s1, ...lineStyle, pointRadius: 3 },
          { label: 'Anos finais', data: finData, borderColor: C.s2, backgroundColor: C.s2fill, fill: true, pointBackgroundColor: C.s2, ...lineStyle, pointRadius: 3 },
        ]
      },
      options: { ...chartOpts, scales: { ...chartOpts.scales,
        y: { min: 2.5, max: 6.5, ticks: { color: C.muted }, grid: { color: C.grid } } } }
    });
  }

  // Alfabetização
  const alf = g(D, 'secoes.demografia.censo_2022.taxa_alfabetizacao');
  if (alf != null) {
    document.getElementById('alfAno').textContent = '2022';
    const pctAlf = (alf * 100).toFixed(1);
    document.getElementById('alfPctVal').textContent = pctAlf.replace('.', ',') + '%';
    document.getElementById('alfMeter').style.width = pctAlf + '%';
  }

  // ENEM
  const enem = g(D, 'secoes.educacao.enem');
  if (enem) {
    document.getElementById('enemAno').textContent = enem.ano || '';
    document.getElementById('enemList').innerHTML =
      '<li><span>Inscritos</span><span>' + fNum(enem.inscritos || 0) + '</span></li>' +
      '<li><span>Presentes</span><span>' + fNum(enem.presentes || 0) + '</span></li>' +
      '<li><span>Média geral</span><span>' + fNum1(enem.media_geral || 0) + '</span></li>' +
      '<li><span>Redação</span><span>' + fNum1(enem.redacao || 0) + '</span></li>';
    document.getElementById('enemDetList').innerHTML =
      '<li><span>Linguagens</span><span>' + fNum1(enem.linguagens || 0) + '</span></li>' +
      '<li><span>Matemática</span><span>' + fNum1(enem.matematica || 0) + '</span></li>' +
      '<li><span>Ciências Humanas</span><span>' + fNum1(enem.humanas || 0) + '</span></li>' +
      '<li><span>Ciências da Natureza</span><span>' + fNum1(enem.natureza || 0) + '</span></li>';
  }

  // CNES
  const cnes = g(D, 'secoes.saude.cnes');
  if (cnes) {
    const comp = cnes.competencia || '';
    document.getElementById('cnesAno').textContent = comp.slice(0, 4);
    document.getElementById('cnesAno2').textContent = cnes.leitos ? cnes.leitos.competencia.slice(0, 4) : comp.slice(0, 4);
    document.getElementById('cnesAno3').textContent = cnes.profissionais ? cnes.profissionais.competencia.slice(0, 4) : comp.slice(0, 4);
    document.getElementById('cnesAno4').textContent = cnes.equipes ? cnes.equipes.competencia.slice(0, 4) : comp.slice(0, 4);
    document.getElementById('cnesEstab').textContent = fNum(cnes.estabelecimentos || 0);
    const leitos = cnes.leitos ? cnes.leitos.total : 0;
    document.getElementById('cnesLeitos').textContent = fNum(leitos);
    document.getElementById('cnesLeitosBench').innerHTML = '<span>' + (leitos && pop2024 ? (leitos / pop2024 * 1000).toFixed(1).replace('.', ',') : '') + '/1.000 hab</span>';
    document.getElementById('cnesProf').textContent = fNum(cnes.profissionais ? cnes.profissionais.vinculos : 0);
    document.getElementById('cnesEquip').textContent = cnes.equipes ? cnes.equipes.total : 0;
  }

  // Nascidos vivos
  const nasc = g(D, 'secoes.saude.nascidos_vivos');
  if (nasc) {
    document.getElementById('nasciAno').textContent = nasc.ano || '';
    document.getElementById('nasciList').innerHTML =
      '<li><span>Total</span><span>' + fNum(nasc.nascidos_vivos || 0) + '</span></li>' +
      '<li><span>Partos cesáreos</span><span>' + fNum1(nasc.pct_cesareo || 0) + '%</span></li>' +
      '<li><span>Baixo peso ao nascer</span><span>' + fNum1(nasc.pct_baixo_peso || 0) + '%</span></li>';
  }

  // Dengue
  const dengue = g(D, 'secoes.saude.dengue');
  if (dengue) {
    document.getElementById('dengueAno').textContent = dengue.ano || '';
    document.getElementById('dengueList').innerHTML =
      '<li><span>Casos notificados</span><span>' + fNum(dengue.notificados || 0) + '</span></li>' +
      '<li><span>Casos confirmados</span><span>' + fNum(dengue.confirmados || 0) + '</span></li>' +
      '<li><span>Casos graves / óbitos</span><span>' + (dengue.graves || 0) + ' / ' + (dengue.obitos || 0) + '</span></li>';
    const ant = dengue.notificados_ano_anterior;
    if (ant) {
      const delta = ((dengue.notificados || 0) / ant - 1) * 100;
      document.getElementById('dengueDelta').innerHTML =
        (delta < 0 ? '▼ ' : '▲ ') + Math.abs(delta).toFixed(0) + '% notificações <span class="vs">vs ' + ((dengue.ano || 1) - 1) + '</span>';
    }
  }

  // Segurança
  // O FBSP aparece no cabeçalho como fonte; quando o município fica fora da amostra do
  // anuário, dizer isso é melhor do que deixar a fonte citada sem nenhum número atrás
  const fbsp = g(D, 'secoes.seguranca.fbsp');
  setTxt('fbspNota', fbsp && fbsp.disponivel === false
    ? 'Anuário FBSP: ' + (fbsp.motivo || 'sem dado para este município') + ' — os números abaixo vêm do ISP/RJ.'
    : '');

  const seg = g(D, 'secoes.seguranca.isp_rj');
  if (seg) {
    const oco = seg.ocorrencias || {};
    const ano = seg.ano || '';
    document.getElementById('segAno').textContent = ano;
    document.getElementById('segAno2').textContent = ano;
    document.getElementById('segAno3').textContent = ano;
    document.getElementById('segAno4').textContent = ano;
    document.getElementById('segAno5').textContent = ano;
    document.getElementById('segAno6').textContent = ano;
    document.getElementById('segAno7').textContent = ano;
    document.getElementById('segAno8').textContent = ano;
    document.getElementById('segAno9').textContent = ano;
    document.getElementById('segAno10').textContent = ano;

    document.getElementById('segHomicidios').textContent = oco.homicidio_doloso || 0;
    const antHom = seg.homicidio_doloso_ano_anterior;
    if (antHom) {
      const homDelta = antHom > 0 ? Math.round((oco.homicidio_doloso - antHom) / antHom * 100) : 0;
      // Alta de homicídio é ruim — a cor acompanha o sinal, não fica fixa em verde
      document.getElementById('segHomicDelta').className = 'delta ' + (homDelta <= 0 ? 'down-good' : 'up-bad');
      document.getElementById('segHomicDelta').innerHTML = (homDelta <= 0 ? '▼ ' : '▲ ') + Math.abs(homDelta) + '% <span class="vs">vs ' + (ano - 1) + '</span>';
    }

    // Taxas
    const tx = seg.taxas_100k || {};
    const txUf = seg.taxas_100k_uf || {};
    document.getElementById('segHomicBench').innerHTML = '<span>' + (tx.taxa_homicidio_doloso ? fNum1(tx.taxa_homicidio_doloso) : '') + '/100k · <b>RJ:</b> ' + fNum1(txUf.taxa_homicidio_doloso || 0) + '</span>';
    document.getElementById('segLetal').textContent = oco.letalidade_violenta || 0;
    document.getElementById('segLetalBench').innerHTML = '<span>' + (tx.taxa_letalidade_violenta ? fNum1(tx.taxa_letalidade_violenta) : '') + '/100k · <b>RJ:</b> ' + fNum1(txUf.taxa_letalidade_violenta || 0) + '</span>';
    document.getElementById('segEstupro').textContent = oco.estupro || 0;
    document.getElementById('segInterv').textContent = oco.intervencao_policial || 0;
    document.getElementById('segRoubo').textContent = oco.roubo_veiculo || 0;
    document.getElementById('segRouboBench').innerHTML = '<span>' + (tx.taxa_roubo_veiculo ? fNum1(tx.taxa_roubo_veiculo) : '') + '/100k · <b>RJ:</b> ' + fNum1(txUf.taxa_roubo_veiculo || 0) + '/100k</span>';
    document.getElementById('segTentativa').textContent = oco.tentativa_homicidio || 0;
    document.getElementById('segLatroc').textContent = oco.latrocinio || 0;
    document.getElementById('segCvli').textContent = oco.cvli || 0;

    // Taxas — barra agrupada município × RJ (mesma unidade, comparação direta)
    const taxaLinhas = [
      ['Homicídio doloso', 'taxa_homicidio_doloso'],
      ['Letalidade violenta', 'taxa_letalidade_violenta'],
      ['Tentativa de homicídio', 'taxa_tentativa_homicidio'],
      ['Estupro', 'taxa_estupro'],
      ['Latrocínio', 'taxa_latrocinio'],
    ].filter(([, k]) => tx[k] != null || txUf[k] != null);
    if (taxaLinhas.length) {
      criaGrafico(el_('taxasChart'), {
        type: 'bar', data: {
          labels: taxaLinhas.map(l => l[0]),
          datasets: [
            { label: 'Município', data: taxaLinhas.map(([, k]) => tx[k]), backgroundColor: C.s1, maxBarThickness: 12, borderRadius: 3, borderSkipped: 'start' },
            { label: 'Estado do RJ', data: taxaLinhas.map(([, k]) => txUf[k]), backgroundColor: C.s6, maxBarThickness: 12, borderRadius: 3, borderSkipped: 'start' },
          ]
        },
        options: { ...chartOpts, indexAxis: 'y',
          plugins: { ...chartOpts.plugins,
            legend: { position: 'bottom', labels: { color: C.tick, usePointStyle: true, pointStyle: 'circle', padding: 8, boxWidth: 8, font: { size: 10 } } },
            tooltip: { ...chartOpts.plugins.tooltip,
              callbacks: { label: ctx => ctx.parsed.x == null
                ? ctx.dataset.label + ': sem taxa publicada'
                : ctx.dataset.label + ': ' + fNum1(ctx.parsed.x) + '/100 mil hab' } } },
          scales: { x: { beginAtZero: true, ticks: { color: C.muted, callback: v => fNum1(v) }, grid: { color: C.grid } },
                    y: { ticks: { color: C.tick, autoSkip: false, font: { size: 10 } }, grid: { display: false } } } }
      });
    } else { vazioGrafico('taxasChart'); }

    // Crime chart
    if (document.getElementById('crimeChart') && seg.mensal) {
      const months = ['Jan', 'Fev', 'Mar', 'Abr', 'Mai', 'Jun', 'Jul', 'Ago', 'Set', 'Out', 'Nov', 'Dez'];
      const crimeData = months.map((_, i) => {
        const m = seg.mensal.find(d => d.mes === i + 1);
        return m ? m.homicidio_doloso : 0;
      });
      criaGrafico(document.getElementById('crimeChart'), {
        type: 'line', data: {
          labels: months,
          datasets: [{ label: 'Homicídio doloso', data: crimeData, borderColor: C.s1, backgroundColor: C.s1fill, fill: true, pointBackgroundColor: C.s1, ...lineStyle }]
        },
        options: { ...chartOpts, plugins: noLegend,
          scales: { x: { ticks: { color: C.muted }, grid: { color: C.grid } },
                    y: { min: 0, max: Math.max(4, ...crimeData), ticks: { color: C.muted, stepSize: 1 }, grid: { color: C.grid } } } }
      });
    } else { vazioGrafico('crimeChart'); }
  } else {
    // O ISP só publica estatística do Rio de Janeiro — fora do RJ a seção fica sem fonte
    const foraRj = (g(D, 'municipio.sigla_uf') || '') !== 'RJ';
    const msgSeg = foraRj
      ? 'O ISP publica estatística só para municípios do Rio de Janeiro'
      : SEM_DADO;
    vazioValores('segHomicidios', 'segLetal', 'segEstupro', 'segInterv',
      'segRoubo', 'segTentativa', 'segLatroc', 'segCvli');
    vazioGrafico('crimeChart', msgSeg); vazioGrafico('taxasChart', msgSeg);
    setTxt('taxasNota', '');
  }

  // Conectividade
  document.getElementById('blAno').textContent = (g(D, 'secoes.conectividade.banda_larga.competencia') || '').slice(0, 4);
  document.getElementById('blVal').innerHTML = fNum1(g(D, 'secoes.conectividade.banda_larga.densidade_100hab') || 0) + ' <span class="unit">/100 hab</span>';
  document.getElementById('ibcAno2').textContent = g(D, 'secoes.conectividade.ibc.ano') || '';
  document.getElementById('ibcVal2').textContent = fNum1(g(D, 'secoes.conectividade.ibc.ibc') || 0);
  document.getElementById('covAno').textContent = g(D, 'secoes.conectividade.ibc.ano') || '';
  document.getElementById('covVal').innerHTML = fNum1(g(D, 'secoes.conectividade.ibc.cobertura_pop_4g5g') || 0) + ' <span class="unit">%</span>';
  document.getElementById('fibraAno').textContent = g(D, 'secoes.conectividade.ibc.ano') || '';
  // O `||` liga mais frouxo que o `+`: sem os parênteses o valor real saía sem a unidade
  const fibraPct = g(D, 'secoes.conectividade.ibc.fibra');
  if (fibraPct != null) setHtml('fibraVal', fNum1(fibraPct) + ' <span class="unit">%</span>');
  else vazioValor('fibraVal');

  // Política
  const pol = g(D, 'secoes.politica');
  if (pol) {
    const anoPol = pol.ano || '';
    document.getElementById('polAno').textContent = anoPol;
    document.getElementById('polAno2').textContent = anoPol;
    document.getElementById('polAno3').textContent = pol.ano_prefeito || anoPol;

    const eleit = pol.eleitorado || {};
    document.getElementById('polEleitList').innerHTML =
      '<li><span>Eleitores aptos</span><span>' + fNum(eleit.aptos || 0) + '</span></li>' +
      '<li><span>Biometria coletada</span><span>' + (eleit.aptos ? (eleit.biometria / eleit.aptos * 100).toFixed(1).replace('.', ',') + '%' : '—') + '</span></li>' +
      '<li><span>Zonas eleitorais</span><span>' + (eleit.zonas || 0) + '</span></li>';

    // Códigos TSE: genero 2 = feminino, 4 = masculino
    const gen = pol.genero || {};
    const totalGen = (gen['2'] || 0) + (gen['4'] || 0);
    document.getElementById('polPerfilList').innerHTML =
      '<li><span>Feminino</span><span>' + (totalGen > 0 ? ((gen['2'] || 0) / totalGen * 100).toFixed(1).replace('.', ',') + '%' : '—') + '</span></li>' +
      '<li><span>Masculino</span><span>' + (totalGen > 0 ? ((gen['4'] || 0) / totalGen * 100).toFixed(1).replace('.', ',') + '%' : '—') + '</span></li>';

    // Grau de instrução do eleitorado — códigos do dicionário do TSE
    // (br_tse_eleicoes.dicionario, coluna `instrucao`). É escala ordinal:
    // a ordem é a do grau, nunca a do volume; "não informado" fecha a lista.
    const INSTRUCAO_TSE = [
      ['1', 'Analfabeto'], ['2', 'Lê e escreve'],
      ['3', 'Fundamental incompleto'], ['4', 'Fundamental completo'],
      ['5', 'Médio incompleto'], ['6', 'Médio completo'],
      ['7', 'Superior incompleto'], ['8', 'Superior completo'],
      ['0', 'Não informado'],
    ];
    const ins = pol.instrucao || {};
    const totalIns = Object.values(ins).reduce((s, n) => s + (Number(n) || 0), 0);
    const linhasIns = INSTRUCAO_TSE
      .filter(([c]) => ins[c] != null)
      .map(([c, rot]) => ({ k: rot, v: ins[c] }))
      .sort((a, b) => b.v - a.v);
    barrasCategoria('polInstrucaoBars', linhasIns, totalIns, C.s1, { soPct: true });

    const pref = pol.prefeito || {};
    const eletPref = g(D, 'secoes.politica.eleitorado');
    const eleito = pref.eleito || {};
    document.getElementById('polResultList').innerHTML =
      '<li><span>Votos nominais</span><span>' + fNum(pref.votos_nominais || 0) + '</span></li>' +
      '<li><span>Brancos + nulos</span><span>' + fNum((pref.votos_brancos || 0) + (pref.votos_nulos || 0)) + '</span></li>' +
      '<li><span>Abstenção</span><span>' + (pref.aptos ? (pref.abstencoes / pref.aptos * 100).toFixed(1).replace('.', ',') + '%' : '') + '</span></li>' +
      '<li><span>Vencedor (1º turno)</span><span>' + (eleito.nome_urna || '') + ' · ' + (eleito.partido || '') + '</span></li>';
  }

  // Transparência
  const ebt = g(D, 'secoes.transparencia.ebt') || [];
  const ebtUlt = ebt.length > 0 ? ebt[ebt.length - 1] : null;
  if (ebtUlt) {
    document.getElementById('ebtAno').textContent = ebtUlt.ano || '';
    document.getElementById('ebtVal').textContent = fNum1(ebtUlt.nota || 0);
    document.getElementById('ebtMeter').querySelector('.meter-fill').style.width = ((ebtUlt.nota || 0) * 10) + '%';
    // A nota estava sempre pintada de verde. Sem média nacional no JSON, a faixa
    // sai da própria escala 0–10 da CGU e o ranking do ano vai na legenda.
    const cardEbt = document.getElementById('ebtVal').closest('.card');
    const nota = ebtUlt.nota || 0;
    cardEbt.classList.remove('st-good-b', 'st-warn-b', 'st-serious-b');
    cardEbt.classList.add(nota >= 8 ? 'st-good-b' : (nota >= 5 ? 'st-warn-b' : 'st-serious-b'));
    setTxt('ebtRank', ebtUlt.ranking ? ebtUlt.ranking + 'º no ranking CGU' : '');
  }

  const clp = g(D, 'secoes.transparencia.clp');
  if (clp) {
    document.getElementById('clpAno').textContent = clp.ano || '';
    const pilares = clp.pilares || [];
    const geral = pilares.find(p => p.pilar_dimensao === 'Ranking Geral');
    const inst = pilares.find(p => p.pilar_dimensao === 'Dimensão: Instituições');
    const capital = pilares.find(p => p.pilar_dimensao === 'Capital humano');
    document.getElementById('clpList').innerHTML =
      '<li><span>Colocação nacional</span><span>' + (geral ? geral.colocacao + 'º' : '') + '</span></li>' +
      '<li><span>Nota geral</span><span>' + (geral ? fNum1(geral.nota_geral) : '') + '</span></li>' +
      '<li><span>Pilar: instituições</span><span>' + (inst ? fNum1(inst.nota_geral) : '') + '</span></li>' +
      '<li><span>Pilar: capital humano</span><span>' + (capital ? fNum1(capital.nota_geral) : '') + '</span></li>';
  }

  // Social / IVS
  const avs = g(D, 'secoes.social.avs');
  if (avs) {
    // IVS e IDHM são índices ancorados em 0 e 1 — a barra pode ser lida no absoluto,
    // então a escala é fixa em 1 e não no maior valor da própria lista.
    const idx3 = v => v.toFixed(3).replace('.', ',');
    const linhasIvs = [
      ['IVS geral', avs.ivs], ['Infraestrutura urbana', avs.ivs_infraestrutura_urbana],
      ['Capital humano', avs.ivs_capital_humano], ['Renda e trabalho', avs.ivs_renda_trabalho],
    ].filter(r => r[1] != null).map(r => ({ k: r[0], v: r[1] }));
    barrasCategoria('ivsBars', linhasIvs, 0, C.s6, { escalaMax: 1, fmtValor: idx3 });
    document.getElementById('idhmVal').textContent = avs.idhm != null ? avs.idhm.toFixed(3).replace('.', ',') : '';
    document.getElementById('idhmVal2').textContent = avs.idhm != null ? avs.idhm.toFixed(3).replace('.', ',') : '';
    const linhasIdhm = [
      ['Longevidade', avs.idhm_longevidade], ['Renda', avs.idhm_renda], ['Educação', avs.idhm_educacao],
    ].filter(r => r[1] != null).map(r => ({ k: r[0], v: r[1] }));
    barrasCategoria('idhmCompBars', linhasIdhm, 0, C.s5, { escalaMax: 1, fmtValor: idx3 });
  } else {
    barrasCategoria('ivsBars', [], 0); barrasCategoria('idhmCompBars', [], 0);
    vazioValores('idhmVal', 'idhmVal2');
  }

  // Primeira infância
  const pi = g(D, 'secoes.social.primeira_infancia');
  if (pi) {
    document.getElementById('piAno').textContent = pi.ano || '';
    document.getElementById('piList').innerHTML =
      '<li><span>Taxa bruta pré-escola</span><span>' + fNum1(pi.taxa_bruta_pre_escola || 0) + '%</span></li>' +
      '<li><span>Taxa líquida pré-escola</span><span>' + fNum1(pi.taxa_liquida_pre_escola || 0) + '%</span></li>' +
      '<li><span>Matrículas</span><span>' + fNum(pi.matriculas_pre_escola || 0) + '</span></li>';
  }

  // Bolsa Família
  const bf = g(D, 'secoes.beneficios.bolsa_familia');
  if (bf) {
    document.getElementById('bfAno').textContent = (bf.competencia || '').slice(0, 4);
    document.getElementById('bfAno2').textContent = (bf.competencia || '').slice(0, 4);
    document.getElementById('bfAno3').textContent = (bf.competencia || '').slice(0, 4);
    document.getElementById('bfFamilias').innerHTML = fNum(bf.familias || 0) + ' <span class="unit">famílias</span>';
    document.getElementById('bfValMed').innerHTML = 'R$ ' + Math.round(bf.valor_medio || 0).toLocaleString('pt-BR') + ' <span class="unit">/família·mês</span>';
    document.getElementById('bfRepasse').innerHTML = 'R$ ' + fNum1((bf.repasse_mensal || 0) / 1e6) + ' <span class="unit">mi</span>';
    const dom = g(D, 'secoes.demografia.censo_2022.domicilios') || 1;
    document.getElementById('bfBench').innerHTML = (bf.familias / dom * 100).toFixed(1).replace('.', ',') + '% dos domicílios';
  }

  // BPC
  const bpc = g(D, 'secoes.beneficios.bpc');
  if (bpc) {
    document.getElementById('bpcAno').textContent = g(D, 'secoes.beneficios.bolsa_familia.competencia', '').slice(0, 4) || '';
    document.getElementById('bpcVal').textContent = fNum(bpc.beneficiarios || 0);
  }

  // RAIS
  const rais = g(D, 'secoes.trabalho.rais');
  if (rais) {
    document.getElementById('raisAno').textContent = rais.ano || '';
    document.getElementById('raisAno2').textContent = rais.ano || '';
    document.getElementById('raisAno3').textContent = rais.ano || '';
    document.getElementById('raisVinculos').textContent = fNum(rais.vinculos_ativos_3112 || 0);
    const antRais = rais.vinculos_ativos_ano_anterior;
    if (antRais) {
      const dRais = (rais.vinculos_ativos_3112 - antRais) / antRais * 100;
      setCls('raisDelta', 'delta ' + (dRais >= 0 ? 'up' : 'down'));
      setHtml('raisDelta', (dRais >= 0 ? '▲ +' : '▼ −') + Math.abs(dRais).toFixed(1).replace('.', ',') +
        '% <span class="vs">vs ' + (rais.ano - 1) + '</span>');
    }
    document.getElementById('raisEstab').textContent = fNum(rais.estabelecimentos || 0);
    document.getElementById('raisSalMed').innerHTML = 'R$ ' + fNum(Math.round(rais.remuneracao_media || 0));
    setHtml('raisBench', '<span>' + Math.round((rais.vinculos_ativos_3112 || 0) / pop2024 * 100) +
      '% da população</span>');
  } else {
    vazioValores('raisVinculos', 'raisEstab', 'raisSalMed');
  }

  // CAGED
  const caged = g(D, 'secoes.trabalho.caged');
  if (caged) {
    document.getElementById('cagedAno').textContent = caged.ano || '';
    document.getElementById('cagedSaldo').textContent = (caged.saldo > 0 ? '+' : '') + fNum(caged.saldo || 0);
    document.getElementById('cagedDetSub').textContent = fNum(caged.admissoes || 0) + ' admissões − ' + fNum(caged.desligamentos || 0) + ' desligamentos';
  }

  // Maiores empregadores — linha de tabela
  const rowEmpregRank = (e, i, fallbackName, tagField) => {
    const nome = e.empresa || fallbackName;
    const val = e.vinculos_ativos || 0;
    const tag = e[tagField] || '';
    // A RAIS grava razão social e setor em CAIXA ALTA; as tabelas vizinhas
    // (emendas, fornecedores) já usam titulo(), então aqui também
    return '<tr>' +
      '<td class="rank-name" title="' + nome + '"><span class="rk-num">' + (i + 1) + '.</span><b>' + titulo(nome) + '</b></td>' +
      '<td class="area" title="' + tag + '">' + titulo(tag).replace('; Reparação de Veículos Automotores e Motocicletas', '') + '</td>' +
      '<td class="valor" data-label="Vínculos ativos"><span class="val">' + fNum(val) + '</span></td>' +
      '</tr>';
  };

  // Maiores empregadores privados
  const empreg = g(D, 'secoes.trabalho.top_empregadores');
  const empregTop = (empreg && empreg.top) || [];
  if (empregTop.length) {
    document.getElementById('empregAno').textContent = empreg.ano || '';
    const rowEmpreg = (e, i) => rowEmpregRank(e, i, 'empresa não informada', 'setor');
    document.getElementById('empregList').innerHTML = empregTop.slice(0, 5).map(rowEmpreg).join('');
    document.getElementById('empregDetList').innerHTML = empregTop.slice(5).map((e, i) => rowEmpregRank(e, i + 5, 'empresa não informada', 'setor')).join('');
  } else { vazioTabela('empregList', 3); vazioTabela('empregDetList', 3); }

  // Maiores empregadores públicos
  const empregPub = g(D, 'secoes.trabalho.top_empregadores_publicos');
  const empregPubTop = (empregPub && empregPub.top) || [];
  if (empregPubTop.length) {
    document.getElementById('empregPubAno').textContent = empregPub.ano || '';
    document.getElementById('empregPubList').innerHTML = empregPubTop.map((e, i) => rowEmpregRank(e, i, 'órgão não informado', 'natureza')).join('');
  } else { vazioTabela('empregPubList', 3); }

  // Comex
  const exp = g(D, 'secoes.comercio_exterior.exportacoes');
  const imp = g(D, 'secoes.comercio_exterior.importacoes');
  if (exp && imp) {
    const anoComex = exp.ano || '';
    document.getElementById('comexAno').textContent = anoComex;
    document.getElementById('comexAno2').textContent = anoComex;
    document.getElementById('comexAno3').textContent = anoComex;
    document.getElementById('comexAno4').textContent = anoComex;
    document.getElementById('comexAno5').textContent = anoComex;
    document.getElementById('comexAno6').textContent = anoComex;

    const expVal = Number(exp.total_fob_usd || 0);
    const impVal = Number(imp.total_fob_usd || 0);
    document.getElementById('expVal').innerHTML = 'US$ ' + fNum1(expVal / 1e6) + ' <span class="unit">mi</span>';
    document.getElementById('impVal').innerHTML = 'US$ ' + fNum1(impVal / 1e6) + ' <span class="unit">mi</span>';
    const bal = expVal - impVal;
    document.getElementById('balancaVal').innerHTML = (bal < 0 ? '−' : '') + 'US$ ' + fNum1(Math.abs(bal) / 1e6) + ' <span class="unit">mi</span>';

    // A seta e a cor vinham fixas em "▲ +": com queda saía "▲ +-22,7%" em verde.
    // `bomSeSobe` separa exportação (subir é bom) de importação (subir pesa na balança).
    const deltaComex = (id, atual, anterior, bomSeSobe) => {
      if (!anterior) { setTxt(id, ''); return; }
      const d = (atual / anterior - 1) * 100;
      const sobe = d >= 0;
      setCls(id, 'delta ' + (sobe ? (bomSeSobe ? 'up' : 'up-bad') : (bomSeSobe ? 'down' : 'down-good')));
      setHtml(id, (sobe ? '▲ +' : '▼ −') + Math.abs(d).toFixed(1).replace('.', ',') +
        '% <span class="vs">vs ' + (anoComex - 1) + '</span>');
    };
    deltaComex('expDelta', expVal, Number(exp.ano_anterior_fob_usd || 0), true);
    deltaComex('impDelta', impVal, Number(imp.ano_anterior_fob_usd || 0), false);

    const deficit = bal < 0;
    pill('stComex', deficit ? 'st-warn' : 'st-good', deficit ? '! déficit' : '✓ superávit');
    const cardBal = el_('balancaVal').closest('.card');
    cardBal.classList.remove('st-warn-b', 'st-good-b');
    cardBal.classList.add(deficit ? 'st-warn-b' : 'st-good-b');
    setTxt('balancaSub', (deficit ? 'Importa mais do que exporta' : 'Exporta mais do que importa') +
      ' · US$ ' + fNum1(Math.abs(bal) / 1e6) + ' mi de diferença em ' + anoComex);

    // Export destinations — a fonte guarda ISO3; o código sozinho não diz nada a quem lê.
    // Só os parceiros frequentes do Brasil estão mapeados; o resto cai no próprio código.
    const PAIS_ISO3 = {
      ARG: 'Argentina', BOL: 'Bolívia', CHL: 'Chile', COL: 'Colômbia', PRY: 'Paraguai',
      PER: 'Peru', URY: 'Uruguai', VEN: 'Venezuela', MEX: 'México', USA: 'Estados Unidos',
      CAN: 'Canadá', DEU: 'Alemanha', ESP: 'Espanha', FRA: 'França', GBR: 'Reino Unido',
      ITA: 'Itália', NLD: 'Países Baixos', PRT: 'Portugal', BEL: 'Bélgica', CHE: 'Suíça',
      RUS: 'Rússia', CHN: 'China', JPN: 'Japão', KOR: 'Coreia do Sul', IND: 'Índia',
      IDN: 'Indonésia', VNM: 'Vietnã', THA: 'Tailândia', TUR: 'Turquia', ARE: 'Emirados Árabes',
      SAU: 'Arábia Saudita', ZAF: 'África do Sul', AUS: 'Austrália', NGA: 'Nigéria',
      EGY: 'Egito', MAR: 'Marrocos', ISR: 'Israel', TWN: 'Taiwan', HKG: 'Hong Kong', SGP: 'Singapura',
    };
    const nomePais = c => PAIS_ISO3[c] || c;
    const destinos = exp.top_paises || [];
    setHtml('comexDestList', destinos.length
      ? destinos.slice(0, 6).map(d => liRow(nomePais(d.pais_iso3) +
          (PAIS_ISO3[d.pais_iso3] ? ' <span style="color:var(--text3)">' + d.pais_iso3 + '</span>' : ''),
          'US$ ' + fNum1(Number(d.valor_fob_usd) / 1e6) + ' mi')).join('')
      : '');
    if (!destinos.length) vazioLista('comexDestList');

    // Export/Import charts
    const sh4ToLabel = { '8301': 'Metais', '6212': 'Vestuário', '2208': 'Bebidas', '2403': 'Tabaco', '8302': 'Fechaduras', '6108': 'Vestuário', '2204': 'Vinhos', '1101': 'Cereais', '3006': 'Farmac.', '3005': 'Farmac.' };
    const topExp = (exp.top_sh4 || []).slice(0, 4);
    const topImp = (imp.top_sh4 || []).slice(0, 4);
    if (topExp.length) {
      criaGrafico(document.getElementById('expChart'), {
        type: 'bar', data: {
          labels: topExp.map(d => sh4ToLabel[d.id_sh4] || ('SH4 ' + d.id_sh4)),
          datasets: [{ data: topExp.map(d => Number(d.valor_fob_usd) / 1e6), backgroundColor: C.s1, maxBarThickness: 16, borderRadius: 4, borderSkipped: 'start' }]
        },
        options: { ...chartOpts, indexAxis: 'y', plugins: { ...noLegend, tooltip: { ...chartOpts.plugins.tooltip,
          callbacks: { label: ctx => 'US$ ' + fNum1(ctx.parsed.x) + ' mi' } } },
          scales: { x: { ticks: { color: C.muted, callback: v => 'US$ ' + fNum1(v) + ' mi' }, grid: { color: C.grid } },
                    y: { ticks: { color: C.tick, font: { size: 11 } }, grid: { display: false } } } }
      });
    } else { vazioGrafico('expChart'); }
    if (topImp.length) {
      criaGrafico(document.getElementById('impChart'), {
        type: 'bar', data: {
          labels: topImp.map(d => sh4ToLabel[d.id_sh4] || ('SH4 ' + d.id_sh4)),
          datasets: [{ data: topImp.map(d => Number(d.valor_fob_usd) / 1e6), backgroundColor: C.s2, maxBarThickness: 16, borderRadius: 4, borderSkipped: 'start' }]
        },
        options: { ...chartOpts, indexAxis: 'y', plugins: { ...noLegend, tooltip: { ...chartOpts.plugins.tooltip,
          callbacks: { label: ctx => 'US$ ' + fNum1(ctx.parsed.x) + ' mi' } } },
          scales: { x: { ticks: { color: C.muted, callback: v => 'US$ ' + fNum1(v) + ' mi' }, grid: { color: C.grid } },
                    y: { ticks: { color: C.tick, font: { size: 11 } }, grid: { display: false } } } }
      });
    } else { vazioGrafico('impChart'); }
  } else {
    vazioValores('expVal', 'impVal', 'balancaVal');
    setTxt('balancaSub', ''); pill('stComex', null);
    vazioGrafico('expChart'); vazioGrafico('impChart'); vazioLista('comexDestList');
  }

  // Agro
  const lavouras = g(D, 'secoes.agropecuaria.lavouras_top') || [];
  if (lavouras.length) {
    const anoAgro = lavouras[0].ano || '';
    document.getElementById('pamAno').textContent = anoAgro;
    const totalVal = lavouras.reduce((s, l) => s + (l.valor_producao || 0), 0);
    const top3 = lavouras.slice(0, 3);
    const rest = lavouras.slice(3);
    document.getElementById('pamList').innerHTML =
      '<li><span>Valor total da produção</span><span>R$ ' + fNum1(totalVal / 1e3) + ' mi</span></li>' +
      top3.map(l => '<li><span>' + l.produto + '</span><span>' + fNum(l.area_colhida || 0) + ' ha · ' + fNum(l.quantidade_produzida || 0) + ' t</span></li>').join('');
    document.getElementById('pamDetList').innerHTML = rest.map(l =>
      '<li><span>' + l.produto + '</span><span>' + fNum(l.area_colhida || 0) + ' ha · ' + fNum(l.quantidade_produzida || 0) + ' t</span></li>'
    ).join('');
  }

  const rebanhos = g(D, 'secoes.agropecuaria.rebanhos') || {};
  const efetivos = rebanhos.efetivos || [];
  if (efetivos.length) {
    document.getElementById('ppmAno').textContent = rebanhos.ano || '';
    const top3Reb = efetivos.slice(0, 3);
    const restReb = efetivos.slice(3);
    document.getElementById('ppmList').innerHTML = top3Reb.map(r =>
      '<li><span>' + r.tipo_rebanho + '</span><span>' + fNum(r.quantidade || 0) + ' cab.</span></li>'
    ).join('');
    document.getElementById('ppmDetList').innerHTML = restReb.map(r =>
      '<li><span>' + r.tipo_rebanho + '</span><span>' + fNum(r.quantidade || 0) + ' cab.</span></li>'
    ).join('');
  }

  // Vizinhos — ranking de população com PIB per capita comparado por linha
  const vizinhos = g(D, 'secoes.vizinhanca.municipios') || [];
  const viziRef = g(D, 'secoes.vizinhanca.referencia');
  const nomeMunicipio = g(D, 'municipio.nome');
  if (vizinhos.length && document.getElementById('viziRanking')) {
    const refPop = viziRef && viziRef.populacao;
    const refPc = (viziRef && viziRef.pib_per_capita) || 0;
    document.getElementById('viziAno').textContent = (viziRef && viziRef.populacao_ano || '') + ' · PIB ' + (viziRef && viziRef.pib_ano || '');

    const acima = vizinhos.filter(v => (v.pib_per_capita || 0) > refPc).length;
    const abaixo = vizinhos.filter(v => v.pib_per_capita != null && v.pib_per_capita < refPc).length;
    // O per capita daqui divide o PIB do ano do PIB pela população do ano corrente,
    // então diverge do valor publicado pelo IBGE na seção Economia — dizer isso
    const pcOficial = g(D, 'secoes.economia.pib.pib_per_capita.valor');
    document.getElementById('viziResumo').innerHTML =
      vizinhos.length + ' municípios limítrofes (todos no ' + g(D, 'municipio.sigla_uf') + ') · <b style="color:var(--text)">' + nomeMunicipio + '</b>: R$ ' + fNum(Math.round(refPc)) + ' per capita — ' + acima + ' vizinho(s) acima, ' + abaixo + ' abaixo' +
      (pcOficial ? '<br>Base comparável: PIB de ' + (viziRef.pib_ano || '') + ' sobre a população de ' + (viziRef.populacao_ano || '') +
        ' para todos os municípios. O valor oficial do IBGE em Economia (R$ ' + fNum(Math.round(pcOficial)) + ') usa a população do próprio ano do PIB.' : '');

    const ranking = [{ nome: nomeMunicipio, populacao: refPop, pib_per_capita: refPc, self: true }, ...vizinhos]
      .sort((a, b) => (b.populacao || 0) - (a.populacao || 0));
    const maxPc = Math.max(...ranking.map(v => v.pib_per_capita || 0), 1);
    document.getElementById('viziRanking').innerHTML = ranking.map((v, i) => {
      const pc = v.pib_per_capita || 0;
      const fillColor = v.self ? C.s1 : (pc >= refPc ? C.s5 : C.s6);
      return '<div class="vr-row">' +
        '<div class="vr-top"><span class="vr-name' + (v.self ? ' me' : '') + '">' + (i + 1) + '. ' + v.nome + '</span><span class="vr-pop">' + fNum(v.populacao || 0) + ' hab</span></div>' +
        '<div class="vr-bottom"><div class="vr-track"><div class="vr-fill" style="width:' + (pc / maxPc * 100).toFixed(0) + '%;background:' + fillColor + '"></div></div><span class="vr-pib">R$ ' + Math.round(pc / 1000) + 'k/hab</span></div>' +
        '</div>';
    }).join('');

    // O minimapa tem as posições relativas desenhadas à mão para Nova Friburgo —
    // o JSON não traz coordenada de vizinho, então em outro município ele seria
    // um mapa inventado. Só aparece quando os dados são os de Nova Friburgo.
    const ehFriburgo = String(g(D, 'municipio.id_municipio')) === '3303401';
    const mapCard = el_('miniMapCard');
    if (mapCard) mapCard.hidden = !ehFriburgo;
    // Minimapa: mostra PIB per capita de cada vizinho no lugar do código IBGE
    const pcById = new Map(vizinhos.map(v => [String(v.id_municipio), v.pib_per_capita]));
    pcById.set(String(g(D, 'municipio.id_municipio')), refPc);
    document.querySelectorAll('.mm-code[data-mid]').forEach(el => {
      const pc = pcById.get(el.dataset.mid);
      el.textContent = pc ? 'R$ ' + Math.round(pc / 1000) + 'k/hab' : '—';
    });
  }

  // =========================================================================
  // VISÃO GERAL — cartões-síntese
  // =========================================================================
  const sim = ok(g(D, 'secoes.saude.mortalidade'));
  // Mortalidade infantil tem ano próprio: o último em que SIM e SINASC estão fechados
  const simInf = (sim && sim.infantil) || null;
  const simInfAnt = simInf ? (sim.serie || []).find(r => r.ano === simInf.ano - 1) || null : null;
  const sih = ok(g(D, 'secoes.saude.internacoes'));
  const viol = ok(g(D, 'secoes.seguranca.violencia_sinan'));
  const emp = ok(g(D, 'secoes.empresas'));
  const ibc = ok(g(D, 'secoes.conectividade.ibc'));
  const txSeg = g(D, 'secoes.seguranca.isp_rj.taxas_100k') || {};
  const txSegUf = g(D, 'secoes.seguranca.isp_rj.taxas_100k_uf') || {};

  const pop2023it = find(popSerie, 'ano', 2023);
  if (pop2023it && pop2024) {
    const dp = (pop2024 / pop2023it.populacao - 1) * 100;
    setCls('popDelta', 'delta ' + (dp >= 0 ? 'up' : 'down'));
    setHtml('popDelta', (dp >= 0 ? '▲ +' : '▼ ') + Math.abs(dp).toFixed(1).replace('.', ',') + '% <span class="vs">vs 2023</span>');
  }

  if (ideb2023Ini) {
    setTxt('idebIniciaisVal', fNum1(ideb2023Ini.ideb));
    setTxt('idebIniciaisAno', String(ideb2023Ini.ano || ''));
    const acimaBr = brIni != null && ideb2023Ini.ideb >= brIni;
    setCls('idebIniciaisStatus', 'status ' + (acimaBr ? 'st-good' : 'st-warn'));
    setTxt('idebIniciaisStatus', acimaBr ? '✓ acima do Brasil' : '! abaixo do Brasil');
    if (ideb2021Ini) {
      const di = ideb2023Ini.ideb - ideb2021Ini.ideb;
      setCls('idebIniciaisDelta', 'delta ' + (di >= 0 ? 'up' : 'down'));
      setHtml('idebIniciaisDelta', (di >= 0 ? '▲ +' : '▼ ') + Math.abs(di).toFixed(1).replace('.', ',') + ' <span class="vs">vs 2021</span>');
    }
  } else { vazioValor('idebIniciaisVal'); }

  if (snis) {
    setTxt('esgVintage', String(snis.ano || ''));
    if (snis.ano_anterior) {
      const dt = (snis.indice_tratamento_esgoto || 0) - (snis.ano_anterior.t || 0);
      setCls('esgDelta', 'delta ' + (dt >= 0 ? 'up' : 'down'));
      setHtml('esgDelta', (dt >= 0 ? '▲ +' : '▼ ') + Math.abs(dt).toFixed(1).replace('.', ',') + ' pp <span class="vs">vs ' + ((snis.ano || 0) - 1) + '</span>');
    }
    // O índice é sobre o coletado; o alcance real depende também da coleta
    const efetivo = (snis.indice_coleta_esgoto || 0) * (snis.indice_tratamento_esgoto || 0) / 100;
    const textoEfetivo = 'Cobertura efetiva ≈ ' + fNum1(efetivo) + '% do esgoto gerado (coleta × tratamento)';
    setTxt('esgResumoSub', textoEfetivo);
    setTxt('esgTSub', textoEfetivo);
  }

  if (txSeg.taxa_homicidio_doloso != null) {
    setHtml('homVal', fNum1(txSeg.taxa_homicidio_doloso) + ' <span class="unit">/100k hab</span>');
    setTxt('homVintage', String(txSeg.ano || ''));
    setCls('homDelta', 'delta flat');
    setHtml('homDelta', '<span class="vs">' + (txSegUf.taxa_homicidio_doloso ? Math.round(txSegUf.taxa_homicidio_doloso / txSeg.taxa_homicidio_doloso) + '× abaixo da taxa fluminense' : 'taxa ISP mais recente') + '</span>');
  } else { vazioValor('homVal'); }

  if (caged) setHtml('cagedDet', '<span class="vs">' + fNum(caged.admissoes || 0) + ' admissões − ' + fNum(caged.desligamentos || 0) + ' desligamentos</span>');

  if (ibc) {
    setTxt('ibcVal', fNum1(ibc.ibc));
    const dibc = (ibc.ibc || 0) - (ibc.media_brasil || 0);
    setCls('ibcDelta', 'delta ' + (dibc >= 0 ? 'up' : 'down'));
    setHtml('ibcDelta', (dibc >= 0 ? '▲ +' : '▼ ') + fNum1(Math.abs(dibc)) + ' <span class="vs">vs média nacional</span>');
  } else { vazioValor('ibcVal'); }

  // Mortalidade infantil (resumo)
  if (simInf && simInf.taxa_1000nv != null) {
    setTxt('resInfAno', String(simInf.ano || ''));
    setHtml('resInfVal', fNum1(simInf.taxa_1000nv) + ' <span class="unit">/1.000 nasc.</span>');
    const antSim = simInfAnt;
    if (antSim && antSim.infantis != null) {
      const dif = (simInf.obitos || 0) - antSim.infantis;
      setCls('resInfDelta', 'delta ' + (dif <= 0 ? 'down-good' : 'up-bad'));
      setHtml('resInfDelta', (dif <= 0 ? '▼ ' : '▲ +') + Math.abs(dif) + ' óbito(s) <span class="vs">vs ' + antSim.ano + '</span>');
    }
  } else { vazioValor('resInfVal'); }

  // Internações SUS (resumo)
  if (sih && sih.internacoes != null) {
    setTxt('resSihAno', String(sih.ano || ''));
    setHtml('resSihVal', fNum(sih.internacoes) + ' <span class="unit">AIH</span>');
    const antSih = sih.ano_anterior;
    if (antSih && antSih.internacoes) {
      const ds = (sih.internacoes / antSih.internacoes - 1) * 100;
      setCls('resSihDelta', 'delta ' + (ds >= 0 ? 'up-bad' : 'down-good'));
      setHtml('resSihDelta', (ds >= 0 ? '▲ +' : '▼ ') + Math.abs(ds).toFixed(1).replace('.', ',') + '% <span class="vs">vs ' + ((sih.ano || 0) - 1) + '</span>');
    }
  } else { vazioValor('resSihVal'); }

  // Violência notificada (resumo)
  if (viol && viol.notificacoes != null) {
    setTxt('resViolAno', String(viol.ano || ''));
    setHtml('resViolVal', fNum(viol.notificacoes) + ' <span class="unit">notificações</span>');
    setCls('resViolDelta', 'delta flat');
    setHtml('resViolDelta', '<span class="vs">' + fNum1(viol.pct_feminino || 0) + '% das vítimas são mulheres</span>');
  } else { vazioValor('resViolVal'); pill('stViol', null); }

  // Empresas ativas (resumo)
  if (emp && emp.ativas != null) {
    setTxt('resEmpAno', (emp.competencia || '').slice(0, 4));
    setHtml('resEmpVal', fNum(emp.ativas) + ' <span class="unit">CNPJ</span>');
    const dem = emp.demografia_empresarial || [];
    const ultDem = dem.length ? dem[dem.length - 1] : null;
    if (ultDem) {
      setCls('resEmpDelta', 'delta ' + (ultDem.saldo >= 0 ? 'up' : 'down'));
      setHtml('resEmpDelta', (ultDem.saldo >= 0 ? '▲ +' : '▼ ') + fNum(Math.abs(ultDem.saldo)) + ' <span class="vs">saldo em ' + ultDem.ano + '</span>');
    }
  } else { vazioValor('resEmpVal'); }

  // ---- Semáforos derivados do dado ----------------------------------------
  // Cada selo abaixo estava escrito à mão no HTML com o resultado de Nova Friburgo.
  // Aqui cada um passa a sair do próprio número, com a referência explícita no rótulo.
  if (pop2023it && pop2024) {
    const cresce = pop2024 >= pop2023it.populacao;
    pill('stPop', cresce ? 'st-good' : 'st-warn', cresce ? '✓ crescendo' : '! encolhendo');
  } else { pill('stPop', null); }

  pillVs('stPibPc', pibPc && pibPc.valor, pibPc && pibPc.uf, ['acima do RJ', 'abaixo do RJ']);
  setTxt('resPibPcAno', pibPc && pibPc.ano ? String(pibPc.ano) : '');
  setTxt('resPopAno', pop2024item && pop2024item.ano ? String(pop2024item.ano) : '');
  setTxt('resCagedAno', caged && caged.ano ? String(caged.ano) : '');
  setTxt('resIbcAno', ibc && ibc.ano ? String(ibc.ano) : '');
  const esgAnt = snis && snis.ano_anterior && snis.ano_anterior.indice_tratamento_esgoto;
  if (snis && snis.indice_tratamento_esgoto != null && esgAnt != null) {
    const sobe = snis.indice_tratamento_esgoto >= esgAnt;
    pill('stEsg', sobe ? 'st-good' : 'st-warn', sobe ? '✓ em alta' : '! em queda');
  } else { pill('stEsg', null); }
  pillVs('stIbc', ibc && ibc.ibc, ibc && ibc.media_brasil, ['acima da média BR', 'abaixo da média BR']);
  if (simInf && simInf.obitos != null && simInfAnt && simInfAnt.infantis != null) {
    const cai = simInf.obitos <= simInfAnt.infantis;
    pill('stInf', cai ? 'st-good' : 'st-warn', cai ? '✓ em queda' : '! em alta');
  } else { pill('stInf', null); }

  if (txSeg.taxa_homicidio_doloso != null && txSegUf.taxa_homicidio_doloso) {
    const r = txSeg.taxa_homicidio_doloso / txSegUf.taxa_homicidio_doloso;
    if (r <= 0.5) pill('stHom', 'st-good', '✓ muito abaixo RJ');
    else if (r <= 1) pill('stHom', 'st-good', '✓ abaixo do RJ');
    else if (r <= 1.3) pill('stHom', 'st-warn', '! acima do RJ');
    else pill('stHom', 'st-crit', '✕ muito acima RJ');
  } else { pill('stHom', null); }

  if (caged && caged.saldo != null) {
    pill('stCaged', caged.saldo >= 0 ? 'st-good' : 'st-crit', caged.saldo >= 0 ? '✓ positivo' : '✕ negativo');
  } else { pill('stCaged', null); }

  if (sih && sih.ano_anterior && sih.ano_anterior.internacoes) {
    const sobe = sih.internacoes >= sih.ano_anterior.internacoes;
    pill('stSih', sobe ? 'st-warn' : 'st-good', sobe ? '! em alta' : '✓ em queda');
  } else { pill('stSih', null); }

  const ultDemoEmp = emp && (emp.demografia_empresarial || []).slice(-1)[0];
  if (ultDemoEmp) {
    pill('stEmp', ultDemoEmp.saldo >= 0 ? 'st-good' : 'st-crit',
      ultDemoEmp.saldo >= 0 ? '✓ saldo positivo' : '✕ saldo negativo');
  } else { pill('stEmp', null); }

  // Faixas do PNUD para o IDHM e do IPEA para o IVS — nomes oficiais, não adjetivos soltos
  const idhmV = avs && avs.idhm;
  if (idhmV != null) {
    const faixa = idhmV >= 0.8 ? ['st-good', '✓ muito alto'] : idhmV >= 0.7 ? ['st-good', '✓ alto']
      : idhmV >= 0.6 ? ['st-warn', '! médio'] : idhmV >= 0.5 ? ['st-serious', '! baixo'] : ['st-crit', '✕ muito baixo'];
    pill('stIdhm', faixa[0], faixa[1]); pill('stIdhm2', faixa[0], faixa[1]);
  } else { pill('stIdhm', null); pill('stIdhm2', null); }

  const ivsV = avs && avs.ivs;
  if (ivsV != null) {
    const faixa = ivsV <= 0.2 ? ['st-good', '✓ muito baixa'] : ivsV <= 0.3 ? ['st-good', '✓ baixa']
      : ivsV <= 0.4 ? ['st-warn', '! média'] : ivsV <= 0.5 ? ['st-serious', '! alta'] : ['st-crit', '✕ muito alta'];
    pill('stIvs', faixa[0], faixa[1]);
  } else { pill('stIvs', null); }

  if (dengue && dengue.notificados_ano_anterior) {
    const cai = (dengue.notificados || 0) <= dengue.notificados_ano_anterior;
    pill('stDengue', cai ? 'st-good' : 'st-warn', cai ? '✓ em queda' : '! em alta');
  } else { pill('stDengue', null); }

  // =========================================================================
  // DEMOGRAFIA — censo 2022 ampliado (cor/raça, religião, alfabetização)
  // =========================================================================
  const cx = ok(g(D, 'secoes.demografia.censo_extra'));

  if (alf != null) {
    // A taxa do censo é sobre a população em idade de alfabetização, não sobre o total —
    // usar a base real quando ela vem no recorte por cor/raça
    const baseAlf = ((cx && cx.alfabetizacao_por_raca) || []).reduce((s, r) => s + (r.total || 0), 0) || pop2022;
    setTxt('alfDelta', '≈ ' + fNum(Math.round(baseAlf * (1 - alf))) + ' não alfabetizadas entre ' + fNum(baseAlf) + ' na base do censo');
  }
  // Sem índice de envelhecimento nacional no JSON, o subtítulo descreve o próprio
  // número em vez de compará-lo com uma média que a página não tem.
  const pir65 = g(D, 'secoes.demografia.piramide_etaria_2022');
  const idosos65 = pir65 && pir65.grupos ? pir65.grupos.reduce((acc, rot, i) => {
    const ini = parseInt(rot, 10);
    return acc + (ini >= 65 ? (pir65.homens[i] || 0) + (pir65.mulheres[i] || 0) : 0);
  }, 0) : null;
  if (env != null && idosos65) {
    setTxt('envDelta', fNum(idosos65) + ' pessoas de 65 anos ou mais no censo 2022');
  } else { setTxt('envDelta', ''); }

  // Cor ou raça — 2010 vs 2022
  const raca2010 = (cx && cx.cor_raca && cx.cor_raca['2010']) || [];
  const raca2022 = (cx && cx.cor_raca && cx.cor_raca['2022']) || [];
  if (raca2010.length && raca2022.length) {
    const cats = raca2022.map(r => r.cor_raca);
    const v10 = cats.map(c => (raca2010.find(r => r.cor_raca === c) || {}).populacao || 0);
    const v22 = cats.map(c => (raca2022.find(r => r.cor_raca === c) || {}).populacao || 0);
    criaGrafico(el_('racaChart'), {
      type: 'bar', data: {
        labels: cats,
        datasets: [
          { label: '2010', data: v10, backgroundColor: C.s1, maxBarThickness: 18, borderRadius: 3 },
          { label: '2022', data: v22, backgroundColor: C.s5, maxBarThickness: 18, borderRadius: 3 },
        ]
      },
      options: { ...chartOpts, indexAxis: 'y',
        plugins: { ...chartOpts.plugins, tooltip: { ...chartOpts.plugins.tooltip,
          callbacks: { label: ctx => ctx.dataset.label + ': ' + fNum(ctx.parsed.x) + ' hab' } } },
        scales: { x: { ticks: { color: C.muted, callback: v => fNum(v) }, grid: { color: C.grid } },
                  y: { ticks: { color: C.tick, autoSkip: false, font: { size: 11 } }, grid: { display: false } } } }
    });
    const variacoes = cats.map((c, i) => ({ c, pct: v10[i] ? (v22[i] / v10[i] - 1) * 100 : 0, base: v10[i] }))
      .filter(x => x.base > 5000).sort((a, b) => b.pct - a.pct);
    if (variacoes.length > 1) {
      const sobe = variacoes[0], desce = variacoes[variacoes.length - 1];
      setTxt('racaSub', 'Entre os censos, ' + sobe.c.toLowerCase() + ' ' + (sobe.pct >= 0 ? '+' : '−') + fNum1(Math.abs(sobe.pct)) + '% e ' +
        desce.c.toLowerCase() + ' ' + (desce.pct >= 0 ? '+' : '−') + fNum1(Math.abs(desce.pct)) + '% — autodeclaração, muda mais que a composição real da população');
    }
  } else { vazioGrafico('racaChart'); }

  // Religião — censo 2022
  const relig = (cx && cx.religiao) || null;
  const grupos = (relig && relig.grupos) || [];
  if (grupos.length) {
    const top = grupos.slice(0, 6);
    const resto = grupos.slice(6).reduce((s, r) => s + (r.populacao || 0), 0);
    const labels = top.map(r => r.religiao.replace('Católica Apostólica Romana', 'Católica'));
    const dados = top.map(r => r.populacao);
    if (resto > 0) { labels.push('Demais'); dados.push(resto); }
    criaGrafico(el_('religiaoChart'), {
      type: 'doughnut', data: {
        labels, datasets: [{ data: dados, backgroundColor: [C.s1, C.s2, C.s3, C.s4, C.s5, C.s6, C.s7], borderColor: C.surface, borderWidth: 2 }]
      },
      options: {
        responsive: true, maintainAspectRatio: false, cutout: '58%',
        plugins: {
          legend: { position: 'bottom', labels: { color: C.tick, padding: 8, usePointStyle: true, boxWidth: 8, font: { size: 10 } } },
          tooltip: { ...chartOpts.plugins.tooltip,
            callbacks: { label: ctx => ctx.label + ': ' + fNum(ctx.parsed) + ' (' + pctDe(ctx.parsed, relig.total_10_anos_ou_mais).toFixed(1).replace('.', ',') + '%)' } }
        }
      }
    });
  } else { vazioGrafico('religiaoChart'); }

  // Alfabetização por cor/raça
  const alfRaca = (cx && cx.alfabetizacao_por_raca) || [];
  if (alfRaca.length) {
    setHtml('alfRacaList', alfRaca.map(r =>
      liRow(r.cor_raca + ' <span style="color:var(--text3)">(' + fNum(r.total) + ')</span>', fNum1(r.taxa) + '%')).join(''));
    const relevantes = alfRaca.filter(r => (r.total || 0) >= 1000);
    if (relevantes.length > 1) {
      const taxas = relevantes.map(r => r.taxa);
      setTxt('alfRacaGap', fNum1(Math.max(...taxas) - Math.min(...taxas)) + ' pp (grupos com 1.000+ pessoas)');
    } else { setTxt('alfRacaGap', '—'); }
  } else { vazioLista('alfRacaList'); setTxt('alfRacaGap', '—'); }

  // =========================================================================
  // INFRAESTRUTURA — domicílios do censo 2022
  // =========================================================================
  const dom = ok(g(D, 'secoes.infraestrutura.censo_domicilios'));

  // Categoria do censo vem como frase inteira; o eixo só cabe se ela for encurtada
  // por regra explícita — cortar em N caracteres deixava "…ligada" e "…não ligada"
  // indistinguíveis no eixo do esgotamento.
  const CURTO_CENSO = {
    'Rede geral, rede pluvial ou fossa ligada à rede': 'Rede geral / pluvial',
    'Fossa séptica ou fossa filtro não ligada à rede': 'Fossa séptica (isolada)',
    'Fossa rudimentar ou buraco': 'Fossa rudimentar',
    'Rio, lago, córrego ou mar': 'Rio, lago ou mar',
    'Não tinham banheiro nem sanitário': 'Sem banheiro',
  };
  const curtoCenso = s => CURTO_CENSO[s] || truncaPalavra(s, 30);

  function barraCategorias(canvasId, bloco, unidade) {
    const cats = (bloco && bloco.categorias) || [];
    if (!cats.length) { vazioGrafico(canvasId); return null; }
    const dados = cats.slice(0, 7);
    criaGrafico(el_(canvasId), {
      type: 'bar', data: {
        labels: dados.map(c => curtoCenso(c.categoria)),
        datasets: [{ data: dados.map(c => c.pct), backgroundColor: C.s1, maxBarThickness: 16, borderRadius: 4, borderSkipped: 'start' }]
      },
      options: { ...chartOpts, indexAxis: 'y',
        plugins: { ...noLegend, tooltip: { ...chartOpts.plugins.tooltip,
          callbacks: { title: ctx => dados[ctx[0].dataIndex].categoria,
            label: ctx => fNum1(ctx.parsed.x) + '% · ' + fNum(dados[ctx.dataIndex].populacao) + ' ' + (unidade || 'hab') } } },
        scales: { x: { ticks: { color: C.muted, callback: v => v + '%' }, grid: { color: C.grid } },
                  y: { ticks: { color: C.tick, autoSkip: false, font: { size: 10 } }, grid: { display: false } } } }
    });
    return dados;
  }

  if (dom) {
    barraCategorias('domEsgotoChart', dom.esgotamento);
    // Água: 3 categorias — rosca lê melhor que barra
    const agua = (dom.agua && dom.agua.categorias) || [];
    if (agua.length) {
      criaGrafico(el_('domAguaChart'), {
        type: 'doughnut', data: {
          labels: agua.map(c => c.categoria.replace('Possui ligação à rede geral e a utiliza como forma principal', 'Rede geral (principal)')
            .replace('Possui ligação à rede geral, mas utiliza principalmente outra forma', 'Rede geral (secundária)')
            .replace('Não possui ligação com a rede geral', 'Sem rede geral')),
          datasets: [{ data: agua.map(c => c.populacao), backgroundColor: [C.s1, C.s6, C.s4], borderColor: C.surface, borderWidth: 2 }]
        },
        options: {
          responsive: true, maintainAspectRatio: false, cutout: '58%',
          plugins: {
            legend: { position: 'bottom', labels: { color: C.tick, padding: 8, usePointStyle: true, boxWidth: 8, font: { size: 10 } } },
            tooltip: { ...chartOpts.plugins.tooltip,
              callbacks: { label: ctx => ctx.label + ': ' + fNum(ctx.parsed) + ' hab (' + pctDe(ctx.parsed, dom.agua.total).toFixed(1).replace('.', ',') + '%)' } }
          }
        }
      });
    } else { vazioGrafico('domAguaChart'); }

    // Rótulos do censo são frases inteiras — encurtar antes de virar eixo de barra
    // (o texto completo fica no `title`, acessível no hover)
    const curto = s => String(s)
      .replace('Jogado em terreno baldio, encosta ou área pública', 'Terreno baldio')
      .replace('Queimado na propriedade', 'Queimado')
      .replace('Enterrado na propriedade', 'Enterrado')
      .replace('Habitação em casa de cômodos ou cortiço', 'Cômodos / cortiço')
      .replace('Estrutura residencial permanente degradada ou inacabada', 'Degradado')
      .replace('Casa de vila ou em condomínio', 'Vila / condomínio')
      ; // encurtado por regra acima; o resto cai no truncador por palavra
    const curtoDom = s => truncaPalavra(curto(s), 22);
    const catBarras = cats => cats.map(c => ({ k: curtoDom(c.categoria), titulo: c.categoria, v: c.populacao }));

    const lixo = (dom.lixo && dom.lixo.categorias) || [];
    barrasCategoria('domLixoBars', catBarras(lixo), (dom.lixo || {}).total, C.s5, { soPct: true });

    const tipos = (dom.tipo_domicilio && dom.tipo_domicilio.categorias) || [];
    barrasCategoria('domTipoBars', catBarras(tipos), (dom.tipo_domicilio || {}).total, C.s1, { soPct: true });

    // Espécies do censo aninham entre si — mostrar as mutuamente exclusivas
    const rec = dom.domicilios_recenseados || [];
    const acha = n => (rec.find(r => r.especie === n) || {}).domicilios;
    const linhas = [
      ['Ocupados', acha('Particular permanente ocupado')],
      ['Vagos', acha('Particular permanente não ocupado - vago')],
      ['Uso ocasional', acha('Particular permanente não ocupado - uso ocasional')],
      ['Coletivos', acha('Coletivo')],
    ].filter(r => r[1] != null);
    setHtml('domRecList', linhas.length
      ? linhas.map(r => liRow(r[0], fNum(r[1]))).join('')
      : '');
    if (!linhas.length) vazioLista('domRecList');
  } else {
    vazioGrafico('domEsgotoChart'); vazioGrafico('domAguaChart');
    barrasCategoria('domLixoBars', [], 0); barrasCategoria('domTipoBars', [], 0);
    vazioLista('domRecList');
  }

  // Notas de leitura — SNIS (prestador) e censo (morador) medem coisas diferentes
  const esgRede = dom && dom.esgotamento && (dom.esgotamento.categorias || [])[0];
  setTxt('domEsgotoNota', 'Declarado pelo morador (IBGE)' +
    (snis ? ' — o SNIS registra ' + fNum1(snis.indice_coleta_esgoto || 0) + '% de coleta no mesmo município, contra ' +
      (esgRede ? fNum1(esgRede.pct) : '—') + '% ligados à rede aqui' : '') +
    '. As duas medidas divergem por construção: uma é o cadastro do prestador, a outra é a percepção de quem mora.');
  const aguaRede = dom && dom.agua && (dom.agua.categorias || [])[0];
  setTxt('domAguaNota', 'Declarado pelo morador (IBGE)' +
    (snis ? ' — SNIS: ' + fNum1(snis.indice_atendimento_total_agua || 0) + '% de atendimento; censo: ' +
      (aguaRede ? fNum1(aguaRede.pct) : '—') + '% usam a rede geral como forma principal' : '') + '.');

  // =========================================================================
  // ECONOMIA — PIB per capita, combustíveis (ANP), INPC
  // =========================================================================
  if (pibPc) setHtml('pibPcVal', 'R$ ' + fNum(Math.round(pibPc.valor || 0)));

  const anp = ok(g(D, 'secoes.economia.combustiveis'));
  const produtos = (anp && anp.produtos) || [];
  if (produtos.length) {
    const coleta = produtos[0].ultima_coleta || '';
    setTxt('anpAno', coleta ? coleta.slice(5, 7) + '/' + coleta.slice(0, 4) : '');
    // GLP é vendido por botijão de 13 kg — nunca comparar com o litro
    const unidade = p => /GLP/.test(p.produto) ? '/13 kg' : '/l';
    const linhaAnp = p => {
      const d = (p.preco_municipio || 0) - (p.preco_brasil || 0);
      const cor = d > 0 ? 'var(--delta-bad)' : 'var(--delta-good)';
      // titulo() preserva "S10"/"GLP" — charAt+toLowerCase devolvia "Diesel s10"
      return liRow(titulo(p.produto).replace(/\bS10\b/i, 'S10').replace(/\bGlp\b/, 'GLP'),
        'R$ ' + fmt2(p.preco_municipio) + ' <span style="color:var(--text3)">' + unidade(p) + '</span>' +
        ' <span style="color:' + cor + ';font-size:.72rem">' + (d >= 0 ? '+' : '−') + fmt2(Math.abs(d)) + ' vs BR</span>');
    };
    const destaque = ['GASOLINA COMUM', 'ETANOL', 'DIESEL S10'];
    const principais = destaque.map(n => produtos.find(p => p.produto === n)).filter(Boolean);
    setHtml('anpList', (principais.length ? principais : produtos.slice(0, 3)).map(linhaAnp).join(''));
    setHtml('anpDetList', produtos.map(linhaAnp).join(''));
    const postos = Math.max(...produtos.map(p => p.postos || 0));
    setTxt('anpPostos', 'Até ' + postos + ' postos pesquisados · média dos últimos ' + (anp.janela_dias || 60) + ' dias até ' +
      (coleta ? coleta.split('-').reverse().join('/') : '—'));
  } else {
    vazioLista('anpList'); vazioLista('anpDetList');
    setTxt('anpPostos', 'A ANP não coletou preço neste município na janela');
  }

  if (inpc) {
    setHtml('inpcDetList',
      liRow('Acumulado no ano', (inpc.variacao_anual != null ? inpc.variacao_anual.toFixed(2).replace('.', ',') + '%' : '—')) +
      liRow('Referência', 'Brasil — o INPC não é apurado por município'));
  }

  // =========================================================================
  // EMPRESAS — base CNPJ da Receita Federal
  // =========================================================================
  if (emp) {
    const comp = emp.competencia || '';
    ['cnpjComp', 'cnpjComp2', 'cnpjComp3', 'cnpjComp4', 'cnpjComp5', 'cnpjComp6']
      .forEach(id => setTxt(id, comp ? comp.split('-').reverse().join('/') : ''));
    setTxt('cnpjAtivas', fNum(emp.ativas || 0));
    setTxt('cnpjPorHab', pop2024 ? fNum1((emp.ativas || 0) / pop2024 * 100) + ' por 100 habitantes' : '');
    setTxt('cnpjMatriz', fNum(emp.matrizes || 0));
    setTxt('cnpjFilial', fNum(emp.filiais || 0) + ' filiais · ' +
      fNum1(pctDe(emp.matrizes, (emp.matrizes || 0) + (emp.filiais || 0))) + '% dos ativos são matriz');
    setHtml('cnpjIdade', fNum1(emp.idade_media_anos || 0) + ' <span class="unit">anos</span>');
    setTxt('cnpjBaixadas', fNum(emp.baixadas || 0));
    setTxt('cnpjRegistradas', fNum(emp.registradas || 0) + ' CNPJ já registrados no município');

    const secoes = emp.por_secao_cnae || [];
    if (secoes.length) {
      criaGrafico(el_('cnaeChart'), {
        type: 'bar', data: {
          labels: secoes.map(s => {
            const n = titulo(s.secao).replace('; Reparação de Veículos Automotores e Motocicletas', '')
              .replace('Atividades Administrativas e Serviços Complementares', 'Ativ. administrativas')
              .replace('Atividades Profissionais, Científicas e Técnicas', 'Ativ. profissionais/técnicas')
              .replace('Transporte, Armazenagem E Correio', 'Transporte e armazenagem');
            return truncaPalavra(n, 34);
          }),
          datasets: [{ data: secoes.map(s => s.ativas), backgroundColor: C.s1, maxBarThickness: 16, borderRadius: 4, borderSkipped: 'start' }]
        },
        options: { ...chartOpts, indexAxis: 'y',
          plugins: { ...noLegend, tooltip: { ...chartOpts.plugins.tooltip,
            callbacks: { title: ctx => secoes[ctx[0].dataIndex].secao, label: ctx => fNum(ctx.parsed.x) + ' estabelecimentos ativos' } } },
          scales: { x: { ticks: { color: C.muted, callback: v => fNum(v) }, grid: { color: C.grid } },
                    y: { ticks: { color: C.tick, autoSkip: false, font: { size: 10 } }, grid: { display: false } } } }
      });
    } else { vazioGrafico('cnaeChart'); }

    const demoEmp = emp.demografia_empresarial || [];
    if (demoEmp.length > 1) {
      setTxt('cnpjDemoAno', demoEmp[0].ano + '–' + demoEmp[demoEmp.length - 1].ano);
      criaGrafico(el_('cnpjDemoChart'), {
        type: 'bar', data: {
          labels: demoEmp.map(r => r.ano),
          datasets: [
            { label: 'Aberturas', data: demoEmp.map(r => r.aberturas), backgroundColor: C.s5, maxBarThickness: 16, borderRadius: 3, order: 2 },
            { label: 'Baixas', data: demoEmp.map(r => r.baixas), backgroundColor: C.s6, maxBarThickness: 16, borderRadius: 3, order: 2 },
            { label: 'Saldo', data: demoEmp.map(r => r.saldo), type: 'line', borderColor: C.s1, backgroundColor: C.s1, pointBackgroundColor: C.s1, ...lineStyle, pointRadius: 3, fill: false, order: 1 },
          ]
        },
        options: { ...chartOpts,
          plugins: { ...chartOpts.plugins, tooltip: { ...chartOpts.plugins.tooltip,
            callbacks: { label: ctx => ctx.dataset.label + ': ' + fNum(ctx.parsed.y) } } },
          scales: { x: { ticks: { color: C.muted }, grid: { display: false } },
                    y: { ticks: { color: C.muted, callback: v => fNum(v) }, grid: { color: C.grid } } } }
      });
      const ultDemo = demoEmp[demoEmp.length - 1];
      const pico = demoEmp.reduce((a, b) => (b.saldo > a.saldo ? b : a), demoEmp[0]);
      setTxt('cnpjDemoSub', 'Saldo positivo em todos os anos da série · maior saldo em ' + pico.ano +
        ' (+' + fNum(pico.saldo) + ') · ' + ultDemo.ano + ' fechou em +' + fNum(ultDemo.saldo) +
        '. Ano corrente pode estar incompleto no espelho.');
    } else { vazioGrafico('cnpjDemoChart'); }

    // Ranking com barra proporcional — nomes de CNAE são longos demais pra um eixo
    const ativs = emp.top_atividades || [];
    if (ativs.length) {
      const maxAtiv = Math.max(...ativs.map(a => a.ativas || 0), 1);
      setHtml('cnaeTopList', ativs.map((a, i) =>
        '<tr>' +
        '<td class="rank-name" title="' + a.atividade + '"><span class="rk-num">' + (i + 1) + '.</span><b>' + a.atividade + '</b></td>' +
        '<td class="area"><div class="rank-bar"><div class="track"><div class="fill" style="width:' + (a.ativas / maxAtiv * 100).toFixed(0) + '%"></div></div>' +
        '<span class="pct">' + fNum1(pctDe(a.ativas, emp.ativas)) + '%</span></div></td>' +
        '<td class="valor" data-label="Estabelecimentos"><span class="val">' + fNum(a.ativas) + '</span></td>' +
        '</tr>').join(''));
    } else { vazioTabela('cnaeTopList', 3); }
  } else {
    vazioValores('cnpjAtivas', 'cnpjMatriz', 'cnpjIdade', 'cnpjBaixadas');
    vazioGrafico('cnaeChart'); vazioGrafico('cnpjDemoChart'); vazioTabela('cnaeTopList', 3);
  }

  // =========================================================================
  // TRABALHO — complementos
  // =========================================================================
  if (caged) {
    setTxt('cagedSaldoVal', (caged.saldo > 0 ? '+' : '') + fNum(caged.saldo || 0));
  } else { vazioValor('cagedSaldoVal'); }
  if (rais) {
    setHtml('raisSalBench', '<span>Média das remunerações da RAIS' + (rais.ano ? ' ' + rais.ano : '') + '</span>' +
      (caged && caged.salario_medio_admissao ? '<span><b>Admissão (CAGED ' + caged.ano + '):</b> R$ ' + fNum(Math.round(caged.salario_medio_admissao)) + '</span>' : ''));
  }

  // =========================================================================
  // EDUCAÇÃO — censo escolar e SISU
  // =========================================================================
  const ce = ok(g(D, 'secoes.educacao.censo_escolar'));
  if (ce) {
    const anoCe = String(ce.ano || '');
    ['censoEscAno', 'censoEscAno2', 'censoEscAno3', 'censoEscAno4', 'censoEscAno5', 'censoEscAno6', 'censoEscAno7'].forEach(id => setTxt(id, anoCe));

    // Ordem etária, não por volume: infantil → fundamental → médio é a leitura natural
    const etapas = [
      ['Educação infantil', ce.matriculas_infantil],
      ['Ensino fundamental', ce.matriculas_fundamental],
      ['Ensino médio', ce.matriculas_medio],
    ].filter(e => e[1] != null).map(e => ({ k: e[0], v: e[1] }));
    barrasCategoria('matEtapaBars', etapas, ce.matriculas, C.s1);
    setHtml('matEtapaDetList',
      liRow('EJA', fNum(ce.matriculas_eja || 0)) +
      liRow('Educação especial (incluída)', fNum(ce.matriculas_especial || 0)) +
      liRow('Total de matrículas', fNum(ce.matriculas || 0)) +
      liRow('Turmas', fNum(ce.turmas || 0)));

    setTxt('escTotal', fNum(ce.escolas || 0));
    setTxt('escRuralSub', fNum(ce.escolas_rurais || 0) + ' na zona rural (' + fNum1(pctDe(ce.escolas_rurais, ce.escolas)) + '%)');
    setTxt('escMat', fNum(ce.matriculas || 0));
    const serieCe = ce.serie || [];
    const antCe = serieCe.length > 1 ? serieCe[serieCe.length - 2] : null;
    if (antCe && antCe.matriculas) {
      const dce = (ce.matriculas / antCe.matriculas - 1) * 100;
      setCls('escMatDelta', 'delta ' + (dce >= 0 ? 'up' : 'down'));
      setHtml('escMatDelta', (dce >= 0 ? '▲ +' : '▼ ') + Math.abs(dce).toFixed(1).replace('.', ',') + '% <span class="vs">vs ' + antCe.ano + '</span>');
    }
    setTxt('escDoc', fNum(ce.docentes || 0));
    setTxt('escDocSub', ce.docentes ? fNum1((ce.matriculas || 0) / ce.docentes) + ' matrículas por docente' : '');
    setTxt('escTransp', fNum(ce.matriculas_transporte || 0));
    setTxt('escTranspSub', fNum1(pctDe(ce.matriculas_transporte, ce.matriculas)) + '% das matrículas usam transporte escolar');

    const redes = ce.por_rede || [];
    if (redes.length) {
      criaGrafico(el_('redeChart'), {
        type: 'doughnut', data: {
          labels: redes.map(r => r.rede),
          datasets: [{ data: redes.map(r => r.matriculas), backgroundColor: [C.s1, C.s4, C.s5, C.s3], borderColor: C.surface, borderWidth: 2 }]
        },
        options: {
          responsive: true, maintainAspectRatio: false, cutout: '58%',
          plugins: {
            legend: { position: 'bottom', labels: { color: C.tick, padding: 10, usePointStyle: true, boxWidth: 8, font: { size: 10 } } },
            tooltip: { ...chartOpts.plugins.tooltip,
              callbacks: { label: ctx => {
                const r = redes[ctx.dataIndex];
                return r.rede + ': ' + fNum(r.matriculas) + ' matrículas · ' + fNum(r.escolas) + ' escolas';
              } } }
          }
        }
      });
    } else { vazioGrafico('redeChart'); }

    const infra = [
      ['Internet', ce.com_internet], ['Esgoto na rede', ce.com_esgoto_rede],
      ['Rampa de acesso', ce.com_rampa_acessibilidade], ['Biblioteca', ce.com_biblioteca],
      ['Quadra', ce.com_quadra], ['Laboratório', ce.com_laboratorio],
    ].filter(r => r[1] != null).sort((a, b) => b[1] - a[1]);
    setHtml('escInfraBars', infra.length ? infra.map(r => {
      const p = pctDe(r[1], ce.escolas);
      return '<div class="row"><span>' + r[0] + '</span><div class="track"><div class="fill" style="width:' +
        p.toFixed(0) + '%;background:' + (p >= 80 ? C.s5 : p >= 50 ? C.s4 : C.s6) + '"></div></div><span>' + fNum1(p) + '%</span></div>';
    }).join('') : '<div class="empty">' + SEM_DADO + '</div>');
  } else {
    barrasCategoria('matEtapaBars', [], 0); vazioLista('matEtapaDetList');
    vazioValores('escTotal', 'escMat', 'escDoc', 'escTransp');
    vazioGrafico('redeChart'); setHtml('escInfraBars', '<div class="empty">' + SEM_DADO + '</div>');
  }

  const sisu = ok(g(D, 'secoes.educacao.sisu'));
  const sisuSerie = (sisu && sisu.serie) || [];
  const sisuUlt = sisuSerie.length ? sisuSerie[sisuSerie.length - 1] : null;
  if (sisuUlt) {
    setTxt('sisuAno', String(sisuUlt.ano || ''));
    setHtml('sisuList',
      liRow('Candidatos do município', fNum(sisuUlt.candidatos || 0)) +
      liRow('Aprovados', fNum(sisuUlt.aprovados || 0)) +
      liRow('Matrículas efetivadas', fNum(sisuUlt.matriculados || 0)) +
      liRow('Nota média', fNum1(sisuUlt.nota_media || 0)));
    const cursos = sisu.top_cursos || [];
    setHtml('sisuCursosList', cursos.length
      ? cursos.map(c => liRow(titulo(c.curso) + ' <span style="color:var(--text3)">· ' + c.ies + '</span>', fNum(c.matriculados))).join('')
      : '');
    if (!cursos.length) vazioLista('sisuCursosList');
  } else {
    vazioLista('sisuList'); vazioLista('sisuCursosList');
  }

  // =========================================================================
  // SAÚDE — SISVAN, IEPS, ANS, Farmácia Popular, cobertura vacinal
  // =========================================================================
  const sisvan = ok(g(D, 'secoes.saude.sisvan'));
  if (sisvan && (sisvan.criancas_acompanhadas || 0) > 0) {
    setTxt('sisvanAno', String(sisvan.ano || ''));
    setHtml('sisvanList',
      liRow('Crianças acompanhadas', fNum(sisvan.criancas_acompanhadas)) +
      liRow('Baixo peso', sisvan.pct_baixo_peso != null ? fNum1(sisvan.pct_baixo_peso) + '%' : '—') +
      liRow('Excesso de peso', sisvan.pct_excesso_peso != null ? fNum1(sisvan.pct_excesso_peso) + '%' : '—'));
  } else {
    setTxt('sisvanAno', sisvan && sisvan.ano ? String(sisvan.ano) : '');
    vazioLista('sisvanList', 'Nenhuma criança acompanhada registrada no SISVAN para este município no ano');
  }

  const ieps = ok(g(D, 'secoes.saude.ieps'));
  const ind = (ieps && ieps.indicadores) || {};
  const anosInd = (ieps && ieps.ano_por_indicador) || {};
  if (ieps && Object.keys(ind).length) {
    const anoDe = k => String(anosInd[k] || ieps.ano_max || '');
    setTxt('iepsAno', anoDe('medicos_1000hab'));
    setTxt('iepsAno2', anoDe('enfermeiros_1000hab'));
    setTxt('iepsAno3', anoDe('cobertura_esf'));
    setTxt('iepsAno4', anoDe('despesa_saude_per_capita'));
    setTxt('iepsAno5', anoDe('taxa_internacao_csap_100k'));
    setTxt('iepsAno6', anoDe('pct_prenatal_adequado'));
    setTxt('iepsMed', fNum1(ind.medicos_1000hab || 0));
    setTxt('iepsEnf', fNum1(ind.enfermeiros_1000hab || 0));
    setHtml('iepsEsf', fNum1(ind.cobertura_esf || 0) + ' <span class="unit">%</span>');
    setHtml('iepsGasto', 'R$ ' + fNum(Math.round(ind.despesa_saude_per_capita || 0)) + ' <span class="unit">/hab·ano</span>');
    setHtml('iepsGastoBench', '<span>' + fNum1(ind.pct_receita_propria_saude || 0) + '% da receita própria · <b>mínimo legal:</b> 15%</span>');
    setTxt('iepsCsap', fNum(Math.round(ind.taxa_internacao_csap_100k || 0)));
    setHtml('iepsPrenatal', fNum1(ind.pct_prenatal_adequado || 0) + ' <span class="unit">%</span>');
    setTxt('iepsPrenatalSub', '7 consultas ou mais · ' + fNum1(ind.pct_prenatal_zero || 0) + '% das gestantes não fizeram nenhuma');
  } else {
    vazioValores('iepsMed', 'iepsEnf', 'iepsEsf', 'iepsGasto', 'iepsCsap', 'iepsPrenatal');
  }

  const ans = ok(g(D, 'secoes.saude.planos_privados'));
  if (ans) {
    const compAns = (ans.competencia || '').split('-').reverse().join('/');
    setTxt('ansComp', compAns); setTxt('ansComp2', compAns);
    setHtml('ansCob', fNum1(ans.cobertura_pct || 0) + ' <span class="unit">%</span>');
    setTxt('ansSub', fNum(ans.medico_hospitalar || 0) + ' beneficiários médico-hospitalares (ANS) · o IEPS mede o mesmo em ' +
      (ind.cobertura_plano_privado != null ? fNum1(ind.cobertura_plano_privado) + '% para ' + (anosInd.cobertura_plano_privado || ieps && ieps.ano_max) : 'ano anterior'));
    const contr = ans.por_contratacao || [];
    const relevante = contr.filter(c => (c.beneficiarios || 0) >= 10);
    setHtml('ansList', relevante.length
      ? relevante.map(c => liRow(c.tipo, fNum(c.beneficiarios) + ' <span style="color:var(--text3)">(' + fNum1(pctDe(c.beneficiarios, ans.beneficiarios_total)) + '%)</span>')).join('') +
        liRow('Odontológico (à parte)', fNum(ans.odontologico || 0))
      : '');
    if (!relevante.length) vazioLista('ansList');
  } else {
    vazioValor('ansCob'); vazioLista('ansList');
  }

  const farm = ok(g(D, 'secoes.saude.farmacia_popular'));
  if (farm && farm.estabelecimentos_credenciados != null) setTxt('farmPopVal', fNum(farm.estabelecimentos_credenciados));
  else vazioValor('farmPopVal');

  const imun = ok(g(D, 'secoes.saude.imunizacao'));
  const imunSerie = (imun && imun.serie) || [];
  if (imunSerie.length > 1) {
    setTxt('imunAno', imunSerie[0].ano + '–' + imunSerie[imunSerie.length - 1].ano);
    const linhas = [
      ['Tríplice viral (D1)', 'cobertura_triplice_viral_d1', C.s1],
      ['Poliomielite', 'cobertura_poliomielite', C.s5],
      ['BCG', 'cobertura_bcg', C.s4],
      ['Pentavalente', 'cobertura_penta', C.s3],
      ['Cobertura total', 'cobertura_total', C.s8],
    ];
    criaGrafico(el_('imunChart'), {
      type: 'line', data: {
        labels: imunSerie.map(r => r.ano),
        datasets: linhas.map(([rot, k, cor]) => ({
          label: rot, data: imunSerie.map(r => r[k]),
          borderColor: cor, backgroundColor: cor, pointBackgroundColor: cor,
          ...lineStyle, pointRadius: 2, fill: false, spanGaps: false,
          borderWidth: k === 'cobertura_total' ? 3 : 1.8,
        }))
      },
      options: { ...chartOpts,
        plugins: { ...chartOpts.plugins,
          legend: { position: 'bottom', labels: { color: C.tick, usePointStyle: true, pointStyle: 'circle', padding: 8, boxWidth: 8, font: { size: 10 } } },
          tooltip: { ...chartOpts.plugins.tooltip, callbacks: { label: ctx => ctx.dataset.label + ': ' + (ctx.parsed.y == null ? 'sem registro' : fNum1(ctx.parsed.y) + '%') } } },
        scales: { x: { ticks: { color: C.muted }, grid: { color: C.grid } },
                  y: { ticks: { color: C.muted, callback: v => v + '%' }, grid: { color: C.grid } } } }
    });
  } else { vazioGrafico('imunChart'); }

  // =========================================================================
  // MORTALIDADE (SIM) e INTERNAÇÕES (SIH/AIH)
  // =========================================================================
  if (sim) {
    const anoSim = String(sim.ano || '');
    ['simAno', 'simAno2', 'simAno3', 'simAno4', 'simAno5', 'simAno6', 'simAno7'].forEach(id => setTxt(id, anoSim));
    setTxt('simObitos', fNum(sim.obitos || 0));
    setTxt('simTaxa', fNum1(sim.taxa_mortalidade_1000hab || 0) + ' óbitos por 1.000 habitantes');
    if (simInf && simInf.taxa_1000nv != null) {
      setTxt('simAno2', String(simInf.ano || ''));
      setHtml('simInfantil', fNum1(simInf.taxa_1000nv) + ' <span class="unit">/1.000 nasc.</span>');
      setTxt('simNeonatalSub', fNum(simInf.obitos || 0) + ' óbitos de menores de 1 ano' +
        (simInf.neonatais != null ? ', ' + fNum(simInf.neonatais) + ' deles no período neonatal' : '') +
        ' · ' + fNum(simInf.nascidos_vivos) + ' nascidos vivos');
    } else { vazioValor('simInfantil'); }
    setHtml('simIdade', fNum1(sim.idade_media_obito || 0) + ' <span class="unit">anos</span>');
    setTxt('simSexo', fNum(sim.homens || 0) + ' homens · ' + fNum(sim.mulheres || 0) + ' mulheres');
    setHtml('simMalDef', fNum1(pctDe(sim.mal_definidas, sim.obitos)) + ' <span class="unit">%</span>');

    const caps = sim.por_capitulo || [];
    if (caps.length) {
      criaGrafico(el_('simCapChart'), {
        type: 'bar', data: {
          labels: caps.map(c => capituloCurto(c.capitulo)),
          datasets: [{ data: caps.map(c => c.obitos), backgroundColor: C.s8, maxBarThickness: 16, borderRadius: 4, borderSkipped: 'start' }]
        },
        options: { ...chartOpts, indexAxis: 'y',
          plugins: { ...noLegend, tooltip: { ...chartOpts.plugins.tooltip,
            callbacks: { title: ctx => caps[ctx[0].dataIndex].capitulo, label: ctx => fNum(ctx.parsed.x) + ' óbitos (' + fNum1(pctDe(ctx.parsed.x, sim.obitos)) + '% do total)' } } },
          scales: { x: { ticks: { color: C.muted, callback: v => fNum(v) }, grid: { color: C.grid } },
                    y: { ticks: { color: C.tick, autoSkip: false, font: { size: 10 } }, grid: { display: false } } } }
      });
    } else { vazioGrafico('simCapChart'); }

    const serieSim = sim.serie || [];
    if (serieSim.length > 1) {
      setTxt('simSerieAno', serieSim[0].ano + '–' + serieSim[serieSim.length - 1].ano);
      criaGrafico(el_('simSerieChart'), {
        type: 'line', data: {
          labels: serieSim.map(r => r.ano),
          datasets: [
            // Escalas muito diferentes (milhares vs dezenas): encoding distinto evita
            // ler a linha vermelha como se fosse a série maior
            { label: 'Óbitos infantis', type: 'bar', data: serieSim.map(r => r.infantis), backgroundColor: C.s8 + '66', borderColor: C.s8, borderWidth: 1, maxBarThickness: 18, borderRadius: 3, yAxisID: 'y1', order: 2 },
            { label: 'Óbitos totais', data: serieSim.map(r => r.obitos), borderColor: C.s1, backgroundColor: C.s1fill, fill: true, pointBackgroundColor: C.s1, ...lineStyle, pointRadius: 3, yAxisID: 'y', order: 1 },
          ]
        },
        options: { ...chartOpts,
          scales: {
            x: { ticks: { color: C.muted }, grid: { display: false } },
            y: { position: 'left', ticks: { color: C.s1, callback: v => fNum(v) }, grid: { color: C.grid }, title: { display: true, text: 'Total', color: C.s1 } },
            y1: { position: 'right', beginAtZero: true, ticks: { color: C.s8, stepSize: 10 }, grid: { display: false }, title: { display: true, text: 'Infantis', color: C.s8 } },
          } }
      });
    } else { vazioGrafico('simSerieChart'); }

    const causas = sim.top_causas || [];
    setHtml('simCausasList', causas.length
      ? causas.map((c, i) =>
        '<tr class="com-barra" style="--p:' + (c.obitos / (causas[0].obitos || 1) * 100).toFixed(0) + '%"><td class="rank-name" title="' + c.descricao + '"><span class="rk-num">' + (i + 1) + '.</span><b>' + c.descricao + '</b> <span class="cod-badge so-celular">' + c.cid + '</span></td>' +
        '<td class="area cod"><span class="cod-badge">' + c.cid + '</span></td>' +
        '<td class="valor" data-label="Óbitos"><span class="val">' + fNum(c.obitos) + '</span></td></tr>').join('')
      : '');
    if (!causas.length) vazioTabela('simCausasList', 3);

    const extTot = sim.causas_externas || 0;
    setHtml('simExternasTotal', fNum(extTot) + ' <span class="unit">óbitos</span>');
    setTxt('simExternasSub', fNum1(pctDe(extTot, sim.obitos)) + '% de todos os óbitos do ano');
    // O restante (quedas, afogamentos, envenenamentos…) não vem detalhado na extração;
    // nomear a sobra é mais honesto do que deixar o gráfico somar menos que o total
    const extDet = [
      { k: 'Acidentes de transporte', v: sim.transporte || 0 },
      { k: 'Agressões', v: sim.agressoes || 0 },
      { k: 'Lesões autoprovocadas', v: sim.suicidios || 0 },
    ];
    const extResto = extTot - extDet.reduce((s, r) => s + r.v, 0);
    if (extResto > 0) extDet.push({ k: 'Demais', titulo: 'Demais causas externas (quedas, afogamentos, envenenamentos e outras)', v: extResto });
    extDet.sort((a, b) => b.v - a.v);
    barrasCategoria('simExternasBars', extDet, extTot, C.s6);
    setHtml('simMaternasList', liRow('Óbitos maternos <span style="color:var(--text3)">(cap. XV)</span>', fNum(sim.maternas || 0)));
  } else {
    vazioValores('simObitos', 'simInfantil', 'simIdade', 'simMalDef');
    vazioGrafico('simCapChart'); vazioGrafico('simSerieChart');
    vazioTabela('simCausasList', 3);
    vazioValor('simExternasTotal'); setTxt('simExternasSub', '');
    barrasCategoria('simExternasBars', [], 0); setHtml('simMaternasList', '');
  }

  if (sih) {
    const anoSih = String(sih.ano || '');
    ['sihAno', 'sihAno2', 'sihAno3', 'sihAno4', 'sihAno5'].forEach(id => setTxt(id, anoSih));
    setTxt('sihTotal', fNum(sih.internacoes || 0));
    const antSih = sih.ano_anterior;
    if (antSih && antSih.internacoes) {
      const dsih = (sih.internacoes / antSih.internacoes - 1) * 100;
      setCls('sihDelta', 'delta ' + (dsih >= 0 ? 'up' : 'down'));
      setHtml('sihDelta', (dsih >= 0 ? '▲ +' : '▼ ') + Math.abs(dsih).toFixed(1).replace('.', ',') + '% <span class="vs">vs ' + ((sih.ano || 0) - 1) + '</span>');
    }
    setHtml('sihValor', 'R$ ' + fNum1((sih.valor_total || 0) / 1e6) + ' <span class="unit">mi</span>');
    setTxt('sihValorMedio', 'R$ ' + fNum(Math.round(sih.valor_medio_aih || 0)) + ' por internação · ' + fNum(sih.diarias_uti || 0) + ' diárias de UTI' +
      (sih.permanencia_media != null ? ' · permanência média de ' + fNum1(sih.permanencia_media) + ' dias' : ''));
    setHtml('sihMort', fNum1(sih.taxa_mortalidade_hospitalar || 0) + ' <span class="unit">%</span>');
    setTxt('sihObitos', fNum(sih.obitos_hospitalares || 0) + ' óbitos durante a internação');
    setHtml('sihLocal', fNum1(sih.pct_no_municipio || 0) + ' <span class="unit">%</span>');
    setTxt('sihLocalSub', fNum(sih.no_municipio || 0) + ' das ' + fNum(sih.internacoes || 0) + ' internações · ' + fNum(sih.urgencia || 0) + ' foram urgência');

    const capsSih = sih.por_capitulo || [];
    if (capsSih.length) {
      criaGrafico(el_('sihCapChart'), {
        type: 'bar', data: {
          labels: capsSih.map(c => capituloCurto(c.capitulo)),
          datasets: [{ data: capsSih.map(c => c.internacoes), backgroundColor: C.s1, maxBarThickness: 16, borderRadius: 4, borderSkipped: 'start' }]
        },
        options: { ...chartOpts, indexAxis: 'y',
          plugins: { ...noLegend, tooltip: { ...chartOpts.plugins.tooltip,
            callbacks: { title: ctx => capsSih[ctx[0].dataIndex].capitulo,
              label: ctx => fNum(ctx.parsed.x) + ' internações · R$ ' + fNum1(capsSih[ctx.dataIndex].valor / 1e6) + ' mi' } } },
          scales: { x: { ticks: { color: C.muted, callback: v => fNum(v) }, grid: { color: C.grid } },
                    y: { ticks: { color: C.tick, autoSkip: false, font: { size: 10 } }, grid: { display: false } } } }
      });
    } else { vazioGrafico('sihCapChart'); }

    const serieSih = sih.serie || [];
    if (serieSih.length > 1) {
      setTxt('sihSerieAno', serieSih[0].ano + '–' + serieSih[serieSih.length - 1].ano);
      criaGrafico(el_('sihSerieChart'), {
        type: 'bar', data: {
          labels: serieSih.map(r => r.ano),
          datasets: [
            { label: 'Internações', data: serieSih.map(r => r.internacoes), backgroundColor: C.s1, maxBarThickness: 20, borderRadius: 3, yAxisID: 'y', order: 2 },
            { label: 'Gasto SUS (R$ mi)', type: 'line', data: serieSih.map(r => r.valor / 1e6), borderColor: C.s4, backgroundColor: C.s4, pointBackgroundColor: C.s4, ...lineStyle, pointRadius: 3, fill: false, yAxisID: 'y1', order: 1 },
          ]
        },
        options: { ...chartOpts,
          plugins: { ...chartOpts.plugins, tooltip: { ...chartOpts.plugins.tooltip,
            callbacks: { label: ctx => ctx.datasetIndex === 0 ? fNum(ctx.parsed.y) + ' internações' : 'R$ ' + fNum1(ctx.parsed.y) + ' mi' } } },
          scales: {
            x: { ticks: { color: C.muted }, grid: { display: false } },
            y: { position: 'left', ticks: { color: C.s1, callback: v => fNum(v) }, grid: { color: C.grid } },
            y1: { position: 'right', ticks: { color: C.s4, callback: v => 'R$ ' + fNum(v) + ' mi' }, grid: { display: false } },
          } }
      });
    } else { vazioGrafico('sihSerieChart'); }
  } else {
    vazioValores('sihTotal', 'sihValor', 'sihMort', 'sihLocal');
    vazioGrafico('sihCapChart'); vazioGrafico('sihSerieChart');
  }

  // =========================================================================
  // SEGURANÇA — complementos ISP e violência notificada (SINAN/VIVA)
  // =========================================================================
  if (txSeg.taxa_estupro != null) {
    setHtml('segEstBench', '<span>' + fNum1(txSeg.taxa_estupro) + '/100k (' + (txSeg.ano || '') + ') · <b>RJ:</b> ' + fNum1(txSegUf.taxa_estupro || 0) + '</span>');
  }
  if (txSeg.ano) {
    setTxt('segAno10', String(txSeg.ano));
    setTxt('taxasNota', 'As taxas por 100 mil habitantes do ISP têm ano-base próprio (' + txSeg.ano +
      '), anterior ao das ocorrências absolutas acima (' + (g(D, 'secoes.seguranca.isp_rj.ano') || '—') + ') — não são a mesma safra de dado.');
  }
  if (txSeg.taxa_roubo_veiculo == null) {
    setHtml('segRouboBench', '<span>Sem taxa/100k no ISP · <b>RJ:</b> ' + fNum1(txSegUf.taxa_roubo_veiculo || 0) + '/100k</span>');
  }

  if (viol) {
    const anoV = String(viol.ano || '');
    ['violAno', 'violAno2', 'violAno3', 'violAno4', 'violAno5', 'violAno6'].forEach(id => setTxt(id, anoV));
    setTxt('violTotal', fNum(viol.notificacoes || 0));
    setTxt('violFem', fNum(viol.feminino || 0));
    setTxt('violFemSub', fNum1(viol.pct_feminino || 0) + '% das notificações · ' + fNum(viol.masculino || 0) + ' do sexo masculino');
    setTxt('violNegros', fNum(viol.negros || 0));
    setTxt('violNegrosSub', fNum1(viol.pct_negros || 0) + '% · ' + (viol.nota_raca || '') + ' · ' + fNum(viol.raca_ignorada || 0) + ' sem raça informada');
    setTxt('violAuto', fNum(viol.autoprovocadas || 0));
    setTxt('violAutoSub', fNum1(pctDe(viol.autoprovocadas, viol.notificacoes)) + '% das notificações — tentativa de suicídio e automutilação');

    const serieV = viol.serie || [];
    if (serieV.length > 1) {
      setTxt('violSerieAno', serieV[0].ano + '–' + serieV[serieV.length - 1].ano);
      criaGrafico(el_('violSerieChart'), {
        type: 'line', data: {
          labels: serieV.map(r => r.ano),
          datasets: [
            { label: 'Total notificado', data: serieV.map(r => r.notificacoes), borderColor: C.s1, backgroundColor: C.s1fill, fill: true, pointBackgroundColor: C.s1, ...lineStyle, pointRadius: 3 },
            { label: 'Autoprovocadas', data: serieV.map(r => r.autoprovocadas), borderColor: C.s8, backgroundColor: C.s8, pointBackgroundColor: C.s8, ...lineStyle, pointRadius: 3, fill: false },
          ]
        },
        options: { ...chartOpts,
          plugins: { ...chartOpts.plugins,
            legend: { position: 'bottom', labels: { color: C.tick, usePointStyle: true, pointStyle: 'circle', padding: 8, boxWidth: 8, font: { size: 10 } } } },
          scales: { x: { ticks: { color: C.muted }, grid: { color: C.grid } },
                    y: { beginAtZero: true, ticks: { color: C.muted, callback: v => fNum(v) }, grid: { color: C.grid } } } }
      });
    } else { vazioGrafico('violSerieChart'); }

    const tipos = [
      ['Física', viol.fisica], ['Negligência', viol.negligencia], ['Sexual', viol.sexual],
      ['Psicológica', viol.psicologica], ['Financeira', viol.financeira], ['Tortura', viol.tortura],
      ['Por arma de fogo', viol.arma_fogo], ['Tráfico de pessoas', viol.trafico_humano],
      ['Trabalho infantil', viol.infantil_trabalho],
    ].filter(t => (t[1] || 0) > 0).sort((a, b) => b[1] - a[1]);
    if (tipos.length) {
      criaGrafico(el_('violTipoChart'), {
        type: 'bar', data: {
          labels: tipos.map(t => t[0]),
          datasets: [{ data: tipos.map(t => t[1]), backgroundColor: C.s3, maxBarThickness: 16, borderRadius: 4, borderSkipped: 'start' }]
        },
        options: { ...chartOpts, indexAxis: 'y',
          plugins: { ...noLegend, tooltip: { ...chartOpts.plugins.tooltip,
            callbacks: { label: ctx => fNum(ctx.parsed.x) + ' notificações' } } },
          scales: { x: { ticks: { color: C.muted, callback: v => fNum(v) }, grid: { color: C.grid } },
                    y: { ticks: { color: C.tick, autoSkip: false, font: { size: 11 } }, grid: { display: false } } } }
      });
    } else { vazioGrafico('violTipoChart', 'Nenhum tipo de violência com registro no ano'); }

    const locais = agrupa(viol.por_local, 'local', 'n');
    barrasCategoria('violLocalBars', locais, viol.notificacoes, C.s3);

    // O SINAN devolve "Ignorado" em mais de um código — agrupar antes de exibir.
    // Ciclo de vida é ordinal: ordenar por volume destruiria o eixo etário.
    const ORDEM_CICLO = ['Criança (0-9)', 'Adolescente (10-19)', 'Jovem (20-24)', 'Adulto (25-59)', 'Idoso (60+)'];
    const ciclos = agrupa(viol.por_ciclo_vida, 'ciclo', 'n').sort((a, b) => {
      const ia = ORDEM_CICLO.indexOf(a.k), ib = ORDEM_CICLO.indexOf(b.k);
      return (ia < 0 ? 99 : ia) - (ib < 0 ? 99 : ib);
    });
    barrasCategoria('violCicloBars', ciclos, viol.notificacoes, C.s8);
  } else {
    vazioValores('violTotal', 'violFem', 'violNegros', 'violAuto');
    vazioGrafico('violSerieChart'); vazioGrafico('violTipoChart');
    barrasCategoria('violLocalBars', [], 0); barrasCategoria('violCicloBars', [], 0);
  }

  // =========================================================================
  // POLÍTICA — Câmara Municipal, perfil de candidatos, financiamento
  // =========================================================================
  const cam = ok(g(D, 'secoes.politica.camara_municipal'));
  if (cam) {
    const anoCam = String(cam.ano || '');
    ['camAno', 'camAno2', 'camAno3'].forEach(id => setTxt(id, anoCam));
    const banc = (cam.bancadas || []).slice().sort((a, b) => (b.cadeiras - a.cadeiras) || (b.votos - a.votos));
    setTxt('camTotal', '· ' + (cam.cadeiras_total || banc.reduce((s, b) => s + b.cadeiras, 0)) + ' cadeiras');
    if (banc.length) {
      criaGrafico(el_('camaraChart'), {
        type: 'bar', data: {
          labels: banc.map(b => b.partido),
          datasets: [{ data: banc.map(b => b.cadeiras), backgroundColor: C.s1, maxBarThickness: 14, borderRadius: 3, borderSkipped: 'start' }]
        },
        options: { ...chartOpts, indexAxis: 'y',
          plugins: { ...noLegend, tooltip: { ...chartOpts.plugins.tooltip,
            callbacks: { label: ctx => banc[ctx.dataIndex].cadeiras + ' cadeira(s) · ' + fNum(banc[ctx.dataIndex].votos) + ' votos de legenda' } } },
          scales: { x: { beginAtZero: true, ticks: { color: C.muted, stepSize: 1, precision: 0 }, grid: { color: C.grid } },
                    y: { ticks: { color: C.tick, autoSkip: false, font: { size: 10 } }, grid: { display: false } } } }
      });
    } else { vazioGrafico('camaraChart'); }

    const pc = cam.perfil_candidatos || {};
    setHtml('candPerfilList', pc.candidatos
      ? liRow('Candidatos', fNum(pc.candidatos)) +
        liRow('Mulheres', fNum(pc.feminino || 0) + ' <span style="color:var(--text3)">(' + fNum1(pctDe(pc.feminino, pc.candidatos)) + '%)</span>') +
        liRow('Negros (pretos + pardos)', fNum(pc.negros || 0) + ' <span style="color:var(--text3)">(' + fNum1(pctDe(pc.negros, pc.candidatos)) + '%)</span>') +
        liRow('Idade média', fNum1(pc.idade_media || 0) + ' anos')
      : '');
    if (!pc.candidatos) vazioLista('candPerfilList');

    const fin2 = cam.financiamento || [];
    setHtml('financList', fin2.length
      ? fin2.map(f => liRow(f.cargo.charAt(0).toUpperCase() + f.cargo.slice(1) + ' <span style="color:var(--text3)">(' + fNum(f.candidatos) + ')</span>',
          'R$ ' + fNum1((f.receita || 0) / 1e6) + ' mi')).join('') +
        liRow('Média por candidato', 'R$ ' + fNum(Math.round(
          fin2.reduce((s, f) => s + f.receita, 0) / Math.max(1, fin2.reduce((s, f) => s + f.candidatos, 0)))))
      : '');
    if (!fin2.length) vazioLista('financList');
  } else {
    vazioGrafico('camaraChart'); vazioLista('candPerfilList'); vazioLista('financList');
  }

  const dep = ok(g(D, 'secoes.politica.deputados_nascidos'));
  const deps = (dep && dep.deputados) || [];
  setHtml('depNascList', deps.length
    ? deps.map(d2 => liRow(titulo(d2.nome),
        (d2.nascimento ? d2.nascimento.slice(0, 4) : '—') + (d2.falecido ? ' <span style="color:var(--text3)">†</span>' : ''))).join('')
    : '');
  if (!deps.length) vazioLista('depNascList', 'Nenhum deputado federal registrado como nascido aqui');

  // =========================================================================
  // TRANSPARÊNCIA — Querido Diário, IFGF, CAPAG, servidores, consumidor
  // =========================================================================
  const qd = ok(g(D, 'secoes.transparencia.diarios_oficiais'));
  if (qd && qd.total_edicoes) {
    const serieQd = qd.serie || [];
    setTxt('qdAno', serieQd.length ? serieQd[0].ano + '–' + serieQd[serieQd.length - 1].ano : '');
    setHtml('qdList',
      liRow('Edições coletadas', fNum(qd.total_edicoes)) +
      liRow('Última edição', qd.ultima_edicao ? qd.ultima_edicao.split('-').reverse().join('/') : '—') +
      serieQd.slice().reverse().map(r => liRow(r.ano, fNum(r.edicoes) + ' edições <span style="color:var(--text3)">(' + fNum(r.extras) + ' extras)</span>')).join(''));
  } else {
    vazioLista('qdList', 'Município ainda não coberto pelo Querido Diário');
  }

  const fiscal = ok(g(D, 'secoes.transparencia.fiscal'));
  const ifgf = (fiscal && fiscal.ifgf) || [];
  if (ifgf.length > 1) {
    setTxt('ifgfAno', ifgf[0].ano + '–' + ifgf[ifgf.length - 1].ano);
    criaGrafico(el_('ifgfChart'), {
      type: 'line', data: {
        labels: ifgf.map(r => r.ano),
        datasets: [{ label: 'IFGF', data: ifgf.map(r => r.indice), borderColor: C.s1, backgroundColor: C.s1fill, fill: true, pointBackgroundColor: C.s1, ...lineStyle, pointRadius: 3 }]
      },
      options: { ...chartOpts, plugins: { ...noLegend, tooltip: { ...chartOpts.plugins.tooltip,
        callbacks: { label: ctx => {
          const r = ifgf[ctx.dataIndex];
          return 'IFGF ' + fmt2(r.indice) + ' · ' + r.ranking_estadual + 'º no RJ, ' + fNum(r.ranking_nacional) + 'º no país';
        } } } },
        scales: { x: { ticks: { color: C.muted }, grid: { color: C.grid } },
                  y: { min: 0, max: 1, ticks: { color: C.muted, callback: v => fmt2(v) }, grid: { color: C.grid } } } }
    });
    const ultIfgf = ifgf[ifgf.length - 1];
    setTxt('ifgfSub', 'Escala 0–1 · ' + ultIfgf.ano + ': ' + fmt2(ultIfgf.indice) + ' — ' + ultIfgf.ranking_estadual +
      'º entre os municípios do RJ e ' + fNum(ultIfgf.ranking_nacional) + 'º no país. Acima de 0,8 é gestão de excelência; abaixo de 0,4, crítica.');
  } else { vazioGrafico('ifgfChart'); }

  const capag = (fiscal && fiscal.capag) || null;
  if (capag) {
    // A é boa, B aceitável, C/D preocupante — a letra sozinha não diz isso a quem lê
    const CLASSE_CAPAG = { A: 'st-good', B: 'st-good', C: 'st-warn', D: 'st-crit' };
    const nota = n => n
      ? '<span class="status ' + (CLASSE_CAPAG[n] || 'st-warn') + '">' + n + '</span>'
      : '<span class="empty" style="padding:0">não divulgada</span>';
    setHtml('capagList',
      liRow('Nota geral (CAPAG)', nota(capag.capag)) +
      liRow('Endividamento', nota(capag.nota_endividamento)) +
      liRow('Poupança corrente', nota(capag.nota_poupanca_corrente)) +
      liRow('Liquidez', nota(capag.nota_liquidez)));
  } else { vazioLista('capagList'); }

  const serv = ok(g(D, 'secoes.transparencia.servidores'));
  if (serv && serv.adm_direta != null) {
    setTxt('servAno', String(serv.ano || ''));
    setHtml('servList',
      liRow('Administração direta', fNum(serv.adm_direta)) +
      liRow('Estatutários', fNum(serv.estatutario_adm_direta || 0)) +
      liRow('Celetistas', fNum(serv.clt_adm_direta || 0)) +
      liRow('Comissionados', fNum(serv.comissionado_adm_direta || 0) + ' <span style="color:var(--text3)">(' + fNum1(pctDe(serv.comissionado_adm_direta, serv.adm_direta)) + '%)</span>') +
      liRow('Administração indireta', fNum(serv.adm_indireta || 0)));
  } else { vazioLista('servList'); }

  const cons = ok(g(D, 'secoes.transparencia.consumidor'));
  const serieCons = (cons && cons.serie) || [];
  if (serieCons.length > 1) {
    setTxt('consAno', serieCons[0].ano + '–' + serieCons[serieCons.length - 1].ano);
    setTxt('consAno2', String(cons.ano || ''));
    criaGrafico(el_('consChart'), {
      type: 'bar', data: {
        labels: serieCons.map(r => r.ano),
        datasets: [
          { label: 'Reclamações', data: serieCons.map(r => r.reclamacoes), backgroundColor: C.s1, maxBarThickness: 18, borderRadius: 3, yAxisID: 'y', order: 2 },
          { label: 'Nota média (0–5)', type: 'line', data: serieCons.map(r => r.nota_media), borderColor: C.s4, backgroundColor: C.s4, pointBackgroundColor: C.s4, ...lineStyle, pointRadius: 3, fill: false, yAxisID: 'y1', order: 1 },
        ]
      },
      options: { ...chartOpts,
        plugins: { ...chartOpts.plugins,
          legend: { position: 'bottom', labels: { color: C.tick, usePointStyle: true, pointStyle: 'circle', padding: 8, boxWidth: 8, font: { size: 10 } } },
          tooltip: { ...chartOpts.plugins.tooltip,
            callbacks: { label: ctx => ctx.datasetIndex === 0 ? fNum(ctx.parsed.y) + ' reclamações' : 'nota ' + fmt2(ctx.parsed.y) } } },
        scales: {
          x: { ticks: { color: C.muted }, grid: { display: false } },
          y: { position: 'left', beginAtZero: true, ticks: { color: C.s1, callback: v => fNum(v) }, grid: { color: C.grid } },
          y1: { position: 'right', min: 0, max: 5, ticks: { color: C.s4, callback: v => fmt2(v) }, grid: { display: false } },
        } }
    });
    const ultCons = serieCons.find(r => r.ano === cons.ano) || serieCons[serieCons.length - 1];
    setTxt('consSub', ultCons.ano + ': ' + fNum(ultCons.reclamacoes) + ' reclamações, ' + fNum1(ultCons.pct_respondida) +
      '% respondidas pelas empresas, nota média ' + fmt2(ultCons.nota_media) + ' de 5. O ano corrente pode estar parcial.');
  } else { vazioGrafico('consChart'); }

  const segms = (cons && cons.top_segmentos) || [];
  if (segms.length) {
    const totSeg = segms.reduce((s, r) => s + (r.reclamacoes || 0), 0);
    criaGrafico(el_('consSegChart'), {
      type: 'bar', data: {
        labels: segms.map(s => s.segmento
          .replace('Bancos, Financeiras e Administradoras de Cartão', 'Bancos e cartões')
          .replace(/^Operadoras de Telecomunicações.*/, 'Telecomunicações')
          .replace('Provedores de Conteúdo e Outros Serviços na Internet', 'Serviços de internet')
          .replace(/^(.*)$/, m => truncaPalavra(m, 30))
          ),
        datasets: [{ data: segms.map(s => s.reclamacoes), backgroundColor: C.s1, maxBarThickness: 16, borderRadius: 4, borderSkipped: 'start' }]
      },
      options: { ...chartOpts, indexAxis: 'y',
        plugins: { ...noLegend, tooltip: { ...chartOpts.plugins.tooltip,
          callbacks: { title: ctx => segms[ctx[0].dataIndex].segmento,
            label: ctx => fNum(ctx.parsed.x) + ' reclamações (' + fNum1(pctDe(ctx.parsed.x, totSeg)) + '% do top ' + segms.length + ')' } } },
        scales: { x: { beginAtZero: true, ticks: { color: C.muted, callback: v => fNum(v) }, grid: { color: C.grid } },
                  y: { ticks: { color: C.tick, autoSkip: false, font: { size: 10 } }, grid: { display: false } } } }
    });
  } else { vazioGrafico('consSegChart'); }
  const emps = (cons && cons.top_empresas) || [];
  setHtml('consEmpList', emps.length
    ? emps.map(e => liRow(e.empresa, fNum(e.reclamacoes))).join('')
    : '');
  if (!emps.length) vazioLista('consEmpList');

  // =========================================================================
  // RECURSOS FEDERAIS — emendas, contratos e licitações da União
  // =========================================================================
  const emd = ok(g(D, 'secoes.transparencia.emendas'));
  const serieEmd = (emd && emd.serie) || [];
  if (serieEmd.length) {
    const ultEmd = serieEmd.find(r => r.ano === emd.ano) || serieEmd[serieEmd.length - 1];
    setTxt('emdAno', String(ultEmd.ano)); setTxt('emdAno2', String(ultEmd.ano));
    setHtml('emdPago', 'R$ ' + fNum1((ultEmd.pago || 0) / 1e6) + ' <span class="unit">mi</span>');
    setTxt('emdSub', fNum(ultEmd.emendas || 0) + ' emendas destinadas ao município em ' + ultEmd.ano);
    setHtml('emdEmp', 'R$ ' + fNum1((ultEmd.empenhado || 0) / 1e6) + ' <span class="unit">mi</span>');
    setTxt('emdExecSub', ultEmd.empenhado ? fNum1(pctDe(ultEmd.pago, ultEmd.empenhado)) + '% do empenhado já foi pago' : '');
    setTxt('emdSerieAno', serieEmd[0].ano + '–' + serieEmd[serieEmd.length - 1].ano);
    criaGrafico(el_('emdChart'), {
      type: 'bar', data: {
        labels: serieEmd.map(r => r.ano),
        datasets: [
          { label: 'Empenhado', data: serieEmd.map(r => r.empenhado / 1e6), backgroundColor: C.s1, maxBarThickness: 16, borderRadius: 3 },
          { label: 'Pago', data: serieEmd.map(r => r.pago / 1e6), backgroundColor: C.s5, maxBarThickness: 16, borderRadius: 3 },
        ]
      },
      options: { ...chartOpts,
        plugins: { ...chartOpts.plugins,
          legend: { position: 'bottom', labels: { color: C.tick, usePointStyle: true, pointStyle: 'circle', padding: 8, boxWidth: 8, font: { size: 10 } } },
          tooltip: { ...chartOpts.plugins.tooltip, callbacks: { label: ctx => ctx.dataset.label + ': R$ ' + fNum1(ctx.parsed.y) + ' mi' } } },
        scales: { x: { ticks: { color: C.muted }, grid: { display: false } },
                  y: { beginAtZero: true, ticks: { color: C.muted, callback: v => 'R$ ' + fNum(v) + ' mi' }, grid: { color: C.grid } } } }
    });
    setTxt('emdJanela', emd.janela_autores || '');
    const autores = emd.top_autores || [];
    setHtml('emdAutoresList', autores.length
      ? autores.map((a, i) =>
        '<tr><td class="rank-name" title="' + a.autor + '"><span class="rk-num">' + (i + 1) + '.</span><b>' +
        titulo(a.autor) + '</b></td>' +
        '<td class="area">' + fNum(a.emendas) + ' emenda(s)</td>' +
        '<td class="valor" data-label="Pago"><span class="val">R$ ' + fNum1(a.pago / 1e6) + ' mi</span></td></tr>').join('')
      : '');
    if (!autores.length) vazioTabela('emdAutoresList', 3);
    const funcoes = emd.por_funcao || [];
    setHtml('emdFuncaoList', funcoes.length
      ? funcoes.map(f => liRow(f.funcao, 'R$ ' + fNum1((f.pago || 0) / 1e6) + ' mi')).join('')
      : '');
    if (!funcoes.length) vazioLista('emdFuncaoList');
  } else {
    vazioValores('emdPago', 'emdEmp'); vazioGrafico('emdChart');
    vazioTabela('emdAutoresList', 3); vazioLista('emdFuncaoList');
  }

  const compras = ok(g(D, 'secoes.transparencia.compras_federais'));
  const forn = (compras && compras.fornecedores_locais) || null;
  const serieForn = (forn && forn.serie) || [];
  if (serieForn.length) {
    const totForn = serieForn.reduce((s, r) => s + (r.valor || 0), 0);
    const nContratos = serieForn.reduce((s, r) => s + (r.contratos || 0), 0);
    const janelaForn = serieForn[0].ano + '–' + serieForn[serieForn.length - 1].ano;
    setTxt('fornAno', janelaForn); setTxt('fornJanela', janelaForn);
    setHtml('fornValor', 'R$ ' + fNum1(totForn / 1e6) + ' <span class="unit">mi</span>');
    setTxt('fornSub', fNum(nContratos) + ' contratos no período · CNPJ localizado no município (snapshot ' + (forn.snapshot_cnpj || '—') + ')');
    const topForn = forn.top || [];
    setHtml('fornList', topForn.length
      ? topForn.map((f, i) =>
        '<tr><td class="rank-name" title="' + f.empresa + '"><span class="rk-num">' + (i + 1) + '.</span><b>' +
        titulo(f.empresa) + '</b></td>' +
        '<td class="area">' + fNum(f.contratos) + ' contrato(s)</td>' +
        '<td class="valor" data-label="Valor"><span class="val">R$ ' + fNum1(f.valor / 1e6) + ' mi</span></td></tr>').join('')
      : '');
    if (!topForn.length) vazioTabela('fornList', 3);
  } else {
    vazioValor('fornValor'); vazioTabela('fornList', 3);
  }

  const lic = (compras && compras.licitacoes_no_municipio) || null;
  const serieLic = (lic && lic.serie) || [];
  if (serieLic.length) {
    const janelaLic = serieLic[0].ano + '–' + serieLic[serieLic.length - 1].ano;
    const orgaos = lic.por_orgao || [];
    // A série por ano e o total por órgão não fecham: algumas licitações vêm sem ano
    // na fonte. O total oficial é o do órgão; a diferença é dita, não escondida.
    const nSerie = serieLic.reduce((s, r) => s + (r.licitacoes || 0), 0);
    const nOrgao = orgaos.reduce((s, r) => s + (r.licitacoes || 0), 0);
    const totLic = orgaos.length
      ? orgaos.reduce((s, r) => s + (r.valor || 0), 0)
      : serieLic.reduce((s, r) => s + (r.valor || 0), 0);
    const nLic = nOrgao || nSerie;
    setTxt('licAno', janelaLic); setTxt('licJanela', janelaLic);
    setHtml('licValor', 'R$ ' + fNum1(totLic / 1e6) + ' <span class="unit">mi</span>');
    setTxt('licSub', fNum(nLic) + ' licitações no período');
    setHtml('licOrgaoList', orgaos.length
      ? orgaos.map(o => liRow(o.orgao, fNum(o.licitacoes) + ' licit. · R$ ' + fNum1((o.valor || 0) / 1e6) + ' mi')).join('')
      : '');
    if (!orgaos.length) vazioLista('licOrgaoList');
    setTxt('licNota', nOrgao > nSerie
      ? fNum(nOrgao - nSerie) + ' licitações não trazem ano na fonte e ficam fora do gráfico por ano'
      : '');
    barrasCategoria('licAnoBars',
      serieLic.slice().reverse().map(r => ({ k: String(r.ano), v: r.valor || 0 })),
      0, C.s5, { fmtValor: v => 'R$ ' + fNum1(v / 1e6) + ' mi' });
  } else {
    vazioValor('licValor'); vazioLista('licOrgaoList');
    barrasCategoria('licAnoBars', [], 0); setTxt('licNota', '');
  }

  // =========================================================================
  // BENEFÍCIOS — Cadastro Único
  // =========================================================================
  // O painel do MDS (cadunico_mds) vai até o mês corrente; o br_mc_indicadores
  // parou em 2020 e só entra quando o MDS não cobre o município.
  const cadMds = ok(g(D, 'secoes.beneficios.cadunico_mds'));
  const cad = ok(g(D, 'secoes.beneficios.cadastro_unico'));
  const mmaa = s => (s || '').split('-').reverse().join('/');
  const popAtual = (() => { const s = g(D, 'secoes.demografia.populacao_serie') || []; return s.length ? s[s.length - 1].populacao : null; })();
  const cadIds = ['cadAno', 'cadAno2'];
  if (cadMds && cadMds.familias) {
    const comp = mmaa(cadMds.competencia);
    cadIds.forEach(id => { setTxt(id, comp); const e = el_(id); if (e) e.classList.remove('old'); });
    const pes = cadMds.pessoas || {}, fam = cadMds.familias;
    setTxt('cadPessoas', fNum(pes.total));
    setTxt('cadPctSub', popAtual ? fNum1(pctDe(pes.total, popAtual)) + '% da população estimada' : '');
    setTxt('cadFamilias', fNum(fam.total));
    setTxt('cadFamSub', fNum(fam.pobreza) + ' em situação de pobreza (' + fNum1(pctDe(fam.pobreza, fam.total)) + '%)');
    const at = cadMds.atualizacao || {};
    setHtml('cadAtualList',
      (at.taxa != null ? liRow('Cadastros atualizados', fNum1(at.taxa) + '%') : '') +
      (cadMds.local ? liRow('Famílias em área rural', fNum(cadMds.local.rural) + ' (' + fNum1(pctDe(cadMds.local.rural, fam.total)) + '%)') : '') +
      (cadMds.trabalho_infantil && cadMds.trabalho_infantil.pessoas != null
        ? liRow('Trabalho infantil identificado (' + mmaa(cadMds.trabalho_infantil.competencia) + ')', fNum(cadMds.trabalho_infantil.pessoas) + ' pessoa(s)') : ''));

    setTxt('cadRendaAno', comp);
    barrasCategoria('cadRendaBars', [
      { k: 'Pobreza', v: fam.pobreza || 0, titulo: 'Renda per capita até a linha do Bolsa Família (R$ 218)' },
      { k: 'Baixa renda', v: fam.baixa_renda || 0, titulo: 'Acima da linha de pobreza, até ½ salário-mínimo per capita' },
      { k: 'Acima de ½ SM', v: fam.acima_meio_sm || 0 },
    ], fam.total, C.s4);
    const sp = cadMds.saida_pobreza_pbf || {};
    setTxt('cadSaidaSub', sp.saem != null
      ? 'Com o Bolsa Família, ' + fNum(sp.saem) + ' famílias beneficiárias passam da linha de pobreza; ' +
        fNum(sp.permanecem) + ' continuam abaixo (' + mmaa(sp.competencia) + ')' : '');

    const serie = cadMds.serie_familias || [];
    if (serie.length) {
      setTxt('cadSerieAno', serie[0].ano + '–' + serie[serie.length - 1].ano);
      criaGrafico(el_('cadSerieChart'), {
        type: 'line', data: { labels: serie.map(r => String(r.ano)),
          datasets: [{ label: 'Famílias', data: serie.map(r => r.familias), borderColor: C.s4, backgroundColor: C.s4fill, fill: true, pointBackgroundColor: C.s4, ...lineStyle, pointRadius: 3 }] },
        options: { ...chartOpts, plugins: { ...noLegend, tooltip: { ...chartOpts.plugins.tooltip,
          callbacks: { label: ctx => fNum(ctx.parsed.y) + ' famílias (' + mmaa(serie[ctx.dataIndex].ref) + ')' } } },
          scales: { ...chartOpts.scales, y: { ...chartOpts.scales.y, ticks: { color: C.muted, callback: v => fNum(v) } } } }
      });
    } else vazioGrafico('cadSerieChart');

    const rs = cadMds.responsavel_sexo || {};
    setTxt('cadRespAno', comp);
    barrasCategoria('cadSexoBars', [{ k: 'Mulher', v: rs.feminino || 0 }, { k: 'Homem', v: rs.masculino || 0 }],
      (rs.feminino || 0) + (rs.masculino || 0), C.s3);
    const raca = (cadMds.raca_cor || []).filter(r => r.pessoas);
    barrasCategoria('cadRacaBars', raca.map(r => ({ k: r.raca, v: r.pessoas })),
      raca.reduce((t, r) => t + r.pessoas, 0), C.s7);

    const gp = cadMds.grupos_especificos || {};
    setTxt('cadGpteAno', comp);
    setTxt('cadGpteSub', gp.total ? fNum(gp.total) + ' famílias (' + fNum1(pctDe(gp.total, fam.total)) + '% do cadastro) — uma família pode estar em mais de um grupo' : '');
    barrasCategoria('cadGpteBars', (gp.lista || []).slice(0, 8).map(r => ({ k: r.grupo, v: r.familias, titulo: r.grupo })),
      0, C.s5, { fmtValor: v => fNum(v), msgVazio: 'Nenhuma família de grupo específico cadastrada' });

    const rua = cadMds.situacao_rua || {};
    setTxt('cadRuaAno', mmaa(rua.competencia));
    if (rua.pessoas != null) {
      setHtml('cadRuaList',
        liRow('Pessoas em situação de rua', fNum(rua.pessoas)) +
        liRow('Famílias', fNum(rua.familias)) +
        (rua.pct_atendimento != null ? liRow('Com atendimento institucional', fNum1(rua.pct_atendimento) + '%') : '') +
        (popAtual ? liRow('Por 10 mil habitantes', fNum1(rua.pessoas / popAtual * 1e4)) : ''));
    } else vazioLista('cadRuaList');

    const esg = cadMds.esgoto || [];
    const esgTot = esg.reduce((t, r) => t + (r.familias || 0), 0);
    setTxt('cadEsgAno', comp);
    barrasCategoria('cadEsgBars', esg.filter(r => r.familias).map(r => ({ k: r.forma, v: r.familias, titulo: r.forma })).sort((a, b) => b.v - a.v),
      esgTot, C.s1, { soPct: true });
  } else {
    if (cad) {
      const compCad = mmaa(cad.competencia);
      cadIds.forEach(id => setTxt(id, compCad));
      setTxt('cadPessoas', fNum(cad.pessoas_cadastradas || 0));
      setTxt('cadPctSub', fNum1(cad.pct_populacao || 0) + '% da população na competência');
      setTxt('cadFamilias', fNum(cad.familias_cadastradas || 0));
      setTxt('cadFamSub', fNum(cad.familias_pbf || 0) + ' delas recebiam Bolsa Família (' +
        fNum1(pctDe(cad.familias_pbf, cad.familias_cadastradas)) + '%)');
    } else {
      vazioValores('cadPessoas', 'cadFamilias');
    }
    vazioLista('cadAtualList'); vazioLista('cadRuaList'); vazioGrafico('cadSerieChart');
    ['cadRendaBars', 'cadSexoBars', 'cadRacaBars', 'cadGpteBars', 'cadEsgBars'].forEach(id => barrasCategoria(id, [], 0));
  }

  // =========================================================================
  // AGROPECUÁRIA — assentamentos do INCRA
  // =========================================================================
  const assent = ok(g(D, 'secoes.agropecuaria.assentamentos'));
  if (assent) {
    setTxt('assentN', fNum(assent.total));
    setTxt('assentSub', assent.total
      ? fNum(assent.familias) + ' famílias assentadas · ' + fNum(Math.round(assent.area_ha)) + ' ha'
      : 'Nenhum projeto de assentamento no município');
    const rowAssent = (a, i) => '<tr>' +
      '<td class="rank-name" title="' + a.nome + ' · ' + (a.obtencao || '') + '"><span class="rk-num">' + (i + 1) + '.</span><b>' + titulo(a.nome).replace(/^(P[A-Z]?[a-z]?) /, m => m.toUpperCase()) + '</b></td>' +
      '<td class="area">' + a.fase + ' · ' + String(a.criacao || '').slice(-4) + '</td>' +
      '<td class="valor"><span class="val">' + fNum(a.familias) + '</span></td></tr>';
    const proj = assent.projetos || [];
    if (proj.length) setHtml('assentList', proj.slice(0, 5).map(rowAssent).join(''));
    else vazioTabela('assentList', 3, 'Nenhum projeto de assentamento do INCRA no município');
    setHtml('assentDetList', proj.slice(5).map((a, i) => rowAssent(a, i + 5)).join(''));
    const mais = el_('assentMore'); if (mais) mais.hidden = proj.length <= 5;
  } else {
    vazioValor('assentN'); vazioTabela('assentList', 3);
    const mais = el_('assentMore'); if (mais) mais.hidden = true;
  }

  // =========================================================================
  // ENERGIA & FROTA
  // =========================================================================
  const TIPO_VEICULO = { automovel: 'Automóvel', motocicleta: 'Motocicleta', caminhonete: 'Caminhonete',
    camioneta: 'Camioneta', motoneta: 'Motoneta', caminhao: 'Caminhão', reboque: 'Reboque',
    utilitario: 'Utilitário', semi_reboque: 'Semirreboque', micro_onibus: 'Micro-ônibus',
    caminhao_trator: 'Caminhão-trator', onibus: 'Ônibus', ciclomotor: 'Ciclomotor', outros: 'Outros' };
  const mesAno = s => (s || '').split('-').reverse().join('/');
  const frota = ok(g(D, 'secoes.infraestrutura.frota'));
  if (frota) {
    const comp = mesAno(frota.competencia);
    ['frotaAno', 'frotaAno2', 'frotaAno3'].forEach(id => setTxt(id, comp));
    setTxt('frotaTotal', fNum(frota.total));
    const serie = frota.serie || [];
    const ant = serie.length > 5 ? serie[serie.length - 6] : null;
    if (ant && ant.total) {
      const d = (frota.total / ant.total - 1) * 100;
      setCls('frotaDelta', 'delta ' + (d >= 0 ? 'up' : 'down'));
      setHtml('frotaDelta', (d >= 0 ? '▲ +' : '▼ −') + fNum1(Math.abs(d)) + '% <span class="vs">vs ' + ant.ano + '</span>');
    }
    const tx = frota.veiculos_1000hab || {};
    setTxt('frotaTaxa', tx.municipio != null ? fNum(Math.round(tx.municipio)) : '—');
    barrasCategoria('frotaTaxaBars', [
      { k: truncaPalavra(g(D, 'municipio.nome'), 10), v: tx.municipio || 0, titulo: g(D, 'municipio.nome') },
      { k: g(D, 'municipio.sigla_uf') || 'UF', v: tx.uf || 0 }, { k: 'Brasil', v: tx.brasil || 0 },
    ], 0, null, { fmtValor: v => fNum(Math.round(v)) });
    const barraMe = el_('frotaTaxaBars') && el_('frotaTaxaBars').querySelector('.row');
    if (barraMe) barraMe.classList.add('me');
    barrasCategoria('frotaTipoBars', (frota.por_tipo || []).slice(0, 8)
      .map(r => ({ k: TIPO_VEICULO[r.tipo] || r.tipo, v: r.quantidade })), frota.total, C.s4);
    if (serie.length) {
      setTxt('frotaSerieAno', serie[0].ano + '–' + serie[serie.length - 1].ano);
      criaGrafico(el_('frotaChart'), {
        type: 'line', data: { labels: serie.map(r => String(r.ano)),
          datasets: [{ label: 'Veículos', data: serie.map(r => r.total), borderColor: C.s4, backgroundColor: C.s4fill, fill: true, pointBackgroundColor: C.s4, ...lineStyle, pointRadius: 3 }] },
        options: { ...chartOpts, plugins: noLegend, scales: { ...chartOpts.scales, y: { ...chartOpts.scales.y, ticks: { color: C.muted, callback: v => fNum(v) } } } }
      });
    } else vazioGrafico('frotaChart');
  } else {
    vazioValores('frotaTotal', 'frotaTaxa'); barrasCategoria('frotaTaxaBars', [], 0);
    barrasCategoria('frotaTipoBars', [], 0); vazioGrafico('frotaChart');
  }

  const cont = ok(g(D, 'secoes.infraestrutura.energia_continuidade'));
  const serieCont = (cont && cont.serie) || [];
  if (serieCont.length) {
    setTxt('contAno', serieCont[0].ano + '–' + serieCont[serieCont.length - 1].ano);
    criaGrafico(el_('contChart'), {
      type: 'line', data: { labels: serieCont.map(r => String(r.ano)), datasets: [
        { label: 'DEC (horas sem luz)', data: serieCont.map(r => r.dec_horas), borderColor: C.s1, pointBackgroundColor: C.s1, ...lineStyle, pointRadius: 3 },
        { label: 'Limite DEC', data: serieCont.map(r => r.limite_dec), borderColor: C.s1, borderDash: [4, 4], borderWidth: 1.5, pointRadius: 0 },
        { label: 'FEC (interrupções)', data: serieCont.map(r => r.fec_vezes), borderColor: C.s6, pointBackgroundColor: C.s6, ...lineStyle, pointRadius: 3 },
        { label: 'Limite FEC', data: serieCont.map(r => r.limite_fec), borderColor: C.s6, borderDash: [4, 4], borderWidth: 1.5, pointRadius: 0 },
      ] },
      options: { ...chartOpts, plugins: { ...chartOpts.plugins, tooltip: { ...chartOpts.plugins.tooltip,
        callbacks: { label: ctx => ctx.dataset.label + ': ' + (ctx.parsed.y == null ? '—' : fNum1(ctx.parsed.y)) } } } }
    });
    setTxt('contNota', 'Média anual por consumidor nos conjuntos elétricos ' +
      cont.conjuntos.map(c => c.nome + ' (' + c.agente + ')').join(', ') +
      ' — a ANEEL mede por conjunto, que pode atender também municípios vizinhos. Tracejado: limite regulatório.');
  } else {
    vazioGrafico('contChart', 'Nenhum conjunto elétrico da ANEEL leva o nome do município');
    setTxt('contNota', 'A ANEEL mede interrupções por conjunto elétrico (nome de subestação), sem correspondência oficial com municípios.');
  }

  const gd = ok(g(D, 'secoes.infraestrutura.energia_gd'));
  if (gd) {
    const dataGd = mesAno((gd.data_base || '').slice(0, 7));
    ['gdAno', 'gdAno2', 'gdAno3', 'gdAno4', 'gdAno5'].forEach(id => setTxt(id, dataGd));
    setTxt('gdInst', fNum(gd.instalacoes));
    setHtml('gdMw', fNum1(gd.potencia_mw) + ' <span class="unit">MW</span>');
    const fontes = gd.por_fonte || [];
    setTxt('gdFonteSub', fontes.length === 1 ? 'Toda de ' + fontes[0].fonte.toLowerCase()
      : fontes.map(f => f.fonte + ' ' + fNum1(pctDe(f.kw, gd.potencia_mw * 1000)) + '%').join(' · '));
    setHtml('gdWhab', gd.w_por_habitante != null ? fNum(Math.round(gd.w_por_habitante)) + ' <span class="unit">W/hab</span>' : '—');
    setTxt('gdUcs', fNum(gd.ucs_recebem_credito));
    barrasCategoria('gdClasseBars', (gd.por_classe || []).map(c => ({ k: c.classe, v: c.kw })),
      gd.potencia_mw * 1000, C.s4, { fmtValor: v => fNum(Math.round(v)) + ' kW' });
    const anos = gd.por_ano_cadastro || [];
    if (anos.length) {
      setTxt('gdSerieAno', anos[0].ano + '–' + anos[anos.length - 1].ano);
      criaGrafico(el_('gdChart'), {
        type: 'bar', data: { labels: anos.map(a => String(a.ano)),
          datasets: [{ data: anos.map(a => a.instalacoes), backgroundColor: C.s4, maxBarThickness: 22, borderRadius: 4 }] },
        options: { ...chartOpts, plugins: noLegend }
      });
    } else vazioGrafico('gdChart');
  } else {
    vazioValores('gdInst', 'gdMw', 'gdWhab', 'gdUcs'); barrasCategoria('gdClasseBars', [], 0); vazioGrafico('gdChart');
  }

  // =========================================================================
  // TRABALHO — lista suja do trabalho escravo
  // =========================================================================
  const ls = ok(g(D, 'secoes.trabalho.lista_suja'));
  if (ls) {
    const coleta = mesAno(ls.data_coleta);
    setTxt('lsAno', coleta); setTxt('lsAno2', coleta);
    pill('stLs', ls.total ? 'st-crit' : 'st-good', ls.total ? '! ' + ls.total + ' na lista' : '✓ nenhum');
    if (ls.total) {
      setHtml('lsList', ls.empregadores.map((e, i) => '<tr>' +
        '<td class="rank-name" title="' + e.local + '"><span class="rk-num">' + (i + 1) + '.</span><b>' + titulo(e.empregador) + '</b></td>' +
        '<td class="area" title="' + (e.atividade || '') + '">' + (e.atividade || '—') + ' · ação ' + e.ano_acao_fiscal + '</td>' +
        '<td class="valor"><span class="val">' + fNum(e.trabalhadores) + '</span></td></tr>').join(''));
    } else vazioTabela('lsList', 3, 'Nenhum empregador com endereço no município na lista atual');
    setHtml('lsCtxList',
      liRow('No município', fNum(ls.total) + ' empregador(es) · ' + fNum(ls.trabalhadores) + ' trabalhadores') +
      liRow('Na UF', fNum(ls.uf.empregadores) + ' · ' + fNum(ls.uf.trabalhadores) + ' trabalhadores') +
      liRow('No Brasil', fNum(ls.brasil.empregadores) + ' · ' + fNum(ls.brasil.trabalhadores) + ' trabalhadores'));
  } else {
    pill('stLs', null); vazioTabela('lsList', 3); vazioLista('lsCtxList');
  }

  // =========================================================================
  // SEGURANÇA — SINESP, PRF e SISDEPEN
  // =========================================================================
  const nomeMun = g(D, 'municipio.nome'), siglaUf = g(D, 'municipio.sigla_uf') || 'UF';
  // município × UF × Brasil na mesma régua; a primeira linha é sempre a do município
  function barrasTresNiveis(id, t, fmt) {
    if (!t || t.municipio == null) { barrasCategoria(id, [], 0); return; }
    barrasCategoria(id, [
      { k: truncaPalavra(nomeMun, 10), v: t.municipio || 0, titulo: nomeMun },
      { k: siglaUf, v: t.uf || 0 }, { k: 'Brasil', v: t.brasil || 0 },
    ], 0, null, { fmtValor: fmt });
    const eu = el_(id) && el_(id).querySelector('.row');
    if (eu) eu.classList.add('me');
  }
  const sn = ok(g(D, 'secoes.seguranca.sinesp'));
  if (sn && sn.por_tipo) {
    const tp = sn.por_tipo, vit = k => (tp[k] && tp[k].vitimas != null) ? tp[k].vitimas : null;
    const txtVit = k => vit(k) == null ? '—' : fNum(vit(k));
    ['snAno', 'snAno2', 'snAno3', 'snAno4', 'snAno5', 'snAno6'].forEach(id => setTxt(id, String(sn.ano)));
    const tx = sn.taxa_homicidio_doloso_100k || {};
    setTxt('snHom', txtVit('homicidio_doloso'));
    setTxt('snHomSub', 'Vítimas' + (tx.municipio != null ? ' · ' + fNum1(tx.municipio) + ' por 100 mil hab' : ''));
    setTxt('snTent', txtVit('tentativa_de_homicidio'));
    setTxt('snTrans', txtVit('morte_no_transito_exceto_homicidio_doloso'));
    setTxt('snSuic', txtVit('suicidio'));
    const sFem = tp.suicidio && tp.suicidio.vitimas_feminino;
    setTxt('snSuicSub', 'Vítimas' + (sFem != null && vit('suicidio') ? ' · ' + fNum(sFem) + ' mulheres' : ''));
    barrasTresNiveis('snTaxaBars', tx, v => fNum1(v));
    const isp = ok(g(D, 'secoes.seguranca.isp_rj'));
    const ispHom = isp && isp.ano === sn.ano ? g(isp, 'ocorrencias.homicidio_doloso') : null;
    setTxt('snNota', 'O SINESP reúne o que cada estado informa ao Ministério da Justiça e conta vítimas.' +
      (ispHom != null && ispHom !== vit('homicidio_doloso')
        ? ' O número não coincide com o do ISP-RJ nos cartões acima (' + fNum(ispHom) + ' em ' + sn.ano + '): são bases e critérios de contagem diferentes.' : ''));
    const parc = sn.ano_parcial, vp = k => parc && parc.por_tipo[k] ? parc.por_tipo[k].vitimas : null;
    setHtml('snList',
      liRow('Feminicídio', txtVit('feminicidio')) +
      liRow('Tentativa de feminicídio', txtVit('tentativa_de_feminicidio')) +
      liRow('Latrocínio', txtVit('latrocinio')) +
      liRow('Lesão corporal seguida de morte', txtVit('lesao_corporal_seguida_de_morte')) +
      liRow('Morte a esclarecer', txtVit('morte_a_esclarecer')) +
      liRow('Mandados de prisão cumpridos', tp.mandado_de_prisao_cumprido && tp.mandado_de_prisao_cumprido.ocorrencias != null
        ? fNum(tp.mandado_de_prisao_cumprido.ocorrencias) : '—') +
      (parc && vp('homicidio_doloso') != null
        ? liRow('Homicídio doloso em ' + parc.ano + ' (até ' + String(parc.ate_mes).padStart(2, '0') + '/' + parc.ano + ')', fNum(vp('homicidio_doloso'))) : ''));
    const serie = (sn.serie || []).filter(r => r.meses === 12);
    if (serie.length) {
      setTxt('snSerieAno', serie[0].ano + '–' + serie[serie.length - 1].ano);
      setTxt('snSerieNota', 'Só anos com os 12 meses informados');
      criaGrafico(el_('snChart'), {
        type: 'bar', data: { labels: serie.map(r => String(r.ano)),
          datasets: [{ label: 'Vítimas', data: serie.map(r => r.homicidio_doloso), backgroundColor: C.s8, maxBarThickness: 22, borderRadius: 4 }] },
        options: { ...chartOpts, plugins: noLegend }
      });
    } else vazioGrafico('snChart');
  } else {
    vazioValores('snHom', 'snTent', 'snTrans', 'snSuic'); barrasCategoria('snTaxaBars', [], 0);
    vazioLista('snList'); vazioGrafico('snChart');
  }

  const prf = ok(g(D, 'secoes.seguranca.prf'));
  if (prf && prf.acidentes) {
    setTxt('prfAno', prf.desde + '–' + prf.ate);
    const lista = (arr, n) => (arr || []).slice(0, n).map(r => r.k + ' (' + fNum(r.n) + ')').join(' · ') || '—';
    setHtml('prfList',
      liRow('Acidentes', fNum(prf.acidentes)) + liRow('Mortos', fNum(prf.mortos)) +
      liRow('Feridos graves', fNum(prf.feridos_graves)) +
      liRow('Rodovias', lista(prf.por_rodovia, 3)) +
      liRow('Tipo mais comum', lista(prf.por_tipo, 1)) + liRow('Causa mais comum', lista(prf.por_causa, 1)));
  } else {
    vazioLista('prfList', prf && prf.disponivel === false
      ? 'Nenhum acidente atendido pela PRF no município desde ' + prf.desde : SEM_DADO);
  }

  const sisdep = ok(g(D, 'secoes.seguranca.sisdepen'));
  if (sisdep && sisdep.unidades) {
    setTxt('depAno', sisdep.competencia);
    setHtml('depList',
      liRow('Unidades prisionais', fNum(sisdep.unidades)) + liRow('Pessoas custodiadas', fNum(sisdep.populacao)) +
      liRow('Capacidade', fNum(sisdep.capacidade)) +
      liRow('Ocupação', sisdep.taxa_ocupacao != null ? fNum1(sisdep.taxa_ocupacao * 100) + '%' : '—') +
      liRow('Presos provisórios', fNum(sisdep.provisorios) + ' · ' + fNum1(pctDe(sisdep.provisorios, sisdep.populacao)) + '%') +
      liRow('Mulheres', fNum(sisdep.mulheres) + ' · ' + fNum1(pctDe(sisdep.mulheres, sisdep.populacao)) + '%'));
  } else {
    vazioLista('depList', sisdep && sisdep.disponivel === false ? 'Nenhuma unidade prisional no município' : SEM_DADO);
  }

  // =========================================================================
  // BENEFÍCIOS — INSS
  // =========================================================================
  const CAT_INSS = { aposentadoria_idade: 'Aposentadoria por idade', aposentadoria_tempo_contribuicao: 'Aposentadoria por tempo de contribuição',
    pensao_morte: 'Pensão por morte', aposentadoria_invalidez: 'Aposentadoria por invalidez', bpc_loas: 'BPC',
    aposentadoria_especial: 'Aposentadoria especial', auxilio_incapacidade_temporaria: 'Auxílio por incapacidade temporária',
    auxilio_acidente: 'Auxílio-acidente', salario_maternidade: 'Salário-maternidade' };
  const inss = ok(g(D, 'secoes.beneficios.inss'));
  if (inss && inss.beneficios) {
    const comp = mesAno(inss.competencia);
    ['inssAno', 'inssAno2', 'inssAno3', 'inssAno4', 'inssAno5'].forEach(id => setTxt(id, comp));
    const tx = inss.por_1000hab || {};
    setTxt('inssN', fNum(inss.beneficios));
    setTxt('inssNSub', tx.municipio != null ? fNum(Math.round(tx.municipio)) + ' benefícios para cada 1.000 habitantes' : '');
    setHtml('inssValor', 'R$ ' + fNum1(inss.valor_mensal / 1e6) + ' <span class="unit">mi</span>');
    setTxt('inssMedio', fReal(inss.valor_medio));
    const cheios = (inss.concedidos || []).filter(r => r.meses === 12);
    const conc = cheios[cheios.length - 1];
    if (conc) {
      setTxt('inssConcAno', String(conc.ano)); setTxt('inssConc', fNum(conc.beneficios));
      setTxt('inssConcSub', 'Novos benefícios no ano · R$ ' + fNum1(conc.valor / 1e6) + ' mi em valor mensal');
    } else vazioValor('inssConc');
    // as nove categorias nomeadas; o resto (rendas vitalícias, auxílio-reclusão…) vira "Outros"
    const cats = (inss.por_categoria || []).filter(r => CAT_INSS[r.k]).map(r => ({ k: CAT_INSS[r.k], v: r.n }));
    const outros = inss.beneficios - cats.reduce((a, r) => a + r.v, 0);
    if (outros > 0) cats.push({ k: 'Outros', v: outros });
    barrasCategoria('inssCatBars', cats, inss.beneficios, C.s4);
    const bpcCgu = g(D, 'secoes.beneficios.bpc.beneficiarios'), bpcInss = (inss.por_categoria || []).find(r => r.k === 'bpc_loas');
    setTxt('inssBpcNota', bpcCgu != null && bpcInss
      ? 'O BPC aqui (' + fNum(bpcInss.n) + ') vem da folha do INSS; o cartão do topo (' + fNum(bpcCgu) + ') vem do Portal da Transparência, em outra competência.' : '');
    barrasTresNiveis('inssTaxaBars', tx, v => fNum(Math.round(v)));
    const rot = { feminino: 'Mulheres', masculino: 'Homens' };
    barrasCategoria('inssSexoBars', (inss.por_sexo || []).map(r => ({ k: rot[r.k] || r.k, v: r.n })).sort((a, b) => b.v - a.v),
      inss.beneficios, C.s4, { soPct: true });
    const faixa = k => /^(60|65)/.test(k) ? '60 a 69 anos' : /^70/.test(k) ? '70 anos ou mais' : 'Até 59 anos';
    const idade = agrupa((inss.por_faixa_etaria || []).map(r => ({ k: faixa(r.k), n: r.n })), 'k', 'n');
    const ordem = ['Até 59 anos', '60 a 69 anos', '70 anos ou mais'];
    barrasCategoria('inssIdadeBars', idade.sort((a, b) => ordem.indexOf(a.k) - ordem.indexOf(b.k)), inss.beneficios, C.s4, { soPct: true });
    const serie = inss.serie || [];
    if (serie.length > 1) {
      setTxt('inssSerieAno', serie[0].ano + '–' + serie[serie.length - 1].ano);
      criaGrafico(el_('inssChart'), {
        type: 'line', data: { labels: serie.map(r => String(r.ano)),
          datasets: [{ label: 'Benefícios', data: serie.map(r => r.beneficios), borderColor: C.s4, backgroundColor: C.s4fill, fill: true, pointBackgroundColor: C.s4, ...lineStyle, pointRadius: 3 }] },
        options: { ...chartOpts, plugins: noLegend, scales: { ...chartOpts.scales, y: { ...chartOpts.scales.y, ticks: { color: C.muted, callback: v => fNum(v) } } } }
      });
    } else vazioGrafico('inssChart');
  } else {
    vazioValores('inssN', 'inssValor', 'inssMedio', 'inssConc');
    ['inssCatBars', 'inssTaxaBars', 'inssSexoBars', 'inssIdadeBars'].forEach(id => barrasCategoria(id, [], 0));
    vazioGrafico('inssChart');
  }

  // =========================================================================
  // SOCIAL — SinPatinhas
  // =========================================================================
  const pat = ok(g(D, 'secoes.social.sinpatinhas'));
  if (pat && pat.animais) {
    const ate = mesAno((pat.periodo.ate || '').slice(0, 7));
    ['patAno', 'patAno2', 'patAno3'].forEach(id => setTxt(id, 'até ' + ate));
    setTxt('patN', fNum(pat.animais));
    barrasCategoria('patEspBars', (pat.por_especie || []).map(r => ({ k: r.k, v: r.n })), pat.animais, C.s4);
    barrasTresNiveis('patTaxaBars', pat.por_1000hab, v => fNum1(v));
  } else {
    vazioValor('patN'); barrasCategoria('patEspBars', [], 0); barrasCategoria('patTaxaBars', [], 0);
  }


  // =========================================================================
  // EXTRAS — fontes do espelho que entraram em out/2026 (CFEM, CAR, Pix, BNDES…)
  // Cartões montados a partir de uma lista declarativa: cada um some sozinho
  // quando o bloco veio com erro ou "disponivel: false".
  // =========================================================================
  const esc = t => String(t == null ? '' : t).replace(/[&<>"]/g, c => ({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;'}[c]));
  const fMi = n => n == null ? '' : 'R$ ' + fNum1(Number(n) / 1e6) + ' mi';
  const fRealC = n => n == null ? '' : (Math.abs(n) >= 1e6 ? fMi(n) : fReal(n));
  const cartaoExtra = (alvo, c) => {
    const box = el_('extras-' + alvo); if (!box) return;
    const id = 'x' + Math.random().toString(36).slice(2, 9);
    let h = '<div class="card' + (c.valor != null && !c.barras && !c.lista ? ' card-metric' : '') + '"><h3>' + esc(c.titulo) +
      (c.vintage ? ' <span class="vintage">' + esc(c.vintage) + '</span>' : '') + '</h3>';
    if (c.valor != null) h += '<div class="' + (c.barras || c.lista ? 'value-sm' : 'value') + '">' + esc(c.valor) + '</div>';
    if (c.sub) h += '<div class="sub" style="margin-bottom:.55rem">' + c.sub + '</div>';
    if (c.barras) h += '<div class="bench-bars wide" id="' + id + '"></div>';
    if (c.lista) h += '<ul class="data-list">' + (c.lista.length ? c.lista.map(([a, b]) => liRow(esc(a), esc(b))).join('')
      : '<li style="border-bottom:none;display:block"><span class="empty">' + SEM_DADO + '</span></li>') + '</ul>';
    box.insertAdjacentHTML('beforeend', h + '</div>');
    if (c.barras) barrasCategoria(id, c.barras.linhas, c.barras.total, c.barras.cor, c.barras.opts);
  };
  const X = p => ok(g(D, p)) && g(D, p).disponivel !== false ? g(D, p) : null;
  const top = (arr, k, v, n) => (arr || []).filter(r => r[v] != null && Number(r[v]) > 0).slice(0, n || 8)
    .map(r => ({ k: truncaPalavra(titulo(String(r[k] ?? '—')), 34), titulo: r[k], v: Number(r[v]) }));
  const ultAno = (arr, k) => (arr && arr.length) ? arr[arr.length - 1][k || 'ano'] : '';

  // Demografia
  { const n = X('secoes.demografia.nomes');
    if (n && n.top && n.top.length) cartaoExtra('demo', { titulo: 'Nomes mais comuns', vintage: 'Censo 2010',
      barras: { linhas: n.top.slice(0, 10).map(r => ({ k: r.nome, v: r.pessoas })), total: 0, cor: C.s2 } }); }

  // Economia
  { const p = X('secoes.economia.pix');
    if (p) {
      cartaoExtra('econ', { titulo: 'Pix — valor pago no mês', vintage: mesAno(p.competencia), valor: fRealC(p.valor_pago),
        sub: fNum(p.transacoes_pagas) + ' transações · recebido ' + fRealC(p.valor_recebido) });
      cartaoExtra('econ', { titulo: 'Pessoas que pagam com Pix', vintage: mesAno(p.competencia), valor: fNum(p.pagadores_pf),
        sub: (p.pagadores_pf_por_hab != null ? fNum1(p.pagadores_pf_por_hab * 100) + '% da população · ' : '') + fNum(p.pagadores_pj) + ' empresas pagadoras' });
    }
    const b = X('secoes.economia.bndes');
    if (b && b.serie_indiretas && b.serie_indiretas.length) {
      // ano corrente ainda incompleto: o cartão destaca o último ano fechado
      const anoGer = Number(String(g(D, 'gerado_em') || '').slice(0, 4)) || Infinity;
      const fechados = b.serie_indiretas.filter(r => r.ano < anoGer), serieB = fechados.length ? fechados : b.serie_indiretas;
      const u = serieB[serieB.length - 1];
      cartaoExtra('econ', { titulo: 'BNDES — desembolsos via bancos', vintage: String(u.ano),
        valor: fRealC(u.desembolsado), sub: fNum(u.operacoes) + ' operações indiretas no ano',
        barras: { linhas: serieB.slice(-8).map(r => ({ k: String(r.ano), v: r.desembolsado })), total: 0, cor: C.s1, opts: { fmtValor: fRealC } } });
      if (b.porte_5a && b.porte_5a.length) cartaoExtra('econ', { titulo: 'BNDES por porte do cliente', vintage: '5 anos',
        barras: { linhas: top(b.porte_5a, 'porte', 'desembolsado'), total: 0, cor: C.s1, opts: { fmtValor: fRealC } } });
      if ((b.administracao_publica || []).length) cartaoExtra('econ', { titulo: 'BNDES com a prefeitura', vintage: String(b.administracao_publica[0].ano || ''),
        lista: b.administracao_publica.slice(0, 5).map(r => [truncaPalavra(titulo(r.projeto || r.programa || ''), 48), fRealC(r.valor)]) });
    }
    const emp = X('secoes.empresas');
    if (emp && emp.mei != null) cartaoExtra('econ', { titulo: 'Microempreendedores individuais (MEI)', vintage: mesAno(emp.competencia),
      valor: fNum(emp.mei), sub: 'Empresas ativas com sede no município optantes pelo MEI' + (emp.ativas ? ' · ' + fNum1(pctDe(emp.mei, emp.ativas)) + '% dos estabelecimentos ativos' : '') });
    const m = X('secoes.economia.mineracao_cfem');
    if (m) cartaoExtra('econ', { titulo: 'CFEM — royalties da mineração', vintage: String(m.ano), valor: fRealC(m.valor_ano),
      sub: 'Recolhido no ano; o município fica com 60%',
      barras: { linhas: top(m.substancias, 'substancia', 'valor', 5), total: 0, cor: C.s3, opts: { fmtValor: fRealC } } });
  }

  // Educação
  { const a = X('secoes.educacao.alfabetizacao');
    if (a) cartaoExtra('educ', { titulo: 'Criança Alfabetizada', vintage: String(a.ano), valor: fNum1(a.taxa) + '%',
      sub: 'Alunos do 2º ano alfabetizados (rede pública)' + (a.media_municipios_uf != null ? ' · média dos municípios da UF ' + fNum1(a.media_municipios_uf) + '%' : '') });
    const i = X('secoes.educacao.inse');
    if (i) cartaoExtra('educ', { titulo: 'Nível socioeconômico dos alunos (INSE)', vintage: String(i.ano), valor: fNum1(i.inse).replace(/,0$/, ',0'),
      sub: 'Escala 1–8 · UF ' + fNum1(i.media_municipios_uf) + ' · Brasil ' + fNum1(i.media_municipios_br),
      barras: { linhas: (i.niveis_pct || []).map(r => ({ k: 'Nível ' + r.nivel, v: r.pct })), total: 0, cor: C.s2, opts: { fmtValor: v => fNum1(v) + '%' } } });
    const s = X('secoes.educacao.superior');
    if (s) {
      cartaoExtra('educ', { titulo: 'Ensino superior — matrículas', vintage: String(s.ano), valor: fNum(s.matriculas),
        sub: fNum(s.matriculas_presenciais) + ' presenciais em ' + fNum(s.cursos_presenciais) + ' cursos · ' + fNum(s.matriculas_ead) + ' EaD em polos · ' + fNum(s.concluintes) + ' concluintes',
        barras: { linhas: (s.por_rede || []).map(r => ({ k: r.rede, v: r.matriculas })), total: s.matriculas, cor: C.s2 } });
      cartaoExtra('educ', { titulo: 'Matrículas por área', vintage: String(s.ano),
        barras: { linhas: top(s.por_area, 'area', 'matriculas', 8), total: s.matriculas, cor: C.s2 } });
    }
    const c = X('secoes.educacao.conectada');
    if (c) cartaoExtra('educ', { titulo: 'Internet nas escolas públicas', vintage: String(c.ano), valor: fNum(c.com_internet) + ' de ' + fNum(c.escolas),
      sub: fNum(c.internet_aprendizagem) + ' usam internet para aprendizagem · ' + fNum(c.laboratorio) + ' com laboratório' +
        (c.download_mediano != null ? ' · download mediano ' + fNum1(c.download_mediano) + ' Mbps' : ''),
      barras: { linhas: top(c.por_faixa, 'faixa', 'escolas'), total: c.escolas, cor: C.s2 } });
    const e = X('secoes.educacao.especial');
    if (e && (e.por_tipo || []).some(r => r.matriculas > 0)) cartaoExtra('educ', { titulo: 'Educação especial por deficiência', vintage: String(e.ano),
      barras: { linhas: top(e.por_tipo, 'tipo', 'matriculas', 8), total: 0, cor: C.s2 } });
    const sv = X('secoes.educacao.sisu'), vg = sv && (sv.vagas_no_municipio || []).filter(r => r.total);
    if (vg && vg.length) { const u = vg[vg.length - 1];
      cartaoExtra('educ', { titulo: 'Vagas do SISU em campi do município', vintage: String(u.ano), valor: fNum(u.total),
        sub: 'Soma das vagas dos dois semestres', barras: { linhas: [{ k: 'Ampla concorrência', v: u.ampla }, { k: 'Cotas e reservas', v: u.cotas }], total: u.total, cor: C.s2 } }); }
    const q = X('secoes.educacao.cnpq');
    if (q && q.serie) { const u = q.serie[q.serie.length - 1];
      cartaoExtra('educ', { titulo: 'Bolsas do CNPq com destino no município', vintage: String(u.ano), valor: fNum(u.processos),
        sub: fRealC(u.valor) + ' no ano', barras: { linhas: top(q.por_modalidade, 'modalidade', 'processos', 6), total: u.processos, cor: C.s2 } }); }
  }

  // Saúde
  { const cn = X('secoes.saude.cnes');
    if (cn && cn.equipes && (cn.equipes.por_tipo || []).length) {
      const ROT_EQ = { eSF: 'Saúde da Família (eSF)', eSB: 'Saúde Bucal (eSB)', eAP: 'Atenção Primária (eAP)', eMulti: 'Multiprofissionais (eMulti)', outras: 'Outras' };
      cartaoExtra('saude', { titulo: 'Equipes de saúde por tipo', vintage: mesAno(cn.equipes.competencia),
        barras: { linhas: cn.equipes.por_tipo.map(r => ({ k: ROT_EQ[r.tipo] || r.tipo, v: r.n })), total: cn.equipes.total, cor: C.s8 } });
    }
    if (cn && (cn.unidades || cn.agentes)) {
      const u = cn.unidades || {}, ag = cn.agentes || {};
      cartaoExtra('saude', { titulo: 'Rede de atenção', vintage: mesAno(cn.competencia), lista: [
        ['Unidades básicas de saúde (UBS e postos)', fNum(u.ubs)], ['UPA / pronto atendimento', fNum(u.upa)],
        ['CAPS', fNum(u.caps)], ['Unidades móveis de urgência (SAMU)', fNum(u.samu)],
        ['Agentes comunitários de saúde (ACS)' + (ag.competencia ? ' · ' + mesAno(ag.competencia) : ''), fNum(ag.acs)],
        ['Agentes de combate às endemias (ACE)', fNum(ag.ace)]].filter(r => r[1] !== '') });
    }
    const a = X('secoes.saude.atencao_basica');
    if (a) cartaoExtra('saude', { titulo: 'Cobertura da atenção básica', vintage: mesAno(a.referencia), valor: fNum1(a.cobertura_ab) + '%',
      sub: 'Estratégia Saúde da Família: ' + fNum1(a.cobertura_esf) + '% · ' + fNum(a.equipes) + ' equipes. Indicador descontinuado em 2020.' }); }

  // Infraestrutura
  { const o = X('secoes.infraestrutura.obras_cno');
    if (o) {
      cartaoExtra('infra', { titulo: 'Obras registradas na Receita (CNO)', vintage: mesAno((o.data_extracao || '').slice(0, 7)), valor: fNum(o.obras),
        barras: { linhas: (o.por_situacao || []).map(r => ({ k: r.situacao, v: r.obras })), total: o.obras, cor: C.s3 } });
      if ((o.iniciadas_por_ano || []).length) cartaoExtra('infra', { titulo: 'Obras iniciadas por ano',
        barras: { linhas: o.iniciadas_por_ano.map(r => ({ k: String(r.ano), v: r.obras })), total: 0, cor: C.s3 } });
    }
    const w = X('secoes.infraestrutura.outorgas_agua');
    if (w) cartaoExtra('infra', { titulo: 'Outorgas de captação de água', valor: fNum(w.outorgas), sub: 'Vazão média somada: ' + fNum1(w.vazao_total) + ' m³/h',
      lista: (w.maiores || []).slice(0, 5).map(r => [truncaPalavra(titulo(r.responsavel), 40), fNum1(r.vazao) + ' m³/h']) });
  }

  // Meio ambiente
  { const c = X('secoes.meio_ambiente.car');
    if (c) {
      const cam = c.camadas_ha || {};
      cartaoExtra('amb', { titulo: 'Cadastro Ambiental Rural', vintage: mesAno((c.data_extracao || '').slice(0, 7)), valor: fNum(c.imoveis) + ' imóveis',
        sub: fNum(Math.round(c.area_ha)) + ' ha cadastrados · ' + fNum(c.pendentes) + ' pendentes',
        barras: { linhas: [['Vegetação nativa', cam.vegetacao_nativa], ['Reserva legal', cam.reserva_legal], ['APP', cam.app],
          ['Área consolidada', cam.area_consolidada], ['Uso restrito', cam.uso_restrito]].filter(r => r[1] > 0).map(([k, v]) => ({ k, v })).sort((a, b) => b.v - a.v),
          total: 0, cor: C.s3, opts: { fmtValor: v => fNum(Math.round(v)) + ' ha' } } });
      cartaoExtra('amb', { titulo: 'Situação da análise do CAR', vintage: mesAno((c.data_extracao || '').slice(0, 7)),
        barras: { linhas: top(c.por_condicao, 'condicao', 'imoveis', 5).map(r => ({ ...r, k: truncaPalavra(r.titulo, 36) })), total: c.imoveis, cor: C.s3 } });
    }
    const b = X('secoes.meio_ambiente.ibama');
    if (b) cartaoExtra('amb', { titulo: 'Autos de infração do IBAMA', valor: fNum(b.autos_total),
      sub: fRealC(b.valor_total) + ' em multas · ' + fNum(b.embargos) + ' embargos (' + fNum(b.embargos_5a) + ' nos últimos 5 anos)',
      barras: { linhas: (b.serie || []).slice(-8).map(r => ({ k: String(r.ano), v: r.autos })), total: 0, cor: C.s3 } });
    const d = X('secoes.meio_ambiente.desastres');
    if (d) cartaoExtra('amb', { titulo: 'Emergência ou calamidade vigente', vintage: mesAno((d.data_extracao || '').slice(0, 7)),
      valor: d.vigentes.length ? fNum(d.vigentes.length) : 'Nenhuma',
      sub: fNum(d.municipios_uf_com_reconhecimento) + ' municípios da UF com reconhecimento vigente',
      lista: d.vigentes.length ? d.vigentes.map(r => [r.desastre + ' — ' + r.situacao, 'até ' + mesAno(r.vigencia)]) : null });
    const e = X('secoes.meio_ambiente.estacoes_inmet');
    if (e && e.estacoes.length) cartaoExtra('amb', { titulo: 'Estações meteorológicas do INMET',
      lista: e.estacoes.map(r => [titulo(r.estacao) + ' (' + r.id_estacao + ')', fNum(Math.round(r.altitude)) + ' m']) });
  }

  // Política
  { const f = X('secoes.politica.filiados');
    if (f) cartaoExtra('pol', { titulo: 'Filiados a partidos', vintage: mesAno((f.data_extracao || '').slice(0, 7)), valor: fNum(f.filiados),
      barras: { linhas: (f.por_partido || []).slice(0, 10).map(r => ({ k: r.partido, v: r.filiados })), total: f.filiados, cor: C.s5 } });
    const c = X('secoes.politica.financas_campanha');
    if (c) {
      const rec = (c.receitas_por_cargo || []).reduce((a, r) => a + (r.valor || 0), 0);
      cartaoExtra('pol', { titulo: 'Dinheiro das campanhas', vintage: String(c.ano), valor: fRealC(rec),
        sub: (c.receitas_por_cargo || []).map(r => titulo(r.cargo) + ': ' + fRealC(r.valor) + ' (' + fNum(r.candidatos) + ' candidaturas)').join(' · '),
        barras: { linhas: top(c.receitas_por_origem, 'origem', 'valor', 6).map(r => ({ ...r, k: truncaPalavra(String(r.titulo).replace(/^recursos d[eo] /, ''), 30) })), total: rec, cor: C.s5 } });
      cartaoExtra('pol', { titulo: 'Gastos das campanhas por tipo', vintage: String(c.ano),
        barras: { linhas: top(c.despesas_por_tipo, 'tipo', 'valor', 7), total: 0, cor: C.s5, opts: { fmtValor: fRealC } } });
    }
  }

  // Transparência
  { const c = X('secoes.transparencia.cauc');
    if (c) cartaoExtra('transp', { titulo: 'CAUC — requisitos para receber verba federal', vintage: c.data_pesquisa || '',
      valor: c.pendencias ? c.pendencias + ' pendência' + (c.pendencias > 1 ? 's' : '') : 'Sem pendências',
      sub: fNum(c.regulares) + ' de ' + fNum(c.itens) + ' itens comprovados',
      lista: (c.itens_pendentes || []).map(r => [truncaPalavra(r.descricao, 60), r.item]) });
    const f = X('secoes.transparencia.fiscalizacao_cgu');
    if (f) cartaoExtra('transp', { titulo: 'Sorteios de fiscalização da CGU', valor: f.sorteios.length ? fNum(f.sorteios.length) : 'Nenhum',
      sub: f.sorteios.length ? 'Sorteio nº ' + f.sorteios.join(', ') : 'O município nunca foi sorteado' });
  }

  // Social / cultura
  { const r = X('secoes.social.rouanet');
    if (r) cartaoExtra('social', { titulo: 'Lei Rouanet — proponentes locais', valor: fNum(r.proponentes),
      sub: fNum(r.projetos) + ' projetos · ' + fRealC(r.valor_projetos) + ' aprovados para captar',
      lista: (r.top_proponentes || []).slice(0, 5).map(x => [truncaPalavra(x.nome, 44), fRealC(x.valor)]) }); }

  // Agropecuária
  { const a = X('secoes.agropecuaria.aquicultura');
    if (a) cartaoExtra('agro', { titulo: 'Aquicultura', vintage: String(a.ano), valor: 'R$ ' + fNum(a.valor_total) + ' mil',
      barras: { linhas: top(a.produtos, 'produto', 'valor', 6), total: a.valor_total, cor: C.s1 } });
    const s = X('secoes.agropecuaria.extracao_silvicultura');
    if (s) [['silvicultura', 'Silvicultura'], ['extracao_vegetal', 'Extração vegetal']].forEach(([k, rot]) => {
      const b = s[k]; if (!b) return;
      cartaoExtra('agro', { titulo: rot, vintage: String(b.ano), valor: 'R$ ' + fNum(b.valor_total) + ' mil',
        barras: { linhas: top(b.produtos, 'produto', 'valor', 6), total: b.valor_total, cor: C.s1 } });
    });
    const i = X('secoes.agropecuaria.imoveis_rurais');
    if (i) {
      if (i.cafir) cartaoExtra('agro', { titulo: 'Imóveis rurais na Receita (CAFIR)', vintage: mesAno((i.cafir.data_referencia || '').slice(0, 7)),
        valor: fNum(i.cafir.imoveis), sub: fNum(Math.round(i.cafir.area_ha)) + ' ha · área mediana ' + fNum1(i.cafir.area_mediana_ha) + ' ha · ' +
          fNum(i.cafir.imoveis_1000ha_mais) + ' com 1.000 ha ou mais' });
      if ((i.itr || []).length) cartaoExtra('agro', { titulo: 'ITR arrecadado', vintage: String(ultAno(i.itr)),
        barras: { linhas: i.itr.slice(-8).map(r => ({ k: String(r.ano), v: r.valor })), total: 0, cor: C.s1, opts: { fmtValor: fRealC } } });
    }    const cr = X('secoes.agropecuaria.credito_rural');
    if (cr && (cr.serie || []).length) {
      // ano corrente ainda incompleto: o cartão destaca o último ano fechado
      const cheios = cr.serie.filter(r => r.ultimo_mes === 12), u = cheios.length ? cheios[cheios.length - 1] : cr.serie[cr.serie.length - 1];
      cartaoExtra('agro', { titulo: 'Crédito rural — PRONAF', vintage: String(u.ano), valor: fRealC(u.valor_pronaf),
        sub: fNum(u.contratos_pronaf) + ' contratos de agricultura familiar · ' + fNum(u.contratos) + ' com recurso público no total (' + fRealC(u.valor) + '). Crédito com recurso livre não entra.',
        barras: { linhas: cheios.slice(-8).map(r => ({ k: String(r.ano), v: r.valor_pronaf })), total: 0, cor: C.s1, opts: { fmtValor: fRealC } } });
    }
  }

  // Benefícios
  { const p = X('secoes.beneficios.programas_cgu');
    if (p) [['gas_do_povo', 'Gás do Povo', 'famílias'], ['pe_de_meia', 'Pé-de-Meia', 'estudantes'], ['seguro_defeso', 'Seguro Defeso', 'pescadores']]
      .forEach(([k, rot, quem]) => { const b = ok(p[k]); if (!b) return;
        cartaoExtra('benef', { titulo: rot, vintage: mesAno(b.competencia), valor: fNum(b.pessoas), sub: quem + ' · ' + fRealC(b.valor) + ' no mês' }); });
    const ib = X('secoes.beneficios.inss'), bt = ib && ib.bpc_por_tipo;
    if (bt && (bt.idoso || bt.pcd)) cartaoExtra('benef', { titulo: 'BPC por público', vintage: mesAno(ib.competencia),
      barras: { linhas: [{ k: 'Pessoa idosa', v: bt.idoso || 0 }, { k: 'Pessoa com deficiência', v: bt.pcd || 0 }], total: (bt.idoso || 0) + (bt.pcd || 0), cor: C.s4 } });
  }

  // Seções que ficaram sem nenhum cartão extra não deixam um vão no layout
  document.querySelectorAll('.extras').forEach(e => { if (!e.children.length) e.remove(); });

  // Insights
  // Cada destaque só entra se o dado por trás dele existir: no fixture vazio a lista
  // antiga escrevia "mortalidade infantil de — ... menos da metade da média brasileira",
  // isto é, afirmava a comparação sem ter o número. Nada de dado, nada de frase.
  const insights = document.getElementById('insightsList');
  if (insights) {
    const hom = g(D, 'secoes.seguranca.isp_rj.taxas_100k.taxa_homicidio_doloso');
    const homUf = g(D, 'secoes.seguranca.isp_rj.taxas_100k_uf.taxa_homicidio_doloso');
    const pibPcV = g(D, 'secoes.economia.pib.pib_per_capita.valor');
    const pibPcUf = g(D, 'secoes.economia.pib.pib_per_capita.uf');
    const envV = g(D, 'secoes.demografia.censo_2022.indice_envelhecimento');
    const esgT = g(D, 'secoes.infraestrutura.snis.indice_tratamento_esgoto');
    const linhas = [];
    const add = (cls, rot, html) => linhas.push(
      '<li><span class="status ' + cls + '">' + rot + '</span><span>' + html + '</span></li>');

    if (hom != null && homUf) {
      const razao = homUf / hom;
      add(hom <= homUf ? 'st-good' : 'st-crit', hom <= homUf ? '✓ forte' : '✕ crítico',
        '<b>Segurança:</b> taxa de homicídios de ' + fNum1(hom) + '/100 mil hab — ' +
        (hom <= homUf ? 'cerca de ' + fNum1(razao) + '× abaixo' : fNum1(1 / razao) + '× acima') +
        ' da média fluminense (' + fNum1(homUf) + ').');
    }
    if (ideb2023Ini || ideb2023Fin) {
      const acimaFin = ideb2023Fin && brFin != null && ideb2023Fin.ideb >= brFin;
      const partes = [];
      if (ideb2023Ini) partes.push('IDEB dos anos iniciais em ' + fNum1(ideb2023Ini.ideb) +
        (brIni != null ? ' (' + (ideb2023Ini.ideb >= brIni ? 'acima' : 'abaixo') + ' do Brasil, ' + fNum1(brIni) + ')' : ''));
      if (ideb2023Fin) partes.push('anos finais em ' + fNum1(ideb2023Fin.ideb) +
        (brFin != null ? ' (' + (acimaFin ? 'acima' : 'abaixo') + ' da média nacional, ' + fNum1(brFin) + ')' : ''));
      if (alf != null) partes.push('alfabetização de ' + fNum1(alf * 100) + '% das pessoas de 15 anos ou mais');
      add(acimaFin ? 'st-good' : 'st-warn', acimaFin ? '✓ forte' : '! atenção',
        '<b>Educação:</b> ' + partes.join('; ') + '.');
    }
    if (pibPcV && pibPcUf) {
      const dif = Math.round((1 - pibPcV / pibPcUf) * 100);
      add(dif <= 0 ? 'st-good' : 'st-warn', dif <= 0 ? '✓ forte' : '! atenção',
        '<b>Economia:</b> PIB per capita ' + Math.abs(dif) + '% ' + (dif > 0 ? 'abaixo' : 'acima') +
        ' da média estadual' +
        (caged && caged.saldo != null ? '; saldo de empregos de ' + (caged.saldo >= 0 ? '+' : '−') + fNum(Math.abs(caged.saldo)) + ' em ' + caged.ano : '') +
        (exp && imp ? '; balança comercial ' +
          (Number(exp.total_fob_usd) >= Number(imp.total_fob_usd) ? 'superavitária' : 'deficitária') +
          ' em US$ ' + fNum1(Math.abs(Number(imp.total_fob_usd) - Number(exp.total_fob_usd)) / 1e6) + ' mi' : '') + '.');
    }
    // O JSON não traz índice de envelhecimento do Brasil — o destaque relata o
    // número do censo, sem afirmar posição relativa que a página não pode checar.
    const idadeMed = g(D, 'secoes.demografia.censo_2022.idade_mediana');
    if (envV != null) {
      add('st-warn', '! atenção',
        '<b>Demografia:</b> ' + fNum1(envV) + ' idosos de 65+ para cada 100 jovens de 0–14 no censo 2022' +
        (idadeMed != null ? ', com idade mediana de ' + fNum1(idadeMed) + ' anos' : '') + '.');
    }
    if (simInf && simInf.taxa_1000nv != null) {
      const tmi = simInf.taxa_1000nv;
      const antTmi = simInfAnt;
      const caiTmi = antTmi && antTmi.infantis != null ? (simInf.obitos || 0) <= antTmi.infantis : null;
      add(caiTmi === false ? 'st-warn' : 'st-good', caiTmi === false ? '! atenção' : '✓ forte',
        '<b>Saúde materno-infantil:</b> mortalidade infantil de ' + fNum1(tmi) +
        ' por 1.000 nascidos vivos em ' + simInf.ano +
        (antTmi ? ' (' + fNum(simInf.obitos || 0) + ' óbitos, ante ' + fNum(antTmi.infantis) + ' em ' + antTmi.ano + ')' : '') +
        (sim.obitos ? ' — ' + fNum1(pctDe(sim.mal_definidas, sim.obitos)) + '% dos óbitos ainda entram como causa mal definida' : '') + '.');
    }
    if (sih && sih.internacoes != null) {
      const sobe = sih.ano_anterior && sih.ano_anterior.internacoes && sih.internacoes >= sih.ano_anterior.internacoes;
      add(sobe ? 'st-warn' : 'st-good', sobe ? '! atenção' : '✓ forte',
        '<b>Rede hospitalar:</b> ' + fNum(sih.internacoes) + ' internações pelo SUS em ' + sih.ano +
        (sih.ano_anterior && sih.ano_anterior.internacoes
          ? ', ' + fNum1(Math.abs(sih.internacoes / sih.ano_anterior.internacoes - 1) * 100) + '% ' + (sobe ? 'acima' : 'abaixo') + ' do ano anterior' : '') +
        (sih.valor_total ? ' e R$ ' + fNum1(sih.valor_total / 1e6) + ' mi de gasto federal' : '') +
        (sih.pct_no_municipio != null ? '; ' + fNum1(sih.pct_no_municipio) + '% ocorrem no próprio município' : '') + '.');
    }
    if (viol && viol.notificacoes != null) {
      add('st-serious', '! crítico',
        '<b>Violência notificada:</b> ' + fNum(viol.notificacoes) + ' notificações do SINAN em ' + viol.ano +
        ', ' + fNum1(viol.pct_feminino || 0) + '% contra mulheres e ' +
        fNum1(pctDe(viol.autoprovocadas, viol.notificacoes)) +
        '% de lesões autoprovocadas — um retrato da saúde, não da polícia, e sabidamente subnotificado.');
    }
    if (snis) {
      add('st-warn', '! atenção',
        '<b>Saneamento:</b> o SNIS registra ' + fNum1(snis.indice_coleta_esgoto || 0) + '% de coleta e ' +
        fNum1(esgT || 0) + '% de tratamento do coletado' +
        (dom && dom.esgotamento && dom.esgotamento.categorias[0]
          ? ', mas no censo 2022 só ' + fNum1(dom.esgotamento.categorias[0].pct) + '% dos moradores declaram estar ligados à rede' : '') +
        (atlas && atlas.investimento_coleta_tratatamento
          ? '; a ANA ainda estima R$ ' + fNum(Math.round(atlas.investimento_coleta_tratatamento / 1e6)) + ' mi de investimento até 2035' : '') + '.');
    }

    insights.innerHTML = linhas.length
      ? linhas.join('')
      : '<li><span class="empty">Sem indicadores suficientes para destacar neste município</span></li>';
  }

  // Sparklines
  document.querySelectorAll('[data-spark-path]').forEach(el => {
    const raw = g(D, el.dataset.sparkPath);
    const arr = Array.isArray(raw) ? raw : [];
    const key = el.dataset.sparkKey || 'populacao';
    const values = arr.map(d => d[key]).filter(v => v != null);
    if (values.length < 2) return;
    const min = Math.min(...values), max = Math.max(...values), range = max - min || 1;
    const W = 100, H = 28, pad = 3;
    const pts = values.map((v, i) => [
      pad + i * (W - 2 * pad) / (values.length - 1),
      H - pad - (v - min) / range * (H - 2 * pad)
    ]);
    const path = pts.map(p => p.map(n => n.toFixed(1)).join(',')).join(' ');
    const [ex, ey] = pts[pts.length - 1];
    el.innerHTML = '<svg viewBox="0 0 ' + W + ' ' + H + '" preserveAspectRatio="none" aria-hidden="true">' +
      '<polyline points="' + path + '" fill="none" stroke="' + C.muted + '" stroke-width="1.5" stroke-linejoin="round" stroke-linecap="round"/>' +
      '<circle cx="' + ex.toFixed(1) + '" cy="' + ey.toFixed(1) + '" r="2.5" fill="' + C.s1 + '" stroke="' + C.surface + '" stroke-width="1.5"/></svg>';
  });

  // Scroll spy
  const sections = [...document.querySelectorAll('.section')];
  const navItems = document.querySelectorAll('.sidebar-item');
  const mobileNav = document.querySelector('.mobile-nav');
  let spyQueued = false, spyLastId = null;
  function updateSpy() {
    spyQueued = false;
    const line = scrollY + innerHeight * .35;
    let best = sections[0];
    for (const s of sections) if (s.offsetTop <= line) best = s;
    if (innerHeight + scrollY >= document.documentElement.scrollHeight - 2) best = sections[sections.length - 1];
    if (best.id === spyLastId) return;
    spyLastId = best.id;
    navItems.forEach(a => a.classList.toggle('active', a.getAttribute('href') === '#' + best.id));
    const ativo = [...navItems].find(a => a.getAttribute('href') === '#' + best.id);
    setTxt('heroSec', ativo ? ativo.textContent.trim() : '');
    if (mobileNav) {
      mobileNav.querySelectorAll('a').forEach(a => {
        const on = a.getAttribute('href') === '#' + best.id;
        a.classList.toggle('active', on);
        if (on) a.scrollIntoView({ behavior: 'smooth', inline: 'center', block: 'nearest' });
      });
    }
  }
  addEventListener('scroll', () => {
    if (!spyQueued) { spyQueued = true; requestAnimationFrame(updateSpy); }
  }, { passive: true });
  addEventListener('resize', updateSpy);
  updateSpy();

  // Cabeçalho preso: no desktop ele encolhe ao rolar. Medimos as duas alturas
  // (solto e preso): a presa vira --hero-h (as âncoras das seções descontam esse
  // espaço) e a diferença vira --hero-gap, para o conteúdo não pular na troca.
  const heroTop = document.getElementById('heroTop');
  if (heroTop) {
    const raiz = document.documentElement.style;
    const medeHero = () => {
      const preso = heroTop.classList.contains('stuck');
      raiz.setProperty('--hero-gap', '0px');
      heroTop.classList.remove('stuck');
      const solto = heroTop.offsetHeight;
      heroTop.classList.add('stuck');
      const compacto = heroTop.offsetHeight;
      heroTop.classList.toggle('stuck', preso);
      raiz.setProperty('--hero-h', compacto + 'px');
      raiz.setProperty('--hero-gap', (solto - compacto) + 'px');
    };
    medeHero();
    addEventListener('resize', medeHero);
    if (document.fonts && document.fonts.ready) document.fonts.ready.then(medeHero);
    const marcaHero = () => heroTop.classList.toggle('stuck', scrollY > 4);
    addEventListener('scroll', marcaHero, { passive: true });
    marcaHero();
  }

  // Link direto de cada seção: copia a URL já apontando para ela
  sections.forEach(sec => {
    const h2 = sec.querySelector('.section-header h2');
    if (!h2 || !sec.id) return;
    const b = document.createElement('button');
    b.type = 'button'; b.className = 'sec-link'; b.textContent = '🔗';
    b.title = 'Copiar link desta seção'; b.setAttribute('aria-label', 'Copiar link da seção ' + h2.textContent.trim());
    b.addEventListener('click', async () => {
      const url = location.origin + location.pathname + location.search + '#' + sec.id;
      history.replaceState(null, '', '#' + sec.id);
      try { await navigator.clipboard.writeText(url); } catch (e) { return; }
      b.textContent = '✓ copiado'; b.classList.add('ok');
      setTimeout(() => { b.textContent = '🔗'; b.classList.remove('ok'); }, 1600);
    });
    h2.after(b);
  });

  // Seção em que todo cartão ficou sem dado: o corpo recolhe atrás de um aviso
  // (título, âncora e item do menu continuam no lugar).
  sections.forEach(sec => {
    const cards = [...sec.querySelectorAll('.card')];
    const vazio = c => !!c.querySelector('.empty-val, .empty') && !c.querySelector('canvas, svg') &&
      ![...c.querySelectorAll('.value')].some(v => !v.classList.contains('empty-val') && v.textContent.trim()) &&
      ![...c.querySelectorAll('li, tbody tr')].some(r => !r.querySelector('.empty') && r.textContent.trim());
    if (!cards.length || !cards.every(vazio)) return;
    sec.classList.add('sec-vazia');
    const nota = document.createElement('div');
    nota.className = 'sec-vazia-nota';
    nota.innerHTML = '<span>Sem dados desta seção para este município.</span> <button type="button">mostrar cartões vazios</button>';
    nota.querySelector('button').addEventListener('click', e => {
      const aberta = sec.classList.toggle('aberta');
      e.target.textContent = aberta ? 'recolher' : 'mostrar cartões vazios';
    });
    sec.querySelector('.section-header').after(nota);
    document.querySelectorAll('.sidebar-item[href="#' + sec.id + '"], .mobile-nav a[href="#' + sec.id + '"]').forEach(a => a.classList.add('sem-dado'));
  });

  const savedScroll = sessionStorage.getItem('rodado-scroll');
  if (savedScroll != null) {
    sessionStorage.removeItem('rodado-scroll');
    scrollTo(0, Number(savedScroll));
  }
}

init().finally(() => document.body.classList.remove('carregando'));
