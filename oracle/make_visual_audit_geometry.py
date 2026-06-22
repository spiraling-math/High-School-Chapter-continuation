"""Geometry visual edge-case audit (HUMAN INSPECTION REQUIRED before final approval).

Renders representative angle measures — including the reflex cases that motivated the
v1.1.0 revision — and, for each, shows the FigureModel regions, the intended region
index, the SVG large-arc + sweep flags for that region, the label anchor coordinates,
the rendered inline SVG, and the validation results. Also exercises every task family
(to show interior-arc concavity and the vertically-opposite neutral leader), a
multi-diagram page, and monochrome print output.

Run:  python oracle/make_visual_audit_geometry.py
Writes: docs/review/geometry_visual_audit.html
"""

from __future__ import annotations

import os
import re
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, HERE)

from spi_oracle import geometry as geo  # noqa: E402

OUT = os.path.join(ROOT, "docs", "review", "geometry_visual_audit.html")
ARC_RE = re.compile(r'<path class="ga" d="M (-?\d+) (-?\d+) A (\d+) (\d+) 0 (\d) (\d) (-?\d+) (-?\d+)"/>')
SCAN = 200000


def _find(pred, cfg_task, mode="free-response", limit=SCAN):
    for s in range(1, limit):
        it = geo.generate(s, {"task": cfg_task, "interactionType": mode})
        if pred(it):
            return s, it
    return None, None


def _angles_at_point_with_unknown(measure):
    return _find(lambda it: geo.solve(it["params"]) == measure, "angles_at_point_missing")


def _angles_at_point_with_given(measure):
    return _find(lambda it: measure in geo._ctx(it["params"])["givens"], "angles_at_point_missing")


def _region_card(label, role, measure, seed, it):
    """role: 'unknown' or 'given' — which region has the target measure."""
    p = it["params"]
    fig = geo._build_figure(p)
    P = geo._layout(fig["points"])
    svg = it["media"][0]["svg"]
    arcs = ARC_RE.findall(svg)
    # intended region index = the region whose measure == target
    regions = p.get("regions", [])
    if regions:
        idx = next((j for j, (vn, start, m) in enumerate(fig["arcs"]) if m == measure), 0)
    else:
        idx = 0
    a = arcs[idx] if idx < len(arcs) else ("?",) * 8
    large, sweep = (a[4], a[5]) if len(a) >= 6 else ("?", "?")
    # label anchor for that region (from the adaptive placer)
    placements, leaders = geo._place_labels(P, fig)
    lp = (placements[idx][0], placements[idx][1])
    led = "yes (callout leader)" if leaders[idx] is not None else "no (inside sector)"
    v = geo.validate(it)
    checks = {c["name"]: c["result"] for c in v["checks"]}
    key = ("svg-realises-data", "arc-large-flag-correct", "arc-sweep-correct",
           "labels-within-canvas", "label-ray-clearance", "label-label-clearance",
           "small-sector-label-unambiguous", "reflex-region-rendered-correctly")
    chips = " ".join(f'<span class="chk {checks.get(k,"na")}">{k}={checks.get(k,"n/a")}</span>' for k in key)
    reflex = " REFLEX" if measure > 180 else (" straight" if measure == 180 else "")
    return f"""
<section class="card">
  <h3>{label}: {measure}&deg;{reflex} <small>({role}; seed {seed}; task angles_at_point)</small></h3>
  <ul class="meta">
    <li><b>FigureModel regions:</b> {regions} &nbsp; <b>unknownIndex:</b> {p.get('unknownIndex')}</li>
    <li><b>Intended region index:</b> {idx} &nbsp; <b>measure:</b> {measure}&deg;</li>
    <li><b>SVG arc flags for that region:</b> large-arc=<b>{large}</b>, sweep=<b>{sweep}</b>
        (policy: large-arc=1 iff measure&gt;180; sweep=0 always)</li>
    <li><b>Label anchor (laid-out px):</b> ({lp[0]}, {lp[1]}), text-anchor=middle &nbsp; <b>leader:</b> {led}</li>
    <li><b>Validation:</b> <b class="{v['status']}">{v['status']}</b></li>
  </ul>
  <div class="checks">{chips}</div>
  <div class="fig">{svg}</div>
</section>"""


