/**
 * ADDITIVE shared presentation theme for gen.measurement.mensuration dimensioned figures (owner J).
 *
 * This module REUSES the approved coordinate-lines v1.0.2 visual contract
 * (`core/visual-style/cartesian-theme`) without modifying it — the same `cx-figure` root isolation,
 * the same per-root-variable + one-common-ruleset model, and the same presentationSvg()/exportSvg()
 * materialised-export contract. It FOLLOWS the `data-chart-theme` additive PATTERN (same mechanism)
 * but does NOT depend on it: presentation/export compose cartesian + mensuration rulesets only, so
 * none of the chart `--cx-bar*`/`--cx-symbol*` variables are pulled in. It ADDS mensuration
 * dimension-rendering primitives (shape, dimension/extension lines, arrowheads, right-angle +
 * perpendicular-height markers, measurement labels, the unknown-side marker, the NOT-TO-SCALE
 * banner, the decomposition cut line, and the answer-key result/overlay labels).
 *
 * Coordinate-lines and stats outputs are unaffected: this theme only adds variables + one ruleset
 * under the shared `cx-figure` root. The monochrome `print` mode is the colour-free authoritative
 * rendering; colour never carries meaning alone (the unknown side is the text "?", NOT-TO-SCALE is
 * text, the decomposition cut is dashed, dimension lines are offset with arrowheads).
 */

import { readFileSync } from "node:fs";
import { fileURLToPath } from "node:url";
import {
  COMMON_CSS as CART_COMMON_CSS,
  modeVars as cartModeVars,
  type Mode,
} from "./cartesian-theme.ts";

const theme = JSON.parse(
  readFileSync(fileURLToPath(new URL("./mensuration-theme.json", import.meta.url)), "utf8"),
) as { commonCss: string; modes: Record<string, Record<string, string>> };

export type { Mode };
export const MODES: Mode[] = ["print", "premium", "premium-dark", "accessible"];

/** The mensuration additive ruleset (dimension-rendering primitives only). */
export const MENSURATION_COMMON_CSS: string = theme.commonCss;
/** The full ruleset a host document needs for mensuration figures: cartesian shared + mensuration. */
export const COMMON_CSS: string = CART_COMMON_CSS + theme.commonCss;
const MENS_VARS = theme.modes as Record<Mode, Record<string, string>>;

/** The merged variable set for a mode: shared cartesian variables + mensuration variables. */
export function modeVars(mode: Mode): Record<string, string> {
  return { ...cartModeVars(mode), ...MENS_VARS[mode] };
}

/** Inline `style="--cx-…"` declaration carrying all of this mode's variables for one root. */
export function modeVarStyle(mode: Mode): string {
  return Object.entries(modeVars(mode)).map(([k, v]) => `${k}:${v}`).join(";");
}

/** The full common ruleset with every `var(--cx-…)` resolved to this mode's concrete colour. */
export function resolveCommonCss(mode: Mode): string {
  const vars = modeVars(mode);
  return COMMON_CSS.replace(/var\((--cx-[a-z-]+)\)/g, (_m, name: string) => vars[name] ?? "#000");
}

const STYLE_RE = /<style>[\s\S]*?<\/style>/;
const stripCanonicalStyle = (svg: string): string => svg.replace(STYLE_RE, "");
const addRootAttrs = (svg: string, attrs: string): string => svg.replace(/^<svg /, `<svg ${attrs} `);

/** Presentation copy for in-document display (relies on one document-level COMMON_CSS). */
export function presentationSvg(svg: string, mode: Mode): string {
  return addRootAttrs(stripCanonicalStyle(svg), `class="cx-figure" style="${modeVarStyle(mode)}"`);
}

/** Self-contained export copy: the mode's concrete colours are baked inside the clone (6000×4200). */
export function exportSvg(svg: string, mode: Mode, width = 6000, height = 4200): string {
  const body = stripCanonicalStyle(svg);
  const withAttrs = addRootAttrs(body, `class="cx-figure" width="${width}" height="${height}"`);
  return withAttrs.replace(/(<svg[^>]*>)/, `$1<style>${resolveCommonCss(mode)}</style>`);
}

/** Background colour for a mode (used to fill the raster canvas before drawing). */
export function modeBackground(mode: Mode): string {
  return modeVars(mode)["--cx-bg"] ?? "#ffffff";
}
