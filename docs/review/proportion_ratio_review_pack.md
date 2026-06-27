# gen.proportion.ratio v1.0.2 — Curriculum Review Pack

> **PENDING REVIEW.** Generator **gen.proportion.ratio v1.0.2**, validator v1.0.2. Objectives are approved-for-implementation. Required coverage cells are derived from the 10,000-seed distribution report; every exemplar below carries the full per-item record and a `curriculumReviewDecision` field for your APPROVE / REVISE / REJECT per item.

## Summary

- Representative exemplars: **28** · full coverage: **True** · all machine-valid: **True** · all exemplars complete: **True**.
- Ratio-checker matrix: all-ok **True**; all 9 result codes reached **True**.
- Diagnostics **16/16** exercised (inapplicable 0, recomputation mismatches 0).
- MC policy ok **True** (best_buy MC-only; 6 FR-only tasks reject MC).

## Ratio-checker matrix

| case | expected | response | requireSimplest | expected code | actual code | ok |
|---|---|---|---|---|---|---|
| 2:3 accepts 4:6 as an equivalent (non-simplest) form | 2:3 | `4:6` | False | correct | correct | True |
| 2:3 flags 4:6 equivalent-not-simplified when simplest required | 2:3 | `4:6` | True | equivalent-not-simplified | equivalent-not-simplified | True |
| 2:3 accepts itself | 2:3 | `2:3` | True | correct | correct | True |
| 2:3 rejects 3:2 as wrong-order | 2:3 | `3:2` | True | wrong-order | wrong-order | True |
| 2:3:5 accepts 4:6:10 (three-part equivalent) | 2:3:5 | `4:6:10` | False | correct | correct | True |
| 2:3:5 flags 4:6:10 equivalent-not-simplified when simplest required | 2:3:5 | `4:6:10` | True | equivalent-not-simplified | equivalent-not-simplified | True |
| 2:3 rejects 2:5 as wrong-ratio | 2:3 | `2:5` | True | wrong-ratio | wrong-ratio | True |
| 2:3 rejects 2:3:5 as wrong-number-of-parts | 2:3 | `2:3:5` | True | wrong-number-of-parts | wrong-number-of-parts | True |
| ratio with a zero part rejected | 2:3 | `0:3` | True | zero-or-negative-part | zero-or-negative-part | True |
| ratio with a negative part rejected | 2:3 | `-2:3` | True | zero-or-negative-part | zero-or-negative-part | True |
| malformed text rejected | 2:3 | `flip it` | True | malformed-response | malformed-response | True |
| extra trailing text rejected | 2:3 | `2:3 cats` | True | unparsed-trailing-text | unparsed-trailing-text | True |
| spaces around the colon accepted | 2:3 | `2 : 3` | True | correct | correct | True |
| comma-separated rejected (unsupported-term) | 2:3 | `2,3` | True | unsupported-term | unsupported-term | True |
| unicode ratio colon rejected (unsupported-term) | 2:3 | `2∶3` | True | unsupported-term | unsupported-term | True |
| the 'to' word form rejected (unsupported-term) | 2:3 | `2 to 3` | True | unsupported-term | unsupported-term | True |

Codes reached: correct, equivalent-not-simplified, malformed-response, unparsed-trailing-text, unsupported-term, wrong-number-of-parts, wrong-order, wrong-ratio, zero-or-negative-part.

## Diagnostics exercised by task

- **best_buy**: MISC.RATIO.LOWEST_PRICE_NOT_BEST, MISC.RATIO.NO_UNIT_RATE_COMPARE
- **direct_proportion**: MISC.RATIO.ADDITIVE_NOT_MULTIPLICATIVE, MISC.RATIO.DIVIDES_NOT_MULTIPLIES_UNITARY, MISC.RATIO.INVERSE_FOR_DIRECT
- **fraction_to_ratio**: MISC.RATIO.ADDS_PARTS_WRONG, MISC.RATIO.NOT_SIMPLIFIED, MISC.RATIO.PART_AS_WHOLE, MISC.RATIO.REVERSED_ORDER
- **inverse_proportion**: MISC.RATIO.ADDITIVE_NOT_MULTIPLICATIVE, MISC.RATIO.DIRECT_FOR_INVERSE, MISC.RATIO.MULTIPLIES_NOT_DIVIDES_UNITARY
- **missing_part**: MISC.RATIO.DIVIDES_BY_ONE_PART, MISC.RATIO.MULTIPLIES_NOT_DIVIDES_UNITARY
- **ratio_to_fraction**: MISC.RATIO.FRACTION_PART_OVER_PART, MISC.RATIO.PART_AS_WHOLE, MISC.RATIO.REVERSED_ORDER
- **share_three_part**: MISC.RATIO.DIVIDES_BY_ONE_PART, MISC.RATIO.WRONG_TOTAL_PARTS
- **share_two_part**: MISC.RATIO.DIVIDES_BY_ONE_PART, MISC.RATIO.PART_AS_WHOLE, MISC.RATIO.WRONG_TOTAL_PARTS
- **simple_scale**: MISC.RATIO.ADDITIVE_NOT_MULTIPLICATIVE, MISC.RATIO.SCALE_WRONG_DIRECTION
- **simplify**: MISC.RATIO.ADDS_PARTS_WRONG, MISC.RATIO.EQUIVALENT_NOT_SIMPLIFIED, MISC.RATIO.NOT_SIMPLIFIED
- **unit_rate**: MISC.RATIO.DIVIDES_NOT_MULTIPLIES_UNITARY
- **write_from_quantities**: MISC.RATIO.NOT_SIMPLIFIED, MISC.RATIO.REVERSED_ORDER

## MC interaction policy

| task | rule | ok | detail |
|---|---|---|---|
| best_buy | mc-only | True | best_buy rejects free-response (InteractionNotSupported) |
| write_from_quantities | fr-only-rejects-mc | True | write_from_quantities rejects an explicit multiple-choice request |
| share_two_part | fr-only-rejects-mc | True | share_two_part rejects an explicit multiple-choice request |
| share_three_part | fr-only-rejects-mc | True | share_three_part rejects an explicit multiple-choice request |
| missing_part | fr-only-rejects-mc | True | missing_part rejects an explicit multiple-choice request |
| unit_rate | fr-only-rejects-mc | True | unit_rate rejects an explicit multiple-choice request |
| simple_scale | fr-only-rejects-mc | True | simple_scale rejects an explicit multiple-choice request |

## share_three_part — seed 14 — band 3 (table-completion, free-response)

| field | value |
|---|---|
| objective | SPI.MIDDLE.RATIO.SHARE_THREE_PART.01 |
| interaction / answer | free-response / table-completion |
| difficulty band | 3 (axes: {"numericalComplexity": 0.3, "exactVsApproximate": 0, "reasoningSteps": 0.6, "abstraction": 0.5}) |
| prompt | Share 30 sweets between Dana, Eli, Faye in the ratio 3:2:1. Give each share. |
| params | `{"task": "share_three_part", "title": "Sharing sweets", "labels": ["Dana", "Eli", "Faye"], "unit": "sweets", "parts": [3, 2, 1], "total": 30}` |
| canonical answer | `{"cells": [{"location": "Dana", "value": 15}, {"location": "Eli", "value": 10}, {"location": "Faye", "value": 5}]}` |
| answer display | Dana=15, Eli=10, Faye=5 |
| accepted form / checker | Table completion: each labelled share is matched by location label (order-independent) against the exact canonical integer value; the shares sum to the whole. |
| worked solution | 1. Add the parts to find the total number of parts -> 3 + 2 + 1 = 6; 2. Find the value of one part -> 30 ÷ 6 = 5; 3. Multiply to give each share -> Dana=15, Eli=10, Faye=5 |
| student alt text | A bar model for the ratio 3:2:1. Share 30 sweets between Dana, Eli, Faye in the ratio 3:2:1. Give each share. |
| answer-key alt text | Answer key. A bar model for the ratio 3:2:1. The solved quantities are shown. |
| student data table | `{"columns": ["Share", "Ratio part"], "rows": [["Dana", "3 parts"], ["Eli", "2 parts"], ["Faye", "1 part"]]}` |
| answer-key data table | `{"columns": ["Share", "Ratio part"], "rows": [["Dana", "3 parts -> 15 sweets"], ["Eli", "2 parts -> 10 sweets"], ["Faye", "1 part -> 5 sweets"]]}` |
| diagnostics exercised | MISC.RATIO.WRONG_TOTAL_PARTS |
| validation checks | 21/21 pass |
| covers cells | 10 |
| reproduction | `python -c "import sys; sys.path.insert(0,'oracle'); from spi_oracle import ratio as R; print(R.serialize(R.generate(14, {'task': 'share_three_part'})))"` |
| curriculum-review decision | ☐ APPROVE ☐ REVISE ☐ REJECT |

<details><summary>student figure (SVG)</summary>

```xml
<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1000 300" role="img" aria-label="A bar model for the ratio 3:2:1. Share 30 sweets between Dana, Eli, Faye in the ratio 3:2:1. Give each share.">
<title>Bar model</title><desc>A bar model for the ratio 3:2:1. Unknown quantities are marked with a question mark. Share 30 sweets between Dana, Eli, Faye in the ratio 3:2:1. Give each share.</desc>
<style>.rt-bar-given{fill:#dddddd;stroke:#111;stroke-width:2}.rt-bar-unknown{fill:#ffffff;stroke:#111;stroke-width:2;stroke-dasharray:6 4}.rt-bar-frame{fill:none;stroke:#111;stroke-width:2.5}.rt-divider{stroke:#111;stroke-width:1.5}.rt-axis{stroke:#111;stroke-width:2.5;fill:none}.rt-tick{stroke:#111;stroke-width:2}.rt-given-pt{fill:#111;stroke:#111;stroke-width:2}.rt-unknown-pt{fill:#ffffff;stroke:#111;stroke-width:2.5;stroke-dasharray:4 3}.rt-rung{stroke:#111;stroke-width:1.5;stroke-dasharray:3 4}.rt-table-line{stroke:#111;stroke-width:2;fill:none}.rt-table-given{fill:#dddddd;stroke:#111;stroke-width:1.5}text{font-family:sans-serif;font-size:26px;fill:#111}.rt-ticklbl{font-size:20px;fill:#333}.rt-lbl{font-size:26px;fill:#111}.rt-unknown-lbl{font-size:28px;font-weight:bold;fill:#111}</style>
<g class="rt-base">
<text class="rt-lbl" x="500" y="56" text-anchor="middle">Bar model: 30 sweets shared in 3:2:1</text>
<rect class="rt-bar-unknown" data-cell="0" x="80" y="110" width="420" height="90"/>
<text class="rt-lbl" x="290" y="236" text-anchor="middle">Dana (3 parts)</text>
<rect class="rt-bar-unknown" data-cell="1" x="500" y="110" width="280" height="90"/>
<text class="rt-lbl" x="640" y="236" text-anchor="middle">Eli (2 parts)</text>
<rect class="rt-bar-unknown" data-cell="2" x="780" y="110" width="140" height="90"/>
<text class="rt-lbl" x="850" y="236" text-anchor="middle">Faye (1 part)</text>
<rect class="rt-bar-frame" x="80" y="110" width="840" height="90"/>
</g>
<g class="rt-student">
<text class="rt-unknown-lbl" x="290" y="172" text-anchor="middle">?</text>
<text class="rt-unknown-lbl" x="640" y="172" text-anchor="middle">?</text>
<text class="rt-unknown-lbl" x="850" y="172" text-anchor="middle">?</text>
</g>
</svg>
```

</details>
<details><summary>answer-key figure (SVG)</summary>

```xml
<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1000 300" role="img" aria-label="Answer key. A bar model for the ratio 3:2:1. The solved quantities are shown.">
<title>Bar model</title><desc>A bar model for the ratio 3:2:1. The solution overlay reveals the answer to: Share 30 sweets between Dana, Eli, Faye in the ratio 3:2:1. Give each share.</desc>
<style>.rt-bar-given{fill:#dddddd;stroke:#111;stroke-width:2}.rt-bar-unknown{fill:#ffffff;stroke:#111;stroke-width:2;stroke-dasharray:6 4}.rt-bar-frame{fill:none;stroke:#111;stroke-width:2.5}.rt-divider{stroke:#111;stroke-width:1.5}.rt-axis{stroke:#111;stroke-width:2.5;fill:none}.rt-tick{stroke:#111;stroke-width:2}.rt-given-pt{fill:#111;stroke:#111;stroke-width:2}.rt-unknown-pt{fill:#ffffff;stroke:#111;stroke-width:2.5;stroke-dasharray:4 3}.rt-rung{stroke:#111;stroke-width:1.5;stroke-dasharray:3 4}.rt-table-line{stroke:#111;stroke-width:2;fill:none}.rt-table-given{fill:#dddddd;stroke:#111;stroke-width:1.5}text{font-family:sans-serif;font-size:26px;fill:#111}.rt-ticklbl{font-size:20px;fill:#333}.rt-lbl{font-size:26px;fill:#111}.rt-unknown-lbl{font-size:28px;font-weight:bold;fill:#111}</style>
<g class="rt-base">
<text class="rt-lbl" x="500" y="56" text-anchor="middle">Bar model: 30 sweets shared in 3:2:1</text>
<rect class="rt-bar-unknown" data-cell="0" x="80" y="110" width="420" height="90"/>
<text class="rt-lbl" x="290" y="236" text-anchor="middle">Dana (3 parts)</text>
<rect class="rt-bar-unknown" data-cell="1" x="500" y="110" width="280" height="90"/>
<text class="rt-lbl" x="640" y="236" text-anchor="middle">Eli (2 parts)</text>
<rect class="rt-bar-unknown" data-cell="2" x="780" y="110" width="140" height="90"/>
<text class="rt-lbl" x="850" y="236" text-anchor="middle">Faye (1 part)</text>
<rect class="rt-bar-frame" x="80" y="110" width="840" height="90"/>
</g>
<g class="rt-overlay">
<text class="rt-unknown-lbl" x="290" y="172" text-anchor="middle">15</text>
<text class="rt-unknown-lbl" x="640" y="172" text-anchor="middle">10</text>
<text class="rt-unknown-lbl" x="850" y="172" text-anchor="middle">5</text>
</g>
</svg>
```

</details>

## write_from_quantities — seed 23 — band 1 (ratio, free-response)

| field | value |
|---|---|
| objective | SPI.MIDDLE.RATIO.WRITE_FROM_QUANTITIES.01 |
| interaction / answer | free-response / ratio |
| difficulty band | 1 (axes: {"numericalComplexity": 0.3, "exactVsApproximate": 0, "reasoningSteps": 0.35, "abstraction": 0.3}) |
| prompt | In a paint mixture there are 6 red paint, 4 white paint. Write the ratio of red paint to white paint in its simplest form. |
| params | `{"task": "write_from_quantities", "title": "Paint mixture", "labels": ["red paint", "white paint"], "unit": "litres", "quantities": [6, 4]}` |
| canonical answer | `{"parts": [3, 2]}` |
| answer display | 3:2 |
| accepted form / checker | Ratio checker (order-sensitive): the canonical simplest-form ordered tuple is the answer; an equivalent form is judged by require_simplest (any equivalent ordered ratio accepted). Reversed order is rejected (wrong-order); a different ratio is wrong-ratio; the wrong number of parts is wrong-number-of-parts; zero/negative/malformed/extra-text/comma/unicode-colon/'to' all map to their named result codes. |
| worked solution | 1. Find the greatest common divisor of the parts -> gcd = 2; 2. Divide every part by the gcd, keeping the order -> 3:2 |
| student alt text | No figure; the data is given in the prompt. In a paint mixture there are 6 red paint, 4 white paint. Write the ratio of red paint to white paint in its simplest form. |
| student data table | `{"columns": ["Quantity", "Value"], "rows": [], "note": "no figure for this task; data is given in the prompt"}` |
| diagnostics exercised | MISC.RATIO.REVERSED_ORDER, MISC.RATIO.NOT_SIMPLIFIED |
| validation checks | 11/11 pass |
| covers cells | 6 |
| reproduction | `python -c "import sys; sys.path.insert(0,'oracle'); from spi_oracle import ratio as R; print(R.serialize(R.generate(23, {'task': 'write_from_quantities'})))"` |
| curriculum-review decision | ☐ APPROVE ☐ REVISE ☐ REJECT |

## direct_proportion — seed 1 — band 3 (integer, free-response)

| field | value |
|---|---|
| objective | SPI.MIDDLE.RATIO.DIRECT_PROPORTION.01 |
| interaction / answer | free-response / integer |
| difficulty band | 3 (axes: {"numericalComplexity": 0.3, "exactVsApproximate": 0, "reasoningSteps": 0.55, "abstraction": 0.5}) |
| prompt | 2 boxes hold 7 pencils. How many pencils are in 10 boxes? Give an exact value. |
| params | `{"task": "direct_proportion", "givenLabel": "pencils", "perLabel": "boxes", "quantity": 2, "total": 7, "target": 10}` |
| canonical answer | `{"num": 35, "den": 1}` |
| answer display | 35 |
| accepted form / checker | Exact-rational checker: the answer is the exact reduced Fraction (num/den); no float, no tolerance; integer-when-whole carries den 1. |
| worked solution | 1. Find the value of one unit -> 7 ÷ 2 = 7/2; 2. Multiply by the required quantity -> 7/2 × 10 = 35 |
| student alt text | A double number line aligning the two proportional quantities. 2 boxes hold 7 pencils. How many pencils are in 10 boxes? Give an exact value. |
| answer-key alt text | Answer key. A double number line aligning the two proportional quantities. The solved quantities are shown. |
| student data table | `{"columns": ["boxes", "pencils"], "rows": [["2", "7"], ["10", "?"]]}` |
| answer-key data table | `{"columns": ["boxes", "pencils"], "rows": [["2", "7"], ["10", "35"]]}` |
| diagnostics exercised | MISC.RATIO.ADDITIVE_NOT_MULTIPLICATIVE, MISC.RATIO.INVERSE_FOR_DIRECT, MISC.RATIO.DIVIDES_NOT_MULTIPLIES_UNITARY |
| validation checks | 22/22 pass |
| covers cells | 5 |
| reproduction | `python -c "import sys; sys.path.insert(0,'oracle'); from spi_oracle import ratio as R; print(R.serialize(R.generate(1, {'task': 'direct_proportion'})))"` |
| curriculum-review decision | ☐ APPROVE ☐ REVISE ☐ REJECT |

<details><summary>student figure (SVG)</summary>

```xml
<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1000 260" role="img" aria-label="A double number line aligning the two proportional quantities. 2 boxes hold 7 pencils. How many pencils are in 10 boxes? Give an exact value.">
<title>Double number line</title><desc>A double number line aligning the two proportional quantities. Unknown quantities are marked with a question mark. 2 boxes hold 7 pencils. How many pencils are in 10 boxes? Give an exact value.</desc>
<style>.rt-bar-given{fill:#dddddd;stroke:#111;stroke-width:2}.rt-bar-unknown{fill:#ffffff;stroke:#111;stroke-width:2;stroke-dasharray:6 4}.rt-bar-frame{fill:none;stroke:#111;stroke-width:2.5}.rt-divider{stroke:#111;stroke-width:1.5}.rt-axis{stroke:#111;stroke-width:2.5;fill:none}.rt-tick{stroke:#111;stroke-width:2}.rt-given-pt{fill:#111;stroke:#111;stroke-width:2}.rt-unknown-pt{fill:#ffffff;stroke:#111;stroke-width:2.5;stroke-dasharray:4 3}.rt-rung{stroke:#111;stroke-width:1.5;stroke-dasharray:3 4}.rt-table-line{stroke:#111;stroke-width:2;fill:none}.rt-table-given{fill:#dddddd;stroke:#111;stroke-width:1.5}text{font-family:sans-serif;font-size:26px;fill:#111}.rt-ticklbl{font-size:20px;fill:#333}.rt-lbl{font-size:26px;fill:#111}.rt-unknown-lbl{font-size:28px;font-weight:bold;fill:#111}</style>
<g class="rt-base">
<text class="rt-lbl" x="500" y="52" text-anchor="middle">Double number line</text>
<line class="rt-axis" x1="120" y1="110" x2="880" y2="110"/>
<line class="rt-axis" x1="120" y1="200" x2="880" y2="200"/>
<text class="rt-lbl" x="104" y="118" text-anchor="end">boxes</text>
<text class="rt-lbl" x="104" y="208" text-anchor="end">pencils</text>
<line class="rt-rung" x1="373" y1="110" x2="373" y2="200"/>
<circle class="rt-given-pt" cx="373" cy="110" r="6"/>
<text class="rt-ticklbl" x="373" y="96" text-anchor="middle">2</text>
<circle class="rt-given-pt" cx="373" cy="200" r="6"/>
<text class="rt-ticklbl" x="373" y="236" text-anchor="middle">7</text>
<line class="rt-rung" x1="626" y1="110" x2="626" y2="200"/>
<circle class="rt-given-pt" cx="626" cy="110" r="6"/>
<text class="rt-ticklbl" x="626" y="96" text-anchor="middle">10</text>
<circle class="rt-unknown-pt" cx="626" cy="200" r="7"/>
</g>
<g class="rt-student">
<text class="rt-unknown-lbl" x="626" y="236" text-anchor="middle">?</text>
</g>
</svg>
```

</details>
<details><summary>answer-key figure (SVG)</summary>

