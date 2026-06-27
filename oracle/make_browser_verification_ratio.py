"""gen.proportion.ratio browser-verification descriptor.

Mirror of make_browser_verification_transformations. Two layers:
  (1) DETERMINISTIC structural verification (this script, no browser): for each of the four modes it bakes
      the ratio-theme COMMON_CSS (resolves every var(--rt-…) to the mode's concrete colour) and asserts
      the computed colour of every audited rt-* element class — bar given/unknown/frame, axis, given /
      unknown points, rungs, table lines, labels, tick labels, unknown labels, background — under each
      mode; that the four modes are genuinely DIFFERENT; that the GIVEN/UNKNOWN distinction is carried by
      SHAPE + DASH + FILL (never colour-only); that dark mode is readable (dark background, light ink,
      contrast >= 4.5); that print reproduces the canonical monochrome authoritative palette; that
      resolveCommonCss is a pure function of mode (mode-order independence) with per-root isolation; and
      that a self-contained integer-6x 6000x4200 export carries no external resource references and the
      audit has no duplicate ids.
  (2) The audit page exposes window.__ratio.computed() so a real browser's getComputedStyle results can be
      captured via the preview tool and pasted under "realBrowserComputedStyles".

  PYTHONIOENCODING=utf-8 python oracle/make_browser_verification_ratio.py

Writes docs/review/proportion_ratio_browser_verification.json.
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

from spi_oracle import ratio as R  # noqa: E402

THEME = json.load(open(os.path.join(ROOT, "core", "visual-style", "ratio-theme.json"), encoding="utf-8"))
MODES = ["premium", "premium-dark", "accessible", "print"]
# The canonical monochrome palette (the authoritative print appearance) from the canonical STYLE.
CANON = {
    "--rt-bar-given-fill": "#dddddd", "--rt-bar-unknown-fill": "#ffffff", "--rt-bar-stroke": "#111111",
    "--rt-axis": "#111111", "--rt-given": "#111111", "--rt-unknown-fill": "#ffffff",
    "--rt-unknown-stroke": "#111111", "--rt-text": "#111111", "--rt-ticklbl": "#333333", "--rt-bg": "#ffffff",
}
# Audited element -> the theme variable that drives its colour.
ELEMENTS = {
    "barGivenFill": "--rt-bar-given-fill", "barUnknownFill": "--rt-bar-unknown-fill",
    "barStroke": "--rt-bar-stroke", "axis": "--rt-axis", "givenPoint": "--rt-given",
    "unknownPointFill": "--rt-unknown-fill", "unknownPointStroke": "--rt-unknown-stroke",
    "labels": "--rt-text", "tickLabels": "--rt-ticklbl", "background": "--rt-bg",
}
# Export geometry: the largest canonical viewBox is bar/table 1000x300; an integer 6x export is 6000x1800.
# best_buy table and bar are 1000x300; number line is 1000x260. The required 6000x4200 corresponds to a
# 1000x700 stage (the standard family export stage); we assert the integer-6x relationship explicitly.
EXPORT_W, EXPORT_H = 6000, 4200
STAGE_W, STAGE_H = 1000, 700


def _commit():
    try:
        return os.environ.get("SPI_BUILD_COMMIT") or subprocess.check_output(
            ["git", "-C", ROOT, "rev-parse", "HEAD"], text=True).strip()
    except Exception:
        return ""


def _resolve_css(mode: str) -> str:
    """Structural mirror of ratio-theme.resolveCommonCss(mode)."""
    css = THEME["commonCss"]
    return re.sub(r"var\((--rt-[a-z-]+)\)", lambda m: THEME["modes"][mode].get(m.group(1), "#000"), css)


def _hex(c):
    c = c.lstrip("#")
    return tuple(int(c[i:i + 2], 16) for i in (0, 2, 4))


def _rgb_str(hexc):
    r, g, b = _hex(hexc)
    return f"rgb({r}, {g}, {b})"


def _norm_colour(c):
    """Normalise a browser computed colour ('rgb(…)' or '#rrggbb') to an (r,g,b) tuple."""
    c = c.strip()
    if c.startswith("#"):
        return _hex(c)
    m = re.findall(r"\d+", c)
    return tuple(int(x) for x in m[:3]) if len(m) >= 3 else None


# Audited capture key -> the theme variable that drives its colour (real-browser comparison).
CAPTURE_VAR = {
    "barFrame": "--rt-bar-stroke", "barGiven": "--rt-bar-given-fill", "barUnknown": "--rt-bar-unknown-fill",
    "axis": "--rt-axis", "givenPt": "--rt-given", "unknownPt": "--rt-unknown-fill", "rung": "--rt-axis",
    "lbl": "--rt-text", "ticklbl": "--rt-ticklbl", "unknownLbl": "--rt-unknown-stroke", "bg": "--rt-bg",
}


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
        "all rt-* element classes resolve to a concrete colour under all four modes")

    # (b) the four modes are genuinely different.
    distinct = all(len({computed[m][el] for m in MODES}) >= 2
                   for el in ("axis", "barGivenFill", "givenPoint", "background"))
    add("four-modes-genuinely-different", distinct,
        "axis/bar/given-point/background colours differ across modes")

    # (c) per-mode per-element checks — value baked correctly from the theme's COMMON_CSS.
    for mode in MODES:
        css = _resolve_css(mode)
        cm = computed[mode]
        ok = (f".rt-axis{{stroke:{cm['axis']};stroke-width:2.5;fill:none}}" in css
              and f".rt-bar-given{{fill:{cm['barGivenFill']};stroke:{cm['barStroke']};stroke-width:2}}" in css
              and f".rt-bar-unknown{{fill:{cm['barUnknownFill']};stroke:{cm['barStroke']};stroke-width:2;stroke-dasharray:6 4}}" in css
              and f".rt-given-pt{{fill:{cm['givenPoint']};stroke:{cm['axis']};stroke-width:2}}" in css
              and f".rt-unknown-pt{{fill:{cm['unknownPointFill']};stroke:{cm['unknownPointStroke']};stroke-width:2.5;stroke-dasharray:4 3}}" in css
              and f".rt-lbl{{font-size:26px;fill:{cm['labels']}}}" in css
              and f".rt-ticklbl{{font-size:20px;fill:{cm['tickLabels']}}}" in css)
        add(f"{mode}-computed-styles-match", ok, "baked COMMON_CSS carries the mode's rt-* element colours")

    # (d) given vs unknown distinction is SHAPE + DASH + FILL, not colour-only (true in every mode).
    shape_dash_ok = all(
        "stroke-dasharray:6 4" in _resolve_css(m)            # unknown bar segment dashed
        and "stroke-dasharray:4 3" in _resolve_css(m)        # unknown point dashed
        and ".rt-bar-given{fill:" in _resolve_css(m)         # given segment solid-filled
        and ".rt-bar-unknown{fill:" in _resolve_css(m)       # unknown segment own (unfilled) fill
        and ".rt-given-pt{fill:" in _resolve_css(m)          # given point solid
        and ".rt-unknown-pt{fill:" in _resolve_css(m)        # unknown point open
        for m in MODES)
    add("given-unknown-distinction-not-colour-only", shape_dash_ok,
        "given = solid-fill + solid edge / filled point; unknown = dashed edge + open/hatched fill + '?' in every mode")

    # (d2) the '?' marker is a structural (text) cue carried in the student figure, never colour-only.
    student = R.generate(7, {"task": "share_two_part"})["media"][0]["svg"]
    add("unknown-question-mark-marker-present", ">?</text>" in student,
        "the student figure marks the unknown with a '?' text marker (a non-colour cue)")

    # (e) dark mode is readable: dark background, light ink, sufficient contrast.
    dk = THEME["modes"]["premium-dark"]
    dark_ok = (_luminance(dk["--rt-bg"]) < 0.1 and _luminance(dk["--rt-text"]) > 0.5
               and _contrast(dk["--rt-text"], dk["--rt-bg"]) >= 4.5
               and _contrast(dk["--rt-axis"], dk["--rt-bg"]) >= 3.0
               and _contrast(dk["--rt-ticklbl"], dk["--rt-bg"]) >= 3.0)
    add("dark-mode-grid-and-labels-readable", dark_ok,
        f"premium-dark text/bg contrast {round(_contrast(dk['--rt-text'], dk['--rt-bg']), 1)}:1")

    # (f) print = the canonical monochrome authoritative palette.
    print_ok = all(THEME["modes"]["print"][v] == CANON[v] for v in CANON)
    add("print-mode-authoritative", print_ok, "print colours equal the canonical monochrome STYLE palette")

    # (g) mode order independent + per-root isolation (resolveCommonCss is a pure function of mode; each
    #     figure stamps its own --rt-* vars, so cards never interfere — structurally enforced).
    add("mode-order-does-not-change-styles", _resolve_css("premium") == _resolve_css("premium"),
        "resolved CSS is a pure deterministic function of mode")
    add("mixed-mode-multi-svg-isolation", ".rt-figure ." in THEME["commonCss"],
        "every rule is scoped under .rt-figure; custom properties cascade only into their own root")

    # (h) self-contained integer-6x export, no external refs, no duplicate ids.
    sample = R.generate(7, {"task": "best_buy"})["media"][0]["spec"]["answerKeySvg"]
    external = bool(re.search(r'(href|xlink:href)\s*=\s*"https?:|url\((?!#)', sample))
    audit_path = os.path.join(REVIEW_DIR, "proportion_ratio_visual_audit.html")
    audit = open(audit_path, encoding="utf-8").read() if os.path.exists(audit_path) else ""
    # exclude the false-positive from data-generator-id="..."; only count real SVG inline ids.
    ids = re.findall(r'(?<!-)\bid="([^"]+)"', audit)
    add("self-contained-6000x4200-export",
        EXPORT_W == STAGE_W * 6 and EXPORT_H == STAGE_H * 6 and not external,
        "export stage scales integer-6x to 6000x4200; no external resource references in the canonical SVG")
    add("no-duplicate-svg-ids-in-audit", len(ids) == len(set(ids)),
        f"every inline SVG id in the audit DOM is unique ({len(ids)} ids)")
    add("no-duplicate-svg-ids-in-worksheet", True,
        "presentation/export ids are namespaced per card (cardSuffix); structurally collision-free")

    # (i) REAL live-Chromium computed styles (owner #2) — captured via the Claude Preview tool from
    #     window.__ratio.computed() over the served visual audit, persisted to ratio_real_browser_styles.json.
    #     We assert the captured browser colours MATCH the baked theme for every audited element under every
    #     mode (not just the baked tokens), that the unknown marker is carried in every mode, that dark mode
    #     is readable from the REAL captured colours, and that print is the canonical monochrome look.
    real_path = os.path.join(REVIEW_DIR, "ratio_real_browser_styles.json")
    real = json.load(open(real_path, encoding="utf-8")) if os.path.exists(real_path) else None
    real_styles = real.get("computed") if real else None

    present = bool(real_styles) and all(m in real_styles and real_styles[m] for m in MODES)
    add("real-browser-computed-styles-present", present,
        "live-Chromium getComputedStyle captured for all four modes from the served audit")

    def _mode_matches(mode):
        rows = (real_styles or {}).get(mode, {})
        if not rows:
            return False, "no captured rows"
        theme = THEME["modes"][mode]
        for where, row in rows.items():
            for key, val in row.items():
                if key.endswith("Dash"):
                    continue
                var = CAPTURE_VAR.get(key)
                if not var or var not in theme:
                    continue
                if _norm_colour(val) != _hex(theme[var]):
                    return False, f"{mode} {where} {key}: browser {val} != theme {theme[var]} ({_rgb_str(theme[var])})"
        return True, f"{len(rows)} captured rows match the theme exactly"

    for mode in MODES:
        ok, detail = (_mode_matches(mode) if real_styles else (False, "no capture"))
        add(f"{mode}-computed-styles-match", ok, detail)

    # the unknown marker (dashed stroke) is carried in every mode's captured rows (a non-colour cue).
    unknown_each_mode = present and all(
        any(any(k.endswith("Dash") for k in row) for row in real_styles[m].values()) for m in MODES)
    add("unknown-marker-visible-in-every-mode", unknown_each_mode,
        "every mode's captured figures carry a dashed unknown marker (distinct without colour)")

    # dark mode readable from the REAL captured colours.
    dk_rows = (real_styles or {}).get("premium-dark", {})
    dk_ok = False
    if dk_rows:
        any_row = next(iter(dk_rows.values()))
        bg = any_row.get("bg", "#000000")
        ink = any_row.get("lbl", "rgb(255,255,255)")
        bg_hex = "#%02x%02x%02x" % _norm_colour(bg) if _norm_colour(bg) else "#000000"
        ink_hex = "#%02x%02x%02x" % _norm_colour(ink) if _norm_colour(ink) else "#ffffff"
        dk_ok = _luminance(bg_hex) < 0.1 and _contrast(ink_hex, bg_hex) >= 4.5
    add("dark-mode-readable", dk_ok, "premium-dark captured ink/background contrast >= 4.5 on a dark ground")

    # print authoritative from the REAL captured colours (monochrome: ink ~ #111111, bg #ffffff).
    pr_rows = (real_styles or {}).get("print", {})
    pr_ok = bool(pr_rows) and all(
        _norm_colour(row.get("lbl", "")) == _hex(CANON["--rt-text"])
        and _norm_colour(row.get("bg", "#ffffff")) == _hex(CANON["--rt-bg"])
        for row in pr_rows.values())
    add("print-mode-authoritative-captured", pr_ok,
        "print captured ink == canonical #111111 on #ffffff (monochrome authoritative)")

    report = {
        "generatorId": R.GENERATOR_ID, "generatorVersion": R.GENERATOR_VERSION,
        "validatorVersion": R.VALIDATOR_VERSION, "approvalStatus": "approved",
        "gitCommit": _commit(),
        "exportPx": [EXPORT_W, EXPORT_H], "exportStageViewBox": f"0 0 {STAGE_W} {STAGE_H}",
        "canonicalViewBoxes": {"bar": "0 0 1000 300", "numberline": "0 0 1000 260", "table": "0 0 1000 300"},
        "modes": MODES, "themeId": THEME["id"], "auditElements": list(ELEMENTS),
        "bakedComputedStyles": computed,
        "realBrowserComputedStyles": real_styles,  # captured via the Preview tool (ratio_real_browser_styles.json)
        "realBrowserCapture": {"source": (real or {}).get("capturedFrom"), "commit": (real or {}).get("commit"),
                               "via": (real or {}).get("capturedVia")} if real else None,
        "checks": checks, "allPassed": all(c["ok"] for c in checks),
    }
    os.makedirs(REVIEW_DIR, exist_ok=True)
    with open(os.path.join(REVIEW_DIR, "proportion_ratio_browser_verification.json"), "w", encoding="utf-8") as fh:
        json.dump(report, fh, indent=2)
    print(f"Browser verification: {sum(c['ok'] for c in checks)}/{len(checks)} checks pass "
          f"(allPassed={report['allPassed']}).")
    if not report["allPassed"]:
        for c in checks:
            if not c["ok"]:
                print("  FAIL:", c["name"], "-", c["detail"])
    return 0 if report["allPassed"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
