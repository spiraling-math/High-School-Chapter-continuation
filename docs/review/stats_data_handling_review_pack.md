# Review pack — `gen.stats.data-handling` v1.0.2

Validator v1.0.2. **28 items** (9 chart SVGs + 19 semantic tables). **Curriculum-review cells: 57/57** (derived from the distribution report: every task × supported interaction, × reachable difficulty band, × realised answer shape); extra dimensions 113/113; misconceptions 36/36. Full coverage: **True**; all items machine-valid: **True**.

Status: **PENDING REVIEW** — gated out of normal Studio + production until owner approval.
Objectives are `approved-for-implementation`; items are machine-validated, never auto-published.

## Coverage matrix (task × interaction / band / answer shape)

| Task | Interactions (reachable→seed) | Bands (reachable→seed) | Answer shapes (→seed) |
| --- | --- | --- | --- |
| `read_bar_chart` | FR→8, MC→5 | 1→8, 2→5 | integer→5 |
| `read_pictogram` | FR→1, MC→1 | 1→8, 2→1 | integer→1 |
| `read_table_value` | FR→4, MC→1 | 1→4, 2→1 | integer→1 |
| `read_line_graph` | FR→1, MC→2 | 1→2, 2→1 | integer→2 |
| `complete_frequency_table` | FR→1, MC=n/a | 2→1, 3→5 | table-completion→1 |
| `mean_from_list` | FR→2, MC→45 | 2→2, 3→45 | exact-rational→45, integer→2 |
| `median_from_list` | FR→1, MC→5 | 2→2, 3→5 | exact-rational→5, integer→2 |
| `mode_from_list` | FR→8, MC→1 | 1→8, 2→1 | integer→1 |
| `range_from_list` | FR→19, MC→1 | 1→19, 2→1 | integer→1 |
| `mean_from_freq_table` | FR→130, MC→1 | 3→1, 4→130 | exact-rational→1, integer→130 |
| `single_event_probability` | FR→6, MC→1 | 2→6, 3→1 | fraction→1 |

## 1. mean_from_list (multiple-choice) — band 3

- **Objective:** `SPI.MIDDLE.STAT.AVG.MEAN_LIST.01`
- **Answer type:** exact-rational
- **Seed:** 45
- **Prompt:** Calculate the mean of the data. Give your answer as an integer or a fraction in its simplest form.
- **Canonical answer:** `11/2`

<details><summary>figure (semantic HTML table)</summary>

<table class="cx-list">
<caption>Data values</caption>
<tbody><tr>
<td>4</td>
<td>6</td>
<td>7</td>
<td>-6</td>
<td>13</td>
<td>9</td>
</tr></tbody></table>

</details>

**Worked solution:**
  1. Add the values: 4 + 6 + 7 − 6 + 13 + 9 = 33
  2. Divide by how many values: 33 ÷ 6 = 11/2

**Distractors (misconception-backed):**
  - `33` — MISC.STAT.MEAN_NO_DIVIDE: Adds the values but forgets to divide by how many there are.
  - `33/5` — MISC.STAT.MEAN_DIVIDE_WRONG_N: Divides by the wrong number of values.
  - `7/2` — MISC.STAT.MEAN_MIDRANGE: Averages only the largest and smallest values instead of all of them.

- **Accessibility (spoken):** A list of values titled Data values.
- **Difficulty axes:** {'numericalComplexity': 0.55, 'readingDemand': 0.2, 'interpretationDemand': 0.3, 'reasoningSteps': 0.35, 'informationDensity': 1, 'scaffolding': 0.5}
- **Reproduce:** `python -c "import sys;sys.path.insert(0,'oracle/spi_oracle');import data_handling as d;print(d.serialize(d.generate(45,{"interactionType": "multiple-choice", "task": "mean_from_list"})))"`

---

## 2. read_bar_chart (multiple-choice) — band 2

- **Objective:** `SPI.MIDDLE.STAT.READ.BAR_CHART.01`
- **Answer type:** integer
- **Seed:** 5
- **Prompt:** How many children are in the category “Pear”?
- **Canonical answer:** `25`

<details><summary>figure (canonical SVG)</summary>

```svg
<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1000 700" role="img" aria-label="Vertical bar chart: Favourite fruit.">
<title>Favourite fruit</title>
<desc>A bar chart titled Favourite fruit. Read the frequency for the named category from the labelled axis.</desc>
<style>.cx-axis{stroke:#111;stroke-width:3;fill:none}.cx-tick{stroke:#111;stroke-width:2}.cx-tick-minor{stroke:#111;stroke-width:1.5}.cx-grid-major{stroke:#888;stroke-width:1.25;fill:none}.cx-grid-minor{stroke:#bbb;stroke-width:0.75;fill:none}.cx-bar{fill:#bbb;stroke:#111;stroke-width:2}.cx-line{stroke:#111;stroke-width:3;fill:none}.cx-pt-outline{fill:#fff;stroke:#111;stroke-width:4}.cx-pt-core{fill:#111}.cx-symbol{fill:#555;stroke:#111;stroke-width:1.5}text{font-family:sans-serif;font-size:24px;fill:#111}.cx-ticklbl{font-size:20px;fill:#333}.cx-catlbl{font-size:20px;fill:#111}.cx-axislbl{font-size:22px;fill:#111}.cx-keylbl{font-size:20px;fill:#111}</style>
<line class="cx-axis" x1="120" y1="70" x2="120" y2="590"/>
<line class="cx-axis" x1="120" y1="590" x2="950" y2="590"/>
<line class="cx-grid-minor" x1="120" y1="538" x2="950" y2="538"/>
<line class="cx-tick-minor" x1="116" y1="538" x2="120" y2="538"/>
<line class="cx-grid-minor" x1="120" y1="434" x2="950" y2="434"/>
<line class="cx-tick-minor" x1="116" y1="434" x2="120" y2="434"/>
<line class="cx-grid-minor" x1="120" y1="330" x2="950" y2="330"/>
<line class="cx-tick-minor" x1="116" y1="330" x2="120" y2="330"/>
<line class="cx-grid-minor" x1="120" y1="226" x2="950" y2="226"/>
<line class="cx-tick-minor" x1="116" y1="226" x2="120" y2="226"/>
<line class="cx-
```

</details>

**Worked solution:**
  1. Locate the bar for the named category: the bar for “Pear”
  2. Read its height using the vertical-axis scale: 25

**Distractors (misconception-backed):**
  - `30` — MISC.STAT.READ_OFF_BY_STEP: Reads the value one step up or down the scale.
  - `5` — MISC.STAT.READ_MISCOUNT_SCALE: Counts the squares instead of using the scale on the axis.
  - `35` — MISC.STAT.READ_OFF_BY_MAJOR_STEP: Reads the value one whole labelled gridline up or down.

- **Accessibility (spoken):** A bar chart titled Favourite fruit. Read the frequency for the named category from the labelled axis.
- **Difficulty axes:** {'numericalComplexity': 0.9, 'readingDemand': 0.25, 'interpretationDemand': 0.15, 'reasoningSteps': 0.1, 'informationDensity': 0.667, 'scaffolding': 0.1}
- **Reproduce:** `python -c "import sys;sys.path.insert(0,'oracle/spi_oracle');import data_handling as d;print(d.serialize(d.generate(5,{"interactionType": "multiple-choice", "task": "read_bar_chart"})))"`

---

## 3. median_from_list (multiple-choice) — band 3

- **Objective:** `SPI.MIDDLE.STAT.AVG.MEDIAN_LIST.01`
- **Answer type:** exact-rational
- **Seed:** 5
- **Prompt:** Find the median of the data. Give your answer as an integer or a fraction in its simplest form.
- **Canonical answer:** `11/2`

<details><summary>figure (semantic HTML table)</summary>

<table class="cx-list">
<caption>Numerical data</caption>
<tbody><tr>
<td>6</td>
<td>1</td>
<td>16</td>
<td>5</td>
<td>6</td>
<td>3</td>
</tr></tbody></table>

</details>

