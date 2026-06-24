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
import * as geometric from "../domains/sequences/geometric.ts";
import * as linear from "../domains/algebra/linear-equations.ts";
import * as geometryAngles from "../domains/geometry/angles.ts";
import * as coordinateLines from "../domains/geometry/coordinate-lines.ts";
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
// Include geometric items (exact-rational answers, all five tasks).
for (const [task, mode] of [["nth_term", "multiple-choice"], ["sum_n", "integer"], ["find_r", "integer"], ["find_n_for_value", "integer"], ["sum_infinite", "integer"]]) {
  const item = geometric.generate(7, { task, answerType: mode });
  records.push(makeRecord(item, geometric.validate(item).status, { mode, genConfig: { answerType: mode, task } }));
}
// Include linear-equations items (all five tasks; integer + exact-rational answers).
for (const [task, mode] of [["one_step_add", "multiple-choice"], ["one_step_mul", "integer"], ["two_step", "multiple-choice"], ["both_sides", "integer"], ["brackets", "multiple-choice"]]) {
  const item = linear.generate(11, { task, answerType: mode });
  records.push(makeRecord(item, linear.validate(item).status, { mode, genConfig: { answerType: mode, task } }));
}
// Include geometry (angles, SVG diagrams) — curriculum-approved at v1.2.3
// (DECISION_LOG.md #40), so it is part of production exports/samples. VO is free-response
// only; the others are multiple-choice. See core/sdk/sequence-registry.ts (approvalStatus).
for (const [task, mode] of [["straight_line_missing_angle", "multiple-choice"], ["triangle_missing_angle", "multiple-choice"], ["isosceles_base_angle", "multiple-choice"], ["vertically_opposite_angle", "free-response"], ["angles_at_point_missing", "multiple-choice"]]) {
  const item = geometryAngles.generate(13, { task, interactionType: mode });
  records.push(makeRecord(item, geometryAngles.validate(item).status, { mode, genConfig: { interactionType: mode, task } }));
}
// Include coordinate geometry & straight-line graphs — curriculum-approved at v1.0.2
// (DECISION_LOG.md #44). plot_point is free-response only; the others are multiple-choice.
for (const [task, mode] of [["read_point", "multiple-choice"], ["plot_point", "free-response"], ["gradient_two_points", "multiple-choice"], ["midpoint", "multiple-choice"], ["interpret_mx_c", "multiple-choice"], ["equation_from_graph", "multiple-choice"], ["equation_from_two_points", "multiple-choice"]]) {
  const item = coordinateLines.generate(13, { task, interactionType: mode });
  records.push(makeRecord(item, coordinateLines.validate(item).status, { mode, genConfig: { interactionType: mode, task } }));
}

const katexCss = inlineKatexCss();

writeFileSync(join(OUT, "worksheet.html"),
  studentWorksheet(records, { katex, title: "SPI-Math Worksheet", instructions: "Answer all questions. Show your working." }));
writeFileSync(join(OUT, "answer-key.html"), answerKey(records, { title: "SPI-Math Answer Key" }));
writeFileSync(join(OUT, "solutions.html"),
  workedSolutions(records, { katex, katexCss, title: "SPI-Math Worked Solutions" }));
writeFileSync(join(OUT, "bank.json"), exportBankJson(records));

console.log(`Samples written to ${OUT}`);
for (const f of ["worksheet.html", "answer-key.html", "solutions.html", "bank.json"]) console.log("  " + f);
