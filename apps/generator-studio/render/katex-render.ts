/**
 * Item rendering to accessible HTML strings.
 *
 * Math is rendered with KaTeX to HTML+MathML (the MathML gives screen readers
 * accessible notation). The KaTeX instance is INJECTED so the same renderers
 * run in the browser (window.katex) and in Node tests (import katex from
 * "katex"). No DOM is required to produce the HTML strings.
 */

import type { Json } from "../../../core/serialization/canonical.ts";

export interface KatexLike { renderToString(tex: string, options?: Record<string, unknown>): string; }

export function escapeHtml(s: string): string {
  return s
    .replace(/&/g, "&amp;").replace(/</g, "&lt;").replace(/>/g, "&gt;")
    .replace(/"/g, "&quot;").replace(/'/g, "&#39;");
}

export function mathHtml(latex: string, katex: KatexLike, display = false): string {
  return katex.renderToString(latex, {
    displayMode: display,
    throwOnError: false,
    output: "htmlAndMathml",
  });
}

type Block = { kind: string; text?: string; latex?: string };

function renderBlocks(item: Record<string, Json>, katex: KatexLike): string {
  const prompt = item["prompt"] as { instruction?: string; blocks: Block[] };
  return prompt.blocks
    .map((b) => {
      if (b.kind === "math" || b.kind === "math-inline") {
        return `<p>${mathHtml(b.latex ?? "", katex, b.kind === "math")}</p>`;
      }
      return `<p>${escapeHtml(b.text ?? "")}</p>`;
    })
    .join("");
}

/** Student-facing question: stem + options, NEVER marking the correct option. */
export function renderQuestionStudent(item: Record<string, Json>, katex: KatexLike): string {
  let html = `<div class="stem">${renderBlocks(item, katex)}</div>`;
  const options = item["options"] as Array<{ label: string; display: string }> | undefined;
  if (options) {
    html += `<ul class="options" role="list">`;
    for (const o of options) {
      html += `<li><span class="label">${escapeHtml(o.label)}</span><span>${escapeHtml(o.display)}</span></li>`;
    }
    html += `</ul>`;
  }
  return html;
}

/** Teacher/preview question: like student, but marks the correct option (non-color: text + icon). */
export function renderQuestionTeacher(item: Record<string, Json>, katex: KatexLike): string {
  let html = `<div class="stem">${renderBlocks(item, katex)}</div>`;
  const options = item["options"] as Array<{ label: string; display: string; correct: boolean }> | undefined;
  if (options) {
    html += `<ul class="options" role="list">`;
    for (const o of options) {
      html += `<li class="${o.correct ? "correct" : ""}"><span class="label">${escapeHtml(o.label)}</span><span>${escapeHtml(o.display)}</span></li>`;
    }
    html += `</ul>`;
  }
  return html;
}

export function renderAnswer(item: Record<string, Json>): string {
  const a = item["answer"] as { display: string; units?: string };
  const units = a.units ? ` ${escapeHtml(a.units)}` : "";
  return `<div class="answer-box">${escapeHtml(a.display)}${units}</div>`;
}

export function renderSolution(item: Record<string, Json>, katex: KatexLike): string {
  const sol = item["solution"] as { steps: Array<{ number: number; transformation?: string; explanation?: string; ruleOrTheorem?: string; intermediateResult?: string }> };
  return sol.steps
    .map((s) => {
      const bits: string[] = [];
      if (s.ruleOrTheorem) bits.push(mathHtml(s.ruleOrTheorem, katex, false));
      if (s.intermediateResult) bits.push(mathHtml(s.intermediateResult, katex, true));
      const why = s.explanation ? `<span class="why"> — ${escapeHtml(s.explanation)}</span>` : "";
      return `<div class="sol-step"><span class="n">${s.number}.</span><span>${escapeHtml(s.transformation ?? "")}</span>${why}<div>${bits.join(" ")}</div></div>`;
    })
    .join("");
}

export function renderValidation(result: { status: string; checks: Array<{ name: string; result: string; detail: string }> }): string {
  const items = result.checks
    .map((c) => {
      const ok = c.result === "pass";
      const icon = ok ? "✓" : "✗";
      const cls = ok ? "pass" : "fail";
      return `<li><span class="${cls}" aria-hidden="true">${icon}</span><span class="${cls}">${ok ? "PASS" : "FAIL"}</span><span class="name">${escapeHtml(c.name)}</span><span class="detail">${escapeHtml(c.detail)}</span></li>`;
    })
    .join("");
  return `<p>Overall: <strong class="${result.status === "pass" ? "pass" : "fail"}">${escapeHtml(result.status.toUpperCase())}</strong></p><ul class="checks" role="list">${items}</ul>`;
}
