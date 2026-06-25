# Review pack — `gen.stats.data-handling` v1.0.1

Validator v1.0.1. **33 items** (11 chart SVGs + 22 semantic tables). Coverage: 89/89 required dimensions; misconceptions shown: 35/35. All items machine-valid: **True**.

Status: **PENDING REVIEW** — gated out of normal Studio + production until owner approval.
Objectives are `approved-for-implementation`; items are machine-validated, never auto-published.

## 1. median_from_list (free-response) — band 2

- **Objective:** `SPI.MIDDLE.STAT.AVG.MEDIAN_LIST.01`
- **Answer type:** integer
- **Seed:** 1
- **Prompt:** Find the median of the data. Give your answer as an integer or a fraction in its simplest form.
- **Canonical answer:** `14`

<details><summary>figure (semantic HTML table)</summary>

<table class="cx-list">
<caption>Test scores</caption>
<tbody><tr>
<td>20</td>
<td>20</td>
<td>6</td>
<td>13</td>
<td>15</td>
<td>9</td>
</tr></tbody></table>

</details>

**Worked solution:**
  1. Order the values: 6, 9, 13, 15, 20, 20
  2. Identify the two middle values: 13 and 15
  3. Average the two middle values: (13 + 15) ÷ 2 = 14

- **Accessibility (spoken):** A list of values titled Test scores.
- **Difficulty axes:** {'numericalComplexity': 0.3, 'readingDemand': 0.2, 'interpretationDemand': 0.3, 'reasoningSteps': 0.35, 'informationDensity': 1, 'scaffolding': 0.5}
- **Reproduce:** `python -c "import sys;sys.path.insert(0,'oracle/spi_oracle');import data_handling as d;print(d.serialize(d.generate(1,{'interactionType':'free-response'})))"`

---

## 2. range_from_list (multiple-choice) — band 2

- **Objective:** `SPI.MIDDLE.STAT.AVG.RANGE_LIST.01`
- **Answer type:** integer
- **Seed:** 1
- **Prompt:** Work out the range of the data.
- **Canonical answer:** `15`

<details><summary>figure (semantic HTML table)</summary>

<table class="cx-list">
<caption>Goals scored</caption>
<tbody><tr>
<td>13</td>
<td>18</td>
<td>24</td>
<td>9</td>
</tr></tbody></table>

</details>

**Worked solution:**
  1. Identify the largest and smallest values: largest 24, smallest 9
  2. Subtract: 24 − 9 = 15

**Distractors (misconception-backed):**
  - `24` — MISC.STAT.RANGE_IS_MAX: Gives the largest value instead of the difference.
  - `33` — MISC.STAT.RANGE_ADDS: Adds the largest and smallest values instead of subtracting.
  - `9` — MISC.STAT.RANGE_IS_MIN: Gives the smallest value instead of the difference.

- **Accessibility (spoken):** A list of values titled Goals scored.
- **Difficulty axes:** {'numericalComplexity': 0.35, 'readingDemand': 0.2, 'interpretationDemand': 0.2, 'reasoningSteps': 0.2, 'informationDensity': 0, 'scaffolding': 0.1}
- **Reproduce:** `python -c "import sys;sys.path.insert(0,'oracle/spi_oracle');import data_handling as d;print(d.serialize(d.generate(1,{'interactionType':'multiple-choice'})))"`

---

## 3. range_from_list (free-response) — band 2

- **Objective:** `SPI.MIDDLE.STAT.AVG.RANGE_LIST.01`
- **Answer type:** integer
- **Seed:** 2
- **Prompt:** Work out the range of the data.
- **Canonical answer:** `23`

<details><summary>figure (semantic HTML table)</summary>

<table class="cx-list">
<caption>Ages</caption>
<tbody><tr>
<td>27</td>
<td>19</td>
<td>15</td>
<td>11</td>
<td>24</td>
<td>4</td>
</tr></tbody></table>

</details>

**Worked solution:**
  1. Identify the largest and smallest values: largest 27, smallest 4
  2. Subtract: 27 − 4 = 23

- **Accessibility (spoken):** A list of values titled Ages.
- **Difficulty axes:** {'numericalComplexity': 0.45, 'readingDemand': 0.2, 'interpretationDemand': 0.2, 'reasoningSteps': 0.2, 'informationDensity': 0.667, 'scaffolding': 0.5}
- **Reproduce:** `python -c "import sys;sys.path.insert(0,'oracle/spi_oracle');import data_handling as d;print(d.serialize(d.generate(2,{'interactionType':'free-response'})))"`

---

## 4. mode_from_list (free-response) — band 1

- **Objective:** `SPI.MIDDLE.STAT.AVG.MODE_LIST.01`
- **Answer type:** integer
- **Seed:** 3
- **Prompt:** Write down the mode of the data.
- **Canonical answer:** `5`

<details><summary>figure (semantic HTML table)</summary>

<table class="cx-list">
<caption>Goals scored</caption>
<tbody><tr>
<td>7</td>
<td>5</td>
<td>10</td>
<td>5</td>
<td>5</td>
</tr></tbody></table>

</details>

**Worked solution:**
  1. Count how many times each value occurs: Tally the values.
  2. Identify the most common value: 5

- **Accessibility (spoken):** A list of values titled Goals scored.
- **Difficulty axes:** {'numericalComplexity': 0.183, 'readingDemand': 0.2, 'interpretationDemand': 0.2, 'reasoningSteps': 0.2, 'informationDensity': 0, 'scaffolding': 0.1}
- **Reproduce:** `python -c "import sys;sys.path.insert(0,'oracle/spi_oracle');import data_handling as d;print(d.serialize(d.generate(3,{'interactionType':'free-response'})))"`

---

## 5. mean_from_list (multiple-choice) — band 3

- **Objective:** `SPI.MIDDLE.STAT.AVG.MEAN_LIST.01`
- **Answer type:** exact-rational
- **Seed:** 3
- **Prompt:** Calculate the mean of the data. Give your answer as an integer or a fraction in its simplest form.
- **Canonical answer:** `29/5`

<details><summary>figure (semantic HTML table)</summary>

<table class="cx-list">
<caption>Temperature change</caption>
<tbody><tr>
<td>-1</td>
<td>-4</td>
<td>13</td>
<td>6</td>
<td>15</td>
</tr></tbody></table>

</details>

**Worked solution:**
  1. Add the values: -1 − 4 + 13 + 6 + 15 = 29
  2. Divide by how many values: 29 ÷ 5 = 29/5

**Distractors (misconception-backed):**
  - `29` — MISC.STAT.MEAN_NO_DIVIDE: Adds the values but forgets to divide by how many there are.
  - `29/4` — MISC.STAT.MEAN_DIVIDE_WRONG_N: Divides by the wrong number of values.
  - `11/2` — MISC.STAT.MEAN_MIDRANGE: Averages only the largest and smallest values instead of all of them.

- **Accessibility (spoken):** A list of values titled Temperature change.
- **Difficulty axes:** {'numericalComplexity': 0.55, 'readingDemand': 0.2, 'interpretationDemand': 0.3, 'reasoningSteps': 0.35, 'informationDensity': 0.667, 'scaffolding': 0.5}
- **Reproduce:** `python -c "import sys;sys.path.insert(0,'oracle/spi_oracle');import data_handling as d;print(d.serialize(d.generate(3,{'interactionType':'multiple-choice'})))"`

---

## 6. single_event_probability (free-response) — band 2

- **Objective:** `SPI.MIDDLE.STAT.PROB.SINGLE_EVENT.01`
- **Answer type:** fraction
- **Seed:** 4
- **Prompt:** One counter is chosen at random from a bag of counters containing the counters shown (each counter is equally likely). What is the probability that the counter chosen is Blue? Give your answer as a fraction in its simplest form.
- **Canonical answer:** `0`

<details><summary>figure (semantic HTML table)</summary>

<table class="cx-table">
<caption>Contents of a bag of counters</caption>
<thead><tr><th scope="col">Type</th><th scope="col">How many</th></tr></thead>
<tbody>
<tr><th scope="row">Red</th><td>1</td></tr>
<tr><th scope="row">Blue</th><td>0</td></tr>
<tr class="cx-total"><th scope="row">Total</th><td>1</td></tr>
</tbody></table>

</details>

**Worked solution:**
  1. Count favourable and total outcomes: 0 favourable out of 1
  2. Write as a fraction in simplest form: 0

**Common-error notes:**
  - MISC.STAT.PROB_UNREDUCED: Writes a correct but unsimplified fraction. → _Your value is equivalent, but simplify the fraction to its simplest form._

- **Accessibility (spoken):** A frequency table titled Contents of a bag of counters.
- **Difficulty axes:** {'numericalComplexity': 0.063, 'readingDemand': 0.25, 'interpretationDemand': 0.4, 'reasoningSteps': 0.35, 'informationDensity': 0, 'scaffolding': 0.5}
- **Reproduce:** `python -c "import sys;sys.path.insert(0,'oracle/spi_oracle');import data_handling as d;print(d.serialize(d.generate(4,{'interactionType':'free-response'})))"`

