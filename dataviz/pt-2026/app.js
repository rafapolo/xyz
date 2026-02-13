const legendPanel = d3.select("#legend");
const mainlandTitle = d3.select("#mainland-title");

const svgConfigs = [
  { selector: "#map-mainland", nuts1: "Continente", width: 840, height: 620 },
];
const INITIAL_ZOOM = 1.2;
const INITIAL_LOCALITY = "Lisboa";

const NO_DATA_COLOR = "#4b5563";
const SPECIAL_REGION_MAP = {
  "calheta [r.a.a.]": "Calheta de São Jorge",
  "calheta [r.a.m.]": "Calheta",
  "lagoa": "Lagoa [Faro]",
  "vila da praia da vitoria": "Praia da Vitória",
};
const NON_MUNICIPAL_REGIONS = new Set(["Portugal", "Portugal + Estrangeiro", "Estrangeiro"]);
const NON_CANDIDATE_TYPES = new Set(["Voto em branco", "Voto nulo"]);
const CANDIDATE_COLORS = ["#0f766e", "#b91c1c", "#1d4ed8", "#854d0e", "#7c3aed", "#be185d"];
const CANDIDATE_COLOR_OVERRIDES = {
  "andre ventura": "#2f6fed",
  "antonio jose seguro": "#e34a4a",
};

const normalize = (value) =>
  (value || "")
    .trim()
    .normalize("NFD")
    .replace(/[\u0300-\u036f]/g, "")
    .toLowerCase();

const formatVotes = d3.format(",");
const formatPct = d3.format(".1%");
const escapeHtml = (value) =>
  (value || "")
    .replaceAll("&", "&amp;")
    .replaceAll("<", "&lt;")
    .replaceAll(">", "&gt;")
    .replaceAll('"', "&quot;")
    .replaceAll("'", "&#39;");

const resolveCsvRegionToMapRegion = (csvRegion) => {
  const key = normalize(csvRegion);
  return SPECIAL_REGION_MAP[key] || csvRegion.trim();
};
const resolveCandidateColor = (candidate, fallbackColor) =>
  CANDIDATE_COLOR_OVERRIDES[normalize(candidate)] || fallbackColor;

