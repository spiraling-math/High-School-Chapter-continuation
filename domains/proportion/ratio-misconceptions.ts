/**
 * gen.proportion.ratio — MISC.RATIO.* registry (16) and per-item diagnostics (owner 10).
 *
 * Byte-for-byte TypeScript mirror of oracle/spi_oracle/ratio_misconceptions.py.
 * Single source of truth for ratio misconception IDs. Each diagnostic declares a predicted student
 * response computed by an EXACT formula and the expected checker result code; an inapplicable or
 * answer-colliding diagnostic is OMITTED.
 */

import { Rational } from "../../core/exact-math/rational.ts";
import * as RC from "./ratio-core.ts";

// eslint-disable-next-line @typescript-eslint/no-explicit-any
type Json = any;

export const DOMAIN = "proportion";

function _m(mid: string, title: string, obs: string, feedback: string, hint: string, objs: string[]): Json {
  return {
    misconceptionId: mid,
    domain: DOMAIN,
    title,
    description: obs,
    observableError: obs,
    feedback,
    remediationHint: hint,
    objectiveRelationships: [...objs],
    reviewStatus: "proposed",
    version: "1.0.0",
  };
}

const _SIMP = ["SPI.MIDDLE.RATIO.SIMPLIFY.01"];
const _WRITE = ["SPI.MIDDLE.RATIO.WRITE_FROM_QUANTITIES.01"];
const _R2F = ["SPI.MIDDLE.RATIO.RATIO_TO_FRACTION.01"];
const _F2R = ["SPI.MIDDLE.RATIO.FRACTION_TO_RATIO.01"];
const _SHARE = ["SPI.MIDDLE.RATIO.SHARE_TWO_PART.01", "SPI.MIDDLE.RATIO.SHARE_THREE_PART.01"];
const _MISS = ["SPI.MIDDLE.RATIO.MISSING_PART.01"];
const _DIR = ["SPI.MIDDLE.RATIO.DIRECT_PROPORTION.01"];
const _INV = ["SPI.MIDDLE.RATIO.INVERSE_PROPORTION.01"];
const _RATE = ["SPI.MIDDLE.RATIO.UNIT_RATE.01"];
const _BUY = ["SPI.MIDDLE.RATIO.BEST_BUY.01"];
const _SCALE = ["SPI.MIDDLE.RATIO.SIMPLE_SCALE.01"];

