/**
 * Build sample standalone exports for offline (file://) verification.
 *
 * Produces a worksheet, answer key, worked solutions, and a bank JSON file from
 * representative seeds. The worked-solutions export embeds the real inlined
 * KaTeX CSS, so it renders math offline with no external dependency.
 *
 * Run:  node scripts/build-samples.mjs
 * Output: apps/generator-studio/dist/samples/
 */

import katex from "katex";
import { writeFileSync, mkdirSync } from "node:fs";
import { join } from "node:path";
import { ROOT, inlineKatexCss } from "./katex-bundle.mjs";
import { generate } from "../domains/sequences/arithmetic.ts";
import { validate } from "../domains/sequences/validate.ts";
import { makeRecord } from "../core/bank/record.ts";
import { studentWorksheet } from "../exporters/html/worksheet.ts";
import { answerKey } from "../exporters/html/answer-key.ts";
import { workedSolutions } from "../exporters/html/solutions.ts";
import { exportBankJson } from "../exporters/json/bank-json.ts";

const OUT = join(ROOT, "apps", "generator-studio", "dist", "samples");
mkdirSync(OUT, { recursive: true });

const seeds = [1, 2, 3, 42, 7, 86];
const records = seeds.map((s, i) => {
  const mode = i % 2 === 0 ? "multiple-choice" : "integer";
  const item = generate(s, { answerType: mode });
  return makeRecord(item, validate(item).status, { mode, genConfig: { answerType: mode } });
});

const katexCss = inlineKatexCss();

writeFileSync(join(OUT, "worksheet.html"),
  studentWorksheet(records, { katex, title: "SPI-Math Worksheet", instructions: "Answer all questions. Show your working." }));
writeFileSync(join(OUT, "answer-key.html"), answerKey(records, { title: "SPI-Math Answer Key" }));
writeFileSync(join(OUT, "solutions.html"),
  workedSolutions(records, { katex, katexCss, title: "SPI-Math Worked Solutions" }));
writeFileSync(join(OUT, "bank.json"), exportBankJson(records));

console.log(`Samples written to ${OUT}`);
for (const f of ["worksheet.html", "answer-key.html", "solutions.html", "bank.json"]) console.log("  " + f);