def _task_card(label, task, mode="free-response"):
    s, it = _find(lambda x: True, task, mode)
    p = it["params"]
    v = geo.validate(it)
    svg = it["media"][0]["svg"]
    extra = ""
    if task == "vertically_opposite_angle":
        extra = (f' &nbsp; <b>arcs:</b> {svg.count(chr(60)+"path class="+chr(34)+"ga")}'
                 f' &nbsp; <b>ticks:</b> {svg.count("gt"+chr(34))}'
                 f' &nbsp; <b>neutral leaders:</b> {svg.count("gx"+chr(34))}')
    return f"""
<section class="card">
  <h3>{label} <small>(seed {s}; {mode})</small></h3>
  <ul class="meta">
    <li><b>Params:</b> {p}</li>
    <li><b>Answer:</b> x = {it['answer']['display']} &nbsp; <b>Validation:</b> <b class="{v['status']}">{v['status']}</b>{extra}</li>
    <li><b>Long description:</b> {it['accessibility']['longDescription']}</li>
  </ul>
  <div class="fig">{svg}</div>
</section>"""


def _load_prev():
    """Load the superseded v1.2.0 generator (for before/after) from its git tag."""
    try:
        src = subprocess.check_output(
            ["git", "show", "geometry-v1.2.0-superseded:oracle/spi_oracle/geometry.py"],
            cwd=ROOT, text=True, encoding="utf-8")
    except Exception:
        return None, None
    path = os.path.join(HERE, "spi_oracle", "_geom_prev.py")
    with open(path, "w", encoding="utf-8") as fh:
        fh.write(src)
    import importlib
    import spi_oracle._geom_prev as prev  # noqa
    importlib.reload(prev)
    return prev, path


def _before_after_cards():
    """Render the three owner-named regression seeds with BOTH the v1.2.0 (before) and
    v1.2.1 (after) label engines on the IDENTICAL parameters, side by side."""
    prev, path = _load_prev()
    cards = ['<h2>Before / after — owner-named regression seeds (identical parameters; v1.2.0 vs v1.2.1)</h2>']
    seeds = [(98, "10-degree unknown"), (26, "248 / 52 / 10 / x"), (13322, "327 reflex with 12 and 21 adjacent")]
    for seed, note in seeds:
        after = geo.generate(seed, {"task": "angles_at_point_missing", "interactionType": "free-response"})
        params = after["params"]
        after_svg = after["media"][0]["svg"]
        v = geo.validate(after)
        if prev is not None:
            try:
                pfig = prev._build_figure(params)
                pacc = prev._accessibility(params)
                before_svg = prev.canonical_svg(pfig, pacc["alt"], pacc["title"], pacc["desc"])
            except Exception as exc:  # pragma: no cover
                before_svg = f"<p>could not render v1.2.0: {exc}</p>"
        else:
            before_svg = "<p>v1.2.0 tag unavailable</p>"
        cards.append(f"""
<section class="card wide">
  <h3>seed {seed} &mdash; {note} <small>(regions {params.get('regions')}, unknown {geo.solve(params)})</small></h3>
  <p><b>v1.2.1 validation:</b> <b class="{v['status']}">{v['status']}</b></p>
  <div class="ba">
    <figure><figcaption>Before (v1.2.0)</figcaption>{before_svg}</figure>
    <figure><figcaption>After (v1.2.1)</figcaption>{after_svg}</figure>
  </div>
</section>""")
    if path is not None and os.path.exists(path):
        os.remove(path)
        sys.modules.pop("spi_oracle._geom_prev", None)
    return cards


