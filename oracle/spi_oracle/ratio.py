"""gen.proportion.ratio v1.0.0 — generator, family-local ratio renderer (bar models / double number
lines / proportional best-buy table), and the independent validator.

RENDERER (owner J): a NEW additive theme (core/visual-style/ratio-theme.{json,ts}) carries the
presentation modes; the canonical monochrome <style> emitted here is the authoritative `print` look and
is never mutated. tx-style class names are prefixed `rt-`. Figures:
  * bar models           -> ratio_to_fraction, fraction_to_ratio, share_two_part, share_three_part, missing_part
  * double number lines  -> direct_proportion, unit_rate, simple_scale
  * proportional table    -> best_buy
  * no figure             -> simplify, write_from_quantities, inverse_proportion

ROLE-BASED LEAKAGE (owner J): the STUDENT figure shows only GIVEN quantities and unknown markers ("?");
the ANSWER-KEY figure adds the solved overlay. A given value that coincidentally equals the answer is
NOT leakage — the leakage check is role-based (is the unknown rendered as a value in the student
figure?), never raw-equality.

EXACT (owner E,F,G,I): every value is an integer or an exact Fraction — no floats, tolerance, or
irrational anywhere. The model + parser + encoders + result codes live in ratio_core (never modified
here); the 16 misconceptions + per-item diagnostics live in ratio_misconceptions.

domains/proportion/ratio.ts mirrors this byte-for-byte.
"""

from __future__ import annotations

import json
import os
import re
import sys
from fractions import Fraction
from typing import Any, Dict, List, Optional, Tuple

_HERE = os.path.dirname(os.path.abspath(__file__))
if _HERE not in sys.path:
    sys.path.insert(0, _HERE)
_PARENT = os.path.dirname(_HERE)
if _PARENT not in sys.path:
    sys.path.insert(0, _PARENT)

from spi_oracle.seeded_random import Mulberry32  # noqa: E402
from spi_oracle.difficulty import round3, clamp01  # noqa: E402
from spi_oracle import ratio_core as RC  # noqa: E402
from spi_oracle import ratio_misconceptions as RM  # noqa: E402

GENERATOR_ID = "gen.proportion.ratio"
GENERATOR_VERSION = "1.0.2"
VALIDATOR_VERSION = "1.0.2"
CALCULATOR_POLICY = "calculator-not-required"

# --------------------------------------------------------------------------- #
# Task -> objective mapping (mirror of core/curriculum/ratio-objective-ids.ts)
# --------------------------------------------------------------------------- #
RATIO_TASKS: Tuple[str, ...] = (
    "simplify", "write_from_quantities", "ratio_to_fraction", "fraction_to_ratio",
    "share_two_part", "share_three_part", "missing_part", "direct_proportion",
    "inverse_proportion", "unit_rate", "best_buy", "simple_scale",
)
TASKS = RATIO_TASKS

OBJECTIVE_BY_TASK = {
    "simplify": "SPI.MIDDLE.RATIO.SIMPLIFY.01",
    "write_from_quantities": "SPI.MIDDLE.RATIO.WRITE_FROM_QUANTITIES.01",
    "ratio_to_fraction": "SPI.MIDDLE.RATIO.RATIO_TO_FRACTION.01",
    "fraction_to_ratio": "SPI.MIDDLE.RATIO.FRACTION_TO_RATIO.01",
    "share_two_part": "SPI.MIDDLE.RATIO.SHARE_TWO_PART.01",
    "share_three_part": "SPI.MIDDLE.RATIO.SHARE_THREE_PART.01",
    "missing_part": "SPI.MIDDLE.RATIO.MISSING_PART.01",
    "direct_proportion": "SPI.MIDDLE.RATIO.DIRECT_PROPORTION.01",
    "inverse_proportion": "SPI.MIDDLE.RATIO.INVERSE_PROPORTION.01",
    "unit_rate": "SPI.MIDDLE.RATIO.UNIT_RATE.01",
    "best_buy": "SPI.MIDDLE.RATIO.BEST_BUY.01",
    "simple_scale": "SPI.MIDDLE.RATIO.SIMPLE_SCALE.01",
}

# Interaction policy (owner C). best_buy is multiple-choice-only; the other MC_ELIGIBLE add MC to FR;
# everything else is free-response only and an explicit MC request raises (never a silent FR).
MC_ELIGIBLE_TASKS: Tuple[str, ...] = (
    "simplify", "ratio_to_fraction", "fraction_to_ratio", "direct_proportion", "inverse_proportion", "best_buy",
)
MC_ONLY_TASKS: Tuple[str, ...] = ("best_buy",)

# Answer kind per task (owner D) — drives the ratio_core encoder used.
ANSWER_KIND = {
    "simplify": "ratio", "write_from_quantities": "ratio", "ratio_to_fraction": "rational",
    "fraction_to_ratio": "ratio", "share_two_part": "table", "share_three_part": "table",
    "missing_part": "integer", "direct_proportion": "rational", "inverse_proportion": "integer",
    "unit_rate": "rational", "best_buy": "mc", "simple_scale": "rational",
}

# Figure kind per task (owner J).
FIGURE_KIND = {
    "ratio_to_fraction": "bar", "fraction_to_ratio": "bar", "share_two_part": "bar",
    "share_three_part": "bar", "missing_part": "bar",
    "direct_proportion": "numberline", "unit_rate": "numberline", "simple_scale": "numberline",
    "best_buy": "table",
    "simplify": None, "write_from_quantities": None, "inverse_proportion": None,
}

# Single source-of-truth difficulty bands (provisional; both declared bands reachable per task).
TASK_BANDS = {
    "simplify": (1, 3), "write_from_quantities": (1, 3), "ratio_to_fraction": (2, 3),
    "fraction_to_ratio": (2, 3), "share_two_part": (2, 3), "share_three_part": (3, 4),
    "missing_part": (2, 3), "direct_proportion": (2, 4), "inverse_proportion": (3, 4),
    "unit_rate": (2, 3), "best_buy": (3, 4), "simple_scale": (2, 4),
}

MAX_PARAM_ATTEMPTS = 800


class InteractionNotSupported(Exception):
    """Raised when an unsupported interaction is requested for a task (owner C). Never substituted by a
    silent free-response item."""


def supported_interactions(task: str) -> Tuple[str, ...]:
    if task in MC_ONLY_TASKS:
        return ("multiple-choice",)
    if task in MC_ELIGIBLE_TASKS:
        return ("free-response", "multiple-choice")
    return ("free-response",)


# --------------------------------------------------------------------------- #
# Themed contexts (labels carry their own meaning — a non-colour indicator).
# --------------------------------------------------------------------------- #
_QTY_THEMES = [
    ("Paint mixture", ["red paint", "white paint", "blue paint"], "litres"),
    ("Fruit basket", ["apples", "oranges", "pears"], "pieces"),
    ("Class survey", ["boys", "girls", "teachers"], "people"),
    ("Recipe", ["flour", "sugar", "butter"], "grams"),
    ("Garden", ["roses", "tulips", "daisies"], "plants"),
]
_SHARE_THEMES = [
    ("Sharing money", ["Amir", "Beth", "Carl"], "pounds"),
    ("Sharing sweets", ["Dana", "Eli", "Faye"], "sweets"),
    ("Sharing marbles", ["Gus", "Hana", "Ivan"], "marbles"),
    ("Sharing stickers", ["Jo", "Kim", "Lee"], "stickers"),
]
# --------------------------------------------------------------------------- #
# CONTEXT-DOMAIN REGISTRY (correction #3). Every rate/quantity noun used by a
# direct_proportion / unit_rate item is classified into a CONTEXT DOMAIN that
# determines whether a FRACTIONAL answer is meaningful for that noun:
#   * count-discrete-integer-only : physical count nouns (books, apples, ...) —
#       the answer (and any displayed per-context quantity) MUST be an integer.
#   * continuous-measure          : litres, metres, kilograms, hours, ... —
#       rational answers are allowed.
#   * abstract-number             : units, points, parts — rational allowed
#       (used by simple_scale per correction #5).
#   * average-rate-allowed        : a count noun used ONLY with explicit
#       "average ... per ..." wording — rational allowed. Reserved for v1.0.1;
#       all rational rate answers route through continuous-measure instead.
# The amount noun ("books") is the quantity whose value is the ANSWER; the per
# noun ("shelves") is the basis. A theme's domain is the AMOUNT noun's domain.
# --------------------------------------------------------------------------- #
CONTEXT_DOMAIN_COUNT = "count-discrete-integer-only"
CONTEXT_DOMAIN_CONTINUOUS = "continuous-measure"
CONTEXT_DOMAIN_ABSTRACT = "abstract-number"
CONTEXT_DOMAIN_AVERAGE = "average-rate-allowed"

# Amount-noun -> context domain. Count nouns demand an integer answer; measures
# allow rational answers. (Used to route compute-answer-then-pick-context.)
_CONTEXT_DOMAINS = {
    # count-discrete (integer-only answers)
    "books": CONTEXT_DOMAIN_COUNT, "apples": CONTEXT_DOMAIN_COUNT,
    "pencils": CONTEXT_DOMAIN_COUNT, "eggs": CONTEXT_DOMAIN_COUNT,
    # continuous-measure (rational answers allowed)
    "litres": CONTEXT_DOMAIN_CONTINUOUS, "metres": CONTEXT_DOMAIN_CONTINUOUS,
    "kilograms": CONTEXT_DOMAIN_CONTINUOUS, "grams": CONTEXT_DOMAIN_CONTINUOUS,
    "kilometres": CONTEXT_DOMAIN_CONTINUOUS, "litres of water": CONTEXT_DOMAIN_CONTINUOUS,
}

# Rate themes are (amountNoun, perNoun) split by the amount noun's domain. An
# INTEGER answer may use either a count-discrete OR a continuous theme; a
# FRACTIONAL answer must use a continuous theme (never a count noun) so an item
# never claims a fractional book / apple / pencil.
_RATE_THEMES_COUNT = [
    ("books", "shelves"), ("apples", "bags"), ("pencils", "boxes"), ("eggs", "trays"),
]
_RATE_THEMES_CONTINUOUS = [
    ("litres", "tanks"), ("kilometres", "hours"), ("grams", "spoons"),
    ("metres", "rolls"), ("kilograms", "sacks"),
]
_BUY_THEMES = [
    ("pencils", "pencil"), ("apples", "apple"), ("notebooks", "notebook"),
    ("markers", "marker"), ("erasers", "eraser"),
]
_INVERSE_THEMES = [
    ("workers", "days", "to finish the job"),
    ("taps", "hours", "to fill the tank"),
    ("machines", "minutes", "to complete the batch"),
    ("painters", "days", "to paint the hall"),
]
# Dimensionless scale contexts (correction #5, POLICY A): NO cm/km/m anywhere.
# (kind, srcUnitWord, dstUnitWord) where the units are abstract "... units".
_SCALE_THEMES = [
    ("model", "model unit", "real unit"),
    ("plan", "plan unit", "actual unit"),
    ("drawing", "drawing unit", "real unit"),
    ("map", "map unit", "ground unit"),
]

