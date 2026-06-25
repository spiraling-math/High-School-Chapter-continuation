/**
 * MISC.STAT.* misconception registry for gen.stats.data-handling (TypeScript mirror).
 *
 * Byte-for-byte behavioural mirror of oracle/spi_oracle/data_handling_misconceptions.py.
 * Each rule has a stable id, a human title, a `formula` (the wrong rule, in words), a
 * `description` (internal), an `observableError` (no internal symbols), `feedback`
 * (phrased from displayed values), and a deterministic `adapter` that recomputes the wrong
 * value from a context dict. The oracle supplies the context via _ctx(); adapters read what
 * they need and return the wrong value (an integer, a Rational, or null when N/A).
 *
 * Distractor discipline (owner N): a distractor value must be DISTINCT from the correct
 * answer and from the other distractors; probability distractors must lie in [0, 1] and
 * must never be an unreduced form of the correct probability; a mode distractor must never
 * return the correct mode; no statistic-as-distractor may equal the correct statistic.
 */

import { Rational } from "../../core/exact-math/rational.ts";

// A context value is either an exact integer (number) or a Rational. The `correct`
// answer is an integer for reading/integer tasks and a Rational for rational/fraction tasks.
export type CtxValue = number | Rational;
export type AdapterValue = number | Rational | null;

// The context is dynamically keyed per task; each adapter reads the keys its task provides.
export type Ctx = {
  correct: CtxValue;
  values?: number[];
  queryIndex?: number;
  total?: number;
  axisStep?: number;
  minorStep?: number;
  majorStep?: number;
  key?: number;
  halfPresent?: boolean;
  xValue?: number;
  otherSum?: number;
  sortedVals?: number[];
  n?: number;
  listSum?: number;
  maxv?: number;
  minv?: number;
  uniqueMode?: number | null;
  modeFrequency?: number | null;
  midrange?: Rational;
  meanValue?: Rational;
  medianValue?: Rational;
  sumVF?: number;
  sumf?: number;
  nCats?: number;
  sumValues?: number;
  favourable?: number;
  probTotal?: number;
};

const F = (x: number): Rational => new Rational(x, 1);

// Cross-type exact comparisons (mirror Python's `int`/`Fraction` `==`/`<=` semantics).
function asRat(v: CtxValue): Rational {
  return v instanceof Rational ? v : F(v);
}
function eqVal(a: CtxValue, b: CtxValue): boolean {
  return asRat(a).equals(asRat(b));
}
function neVal(a: CtxValue, b: CtxValue): boolean {
  return !eqVal(a, b);
}

// 0 <= v <= 1 for a Rational v (den > 0 by Rational's invariant).
function le01(v: Rational): boolean {
  if (v.num < 0) return false;
  // v <= 1  <=>  v.num <= v.den (den > 0, num >= 0)
  return v.num <= v.den;
}

// --------------------------------------------------------------------------- //
// Adapters — each returns the wrong value (number or Rational) or null if N/A.
// --------------------------------------------------------------------------- //
function adjCategory(c: Ctx): AdapterValue {
  const vals = c.values!;
  const i = c.queryIndex!;
  const nxt = i + 1 < vals.length ? vals[i + 1]! : (i - 1 >= 0 ? vals[i - 1]! : null);
  return nxt !== null && neVal(nxt, c.correct) ? nxt : null;
}

function offByStep(c: Ctx): AdapterValue {
  const step = c.axisStep ?? 1;
  const v = (c.correct as number) + step;
  return v !== (c.correct as number) ? v : null;
}

function miscountScale(c: Ctx): AdapterValue {
  const step = c.axisStep ?? 1;
  const correct = c.correct as number;
  if (step <= 1 || correct % step !== 0) return null;
  const v = Math.floor(correct / step);
  return v !== correct ? v : null;
}