```xml
<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1000 260" role="img" aria-label="Answer key. A double number line aligning the two proportional quantities. The solved quantities are shown.">
<title>Double number line</title><desc>A double number line aligning the two proportional quantities. The solution overlay reveals the answer to: 2 boxes hold 7 pencils. How many pencils are in 10 boxes? Give an exact value.</desc>
<style>.rt-bar-given{fill:#dddddd;stroke:#111;stroke-width:2}.rt-bar-unknown{fill:#ffffff;stroke:#111;stroke-width:2;stroke-dasharray:6 4}.rt-bar-frame{fill:none;stroke:#111;stroke-width:2.5}.rt-divider{stroke:#111;stroke-width:1.5}.rt-axis{stroke:#111;stroke-width:2.5;fill:none}.rt-tick{stroke:#111;stroke-width:2}.rt-given-pt{fill:#111;stroke:#111;stroke-width:2}.rt-unknown-pt{fill:#ffffff;stroke:#111;stroke-width:2.5;stroke-dasharray:4 3}.rt-rung{stroke:#111;stroke-width:1.5;stroke-dasharray:3 4}.rt-table-line{stroke:#111;stroke-width:2;fill:none}.rt-table-given{fill:#dddddd;stroke:#111;stroke-width:1.5}text{font-family:sans-serif;font-size:26px;fill:#111}.rt-ticklbl{font-size:20px;fill:#333}.rt-lbl{font-size:26px;fill:#111}.rt-unknown-lbl{font-size:28px;font-weight:bold;fill:#111}</style>
<g class="rt-base">
<text class="rt-lbl" x="500" y="52" text-anchor="middle">Double number line</text>
<line class="rt-axis" x1="120" y1="110" x2="880" y2="110"/>
<line class="rt-axis" x1="120" y1="200" x2="880" y2="200"/>
<text class="rt-lbl" x="104" y="118" text-anchor="end">boxes</text>
<text class="rt-lbl" x="104" y="208" text-anchor="end">pencils</text>
<line class="rt-rung" x1="373" y1="110" x2="373" y2="200"/>
<circle class="rt-given-pt" cx="373" cy="110" r="6"/>
<text class="rt-ticklbl" x="373" y="96" text-anchor="middle">2</text>
<circle class="rt-given-pt" cx="373" cy="200" r="6"/>
<text class="rt-ticklbl" x="373" y="236" text-anchor="middle">7</text>
<line class="rt-rung" x1="626" y1="110" x2="626" y2="200"/>
<circle class="rt-given-pt" cx="626" cy="110" r="6"/>
<text class="rt-ticklbl" x="626" y="96" text-anchor="middle">10</text>
<circle class="rt-unknown-pt" cx="626" cy="200" r="7"/>
</g>
<g class="rt-overlay">
<text class="rt-unknown-lbl" x="626" y="236" text-anchor="middle">35</text>
</g>
</svg>
```

</details>

## best_buy — seed 30 — band 3 (multiple-choice, multiple-choice)

| field | value |
|---|---|
| objective | SPI.MIDDLE.RATIO.BEST_BUY.01 |
| interaction / answer | multiple-choice / multiple-choice |
| difficulty band | 3 (axes: {"numericalComplexity": 0.3, "exactVsApproximate": 0, "reasoningSteps": 0.7, "abstraction": 0.6}) |
| prompt | You can buy erasers: option A offers 8 erasers for 3 tokens; option B offers 15 erasers for 11 tokens. Which option is the best value (the lowest cost per eraser)? Choose the best option. |
| params | `{"task": "best_buy", "items": "erasers", "item": "eraser", "options": [{"label": "A", "itemCount": 8, "tokenCost": 3, "unitRate": {"num": 3, "den": 8}}, {"label": "B", "itemCount": 15, "tokenCost": 11, "unitRate": {"num": 11, "den": 15}}], "correctLabel": "A"}` |
| canonical answer | `"A"` |
| answer display | A |
| accepted form / checker | Best-buy choice checker: the selected labelled option id is the answer; the correct option is the UNIQUE strict-minimum exact unit rate. A single letter A/B/C is parsed; anything else is malformed-response and a wrong letter is wrong-choice. |
| worked solution | 1. Cost per eraser of option A -> 3 tokens ÷ 8 erasers = 3/8 tokens per eraser; 2. Cost per eraser of option B -> 11 tokens ÷ 15 erasers = 11/15 tokens per eraser; 3. Compare the cost per item and choose the strict minimum -> the lowest cost per eraser is 3/8 -> option A |
| student alt text | A comparison table of each option's item count and token cost. You can buy erasers: option A offers 8 erasers for 3 tokens; option B offers 15 erasers for 11 tokens. Which option is the best value (the lowest cost per eraser)? Choose the best option. |
| answer-key alt text | Answer key. A comparison table of each option's item count and token cost. The solved quantities are shown. |
| student data table | `{"columns": ["Option", "Erasers", "Tokens"], "rows": [["A", "8", "3"], ["B", "15", "11"]]}` |
| answer-key data table | `{"columns": ["Option", "Erasers", "Tokens", "Cost per eraser (tokens)"], "rows": [["A", "8", "3", "3/8 (best)"], ["B", "15", "11", "11/15"]]}` |
| MC options | A=8 erasers for 3 tokens ✓; B=15 erasers for 11 tokens |
| diagnostics exercised | MISC.RATIO.NO_UNIT_RATE_COMPARE |
| validation checks | 31/31 pass |
| covers cells | 5 |
| reproduction | `python -c "import sys; sys.path.insert(0,'oracle'); from spi_oracle import ratio as R; print(R.serialize(R.generate(30, {'task': 'best_buy'})))"` |
| curriculum-review decision | ☐ APPROVE ☐ REVISE ☐ REJECT |

<details><summary>student figure (SVG)</summary>

```xml
<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1000 300" role="img" aria-label="A comparison table of each option&#39;s item count and token cost. You can buy erasers: option A offers 8 erasers for 3 tokens; option B offers 15 erasers for 11 tokens. Which option is the best value (the lowest cost per eraser)? Choose the best option.">
<title>Best-buy comparison table</title><desc>A comparison table of each option&#39;s item count and token cost. Unknown quantities are marked with a question mark. You can buy erasers: option A offers 8 erasers for 3 tokens; option B offers 15 erasers for 11 tokens. Which option is the best value (the lowest cost per eraser)? Choose the best option.</desc>
<style>.rt-bar-given{fill:#dddddd;stroke:#111;stroke-width:2}.rt-bar-unknown{fill:#ffffff;stroke:#111;stroke-width:2;stroke-dasharray:6 4}.rt-bar-frame{fill:none;stroke:#111;stroke-width:2.5}.rt-divider{stroke:#111;stroke-width:1.5}.rt-axis{stroke:#111;stroke-width:2.5;fill:none}.rt-tick{stroke:#111;stroke-width:2}.rt-given-pt{fill:#111;stroke:#111;stroke-width:2}.rt-unknown-pt{fill:#ffffff;stroke:#111;stroke-width:2.5;stroke-dasharray:4 3}.rt-rung{stroke:#111;stroke-width:1.5;stroke-dasharray:3 4}.rt-table-line{stroke:#111;stroke-width:2;fill:none}.rt-table-given{fill:#dddddd;stroke:#111;stroke-width:1.5}text{font-family:sans-serif;font-size:26px;fill:#111}.rt-ticklbl{font-size:20px;fill:#333}.rt-lbl{font-size:26px;fill:#111}.rt-unknown-lbl{font-size:28px;font-weight:bold;fill:#111}</style>
<g class="rt-base">
<text class="rt-lbl" x="500" y="48" text-anchor="middle">Compare the options by cost per item</text>
<line class="rt-table-line" x1="80" y1="80" x2="920" y2="80"/>
<line class="rt-table-line" x1="80" y1="136" x2="920" y2="136"/>
<line class="rt-table-line" x1="80" y1="192" x2="920" y2="192"/>
<line class="rt-table-line" x1="80" y1="248" x2="920" y2="248"/>
<line class="rt-table-line" x1="80" y1="304" x2="920" y2="304"/>
<line class="rt-table-line" x1="80" y1="80" x2="80" y2="304"/>
<line class="rt-table-line" x1="360" y1="80" x2="360" y2="304"/>
<line class="rt-table-line" x1="640" y1="80" x2="640" y2="304"/>
<line class="rt-table-line" x1="920" y1="80" x2="920" y2="304"/>
<text class="rt-ticklbl" x="92" y="116" text-anchor="start">Option</text>
<text class="rt-ticklbl" x="92" y="172" text-anchor="start">Erasers</text>
<text class="rt-ticklbl" x="92" y="228" text-anchor="start">Tokens</text>
<text class="rt-ticklbl" x="92" y="284" text-anchor="start">Cost per eraser (tokens)</text>
<text class="rt-lbl" x="500" y="116" text-anchor="middle">A</text>
<text class="rt-lbl" x="500" y="172" text-anchor="middle">8</text>
<text class="rt-lbl" x="500" y="228" text-anchor="middle">3</text>
<text class="rt-lbl" x="780" y="116" text-anchor="middle">B</text>
<text class="rt-lbl" x="780" y="172" text-anchor="middle">15</text>
<text class="rt-lbl" x="780" y="228" text-anchor="middle">11</text>
</g>
<g class="rt-student">
<text class="rt-unknown-lbl" x="500" y="284" text-anchor="middle">?</text>
<text class="rt-unknown-lbl" x="780" y="284" text-anchor="middle">?</text>
</g>
</svg>
```

</details>
<details><summary>answer-key figure (SVG)</summary>

```xml
<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1000 300" role="img" aria-label="Answer key. A comparison table of each option&#39;s item count and token cost. The solved quantities are shown.">
<title>Best-buy comparison table</title><desc>A comparison table of each option&#39;s item count and token cost. The solution overlay reveals the answer to: You can buy erasers: option A offers 8 erasers for 3 tokens; option B offers 15 erasers for 11 tokens. Which option is the best value (the lowest cost per eraser)? Choose the best option.</desc>
<style>.rt-bar-given{fill:#dddddd;stroke:#111;stroke-width:2}.rt-bar-unknown{fill:#ffffff;stroke:#111;stroke-width:2;stroke-dasharray:6 4}.rt-bar-frame{fill:none;stroke:#111;stroke-width:2.5}.rt-divider{stroke:#111;stroke-width:1.5}.rt-axis{stroke:#111;stroke-width:2.5;fill:none}.rt-tick{stroke:#111;stroke-width:2}.rt-given-pt{fill:#111;stroke:#111;stroke-width:2}.rt-unknown-pt{fill:#ffffff;stroke:#111;stroke-width:2.5;stroke-dasharray:4 3}.rt-rung{stroke:#111;stroke-width:1.5;stroke-dasharray:3 4}.rt-table-line{stroke:#111;stroke-width:2;fill:none}.rt-table-given{fill:#dddddd;stroke:#111;stroke-width:1.5}text{font-family:sans-serif;font-size:26px;fill:#111}.rt-ticklbl{font-size:20px;fill:#333}.rt-lbl{font-size:26px;fill:#111}.rt-unknown-lbl{font-size:28px;font-weight:bold;fill:#111}</style>
<g class="rt-base">
<text class="rt-lbl" x="500" y="48" text-anchor="middle">Compare the options by cost per item</text>
<line class="rt-table-line" x1="80" y1="80" x2="920" y2="80"/>
<line class="rt-table-line" x1="80" y1="136" x2="920" y2="136"/>
<line class="rt-table-line" x1="80" y1="192" x2="920" y2="192"/>
<line class="rt-table-line" x1="80" y1="248" x2="920" y2="248"/>
<line class="rt-table-line" x1="80" y1="304" x2="920" y2="304"/>
<line class="rt-table-line" x1="80" y1="80" x2="80" y2="304"/>
<line class="rt-table-line" x1="360" y1="80" x2="360" y2="304"/>
<line class="rt-table-line" x1="640" y1="80" x2="640" y2="304"/>
<line class="rt-table-line" x1="920" y1="80" x2="920" y2="304"/>
<text class="rt-ticklbl" x="92" y="116" text-anchor="start">Option</text>
<text class="rt-ticklbl" x="92" y="172" text-anchor="start">Erasers</text>
<text class="rt-ticklbl" x="92" y="228" text-anchor="start">Tokens</text>
<text class="rt-ticklbl" x="92" y="284" text-anchor="start">Cost per eraser (tokens)</text>
<text class="rt-lbl" x="500" y="116" text-anchor="middle">A</text>
<text class="rt-lbl" x="500" y="172" text-anchor="middle">8</text>
<text class="rt-lbl" x="500" y="228" text-anchor="middle">3</text>
<text class="rt-lbl" x="780" y="116" text-anchor="middle">B</text>
<text class="rt-lbl" x="780" y="172" text-anchor="middle">15</text>
<text class="rt-lbl" x="780" y="228" text-anchor="middle">11</text>
</g>
<g class="rt-overlay">
<text class="rt-unknown-lbl" x="500" y="284" text-anchor="middle">3/8 ✓</text>
<text class="rt-unknown-lbl" x="780" y="284" text-anchor="middle">11/15</text>
</g>
</svg>
```

</details>

## ratio_to_fraction — seed 9 — band 2 (exact-rational, free-response)

| field | value |
|---|---|
| objective | SPI.MIDDLE.RATIO.RATIO_TO_FRACTION.01 |
| interaction / answer | free-response / exact-rational |
| difficulty band | 2 (axes: {"numericalComplexity": 0.55, "exactVsApproximate": 0, "reasoningSteps": 0.45, "abstraction": 0.5}) |
| prompt | The garden mixes roses and tulips in the ratio 1:6. What fraction of the whole is tulips? Give your answer as a fraction in its simplest form. |
| params | `{"task": "ratio_to_fraction", "title": "Garden", "labels": ["roses", "tulips"], "unit": "plants", "parts": [1, 6], "partIndex": 1}` |
| canonical answer | `{"num": 6, "den": 7}` |
| answer display | 6/7 |
| accepted form / checker | Exact-rational checker: the answer is the exact reduced Fraction (num/den); no float, no tolerance; integer-when-whole carries den 1. |
| worked solution | 1. Add the parts to find the total number of parts -> 1 + 6 = 7; 2. Write the named part over the total -> 6/7 = 6/7 |
| student alt text | A bar model for the ratio 1:6. The garden mixes roses and tulips in the ratio 1:6. What fraction of the whole is tulips? Give your answer as a fraction in its simplest form. |
| answer-key alt text | Answer key. A bar model for the ratio 1:6. The solved quantities are shown. |
| student data table | `{"columns": ["Part", "Size"], "rows": [["roses (1)", "1"], ["tulips (6)", "6"]]}` |
| answer-key data table | `{"columns": ["Part", "Size"], "rows": [["roses (1)", "1"], ["tulips (6)", "6"]]}` |
| diagnostics exercised | MISC.RATIO.FRACTION_PART_OVER_PART, MISC.RATIO.REVERSED_ORDER, MISC.RATIO.PART_AS_WHOLE |
| validation checks | 19/19 pass |
| covers cells | 4 |
| reproduction | `python -c "import sys; sys.path.insert(0,'oracle'); from spi_oracle import ratio as R; print(R.serialize(R.generate(9, {'task': 'ratio_to_fraction'})))"` |
| curriculum-review decision | ☐ APPROVE ☐ REVISE ☐ REJECT |

<details><summary>student figure (SVG)</summary>

```xml
<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1000 300" role="img" aria-label="A bar model for the ratio 1:6. The garden mixes roses and tulips in the ratio 1:6. What fraction of the whole is tulips? Give your answer as a fraction in its simplest form.">
<title>Bar model</title><desc>A bar model for the ratio 1:6. Unknown quantities are marked with a question mark. The garden mixes roses and tulips in the ratio 1:6. What fraction of the whole is tulips? Give your answer as a fraction in its simplest form.</desc>
<style>.rt-bar-given{fill:#dddddd;stroke:#111;stroke-width:2}.rt-bar-unknown{fill:#ffffff;stroke:#111;stroke-width:2;stroke-dasharray:6 4}.rt-bar-frame{fill:none;stroke:#111;stroke-width:2.5}.rt-divider{stroke:#111;stroke-width:1.5}.rt-axis{stroke:#111;stroke-width:2.5;fill:none}.rt-tick{stroke:#111;stroke-width:2}.rt-given-pt{fill:#111;stroke:#111;stroke-width:2}.rt-unknown-pt{fill:#ffffff;stroke:#111;stroke-width:2.5;stroke-dasharray:4 3}.rt-rung{stroke:#111;stroke-width:1.5;stroke-dasharray:3 4}.rt-table-line{stroke:#111;stroke-width:2;fill:none}.rt-table-given{fill:#dddddd;stroke:#111;stroke-width:1.5}text{font-family:sans-serif;font-size:26px;fill:#111}.rt-ticklbl{font-size:20px;fill:#333}.rt-lbl{font-size:26px;fill:#111}.rt-unknown-lbl{font-size:28px;font-weight:bold;fill:#111}</style>
<g class="rt-base">
<text class="rt-lbl" x="500" y="56" text-anchor="middle">Bar model: the whole split as 1:6</text>
<rect class="rt-bar-given" data-cell="0" x="80" y="110" width="120" height="90"/>
<text class="rt-lbl" x="140" y="236" text-anchor="middle">roses (1)</text>
<rect class="rt-bar-given" data-cell="1" x="200" y="110" width="720" height="90"/>
<text class="rt-lbl" x="560" y="236" text-anchor="middle">tulips (6)</text>
<rect class="rt-bar-frame" x="80" y="110" width="840" height="90"/>
</g>
<g class="rt-student">
<text class="rt-unknown-lbl" x="500" y="278" text-anchor="middle">Answer: ?</text>
</g>
</svg>
```

</details>
<details><summary>answer-key figure (SVG)</summary>

```xml
<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1000 300" role="img" aria-label="Answer key. A bar model for the ratio 1:6. The solved quantities are shown.">
<title>Bar model</title><desc>A bar model for the ratio 1:6. The solution overlay reveals the answer to: The garden mixes roses and tulips in the ratio 1:6. What fraction of the whole is tulips? Give your answer as a fraction in its simplest form.</desc>
<style>.rt-bar-given{fill:#dddddd;stroke:#111;stroke-width:2}.rt-bar-unknown{fill:#ffffff;stroke:#111;stroke-width:2;stroke-dasharray:6 4}.rt-bar-frame{fill:none;stroke:#111;stroke-width:2.5}.rt-divider{stroke:#111;stroke-width:1.5}.rt-axis{stroke:#111;stroke-width:2.5;fill:none}.rt-tick{stroke:#111;stroke-width:2}.rt-given-pt{fill:#111;stroke:#111;stroke-width:2}.rt-unknown-pt{fill:#ffffff;stroke:#111;stroke-width:2.5;stroke-dasharray:4 3}.rt-rung{stroke:#111;stroke-width:1.5;stroke-dasharray:3 4}.rt-table-line{stroke:#111;stroke-width:2;fill:none}.rt-table-given{fill:#dddddd;stroke:#111;stroke-width:1.5}text{font-family:sans-serif;font-size:26px;fill:#111}.rt-ticklbl{font-size:20px;fill:#333}.rt-lbl{font-size:26px;fill:#111}.rt-unknown-lbl{font-size:28px;font-weight:bold;fill:#111}</style>
<g class="rt-base">
<text class="rt-lbl" x="500" y="56" text-anchor="middle">Bar model: the whole split as 1:6</text>
<rect class="rt-bar-given" data-cell="0" x="80" y="110" width="120" height="90"/>
<text class="rt-lbl" x="140" y="236" text-anchor="middle">roses (1)</text>
<rect class="rt-bar-given" data-cell="1" x="200" y="110" width="720" height="90"/>
<text class="rt-lbl" x="560" y="236" text-anchor="middle">tulips (6)</text>
<rect class="rt-bar-frame" x="80" y="110" width="840" height="90"/>
</g>
<g class="rt-overlay">
<text class="rt-unknown-lbl" x="500" y="278" text-anchor="middle">Answer: 6/7</text>
</g>
</svg>
```

</details>

## share_two_part — seed 18 — band 2 (table-completion, free-response)

| field | value |
|---|---|
| objective | SPI.MIDDLE.RATIO.SHARE_TWO_PART.01 |
| interaction / answer | free-response / table-completion |
| difficulty band | 2 (axes: {"numericalComplexity": 0.3, "exactVsApproximate": 0, "reasoningSteps": 0.5, "abstraction": 0.4}) |
| prompt | Share 36 marbles between Gus, Hana in the ratio 3:1. Give each share. |
| params | `{"task": "share_two_part", "title": "Sharing marbles", "labels": ["Gus", "Hana"], "unit": "marbles", "parts": [3, 1], "total": 36}` |
| canonical answer | `{"cells": [{"location": "Gus", "value": 27}, {"location": "Hana", "value": 9}]}` |
| answer display | Gus=27, Hana=9 |
| accepted form / checker | Table completion: each labelled share is matched by location label (order-independent) against the exact canonical integer value; the shares sum to the whole. |
| worked solution | 1. Add the parts to find the total number of parts -> 3 + 1 = 4; 2. Find the value of one part -> 36 ÷ 4 = 9; 3. Multiply to give each share -> Gus=27, Hana=9 |
| student alt text | A bar model for the ratio 3:1. Share 36 marbles between Gus, Hana in the ratio 3:1. Give each share. |
| answer-key alt text | Answer key. A bar model for the ratio 3:1. The solved quantities are shown. |
| student data table | `{"columns": ["Share", "Ratio part"], "rows": [["Gus", "3 parts"], ["Hana", "1 part"]]}` |
| answer-key data table | `{"columns": ["Share", "Ratio part"], "rows": [["Gus", "3 parts -> 27 marbles"], ["Hana", "1 part -> 9 marbles"]]}` |
| diagnostics exercised | MISC.RATIO.WRONG_TOTAL_PARTS, MISC.RATIO.DIVIDES_BY_ONE_PART, MISC.RATIO.PART_AS_WHOLE |
| validation checks | 21/21 pass |
| covers cells | 4 |
| reproduction | `python -c "import sys; sys.path.insert(0,'oracle'); from spi_oracle import ratio as R; print(R.serialize(R.generate(18, {'task': 'share_two_part'})))"` |
| curriculum-review decision | ☐ APPROVE ☐ REVISE ☐ REJECT |

<details><summary>student figure (SVG)</summary>

