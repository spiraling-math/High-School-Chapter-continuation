"""gen.geometry.transformations visual audit (self-contained, themed, computed-style ready).

Renders representative items in BOTH channels (student vs answer-key) across the four approved modes
(premium-light / premium-dark / accessible-colour / monochrome-print) using the transformations-theme
presentation layer: the document carries ONE var()-based COMMON_CSS ruleset and every figure stamps its
mode's CSS custom properties on its OWN root (class="tx-figure"), so modes stay isolated per root and the
mode order never changes any card's styles. Each embedded SVG's inline ids are namespaced per card, so
the same item across four modes never collides in the shared DOM (owner #4). The page carries artifact-
identity metadata (data-generator-id/version, data-validator-version, data-git-commit) and a
window.__trans.computed() hook that calls real-browser getComputedStyle on each SVG element class under
each mode (owner #5) — captured via the preview tool into the browser-verification report.

  python oracle/make_visual_audit_transformations.py

Writes docs/review/transformations_visual_audit.html. Version is fully dynamic from GENERATOR_VERSION.
"""

from __future__ import annotations

import html
import json
import os
import re
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
THEME = json.load(open(os.path.join(ROOT, "core", "visual-style", "transformations-theme.json"), encoding="utf-8"))
MODES = ["premium", "premium-dark", "accessible", "print"]
MODE_LABEL = {"premium": "Premium light", "premium-dark": "Premium dark",
              "accessible": "Accessible colour", "print": "Monochrome print"}
_STYLE_RE = re.compile(r"<style>.*?</style>", re.DOTALL)


def _commit():
    try:
        return os.environ.get("SPI_BUILD_COMMIT") or subprocess.check_output(
            ["git", "-C", ROOT, "rev-parse", "HEAD"], text=True).strip()
    except Exception:
        return ""


def _mode_var_style(mode: str) -> str:
    return ";".join(f"{k}:{v}" for k, v in THEME["modes"][mode].items())


def _presentation_svg(svg: str, mode: str, card_uid: str) -> str:
    """Mirror of transformations-theme.presentationSvg: strip canonical <style>, stamp class + mode vars
    on the root, and namespace every inline id (and url(#...) ref) by the card uid."""
    body = _STYLE_RE.sub("", svg)
    body = body.replace("<svg ", f'<svg class="tx-figure" style="{_mode_var_style(mode)}" ', 1)
    body = re.sub(r'id="([^"]+)"', lambda m: f'id="{m.group(1)}--{card_uid}"', body)
    body = re.sub(r"url\(#([^)]+)\)", lambda m: f"url(#{m.group(1)}--{card_uid})", body)
    return body