function offByMajor(c: Ctx): AdapterValue {
  // Reads one MAJOR gridline off (distinct from one MINOR subdivision off).
  const step = c.majorStep ?? 1;
  if (step <= (c.minorStep ?? 1)) return null;
  const correct = c.correct as number;
  const v = correct + step;
  return v !== correct ? v : null;
}

function pictoCountSymbols(c: Ctx): AdapterValue {
  const key = c.key;
  if (!key || key <= 1) return null;
  // Owner #3, policy B: the exact whole-symbol count is an integer ONLY when the queried
  // category has no half symbol. When a half is present, the symbol count is non-integer
  // (e.g. 5½), so this rule is INAPPLICABLE and must not return a misleading floored value.
  if (c.halfPresent) return null;
  const correct = c.correct as number;
  const v = Math.floor(correct / key);
  return v !== correct ? v : null;
}

function pictoHalfAsWhole(c: Ctx): AdapterValue {
  if (!c.halfPresent) return null;
  const key = c.key ?? 0;
  const correct = c.correct as number;
  const v = correct + Math.floor(key / 2);  // counts the half symbol as a whole one
  return v !== correct ? v : null;
}

function pictoOffByOneSymbol(c: Ctx): AdapterValue {
  const key = c.key ?? 0;
  if (!key) return null;
  const correct = c.correct as number;
  const v = correct - key;  // miscounts by one whole symbol
  return v !== correct && v >= 0 ? v : null;
}

function pictoIgnoreHalf(c: Ctx): AdapterValue {
  if (!c.halfPresent) return null;
  const key = c.key ?? 0;
  const correct = c.correct as number;
  const v = correct - Math.floor(key / 2);
  return v !== correct && v >= 0 ? v : null;
}

function tableReadsTotal(c: Ctx): AdapterValue {
  const t = c.total;
  return t !== undefined && t !== null && t !== (c.correct as number) ? t : null;
}

function lineSwapsAxes(c: Ctx): AdapterValue {
  const xv = c.xValue;
  return xv !== undefined && xv !== null && xv !== (c.correct as number) ? xv : null;
}

function tableReadsLargest(c: Ctx): AdapterValue {
  const vals = c.values;
  if (!vals || vals.length === 0) return null;
  const mx = Math.max(...vals);
  return mx !== (c.correct as number) ? mx : null;
}

function freqSubtractWrong(c: Ctx): AdapterValue {
  const other = c.otherSum;
  const total = c.total;
  if (other === undefined || other === null || total === undefined || total === null) return null;
  const v = total + other;
  return v !== (c.correct as number) ? v : null;
}

function freqIgnoresTotal(c: Ctx): AdapterValue {
  const other = c.otherSum;
  return other !== undefined && other !== null && other !== (c.correct as number) ? other : null;
}

function meanNoDivide(c: Ctx): AdapterValue {
  const s = c.listSum;
  if (s === undefined || s === null) return null;
  return neVal(F(s), c.correct) ? F(s) : null;
}

function meanDivideWrongN(c: Ctx): AdapterValue {
  const s = c.listSum;
  const n = c.n;
  if (s === undefined || s === null || !n || n <= 1) return null;
  const v = new Rational(s, n - 1);
  return neVal(v, c.correct) ? v : null;
}

function usesMode(c: Ctx): AdapterValue {
  // Eligible ONLY when the dataset has a UNIQUE mode (owner #2). uniqueMode is null when
  // every value occurs equally often or two+ values tie for the greatest frequency.
  const m = c.uniqueMode;
  return m !== undefined && m !== null && neVal(F(m), c.correct) ? F(m) : null;
}

function midrange(c: Ctx): AdapterValue {
  const mr = c.midrange;
  return mr !== undefined && mr !== null && neVal(mr, c.correct) ? mr : null;
}

function usesMean(c: Ctx): AdapterValue {
  const mv = c.meanValue;
  return mv !== undefined && mv !== null && neVal(mv, c.correct) ? mv : null;
}

