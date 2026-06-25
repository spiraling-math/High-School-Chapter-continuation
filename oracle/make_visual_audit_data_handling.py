"""Build the gen.stats.data-handling visual audit (owner decision K/O).

A self-contained HTML page proving the additive data-chart-theme: every chart figure rendered
in the four modes (premium / premium-dark / accessible-colour / monochrome-print) using the
approved PER-ROOT CSS-custom-property isolation (class cx-figure + one common ruleset = cartesian
shared ruleset + the data-chart additive ruleset). Includes a "multiple figures in one document"
isolation section and a materialised self-contained export sample (exportSvg, 6000x4200), with a
window.__dc hook (computed styles + an export data URL) for browser-level verification.

Writes: docs/review/stats_data_handling_visual_audit.html
"""

from __future__ import annotations

import json
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, os.path.join(HERE, "spi_oracle"))

from spi_oracle import data_handling as dh  # noqa: E402

REVIEW_DIR = os.path.join(ROOT, "docs", "review")
VSTYLE = os.path.join(ROOT, "core", "visual-style")
MODES = ["premium", "premium-dark", "accessible", "print"]

_cart = json.load(open(os.path.join(VSTYLE, "cartesian-theme.json"), encoding="utf-8"))
_dc = json.load(open(os.path.join(VSTYLE, "data-chart-theme.json"), encoding="utf-8"))
COMMON_CSS = _cart["commonCss"] + _dc["commonCss"]
_STYLE_RE = re.compile(r"<style>.*?</style>", re.S)


def mode_vars(mode):
    v = dict(_cart["modes"][mode]); v.update(_dc["modes"][mode]); return v


def mode_var_style(mode):
    return ";".join(f"{k}:{v}" for k, v in mode_vars(mode).items())


def resolve_common_css(mode):
    v = mode_vars(mode)
    return re.sub(r"var\((--cx-[a-z-]+)\)", lambda m: v.get(m.group(1), "#000"), COMMON_CSS)


def presentation_svg(svg, mode):
    body = _STYLE_RE.sub("", svg)
    return re.sub(r"^<svg ", f'<svg class="cx-figure" style="{mode_var_style(mode)}" ', body, count=1)


def export_svg(svg, mode, w=6000, h=4200):
    body = _STYLE_RE.sub("", svg)
    body = re.sub(r"^<svg ", f'<svg class="cx-figure" width="{w}" height="{h}" ', body, count=1)
    return re.sub(r"(<svg[^>]*>)", r"\1" + f"<style>{resolve_common_css(mode)}</style>", body, count=1)


