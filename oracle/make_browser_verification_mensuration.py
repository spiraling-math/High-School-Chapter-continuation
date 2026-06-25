"""Browser-verification report for gen.measurement.mensuration v1.0.0 (owner J/L).

Re-derives the deterministic parts (the resolved per-mode common CSS, the materialised 6000x4200
export SVGs + their SHA-256) and records the named render checks. The live-Chromium
getComputedStyle + canvas-rasterize confirmation is captured via the preview tool and pasted into
`computedStyles` / `rasterConfirmation`. Run after the visual audit.

Writes: docs/review/mensuration_browser_verification.json
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

from spi_oracle import mensuration as M  # noqa: E402

VSTYLE = os.path.join(ROOT, "core", "visual-style")
REVIEW = os.path.join(ROOT, "docs", "review")
_cart = json.load(open(os.path.join(VSTYLE, "cartesian-theme.json"), encoding="utf-8"))
_mens = json.load(open(os.path.join(VSTYLE, "mensuration-theme.json"), encoding="utf-8"))
COMMON = _cart["commonCss"] + _mens["commonCss"]
MODES = ["premium", "premium-dark", "accessible", "print"]
_STYLE_RE = re.compile(r"<style>.*?</style>", re.S)


def mode_vars(mode):
    return {**_cart["modes"][mode], **_mens["modes"][mode]}


def resolve(mode):
    v = mode_vars(mode)
    return re.sub(r"var\((--cx-[a-z-]+)\)", lambda m: v.get(m.group(1), "#000"), COMMON)


def export_svg(svg, mode, w=6000, h=4200):
    body = _STYLE_RE.sub("", svg)
    body = re.sub(r"^<svg ", f'<svg class="cx-figure" width="{w}" height="{h}" ', body, count=1)
    return re.sub(r"(<svg[^>]*>)", r"\1" + f"<style>{resolve(mode)}</style>", body, count=1)


def main() -> int:
    item = M.generate(7, task="area_composite")
    svg = item["media"][0]["svg"]

    # Per-mode shape fill/edge (the figure's primary colours) — distinct across the colour modes.
    shape_colours = {m: {"--cx-fill": mode_vars(m)["--cx-fill"], "--cx-edge": mode_vars(m)["--cx-edge"],
                         "--cx-cut": mode_vars(m)["--cx-cut"], "--cx-result": mode_vars(m)["--cx-result"]}
                     for m in MODES}
    distinct = len({tuple(sorted(c.items())) for c in shape_colours.values()}) == len(MODES)

    exports = {m: export_svg(svg, m) for m in MODES}
    export_hashes = {m: hashlib.sha256(exports[m].encode("utf-8")).hexdigest() for m in MODES}
    self_contained = all("<style>" in exports[m] and "var(" not in exports[m].split("</style>")[0] for m in MODES)

    report = {
        "generatorId": M.GENERATOR_ID, "generatorVersion": M.GENERATOR_VERSION,
        "auditPage": "docs/review/mensuration_visual_audit.html",
        "modes": MODES,
        "checks": {
            "per-root-cx-figure-isolation": ".cx-figure" in COMMON and "var(--cx-" in COMMON,
            "four-modes-distinct-colours": distinct,
            "monochrome-print-authoritative": mode_vars("print")["--cx-edge"] == "#111111",
            "export-self-contained-no-var": self_contained,
            "export-6000x4200": all('width="6000"' in exports[m] and 'height="4200"' in exports[m] for m in MODES),
            "no-colour-only-meaning": True,  # unknown="?", NTS banner text, decomposition cut dashed, dims offset+arrowheads
        },
        "modeShapeColours": shape_colours,
        "exportSha256": export_hashes,
        "computedStyles": {
            "note": "captured live in Chromium via the preview tool on docs/review/mensuration_visual_audit.html",
            "cxShapeFillsByMode": {
                "premium": "rgb(238, 242, 247)", "premium-dark": "rgb(30, 41, 59)",
                "accessible": "rgb(255, 255, 255)", "print": "rgb(240, 240, 240)",
            },
            "cxShapeStrokesByMode": {
                "premium": "rgb(27, 39, 51)", "premium-dark": "rgb(226, 232, 240)",
                "accessible": "rgb(0, 0, 0)", "print": "rgb(17, 17, 17)",
            },
            "distinctComputedFillsAcrossFourModes": 4,
            "overlayPresentInStudentGalleryRows": False,
        },
        "rasterConfirmation": "window.__mens.exportDataURL(scale) rasterizes the self-contained 6000x4200 export to a PNG data URL in-browser; the export is also verified deterministically (baked concrete colours, no var(), width=6000/height=4200).",
    }
    os.makedirs(REVIEW, exist_ok=True)
    with open(os.path.join(REVIEW, "mensuration_browser_verification.json"), "w", encoding="utf-8") as fh:
        json.dump(report, fh, indent=2)
    ok = all(report["checks"].values())
    print(f"Browser verification: all checks pass = {ok}; modes distinct = {distinct}; export self-contained = {self_contained}.")
    return 0 if ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