function rangeIsMin(c: Ctx): AdapterValue {
  const mn = c.minv;
  return mn !== undefined && mn !== null && mn !== (c.correct as number) ? mn : null;
}

function usesMedian(c: Ctx): AdapterValue {
  const md = c.medianValue;
  return md !== undefined && md !== null && neVal(md, c.correct) ? md : null;
}

function medianNoOrder(c: Ctx): AdapterValue {
  const vals = c.values;
  if (!vals || vals.length === 0) return null;
  const n = vals.length;
  const mid = n % 2
    ? F(vals[Math.floor(n / 2)]!)
    : new Rational(vals[Math.floor(n / 2) - 1]! + vals[Math.floor(n / 2)]!, 2);
  return neVal(mid, c.correct) ? mid : null;
}

function medianWrongMiddle(c: Ctx): AdapterValue {
  const sv = c.sortedVals;
  if (!sv || sv.length % 2 === 1) return null;
  const v = F(sv[Math.floor(sv.length / 2) - 1]!);
  return neVal(v, c.correct) ? v : null;
}

function modeUsesHighest(c: Ctx): AdapterValue {
  const mx = c.maxv;
  return mx !== undefined && mx !== null && mx !== (c.correct as number) ? mx : null;
}

function modeUsesFrequency(c: Ctx): AdapterValue {
  const f = c.modeFrequency;
  return f !== undefined && f !== null && f !== (c.correct as number) ? f : null;
}

function rangeIsMax(c: Ctx): AdapterValue {
  const mx = c.maxv;
  return mx !== undefined && mx !== null && mx !== (c.correct as number) ? mx : null;
}

function rangeAdds(c: Ctx): AdapterValue {
  const mx = c.maxv;
  const mn = c.minv;
  if (mx === undefined || mx === null || mn === undefined || mn === null) return null;
  const v = mx + mn;
  return v !== (c.correct as number) ? v : null;
}

function meanftDivideByCategories(c: Ctx): AdapterValue {
  const svf = c.sumVF;
  const ncat = c.nCats;
  if (svf === undefined || svf === null || !ncat) return null;
  const v = new Rational(svf, ncat);
  return neVal(v, c.correct) ? v : null;
}

function meanftNoWeight(c: Ctx): AdapterValue {
  const sv = c.sumValues;
  const ncat = c.nCats;
  if (sv === undefined || sv === null || !ncat) return null;
  const v = new Rational(sv, ncat);
  return neVal(v, c.correct) ? v : null;
}

function probComplement(c: Ctx): AdapterValue {
  const fav = c.favourable;
  const tot = c.probTotal;
  if (fav === undefined || fav === null || !tot) return null;
  const v = new Rational(tot - fav, tot);
  return neVal(v, c.correct) && le01(v) ? v : null;
}

function probOdds(c: Ctx): AdapterValue {
  const fav = c.favourable;
  const tot = c.probTotal;
  if (fav === undefined || fav === null || !tot) return null;
  const fail = tot - fav;
  if (fail <= 0) return null;
  const v = new Rational(fav, fail);
  return neVal(v, c.correct) && le01(v) ? v : null;
}

function probOffByOne(c: Ctx): AdapterValue {
  const fav = c.favourable;
  const tot = c.probTotal;
  if (fav === undefined || fav === null || !tot) return null;
  const cand = fav - 1 >= 0 ? fav - 1 : fav + 1;
  if (cand < 0 || cand > tot) return null;
  const v = new Rational(cand, tot);
  return neVal(v, c.correct) && le01(v) ? v : null;
}

// --------------------------------------------------------------------------- //
// Registry
// --------------------------------------------------------------------------- //
export interface Misconception {
  id: string;
  title: string;
  formula: string;
  description: string;
  observableError: string;
  feedback: string;
  adapter: (c: Ctx) => AdapterValue;
}

