# Design Brief: De-genericize the Gaman website

You're working in a Flask app for a running-analytics product called Gaman. The
frontend lives in `src/templates/` (Jinja2 HTML) and `src/static/style.css` (a single
~130KB stylesheet using CSS custom properties). The landing page is `login.html`; the
authenticated product is `dashboard.html`. Tests in `tests/test_dashboard_rendering.py`
assert on rendered markup — keep them green (update expectations only when a change is
intentional).

## Goal

The site currently reads as AI-generated/templated. Make it look deliberately designed
and specific, without a full rebuild. Preserve the good existing decisions:

- the hard-offset shadow (`--shadow: 0 5px 0` with no blur),
- the monochrome-purple brand identity,
- `tabular-nums` on all data,
- the honesty framing (measured data vs. estimate vs. model guidance) — that framing is
  the product's personality; lean into it.

## Tasks (in priority order)

1. **Replace the fonts.** Headings currently use `Times New Roman` and body uses `Arial`
   — both read as unstyled defaults. Introduce a self-hosted (no external CDN) pairing:
   one characterful display serif for headings (e.g. Fraunces or Instrument Serif) and one
   clean grotesque for body/UI/data (e.g. Space Grotesk or Geist). Add `@font-face` with
   locally stored `woff2` files; update the `font-family` declarations throughout
   `style.css`. Keep `tabular-nums` on numeric data.

2. **Break the repetitive section rhythm.** Every landing section in `login.html` is the
   same molecule: `section-kicker` → serif headline → one sentence. Remove the numbered
   `01/02/03` benefit cards and replace them with something showing the actual product (a
   real dashboard screenshot or one annotated live stat). Vary section shapes so they
   aren't all eyebrow+headline+subtext.

3. **Rewrite the landing copy** in a specific, human voice. Replace abstract parallel
   fragments ("Less dashboard noise. More useful direction.") with concrete runner moments
   (e.g. the 6am "do I run the intervals or bag it" decision). Specificity over polish.

4. **Fix the semantic colors.** In `:root`, `--red`, `--green`, `--yellow` are all
   purple-shifted, so status states look identical. Keep purple as the brand accent, but
   give success/warning/danger genuinely distinct, accessible hues. Update both the light
   `:root` and the `[data-theme="dark"]` / `prefers-color-scheme: dark` blocks.

5. **Rethink the cinematic-video hero** (`.landing-hero`). The full-bleed nature video +
   dark scrim + white serif headline is the most-cloned template hero. Make it
   product-forward — e.g. the video framed alongside a real dashboard view rather than
   filling the screen behind text.

## Constraints

- No external CDNs or third-party media (self-host everything).
- Maintain existing accessibility (skip links, ARIA, visible focus, reduced-motion handling).
- Keep the site responsive and the dark theme working.
- Run the test suite after changes (`PYTHONPATH=src python -m pytest tests -q`) and update
  any assertions you intentionally changed.