---

## 7. single_event_probability (multiple-choice) — band 3

- **Objective:** `SPI.MIDDLE.STAT.PROB.SINGLE_EVENT.01`
- **Answer type:** fraction
- **Seed:** 4
- **Prompt:** One bead is chosen at random from a box of beads containing the beads shown (each bead is equally likely). What is the probability that the bead chosen is White? Give your answer as a fraction in its simplest form.
- **Canonical answer:** `5/19`

<details><summary>figure (semantic HTML table)</summary>

<table class="cx-table">
<caption>Contents of a box of beads</caption>
<thead><tr><th scope="col">Type</th><th scope="col">How many</th></tr></thead>
<tbody>
<tr><th scope="row">Red</th><td>5</td></tr>
<tr><th scope="row">Blue</th><td>3</td></tr>
<tr><th scope="row">White</th><td>5</td></tr>
<tr><th scope="row">Black</th><td>6</td></tr>
<tr class="cx-total"><th scope="row">Total</th><td>19</td></tr>
</tbody></table>

</details>

**Worked solution:**
  1. Count favourable and total outcomes: 5 favourable out of 19
  2. Write as a fraction in simplest form: 5/19

**Distractors (misconception-backed):**
  - `14/19` — MISC.STAT.PROB_COMPLEMENT: Counts the outcomes that are not wanted instead of the ones that are.
  - `5/14` — MISC.STAT.PROB_ODDS: Compares wanted outcomes to unwanted outcomes instead of to the total.
  - `4/19` — MISC.STAT.PROB_OFF_BY_ONE: Counts one too few or one too many of the wanted outcomes.

**Common-error notes:**
  - MISC.STAT.PROB_UNREDUCED: Writes a correct but unsimplified fraction. → _Your value is equivalent, but simplify the fraction to its simplest form._

- **Accessibility (spoken):** A frequency table titled Contents of a box of beads.
- **Difficulty axes:** {'numericalComplexity': 1, 'readingDemand': 0.25, 'interpretationDemand': 0.4, 'reasoningSteps': 0.35, 'informationDensity': 0.667, 'scaffolding': 0.5}
- **Reproduce:** `python -c "import sys;sys.path.insert(0,'oracle/spi_oracle');import data_handling as d;print(d.serialize(d.generate(4,{'interactionType':'multiple-choice'})))"`

---

## 8. mean_from_list (multiple-choice) — band 2

- **Objective:** `SPI.MIDDLE.STAT.AVG.MEAN_LIST.01`
- **Answer type:** integer
- **Seed:** 5
- **Prompt:** Calculate the mean of the data. Give your answer as an integer or a fraction in its simplest form.
- **Canonical answer:** `11`

<details><summary>figure (semantic HTML table)</summary>

<table class="cx-list">
<caption>Goals scored</caption>
<tbody><tr>
<td>17</td>
<td>7</td>
<td>9</td>
</tr></tbody></table>

</details>

**Worked solution:**
  1. Add the values: 17 + 7 + 9 = 33
  2. Divide by how many values: 33 ÷ 3 = 11

**Distractors (misconception-backed):**
  - `33` — MISC.STAT.MEAN_NO_DIVIDE: Adds the values but forgets to divide by how many there are.
  - `33/2` — MISC.STAT.MEAN_DIVIDE_WRONG_N: Divides by the wrong number of values.
  - `12` — MISC.STAT.MEAN_MIDRANGE: Averages only the largest and smallest values instead of all of them.

- **Accessibility (spoken):** A list of values titled Goals scored.
- **Difficulty axes:** {'numericalComplexity': 0.3, 'readingDemand': 0.2, 'interpretationDemand': 0.3, 'reasoningSteps': 0.35, 'informationDensity': 0, 'scaffolding': 0.5}
- **Reproduce:** `python -c "import sys;sys.path.insert(0,'oracle/spi_oracle');import data_handling as d;print(d.serialize(d.generate(5,{'interactionType':'multiple-choice'})))"`

---

## 9. mean_from_list (free-response) — band 2

- **Objective:** `SPI.MIDDLE.STAT.AVG.MEAN_LIST.01`
- **Answer type:** integer
- **Seed:** 6
- **Prompt:** Calculate the mean of the data. Give your answer as an integer or a fraction in its simplest form.
- **Canonical answer:** `-1`

<details><summary>figure (semantic HTML table)</summary>

<table class="cx-list">
<caption>Change in value</caption>
<tbody><tr>
<td>8</td>
<td>-5</td>
<td>-6</td>
</tr></tbody></table>

</details>

**Worked solution:**
  1. Add the values: 8 − 5 − 6 = -3
  2. Divide by how many values: -3 ÷ 3 = -1

- **Accessibility (spoken):** A list of values titled Change in value.
- **Difficulty axes:** {'numericalComplexity': 0.3, 'readingDemand': 0.2, 'interpretationDemand': 0.3, 'reasoningSteps': 0.35, 'informationDensity': 0, 'scaffolding': 0.5}
- **Reproduce:** `python -c "import sys;sys.path.insert(0,'oracle/spi_oracle');import data_handling as d;print(d.serialize(d.generate(6,{'interactionType':'free-response'})))"`

---

## 10. median_from_list (multiple-choice) — band 2

- **Objective:** `SPI.MIDDLE.STAT.AVG.MEDIAN_LIST.01`
- **Answer type:** integer
- **Seed:** 6
- **Prompt:** Find the median of the data. Give your answer as an integer or a fraction in its simplest form.
- **Canonical answer:** `8`

<details><summary>figure (semantic HTML table)</summary>

<table class="cx-list">
<caption>Test scores</caption>
<tbody><tr>
<td>5</td>
<td>11</td>
<td>2</td>
<td>1</td>
<td>19</td>
<td>20</td>
</tr></tbody></table>

</details>

**Worked solution:**
  1. Order the values: 1, 2, 5, 11, 19, 20
  2. Identify the two middle values: 5 and 11
  3. Average the two middle values: (5 + 11) ÷ 2 = 8

**Distractors (misconception-backed):**
  - `3/2` — MISC.STAT.MEDIAN_NO_ORDER: Takes the middle value without putting the list in order first.
  - `5` — MISC.STAT.MEDIAN_WRONG_MIDDLE: Picks one of the two middle values instead of their average.
  - `29/3` — MISC.STAT.MEDIAN_USES_MEAN: Adds the values and divides instead of finding the middle value.

- **Accessibility (spoken):** A list of values titled Test scores.
- **Difficulty axes:** {'numericalComplexity': 0.3, 'readingDemand': 0.2, 'interpretationDemand': 0.3, 'reasoningSteps': 0.35, 'informationDensity': 1, 'scaffolding': 0.5}
- **Reproduce:** `python -c "import sys;sys.path.insert(0,'oracle/spi_oracle');import data_handling as d;print(d.serialize(d.generate(6,{'interactionType':'multiple-choice'})))"`

---

## 11. read_bar_chart (free-response) — band 1

- **Objective:** `SPI.MIDDLE.STAT.READ.BAR_CHART.01`
- **Answer type:** integer
- **Seed:** 7
- **Prompt:** How many readers are in the category “Science”?
- **Canonical answer:** `2`

<details><summary>figure (canonical SVG)</summary>

```svg
<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1000 700" role="img" aria-label="Vertical bar chart: Books read.">
<title>Books read</title>
<desc>A bar chart titled Books read. Read the frequency for the named category from the labelled axis.</desc>
<style>.cx-axis{stroke:#111;stroke-width:3;fill:none}.cx-tick{stroke:#111;stroke-width:2}.cx-grid-major{stroke:#888;stroke-width:1.25;fill:none}.cx-bar{fill:#bbb;stroke:#111;stroke-width:2}.cx-line{stroke:#111;stroke-width:3;fill:none}.cx-pt-outline{fill:#fff;stroke:#111;stroke-width:4}.cx-pt-core{fill:#111}.cx-symbol{fill:#555;stroke:#111;stroke-width:1.5}text{font-family:sans-serif;font-size:24px;fill:#111}.cx-ticklbl{font-size:20px;fill:#333}.cx-catlbl{font-size:20px;fill:#111}.cx-axislbl{font-size:22px;fill:#111}.cx-keylbl{font-size:20px;fill:#111}</style>
<line class="cx-axis" x1="120" y1="70" x2="120" y2="590"/>
<line class="cx-axis" x1="120" y1="590" x2="950" y2="590"/>
<line class="cx-tick" x1="114" y1="590" x2="120" y2="590"/>
<text class="cx-ticklbl" x="108" y="597" text-anchor="end">0</text>
<line class="cx-grid-major" x1="120" y1="486" x2="950" y2="486"/>
<line class="cx-tick" x1="114" y1="486" x2="120" y2="486"/>
<text class="cx-ticklbl" x="108" y="493" text-anchor="end">1</text>
<line class="cx-grid-major" x1="120" y1="382" x2="950" y2="382"/>
<line class="cx-tick" x1="114" y1="382" x2="120" y2="382"/>
<text class="cx-ticklbl" x="108" y="389" text-anchor="end">2</text>
<line class="cx-grid-major" x1="120" y1="278" x2="950" y2="278"/>
<line class="cx-tick" x1="114" y1="278" x2="120" y2="278"/>
<text class="cx-
```

