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

  if (!reducedMotion.matches && "IntersectionObserver" in window) {
    var revealTargets = document.querySelectorAll(".landing-benefits, .landing-how-preview, .landing-safety, .landing-about, .landing-footer");
    revealTargets.forEach(function (target) { target.classList.add("reveal-on-scroll"); });
    var observer = new IntersectionObserver(function (entries) {
      entries.forEach(function (entry) {
        if (entry.isIntersecting) {
          entry.target.classList.add("is-revealed");
          observer.unobserve(entry.target);
        }
      });
    }, { threshold: 0.14 });
    revealTargets.forEach(function (target) { observer.observe(target); });

    /* Children of a revealed section arrive in sequence rather than as one
       slab. The index drives a transition-delay via --stagger. */
    revealTargets.forEach(function (target) {
      var kids = target.querySelectorAll(
        ".section-kicker, h2, h3, p, .landing-preview-card, .editorial-link, .landing-about-photo, nav, .landing-wordmark"
      );
      var index = 0;
      kids.forEach(function (kid) {
        if (kid.closest(".method-track")) return;
        if (kid.parentElement && kid.parentElement.closest(".landing-preview-card")) return;
        kid.setAttribute("data-stagger", "");
        kid.style.setProperty("--stagger", String(index));
        index += 1;
      });
      target.querySelectorAll(".method-track li").forEach(function (item, i) {
        item.style.setProperty("--stagger", String(i));
      });
    });

    /* Numbers count up to their printed value when the card arrives, then
       are restored verbatim so the rendered text is never left altered. */
    var counters = document.querySelectorAll(".landing-preview-stats strong");
    counters.forEach(function (node) {
      var match = /^\s*(\d+(?:\.\d+)?)/.exec(node.textContent || "");
      if (!match) return;
      node.setAttribute("data-countup", "");
      node.dataset.finalText = node.textContent;
      node.dataset.target = match[1];
    });

    var countObserver = new IntersectionObserver(function (entries) {
      entries.forEach(function (entry) {
        if (!entry.isIntersecting) return;
        var node = entry.target;
        countObserver.unobserve(node);
        var target = parseFloat(node.dataset.target);
        var decimals = (node.dataset.target.split(".")[1] || "").length;
        var suffix = node.dataset.finalText.replace(/^\s*\d+(?:\.\d+)?/, "");
        var started = null;
        var DURATION = 900;

        function tick(now) {
          if (started === null) started = now;
          var t = Math.min((now - started) / DURATION, 1);
          var eased = 1 - Math.pow(1 - t, 3);
          node.textContent = (target * eased).toFixed(decimals) + suffix;
          if (t < 1) window.requestAnimationFrame(tick);
          else node.textContent = node.dataset.finalText;
        }
        window.requestAnimationFrame(tick);
      });
    }, { threshold: 0.6 });
    counters.forEach(function (node) {
      if (node.hasAttribute("data-countup")) countObserver.observe(node);
    });

    /* One rAF loop drives every scroll-linked value. */
    var track = document.querySelector(".method-track");
    var trackItems = track ? Array.prototype.slice.call(track.querySelectorAll("li")) : [];
    var photo = document.querySelector(".landing-about-photo");
    var heroContent = document.querySelector(".landing-content");

    var progress = document.createElement("div");
    progress.className = "scroll-progress";
    progress.setAttribute("aria-hidden", "true");
    progress.appendChild(document.createElement("span"));
    document.body.appendChild(progress);

    var root = document.documentElement;
    var ticking = false;

    function onScroll() {
      var scrollY = window.scrollY;
      var viewport = window.innerHeight;

      var scrollable = document.documentElement.scrollHeight - viewport;
      root.style.setProperty("--scroll-progress", String(scrollable > 0 ? Math.min(scrollY / scrollable, 1) : 0));

      var capped = Math.min(scrollY, 700);
      root.style.setProperty("--gaman-scroll-scale", String(1.015 + capped * 0.00004));
      root.style.setProperty("--gaman-scroll-shift", (capped * 0.025) + "px");

      /* Hero copy drifts up and dims at roughly half the video's rate, so the
         two layers separate as you leave the fold. */
      if (heroContent) {
        var heroT = Math.min(scrollY / (viewport * 0.85), 1);
        root.style.setProperty("--hero-shift", (-heroT * 90) + "px");
        root.style.setProperty("--hero-fade", String(1 - heroT * 0.9));
      }

      if (track) {
        var rect = track.getBoundingClientRect();
        var drawn = (viewport * 0.82 - rect.top) / (rect.height || 1);
        root.style.setProperty("--track-draw", String(Math.max(0, Math.min(drawn, 1))));
        trackItems.forEach(function (item) {
          var box = item.getBoundingClientRect();
          var mid = box.top + box.height / 2;
          item.classList.toggle("is-active", mid > 0 && mid < viewport * 0.66);
        });
      }

      if (photo) {
        var pr = photo.getBoundingClientRect();
        if (pr.bottom > 0 && pr.top < viewport) {
          var centred = (pr.top + pr.height / 2 - viewport / 2) / viewport;
          root.style.setProperty("--photo-shift", (centred * -34) + "px");
        }
      }

      ticking = false;
    }

    window.addEventListener("scroll", function () {
      if (ticking) return;
      ticking = true;
      window.requestAnimationFrame(onScroll);
    }, { passive: true });
    window.addEventListener("resize", onScroll, { passive: true });
    onScroll();
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
