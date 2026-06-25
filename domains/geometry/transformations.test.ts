/**
 * Unit tests for gen.geometry.transformations (the byte-for-byte mirror of the Python oracle).
 * Covers: the exact engine, ASCII-deg display, the anchored parser forms + variants, the checker
 * result codes, congruence + orientation, describe uniqueness, validate() across all 9 tasks,
 * MC -> InteractionNotSupported, and the misconception diagnostics.
 *
 * Run:  node --test domains/geometry/transformations.test.ts
 */

import { test } from "node:test";
import assert from "node:assert/strict";

import * as TC from "./transformations-core.ts";
import * as TS from "./transformations-shapes.ts";
import { checkDescription } from "./transformations-checker.ts";
import { diagnosticsFor, MISCONCEPTIONS, ALL_IDS } from "./transformations-misconceptions.ts";
import {
  generate,
  validate,
  serialize,
  describe,
  TASKS,
  OBJECTIVE_BY_TASK,
  txGridRound,
  InteractionNotSupported,
} from "./transformations.ts";

// --------------------------------------------------------------------------- //
// Exact engine
// --------------------------------------------------------------------------- //
test("engine: translation / reflection / rotation exact values", () => {
  assert.deepEqual(TC.applyTranslation([2, 3], -5, 4), [-3, 7]);
  assert.deepEqual(TC.reflectXEqA([4, 1], 1), [-2, 1]); // x = 1
  assert.deepEqual(TC.reflectYEqB([4, 1], 0), [4, -1]); // y = 0 (x-axis)
  assert.deepEqual(TC.reflectYEqX([2, 5]), [5, 2]);
  assert.deepEqual(TC.reflectYEqNegX([2, 5]), [-5, -2]);
  // 90 deg anticlockwise about origin: (x, y) -> (-y, x)
  assert.deepEqual(TC.rotateQuarter([3, 1], 0, 0, 1), [-1, 3]);
  // 180 about (1,1): (x,y) -> (2-x, 2-y)
  assert.deepEqual(TC.rotateQuarter([3, 4], 1, 1, 2), [-1, -2]);
  // 270 anticlockwise about origin: (x,y) -> (y,-x)
  assert.deepEqual(TC.rotateQuarter([3, 1], 0, 0, 3), [1, -3]);
});

test("engine: applyTransform dispatches on descriptor kind", () => {
  assert.deepEqual(TC.applyTransform(TC.translationDesc(1, -2), [0, 0]), [1, -2]);
  assert.deepEqual(TC.applyTransform(TC.reflectionDiagonal("y=x"), [3, 7]), [7, 3]);
  assert.deepEqual(TC.applyTransform(TC.rotationDesc(0, 0, 2), [2, 3]), [-2, -3]);
});

test("translationDesc rejects the zero vector", () => {
  assert.throws(() => TC.translationDesc(0, 0));
});

// --------------------------------------------------------------------------- //
// ASCII-deg display + axis equations
// --------------------------------------------------------------------------- //
test("format_display uses ASCII 'deg' and the canonical phrasings", () => {
  assert.equal(TC.formatDisplay(TC.translationDesc(3, -4)), "translation by vector (3, -4)");
  assert.equal(TC.formatDisplay(TC.reflectionVertical(2)), "reflection in x = 2");
  assert.equal(TC.formatDisplay(TC.reflectionHorizontal(-1)), "reflection in y = -1");
  assert.equal(TC.formatDisplay(TC.reflectionDiagonal("y=x")), "reflection in y = x");
  assert.equal(TC.formatDisplay(TC.reflectionDiagonal("y=-x")), "reflection in y = -x");
  assert.equal(TC.formatDisplay(TC.rotationDesc(1, 2, 1)), "rotation 90 deg anticlockwise about (1, 2)");
  assert.equal(TC.formatDisplay(TC.rotationDesc(0, 0, 2)), "rotation 180 deg about (0, 0)");
  assert.equal(TC.formatDisplay(TC.rotationDesc(-3, 1, 3)), "rotation 270 deg anticlockwise about (-3, 1)");
  // no degree symbol anywhere
  for (const d of [TC.rotationDesc(0, 0, 1), TC.rotationDesc(0, 0, 2), TC.rotationDesc(0, 0, 3)]) {
    assert.ok(!TC.formatDisplay(d).includes("°"));
  }
});

