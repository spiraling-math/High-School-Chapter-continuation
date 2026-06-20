/**
 * Geometric-sequences generator tests (Node built-in test runner).
 * Decisive test: byte-for-byte parity with the Python oracle's golden + parity
 * fixtures. Run:  node --test domains/sequences/geometric.test.ts
 */

import { test } from "node:test";
import assert from "node:assert/strict";
import { readFileSync } from "node:fs";
import { fileURLToPath } from "node:url";
import { dirname, join } from "node:path";
import { generate, serialize, solve, ALL_TASKS, type Params } from "./geometric.ts";
import { MISCONCEPTIONS } from "./geometric-misconceptions.ts";
import { Rational } from "../../core/exact-math/rational.ts";

const here = dirname(fileURLToPath(import.meta.url));
const golden = JSON.parse(readFileSync(join(here, "../../oracle/golden/geometric_sequences.golden.json"), "utf8")) as Array<{ seed: number; serialized: string }>;
const parity = JSON.parse(readFileSync(join(here, "../../oracle/golden/geometric_sequences.parity.json"), "utf8")) as Array<{ seed: number; mode: "integer" | "multiple-choice"; serialized: string }>;

function P(task: string, u1: number, rnum: number, rden: number, extra: Record<string, number> = {}): Params {
  return { task: task as Params["task"], u1, r: { num: rnum, den: rden }, ...extra };
}

test("byte-for-byte parity with the oracle golden vectors", () => {
  for (const g of golden) assert.equal(serialize(generate(g.seed, { answerType: "multiple-choice" })), g.serialized, `seed ${g.seed}`);
});

test(`byte-for-byte parity across ${parity.length} oracle fixture entries`, () => {
  let mismatches = 0, first = "";
  for (const f of parity) {
    const got = serialize(generate(f.seed, { answerType: f.mode }));
    if (got !== f.serialized) { mismatches++; if (!first) first = `seed ${f.seed} (${f.mode})\n got:${got}\n exp:${f.serialized}`; }
  }
  assert.equal(mismatches, 0, `${mismatches} mismatch(es). First:\n${first}`);
});

test("known exact values", () => {
  assert.ok((solve(P("nth_term", 2, 3, 1, { n: 4 })) as Rational).equals(new Rational(54)));
  assert.ok((solve(P("nth_term", 9, -2, 3, { n: 3 })) as Rational).equals(new Rational(4)));
  assert.ok((solve(P("sum_n", 1, 2, 1, { n: 4 })) as Rational).equals(new Rational(15)));
  assert.ok((solve(P("sum_infinite", 6, 1, 2)) as Rational).equals(new Rational(12)));
  assert.ok((solve(P("sum_infinite", 5, 1, 3)) as Rational).equals(new Rational(15, 2)));
  assert.ok((solve(P("find_r", 2, 3, 1, { k: 2 })) as Rational).equals(new Rational(3)));
  assert.ok((solve(P("find_r", 2, 1, 2, { k: 4 })) as Rational).equals(new Rational(1, 2)));
  assert.equal(solve(P("find_n_for_value", 2, 3, 1, { n: 4 })), 4);
});

test("reproducible and rejects invalid config", () => {
  for (const s of [1, 42, 123456789]) {
    assert.equal(serialize(generate(s, { answerType: "multiple-choice" })), serialize(generate(s, { answerType: "multiple-choice" })));
  }
  assert.throws(() => generate(1, { task: "bogus" as never }));
  assert.throws(() => generate(1, { task: "sum_infinite", answerType: "multiple-choice" }));
});

test("MC distractors are distinct misconceptions and agree with their formulas (incl. seeds 1,2,3,86)", () => {
  const seeds = [...Array(2000).keys()].map((i) => i + 1).concat([86]);
  for (const s of seeds) {
    const item = generate(s, { answerType: "multiple-choice" });
    const ds = item["distractors"] as Array<{ value: { num: number; den: number }; misconceptionId: string; rationale: string }>;
    assert.equal(new Set(ds.map((d) => d.misconceptionId)).size, ds.length, `seed ${s}`);
    const p = item["params"] as unknown as Params;
    const r = new Rational(p.r.num, p.r.den);
    for (const d of ds) {
      const expected = MISCONCEPTIONS[d.misconceptionId]!.formula(p.u1, r, p.n!);
      assert.equal(expected.num, d.value.num, `seed ${s}`);
      assert.equal(expected.den, d.value.den, `seed ${s}`);
      assert.equal(d.rationale, MISCONCEPTIONS[d.misconceptionId]!.observableError);
    }
  }
});

test("every task is reachable in free-response mode", () => {
  const seen = new Set<string>();
  for (let s = 1; s <= 2000; s++) seen.add((generate(s, { answerType: "integer" })["params"] as unknown as Params).task);
  assert.deepEqual([...seen].sort(), [...ALL_TASKS].sort());
});