```xml
<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1000 300" role="img" aria-label="A bar model for the ratio 3:1. Share 36 marbles between Gus, Hana in the ratio 3:1. Give each share.">
<title>Bar model</title><desc>A bar model for the ratio 3:1. Unknown quantities are marked with a question mark. Share 36 marbles between Gus, Hana in the ratio 3:1. Give each share.</desc>
<style>.rt-bar-given{fill:#dddddd;stroke:#111;stroke-width:2}.rt-bar-unknown{fill:#ffffff;stroke:#111;stroke-width:2;stroke-dasharray:6 4}.rt-bar-frame{fill:none;stroke:#111;stroke-width:2.5}.rt-divider{stroke:#111;stroke-width:1.5}.rt-axis{stroke:#111;stroke-width:2.5;fill:none}.rt-tick{stroke:#111;stroke-width:2}.rt-given-pt{fill:#111;stroke:#111;stroke-width:2}.rt-unknown-pt{fill:#ffffff;stroke:#111;stroke-width:2.5;stroke-dasharray:4 3}.rt-rung{stroke:#111;stroke-width:1.5;stroke-dasharray:3 4}.rt-table-line{stroke:#111;stroke-width:2;fill:none}.rt-table-given{fill:#dddddd;stroke:#111;stroke-width:1.5}text{font-family:sans-serif;font-size:26px;fill:#111}.rt-ticklbl{font-size:20px;fill:#333}.rt-lbl{font-size:26px;fill:#111}.rt-unknown-lbl{font-size:28px;font-weight:bold;fill:#111}</style>
<g class="rt-base">
<text class="rt-lbl" x="500" y="56" text-anchor="middle">Bar model: 36 marbles shared in 3:1</text>
<rect class="rt-bar-unknown" data-cell="0" x="80" y="110" width="630" height="90"/>
<text class="rt-lbl" x="395" y="236" text-anchor="middle">Gus (3 parts)</text>
<rect class="rt-bar-unknown" data-cell="1" x="710" y="110" width="210" height="90"/>
<text class="rt-lbl" x="815" y="236" text-anchor="middle">Hana (1 part)</text>
<rect class="rt-bar-frame" x="80" y="110" width="840" height="90"/>
</g>
<g class="rt-student">
<text class="rt-unknown-lbl" x="395" y="172" text-anchor="middle">?</text>
<text class="rt-unknown-lbl" x="815" y="172" text-anchor="middle">?</text>
</g>
</svg>
```

</details>
<details><summary>answer-key figure (SVG)</summary>

```xml
<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1000 300" role="img" aria-label="Answer key. A bar model for the ratio 3:1. The solved quantities are shown.">
<title>Bar model</title><desc>A bar model for the ratio 3:1. The solution overlay reveals the answer to: Share 36 marbles between Gus, Hana in the ratio 3:1. Give each share.</desc>
<style>.rt-bar-given{fill:#dddddd;stroke:#111;stroke-width:2}.rt-bar-unknown{fill:#ffffff;stroke:#111;stroke-width:2;stroke-dasharray:6 4}.rt-bar-frame{fill:none;stroke:#111;stroke-width:2.5}.rt-divider{stroke:#111;stroke-width:1.5}.rt-axis{stroke:#111;stroke-width:2.5;fill:none}.rt-tick{stroke:#111;stroke-width:2}.rt-given-pt{fill:#111;stroke:#111;stroke-width:2}.rt-unknown-pt{fill:#ffffff;stroke:#111;stroke-width:2.5;stroke-dasharray:4 3}.rt-rung{stroke:#111;stroke-width:1.5;stroke-dasharray:3 4}.rt-table-line{stroke:#111;stroke-width:2;fill:none}.rt-table-given{fill:#dddddd;stroke:#111;stroke-width:1.5}text{font-family:sans-serif;font-size:26px;fill:#111}.rt-ticklbl{font-size:20px;fill:#333}.rt-lbl{font-size:26px;fill:#111}.rt-unknown-lbl{font-size:28px;font-weight:bold;fill:#111}</style>
<g class="rt-base">
<text class="rt-lbl" x="500" y="56" text-anchor="middle">Bar model: 36 marbles shared in 3:1</text>
<rect class="rt-bar-unknown" data-cell="0" x="80" y="110" width="630" height="90"/>
<text class="rt-lbl" x="395" y="236" text-anchor="middle">Gus (3 parts)</text>
<rect class="rt-bar-unknown" data-cell="1" x="710" y="110" width="210" height="90"/>
<text class="rt-lbl" x="815" y="236" text-anchor="middle">Hana (1 part)</text>
<rect class="rt-bar-frame" x="80" y="110" width="840" height="90"/>
</g>
<g class="rt-overlay">
<text class="rt-unknown-lbl" x="395" y="172" text-anchor="middle">27</text>
<text class="rt-unknown-lbl" x="815" y="172" text-anchor="middle">9</text>
</g>
</svg>
```

</details>

## inverse_proportion — seed 2 — band 3 (integer, free-response)

| field | value |
|---|---|
| objective | SPI.MIDDLE.RATIO.INVERSE_PROPORTION.01 |
| interaction / answer | free-response / integer |
| difficulty band | 3 (axes: {"numericalComplexity": 0.3, "exactVsApproximate": 0, "reasoningSteps": 0.7, "abstraction": 0.65}) |
| prompt | 3 taps take 7 hours to fill the tank. How many hours would 21 taps take to fill the tank? |
| params | `{"task": "inverse_proportion", "agent": "taps", "unit": "hours", "tail": "to fill the tank", "q1": 3, "v1": 7, "q2": 21}` |
| canonical answer | `{"num": 1, "den": 1}` |
| answer display | 1 |
| accepted form / checker | Integer checker: the exact positive integer is the only accepted value (no tolerance). |
| worked solution | 1. Use the product invariant (more means less) -> 3 × 7 = 21; 2. Divide the product by the new quantity -> 21 ÷ 21 = 1 |
| student alt text | No figure; the data is given in the prompt. 3 taps take 7 hours to fill the tank. How many hours would 21 taps take to fill the tank? |
| student data table | `{"columns": ["Quantity", "Value"], "rows": [], "note": "no figure for this task; data is given in the prompt"}` |
| diagnostics exercised | MISC.RATIO.DIRECT_FOR_INVERSE, MISC.RATIO.MULTIPLIES_NOT_DIVIDES_UNITARY, MISC.RATIO.ADDITIVE_NOT_MULTIPLICATIVE |
| validation checks | 8/8 pass |
| covers cells | 3 |
| reproduction | `python -c "import sys; sys.path.insert(0,'oracle'); from spi_oracle import ratio as R; print(R.serialize(R.generate(2, {'task': 'inverse_proportion'})))"` |
| curriculum-review decision | ☐ APPROVE ☐ REVISE ☐ REJECT |

## simple_scale — seed 4 — band 2 (integer, free-response)

| field | value |
|---|---|
| objective | SPI.MIDDLE.RATIO.SIMPLE_SCALE.01 |
| interaction / answer | free-response / integer |
| difficulty band | 2 (axes: {"numericalComplexity": 0.3, "exactVsApproximate": 0, "reasoningSteps": 0.5, "abstraction": 0.5}) |
| prompt | On a plan, 1 plan unit represents 2 actual units. A part measures 6 plan units. How many actual units long is it in reality? Give an exact value. |
| params | `{"task": "simple_scale", "scaleKind": "plan", "srcUnit": "plan unit", "dstUnit": "actual unit", "value": 6, "factorNum": 2, "factorDen": 1, "direction": "multiply"}` |
| canonical answer | `{"num": 12, "den": 1}` |
| answer display | 12 |
| accepted form / checker | Exact-rational checker: the answer is the exact reduced Fraction (num/den); no float, no tolerance; integer-when-whole carries den 1. |
| worked solution | 1. Find the scale factor -> 2/1; 2. Multiply the value by the scale factor -> 6 × 2/1 = 12 |
| student alt text | A double number line aligning the two proportional quantities. On a plan, 1 plan unit represents 2 actual units. A part measures 6 plan units. How many actual units long is it in reality? Give an exact value. |
| answer-key alt text | Answer key. A double number line aligning the two proportional quantities. The solved quantities are shown. |
| student data table | `{"columns": ["plan unit", "actual unit"], "rows": [["1", "2"], ["6", "?"]]}` |
| answer-key data table | `{"columns": ["plan unit", "actual unit"], "rows": [["1", "2"], ["6", "12"]]}` |
| diagnostics exercised | MISC.RATIO.SCALE_WRONG_DIRECTION, MISC.RATIO.ADDITIVE_NOT_MULTIPLICATIVE |
| validation checks | 31/31 pass |
| covers cells | 3 |
| reproduction | `python -c "import sys; sys.path.insert(0,'oracle'); from spi_oracle import ratio as R; print(R.serialize(R.generate(4, {'task': 'simple_scale'})))"` |
| curriculum-review decision | ☐ APPROVE ☐ REVISE ☐ REJECT |

<details><summary>student figure (SVG)</summary>

```xml
<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1000 260" role="img" aria-label="A double number line aligning the two proportional quantities. On a plan, 1 plan unit represents 2 actual units. A part measures 6 plan units. How many actual units long is it in reality? Give an exact value.">
<title>Double number line</title><desc>A double number line aligning the two proportional quantities. Unknown quantities are marked with a question mark. On a plan, 1 plan unit represents 2 actual units. A part measures 6 plan units. How many actual units long is it in reality? Give an exact value.</desc>
<style>.rt-bar-given{fill:#dddddd;stroke:#111;stroke-width:2}.rt-bar-unknown{fill:#ffffff;stroke:#111;stroke-width:2;stroke-dasharray:6 4}.rt-bar-frame{fill:none;stroke:#111;stroke-width:2.5}.rt-divider{stroke:#111;stroke-width:1.5}.rt-axis{stroke:#111;stroke-width:2.5;fill:none}.rt-tick{stroke:#111;stroke-width:2}.rt-given-pt{fill:#111;stroke:#111;stroke-width:2}.rt-unknown-pt{fill:#ffffff;stroke:#111;stroke-width:2.5;stroke-dasharray:4 3}.rt-rung{stroke:#111;stroke-width:1.5;stroke-dasharray:3 4}.rt-table-line{stroke:#111;stroke-width:2;fill:none}.rt-table-given{fill:#dddddd;stroke:#111;stroke-width:1.5}text{font-family:sans-serif;font-size:26px;fill:#111}.rt-ticklbl{font-size:20px;fill:#333}.rt-lbl{font-size:26px;fill:#111}.rt-unknown-lbl{font-size:28px;font-weight:bold;fill:#111}</style>
<g class="rt-base">
<text class="rt-lbl" x="500" y="52" text-anchor="middle">Double number line</text>
<line class="rt-axis" x1="120" y1="110" x2="880" y2="110"/>
<line class="rt-axis" x1="120" y1="200" x2="880" y2="200"/>
<text class="rt-lbl" x="104" y="118" text-anchor="end">plan unit</text>
<text class="rt-lbl" x="104" y="208" text-anchor="end">actual unit</text>
<line class="rt-rung" x1="373" y1="110" x2="373" y2="200"/>
<circle class="rt-given-pt" cx="373" cy="110" r="6"/>
<text class="rt-ticklbl" x="373" y="96" text-anchor="middle">1</text>
<circle class="rt-given-pt" cx="373" cy="200" r="6"/>
<text class="rt-ticklbl" x="373" y="236" text-anchor="middle">2</text>
<line class="rt-rung" x1="626" y1="110" x2="626" y2="200"/>
<circle class="rt-given-pt" cx="626" cy="110" r="6"/>
<text class="rt-ticklbl" x="626" y="96" text-anchor="middle">6</text>
<circle class="rt-unknown-pt" cx="626" cy="200" r="7"/>
</g>
<g class="rt-student">
<text class="rt-unknown-lbl" x="626" y="236" text-anchor="middle">?</text>
</g>
</svg>
```

</details>
<details><summary>answer-key figure (SVG)</summary>

```xml
<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1000 260" role="img" aria-label="Answer key. A double number line aligning the two proportional quantities. The solved quantities are shown.">
<title>Double number line</title><desc>A double number line aligning the two proportional quantities. The solution overlay reveals the answer to: On a plan, 1 plan unit represents 2 actual units. A part measures 6 plan units. How many actual units long is it in reality? Give an exact value.</desc>
<style>.rt-bar-given{fill:#dddddd;stroke:#111;stroke-width:2}.rt-bar-unknown{fill:#ffffff;stroke:#111;stroke-width:2;stroke-dasharray:6 4}.rt-bar-frame{fill:none;stroke:#111;stroke-width:2.5}.rt-divider{stroke:#111;stroke-width:1.5}.rt-axis{stroke:#111;stroke-width:2.5;fill:none}.rt-tick{stroke:#111;stroke-width:2}.rt-given-pt{fill:#111;stroke:#111;stroke-width:2}.rt-unknown-pt{fill:#ffffff;stroke:#111;stroke-width:2.5;stroke-dasharray:4 3}.rt-rung{stroke:#111;stroke-width:1.5;stroke-dasharray:3 4}.rt-table-line{stroke:#111;stroke-width:2;fill:none}.rt-table-given{fill:#dddddd;stroke:#111;stroke-width:1.5}text{font-family:sans-serif;font-size:26px;fill:#111}.rt-ticklbl{font-size:20px;fill:#333}.rt-lbl{font-size:26px;fill:#111}.rt-unknown-lbl{font-size:28px;font-weight:bold;fill:#111}</style>
<g class="rt-base">
<text class="rt-lbl" x="500" y="52" text-anchor="middle">Double number line</text>
<line class="rt-axis" x1="120" y1="110" x2="880" y2="110"/>
<line class="rt-axis" x1="120" y1="200" x2="880" y2="200"/>
<text class="rt-lbl" x="104" y="118" text-anchor="end">plan unit</text>
<text class="rt-lbl" x="104" y="208" text-anchor="end">actual unit</text>
<line class="rt-rung" x1="373" y1="110" x2="373" y2="200"/>
<circle class="rt-given-pt" cx="373" cy="110" r="6"/>
<text class="rt-ticklbl" x="373" y="96" text-anchor="middle">1</text>
<circle class="rt-given-pt" cx="373" cy="200" r="6"/>
<text class="rt-ticklbl" x="373" y="236" text-anchor="middle">2</text>
<line class="rt-rung" x1="626" y1="110" x2="626" y2="200"/>
<circle class="rt-given-pt" cx="626" cy="110" r="6"/>
<text class="rt-ticklbl" x="626" y="96" text-anchor="middle">6</text>
<circle class="rt-unknown-pt" cx="626" cy="200" r="7"/>
</g>
<g class="rt-overlay">
<text class="rt-unknown-lbl" x="626" y="236" text-anchor="middle">12</text>
</g>
</svg>
```

</details>

## missing_part — seed 6 — band 2 (integer, free-response)

| field | value |
|---|---|
| objective | SPI.MIDDLE.RATIO.MISSING_PART.01 |
| interaction / answer | free-response / integer |
| difficulty band | 2 (axes: {"numericalComplexity": 0.3, "exactVsApproximate": 0, "reasoningSteps": 0.5, "abstraction": 0.45}) |
| prompt | Jo and Kim share an amount in the ratio 3:1. Jo gets 18 stickers. How many stickers does Kim get? |
| params | `{"task": "missing_part", "title": "Sharing stickers", "labels": ["Jo", "Kim"], "unit": "stickers", "parts": [3, 1], "knownIndex": 0, "missingIndex": 1, "knownValue": 18}` |
| canonical answer | `{"num": 6, "den": 1}` |
| answer display | 6 |
| accepted form / checker | Integer checker: the exact positive integer is the only accepted value (no tolerance). |
| worked solution | 1. Find the value of one part from the known share -> 18 ÷ 3 = 6; 2. Multiply by the missing part's ratio value -> 6 × 1 = 6 |
| student alt text | A bar model for the ratio 3:1. Jo and Kim share an amount in the ratio 3:1. Jo gets 18 stickers. How many stickers does Kim get? |
| answer-key alt text | Answer key. A bar model for the ratio 3:1. The solved quantities are shown. |
| student data table | `{"columns": ["Part", "Value"], "rows": [["Jo", "3 parts = 18"], ["Kim", "1 part = ?"]]}` |
| answer-key data table | `{"columns": ["Part", "Value"], "rows": [["Jo", "3 parts = 18"], ["Kim", "1 part = 6"]]}` |
| diagnostics exercised | MISC.RATIO.DIVIDES_BY_ONE_PART, MISC.RATIO.MULTIPLIES_NOT_DIVIDES_UNITARY |
| validation checks | 20/20 pass |
| covers cells | 3 |
| reproduction | `python -c "import sys; sys.path.insert(0,'oracle'); from spi_oracle import ratio as R; print(R.serialize(R.generate(6, {'task': 'missing_part'})))"` |
| curriculum-review decision | ☐ APPROVE ☐ REVISE ☐ REJECT |

<details><summary>student figure (SVG)</summary>

```xml
<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1000 300" role="img" aria-label="A bar model for the ratio 3:1. Jo and Kim share an amount in the ratio 3:1. Jo gets 18 stickers. How many stickers does Kim get?">
<title>Bar model</title><desc>A bar model for the ratio 3:1. Unknown quantities are marked with a question mark. Jo and Kim share an amount in the ratio 3:1. Jo gets 18 stickers. How many stickers does Kim get?</desc>
<style>.rt-bar-given{fill:#dddddd;stroke:#111;stroke-width:2}.rt-bar-unknown{fill:#ffffff;stroke:#111;stroke-width:2;stroke-dasharray:6 4}.rt-bar-frame{fill:none;stroke:#111;stroke-width:2.5}.rt-divider{stroke:#111;stroke-width:1.5}.rt-axis{stroke:#111;stroke-width:2.5;fill:none}.rt-tick{stroke:#111;stroke-width:2}.rt-given-pt{fill:#111;stroke:#111;stroke-width:2}.rt-unknown-pt{fill:#ffffff;stroke:#111;stroke-width:2.5;stroke-dasharray:4 3}.rt-rung{stroke:#111;stroke-width:1.5;stroke-dasharray:3 4}.rt-table-line{stroke:#111;stroke-width:2;fill:none}.rt-table-given{fill:#dddddd;stroke:#111;stroke-width:1.5}text{font-family:sans-serif;font-size:26px;fill:#111}.rt-ticklbl{font-size:20px;fill:#333}.rt-lbl{font-size:26px;fill:#111}.rt-unknown-lbl{font-size:28px;font-weight:bold;fill:#111}</style>
<g class="rt-base">
<text class="rt-lbl" x="500" y="56" text-anchor="middle">Bar model: parts in the ratio 3:1</text>
<rect class="rt-bar-given" data-cell="0" x="80" y="110" width="630" height="90"/>
<text class="rt-lbl" x="395" y="236" text-anchor="middle">Jo = 18</text>
<rect class="rt-bar-unknown" data-cell="1" x="710" y="110" width="210" height="90"/>
<text class="rt-lbl" x="815" y="236" text-anchor="middle">Kim = ?</text>
<rect class="rt-bar-frame" x="80" y="110" width="840" height="90"/>
</g>
<g class="rt-student">
<text class="rt-unknown-lbl" x="815" y="172" text-anchor="middle">?</text>
</g>
</svg>
```

</details>
<details><summary>answer-key figure (SVG)</summary>

```xml
<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1000 300" role="img" aria-label="Answer key. A bar model for the ratio 3:1. The solved quantities are shown.">
<title>Bar model</title><desc>A bar model for the ratio 3:1. The solution overlay reveals the answer to: Jo and Kim share an amount in the ratio 3:1. Jo gets 18 stickers. How many stickers does Kim get?</desc>
<style>.rt-bar-given{fill:#dddddd;stroke:#111;stroke-width:2}.rt-bar-unknown{fill:#ffffff;stroke:#111;stroke-width:2;stroke-dasharray:6 4}.rt-bar-frame{fill:none;stroke:#111;stroke-width:2.5}.rt-divider{stroke:#111;stroke-width:1.5}.rt-axis{stroke:#111;stroke-width:2.5;fill:none}.rt-tick{stroke:#111;stroke-width:2}.rt-given-pt{fill:#111;stroke:#111;stroke-width:2}.rt-unknown-pt{fill:#ffffff;stroke:#111;stroke-width:2.5;stroke-dasharray:4 3}.rt-rung{stroke:#111;stroke-width:1.5;stroke-dasharray:3 4}.rt-table-line{stroke:#111;stroke-width:2;fill:none}.rt-table-given{fill:#dddddd;stroke:#111;stroke-width:1.5}text{font-family:sans-serif;font-size:26px;fill:#111}.rt-ticklbl{font-size:20px;fill:#333}.rt-lbl{font-size:26px;fill:#111}.rt-unknown-lbl{font-size:28px;font-weight:bold;fill:#111}</style>
<g class="rt-base">
<text class="rt-lbl" x="500" y="56" text-anchor="middle">Bar model: parts in the ratio 3:1</text>
<rect class="rt-bar-given" data-cell="0" x="80" y="110" width="630" height="90"/>
<text class="rt-lbl" x="395" y="236" text-anchor="middle">Jo = 18</text>
<rect class="rt-bar-unknown" data-cell="1" x="710" y="110" width="210" height="90"/>
<text class="rt-lbl" x="815" y="236" text-anchor="middle">Kim = ?</text>
<rect class="rt-bar-frame" x="80" y="110" width="840" height="90"/>
</g>
<g class="rt-overlay">
<text class="rt-unknown-lbl" x="815" y="172" text-anchor="middle">6</text>
</g>
</svg>
```

</details>

## simplify — seed 7 — band 3 (ratio, free-response)

| field | value |
|---|---|
| objective | SPI.MIDDLE.RATIO.SIMPLIFY.01 |
| interaction / answer | free-response / ratio |
| difficulty band | 3 (axes: {"numericalComplexity": 0.4, "exactVsApproximate": 0, "reasoningSteps": 0.4, "abstraction": 0.35}) |
| prompt | Write the ratio 40:32:24 in its simplest form. |
| params | `{"task": "simplify", "parts": [40, 32, 24]}` |
| canonical answer | `{"parts": [5, 4, 3]}` |
| answer display | 5:4:3 |
| accepted form / checker | Ratio checker (order-sensitive): the canonical simplest-form ordered tuple is the answer; an equivalent form is judged by require_simplest (simplest form required). Reversed order is rejected (wrong-order); a different ratio is wrong-ratio; the wrong number of parts is wrong-number-of-parts; zero/negative/malformed/extra-text/comma/unicode-colon/'to' all map to their named result codes. |
| worked solution | 1. Find the greatest common divisor of the parts -> gcd = 8; 2. Divide every part by the gcd, keeping the order -> 5:4:3 |
| student alt text | No figure; the data is given in the prompt. Write the ratio 40:32:24 in its simplest form. |
| student data table | `{"columns": ["Quantity", "Value"], "rows": [], "note": "no figure for this task; data is given in the prompt"}` |
| diagnostics exercised | MISC.RATIO.NOT_SIMPLIFIED, MISC.RATIO.EQUIVALENT_NOT_SIMPLIFIED, MISC.RATIO.ADDS_PARTS_WRONG |
| validation checks | 10/10 pass |
| covers cells | 3 |
| reproduction | `python -c "import sys; sys.path.insert(0,'oracle'); from spi_oracle import ratio as R; print(R.serialize(R.generate(7, {'task': 'simplify'})))"` |
| curriculum-review decision | ☐ APPROVE ☐ REVISE ☐ REJECT |

