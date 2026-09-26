/**
 * Single source of truth for the gen.functions.foundations task -> objective mapping.
 * Every specification section, objective record, generator, validator, fixture, review-pack record and
 * registry entry MUST use exactly these eleven task slugs + eleven objective IDs. The Python oracle mirrors
 * this verbatim (oracle/spi_oracle/functions.py: OBJECTIVE_BY_TASK) and a test asserts the two agree and that
 * all eleven IDs exist in curriculum/objectives/SPI.IBDPAASL.FUNC.json (reviewStatus: proposed).
 *
 * Stage ibdp-aasl, domain `functions` (ID segment FUNC), strand `introducing-functions`. Every task supports
 * free-response and multiple-choice except identify_function, which is MULTIPLE-CHOICE-ONLY (an explicit
 * free-response request raises interaction-not-supported, never a silent substitution).
 */

export const FUNCTIONS_TASKS = [
  "identify_function",
  "evaluate_function",
  "solve_for_input",
  "domain_of_function",
  "range_of_function",
  "composite_value",
  "composite_expression",
  "function_from_composite",
  "inverse_value",
  "inverse_expression",
  "one_to_one_restriction",
] as const;

export type FunctionsTask = (typeof FUNCTIONS_TASKS)[number];

export const OBJECTIVE_BY_TASK: Record<FunctionsTask, string> = {
  identify_function: "SPI.IBDPAASL.FUNC.IDENTIFY_FUNCTION.01",
  evaluate_function: "SPI.IBDPAASL.FUNC.EVALUATE.01",
  solve_for_input: "SPI.IBDPAASL.FUNC.SOLVE_FOR_INPUT.01",
  domain_of_function: "SPI.IBDPAASL.FUNC.DOMAIN.01",
  range_of_function: "SPI.IBDPAASL.FUNC.RANGE.01",
  composite_value: "SPI.IBDPAASL.FUNC.COMPOSITE_VALUE.01",
  composite_expression: "SPI.IBDPAASL.FUNC.COMPOSITE_EXPRESSION.01",
  function_from_composite: "SPI.IBDPAASL.FUNC.FUNCTION_FROM_COMPOSITE.01",
  inverse_value: "SPI.IBDPAASL.FUNC.INVERSE_VALUE.01",
  inverse_expression: "SPI.IBDPAASL.FUNC.INVERSE_EXPRESSION.01",
  one_to_one_restriction: "SPI.IBDPAASL.FUNC.ONE_TO_ONE_RESTRICTION.01",
};

/** The eleven objective IDs, in task order. */
export const FUNCTIONS_OBJECTIVE_IDS: string[] = FUNCTIONS_TASKS.map((t) => OBJECTIVE_BY_TASK[t]);

/** The free-response answer family per task (MC items keep the same mathematical type; identify_function's
 *  mathematics IS the selection, so it is `multiple-choice`). */
export const ANSWER_TYPES_BY_TASK: Record<FunctionsTask, string[]> = {
  identify_function: ["multiple-choice"],
  evaluate_function: ["integer", "exact-rational"],
  solve_for_input: ["integer", "exact-rational"],
  domain_of_function: ["interval"],
  range_of_function: ["interval"],
  composite_value: ["integer", "exact-rational"],
  composite_expression: ["algebraic-expression"],
  function_from_composite: ["algebraic-expression"],
  inverse_value: ["integer", "exact-rational"],
  inverse_expression: ["algebraic-expression"],
  one_to_one_restriction: ["integer", "exact-rational"],
};

/** Tasks that support ONLY multiple-choice. */
export const MC_ONLY_TASKS: FunctionsTask[] = ["identify_function"];

/** Declared difficulty band range per task (every band in the range must be reachable). */
export const TASK_BANDS: Record<FunctionsTask, [number, number]> = {
  identify_function: [1, 2], evaluate_function: [1, 3], solve_for_input: [2, 3], domain_of_function: [2, 4],
  range_of_function: [3, 5], composite_value: [2, 3], composite_expression: [3, 5], function_from_composite: [4, 5],
  inverse_value: [2, 4], inverse_expression: [3, 4], one_to_one_restriction: [4, 5],
};

export function supportedInteractions(task: string): string[] {
  return (MC_ONLY_TASKS as string[]).includes(task) ? ["multiple-choice"] : ["free-response", "multiple-choice"];
}
