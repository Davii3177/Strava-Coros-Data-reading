(function () {
  var DEFAULT_COLLAPSED = new Set([
    "goal-center", "personal-records", "shoes", "recovery-timeline",
    "pace-trends", "runs", "calendar", "recovery", "workouts", "races"
  ]);
  var sections = [];

  function savedState(id) {
    try { return localStorage.getItem("gaman-section-v2-" + id); } catch (_) { return null; }
  }

  function saveState(id, collapsed) {
    try { localStorage.setItem("gaman-section-v2-" + id, collapsed ? "collapsed" : "expanded"); } catch (_) { /* Storage is optional. */ }
  }

  function setCollapsed(section, collapsed, persist) {
    var button = section.querySelector(".section-collapse-button");
    section.classList.toggle("is-section-collapsed", collapsed);
    if (button) {
      button.setAttribute("aria-expanded", String(!collapsed));
      button.textContent = collapsed ? "View" : "Close";
      button.setAttribute("title", collapsed ? "Open this section" : "Collapse this section");
    }
    if (persist) saveState(section.id, collapsed);
    if (!collapsed) window.setTimeout(function () { window.dispatchEvent(new Event("resize")); }, 50);
  }

  document.querySelectorAll(".card[id]").forEach(function (section) {
    if (!DEFAULT_COLLAPSED.has(section.id)) return;
    var heading = Array.from(section.children).find(function (child) {
      return child.classList && child.classList.contains("section-heading");
    });
    if (!heading) return;

    section.classList.add("dashboard-collapsible");
    var button = document.createElement("button");
    button.type = "button";
    button.className = "section-collapse-button";
    button.addEventListener("click", function () {
      setCollapsed(section, !section.classList.contains("is-section-collapsed"), true);
    });
    heading.appendChild(button);
    sections.push(section);

    var stored = savedState(section.id);
    var linked = window.location.hash === "#" + section.id;
    setCollapsed(section, linked ? false : stored ? stored === "collapsed" : true, false);
  });

  function openLinkedSection() {
    if (!window.location.hash) return;
    var target = document.getElementById(window.location.hash.slice(1));
    if (target && target.classList.contains("dashboard-collapsible")) setCollapsed(target, false, true);
  }

  document.addEventListener("click", function (event) {
    var link = event.target.closest('a[href^="#"]');
    if (!link || link.getAttribute("href") === "#") return;
    var target = document.getElementById(link.getAttribute("href").slice(1));
    if (target && target.classList.contains("dashboard-collapsible")) setCollapsed(target, false, true);
  });
  window.addEventListener("hashchange", openLinkedSection);

  var expandAll = document.querySelector("[data-expand-all]");
  var compactAll = document.querySelector("[data-compact-all]");
  if (expandAll) expandAll.addEventListener("click", function () {
    sections.forEach(function (section) { setCollapsed(section, false, true); });
  });
  if (compactAll) compactAll.addEventListener("click", function () {
    sections.forEach(function (section) { setCollapsed(section, true, true); });
    var reducedMotion = window.matchMedia("(prefers-reduced-motion: reduce)").matches;
    document.getElementById("daily").scrollIntoView({ behavior: reducedMotion ? "auto" : "smooth", block: "start" });
  });
}());
