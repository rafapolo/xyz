(function () {
  "use strict";

  var config = window.UF_CONFIG || {};
  var uf = config.uf;
  var ufLower = uf.toLowerCase();
  var DARK_STYLE = "https://basemaps.cartocdn.com/gl/dark-matter-gl-style/style.json";
  // kepler.gl's exported "radius" config value is NOT a literal deck.gl
  // ScatterplotLayer pixel radius — kepler applies its own internal scaling
  // before handing radius to deck.gl. Feeding the raw config value (3)
  // straight into our ScatterplotLayer produced dots ~3x wider than the
  // kepler.gl reference render (measured via connected-component blob
  // analysis on both screenshots: isolated single dots came out ~8-9px
  // diameter here vs ~2-4px in the reference). This constant corrects for
  // that gap; tune it visually against the reference if the source data or
  // template radius changes.
  var KEPLER_RADIUS_TO_PIXELS = 1 / 3;

  function setLoading(msg) {
    var el = document.getElementById("loading");
    if (el) el.textContent = msg;
  }

  // Fetch + gunzip + parse happen in worker.js, off the main thread — keeps
  // the page responsive while the biggest states (millions of points) are
  // being decoded, instead of a synchronous parse loop blocking everything.
  function loadPointsInWorker(url) {
    return new Promise(function (resolve, reject) {
      var worker = new Worker("../worker.js");
      worker.onmessage = function (e) {
        worker.terminate();
        if (e.data.ok) {
          resolve({ n: e.data.n, positions: e.data.positions });
        } else {
          reject(new Error(e.data.error));
        }
      };
      worker.onerror = function (err) {
        worker.terminate();
        reject(err);
      };
      worker.postMessage({ url: url });
    });
  }

  // Same fitBounds math deck.gl's WebMercatorViewport uses.
  function fitBounds(bbox, width, height, padding) {
    var WORLD_DIM = 512;
    var ZOOM_MAX = 20;
    function lat2y(lat) {
      var s = Math.sin((lat * Math.PI) / 180);
      return 0.5 - Math.log((1 + s) / (1 - s)) / (4 * Math.PI);
    }
    function lng2x(lng) {
      return lng / 360 + 0.5;
    }
    var x0 = lng2x(bbox[0]), x1 = lng2x(bbox[2]);
    var y0 = lat2y(bbox[3]), y1 = lat2y(bbox[1]);
    var fracWidth = Math.abs(x1 - x0) || 1e-9;
    var fracHeight = Math.abs(y1 - y0) || 1e-9;
    var usableW = Math.max(width - padding * 2, 1);
    var usableH = Math.max(height - padding * 2, 1);
    var zoomX = Math.log2(usableW / WORLD_DIM / fracWidth);
    var zoomY = Math.log2(usableH / WORLD_DIM / fracHeight);
    var zoom = Math.min(zoomX, zoomY, ZOOM_MAX);
    return {
      longitude: (bbox[0] + bbox[2]) / 2,
      latitude: (bbox[1] + bbox[3]) / 2,
      zoom: zoom,
    };
  }

  // CARTO's dark-matter has real color contrast between water/land/borders
  // (e.g. water is #2C353C, a blue-gray, against a #0e0e0e background) —
  // kepler.gl's own bundled "dark" style is uniformly near-pure-black with
  // no visible water/land distinction at all. A CSS brightness filter only
  // scales colors down proportionally, so that contrast stays visible as a
  // faint coastline. Force the actual paint colors instead so water/land/
  // borders all collapse to the same near-black as the background.
  var FLATTEN_TO_BLACK = "#000000";

  function hideRoads(map) {
    var layers = map.getStyle().layers || [];
    layers.forEach(function (l) {
      var hideByName = /road|label|place|poi/i.test(l.id);
      var hideBySource = /^(transportation|transportation_name|aeroway|housenumber)$/.test(
        l["source-layer"] || ""
      );
      if (hideByName || hideBySource) {
        map.setLayoutProperty(l.id, "visibility", "none");
        return;
      }

      // Flatten remaining land/water/boundary fills+lines to black so no
      // basemap geography is visible behind the dot cloud — only the dots
      // should read as "signal".
      if (l.type === "background") {
        map.setPaintProperty(l.id, "background-color", FLATTEN_TO_BLACK);
      } else if (l.type === "fill" && /landcover|landuse|park|water/.test(l["source-layer"] || "")) {
        map.setPaintProperty(l.id, "fill-color", FLATTEN_TO_BLACK);
      } else if (l.type === "line" && /waterway|boundary/.test(l["source-layer"] || "")) {
        map.setPaintProperty(l.id, "line-color", FLATTEN_TO_BLACK);
      }
    });
  }

  // deck.gl's fragment shader multiplies (vertex color alpha) * (layer
  // `opacity` prop) before additive blending sums it into the framebuffer.
  // Those are two genuinely different knobs:
  // - "opacidade" (0.05-1) sets the vertex color's alpha channel — quantized
  //   to 8-bit, this is ordinary per-dot transparency.
  // - "brilho" (0.02-2.5) is the layer's `opacity` prop — a full-float
  //   uniform, NOT quantized, so it can exceed 1. Because additive blending
  //   sums N overlapping dots' contributions before the framebuffer clamps
  //   to white, this float gain is what actually controls how many stacked
  //   establishments it takes to saturate a "stacked" pixel to white,
  //   largely independent of how transparent a single isolated dot looks.
  function buildLayer(points, layerCfg, opacityAlpha, brilhoGain, radius) {
    var color = layerCfg.color.concat([Math.round(255 * opacityAlpha)]);
    return new deck.ScatterplotLayer({
      id: "estabelecimentos",
      data: {
        length: points.n,
        attributes: {
          getPosition: { value: points.positions, size: 2 },
        },
      },
      getFillColor: color,
      getRadius: radius,
      radiusUnits: "pixels",
      opacity: brilhoGain,
      pickable: false,
      // kepler.gl's point layer always faces the camera. Without this,
      // ScatterplotLayer's default (billboard:false) draws each dot as a flat
      // disc lying on the ground plane, which perspective-squishes into a
      // visible ellipse under the pitch:50 tilt — dots look stretched/blobby
      // instead of the crisp small circles in the kepler.gl reference.
      billboard: true,
      parameters: {
        blend: true,
        blendFunc: [WebGLRenderingContext.SRC_ALPHA, WebGLRenderingContext.ONE],
        blendEquation: WebGLRenderingContext.FUNC_ADD,
        depthTest: false,
      },
    });
  }

  // "tamanho" (dotsize) is a multiplier of the default radius — 1 means the
  // current/default size (the kepler-matched radius). All three sliders
  // share one rebuild so moving any one reflects the others' current
  // positions instead of resetting them.
  function wireSliders(points, layerCfg, overlay) {
    var opacity = document.getElementById("opacity");
    var brightness = document.getElementById("brightness");
    var dotsize = document.getElementById("dotsize");
    if (!opacity || !brightness || !dotsize) return;
    opacity.value = layerCfg.opacity;
    brightness.value = 1;
    dotsize.value = 1;
    function rebuild() {
      var opacityAlpha = parseFloat(opacity.value);
      var brilhoGain = parseFloat(brightness.value);
      var radius = layerCfg.radius * parseFloat(dotsize.value);
      overlay.setProps({ layers: [buildLayer(points, layerCfg, opacityAlpha, brilhoGain, radius)] });
    }
    opacity.addEventListener("input", rebuild);
    brightness.addEventListener("input", rebuild);
    dotsize.addEventListener("input", rebuild);
  }

  function render(points, bbox, layerCfg, mapState) {
    var view = fitBounds(bbox, window.innerWidth, window.innerHeight, 40);
    // minZoom caps how far a user can zoom OUT interactively — but it must
    // never exceed the zoom this page actually needs to fit its own data.
    // The BR (whole-country) page fits at ~zoom 3-4; forcing minZoom:8
    // there would crop the initial "see all of Brazil" view down to a
    // sliver. Per-state pages mostly fit above 8 anyway, so this only
    // matters for outliers like BR.
    var minZoom = Math.min(8, view.zoom);

    var map = new maplibregl.Map({
      container: "map",
      style: DARK_STYLE,
      center: [view.longitude, view.latitude],
      zoom: view.zoom,
      minZoom: minZoom,
      maxZoom: 15,
      pitch: mapState.pitch,
      bearing: mapState.bearing,
      antialias: true,
      dragRotate: mapState.dragRotate,
    });

    map.on("load", function () {
      hideRoads(map);
      var overlay = new deck.MapboxOverlay({
        interleaved: false,
        layers: [buildLayer(points, layerCfg, layerCfg.opacity, 1, layerCfg.radius)],
      });
      map.addControl(overlay);
      wireSliders(points, layerCfg, overlay);
      wireZoomReadout(map);
    });
  }

  function wireZoomReadout(map) {
    var el = document.getElementById("zoomval");
    function update() {
      var z = map.getZoom().toFixed(2);
      if (el) el.textContent = z;
      console.log("zoom:", z);
    }
    map.on("move", update);
    update();
  }

  function main() {
    setLoading("carregando " + uf + "…");
    Promise.all([
      fetch("../data/meta.json").then(function (r) { return r.json(); }),
      fetch("../config_template.json").then(function (r) { return r.json(); }),
    ])
      .then(function (results) {
        var meta = results[0], template = results[1];
        var info = meta[uf];
        if (!info) throw new Error("sem dados para UF " + uf);

        var layerConfig = template.config.config.visState.layers[0].config;
        var layerCfg = {
          color: layerConfig.color,
          radius: layerConfig.visConfig.radius * KEPLER_RADIUS_TO_PIXELS,
          opacity: layerConfig.visConfig.opacity,
        };
        var mapState = template.config.config.mapState;

        var hud = document.getElementById("hud");
        if (hud) {
          hud.innerHTML =
            '<div class="uf-title">' + (config.title || uf) + "</div>" +
            '<div class="uf-stats">' +
            info.n_estab_geolocalizados.toLocaleString("pt-BR") +
            " estabelecimentos geolocalizados (" +
            (info.n_estab_ativos ? ((info.n_estab_geolocalizados / info.n_estab_ativos) * 100).toFixed(1) : "0") +
            "% dos " +
            info.n_estab_ativos.toLocaleString("pt-BR") +
            " ativos) &middot; <a href=\"../\">todos os estados</a></div>";
        }

        var dataUrl = new URL("../data/" + ufLower + ".bin.gz", window.location.href).href;
        return loadPointsInWorker(dataUrl).then(function (points) {
          setLoading("");
          render(points, info.bbox, layerCfg, mapState);
        });
      })
      .catch(function (err) {
        console.error(err);
        setLoading("erro ao carregar " + uf + ": " + err.message);
      });
  }

  main();
})();