</details>

**Worked solution:**
  1. Locate the bar for the named category: the bar for “Science”
  2. Read its height using the vertical-axis scale: 2

- **Accessibility (spoken):** A bar chart titled Books read. Read the frequency for the named category from the labelled axis.
- **Difficulty axes:** {'numericalComplexity': 0.1, 'readingDemand': 0.25, 'interpretationDemand': 0.15, 'reasoningSteps': 0.1, 'informationDensity': 0.667, 'scaffolding': 0.1}
- **Reproduce:** `python -c "import sys;sys.path.insert(0,'oracle/spi_oracle');import data_handling as d;print(d.serialize(d.generate(7,{'interactionType':'free-response'})))"`

---

## 12. read_pictogram (multiple-choice) — band 2

- **Objective:** `SPI.MIDDLE.STAT.READ.PICTOGRAM.01`
- **Answer type:** integer
- **Seed:** 7
- **Prompt:** Use the key to find the number of pupils for “Hockey”.
- **Canonical answer:** `55`

<details><summary>figure (canonical SVG)</summary>

```svg
<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1000 700" role="img" aria-label="Pictogram: Sport played.">
<title>Sport played</title>
<desc>A pictogram titled Sport played, where one symbol represents 10 pupils. Read the frequency for the named category.</desc>
<style>.cx-axis{stroke:#111;stroke-width:3;fill:none}.cx-tick{stroke:#111;stroke-width:2}.cx-grid-major{stroke:#888;stroke-width:1.25;fill:none}.cx-bar{fill:#bbb;stroke:#111;stroke-width:2}.cx-line{stroke:#111;stroke-width:3;fill:none}.cx-pt-outline{fill:#fff;stroke:#111;stroke-width:4}.cx-pt-core{fill:#111}.cx-symbol{fill:#555;stroke:#111;stroke-width:1.5}text{font-family:sans-serif;font-size:24px;fill:#111}.cx-ticklbl{font-size:20px;fill:#333}.cx-catlbl{font-size:20px;fill:#111}.cx-axislbl{font-size:22px;fill:#111}.cx-keylbl{font-size:20px;fill:#111}</style>
<text class="cx-keylbl" x="120" y="48">Key: 1 symbol represents 10 pupils.</text>
<text class="cx-catlbl" x="80" y="114" text-anchor="start">Football</text>
<rect class="cx-symbol" data-cat="0" x="280" y="90" width="34" height="34" rx="6"/>
<rect class="cx-symbol" data-cat="0" x="324" y="90" width="34" height="34" rx="6"/>
<rect class="cx-symbol" data-cat="0" data-half="1" x="368" y="90" width="17" height="34" rx="6"/>
<text class="cx-catlbl" x="80" y="184" text-anchor="start">Tennis</text>
<rect class="cx-symbol" data-cat="1" x="280" y="160" width="34" height="34" rx="6"/>
<rect class="cx-symbol" data-cat="1" x="324" y="160" width="34" height="34" rx="6"/>
<rect class="cx-symbol" data-cat="1" x="368" y="160" width="34" height="34" rx="6"/>
<rect class="
```

</details>

**Worked solution:**
  1. Count the whole and half symbols in the named row: 5 whole symbols and 1 half symbol
  2. Apply the displayed key: 5 × 10 + 5 = 55

**Distractors (misconception-backed):**
  - `50` — MISC.STAT.PICTO_IGNORES_HALF: Leaves out the value of the half symbol.
  - `60` — MISC.STAT.PICTO_HALF_AS_WHOLE: Counts the half symbol as if it were a whole symbol.
  - `35` — MISC.STAT.READ_WRONG_CATEGORY: Reads the frequency of a neighbouring category.

- **Accessibility (spoken):** A pictogram titled Sport played, where one symbol represents 10 pupils. Read the frequency for the named category.
- **Difficulty axes:** {'numericalComplexity': 0.6, 'readingDemand': 0.15, 'interpretationDemand': 0.25, 'reasoningSteps': 0.15, 'informationDensity': 0, 'scaffolding': 0.1}
- **Reproduce:** `python -c "import sys;sys.path.insert(0,'oracle/spi_oracle');import data_handling as d;print(d.serialize(d.generate(7,{'interactionType':'multiple-choice'})))"`

---

## 13. read_pictogram (free-response) — band 2

- **Objective:** `SPI.MIDDLE.STAT.READ.PICTOGRAM.01`
- **Answer type:** integer
- **Seed:** 8
- **Prompt:** Use the key to find the number of children for “Apple”.
- **Canonical answer:** `15`

<details><summary>figure (canonical SVG)</summary>

```svg
<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1000 700" role="img" aria-label="Pictogram: Favourite fruit.">
<title>Favourite fruit</title>
<desc>A pictogram titled Favourite fruit, where one symbol represents 5 children. Read the frequency for the named category.</desc>
<style>.cx-axis{stroke:#111;stroke-width:3;fill:none}.cx-tick{stroke:#111;stroke-width:2}.cx-grid-major{stroke:#888;stroke-width:1.25;fill:none}.cx-bar{fill:#bbb;stroke:#111;stroke-width:2}.cx-line{stroke:#111;stroke-width:3;fill:none}.cx-pt-outline{fill:#fff;stroke:#111;stroke-width:4}.cx-pt-core{fill:#111}.cx-symbol{fill:#555;stroke:#111;stroke-width:1.5}text{font-family:sans-serif;font-size:24px;fill:#111}.cx-ticklbl{font-size:20px;fill:#333}.cx-catlbl{font-size:20px;fill:#111}.cx-axislbl{font-size:22px;fill:#111}.cx-keylbl{font-size:20px;fill:#111}</style>
<text class="cx-keylbl" x="120" y="48">Key: 1 symbol represents 5 children.</text>
<text class="cx-catlbl" x="80" y="114" text-anchor="start">Apple</text>
<rect class="cx-symbol" data-cat="0" x="280" y="90" width="34" height="34" rx="6"/>
<rect class="cx-symbol" data-cat="0" x="324" y="90" width="34" height="34" rx="6"/>
<rect class="cx-symbol" data-cat="0" x="368" y="90" width="34" height="34" rx="6"/>
<text class="cx-catlbl" x="80" y="184" text-anchor="start">Banana</text>
<rect class="cx-symbol" data-cat="1" x="280" y="160" width="34" height="34" rx="6"/>
<rect class="cx-symbol" data-cat="1" x="324" y="160" width="34" height="34" rx="6"/>
<rect class="cx-symbol" data-cat="1" x="368" y="160" width="34" height="34" rx="6"/>
<text class="cx-cat
```

</details>

**Worked solution:**
  1. Count the whole and half symbols in the named row: 3 whole symbols
  2. Apply the displayed key: 3 × 5 = 15

- **Accessibility (spoken):** A pictogram titled Favourite fruit, where one symbol represents 5 children. Read the frequency for the named category.
- **Difficulty axes:** {'numericalComplexity': 0.4, 'readingDemand': 0.25, 'interpretationDemand': 0.25, 'reasoningSteps': 0.15, 'informationDensity': 0.667, 'scaffolding': 0.5}
- **Reproduce:** `python -c "import sys;sys.path.insert(0,'oracle/spi_oracle');import data_handling as d;print(d.serialize(d.generate(8,{'interactionType':'free-response'})))"`

---

## 14. median_from_list (multiple-choice) — band 2

- **Objective:** `SPI.MIDDLE.STAT.AVG.MEDIAN_LIST.01`
- **Answer type:** integer
- **Seed:** 8
- **Prompt:** Find the median of the data. Give your answer as an integer or a fraction in its simplest form.
- **Canonical answer:** `10`

<details><summary>figure (semantic HTML table)</summary>

<table class="cx-list">
<caption>Shoe sizes</caption>
<tbody><tr>
<td>16</td>
<td>1</td>
<td>10</td>
<td>8</td>
<td>11</td>
<td>7</td>
<td>11</td>
</tr></tbody></table>

</details>

**Worked solution:**
  1. Order the values: 1, 7, 8, 10, 11, 11, 16
  2. Identify the single middle value: 10