## fraction_to_ratio — seed 12 — band 2 (ratio, free-response)

| field | value |
|---|---|
| objective | SPI.MIDDLE.RATIO.FRACTION_TO_RATIO.01 |
| interaction / answer | free-response / ratio |
| difficulty band | 2 (axes: {"numericalComplexity": 0.3, "exactVsApproximate": 0, "reasoningSteps": 0.45, "abstraction": 0.5}) |
| prompt | In a group, 2/3 are one type and the rest are another. Write the ratio of the first type to the rest in its simplest form. |
| params | `{"task": "fraction_to_ratio", "num": 2, "den": 3}` |
| canonical answer | `{"parts": [2, 1]}` |
| answer display | 2:1 |
| accepted form / checker | Ratio checker (order-sensitive): the canonical simplest-form ordered tuple is the answer; an equivalent form is judged by require_simplest (any equivalent ordered ratio accepted). Reversed order is rejected (wrong-order); a different ratio is wrong-ratio; the wrong number of parts is wrong-number-of-parts; zero/negative/malformed/extra-text/comma/unicode-colon/'to' all map to their named result codes. |
| worked solution | 1. Find the remaining part of the whole -> 3 - 2 = 1; 2. Write the part-to-rest ratio and simplify -> 2:1 |
| student alt text | A bar model split into 3 equal parts. In a group, 2/3 are one type and the rest are another. Write the ratio of the first type to the rest in its simplest form. |
| answer-key alt text | Answer key. A bar model split into 3 equal parts. The solved quantities are shown. |
| student data table | `{"columns": ["Part", "Size"], "rows": [["named part (2)", "2"], ["rest (1)", "1"]]}` |
| answer-key data table | `{"columns": ["Part", "Size"], "rows": [["named part (2)", "2"], ["rest (1)", "1"]]}` |
| diagnostics exercised | MISC.RATIO.REVERSED_ORDER, MISC.RATIO.PART_AS_WHOLE, MISC.RATIO.ADDS_PARTS_WRONG |
| validation checks | 20/20 pass |
| covers cells | 3 |
| reproduction | `python -c "import sys; sys.path.insert(0,'oracle'); from spi_oracle import ratio as R; print(R.serialize(R.generate(12, {'task': 'fraction_to_ratio'})))"` |
| curriculum-review decision | ☐ APPROVE ☐ REVISE ☐ REJECT |

<details><summary>student figure (SVG)</summary>

```xml
<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1000 300" role="img" aria-label="A bar model split into 3 equal parts. In a group, 2/3 are one type and the rest are another. Write the ratio of the first type to the rest in its simplest form.">
<title>Bar model</title><desc>A bar model split into 3 equal parts. Unknown quantities are marked with a question mark. In a group, 2/3 are one type and the rest are another. Write the ratio of the first type to the rest in its simplest form.</desc>
<style>.rt-bar-given{fill:#dddddd;stroke:#111;stroke-width:2}.rt-bar-unknown{fill:#ffffff;stroke:#111;stroke-width:2;stroke-dasharray:6 4}.rt-bar-frame{fill:none;stroke:#111;stroke-width:2.5}.rt-divider{stroke:#111;stroke-width:1.5}.rt-axis{stroke:#111;stroke-width:2.5;fill:none}.rt-tick{stroke:#111;stroke-width:2}.rt-given-pt{fill:#111;stroke:#111;stroke-width:2}.rt-unknown-pt{fill:#ffffff;stroke:#111;stroke-width:2.5;stroke-dasharray:4 3}.rt-rung{stroke:#111;stroke-width:1.5;stroke-dasharray:3 4}.rt-table-line{stroke:#111;stroke-width:2;fill:none}.rt-table-given{fill:#dddddd;stroke:#111;stroke-width:1.5}text{font-family:sans-serif;font-size:26px;fill:#111}.rt-ticklbl{font-size:20px;fill:#333}.rt-lbl{font-size:26px;fill:#111}.rt-unknown-lbl{font-size:28px;font-weight:bold;fill:#111}</style>
<g class="rt-base">
<text class="rt-lbl" x="500" y="56" text-anchor="middle">Bar model: 2 of 3 equal parts shaded</text>
<rect class="rt-bar-given" data-cell="0" x="80" y="110" width="560" height="90"/>
<text class="rt-lbl" x="360" y="236" text-anchor="middle">named part (2)</text>
<rect class="rt-bar-given" data-cell="1" x="640" y="110" width="280" height="90"/>
<text class="rt-lbl" x="780" y="236" text-anchor="middle">rest (1)</text>
<rect class="rt-bar-frame" x="80" y="110" width="840" height="90"/>
</g>
<g class="rt-student">
<text class="rt-unknown-lbl" x="500" y="278" text-anchor="middle">Answer: ?</text>
</g>
</svg>
```

</details>
<details><summary>answer-key figure (SVG)</summary>

```xml
<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1000 300" role="img" aria-label="Answer key. A bar model split into 3 equal parts. The solved quantities are shown.">
<title>Bar model</title><desc>A bar model split into 3 equal parts. The solution overlay reveals the answer to: In a group, 2/3 are one type and the rest are another. Write the ratio of the first type to the rest in its simplest form.</desc>
<style>.rt-bar-given{fill:#dddddd;stroke:#111;stroke-width:2}.rt-bar-unknown{fill:#ffffff;stroke:#111;stroke-width:2;stroke-dasharray:6 4}.rt-bar-frame{fill:none;stroke:#111;stroke-width:2.5}.rt-divider{stroke:#111;stroke-width:1.5}.rt-axis{stroke:#111;stroke-width:2.5;fill:none}.rt-tick{stroke:#111;stroke-width:2}.rt-given-pt{fill:#111;stroke:#111;stroke-width:2}.rt-unknown-pt{fill:#ffffff;stroke:#111;stroke-width:2.5;stroke-dasharray:4 3}.rt-rung{stroke:#111;stroke-width:1.5;stroke-dasharray:3 4}.rt-table-line{stroke:#111;stroke-width:2;fill:none}.rt-table-given{fill:#dddddd;stroke:#111;stroke-width:1.5}text{font-family:sans-serif;font-size:26px;fill:#111}.rt-ticklbl{font-size:20px;fill:#333}.rt-lbl{font-size:26px;fill:#111}.rt-unknown-lbl{font-size:28px;font-weight:bold;fill:#111}</style>
<g class="rt-base">
<text class="rt-lbl" x="500" y="56" text-anchor="middle">Bar model: 2 of 3 equal parts shaded</text>
<rect class="rt-bar-given" data-cell="0" x="80" y="110" width="560" height="90"/>
<text class="rt-lbl" x="360" y="236" text-anchor="middle">named part (2)</text>
<rect class="rt-bar-given" data-cell="1" x="640" y="110" width="280" height="90"/>
<text class="rt-lbl" x="780" y="236" text-anchor="middle">rest (1)</text>
<rect class="rt-bar-frame" x="80" y="110" width="840" height="90"/>
</g>
<g class="rt-overlay">
<text class="rt-unknown-lbl" x="500" y="278" text-anchor="middle">Answer: 2:1</text>
</g>
</svg>
```

</details>

## unit_rate — seed 20 — band 2 (integer, free-response)

| field | value |
|---|---|
| objective | SPI.MIDDLE.RATIO.UNIT_RATE.01 |
| interaction / answer | free-response / integer |
| difficulty band | 2 (axes: {"numericalComplexity": 0.3, "exactVsApproximate": 0, "reasoningSteps": 0.45, "abstraction": 0.4}) |
| prompt | 4 trays hold 12 eggs. How many eggs per tray? Give an exact value. |
| params | `{"task": "unit_rate", "amountLabel": "eggs", "perLabel": "trays", "total": 12, "quantity": 4}` |
| canonical answer | `{"num": 3, "den": 1}` |
| answer display | 3 |
| accepted form / checker | Exact-rational checker: the answer is the exact reduced Fraction (num/den); no float, no tolerance; integer-when-whole carries den 1. |
| worked solution | 1. Divide the total by the number of units -> 12 ÷ 4 = 3 |
| student alt text | A double number line aligning the two proportional quantities. 4 trays hold 12 eggs. How many eggs per tray? Give an exact value. |
| answer-key alt text | Answer key. A double number line aligning the two proportional quantities. The solved quantities are shown. |
| student data table | `{"columns": ["trays", "eggs"], "rows": [["4", "12"], ["1", "?"]]}` |
| answer-key data table | `{"columns": ["trays", "eggs"], "rows": [["4", "12"], ["1", "3"]]}` |
| diagnostics exercised | MISC.RATIO.DIVIDES_NOT_MULTIPLIES_UNITARY |
| validation checks | 24/24 pass |
| covers cells | 3 |
| reproduction | `python -c "import sys; sys.path.insert(0,'oracle'); from spi_oracle import ratio as R; print(R.serialize(R.generate(20, {'task': 'unit_rate'})))"` |
| curriculum-review decision | ☐ APPROVE ☐ REVISE ☐ REJECT |

<details><summary>student figure (SVG)</summary>

```xml
<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1000 260" role="img" aria-label="A double number line aligning the two proportional quantities. 4 trays hold 12 eggs. How many eggs per tray? Give an exact value.">
<title>Double number line</title><desc>A double number line aligning the two proportional quantities. Unknown quantities are marked with a question mark. 4 trays hold 12 eggs. How many eggs per tray? Give an exact value.</desc>
<style>.rt-bar-given{fill:#dddddd;stroke:#111;stroke-width:2}.rt-bar-unknown{fill:#ffffff;stroke:#111;stroke-width:2;stroke-dasharray:6 4}.rt-bar-frame{fill:none;stroke:#111;stroke-width:2.5}.rt-divider{stroke:#111;stroke-width:1.5}.rt-axis{stroke:#111;stroke-width:2.5;fill:none}.rt-tick{stroke:#111;stroke-width:2}.rt-given-pt{fill:#111;stroke:#111;stroke-width:2}.rt-unknown-pt{fill:#ffffff;stroke:#111;stroke-width:2.5;stroke-dasharray:4 3}.rt-rung{stroke:#111;stroke-width:1.5;stroke-dasharray:3 4}.rt-table-line{stroke:#111;stroke-width:2;fill:none}.rt-table-given{fill:#dddddd;stroke:#111;stroke-width:1.5}text{font-family:sans-serif;font-size:26px;fill:#111}.rt-ticklbl{font-size:20px;fill:#333}.rt-lbl{font-size:26px;fill:#111}.rt-unknown-lbl{font-size:28px;font-weight:bold;fill:#111}</style>
<g class="rt-base">
<text class="rt-lbl" x="500" y="52" text-anchor="middle">Double number line</text>
<line class="rt-axis" x1="120" y1="110" x2="880" y2="110"/>
<line class="rt-axis" x1="120" y1="200" x2="880" y2="200"/>
<text class="rt-lbl" x="104" y="118" text-anchor="end">trays</text>
<text class="rt-lbl" x="104" y="208" text-anchor="end">eggs</text>
<line class="rt-rung" x1="373" y1="110" x2="373" y2="200"/>
<circle class="rt-given-pt" cx="373" cy="110" r="6"/>
<text class="rt-ticklbl" x="373" y="96" text-anchor="middle">4</text>
<circle class="rt-given-pt" cx="373" cy="200" r="6"/>
<text class="rt-ticklbl" x="373" y="236" text-anchor="middle">12</text>
<line class="rt-rung" x1="626" y1="110" x2="626" y2="200"/>
<circle class="rt-given-pt" cx="626" cy="110" r="6"/>
<text class="rt-ticklbl" x="626" y="96" text-anchor="middle">1</text>
<circle class="rt-unknown-pt" cx="626" cy="200" r="7"/>
</g>
<g class="rt-student">
<text class="rt-unknown-lbl" x="626" y="236" text-anchor="middle">?</text>
</g>
</svg>
```

</details>
<details><summary>answer-key figure (SVG)</summary>

```xml
<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1000 260" role="img" aria-label="Answer key. A double number line aligning the two proportional quantities. The solved quantities are shown.">
<title>Double number line</title><desc>A double number line aligning the two proportional quantities. The solution overlay reveals the answer to: 4 trays hold 12 eggs. How many eggs per tray? Give an exact value.</desc>
<style>.rt-bar-given{fill:#dddddd;stroke:#111;stroke-width:2}.rt-bar-unknown{fill:#ffffff;stroke:#111;stroke-width:2;stroke-dasharray:6 4}.rt-bar-frame{fill:none;stroke:#111;stroke-width:2.5}.rt-divider{stroke:#111;stroke-width:1.5}.rt-axis{stroke:#111;stroke-width:2.5;fill:none}.rt-tick{stroke:#111;stroke-width:2}.rt-given-pt{fill:#111;stroke:#111;stroke-width:2}.rt-unknown-pt{fill:#ffffff;stroke:#111;stroke-width:2.5;stroke-dasharray:4 3}.rt-rung{stroke:#111;stroke-width:1.5;stroke-dasharray:3 4}.rt-table-line{stroke:#111;stroke-width:2;fill:none}.rt-table-given{fill:#dddddd;stroke:#111;stroke-width:1.5}text{font-family:sans-serif;font-size:26px;fill:#111}.rt-ticklbl{font-size:20px;fill:#333}.rt-lbl{font-size:26px;fill:#111}.rt-unknown-lbl{font-size:28px;font-weight:bold;fill:#111}</style>
<g class="rt-base">
<text class="rt-lbl" x="500" y="52" text-anchor="middle">Double number line</text>
<line class="rt-axis" x1="120" y1="110" x2="880" y2="110"/>
<line class="rt-axis" x1="120" y1="200" x2="880" y2="200"/>
<text class="rt-lbl" x="104" y="118" text-anchor="end">trays</text>
<text class="rt-lbl" x="104" y="208" text-anchor="end">eggs</text>
<line class="rt-rung" x1="373" y1="110" x2="373" y2="200"/>
<circle class="rt-given-pt" cx="373" cy="110" r="6"/>
<text class="rt-ticklbl" x="373" y="96" text-anchor="middle">4</text>
<circle class="rt-given-pt" cx="373" cy="200" r="6"/>
<text class="rt-ticklbl" x="373" y="236" text-anchor="middle">12</text>
<line class="rt-rung" x1="626" y1="110" x2="626" y2="200"/>
<circle class="rt-given-pt" cx="626" cy="110" r="6"/>
<text class="rt-ticklbl" x="626" y="96" text-anchor="middle">1</text>
<circle class="rt-unknown-pt" cx="626" cy="200" r="7"/>
</g>
<g class="rt-overlay">
<text class="rt-unknown-lbl" x="626" y="236" text-anchor="middle">3</text>
</g>
</svg>
```

</details>

## simplify — seed 4 — band 2 (ratio, multiple-choice)

| field | value |
|---|---|
| objective | SPI.MIDDLE.RATIO.SIMPLIFY.01 |
| interaction / answer | multiple-choice / ratio |
| difficulty band | 2 (axes: {"numericalComplexity": 0.3, "exactVsApproximate": 0, "reasoningSteps": 0.3, "abstraction": 0.25}) |
| prompt | Write the ratio 8:4 in its simplest form. |
| params | `{"task": "simplify", "parts": [8, 4]}` |
| canonical answer | `{"parts": [2, 1]}` |
| answer display | 2:1 |
| accepted form / checker | Ratio checker (order-sensitive): the canonical simplest-form ordered tuple is the answer; an equivalent form is judged by require_simplest (simplest form required). Reversed order is rejected (wrong-order); a different ratio is wrong-ratio; the wrong number of parts is wrong-number-of-parts; zero/negative/malformed/extra-text/comma/unicode-colon/'to' all map to their named result codes. |
| worked solution | 1. Find the greatest common divisor of the parts -> gcd = 4; 2. Divide every part by the gcd, keeping the order -> 2:1 |
| student alt text | No figure; the data is given in the prompt. Write the ratio 8:4 in its simplest form. |
| student data table | `{"columns": ["Quantity", "Value"], "rows": [], "note": "no figure for this task; data is given in the prompt"}` |
| MC options | A=8:4; B=3; C=4:2; D=2:1 ✓ |
| diagnostics exercised | MISC.RATIO.NOT_SIMPLIFIED, MISC.RATIO.EQUIVALENT_NOT_SIMPLIFIED, MISC.RATIO.ADDS_PARTS_WRONG |
| validation checks | 15/15 pass |
| covers cells | 2 |
| reproduction | `python -c "import sys; sys.path.insert(0,'oracle'); from spi_oracle import ratio as R; print(R.serialize(R.generate(4, {'task': 'simplify'})))"` |
| curriculum-review decision | ☐ APPROVE ☐ REVISE ☐ REJECT |

## ratio_to_fraction — seed 10 — band 3 (exact-rational, multiple-choice)

| field | value |
|---|---|
| objective | SPI.MIDDLE.RATIO.RATIO_TO_FRACTION.01 |
| interaction / answer | multiple-choice / exact-rational |
| difficulty band | 3 (axes: {"numericalComplexity": 0.65, "exactVsApproximate": 0, "reasoningSteps": 0.55, "abstraction": 0.6}) |
| prompt | The class survey mixes boys and girls in the ratio 7:5. What fraction of the whole is girls? Give your answer as a fraction in its simplest form. |
| params | `{"task": "ratio_to_fraction", "title": "Class survey", "labels": ["boys", "girls"], "unit": "people", "parts": [7, 5], "partIndex": 1}` |
| canonical answer | `{"num": 5, "den": 12}` |
| answer display | 5/12 |
| accepted form / checker | Exact-rational checker: the answer is the exact reduced Fraction (num/den); no float, no tolerance; integer-when-whole carries den 1. |
| worked solution | 1. Add the parts to find the total number of parts -> 7 + 5 = 12; 2. Write the named part over the total -> 5/12 = 5/12 |
| student alt text | A bar model for the ratio 7:5. The class survey mixes boys and girls in the ratio 7:5. What fraction of the whole is girls? Give your answer as a fraction in its simplest form. |
| answer-key alt text | Answer key. A bar model for the ratio 7:5. The solved quantities are shown. |
| student data table | `{"columns": ["Part", "Size"], "rows": [["boys (7)", "7"], ["girls (5)", "5"]]}` |
| answer-key data table | `{"columns": ["Part", "Size"], "rows": [["boys (7)", "7"], ["girls (5)", "5"]]}` |
| MC options | A=7/12; B=5/12 ✓; C=1; D=5/7 |
| diagnostics exercised | MISC.RATIO.FRACTION_PART_OVER_PART, MISC.RATIO.REVERSED_ORDER, MISC.RATIO.PART_AS_WHOLE |
| validation checks | 24/24 pass |
| covers cells | 2 |
| reproduction | `python -c "import sys; sys.path.insert(0,'oracle'); from spi_oracle import ratio as R; print(R.serialize(R.generate(10, {'task': 'ratio_to_fraction'})))"` |
| curriculum-review decision | ☐ APPROVE ☐ REVISE ☐ REJECT |

<details><summary>student figure (SVG)</summary>

```xml
<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1000 300" role="img" aria-label="A bar model for the ratio 7:5. The class survey mixes boys and girls in the ratio 7:5. What fraction of the whole is girls? Give your answer as a fraction in its simplest form.">
<title>Bar model</title><desc>A bar model for the ratio 7:5. Unknown quantities are marked with a question mark. The class survey mixes boys and girls in the ratio 7:5. What fraction of the whole is girls? Give your answer as a fraction in its simplest form.</desc>
<style>.rt-bar-given{fill:#dddddd;stroke:#111;stroke-width:2}.rt-bar-unknown{fill:#ffffff;stroke:#111;stroke-width:2;stroke-dasharray:6 4}.rt-bar-frame{fill:none;stroke:#111;stroke-width:2.5}.rt-divider{stroke:#111;stroke-width:1.5}.rt-axis{stroke:#111;stroke-width:2.5;fill:none}.rt-tick{stroke:#111;stroke-width:2}.rt-given-pt{fill:#111;stroke:#111;stroke-width:2}.rt-unknown-pt{fill:#ffffff;stroke:#111;stroke-width:2.5;stroke-dasharray:4 3}.rt-rung{stroke:#111;stroke-width:1.5;stroke-dasharray:3 4}.rt-table-line{stroke:#111;stroke-width:2;fill:none}.rt-table-given{fill:#dddddd;stroke:#111;stroke-width:1.5}text{font-family:sans-serif;font-size:26px;fill:#111}.rt-ticklbl{font-size:20px;fill:#333}.rt-lbl{font-size:26px;fill:#111}.rt-unknown-lbl{font-size:28px;font-weight:bold;fill:#111}</style>
<g class="rt-base">
<text class="rt-lbl" x="500" y="56" text-anchor="middle">Bar model: the whole split as 7:5</text>
<rect class="rt-bar-given" data-cell="0" x="80" y="110" width="490" height="90"/>
<text class="rt-lbl" x="325" y="236" text-anchor="middle">boys (7)</text>
<rect class="rt-bar-given" data-cell="1" x="570" y="110" width="350" height="90"/>
<text class="rt-lbl" x="745" y="236" text-anchor="middle">girls (5)</text>
<rect class="rt-bar-frame" x="80" y="110" width="840" height="90"/>
</g>
<g class="rt-student">
<text class="rt-unknown-lbl" x="500" y="278" text-anchor="middle">Answer: ?</text>
</g>
</svg>
```

</details>
<details><summary>answer-key figure (SVG)</summary>