**Worked solution:**
  1. Order the values: 1, 3, 5, 6, 6, 16
  2. Identify the two middle values: 5 and 6
  3. Average the two middle values: (5 + 6) ÷ 2 = 11/2

**Distractors (misconception-backed):**
  - `21/2` — MISC.STAT.MEDIAN_NO_ORDER: Takes the middle value without putting the list in order first.
  - `5` — MISC.STAT.MEDIAN_WRONG_MIDDLE: Picks one of the two middle values instead of their average.
  - `6` — MISC.STAT.AVG_USES_MODE: Gives the most common value instead of the one asked for.

- **Accessibility (spoken):** A list of values titled Numerical data.
- **Difficulty axes:** {'numericalComplexity': 0.55, 'readingDemand': 0.2, 'interpretationDemand': 0.3, 'reasoningSteps': 0.35, 'informationDensity': 1, 'scaffolding': 0.5}
- **Reproduce:** `python -c "import sys;sys.path.insert(0,'oracle/spi_oracle');import data_handling as d;print(d.serialize(d.generate(5,{"interactionType": "multiple-choice", "task": "median_from_list"})))"`

---

## 4. read_pictogram (multiple-choice) — band 2

- **Objective:** `SPI.MIDDLE.STAT.READ.PICTOGRAM.01`
- **Answer type:** integer
- **Seed:** 1
- **Prompt:** Use the key to find the number of students for “Fish”.
- **Canonical answer:** `10`

<details><summary>figure (canonical SVG)</summary>

```svg
<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1000 700" role="img" aria-label="Pictogram: Favourite pet.">
<title>Favourite pet</title>
<desc>A pictogram titled Favourite pet, where one symbol represents 5 students. Read the frequency for the named category.</desc>
<style>.cx-axis{stroke:#111;stroke-width:3;fill:none}.cx-tick{stroke:#111;stroke-width:2}.cx-tick-minor{stroke:#111;stroke-width:1.5}.cx-grid-major{stroke:#888;stroke-width:1.25;fill:none}.cx-grid-minor{stroke:#bbb;stroke-width:0.75;fill:none}.cx-bar{fill:#bbb;stroke:#111;stroke-width:2}.cx-line{stroke:#111;stroke-width:3;fill:none}.cx-pt-outline{fill:#fff;stroke:#111;stroke-width:4}.cx-pt-core{fill:#111}.cx-symbol{fill:#555;stroke:#111;stroke-width:1.5}text{font-family:sans-serif;font-size:24px;fill:#111}.cx-ticklbl{font-size:20px;fill:#333}.cx-catlbl{font-size:20px;fill:#111}.cx-axislbl{font-size:22px;fill:#111}.cx-keylbl{font-size:20px;fill:#111}</style>
<text class="cx-keylbl" x="120" y="48">Key: 1 symbol represents 5 students.</text>
<text class="cx-catlbl" x="80" y="114" text-anchor="start">Cat</text>
<rect class="cx-symbol" data-cat="0" x="280" y="90" width="34" height="34" rx="6"/>
<rect class="cx-symbol" data-cat="0" x="324" y="90" width="34" height="34" rx="6"/>
<rect class="cx-symbol" data-cat="0" x="368" y="90" width="34" height="34" rx="6"/>
<rect class="cx-symbol" data-cat="0" x="412" y="90" width="34" height="34" rx="6"/>
<rect class="cx-symbol" data-cat="0" x="456" y="90" width="34" height="34" rx="6"/>
<text class="cx-catlbl" x="80" y="184" text-anchor="start">Dog</text>
<rect class="cx-sy
```

</details>

**Worked solution:**
  1. Count the whole and half symbols in the named row: 2 whole symbols
  2. Apply the displayed key: 2 × 5 = 10

**Distractors (misconception-backed):**
  - `2` — MISC.STAT.PICTO_COUNTS_SYMBOLS: Counts the symbols without using the key.
  - `20` — MISC.STAT.READ_WRONG_CATEGORY: Reads the frequency of a neighbouring category.
  - `5` — MISC.STAT.PICTO_OFF_BY_ONE_SYMBOL: Counts one symbol too few when reading the row.

- **Accessibility (spoken):** A pictogram titled Favourite pet, where one symbol represents 5 students. Read the frequency for the named category.
- **Difficulty axes:** {'numericalComplexity': 0.4, 'readingDemand': 0.2, 'interpretationDemand': 0.25, 'reasoningSteps': 0.15, 'informationDensity': 0.333, 'scaffolding': 0.1}
- **Reproduce:** `python -c "import sys;sys.path.insert(0,'oracle/spi_oracle');import data_handling as d;print(d.serialize(d.generate(1,{"interactionType": "multiple-choice", "task": "read_pictogram"})))"`

---

## 5. range_from_list (multiple-choice) — band 2

- **Objective:** `SPI.MIDDLE.STAT.AVG.RANGE_LIST.01`
- **Answer type:** integer
- **Seed:** 1
- **Prompt:** Work out the range of the data.
- **Canonical answer:** `21`

<details><summary>figure (semantic HTML table)</summary>

<table class="cx-list">
<caption>Test scores</caption>
<tbody><tr>
<td>30</td>
<td>30</td>
<td>9</td>
<td>19</td>
<td>22</td>
<td>13</td>
</tr></tbody></table>

</details>

**Worked solution:**
  1. Identify the largest and smallest values: largest 30, smallest 9
  2. Subtract: 30 − 9 = 21

**Distractors (misconception-backed):**
  - `30` — MISC.STAT.RANGE_IS_MAX: Gives the largest value instead of the difference.
  - `39` — MISC.STAT.RANGE_ADDS: Adds the largest and smallest values instead of subtracting.
  - `9` — MISC.STAT.RANGE_IS_MIN: Gives the smallest value instead of the difference.

- **Accessibility (spoken):** A list of values titled Test scores.
- **Difficulty axes:** {'numericalComplexity': 0.45, 'readingDemand': 0.2, 'interpretationDemand': 0.2, 'reasoningSteps': 0.2, 'informationDensity': 0.667, 'scaffolding': 0.5}
- **Reproduce:** `python -c "import sys;sys.path.insert(0,'oracle/spi_oracle');import data_handling as d;print(d.serialize(d.generate(1,{"interactionType": "multiple-choice", "task": "range_from_list"})))"`

---

## 6. single_event_probability (multiple-choice) — band 3

- **Objective:** `SPI.MIDDLE.STAT.PROB.SINGLE_EVENT.01`
- **Answer type:** fraction
- **Seed:** 1
- **Prompt:** One bead is chosen at random from a box of beads containing the beads shown (each bead is equally likely). What is the probability that the bead chosen is Red? Give your answer as a fraction in its simplest form.
- **Canonical answer:** `1/5`

<details><summary>figure (semantic HTML table)</summary>

<table class="cx-table">
<caption>Contents of a box of beads</caption>
<thead><tr><th scope="col">Type</th><th scope="col">How many</th></tr></thead>
<tbody>
<tr><th scope="row">Red</th><td>3</td></tr>
<tr><th scope="row">Blue</th><td>6</td></tr>
<tr><th scope="row">White</th><td>3</td></tr>
<tr><th scope="row">Black</th><td>3</td></tr>
<tr class="cx-total"><th scope="row">Total</th><td>15</td></tr>
</tbody></table>

</details>

**Worked solution:**
  1. Count favourable and total outcomes: 3 favourable out of 15
  2. Write as a fraction in simplest form: 1/5

**Distractors (misconception-backed):**
  - `4/5` — MISC.STAT.PROB_COMPLEMENT: Counts the outcomes that are not wanted instead of the ones that are.
  - `1/4` — MISC.STAT.PROB_ODDS: Compares wanted outcomes to unwanted outcomes instead of to the total.
  - `2/15` — MISC.STAT.PROB_OFF_BY_ONE: Counts one too few or one too many of the wanted outcomes.

**Common-error notes:**
  - MISC.STAT.PROB_UNREDUCED: Writes a correct but unsimplified fraction. → _Your value is equivalent, but simplify the fraction to its simplest form._

