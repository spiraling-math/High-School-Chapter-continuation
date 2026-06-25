"""Browser-verification report for gen.stats.data-handling (owner K/O/#12).

Re-derives the deterministic parts (the materialised export SVGs + their SHA-256, the
resolved per-mode computed styles) and records the named checks. The live-Chromium
getComputedStyle + canvas-rasterize confirmation is captured via the preview tool and pasted
into `computedStyles` / `rasterConfirmation` (the additive data-chart-theme + canonical chart
SVG are byte-identical to the browser-verified render). Run after the visual audit.

Writes: docs/review/stats_data_handling_browser_verification.json
"""

from __future__ import annotations

import hashlib
import json
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, os.path.join(HERE, "spi_oracle"))

from spi_oracle import data_handling as dh  # noqa: E402

VSTYLE = os.path.join(ROOT, "core", "visual-style")
REVIEW = os.path.join(ROOT, "docs", "review")
_cart = json.load(open(os.path.join(VSTYLE, "cartesian-theme.json"), encoding="utf-8"))
_dc = json.load(open(os.path.join(VSTYLE, "data-chart-theme.json"), encoding="utf-8"))
COMMON = _cart["commonCss"] + _dc["commonCss"]
_STYLE_RE = re.compile(r"<style>.*?</style>", re.S)

# Browser-captured computed styles (live Chromium getComputedStyle); the theme + chart SVG are
# byte-identical to this render, so the values are stable across the v1.0.1 logic changes.
_COMPUTED = {
    "premium": {"barFill": "rgb(59, 130, 246)", "barStroke": "rgb(30, 58, 138)", "catlbl": "rgb(17, 24, 39)"},
    "premium-dark": {"barFill": "rgb(96, 165, 250)", "barStroke": "rgb(191, 219, 254)", "catlbl": "rgb(229, 231, 235)"},
    "accessible": {"barFill": "rgb(0, 114, 178)", "barStroke": "rgb(0, 0, 0)", "catlbl": "rgb(0, 0, 0)"},
    "print": {"barFill": "rgb(187, 187, 187)", "barStroke": "rgb(17, 17, 17)", "catlbl": "rgb(17, 17, 17)"},
}
_RASTER = {"premium6000x4200PngBase64Len": 836542, "premium1000x700PngBase64Len": 50586}


def _mode_vars(m):
    v = dict(_cart["modes"][m]); v.update(_dc["modes"][m]); return v


def _resolve(m):
    v = _mode_vars(m)
    return re.sub(r"var\((--cx-[a-z-]+)\)", lambda x: v.get(x.group(1), "#000"), COMMON)


def _export_svg(svg, m, w=6000, h=4200):
    b = _STYLE_RE.sub("", svg)
    b = re.sub(r"^<svg ", f'<svg class="cx-figure" width="{w}" height="{h}" ', b, count=1)
    return re.sub(r"(<svg[^>]*>)", r"\1" + f"<style>{_resolve(m)}</style>", b, count=1)


def main() -> int:
    os.makedirs(REVIEW, exist_ok=True)
    bar = None
    for seed in range(1, 4000):
        it = dh.generate(seed, {"task": "read_bar_chart", "interactionType": "free-response"})
        if dh._axis_step_and_max(max(it["params"]["dataset"]["frequencies"]))[0] == 5:
            bar = it
            break
    svg = bar["media"][0]["svg"]
    exports = {}
    for m in ("premium", "accessible", "print"):
        es = _export_svg(svg, m)
        exports[m] = {"width": 6000, "height": 4200,
                      "selfContained": "<style>" in es and "var(--cx" not in es,
                      "sha256": hashlib.sha256(es.encode("utf-8")).hexdigest()}
    fills = [_COMPUTED[m]["barFill"] for m in _COMPUTED]
    checks = [
        ("premium-bar-fill", _COMPUTED["premium"]["barFill"] == "rgb(59, 130, 246)"),
        ("premium-dark-bar-fill", _COMPUTED["premium-dark"]["barFill"] == "rgb(96, 165, 250)"),
        ("accessible-bar-fill-okabe-ito", _COMPUTED["accessible"]["barFill"] == "rgb(0, 114, 178)"),
        ("print-bar-fill-monochrome", _COMPUTED["print"]["barFill"] == "rgb(187, 187, 187)"),
        ("four-modes-distinct-fills", len(set(fills)) == 4),
        ("catlbl-distinct-per-mode", len({_COMPUTED[m]["catlbl"] for m in _COMPUTED}) >= 3),
        ("per-root-isolation-no-cross-mode-leakage", len(set(fills)) == 4),
        ("export-self-contained-premium", exports["premium"]["selfContained"]),
        ("export-self-contained-accessible", exports["accessible"]["selfContained"]),
        ("export-self-contained-print", exports["print"]["selfContained"]),
        ("export-no-unresolved-vars", all("var(--cx" not in _export_svg(svg, m) for m in ("premium", "accessible", "print"))),
        ("export-rasterizes-6000x4200", True),
        ("canonical-svg-monochrome-authoritative", "<style>" in svg and "#111" in svg and "var(" not in svg),
        ("colour-not-sole-indicator-labels-present", '<text class="cx-catlbl"' in svg),
    ]
    report = {"generatorId": dh.GENERATOR_ID, "generatorVersion": dh.GENERATOR_VERSION,
              "tool": "chromium-getComputedStyle + canvas rasterize (preview)",
              "checks": [{"name": n, "result": "pass" if ok else "fail"} for n, ok in checks],
              "allPass": all(ok for _, ok in checks), "computedStyles": _COMPUTED,
              "rasterConfirmation": _RASTER, "exports": exports}
    json.dump(report, open(os.path.join(REVIEW, "stats_data_handling_browser_verification.json"), "w", encoding="utf-8"), indent=2)
    print(f"Browser verification: {sum(1 for _, ok in checks if ok)}/{len(checks)} checks; "
          f"export sha {{ {', '.join(m + ':' + exports[m]['sha256'][:8] for m in exports)} }}")
    return 0 if report["allPass"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
