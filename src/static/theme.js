(function () {
  var CHART_CHROME = {
    light: { font: "#06294a", grid: "rgba(20,118,194,.22)", ring: "#ffffff" },
    dark: { font: "#fbf4ff", grid: "rgba(150,99,214,.28)", ring: "#20122f" },
  };

  function currentTheme() {
    var saved = document.documentElement.getAttribute("data-theme");
    return saved || (window.matchMedia("(prefers-color-scheme: dark)").matches ? "dark" : "light");
  }

  function updateToggle(theme) {
    var button = document.getElementById("theme-toggle");
    if (!button) return;
    var light = theme === "light";
    button.classList.add("theme-icon-button");
    button.setAttribute("aria-label", light ? "Switch to dark mode" : "Switch to light mode");
    button.setAttribute("title", light ? "Switch to dark mode" : "Switch to light mode");
    button.innerHTML = light
      ? '<svg viewBox="0 0 24 24" aria-hidden="true"><circle cx="12" cy="12" r="4"></circle><path d="M12 2v2M12 20v2M4.93 4.93l1.41 1.41M17.66 17.66l1.41 1.41M2 12h2M20 12h2M4.93 19.07l1.41-1.41M17.66 6.34l1.41-1.41"></path></svg><span class="sr-only">Light mode</span>'
      : '<svg viewBox="0 0 24 24" aria-hidden="true"><path d="M20.5 15.4A8.5 8.5 0 0 1 8.6 3.5 8.5 8.5 0 1 0 20.5 15.4Z"></path></svg><span class="sr-only">Dark mode</span>';
  }

  function applyChartTheme(theme) {
    var chart = document.getElementById("pace-chart");
    if (!chart || !window.Plotly) return;
    var chrome = CHART_CHROME[theme];
    window.Plotly.relayout(chart, { "font.color": chrome.font, "xaxis.gridcolor": chrome.grid, "xaxis.linecolor": chrome.grid, "yaxis.gridcolor": chrome.grid, "yaxis.linecolor": chrome.grid });
    var traces = (chart.data || []).length;
    if (traces) window.Plotly.restyle(chart, { "marker.line.color": chrome.ring }, Array.from({ length: traces }, function (_, index) { return index; }));
  }

  function mountProductFlow() {
    var hero = document.querySelector(".landing-hero");
    if (!hero || hero.querySelector(".product-flow")) return;
    hero.insertAdjacentHTML("beforeend", `
      <section class="product-flow" aria-label="How Gaman AI works">
        <div class="flow-kicker"><span>YOUR DATA, CONNECTED</span><i></i></div>
        <div class="flow-canvas" aria-hidden="true">
          <svg viewBox="0 0 500 420" preserveAspectRatio="xMidYMid meet">
            <defs><filter id="flow-glow"><feGaussianBlur stdDeviation="4" result="blur"/><feMerge><feMergeNode in="blur"/><feMergeNode in="SourceGraphic"/></feMerge></filter></defs>
            <path id="stream-strava" class="flow-line input-line" d="M82 105 C145 105 155 194 238 205"/>
            <path id="stream-coros" class="flow-line input-line" d="M82 310 C145 310 155 224 238 211"/>
            <path id="stream-analysis" class="flow-line output-line" d="M270 198 C337 185 353 92 429 82"/>
            <path id="stream-workout" class="flow-line output-line" d="M274 211 C341 211 357 211 429 211"/>
            <path id="stream-recovery" class="flow-line output-line" d="M270 224 C337 237 353 326 429 337"/>
            <circle class="flow-packet packet-blue" r="5"><animateMotion dur="2.6s" repeatCount="indefinite"><mpath href="#stream-strava"/></animateMotion></circle>
            <circle class="flow-packet packet-yellow" r="5"><animateMotion dur="3s" begin="-.8s" repeatCount="indefinite"><mpath href="#stream-coros"/></animateMotion></circle>
            <circle class="flow-packet packet-green" r="4"><animateMotion dur="2.7s" begin="-1.1s" repeatCount="indefinite"><mpath href="#stream-analysis"/></animateMotion></circle>
            <circle class="flow-packet packet-purple" r="4"><animateMotion dur="2.9s" begin="-.4s" repeatCount="indefinite"><mpath href="#stream-workout"/></animateMotion></circle>
            <circle class="flow-packet packet-red" r="4"><animateMotion dur="3.1s" begin="-1.7s" repeatCount="indefinite"><mpath href="#stream-recovery"/></animateMotion></circle>
            <circle class="core-ring ring-one" cx="255" cy="211" r="52"/><circle class="core-ring ring-two" cx="255" cy="211" r="68"/>
          </svg>
          <div class="flow-node source-node strava-node"><small>SOURCE 01</small><strong>STRAVA</strong><span>ACTIVITIES</span></div>
          <div class="flow-node source-node coros-node"><small>SOURCE 02</small><strong>COROS</strong><span>ACTIVITIES</span></div>
          <div class="flow-core"><span>GA</span><strong>GAMAN AI</strong><small>ANALYZE</small></div>
          <div class="flow-node output-node analysis-node"><small>UNDERSTAND</small><strong>TRAINING</strong><span>PACE + LOAD</span></div>
          <div class="flow-node output-node workout-node"><small>PREPARE</small><strong>WORKOUTS</strong><span>NEXT 7 DAYS</span></div>
          <div class="flow-node output-node recovery-node"><small>RECOVER</small><strong>BODY CHECK</strong><span>GUIDANCE</span></div>
        </div>
        <div class="flow-caption"><span>ACTIVITY</span><b>→</b><span>INSIGHT</span><b>→</b><span>ACTION</span></div>
      </section>`);
  }

  var initialTheme = currentTheme();
  applyChartTheme(initialTheme);
  updateToggle(initialTheme);
  mountProductFlow();
  var toggle = document.getElementById("theme-toggle");
  if (toggle) toggle.addEventListener("click", function () {
    var next = currentTheme() === "dark" ? "light" : "dark";
    document.documentElement.setAttribute("data-theme", next);
    localStorage.setItem("theme", next);
    applyChartTheme(next);
    updateToggle(next);
  });
}());