- **Accessibility (spoken):** A frequency table titled Contents of a box of beads.
- **Difficulty axes:** {'numericalComplexity': 1, 'readingDemand': 0.25, 'interpretationDemand': 0.4, 'reasoningSteps': 0.35, 'informationDensity': 0.667, 'scaffolding': 0.5}
- **Reproduce:** `python -c "import sys;sys.path.insert(0,'oracle/spi_oracle');import data_handling as d;print(d.serialize(d.generate(1,{"interactionType": "multiple-choice", "task": "single_event_probability"})))"`

---

## 7. read_table_value (multiple-choice) — band 2

- **Objective:** `SPI.MIDDLE.STAT.READ.TABLE_VALUE.01`
- **Answer type:** integer
- **Seed:** 1
- **Prompt:** How many cars are in the category “Black”?
- **Canonical answer:** `12`

<details><summary>figure (semantic HTML table)</summary>

<table class="cx-table">
<caption>Colour of car</caption>
<thead><tr><th scope="col">Category</th><th scope="col">Frequency</th></tr></thead>
<tbody>
<tr><th scope="row">Red</th><td>12</td></tr>
<tr><th scope="row">Blue</th><td>25</td></tr>
<tr><th scope="row">Black</th><td>12</td></tr>
<tr><th scope="row">White</th><td>13</td></tr>
<tr><th scope="row">Silver</th><td>5</td></tr>
<tr class="cx-total"><th scope="row">Total</th><td>67</td></tr>
</tbody></table>

</details>

**Worked solution:**
  1. Locate the row for the named category: the row for “Black”
  2. Read the frequency in that row: 12

**Distractors (misconception-backed):**
  - `67` — MISC.STAT.TABLE_READS_TOTAL: Reads the total instead of the row that was asked for.
  - `13` — MISC.STAT.TABLE_ADJACENT_ROW: Reads the frequency from the wrong row of the table.
  - `25` — MISC.STAT.TABLE_READS_LARGEST: Reads the largest frequency in the table instead of the named category.

- **Accessibility (spoken):** A frequency table titled Colour of car.
- **Difficulty axes:** {'numericalComplexity': 0.5, 'readingDemand': 0.25, 'interpretationDemand': 0.1, 'reasoningSteps': 0.1, 'informationDensity': 0.667, 'scaffolding': 0.5}
- **Reproduce:** `python -c "import sys;sys.path.insert(0,'oracle/spi_oracle');import data_handling as d;print(d.serialize(d.generate(1,{"interactionType": "multiple-choice", "task": "read_table_value"})))"`

---

## 8. mode_from_list (multiple-choice) — band 2

- **Objective:** `SPI.MIDDLE.STAT.AVG.MODE_LIST.01`
- **Answer type:** integer
- **Seed:** 1
- **Prompt:** Write down the mode of the data.
- **Canonical answer:** `4`

<details><summary>figure (semantic HTML table)</summary>

<table class="cx-list">
<caption>Goals scored</caption>
<tbody><tr>
<td>4</td>
<td>8</td>
<td>4</td>
<td>10</td>
<td>10</td>
<td>4</td>
</tr></tbody></table>

</details>

**Worked solution:**
  1. Count how many times each value occurs: Tally the values.
  2. Identify the most common value: 4

**Distractors (misconception-backed):**
  - `10` — MISC.STAT.MODE_USES_HIGHEST: Gives the largest value instead of the most common one.
  - `3` — MISC.STAT.MODE_USES_FREQUENCY: Gives how many times the mode occurs instead of the value itself.
  - `6` — MISC.STAT.AVG_USES_MEDIAN: Gives the middle value instead of the most common one.

- **Accessibility (spoken):** A list of values titled Goals scored.
- **Difficulty axes:** {'numericalComplexity': 0.2, 'readingDemand': 0.2, 'interpretationDemand': 0.2, 'reasoningSteps': 0.2, 'informationDensity': 0.333, 'scaffolding': 0.5}
- **Reproduce:** `python -c "import sys;sys.path.insert(0,'oracle/spi_oracle');import data_handling as d;print(d.serialize(d.generate(1,{"interactionType": "multiple-choice", "task": "mode_from_list"})))"`

---

## 9. read_line_graph (multiple-choice) — band 1

- **Objective:** `SPI.MIDDLE.STAT.READ.LINE_GRAPH.01`
- **Answer type:** integer
- **Seed:** 2
- **Prompt:** What is the value at Day 4?
- **Canonical answer:** `9`

<details><summary>figure (canonical SVG)</summary>

```svg
<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1000 700" role="img" aria-label="Line graph: Plant height.">
<title>Plant height</title>
<desc>A line graph titled Plant height with marked points at each labelled position. Read the value at the named position.</desc>
<style>.cx-axis{stroke:#111;stroke-width:3;fill:none}.cx-tick{stroke:#111;stroke-width:2}.cx-tick-minor{stroke:#111;stroke-width:1.5}.cx-grid-major{stroke:#888;stroke-width:1.25;fill:none}.cx-grid-minor{stroke:#bbb;stroke-width:0.75;fill:none}.cx-bar{fill:#bbb;stroke:#111;stroke-width:2}.cx-line{stroke:#111;stroke-width:3;fill:none}.cx-pt-outline{fill:#fff;stroke:#111;stroke-width:4}.cx-pt-core{fill:#111}.cx-symbol{fill:#555;stroke:#111;stroke-width:1.5}text{font-family:sans-serif;font-size:24px;fill:#111}.cx-ticklbl{font-size:20px;fill:#333}.cx-catlbl{font-size:20px;fill:#111}.cx-axislbl{font-size:22px;fill:#111}.cx-keylbl{font-size:20px;fill:#111}</style>
<line class="cx-axis" x1="120" y1="70" x2="120" y2="590"/>
<line class="cx-axis" x1="120" y1="590" x2="950" y2="590"/>
<line class="cx-grid-minor" x1="120" y1="557" x2="950" y2="557"/>
<line class="cx-tick-minor" x1="116" y1="557" x2="120" y2="557"/>
<line class="cx-grid-minor" x1="120" y1="492" x2="950" y2="492"/>
<line class="cx-tick-minor" x1="116" y1="492" x2="120" y2="492"/>
<line class="cx-grid-minor" x1="120" y1="427" x2="950" y2="427"/>
<line class="cx-tick-minor" x1="116" y1="427" x2="120" y2="427"/>
<line class="cx-grid-minor" x1="120" y1="362" x2="950" y2="362"/>
<line class="cx-tick-minor" x1="116" y1="362" x2="120" y2="362"/>
<line class="cx
```

</details>

**Worked solution:**
  1. Locate the requested position on the horizontal axis: Day 4
  2. Read the value of the marked point from the vertical axis: 9

**Distractors (misconception-backed):**
  - `10` — MISC.STAT.READ_OFF_BY_STEP: Reads the value one step up or down the scale.
  - `4` — MISC.STAT.LINE_SWAPS_AXES: Reads the value off the horizontal axis instead of the vertical axis.
  - `11` — MISC.STAT.READ_OFF_BY_MAJOR_STEP: Reads the value one whole labelled gridline up or down.

- **Accessibility (spoken):** A line graph titled Plant height with marked points at each labelled position. Read the value at the named position.
- **Difficulty axes:** {'numericalComplexity': 0.3, 'readingDemand': 0.25, 'interpretationDemand': 0.2, 'reasoningSteps': 0.1, 'informationDensity': 0, 'scaffolding': 0.1}
- **Reproduce:** `python -c "import sys;sys.path.insert(0,'oracle/spi_oracle');import data_handling as d;print(d.serialize(d.generate(2,{"interactionType": "multiple-choice", "task": "read_line_graph"})))"`

---

## 10. median_from_list (multiple-choice) — band 2

- **Objective:** `SPI.MIDDLE.STAT.AVG.MEDIAN_LIST.01`
- **Answer type:** integer
- **Seed:** 2
- **Prompt:** Find the median of the data. Give your answer as an integer or a fraction in its simplest form.
- **Canonical answer:** `11`

