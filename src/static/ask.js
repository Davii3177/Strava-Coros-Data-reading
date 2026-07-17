(function () {
  var launcher = document.querySelector("[data-ask-open]");
  var panel = document.getElementById("ask-panel");
  if (!launcher || !panel) return;

  var log = document.getElementById("ask-log");
  var form = document.getElementById("ask-form");
  var input = document.getElementById("ask-input");
  var closeButton = panel.querySelector("[data-ask-close]");
  var history = [];
  var busy = false;

  function open() {
    if (typeof panel.showModal === "function") { if (!panel.open) panel.showModal(); }
    else panel.setAttribute("open", "");
    if (!log.childElementCount) greeting();
    input.focus();
  }
  function close() {
    if (typeof panel.close === "function") { if (panel.open) panel.close(); }
    else panel.removeAttribute("open");
    launcher.focus();
  }
  launcher.addEventListener("click", open);
  closeButton.addEventListener("click", close);
  // Close when clicking the backdrop (outside the dialog content box).
  panel.addEventListener("click", function (event) {
    if (event.target === panel) close();
  });

  function bubble(role, text) {
    var wrap = document.createElement("div");
    wrap.className = "ask-msg ask-" + role;
    var body = document.createElement("div");
    body.className = "ask-bubble";
    body.textContent = text;
    wrap.appendChild(body);
    log.appendChild(wrap);
    log.scrollTop = log.scrollHeight;
    return wrap;
  }

  function greeting() {
    bubble("bot", "Hi — I’m Gaman. Ask about today’s session, your recent load, pacing, or an upcoming race. I answer from your logged data.");
    var chips = document.createElement("div");
    chips.className = "ask-chips";
    ["Should I run today?", "How’s my recent training load?", "What should I do before my race?"].forEach(function (question) {
      var chip = document.createElement("button");
      chip.type = "button";
      chip.className = "ask-chip";
      chip.textContent = question;
      chip.addEventListener("click", function () { input.value = question; send(); });
      chips.appendChild(chip);
    });
    log.appendChild(chips);
    log.scrollTop = log.scrollHeight;
  }

  function autosize() {
    input.style.height = "auto";
    input.style.height = Math.min(input.scrollHeight, 120) + "px";
  }

  async function send() {
    if (busy) return;
    var question = input.value.trim();
    if (!question) return;

    var chips = log.querySelector(".ask-chips");
    if (chips) chips.remove();
    bubble("user", question);
    input.value = "";
    autosize();

    busy = true;
    form.classList.add("is-busy");
    var typing = bubble("bot", "…");
    typing.classList.add("ask-typing");

    try {
      var response = await fetch("/api/ask", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ question: question, history: history }),
      });
      var data = await response.json();
      typing.remove();
      if (!response.ok) throw new Error(data.error || "Ask Gaman is unavailable right now.");
      bubble("bot", data.answer);
      if (data.ok) {
        history.push({ role: "user", content: question });
        history.push({ role: "assistant", content: data.answer });
        history = history.slice(-8);
      }
    } catch (error) {
      if (typing.parentElement) typing.remove();
      bubble("bot", error.message || "Ask Gaman is unavailable right now.");
    } finally {
      busy = false;
      form.classList.remove("is-busy");
      input.focus();
    }
  }

  form.addEventListener("submit", function (event) { event.preventDefault(); send(); });
  input.addEventListener("input", autosize);
  input.addEventListener("keydown", function (event) {
    if (event.key === "Enter" && !event.shiftKey) { event.preventDefault(); send(); }
  });
}());
