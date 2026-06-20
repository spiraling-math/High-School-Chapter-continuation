/**
 * Worked-solutions export (standalone offline HTML).
 *
 * Question, full structured worked solution (math rendered with KaTeX), and the
 * canonical answer. Embeds the bundled KaTeX CSS (fonts inlined) so it renders
 * offline from file:// with no external dependency.
 */

import type { BankRecord } from "../../core/bank/types.ts";
import { displayItem } from "../../apps/generator-studio/wording.ts";
import { renderQuestionStudent, renderSolution, type KatexLike } from "../../apps/generator-studio/render/katex-render.ts";
import { htmlDoc, escapeHtml } from "./doc.ts";

export interface SolutionsOptions { katex: KatexLike; katexCss: string; title?: string; }

export function workedSolutions(records: BankRecord[], opts: SolutionsOptions): string {
  const title = opts.title ?? "Worked solutions";
  const items = records
    .map((r, i) => {
      const shown = displayItem(r.item, r.wording);
      const q = renderQuestionStudent(shown, opts.katex);
      const sol = renderSolution(r.item, opts.katex);
      const a = r.item["answer"] as { display: string };
      return `<section class="exam-item"><span class="qnum">${i + 1}.</span>${q}` +
        `<h3>Solution</h3>${sol}` +
        `<p><strong>Answer:</strong> ${escapeHtml(a.display)}</p></section>`;
    })
    .join("\n");
  return htmlDoc(title, opts.katexCss, `<h1>${escapeHtml(title)}</h1>${items}`);
}
