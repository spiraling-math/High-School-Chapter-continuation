/**
 * Automated accessibility gates (axe-core + jsdom).
 *
 * Requires ZERO critical/serious axe violations across the app's surfaces and
 * exports. axe-core and jsdom are DEV/TEST-only dependencies — they are never
 * bundled into the offline app or its exports.
 *
 * Surfaces covered:
 *   - Generator Studio shell + question-bank table (the real app mounted in jsdom)
 *   - question preview view, worked-solution view, validation view (render fns)
 *   - student worksheet, answer-key, worked-solution exports (export HTML)
 *
 * Documented exception: jsdom performs no layout (and no canvas), so the
 * `color-contrast` rule cannot be evaluated here; it is disabled in these gates
 * and verified against the rendered app in the browser instead. No other
 * critical/serious rule is suppressed.
 *
 * Run:  node --test apps/generator-studio/a11y.test.ts
 */

import { test } from "node:test";
import assert from "node:assert/strict";
import { readFileSync } from "node:fs";
import { fileURLToPath } from "node:url";
import { JSDOM } from "jsdom";
import axeCore from "axe-core";
import katex from "katex";
import "fake-indexeddb/auto";
import { generate as genArith } from "../../domains/sequences/arithmetic.ts";
import { validate } from "../../domains/sequences/validate.ts";
import { makeRecord } from "../../core/bank/record.ts";
import { renderQuestionTeacher, renderSolution, renderValidation, type KatexLike } from "./render/katex-render.ts";
import { studentWorksheet } from "../../exporters/html/worksheet.ts";
import { answerKey } from "../../exporters/html/answer-key.ts";
import { workedSolutions } from "../../exporters/html/solutions.ts";

const axeSource = (axeCore as unknown as { source: string }).source;
const kx = katex as unknown as KatexLike;
const SERIOUS = new Set(["critical", "serious"]);
// color-contrast needs layout/canvas, which jsdom lacks; verified in-browser instead.
const AXE_OPTS = { resultTypes: ["violations"], rules: { "color-contrast": { enabled: false } } };

interface AxeNode { target: string[] }
interface AxeViolation { id: string; impact: string; nodes: AxeNode[] }
interface AxeResult { violations: AxeViolation[] }
interface AxeWindow { axe: { run(ctx: unknown, opts?: unknown): Promise<AxeResult> }; eval(s: string): void }

function summarize(res: AxeResult): Array<{ id: string; impact: string; targets: string[] }> {
  return res.violations
    .filter((v) => SERIOUS.has(v.impact))
    .map((v) => ({ id: v.id, impact: v.impact, targets: v.nodes.flatMap((n) => n.target) }));
}

/** Run axe inside a jsdom built from a static HTML string. */
async function seriousViolations(html: string): Promise<Array<{ id: string; impact: string; targets: string[] }>> {
  const dom = new JSDOM(html, { runScripts: "dangerously", pretendToBeVisual: true });
  const w = dom.window as unknown as AxeWindow;
  w.eval(axeSource);
  return summarize(await w.axe.run((dom.window as unknown as { document: unknown }).document, AXE_OPTS));
}

function noViolations(v: Array<{ id: string; impact: string; targets: string[] }>): void {
  assert.equal(v.length, 0, `critical/serious axe violations: ${JSON.stringify(v)}`);
}

function page(title: string, body: string): string {
  return `<!doctype html><html lang="en"><head><meta charset="utf-8"><title>${title}</title></head>` +
    `<body><main><h1>${title}</h1>${body}</main></body></html>`;
}

const item = genArith(123, { answerType: "multiple-choice" });
const rec = makeRecord(item, validate(item).status, { mode: "multiple-choice", genConfig: { answerType: "multiple-choice" } });

