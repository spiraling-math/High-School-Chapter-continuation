/**
 * Single source of truth for the gen.proportion.ratio task -> objective mapping (owner A, C, D).
 * Every specification section, objective record, solver, validator, parser/checker, fixture, review-pack
 * record, and registry entry MUST use exactly these twelve task slugs + twelve objective IDs — no
 * alternative spellings (no _UNITARY suffix). The Python oracle mirrors this verbatim
 * (oracle/spi_oracle/ratio.py: OBJECTIVE_BY_TASK) and a parity test asserts the two agree and that all
 * twelve IDs exist in curriculum/objectives/SPI.MIDDLE.RATIO.json.
 *
 * Domain `proportion`, strand `ratio-and-proportion`, objective segment `RATIO` (owner A).
 * Interaction is FREE-RESPONSE-first; only the six MC_ELIGIBLE_TASKS support multiple-choice, and
 * best_buy is MULTIPLE-CHOICE-ONLY (owner C). An explicit MC request for an MC-ineligible task raises an
 * interaction-not-supported error (never a silent free-response substitution).
 */

export const RATIO_TASKS = [
  "simplify",
  "write_from_quantities",
  "ratio_to_fraction",
  "fraction_to_ratio",
  "share_two_part",
  "share_three_part",
  "missing_part",
  "direct_proportion",
  "inverse_proportion",
  "unit_rate",
  "best_buy",
  "simple_scale",
] as const;

export type RatioTask = (typeof RATIO_TASKS)[number];

export const OBJECTIVE_BY_TASK: Record<RatioTask, string> = {
  simplify: "SPI.MIDDLE.RATIO.SIMPLIFY.01",
  write_from_quantities: "SPI.MIDDLE.RATIO.WRITE_FROM_QUANTITIES.01",
  ratio_to_fraction: "SPI.MIDDLE.RATIO.RATIO_TO_FRACTION.01",
  fraction_to_ratio: "SPI.MIDDLE.RATIO.FRACTION_TO_RATIO.01",
  share_two_part: "SPI.MIDDLE.RATIO.SHARE_TWO_PART.01",
  share_three_part: "SPI.MIDDLE.RATIO.SHARE_THREE_PART.01",
  missing_part: "SPI.MIDDLE.RATIO.MISSING_PART.01",
  direct_proportion: "SPI.MIDDLE.RATIO.DIRECT_PROPORTION.01",
  inverse_proportion: "SPI.MIDDLE.RATIO.INVERSE_PROPORTION.01",
  unit_rate: "SPI.MIDDLE.RATIO.UNIT_RATE.01",
  best_buy: "SPI.MIDDLE.RATIO.BEST_BUY.01",
  simple_scale: "SPI.MIDDLE.RATIO.SIMPLE_SCALE.01",
};

/** The twelve approved objective IDs, in task order. */
export const RATIO_OBJECTIVE_IDS: string[] = RATIO_TASKS.map((t) => OBJECTIVE_BY_TASK[t]);

/** The objective answer types per task (owner D). best_buy is the only multiple-choice answer. */
export const ANSWER_TYPES_BY_TASK: Record<RatioTask, string[]> = {
  simplify: ["ratio"],
  write_from_quantities: ["ratio"],
  ratio_to_fraction: ["exact-rational"],
  fraction_to_ratio: ["ratio"],
  share_two_part: ["table-completion"],
  share_three_part: ["table-completion"],
  missing_part: ["integer"],
  direct_proportion: ["integer", "exact-rational"],
  inverse_proportion: ["integer"],
  unit_rate: ["integer", "exact-rational"],
  best_buy: ["multiple-choice"],
  simple_scale: ["integer", "exact-rational"],
};

/** Tasks that may be presented as multiple-choice (owner C). best_buy is MC-ONLY. */
export const MC_ELIGIBLE_TASKS: RatioTask[] = [
  "simplify", "ratio_to_fraction", "fraction_to_ratio", "direct_proportion", "inverse_proportion", "best_buy",
];

/** best_buy supports ONLY multiple-choice in v1.0.0 (owner C/D). */
export const MC_ONLY_TASKS: RatioTask[] = ["best_buy"];

/** Supported interactions per task (owner C). FR-first; the MC-eligible add multiple-choice; best_buy is MC-only. */
export const SUPPORTED_INTERACTIONS_BY_TASK: Record<RatioTask, string[]> = Object.fromEntries(
  RATIO_TASKS.map((t) => {
    if (MC_ONLY_TASKS.includes(t)) return [t, ["multiple-choice"]];
    return [t, MC_ELIGIBLE_TASKS.includes(t) ? ["free-response", "multiple-choice"] : ["free-response"]];
  }),
) as Record<RatioTask, string[]>;
