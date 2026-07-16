(function () {
  var heroVideo = document.querySelector("video.landing-hero-media");
  var reducedMotion = window.matchMedia("(prefers-reduced-motion: reduce)");
  var compactScreen = window.matchMedia("(max-width: 640px)");

  function updateHeroMotion(event) {
    if (!heroVideo) return;
    var saveData = navigator.connection && navigator.connection.saveData;
    if (event.matches || compactScreen.matches || saveData) {
      heroVideo.pause();
      heroVideo.currentTime = 0;
      return;
    }
    var playback = heroVideo.play();
    if (playback && typeof playback.catch === "function") playback.catch(function () {});
  }

  updateHeroMotion(reducedMotion);
  if (typeof reducedMotion.addEventListener === "function") {
    reducedMotion.addEventListener("change", updateHeroMotion);
    compactScreen.addEventListener("change", updateHeroMotion);
  } else if (typeof reducedMotion.addListener === "function") {
    reducedMotion.addListener(updateHeroMotion);
    compactScreen.addListener(updateHeroMotion);
  }

  var dialog = document.getElementById("login-dialog");
  if (!dialog) return;

  var password = document.getElementById("password");
  var lastOpener = null;

  function openDialog(event) {
    if (event) {
      event.preventDefault();
      lastOpener = event.currentTarget;
    }
    if (typeof dialog.showModal === "function") dialog.showModal();
    else dialog.setAttribute("open", "");
    window.setTimeout(function () { if (password) password.focus(); }, 0);
  }

  function closeDialog() {
    if (typeof dialog.close === "function") dialog.close();
    else {
      dialog.removeAttribute("open");
      if (lastOpener) lastOpener.focus();
    }
  }

  document.querySelectorAll("[data-login-open]").forEach(function (trigger) {
    trigger.addEventListener("click", openDialog);
  });

  var close = dialog.querySelector("[data-login-close]");
  if (close) close.addEventListener("click", closeDialog);
  dialog.addEventListener("click", function (event) {
    if (event.target === dialog) closeDialog();
  });
  dialog.addEventListener("close", function () {
    if (lastOpener) lastOpener.focus();
  });

  if (dialog.dataset.autoOpen === "true") openDialog();
}());