<details><summary>figure (semantic HTML table)</summary>

<table class="cx-list">
<caption>Daily steps</caption>
<tbody><tr>
<td>6</td>
<td>11</td>
<td>18</td>
<td>13</td>
<td>10</td>
</tr></tbody></table>

</details>

**Worked solution:**
  1. Order the values: 6, 10, 11, 13, 18
  2. Identify the single middle value: 11

**Distractors (misconception-backed):**
  - `18` — MISC.STAT.MEDIAN_NO_ORDER: Takes the middle value without putting the list in order first.
  - `58/5` — MISC.STAT.MEDIAN_USES_MEAN: Adds the values and divides instead of finding the middle value.
  - `12` — MISC.STAT.MEDIAN_MIDRANGE: Averages the largest and smallest values instead of finding the middle.

- **Accessibility (spoken):** A list of values titled Daily steps.
- **Difficulty axes:** {'numericalComplexity': 0.3, 'readingDemand': 0.2, 'interpretationDemand': 0.3, 'reasoningSteps': 0.35, 'informationDensity': 0.667, 'scaffolding': 0.5}
- **Reproduce:** `python -c "import sys;sys.path.insert(0,'oracle/spi_oracle');import data_handling as d;print(d.serialize(d.generate(2,{"interactionType": "multiple-choice", "task": "median_from_list"})))"`

---

## 11. mean_from_freq_table (multiple-choice) — band 3

- **Objective:** `SPI.MIDDLE.STAT.AVG.MEAN_FREQ_TABLE.01`
- **Answer type:** exact-rational
- **Seed:** 1
- **Prompt:** Calculate the mean from the frequency table. Give your answer as an integer or a fraction in its simplest form.
- **Canonical answer:** `12/7`

<details><summary>figure (semantic HTML table)</summary>

<table class="cx-table">
<caption>Shoe sizes</caption>
<thead><tr><th scope="col">Value</th><th scope="col">Frequency</th></tr></thead>
<tbody>
<tr><th scope="row">1</th><td>6</td></tr>
<tr><th scope="row">2</th><td>6</td></tr>
<tr><th scope="row">3</th><td>2</td></tr>
</tbody></table>

</details>

**Worked solution:**
  1. Multiply each value by its frequency and add: 1×6 + 2×6 + 3×2 = 24
  2. Divide by the total frequency: 24 ÷ 14 = 12/7

**Distractors (misconception-backed):**
  - `8` — MISC.STAT.MEANFT_DIVIDE_BY_CATEGORIES: Divides the total by the number of rows instead of the total frequency.
  - `2` — MISC.STAT.MEANFT_NO_WEIGHT: Averages the listed values without using the frequencies.
  - `24/13` — MISC.STAT.MEAN_DIVIDE_WRONG_N: Divides by the wrong number of values.

- **Accessibility (spoken):** A frequency table titled Shoe sizes.
- **Difficulty axes:** {'numericalComplexity': 0.8, 'readingDemand': 0.4, 'interpretationDemand': 0.55, 'reasoningSteps': 0.7, 'informationDensity': 0, 'scaffolding': 0.5}
- **Reproduce:** `python -c "import sys;sys.path.insert(0,'oracle/spi_oracle');import data_handling as d;print(d.serialize(d.generate(1,{"interactionType": "multiple-choice", "task": "mean_from_freq_table"})))"`

---

## 12. read_pictogram (multiple-choice) — band 1

- **Objective:** `SPI.MIDDLE.STAT.READ.PICTOGRAM.01`
- **Answer type:** integer
- **Seed:** 8
- **Prompt:** Use the key to find the number of pupils for “Tennis”.
- **Canonical answer:** `9`

<details><summary>figure (canonical SVG)</summary>

```svg
<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1000 700" role="img" aria-label="Pictogram: Sport played.">
<title>Sport played</title>
<desc>A pictogram titled Sport played, where one symbol represents 2 pupils. Read the frequency for the named category.</desc>
<style>.cx-axis{stroke:#111;stroke-width:3;fill:none}.cx-tick{stroke:#111;stroke-width:2}.cx-tick-minor{stroke:#111;stroke-width:1.5}.cx-grid-major{stroke:#888;stroke-width:1.25;fill:none}.cx-grid-minor{stroke:#bbb;stroke-width:0.75;fill:none}.cx-bar{fill:#bbb;stroke:#111;stroke-width:2}.cx-line{stroke:#111;stroke-width:3;fill:none}.cx-pt-outline{fill:#fff;stroke:#111;stroke-width:4}.cx-pt-core{fill:#111}.cx-symbol{fill:#555;stroke:#111;stroke-width:1.5}text{font-family:sans-serif;font-size:24px;fill:#111}.cx-ticklbl{font-size:20px;fill:#333}.cx-catlbl{font-size:20px;fill:#111}.cx-axislbl{font-size:22px;fill:#111}.cx-keylbl{font-size:20px;fill:#111}</style>
<text class="cx-keylbl" x="120" y="48">Key: 1 symbol represents 2 pupils.</text>
<text class="cx-catlbl" x="80" y="114" text-anchor="start">Football</text>
<rect class="cx-symbol" data-cat="0" x="280" y="90" width="34" height="34" rx="6"/>
<text class="cx-catlbl" x="80" y="184" text-anchor="start">Tennis</text>
<rect class="cx-symbol" data-cat="1" x="280" y="160" width="34" height="34" rx="6"/>
<rect class="cx-symbol" data-cat="1" x="324" y="160" width="34" height="34" rx="6"/>
<rect class="cx-symbol" data-cat="1" x="368" y="160" width="34" height="34" rx="6"/>
<rect class="cx-symbol" data-cat="1" x="412" y="160" width="34" height="34" rx="6"/>
<rect class="
```

</details>

**Worked solution:**
  1. Count the whole and half symbols in the named row: 4 whole symbols and 1 half symbol
  2. Apply the displayed key: 4 × 2 + 1 = 9

**Distractors (misconception-backed):**
  - `8` — MISC.STAT.PICTO_IGNORES_HALF: Leaves out the value of the half symbol.
  - `10` — MISC.STAT.PICTO_HALF_AS_WHOLE: Counts the half symbol as if it were a whole symbol.
  - `3` — MISC.STAT.READ_WRONG_CATEGORY: Reads the frequency of a neighbouring category.

- **Accessibility (spoken):** A pictogram titled Sport played, where one symbol represents 2 pupils. Read the frequency for the named category.
- **Difficulty axes:** {'numericalComplexity': 0.3, 'readingDemand': 0.15, 'interpretationDemand': 0.25, 'reasoningSteps': 0.15, 'informationDensity': 0, 'scaffolding': 0.1}
- **Reproduce:** `python -c "import sys;sys.path.insert(0,'oracle/spi_oracle');import data_handling as d;print(d.serialize(d.generate(8,{"interactionType": "multiple-choice", "task": "read_pictogram"})))"`

---

## 13. complete_frequency_table (free-response) — band 2

- **Objective:** `SPI.MIDDLE.STAT.FREQ.COMPLETE_TABLE.01`
- **Answer type:** table-completion
- **Seed:** 1
- **Prompt:** Find the missing value in the frequency table.
- **Canonical answer:** `46`

<details><summary>figure (semantic HTML table)</summary>

<table class="cx-table">
<caption>Colour of car</caption>
<thead><tr><th scope="col">Category</th><th scope="col">Frequency</th></tr></thead>
<tbody>
<tr><th scope="row">Red</th><td>10</td></tr>
<tr><th scope="row">Blue</th><td>18</td></tr>
<tr><th scope="row">Black</th><td>18</td></tr>
<tr class="cx-total"><th scope="row">Total</th><td class="cx-blank"><input type="text" inputmode="numeric" aria-label="Total frequency"></td></tr>
</tbody></table>

</details>

**Worked solution:**
  1. Add every displayed frequency: 10 + 18 + 18 = 46

