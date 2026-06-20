// Ambient declarations for the Generator Studio app.

// Injected at build time by scripts/build-studio.mjs via esbuild `define`.
// Contains the bundled KaTeX CSS (fonts inlined as data URIs) so that exported
// HTML can embed it with no external dependency.
declare const __KATEX_CSS__: string;

// KaTeX UMD global, provided by the inlined katex.min.js script in the built page.
interface KatexStatic {
  renderToString(tex: string, options?: Record<string, unknown>): string;
}
interface Window {
  katex: KatexStatic;
}