Promise.all([d3.json("./data/municipalities.geojson"), d3.csv("./votos_portugal_2026.csv")])
  .then(([geojson, rows]) => {
    const cleanRows = rows
      .map((row) => ({
        ano: (row.Ano || "").trim(),
        region: (row["Região"] || "").trim(),
        type: (row["Tipo de voto/Candidato"] || "").trim(),
        votes: Number((row.Votos || "").toString().replace(/[^\d]/g, "")) || 0,
      }))
      .filter(
        (row) =>
          row.region &&
          row.type &&
          row.votes >= 0 &&
          !NON_MUNICIPAL_REGIONS.has(row.region)
      );

    const latestAno = d3.max(cleanRows, (d) => d.ano) || "2026";
    d3.select(".header p").text("Mapa colorido por distribuiçao dos votos. Clique numa localidade.");

    const groupedByRegion = d3.group(cleanRows, (d) => resolveCsvRegionToMapRegion(d.region));
    const electionByRegion = new Map();
    const allCandidates = new Set();
    const candidateTotals = d3.rollup(
      cleanRows.filter((d) => !NON_CANDIDATE_TYPES.has(d.type)),
      (v) => d3.sum(v, (d) => d.votes),
      (d) => d.type
    );

    groupedByRegion.forEach((entries, regionKey) => {
      const totalsByType = d3.rollup(
        entries,
        (v) => d3.sum(v, (d) => d.votes),
        (d) => d.type
      );

      const candidateRows = Array.from(totalsByType.entries())
        .filter(([type]) => !NON_CANDIDATE_TYPES.has(type))
        .map(([type, votes]) => ({ type, votes }))
        .sort((a, b) => d3.descending(a.votes, b.votes));

      candidateRows.forEach((row) => allCandidates.add(row.type));

      const allRows = Array.from(totalsByType.entries())
        .map(([type, votes]) => ({ type, votes }))
        .sort((a, b) => d3.descending(a.votes, b.votes));

      electionByRegion.set(regionKey, {
        winner: candidateRows[0]?.type || null,
        winnerVotes: candidateRows[0]?.votes || 0,
        totalVotes: d3.sum(allRows, (d) => d.votes),
        candidateVotes: new Map(candidateRows.map((row) => [row.type, row.votes])),
        rows: allRows,
      });
    });

    const candidateDomain = Array.from(allCandidates).sort(
      (a, b) => (candidateTotals.get(b) || 0) - (candidateTotals.get(a) || 0)
    );
    const twoCandidateMode = candidateDomain.length === 2;
    let candidateA = candidateDomain[0] || null;
    let candidateB = candidateDomain[1] || null;
    if (twoCandidateMode) {
      const seguro = candidateDomain.find((c) => normalize(c).includes("seguro"));
      const ventura = candidateDomain.find((c) => normalize(c).includes("ventura"));
      if (seguro && ventura) {
        candidateB = seguro;   // esquerda
        candidateA = ventura;  // direita
      }
    }
    const fallbackScale = d3.scaleOrdinal(
      candidateDomain,
      CANDIDATE_COLORS.slice(0, candidateDomain.length)
    );
    const color = (candidate) => resolveCandidateColor(candidate, fallbackScale(candidate));
    const mixColor =
      twoCandidateMode &&
      d3
        .scaleLinear()
        .domain([0, 1])
        .range([color(candidateB), color(candidateA)])
        .interpolate(d3.interpolateRgb);

    let renderSelection = () => {};
    const selectLocality = (locality, election) => {
      d3.selectAll(".municipality").classed("active", false);
      d3.selectAll(`.municipality[data-region-key="${CSS.escape(locality)}"]`)
        .classed("active", true)
        .raise();
      renderSelection(locality, election);
    };

    geojson.features.forEach((feature) => {
      const regionKey = feature.properties.region_key;
      feature.properties.results = electionByRegion.get(regionKey) || null;
    });

    svgConfigs.forEach((cfg) => {
      const localFeatures = geojson.features.filter((f) => f.properties.nuts1 === cfg.nuts1);
      const localCollection = { type: "FeatureCollection", features: localFeatures };

      const svg = d3.select(cfg.selector);
      svg.attr("viewBox", `0 0 ${cfg.width} ${cfg.height}`);
      const g = svg.append("g");
      const mapLayer = g.append("g");

      const projection = d3.geoMercator().fitSize([cfg.width, cfg.height], localCollection);
      const path = d3.geoPath(projection);

      const zoom = d3
        .zoom()
        .scaleExtent([1, 8])
        .translateExtent([
          [0, 0],
          [cfg.width, cfg.height],
        ])
        .extent([
          [0, 0],
          [cfg.width, cfg.height],
        ])
        .on("zoom", (event) => {
          mapLayer.attr("transform", event.transform);
        });

      svg.call(zoom);

      const initialTransform = d3.zoomIdentity
        .translate(
          (cfg.width * (1 - INITIAL_ZOOM)) / 2,
          (cfg.height * (1 - INITIAL_ZOOM)) / 2
        )
        .scale(INITIAL_ZOOM);

      svg.call(zoom.transform, initialTransform);

      mapLayer
        .selectAll("path")
        .data(localFeatures)
        .join("path")
        .attr("class", "municipality")
        .attr("d", path)
        .attr("data-region-key", (d) => d.properties.region_key)
        .style("fill", (d) => {
          const election = d.properties.results;
          if (!election) return NO_DATA_COLOR;

          if (twoCandidateMode) {
            const votesA = election.candidateVotes.get(candidateA) || 0;
            const votesB = election.candidateVotes.get(candidateB) || 0;
            const total = votesA + votesB;
            if (total === 0) return NO_DATA_COLOR;
            const shareA = votesA / total;
            return mixColor(shareA);
          }

          const winner = election.winner;
          return winner ? color(winner) : NO_DATA_COLOR;
        })
        .on("click", function (_, d) {
          const locality = d.properties.region_key;
          const election = d.properties.results;
          selectLocality(locality, election);
        })
        .append("title")
        .text((d) => {
          const election = d.properties.results;
          if (!election) return `${d.properties.region_key}: sem dados`;
          if (!twoCandidateMode) return `${d.properties.region_key}: ${election.winner}`;

          const votesA = election.candidateVotes.get(candidateA) || 0;
          const votesB = election.candidateVotes.get(candidateB) || 0;
          const total = votesA + votesB;
          const shareA = total > 0 ? votesA / total : 0;
          const shareB = total > 0 ? votesB / total : 0;
          return `${d.properties.region_key}: ${candidateA} ${formatPct(shareA)} | ${candidateB} ${formatPct(shareB)}`;
        });
    });

    if (twoCandidateMode) {
      legendPanel.html(`
        <div class="mix-legend">
          <div class="mix-legend-head">
            <span>${escapeHtml(candidateB)}</span>
            <span>${escapeHtml(candidateA)}</span>
          </div>
          <div class="mix-legend-bar-wrap">
            <div class="mix-legend-bar" style="background: linear-gradient(to right, ${color(candidateB)} 0%, ${color(candidateA)} 100%);"></div>
            <div class="mix-pointer mix-pointer-b" id="mix-pointer-b" style="left:0%;background:${color(candidateB)};"></div>
            <div class="mix-pointer mix-pointer-a" id="mix-pointer-a" style="left:100%;background:${color(candidateA)};"></div>
          </div>
          <div class="mix-legend-ticks">
            <span>0%</span><span>25%</span><span>50%</span><span>75%</span><span>100%</span>
          </div>
          <div class="mix-legend-badges">
            <div class="mix-badge" id="mix-badge-b">
              <span class="mix-marker-dot" style="background:${color(candidateB)}"></span>
              <span id="mix-marker-b-label">${escapeHtml(candidateB)} 0.0%</span>
            </div>
            <div class="mix-badge" id="mix-badge-a">
              <span class="mix-marker-dot" style="background:${color(candidateA)}"></span>
              <span id="mix-marker-a-label">${escapeHtml(candidateA)} 0.0%</span>
            </div>
          </div>
        </div>
      `);

      const pointerA = d3.select("#mix-pointer-a");
      const pointerB = d3.select("#mix-pointer-b");
      const markerALabel = d3.select("#mix-marker-a-label");
      const markerBLabel = d3.select("#mix-marker-b-label");

      renderSelection = (locality, election) => {
        if (!election) {
          mainlandTitle.text(`Continente - ${locality} (sem dados)`);
          return;
        }

        const votesA = election.candidateVotes.get(candidateA) || 0;
        const votesB = election.candidateVotes.get(candidateB) || 0;
        const total = votesA + votesB;
        const shareA = total > 0 ? votesA / total : 0;
        const shareB = total > 0 ? votesB / total : 0;

        pointerA.style("left", `${shareA * 100}%`);
        pointerB.style("left", `${shareB * 100}%`);
        markerALabel.text(`${candidateA} ${formatPct(shareA)}`);
        markerBLabel.text(`${candidateB} ${formatPct(shareB)}`);
        mainlandTitle.text(`Continente - ${locality}`);
      };
    } else {
      const legendItems = [
        ...candidateDomain.map((candidate) => ({
          label: candidate,
          color: color(candidate),
        })),
      ];

      legendPanel
        .selectAll(".legend-item")
        .data(legendItems)
        .join("div")
        .attr("class", "legend-item")
        .html((d) => `<span class="legend-swatch" style="background:${d.color}"></span><span>${d.label}</span>`);

      renderSelection = () => {};
    }

    const initialFeature =
      geojson.features.find(
        (f) => normalize(f?.properties?.region_key) === normalize(INITIAL_LOCALITY)
      ) || null;
    if (initialFeature) {
      selectLocality(initialFeature.properties.region_key, initialFeature.properties.results);
    }

  })
  .catch((error) => {
    mainlandTitle.text("Continente");
    legendPanel.html('<div class="legend-item">Erro ao carregar dados do mapa eleitoral.</div>');
    console.error(error);
  });