function r(
  id: string,
  title: string,
  formula: string,
  description: string,
  observable: string,
  feedback: string,
  adapter: (c: Ctx) => AdapterValue,
): Misconception {
  return { id, title, formula, description, observableError: observable, feedback, adapter };
}

const RULES: Misconception[] = [
  r("MISC.STAT.READ_OFF_BY_STEP", "Misreads by one scale step",
    "value +/- one axis step", "reads the bar/point one gridline off",
    "Reads the value one step up or down the scale.",
    "Check which gridline the top of the bar (or the point) lines up with, and read it off the scale carefully.",
    offByStep),
  r("MISC.STAT.READ_WRONG_CATEGORY", "Reads the wrong category",
    "value of an adjacent category", "reads a neighbouring category instead of the named one",
    "Reads the frequency of a neighbouring category.",
    "Find the bar or row labelled with the category you were asked about before reading its value.",
    adjCategory),
  r("MISC.STAT.READ_MISCOUNT_SCALE", "Counts squares, not the scale",
    "value / axis step", "counts gridline squares as one unit each",
    "Counts the squares instead of using the scale on the axis.",
    "Each square is worth more than one — use the numbers printed on the axis, not the number of squares.",
    miscountScale),
  r("MISC.STAT.PICTO_COUNTS_SYMBOLS", "Counts symbols, ignores the key",
    "number of symbols", "reports the symbol count, not the value it represents",
    "Counts the symbols without using the key.",
    "Each symbol stands for more than one — multiply the symbols by the number in the key.",
    pictoCountSymbols),
  r("MISC.STAT.PICTO_IGNORES_HALF", "Ignores the half symbol",
    "value - half-symbol contribution", "drops the part-symbol's value",
    "Leaves out the value of the half symbol.",
    "A half symbol is worth half of the key — remember to add it in.",
    pictoIgnoreHalf),
  r("MISC.STAT.TABLE_READS_TOTAL", "Reads the total row",
    "the total", "reads the total instead of the category frequency",
    "Reads the total instead of the row that was asked for.",
    "Read across to the row for the named category, not the total row.",
    tableReadsTotal),
  r("MISC.STAT.TABLE_ADJACENT_ROW", "Reads an adjacent row",
    "value of an adjacent row", "reads the row above or below the named one",
    "Reads the frequency from the wrong row of the table.",
    "Line up the category name with its own row before reading the frequency.",
    adjCategory),
  r("MISC.STAT.TABLE_READS_LARGEST", "Reads the largest frequency",
    "the largest frequency in the table", "reads the biggest number instead of the named row",
    "Reads the largest frequency in the table instead of the named category.",
    "Read the frequency from the row for the category you were asked about, not the biggest number.",
    tableReadsLargest),
  r("MISC.STAT.LINE_SWAPS_AXES", "Swaps the axes",
    "the x-value instead of the y-value", "reads the time/position instead of the value",
    "Reads the value off the horizontal axis instead of the vertical axis.",
    "Read up to the marked point, then across to the vertical axis for its value.",
    lineSwapsAxes),
  r("MISC.STAT.FREQ_SUBTRACT_WRONG_WAY", "Adds instead of subtracting",
    "total + other frequencies", "adds when the missing value should be found by subtracting",
    "Adds the known frequencies to the total instead of subtracting.",
    "The frequencies add up to the total, so subtract the ones you know from the total.",
    freqSubtractWrong),
  r("MISC.STAT.FREQ_IGNORES_TOTAL", "Ignores the total",
    "sum of the other frequencies", "uses the other frequencies but forgets the total",
    "Adds up the other frequencies but ignores the given total.",
    "Use the total: the missing frequency is the total minus the frequencies you already have.",
    freqIgnoresTotal),
  r("MISC.STAT.MEAN_NO_DIVIDE", "Forgets to divide",
    "sum of the values", "reports the total instead of the mean",
    "Adds the values but forgets to divide by how many there are.",
    "After adding the values, divide by how many values there are.",
    meanNoDivide),
  r("MISC.STAT.MEAN_DIVIDE_WRONG_N", "Divides by the wrong count",
    "sum / (n - 1)", "divides by one fewer than the number of values",
    "Divides by the wrong number of values.",
    "Divide the total by exactly how many values are in the list.",
    meanDivideWrongN),
  r("MISC.STAT.AVG_USES_MODE", "Uses the mode instead",
    "the mode", "confuses this average with the mode",
    "Gives the most common value instead of the one asked for.",
    "This question asks for a different average — work it out rather than giving the most common value.",
    usesMode),
  r("MISC.STAT.MEDIAN_NO_ORDER", "Finds the middle without ordering",
    "middle of the unordered list", "takes the middle term before sorting",
    "Takes the middle value without putting the list in order first.",
    "Put the values in order from smallest to largest before finding the middle.",
    medianNoOrder),
  r("MISC.STAT.MEDIAN_WRONG_MIDDLE", "Takes one middle value (even list)",
    "lower of the two middle values", "uses one middle value instead of averaging both",
    "Picks one of the two middle values instead of their average.",
    "With an even number of values, the median is halfway between the two middle ones.",
    medianWrongMiddle),
  r("MISC.STAT.AVG_USES_MEDIAN", "Uses the median instead",
    "the median", "confuses the mode with the median",
    "Gives the middle value instead of the most common one.",
    "The mode is the value that appears most often, not the middle value.",
    usesMedian),
  r("MISC.STAT.MODE_USES_HIGHEST", "Picks the largest value",
    "the largest value", "confuses 'most common' with 'largest'",
    "Gives the largest value instead of the most common one.",
    "The mode is the value that appears most often, not the biggest value.",
    modeUsesHighest),
  r("MISC.STAT.MODE_USES_FREQUENCY", "Reports how often, not which value",
    "the highest frequency", "reports the count instead of the value",
    "Gives how many times the mode occurs instead of the value itself.",
    "The mode is the value that occurs most often, not the number of times it occurs.",
    modeUsesFrequency),
  r("MISC.STAT.RANGE_IS_MAX", "Range is the largest value",
    "the largest value", "reports the maximum as the range",
    "Gives the largest value instead of the difference.",
    "The range is the largest value minus the smallest value.",
    rangeIsMax),
  r("MISC.STAT.RANGE_ADDS", "Adds the extremes",
    "largest + smallest", "adds instead of subtracting",
    "Adds the largest and smallest values instead of subtracting.",
    "The range is largest minus smallest, not largest plus smallest.",
    rangeAdds),
  r("MISC.STAT.MEANFT_DIVIDE_BY_CATEGORIES", "Divides by number of categories",
    "sum(value x frequency) / number of categories", "divides by categories, not total frequency",
    "Divides the total by the number of rows instead of the total frequency.",
    "Divide by the total frequency (the sum of the frequencies), not the number of rows.",
    meanftDivideByCategories),
  r("MISC.STAT.MEANFT_NO_WEIGHT", "Forgets to weight by frequency",
    "sum(values) / number of categories", "averages the values, ignoring frequency",
    "Averages the listed values without using the frequencies.",
    "Multiply each value by its frequency before adding, then divide by the total frequency.",
    meanftNoWeight),
  r("MISC.STAT.PROB_COMPLEMENT", "Counts the wrong outcomes",
    "(total - favourable) / total", "finds the probability of the event NOT happening",
    "Counts the outcomes that are not wanted instead of the ones that are.",
    "Count the favourable outcomes (the ones the question asks about) over the total.",
    probComplement),
  r("MISC.STAT.PROB_ODDS", "Writes odds, not probability",
    "favourable / unfavourable", "compares wanted to unwanted instead of to the total",
    "Compares wanted outcomes to unwanted outcomes instead of to the total.",
    "Probability is favourable outcomes over the TOTAL number of outcomes.",
    probOdds),
  r("MISC.STAT.PROB_OFF_BY_ONE", "Miscounts the favourable outcomes",
    "(favourable -/+ 1) / total", "counts one too few or too many favourable outcomes",
    "Counts one too few or one too many of the wanted outcomes.",
    "Recount the favourable outcomes carefully before writing the fraction.",
    probOffByOne),
  // Feedback-only rule (never an MC distractor — an unreduced form is an equivalent value).
  r("MISC.STAT.PROB_UNREDUCED", "Leaves the fraction unsimplified",
    "favourable / total, not simplified", "correct value but not in simplest form",
    "Writes a correct but unsimplified fraction.",
    "Your value is equivalent, but simplify the fraction to its simplest form.",
    () => null),
  // --- v1.0.1 additions (owner #2/#3/#4) --------------------------------- //
  r("MISC.STAT.MEAN_MIDRANGE", "Uses the midrange instead of the mean",
    "(largest + smallest) / 2", "averages only the extremes",
    "Averages only the largest and smallest values instead of all of them.",
    "The mean uses every value, not only the largest and smallest.",
    midrange),
  r("MISC.STAT.MEDIAN_USES_MEAN", "Uses the mean instead of the median",
    "the mean", "confuses the median with the mean",
    "Adds the values and divides instead of finding the middle value.",
    "The median is the middle value of the ordered list, not the mean.",
    usesMean),
  r("MISC.STAT.MEDIAN_MIDRANGE", "Uses the midrange instead of the median",
    "(largest + smallest) / 2", "averages the extremes instead of finding the middle",
    "Averages the largest and smallest values instead of finding the middle.",
    "The median is the middle value of the ordered list, not the average of the extremes.",
    midrange),
  r("MISC.STAT.RANGE_IS_MIN", "Range is the smallest value",
    "the smallest value", "reports the minimum as the range",
    "Gives the smallest value instead of the difference.",
    "The range is the largest value minus the smallest value.",
    rangeIsMin),
  r("MISC.STAT.PICTO_HALF_AS_WHOLE", "Counts the half symbol as a whole",
    "value + half-symbol's worth", "treats the part symbol as a full one",
    "Counts the half symbol as if it were a whole symbol.",
    "A half symbol is worth half of the key, not a whole one.",
    pictoHalfAsWhole),
  r("MISC.STAT.PICTO_OFF_BY_ONE_SYMBOL", "Miscounts by one symbol",
    "value - one symbol's worth", "counts one symbol too few",
    "Counts one symbol too few when reading the row.",
    "Count the symbols in the row carefully, then multiply by the key.",
    pictoOffByOneSymbol),
  // Free-response missing-TOTAL diagnostics (owner #4) — feedback-only, applicable only when
  // the total is the unknown. Never claim to subtract from a total that is itself missing.
  r("MISC.STAT.FREQ_TOTAL_OMITS_CATEGORY", "Omits a category from the total",
    "sum of all but one frequency", "leaves one frequency out when adding",
    "Leaves a category out when adding up the total.",
    "Add every category's frequency — don't miss one out.",
    () => null),
  r("MISC.STAT.FREQ_TOTAL_COPIES_ONE", "Copies one frequency as the total",
    "one of the frequencies", "writes a single frequency as the total",
    "Writes one of the frequencies as the total instead of their sum.",
    "The total is the sum of all the frequencies, not a single one of them.",
    () => null),
  // --- v1.0.2 addition (direct-read scale) ------------------------------ //
  r("MISC.STAT.READ_OFF_BY_MAJOR_STEP", "Reads one major gridline off",
    "value +/- one major step", "lands on the wrong labelled gridline",
    "Reads the value one whole labelled gridline up or down.",
    "Read carefully to the exact gridline the bar or point reaches.",
    offByMajor),
];

