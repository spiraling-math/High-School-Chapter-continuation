/**
 * Shared standalone-HTML document wrapper for exports.
 *
 * Every export is a single self-contained HTML document with NO external
 * references — it opens directly from file:// and works offline. The wrapper
 * asserts this invariant at build time so a regression cannot ship a CDN or
 * network dependency. No <script> is ever emitted (exports are static).
 */

export function escapeHtml(s: string): string {
  return s
    .replace(/&/g, "&amp;").replace(/</g, "&lt;").replace(/>/g, "&gt;")
    .replace(/"/g, "&quot;").replace(/'/g, "&#39;");
}

/** Minimal, self-contained document styling (independent of the app stylesheet). */
export const DOC_CSS = `
:root{--ink:#11203f;--soft:#44516e;--line:#d8e0f0;--navy:#0a1573;}
*{box-sizing:border-box}
body{margin:0;font-family:"Inter",system-ui,-apple-system,"Segoe UI",Roboto,sans-serif;color:var(--ink);background:#fff;line-height:1.55}
.doc{max-width:820px;margin:0 auto;padding:28px}
h1{font-size:22px;margin:0 0 4px}
.subtitle{color:var(--soft);font-size:13px;margin:0 0 18px}
.exam-item{padding:12px 0;border-bottom:1px solid var(--line);break-inside:avoid;page-break-inside:avoid}
.qnum{font-weight:700;color:var(--navy);margin-right:8px}
.stem p{margin:.3em 0}
.options{list-style:none;padding:0;margin:10px 0 0;display:grid;gap:6px}
.options li{display:flex;gap:10px;padding:6px 10px;border:1px solid var(--line);border-radius:8px}
.options .label{font-weight:700;color:var(--navy)}
.answer-space{height:52px;border-bottom:1px dotted var(--soft);margin-top:8px}
.sol-step{padding:6px 0;border-bottom:1px dashed var(--line)}
.sol-step .n{font-weight:700;color:#0792a8;margin-right:6px}
h3{font-size:14px;margin:10px 0 4px;color:var(--soft);text-transform:uppercase;letter-spacing:.05em}
@media print{.exam-item{break-inside:avoid}body{font-size:12pt}}
`;

const EXTERNAL_PATTERNS = [/<link\b/i, /<script\b/i, /\bsrc\s*=\s*["']https?:/i, /url\(\s*["']?https?:/i, /@import/i];

export function assertNoExternalRefs(html: string): void {
  for (const p of EXTERNAL_PATTERNS) {
    if (p.test(html)) throw new Error(`Export contains a forbidden external/script reference matching ${p}`);
  }
}

export function htmlDoc(title: string, headCss: string, bodyHtml: string): string {
  const html = `<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>${escapeHtml(title)}</title>
<style>${DOC_CSS}</style>
${headCss ? `<style>${headCss}</style>` : ""}
</head>
<body>
<main class="doc">
${bodyHtml}
</main>
</body>
</html>`;
  assertNoExternalRefs(html);
  return html;
}
