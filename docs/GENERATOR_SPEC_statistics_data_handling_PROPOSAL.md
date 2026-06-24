# Generator Specification Proposal — `gen.stats.data-handling` v1.0.0 (Statistics and Data Handling)

> **STATUS: PROPOSAL ONLY — for the owner to APPROVE / REJECT. NO implementation begins until the owner approves.**
> This document proposes — and asks the owner to APPROVE or REJECT as a whole — the **objectives, task scope, data model, chart-type roster, answer/equivalence checkers, misconception registry, difficulty model, validation contract, accessibility model, review-pack plan, versioning, and reusable-vs-family infrastructure** for the first SPI-Math Statistics and Data Handling generator family. **No code, fixtures, objective JSON, SVG, or registry entry is written until the owner approves these objectives / tasks / data-model / chart-types / misconceptions / difficulty / validation / accessibility / review-pack.** Work proceeds **oracle-first** (the independent Python `spi_oracle` is authored and frozen before the TypeScript mirror) and the family is **registered `approvalStatus: pending-review`** — gated out of normal Generator Studio use and out of production exports/samples until a later owner review-pack decision; the initial item lifecycle is the machine-validated `lifecycle.state = generated`. **Every existing platform gate is retained without exception:** deterministic seeded generation (byte-identical Mulberry32 / Python PRNG streams; deterministic redraw); exact `Rational` / integer arithmetic with **no floats and no irrationals in any answer**; independent Python + TypeScript verification with closure-agreement; canonical item + SVG byte-for-byte parity; runtime Ajv schema validation at boundaries; misconception-backed distractors (≥ 3 distinct, rule-recomputed, else deterministic redraw); golden (4-seed) + parity (150 × 2) + 10,000-seed (`SPI_SWEEP`) stability sweeps with reproducibility re-check and a distribution report; accessibility (axe-core 0 critical/serious, WCAG AA) with a data-table fallback for every figure; offline HTML/JSON exports (worksheet / answer-key / solutions, offline KaTeX) with bank-json round-trip; immutable approved-generator fixtures; a generation manifest with blocking artifact-integrity tests. **This family reuses the newly-approved `gen.geometry.coordinate-lines` Cartesian renderer discipline and `core/visual-style/cartesian-theme.{json,ts}` — it does NOT invent a parallel renderer, style layer, or export path.** Bar charts, line graphs, and scatter plots reuse the approved equal-/independent-scale viewport, single `gridRound` projection, axes / gridlines / plotted-point primitives, the per-root `cx-figure` CSS-custom-property style-isolation contract (modes premium / premium-dark / accessible / print), and the `presentationSvg()` / `exportSvg()` materialised 6000 × 4200 (S = 6) high-resolution export. **Every deferred chart type and every deferred statistic is DETERMINISTICALLY EXCLUDED — never silently included** (see §8, §11): no standard deviation / surds, no regression or trend lines, no irrational quartile interpolation; deferred chart types are unreachable from the seeded task loop, not merely undrawn.

## Overview

`gen.stats.data-handling` is proposed as **the next architecture-proving family after `gen.geometry.coordinate-lines`** because it is the first family whose figures are intrinsically **multi-series, data-bearing displays** rather than single geometric constructions: a bar chart, line graph, or scatter plot carries several categories or paired observations at once, where the **same seeded dataset must simultaneously realise the chart, the prompt, the canonical answer, the worked solution, and the accessibility data-table** — proving that one deterministic source of truth can drive a far richer figure under every existing gate. It is also the first family to **consume the newly-approved premium colour / style-isolation / export layer as a reuser rather than its author**: `coordinate-lines` introduced `cartesian-theme` and the per-root `cx-figure` isolation + materialised 6000 × 4200 export contract; Statistics validates that contract by depending on it for genuinely multi-series colour (categories and series that must remain distinguishable by **pattern / label / marker, never colour alone**, and must survive the CVD-safe `accessible` and monochrome-authoritative `print` modes). Sequencing Statistics here is deliberate: it stresses the reusable Cartesian renderer (axes, gridlines, plotted points, independent y-scaling for frequency data) and the approved export/style isolation on **new figure shapes** while every statistic stays **exact** (mean / median / mode / range / single-event probability as exact `Rational` / integer / fraction), so the architecture is proven before any approximate or inferential statistics are ever attempted.

The proposed v1.0.0 scope is the small, fully-exact core of middle-school data handling: **read a value from a bar chart / pictogram / table; complete a frequency table; compute mean / median / mode / range from a small integer data list and from a frequency table; read a value from a line graph; and state a simple single-event probability as an exact fraction** — each backed by a 1:1 micro-objective under a new `statistics` domain and a new data-handling strand, each answered with an **existing** `answer.type` enum value (`integer`, `exact-rational`, `fraction`, `set`, `ordered-pair`, `table-completion`) under an existing `interactionType` (free-response or, where ≥ 3 misconception-backed distractors exist, `multiple-choice`). **No schema change is required:** every answer type and interaction this family needs is already in `question-item.schema.json`, and `domain` / `strand` are free-form strings in `curriculum-objective.schema.json`. Sections 1–15 below develop each decision; this front matter fixes the identifiers, the reuse posture, and the approval gate the owner is being asked to rule on.

## Identifier glossary

| Item | Value (use verbatim) |
| --- | --- |
| Generator id | `gen.stats.data-handling` |
| Generator version | `1.0.0` |
| Validator version | `1.0.0` |
| Stage | `middle-school` |
| Domain (new) | `statistics` (proposed; `data-handling` is the alternative the owner may select — §1 records the choice) |
| Strand (new) | `data-handling-and-probability` (new strand under the new domain; distinct from all existing geometry/algebra/sequences strands) |
| Objective ID pattern | `SPI.MIDDLE.STAT.<TOPIC>[.<MICRO>].NN` (matches `^SPI\.[A-Z0-9]+(\.[A-Z0-9_]+)+\.[0-9]{2}$`) |
| Misconception ID prefix | `MISC.STAT.*` (registry-backed; ≥ 3 distinct per MC-eligible task or deterministic redraw) |
| Answer types used (all already in enum) | `integer`, `exact-rational`, `fraction`, `set`, `ordered-pair`, `table-completion` |
| Interaction types used (already in enum) | `free-response`; `multiple-choice` only where ≥ 3 misconception-backed distractors exist |
| Reused renderer | `gen.geometry.coordinate-lines` Cartesian renderer (`cx-*`, single `gridRound` projection, integer coords, no runtime trig, byte-identical Py ↔ TS) |
| Reused style / export | `core/visual-style/cartesian-theme.{json,ts}` — per-root `cx-figure` custom properties; modes `premium` / `premium-dark` / `accessible` / `print`; `presentationSvg()` / `exportSvg(…, 6000, 4200)` materialised export |
| Reused checkers | `core/answer-checking` exact-rational + ordered-pair (extended with set / list / table-completion checkers as needed, byte-parity Py/TS) |
| Initial registry status | `approvalStatus: pending-review` (gated from normal Studio + production until owner review-pack decision) |
| Initial item lifecycle | `lifecycle.state = generated` (machine-validated) |
| Provenance | `origin: generated`, `rightsStatus: academy-owned` |

**Proposed v1.0.0 chart types (IN) vs DEFERRED (deterministically excluded)**

| Status | Chart / statistic | Note |
| --- | --- | --- |
| IN v1.0.0 | bar chart, pictogram, frequency table, line graph (reading), single-event probability | exact integer frequencies / small integer data list; reuses Cartesian axes + independent y-scale |
| IN v1.0.0 | mean / median / mode / range (from list and from frequency table) | all exact `Rational` / integer / fraction / `set` (mode may be a `set`) |
| DEFERRED | pie chart | exact only if every sector angle is an integer degree; deferred to v1.0.0, candidate for a later version under that constraint |
| DEFERRED | scatter plot (correlation reading) | deferred; the reusable plotted-point layer is proven here but correlation reading awaits a later version |
| DEFERRED | histogram, stem-and-leaf | deferred (grouped-data / display conventions out of v1.0.0 scope) |
| DEFERRED | standard deviation, variance, regression / trend lines, quartiles needing interpolation | excluded by the **exact-only** rule (surds / irrationals / floats forbidden in answers) |

> Each DEFERRED row is **unreachable from the seeded task loop**, not merely undrawn (§8 validator, §11 edge cases): the task enum, the chart-type selector, and the parameter loop have no path that produces a deferred chart or a non-exact statistic; a request for one is rejected, never silently downgraded.

## Table of contents

1. Curriculum placement and objective IDs
2. Objective wording and prerequisites
3. Task-to-objective mapping
4. Data model and parameter model — the single seeded dataset
5. Answer representation and equivalence checkers (set / list / table-completion / exact-rational)
6. Chart types and the SVG renderer contract
7. Reuse of the approved Cartesian renderer + `cartesian-theme` (style isolation + 6000 × 4200 export)
8. Misconception registry proposal (`MISC.STAT.*`)
9. Difficulty model (schema-valid axes; `bandFromScore`)
10. Edge-case and degeneracy policy (deterministic exclusion of deferred charts / statistics)
11. Solver and independent-validator design (recompute + byte-SVG + closure-agreement)
12. Accessibility model (spoken math, data-table fallback, non-colour indicators)
13. Review-pack plan (md/json + per-item SVGs; exporters; a11y axe gate; manifest + integrity tests)
14. Versioning and approval plan (`approvalStatus: pending-review` gating)
15. New reusable vs family-specific infrastructure


---

## 1. Curriculum placement and objective IDs

**Placement.** SPI-Math Middle School → **Statistics & Data Handling** → *Reading data displays and computing summary statistics from exact integer data*. This is the platform's first **`statistics` domain** family. It is positioned immediately after the approved `gen.geometry.coordinate-lines` family on purpose: it is the first family to **consume** the now-approved Cartesian renderer + `cartesian-theme` as a *display dependency* rather than as the thing under proof — bar charts and line graphs reuse the very same axes / ticks / gridlines / plotted-point layer (`cx-` classes, `viewBox 0 0 1000 700`, single `gridRound` round-half-up projection over exact `Rational`/`Fraction`, byte-identical Python ↔ TypeScript canonical SVG) and the same four render modes. No parallel renderer is introduced.