```xml
<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1000 300" role="img" aria-label="Answer key. A bar model for the ratio 7:5. The solved quantities are shown.">
<title>Bar model</title><desc>A bar model for the ratio 7:5. The solution overlay reveals the answer to: The class survey mixes boys and girls in the ratio 7:5. What fraction of the whole is girls? Give your answer as a fraction in its simplest form.</desc>
<style>.rt-bar-given{fill:#dddddd;stroke:#111;stroke-width:2}.rt-bar-unknown{fill:#ffffff;stroke:#111;stroke-width:2;stroke-dasharray:6 4}.rt-bar-frame{fill:none;stroke:#111;stroke-width:2.5}.rt-divider{stroke:#111;stroke-width:1.5}.rt-axis{stroke:#111;stroke-width:2.5;fill:none}.rt-tick{stroke:#111;stroke-width:2}.rt-given-pt{fill:#111;stroke:#111;stroke-width:2}.rt-unknown-pt{fill:#ffffff;stroke:#111;stroke-width:2.5;stroke-dasharray:4 3}.rt-rung{stroke:#111;stroke-width:1.5;stroke-dasharray:3 4}.rt-table-line{stroke:#111;stroke-width:2;fill:none}.rt-table-given{fill:#dddddd;stroke:#111;stroke-width:1.5}text{font-family:sans-serif;font-size:26px;fill:#111}.rt-ticklbl{font-size:20px;fill:#333}.rt-lbl{font-size:26px;fill:#111}.rt-unknown-lbl{font-size:28px;font-weight:bold;fill:#111}</style>
<g class="rt-base">
<text class="rt-lbl" x="500" y="56" text-anchor="middle">Bar model: the whole split as 7:5</text>
<rect class="rt-bar-given" data-cell="0" x="80" y="110" width="490" height="90"/>
<text class="rt-lbl" x="325" y="236" text-anchor="middle">boys (7)</text>
<rect class="rt-bar-given" data-cell="1" x="570" y="110" width="350" height="90"/>
<text class="rt-lbl" x="745" y="236" text-anchor="middle">girls (5)</text>
<rect class="rt-bar-frame" x="80" y="110" width="840" height="90"/>
</g>
<g class="rt-overlay">
<text class="rt-unknown-lbl" x="500" y="278" text-anchor="middle">Answer: 5/12</text>
</g>
</svg>
```

</details>

## fraction_to_ratio — seed 5 — band 3 (ratio, multiple-choice)

| field | value |
|---|---|
| objective | SPI.MIDDLE.RATIO.FRACTION_TO_RATIO.01 |
| interaction / answer | multiple-choice / ratio |
| difficulty band | 3 (axes: {"numericalComplexity": 0.4, "exactVsApproximate": 0, "reasoningSteps": 0.55, "abstraction": 0.6}) |
| prompt | In a group, 6/8 are one type and the rest are another. Write the ratio of the first type to the rest in its simplest form. |
| params | `{"task": "fraction_to_ratio", "num": 6, "den": 8}` |
| canonical answer | `{"parts": [3, 1]}` |
| answer display | 3:1 |
| accepted form / checker | Ratio checker (order-sensitive): the canonical simplest-form ordered tuple is the answer; an equivalent form is judged by require_simplest (any equivalent ordered ratio accepted). Reversed order is rejected (wrong-order); a different ratio is wrong-ratio; the wrong number of parts is wrong-number-of-parts; zero/negative/malformed/extra-text/comma/unicode-colon/'to' all map to their named result codes. |
| worked solution | 1. Find the remaining part of the whole -> 8 - 6 = 2; 2. Write the part-to-rest ratio and simplify -> 3:1 |
| student alt text | A bar model split into 8 equal parts. In a group, 6/8 are one type and the rest are another. Write the ratio of the first type to the rest in its simplest form. |
| answer-key alt text | Answer key. A bar model split into 8 equal parts. The solved quantities are shown. |
| student data table | `{"columns": ["Part", "Size"], "rows": [["named part (6)", "6"], ["rest (2)", "2"]]}` |
| answer-key data table | `{"columns": ["Part", "Size"], "rows": [["named part (6)", "6"], ["rest (2)", "2"]]}` |
| MC options | A=3:4; B=4:3; C=1:3; D=3:1 ✓ |
| diagnostics exercised | MISC.RATIO.REVERSED_ORDER, MISC.RATIO.PART_AS_WHOLE, MISC.RATIO.ADDS_PARTS_WRONG, MISC.RATIO.NOT_SIMPLIFIED |
| validation checks | 25/25 pass |
| covers cells | 2 |
| reproduction | `python -c "import sys; sys.path.insert(0,'oracle'); from spi_oracle import ratio as R; print(R.serialize(R.generate(5, {'task': 'fraction_to_ratio'})))"` |
| curriculum-review decision | ☐ APPROVE ☐ REVISE ☐ REJECT |

<details><summary>student figure (SVG)</summary>

```xml
<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1000 300" role="img" aria-label="A bar model split into 8 equal parts. In a group, 6/8 are one type and the rest are another. Write the ratio of the first type to the rest in its simplest form.">
<title>Bar model</title><desc>A bar model split into 8 equal parts. Unknown quantities are marked with a question mark. In a group, 6/8 are one type and the rest are another. Write the ratio of the first type to the rest in its simplest form.</desc>
<style>.rt-bar-given{fill:#dddddd;stroke:#111;stroke-width:2}.rt-bar-unknown{fill:#ffffff;stroke:#111;stroke-width:2;stroke-dasharray:6 4}.rt-bar-frame{fill:none;stroke:#111;stroke-width:2.5}.rt-divider{stroke:#111;stroke-width:1.5}.rt-axis{stroke:#111;stroke-width:2.5;fill:none}.rt-tick{stroke:#111;stroke-width:2}.rt-given-pt{fill:#111;stroke:#111;stroke-width:2}.rt-unknown-pt{fill:#ffffff;stroke:#111;stroke-width:2.5;stroke-dasharray:4 3}.rt-rung{stroke:#111;stroke-width:1.5;stroke-dasharray:3 4}.rt-table-line{stroke:#111;stroke-width:2;fill:none}.rt-table-given{fill:#dddddd;stroke:#111;stroke-width:1.5}text{font-family:sans-serif;font-size:26px;fill:#111}.rt-ticklbl{font-size:20px;fill:#333}.rt-lbl{font-size:26px;fill:#111}.rt-unknown-lbl{font-size:28px;font-weight:bold;fill:#111}</style>
<g class="rt-base">
<text class="rt-lbl" x="500" y="56" text-anchor="middle">Bar model: 6 of 8 equal parts shaded</text>
<rect class="rt-bar-given" data-cell="0" x="80" y="110" width="630" height="90"/>
<text class="rt-lbl" x="395" y="236" text-anchor="middle">named part (6)</text>
<rect class="rt-bar-given" data-cell="1" x="710" y="110" width="210" height="90"/>
<text class="rt-lbl" x="815" y="236" text-anchor="middle">rest (2)</text>
<rect class="rt-bar-frame" x="80" y="110" width="840" height="90"/>
</g>
<g class="rt-student">
<text class="rt-unknown-lbl" x="500" y="278" text-anchor="middle">Answer: ?</text>
</g>
</svg>
```

</details>
<details><summary>answer-key figure (SVG)</summary>

```xml
<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1000 300" role="img" aria-label="Answer key. A bar model split into 8 equal parts. The solved quantities are shown.">
<title>Bar model</title><desc>A bar model split into 8 equal parts. The solution overlay reveals the answer to: In a group, 6/8 are one type and the rest are another. Write the ratio of the first type to the rest in its simplest form.</desc>
<style>.rt-bar-given{fill:#dddddd;stroke:#111;stroke-width:2}.rt-bar-unknown{fill:#ffffff;stroke:#111;stroke-width:2;stroke-dasharray:6 4}.rt-bar-frame{fill:none;stroke:#111;stroke-width:2.5}.rt-divider{stroke:#111;stroke-width:1.5}.rt-axis{stroke:#111;stroke-width:2.5;fill:none}.rt-tick{stroke:#111;stroke-width:2}.rt-given-pt{fill:#111;stroke:#111;stroke-width:2}.rt-unknown-pt{fill:#ffffff;stroke:#111;stroke-width:2.5;stroke-dasharray:4 3}.rt-rung{stroke:#111;stroke-width:1.5;stroke-dasharray:3 4}.rt-table-line{stroke:#111;stroke-width:2;fill:none}.rt-table-given{fill:#dddddd;stroke:#111;stroke-width:1.5}text{font-family:sans-serif;font-size:26px;fill:#111}.rt-ticklbl{font-size:20px;fill:#333}.rt-lbl{font-size:26px;fill:#111}.rt-unknown-lbl{font-size:28px;font-weight:bold;fill:#111}</style>
<g class="rt-base">
<text class="rt-lbl" x="500" y="56" text-anchor="middle">Bar model: 6 of 8 equal parts shaded</text>
<rect class="rt-bar-given" data-cell="0" x="80" y="110" width="630" height="90"/>
<text class="rt-lbl" x="395" y="236" text-anchor="middle">named part (6)</text>
<rect class="rt-bar-given" data-cell="1" x="710" y="110" width="210" height="90"/>
<text class="rt-lbl" x="815" y="236" text-anchor="middle">rest (2)</text>
<rect class="rt-bar-frame" x="80" y="110" width="840" height="90"/>
</g>
<g class="rt-overlay">
<text class="rt-unknown-lbl" x="500" y="278" text-anchor="middle">Answer: 3:1</text>
</g>
</svg>
```

</details>

## direct_proportion — seed 1 — band 4 (exact-rational, multiple-choice)

| field | value |
|---|---|
| objective | SPI.MIDDLE.RATIO.DIRECT_PROPORTION.01 |
| interaction / answer | multiple-choice / exact-rational |
| difficulty band | 4 (axes: {"numericalComplexity": 0.65, "exactVsApproximate": 0, "reasoningSteps": 0.65, "abstraction": 0.6}) |
| prompt | 6 sacks hold 1 kilogram. How many kilograms are in 10 sacks? Give an exact value. |
| params | `{"task": "direct_proportion", "givenLabel": "kilograms", "perLabel": "sacks", "quantity": 6, "total": 1, "target": 10}` |
| canonical answer | `{"num": 5, "den": 3}` |
| answer display | 5/3 |
| accepted form / checker | Exact-rational checker: the answer is the exact reduced Fraction (num/den); no float, no tolerance; integer-when-whole carries den 1. |
| worked solution | 1. Find the value of one unit -> 1 ÷ 6 = 1/6; 2. Multiply by the required quantity -> 1/6 × 10 = 5/3 |
| student alt text | A double number line aligning the two proportional quantities. 6 sacks hold 1 kilogram. How many kilograms are in 10 sacks? Give an exact value. |
| answer-key alt text | Answer key. A double number line aligning the two proportional quantities. The solved quantities are shown. |
| student data table | `{"columns": ["sacks", "kilograms"], "rows": [["6", "1"], ["10", "?"]]}` |
| answer-key data table | `{"columns": ["sacks", "kilograms"], "rows": [["6", "1"], ["10", "5/3"]]}` |
| MC options | A=5/3 ✓; B=3/5; C=1/60; D=5 |
| diagnostics exercised | MISC.RATIO.ADDITIVE_NOT_MULTIPLICATIVE, MISC.RATIO.INVERSE_FOR_DIRECT, MISC.RATIO.DIVIDES_NOT_MULTIPLIES_UNITARY |
| validation checks | 27/27 pass |
| covers cells | 2 |
| reproduction | `python -c "import sys; sys.path.insert(0,'oracle'); from spi_oracle import ratio as R; print(R.serialize(R.generate(1, {'task': 'direct_proportion'})))"` |
| curriculum-review decision | ☐ APPROVE ☐ REVISE ☐ REJECT |

<details><summary>student figure (SVG)</summary>

```xml
<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1000 260" role="img" aria-label="A double number line aligning the two proportional quantities. 6 sacks hold 1 kilogram. How many kilograms are in 10 sacks? Give an exact value.">
<title>Double number line</title><desc>A double number line aligning the two proportional quantities. Unknown quantities are marked with a question mark. 6 sacks hold 1 kilogram. How many kilograms are in 10 sacks? Give an exact value.</desc>
<style>.rt-bar-given{fill:#dddddd;stroke:#111;stroke-width:2}.rt-bar-unknown{fill:#ffffff;stroke:#111;stroke-width:2;stroke-dasharray:6 4}.rt-bar-frame{fill:none;stroke:#111;stroke-width:2.5}.rt-divider{stroke:#111;stroke-width:1.5}.rt-axis{stroke:#111;stroke-width:2.5;fill:none}.rt-tick{stroke:#111;stroke-width:2}.rt-given-pt{fill:#111;stroke:#111;stroke-width:2}.rt-unknown-pt{fill:#ffffff;stroke:#111;stroke-width:2.5;stroke-dasharray:4 3}.rt-rung{stroke:#111;stroke-width:1.5;stroke-dasharray:3 4}.rt-table-line{stroke:#111;stroke-width:2;fill:none}.rt-table-given{fill:#dddddd;stroke:#111;stroke-width:1.5}text{font-family:sans-serif;font-size:26px;fill:#111}.rt-ticklbl{font-size:20px;fill:#333}.rt-lbl{font-size:26px;fill:#111}.rt-unknown-lbl{font-size:28px;font-weight:bold;fill:#111}</style>
<g class="rt-base">
<text class="rt-lbl" x="500" y="52" text-anchor="middle">Double number line</text>
<line class="rt-axis" x1="120" y1="110" x2="880" y2="110"/>
<line class="rt-axis" x1="120" y1="200" x2="880" y2="200"/>
<text class="rt-lbl" x="104" y="118" text-anchor="end">sacks</text>
<text class="rt-lbl" x="104" y="208" text-anchor="end">kilograms</text>
<line class="rt-rung" x1="373" y1="110" x2="373" y2="200"/>
<circle class="rt-given-pt" cx="373" cy="110" r="6"/>
<text class="rt-ticklbl" x="373" y="96" text-anchor="middle">6</text>
<circle class="rt-given-pt" cx="373" cy="200" r="6"/>
<text class="rt-ticklbl" x="373" y="236" text-anchor="middle">1</text>
<line class="rt-rung" x1="626" y1="110" x2="626" y2="200"/>
<circle class="rt-given-pt" cx="626" cy="110" r="6"/>
<text class="rt-ticklbl" x="626" y="96" text-anchor="middle">10</text>
<circle class="rt-unknown-pt" cx="626" cy="200" r="7"/>
</g>
<g class="rt-student">
<text class="rt-unknown-lbl" x="626" y="236" text-anchor="middle">?</text>
</g>
</svg>
```

</details>
<details><summary>answer-key figure (SVG)</summary>

```xml
<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1000 260" role="img" aria-label="Answer key. A double number line aligning the two proportional quantities. The solved quantities are shown.">
<title>Double number line</title><desc>A double number line aligning the two proportional quantities. The solution overlay reveals the answer to: 6 sacks hold 1 kilogram. How many kilograms are in 10 sacks? Give an exact value.</desc>
<style>.rt-bar-given{fill:#dddddd;stroke:#111;stroke-width:2}.rt-bar-unknown{fill:#ffffff;stroke:#111;stroke-width:2;stroke-dasharray:6 4}.rt-bar-frame{fill:none;stroke:#111;stroke-width:2.5}.rt-divider{stroke:#111;stroke-width:1.5}.rt-axis{stroke:#111;stroke-width:2.5;fill:none}.rt-tick{stroke:#111;stroke-width:2}.rt-given-pt{fill:#111;stroke:#111;stroke-width:2}.rt-unknown-pt{fill:#ffffff;stroke:#111;stroke-width:2.5;stroke-dasharray:4 3}.rt-rung{stroke:#111;stroke-width:1.5;stroke-dasharray:3 4}.rt-table-line{stroke:#111;stroke-width:2;fill:none}.rt-table-given{fill:#dddddd;stroke:#111;stroke-width:1.5}text{font-family:sans-serif;font-size:26px;fill:#111}.rt-ticklbl{font-size:20px;fill:#333}.rt-lbl{font-size:26px;fill:#111}.rt-unknown-lbl{font-size:28px;font-weight:bold;fill:#111}</style>
<g class="rt-base">
<text class="rt-lbl" x="500" y="52" text-anchor="middle">Double number line</text>
<line class="rt-axis" x1="120" y1="110" x2="880" y2="110"/>
<line class="rt-axis" x1="120" y1="200" x2="880" y2="200"/>
<text class="rt-lbl" x="104" y="118" text-anchor="end">sacks</text>
<text class="rt-lbl" x="104" y="208" text-anchor="end">kilograms</text>
<line class="rt-rung" x1="373" y1="110" x2="373" y2="200"/>
<circle class="rt-given-pt" cx="373" cy="110" r="6"/>
<text class="rt-ticklbl" x="373" y="96" text-anchor="middle">6</text>
<circle class="rt-given-pt" cx="373" cy="200" r="6"/>
<text class="rt-ticklbl" x="373" y="236" text-anchor="middle">1</text>
<line class="rt-rung" x1="626" y1="110" x2="626" y2="200"/>
<circle class="rt-given-pt" cx="626" cy="110" r="6"/>
<text class="rt-ticklbl" x="626" y="96" text-anchor="middle">10</text>
<circle class="rt-unknown-pt" cx="626" cy="200" r="7"/>
</g>
<g class="rt-overlay">
<text class="rt-unknown-lbl" x="626" y="236" text-anchor="middle">5/3</text>
</g>
</svg>
```

</details>

## inverse_proportion — seed 10 — band 4 (integer, multiple-choice)

| field | value |
|---|---|
| objective | SPI.MIDDLE.RATIO.INVERSE_PROPORTION.01 |
| interaction / answer | multiple-choice / integer |
| difficulty band | 4 (axes: {"numericalComplexity": 0.4, "exactVsApproximate": 0, "reasoningSteps": 0.8, "abstraction": 0.75}) |
| prompt | 8 machines take 9 minutes to complete the batch. How many minutes would 36 machines take to complete the batch? |
| params | `{"task": "inverse_proportion", "agent": "machines", "unit": "minutes", "tail": "to complete the batch", "q1": 8, "v1": 9, "q2": 36}` |
| canonical answer | `{"num": 2, "den": 1}` |
| answer display | 2 |
| accepted form / checker | Integer checker: the exact positive integer is the only accepted value (no tolerance). |
| worked solution | 1. Use the product invariant (more means less) -> 8 × 9 = 72; 2. Divide the product by the new quantity -> 72 ÷ 36 = 2 |
| student alt text | No figure; the data is given in the prompt. 8 machines take 9 minutes to complete the batch. How many minutes would 36 machines take to complete the batch? |
| student data table | `{"columns": ["Quantity", "Value"], "rows": [], "note": "no figure for this task; data is given in the prompt"}` |
| MC options | A=72; B=2 ✓; C=37; D=81/2 |
| diagnostics exercised | MISC.RATIO.DIRECT_FOR_INVERSE, MISC.RATIO.MULTIPLIES_NOT_DIVIDES_UNITARY, MISC.RATIO.ADDITIVE_NOT_MULTIPLICATIVE |
| validation checks | 13/13 pass |
| covers cells | 2 |
| reproduction | `python -c "import sys; sys.path.insert(0,'oracle'); from spi_oracle import ratio as R; print(R.serialize(R.generate(10, {'task': 'inverse_proportion'})))"` |
| curriculum-review decision | ☐ APPROVE ☐ REVISE ☐ REJECT |

## write_from_quantities — seed 8 — band 3 (ratio, free-response)

| field | value |
|---|---|
| objective | SPI.MIDDLE.RATIO.WRITE_FROM_QUANTITIES.01 |
| interaction / answer | free-response / ratio |
| difficulty band | 3 (axes: {"numericalComplexity": 0.4, "exactVsApproximate": 0, "reasoningSteps": 0.45, "abstraction": 0.4}) |
| prompt | In a recipe there are 25 flour, 20 sugar, 30 butter. Write the ratio of flour to sugar to butter in its simplest form. |
| params | `{"task": "write_from_quantities", "title": "Recipe", "labels": ["flour", "sugar", "butter"], "unit": "grams", "quantities": [25, 20, 30]}` |
| canonical answer | `{"parts": [5, 4, 6]}` |
| answer display | 5:4:6 |
| accepted form / checker | Ratio checker (order-sensitive): the canonical simplest-form ordered tuple is the answer; an equivalent form is judged by require_simplest (any equivalent ordered ratio accepted). Reversed order is rejected (wrong-order); a different ratio is wrong-ratio; the wrong number of parts is wrong-number-of-parts; zero/negative/malformed/extra-text/comma/unicode-colon/'to' all map to their named result codes. |
| worked solution | 1. Find the greatest common divisor of the parts -> gcd = 5; 2. Divide every part by the gcd, keeping the order -> 5:4:6 |
| student alt text | No figure; the data is given in the prompt. In a recipe there are 25 flour, 20 sugar, 30 butter. Write the ratio of flour to sugar to butter in its simplest form. |
| student data table | `{"columns": ["Quantity", "Value"], "rows": [], "note": "no figure for this task; data is given in the prompt"}` |
| diagnostics exercised | MISC.RATIO.REVERSED_ORDER, MISC.RATIO.NOT_SIMPLIFIED |
| validation checks | 11/11 pass |
| covers cells | 1 |
| reproduction | `python -c "import sys; sys.path.insert(0,'oracle'); from spi_oracle import ratio as R; print(R.serialize(R.generate(8, {'task': 'write_from_quantities'})))"` |
| curriculum-review decision | ☐ APPROVE ☐ REVISE ☐ REJECT |

## missing_part — seed 13 — band 3 (integer, free-response)

| field | value |
|---|---|
| objective | SPI.MIDDLE.RATIO.MISSING_PART.01 |
| interaction / answer | free-response / integer |
| difficulty band | 3 (axes: {"numericalComplexity": 0.4, "exactVsApproximate": 0, "reasoningSteps": 0.6, "abstraction": 0.55}) |
| prompt | Gus and Hana share an amount in the ratio 5:2. Gus gets 35 marbles. How many marbles does Hana get? |
| params | `{"task": "missing_part", "title": "Sharing marbles", "labels": ["Gus", "Hana"], "unit": "marbles", "parts": [5, 2], "knownIndex": 0, "missingIndex": 1, "knownValue": 35}` |
| canonical answer | `{"num": 14, "den": 1}` |
| answer display | 14 |
| accepted form / checker | Integer checker: the exact positive integer is the only accepted value (no tolerance). |
| worked solution | 1. Find the value of one part from the known share -> 35 ÷ 5 = 7; 2. Multiply by the missing part's ratio value -> 7 × 2 = 14 |
| student alt text | A bar model for the ratio 5:2. Gus and Hana share an amount in the ratio 5:2. Gus gets 35 marbles. How many marbles does Hana get? |
| answer-key alt text | Answer key. A bar model for the ratio 5:2. The solved quantities are shown. |
| student data table | `{"columns": ["Part", "Value"], "rows": [["Gus", "5 parts = 35"], ["Hana", "2 parts = ?"]]}` |
| answer-key data table | `{"columns": ["Part", "Value"], "rows": [["Gus", "5 parts = 35"], ["Hana", "2 parts = 14"]]}` |
| diagnostics exercised | MISC.RATIO.DIVIDES_BY_ONE_PART, MISC.RATIO.MULTIPLIES_NOT_DIVIDES_UNITARY |
| validation checks | 20/20 pass |
| covers cells | 1 |
| reproduction | `python -c "import sys; sys.path.insert(0,'oracle'); from spi_oracle import ratio as R; print(R.serialize(R.generate(13, {'task': 'missing_part'})))"` |
| curriculum-review decision | ☐ APPROVE ☐ REVISE ☐ REJECT |

