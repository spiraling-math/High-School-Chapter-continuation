/** Shared KaTeX asset bundling: inline CSS (woff2 fonts as data URIs) + JS text. */

import { readFileSync } from "node:fs";
import { dirname, join } from "node:path";
import { fileURLToPath } from "node:url";

export const ROOT = dirname(dirname(fileURLToPath(import.meta.url)));
const KATEX = join(ROOT, "node_modules", "katex", "dist");
const FONTS = join(KATEX, "fonts");

/** KaTeX CSS with every woff2 font inlined as a data URI; no relative paths remain. */
export function inlineKatexCss() {
  let css = readFileSync(join(KATEX, "katex.min.css"), "utf8");
  css = css.replace(/url\(fonts\/([\w-]+)\.woff2\)/g, (_m, name) => {
    const b64 = readFileSync(join(FONTS, `${name}.woff2`)).toString("base64");
    return `url(data:font/woff2;base64,${b64})`;
  });
  css = css.replace(/,url\(fonts\/[\w-]+\.woff\)\s*format\((["'])woff\1\)/g, "");
  css = css.replace(/,url\(fonts\/[\w-]+\.ttf\)\s*format\((["'])truetype\1\)/g, "");
  if (css.includes("fonts/")) throw new Error("KaTeX CSS still references a relative fonts/ path after inlining");
  return css;
}

export function katexJs() {
  return readFileSync(join(KATEX, "katex.min.js"), "utf8");
}
