/**
 * Shared Cartesian presentation theme (coordinate-lines + future data-viz families).
 *
 * Render modes are sets of CSS CUSTOM PROPERTIES applied to each figure's OWN root SVG
 * (`class="cx-figure"`). A single immutable common ruleset (`COMMON_CSS`) reads those
 * variables. Because custom properties cascade only into their own subtree, every figure is
 * isolated — multiple modes on one page, reordered cards, several questions per worksheet,
 * and SVGs from other generator families never interfere (the v1.0.1 defect, where unscoped
 * global `.cx-line{stroke:#111}` blocks from later inline SVGs overrode earlier premium
 * rules, is structurally impossible here).
 *
 * - `presentationSvg(svg, mode)` — for IN-DOCUMENT display: strips the canonical SVG's
 *   internal monochrome <style> and stamps the mode's variables on the root; rendering
 *   relies on the one document-level `COMMON_CSS`.
 * - `exportSvg(svg, mode, w, h)` — for EXPORT: fully self-contained; bakes the mode's
 *   concrete colours into an internal <style> inside the clone, depending on NO external CSS.
 *
 * The monochrome `print` mode reproduces the canonical authoritative appearance. The canonical
 * item (`media[0].svg`) is never mutated — theming is a presentation layer only.
 */

import { readFileSync } from "node:fs";
import { fileURLToPath } from "node:url";

const theme = JSON.parse(readFileSync(fileURLToPath(new URL("./cartesian-theme.json", import.meta.url)), "utf8")) as {
  commonCss: string;
  modes: Record<string, Record<string, string>>;
};

export type Mode = "print" | "premium" | "premium-dark" | "accessible";
export const MODES: Mode[] = ["print", "premium", "premium-dark", "accessible"];
export const COMMON_CSS: string = theme.commonCss;
const VARS = theme.modes as Record<Mode, Record<string, string>>;

export function modeVars(mode: Mode): Record<string, string> {
  return VARS[mode];
}

/** Inline `style="--cx-…"` declaration string carrying this mode's variables for one root. */
export function modeVarStyle(mode: Mode): string {
  return Object.entries(VARS[mode]).map(([k, v]) => `${k}:${v}`).join(";");
}

/** The common ruleset with every `var(--cx-…)` resolved to this mode's concrete colour. */
export function resolveCommonCss(mode: Mode): string {
  return COMMON_CSS.replace(/var\((--cx-[a-z-]+)\)/g, (_m, name: string) => VARS[mode][name] ?? "#000");
}

const STYLE_RE = /<style>[\s\S]*?<\/style>/;

function stripCanonicalStyle(svg: string): string {
  return svg.replace(STYLE_RE, "");
}

function addRootAttrs(svg: string, attrs: string): string {
  return svg.replace(/^<svg /, `<svg ${attrs} `);
}

/** Presentation copy for in-document display (depends on one document-level COMMON_CSS). */
export function presentationSvg(svg: string, mode: Mode): string {
  return addRootAttrs(stripCanonicalStyle(svg), `class="cx-figure" style="${modeVarStyle(mode)}"`);
}

/** Self-contained export copy: the mode's concrete colours are baked inside the clone. */
export function exportSvg(svg: string, mode: Mode, width = 6000, height = 4200): string {
  const body = stripCanonicalStyle(svg);
  const withAttrs = addRootAttrs(body, `class="cx-figure" width="${width}" height="${height}"`);
  // Inject the resolved (concrete) common ruleset immediately after the opening <svg ...> tag.
  return withAttrs.replace(/(<svg[^>]*>)/, `$1<style>${resolveCommonCss(mode)}</style>`);
}

/** Background colour for a mode (used to fill the raster canvas before drawing the SVG). */
export function modeBackground(mode: Mode): string {
  return VARS[mode]["--cx-bg"] ?? "#ffffff";
}