export const MISCONCEPTIONS: Json[] = [
  _m(
    "MISC.RATIO.NOT_SIMPLIFIED",
    "Does not simplify fully",
    "Divides the parts by a common factor but not by the full greatest common divisor.",
    "Divide every part by their GREATEST common divisor so no common factor remains.",
    "Find the gcd of all parts before dividing.",
    [..._SIMP, ..._WRITE, ..._F2R],
  ),
  _m(
    "MISC.RATIO.EQUIVALENT_NOT_SIMPLIFIED",
    "Leaves the ratio unsimplified",
    "Gives an equivalent ratio that is not in simplest form when simplest form is required.",
    "An equivalent ratio is correct in value but the task asks for simplest form.",
    "Keep dividing until the parts share no common factor.",
    [..._SIMP],
  ),
  _m(
    "MISC.RATIO.REVERSED_ORDER",
    "Reverses the order of the ratio",
    "Writes the parts in the wrong order (e.g. b:a instead of a:b).",
    "Order matters in a ratio: 2:3 is not the same as 3:2. Match each part to the named quantity.",
    "Write the parts in the order the quantities are named.",
    [..._WRITE, ..._F2R],
  ),
  _m(
    "MISC.RATIO.ADDS_PARTS_WRONG",
    "Combines the ratio parts incorrectly",
    "Adds or combines the ratio parts incorrectly when forming or simplifying the ratio.",
    "Keep the parts separate; only divide each by the common factor.",
    "Do not add the parts together when simplifying.",
    [..._SIMP, ..._SHARE],
  ),
  _m(
    "MISC.RATIO.PART_AS_WHOLE",
    "Treats one part as the whole",
    "Uses a single part as the total instead of the sum of all parts.",
    "The whole is the SUM of all the parts, not one part.",
    "Add all the parts to find the total before sharing.",
    [..._R2F, ..._SHARE],
  ),
  _m(
    "MISC.RATIO.WRONG_TOTAL_PARTS",
    "Uses the wrong total number of parts",
    "Counts the wrong number of total parts when sharing.",
    "Add every part of the ratio to get the total number of parts.",
    "Total parts = sum of all the ratio parts.",
    [..._SHARE],
  ),
  _m(
    "MISC.RATIO.DIVIDES_BY_ONE_PART",
    "Divides by one part instead of the total",
    "Divides the whole by a single ratio part instead of by the total number of parts.",
    "Divide the whole by the TOTAL number of parts to find the value of one part.",
    "One part = whole / (sum of parts).",
    [..._SHARE, ..._MISS],
  ),
  _m(
    "MISC.RATIO.MULTIPLIES_NOT_DIVIDES_UNITARY",
    "Multiplies when it should divide",
    "Multiplies to find one unit instead of dividing.",
    "To find one unit, DIVIDE the total by the quantity.",
    "One unit = total / quantity.",
    [..._MISS, ..._DIR],
  ),
  _m(
    "MISC.RATIO.DIVIDES_NOT_MULTIPLIES_UNITARY",
    "Divides when it should multiply",
    "Divides by the required quantity instead of multiplying after finding one unit.",
    "After finding one unit, MULTIPLY by the required quantity.",
    "Result = one unit x required quantity.",
    [..._DIR, ..._RATE],
  ),
  _m(
    "MISC.RATIO.DIRECT_FOR_INVERSE",
    "Uses direct proportion for an inverse problem",
    "Scales directly when the quantities are inversely proportional.",
    "When one quantity goes up the other goes DOWN: use the product invariant, not direct scaling.",
    "Use q1 x v1 = q2 x v2 for inverse proportion.",
    [..._INV],
  ),
  _m(
    "MISC.RATIO.INVERSE_FOR_DIRECT",
    "Uses inverse proportion for a direct problem",
    "Applies the inverse rule when the quantities are directly proportional.",
    "When both quantities grow together, use the unitary (direct) method, not the inverse rule.",
    "Find one unit, then multiply.",
    [..._DIR],
  ),
  _m(
    "MISC.RATIO.NO_UNIT_RATE_COMPARE",
    "Compares without a unit rate",
    "Compares the options by raw total instead of normalising to a unit rate.",
    "Compare value for money by the rate PER ONE UNIT, not by the total.",
    "Find each option's unit rate before comparing.",
    [..._BUY],
  ),
  _m(
    "MISC.RATIO.LOWEST_PRICE_NOT_BEST",
    "Chooses the cheapest, not the best value",
    "Picks the lowest total price instead of the lowest unit rate.",
    "The best value has the lowest cost PER UNIT, which is not always the cheapest pack.",
    "Compare unit rates, then choose the smallest.",
    [..._BUY],
  ),
  _m(
    "MISC.RATIO.SCALE_WRONG_DIRECTION",
    "Scales in the wrong direction",
    "Multiplies when it should divide (or vice versa) when applying the scale.",
    "Check whether the value should grow or shrink, then scale the right way.",
    "Decide the direction of the scale before multiplying or dividing.",
    [..._SCALE],
  ),
  _m(
    "MISC.RATIO.ADDITIVE_NOT_MULTIPLICATIVE",
    "Adds instead of scaling",
    "Adds a constant difference instead of multiplying by the scale factor.",
    "Proportion is MULTIPLICATIVE: multiply by the scale factor, do not add a difference.",
    "Use multiplication by the scale factor, not addition.",
    [..._DIR, ..._SCALE, ..._INV],
  ),
  _m(
    "MISC.RATIO.FRACTION_PART_OVER_PART",
    "Writes part over the other part",
    "Writes one part over the other part instead of the part over the whole.",
    "A fraction of the whole is the part over the TOTAL (sum of parts), not part over part.",
    "Fraction of the whole = part / (sum of parts).",
    [..._R2F],
  ),
];

