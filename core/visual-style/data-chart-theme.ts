/**
 * ADDITIVE shared presentation theme for gen.stats.data-handling figures (decision K).
 *
 * This module REUSES the approved coordinate-lines v1.0.2 visual contract
 * (`core/visual-style/cartesian-theme`) without modifying it: the same `cx-figure` root
 * isolation, the same shared axis/tick/grid/line/point/text CSS custom properties, and the
 * same per-root-variable + one-common-ruleset isolation that makes several modes / families
 * coexist on one page. It ADDS statistics primitives (chart bars, pictogram symbols,
 * category labels, axis-title labels, key labels) as new `--cx-*` variables plus one
 * additive common ruleset.
 *
 * Because the data-chart variables and ruleset are ADDITIVE and share the same `cx-figure`
 * root + `--cx-*` namespace, a stats figure and a coordinate-lines figure render correctly
 * on the same page with no interference. The monochrome `print` mode is the colour-free
 * authoritative rendering; colour never carries meaning alone (every category/series is also
 * labelled on the axis).
 *
 * `presentationSvg(svg, mode)` / `exportSvg(svg, mode, w, h)` extend the cartesian behaviour:
 * presentation relies on BOTH document-level common rulesets (cartesian + data-chart);
 * export bakes BOTH resolved rulesets inside the clone (self-contained 6000×4200 default).
 */

import { readFileSync } from "node:fs";
import { fileURLToPath } from "node:url";
import {
  COMMON_CSS as CART_COMMON_CSS,
  modeVars as cartModeVars,
  type Mode,
} from "./cartesian-theme.ts";

const theme = JSON.parse(
  readFileSync(fileURLToPath(new URL("./data-chart-theme.json", import.meta.url)), "utf8"),
) as { commonCss: string; modes: Record<string, Record<string, string>> };

export type { Mode };
export const MODES: Mode[] = ["print", "premium", "premium-dark", "accessible"];

/** The data-chart additive ruleset (statistics primitives only). */
export const DATA_CHART_COMMON_CSS: string = theme.commonCss;
/** The full ruleset a host document needs for stats figures: cartesian shared + data-chart. */
export const COMMON_CSS: string = CART_COMMON_CSS + theme.commonCss;
const DC_VARS = theme.modes as Record<Mode, Record<string, string>>;

/** The merged variable set for a mode: shared cartesian variables + data-chart variables. */
export function modeVars(mode: Mode): Record<string, string> {
  return { ...cartModeVars(mode), ...DC_VARS[mode] };
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

/** Self-contained export copy: the mode's concrete colours are baked inside the clone. */
export function exportSvg(svg: string, mode: Mode, width = 6000, height = 4200): string {
  const body = stripCanonicalStyle(svg);
  const withAttrs = addRootAttrs(body, `class="cx-figure" width="${width}" height="${height}"`);
  return withAttrs.replace(/(<svg[^>]*>)/, `$1<style>${resolveCommonCss(mode)}</style>`);
}

/** Background colour for a mode (used to fill the raster canvas before drawing). */
export function modeBackground(mode: Mode): string {
  return modeVars(mode)["--cx-bg"] ?? "#ffffff";
}