// --- WCAG contrast guard (the color-contrast rule cannot run in jsdom) --------- //
function relLum(hex: string): number {
  const m = hex.replace("#", "");
  const chan = [0, 2, 4]
    .map((i) => parseInt(m.slice(i, i + 2), 16) / 255)
    .map((c) => (c <= 0.03928 ? c / 12.92 : Math.pow((c + 0.055) / 1.055, 2.4)));
  return 0.2126 * chan[0]! + 0.7152 * chan[1]! + 0.0722 * chan[2]!;
}
function contrast(a: string, b: string): number {
  const la = relLum(a), lb = relLum(b);
  return (Math.max(la, lb) + 0.05) / (Math.min(la, lb) + 0.05);
}

test("a11y: text colour tokens meet WCAG AA (>= 4.5:1) on the paper background", () => {
  const css = readFileSync(fileURLToPath(new URL("./styles.css", import.meta.url)), "utf8");
  const token = (name: string): string => {
    const m = new RegExp(`--${name}:\\s*(#[0-9a-fA-F]{6})`).exec(css);
    assert.ok(m, `token --${name} present`);
    return m![1]!;
  };
  const paper = token("paper");
  for (const t of ["ink", "ink-soft", "ink-faint"]) {
    const ratio = contrast(token(t), paper);
    assert.ok(ratio >= 4.5, `--${t} (${token(t)}) on --paper is ${ratio.toFixed(2)}:1, need >= 4.5:1`);
  }
});

test("a11y: question preview view — no critical/serious violations", async () => {
  noViolations(await seriousViolations(page("Question preview", renderQuestionTeacher(item, kx))));
});

test("a11y: worked-solution view — no critical/serious violations", async () => {
  noViolations(await seriousViolations(page("Worked solution", renderSolution(item, kx))));
});

test("a11y: validation view — no critical/serious violations", async () => {
  noViolations(await seriousViolations(page("Validation", renderValidation(validate(item)))));
});

test("a11y: student worksheet export — no critical/serious violations", async () => {
  noViolations(await seriousViolations(studentWorksheet([rec], { katex: kx, title: "Worksheet" })));
});

test("a11y: answer-key export — no critical/serious violations", async () => {
  noViolations(await seriousViolations(answerKey([rec], { title: "Answer key" })));
});

test("a11y: worked-solution export — no critical/serious violations", async () => {
  noViolations(await seriousViolations(workedSolutions([rec], { katex: kx, katexCss: "", title: "Solutions" })));
});

test("a11y: Generator Studio shell + question-bank table — no critical/serious violations", async () => {
  const dom = new JSDOM(
    `<!doctype html><html lang="en"><head><meta charset="utf-8"><title>SPI-Math Generator Studio</title></head>` +
    `<body><div id="app"></div></body></html>`,
    { runScripts: "dangerously", pretendToBeVisual: true, url: "http://localhost/" },
  );
  const w = dom.window as unknown as AxeWindow & { katex: KatexLike; document: { getElementById(id: string): { click(): void } | null; querySelector(s: string): unknown } };
  const g = globalThis as unknown as Record<string, unknown>;
  const wany = dom.window as unknown as Record<string, unknown>;
  const prev = { window: g["window"], document: g["document"], Option: g["Option"] };
  g["window"] = dom.window;
  g["document"] = dom.window.document;
  g["Option"] = wany["Option"]; // app builds <option>s with `new Option(...)`
  w.katex = kx;
  try {
    const { mountStudio } = await import("./main.ts");
    mountStudio(); // generates an initial item synchronously
    w.document.getElementById("save")?.click(); // populate the bank table (store.put validates the item)
    await new Promise((r) => setTimeout(r, 250)); // let the async put + bank re-render settle
    w.eval(axeSource);
    noViolations(summarize(await w.axe.run(dom.window.document, AXE_OPTS)));
    assert.ok(w.document.querySelector('[aria-label="Saved items"]'), "bank table rendered");
  } finally {
    g["window"] = prev.window;
    g["document"] = prev.document;
    g["Option"] = prev.Option;
  }
});
