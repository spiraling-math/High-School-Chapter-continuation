/**
 * Style-isolation contract for the additive data-chart-theme (owner decision K).
 *
 * Asserts the extension reuses the approved cartesian-theme cx-figure isolation + shared
 * variables and adds statistics primitives, that each render mode produces distinct per-root
 * variables (so several modes / families coexist on one page without interference), and that
 * the materialised export is self-contained (no external CSS, no unresolved variables).
 *
 * Run:  node --test core/visual-style/data-chart-theme.test.ts
 */

import { test } from "node:test";
import assert from "node:assert/strict";
import {
  MODES, COMMON_CSS, DATA_CHART_COMMON_CSS, modeVars, modeVarStyle, resolveCommonCss,
  presentationSvg, exportSvg, modeBackground,
} from "./data-chart-theme.ts";
import { COMMON_CSS as CART_COMMON_CSS } from "./cartesian-theme.ts";

const SAMPLE = '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1000 700">'
  + "<style>.cx-bar{fill:#bbb}</style>"
  + '<rect class="cx-bar" data-cat="0" x="1" y="2" width="3" height="4"/>'
  + '<text class="cx-catlbl" x="5" y="6">Cat</text></svg>';

test("four modes; each carries shared + data-chart variables", () => {
  assert.deepEqual(MODES, ["print", "premium", "premium-dark", "accessible"]);
  for (const m of MODES) {
    const v = modeVars(m);
    assert.ok("--cx-axis" in v, `${m} reuses shared --cx-axis`);          // from cartesian
    assert.ok("--cx-bar-fill" in v, `${m} adds --cx-bar-fill`);            // data-chart primitive
    assert.ok("--cx-symbol-fill" in v && "--cx-catlbl" in v, `${m} adds symbol/label vars`);
  }
});

test("modes produce distinct bar fills (per-root isolation source)", () => {
  const fills = new Set(MODES.map((m) => modeVars(m)["--cx-bar-fill"]));
  assert.equal(fills.size, 4, "every mode has a distinct bar fill");
  assert.equal(modeVars("premium")["--cx-bar-fill"], "#3b82f6");
  assert.equal(modeVars("accessible")["--cx-bar-fill"], "#0072b2");      // Okabe-Ito
  assert.equal(modeVars("print")["--cx-bar-fill"], "#bbbbbb");           // monochrome authoritative
});

test("COMMON_CSS is additive: cartesian shared ruleset + data-chart ruleset", () => {
  assert.ok(COMMON_CSS.startsWith(CART_COMMON_CSS), "reuses the cartesian common ruleset verbatim");
  assert.ok(COMMON_CSS.includes(DATA_CHART_COMMON_CSS), "appends the data-chart ruleset");
  assert.ok(DATA_CHART_COMMON_CSS.includes(".cx-figure .cx-bar{fill:var(--cx-bar-fill)"), "bars themed via variable");
});

test("presentationSvg strips the canonical <style> and stamps a per-root cx-figure + vars", () => {
  const out = presentationSvg(SAMPLE, "premium");
  assert.ok(!out.includes("<style>"), "canonical monochrome <style> removed");
  assert.ok(out.includes('class="cx-figure"'), "isolation root class applied");
  assert.ok(out.includes("--cx-bar-fill:#3b82f6"), "premium variables on the root");
  // two figures in one document with different modes keep their own variables (no leakage)
  const doc = presentationSvg(SAMPLE, "premium") + presentationSvg(SAMPLE, "accessible");
  assert.ok(doc.includes("--cx-bar-fill:#3b82f6") && doc.includes("--cx-bar-fill:#0072b2"),
    "each figure root carries its own mode's variables");
});

test("exportSvg is self-contained: concrete colours, no unresolved variables, sized", () => {
  for (const m of MODES) {
    const out = exportSvg(SAMPLE, m, 6000, 4200);
    assert.ok(out.includes("<style>"), `${m} export bakes a <style>`);
    assert.ok(!out.includes("var(--cx"), `${m} export has no unresolved variables`);
    assert.ok(out.includes('width="6000"') && out.includes('height="4200"'), `${m} export is 6000x4200`);
  }
  assert.ok(exportSvg(SAMPLE, "premium").includes("fill:#3b82f6"), "premium bar colour materialised");
  assert.ok(resolveCommonCss("premium").includes("#3b82f6") && !resolveCommonCss("premium").includes("var("));
});

test("modeBackground reuses the shared --cx-bg (dark mode is dark)", () => {
  assert.equal(modeBackground("print"), "#ffffff");
  assert.equal(modeBackground("premium-dark"), "#0b1220");
});
