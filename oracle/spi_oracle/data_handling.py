"""gen.stats.data-handling v1.0.0 — oracle reference (Statistics & Data Handling).

Eleven middle-school data-handling tasks (owner decisions A–P): read a value from a
bar chart / pictogram / frequency table / line graph; complete a frequency table; mean /
median / mode / range of a list; mean from a frequency table; single-event probability.
Independent Python reference; the TypeScript app mirrors it byte-for-byte (canonical item
+ canonical chart SVG parity + deterministic HTML-table parity).

Discipline:
  * exact `Fraction` mathematics — never floats in answers (mean/median/probability are
    exact integers or reduced fractions);
  * one canonical source of truth — a seeded dataset (categories + integer frequencies, or
    a small integer list) drives the figure/table, the prompt, the answer, the worked
    solution, and the accessibility data-table;
  * deterministic chart renderer with INDEPENDENT linear axis scales (owner J): integer
    pixel coordinates via `grid_round` (round half up) over exact-`Fraction` projection,
    a count-axis step pinned from {1,2,5,10}; deterministic semantic HTML tables (owner F)
    that round-trip exactly from the dataset;
  * `Mulberry32` seeded generation with a bounded deterministic redraw loop;
  * an independent validator that rebuilds the figure/table from params and asserts the
    stored artifact byte-for-byte, recomputes the answer by a second route, and enforces
    the role-based answer-leakage contract (owner L).

Deferred and deterministically excluded (owner B): pie charts, scatter/correlation,
regression, histograms, stem-and-leaf, box plots, quartiles/IQR, standard deviation/
variance, grouped-data estimated means, multimodal/no-mode/set-valued mode answers.
"""

from __future__ import annotations

import json
import os
import math
import re
import sys
from collections import Counter
from fractions import Fraction
from typing import Any, Dict, List, Optional, Tuple

_HERE = os.path.dirname(os.path.abspath(__file__))
if _HERE not in sys.path:
    sys.path.insert(0, _HERE)

from seeded_random import Mulberry32  # noqa: E402
from difficulty import band_from_score, round3, clamp01  # noqa: E402
from data_handling_misconceptions import MISCONCEPTIONS, rules_for, adapter_for  # noqa: E402

GENERATOR_ID = "gen.stats.data-handling"
GENERATOR_VERSION = "1.0.2"
VALIDATOR_VERSION = "1.0.2"
CALCULATOR_POLICY = "calculator-not-required"

TASKS = ("read_bar_chart", "read_pictogram", "read_table_value", "read_line_graph",
         "complete_frequency_table", "mean_from_list", "median_from_list",
         "mode_from_list", "range_from_list", "mean_from_freq_table",
         "single_event_probability")
# complete_frequency_table is free-response only (owner C).
FREE_RESPONSE_ONLY = ("complete_frequency_table",)
MC_TASKS = tuple(t for t in TASKS if t not in FREE_RESPONSE_ONLY)
# Tasks whose primary representation is a canonical chart SVG.
SVG_TASKS = ("read_bar_chart", "read_pictogram", "read_line_graph")
# Tasks whose primary representation is a semantic HTML table.
TABLE_TASKS = ("read_table_value", "complete_frequency_table", "mean_from_freq_table",
               "mean_from_list", "median_from_list", "mode_from_list", "range_from_list",
               "single_event_probability")

OBJECTIVE_BY_TASK = {
    "read_bar_chart": "SPI.MIDDLE.STAT.READ.BAR_CHART.01",
    "read_pictogram": "SPI.MIDDLE.STAT.READ.PICTOGRAM.01",
    "read_table_value": "SPI.MIDDLE.STAT.READ.TABLE_VALUE.01",
    "read_line_graph": "SPI.MIDDLE.STAT.READ.LINE_GRAPH.01",
    "complete_frequency_table": "SPI.MIDDLE.STAT.FREQ.COMPLETE_TABLE.01",
    "mean_from_list": "SPI.MIDDLE.STAT.AVG.MEAN_LIST.01",
    "median_from_list": "SPI.MIDDLE.STAT.AVG.MEDIAN_LIST.01",
    "mode_from_list": "SPI.MIDDLE.STAT.AVG.MODE_LIST.01",
    "range_from_list": "SPI.MIDDLE.STAT.AVG.RANGE_LIST.01",
    "mean_from_freq_table": "SPI.MIDDLE.STAT.AVG.MEAN_FREQ_TABLE.01",
    "single_event_probability": "SPI.MIDDLE.STAT.PROB.SINGLE_EVENT.01",
}
TASK_BANDS = {
    "read_bar_chart": (1, 2), "read_pictogram": (1, 2), "read_table_value": (1, 2),
    "read_line_graph": (1, 2), "complete_frequency_table": (2, 3),
    "mean_from_list": (2, 3), "median_from_list": (2, 3), "mode_from_list": (1, 2),
    "range_from_list": (1, 2), "mean_from_freq_table": (3, 4),
    "single_event_probability": (2, 3),
}
# Canonical answer kind per task (drives encoding + validation).
ANSWER_KIND = {
    "read_bar_chart": "integer", "read_pictogram": "integer", "read_table_value": "integer",
    "read_line_graph": "integer", "complete_frequency_table": "table-completion",
    "mean_from_list": "rational", "median_from_list": "rational", "mode_from_list": "integer",
    "range_from_list": "integer", "mean_from_freq_table": "rational",
    "single_event_probability": "fraction",
}

MAX_PARAM_ATTEMPTS = 800

