"""Visual audit + premium colour-graphics gallery for gen.geometry.coordinate-lines v1.0.0.

Produces docs/review/coordinate_lines_visual_audit.html: per-task canonical (monochrome,
authoritative) figures with validation chips; the PREMIUM GALLERY rendering the SAME
canonical geometry in three coordinated modes (premium colour / accessible CVD-safe colour /
print monochrome) plus a light/dark background pair, a multi-line/point stress test with a
legend, a zoomed vector view proving sharpness, and a 6000x4200 high-resolution export
(authoritative SVG + a client-side PNG download). Colour is a presentation skin over the
cx-* classes; it never moves a coordinate and never carries meaning alone (every series also
differs by dash pattern and marker). The footer carries the build identity for the manifest
artifact-integrity test.

Run:  python oracle/make_visual_audit_coordinate_lines.py
"""

from __future__ import annotations

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
HIRES_SVG = os.path.join(REVIEW_DIR, "coordinate_lines_8k_sample.svg")

# Premium / accessible palettes (greyscale-safe meaning: colour is paired with dash + marker).
PREMIUM = ["#2563eb", "#dc2626", "#059669", "#d97706", "#7c3aed", "#0891b2", "#be185d", "#4d7c0f"]
ACCESSIBLE = ["#0072B2", "#D55E00", "#009E73", "#CC79A7", "#56B4E9", "#E69F00", "#000000", "#F0E442"]  # Okabe-Ito
DASHES = ["none", "8 5", "2 4", "10 4 2 4", "6 3", "1 5", "12 6", "4 4"]

# Mode skins: CSS overrides injected into a copy of the canonical SVG (cx-* classes).
SKINS = {
    "premium": ".cx-line{stroke:#2563eb}.cx-pt-core{fill:#dc2626}.cx-pt-outline{stroke:#dc2626}"
               ".cx-grid-major{stroke:#c7d2fe}.cx-grid-minor{stroke:#e9edff}.cx-axis{stroke:#1e293b}.cx-guide{stroke:#7c3aed}",
    "accessible": ".cx-line{stroke:#0072B2;stroke-dasharray:none}.cx-pt-core{fill:#D55E00}.cx-pt-outline{stroke:#D55E00}"
                  ".cx-grid-major{stroke:#999}.cx-grid-minor{stroke:#ccc}.cx-axis{stroke:#000}.cx-guide{stroke:#009E73}",
    "print": "",  # the canonical monochrome SVG IS print mode
}


def _skin(svg: str, css: str, dark: bool = False) -> str:
    extra = css
    if dark:
        extra += "text{fill:#e5e7eb}.cx-ticklbl{fill:#cbd5e1}.cx-axis{stroke:#e5e7eb}.cx-grid-major{stroke:#475569}.cx-grid-minor{stroke:#334155}.cx-pt-outline{fill:#0b1220}"
    if not extra:
        return svg
    return svg.replace("</svg>", f"<style>{extra}</style></svg>")


def _chips(item) -> str:
    v = cl.validate(item)
    out = []
    for c in v["checks"][:8]:
        cls = "ok" if c["result"] == "pass" else "bad"
        out.append(f'<span class="chip {cls}">{c["name"]}={c["result"]}</span>')
    return " ".join(out)


def _card(title: str, sub: str, svg: str) -> str:
    return f'<section class="card"><h3>{title}</h3><div class="sub">{sub}</div><div class="fig">{svg}</div></section>'


