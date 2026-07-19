(function () {
  "use strict";

  var reducedMotion = window.matchMedia("(prefers-reduced-motion: reduce)").matches;
  var loading = false;

  function showLoading() {
    if (loading || reducedMotion) return;
    loading = true;
    document.body.classList.add("is-navigating");
  }

  function isInternalNavigation(link, event) {
    if (event.defaultPrevented || event.button !== 0 || event.metaKey || event.ctrlKey || event.shiftKey || event.altKey) return false;
    if (link.target || link.hasAttribute("download") || link.getAttribute("href").charAt(0) === "#") return false;
    var url = new URL(link.href, window.location.href);
    return url.origin === window.location.origin && url.href !== window.location.href;
  }

  document.addEventListener("click", function (event) {
    var link = event.target.closest("a[href]");
    if (link && isInternalNavigation(link, event)) showLoading();
  });

  document.addEventListener("submit", function (event) {
    var form = event.target;
    if (!event.defaultPrevented && form.matches("form") && !form.hasAttribute("data-no-page-loader")) showLoading();
  });

  window.addEventListener("pageshow", function () {
    loading = false;
    document.body.classList.remove("is-navigating");
  });
}());