**Common-error notes:**
  - MISC.STAT.FREQ_TOTAL_OMITS_CATEGORY: Leaves a category out when adding up the total. → _Add every category's frequency — don't miss one out._
  - MISC.STAT.FREQ_TOTAL_COPIES_ONE: Writes one of the frequencies as the total instead of their sum. → _The total is the sum of all the frequencies, not a single one of them._

- **Accessibility (spoken):** A frequency table titled Colour of car.
- **Difficulty axes:** {'numericalComplexity': 0.767, 'readingDemand': 0.25, 'interpretationDemand': 0.3, 'reasoningSteps': 0.3, 'informationDensity': 0, 'scaffolding': 0.5}
- **Reproduce:** `python -c "import sys;sys.path.insert(0,'oracle/spi_oracle');import data_handling as d;print(d.serialize(d.generate(1,{"interactionType": "free-response", "task": "complete_frequency_table"})))"`

---

## 14. mean_from_list (free-response) — band 2

- **Objective:** `SPI.MIDDLE.STAT.AVG.MEAN_LIST.01`
- **Answer type:** integer
- **Seed:** 2
- **Prompt:** Calculate the mean of the data. Give your answer as an integer or a fraction in its simplest form.
- **Canonical answer:** `13`

<details><summary>figure (semantic HTML table)</summary>

<table class="cx-list">
<caption>Ages</caption>
<tbody><tr>
<td>11</td>
<td>18</td>
<td>13</td>
<td>10</td>
</tr></tbody></table>

</details>

**Worked solution:**
  1. Add the values: 11 + 18 + 13 + 10 = 52
  2. Divide by how many values: 52 ÷ 4 = 13

- **Accessibility (spoken):** A list of values titled Ages.
- **Difficulty axes:** {'numericalComplexity': 0.3, 'readingDemand': 0.2, 'interpretationDemand': 0.3, 'reasoningSteps': 0.35, 'informationDensity': 0.333, 'scaffolding': 0.1}
- **Reproduce:** `python -c "import sys;sys.path.insert(0,'oracle/spi_oracle');import data_handling as d;print(d.serialize(d.generate(2,{"interactionType": "free-response", "task": "mean_from_list"})))"`

---

## 15. read_bar_chart (free-response) — band 1

- **Objective:** `SPI.MIDDLE.STAT.READ.BAR_CHART.01`
- **Answer type:** integer
- **Seed:** 8
- **Prompt:** How many cars are in the category “Black”?
- **Canonical answer:** `4`

<details><summary>figure (canonical SVG)</summary>

```svg
<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1000 700" role="img" aria-label="Vertical bar chart: Colour of car.">
<title>Colour of car</title>
<desc>A bar chart titled Colour of car. Read the frequency for the named category from the labelled axis.</desc>
<style>.cx-axis{stroke:#111;stroke-width:3;fill:none}.cx-tick{stroke:#111;stroke-width:2}.cx-tick-minor{stroke:#111;stroke-width:1.5}.cx-grid-major{stroke:#888;stroke-width:1.25;fill:none}.cx-grid-minor{stroke:#bbb;stroke-width:0.75;fill:none}.cx-bar{fill:#bbb;stroke:#111;stroke-width:2}.cx-line{stroke:#111;stroke-width:3;fill:none}.cx-pt-outline{fill:#fff;stroke:#111;stroke-width:4}.cx-pt-core{fill:#111}.cx-symbol{fill:#555;stroke:#111;stroke-width:1.5}text{font-family:sans-serif;font-size:24px;fill:#111}.cx-ticklbl{font-size:20px;fill:#333}.cx-catlbl{font-size:20px;fill:#111}.cx-axislbl{font-size:22px;fill:#111}.cx-keylbl{font-size:20px;fill:#111}</style>
<line class="cx-axis" x1="120" y1="70" x2="120" y2="590"/>
<line class="cx-axis" x1="120" y1="590" x2="950" y2="590"/>
<line class="cx-tick" x1="114" y1="590" x2="120" y2="590"/>
<text class="cx-ticklbl" x="108" y="597" text-anchor="end">0</text>
<line class="cx-grid-major" x1="120" y1="503" x2="950" y2="503"/>
<line class="cx-tick" x1="114" y1="503" x2="120" y2="503"/>
<text class="cx-ticklbl" x="108" y="510" text-anchor="end">1</text>
<line class="cx-grid-major" x1="120" y1="417" x2="950" y2="417"/>
<line class="cx-tick" x1="114" y1="417" x2="120" y2="417"/>
<text class="cx-ticklbl" x="108" y="424" text-anchor="end">2</text>
<line class="cx-grid-major" x1="12
```

</details>

**Worked solution:**
  1. Locate the bar for the named category: the bar for “Black”
  2. Read its height using the vertical-axis scale: 4

- **Accessibility (spoken):** A bar chart titled Colour of car. Read the frequency for the named category from the labelled axis.
- **Difficulty axes:** {'numericalComplexity': 0.12, 'readingDemand': 0.15, 'interpretationDemand': 0.15, 'reasoningSteps': 0.1, 'informationDensity': 0, 'scaffolding': 0.1}
- **Reproduce:** `python -c "import sys;sys.path.insert(0,'oracle/spi_oracle');import data_handling as d;print(d.serialize(d.generate(8,{"interactionType": "free-response", "task": "read_bar_chart"})))"`

---

## 16. range_from_list (free-response) — band 1

- **Objective:** `SPI.MIDDLE.STAT.AVG.RANGE_LIST.01`
- **Answer type:** integer
- **Seed:** 19
- **Prompt:** Work out the range of the data.
- **Canonical answer:** `0`

<details><summary>figure (semantic HTML table)</summary>

<table class="cx-list">
<caption>Numbers of pets</caption>
<tbody><tr>
<td>4</td>
<td>4</td>
<td>4</td>
<td>4</td>
</tr></tbody></table>

</details>

**Worked solution:**
  1. Identify the largest and smallest values: largest 4, smallest 4
  2. Subtract: 4 − 4 = 0

- **Accessibility (spoken):** A list of values titled Numbers of pets.
- **Difficulty axes:** {'numericalComplexity': 0.1, 'readingDemand': 0.2, 'interpretationDemand': 0.2, 'reasoningSteps': 0.2, 'informationDensity': 0, 'scaffolding': 0.5}
- **Reproduce:** `python -c "import sys;sys.path.insert(0,'oracle/spi_oracle');import data_handling as d;print(d.serialize(d.generate(19,{"interactionType": "free-response", "task": "range_from_list"})))"`

---

## 17. mean_from_freq_table (free-response) — band 4

- **Objective:** `SPI.MIDDLE.STAT.AVG.MEAN_FREQ_TABLE.01`
- **Answer type:** integer
- **Seed:** 130
- **Prompt:** Calculate the mean from the frequency table. Give your answer as an integer or a fraction in its simplest form.
- **Canonical answer:** `5`

<details><summary>figure (semantic HTML table)</summary>

<table class="cx-table">
<caption>Goals scored</caption>
<thead><tr><th scope="col">Value</th><th scope="col">Frequency</th></tr></thead>
<tbody>
<tr><th scope="row">2</th><td>1</td></tr>
<tr><th scope="row">3</th><td>3</td></tr>
<tr><th scope="row">4</th><td>2</td></tr>
<tr><th scope="row">5</th><td>5</td></tr>
<tr><th scope="row">6</th><td>3</td></tr>
<tr><th scope="row">7</th><td>4</td></tr>
</tbody></table>

</details>

**Worked solution:**
  1. Multiply each value by its frequency and add: 2×1 + 3×3 + 4×2 + 5×5 + 6×3 + 7×4 = 90
  2. Divide by the total frequency: 90 ÷ 18 = 5

- **Accessibility (spoken):** A frequency table titled Goals scored.
- **Difficulty axes:** {'numericalComplexity': 0.55, 'readingDemand': 0.55, 'interpretationDemand': 0.55, 'reasoningSteps': 0.7, 'informationDensity': 1, 'scaffolding': 0.5}
- **Reproduce:** `python -c "import sys;sys.path.insert(0,'oracle/spi_oracle');import data_handling as d;print(d.serialize(d.generate(130,{"interactionType": "free-response", "task": "mean_from_freq_table"})))"`