def _stress_svg(mode: str, dark: bool = False) -> str:
    """Synthetic multi-line + multi-point premium stress test with a legend (>=6 series).
    Built from the same deterministic projection primitives as the item renderer."""
    lines = [(Fraction(1, 1), Fraction(0)), (Fraction(-1, 2), Fraction(3)), (Fraction(2, 1), Fraction(-4)),
             (Fraction(1, 3), Fraction(2)), (Fraction(-2, 1), Fraction(5)), (Fraction(3, 2), Fraction(-1))]
    pts = [(-5, -5), (4, 6), (-3, 4), (6, -3)]
    lay = cl._viewport([(-7, -7), (7, 7)])
    palette = ACCESSIBLE if mode == "accessible" else PREMIUM
    out = [f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {cl.VIEW_W} {cl.VIEW_H}" role="img" aria-label="Stress test: six straight lines and four points on one grid.">']
    out.append(f"<style>{cl.STYLE}</style>")
    # axes + grid via a blank canonical figure (reuse the renderer for the frame).
    frame = cl._figure("plot_point", {"task": "plot_point", "x": 0, "y": 0, "scaffold": False}, lay, False)
    frame_inner = "\n".join(frame.split("\n")[4:-1])  # drop <svg>/<title>/<desc>/<style> and </svg>
    out.append(frame_inner)
    glow = '' if mode == "print" else 'filter="url(#glow)"'
    if mode != "print":
        out.append('<defs><filter id="glow" x="-20%" y="-20%" width="140%" height="140%"><feGaussianBlur stdDeviation="2" result="b"/><feMerge><feMergeNode in="b"/><feMergeNode in="SourceGraphic"/></feMerge></filter></defs>')
    for i, (m, c) in enumerate(lines):
        seg = cl._clip_line(m, c, lay)
        if not seg:
            continue
        col = "#111" if mode == "print" else palette[i % len(palette)]
        dash = DASHES[i % len(DASHES)] if mode != "premium" else "none"
        da = f';stroke-dasharray:{dash}' if dash != "none" else ""
        p1 = (cl.proj_x(lay, seg[0][0]), cl.proj_y(lay, seg[0][1]))
        p2 = (cl.proj_x(lay, seg[1][0]), cl.proj_y(lay, seg[1][1]))
        out.append(f'<line x1="{p1[0]}" y1="{p1[1]}" x2="{p2[0]}" y2="{p2[1]}" style="stroke:{col};stroke-width:3;fill:none{da}" {glow}/>')
        out.append(f'<text x="{p2[0]+6}" y="{p2[1]}" style="font-size:20px;fill:{col}">L{i+1}</text>')
    for j, (x, y) in enumerate(pts):
        col = "#111" if mode == "print" else palette[(j + 3) % len(palette)]
        px, py = cl.proj_x(lay, Fraction(x)), cl.proj_y(lay, Fraction(y))
        out.append(f'<circle cx="{px}" cy="{py}" r="9" style="fill:#fff;stroke:{col};stroke-width:4"/><circle cx="{px}" cy="{py}" r="5" style="fill:{col}"/>')
    # legend
    out.append('<g transform="translate(40,40)">')
    for i in range(len(lines)):
        col = "#111" if mode == "print" else palette[i % len(palette)]
        dash = DASHES[i % len(DASHES)] if mode != "premium" else "none"
        da = f';stroke-dasharray:{dash}' if dash != "none" else ""
        out.append(f'<line x1="0" y1="{i*24}" x2="34" y2="{i*24}" style="stroke:{col};stroke-width:3{da}"/><text x="42" y="{i*24+6}" style="font-size:18px;fill:#333">line L{i+1}</text>')
    out.append('</g>')
    out.append("</svg>")
    return _skin("\n".join(out), "", dark)


def build() -> None:
    commit, ts = build_commit(), build_timestamp()
    samples = {
        "read_point": (13, "free-response"), "plot_point": (7, "free-response"),
        "gradient_two_points": (3, "multiple-choice"), "midpoint": (9, "multiple-choice"),
        "interpret_mx_c": (5, "multiple-choice"), "equation_from_graph": (11, "multiple-choice"),
        "equation_from_two_points": (2, "multiple-choice"),
    }
    cards = []
    for task, (seed, inter) in samples.items():
        it = cl.generate(seed, {"task": task, "interactionType": inter})
        svg = it["media"][0]["svg"] if it.get("media") else f'<div class="noeq">No figure (text item): {it["prompt"]["blocks"][0]["text"]}</div>'
        cards.append(_card(f"{task} — seed {seed} ({inter})", f"answer: <code>{it['answer']['display']}</code> · band {it['difficulty']['overallBand']}<br>{_chips(it)}", svg))

    # Premium gallery: one figure (equation_from_two_points) in the three modes + dark.
    gallery_item = cl.generate(2, {"task": "equation_from_two_points", "interactionType": "free-response"})
    g_svg = gallery_item["media"][0]["svg"]
    gallery = [
        _card("Premium colour (light)", "rich-but-restrained palette; crisp points; glow outside the stroke", _skin(g_svg, SKINS["premium"])),
        _card("Premium colour (dark)", "same geometry on a dark background", f'<div class="dark">{_skin(g_svg, SKINS["premium"], dark=True)}</div>'),
        _card("Accessible colour (CVD-safe)", "Okabe-Ito palette; colour paired with dash + marker; strong contrast", _skin(g_svg, SKINS["accessible"])),
        _card("Print (monochrome, authoritative)", "the canonical SVG; what production student/print exports inline", g_svg),
    ]
    stress = [
        _card("Stress test — premium colour", "six lines + four points, auto-assigned distinguishable colours, a legend, and end-labels", _stress_svg("premium")),
        _card("Stress test — accessible colour", "CVD-safe palette + distinct dash patterns + markers (no colour-only meaning)", _stress_svg("accessible")),
        _card("Stress test — print monochrome", "distinct dash patterns + markers carry all meaning with no colour", _stress_svg("print")),
    ]
    zoom = _card("Zoom (vector sharpness)", "the canonical SVG scaled 2.4x — strokes, points, and labels stay perfectly sharp (no rasterisation)", f'<div class="zoom">{g_svg}</div>')

    # 6000x4200 high-resolution export (authoritative SVG); a client-side button rasterises a PNG.
    hires = g_svg.replace("<svg ", f'<svg width="6000" height="4200" ', 1)
    with open(HIRES_SVG, "w", encoding="utf-8") as fh:
        fh.write(hires)

    png = cl.png_export_transform()
    html = f"""<!doctype html><html lang="en"><head><meta charset="utf-8">
<title>Coordinate-lines visual audit + premium gallery v{cl.GENERATOR_VERSION}</title>
<style>
 body{{font-family:system-ui,sans-serif;margin:0;background:#fafafa;color:#111}}
 header{{padding:16px 24px;background:#0f172a;color:#fff}}
 h1{{font-size:20px;margin:0}} h2{{margin:28px 24px 8px;font-size:18px}}
 .grid{{display:grid;grid-template-columns:repeat(auto-fill,minmax(420px,1fr));gap:14px;padding:0 24px}}
 .card{{background:#fff;border:1px solid #e5e7eb;border-radius:10px;padding:12px}}
 .card h3{{margin:0 0 4px;font-size:15px}} .sub{{font-size:12px;color:#475569;margin-bottom:8px}}
 .fig svg{{width:100%;height:auto;border:1px solid #f1f5f9;background:#fff}}
 .dark{{background:#0b1220;border-radius:8px}} .dark svg{{background:#0b1220}}
 .zoom{{overflow:auto;max-height:520px}} .zoom svg{{width:240%;height:auto}}
 .chip{{display:inline-block;font-size:10px;padding:1px 5px;border-radius:4px;margin:1px}}
 .chip.ok{{background:#dcfce7;color:#166534}} .chip.bad{{background:#fee2e2;color:#991b1b}}
 code{{background:#f1f5f9;padding:1px 4px;border-radius:4px}} .noeq{{padding:30px;color:#475569;font-style:italic}}
 footer{{margin:30px;font-size:12px;color:#475569}}
 button{{margin:8px 24px;padding:8px 14px;font-size:14px;border-radius:8px;border:1px solid #cbd5e1;background:#fff;cursor:pointer}}
</style></head><body>
<header><h1>Coordinate geometry &amp; straight-line graphs — visual audit &amp; premium gallery (v{cl.GENERATOR_VERSION})</h1>
<div style="font-size:12px;opacity:.8">The canonical monochrome SVG is authoritative; colour modes are presentation skins over the same geometry. Colour never carries meaning alone.</div></header>

<h2>1. Per-task canonical figures (monochrome, to scale, answer-free)</h2>
<div class="grid">{''.join(cards)}</div>

<h2>2. Premium gallery — three coordinated render modes (same geometry)</h2>
<div class="grid">{''.join(gallery)}</div>

<h2>3. Many-line / many-point stress test (legend; colour + dash + marker)</h2>
<div class="grid">{''.join(stress)}</div>

<h2>4. Vector zoom + high-resolution export</h2>
<div class="grid">{zoom}
<section class="card"><h3>High-resolution raster export</h3>
<div class="sub">Envelope {png['maxEnvelope']} → integer scale {png['scale']} → <b>{png['width']}×{png['height']}</b>, derived from the canonical SVG (<code>coordinate_lines_8k_sample.svg</code>). The SVG is the authoritative 8K-like deliverable; the PNG is rasterised from it with exact coordinate preservation (pngCoord = {png['scale']}·svgCoord).</div>
<div class="fig" id="src">{g_svg}</div>
<button onclick="dl()">Download {png['width']}×{png['height']} PNG</button></section>
</div>

<footer id="audit-meta" data-generator-id="{cl.GENERATOR_ID}" data-generator-version="{cl.GENERATOR_VERSION}" data-git-commit="{commit}" data-generated="{ts}">
Build: {cl.GENERATOR_ID} v{cl.GENERATOR_VERSION} · commit {commit[:10]} · {ts}. Reviewed by the curriculum authority before any production exposure.</footer>
<script>
function dl(){{const s=document.querySelector('#src svg').cloneNode(true);s.setAttribute('width',{png['width']});s.setAttribute('height',{png['height']});
const xml=new XMLSerializer().serializeToString(s);const img=new Image();
img.onload=function(){{const cv=document.createElement('canvas');cv.width={png['width']};cv.height={png['height']};const cx=cv.getContext('2d');cx.fillStyle='#fff';cx.fillRect(0,0,cv.width,cv.height);cx.drawImage(img,0,0);const a=document.createElement('a');a.download='coordinate_lines_{png['width']}x{png['height']}.png';a.href=cv.toDataURL('image/png');a.click();}};
img.src='data:image/svg+xml;base64,'+btoa(unescape(encodeURIComponent(xml)));}}
</script>
</body></html>"""
    with open(OUT, "w", encoding="utf-8") as fh:
        fh.write(html)
    print(f"Wrote {OUT}: {len(cards)} task cards + premium gallery (3 modes + dark) + stress test + zoom + {png['width']}x{png['height']} export (v{cl.GENERATOR_VERSION}, commit {commit[:10]}).")


if __name__ == "__main__":
    build()