**Distractors (misconception-backed):**
  - `8` — MISC.STAT.MEDIAN_NO_ORDER: Takes the middle value without putting the list in order first.
  - `11` — MISC.STAT.AVG_USES_MODE: Gives the most common value instead of the one asked for.
  - `64/7` — MISC.STAT.MEDIAN_USES_MEAN: Adds the values and divides instead of finding the middle value.

- **Accessibility (spoken):** A list of values titled Shoe sizes.
- **Difficulty axes:** {'numericalComplexity': 0.3, 'readingDemand': 0.2, 'interpretationDemand': 0.3, 'reasoningSteps': 0.35, 'informationDensity': 1, 'scaffolding': 0.5}
- **Reproduce:** `python -c "import sys;sys.path.insert(0,'oracle/spi_oracle');import data_handling as d;print(d.serialize(d.generate(8,{'interactionType':'multiple-choice'})))"`

---

## 15. read_table_value (free-response) — band 2

- **Objective:** `SPI.MIDDLE.STAT.READ.TABLE_VALUE.01`
- **Answer type:** integer
- **Seed:** 9
- **Prompt:** How many readers are in the category “Mystery”?
- **Canonical answer:** `21`

<details><summary>figure (semantic HTML table)</summary>

<table class="cx-table">
<caption>Books read</caption>
<thead><tr><th scope="col">Category</th><th scope="col">Frequency</th></tr></thead>
<tbody>
<tr><th scope="row">Mystery</th><td>21</td></tr>
<tr><th scope="row">Fantasy</th><td>19</td></tr>
<tr><th scope="row">Comic</th><td>18</td></tr>
<tr class="cx-total"><th scope="row">Total</th><td>58</td></tr>
</tbody></table>

</details>

**Worked solution:**
  1. Locate the row for the named category: the row for “Mystery”
  2. Read the frequency in that row: 21

- **Accessibility (spoken):** A frequency table titled Books read.
- **Difficulty axes:** {'numericalComplexity': 0.42, 'readingDemand': 0.15, 'interpretationDemand': 0.1, 'reasoningSteps': 0.1, 'informationDensity': 0, 'scaffolding': 0.5}
- **Reproduce:** `python -c "import sys;sys.path.insert(0,'oracle/spi_oracle');import data_handling as d;print(d.serialize(d.generate(9,{'interactionType':'free-response'})))"`

---

## 16. read_line_graph (multiple-choice) — band 2

- **Objective:** `SPI.MIDDLE.STAT.READ.LINE_GRAPH.01`
- **Answer type:** integer
- **Seed:** 9
- **Prompt:** What is the value at Day 4?
- **Canonical answer:** `10`

<details><summary>figure (canonical SVG)</summary>

```svg
<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1000 700" role="img" aria-label="Line graph: Plant height.">
<title>Plant height</title>
<desc>A line graph titled Plant height with marked points at each labelled position. Read the value at the named position.</desc>
<style>.cx-axis{stroke:#111;stroke-width:3;fill:none}.cx-tick{stroke:#111;stroke-width:2}.cx-grid-major{stroke:#888;stroke-width:1.25;fill:none}.cx-bar{fill:#bbb;stroke:#111;stroke-width:2}.cx-line{stroke:#111;stroke-width:3;fill:none}.cx-pt-outline{fill:#fff;stroke:#111;stroke-width:4}.cx-pt-core{fill:#111}.cx-symbol{fill:#555;stroke:#111;stroke-width:1.5}text{font-family:sans-serif;font-size:24px;fill:#111}.cx-ticklbl{font-size:20px;fill:#333}.cx-catlbl{font-size:20px;fill:#111}.cx-axislbl{font-size:22px;fill:#111}.cx-keylbl{font-size:20px;fill:#111}</style>
<line class="cx-axis" x1="120" y1="70" x2="120" y2="590"/>
<line class="cx-axis" x1="120" y1="590" x2="950" y2="590"/>
<line class="cx-tick" x1="114" y1="590" x2="120" y2="590"/>
<text class="cx-ticklbl" x="108" y="597" text-anchor="end">0</text>
<line class="cx-grid-major" x1="120" y1="460" x2="950" y2="460"/>
<line class="cx-tick" x1="114" y1="460" x2="120" y2="460"/>
<text class="cx-ticklbl" x="108" y="467" text-anchor="end">5</text>
<line class="cx-grid-major" x1="120" y1="330" x2="950" y2="330"/>
<line class="cx-tick" x1="114" y1="330" x2="120" y2="330"/>
<text class="cx-ticklbl" x="108" y="337" text-anchor="end">10</text>
<line class="cx-grid-major" x1="120" y1="200" x2="950" y2="200"/>
<line class="cx-tick" x1="114" y1="200" x2="120" y2="200"/>
```

</details>

**Worked solution:**
  1. Locate the requested position on the horizontal axis: Day 4
  2. Read the value of the marked point from the vertical axis: 10

**Distractors (misconception-backed):**
  - `15` — MISC.STAT.READ_OFF_BY_STEP: Reads the value one step up or down the scale.
  - `4` — MISC.STAT.LINE_SWAPS_AXES: Reads the value off the horizontal axis instead of the vertical axis.
  - `2` — MISC.STAT.READ_MISCOUNT_SCALE: Counts the squares instead of using the scale on the axis.

- **Accessibility (spoken):** A line graph titled Plant height with marked points at each labelled position. Read the value at the named position.
- **Difficulty axes:** {'numericalComplexity': 0.34, 'readingDemand': 0.3, 'interpretationDemand': 0.2, 'reasoningSteps': 0.1, 'informationDensity': 0.333, 'scaffolding': 0.5}
- **Reproduce:** `python -c "import sys;sys.path.insert(0,'oracle/spi_oracle');import data_handling as d;print(d.serialize(d.generate(9,{'interactionType':'multiple-choice'})))"`

---

## 17. median_from_list (multiple-choice) — band 2

- **Objective:** `SPI.MIDDLE.STAT.AVG.MEDIAN_LIST.01`
- **Answer type:** integer
- **Seed:** 10
- **Prompt:** Find the median of the data. Give your answer as an integer or a fraction in its simplest form.
- **Canonical answer:** `7`

<details><summary>figure (semantic HTML table)</summary>

<table class="cx-list">
<caption>Data values</caption>
<tbody><tr>
<td>17</td>
<td>10</td>
<td>9</td>
<td>5</td>
<td>2</td>
<td>1</td>
</tr></tbody></table>

</details>

**Worked solution:**
  1. Order the values: 1, 2, 5, 9, 10, 17
  2. Identify the two middle values: 5 and 9
  3. Average the two middle values: (5 + 9) ÷ 2 = 7

**Distractors (misconception-backed):**
  - `5` — MISC.STAT.MEDIAN_WRONG_MIDDLE: Picks one of the two middle values instead of their average.
  - `22/3` — MISC.STAT.MEDIAN_USES_MEAN: Adds the values and divides instead of finding the middle value.
  - `9` — MISC.STAT.MEDIAN_MIDRANGE: Averages the largest and smallest values instead of finding the middle.

- **Accessibility (spoken):** A list of values titled Data values.
- **Difficulty axes:** {'numericalComplexity': 0.3, 'readingDemand': 0.2, 'interpretationDemand': 0.3, 'reasoningSteps': 0.35, 'informationDensity': 1, 'scaffolding': 0.5}
- **Reproduce:** `python -c "import sys;sys.path.insert(0,'oracle/spi_oracle');import data_handling as d;print(d.serialize(d.generate(10,{'interactionType':'multiple-choice'})))"`

---

## 18. read_line_graph (free-response) — band 2

- **Objective:** `SPI.MIDDLE.STAT.READ.LINE_GRAPH.01`
- **Answer type:** integer
- **Seed:** 12
- **Prompt:** What is the value at Mon?
- **Canonical answer:** `10`

<details><summary>figure (canonical SVG)</summary>

```svg
<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1000 700" role="img" aria-label="Line graph: Temperature.">
<title>Temperature</title>
<desc>A line graph titled Temperature with marked points at each labelled position. Read the value at the named position.</desc>
<style>.cx-axis{stroke:#111;stroke-width:3;fill:none}.cx-tick{stroke:#111;stroke-width:2}.cx-grid-major{stroke:#888;stroke-width:1.25;fill:none}.cx-bar{fill:#bbb;stroke:#111;stroke-width:2}.cx-line{stroke:#111;stroke-width:3;fill:none}.cx-pt-outline{fill:#fff;stroke:#111;stroke-width:4}.cx-pt-core{fill:#111}.cx-symbol{fill:#555;stroke:#111;stroke-width:1.5}text{font-family:sans-serif;font-size:24px;fill:#111}.cx-ticklbl{font-size:20px;fill:#333}.cx-catlbl{font-size:20px;fill:#111}.cx-axislbl{font-size:22px;fill:#111}.cx-keylbl{font-size:20px;fill:#111}</style>
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
<line class="cx-grid-major" x1="120" y1="367" x2="950" y2="367"/>
<line class="cx-tick" x1="114" y1="367" x2="120" y2="367"/>
<t
```

