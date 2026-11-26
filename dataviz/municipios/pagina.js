// Página de um município (/dataviz/municipios/<id>/, gerada por gera_indice.py): troca o documento
// pelo painel.html, com o bloco <!-- painel:seo --> da página no lugar do genérico do painel, para
// que título, descrição e canonical continuem os do município depois da troca.
(function () {
  var id = window.ID_MUN_FIXO, q = new URLSearchParams(location.search), FIM = '<!-- /painel:seo -->';
  if (q.get('dados') !== 'local') window.DADOS_PREFETCH = fetch('https://xyz-municipio.hel1.your-objectstorage.com/' + id + '.json');
  ['/dataviz/municipios/vendor/chart-4.4.7.umd.min.js', '/dataviz/municipios/app.js?v=5'].forEach(function (u) {
    var l = document.createElement('link'); l.rel = 'preload'; l.as = 'script'; l.href = u; document.head.appendChild(l);
  });
  var h = document.head.innerHTML, seo = h.slice(h.indexOf('<!-- painel:seo'), h.indexOf(FIM) + FIM.length);
  document.documentElement.style.visibility = 'hidden';
  fetch('/dataviz/municipios/painel.html', { cache: 'no-cache' }).then(function (r) { return r.text(); }).then(function (t) {
    var a = t.indexOf('<!-- painel:seo'), b = t.indexOf(FIM);
    if (a >= 0 && b > a) t = t.slice(0, a) + seo + t.slice(b + FIM.length);
    document.open(); document.write(t); document.close();
  }).catch(function () { document.documentElement.style.visibility = ''; });
})();
