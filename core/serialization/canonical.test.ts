/**
 * Canonical serialization tests (Node built-in test runner).
 * Run:  node --test core/serialization/canonical.test.ts
 */

import { test } from "node:test";
import assert from "node:assert/strict";
import { canonicalStringify } from "./canonical.ts";

test("sorts object keys lexicographically and uses no whitespace", () => {
  const out = canonicalStringify({ b: 1, a: 2, c: 3 });
  assert.equal(out, '{"a":2,"b":1,"c":3}');
});

test("sorts keys recursively in nested objects and arrays", () => {
  const out = canonicalStringify({ z: { y: 1, x: 2 }, a: [{ q: 1, p: 2 }] });
  assert.equal(out, '{"a":[{"p":2,"q":1}],"z":{"x":2,"y":1}}');
});

test("serializes primitives like Python json.dumps", () => {
  assert.equal(canonicalStringify(31), "31");
  assert.equal(canonicalStringify(-23), "-23");
  assert.equal(canonicalStringify(0.15), "0.15");
  assert.equal(canonicalStringify(true), "true");
  assert.equal(canonicalStringify(null), "null");
  assert.equal(canonicalStringify("hi"), '"hi"');
});

test("matches a known oracle-style serialization", () => {
  // Mirrors the shape of an answer object; keys deliberately out of order.
  const obj = { type: "integer", display: "31", canonical: 31 };
  assert.equal(
    canonicalStringify(obj),
    '{"canonical":31,"display":"31","type":"integer"}',
  );
});

test("rejects non-finite numbers", () => {
  assert.throws(() => canonicalStringify(Number.NaN));
  assert.throws(() => canonicalStringify(Number.POSITIVE_INFINITY));
});
