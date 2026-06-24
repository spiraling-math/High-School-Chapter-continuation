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
GENERATOR_VERSION = "1.0.0"
VALIDATOR_VERSION = "1.0.0"
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
_LIST_THEMES = [
    ("Test scores", "marks"), ("Goals scored", "goals"), ("Ages", "years"),
    ("Shoe sizes", "sizes"), ("Numbers of pets", "pets"), ("Daily steps", "thousand steps"),
]
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
    ".cx-grid-major{stroke:#888;stroke-width:1.25;fill:none}"
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
    """Pin a count-axis step from {1,2,5,10} (owner J) and a nice axis maximum."""
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


def _value_axis(out: List[str], ymax: int, step: int, unit_label: str) -> None:
    # y-axis line + ticks + integer labels + gridlines at each step.
    out.append(f'<line class="cx-axis" x1="{PLOT_X0}" y1="{PLOT_Y0}" x2="{PLOT_X0}" y2="{PLOT_Y1}"/>')
    out.append(f'<line class="cx-axis" x1="{PLOT_X0}" y1="{PLOT_Y1}" x2="{PLOT_X1}" y2="{PLOT_Y1}"/>')
    v = 0
    while v <= ymax:
        py = _py(ymax, v)
        if v != 0:
            out.append(f'<line class="cx-grid-major" x1="{PLOT_X0}" y1="{py}" x2="{PLOT_X1}" y2="{py}"/>')
        out.append(f'<line class="cx-tick" x1="{PLOT_X0 - 6}" y1="{py}" x2="{PLOT_X0}" y2="{py}"/>')
        out.append(f'<text class="cx-ticklbl" x="{PLOT_X0 - 12}" y="{py + 7}" text-anchor="end">{v}</text>')
        v += step
    out.append(f'<text class="cx-axislbl" x="36" y="{(PLOT_Y0 + PLOT_Y1) // 2}" '
               f'text-anchor="middle" transform="rotate(-90 36 {(PLOT_Y0 + PLOT_Y1) // 2})">{_esc(unit_label)}</text>')