---

## 18. single_event_probability (free-response) — band 2

- **Objective:** `SPI.MIDDLE.STAT.PROB.SINGLE_EVENT.01`
- **Answer type:** fraction
- **Seed:** 6
- **Prompt:** One bead is chosen at random from a box of beads containing the beads shown (each bead is equally likely). What is the probability that the bead chosen is Blue? Give your answer as a fraction in its simplest form.
- **Canonical answer:** `0`

<details><summary>figure (semantic HTML table)</summary>

<table class="cx-table">
<caption>Contents of a box of beads</caption>
<thead><tr><th scope="col">Type</th><th scope="col">How many</th></tr></thead>
<tbody>
<tr><th scope="row">Red</th><td>4</td></tr>
<tr><th scope="row">Blue</th><td>0</td></tr>
<tr class="cx-total"><th scope="row">Total</th><td>4</td></tr>
</tbody></table>

</details>

**Worked solution:**
  1. Count favourable and total outcomes: 0 favourable out of 4
  2. Write as a fraction in simplest form: 0

**Common-error notes:**
  - MISC.STAT.PROB_UNREDUCED: Writes a correct but unsimplified fraction. → _Your value is equivalent, but simplify the fraction to its simplest form._

- **Accessibility (spoken):** A frequency table titled Contents of a box of beads.
- **Difficulty axes:** {'numericalComplexity': 0.25, 'readingDemand': 0.25, 'interpretationDemand': 0.4, 'reasoningSteps': 0.35, 'informationDensity': 0, 'scaffolding': 0.5}
- **Reproduce:** `python -c "import sys;sys.path.insert(0,'oracle/spi_oracle');import data_handling as d;print(d.serialize(d.generate(6,{"interactionType": "free-response", "task": "single_event_probability"})))"`

---

## 19. read_table_value (free-response) — band 1

- **Objective:** `SPI.MIDDLE.STAT.READ.TABLE_VALUE.01`
- **Answer type:** integer
- **Seed:** 4
- **Prompt:** How many readers are in the category “Fantasy”?
- **Canonical answer:** `3`

<details><summary>figure (semantic HTML table)</summary>

<table class="cx-table">
<caption>Books read</caption>
<thead><tr><th scope="col">Category</th><th scope="col">Frequency</th></tr></thead>
<tbody>
<tr><th scope="row">Mystery</th><td>7</td></tr>
<tr><th scope="row">Fantasy</th><td>3</td></tr>
<tr><th scope="row">Comic</th><td>7</td></tr>
<tr class="cx-total"><th scope="row">Total</th><td>17</td></tr>
</tbody></table>

</details>

**Worked solution:**
  1. Locate the row for the named category: the row for “Fantasy”
  2. Read the frequency in that row: 3

- **Accessibility (spoken):** A frequency table titled Books read.
- **Difficulty axes:** {'numericalComplexity': 0.14, 'readingDemand': 0.15, 'interpretationDemand': 0.1, 'reasoningSteps': 0.1, 'informationDensity': 0, 'scaffolding': 0.5}
- **Reproduce:** `python -c "import sys;sys.path.insert(0,'oracle/spi_oracle');import data_handling as d;print(d.serialize(d.generate(4,{"interactionType": "free-response", "task": "read_table_value"})))"`

---

## 20. read_line_graph (free-response) — band 2

- **Objective:** `SPI.MIDDLE.STAT.READ.LINE_GRAPH.01`
- **Answer type:** integer
- **Seed:** 1
- **Prompt:** What is the value at Day 3?
- **Canonical answer:** `10`

<details><summary>figure (canonical SVG)</summary>

```svg
<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1000 700" role="img" aria-label="Line graph: Plant height.">
<title>Plant height</title>
<desc>A line graph titled Plant height with marked points at each labelled position. Read the value at the named position.</desc>
<style>.cx-axis{stroke:#111;stroke-width:3;fill:none}.cx-tick{stroke:#111;stroke-width:2}.cx-tick-minor{stroke:#111;stroke-width:1.5}.cx-grid-major{stroke:#888;stroke-width:1.25;fill:none}.cx-grid-minor{stroke:#bbb;stroke-width:0.75;fill:none}.cx-bar{fill:#bbb;stroke:#111;stroke-width:2}.cx-line{stroke:#111;stroke-width:3;fill:none}.cx-pt-outline{fill:#fff;stroke:#111;stroke-width:4}.cx-pt-core{fill:#111}.cx-symbol{fill:#555;stroke:#111;stroke-width:1.5}text{font-family:sans-serif;font-size:24px;fill:#111}.cx-ticklbl{font-size:20px;fill:#333}.cx-catlbl{font-size:20px;fill:#111}.cx-axislbl{font-size:22px;fill:#111}.cx-keylbl{font-size:20px;fill:#111}</style>
<line class="cx-axis" x1="120" y1="70" x2="120" y2="590"/>
<line class="cx-axis" x1="120" y1="590" x2="950" y2="590"/>
<line class="cx-tick" x1="114" y1="590" x2="120" y2="590"/>
<text class="cx-ticklbl" x="108" y="597" text-anchor="end">0</text>
<line class="cx-grid-major" x1="120" y1="516" x2="950" y2="516"/>
<line class="cx-tick" x1="114" y1="516" x2="120" y2="516"/>
<text class="cx-ticklbl" x="108" y="523" text-anchor="end">5</text>
<line class="cx-grid-major" x1="120" y1="441" x2="950" y2="441"/>
<line class="cx-tick" x1="114" y1="441" x2="120" y2="441"/>
<text class="cx-ticklbl" x="108" y="448" text-anchor="end">10</text>
<line class="cx-grid-major
```

</details>

**Worked solution:**
  1. Locate the requested position on the horizontal axis: Day 3
  2. Read the value of the marked point from the vertical axis: 10

- **Accessibility (spoken):** A line graph titled Plant height with marked points at each labelled position. Read the value at the named position.
- **Difficulty axes:** {'numericalComplexity': 0.7, 'readingDemand': 0.25, 'interpretationDemand': 0.2, 'reasoningSteps': 0.1, 'informationDensity': 0, 'scaffolding': 0.5}
- **Reproduce:** `python -c "import sys;sys.path.insert(0,'oracle/spi_oracle');import data_handling as d;print(d.serialize(d.generate(1,{"interactionType": "free-response", "task": "read_line_graph"})))"`

---

## 21. complete_frequency_table (free-response) — band 3

- **Objective:** `SPI.MIDDLE.STAT.FREQ.COMPLETE_TABLE.01`
- **Answer type:** table-completion
- **Seed:** 5
- **Prompt:** Find the missing value in the frequency table.
- **Canonical answer:** `14`

<details><summary>figure (semantic HTML table)</summary>

<table class="cx-table">
<caption>Colour of car</caption>
<thead><tr><th scope="col">Category</th><th scope="col">Frequency</th></tr></thead>
<tbody>
<tr><th scope="row">Red</th><td>5</td></tr>
<tr><th scope="row">Blue</th><td>12</td></tr>
<tr><th scope="row">Black</th><td>3</td></tr>
<tr><th scope="row">White</th><td>12</td></tr>
<tr><th scope="row">Silver</th><td class="cx-blank"><input type="text" inputmode="numeric" aria-label="Frequency for Silver"></td></tr>
<tr class="cx-total"><th scope="row">Total</th><td>46</td></tr>
</tbody></table>

</details>

**Worked solution:**
  1. Subtract the sum of the known frequencies from the displayed total: 46 − 32 = 14

**Common-error notes:**
  - MISC.STAT.FREQ_SUBTRACT_WRONG_WAY: Adds the known frequencies to the total instead of subtracting. → _The frequencies add up to the total, so subtract the ones you know from the total._
  - MISC.STAT.FREQ_IGNORES_TOTAL: Adds up the other frequencies but ignores the given total. → _Use the total: the missing frequency is the total minus the frequencies you already have._