def _chart_items():
    out = {}
    # one bar chart per axis scale {1,2,5,10}, a whole-symbol + half-symbol pictogram, a line graph
    want_scales = {1, 2, 5, 10}
    for seed in range(1, 4000):
        it = dh.generate(seed, {"task": "read_bar_chart", "interactionType": "free-response"})
        ds = it["params"]["dataset"]
        step = dh._axis_step_and_max(max(ds["frequencies"]))[0]
        if step in want_scales and f"bar{step}" not in out:
            out[f"bar{step}"] = it
            want_scales.discard(step)
        if not want_scales:
            break
    for seed in range(1, 4000):
        it = dh.generate(seed, {"task": "read_pictogram", "interactionType": "free-response"})
        ds = it["params"]["dataset"]; key = ds["pictogramKey"]
        anyhalf = any((f % key) == (key // 2) and key % 2 == 0 for f in ds["frequencies"])
        if anyhalf and "pictoHalf" not in out:
            out["pictoHalf"] = it
        if not anyhalf and "pictoWhole" not in out:
            out["pictoWhole"] = it
        if "pictoHalf" in out and "pictoWhole" in out:
            break
    out["line"] = dh.generate(7, {"task": "read_line_graph", "interactionType": "free-response"})
    return out


def main() -> int:
    os.makedirs(REVIEW_DIR, exist_ok=True)
    items = _chart_items()
    parts = [
        "<!doctype html><html lang='en'><head><meta charset='utf-8'>",
        "<title>stats data-handling — visual audit</title>",
        "<style>",
        "body{font-family:sans-serif;margin:24px;background:#f6f7f9;color:#111}",
        "h1,h2{font-weight:650} .grid{display:flex;gap:16px;flex-wrap:wrap}",
        ".card{background:#fff;border:1px solid #e5e7eb;border-radius:10px;padding:10px;width:330px}",
        ".card.dark{background:#0b1220;color:#e5e7eb}",
        ".card svg{width:100%;height:auto;display:block}",
        ".mode{font-size:12px;color:#6b7280;margin-bottom:4px}",
        "table.cx-table,table.cx-list{border-collapse:collapse;margin:6px 0;font-size:14px}",
        "table.cx-table th,table.cx-table td,table.cx-list td{border:1px solid #cbd5e1;padding:4px 10px;text-align:center}",
        ".cx-blank input{width:64px}",
        # The ONE common ruleset (cartesian shared + data-chart additive). Per-root variables do the theming.
        COMMON_CSS,
        "</style></head><body>",
        "<h1>gen.stats.data-handling — visual audit</h1>",
        f"<p>Generator {dh.GENERATOR_VERSION}; validator {dh.VALIDATOR_VERSION}. Four render modes via per-root CSS "
        "custom properties (class <code>cx-figure</code>) + one common ruleset (cartesian shared + data-chart additive). "
        "Colour never carries meaning alone: every category/series is labelled; the monochrome <b>print</b> mode is the "
        "colour-free authoritative rendering.</p>",
    ]

    # Direct-read scale contract (owner v1.0.2): before -> after for charts whose queried value
    # sits on a MINOR subdivision. "Before" strips the minor grid (the v1.0.1 look) so the
    # queried bar/point falls between labelled ticks; "after" renders the minor subdivisions so
    # the value is exactly recoverable from a visible mark.
    import re as _re
    minor_re = _re.compile(r'<line class="cx-(?:grid|tick)-minor"[^>]*/>\n?')
    parts.append("<h2>Direct-read scale contract — before → after (minor subdivisions)</h2>")
    parts.append("<p>Charts whose queried value lands on a minor subdivision. <b>Before</b> (minor "
                 "grid removed) the value falls between labelled ticks; <b>after</b> it sits on a visible mark.</p>")
    shown = 0
    for seed in range(1, 4000):
        if shown >= 3:
            break
        it = dh.generate(seed, {"task": "read_bar_chart", "interactionType": "free-response"})
        ds = it["params"]["dataset"]
        major, minor, _y = dh._chart_scale(ds["frequencies"])
        q = ds["frequencies"][it["params"]["queryIndex"]]
        if not (minor < major and q % major != 0):
            continue
        shown += 1
        after = it["media"][0]["svg"]
        before = minor_re.sub("", after)
        cat = ds["categories"][it["params"]["queryIndex"]]
        parts.append(f"<h3>seed {seed} — queried “{cat}” = {q} (major {major}, minor {minor})</h3><div class='grid'>")
        parts.append(f"<div class='card'><div class='mode'>before (no minor grid — value between ticks)</div>{presentation_svg(before, 'print')}</div>")
        parts.append(f"<div class='card'><div class='mode'>after (minor subdivision resolves {q})</div>{presentation_svg(after, 'print')}</div>")
        parts.append("</div>")

    for key, it in items.items():
        svg = it["media"][0]["svg"]
        parts.append(f"<h2>{key} — {it['params']['task']}</h2><div class='grid'>")
        for mode in MODES:
            cls = "card dark" if mode == "premium-dark" else "card"
            parts.append(f"<div class='{cls}'><div class='mode'>{mode}</div>{presentation_svg(svg, mode)}</div>")
        parts.append("</div>")

    # Isolation section: premium + dark + accessible + print bar charts in ONE container — must not interfere.
    parts.append("<h2>Per-root isolation — four modes of the same figure in one container</h2><div class='grid'>")
    bar = items.get("bar5") or next(iter(items.values()))
    for mode in MODES:
        cls = "card dark" if mode == "premium-dark" else "card"
        parts.append(f"<div class='{cls}'><div class='mode'>{mode}</div>{presentation_svg(bar['media'][0]['svg'], mode)}</div>")
    parts.append("</div>")

    # Tables section (semantic HTML, authoritative).
    parts.append("<h2>Semantic tables (authoritative)</h2>")
    for task in ("read_table_value", "complete_frequency_table", "mean_from_freq_table", "single_event_probability",
                 "mean_from_list"):
        it = dh.generate(7, {"task": task, "interactionType": "free-response"})
        parts.append(f"<h3>{task}</h3>" + it["media"][0]["spec"]["html"])

    # Export sample + browser hook.
    exp = export_svg(bar["media"][0]["svg"], "premium", 6000, 4200)
    parts.append("<h2>Materialised export (premium, 6000×4200, self-contained)</h2>")
    parts.append("<div id='exp' style='width:330px'>" + presentation_svg(bar["media"][0]["svg"], "premium") + "</div>")
    parts.append("<script>")
    parts.append("window.__dc = {")
    parts.append("  modes: " + json.dumps(MODES) + ",")
    parts.append("  exportSvg: " + json.dumps(exp) + ",")
    parts.append("  computed: function(){ var out={}; document.querySelectorAll('.card svg').forEach(function(s,i){")
    parts.append("    var bar=s.querySelector('.cx-bar'); var cs=bar?getComputedStyle(bar):null;")
    parts.append("    out[i]={fill: cs?cs.fill:null, stroke: cs?cs.stroke:null}; }); return out; },")
    parts.append("  exportDataURL: function(scale){ scale=scale||6; return new Promise(function(res,rej){")
    parts.append("    var svg=window.__dc.exportSvg; var img=new Image();")
    parts.append("    var url='data:image/svg+xml;charset=utf-8,'+encodeURIComponent(svg);")
    parts.append("    img.onload=function(){ var c=document.createElement('canvas'); c.width=1000*scale; c.height=700*scale;")
    parts.append("      var ctx=c.getContext('2d'); ctx.fillStyle='#ffffff'; ctx.fillRect(0,0,c.width,c.height);")
    parts.append("      ctx.drawImage(img,0,0,c.width,c.height); res(c.toDataURL('image/png').length); };")
    parts.append("    img.onerror=function(e){ rej(''+e); }; img.src=url; }); }")
    parts.append("};")
    parts.append("</script>")
    parts.append(f"<footer style='margin-top:24px;color:#6b7280;font-size:12px'>Build: {dh.GENERATOR_ID} "
                 f"{dh.GENERATOR_VERSION}; modes {', '.join(MODES)}; per-root cx-figure isolation; export 6000×4200.</footer>")
    parts.append("</body></html>")

    with open(os.path.join(REVIEW_DIR, "stats_data_handling_visual_audit.html"), "w", encoding="utf-8") as fh:
        fh.write("\n".join(parts))
    print(f"Visual audit written: {len(items)} chart figures × {len(MODES)} modes + isolation + tables + export.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
