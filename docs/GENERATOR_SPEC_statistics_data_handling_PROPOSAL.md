# Generator Specification — `gen.stats.data-handling` v1.0.0 (Statistics and Data Handling)

> **STATUS: APPROVED WITH REQUIRED REVISIONS (owner, 2026-06-24) — revised; implementation proceeding oracle-first. Objective status: approved-for-implementation; generator registry: pending-review (gated) until the implemented review-pack decision.**
> This document records — and applies the owner's APPROVE-WITH-REQUIRED-REVISIONS directive on — the **objectives, task scope, data model, chart-type roster, answer/equivalence checkers, misconception registry, difficulty model, validation contract, accessibility model, review-pack plan, versioning, and reusable-vs-family infrastructure** for the first SPI-Math Statistics and Data Handling generator family. The eleven objectives are **approved-for-implementation** (curriculum-approved and cleared for the generator build) and the generator family is **registered `approvalStatus: pending-review`** — gated out of normal Generator Studio use and out of production exports/samples until the implemented review-pack decision; the initial item lifecycle is the machine-validated `lifecycle.state = generated`. Implementation proceeds **oracle-first** (the independent Python `spi_oracle` is authored and frozen before the TypeScript mirror). **Every existing platform gate is retained without exception:** deterministic seeded generation (byte-identical Mulberry32 / Python PRNG streams; deterministic redraw); exact `Rational` / integer arithmetic with **no floats and no irrationals in any answer**; independent Python + TypeScript verification with closure-agreement; canonical item + SVG byte-for-byte parity for chart media AND deterministic HTML-table parity for tables; runtime Ajv schema validation at boundaries; misconception-backed distractors (≥ 3 distinct, rule-recomputed, else deterministic redraw); golden (4-seed) + parity (150 × 2) + 10,000-seed (`SPI_SWEEP`) stability sweeps with reproducibility re-check and a distribution report; style-isolation testing; accessibility (axe-core 0 critical/serious, WCAG AA) with a data-table fallback for every figure; offline HTML/JSON exports (worksheet / answer-key / solutions, offline KaTeX) with bank-json round-trip; immutable approved-generator fixtures; a generation manifest with blocking artifact-integrity tests + SHA-256. The approved arithmetic / geometric / linear / angle-geometry / `gen.geometry.coordinate-lines` generators keep their output **byte-for-byte unchanged.** **This family reuses the approved `gen.geometry.coordinate-lines` v1.0.2 visual contract through a versioned ADDITIVE shared extension — it does NOT alter the coordinate-lines visual contract in place, and does NOT invent a parallel renderer, style layer, or export path.** Statistical charts (bar charts, line graphs) reuse the `cx-figure` per-root CSS-custom-property style-isolation contract (modes premium / premium-dark / accessible / print), the common axis/grid variables, `presentationSvg()` / `exportSvg()`, and the materialised 6000 × 4200 (S = 6) high-resolution export, with statistics primitives (chart bars, category labels, pictogram symbols, bar hatches, legends, data-point labels) ADDED in the new extension. Statistical graphs are NOT held to the coordinate-geometry equal x/y pixel scale: each axis is internally linear and uniformly scaled, but x and y use independent scales (different quantities). **Every deferred chart type and every deferred statistic is DETERMINISTICALLY EXCLUDED — never silently included** (see §8, §11): no pie charts, scatter/correlation, regression/lines of best fit, histograms, stem-and-leaf, box plots, quartiles/IQR, standard deviation/variance, grouped-data estimated means, or multimodal/no-mode/set-valued mode responses; deferred chart types are unreachable from the seeded task loop, not merely undrawn.

## Overview

`gen.stats.data-handling` is **the next architecture-proving family after `gen.geometry.coordinate-lines`** because it is the first family whose figures are intrinsically **multi-series, data-bearing displays** rather than single geometric constructions: a bar chart or line graph carries several categories or ordered observations at once, where the **same seeded dataset must simultaneously realise the chart, the prompt, the canonical answer, the worked solution, and the accessibility data-table** — proving that one deterministic source of truth can drive a far richer figure under every existing gate. It is also the first family to **consume the approved premium colour / style-isolation / export layer as a reuser rather than its author**: `coordinate-lines` v1.0.2 introduced the per-root `cx-figure` isolation + materialised 6000 × 4200 export contract; Statistics reuses that contract through a **versioned ADDITIVE shared extension** (see §7/§15) — it does NOT alter the coordinate-lines visual contract in place — depending on it for genuinely multi-series presentation (categories and series that must remain distinguishable by **pattern / label / marker, never colour alone**, and must survive the CVD-safe `accessible` and monochrome-authoritative `print` modes). Sequencing Statistics here is deliberate: it stresses the reusable Cartesian substrate (axes, gridlines, plotted points, **independent y-scaling for frequency data**) and the approved export/style isolation on **new figure shapes** while every statistic stays **exact** (mean / median / mode / range / single-event probability as exact `Rational` / integer / fraction), so the architecture is proven before any approximate or inferential statistics are ever attempted. **Statistical graphs are not held to the coordinate-geometry equal x/y pixel scale:** each axis is internally linear and uniformly scaled, but x and y measure different quantities and use **independent** scales (§6.7, §J).

The v1.0.0 scope is the small, fully-exact core of middle-school data handling: **read a value from a bar chart / pictogram / table; complete a frequency table; compute mean / median / mode / range from a small integer data list and from a frequency table; read a value from a line graph; and state a simple single-event probability as an exact fraction** — each backed by a 1:1 micro-objective under the new `statistics` domain and the new `data-handling-and-probability` strand, each answered with an **existing** `answer.type` enum value (`integer`, `exact-rational`, `fraction`, `table-completion`) under an existing `interactionType` (free-response or, where ≥ 3 misconception-backed distractors exist, `multiple-choice`). The `set` / multimodal mode encoding is **deferred** (a unique mode is required, so the v1.0.0 mode answer is a single `integer`, never a set). **No schema change is required:** every answer type and interaction this family needs is already in `question-item.schema.json`, and `domain` / `strand` are free-form strings in `curriculum-objective.schema.json`. Sections 1–15 below develop each decision; this front matter fixes the identifiers, the reuse posture, and the approval gate.

## Identifier glossary

| Item | Value (use verbatim) |
| --- | --- |
| Domain | `statistics` |
| Strand | `data-handling-and-probability` |
| Generator id | `gen.stats.data-handling` |
| Generator version | `1.0.0` |
| Validator version | `1.0.0` |
| Stage | `middle-school` |
| Objective ID pattern | `SPI.MIDDLE.STAT.<TOPIC>.<MICRO>.01` (matches `^SPI\.[A-Z0-9]+(\.[A-Z0-9_]+)+\.[0-9]{2}$`) |
| Misconception ID prefix | `MISC.STAT.*` (registry-backed; ≥ 3 distinct per MC-eligible task or deterministic redraw) |
| Answer types used (all already in enum) | `integer`, `exact-rational`, `fraction`, `table-completion` |
| Interaction types used (already in enum) | `free-response`; `multiple-choice` only where ≥ 3 misconception-backed distractors exist |
| Reused substrate | `gen.geometry.coordinate-lines` v1.0.2 Cartesian primitives (`cx-*`, single `gridRound` projection, integer coords, no runtime trig, byte-identical Py ↔ TS) — reused through a versioned ADDITIVE extension, NOT altered in place |
| Reused style / export | the approved coordinate-lines v1.0.2 visual contract via the additive `core/visual-style/data-chart-theme/` + `core/render/data-charts/` extension — reuses per-root `cx-figure` isolation, common axis/grid variables, modes `premium` / `premium-dark` / `accessible` / `print`, `presentationSvg()` / `exportSvg(…, 6000, 4200)` materialised export; ADDS statistics primitives (bars, category labels, pictogram symbols, hatches, legends, data-point labels) |
| Reused checkers | `core/answer-checking` exact-rational + the existing checker shape (extended with a `table-completion` checker, byte-parity Py/TS) |
| Initial registry status | `approvalStatus: pending-review` (gated from normal Studio + production until the implemented review-pack decision) |
| Initial item lifecycle | `lifecycle.state = generated` (machine-validated) |
| Provenance | `origin: generated`, `rightsStatus: academy-owned` |

**v1.0.0 chart types (IN) vs DEFERRED (deterministically excluded)**

| Status | Chart / statistic | Note |
| --- | --- | --- |
| IN v1.0.0 | vertical bar chart, pictogram, frequency table, line graph (reading), single-event probability | exact integer frequencies / small integer data list; reuses Cartesian axes + **independent** y-scale; bar charts are VERTICAL only in v1.0.0 |
| IN v1.0.0 | mean / median / mode (unique only) / range (from list and from frequency table) | all exact `Rational` / integer / fraction; **mode is a single `integer` (unique mode required) — never a `set`** |
| DEFERRED | pie chart | exact only if every sector angle is an integer degree; deferred from v1.0.0, candidate for a later version under that constraint |
| DEFERRED | scatter plot / correlation, regression / lines of best fit | qualitative correlation reading and least-squares regression are out of v1.0.0 scope; regression is irrational in general |
| DEFERRED | histogram, stem-and-leaf, box plot | grouped-data / display conventions out of v1.0.0 scope; stem-and-leaf stays deferred |
| DEFERRED | standard deviation, variance, quartiles / IQR, grouped-data estimated means | excluded by the **exact-only** rule (surds / irrationals / floats / non-half fractional positions forbidden in answers) |
| DEFERRED | multimodal / no-mode responses, set-valued mode answers | v1.0.0 requires a unique mode and emits a single `integer`; the `set` encoding is deferred |

> Each DEFERRED row is **unreachable from the seeded task loop**, not merely undrawn (§8 validator, §10/§11 edge cases): the task enum, the chart-type selector, and the parameter loop have no path that produces a deferred chart or a non-exact statistic; a request for one is rejected, never silently downgraded.

## Table of contents

1. Curriculum placement and objective IDs
2. Objective wording and prerequisites
3. Task-to-objective mapping
4. Data model and parameter model — the single seeded dataset
5. Answer representation and equivalence checkers (set / list / table-completion / exact-rational)
6. Chart types and the SVG renderer contract
7. Reuse of the approved Cartesian substrate via an additive `data-chart-theme` extension (style isolation + 6000 × 4200 export; coordinate-lines unchanged)
8. Misconception registry (`MISC.STAT.*`, approved in principle)
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

**Identifier structure (owner-pinned).** Every objective ID has the form `SPI.MIDDLE.STAT.<TOPIC>.<MICRO>.01`, decomposed as: `SPI` (academy) · **`MIDDLE` (stage segment — verified: every existing middle-school objectiveId uses `MIDDLE`, never `MS`)** · **`STAT` = the domain segment** · **`<TOPIC>` = the topic segment** (`READ` = reading displays, `FREQ` = frequency tables, `AVG` = averages and spread, `PROB` = single-event probability) · **`<MICRO>` = the micro-skill segment** · `01` (the two-digit ordinal). Every ID matches the schema pattern `^SPI\.[A-Z0-9]+(\.[A-Z0-9_]+)+\.[0-9]{2}$` and the precedent depth of `SPI.MIDDLE.ALG.LINEQ.ONESTEP_MUL.01` / `SPI.MIDDLE.GEO.COORD.GRADIENT_TWO_POINTS.01`, so the five-segment depth is unambiguous to reviewers. `STAT` is the new domain segment, deliberately distinct from `NUM` / `ALG` / `GEO`.

**The eleven canonical objective IDs (owner-pinned; used EXACTLY, no alternative spellings anywhere):**

```
SPI.MIDDLE.STAT.READ.BAR_CHART.01
SPI.MIDDLE.STAT.READ.PICTOGRAM.01
SPI.MIDDLE.STAT.READ.TABLE_VALUE.01
SPI.MIDDLE.STAT.READ.LINE_GRAPH.01
SPI.MIDDLE.STAT.FREQ.COMPLETE_TABLE.01
SPI.MIDDLE.STAT.AVG.MEAN_LIST.01
SPI.MIDDLE.STAT.AVG.MEDIAN_LIST.01
SPI.MIDDLE.STAT.AVG.MODE_LIST.01
SPI.MIDDLE.STAT.AVG.RANGE_LIST.01
SPI.MIDDLE.STAT.AVG.MEAN_FREQ_TABLE.01
SPI.MIDDLE.STAT.PROB.SINGLE_EVENT.01
```

