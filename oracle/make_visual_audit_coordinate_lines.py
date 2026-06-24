"""Visual audit + premium colour gallery for gen.geometry.coordinate-lines (v1.0.2).

CSS-isolation correct: render modes are PER-ROOT CSS CUSTOM PROPERTIES on each figure's own
`<svg class="cx-figure" style="--cx-line:…">`, read by ONE immutable common ruleset in the
document head. The canonical monochrome SVG keeps its own internal <style> and is shown as
the authoritative print figure; presentation copies strip that <style> so the geometry classes
resolve via the per-root variables. Several modes on one page, reordered cards, multiple
questions, and SVGs from other families therefore never interfere (the v1.0.1 global-selector
leakage is structurally impossible). The high-resolution export MATERIALIZES the selected
mode's concrete colours inside the cloned SVG before rasterising — it depends on no external
CSS. The page also exposes `window.__cx` (computed-style isolation results, reversed-order
check, and 6000x4200 export rasterisers with pixel sampling) for the blocking browser tests.

Run:  python oracle/make_visual_audit_coordinate_lines.py
"""

from __future__ import annotations

import json
import os
import re
import sys
from fractions import Fraction

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, HERE)

from spi_oracle import coordinate_lines as cl  # noqa: E402
from build_meta import build_commit, build_timestamp  # noqa: E402

REVIEW_DIR = os.path.join(ROOT, "docs", "review")
OUT = os.path.join(REVIEW_DIR, "coordinate_lines_visual_audit.html")
HIRES = os.path.join(REVIEW_DIR, "coordinate_lines_8k_sample.svg")
THEME = json.load(open(os.path.join(ROOT, "core", "visual-style", "cartesian-theme.json"), encoding="utf-8"))
MODES = ["print", "premium", "premium-dark", "accessible"]
MODE_LABEL = {"print": "Print (monochrome, authoritative)", "premium": "Premium colour (light)",
              "premium-dark": "Premium colour (dark)", "accessible": "Accessible colour (CVD-safe)"}
PALETTE = {"premium": ["#2563eb", "#dc2626", "#059669", "#d97706", "#7c3aed", "#0891b2"],
           "accessible": ["#0072b2", "#d55e00", "#009e73", "#cc79a7", "#56b4e9", "#e69f00"]}
DASHES = ["none", "8 5", "2 4", "10 4 2 4", "6 3", "1 5"]
_STYLE_RE = re.compile(r"<style>.*?</style>", re.S)


def _mode_var_style(mode: str) -> str:
    return ";".join(f"{k}:{v}" for k, v in THEME["modes"][mode].items())


def _resolve_css(mode: str) -> str:
    return re.sub(r"var\((--cx-[a-z-]+)\)", lambda m: THEME["modes"][mode][m.group(1)], THEME["commonCss"])


def presentation_svg(svg: str, mode: str) -> str:
    body = _STYLE_RE.sub("", svg, count=1)
    return body.replace("<svg ", f'<svg class="cx-figure" style="{_mode_var_style(mode)}" ', 1)


def _bg(mode: str) -> str:
    return THEME["modes"][mode]["--cx-bg"]