</details>

**Worked solution:**
  1. Locate the requested position on the horizontal axis: Mon
  2. Read the value of the marked point from the vertical axis: 10

- **Accessibility (spoken):** A line graph titled Temperature with marked points at each labelled position. Read the value at the named position.
- **Difficulty axes:** {'numericalComplexity': 0.62, 'readingDemand': 0.3, 'interpretationDemand': 0.2, 'reasoningSteps': 0.1, 'informationDensity': 0.333, 'scaffolding': 0.5}
- **Reproduce:** `python -c "import sys;sys.path.insert(0,'oracle/spi_oracle');import data_handling as d;print(d.serialize(d.generate(12,{'interactionType':'free-response'})))"`

---

## 19. read_table_value (multiple-choice) — band 2

- **Objective:** `SPI.MIDDLE.STAT.READ.TABLE_VALUE.01`
- **Answer type:** integer
- **Seed:** 12
- **Prompt:** How many students are in the category “Fish”?
- **Canonical answer:** `2`

<details><summary>figure (semantic HTML table)</summary>

<table class="cx-table">
<caption>Favourite pet</caption>
<thead><tr><th scope="col">Category</th><th scope="col">Frequency</th></tr></thead>
<tbody>
<tr><th scope="row">Cat</th><td>24</td></tr>
<tr><th scope="row">Dog</th><td>5</td></tr>
<tr><th scope="row">Fish</th><td>2</td></tr>
<tr><th scope="row">Bird</th><td>18</td></tr>
<tr class="cx-total"><th scope="row">Total</th><td>49</td></tr>
</tbody></table>

</details>

**Worked solution:**
  1. Locate the row for the named category: the row for “Fish”
  2. Read the frequency in that row: 2

**Distractors (misconception-backed):**
  - `49` — MISC.STAT.TABLE_READS_TOTAL: Reads the total instead of the row that was asked for.
  - `18` — MISC.STAT.TABLE_ADJACENT_ROW: Reads the frequency from the wrong row of the table.
  - `24` — MISC.STAT.TABLE_READS_LARGEST: Reads the largest frequency in the table instead of the named category.

- **Accessibility (spoken):** A frequency table titled Favourite pet.
- **Difficulty axes:** {'numericalComplexity': 0.48, 'readingDemand': 0.2, 'interpretationDemand': 0.1, 'reasoningSteps': 0.1, 'informationDensity': 0.333, 'scaffolding': 0.5}
- **Reproduce:** `python -c "import sys;sys.path.insert(0,'oracle/spi_oracle');import data_handling as d;print(d.serialize(d.generate(12,{'interactionType':'multiple-choice'})))"`

---

## 20. complete_frequency_table (free-response) — band 2

- **Objective:** `SPI.MIDDLE.STAT.FREQ.COMPLETE_TABLE.01`
- **Answer type:** table-completion
- **Seed:** 14
- **Prompt:** Find the missing value in the frequency table.
- **Canonical answer:** `35`

<details><summary>figure (semantic HTML table)</summary>

<table class="cx-table">
<caption>Sport played</caption>
<thead><tr><th scope="col">Category</th><th scope="col">Frequency</th></tr></thead>
<tbody>
<tr><th scope="row">Football</th><td>8</td></tr>
<tr><th scope="row">Tennis</th><td>5</td></tr>
<tr><th scope="row">Hockey</th><td>9</td></tr>
<tr><th scope="row">Netball</th><td>13</td></tr>
<tr class="cx-total"><th scope="row">Total</th><td class="cx-blank"><input type="text" inputmode="numeric" aria-label="Total frequency"></td></tr>
</tbody></table>

</details>

**Worked solution:**
  1. Add every displayed frequency: 8 + 5 + 9 + 13 = 35

**Common-error notes:**
  - MISC.STAT.FREQ_TOTAL_OMITS_CATEGORY: Leaves a category out when adding up the total. → _Add every category's frequency — don't miss one out._
  - MISC.STAT.FREQ_TOTAL_COPIES_ONE: Writes one of the frequencies as the total instead of their sum. → _The total is the sum of all the frequencies, not a single one of them._

- **Accessibility (spoken):** A frequency table titled Sport played.
- **Difficulty axes:** {'numericalComplexity': 0.583, 'readingDemand': 0.3, 'interpretationDemand': 0.3, 'reasoningSteps': 0.3, 'informationDensity': 0.333, 'scaffolding': 0.5}
- **Reproduce:** `python -c "import sys;sys.path.insert(0,'oracle/spi_oracle');import data_handling as d;print(d.serialize(d.generate(14,{'interactionType':'free-response'})))"`

---

## 21. read_bar_chart (free-response) — band 2

- **Objective:** `SPI.MIDDLE.STAT.READ.BAR_CHART.01`
- **Answer type:** integer
- **Seed:** 19
- **Prompt:** How many pupils are in the category “Rugby”?
- **Canonical answer:** `9`

<details><summary>figure (canonical SVG)</summary>

```svg
<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1000 700" role="img" aria-label="Vertical bar chart: Sport played.">
<title>Sport played</title>
<desc>A bar chart titled Sport played. Read the frequency for the named category from the labelled axis.</desc>
<style>.cx-axis{stroke:#111;stroke-width:3;fill:none}.cx-tick{stroke:#111;stroke-width:2}.cx-grid-major{stroke:#888;stroke-width:1.25;fill:none}.cx-bar{fill:#bbb;stroke:#111;stroke-width:2}.cx-line{stroke:#111;stroke-width:3;fill:none}.cx-pt-outline{fill:#fff;stroke:#111;stroke-width:4}.cx-pt-core{fill:#111}.cx-symbol{fill:#555;stroke:#111;stroke-width:1.5}text{font-family:sans-serif;font-size:24px;fill:#111}.cx-ticklbl{font-size:20px;fill:#333}.cx-catlbl{font-size:20px;fill:#111}.cx-axislbl{font-size:22px;fill:#111}.cx-keylbl{font-size:20px;fill:#111}</style>
<line class="cx-axis" x1="120" y1="70" x2="120" y2="590"/>
<line class="cx-axis" x1="120" y1="590" x2="950" y2="590"/>
<line class="cx-tick" x1="114" y1="590" x2="120" y2="590"/>
<text class="cx-ticklbl" x="108" y="597" text-anchor="end">0</text>
<line class="cx-grid-major" x1="120" y1="525" x2="950" y2="525"/>
<line class="cx-tick" x1="114" y1="525" x2="120" y2="525"/>
<text class="cx-ticklbl" x="108" y="532" text-anchor="end">2</text>
<line class="cx-grid-major" x1="120" y1="460" x2="950" y2="460"/>
<line class="cx-tick" x1="114" y1="460" x2="120" y2="460"/>
<text class="cx-ticklbl" x="108" y="467" text-anchor="end">4</text>
<line class="cx-grid-major" x1="120" y1="395" x2="950" y2="395"/>
<line class="cx-tick" x1="114" y1="395" x2="120" y2="395"/>
<text clas
```

</details>

**Worked solution:**
  1. Locate the bar for the named category: the bar for “Rugby”
  2. Read its height using the vertical-axis scale: 9

- **Accessibility (spoken):** A bar chart titled Sport played. Read the frequency for the named category from the labelled axis.
- **Difficulty axes:** {'numericalComplexity': 0.32, 'readingDemand': 0.25, 'interpretationDemand': 0.15, 'reasoningSteps': 0.1, 'informationDensity': 0.667, 'scaffolding': 0.1}
- **Reproduce:** `python -c "import sys;sys.path.insert(0,'oracle/spi_oracle');import data_handling as d;print(d.serialize(d.generate(19,{'interactionType':'free-response'})))"`

---

## 22. complete_frequency_table (free-response) — band 2

- **Objective:** `SPI.MIDDLE.STAT.FREQ.COMPLETE_TABLE.01`
- **Answer type:** table-completion
- **Seed:** 21
- **Prompt:** Find the missing value in the frequency table.
- **Canonical answer:** `10`

<details><summary>figure (semantic HTML table)</summary>

<table class="cx-table">
<caption>Sport played</caption>
<thead><tr><th scope="col">Category</th><th scope="col">Frequency</th></tr></thead>
<tbody>
<tr><th scope="row">Football</th><td>8</td></tr>
<tr><th scope="row">Tennis</th><td class="cx-blank"><input type="text" inputmode="numeric" aria-label="Frequency for Tennis"></td></tr>
<tr><th scope="row">Hockey</th><td>17</td></tr>
<tr class="cx-total"><th scope="row">Total</th><td>35</td></tr>
</tbody></table>

</details>

**Worked solution:**
  1. Subtract the sum of the known frequencies from the displayed total: 35 − 25 = 10