test("answerObject derives display from the canonical descriptor", () => {
  const a = TC.answerObject(TC.rotationDesc(0, 0, 1));
  assert.equal(a.type, "transformation");
  assert.deepEqual(a.canonical, TC.rotationDesc(0, 0, 1));
  assert.equal(a.display, "rotation 90 deg anticlockwise about (0, 0)");
});

// --------------------------------------------------------------------------- //
// Parser forms + variants
// --------------------------------------------------------------------------- //
test("parser: translation forms and variants", () => {
  assert.deepEqual(TC.parseDescriptor("translation by vector (3, -4)").descriptor, TC.translationDesc(3, -4));
  assert.deepEqual(TC.parseDescriptor("translate (3,-4)").descriptor, TC.translationDesc(3, -4));
  assert.deepEqual(TC.parseDescriptor("translation by the column vector [3; -4]").descriptor, TC.translationDesc(3, -4));
  // unicode minus normalised
  assert.deepEqual(TC.parseDescriptor("translation by vector (−3, 4)").descriptor, TC.translationDesc(-3, 4));
  assert.equal(TC.parseDescriptor("translation").code, "missing-translation-vector");
  assert.equal(TC.parseDescriptor("translation by vector (0, 0)").code, "contradictory-description");
  assert.equal(TC.parseDescriptor("translation by vector (1, 2) and more").code, "unparsed-trailing-text");
});

test("parser: reflection lines incl. axis aliases", () => {
  assert.deepEqual(TC.parseDescriptor("reflection in x = 3").descriptor, TC.reflectionVertical(3));
  assert.deepEqual(TC.parseDescriptor("reflection in y=-2").descriptor, TC.reflectionHorizontal(-2));
  assert.deepEqual(TC.parseDescriptor("reflection in the x-axis").descriptor, TC.reflectionHorizontal(0));
  assert.deepEqual(TC.parseDescriptor("reflection in the y axis").descriptor, TC.reflectionVertical(0));
  assert.deepEqual(TC.parseDescriptor("reflection in y = x").descriptor, TC.reflectionDiagonal("y=x"));
  assert.deepEqual(TC.parseDescriptor("reflection in y = -x").descriptor, TC.reflectionDiagonal("y=-x"));
  assert.equal(TC.parseDescriptor("reflection in the moon").code, "unsupported-reflection-line");
});

test("parser: rotation forms, direction handling, degree variants", () => {
  assert.deepEqual(TC.parseDescriptor("rotation 90 degrees anticlockwise about (1, 2)").descriptor, TC.rotationDesc(1, 2, 1));
  assert.deepEqual(TC.parseDescriptor("rotation 90° clockwise about the origin").descriptor, TC.rotationDesc(0, 0, 3));
  assert.deepEqual(TC.parseDescriptor("rotate 270 deg counterclockwise about (0,0)").descriptor, TC.rotationDesc(0, 0, 3));
  assert.deepEqual(TC.parseDescriptor("half turn about (2, -1)").descriptor, TC.rotationDesc(2, -1, 2));
  assert.deepEqual(TC.parseDescriptor("rotation 180 deg about (0, 0)").descriptor, TC.rotationDesc(0, 0, 2));
  // quarter-turn without a direction is ambiguous
  assert.equal(TC.parseDescriptor("rotation 90 deg about (0, 0)").code, "ambiguous-description");
  // contradictory direction
  assert.equal(TC.parseDescriptor("rotation 90 deg clockwise anticlockwise about (0,0)").code, "contradictory-description");
  // missing centre
  assert.equal(TC.parseDescriptor("rotation 180 deg").code, "missing-rotation-centre");
  // unsupported angle
  assert.equal(TC.parseDescriptor("rotation 45 deg anticlockwise about (0, 0)").code, "unsupported-angle");
});