<details><summary>student figure (SVG)</summary>

```xml
<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1000 300" role="img" aria-label="A bar model for the ratio 5:2. Gus and Hana share an amount in the ratio 5:2. Gus gets 35 marbles. How many marbles does Hana get?">
<title>Bar model</title><desc>A bar model for the ratio 5:2. Unknown quantities are marked with a question mark. Gus and Hana share an amount in the ratio 5:2. Gus gets 35 marbles. How many marbles does Hana get?</desc>
<style>.rt-bar-given{fill:#dddddd;stroke:#111;stroke-width:2}.rt-bar-unknown{fill:#ffffff;stroke:#111;stroke-width:2;stroke-dasharray:6 4}.rt-bar-frame{fill:none;stroke:#111;stroke-width:2.5}.rt-divider{stroke:#111;stroke-width:1.5}.rt-axis{stroke:#111;stroke-width:2.5;fill:none}.rt-tick{stroke:#111;stroke-width:2}.rt-given-pt{fill:#111;stroke:#111;stroke-width:2}.rt-unknown-pt{fill:#ffffff;stroke:#111;stroke-width:2.5;stroke-dasharray:4 3}.rt-rung{stroke:#111;stroke-width:1.5;stroke-dasharray:3 4}.rt-table-line{stroke:#111;stroke-width:2;fill:none}.rt-table-given{fill:#dddddd;stroke:#111;stroke-width:1.5}text{font-family:sans-serif;font-size:26px;fill:#111}.rt-ticklbl{font-size:20px;fill:#333}.rt-lbl{font-size:26px;fill:#111}.rt-unknown-lbl{font-size:28px;font-weight:bold;fill:#111}</style>
<g class="rt-base">
<text class="rt-lbl" x="500" y="56" text-anchor="middle">Bar model: parts in the ratio 5:2</text>
<rect class="rt-bar-given" data-cell="0" x="80" y="110" width="600" height="90"/>
<text class="rt-lbl" x="380" y="236" text-anchor="middle">Gus = 35</text>
<rect class="rt-bar-unknown" data-cell="1" x="680" y="110" width="240" height="90"/>
<text class="rt-lbl" x="800" y="236" text-anchor="middle">Hana = ?</text>
<rect class="rt-bar-frame" x="80" y="110" width="840" height="90"/>
</g>
<g class="rt-student">
<text class="rt-unknown-lbl" x="800" y="172" text-anchor="middle">?</text>
</g>
</svg>
```

</details>
<details><summary>answer-key figure (SVG)</summary>

```xml
<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1000 300" role="img" aria-label="Answer key. A bar model for the ratio 5:2. The solved quantities are shown.">
<title>Bar model</title><desc>A bar model for the ratio 5:2. The solution overlay reveals the answer to: Gus and Hana share an amount in the ratio 5:2. Gus gets 35 marbles. How many marbles does Hana get?</desc>
<style>.rt-bar-given{fill:#dddddd;stroke:#111;stroke-width:2}.rt-bar-unknown{fill:#ffffff;stroke:#111;stroke-width:2;stroke-dasharray:6 4}.rt-bar-frame{fill:none;stroke:#111;stroke-width:2.5}.rt-divider{stroke:#111;stroke-width:1.5}.rt-axis{stroke:#111;stroke-width:2.5;fill:none}.rt-tick{stroke:#111;stroke-width:2}.rt-given-pt{fill:#111;stroke:#111;stroke-width:2}.rt-unknown-pt{fill:#ffffff;stroke:#111;stroke-width:2.5;stroke-dasharray:4 3}.rt-rung{stroke:#111;stroke-width:1.5;stroke-dasharray:3 4}.rt-table-line{stroke:#111;stroke-width:2;fill:none}.rt-table-given{fill:#dddddd;stroke:#111;stroke-width:1.5}text{font-family:sans-serif;font-size:26px;fill:#111}.rt-ticklbl{font-size:20px;fill:#333}.rt-lbl{font-size:26px;fill:#111}.rt-unknown-lbl{font-size:28px;font-weight:bold;fill:#111}</style>
<g class="rt-base">
<text class="rt-lbl" x="500" y="56" text-anchor="middle">Bar model: parts in the ratio 5:2</text>
<rect class="rt-bar-given" data-cell="0" x="80" y="110" width="600" height="90"/>
<text class="rt-lbl" x="380" y="236" text-anchor="middle">Gus = 35</text>
<rect class="rt-bar-unknown" data-cell="1" x="680" y="110" width="240" height="90"/>
<text class="rt-lbl" x="800" y="236" text-anchor="middle">Hana = ?</text>
<rect class="rt-bar-frame" x="80" y="110" width="840" height="90"/>
</g>
<g class="rt-overlay">
<text class="rt-unknown-lbl" x="800" y="172" text-anchor="middle">14</text>
</g>
</svg>
```

</details>

## share_three_part — seed 21 — band 4 (table-completion, free-response)

| field | value |
|---|---|
| objective | SPI.MIDDLE.RATIO.SHARE_THREE_PART.01 |
| interaction / answer | free-response / table-completion |
| difficulty band | 4 (axes: {"numericalComplexity": 0.4, "exactVsApproximate": 0, "reasoningSteps": 0.7, "abstraction": 0.6}) |
| prompt | Share 70 sweets between Dana, Eli, Faye in the ratio 2:2:3. Give each share. |
| params | `{"task": "share_three_part", "title": "Sharing sweets", "labels": ["Dana", "Eli", "Faye"], "unit": "sweets", "parts": [2, 2, 3], "total": 70}` |
| canonical answer | `{"cells": [{"location": "Dana", "value": 20}, {"location": "Eli", "value": 20}, {"location": "Faye", "value": 30}]}` |
| answer display | Dana=20, Eli=20, Faye=30 |
| accepted form / checker | Table completion: each labelled share is matched by location label (order-independent) against the exact canonical integer value; the shares sum to the whole. |
| worked solution | 1. Add the parts to find the total number of parts -> 2 + 2 + 3 = 7; 2. Find the value of one part -> 70 ÷ 7 = 10; 3. Multiply to give each share -> Dana=20, Eli=20, Faye=30 |
| student alt text | A bar model for the ratio 2:2:3. Share 70 sweets between Dana, Eli, Faye in the ratio 2:2:3. Give each share. |
| answer-key alt text | Answer key. A bar model for the ratio 2:2:3. The solved quantities are shown. |
| student data table | `{"columns": ["Share", "Ratio part"], "rows": [["Dana", "2 parts"], ["Eli", "2 parts"], ["Faye", "3 parts"]]}` |
| answer-key data table | `{"columns": ["Share", "Ratio part"], "rows": [["Dana", "2 parts -> 20 sweets"], ["Eli", "2 parts -> 20 sweets"], ["Faye", "3 parts -> 30 sweets"]]}` |
| diagnostics exercised | MISC.RATIO.DIVIDES_BY_ONE_PART |
| validation checks | 21/21 pass |
| covers cells | 1 |
| reproduction | `python -c "import sys; sys.path.insert(0,'oracle'); from spi_oracle import ratio as R; print(R.serialize(R.generate(21, {'task': 'share_three_part'})))"` |
| curriculum-review decision | ☐ APPROVE ☐ REVISE ☐ REJECT |

<details><summary>student figure (SVG)</summary>

```xml
<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1000 300" role="img" aria-label="A bar model for the ratio 2:2:3. Share 70 sweets between Dana, Eli, Faye in the ratio 2:2:3. Give each share.">
<title>Bar model</title><desc>A bar model for the ratio 2:2:3. Unknown quantities are marked with a question mark. Share 70 sweets between Dana, Eli, Faye in the ratio 2:2:3. Give each share.</desc>
<style>.rt-bar-given{fill:#dddddd;stroke:#111;stroke-width:2}.rt-bar-unknown{fill:#ffffff;stroke:#111;stroke-width:2;stroke-dasharray:6 4}.rt-bar-frame{fill:none;stroke:#111;stroke-width:2.5}.rt-divider{stroke:#111;stroke-width:1.5}.rt-axis{stroke:#111;stroke-width:2.5;fill:none}.rt-tick{stroke:#111;stroke-width:2}.rt-given-pt{fill:#111;stroke:#111;stroke-width:2}.rt-unknown-pt{fill:#ffffff;stroke:#111;stroke-width:2.5;stroke-dasharray:4 3}.rt-rung{stroke:#111;stroke-width:1.5;stroke-dasharray:3 4}.rt-table-line{stroke:#111;stroke-width:2;fill:none}.rt-table-given{fill:#dddddd;stroke:#111;stroke-width:1.5}text{font-family:sans-serif;font-size:26px;fill:#111}.rt-ticklbl{font-size:20px;fill:#333}.rt-lbl{font-size:26px;fill:#111}.rt-unknown-lbl{font-size:28px;font-weight:bold;fill:#111}</style>
<g class="rt-base">
<text class="rt-lbl" x="500" y="56" text-anchor="middle">Bar model: 70 sweets shared in 2:2:3</text>
<rect class="rt-bar-unknown" data-cell="0" x="80" y="110" width="240" height="90"/>
<text class="rt-lbl" x="200" y="236" text-anchor="middle">Dana (2 parts)</text>
<rect class="rt-bar-unknown" data-cell="1" x="320" y="110" width="240" height="90"/>
<text class="rt-lbl" x="440" y="236" text-anchor="middle">Eli (2 parts)</text>
<rect class="rt-bar-unknown" data-cell="2" x="560" y="110" width="360" height="90"/>
<text class="rt-lbl" x="740" y="236" text-anchor="middle">Faye (3 parts)</text>
<rect class="rt-bar-frame" x="80" y="110" width="840" height="90"/>
</g>
<g class="rt-student">
<text class="rt-unknown-lbl" x="200" y="172" text-anchor="middle">?</text>
<text class="rt-unknown-lbl" x="440" y="172" text-anchor="middle">?</text>
<text class="rt-unknown-lbl" x="740" y="172" text-anchor="middle">?</text>
</g>
</svg>
```

</details>
<details><summary>answer-key figure (SVG)</summary>

```xml
<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1000 300" role="img" aria-label="Answer key. A bar model for the ratio 2:2:3. The solved quantities are shown.">
<title>Bar model</title><desc>A bar model for the ratio 2:2:3. The solution overlay reveals the answer to: Share 70 sweets between Dana, Eli, Faye in the ratio 2:2:3. Give each share.</desc>
<style>.rt-bar-given{fill:#dddddd;stroke:#111;stroke-width:2}.rt-bar-unknown{fill:#ffffff;stroke:#111;stroke-width:2;stroke-dasharray:6 4}.rt-bar-frame{fill:none;stroke:#111;stroke-width:2.5}.rt-divider{stroke:#111;stroke-width:1.5}.rt-axis{stroke:#111;stroke-width:2.5;fill:none}.rt-tick{stroke:#111;stroke-width:2}.rt-given-pt{fill:#111;stroke:#111;stroke-width:2}.rt-unknown-pt{fill:#ffffff;stroke:#111;stroke-width:2.5;stroke-dasharray:4 3}.rt-rung{stroke:#111;stroke-width:1.5;stroke-dasharray:3 4}.rt-table-line{stroke:#111;stroke-width:2;fill:none}.rt-table-given{fill:#dddddd;stroke:#111;stroke-width:1.5}text{font-family:sans-serif;font-size:26px;fill:#111}.rt-ticklbl{font-size:20px;fill:#333}.rt-lbl{font-size:26px;fill:#111}.rt-unknown-lbl{font-size:28px;font-weight:bold;fill:#111}</style>
<g class="rt-base">
<text class="rt-lbl" x="500" y="56" text-anchor="middle">Bar model: 70 sweets shared in 2:2:3</text>
<rect class="rt-bar-unknown" data-cell="0" x="80" y="110" width="240" height="90"/>
<text class="rt-lbl" x="200" y="236" text-anchor="middle">Dana (2 parts)</text>
<rect class="rt-bar-unknown" data-cell="1" x="320" y="110" width="240" height="90"/>
<text class="rt-lbl" x="440" y="236" text-anchor="middle">Eli (2 parts)</text>
<rect class="rt-bar-unknown" data-cell="2" x="560" y="110" width="360" height="90"/>
<text class="rt-lbl" x="740" y="236" text-anchor="middle">Faye (3 parts)</text>
<rect class="rt-bar-frame" x="80" y="110" width="840" height="90"/>
</g>
<g class="rt-overlay">
<text class="rt-unknown-lbl" x="200" y="172" text-anchor="middle">20</text>
<text class="rt-unknown-lbl" x="440" y="172" text-anchor="middle">20</text>
<text class="rt-unknown-lbl" x="740" y="172" text-anchor="middle">30</text>
</g>
</svg>
```

</details>

## direct_proportion — seed 22 — band 2 (integer, free-response)

| field | value |
|---|---|
| objective | SPI.MIDDLE.RATIO.DIRECT_PROPORTION.01 |
| interaction / answer | free-response / integer |
| difficulty band | 2 (axes: {"numericalComplexity": 0.3, "exactVsApproximate": 0, "reasoningSteps": 0.55, "abstraction": 0.5}) |
| prompt | 3 sacks hold 9 kilograms. How many kilograms are in 5 sacks? Give an exact value. |
| params | `{"task": "direct_proportion", "givenLabel": "kilograms", "perLabel": "sacks", "quantity": 3, "total": 9, "target": 5}` |
| canonical answer | `{"num": 15, "den": 1}` |
| answer display | 15 |
| accepted form / checker | Exact-rational checker: the answer is the exact reduced Fraction (num/den); no float, no tolerance; integer-when-whole carries den 1. |
| worked solution | 1. Find the value of one unit -> 9 ÷ 3 = 3; 2. Multiply by the required quantity -> 3 × 5 = 15 |
| student alt text | A double number line aligning the two proportional quantities. 3 sacks hold 9 kilograms. How many kilograms are in 5 sacks? Give an exact value. |
| answer-key alt text | Answer key. A double number line aligning the two proportional quantities. The solved quantities are shown. |
| student data table | `{"columns": ["sacks", "kilograms"], "rows": [["3", "9"], ["5", "?"]]}` |
| answer-key data table | `{"columns": ["sacks", "kilograms"], "rows": [["3", "9"], ["5", "15"]]}` |
| diagnostics exercised | MISC.RATIO.ADDITIVE_NOT_MULTIPLICATIVE, MISC.RATIO.INVERSE_FOR_DIRECT, MISC.RATIO.DIVIDES_NOT_MULTIPLIES_UNITARY |
| validation checks | 22/22 pass |
| covers cells | 1 |
| reproduction | `python -c "import sys; sys.path.insert(0,'oracle'); from spi_oracle import ratio as R; print(R.serialize(R.generate(22, {'task': 'direct_proportion'})))"` |
| curriculum-review decision | ☐ APPROVE ☐ REVISE ☐ REJECT |

<details><summary>student figure (SVG)</summary>

```xml
<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1000 260" role="img" aria-label="A double number line aligning the two proportional quantities. 3 sacks hold 9 kilograms. How many kilograms are in 5 sacks? Give an exact value.">
<title>Double number line</title><desc>A double number line aligning the two proportional quantities. Unknown quantities are marked with a question mark. 3 sacks hold 9 kilograms. How many kilograms are in 5 sacks? Give an exact value.</desc>
<style>.rt-bar-given{fill:#dddddd;stroke:#111;stroke-width:2}.rt-bar-unknown{fill:#ffffff;stroke:#111;stroke-width:2;stroke-dasharray:6 4}.rt-bar-frame{fill:none;stroke:#111;stroke-width:2.5}.rt-divider{stroke:#111;stroke-width:1.5}.rt-axis{stroke:#111;stroke-width:2.5;fill:none}.rt-tick{stroke:#111;stroke-width:2}.rt-given-pt{fill:#111;stroke:#111;stroke-width:2}.rt-unknown-pt{fill:#ffffff;stroke:#111;stroke-width:2.5;stroke-dasharray:4 3}.rt-rung{stroke:#111;stroke-width:1.5;stroke-dasharray:3 4}.rt-table-line{stroke:#111;stroke-width:2;fill:none}.rt-table-given{fill:#dddddd;stroke:#111;stroke-width:1.5}text{font-family:sans-serif;font-size:26px;fill:#111}.rt-ticklbl{font-size:20px;fill:#333}.rt-lbl{font-size:26px;fill:#111}.rt-unknown-lbl{font-size:28px;font-weight:bold;fill:#111}</style>
<g class="rt-base">
<text class="rt-lbl" x="500" y="52" text-anchor="middle">Double number line</text>
<line class="rt-axis" x1="120" y1="110" x2="880" y2="110"/>
<line class="rt-axis" x1="120" y1="200" x2="880" y2="200"/>
<text class="rt-lbl" x="104" y="118" text-anchor="end">sacks</text>
<text class="rt-lbl" x="104" y="208" text-anchor="end">kilograms</text>
<line class="rt-rung" x1="373" y1="110" x2="373" y2="200"/>
<circle class="rt-given-pt" cx="373" cy="110" r="6"/>
<text class="rt-ticklbl" x="373" y="96" text-anchor="middle">3</text>
<circle class="rt-given-pt" cx="373" cy="200" r="6"/>
<text class="rt-ticklbl" x="373" y="236" text-anchor="middle">9</text>
<line class="rt-rung" x1="626" y1="110" x2="626" y2="200"/>
<circle class="rt-given-pt" cx="626" cy="110" r="6"/>
<text class="rt-ticklbl" x="626" y="96" text-anchor="middle">5</text>
<circle class="rt-unknown-pt" cx="626" cy="200" r="7"/>
</g>
<g class="rt-student">
<text class="rt-unknown-lbl" x="626" y="236" text-anchor="middle">?</text>
</g>
</svg>
```

</details>
<details><summary>answer-key figure (SVG)</summary>

```xml
<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1000 260" role="img" aria-label="Answer key. A double number line aligning the two proportional quantities. The solved quantities are shown.">
<title>Double number line</title><desc>A double number line aligning the two proportional quantities. The solution overlay reveals the answer to: 3 sacks hold 9 kilograms. How many kilograms are in 5 sacks? Give an exact value.</desc>
<style>.rt-bar-given{fill:#dddddd;stroke:#111;stroke-width:2}.rt-bar-unknown{fill:#ffffff;stroke:#111;stroke-width:2;stroke-dasharray:6 4}.rt-bar-frame{fill:none;stroke:#111;stroke-width:2.5}.rt-divider{stroke:#111;stroke-width:1.5}.rt-axis{stroke:#111;stroke-width:2.5;fill:none}.rt-tick{stroke:#111;stroke-width:2}.rt-given-pt{fill:#111;stroke:#111;stroke-width:2}.rt-unknown-pt{fill:#ffffff;stroke:#111;stroke-width:2.5;stroke-dasharray:4 3}.rt-rung{stroke:#111;stroke-width:1.5;stroke-dasharray:3 4}.rt-table-line{stroke:#111;stroke-width:2;fill:none}.rt-table-given{fill:#dddddd;stroke:#111;stroke-width:1.5}text{font-family:sans-serif;font-size:26px;fill:#111}.rt-ticklbl{font-size:20px;fill:#333}.rt-lbl{font-size:26px;fill:#111}.rt-unknown-lbl{font-size:28px;font-weight:bold;fill:#111}</style>
<g class="rt-base">
<text class="rt-lbl" x="500" y="52" text-anchor="middle">Double number line</text>
<line class="rt-axis" x1="120" y1="110" x2="880" y2="110"/>
<line class="rt-axis" x1="120" y1="200" x2="880" y2="200"/>
<text class="rt-lbl" x="104" y="118" text-anchor="end">sacks</text>
<text class="rt-lbl" x="104" y="208" text-anchor="end">kilograms</text>
<line class="rt-rung" x1="373" y1="110" x2="373" y2="200"/>
<circle class="rt-given-pt" cx="373" cy="110" r="6"/>
<text class="rt-ticklbl" x="373" y="96" text-anchor="middle">3</text>
<circle class="rt-given-pt" cx="373" cy="200" r="6"/>
<text class="rt-ticklbl" x="373" y="236" text-anchor="middle">9</text>
<line class="rt-rung" x1="626" y1="110" x2="626" y2="200"/>
<circle class="rt-given-pt" cx="626" cy="110" r="6"/>
<text class="rt-ticklbl" x="626" y="96" text-anchor="middle">5</text>
<circle class="rt-unknown-pt" cx="626" cy="200" r="7"/>
</g>
<g class="rt-overlay">
<text class="rt-unknown-lbl" x="626" y="236" text-anchor="middle">15</text>
</g>
</svg>
```

</details>

## share_two_part — seed 32 — band 3 (table-completion, free-response)

| field | value |
|---|---|
| objective | SPI.MIDDLE.RATIO.SHARE_TWO_PART.01 |
| interaction / answer | free-response / table-completion |
| difficulty band | 3 (axes: {"numericalComplexity": 0.4, "exactVsApproximate": 0, "reasoningSteps": 0.6, "abstraction": 0.5}) |
| prompt | Share 49 stickers between Jo, Kim in the ratio 2:5. Give each share. |
| params | `{"task": "share_two_part", "title": "Sharing stickers", "labels": ["Jo", "Kim"], "unit": "stickers", "parts": [2, 5], "total": 49}` |
| canonical answer | `{"cells": [{"location": "Jo", "value": 14}, {"location": "Kim", "value": 35}]}` |
| answer display | Jo=14, Kim=35 |
| accepted form / checker | Table completion: each labelled share is matched by location label (order-independent) against the exact canonical integer value; the shares sum to the whole. |
| worked solution | 1. Add the parts to find the total number of parts -> 2 + 5 = 7; 2. Find the value of one part -> 49 ÷ 7 = 7; 3. Multiply to give each share -> Jo=14, Kim=35 |
| student alt text | A bar model for the ratio 2:5. Share 49 stickers between Jo, Kim in the ratio 2:5. Give each share. |
| answer-key alt text | Answer key. A bar model for the ratio 2:5. The solved quantities are shown. |
| student data table | `{"columns": ["Share", "Ratio part"], "rows": [["Jo", "2 parts"], ["Kim", "5 parts"]]}` |
| answer-key data table | `{"columns": ["Share", "Ratio part"], "rows": [["Jo", "2 parts -> 14 stickers"], ["Kim", "5 parts -> 35 stickers"]]}` |
| diagnostics exercised | MISC.RATIO.PART_AS_WHOLE |
| validation checks | 21/21 pass |
| covers cells | 1 |
| reproduction | `python -c "import sys; sys.path.insert(0,'oracle'); from spi_oracle import ratio as R; print(R.serialize(R.generate(32, {'task': 'share_two_part'})))"` |
| curriculum-review decision | ☐ APPROVE ☐ REVISE ☐ REJECT |

