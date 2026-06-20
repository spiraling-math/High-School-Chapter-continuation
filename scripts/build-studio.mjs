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
import { join } from "node:path";
import { ROOT, inlineKatexCss, katexJs as readKatexJs } from "./katex-bundle.mjs";

const APP = join(ROOT, "apps", "generator-studio");

const katexCss = inlineKatexCss();
const katexJs = readKatexJs();
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