export const ALL_IDS: readonly string[] = MISCONCEPTIONS.map((m) => m.misconceptionId as string);
const _BY_ID: Record<string, Json> = {};
for (const m of MISCONCEPTIONS) {
  _BY_ID[m.misconceptionId as string] = m;
}

export function registry(): Json[] {
  return MISCONCEPTIONS.map((m) => ({ ...m }));
}

// --------------------------------------------------------------------------- //
// Per-item diagnostics (owner 10).
// --------------------------------------------------------------------------- //
function _ratioDiag(
  mid: string,
  correctParts: number[],
  predictedParts: number[] | null,
  requireSimplest: boolean,
): Json | null {
  if (predictedParts === null || predictedParts.some((p) => p <= 0)) {
    return null;
  }
  const correctSimplest = RC.simplifyParts(correctParts);
  if (RC.formatRatio(predictedParts) === RC.formatRatio(correctSimplest)) {
    return null; // predicted response coincides with the correct answer -> omit
  }
  const code = RC.checkRatio(correctSimplest, RC.formatRatio(predictedParts), requireSimplest).code as string;
  if (code === "correct") {
    return null;
  }
  return {
    misconceptionId: mid,
    domain: DOMAIN,
    task: null,
    predictedResponse: RC.formatRatio(predictedParts),
    predictedCanonical: { parts: [...predictedParts] },
    requireSimplest,
    observableError: _BY_ID[mid].observableError,
    feedback: _BY_ID[mid].feedback,
    expectedResultCode: code,
  };
}

function _toRational(v: number | Rational): Rational {
  return v instanceof Rational ? v : Rational.from(v);
}

function _numDiag(mid: string, correct: number | Rational, predicted: number | Rational | null): Json | null {
  if (predicted === null) {
    return null;
  }
  const cf = _toRational(correct);
  const pf = _toRational(predicted);
  if (pf.equals(cf)) {
    return null;
  }
  const disp = pf.den === 1 ? String(pf.num) : `${pf.num}/${pf.den}`;
  return {
    misconceptionId: mid,
    domain: DOMAIN,
    task: null,
    predictedResponse: disp,
    predictedCanonical: { num: pf.num, den: pf.den },
    observableError: _BY_ID[mid].observableError,
    feedback: _BY_ID[mid].feedback,
    expectedResultCode: "incorrect",
  };
}

function _choiceDiag(mid: string, correctLabel: string, predictedLabel: string | null): Json | null {
  if (predictedLabel === null || predictedLabel === correctLabel) {
    return null;
  }
  return {
    misconceptionId: mid,
    domain: DOMAIN,
    task: null,
    predictedResponse: predictedLabel,
    predictedCanonical: predictedLabel,
    observableError: _BY_ID[mid].observableError,
    feedback: _BY_ID[mid].feedback,
    expectedResultCode: "wrong-choice",
  };
}

function _tableDiag(mid: string, correctCells: number[], labels: string[], predicted: Json[]): Json | null {
  if (predicted === null) {
    return null;
  }
  if (predicted.some((c) => (c.value as number) < 0)) {
    return null;
  }
  const correctByLabel: Record<string, number> = {};
  labels.forEach((lab, i) => {
    correctByLabel[lab] = correctCells[i] as number;
  });
  const predByLabel: Record<string, number> = {};
  for (const c of predicted) {
    predByLabel[c.location as string] = c.value as number;
  }
  // dict equality (Python {==}): same key set and same values
  const ck = Object.keys(correctByLabel);
  const pk = Object.keys(predByLabel);
  if (ck.length === pk.length && ck.every((k) => predByLabel[k] === correctByLabel[k])) {
    return null;
  }
  return {
    misconceptionId: mid,
    domain: DOMAIN,
    task: null,
    predictedResponse: predicted.map((c) => `${c.location}=${c.value}`).join(", "),
    predictedCanonical: { cells: [...predicted] },
    observableError: _BY_ID[mid].observableError,
    feedback: _BY_ID[mid].feedback,
    expectedResultCode: "incorrect",
  };
}

