// Fetch + gunzip + parse a state's point file off the main thread, so the
// page stays responsive (loading text keeps animating, sliders stay
// clickable) while the biggest states (SP, MG, PR — millions of points)
// are being decoded. Posts back one interleaved Float32Array via a
// Transferable (zero-copy — ownership moves to the main thread, no
// serialization cost for what can be tens of MB of data).

self.onmessage = function (e) {
  var url = e.data.url;
  fetch(url)
    .then(function (res) {
      if (!res.ok) throw new Error("fetch " + url + " -> " + res.status);
      var stream = res.body.pipeThrough(new DecompressionStream("gzip"));
      return new Response(stream).arrayBuffer();
    })
    .then(function (buf) {
      // Struct-of-arrays layout written by extrai_estados_cnpj.py's
      // write_points_soa(): n lngs (f32), then n lats (f32), then n weights
      // (u16) — three homogeneous aligned blocks, each a genuine zero-copy
      // typed-array view (no per-point parsing needed to get here, unlike
      // the old interleaved format which required DataView calls per point
      // since 10-byte records don't land on 4-byte-aligned offsets).
      var n = (buf.byteLength / 10) | 0;
      var lngs = new Float32Array(buf, 0, n);
      var lats = new Float32Array(buf, 4 * n, n);
      // weights (Uint16Array at byte offset 8*n) are unused by this
      // renderer (dot size/brightness are user-controlled sliders, not
      // per-point weight) — skip reading them, nothing to gain.

      // deck.gl's ScatterplotLayer getPosition wants one interleaved
      // [lng,lat,lng,lat,...] buffer, so we still do one copy pass here —
      // but it's plain indexed typed-array reads, not DataView method
      // calls, so it JITs much better than the old per-point parse loop.
      var positions = new Float32Array(n * 2);
      for (var i = 0; i < n; i++) {
        positions[i * 2] = lngs[i];
        positions[i * 2 + 1] = lats[i];
      }

      self.postMessage({ ok: true, n: n, positions: positions }, [positions.buffer]);
    })
    .catch(function (err) {
      self.postMessage({ ok: false, error: err.message });
    });
};
