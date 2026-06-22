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

test("reflex regions render the reflex arc (large-arc-flag=1, sweep=0)", () => {
  // angles_at_point seed 1 has a 263-degree UNKNOWN; the arc must be the reflex arc.
  const it = generate(1, { task: "angles_at_point_missing", interactionType: "multiple-choice" });
  assert.equal((it["answer"] as { canonical: { num: number } }).canonical.num, 263);
  assert.equal(validate(it).status, "pass");
  const svg = (it["media"] as Array<{ svg: string }>)[0]!.svg;
  const flags = [...svg.matchAll(/A 70 70 0 (\d) (\d)/g)].map((m) => `${m[1]}${m[2]}`);
  assert.ok(flags.includes("10"), `a reflex arc (large=1,sweep=0) is present: ${flags}`);
  assert.ok(flags.every((f) => f[1] === "0"), "every arc uses sweep=0");
});

test("validator (TS) catches a tampered large-arc flag and a tampered sweep", () => {
  const it = generate(1, { task: "angles_at_point_missing", interactionType: "free-response" }) as Record<string, Json>;
  const svg = (it["media"] as Array<{ svg: string }>)[0]!.svg;
  (it["media"] as Array<{ svg: string }>)[0]!.svg = svg.replace("A 70 70 0 1 0", "A 70 70 0 0 0");
  let names = validate(it).checks.filter((c) => c.result === "fail").map((c) => c.name);
  assert.ok(names.includes("arc-large-flag-correct") && names.includes("reflex-region-rendered-correctly"));
  const tri = generate(5, { task: "triangle_missing_angle", interactionType: "free-response" }) as Record<string, Json>;
  (tri["media"] as Array<{ svg: string }>)[0]!.svg = (tri["media"] as Array<{ svg: string }>)[0]!.svg.replace("A 70 70 0 0 0", "A 70 70 0 0 1");
  names = validate(tri).checks.filter((c) => c.result === "fail").map((c) => c.name);
  assert.ok(names.includes("arc-sweep-correct"));
});

test("vertically opposite uses a neutral leader, not a matching arc", () => {
  for (let s = 1; s <= 60; s++) {
    const it = generate(s, { task: "vertically_opposite_angle", interactionType: "free-response" });
    const svg = (it["media"] as Array<{ svg: string }>)[0]!.svg;
    assert.equal((svg.match(/<path class="ga"/g) ?? []).length, 1, "only the given angle has an arc");
    assert.equal((svg.match(/class="gt"/g) ?? []).length, 0, "no congruence ticks");
    assert.equal((svg.match(/class="gx"/g) ?? []).length, 1, "one neutral leader");
    const v = validate(it);
    assert.ok(v.checks.find((c) => c.name === "no-theorem-revealing-markers")?.result === "pass");
    assert.ok(v.checks.find((c) => c.name === "target-region-unambiguous")?.result === "pass");
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

test("no two rendered angle/vertex labels overlap (parsed from the SVG)", () => {
  const CHARW = (c: string): number => (c === "x" ? 16 : c === "°" ? 11 : 17);
  const box = (x: number, y: number, anc: string, t: string): [number, number, number, number] => {
    const w = [...t].reduce((a, c) => a + CHARW(c), 0);
    const left = anc === "middle" ? x - Math.floor(w / 2) : anc === "end" ? x - w : x;
    return [left, y - 22, left + w, y + 8];
  };
  const ov = (a: number[], b: number[]): boolean => !(a[2]! <= b[0]! || b[2]! <= a[0]! || a[3]! <= b[1]! || b[3]! <= a[1]!);
  const re = /<text([^>]*)>([^<]*)<\/text>/g;
  for (let s = 1; s <= 300; s++) {
    for (const mode of ["free-response", "multiple-choice"] as const) {
      const svg = (generate(s, { interactionType: mode })["media"] as Array<{ svg: string }>)[0]!.svg;
      const boxes: number[][] = [];
      let m: RegExpExecArray | null;
      re.lastIndex = 0;
      while ((m = re.exec(svg))) {
        const attrs = m[1]!, text = m[2]!;
        if (attrs.includes('class="gn"')) continue; // NOT TO SCALE
        const x = Number(/x="(-?\d+)"/.exec(attrs)![1]);
        const y = Number(/y="(-?\d+)"/.exec(attrs)![1]);
        const anc = /text-anchor="(\w+)"/.exec(attrs)?.[1] ?? "start";
        boxes.push(box(x, y, anc, text));
      }
      for (let i = 0; i < boxes.length; i++) for (let j = i + 1; j < boxes.length; j++) {
        assert.ok(!ov(boxes[i]!, boxes[j]!), `seed ${s} ${mode}: labels overlap`);
      }
    }
  }
});

test("solve gives the integer-degree closure answers", () => {
  assert.equal(solve({ task: "triangle_missing_angle", A: 50, B: 60 } as unknown as Params), 70);
  assert.equal(solve({ task: "isosceles_base_angle", apex: 40 } as unknown as Params), 70);
  assert.equal(solve({ task: "vertically_opposite_angle", theta: 115 } as unknown as Params), 115);
});
