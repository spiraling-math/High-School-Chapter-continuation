/**
 * Independent TypeScript structural gate for gen.stats.data-handling v1.0.0.
 * Confirms every task generates, the owner interaction rules hold
 * (complete_frequency_table rejects multiple-choice), probability MC options encode
 * fractions in [0,1], and media kinds are correct per task.
 *
 * Run:  node --test domains/statistics/data-handling.test.ts
 */

import { test } from "node:test";
import assert from "node:assert/strict";
import { Rational } from "../../core/exact-math/rational.ts";
import { generate, validate, TASKS } from "./data-handling.ts";

const SVG_TASKS = new Set(["read_bar_chart", "read_pictogram", "read_line_graph"]);

test("every task generates and validates (free-response)", () => {
  for (const task of TASKS) {
    let generated = false;
    // sweep a few seeds because some tasks redraw on certain seeds
    for (let s = 1; s <= 40 && !generated; s++) {
      const item = generate(s, { task, interactionType: "free-response" });
      assert.equal(item.params.task, task, `seed ${s} task ${task}`);
      assert.equal(validate(item).status, "pass", `${task} seed ${s}`);
      generated = true;
    }
    assert.ok(generated, `task ${task} should generate`);
  }
});

test("complete_frequency_table rejects multiple-choice (throws)", () => {
  assert.throws(
    () => generate(5, { task: "complete_frequency_table", interactionType: "multiple-choice" }),
    /free-response only/,
  );
});

test("media kind is correct per task (svg for charts, table otherwise)", () => {
  for (const task of TASKS) {
    const item = generate(3, { task, interactionType: "free-response" });
    const media = item.media;
    assert.equal(media.length, 1, `${task} has one media asset`);
    if (SVG_TASKS.has(task)) {
      assert.equal(media[0].kind, "svg", `${task} media is svg`);
      assert.ok(typeof media[0].svg === "string" && media[0].svg.startsWith("<svg"), `${task} svg string`);
    } else {
      assert.equal(media[0].kind, "table", `${task} media is table`);
      assert.equal(media[0].spec.format, "semantic-html", `${task} semantic-html`);
    }
  }
});

test("probability MC options all encode fractions in [0,1]", () => {
  let seen = 0;
  for (let s = 1; s <= 400; s++) {
    const item = generate(s, { task: "single_event_probability", interactionType: "multiple-choice" });
    seen++;
    for (const o of item.options) {
      assert.ok(typeof o.value === "object" && o.value !== null && "num" in o.value, `seed ${s} option encodes a fraction`);
      const f = new Rational(o.value.num, o.value.den);
      assert.ok(f.num >= 0 && f.num <= f.den, `seed ${s} option ${o.display} lies in [0,1]`);
    }
    assert.equal(item.options.length, 4, `seed ${s} has four options`);
    assert.equal(item.options.filter((o: { correct: boolean }) => o.correct).length, 1, `seed ${s} one correct`);
  }
  assert.ok(seen > 0, "generated at least one probability MC item");
});
