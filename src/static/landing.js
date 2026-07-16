(function () {
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
