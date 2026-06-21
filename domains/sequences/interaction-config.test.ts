/**
 * TD-1 config-acceptance tests (Node built-in test runner).
 *
 * Proves the forward `interactionType` config key produces byte-for-byte identical
 * items to the legacy `answerType` selector, for both approved generators — so
 * the migration is back-compatible and stored seeds/fixtures still reproduce.
 *
 * Run:  node --test domains/sequences/interaction-config.test.ts
 */

import { test } from "node:test";
import assert from "node:assert/strict";
import * as arithmetic from "./arithmetic.ts";
import * as geometric from "./geometric.ts";

const GENS = [
  { name: "arithmetic", generate: arithmetic.generate, serialize: arithmetic.serialize },
  { name: "geometric", generate: geometric.generate, serialize: geometric.serialize },
];

for (const g of GENS) {
  test(`${g.name}: interactionType maps to the legacy answerType byte-for-byte`, () => {
    for (let s = 1; s <= 300; s++) {
      assert.equal(
        g.serialize(g.generate(s, { interactionType: "multiple-choice" } as never)),
        g.serialize(g.generate(s, { answerType: "multiple-choice" } as never)),
        `${g.name} MC seed ${s}`,
      );
      assert.equal(
        g.serialize(g.generate(s, { interactionType: "free-response" } as never)),
        g.serialize(g.generate(s, { answerType: "integer" } as never)),
        `${g.name} free-response seed ${s}`,
      );
    }
  });

  test(`${g.name}: explicit interactionType overrides answerType`, () => {
    // interactionType wins when both are present.
    assert.equal(
      g.serialize(g.generate(7, { interactionType: "multiple-choice", answerType: "integer" } as never)),
      g.serialize(g.generate(7, { answerType: "multiple-choice" } as never)),
    );
  });
}