- **Accessibility (spoken):** A frequency table titled Colour of car.
- **Difficulty axes:** {'numericalComplexity': 0.767, 'readingDemand': 0.35, 'interpretationDemand': 0.3, 'reasoningSteps': 0.3, 'informationDensity': 0.667, 'scaffolding': 0.5}
- **Reproduce:** `python -c "import sys;sys.path.insert(0,'oracle/spi_oracle');import data_handling as d;print(d.serialize(d.generate(5,{"interactionType": "free-response", "task": "complete_frequency_table"})))"`

---

## 22. mode_from_list (free-response) — band 1

- **Objective:** `SPI.MIDDLE.STAT.AVG.MODE_LIST.01`
- **Answer type:** integer
- **Seed:** 8
- **Prompt:** Write down the mode of the data.
- **Canonical answer:** `6`

<details><summary>figure (semantic HTML table)</summary>

<table class="cx-list">
<caption>Test scores</caption>
<tbody><tr>
<td>8</td>
<td>6</td>
<td>6</td>
<td>9</td>
<td>6</td>
</tr></tbody></table>

</details>

**Worked solution:**
  1. Count how many times each value occurs: Tally the values.
  2. Identify the most common value: 6

- **Accessibility (spoken):** A list of values titled Test scores.
- **Difficulty axes:** {'numericalComplexity': 0.15, 'readingDemand': 0.2, 'interpretationDemand': 0.2, 'reasoningSteps': 0.2, 'informationDensity': 0, 'scaffolding': 0.5}
- **Reproduce:** `python -c "import sys;sys.path.insert(0,'oracle/spi_oracle');import data_handling as d;print(d.serialize(d.generate(8,{"interactionType": "free-response", "task": "mode_from_list"})))"`

---

## 23. read_bar_chart (free-response) — band 2

- **Objective:** `SPI.MIDDLE.STAT.READ.BAR_CHART.01`
- **Answer type:** integer
- **Seed:** 1
- **Prompt:** How many students are in the category “Fish”?
- **Canonical answer:** `10`

<details><summary>figure (canonical SVG)</summary>

```svg
<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1000 700" role="img" aria-label="Vertical bar chart: Favourite pet.">
<title>Favourite pet</title>
<desc>A bar chart titled Favourite pet. Read the frequency for the named category from the labelled axis.</desc>
<style>.cx-axis{stroke:#111;stroke-width:3;fill:none}.cx-tick{stroke:#111;stroke-width:2}.cx-tick-minor{stroke:#111;stroke-width:1.5}.cx-grid-major{stroke:#888;stroke-width:1.25;fill:none}.cx-grid-minor{stroke:#bbb;stroke-width:0.75;fill:none}.cx-bar{fill:#bbb;stroke:#111;stroke-width:2}.cx-line{stroke:#111;stroke-width:3;fill:none}.cx-pt-outline{fill:#fff;stroke:#111;stroke-width:4}.cx-pt-core{fill:#111}.cx-symbol{fill:#555;stroke:#111;stroke-width:1.5}text{font-family:sans-serif;font-size:24px;fill:#111}.cx-ticklbl{font-size:20px;fill:#333}.cx-catlbl{font-size:20px;fill:#111}.cx-axislbl{font-size:22px;fill:#111}.cx-keylbl{font-size:20px;fill:#111}</style>
<line class="cx-axis" x1="120" y1="70" x2="120" y2="590"/>
<line class="cx-axis" x1="120" y1="590" x2="950" y2="590"/>
<line class="cx-tick" x1="114" y1="590" x2="120" y2="590"/>
<text class="cx-ticklbl" x="108" y="597" text-anchor="end">0</text>
<line class="cx-grid-major" x1="120" y1="516" x2="950" y2="516"/>
<line class="cx-tick" x1="114" y1="516" x2="120" y2="516"/>
<text class="cx-ticklbl" x="108" y="523" text-anchor="end">5</text>
<line class="cx-grid-major" x1="120" y1="441" x2="950" y2="441"/>
<line class="cx-tick" x1="114" y1="441" x2="120" y2="441"/>
<text class="cx-ticklbl" x="108" y="448" text-anchor="end">10</text>
<line class="cx-grid-major" x1="1
```

</details>

**Worked solution:**
  1. Locate the bar for the named category: the bar for “Fish”
  2. Read its height using the vertical-axis scale: 10

- **Accessibility (spoken):** A bar chart titled Favourite pet. Read the frequency for the named category from the labelled axis.
- **Difficulty axes:** {'numericalComplexity': 0.7, 'readingDemand': 0.2, 'interpretationDemand': 0.15, 'reasoningSteps': 0.1, 'informationDensity': 0.333, 'scaffolding': 0.1}
- **Reproduce:** `python -c "import sys;sys.path.insert(0,'oracle/spi_oracle');import data_handling as d;print(d.serialize(d.generate(1,{"interactionType": "free-response", "task": "read_bar_chart"})))"`

---

## 24. read_bar_chart (free-response) — band 2

- **Objective:** `SPI.MIDDLE.STAT.READ.BAR_CHART.01`
- **Answer type:** integer
- **Seed:** 6
- **Prompt:** How many students are in the category “Bird”?
- **Canonical answer:** `2`

<details><summary>figure (canonical SVG)</summary>

```svg
<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1000 700" role="img" aria-label="Vertical bar chart: Favourite pet.">
<title>Favourite pet</title>
<desc>A bar chart titled Favourite pet. Read the frequency for the named category from the labelled axis.</desc>
<style>.cx-axis{stroke:#111;stroke-width:3;fill:none}.cx-tick{stroke:#111;stroke-width:2}.cx-tick-minor{stroke:#111;stroke-width:1.5}.cx-grid-major{stroke:#888;stroke-width:1.25;fill:none}.cx-grid-minor{stroke:#bbb;stroke-width:0.75;fill:none}.cx-bar{fill:#bbb;stroke:#111;stroke-width:2}.cx-line{stroke:#111;stroke-width:3;fill:none}.cx-pt-outline{fill:#fff;stroke:#111;stroke-width:4}.cx-pt-core{fill:#111}.cx-symbol{fill:#555;stroke:#111;stroke-width:1.5}text{font-family:sans-serif;font-size:24px;fill:#111}.cx-ticklbl{font-size:20px;fill:#333}.cx-catlbl{font-size:20px;fill:#111}.cx-axislbl{font-size:22px;fill:#111}.cx-keylbl{font-size:20px;fill:#111}</style>
<line class="cx-axis" x1="120" y1="70" x2="120" y2="590"/>
<line class="cx-axis" x1="120" y1="590" x2="950" y2="590"/>
<line class="cx-tick" x1="114" y1="590" x2="120" y2="590"/>
<text class="cx-ticklbl" x="108" y="597" text-anchor="end">0</text>
<line class="cx-grid-major" x1="120" y1="486" x2="950" y2="486"/>
<line class="cx-tick" x1="114" y1="486" x2="120" y2="486"/>
<text class="cx-ticklbl" x="108" y="493" text-anchor="end">2</text>
<line class="cx-grid-major" x1="120" y1="382" x2="950" y2="382"/>
<line class="cx-tick" x1="114" y1="382" x2="120" y2="382"/>
<text class="cx-ticklbl" x="108" y="389" text-anchor="end">4</text>
<line class="cx-grid-major" x1="12
```

</details>

**Worked solution:**
  1. Locate the bar for the named category: the bar for “Bird”
  2. Read its height using the vertical-axis scale: 2

- **Accessibility (spoken):** A bar chart titled Favourite pet. Read the frequency for the named category from the labelled axis.
- **Difficulty axes:** {'numericalComplexity': 0.2, 'readingDemand': 0.2, 'interpretationDemand': 0.15, 'reasoningSteps': 0.1, 'informationDensity': 0.333, 'scaffolding': 0.5}
- **Reproduce:** `python -c "import sys;sys.path.insert(0,'oracle/spi_oracle');import data_handling as d;print(d.serialize(d.generate(6,{"interactionType": "free-response", "task": "read_bar_chart"})))"`

---

## 25. read_pictogram (free-response) — band 2

