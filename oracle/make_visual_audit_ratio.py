"""gen.proportion.ratio visual audit (self-contained, themed, computed-style ready).

Mirror of make_visual_audit_transformations. Renders representative figure-bearing items in BOTH channels
(student vs answer-key) across the four approved modes (premium-light / premium-dark / accessible-colour /
monochrome-print) using the ratio-theme presentation layer: the document carries ONE var()-based
COMMON_CSS ruleset and every figure stamps its mode's CSS custom properties on its OWN root
(class="rt-figure"), so modes stay isolated per root and the mode order never changes any card's styles.
Each embedded SVG's inline ids are namespaced per card, so the same item across four modes never collides
in the shared DOM. The page carries artifact-identity metadata (data-generator-id/version,
data-validator-version, data-git-commit) and a window.__ratio.computed() hook that calls real-browser
getComputedStyle on each rt-* element class under each mode — captured via the preview tool into the
browser-verification report.

  PYTHONIOENCODING=utf-8 python oracle/make_visual_audit_ratio.py

Writes docs/review/proportion_ratio_visual_audit.html. Version is fully dynamic from GENERATOR_VERSION.
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

from spi_oracle import ratio as R  # noqa: E402

GEN_VER = R.GENERATOR_VERSION
VAL_VER = R.VALIDATOR_VERSION
THEME = json.load(open(os.path.join(ROOT, "core", "visual-style", "ratio-theme.json"), encoding="utf-8"))
MODES = ["premium", "premium-dark", "accessible", "print"]
MODE_LABEL = {"premium": "Premium light", "premium-dark": "Premium dark",
              "accessible": "Accessible colour", "print": "Monochrome print"}
_STYLE_RE = re.compile(r"<style>.*?</style>", re.DOTALL)

# One representative figure-bearing item per figure family (bar models, double number lines, best-buy
# table). The answer-key SVG covers every element type incl. the solved overlay.
FIGURE_TASKS = [
    ("share_two_part", "Bar model — share two part"),
    ("share_three_part", "Bar model — share three part"),
    ("missing_part", "Bar model — missing part"),
    ("ratio_to_fraction", "Bar model — ratio to fraction"),
    ("fraction_to_ratio", "Bar model — fraction to ratio"),
    ("direct_proportion", "Double number line — direct proportion"),
    ("unit_rate", "Double number line — unit rate"),
    ("simple_scale", "Double number line — simple scale"),
    ("best_buy", "Best-buy comparison table"),
]


def _commit():
    try:
        return os.environ.get("SPI_BUILD_COMMIT") or subprocess.check_output(
            ["git", "-C", ROOT, "rev-parse", "HEAD"], text=True).strip()
    except Exception:
        return ""


def _mode_var_style(mode: str) -> str:
    return ";".join(f"{k}:{v}" for k, v in THEME["modes"][mode].items())


def _presentation_svg(svg: str, mode: str, card_uid: str) -> str:
    """Mirror of ratio-theme.presentationSvg: strip canonical <style>, stamp class="rt-figure" + the mode
    vars on the root, and namespace every inline id (and url(#...) ref) by the card uid."""
    body = _STYLE_RE.sub("", svg)
    body = body.replace("<svg ", f'<svg class="rt-figure" style="{_mode_var_style(mode)}" ', 1)
    body = re.sub(r'id="([^"]+)"', lambda m: f'id="{m.group(1)}--{card_uid}"', body)
    body = re.sub(r"url\(#([^)]+)\)", lambda m: f"url(#{m.group(1)}--{card_uid})", body)
    return body


def main() -> int:
    commit = _commit()
    items = []
    for task, label in FIGURE_TASKS:
        it = R.generate(7, {"task": task})
        if it.get("media"):
            items.append((task, label, it))

    gallery = []
    for mode in MODES:
        cards = []
        for task, label, it in items:
            m = it["media"][0]
            uid_s = f"{task}-{mode}-s"
            uid_k = f"{task}-{mode}-k"
            stu = _presentation_svg(m["svg"], mode, uid_s)
            key = _presentation_svg(m["spec"]["answerKeySvg"], mode, uid_k)
            cards.append(
                f'<div class="card" data-mode="{mode}" data-task="{task}">'
                f'<div class="cap">{html.escape(label)} · band {it["difficulty"]["overallBand"]}</div>'
                f'<div class="pair"><figure><figcaption>student</figcaption>{stu}</figure>'
                f'<figure><figcaption>answer key</figcaption>{key}</figure></div></div>')
        gallery.append(f'<section class="mode-block" data-mode="{mode}"><h2>{MODE_LABEL[mode]}</h2>'
                       f'<div class="grid">{"".join(cards)}</div></section>')

    # label/figure stress sample: clustered share/table figures with longer themed labels (premium-dark).
    stress = []
    for task, seed in (("share_three_part", 3), ("best_buy", 17), ("share_three_part", 29)):
        it = R.generate(seed, {"task": task})
        if not it.get("media"):
            continue
        stress.append(f'<figure><figcaption>{html.escape(task)} seed {seed}</figcaption>'
                      f'{_presentation_svg(it["media"][0]["spec"]["answerKeySvg"], "premium-dark", f"stress-{task}-{seed}")}</figure>')

    common_css = THEME["commonCss"]
    mode_meta = json.dumps(THEME["modes"])

    doc = f"""<!doctype html>
<html lang="en" data-generator-id="{R.GENERATOR_ID}" data-generator-version="{GEN_VER}"
      data-validator-version="{VAL_VER}" data-git-commit="{html.escape(commit)}">
<head>
<meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1">
<meta name="generator" content="{R.GENERATOR_ID}@{GEN_VER}">
<title>{R.GENERATOR_ID} v{GEN_VER} — visual audit</title>
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
  svg.rt-figure {{ width:360px; height:auto; }}
  /* The ONE document-level common ruleset; each figure root carries its mode's --rt-* vars. */
  {common_css}
</style>
</head>
<body>
<header>
  <h1>{R.GENERATOR_ID} v{GEN_VER} — visual audit</h1>
  <div class="meta">validator v{VAL_VER} · commit {html.escape(commit[:12])} · CURRICULUM-APPROVED · given = solid-filled solid edge (or filled point); unknown = hatched/dashed segment + '?' (or open dashed point) — distinct without colour</div>
</header>
<p>Each figure stamps its mode's CSS custom properties on its own <code>class="rt-figure"</code> root; one
shared <code>var()</code> ruleset reads them, so modes are isolated per root and reordering cards cannot
change any card's computed styles. The student channel shows only given quantities and a '?' for the
unknown; the answer-key channel shares byte-identical base geometry and adds only the solved overlay.
Print is the canonical monochrome authoritative look.</p>
{''.join(gallery)}
<section class="mode-block" data-mode="premium-dark"><h2>Label/figure stress (premium dark, answer-key channel)</h2>
<div class="pair">{''.join(stress)}</div></section>
<footer class="meta">{R.GENERATOR_ID} v{GEN_VER} · validator v{VAL_VER} · commit {html.escape(commit[:12])} · curriculum-approved.</footer>
<script>
  window.__ratio = {{
    generatorId: "{R.GENERATOR_ID}", version: "{GEN_VER}", validatorVersion: "{VAL_VER}", commit: "{html.escape(commit)}",
    modes: {mode_meta},
    // Real-browser computed styles of actual rt-* SVG elements, grouped by where (student/key) x mode.
    computed: function () {{
      var sel = {{ barGiven: ".rt-bar-given", barUnknown: ".rt-bar-unknown", barFrame: ".rt-bar-frame",
        axis: ".rt-axis", givenPt: ".rt-given-pt", unknownPt: ".rt-unknown-pt", rung: ".rt-rung",
        tableLine: ".rt-table-line", lbl: ".rt-lbl", ticklbl: ".rt-ticklbl", unknownLbl: ".rt-unknown-lbl" }};
      var out = {{}};
      document.querySelectorAll('.card').forEach(function (card) {{
        var mode = card.dataset.mode, task = card.dataset.task;
        card.querySelectorAll('figure').forEach(function (fig) {{
          var where = fig.querySelector('figcaption').textContent;  // student / answer key
          var svg = fig.querySelector('svg'); if (!svg) return;
          var row = {{ bg: getComputedStyle(svg).getPropertyValue('--rt-bg').trim() }};
          for (var k in sel) {{ var e = svg.querySelector(sel[k]); if (e) {{
            var cs = getComputedStyle(e);
            row[k] = (k === 'lbl' || k === 'ticklbl' || k === 'unknownLbl' || k === 'givenPt'
                      || k === 'barGiven' || k === 'barUnknown' || k === 'unknownPt') ? cs.fill : cs.stroke;
            if (k === 'barUnknown' || k === 'rung' || k === 'unknownPt') row[k + 'Dash'] = cs.strokeDasharray;
          }} }}
          (out[mode] = out[mode] || {{}})[task + ':' + where] = row;
        }});
      }});
      return out;
    }}
  }};
  document.title = "{R.GENERATOR_ID} v{GEN_VER} — visual audit";
</script>
</body>
</html>
"""
    os.makedirs(REVIEW_DIR, exist_ok=True)
    out = os.path.join(REVIEW_DIR, "proportion_ratio_visual_audit.html")
    with open(out, "w", encoding="utf-8") as fh:
        fh.write(doc)
    # duplicate-id self-check across the whole audit DOM.
    ids = re.findall(r'id="([^"]+)"', doc)
    dup = len(ids) != len(set(ids))
    print(f"Visual audit written: {out} (v{GEN_VER}, commit {commit[:12]}). "
          f"inline ids: {len(ids)} ({len(set(ids))} unique). duplicate ids in audit: {dup}.")
    return 1 if dup else 0


if __name__ == "__main__":
    raise SystemExit(main())