**Common-error notes:**
  - MISC.STAT.FREQ_SUBTRACT_WRONG_WAY: Adds the known frequencies to the total instead of subtracting. → _The frequencies add up to the total, so subtract the ones you know from the total._
  - MISC.STAT.FREQ_IGNORES_TOTAL: Adds up the other frequencies but ignores the given total. → _Use the total: the missing frequency is the total minus the frequencies you already have._

- **Accessibility (spoken):** A frequency table titled Sport played.
- **Difficulty axes:** {'numericalComplexity': 0.583, 'readingDemand': 0.25, 'interpretationDemand': 0.3, 'reasoningSteps': 0.3, 'informationDensity': 0, 'scaffolding': 0.5}
- **Reproduce:** `python -c "import sys;sys.path.insert(0,'oracle/spi_oracle');import data_handling as d;print(d.serialize(d.generate(21,{'interactionType':'free-response'})))"`

---

## 23. mode_from_list (multiple-choice) — band 2

- **Objective:** `SPI.MIDDLE.STAT.AVG.MODE_LIST.01`
- **Answer type:** integer
- **Seed:** 22
- **Prompt:** Write down the mode of the data.
- **Canonical answer:** `1`

<details><summary>figure (semantic HTML table)</summary>

<table class="cx-list">
<caption>Goals scored</caption>
<tbody><tr>
<td>3</td>
<td>1</td>
<td>8</td>
<td>1</td>
<td>7</td>
<td>1</td>
</tr></tbody></table>

</details>

**Worked solution:**
  1. Count how many times each value occurs: Tally the values.
  2. Identify the most common value: 1

**Distractors (misconception-backed):**
  - `8` — MISC.STAT.MODE_USES_HIGHEST: Gives the largest value instead of the most common one.
  - `3` — MISC.STAT.MODE_USES_FREQUENCY: Gives how many times the mode occurs instead of the value itself.
  - `2` — MISC.STAT.AVG_USES_MEDIAN: Gives the middle value instead of the most common one.

- **Accessibility (spoken):** A list of values titled Goals scored.
- **Difficulty axes:** {'numericalComplexity': 0.217, 'readingDemand': 0.2, 'interpretationDemand': 0.2, 'reasoningSteps': 0.2, 'informationDensity': 0.333, 'scaffolding': 0.1}
- **Reproduce:** `python -c "import sys;sys.path.insert(0,'oracle/spi_oracle');import data_handling as d;print(d.serialize(d.generate(22,{'interactionType':'multiple-choice'})))"`

---

## 24. mean_from_freq_table (free-response) — band 4

- **Objective:** `SPI.MIDDLE.STAT.AVG.MEAN_FREQ_TABLE.01`
- **Answer type:** exact-rational
- **Seed:** 30
- **Prompt:** Calculate the mean from the frequency table. Give your answer as an integer or a fraction in its simplest form.
- **Canonical answer:** `24/13`

<details><summary>figure (semantic HTML table)</summary>

<table class="cx-table">
<caption>Daily steps</caption>
<thead><tr><th scope="col">Value</th><th scope="col">Frequency</th></tr></thead>
<tbody>
<tr><th scope="row">0</th><td>1</td></tr>
<tr><th scope="row">1</th><td>3</td></tr>
<tr><th scope="row">2</th><td>6</td></tr>
<tr><th scope="row">3</th><td>3</td></tr>
</tbody></table>

</details>

**Worked solution:**
  1. Multiply each value by its frequency and add: 0×1 + 1×3 + 2×6 + 3×3 = 24
  2. Divide by the total frequency: 24 ÷ 13 = 24/13

- **Accessibility (spoken):** A frequency table titled Daily steps.
- **Difficulty axes:** {'numericalComplexity': 0.8, 'readingDemand': 0.45, 'interpretationDemand': 0.55, 'reasoningSteps': 0.7, 'informationDensity': 0.333, 'scaffolding': 0.5}
- **Reproduce:** `python -c "import sys;sys.path.insert(0,'oracle/spi_oracle');import data_handling as d;print(d.serialize(d.generate(30,{'interactionType':'free-response'})))"`

---

## 25. mean_from_freq_table (multiple-choice) — band 4

- **Objective:** `SPI.MIDDLE.STAT.AVG.MEAN_FREQ_TABLE.01`
- **Answer type:** exact-rational
- **Seed:** 30
- **Prompt:** Calculate the mean from the frequency table. Give your answer as an integer or a fraction in its simplest form.
- **Canonical answer:** `24/13`

<details><summary>figure (semantic HTML table)</summary>

<table class="cx-table">
<caption>Daily steps</caption>
<thead><tr><th scope="col">Value</th><th scope="col">Frequency</th></tr></thead>
<tbody>
<tr><th scope="row">0</th><td>1</td></tr>
<tr><th scope="row">1</th><td>3</td></tr>
<tr><th scope="row">2</th><td>6</td></tr>
<tr><th scope="row">3</th><td>3</td></tr>
</tbody></table>

</details>

**Worked solution:**
  1. Multiply each value by its frequency and add: 0×1 + 1×3 + 2×6 + 3×3 = 24
  2. Divide by the total frequency: 24 ÷ 13 = 24/13

**Distractors (misconception-backed):**
  - `6` — MISC.STAT.MEANFT_DIVIDE_BY_CATEGORIES: Divides the total by the number of rows instead of the total frequency.
  - `3/2` — MISC.STAT.MEANFT_NO_WEIGHT: Averages the listed values without using the frequencies.
  - `2` — MISC.STAT.MEAN_DIVIDE_WRONG_N: Divides by the wrong number of values.

- **Accessibility (spoken):** A frequency table titled Daily steps.
- **Difficulty axes:** {'numericalComplexity': 0.8, 'readingDemand': 0.45, 'interpretationDemand': 0.55, 'reasoningSteps': 0.7, 'informationDensity': 0.333, 'scaffolding': 0.5}
- **Reproduce:** `python -c "import sys;sys.path.insert(0,'oracle/spi_oracle');import data_handling as d;print(d.serialize(d.generate(30,{'interactionType':'multiple-choice'})))"`

---

## 26. read_pictogram (multiple-choice) — band 2

- **Objective:** `SPI.MIDDLE.STAT.READ.PICTOGRAM.01`
- **Answer type:** integer
- **Seed:** 32
- **Prompt:** Use the key to find the number of cars for “White”.
- **Canonical answer:** `7`

<details><summary>figure (canonical SVG)</summary>

```svg
<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1000 700" role="img" aria-label="Pictogram: Colour of car.">
<title>Colour of car</title>
<desc>A pictogram titled Colour of car, where one symbol represents 2 cars. Read the frequency for the named category.</desc>
<style>.cx-axis{stroke:#111;stroke-width:3;fill:none}.cx-tick{stroke:#111;stroke-width:2}.cx-grid-major{stroke:#888;stroke-width:1.25;fill:none}.cx-bar{fill:#bbb;stroke:#111;stroke-width:2}.cx-line{stroke:#111;stroke-width:3;fill:none}.cx-pt-outline{fill:#fff;stroke:#111;stroke-width:4}.cx-pt-core{fill:#111}.cx-symbol{fill:#555;stroke:#111;stroke-width:1.5}text{font-family:sans-serif;font-size:24px;fill:#111}.cx-ticklbl{font-size:20px;fill:#333}.cx-catlbl{font-size:20px;fill:#111}.cx-axislbl{font-size:22px;fill:#111}.cx-keylbl{font-size:20px;fill:#111}</style>
<text class="cx-keylbl" x="120" y="48">Key: 1 symbol represents 2 cars.</text>
<text class="cx-catlbl" x="80" y="114" text-anchor="start">Red</text>
<rect class="cx-symbol" data-cat="0" x="280" y="90" width="34" height="34" rx="6"/>
<rect class="cx-symbol" data-cat="0" x="324" y="90" width="34" height="34" rx="6"/>
<rect class="cx-symbol" data-cat="0" data-half="1" x="368" y="90" width="17" height="34" rx="6"/>
<text class="cx-catlbl" x="80" y="184" text-anchor="start">Blue</text>
<rect class="cx-symbol" data-cat="1" x="280" y="160" width="34" height="34" rx="6"/>
<rect class="cx-symbol" data-cat="1" x="324" y="160" width="34" height="34" rx="6"/>
<text class="cx-catlbl" x="80" y="254" text-anchor="start">Black</text>
<rect class="cx-symbol" data-cat="2"
```

</details>

**Worked solution:**
  1. Count the whole and half symbols in the named row: 3 whole symbols and 1 half symbol
  2. Apply the displayed key: 3 × 2 + 1 = 7

**Distractors (misconception-backed):**
  - `6` — MISC.STAT.PICTO_IGNORES_HALF: Leaves out the value of the half symbol.
  - `8` — MISC.STAT.PICTO_HALF_AS_WHOLE: Counts the half symbol as if it were a whole symbol.
  - `5` — MISC.STAT.PICTO_OFF_BY_ONE_SYMBOL: Counts one symbol too few when reading the row.

