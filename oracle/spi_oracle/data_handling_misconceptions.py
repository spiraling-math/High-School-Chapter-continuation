"""MISC.STAT.* misconception registry for gen.stats.data-handling (owner decision N).

Each rule has: a stable id, a human title, a `formula` (the wrong rule, in words),
a `description` (internal), an `observableError` (no internal symbols), `feedback`
(phrased from displayed values, no internal symbols), and a deterministic `adapter`
that recomputes the wrong value from a context dict. An `applies` predicate decides
eligibility for a given context. The TypeScript mirror reproduces this registry and the
validator independently recomputes each distractor through the same adapter.

Distractor discipline (owner N):
  * a distractor value must be DISTINCT from the correct answer and from the other
    distractors; if three valid distinct distractors cannot be produced the generator
    redraws (never pads with arbitrary nearby numbers);
  * probability distractors must lie in [0, 1] and must never be an unreduced form of
    the correct probability (that is an equivalent value, surfaced only as feedback);
  * a mode distractor must never return the correct mode; no statistic-as-distractor may
    equal the correct statistic.
"""

from __future__ import annotations

from fractions import Fraction
from typing import Any, Callable, Dict, List, Optional


# --------------------------------------------------------------------------- #
# Adapters — each returns the wrong value (int or Fraction) or None if N/A.
# Context keys are supplied by the oracle's _ctx(); adapters read what they need.
# --------------------------------------------------------------------------- #
def _adj_category(c: Dict[str, Any]) -> Optional[int]:
    vals, i = c["values"], c["queryIndex"]
    nxt = vals[i + 1] if i + 1 < len(vals) else (vals[i - 1] if i - 1 >= 0 else None)
    return nxt if (nxt is not None and nxt != c["correct"]) else None


def _off_by_step(c: Dict[str, Any]) -> Optional[int]:
    step = c.get("axisStep", 1)
    v = c["correct"] + step
    return v if v != c["correct"] else None


def _miscount_scale(c: Dict[str, Any]) -> Optional[int]:
    step = c.get("axisStep", 1)
    if step <= 1 or c["correct"] % step != 0:
        return None
    v = c["correct"] // step
    return v if v != c["correct"] else None


def _picto_count_symbols(c: Dict[str, Any]) -> Optional[int]:
    key = c.get("key")
    if not key or key <= 1:
        return None
    # Owner #3, policy B: the exact whole-symbol count is an integer ONLY when the queried
    # category has no half symbol. When a half is present, the symbol count is non-integer
    # (e.g. 5½), so this rule is INAPPLICABLE and must not return a misleading floored value.
    if c.get("halfPresent"):
        return None
    v = c["correct"] // key
    return v if v != c["correct"] else None


def _picto_half_as_whole(c: Dict[str, Any]) -> Optional[int]:
    if not c.get("halfPresent"):
        return None
    key = c.get("key", 0)
    v = c["correct"] + key // 2          # counts the half symbol as a whole one
    return v if v != c["correct"] else None


def _picto_off_by_one_symbol(c: Dict[str, Any]) -> Optional[int]:
    key = c.get("key", 0)
    if not key:
        return None
    v = c["correct"] - key               # miscounts by one whole symbol
    return v if (v != c["correct"] and v >= 0) else None


def _picto_ignore_half(c: Dict[str, Any]) -> Optional[int]:
    if not c.get("halfPresent"):
        return None
    key = c.get("key", 0)
    v = c["correct"] - key // 2
    return v if (v != c["correct"] and v >= 0) else None


def _table_reads_total(c: Dict[str, Any]) -> Optional[int]:
    t = c.get("total")
    return t if (t is not None and t != c["correct"]) else None


def _line_swaps_axes(c: Dict[str, Any]) -> Optional[int]:
    xv = c.get("xValue")
    return xv if (xv is not None and xv != c["correct"]) else None


def _table_reads_largest(c: Dict[str, Any]) -> Optional[int]:
    vals = c.get("values")
    if not vals:
        return None
    mx = max(vals)
    return mx if mx != c["correct"] else None