**Identifier structure (stated explicitly).** Every objective ID has the form `SPI.MIDDLE.STAT.<TOPIC>.<MICRO>.01`, decomposed as: `SPI` (academy) · **`MIDDLE` (stage segment — verified: every existing middle-school objectiveId uses `MIDDLE`, never `MS`)** · **`STAT` = the domain segment** · **`<TOPIC>` = the topic segment** (`READ` = reading displays, `FREQ` = frequency tables, `AVG` = averages and spread, `PROB` = single-event probability) · **`<MICRO>` = the micro-skill segment** · `01` (the two-digit ordinal). Every ID matches the schema pattern `^SPI\.[A-Z0-9]+(\.[A-Z0-9_]+)+\.[0-9]{2}$` and the precedent depth of `SPI.MIDDLE.ALG.LINEQ.ONESTEP_MUL.01` / `SPI.MIDDLE.GEO.COORD.GRADIENT_TWO_POINTS.01`, so the five-segment depth is unambiguous to reviewers. `STAT` is the new domain segment, deliberately distinct from `NUM` / `ALG` / `GEO`. **The canonical objectiveId spelling is `SPI.MIDDLE.STAT.<TOPIC>.<MICRO>.01` and is used verbatim everywhere in this proposal (including every other cluster's solver table, coverage matrix, and validator-check text) — `SPI.MS.STATISTICS.*` is NOT used anywhere; the objective-mapping validator compares exact strings, so a stage/domain-segment drift would never match the authored IDs.**

**New domain and strand (proposed, single pinned spelling).** This family introduces the new curriculum **domain `statistics`** and, within it, the new **strand `data-handling-and-probability`** (one spelling, used identically here and in every other section of this proposal — there is no `data-handling-and-summary-statistics` variant; single-event probability O11 is in scope, so the strand name names it). A **curriculum-schema test pins the exact strings `domain: "statistics"` and `strand: "data-handling-and-probability"`** — both `domain` and `strand` are free-string fields in `schemas/curriculum-objective.schema.json` today, so no enum edit is required; the test pins the exact spellings so a typo cannot silently fork the strand. The objectives are authored as new `curriculum/objectives/SPI.MIDDLE.STAT.json` entries (one JSON array), validated by `schemas/curriculum-objective.schema.json`.

**Classification (identical across all objectives unless noted):**

| Field | Value |
|---|---|
| `academy` | `SPI-Math` |
| `programme` | `SPI-Math Middle School` |
| `stage` | `middle-school` |
| `course` | `SPI-Math Middle School Mathematics` |
| `domain` | `statistics` |
| `strand` | `data-handling-and-probability` |
| `unit` | `Data handling and probability` |
| `topic` | per-objective (`reading data displays`, `frequency tables`, `averages and range`, `single-event probability`) |
| `calculatorPolicy` | `calculator-not-required` (all statistics are exact integer / exact-rational — no decimals, no surds) |
| `reviewStatus` | `proposed` (lifecycle below) |
| `version` | `1.0.0` |
| `crossDomainRelationships` | explicit approved objective IDs (per-objective, Section 2) — e.g. `SPI.MIDDLE.NUM.SIGNED_OPERATIONS.01`; never a `SPI.MIDDLE.NUM.*` wildcard. **This is an authoring convention enforced by the new family graph test (below), NOT by the shared `graph-check.ts`, which never inspects `crossDomainRelationships`.** |

**Objective lifecycle (stated explicitly).** All eleven objectives are authored at `reviewStatus: "proposed"` for this pre-owner-decision proposal. The intended progression mirrors the coordinate-lines precedent (the schema documents `approved-for-implementation` as "curriculum-approved and cleared for generator build while the generator itself remains pending-review"): on owner APPROVE-WITH-REVISIONS the curriculum sign-off flips these to **`approved-for-implementation`** so the generator build can proceed while the generator stays `pending-review`; at final approval they become `approved`. **The new bespoke family graph test asserts the CURRENT expected `reviewStatus` (`proposed` at proposal stage, not a hard-coded `approved`)**, so it does not inherit the coordinate-lines graph test's `reviewStatus === 'approved'` assertion verbatim and stays green at every stage.

**v1.0.0 scope decision — eleven micro-objectives, strictly 1:1 with eleven `gen.stats.data-handling` v1.0.0 tasks.** This taxonomy is canonical and is propagated identically through every cluster (objective table, wording blocks, mapping table, generator task enum, misconception eligibility, solver table, coverage matrix, scope statement). **The median / mode / range of a list are three separate tasks and three separate objectives** (a list read-off `read_table_value` is its own task with its own objective), so the task↔objective↔interaction relation is a genuine bijection and the inherited `objective-mapping` check (one `OBJECTIVE_BY_TASK[task]` per task) is well-defined for every task.

The following chart types and statistics are **IN v1.0.0** because each is exact and each reuses an already-approved mechanism: **bar chart, pictogram, table value, line graph** (display reading); **mean, median, mode, range** from a small integer list, and **mean from a frequency table** (exact integer / exact-rational); and **single-event probability** as an exact reduced fraction. The following are **DEFERRED and deterministically excluded** (see Section 3 for the exclusion invariant): **pie chart** (angle 360·f/Σf is not exact-rational-safe for arbitrary frequencies, and sector geometry needs runtime trig the renderer forbids), **histogram with unequal class widths** (frequency-density introduces non-trivial rationals and a different bar semantic), **scatter plot / correlation / line of best fit** (regression needs least-squares and is irrational in general), **stem-and-leaf** (a non-Cartesian layout outside the approved renderer), **set-valued / multi-modal "all modes" and "no mode" reporting** (the `set` answer machinery is moved to the deferred list for v1.0.0 — see Section 2 O8 and Section 3), and **standard deviation / variance / interquartile range / quartiles** (surds or non-half / non-list-element fractional positions). Every deferred type is excluded by construction, never silently emitted.

**The eleven micro-objectives (1:1 with the eleven `gen.stats.data-handling` v1.0.0 tasks). Task spellings here are the single canonical `task` enum used verbatim everywhere:**

| # | objectiveId | topic · subtopic | microSkill | Generator task |
|---|---|---|---|---|
| O1 | `SPI.MIDDLE.STAT.READ.BAR_CHART.01` | reading data displays · read a value from a bar chart | read the frequency of one named category from a single bar chart | `read_bar_chart` |
| O2 | `SPI.MIDDLE.STAT.READ.PICTOGRAM.01` | reading data displays · read a value from a pictogram | read the frequency of one category from a pictogram using its integer key | `read_pictogram` |
| O3 | `SPI.MIDDLE.STAT.READ.TABLE_VALUE.01` | reading data displays · read a value from a data table | read one frequency cell from a given two-row frequency/data table | `read_table_value` |
| O4 | `SPI.MIDDLE.STAT.READ.LINE_GRAPH.01` | reading data displays · read a value from a line graph | read the plotted value at a labelled point on a single line graph | `read_line_graph` |
| O5 | `SPI.MIDDLE.STAT.FREQ.COMPLETE_TABLE.01` | frequency tables · complete a frequency table | fill the missing cell(s) of a frequency table given the total or remaining counts | `complete_frequency_table` |
| O6 | `SPI.MIDDLE.STAT.AVG.MEAN_LIST.01` | averages and range · mean of a list | compute the mean of a small integer data list as an exact integer or exact-rational | `mean_from_list` |
| O7 | `SPI.MIDDLE.STAT.AVG.MEDIAN_LIST.01` | averages and range · median of a list | compute the median of a small integer data list exactly | `median_from_list` |
| O8 | `SPI.MIDDLE.STAT.AVG.MODE_LIST.01` | averages and range · mode of a list | identify the (unique) mode of a small integer data list | `mode_from_list` |
| O9 | `SPI.MIDDLE.STAT.AVG.RANGE_LIST.01` | averages and range · range of a list | compute the range (max − min) of a small integer data list | `range_from_list` |
| O10 | `SPI.MIDDLE.STAT.AVG.MEAN_FREQ_TABLE.01` | averages and range · mean from a frequency table | compute the mean from a frequency table as Σ(x·f)/Σf, exact | `mean_from_freq_table` |
| O11 | `SPI.MIDDLE.STAT.PROB.SINGLE_EVENT.01` | single-event probability · probability of one event | compute the probability of one equally-likely single event as an exact reduced fraction | `single_event_probability` |

**Canonical task→objective map (the `OBJECTIVE_BY_TASK` constant the `objective-mapping` validator keys on):**

```
read_bar_chart            -> SPI.MIDDLE.STAT.READ.BAR_CHART.01       (O1)
read_pictogram            -> SPI.MIDDLE.STAT.READ.PICTOGRAM.01       (O2)
read_table_value          -> SPI.MIDDLE.STAT.READ.TABLE_VALUE.01     (O3)
read_line_graph           -> SPI.MIDDLE.STAT.READ.LINE_GRAPH.01      (O4)
complete_frequency_table  -> SPI.MIDDLE.STAT.FREQ.COMPLETE_TABLE.01  (O5)
mean_from_list            -> SPI.MIDDLE.STAT.AVG.MEAN_LIST.01        (O6)
median_from_list          -> SPI.MIDDLE.STAT.AVG.MEDIAN_LIST.01      (O7)
mode_from_list            -> SPI.MIDDLE.STAT.AVG.MODE_LIST.01        (O8)
range_from_list           -> SPI.MIDDLE.STAT.AVG.RANGE_LIST.01      (O9)
mean_from_freq_table      -> SPI.MIDDLE.STAT.AVG.MEAN_FREQ_TABLE.01  (O10)
single_event_probability  -> SPI.MIDDLE.STAT.PROB.SINGLE_EVENT.01    (O11)
```

All eleven enter the curriculum graph at `reviewStatus: proposed`. **No existing objective is modified.** The approved `SPI.MIDDLE.NUM.*`, `SPI.MIDDLE.ALG.*` and `SPI.MIDDLE.GEO.COORD.*` objectives are referenced only as prerequisites / cross-domain links (incoming edges added in *this* family's arrays); their own files are untouched.

> **Reference-integrity note (verified against `curriculum/objectives/*`).**
> - **Authored & approved (safe prerequisite targets, all verified present as `objectiveId` entries):** `SPI.MIDDLE.NUM.SIGNED_OPERATIONS.01`; `SPI.MIDDLE.ALG.INVERSE_OPERATIONS.01`; `SPI.MIDDLE.ALG.EXPAND_BRACKETS.01`; the eight `SPI.MIDDLE.GEO.COORD.*` objectives (`CARTESIAN_PLANE`, `READ_POINT`, `PLOT_POINT`, `GRADIENT_TWO_POINTS`, `MIDPOINT`, `INTERPRET_MX_C`, `EQUATION_FROM_GRAPH`, `EQUATION_FROM_2PTS`); the five `SPI.MIDDLE.ALG.LINEQ.*` objectives; the five `SPI.MIDDLE.GEO.*` angle objectives.
> - **Referenced-but-undefined (dangling) nodes that this family deliberately AVOIDS (verified: referenced in other files' arrays but having no authored `objectiveId`):** `SPI.MIDDLE.NUM.INTEGERS_NUMBER_LINE.01`, `SPI.MIDDLE.ALG.SUBSTITUTION.01`, **`SPI.MIDDLE.ALG.NOTATION_SUBSTITUTION.01`** (referenced as a prerequisite in `SPI.MIDDLE.ALG.FOUNDATIONS.json` yet not authored), `SPI.MIDDLE.GEO.TRIANGLE_CLASSIFY.01`, `SPI.MIDDLE.GEO.ANGLE_MEASURE_NOTATION.01`, and `SPI.MIDDLE.NUM.ORDER_OF_OPERATIONS.01` (the last appears only in `relatedObjectives`, not as a prerequisite, but is likewise unauthored). This family routes **every** prerequisite/cross-domain edge to an authored, approved ID (or to an earlier objective in this same family). It therefore adds **zero new** unresolved-prerequisite warnings.

> **Gate accuracy (corrected — verified against `core/curriculum/graph-check.ts`).** `graph-check.ts` enforces, as **ERRORS** that fail `report.ok`: (a) **no duplicate objectiveIds** and (b) **no prerequisite cycle** (DFS over resolved prerequisite edges only). It treats an **unresolved prerequisite as a non-blocking WARNING** (`report.ok` stays `true` even with a dangling prereq), and it **inspects `prerequisites` only — never `crossDomainRelationships` or `relatedObjectives`.** This family's promise is therefore "adds zero new unresolved-prerequisite **WARNINGS**", not a red/green resolution gate. The cross-domain / authored-target guarantees are enforced by a **new bespoke `stats-data-handling-graph.test.ts`** (modelled on `coordinate-lines-graph.test.ts`) that asserts: the eleven STAT objectives are present; every `prerequisites` AND every `crossDomainRelationships` target resolves to an authored `objectiveId` (this is the part the shared tool does not do); the subgraph is acyclic; and each objective carries the stage-appropriate `reviewStatus`.

---

## 2. Objective wording and prerequisites

Each block below uses `curriculum-objective.schema.json` field names. Shared fields from Section 1 (`academy`, `programme`, `stage`, `course`, `domain: statistics`, `strand: data-handling-and-probability`, `unit`, `calculatorPolicy: calculator-not-required`, `reviewStatus: proposed`, `version: 1.0.0`) are not repeated. `answerTypes` entries are drawn from the platform `answer.type` enum (`question-item.schema.json#/$defs/answerType`) and are **MATHEMATICAL answer types only** — `multiple-choice` is an interaction-support mechanism and is **never** listed in `answerTypes`. `allowedRepresentations` entries are drawn from the objective-schema enum (`symbolic`, `numeric`, `graphical`, `tabular`, `diagram`, `verbal-context`, …). Every objective now also populates `vocabulary`, `notation`, and `commonMisconceptions` (the registry IDs from Cluster B's `core/misconceptions/data-handling.json`, prefix `MISC.STAT.<GROUP>.<NAME>`, the single registry namespace — there is no `MISC.STATS.*` variant), matching the coordinate-lines / sequences precedent where each objective lists its 2–3 associated misconceptions.

**No new foundational prerequisite is needed.** Unlike the coordinate-lines family (which had to author `CARTESIAN_PLANE.01`), every prerequisite this family needs already exists and is approved: directed-number / exact-rational arithmetic (`SPI.MIDDLE.NUM.SIGNED_OPERATIONS.01`, whose `answerTypes` already include `exact-rational`) and Cartesian value reading for the chart-axis tasks (`SPI.MIDDLE.GEO.COORD.READ_POINT.01`, which transitively requires `CARTESIAN_PLANE.01`).

> **Read-off answer-type note (reconciled).** All four read tasks (O1–O4) declare `answerTypes: [integer]` ONLY. There is **no `ordered-pair` read-off variant** in v1.0.0: a category read-off whose value is the integer frequency is a plain `integer`, and a string category label is never representable as the numeric `{x,y}` pair that `checkOrderedPair` requires. Any worked-example or solver text that previously suggested an `ordered-pair` "(category, value)" encoding is dropped to keep each item's `answer.type` within its objective's declared `answerTypes`.

---

**O1 — `SPI.MIDDLE.STAT.READ.BAR_CHART.01`** (task `read_bar_chart`)
- `topic`: reading data displays · `subtopic`: read a value from a bar chart
- `microSkill`: read the frequency of one named category from a single (vertical or horizontal) bar chart with an integer-scaled axis
- `objectiveWording`: "Read the frequency of a named category from a bar chart with a clearly scaled axis."
- `prerequisites`: [`SPI.MIDDLE.GEO.COORD.READ_POINT.01`] — reusing the approved axis/value-reading skill (the bar chart shares the Cartesian frequency axis).
- `successCriteria`: ["Identifies the bar belonging to the named category.", "Reads the bar's height against the scaled frequency axis, including when the value falls between two labelled gridlines (integer scale).", "States the frequency as a whole number."]
- `allowedRepresentations`: [`graphical`, `diagram`, `tabular`, `numeric`]
- `vocabulary`: ["bar chart", "category", "frequency", "axis", "scale"]
- `notation`: ["whole-number frequencies on the count axis"]
- `answerTypes`: [`integer`]
- `commonMisconceptions`: [`MISC.STAT.READ.NEAREST_GRIDLINE`, `MISC.STAT.READ.SCALE_STEP_IS_ONE`, `MISC.STAT.READ.ADJACENT_CATEGORY`]
- `difficultyRange`: {min:1, max:2}

**O2 — `SPI.MIDDLE.STAT.READ.PICTOGRAM.01`** (task `read_pictogram`)
- `topic`: reading data displays · `subtopic`: read a value from a pictogram
- `microSkill`: read the frequency of one category from a pictogram, applying its integer "one symbol = k units" key (whole and half symbols only)
- `objectiveWording`: "Read the frequency of a category from a pictogram, using the key that states how many items each symbol represents."
- `prerequisites`: [`SPI.MIDDLE.NUM.SIGNED_OPERATIONS.01`] — multiplying the symbol count by the integer key.
- `successCriteria`: ["Reads the key (symbol value k, an integer).", "Counts whole and half symbols for the named category.", "Computes frequency = (symbols)·k exactly, where every emitted value is a whole number."]
- `allowedRepresentations`: [`diagram`, `graphical`, `tabular`, `numeric`]
- `vocabulary`: ["pictogram", "key", "symbol", "represents", "frequency"]
- `notation`: ["one symbol = k items (k a positive integer)"]
- `answerTypes`: [`integer`]
- `commonMisconceptions`: [`MISC.STAT.READ.IGNORES_KEY`, `MISC.STAT.READ.HALF_AS_WHOLE`, `MISC.STAT.READ.WRONG_KEY`]
- `difficultyRange`: {min:1, max:3}
- Note: the key `k` and symbol counts are constrained so the product is always a non-negative integer; half-symbols are only drawn when `k` is even (so half a symbol is still an integer). Quarter symbols are deferred.

**O3 — `SPI.MIDDLE.STAT.READ.TABLE_VALUE.01`** (task `read_table_value`)
- `topic`: reading data displays · `subtopic`: read a value from a data table
- `microSkill`: read one named frequency cell from a given two-row frequency / data table
- `objectiveWording`: "Read the frequency of a named category directly from a frequency table."
- `prerequisites`: [`SPI.MIDDLE.NUM.SIGNED_OPERATIONS.01`]
- `successCriteria`: ["Locates the column for the named category.", "Reads the integer frequency in that column.", "States the value as a whole number."]
- `allowedRepresentations`: [`tabular`, `numeric`, `verbal-context`]
- `vocabulary`: ["frequency table", "category", "row", "column", "frequency"]
- `notation`: ["whole-number cell entries"]
- `answerTypes`: [`integer`]
- `commonMisconceptions`: [`MISC.STAT.READ.ADJACENT_CATEGORY`, `MISC.STAT.READ.READS_TOTAL_ROW`, `MISC.STAT.READ.TRANSPOSES_CELL`]
- `difficultyRange`: {min:1, max:2}
- Note: a pure table-lookup task (no chart, no arithmetic) authored to give `read_table_value` its own objective so the 1:1 task↔objective bijection holds; distinct from O5 `complete_frequency_table`, which requires the total-relationship arithmetic.

**O4 — `SPI.MIDDLE.STAT.READ.LINE_GRAPH.01`** (task `read_line_graph`)
- `topic`: reading data displays · `subtopic`: read a value from a line graph
- `microSkill`: read the plotted value at a labelled x-position on a single time-series line graph
- `objectiveWording`: "Read the value shown at a labelled point on a single line graph."
- `prerequisites`: [`SPI.MIDDLE.GEO.COORD.READ_POINT.01`]
- `successCriteria`: ["Locates the labelled x-position on the horizontal axis.", "Follows the plotted line to the marked data point.", "Reads the corresponding value on the integer-scaled vertical axis."]
- `allowedRepresentations`: [`graphical`, `diagram`, `numeric`]
- `vocabulary`: ["line graph", "axis", "plotted point", "value", "time series"]
- `notation`: ["integer-scaled vertical axis; lattice data points"]
- `answerTypes`: [`integer`]
- `commonMisconceptions`: [`MISC.STAT.READ.ADJACENT_POINT`, `MISC.STAT.READ.AXIS_CONFUSION`, `MISC.STAT.READ.SCALE_STEP_IS_ONE`]
- `difficultyRange`: {min:1, max:3}
- Note: only **marked lattice data points** are queried (no interpolation between marks in v1.0.0), so every read value is an exact integer; the line segments reuse the approved `.cx-line` straight-line layer.

**O5 — `SPI.MIDDLE.STAT.FREQ.COMPLETE_TABLE.01`** (task `complete_frequency_table`)
- `topic`: frequency tables · `subtopic`: complete a frequency table
- `microSkill`: fill the missing cell(s) of a frequency table given the total and the remaining counts
- `objectiveWording`: "Complete the missing entries of a frequency table so that the category frequencies sum to the given total."
- `prerequisites`: [`SPI.MIDDLE.NUM.SIGNED_OPERATIONS.01`]
- `successCriteria`: ["Uses the relationship (total = Σ category frequencies) to find a missing frequency.", "Fills every missing cell with a non-negative integer.", "Confirms the completed column sums to the stated total."]
- `allowedRepresentations`: [`tabular`, `numeric`, `verbal-context`]
- `vocabulary`: ["frequency table", "total", "missing value", "sum"]
- `notation`: ["total = sum of category frequencies"]
- `answerTypes`: [`table-completion`, `integer`]
- `commonMisconceptions`: [`MISC.STAT.FREQ.WRONG_DIRECTION`, `MISC.STAT.FREQ.OMITS_CATEGORY`, `MISC.STAT.FREQ.COPIES_TOTAL`]
- `difficultyRange`: {min:1, max:3}
- Note: the canonical answer is a `table-completion` payload (the set of `{cellId → integer}` fills); a single-missing-cell variant additionally exposes an `integer` equivalent so the simplest case can be checked as a plain integer. **`table-completion` is the answer.type only — the `interactionType` is `free-response` (or `multiple-choice` for the single-cell variant); see Section 3.** All cells are non-negative integers by construction.

**O6 — `SPI.MIDDLE.STAT.AVG.MEAN_LIST.01`** (task `mean_from_list`)
- `topic`: averages and range · `subtopic`: mean of a small data list
- `microSkill`: compute the arithmetic mean of a small integer data list as an exact value (Σx / n)
- `objectiveWording`: "Calculate the mean of a small list of whole-number data values, giving the answer exactly."
- `prerequisites`: [`SPI.MIDDLE.NUM.SIGNED_OPERATIONS.01`]
- `successCriteria`: ["Adds all data values correctly.", "Divides the total by the number of values n.", "States the mean as an exact integer or fully reduced fraction (never a rounded decimal)."]
- `allowedRepresentations`: [`numeric`, `tabular`, `verbal-context`]
- `vocabulary`: ["mean", "average", "sum", "data value"]
- `notation`: ["mean = (sum of values) ÷ (number of values)"]
- `answerTypes`: [`integer`, `exact-rational`]
- `commonMisconceptions`: [`MISC.STAT.MEAN.DIVIDE_BY_N_MINUS_ONE`, `MISC.STAT.MEAN.FORGOT_TO_DIVIDE`, `MISC.STAT.MEAN.EQUALS_MEDIAN`]
- `difficultyRange`: {min:2, max:3}
- Note: the mean is `Σx / n` as a reduced `{num, den}`. **The stored `answer.type` follows the computed denominator: `integer` when `den === 1`, `exact-rational` when `den > 1`** — so the inherited answer-type-consistency check (integer ⇔ den 1) passes. No rounding ever occurs.

**O7 — `SPI.MIDDLE.STAT.AVG.MEDIAN_LIST.01`** (task `median_from_list`)
- `topic`: averages and range · `subtopic`: median of a small data list
- `microSkill`: determine the median of a small integer data list exactly
- `objectiveWording`: "Find the median of a small list of whole-number data values."
- `prerequisites`: [`SPI.MIDDLE.NUM.SIGNED_OPERATIONS.01`, `SPI.MIDDLE.STAT.AVG.MEAN_LIST.01`]
- `successCriteria`: ["Orders the data.", "Identifies the middle value (odd n) or the exact mean of the two middle values (even n).", "States the median exactly (integer when the two middle values share parity, half-integer otherwise)."]
- `allowedRepresentations`: [`numeric`, `tabular`, `verbal-context`]
- `vocabulary`: ["median", "ordered list", "middle value"]
- `notation`: ["even n: median = (a + b) ÷ 2 for the two middle values"]
- `answerTypes`: [`integer`, `exact-rational`]
- `commonMisconceptions`: [`MISC.STAT.MEDIAN.UNORDERED_MIDDLE`, `MISC.STAT.MEDIAN.AVERAGES_ENDS`, `MISC.STAT.MEDIAN.EQUALS_MEAN`]
- `difficultyRange`: {min:2, max:4}
- Note: even-n median is `(a+b)/2`, exact with `den ∈ {1,2}`; **the stored `answer.type` is set from the computed denominator (integer when den 1, exact-rational when den 2)** so answer-type-consistency passes — the median is never pinned to `exact-rational` unconditionally. The list always **has spread (max > min)** by the dataset-has-spread gate, so degenerate uniform lists never reach this task.

**O8 — `SPI.MIDDLE.STAT.AVG.MODE_LIST.01`** (task `mode_from_list`)
- `topic`: averages and range · `subtopic`: mode of a small data list
- `microSkill`: identify the single (unique) mode of a small integer data list
- `objectiveWording`: "Find the mode of a small list of whole-number data values."
- `prerequisites`: [`SPI.MIDDLE.NUM.SIGNED_OPERATIONS.01`]
- `successCriteria`: ["Counts how often each value occurs.", "Identifies the value with the greatest frequency.", "States that single value."]
- `allowedRepresentations`: [`numeric`, `tabular`, `verbal-context`]
- `vocabulary`: ["mode", "most frequent", "frequency"]
- `notation`: ["mode = the most frequently occurring value"]
- `answerTypes`: [`integer`]
- `commonMisconceptions`: [`MISC.STAT.MODE.RETURNS_FREQUENCY`, `MISC.STAT.MODE.RETURNS_MAXIMUM`, `MISC.STAT.MODE.RETURNS_MEDIAN`]
- `difficultyRange`: {min:1, max:3}
- Note: **v1.0.0 mode is a single-value `integer` only.** A **unique mode is required** by construction (the mode-unique gate: `maxFreq ≥ secondFreq + 1`), so all-distinct ("no mode") and multi-modal lists are **redrawn / excluded**; there is **no empty-set or all-values "no mode" convention emitted in v1.0.0**. The `set`-valued "all modes" / "no mode" encoding (and its `set` checker) is **DEFERRED** — `set` is not used as an answer.type by any v1.0.0 task. The eligibility row for this task therefore does **not** include any "returns the mode" foil (an adapter returning the mode value cannot back a mode-task distractor); the three distractors are concrete distinct misconceptions (frequency-of-mode, maximum, median).

**O9 — `SPI.MIDDLE.STAT.AVG.RANGE_LIST.01`** (task `range_from_list`)
- `topic`: averages and range · `subtopic`: range of a small data list
- `microSkill`: compute the range (maximum − minimum) of a small integer data list
- `objectiveWording`: "Find the range of a small list of whole-number data values."
- `prerequisites`: [`SPI.MIDDLE.NUM.SIGNED_OPERATIONS.01`]
- `successCriteria`: ["Identifies the maximum and minimum values.", "Computes range = maximum − minimum.", "States the range as a whole number."]
- `allowedRepresentations`: [`numeric`, `tabular`, `verbal-context`]
- `vocabulary`: ["range", "maximum", "minimum", "spread"]
- `notation`: ["range = maximum − minimum"]
- `answerTypes`: [`integer`]
- `commonMisconceptions`: [`MISC.STAT.RANGE.SUMS_ENDS`, `MISC.STAT.RANGE.RETURNS_MAXIMUM`, `MISC.STAT.RANGE.COUNTS_VALUES`]
- `difficultyRange`: {min:1, max:3}
- Note: the dataset-has-spread gate guarantees `max > min`, so the range is a positive integer; **a uniform list (range = 0) is excluded for this task and for O7 median by that same gate, and is only reachable for the mean (O6) and mode (O8) tasks.** No deliberate range = 0 teaching item is emitted in v1.0.0.

**O10 — `SPI.MIDDLE.STAT.AVG.MEAN_FREQ_TABLE.01`** (task `mean_from_freq_table`)
- `topic`: averages and range · `subtopic`: mean from a frequency table
- `microSkill`: compute the mean from a frequency table as Σ(x·f)/Σf, exactly
- `objectiveWording`: "Calculate the mean of a data set presented as a frequency table, giving the answer exactly."
- `prerequisites`: [`SPI.MIDDLE.STAT.AVG.MEAN_LIST.01`, `SPI.MIDDLE.STAT.FREQ.COMPLETE_TABLE.01`]
- `successCriteria`: ["Forms the products x·f for each row.", "Sums the products Σ(x·f) and the frequencies Σf.", "Divides to give the mean as an exact integer or fully reduced fraction."]
- `allowedRepresentations`: [`tabular`, `numeric`, `verbal-context`]
- `vocabulary`: ["frequency table", "weighted mean", "product", "total frequency"]
- `notation`: ["mean = Σ(x·f) ÷ Σf"]
- `answerTypes`: [`integer`, `exact-rational`]
- `commonMisconceptions`: [`MISC.STAT.MEANFT.DIVIDE_BY_ROWS`, `MISC.STAT.MEANFT.IGNORES_FREQUENCY`, `MISC.STAT.MEANFT.UNWEIGHTED_SUM`]
- `difficultyRange`: {min:3, max:4}
- Note: `mean = Σ(x·f) / Σf` as a reduced `{num, den}`; **`Σf ≥ 1`** by construction (a non-empty table), so the mean is always defined and exact, with `answer.type` set from `den` as in O6. **Frequencies are constrained not-all-equal and not all-but-one-zero**, so the ignore-frequency distractor (unweighted mean of the x-values) cannot coincide with the weighted mean (it would otherwise collide when every frequency is equal).

**O11 — `SPI.MIDDLE.STAT.PROB.SINGLE_EVENT.01`** (task `single_event_probability`)
- `topic`: single-event probability · `subtopic`: probability of one equally-likely event
- `microSkill`: compute the probability of one equally-likely single event as an exact reduced fraction in [0, 1]
- `objectiveWording`: "Find the probability of a single event with equally likely outcomes, giving the answer as a fraction in its simplest form."
- `prerequisites`: [`SPI.MIDDLE.NUM.SIGNED_OPERATIONS.01`]
- `successCriteria`: ["Counts the favourable outcomes and the total equally-likely outcomes.", "Forms P(event) = favourable / total.", "Gives the probability as a fully reduced fraction between 0 and 1 inclusive."]
- `allowedRepresentations`: [`numeric`, `tabular`, `diagram`, `verbal-context`]
- `vocabulary`: ["probability", "outcome", "favourable", "equally likely", "event"]
- `notation`: ["P(event) = (favourable outcomes) ÷ (total outcomes)"]
- `answerTypes`: [`fraction`, `exact-rational`]
- `commonMisconceptions`: [`MISC.STAT.PROB.COMPLEMENT`, `MISC.STAT.PROB.ODDS_AS_FRACTION`, `MISC.STAT.PROB.NUM_DENOM_SWAP`]
- `difficultyRange`: {min:2, max:3}
- Note: `total ≥ 1` and `0 ≤ favourable ≤ total` by construction, so `P ∈ [0,1]` is always an exact reduced fraction; `accepts.fraction = true`, `accepts.decimal = false`. **The MC-eligible distractors all lie in [0,1] and differ from the key as exact Rationals** — see Section 3 for the in-range filter and the corrected `odds-as-fraction` rule (`favourable/(total − favourable)`, replacing the never-in-range `total/favourable`). **`diagram` is in `allowedRepresentations` for an optional spinner/region illustration; the probability item carries no Cartesian chart**, and where a diagram is shown it is a non-chart illustration drawn from the same `{favourable, total}` dataset, not a bar/line figure.

**Prerequisite DAG edges added by this family** (child --prereq--> parent; every target is an authored, approved objective or an earlier objective in this same family — there are no new/proposed prerequisite nodes):

```
O1  STAT.READ.BAR_CHART.01       -> SPI.MIDDLE.GEO.COORD.READ_POINT.01   (authored, approved)
O2  STAT.READ.PICTOGRAM.01       -> SPI.MIDDLE.NUM.SIGNED_OPERATIONS.01   (authored, approved)
O3  STAT.READ.TABLE_VALUE.01     -> SPI.MIDDLE.NUM.SIGNED_OPERATIONS.01   (authored, approved)
O4  STAT.READ.LINE_GRAPH.01      -> SPI.MIDDLE.GEO.COORD.READ_POINT.01    (authored, approved)
O5  STAT.FREQ.COMPLETE_TABLE.01  -> SPI.MIDDLE.NUM.SIGNED_OPERATIONS.01   (authored, approved)
O6  STAT.AVG.MEAN_LIST.01        -> SPI.MIDDLE.NUM.SIGNED_OPERATIONS.01   (authored, approved)
O7  STAT.AVG.MEDIAN_LIST.01      -> SPI.MIDDLE.NUM.SIGNED_OPERATIONS.01 ; O6
O8  STAT.AVG.MODE_LIST.01        -> SPI.MIDDLE.NUM.SIGNED_OPERATIONS.01   (authored, approved)
O9  STAT.AVG.RANGE_LIST.01       -> SPI.MIDDLE.NUM.SIGNED_OPERATIONS.01   (authored, approved)
O10 STAT.AVG.MEAN_FREQ_TABLE.01  -> O6 ; O5
O11 STAT.PROB.SINGLE_EVENT.01    -> SPI.MIDDLE.NUM.SIGNED_OPERATIONS.01   (authored, approved)
```

`crossDomainRelationships` (lateral synoptic links, not prerequisites): O1/O4 → `SPI.MIDDLE.GEO.COORD.READ_POINT.01` (shared Cartesian axis reading); O6/O10 → `SPI.MIDDLE.NUM.SIGNED_OPERATIONS.01` (the exact-rational division that produces a mean). Each is an **explicit ID, never a wildcard** — an authoring convention enforced by the new family graph test (which resolves every cross-domain ID to an authored objective), since the shared `graph-check.ts` never inspects `crossDomainRelationships`. The subgraph is acyclic — a clean topological order is O1, O2, O3, O4, O5, O6, O7, O8, O9, O11, O10. **`graph-check.ts` validates the merged graph for duplicate IDs (error) and prerequisite cycles (error) and emits unresolved prerequisites as WARNINGS; this family adds no new unresolved-prerequisite warning** (every target above is authored & approved, or O5/O6 in the same file).

---

## 3. Task-to-objective mapping

The mapping is strictly 1:1 — each of the eleven `gen.stats.data-handling` v1.0.0 tasks realises exactly one objective and each objective is realised by exactly one task, so the inherited `objective-mapping` check (`OBJECTIVE_BY_TASK[task]` single-valued, Section 1) holds for every task. `interactionType` values are drawn ONLY from the item-schema enum `["free-response","multiple-choice","multiple-select","matching","ordering","classification"]`; **`free-response` is the default and the only non-MC interaction used. `table-completion` is NOT an `interactionType` (verified: it is an `answer.type` enum member only) — any item carrying `interactionType:"table-completion"` would fail runtime Ajv schema validation and the inherited `interaction-type` check (which passes only for `free-response`/`multiple-choice`). O5 `complete_frequency_table` therefore carries `interactionType: "free-response"` with `answer.type: "table-completion"`; the new `checkTableCompletion` checker operates on that free-response answer.** No additive `interactionType` schema change is proposed.

**Multiple-choice is an interaction-support mechanism, not an answer type** — the `answer.type` column lists the underlying mathematical answer type, never `multiple-choice`. **MC is offered only where at least three distinct, misconception-backed distractors are pedagogically defensible** (the same registry discipline as the approved families: each distractor is computed from a registry rule, must be **DISTINCT by EXACT Rational equality** — `{num,den}` reduced before comparison, so `2/8` and `1/4` are the same value, never "distinct" — must not equal the answer (also by exact-Rational equality, not display-string equality), and exactly three are required or the seeded param loop redraws). Where three defensible distinct distractors cannot be fielded for a given draw, the item is emitted `free-response`. **An explicitly requested interaction type is never silently changed:** if MC is requested, the generator redraws deterministically until the draw is MC-eligible (it never silently substitutes FR); if FR is requested it is never silently upgraded to MC. The generator's `interactionTypes` for a task are derived solely from its `task.mc` flag (`["free-response","multiple-choice"]` when MC-capable, else `["free-response"]`), matching `core/sdk/generator-module.ts`.

| Task | objectiveId | interactionType(s) | answer.type | MC offered? | Rationale (three distinct misconception-backed distractors; all gated distinct-from-key over exact Rationals) |
|---|---|---|---|---|---|
| `read_bar_chart` | O1 `READ.BAR_CHART.01` | `free-response`, `multiple-choice` | `integer` | Yes | (a) `MISC.STAT.READ.NEAREST_GRIDLINE` reads the nearer labelled line, not the bar top; (b) `MISC.STAT.READ.SCALE_STEP_IS_ONE` treats the scale step as 1 when the axis steps by k>1; (c) `MISC.STAT.READ.ADJACENT_CATEGORY` reads a neighbouring bar. Distinct integers in general position; degenerate equalities redraw. |
| `read_pictogram` | O2 `READ.PICTOGRAM.01` | `free-response`, `multiple-choice` | `integer` | Yes | (a) `MISC.STAT.READ.IGNORES_KEY` returns the symbol count, not count·k; (b) `MISC.STAT.READ.HALF_AS_WHOLE` treats a half-symbol as a whole; (c) `MISC.STAT.READ.WRONG_KEY` uses an off-by-one key. Three distinct integers when k>1 and a half-symbol exists; otherwise FR-eligible (MC pinned ⇒ redraw). |
| `read_table_value` | O3 `READ.TABLE_VALUE.01` | `free-response`, `multiple-choice` | `integer` | Yes | (a) `MISC.STAT.READ.ADJACENT_CATEGORY` reads the neighbouring column; (b) `MISC.STAT.READ.READS_TOTAL_ROW` reads the total instead of the cell; (c) `MISC.STAT.READ.TRANSPOSES_CELL` reads the wrong row. Three distinct integers in general position. |
| `read_line_graph` | O4 `READ.LINE_GRAPH.01` | `free-response`, `multiple-choice` | `integer` | Yes | (a) `MISC.STAT.READ.ADJACENT_POINT` (one x-step off); (b) `MISC.STAT.READ.AXIS_CONFUSION` reads the x-coordinate where y was asked; (c) `MISC.STAT.READ.SCALE_STEP_IS_ONE`. Three distinct integers in general position. |
| `complete_frequency_table` | O5 `FREQ.COMPLETE_TABLE.01` | `free-response` (primary); `multiple-choice` **only for the single-missing-cell variant** | `table-completion` \| `integer` | Single-cell: Yes; multi-cell: **No** | Single missing cell: (a) `MISC.STAT.FREQ.WRONG_DIRECTION` subtracts the wrong way / adds; (b) `MISC.STAT.FREQ.OMITS_CATEGORY` drops one category from the running sum; (c) `MISC.STAT.FREQ.COPIES_TOTAL` copies the total into the cell. Three distinct integers. Multi-cell fills cannot field three *single* defensible distractors, so they are FR with `answer.type: table-completion` only. |
| `mean_from_list` | O6 `AVG.MEAN_LIST.01` | `free-response`, `multiple-choice` | `integer` \| `exact-rational` | Yes | (a) `MISC.STAT.MEAN.DIVIDE_BY_N_MINUS_ONE`; (b) `MISC.STAT.MEAN.FORGOT_TO_DIVIDE` (returns Σx); (c) `MISC.STAT.MEAN.EQUALS_MEDIAN` (returns the middle value). MC gated on **mean ≠ median ≠ Σx as exact Rationals AND the dataset non-uniform** (so the median foil cannot equal the key for symmetric/uniform data); collisions redraw. |
| `median_from_list` | O7 `AVG.MEDIAN_LIST.01` | `free-response`, `multiple-choice` | `integer` \| `exact-rational` | Yes | (a) `MISC.STAT.MEDIAN.UNORDERED_MIDDLE` (middle of the unordered list); (b) `MISC.STAT.MEDIAN.AVERAGES_ENDS` ((min+max)/2); (c) `MISC.STAT.MEDIAN.EQUALS_MEAN`. **MC pre-acceptance gate (exact Rationals): median ≠ (min+max)/2 AND median ≠ middleUnordered(list) AND all three distractors mutually distinct and ≠ key**, because (min+max)/2 equals the median for *every* symmetric or evenly-spaced list (e.g. [2,4,6], [1,3,5,7], [3,3,3]) — a frequent collision, not a rare one. When AVERAGES_ENDS collides it is dropped; the row backfills from EQUALS_MEAN / UNORDERED_MIDDLE so three distinct ids remain, else the item is FR. |
| `mode_from_list` | O8 `AVG.MODE_LIST.01` | `free-response`, `multiple-choice` | `integer` | Yes | (a) `MISC.STAT.MODE.RETURNS_FREQUENCY` returns the count of the mode, not the value; (b) `MISC.STAT.MODE.RETURNS_MAXIMUM`; (c) `MISC.STAT.MODE.RETURNS_MEDIAN`. **No "returns the mode" foil exists** (it would equal the key). Unique mode guaranteed (`maxFreq ≥ secondFreq + 1`); single-value `integer` only — the `set`/multimodal path is deferred and never reachable in v1.0.0. |
| `range_from_list` | O9 `AVG.RANGE_LIST.01` | `free-response`, `multiple-choice` | `integer` | Yes | (a) `MISC.STAT.RANGE.SUMS_ENDS` (max+min); (b) `MISC.STAT.RANGE.RETURNS_MAXIMUM`; (c) `MISC.STAT.RANGE.COUNTS_VALUES` (counts the data instead of subtracting). max>min by the spread gate, so the range is a positive integer and the three foils are distinct in general position. |
| `mean_from_freq_table` | O10 `AVG.MEAN_FREQ_TABLE.01` | `free-response`, `multiple-choice` | `integer` \| `exact-rational` | Yes | (a) `MISC.STAT.MEANFT.DIVIDE_BY_ROWS` (÷ number of categories, not Σf); (b) `MISC.STAT.MEANFT.IGNORES_FREQUENCY` (unweighted mean of the x-values); (c) `MISC.STAT.MEANFT.UNWEIGHTED_SUM`. **MC gated on frequencies not-all-equal** (else IGNORES_FREQUENCY equals the weighted mean) and on the three values being distinct as exact Rationals; collisions redraw. |
| `single_event_probability` | O11 `PROB.SINGLE_EVENT.01` | `free-response`, `multiple-choice` | `fraction` \| `exact-rational` | Yes | (a) `MISC.STAT.PROB.COMPLEMENT` (unfavourable/total = 1−P); (b) `MISC.STAT.PROB.ODDS_AS_FRACTION` = favourable/(total−favourable) — **the corrected single rule, in (0,1) only when favourable < total/2**; (c) `MISC.STAT.PROB.NUM_DENOM_SWAP` (the inverted fraction). **In-range filter: every distractor must lie in [0,1] and differ from P as exact Rationals**; if odds or the swap leaves the unit interval, it is redrawn/backfilled. **MC requires `total` large enough that ≥3 distinct in-range distractors are reachable** (minimum-outcome-space gate), and `favourable = total` (P=1), P=0, and P=1/2 are FR-only endpoint cases an MC request redraws away from. |

**Free-response / non-MC-only summary.** Free-response is the default interaction everywhere and is the only interaction for: **multi-cell `complete_frequency_table`** (`answer.type: table-completion`, no single-value distractors); and the degenerate probability sub-cases of O11 (`P ∈ {0, 1, 1/2}`, where the complement/odds/swap distractors collide or leave [0,1]). In each, an explicit MC request is either rejected as unsupported (multi-cell table) or triggers a deterministic redraw away from the ineligible sub-case (O11 endpoints) — MC is **never** silently downgraded to FR, and FR is never silently upgraded to MC. **There is no `set`-valued task in v1.0.0** (the multi-modal "all modes" encoding is deferred), so the previously-mentioned set-only FR case does not arise.

**Answer-type, checker, and exclusion notes.**

- **No `answer.type` enum edit is required.** Every `answer.type` above (`integer`, `exact-rational`, `fraction`, `table-completion`) is already an enum member of `question-item.schema.json#/$defs/answerType` (verified). **`set` and `list` are NOT used:** `set` is deferred with multi-modal mode, and **`list` is not in the enum at all** (the enum has `sequence` and `ordering` but no `list`) — no task needs an ordered-list answer type, since reads use `integer`, means/medians use `integer`/`exact-rational`, and probability uses `fraction`/`exact-rational`. `multiple-choice` is never used as an `answer.type` (interaction only).
- **New checkers, no schema change.** Only one new checker is needed in v1.0.0: a **`table-completion` checker** (`checkTableCompletion`, cell-by-cell exact-integer agreement keyed by `cellId`, target answer.type `table-completion` — a valid enum member, so **no schema change**). It reuses the `Rational {num,den}` primitives and is mirrored byte-for-byte in the Python oracle. The exact-rational / fraction answers serialise as reduced `{num,den}` (den ≥ 1) and are checked by `core/answer-checking/rational-checker.ts checkExactRational` (which accepts equivalent fractions — so an un-reduced fraction is **not** a distractor; "PROB_UNREDUCED" is not a misconception and is not listed anywhere). The schema's `answer.allOf` `if/then` constraints exist only for `integer` (den 1) and `exact-rational` ({num,den}, den ≥ 1); the `table-completion` canonical `{cells:[{cellId,value:{num,den}}]}` shape is schema-unconstrained free-form and is **validated by the checker only** — this is stated explicitly so no false "schema change" is claimed.
- **Single deterministic dataset as the single source.** For every task the seeded `params` carry one canonical `DataSet` (the field names and `kind` discriminator are pinned once in Cluster B's §4.2 and referenced verbatim by the validator), and that same dataset is the sole source for the rendered chart, the prompt, the answer, the worked solution, and the accessibility `dataTableFallback`. The independent Python + TS verifiers recompute the statistic from `params` (`closure-agreement`, comparing canonicals by **reduced-Rational equality** — a `{num:4,den:1}` mean equals a submitted "4") and assert the canonical SVG is byte-for-byte realised from the same dataset (`svg-realises-data`).
- **A11y data-table fallback needs no schema change.** `media[].dataTableFallback` is typed as a generic `{type:"object"}` in the schema (verified), so the structured (category, frequency) / value-list table stored there is schema-valid as-is.
- **`distractor.rationale` equals the registry `observableError`.** Each emitted distractor's `rationale` is set EQUAL to its misconception's `observableError` string, so the inherited `distractor-rationale-matches` check (which asserts `rationale === MISCONCEPTIONS[id].observableError`) passes. The registry entries (Cluster B §8) supply `description` (required by `misconception.schema.json`), `observableError`, and `feedback`; `domain` is set to **`"statistics"`** (mirroring the curriculum domain and the geometry/linear/sequences precedent), prefix `MISC.STAT.<GROUP>.<NAME>`.

**Inherited coordinate-lines validator checks: inherit / override / replace (this family does NOT take the figure battery verbatim).** The statistics validator runs the inherited closure/provenance/MC gates unchanged but must override three figure checks that cannot transfer:

| Inherited check (coordinate-lines `validate`) | Disposition for statistics | Reason |
|---|---|---|
| `params-in-domain`, `objective-mapping`, `interaction-type`, `answer-type-consistency`, `closure-agreement`, `provenance-complete`, `version-fields-present`, all MC checks (`min-three-distractors`, `distractors-distinct-misconceptions`, `distractor-not-answer`, `distractor-rationale-matches`, `exactly-one-correct`) | **Inherit verbatim** | task→objective is 1:1; answer types are exact Rationals; MC discipline is identical. |
| `tick-labels-integer` | **Inherit, but category strings are NOT emitted as `cx-ticklbl`** | the check scrapes `<text class="cx-ticklbl">` and requires every match to be an integer; category labels are emitted under a new `cx-cat` class ONLY, so `cx-ticklbl` stays all-integer and the check stays green. The count axis still uses `cx-ticklbl` for its integer ticks. |
| `no-answer-label-in-svg` | **REPLACE** with `no-statistic-in-svg` | the inherited check fails any `<text>` containing `,`, `/`, or `=` — but a pictogram key text ("1 picture = 5") contains `=`, and category/unit labels ("km/h", "Year 7, boys") contain `/` and `,`. The replacement predicate is **"no figure `<text>` equals the canonical answer's display string (or any distractor display)"** by string/token equality, NOT the character blocklist. A pinned test asserts a pictogram with key "1 picture = 5" passes and a figure whose `<text>` equals the answer fails. |
| `media-to-scale` | **Apply to bar/line charts only; REPLACE for pictograms with `pictogram-key-exact`** | the inherited check hard-asserts `media[0].toScale === true`. Bar charts and line graphs keep `toScale: true` (height-to-scale). Pictograms are glyph-count figures, not height-to-scale, so they carry `toScale: false` and are instead gated by `pictogram-key-exact` (every glyph count × key = the integer frequency). The two spec passages are reconciled to this single policy. |
| `no-colour-only-information` | **Inherit, with GREYS extended (owner sign-off)** | see palette note below. |
| `svg-realises-data` | **Inherit, restricted to in-scope charts** | recompute covers bar tops, pictogram glyph counts (+ exact partial-glyph clip width), table cells, and line-graph lattice points only. **No pie-sector or scatter-point recomputation branch exists** (those are structurally absent from every dispatch table). |

**Canonical SVG, greyscale palette, and cartesian-theme diff (the concrete, verified changes).**

- **The canonical `media[0].svg` carries the internal unscoped monochrome `<style>` and NO `class="cx-figure"`** (byte-identical discipline to coordinate-lines, where `figure()` emits `<svg … role="img">` + internal `<style>` and never stamps `cx-figure`). `class="cx-figure"` and the per-root `--cx-*` variables are added **only** by `presentationSvg()` / `exportSvg()` at presentation/export time (which strip the canonical `<style>` and stamp the root). The accessibility-envelope canonical form is this un-themed monochrome SVG.
- **Byte-parity Py/TS applies to the canonical `media[0].svg` and to `params`/`answer`/`distractors` only.** The `presentationSvg`/`exportSvg`/render-mode/6000×4200-export theme layer is a **TypeScript-only presentation concern** (`core/visual-style/cartesian-theme.ts` exists only in TS; there is no `cartesian_theme.py`) and is **NOT mirrored in the Python oracle.** The Python oracle emits the canonical monochrome SVG and the statistic; the browser-verification + style-isolation evidence is generated from the TS theme. No Python theme byte-parity is claimed.
- **Export sizing is reused verbatim, not recomputed:** the inherited `exportEnvelope` constant `maxEnvelope = 7680×4320` gives `S = min(floor(7680/1000), floor(4320/700)) = min(7,6) = 6`, hence **6000×4200** — identical to coordinate-lines.
- **Committed greyscale palette + GREYS extension.** The canonical short-hex `STYLE` constant currently uses `#111,#333,#888,#bbb,#fff,#555,#444` and `GREYS = {#111,#333,#444,#555,#888,#bbb,#fff}`. The statistics canonical figure uses **only shades already in GREYS**: `.cx-bar` fill `#bbb`, the bar hatch stroke `#555`, the category text `.cx-cat` fill `#333`, and `.cx-icon` (pictogram glyph) fill `#555`. Because all four are already GREYS members, **`no-colour-only-information` passes with NO change to GREYS** in either language — the family deliberately confines itself to the existing greyscale set rather than introducing a new shade requiring owner sign-off. (Should a future figure need a distinct mid-grey, GREYS would be extended byte-identically in both `coordinate-lines.ts` and `coordinate_lines.py` with owner sign-off; v1.0.0 does not require it.)
- **Concrete `cartesian-theme.json` + canonical `STYLE` diff** (names obey the `resolveCommonCss` regex `var\(--cx-[a-z-]+\)`, i.e. lowercase-and-hyphen only): add three variables `--cx-bar-fill`, `--cx-bar-hatch`, `--cx-cat` to `variables[]`; give each a value in **all four** mode objects (`print`/`premium`/`premium-dark`/`accessible`) — e.g. print `--cx-bar-fill:#bbbbbb; --cx-bar-hatch:#555555; --cx-cat:#333333`, with CVD-safe and dark equivalents for the other three; append `.cx-figure .cx-bar{fill:var(--cx-bar-fill);stroke:var(--cx-bar-hatch);stroke-width:1}`, `.cx-figure .cx-cat{font-size:20px;fill:var(--cx-cat)}`, `.cx-figure .cx-icon{fill:var(--cx-bar-hatch)}` to `commonCss`; and add the **same rules with the canonical short-hex colours** (`#bbb/#555/#333`) to the `STYLE` constant in **both** `coordinate-lines.ts` and `coordinate_lines.py`, kept byte-identical, so `svg-realises-data` parity holds. (Pictogram icons reuse `--cx-bar-hatch`; no separate icon variable is needed.)
- **Id-free hatch.** The bar hatch is drawn as **inline integer-coordinate `<line>` stroke elements clipped to the bar rectangle, in deterministic element order** — NOT an SVG `<pattern id=…>` + `fill="url(#…)"`, which is forbidden by the inherited no-id / no-`url(#…)` canonical-SVG rule. The `bar-pattern-distinct` check inspects these inline hatch lines, not a pattern id. This keeps coordinates integer-only and the no-id invariant intact.

**Probability dataset source (made concrete).** For `single_event_probability` the seeded `params` carry an integer `(favourable, total)` pair drawn so `1 ≤ favourable ≤ total`, `total` is within the bounded outcome-space cap (large enough for MC reachability), and the favourable category is named. **No bar/line chart is rendered for probability** (it is not a Cartesian figure task); an optional non-chart `diagram` (e.g. a labelled spinner/region) may be drawn from the same `{favourable, total}` dataset, consistent with `allowedRepresentations: [..., diagram, ...]` in O11.

**Worked end-to-end example item (schema-valid, O6 `mean_from_list`, exact-rational mean).** Shown so reviewers can confirm the encodings validate against `question-item.schema.json`:

```json
{
  "itemId": "ITEM-stat-mean-list-0001",
  "schemaVersion": "1.0.0",
  "objectiveIds": ["SPI.MIDDLE.STAT.AVG.MEAN_LIST.01"],
  "generatorId": "gen.stats.data-handling",
  "generatorVersion": "1.0.0",
  "seed": 305419896,
  "params": { "task": "mean_from_list", "dataset": { "kind": "list", "values": [3, 5, 8, 4] } },
  "prompt": {
    "instruction": "Find",
    "blocks": [
      { "kind": "text", "text": "Four students scored the following marks out of 10:" },
      { "kind": "math-inline", "latex": "3,\\ 5,\\ 8,\\ 4" },
      { "kind": "text", "text": "Find the mean mark, giving your answer exactly." }
    ]
  },
  "answer": { "type": "exact-rational", "canonical": { "num": 5, "den": 1 }, "display": "5", "accepts": { "fraction": true, "decimal": false } },
  "distractors": [
    { "id": "d1", "value": { "num": 20, "den": 3 }, "display": "\\tfrac{20}{3}", "misconceptionId": "MISC.STAT.MEAN.DIVIDE_BY_N_MINUS_ONE", "rationale": "Answer is the total divided by one fewer than the number of values." },
    { "id": "d2", "value": { "num": 20, "den": 1 }, "display": "20", "misconceptionId": "MISC.STAT.MEAN.FORGOT_TO_DIVIDE", "rationale": "Answer is the sum of the values, not divided by how many there are." },
    { "id": "d3", "value": { "num": 9, "den": 2 }, "display": "\\tfrac{9}{2}", "misconceptionId": "MISC.STAT.MEAN.EQUALS_MEDIAN", "rationale": "Answer is the middle value of the ordered list, not the mean." }
  ],
  "options": [
    { "label": "A", "value": { "num": 5, "den": 1 }, "display": "5", "correct": true },
    { "label": "B", "value": { "num": 20, "den": 3 }, "display": "\\tfrac{20}{3}", "correct": false, "misconceptionId": "MISC.STAT.MEAN.DIVIDE_BY_N_MINUS_ONE" },
    { "label": "C", "value": { "num": 20, "den": 1 }, "display": "20", "correct": false, "misconceptionId": "MISC.STAT.MEAN.FORGOT_TO_DIVIDE" },
    { "label": "D", "value": { "num": 9, "den": 2 }, "display": "\\tfrac{9}{2}", "correct": false, "misconceptionId": "MISC.STAT.MEAN.EQUALS_MEDIAN" }
  ],
  "solution": {
    "steps": [
      { "number": 1, "transformation": "Add the values", "intermediateResult": "3 + 5 + 8 + 4 = 20" },
      { "number": 2, "transformation": "Divide by the count", "intermediateResult": "\\tfrac{20}{4} = 5", "dependsOn": [1], "marks": 1 }
    ]
  },
  "difficulty": { "overallBand": 2, "axes": { "numericalComplexity": 0.25, "reasoningSteps": 0.2, "readingDemand": 0.15, "interpretationDemand": 0.1, "informationDensity": 0.2 } },
  "interactionType": "multiple-choice",
  "calculatorPolicy": "calculator-not-required",
  "estimatedTimeSeconds": 60,
  "media": [],
  "accessibility": { "spokenMath": "Find the mean of three, five, eight and four.", "nonColorIndicators": true },
  "provenance": { "origin": "generated", "rightsStatus": "academy-owned", "originalityNote": "Original parameterized item." },
  "lifecycle": { "state": "machine-validated", "validation": { "status": "pass", "validatorVersion": "1.0.0", "checks": [{ "name": "closure-agreement", "result": "pass" }] } }
}
```

This example exercises the load-bearing encodings: the `exact-rational` canonical `{num,den}` with `den=1` correctly typed `exact-rational` (the value 5 is exact; note where `den=1` and the objective also allows `integer`, the generator may instead store `type:"integer"` per the den-driven rule in O6); distractor `value` objects in the same `{num,den}` family; each `distractor.rationale` equal to its registry `observableError`; the difficulty `axes` drawn only from the closed enum (`numericalComplexity, reasoningSteps, readingDemand, interpretationDemand, informationDensity` — five axes, weights summing to 1.0, all valid closed-enum members; `scaffolding`/`representation`/etc. are deliberately schema-absent, mirroring coordinate-lines emitting four); `interactionType: "multiple-choice"` (a valid enum value); and `media: []` for the no-chart list task. A parallel `table-completion` example (O5) would carry `answer.type:"table-completion"`, `interactionType:"free-response"`, and `canonical:{cells:[{cellId:"c2", value:{num:7,den:1}}]}` validated by `checkTableCompletion`.

**Deferred chart types / statistics are deterministically excluded — never silently included.** The generator's task enum contains exactly the eleven v1.0.0 tasks; there is **no code path** that emits a pie chart, histogram with unequal widths / frequency density, scatter plot / correlation / regression line, stem-and-leaf plot, box plot / IQR / quartiles, standard deviation / variance, or a `set`-valued / multi-modal mode. Any dataset draw that would require a deferred construct fails its acceptance predicate and the seeded param loop redraws (every probability/mean reduction is well-defined, so no surd ever arises; pictogram keys keep every value integral; mode draws keep a unique mode; range/median draws keep spread). The independent Python + TS verifiers assert a `deferred-construct-excluded` invariant per task (no pie sector, no frequency-density bar, no plotted scatter cloud, no regression line, no `set` answer, no surd in any stored value), mirroring the per-task `vertical-line-excluded` split used by coordinate-lines.


---

> **Cross-cluster reconciliation notes for §4–§5 (resolving the task-taxonomy and naming blockers).** These sections are written against ONE canonical task list and require Cluster A (§1–§3) to match it verbatim. (a) **Eleven tasks, eleven objectives, strict 1:1.** O6 `median_mode_range_from_list` is split into three objectives/tasks (`median_from_list`, `mode_from_list`, `range_from_list`) and a `read_table_value` task gets its own objective, giving the bijection the inherited `objective-mapping` check requires (it compares `objectiveIds` to exactly `[OBJECTIVE_BY_TASK[task]]`; verified `domains/geometry/coordinate-lines.ts:811`). The explicit `OBJECTIVE_BY_TASK` analogue is pinned in §4.6. (b) **One spelling per task,** declared once in §4.6 and referenced verbatim everywhere. (c) **`interactionType` is `free-response` for `complete_frequency_table`** — `table-completion` is an `answer.type` only, NOT an `interactionType` (the schema enum is exactly `["free-response","multiple-choice","multiple-select","matching","ordering","classification"]`, verified `schemas/question-item.schema.json:121`; the inherited `interaction-type` check passes only `free-response`/`multiple-choice`, verified line 810). (d) **One `DataSet.kind` vocabulary** (`"frequency" | "list"`) and one field-name set, pinned in §4.2 and used in every validator-check description. (e) **No `answer.type` enum edit, no `interactionType` enum edit, no schema change of any kind** is required by §4–§5: every type used (`integer`, `exact-rational`, `fraction`, `set`-deferred, `ordered-pair`, `table-completion`) is already in the platform `answerType` enum (verified), and `media[].dataTableFallback` is already a free-form object (verified `mediaAsset.dataTableFallback:{type:"object"}`).

## 4. Data model and parameter model

### 4.1 One seeded dataset, five consumers

The family `gen.stats.data-handling` is built on a single rule that every platform gate depends on: **one deterministic seeded `DataSet` is the sole source of truth**, and the chart SVG, the prompt text, the answer, the worked solution, and the accessibility data-table are all *derived projections* of that one object. No consumer ever re-samples the RNG or re-derives a value independently. This is what lets the validator's `svg-realises-data` and `closure-agreement` checks recompute everything from `params` and assert byte-identity, and it is what makes Python/TypeScript byte-parity tractable: parity is required only on the dataset constructor and the projections, not on five parallel pipelines.

```
seed ──► Mulberry32 (core/seeded-random/mulberry32.ts ≡ oracle/spi_oracle/seeded_random.py, byte-identical)
        │
        └─► DataSet  (exact integers only)  ──► single source for:
              ├─ figure(dataset)         → canonical greyscale media[0].svg (viewBox 0 0 1000 700)
              ├─ prompt(dataset, task)   → prompt.blocks / prompt.instruction
              ├─ statistic(dataset,task) → answer.canonical (exact Rational {num,den} / table-completion)
              ├─ solution(dataset,task)  → solution.steps[]
              └─ dataTable(dataset)      → media[0].dataTableFallback  (a11y; free-form object, schema-valid as-is)
```

The dataset is stored verbatim in `item.params` (canonical JSON, sorted keys, via `core/serialization/canonical.ts`), so the validator and the redraw harness reconstruct it without RNG and recompute each projection. The figure construction reuses the approved Cartesian renderer discipline from `gen.geometry.coordinate-lines` (equal-scale viewport, the single `gridRound` round-half-up projection over exact `Rational`, no runtime trig) and the approved `core/visual-style/cartesian-theme` render-mode contract; bar/line/pictogram figures are layouts over that renderer, not a new one. **Parity scope (correcting the over-broad "byte-parity Py/TS for theming" claim):** byte-parity Py/TS is required for the *canonical* `media[0].svg`, `params`, `answer.canonical`, and the `distractors`. The `presentationSvg`/`exportSvg` render-mode layer (`cartesian-theme.ts`) is a **TypeScript-only presentation concern** — there is no `oracle/spi_oracle/cartesian_theme.py` (verified: none exists) and the themed/exported copies are never serialised into the item, so no Python theme mirror exists or is promised.

### 4.2 The canonical `DataSet` object (the single source)

Every value is an exact integer; nothing in the dataset is a float. The dataset has **exactly one of two `kind` values — `"frequency" | "list"`** (this is the single, canonical `kind` vocabulary; §6/§11 `params-in-domain` use these literals verbatim). Field names below are canonical and are referenced unchanged by every validator-check description.

**Categorical / frequency dataset** (`kind: "frequency"`) — drives bar chart, pictogram, frequency table, `read_table_value`, and the `mean_from_freq_table` task:

| field | shape | meaning / invariant |
|---|---|---|
| `kind` | `"frequency"` | discriminator |
| `categories` | `string[]`, length `k`, `2 ≤ k ≤ 6` | category labels; deterministic order **is** the canonical chart/table/data-table order |
| `frequencies` | `number[]`, length `k` | non-negative integers, `frequencies[i] ≥ 0` |
| `unit` | `{ singular: string, plural: string }` | context noun ("student"/"students") for prompt + a11y |
| `pictogramKey` | `number \| null` | symbols-per-unit `s ≥ 1`; non-null **only** when `frequencies[i] % s === 0` for every `i` (whole symbols only — §4.5) |

**List dataset** (`kind: "list"`) — drives `mean_from_list`, `median_from_list`, `mode_from_list`, `range_from_list`, the line graph (as an ordered `(index, value)` series), and `single_event_probability`:

| field | shape | meaning / invariant |
|---|---|---|
| `kind` | `"list"` | discriminator |
| `values` | `number[]`, length `n`, `3 ≤ n ≤ 9` | integers (may repeat; may be negative for context-free lists, non-negative for counts) |
| `sorted` | `number[]` | `values` ascending — materialised so median/range derivation never re-sorts implicitly; parity-checked against a deterministic stable sort |
| `unit` | `{ singular: string, plural: string }` | context noun |
| `seriesLabels` | `string[] \| null` | x-axis labels for line-graph rendering (e.g. months); `null` for an unlabelled list. A line-graph dataset is a `list` PLUS non-null `seriesLabels` — there is no separate `"time-series"` kind. |

The single canonical names are: `frequencies` (not `freq`), `values` (not `data`), `pictogramKey` (not `glyphValue`/`unit?`), and `unit` for the context noun object. §6 and §11 use these exact names; any drift breaks `closure-agreement`/`svg-realises-data` because `params.dataset` is serialised with sorted keys and recomputed key-for-key.

A `list` dataset can be re-expressed as a frequency table internally (value → count) for any frequency-table-style derivation; that derived table is a pure function of `values`, so it is **not** stored separately.

**Probability source (specified, resolving the underspecified-source finding).** `single_event_probability` uses a `frequency` dataset (e.g. a spinner/colour-count table) and attaches `outcomeSpace = { favourable: number, total: number }` where `favourable = frequencies[targetCategoryIndex]` and `total = Σ frequencies`. Both are exact integers with `total ≥ 1` and `0 ≤ favourable ≤ total`. Because `favourable` and `total` are read from the same frequencies that draw the chart, the displayed figure and the probability share one source. **Chart-present decision (resolving the §6.9 vs O8 contradiction):** the probability item DOES show the frequency chart/table (so O8's `allowedRepresentations` legitimately includes `diagram`/`tabular`); the `no-statistic-in-svg` check (§5.7) guarantees the figure never prints the fraction answer.

### 4.3 Parameter model and sampling

`params` mirrors the coordinate-lines pattern — a flat, canonical-JSON record sufficient to redraw the item with no RNG:

```
params = {
  task,                    // one canonical task id from the §4.6 enum (one spelling, used everywhere)
  chartType,               // "bar" | "pictogram" | "frequency-table" | "line"  (deferred types absent from the enum — §4.6)
  dataset,                 // the DataSet object above (the single source)
  targetCategoryIndex?,    // for read_bar_chart / read_pictogram / read_table_value / single_event_probability
  blankCellIds?,           // for complete_frequency_table: which cells are blanked (ids per §5.4)
  mc?,                     // boolean: whether multiple-choice is offered (drives interactionType — §4.6)
  rngTrace?                // optional debug breadcrumb; never read by the validator
}
```

`interactionType` is derived from `params.mc` exactly as coordinate-lines derives it: `mc === true ⇒ "multiple-choice"`, else `"free-response"`. **No task ever sets `interactionType:"table-completion"`** — that string is not in the schema enum and would fail Ajv validation at the storage/import/export boundary and fail the inherited `interaction-type` check.

Sampling is staged and bounded, exactly like coordinate-lines' `MAX_PARAM_ATTEMPTS` loop:

1. Draw `kind`, `k`/`n`, labels, then each integer frequency/value with `nextInt`.
2. Apply **task-eligibility guards** (§4.4) and **degenerate-case / MC-eligibility policy** (§4.5). If the draw violates a guard for the chosen task, perform a **deterministic redraw** (advance the same RNG stream and resample) — never a silent patch. This mirrors the platform's "`<3` distinct misconception distractors ⇒ redraw" rule and keeps the seed→item map total.
3. Once a dataset survives the guards, all statistic projections are pure; no further RNG is consumed for the mathematics (only for distractor ordering / `shuffle`, when `mc`).

Because both languages consume the identical `Mulberry32` stream in the identical order, the surviving dataset is byte-identical across Python and TypeScript for every seed; the 4-seed golden and 150×2 parity fixtures lock the constructor, and `SPI_SWEEP=10000` exercises the redraw guards.

### 4.4 Task-eligibility guards (so a statistic is always well-posed and exact)

| guard | applies to | rule |
|---|---|---|
| `nonEmpty` | all stat tasks | total count `≥ 1`; for `list`, `n ≥ 3` |
| `meanExact` | `mean_from_list`, `mean_from_freq_table` | mean is `Σ/(n)` or `(Σ fᵢ·vᵢ)/(Σ fᵢ)` — always an exact `Rational`; no guard beyond non-empty, but the **display** form is chosen by `terminates(den)` (reuse `terminates()` from `core/answer-checking/rational-checker.ts`) |
| `dataset-has-spread` | `range_from_list`, `median_from_list` | `max(values) > min(values)` — **uniform lists (`max === min`, range 0) are redrawn for these two tasks** (§4.5) |
| `medianDefined` | `median_from_list` | `n ≥ 3`; even-`n` two-middle average kept exact (§5.2) |
| `mode-unique` | `mode_from_list` | strict uniqueness: `maxFreq ≥ secondFreq + 1` over the value→count table. Multi-modal AND all-distinct ("no mode") lists are **redrawn** for v1.0.0 (§4.5). |
| `freqNotAllEqual` | `mean_from_freq_table` **when `mc`** | the frequencies are not all equal — otherwise the weighted mean equals the unweighted mean and the `IGNORES_FREQ` distractor would collide with the key (added per the MISSING finding) |
| `probExact` | `single_event_probability` | `total ≥ 1`; answer is `favourable/total` reduced via `Rational`; for MC, `total ≥ 4` so ≥3 distinct in-range distractors are reachable (§4.5) |
| `pictogramWhole` | pictogram render | `pictogramKey` divides every frequency (else render as a bar chart) |
| `readableChart` | all figure tasks | at least one positive frequency so the chart has a non-degenerate axis; max frequency bounded so bars fit the equal-scale viewport |

### 4.5 Degenerate cases — enumerated, never silent

- **Empty data:** excluded by `nonEmpty`. Mean/median/mode/range are undefined on `n = 0`; such draws are redrawn. No "0/0" ever reaches an answer.
- **Uniform data** (all values equal, e.g. `[4,4,4,4]`): mean = median = mode = that value; **range = 0** (exact). Uniform lists are **redrawn for `range_from_list` and `median_from_list`** (guard `dataset-has-spread`), so `range = 0` is **not emittable** for those tasks. Uniform data IS reachable only for `mean_from_list` and `mode_from_list`, capped at a small probability per task family so it does not dominate the sweep; when used for `mode_from_list` the mode is the single uniform value (well-defined). (This resolves the §4.5-example-vs-spread-gate inconsistency: the range-0 example is intentionally *not* in scope for range/median.)
- **Multi-modal** (two+ values tied for most frequent): fails `mode-unique` → **redrawn**. The single-value mode answer is therefore always well-posed for the seeds that survive. The `set`-valued (multimodal) mode encoding is **DEFERRED** (§5.3); no empty-set or total-set convention is emitted in v1.0.0.
- **No mode** (every value distinct, all counts 1): fails `mode-unique` → **redrawn**. There is no "empty set" / "all values" convention in v1.0.0 (deferred with the multimodal `set` encoding).
- **Even vs odd `n` for median:** odd → middle element of `sorted` (an integer); even → exact average of the two middle elements. If the two middles share parity the average is an integer (`den === 1`); if they differ in parity it is a half-integer (`Rational` with `den === 2`). Both are first-class (§5.2); the stored `answer.type` is set from the computed `den` (`integer` when `den === 1`, else `exact-rational`).
- **Ties in the data list:** allowed; they are exactly what create the unique mode and equal-valued bars. The materialised `sorted` array makes tie-handling deterministic and parity-checked.
- **Pictogram non-divisible counts:** disallowed for pictogram rendering (`pictogramWhole`); the same dataset renders as a bar chart instead. The chart never shows a misleading fractional symbol.
- **Probability endpoints:** `favourable === 0` (`P = 0`) and `favourable === total` (`P = 1`) are free-response-only and are **never offered as MC** (the `favourable/(total−favourable)` distractor is undefined or out of range there — §5.5). `P = 1/2` is permitted.

### 4.6 In-scope vs deferred — the canonical task list, deterministically excluded

**v1.0.0 chart scope:** `chartType ∈ { "bar", "pictogram", "frequency-table", "line" }`.

**v1.0.0 canonical task enum (one spelling each; the single source of truth referenced verbatim by §1–§3, §5, §8.3, §11, §13, §14):**

| task id | chartType | answer.type | objectiveId (the `OBJECTIVE_BY_TASK` analogue) | MC? |
|---|---|---|---|---|
| `read_bar_chart` | bar | `integer` | `SPI.MIDDLE.STAT.READ.BAR.01` | yes |
| `read_pictogram` | pictogram | `integer` | `SPI.MIDDLE.STAT.READ.PICTOGRAM.01` | yes |
| `read_table_value` | frequency-table | `integer` | `SPI.MIDDLE.STAT.READ.TABLE.01` | yes |
| `read_line_graph` | line | `integer` | `SPI.MIDDLE.STAT.READ.LINE.01` | yes |
| `complete_frequency_table` | frequency-table | `table-completion` | `SPI.MIDDLE.STAT.FREQ.COMPLETE.01` | no (free-response) |
| `mean_from_list` | bar | `integer \| exact-rational` | `SPI.MIDDLE.STAT.AVG.MEAN_LIST.01` | yes |
| `median_from_list` | bar | `integer \| exact-rational` | `SPI.MIDDLE.STAT.AVG.MEDIAN_LIST.01` | yes |
| `mode_from_list` | bar | `integer` | `SPI.MIDDLE.STAT.AVG.MODE_LIST.01` | yes |
| `range_from_list` | bar | `integer` | `SPI.MIDDLE.STAT.AVG.RANGE_LIST.01` | yes |
| `mean_from_freq_table` | frequency-table | `integer \| exact-rational` | `SPI.MIDDLE.STAT.AVG.MEAN_FREQ.01` | yes |
| `single_event_probability` | frequency-table | `fraction \| integer` | `SPI.MIDDLE.STAT.PROB.SINGLE_EVENT.01` | yes |

This is a strict 1:1 task↔objective bijection (11 tasks, 11 objectives) — the precondition for the inherited `objective-mapping` check, which asserts `item.objectiveIds === [OBJECTIVE_BY_TASK[task]]`. Objective IDs use the canonical `SPI.MIDDLE.STAT.<TOPIC>.<MICRO>.01` form (stage `middle-school`, domain `statistics`); §11 must reference **these** literals, not `SPI.MS.STATISTICS.*`.

**Deferred to a later version (structurally excluded):** pie chart, scatter/correlation, histogram, stem-and-leaf; and the statistics standard deviation, regression/line-of-best-fit, quartiles/IQR (§5.6), and the multimodal/no-mode **`set`-valued mode** answer (§5.3). Exclusion is **structural, not advisory**: `chartType` and `task` are closed enums in the generator; the deferred values are absent from the enum and from the dispatch tables (the analogue of coordinate-lines' `TASKS`/`FIGURE_TASKS`), so no seed can ever produce them. The artifact-integrity test asserts the enum membership, so re-introducing a deferred type without curriculum sign-off fails the build.

---

## 5. Answer representation and equivalence checkers

### 5.1 Encoding rules common to all tasks

Every answer uses an **existing** `answer.type` enum value — **no `answer.type` enum edit and no schema change are required** (each type below is already in the platform `answerType` enum, verified against `schemas/question-item.schema.json`):

- `integer` / `exact-rational` / `fraction`: canonical is the reduced rational object `{num, den}`, `den ≥ 1`. `integer` carries `den === 1`; `exact-rational`/`fraction` carry `den > 1`. The schema's `allOf` `if/then` constraints for `integer` (`den` must be `1`) and `exact-rational` (`{num, den≥1}`) are honoured exactly; the inherited `answer-type-consistency` discipline (`integer ⇔ den === 1`) is preserved.
- `ordered-pair`: **not used by v1.0.0 read-offs** (see below).
- `table-completion`: free-form canonical `{ cells: [...] }` (§5.4); the schema has no `if/then` for this type, so it is **checker-validated** (stated explicitly to satisfy the "no falsely-claimed schema change" check). `table-completion` is the `answer.type`; the `interactionType` is `free-response`.
- `set`: **deferred** (the multimodal mode path — §5.3). `checkUnorderedSet` is therefore proposed but not exercised in v1.0.0.

**Read-offs are plain `integer` (resolving the ordered-pair-not-in-objectives finding).** Reading a value from a bar/pictogram/table/line graph yields an `integer` answer checked by `checkExactRational`. The `ordered-pair`/`checkOrderedPair` "which category has value v / read the point at month M" variant is **dropped from v1.0.0**, because (a) the read objectives declare only `answerTypes:[integer]`, and an item's `answer.type` must be in its objective's `answerTypes`; and (b) `checkOrderedPair`'s canonical is a numeric `{x:{num,den}, y:{num,den}}` (verified `coordinate-checkers.ts:36`) and cannot represent a string category label. If a labelled point read-off is wanted later, it requires adding `ordered-pair` to the objective's `answerTypes` AND constraining the first component to an integer index.

All numeric canonicals are produced by exact `Rational` arithmetic (`core/exact-math/rational.ts`), so `{num, den}` and the display string match the Python oracle byte-for-byte. The display form for a `Rational` answer is selected deterministically: integer when `den === 1`; otherwise the fraction `num/den`, with a terminating decimal *offered as an accepted equivalent* only when `terminates(den)` is true — reusing the existing `terminates()` and `checkExactRational(input, {num,den}, accepts)` from `core/answer-checking/rational-checker.ts`. No checker touches a float for the accept/reject decision.

**Checker reuse, by name:**

| answer.type | checker | maps to enum value | canonicalisation | comparison |
|---|---|---|---|---|
| `integer` / `exact-rational` / `fraction` | `checkExactRational` (`rational-checker.ts`, reused) | `integer`/`exact-rational`/`fraction` (existing) | reduced `Rational`, `den ≥ 1` | exact `{num,den}` equality; equivalent fractions always accepted; decimal only if `accepts.decimal` |
| `table-completion` | **new** `checkTableCompletion` (added to `core/answer-checking`) | `table-completion` (existing enum value — no schema change) | per-cell reduced `Rational`, keyed by cell id | every required cell exactly equal; submitted cell-id set must equal the required set exactly |
| `set` (**deferred**) | **new** `checkUnorderedSet` (added to `core/answer-checking`, but **not used in v1.0.0**) | `set` (existing enum value — no schema change) | sorted, de-duplicated list of reduced `Rational` | order-insensitive exact set equality |

`checkTableCompletion` is deliberately family-agnostic (no `gen.stats` imports), mirroring how `coordinate-checkers.ts` was written to be reusable, and is byte-parity-mirrored in `oracle/spi_oracle` like every other core primitive. `checkUnorderedSet` ships with the deferred multimodal-mode work, not v1.0.0.

**Exact-Rational distractor distinctness invariant (added per MISSING finding).** Before any MC is emitted, every distractor value is compared to the key and to every other distractor by **exact reduced-`Rational` equality on `{num, den}`**, NOT by display-string equality. (The inherited `distractor-not-answer` check compares `d.display !== answer.display`, verified `coordinate-lines.ts:870` — a necessary but not sufficient gate, since `2/8` and `1/4` differ as strings yet are equal as values.) The generator therefore reduces both operands first; if any distractor reduces to the key (or to another distractor), it is dropped and backfilled, else the seed is redrawn under the `<3 distinct ⇒ redraw` rule. **Distractor rationale coupling (added per MISSING finding):** each emitted `distractor.rationale` is set **string-equal to the registry `observableError`** so the inherited `distractor-rationale-matches` check (verified `coordinate-lines.ts:871`) passes.

### 5.2 Mean, median, range, and read-offs

- **Mean** `= (Σ values) / n` for a list, or `(Σ fᵢ·vᵢ) / (Σ fᵢ)` for a frequency table, built as a single `Rational` and reduced. `answer.type` is `integer` when `den === 1`, else `exact-rational`. Accepts: equivalent fractions always; decimal only when `terminates(den)`. Example: `[3,5,5,8] → 21/4` (`exact-rational`, display `21/4`, decimal `5.25` accepted because `den = 4` terminates).
- **Median** from `sorted` (the materialised array, never re-sorted): odd `n` → `sorted[(n−1)/2]` as an integer `Rational`; even `n` → `(sorted[n/2 − 1] + sorted[n/2]) / 2`, an exact `Rational` (`den ∈ {1, 2}`). Example: `[2,3,6,9] → (3+6)/2 = 9/2`. **The stored `answer.type` is set from the computed `den`** — `integer` when the two middles share parity (`den === 1`), `exact-rational` when they differ (`den === 2`). The coverage matrix (§13.2) must therefore list `median_from_list` as `integer | exact-rational`, NOT pinned to `exact-rational`, so the `answer-type-consistency` check (`integer ⇔ den === 1`) passes. The two-middle-values average is first-class, never rounded.
- **Range** `= max − min` over `sorted`, always a non-negative integer (`answer.type:"integer"`). Uniform data (range 0) is excluded for this task by `dataset-has-spread` (§4.5), so the emitted range is always `≥ 1`. The checker is `checkExactRational` with `accepts:{decimal:false}` (range is integral).
- **Read a value** from a bar/pictogram/table/line graph: the read-off is an `integer` answer via `checkExactRational`. Pictogram read-offs multiply the symbol count by `pictogramKey`, and the solution shows that multiplication.

### 5.3 Mode — single-value, unique, `integer` (v1.0.0)

For v1.0.0 the mode is computed over the value→count table of `sorted` and is gated to a **strictly unique** modal value by `mode-unique` (§4.4). The canonical encoding is therefore a single `integer` (`answer.type:"integer"`, `{num, den:1}`), checked by `checkExactRational`. Examples: `[2,2,5] → 2`; `[1,1,2,2,2,9] → 2`.

**The `set`-valued mode is DEFERRED** (resolving the dead-path / three-way-convention contradiction). Because `mode-unique` redraws every multimodal and every all-distinct ("no mode") list, the `set` machinery (`checkUnorderedSet`) would never be exercised in v1.0.0; it is moved to the deferred list together with a future "taught multimodal / no-mode" sub-objective. There is therefore **no empty-set, total-set, or `set`-typed mode answer in v1.0.0**, and the conditional empty-set language is removed from this proposal's in-scope surface. When the deferred work lands, `checkUnorderedSet` will compare each set element by the **same reduced-`Rational` equality** used for scalar answers (so a stored `{num:4,den:1}` matches a submitted `4`), with the set sorted ascending and de-duplicated for a byte-stable canonical.

### 5.4 Table-completion (frequency-table cells)

For `complete_frequency_table`, the prompt shows a frequency table with one or more cells blank (a missing frequency, or a "Total" cell); `interactionType:"free-response"` and `answer.type:"table-completion"`. The canonical is a keyed map of the blanked cells:

```
answer.canonical = { cells: [ { id: "freq.<categoryIndex>" | "total", value: {num, den} }, ... ] }
```

`checkTableCompletion` canonicalises each submitted cell to a reduced `Rational` keyed by `id`, then requires (a) the submitted cell-id set to equal the required set exactly (no missing, no extra) and (b) every cell to be exactly equal. Frequencies are integers (`den === 1`); a "Total" cell is `Σ frequencies`. Because the table is a pure projection of the same `DataSet`, the blanked values and their answers are guaranteed consistent with the chart and the a11y data-table. The `{cells:[...]}` shape is free-form under the schema (no `if/then` for `table-completion`), validated solely by `checkTableCompletion`; the validator's `table-cells-match-dataset` check (§5.7) re-asserts the cell ids and values are the exact projection of `params.dataset`.

### 5.5 Probability (single event) as an exact fraction

`single_event_probability` encodes `P = favourable / total` from `outcomeSpace`, built as one `Rational` and reduced (e.g. `3/12 → 1/4`). `answer.type` is `fraction` (or `integer` for `P = 0` / `P = 1`). Checked by `checkExactRational` with `accepts:{ fraction:true, decimal: terminates(den), mixed:false }`, so `1/4`, `2/8`, and `0.25` all pass while `0.3` fails.

**Single reconciled, in-range distractor rule (resolving the §5.5-vs-§8.2 disagreement and the out-of-range finding).** The probability misconception distractor is the **odds-as-fraction** value `favourable / (total − favourable)` (registry `MISC.STAT.PROB.NUM_OVER_FAVOURABLE`, summary "writes wanted-to-unwanted instead of wanted-to-total"). This lies in `(0, 1)` exactly when `favourable < total − favourable`, i.e. `favourable < total/2`. It is therefore subject to an explicit **in-range filter — every probability distractor value must lie in `[0, 1]`** (added as the §-level `prob-distractor-in-range` MC gate); when the value leaves the unit interval or equals the key, that distractor is dropped and backfilled, else the seed is redrawn. The earlier `total/favourable` formulation is **removed** (it is `≥ 1` for every proper probability, so it is never a valid probability and at `favourable === total` collides with `P = 1`). The `favourable === total` and `favourable === 0` endpoints are MC-suppressed (§4.5). With `total ≥ 4` (the `probExact` MC gate) and the in-range filter, ≥3 distinct misconception-backed distractors in `(0, 1)` are reachable, satisfying the `≥3 distinct ⇒ else redraw` gate. An un-reduced fraction (`2/8`) is **not** a distractor (the checker accepts equivalents).

### 5.6 Quartiles / IQR and other exactness boundaries

Quartiles and IQR are **deferred** from v1.0.0 and structurally excluded (their task ids are absent from the §4.6 enum). The exact-math boundary is stated conservatively (correcting the over-strong "stays rational" claim): quartiles are rational **only under list-element or two-element-average conventions**; several standard interpolation conventions (e.g. `(n−1)p` / CDF methods) place a quartile at a non-half fractional position (`den ∈ {4}` or worse) — still rational, but not within the `den ∈ {1, 2}` regime the rest of this family assumes, and the convention itself is ambiguous across curricula (inclusive vs exclusive median, Tukey hinges). When introduced, quartiles will reuse `checkExactRational`, and **any chosen convention that would yield a non-list, non-half value triggers a deterministic redraw**, preserving the platform's no-irrationals rule. Standard deviation (surds) and regression lines remain out by the same rule: nothing whose exact value is irrational is ever emitted.

### 5.7 Validator hooks for answers

The independent validator (`validate(item) → {status, validatorVersion, checks[]}`) gains answer-side checks alongside the existing `svg-realises-data` and `closure-agreement`. These run in both the Python oracle and the TypeScript production path, holding the answer layer to the same byte-parity and recomputation discipline as the figure:

- `closure-agreement` (existing, extended): recompute the statistic from `params.dataset` by a second route and assert it equals `answer.canonical` exactly (`Rational`/table equality, never float). Mean/median/range and each table cell are compared by reduced-`Rational` equality on `{num, den}`.
- `answer-type-consistency` (inherited discipline): assert `integer ⇔ den === 1` for mean/median/mode/range/probability, so the stored type is never mislabelled (notably the even-`n` median `den === 1` case is tagged `integer`, not `exact-rational`).
- `answer-checker-accepts-canonical`: feed `answer.display` (and each `accepts`/`equivalentForms` form) back through the named checker and assert it returns `true`; feed each distractor display and assert `false`.
- `distractor-distinct-exact` (added per MISSING finding): assert every distractor value differs from the key and from every other distractor by **reduced-`Rational` `{num, den}` inequality**, not display-string inequality.
- `prob-distractor-in-range`: for `single_event_probability` MC items, assert every distractor value lies in `[0, 1]` and `favourable ∉ {0, total}`.
- `table-cells-match-dataset`: assert the `table-completion` cell ids and values are exactly the projection of `params.dataset`.

**Inherited-vs-overridden validator checks (added per MISSING finding — the per-check disposition for the figure-side gates these answer checks sit beside).** Because three inherited coordinate-lines checks cannot transfer verbatim to statistics figures, §6/§11 must REPLACE rather than inherit them; this is flagged here because the answer encodings depend on it: (1) `no-answer-label-in-svg` (inherited predicate bans `text` containing `,`/`/`/`=`, verified `coordinate-lines.ts:835`) is **replaced** by a statistics-specific `no-statistic-in-svg` whose predicate is "no figure `<text>` equals `answer.display` or any distractor display" — category labels, the pictogram key line (`1 picture = 5`), and axis-unit text legitimately contain `=`/`/`/`,`; (2) `tick-labels-integer` (scrapes `cx-ticklbl`, verified line 832) stays **verbatim** but applies only to the integer count axis — category strings are emitted under a separate `cx-cat` class, never `cx-ticklbl`; (3) `media-to-scale` (asserts `toScale === true`, verified line 828) is inherited **verbatim for bar/line** charts and **replaced for pictograms** (glyph-count figures carry `toScale:false` plus a `pictogram-key-exact` check). The full inherit/override/replace table lives in §11.4; it is referenced here so the answer-side checks above are understood to run alongside the *replaced*, not the verbatim, figure gates.


---

## 6. Chart types and the SVG renderer contract

This section fixes the **canonical, monochrome-authoritative** chart renderer for `gen.stats.data-handling` v1.0.0 and the per-chart contract every figure must satisfy. It does **not** invent a renderer: it extends the Cartesian discipline already shipped and approved in `gen.geometry.coordinate-lines` (`domains/geometry/coordinate-lines.ts` / `oracle/spi_oracle/coordinate_lines.py`) — a single source of truth (`params` → a seeded dataset), all coordinates produced as **integers** by `gridRound(num, den)` round-half-up over exact `Rational`/`Fraction`, **no runtime trig and no floats in the emitted geometry**, a hand-serialised SVG that is **byte-for-byte identical between TypeScript and the Python oracle**, and the `cx-*` class vocabulary read by the approved `core/visual-style/cartesian-theme` (§7). Colour is a presentation overlay over this same canonical geometry and **never carries meaning alone**.

> **The canonical monochrome SVG is AUTHORITATIVE and carries NO `class="cx-figure"`.** Exactly as the coordinate-lines `figure()` (`coordinate-lines.ts` line 189: `<svg … viewBox="0 0 1000 700" role="img" aria-label="…">` with an internal monochrome `<style>` block, **no** `class` attribute), the stored `media[0].svg` is the un-themed, short-hex monochrome figure with its own embedded `<style>`. The `class="cx-figure"` root + per-root `--cx-*` custom properties are stamped **only** by `presentationSvg()` / `exportSvg()` (`core/visual-style/cartesian-theme.ts` lines 60–69) at presentation/export time; they never mutate the canonical figure. Every downstream gate — the golden + 150×2 parity fixtures, the `SPI_SWEEP = 10000` stability sweep, the independent validator (`validate(item) → {status, validatorVersion, checks[]}`), the bank-json round-trip, and the offline HTML exporters — re-derives, re-serialises, and byte-compares **this** canonical `media[0].svg`. The premium / premium-dark / accessible / print skins add no positional information and never become a second stored figure (§7).

### 6.1 The single dataset is the source of truth for every artifact

The renderer is a pure function `chartSvg(model, alt, title, desc) → string`, where `model` is built **only** from the deterministic seeded **dataset** serialised verbatim into `params.dataset` (canonical JSON, sorted keys) — the same object that feeds the prompt, the answer, the solution, and `media[].dataTableFallback`. There is **one canonical `DataSet` field schema**, pinned here and referenced by that exact spelling in every other cluster (§4.2, §11.1, and every validator-check description); the discriminator is `kind ∈ {"frequency", "list"}` (two values only — line-graph/time-series is a `list` with `seriesLabels`; a frequency table is a `frequency` dataset):

| `kind` | Canonical fields (exact names) | Invariant |
|---|---|---|
| `"frequency"` | `categories: string[]`, `frequencies: int[]` (parallel arrays), `glyphValue?: int` (pictogram icon value, present iff `chartType === "pictogram"`) | `len(categories) == len(frequencies)`; every `frequencies[i]` a non-negative **integer**; `1 ≤ len ≤ MAX_CATEGORIES`; `Σ frequencies ≥ 1` |
| `"list"` | `values: int[]`, `seriesLabels?: string[]` (line-graph independent-axis labels, `len == len(values)`) | every value an **integer**; `1 ≤ len ≤ MAX_LIST_LEN`; stored in draw order (sorting is a solution step, never a stored mutation) |

> **Field-name discipline.** The canonical names are `frequencies` (not `freq`), `glyphValue` (not `unit`/`pictogramKey`), `values`, `categories`, `seriesLabels`. Because the dataset is serialised verbatim and the validator recomputes the figure/answer from those exact keys, any drift breaks `closure-agreement` / `svg-realises-data` reproducibility; these spellings are the single source of truth everywhere.

The **same** `"frequency"` dataset realises a bar chart, a pictogram, or a frequency table; the **same** `"list"` dataset realises a line graph and the mean/median/mode/range tasks. The chart, the prompt text, the canonical answer, the worked solution, and the accessibility data-table are therefore five views of **one** integer dataset, which is exactly what makes `dataset-realises-chart` (figure recomputed from `params.dataset`) and `closure-agreement` (answer recomputed by a second route) byte-deterministic across Py/TS. The window, the unit scale, and the integer offsets come from §7 and are part of `model`; the renderer **never recomputes** them.

### 6.2 v1.0.0 chart set (proposed) and deferrals — deterministically excluded

A chart type is **in v1.0.0 only if its geometry is exact-integer, faithfully readable, and answer-free where the figure must not reveal the answer.** Deferred chart types are **deterministically excluded** — the generator never selects a deferred `chartType`, deferred types are **absent from every dispatch table** (never reachable), and the validator's `chart-type-in-scope` check (§6.9) fails any item carrying one, so a deferred chart can never be silently emitted.

| Chart type | v1.0.0? | Tasks served | Rationale |
|---|---|---|---|
| **Bar chart** (vertical) | **IN** | `read_bar_chart`, `read_table_value` (table form), `complete_frequency_table` (table form), `mean_from_freq_table` | Integer frequencies → integer bar heights on an equal-step count axis; the cleanest reuse of the Cartesian axis/gridline/tick discipline. |
| **Pictogram** | **IN** | `read_pictogram` | A `"frequency"` dataset with a committed integer `glyphValue` (icon = `glyphValue` items); each row draws `floor(frequencies[i]/glyphValue)` full icons + a fractional icon when `glyphValue ∤ frequencies[i]`, the fraction being an **exact `Rational`** (e.g. a half-icon = `1/2·glyphValue`) clipped by an integer-coordinate path. No trig, no float. |
| **Frequency table** | **IN** | `read_table_value`, `complete_frequency_table`, `mean_from_freq_table` | An SVG ruled grid of integer cells with `<text>`. Pure integer layout; the table **is** the data-table, so it doubles as the accessibility fallback. For `complete_frequency_table` one cell is blanked (answer.type `table-completion`, interactionType **`free-response`** — see §6.9 / §11.4). |
| **Line graph** (time series) | **IN** | `read_line_graph` | A `"list"` dataset plotted as `(i, value)` integer lattice points joined by a polyline — a **direct reuse** of the coordinate-lines plotted-point + clipped-segment primitives (`pointEls`, `lineEl`, the §7 projection). |
| **Pie chart** | **DEFER** | — | Sector boundaries need angles; faithful sectors require `sin/cos`, forbidden in emitted geometry (no runtime trig), and exact sector angles are generally irrational fractions of the circle. **Absent from every v1.0.0 dispatch table.** (If later admitted, only via a committed integer **direction table** restricting to partitions whose angles land on tabulated directions, mirroring the coordinate-lines arrowhead construction.) |
| **Scatter plot** | **DEFER** | — | Plotting integer `(x, y)` pairs is in-discipline, but the v1.0.0 *reading* task ("describe the correlation") is a qualitative judgement, and any line-of-best-fit / regression is **irrational** and out of scope. The scatter *primitive* (lattice points, no join) is reusable infrastructure; the **correlation task is deferred and structurally absent.** |
| **Histogram** | **DEFER** | — | Distinguished from a bar chart by **continuous class intervals and frequency density** (`frequency / class width`), introducing non-integer density that exceeds the v1.0.0 exact-integer frame. **Excluded.** |
| **Stem-and-leaf** | **DEFER** | — | A typographic table with its own back-to-back and key conventions, a distinct layout primitive. **Excluded from v1.0.0**, scheduled as a fast follow (needs no new math, only a new text-layout primitive). |

> **Statistics in v1.0.0 are EXACT only.** Mean, median, mode, and range from a `"list"` or a `"frequency"` dataset are exact `Rational`/`integer` values; **standard deviation (surds), frequency density, and regression/best-fit lines are deferred and never emitted** (the `no-irrational-statistic` check, §6.9, fails any answer whose canonical value is not a finite reduced `{num, den}`). Single-event probability is an exact `fraction` answer (`favourable/total`, reduced). The probability task carries **no chart** (it draws from a small committed outcome space; §6.9 `chart-type-in-scope` admits a chart-absent case for it).

### 6.3 Chart primitives needed, and where reusable pieces live

The coordinate-lines renderer already provides the **reusable Cartesian substrate**: the equal-scale viewport + single `gridRound` projection of record (§7), axes with integer arrowheads, major/minor gridlines, integer ticks with a deterministic label-thinning stride (`MAX_LABELS_PER_AXIS`), plotted points (`cx-pt-outline` halo under `cx-pt-core`), a clipped straight `cx-line`, the integer collision-avoidance label placer, the `esc` XML-escape map, and the deterministic element-emission order. Line graphs **reuse these unchanged**. Statistics adds exactly four new chart primitives, factored out so both families share them:

| New primitive | Role | Proposed home (extracted from the coordinate-lines renderer into a shared module) |
|---|---|---|
| **Bars** | `barEls(catIndex, height, U, P) → string[]` — an integer-coordinate `<rect>` (or `<path>`) on the count axis, plus a committed greyscale **inline hatch** (a set of integer-coordinate `<line>` strokes clipped to the bar, **no `<pattern>`/`url(#…)`** — see §6.6) so adjacent bars differ without colour | `core/render/cartesian-axes.ts` + `core/render/bars.ts` (TS); `oracle/spi_oracle/render/*` (Py mirror) |
| **Category axis** | a discrete, **equal-step** horizontal axis carrying category **labels** under each bar/icon column (class `cx-cat`, **never** `cx-ticklbl` — §6.5); integer column centres via the §7 projection | `core/render/cartesian-axes.ts` (category-axis mode) |
| **Pictogram icons** | `iconEls(catIndex, count, glyphValue) → string[]` — a committed integer icon glyph repeated `floor(frequencies[i]/glyphValue)` times, plus one exact-`Rational` clipped partial icon; a **key** (`1 icon = glyphValue`) is always emitted | `core/render/pictogram.ts` |
| **Table grid** | `tableGrid(dataset, blankCell?) → string[]` — ruled integer rows/cols of `<text>` cells; the visible frequency table **and** the data-table fallback share this | `core/render/table-grid.ts` |

These live under a proposed `core/render/*` so they are shared, not copied: the point/line/axis code that coordinate-lines proved is **lifted verbatim** (same `gridRound`, same projection, same byte output) and both families import it. **No parallel renderer is created.** The pie-sector primitive is **NOT built in v1.0.0** (the deferral is explicit, not a silent gap).

### 6.4 Canvas, frame, and the single projection of record

- `viewBox` is fixed at **`0 0 1000 700`** (`VIEW_W = 1000`, `VIEW_H = 700`), identical to coordinate-lines.
- A **single unit length `U`** (integer px per data unit) governs the **count axis** (and, for line graphs, both axes at equal scale). The category axis uses a separate committed integer **column pitch** `P` (px per category slot) so categories are evenly spaced; `U` and `P` are both integers, chosen by §7.
- **There is exactly one projection of record, defined in §7.** It keeps the centering offset and the unit-scaled term **inside one exact `Rational`** and applies a **single** `gridRound` at the end — exactly as `projX`/`projY` do in `coordinate-lines.ts`. This section commits no separate projection formula. For integer dataset values and integer `U`/`P` the unit-scaled term is already integer, so the only rounding is the single `gridRound`; for the one fractional case (a pictogram partial icon at `frequencies[i] mod glyphValue / glyphValue`) the same single `gridRound` runs over the whole exact sum. No `Math.*`, no `sin`/`cos`, no float division survives into the string.

### 6.5 Style block and the `cx-*` class vocabulary (reused + extended, with committed greyscale)

The canonical `<style>` block is the **same committed monochrome short-hex constant** coordinate-lines emits (`STYLE` in `coordinate-lines.ts` lines 54–65 and `coordinate_lines.py` lines 87–97), extended with three statistics classes. All are monochrome; every distinction is carried by **width, greyscale, and inline hatch geometry**, never colour. **Crucially, the inherited `no-colour-only-information` check (`coordinate-lines.ts` line 861; `coordinate_lines.py` line 1100) scrapes every `fill:`/`stroke:#hex` from the canonical SVG and asserts the colour set is a subset of `GREYS`** (`{#111,#333,#444,#555,#888,#bbb,#fff}`). The statistics classes therefore use **only shades already in `GREYS` plus one committed addition `#666`**, and `GREYS` is **extended to `{#111,#333,#444,#555,#666,#888,#bbb,#fff}` byte-identically in both `coordinate-lines.ts` and `coordinate_lines.py`** (with owner sign-off, recorded in the manifest). The exact committed palette:

| class | role | committed canonical colours |
|---|---|---|
| `.cx-axis` · `.cx-tick` · `.cx-ticklbl` | count/value axis, ticks, **integer** count-axis labels | `#111` / `#111` / `#333` (reused verbatim) |
| `.cx-grid-major` · `.cx-grid-minor` | count-axis gridlines | `#888` / `#bbb` (reused verbatim) |
| `.cx-line` · `.cx-pt-core` · `.cx-pt-outline` | line-graph polyline + plotted points | `#111` / `#111` / fill `#fff` stroke `#111` (reused verbatim) |
| `.cx-lbl` · `.cx-guide` | value labels · scaffold guides | `#111` / `#555` (reused verbatim) |
| **`.cx-bar`** | bar fill + outline; fill `#fff`, outline `#111` | **new**: `fill:#fff;stroke:#111;stroke-width:2.5` |
| **`.cx-bar-hatch`** | inline hatch strokes drawn inside a bar | **new**: `stroke:#666;stroke-width:1` (greyscale, `#666` added to `GREYS`) |
| **`.cx-cat`** | category-axis labels (text under each column) | **new**: `font-size:22px;fill:#111` |
| **`.cx-icon`** | pictogram icon glyph + its clipped partial; fill `#444`, outline `#111` | **new**: `fill:#444;stroke:#111;stroke-width:1.5` |

The **invariant** (asserted by `axes-stronger-than-grid`, reused): `width(.cx-axis) > width(.cx-grid-major) > width(.cx-grid-minor)`, and `.cx-bar`/`.cx-icon` outlines are distinct from gridlines by width and greyscale. Bars are distinguished from one another by **a per-category hatch density/orientation** (an integer-parametrised inline stroke set, §6.6), not by fill hue. The premium layer (§7) preserves this width-and-pattern hierarchy.

### 6.6 Deterministic element order and the id-free hatch

The serialiser emits in **one fixed order** so the byte stream is canonical (matching the coordinate-lines `minor-grid → major-grid → axes → ticks → guides → line → points → labels` discipline): root `<svg role="img" aria-label="…">`, `<title>`, `<desc>`, `<style>`; then **minor gridlines**, **major gridlines**, **count axis** (+ integer arrowhead, + integer tick labels), **category axis** (column labels under class `cx-cat`), the **chart body** (bars in `categories[]` order, each immediately followed by its inline hatch strokes / icons in `categories[]` order / the line-graph polyline then its points / table rows top-to-bottom), then **value labels** placed by the reused label engine, then `</svg>`.

**No `id` attribute and no `url(#…)` reference appears in the canonical SVG** (safe multi-item worksheet export). The greyscale hatch that distinguishes bars is therefore **not** an SVG `<pattern>`/`fill=url(#…)`; it is **inline clipped stroke geometry** — a deterministic set of integer-coordinate `<line class="cx-bar-hatch" …>` elements whose endpoints are computed from the bar's integer rectangle (a fixed integer stride per category index, clipped to the bar edges by integer min/max, no float). Each bar's `<rect>` is emitted first, then its hatch lines, in element order. This keeps integer-only coordinates and the no-id/no-url(#) invariant; the `bar-pattern-distinct` check (§6.9) inspects the inline hatch elements, never a pattern id. All numeric attributes are integers; text is XML-escaped with the same `esc` map.

### 6.7 Equal vs where-appropriate axis scaling, and `toScale`

- **Line graph:** **equal x/y unit scale** `U` on both axes (genuine geometric faithfulness), exactly as coordinate-lines; `media[].toScale = true`.
- **Bar chart:** the **count axis** uses a single integer `U` (uniform per chart, so bar heights are directly comparable and `0` sits on the baseline); the **category axis** uses a uniform integer column pitch `P`. The two axes measure different quantities, so they are independently scaled but each is **internally uniform** — the §6.9 `uniform-count-scale` and `uniform-category-pitch` checks assert this. `media[].toScale = true` for bar charts (the count axis is to scale; no "NOT TO SCALE" label is emitted). A bar baseline is always the projection of count `0`, guaranteed inside the window by §7.
- **Pictogram:** a pictogram is a **glyph-count figure, not a height-to-scale figure** (a row's meaning is its icon count + the key, not a measured length). Pictograms therefore carry **`media[].toScale = false`**, and the family **does not inherit the `media-to-scale` gate for pictograms** (the inherited check at `coordinate-lines.ts` line 828 hard-asserts `toScale === true` for every figure task — see the §6.9 inherit/override table). Instead, pictograms are gated by `pictogram-key-present` + `pictogram-partial-exact`. This single policy resolves the prior §6.7-vs-§11.4 conflict: **bar/line = `toScale:true` under `media-to-scale`; pictogram = `toScale:false` under `pictogram-key-*`.**
- **Frequency table:** a table is not a scaled figure; it carries no `toScale` obligation (the table-grid is a pure layout) and is gated by `data-table-matches-dataset`.

### 6.8 Answer-free figures where the figure must not reveal the answer

The dataset feeds both the figure and the answer, so the renderer enforces **per-task leakage rules**, mirroring the coordinate-lines `plot-point-target-absent` discipline:

- **Read-a-value** (`read_bar_chart` / `read_pictogram` / `read_line_graph` / `read_table_value`): the figure shows all data (that is the point of the task) but **no `<text>` equals the queried value's display string** beyond the axis ticks / table cells the student must read; the answer is the read-off integer, never printed as a redundant label.
- **Complete-a-frequency-table** (`complete_frequency_table`, answer.type `table-completion`, interactionType `free-response`): the blanked cell is rendered **empty** (the `table-blank-cell-empty` check fails any item whose blanked cell already shows its value), and the accessibility data-table likewise blanks it.
- **Compute mean / median / mode / range / probability**: the figure/table shows the raw data; **the computed statistic is never drawn**. The `no-statistic-in-svg` check (§6.9) fails any figure whose `<text>` **equals** the canonical answer's `display` string (string equality, not a character blocklist). The statistic appears **only** in the answer key / worked solution, derived deterministically from the same dataset.

### 6.9 Validator checks: inherited (verbatim / overridden / replaced) + new statistics checks

The family runs the coordinate-lines validator battery, but **three inherited checks cannot transfer verbatim** because they assume a single-coordinate Cartesian figure with no category text, no key, and a height-to-scale figure. The table below is the authoritative inherit/override/replace map; every check still runs in **both** the Python oracle and the TS mirror with byte-identical results and appears as `{name, result, detail}` in `validate(item).checks[]`, **blocking** (any `fail` ⇒ `status = fail`).

**Inherited VERBATIM:** `svg-realises-data` (specialised as `dataset-realises-chart`), `closure-agreement`, `axes-stronger-than-grid`, `min-three-distractors`, `distractors-distinct-misconceptions`, `distractor-value-matches-rule`, `distractor-not-answer` (computed over **exact reduced `{num,den}` equality**, not display strings — so `2/8` and `1/4` are NOT distinct), `distractor-rationale-matches` (each `distractor.rationale` is set **equal to** the registry `observableError` string), `exactly-one-correct`, `provenance-complete`, `version-fields-present`, `objective-mapping`, `a11y-*`.

**Inherited but OVERRIDDEN / REPLACED:**

| Inherited check | Disposition | Reason / replacement |
|---|---|---|
| `no-answer-label-in-svg` (line 835/1071: fails any `<text>` containing `,`, `/`, `=`) | **REPLACED** by `no-statistic-in-svg` | Statistics figures legitimately render category labels (which may contain `,`/`/`, e.g. `km/h`, `Year 7, boys`) and a pictogram **key** literally containing `=` (`1 icon = 5`). The character-blocklist would fail **every** pictogram and most labelled bar charts. The replacement predicate is **string-equality / token match against `answer.display` and each distractor `display`**, NOT the `,`/`/`/`=` blocklist. A pinned test asserts a pictogram whose key text is `1 picture = 5` **passes** and a figure whose `<text>` equals the answer **fails**. |
| `tick-labels-integer` (line 832/1063: scrapes `<text class="cx-ticklbl">`, requires integers) | **INHERITED VERBATIM, scope clarified** | Category strings are emitted under `cx-cat` **only**; `cx-ticklbl` is reserved for the integer **count-axis** labels. A pinned test asserts no `cx-ticklbl` `<text>` is non-numeric (so `tick-labels-integer` stays green) and that category strings appear **only** under `cx-cat`. The `category-label-correctness` check (§11.4) scrapes `cx-cat` for the ordered category strings and `cx-ticklbl` for integer ticks **separately**. |
| `media-to-scale` (line 828: `toScale === true` for all figure tasks) | **OVERRIDDEN per task** | Applied to **bar / line** figures (`toScale:true`); **not** applied to pictograms (`toScale:false`, gated instead by `pictogram-key-present`/`pictogram-partial-exact`); frequency tables carry no `toScale` obligation. |
| `no-colour-only-information` (line 861/1100: colours ⊆ `GREYS`) | **INHERITED VERBATIM against an EXTENDED `GREYS`** | `GREYS` is extended to include `#666` (the `cx-bar-hatch` stroke) and `#444` (the `cx-icon` fill) — both committed in §6.5, added byte-identically to the `GREYS` set in TS and Py. A pinned test asserts the canonical statistics SVG's fill/stroke colours are a subset of the extended `GREYS`. |
| `interaction-type` (line 810: passes only for `free-response`/`multiple-choice`) | **INHERITED VERBATIM** | Every task — including `complete_frequency_table` — carries `interactionType: "free-response"` (or `"multiple-choice"` when MC is offered). `table-completion` is an **answer.type only**, never an interactionType (it is absent from the schema interactionType enum, lines 121). No schema change is claimed or required. |

**New statistics checks (in addition to the above):**

| Check | Asserts |
|---|---|
| `chart-type-in-scope` | `params.chartType ∈ {bar, pictogram, freq-table, line-graph}` (and `single_event_probability` has **no** chart); a **deferred** type (pie/scatter/histogram/stem-leaf) fails — deferrals are never silently emitted. |
| `no-irrational-statistic` | the canonical answer value is a finite reduced `{num, den}` (or integer); standard deviation / density / regression can never appear. |
| `dataset-realises-chart` | the chart recomputed from `params.dataset` matches `media[0].svg` **byte-for-byte** — covering **only** bar tops, pictogram glyph counts (+ the exact partial-glyph clip width), line-graph lattice points, and table cells. **No pie-sector or scatter branch exists** (those types are absent from every dispatch table — §6.2). |
| `data-table-matches-dataset` | `media[].dataTableFallback` lists exactly the dataset categories+frequencies / value list — same integers, same order — so the fallback is information-equivalent. (`dataTableFallback` is a generic `{type:"object"}` in the schema, line 316; **no schema change required**.) |
| `uniform-count-scale` | one integer `U` governs every bar/point on the count axis; the baseline is the projection of count `0`. |
| `uniform-category-pitch` | category columns are evenly spaced by one integer pitch `P`. |
| `pictogram-key-present` · `pictogram-partial-exact` | a pictogram emits its `1 icon = glyphValue` key; any partial icon is an **exact `Rational`** fraction of a full icon (no float width). |
| `bar-pattern-distinct` | bar fills differ by **inline greyscale hatch geometry** (the `cx-bar-hatch` strokes), not colour alone (the bar analogue of `no-colour-only-information`); the check inspects the inline hatch elements, never a pattern id. |
| `table-blank-cell-empty` | for `complete_frequency_table`, the blanked cell is empty in **both** the figure and the data-table. |
| `no-statistic-in-svg` | no figure `<text>` **equals** the canonical answer's `display` string or any distractor `display` (answer-free leakage gate; the replacement for `no-answer-label-in-svg`). |

> **Answer-type checkers, no schema change.** The new checkers map to existing answer.type enum members: `checkTableCompletion → table-completion` (enum line 202), `checkUnorderedSet → set` (enum line 198) — both already in the schema. **No answer.type enum edit is required** for any v1.0.0 task (mirroring the no-schema-change posture stated for the other answer types). There is **no `list` answer type** in the schema; no v1.0.0 task needs one (reads/probability use `integer`/`fraction`, line graph reads use `integer`).

---

## 7. Reuse of the approved Cartesian renderer + visual theme

This family **reuses the approved Cartesian renderer and the approved `core/visual-style/cartesian-theme` contract directly** and **does not introduce a parallel renderer or a parallel theme.** The viewport/projection discipline below is the coordinate-lines discipline (`domains/geometry/coordinate-lines.ts` / `oracle/spi_oracle/coordinate_lines.py`); the render-mode / colour / export contract below is `core/visual-style/cartesian-theme.{json,ts}` used **by name, extended additively** for bars/categories/icons.

### 7.1 The coordinate-lines viewport + single projection of record (reused verbatim)

The statistics renderer reuses the coordinate-lines viewport algorithm (`viewport()`, lines 111+) and projection without modification:

- **Data window from the dataset (integers only).** For a line graph the window is built from the integer lattice points `(i, value)` **plus the baseline/origin**, padded by the inherited integer margin `DATA_MARGIN_UNITS = 1` (the coordinate-lines `viewport()` over an integer set, so `min`/`max` agree byte-for-byte Py/TS). For a bar chart / pictogram the **count-axis** window is `[0, max(frequencies) + 1]` (the baseline `0` is always included), and the **category axis** spans the `len(categories)` equal slots; both bounds are integers, guaranteeing integer ticks and integer-unit gridlines.
- **Equal-scale unit `U` and integer centering offsets.** `U = min(floor(aw/Wx), floor(ah/Wy))` with the committed inset `PAD`, exactly as `viewport()`; the centering half-slack is kept as an exact `Rational` and **never pre-rounded** (`offX`, `offY`). The line graph uses one `U` on both axes; the bar/pictogram count axis uses `U`, the category axis uses the committed integer pitch `P`.
- **The single projection of record.** `projX`/`projY` from `coordinate-lines.ts` — one exact `Rational` sum (`offset + Rational(value − min)·U`) rounded **exactly once** by `gridRound(num, den)` (round-half-up; Python `Fraction`, TS `Rational`/BigInt produce the identical byte stream). **No second rounding, no float, no trig.** Bars project their top via this projection; pictogram icon rows project their baselines via it; line-graph points and the clipped polyline project via it. Reusing one projection is what keeps the statistics figures byte-identical Py↔TS under the golden + 150×2 parity fixtures and the `SPI_SWEEP = 10000` sweep.
- **Clipping.** Line-graph segments reuse the exact-rational clip (`clipLine` / Liang–Barsky over `Rational`); a clip collapsing to a point is rejected and the seeded param loop redraws (deterministic), so a zero-length segment can never be emitted. Bars and icons are constructed entirely inside the window, so they need no clipping; the `within-canvas` clearance check (reused) still asserts every bar top, icon, hatch stroke, and label box lies inside the `PAD`-inset box `[PAD, VIEW_W−PAD] × [PAD, VIEW_H−PAD]`.

The pinned constants are inherited unchanged: `VIEW_W = 1000`, `VIEW_H = 700`, `PAD = 40`, `U_MIN = 24`, `DATA_MARGIN_UNITS = 1`, `MAX_LABELS_PER_AXIS = 11`, `MINOR_GRID_MIN_U = 32` (verified in `coordinate-lines.ts` lines 51–52). With the committed dataset bounds (`MAX_CATEGORIES`, `MAX_LIST_LEN`, and a committed `frequencies` ceiling), `U ≥ U_MIN` is statically reachable for every admissible dataset, exactly as in the coordinate-lines `U_MIN`-reachability argument, so the sweep never throws on scale.

### 7.2 The approved `cartesian-theme` render-mode contract (reused by name, additively extended)

Presentation, theming, and export are delegated **entirely** to `core/visual-style/cartesian-theme.{json,ts}` — the approved per-SVG style-isolation + export contract. The canonical figure is **un-themed** (§6 banner); the theme layer is presentation-only.

- **The canonical figure carries NO `cx-figure`.** The authoritative `media[0].svg` is byte-identical in shape to the coordinate-lines `figure()` output: an `<svg viewBox="0 0 1000 700" role="img" aria-label="…">` with an internal **un-scoped monochrome `<style>`** and **no `class` attribute** (verified, `coordinate-lines.ts` lines 189–192). This is also the **canonical (un-themed) accessibility-envelope form** the axe-core gate exercises. `class="cx-figure"` + the per-root `--cx-*` custom properties are added **only** by `presentationSvg()` (in-document) and `exportSvg()` (self-contained), exactly as the approved `cartesian-theme.ts` does (lines 60–69) — never by the generator, never into the stored item.
- **Per-root CSS custom properties + one common ruleset.** At presentation/export time each figure becomes a root SVG carrying class **`cx-figure`** and its **own** per-root CSS custom properties read by the single immutable `COMMON_CSS` ruleset (`cartesian-theme.json#commonCss`). Because custom properties cascade only into their own subtree, every figure is isolated — several modes on one page, reordered cards, multiple questions per worksheet, and SVGs from coordinate-lines or any other family never interfere. This is the v1.0.1 per-root isolation fix, inherited structurally.
- **The concrete additive diff to `cartesian-theme.json` (the minimum to support bars/categories/icons).** The new classes need their own variables (a bar fill cannot be driven off `--cx-line` alone, since bars must differ from the line colour and carry an independent hatch). The diff, kept consistent with the `resolveCommonCss` regex `var(--cx-[a-z-]+)` (lowercase + hyphen only, line 46):
  1. **`variables[]`** gains `--cx-bar-fill`, `--cx-bar-hatch`, `--cx-icon` (three entries, all lowercase-hyphen so the resolver matches them).
  2. **All four mode objects** gain values for the three new variables:
     - `print` (canonical): `--cx-bar-fill:#ffffff`, `--cx-bar-hatch:#666666`, `--cx-icon:#444444`.
     - `accessible`: `--cx-bar-fill:#ffffff`, `--cx-bar-hatch:#000000`, `--cx-icon:#0072b2` (the CVD-safe blue already used for `--cx-line`).
     - `premium`: `--cx-bar-fill:#eef2ff`, `--cx-bar-hatch:#6366f1`, `--cx-icon:#2563eb`.
     - `premium-dark`: `--cx-bar-fill:#1e293b`, `--cx-bar-hatch:#93c5fd`, `--cx-icon:#60a5fa`.
  3. **`commonCss`** gains three rules **inside the existing single ruleset** (one line each): `.cx-figure .cx-bar{fill:var(--cx-bar-fill);stroke:var(--cx-line);stroke-width:2.5}`, `.cx-figure .cx-bar-hatch{stroke:var(--cx-bar-hatch);stroke-width:1;fill:none}`, `.cx-figure .cx-cat{font-size:22px;fill:var(--cx-text)}`, `.cx-figure .cx-icon{fill:var(--cx-icon);stroke:var(--cx-line);stroke-width:1.5}` (`.cx-cat` reuses `--cx-text`, so it needs no new variable).
  4. **The canonical short-hex `STYLE` constants** in **both** `coordinate-lines.ts` (lines 54–65) and `coordinate_lines.py` (lines 87–97) — or the shared `core/render` module — gain the **same rules with the committed canonical (`print`-mode) colours** from §6.5, kept **byte-identical** between TS and Py, so `dataset-realises-chart` parity holds.
  5. **`GREYS`** is extended to `{#111,#333,#444,#555,#666,#888,#bbb,#fff}` byte-identically in TS and Py (the `#666` hatch and `#444` icon shades).

  This is an **extension of the approved contract, not a parallel theme**: the four modes, the `cx-figure` isolation, `presentationSvg()`/`exportSvg()`, and `resolveCommonCss` are unchanged in mechanism.
- **The four modes are reused unchanged:** `print` (monochrome authoritative, reproducing the canonical look), `premium`, `premium-dark`, and `accessible` (CVD-safe — `--cx-line:#0072b2`, `--cx-pt-core:#d55e00`). The canonical student/print default is **accessible + monochrome-safe**; the inline bar hatch and the pictogram icon shape are the **non-colour channel** that survives `print` and CVD, so colour never carries meaning alone (a bar's identity is its category label + hatch, not its hue).
- **`presentationSvg(svg, mode)` vs `exportSvg(svg, mode, w, h)`** are reused verbatim (`cartesian-theme.ts` lines 60–70): `presentationSvg` strips the canonical internal monochrome `<style>` and stamps the mode's variables on the `cx-figure` root for in-document display (relying on one document-level `COMMON_CSS`); `exportSvg` produces a **fully self-contained** clone with the mode's concrete colours baked into an internal `<style>` via `resolveCommonCss(mode)`. The canonical `media[0].svg` is **never mutated** — so switching modes never changes the stored item or its `contentHash`.

> **Py/TS byte-parity scope.** Byte-identical Py↔TS parity is required on the **canonical `media[0].svg`** and on `params`/`answer`/`distractors` only. The `presentationSvg`/`exportSvg`/render-mode/6000×4200 theme layer is a **TypeScript-only presentation concern** (`cartesian-theme.ts` exists only in TS; there is no `oracle/spi_oracle/cartesian_theme.py`, and theming output is never serialised into the item). The build plan therefore writes the **Python oracle first for the canonical SVG**, and the browser-verification + style-isolation evidence is generated from the TS theme. **No Python theme mirror is claimed or required.**

### 7.3 Materialised self-contained 6000×4200 export (reused)

The high-resolution PNG/SVG export reuses the coordinate-lines materialised export contract unchanged. The **max device envelope `7680×4320` is an inherited coordinate-lines constant**, not re-chosen here (verified in `coordinate-lines.ts` line 507–508, `exportEnvelope`: `maxEnvelope = "7680x4320"`, `scale = min(floor(7680/VIEW_W), floor(4320/VIEW_H))`). For the committed `viewBox 0 0 1000 700` this gives integer device scale `S = min(floor(7680/1000), floor(4320/700)) = min(7, 6) = 6`, a **`6000×4200`** export (the `4320` height is the binding constraint), reused **verbatim, not recomputed**. `exportSvg(svg, mode, 6000, 4200)` materialises the export **inside the cloned SVG** — the mode's resolved colours and the explicit `width="6000" height="4200"` are baked into the clone, so the export is self-contained and rasteriser-independent. Every canonical integer coordinate `v` maps to device pixel `S·v` exactly, and `(S·v)/S = v` recovers it (the exact-integer `png-coordinate-preservation` identity), because `S` is integer and the map is `S·v` — no float multiply, no tolerance. The PNG is regenerable and **never stored in the item** (so it is excluded from `contentHash` because it is never serialised, not by carve-out); `media[0].svg` — the canonical monochrome figure — remains the single authoritative deliverable that the offline HTML exporters inline and the axe-core a11y gate exercises.

### 7.4 What this reuse buys, and what it forbids

By reusing the coordinate-lines projection/viewport and the `cartesian-theme` contract rather than reinventing them, the statistics family inherits, under the same gates: byte-identical Py/TS **canonical** SVG (golden 4-seed + 150×2 parity + `SPI_SWEEP = 10000` + reproducibility), the per-root style isolation that makes multi-figure worksheets safe, the four approved render modes (additively extended for bars/categories/icons), the materialised 6000×4200 export, and the answer-recomputation / closure-agreement discipline. The reuse **forbids**, by construction: any second projection formula, any float or `sin/cos` in emitted geometry, any second theme or unscoped global CSS, any `<pattern>`/`url(#…)` in the canonical SVG (hatch is inline integer strokes — §6.6), any colour-only distinction (every bar/series/icon also differs by hatch/label/marker, and every canonical colour is in the extended `GREYS`), and any deferred chart type (pie/scatter/histogram/stem-and-leaf) leaking into a render — each is absent from every dispatch table and deterministically rejected by §6.2 and the `chart-type-in-scope` check.


---

## 8. Misconception registry proposal

All entries follow `schemas/misconception.schema.json` **exactly** (the same shape used by `core/misconceptions/geometry-angles.json`), live in a new file `core/misconceptions/data-handling.json`, and are authored at `reviewStatus: "draft"` (stated explicitly on every entry, never relying on a default). They mirror the geometry-angles discipline:

- The **required** schema fields `[misconceptionId, domain, description, observableError, reviewStatus]` are present on every entry; `title`, `typicalIncorrectMethod`, `distractorRule`, `validRange`, `feedback`, `relatedMisconceptions` are optional and used as geometry-angles uses them.
- The load-bearing transformation lives in **`distractorRule.summary`** (a plain-English wrong-pathway sentence) and, where a clean symbolic form exists, in the *optional* **`distractorRule.expression`** — exactly as `geometry-angles.json` does (`{summary:"Uses 360 on a straight line", expression:"360 - sum(givens)"}`). `distractorRule.expression` is **internal-only** and may contain math symbols (`/`, `*`, `±`, `Σ`); the symbol-hygiene gate (§8.1) does **not** touch it.
- `domain` is **`"statistics"`** on every entry — mirroring the curriculum `domain` (Section 1) and the platform precedent that ties the misconception `domain` to the curriculum domain string (`geometry-angles → "geometry"`, `linear-equations → "linear-equations"`). The earlier `"data-handling"` value is dropped.
- `validRange.levels` is `["middle-school"]`.
- Every `observableError`/`feedback`/`description` string is phrased from **displayed quantities only**, with **no internal symbols** (no `n`, no `Σ`, no `/`, no `*`, no param names) — see the hygiene gate in §8.1.

### 8.1 Registry conventions specific to this family

- **ID convention.** `MISC.STAT.<TASK_GROUP>.<SHORT_NAME>`, matching the existing `^MISC\.[A-Z0-9]+(\.[A-Z0-9_]+)+$` pattern. This is the single canonical prefix for the family; Section 13.2's coverage table cites these exact IDs (the `MISC.STATS.*` spellings are removed everywhere). Task groups: `READ` (chart/table reading), `MEAN`, `MEDIAN`, `MODE`, `RANGE`, `PICTO` (pictogram key), `PROB` (single-event probability), `GENERIC` (diagnostic-only).
- **Deterministic value adapter.** Each entry's wrong pathway is realised by one pure function `adapt(dataset, correct) -> Rational | null` in the generator (documented in `distractorRule.summary`, not invented per item), exactly as `coordinate-lines` realises its rules in code while the registry documents the transformation. The adapter consumes only the seeded dataset and the correct answer, so the distractor is reproducible under deterministic redraw and recomputable by the validator's second-route check (closure-agreement). An adapter that cannot be expressed as an exact `integer`/`exact-rational`/`fraction` returns `null` and is rejected at draw time (see §10). Returning `null` also lets an adapter **decline** for a given seed (e.g. when its output would collide with the key); the distinctness gate then backfills from the task's other eligible IDs.
- **Distractor ≠ answer is an EXACT-Rational invariant.** Before any MC interaction is emitted, every candidate distractor value is reduced to `{num,den}` (`den ≥ 1`, reduced) and compared to the key's reduced `{num,den}` by **exact-Rational equality**, never by display-string equality. This guarantees `2/8` cannot pose as "distinct" from `1/4`, and that an adapter whose output happens to equal the key on a particular seed is dropped. This is the same comparison the validator's `distractor-not-answer` and `mc-distractors-distinct-and-valid` checks recompute from `params`.
- **Distinctness gate.** Reusing the platform rule: an item that wants a multiple-choice interaction needs **≥3 DISTINCT misconception-backed distractor values** after exact-Rational de-duplication against the key and against each other; otherwise the generator does a deterministic redraw, and if the task is structurally MC-thin it is authored free-response from the start (§10.6). Distinctness is by **reduced value**, so two rules that collide on a given seeded dataset count once.
- **`distractor.rationale === registry.observableError`.** Each emitted distractor sets `distractor.rationale` to the **exact** `observableError` string of its backing misconception, satisfying the inherited `distractor-rationale-matches` check (`coordinate-lines.ts` asserts `d.rationale === MISCONCEPTIONS[d.misconceptionId].observableError`). The generator copies the registry string verbatim; a registry-parity test asserts the two are byte-identical.
- **Symbol-hygiene check (scope: `observableError` + `feedback` ONLY).** A blocking registry test `no-internal-symbols-in-observable-feedback` asserts that the `observableError` and `feedback` fields of every entry contain none of the token patterns `{ n, Σ, /, *, =, mean(, x_i }` and reference only words a student sees ("the total", "the largest value", "each picture", "the number of wanted outcomes over the total"). The gate is explicitly **NOT** applied to `distractorRule.expression` (internal, symbol-bearing by design) nor `typicalIncorrectMethod`. All 17 entries below are pre-audited to pass: probability feedback says "over" in words, never "/"; no cell contains a slash, asterisk, or equals sign.

### 8.2 Proposed entries

Every entry carries the five required fields; the table shows the student-facing `observableError`/`feedback`/`description` and the internal `distractorRule.summary` (load-bearing) with its optional `distractorRule.expression` in parentheses. `domain:"statistics"`, `reviewStatus:"draft"`, `validRange.levels:["middle-school"]` on all.

| `misconceptionId` | `title` | `description` (why students hold it) | `observableError` (no symbols) | `distractorRule.summary` (+ `expression`) — internal | `feedback` (no symbols) |
| --- | --- | --- | --- | --- | --- |
| `MISC.STAT.READ.READS_FREQUENCY_AS_CATEGORY` | Reads the frequency as the category | Confuses the two axes of a chart/table, reporting the label where a count was wanted or vice-versa. | Gave a category label where a count was asked, or a count where the label was asked. | Return the paired-axis value of the target bar/row (`swapAxis(target)`). | Read up to the bar's height for the count, and along the bottom for the category. Check which one the question asks for. |
| `MISC.STAT.READ.ADJACENT_BAR` | Reads the neighbouring bar | Misaligns the named category with its bar and reads the one next to it. | Read the bar next to the named category. | Frequency of the category one step left, or right if leftmost (`neighbourValue(target)`). | Find the named category first along the bottom axis, then read straight up that one bar. |
| `MISC.STAT.READ.MISREADS_SCALE_STEP` | Misreads the scale by one gridline | Misjudges what each gridline is worth and reads one step out. | Read the value one scale-step out. | Target plus or minus the chart's exact integer gridline spacing (`offByScaleStep(target)`). | Count the gridlines on the scale carefully; check how much each gridline is worth before reading the height. |
| `MISC.STAT.PICTO.KEY_OFF_BY_ONE` | Counts pictures, ignores the key | Treats every picture as worth one, ignoring the key's value. | Counted the pictures instead of multiplying by the key. | Number of symbols for the category, not multiplied by the key (`pictureCount(target)`). | Each picture stands for more than one. Multiply the number of pictures by the value of one picture shown in the key. |
| `MISC.STAT.PICTO.HALF_SYMBOL_DROPPED` | Ignores the part symbol | Counts only whole pictures and discards a partial one at the end of a row. | Dropped the partial picture at the end of the row. | Whole symbols times the key, omitting the partial symbol's contribution (`dropPartial(target)`). | A part-picture counts too. Add the value of the partial symbol to the value of the whole ones. |
| `MISC.STAT.MEAN.FORGOT_TO_DIVIDE` | Forgets to divide by how many | Stops at the total, forgetting the average is the total shared out. | Gave the total instead of the average. | The sum of all values, undivided (`sumOnly(list)`). | You found the total. Now share it equally by dividing by how many values there are. |
| `MISC.STAT.MEAN.DIVIDES_BY_NUM_CATEGORIES` | Divides by the number of categories | Divides the total by how many groups appear rather than by how many values there are. | Divided by the number of categories, not the number of values. | Total over the count of distinct categories (`sum/categoryCount`, exact rational). | Divide the total by how many values there are altogether, not by how many different groups there are. |
| `MISC.STAT.MEAN.EQUALS_MODE` | Reports the most common value as the mean | Conflates "typical" with "most frequent", giving the mode for the mean. | Gave the most frequent value instead of the average. | The most frequent value, declining when it equals the mean (`mode(list)`, gated; see §10.2). | The most common value is the mode. The mean is the total shared equally between all the values. |
| `MISC.STAT.MEAN.FREQTABLE_IGNORES_FREQ` | Averages the values, ignoring frequency | Averages the distinct values in the value column and ignores how often each occurs. | Averaged the distinct values and ignored how often each occurred. | Unweighted mean of the value column (`sum(distinctValues)/distinctCount`), declining when frequencies are all equal. | Each value happens more than once. Weight every value by its frequency before adding and dividing. |
| `MISC.STAT.MEDIAN.NO_ORDERING` | Takes the middle without ordering | Picks the physically central entry of the list as printed, skipping the ordering step. | Took the middle of the list as written, not the ordered list. | Middle entry, or mean of two middles, of the list in given order (`middleUnordered(list)`). | Put the values in order from smallest to largest first, then find the middle one. |
| `MISC.STAT.MEDIAN.AVERAGES_ENDS` | Averages smallest and largest | Believes the middle value is halfway between the extremes. | Averaged the smallest and largest instead of finding the middle. | Midpoint of the extremes (`(min+max)/2`, exact rational), declining when it equals the key. | The middle value is not always halfway between the smallest and largest. Order the values and find the centre one. |
| `MISC.STAT.MODE.RETURNS_FREQUENCY` | Gives the count of the mode | Reports how often the commonest value occurs rather than the value itself. | Gave how many times the commonest value appears, not the value itself. | The highest frequency, not the value carrying it (`maxFrequency(list)`). | The mode is the value that appears most often, not the number of times it appears. |
| `MISC.STAT.MODE.RETURNS_MEDIAN` | Gives the middle value as the mode | Confuses the two "averages", returning the ordered-middle value for the mode. | Gave the middle value of the ordered list instead of the most common one. | The median of the list, declining when it equals the mode (`median(list)`, gated). | The mode is the value that appears most often. The middle value of the ordered list is the median, a different measure. |
| `MISC.STAT.RANGE.MAX_ONLY` | Range is the largest value | Reads "range" as "the top value" and omits the subtraction. | Gave the largest value as the range. | The largest value alone (`max(list)`). | The range is how spread out the values are: subtract the smallest value from the largest. |
| `MISC.STAT.RANGE.COUNT_OF_VALUES` | Range is how many values | Confuses spread with the count of data points. | Gave the number of values as the range. | How many data values there are (`count(list)`). | The range measures spread, not how many values there are. Subtract the smallest from the largest. |
| `MISC.STAT.PROB.RECIPROCAL` | Writes the chance upside down | Puts the total on top and the favourable count underneath. | Wrote the chance upside down. | Total over favourable, only when this stays a valid chance below one, else declines (`total/favourable`, exact rational; see §10.5). | The chance is the number of wanted outcomes over the total number of outcomes, in that order. |
| `MISC.STAT.PROB.OVER_CATEGORIES` | Denominator is the number of categories | Uses how many groups there are as the total instead of how many outcomes. | Used the number of categories as the total. | Favourable over the count of distinct categories (`favourable/categoryCount`, exact rational). | The bottom of the fraction is the total number of outcomes altogether, not the number of different groups. |
| `MISC.STAT.PROB.OFF_BY_ONE_FAVOURABLE` | Miscounts the wanted outcomes | Miscounts the favourable outcomes by one when scanning the data. | Counted one too many, or one too few, wanted outcomes. | Favourable adjusted by one over total, staying strictly inside the open interval (`(favourable ± 1)/total`, exact rational; see §10.5). | Re-count exactly how many outcomes match what is asked, then put that over the total. |

`MISC.STAT.MEAN.EQUALS_MODE` carries `relatedMisconceptions: ["MISC.STAT.MEAN.FORGOT_TO_DIVIDE"]`; `MISC.STAT.MEDIAN.NO_ORDERING` relates to `MISC.STAT.MEDIAN.AVERAGES_ENDS`; `MISC.STAT.RANGE.MAX_ONLY` relates to `MISC.STAT.RANGE.COUNT_OF_VALUES`; `MISC.STAT.MODE.RETURNS_MEDIAN` relates to `MISC.STAT.MODE.RETURNS_FREQUENCY`. A purely diagnostic entry `MISC.STAT.GENERIC.ARITH_SLIP` (carries the required fields but **no** `distractorRule`, free-response analysis only, mirroring the diagnostic-only precedent) is registered but **never** used as an MC distractor.

**Resolved review findings on adapter correctness:**

- **`MISC.STAT.PROB.RECIPROCAL` (was `NUM_OVER_FAVOURABLE`).** Reconciled to a single rule across §5.5 and §8: the distractor is `total/favourable`. Because this is `≥ 1` for any proper probability, the §10.5 in-range filter **rejects it unless it lands strictly inside `(0,1)`** — i.e. it is only ever emitted when the misconception genuinely produces a sub-one fraction; otherwise the adapter returns `null` and the distinctness gate backfills. It is always suppressed when `favourable = total` (the certain-event key, a §10.5 endpoint). The earlier "improper fraction > 1 as a tell" and the §5.5/§8.2 disagreement are eliminated; §5.5's worked example is updated to this single rule.
- **`MISC.STAT.MEAN.EQUALS_MODE`.** Now gated on `mean ≠ mode` as an exact-Rational inequality (§10.2); the adapter returns `null` for uniform or symmetric data where `mean = mode`, so it can never equal the key. Removed entirely from the `mode_from_list` eligibility row (an adapter returning the mode value cannot back a *mode-task* distractor) and replaced there by the concrete `MISC.STAT.MODE.RETURNS_MEDIAN`.
- **`MISC.STAT.MEDIAN.AVERAGES_ENDS`.** The review correctly notes `median = (min+max)/2` is **common**, not rare, for small symmetric/evenly-spaced integer lists. The adapter now returns `null` whenever its value equals the key (exact-Rational), and §10.2 adds a dedicated pre-acceptance gate so a median MC seed is only retained when all three eligible distractor values are pairwise-distinct from the key and each other; otherwise the item redraws or is emitted free-response.
- **`MISC.STAT.READ.MISREADS_SCALE_STEP` (was `..._HALFSTEP`).** Renamed and re-specified to a **whole** gridline step (`target ± gridStep`) so the output is always an exact integer; no half-gridline value can arise.

### 8.3 Task → eligible-misconception map

This is the `task -> [ids]` eligibility table the generator consults before assembling distractors; only listed IDs may back a distractor for that task, and each adapter is validated against the task's answer type. The canonical task spellings here are used verbatim across §1–§3, §9, §11, §13, §14. Tasks `complete_frequency_table` and `read_line_graph` are intentionally **MC-ineligible** and authored free-response from the start (§10.6).

| Task | `interactionType` | `answer.type` | Eligible misconception IDs |
| --- | --- | --- | --- |
| `read_bar_chart` | `free-response` / `multiple-choice` | `integer` | `READ.READS_FREQUENCY_AS_CATEGORY`, `READ.ADJACENT_BAR`, `READ.MISREADS_SCALE_STEP` |
| `read_pictogram` | `free-response` / `multiple-choice` | `integer` | `PICTO.KEY_OFF_BY_ONE`, `PICTO.HALF_SYMBOL_DROPPED`, `READ.ADJACENT_BAR` |
| `read_table_value` | `free-response` / `multiple-choice` | `integer` | `READ.READS_FREQUENCY_AS_CATEGORY`, `READ.ADJACENT_BAR`, `READ.MISREADS_SCALE_STEP` |
| `complete_frequency_table` | `free-response` | `table-completion` | — (no MC; validated, not distracted) |
| `read_line_graph` | `free-response` | `integer` | — (no MC; see §10.6) |
| `mean_from_list` | `free-response` / `multiple-choice` | `exact-rational` | `MEAN.FORGOT_TO_DIVIDE`, `MEAN.DIVIDES_BY_NUM_CATEGORIES`, `MEAN.EQUALS_MODE` (gated `mean≠mode`) |
| `mean_from_freq_table` | `free-response` / `multiple-choice` | `exact-rational` | `MEAN.FREQTABLE_IGNORES_FREQ` (gated freqs-not-all-equal), `MEAN.FORGOT_TO_DIVIDE`, `MEAN.DIVIDES_BY_NUM_CATEGORIES` |
| `median_from_list` | `free-response` / `multiple-choice` | `integer` \| `exact-rational` | `MEDIAN.NO_ORDERING`, `MEDIAN.AVERAGES_ENDS` (gated `≠key`), `MODE.RETURNS_FREQUENCY` |
| `mode_from_list` | `free-response` / `multiple-choice` | `integer` | `MODE.RETURNS_FREQUENCY`, `MODE.RETURNS_MEDIAN` (gated `median≠mode`), `READ.ADJACENT_BAR` |
| `range_from_list` | `free-response` / `multiple-choice` | `integer` | `RANGE.MAX_ONLY`, `RANGE.COUNT_OF_VALUES`, `MEDIAN.AVERAGES_ENDS` |
| `single_event_probability` | `free-response` / `multiple-choice` | `fraction` | `PROB.RECIPROCAL`, `PROB.OVER_CATEGORIES`, `PROB.OFF_BY_ONE_FAVOURABLE` |

All `interactionType` values above are members of the schema enum `[free-response, multiple-choice, multiple-select, matching, ordering, classification]`. `complete_frequency_table` is **`free-response`** with `answer.type: "table-completion"` — `table-completion` is a valid **answer.type**, never an interactionType. The earlier `interactionType:"table-completion"` claim is removed everywhere (it would fail Ajv validation and the inherited `interaction-type` check).

Every MC-eligible row lists **≥3 candidates with a guaranteed-distinct 3rd id after the §8.2 gating**:
- `median_from_list` keeps `MODE.RETURNS_FREQUENCY` (a count, structurally unequal to a median value unless coincidental, itself de-duped) and `MEDIAN.NO_ORDERING` as the two robust distractors when `AVERAGES_ENDS` declines on a symmetric seed.
- `mode_from_list` keeps `MODE.RETURNS_FREQUENCY` and `READ.ADJACENT_BAR` when `RETURNS_MEDIAN` declines (`median = mode`).
- `range_from_list` keeps `MAX_ONLY` and `COUNT_OF_VALUES` (always distinct from the range and from each other on a spread list) when `AVERAGES_ENDS` declines.

The map is asserted complete by a blocking test `eligibility-covers-mc-tasks`: every MC-eligible task has ≥3 eligible IDs, every referenced ID exists in `data-handling.json` at `reviewStatus ≥ draft`, and (the new clause) for at least the bounded sweep every MC seed retained for that task does in fact realise 3 distinct in-range values.

### 8.4 Checker → answer-type mapping (no schema change required)

To close the "falsely-claimed schema change" audit: every answer type and interaction this family emits already exists in `question-item.schema.json`. **No schema edit is required.**

| Checker | `answer.type` it targets | Enum member exists? |
| --- | --- | --- |
| `checkExactRational` (existing) | `exact-rational`, `fraction` | yes |
| `checkInteger` (existing) | `integer` | yes |
| `checkTableCompletion` (new, operates on the free-response answer) | `table-completion` | yes |
| `checkOrderedPair` (existing, only if a read-off objective declares it) | `ordered-pair` | yes |

The mode is encoded as **single-value `integer`** for v1.0.0 (a unique mode is guaranteed by §10.2), so **no `set` answer type and no `checkUnorderedSet` is exercised** in v1.0.0; the `set`-valued multimodal/no-mode encoding is **deferred** (§10.7). There is **no `list` answer type** in the schema (the enum has `sequence` and `ordering`, not `list`); this family needs neither, so any earlier reference to a "new `list` checker" is removed. `media[].dataTableFallback` is typed as a generic `object` in the schema, so the structured `(category, frequency)` / value-list accessibility table is schema-valid with **no schema change**.

## 9. Difficulty model

The family reuses `core/difficulty/band.ts` unchanged — `bandFromScore(score)` mapping a weighted axis score in `[0,1]` to `1..5`, and `round3` for axis serialization — exactly as `domains/geometry/coordinate-lines.ts` does. **No band function is invented.** Generators populate the closed `difficulty.axes` enum only and clamp the result to the objective's `difficultyRange`.

### 9.1 Axes used

Per the seed scope this is a **reading/interpretation** family, not an algebra family. It emits exactly **five** of the sixteen schema axes and deliberately leaves the rest schema-absent (the generator emits only the axes it sets, as `coordinate-lines` emits four):

| Axis (closed schema enum) | What it measures here |
| --- | --- |
| `numericalComplexity` | Magnitude/denominators of the values and answer (larger counts, non-trivial denominators in a probability or mean). |
| `readingDemand` | Decoding the representation: a bare table < bar chart < pictogram-with-key < line graph. |
| `interpretationDemand` | Turning a read value into a statistic in context (read = low; weighting and dividing = high). |
| `reasoningSteps` | Number of distinct steps (single read = 1; mean-from-frequency-table = read, weight, sum, divide). |
| `informationDensity` | Number of categories / data values the student must track at once. |

All five are members of `question-item.schema.json#/$defs/difficultyProfile.axes` (verified: `numericalComplexity`, `readingDemand`, `interpretationDemand`, `reasoningSteps`, `informationDensity` are all present); **no invented axis names**. `scaffolding`, `representation`, and the other eleven axes are deliberately **schema-absent** (not emitted), mirroring `coordinate-lines` emitting four — stated explicitly so a reviewer does not expect all sixteen. `scaffolding` is folded into `reasoningSteps` exactly as `coordinate-lines` does (`scaffold ? -0.10 : +0.05`).

### 9.2 Scoring function

The generator's `difficulty(task, params)` follows the `coordinate-lines` shape exactly:

1. Per-task base tables `RD_BASE[task]`, `ID_BASE[task]`, `RS_BASE[task]` give the representation-/interpretation-driven components; `numericalComplexity` and `informationDensity` are computed from the **realised seeded data** (so they are monotonic in the values actually drawn), not from a table.
2. Weighted sum (weights sum to **1.00**, emphasising reasoning/interpretation over raw number size, consistent with `DIFFICULTY_MODEL.md` §2 which states `numericalComplexity` is intentionally not dominant):

```
score = 0.15*numericalComplexity
      + 0.20*readingDemand
      + 0.25*interpretationDemand
      + 0.25*reasoningSteps
      + 0.15*informationDensity
band  = bandFromScore(score)                 // shared function, no override
band  = clamp(band, objective.difficultyRange.min, objective.difficultyRange.max)
```

3. Each emitted axis value is passed through `round3` before serialization, byte-identically in Python and TS.

### 9.3 Numerical-complexity formula (data-driven, exact) — with pinned constants

Computed from the realised dataset so the value is deterministic and reproducible. **All per-task constants are pinned here** (the review correctly noted these were previously unspecified), mirroring how `coordinate-lines` pins `COORD_MAX=10`:

| Constant | Value | Used by |
| --- | --- | --- |
| `SCALE_MAX` | chart's top gridline value (realised per item; drawn from `{10, 20, 30, 50}`) | reading tasks |
| `K_MEAN` | `12` | `mean_from_list`, `mean_from_freq_table` numericalComplexity |
| `K_PROB` | `12` | `single_event_probability` numericalComplexity |
| `SPREAD_CAP` | `15` | `mode_from_list`, `range_from_list`, integer `median_from_list` |
| `DENSITY_CAP` | `8` | informationDensity for all tasks |
| `GRID_STEP` | the chart's exact integer gridline spacing (realised; one of `{1, 2, 5}`) | `READ.MISREADS_SCALE_STEP` adapter |

- **Reading tasks (`integer` answer):** `numericalComplexity = min(1, answerValue / SCALE_MAX)`. Bigger reads off a taller scale score higher.
- **Statistic tasks with `exact-rational`/`fraction` answer:** `numericalComplexity = min(1, (|num| + den) / K_task)` with `K_task ∈ {K_MEAN, K_PROB}` (mirroring the `coordinate-lines` `(|m.num| + m.den)/10` shape). A non-unit denominator (a "messy" mean, or a probability not reducible to a unit fraction) raises the score; a whole-number mean scores low.
- **List statistics (`mode`/`range`/`median` integer):** `numericalComplexity = min(1, (max - min) / SPREAD_CAP)`, so wider spreads read as harder.

### 9.4 Per-task base axes and objective band clamps

`overallBand` is always clamped into the owning objective's `difficultyRange{min,max}` after `bandFromScore`, so an objective authored at `difficultyRange:{min:1,max:2}` can never emit a band-4 item even on an adversarial seed.

| Task | `readingDemand` | `interpretationDemand` | `reasoningSteps` (base) | `informationDensity` source | Objective `difficultyRange` |
| --- | --- | --- | --- | --- | --- |
| `read_table_value` | 0.15 | 0.05 | 0.10 | row count | 1–2 |
| `read_bar_chart` | 0.30 | 0.10 | 0.15 | bar count | 1–2 |
| `read_pictogram` | 0.45 | 0.15 | 0.30 | row count | 2–3 |
| `read_line_graph` | 0.40 | 0.25 | 0.20 | point count | 2–3 |
| `complete_frequency_table` | 0.25 | 0.10 | 0.30 | row count | 2–3 |
| `mode_from_list` | 0.10 | 0.20 | 0.25 | list length | 2–3 |
| `range_from_list` | 0.10 | 0.20 | 0.30 | list length | 2–3 |
| `median_from_list` | 0.10 | 0.30 | 0.45 | list length | 2–4 |
| `mean_from_list` | 0.10 | 0.35 | 0.50 | list length | 2–4 |
| `mean_from_freq_table` | 0.30 | 0.40 | 0.70 | row count | 3–4 |
| `single_event_probability` | 0.20 | 0.45 | 0.40 | category count | 2–4 |

`informationDensity = min(1, count / DENSITY_CAP)` where `count` is the number of bars/rows/data values and `DENSITY_CAP = 8`, so it grows with the seeded dataset size and is monotonic. The `read_table_value` row is the objective that backs the previously-unmapped `read_table_value` task (the §1 objective set is reconciled to one objective per task; the task↔objective bijection is restated in §8.3 / the §11 `OBJECTIVE_BY_TASK` constant).

### 9.5 Band-reachability analysis (closes the §14.3 "every declared band reachable" gate)

The review correctly required a reachability argument given the bounded dataset sizes (`k` categories `2..6`, list length `n` `3..9`) and the narrow clamps. For each objective we exhibit a seed family that reaches each end of its declared range under the §9.2 weights; the §14.3 sweep then **confirms** reachability empirically rather than assuming it:

- **Bands 1–2 objectives** (`read_table_value`, `read_bar_chart`): minimum score with `count=2`, small `answerValue`, low base axes lands band 1; a full `count=6`, near-`SCALE_MAX` read lands band 2. Both reachable; the clamp `max=2` caps the top.
- **Bands 2–3 objectives** (`read_pictogram`, `read_line_graph`, `complete_frequency_table`, `mode`, `range`): the higher reading/reasoning bases plus larger `count`/spread push into band 3; small instances sit at band 2.
- **Bands 2–4 objectives** (`median`, `mean_from_list`, `single_event_probability`): a whole-number answer with small `count` sits at band 2; a non-unit-denominator answer (`den>1`) at full `count`/spread reaches band 4. A property test `declared-bands-reachable` asserts, over the 10,000-seed corpus, that **every** integer band inside each objective's `difficultyRange` is hit by at least one accepted seed; if any band is unreachable under the pinned constants the test fails (forcing a constant or range revision before sign-off), so the §14.3 promise is enforced, not asserted.

### 9.6 Monotonicity guarantees (asserted by property tests)

Mirroring `DIFFICULTY_MODEL.md` §3, a property test asserts the band is non-decreasing in the obvious controls, swept over the 10,000-seed corpus:

- More categories / longer data list ⇒ `informationDensity` ↑ ⇒ band non-decreasing.
- A non-unit-denominator mean/probability ⇒ `numericalComplexity` ↑ vs. an integer answer of the same shape.
- Frequency-table mean ⇒ band ≥ same-data list mean (extra weighting step in `reasoningSteps`).
- Turning scaffolding on never raises the band (the `-0.10` `reasoningSteps` adjustment).

A second test `bands-within-objective-range` asserts every generated item's `overallBand` lies inside its objective's `difficultyRange`, across all seeds. The median row's `answer.type` is set from the **computed denominator** (`den=1 ⇒ integer`, `den=2 ⇒ exact-rational`), so the difficulty/answer-type pairing never mislabels an integer median; the §11.4 `answer-type-consistency` check (which asserts `integer ⇔ den=1`) therefore passes.

## 10. Edge-case and degeneracy policy

Every rule here is a **deterministic pre-acceptance gate** evaluated from the seeded dataset before the item is realised. A seed that fails any gate triggers the platform's deterministic redraw (re-seed forward by the documented step), never a silent mutation of data; this preserves byte-identical Python/TS behaviour and the 10,000-seed reproducibility guarantee. Each gate is also a named validator check so a stored item can be re-audited. **Every "distractor ≠ key" or "distractor distinct" decision is an exact-Rational comparison on reduced `{num,den}` (§8.1), never a display-string comparison.**

### 10.1 Empty and degenerate datasets — excluded

- **Non-empty.** The data list / frequency table must have `dataCount ≥ DATA_MIN_task` (lists: `n ≥ 3`; frequency tables: `≥3` categories with total frequency `Σf ≥ 5`). Empty or single-value datasets are redrawn. Validator check: `dataset-nonempty`.
- **Non-constant for spread statistics.** For `range_from_list` and `median_from_list`, `max > min` is required; a constant list gives range 0 and a trivial median, so such seeds are redrawn. Validator check: `dataset-has-spread`. Consequently a **`range = 0` (uniform) item is unreachable for `range_from_list`/`median_from_list`**; uniform data is only reachable for `mean_from_list`/`mode_from_list` (where a flat list is a legitimate teaching case), and the earlier "range = 0 (exact)" worked example is scoped to those tasks only — it does not contradict this gate.
- **At least two distinct categories** for any chart/probability task, so a chart is meaningful and a probability is neither 0 nor 1 unless that is the deliberate objective. Validator check: `categories-distinct`.

### 10.2 Ties, multi-modality, "no mode", and median collisions

- **`mode_from_list` — unique single-value mode for v1.0.0.** Require a **unique** mode whose frequency strictly exceeds the next: `maxFreq ≥ secondFreq + 1`. This is the single pinned v1.0.0 convention: **all-distinct ("no mode") and multi-modal lists are redrawn/excluded**, the mode is encoded as a single `integer` (not a `set`), and **no empty-set / all-values convention is emitted in v1.0.0**. The `set`-valued multimodal/no-mode encoding is **deferred** (§10.7). Validator check: `mode-unique`. The earlier three-way statement (empty set / total set / redraw) is resolved to this one disposition.
- **`median_from_list` — both parities, exact, typed from `den`.** Odd `n` ⇒ exact `integer` middle; even `n` ⇒ `(a+b)/2` as an `exact-rational` **only when `den=2`**, else (same-parity middles) the average is a whole number tagged `integer`. A gate `median-answer-typed` sets the stored `answer.type` from the computed denominator (`den=1 ⇒ integer`, `den=2 ⇒ exact-rational`), so an integer median is never mislabelled `exact-rational`; the coverage matrix lists `median_from_list` as `integer | exact-rational`, not pinned to `exact-rational`. `checkExactRational` accepts equivalent fractions, so checking is unaffected.
- **Median MC anti-collision gate (new, closes the major finding).** Because `median = (min+max)/2` is **common** for small symmetric/evenly-spaced integer lists (e.g. `[2,4,6]→4=(2+6)/2`; `[1,3,5,7]→4=(1+7)/2`), an MC `median_from_list` seed is retained **only when**, computed as exact Rationals:
  `median ≠ (min+max)/2` **AND** `median ≠ middleUnordered(list)` **AND** the third eligible distractor (`MODE.RETURNS_FREQUENCY`) `≠ median` **AND** the three distractor values are pairwise-distinct.
  Otherwise the generator redraws; if redraw repeatedly fails the MC budget the item is emitted **free-response**. This prevents the silent answer-equality and the distribution distortion the §13.5 redraw report would otherwise show. `MEDIAN.AVERAGES_ENDS` is documented as the rule that collides for symmetric lists and is **dropped-then-backfilled** (the row still has a distinct 3rd id). Validator check: `median-mc-distinct`.
- **`MEAN.EQUALS_MODE` and `MODE.RETURNS_MEDIAN` distractors** are each only eligible when the relevant exact-Rational inequality holds for that seed (`mean ≠ mode`; `median ≠ mode`); otherwise the adapter returns `null` and the distinctness gate backfills. §10.2 guarantees a unique mode exists but **not** that `mode ≠ mean` / `mode ≠ median`, which is exactly why these inequalities are explicit MC gates. For `mean` tasks the dataset must additionally be **non-uniform** (a hard MC gate, consistent with the uniform-cap) so `mode(list)` cannot equal the mean by construction.

### 10.3 Mean must be exact and "interesting enough"

- The mean is computed as a `fractions.Fraction` / `Rational{num,den}` (`den ≥ 1`, reduced) — never a float. No surds ever arise (standard deviation is deferred entirely, §10.7), so exactness is structural. Validator check: `mean-exact-rational`.
- **`mean_from_freq_table` degeneracy gates (closes the missing-item finding).** Beyond `Σf ≥ 5`: (a) **not all frequency mass in one row** — at least two rows have `frequency ≥ 1`, so the weighted mean is not the trivial "the one value with any count"; (b) for MC, **frequencies not all equal** — when every frequency is equal the weighted mean equals the unweighted mean and `MEAN.FREQTABLE_IGNORES_FREQ` would collide with the key, so such seeds are MC-ineligible (still valid free-response). Validator checks: `freqtable-mass-spread`, and `freqtable-mc-frequencies-distinct` for the MC path.
- **Anti-triviality (optional per objective).** Objectives targeting band ≥3 may require `den > 1` (a non-integer mean) so the answer is not a giveaway; band 1–2 objectives may require `den = 1` (whole-number mean) for accessibility. Either way the requirement is a deterministic gate, not a post-hoc filter.

### 10.4 Pictogram keys divide evenly

- The pictogram key `k` (value per symbol) must satisfy `frequency_c mod k == 0` for **every** category `c`, OR the seed must permit an **exact** half symbol (`frequency_c mod k ∈ {0, k/2}` only when `k` is even). No category may require a third- or fifth-of-a-symbol. Off-key seeds are redrawn. Validator check: `pictogram-key-divides`.
- The chosen `k` is drawn from a small whitelist `{2, 5, 10}` so the key is realistic and the partial-symbol case is always a clean half. This is what makes `MISC.STAT.PICTO.KEY_OFF_BY_ONE` and `MISC.STAT.PICTO.HALF_SYMBOL_DROPPED` well-defined **integer** adapters.

### 10.5 Probability is an exact, bounded fraction with reachable MC distractors

- `single_event_probability` returns `favourable/total` as a reduced `fraction`, with `0 < favourable < total` (strictly proper and non-zero) unless an objective explicitly targets a certain/impossible event. Validator check: `probability-in-open-unit-interval` (or the explicit-endpoint variant).
- **In-range distractor filter (single rule for all three probability adapters).** Every probability distractor value is dropped unless it lands strictly inside `(0,1)` and is `≠` the key (exact Rational). Concretely: `PROB.RECIPROCAL` (`total/favourable`) is kept only on the rare seeds where it is sub-one and is otherwise `null`; `PROB.OFF_BY_ONE_FAVOURABLE` is suppressed when `favourable = 1` (low side) or `favourable = total-1` (high side) would push it to 0 or 1; `PROB.OVER_CATEGORIES` is kept only when `favourable/categoryCount ∈ (0,1)` and `≠` the key. The distinctness gate backfills any drop.
- **Minimum outcome-space gate for probability MC (closes the missing-item finding).** A probability item is only offered as **MC** when `total ≥ TOTAL_MIN_MC = 6`. Small spaces (e.g. `P=2/3` with `total=3`) have too few in-range misconception values to reach 3 distinct distractors; below the threshold the item is **free-response**. Validator check: `probability-mc-space-sufficient`. Endpoint cases (certain / impossible / exactly one-half taught deliberately) are **free-response only** and never attempt MC.

### 10.6 Multiple-choice only where 3 distinct defensible distractors exist

- An MC interaction is emitted **only** when the task's eligibility row (§8.3) yields **≥3 distinct, in-range, defensible** distractor values after exact-Rational de-duplication against the key. The "in-range" filter drops any adapter output that is negative, exceeds the chart scale, or (for probabilities) leaves the open unit interval. Validator check: `mc-distractors-distinct-and-valid` (reuses the platform ≥3-distinct gate; comparison is exact-Rational).
- If a seed yields fewer than 3, the generator **redraws**. If a task is structurally MC-thin it is authored **free-response from the start** and never attempts MC: `complete_frequency_table` (`answer.type: table-completion`, `interactionType: free-response`); `read_line_graph` (`integer` free-response). These appear in §8.3 with no eligible IDs by design, and a test `mc-thin-tasks-are-free-response` asserts they never emit `interactionType: multiple-choice` (and never the non-existent `interactionType:"table-completion"`).
- Distractor `display` strings are materialised from the **displayed** dataset values (no internal symbols), consistent with the misconception `feedback` hygiene gate, and each distractor's `rationale` is set equal to its misconception's `observableError` (§8.1) for the inherited `distractor-rationale-matches` check.

### 10.7 Deferred chart types and statistics — deterministically excluded

The v1.0.0 generator's task enum and chart-type enum **structurally omit** the deferred items; they are not reachable by any seed, and no dispatch table, validator branch, or checker references them. A blocking test `no-deferred-types-emitted` sweeps the 10,000-seed corpus and asserts no generated item carries a deferred `chartType` or a deferred statistic.

| Deferred (NOT in v1.0.0) | Reason | Exclusion mechanism |
| --- | --- | --- |
| Pie charts | Angle computation needs runtime trig / non-integer sector boundaries, violating the integer-coordinate canonical-SVG rule. | Not in `chartType` enum; sweep test. **No pie-sector branch appears in `chart-realises-data`.** |
| Histograms (unequal class widths, frequency density) | Frequency density is a derived ratio easy to author non-exactly; class boundaries add interpretation load beyond scope. | Not in `chartType` enum; sweep test. |
| Scatter / correlation reading | "Correlation" reading is qualitative/judgemental, not an exact-rational answer; defer with the regression line. | Not in task enum; sweep test. **No scatter-point branch in `chart-realises-data`.** |
| Regression / line of best fit | Requires least-squares (irrational slopes) — violates the exact-rational / no-surds rule. | Not in task enum; sweep test. |
| Standard deviation / variance with surds | Generally irrational — explicitly out per the EXACT-MATH constraint. | No such task exists; sweep test + `mean-exact-rational` keeps the family surd-free. |
| Stem-and-leaf | Deferred as a representation only (the underlying list stats are in scope via lists); revisit in a later minor. | Not in `chartType` enum; sweep test. |
| Multi-modal / "no mode" reporting; `set`-valued mode + `checkUnorderedSet` | v1.0.0 requires a unique single-value `integer` mode (§10.2). | `mode-unique` redraw gate; `set` answer type and its checker are not wired in v1.0.0. |
| Grouped-data estimated mean (midpoint method) | Introduces estimation + interval midpoints beyond exact small-data scope. | Not in task enum; sweep test. |

`chart-realises-data` (v1.0.0) recomputes **only** bar tops, pictogram glyph counts (plus the exact partial-glyph clip width), line-graph lattice points, and frequency-table cells from `params`; the previously-listed pie-sector and scatter-point branches are removed (they were dead code contradicting the deferred-exclusion guarantee). They live only in the deferred-version note.

### 10.8 Determinism and audit summary

Every gate above is (a) a pre-acceptance check driving deterministic redraw and (b) a named validator check recomputed from `params`. Combined with the single-source seeded dataset (chart, prompt, answer, solution, accessibility data-table all derived from one dataset), the byte-identical Python/TS oracle on the **canonical `media[0].svg`, params, answer, and distractors** (the presentation/export theme layer is a TypeScript-only concern and is *not* mirrored in Python — see the cluster-C render notes), and the exact-Rational distractor comparisons throughout, this guarantees that exclusion is deterministic and reproducible, that no degenerate or deferred item can be silently emitted, and that the validator can independently confirm both the figure (`svg-realises-data`) and the answer (`closure-agreement`) for every accepted item.


---

## 11. Solver and independent-validator design

> **Canonical task enum and objective map (pinned here so §11 is self-consistent with §4.6/§8.3/§13.2).**
> This cluster keeps the **eleven-task taxonomy** with an **11:1** task↔objective bijection (the reconciliation chosen across clusters in response to the cross-cluster taxonomy blocker). The `task` literal is the single source of truth in `params.task`; every check below keys on these exact spellings:
>
> `read_bar_chart`, `read_pictogram`, `read_table_value`, `read_line_graph`, `complete_frequency_table`, `mean_from_list`, `mean_from_freq_table`, `median_from_list`, `mode_from_list`, `range_from_list`, `single_event_probability`.
>
> The validator's `objective-mapping` check uses an `OBJECTIVE_BY_TASK` constant (modelled exactly on coordinate-lines' constant) giving one authored objectiveId per task. All objectiveIds use the canonical authored spelling **`SPI.MIDDLE.STAT.<TOPIC>.<MICRO>.01`** — `MIDDLE` stage segment, `STAT` domain segment, ≥ 5 dotted segments — never `SPI.MS.STATISTICS.*`:
>
> | `task` | `objectiveId` | `answer.type` | `interactionType` |
> |---|---|---|---|
> | `read_bar_chart` | `SPI.MIDDLE.STAT.READ.BAR_VALUE.01` | `integer` | `free-response` \| `multiple-choice` |
> | `read_pictogram` | `SPI.MIDDLE.STAT.READ.PICTOGRAM_VALUE.01` | `integer` | `free-response` \| `multiple-choice` |
> | `read_table_value` | `SPI.MIDDLE.STAT.READ.TABLE_VALUE.01` | `integer` | `free-response` \| `multiple-choice` |
> | `read_line_graph` | `SPI.MIDDLE.STAT.READ.LINE_GRAPH.01` | `integer` | `free-response` \| `multiple-choice` |
> | `complete_frequency_table` | `SPI.MIDDLE.STAT.FREQ.COMPLETE_TABLE.01` | `table-completion` | **`free-response`** |
> | `mean_from_list` | `SPI.MIDDLE.STAT.AVG.MEAN_LIST.01` | `integer` \| `exact-rational` | `free-response` \| `multiple-choice` |
> | `mean_from_freq_table` | `SPI.MIDDLE.STAT.AVG.MEAN_FREQ_TABLE.01` | `integer` \| `exact-rational` | `free-response` \| `multiple-choice` |
> | `median_from_list` | `SPI.MIDDLE.STAT.AVG.MEDIAN_LIST.01` | `integer` \| `exact-rational` | `free-response` \| `multiple-choice` |
> | `mode_from_list` | `SPI.MIDDLE.STAT.AVG.MODE_LIST.01` | `integer` | `free-response` \| `multiple-choice` |
> | `range_from_list` | `SPI.MIDDLE.STAT.AVG.RANGE_LIST.01` | `integer` | `free-response` \| `multiple-choice` |
> | `single_event_probability` | `SPI.MIDDLE.STAT.PROB.SINGLE_EVENT.01` | `fraction` | `free-response` \| `multiple-choice` |
>
> **`interactionType` is from the schema enum only** (`question-item.schema.json` ⇒ `free-response`, `multiple-choice`, `multiple-select`, `matching`, `ordering`, `classification`). `complete_frequency_table` is **`free-response`** with `answer.type:"table-completion"`. **`table-completion` is NOT an `interactionType`** — that earlier claim is withdrawn; it is an `answer.type` value only. No schema change is requested for any item field: `set`, `table-completion`, and `fraction` are already members of the `answer.type` enum, and `dataTableFallback` is already typed `{type:"object"}` (free-form) — **no `answer.type` enum edit and no schema change are required for this family.**

### 11.1 The deterministic dataset is the single source of truth

Every `gen.stats.data-handling` item is generated from one seeded artefact, the **dataset record**, materialised once in `params.dataset` and never recomputed downstream. The field schema below is the **single canonical `DataSet` vocabulary**; §4.2/§6.1 reference these exact names and types (`kind` discriminator, `frequencies`, `values`, `glyphValue`):

```
params.dataset = {
  kind: "frequency" | "list",        // exactly two discriminator values
  categories?: string[],             // "frequency" kind: bar / pictogram / table / pie x-labels, display order
  frequencies?: integer[],           // "frequency" kind: parallel to categories; counts ARE integers >= 0
  values?: integer[],                // "list" kind: raw data list for mean/median/mode/range
  seriesLabels?: string[],           // "list" kind used as a time-series (line graph): x-axis labels parallel to values
  glyphValue?: integer               // pictogram key (1 glyph = glyphValue items), exact integer divisor
}
params.task = <one of the eleven literals above>
```

A **line graph / time-series** is a `list` dataset carrying `seriesLabels`; a **frequency table** is a `frequency` dataset. There is **one** `kind` vocabulary (`"frequency" | "list"`) used identically by the generator and by the validator's `params-in-domain` check, eliminating the §4.2/§11.1 discriminator drift. The chart SVG, the prompt blocks, the `answer`, the `solution.steps`, the distractors, and the accessibility `dataTableFallback` are all **pure functions of `params.dataset` plus `params.task`**. The solver never reads the chart back; the chart never carries a value the dataset does not. This is what makes every validator check below a closed-loop recomputation rather than a heuristic.

### 11.2 Solver: exact statistics, no irrationals

The solver computes each task's canonical answer over `core/exact-math/rational.ts` (`Rational{num,den}`, den ≥ 1, reduced) with a byte-identical `oracle/spi_oracle` Python mirror over `fractions.Fraction`. Statistics in v1.0.0 are closed over the rationals:

| Task (micro-objective) | Statistic | Exact form | `answer.type` |
|---|---|---|---|
| `read_bar_chart` / `read_pictogram` / `read_table_value` | one cell lookup | integer | `integer` |
| `read_line_graph` | one plotted reading | integer | `integer` |
| `complete_frequency_table` | row/total completion | integer cells | `table-completion` |
| `mean_from_list` / `mean_from_freq_table` | Σ(f·x)/Σf | `Rational` reduced | `integer` **iff** den = 1, else `exact-rational` |
| `median_from_list` | middle / mean-of-two-middles | `Rational`, den ∈ {1,2} | `integer` **iff** den = 1, else `exact-rational` |
| `mode_from_list` | unique argmax frequency | **single integer** | `integer` |
| `range_from_list` | max − min | integer | `integer` |
| `single_event_probability` | favourable/total | `Rational` reduced, value ∈ (0,1) | `fraction` |

**Mode is a single value in v1.0.0.** The earlier `set`/multimodal/no-mode mode contract is **deferred in its entirety**: `mode_from_list` requires a **unique** mode (`maxFreq ≥ secondFreq + 1`, exact integer comparison) enforced by the §10.2 redraw gate, so `answer.type` is always `integer`. The `set`-valued (`checkUnorderedSet`) machinery and the empty-set / all-values "no-mode" conventions are **moved to the deferred list** and never exercised in v1.0.0 — this removes the dead/contradictory `set` path. There is **no `list` answer type** anywhere: `list` is not a member of the `answer.type` enum; line-graph reads use `integer`, probability uses `fraction`, and ordered structures (none are needed in v1.0.0) would use the enum's `sequence`/`ordering` — but none are.

**Mean/median answer-type tagging is computed from the denominator.** `median_from_list` is tagged `integer` when the mean-of-two-middles is a whole number (same-parity middles ⇒ den = 1) and `exact-rational` only when it is a half-integer (different-parity middles ⇒ den = 2); the coverage matrix lists it as `integer | exact-rational`, **never pinned to `exact-rational`**, so the validator's `answer-type-consistency` (`integer ⇔ den = 1`) passes. The same rule applies to `mean_from_list` / `mean_from_freq_table`.

**Determinacy guards baked into generation (not just validated).** The `mulberry32`-seeded **deterministic redraw** (`core/seeded-random`, byte-identical Python/TypeScript) rejects, before emission:
- **Mode:** any list without a strictly unique mode (no-mode/multimodal excluded; the single v1.0.0 convention).
- **Median / range:** **`dataset-has-spread` (max > min)** — so **uniform `range = 0` lists are excluded for `median_from_list` and `range_from_list`**; the `range = 0` case is reachable **only** for `mean_from_list`/`mode_from_list` (and any deliberate range-0 teaching item would be a separately-gated, capped sub-case, not a side effect). This pins the §4.5/§10.1 interaction.
- **Probability:** favourable/total reduced with **`0 < value < 1`** (proper, in the open unit interval), `gcd(num,den) = 1`, `den ≥ 1`; **certain (P = 1) / impossible (P = 0) / one-half** are free-response-only and **redrawn away for MC**, and **MC additionally requires `total` large enough that ≥ 3 in-range, distinct misconception distractors exist** (a minimum-outcome-space gate — e.g. `P = 2/3, total = 3` has too few in-range foils and is redrawn for MC).

No surd, standard deviation, regression line, quartile/IQR interpolation, pie sector, scatter point, or histogram class is ever produced — those tasks/statistics are **absent from the closed `task` enum and from every dispatch table**, so they are **deterministically excluded, never silently included**.

### 11.3 Independent validator: shape and contract

The validator is a **separate module** that imports nothing from the generator's closures; it rebuilds the figure and re-derives the answer from `params.dataset` alone, exactly as `domains/geometry/coordinate-lines.ts::validate(item)` does for coordinate-lines. It returns the platform-standard shape:

```
validate(item) -> {
  status: "pass" | "fail",
  validatorVersion: <string>,
  checks: [ { name: <string>, result: "pass" | "fail" | "skip", detail: <string> }, … ]
}
```

`status` is `pass` iff every non-skipped check passes. The result is **not serialised into the item**, so functional parity (same `status`, same failing `name`s) suffices between the Python and TypeScript validators rather than byte parity — mirroring the coordinate-lines rule.

**Byte-parity scope (explicit).** Independent **Python ⇄ TypeScript byte parity** is required on the **canonical `media[0].svg`** and on `params` / `answer` / `distractors` only. The `presentationSvg` / `exportSvg` render-mode/theme layer is a **TypeScript-only presentation concern** (matching the approved `core/visual-style/cartesian-theme.ts`, which has **no Python mirror**) and is **not** byte-mirrored in the Python oracle; the §11.4 style-isolation/export checks therefore run against the **TS** theme module, and the Python oracle emits only the canonical monochrome SVG. No "Python theme byte-parity" obligation is claimed.

### 11.4 Inherit / override / replace — the inherited coordinate-lines battery is NOT transferred verbatim

Statistics charts carry category text, a pictogram key, and axis-unit text that the inherited coordinate-lines checks were never designed for. The table below pins, per check, whether it is **inherited verbatim**, **replaced**, or **scoped/overridden**. This is the load-bearing reconciliation; the three blockers (`no-answer-label-in-svg` character blocklist, `tick-labels-integer` scraping category strings, `media-to-scale` for pictograms) are resolved here.

| Inherited check | Disposition for statistics |
|---|---|
| `params-in-domain`, `objective-mapping`, `closure-agreement`, `provenance-complete`, `version-fields-present`, `media-present`/`media-absent-for-text-task`, `svg-realises-data`, `axes-stronger-than-grid`, `a11y-fields-present`, `a11y-non-color`, the seven distractor checks | **Inherited verbatim** (semantics unchanged; the cross-family CI harness treats reused names uniformly) |
| `no-answer-label-in-svg` | **REPLACED** by `no-statistic-in-svg` (string-equality predicate, see below). The inherited `,`/`/`/`=` **character blocklist must NOT transfer** — a pictogram key text `"1 picture = 5"` contains `=`, category labels contain `,`/`/` (`"km/h"`, `"Year 7, boys"`), so the verbatim check would reject every pictogram and most labelled bar charts. |
| `tick-labels-integer` | **Inherited but scoped to the count axis only.** Category strings are emitted under `class="cx-cat"`, **never** `cx-ticklbl`; `cx-ticklbl` is reserved for the integer count-axis labels. The check scrapes `<text class="cx-ticklbl">…` and still requires `-?\d+`, which now stays green because no category string is ever a `cx-ticklbl`. A companion `category-label-correctness` scrapes `cx-cat`. |
| `media-to-scale` | **Scoped:** applied verbatim to **bar / line-graph** charts (`toScale === true`); **NOT applied to pictograms** (glyph-count figures, not height-to-scale), which carry `toScale:false` and instead pass `pictogram-key-exact`. (This reconciles §6.7/§11.4: pictograms are `toScale:false`, no "NOT TO SCALE" label is emitted, and the verbatim `media-to-scale` gate is **not** inherited for them.) |
| `equal-axis-scale`, `premium-spec-parity`, `plot-point-target-absent`, `line-clipped-within-viewport`, `lattice-anchors-readable` | **Not applicable / replaced** by the statistics geometry checks (`axis-scale-consistency`, `chart-realises-data`). |

#### Provenance, mapping, and schema (every item)

| Check name | Asserts |
|---|---|
| `params-in-domain` | `dataset.kind ∈ {"frequency","list"}` and matches `task`; counts are non-negative integers; `Σf` / list length within the task's seeded bounds; no deferred field (no pie/scatter/histogram/class shape) present |
| `objective-mapping` | `item.objectiveIds` equals `[OBJECTIVE_BY_TASK[task]]`, the single authored `SPI.MIDDLE.STAT.<TOPIC>.<MICRO>.01` for `task` |
| `interaction-type` | `interactionType ∈ {"free-response","multiple-choice"}` (the inherited predicate); `complete_frequency_table` is always `free-response` |
| `answer-type-consistency` | `answer.type` equals the §11.2 row: for mean/median, `integer ⇔ canonical.den = 1` and `exact-rational ⇔ den ≠ 1`; `mode_from_list ⇒ integer`; probability ⇒ `fraction`; `complete_frequency_table ⇒ table-completion` |
| `provenance-complete` | `origin = "generated"`, `rightsStatus` present |
| `version-fields-present` | `generatorId` / `generatorVersion` equal the family constants |

#### Answer correctness (closure-agreement, second route)

| Check name | Asserts |
|---|---|
| `closure-agreement` | the validator's **independent** recomputation from `dataset` equals `answer.canonical` under canonical-stringify — mean recomputed as `Rational(Σf·x, Σf)` reduced; median by independent sort; probability by independent gcd-reduction. **All comparisons are exact-Rational equality on the reduced `{num,den}`**, so `2/8` and `1/4` are the same value (never "distinct"); the mode single value `{num:k,den:1}` is compared by the same reduced-Rational equality (membership reduces each element first), and `complete_frequency_table` cells are compared cell-by-cell as exact integers |
| `mean-divisor-is-total` | for `mean_from_freq_table`, the denominator route uses `Σf`, not the category count (guards divide-by-categories at the answer level) |
| `probability-reduced-and-bounded` | `0 < favourable < total`, `gcd(num,den)=1`, `den ≥ 1`, value strictly inside `(0,1)` |
| `table-completion-consistency` | for `complete_frequency_table`, every blank's expected value is recomputed from row/column totals and matches `answer.canonical` (`checkTableCompletion`, mapping to the **`table-completion`** answer.type — a valid enum member, **no schema change**) |

#### Chart-realises-data (the statistics analogue of `svg-realises-data`)

| Check name | Asserts |
|---|---|
| `svg-realises-data` | the validator rebuilds the figure from `params.dataset` through the **same canonical SVG pipeline** (viewBox `0 0 1000 700`, `gridRound` round-half-up over `Rational`, no runtime trig) and asserts the stored `media[0].svg` **byte-for-byte**; Python and TypeScript canonical renderers are byte-identical |
| `chart-realises-data` | the **geometric** realisation matches the dataset exactly, decoded back out of the SVG: each **bar** top y-coordinate `= gridRound(project(frequency))` for its category; each **pictogram** row's glyph count `= frequency / glyphValue` (whole glyphs plus the exact fractional last-glyph clip width); each **line-graph** plotted point `= gridRound(project(index, value))` on the integer lattice. **Pie and scatter branches are absent** — those types are deferred and unreachable, so the validator carries no pie-sector / scatter-point recomputation (their realisation lives only in the deferred-version note) |
| `category-label-correctness` | the ordered `<text class="cx-cat">…` category labels equal `dataset.categories` (or `seriesLabels`) **in order**; separately, the `<text class="cx-ticklbl">…` count-axis labels are integers in ascending order matching the chosen scale. Category strings appear **only** under `cx-cat`; no `cx-ticklbl` text is non-numeric |
| `axis-scale-consistency` | one declared integer units-per-pixel scale reproduces every gridline and every datum (the bar/line analogue of coordinate-lines `equal-axis-scale`) |
| `media-to-scale` | `media[0].toScale === true` for **bar / line** charts; **not asserted for pictograms** (see inherit table), which instead pass `pictogram-key-exact` |
| `pictogram-key-exact` | `glyphValue` divides each plotted frequency into the stated whole + fractional glyphs with no rounding drift; the integer-coordinate partial-glyph clip width is exact |

#### No-statistic-leakage (replaces `no-answer-label-in-svg`)

| Check name | Asserts |
|---|---|
| `no-statistic-in-svg` | for **derived-answer** tasks (mean/median/mode/range/probability, and a line/point read of an *unlabelled* datum), **no figure `<text>` equals the canonical answer's `display` string, nor any distractor `display`** — a **string-equality / token match against `answer.display` and each distractor display**, **NOT** the inherited `,`/`/`/`=` character blocklist. Category labels, the pictogram key line (`"1 picture = 5"`), and axis-unit text (`"km/h"`) are permitted by construction. **Pinned tests:** a pictogram whose key text is `"1 picture = 5"` **passes**; a figure whose `<text>` equals the answer **fails** |
| `read-task-value-present` | conversely, for direct `read_*` tasks the queried value **must** be legible in the chart/table (a read task whose answer is invisible is invalid) |
| `axis-labels-not-leaking` | axis/key labels disclose units and scale only, never the computed statistic |

#### Distractor checks (multiple-choice interaction) — reused verbatim, statistics-specific eligibility

| Check name | Asserts |
|---|---|
| `min-three-distractors` | `≥ 3` distractors |
| `distractors-distinct-misconceptions` | misconceptionIds are **distinct** and **registered in `core/misconceptions/data-handling.json`**, using the **single `MISC.STAT.<GROUP>.<NAME>` namespace** (the `MISC.STATS.*` spelling is withdrawn). Examples: `MISC.STAT.MEAN.DIVIDE_BY_CATEGORY_COUNT`, `MISC.STAT.MEAN.FREQTABLE_IGNORES_FREQ`, `MISC.STAT.MEDIAN.MIDDLE_OF_UNSORTED`, `MISC.STAT.MEDIAN.AVERAGES_ENDS`, `MISC.STAT.RANGE.MAX_ONLY`, `MISC.STAT.MODE.HIGHEST_VALUE`, `MISC.STAT.PROB.ODDS_AS_FRACTION` |
| `distractor-value-matches-rule` | each distractor value equals its misconception adapter recomputed from `dataset` (no hand-authored numbers) |
| `distractor-not-answer` | no distractor equals the canonical answer, **compared as exact-Rational equality on the reduced `{num,den}`** (display-string distinctness is insufficient: `2/8` must not slip past `1/4`). Computed over exact Rationals for **every** adapter **before MC emission** |
| `distractor-rationale-matches` | **`distractor.rationale === registry.observableError`** for each id — the generator sets each item's `distractor.rationale` equal to the registry `observableError` string (displayed-value language, no internal symbols), so the inherited check passes |
| `distractor-feedback-present` | registry `feedback` exists for each id |
| `exactly-one-correct` | exactly one option flagged correct and equal to `answer.display` |

**Statistics-specific MC eligibility gates (computed as exact Rationals before MC is offered; otherwise redraw or emit free-response).** These close the collision findings:

- **`median_from_list`:** require `median ≠ (min+max)/2` **AND** `median ≠ middleUnordered(list)` **AND** `median ≠` the third eligible distractor, all as exact Rationals. `MISC.STAT.MEDIAN.AVERAGES_ENDS` `(min+max)/2` collides with the key for **every symmetric / evenly-spaced list** (`[2,4,6]→4=(2+6)/2`; `[1,3,5,7]→4`; `[3,3,3]→3`), so it is **frequently dropped-then-backfilled**; the §10.2 redraw report shows this drop, and each median/range MC row retains a guaranteed-distinct 3rd id after the drop (median backfilled via `MISC.STAT.MEAN.EQUALS_MODE`-class foils gated below; range via `MISC.STAT.RANGE.MAX_ONLY`).
- **`mean_from_list` / `mean_from_freq_table`:** `MISC.STAT.MEAN.EQUALS_MODE` (distractor = `mode(list)`) is eligible **only when `mean ≠ mode`** (exact Rational inequality) and the dataset is **non-uniform** (hard MC gate, not merely the uniform-cap). For `mean_from_freq_table` additionally require **frequencies not all equal**, else `MISC.STAT.MEAN.FREQTABLE_IGNORES_FREQ` (unweighted mean) collides with the weighted mean.
- **`mode_from_list`:** `MISC.STAT.MEAN.EQUALS_MODE` is **removed** from this row (an adapter returning the mode value cannot back a mode-task distractor); it is replaced with **concrete** mode foils — `MISC.STAT.MODE.RETURNS_MEDIAN` and `MISC.STAT.MODE.HIGHEST_VALUE` (the highest value, not the most frequent) — keeping ≥ 3 distinct registered ids.
- **`single_event_probability`:** the odds foil is the **single reconciled rule** `favourable/(total − favourable)` (odds-as-fraction, `MISC.STAT.PROB.ODDS_AS_FRACTION`), eligible **only when it lies in `(0,1)`** i.e. `favourable < total/2`; the discredited `total/favourable` (always ≥ 1, never a valid probability) is removed. An **in-range filter `distractor value ∈ (0,1)`** redraws/backfills any foil leaving the unit interval or equalling the key, and MC is **suppressed when `favourable = total` (P = 1)**.

#### Per-SVG style-isolation + materialised-export (TypeScript theme layer; reused from `core/visual-style/cartesian-theme.ts`)

The validator re-derives presentation and export copies from the **canonical** `media[0].svg` using the **TS** `presentationSvg` / `exportSvg` and asserts the v1.0.2 isolation contract structurally, exactly as `coordinate-lines-style-isolation.test.ts` does. The **canonical `media[0].svg` itself carries the internal unscoped monochrome `<style>` and does NOT carry `class="cx-figure"`** (byte-identical to coordinate-lines); `class="cx-figure"` + the per-root `--cx-*` variables are added **only** by `presentationSvg`/`exportSvg` at presentation/export time.

| Check name | Asserts |
|---|---|
| `axes-stronger-than-grid` | `stroke-width(cx-axis=3) > cx-grid-major(1.25) > cx-grid-minor(0.75) > 0`, preserved on bar/line backgrounds |
| `tick-labels-integer` | all `cx-ticklbl` count-axis labels are integers (category text lives under `cx-cat`, so this stays green) |
| `style-isolation-per-root` | `presentationSvg(svg, mode)` strips the canonical `<style>` and stamps `class="cx-figure" style="--cx-…"`; the figure depends only on the **one** scoped `COMMON_CSS` ruleset; **no unscoped global `.cx-*{…}` block exists** (the v1.0.1 defect is structurally impossible). No hard-coded DOM `id` and no `url(#…)` appears in the canonical SVG (so the inline hatch must be id-free — see §12.3) |
| `export-self-contained` | `exportSvg(svg, mode, 6000, 4200)` bakes concrete colours via `resolveCommonCss(mode)` (no `var(--…)`, no `<link>`/`@import`/`url()`), carries `width="6000" height="4200"`; the **6000×4200 (S=6)** PNG is materialised inside the cloned SVG. The envelope **`maxEnvelope = 7680×4320` is the inherited coordinate-lines constant** (`coordinate-lines.ts exportEnvelope`), so `S = min(⌊7680/1000⌋, ⌊4320/700⌋) = min(7,6) = 6` and 6000×4200 are **reused verbatim, not recomputed** |
| `modes-differ` | `print` (monochrome authoritative) and `premium` resolve to different ink; `premium-dark` line/text stay light on the dark background |
| `canonical-svg-unmutated` | re-running `generate(seed,…)` yields the same `media[0].svg`; theming never mutates the canonical item |

**Concrete `cartesian-theme` diff committed by this family** (so `svg-realises-data` parity and `no-colour-only-information` both hold):

1. **New variables** appended to `cartesian-theme.json variables[]`: `--cx-bar-fill`, `--cx-bar-hatch`, `--cx-cat`, `--cx-icon` (all lowercase-and-hyphen, satisfying `resolveCommonCss`'s `var(--cx-[a-z-]+)` regex).
2. **Per-mode values added to ALL FOUR mode objects** (`print`, `premium`, `premium-dark`, `accessible`): `print` uses the canonical greys (`--cx-bar-fill:#bbb`, `--cx-bar-hatch:#555`, `--cx-cat:#333`, `--cx-icon:#111`); `premium`/`premium-dark`/`accessible` restyle hue but each remains legible without colour (the redundant channel is geometric, see §12.3).
3. **`commonCss`** gains, inside the **single** `.cx-figure …` ruleset: `.cx-figure .cx-bar{fill:var(--cx-bar-fill);stroke:var(--cx-cat);stroke-width:2}.cx-figure .cx-cat{font-size:20px;fill:var(--cx-cat)}.cx-figure .cx-icon{fill:var(--cx-icon)}` (hatch strokes inherit `--cx-bar-hatch`).
4. **The canonical short-hex `STYLE` constant in BOTH `coordinate-lines.ts` and `coordinate_lines.py`** (or the shared `core/render` module) gains the **same** rules with concrete greys, kept **byte-identical** across languages: `.cx-bar{fill:#bbb;stroke:#333;stroke-width:2}.cx-bar-hatch{stroke:#555;stroke-width:1.5}.cx-cat{font-size:20px;fill:#333}.cx-icon{fill:#111}`.
5. **`GREYS` is extended (with family/owner sign-off) in BOTH languages, byte-identically**, to the exact committed set used by the canonical bar fill / hatch stroke / icon: `GREYS = {#111, #333, #444, #555, #888, #999, #bbb, #fff}` (adding **`#999`** for the mid-grey hatch; `#bbb`/`#555`/`#333`/`#111` are already present). The canonical statistics SVG's fill/stroke colours are a **subset** of this extended `GREYS`, pinned by `no-colour-only-information` and an integrity test.

### 11.5 Sweep and parity obligations

The validator runs inside the standard harness: **golden (4 seeds)**, **parity 150×2** (Python ⇄ TypeScript — the **canonical item + SVG byte-equal** and the validator `status`/failing-names equal; the TS-only theme layer is excluded from byte-parity per §11.3), **`SPI_SWEEP=10000`** with full reproducibility and a distribution report, and a **blocking artifact-integrity test** over the immutable approved-generator fixtures. The distribution report includes a **per-task band-reachability proof** — every band declared in each objective's `difficultyRange` must be reached by some seed given the bounded dataset sizes (`k` ∈ 2..6, `n` ∈ 3..9); an unreachable declared band **fails** the sweep gate (mirroring coordinate-lines' `U_MIN`-reachability argument), and the MC-drop/backfill rate for `median_from_list` (the `AVERAGES_ENDS` collision) is reported as the redraw anomaly it is, not a silent loss. Any `status:"fail"` in the sweep, any byte divergence in `svg-realises-data`, or any closure disagreement aborts the build.

---

## 12. Accessibility model

The accessibility contract is **information-equivalence**: a non-visual user must recover the *entire dataset* and answer the item without the chart. Because the chart and the data-table are both pure functions of `params.dataset`, equivalence is guaranteed by construction and enforced by the validator. `media[].dataTableFallback` is typed `{type:"object"}` (free-form) in `question-item.schema.json`, so the structured table the family stores is **schema-valid with no schema change**.

### 12.1 Canonical SVG accessibility envelope (this is the un-themed canonical form)

The **canonical authoritative `media[0].svg`** — the byte-parity artefact, identical in shape to coordinate-lines — carries the **internal unscoped monochrome `<style>` and NO `class="cx-figure"`**:

```
<svg xmlns="…" viewBox="0 0 1000 700" role="img" aria-label="<alt>">
  <title>…</title><desc>…</desc>
  <style>…canonical short-hex greyscale (the STYLE constant)…</style>
  …figure…
</svg>
```

`class="cx-figure"` and the per-root `--cx-*` variables are added **only** by `presentationSvg`/`exportSvg` at presentation/export time (§11.4); the canonical figure is never pre-stamped with them, so byte-for-byte `svg-realises-data` parity against the reused coordinate-lines pipeline holds.

- **`role="img"` + `aria-label`** so assistive tech announces the figure as a single labelled image.
- **`<title>`** — short chart identity (e.g. *"Bar chart: favourite fruit, 5 categories"*).
- **`<desc>`** — the long description: chart type, axis/category meaning, scale, salient trend, in displayed-value language with no internal symbols.
- **No hard-coded DOM `id`s, no `url(#…)`.** Elements are addressed by **class** (`cx-axis`, `cx-grid-major`, `cx-bar`, `cx-bar-hatch`, `cx-icon`, `cx-cat`, `cx-ticklbl`, …), never by `id`. This lets `cartesian-theme` isolate figures per-root and lets many items share one page; `style-isolation-per-root` enforces it. The **hatch is id-free** (see §12.3).

### 12.2 Item-level accessibility object

Each item carries the schema's `accessibility` block plus the per-media fallbacks:

```
accessibility: {
  spokenMath:  <answer & key quantities as speakable text, e.g. "the mean is three over two">,
  altText:     <one-line chart summary, == media[0].altText>,
  longDescription: <== media[0].longDescription, == <desc>>,
  nonColorIndicators: true
}
media[0]: { …, toScale, altText, longDescription, dataTableFallback }
```

**`dataTableFallback` — the exact dataset, information-equivalent to the chart.** It is a structured table rendered from `params.dataset` (free-form `{type:"object"}`, no schema change): for `frequency` datasets (bar / pictogram / table), the (category, frequency) rows plus the total and any key (`1 ◼ = glyphValue`); for `list` datasets, the ordered values; for a line graph (`list` + `seriesLabels`), the (label, value) pairs; for `complete_frequency_table` the full table **with the blanks left blank in the prompt fallback** (the completed answer table appears only in the solution export). The validator's **`chart-realises-data`** and a dedicated **`datatable-matches-dataset`** check assert the fallback reproduces `params.dataset` cell-for-cell — so the table is provably the chart's information twin.

### 12.3 No colour-only information, across ALL render modes

Colour never carries meaning alone; every colour-coded element is **paired** with a redundant non-colour channel that lives in the **canonical geometry**, so it survives all four modes unchanged:

- **bars:** the category **label** under each bar (class `cx-cat`) and, when bars must be told apart without axis position, an **id-free greyscale hatch** — drawn as **inline integer-coordinate `<line>`/`<path>` stroke elements** (class `cx-bar-hatch`) clipped to the bar rect in the deterministic element order, **never** an SVG `<pattern>` + `fill=url(#id)` (which §6.6's no-`id`/no-`url(#…)` rule forbids). `bar-pattern-distinct` checks these inline hatch elements;
- **pictograms:** a printed **glyph key** and counted glyphs (count, not colour, conveys magnitude);
- **line graphs:** distinct **point markers** + direct labels and **dashed vs solid stroke patterns**, not hue.

The canonical SVG is **greyscale-authoritative**; the four `cartesian-theme` render modes (`premium`, `premium-dark`, **`accessible` = CVD-safe Okabe–Ito-style palette**, `print` = monochrome) only restyle via per-root CSS variables and **must each remain legible without colour**. The validator enforces this at two levels: `no-colour-only-information` (canonical figure fill/stroke colours ∈ the **extended `GREYS` = {#111,#333,#444,#555,#888,#999,#bbb,#fff}** committed in §11.4, in both `coordinate-lines.ts` and `coordinate_lines.py` byte-identically) and `nonColorIndicators === true`; the redundant channel (label / marker / hatch) is checked structurally. Pie and scatter are deferred, so no pie/scatter colour-coding exists to reconcile.

### 12.4 No answer in the accessibility text

For derived-answer tasks, the `<desc>`, `altText`, `longDescription`, and `dataTableFallback` describe the **data**, never the result — mirrored by the validator's `no-answer-in-accessibility-text` (string-equality against `answer.display`) and `no-statistic-in-svg`. `spokenMath` *does* speak the answer, but it lives in the item's `accessibility`/solution channel, not in the figure or the prompt fallback, so a screen-reader user solves the same problem a sighted user does. For direct `read_*` tasks the queried value is legible in both the chart and the data-table (`read-task-value-present`).

### 12.5 Conformance gates

- **WCAG 2.1 AA**: text and non-text contrast verified for `print`, `premium`, `premium-dark`, and `accessible`; `accessible` mode uses the CVD-safe palette and is the default for the a11y export.
- **axe-core gate**: **0 critical / 0 serious** violations on every exported worksheet, answer-key, and solution page (the family-wide gate); a non-zero count blocks delivery.
- **Printable monochrome**: `print` reproduces the canonical authoritative appearance with no loss of information; the **6000×4200 (S=6)** export (with the inherited `maxEnvelope = 7680×4320`) is materialised inside the cloned SVG via `exportSvg(svg,"print",6000,4200)` and is self-contained (no external CSS/network), so offline KaTeX worksheets and answer keys render identically without colour.
- **Offline**: all accessibility assets (data-table fallback, spokenMath, long description) are inline in the bank-json and survive round-trip, with no runtime dependency.


---

## 13. Review-pack plan

The review pack is the single human-facing artefact the curriculum authority decides on. It is **fully machine-generated** from the same seeded datasets that drive generation, byte-reproducible, and mirrors the coordinate-lines pack (`docs/review/coordinate_lines_review_pack.{md,json}` + `coordinate_lines_svgs/` + `coordinate_lines_manifest.json` + `coordinate_lines_distribution.json` + `coordinate_lines_visual_audit.html`). Nothing in the pack is hand-authored; the Python oracle is the source of every figure, answer, and number, and the TS app reproduces the **canonical** item JSON + canonical media SVG byte-for-byte.

### 13.1 Artefacts and oracle commands

| Artefact | Path | Producer (oracle-first) |
| --- | --- | --- |
| Review pack (human) | `docs/review/stats_data_handling_review_pack.md` | `oracle/make_review_pack_stats.py` |
| Review pack (machine) | `docs/review/stats_data_handling_review_pack.json` | `oracle/make_review_pack_stats.py` |
| Per-item figures | `docs/review/stats_svgs/<task>__<interaction>__<seed>.svg` | same |
| Visual audit + premium gallery + raster export | `docs/review/stats_data_handling_visual_audit.html` | `oracle/make_visual_audit_stats.py` (TS-rendered theme; see §13.4) |
| Distribution report (>=10k) | `docs/review/stats_data_handling_distribution.json` | `oracle/run_stats_data_handling.py` |
| Browser style-isolation evidence | `docs/review/stats_data_handling_browser_verification.json` | TS audit harness (real-browser `getComputedStyle` + export pixels) |
| Manifest | `docs/review/stats_data_handling_manifest.json` | `oracle/make_stats_manifest.py` |

The Python oracle authors the canonical item JSON and canonical media SVG; the TS app re-derives each through `validate(item)` and asserts byte-equality, and the pack is **gated by parity** before it is allowed to ship. The presentation/export theme layer (visual audit + browser verification) is generated by the **TypeScript** harness only — see §13.4.

### 13.2 Coverage matrix (every task × interaction × band, every chart, every misconception)

The pack opens with the curriculum block (objective table, `answerTypes` mathematical-only assertion, the prerequisite-graph edges authored in cluster A, exactly as the coordinate-lines pack), then enumerates, per v1.0.0 task, at least one worked seed for **every (interaction, band) cell that the distribution report proves reachable**, plus, for each MC task, one fully expanded distractor set with misconception attributions.

The v1.0.0 task set is the **single canonical eleven-task taxonomy fixed in cluster A/§4.6** — `read_bar_chart`, `read_pictogram`, `read_table_value`, `complete_frequency_table`, `read_line_graph`, `mean_from_list`, `median_from_list`, `mode_from_list`, `range_from_list`, `mean_from_freq_table`, `single_event_probability` — eleven tasks, **1:1** with eleven authored objectives (cluster A having split `median_mode_range_from_list` into `MEDIAN_LIST.01` / `MODE_LIST.01` / `RANGE_LIST.01` and added `READ.TABLE_VALUE.01`). These literal spellings are used verbatim here and in every other section; `task` is a closed enum and the sole source of truth in `params.task`. The explicit `OBJECTIVE_BY_TASK` map (cluster A) services the `objective-mapping` check for every one of the eleven:

| Task | `objectiveId` | Chart/source | `answer.type` | `interactionType` | Band span |
| --- | --- | --- | --- | --- | --- |
| `read_bar_chart` | `SPI.MIDDLE.STAT.READ.BAR_CHART.01` | bar chart | `integer` | `free-response` / `multiple-choice` | 1–2 |
| `read_pictogram` | `SPI.MIDDLE.STAT.READ.PICTOGRAM.01` | pictogram (integer key) | `integer` | `free-response` / `multiple-choice` | 1–2 |
| `read_table_value` | `SPI.MIDDLE.STAT.READ.TABLE_VALUE.01` | frequency table | `integer` | `free-response` / `multiple-choice` | 1–2 |
| `complete_frequency_table` | `SPI.MIDDLE.STAT.FREQ.COMPLETE_TABLE.01` | frequency table | `table-completion` | **`free-response`** | 2–3 |
| `read_line_graph` | `SPI.MIDDLE.STAT.READ.LINE_GRAPH.01` | line graph (Cartesian reuse) | `integer` | `free-response` / `multiple-choice` | 1–3 |
| `mean_from_list` | `SPI.MIDDLE.STAT.AVG.MEAN_LIST.01` | integer data list | `exact-rational` | `free-response` / `multiple-choice` | 2–4 |
| `median_from_list` | `SPI.MIDDLE.STAT.AVG.MEDIAN_LIST.01` | integer data list | **`integer` \| `exact-rational`** | `free-response` / `multiple-choice` | 2–3 |
| `mode_from_list` | `SPI.MIDDLE.STAT.AVG.MODE_LIST.01` | integer data list | `integer` | `free-response` / `multiple-choice` | 1–2 |
| `range_from_list` | `SPI.MIDDLE.STAT.AVG.RANGE_LIST.01` | integer data list | `integer` | `free-response` / `multiple-choice` | 1–2 |
| `mean_from_freq_table` | `SPI.MIDDLE.STAT.FREQ.MEAN_TABLE.01` | frequency table | `exact-rational` | `free-response` / `multiple-choice` | 3–4 |
| `single_event_probability` | `SPI.MIDDLE.STAT.PROB.SINGLE_EVENT.01` | spinner/category table | `fraction` | `free-response` / `multiple-choice` | 2–3 |

**`interactionType` is always a valid schema enum member.** The item schema's `interactionType` enum is exactly `["free-response","multiple-choice","multiple-select","matching","ordering","classification"]` — `table-completion` is **not** in it. `complete_frequency_table` therefore carries `interactionType: "free-response"` with `answer.type: "table-completion"`; the multi-cell-vs-single-cell distinction governs only whether MC is offered, never the interaction name. No item ever carries `interactionType: "table-completion"`, so none is rejected by the precompiled Ajv validator at the storage/import/export boundary. This proposal requests **no `interactionType` schema change**.

**`answer.type` for median is computed, never pinned.** `median_from_list` stores `integer` when the even-n average has `den = 1` (same-parity middles) and `exact-rational` when `den = 2` (half-integer); the median solver sets the stored type from the computed `den` so the inherited `answer-type-consistency` check (`integer ⇔ den = 1`) passes. The coverage matrix above lists `integer | exact-rational` for this reason and never pins median to `exact-rational`.

**`answer.type` for mode is single-value `integer` only in v1.0.0.** The `set`/multimodal and no-mode encodings are **deferred** with the multimodal sub-objective; the §10.2 mode-unique redraw gate (`maxFreq >= secondFreq + 1`) excludes all-distinct and multimodal lists, so `checkUnorderedSet`/the `set` answer type are not exercised by any v1.0.0 mode task. No empty-set / all-values "no mode" convention is emitted in v1.0.0. (`checkUnorderedSet → set` and `checkTableCompletion → table-completion` both target existing answer.type enum members — **no answer.type schema edit is required** for either, exactly as none is required for the others. No `list` answer type is introduced anywhere: `list` is not an enum member, and no task needs an ordered-list answer — line graph / probability use `integer` / `ordered-pair` / `fraction`.)

Each worked seed prints: prompt blocks (`prompt.blocks` typed content + `prompt.instruction`) with the chart cited via a `media-ref`/`table-ref` block; the figure (`![figure](stats_svgs/...)`) for chart-backed tasks; alt text and `longDescription`; the canonical answer with its computed `answer.type` and `display` (rationals as `{num,den}`); the **single source dataset** echoed as the `media[].dataTableFallback` accessibility table (the schema types `dataTableFallback` as a generic object, so the `{categories[],frequencies[]}` / `{values[]}` table is schema-valid **with no schema change**) so a reviewer sees the chart, the table, the prompt, the answer and the solution all derive from one seed; the worked `solution.steps` (with per-step `marks` and `estimatedTimeSeconds`); and a reproduce line `generate(<seed>, {'task': ..., 'interactionType': ...})`.

**One fully-worked schema-valid exemplar.** Because no approved family ships a spec without a concrete example, the pack's first section embeds **one fully-populated `question-item.schema.json` item per task family** (a read task, the `table-completion` task, a `mean_from_list`, a `median_from_list` half-integer case, a `mode_from_list`, and a `single_event_probability`) showing `prompt.blocks`, `answer.canonical` (`{num,den}` for rationals, the `{cells:[...]}` shape for `table-completion`, the `{num,den}` reduced fraction for probability), `distractors[]`, `solution.steps` with `marks`, `difficulty.axes`, `media[].svg` + `dataTableFallback`, `accessibility`, `provenance{origin:"generated",rightsStatus:"academy-owned"}`, and `lifecycle{state:"generated"}`. Each exemplar is asserted to pass the precompiled standalone validator in the integrity test of §13.6. Where the schema has explicit `allOf` constraints only for `integer`/`exact-rational`, the `table-completion` `{cells:[...]}` and probability `fraction` canonicals are stated to be **free-form canonical validated by their checker**, not by a schema `if/then` — no schema change is claimed for them.

**Chart-type coverage.** v1.0.0 ships bar chart, pictogram, frequency table, line graph. The pack carries a **"Deferred chart types and statistics"** section that names each excluded type and the deterministic exclusion: pie chart, scatter/correlation, histogram, stem-and-leaf, and the statistics standard deviation / variance / regression line / interpolated quartiles (IQR) are **never emitted** — `paramsInDomain` rejects their task ids, the registry exposes no task entry, and an integration test asserts these ids `generate`-throw and never appear in a 10k sweep, so exclusion is enforced, not implicit (the digest's "deterministically excluded, never silently included" rule).

**Misconception coverage — IDs cited verbatim from the cluster-D registry.** A "Misconceptions exercised" table lists every misconception id with its `observableError` and `feedback` (displayed-value language only, no internal symbols/expressions), the tasks it is eligible for, and one MC seed that actually instantiates it as a distractor. The ids use the **single canonical namespace `MISC.STAT.<TASK_GROUP>.<SHORT_NAME>`** fixed in cluster D (matching `^MISC\.[A-Z0-9]+(\.[A-Z0-9_]+)+$`) — **not** the divergent `MISC.STATS.*` spellings; this pack cites the cluster-D ids exactly so the `eligibility-covers-mc-tasks` test (every referenced id exists in `core/misconceptions/data-handling.json`) passes. Representative ids: `MISC.STAT.MEAN.FORGOT_TO_DIVIDE` (reports the sum), `MISC.STAT.MEAN.DIVIDE_BY_CATEGORY_COUNT` (divides by number of distinct values not total frequency), `MISC.STAT.MEAN.FREQTABLE_IGNORES_FREQ` (averages the values column, ignoring frequencies), `MISC.STAT.MEAN.EQUALS_MODE` (reports the mode), `MISC.STAT.MEDIAN.UNORDERED_MIDDLE` (middle of the unsorted list), `MISC.STAT.MEDIAN.EVEN_PICKS_ONE` (one central value instead of the average of two), `MISC.STAT.MEDIAN.AVERAGES_ENDS` (averages min and max), `MISC.STAT.MODE.IS_FREQUENCY` (reports the frequency not the value), `MISC.STAT.RANGE.INCLUDES_COUNT`, `MISC.STAT.PROB.NUM_OVER_FAVOURABLE` (odds-as-fraction `favourable/(total−favourable)`, in-range only when `favourable < total/2`), `MISC.STAT.PICTOGRAM.IGNORES_KEY` (counts symbols, ignoring the key). **`PROB_UNREDUCED` is not listed** — an un-reduced fraction is not a distractor, because `checkExactRational`/the fraction checker accept equivalent forms (`2/8` and `1/4` are the same answer). Each row's `feedback`/`observableError` strings are pre-checked to contain none of the banned tokens (`/`, `*`, `Σ`, `n`, `mean(`, `x_i`); probability feedback is spelled in words — "over the total", not "/").

**Distractor coupling and exact-equality invariants asserted in the pack.** For every MC seed the pack records that:
- each `distractor.rationale` is set **equal to that misconception's registry `observableError`** (the inherited `distractor-rationale-matches` check requires byte-equality), and
- **no distractor value equals the key**, compared as **reduced exact Rationals** (`{num,den}` after reduction), not display strings — so `2/8` cannot slip past `1/4`. Distinctness among distractors is likewise exact-Rational, not display-string.

Several adapter collisions are documented as **drop-then-backfill** because their value frequently equals the key on small integer data, exactly as the cluster-B/§10 gates require:
- `MISC.STAT.MEDIAN.AVERAGES_ENDS` `(min+max)/2` equals the median for **every symmetric / evenly-spaced list** (`[2,4,6]→4`, `[1,3,5,7]→4`), so median MC requires a pre-acceptance gate `median ≠ (min+max)/2 ∧ median ≠ middleUnordered(list) ∧ median ≠ third-distractor`, all exact Rationals, before MC is allowed; otherwise the seed is redrawn or emitted free-response. The pack confirms the median/range rows still carry a guaranteed-distinct third id after this drop.
- `MISC.STAT.MEAN.EQUALS_MODE` `mode(list)` equals the mean for uniform/symmetric data, so for mean tasks its eligibility is gated on `mean ≠ mode` (exact inequality) and a non-uniform dataset (a hard MC gate, beyond the §4.5 uniform cap). It is **removed entirely** from the `mode_from_list` eligibility row (an adapter returning the mode cannot back a mode distractor) and replaced there by a concrete misconception (returns the median / a value adjacent to the mode); the row is re-confirmed to retain ≥3 distinct ids.
- `MISC.STAT.MEAN.FREQTABLE_IGNORES_FREQ` equals the weighted mean when all frequencies are equal, so `mean_from_freq_table` MC carries a "frequencies not all equal" gate.

### 13.3 Deterministic MC + answer-free figures (named checks in the pack)

The pack records, per MC seed, the **≥3 DISTINCT misconception-backed distractors** rule and the deterministic-redraw behaviour: if a seed cannot produce three distinct misconception-attributed distractors — all in range and none equal to the key under exact-Rational comparison — with a correct option, it is **deterministically redrawn** (same mulberry32/`seeded_random.py` stream, byte-identical Py/TS), and the redraw is reproducible — never random suppression. For `single_event_probability` MC the pack additionally records a **minimum outcome-space size (`total`) gate** so that ≥3 distinct in-range distractors in `(0,1)` distinct from `P` are reachable, and the §10.5 endpoint policy: certain (`P = 1`, including `favourable = total`) / impossible (`P = 0`) / `P = 1/2` are **free-response only** and MC redraws away from them. Each MC item lists `distractors[{id,value,display,misconceptionId,rationale}]` and asserts the §13.2 invariants.

For chart-backed tasks the figure must be **answer-free**: it shows the data, never the answer. This is the statistics analogue of coordinate-lines' answer-free figure rule, but it is **a replacement, not the inherited check verbatim** (see §13.6 inherit/override table). Named figure checks surfaced in the pack JSON per item:

- `svg-realises-data` — recomputed SVG equals stored SVG byte-for-byte (figure rebuilt from `params`), **inherited verbatim**.
- `chart-realises-data` (statistics-specific) — every plotted bar top, pictogram glyph count (plus the exact partial-glyph clip width), frequency-table cell, and line-graph lattice point equals the seed dataset (no figure can drift from the `dataTableFallback` the answer is computed from). For v1.0.0 this covers **only** bar tops, pictogram glyph counts, and line-graph lattice points — there is **no pie-sector or scatter-point branch** (those types are deferred and absent from every dispatch table).
- `no-statistic-in-svg` (statistics-specific, **replaces** the inherited `no-answer-label-in-svg`) — predicate is **string-equality**: no figure `<text>` equals the canonical answer's `display` string or any distractor `display`. It does **not** use the inherited character blocklist `','`,`'/'`,`'='`. Category labels, axis-unit text (`km/h`, `Year 7, boys`), and the pictogram key line (`1 picture = 5`) may by construction contain `'='`, `'/'`, `','`. A pinned test asserts a pictogram with key text `1 picture = 5` **passes** and a figure whose `<text>` equals the answer **fails**.
- `frequency-table-blank-cell` (statistics-specific) — `complete_frequency_table` figures leave the asked cell empty.
- `pictogram-key-exact` (statistics-specific) — the rendered key glyph value equals `dataset.glyphValue`.
- `tick-labels-integer`, `axes-stronger-than-grid`, `equal-axis-scale` (line graph) — **inherited verbatim** from the Cartesian renderer discipline, with the rider below.
- `category-label-correctness` — category strings are scraped from class **`cx-cat` only** and equal `dataset.categories`; the integer count-axis labels are scraped from class **`cx-ticklbl`**. No category string is ever emitted under `cx-ticklbl`, so the inherited `tick-labels-integer` check (which requires every `cx-ticklbl` `<text>` to match `^-?\d+$`) stays green; a check asserts no `cx-ticklbl` `<text>` is non-numeric and that category strings appear only under `cx-cat`.

**`media[].toScale` policy is stated once.** Bar charts and line graphs carry `media[0].toScale = true` and are governed by the inherited `media-to-scale` check; **pictograms carry `toScale: false`** (they are glyph-count figures, not height-to-scale) and are governed by `pictogram-key-exact` **instead** — so the family does **not** inherit the `media-to-scale` gate verbatim for pictograms. No "NOT TO SCALE" label is emitted.

### 13.4 Render modes + 6000×4200 export

Every pack figure and the visual-audit gallery reuse `core/visual-style/cartesian-theme.{json,ts}` by name, with **no parallel theme**, and the render-mode/presentation/export layer is a **TypeScript-only presentation concern** (there is no `oracle/spi_oracle/cartesian_theme.py`, and none is added): byte-parity Py/TS applies to the **canonical `media[0].svg` and to `params`/`answer`/`distractors` only**, never to the themed or exported copies, which are not serialised into the item. The visual audit and browser-verification evidence are generated from the TS theme.

**The canonical figure does NOT carry `class="cx-figure"`.** Matching coordinate-lines exactly, the authoritative `media[0].svg` carries the internal **unscoped monochrome `<style>`** block and **no** `class="cx-figure"`; this is the accessibility-envelope (un-themed) canonical form on which `svg-realises-data` parity is asserted. `class="cx-figure"` plus the per-root `--cx-*` variables are stamped **only by `presentationSvg(svg, mode)`** (which strips the canonical `<style>`) and `exportSvg(svg, mode, w, h)` (which bakes a self-contained `<style>` via `resolveCommonCss`). The four modes — **premium**, **premium-dark**, **accessible** (CVD-safe), **print** (monochrome authoritative) — coexist on one page with zero cascade leakage because each figure root carries its own custom properties read by the one common `.cx-figure` ruleset; **colour never carries meaning alone** — every series is paired with a hatch/pattern and a printed category label, satisfying `nonColorIndicators`.

**Concrete theme diff (committed in this proposal).** The new series classes require an explicit, byte-disciplined extension on five fronts; `resolveCommonCss`'s `var\((--cx-[a-z-]+)\)` regex constrains new names to lowercase-and-hyphen:
1. Add three variables to `cartesian-theme.json` `variables[]`: `--cx-bar-fill`, `--cx-bar-hatch`, `--cx-icon`.
2. Give all **four** mode objects a value for each new variable (print uses the canonical short-hex greys below; premium/premium-dark/accessible use mode-appropriate, CVD-safe ink that still pairs colour with hatch).
3. Append three rules to `commonCss`: `.cx-figure .cx-bar{fill:var(--cx-bar-fill)}`, `.cx-figure .cx-cat{font-size:24px;fill:var(--cx-text)}`, `.cx-figure .cx-icon{fill:var(--cx-icon)}` (the hatch stroke reads `--cx-bar-hatch`).
4. Add the **same** rules with the canonical short-hex colours to the `STYLE` constant in **both** `domains/geometry/coordinate-lines.ts` (or the shared render module) **and** `oracle/spi_oracle/*` (Python), kept **byte-identical**, so `svg-realises-data` parity holds.
5. **Extend `GREYS`** in both languages, byte-identically, with the committed greyscale palette below (with family/owner sign-off), because the inherited `no-colour-only-information` check asserts every canonical `fill:/stroke:#hex` is a subset of `GREYS`, whose current members are exactly `#111 #333 #444 #555 #888 #bbb #fff`.

**Committed canonical greyscale palette** (the authoritative monochrome figure): `.cx-bar` fill `#888`; bar hatch stroke `#333`; `.cx-icon` fill `#333`; `.cx-cat` label `#111`. All four are already members of the current `GREYS` set, so the only addition is a one-line confirmation in the test; if a future shade outside the set is wanted it is added to `GREYS` in both languages with sign-off. A pinned test asserts every `fill/stroke` hex in the canonical statistics SVG is a subset of the (current) `GREYS`.

**Id-free hatch.** Because the canonical-SVG rule forbids any `id` attribute and any `url(#…)` reference (the safe-multi-item-export invariant), bar hatching is drawn as **inline clipped stroke geometry** — a deterministic, integer-coordinate set of `<line>` elements emitted in fixed element order inside each bar rect — never an SVG `<pattern>` + `fill=url(#id)`. The `bar-pattern-distinct` check inspects those inline hatch elements, not a pattern id, and the no-`id`/no-`url(#)` invariant is re-asserted.

**Export.** The audit emits `presentationSvg()` display copies and `exportSvg()` self-contained copies, and materialises the **6000×4200 high-resolution PNG export inside the cloned SVG** for premium / accessible / print. The sizing is reused verbatim, not recomputed: `maxEnvelope = "7680x4320"` is the inherited coordinate-lines constant (`exportEnvelope` in `coordinate-lines.ts`), giving `S = min(⌊7680/1000⌋, ⌊4320/700⌋) = min(7,6) = 6` over `viewBox "0 0 1000 700"` → 6000×4200, exactly as the coordinate-lines manifest's `rasterExports` block.

### 13.5 Distribution report (≥10,000 seeds)

`stats_data_handling_distribution.json` mirrors `coordinate_lines_distribution.json`: top-level `generatorId`, `generatorVersion`, `sweep: 10000`, `invalid: 0`. Per task: `count`, `freeResponse`, `multipleChoice` (**FR-vs-MC split**), `objectiveRange`, `bands{}`, `bandPct{}` (**per-task band %**), `unreachableBands`, `overConcentratedBands`, and **exact-answer-kind counts** `integerAnswers` / `exactRationalAnswers` / `fractionAnswers` / `tableCompletionAnswers`. Family-specific aggregates: `mean{integer, properFraction}`, `median{integer, halfInteger}` (the `den ∈ {1,2}` split that drives the median answer-type tag), `probability{reducedProper, unitFraction, zeroOrOne}`, `mode{single}` (multimodal/no-mode are excluded by the §10.2 gate, so they do not appear in v1.0.0). A `redraw` block reports `sampleSeeds`, and for `freeResponse`/`multipleChoice` the `avgAttempts`, `rejectionRatePerAccept`, and `fractionNeedingRedraw` (**redraw rate**) — the median-MC `AVERAGES_ENDS` drop-then-backfill and the probability in-range/endpoint redraws are expected to show here and are documented as designed, not anomalous.

**Band-reachability is proven, not assumed.** Because the §14.3 sweep gate requires "every declared band reachable", the report includes a per-task **reachability proof** analogous to coordinate-lines' `U_MIN`-reachability: for each task it shows that, given the bounded dataset sizes (categories `k ∈ 2..6`, list `n ∈ 3..9`) and the pinned weighted-score formula with the pinned per-task constants (`K_task`, `spreadCap_task`, `DENSITY_CAP`, `scaleMax`, `gridStep` — all given concrete values in cluster C, not left symbolic), at least one parameter assignment lands in each band of the objective's `difficultyRange`. Any task whose narrow clamp (e.g. a `read_*` task capped at band 2) cannot reach a band declares that band **out of range in the objective**, not unreachable — so `unreachableBands` is empty by construction and the sweep gate cannot fail on an undeclared-but-unreachable band.

Any residual band concentration within a reachable range is recorded as a **non-blocking** `calibrationNotes` entry — the approved exact mathematics is never bent to balance percentages, matching the `interpret_mx_c` precedent. `invalid` must be `0` (every swept item passes `validate`) or the sweep gate fails.

### 13.6 Manifest + artifact-integrity + style-isolation tests + inherit/override table

`stats_data_handling_manifest.json` follows `spi-math-...-manifest/1`: `generatorId`, `generatorVersion`, `validatorVersion`, `gitCommit`, `generatedAt`, the `pngExport` block (`scale:6`, `6000×4200`, `viewBox "0 0 1000 700"`), the ordered `commands[]` to regenerate, `sha256{}` over each artefact (reviewPackMd, reviewPackJson, visualAudit, goldenFixture, parityFixture, distributionReport, hiresSample, browserVerification), `sha256SvgDir`, `svgCount`, and `rasterExports{premium,accessible,print}` (each width/height/sha256).

**Inherited-check inherit / override / replace table.** Because the family reuses the coordinate-lines validator battery, the pack pins exactly how each inherited check transfers, so no inherited check silently breaks on statistics figures:

| Inherited check | Disposition | Why |
| --- | --- | --- |
| `svg-realises-data` | **inherit verbatim** | canonical figure rebuilt from `params` byte-for-byte. |
| `closure-agreement` | **inherit verbatim** (second-route recompute per statistic) | reduced-Rational equality; mode `set` (deferred) and mean/median `exact-rational` would compare each element reduced first. |
| `tick-labels-integer` | **inherit verbatim** | count-axis labels are `cx-ticklbl` integers; category strings live under `cx-cat`. |
| `equal-axis-scale` | **inherit verbatim** (line graph only) | reused viewport. |
| `media-to-scale` | **override** | applied to bar/line only; pictograms use `pictogram-key-exact` with `toScale:false`. |
| `no-answer-label-in-svg` | **replace** | replaced by `no-statistic-in-svg` (string-equality, not the `,`/`/`/`=` blocklist) so keys/labels render. |
| `no-colour-only-information` | **inherit, with extended `GREYS`** | canonical greys committed in §13.4; pattern+label pairing satisfies the rule. |
| `distractor-rationale-matches` | **inherit verbatim** | each `distractor.rationale === registry.observableError`. |
| `distractors-distinct-misconceptions` | **inherit verbatim** | ids distinct and present in `data-handling.json`. |

Two **blocking** test files reuse the coordinate-lines pattern verbatim:

- `domains/statistics/stats-data-handling-integrity.test.ts` — asserts the audit + pack + manifest all state the **current** `GENERATOR_VERSION` and **no other** version string; the audit `data-git-commit` equals the manifest `gitCommit` (`^[0-9a-f]{7,40}$`); every `manifest.sha256[*]` equals `createHash("sha256")` of the serialized file; and the **embedded exemplar items each pass the precompiled standalone schema validator** (§13.2). Skips cleanly when the manifest is absent.
- `domains/statistics/stats-data-handling-style-isolation.test.ts` — the **computed-style / style-isolation** gate: the **canonical** `media[0].svg` carries the internal unscoped `<style>` and **no** `class="cx-figure"`; `presentationSvg` strips that `<style>` and stamps `class="cx-figure" style="--cx-..."`; the extended `COMMON_CSS` selectors (including the new `.cx-bar/.cx-cat/.cx-icon`) are all scoped under `.cx-figure` and never appear unscoped; `exportSvg(..., 6000, 4200)` is self-contained (concrete colours, no `var(`, no `<link>/@import/url(`) and premium/print bake different ink for the bar/hatch/icon variables; dark-mode series/text are light on the dark bg; theming never mutates the canonical item SVG; and the audit HTML has **exactly one** common `.cx-figure` ruleset with **zero** active unscoped global `cx-*` overrides (the v1.0.1 leak that DECISION_LOG #43 fixed), every gallery figure carrying its own `--cx-...` variables.

---

## 14. Versioning and approval plan

### 14.1 v1.0.0 scope (the proposed tasks only)

`gen.stats.data-handling` v**1.0.0** ships **exactly** the eleven tasks of §13.2 — `read_bar_chart`, `read_pictogram`, `read_table_value`, `complete_frequency_table`, `read_line_graph`, `mean_from_list`, `median_from_list`, `mode_from_list`, `range_from_list`, `mean_from_freq_table`, `single_event_probability` — **1:1** with the eleven authored objectives of cluster A, over the single new strand **`data-handling-and-probability`** (the strand string is pinned exactly once, here and in §15.2 and the cluster-A classification table and curriculum-schema test, so a typo cannot silently fork the strand; probability is in scope, hence this spelling) in domain `statistics`, SPI-Math Middle School.

**Deferred to a later version and deterministically excluded:** pie chart, scatter/correlation, histogram, stem-and-leaf; standard deviation / variance / regression / interpolated quartiles (all require irrationals or non-exact arithmetic, barred by the exact-rational rule); and the `set`-valued multimodal / no-mode mode encoding (deferred with a taught multimodal sub-objective). Deferral is enforced by `paramsInDomain` rejection + absence from the registry task list + an integration test asserting these task ids `generate`-throw and never appear in a 10k sweep. No deferred chart type appears in any dispatch table, so the `chart-realises-data` check carries no pie-sector or scatter-point branch.

### 14.2 Oracle-first build order

1. Author `curriculum/objectives/SPI.MIDDLE.STAT.*.json` (the **eleven** objectives, with `vocabulary[]`, `notation[]`, and `commonMisconceptions[]` referencing the cluster-D `MISC.STAT.*` ids) against `schemas/curriculum-objective.schema.json` at `reviewStatus: "proposed"`. `core/curriculum/graph-check.ts` enforces **no-duplicate-IDs and no-prerequisite-cycle as ERRORS (the DAG)** and emits **unresolved prerequisites as non-blocking WARNINGS only**; it does **not** inspect `crossDomainRelationships`. The family's promise is therefore "adds **zero new unresolved-prerequisite warnings**" (every prerequisite targets an authored ID), **not** a red/green cross-domain resolution gate. A **new bespoke** `domains/statistics/stats-data-handling-graph.test.ts` (modelled on `coordinate-lines-graph.test.ts`) asserts the eleven STAT objectives are present, their prerequisites resolve, that **every `crossDomainRelationships`/`prerequisites` target is an authored `objectiveId`** (the per-objective-explicit-ID convention is enforced here, since the shared tool does not), and the **current** expected `reviewStatus` (`proposed` now, `approved-for-implementation` on owner APPROVE-WITH-REVISIONS, `approved` at final approval) — not a hardcoded `approved`.
2. Write the **Python oracle** (`oracle/spi_oracle/stats_*`) first: the single seeded dataset model, exact `fractions.Fraction` solvers, the canonical monochrome SVG (carrying the unscoped `<style>`, **no** `class="cx-figure"`), and the `MISC.STAT.*` registry. Generate golden + parity fixtures from the oracle. **No Python theme mirror is written** — the render-mode/presentation/export layer is TypeScript-only.
3. Mirror in **TypeScript** (`domains/statistics/stats-data-handling.ts`) using `core/exact-math/rational.ts`, `core/seeded-random/mulberry32.ts`, `core/difficulty/band.ts`, the Cartesian renderer primitives, and `cartesian-theme.ts` (extended per §13.4). Add `checkUnorderedSet` (→ `set`, deferred multimodal use) and `checkTableCompletion` (→ `table-completion`) to `core/answer-checking`, reusing the exact-rational checker shape; **no `list` checker** and **no answer.type schema edit**.
4. `validate(item) → {status, validatorVersion, checks[]}` recomputes every figure and answer (second route) and runs the §13.3 named checks plus the §13.6 inherited/overridden battery.

### 14.3 Gates (all blocking before any approval)

| Gate | Spec |
| --- | --- |
| Golden | 4 seeds, frozen `oracle/golden/stats_data_handling.golden.json`, Py-authored, TS-verified byte-identical (canonical item JSON + canonical SVG). |
| Parity | 150 seeds × 2 interactions, `stats_data_handling.parity.json`; independent Python + TypeScript output **byte-identical** (item JSON + canonical SVG). Theme/export copies are TS-only and excluded from parity. |
| Sweep | `SPI_SWEEP = 10000` seeds: `invalid: 0`, every **declared** band reachable (§13.5 reachability proof), ≥3 distinct in-range misconception distractors per MC under exact-Rational comparison (else deterministic redraw), reproducibility (re-running a seed reproduces byte-for-byte). |
| Distribution | `stats_data_handling_distribution.json` emitted and integrity-checked (§13.5). |
| a11y | axe gate over rendered items: 0 critical / 0 serious, WCAG AA; `dataTableFallback` + non-colour indicators present. |
| Exports | worksheet / answer-key / solutions + offline KaTeX render; bank-json round-trip is lossless. |
| Integrity + style-isolation + graph | the two blocking tests of §13.6 and the bespoke graph test of §14.2 pass. |

### 14.4 Approval lifecycle and immutability

The family registers in `core/sdk/sequence-registry.ts` with an **explicit** `approvalStatus: "pending-review"` field. This must be **present, not omitted**: `approvalStatusOf` in `core/sdk/generator-module.ts` **defaults to `"approved"`** when the field is absent, so an omitted field would silently leak an unreviewed family into normal Studio and production. With the field present, `generatorsForMode` exposes the family **only in review mode** and `approvedGenerators()` excludes it — gated from normal Studio and from production exports/samples until the owner decides on the review pack. An integrity test asserts the STAT entry carries `approvalStatus: "pending-review"` until owner approval.

Newly generated items begin at `lifecycle.state = "generated"` → `machine-validated`; the registry approval does **not** auto-approve future items. On owner approval the entry flips to `approvalStatus: "approved"` with a DECISION_LOG reference (date + decision number), the eleven objective files move to `reviewStatus: "approved"`, and the **golden + parity fixtures become immutable** — any future change ships as a new version (v1.0.1+), preserving the approved version in history (tags), unregistered and unselectable, exactly as v1.0.0/v1.0.1 of coordinate-lines are preserved. Rejection routes to a revised version; the rejected version is never registered. The 10,000-seed stability run is the standing regression guard across versions.

---

## 15. New reusable vs family-specific infrastructure

The family is built to **maximise reuse** of the newly-approved infrastructure and to add only the genuinely statistics-specific pieces. Nothing in the shared column is reinvented.

### 15.1 Shared (reused as-is, by name)

| Shared asset | Source | Reuse in this family |
| --- | --- | --- |
| Cartesian renderer discipline (equal-scale viewport, single `gridRound` projection, `cx-` classes, clipping, the inherited `7680×4320` export envelope → S=6 → 6000×4200) | `gen.geometry.coordinate-lines` primitives | Axes, gridlines, integer ticks, plotted points/segments for the **line graph**; the bar/pictogram baseline + category axis reuse the same viewport + integer projection; the export sizing is reused verbatim, not recomputed. |
| Render-mode theme contract (per-root CSS vars, one common ruleset, premium/dark/accessible/print, `presentationSvg`/`exportSvg`, materialised 6000×4200 export) | `core/visual-style/cartesian-theme.{json,ts}` | Every figure and the visual audit. **TypeScript-only** (no Python mirror); byte-parity Py/TS is required of the canonical SVG + params/answer/distractors, **not** of the themed/exported copies. New series variables (`--cx-bar-fill`/`--cx-bar-hatch`/`--cx-icon`) follow the same per-root pattern (concrete diff in §13.4). |
| Exact arithmetic | `core/exact-math/rational.ts` + Python `fractions.Fraction` | All means/medians/probabilities as exact `{num,den}`; all distractor-vs-key and distinctness comparisons are reduced-Rational equality. |
| Seeded RNG (byte-identical Py/TS) | `core/seeded-random/mulberry32.ts` + `oracle/spi_oracle/seeded_random.py` | Deterministic dataset draw + deterministic MC redraw (median `AVERAGES_ENDS` drop, probability in-range/endpoint redraw). |
| Difficulty banding | `core/difficulty/band.ts` (`bandFromScore`, `round3`) | Weighted-axes score → band, using only the five closed-enum axes the generator emits. |
| Answer-checking | `core/answer-checking` (exact-rational + the checker shape) | Reused for numeric/probability answers; new `checkUnorderedSet` (→ `set`) / `checkTableCompletion` (→ `table-completion`) added in the same module, both targeting **existing** answer.type enum members (no schema edit). |
| Curriculum graph tool | `core/curriculum/graph-check.ts` | Used for its actual guarantee — duplicate-ID + prerequisite-cycle ERRORS, unresolved-prerequisite WARNINGS — **not** for cross-domain validation (which it does not perform; that is the bespoke family graph test). |
| Manifest + artifact-integrity + style-isolation tooling | `oracle/make_*_manifest.py`, `*-integrity.test.ts`, `*-style-isolation.test.ts` patterns | §13.6 tests are direct adaptations. |
| Delivery harness | review-pack/audit generators, exporters, bank-json round-trip, axe gate, SDK registry + approval flow (with **explicit** `approvalStatus`) | Driven family-specifically but mechanism unchanged. |

### 15.2 Family-specific (new, statistics-only)

| New asset | What it is |
| --- | --- |
| Seeded dataset model | The single source of truth per item, with **one canonical field vocabulary** pinned in cluster A/§4.2 and referenced identically everywhere: discriminator `kind: "frequency" \| "list"` (line-graph/time-series = a `list` plus `seriesLabels`; frequency-table = a `frequency` dataset); fields `categories[]`, `frequencies[]` (int), `values[]` (int), pictogram `glyphValue` (int), and probability `outcomeSpace{favourable,total}` drawn from the same category frequencies (`total = Σf`); from this the chart, prompt, answer, solution, and `dataTableFallback` are all derived. |
| Statistics solvers | Exact `mean = (Σ f·x)/(Σ f)`, `median` (sorted; even-n → average of two middles, tagged `integer` when `den=1`, `exact-rational` when `den=2`), `mode` (single value of max frequency, `uniqueModeWhenAsked` gate; multimodal/no-mode deferred), `range = max − min`, weighted mean from a frequency table, `P(event) = favourable/total` reduced — all returning `Rational`/`Fraction`. |
| `MISC.STAT.*` registry | `core/misconceptions/data-handling.json`, the cluster-D ids under the single namespace `MISC.STAT.<TASK_GROUP>.<SHORT_NAME>`, each entry carrying the schema-required `{misconceptionId, domain, description, observableError, reviewStatus:"draft"}` (plus optional `title`), with the value-adapter intent in `distractorRule.summary` (and optional `typicalIncorrectMethod`), reserving `distractorRule.expression` for the optional internal symbolic form; `domain: "statistics"` to mirror the curriculum domain; `observableError`/`feedback` free of internal symbols; + task→[ids] eligibility; byte-parity Py/TS. |
| Per-chart canonical figures | Hand-rolled bar chart, pictogram (integer-key glyph repetition with exact partial-glyph clip), frequency table, and line-graph builders — integer coordinates via `gridRound`, no runtime trig, byte-identical Py↔TS, `role=img` + `<title>/<desc>` + `dataTableFallback`, greyscale-safe with **id-free inline-stroke hatching** (no `<pattern>`/`url(#)`), category strings under `cx-cat` and integer ticks under `cx-ticklbl`. |
| Per-chart validator checks | The statistics-only checks of §13.3 — `chart-realises-data` (bar tops / pictogram glyph counts / line-graph lattice points only), `no-statistic-in-svg` (string-equality, replacing `no-answer-label-in-svg`), `frequency-table-blank-cell`, `pictogram-key-exact`, `category-label-correctness`, `bar-pattern-distinct` — plus the overridden `media-to-scale` (bar/line only) and `closure-agreement` recomputing the asked statistic by a second route. |
| Curriculum objectives + strand | The eleven `SPI.MIDDLE.STAT.*` objective files (with `vocabulary[]`, `notation[]`, `commonMisconceptions[]`) and the `data-handling-and-probability` strand; the explicit `OBJECTIVE_BY_TASK` map. |
| The review pack itself | `oracle/make_review_pack_stats.py` and the family pack/audit/distribution/manifest content of §13, including the per-task band-reachability proof and the fully-populated schema-valid exemplar items. |


---

## Appendix A — Open decisions for the owner

Design choices surfaced during authoring + adversarial review. They do not block the APPROVE/REJECT of the proposal as a whole; engineering adopts the owner's answers (or the stated defaults) at build time. No implementation begins until the proposal is approved.

1. Adding the .cx-bar / .cx-cat / .cx-icon rules and any new per-mode variables to the approved core/visual-style/cartesian-theme.{json,ts} is a change to an owner-approved, frozen contract (coordinate-lines v1.0.2). Owner sign-off is needed on whether bars/categories/icons may extend the single committed ruleset in place, versus the statistics family carrying its own additive ruleset that still reuses the cx-figure per-root isolation.
2. The frequency table can be realised either as an in-SVG ruled grid (so it round-trips through the same byte-parity + export pipeline as the charts) or as a host-rendered HTML table. The proposal assumes the in-SVG grid for uniformity; owner/curriculum confirmation is needed, since an HTML table would sit outside the SVG parity/export gates.
3. Stem-and-leaf is deferred only because it needs a new text-layout primitive (not new math). If the owner wants it in v1.0.0, it is the lowest-risk deferral to pull forward.
4. Pictogram partial-icon clipping is exact-rational, but the set of allowed unit values (e.g. unit in {2,5,10}) and which fractional icons are permitted (half/quarter) should be pinned by curriculum so the clipped-icon geometry stays legible and the redraw loop has a guaranteed-acceptable draw.


## Appendix B — Cross-section consistency notes (for human double-check)

1. Domain naming is left as an explicit owner decision: the front matter proposes domain `statistics` with `data-handling` as the named alternative, since the schema treats `domain` as a free-form string and there is no existing statistics/data objective file to follow. Section 1 must record the final choice and use it verbatim across all objective IDs and the registry.
2. Objective ID segment uses `STAT` for the domain segment (e.g. `SPI.MIDDLE.STAT.MEAN.01`). If the owner selects domain `data-handling` instead of `statistics`, confirm whether the ID segment should remain `STAT` or change to a `DATA`-style segment; the front-matter pattern `SPI.MIDDLE.STAT.<TOPIC>[.<MICRO>].NN` assumes `STAT`.
3. The proposed new strand value `data-handling-and-probability` is a free-form string and needs no enum change, but — mirroring the coordinate-lines precedent — a curriculum-schema test should assert the new strand (and new domain) value is accepted; flag in Section 1 / the validator section.
4. `mode` answers may legitimately be multimodal: the front matter allows `set` as an answer type for mode so a multimodal dataset returns a set of values. Section 4 must fix whether v1.0.0 datasets are constrained to a unique mode (answer type `integer`) or permit multimodal results (answer type `set`), since this changes the answer-type roster and the checker set.
5. Pictogram `read-value` requires a fixed integer key (one symbol = k units) for the value to be exact; half-symbols are only admissible when k is even. Section 3/5 must constrain the key so every readable value is an exact integer, otherwise pictogram readings risk non-integer values and must redraw.
6. Probability is single-event and stated as an exact fraction (answer type `fraction`); Section 2/4 should confirm whether the canonical form is the reduced fraction only, or whether an equivalent-forms checker also accepts unreduced equivalents (consistent with the exact-rational equivalence discipline).
7. Pie chart is listed DEFERRED in this front matter even though it could be exact when all sector angles are integer degrees; this is a scope decision (kept out of v1.0.0) rather than an exactness exclusion. Section 9 must state the deterministic-exclusion mechanism for pie charts distinctly from the exactness-based exclusions (std dev, regression, interpolated quartiles).
8. Frequency-table tasks span both `table-completion` (complete the table) and statistics computed from a table (mean/median/mode/range from a frequency table). Section 4 must keep the `table-completion` checker (cell-wise) distinct from the numeric statistic checkers so a single objective is not conflated across two answer types.
9. The reused `exportSvg` default is 6000 × 4200 (S = 6) per `cartesian-theme.ts`; multi-series statistics figures must be confirmed to fit this canvas at full series count without legend overflow — Section 6 should carry the named visual-quality / overload check inherited from the coordinate-lines premium contract.
10. Line-graph and bar-chart frequency axes need an INDEPENDENT y-scale (frequency), not the equal-unit-scale x=y viewport that coordinate-lines uses for geometry. Section 5/6 must state explicitly that this family selects the renderer's independent-scale viewport mode (still a single `gridRound` projection, still byte-identical) so reviewers do not assume equal-scale axes.

## Appendix C — Authoring & verification provenance

Authored by a multi-agent workflow: 15 sections drafted in parallel against a fixed platform-conventions digest, reviewed by four adversarial critics (statistics correctness, platform-fit, renderer/visual reuse, completeness), then revised against the consolidated findings and synthesized. The critics raised 44 findings (9 blocker-severity, 22 missing items), applied in the revision pass. Residual items are the open decisions (Appendix A) and the consistency notes (Appendix B). PROPOSAL ONLY — no implementation, code, fixtures, or registry entry exists until the owner approves.
