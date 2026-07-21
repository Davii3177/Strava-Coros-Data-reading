"""Generate src/templates/research.html from RESEARCH.md.

One-time (re)build step, run manually whenever RESEARCH.md changes:

    python tools/build_research_page.py

Uses the python-markdown package at build time only -- the generated HTML is
committed, so the deployed app needs no markdown dependency. The document
content is emitted verbatim (no claims added or removed); only structure and
styling hooks are applied:
- tables are wrapped in scrollable .table-wrap containers
- region headings get stable ids (region-0 ... region-12) for deep links
- other h2 headings get slugified ids
- external links open in a new tab
"""
import re
from pathlib import Path

import markdown

ROOT = Path(__file__).resolve().parent.parent
SOURCE = ROOT / "RESEARCH.md"
TARGET = ROOT / "src" / "templates" / "research.html"


def slugify(text: str) -> str:
    text = re.sub(r"[^a-z0-9]+", "-", text.lower())
    return text.strip("-")


def main() -> None:
    raw = SOURCE.read_text(encoding="utf-8")

    # Split off the H1 title and the italic intro line; they become the hero.
    lines = raw.splitlines()
    assert lines[0].startswith("# "), "expected H1 on the first line"
    title = lines[0][2:].strip()
    body_start = 1
    intro = ""
    for i in range(1, len(lines)):
        stripped = lines[i].strip()
        if not stripped:
            continue
        if stripped.startswith("*") and stripped.endswith("*"):
            intro = stripped.strip("*")
            body_start = i + 1
        else:
            body_start = i
        break

    body_md = "\n".join(lines[body_start:])
    html = markdown.markdown(body_md, extensions=["tables"])

    # Wrap every table in a scroll container (site convention: .table-wrap).
    html = html.replace(
        "<table>", '<div class="table-wrap" role="region" tabindex="0"><table>'
    ).replace("</table>", "</table></div>")

    # Region headings get stable ids; other h2/h3 headings get slug ids.
    def add_heading_id(match):
        tag, text = match.group(1), match.group(2)
        plain = re.sub(r"<[^>]+>", "", text)
        region = re.match(r"Region\s+(\d+)", plain)
        hid = f"region-{region.group(1)}" if region else slugify(plain)
        return f'<{tag} id="{hid}">{text}</{tag}>'

    html = re.sub(r"<(h[23])>(.*?)</\1>", add_heading_id, html, flags=re.S)

    # External links open in a new tab.
    html = html.replace('<a href="http', '<a target="_blank" rel="noreferrer" href="http')

    page = f"""<!doctype html>
<html lang="en" data-theme="light">
<head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1"><title>Research - Gaman</title><meta name="description" content="A source-cited, evidence-graded literature review of running-related pain and soreness by body region, with treatments, red flags, and limitations."><link rel="stylesheet" href="{{{{ url_for('static', filename='style.css', v=ASSET_VERSION) }}}}"></head>
<body class="method-body research-body">
  <a class="skip-link" href="#research-content">Skip to content</a>
  <header class="method-header"><a class="landing-wordmark" href="{{{{ url_for('index') }}}}">Gaman</a><a href="{{{{ url_for('index') }}}}">Back to Gaman</a></header>
  <main class="method-page research-page" id="research-content">
    <header class="method-hero"><p class="section-kicker">Research library</p><h1>{title}</h1><p>{intro}</p></header>
    <article class="research-content">
{html}
    </article>
  </main>
  <footer class="landing-footer"><a href="https://github.com/Davii3177/Strava-Coros-Data-reading" target="_blank" rel="noreferrer">GitHub</a><a href="mailto:davidch3@andrew.cmu.edu">davidch3@andrew.cmu.edu</a><a href="{{{{ url_for('how_it_works_page') }}}}">How it works</a></footer>
</body>
</html>
"""
    TARGET.write_text(page, encoding="utf-8", newline="\n")
    print(f"wrote {TARGET} ({len(page)} chars)")


if __name__ == "__main__":
    main()
