/**
 * Single source of truth for the gen.stats.data-handling task -> objective mapping
 * (owner decision A). Every specification section, objective record, descriptor,
 * validator, fixture, review-pack record, and registry entry MUST use exactly these
 * IDs — no alternative spellings. The Python oracle mirrors this map verbatim
 * (oracle/spi_oracle/data_handling.py: OBJECTIVE_BY_TASK) and a parity test asserts
 * the two agree and that all eleven IDs exist in curriculum/objectives/SPI.MIDDLE.STAT.json.
 */

export const STAT_TASKS = [
  "read_bar_chart",
  "read_pictogram",
  "read_table_value",
  "read_line_graph",
  "complete_frequency_table",
  "mean_from_list",
  "median_from_list",
  "mode_from_list",
  "range_from_list",
  "mean_from_freq_table",
  "single_event_probability",
] as const;

export type StatTask = (typeof STAT_TASKS)[number];

export const OBJECTIVE_BY_TASK: Record<StatTask, string> = {
  read_bar_chart: "SPI.MIDDLE.STAT.READ.BAR_CHART.01",
  read_pictogram: "SPI.MIDDLE.STAT.READ.PICTOGRAM.01",
  read_table_value: "SPI.MIDDLE.STAT.READ.TABLE_VALUE.01",
  read_line_graph: "SPI.MIDDLE.STAT.READ.LINE_GRAPH.01",
  complete_frequency_table: "SPI.MIDDLE.STAT.FREQ.COMPLETE_TABLE.01",
  mean_from_list: "SPI.MIDDLE.STAT.AVG.MEAN_LIST.01",
  median_from_list: "SPI.MIDDLE.STAT.AVG.MEDIAN_LIST.01",
  mode_from_list: "SPI.MIDDLE.STAT.AVG.MODE_LIST.01",
  range_from_list: "SPI.MIDDLE.STAT.AVG.RANGE_LIST.01",
  mean_from_freq_table: "SPI.MIDDLE.STAT.AVG.MEAN_FREQ_TABLE.01",
  single_event_probability: "SPI.MIDDLE.STAT.PROB.SINGLE_EVENT.01",
};

/** The eleven approved objective IDs, in task order. */
export const STAT_OBJECTIVE_IDS: string[] = STAT_TASKS.map((t) => OBJECTIVE_BY_TASK[t]);

/** Tasks that are free-response only in v1.0.0 (never offered as multiple-choice). */
export const FREE_RESPONSE_ONLY_TASKS: StatTask[] = ["complete_frequency_table"];
