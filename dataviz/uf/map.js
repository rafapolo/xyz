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

  // Zoom-driven dot geometry.
  //
  // radiusUnits:"pixels" keeps a dot the same size on screen at every zoom
  // while the points themselves spread apart 2x per zoom level. So a single
  // fixed tuning can only ever look right at one zoom: tune it for the fitted
  // "whole state" view and zooming in dilutes the cloud into invisible specks;
  // tune it for the close view and the far view saturates into white mush.
  //
  // These two endpoints are the two pictures we actually want:
  // - t=0 (min zoom): a top-down aerial plate. Sub-pixel dots, low alpha and
  //   low gain, so a city reads as continuous glowing texture whose *density*
  //   is the signal rather than as separate discs.
  // - t=1 (max zoom): a night perspective. Each dot is one visible lamp, so it
  //   needs real pixel area plus more alpha and more gain (see the additive
  //   blending note on buildLayer below — far out, thousands of dots stack per
  //   pixel and clamp to white; close in, dots are isolated and need the gain).
  // Each endpoint pair is exactly its slider's min/max, so the curve never
  // extrapolates past the control: at min zoom the knob sits hard against the
  // left stop, at max zoom against the right, and every value in between is
  // reachable both by zooming and by dragging. Changing a slider's min/max in
  // the page template means changing the matching pair here.
  var ZOOM_AUTO = {
    radius: [0.1, 2.5],  // multiplier of the kepler-matched base radius
    alpha: [0.05, 1.0],  // vertex color alpha (quantized to 8-bit)
    gain: [0.02, 2.5],   // layer `opacity` float uniform
  };

  // Everything hangs off one normalized position in the page's own interactive
  // zoom range — normalized per page because BR fits at ~zoom 3.7 while a small
  // state fits above 8, so the same absolute zoom is a very different altitude.
  //
  //   t = (z - zMin) / (zMax - zMin)          clamped to [0,1]
  //
  // The two knob families interpolate differently on purpose.
  //
  // radius is LINEAR in t: the dot grows in direct proportion to how far the
  // zoom has travelled, so half way between the two zoom stops is half way
  // between the smallest and largest dot. A geometric curve here spends most of
  // its travel down near the minimum and then rushes the last stretch, which
  // makes the middle zooms feel stuck.
  //
  //   f(t) = a + (b - a) * t
  //
  // alpha and gain stay GEOMETRIC: they are light contributions summed by
  // additive blending, and perceived brightness responds to ratios, not
  // differences — a constant ratio per zoom level is what reads as an even
  // ramp there.
  //
  //   f(t) = a * (b / a)^t
  function lerpLinear(range, t) {
    return range[0] + (range[1] - range[0]) * t;
  }

  function lerpGeom(range, t) {
    return range[0] * Math.pow(range[1] / range[0], t);
  }

  function clamp(v, lo, hi) {
    return Math.min(hi, Math.max(lo, v));
  }

  function autoParams(z, zMin, zMax) {
    var t = clamp((z - zMin) / Math.max(zMax - zMin, 1e-9), 0, 1);
    return {
      radius: lerpLinear(ZOOM_AUTO.radius, t),
      alpha: lerpGeom(ZOOM_AUTO.alpha, t),
      gain: lerpGeom(ZOOM_AUTO.gain, t),
    };
  }

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
  //
  // `binaryData` MUST be the same object reference across every rebuild: a
  // fresh wrapper makes deck.gl treat the data as changed and re-upload the
  // whole multi-million-point Float32Array, which is fatal now that we rebuild
  // on every zoom frame. With a stable reference and constant (non-function)
  // getFillColor/getRadius/opacity, a rebuild is just a uniform update.
  function buildLayer(binaryData, layerCfg, opacityAlpha, brilhoGain, radius) {
    var color = layerCfg.color.concat([Math.round(255 * opacityAlpha)]);
    return new deck.ScatterplotLayer({
      id: "estabelecimentos",
      data: binaryData,
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

  // The three sliders are ABSOLUTE readouts-and-controls, not trims: the zoom
  // curve writes the computed value straight into each slider's `value`, so the
  // knob slides on its own as you zoom and its position *is* the current value.
  // Their min/max are the originals (alpha 0.05-1, gain 0.02-2.5, radius
  // multiplier 0.1-2.5) and ZOOM_AUTO spans exactly those, so the knob travels
  // the full width of its track and nothing is reachable only by extrapolation.
  //
  // Dragging a slider overrides that value until the next zoom, which
  // re-asserts the curve — the cost of having the knobs track the zoom.
  function wireControls(binaryData, layerCfg, overlay, map) {
    var opacity = document.getElementById("opacity");
    var brightness = document.getElementById("brightness");
    var dotsize = document.getElementById("dotsize");
    var zoomval = document.getElementById("zoomval");
    var zMin = map.getMinZoom();
    var zMax = map.getMaxZoom();

    function set(el, v) {
      if (el) el.value = v;
    }

    function get(el, fallback) {
      var v = el ? parseFloat(el.value) : NaN;
      return isNaN(v) ? fallback : v;
    }

    // fromZoom: recompute from the curve and push the values into the sliders.
    // Otherwise the user just dragged one, so read the sliders as-is.
    function apply(fromZoom) {
      var z = map.getZoom();
      if (fromZoom) {
        var auto = autoParams(z, zMin, zMax);
        set(opacity, auto.alpha.toFixed(2));
        set(brightness, auto.gain.toFixed(2));
        set(dotsize, auto.radius.toFixed(2));
      }
      var alpha = clamp(get(opacity, 1), 0.05, 1);
      var gain = clamp(get(brightness, 1), 0.02, 2.5);
      var radius = layerCfg.radius * Math.max(get(dotsize, 1), 0.1);
      overlay.setProps({ layers: [buildLayer(binaryData, layerCfg, alpha, gain, radius)] });
      if (zoomval) zoomval.textContent = z.toFixed(2);
    }

    // "zoom" fires many times per second during a wheel/pinch — coalesce to at
    // most one rebuild per animation frame.
    var pendingFrame = false;
    var pendingZoom = false;
    function schedule(fromZoom) {
      if (fromZoom) pendingZoom = true;
      if (pendingFrame) return;
      pendingFrame = true;
      requestAnimationFrame(function () {
        pendingFrame = false;
        var wasZoom = pendingZoom;
        pendingZoom = false;
        apply(wasZoom);
      });
    }

    [opacity, brightness, dotsize].forEach(function (el) {
      if (el) el.addEventListener("input", function () { schedule(false); });
    });
    map.on("zoom", function () { schedule(true); });
    apply(true);
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

    // Built once, then shared by every rebuild — see buildLayer().
    var binaryData = {
      length: points.n,
      attributes: {
        getPosition: { value: points.positions, size: 2 },
      },
    };

    map.on("load", function () {
      hideRoads(map);
      var overlay = new deck.MapboxOverlay({
        interleaved: false,
        layers: [],
      });
      map.addControl(overlay);
      // wireControls() does the first apply(), which builds the layer at the
      // auto values for the initial (fitted) zoom.
      wireControls(binaryData, layerCfg, overlay, map);
    });
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
