/* Busca de município (combobox): usada no painel e no índice. Lê municipios.json (id, nome, uf)
   do bucket só quando o campo ganha foco. Ignora acento e caixa, mostra a UF e funciona pelo teclado. */
// Busca de município: lê o índice (id, nome, UF) do bucket só quando o campo ganha foco.
// Ignora acento e caixa, mostra a UF (há homônimos) e funciona pelo teclado.
(function () {
  let indice = null, ativo = -1, achados = [];
  const norm = t => String(t || '').normalize('NFD').replace(/[\u0300-\u036f]/g, '').toLowerCase().trim();
  const carrega = () => indice || (indice = fetch((window.BUSCA_INDICE || (typeof DADOS_BASE !== 'undefined' ? DADOS_BASE : '') + 'municipios.json')).then(r => r.ok ? r.json() : [])
    .then(l => l.map(m => ({ ...m, n: norm(m.nome) }))).catch(() => (indice = null, [])));
  const pronto = fn => document.readyState === 'loading' ? document.addEventListener('DOMContentLoaded', fn) : fn();
  pronto(() => {
    const inp = document.getElementById('buscaMun'), lista = document.getElementById('buscaLista');
    if (!inp || !lista) return;
    const fecha = () => { lista.hidden = true; inp.setAttribute('aria-expanded', 'false'); inp.removeAttribute('aria-activedescendant'); ativo = -1; };
    const vai = m => { location.href = (window.BUSCA_PAINEL || '') + '?id=' + m.id; };
    const marca = i => {
      ativo = i;
      [...lista.children].forEach((li, k) => li.setAttribute('aria-selected', k === i ? 'true' : 'false'));
      if (i >= 0 && lista.children[i]) { inp.setAttribute('aria-activedescendant', lista.children[i].id); lista.children[i].scrollIntoView({ block: 'nearest' }); }
    };
    const mostra = async () => {
      const q = norm(inp.value);
      if (q.length < 2) return fecha();
      const todos = await carrega();
      if (norm(inp.value) !== q) return;
      const exato = [], ini = [], meio = [];
      for (const m of todos) { const k = m.n.indexOf(q); if (k < 0) continue; (m.n === q ? exato : k === 0 ? ini : meio).push(m); }
      const curto = (x, y) => x.n.length - y.n.length || (x.n < y.n ? -1 : x.n > y.n ? 1 : 0);
      achados = exato.concat(ini.sort(curto), meio.sort(curto)).slice(0, 12);
      lista.replaceChildren(...(achados.length ? achados.map((m, i) => {
        const li = document.createElement('li'); li.id = 'busca-' + i; li.setAttribute('role', 'option');
        li.append(m.nome); const s = document.createElement('small'); s.textContent = m.uf; li.append(s);
        li.addEventListener('mousedown', e => { e.preventDefault(); vai(m); });
        return li;
      }) : [Object.assign(document.createElement('li'), { className: 'vazio', textContent: 'Nenhum município encontrado' })]));
      lista.hidden = false; inp.setAttribute('aria-expanded', 'true'); marca(achados.length ? 0 : -1);
    };
    inp.addEventListener('focus', carrega);
    inp.addEventListener('input', mostra);
    inp.addEventListener('keydown', e => {
      if (e.key === 'ArrowDown' || e.key === 'ArrowUp') {
        if (lista.hidden) { mostra(); return; }
        e.preventDefault(); if (achados.length) marca((ativo + (e.key === 'ArrowDown' ? 1 : -1) + achados.length) % achados.length);
      } else if (e.key === 'Enter') { if (achados[ativo] && !lista.hidden) { e.preventDefault(); vai(achados[ativo]); } }
      else if (e.key === 'Escape') { fecha(); inp.blur(); }
    });
    inp.addEventListener('blur', () => setTimeout(fecha, 120));
    document.addEventListener('keydown', e => {
      if (e.key === '/' && !/^(INPUT|TEXTAREA|SELECT)$/.test(document.activeElement.tagName)) { e.preventDefault(); inp.focus(); inp.select(); }
    });
  });
})();