- **Objective:** `SPI.MIDDLE.STAT.READ.PICTOGRAM.01`
- **Answer type:** integer
- **Seed:** 1
- **Prompt:** Use the key to find the number of students for “Fish”.
- **Canonical answer:** `10`

<details><summary>figure (canonical SVG)</summary>

```svg
<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1000 700" role="img" aria-label="Pictogram: Favourite pet.">
<title>Favourite pet</title>
<desc>A pictogram titled Favourite pet, where one symbol represents 5 students. Read the frequency for the named category.</desc>
<style>.cx-axis{stroke:#111;stroke-width:3;fill:none}.cx-tick{stroke:#111;stroke-width:2}.cx-tick-minor{stroke:#111;stroke-width:1.5}.cx-grid-major{stroke:#888;stroke-width:1.25;fill:none}.cx-grid-minor{stroke:#bbb;stroke-width:0.75;fill:none}.cx-bar{fill:#bbb;stroke:#111;stroke-width:2}.cx-line{stroke:#111;stroke-width:3;fill:none}.cx-pt-outline{fill:#fff;stroke:#111;stroke-width:4}.cx-pt-core{fill:#111}.cx-symbol{fill:#555;stroke:#111;stroke-width:1.5}text{font-family:sans-serif;font-size:24px;fill:#111}.cx-ticklbl{font-size:20px;fill:#333}.cx-catlbl{font-size:20px;fill:#111}.cx-axislbl{font-size:22px;fill:#111}.cx-keylbl{font-size:20px;fill:#111}</style>
<text class="cx-keylbl" x="120" y="48">Key: 1 symbol represents 5 students.</text>
<text class="cx-catlbl" x="80" y="114" text-anchor="start">Cat</text>
<rect class="cx-symbol" data-cat="0" x="280" y="90" width="34" height="34" rx="6"/>
<rect class="cx-symbol" data-cat="0" x="324" y="90" width="34" height="34" rx="6"/>
<rect class="cx-symbol" data-cat="0" x="368" y="90" width="34" height="34" rx="6"/>
<rect class="cx-symbol" data-cat="0" x="412" y="90" width="34" height="34" rx="6"/>
<rect class="cx-symbol" data-cat="0" x="456" y="90" width="34" height="34" rx="6"/>
<text class="cx-catlbl" x="80" y="184" text-anchor="start">Dog</text>
<rect class="cx-sy
```

</details>

**Worked solution:**
  1. Count the whole and half symbols in the named row: 2 whole symbols
  2. Apply the displayed key: 2 × 5 = 10

- **Accessibility (spoken):** A pictogram titled Favourite pet, where one symbol represents 5 students. Read the frequency for the named category.
- **Difficulty axes:** {'numericalComplexity': 0.4, 'readingDemand': 0.2, 'interpretationDemand': 0.25, 'reasoningSteps': 0.15, 'informationDensity': 0.333, 'scaffolding': 0.1}
- **Reproduce:** `python -c "import sys;sys.path.insert(0,'oracle/spi_oracle');import data_handling as d;print(d.serialize(d.generate(1,{"interactionType": "free-response", "task": "read_pictogram"})))"`

---

## 26. median_from_list (free-response) — band 2

- **Objective:** `SPI.MIDDLE.STAT.AVG.MEDIAN_LIST.01`
- **Answer type:** exact-rational
- **Seed:** 1
- **Prompt:** Find the median of the data. Give your answer as an integer or a fraction in its simplest form.
- **Canonical answer:** `31/2`

<details><summary>figure (semantic HTML table)</summary>

<table class="cx-list">
<caption>Daily steps</caption>
<tbody><tr>
<td>11</td>
<td>20</td>
<td>20</td>
<td>6</td>
</tr></tbody></table>

</details>

**Worked solution:**
  1. Order the values: 6, 11, 20, 20
  2. Identify the two middle values: 11 and 20
  3. Average the two middle values: (11 + 20) ÷ 2 = 31/2

- **Accessibility (spoken):** A list of values titled Daily steps.
- **Difficulty axes:** {'numericalComplexity': 0.55, 'readingDemand': 0.2, 'interpretationDemand': 0.3, 'reasoningSteps': 0.35, 'informationDensity': 0.333, 'scaffolding': 0.5}
- **Reproduce:** `python -c "import sys;sys.path.insert(0,'oracle/spi_oracle');import data_handling as d;print(d.serialize(d.generate(1,{"interactionType": "free-response", "task": "median_from_list"})))"`

---

## 27. single_event_probability (free-response) — band 2

- **Objective:** `SPI.MIDDLE.STAT.PROB.SINGLE_EVENT.01`
- **Answer type:** fraction
- **Seed:** 22
- **Prompt:** One bead is chosen at random from a box of beads containing the beads shown (each bead is equally likely). What is the probability that the bead chosen is Red? Give your answer as a fraction in its simplest form.
- **Canonical answer:** `1/2`

<details><summary>figure (semantic HTML table)</summary>

<table class="cx-table">
<caption>Contents of a box of beads</caption>
<thead><tr><th scope="col">Type</th><th scope="col">How many</th></tr></thead>
<tbody>
<tr><th scope="row">Red</th><td>2</td></tr>
<tr><th scope="row">Blue</th><td>2</td></tr>
<tr class="cx-total"><th scope="row">Total</th><td>4</td></tr>
</tbody></table>

</details>

**Worked solution:**
  1. Count favourable and total outcomes: 2 favourable out of 4
  2. Write as a fraction in simplest form: 1/2

**Common-error notes:**
  - MISC.STAT.PROB_UNREDUCED: Writes a correct but unsimplified fraction. → _Your value is equivalent, but simplify the fraction to its simplest form._

- **Accessibility (spoken):** A frequency table titled Contents of a box of beads.
- **Difficulty axes:** {'numericalComplexity': 0.35, 'readingDemand': 0.25, 'interpretationDemand': 0.4, 'reasoningSteps': 0.35, 'informationDensity': 0, 'scaffolding': 0.5}
- **Reproduce:** `python -c "import sys;sys.path.insert(0,'oracle/spi_oracle');import data_handling as d;print(d.serialize(d.generate(22,{"interactionType": "free-response", "task": "single_event_probability"})))"`

---

## 28. single_event_probability (free-response) — band 2

- **Objective:** `SPI.MIDDLE.STAT.PROB.SINGLE_EVENT.01`
- **Answer type:** fraction
- **Seed:** 38
- **Prompt:** One card is chosen at random from a set of cards containing the cards shown (each card is equally likely). What is the probability that the card chosen is Circle? Give your answer as a fraction in its simplest form.
- **Canonical answer:** `1`

<details><summary>figure (semantic HTML table)</summary>

<table class="cx-table">
<caption>Contents of a set of cards</caption>
<thead><tr><th scope="col">Type</th><th scope="col">How many</th></tr></thead>
<tbody>
<tr><th scope="row">Star</th><td>0</td></tr>
<tr><th scope="row">Circle</th><td>6</td></tr>
<tr><th scope="row">Square</th><td>0</td></tr>
<tr><th scope="row">Triangle</th><td>0</td></tr>
<tr class="cx-total"><th scope="row">Total</th><td>6</td></tr>
</tbody></table>

</details>

**Worked solution:**
  1. Count favourable and total outcomes: 6 favourable out of 6
  2. Write as a fraction in simplest form: 1

**Common-error notes:**
  - MISC.STAT.PROB_UNREDUCED: Writes a correct but unsimplified fraction. → _Your value is equivalent, but simplify the fraction to its simplest form._

- **Accessibility (spoken):** A frequency table titled Contents of a set of cards.
- **Difficulty axes:** {'numericalComplexity': 0.375, 'readingDemand': 0.25, 'interpretationDemand': 0.4, 'reasoningSteps': 0.35, 'informationDensity': 0.667, 'scaffolding': 0.5}
- **Reproduce:** `python -c "import sys;sys.path.insert(0,'oracle/spi_oracle');import data_handling as d;print(d.serialize(d.generate(38,{"interactionType": "free-response", "task": "single_event_probability"})))"`

---
