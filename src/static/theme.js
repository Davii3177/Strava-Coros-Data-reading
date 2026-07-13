(function () {
  var CHART_CHROME = {
    light: { font: "#111111", grid: "#e8e8e8", ring: "#ffffff" },
    dark: { font: "#ffffff", grid: "#262626", ring: "#141414" },
  };

  function currentTheme() {
    var attr = document.documentElement.getAttribute("data-theme");
    if (attr) return attr;
    return window.matchMedia("(prefers-color-scheme: dark)").matches ? "dark" : "light";
  }

  function applyChartTheme(theme) {
    var chart = document.getElementById("pace-chart");
    if (!chart || !window.Plotly) return;
    var chrome = CHART_CHROME[theme] || CHART_CHROME.light;
    window.Plotly.relayout(chart, {
      "font.color": chrome.font,
      "xaxis.gridcolor": chrome.grid,
      "xaxis.linecolor": chrome.grid,
      "yaxis.gridcolor": chrome.grid,
      "yaxis.linecolor": chrome.grid,
    });
    var traceCount = (chart.data || []).length;
    if (traceCount) {
      window.Plotly.restyle(chart, { "marker.line.color": chrome.ring }, Array.from({ length: traceCount }, function (_, i) { return i; }));
    }
  }

  applyChartTheme(currentTheme());

  var button = document.getElementById("theme-toggle");
  if (button) {
    button.addEventListener("click", function () {
      var next = currentTheme() === "dark" ? "light" : "dark";
      document.documentElement.setAttribute("data-theme", next);
      localStorage.setItem("theme", next);
      applyChartTheme(next);
    });
  }
})();