test("parser: malformed responses", () => {
  assert.equal(TC.parseDescriptor("").code, "malformed-response");
  assert.equal(TC.parseDescriptor(null).code, "malformed-response");
  assert.equal(TC.parseDescriptor("turn it a bit").code, "malformed-response");
});

// --------------------------------------------------------------------------- //
// Checker codes
// --------------------------------------------------------------------------- //
test("checker: correct + wrong-* codes", () => {
  const trans = TC.translationDesc(2, 3);
  assert.equal(checkDescription(trans, "translation by vector (2, 3)"), "correct");
  assert.equal(checkDescription(trans, "translation by vector (3, 2)"), "wrong-translation-vector");
  assert.equal(checkDescription(trans, "reflection in x = 0"), "wrong-transformation-type");

  const refl = TC.reflectionVertical(1);
  assert.equal(checkDescription(refl, "reflection in x = 1"), "correct");
  assert.equal(checkDescription(refl, "reflection in x = 2"), "wrong-reflection-axis");

  const rot = TC.rotationDesc(1, 1, 1);
  assert.equal(checkDescription(rot, "rotation 90 deg anticlockwise about (1, 1)"), "correct");
  assert.equal(checkDescription(rot, "rotation 90 deg anticlockwise about (2, 2)"), "wrong-rotation-centre");
  assert.equal(checkDescription(rot, "rotation 90 deg clockwise about (1, 1)"), "wrong-rotation-amount");

  // parse-level codes propagate through the checker
  assert.equal(checkDescription(trans, ""), "malformed-response");
});

// --------------------------------------------------------------------------- //
// Congruence + orientation
// --------------------------------------------------------------------------- //
test("congruence by squared distances + orientation rules", () => {
  const tri: TC.Point[] = [
    [0, 0],
    [3, 0],
    [0, 2],
  ];
  const reflected = tri.map((p) => TC.reflectYEqB(p, 0)); // reflect in x-axis
  assert.ok(TS.congruentInCorrespondence(tri, reflected, "triangle"));
  assert.equal(TS.orientationSign(tri), -TS.orientationSign(reflected));

  const rotated = tri.map((p) => TC.rotateQuarter(p, 0, 0, 1));
  assert.ok(TS.congruentInCorrespondence(tri, rotated, "triangle"));
  assert.equal(TS.orientationSign(tri), TS.orientationSign(rotated)); // rotation preserves orientation

  // non-congruent (scaled) is rejected
  const scaled: TC.Point[] = [
    [0, 0],
    [6, 0],
    [0, 4],
  ];
  assert.ok(!TS.congruentInCorrespondence(tri, scaled, "triangle"));
});

// --------------------------------------------------------------------------- //
// Describe uniqueness
// --------------------------------------------------------------------------- //
test("uniqueDescriptor returns the single family descriptor", () => {
  const tri: TC.Point[] = [
    [-4, 4],
    [2, 0],
    [-1, 0],
  ];
  const desc = TC.rotationDesc(-2, 0, 3);
  const img = tri.map((p) => TC.applyTransform(desc, p));
  const uniq = TS.uniqueDescriptor("rotation", tri, img);
  assert.ok(uniq !== null);
  assert.ok(TC.descriptorsEqual(uniq, desc));

  // unchanged object -> null
  assert.equal(TS.uniqueDescriptor("translation", tri, tri), null);
});

// --------------------------------------------------------------------------- //
// txGridRound negative-rounding (the parity-critical divmod semantics)
// --------------------------------------------------------------------------- //
test("txGridRound mirrors Python round-half-up via floored divmod", () => {
  assert.equal(txGridRound(5, 2), 3); // 2.5 -> 3
  assert.equal(txGridRound(4, 2), 2);
  assert.equal(txGridRound(3, 2), 2); // 1.5 -> 2
  assert.equal(txGridRound(-5, 2), -2); // divmod(-5,2)=(-3,1); 2*1>=2 -> -2
  assert.equal(txGridRound(-3, 2), -1); // divmod(-3,2)=(-2,1); -> -1
  assert.equal(txGridRound(-4, 2), -2);
  assert.equal(txGridRound(-1, 2), 0); // divmod(-1,2)=(-1,1); -> 0
  assert.equal(txGridRound(7, 3), 2); // divmod(7,3)=(2,1); 2*1<3 -> 2
  assert.equal(txGridRound(8, 3), 3); // divmod(8,3)=(2,2); 2*2>=3 -> 3
});