def _stress_svg(mode: str) -> str:
    """Six-line + four-point stress test as a cx-figure. The frame (axes/grid/ticks) themes via
    the per-root variables; the six series carry their own INLINE element styles (colour + dash
    + marker), which never participate in any document cascade."""
    lines = [(Fraction(1, 1), Fraction(0)), (Fraction(-1, 2), Fraction(3)), (Fraction(2, 1), Fraction(-4)),
             (Fraction(1, 3), Fraction(2)), (Fraction(-2, 1), Fraction(5)), (Fraction(3, 2), Fraction(-1))]
    pts = [(-5, -5), (4, 6), (-3, 4), (6, -3)]
    lay = cl._viewport([(-7, -7), (7, 7)])
    pal = PALETTE.get(mode, ["#111"] * 6)
    out = [f'<svg class="cx-figure" style="{_mode_var_style(mode)}" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {cl.VIEW_W} {cl.VIEW_H}" role="img" aria-label="Stress test: six straight lines and four points on one grid.">']
    frame = cl._figure("plot_point", {"task": "plot_point", "x": 0, "y": 0, "scaffold": False}, lay, False)
    out.append("\n".join(_STYLE_RE.sub("", frame).split("\n")[4:-1]))  # frame geometry only (no <style>)
    for i, (m, c) in enumerate(lines):
        seg = cl._clip_line(m, c, lay)
        if not seg:
            continue
        col = "#111" if mode == "print" else pal[i % len(pal)]
        dash = DASHES[i % len(DASHES)] if mode != "premium" else "none"
        da = f";stroke-dasharray:{dash}" if dash != "none" else ""
        p1 = (cl.proj_x(lay, seg[0][0]), cl.proj_y(lay, seg[0][1]))
        p2 = (cl.proj_x(lay, seg[1][0]), cl.proj_y(lay, seg[1][1]))
        out.append(f'<line x1="{p1[0]}" y1="{p1[1]}" x2="{p2[0]}" y2="{p2[1]}" style="stroke:{col};stroke-width:3;fill:none{da}"/>')
        out.append(f'<text x="{p2[0]+6}" y="{p2[1]}" style="font-size:20px;fill:{col}">L{i+1}</text>')
    for j, (x, y) in enumerate(pts):
        col = "#111" if mode == "print" else pal[(j + 2) % len(pal)]
        px, py = cl.proj_x(lay, Fraction(x)), cl.proj_y(lay, Fraction(y))
        out.append(f'<circle cx="{px}" cy="{py}" r="9" style="fill:{_bg(mode)};stroke:{col};stroke-width:4"/><circle cx="{px}" cy="{py}" r="5" style="fill:{col}"/>')
    out.append('<g transform="translate(40,40)">')
    for i in range(len(lines)):
        col = "#111" if mode == "print" else pal[i % len(pal)]
        dash = DASHES[i % len(DASHES)] if mode != "premium" else "none"
        da = f";stroke-dasharray:{dash}" if dash != "none" else ""
        out.append(f'<line x1="0" y1="{i*24}" x2="34" y2="{i*24}" style="stroke:{col};stroke-width:3{da}"/><text x="42" y="{i*24+6}" style="font-size:18px;fill:var(--cx-text)">line L{i+1}</text>')
    out.append("</g></svg>")
    return "\n".join(out)


def _card(mode: str, svg: str, dark: bool, with_table: bool = True) -> str:
    bg = f' style="background:{_bg(mode)}"' if dark else ""
    table = f'<table class="cs" data-mode="{mode}"><thead><tr><th>element</th><th>computed</th></tr></thead><tbody></tbody></table>' if with_table else ""
    return (f'<section class="card" data-mode="{mode}"><h3>{MODE_LABEL[mode]}</h3>'
            f'<div class="fig"{bg}>{svg}</div>{table}</section>')


