/**
 * gen.measurement.mensuration additive theme (owner J): verifies the per-root cx-figure isolation,
 * the four render modes, the self-contained 6000×4200 export, and that the theme is ADDITIVE over
 * cartesian-theme (it reuses cartesian variables and adds the mensuration dimension primitives).
 *
 * Run:  node --test core/visual-style/mensuration-theme.test.ts
 */

import { test } from "node:test";
import assert from "node:assert/strict";
import { MODES, COMMON_CSS, MENSURATION_COMMON_CSS, modeVars, modeVarStyle, resolveCommonCss, presentationSvg, exportSvg } from "./mensuration-theme.ts";
import { modeVars as cartModeVars } from "./cartesian-theme.ts";
import { generate } from "../../domains/measurement/mensuration.ts";

const MENS_VARS = ["--cx-fill", "--cx-edge", "--cx-dim", "--cx-unknown", "--cx-nts", "--cx-cut", "--cx-result"];

test("four modes, each providing every mensuration variable plus the inherited cartesian variables", () => {
  assert.deepEqual([...MODES].sort(), ["accessible", "premium", "premium-dark", "print"]);
  for (const mode of MODES) {
    const vars = modeVars(mode);
    for (const v of MENS_VARS) assert.ok(v in vars, `${mode} missing ${v}`);
    // additive: every cartesian variable is still present (inherited, not replaced)
    for (const k of Object.keys(cartModeVars(mode))) assert.ok(k in vars, `${mode} dropped inherited ${k}`);
  }
});

test("presentationSvg strips the canonical <style> and scopes one cx-figure root", () => {
  const item = generate(7) as { media: { svg: string }[] };
  const svg = item.media[0]!.svg;
  const pres = presentationSvg(svg, "premium");
  assert.ok(!/<style>/.test(pres), "canonical <style> must be stripped for presentation");
  assert.ok(pres.startsWith('<svg class="cx-figure" style="'));
  assert.ok(pres.includes("--cx-fill:") && pres.includes("--cx-edge:"));
});

test("exportSvg is self-contained 6000×4200 with concrete colours baked in (no var() left)", () => {
  const item = generate(7) as { media: { svg: string }[] };
  const out = exportSvg(item.media[0]!.svg, "print");
  assert.ok(out.includes('width="6000"') && out.includes('height="4200"'));
  assert.ok(out.includes("<style>") && out.includes(".cx-figure .cx-shape{"));
  const styleBlock = out.slice(out.indexOf("<style>"), out.indexOf("</style>"));
  assert.ok(!/var\(/.test(styleBlock), "export must bake concrete colours (no var())");
});

test("every cx-class used in a generated figure has a rule in the resolved CSS", () => {
  const classes = new Set<string>();
  for (let s = 0; s < 80; s++) {
    const item = generate(s) as { media: { svg: string; spec: { answerKeySvg: string } }[] };
    for (const svg of [item.media[0]!.svg, item.media[0]!.spec.answerKeySvg]) {
      for (const m of svg.matchAll(/class="(cx-[a-z]+)"/g)) classes.add(m[1]!);
    }
  }
  // Structural group wrappers (<g class="cx-base|cx-annot|cx-overlay">) and the root carry no fill/
  // stroke rule by design; only the drawn primitives are themed.
  const STRUCTURAL = new Set(["cx-figure", "cx-base", "cx-annot", "cx-overlay"]);
  const css = resolveCommonCss("premium");
  for (const c of classes) {
    if (STRUCTURAL.has(c)) continue;
    assert.ok(COMMON_CSS.includes(`.cx-figure .${c}{`) || MENSURATION_COMMON_CSS.includes(`.${c}{`), `no rule for .${c}`);
    assert.ok(css.includes(`.${c}{`) || css.includes(`.cx-figure .${c}{`), `unresolved rule for .${c}`);
  }
});
