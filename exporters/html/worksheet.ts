/**
 * Student worksheet export (standalone offline HTML).
 *
 * Contains questions ONLY: stem, options (never marking the correct one), and
 * an answer space for free-response items. It must not reveal canonical answers,
 * distractor rationales, validation, or any other teacher metadata.
 */

import type { BankRecord } from "../../core/bank/types.ts";
import { displayItem } from "../../apps/generator-studio/wording.ts";
import { renderQuestionStudent, type KatexLike } from "../../apps/generator-studio/render/katex-render.ts";
import { htmlDoc, escapeHtml } from "./doc.ts";

export interface WorksheetOptions { katex: KatexLike; title?: string; instructions?: string; }

export function studentWorksheet(records: BankRecord[], opts: WorksheetOptions): string {
  const title = opts.title ?? "Worksheet";
  const items = records
    .map((r, i) => {
      const shown = displayItem(r.item, r.wording);
      const q = renderQuestionStudent(shown, opts.katex);
      const hasOptions = Boolean(shown["options"]);
      const space = hasOptions ? "" : `<div class="answer-space" aria-hidden="true"></div>`;
      return `<section class="exam-item"><span class="qnum">${i + 1}.</span>${q}${space}</section>`;
    })
    .join("\n");
  const body = `<h1>${escapeHtml(title)}</h1>` +
    (opts.instructions ? `<p class="subtitle">${escapeHtml(opts.instructions)}</p>` : "") +
    items;
  // Worksheets currently carry no display math, so KaTeX CSS is not embedded.
  return htmlDoc(title, "", body);
}