// --------------------------------------------------------------------------- //
// Misconception registry + diagnostics
// --------------------------------------------------------------------------- //
test("misconception registry has the 24 owner-K IDs, all MISC.TRANS.*", () => {
  assert.equal(MISCONCEPTIONS.length, 24);
  assert.equal(new Set(ALL_IDS).size, 24);
  for (const id of ALL_IDS) assert.ok(id.startsWith("MISC.TRANS."));
  assert.ok(ALL_IDS.includes("MISC.TRANS.NAMES_REFLECTION_FOR_ROTATION"));
});

test("diagnostics_for: perform tasks predict wrong coordinates; collisions dropped", () => {
  const src: TC.Point[] = [[2, -6]];
  const desc = TC.translationDesc(0, 5);
  const diags = diagnosticsFor("translate_point", src, desc);
  assert.ok(diags.length > 0);
  // the correct image is (2, -1); no diagnostic may predict it
  for (const d of diags) {
    assert.equal(d.kind, "value");
    assert.ok(!(d.predicted.x === 2 && d.predicted.y === -1));
  }
});

test("diagnostics_for: describe rotation yields parser + descriptor diagnostics", () => {
  const tri: TC.Point[] = [
    [-4, 4],
    [2, 0],
    [-1, 0],
  ];
  const desc = TC.rotationDesc(-2, 0, 3);
  const diags = diagnosticsFor("describe_rotation", tri, desc);
  const ids = diags.map((d) => d.misconceptionId);
  assert.ok(ids.includes("MISC.TRANS.RIGHT_ANGLE_MISSING_CENTRE"));
  assert.ok(ids.includes("MISC.TRANS.RIGHT_CENTRE_WRONG_DIRECTION"));
  assert.ok(ids.includes("MISC.TRANS.NAMES_REFLECTION_FOR_ROTATION"));
  const missing = diags.find((d) => d.misconceptionId === "MISC.TRANS.RIGHT_ANGLE_MISSING_CENTRE");
  assert.equal(missing.kind, "parser");
  assert.equal(missing.predicted, null);
  assert.equal(missing.studentResponseText, "rotation 270 deg anticlockwise");
});

// --------------------------------------------------------------------------- //
// Generation, validation, interaction support
// --------------------------------------------------------------------------- //
test("all 9 tasks generate and validate across several seeds", () => {
  assert.equal(TASKS.length, 9);
  for (const task of TASKS) {
    for (let seed = 1; seed <= 12; seed++) {
      const item = generate(seed, { interactionType: "free-response", task });
      assert.equal(item.params.task, task);
      assert.equal(item.objectiveIds[0], OBJECTIVE_BY_TASK[task]);
      const v = validate(item);
      assert.equal(v.valid, true, `validate ${task} seed ${seed}: ${JSON.stringify(v.checks.filter((c: { ok: boolean }) => !c.ok))}`);
      // serialize round-trips through canonical JSON
      assert.equal(typeof serialize(item), "string");
    }
  }
});

test("random task selection when no task is pinned", () => {
  const item = generate(42, { interactionType: "free-response" });
  assert.ok(TASKS.includes(item.params.task));
  assert.equal(validate(item).valid, true);
});

test("unsupported interaction (e.g. multiple-choice) throws InteractionNotSupported", () => {
  assert.throws(
    () => generate(1, { interactionType: "multiple-choice" }),
    (e: unknown) => e instanceof InteractionNotSupported,
  );
});

test("describe() advertises the generator surface", () => {
  const d = describe();
  assert.equal(d.generatorId, "gen.geometry.transformations");
  assert.equal(d.version, "1.0.0");
  assert.deepEqual(d.tasks, TASKS);
  assert.deepEqual(d.interactionTypes, ["free-response"]);
  assert.deepEqual(d.answerTypes, ["coordinate", "table-completion", "transformation"]);
});