def build():
    cards = _before_after_cards()
    # Representative measures (owner list) as the UNKNOWN region.
    for measure in (10, 90, 179, 180, 181, 209, 248, 263):
        s, it = _angles_at_point_with_unknown(measure)
        if it:
            cards.append(_region_card(f"Unknown measure", "unknown", measure, s, it))
        else:
            cards.append(f'<section class="card"><h3>Unknown measure {measure}&deg; — not generated in scan</h3></section>')
    # Near-maximum unknown: the largest unknown measure found in a scan window.
    best_s, best_it, best_m = None, None, 0
    for s in range(1, 20000):
        it = geo.generate(s, {"task": "angles_at_point_missing", "interactionType": "free-response"})
        m = geo.solve(it["params"])
        if m > best_m:
            best_s, best_it, best_m = s, it, m
    cards.append(_region_card("Near-maximum unknown", "unknown", best_m, best_s, best_it))
    # Reflex GIVEN angles.
    for measure in (209, 248, 263):
        s, it = _angles_at_point_with_given(measure)
        if it:
            cards.append(_region_card("Given measure", "given", measure, s, it))
    # Every task family (interior-arc concavity + the VO neutral leader).
    cards.append(_task_card("Triangle (interior arcs must be concave toward each vertex)", "triangle_missing_angle", "multiple-choice"))
    cards.append(_task_card("Isosceles (equal-side ticks; base angle x)", "isosceles_base_angle", "multiple-choice"))
    cards.append(_task_card("Straight line", "straight_line_missing_angle", "multiple-choice"))
    cards.append(_task_card("Vertically opposite (neutral leader; no matching arc)", "vertically_opposite_angle", "free-response"))

    html = f"""<!doctype html>
<html lang="en"><head><meta charset="utf-8">
<title>Geometry Visual Edge-Case Audit — gen.geometry.angles-figures v{geo.GENERATOR_VERSION}</title>
<style>
  body {{ font-family: system-ui, sans-serif; color: #111; background: #fff; margin: 24px; }}
  h1 {{ font-size: 20px; }}
  .note {{ background: #f4f4f4; padding: 10px 14px; border-left: 4px solid #444; max-width: 60em; }}
  .grid {{ display: grid; grid-template-columns: repeat(auto-fill, minmax(440px, 1fr)); gap: 18px; margin-top: 18px; }}
  .grid h2 {{ grid-column: 1 / -1; font-size: 17px; margin: 8px 0 0; border-top: 2px solid #ccc; padding-top: 14px; }}
  .card.wide {{ grid-column: 1 / -1; }}
  .ba {{ display: grid; grid-template-columns: 1fr 1fr; gap: 14px; }}
  .ba figure {{ margin: 0; }}
  .ba figcaption {{ font-weight: bold; font-size: 13px; margin-bottom: 4px; }}
  .ba svg {{ width: 100%; height: auto; border: 1px solid #eee; background: #fff; }}
  .card {{ border: 1px solid #bbb; border-radius: 8px; padding: 12px; break-inside: avoid; }}
  .card h3 {{ font-size: 15px; margin: 0 0 8px; }}
  .card small {{ color: #555; font-weight: normal; }}
  .meta {{ list-style: none; padding: 0; margin: 0 0 8px; font-size: 13px; }}
  .meta li {{ margin: 2px 0; }}
  .checks {{ font-size: 11px; margin-bottom: 8px; }}
  .chk {{ display: inline-block; padding: 1px 6px; margin: 1px; border-radius: 4px; border: 1px solid #999; }}
  .chk.pass {{ background: #eef7ee; }} .chk.fail {{ background: #fdecec; border-color: #b00; }}
  .pass {{ color: #060; }} .fail {{ color: #b00; }}
  .fig svg {{ width: 100%; height: auto; border: 1px solid #eee; background: #fff; }}
  @media print {{ body {{ margin: 0; }} .grid {{ grid-template-columns: 1fr 1fr; }} .note {{ border-color: #000; }} }}
</style></head>
<body>
<h1>Geometry Visual Edge-Case Audit &mdash; <code>gen.geometry.angles-figures</code> v{geo.GENERATOR_VERSION}</h1>
<p class="note"><b>Human inspection required.</b> This page is for the curriculum authority to visually confirm that
every angle region &mdash; especially reflex regions above 180&deg; and the vertically-opposite target &mdash; is drawn in
the correct sector before final approval. Each card lists the FigureModel regions, the intended region index, the SVG
large-arc/sweep flags, the label anchor, and the validation results. All figures are <b>NOT TO SCALE</b> and monochrome;
the page prints in black and white. Generated by <code>oracle/make_visual_audit_geometry.py</code>.</p>
<div class="grid">
{''.join(cards)}
</div>
</body></html>"""
    with open(OUT, "w", encoding="utf-8") as fh:
        fh.write(html)
    print(f"Wrote {OUT}: {len(cards)} cards.")


if __name__ == "__main__":
    build()
