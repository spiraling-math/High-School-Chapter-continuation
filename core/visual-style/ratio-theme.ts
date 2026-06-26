/**
 * Presentation theme for gen.proportion.ratio (owner J/#5). A NEW additive theme — it does NOT
 * extend or mutate any shared theme.
 *
 * Render modes are sets of CSS custom properties applied to each figure's OWN root SVG
 * (`class="rt-figure"`). One immutable common ruleset (`COMMON_CSS`) reads those variables. Because
 * custom properties cascade only into their own subtree, every figure is isolated — multiple modes on
 * one page, reordered cards, several questions per worksheet, and SVGs from other families never
 * interfere. The GIVEN/UNKNOWN distinction is carried by SHAPE, DASH and FILL (solid-filled solid-edge
 * given segments vs hatched/dashed unknown segments with a '?' marker; solid given points vs dashed
 * open unknown points) inside `COMMON_CSS`, so it survives in EVERY mode and is never colour-only.
 *
 * The canonical ratio SVG keeps its own monochrome <style> (the authoritative `print` appearance) and
 * is NEVER mutated — theming is a presentation layer only.
 *
 * - `presentationSvg(svg, mode, cardSuffix)` — IN-DOCUMENT display: strips the canonical <style>, stamps
 *   the mode's variables on the root, and namespaces every inline id by `cardSuffix` so the same item's
 *   key SVG rendered across several mode cards never collides.
 * - `exportSvg(svg, mode, w, h, cardSuffix)` — EXPORT: fully self-contained; bakes the mode's concrete
 *   colours into an internal <style> inside the clone and namespaces ids.
 */

import { readFileSync } from "node:fs";
import { fileURLToPath } from "node:url";

const theme = JSON.parse(readFileSync(fileURLToPath(new URL("./ratio-theme.json", import.meta.url)), "utf8")) as {
  id: string;
  commonCss: string;
  modes: Record<string, Record<string, string>>;
};

export type Mode = "print" | "premium" | "premium-dark" | "accessible";
export const MODES: Mode[] = ["print", "premium", "premium-dark", "accessible"];
export const THEME_ID: string = theme.id;
export const COMMON_CSS: string = theme.commonCss;
const VARS = theme.modes as Record<Mode, Record<string, string>>;

export function modeVars(mode: Mode): Record<string, string> {
  return VARS[mode];
}

/** Inline `style="--rt-…"` declaration string carrying this mode's variables for one root. */
export function modeVarStyle(mode: Mode): string {
  return Object.entries(VARS[mode]).map(([k, v]) => `${k}:${v}`).join(";");
}

/** The common ruleset with every `var(--rt-…)` resolved to this mode's concrete colour. */
export function resolveCommonCss(mode: Mode): string {
  return COMMON_CSS.replace(/var\((--rt-[a-z-]+)\)/g, (_m, name: string) => VARS[mode][name] ?? "#000");
}

/** Background colour for a mode (used to fill the raster canvas before drawing the SVG). */
export function modeBackground(mode: Mode): string {
  return VARS[mode]["--rt-bg"] ?? "#ffffff";
}

const STYLE_RE = /<style>[\s\S]*?<\/style>/;

function stripCanonicalStyle(svg: string): string {
  return svg.replace(STYLE_RE, "");
}

function addRootAttrs(svg: string, attrs: string): string {
  return svg.replace(/^<svg /, `<svg ${attrs} `);
}

/** Namespace every inline id (and its url(#…) references) by a per-card suffix so the same SVG can be
 *  embedded many times in one document without DOM id collisions. */
export function namespaceIds(svg: string, cardSuffix: string): string {
  if (!cardSuffix) return svg;
  return svg
    .replace(/id="([^"]+)"/g, (_m, id: string) => `id="${id}--${cardSuffix}"`)
    .replace(/url\(#([^)]+)\)/g, (_m, id: string) => `url(#${id}--${cardSuffix})`);
}

/** Presentation copy for in-document display (depends on one document-level COMMON_CSS). */
export function presentationSvg(svg: string, mode: Mode, cardSuffix = ""): string {
  const themed = addRootAttrs(stripCanonicalStyle(svg), `class="rt-figure" style="${modeVarStyle(mode)}"`);
  return namespaceIds(themed, cardSuffix);
}

/** Self-contained export copy: the mode's concrete colours are baked inside the clone. */
export function exportSvg(svg: string, mode: Mode, width = 6000, height = 1800, cardSuffix = ""): string {
  const body = stripCanonicalStyle(svg);
  const withAttrs = addRootAttrs(body, `class="rt-figure" width="${width}" height="${height}"`);
  const baked = withAttrs.replace(/(<svg[^>]*>)/, `$1<style>${resolveCommonCss(mode)}</style>`);
  return namespaceIds(baked, cardSuffix);
}