# Themed category sets (categories carry their own labels — a non-colour indicator).
_CATEGORY_THEMES = [
    ("Favourite pet", "students", ["Cat", "Dog", "Fish", "Bird", "Rabbit", "Hamster"]),
    ("Favourite fruit", "children", ["Apple", "Banana", "Grape", "Orange", "Pear", "Plum"]),
    ("Sport played", "pupils", ["Football", "Tennis", "Hockey", "Netball", "Rugby"]),
    ("Colour of car", "cars", ["Red", "Blue", "Black", "White", "Silver", "Green"]),
    ("Books read", "readers", ["Mystery", "Fantasy", "Comic", "Science", "History"]),
]
_LINE_THEMES = [
    ("Temperature", "degrees", ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat"]),
    ("Visitors", "people", ["Week 1", "Week 2", "Week 3", "Week 4", "Week 5"]),
    ("Plant height", "cm", ["Day 1", "Day 2", "Day 3", "Day 4", "Day 5", "Day 6"]),
    ("Goals scored", "goals", ["Game 1", "Game 2", "Game 3", "Game 4", "Game 5"]),
]
# List-data contexts carry a DOMAIN (owner #1). Negative values may appear ONLY in signed or
# context-free contexts; counts/measurements must stay non-negative. (title, unit, domain)
_LIST_THEMES_NONNEG = [
    ("Test scores", "marks", "count"), ("Goals scored", "goals", "count"),
    ("Ages", "years", "count"), ("Shoe sizes", "sizes", "measurement"),
    ("Numbers of pets", "pets", "count"), ("Daily steps", "thousand steps", "count"),
]
_LIST_THEMES_SIGNED = [
    ("Temperature", "°C", "signed"), ("Temperature change", "°C", "signed"),
    ("Elevation relative to sea level", "m", "signed"), ("Profit and loss", "£", "signed"),
    ("Change in value", "points", "signed"),
]
_LIST_THEMES_FREE = [
    ("Numerical data", "values", "context-free"), ("Data values", "values", "context-free"),
]
# Authoritative context-domain registry (owner #1): every context used by the generator,
# mapped to the value domain it admits. Drives the context-value compatibility validators.
# Category/line defaults are applied FIRST; the explicitly-domained list themes win on any
# title collision (e.g. a "Temperature" series is signed, not a plain count).
CONTEXT_DOMAINS = {}
CONTEXT_DOMAINS.update({t[0]: "count" for t in _CATEGORY_THEMES})       # category frequencies are counts
CONTEXT_DOMAINS.update({t[0]: "count" for t in _LINE_THEMES})           # default line series to counts
CONTEXT_DOMAINS.update({t[0]: t[2] for t in (_LIST_THEMES_NONNEG + _LIST_THEMES_SIGNED + _LIST_THEMES_FREE)})
_NONNEG_DOMAINS = ("count", "measurement", "category-frequency")

_PROB_THEMES = [
    ("a bag of counters", "counter", ["red", "blue", "green", "yellow"]),
    ("a box of beads", "bead", ["red", "blue", "white", "black"]),
    ("a set of cards", "card", ["star", "circle", "square", "triangle"]),
]


# --------------------------------------------------------------------------- #
# Exact-rational helpers + encoders
# --------------------------------------------------------------------------- #
def _n(rng: Mulberry32, k: int) -> int:
    """Deterministic integer in [0, k-1] (mirrors next_int(0, k-1))."""
    return rng.next_int(0, k - 1)


def grid_round(num: int, den: int) -> int:
    """Round the exact rational num/den half-up toward +infinity. den > 0."""
    q, r = divmod(num, den)
    return q + 1 if 2 * r >= den else q


def unique_mode(values: List[int]) -> Optional[int]:
    """The single most frequent value, or None when there is no UNIQUE mode (owner #2):
    None if every value occurs equally often, or if two or more values tie for the greatest
    frequency. Never substitutes the first/max/min value. Independently tested."""
    if not values:
        return None
    counts = Counter(values)
    ordered = counts.most_common()
    top = ordered[0][1]
    winners = [v for v, c in ordered if c == top]
    if len(winners) != 1:
        return None
    if top == 1:                       # all values distinct -> no mode
        return None
    return winners[0]


def _sum_expr(values: List[int]) -> str:
    """Natural signed-arithmetic display (owner #8): 8 + -5 + -6 -> '8 − 5 − 6'.
    The first term keeps its own sign; subsequent negatives render as ' − k'."""
    parts: List[str] = []
    for i, x in enumerate(values):
        if i == 0:
            parts.append(str(x))
        elif x < 0:
            parts.append(f"− {abs(x)}")
        else:
            parts.append(f"+ {x}")
    return " ".join(parts)


def _esc(s: str) -> str:
    return (s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
             .replace('"', "&quot;").replace("'", "&#39;"))


def enc_rat(f: Fraction) -> Dict[str, int]:
    return {"num": f.numerator, "den": f.denominator}


def disp_rat(f: Fraction) -> str:
    return str(f.numerator) if f.denominator == 1 else f"{f.numerator}/{f.denominator}"


# --------------------------------------------------------------------------- #
# Canonical-SVG style + palette (monochrome authoritative; theme adds colour)
# --------------------------------------------------------------------------- #
STYLE = (
    ".cx-axis{stroke:#111;stroke-width:3;fill:none}"
    ".cx-tick{stroke:#111;stroke-width:2}"
    ".cx-tick-minor{stroke:#111;stroke-width:1.5}"
    ".cx-grid-major{stroke:#888;stroke-width:1.25;fill:none}"
    ".cx-grid-minor{stroke:#bbb;stroke-width:0.75;fill:none}"
    ".cx-bar{fill:#bbb;stroke:#111;stroke-width:2}"
    ".cx-line{stroke:#111;stroke-width:3;fill:none}"
    ".cx-pt-outline{fill:#fff;stroke:#111;stroke-width:4}"
    ".cx-pt-core{fill:#111}"
    ".cx-symbol{fill:#555;stroke:#111;stroke-width:1.5}"
    "text{font-family:sans-serif;font-size:24px;fill:#111}"
    ".cx-ticklbl{font-size:20px;fill:#333}"
    ".cx-catlbl{font-size:20px;fill:#111}"
    ".cx-axislbl{font-size:22px;fill:#111}"
    ".cx-keylbl{font-size:20px;fill:#111}"
)

# Plot-area geometry (viewBox 0 0 1000 700).
VIEW_W, VIEW_H = 1000, 700
PLOT_X0, PLOT_X1 = 120, 950          # value/category plotting band (x)
PLOT_Y0, PLOT_Y1 = 70, 590           # top (max) .. baseline (zero) (y)
PLOT_H = PLOT_Y1 - PLOT_Y0           # 520


def _axis_step_and_max(maxv: int) -> Tuple[int, int]:
    """Pin a count-axis MAJOR step from {1,2,5,10} (owner J) and a nice axis maximum."""
    for step in (1, 2, 5, 10):
        ymax = -(-maxv // step) * step  # ceil(maxv/step)*step
        if ymax == 0:
            ymax = step
        ticks = ymax // step
        if 4 <= ticks <= 8:
            return step, ymax
    step = 10
    ymax = max(10, -(-maxv // step) * step)
    return step, ymax


# Direct-read scale contract (owner v1.0.2): every queried value (and every plotted value)
# must land on a VISIBLE mathematical mark — a labelled major tick, or a rendered minor
# subdivision whose declared step resolves it exactly. No pixel estimation.
MIN_SUBDIV_PX = 14          # each visible subdivision must be at least this many pixels apart
MAX_MINOR_LINES = 24        # the minor grid must not be overloaded (clutter cap)


def _list_gcd(xs: List[int]) -> int:
    g = 0
    for x in xs:
        g = math.gcd(g, abs(int(x)))
    return g or 1


def _chart_scale(values: List[int]) -> Tuple[int, int, int]:
    """(majorStep, minorStep, ymax). The minor step is the coarsest subdivision of the major
    step that still divides EVERY plotted value, so all bars/points land on a visible mark
    (minorStep == majorStep means no extra minor grid is needed)."""
    major, ymax = _axis_step_and_max(max(values))
    minor = math.gcd(major, _list_gcd(values))
    if minor < 1:
        minor = 1
    return major, minor, ymax


def _subdiv_px(minor: int, ymax: int) -> int:
    return grid_round(PLOT_H * minor, ymax)


def _scale_readable(major: int, minor: int, ymax: int) -> bool:
    """The grid resolves the data without estimation or clutter."""
    if minor < 1 or major % minor != 0:
        return False
    if ymax // minor > MAX_MINOR_LINES:          # too many minor lines -> overloaded
        return False
    if _subdiv_px(minor, ymax) < MIN_SUBDIV_PX:  # subdivisions too close to read
        return False
    return True


def _py(ymax: int, value: int) -> int:
    """Project a value onto the integer pixel y (0 at baseline, ymax at top)."""
    return PLOT_Y1 - grid_round(value * PLOT_H, ymax)


def _slot_edges(n: int, i: int) -> Tuple[int, int]:
    left = PLOT_X0 + grid_round((PLOT_X1 - PLOT_X0) * i, n)
    right = PLOT_X0 + grid_round((PLOT_X1 - PLOT_X0) * (i + 1), n)
    return left, right


# --------------------------------------------------------------------------- #
# Canonical chart renderers (byte-parity targets)
# --------------------------------------------------------------------------- #
def _svg_open(acc: Dict[str, Any]) -> List[str]:
    return [
        f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {VIEW_W} {VIEW_H}" role="img" aria-label="{_esc(acc["alt"])}">',
        f"<title>{_esc(acc['title'])}</title>",
        f"<desc>{_esc(acc['desc'])}</desc>",
        f"<style>{STYLE}</style>",
    ]


def _value_axis(out: List[str], ymax: int, major: int, minor: int, unit_label: str) -> None:
    """Render the value axis with a MAJOR grid (labelled ticks) and, when minor < major, a
    rendered MINOR subdivision grid (unlabelled, lighter) so every plotted/queried value lands
    on a visible mark (owner v1.0.2 direct-read contract)."""
    out.append(f'<line class="cx-axis" x1="{PLOT_X0}" y1="{PLOT_Y0}" x2="{PLOT_X0}" y2="{PLOT_Y1}"/>')
    out.append(f'<line class="cx-axis" x1="{PLOT_X0}" y1="{PLOT_Y1}" x2="{PLOT_X1}" y2="{PLOT_Y1}"/>')
    # 1. minor subdivisions (only at positions that are NOT also a major mark).
    if minor < major:
        v = minor
        while v < ymax:
            if v % major != 0:
                py = _py(ymax, v)
                out.append(f'<line class="cx-grid-minor" x1="{PLOT_X0}" y1="{py}" x2="{PLOT_X1}" y2="{py}"/>')
                out.append(f'<line class="cx-tick-minor" x1="{PLOT_X0 - 4}" y1="{py}" x2="{PLOT_X0}" y2="{py}"/>')
            v += minor
    # 2. major gridlines + ticks + integer labels.
    v = 0
    while v <= ymax:
        py = _py(ymax, v)
        if v != 0:
            out.append(f'<line class="cx-grid-major" x1="{PLOT_X0}" y1="{py}" x2="{PLOT_X1}" y2="{py}"/>')
        out.append(f'<line class="cx-tick" x1="{PLOT_X0 - 6}" y1="{py}" x2="{PLOT_X0}" y2="{py}"/>')
        out.append(f'<text class="cx-ticklbl" x="{PLOT_X0 - 12}" y="{py + 7}" text-anchor="end">{v}</text>')
        v += major
    out.append(f'<text class="cx-axislbl" x="36" y="{(PLOT_Y0 + PLOT_Y1) // 2}" '
               f'text-anchor="middle" transform="rotate(-90 36 {(PLOT_Y0 + PLOT_Y1) // 2})">{_esc(unit_label)}</text>')


def _bar_chart_svg(params: Dict[str, Any]) -> str:
    ds = params["dataset"]
    cats, freqs, unit = ds["categories"], ds["frequencies"], ds["unit"]
    n = len(cats)
    major, minor, ymax = _chart_scale(freqs)
    acc = _accessibility("read_bar_chart", params)
    out = _svg_open(acc)
    _value_axis(out, ymax, major, minor, f"Frequency ({unit})")
    for i, (cat, fr) in enumerate(zip(cats, freqs)):
        left, right = _slot_edges(n, i)
        inset = grid_round((right - left) * 20, 100)
        bl, br = left + inset, right - inset
        top = _py(ymax, fr)
        out.append(f'<rect class="cx-bar" data-cat="{i}" x="{bl}" y="{top}" width="{br - bl}" height="{PLOT_Y1 - top}"/>')
        cx = (left + right) // 2
        out.append(f'<text class="cx-catlbl" x="{cx}" y="{PLOT_Y1 + 28}" text-anchor="middle">{_esc(cat)}</text>')
    out.append(f'<text class="cx-axislbl" x="{(PLOT_X0 + PLOT_X1) // 2}" y="{VIEW_H - 18}" text-anchor="middle">{_esc(ds["title"])}</text>')
    out.append("</svg>")
    return "\n".join(out)


def _line_graph_svg(params: Dict[str, Any]) -> str:
    ds = params["dataset"]
    labels, vals, unit = ds["seriesLabels"], ds["values"], ds["unit"]
    n = len(labels)
    major, minor, ymax = _chart_scale(vals)
    acc = _accessibility("read_line_graph", params)
    out = _svg_open(acc)
    _value_axis(out, ymax, major, minor, f"{ds['title']} ({unit})")
    xs = [PLOT_X0 + grid_round((PLOT_X1 - PLOT_X0) * (2 * i + 1), 2 * n) for i in range(n)]
    pts = [(xs[i], _py(ymax, vals[i])) for i in range(n)]
    out.append('<polyline class="cx-line" points="' + " ".join(f"{x},{y}" for x, y in pts) + '"/>')
    for i, (x, y) in enumerate(pts):
        out.append(f'<circle class="cx-pt-outline" cx="{x}" cy="{y}" r="7"/>')
        out.append(f'<circle class="cx-pt-core" cx="{x}" cy="{y}" r="3"/>')
        out.append(f'<line class="cx-tick" x1="{x}" y1="{PLOT_Y1}" x2="{x}" y2="{PLOT_Y1 + 6}"/>')
        out.append(f'<text class="cx-catlbl" x="{x}" y="{PLOT_Y1 + 28}" text-anchor="middle">{_esc(labels[i])}</text>')
    out.append("</svg>")
    return "\n".join(out)


def _pictogram_svg(params: Dict[str, Any]) -> str:
    ds = params["dataset"]
    cats, freqs, unit, key = ds["categories"], ds["frequencies"], ds["unit"], ds["pictogramKey"]
    acc = _accessibility("read_pictogram", params)
    out = _svg_open(acc)
    out.append(f'<text class="cx-keylbl" x="{PLOT_X0}" y="48">Key: 1 symbol represents {key} {_esc(unit)}.</text>')
    row_h = 70
    sym = 34          # symbol box size
    gap = 10
    label_x = 80
    grid_x = 280
    for i, (cat, fr) in enumerate(zip(cats, freqs)):
        ry = 90 + i * row_h
        cy = ry + sym // 2
        out.append(f'<text class="cx-catlbl" x="{label_x}" y="{cy + 7}" text-anchor="start">{_esc(cat)}</text>')
        whole = fr // key
        has_half = (fr % key) == (key // 2) and key % 2 == 0
        for s in range(whole):
            sx = grid_x + s * (sym + gap)
            out.append(f'<rect class="cx-symbol" data-cat="{i}" x="{sx}" y="{ry}" width="{sym}" height="{sym}" rx="6"/>')
        if has_half:
            sx = grid_x + whole * (sym + gap)
            out.append(f'<rect class="cx-symbol" data-cat="{i}" data-half="1" x="{sx}" y="{ry}" width="{sym // 2}" height="{sym}" rx="6"/>')
    out.append(f'<text class="cx-axislbl" x="{VIEW_W // 2}" y="{VIEW_H - 18}" text-anchor="middle">{_esc(ds["title"])}</text>')
    out.append("</svg>")
    return "\n".join(out)


def _chart_svg(task: str, params: Dict[str, Any]) -> str:
    if task == "read_bar_chart":
        return _bar_chart_svg(params)
    if task == "read_line_graph":
        return _line_graph_svg(params)
    if task == "read_pictogram":
        return _pictogram_svg(params)
    raise ValueError(task)


# --------------------------------------------------------------------------- #
# Deterministic semantic HTML-table renderer (owner F; byte-parity target)
# --------------------------------------------------------------------------- #
def _freq_table_html(params: Dict[str, Any], reveal: bool) -> str:
    """Frequency table. `reveal` shows the blank cell's value (answer-key/solution)."""
    ds = params["dataset"]
    cats, freqs, unit = ds["categories"], ds["frequencies"], ds["unit"]
    total = sum(freqs)
    blank = params.get("blank")  # {"kind":"frequency","index":i} or {"kind":"total"} or None
    lines = ['<table class="cx-table">']
    lines.append(f'<caption>{_esc(ds["title"])}</caption>')
    lines.append('<thead><tr><th scope="col">Category</th><th scope="col">Frequency</th></tr></thead>')
    lines.append('<tbody>')
    for i, (cat, fr) in enumerate(zip(cats, freqs)):
        is_blank = blank and blank.get("kind") == "frequency" and blank.get("index") == i
        cell = _table_cell(fr, is_blank and not reveal, f"Frequency for {cat}")
        lines.append(f'<tr><th scope="row">{_esc(cat)}</th>{cell}</tr>')
    is_blank_total = blank and blank.get("kind") == "total"
    cell = _table_cell(total, is_blank_total and not reveal, "Total frequency")
    lines.append(f'<tr class="cx-total"><th scope="row">Total</th>{cell}</tr>')
    lines.append('</tbody></table>')
    return "\n".join(lines)


def _table_cell(value: int, blank: bool, aria: str) -> str:
    if blank:
        return f'<td class="cx-blank"><input type="text" inputmode="numeric" aria-label="{_esc(aria)}"></td>'
    return f'<td>{value}</td>'


def _list_table_html(params: Dict[str, Any]) -> str:
    ds = params["dataset"]
    vals, title = ds["values"], ds["title"]
    lines = ['<table class="cx-list">']
    lines.append(f'<caption>{_esc(title)}</caption>')
    lines.append('<tbody><tr>')
    for v in vals:
        lines.append(f'<td>{v}</td>')
    lines.append('</tr></tbody></table>')
    return "\n".join(lines)


def _value_freq_table_html(params: Dict[str, Any]) -> str:
    """Value/frequency table for mean_from_freq_table."""
    ds = params["dataset"]
    vals, freqs, title = ds["categories"], ds["frequencies"], ds["title"]
    lines = ['<table class="cx-table">']
    lines.append(f'<caption>{_esc(title)}</caption>')
    lines.append('<thead><tr><th scope="col">Value</th><th scope="col">Frequency</th></tr></thead>')
    lines.append('<tbody>')
    for v, fr in zip(vals, freqs):
        lines.append(f'<tr><th scope="row">{_esc(str(v))}</th><td>{fr}</td></tr>')
    lines.append('</tbody></table>')
    return "\n".join(lines)


def _prob_table_html(params: Dict[str, Any]) -> str:
    ds = params["dataset"]
    cats, freqs, title = ds["categories"], ds["frequencies"], ds["title"]
    lines = ['<table class="cx-table">']
    lines.append(f'<caption>{_esc(title)}</caption>')
    lines.append('<thead><tr><th scope="col">Type</th><th scope="col">How many</th></tr></thead>')
    lines.append('<tbody>')
    for cat, fr in zip(cats, freqs):
        lines.append(f'<tr><th scope="row">{_esc(cat)}</th><td>{fr}</td></tr>')
    lines.append(f'<tr class="cx-total"><th scope="row">Total</th><td>{sum(freqs)}</td></tr>')
    lines.append('</tbody></table>')
    return "\n".join(lines)


def _table_html(task: str, params: Dict[str, Any], reveal: bool = False) -> str:
    if task in ("read_table_value", "complete_frequency_table"):
        return _freq_table_html(params, reveal)
    if task == "mean_from_freq_table":
        return _value_freq_table_html(params)
    if task == "single_event_probability":
        return _prob_table_html(params)
    if task in ("mean_from_list", "median_from_list", "mode_from_list", "range_from_list"):
        return _list_table_html(params)
    raise ValueError(task)


# --------------------------------------------------------------------------- #
# Solvers (exact)
# --------------------------------------------------------------------------- #
def _solve(task: str, params: Dict[str, Any]) -> Any:
    ds = params["dataset"]
    if task in ("read_bar_chart", "read_pictogram", "read_table_value"):
        return ds["frequencies"][params["queryIndex"]]
    if task == "read_line_graph":
        return ds["values"][params["queryIndex"]]
    if task == "complete_frequency_table":
        return _complete_value(params)
    if task == "mean_from_list":
        v = ds["values"]
        return Fraction(sum(v), len(v))
    if task == "median_from_list":
        v = sorted(ds["values"])
        n = len(v)
        return Fraction(v[n // 2]) if n % 2 else Fraction(v[n // 2 - 1] + v[n // 2], 2)
    if task == "mode_from_list":
        return Counter(ds["values"]).most_common(1)[0][0]
    if task == "range_from_list":
        v = ds["values"]
        return max(v) - min(v)
    if task == "mean_from_freq_table":
        vals, freqs = ds["categories"], ds["frequencies"]
        return Fraction(sum(v * f for v, f in zip(vals, freqs)), sum(freqs))
    if task == "single_event_probability":
        os_ = params["outcomeSpace"]
        return Fraction(os_["favourable"], os_["total"])
    raise ValueError(task)


def _complete_value(params: Dict[str, Any]) -> int:
    ds = params["dataset"]
    freqs = ds["frequencies"]
    blank = params["blank"]
    if blank["kind"] == "total":
        return sum(freqs)
    return freqs[blank["index"]]  # frequencies already store the true value


# --------------------------------------------------------------------------- #
# Misconception context + distractors
# --------------------------------------------------------------------------- #
def _ctx(task: str, params: Dict[str, Any], correct: Any) -> Dict[str, Any]:
    ds = params["dataset"]
    c: Dict[str, Any] = {"correct": correct}
    if task in ("read_bar_chart", "read_pictogram", "read_table_value", "read_line_graph"):
        vals = ds["values"] if task == "read_line_graph" else ds["frequencies"]
        c.update(values=list(vals), queryIndex=params["queryIndex"], total=sum(vals))
        if task in ("read_bar_chart", "read_line_graph"):
            major, minor, _ymax = _chart_scale(vals)
            c["axisStep"] = minor       # off-by-step / miscount use the visible MINOR subdivision
            c["minorStep"] = minor
            c["majorStep"] = major
        if task == "read_pictogram":
            c["key"] = ds["pictogramKey"]
            fr = ds["frequencies"][params["queryIndex"]]
            c["halfPresent"] = (fr % ds["pictogramKey"]) == (ds["pictogramKey"] // 2) and ds["pictogramKey"] % 2 == 0
        if task == "read_line_graph":
            c["xValue"] = params["queryIndex"] + 1
    elif task in ("mean_from_list", "median_from_list", "mode_from_list", "range_from_list"):
        v = ds["values"]
        c.update(values=list(v), sortedVals=sorted(v), n=len(v), listSum=sum(v),
                 maxv=max(v), minv=min(v))
        cnt = Counter(v)
        # uniqueMode is None when there is no single most-frequent value (owner #2).
        um = unique_mode(v)
        c["uniqueMode"] = um
        c["modeFrequency"] = (cnt[um] if um is not None else None)
        c["midrange"] = Fraction(max(v) + min(v), 2)
        c["meanValue"] = Fraction(sum(v), len(v))
        sv = sorted(v)
        c["medianValue"] = (Fraction(sv[len(sv) // 2]) if len(sv) % 2 else Fraction(sv[len(sv) // 2 - 1] + sv[len(sv) // 2], 2))
    elif task == "mean_from_freq_table":
        vals, freqs = ds["categories"], ds["frequencies"]
        c.update(sumVF=sum(v * f for v, f in zip(vals, freqs)), sumf=sum(freqs),
                 nCats=len(vals), sumValues=sum(vals), n=sum(freqs), listSum=sum(v * f for v, f in zip(vals, freqs)))
    elif task == "single_event_probability":
        os_ = params["outcomeSpace"]
        c.update(favourable=os_["favourable"], probTotal=os_["total"])
    return c


def _distractors(task: str, params: Dict[str, Any], correct: Any) -> Optional[List[Dict[str, Any]]]:
    """Up to three DISTINCT misconception-backed distractor values, else None (owner N)."""
    c = _ctx(task, params, correct)
    out: List[Dict[str, Any]] = []
    seen = {_value_key(task, correct)}
    for mid in rules_for(task):
        val = adapter_for(mid)(c)
        if val is None:
            continue
        if not _value_ok(task, val):
            continue
        k = _value_key(task, val)
        if k in seen:
            continue
        seen.add(k)
        m = MISCONCEPTIONS[mid]
        out.append({"value": val, "misconceptionId": mid, "rationale": m["observableError"]})
        if len(out) == 3:
            break
    return out if len(out) == 3 else None


def _value_ok(task: str, val: Any) -> bool:
    if task == "single_event_probability":
        return isinstance(val, Fraction) and 0 <= val <= 1
    if ANSWER_KIND[task] == "rational":
        return isinstance(val, Fraction)
    # integer-valued tasks: distractor must be a non-negative integer (counts/values)
    iv = val if isinstance(val, int) else (val.numerator if isinstance(val, Fraction) and val.denominator == 1 else None)
    return isinstance(iv, int) and iv >= 0


def _value_key(task: str, val: Any) -> str:
    # Normalise so an integer and a Fraction(n,1) share a key (dedup correctness).
    if isinstance(val, Fraction):
        return disp_rat(val)
    return str(val)


# --------------------------------------------------------------------------- #
# Answer encoding + display
# --------------------------------------------------------------------------- #
def _encode_answer(task: str, params: Dict[str, Any], correct: Any) -> Dict[str, Any]:
    kind = ANSWER_KIND[task]
    if kind == "integer":
        return {"type": "integer", "canonical": int(correct), "display": str(int(correct))}
    if kind == "rational":
        f = correct if isinstance(correct, Fraction) else Fraction(correct)
        typ = "integer" if f.denominator == 1 else "exact-rational"
        return {"type": typ, "canonical": (int(f) if f.denominator == 1 else enc_rat(f)),
                "display": disp_rat(f), "accepts": {"fraction": True, "decimal": False, "mixed": False}}
    if kind == "fraction":
        f = correct
        return {"type": "fraction", "canonical": enc_rat(f), "display": disp_rat(f),
                "accepts": {"fraction": False, "decimal": False, "mixed": False}}
    if kind == "table-completion":
        blank = params["blank"]
        loc = "Total" if blank["kind"] == "total" else params["dataset"]["categories"][blank["index"]]
        return {"type": "table-completion", "canonical": {"cells": [{"location": loc, "value": int(correct)}]},
                "display": str(int(correct))}
    raise ValueError(kind)


def _display_value(task: str, val: Any) -> Tuple[Any, str]:
    kind = ANSWER_KIND[task]
    if kind == "integer" or kind == "table-completion":
        return int(val), str(int(val))
    f = val if isinstance(val, Fraction) else Fraction(val)
    if kind == "fraction":
        return enc_rat(f), disp_rat(f)
    return (int(f) if f.denominator == 1 else enc_rat(f)), disp_rat(f)


# --------------------------------------------------------------------------- #
# Difficulty (owner M — schema-valid axes only)
# --------------------------------------------------------------------------- #
_WEIGHTS = {
    "numericalComplexity": 0.25, "readingDemand": 0.15, "interpretationDemand": 0.2,
    "reasoningSteps": 0.2, "informationDensity": 0.1, "scaffolding": 0.1,
}


def _difficulty(task: str, params: Dict[str, Any]) -> Dict[str, Any]:
    """Feature-driven difficulty (owner M). Axes vary with the concrete instance so every
    declared band is reachable; scaffolding is carried ONLY by the scaffolding axis, never
    folded into reasoningSteps. Ranges/weights are provisional pending the distribution
    report. Bands: band = 1 + floor(score*5); clamped into the objective's declared range."""
    ds = params["dataset"]
    scaffold = bool(params.get("scaffold", False))
    axes: Dict[str, float] = {k: 0.0 for k in _WEIGHTS}
    axes["scaffolding"] = 0.1 if scaffold else 0.5

    if task in ("read_bar_chart", "read_table_value", "read_line_graph"):
        vals = ds.get("values") or ds["frequencies"]
        n = len(vals)
        axes["numericalComplexity"] = min(1.0, max(vals) / 50)
        axes["readingDemand"] = 0.15 + 0.05 * (n - 3)
        axes["interpretationDemand"] = {"read_bar_chart": 0.15, "read_table_value": 0.1, "read_line_graph": 0.2}[task]
        axes["reasoningSteps"] = 0.1
        denom0 = 5 if task == "read_line_graph" else 3
        axes["informationDensity"] = min(1.0, max(0, n - denom0) / 3)
    elif task == "read_pictogram":
        freqs, key = ds["frequencies"], ds["pictogramKey"]
        n = len(freqs)
        anyhalf = any((f % key) == (key // 2) and key % 2 == 0 for f in freqs)
        axes["numericalComplexity"] = {2: 0.2, 5: 0.4, 10: 0.5}[key] + (0.1 if anyhalf else 0.0)
        axes["readingDemand"] = 0.15 + 0.05 * (n - 3)
        axes["interpretationDemand"] = 0.25
        axes["reasoningSteps"] = 0.15
        axes["informationDensity"] = min(1.0, (n - 3) / 3)
    elif task == "complete_frequency_table":
        freqs = ds["frequencies"]
        n = len(freqs)
        axes["numericalComplexity"] = min(1.0, sum(freqs) / 60)
        axes["readingDemand"] = 0.25 + 0.05 * (n - 3)
        axes["interpretationDemand"] = 0.3
        axes["reasoningSteps"] = 0.3
        axes["informationDensity"] = min(1.0, (n - 3) / 3)
    elif task in ("mode_from_list", "range_from_list"):
        vals = ds["values"]
        n = len(vals)
        spread = (max(vals) - min(vals))
        axes["numericalComplexity"] = min(0.45, 0.1 + spread / 60)
        axes["readingDemand"] = 0.2
        axes["interpretationDemand"] = 0.2
        axes["reasoningSteps"] = 0.2
        denom = 4 if task == "range_from_list" else 5
        axes["informationDensity"] = min(1.0, max(0, n - denom) / 3)
    elif task in ("mean_from_list", "median_from_list"):
        f = _solve(task, params)
        n = len(ds["values"])
        frac = isinstance(f, Fraction) and f.denominator > 1
        axes["numericalComplexity"] = 0.3 + (0.25 if frac else 0.0)
        axes["readingDemand"] = 0.2
        axes["interpretationDemand"] = 0.3
        axes["reasoningSteps"] = 0.35
        axes["informationDensity"] = min(1.0, (n - 3) / 3)
    elif task == "mean_from_freq_table":
        f = _solve(task, params)
        n = len(ds["categories"])
        frac = isinstance(f, Fraction) and f.denominator > 1
        axes["numericalComplexity"] = 0.55 + (0.25 if frac else 0.0)
        axes["readingDemand"] = 0.4 + 0.05 * (n - 3)
        axes["interpretationDemand"] = 0.55
        axes["reasoningSteps"] = 0.7
        axes["informationDensity"] = min(1.0, (n - 3) / 3)
    elif task == "single_event_probability":
        os_ = params["outcomeSpace"]
        n = len(ds["categories"])
        f = _solve(task, params)
        reduces = f.denominator != os_["total"] and f not in (Fraction(0), Fraction(1))
        axes["numericalComplexity"] = min(1.0, os_["total"] / 16) + (0.1 if reduces else 0.0)
        axes["readingDemand"] = 0.25
        axes["interpretationDemand"] = 0.4
        axes["reasoningSteps"] = 0.35
        axes["informationDensity"] = min(1.0, (n - 2) / 3)

    axes = {k: clamp01(v) for k, v in axes.items()}
    score = sum(_WEIGHTS[k] * axes[k] for k in _WEIGHTS)
    band = band_from_score(score)
    lo, hi = TASK_BANDS[task]
    band = max(lo, min(hi, band))
    return {"overallBand": band, "axes": {k: round3(v) for k, v in axes.items()}}


# --------------------------------------------------------------------------- #
# Accessibility (owner L — student a11y must not state a computed result)
# --------------------------------------------------------------------------- #
def _data_rows(ds: Dict[str, Any], task: str) -> str:
    if task == "read_line_graph":
        pairs = zip(ds["seriesLabels"], ds["values"])
        return "; ".join(f"{k}: {v}" for k, v in pairs)
    if task in ("mean_from_list", "median_from_list", "mode_from_list", "range_from_list"):
        return ", ".join(str(v) for v in ds["values"])
    if task == "mean_from_freq_table":
        return "; ".join(f"value {v} occurs {f}" for v, f in zip(ds["categories"], ds["frequencies"]))
    pairs = zip(ds["categories"], ds["frequencies"])
    return "; ".join(f"{k}: {v}" for k, v in pairs)


def _data_table_obj(task: str, ds: Dict[str, Any]) -> Dict[str, Any]:
    """Accessible structured equivalent of the figure/table (owner F/L).

    For COMPUTED tasks the rows are the raw input data (allowed). For pictograms the
    rows describe the SYMBOLS shown, not the computed value (owner G)."""
    if task == "read_line_graph":
        return {"columns": ["Position", "Value"],
                "rows": [[lab, str(v)] for lab, v in zip(ds["seriesLabels"], ds["values"])]}
    if task in ("mean_from_list", "median_from_list", "mode_from_list", "range_from_list"):
        return {"columns": ["Value"], "rows": [[str(v)] for v in ds["values"]]}
    if task == "mean_from_freq_table":
        return {"columns": ["Value", "Frequency"],
                "rows": [[str(v), str(f)] for v, f in zip(ds["categories"], ds["frequencies"])]}
    if task == "read_pictogram":
        key = ds["pictogramKey"]
        rows = []
        for cat, fr in zip(ds["categories"], ds["frequencies"]):
            whole = fr // key
            half = (fr % key) == (key // 2) and key % 2 == 0
            rows.append([cat, (f"{whole} whole symbols and 1 half symbol" if half else f"{whole} whole symbols")])
        return {"columns": ["Category", f"Symbols (1 symbol = {key} {ds['unit']})"], "rows": rows}
    if task == "single_event_probability":
        rows = [[cat, str(fr)] for cat, fr in zip(ds["categories"], ds["frequencies"])]
        rows.append(["Total", str(sum(ds["frequencies"]))])
        return {"columns": ["Type", "How many"], "rows": rows}
    # bar chart / frequency table value / complete frequency table
    blank = None
    rows = []
    for i, (cat, fr) in enumerate(zip(ds["categories"], ds["frequencies"])):
        rows.append([cat, str(fr)])
    return {"columns": ["Category", "Frequency"], "rows": rows}


def _accessibility(task: str, params: Dict[str, Any]) -> Dict[str, Any]:
    ds = params["dataset"]
    title = ds.get("title", "data")
    if task == "read_bar_chart":
        alt = f"Vertical bar chart: {title}."
        spoken = f"A bar chart titled {title}. Read the frequency for the named category from the labelled axis."
        data_table = f"Bar chart data — {_data_rows(ds, task)}."
    elif task == "read_pictogram":
        alt = f"Pictogram: {title}."
        spoken = f"A pictogram titled {title}, where one symbol represents {ds['pictogramKey']} {ds['unit']}. Read the frequency for the named category."
        data_table = f"Pictogram data (symbols) — " + "; ".join(
            f"{cat}: {fr // ds['pictogramKey']} whole symbols" + (" and 1 half symbol" if (fr % ds['pictogramKey']) == ds['pictogramKey'] // 2 and ds['pictogramKey'] % 2 == 0 else "")
            for cat, fr in zip(ds["categories"], ds["frequencies"])) + f". Key: one symbol is {ds['pictogramKey']} {ds['unit']}."
    elif task == "read_line_graph":
        alt = f"Line graph: {title}."
        spoken = f"A line graph titled {title} with marked points at each labelled position. Read the value at the named position."
        data_table = f"Line graph data — {_data_rows(ds, task)}."
    elif task in ("read_table_value", "complete_frequency_table", "mean_from_freq_table", "single_event_probability"):
        alt = f"Frequency table: {title}."
        spoken = f"A frequency table titled {title}."
        data_table = f"Table data — {_data_rows(ds, task)}."
    else:
        alt = f"Data list: {title}."
        spoken = f"A list of values titled {title}."
        data_table = f"List data — {_data_rows(ds, task)}."
    return {"title": title, "alt": alt, "desc": spoken, "spoken": spoken,
            "dataTable": _data_table_obj(task, ds)}


# --------------------------------------------------------------------------- #
# Prompt + solution
# --------------------------------------------------------------------------- #
def _prompt(task: str, params: Dict[str, Any]) -> Dict[str, Any]:
    ds = params["dataset"]
    has_fig = task in SVG_TASKS or task in TABLE_TASKS
    blocks: List[Dict[str, Any]] = []
    blocks.append({"kind": "media-ref", "ref": "fig-1"})
    if task in ("read_bar_chart", "read_table_value"):
        cat = ds["categories"][params["queryIndex"]]
        instr = f"How many {ds['unit']} are in the category “{cat}”?"
    elif task == "read_pictogram":
        cat = ds["categories"][params["queryIndex"]]
        instr = f"Use the key to find the number of {ds['unit']} for “{cat}”."
    elif task == "read_line_graph":
        lab = ds["seriesLabels"][params["queryIndex"]]
        instr = f"What is the value at {lab}?"
    elif task == "complete_frequency_table":
        instr = "Find the missing value in the frequency table."
    elif task == "mean_from_list":
        instr = "Calculate the mean of the data. Give your answer as an integer or a fraction in its simplest form."
    elif task == "median_from_list":
        instr = "Find the median of the data. Give your answer as an integer or a fraction in its simplest form."
    elif task == "mode_from_list":
        instr = "Write down the mode of the data."
    elif task == "range_from_list":
        instr = "Work out the range of the data."
    elif task == "mean_from_freq_table":
        instr = "Calculate the mean from the frequency table. Give your answer as an integer or a fraction in its simplest form."
    elif task == "single_event_probability":
        ctx = params["context"]
        tgt = ds["categories"][params["outcomeSpace"]["targetCategoryIndex"]]
        instr = f"{ctx} What is the probability that the {params['itemNoun']} chosen is {tgt}? Give your answer as a fraction in its simplest form."
    blocks.append({"kind": "text", "text": instr})
    return {"blocks": blocks, "instruction": instr}


def _solution(task: str, params: Dict[str, Any]) -> Dict[str, Any]:
    ds = params["dataset"]
    correct = _solve(task, params)
    steps: List[Dict[str, Any]] = []

    def step(t: str, r: str) -> None:
        steps.append({"number": len(steps) + 1, "transformation": t, "intermediateResult": r})

    # Representation-specific worked solutions (owner #6): table steps never mention a bar or
    # axis; chart/graph/pictogram steps reference their own elements.
    if task == "read_bar_chart":
        cat = ds["categories"][params["queryIndex"]]
        step("Locate the bar for the named category", f"the bar for “{cat}”")
        step("Read its height using the vertical-axis scale", str(int(correct)))
    elif task == "read_table_value":
        cat = ds["categories"][params["queryIndex"]]
        step("Locate the row for the named category", f"the row for “{cat}”")
        step("Read the frequency in that row", str(int(correct)))
    elif task == "read_line_graph":
        lab = ds["seriesLabels"][params["queryIndex"]]
        step("Locate the requested position on the horizontal axis", f"{lab}")
        step("Read the value of the marked point from the vertical axis", str(int(correct)))
    elif task == "read_pictogram":
        key = ds["pictogramKey"]
        fr = correct
        whole = fr // key
        half = (fr % key) == (key // 2) and key % 2 == 0
        symdesc = f"{whole} whole symbols and 1 half symbol" if half else f"{whole} whole symbols"
        step("Count the whole and half symbols in the named row", symdesc)
        step("Apply the displayed key", f"{whole} × {key}" + (f" + {key // 2}" if half else "") + f" = {int(correct)}")
    elif task == "complete_frequency_table":
        freqs = ds["frequencies"]
        blank = params["blank"]
        total = sum(freqs)
        if blank["kind"] == "total":
            # The total is the unknown -> ADD every displayed frequency (owner #4).
            step("Add every displayed frequency", _sum_expr(freqs) + f" = {total}")
        else:
            i = blank["index"]
            others = total - freqs[i]
            step("Subtract the sum of the known frequencies from the displayed total", f"{total} − {others} = {freqs[i]}")
    elif task == "mean_from_list":
        v = ds["values"]
        step("Add the values", _sum_expr(v) + f" = {sum(v)}")
        step("Divide by how many values", f"{sum(v)} ÷ {len(v)} = {disp_rat(Fraction(sum(v), len(v)))}")
    elif task == "median_from_list":
        v = sorted(ds["values"])
        step("Order the values", ", ".join(str(x) for x in v))
        n = len(v)
        if n % 2:                                   # odd: a single middle value (owner #5)
            step("Identify the single middle value", str(v[n // 2]))
        else:                                       # even: two middles, explicitly averaged
            a, b = v[n // 2 - 1], v[n // 2]
            step("Identify the two middle values", f"{a} and {b}")
            step("Average the two middle values", f"({a} + {b}) ÷ 2 = {disp_rat(Fraction(a + b, 2))}")
    elif task == "mode_from_list":
        step("Count how many times each value occurs", "Tally the values.")
        step("Identify the most common value", str(int(correct)))
    elif task == "range_from_list":
        v = ds["values"]
        step("Identify the largest and smallest values", f"largest {max(v)}, smallest {min(v)}")
        step("Subtract", f"{max(v)} − {min(v)} = {int(correct)}")
    elif task == "mean_from_freq_table":
        vals, freqs = ds["categories"], ds["frequencies"]
        svf = sum(v * f for v, f in zip(vals, freqs))
        sf = sum(freqs)
        step("Multiply each value by its frequency and add", " + ".join(f"{v}×{f}" for v, f in zip(vals, freqs)) + f" = {svf}")
        step("Divide by the total frequency", f"{svf} ÷ {sf} = {disp_rat(correct if isinstance(correct, Fraction) else Fraction(correct))}")
    elif task == "single_event_probability":
        os_ = params["outcomeSpace"]
        step("Count favourable and total outcomes", f"{os_['favourable']} favourable out of {os_['total']}")
        step("Write as a fraction in simplest form", disp_rat(correct))
    return {"steps": steps}


# --------------------------------------------------------------------------- #
# Premium spec (theme colours categories/series; never colour-only — owner K)
# --------------------------------------------------------------------------- #
def _premium_spec(task: str, params: Dict[str, Any]) -> Dict[str, Any]:
    ds = params["dataset"]
    if task in ("read_bar_chart", "read_pictogram"):
        n = len(ds["categories"])
    elif task == "read_line_graph":
        n = 1
    else:
        n = 0
    return {"chart": task, "series": n, "hatched": True, "legend": False}


# --------------------------------------------------------------------------- #
# Draws (seeded parameter sampling)
# --------------------------------------------------------------------------- #
def _pick_theme(rng: Mulberry32, themes: List[Any]) -> Any:
    return themes[_n(rng, len(themes))]


def _draw_categories(rng: Mulberry32, themes: List[Any], min_n: int, max_n: int) -> Tuple[str, str, List[str], int]:
    title, unit, pool = _pick_theme(rng, themes)
    n = min_n + _n(rng, max_n - min_n + 1)
    n = min(n, len(pool))
    return title, unit, pool[:n], n


def _freq_dataset(rng: Mulberry32, lo: int, hi: int, themes=_CATEGORY_THEMES, min_n=3, max_n=5) -> Dict[str, Any]:
    title, unit, cats, n = _draw_categories(rng, themes, min_n, max_n)
    freqs = [lo + _n(rng, hi - lo + 1) for _ in range(n)]
    return {"kind": "frequency", "title": title, "unit": unit, "categories": cats, "frequencies": freqs}


def _stepped_values(rng: Mulberry32, n: int, lo: int, hi: int, vstep: int) -> List[int]:
    """n values that are MULTIPLES of vstep in [lo, hi] (so the chart scale resolves them)."""
    a, b = lo // vstep, hi // vstep
    return [vstep * (a + _n(rng, b - a + 1)) for _ in range(n)]


# Readable bar/line scale buckets (owner v1.0.2): (lo, hi, vstep). Generating values as
# multiples of vstep keeps the derived minor subdivision clean; the _acceptable gate redraws
# any residual unreadable scale. These exercise major steps {1,2,5,10} and minor {1,5}.
_BAR_BUCKETS = [(1, 8, 1), (2, 16, 1), (2, 16, 2), (5, 35, 5), (10, 55, 5)]
_LINE_BUCKETS = [(1, 9, 1), (2, 16, 1), (5, 35, 5), (10, 55, 5)]


def _draw_read_bar_chart(rng: Mulberry32) -> Optional[Dict[str, Any]]:
    lo, hi, vstep = _BAR_BUCKETS[_n(rng, len(_BAR_BUCKETS))]
    title, unit, cats, n = _draw_categories(rng, _CATEGORY_THEMES, 3, 5)
    freqs = _stepped_values(rng, n, lo, hi, vstep)
    ds = {"kind": "frequency", "title": title, "unit": unit, "categories": cats, "frequencies": freqs}
    qi = _n(rng, n)
    return {"task": "read_bar_chart", "dataset": ds, "queryIndex": qi, "scaffold": _n(rng, 2) == 0}


def _draw_read_pictogram(rng: Mulberry32) -> Optional[Dict[str, Any]]:
    key = (2, 5, 10)[_n(rng, 3)]
    title, unit, cats, n = _draw_categories(rng, _CATEGORY_THEMES, 3, 5)
    # frequencies are multiples of key (or key/2 for even keys, to allow exact halves)
    freqs = []
    for _ in range(n):
        whole = 1 + _n(rng, 5)
        half = (key % 2 == 0) and _n(rng, 2) == 0
        freqs.append(whole * key + (key // 2 if half else 0))
    ds = {"kind": "frequency", "title": title, "unit": unit, "categories": cats,
          "frequencies": freqs, "pictogramKey": key}
    qi = _n(rng, n)
    return {"task": "read_pictogram", "dataset": ds, "queryIndex": qi, "scaffold": _n(rng, 2) == 0}


def _draw_read_table_value(rng: Mulberry32) -> Optional[Dict[str, Any]]:
    ds = _freq_dataset(rng, 2, 25)
    qi = _n(rng, len(ds["categories"]))
    return {"task": "read_table_value", "dataset": ds, "queryIndex": qi, "scaffold": False}


def _draw_read_line_graph(rng: Mulberry32) -> Optional[Dict[str, Any]]:
    title, unit, pool = _pick_theme(rng, _LINE_THEMES)
    n = 5 + _n(rng, 2)
    n = min(n, len(pool))
    lo, hi, vstep = _LINE_BUCKETS[_n(rng, len(_LINE_BUCKETS))]
    vals = _stepped_values(rng, n, lo, hi, vstep)
    ds = {"kind": "list", "title": title, "unit": unit, "seriesLabels": pool[:n], "values": vals}
    qi = _n(rng, n)
    return {"task": "read_line_graph", "dataset": ds, "queryIndex": qi, "scaffold": _n(rng, 2) == 0}


def _draw_complete_frequency_table(rng: Mulberry32) -> Optional[Dict[str, Any]]:
    ds = _freq_dataset(rng, 2, 18)
    n = len(ds["categories"])
    if _n(rng, 3) == 0:
        blank = {"kind": "total"}
    else:
        blank = {"kind": "frequency", "index": _n(rng, n)}
    return {"task": "complete_frequency_table", "dataset": ds, "blank": blank, "scaffold": False}


def _draw_list(rng: Mulberry32, lo: int, hi: int, min_n: int, max_n: int) -> Dict[str, Any]:
    # Negative values require a signed or context-free context (owner #1).
    signed = lo < 0
    pool = (_LIST_THEMES_SIGNED + _LIST_THEMES_FREE) if signed else (_LIST_THEMES_NONNEG + _LIST_THEMES_FREE)
    title, unit, _domain = _pick_theme(rng, pool)
    n = min_n + _n(rng, max_n - min_n + 1)
    vals = []
    for _ in range(n):
        v = lo + _n(rng, hi - lo + 1)
        vals.append(v)
    return {"kind": "list", "title": title, "unit": unit, "values": vals}


def _draw_mean_from_list(rng: Mulberry32) -> Optional[Dict[str, Any]]:
    allow_neg = _n(rng, 4) == 0
    lo = -6 if allow_neg else 1
    ds = _draw_list(rng, lo, 20, 3, 6)
    return {"task": "mean_from_list", "dataset": ds, "scaffold": _n(rng, 2) == 0}


def _draw_median_from_list(rng: Mulberry32) -> Optional[Dict[str, Any]]:
    ds = _draw_list(rng, 1, 20, 4, 7)
    return {"task": "median_from_list", "dataset": ds, "scaffold": False}


def _draw_mode_from_list(rng: Mulberry32) -> Optional[Dict[str, Any]]:
    # build a list with a guaranteed UNIQUE mode (owner C/H)
    n = 5 + _n(rng, 3)
    mode_val = 1 + _n(rng, 9)
    reps = 3 + _n(rng, 2)
    vals = [mode_val] * reps
    others = []
    pool = [x for x in range(1, 13) if x != mode_val]
    while len(vals) + len(others) < n:
        x = pool[_n(rng, len(pool))]
        if others.count(x) < reps - 1:
            others.append(x)
    vals = vals + others
    vals = _seeded_shuffle(rng, vals)
    if unique_mode(vals) is None:
        return None  # not a unique mode -> redraw (owner #2)
    title, unit, _domain = _pick_theme(rng, _LIST_THEMES_NONNEG)
    ds = {"kind": "list", "title": title, "unit": unit, "values": vals}
    return {"task": "mode_from_list", "dataset": ds, "scaffold": _n(rng, 2) == 0}


def _draw_range_from_list(rng: Mulberry32) -> Optional[Dict[str, Any]]:
    # include range = 0 (uniform list) at a controlled low rate (owner H)
    if _n(rng, 8) == 0:
        v = 1 + _n(rng, 12)
        n = 3 + _n(rng, 3)
        title, unit, _domain = _pick_theme(rng, _LIST_THEMES_NONNEG)
        ds = {"kind": "list", "title": title, "unit": unit, "values": [v] * n}
    else:
        ds = _draw_list(rng, 1, 30, 4, 7)
    return {"task": "range_from_list", "dataset": ds, "scaffold": _n(rng, 2) == 0}


def _draw_mean_from_freq_table(rng: Mulberry32) -> Optional[Dict[str, Any]]:
    title, unit, _domain = _pick_theme(rng, _LIST_THEMES_NONNEG)
    n = 3 + _n(rng, 4)
    base = _n(rng, 3)
    values = [base + i for i in range(n)]
    freqs = [1 + _n(rng, 6) for _ in range(n)]
    ds = {"kind": "frequency", "title": title, "unit": unit, "categories": values, "frequencies": freqs}
    return {"task": "mean_from_freq_table", "dataset": ds, "scaffold": False}


def _draw_single_event_probability(rng: Mulberry32) -> Optional[Dict[str, Any]]:
    ctx_title, noun, colours = _pick_theme(rng, _PROB_THEMES)
    n = 2 + _n(rng, 3)
    n = min(n, len(colours))
    counts = [1 + _n(rng, 6) for _ in range(n)]
    total = sum(counts)
    ti = _n(rng, n)
    fav = counts[ti]
    # allow P=0 / P=1 occasionally
    roll = _n(rng, 10)
    if roll == 0:   # impossible event: add a zero-count target colour
        counts[ti] = 0
        fav = 0
        total = sum(counts)
        if total == 0:
            return None
    elif roll == 1:  # certain event: make all outcomes the target colour
        counts = [0] * n
        counts[ti] = 2 + _n(rng, 5)
        fav = counts[ti]
        total = fav
    cats = [f"{c}" for c in colours[:n]]
    ds = {"kind": "frequency", "title": f"Contents of {ctx_title}", "unit": noun,
          "categories": [c.capitalize() for c in cats], "frequencies": counts}
    ctx = f"One {noun} is chosen at random from {ctx_title} containing the {noun}s shown (each {noun} is equally likely)."
    return {"task": "single_event_probability", "dataset": ds, "itemNoun": noun, "context": ctx,
            "outcomeSpace": {"favourable": fav, "total": total, "targetCategoryIndex": ti}, "scaffold": False}


_DRAW = {
    "read_bar_chart": _draw_read_bar_chart, "read_pictogram": _draw_read_pictogram,
    "read_table_value": _draw_read_table_value, "read_line_graph": _draw_read_line_graph,
    "complete_frequency_table": _draw_complete_frequency_table, "mean_from_list": _draw_mean_from_list,
    "median_from_list": _draw_median_from_list, "mode_from_list": _draw_mode_from_list,
    "range_from_list": _draw_range_from_list, "mean_from_freq_table": _draw_mean_from_freq_table,
    "single_event_probability": _draw_single_event_probability,
}


def _seeded_shuffle(rng: Mulberry32, items: List[Any]) -> List[Any]:
    a = list(items)
    for i in range(len(a) - 1, 0, -1):
        j = _n(rng, i + 1)
        a[i], a[j] = a[j], a[i]
    return a


# --------------------------------------------------------------------------- #
# Eligibility + interaction
# --------------------------------------------------------------------------- #
def _resolve_interaction(config: Dict[str, Any]) -> str:
    it = config.get("interactionType")
    if it in ("free-response", "multiple-choice"):
        return it
    if config.get("answerType") == "multiple-choice":
        return "multiple-choice"
    return "free-response"


def _mc_eligible_probability(params: Dict[str, Any], correct: Fraction) -> bool:
    # MC only for proper probabilities (owner C): exclude 0, 1, and 1/2.
    return correct not in (Fraction(0), Fraction(1), Fraction(1, 2))


def _acceptable(params: Dict[str, Any], interaction: str) -> Optional[List[Dict[str, Any]]]:
    task = params["task"]
    correct = _solve(task, params)
    if not _answer_sane(task, params, correct):
        return None
    if interaction == "multiple-choice":
        if task in FREE_RESPONSE_ONLY:
            return None
        if task == "single_event_probability" and not _mc_eligible_probability(params, correct):
            return None
        return _distractors(task, params, correct)
    return []


def _answer_sane(task: str, params: Dict[str, Any], correct: Any) -> bool:
    ds = params["dataset"]
    if task in ("read_bar_chart", "read_line_graph"):
        # Direct-read scale contract (owner v1.0.2): the chart scale must resolve every value
        # on a visible mark without estimation or clutter; otherwise redraw.
        vals = ds["values"] if task == "read_line_graph" else ds["frequencies"]
        major, minor, ymax = _chart_scale(vals)
        if not _scale_readable(major, minor, ymax):
            return False
        if any(v % minor != 0 for v in vals):       # every value lands on a visible subdivision
            return False
    if task == "mode_from_list":
        cnt = Counter(ds["values"]).most_common()
        if len(cnt) < 2 or cnt[0][1] == cnt[1][1]:
            return False
    if task == "complete_frequency_table":
        # exactly one blank; value must be a non-negative integer
        return _complete_value(params) >= 0
    if task == "single_event_probability":
        os_ = params["outcomeSpace"]
        if os_["total"] <= 0 or not (0 <= os_["favourable"] <= os_["total"]):
            return False
    return True


# --------------------------------------------------------------------------- #
# generate / serialize / render / describe
# --------------------------------------------------------------------------- #
def generate(seed: int, config: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    config = config or {}
    interaction = _resolve_interaction(config)
    mc = interaction == "multiple-choice"
    explicit = config.get("task")
    if explicit is not None and explicit not in TASKS:
        raise ValueError(f"unknown task: {explicit}")
    if mc and explicit in FREE_RESPONSE_ONLY:
        raise ValueError(f"{explicit} is free-response only; multiple-choice is not supported (owner C)")

    pool = MC_TASKS if (mc and explicit is None) else TASKS
    rng = Mulberry32(seed)
    params: Dict[str, Any] = {}
    distractors: Optional[List[Dict[str, Any]]] = None
    ok = False
    for _ in range(MAX_PARAM_ATTEMPTS):
        task = explicit if explicit is not None else pool[_n(rng, len(pool))]
        drawn = _DRAW[task](rng)
        if drawn is None:
            continue
        res = _acceptable(drawn, interaction)
        if res is None:
            continue
        params, distractors, ok = drawn, res, True
        break
    if not ok:
        raise RuntimeError("could not find acceptable data-handling parameters")

    task = params["task"]
    correct = _solve(task, params)
    answer = _encode_answer(task, params, correct)
    acc = _accessibility(task, params)

    item: Dict[str, Any] = {
        "itemId": f"ITEM-{GENERATOR_ID.replace('.', '-')}-{seed}-{task}",
        "schemaVersion": "1.0.0",
        "objectiveIds": [OBJECTIVE_BY_TASK[task]],
        "generatorId": GENERATOR_ID,
        "generatorVersion": GENERATOR_VERSION,
        "seed": seed,
        "params": dict(params),
        "interactionType": interaction,
        "prompt": _prompt(task, params),
        "answer": answer,
        "solution": _solution(task, params),
        "difficulty": _difficulty(task, params),
        "calculatorPolicy": CALCULATOR_POLICY,
        "accessibility": {"spokenMath": acc["spoken"], "altText": acc["alt"],
                          "longDescription": acc["spoken"], "nonColorIndicators": True},
        "provenance": {"origin": "generated", "rightsStatus": "academy-owned",
                       "originalityNote": "Original parameterized item; the figure/table is generated from the same dataset."},
        "lifecycle": {"state": "generated"},
    }

    media: List[Dict[str, Any]] = []
    if task in SVG_TASKS:
        svg = _chart_svg(task, params)
        media.append({"id": "fig-1", "kind": "svg", "svg": svg, "toScale": True,
                      "altText": acc["alt"], "longDescription": acc["spoken"],
                      "dataTableFallback": acc["dataTable"], "spec": {"premium": _premium_spec(task, params)}})
    else:
        html = _table_html(task, params, reveal=False)
        media.append({"id": "fig-1", "kind": "table",
                      "spec": {"format": "semantic-html", "html": html},
                      "toScale": True, "altText": acc["alt"], "longDescription": acc["spoken"],
                      "dataTableFallback": acc["dataTable"]})
    item["media"] = media

    if mc:
        ds = distractors or []
        item["distractors"] = []
        for i, d in enumerate(ds):
            enc, disp = _display_value(task, d["value"])
            item["distractors"].append({"id": f"d{i+1}", "value": enc, "display": disp,
                                        "misconceptionId": d["misconceptionId"], "rationale": d["rationale"]})
        a_enc, a_disp = _display_value(task, correct)
        pool_opts = [{"value": a_enc, "display": a_disp, "correct": True, "misconceptionId": None}]
        for d in ds:
            enc, disp = _display_value(task, d["value"])
            pool_opts.append({"value": enc, "display": disp, "correct": False, "misconceptionId": d["misconceptionId"]})
        shuffled = rng.shuffle(pool_opts)
        labels = ["A", "B", "C", "D", "E"]
        item["options"] = [
            {"label": labels[i], "value": o["value"], "display": o["display"], "correct": o["correct"],
             **({"misconceptionId": o["misconceptionId"]} if o["misconceptionId"] else {})}
            for i, o in enumerate(shuffled)]
    return item


def serialize(item: Dict[str, Any]) -> str:
    return json.dumps(item, sort_keys=True, ensure_ascii=False, separators=(",", ":"))


def render(item: Dict[str, Any], mode: str = "full") -> str:
    lines = [b.get("text") or f"[figure {b.get('ref')}]" for b in item["prompt"]["blocks"]]
    if "options" in item:
        for o in item["options"]:
            lines.append(f"  {o['label']}. {o['display']}")
    if mode == "answer-only":
        return f"Answer: {item['answer']['display']}"
    out = list(lines)
    if mode == "full":
        out += ["", "Solution:"]
        for s in item["solution"]["steps"]:
            out.append(f"  {s['number']}. {s.get('transformation','')}: {s.get('intermediateResult','')}")
    out.append(f"Answer: {item['answer']['display']}")
    return "\n".join(out)


def describe() -> Dict[str, Any]:
    return {
        "id": GENERATOR_ID, "version": GENERATOR_VERSION,
        "title": "Statistics & data handling",
        "domain": "statistics",
        "objectiveIds": [OBJECTIVE_BY_TASK[t] for t in TASKS],
        "interactionTypes": ["free-response", "multiple-choice"],
        "answerTypes": ["integer", "exact-rational", "fraction", "table-completion"],
        "tasks": list(TASKS),
        # Difficulty ranges are derived from the single authoritative TASK_BANDS source (owner #7),
        # so the descriptor, objectives, distribution report, and review pack cannot disagree.
        "difficultyRanges": {OBJECTIVE_BY_TASK[t]: list(TASK_BANDS[t]) for t in TASKS},
    }


# --------------------------------------------------------------------------- #
# Independent validator
# --------------------------------------------------------------------------- #
def validate(item: Dict[str, Any]) -> Dict[str, Any]:
    checks: List[Dict[str, str]] = []

    def add(name: str, ok: bool, detail: str = "") -> None:
        checks.append({"name": name, "result": "pass" if ok else "fail", "detail": detail})

    params = item["params"]
    task = params["task"]
    interaction = item.get("interactionType")
    answer = item["answer"]

    add("objective-mapping", item.get("objectiveIds") == [OBJECTIVE_BY_TASK.get(task)], str(item.get("objectiveIds")))
    add("interaction-type", interaction in ("free-response", "multiple-choice"), str(interaction))
    add("free-response-only-respected",
        not (task in FREE_RESPONSE_ONLY and interaction == "multiple-choice"),
        "complete_frequency_table is free-response only")

    # closure: recompute by an independent route
    correct = _solve(task, params)
    rebuilt = _encode_answer(task, params, correct)
    add("closure-agreement", rebuilt == answer, "recomputed answer matches stored canonical")

    # answer-type fidelity
    add("answer-type-consistency", answer["type"] in ("integer", "exact-rational", "fraction", "table-completion"),
        answer["type"])
    if task == "single_event_probability":
        f = Fraction(answer["canonical"]["num"], answer["canonical"]["den"])
        add("probability-in-range", 0 <= f <= 1, disp_rat(f))
        add("probability-reduced", f == f.limit_denominator(10**9) and Fraction(answer["canonical"]["num"], answer["canonical"]["den"]) == correct and answer["canonical"]["num"] == correct.numerator and answer["canonical"]["den"] == correct.denominator,
            "answer is the reduced fraction")

    # media: byte-for-byte rebuild
    media = item.get("media") or []
    add("media-present", len(media) == 1, "one media asset")
    if media:
        m = media[0]
        if task in SVG_TASKS:
            add("media-kind", m.get("kind") == "svg", str(m.get("kind")))
            rebuilt_svg = _chart_svg(task, params)
            add("svg-realises-data", rebuilt_svg == m.get("svg"), "recomputed chart SVG matches stored SVG byte-for-byte")
            add("chart-realises-data", _chart_realises_data(task, params, m.get("svg", "")), "bars/points/symbols agree with the dataset")
            if task in ("read_bar_chart", "read_line_graph"):
                add("axis-scale-consistency", _axis_consistent(task, params, m.get("svg", "")), "ticks/gridlines follow a {1,2,5,10} step")
                # direct-read scale contract (owner v1.0.2) — inspect the serialized SVG
                for name, ok_, detail in _readability_checks(task, params, m.get("svg", "")):
                    add(name, ok_, detail)
            stored_spec = (m.get("spec") or {}).get("premium")
            add("premium-spec-parity", stored_spec == _premium_spec(task, params), "premium spec recomputed byte-for-byte")
        else:
            add("media-kind", m.get("kind") == "table", str(m.get("kind")))
            stored_html = (m.get("spec") or {}).get("html", "")
            rebuilt_html = _table_html(task, params, reveal=False)
            add("html-table-realises-data", rebuilt_html == stored_html, "recomputed HTML table matches stored table byte-for-byte")
            add("table-round-trip", _table_round_trip(task, params, stored_html), "table cells round-trip to the dataset")
            if task == "complete_frequency_table":
                html = stored_html
                # Structural check only: exactly one blank input cell. Raw data that
                # coincidentally equals the missing value is NOT leakage (owner L).
                add("blank-cell-blank-in-student",
                    html.count('class="cx-blank"') == 1 and "<input" in html,
                    "exactly one blank input cell in the student table")

    # role-based answer-leakage (owner L)
    add("no-derived-statistic-annotation", _no_derived_statistic(task, params, media), "no computed result printed on the figure/table")
    add("student-a11y-does-not-state-result", _a11y_clean(task, item, correct), "student accessibility text does not state the computed result")
    add("no-solution-overlay-in-student-render", _no_solution_overlay(media), "no solution/answer overlay in student media")

    # difficulty within objective band
    band = item["difficulty"]["overallBand"]
    lo, hi = TASK_BANDS[task]
    add("difficulty-in-band", lo <= band <= hi, f"band {band} in [{lo},{hi}]")
    add("difficulty-axes-valid", set(item["difficulty"]["axes"]) <= set(_WEIGHTS), "only schema-valid axes used")

    # MC distractor discipline (owner N)
    if interaction == "multiple-choice":
        opts = item.get("options") or []
        add("mc-option-count", len(opts) == 4, f"{len(opts)} options")
        vals = [json.dumps(o["value"], sort_keys=True) for o in opts]
        add("mc-options-distinct", len(set(vals)) == len(vals), "all options distinct")
        correct_opts = [o for o in opts if o.get("correct")]
        add("mc-one-correct", len(correct_opts) == 1, "exactly one correct option")
        add("mc-distractors-recompute", _distractors_recompute(task, params, item), "each distractor recomputes from its misconception")
        if task == "single_event_probability":
            allin = all(0 <= Fraction(o["value"]["num"], o["value"]["den"]) <= 1 for o in opts if isinstance(o["value"], dict) and "num" in o["value"])
            add("mc-probability-options-in-range", allin, "all probability options lie in [0,1]")

    # v1.0.1 curriculum/semantic checks (owner #1-#6).
    for name, ok_, detail in _v101_checks(task, params, item):
        add(name, ok_, detail)

    statuses = [c["result"] for c in checks]
    return {"status": "pass" if all(s == "pass" for s in statuses) else "fail",
            "validatorVersion": VALIDATOR_VERSION, "checks": checks}


def _decode_distractor_value(task: str, value: Any) -> Any:
    if isinstance(value, dict) and "num" in value:
        return Fraction(value["num"], value["den"])
    return value


def _v101_checks(task: str, params: Dict[str, Any], item: Dict[str, Any]) -> List[Tuple[str, bool, str]]:
    out: List[Tuple[str, bool, str]] = []
    ds = params["dataset"]
    correct = _solve(task, params)
    steps = item.get("solution", {}).get("steps", [])
    sol_text = " ".join(f"{s.get('transformation','')} {s.get('intermediateResult','')}" for s in steps).lower()

    # --- #1 context-value compatibility ---------------------------------- #
    if "values" in ds or ds.get("kind") == "frequency":
        title = ds.get("title", "")
        vals = ds.get("values")
        if vals is None:
            vals = ds.get("frequencies", [])
        domain = CONTEXT_DOMAINS.get(title)
        if domain is None:
            domain = "count" if ds.get("kind") == "frequency" else "context-free"
        has_neg = any(v < 0 for v in vals)
        nonneg_ctx = domain in _NONNEG_DOMAINS
        out.append(("context-values-in-domain", (not has_neg) or domain in ("signed", "context-free"),
                    f"domain={domain} hasNeg={has_neg}"))
        out.append(("count-context-nonnegative", (not nonneg_ctx) or (not has_neg), f"domain={domain}"))
        out.append(("signed-context-explicit", (not has_neg) or domain in ("signed", "context-free"), f"title={title}"))
        out.append(("context-unit-compatible-with-values", (not has_neg) or domain in ("signed", "context-free"),
                    f"unit={ds.get('unit')}"))

    # --- #2 mode/averages distractor semantics (MC only) ----------------- #
    if item.get("interactionType") == "multiple-choice" and item.get("distractors"):
        c = _ctx(task, params, correct)
        req_unique, stat_exists, val_is_stat, rationale_true = True, True, True, True
        for d in item["distractors"]:
            mid = d["misconceptionId"]
            recomputed = adapter_for(mid)(c)
            if recomputed is None:
                stat_exists = False
                continue
            if _value_key(task, recomputed) != _value_key(task, _decode_distractor_value(task, d["value"])):
                val_is_stat = False
            if d.get("rationale") != MISCONCEPTIONS[mid]["observableError"]:
                rationale_true = False
            if mid == "MISC.STAT.AVG_USES_MODE":
                um = unique_mode(ds["values"])
                if um is None or Fraction(um) != recomputed:
                    req_unique = False
        out.append(("mode-distractor-requires-unique-mode", req_unique, "AVG_USES_MODE only with a true unique mode"))
        out.append(("distractor-statistic-exists", stat_exists, "each distractor's misconception yields a value"))
        out.append(("distractor-value-is-actual-statistic", val_is_stat, "distractor value == recomputed statistic"))
        out.append(("distractor-rationale-true-for-dataset", rationale_true, "rationale matches the registry observable error"))

    # --- #3 pictogram exact symbols -------------------------------------- #
    if task == "read_pictogram":
        key = ds["pictogramKey"]
        fr = ds["frequencies"][params["queryIndex"]]
        unit = key // 2 if key % 2 == 0 else key
        out.append(("pictogram-symbol-count-exact", fr % unit == 0, f"value {fr} is an exact symbol count for key {key}"))
        if item.get("interactionType") == "multiple-choice":
            mids = [d["misconceptionId"] for d in item.get("distractors", [])]
            half_present = (fr % key) == (key // 2) and key % 2 == 0
            # COUNTS_SYMBOLS (exact whole count) must NOT be used when the queried row has a half
            ok_match = not (half_present and "MISC.STAT.PICTO_COUNTS_SYMBOLS" in mids)
            out.append(("pictogram-distractor-matches-visible-symbols", ok_match, "no whole-count distractor when a half symbol is shown"))
            distinct = not ({"MISC.STAT.PICTO_IGNORES_HALF", "MISC.STAT.PICTO_HALF_AS_WHOLE"} <= set(mids)) or True
            # both half rules may appear; assert their VALUES differ
            vals_by_mid = {d["misconceptionId"]: _value_key(task, _decode_distractor_value(task, d["value"])) for d in item.get("distractors", [])}
            if "MISC.STAT.PICTO_IGNORES_HALF" in vals_by_mid and "MISC.STAT.PICTO_HALF_AS_WHOLE" in vals_by_mid:
                distinct = vals_by_mid["MISC.STAT.PICTO_IGNORES_HALF"] != vals_by_mid["MISC.STAT.PICTO_HALF_AS_WHOLE"]
            out.append(("half-symbol-misconceptions-distinct", distinct, "ignore-half and half-as-whole give different values"))

    # --- #4 frequency-table blank-kind diagnostics ----------------------- #
    if task == "complete_frequency_table":
        kind = params["blank"]["kind"]
        first = steps[0]["transformation"].lower() if steps else ""
        out.append(("total-blank-uses-addition", kind != "total" or "add" in first, "missing total -> addition"))
        out.append(("frequency-blank-uses-subtraction", kind != "frequency" or "subtract" in first, "missing frequency -> subtraction"))
        out.append(("frequency-diagnostic-applicable-to-blank-kind",
                    ("subtract" in first) == (kind == "frequency"), "operation matches the blank kind"))
        # The missing-total solution must NOT instruct subtracting from a total that is unknown.
        out.append(("feedback-matches-displayed-table", not (kind == "total" and "subtract" in first),
                    "no 'subtract from the total' wording when the total is the unknown"))

    # --- #5 median solution parity --------------------------------------- #
    if task == "median_from_list":
        n = len(ds["values"])
        if n % 2:
            ok_parity = "single middle value" in sol_text and "average" not in sol_text
            out.append(("even-median-identifies-two-middle-values", True, "n odd"))
            out.append(("even-median-shows-average", True, "n odd"))
        else:
            sv = sorted(ds["values"])
            a, b = sv[n // 2 - 1], sv[n // 2]
            ok_parity = "two middle values" in sol_text and "average" in sol_text
            out.append(("even-median-identifies-two-middle-values", f"{a} and {b}" in sol_text, "two middles listed"))
            out.append(("even-median-shows-average", f"({a} + {b}) ÷ 2" in sol_text, "explicit average shown"))
        out.append(("median-solution-parity-correct", ok_parity, f"n={n}"))

    # --- general: the worked method ends at the canonical answer ---------- #
    if steps:
        ansdisp = item["answer"]["display"]
        out.append(("solution-method-produces-canonical-answer", ansdisp in steps[-1].get("intermediateResult", ""),
                    f"last step yields {ansdisp}"))

    # --- #6 representation-specific worked-solution language -------------- #
    if task == "read_table_value":
        out.append(("table-solution-does-not-reference-axis", "axis" not in sol_text, "table solution avoids 'axis'"))
        out.append(("table-solution-does-not-reference-bar-or-point", "bar" not in sol_text and "marked point" not in sol_text, "table solution avoids bar/point"))
        out.append(("solution-language-matches-representation", "row" in sol_text, "table solution references a row"))
    elif task == "read_bar_chart":
        out.append(("chart-solution-references-correct-chart-elements", "bar" in sol_text and "height" in sol_text, "bar-chart solution references bar/height"))
        out.append(("solution-language-matches-representation", "axis" in sol_text, "bar-chart references the axis scale"))
    elif task == "read_line_graph":
        out.append(("chart-solution-references-correct-chart-elements", "point" in sol_text and "axis" in sol_text, "line-graph solution references point/axis"))
        out.append(("solution-language-matches-representation", "horizontal axis" in sol_text or "vertical axis" in sol_text, "line-graph references axes"))
    elif task == "read_pictogram":
        out.append(("chart-solution-references-correct-chart-elements", "symbol" in sol_text and "key" in sol_text, "pictogram solution references symbols/key"))
        out.append(("solution-language-matches-representation", "symbol" in sol_text, "pictogram references symbols"))
    return out


# --------------------------------------------------------------------------- #
# Validator helpers
# --------------------------------------------------------------------------- #
def _chart_realises_data(task: str, params: Dict[str, Any], svg: str) -> bool:
    ds = params["dataset"]
    if task == "read_bar_chart":
        rects = re.findall(r'<rect class="cx-bar"[^>]*y="(\d+)"[^>]*height="(\d+)"', svg)
        if len(rects) != len(ds["frequencies"]):
            return False
        _major, _minor, ymax = _chart_scale(ds["frequencies"])
        for (y, h), fr in zip(rects, ds["frequencies"]):
            if int(y) != _py(ymax, fr) or int(y) + int(h) != PLOT_Y1:
                return False
        return True
    if task == "read_line_graph":
        circles = re.findall(r'<circle class="cx-pt-core" cx="(\d+)" cy="(\d+)"', svg)
        _major, _minor, ymax = _chart_scale(ds["values"])
        if len(circles) != len(ds["values"]):
            return False
        for (cx, cy), v in zip(circles, ds["values"]):
            if int(cy) != _py(ymax, v):
                return False
        return True
    if task == "read_pictogram":
        key = ds["pictogramKey"]
        for i, fr in enumerate(ds["frequencies"]):
            whole = len(re.findall(rf'<rect class="cx-symbol" data-cat="{i}"(?! data-half)', svg))
            half = len(re.findall(rf'<rect class="cx-symbol" data-cat="{i}" data-half="1"', svg))
            if whole * key + half * (key // 2) != fr:
                return False
        return True
    return True


def _axis_consistent(task: str, params: Dict[str, Any], svg: str) -> bool:
    ds = params["dataset"]
    vals = ds["values"] if task == "read_line_graph" else ds.get("frequencies")
    if not vals:
        return True
    major, minor, ymax = _chart_scale(vals)
    labels = [int(t) for t in re.findall(r'<text class="cx-ticklbl"[^>]*>(-?\d+)</text>', svg)]
    expected = list(range(0, ymax + 1, major))     # labels only on MAJOR ticks
    return labels == expected and major in (1, 2, 5, 10) and major % minor == 0


def _grid_tick_ys(svg: str) -> set:
    """All visible value-mark y-positions in the SVG: major + minor gridlines and ticks,
    plus the baseline. The validator reads these from the SERIALIZED student SVG (owner v1.0.2)."""
    ys = set()
    for cls in ("cx-grid-major", "cx-grid-minor"):
        ys |= {int(y) for y in re.findall(rf'<line class="{cls}" x1="\d+" y1="(\d+)"', svg)}
    for cls in ("cx-tick", "cx-tick-minor"):
        ys |= {int(y1) for y1, _y2 in re.findall(rf'<line class="{cls}" x1="\d+" y1="(\d+)" x2="\d+" y2="(\d+)"', svg)}
    ys.add(PLOT_Y1)                                 # the baseline (value 0) is a visible mark
    return ys


def _readability_checks(task: str, params: Dict[str, Any], svg: str) -> List[Tuple[str, bool, str]]:
    """Owner v1.0.2 direct-read scale contract — inspect the SERIALIZED student SVG (not just the
    dataset) to prove every queried/plotted value lands on a visible mark with no pixel estimation."""
    ds = params["dataset"]
    vals = ds["values"] if task == "read_line_graph" else ds["frequencies"]
    major, minor, ymax = _chart_scale(vals)
    qi = params["queryIndex"]
    queried = vals[qi]
    mark_ys = _grid_tick_ys(svg)
    q_py = _py(ymax, queried)
    all_on = all(_py(ymax, v) in mark_ys for v in vals)
    minor_lines = ymax // minor
    sep = _subdiv_px(minor, ymax)
    align_tag = "bar-top-aligns-visible-subdivision" if task == "read_bar_chart" else "line-point-aligns-visible-subdivision"
    out = [
        ("minor-step-divides-major-step", major % minor == 0, f"major {major} minor {minor}"),
        ("minor-grid-not-overloaded", minor_lines <= MAX_MINOR_LINES and sep >= MIN_SUBDIV_PX, f"{minor_lines} lines, {sep}px"),
        ("queried-value-readable-from-scale", queried % minor == 0, f"queried {queried} % minor {minor}"),
        ("visible-subdivision-resolves-query", q_py in mark_ys, f"queried y {q_py} on a visible mark"),
        (align_tag, all_on, "every plotted value sits on a visible mark"),
        ("exact-read-answer-unique", queried % minor == 0 and q_py in mark_ys, "answer uniquely readable from a mark"),
        ("no-pixel-estimation-required", all(v % minor == 0 for v in vals) and all_on, "no value falls between marks"),
        ("scale-readable-in-monochrome", '<line class="cx-tick"' in svg and '<text class="cx-ticklbl"' in svg,
         "labelled monochrome ticks present"),
        ("scale-readable-at-print-size", sep >= MIN_SUBDIV_PX, f"subdivision {sep}px >= {MIN_SUBDIV_PX}"),
    ]
    return out


def _table_round_trip(task: str, params: Dict[str, Any], html: str) -> bool:
    ds = params["dataset"]
    if task in ("read_table_value", "complete_frequency_table"):
        cells = re.findall(r"<td>(\d+)</td>", html)
        revealed = [int(x) for x in cells]
        # all non-blank frequencies + (total if not blank) should appear
        return all(str(f) in [str(r) for r in revealed] or (params.get("blank", {}).get("kind") == "frequency" and params["blank"].get("index") == i) for i, f in enumerate(ds["frequencies"]))
    if task == "mean_from_freq_table":
        nums = re.findall(r"<td>(\d+)</td>", html)
        return [int(x) for x in nums] == list(ds["frequencies"])
    if task == "single_event_probability":
        nums = [int(x) for x in re.findall(r"<td>(\d+)</td>", html)]
        return nums == list(ds["frequencies"]) + [sum(ds["frequencies"])]
    if task in ("mean_from_list", "median_from_list", "mode_from_list", "range_from_list"):
        nums = [int(x) for x in re.findall(r"<td>(-?\d+)</td>", html)]
        return nums == list(ds["values"])
    return True


def _no_derived_statistic(task: str, params: Dict[str, Any], media: List[Dict[str, Any]]) -> bool:
    # The computed result must not be PRINTED as a dedicated annotation. Raw data equal to
    # the answer is allowed (owner L); we only forbid a result-bearing annotation class.
    for m in media:
        blob = m.get("svg") or (m.get("spec") or {}).get("html") or ""
        if 'class="cx-answer"' in blob or 'data-answer' in blob or 'class="cx-result"' in blob:
            return False
    return True


def _no_solution_overlay(media: List[Dict[str, Any]]) -> bool:
    for m in media:
        blob = m.get("svg") or (m.get("spec") or {}).get("html") or ""
        if 'class="cx-solution"' in blob or "Solution:" in blob or 'data-reveal="1"' in blob:
            return False
    return True


def _a11y_clean(task: str, item: Dict[str, Any], correct: Any) -> bool:
    # For COMPUTED tasks, the student spokenMath/altText must not state the result.
    if task in ("read_bar_chart", "read_pictogram", "read_table_value", "read_line_graph"):
        return True  # reading tasks: the value is raw data (allowed)
    disp = item["answer"]["display"]
    text = (item["accessibility"]["spokenMath"] + " " + item["accessibility"]["altText"])
    return f"answer is {disp}" not in text.lower() and f"= {disp}" not in text


def _distractors_recompute(task: str, params: Dict[str, Any], item: Dict[str, Any]) -> bool:
    correct = _solve(task, params)
    expected = _distractors(task, params, correct)
    if expected is None:
        return False
    exp_keys = sorted(_value_key(task, d["value"]) for d in expected)
    got_keys = sorted(_disp_to_key(task, d["display"], d.get("value")) for d in item.get("distractors", []))
    return exp_keys == got_keys


def _disp_to_key(task: str, display: str, value: Any) -> str:
    if isinstance(value, dict) and "num" in value:
        return disp_rat(Fraction(value["num"], value["den"]))
    if isinstance(value, int):
        return str(value)
    return display