- **Accessibility (spoken):** A pictogram titled Colour of car, where one symbol represents 2 cars. Read the frequency for the named category.
- **Difficulty axes:** {'numericalComplexity': 0.3, 'readingDemand': 0.2, 'interpretationDemand': 0.25, 'reasoningSteps': 0.15, 'informationDensity': 0.333, 'scaffolding': 0.5}
- **Reproduce:** `python -c "import sys;sys.path.insert(0,'oracle/spi_oracle');import data_handling as d;print(d.serialize(d.generate(32,{'interactionType':'multiple-choice'})))"`

---

## 27. read_bar_chart (multiple-choice) — band 1

- **Objective:** `SPI.MIDDLE.STAT.READ.BAR_CHART.01`
- **Answer type:** integer
- **Seed:** 34
- **Prompt:** How many pupils are in the category “Hockey”?
- **Canonical answer:** `12`

<details><summary>figure (canonical SVG)</summary>

```svg
<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1000 700" role="img" aria-label="Vertical bar chart: Sport played.">
<title>Sport played</title>
<desc>A bar chart titled Sport played. Read the frequency for the named category from the labelled axis.</desc>
<style>.cx-axis{stroke:#111;stroke-width:3;fill:none}.cx-tick{stroke:#111;stroke-width:2}.cx-grid-major{stroke:#888;stroke-width:1.25;fill:none}.cx-bar{fill:#bbb;stroke:#111;stroke-width:2}.cx-line{stroke:#111;stroke-width:3;fill:none}.cx-pt-outline{fill:#fff;stroke:#111;stroke-width:4}.cx-pt-core{fill:#111}.cx-symbol{fill:#555;stroke:#111;stroke-width:1.5}text{font-family:sans-serif;font-size:24px;fill:#111}.cx-ticklbl{font-size:20px;fill:#333}.cx-catlbl{font-size:20px;fill:#111}.cx-axislbl{font-size:22px;fill:#111}.cx-keylbl{font-size:20px;fill:#111}</style>
<line class="cx-axis" x1="120" y1="70" x2="120" y2="590"/>
<line class="cx-axis" x1="120" y1="590" x2="950" y2="590"/>
<line class="cx-tick" x1="114" y1="590" x2="120" y2="590"/>
<text class="cx-ticklbl" x="108" y="597" text-anchor="end">0</text>
<line class="cx-grid-major" x1="120" y1="503" x2="950" y2="503"/>
<line class="cx-tick" x1="114" y1="503" x2="120" y2="503"/>
<text class="cx-ticklbl" x="108" y="510" text-anchor="end">2</text>
<line class="cx-grid-major" x1="120" y1="417" x2="950" y2="417"/>
<line class="cx-tick" x1="114" y1="417" x2="120" y2="417"/>
<text class="cx-ticklbl" x="108" y="424" text-anchor="end">4</text>
<line class="cx-grid-major" x1="120" y1="330" x2="950" y2="330"/>
<line class="cx-tick" x1="114" y1="330" x2="120" y2="330"/>
<text clas
```

</details>

**Worked solution:**
  1. Locate the bar for the named category: the bar for “Hockey”
  2. Read its height using the vertical-axis scale: 12

**Distractors (misconception-backed):**
  - `14` — MISC.STAT.READ_OFF_BY_STEP: Reads the value one step up or down the scale.
  - `7` — MISC.STAT.READ_WRONG_CATEGORY: Reads the frequency of a neighbouring category.
  - `6` — MISC.STAT.READ_MISCOUNT_SCALE: Counts the squares instead of using the scale on the axis.

- **Accessibility (spoken):** A bar chart titled Sport played. Read the frequency for the named category from the labelled axis.
- **Difficulty axes:** {'numericalComplexity': 0.24, 'readingDemand': 0.15, 'interpretationDemand': 0.15, 'reasoningSteps': 0.1, 'informationDensity': 0, 'scaffolding': 0.5}
- **Reproduce:** `python -c "import sys;sys.path.insert(0,'oracle/spi_oracle');import data_handling as d;print(d.serialize(d.generate(34,{'interactionType':'multiple-choice'})))"`

---

## 28. read_bar_chart (free-response) — band 2

- **Objective:** `SPI.MIDDLE.STAT.READ.BAR_CHART.01`
- **Answer type:** integer
- **Seed:** 35
- **Prompt:** How many cars are in the category “Blue”?
- **Canonical answer:** `13`

<details><summary>figure (canonical SVG)</summary>

```svg
<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1000 700" role="img" aria-label="Vertical bar chart: Colour of car.">
<title>Colour of car</title>
<desc>A bar chart titled Colour of car. Read the frequency for the named category from the labelled axis.</desc>
<style>.cx-axis{stroke:#111;stroke-width:3;fill:none}.cx-tick{stroke:#111;stroke-width:2}.cx-grid-major{stroke:#888;stroke-width:1.25;fill:none}.cx-bar{fill:#bbb;stroke:#111;stroke-width:2}.cx-line{stroke:#111;stroke-width:3;fill:none}.cx-pt-outline{fill:#fff;stroke:#111;stroke-width:4}.cx-pt-core{fill:#111}.cx-symbol{fill:#555;stroke:#111;stroke-width:1.5}text{font-family:sans-serif;font-size:24px;fill:#111}.cx-ticklbl{font-size:20px;fill:#333}.cx-catlbl{font-size:20px;fill:#111}.cx-axislbl{font-size:22px;fill:#111}.cx-keylbl{font-size:20px;fill:#111}</style>
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
<line class="cx-grid-major" x1="120" y1="367" x2="950" y2="367"/>
<line class="cx-tick" x1="114" y1="367" x2="120" y2="367"/>
<text 
```

</details>

**Worked solution:**
  1. Locate the bar for the named category: the bar for “Blue”
  2. Read its height using the vertical-axis scale: 13

- **Accessibility (spoken):** A bar chart titled Colour of car. Read the frequency for the named category from the labelled axis.
- **Difficulty axes:** {'numericalComplexity': 0.62, 'readingDemand': 0.25, 'interpretationDemand': 0.15, 'reasoningSteps': 0.1, 'informationDensity': 0.667, 'scaffolding': 0.5}
- **Reproduce:** `python -c "import sys;sys.path.insert(0,'oracle/spi_oracle');import data_handling as d;print(d.serialize(d.generate(35,{'interactionType':'free-response'})))"`

---

## 29. read_bar_chart (free-response) — band 2

- **Objective:** `SPI.MIDDLE.STAT.READ.BAR_CHART.01`
- **Answer type:** integer
- **Seed:** 39
- **Prompt:** How many pupils are in the category “Football”?
- **Canonical answer:** `49`

<details><summary>figure (canonical SVG)</summary>

```svg
<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1000 700" role="img" aria-label="Vertical bar chart: Sport played.">
<title>Sport played</title>
<desc>A bar chart titled Sport played. Read the frequency for the named category from the labelled axis.</desc>
<style>.cx-axis{stroke:#111;stroke-width:3;fill:none}.cx-tick{stroke:#111;stroke-width:2}.cx-grid-major{stroke:#888;stroke-width:1.25;fill:none}.cx-bar{fill:#bbb;stroke:#111;stroke-width:2}.cx-line{stroke:#111;stroke-width:3;fill:none}.cx-pt-outline{fill:#fff;stroke:#111;stroke-width:4}.cx-pt-core{fill:#111}.cx-symbol{fill:#555;stroke:#111;stroke-width:1.5}text{font-family:sans-serif;font-size:24px;fill:#111}.cx-ticklbl{font-size:20px;fill:#333}.cx-catlbl{font-size:20px;fill:#111}.cx-axislbl{font-size:22px;fill:#111}.cx-keylbl{font-size:20px;fill:#111}</style>
<line class="cx-axis" x1="120" y1="70" x2="120" y2="590"/>
<line class="cx-axis" x1="120" y1="590" x2="950" y2="590"/>
<line class="cx-tick" x1="114" y1="590" x2="120" y2="590"/>
<text class="cx-ticklbl" x="108" y="597" text-anchor="end">0</text>
<line class="cx-grid-major" x1="120" y1="486" x2="950" y2="486"/>
<line class="cx-tick" x1="114" y1="486" x2="120" y2="486"/>
<text class="cx-ticklbl" x="108" y="493" text-anchor="end">10</text>
<line class="cx-grid-major" x1="120" y1="382" x2="950" y2="382"/>
<line class="cx-tick" x1="114" y1="382" x2="120" y2="382"/>
<text class="cx-ticklbl" x="108" y="389" text-anchor="end">20</text>
<line class="cx-grid-major" x1="120" y1="278" x2="950" y2="278"/>
<line class="cx-tick" x1="114" y1="278" x2="120" y2="278"/>
<text cl
```

</details>