<details><summary>student figure (SVG)</summary>

```xml
<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1000 300" role="img" aria-label="A bar model for the ratio 2:5. Share 49 stickers between Jo, Kim in the ratio 2:5. Give each share.">
<title>Bar model</title><desc>A bar model for the ratio 2:5. Unknown quantities are marked with a question mark. Share 49 stickers between Jo, Kim in the ratio 2:5. Give each share.</desc>
<style>.rt-bar-given{fill:#dddddd;stroke:#111;stroke-width:2}.rt-bar-unknown{fill:#ffffff;stroke:#111;stroke-width:2;stroke-dasharray:6 4}.rt-bar-frame{fill:none;stroke:#111;stroke-width:2.5}.rt-divider{stroke:#111;stroke-width:1.5}.rt-axis{stroke:#111;stroke-width:2.5;fill:none}.rt-tick{stroke:#111;stroke-width:2}.rt-given-pt{fill:#111;stroke:#111;stroke-width:2}.rt-unknown-pt{fill:#ffffff;stroke:#111;stroke-width:2.5;stroke-dasharray:4 3}.rt-rung{stroke:#111;stroke-width:1.5;stroke-dasharray:3 4}.rt-table-line{stroke:#111;stroke-width:2;fill:none}.rt-table-given{fill:#dddddd;stroke:#111;stroke-width:1.5}text{font-family:sans-serif;font-size:26px;fill:#111}.rt-ticklbl{font-size:20px;fill:#333}.rt-lbl{font-size:26px;fill:#111}.rt-unknown-lbl{font-size:28px;font-weight:bold;fill:#111}</style>
<g class="rt-base">
<text class="rt-lbl" x="500" y="56" text-anchor="middle">Bar model: 49 stickers shared in 2:5</text>
<rect class="rt-bar-unknown" data-cell="0" x="80" y="110" width="240" height="90"/>
<text class="rt-lbl" x="200" y="236" text-anchor="middle">Jo (2 parts)</text>
<rect class="rt-bar-unknown" data-cell="1" x="320" y="110" width="600" height="90"/>
<text class="rt-lbl" x="620" y="236" text-anchor="middle">Kim (5 parts)</text>
<rect class="rt-bar-frame" x="80" y="110" width="840" height="90"/>
</g>
<g class="rt-student">
<text class="rt-unknown-lbl" x="200" y="172" text-anchor="middle">?</text>
<text class="rt-unknown-lbl" x="620" y="172" text-anchor="middle">?</text>
</g>
</svg>
```

</details>
<details><summary>answer-key figure (SVG)</summary>

```xml
<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1000 300" role="img" aria-label="Answer key. A bar model for the ratio 2:5. The solved quantities are shown.">
<title>Bar model</title><desc>A bar model for the ratio 2:5. The solution overlay reveals the answer to: Share 49 stickers between Jo, Kim in the ratio 2:5. Give each share.</desc>
<style>.rt-bar-given{fill:#dddddd;stroke:#111;stroke-width:2}.rt-bar-unknown{fill:#ffffff;stroke:#111;stroke-width:2;stroke-dasharray:6 4}.rt-bar-frame{fill:none;stroke:#111;stroke-width:2.5}.rt-divider{stroke:#111;stroke-width:1.5}.rt-axis{stroke:#111;stroke-width:2.5;fill:none}.rt-tick{stroke:#111;stroke-width:2}.rt-given-pt{fill:#111;stroke:#111;stroke-width:2}.rt-unknown-pt{fill:#ffffff;stroke:#111;stroke-width:2.5;stroke-dasharray:4 3}.rt-rung{stroke:#111;stroke-width:1.5;stroke-dasharray:3 4}.rt-table-line{stroke:#111;stroke-width:2;fill:none}.rt-table-given{fill:#dddddd;stroke:#111;stroke-width:1.5}text{font-family:sans-serif;font-size:26px;fill:#111}.rt-ticklbl{font-size:20px;fill:#333}.rt-lbl{font-size:26px;fill:#111}.rt-unknown-lbl{font-size:28px;font-weight:bold;fill:#111}</style>
<g class="rt-base">
<text class="rt-lbl" x="500" y="56" text-anchor="middle">Bar model: 49 stickers shared in 2:5</text>
<rect class="rt-bar-unknown" data-cell="0" x="80" y="110" width="240" height="90"/>
<text class="rt-lbl" x="200" y="236" text-anchor="middle">Jo (2 parts)</text>
<rect class="rt-bar-unknown" data-cell="1" x="320" y="110" width="600" height="90"/>
<text class="rt-lbl" x="620" y="236" text-anchor="middle">Kim (5 parts)</text>
<rect class="rt-bar-frame" x="80" y="110" width="840" height="90"/>
</g>
<g class="rt-overlay">
<text class="rt-unknown-lbl" x="200" y="172" text-anchor="middle">14</text>
<text class="rt-unknown-lbl" x="620" y="172" text-anchor="middle">35</text>
</g>
</svg>
```

</details>

## simple_scale — seed 36 — band 4 (exact-rational, free-response)

| field | value |
|---|---|
| objective | SPI.MIDDLE.RATIO.SIMPLE_SCALE.01 |
| interaction / answer | free-response / exact-rational |
| difficulty band | 4 (axes: {"numericalComplexity": 0.65, "exactVsApproximate": 0, "reasoningSteps": 0.6, "abstraction": 0.6}) |
| prompt | On a map, 2 map units represent 3 ground units. A part measures 17 map units. How many ground units long is it in reality? Give an exact value. |
| params | `{"task": "simple_scale", "scaleKind": "map", "srcUnit": "map unit", "dstUnit": "ground unit", "value": 17, "factorNum": 3, "factorDen": 2, "direction": "multiply"}` |
| canonical answer | `{"num": 51, "den": 2}` |
| answer display | 51/2 |
| accepted form / checker | Exact-rational checker: the answer is the exact reduced Fraction (num/den); no float, no tolerance; integer-when-whole carries den 1. |
| worked solution | 1. Find the scale factor -> 3/2; 2. Multiply the value by the scale factor -> 17 × 3/2 = 51/2 |
| student alt text | A double number line aligning the two proportional quantities. On a map, 2 map units represent 3 ground units. A part measures 17 map units. How many ground units long is it in reality? Give an exact value. |
| answer-key alt text | Answer key. A double number line aligning the two proportional quantities. The solved quantities are shown. |
| student data table | `{"columns": ["map unit", "ground unit"], "rows": [["2", "3"], ["17", "?"]]}` |
| answer-key data table | `{"columns": ["map unit", "ground unit"], "rows": [["2", "3"], ["17", "51/2"]]}` |
| diagnostics exercised | MISC.RATIO.SCALE_WRONG_DIRECTION, MISC.RATIO.ADDITIVE_NOT_MULTIPLICATIVE |
| validation checks | 31/31 pass |
| covers cells | 1 |
| reproduction | `python -c "import sys; sys.path.insert(0,'oracle'); from spi_oracle import ratio as R; print(R.serialize(R.generate(36, {'task': 'simple_scale'})))"` |
| curriculum-review decision | ☐ APPROVE ☐ REVISE ☐ REJECT |

<details><summary>student figure (SVG)</summary>

```xml
<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1000 260" role="img" aria-label="A double number line aligning the two proportional quantities. On a map, 2 map units represent 3 ground units. A part measures 17 map units. How many ground units long is it in reality? Give an exact value.">
<title>Double number line</title><desc>A double number line aligning the two proportional quantities. Unknown quantities are marked with a question mark. On a map, 2 map units represent 3 ground units. A part measures 17 map units. How many ground units long is it in reality? Give an exact value.</desc>
<style>.rt-bar-given{fill:#dddddd;stroke:#111;stroke-width:2}.rt-bar-unknown{fill:#ffffff;stroke:#111;stroke-width:2;stroke-dasharray:6 4}.rt-bar-frame{fill:none;stroke:#111;stroke-width:2.5}.rt-divider{stroke:#111;stroke-width:1.5}.rt-axis{stroke:#111;stroke-width:2.5;fill:none}.rt-tick{stroke:#111;stroke-width:2}.rt-given-pt{fill:#111;stroke:#111;stroke-width:2}.rt-unknown-pt{fill:#ffffff;stroke:#111;stroke-width:2.5;stroke-dasharray:4 3}.rt-rung{stroke:#111;stroke-width:1.5;stroke-dasharray:3 4}.rt-table-line{stroke:#111;stroke-width:2;fill:none}.rt-table-given{fill:#dddddd;stroke:#111;stroke-width:1.5}text{font-family:sans-serif;font-size:26px;fill:#111}.rt-ticklbl{font-size:20px;fill:#333}.rt-lbl{font-size:26px;fill:#111}.rt-unknown-lbl{font-size:28px;font-weight:bold;fill:#111}</style>
<g class="rt-base">
<text class="rt-lbl" x="500" y="52" text-anchor="middle">Double number line</text>
<line class="rt-axis" x1="120" y1="110" x2="880" y2="110"/>
<line class="rt-axis" x1="120" y1="200" x2="880" y2="200"/>
<text class="rt-lbl" x="104" y="118" text-anchor="end">map unit</text>
<text class="rt-lbl" x="104" y="208" text-anchor="end">ground unit</text>
<line class="rt-rung" x1="373" y1="110" x2="373" y2="200"/>
<circle class="rt-given-pt" cx="373" cy="110" r="6"/>
<text class="rt-ticklbl" x="373" y="96" text-anchor="middle">2</text>
<circle class="rt-given-pt" cx="373" cy="200" r="6"/>
<text class="rt-ticklbl" x="373" y="236" text-anchor="middle">3</text>
<line class="rt-rung" x1="626" y1="110" x2="626" y2="200"/>
<circle class="rt-given-pt" cx="626" cy="110" r="6"/>
<text class="rt-ticklbl" x="626" y="96" text-anchor="middle">17</text>
<circle class="rt-unknown-pt" cx="626" cy="200" r="7"/>
</g>
<g class="rt-student">
<text class="rt-unknown-lbl" x="626" y="236" text-anchor="middle">?</text>
</g>
</svg>
```

</details>
<details><summary>answer-key figure (SVG)</summary>

```xml
<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1000 260" role="img" aria-label="Answer key. A double number line aligning the two proportional quantities. The solved quantities are shown.">
<title>Double number line</title><desc>A double number line aligning the two proportional quantities. The solution overlay reveals the answer to: On a map, 2 map units represent 3 ground units. A part measures 17 map units. How many ground units long is it in reality? Give an exact value.</desc>
<style>.rt-bar-given{fill:#dddddd;stroke:#111;stroke-width:2}.rt-bar-unknown{fill:#ffffff;stroke:#111;stroke-width:2;stroke-dasharray:6 4}.rt-bar-frame{fill:none;stroke:#111;stroke-width:2.5}.rt-divider{stroke:#111;stroke-width:1.5}.rt-axis{stroke:#111;stroke-width:2.5;fill:none}.rt-tick{stroke:#111;stroke-width:2}.rt-given-pt{fill:#111;stroke:#111;stroke-width:2}.rt-unknown-pt{fill:#ffffff;stroke:#111;stroke-width:2.5;stroke-dasharray:4 3}.rt-rung{stroke:#111;stroke-width:1.5;stroke-dasharray:3 4}.rt-table-line{stroke:#111;stroke-width:2;fill:none}.rt-table-given{fill:#dddddd;stroke:#111;stroke-width:1.5}text{font-family:sans-serif;font-size:26px;fill:#111}.rt-ticklbl{font-size:20px;fill:#333}.rt-lbl{font-size:26px;fill:#111}.rt-unknown-lbl{font-size:28px;font-weight:bold;fill:#111}</style>
<g class="rt-base">
<text class="rt-lbl" x="500" y="52" text-anchor="middle">Double number line</text>
<line class="rt-axis" x1="120" y1="110" x2="880" y2="110"/>
<line class="rt-axis" x1="120" y1="200" x2="880" y2="200"/>
<text class="rt-lbl" x="104" y="118" text-anchor="end">map unit</text>
<text class="rt-lbl" x="104" y="208" text-anchor="end">ground unit</text>
<line class="rt-rung" x1="373" y1="110" x2="373" y2="200"/>
<circle class="rt-given-pt" cx="373" cy="110" r="6"/>
<text class="rt-ticklbl" x="373" y="96" text-anchor="middle">2</text>
<circle class="rt-given-pt" cx="373" cy="200" r="6"/>
<text class="rt-ticklbl" x="373" y="236" text-anchor="middle">3</text>
<line class="rt-rung" x1="626" y1="110" x2="626" y2="200"/>
<circle class="rt-given-pt" cx="626" cy="110" r="6"/>
<text class="rt-ticklbl" x="626" y="96" text-anchor="middle">17</text>
<circle class="rt-unknown-pt" cx="626" cy="200" r="7"/>
</g>
<g class="rt-overlay">
<text class="rt-unknown-lbl" x="626" y="236" text-anchor="middle">51/2</text>
</g>
</svg>
```

</details>

## best_buy — seed 41 — band 4 (multiple-choice, multiple-choice)

| field | value |
|---|---|
| objective | SPI.MIDDLE.RATIO.BEST_BUY.01 |
| interaction / answer | multiple-choice / multiple-choice |
| difficulty band | 4 (axes: {"numericalComplexity": 0.4, "exactVsApproximate": 0, "reasoningSteps": 0.8, "abstraction": 0.7}) |
| prompt | You can buy notebooks: option A offers 18 notebooks for 11 tokens; option B offers 16 notebooks for 12 tokens; option C offers 15 notebooks for 2 tokens. Which option is the best value (the lowest cost per notebook)? Choose the best option. |
| params | `{"task": "best_buy", "items": "notebooks", "item": "notebook", "options": [{"label": "A", "itemCount": 18, "tokenCost": 11, "unitRate": {"num": 11, "den": 18}}, {"label": "B", "itemCount": 16, "tokenCost": 12, "unitRate": {"num": 12, "den": 16}}, {"label": "C", "itemCount": 15, "tokenCost": 2, "unitRate": {"num": 2, "den": 15}}], "correctLabel": "C"}` |
| canonical answer | `"C"` |
| answer display | C |
| accepted form / checker | Best-buy choice checker: the selected labelled option id is the answer; the correct option is the UNIQUE strict-minimum exact unit rate. A single letter A/B/C is parsed; anything else is malformed-response and a wrong letter is wrong-choice. |
| worked solution | 1. Cost per notebook of option A -> 11 tokens ÷ 18 notebooks = 11/18 tokens per notebook; 2. Cost per notebook of option B -> 12 tokens ÷ 16 notebooks = 3/4 tokens per notebook; 3. Cost per notebook of option C -> 2 tokens ÷ 15 notebooks = 2/15 tokens per notebook; 4. Compare the cost per item and choose the strict minimum -> the lowest cost per notebook is 2/15 -> option C |
| student alt text | A comparison table of each option's item count and token cost. You can buy notebooks: option A offers 18 notebooks for 11 tokens; option B offers 16 notebooks for 12 tokens; option C offers 15 notebooks for 2 tokens. Which option is the best value (the lowest cost per notebook)? Choose the best option. |
| answer-key alt text | Answer key. A comparison table of each option's item count and token cost. The solved quantities are shown. |
| student data table | `{"columns": ["Option", "Notebooks", "Tokens"], "rows": [["A", "18", "11"], ["B", "16", "12"], ["C", "15", "2"]]}` |
| answer-key data table | `{"columns": ["Option", "Notebooks", "Tokens", "Cost per notebook (tokens)"], "rows": [["A", "18", "11", "11/18"], ["B", "16", "12", "3/4"], ["C", "15", "2", "2/15 (best)"]]}` |
| MC options | A=18 notebooks for 11 tokens; B=16 notebooks for 12 tokens; C=15 notebooks for 2 tokens ✓ |
| diagnostics exercised | MISC.RATIO.NO_UNIT_RATE_COMPARE |
| validation checks | 31/31 pass |
| covers cells | 1 |
| reproduction | `python -c "import sys; sys.path.insert(0,'oracle'); from spi_oracle import ratio as R; print(R.serialize(R.generate(41, {'task': 'best_buy'})))"` |
| curriculum-review decision | ☐ APPROVE ☐ REVISE ☐ REJECT |

<details><summary>student figure (SVG)</summary>

```xml
<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1000 300" role="img" aria-label="A comparison table of each option&#39;s item count and token cost. You can buy notebooks: option A offers 18 notebooks for 11 tokens; option B offers 16 notebooks for 12 tokens; option C offers 15 notebooks for 2 tokens. Which option is the best value (the lowest cost per notebook)? Choose the best option.">
<title>Best-buy comparison table</title><desc>A comparison table of each option&#39;s item count and token cost. Unknown quantities are marked with a question mark. You can buy notebooks: option A offers 18 notebooks for 11 tokens; option B offers 16 notebooks for 12 tokens; option C offers 15 notebooks for 2 tokens. Which option is the best value (the lowest cost per notebook)? Choose the best option.</desc>
<style>.rt-bar-given{fill:#dddddd;stroke:#111;stroke-width:2}.rt-bar-unknown{fill:#ffffff;stroke:#111;stroke-width:2;stroke-dasharray:6 4}.rt-bar-frame{fill:none;stroke:#111;stroke-width:2.5}.rt-divider{stroke:#111;stroke-width:1.5}.rt-axis{stroke:#111;stroke-width:2.5;fill:none}.rt-tick{stroke:#111;stroke-width:2}.rt-given-pt{fill:#111;stroke:#111;stroke-width:2}.rt-unknown-pt{fill:#ffffff;stroke:#111;stroke-width:2.5;stroke-dasharray:4 3}.rt-rung{stroke:#111;stroke-width:1.5;stroke-dasharray:3 4}.rt-table-line{stroke:#111;stroke-width:2;fill:none}.rt-table-given{fill:#dddddd;stroke:#111;stroke-width:1.5}text{font-family:sans-serif;font-size:26px;fill:#111}.rt-ticklbl{font-size:20px;fill:#333}.rt-lbl{font-size:26px;fill:#111}.rt-unknown-lbl{font-size:28px;font-weight:bold;fill:#111}</style>
<g class="rt-base">
<text class="rt-lbl" x="500" y="48" text-anchor="middle">Compare the options by cost per item</text>
<line class="rt-table-line" x1="80" y1="80" x2="920" y2="80"/>
<line class="rt-table-line" x1="80" y1="136" x2="920" y2="136"/>
<line class="rt-table-line" x1="80" y1="192" x2="920" y2="192"/>
<line class="rt-table-line" x1="80" y1="248" x2="920" y2="248"/>
<line class="rt-table-line" x1="80" y1="304" x2="920" y2="304"/>
<line class="rt-table-line" x1="80" y1="80" x2="80" y2="304"/>
<line class="rt-table-line" x1="290" y1="80" x2="290" y2="304"/>
<line class="rt-table-line" x1="500" y1="80" x2="500" y2="304"/>
<line class="rt-table-line" x1="710" y1="80" x2="710" y2="304"/>
<line class="rt-table-line" x1="920" y1="80" x2="920" y2="304"/>
<text class="rt-ticklbl" x="92" y="116" text-anchor="start">Option</text>
<text class="rt-ticklbl" x="92" y="172" text-anchor="start">Notebooks</text>
<text class="rt-ticklbl" x="92" y="228" text-anchor="start">Tokens</text>
<text class="rt-ticklbl" x="92" y="284" text-anchor="start">Cost per notebook (tokens)</text>
<text class="rt-lbl" x="395" y="116" text-anchor="middle">A</text>
<text class="rt-lbl" x="395" y="172" text-anchor="middle">18</text>
<text class="rt-lbl" x="395" y="228" text-anchor="middle">11</text>
<text class="rt-lbl" x="605" y="116" text-anchor="middle">B</text>
<text class="rt-lbl" x="605" y="172" text-anchor="middle">16</text>
<text class="rt-lbl" x="605" y="228" text-anchor="middle">12</text>
<text class="rt-lbl" x="815" y="116" text-anchor="middle">C</text>
<text class="rt-lbl" x="815" y="172" text-anchor="middle">15</text>
<text class="rt-lbl" x="815" y="228" text-anchor="middle">2</text>
</g>
<g class="rt-student">
<text class="rt-unknown-lbl" x="395" y="284" text-anchor="middle">?</text>
<text class="rt-unknown-lbl" x="605" y="284" text-anchor="middle">?</text>
<text class="rt-unknown-lbl" x="815" y="284" text-anchor="middle">?</text>
</g>
</svg>
```

</details>
<details><summary>answer-key figure (SVG)</summary>

