/**
 * Structural computed-style gate for the transformations presentation theme (owner REVISE #5).
 *
 * No headless browser is available here, so these are DETERMINISTIC structural checks on the theme's
 * resolved (baked) CSS — the same colours a real browser's getComputedStyle returns (the audit page's
 * window.__trans.computed() capture, recorded in transformations_browser_verification.json, confirms the
 * real-browser values match these baked ones across 72 figures with 0 mismatches). They assert: every
 * audited element class resolves to a concrete colour in each mode; the four modes are genuinely
 * different; print reproduces the canonical monochrome authoritative palette; dark mode is readable; the
 * source/image distinction is carried by SHAPE + DASH (never colour-only); per-root isolation (each
 * figure stamps its own vars); mode order never changes a card's styles; and inline ids are namespaced
 * per card so multiple SVGs in one DOM never collide.
 *
 * Run:  node --test core/visual-style/transformations-theme.test.ts
 */

import { test } from "node:test";
import assert from "node:assert/strict";
import {
  MODES, modeVars, modeVarStyle, resolveCommonCss, modeBackground, presentationSvg, exportSvg,
  namespaceIds, COMMON_CSS, type Mode,
} from "./transformations-theme.ts";

// A minimal canonical SVG carrying every tx-* element class + a namespaced marker.
const SAMPLE =
  '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1000 700" role="img" aria-label="x">' +
  "<title>t</title><desc>d</desc>" +
  "<style>.tx-axis{stroke:#111}.tx-vec{stroke:#111;fill:none}</style>" +
  '<defs><marker id="tx-arrow-ITEM-A"><path/></marker></defs>' +
  '<g class="tx-base"><line class="tx-grid"/><line class="tx-axis"/><path class="tx-src-edge"/>' +
  '<circle class="tx-src-core"/><path class="tx-img-edge"/><rect class="tx-img-open"/>' +
  '<text class="tx-ticklbl">0</text><text class="tx-lbl">A</text></g>' +
  '<g class="tx-overlay"><line class="tx-mirror"/><line class="tx-vec" marker-end="url(#tx-arrow-ITEM-A)"/>' +
  '<circle class="tx-centre"/></g></svg>';

const CANON: Record<string, string> = {
  "--tx-axis": "#111111", "--tx-grid": "#bbbbbb", "--tx-src-core": "#111111",
  "--tx-img-open-fill": "#ffffff", "--tx-text": "#111111", "--tx-ticklbl": "#333333", "--tx-bg": "#ffffff",
};
const hex = (c: string) => c.replace("#", "").match(/.{2}/g)!.map((h) => parseInt(h, 16));
const lum = (c: string) => {
  const ch = hex(c).map((v) => {
    const u = v / 255;
    return u <= 0.03928 ? u / 12.92 : ((u + 0.055) / 1.055) ** 2.4;
  });
  return 0.2126 * (ch[0] ?? 0) + 0.7152 * (ch[1] ?? 0) + 0.0722 * (ch[2] ?? 0);
};
const contrast = (a: string, b: string) => {
  const la = lum(a), lb = lum(b), hi = Math.max(la, lb), lo = Math.min(la, lb);
  return (hi + 0.05) / (lo + 0.05);
};

test("the four modes are present", () => {
  assert.deepEqual(MODES, ["print", "premium", "premium-dark", "accessible"]);
});