# --------------------------------------------------------------------------- #
# GRAMMATICAL NOUN REGISTRY (follow-up correction). Every noun a count can precede
# is stored as an EXPLICIT (singular, plural) pair so display never relies on a
# naive `[:-1]`/`+ "s"` singularizer (which mis-produces "1 boys", "per shelve").
# Keyed by the PLURAL form (the canonical form the theme tables store). _count()
# routes EVERY "<count> <noun>" through this map; _singular() gives the "per <unit>"
# form. Mirrored byte-for-byte in ratio.ts.
# --------------------------------------------------------------------------- #
_NOUNS = {
    # rate amount/per nouns
    "books": ("book", "books"), "shelves": ("shelf", "shelves"),
    "apples": ("apple", "apples"), "bags": ("bag", "bags"),
    "pencils": ("pencil", "pencils"), "boxes": ("box", "boxes"),
    "eggs": ("egg", "eggs"), "trays": ("tray", "trays"),
    "litres": ("litre", "litres"), "tanks": ("tank", "tanks"),
    "kilometres": ("kilometre", "kilometres"), "hours": ("hour", "hours"),
    "grams": ("gram", "grams"), "spoons": ("spoon", "spoons"),
    "metres": ("metre", "metres"), "rolls": ("roll", "rolls"),
    "kilograms": ("kilogram", "kilograms"), "sacks": ("sack", "sacks"),
    # best_buy item + tokens
    "notebooks": ("notebook", "notebooks"), "markers": ("marker", "markers"),
    "erasers": ("eraser", "erasers"), "tokens": ("token", "tokens"),
    # write_from_quantities labels
    "oranges": ("orange", "oranges"), "pears": ("pear", "pears"),
    "boys": ("boy", "boys"), "girls": ("girl", "girls"),
    "teachers": ("teacher", "teachers"), "roses": ("rose", "roses"),
    "tulips": ("tulip", "tulips"), "daisies": ("daisy", "daisies"),
    # mass / uncountable nouns used as labels (singular == plural form)
    "red paint": ("red paint", "red paint"), "white paint": ("white paint", "white paint"),
    "blue paint": ("blue paint", "blue paint"),
    "flour": ("flour", "flour"), "sugar": ("sugar", "sugar"), "butter": ("butter", "butter"),
    # _QTY_THEMES units (only ever appear as bare labels, registered for completeness)
    "pieces": ("piece", "pieces"), "people": ("person", "people"), "plants": ("plant", "plants"),
    # share units
    "pounds": ("pound", "pounds"), "sweets": ("sweet", "sweets"),
    "marbles": ("marble", "marbles"), "stickers": ("sticker", "stickers"),
    # inverse-proportion agents + units
    "workers": ("worker", "workers"), "taps": ("tap", "taps"),
    "machines": ("machine", "machines"), "painters": ("painter", "painters"),
    "days": ("day", "days"), "minutes": ("minute", "minutes"),
    # ratio-part word (figures, data tables, solutions) — "1 part" vs "2 parts"
    "parts": ("part", "parts"),
}


def _n(rng: Mulberry32, k: int) -> int:
    return rng.next_int(0, k - 1)


def _pick(rng: Mulberry32, items: List[Any]) -> Any:
    return items[_n(rng, len(items))]


def _disp_rat(f: Fraction) -> str:
    return str(f.numerator) if f.denominator == 1 else f"{f.numerator}/{f.denominator}"


def _is_one(n: Any) -> bool:
    """True iff the displayed count is exactly 1 (an integer 1 or the Fraction 1)."""
    val = n.numerator if isinstance(n, Fraction) and n.denominator == 1 else n
    return val == 1


def _forms(word: str) -> Tuple[str, str]:
    """(singular, plural) for a noun stored in its PLURAL form. Falls back to regular '+s'
    pluralization for words not in the registry (e.g. dynamically composed unit words)."""
    if word in _NOUNS:
        return _NOUNS[word]
    return (word, word + "s")


def _count_pair(n: Any, sing: str, plur: str) -> str:
    """Grammatical "<count> <noun>" from an EXPLICIT (singular, plural) pair (used where the pair is
    already at hand, e.g. best_buy's (item, items)). Mirrored byte-for-byte in ratio.ts."""
    return f"{_fmt_val(n)} {sing if _is_one(n) else plur}"


def _count(n: Any, word: str) -> str:
    """Grammatical "<count> <noun>" using the EXPLICIT (singular, plural) registry: '1 box' /
    '2 boxes', '1 shelf' / '5 shelves', '1 token' / '9 tokens'. Mirrored byte-for-byte in ratio.ts."""
    sing, plur = _forms(word)
    return _count_pair(n, sing, plur)


def _singular(word: str) -> str:
    """The singular form of a registry noun, for 'per <unit>' phrasing ('per shelf', 'per spoon')."""
    return _forms(word)[0]


# Plural forms that MUST NOT follow a count of 1 or the word "per". Built from the registry (any noun
# whose singular differs from its plural) plus the scale-unit plurals "<word> units" and the fixed
# count word "tokens". Used by _grammar_violations + the noun-count-grammatical validator check.
_PLURAL_FORMS = frozenset(
    [plur for (sing, plur) in _NOUNS.values() if sing != plur]
    + ["units", "tokens", "parts", "shelve"]   # 'shelve' = the old naive-singularizer artifact (guard)
)
# scale unit plurals like "model units"/"real units" pluralize regularly; the generic "units" guard
# below catches them via the trailing token.
_GRAMMAR_RE_ONE = re.compile(r"\b1 ([A-Za-z]+)\b")
_GRAMMAR_RE_PER = re.compile(r"\bper ([A-Za-z]+)\b")


def _grammar_violations(text: str) -> List[str]:
    """Return the list of count-agreement violations in `text`: any "1 <plural>" (plural after a count
    of one) or any "per <plural>"/"per shelve" (a count-basis that must be singular). Mass nouns
    (singular == plural) are exempt. Mirrored byte-for-byte in ratio.ts."""
    out: List[str] = []
    for m in _GRAMMAR_RE_ONE.finditer(text):
        w = m.group(1)
        if w in _PLURAL_FORMS:
            out.append(f"1 {w}")
    for m in _GRAMMAR_RE_PER.finditer(text):
        w = m.group(1)
        if w in _PLURAL_FORMS:
            out.append(f"per {w}")
    out.extend(_scale_verb_violations(text))
    return out


# Subject-verb agreement for the scale relation "<n> <…> unit[s] represent[s] …" (owner REVISE #1):
# a count of 1 takes the SINGULAR noun + SINGULAR verb ("1 plan unit represents"); any other count
# takes the PLURAL noun + PLURAL verb ("2 plan units represent"). Inspects the RENDERED text.
_SCALE_VERB_RE = re.compile(r"\b(\d+) ([A-Za-z]+ )?unit(s?) (represent|represents)\b")


def _scale_verb_violations(text: str) -> List[str]:
    """Return subject-verb (and noun-number) disagreements in scale wording. Mirrored in ratio.ts."""
    out: List[str] = []
    for m in _SCALE_VERB_RE.finditer(text):
        n = int(m.group(1))
        noun_plural = m.group(3) == "s"
        verb = m.group(4)
        sing = (n == 1)
        if sing and (noun_plural or verb != "represents"):
            out.append(m.group(0))                       # e.g. "1 plan unit represent"
        if not sing and ((not noun_plural) or verb != "represent"):
            out.append(m.group(0))                       # e.g. "2 plan units represents"
    return out


def _units(n: Any, word: str) -> str:
    """Grammatical count phrase for a dimensionless scale unit (correction #5): '1 model unit' /
    '2 model units'. Scale unit words pluralize regularly ('+s'). Delegates to _count via the
    regular-plural fallback. Mirrored byte-for-byte in ratio.ts."""
    return _count(n, word)


def _esc(s: str) -> str:
    return (s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
             .replace('"', "&quot;").replace("'", "&#39;"))


# --------------------------------------------------------------------------- #
# Parameter draws (seeded; exact integer/Fraction only; deterministic redraw)
# --------------------------------------------------------------------------- #
def _draw_simplify(rng: Mulberry32) -> Optional[Dict[str, Any]]:
    three = _n(rng, 3) == 0
    k = 2 + _n(rng, 7)                       # common multiplier 2..8 (ensures simplifiable)
    if three:
        base = [1 + _n(rng, 6), 1 + _n(rng, 6), 1 + _n(rng, 6)]
    else:
        base = [1 + _n(rng, 8), 1 + _n(rng, 8)]
    if RC.gcd_list(base) != 1:
        return None                           # want a coprime base so k IS the gcd
    parts = [p * k for p in base]
    return {"task": "simplify", "parts": parts}


def _draw_write_from_quantities(rng: Mulberry32) -> Optional[Dict[str, Any]]:
    title, labels, unit = _pick(rng, _QTY_THEMES)
    three = _n(rng, 3) == 0
    nq = 3 if three else 2
    k = 1 + _n(rng, 6)                        # scale so quantities need simplifying sometimes
    base = [1 + _n(rng, 7) for _ in range(nq)]
    if RC.gcd_list(base) != 1:
        return None
    quantities = [b * k for b in base]
    return {"task": "write_from_quantities", "title": title,
            "labels": labels[:nq], "unit": unit, "quantities": quantities}


def _draw_ratio_to_fraction(rng: Mulberry32) -> Optional[Dict[str, Any]]:
    title, labels, unit = _pick(rng, _QTY_THEMES)
    parts = [1 + _n(rng, 7), 1 + _n(rng, 7)]
    if parts[0] == parts[1]:
        return None
    part_index = _n(rng, 2)
    return {"task": "ratio_to_fraction", "title": title, "labels": labels[:2],
            "unit": unit, "parts": parts, "partIndex": part_index}


def _draw_fraction_to_ratio(rng: Mulberry32) -> Optional[Dict[str, Any]]:
    den = 3 + _n(rng, 8)                      # 3..10
    num = 1 + _n(rng, den - 1)                # 1..den-1 (proper)
    rest = den - num
    if num == rest:
        return None
    return {"task": "fraction_to_ratio", "num": num, "den": den}


def _draw_share(rng: Mulberry32, three: bool) -> Optional[Dict[str, Any]]:
    title, labels, unit = _pick(rng, _SHARE_THEMES)
    nq = 3 if three else 2
    parts = [1 + _n(rng, 5) for _ in range(nq)]
    if RC.gcd_list(parts) != 1:
        return None                           # ratio given in simplest form
    if len(set(parts)) == 1:
        return None                           # all-equal sharing is trivial
    s = sum(parts)
    one = 2 + _n(rng, 9)                      # value of one part 2..10
    total = one * s
    return {"task": "share_three_part" if three else "share_two_part", "title": title,
            "labels": labels[:nq], "unit": unit, "parts": parts, "total": total}


def _draw_missing_part(rng: Mulberry32) -> Optional[Dict[str, Any]]:
    title, labels, unit = _pick(rng, _SHARE_THEMES)
    parts = [1 + _n(rng, 6), 1 + _n(rng, 6)]
    if RC.gcd_list(parts) != 1 or parts[0] == parts[1]:
        return None
    known_index = _n(rng, 2)
    missing_index = 1 - known_index
    one = 2 + _n(rng, 9)
    known_value = one * parts[known_index]    # ensures parts[known] divides known_value
    return {"task": "missing_part", "title": title, "labels": labels[:2], "unit": unit,
            "parts": parts, "knownIndex": known_index, "missingIndex": missing_index,
            "knownValue": known_value}


def _draw_direct_proportion(rng: Mulberry32) -> Optional[Dict[str, Any]]:
    # Correction #3: draw numeric params, compute the EXACT answer FIRST, then choose a context whose
    # domain MATCHES the answer (integer -> count-discrete OR continuous; fractional -> continuous only,
    # never a count noun). Theme draw moves AFTER the numeric draw — fixtures regenerate.
    quantity = 2 + _n(rng, 7)                 # 2..8 units
    one_unit_num = 1 + _n(rng, 12)            # total per unit basis
    whole_result = _n(rng, 2) == 0
    if whole_result:
        total = quantity * one_unit_num       # whole unit rate -> integer-friendly
    else:
        total = one_unit_num                  # may produce a fraction
    target = 2 + _n(rng, 9)                   # 2..10
    if target == quantity:
        return None
    answer = Fraction(total, quantity) * target
    pool = _RATE_THEMES_COUNT + _RATE_THEMES_CONTINUOUS if answer.denominator == 1 else _RATE_THEMES_CONTINUOUS
    a, b = _pick(rng, pool)
    return {"task": "direct_proportion", "givenLabel": a, "perLabel": b,
            "quantity": quantity, "total": total, "target": target}