```xml
<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1000 300" role="img" aria-label="Answer key. A comparison table of each option&#39;s item count and token cost. The solved quantities are shown.">
<title>Best-buy comparison table</title><desc>A comparison table of each option&#39;s item count and token cost. The solution overlay reveals the answer to: You can buy notebooks: option A offers 18 notebooks for 11 tokens; option B offers 16 notebooks for 12 tokens; option C offers 15 notebooks for 2 tokens. Which option is the best value (the lowest cost per notebook)? Choose the best option.</desc>
<style>.rt-bar-given{fill:#dddddd;stroke:#111;stroke-width:2}.rt-bar-unknown{fill:#ffffff;stroke:#111;stroke-width:2;stroke-dasharray:6 4}.rt-bar-frame{fill:none;stroke:#111;stroke-width:2.5}.rt-divider{stroke:#111;stroke-width:1.5}.rt-axis{stroke:#111;stroke-width:2.5;fill:none}.rt-tick{stroke:#111;stroke-width:2}.rt-given-pt{fill:#111;stroke:#111;stroke-width:2}.rt-unknown-pt{fill:#ffffff;stroke:#111;stroke-width:2.5;stroke-dasharray:4 3}.rt-rung{stroke:#111;stroke-width:1.5;stroke-dasharray:3 4}.rt-table-line{stroke:#111;stroke-width:2;fill:none}.rt-table-given{fill:#dddddd;stroke:#111;stroke-width:1.5}text{font-family:sans-serif;font-size:26px;fill:#111}.rt-ticklbl{font-size:20px;fill:#333}.rt-lbl{font-size:26px;fill:#111}.rt-unknown-lbl{font-size:28px;font-weight:bold;fill:#111}</style>
<g class="rt-base">
<text class="rt-lbl" x="500" y="48" text-anchor="middle">Compare the options by cost per item</text>
<line class="rt-table-line" x1="80" y1="80" x2="920" y2="80"/>
<line class="rt-table-line" x1="80" y1="136" x2="920" y2="136"/>
<line class="rt-table-line" x1="80" y1="192" x2="920" y2="192"/>
<line class="rt-table-line" x1="80" y1="248" x2="920" y2="248"/>
<line class="rt-table-line" x1="80" y1="304" x2="920" y2="304"/>
<line class="rt-table-line" x1="80" y1="80" x2="80" y2="304"/>
<line class="rt-table-line" x1="290" y1="80" x2="290" y2="304"/>
<line class="rt-table-line" x1="500" y1="80" x2="500" y2="304"/>
<line class="rt-table-line" x1="710" y1="80" x2="710" y2="304"/>
<line class="rt-table-line" x1="920" y1="80" x2="920" y2="304"/>
<text class="rt-ticklbl" x="92" y="116" text-anchor="start">Option</text>
<text class="rt-ticklbl" x="92" y="172" text-anchor="start">Notebooks</text>
<text class="rt-ticklbl" x="92" y="228" text-anchor="start">Tokens</text>
<text class="rt-ticklbl" x="92" y="284" text-anchor="start">Cost per notebook (tokens)</text>
<text class="rt-lbl" x="395" y="116" text-anchor="middle">A</text>
<text class="rt-lbl" x="395" y="172" text-anchor="middle">18</text>
<text class="rt-lbl" x="395" y="228" text-anchor="middle">11</text>
<text class="rt-lbl" x="605" y="116" text-anchor="middle">B</text>
<text class="rt-lbl" x="605" y="172" text-anchor="middle">16</text>
<text class="rt-lbl" x="605" y="228" text-anchor="middle">12</text>
<text class="rt-lbl" x="815" y="116" text-anchor="middle">C</text>
<text class="rt-lbl" x="815" y="172" text-anchor="middle">15</text>
<text class="rt-lbl" x="815" y="228" text-anchor="middle">2</text>
</g>
<g class="rt-overlay">
<text class="rt-unknown-lbl" x="395" y="284" text-anchor="middle">11/18</text>
<text class="rt-unknown-lbl" x="605" y="284" text-anchor="middle">3/4</text>
<text class="rt-unknown-lbl" x="815" y="284" text-anchor="middle">2/15 ✓</text>
</g>
</svg>
```

</details>

## unit_rate — seed 69 — band 3 (exact-rational, free-response)

| field | value |
|---|---|
| objective | SPI.MIDDLE.RATIO.UNIT_RATE.01 |
| interaction / answer | free-response / exact-rational |
| difficulty band | 3 (axes: {"numericalComplexity": 0.65, "exactVsApproximate": 0, "reasoningSteps": 0.55, "abstraction": 0.5}) |
| prompt | 4 sacks hold 34 kilograms. How many kilograms per sack? Give an exact value. |
| params | `{"task": "unit_rate", "amountLabel": "kilograms", "perLabel": "sacks", "total": 34, "quantity": 4}` |
| canonical answer | `{"num": 17, "den": 2}` |
| answer display | 17/2 |
| accepted form / checker | Exact-rational checker: the answer is the exact reduced Fraction (num/den); no float, no tolerance; integer-when-whole carries den 1. |
| worked solution | 1. Divide the total by the number of units -> 34 ÷ 4 = 17/2 |
| student alt text | A double number line aligning the two proportional quantities. 4 sacks hold 34 kilograms. How many kilograms per sack? Give an exact value. |
| answer-key alt text | Answer key. A double number line aligning the two proportional quantities. The solved quantities are shown. |
| student data table | `{"columns": ["sacks", "kilograms"], "rows": [["4", "34"], ["1", "?"]]}` |
| answer-key data table | `{"columns": ["sacks", "kilograms"], "rows": [["4", "34"], ["1", "17/2"]]}` |
| diagnostics exercised | MISC.RATIO.DIVIDES_NOT_MULTIPLIES_UNITARY |
| validation checks | 24/24 pass |
| covers cells | 1 |
| reproduction | `python -c "import sys; sys.path.insert(0,'oracle'); from spi_oracle import ratio as R; print(R.serialize(R.generate(69, {'task': 'unit_rate'})))"` |
| curriculum-review decision | ☐ APPROVE ☐ REVISE ☐ REJECT |

<details><summary>student figure (SVG)</summary>

```xml
<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1000 260" role="img" aria-label="A double number line aligning the two proportional quantities. 4 sacks hold 34 kilograms. How many kilograms per sack? Give an exact value.">
<title>Double number line</title><desc>A double number line aligning the two proportional quantities. Unknown quantities are marked with a question mark. 4 sacks hold 34 kilograms. How many kilograms per sack? Give an exact value.</desc>
<style>.rt-bar-given{fill:#dddddd;stroke:#111;stroke-width:2}.rt-bar-unknown{fill:#ffffff;stroke:#111;stroke-width:2;stroke-dasharray:6 4}.rt-bar-frame{fill:none;stroke:#111;stroke-width:2.5}.rt-divider{stroke:#111;stroke-width:1.5}.rt-axis{stroke:#111;stroke-width:2.5;fill:none}.rt-tick{stroke:#111;stroke-width:2}.rt-given-pt{fill:#111;stroke:#111;stroke-width:2}.rt-unknown-pt{fill:#ffffff;stroke:#111;stroke-width:2.5;stroke-dasharray:4 3}.rt-rung{stroke:#111;stroke-width:1.5;stroke-dasharray:3 4}.rt-table-line{stroke:#111;stroke-width:2;fill:none}.rt-table-given{fill:#dddddd;stroke:#111;stroke-width:1.5}text{font-family:sans-serif;font-size:26px;fill:#111}.rt-ticklbl{font-size:20px;fill:#333}.rt-lbl{font-size:26px;fill:#111}.rt-unknown-lbl{font-size:28px;font-weight:bold;fill:#111}</style>
<g class="rt-base">
<text class="rt-lbl" x="500" y="52" text-anchor="middle">Double number line</text>
<line class="rt-axis" x1="120" y1="110" x2="880" y2="110"/>
<line class="rt-axis" x1="120" y1="200" x2="880" y2="200"/>
<text class="rt-lbl" x="104" y="118" text-anchor="end">sacks</text>
<text class="rt-lbl" x="104" y="208" text-anchor="end">kilograms</text>
<line class="rt-rung" x1="373" y1="110" x2="373" y2="200"/>
<circle class="rt-given-pt" cx="373" cy="110" r="6"/>
<text class="rt-ticklbl" x="373" y="96" text-anchor="middle">4</text>
<circle class="rt-given-pt" cx="373" cy="200" r="6"/>
<text class="rt-ticklbl" x="373" y="236" text-anchor="middle">34</text>
<line class="rt-rung" x1="626" y1="110" x2="626" y2="200"/>
<circle class="rt-given-pt" cx="626" cy="110" r="6"/>
<text class="rt-ticklbl" x="626" y="96" text-anchor="middle">1</text>
<circle class="rt-unknown-pt" cx="626" cy="200" r="7"/>
</g>
<g class="rt-student">
<text class="rt-unknown-lbl" x="626" y="236" text-anchor="middle">?</text>
</g>
</svg>
```

</details>
<details><summary>answer-key figure (SVG)</summary>

```xml
<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1000 260" role="img" aria-label="Answer key. A double number line aligning the two proportional quantities. The solved quantities are shown.">
<title>Double number line</title><desc>A double number line aligning the two proportional quantities. The solution overlay reveals the answer to: 4 sacks hold 34 kilograms. How many kilograms per sack? Give an exact value.</desc>
<style>.rt-bar-given{fill:#dddddd;stroke:#111;stroke-width:2}.rt-bar-unknown{fill:#ffffff;stroke:#111;stroke-width:2;stroke-dasharray:6 4}.rt-bar-frame{fill:none;stroke:#111;stroke-width:2.5}.rt-divider{stroke:#111;stroke-width:1.5}.rt-axis{stroke:#111;stroke-width:2.5;fill:none}.rt-tick{stroke:#111;stroke-width:2}.rt-given-pt{fill:#111;stroke:#111;stroke-width:2}.rt-unknown-pt{fill:#ffffff;stroke:#111;stroke-width:2.5;stroke-dasharray:4 3}.rt-rung{stroke:#111;stroke-width:1.5;stroke-dasharray:3 4}.rt-table-line{stroke:#111;stroke-width:2;fill:none}.rt-table-given{fill:#dddddd;stroke:#111;stroke-width:1.5}text{font-family:sans-serif;font-size:26px;fill:#111}.rt-ticklbl{font-size:20px;fill:#333}.rt-lbl{font-size:26px;fill:#111}.rt-unknown-lbl{font-size:28px;font-weight:bold;fill:#111}</style>
<g class="rt-base">
<text class="rt-lbl" x="500" y="52" text-anchor="middle">Double number line</text>
<line class="rt-axis" x1="120" y1="110" x2="880" y2="110"/>
<line class="rt-axis" x1="120" y1="200" x2="880" y2="200"/>
<text class="rt-lbl" x="104" y="118" text-anchor="end">sacks</text>
<text class="rt-lbl" x="104" y="208" text-anchor="end">kilograms</text>
<line class="rt-rung" x1="373" y1="110" x2="373" y2="200"/>
<circle class="rt-given-pt" cx="373" cy="110" r="6"/>
<text class="rt-ticklbl" x="373" y="96" text-anchor="middle">4</text>
<circle class="rt-given-pt" cx="373" cy="200" r="6"/>
<text class="rt-ticklbl" x="373" y="236" text-anchor="middle">34</text>
<line class="rt-rung" x1="626" y1="110" x2="626" y2="200"/>
<circle class="rt-given-pt" cx="626" cy="110" r="6"/>
<text class="rt-ticklbl" x="626" y="96" text-anchor="middle">1</text>
<circle class="rt-unknown-pt" cx="626" cy="200" r="7"/>
</g>
<g class="rt-overlay">
<text class="rt-unknown-lbl" x="626" y="236" text-anchor="middle">17/2</text>
</g>
</svg>
```

</details>

## simple_scale — seed 109 — band 3 (integer, free-response)

| field | value |
|---|---|
| objective | SPI.MIDDLE.RATIO.SIMPLE_SCALE.01 |
| interaction / answer | free-response / integer |
| difficulty band | 3 (axes: {"numericalComplexity": 0.3, "exactVsApproximate": 0, "reasoningSteps": 0.5, "abstraction": 0.5}) |
| prompt | On a map, 2 map units represent 6 ground units. A part measures 8 map units. How many ground units long is it in reality? Give an exact value. |
| params | `{"task": "simple_scale", "scaleKind": "map", "srcUnit": "map unit", "dstUnit": "ground unit", "value": 8, "factorNum": 6, "factorDen": 2, "direction": "multiply"}` |
| canonical answer | `{"num": 24, "den": 1}` |
| answer display | 24 |
| accepted form / checker | Exact-rational checker: the answer is the exact reduced Fraction (num/den); no float, no tolerance; integer-when-whole carries den 1. |
| worked solution | 1. Find the scale factor -> 6/2; 2. Multiply the value by the scale factor -> 8 × 6/2 = 24 |
| student alt text | A double number line aligning the two proportional quantities. On a map, 2 map units represent 6 ground units. A part measures 8 map units. How many ground units long is it in reality? Give an exact value. |
| answer-key alt text | Answer key. A double number line aligning the two proportional quantities. The solved quantities are shown. |
| student data table | `{"columns": ["map unit", "ground unit"], "rows": [["2", "6"], ["8", "?"]]}` |
| answer-key data table | `{"columns": ["map unit", "ground unit"], "rows": [["2", "6"], ["8", "24"]]}` |
| diagnostics exercised | MISC.RATIO.SCALE_WRONG_DIRECTION, MISC.RATIO.ADDITIVE_NOT_MULTIPLICATIVE |
| validation checks | 31/31 pass |
| covers cells | 1 |
| reproduction | `python -c "import sys; sys.path.insert(0,'oracle'); from spi_oracle import ratio as R; print(R.serialize(R.generate(109, {'task': 'simple_scale'})))"` |
| curriculum-review decision | ☐ APPROVE ☐ REVISE ☐ REJECT |

<details><summary>student figure (SVG)</summary>

```xml
<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1000 260" role="img" aria-label="A double number line aligning the two proportional quantities. On a map, 2 map units represent 6 ground units. A part measures 8 map units. How many ground units long is it in reality? Give an exact value.">
<title>Double number line</title><desc>A double number line aligning the two proportional quantities. Unknown quantities are marked with a question mark. On a map, 2 map units represent 6 ground units. A part measures 8 map units. How many ground units long is it in reality? Give an exact value.</desc>
<style>.rt-bar-given{fill:#dddddd;stroke:#111;stroke-width:2}.rt-bar-unknown{fill:#ffffff;stroke:#111;stroke-width:2;stroke-dasharray:6 4}.rt-bar-frame{fill:none;stroke:#111;stroke-width:2.5}.rt-divider{stroke:#111;stroke-width:1.5}.rt-axis{stroke:#111;stroke-width:2.5;fill:none}.rt-tick{stroke:#111;stroke-width:2}.rt-given-pt{fill:#111;stroke:#111;stroke-width:2}.rt-unknown-pt{fill:#ffffff;stroke:#111;stroke-width:2.5;stroke-dasharray:4 3}.rt-rung{stroke:#111;stroke-width:1.5;stroke-dasharray:3 4}.rt-table-line{stroke:#111;stroke-width:2;fill:none}.rt-table-given{fill:#dddddd;stroke:#111;stroke-width:1.5}text{font-family:sans-serif;font-size:26px;fill:#111}.rt-ticklbl{font-size:20px;fill:#333}.rt-lbl{font-size:26px;fill:#111}.rt-unknown-lbl{font-size:28px;font-weight:bold;fill:#111}</style>
<g class="rt-base">
<text class="rt-lbl" x="500" y="52" text-anchor="middle">Double number line</text>
<line class="rt-axis" x1="120" y1="110" x2="880" y2="110"/>
<line class="rt-axis" x1="120" y1="200" x2="880" y2="200"/>
<text class="rt-lbl" x="104" y="118" text-anchor="end">map unit</text>
<text class="rt-lbl" x="104" y="208" text-anchor="end">ground unit</text>
<line class="rt-rung" x1="373" y1="110" x2="373" y2="200"/>
<circle class="rt-given-pt" cx="373" cy="110" r="6"/>
<text class="rt-ticklbl" x="373" y="96" text-anchor="middle">2</text>
<circle class="rt-given-pt" cx="373" cy="200" r="6"/>
<text class="rt-ticklbl" x="373" y="236" text-anchor="middle">6</text>
<line class="rt-rung" x1="626" y1="110" x2="626" y2="200"/>
<circle class="rt-given-pt" cx="626" cy="110" r="6"/>
<text class="rt-ticklbl" x="626" y="96" text-anchor="middle">8</text>
<circle class="rt-unknown-pt" cx="626" cy="200" r="7"/>
</g>
<g class="rt-student">
<text class="rt-unknown-lbl" x="626" y="236" text-anchor="middle">?</text>
</g>
</svg>
```

</details>
<details><summary>answer-key figure (SVG)</summary>

```xml
<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1000 260" role="img" aria-label="Answer key. A double number line aligning the two proportional quantities. The solved quantities are shown.">
<title>Double number line</title><desc>A double number line aligning the two proportional quantities. The solution overlay reveals the answer to: On a map, 2 map units represent 6 ground units. A part measures 8 map units. How many ground units long is it in reality? Give an exact value.</desc>
<style>.rt-bar-given{fill:#dddddd;stroke:#111;stroke-width:2}.rt-bar-unknown{fill:#ffffff;stroke:#111;stroke-width:2;stroke-dasharray:6 4}.rt-bar-frame{fill:none;stroke:#111;stroke-width:2.5}.rt-divider{stroke:#111;stroke-width:1.5}.rt-axis{stroke:#111;stroke-width:2.5;fill:none}.rt-tick{stroke:#111;stroke-width:2}.rt-given-pt{fill:#111;stroke:#111;stroke-width:2}.rt-unknown-pt{fill:#ffffff;stroke:#111;stroke-width:2.5;stroke-dasharray:4 3}.rt-rung{stroke:#111;stroke-width:1.5;stroke-dasharray:3 4}.rt-table-line{stroke:#111;stroke-width:2;fill:none}.rt-table-given{fill:#dddddd;stroke:#111;stroke-width:1.5}text{font-family:sans-serif;font-size:26px;fill:#111}.rt-ticklbl{font-size:20px;fill:#333}.rt-lbl{font-size:26px;fill:#111}.rt-unknown-lbl{font-size:28px;font-weight:bold;fill:#111}</style>
<g class="rt-base">
<text class="rt-lbl" x="500" y="52" text-anchor="middle">Double number line</text>
<line class="rt-axis" x1="120" y1="110" x2="880" y2="110"/>
<line class="rt-axis" x1="120" y1="200" x2="880" y2="200"/>
<text class="rt-lbl" x="104" y="118" text-anchor="end">map unit</text>
<text class="rt-lbl" x="104" y="208" text-anchor="end">ground unit</text>
<line class="rt-rung" x1="373" y1="110" x2="373" y2="200"/>
<circle class="rt-given-pt" cx="373" cy="110" r="6"/>
<text class="rt-ticklbl" x="373" y="96" text-anchor="middle">2</text>
<circle class="rt-given-pt" cx="373" cy="200" r="6"/>
<text class="rt-ticklbl" x="373" y="236" text-anchor="middle">6</text>
<line class="rt-rung" x1="626" y1="110" x2="626" y2="200"/>
<circle class="rt-given-pt" cx="626" cy="110" r="6"/>
<text class="rt-ticklbl" x="626" y="96" text-anchor="middle">8</text>
<circle class="rt-unknown-pt" cx="626" cy="200" r="7"/>
</g>
<g class="rt-overlay">
<text class="rt-unknown-lbl" x="626" y="236" text-anchor="middle">24</text>
</g>
</svg>
```

</details>

## write_from_quantities — seed 135 — band 2 (ratio, free-response)

| field | value |
|---|---|
| objective | SPI.MIDDLE.RATIO.WRITE_FROM_QUANTITIES.01 |
| interaction / answer | free-response / ratio |
| difficulty band | 2 (axes: {"numericalComplexity": 0.3, "exactVsApproximate": 0, "reasoningSteps": 0.35, "abstraction": 0.3}) |
| prompt | In a recipe there are 3 flour, 21 sugar. Write the ratio of flour to sugar in its simplest form. |
| params | `{"task": "write_from_quantities", "title": "Recipe", "labels": ["flour", "sugar"], "unit": "grams", "quantities": [3, 21]}` |
| canonical answer | `{"parts": [1, 7]}` |
| answer display | 1:7 |
| accepted form / checker | Ratio checker (order-sensitive): the canonical simplest-form ordered tuple is the answer; an equivalent form is judged by require_simplest (any equivalent ordered ratio accepted). Reversed order is rejected (wrong-order); a different ratio is wrong-ratio; the wrong number of parts is wrong-number-of-parts; zero/negative/malformed/extra-text/comma/unicode-colon/'to' all map to their named result codes. |
| worked solution | 1. Find the greatest common divisor of the parts -> gcd = 3; 2. Divide every part by the gcd, keeping the order -> 1:7 |
| student alt text | No figure; the data is given in the prompt. In a recipe there are 3 flour, 21 sugar. Write the ratio of flour to sugar in its simplest form. |
| student data table | `{"columns": ["Quantity", "Value"], "rows": [], "note": "no figure for this task; data is given in the prompt"}` |
| diagnostics exercised | MISC.RATIO.REVERSED_ORDER, MISC.RATIO.NOT_SIMPLIFIED |
| validation checks | 11/11 pass |
| covers cells | 1 |
| reproduction | `python -c "import sys; sys.path.insert(0,'oracle'); from spi_oracle import ratio as R; print(R.serialize(R.generate(135, {'task': 'write_from_quantities'})))"` |
| curriculum-review decision | ☐ APPROVE ☐ REVISE ☐ REJECT |

## simplify — seed 453 — band 1 (ratio, free-response)

| field | value |
|---|---|
| objective | SPI.MIDDLE.RATIO.SIMPLIFY.01 |
| interaction / answer | free-response / ratio |
| difficulty band | 1 (axes: {"numericalComplexity": 0.3, "exactVsApproximate": 0, "reasoningSteps": 0.3, "abstraction": 0.25}) |
| prompt | Write the ratio 3:3 in its simplest form. |
| params | `{"task": "simplify", "parts": [3, 3]}` |
| canonical answer | `{"parts": [1, 1]}` |
| answer display | 1:1 |
| accepted form / checker | Ratio checker (order-sensitive): the canonical simplest-form ordered tuple is the answer; an equivalent form is judged by require_simplest (simplest form required). Reversed order is rejected (wrong-order); a different ratio is wrong-ratio; the wrong number of parts is wrong-number-of-parts; zero/negative/malformed/extra-text/comma/unicode-colon/'to' all map to their named result codes. |
| worked solution | 1. Find the greatest common divisor of the parts -> gcd = 3; 2. Divide every part by the gcd, keeping the order -> 1:1 |
| student alt text | No figure; the data is given in the prompt. Write the ratio 3:3 in its simplest form. |
| student data table | `{"columns": ["Quantity", "Value"], "rows": [], "note": "no figure for this task; data is given in the prompt"}` |
| diagnostics exercised | MISC.RATIO.EQUIVALENT_NOT_SIMPLIFIED, MISC.RATIO.ADDS_PARTS_WRONG |
| validation checks | 10/10 pass |
| covers cells | 1 |
| reproduction | `python -c "import sys; sys.path.insert(0,'oracle'); from spi_oracle import ratio as R; print(R.serialize(R.generate(453, {'task': 'simplify'})))"` |
| curriculum-review decision | ☐ APPROVE ☐ REVISE ☐ REJECT |