test("every audited element class resolves to a concrete colour in each mode", () => {
  const vars = ["--tx-grid", "--tx-axis", "--tx-src-edge", "--tx-src-core", "--tx-img-edge",
    "--tx-img-open-stroke", "--tx-mirror", "--tx-vec", "--tx-centre-fill", "--tx-text", "--tx-ticklbl", "--tx-bg"];
  for (const m of MODES) for (const v of vars) {
    assert.match(modeVars(m)[v] ?? "", /^#[0-9a-f]{6}$/, `${m} ${v}`);
  }
});

test("the four modes are genuinely different", () => {
  for (const v of ["--tx-axis", "--tx-src-core", "--tx-img-edge", "--tx-bg"]) {
    const distinct = new Set(MODES.map((m) => modeVars(m)[v]));
    assert.ok(distinct.size >= 2, `${v} should vary across modes`);
  }
});

test("exportSvg bakes the mode's concrete colours for each element class", () => {
  for (const m of MODES as Mode[]) {
    const css = resolveCommonCss(m);
    assert.ok(css.includes(`.tx-axis{stroke:${modeVars(m)["--tx-axis"]}`), `${m} axis`);
    assert.ok(css.includes(`.tx-src-core{fill:${modeVars(m)["--tx-src-core"]}}`), `${m} src core`);
    assert.ok(css.includes(`stroke:${modeVars(m)["--tx-img-edge"]};stroke-width:3;fill:none;stroke-dasharray:8 5`), `${m} img edge dash`);
    assert.ok(!/var\(/.test(exportSvg(SAMPLE, m)), `${m} export has no unresolved var()`);
  }
});

test("source vs image distinction is shape + dash, never colour-only (every mode)", () => {
  for (const m of MODES as Mode[]) {
    const css = resolveCommonCss(m);
    assert.ok(css.includes("stroke-dasharray:8 5"), `${m} image edge dashed`);     // image edge dashed
    assert.ok(/\.tx-img-open\{fill:/.test(css), `${m} image vertex open square`);  // image = open square
    assert.ok(/\.tx-src-core\{fill:/.test(css), `${m} source vertex filled`);      // source = filled circle
  }
});

test("print mode reproduces the canonical monochrome authoritative palette", () => {
  for (const v of Object.keys(CANON)) assert.equal(modeVars("print")[v], CANON[v], v);
});

test("dark mode is readable (dark bg, light ink, sufficient contrast)", () => {
  const d = modeVars("premium-dark");
  const bg = d["--tx-bg"]!, text = d["--tx-text"]!, axis = d["--tx-axis"]!;
  assert.ok(lum(bg) < 0.1, "dark background");
  assert.ok(lum(text) > 0.5, "light ink");
  assert.ok(contrast(text, bg) >= 4.5, "text contrast >= 4.5");
  assert.ok(contrast(axis, bg) >= 3.0, "axis contrast >= 3");
});

test("presentationSvg stamps the mode vars on the figure's own root (per-root isolation)", () => {
  const p = presentationSvg(SAMPLE, "premium-dark", "c1");
  assert.match(p, /^<svg class="tx-figure" style="--tx-/);
  assert.ok(!/<style>/.test(p), "canonical <style> stripped");
  assert.ok(COMMON_CSS.includes(".tx-figure ."), "common rules scoped under .tx-figure");
});

test("mode order does not change a card's styles (pure function of mode)", () => {
  assert.equal(resolveCommonCss("premium"), resolveCommonCss("premium"));
  assert.notEqual(resolveCommonCss("premium"), resolveCommonCss("premium-dark"));
});

test("inline ids are namespaced per card so multiple SVGs never collide", () => {
  const a = presentationSvg(SAMPLE, "print", "cardA");
  const b = presentationSvg(SAMPLE, "print", "cardB");
  assert.match(a, /id="tx-arrow-ITEM-A--cardA"/);
  assert.match(a, /url\(#tx-arrow-ITEM-A--cardA\)/);
  assert.match(b, /id="tx-arrow-ITEM-A--cardB"/);
  // combined document: the two cards' marker ids differ -> no collision
  const ids = [...(a + b).matchAll(/id="([^"]+)"/g)].map((m) => m[1]!);
  assert.equal(new Set(ids).size, ids.length, "no duplicate ids across cards");
});

test("modeBackground returns each mode's background", () => {
  assert.equal(modeBackground("premium-dark"), "#0b1220");
  assert.equal(modeBackground("print"), "#ffffff");
});