def main() -> int:
    commit = _commit()
    # one representative item per task (the answer-key SVG covers every element type incl. overlays).
    items = [(task, T.generate(7, {"task": task})) for task in T.TASKS]

    gallery = []
    for mode in MODES:
        cards = []
        for task, it in items:
            m = it["media"][0]
            uid_s = f"{task}-{mode}-s"
            uid_k = f"{task}-{mode}-k"
            stu = _presentation_svg(m["svg"], mode, uid_s)
            key = _presentation_svg(m["spec"]["answerKeySvg"], mode, uid_k)
            cards.append(
                f'<div class="card" data-mode="{mode}" data-task="{task}">'
                f'<div class="cap">{html.escape(task)} · band {it["difficulty"]["overallBand"]}</div>'
                f'<div class="pair"><figure><figcaption>student</figcaption>{stu}</figure>'
                f'<figure><figcaption>answer key</figcaption>{key}</figure></div></div>')
        gallery.append(f'<section class="mode-block" data-mode="{mode}"><h2>{MODE_LABEL[mode]}</h2>'
                       f'<div class="grid">{"".join(cards)}</div></section>')

    # label-collision stress (clustered figures exercise the bbox-clearance engine) in premium-dark.
    stress = []
    for seed in (3, 17, 29):
        it = T.generate(seed, {"task": "describe_rotation"})
        stress.append(f'<figure><figcaption>describe_rotation seed {seed}</figcaption>'
                      f'{_presentation_svg(it["media"][0]["svg"], "premium-dark", f"stress-{seed}")}</figure>')

    common_css = THEME["commonCss"]
    mode_meta = json.dumps(THEME["modes"])

    doc = f"""<!doctype html>
<html lang="en" data-generator-id="{T.GENERATOR_ID}" data-generator-version="{GEN_VER}"
      data-validator-version="{VAL_VER}" data-git-commit="{html.escape(commit)}">
<head>
<meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1">
<meta name="generator" content="{T.GENERATOR_ID}@{GEN_VER}">
<title>{T.GENERATOR_ID} v{GEN_VER} — visual audit</title>
<style>
  :root {{ font-family: system-ui, sans-serif; }}
  body {{ margin:0; padding:24px; background:#f6f7f9; color:#111; }}
  header {{ border-bottom:1px solid #8888; padding-bottom:12px; margin-bottom:8px; }}
  header h1 {{ margin:0; font-size:20px; }}
  .meta {{ font:12px/1.5 ui-monospace,monospace; opacity:.75; }}
  .mode-block {{ margin:22px 0; }}
  .mode-block[data-mode="premium-dark"] {{ background:#0b1220; color:#e5e7eb; padding:12px; border-radius:8px; }}
  .grid, .pair {{ display:flex; gap:18px; flex-wrap:wrap; }}
  .card {{ border:1px solid #8884; border-radius:6px; padding:8px; }}
  .cap, figcaption {{ font:12px/1.4 ui-monospace,monospace; opacity:.8; }}
  figure {{ margin:0; }}
  svg.tx-figure {{ width:300px; height:auto; }}
  /* The ONE document-level common ruleset; each figure root carries its mode's --tx-* vars. */
  {common_css}
</style>
</head>
<body>
<header>
  <h1>{T.GENERATOR_ID} v{GEN_VER} — visual audit</h1>
  <div class="meta">validator v{VAL_VER} · commit {html.escape(commit[:12])} · CURRICULUM-APPROVED (DECISION_LOG #57) · source = filled circle + solid edge; image = open square + dashed edge (distinct without colour)</div>
</header>
<p>Each figure stamps its mode's CSS custom properties on its own <code>class="tx-figure"</code> root; one
shared <code>var()</code> ruleset reads them, so modes are isolated per root and reordering cards cannot
change any card's computed styles. Perform items hide the image in the student channel; describe items
show both figures. The answer-key channel shares byte-identical base geometry and adds only the overlay.</p>
{''.join(gallery)}
<section class="mode-block" data-mode="premium-dark"><h2>Label-collision stress (premium dark)</h2>
<div class="pair">{''.join(stress)}</div></section>
<footer class="meta">gen.geometry.transformations v{GEN_VER} · validator v{VAL_VER} · commit {html.escape(commit[:12])} · curriculum-approved (DECISION_LOG #57).</footer>
<script>
  window.__trans = {{
    generatorId: "{T.GENERATOR_ID}", version: "{GEN_VER}", validatorVersion: "{VAL_VER}", commit: "{html.escape(commit)}",
    modes: {mode_meta},
    // Real-browser computed styles of actual SVG elements, grouped by where (student/key) x mode (owner #5).
    computed: function () {{
      var sel = {{ axis: ".tx-axis", grid: ".tx-grid", srcEdge: ".tx-src-edge", srcCore: ".tx-src-core",
        imgEdge: ".tx-img-edge", imgOpen: ".tx-img-open", mirror: ".tx-mirror", vec: ".tx-vec",
        centre: ".tx-centre", label: ".tx-lbl", ticklbl: ".tx-ticklbl" }};
      var out = {{}};
      document.querySelectorAll('.card').forEach(function (card) {{
        var mode = card.dataset.mode, task = card.dataset.task;
        card.querySelectorAll('figure').forEach(function (fig) {{
          var where = fig.querySelector('figcaption').textContent;  // student / answer key
          var svg = fig.querySelector('svg'); if (!svg) return;
          var row = {{ bg: getComputedStyle(svg).getPropertyValue('--tx-bg').trim() }};
          for (var k in sel) {{ var e = svg.querySelector(sel[k]); if (e) {{
            var cs = getComputedStyle(e);
            row[k] = (sel[k] === '.tx-src-core' || sel[k] === '.tx-img-open' || k === 'label' || k === 'ticklbl') ? cs.fill : cs.stroke;
            if (sel[k] === '.tx-img-edge' || sel[k] === '.tx-mirror') row[k + 'Dash'] = cs.strokeDasharray;
          }} }}
          (out[mode] = out[mode] || {{}})[task + ':' + where] = row;
        }});
      }});
      return out;
    }}
  }};
  document.title = "{T.GENERATOR_ID} v{GEN_VER} — visual audit";
</script>
</body>
</html>
"""
    os.makedirs(REVIEW_DIR, exist_ok=True)
    out = os.path.join(REVIEW_DIR, "transformations_visual_audit.html")
    with open(out, "w", encoding="utf-8") as fh:
        fh.write(doc)
    # duplicate-id self-check across the whole audit DOM (owner #4).
    ids = re.findall(r'id="([^"]+)"', doc)
    dup = len(ids) != len(set(ids))
    print(f"Visual audit written: {out} (v{GEN_VER}, commit {commit[:12]}). duplicate ids in audit: {dup}.")
    return 1 if dup else 0


if __name__ == "__main__":
    raise SystemExit(main())