def _freq_subtract_wrong(c: Dict[str, Any]) -> Optional[int]:
    # adds the other frequencies to the total instead of subtracting
    other, total = c.get("otherSum"), c.get("total")
    if other is None or total is None:
        return None
    v = total + other
    return v if v != c["correct"] else None


def _freq_ignores_total(c: Dict[str, Any]) -> Optional[int]:
    other = c.get("otherSum")
    return other if (other is not None and other != c["correct"]) else None


def _mean_no_divide(c: Dict[str, Any]) -> Optional[Fraction]:
    s = c.get("listSum")
    return Fraction(s) if (s is not None and Fraction(s) != c["correct"]) else None


def _mean_divide_wrong_n(c: Dict[str, Any]) -> Optional[Fraction]:
    s, n = c.get("listSum"), c.get("n")
    if s is None or not n or n <= 1:
        return None
    v = Fraction(s, n - 1)
    return v if v != c["correct"] else None


def _uses_mode(c: Dict[str, Any]) -> Optional[Fraction]:
    # Eligible ONLY when the dataset has a UNIQUE mode (owner #2). uniqueMode is None when
    # every value occurs equally often or two+ values tie for the greatest frequency.
    m = c.get("uniqueMode")
    return Fraction(m) if (m is not None and Fraction(m) != c["correct"]) else None


def _midrange(c: Dict[str, Any]) -> Optional[Fraction]:
    mr = c.get("midrange")
    return mr if (mr is not None and mr != c["correct"]) else None


def _uses_mean(c: Dict[str, Any]) -> Optional[Fraction]:
    mv = c.get("meanValue")
    return mv if (mv is not None and mv != c["correct"]) else None


def _range_is_min(c: Dict[str, Any]) -> Optional[int]:
    mn = c.get("minv")
    return mn if (mn is not None and mn != c["correct"]) else None


def _uses_median(c: Dict[str, Any]) -> Optional[Fraction]:
    md = c.get("medianValue")
    return md if (md is not None and md != c["correct"]) else None