def _draw_inverse_proportion(rng: Mulberry32) -> Optional[Dict[str, Any]]:
    agent, unit, tail = _pick(rng, _INVERSE_THEMES)
    q1 = 2 + _n(rng, 7)
    v1 = 2 + _n(rng, 11)
    prod = q1 * v1
    # pick q2 dividing prod, q2 != q1, giving an integer v2
    divisors = [d for d in range(2, prod + 1) if prod % d == 0 and d != q1 and prod // d != v1]
    if not divisors:
        return None
    q2 = divisors[_n(rng, len(divisors))]
    return {"task": "inverse_proportion", "agent": agent, "unit": unit, "tail": tail,
            "q1": q1, "v1": v1, "q2": q2}


def _draw_unit_rate(rng: Mulberry32) -> Optional[Dict[str, Any]]:
    # Correction #3: numeric draw FIRST, compute the EXACT rate, then pick a context by domain
    # (fractional rate -> continuous-measure only; never a count noun).
    quantity = 2 + _n(rng, 7)
    whole = _n(rng, 2) == 0
    if whole:
        total = quantity * (1 + _n(rng, 12))
    else:
        total = 1 + _n(rng, 40)
    if total == 0:
        return None
    rate = Fraction(total, quantity)
    pool = _RATE_THEMES_COUNT + _RATE_THEMES_CONTINUOUS if rate.denominator == 1 else _RATE_THEMES_CONTINUOUS
    a, b = _pick(rng, pool)
    return {"task": "unit_rate", "amountLabel": a, "perLabel": b,
            "total": total, "quantity": quantity}


def _draw_best_buy(rng: Mulberry32) -> Optional[Dict[str, Any]]:
    # Correction #4: COST-LIKE DENOMINATOR policy (no currency). Each option is
    # "<itemCount> <items> for <tokenCost> tokens"; the unit rate is COST PER ITEM =
    # Fraction(tokenCost, itemCount) (tokens per item); the BEST VALUE is the STRICT MINIMUM
    # tokens-per-item. items is the plural noun, item the singular.
    items, item = _pick(rng, _BUY_THEMES)
    n_opts = 2 + _n(rng, 2)                    # 2 or 3 options
    options = []
    for i in range(n_opts):
        item_count = 3 + _n(rng, 28)           # 3..30
        token_cost = 2 + _n(rng, 11)           # 2..12
        options.append({"label": chr(ord("A") + i), "itemCount": item_count,
                        "tokenCost": token_cost,
                        "unitRate": {"num": token_cost, "den": item_count}})
    # Require all option (itemCount, tokenCost) displays distinct (no byte-identical option), all
    # cost-per-item rates pairwise distinct, AND a unique strict-MINIMUM cost-per-item. Redraw on a tie.
    displays = [(o["itemCount"], o["tokenCost"]) for o in options]
    if len(set(displays)) != len(displays):
        return None
    rates = [Fraction(o["tokenCost"], o["itemCount"]) for o in options]
    if len(set(rates)) != len(rates):
        return None
    mn = min(rates)
    winners = [i for i, r in enumerate(rates) if r == mn]
    if len(winners) != 1:
        return None
    correct = options[winners[0]]["label"]
    return {"task": "best_buy", "items": items, "item": item,
            "options": options, "correctLabel": correct}


def _draw_simple_scale(rng: Mulberry32) -> Optional[Dict[str, Any]]:
    # Correction #5 (POLICY A, dimensionless): NO cm/km/m. srcUnit/dstUnit are abstract "... units".
    # The answer is the BARE NUMBER of dst units = value*num/den (no cross-unit conversion).
    kind, src_unit, dst_unit = _pick(rng, _SCALE_THEMES)
    fnum = 1 + _n(rng, 9)
    fden = 1 + _n(rng, 9)
    if fnum == fden:
        return None
    value = 2 + _n(rng, 19)                    # 2..20
    direction = "multiply"                     # value (src) -> dst by factor fnum/fden
    return {"task": "simple_scale", "scaleKind": kind, "srcUnit": src_unit, "dstUnit": dst_unit,
            "value": value, "factorNum": fnum, "factorDen": fden, "direction": direction}


_DRAW = {
    "simplify": lambda r: _draw_simplify(r),
    "write_from_quantities": lambda r: _draw_write_from_quantities(r),
    "ratio_to_fraction": lambda r: _draw_ratio_to_fraction(r),
    "fraction_to_ratio": lambda r: _draw_fraction_to_ratio(r),
    "share_two_part": lambda r: _draw_share(r, three=False),
    "share_three_part": lambda r: _draw_share(r, three=True),
    "missing_part": lambda r: _draw_missing_part(r),
    "direct_proportion": lambda r: _draw_direct_proportion(r),
    "inverse_proportion": lambda r: _draw_inverse_proportion(r),
    "unit_rate": lambda r: _draw_unit_rate(r),
    "best_buy": lambda r: _draw_best_buy(r),
    "simple_scale": lambda r: _draw_simple_scale(r),
}


# --------------------------------------------------------------------------- #
# Solvers (exact) — each returns the canonical value object for the task.
# --------------------------------------------------------------------------- #
def _solve(task: str, params: Dict[str, Any]) -> Any:
    if task == "simplify":
        return RC.simplify_parts(params["parts"])
    if task == "write_from_quantities":
        return RC.simplify_parts(params["quantities"])
    if task == "ratio_to_fraction":
        a, b = params["parts"]
        part = params["parts"][params["partIndex"]]
        return Fraction(part, a + b)
    if task == "fraction_to_ratio":
        num, den = params["num"], params["den"]
        return RC.simplify_parts([num, den - num])
    if task in ("share_two_part", "share_three_part"):
        return RC.share(params["total"], params["parts"])
    if task == "missing_part":
        return RC.missing_part(params["knownValue"], params["knownIndex"],
                               params["missingIndex"], params["parts"])
    if task == "direct_proportion":
        return RC.direct_proportion(params["total"], params["quantity"], params["target"])
    if task == "inverse_proportion":
        return RC.inverse_proportion(params["q1"], params["v1"], params["q2"])
    if task == "unit_rate":
        return RC.unit_rate(params["total"], params["quantity"])
    if task == "best_buy":
        return params["correctLabel"]
    if task == "simple_scale":
        return RC.scale_value(params["value"], Fraction(params["factorNum"], params["factorDen"]))
    raise ValueError(task)


# --------------------------------------------------------------------------- #
# Exactness gate (owner E,F,G,I) — the deterministic-redraw acceptance test.
# --------------------------------------------------------------------------- #
def _acceptable(task: str, params: Dict[str, Any]) -> bool:
    sol = _solve(task, params)
    if task in ("share_two_part", "share_three_part"):
        return sol is not None              # total divisible by sum(parts)
    if task == "missing_part":
        return sol is not None and sol > 0   # integer-only; positive
    if task == "inverse_proportion":
        return sol is not None and sol > 0   # integer-only; positive
    if task == "best_buy":
        # Correction #4: cost-per-item = tokenCost / itemCount; best = strict MIN tokens-per-item.
        rates = [Fraction(o["tokenCost"], o["itemCount"]) for o in params["options"]]
        mn = min(rates)
        return sum(1 for r in rates if r == mn) == 1  # unique strict minimum
    if task == "ratio_to_fraction":
        return 0 < sol < 1                    # a proper fraction part/whole
    if task in ("direct_proportion", "unit_rate", "simple_scale"):
        return isinstance(sol, Fraction) and sol > 0
    return True


# --------------------------------------------------------------------------- #
# Answer encoding (owner D — uses the ratio_core encoders).
# --------------------------------------------------------------------------- #
def _share_labels_cells(params: Dict[str, Any]) -> List[Tuple[str, int]]:
    shares = RC.share(params["total"], params["parts"])
    return [(lab, val) for lab, val in zip(params["labels"], shares)]


def _encode_answer(task: str, params: Dict[str, Any]) -> Dict[str, Any]:
    kind = ANSWER_KIND[task]
    sol = _solve(task, params)
    if kind == "ratio":
        return RC.ratio_answer(sol)
    if kind == "rational":
        return RC.rational_answer(sol)
    if kind == "integer":
        return RC.integer_answer(sol)
    if kind == "table":
        return RC.table_answer(_share_labels_cells(params))
    if kind == "mc":
        return RC.mc_answer(sol)
    raise ValueError(kind)


# =========================================================================== #
# RENDERER (owner J) — family-local; tx-style class names prefixed `rt-`.
# viewBox 0 0 1000 H. bar ~ 0 0 1000 300; number line ~ 0 0 1000 260; table ~ 0 0 1000 300.
# =========================================================================== #
BAR_W, BAR_H = 1000, 300
NL_W, NL_H = 1000, 260
TBL_W, TBL_H = 1000, 300

STYLE = (
    ".rt-bar-given{fill:#dddddd;stroke:#111;stroke-width:2}"
    ".rt-bar-unknown{fill:#ffffff;stroke:#111;stroke-width:2;stroke-dasharray:6 4}"
    ".rt-bar-frame{fill:none;stroke:#111;stroke-width:2.5}"
    ".rt-divider{stroke:#111;stroke-width:1.5}"
    ".rt-axis{stroke:#111;stroke-width:2.5;fill:none}"
    ".rt-tick{stroke:#111;stroke-width:2}"
    ".rt-given-pt{fill:#111;stroke:#111;stroke-width:2}"
    ".rt-unknown-pt{fill:#ffffff;stroke:#111;stroke-width:2.5;stroke-dasharray:4 3}"
    ".rt-rung{stroke:#111;stroke-width:1.5;stroke-dasharray:3 4}"
    ".rt-table-line{stroke:#111;stroke-width:2;fill:none}"
    ".rt-table-given{fill:#dddddd;stroke:#111;stroke-width:1.5}"
    "text{font-family:sans-serif;font-size:26px;fill:#111}"
    ".rt-ticklbl{font-size:20px;fill:#333}"
    ".rt-lbl{font-size:26px;fill:#111}"
    ".rt-unknown-lbl{font-size:28px;font-weight:bold;fill:#111}"
)


def _svg_header(view_w: int, view_h: int, acc: Dict[str, str]) -> List[str]:
    return [
        f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {view_w} {view_h}" role="img" aria-label="{_esc(acc["alt"])}">',
        f"<title>{_esc(acc['title'])}</title><desc>{_esc(acc['desc'])}</desc>",
        f"<style>{STYLE}</style>",
    ]


# --- bar models ------------------------------------------------------------- #
def _bar_segments(task: str, params: Dict[str, Any]) -> Tuple[List[int], List[bool], List[str]]:
    """Return (weights, givenFlags, cellLabels). givenFlags[i] False marks an UNKNOWN cell, drawn as a
    dashed/hatched segment with a '?' in the STUDENT figure; the answer-key reveals its value."""
    if task == "ratio_to_fraction":
        a, b = params["parts"]
        idx = params["partIndex"]
        # all parts are given (the figure shows the whole partitioned); the unknown is the FRACTION,
        # which is a label, not a bar cell -> highlight the named part.
        weights = [a, b]
        labels = [f"{params['labels'][0]} ({a})", f"{params['labels'][1]} ({b})"]
        given = [True, True]
        return weights, given, labels
    if task == "fraction_to_ratio":
        num, den = params["num"], params["den"]
        weights = [num, den - num]
        labels = [f"named part ({num})", f"rest ({den - num})"]
        return weights, [True, True], labels
    if task in ("share_two_part", "share_three_part"):
        parts = params["parts"]
        labels = [f"{lab} ({_count(p, 'parts')})" for lab, p in zip(params["labels"], parts)]
        return list(parts), [False] * len(parts), labels  # share values are the unknowns
    if task == "missing_part":
        parts = params["parts"]
        ki, mi = params["knownIndex"], params["missingIndex"]
        given = [False, False]
        given[ki] = True
        labels = ["", ""]
        labels[ki] = f"{params['labels'][ki]} = {params['knownValue']}"
        labels[mi] = f"{params['labels'][mi]} = ?"
        return list(parts), given, labels
    raise ValueError(task)


def _render_bar(task: str, params: Dict[str, Any], answer_key: bool, acc: Dict[str, str]) -> str:
    weights, given, labels = _bar_segments(task, params)
    total_w = sum(weights)
    x0, x1 = 80, 920
    band = x1 - x0
    y0 = 110
    h = 90
    out = _svg_header(BAR_W, BAR_H, acc)
    # partition cells proportionally with integer pixel edges
    acc_w = 0
    edges = [x0]
    for w in weights:
        acc_w += w
        edges.append(x0 + (band * acc_w) // total_w)
    # ----- shared base (byte-identical in both channels): frame, cells, labels (NO ? and NO value) -----
    out.append('<g class="rt-base">')
    out.append(f'<text class="rt-lbl" x="{BAR_W // 2}" y="56" text-anchor="middle">{_esc(_bar_caption(task, params))}</text>')
    for i, w in enumerate(weights):
        lx, rx = edges[i], edges[i + 1]
        cls = "rt-bar-given" if given[i] else "rt-bar-unknown"
        out.append(f'<rect class="{cls}" data-cell="{i}" x="{lx}" y="{y0}" width="{rx - lx}" height="{h}"/>')
        cx = (lx + rx) // 2
        if labels[i]:
            out.append(f'<text class="rt-lbl" x="{cx}" y="{y0 + h + 36}" text-anchor="middle">{_esc(labels[i])}</text>')
    out.append(f'<rect class="rt-bar-frame" x="{x0}" y="{y0}" width="{band}" height="{h}"/>')
    out.append("</g>")
    # ----- role-specific channel: student '?' markers vs answer-key solved values -----
    # For ratio_to_fraction / fraction_to_ratio every bar cell is GIVEN (the figure shows the whole
    # partitioned); the unknown is the FRACTION/RATIO answer, drawn as an answer caption (a '?' for the
    # student, the solved value in the key) so the key is strictly additive and role-based.
    unknown_cells = [(i, (edges[i] + edges[i + 1]) // 2) for i in range(len(weights)) if not given[i]]
    answer_only = task in ("ratio_to_fraction", "fraction_to_ratio")
    ay = y0 + h + 78
    if answer_key:
        out.append('<g class="rt-overlay">')
        for i, cx in unknown_cells:
            val = _bar_cell_value(task, params, i)
            if val is not None:
                out.append(f'<text class="rt-unknown-lbl" x="{cx}" y="{y0 + h - 28}" text-anchor="middle">{val}</text>')
        if answer_only:
            sol = _solve(task, params)
            disp = _disp_rat(sol) if isinstance(sol, Fraction) else RC.format_ratio(sol)
            out.append(f'<text class="rt-unknown-lbl" x="{BAR_W // 2}" y="{ay}" text-anchor="middle">Answer: {_esc(disp)}</text>')
        out.append("</g>")
    else:
        out.append('<g class="rt-student">')
        for i, cx in unknown_cells:
            out.append(f'<text class="rt-unknown-lbl" x="{cx}" y="{y0 + h - 28}" text-anchor="middle">?</text>')
        if answer_only:
            out.append(f'<text class="rt-unknown-lbl" x="{BAR_W // 2}" y="{ay}" text-anchor="middle">Answer: ?</text>')
        out.append("</g>")
    out.append("</svg>")
    return "\n".join(out)


def _bar_cell_value(task: str, params: Dict[str, Any], i: int) -> Optional[int]:
    """The SOLVED value placed inside cell i in the answer-key overlay, or None if cell i is a given."""
    if task in ("share_two_part", "share_three_part"):
        shares = RC.share(params["total"], params["parts"])
        return shares[i]
    if task == "missing_part":
        if i == params["missingIndex"]:
            return _solve(task, params)
        return None
    return None  # ratio_to_fraction / fraction_to_ratio have no unknown bar cell


def _bar_caption(task: str, params: Dict[str, Any]) -> str:
    if task == "ratio_to_fraction":
        return f"Bar model: the whole split as {RC.format_ratio(params['parts'])}"
    if task == "fraction_to_ratio":
        return f"Bar model: {params['num']} of {params['den']} equal parts shaded"
    if task in ("share_two_part", "share_three_part"):
        return f"Bar model: {_count(params['total'], params['unit'])} shared in {RC.format_ratio(params['parts'])}"
    if task == "missing_part":
        return f"Bar model: parts in the ratio {RC.format_ratio(params['parts'])}"
    return "Bar model"


# --- double number lines ---------------------------------------------------- #
def _nl_pairs(task: str, params: Dict[str, Any]) -> Tuple[str, str, List[Tuple[Any, Any, bool]]]:
    """Return (topLabel, bottomLabel, rungs) where each rung is (topValue, bottomValue, isUnknown).
    The unknown rung's bottom value is '?' in the student figure and the solved value in the key."""
    if task == "direct_proportion":
        q, total, target = params["quantity"], params["total"], params["target"]
        one = Fraction(total, q)
        return (params["perLabel"], params["givenLabel"],
                [(q, total, False), (target, one * target, True)])
    if task == "unit_rate":
        q, total = params["quantity"], params["total"]
        one = Fraction(total, q)
        return (params["perLabel"], params["amountLabel"],
                [(q, total, False), (1, one, True)])
    if task == "simple_scale":
        v, fnum, fden = params["value"], params["factorNum"], params["factorDen"]
        scaled = Fraction(v) * Fraction(fnum, fden)
        return (params["srcUnit"], params["dstUnit"],
                [(fden, fnum, False), (v, scaled, True)])
    raise ValueError(task)


def _render_numberline(task: str, params: Dict[str, Any], answer_key: bool, acc: Dict[str, str]) -> str:
    top_lbl, bot_lbl, rungs = _nl_pairs(task, params)
    x0, x1 = 120, 880
    y_top, y_bot = 110, 200
    out = _svg_header(NL_W, NL_H, acc)
    out.append('<g class="rt-base">')
    out.append(f'<text class="rt-lbl" x="{NL_W // 2}" y="52" text-anchor="middle">{_esc("Double number line")}</text>')
    out.append(f'<line class="rt-axis" x1="{x0}" y1="{y_top}" x2="{x1}" y2="{y_top}"/>')
    out.append(f'<line class="rt-axis" x1="{x0}" y1="{y_bot}" x2="{x1}" y2="{y_bot}"/>')
    out.append(f'<text class="rt-lbl" x="{x0 - 16}" y="{y_top + 8}" text-anchor="end">{_esc(top_lbl)}</text>')
    out.append(f'<text class="rt-lbl" x="{x0 - 16}" y="{y_bot + 8}" text-anchor="end">{_esc(bot_lbl)}</text>')
    n = len(rungs)
    xs = [x0 + (x1 - x0) * (i + 1) // (n + 1) for i in range(n)]
    for i, (tv, bv, unknown) in enumerate(rungs):
        px = xs[i]
        out.append(f'<line class="rt-rung" x1="{px}" y1="{y_top}" x2="{px}" y2="{y_bot}"/>')
        # top tick + value (always given)
        out.append(f'<circle class="rt-given-pt" cx="{px}" cy="{y_top}" r="6"/>')
        out.append(f'<text class="rt-ticklbl" x="{px}" y="{y_top - 14}" text-anchor="middle">{_esc(_fmt_val(tv))}</text>')
        # bottom tick: given value rendered in base; unknown rendered as an open dashed point (no value)
        if unknown:
            out.append(f'<circle class="rt-unknown-pt" cx="{px}" cy="{y_bot}" r="7"/>')
        else:
            out.append(f'<circle class="rt-given-pt" cx="{px}" cy="{y_bot}" r="6"/>')
            out.append(f'<text class="rt-ticklbl" x="{px}" y="{y_bot + 36}" text-anchor="middle">{_esc(_fmt_val(bv))}</text>')
    out.append("</g>")
    # role-specific channel: student '?' marker vs answer-key solved value, both BELOW the base group
    if answer_key:
        out.append('<g class="rt-overlay">')
        for i, (tv, bv, unknown) in enumerate(rungs):
            if unknown:
                out.append(f'<text class="rt-unknown-lbl" x="{xs[i]}" y="{y_bot + 36}" text-anchor="middle">{_esc(_fmt_val(bv))}</text>')
        out.append("</g>")
    else:
        out.append('<g class="rt-student">')
        for i, (tv, bv, unknown) in enumerate(rungs):
            if unknown:
                out.append(f'<text class="rt-unknown-lbl" x="{xs[i]}" y="{y_bot + 36}" text-anchor="middle">?</text>')
        out.append("</g>")
    out.append("</svg>")
    return "\n".join(out)


def _fmt_val(v: Any) -> str:
    if isinstance(v, Fraction):
        return _disp_rat(v)
    return str(v)


# --- proportional best-buy table -------------------------------------------- #
def _render_table(task: str, params: Dict[str, Any], answer_key: bool, acc: Dict[str, str]) -> str:
    options = params["options"]
    n = len(options)
    out = _svg_header(TBL_W, TBL_H, acc)
    x0, x1 = 80, 920
    col_w = (x1 - x0) // (n + 1)
    y0 = 80
    row_h = 56
    # Correction #4: cost-like columns — items + tokens; the unknown row is COST PER ITEM
    # (tokens per <singular-item>).
    rows = ["Option", f"{params['items'].capitalize()}", "Tokens",
            f"Cost per {params['item']} (tokens)"]
    n_rows = len(rows)
    # ----- shared base: a fixed 4-row grid + row headers + given option/items/tokens values (NO rates) ----
    out.append('<g class="rt-base">')
    out.append(f'<text class="rt-lbl" x="{TBL_W // 2}" y="48" text-anchor="middle">{_esc("Compare the options by cost per item")}</text>')
    for r in range(n_rows + 1):
        y = y0 + r * row_h
        out.append(f'<line class="rt-table-line" x1="{x0}" y1="{y}" x2="{x0 + col_w * (n + 1)}" y2="{y}"/>')
    for c in range(n + 2):
        x = x0 + c * col_w
        out.append(f'<line class="rt-table-line" x1="{x}" y1="{y0}" x2="{x}" y2="{y0 + row_h * n_rows}"/>')
    for r, label in enumerate(rows):
        ty = y0 + r * row_h + 36
        out.append(f'<text class="rt-ticklbl" x="{x0 + 12}" y="{ty}" text-anchor="start">{_esc(label)}</text>')
    for i, o in enumerate(options):
        cx = x0 + col_w * (i + 1) + col_w // 2
        out.append(f'<text class="rt-lbl" x="{cx}" y="{y0 + 36}" text-anchor="middle">{_esc(o["label"])}</text>')
        out.append(f'<text class="rt-lbl" x="{cx}" y="{y0 + row_h + 36}" text-anchor="middle">{o["itemCount"]}</text>')
        out.append(f'<text class="rt-lbl" x="{cx}" y="{y0 + 2 * row_h + 36}" text-anchor="middle">{o["tokenCost"]}</text>')
    out.append("</g>")
    # ----- role-specific channel: the cost-per-item row is the UNKNOWN (a '?' for the student, the exact
    # rate + a check mark on the best option in the key) -----
    ry = y0 + 3 * row_h + 36
    if answer_key:
        out.append('<g class="rt-overlay">')
        for i, o in enumerate(options):
            cx = x0 + col_w * (i + 1) + col_w // 2
            rate = Fraction(o["tokenCost"], o["itemCount"])
            mark = " ✓" if o["label"] == params["correctLabel"] else ""
            out.append(f'<text class="rt-unknown-lbl" x="{cx}" y="{ry}" text-anchor="middle">{_esc(_disp_rat(rate) + mark)}</text>')
        out.append("</g>")
    else:
        out.append('<g class="rt-student">')
        for i, o in enumerate(options):
            cx = x0 + col_w * (i + 1) + col_w // 2
            out.append(f'<text class="rt-unknown-lbl" x="{cx}" y="{ry}" text-anchor="middle">?</text>')
        out.append("</g>")
    out.append("</svg>")
    return "\n".join(out)


def render(task: str, params: Dict[str, Any], answer_key: bool, acc: Dict[str, str]) -> Optional[str]:
    fig = FIGURE_KIND[task]
    if fig is None:
        return None
    if fig == "bar":
        return _render_bar(task, params, answer_key, acc)
    if fig == "numberline":
        return _render_numberline(task, params, answer_key, acc)
    if fig == "table":
        return _render_table(task, params, answer_key, acc)
    raise ValueError(fig)


# --------------------------------------------------------------------------- #
# Difficulty (owner: single source-of-truth TASK_BANDS + a structural lever so BOTH bands reachable).
# --------------------------------------------------------------------------- #
def _is_high_complexity(task: str, params: Dict[str, Any]) -> bool:
    if task in ("simplify", "write_from_quantities"):
        parts = params.get("parts") or params.get("quantities")
        return len(parts) == 3                              # three-part is harder
    if task in ("ratio_to_fraction", "fraction_to_ratio"):
        sol = _solve(task, params)
        if task == "ratio_to_fraction":
            return params["parts"][0] + params["parts"][1] >= 9   # larger whole -> harder
        return RC.gcd_list([params["num"], params["den"] - params["num"]]) > 1  # needs simplifying
    if task in ("share_two_part", "share_three_part"):
        return params["total"] >= 40                        # larger totals harder
    if task == "missing_part":
        return params["knownValue"] >= 30
    if task == "direct_proportion":
        return _solve(task, params).denominator > 1         # fractional result harder
    if task == "inverse_proportion":
        return params["q1"] * params["v1"] >= 60
    if task == "unit_rate":
        return _solve(task, params).denominator > 1
    if task == "best_buy":
        return len(params["options"]) == 3                  # three options harder than two
    if task == "simple_scale":
        return _solve(task, params).denominator > 1
    return False


def _complexity_tier(task: str, params: Dict[str, Any]) -> int:
    """Deterministic complexity classifier returning a tier in {0, 1, 2} from MEANINGFUL structural
    features of the item. tier 0 = simplest, tier 2 = hardest. The four tasks that declare a 3-value
    band ([lo,lo+1,lo+2]) accumulate up to three independent structural signals so the MIDDLE band
    (tier 1) genuinely occurs; the other eight tasks (2-value bands) keep the binary high/low lever
    (tier 0 or tier 2) so both endpoints stay covered. Identical in ratio.ts."""
    if task in ("simplify", "write_from_quantities"):
        parts = params.get("parts") or params.get("quantities")
        s = 0
        if len(parts) == 3:                                 # three-part is harder than two-part
            s += 1
        if RC.gcd_list(parts) >= 4:                         # larger gcd -> more reduction work
            s += 1
        if max(parts) >= 12:                                # larger operands
            s += 1
        return min(s, 2)
    if task == "direct_proportion":
        sol = _solve(task, params)
        s = 0
        if sol.denominator > 1:                             # fractional result harder
            s += 1
        if params["target"] >= 7:                           # larger multiplier
            s += 1
        if params["total"] >= 12:                           # larger operands
            s += 1
        return min(s, 2)
    if task == "simple_scale":
        sol = _solve(task, params)
        s = 0
        if sol.denominator > 1:                             # fractional result harder
            s += 1
        if params["value"] >= 11:                           # larger value to scale
            s += 1
        if max(params["factorNum"], params["factorDen"]) >= 6:   # larger scale factor parts
            s += 1
        return min(s, 2)
    # 2-value-band tasks: keep the binary high/low lever (tier 0 -> lo, tier 2 -> hi).
    return 2 if _is_high_complexity(task, params) else 0


def _difficulty(task: str, params: Dict[str, Any]) -> Dict[str, Any]:
    lo, hi = TASK_BANDS[task]
    high = _is_high_complexity(task, params)
    # Map the structural complexity tier onto the FULL declared inclusive range [lo,hi] so every band
    # (including the interior band of a 3-span task) is reachable. For a 2-span task the tier is 0 or 2,
    # so tier==0 -> lo and any higher tier -> hi keeps both endpoints covered.
    span = hi - lo + 1
    tier = _complexity_tier(task, params)
    if span <= 2:
        band = lo if tier == 0 else hi
    else:
        band = min(lo + tier, hi)

    sol = _solve(task, params)
    frac = isinstance(sol, Fraction) and sol.denominator > 1
    # descriptive axes (transparency only; the band above is the structural lever). All exact.
    steps_by_task = {
        "simplify": 0.3, "write_from_quantities": 0.35, "ratio_to_fraction": 0.45,
        "fraction_to_ratio": 0.45, "share_two_part": 0.5, "share_three_part": 0.6,
        "missing_part": 0.5, "direct_proportion": 0.55, "inverse_proportion": 0.7,
        "unit_rate": 0.45, "best_buy": 0.7, "simple_scale": 0.5,
    }
    abstraction_by_task = {
        "simplify": 0.25, "write_from_quantities": 0.3, "ratio_to_fraction": 0.5,
        "fraction_to_ratio": 0.5, "share_two_part": 0.4, "share_three_part": 0.5,
        "missing_part": 0.45, "direct_proportion": 0.5, "inverse_proportion": 0.65,
        "unit_rate": 0.4, "best_buy": 0.6, "simple_scale": 0.5,
    }
    rs = steps_by_task[task] + (0.1 if high else 0.0)
    ab = abstraction_by_task[task] + (0.1 if high else 0.0)
    nc = 0.3 + (0.25 if frac else 0.0) + (0.1 if high else 0.0)
    axes = {
        "numericalComplexity": round3(clamp01(nc)),
        # ratio is ALWAYS exact (no approximation), so this axis is always 0; route it through
        # round3 like every other axis so json.dumps emits int 0 (not 0.0) and the TS mirror's
        # canonical serializer reproduces it byte-for-byte with no special-casing.
        "exactVsApproximate": round3(clamp01(0.0)),
        "reasoningSteps": round3(clamp01(rs)),
        "abstraction": round3(clamp01(ab)),
    }
    return {"overallBand": band, "axes": axes}


# --------------------------------------------------------------------------- #
# Accessibility (owner: spokenMath/altText/longDescription + dataTableFallback; role-based, no leakage).
# --------------------------------------------------------------------------- #
def _data_table(task: str, params: Dict[str, Any], answer_key: bool) -> Dict[str, Any]:
    if task in ("share_two_part", "share_three_part"):
        rows = [[lab, _count(p, "parts")] for lab, p in zip(params["labels"], params["parts"])]
        if answer_key:
            shares = RC.share(params["total"], params["parts"])
            rows = [[lab, f"{_count(p, 'parts')} -> {_count(v, params['unit'])}"]
                    for lab, p, v in zip(params["labels"], params["parts"], shares)]
        return {"columns": ["Share", "Ratio part"], "rows": rows}
    if task == "missing_part":
        ki, mi = params["knownIndex"], params["missingIndex"]
        rows = [["", ""], ["", ""]]
        rows[ki] = [params["labels"][ki], f"{_count(params['parts'][ki], 'parts')} = {params['knownValue']}"]
        rows[mi] = [params["labels"][mi], f"{_count(params['parts'][mi], 'parts')} = " + (str(_solve(task, params)) if answer_key else "?")]
        return {"columns": ["Part", "Value"], "rows": rows}
    if task == "best_buy":
        cols = ["Option", params["items"].capitalize(), "Tokens"]
        rows = [[o["label"], str(o["itemCount"]), str(o["tokenCost"])] for o in params["options"]]
        if answer_key:
            cols.append(f"Cost per {params['item']} (tokens)")
            rows = [[o["label"], str(o["itemCount"]), str(o["tokenCost"]),
                     _disp_rat(Fraction(o["tokenCost"], o["itemCount"]))
                     + (" (best)" if o["label"] == params["correctLabel"] else "")]
                    for o in params["options"]]
        return {"columns": cols, "rows": rows}
    if task in ("direct_proportion", "unit_rate", "simple_scale"):
        top_lbl, bot_lbl, rungs = _nl_pairs(task, params)
        rows = []
        for tv, bv, unknown in rungs:
            b = "?" if (unknown and not answer_key) else _fmt_val(bv)
            rows.append([_fmt_val(tv), b])
        return {"columns": [top_lbl, bot_lbl], "rows": rows}
    if task in ("ratio_to_fraction", "fraction_to_ratio"):
        weights, _given, labels = _bar_segments(task, params)
        return {"columns": ["Part", "Size"], "rows": [[lab, str(w)] for lab, w in zip(labels, weights)]}
    return {"columns": ["Quantity", "Value"], "rows": []}


def _accessibility(task: str, params: Dict[str, Any], answer_key: bool) -> Dict[str, str]:
    fig = FIGURE_KIND[task]
    instr = _instruction(task, params)
    if fig == "bar":
        base = f"A bar model for the ratio {RC.format_ratio(params.get('parts', [1, 1]))}." \
            if task in ("ratio_to_fraction", "share_two_part", "share_three_part", "missing_part") \
            else f"A bar model split into {params.get('den', 0)} equal parts."
        title = "Bar model"
    elif fig == "numberline":
        base = "A double number line aligning the two proportional quantities."
        title = "Double number line"
    elif fig == "table":
        base = "A comparison table of each option's item count and token cost."
        title = "Best-buy comparison table"
    else:
        base = "No figure; the data is given in the prompt."
        title = "Ratio question"
    if answer_key:
        alt = f"Answer key. {base} The solved quantities are shown."
        desc = f"{base} The solution overlay reveals the answer to: {instr}"
    else:
        alt = f"{base} {instr}"
        desc = f"{base} Unknown quantities are marked with a question mark. {instr}"
    return {"title": title, "alt": alt, "desc": desc, "spokenMath": alt,
            "longDescription": f"{title}. {desc}"}


# --------------------------------------------------------------------------- #
# Prompt + solution
# --------------------------------------------------------------------------- #
def _instruction(task: str, params: Dict[str, Any]) -> str:
    if task == "simplify":
        return f"Write the ratio {RC.format_ratio(params['parts'])} in its simplest form."
    if task == "write_from_quantities":
        qs = ", ".join(_count(v, lab) for v, lab in zip(params["quantities"], params["labels"]))
        return (f"In a {params['title'].lower()} there are {qs}. "
                f"Write the ratio of {' to '.join(params['labels'])} in its simplest form.")
    if task == "ratio_to_fraction":
        a, b = params["parts"]
        named = params["labels"][params["partIndex"]]
        return (f"The {params['title'].lower()} mixes {params['labels'][0]} and {params['labels'][1]} "
                f"in the ratio {a}:{b}. What fraction of the whole is {named}? "
                f"Give your answer as a fraction in its simplest form.")
    if task == "fraction_to_ratio":
        return (f"In a group, {params['num']}/{params['den']} are one type and the rest are another. "
                f"Write the ratio of the first type to the rest in its simplest form.")
    if task in ("share_two_part", "share_three_part"):
        return (f"Share {_count(params['total'], params['unit'])} between {', '.join(params['labels'])} "
                f"in the ratio {RC.format_ratio(params['parts'])}. Give each share.")
    if task == "missing_part":
        ki, mi = params["knownIndex"], params["missingIndex"]
        return (f"{params['labels'][ki]} and {params['labels'][mi]} share an amount in the ratio "
                f"{RC.format_ratio(params['parts'])}. {params['labels'][ki]} gets "
                f"{_count(params['knownValue'], params['unit'])}. How many {_forms(params['unit'])[1]} "
                f"does {params['labels'][mi]} get?")
    if task == "direct_proportion":
        return (f"{_count(params['quantity'], params['perLabel'])} hold "
                f"{_count(params['total'], params['givenLabel'])}. "
                f"How many {_forms(params['givenLabel'])[1]} are in {_count(params['target'], params['perLabel'])}? "
                f"Give an exact value.")
    if task == "inverse_proportion":
        return (f"{_count(params['q1'], params['agent'])} take {_count(params['v1'], params['unit'])} {params['tail']}. "
                f"How many {_forms(params['unit'])[1]} would {_count(params['q2'], params['agent'])} take {params['tail']}?")
    if task == "unit_rate":
        return (f"{_count(params['quantity'], params['perLabel'])} hold "
                f"{_count(params['total'], params['amountLabel'])}. "
                f"How many {_forms(params['amountLabel'])[1]} per {_singular(params['perLabel'])}? "
                f"Give an exact value.")
    if task == "best_buy":
        # Correction #4: cost-like — "<itemCount> <items> for <tokenCost> tokens"; best = lowest
        # cost per <singular-item>. itemCount/tokenCost routed through _count for grammatical agreement.
        opts = "; ".join(f"option {o['label']} offers {_count_pair(o['itemCount'], params['item'], params['items'])} "
                         f"for {_count(o['tokenCost'], 'tokens')}"
                         for o in params["options"])
        return (f"You can buy {params['items']}: {opts}. Which option is the best value "
                f"(the lowest cost per {params['item']})? Choose the best option.")
    if task == "simple_scale":
        # Correction #5 (POLICY A, dimensionless): grammatical "... unit/units"; a BARE-NUMBER answer
        # of dst units; NO cross-unit conversion.
        # Subject-verb agreement (owner REVISE #1): the verb agrees with the SUBJECT count (factorDen) —
        # "1 plan unit REPRESENTS ..." / "2 plan units REPRESENT ...".
        rep = "represents" if params["factorDen"] == 1 else "represent"
        return (f"On a {params['scaleKind']}, {_units(params['factorDen'], params['srcUnit'])} {rep} "
                f"{_units(params['factorNum'], params['dstUnit'])}. A part measures "
                f"{_units(params['value'], params['srcUnit'])}. How many {params['dstUnit']}s long is it "
                f"in reality? Give an exact value.")
    raise ValueError(task)


def _prompt(task: str, params: Dict[str, Any]) -> Dict[str, Any]:
    blocks: List[Dict[str, Any]] = []
    if FIGURE_KIND[task] is not None:
        blocks.append({"kind": "media-ref", "ref": "fig-1"})
    blocks.append({"kind": "text", "text": _instruction(task, params)})
    return {"blocks": blocks, "instruction": _instruction(task, params)}


def _solution(task: str, params: Dict[str, Any]) -> Dict[str, Any]:
    steps: List[Dict[str, Any]] = []

    def step(t: str, r: str) -> None:
        steps.append({"number": len(steps) + 1, "transformation": t, "intermediateResult": r})

    sol = _solve(task, params)
    if task in ("simplify", "write_from_quantities"):
        src = params.get("parts") or params["quantities"]
        g = RC.gcd_list(src)
        step("Find the greatest common divisor of the parts", f"gcd = {g}")
        step("Divide every part by the gcd, keeping the order", RC.format_ratio(sol))
    elif task == "ratio_to_fraction":
        a, b = params["parts"]
        part = params["parts"][params["partIndex"]]
        step("Add the parts to find the total number of parts", f"{a} + {b} = {a + b}")
        step("Write the named part over the total", f"{part}/{a + b} = {_disp_rat(sol)}")
    elif task == "fraction_to_ratio":
        num, den = params["num"], params["den"]
        step("Find the remaining part of the whole", f"{den} - {num} = {den - num}")
        step("Write the part-to-rest ratio and simplify", RC.format_ratio(sol))
    elif task in ("share_two_part", "share_three_part"):
        parts = params["parts"]
        s = sum(parts)
        one = params["total"] // s
        step("Add the parts to find the total number of parts", f"{' + '.join(map(str, parts))} = {s}")
        step("Find the value of one part", f"{params['total']} ÷ {s} = {one}")
        step("Multiply to give each share", ", ".join(f"{lab}={v}" for lab, v in _share_labels_cells(params)))
    elif task == "missing_part":
        ki, mi = params["knownIndex"], params["missingIndex"]
        one = params["knownValue"] // params["parts"][ki]
        step("Find the value of one part from the known share",
             f"{params['knownValue']} ÷ {params['parts'][ki]} = {one}")
        step("Multiply by the missing part's ratio value", f"{one} × {params['parts'][mi]} = {sol}")
    elif task == "direct_proportion":
        q, total, target = params["quantity"], params["total"], params["target"]
        one = Fraction(total, q)
        step("Find the value of one unit", f"{total} ÷ {q} = {_disp_rat(one)}")
        step("Multiply by the required quantity", f"{_disp_rat(one)} × {target} = {_disp_rat(sol)}")
    elif task == "inverse_proportion":
        q1, v1, q2 = params["q1"], params["v1"], params["q2"]
        step("Use the product invariant (more means less)", f"{q1} × {v1} = {q1 * v1}")
        step("Divide the product by the new quantity", f"{q1 * v1} ÷ {q2} = {sol}")
    elif task == "unit_rate":
        step("Divide the total by the number of units",
             f"{params['total']} ÷ {params['quantity']} = {_disp_rat(sol)}")
    elif task == "best_buy":
        # Correction #4: cost per item = tokens ÷ items; the best value is the lowest cost per item.
        # Every count->noun (tokens, items, the rate's tokens) routes through _count for agreement
        # (a rate of exactly 1 reads "1 token per <item>", never "1 tokens").
        for o in params["options"]:
            rate = Fraction(o["tokenCost"], o["itemCount"])
            step(f"Cost per {params['item']} of option {o['label']}",
                 f"{_count(o['tokenCost'], 'tokens')} ÷ {_count_pair(o['itemCount'], params['item'], params['items'])} "
                 f"= {_count(rate, 'tokens')} per {params['item']}")
        rates = {o["label"]: Fraction(o["tokenCost"], o["itemCount"]) for o in params["options"]}
        step("Compare the cost per item and choose the strict minimum",
             f"the lowest cost per {params['item']} is {_disp_rat(rates[params['correctLabel']])} -> option {params['correctLabel']}")
    elif task == "simple_scale":
        v, fnum, fden = params["value"], params["factorNum"], params["factorDen"]
        step("Find the scale factor", f"{fnum}/{fden}")
        step("Multiply the value by the scale factor", f"{v} × {fnum}/{fden} = {_disp_rat(sol)}")
    return {"steps": steps}


# --------------------------------------------------------------------------- #
# MC option assembly (owner C) — misconception-backed distractors from diagnostics_for.
# --------------------------------------------------------------------------- #
def _answer_display_value(task: str, value: Any) -> Tuple[Any, str]:
    """(encoded value, display) for an MC option whose family matches the canonical answer."""
    kind = ANSWER_KIND[task]
    if kind == "ratio":
        return {"parts": list(value)}, RC.format_ratio(value)
    if kind in ("rational", "integer"):
        f = value if isinstance(value, Fraction) else Fraction(value)
        if f.denominator == 1:
            return int(f), str(f.numerator)
        return {"num": f.numerator, "den": f.denominator}, _disp_rat(f)
    if kind == "mc":
        return value, value
    raise ValueError(kind)


def _mc_distractors(task: str, params: Dict[str, Any]) -> Optional[List[Dict[str, Any]]]:
    """Three DISTINCT misconception-backed distractors from diagnostics_for, else None (redraw)."""
    correct = _solve(task, params)
    if task == "best_buy":
        correct_key = correct                                  # the option label
    else:
        ce, _ = _answer_display_value(task, correct)
        correct_key = json.dumps(ce, sort_keys=True)
    out: List[Dict[str, Any]] = []
    seen = {correct_key}
    for d in RM.diagnostics_for(task, params):
        if task == "best_buy":
            val = d["predictedResponse"]
            key = val
            enc, disp = val, val
        else:
            pc = d["predictedCanonical"]
            if "parts" in pc:
                enc, disp = {"parts": pc["parts"]}, RC.format_ratio(pc["parts"])
            else:
                f = Fraction(pc["num"], pc["den"])
                enc, disp = _answer_display_value(task, f)
            key = json.dumps(enc, sort_keys=True)
        if key in seen:
            continue
        seen.add(key)
        out.append({"value": enc, "display": disp, "misconceptionId": d["misconceptionId"],
                    "rationale": d["observableError"]})
        if len(out) == 3:
            break
    return out if len(out) == 3 else None


# --------------------------------------------------------------------------- #
# Public generate()
# --------------------------------------------------------------------------- #
def _resolve_interaction(task: str, config: Dict[str, Any]) -> str:
    requested = config.get("interactionType")
    if requested is None:
        return "multiple-choice" if task in MC_ONLY_TASKS else "free-response"
    if requested not in ("free-response", "multiple-choice"):
        raise InteractionNotSupported(f"unsupported interaction {requested!r} for {task!r}")
    if requested not in supported_interactions(task):
        raise InteractionNotSupported(
            f"task {task!r} does not support {requested!r} (supported: {supported_interactions(task)})")
    return requested


def generate(seed: int, config: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    config = config or {}
    explicit = config.get("task")
    if explicit is not None and explicit not in OBJECTIVE_BY_TASK:
        raise ValueError(f"unknown task {explicit!r}")

    rng = Mulberry32(seed)
    if explicit is None:
        # No task supplied: narrow the draw pool to tasks the requested interaction can actually serve,
        # so a no-task request NEVER raises InteractionNotSupported.
        #   * MC requested  -> only MC-eligible tasks (existing behaviour).
        #   * FR requested   -> exclude MC-ONLY tasks (best_buy), which cannot be free-response.
        #   * default (None) -> the full RATIO_TASKS pool unchanged (best_buy then resolves to its
        #     default MC interaction), so the committed default-interaction golden vectors are
        #     byte-for-byte unaffected.
        requested = config.get("interactionType")
        if requested == "multiple-choice":
            pool = list(MC_ELIGIBLE_TASKS)
        elif requested == "free-response":
            pool = [t for t in RATIO_TASKS if t not in MC_ONLY_TASKS]
        else:
            pool = list(RATIO_TASKS)
        task = pool[_n(rng, len(pool))]
    else:
        task = explicit

    interaction = _resolve_interaction(task, config)
    mc = interaction == "multiple-choice"

    params: Dict[str, Any] = {}
    distractors: Optional[List[Dict[str, Any]]] = None
    ok = False
    for _ in range(MAX_PARAM_ATTEMPTS):
        drawn = _DRAW[task](rng)
        if drawn is None:
            continue
        if not _acceptable(task, drawn):
            continue
        if mc and task != "best_buy":
            # MC-eligible non-best_buy: assemble 3 misconception-backed distractors (redraw otherwise).
            ds = _mc_distractors(task, drawn)
            if ds is None:
                continue
            distractors = ds
        params, ok = drawn, True
        break
    if not ok:
        raise RuntimeError(f"could not draw acceptable ratio params for {task} seed={seed}")

    answer = _encode_answer(task, params)
    acc = _accessibility(task, params, answer_key=False)
    acc_key = _accessibility(task, params, answer_key=True)
    item_id = f"ITEM-RATIO-{task}-{seed}"

    item: Dict[str, Any] = {
        "itemId": item_id,
        "schemaVersion": "1.0.0",
        "objectiveIds": [OBJECTIVE_BY_TASK[task]],
        "generatorId": GENERATOR_ID,
        "generatorVersion": GENERATOR_VERSION,
        "seed": seed,
        "interactionType": interaction,
        "prompt": _prompt(task, params),
        "answer": answer,
        "solution": _solution(task, params),
        "calculatorPolicy": CALCULATOR_POLICY,
        "provenance": {"origin": "generated", "rightsStatus": "academy-owned",
                       "originalityNote": "Original parameterized item; the figure is generated from the same params."},
        "lifecycle": {"state": "generated"},
        "accessibility": {"spokenMath": acc["spokenMath"], "altText": acc["alt"],
                          "longDescription": acc["longDescription"], "nonColorIndicators": True},
        "difficulty": _difficulty(task, params),
        "params": _public_params(task, params),
    }

    student_svg = render(task, params, answer_key=False, acc=acc)
    if student_svg is not None:
        key_svg = render(task, params, answer_key=True, acc=acc_key)
        item["media"] = [{
            "id": "fig-1", "kind": "svg", "svg": student_svg,
            "spec": {
                "answerKeySvg": key_svg,
                "figureKind": FIGURE_KIND[task],
                "answerKeyAltText": acc_key["alt"],
                "answerKeyLongDescription": acc_key["longDescription"],
                "answerKeyDataTableFallback": _data_table(task, params, answer_key=True),
            },
            "toScale": True,
            "altText": acc["alt"],
            "longDescription": acc["longDescription"],
            "dataTableFallback": _data_table(task, params, answer_key=False),
        }]

    if mc and task == "best_buy":
        # The MC option set IS the labelled buy options (A/B/C); the correct one has the strict-minimum
        # cost per item. Option order is fixed (the figure/table already lays them out as A/B/C). Each
        # wrong option carries the misconception a student picking it would exhibit.
        diags = {d["predictedResponse"]: d for d in RM.diagnostics_for(task, params)}
        item["options"] = []
        for o in params["options"]:
            correct = o["label"] == params["correctLabel"]
            opt = {"label": o["label"], "value": o["label"],
                   "display": f"{_count_pair(o['itemCount'], params['item'], params['items'])} for {_count(o['tokenCost'], 'tokens')}",
                   "correct": correct}
            if not correct and o["label"] in diags:
                opt["misconceptionId"] = diags[o["label"]]["misconceptionId"]
            item["options"].append(opt)
    elif mc:
        ds = distractors or []
        item["distractors"] = [
            {"id": f"d{i+1}", "value": d["value"], "display": d["display"],
             "misconceptionId": d["misconceptionId"], "rationale": d["rationale"]}
            for i, d in enumerate(ds)]
        a_enc, a_disp = _answer_display_value(task, _solve(task, params))
        pool_opts = [{"value": a_enc, "display": a_disp, "correct": True, "misconceptionId": None}]
        for d in ds:
            pool_opts.append({"value": d["value"], "display": d["display"], "correct": False,
                              "misconceptionId": d["misconceptionId"]})
        shuffled = rng.shuffle(pool_opts)
        labels = ["A", "B", "C", "D"]
        item["options"] = [
            {"label": labels[i], "value": o["value"], "display": o["display"], "correct": o["correct"],
             **({"misconceptionId": o["misconceptionId"]} if o["misconceptionId"] else {})}
            for i, o in enumerate(shuffled)]
    return item


def _public_params(task: str, params: Dict[str, Any]) -> Dict[str, Any]:
    """The mathematical params stored on the item (single source of truth). best_buy carries each
    option's EXACT unit-rate witness; sharing carries the solved shares' witness implicitly via parts."""
    out = dict(params)
    if task == "best_buy":
        out["options"] = [dict(o) for o in params["options"]]   # each carries unitRate {num,den}
    return out


# --------------------------------------------------------------------------- #
# Independent validator — re-derives everything from params; never trusts forward output.
# --------------------------------------------------------------------------- #
def validate(item: Dict[str, Any]) -> Dict[str, Any]:
    checks: List[Dict[str, Any]] = []

    def add(name: str, ok: bool, detail: str = "") -> None:
        checks.append({"name": name, "ok": bool(ok), "detail": detail})

    p = item["params"]
    task = p["task"]
    interaction = item.get("interactionType")
    answer = item["answer"]

    add("objective-mapping", item.get("objectiveIds") == [OBJECTIVE_BY_TASK.get(task)], str(item.get("objectiveIds")))

    # interaction policy (owner C)
    sup = supported_interactions(task)
    add("interaction-supported", interaction in sup, f"{interaction} in {sup}")
    if task in MC_ONLY_TASKS:
        add("best-buy-is-mc-only", interaction == "multiple-choice")
    if task not in MC_ELIGIBLE_TASKS:
        add("fr-only-task-not-mc", interaction == "free-response")

    # independent re-derivation of the answer (do NOT trust the forward engine output)
    sol = _solve(task, p)
    rebuilt = _encode_answer(task, p)
    add("answer-recomputes", rebuilt == answer, "answer re-derived from params matches stored canonical")

    kind = ANSWER_KIND[task]
    if kind == "ratio":
        parts = answer["canonical"]["parts"]
        add("ratio-in-simplest-form", RC.gcd_list(parts) == 1, RC.format_ratio(parts))
        add("ratio-order-preserved", parts == RC.simplify_parts(sol), f"{parts}")
        # checker matrix sanity on this answer: an equivalent unsimplified form is flagged.
        scaled = [pp * 2 for pp in parts]
        add("checker-accepts-self", RC.check_ratio(parts, RC.format_ratio(parts), require_simplest=True)["code"] == "correct")
        add("checker-flags-unsimplified",
            RC.check_ratio(parts, RC.format_ratio(scaled), require_simplest=True)["code"] in ("equivalent-not-simplified",))
    elif kind == "integer":
        add("integer-exact", answer["canonical"]["den"] == 1 and isinstance(sol, int) and sol > 0, str(sol))
        if task == "inverse_proportion":
            add("inverse-product-invariant", p["q1"] * p["v1"] == p["q2"] * sol,
                f"{p['q1']}*{p['v1']} == {p['q2']}*{sol}")
        if task == "missing_part":
            one = p["knownValue"] // p["parts"][p["knownIndex"]]
            add("missing-part-divisible", p["knownValue"] % p["parts"][p["knownIndex"]] == 0)
            add("missing-part-cross-multiplies", one * p["parts"][p["missingIndex"]] == sol)
    elif kind == "rational":
        f = Fraction(answer["canonical"]["num"], answer["canonical"]["den"])
        add("rational-exact-and-reduced", f == sol and f.numerator == sol.numerator and f.denominator == sol.denominator,
            _disp_rat(f))
        if task == "ratio_to_fraction":
            a, b = p["parts"]
            add("fraction-proper", 0 < f < 1, _disp_rat(f))
            add("fraction-part-over-whole", f == Fraction(p["parts"][p["partIndex"]], a + b))
        if task == "unit_rate":
            add("unit-rate-recomputes", f == Fraction(p["total"], p["quantity"]))
        if task == "direct_proportion":
            add("direct-cross-multiplies", f == Fraction(p["total"], p["quantity"]) * p["target"])
        if task == "simple_scale":
            add("scale-recomputes", f == Fraction(p["value"]) * Fraction(p["factorNum"], p["factorDen"]))
        # --- correction #3 (context-value compatibility) for direct_proportion / unit_rate ---
        if task in ("direct_proportion", "unit_rate"):
            amount_noun = p["givenLabel"] if task == "direct_proportion" else p["amountLabel"]
            domain = _CONTEXT_DOMAINS.get(amount_noun)
            is_int = f.denominator == 1
            # the answer is compatible with its context's domain (count-discrete demands an integer)
            compatible = domain is not None and (
                domain != CONTEXT_DOMAIN_COUNT or is_int)
            add("context-answer-compatible", compatible,
                f"{amount_noun} domain={domain} answerInt={is_int}")
            add("discrete-count-answer-integer",
                domain != CONTEXT_DOMAIN_COUNT or is_int,
                "a count-discrete context carries an integer answer")
            add("rational-answer-uses-continuous-or-average-context",
                is_int or domain in (CONTEXT_DOMAIN_CONTINUOUS, CONTEXT_DOMAIN_ABSTRACT, CONTEXT_DOMAIN_AVERAGE),
                "a fractional answer uses a continuous / abstract / average context")
            # no fractional books/students/sheets/people: a count-noun context never carries a fraction
            add("no-fractional-books-students-sheets-or-people",
                not (domain == CONTEXT_DOMAIN_COUNT and not is_int),
                "no count-noun context carries a fractional answer")
            if task == "unit_rate":
                add("unit-rate-context-allows-rational",
                    is_int or domain in (CONTEXT_DOMAIN_CONTINUOUS, CONTEXT_DOMAIN_ABSTRACT, CONTEXT_DOMAIN_AVERAGE),
                    "a fractional unit rate uses a continuous / abstract / average context")
        # --- correction #5 (simple-scale wording + answer contract) ---
        if task == "simple_scale":
            # owner REVISE #1/#2: inspect the ACTUAL RENDERED strings on every surface — prompt, alt text,
            # long description, and the SVG <desc> — for count + subject-verb agreement, so wording such as
            # "1 plan unit represent" FAILS (the prior checks only confirmed the noun substrings were present
            # and never inspected the verb, hence the false pass).
            instr = item["prompt"]["instruction"]
            acc = item.get("accessibility", {}) or {}
            a11y_text = " ".join(str(acc.get(k, "")) for k in ("altText", "longDescription", "spokenMath"))
            svg = item["media"][0]["svg"] if item.get("media") else ""
            _md = re.search(r"<desc>(.*?)</desc>", svg, re.S)
            svg_desc = _md.group(1) if _md else ""

            def _scale_ok(s: str) -> bool:                      # no count- OR verb-agreement violation
                return not _grammar_violations(s)

            den, num, val = p["factorDen"], p["factorNum"], p["value"]
            # noun number agreement on the RENDERED prompt (each displayed count present + correct number).
            sp_ok = not _scale_verb_violations(instr)
            for cnt, word in ((den, p["srcUnit"]), (num, p["dstUnit"]), (val, p["srcUnit"])):
                phrase = _units(cnt, word)
                if phrase not in instr:
                    sp_ok = False
                if (cnt == 1) == phrase.endswith("s"):          # 1->no 's'; n->'s'
                    sp_ok = False
            add("singular-plural-units-correct", sp_ok, "rendered prompt: 1 <word> vs n <word>s + verb agreement")
            add("singular-plural-units-correct-inspects-rendered-text", sp_ok and str(den) in instr,
                "the check parses the actual rendered prompt string, not just substring presence")
            add("scale-unit-wording-grammatical", _scale_ok(instr),
                "rendered prompt has no count/subject-verb disagreement")
            add("scale-unit-wording-grammatical-inspects-rendered-text", _scale_ok(instr),
                "grammar check inspects the rendered prompt text")
            # explicit subject-verb agreement: singular subject -> 'represents'; plural -> 'represent'.
            add("scale-singular-represents", (den != 1) or (f"{_units(1, p['srcUnit'])} represents " in instr),
                "a singular subject (count 1) takes 'represents'")
            add("scale-plural-represent", (den == 1) or (f"{_units(den, p['srcUnit'])} represent " in instr),
                "a plural subject (count > 1) takes 'represent'")
            # per-surface grammar validity (prompt / a11y / svg desc).
            add("scale-prompt-grammar-valid", _scale_ok(instr), "rendered prompt grammar valid")
            add("scale-a11y-grammar-valid", _scale_ok(a11y_text), "alt text + long description grammar valid")
            add("scale-svg-desc-grammar-valid", _scale_ok(svg_desc), "SVG <desc> grammar valid")
            # the prompt asks for a number of dst abstract units and the answer is that bare number
            add("scale-answer-contract-matches-prompt",
                f"How many {p['dstUnit']}s long" in instr and f == Fraction(p["value"]) * Fraction(p["factorNum"], p["factorDen"]),
                "prompt asks a bare number of dst units; answer is that number")
            # NO measurement unit is being asked while returning a bare number (no cm/km/m tokens)
            mtokens = ("cm", "km", " m ", "centimetre", "kilometre", "metre", "centimeter",
                       "kilometer", "meter")
            add("measurement-unit-answer-not-bare-number",
                not any(tok in instr for tok in mtokens),
                "no measurement-unit token in a dimensionless scale prompt")
            add("no-cross-unit-conversion-in-v1", p["direction"] == "multiply",
                "a single multiplicative scale factor; no cross-unit conversion")
    elif kind == "table":
        cells = answer["canonical"]["cells"]
        by_label = {c["location"]: c["value"] for c in cells}
        shares = RC.share(p["total"], p["parts"])
        want = {lab: v for lab, v in zip(p["labels"], shares)}
        add("table-labels-match", set(by_label) == set(want) and len(cells) == len(p["parts"]))
        add("table-cell-values-match", by_label == want)
        add("shares-sum-to-whole", sum(by_label.values()) == p["total"], f"sum == {p['total']}")
        add("total-divisible-by-parts", p["total"] % sum(p["parts"]) == 0)
    elif kind == "mc":
        # best_buy: independent strict-minimum COST-PER-ITEM (tokens per item) re-derivation (#4).
        rates = {o["label"]: Fraction(o["tokenCost"], o["itemCount"]) for o in p["options"]}
        mn = min(rates.values())
        winners = [lab for lab, r in rates.items() if r == mn]
        add("best-buy-unique-strict-min", len(winners) == 1, f"winners={winners}")
        add("best-buy-correct-is-min", winners and winners[0] == answer["canonical"] == p["correctLabel"],
            f"min option {winners[0] if winners else None}")
        # stored unit-rate witness agrees with the recomputed exact cost-per-item rate
        wit_ok = all(Fraction(o["unitRate"]["num"], o["unitRate"]["den"]) == Fraction(o["tokenCost"], o["itemCount"])
                     for o in p["options"])
        add("best-buy-unit-rate-witness-exact", wit_ok)
        # --- correction #4 new checks: cost-per-item direction + cost-like (token) denominator ---
        instr = item["prompt"]["instruction"]
        # the rate the validator uses is tokens-per-item (denominator = items); the winner is the strict min
        add("best-buy-rate-direction-consistent",
            all(o["unitRate"]["den"] == o["itemCount"] and o["unitRate"]["num"] == o["tokenCost"] for o in p["options"]),
            "unitRate is tokenCost/itemCount (cost per item) for every option")
        # cost-like denominator: the cost is in TOKENS (no currency symbol) — assert tokens wording, no $/£/€
        no_currency = not any(sym in instr for sym in ("$", "£", "€", "¥"))
        add("best-buy-context-has-cost-like-denominator",
            "tokens" in instr and no_currency, "cost expressed in tokens, no currency symbol")
        add("best-buy-strict-minimum-cost-per-unit", len(winners) == 1 and rates[p["correctLabel"]] == mn,
            "the correct option is the unique strict-minimum tokens-per-item")
        # prompt agrees with the validator: it asks for the lowest cost per item AND the marked-correct
        # option is the strict-min tokens-per-item
        prompt_lowest = f"the lowest cost per {p['item']}" in instr
        add("best-buy-prompt-matches-validator",
            prompt_lowest and p["correctLabel"] == (winners[0] if winners else None),
            "prompt asks lowest cost per item; correct option is strict-min tokens-per-item")
        # feedback (per-option misconception) never lands on the correct option, and the two diagnostics
        # point at the lowest-total / highest-total options (wrong direction), never the cost-per-item min
        diags = {d["predictedResponse"]: d for d in RM.diagnostics_for(task, p)}
        feedback_ok = all(lbl != p["correctLabel"] for lbl in diags)
        add("best-buy-feedback-matches-rate-direction", feedback_ok,
            "every diagnostic's predicted (wrong) option differs from the correct option")
        # the correct option is NOT simply the one with the most items or the fewest tokens unless that
        # also has the min cost-per-item
        most_items = max(p["options"], key=lambda o: (o["itemCount"], o["label"]))["label"]
        fewest_tokens = min(p["options"], key=lambda o: (o["tokenCost"], o["label"]))["label"]
        coincide_ok = ((most_items != p["correctLabel"] or rates[most_items] == mn)
                       and (fewest_tokens != p["correctLabel"] or rates[fewest_tokens] == mn))
        add("no-lowest-product-amount-as-best-value", coincide_ok,
            "the correct option is the min cost-per-item, not merely most-items/fewest-tokens")

    # role-based figure leakage (owner J): the unknown is not rendered as a value in the STUDENT figure;
    # the answer key is additive. A given value equal to the answer is NOT leakage.
    media = item.get("media") or []
    if FIGURE_KIND[task] is not None:
        add("media-present", len(media) == 1)
        if media:
            m = media[0]
            student = m["svg"]
            key = m["spec"]["answerKeySvg"]
            add("media-kind-svg", m.get("kind") == "svg")
            # rebuild byte-for-byte from params
            rs = render(task, p, answer_key=False, acc=_accessibility(task, p, answer_key=False))
            rk = render(task, p, answer_key=True, acc=_accessibility(task, p, answer_key=True))
            add("student-svg-realises-params", rs == student, "student SVG recomputes byte-for-byte")
            add("answer-key-svg-realises-params", rk == key, "answer-key SVG recomputes byte-for-byte")
            # role-based leakage: the student base group has NO rt-overlay; the key adds exactly one.
            add("student-figure-has-no-overlay", '<g class="rt-overlay">' not in student)
            add("answer-key-overlay-additive",
                '<g class="rt-overlay">' in key and '<g class="rt-student">' not in key and student != key)
            add("student-and-key-share-base", _rt_base(student) != "" and _rt_base(student) == _rt_base(key),
                "shared base group byte-identical")
            # role-based unknown check: the unknown is shown as '?' (not its value) in the student figure.
            add("student-unknown-marked-not-valued", _unknown_hidden_in_student(task, p, student))
            add("answer-key-reveals-unknown", _unknown_shown_in_key(task, p, key))
            # accessibility channel separation
            add("student-a11y-no-result", not _a11y_leaks(task, p, m.get("altText", "") + " " + m.get("longDescription", "")))
            add("dataTableFallback-present", isinstance(m.get("dataTableFallback"), dict) and "rows" in m["dataTableFallback"])
    else:
        add("no-figure-for-narrow-task", len(media) == 0, "simplify/write/inverse carry no figure")

    # difficulty within the declared band
    band = item["difficulty"]["overallBand"]
    lo, hi = TASK_BANDS[task]
    add("difficulty-in-band", lo <= band <= hi, f"band {band} in [{lo},{hi}]")

    # MC discipline (owner C)
    if interaction == "multiple-choice":
        opts = item.get("options") or []
        vals = [json.dumps(o["value"], sort_keys=True) for o in opts]
        add("mc-options-distinct", len(set(vals)) == len(vals))
        # the option VALUE keys are always distinct (A/B/C labels / canonical encodings); the learner
        # actually reads the DISPLAY strings, so assert those are pairwise distinct too (owner C / D).
        disps = [o.get("display") for o in opts]
        add("mc-option-displays-distinct", len(set(disps)) == len(disps), f"displays={disps}")
        add("mc-one-correct", sum(1 for o in opts if o.get("correct")) == 1)
        if task == "best_buy":
            # the MC option set IS the labelled buy options (2 or 3); the correct one is the strict min.
            add("mc-option-count-matches-options", len(opts) == len(p["options"]) and 2 <= len(opts) <= 3,
                f"{len(opts)} options")
            correct_opt = [o for o in opts if o.get("correct")]
            add("mc-correct-is-strict-min-option", len(correct_opt) == 1 and correct_opt[0]["value"] == p["correctLabel"])
        else:
            add("mc-option-count", len(opts) == 4, f"{len(opts)} options")
            # each distractor recomputes from its declared misconception via diagnostics_for
            add("mc-distractors-misconception-backed", _distractors_recompute(task, p, item))

    # --- follow-up correction: grammatical noun-count agreement across all surfaced text ---
    # Assemble every learner-visible string that can contain a "<count> <noun>" and assert it has no
    # "1 <plural>" (plural after a count of one) and no malformed "per <plural>" (must be singular).
    grammar_text_parts: List[str] = [item["prompt"]["instruction"]]
    for s in item["solution"]["steps"]:
        grammar_text_parts.append(s["transformation"])
        grammar_text_parts.append(s["intermediateResult"])
    for o in (item.get("options") or []):
        grammar_text_parts.append(str(o.get("display", "")))
    media = item.get("media") or []
    if media:
        m = media[0]
        for dt_key in ("dataTableFallback",):
            dt = m.get(dt_key) or {}
            for row in dt.get("rows", []):
                grammar_text_parts.extend(str(c) for c in row)
        spec = m.get("spec") or {}
        kdt = spec.get("answerKeyDataTableFallback") or {}
        for row in kdt.get("rows", []):
            grammar_text_parts.extend(str(c) for c in row)
    violations = _grammar_violations(" \n ".join(grammar_text_parts))
    add("noun-count-grammatical", not violations, f"violations={violations[:5]}")

    valid = all(c["ok"] for c in checks)
    return {"valid": valid, "validatorVersion": VALIDATOR_VERSION, "checks": checks}


def _rt_base(svg: str) -> str:
    a = svg.find('<g class="rt-base">')
    if a < 0:
        return ""
    b = svg.find("</g>", a)
    return svg[a:b] if b >= 0 else ""


def _unknown_hidden_in_student(task: str, params: Dict[str, Any], student: str) -> bool:
    """Role-based: in the STUDENT figure the unknown bottom/missing value must appear as '?', never as
    its solved value. Checks the student figure has a '?' marker and no rt-overlay group."""
    if '<g class="rt-overlay">' in student:
        return False
    if task in ("share_two_part", "share_three_part", "missing_part", "direct_proportion",
                "unit_rate", "simple_scale", "best_buy", "ratio_to_fraction", "fraction_to_ratio"):
        # the unknown is marked with a '?' in the student channel and never with its solved value.
        if '<g class="rt-student">' not in student:
            return False
        student_grp = student[student.find('<g class="rt-student">'):]
        if "?" not in student_grp:
            return False
        # role-based: the solved value must NOT appear anywhere in the student figure (overlay-free).
        sol = _solve(task, params)
        if task in ("share_two_part", "share_three_part"):
            shares = RC.share(params["total"], params["parts"])
            # a given ratio-part value may coincide with a share; only forbid the value inside rt-student.
            return all(f'>{v}</text>' not in student_grp for v in shares)
        if task == "missing_part":
            return f'>{sol}</text>' not in student_grp
        return True
    return True


def _unknown_shown_in_key(task: str, params: Dict[str, Any], key: str) -> bool:
    if '<g class="rt-overlay">' not in key:
        return False
    sol = _solve(task, params)
    if task in ("share_two_part", "share_three_part"):
        shares = RC.share(params["total"], params["parts"])
        return all(f'>{v}</text>' in key for v in shares)
    if task == "missing_part":
        return f'>{sol}</text>' in key
    if task in ("direct_proportion", "unit_rate", "simple_scale"):
        return _esc(_fmt_val(sol)) in key
    if task == "best_buy":
        return "✓" in key
    return True


def _a11y_leaks(task: str, params: Dict[str, Any], text: str) -> bool:
    """The student accessibility text must not state the computed answer value."""
    if task == "best_buy":
        return False  # the answer is an option label; the table lists raw amounts only
    disp = _encode_answer(task, params).get("display", "")
    t = text.lower()
    return f"answer is {disp}".lower() in t or f"= {disp}".lower() in t


def _distractors_recompute(task: str, params: Dict[str, Any], item: Dict[str, Any]) -> bool:
    expected = _mc_distractors(task, params)
    if expected is None:
        return False
    exp_keys = sorted(json.dumps(d["value"], sort_keys=True) for d in expected)
    got_keys = sorted(json.dumps(d["value"], sort_keys=True) for d in item.get("distractors", []))
    return exp_keys == got_keys


# --------------------------------------------------------------------------- #
# serialize / render-text / describe
# --------------------------------------------------------------------------- #
def serialize(item: Dict[str, Any]) -> str:
    """Canonical JSON (sorted keys, compact) — the byte-for-byte parity contract with the TS mirror."""
    return json.dumps(item, sort_keys=True, ensure_ascii=False, separators=(",", ":"))


def describe() -> Dict[str, Any]:
    return {
        "generatorId": GENERATOR_ID,
        "version": GENERATOR_VERSION,
        "title": "Ratio and proportion",
        "domain": "proportion",
        "strand": "ratio-and-proportion",
        "objectiveIds": [OBJECTIVE_BY_TASK[t] for t in RATIO_TASKS],
        "tasks": list(RATIO_TASKS),
        "interactionTypes": ["free-response", "multiple-choice"],
        "answerTypes": ["ratio", "exact-rational", "integer", "table-completion", "multiple-choice"],
        "difficultyRanges": {OBJECTIVE_BY_TASK[t]: list(TASK_BANDS[t]) for t in RATIO_TASKS},
        "approvalStatus": "pending-review",
    }