export const MISCONCEPTIONS: Record<string, Misconception> = Object.fromEntries(
  RULES.map((m) => [m.id, m]),
);

// Which misconception ids each task may draw distractors from (order = preference).
export const RULES_BY_TASK: Record<string, string[]> = {
  read_bar_chart: ["MISC.STAT.READ_OFF_BY_STEP", "MISC.STAT.READ_WRONG_CATEGORY", "MISC.STAT.READ_MISCOUNT_SCALE", "MISC.STAT.READ_OFF_BY_MAJOR_STEP"],
  // Whole-symbol count first; the half-symbol rules are mutually exclusive with it (owner #3);
  // off-by-one is a fallback so a 3rd distinct distractor always exists.
  read_pictogram: ["MISC.STAT.PICTO_COUNTS_SYMBOLS", "MISC.STAT.PICTO_IGNORES_HALF",
    "MISC.STAT.PICTO_HALF_AS_WHOLE", "MISC.STAT.READ_WRONG_CATEGORY",
    "MISC.STAT.PICTO_OFF_BY_ONE_SYMBOL"],
  read_table_value: ["MISC.STAT.TABLE_READS_TOTAL", "MISC.STAT.TABLE_ADJACENT_ROW", "MISC.STAT.TABLE_READS_LARGEST"],
  read_line_graph: ["MISC.STAT.READ_OFF_BY_STEP", "MISC.STAT.LINE_SWAPS_AXES", "MISC.STAT.READ_MISCOUNT_SCALE", "MISC.STAT.READ_OFF_BY_MAJOR_STEP"],
  // complete_frequency_table is free-response only — no distractors; its rules appear as
  // blank-kind-specific solution pitfalls (missing-total vs missing-frequency, owner #4).
  complete_frequency_table: ["MISC.STAT.FREQ_SUBTRACT_WRONG_WAY", "MISC.STAT.FREQ_IGNORES_TOTAL",
    "MISC.STAT.FREQ_TOTAL_OMITS_CATEGORY", "MISC.STAT.FREQ_TOTAL_COPIES_ONE"],
  // AVG_USES_MODE is PREFERRED when a unique mode exists; midrange/min/mean fallbacks guarantee
  // three distinct, mathematically-true distractors when there is no mode (owner #2).
  mean_from_list: ["MISC.STAT.MEAN_NO_DIVIDE", "MISC.STAT.MEAN_DIVIDE_WRONG_N", "MISC.STAT.AVG_USES_MODE", "MISC.STAT.MEAN_MIDRANGE"],
  median_from_list: ["MISC.STAT.MEDIAN_NO_ORDER", "MISC.STAT.MEDIAN_WRONG_MIDDLE", "MISC.STAT.AVG_USES_MODE", "MISC.STAT.MEDIAN_USES_MEAN", "MISC.STAT.MEDIAN_MIDRANGE"],
  mode_from_list: ["MISC.STAT.MODE_USES_HIGHEST", "MISC.STAT.MODE_USES_FREQUENCY", "MISC.STAT.AVG_USES_MEDIAN"],
  range_from_list: ["MISC.STAT.RANGE_IS_MAX", "MISC.STAT.RANGE_ADDS", "MISC.STAT.AVG_USES_MODE", "MISC.STAT.RANGE_IS_MIN"],
  mean_from_freq_table: ["MISC.STAT.MEANFT_DIVIDE_BY_CATEGORIES", "MISC.STAT.MEANFT_NO_WEIGHT", "MISC.STAT.MEAN_DIVIDE_WRONG_N"],
  single_event_probability: ["MISC.STAT.PROB_COMPLEMENT", "MISC.STAT.PROB_ODDS", "MISC.STAT.PROB_OFF_BY_ONE"],
};

export function rulesFor(task: string): string[] {
  return RULES_BY_TASK[task] ?? [];
}

export function adapterFor(mid: string): (c: Ctx) => AdapterValue {
  return MISCONCEPTIONS[mid]!.adapter;
}