**A single `OBJECTIVE_BY_TASK` constant is the single source of truth for the task↔objective bijection.** One authored `OBJECTIVE_BY_TASK[task]` constant (modelled exactly on coordinate-lines' constant) maps each of the eleven tasks to exactly one of these eleven IDs. A blocking test asserts that **every** section/objective file/descriptor/validator/fixture/review-pack/registry entry uses exactly these eleven IDs — no conflicting form (`READ.BAR.01`, `READ.BAR_VALUE.01`, `READ.PICTOGRAM_VALUE.01`, `READ.TABLE.01`, `READ.LINE.01`, `FREQ.COMPLETE.01`, `FREQ.MEAN_TABLE.01`, `AVG.MEAN_FREQ.01`, or any `SPI.MS.STATISTICS.*` stage/domain drift) appears anywhere. The objective-mapping validator compares exact strings, so any drift would fail. **Objective status during the build is `approved-for-implementation`** (curriculum-approved and cleared for the generator build); the objectives become **fully `approved`** only after the implemented review-pack decision.

**New domain and strand (owner-pinned, single spelling).** This family introduces the new curriculum **domain `statistics`** and, within it, the new **strand `data-handling-and-probability`** (one spelling, used identically here and in every other section — there is no `data-handling-and-summary-statistics` variant; single-event probability O11 is in scope, so the strand name names it). A **curriculum-schema test pins the exact strings `domain: "statistics"` and `strand: "data-handling-and-probability"`** — both `domain` and `strand` are free-string fields in `schemas/curriculum-objective.schema.json` today, so no enum edit is required; the test pins the exact spellings so a typo cannot silently fork the strand. The objectives are authored as new `curriculum/objectives/SPI.MIDDLE.STAT.json` entries (one JSON array), validated by `schemas/curriculum-objective.schema.json`.

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
| `reviewStatus` | `approved-for-implementation` (curriculum-approved and cleared for the generator build; lifecycle below) |
| `version` | `1.0.0` |
| `crossDomainRelationships` | explicit approved objective IDs (per-objective, Section 2) — e.g. `SPI.MIDDLE.NUM.SIGNED_OPERATIONS.01`; never a `SPI.MIDDLE.NUM.*` wildcard. **This is an authoring convention enforced by the new family graph test (below), NOT by the shared `graph-check.ts`, which never inspects `crossDomainRelationships`.** |

**Objective lifecycle (owner directive applied).** On the owner's APPROVE-WITH-REQUIRED-REVISIONS directive (2026-06-24) the eleven objectives are at **`reviewStatus: "approved-for-implementation"`** — curriculum-approved and cleared for the generator build while the generator family itself remains `pending-review` (the schema documents `approved-for-implementation` as "curriculum-approved and cleared for generator build while the generator itself remains pending-review"). At the final implemented review-pack decision they become `approved`. **The new bespoke family graph test asserts the CURRENT expected `reviewStatus` (`approved-for-implementation` now, `approved` at final approval)**, so it does not inherit the coordinate-lines graph test's `reviewStatus === 'approved'` assertion verbatim and stays green at every stage.

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

All eleven enter the curriculum graph at `reviewStatus: approved-for-implementation`. **No existing objective is modified.** The approved `SPI.MIDDLE.NUM.*`, `SPI.MIDDLE.ALG.*` and `SPI.MIDDLE.GEO.COORD.*` objectives are referenced only as prerequisites / cross-domain links (incoming edges added in *this* family's arrays); their own files are untouched.

> **Reference-integrity note (verified against `curriculum/objectives/*`).**
> - **Authored & approved (safe prerequisite targets, all verified present as `objectiveId` entries):** `SPI.MIDDLE.NUM.SIGNED_OPERATIONS.01`; `SPI.MIDDLE.ALG.INVERSE_OPERATIONS.01`; `SPI.MIDDLE.ALG.EXPAND_BRACKETS.01`; the eight `SPI.MIDDLE.GEO.COORD.*` objectives (`CARTESIAN_PLANE`, `READ_POINT`, `PLOT_POINT`, `GRADIENT_TWO_POINTS`, `MIDPOINT`, `INTERPRET_MX_C`, `EQUATION_FROM_GRAPH`, `EQUATION_FROM_2PTS`); the five `SPI.MIDDLE.ALG.LINEQ.*` objectives; the five `SPI.MIDDLE.GEO.*` angle objectives.
> - **Referenced-but-undefined (dangling) nodes that this family deliberately AVOIDS (verified: referenced in other files' arrays but having no authored `objectiveId`):** `SPI.MIDDLE.NUM.INTEGERS_NUMBER_LINE.01`, `SPI.MIDDLE.ALG.SUBSTITUTION.01`, **`SPI.MIDDLE.ALG.NOTATION_SUBSTITUTION.01`** (referenced as a prerequisite in `SPI.MIDDLE.ALG.FOUNDATIONS.json` yet not authored), `SPI.MIDDLE.GEO.TRIANGLE_CLASSIFY.01`, `SPI.MIDDLE.GEO.ANGLE_MEASURE_NOTATION.01`, and `SPI.MIDDLE.NUM.ORDER_OF_OPERATIONS.01` (the last appears only in `relatedObjectives`, not as a prerequisite, but is likewise unauthored). This family routes **every** prerequisite/cross-domain edge to an authored, approved ID (or to an earlier objective in this same family). It therefore adds **zero new** unresolved-prerequisite warnings.

> **Gate accuracy (corrected — verified against `core/curriculum/graph-check.ts`).** `graph-check.ts` enforces, as **ERRORS** that fail `report.ok`: (a) **no duplicate objectiveIds** and (b) **no prerequisite cycle** (DFS over resolved prerequisite edges only). It treats an **unresolved prerequisite as a non-blocking WARNING** (`report.ok` stays `true` even with a dangling prereq), and it **inspects `prerequisites` only — never `crossDomainRelationships` or `relatedObjectives`.** This family's promise is therefore "adds zero new unresolved-prerequisite **WARNINGS**", not a red/green resolution gate. The cross-domain / authored-target guarantees are enforced by a **new bespoke `stats-data-handling-graph.test.ts`** (modelled on `coordinate-lines-graph.test.ts`) that asserts: the eleven STAT objectives are present; every `prerequisites` AND every `crossDomainRelationships` target resolves to an authored `objectiveId` (this is the part the shared tool does not do); the subgraph is acyclic; and each objective carries the stage-appropriate `reviewStatus`.

---

## 2. Objective wording and prerequisites

Each block below uses `curriculum-objective.schema.json` field names. Shared fields from Section 1 (`academy`, `programme`, `stage`, `course`, `domain: statistics`, `strand: data-handling-and-probability`, `unit`, `calculatorPolicy: calculator-not-required`, `reviewStatus: approved-for-implementation`, `version: 1.0.0`) are not repeated. `answerTypes` entries are drawn from the platform `answer.type` enum (`question-item.schema.json#/$defs/answerType`) and are **MATHEMATICAL answer types only** — `multiple-choice` is an interaction-support mechanism and is **never** listed in `answerTypes`. `allowedRepresentations` entries are drawn from the objective-schema enum (`symbolic`, `numeric`, `graphical`, `tabular`, `diagram`, `verbal-context`, …). Every objective now also populates `vocabulary`, `notation`, and `commonMisconceptions` (the registry IDs from Cluster B's `core/misconceptions/data-handling.json`, prefix `MISC.STAT.<GROUP>.<NAME>`, the single registry namespace — there is no `MISC.STATS.*` variant), matching the coordinate-lines / sequences precedent where each objective lists its 2–3 associated misconceptions.

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
- `answerTypes`: [`table-completion`]
- `commonMisconceptions`: [`MISC.STAT.FREQ.WRONG_DIRECTION`, `MISC.STAT.FREQ.OMITS_CATEGORY`, `MISC.STAT.FREQ.COPIES_TOTAL`]
- `difficultyRange`: {min:1, max:3}
- Note: the canonical answer is a `table-completion` payload (the `{cellId → integer}` fill). **Each item has exactly ONE missing cell — one missing frequency OR one missing total — never an underdetermined multi-blank.** **This task is FREE-RESPONSE ONLY: `answer.type` is `table-completion` and `interactionType` is `free-response`; no multiple-choice variant is offered** (see Section 3). All cells are non-negative integers by construction. The misconceptions above are diagnostic (used in feedback / solution narration), not MC distractors.

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
- Note: even-n median is `(a+b)/2`, exact with `den ∈ {1,2}`; **the stored `answer.type` is set from the computed denominator (integer when den 1, exact-rational when den 2)** so answer-type-consistency passes — the median is never pinned to `exact-rational` unconditionally. **Uniform lists are NOT excluded for median (§H)** — they are admitted at a controlled low frequency (the median of a uniform list is well-defined).

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
- Note: **`range = 0` (a uniform list) is a VALID low-band FREE-RESPONSE case (§H)** — `max > min` is NOT required universally; a uniform list is admitted as a deliberate range-0 teaching case at a controlled low frequency. **MC may remain ineligible for `range = 0`** (3 distinct in-range distractors are impossible), in which case the item falls back to free-response. Negative list values may appear at higher bands; the range is then `max − min` over signed integers.

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
| `complete_frequency_table` | O5 `FREQ.COMPLETE_TABLE.01` | `free-response` **only** | `table-completion` | **No** | **FREE-RESPONSE ONLY.** Each item has exactly ONE missing frequency or one missing total (no underdetermined multi-blank); `answer.type` is `table-completion`. The frequency misconceptions are diagnostic (feedback/solution narration), not MC distractors; no MC variant is offered, and an explicit MC request is rejected as unsupported for this FR-only task. |
| `mean_from_list` | O6 `AVG.MEAN_LIST.01` | `free-response`, `multiple-choice` | `integer` \| `exact-rational` | Yes | (a) `MISC.STAT.MEAN.DIVIDE_BY_N_MINUS_ONE`; (b) `MISC.STAT.MEAN.FORGOT_TO_DIVIDE` (returns Σx); (c) `MISC.STAT.MEAN.EQUALS_MEDIAN` (returns the middle value). MC gated on **mean ≠ median ≠ Σx as exact Rationals AND the dataset non-uniform** (so the median foil cannot equal the key for symmetric/uniform data); collisions redraw. |
| `median_from_list` | O7 `AVG.MEDIAN_LIST.01` | `free-response`, `multiple-choice` | `integer` \| `exact-rational` | Yes | (a) `MISC.STAT.MEDIAN.UNORDERED_MIDDLE` (middle of the unordered list); (b) `MISC.STAT.MEDIAN.AVERAGES_ENDS` ((min+max)/2); (c) `MISC.STAT.MEDIAN.EQUALS_MEAN`. **MC pre-acceptance gate (exact Rationals): median ≠ (min+max)/2 AND median ≠ middleUnordered(list) AND all three distractors mutually distinct and ≠ key**, because (min+max)/2 equals the median for *every* symmetric or evenly-spaced list (e.g. [2,4,6], [1,3,5,7], [3,3,3]) — a frequent collision, not a rare one. When AVERAGES_ENDS collides it is dropped; the row backfills from EQUALS_MEAN / UNORDERED_MIDDLE so three distinct ids remain, else the item is FR. |
| `mode_from_list` | O8 `AVG.MODE_LIST.01` | `free-response`, `multiple-choice` | `integer` | Yes | (a) `MISC.STAT.MODE.RETURNS_FREQUENCY` returns the count of the mode, not the value; (b) `MISC.STAT.MODE.RETURNS_MAXIMUM`; (c) `MISC.STAT.MODE.RETURNS_MEDIAN`. **No "returns the mode" foil exists** (it would equal the key). Unique mode guaranteed (`maxFreq ≥ secondFreq + 1`); single-value `integer` only — the `set`/multimodal path is deferred and never reachable in v1.0.0. |
| `range_from_list` | O9 `AVG.RANGE_LIST.01` | `free-response`, `multiple-choice` | `integer` | Yes (when `max>min`; `range=0` is FR-only) | (a) `MISC.STAT.RANGE.SUMS_ENDS` (max+min); (b) `MISC.STAT.RANGE.RETURNS_MAXIMUM`; (c) `MISC.STAT.RANGE.COUNTS_VALUES` (counts the data instead of subtracting). For a non-uniform list the range is positive and the three foils are distinct; **`range = 0` (a uniform list) is a valid low-band FR case** (§H), MC-ineligible there (3 distinct distractors impossible). |
| `mean_from_freq_table` | O10 `AVG.MEAN_FREQ_TABLE.01` | `free-response`, `multiple-choice` | `integer` \| `exact-rational` | Yes | (a) `MISC.STAT.MEANFT.DIVIDE_BY_ROWS` (÷ number of categories, not Σf); (b) `MISC.STAT.MEANFT.IGNORES_FREQUENCY` (unweighted mean of the x-values); (c) `MISC.STAT.MEANFT.UNWEIGHTED_SUM`. **MC gated on frequencies not-all-equal** (else IGNORES_FREQUENCY equals the weighted mean) and on the three values being distinct as exact Rationals; collisions redraw. |
| `single_event_probability` | O11 `PROB.SINGLE_EVENT.01` | `free-response`, `multiple-choice` (MC only for eligible PROPER probabilities) | `fraction` | Yes, for eligible proper probabilities | (a) `MISC.STAT.PROB.COMPLEMENT` (unfavourable/total = 1−P); (b) `MISC.STAT.PROB.ODDS_AS_FRACTION` = favourable/(total−favourable) — **the single corrected rule, in (0,1) only when favourable < total/2**; (c) `MISC.STAT.PROB.NUM_DENOM_SWAP` (the inverted fraction). **In-range filter: every distractor must lie in [0,1] and differ from P as exact Rationals; an out-of-[0,1] value is NEVER used as a distractor** — if odds or the swap leaves the unit interval, it is redrawn/backfilled. **MC is offered only for eligible PROPER probabilities with 3 strong distinct in-range distractors** (minimum-outcome-space gate); **P=0, P=1, and P=1/2 are FREE-RESPONSE ONLY** and an MC request redraws deterministically away from them. |

**Free-response / non-MC-only summary.** Free-response is the default interaction everywhere and is the only interaction for: **`complete_frequency_table`** (FR-only, `answer.type: table-completion`, exactly one missing frequency or one missing total per item, no underdetermined multi-blank); and the degenerate probability sub-cases of O11 (`P ∈ {0, 1, 1/2}`, FR-only, where the complement/odds/swap distractors collide or leave [0,1]). **An explicit interaction request is never silently changed:** for an explicit MC request the generator redraws deterministically until the draw is MC-eligible; for FR-only tasks (`complete_frequency_table`) an explicit MC request is rejected as unsupported; for the O11 FR-only endpoints an MC request redraws away from the ineligible sub-case. MC is **never** silently downgraded to FR, and FR is never silently upgraded to MC; the requested interaction is always preserved. **There is no `set`-valued task in v1.0.0** (the multi-modal "all modes" encoding is deferred; the mode answer is a single `integer`), so no set-only FR case arises.

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
| `no-answer-label-in-svg` | **REPLACE** with the semantic `no-statistic-in-svg` + §L role-based leakage checks | the inherited check fails any `<text>` containing `,`, `/`, or `=` — but a pictogram key text ("1 symbol represents 5 items") and category/unit labels ("km/h", "Year 7, boys") legitimately contain those characters. The replacement judges leakage by **element role + render intent** (no dedicated answer/statistic annotation, no solution overlay, no correct-option styling in student media), NOT by raw text equality — **raw data, ticks, and labels that coincidentally equal the answer are allowed** (§L). A pinned test asserts a pictogram key line passes, a list containing its own answer passes, and a dedicated answer annotation fails. |
| `media-to-scale` | **Apply to bar/line charts only; REPLACE for pictograms with `pictogram-key-exact`** | the inherited check hard-asserts `media[0].toScale === true`. Bar charts and line graphs keep `toScale: true` — meaning **each axis faithfully represents its own declared (independent) scale** (§J), NOT equal px/unit. Pictograms are symbol-count figures, so they carry `toScale: false` and are gated by `pictogram-key-exact` (every symbol count × key = the integer frequency). |
| `no-colour-only-information` | **Inherit verbatim; NO change to the shared grey set** | the statistics figure confines itself to greys already in the reused contract — see palette note below. |
| `svg-realises-data` | **Inherit, restricted to in-scope charts** | recompute covers bar tops, pictogram glyph counts (+ exact partial-glyph clip width), table cells, and line-graph lattice points only. **No pie-sector or scatter-point recomputation branch exists** (those are structurally absent from every dispatch table). |

**Canonical SVG, greyscale palette, and cartesian-theme diff (the concrete, verified changes).**

- **The canonical `media[0].svg` carries the internal unscoped monochrome `<style>` and NO `class="cx-figure"`** (byte-identical discipline to coordinate-lines, where `figure()` emits `<svg … role="img">` + internal `<style>` and never stamps `cx-figure`). `class="cx-figure"` and the per-root `--cx-*` variables are added **only** by `presentationSvg()` / `exportSvg()` at presentation/export time (which strip the canonical `<style>` and stamp the root). The accessibility-envelope canonical form is this un-themed monochrome SVG.
- **Byte-parity Py/TS applies to the canonical `media[0].svg` and to `params`/`answer`/`distractors` only.** The `presentationSvg`/`exportSvg`/render-mode/6000×4200-export theme layer is a **TypeScript-only presentation concern** (`core/visual-style/cartesian-theme.ts` exists only in TS; there is no `cartesian_theme.py`) and is **NOT mirrored in the Python oracle.** The Python oracle emits the canonical monochrome SVG and the statistic; the browser-verification + style-isolation evidence is generated from the TS theme. No Python theme byte-parity is claimed.
- **Export sizing is reused verbatim, not recomputed:** the inherited `exportEnvelope` constant `maxEnvelope = 7680×4320` gives `S = min(floor(7680/1000), floor(4320/700)) = min(7,6) = 6`, hence **6000×4200** — identical to coordinate-lines.
- **Committed greyscale palette — NO change to the shared grey set.** The reused contract's grey set is `{#111,#333,#444,#555,#888,#bbb,#fff}`. The statistics canonical figure uses **only shades already in that set**: `.cx-bar` fill `#bbb`, the bar hatch stroke `#555`, the category text `.cx-cat` fill `#333`, and `.cx-icon` (pictogram symbol) fill `#444`. Because all four are already members, **`no-colour-only-information` passes with NO change to the shared grey set and NO edit to any coordinate-lines source** — the family deliberately confines itself to the existing greyscale set, defining its statistics-class `STYLE` fragment in the additive `data-charts` extension (§7.2) so coordinate-lines output stays byte-for-byte unchanged.
- **Concrete additive `data-chart-theme` extension diff (coordinate-lines source untouched; §7.2, §K)** (names obey the `resolveCommonCss` regex `var\(--cx-[a-z-]+\)`, i.e. lowercase-and-hyphen only): the **extension** declares variables `--cx-bar-fill`, `--cx-bar-hatch`, `--cx-cat`, `--cx-icon`, each given a value in **all four** mode objects (`print`/`premium`/`premium-dark`/`accessible`) — e.g. print `--cx-bar-fill:#bbbbbb; --cx-bar-hatch:#555555; --cx-cat:#333333; --cx-icon:#444444`, with CVD-safe and dark equivalents; the extension's common-ruleset additions append `.cx-figure .cx-bar{fill:var(--cx-bar-fill);stroke:var(--cx-bar-hatch);stroke-width:1}`, `.cx-figure .cx-cat{font-size:20px;fill:var(--cx-cat)}`, `.cx-figure .cx-icon{fill:var(--cx-icon)}`; the canonical short-hex `STYLE` fragment lives in the **`core/render/data-charts/` extension module** (TS) and its Python mirror, kept byte-identical, so `svg-realises-data` parity holds. **The `cartesian-theme.json` and the coordinate-lines `STYLE`/`GREYS` constants are NOT edited.**
- **Id-free hatch.** The bar hatch is drawn as **inline integer-coordinate `<line>` stroke elements clipped to the bar rectangle, in deterministic element order** — NOT an SVG `<pattern id=…>` + `fill="url(#…)"`, which is forbidden by the inherited no-id / no-`url(#…)` canonical-SVG rule. The `bar-pattern-distinct` check inspects these inline hatch lines, not a pattern id. This keeps coordinates integer-only and the no-id invariant intact.

**Probability dataset source.** For `single_event_probability` the seeded `params` carry a `frequency` dataset plus an explicit `outcomeSpace = {favourable, total, targetCategoryIndex}` drawn so `1 ≤ favourable ≤ total` (with `total` large enough for MC reachability when MC is eligible), and the favourable category is named. The context describes equally-likely atomic outcomes ("One item is selected at random from a bag containing the objects shown."). **The probability item DOES show its bag/category frequency table** (the semantic HTML table or its SVG snapshot) drawn from the same `{favourable, total}` source; the `no-statistic-in-svg` / no-answer-in-table checks guarantee the table never prints the fraction answer. No bar/line Cartesian chart is required for probability.

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
  "difficulty": { "overallBand": 2, "axes": { "numericalComplexity": 0.25, "reasoningSteps": 0.2, "readingDemand": 0.15, "interpretationDemand": 0.1, "informationDensity": 0.2, "scaffolding": 0 } },
  "interactionType": "multiple-choice",
  "calculatorPolicy": "calculator-not-required",
  "estimatedTimeSeconds": 60,
  "media": [],
  "accessibility": { "spokenMath": "Find the mean of three, five, eight and four.", "nonColorIndicators": true },
  "provenance": { "origin": "generated", "rightsStatus": "academy-owned", "originalityNote": "Original parameterized item." },
  "lifecycle": { "state": "machine-validated", "validation": { "status": "pass", "validatorVersion": "1.0.0", "checks": [{ "name": "closure-agreement", "result": "pass" }] } }
}
```

This example exercises the load-bearing encodings: the `exact-rational` canonical `{num,den}` with `den=1` correctly typed `exact-rational` (the value 5 is exact; note where `den=1` and the objective also allows `integer`, the generator may instead store `type:"integer"` per the den-driven rule in O6); distractor `value` objects in the same `{num,den}` family; each `distractor.rationale` equal to its registry `observableError`; the difficulty `axes` drawn only from the closed enum (`numericalComplexity, reasoningSteps, readingDemand, interpretationDemand, informationDensity, scaffolding` — the six emitted axes per §9.1, all valid closed-enum members; here `scaffolding:0` for an unscaffolded item; the remaining axes are schema-absent); `interactionType: "multiple-choice"` (a valid enum value); and `media: []` for the no-chart list task. A parallel `table-completion` example (O5) would carry `answer.type:"table-completion"`, `interactionType:"free-response"`, and `canonical:{cells:[{cellId:"c2", value:{num:7,den:1}}]}` validated by `checkTableCompletion`.

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

The dataset is stored verbatim in `item.params` (canonical JSON, sorted keys, via `core/serialization/canonical.ts`), so the validator and the redraw harness reconstruct it without RNG and recompute each projection. The figure construction reuses the approved Cartesian projection from `gen.geometry.coordinate-lines` **in independent-scale viewport mode** (the single `gridRound` round-half-up projection over exact `Rational`, no runtime trig; independent x/y scales — §J) and the approved per-root `cx-figure` render-mode contract via the **additive `data-chart-theme` extension** (§7.2); bar/line/pictogram figures are layouts over that reused projection, not a new renderer, and coordinate-lines source is not edited. **Parity scope:** byte-parity Py/TS is required for the *canonical* `media[0].svg` (chart media) and the deterministic HTML frequency-table, plus `params`, `answer.canonical`, and the `distractors`. The `presentationSvg`/`exportSvg` render-mode layer is a **TypeScript-only presentation concern** — there is no Python theme mirror and the themed/exported copies are never serialised into the item, so no Python theme mirror exists or is promised.

### 4.2 The canonical `DataSet` object (the single source)

Every value is an exact integer; nothing in the dataset is a float. The dataset has **exactly one of two `kind` values — `"frequency" | "list"`** (this is the single, canonical `kind` vocabulary; §6/§11 `params-in-domain` use these literals verbatim). Field names below are canonical and are referenced unchanged by every validator-check description.

**Categorical / frequency dataset** (`kind: "frequency"`) — drives bar chart, pictogram, frequency table, `read_table_value`, and the `mean_from_freq_table` task:

| field | shape | meaning / invariant |
|---|---|---|
| `kind` | `"frequency"` | discriminator |
| `categories` | `string[]`, length `k`, `2 ≤ k ≤ 6` | category labels; deterministic order **is** the canonical chart/table/data-table order |
| `frequencies` | `number[]`, length `k` | non-negative integers, `frequencies[i] ≥ 0` |
| `unit` | `{ singular: string, plural: string }` | context noun ("student"/"students") for prompt + a11y |
| `pictogramKey` | `number \| null` | **the number of items represented by ONE complete symbol** (NOT symbols-per-unit); `pictogramKey ∈ {2,5,10}`; non-null **only** when `chartType === "pictogram"` and each `frequencies[i]` is a whole number of symbols, or an exact half-symbol when `pictogramKey` is even (§4.5, §G). This is the single key name — `glyphValue` / `freq` / `data` are NOT used. |

**List dataset** (`kind: "list"`) — drives `mean_from_list`, `median_from_list`, `mode_from_list`, `range_from_list`, the line graph (as an ordered `(index, value)` series), and `single_event_probability`:

| field | shape | meaning / invariant |
|---|---|---|
| `kind` | `"list"` | discriminator |
| `values` | `number[]`, length `n`, `3 ≤ n ≤ 9` | integers (may repeat; may be negative for context-free lists at higher bands, non-negative for counts) |
| `unit` | `{ singular: string, plural: string }` | context noun |
| `seriesLabels` | `string[] \| null` | **present ONLY for genuinely ordered line-graph data** (time / sequence x-values, e.g. months); `null` for an unordered numerical list. A line-graph dataset is a `list` PLUS non-null `seriesLabels` — there is no separate `"time-series"` kind. |

**No redundant sorted array is stored.** The dataset stores **only `values`** (in draw order); the validator and every derivation **independently sort** a local copy. There is no stored `sorted` field — storing one would duplicate state the validator must re-derive anyway, so median/range derivation sorts a local copy deterministically and parity-checks the result.

The single canonical names are: `frequencies` (not `freq`), `values` (not `data`), `pictogramKey` (not `glyphValue`), and `unit` for the context noun object. §6 and §11 use these exact names; any drift breaks `closure-agreement`/`svg-realises-data` because `params.dataset` is serialised with sorted keys and recomputed key-for-key.

A `list` dataset can be re-expressed as a frequency table internally (value → count) for any frequency-table-style derivation; that derived table is a pure function of `values`, so it is **not** stored separately.

**Probability source.** `single_event_probability` uses a `frequency` dataset (a bag/collection of objects) and attaches an **explicit `outcomeSpace = { favourable, total, targetCategoryIndex }` derived from it**, where `favourable = frequencies[targetCategoryIndex]`, `total = Σ frequencies`. Both are exact integers with `total ≥ 1` and `0 ≤ favourable ≤ total`. **The context describes equally-likely atomic outcomes** — "One item is selected at random from a bag containing the objects shown." — so each object is one equally-likely outcome and `P = favourable/total` is a genuine theoretical probability. **The frequencies are object counts, NOT experimental trial counts: experimental probability (relative frequency from repeated trials) is a later objective and is never conflated with this theoretical single-event probability.** Because `favourable` and `total` are read from the same frequencies that draw the figure, the displayed figure/table and the probability share one source; the `no-statistic-in-svg` check (§5.7) guarantees the figure never prints the fraction answer.

### 4.3 Parameter model and sampling

`params` mirrors the coordinate-lines pattern — a flat, canonical-JSON record sufficient to redraw the item with no RNG:

```
params = {
  task,                    // one canonical task id from the §4.6 enum (one spelling, used everywhere)
  chartType,               // "bar" | "pictogram" | "frequency-table" | "line"  (deferred types absent from the enum — §4.6)
  dataset,                 // the DataSet object above (the single source)
  targetCategoryIndex?,    // for read_bar_chart / read_pictogram / read_table_value / single_event_probability (the outcomeSpace target)
  blankCellId?,            // for complete_frequency_table: the SINGLE blanked cell id (one missing frequency or one total — §5.4)
  mc?,                     // boolean: whether multiple-choice is offered (drives interactionType — §4.6; always false for FR-only tasks)
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
| `range-zero-valid` (NOT a universal spread gate) | `range_from_list` | **`max > min` is NOT required universally (§H): `range = 0` (a uniform list) is a VALID low-band FREE-RESPONSE case.** A uniform list is valid; MC may remain ineligible for `range = 0` (3 distinct distractors impossible there) and falls back to FR. |
| `median-uniform-allowed` | `median_from_list` | **uniform lists are NOT excluded (§H)** — they are admitted at a controlled low frequency; the median of a uniform list is well-defined. |
| `medianDefined` | `median_from_list` | `n ≥ 3`; even-`n` two-middle average kept exact (§5.2) |
| `mode-unique` | `mode_from_list` | strict uniqueness: `maxFreq ≥ secondFreq + 1` over the value→count table. Multi-modal AND all-distinct ("no mode") lists are **redrawn** for v1.0.0 (§4.5). |
| `freqNotAllEqual` | `mean_from_freq_table` **when `mc`** | the frequencies are not all equal — otherwise the weighted mean equals the unweighted mean and the `IGNORES_FREQ` distractor would collide with the key (added per the MISSING finding) |
| `probExact` | `single_event_probability` | `total ≥ 1`; answer is `favourable/total` reduced via `Rational`; for MC, `total ≥ 4` so ≥3 distinct in-range distractors are reachable (§4.5) |
| `pictogramWhole` | pictogram render | `pictogramKey` divides every frequency (else render as a bar chart) |
| `readableChart` | all figure tasks | at least one positive frequency so the chart has a non-degenerate axis; max frequency bounded so bars fit the independent-scale viewport |

### 4.5 Degenerate cases — enumerated, never silent

- **Empty data:** excluded by `nonEmpty`. Mean/median/mode/range are undefined on `n = 0`; such draws are redrawn. No "0/0" ever reaches an answer.
- **Uniform data** (all values equal, e.g. `[4,4,4,4]`): mean = median = that value; **range = 0** (exact, §H). **`range = 0` is a VALID low-band FREE-RESPONSE case for `range_from_list`** — uniform lists are admitted (do NOT require `max > min` universally); MC may remain ineligible for `range = 0` (3 distinct distractors impossible) and falls back to FR. **`median_from_list` does NOT exclude uniform lists** either (admitted at a controlled low frequency, §H). Uniform data is, however, excluded from `mode_from_list` (a unique mode is required — see below). Negative values may appear in context-free numerical lists at higher bands; frequencies / category counts are always non-negative integers; line-graph negatives require a context + a labelled axis (§H).
- **Multi-modal** (two+ values tied for most frequent): fails `mode-unique` → **redrawn**. The single-value mode answer is therefore always well-posed for the seeds that survive. The `set`-valued (multimodal) mode encoding is **DEFERRED** (§5.3); no empty-set or total-set convention is emitted in v1.0.0.
- **No mode** (every value distinct, all counts 1): fails `mode-unique` → **redrawn**. There is no "empty set" / "all values" convention in v1.0.0 (deferred with the multimodal `set` encoding).
- **Even vs odd `n` for median:** odd → middle element of the sorted list (an integer); even → exact average of the two middle elements. If the two middles share parity the average is an integer (`den === 1`); if they differ in parity it is a half-integer (`Rational` with `den === 2`). Both are first-class (§5.2); the stored `answer.type` is set from the computed `den` (`integer` when `den === 1`, else `exact-rational`). **mean / median exact: integer when `den = 1`, else exact-rational (§H).**
- **Ties in the data list:** allowed; they are exactly what create the unique mode and equal-valued bars. The validator independently sorts a local copy (no stored sorted array), making tie-handling deterministic and parity-checked.
- **Pictogram non-divisible counts:** disallowed for pictogram rendering (`pictogramKey` must resolve to whole symbols, or an exact half when the key is even — keys 2/10); the same dataset renders as a bar chart instead. The figure never shows a misleading fractional symbol.
- **Probability endpoints:** `favourable === 0` (`P = 0`), `favourable === total` (`P = 1`), and `P = 1/2` are **free-response only** and are **never offered as MC** (§C, §5.5).

### 4.6 In-scope vs deferred — the canonical task list, deterministically excluded

**v1.0.0 chart scope:** `chartType ∈ { "bar", "pictogram", "frequency-table", "line" }`.

**v1.0.0 canonical task enum (one spelling each; the single source of truth referenced verbatim by §1–§3, §5, §8.3, §11, §13, §14):**

| task id | chartType | answer.type | objectiveId (the `OBJECTIVE_BY_TASK` constant) | MC? |
|---|---|---|---|---|
| `read_bar_chart` | bar | `integer` | `SPI.MIDDLE.STAT.READ.BAR_CHART.01` | yes |
| `read_pictogram` | pictogram | `integer` | `SPI.MIDDLE.STAT.READ.PICTOGRAM.01` | yes |
| `read_table_value` | frequency-table | `integer` | `SPI.MIDDLE.STAT.READ.TABLE_VALUE.01` | yes |
| `read_line_graph` | line | `integer` | `SPI.MIDDLE.STAT.READ.LINE_GRAPH.01` | yes |
| `complete_frequency_table` | frequency-table | `table-completion` | `SPI.MIDDLE.STAT.FREQ.COMPLETE_TABLE.01` | no (free-response only) |
| `mean_from_list` | bar | `integer \| exact-rational` | `SPI.MIDDLE.STAT.AVG.MEAN_LIST.01` | yes |
| `median_from_list` | bar | `integer \| exact-rational` | `SPI.MIDDLE.STAT.AVG.MEDIAN_LIST.01` | yes |
| `mode_from_list` | bar | `integer` | `SPI.MIDDLE.STAT.AVG.MODE_LIST.01` | yes |
| `range_from_list` | bar | `integer` | `SPI.MIDDLE.STAT.AVG.RANGE_LIST.01` | yes |
| `mean_from_freq_table` | frequency-table | `integer \| exact-rational` | `SPI.MIDDLE.STAT.AVG.MEAN_FREQ_TABLE.01` | yes |
| `single_event_probability` | frequency-table | `fraction` | `SPI.MIDDLE.STAT.PROB.SINGLE_EVENT.01` | yes (eligible proper P only) |

This is a strict 1:1 task↔objective bijection (11 tasks, 11 objectives) — the precondition for the inherited `objective-mapping` check, which asserts `item.objectiveIds === [OBJECTIVE_BY_TASK[task]]`. Objective IDs use the eleven canonical `SPI.MIDDLE.STAT.<TOPIC>.<MICRO>.01` literals pinned in §1 (stage `middle-school`, domain `statistics`); every section, including §11, references **these exact eleven literals**, never `READ.BAR.01` / `READ.TABLE.01` / `READ.LINE.01` / `FREQ.COMPLETE.01` / `AVG.MEAN_FREQ.01` / `SPI.MS.STATISTICS.*`. Note `mean_from_list` / `median_from_list` / `mode_from_list` / `range_from_list` show a numerical data list or simple data table as the PRIMARY representation; the `bar` chartType column denotes the dataset family, not an auto-converted bar chart (§E, §6.7).

**Deferred to a later version (structurally excluded):** pie chart, scatter/correlation, regression/line-of-best-fit, histogram, stem-and-leaf, box plot; the statistics standard deviation/variance, quartiles/IQR (§5.6), grouped-data estimated means; and the multimodal/no-mode **`set`-valued mode** answer (§5.3). Exclusion is **structural, not advisory**: `chartType` and `task` are closed enums in the generator; the deferred values are absent from the enum and from the dispatch tables (the analogue of coordinate-lines' `TASKS`/`FIGURE_TASKS`), so no seed can ever produce them. The artifact-integrity test asserts the enum membership, so re-introducing a deferred type without curriculum sign-off fails the build.

---

## 5. Answer representation and equivalence checkers

### 5.1 Encoding rules common to all tasks

Every answer uses an **existing** `answer.type` enum value — **no `answer.type` enum edit and no schema change are required** (each type below is already in the platform `answerType` enum, verified against `schemas/question-item.schema.json`):

- `integer` / `exact-rational` / `fraction`: canonical is the reduced rational object `{num, den}`, `den ≥ 1`. `integer` carries `den === 1`; `exact-rational`/`fraction` carry `den > 1`. The schema's `allOf` `if/then` constraints for `integer` (`den` must be `1`) and `exact-rational` (`{num, den≥1}`) are honoured exactly; the inherited `answer-type-consistency` discipline (`integer ⇔ den === 1`) is preserved.
- `ordered-pair`: **not used by v1.0.0 read-offs** (see below).
- `table-completion`: free-form canonical `{ cells: [...] }` (§5.4); the schema has no `if/then` for this type, so it is **checker-validated** (stated explicitly to satisfy the "no falsely-claimed schema change" check). `table-completion` is the `answer.type`; the `interactionType` is `free-response`.
- `set`: **deferred** (the multimodal mode path — §5.3). `checkUnorderedSet` is therefore proposed but not exercised in v1.0.0.

**Read-offs are plain `integer` (resolving the ordered-pair-not-in-objectives finding).** Reading a value from a bar/pictogram/table/line graph yields an `integer` answer checked by `checkExactRational`. The `ordered-pair`/`checkOrderedPair` "which category has value v / read the point at month M" variant is **dropped from v1.0.0**, because (a) the read objectives declare only `answerTypes:[integer]`, and an item's `answer.type` must be in its objective's `answerTypes`; and (b) `checkOrderedPair`'s canonical is a numeric `{x:{num,den}, y:{num,den}}` (verified `coordinate-checkers.ts:36`) and cannot represent a string category label. If a labelled point read-off is wanted later, it requires adding `ordered-pair` to the objective's `answerTypes` AND constraining the first component to an integer index.

All numeric canonicals are produced by exact `Rational` arithmetic (`core/exact-math/rational.ts`), so `{num, den}` and the display string match the Python oracle byte-for-byte. The display form for a `Rational` answer is selected deterministically: integer when `den === 1`; otherwise the fraction `num/den`. For **mean / median** (`exact-rational`) a terminating decimal is offered as an accepted equivalent when `terminates(den)`. **Probability (`fraction`) is the exception: the canonical is the SIMPLEST-FORM fraction, decimals are NOT accepted, and an unreduced equivalent does not get full correctness (§5.5, §I)** — reusing `checkExactRational(input, {num,den}, accepts)` with `accepts.decimal:false` and reduced-form enforcement for this task. No checker touches a float for the accept/reject decision.

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
- **Median** from a **locally sorted copy of `values`** (the validator independently sorts; no stored sorted array): odd `n` → the middle element as an integer `Rational`; even `n` → `(a + b) / 2` of the two middle elements, an exact `Rational` (`den ∈ {1, 2}`). Example: `[2,3,6,9] → (3+6)/2 = 9/2`. **The stored `answer.type` is set from the computed `den`** — `integer` when the two middles share parity (`den === 1`), `exact-rational` when they differ (`den === 2`). The coverage matrix (§13.2) lists `median_from_list` as `integer | exact-rational`, NOT pinned to `exact-rational`, so the `answer-type-consistency` check (`integer ⇔ den === 1`) passes. The two-middle-values average is first-class, never rounded.
- **Range** `= max − min` over an independently-sorted local copy, always a non-negative integer (`answer.type:"integer"`). **`range = 0` (uniform data) is a VALID low-band FR case (§H, §4.5)** — `max > min` is NOT required universally; MC may be ineligible at `range = 0` and the item falls back to FR. The checker is `checkExactRational` with `accepts:{decimal:false}` (range is integral).
- **Read a value** from a bar/pictogram/table/line graph: the read-off is an `integer` answer via `checkExactRational`. Pictogram read-offs multiply the symbol count by `pictogramKey`, and the solution shows that multiplication.

### 5.3 Mode — single-value, unique, `integer` (v1.0.0)

For v1.0.0 the mode is computed over the value→count table of `sorted` and is gated to a **strictly unique** modal value by `mode-unique` (§4.4). The canonical encoding is therefore a single `integer` (`answer.type:"integer"`, `{num, den:1}`), checked by `checkExactRational`. Examples: `[2,2,5] → 2`; `[1,1,2,2,2,9] → 2`.

**The `set`-valued mode is DEFERRED** (resolving the dead-path / three-way-convention contradiction). Because `mode-unique` redraws every multimodal and every all-distinct ("no mode") list, the `set` machinery (`checkUnorderedSet`) would never be exercised in v1.0.0; it is moved to the deferred list together with a future "taught multimodal / no-mode" sub-objective. There is therefore **no empty-set, total-set, or `set`-typed mode answer in v1.0.0**, and the conditional empty-set language is removed from this proposal's in-scope surface. When the deferred work lands, `checkUnorderedSet` will compare each set element by the **same reduced-`Rational` equality** used for scalar answers (so a stored `{num:4,den:1}` matches a submitted `4`), with the set sorted ascending and de-duplicated for a byte-stable canonical.

### 5.4 Table-completion (frequency-table cells)

For `complete_frequency_table`, the prompt shows a frequency table with **exactly ONE cell blank — one missing frequency OR one missing total** (no underdetermined multi-blank); `interactionType:"free-response"` (**FR-only, no MC variant**) and `answer.type:"table-completion"`. The canonical is a keyed map of the (single) blanked cell, in the cells-array shape (kept uniform for future multi-blank work, but always one entry in v1.0.0):

```
answer.canonical = { cells: [ { id: "freq.<categoryIndex>" | "total", value: {num, den} } ] }   // exactly one cell in v1.0.0
```

`checkTableCompletion` canonicalises each submitted cell to a reduced `Rational` keyed by `id`, then requires (a) the submitted cell-id set to equal the required set exactly (no missing, no extra) and (b) every cell to be exactly equal. Frequencies are integers (`den === 1`); a "Total" cell is `Σ frequencies`. Because the table is a pure projection of the same `DataSet`, the blanked values and their answers are guaranteed consistent with the chart and the a11y data-table. The `{cells:[...]}` shape is free-form under the schema (no `if/then` for `table-completion`), validated solely by `checkTableCompletion`; the validator's `table-cells-match-dataset` check (§5.7) re-asserts the cell ids and values are the exact projection of `params.dataset`.

### 5.5 Probability (single event) as an exact fraction

**Objective wording (verbatim):** "Find the probability of a single event with equally likely outcomes, giving the answer as a fraction in its simplest form." `single_event_probability` encodes `P = favourable / total` from `outcomeSpace`, built as one `Rational` and **reduced to simplest form** (e.g. `3/12 → 1/4`). `answer.type` is `fraction`; the **canonical is the reduced fraction**. **Decimals are NOT accepted** (`accepts:{ fraction:true, decimal:false, mixed:false }`), so `0.25` is rejected even though it equals `1/4`. **FR examples cover `P=0`, `P=1`, `P=1/2`, and other proper fractions** (these endpoints are free-response only — §I, §C). **An unreduced equivalent must NOT receive full correctness:** `2/8` does not pass as fully correct; where targeted feedback is supported the learner is told "Your value is equivalent, but simplify the fraction.", and otherwise v1.0.0 simply **requires the reduced fraction** (`checkExactRational` is configured to accept only the simplest form for this task, not arbitrary equivalents).

**Single reconciled, in-range distractor rule.** The probability misconception distractor is the **odds-as-fraction** value `favourable / (total − favourable)` (registry `MISC.STAT.PROB.ODDS_AS_FRACTION`, summary "writes wanted-to-unwanted instead of wanted-to-total"). This lies in `(0, 1)` exactly when `favourable < total − favourable`, i.e. `favourable < total/2`. **Every probability distractor must lie in `[0, 1]`** (the `prob-distractor-in-range` MC gate) and differ from `P` as exact Rationals; **an out-of-[0,1] value is NEVER used as a distractor** — when a value leaves the unit interval or equals the key, that distractor is dropped and backfilled, else the seed is redrawn. The earlier `total/favourable` formulation is **removed** (it is `≥ 1` for every proper probability). The `favourable === total` (P=1), `favourable === 0` (P=0), and `P=1/2` endpoints are **FR-only** and never offered as MC (§4.5, §C). With a sufficient outcome space and the in-range filter, ≥3 distinct misconception-backed distractors in `(0, 1)` are reachable. **An unreduced fraction (`2/8`) is never used as a distractor.** Note the probability checker requires the **reduced** form (above), so an unreduced student answer does not get full correctness — distinct from the equivalent-accepting policy used for non-probability rational answers.

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

**Inherited-vs-overridden validator checks (the per-check disposition for the figure-side gates these answer checks sit beside).** Because three inherited coordinate-lines checks cannot transfer verbatim to statistics figures, §6/§11 REPLACE rather than inherit them; this is flagged here because the answer encodings depend on it: (1) `no-answer-label-in-svg` (inherited predicate bans `text` containing `,`/`/`/`=`) is **replaced** by the statistics-specific **semantic** `no-statistic-in-svg` + §L role-based leakage checks (no dedicated answer/statistic annotation, no solution overlay, no correct-option styling in student media; **raw data / labels that coincidentally equal the answer are allowed**) — category labels, the pictogram key line, and axis-unit text legitimately contain `=`/`/`/`,`; (2) `tick-labels-integer` stays **verbatim** but applies only to the integer count axis — category strings are emitted under a separate `cx-cat` class, never `cx-ticklbl`; (3) `media-to-scale` (asserts `toScale === true`) is inherited **verbatim for bar/line** charts and **replaced for pictograms** (symbol-count figures carry `toScale:false` plus a `pictogram-key-exact` check). The full inherit/override/replace table lives in §11.4; it is referenced here so the answer-side checks above are understood to run alongside the *replaced*, not the verbatim, figure gates.


---

## 6. Chart types and the SVG renderer contract

This section fixes the **canonical, monochrome-authoritative** chart renderer for `gen.stats.data-handling` v1.0.0 and the per-chart contract every figure must satisfy. It does **not** invent a renderer: it extends the Cartesian discipline already shipped and approved in `gen.geometry.coordinate-lines` (`domains/geometry/coordinate-lines.ts` / `oracle/spi_oracle/coordinate_lines.py`) — a single source of truth (`params` → a seeded dataset), all coordinates produced as **integers** by `gridRound(num, den)` round-half-up over exact `Rational`/`Fraction`, **no runtime trig and no floats in the emitted geometry**, a hand-serialised SVG that is **byte-for-byte identical between TypeScript and the Python oracle**, and the `cx-*` class vocabulary read by the approved `core/visual-style/cartesian-theme` (§7). Colour is a presentation overlay over this same canonical geometry and **never carries meaning alone**.

> **The canonical monochrome SVG is AUTHORITATIVE and carries NO `class="cx-figure"`.** Exactly as the coordinate-lines `figure()` (`coordinate-lines.ts` line 189: `<svg … viewBox="0 0 1000 700" role="img" aria-label="…">` with an internal monochrome `<style>` block, **no** `class` attribute), the stored `media[0].svg` is the un-themed, short-hex monochrome figure with its own embedded `<style>`. The `class="cx-figure"` root + per-root `--cx-*` custom properties are stamped **only** by `presentationSvg()` / `exportSvg()` (`core/visual-style/cartesian-theme.ts` lines 60–69) at presentation/export time; they never mutate the canonical figure. Every downstream gate — the golden + 150×2 parity fixtures, the `SPI_SWEEP = 10000` stability sweep, the independent validator (`validate(item) → {status, validatorVersion, checks[]}`), the bank-json round-trip, and the offline HTML exporters — re-derives, re-serialises, and byte-compares **this** canonical `media[0].svg`. The premium / premium-dark / accessible / print skins add no positional information and never become a second stored figure (§7).

### 6.1 The single dataset is the source of truth for every artifact

The renderer is a pure function `chartSvg(model, alt, title, desc) → string`, where `model` is built **only** from the deterministic seeded **dataset** serialised verbatim into `params.dataset` (canonical JSON, sorted keys) — the same object that feeds the prompt, the answer, the solution, and `media[].dataTableFallback`. There is **one canonical `DataSet` field schema**, pinned here and referenced by that exact spelling in every other cluster (§4.2, §11.1, and every validator-check description); the discriminator is `kind ∈ {"frequency", "list"}` (two values only — line-graph/time-series is a `list` with `seriesLabels`; a frequency table is a `frequency` dataset):

| `kind` | Canonical fields (exact names) | Invariant |
|---|---|---|
| `"frequency"` | `categories: string[]`, `frequencies: int[]` (parallel arrays), `unit: {singular,plural}`, `pictogramKey?: int` (the number of items represented by ONE complete symbol; present only when `chartType === "pictogram"`) | `len(categories) == len(frequencies)`; every `frequencies[i]` a non-negative **integer**; `1 ≤ len ≤ MAX_CATEGORIES`; `Σ frequencies ≥ 1` |
| `"list"` | `values: int[]`, `unit: {singular,plural}`, `seriesLabels?: string[]` (line-graph ordered x-axis labels, `len == len(values)`, present only for ordered line-graph data) | every value an **integer**; `1 ≤ len ≤ MAX_LIST_LEN`; stored in draw order (sorting is a derivation step, never a stored mutation); **no redundant sorted array is stored** |

> **Field-name discipline.** The canonical names are `frequencies` (not `freq`), `pictogramKey` (not `glyphValue`/`unit?` — `pictogramKey` is the number of items per ONE complete symbol, used consistently and as the only name for this concept), `values` (not `data`), `categories`, `seriesLabels`, `unit`. Because the dataset is serialised verbatim and the validator recomputes the figure/answer from those exact keys, any drift breaks `closure-agreement` / `svg-realises-data` reproducibility; these spellings are the single source of truth everywhere. No second alternative key name is introduced for any field.

The **same** `"frequency"` dataset realises a bar chart, a pictogram, or a frequency table; the **same** `"list"` dataset realises a line graph and the mean/median/mode/range tasks. The chart, the prompt text, the canonical answer, the worked solution, and the accessibility data-table are therefore five views of **one** integer dataset, which is exactly what makes `dataset-realises-chart` (figure recomputed from `params.dataset`) and `closure-agreement` (answer recomputed by a second route) byte-deterministic across Py/TS. The window, the unit scale, and the integer offsets come from §7 and are part of `model`; the renderer **never recomputes** them.

### 6.2 v1.0.0 chart set and deferrals — deterministically excluded

A chart type is **in v1.0.0 only if its geometry is exact-integer, faithfully readable, and answer-free where the figure must not reveal the answer.** Deferred chart types are **deterministically excluded** — the generator never selects a deferred `chartType`, deferred types are **absent from every dispatch table** (never reachable), and the validator's `chart-type-in-scope` check (§6.9) fails any item carrying one, so a deferred chart can never be silently emitted.

| Chart type | v1.0.0? | Tasks served | Rationale |
|---|---|---|---|
| **Bar chart** (vertical) | **IN** | `read_bar_chart`, `read_table_value` (table form), `complete_frequency_table` (table form), `mean_from_freq_table` | Integer frequencies → integer bar heights on an equal-step count axis; the cleanest reuse of the Cartesian axis/gridline/tick discipline. |
| **Pictogram** | **IN** | `read_pictogram` | A `"frequency"` dataset with a committed integer `pictogramKey ∈ {2,5,10}` (one complete symbol = `pictogramKey` items); each row draws `floor(frequencies[i]/pictogramKey)` whole symbols + an **exact half-symbol** when `pictogramKey` is even and `frequencies[i] mod pictogramKey === pictogramKey/2` (only keys 2 and 10), clipped by an integer-coordinate path. Quarter / arbitrary fractional / partially-clipped symbols (other than exact half) are **deferred**. No trig, no float. |
| **Frequency table** | **IN** | `read_table_value`, `complete_frequency_table`, `mean_from_freq_table` | **A semantic HTML table is the authoritative learner-facing + accessible renderer** (proper `table`/`tr`/`th`/`td` semantics, keyboard-accessible input cells, deterministic HTML serialisation, print-safe, offline, exact round-trip from the canonical dataset; blank cells stay blank in the student version, answers only in the answer-key/solution — see §F note below). An **optional SVG snapshot** may be derived from the same canonical table model for the gallery/raster but does NOT replace the semantic HTML table. **Table validation is INDEPENDENT from chart-SVG validation** (deterministic HTML-table parity, not SVG byte-parity). For `complete_frequency_table` exactly one cell is blanked — one missing frequency OR one missing total (answer.type `table-completion`, interactionType **`free-response` only** — see §6.9 / §11.4). |
| **Line graph** (time series) | **IN** | `read_line_graph` | A `"list"` dataset plotted as `(i, value)` integer lattice points joined by a polyline — a **direct reuse** of the coordinate-lines plotted-point + clipped-segment primitives (`pointEls`, `lineEl`, the §7 projection). |
| **Pie chart** | **DEFER** | — | Sector boundaries need angles; faithful sectors require `sin/cos`, forbidden in emitted geometry (no runtime trig), and exact sector angles are generally irrational fractions of the circle. **Absent from every v1.0.0 dispatch table.** (If later admitted, only via a committed integer **direction table** restricting to partitions whose angles land on tabulated directions, mirroring the coordinate-lines arrowhead construction.) |
| **Scatter plot** | **DEFER** | — | Plotting integer `(x, y)` pairs is in-discipline, but the v1.0.0 *reading* task ("describe the correlation") is a qualitative judgement, and any line-of-best-fit / regression is **irrational** and out of scope. The scatter *primitive* (lattice points, no join) is reusable infrastructure; the **correlation task is deferred and structurally absent.** |
| **Histogram** | **DEFER** | — | Distinguished from a bar chart by **continuous class intervals and frequency density** (`frequency / class width`), introducing non-integer density that exceeds the v1.0.0 exact-integer frame. **Excluded.** |
| **Stem-and-leaf** | **DEFER** | — | A typographic table with its own back-to-back and key conventions, a distinct layout primitive. **Excluded from v1.0.0**, scheduled as a fast follow (needs no new math, only a new text-layout primitive). |

> **Frequency-table renderer (§F).** The authoritative learner-facing and accessible renderer of every frequency table (`read_table_value`, `complete_frequency_table`, `mean_from_freq_table`) is a **semantic HTML table** with proper `table`/`tr`/`th`/`td` semantics, keyboard-accessible input cells, **deterministic HTML serialisation**, print-safe and offline, with an **exact round-trip from the canonical dataset**. Blank cells stay blank in the student version; answers appear only in the answer-key / solution channel. An **optional SVG snapshot** may be derived from the same canonical table model (for gallery / raster) but **must NOT replace** the semantic HTML table. **Table validation is INDEPENDENT of chart-SVG validation:** tables are gated by deterministic HTML-table parity (round-trip + serialisation), charts by canonical SVG byte-parity.

> **Statistics in v1.0.0 are EXACT only.** Mean, median, mode (unique), and range from a `"list"` or a `"frequency"` dataset are exact `Rational`/`integer` values; **standard deviation / variance (surds), frequency density, quartiles/IQR, grouped-data estimated means, and regression/best-fit lines are deferred and never emitted** (the `no-irrational-statistic` check, §6.9, fails any answer whose canonical value is not a finite reduced `{num, den}`). Single-event probability is an exact `fraction` answer (`favourable/total`, reduced). The probability item **does show its bag/category frequency table** (the semantic HTML table or its SVG snapshot), drawn from the same `{favourable, total}` outcome space; the `no-statistic-in-svg` / no-answer-in-table checks guarantee the figure/table never prints the fraction answer.

### 6.3 Chart primitives needed, and where reusable pieces live

The coordinate-lines renderer already provides the **reusable Cartesian substrate**: the single `gridRound` projection of record (§7), axes with integer arrowheads, major/minor gridlines, integer ticks with a deterministic label-thinning stride (`MAX_LABELS_PER_AXIS`), plotted points (`cx-pt-outline` halo under `cx-pt-core`), a clipped straight `cx-line`, the integer collision-avoidance label placer, the `esc` XML-escape map, and the deterministic element-emission order. Line graphs **reuse these unchanged** (in the independent-scale viewport mode — §7.1). Statistics adds its chart primitives in the **additive `core/render/data-charts/` extension** (§7.2, §K), reusing the projection without modifying any coordinate-lines source:

| New primitive | Role | Home (additive extension; reuses coordinate-lines projection) |
|---|---|---|
| **Bars** | `barEls(catIndex, height, Uy, Px) → string[]` — an integer-coordinate `<rect>` (or `<path>`) on the count axis, plus a committed greyscale **inline hatch** (a set of integer-coordinate `<line>` strokes clipped to the bar, **no `<pattern>`/`url(#…)`** — see §6.6) so adjacent bars differ without colour | `core/render/data-charts/bars.ts` (TS); `oracle/spi_oracle/render/data_charts/*` (Py mirror) |
| **Category axis** | a discrete, **equal-step** horizontal axis carrying category **labels** under each bar/symbol column (class `cx-cat`, **never** `cx-ticklbl` — §6.5); integer column centres via the §7 projection | `core/render/data-charts/category-axis.ts` |
| **Pictogram symbols** | `iconEls(catIndex, count, pictogramKey) → string[]` — a committed integer symbol glyph repeated `floor(frequencies[i]/pictogramKey)` times, plus one exact half-symbol (keys 2/10 only); a **key** ("1 symbol represents `pictogramKey` items") is always emitted | `core/render/data-charts/pictogram.ts` |
| **Table grid** | `tableGrid(dataset, blankCell?) → string[]` — ruled integer rows/cols of `<text>` cells; an SVG snapshot derived from the same canonical table model (the authoritative learner-facing renderer is the semantic HTML table — §F) | `core/render/data-charts/table-grid.ts` |

These live under `core/render/data-charts/*` (the additive extension) so they are shared, not copied: the projection/axis code that coordinate-lines proved is **reused unchanged** (same `gridRound`, same byte output) and the extension imports it without editing coordinate-lines. **No parallel renderer is created, and coordinate-lines source is not modified.** The pie-sector primitive is **NOT built in v1.0.0** (the deferral is explicit, not a silent gap).

### 6.4 Canvas, frame, and the single projection of record

- `viewBox` is fixed at **`0 0 1000 700`** (`VIEW_W = 1000`, `VIEW_H = 700`), identical to coordinate-lines.
- An integer count/value scale **`Uy`** (integer px per count unit) governs the **count / value axis** of bar and line charts; the **category / ordered-x axis** uses a separate committed integer **column pitch** `Px` (px per slot) so categories / ordered observations are evenly spaced. **`Uy` and `Px` are INDEPENDENT** (different quantities — §J); both are integers, chosen by §7.
- **There is exactly one projection of record, defined in §7.** It keeps the centering offset and the unit-scaled term **inside one exact `Rational`** and applies a **single** `gridRound` at the end — exactly as `projX`/`projY` do in `coordinate-lines.ts`. This section commits no separate projection formula. For integer dataset values and integer `Uy`/`Px` the unit-scaled term is already integer, so the only rounding is the single `gridRound`; for the one fractional case (a pictogram exact half-symbol, i.e. `frequencies[i] mod pictogramKey === pictogramKey/2`) the same single `gridRound` runs over the whole exact sum. No `Math.*`, no `sin`/`cos`, no float division survives into the string.

### 6.5 Style block and the `cx-*` class vocabulary (reused substrate + additive statistics classes)

The canonical `<style>` block **reuses** the committed monochrome short-hex axis/grid/line classes from the coordinate-lines contract (unchanged) and **adds** the statistics classes in the `data-charts` extension's own canonical `STYLE` fragment — the coordinate-lines `STYLE`/`GREYS` constants are **not edited** (§7.2, §K). All are monochrome; every distinction is carried by **width, greyscale, and inline hatch geometry**, never colour. The `no-colour-only-information` check asserts every `fill:`/`stroke:#hex` in the canonical statistics SVG is a subset of the greys already valid in the reused contract (`{#111,#333,#444,#555,#888,#bbb,#fff}`). **The statistics classes deliberately confine themselves to those existing greys — no shared `GREYS` set is mutated, and coordinate-lines output stays byte-for-byte unchanged.** The exact committed palette (all members of the existing grey set):

| class | role | committed canonical colours |
|---|---|---|
| `.cx-axis` · `.cx-tick` · `.cx-ticklbl` | count/value axis, ticks, **integer** count-axis labels | `#111` / `#111` / `#333` (reused from contract) |
| `.cx-grid-major` · `.cx-grid-minor` | count-axis gridlines | `#888` / `#bbb` (reused from contract) |
| `.cx-line` · `.cx-pt-core` · `.cx-pt-outline` | line-graph polyline + plotted points | `#111` / `#111` / fill `#fff` stroke `#111` (reused from contract) |
| `.cx-lbl` · `.cx-guide` | value labels · data-point labels | `#111` / `#555` (reused from contract) |
| **`.cx-bar`** | bar fill + outline | **new (extension)**: `fill:#bbb;stroke:#111;stroke-width:2.5` |
| **`.cx-bar-hatch`** | inline hatch strokes drawn inside a bar | **new (extension)**: `stroke:#555;stroke-width:1` (grey already in the set) |
| **`.cx-cat`** | category-axis labels (text under each column) | **new (extension)**: `font-size:22px;fill:#333` |
| **`.cx-icon`** | pictogram symbol glyph + its clipped half; outline `#111` | **new (extension)**: `fill:#444;stroke:#111;stroke-width:1.5` |

The **invariant** (asserted by `axes-stronger-than-grid`, reused): `width(.cx-axis) > width(.cx-grid-major) > width(.cx-grid-minor)`, and `.cx-bar`/`.cx-icon` outlines are distinct from gridlines by width and greyscale. Bars are distinguished from one another by **a per-category hatch density/orientation** (an integer-parametrised inline stroke set, §6.6) plus the category label and (where shown) a legend, not by fill hue. The premium / premium-dark / accessible / print modes (§7) preserve this width-and-pattern hierarchy.

### 6.6 Deterministic element order and the id-free hatch

The serialiser emits in **one fixed order** so the byte stream is canonical (matching the coordinate-lines `minor-grid → major-grid → axes → ticks → guides → line → points → labels` discipline): root `<svg role="img" aria-label="…">`, `<title>`, `<desc>`, `<style>`; then **minor gridlines**, **major gridlines**, **count axis** (+ integer arrowhead, + integer tick labels), **category axis** (column labels under class `cx-cat`), the **chart body** (bars in `categories[]` order, each immediately followed by its inline hatch strokes / icons in `categories[]` order / the line-graph polyline then its points / table rows top-to-bottom), then **value labels** placed by the reused label engine, then `</svg>`.

**No `id` attribute and no `url(#…)` reference appears in the canonical SVG** (safe multi-item worksheet export). The greyscale hatch that distinguishes bars is therefore **not** an SVG `<pattern>`/`fill=url(#…)`; it is **inline clipped stroke geometry** — a deterministic set of integer-coordinate `<line class="cx-bar-hatch" …>` elements whose endpoints are computed from the bar's integer rectangle (a fixed integer stride per category index, clipped to the bar edges by integer min/max, no float). Each bar's `<rect>` is emitted first, then its hatch lines, in element order. This keeps integer-only coordinates and the no-id/no-url(#) invariant; the `bar-pattern-distinct` check (§6.9) inspects the inline hatch elements, never a pattern id. All numeric attributes are integers; text is XML-escaped with the same `esc` map.

### 6.7 Independent-axis scaling (statistical, NOT coordinate-geometry equal-scale), and `toScale`

**Statistical graphs do NOT use the coordinate-geometry equal x/y pixel scale.** Each axis is internally linear and uniformly scaled, but the x and y axes measure **different quantities** and use **independent** scales (§J). The rendered model preserves every data value exactly through **one deterministic `gridRound` projection**, and the Py/TS canonical SVG is byte-identical. `toScale:true` here means **"each axis faithfully represents its own declared scale"**, NOT equal pixels per unit.

- **Line graph:** **uniform x spacing** for the ordered observations (one integer column pitch `Px` per ordered x-position), with the **y scale selected independently from the data range** (one integer `Uy` px per count unit). The two are **not equal px/unit** — x indexes ordered observations, y is the measured value. Only marked lattice points are queried, no interpolation; `media[].toScale = true` (each axis faithful to its own declared scale).
- **Bar chart (vertical only in v1.0.0):** the **count axis** uses a single integer `Uy` (uniform per chart, so bar heights are directly comparable and `0` sits on the baseline); the **category axis** uses a uniform integer column pitch `Px`. The two axes measure different quantities, so they are **independently scaled** but each is **internally uniform** — the §6.9 `uniform-count-scale` and `uniform-category-pitch` checks assert this, plus a pinned **count-axis step from {1,2,5,10}** so ticks/gridlines/bars agree. `media[].toScale = true` (the count axis is faithful to its declared scale; no "NOT TO SCALE" label is emitted). A bar baseline is always the projection of count `0`, guaranteed inside the window by §7.
- **Pictogram:** a pictogram is a **symbol-count figure, not a height-to-scale figure** (a row's meaning is its symbol count + the key, not a measured length). Pictograms therefore carry **`media[].toScale = false`**, and the family **does not inherit the `media-to-scale` gate for pictograms** (the inherited check hard-asserts `toScale === true` for every figure task — see the §6.9 inherit/override table). Instead, pictograms are gated by `pictogram-key-present` + `pictogram-partial-exact`. **bar/line = `toScale:true` under `media-to-scale`; pictogram = `toScale:false` under `pictogram-key-*`.**
- **Frequency table:** a table is not a scaled figure; it carries no `toScale` obligation (the table-grid is a pure layout) and is gated by `data-table-matches-dataset`.

### 6.8 Answer-free figures where the figure must not reveal the answer

The dataset feeds both the figure and the answer, so the renderer enforces **per-task leakage rules**, mirroring the coordinate-lines `plot-point-target-absent` discipline:

- **Read-a-value** (`read_bar_chart` / `read_pictogram` / `read_line_graph` / `read_table_value`): the figure shows all data (that is the point of the task) but **no `<text>` equals the queried value's display string** beyond the axis ticks / table cells the student must read; the answer is the read-off integer, never printed as a redundant label.
- **Complete-a-frequency-table** (`complete_frequency_table`, answer.type `table-completion`, interactionType `free-response`): the blanked cell is rendered **empty** (the `table-blank-cell-empty` check fails any item whose blanked cell already shows its value), and the accessibility data-table likewise blanks it.
- **Compute mean / median / mode / range / probability**: the figure/table shows the raw data; **the computed statistic is never drawn** as a dedicated annotation. The statistic appears **only** in the answer key / worked solution, derived deterministically from the same dataset.

**Answer-leakage is judged by SEMANTIC checks, not raw text equality (§L).** A figure is **NOT rejected merely because some raw-data text equals the answer** — a list may legitimately contain its own mean / median / mode / range / numerator / denominator, an axis tick may coincidentally equal the answer, and accessibility text may describe the raw data. Leakage is judged by **element role + render intent**, requiring:

| Check | Asserts |
|---|---|
| `no-derived-statistic-annotation` | the student figure carries **no dedicated mean/median/mode/range/probability/answer annotation** (a label whose render role is "the computed statistic"). |
| `no-answer-role-in-student-render` | no element in the student figure carries an answer/result role. |
| `no-solution-overlay-in-student-render` | no solution overlay appears in the student figure. |
| `raw-data-equality-is-not-leakage` | raw data (or an axis tick) that **coincidentally** equals the answer does **not** count as leakage — only a dedicated answer/statistic-role element does. |
| `student-a11y-does-not-state-result` | the student-facing accessibility text may describe raw data but **must NOT state the computed result**; no answer-speaking text appears in the student-facing `spokenMath` field. |
| `answer-overlay-present-only-in-solution-mode` | any answer/solution overlay exists **only** in the answer-key / solution channel, never in student media; answer/solution narration lives only in the answer-key/solution channels. |

There is **no correct-option styling in student media**. These semantic checks replace any naive "no `<text>` equals the answer string" rule (which would wrongly reject a legitimate self-referential list).

### 6.9 Validator checks: inherited (verbatim / overridden / replaced) + new statistics checks

The family runs the coordinate-lines validator battery, but **three inherited checks cannot transfer verbatim** because they assume a single-coordinate Cartesian figure with no category text, no key, and a height-to-scale figure. The table below is the authoritative inherit/override/replace map; every check still runs in **both** the Python oracle and the TS mirror with byte-identical results and appears as `{name, result, detail}` in `validate(item).checks[]`, **blocking** (any `fail` ⇒ `status = fail`).

**Inherited VERBATIM:** `svg-realises-data` (specialised as `dataset-realises-chart`), `closure-agreement`, `axes-stronger-than-grid`, `min-three-distractors`, `distractors-distinct-misconceptions`, `distractor-value-matches-rule`, `distractor-not-answer` (computed over **exact reduced `{num,den}` equality**, not display strings — so `2/8` and `1/4` are NOT distinct), `distractor-rationale-matches` (each `distractor.rationale` is set **equal to** the registry `observableError` string), `exactly-one-correct`, `provenance-complete`, `version-fields-present`, `objective-mapping`, `a11y-*`.

**Inherited but OVERRIDDEN / REPLACED:**

| Inherited check | Disposition | Reason / replacement |
|---|---|---|
| `no-answer-label-in-svg` (fails any `<text>` containing `,`, `/`, `=`) | **REPLACED** by the semantic role-based `no-statistic-in-svg` + §L leakage checks | Statistics figures legitimately render category labels (which may contain `,`/`/`, e.g. `km/h`, `Year 7, boys`) and a pictogram **key** (`1 symbol represents 5 items`). The character-blocklist would fail **every** pictogram and most labelled bar charts. The replacement judges leakage by **element role + render intent** (no dedicated answer/statistic annotation, no solution overlay, no correct-option styling in student media), NOT by raw text equality — **raw data, axis ticks, and labels that coincidentally equal the answer are allowed** (§L). A pinned test asserts a pictogram with a key line **passes**, a list containing its own answer **passes**, and a figure with a dedicated answer annotation **fails**. |
| `tick-labels-integer` (line 832/1063: scrapes `<text class="cx-ticklbl">`, requires integers) | **INHERITED VERBATIM, scope clarified** | Category strings are emitted under `cx-cat` **only**; `cx-ticklbl` is reserved for the integer **count-axis** labels. A pinned test asserts no `cx-ticklbl` `<text>` is non-numeric (so `tick-labels-integer` stays green) and that category strings appear **only** under `cx-cat`. The `category-label-correctness` check (§11.4) scrapes `cx-cat` for the ordered category strings and `cx-ticklbl` for integer ticks **separately**. |
| `media-to-scale` (line 828: `toScale === true` for all figure tasks) | **OVERRIDDEN per task** | Applied to **bar / line** figures (`toScale:true`); **not** applied to pictograms (`toScale:false`, gated instead by `pictogram-key-present`/`pictogram-partial-exact`); frequency tables carry no `toScale` obligation. |
| `no-colour-only-information` (colours ⊆ the shared grey set) | **INHERITED VERBATIM; NO change to the shared grey set** | the statistics classes use only greys already in the set (`.cx-bar #bbb`, `.cx-bar-hatch #555`, `.cx-cat #333`, `.cx-icon #444` — all committed in §6.5), so the canonical statistics SVG's fill/stroke colours are already a subset; no grey is added and no coordinate-lines source is edited. A pinned test asserts the subset relation. |
| `interaction-type` (line 810: passes only for `free-response`/`multiple-choice`) | **INHERITED VERBATIM** | Every task — including `complete_frequency_table` — carries `interactionType: "free-response"` (or `"multiple-choice"` when MC is offered). `table-completion` is an **answer.type only**, never an interactionType (it is absent from the schema interactionType enum, lines 121). No schema change is claimed or required. |

**New statistics checks (in addition to the above):**

| Check | Asserts |
|---|---|
| `chart-type-in-scope` | `params.chartType ∈ {bar, pictogram, freq-table, line-graph}` (`single_event_probability` uses the **`frequency-table`** representation — its bag/category table); a **deferred** type (pie/scatter/histogram/stem-leaf/box-plot) fails — deferrals are never silently emitted. |
| `no-irrational-statistic` | the canonical answer value is a finite reduced `{num, den}` (or integer); standard deviation / density / regression can never appear. |
| `dataset-realises-chart` | the chart recomputed from `params.dataset` matches `media[0].svg` **byte-for-byte** — covering **only** bar tops, pictogram glyph counts (+ the exact partial-glyph clip width), line-graph lattice points, and table cells. **No pie-sector or scatter branch exists** (those types are absent from every dispatch table — §6.2). |
| `data-table-matches-dataset` | `media[].dataTableFallback` lists exactly the dataset categories+frequencies / value list — same integers, same order — so the fallback is information-equivalent. (`dataTableFallback` is a generic `{type:"object"}` in the schema, line 316; **no schema change required**.) |
| `uniform-count-scale` | one integer `Uy` governs every bar/point on the count axis (independent of the category pitch); a deterministic count-axis step from {1,2,5,10} is pinned; the baseline is the projection of count `0`. |
| `uniform-category-pitch` | category / ordered-x columns are evenly spaced by one integer pitch `Px`. |
| `pictogram-key-present` · `pictogram-partial-exact` | a pictogram emits its "1 symbol represents `pictogramKey` items" key; any partial symbol is an **exact half** of a full symbol (keys 2/10 only; no float width, no quarter/arbitrary fraction). |
| `bar-pattern-distinct` | bar fills differ by **inline greyscale hatch geometry** (the `cx-bar-hatch` strokes), not colour alone (the bar analogue of `no-colour-only-information`); the check inspects the inline hatch elements, never a pattern id. |
| `table-blank-cell-empty` | for `complete_frequency_table`, the blanked cell is empty in **both** the figure and the data-table. |
| `no-statistic-in-svg` | the student figure carries no element whose **render role** is the computed statistic / answer (a dedicated mean/median/mode/range/probability/answer annotation, a solution overlay, or correct-option styling). This is a **semantic role + render-intent** check (§6.8, §L), **not** a raw `<text>`-equals-answer string test: raw data, axis ticks, category labels, the pictogram key (`"1 symbol represents 5 items"`), and unit text that coincidentally match the answer are NOT leakage. Replaces the inherited `no-answer-label-in-svg` `,`/`/`/`=` character blocklist. |

> **Answer-type checkers, no schema change.** The new checkers map to existing answer.type enum members: `checkTableCompletion → table-completion` (enum line 202), `checkUnorderedSet → set` (enum line 198) — both already in the schema. **No answer.type enum edit is required** for any v1.0.0 task (mirroring the no-schema-change posture stated for the other answer types). There is **no `list` answer type** in the schema; no v1.0.0 task needs one (reads/probability use `integer`/`fraction`, line graph reads use `integer`).

---

## 7. Reuse of the approved Cartesian substrate via an additive visual-style extension

This family **reuses the approved coordinate-lines v1.0.2 visual contract through a versioned ADDITIVE shared extension** — `core/visual-style/data-chart-theme/` and `core/render/data-charts/` — and **does NOT alter the coordinate-lines visual contract in place** and **does not introduce a parallel renderer or a parallel theme.** The extension REUSES the `cx-figure` per-root isolation, the common axis/grid variables, `presentationSvg()`, `exportSvg()`, the premium/premium-dark/accessible/print modes, the 6000×4200 export, and the style-isolation tests; it ADDS statistics primitives (chart bars, category labels, pictogram symbols, bar hatches, legends, data-point labels). **coordinate-lines output stays byte-for-byte unchanged.** After approval the extension may become approved reusable cross-domain infra. The projection/clipping discipline below is the coordinate-lines integer-`gridRound` discipline; the **axis scaling is statistical (independent x/y scales), NOT the coordinate-geometry equal x/y pixel scale** (§6.7, §J).

### 7.1 Reused projection + independent-scale viewport (statistical axes)

The statistics renderer reuses the coordinate-lines integer projection and clipping primitives unchanged, but selects the renderer's **independent-scale viewport mode** (each axis faithful to its own declared scale, NOT equal px/unit — §J):

- **Data window from the dataset (integers only).** For a line graph the window is built from the integer lattice points `(i, value)` **plus the baseline/origin**, padded by the inherited integer margin `DATA_MARGIN_UNITS = 1`, so `min`/`max` agree byte-for-byte Py/TS. For a bar chart / pictogram the **count-axis** window is `[0, max(frequencies) + 1]` (the baseline `0` is always included), and the **category axis** spans the `len(categories)` equal slots; both bounds are integers, guaranteeing integer ticks and integer-unit gridlines.
- **Independent axis scales and integer centering offsets.** The x and y axes use **independent** integer scales because they measure different quantities: the **count / value axis** uses one integer `Uy` px per count unit (with a deterministic count-axis step pinned from `{1,2,5,10}`); the **category / ordered-x axis** uses one integer column pitch `Px`. Each axis is internally linear and uniformly scaled; the centering half-slack is kept as an exact `Rational` and **never pre-rounded** (`offX`, `offY`). This is the renderer's independent-scale mode — **not** the equal-`U`-on-both-axes mode coordinate geometry uses.
- **The single projection of record.** `projX`/`projY` — one exact `Rational` sum (`offset + Rational(value − min)·scale`) rounded **exactly once** by `gridRound(num, den)` (round-half-up; Python `Fraction`, TS `Rational`/BigInt produce the identical byte stream). **No second rounding, no float, no trig.** The rendered model preserves every data value exactly. Bars project their top via this projection; pictogram symbol rows project their baselines via it; line-graph points and the clipped polyline project via it. One deterministic `gridRound` projection is what keeps the statistics figures byte-identical Py↔TS under the golden + 150×2 parity fixtures and the `SPI_SWEEP = 10000` sweep, and lets `axis-scale-consistency` validate that ticks/gridlines/bars/points all agree.
- **Clipping.** Line-graph segments reuse the exact-rational clip (`clipLine` / Liang–Barsky over `Rational`); a clip collapsing to a point is rejected and the seeded param loop redraws (deterministic), so a zero-length segment can never be emitted. Bars and symbols are constructed entirely inside the window, so they need no clipping; the `within-canvas` clearance check (reused) still asserts every bar top, symbol, hatch stroke, and label box lies inside the `PAD`-inset box `[PAD, VIEW_W−PAD] × [PAD, VIEW_H−PAD]`.

The pinned canvas constants are inherited unchanged: `VIEW_W = 1000`, `VIEW_H = 700`, `PAD = 40`, `DATA_MARGIN_UNITS = 1`, `MAX_LABELS_PER_AXIS = 11`. With the committed dataset bounds (`MAX_CATEGORIES`, `MAX_LIST_LEN`, and a committed `frequencies` ceiling), each axis scale clears its minimum-legible-step floor for every admissible dataset, so the sweep never throws on scale.

### 7.2 The additive `data-chart-theme` extension (reuses the v1.0.2 contract; does NOT alter it in place)

Presentation, theming, and export are delegated to a **versioned ADDITIVE shared extension `core/visual-style/data-chart-theme/`** that **REUSES** the approved coordinate-lines v1.0.2 per-SVG style-isolation + export contract — the `cx-figure` per-root isolation, the common axis/grid variables, the `premium`/`premium-dark`/`accessible`/`print` modes, `presentationSvg()`, `exportSvg()`, the 6000×4200 export, and `resolveCommonCss` — and **ADDS** the statistics presentation primitives (chart bars, category labels, pictogram symbols, bar hatches, legends, data-point labels). **The approved coordinate-lines v1.0.2 visual contract is NOT altered in place, and coordinate-lines output stays byte-for-byte unchanged.** The canonical figure is **un-themed** (§6 banner); the theme layer is presentation-only. After approval the extension may become approved reusable cross-domain infra.

- **The canonical figure carries NO `cx-figure`.** The authoritative `media[0].svg` is byte-identical in shape to the coordinate-lines `figure()` output: an `<svg viewBox="0 0 1000 700" role="img" aria-label="…">` with an internal **un-scoped monochrome `<style>`** and **no `class` attribute**. This is also the **canonical (un-themed) accessibility-envelope form** the axe-core gate exercises. `class="cx-figure"` + the per-root `--cx-*` custom properties are added **only** by `presentationSvg()` (in-document) and `exportSvg()` (self-contained) — never by the generator, never into the stored item.
- **Per-root CSS custom properties + one common ruleset (reused).** At presentation/export time each figure becomes a root SVG carrying class **`cx-figure`** and its **own** per-root CSS custom properties read by the common ruleset. Because custom properties cascade only into their own subtree, every figure is isolated — several modes on one page, reordered cards, multiple questions per worksheet, and SVGs from coordinate-lines or any other family never interfere. This is the v1.0.2 per-root isolation, **reused from coordinate-lines, not re-implemented or modified.**
- **The additive statistics theme lives in the extension, NOT in the coordinate-lines contract.** The statistics series classes (`.cx-bar`, `.cx-bar-hatch`, `.cx-cat`, `.cx-icon`, legend/data-point-label classes) and their variables (`--cx-bar-fill`, `--cx-bar-hatch`, `--cx-cat`, `--cx-icon`, all lowercase-hyphen so `resolveCommonCss`'s `var(--cx-[a-z-]+)` regex matches) are defined in the **`data-chart-theme` extension's own variable/ruleset additions**, layered onto the reused common ruleset under the same `.cx-figure` per-root scope. Each new variable carries a value in **all four** mode objects (`print` canonical greys; CVD-safe `accessible`; `premium` / `premium-dark` restyle hue but each remains legible without colour). The coordinate-lines `cartesian-theme.{json,ts}` files, their `STYLE`/`GREYS` constants, and their byte output are **untouched** — the statistics canonical short-hex `STYLE` for bars/hatches/symbols lives in the **`core/render/data-charts/` extension module** (mirrored byte-identically in the Python oracle), so `dataset-realises-chart` parity holds without editing any coordinate-lines source. The statistics canonical figure confines its fills/strokes to greys already valid for the reused contract, so no shared `GREYS` set is mutated.
- **The four modes are reused unchanged** from the v1.0.2 contract: `print` (monochrome authoritative), `premium`, `premium-dark`, and `accessible` (CVD-safe). The canonical student/print default is **accessible + monochrome-safe**; the inline bar hatch, the pictogram symbol shape, the category label, and the legend are the **non-colour channels** that survive `print` and CVD, so colour never carries meaning alone (a bar's identity is its category label + hatch, not its hue).
- **`presentationSvg(svg, mode)` vs `exportSvg(svg, mode, w, h)`** are reused verbatim: `presentationSvg` strips the canonical internal monochrome `<style>` and stamps the mode's variables on the `cx-figure` root for in-document display; `exportSvg` produces a **fully self-contained** clone with the mode's concrete colours baked into an internal `<style>` via `resolveCommonCss(mode)`. The canonical `media[0].svg` is **never mutated** — so switching modes never changes the stored item or its `contentHash`.

> **Py/TS byte-parity scope.** Byte-identical Py↔TS parity is required on the **canonical `media[0].svg`** and on `params`/`answer`/`distractors` only. The `presentationSvg`/`exportSvg`/render-mode/6000×4200 theme layer is a **TypeScript-only presentation concern** (the `data-chart-theme` TS extension reuses `cartesian-theme.ts`, which exists only in TS; there is no Python theme mirror, and theming output is never serialised into the item). The build writes the **Python oracle first for the canonical SVG**, and the browser-verification + style-isolation evidence is generated from the TS theme. **No Python theme mirror is claimed or required.**

### 7.3 Materialised self-contained 6000×4200 export (reused)

The high-resolution PNG/SVG export reuses the coordinate-lines materialised export contract unchanged. The **max device envelope `7680×4320` is an inherited coordinate-lines constant**, not re-chosen here (verified in `coordinate-lines.ts` line 507–508, `exportEnvelope`: `maxEnvelope = "7680x4320"`, `scale = min(floor(7680/VIEW_W), floor(4320/VIEW_H))`). For the committed `viewBox 0 0 1000 700` this gives integer device scale `S = min(floor(7680/1000), floor(4320/700)) = min(7, 6) = 6`, a **`6000×4200`** export (the `4320` height is the binding constraint), reused **verbatim, not recomputed**. `exportSvg(svg, mode, 6000, 4200)` materialises the export **inside the cloned SVG** — the mode's resolved colours and the explicit `width="6000" height="4200"` are baked into the clone, so the export is self-contained and rasteriser-independent. Every canonical integer coordinate `v` maps to device pixel `S·v` exactly, and `(S·v)/S = v` recovers it (the exact-integer `png-coordinate-preservation` identity), because `S` is integer and the map is `S·v` — no float multiply, no tolerance. The PNG is regenerable and **never stored in the item** (so it is excluded from `contentHash` because it is never serialised, not by carve-out); `media[0].svg` — the canonical monochrome figure — remains the single authoritative deliverable that the offline HTML exporters inline and the axe-core a11y gate exercises.

### 7.4 What this reuse buys, and what it forbids

By reusing the coordinate-lines projection/viewport and the `cartesian-theme` contract rather than reinventing them, the statistics family inherits, under the same gates: byte-identical Py/TS **canonical** SVG (golden 4-seed + 150×2 parity + `SPI_SWEEP = 10000` + reproducibility), the per-root style isolation that makes multi-figure worksheets safe, the four approved render modes (additively extended for bars/categories/icons), the materialised 6000×4200 export, and the answer-recomputation / closure-agreement discipline. The reuse **forbids**, by construction: any second projection formula, any float or `sin/cos` in emitted geometry, any second theme or unscoped global CSS, any `<pattern>`/`url(#…)` in the canonical SVG (hatch is inline integer strokes — §6.6), any colour-only distinction (every bar/series/icon also differs by hatch/label/marker, and every canonical colour is in the extended `GREYS`), and any deferred chart type (pie/scatter/histogram/stem-and-leaf) leaking into a render — each is absent from every dispatch table and deterministically rejected by §6.2 and the `chart-type-in-scope` check.


---

## 8. Misconception registry (`MISC.STAT.*`, approved in principle)

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

Per the seed scope this is a **reading/interpretation** family. It emits **six** schema-valid axes — `numericalComplexity`, `readingDemand`, `interpretationDemand`, `reasoningSteps`, `informationDensity`, and `scaffolding` — and leaves the rest schema-absent (the generator emits only the axes it sets):

| Axis (closed schema enum) | What it measures here |
| --- | --- |
| `numericalComplexity` | Magnitude/denominators of the values and answer (larger counts, non-trivial denominators in a probability or mean). |
| `readingDemand` | Decoding the representation: a bare table < bar chart < pictogram-with-key < line graph. |
| `interpretationDemand` | Turning a read value into a statistic in context (read = low; weighting and dividing = high). |
| `reasoningSteps` | Number of distinct reasoning steps (single read = 1; mean-from-frequency-table = read, weight, sum, divide). **Driven by the genuine step count only — scaffolding is NOT simulated through this axis.** |
| `informationDensity` | Number of categories / data values the student must track at once. |
| `scaffolding` | Whether the item supplies scaffolding (worked structure / partial setup). Carried on its **own** `scaffolding` axis — **not folded into `reasoningSteps`** (§M). |

All six are members of `question-item.schema.json#/$defs/difficultyProfile.axes` (verified present: `numericalComplexity`, `readingDemand`, `interpretationDemand`, `reasoningSteps`, `informationDensity`, `scaffolding`); **no invented axis names**. The other axes are deliberately **schema-absent** (not emitted). **Scaffolding uses the dedicated `scaffolding` axis** (a scaffolded item lowers the weighted score via that axis); `reasoningSteps` reflects the true step count only. Ranges/weights are **provisional until the 10,000-seed distribution report** confirms every declared band is reachable.

### 9.2 Scoring function

The generator's `difficulty(task, params)` follows the `coordinate-lines` shape exactly:

1. Per-task base tables `RD_BASE[task]`, `ID_BASE[task]`, `RS_BASE[task]` give the representation-/interpretation-driven components; `numericalComplexity` and `informationDensity` are computed from the **realised seeded data** (so they are monotonic in the values actually drawn), not from a table.
2. Weighted sum (weights sum to **1.00**, emphasising reasoning/interpretation over raw number size, consistent with `DIFFICULTY_MODEL.md` §2 which states `numericalComplexity` is intentionally not dominant):

```
score = 0.15*numericalComplexity
      + 0.20*readingDemand
      + 0.25*interpretationDemand
      + 0.20*reasoningSteps
      + 0.15*informationDensity
      - 0.10*scaffolding                     // dedicated scaffolding axis, NOT folded into reasoningSteps
band  = bandFromScore(score)                 // shared function, no override
band  = clamp(band, objective.difficultyRange.min, objective.difficultyRange.max)
```
(Weights are provisional pending the 10,000-seed distribution report; the `scaffolding` term lowers the score when scaffolding is supplied, on its own axis.)

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
- Turning scaffolding on never raises the band (the `-0.10` weight on the **dedicated `scaffolding` axis**, not a `reasoningSteps` adjustment).

A second test `bands-within-objective-range` asserts every generated item's `overallBand` lies inside its objective's `difficultyRange`, across all seeds. The median row's `answer.type` is set from the **computed denominator** (`den=1 ⇒ integer`, `den=2 ⇒ exact-rational`), so the difficulty/answer-type pairing never mislabels an integer median; the §11.4 `answer-type-consistency` check (which asserts `integer ⇔ den=1`) therefore passes.

## 10. Edge-case and degeneracy policy

Every rule here is a **deterministic pre-acceptance gate** evaluated from the seeded dataset before the item is realised. A seed that fails any gate triggers the platform's deterministic redraw (re-seed forward by the documented step), never a silent mutation of data; this preserves byte-identical Python/TS behaviour and the 10,000-seed reproducibility guarantee. Each gate is also a named validator check so a stored item can be re-audited. **Every "distractor ≠ key" or "distractor distinct" decision is an exact-Rational comparison on reduced `{num,den}` (§8.1), never a display-string comparison.**

### 10.1 Empty and degenerate datasets — excluded

- **Non-empty.** The data list / frequency table must have `dataCount ≥ DATA_MIN_task` (lists: `n ≥ 3`; frequency tables: `≥3` categories with total frequency `Σf ≥ 5`). Empty or single-value datasets are redrawn. Validator check: `dataset-nonempty`.
- **Uniform lists are admitted for range and median (§H).** `max > min` is **NOT** required universally. For `range_from_list`, **`range = 0` (a uniform list) is a VALID low-band free-response case**, admitted at a controlled low frequency; MC may be ineligible at `range = 0` (3 distinct distractors impossible) and the item falls back to FR. For `median_from_list`, uniform lists are **not excluded** (the median is well-defined), also at a controlled low frequency. Validator check: `uniform-list-admitted-controlled-frequency` (records, not forbids, the uniform case). Only `mode_from_list` excludes uniform/all-equal lists (a unique mode is required).
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
> | `read_bar_chart` | `SPI.MIDDLE.STAT.READ.BAR_CHART.01` | `integer` | `free-response` \| `multiple-choice` |
> | `read_pictogram` | `SPI.MIDDLE.STAT.READ.PICTOGRAM.01` | `integer` | `free-response` \| `multiple-choice` |
> | `read_table_value` | `SPI.MIDDLE.STAT.READ.TABLE_VALUE.01` | `integer` | `free-response` \| `multiple-choice` |
> | `read_line_graph` | `SPI.MIDDLE.STAT.READ.LINE_GRAPH.01` | `integer` | `free-response` \| `multiple-choice` |
> | `complete_frequency_table` | `SPI.MIDDLE.STAT.FREQ.COMPLETE_TABLE.01` | `table-completion` | **`free-response`** (only) |
> | `mean_from_list` | `SPI.MIDDLE.STAT.AVG.MEAN_LIST.01` | `integer` \| `exact-rational` | `free-response` \| `multiple-choice` |
> | `mean_from_freq_table` | `SPI.MIDDLE.STAT.AVG.MEAN_FREQ_TABLE.01` | `integer` \| `exact-rational` | `free-response` \| `multiple-choice` |
> | `median_from_list` | `SPI.MIDDLE.STAT.AVG.MEDIAN_LIST.01` | `integer` \| `exact-rational` | `free-response` \| `multiple-choice` |
> | `mode_from_list` | `SPI.MIDDLE.STAT.AVG.MODE_LIST.01` | `integer` | `free-response` \| `multiple-choice` |
> | `range_from_list` | `SPI.MIDDLE.STAT.AVG.RANGE_LIST.01` | `integer` | `free-response` \| `multiple-choice` |
> | `single_event_probability` | `SPI.MIDDLE.STAT.PROB.SINGLE_EVENT.01` | `fraction` | `free-response` \| `multiple-choice` (proper P only) |
>
> **`interactionType` is from the schema enum only** (`question-item.schema.json` ⇒ `free-response`, `multiple-choice`, `multiple-select`, `matching`, `ordering`, `classification`). `complete_frequency_table` is **`free-response` only** with `answer.type:"table-completion"` (exactly one missing frequency or one missing total per item). **`table-completion` is NOT an `interactionType`** — it is an `answer.type` value only. No schema change is requested for any item field: `table-completion` and `fraction` are already members of the `answer.type` enum, and `dataTableFallback` is already typed `{type:"object"}` (free-form) — **no `answer.type` enum edit and no schema change are required for this family.** (`set` is not used in v1.0.0; the multimodal/set-valued mode is deferred.)

### 11.1 The deterministic dataset is the single source of truth

Every `gen.stats.data-handling` item is generated from one seeded artefact, the **dataset record**, materialised once in `params.dataset` and never recomputed downstream. The field schema below is the **single canonical `DataSet` vocabulary**; §4.2/§6.1 reference these exact names and types (`kind` discriminator, `frequencies`, `values`, `pictogramKey`):

```
params.dataset = {
  kind: "frequency" | "list",        // exactly two discriminator values
  categories?: string[],             // "frequency" kind: bar / pictogram / table x-labels, display order
  frequencies?: integer[],           // "frequency" kind: parallel to categories; counts ARE integers >= 0
  values?: integer[],                // "list" kind: raw data list for mean/median/mode/range (no stored sorted copy)
  seriesLabels?: string[],           // "list" kind used as an ORDERED line graph: x-axis labels parallel to values
  pictogramKey?: integer             // pictogram key: items represented by ONE complete symbol; in {2,5,10}
}
params.task = <one of the eleven literals above>
// single_event_probability additionally carries outcomeSpace {favourable,total,targetCategoryIndex}, derived from a frequency dataset
```

A **line graph** is a `list` dataset carrying non-null `seriesLabels` (ordered x-values only); a **frequency table** is a `frequency` dataset. There is **one** `kind` vocabulary (`"frequency" | "list"`) used identically by the generator and by the validator's `params-in-domain` check. The chart SVG, the prompt blocks, the `answer`, the `solution.steps`, the distractors, and the accessibility `dataTableFallback` are all **pure functions of `params.dataset` plus `params.task`**. The solver never reads the chart back; the chart never carries a value the dataset does not. This is what makes every validator check below a closed-loop recomputation rather than a heuristic.

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
- **Median / range:** **`max > min` is NOT required universally (§H).** `range = 0` (a uniform list) is a **valid low-band free-response case** for `range_from_list`, and uniform lists are **not excluded** for `median_from_list` — both admitted at a controlled low frequency. MC may be ineligible at `range = 0` (and the item falls back to FR). Only `mode_from_list` excludes uniform/all-equal lists. This pins the §4.5/§10.1 interaction.
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
| `no-answer-label-in-svg` | **REPLACED** by the semantic role-based `no-statistic-in-svg` + the §6.8/§L leakage checks (`no-derived-statistic-annotation`, `no-answer-role-in-student-render`, `no-solution-overlay-in-student-render`, `raw-data-equality-is-not-leakage`, `student-a11y-does-not-state-result`, `answer-overlay-present-only-in-solution-mode`). The inherited `,`/`/`/`=` **character blocklist must NOT transfer** — a pictogram key text `"1 symbol represents 5 items"`, category labels (`"km/h"`, `"Year 7, boys"`), and a list that coincidentally contains its own answer are all legitimate. Leakage is judged by **element role + render intent**, not by raw text equality. |
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
| `chart-realises-data` | the **geometric** realisation matches the dataset exactly, decoded back out of the SVG: each **bar** top y-coordinate `= gridRound(project(frequency))` for its category; each **pictogram** row's symbol count `= frequency / pictogramKey` (whole symbols plus at most one exact half-symbol clip width, keys 2/10 only); each **line-graph** plotted point `= gridRound(project(index, value))` on the integer lattice. **Pie and scatter branches are absent** — those types are deferred and unreachable, so the validator carries no pie-sector / scatter-point recomputation (their realisation lives only in the deferred-version note) |
| `category-label-correctness` | the ordered `<text class="cx-cat">…` category labels equal `dataset.categories` (or `seriesLabels`) **in order**; separately, the `<text class="cx-ticklbl">…` count-axis labels are integers in ascending order matching the chosen scale. Category strings appear **only** under `cx-cat`; no `cx-ticklbl` text is non-numeric |
| `axis-scale-consistency` | one declared integer units-per-pixel scale reproduces every gridline and every datum (the bar/line analogue of coordinate-lines `equal-axis-scale`) |
| `media-to-scale` | `media[0].toScale === true` for **bar / line** charts; **not asserted for pictograms** (see inherit table), which instead pass `pictogram-key-exact` |
| `pictogram-key-exact` | `pictogramKey` resolves each plotted frequency into whole symbols + at most one exact half-symbol (keys 2/10 only) with no rounding drift; the integer-coordinate half-symbol clip width is exact |

#### No-statistic-leakage — SEMANTIC checks (replaces `no-answer-label-in-svg`; §L)

Leakage is judged by **element role + render intent**, NOT raw text equality: raw data, axis ticks, category labels, the pictogram key, and unit text that **coincidentally** equal the answer are not leakage; only a dedicated answer/statistic-role element, a solution overlay, or correct-option styling is.

| Check name | Asserts |
|---|---|
| `no-derived-statistic-annotation` | for **derived-answer** tasks (mean/median/mode/range/probability), the student figure carries no dedicated mean/median/mode/range/probability/answer annotation |
| `no-answer-role-in-student-render` | no element in the student figure carries an answer/result render role |
| `no-solution-overlay-in-student-render` | no solution overlay appears in the student figure |
| `raw-data-equality-is-not-leakage` | a list value or axis tick that coincidentally equals the answer is **explicitly allowed** (no false reject) — a list may legitimately contain its own mean/median/mode/range/numerator/denominator |
| `student-a11y-does-not-state-result` | the student-facing accessibility text / `spokenMath` describes raw data only and **never states the computed result** |
| `answer-overlay-present-only-in-solution-mode` | any answer/solution overlay exists only in the answer-key/solution channel, never in student media; no correct-option styling in student media |
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

**Concrete `data-chart-theme` extension diff (additive; coordinate-lines source untouched, so `svg-realises-data` parity and `no-colour-only-information` both hold):**

1. **New variables** declared in the **`data-chart-theme` extension** (NOT in `cartesian-theme.json`): `--cx-bar-fill`, `--cx-bar-hatch`, `--cx-cat`, `--cx-icon` (all lowercase-and-hyphen, satisfying `resolveCommonCss`'s `var(--cx-[a-z-]+)` regex).
2. **Per-mode values for ALL FOUR modes** (`print`, `premium`, `premium-dark`, `accessible`) in the extension: `print` uses the canonical greys (`--cx-bar-fill:#bbb`, `--cx-bar-hatch:#555`, `--cx-cat:#333`, `--cx-icon:#444`); `premium`/`premium-dark`/`accessible` restyle hue but each remains legible without colour (the redundant channel is geometric, see §12.3).
3. **The extension's common ruleset additions**, layered under the reused `.cx-figure` per-root scope: `.cx-figure .cx-bar{fill:var(--cx-bar-fill);stroke:var(--cx-cat);stroke-width:2}.cx-figure .cx-cat{font-size:20px;fill:var(--cx-cat)}.cx-figure .cx-icon{fill:var(--cx-icon)}` (hatch strokes read `--cx-bar-hatch`).
4. **The canonical short-hex `STYLE` fragment lives in the `core/render/data-charts/` extension module** (TS) and its Python mirror, kept **byte-identical** across languages: `.cx-bar{fill:#bbb;stroke:#333;stroke-width:2}.cx-bar-hatch{stroke:#555;stroke-width:1.5}.cx-cat{font-size:20px;fill:#333}.cx-icon{fill:#444}`. **The coordinate-lines `STYLE` constant is NOT edited.**
5. **No shared `GREYS` set is mutated.** The canonical statistics figure confines its bar fill / hatch stroke / icon / category text to greys already valid in the reused contract (`#bbb`/`#555`/`#444`/`#333`/`#111`), so `no-colour-only-information` passes with **no grey added and no coordinate-lines source edited** — coordinate-lines output stays byte-for-byte unchanged.

### 11.5 Sweep and parity obligations

The validator runs inside the standard harness: **golden (4 seeds)**, **parity 150×2** (Python ⇄ TypeScript — the **canonical item + chart SVG byte-equal AND the semantic frequency-table deterministic-HTML serialisation round-trip equal**, and the validator `status`/failing-names equal; the TS-only theme layer is excluded from byte-parity per §11.3). **Table validation is independent from chart-SVG validation (§F):** charts are gated by canonical SVG byte-parity, tables by deterministic HTML-table parity (serialisation + exact round-trip from the canonical dataset). Plus **`SPI_SWEEP=10000`** with full reproducibility and a distribution report, and a **blocking artifact-integrity test + SHA-256** over the immutable approved-generator fixtures. The distribution report includes a **per-task band-reachability proof** — every band declared in each objective's `difficultyRange` must be reached by some seed given the bounded dataset sizes; **every declared band must be reachable before fixtures freeze**, and an unreachable declared band **fails** the sweep gate. The median-MC `AVERAGES_ENDS` drop/backfill rate is reported as a redraw anomaly, not a silent loss. Any `status:"fail"` in the sweep, any byte divergence in `svg-realises-data` or HTML-table parity, or any closure disagreement aborts the build. **The approved arithmetic / geometric / linear / angle-geometry / coordinate-lines generators keep their output byte-for-byte unchanged.**

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
  spokenMath:  <the PROMPT spoken, raw data only, NEVER the computed result, e.g. "Find the mean of three, five, eight and four">,
  altText:     <one-line chart summary, == media[0].altText>,
  longDescription: <== media[0].longDescription, == <desc>>,
  nonColorIndicators: true
}
media[0]: { …, toScale, altText, longDescription, dataTableFallback }
```

**`dataTableFallback` — the exact dataset, information-equivalent to the chart.** It is a structured table rendered from `params.dataset` (free-form `{type:"object"}`, no schema change): for `frequency` datasets (bar / pictogram / table), the (category, frequency) rows plus the total and any pictogram key ("1 symbol represents `pictogramKey` items", stated WITHOUT giving the answer); for `list` datasets, the values; for a line graph (`list` + `seriesLabels`), the (label, value) pairs; for `complete_frequency_table` the full table **with the blanks left blank in the prompt fallback** (the completed answer table appears only in the solution export). The validator's **`chart-realises-data`** and a dedicated **`datatable-matches-dataset`** check assert the fallback reproduces `params.dataset` cell-for-cell — so the table is provably the chart's information twin.

### 12.3 No colour-only information, across ALL render modes

Colour never carries meaning alone; every colour-coded element is **paired** with a redundant non-colour channel that lives in the **canonical geometry**, so it survives all four modes unchanged:

- **bars:** the category **label** under each bar (class `cx-cat`) and, when bars must be told apart without axis position, an **id-free greyscale hatch** — drawn as **inline integer-coordinate `<line>`/`<path>` stroke elements** (class `cx-bar-hatch`) clipped to the bar rect in the deterministic element order, **never** an SVG `<pattern>` + `fill=url(#id)` (which §6.6's no-`id`/no-`url(#…)` rule forbids). `bar-pattern-distinct` checks these inline hatch elements;
- **pictograms:** a printed **glyph key** and counted glyphs (count, not colour, conveys magnitude);
- **line graphs:** distinct **point markers** + direct labels and **dashed vs solid stroke patterns**, not hue.

The canonical SVG is **greyscale-authoritative**; the four reused render modes (`premium`, `premium-dark`, **`accessible` = CVD-safe Okabe–Ito-style palette**, `print` = monochrome) only restyle via per-root CSS variables and **must each remain legible without colour**. The validator enforces this at two levels: `no-colour-only-information` (canonical figure fill/stroke colours ∈ the **existing shared grey set `{#111,#333,#444,#555,#888,#bbb,#fff}`** — no grey is added and no coordinate-lines source is edited, §6.5/§11.4) and `nonColorIndicators === true`; the redundant channel (label / marker / hatch / legend) is checked structurally. Pie and scatter are deferred, so no pie/scatter colour-coding exists to reconcile.

### 12.4 No answer in the accessibility text

For derived-answer tasks, the `<desc>`, `altText`, `longDescription`, `dataTableFallback`, **and the student-facing `spokenMath`** describe the **data**, never the result (§L) — enforced by `student-a11y-does-not-state-result`. **There is no answer-speaking text in the student-facing `spokenMath` field; answer/solution narration lives only in the answer-key/solution channels.** A screen-reader user therefore solves the same problem a sighted user does, with the worked result narrated only in the solution export. For direct `read_*` tasks the queried value is legible in both the chart and the data-table (`read-task-value-present`).

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
| `read_bar_chart` | `SPI.MIDDLE.STAT.READ.BAR_CHART.01` | vertical bar chart | `integer` | `free-response` / `multiple-choice` | 1–2 |
| `read_pictogram` | `SPI.MIDDLE.STAT.READ.PICTOGRAM.01` | pictogram (integer key in {2,5,10}) | `integer` | `free-response` / `multiple-choice` | 1–2 |
| `read_table_value` | `SPI.MIDDLE.STAT.READ.TABLE_VALUE.01` | frequency table | `integer` | `free-response` / `multiple-choice` | 1–2 |
| `complete_frequency_table` | `SPI.MIDDLE.STAT.FREQ.COMPLETE_TABLE.01` | frequency table | `table-completion` | **`free-response` only** | 2–3 |
| `read_line_graph` | `SPI.MIDDLE.STAT.READ.LINE_GRAPH.01` | line graph (ordered x; Cartesian reuse) | `integer` | `free-response` / `multiple-choice` | 1–3 |
| `mean_from_list` | `SPI.MIDDLE.STAT.AVG.MEAN_LIST.01` | numerical data list | `integer` \| `exact-rational` | `free-response` / `multiple-choice` | 2–4 |
| `median_from_list` | `SPI.MIDDLE.STAT.AVG.MEDIAN_LIST.01` | numerical data list | **`integer` \| `exact-rational`** | `free-response` / `multiple-choice` | 2–3 |
| `mode_from_list` | `SPI.MIDDLE.STAT.AVG.MODE_LIST.01` | numerical data list | `integer` (unique mode) | `free-response` / `multiple-choice` | 1–2 |
| `range_from_list` | `SPI.MIDDLE.STAT.AVG.RANGE_LIST.01` | numerical data list | `integer` | `free-response` / `multiple-choice` | 1–2 |
| `mean_from_freq_table` | `SPI.MIDDLE.STAT.AVG.MEAN_FREQ_TABLE.01` | frequency table | `integer` \| `exact-rational` | `free-response` / `multiple-choice` | 3–4 |
| `single_event_probability` | `SPI.MIDDLE.STAT.PROB.SINGLE_EVENT.01` | bag/category frequency table | `fraction` | `free-response` / `multiple-choice` (proper P only) | 2–3 |

**`interactionType` is always a valid schema enum member.** The item schema's `interactionType` enum is exactly `["free-response","multiple-choice","multiple-select","matching","ordering","classification"]` — `table-completion` is **not** in it. `complete_frequency_table` therefore carries `interactionType: "free-response"` with `answer.type: "table-completion"`, and is **FREE-RESPONSE ONLY** — each item has exactly one missing frequency or one missing total (no underdetermined multi-blank), and no MC variant is offered. No item ever carries `interactionType: "table-completion"`, so none is rejected by the precompiled Ajv validator at the storage/import/export boundary. This proposal requests **no `interactionType` schema change**.

**`answer.type` for median is computed, never pinned.** `median_from_list` stores `integer` when the even-n average has `den = 1` (same-parity middles) and `exact-rational` when `den = 2` (half-integer); the median solver sets the stored type from the computed `den` so the inherited `answer-type-consistency` check (`integer ⇔ den = 1`) passes. The coverage matrix above lists `integer | exact-rational` for this reason and never pins median to `exact-rational`.

**`answer.type` for mode is single-value `integer` only in v1.0.0.** The `set`/multimodal and no-mode encodings are **deferred** with the multimodal sub-objective; the §10.2 mode-unique redraw gate (`maxFreq >= secondFreq + 1`) excludes all-distinct and multimodal lists, so `checkUnorderedSet`/the `set` answer type are not exercised by any v1.0.0 mode task. No empty-set / all-values "no mode" convention is emitted in v1.0.0. (`checkUnorderedSet → set` and `checkTableCompletion → table-completion` both target existing answer.type enum members — **no answer.type schema edit is required** for either, exactly as none is required for the others. No `list` answer type is introduced anywhere: `list` is not an enum member, and no task needs an ordered-list answer — line graph / probability use `integer` / `ordered-pair` / `fraction`.)

Each worked seed prints: prompt blocks (`prompt.blocks` typed content + `prompt.instruction`) with the chart cited via a `media-ref`/`table-ref` block; the figure (`![figure](stats_svgs/...)`) for chart-backed tasks; alt text and `longDescription`; the canonical answer with its computed `answer.type` and `display` (rationals as `{num,den}`); the **single source dataset** echoed as the `media[].dataTableFallback` accessibility table (the schema types `dataTableFallback` as a generic object, so the `{categories[],frequencies[]}` / `{values[]}` table is schema-valid **with no schema change**) so a reviewer sees the chart, the table, the prompt, the answer and the solution all derive from one seed; the worked `solution.steps` (with per-step `marks` and `estimatedTimeSeconds`); and a reproduce line `generate(<seed>, {'task': ..., 'interactionType': ...})`.

**One fully-worked schema-valid exemplar.** Because no approved family ships a spec without a concrete example, the pack's first section embeds **one fully-populated `question-item.schema.json` item per task family** (a read task, the `table-completion` task, a `mean_from_list`, a `median_from_list` half-integer case, a `mode_from_list`, and a `single_event_probability`) showing `prompt.blocks`, `answer.canonical` (`{num,den}` for rationals, the `{cells:[...]}` shape for `table-completion`, the `{num,den}` reduced fraction for probability), `distractors[]`, `solution.steps` with `marks`, `difficulty.axes`, `media[].svg` + `dataTableFallback`, `accessibility`, `provenance{origin:"generated",rightsStatus:"academy-owned"}`, and `lifecycle{state:"generated"}`. Each exemplar is asserted to pass the precompiled standalone validator in the integrity test of §13.6. Where the schema has explicit `allOf` constraints only for `integer`/`exact-rational`, the `table-completion` `{cells:[...]}` and probability `fraction` canonicals are stated to be **free-form canonical validated by their checker**, not by a schema `if/then` — no schema change is claimed for them.

**Required coverage (§O).** The pack covers all 11 objectives/tasks, every interaction, every realised band, every answer type, every misconception, every chart/table representation, and specifically: **vertical bar-chart scales 1/2/5/10**, **whole + half pictograms** (keys 2/5/10), **odd + even medians**, **integer + fractional means**, **a unique mode**, **range = 0 + positive ranges**, **negative list values at appropriate bands**, **P = 0 / 1 / 1-half / other** probabilities, **blank-vs-completed table**, the **premium / premium-dark / accessible / print** modes, **multiple charts in one document**, **dense-category stress tests**, and **6000×4200 colour + print exports**. Per item the pack records: objective ID, task, interaction, answer type, seed, parameters, canonical dataset, prompt, figure or semantic table, canonical answer, worked solution, misconception calculations, accessibility representation, difficulty axes + band, validation checks, and the exact reproduction command.

**Chart-type coverage.** v1.0.0 ships vertical bar chart, pictogram, frequency table (semantic HTML, §F), line graph. The pack carries a **"Deferred chart types and statistics"** section that names each excluded type and the deterministic exclusion: pie chart, scatter/correlation, regression/lines of best fit, histogram, stem-and-leaf, box plot, and the statistics standard deviation / variance / quartiles / IQR / grouped-data estimated means / set-valued mode are **never emitted** — `paramsInDomain` rejects their task ids, the registry exposes no task entry, and an integration test asserts these ids `generate`-throw and never appear in a 10k sweep, so exclusion is enforced, not implicit (the "deterministically excluded, never silently included" rule).

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
- `no-statistic-in-svg` (statistics-specific, **replaces** the inherited `no-answer-label-in-svg`) — predicate is **semantic role + render intent** (§6.8, §L), not raw text equality: the student figure carries no element whose render role is the computed statistic/answer (a dedicated mean/median/mode/range/probability annotation, a solution overlay, or correct-option styling). Raw data, axis ticks, category labels, axis-unit text (`km/h`, `Year 7, boys`), the pictogram key line (`1 symbol represents 5 items`), and **a list value that coincidentally equals the answer** are all permitted (`raw-data-equality-is-not-leakage`). It does **not** use the inherited character blocklist `','`,`'/'`,`'='`. Pinned tests: a pictogram with a key line **passes**; a list containing its own mean **passes**; a figure carrying a dedicated answer annotation **fails**.
- `frequency-table-blank-cell` (statistics-specific) — `complete_frequency_table` figures leave the asked cell empty.
- `pictogram-key-exact` (statistics-specific) — the rendered key value equals `dataset.pictogramKey` (items per one complete symbol).
- `tick-labels-integer`, `axes-stronger-than-grid` — **inherited verbatim** from the Cartesian renderer discipline, with the rider below. **`equal-axis-scale` is NOT inherited** (statistical axes use independent x/y scales, §J); it is **replaced by `axis-scale-consistency`** (each axis faithful to its own declared linear scale, one `gridRound` projection, ticks/gridlines/points agree).
- `category-label-correctness` — category strings are scraped from class **`cx-cat` only** and equal `dataset.categories`; the integer count-axis labels are scraped from class **`cx-ticklbl`**. No category string is ever emitted under `cx-ticklbl`, so the inherited `tick-labels-integer` check (which requires every `cx-ticklbl` `<text>` to match `^-?\d+$`) stays green; a check asserts no `cx-ticklbl` `<text>` is non-numeric and that category strings appear only under `cx-cat`.

**`media[].toScale` policy is stated once.** Bar charts and line graphs carry `media[0].toScale = true` and are governed by the inherited `media-to-scale` check; **pictograms carry `toScale: false`** (they are glyph-count figures, not height-to-scale) and are governed by `pictogram-key-exact` **instead** — so the family does **not** inherit the `media-to-scale` gate verbatim for pictograms. No "NOT TO SCALE" label is emitted.

### 13.4 Render modes + 6000×4200 export

Every pack figure and the visual-audit gallery use the **additive `core/visual-style/data-chart-theme/` extension** (§7.2, §K) — which REUSES the approved coordinate-lines v1.0.2 contract and does NOT alter it in place — with **no parallel theme**. The render-mode/presentation/export layer is a **TypeScript-only presentation concern** (no Python theme mirror exists or is added): byte-parity Py/TS applies to the **canonical `media[0].svg` and to `params`/`answer`/`distractors` only**, never to the themed or exported copies, which are not serialised into the item. The visual audit and browser-verification evidence are generated from the TS theme.

**The canonical figure does NOT carry `class="cx-figure"`.** Matching coordinate-lines exactly, the authoritative `media[0].svg` carries the internal **unscoped monochrome `<style>`** block and **no** `class="cx-figure"`; this is the accessibility-envelope (un-themed) canonical form on which `svg-realises-data` parity is asserted. `class="cx-figure"` plus the per-root `--cx-*` variables are stamped **only by `presentationSvg(svg, mode)`** (which strips the canonical `<style>`) and `exportSvg(svg, mode, w, h)` (which bakes a self-contained `<style>` via `resolveCommonCss`). The four modes — **premium**, **premium-dark**, **accessible** (CVD-safe), **print** (monochrome authoritative) — coexist on one page with zero cascade leakage because each figure root carries its own custom properties read by the one common `.cx-figure` ruleset; **colour never carries meaning alone** — every series is paired with a hatch/pattern, a printed category label, and (where shown) a legend, satisfying `nonColorIndicators`.

**Concrete additive `data-chart-theme` extension diff (coordinate-lines source untouched).** The new series classes are defined entirely in the extension; `resolveCommonCss`'s `var\((--cx-[a-z-]+)\)` regex constrains new names to lowercase-and-hyphen:
1. Declare new variables in the **extension** (NOT in `cartesian-theme.json`): `--cx-bar-fill`, `--cx-bar-hatch`, `--cx-cat`, `--cx-icon`.
2. Give all **four** mode objects a value for each new variable in the extension (print uses the canonical short-hex greys below; premium/premium-dark/accessible use mode-appropriate, CVD-safe ink that still pairs colour with hatch).
3. The extension's common-ruleset additions, under the reused `.cx-figure` scope: `.cx-figure .cx-bar{fill:var(--cx-bar-fill);stroke:var(--cx-cat);stroke-width:2}`, `.cx-figure .cx-cat{font-size:24px;fill:var(--cx-cat)}`, `.cx-figure .cx-icon{fill:var(--cx-icon)}` (the hatch stroke reads `--cx-bar-hatch`).
4. The canonical short-hex `STYLE` fragment lives in the **`core/render/data-charts/` extension module** (TS) and its **Python mirror**, kept **byte-identical**, so `svg-realises-data` parity holds. **The coordinate-lines `STYLE` constant is NOT edited.**
5. **No shared `GREYS` set is mutated** — the statistics figure confines itself to greys already in the reused contract (`{#111 #333 #444 #555 #888 #bbb #fff}`).

**Committed canonical greyscale palette** (aligned with §6.5; the authoritative monochrome figure): `.cx-bar` fill `#bbb`; bar hatch stroke `#555`; `.cx-cat` label `#333`; `.cx-icon` fill `#444`. All four are already members of the existing grey set, so no grey is added and no coordinate-lines source is edited; a pinned test asserts every `fill/stroke` hex in the canonical statistics SVG is a subset of that set.

**Id-free hatch.** Because the canonical-SVG rule forbids any `id` attribute and any `url(#…)` reference (the safe-multi-item-export invariant), bar hatching is drawn as **inline clipped stroke geometry** — a deterministic, integer-coordinate set of `<line>` elements emitted in fixed element order inside each bar rect — never an SVG `<pattern>` + `fill=url(#id)`. The `bar-pattern-distinct` check inspects those inline hatch elements, not a pattern id, and the no-`id`/no-`url(#)` invariant is re-asserted.

**Export.** The audit emits `presentationSvg()` display copies and `exportSvg()` self-contained copies, and materialises the **6000×4200 high-resolution PNG export inside the cloned SVG** for premium / accessible / print. The sizing is reused verbatim, not recomputed: `maxEnvelope = "7680x4320"` is the inherited coordinate-lines constant (`exportEnvelope` in `coordinate-lines.ts`), giving `S = min(⌊7680/1000⌋, ⌊4320/700⌋) = min(7,6) = 6` over `viewBox "0 0 1000 700"` → 6000×4200, exactly as the coordinate-lines manifest's `rasterExports` block.

### 13.5 Distribution report (≥10,000 seeds)

`stats_data_handling_distribution.json` mirrors `coordinate_lines_distribution.json`: top-level `generatorId`, `generatorVersion`, `sweep: 10000`, `invalid: 0`. Per task the report shows (§M): `count`, **band counts `bands{}` and per-task band `bandPct{}`**, `unreachableBands`, `overConcentratedBands`, the **FR-vs-MC split** (`freeResponse`/`multipleChoice`), the **answer-type distribution** and **integer-vs-rational results** (`integerAnswers`/`exactRationalAnswers`/`fractionAnswers`/`tableCompletionAnswers`), **odd-vs-even list lengths** (`oddLengthLists`/`evenLengthLists`), and the **redraw/rejection rates** (`avgAttempts`, `rejectionRatePerAccept`, `fractionNeedingRedraw`). Family-specific aggregates (§M): `mean{integer, properFraction}`, `median{integer, halfInteger}` (the `den ∈ {1,2}` split), `range{zero, positive}` (**range=0 vs positive**, since range=0 is now a valid FR case), `negativeListValues{count, byBand}` (negatives only at appropriate bands), `probability{endpoint, interior}` (**P=0/1/1-half endpoint vs interior**, `reducedProper`, `unitFraction`), `pictogram{whole, half}` (**whole-vs-half symbols**), `mode{single}` (multimodal/no-mode excluded by §10.2), and `scaffolding{scaffolded, unscaffolded}` (**scaffolded-vs-unscaffolded counts**). A `redraw` block reports `sampleSeeds`; the median-MC `AVERAGES_ENDS` drop-then-backfill and the probability in-range/endpoint redraws are documented as designed, not anomalous. **Every declared band must be reachable before fixtures freeze.**

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
| `equal-axis-scale` | **replace** | statistical axes use INDEPENDENT x/y scales (§J); replaced by `axis-scale-consistency` (each axis faithful to its own declared linear scale, one `gridRound` projection). |
| `media-to-scale` | **override** | applied to bar/line only; pictograms use `pictogram-key-exact` with `toScale:false`. |
| `no-answer-label-in-svg` | **replace** | replaced by the semantic `no-statistic-in-svg` + §L role-based leakage checks (raw-data equality is not leakage; only a dedicated answer/statistic-role element is), not the `,`/`/`/`=` blocklist, so keys/labels render. |
| `no-colour-only-information` | **inherit verbatim; NO change to the shared grey set** | canonical greys committed in §6.5/§13.4 are all already in the set; pattern+label+legend pairing satisfies the rule; no coordinate-lines source edited. |
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

1. Author `curriculum/objectives/SPI.MIDDLE.STAT.*.json` (the **eleven** objectives, with `vocabulary[]`, `notation[]`, and `commonMisconceptions[]` referencing the `MISC.STAT.*` ids) against `schemas/curriculum-objective.schema.json` at `reviewStatus: "approved-for-implementation"` (the owner's curriculum sign-off). `core/curriculum/graph-check.ts` enforces **no-duplicate-IDs and no-prerequisite-cycle as ERRORS (the DAG)** and emits **unresolved prerequisites as non-blocking WARNINGS only**; it does **not** inspect `crossDomainRelationships`. The family's promise is therefore "adds **zero new unresolved-prerequisite warnings**" (every prerequisite targets an authored ID), **not** a red/green cross-domain resolution gate. A **new bespoke** `domains/statistics/stats-data-handling-graph.test.ts` (modelled on `coordinate-lines-graph.test.ts`) asserts the eleven STAT objectives are present, their prerequisites resolve, that **every `crossDomainRelationships`/`prerequisites` target is an authored `objectiveId`** (the per-objective-explicit-ID convention is enforced here, since the shared tool does not), and the **current** expected `reviewStatus` (`approved-for-implementation` now, `approved` at the final review-pack decision) — not a hardcoded `approved`.
2. Write the **Python oracle** (`oracle/spi_oracle/stats_*`) first: the single seeded dataset model, exact `fractions.Fraction` solvers, the canonical monochrome chart SVG (carrying the unscoped `<style>`, **no** `class="cx-figure"`), the **deterministic semantic-HTML frequency-table serialiser** (§F), and the `MISC.STAT.*` registry. Generate golden + parity fixtures (chart SVG + HTML-table) from the oracle. **No Python theme mirror is written** — the render-mode/presentation/export layer is TypeScript-only.
3. Mirror in **TypeScript** (`domains/statistics/stats-data-handling.ts`) using `core/exact-math/rational.ts`, `core/seeded-random/mulberry32.ts`, `core/difficulty/band.ts`, the reused Cartesian projection primitives, and the **additive `core/visual-style/data-chart-theme/` + `core/render/data-charts/` extension** (which reuses `cartesian-theme.ts` without editing it — §7.2, §13.4). Add `checkTableCompletion` (→ `table-completion`) to `core/answer-checking`, reusing the exact-rational checker shape; **no `set` checker, no `list` checker, and no answer.type schema edit** in v1.0.0 (the `set`/multimodal-mode work is deferred).
4. `validate(item) → {status, validatorVersion, checks[]}` recomputes every figure and answer (second route) and runs the §13.3 named checks plus the §13.6 inherited/overridden battery.

### 14.3 Gates (all blocking before any approval)

| Gate | Spec |
| --- | --- |
| Golden | 4 seeds, frozen `oracle/golden/stats_data_handling.golden.json`, Py-authored, TS-verified byte-identical (canonical item JSON + **canonical chart SVG** + **deterministic frequency-table HTML**). |
| Parity | 150 seeds × 2 interactions, `stats_data_handling.parity.json`; independent Python + TypeScript output **byte-identical** for the canonical item JSON, the **canonical chart media SVG**, and the **deterministic HTML-table serialisation** (table parity is independent of chart-SVG parity, §F). Theme/export copies are TS-only and excluded from parity. |
| Sweep | `SPI_SWEEP = 10000` seeds: `invalid: 0`, **every declared band reachable before fixtures freeze** (§13.5 reachability proof), ≥3 distinct in-range misconception distractors per MC under exact-Rational comparison (else deterministic redraw), reproducibility (re-running a seed reproduces byte-for-byte). |
| Distribution | `stats_data_handling_distribution.json` emitted and integrity-checked (§13.5). |
| Style-isolation | the per-root `cx-figure` isolation + materialised export tests (§13.6) pass on the additive `data-chart-theme` extension; coordinate-lines output is byte-for-byte unchanged. |
| a11y | axe gate over rendered items: 0 critical / 0 serious, WCAG AA; semantic-HTML frequency tables, `dataTableFallback` + non-colour indicators present. |
| Exports | worksheet / answer-key / solutions + offline KaTeX render; bank-json round-trip is lossless; 6000×4200 colour + print exports self-contained. |
| Integrity + graph | the blocking integrity tests of §13.6 (manifest + **SHA-256** over every artefact) and the bespoke graph test of §14.2 pass. |
| Approved-generator regression | the approved arithmetic / geometric / linear / angle-geometry / coordinate-lines generators keep their output **byte-for-byte unchanged**. |

### 14.4 Approval lifecycle and immutability

The family registers in `core/sdk/sequence-registry.ts` with an **explicit** `approvalStatus: "pending-review"` field. This must be **present, not omitted**: `approvalStatusOf` in `core/sdk/generator-module.ts` **defaults to `"approved"`** when the field is absent, so an omitted field would silently leak an unreviewed family into normal Studio and production. With the field present, `generatorsForMode` exposes the family **only in review mode** and `approvedGenerators()` excludes it — gated from normal Studio and from production exports/samples until the owner decides on the review pack. An integrity test asserts the STAT entry carries `approvalStatus: "pending-review"` until owner approval.

Newly generated items begin at `lifecycle.state = "generated"` → `machine-validated`; the registry approval does **not** auto-approve future items; there is no auto-approval / auto-publication. The eleven objective files are at `reviewStatus: "approved-for-implementation"` now (curriculum-approved, cleared for the build). On the implemented review-pack decision the registry entry flips to `approvalStatus: "approved"` with a DECISION_LOG reference (date + decision number), the eleven objective files move to `reviewStatus: "approved"`, and the **golden + parity fixtures become immutable** — any future change ships as a new version (v1.0.1+), preserving the approved version in history (tags), unregistered and unselectable, exactly as v1.0.0/v1.0.1 of coordinate-lines are preserved. Rejection routes to a revised version; the rejected version is never registered. The 10,000-seed stability run is the standing regression guard across versions.

---

## 15. New reusable vs family-specific infrastructure

The family is built to **maximise reuse** of the newly-approved infrastructure and to add only the genuinely statistics-specific pieces. Nothing in the shared column is reinvented.

### 15.1 Shared (reused as-is, by name)

| Shared asset | Source | Reuse in this family |
| --- | --- | --- |
| Cartesian renderer discipline (single `gridRound` projection, `cx-` classes, clipping, the inherited `7680×4320` export envelope → S=6 → 6000×4200) reused in **independent-scale viewport mode** (NOT the equal x=y scale, §J) | `gen.geometry.coordinate-lines` primitives, via the additive `core/render/data-charts/` extension | Axes, gridlines, integer ticks, plotted points/segments for the **line graph**; the bar/pictogram baseline + category axis reuse the same projection at an independent y-scale; the export sizing is reused verbatim, not recomputed; coordinate-lines source is not edited. |
| Render-mode theme contract (per-root CSS vars, one common ruleset, premium/dark/accessible/print, `presentationSvg`/`exportSvg`, materialised 6000×4200 export) | `core/visual-style/cartesian-theme.{json,ts}` | Every figure and the visual audit. **TypeScript-only** (no Python mirror); byte-parity Py/TS is required of the canonical SVG + params/answer/distractors, **not** of the themed/exported copies. New series variables (`--cx-bar-fill`/`--cx-bar-hatch`/`--cx-icon`) follow the same per-root pattern (concrete diff in §13.4). |
| Exact arithmetic | `core/exact-math/rational.ts` + Python `fractions.Fraction` | All means/medians/probabilities as exact `{num,den}`; all distractor-vs-key and distinctness comparisons are reduced-Rational equality. |
| Seeded RNG (byte-identical Py/TS) | `core/seeded-random/mulberry32.ts` + `oracle/spi_oracle/seeded_random.py` | Deterministic dataset draw + deterministic MC redraw (median `AVERAGES_ENDS` drop, probability in-range/endpoint redraw). |
| Difficulty banding | `core/difficulty/band.ts` (`bandFromScore`, `round3`) | Weighted-axes score → band, using only the six closed-enum axes the generator emits (incl. the dedicated `scaffolding` axis; §M). |
| Answer-checking | `core/answer-checking` (exact-rational + the checker shape) | Reused for numeric/probability answers; the new `checkTableCompletion` (→ `table-completion`) is added in the same module, targeting an **existing** answer.type enum member (no schema edit). `checkUnorderedSet` (→ `set`) is **deferred** with the multimodal-mode work and is not built or used in v1.0.0. |
| Curriculum graph tool | `core/curriculum/graph-check.ts` | Used for its actual guarantee — duplicate-ID + prerequisite-cycle ERRORS, unresolved-prerequisite WARNINGS — **not** for cross-domain validation (which it does not perform; that is the bespoke family graph test). |
| Manifest + artifact-integrity + style-isolation tooling | `oracle/make_*_manifest.py`, `*-integrity.test.ts`, `*-style-isolation.test.ts` patterns | §13.6 tests are direct adaptations. |
| Delivery harness | review-pack/audit generators, exporters, bank-json round-trip, axe gate, SDK registry + approval flow (with **explicit** `approvalStatus`) | Driven family-specifically but mechanism unchanged. |

### 15.2 Family-specific (new, statistics-only)

| New asset | What it is |
| --- | --- |
| Seeded dataset model | The single source of truth per item, with **one canonical field vocabulary** pinned in cluster A/§4.2 and referenced identically everywhere: discriminator `kind: "frequency" \| "list"` (ordered line graph = a `list` plus `seriesLabels`; frequency table = a `frequency` dataset); fields `categories[]`, `frequencies[]` (int), `values[]` (int, no stored sorted copy), pictogram `pictogramKey` (int, in {2,5,10}, items per one complete symbol), and probability `outcomeSpace{favourable,total,targetCategoryIndex}` drawn from the same category frequencies (`total = Σf`); from this the chart, prompt, answer, solution, and `dataTableFallback` are all derived. |
| Statistics solvers | Exact `mean = (Σ f·x)/(Σ f)`, `median` (sorted; even-n → average of two middles, tagged `integer` when `den=1`, `exact-rational` when `den=2`), `mode` (single value of max frequency, `uniqueModeWhenAsked` gate; multimodal/no-mode deferred), `range = max − min`, weighted mean from a frequency table, `P(event) = favourable/total` reduced — all returning `Rational`/`Fraction`. |
| `MISC.STAT.*` registry | `core/misconceptions/data-handling.json`, the cluster-D ids under the single namespace `MISC.STAT.<TASK_GROUP>.<SHORT_NAME>`, each entry carrying the schema-required `{misconceptionId, domain, description, observableError, reviewStatus:"draft"}` (plus optional `title`), with the value-adapter intent in `distractorRule.summary` (and optional `typicalIncorrectMethod`), reserving `distractorRule.expression` for the optional internal symbolic form; `domain: "statistics"` to mirror the curriculum domain; `observableError`/`feedback` free of internal symbols; + task→[ids] eligibility; byte-parity Py/TS. |
| Per-chart canonical figures | Hand-rolled bar chart, pictogram (integer-key glyph repetition with exact partial-glyph clip), frequency table, and line-graph builders — integer coordinates via `gridRound`, no runtime trig, byte-identical Py↔TS, `role=img` + `<title>/<desc>` + `dataTableFallback`, greyscale-safe with **id-free inline-stroke hatching** (no `<pattern>`/`url(#)`), category strings under `cx-cat` and integer ticks under `cx-ticklbl`. |
| Per-chart validator checks | The statistics-only checks of §13.3 — `chart-realises-data` (bar tops / pictogram symbol counts / line-graph lattice points only), the **semantic §L leakage checks** (`no-statistic-in-svg` / `no-derived-statistic-annotation` / `no-answer-role-in-student-render` / `no-solution-overlay-in-student-render` / `raw-data-equality-is-not-leakage` / `student-a11y-does-not-state-result` / `answer-overlay-present-only-in-solution-mode`, replacing `no-answer-label-in-svg`), `frequency-table-blank-cell`, `pictogram-key-exact`, `category-label-correctness`, `bar-pattern-distinct` — plus the overridden `media-to-scale` (bar/line only) and `closure-agreement` recomputing the asked statistic by a second route. |
| Curriculum objectives + strand | The eleven `SPI.MIDDLE.STAT.*` objective files (with `vocabulary[]`, `notation[]`, `commonMisconceptions[]`) and the `data-handling-and-probability` strand; the explicit `OBJECTIVE_BY_TASK` map. |
| The review pack itself | `oracle/make_review_pack_stats.py` and the family pack/audit/distribution/manifest content of §13, including the per-task band-reachability proof and the fully-populated schema-valid exemplar items. |


---

## Appendix A — Resolved decisions (owner directive, 2026-06-24)

The four design choices surfaced during authoring are now **RESOLVED** by the owner's APPROVE-WITH-REQUIRED-REVISIONS directive. This appendix is retained as a **resolved-decisions record**; the resolutions are applied verbatim across the body of this document.

1. **Visual-style architecture — RESOLVED.** The statistics family does **NOT** alter the approved `core/visual-style/cartesian-theme.{json,ts}` (coordinate-lines v1.0.2) contract in place. It creates a **versioned ADDITIVE shared extension** (`core/visual-style/data-chart-theme/`, `core/render/data-charts/`) that REUSES the `cx-figure` per-root isolation, common axis/grid variables, `presentationSvg()`/`exportSvg()`, the premium/premium-dark/accessible/print modes, the 6000×4200 export, and the style-isolation tests, and ADDS the statistics primitives (chart bars, category labels, pictogram symbols, bar hatches, legends, data-point labels). **coordinate-lines output stays byte-for-byte unchanged.** After approval the extension may become approved reusable cross-domain infra (§7, §K).
2. **Frequency-table renderer — RESOLVED.** A **semantic HTML table** is the authoritative learner-facing + accessible renderer (proper table/row/column/header semantics, keyboard-accessible input cells, deterministic HTML serialisation, print-safe, offline, exact round-trip from the canonical dataset; blanks stay blank in the student version, answers only in the answer-key/solution). An optional SVG snapshot may be derived from the same canonical table model but does not replace it. **Table validation is independent from chart-SVG validation** (§F, §6.2).
3. **Stem-and-leaf — RESOLVED (stays deferred).** Stem-and-leaf remains deferred from v1.0.0 (§B), together with pie charts, scatter/correlation, regression/lines of best fit, histograms, box plots, quartiles/IQR, standard deviation/variance, grouped-data estimated means, and multimodal/no-mode/set-valued mode responses.
4. **Pictogram key / fractional symbols — RESOLVED.** `pictogramKey ∈ {2,5,10}` (the number of items represented by ONE complete symbol). Whole symbols for every key; **half symbols only when `pictogramKey` is even (so keys 2 and 10)**. Quarter / arbitrary fractional / partially-clipped symbols (other than exact half) are deferred. The student figure shows a clear key ("1 symbol represents 10 students."); the a11y + data-table fallback communicate the same WITHOUT giving the answer (§G).

**Confirmed RESOLVED owner choices also recorded here:** domain = `statistics`; objective ID domain segment = `STAT`; **unique-mode-only** so the mode answer is an `integer`, not a `set`; `pictogramKey ∈ {2,5,10}`, whole + half-when-even; **probability is reduced-fraction-only** (decimals not accepted; an unreduced equivalent does not get full correctness).


## Appendix B — Cross-section consistency record (owner decisions applied)

The items below are now **RESOLVED** and applied verbatim throughout the body; they are retained as a consistency record.

1. **Domain — RESOLVED:** domain is `statistics` (no `data-handling` alternative). Used verbatim across all objective IDs and the registry (§1).
2. **Objective ID segment — RESOLVED:** the domain segment is `STAT`; the eleven canonical IDs follow `SPI.MIDDLE.STAT.<TOPIC>.<MICRO>.01` (§1). One `OBJECTIVE_BY_TASK` constant is the single source, asserted everywhere.
3. **Strand — RESOLVED:** the strand value is `data-handling-and-probability` (free-form string); a curriculum-schema test pins both the domain and strand spellings (§1).
4. **Mode — RESOLVED:** v1.0.0 requires a **unique mode**, so the mode answer is a single `integer`, never a `set`. Multimodal / no-mode / set-valued mode responses are deferred; `checkUnorderedSet` / the `set` answer type are not exercised (§5.3, §10.2).
5. **Pictogram key — RESOLVED:** `pictogramKey ∈ {2,5,10}` (items per ONE complete symbol); whole symbols for every key, half symbols only when the key is even (keys 2 and 10); quarter / arbitrary fractions deferred. Every readable value is an exact integer (§G, §10.4).
6. **Probability — RESOLVED:** single-event, answer type `fraction`, **canonical reduced (simplest form) only**; decimals NOT accepted; an unreduced equivalent does not get full correctness (§5.5, §I).
7. **Pie chart — RESOLVED:** deferred from v1.0.0 by deterministic exclusion (absent from the `chartType` enum and every dispatch table), distinct from the exactness-based exclusions (standard deviation / variance / regression / quartiles / IQR / grouped means) (§6.2, §10.7).
8. **Frequency-table answer types — RESOLVED:** the cell-wise `table-completion` checker is kept distinct from the numeric statistic checkers; `complete_frequency_table` is FR-only with exactly one missing frequency or one missing total (§3, §5.4).
9. **Export — RESOLVED:** the reused `exportSvg` materialised export is 6000 × 4200 (S = 6); the visual-quality / overload check (dense-category stress tests, legend fit) is carried in the review pack (§7.3, §13.4, §O).
10. **Axis scaling — RESOLVED:** bar-chart and line-graph axes use **INDEPENDENT** x/y scales (frequency on y), NOT the coordinate-geometry equal x=y viewport; still one deterministic `gridRound` projection, still byte-identical Py/TS, with a count-axis step pinned from {1,2,5,10} (§6.7, §7.1, §J).

## Appendix C — Authoring & verification provenance

Authored by a multi-agent workflow: 15 sections drafted in parallel against a fixed platform-conventions digest, reviewed by four adversarial critics (statistics correctness, platform-fit, renderer/visual reuse, completeness), then revised against the consolidated findings and synthesized. **Subsequently revised IN PLACE to apply the owner's APPROVE-WITH-REQUIRED-REVISIONS directive of 2026-06-24** (decisions A–P): the eleven canonical objective IDs and the `OBJECTIVE_BY_TASK` single source; the interaction matrix (`complete_frequency_table` FR-only; probability MC for proper P only, P=0/1/1-half FR-only; unique mode); the data-model key names (`pictogramKey` as items-per-symbol, no stored sorted array, probability `outcomeSpace`); the independent-axis statistical scaling; the additive `data-chart-theme` / `data-charts` visual-style extension that leaves coordinate-lines byte-for-byte unchanged; the semantic answer-leakage checks; the semantic-HTML frequency-table renderer with independent table parity; the dedicated `scaffolding` difficulty axis; reduced-fraction-only probability; and the resolved Appendix A/B decisions. **Objective status: approved-for-implementation; generator registry: pending-review (gated) until the implemented review-pack decision. Implementation proceeds oracle-first.**
