"""gen.geometry.transformations visual audit page (self-contained HTML).

Renders representative items in BOTH channels (student vs answer-key) across the four approved visual
modes (premium-light / premium-dark / accessible-colour / monochrome-print), plus label-collision
stress samples. The version is fully dynamic (from GENERATOR_VERSION) and the page carries artifact-
identity metadata: data-generator-id / data-generator-version / data-validator-version / data-git-commit
on the root and a window.__trans hook. Source = filled circle + solid edge; image = open square +
dashed edge (distinct WITHOUT colour, owner M).

  python oracle/make_visual_audit_transformations.py

Writes docs/review/transformations_visual_audit.html.
"""

from __future__ import annotations

import html
import os
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
REVIEW_DIR = os.path.join(ROOT, "docs", "review")
sys.path.insert(0, os.path.join(HERE, "spi_oracle"))
sys.path.insert(0, HERE)

from spi_oracle import transformations as T  # noqa: E402

GEN_VER = T.GENERATOR_VERSION
VAL_VER = T.VALIDATOR_VERSION


def _commit():
    try:
        return os.environ.get("SPI_BUILD_COMMIT") or subprocess.check_output(
            ["git", "-C", ROOT, "rev-parse", "HEAD"], text=True).strip()
    except Exception:
        return ""


MODES = [
    ("premium-light", "Premium light", "#ffffff", "#111111"),
    ("premium-dark", "Premium dark", "#0f1420", "#f3f5f9"),
    ("accessible", "Accessible colour", "#fbf9f4", "#1a1a1a"),
    ("print", "Monochrome print", "#ffffff", "#000000"),
]


def _panel(label, svg):
    return f'<figure class="panel"><figcaption>{html.escape(label)}</figcaption>{svg}</figure>'


def main() -> int:
    commit = _commit()
    blocks = []
    for task in T.TASKS:
        item = T.generate(7, {"task": task})
        m = item["media"][0]
        prompt = item["prompt"]["blocks"][0]["text"]
        blocks.append(
            f'<section class="item"><h3>{html.escape(task)} '
            f'<small>band {item["difficulty"]["overallBand"]} · {item["answer"]["type"]}</small></h3>'
            f'<p class="prompt">{html.escape(prompt)}</p>'
            f'<div class="channels">{_panel("Student", m["svg"])}{_panel("Answer key", m["spec"]["answerKeySvg"])}</div>'
            f'</section>')

    # Label-collision stress: clustered points that force the bbox-clearance engine to relocate labels.
    stress = []
    for seed in (3, 17, 29):
        it = T.generate(seed, {"task": "describe_quadrilateral" if False else "describe_rotation"})
        stress.append(_panel(f"describe_rotation seed {seed}", it["media"][0]["svg"]))

    mode_css = "\n".join(
        f'.mode-{cls} {{ background:{bg}; color:{fg}; }}' for cls, _, bg, fg in MODES)
    mode_buttons = "".join(
        f'<button onclick="setMode(\'{cls}\')">{label}</button>' for cls, label, _, _ in MODES)

    doc = f"""<!doctype html>
<html lang="en" data-generator-id="{T.GENERATOR_ID}" data-generator-version="{GEN_VER}"
      data-validator-version="{VAL_VER}" data-git-commit="{html.escape(commit)}">
<head>
<meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1">
<meta name="generator" content="{T.GENERATOR_ID}@{GEN_VER}">
<title>Transformations visual audit · v{GEN_VER}</title>
<style>
  :root {{ font-family: system-ui, sans-serif; }}
  body {{ margin:0; padding:24px; transition:background .2s,color .2s; }}
  header {{ display:flex; gap:12px; align-items:baseline; flex-wrap:wrap; border-bottom:1px solid #8888; padding-bottom:12px; }}
  header h1 {{ margin:0; font-size:20px; }}
  .meta {{ font:12px/1.5 ui-monospace,monospace; opacity:.75; }}
  .controls {{ margin:16px 0; display:flex; gap:8px; flex-wrap:wrap; }}
  button {{ padding:6px 12px; cursor:pointer; }}
  .item {{ margin:28px 0; border-top:1px solid #8884; padding-top:16px; }}
  .item h3 {{ margin:0 0 4px; }} .item h3 small {{ font-weight:400; opacity:.7; }}
  .prompt {{ margin:.2em 0 .8em; }}
  .channels, .stress {{ display:flex; gap:24px; flex-wrap:wrap; }}
  figure.panel {{ margin:0; }} figure.panel svg {{ width:440px; height:auto; border:1px solid #8884; background:#fff; }}
  figcaption {{ font:12px/1.5 ui-monospace,monospace; opacity:.8; margin-bottom:4px; }}
  {mode_css}
</style>
</head>
<body class="mode-premium-light">
<header>
  <h1>gen.geometry.transformations — visual audit</h1>
  <span class="meta">v{GEN_VER} · validator v{VAL_VER} · commit {html.escape(commit[:12])} · PENDING-REVIEW</span>
</header>
<div class="controls"><strong>Mode:</strong> {mode_buttons}</div>
<p>Source = filled circle + solid edge; image = open square + dashed edge — distinct without colour.
Perform items hide the image in the student channel; describe items show both figures. The answer-key
channel shares byte-identical base geometry and adds only the solution overlay.</p>
{''.join(blocks)}
<section class="item"><h3>Label-collision stress</h3>
<div class="stress">{''.join(stress)}</div></section>
<footer class="meta">gen.geometry.transformations v{GEN_VER} · validator v{VAL_VER} · generated for curriculum review (pending-review).</footer>
<script>
  window.__trans = {{ generatorId: "{T.GENERATOR_ID}", version: "{GEN_VER}", validatorVersion: "{VAL_VER}", commit: "{html.escape(commit)}" }};
  function setMode(m) {{ document.body.className = "mode-" + m; }}
</script>
</body>
</html>
"""
    os.makedirs(REVIEW_DIR, exist_ok=True)
    out = os.path.join(REVIEW_DIR, "transformations_visual_audit.html")
    with open(out, "w", encoding="utf-8") as fh:
        fh.write(doc)
    print(f"Visual audit written: {out} (v{GEN_VER}, commit {commit[:12]}).")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
