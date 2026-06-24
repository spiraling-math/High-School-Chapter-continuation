/**
 * CI gate for the coordinate-lines render-mode style ISOLATION + materialized export
 * (DECISION_LOG #43). The v1.0.1 visual audit leaked styles: every inline SVG repeated
 * unscoped global selectors (`.cx-line{stroke:#111}`) so the last SVG won the document
 * cascade and the premium/dark/accessible modes lost their colours. v1.0.2 isolates each
 * figure with PER-ROOT CSS custom properties + one common `.cx-figure` ruleset.
 *
 * These node checks assert the mechanism structurally; the real-browser getComputedStyle +
 * 6000x4200 export pixel results are captured in docs/review/coordinate_lines_browser_verification.json.
 *
 * Run:  node --test domains/geometry/coordinate-lines-style-isolation.test.ts
 */

import { test } from "node:test";
import assert from "node:assert/strict";
import { readFileSync } from "node:fs";
import { fileURLToPath } from "node:url";
import { presentationSvg, exportSvg, resolveCommonCss, modeBackground, modeVars, MODES, COMMON_CSS } from "../../core/visual-style/cartesian-theme.ts";
import { generate } from "./coordinate-lines.ts";

const ROOT = fileURLToPath(new URL("../../", import.meta.url));
const canonical = (generate(2, { task: "equation_from_two_points", interactionType: "free-response" }) as { media: { svg: string }[] }).media[0]!.svg;

test("theme: presentation copy strips the canonical <style> and stamps per-root variables", () => {
  for (const mode of MODES) {
    const pres = presentationSvg(canonical, mode);
    assert.ok(!/<style>/.test(pres), `${mode}: canonical <style> must be stripped`);
    assert.match(pres, /^<svg class="cx-figure" style="--cx-/, `${mode}: per-root variables on the root`);
    assert.ok(pres.includes(`--cx-line:${modeVars(mode)["--cx-line"]}`), `${mode}: own --cx-line value`);
  }
});

test("theme: common ruleset is scoped to .cx-figure and reads variables (no global selectors)", () => {
  for (const sel of [".cx-line", ".cx-axis", ".cx-grid-major", ".cx-grid-minor", ".cx-pt-core", ".cx-pt-outline", ".cx-ticklbl"]) {
    assert.ok(COMMON_CSS.includes(`.cx-figure ${sel}{`), `${sel} must be scoped under .cx-figure`);
    assert.ok(!new RegExp(`(^|[^e] )\\${sel}\\{`).test(COMMON_CSS), `${sel} must never appear unscoped`);
  }
  assert.ok(COMMON_CSS.includes("var(--cx-line)"), "colours come from custom properties");
});

test("theme: export copy is self-contained (concrete colours, no var(), 6000x4200) and modes differ", () => {
  const prem = exportSvg(canonical, "premium", 6000, 4200);
  const mono = exportSvg(canonical, "print", 6000, 4200);
  assert.match(prem, /<svg class="cx-figure" width="6000" height="4200"/);
  assert.ok(!prem.includes("var(--"), "export must bake concrete colours, no var()");
  assert.ok(!/<link|@import|url\(/.test(prem), "export must not reference external CSS / network");
  assert.ok(prem.includes(".cx-figure .cx-line{stroke:#2563eb"), "premium export bakes premium blue");
  assert.ok(mono.includes(".cx-figure .cx-line{stroke:#111111"), "print export bakes monochrome ink");
  assert.notEqual(resolveCommonCss("premium"), resolveCommonCss("print"), "premium and monochrome differ");
});

test("theme: dark mode line + text are light (readable on the dark background)", () => {
  const v = modeVars("premium-dark");
  assert.notEqual(v["--cx-line"], "#111111");
  assert.notEqual(v["--cx-text"], "#111111");
  assert.equal(modeBackground("premium-dark"), "#0b1220");
  // a light foreground on a dark background: line/text brightness clearly exceeds the bg.
  const lum = (hex: string): number => { const n = parseInt(hex.slice(1), 16); return ((n >> 16) & 255) + ((n >> 8) & 255) + (n & 255); };
  assert.ok(lum(v["--cx-line"]!) > lum("#0b1220") + 200, "dark-mode line visible");
  assert.ok(lum(v["--cx-text"]!) > lum("#0b1220") + 200, "dark-mode text visible");
});

test("theme: theming never mutates the canonical item SVG", () => {
  const again = (generate(2, { task: "equation_from_two_points", interactionType: "free-response" }) as { media: { svg: string }[] }).media[0]!.svg;
  assert.equal(again, canonical);
  presentationSvg(canonical, "premium");
  exportSvg(canonical, "premium-dark");
  assert.equal((generate(2, { task: "equation_from_two_points", interactionType: "free-response" }) as { media: { svg: string }[] }).media[0]!.svg, canonical);
});

test("audit HTML: exactly one scoped common ruleset and ZERO active unscoped global cx-* style blocks", () => {
  const html = readFileSync(ROOT + "docs/review/coordinate_lines_visual_audit.html", "utf8");
  const styleBlocks = [...html.matchAll(/<style[^>]*>([\s\S]*?)<\/style>/g)].map((m) => m[1]!);
  const common = styleBlocks.filter((s) => s.includes(".cx-figure .cx-line{stroke:var(--cx-line)"));
  assert.equal(common.length, 1, "exactly one common .cx-figure ruleset");
  // No active <style> block carries an UNSCOPED global `.cx-line{stroke:#…}` (the v1.0.1 defect).
  for (const s of styleBlocks) {
    assert.ok(!/(^|[^e] )\.cx-line\{stroke:#/.test(s), "no unscoped global .cx-line override in any active style block");
  }
});

test("audit HTML: every gallery presentation SVG carries its own per-root cx- variables", () => {
  const html = readFileSync(ROOT + "docs/review/coordinate_lines_visual_audit.html", "utf8");
  const gallery = html.slice(html.indexOf('id="gallery"'), html.indexOf('id="galleryRev"'));
  const figs = [...gallery.matchAll(/<svg class="cx-figure" style="([^"]*)"/g)].map((m) => m[1]!);
  assert.ok(figs.length >= 4, "four gallery figures present");
  for (const style of figs) assert.match(style, /--cx-line:#[0-9a-f]{6}/, "each figure stamps its own --cx-line");
  // the embedded export theme keeps the dark line light (not monochrome ink)
  assert.ok(!/"premium-dark":\{[^}]*"--cx-line":"#111111"/.test(html), "dark line is not monochrome ink");
});