def build() -> None:
    commit, ts = build_commit(), build_timestamp()
    # representative canonical figures per task (authoritative monochrome).
    samples = {"read_point": (13, "free-response"), "plot_point": (7, "free-response"),
               "gradient_two_points": (3, "multiple-choice"), "midpoint": (9, "multiple-choice"),
               "equation_from_graph": (11, "multiple-choice"), "equation_from_two_points": (2, "multiple-choice")}
    per_task = []
    for task, (seed, inter) in samples.items():
        it = cl.generate(seed, {"task": task, "interactionType": inter})
        svg = presentation_svg(it["media"][0]["svg"], "print")
        per_task.append(f'<section class="card"><h3>{task} — seed {seed}</h3><div class="sub">answer <code>{it["answer"]["display"]}</code> · band {it["difficulty"]["overallBand"]}</div><div class="fig">{svg}</div></section>')

    gallery_item = cl.generate(2, {"task": "equation_from_two_points", "interactionType": "free-response"})
    canonical = gallery_item["media"][0]["svg"]
    # The hidden export SOURCE carries NO active <style> (export re-materialises concrete colours),
    # so the document contains exactly ONE cx- ruleset (the common one) — zero global leakage,
    # not even specificity-dependent. It carries no cx-figure class either; the export adds it
    # once (a duplicate class attribute would break strict SVG-in-<img> rasterisation).
    canonical_src = _STYLE_RE.sub("", canonical, count=1)
    gallery = "".join(_card(m, presentation_svg(canonical, m), m == "premium-dark") for m in MODES)
    gallery_rev = "".join(_card(m, presentation_svg(canonical, m), m == "premium-dark", with_table=False) for m in reversed(MODES))
    stress = "".join(_card(m, _stress_svg(m), m == "premium-dark", with_table=False) for m in ["premium", "accessible", "print"])
    zoom = f'<section class="card"><h3>Zoom (vector sharpness)</h3><div class="sub">premium presentation scaled 2.4x — strokes/points/labels stay sharp</div><div class="zoom">{presentation_svg(canonical, "premium")}</div></section>'

    with open(HIRES, "w", encoding="utf-8") as fh:
        fh.write(canonical.replace("<svg ", '<svg width="6000" height="4200" ', 1))

    resolved = {m: _resolve_css(m) for m in MODES}
    bgs = {m: _bg(m) for m in MODES}
    png = cl.png_export_transform()
    theme_js = json.dumps({"resolved": resolved, "bg": bgs, "vars": THEME["modes"]})

    html = _PAGE.format(
        version=cl.GENERATOR_VERSION, common=THEME["commonCss"], per_task="".join(per_task),
        gallery=gallery, gallery_rev=gallery_rev, stress=stress, zoom=zoom, canonical=canonical_src,
        theme_js=theme_js, w=png["width"], h=png["height"], gid=cl.GENERATOR_ID, commit=commit, ts=ts)
    with open(OUT, "w", encoding="utf-8") as fh:
        fh.write(html)
    print(f"Wrote {OUT}: {len(samples)} task cards + 4-mode gallery (per-root CSS-var isolation) + reversed-order test "
          f"+ stress test + zoom + {png['width']}x{png['height']} materialized export (v{cl.GENERATOR_VERSION}, commit {commit[:10]}).")