export function diagnosticsFor(task: string, params: Json): Json[] {
  const out: (Json | null)[] = [];

  if (task === "simplify") {
    const parts = params.parts as number[];
    const g = RC.gcdList(parts);
    // NOT_SIMPLIFIED: divide by a PROPER factor of the gcd (not the full gcd).
    let partialDiv: number | null = null;
    for (let d = 2; d < g; d++) {
      if (g % d === 0) {
        partialDiv = d;
        break;
      }
    }
    if (partialDiv !== null) {
      const pd = partialDiv;
      out.push(_ratioDiag("MISC.RATIO.NOT_SIMPLIFIED", parts, parts.map((p) => Math.trunc(p / pd)), true));
    }
    // EQUIVALENT_NOT_SIMPLIFIED: leaves the ratio exactly as given (unsimplified).
    if (g > 1) {
      out.push(_ratioDiag("MISC.RATIO.EQUIVALENT_NOT_SIMPLIFIED", parts, [...parts], true));
    }
    // ADDS_PARTS_WRONG: collapses two parts into their sum.
    if (parts.length >= 2) {
      const simp = RC.simplifyParts(parts);
      out.push(
        _ratioDiag(
          "MISC.RATIO.ADDS_PARTS_WRONG",
          parts,
          [(simp[0] as number) + (simp[1] as number), ...simp.slice(2)],
          true,
        ),
      );
    }
  } else if (task === "write_from_quantities") {
    const q = params.quantities as number[];
    const simp = RC.simplifyParts(q);
    // REVERSED_ORDER: writes the parts in reversed order.
    out.push(_ratioDiag("MISC.RATIO.REVERSED_ORDER", simp, simp.slice().reverse(), false));
    // NOT_SIMPLIFIED: gives the raw quantities without simplifying.
    if (RC.gcdList(q) > 1) {
      out.push(_ratioDiag("MISC.RATIO.NOT_SIMPLIFIED", simp, [...q], true));
    }
  } else if (task === "ratio_to_fraction") {
    const a = (params.parts as number[])[0] as number;
    const b = (params.parts as number[])[1] as number;
    const idx = params.partIndex as number;
    const part = (params.parts as number[])[idx] as number;
    const other = (params.parts as number[])[1 - idx] as number;
    const correct = new Rational(part, a + b);
    // FRACTION_PART_OVER_PART: writes the part over the OTHER part.
    if (other !== 0) {
      out.push(_numDiag("MISC.RATIO.FRACTION_PART_OVER_PART", correct, new Rational(part, other)));
    }
    // REVERSED_ORDER: gives the OTHER part's fraction of the whole.
    out.push(_numDiag("MISC.RATIO.REVERSED_ORDER", correct, new Rational(other, a + b)));
    // PART_AS_WHOLE: uses the part itself as the whole (gives 1) — surfaced as 1/1.
    out.push(_numDiag("MISC.RATIO.PART_AS_WHOLE", correct, new Rational(1, 1)));
  } else if (task === "fraction_to_ratio") {
    const num = params.num as number;
    const den = params.den as number;
    const rest = den - num;
    const correct = RC.simplifyParts([num, rest]);
    // REVERSED_ORDER: writes rest:part instead of part:rest.
    out.push(_ratioDiag("MISC.RATIO.REVERSED_ORDER", correct, RC.simplifyParts([num, rest]).reverse(), false));
    // PART_AS_WHOLE: writes part:whole (num:den) instead of part:rest.
    out.push(_ratioDiag("MISC.RATIO.PART_AS_WHOLE", correct, RC.simplifyParts([num, den]), false));
    // ADDS_PARTS_WRONG: writes whole:part (den:num).
    out.push(_ratioDiag("MISC.RATIO.ADDS_PARTS_WRONG", correct, RC.simplifyParts([den, num]), false));
    // NOT_SIMPLIFIED: gives part:rest without simplifying.
    if (RC.gcdList([num, rest]) > 1) {
      out.push(_ratioDiag("MISC.RATIO.NOT_SIMPLIFIED", correct, [num, rest], true));
    }
  } else if (task === "share_two_part" || task === "share_three_part") {
    const total = params.total as number;
    const parts = params.parts as number[];
    const labels = params.labels as string[];
    const shares = RC.share(total, parts) as number[];
    const s = parts.reduce((acc, p) => acc + p, 0);
    const one = Math.trunc(total / s);
    // WRONG_TOTAL_PARTS: divides by the number of parts (count), not the sum.
    if (parts.length !== s && total % parts.length === 0) {
      const wrongOne = Math.trunc(total / parts.length);
      const predicted = labels.map((lab, i) => ({ location: lab, value: wrongOne * (parts[i] as number) }));
      const d = _tableDiag("MISC.RATIO.WRONG_TOTAL_PARTS", shares, labels, predicted);
      if (d !== null) out.push(d);
    }
    // DIVIDES_BY_ONE_PART: divides the whole by a single part value instead of the sum.
    if ((parts[0] as number) !== s && total % (parts[0] as number) === 0) {
      const wrongOne = Math.trunc(total / (parts[0] as number));
      const predicted = labels.map((lab, i) => ({ location: lab, value: wrongOne * (parts[i] as number) }));
      const d = _tableDiag("MISC.RATIO.DIVIDES_BY_ONE_PART", shares, labels, predicted);
      if (d !== null) out.push(d);
    }
    // PART_AS_WHOLE: gives each labelled share the value of one part.
    if (task === "share_two_part") {
      void one; // mirrors the (overwritten) Python local
      const predicted = labels.map((lab, i) => ({ location: lab, value: parts[i] as number }));
      const d = _tableDiag("MISC.RATIO.PART_AS_WHOLE", shares, labels, predicted);
      if (d !== null) out.push(d);
    }
  } else if (task === "missing_part") {
    const parts = params.parts as number[];
    const ki = params.knownIndex as number;
    const mi = params.missingIndex as number;
    const kv = params.knownValue as number;
    const one = Math.trunc(kv / (parts[ki] as number));
    const correct = one * (parts[mi] as number);
    // DIVIDES_BY_ONE_PART: uses the known value itself as one part.
    out.push(_numDiag("MISC.RATIO.DIVIDES_BY_ONE_PART", correct, kv * (parts[mi] as number)));
    // MULTIPLIES_NOT_DIVIDES_UNITARY: multiplies to find one unit instead of dividing.
    out.push(
      _numDiag("MISC.RATIO.MULTIPLIES_NOT_DIVIDES_UNITARY", correct, kv * (parts[ki] as number) * (parts[mi] as number)),
    );
  } else if (task === "direct_proportion") {
    const quantity = params.quantity as number;
    const total = params.total as number;
    const target = params.target as number;
    const correct = new Rational(total, quantity).mul(Rational.from(target));
    // ADDITIVE_NOT_MULTIPLICATIVE: adds the difference to the total.
    out.push(_numDiag("MISC.RATIO.ADDITIVE_NOT_MULTIPLICATIVE", correct, Rational.from(total + (target - quantity))));
    // INVERSE_FOR_DIRECT: applies the inverse product rule.
    if (target !== 0) {
      out.push(_numDiag("MISC.RATIO.INVERSE_FOR_DIRECT", correct, new Rational(total * quantity, target)));
    }
    // DIVIDES_NOT_MULTIPLIES_UNITARY: divides by the target instead of multiplying.
    if (target !== 0) {
      out.push(_numDiag("MISC.RATIO.DIVIDES_NOT_MULTIPLIES_UNITARY", correct, new Rational(total, quantity * target)));
    }
  } else if (task === "inverse_proportion") {
    const q1 = params.q1 as number;
    const v1 = params.v1 as number;
    const q2 = params.q2 as number;
    const correct = Math.floor((q1 * v1) / q2);
    // DIRECT_FOR_INVERSE: scales directly (v1 * q2 / q1).
    if (q1 !== 0) {
      out.push(_numDiag("MISC.RATIO.DIRECT_FOR_INVERSE", correct, new Rational(v1 * q2, q1)));
    }
    // MULTIPLIES_NOT_DIVIDES_UNITARY: gives the product q1*v1.
    out.push(_numDiag("MISC.RATIO.MULTIPLIES_NOT_DIVIDES_UNITARY", correct, Rational.from(q1 * v1)));
    // ADDITIVE_NOT_MULTIPLICATIVE: adds the change (q2 - q1) to v1.
    out.push(_numDiag("MISC.RATIO.ADDITIVE_NOT_MULTIPLICATIVE", correct, Rational.from(v1 + (q2 - q1))));
  } else if (task === "unit_rate") {
    const total = params.total as number;
    const quantity = params.quantity as number;
    const correct = new Rational(total, quantity);
    // DIVIDES_NOT_MULTIPLIES_UNITARY: inverts the rate.
    if (total !== 0) {
      out.push(_numDiag("MISC.RATIO.DIVIDES_NOT_MULTIPLIES_UNITARY", correct, new Rational(quantity, total)));
    }
  } else if (task === "best_buy") {
    const options = params.options as Json[];
    const correctLabel = params.correctLabel as string;
    // NO_UNIT_RATE_COMPARE: compares by raw total -> picks the largest total.
    const byTotal = _maxBy(options, (o) => [o.totalAmount as number, o.label as string]);
    out.push(_choiceDiag("MISC.RATIO.NO_UNIT_RATE_COMPARE", correctLabel, byTotal.label as string));
    // LOWEST_PRICE_NOT_BEST: picks the smallest total (cheapest pack).
    const byLowest = _minBy(options, (o) => [o.totalAmount as number, o.label as string]);
    out.push(_choiceDiag("MISC.RATIO.LOWEST_PRICE_NOT_BEST", correctLabel, byLowest.label as string));
  } else if (task === "simple_scale") {
    const value = params.value as number;
    const fnum = params.factorNum as number;
    const fden = params.factorDen as number;
    const factor = new Rational(fnum, fden);
    const correct = Rational.from(value).mul(factor);
    // SCALE_WRONG_DIRECTION: applies the reciprocal.
    if (fnum !== 0) {
      out.push(_numDiag("MISC.RATIO.SCALE_WRONG_DIRECTION", correct, Rational.from(value).mul(new Rational(fden, fnum))));
    }
    // ADDITIVE_NOT_MULTIPLICATIVE: adds the scale parts.
    out.push(_numDiag("MISC.RATIO.ADDITIVE_NOT_MULTIPLICATIVE", correct, Rational.from(value + fnum - fden)));
  }

  return out.filter((d): d is Json => d !== null);
}

// max/min by a tuple key (lexicographic [number, string]), matching Python max(..., key=...) which
// returns the FIRST max on ties (stable scan).
function _cmpKey(a: [number, string], b: [number, string]): number {
  if (a[0] !== b[0]) return a[0] < b[0] ? -1 : 1;
  if (a[1] !== b[1]) return a[1] < b[1] ? -1 : 1;
  return 0;
}

function _maxBy(items: Json[], key: (o: Json) => [number, string]): Json {
  let best = items[0];
  let bestKey = key(items[0]);
  for (let i = 1; i < items.length; i++) {
    const k = key(items[i]);
    if (_cmpKey(k, bestKey) > 0) {
      best = items[i];
      bestKey = k;
    }
  }
  return best;
}

function _minBy(items: Json[], key: (o: Json) => [number, string]): Json {
  let best = items[0];
  let bestKey = key(items[0]);
  for (let i = 1; i < items.length; i++) {
    const k = key(items[i]);
    if (_cmpKey(k, bestKey) < 0) {
      best = items[i];
      bestKey = k;
    }
  }
  return best;
}