def _median_no_order(c: Dict[str, Any]) -> Optional[Fraction]:
    # middle of the UNORDERED list
    vals = c.get("values")
    if not vals:
        return None
    n = len(vals)
    mid = (Fraction(vals[n // 2]) if n % 2 else Fraction(vals[n // 2 - 1] + vals[n // 2], 2))
    return mid if mid != c["correct"] else None


def _median_wrong_middle(c: Dict[str, Any]) -> Optional[Fraction]:
    # for even n, picks the lower-middle value instead of the average of the two
    sv = c.get("sortedVals")
    if not sv or len(sv) % 2 == 1:
        return None
    v = Fraction(sv[len(sv) // 2 - 1])
    return v if v != c["correct"] else None


def _mode_uses_highest(c: Dict[str, Any]) -> Optional[int]:
    mx = c.get("maxv")
    return mx if (mx is not None and mx != c["correct"]) else None


def _mode_uses_frequency(c: Dict[str, Any]) -> Optional[int]:
    f = c.get("modeFrequency")
    return f if (f is not None and f != c["correct"]) else None


def _range_is_max(c: Dict[str, Any]) -> Optional[int]:
    mx = c.get("maxv")
    return mx if (mx is not None and mx != c["correct"]) else None


def _range_adds(c: Dict[str, Any]) -> Optional[int]:
    mx, mn = c.get("maxv"), c.get("minv")
    if mx is None or mn is None:
        return None
    v = mx + mn
    return v if v != c["correct"] else None


def _meanft_divide_by_categories(c: Dict[str, Any]) -> Optional[Fraction]:
    svf, ncat = c.get("sumVF"), c.get("nCats")
    if svf is None or not ncat:
        return None
    v = Fraction(svf, ncat)
    return v if v != c["correct"] else None


def _meanft_no_weight(c: Dict[str, Any]) -> Optional[Fraction]:
    sv, ncat = c.get("sumValues"), c.get("nCats")
    if sv is None or not ncat:
        return None
    v = Fraction(sv, ncat)
    return v if v != c["correct"] else None


def _prob_complement(c: Dict[str, Any]) -> Optional[Fraction]:
    fav, tot = c.get("favourable"), c.get("probTotal")
    if fav is None or not tot:
        return None
    v = Fraction(tot - fav, tot)
    return v if (v != c["correct"] and 0 <= v <= 1) else None


def _prob_odds(c: Dict[str, Any]) -> Optional[Fraction]:
    fav, tot = c.get("favourable"), c.get("probTotal")
    if fav is None or not tot:
        return None
    fail = tot - fav
    if fail <= 0:
        return None
    v = Fraction(fav, fail)
    return v if (v != c["correct"] and 0 <= v <= 1) else None


def _prob_off_by_one(c: Dict[str, Any]) -> Optional[Fraction]:
    fav, tot = c.get("favourable"), c.get("probTotal")
    if fav is None or not tot:
        return None
    cand = fav - 1 if fav - 1 >= 0 else fav + 1
    if cand < 0 or cand > tot:
        return None
    v = Fraction(cand, tot)
    return v if (v != c["correct"] and 0 <= v <= 1) else None


# --------------------------------------------------------------------------- #
# Registry
# --------------------------------------------------------------------------- #
def _r(mid, title, formula, description, observable, feedback, adapter) -> Dict[str, Any]:
    return {"id": mid, "title": title, "formula": formula, "description": description,
            "observableError": observable, "feedback": feedback, "adapter": adapter}


MISCONCEPTIONS: Dict[str, Dict[str, Any]] = {m["id"]: m for m in [
    _r("MISC.STAT.READ_OFF_BY_STEP", "Misreads by one scale step",
       "value +/- one axis step", "reads the bar/point one gridline off",
       "Reads the value one step up or down the scale.",
       "Check which gridline the top of the bar (or the point) lines up with, and read it off the scale carefully.",
       _off_by_step),
    _r("MISC.STAT.READ_WRONG_CATEGORY", "Reads the wrong category",
       "value of an adjacent category", "reads a neighbouring category instead of the named one",
       "Reads the frequency of a neighbouring category.",
       "Find the bar or row labelled with the category you were asked about before reading its value.",
       _adj_category),
    _r("MISC.STAT.READ_MISCOUNT_SCALE", "Counts squares, not the scale",
       "value / axis step", "counts gridline squares as one unit each",
       "Counts the squares instead of using the scale on the axis.",
       "Each square is worth more than one — use the numbers printed on the axis, not the number of squares.",
       _miscount_scale),
    _r("MISC.STAT.PICTO_COUNTS_SYMBOLS", "Counts symbols, ignores the key",
       "number of symbols", "reports the symbol count, not the value it represents",
       "Counts the symbols without using the key.",
       "Each symbol stands for more than one — multiply the symbols by the number in the key.",
       _picto_count_symbols),
    _r("MISC.STAT.PICTO_IGNORES_HALF", "Ignores the half symbol",
       "value - half-symbol contribution", "drops the part-symbol's value",
       "Leaves out the value of the half symbol.",
       "A half symbol is worth half of the key — remember to add it in.",
       _picto_ignore_half),
    _r("MISC.STAT.TABLE_READS_TOTAL", "Reads the total row",
       "the total", "reads the total instead of the category frequency",
       "Reads the total instead of the row that was asked for.",
       "Read across to the row for the named category, not the total row.",
       _table_reads_total),
    _r("MISC.STAT.TABLE_ADJACENT_ROW", "Reads an adjacent row",
       "value of an adjacent row", "reads the row above or below the named one",
       "Reads the frequency from the wrong row of the table.",
       "Line up the category name with its own row before reading the frequency.",
       _adj_category),
    _r("MISC.STAT.TABLE_READS_LARGEST", "Reads the largest frequency",
       "the largest frequency in the table", "reads the biggest number instead of the named row",
       "Reads the largest frequency in the table instead of the named category.",
       "Read the frequency from the row for the category you were asked about, not the biggest number.",
       _table_reads_largest),
    _r("MISC.STAT.LINE_SWAPS_AXES", "Swaps the axes",
       "the x-value instead of the y-value", "reads the time/position instead of the value",
       "Reads the value off the horizontal axis instead of the vertical axis.",
       "Read up to the marked point, then across to the vertical axis for its value.",
       _line_swaps_axes),
    _r("MISC.STAT.FREQ_SUBTRACT_WRONG_WAY", "Adds instead of subtracting",
       "total + other frequencies", "adds when the missing value should be found by subtracting",
       "Adds the known frequencies to the total instead of subtracting.",
       "The frequencies add up to the total, so subtract the ones you know from the total.",
       _freq_subtract_wrong),
    _r("MISC.STAT.FREQ_IGNORES_TOTAL", "Ignores the total",
       "sum of the other frequencies", "uses the other frequencies but forgets the total",
       "Adds up the other frequencies but ignores the given total.",
       "Use the total: the missing frequency is the total minus the frequencies you already have.",
       _freq_ignores_total),
    _r("MISC.STAT.MEAN_NO_DIVIDE", "Forgets to divide",
       "sum of the values", "reports the total instead of the mean",
       "Adds the values but forgets to divide by how many there are.",
       "After adding the values, divide by how many values there are.",
       _mean_no_divide),
    _r("MISC.STAT.MEAN_DIVIDE_WRONG_N", "Divides by the wrong count",
       "sum / (n - 1)", "divides by one fewer than the number of values",
       "Divides by the wrong number of values.",
       "Divide the total by exactly how many values are in the list.",
       _mean_divide_wrong_n),
    _r("MISC.STAT.AVG_USES_MODE", "Uses the mode instead",
       "the mode", "confuses this average with the mode",
       "Gives the most common value instead of the one asked for.",
       "This question asks for a different average — work it out rather than giving the most common value.",
       _uses_mode),
    _r("MISC.STAT.MEDIAN_NO_ORDER", "Finds the middle without ordering",
       "middle of the unordered list", "takes the middle term before sorting",
       "Takes the middle value without putting the list in order first.",
       "Put the values in order from smallest to largest before finding the middle.",
       _median_no_order),
    _r("MISC.STAT.MEDIAN_WRONG_MIDDLE", "Takes one middle value (even list)",
       "lower of the two middle values", "uses one middle value instead of averaging both",
       "Picks one of the two middle values instead of their average.",
       "With an even number of values, the median is halfway between the two middle ones.",
       _median_wrong_middle),
    _r("MISC.STAT.AVG_USES_MEDIAN", "Uses the median instead",
       "the median", "confuses the mode with the median",
       "Gives the middle value instead of the most common one.",
       "The mode is the value that appears most often, not the middle value.",
       _uses_median),
    _r("MISC.STAT.MODE_USES_HIGHEST", "Picks the largest value",
       "the largest value", "confuses 'most common' with 'largest'",
       "Gives the largest value instead of the most common one.",
       "The mode is the value that appears most often, not the biggest value.",
       _mode_uses_highest),
    _r("MISC.STAT.MODE_USES_FREQUENCY", "Reports how often, not which value",
       "the highest frequency", "reports the count instead of the value",
       "Gives how many times the mode occurs instead of the value itself.",
       "The mode is the value that occurs most often, not the number of times it occurs.",
       _mode_uses_frequency),
    _r("MISC.STAT.RANGE_IS_MAX", "Range is the largest value",
       "the largest value", "reports the maximum as the range",
       "Gives the largest value instead of the difference.",
       "The range is the largest value minus the smallest value.",
       _range_is_max),
    _r("MISC.STAT.RANGE_ADDS", "Adds the extremes",
       "largest + smallest", "adds instead of subtracting",
       "Adds the largest and smallest values instead of subtracting.",
       "The range is largest minus smallest, not largest plus smallest.",
       _range_adds),
    _r("MISC.STAT.MEANFT_DIVIDE_BY_CATEGORIES", "Divides by number of categories",
       "sum(value x frequency) / number of categories", "divides by categories, not total frequency",
       "Divides the total by the number of rows instead of the total frequency.",
       "Divide by the total frequency (the sum of the frequencies), not the number of rows.",
       _meanft_divide_by_categories),
    _r("MISC.STAT.MEANFT_NO_WEIGHT", "Forgets to weight by frequency",
       "sum(values) / number of categories", "averages the values, ignoring frequency",
       "Averages the listed values without using the frequencies.",
       "Multiply each value by its frequency before adding, then divide by the total frequency.",
       _meanft_no_weight),
    _r("MISC.STAT.PROB_COMPLEMENT", "Counts the wrong outcomes",
       "(total - favourable) / total", "finds the probability of the event NOT happening",
       "Counts the outcomes that are not wanted instead of the ones that are.",
       "Count the favourable outcomes (the ones the question asks about) over the total.",
       _prob_complement),
    _r("MISC.STAT.PROB_ODDS", "Writes odds, not probability",
       "favourable / unfavourable", "compares wanted to unwanted instead of to the total",
       "Compares wanted outcomes to unwanted outcomes instead of to the total.",
       "Probability is favourable outcomes over the TOTAL number of outcomes.",
       _prob_odds),
    _r("MISC.STAT.PROB_OFF_BY_ONE", "Miscounts the favourable outcomes",
       "(favourable -/+ 1) / total", "counts one too few or too many favourable outcomes",
       "Counts one too few or one too many of the wanted outcomes.",
       "Recount the favourable outcomes carefully before writing the fraction.",
       _prob_off_by_one),
    # Feedback-only rule (never an MC distractor — an unreduced form is an equivalent value).
    _r("MISC.STAT.PROB_UNREDUCED", "Leaves the fraction unsimplified",
       "favourable / total, not simplified", "correct value but not in simplest form",
       "Writes a correct but unsimplified fraction.",
       "Your value is equivalent, but simplify the fraction to its simplest form.",
       lambda c: None),
    # --- v1.0.1 additions (owner #2/#3/#4) --------------------------------- #
    _r("MISC.STAT.MEAN_MIDRANGE", "Uses the midrange instead of the mean",
       "(largest + smallest) / 2", "averages only the extremes",
       "Averages only the largest and smallest values instead of all of them.",
       "The mean uses every value, not only the largest and smallest.",
       _midrange),
    _r("MISC.STAT.MEDIAN_USES_MEAN", "Uses the mean instead of the median",
       "the mean", "confuses the median with the mean",
       "Adds the values and divides instead of finding the middle value.",
       "The median is the middle value of the ordered list, not the mean.",
       _uses_mean),
    _r("MISC.STAT.MEDIAN_MIDRANGE", "Uses the midrange instead of the median",
       "(largest + smallest) / 2", "averages the extremes instead of finding the middle",
       "Averages the largest and smallest values instead of finding the middle.",
       "The median is the middle value of the ordered list, not the average of the extremes.",
       _midrange),
    _r("MISC.STAT.RANGE_IS_MIN", "Range is the smallest value",
       "the smallest value", "reports the minimum as the range",
       "Gives the smallest value instead of the difference.",
       "The range is the largest value minus the smallest value.",
       _range_is_min),
    _r("MISC.STAT.PICTO_HALF_AS_WHOLE", "Counts the half symbol as a whole",
       "value + half-symbol's worth", "treats the part symbol as a full one",
       "Counts the half symbol as if it were a whole symbol.",
       "A half symbol is worth half of the key, not a whole one.",
       _picto_half_as_whole),
    _r("MISC.STAT.PICTO_OFF_BY_ONE_SYMBOL", "Miscounts by one symbol",
       "value - one symbol's worth", "counts one symbol too few",
       "Counts one symbol too few when reading the row.",
       "Count the symbols in the row carefully, then multiply by the key.",
       _picto_off_by_one_symbol),
    # Free-response missing-TOTAL diagnostics (owner #4) — feedback-only, applicable only when
    # the total is the unknown. Never claim to subtract from a total that is itself missing.
    _r("MISC.STAT.FREQ_TOTAL_OMITS_CATEGORY", "Omits a category from the total",
       "sum of all but one frequency", "leaves one frequency out when adding",
       "Leaves a category out when adding up the total.",
       "Add every category's frequency — don't miss one out.",
       lambda c: None),
    _r("MISC.STAT.FREQ_TOTAL_COPIES_ONE", "Copies one frequency as the total",
       "one of the frequencies", "writes a single frequency as the total",
       "Writes one of the frequencies as the total instead of their sum.",
       "The total is the sum of all the frequencies, not a single one of them.",
       lambda c: None),
]}


# Which misconception ids each task may draw distractors from (order = preference).
RULES_BY_TASK: Dict[str, List[str]] = {
    "read_bar_chart": ["MISC.STAT.READ_OFF_BY_STEP", "MISC.STAT.READ_WRONG_CATEGORY", "MISC.STAT.READ_MISCOUNT_SCALE"],
    # Whole-symbol count first; the half-symbol rules are mutually exclusive with it (owner #3);
    # off-by-one is a fallback so a 3rd distinct distractor always exists.
    "read_pictogram": ["MISC.STAT.PICTO_COUNTS_SYMBOLS", "MISC.STAT.PICTO_IGNORES_HALF",
                       "MISC.STAT.PICTO_HALF_AS_WHOLE", "MISC.STAT.READ_WRONG_CATEGORY",
                       "MISC.STAT.PICTO_OFF_BY_ONE_SYMBOL"],
    "read_table_value": ["MISC.STAT.TABLE_READS_TOTAL", "MISC.STAT.TABLE_ADJACENT_ROW", "MISC.STAT.TABLE_READS_LARGEST"],
    "read_line_graph": ["MISC.STAT.READ_OFF_BY_STEP", "MISC.STAT.LINE_SWAPS_AXES", "MISC.STAT.READ_MISCOUNT_SCALE"],
    # complete_frequency_table is free-response only — no distractors; its rules appear as
    # blank-kind-specific solution pitfalls (missing-total vs missing-frequency, owner #4).
    "complete_frequency_table": ["MISC.STAT.FREQ_SUBTRACT_WRONG_WAY", "MISC.STAT.FREQ_IGNORES_TOTAL",
                                 "MISC.STAT.FREQ_TOTAL_OMITS_CATEGORY", "MISC.STAT.FREQ_TOTAL_COPIES_ONE"],
    # AVG_USES_MODE is PREFERRED when a unique mode exists; midrange/min/mean fallbacks guarantee
    # three distinct, mathematically-true distractors when there is no mode (owner #2).
    "mean_from_list": ["MISC.STAT.MEAN_NO_DIVIDE", "MISC.STAT.MEAN_DIVIDE_WRONG_N", "MISC.STAT.AVG_USES_MODE", "MISC.STAT.MEAN_MIDRANGE"],
    "median_from_list": ["MISC.STAT.MEDIAN_NO_ORDER", "MISC.STAT.MEDIAN_WRONG_MIDDLE", "MISC.STAT.AVG_USES_MODE", "MISC.STAT.MEDIAN_USES_MEAN", "MISC.STAT.MEDIAN_MIDRANGE"],
    "mode_from_list": ["MISC.STAT.MODE_USES_HIGHEST", "MISC.STAT.MODE_USES_FREQUENCY", "MISC.STAT.AVG_USES_MEDIAN"],
    "range_from_list": ["MISC.STAT.RANGE_IS_MAX", "MISC.STAT.RANGE_ADDS", "MISC.STAT.AVG_USES_MODE", "MISC.STAT.RANGE_IS_MIN"],
    "mean_from_freq_table": ["MISC.STAT.MEANFT_DIVIDE_BY_CATEGORIES", "MISC.STAT.MEANFT_NO_WEIGHT", "MISC.STAT.MEAN_DIVIDE_WRONG_N"],
    "single_event_probability": ["MISC.STAT.PROB_COMPLEMENT", "MISC.STAT.PROB_ODDS", "MISC.STAT.PROB_OFF_BY_ONE"],
}


def rules_for(task: str) -> List[str]:
    return RULES_BY_TASK.get(task, [])


def adapter_for(mid: str) -> Callable[[Dict[str, Any]], Any]:
    return MISCONCEPTIONS[mid]["adapter"]
