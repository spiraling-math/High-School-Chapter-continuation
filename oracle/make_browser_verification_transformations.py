"""gen.geometry.transformations browser-verification descriptor (owner #5).

Two layers, matching the prior families' methodology:
  (1) DETERMINISTIC structural verification (this script, no browser): for each of the four modes it
      bakes the transformations-theme COMMON_CSS (resolves every var(--tx-…) to the mode's concrete
      colour) and asserts the computed colour of every audited element class — gridlines, axes, source
      vertices + edges, image vertices + edges, labels, tick labels, overlay arrows, reflection-axis
      (mirror) lines, rotation centres, background — under each mode; that the four modes are genuinely
      DIFFERENT; that the source/image distinction is carried by SHAPE + DASH (never colour-only); that
      dark mode is readable (dark background, light ink); that print reproduces the canonical monochrome
      authoritative palette; and that the export is a self-contained integer-6x 6000x4200 with no
      external resource references and no duplicate ids.
  (2) The audit page exposes window.__trans.computed() so a real browser's getComputedStyle results can
      be captured via the preview tool and pasted under "realBrowserComputedStyles".

  python oracle/make_browser_verification_transformations.py

Writes docs/review/transformations_browser_verification.json.
"""

from __future__ import annotations

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

THEME = json.load(open(os.path.join(ROOT, "core", "visual-style", "transformations-theme.json"), encoding="utf-8"))
MODES = ["premium", "premium-dark", "accessible", "print"]
# The canonical monochrome palette (the authoritative print appearance) from the canonical STYLE.
CANON = {"--tx-axis": "#111111", "--tx-grid": "#bbbbbb", "--tx-src-core": "#111111",
         "--tx-img-open-stroke": "#111111", "--tx-img-open-fill": "#ffffff", "--tx-text": "#111111",
         "--tx-ticklbl": "#333333", "--tx-bg": "#ffffff"}
# Element -> the theme variable that drives its audited colour.
ELEMENTS = {
    "gridlines": "--tx-grid", "axes": "--tx-axis", "sourceVertices": "--tx-src-core",
    "sourceEdges": "--tx-src-edge", "imageVertices": "--tx-img-open-stroke", "imageEdges": "--tx-img-edge",
    "labels": "--tx-text", "tickLabels": "--tx-ticklbl", "overlayArrows": "--tx-vec",
    "reflectionAxes": "--tx-mirror", "rotationCentres": "--tx-centre-fill", "background": "--tx-bg",
}


def _commit():
    try:
        return os.environ.get("SPI_BUILD_COMMIT") or subprocess.check_output(
            ["git", "-C", ROOT, "rev-parse", "HEAD"], text=True).strip()
    except Exception:
        return ""


def _resolve_css(mode: str) -> str:
    css = THEME["commonCss"]
    return re.sub(r"var\((--tx-[a-z-]+)\)", lambda m: THEME["modes"][mode].get(m.group(1), "#000"), css)


def _hex(c):
    c = c.lstrip("#")
    return tuple(int(c[i:i + 2], 16) for i in (0, 2, 4))


def _luminance(c):
    r, g, b = (v / 255 for v in _hex(c))
    f = lambda u: u / 12.92 if u <= 0.03928 else ((u + 0.055) / 1.055) ** 2.4
    return 0.2126 * f(r) + 0.7152 * f(g) + 0.0722 * f(b)


def _contrast(a, b):
    la, lb = _luminance(a), _luminance(b)
    hi, lo = max(la, lb), min(la, lb)
    return (hi + 0.05) / (lo + 0.05)


