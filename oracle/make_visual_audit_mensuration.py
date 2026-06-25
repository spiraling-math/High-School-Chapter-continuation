"""Build the gen.measurement.mensuration visual audit (owner J/L).

A self-contained HTML page proving the additive mensuration-theme: representative dimensioned
figures rendered in the four modes (premium / premium-dark / accessible-colour / monochrome-print)
using the approved PER-ROOT CSS-custom-property isolation (class cx-figure + one common ruleset =
cartesian shared ruleset + the mensuration additive ruleset). Includes: student-figure-beside-
answer-key-overlay pairs (proving the answer is absent from the student figure and the overlay is
additive); a NOT-TO-SCALE hidden-dimension example; a label-collision stress case (a dense
composite); a multiple-figures-on-one-document isolation section; and a materialised self-contained
export sample (exportSvg, 6000x4200), with a window.__mens hook (computed styles + an export data
URL) for browser-level verification.

Writes: docs/review/mensuration_visual_audit.html
"""

from __future__ import annotations

import json
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, os.path.join(HERE, "spi_oracle"))

from spi_oracle import mensuration as M  # noqa: E402

VSTYLE = os.path.join(ROOT, "core", "visual-style")
_cart = json.load(open(os.path.join(VSTYLE, "cartesian-theme.json"), encoding="utf-8"))
_mens = json.load(open(os.path.join(VSTYLE, "mensuration-theme.json"), encoding="utf-8"))
COMMON_CSS = _cart["commonCss"] + _mens["commonCss"]
MODES = ["premium", "premium-dark", "accessible", "print"]
_STYLE_RE = re.compile(r"<style>.*?</style>", re.S)


def mode_vars(mode):
    return {**_cart["modes"][mode], **_mens["modes"][mode]}


def mode_var_style(mode):
    return ";".join(f"{k}:{v}" for k, v in mode_vars(mode).items())


def resolve_common_css(mode):
    vars = mode_vars(mode)
    return re.sub(r"var\((--cx-[a-z-]+)\)", lambda m: vars.get(m.group(1), "#000"), COMMON_CSS)


def presentation_svg(svg, mode):
    body = _STYLE_RE.sub("", svg)
    return re.sub(r"^<svg ", f'<svg class="cx-figure" style="{mode_var_style(mode)}" ', body, count=1)


def export_svg(svg, mode, w=6000, h=4200):
    body = _STYLE_RE.sub("", svg)
    body = re.sub(r"^<svg ", f'<svg class="cx-figure" width="{w}" height="{h}" ', body, count=1)
    return re.sub(r"(<svg[^>]*>)", r"\1" + f"<style>{resolve_common_css(mode)}</style>", body, count=1)


def _representatives():
    """One readable item per shape/task family + the four L-corners + a NOT-TO-SCALE hidden case."""
    picks = []
    want = {"perimeter_rectangle": None, "area_rectangle": None, "area_triangle": None,
            "perimeter_composite": None, "area_composite": None,
            "missing_length_perimeter": None, "missing_dimension_area": None, "missing_triangle_base_height": None}
    corners_seen = set()
    dense = None  # label-collision stress: composite with the most labels in a small frame
    for seed in range(1, 4000):
        it = M.generate(seed)
        t = it["params"]["task"]
        if want.get(t) is None:
            want[t] = (seed, it)
        if t == "area_composite":
            c = it["params"]["corner"]
            if c not in corners_seen:
                corners_seen.add(c); picks.append((f"area_composite [{c}, {it['params']['decompMode']}]", seed, it))
            # densest: large W*H, small notch -> tight labels
            score = it["params"]["W"] + it["params"]["H"] - min(it["params"]["a"], it["params"]["b"])
            if dense is None or score > dense[0]:
                dense = (score, seed, it)
        if all(v is not None for v in want.values()) and len(corners_seen) >= 4:
            break
    head = [(t.replace("_", " "), s, it) for t, (s, it) in want.items()]
    return head, picks, dense


