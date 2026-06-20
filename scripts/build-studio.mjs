/**
 * Build the SPI-Math Generator Studio into a single self-contained offline HTML.
 *
 * - Inlines KaTeX CSS with all woff2 fonts as data URIs (no fonts/ folder dep).
 * - Inlines katex.min.js (UMD global) — used for live rendering.
 * - Bundles the TypeScript app with esbuild (IIFE), injecting the bundled KaTeX
 *   CSS via the __KATEX_CSS__ define so runtime HTML exports can embed it.
 * - Composes apps/generator-studio/dist/index.html and asserts it has NO
 *   external resource references (works from file://, offline).
 *
 * Run:  node scripts/build-studio.mjs
 */

import * as esbuild from "esbuild";
import { readFileSync, writeFileSync, mkdirSync } from "node:fs";
import { dirname, join } from "node:path";
import { fileURLToPath } from "node:url";

const ROOT = dirname(dirname(fileURLToPath(import.meta.url)));
const APP = join(ROOT, "apps", "generator-studio");
const KATEX = join(ROOT, "node_modules", "katex", "dist");
const FONTS = join(KATEX, "fonts");

function inlineKatexCss() {
  let css = readFileSync(join(KATEX, "katex.min.css"), "utf8");
  // Replace each woff2 reference with a base64 data URI.
  css = css.replace(/url\(fonts\/([\w-]+)\.woff2\)/g, (_m, name) => {
    const b64 = readFileSync(join(FONTS, `${name}.woff2`)).toString("base64");
    return `url(data:font/woff2;base64,${b64})`;
  });
  // Drop the woff/ttf fallbacks so no relative fonts/ paths remain.
  css = css.replace(/,url\(fonts\/[\w-]+\.woff\)\s*format\((["'])woff\1\)/g, "");
  css = css.replace(/,url\(fonts\/[\w-]+\.ttf\)\s*format\((["'])truetype\1\)/g, "");
  if (css.includes("fonts/")) {
    throw new Error("KaTeX CSS still references a relative fonts/ path after inlining");
  }
  return css;
}

const katexCss = inlineKatexCss();
const katexJs = readFileSync(join(KATEX, "katex.min.js"), "utf8");
const appCss = readFileSync(join(APP, "styles.css"), "utf8");

const result = await esbuild.build({
  entryPoints: [join(APP, "main.ts")],
  bundle: true,
  format: "iife",
  platform: "browser",
  target: "es2022",
  minify: true,
  legalComments: "none",
  write: false,
  define: { __KATEX_CSS__: JSON.stringify(katexCss) },
});
const appJs = result.outputFiles[0].text;

const html = `<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<meta name="color-scheme" content="light">
<title>SPI-Math Generator Studio</title>
<style>${katexCss}</style>
<style>${appCss}</style>
</head>
<body>
<a href="#main" class="skip-link">Skip to content</a>
<div id="app"></div>
<script>${katexJs}</script>
<script>${appJs}</script>
</body>
</html>`;

// Assert no external resource *loads* (offline / file:// safety). We match only
// genuine network references (src=/href=/url()/@import pointing at http(s):// or
// protocol-relative //), not harmless strings such as the MathML namespace URI
// inside KaTeX or regex literals inside the bundled app code.
const EXTERNAL = [
  /<link\b[^>]*\bhref\s*=\s*["']?(?:https?:)?\/\//i,
  /\bsrc\s*=\s*["']?(?:https?:)?\/\//i,
  /url\(\s*["']?(?:https?:)?\/\//i,
  /@import\s+(?:url\()?\s*["']?(?:https?:)?\/\//i,
];
for (const pattern of EXTERNAL) {
  if (pattern.test(html)) throw new Error(`Built HTML contains an external load matching ${pattern}`);
}

const distDir = join(APP, "dist");
mkdirSync(distDir, { recursive: true });
const outPath = join(distDir, "index.html");
writeFileSync(outPath, html, "utf8");

const kb = (s) => `${Math.round(s / 1024)} KB`;
console.log("Built:", outPath);
console.log(`  app bundle : ${kb(appJs.length)}`);
console.log(`  katex css  : ${kb(katexCss.length)} (fonts inlined)`);
console.log(`  katex js   : ${kb(katexJs.length)}`);
console.log(`  total html : ${kb(html.length)}`);
console.log("  external references: none");
