(function () {
  document.querySelectorAll("[data-run-panel]").forEach(function (panel) {
    var search = panel.querySelector("[data-run-search]");
    var toggle = panel.querySelector("[data-panel-toggle]");
    var empty = panel.querySelector("[data-panel-empty]");
    var items = Array.from(panel.querySelectorAll("[data-run-item]"));
    var limit = Number(panel.getAttribute("data-default-limit")) || 4;
    var expanded = false;

    function render() {
      var query = search ? search.value.trim().toLowerCase() : "";
      var matches = items.filter(function (item) {
        return !query || (item.getAttribute("data-search") || "").toLowerCase().includes(query);
      });

      items.forEach(function (item) { item.hidden = true; });
      matches.forEach(function (item, index) {
        item.hidden = !query && !expanded && index >= limit;
      });

      if (empty) empty.hidden = matches.length !== 0;
      if (toggle) {
        toggle.hidden = items.length <= limit || Boolean(query);
        toggle.textContent = expanded ? "Show less" : "Show all (" + items.length + ")";
        toggle.setAttribute("aria-expanded", String(expanded));
      }
    }

    if (search) search.addEventListener("input", render);
    if (toggle) toggle.addEventListener("click", function () {
      expanded = !expanded;
      render();
    });
    render();
  });
}());
