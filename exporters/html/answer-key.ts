/**
 * Answer-key export (standalone offline HTML).
 *
 * Compact list of canonical answers, one per question. Agrees with each item's
 * canonical answer by construction (it reads item.answer.display directly).
 */

import type { BankRecord } from "../../core/bank/types.ts";
import { htmlDoc, escapeHtml } from "./doc.ts";

export interface AnswerKeyOptions { title?: string; }

export function answerKey(records: BankRecord[], opts: AnswerKeyOptions = {}): string {
  const title = opts.title ?? "Answer key";
  const rows = records
    .map((r, i) => {
      const a = r.item["answer"] as { display: string; units?: string };
      const units = a.units ? ` ${escapeHtml(a.units)}` : "";
      return `<div class="exam-item"><span class="qnum">${i + 1}.</span> ${escapeHtml(a.display)}${units}</div>`;
    })
    .join("\n");
  return htmlDoc(title, "", `<h1>${escapeHtml(title)}</h1>${rows}`);
}