_PAGE = """<!doctype html><html lang="en"><head><meta charset="utf-8">
<title>Coordinate-lines visual audit v{version}</title>
<style id="cx-common">{common}</style>
<style>
 body{{font-family:system-ui,sans-serif;margin:0;background:#fafafa;color:#111}}
 header{{padding:16px 24px;background:#0f172a;color:#fff}} h1{{font-size:19px;margin:0}}
 h2{{margin:26px 24px 6px;font-size:17px}}
 .grid{{display:grid;grid-template-columns:repeat(auto-fill,minmax(380px,1fr));gap:14px;padding:0 24px}}
 .card{{background:#fff;border:1px solid #e5e7eb;border-radius:10px;padding:12px}}
 .card h3{{margin:0 0 4px;font-size:14px}} .sub{{font-size:12px;color:#475569;margin-bottom:6px}}
 .fig{{border:1px solid #f1f5f9;border-radius:6px}} .fig svg{{width:100%;height:auto;display:block}}
 .zoom{{overflow:auto;max-height:520px}} .zoom svg{{width:240%;height:auto}}
 table.cs{{width:100%;font-size:11px;border-collapse:collapse;margin-top:8px}}
 table.cs th,table.cs td{{border:1px solid #eee;padding:2px 5px;text-align:left}} table.cs td.sw{{font-family:monospace}}
 code{{background:#f1f5f9;padding:1px 4px;border-radius:4px}}
 button{{margin:8px 24px 0;padding:8px 14px;border-radius:8px;border:1px solid #cbd5e1;background:#fff;cursor:pointer}}
 #status{{margin:8px 24px;font-size:13px}} footer{{margin:30px;font-size:12px;color:#475569}}
 #hidden{{position:absolute;left:-99999px;top:0}}
</style></head><body>
<header><h1>Coordinate geometry &amp; straight-line graphs — visual audit &amp; premium gallery (v{version})</h1>
<div style="font-size:12px;opacity:.85">Per-root CSS custom properties + one common ruleset → each figure is style-isolated. The monochrome canonical SVG is authoritative; colour is a presentation skin and never carries meaning alone.</div></header>

<h2>1. Per-task canonical figures (monochrome, to scale, answer-free)</h2>
<div class="grid">{per_task}</div>

<h2>2. Premium gallery — four coordinated modes on one page (computed styles below each card)</h2>
<div class="grid" id="gallery">{gallery}</div>

<h2>3. Reversed card order (same figures) — proves order does not change styles</h2>
<div class="grid" id="galleryRev">{gallery_rev}</div>

<h2>4. Many-line / many-point stress test (legend; colour + dash + marker)</h2>
<div class="grid">{stress}</div>

<h2>5. Vector zoom + high-resolution materialized colour export</h2>
<div class="grid">{zoom}
<section class="card"><h3>High-resolution raster export ({w}×{h})</h3>
<div class="sub">The selected mode's concrete palette is materialised INSIDE the cloned SVG before rasterising — no external CSS. The mathematical SVG (<code>coordinate_lines_8k_sample.svg</code>) is the authoritative 8K-like deliverable.</div>
<button onclick="dl('premium')">Download premium {w}×{h} PNG</button>
<button onclick="dl('accessible')">Download accessible {w}×{h} PNG</button>
<button onclick="dl('print')">Download monochrome {w}×{h} PNG</button></section></div>

<div id="status"></div>
<div id="hidden"><div id="canonical-src">{canonical}</div></div>

<footer id="audit-meta" data-generator-id="{gid}" data-generator-version="{version}" data-git-commit="{commit}" data-generated="{ts}">
Build: {gid} v{version} · commit {commit} · {ts}. Reviewed by the curriculum authority before any production exposure.</footer>

<script>
const THEME = {theme_js};
const EXPORT_W = {w}, EXPORT_H = {h};
const CANON = document.querySelector('#canonical-src svg');

// Materialise a self-contained export SVG: strip canonical <style>, add cx-figure + a baked
// concrete ruleset for the mode (no var(), no external CSS), and explicit pixel dimensions.
function exportSvgString(mode, w, h) {{
  let s = new XMLSerializer().serializeToString(CANON);
  s = s.replace(/<style>[\\s\\S]*?<\\/style>/, '');
  s = s.replace('<svg ', '<svg class="cx-figure" width="'+w+'" height="'+h+'" ');
  s = s.replace(/(<svg[^>]*>)/, '$1<style>'+THEME.resolved[mode]+'</style>');
  return s;
}}
function rasterise(mode) {{
  return new Promise((resolve) => {{
    const s = exportSvgString(mode, EXPORT_W, EXPORT_H);
    const img = new Image();
    img.onload = function() {{
      const cv = document.createElement('canvas'); cv.width = EXPORT_W; cv.height = EXPORT_H;
      const cx = cv.getContext('2d'); cx.fillStyle = THEME.bg[mode]; cx.fillRect(0,0,cv.width,cv.height);
      cx.drawImage(img, 0, 0, EXPORT_W, EXPORT_H);
      resolve({{cv, cx}});
    }};
    img.src = 'data:image/svg+xml;base64,' + btoa(unescape(encodeURIComponent(s)));
  }});
}}
async function dl(mode) {{
  const {{cv}} = await rasterise(mode);
  const a = document.createElement('a'); a.download = 'coordinate_lines_'+mode+'_'+EXPORT_W+'x'+EXPORT_H+'.png';
  a.href = cv.toDataURL('image/png'); a.click();
}}
// Exposed for the headless browser tests.
window.__cx = {{
  exportDataURL: async (mode) => (await rasterise(mode)).cv.toDataURL('image/png'),
  // Small raster (colours are size-independent) + the canonical 6000x4200 export dimensions.
  sample: (mode) => new Promise((res, rej) => {{
    const ww = 900, hh = 630; const s = exportSvgString(mode, ww, hh); const img = new Image();
    img.onload = () => {{ const cv = document.createElement('canvas'); cv.width = ww; cv.height = hh;
      const cx = cv.getContext('2d'); cx.fillStyle = THEME.bg[mode]; cx.fillRect(0,0,ww,hh); cx.drawImage(img,0,0,ww,hh);
      const d = cx.getImageData(0,0,ww,hh).data; const seen = new Set();
      for (let i=0;i<d.length;i+=4) {{ if (d[i+3] > 200) seen.add(d[i]+','+d[i+1]+','+d[i+2]); }}
      const big = exportSvgString(mode, EXPORT_W, EXPORT_H).match(/width=\"(\\d+)\" height=\"(\\d+)\"/);
      res({{ exportWidth: +big[1], exportHeight: +big[2], colours: [...seen],
             selfContained: !/<link|@import|url\\(/.test(exportSvgString(mode, EXPORT_W, EXPORT_H)) }}); }};
    img.onerror = rej; img.src = 'data:image/svg+xml;base64,' + btoa(unescape(encodeURIComponent(s)));
  }}),
  // Kick off the three full 6000x4200 rasters in the page (persist across evals for chunked capture).
  startFull: () => {{ window.__png = {{}}; ['premium','accessible','print'].forEach((m) => rasterise(m).then(({{cv}}) => {{ window.__png[m] = cv.toDataURL('image/png'); }})); return 'started'; }},
  exportInfo: async (mode) => {{
    const {{cv, cx}} = await rasterise(mode);
    // sample a band of pixels and return the set of opaque colours seen (excludes pure bg)
    const seen = {{}};
    const d = cx.getImageData(0,0,cv.width, Math.min(cv.height, 4200)).data;
    for (let i=0;i<d.length;i+=4*997) {{ const k = d[i]+','+d[i+1]+','+d[i+2]; seen[k]=(seen[k]||0)+1; }}
    return {{ width: cv.width, height: cv.height, colours: Object.keys(seen) }};
  }},
  computed: () => {{
    const out = {{}};
    for (const card of document.querySelectorAll('#gallery .card, #galleryRev .card')) {{
      const mode = card.dataset.mode, where = card.parentElement.id;
      const g = (sel) => {{ const e = card.querySelector('svg '+sel); return e ? getComputedStyle(e) : null; }};
      const line = g('.cx-line'), axis = g('.cx-axis'), gmaj = g('.cx-grid-major'), gmin = g('.cx-grid-minor');
      const core = g('.cx-pt-core'), outl = g('.cx-pt-outline'), tick = g('.cx-ticklbl'), lbl = g('.cx-lbl'), txt = g('text');
      (out[where] = out[where] || {{}})[mode] = {{
        line: line && line.stroke, axis: axis && axis.stroke, gridMajor: gmaj && gmaj.stroke,
        gridMinor: gmin && gmin.stroke, ptCore: core && core.fill, ptOutline: outl && outl.stroke,
        tick: tick && tick.fill, label: lbl && lbl.fill, text: txt && txt.fill,
      }};
    }}
    return out;
  }},
}};
// Fill the computed-style tables beneath each gallery card.
addEventListener('load', () => {{
  for (const card of document.querySelectorAll('#gallery .card')) {{
    const tb = card.querySelector('table.cs tbody'); if (!tb) continue;
    const rows = [['line','.cx-line','stroke'],['axis','.cx-axis','stroke'],['major grid','.cx-grid-major','stroke'],
      ['minor grid','.cx-grid-minor','stroke'],['point core','.cx-pt-core','fill'],['point outline','.cx-pt-outline','stroke'],
      ['tick label','.cx-ticklbl','fill'],['axis/point label','.cx-lbl','fill']];
    for (const [name,sel,prop] of rows) {{ const e=card.querySelector('svg '+sel);
      const v = e ? getComputedStyle(e)[prop] : '—'; tb.insertAdjacentHTML('beforeend','<tr><td>'+name+'</td><td class="sw">'+v+'</td></tr>'); }}
  }}
  document.getElementById('status').textContent = 'Computed-style tables rendered. window.__cx ready for headless tests.';
}});
</script>
</body></html>"""


if __name__ == "__main__":
    build()