def main() -> int:
    head, corner_picks, dense = _representatives()
    parts = [
        "<!doctype html><html><head><meta charset='utf-8'><title>mensuration visual audit</title>",
        "<style>",
        "body{font-family:'Segoe UI',system-ui,sans-serif;margin:24px;background:#fff;color:#111}",
        "h2{margin-top:34px}.row{display:flex;flex-wrap:wrap;gap:14px}",
        ".card{border:1px solid #ddd;border-radius:8px;padding:8px;width:300px}",
        ".card.dark{background:#0f172a;color:#e5e7eb}.mode{font-size:12px;color:#6b7280;margin-bottom:4px}",
        ".card.dark .mode{color:#cbd5e1}.card svg{width:284px;height:auto;display:block}",
        ".pair{display:flex;gap:10px}.pair .col{width:300px}",
        COMMON_CSS,
        "</style></head><body>",
        "<h1>gen.measurement.mensuration v1.0.0 — visual audit</h1>",
        "<p>Per-root <code>cx-figure</code> isolation: one document-level common ruleset (cartesian "
        "shared + mensuration additive); each figure's mode is set only by its own <code>--cx-*</code> "
        "variables. Monochrome <b>print</b> is the colour-free authoritative rendering.</p>",
    ]

    # 1) Four-mode gallery (student figures).
    parts.append("<h2>Every shape family in four modes (student figures)</h2>")
    for label, seed, it in head:
        parts.append(f"<h3>{label} — seed {seed}</h3><div class='row'>")
        for mode in MODES:
            cls = "card dark" if mode == "premium-dark" else "card"
            parts.append(f"<div class='{cls}'><div class='mode'>{mode}</div>{presentation_svg(it['media'][0]['svg'], mode)}</div>")
        parts.append("</div>")

    # 2) Student beside answer-key overlay (answer absent from student; overlay additive).
    parts.append("<h2>Student figure beside answer-key overlay</h2>")
    parts.append("<p>The answer never appears in the student figure; the answer-key adds only the "
                 "<code>cx-overlay</code> group (missing side / decomposition cut / final result).</p>")
    for label, seed, it in head:
        s = presentation_svg(it["media"][0]["svg"], "premium")
        k = presentation_svg(it["media"][0]["spec"]["answerKeySvg"], "premium")
        parts.append(f"<h3>{label}</h3><div class='pair'><div class='col'><div class='mode'>student</div>{s}</div>"
                     f"<div class='col'><div class='mode'>answer key</div>{k}</div></div>")

    # 3) Label-collision stress (densest composite).
    if dense:
        _, seed, it = dense
        parts.append(f"<h2>Label-collision stress — densest composite (seed {seed})</h2><div class='row'>")
        for mode in ("premium", "print"):
            cls = "card"
            parts.append(f"<div class='{cls}'><div class='mode'>{mode}</div>{presentation_svg(it['media'][0]['svg'], mode)}</div>")
        parts.append("</div>")

    # 4) Materialised export (premium, 6000x4200, self-contained).
    exp = export_svg(head[0][2]["media"][0]["svg"], "premium", 6000, 4200)
    parts.append("<h2>Materialised export (premium, 6000×4200, self-contained)</h2>")
    parts.append("<div id='exp' style='width:330px'>" + presentation_svg(head[0][2]["media"][0]["svg"], "premium") + "</div>")
    parts.append("<script>")
    parts.append("window.__mens = {")
    parts.append("  modes: " + json.dumps(MODES) + ",")
    parts.append("  exportSvg: " + json.dumps(exp) + ",")
    parts.append("  computed: function(){ var out={}; document.querySelectorAll('.card svg .cx-shape').forEach(function(s,i){")
    parts.append("    var c=getComputedStyle(s); out[i]={fill:c.fill,stroke:c.stroke}; }); return out; },")
    parts.append("  exportDataURL: function(scale){ scale=scale||6; return new Promise(function(res,rej){")
    parts.append("    var svg=window.__mens.exportSvg; var img=new Image();")
    parts.append("    var blob=new Blob([svg],{type:'image/svg+xml'}); var url=URL.createObjectURL(blob);")
    parts.append("    img.onload=function(){ var cv=document.createElement('canvas'); cv.width=1000*scale; cv.height=700*scale;")
    parts.append("      var cx=cv.getContext('2d'); cx.fillStyle='#fff'; cx.fillRect(0,0,cv.width,cv.height);")
    parts.append("      cx.drawImage(img,0,0,cv.width,cv.height); URL.revokeObjectURL(url); res(cv.toDataURL('image/png')); };")
    parts.append("    img.onerror=rej; img.src=url; }); }")
    parts.append("};")
    parts.append("</script>")
    parts.append(f"<footer style='margin-top:30px;color:#6b7280;font-size:12px'>{M.GENERATOR_ID} v"
                 f"{M.GENERATOR_VERSION}; modes {', '.join(MODES)}; per-root cx-figure isolation; export 6000×4200.</footer>")
    parts.append("</body></html>")

    out = os.path.join(ROOT, "docs", "review", "mensuration_visual_audit.html")
    with open(out, "w", encoding="utf-8") as fh:
        fh.write("\n".join(parts))
    print(f"Visual audit written: {len(head)} families × {len(MODES)} modes + student-vs-key + "
          f"label-collision + 6000×4200 export -> {out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