**Worked solution:**
  1. Locate the bar for the named category: the bar for “Football”
  2. Read its height using the vertical-axis scale: 49

- **Accessibility (spoken):** A bar chart titled Sport played. Read the frequency for the named category from the labelled axis.
- **Difficulty axes:** {'numericalComplexity': 0.98, 'readingDemand': 0.15, 'interpretationDemand': 0.15, 'reasoningSteps': 0.1, 'informationDensity': 0, 'scaffolding': 0.5}
- **Reproduce:** `python -c "import sys;sys.path.insert(0,'oracle/spi_oracle');import data_handling as d;print(d.serialize(d.generate(39,{'interactionType':'free-response'})))"`

---

## 30. read_pictogram (multiple-choice) — band 2

- **Objective:** `SPI.MIDDLE.STAT.READ.PICTOGRAM.01`
- **Answer type:** integer
- **Seed:** 56
- **Prompt:** Use the key to find the number of cars for “Blue”.
- **Canonical answer:** `15`

<details><summary>figure (canonical SVG)</summary>

```svg
<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1000 700" role="img" aria-label="Pictogram: Colour of car.">
<title>Colour of car</title>
<desc>A pictogram titled Colour of car, where one symbol represents 5 cars. Read the frequency for the named category.</desc>
<style>.cx-axis{stroke:#111;stroke-width:3;fill:none}.cx-tick{stroke:#111;stroke-width:2}.cx-grid-major{stroke:#888;stroke-width:1.25;fill:none}.cx-bar{fill:#bbb;stroke:#111;stroke-width:2}.cx-line{stroke:#111;stroke-width:3;fill:none}.cx-pt-outline{fill:#fff;stroke:#111;stroke-width:4}.cx-pt-core{fill:#111}.cx-symbol{fill:#555;stroke:#111;stroke-width:1.5}text{font-family:sans-serif;font-size:24px;fill:#111}.cx-ticklbl{font-size:20px;fill:#333}.cx-catlbl{font-size:20px;fill:#111}.cx-axislbl{font-size:22px;fill:#111}.cx-keylbl{font-size:20px;fill:#111}</style>
<text class="cx-keylbl" x="120" y="48">Key: 1 symbol represents 5 cars.</text>
<text class="cx-catlbl" x="80" y="114" text-anchor="start">Red</text>
<rect class="cx-symbol" data-cat="0" x="280" y="90" width="34" height="34" rx="6"/>
<rect class="cx-symbol" data-cat="0" x="324" y="90" width="34" height="34" rx="6"/>
<rect class="cx-symbol" data-cat="0" x="368" y="90" width="34" height="34" rx="6"/>
<text class="cx-catlbl" x="80" y="184" text-anchor="start">Blue</text>
<rect class="cx-symbol" data-cat="1" x="280" y="160" width="34" height="34" rx="6"/>
<rect class="cx-symbol" data-cat="1" x="324" y="160" width="34" height="34" rx="6"/>
<rect class="cx-symbol" data-cat="1" x="368" y="160" width="34" height="34" rx="6"/>
<text class="cx-catlbl" x="80" y="254
```

</details>

**Worked solution:**
  1. Count the whole and half symbols in the named row: 3 whole symbols
  2. Apply the displayed key: 3 × 5 = 15

**Distractors (misconception-backed):**
  - `3` — MISC.STAT.PICTO_COUNTS_SYMBOLS: Counts the symbols without using the key.
  - `25` — MISC.STAT.READ_WRONG_CATEGORY: Reads the frequency of a neighbouring category.
  - `10` — MISC.STAT.PICTO_OFF_BY_ONE_SYMBOL: Counts one symbol too few when reading the row.

- **Accessibility (spoken):** A pictogram titled Colour of car, where one symbol represents 5 cars. Read the frequency for the named category.
- **Difficulty axes:** {'numericalComplexity': 0.4, 'readingDemand': 0.15, 'interpretationDemand': 0.25, 'reasoningSteps': 0.15, 'informationDensity': 0, 'scaffolding': 0.5}
- **Reproduce:** `python -c "import sys;sys.path.insert(0,'oracle/spi_oracle');import data_handling as d;print(d.serialize(d.generate(56,{'interactionType':'multiple-choice'})))"`

---

## 31. single_event_probability (free-response) — band 2

- **Objective:** `SPI.MIDDLE.STAT.PROB.SINGLE_EVENT.01`
- **Answer type:** fraction
- **Seed:** 104
- **Prompt:** One card is chosen at random from a set of cards containing the cards shown (each card is equally likely). What is the probability that the card chosen is Square? Give your answer as a fraction in its simplest form.
- **Canonical answer:** `1`

<details><summary>figure (semantic HTML table)</summary>

<table class="cx-table">
<caption>Contents of a set of cards</caption>
<thead><tr><th scope="col">Type</th><th scope="col">How many</th></tr></thead>
<tbody>
<tr><th scope="row">Star</th><td>0</td></tr>
<tr><th scope="row">Circle</th><td>0</td></tr>
<tr><th scope="row">Square</th><td>2</td></tr>
<tr><th scope="row">Triangle</th><td>0</td></tr>
<tr class="cx-total"><th scope="row">Total</th><td>2</td></tr>
</tbody></table>

</details>

**Worked solution:**
  1. Count favourable and total outcomes: 2 favourable out of 2
  2. Write as a fraction in simplest form: 1

**Common-error notes:**
  - MISC.STAT.PROB_UNREDUCED: Writes a correct but unsimplified fraction. → _Your value is equivalent, but simplify the fraction to its simplest form._

- **Accessibility (spoken):** A frequency table titled Contents of a set of cards.
- **Difficulty axes:** {'numericalComplexity': 0.125, 'readingDemand': 0.25, 'interpretationDemand': 0.4, 'reasoningSteps': 0.35, 'informationDensity': 0.667, 'scaffolding': 0.5}
- **Reproduce:** `python -c "import sys;sys.path.insert(0,'oracle/spi_oracle');import data_handling as d;print(d.serialize(d.generate(104,{'interactionType':'free-response'})))"`

---

## 32. range_from_list (free-response) — band 1

- **Objective:** `SPI.MIDDLE.STAT.AVG.RANGE_LIST.01`
- **Answer type:** integer
- **Seed:** 166
- **Prompt:** Work out the range of the data.
- **Canonical answer:** `0`

<details><summary>figure (semantic HTML table)</summary>

<table class="cx-list">
<caption>Numbers of pets</caption>
<tbody><tr>
<td>6</td>
<td>6</td>
<td>6</td>
</tr></tbody></table>

</details>

**Worked solution:**
  1. Identify the largest and smallest values: largest 6, smallest 6
  2. Subtract: 6 − 6 = 0

- **Accessibility (spoken):** A list of values titled Numbers of pets.
- **Difficulty axes:** {'numericalComplexity': 0.1, 'readingDemand': 0.2, 'interpretationDemand': 0.2, 'reasoningSteps': 0.2, 'informationDensity': 0, 'scaffolding': 0.5}
- **Reproduce:** `python -c "import sys;sys.path.insert(0,'oracle/spi_oracle');import data_handling as d;print(d.serialize(d.generate(166,{'interactionType':'free-response'})))"`

---

## 33. single_event_probability (free-response) — band 3

- **Objective:** `SPI.MIDDLE.STAT.PROB.SINGLE_EVENT.01`
- **Answer type:** fraction
- **Seed:** 228
- **Prompt:** One card is chosen at random from a set of cards containing the cards shown (each card is equally likely). What is the probability that the card chosen is Circle? Give your answer as a fraction in its simplest form.
- **Canonical answer:** `1/2`

<details><summary>figure (semantic HTML table)</summary>

<table class="cx-table">
<caption>Contents of a set of cards</caption>
<thead><tr><th scope="col">Type</th><th scope="col">How many</th></tr></thead>
<tbody>
<tr><th scope="row">Star</th><td>6</td></tr>
<tr><th scope="row">Circle</th><td>6</td></tr>
<tr class="cx-total"><th scope="row">Total</th><td>12</td></tr>
</tbody></table>

</details>

**Worked solution:**
  1. Count favourable and total outcomes: 6 favourable out of 12
  2. Write as a fraction in simplest form: 1/2

**Common-error notes:**
  - MISC.STAT.PROB_UNREDUCED: Writes a correct but unsimplified fraction. → _Your value is equivalent, but simplify the fraction to its simplest form._

- **Accessibility (spoken):** A frequency table titled Contents of a set of cards.
- **Difficulty axes:** {'numericalComplexity': 0.85, 'readingDemand': 0.25, 'interpretationDemand': 0.4, 'reasoningSteps': 0.35, 'informationDensity': 0, 'scaffolding': 0.5}
- **Reproduce:** `python -c "import sys;sys.path.insert(0,'oracle/spi_oracle');import data_handling as d;print(d.serialize(d.generate(228,{'interactionType':'free-response'})))"`

---
