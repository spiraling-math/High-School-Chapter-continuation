/**
 * Cross-language PRNG parity tests (Node built-in test runner).
 *
 * Asserts the TypeScript Mulberry32 reproduces the Python oracle's committed
 * anchors byte-for-byte. Run:  node --test core/seeded-random/mulberry32.test.ts
 */

import { test } from "node:test";
import assert from "node:assert/strict";
import { readFileSync } from "node:fs";
import { fileURLToPath } from "node:url";
import { dirname, join } from "node:path";
import { Mulberry32 } from "./mulberry32.ts";

const here = dirname(fileURLToPath(import.meta.url));
const anchors: Record<string, number[]> = JSON.parse(
  readFileSync(join(here, "../../oracle/golden/prng_anchors.json"), "utf8"),
);

test("matches Python oracle PRNG anchors (cross-language parity)", () => {
  for (const [seed, expected] of Object.entries(anchors)) {
    const rng = new Mulberry32(Number(seed));
    const got = expected.map(() => rng.nextUint32());
    assert.deepEqual(got, expected, `seed ${seed} stream mismatch`);
  }
});

test("is deterministic for a fixed seed", () => {
  const a = new Mulberry32(123456789);
  const b = new Mulberry32(123456789);
  const sa = Array.from({ length: 20 }, () => a.nextUint32());
  const sb = Array.from({ length: 20 }, () => b.nextUint32());
  assert.deepEqual(sa, sb);
});

test("nextUint32 stays within 32-bit unsigned range", () => {
  const rng = new Mulberry32(1);
  for (let i = 0; i < 1000; i++) {
    const v = rng.nextUint32();
    assert.ok(v >= 0 && v <= 0xffffffff && Number.isInteger(v));
  }
});

test("nextFloat stays within [0, 1)", () => {
  const rng = new Mulberry32(7);
  for (let i = 0; i < 1000; i++) {
    const f = rng.nextFloat();
    assert.ok(f >= 0 && f < 1);
  }
});

test("nextInt is inclusive and covers the full range", () => {
  const rng = new Mulberry32(99);
  const seen = new Set<number>();
  for (let i = 0; i < 5000; i++) {
    const v = rng.nextInt(3, 8);
    assert.ok(v >= 3 && v <= 8);
    seen.add(v);
  }
  assert.deepEqual([...seen].sort(), [3, 4, 5, 6, 7, 8]);
});