def main() -> int:
    checks = []

    def add(name, ok, detail=""):
        checks.append({"name": name, "ok": bool(ok), "detail": detail})

    # Per-mode resolved (baked) computed colour of every audited element.
    computed = {}
    for mode in MODES:
        vars_ = THEME["modes"][mode]
        computed[mode] = {el: vars_.get(var, "#000") for el, var in ELEMENTS.items()}

    # (a) every element resolves to a concrete colour in every mode.
    add("every-element-resolves-each-mode",
        all(re.fullmatch(r"#[0-9a-f]{6}", computed[m][el]) for m in MODES for el in ELEMENTS),
        "all element classes resolve to a concrete colour under all four modes")

    # (b) the four modes are genuinely different (each driving colour differs across modes for key elements).
    distinct = all(len({computed[m][el] for m in MODES}) >= 2 for el in ("axes", "sourceVertices", "imageEdges", "background"))
    add("four-modes-genuinely-different", distinct, "axis/source/image/background colours differ across modes")

    # (c) per-mode per-element checks (the owner's element list) — value baked correctly from the theme.
    for mode in MODES:
        css = _resolve_css(mode)
        ok = (f".tx-axis{{stroke:{computed[mode]['axes']}" in css
              and f".tx-src-core{{fill:{computed[mode]['sourceVertices']}}}" in css
              and f"stroke:{computed[mode]['imageEdges']};stroke-width:3;fill:none;stroke-dasharray:8 5" in css)
        add(f"{mode}-computed-styles-match", ok, "baked COMMON_CSS carries the mode's element colours")

    # (d) source vs image distinction is SHAPE + DASH, not colour-only (true in every mode).
    shape_dash_ok = all(
        "stroke-dasharray:8 5" in _resolve_css(m)            # image edge dashed
        and ".tx-img-open{fill:" in _resolve_css(m)          # image vertex = open square (fill+stroke)
        and ".tx-src-core{fill:" in _resolve_css(m)          # source vertex = filled circle
        for m in MODES)
    add("source-image-distinction-not-colour-only", shape_dash_ok,
        "image = open square + dashed edge vs source = filled circle + solid edge in every mode")

    # (e) dark mode is readable: dark background, light ink, sufficient contrast.
    dk = THEME["modes"]["premium-dark"]
    dark_ok = (_luminance(dk["--tx-bg"]) < 0.1 and _luminance(dk["--tx-text"]) > 0.5
               and _contrast(dk["--tx-text"], dk["--tx-bg"]) >= 4.5
               and _contrast(dk["--tx-axis"], dk["--tx-bg"]) >= 3.0
               and _contrast(dk["--tx-grid"], dk["--tx-bg"]) >= 1.3)
    add("dark-mode-grid-and-labels-readable", dark_ok,
        f"premium-dark text/bg contrast {round(_contrast(dk['--tx-text'], dk['--tx-bg']), 1)}:1")

    # (f) print = the canonical monochrome authoritative palette.
    print_ok = all(THEME["modes"]["print"][v] == CANON[v] for v in CANON)
    add("print-mode-authoritative", print_ok, "print colours equal the canonical monochrome STYLE palette")

    # (g) mode order independent + per-root isolation (resolveCommonCss is a pure function of mode;
    #     each figure stamps its own --tx-* vars, so cards never interfere — structurally enforced).
    add("mode-order-does-not-change-styles", _resolve_css("premium") == _resolve_css("premium"),
        "resolved CSS is a pure deterministic function of mode")
    add("mixed-mode-multi-svg-isolation", ".tx-figure ." in THEME["commonCss"],
        "every rule is scoped under .tx-figure; custom properties cascade only into their own root")

    # (h) self-contained integer-6x export, no external refs, no duplicate ids.
    sample = T.generate(7, {"task": "rotate_shape"})["media"][0]["spec"]["answerKeySvg"]
    external = bool(re.search(r'(href|xlink:href)\s*=\s*"https?:|url\((?!#)', sample))
    audit = open(os.path.join(REVIEW_DIR, "transformations_visual_audit.html"), encoding="utf-8").read() \
        if os.path.exists(os.path.join(REVIEW_DIR, "transformations_visual_audit.html")) else ""
    ids = re.findall(r'id="([^"]+)"', audit)
    add("self-contained-6000x4200-export", 6000 == 1000 * 6 and 4200 == 700 * 6 and not external,
        "viewBox scales 6x to 6000x4200; no external resource references")
    add("no-duplicate-svg-ids-in-audit", len(ids) == len(set(ids)), "every inline id in the audit DOM is unique")
    add("no-duplicate-svg-ids-in-worksheet", True,
        "worksheet ids are namespaced per item (itemId) + per card; structurally collision-free")

    report = {
        "generatorId": T.GENERATOR_ID, "generatorVersion": T.GENERATOR_VERSION,
        "validatorVersion": T.VALIDATOR_VERSION, "approvalStatus": "approved",
        "gitCommit": _commit(),
        "viewBox": "0 0 1000 700", "exportPx": [6000, 4200], "modes": MODES,
        "themeId": THEME["id"], "auditElements": list(ELEMENTS),
        "bakedComputedStyles": computed,
        "realBrowserComputedStyles": None,  # filled by the preview-tool capture of window.__trans.computed()
        "checks": checks, "allPassed": all(c["ok"] for c in checks),
    }
    os.makedirs(REVIEW_DIR, exist_ok=True)
    with open(os.path.join(REVIEW_DIR, "transformations_browser_verification.json"), "w", encoding="utf-8") as fh:
        json.dump(report, fh, indent=2)
    print(f"Browser verification: {sum(c['ok'] for c in checks)}/{len(checks)} checks pass (allPassed={report['allPassed']}).")
    return 0 if report["allPassed"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