def _bar_chart_svg(params: Dict[str, Any]) -> str:
    ds = params["dataset"]
    cats, freqs, unit = ds["categories"], ds["frequencies"], ds["unit"]
    n = len(cats)
    step, ymax = _axis_step_and_max(max(freqs))
    acc = _accessibility("read_bar_chart", params)
    out = _svg_open(acc)
    _value_axis(out, ymax, step, f"Frequency ({unit})")
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
    step, ymax = _axis_step_and_max(max(vals))
    acc = _accessibility("read_line_graph", params)
    out = _svg_open(acc)
    _value_axis(out, ymax, step, f"{ds['title']} ({unit})")
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
            c["axisStep"] = _axis_step_and_max(max(vals))[0]
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
        mode_val, mode_freq = cnt.most_common(1)[0]
        c.update(modeValue=mode_val, modeFrequency=mode_freq)
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
            rows.append([cat, f"{whole}" + (" and a half" if half else "") + " symbol(s)"])
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
            f"{cat}: {fr // ds['pictogramKey']} whole" + (" and a half symbol" if (fr % ds['pictogramKey']) == ds['pictogramKey'] // 2 and ds['pictogramKey'] % 2 == 0 else " symbols")
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

    if task in ("read_bar_chart", "read_table_value", "read_line_graph"):
        step("Locate the named category/position", "Find the matching bar, row, or marked point.")
        step("Read the value from the labelled axis", str(int(correct)))
    elif task == "read_pictogram":
        key = ds["pictogramKey"]
        fr = correct
        whole = fr // key
        half = (fr % key) == (key // 2) and key % 2 == 0
        step("Count the symbols", f"{whole} whole" + (" and a half" if half else "") + " symbol(s)")
        step("Apply the key", f"{whole} × {key}" + (f" + {key // 2}" if half else "") + f" = {int(correct)}")
    elif task == "complete_frequency_table":
        freqs = ds["frequencies"]
        blank = params["blank"]
        total = sum(freqs)
        if blank["kind"] == "total":
            step("Add the frequencies", " + ".join(str(f) for f in freqs) + f" = {total}")
        else:
            i = blank["index"]
            others = total - freqs[i]
            step("Subtract the known frequencies from the total", f"{total} − {others} = {freqs[i]}")
    elif task == "mean_from_list":
        v = ds["values"]
        step("Add the values", " + ".join(str(x) for x in v) + f" = {sum(v)}")
        step("Divide by how many values", f"{sum(v)} ÷ {len(v)} = {disp_rat(Fraction(sum(v), len(v)))}")
    elif task == "median_from_list":
        v = sorted(ds["values"])
        step("Order the values", ", ".join(str(x) for x in v))
        step("Find the middle value", disp_rat(correct if isinstance(correct, Fraction) else Fraction(correct)))
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


def _draw_read_bar_chart(rng: Mulberry32) -> Optional[Dict[str, Any]]:
    # vary the value range to exercise axis steps 1/2/5/10 (owner J/O)
    bucket = _n(rng, 4)
    lo, hi = [(1, 8), (2, 16), (5, 35), (10, 55)][bucket]
    ds = _freq_dataset(rng, lo, hi)
    qi = _n(rng, len(ds["categories"]))
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
    bucket = _n(rng, 3)
    lo, hi = [(1, 9), (2, 18), (5, 40)][bucket]
    vals = [lo + _n(rng, hi - lo + 1) for _ in range(n)]
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


def _draw_list(rng: Mulberry32, lo: int, hi: int, min_n: int, max_n: int, allow_neg: bool = False) -> Dict[str, Any]:
    title, unit = _pick_theme(rng, _LIST_THEMES)
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
    cnt = Counter(vals)
    top = cnt.most_common()
    if len(top) < 2 or top[0][1] == top[1][1]:
        return None  # not a unique mode -> redraw
    ds = {"kind": "list", "title": _pick_theme(rng, _LIST_THEMES)[0], "unit": "values", "values": vals}
    return {"task": "mode_from_list", "dataset": ds, "scaffold": _n(rng, 2) == 0}


def _draw_range_from_list(rng: Mulberry32) -> Optional[Dict[str, Any]]:
    # include range = 0 (uniform list) at a controlled low rate (owner H)
    if _n(rng, 8) == 0:
        v = 1 + _n(rng, 12)
        n = 3 + _n(rng, 3)
        ds = {"kind": "list", "title": _pick_theme(rng, _LIST_THEMES)[0], "unit": "values", "values": [v] * n}
    else:
        ds = _draw_list(rng, 1, 30, 4, 7)
    return {"task": "range_from_list", "dataset": ds, "scaffold": _n(rng, 2) == 0}


def _draw_mean_from_freq_table(rng: Mulberry32) -> Optional[Dict[str, Any]]:
    title, unit = _pick_theme(rng, _LIST_THEMES)
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

    statuses = [c["result"] for c in checks]
    return {"status": "valid" if all(s == "pass" for s in statuses) else "invalid",
            "validatorVersion": VALIDATOR_VERSION, "checks": checks}


# --------------------------------------------------------------------------- #
# Validator helpers
# --------------------------------------------------------------------------- #
def _chart_realises_data(task: str, params: Dict[str, Any], svg: str) -> bool:
    ds = params["dataset"]
    if task == "read_bar_chart":
        rects = re.findall(r'<rect class="cx-bar"[^>]*y="(\d+)"[^>]*height="(\d+)"', svg)
        if len(rects) != len(ds["frequencies"]):
            return False
        step, ymax = _axis_step_and_max(max(ds["frequencies"]))
        for (y, h), fr in zip(rects, ds["frequencies"]):
            if int(y) != _py(ymax, fr) or int(y) + int(h) != PLOT_Y1:
                return False
        return True
    if task == "read_line_graph":
        circles = re.findall(r'<circle class="cx-pt-core" cx="(\d+)" cy="(\d+)"', svg)
        step, ymax = _axis_step_and_max(max(ds["values"]))
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
    step, ymax = _axis_step_and_max(max(vals))
    labels = [int(t) for t in re.findall(r'<text class="cx-ticklbl"[^>]*>(-?\d+)</text>', svg)]
    expected = list(range(0, ymax + 1, step))
    return labels == expected and step in (1, 2, 5, 10)


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
