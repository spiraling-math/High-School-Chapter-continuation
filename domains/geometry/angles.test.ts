/**
 * Geometry-angles generator tests (Node built-in test runner).
 * Byte-for-byte parity with the Python oracle (golden + 300-entry fixture incl. the
 * inline SVG), validator pass, reproducibility, and per-task behaviour.
 *
 * Run:  node --test domains/geometry/angles.test.ts
 */

import { test } from "node:test";
import assert from "node:assert/strict";
import { readFileSync } from "node:fs";
import { fileURLToPath } from "node:url";
import { generate, validate, serialize, solve, TASKS, MC_TASKS, type Config, type Params } from "./angles.ts";
import type { Json } from "../../core/serialization/canonical.ts";

const goldenPath = fileURLToPath(new URL("../../oracle/golden/geometry_angles.golden.json", import.meta.url));
const parityPath = fileURLToPath(new URL("../../oracle/golden/geometry_angles.parity.json", import.meta.url));

test("byte-for-byte parity with the oracle golden vectors (incl. inline SVG)", () => {
  const golden = JSON.parse(readFileSync(goldenPath, "utf8")) as Array<{ seed: number; serialized: string; validation: string }>;
  for (const gg of golden) {
    assert.equal(serialize(generate(gg.seed, { interactionType: "multiple-choice" })), gg.serialized, `golden seed ${gg.seed}`);
    assert.equal(validate(generate(gg.seed, { interactionType: "multiple-choice" })).status, "pass");
  }
});

test("byte-for-byte parity with the 300-entry oracle parity fixture", () => {
  const parity = JSON.parse(readFileSync(parityPath, "utf8")) as Array<{ seed: number; mode: string; serialized: string }>;
  assert.ok(parity.length >= 300);
  for (const p of parity) {
    const cfg: Config = { interactionType: p.mode as "free-response" | "multiple-choice" };
    assert.equal(serialize(generate(p.seed, cfg)), p.serialized, `${p.mode} seed ${p.seed}`);
  }
});

test("validator passes across a property sweep (both interaction types) and is reproducible", () => {
  for (let s = 1; s <= 400; s++) {
    for (const mode of ["free-response", "multiple-choice"] as const) {
      const item = generate(s, { interactionType: mode });
      assert.equal(validate(item).status, "pass", `seed ${s} ${mode}`);
      assert.equal(serialize(generate(s, { interactionType: mode })), serialize(item), `repro ${s} ${mode}`);
    }
  }
});

test("every task is exercised; explicit selection works", () => {
  const seen = new Set<string>();
  for (let s = 1; s <= 400; s++) seen.add((generate(s, { interactionType: "free-response" })["params"] as { task: string }).task);
  for (const t of TASKS) assert.ok(seen.has(t), `task ${t} appears`);
  for (const t of TASKS) {
    const mode = MC_TASKS.includes(t) ? "multiple-choice" : "free-response";
    const item = generate(7, { task: t, interactionType: mode as "multiple-choice" | "free-response" });
    assert.equal((item["params"] as { task: string }).task, t);
    assert.equal(validate(item).status, "pass");
  }
});

test("vertically_opposite_angle is free-response only", () => {
  assert.throws(() => generate(7, { task: "vertically_opposite_angle", interactionType: "multiple-choice" } as Config));
  const item = generate(7, { task: "vertically_opposite_angle", interactionType: "free-response" });
  assert.equal(item["options"], undefined);
});

test("every MC item has a figure, one correct option, and three distinct distractors", () => {
  for (let s = 1; s <= 200; s++) {
    const item = generate(s, { interactionType: "multiple-choice" });
    const media = item["media"] as Array<{ kind: string; svg: string }>;
    assert.equal(media[0]!.kind, "svg");
    assert.ok(media[0]!.svg.includes("NOT TO SCALE"));
    const options = item["options"] as Array<{ display: string; correct: boolean }>;
    assert.equal(options.length, 4);
    assert.equal(options.filter((o) => o.correct).length, 1);
    assert.equal(new Set(options.filter((o) => !o.correct).map((o) => o.display)).size, 3, `seed ${s}`);
  }
});

test("the unknown is labelled x, never its value (no diagram leakage)", () => {
  for (let s = 1; s <= 200; s++) {
    const item = generate(s, { interactionType: "multiple-choice" });
    const svg = (item["media"] as Array<{ svg: string }>)[0]!.svg;
    assert.ok(svg.includes(">x</text>"), `seed ${s} draws x`);
    const ans = (item["answer"] as { display: string }).display;
    // the answer label (e.g. "150°") must not be the unknown's rendered value
    assert.ok(!svg.includes(`>${ans}</text>`) || (item["params"] as { task: string }).task !== "x", "answer not drawn as unknown");
  }
});

test("validator catches a tampered answer", () => {
  const item = generate(3, { interactionType: "multiple-choice" }) as Record<string, Json>;
  (item["answer"] as { canonical: { num: number } }).canonical.num += 1;
  assert.equal(validate(item).status, "fail");
});

test("validator catches a tampered SVG (diagram-to-data)", () => {
  const item = generate(3, { interactionType: "free-response" }) as Record<string, Json>;
  (item["media"] as Array<{ svg: string }>)[0]!.svg += "<!--x-->";
  const v = validate(item);
  assert.equal(v.status, "fail");
  assert.ok(v.checks.some((c) => c.name === "svg-realises-data" && c.result === "fail"));
});

test("solve gives the integer-degree closure answers", () => {
  assert.equal(solve({ task: "triangle_missing_angle", A: 50, B: 60 } as unknown as Params), 70);
  assert.equal(solve({ task: "isosceles_base_angle", apex: 40 } as unknown as Params), 70);
  assert.equal(solve({ task: "vertically_opposite_angle", theta: 115 } as unknown as Params), 115);
});
