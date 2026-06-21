/**
 * Shared multiple-choice option assembly (SDK).
 *
 * Generators select their own distractors from formula-backed misconception rules
 * (that logic stays in each domain). This helper performs ONLY the reusable,
 * domain-independent assembly that every generator repeats: build the option pool
 * (correct + distractors), shuffle deterministically with the generator's seeded
 * RNG, and label A..E — preserving value, order, ids, misconception metadata, and
 * rationale byte-for-byte.
 *
 * Value encoding is injected (`encode`), so an integer generator and an
 * exact-rational generator both reuse this without the helper knowing the maths.
 * There are NO generic/random distractors here.
 */

import type { Json } from "../serialization/canonical.ts";

/** Just the slice of the seeded RNG this helper needs (Mulberry32 satisfies it). */
export interface Shuffler {
  shuffle<T>(items: readonly T[]): T[];
}

export interface McDistractor<V> {
  value: V;
  misconceptionId: string;
  rationale: string;
}

export interface AssembledMultipleChoice {
  distractors: Array<Record<string, Json>>;
  options: Array<Record<string, Json>>;
}

const LABELS = ["A", "B", "C", "D", "E"];

/**
 * Assemble distractor records and shuffled options.
 *
 * Determinism: the only RNG call is a single `shuffle` of the option pool, at the
 * same point the generators previously shuffled — so output is byte-identical.
 * The helper does not deduplicate or validate; uniqueness, "no distractor equals
 * the answer", and the ≥3 requirement remain the domain generator's guarantees
 * (and are checked by the validators).
 */
export function assembleMultipleChoice<V>(
  rng: Shuffler,
  correct: V,
  distractors: ReadonlyArray<McDistractor<V>>,
  encode: (value: V) => { value: Json; display: string },
): AssembledMultipleChoice {
  const distractorRecords: Array<Record<string, Json>> = distractors.map((dd, i) => {
    const e = encode(dd.value);
    return { id: `d${i + 1}`, value: e.value, display: e.display, misconceptionId: dd.misconceptionId, rationale: dd.rationale };
  });

  interface Opt { value: V; correct: boolean; misconceptionId: string | null; }
  const pool: Opt[] = [{ value: correct, correct: true, misconceptionId: null }];
  for (const dd of distractors) pool.push({ value: dd.value, correct: false, misconceptionId: dd.misconceptionId });

  const shuffled = rng.shuffle(pool);
  const options: Array<Record<string, Json>> = shuffled.map((o, i) => {
    const e = encode(o.value);
    const opt: Record<string, Json> = { label: LABELS[i] as string, value: e.value, display: e.display, correct: o.correct };
    if (o.misconceptionId) opt["misconceptionId"] = o.misconceptionId;
    return opt;
  });

  return { distractors: distractorRecords, options };
}
