/* dashboard.js — polls /stream every 3 s and updates all UI components */

// ── Chart setup ──────────────────────────────────────────────────────────────
const CHART_OPTS = (color) => ({
  type: "line",
  data: {
    labels: [],
    datasets: [{
      data: [],
      borderColor: color,
      backgroundColor: color + "22",
      borderWidth: 2,
      pointRadius: 0,
      tension: 0.35,
      fill: true,
    }]
  },
  options: {
    animation: false,
    responsive: true,
    maintainAspectRatio: true,
    scales: {
      x: { display: false },
      y: {
        grid: { color: "#30363d" },
        ticks: { color: "#8b949e", font: { size: 10 } }
      }
    },
    plugins: { legend: { display: false } }
  }
});

const charts = {
  temp: new Chart(document.getElementById("chart-temp"), CHART_OPTS("#58a6ff")),
  vib:  new Chart(document.getElementById("chart-vib"),  CHART_OPTS("#d29922")),
  load: new Chart(document.getElementById("chart-load"), CHART_OPTS("#3fb950")),
  risk: new Chart(document.getElementById("chart-risk"), CHART_OPTS("#f85149")),
};

// ── Gauge arc math ────────────────────────────────────────────────────────────
// The arc path spans 283 px (π × r where r=90).
const ARC_LEN = 283;
const gaugeFg  = document.getElementById("gauge-fg");
const gaugePct = document.getElementById("gauge-pct");

function setGauge(pct) {
  const dash = (pct / 100) * ARC_LEN;
  gaugeFg.setAttribute("stroke-dasharray", `${dash} ${ARC_LEN}`);
  gaugeFg.className.baseVal = "gauge-fg" +
    (pct >= 70 ? " critical" : pct >= 30 ? " warning" : "");
  gaugePct.textContent = pct.toFixed(1) + "%";
}

// ── Alert banner & log ────────────────────────────────────────────────────────
const banner    = document.getElementById("alert-banner");
const alertIcon = document.getElementById("alert-icon");
const alertText = document.getElementById("alert-text");
const alertLog  = document.getElementById("alert-log");

let lastLevel = "";

function setAlert(level, risk) {
  const MAP = {
    Normal:   { icon: "🟢", cls: "normal",   msg: "System Normal — All sensors within range" },
    Warning:  { icon: "🟡", cls: "warning",  msg: "⚠️  Warning — Elevated risk detected" },
    Critical: { icon: "🔴", cls: "critical", msg: "🚨 CRITICAL — Immediate inspection required!" },
  };
  const { icon, cls, msg } = MAP[level] || MAP.Normal;
  banner.className = `alert-banner ${cls}`;
  alertIcon.textContent = icon;
  alertText.textContent = msg;

  // Log entry on level change
  if (level !== lastLevel) {
    const li = document.createElement("li");
    li.className = cls;
    const t = new Date().toLocaleTimeString();
    li.innerHTML = `<span class="log-time">${t}</span>
                    <span class="log-level">${level}</span>
                    <span>Risk: ${risk}%</span>`;
    alertLog.prepend(li);
    // Keep max 20 entries
    while (alertLog.children.length > 20) alertLog.lastChild.remove();
    lastLevel = level;
  }
}

// ── Sensor cards ──────────────────────────────────────────────────────────────
function setCard(id, value, isAnomalyField) {
  document.getElementById(id).textContent = value;
}

function updateCards(cur) {
  const isAnomaly = cur.alert_level === "Critical";

  document.getElementById("val-temp").textContent  = cur.temperature   ?? "—";
  document.getElementById("val-vib").textContent   = cur.vibration     ?? "—";
  document.getElementById("val-load").textContent  = cur.engine_load   ?? "—";
  document.getElementById("val-hours").textContent = cur.operating_hours ?? "—";

  // Pulse cards red/yellow on anomaly
  ["card-temp","card-vib","card-load"].forEach(id => {
    document.getElementById(id).classList.toggle("anomaly", isAnomaly);
  });
}

// ── Chart update ──────────────────────────────────────────────────────────────
function pushChart(chart, label, value, maxLen = 60) {
  chart.data.labels.push(label);
  chart.data.datasets[0].data.push(value);
  if (chart.data.labels.length > maxLen) {
    chart.data.labels.shift();
    chart.data.datasets[0].data.shift();
  }
  chart.update("none");   // skip animation for perf
}

// ── Seed charts from history on load ──────────────────────────────────────────
function seedFromHistory(history) {
  history.forEach((h, i) => {
    const lbl = i.toString();
    pushChart(charts.temp, lbl, h.temperature);
    pushChart(charts.vib,  lbl, h.vibration);
    pushChart(charts.load, lbl, h.engine_load);
    pushChart(charts.risk, lbl, h.risk_score);
  });
}

// ── Main poll loop ────────────────────────────────────────────────────────────
let seeded = false;
let tickIndex = 0;

async function poll() {
  try {
    const res  = await fetch("/stream");
    const json = await res.json();
    const cur  = json.current;
    const hist = json.history;

    if (!seeded && hist.length > 0) {
      seedFromHistory(hist);
      seeded = true;
    }

    const lbl = new Date().toLocaleTimeString();
    pushChart(charts.temp, lbl, cur.temperature);
    pushChart(charts.vib,  lbl, cur.vibration);
    pushChart(charts.load, lbl, cur.engine_load);
    pushChart(charts.risk, lbl, cur.risk_score);

    setGauge(cur.risk_score);
    setAlert(cur.alert_level, cur.risk_score);
    updateCards(cur);

    document.getElementById("last-updated").textContent =
      "Updated " + new Date().toLocaleTimeString();
    document.getElementById("status-dot").style.background =
      cur.alert_level === "Critical" ? "#f85149" :
      cur.alert_level === "Warning"  ? "#d29922" : "#3fb950";

  } catch (e) {
    console.warn("Poll error:", e);
    document.getElementById("last-updated").textContent = "Connection error …";
  }
}

// Initial poll + recurring
poll();
setInterval(poll, 3000);
