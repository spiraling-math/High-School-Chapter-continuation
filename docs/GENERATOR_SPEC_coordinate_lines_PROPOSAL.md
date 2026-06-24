# Generator Specification — `gen.geometry.coordinate-lines` v1.0.1 (Coordinate geometry and straight-line graphs)

> **STATUS: IMPLEMENTED — PENDING FINAL CURRICULUM REVIEW (v1.0.1; owner REVISE applied 2026-06-24).**
> The family is **fully implemented and machine-validated** at **v1.0.1** (Python oracle + byte-parity TypeScript mirror, registered in `core/sdk/sequence-registry.ts` with `approvalStatus: pending-review`). v1.0.0 was implemented, reviewed, and returned with REVISE (`DECISION_LOG.md` #42); v1.0.1 applies the corrections (the read_point worked-solution axis wording; review-pack de-duplication, full interaction coverage, and band-coverage enforcement; the foundational `CARTESIAN_PLANE` objective in the curriculum summary; a strengthened distribution report). **v1.0.0 is preserved unchanged** (tag `coordinate-lines-v1.0.0`). The objective definitions are curriculum-approved (`reviewStatus: approved-for-implementation`); the generator remains **gated out of normal Generator Studio and out of production** until the owner's final APPROVE/REJECT of this review pack. **Every existing platform gate is retained without exception:** deterministic seeded generation (byte-identical Mulberry32 / Python PRNG streams); exact-`Rational` arithmetic (no floats in answers); independent Python + TypeScript verification with closure-agreement; canonical item + SVG byte-for-byte parity; runtime Ajv schema validation at boundaries; misconception-backed distractors (exactly three distinct, rule-recomputed); 10,000-seed (×2-mode) stability sweeps with reproducibility re-check; accessibility tests (axe-core 0 critical/serious, WCAG AA ≥ 4.5:1); offline HTML/JSON exports; immutable approved-generator fixtures; machine-validated initial lifecycle (`lifecycle.state = generated`). **The following advanced features are explicitly DEFERRED and DETERMINISTICALLY EXCLUDED — never silently included:** distance with irrational roots; vertical lines `x = a`; parallel / perpendicular lines; simultaneous-equation intersections; inequalities / shaded regions; function transformations; nonlinear graphs; scatter / regression; and 3D coordinates. In particular, any task whose canonical form is `y = mx + c` deterministically excludes vertical configurations (two equal x-values give no gradient, so the parameter loop redraws).

## Overview

`gen.geometry.coordinate-lines` is the SPI-Math Middle School **Geometry / Algebra bridge** family: reading and plotting Cartesian points, computing gradient and midpoint between lattice points, interpreting `y = mx + c`, and recovering a non-vertical line's equation from a graph or from two points. It is deliberately positioned as the **next architecture-proving step** because it is the first family that has to *compose two already-approved pipelines at once*. It reuses the exact-rational answer machinery and the `y = mx + c` algebraic vocabulary established by the approved `gen.algebra.linear-equations` family (its gradient, intercept, and equation answers are exact `Rational` / `integer` values, and its objectives carry `crossDomainRelationships` to **explicit, approved algebra objective IDs** such as `SPI.MIDDLE.ALG.LINEQ.TWOSTEP.01` — never a wildcard; see Section 2), while simultaneously driving the geometry **SVG pipeline** discipline proven by `gen.geometry.angles-figures` v1.2.3 (integers-only coordinates via `gridRound` round-half-up over exact `Rational`/`Fraction`, no runtime trigonometry, byte-identical Python ↔ TypeScript SVG, `role=img` + `<title>`/`<desc>` accessibility, monochrome no-colour-only-information).

The single new piece of reusable infrastructure this family introduces is a **canonical Cartesian renderer** — an axes / ticks / gridlines / plotted-point / straight-line drawing layer (CSS class prefix `cx-`, `viewBox 0 0 1000 700`, equal x and y unit scale `U` px per unit) that mirrors the existing `.gl`/`.ga`/`.gx` rendering discipline and emits byte-identical SVG from both the oracle and the app. Layered *over* that authoritative monochrome geometry is an optional **premium colour presentation layer** (palette tokens `--cx-series-1..N`, `--cx-axis`, `--cx-grid-major`, `--cx-grid-minor`, `--cx-pt-core`, `--cx-pt-outline`, `--cx-halo`, `--cx-bg`) in which colour never carries meaning alone. Both the Cartesian renderer and the colour layer are designed to be **directly reused by the Statistics & Data Handling family next** (coordinate axes, plotted points, and a high-resolution colour series treatment are exactly what scatter plots and data displays require), which is why proving them here — under all current gates, on the simplest possible geometry — is the right sequencing decision before that larger family is attempted.

## Identifier glossary

| Item | Value (use verbatim) |
| --- | --- |
| Generator id | `gen.geometry.coordinate-lines` |
| Generator version | `1.0.0` |
| Validator version | `1.0.0` |
| Domain · strand | `geometry` · `coordinate-geometry-straight-line-graphs` (new strand, distinct from `angles-lines-triangles-quadrilaterals`) |
| Cross-domain link | approved `SPI.MIDDLE.ALG.LINEQ.TWOSTEP.01` algebra objective (explicit ID via `crossDomainRelationships`; Section 2) |
| Objective status | `approved-for-implementation` (owner, 2026-06-23) |
| Initial registry status | `approvalStatus: pending-review` (gated out of normal Studio + production until the review-pack decision) |
| Initial item lifecycle | `lifecycle.state = generated` (machine-validated) |

**Seven micro-objectives — 1:1 with seven generator tasks**

There is also a foundational prerequisite objective **P0 `SPI.MIDDLE.GEO.COORD.CARTESIAN_PLANE.01`** (canonical answer type `coordinate`; Section 2), authored alongside O1–O7.

| # | Objective ID | Task | Skill | Canonical answer type(s) | MC? |
| --- | --- | --- | --- | --- | --- |
| O1 | `SPI.MIDDLE.GEO.COORD.READ_POINT.01` | `read_point` | read coordinates of a plotted point | `coordinate` | FR + MC (≥ 3 defensible distractors) |
| O2 | `SPI.MIDDLE.GEO.COORD.PLOT_POINT.01` | `plot_point` | plot / identify a point from a pair | `coordinate` | **FR only** (no MC in v1.0.0) |
| O3 | `SPI.MIDDLE.GEO.COORD.GRADIENT_TWO_POINTS.01` | `gradient_two_points` | gradient between two lattice points | `integer`, `exact-rational` | FR + MC when m ≠ 0 (≥ 3 distractors); **zero-gradient is FR only** |
| O4 | `SPI.MIDDLE.GEO.COORD.MIDPOINT.01` | `midpoint` | midpoint of two points | `ordered-pair` | FR + MC (≥ 3 defensible distractors) |
| O5 | `SPI.MIDDLE.GEO.COORD.INTERPRET_MX_C.01` | `interpret_mx_c` | read gradient + y-intercept of `y = mx + c` | `equation` | FR + MC where 3 valid structured distractors exist |
| O6 | `SPI.MIDDLE.GEO.COORD.EQUATION_FROM_GRAPH.01` | `equation_from_graph` | find `y = mx + c` from a graph | `equation` | FR + MC where 3 defensible distractors exist |
| O7 | `SPI.MIDDLE.GEO.COORD.EQUATION_FROM_2PTS.01` | `equation_from_two_points` | equation of a non-vertical line | `equation` | FR + MC where 3 defensible distractors exist |

> Free-response is the default interaction; multiple-choice is offered **only where at least three distinct, misconception-backed distractors are pedagogically defensible** (the same rule-recompute / deterministic-redraw discipline as the approved families). **Multiple-choice is an interaction-support mechanism, NOT an answer type:** every objective's `answerTypes[]` carries **mathematical answer types only** (`coordinate`, `ordered-pair`, `exact-rational`, `integer`, `equation`) and never lists `multiple-choice`. All these answer types are already present in the `question-item.schema.json` `answer.type` enum — **no schema change is required**. `exact-surd` exists in the enum but is **deferred** here (no distance-with-roots in v1.0.0). An explicitly requested interaction type is **never silently changed**: if MC is requested the generator redraws deterministically until the draw is MC-eligible; `plot_point` rejects an MC request as unsupported in v1.0.0 (it never silently returns FR instead).

**Canonical renderer CSS classes (`cx-` prefix, monochrome, authoritative)**

| Class | Role |
| --- | --- |
| `.cx-axis` | x / y axis lines |
| `.cx-tick` · `.cx-ticklbl` | axis tick marks · tick numeric labels |
| `.cx-grid-major` · `.cx-grid-minor` | major / minor gridlines |
| `.cx-line` | a plotted straight line |
| `.cx-pt-core` · `.cx-pt-outline` | plotted-point fill · plotted-point ring |
| `.cx-lbl` · `.cx-guide` | point/value labels · construction guide marks |

**Premium colour palette tokens (presentation layer only — colour never carries meaning alone)**

`--cx-series-1 … --cx-series-N`, `--cx-axis`, `--cx-grid-major`, `--cx-grid-minor`, `--cx-pt-core`, `--cx-pt-outline`, `--cx-halo`, `--cx-bg`. These restyle the **same canonical geometry**; the monochrome-safe canonical SVG remains authoritative for validation and byte-parity.

## Table of contents

1. Curriculum placement and objective IDs
2. Objective wording and prerequisites
3. Task-to-objective mapping
4. Parameter and coordinate model
5. Ordered-pair answer representation and equivalence checker
6. Cartesian SVG renderer contract
7. Viewport and clipping
8. Solver and independent-validator design
9. Misconception registry
10. Difficulty model
11. Edge-case and degeneracy policy
12. Accessibility model
13. Review-pack plan
14. Versioning and approval
15. Reusable-vs-family-specific infrastructure
16. Premium high-resolution colour graphics


---

## 1. Curriculum placement and objective IDs

**Placement.** SPI-Math Middle School -> Geometry/Algebra bridge -> Coordinate geometry and straight-line graphs. This family is the synoptic bridge where the existing `geometry` angle work and the approved `algebra` linear-equation work meet on the Cartesian plane. The seven objectives (plus one new foundational prerequisite, P0, introduced in Section 2) are authored as new `curriculum/objectives/SPI.MIDDLE.GEO.COORD.json` entries (one JSON array), validated by `schemas/curriculum-objective.schema.json`; all match the ID pattern `^SPI\.[A-Z0-9]+(\.[A-Z0-9_]+)+\.[0-9]{2}$`.

**Identifier structure (stated explicitly, per owner decision).** Every objective ID has the form `SPI.MIDDLE.GEO.COORD.<MICRO>.01`, decomposed as: `SPI` (academy) · `MIDDLE` (stage) · **`GEO` = the domain segment** (geometry) · **`COORD` = the topic segment** (coordinate geometry) · **`<MICRO>` = the micro-skill segment** (`CARTESIAN_PLANE`, `READ_POINT`, `PLOT_POINT`, `GRADIENT_TWO_POINTS`, `MIDPOINT`, `INTERPRET_MX_C`, `EQUATION_FROM_GRAPH`, `EQUATION_FROM_2PTS`) · `01` (the two-digit ordinal). This matches the real platform precedent `SPI.MIDDLE.ALG.LINEQ.ONESTEP_MUL.01` (`ALG` domain, `LINEQ` topic, `ONESTEP_MUL` micro-skill), so the five-plus-segment depth is unambiguous to reviewers.

**New strand (approved).** This family introduces the new curriculum strand **`coordinate-geometry-straight-line-graphs`**, which is **distinct from** the existing geometry strand `angles-lines-triangles-quadrilaterals` used by every current `SPI.MIDDLE.GEO` objective. The owner has approved this as a genuinely new, second geometry strand. A **curriculum-schema test will assert the new strand value `coordinate-geometry-straight-line-graphs` is accepted** by any strand enum / controlled vocabulary in `schemas/curriculum-objective.schema.json` (see Appendix B.1).

**Classification (identical across O1..O7 unless noted):**

| Field | Value |
|---|---|
| `academy` | `SPI-Math` |
| `programme` | `SPI-Math Middle School` |
| `stage` | `middle-school` |
| `course` | `SPI-Math Middle School Mathematics` |
| `domain` | `geometry` |
| `strand` | `coordinate-geometry-straight-line-graphs` |
| `unit` | `Coordinate geometry and straight-line graphs` |
| `topic` | `the Cartesian plane and straight-line graphs` |
| `calculatorPolicy` | `calculator-not-required` (all arithmetic is exact integer / exact-rational) |
| `reviewStatus` | `proposed` |
| `version` | `1.0.0` |
| `crossDomainRelationships` | explicit approved algebra objective IDs (per-objective, Section 2) — e.g. `SPI.MIDDLE.ALG.LINEQ.TWOSTEP.01`; never a `SPI.MIDDLE.ALG.LINEQ.*` wildcard |

**The seven micro-objectives (1:1 with the seven `gen.geometry.coordinate-lines` v1.0.0 tasks):**

| # | objectiveId | subtopic | microSkill | Generator task |
|---|---|---|---|---|
| O1 | `SPI.MIDDLE.GEO.COORD.READ_POINT.01` | reading coordinates of a plotted point | read the ordered pair (x, y) of a single plotted lattice point | `read_point` |
| O2 | `SPI.MIDDLE.GEO.COORD.PLOT_POINT.01` | plotting/identifying a point from a pair | identify the grid position of a point given its ordered pair (x, y) | `plot_point` |
| O3 | `SPI.MIDDLE.GEO.COORD.GRADIENT_TWO_POINTS.01` | gradient between two lattice points | compute the gradient between two distinct lattice points as an exact rational | `gradient_two_points` |
| O4 | `SPI.MIDDLE.GEO.COORD.MIDPOINT.01` | midpoint of two points | compute the midpoint of two lattice points as an ordered pair | `midpoint` |
| O5 | `SPI.MIDDLE.GEO.COORD.INTERPRET_MX_C.01` | reading gradient and y-intercept of y = mx + c | read off the gradient m and y-intercept c from an equation in the form y = mx + c | `interpret_mx_c` |
| O6 | `SPI.MIDDLE.GEO.COORD.EQUATION_FROM_GRAPH.01` | finding y = mx + c from a graph | determine the equation y = mx + c of a non-vertical line shown on a grid | `equation_from_graph` |
| O7 | `SPI.MIDDLE.GEO.COORD.EQUATION_FROM_2PTS.01` | equation of a non-vertical line through two points | determine the equation y = mx + c of the non-vertical line through two lattice points | `equation_from_two_points` |

All seven (and P0) enter the curriculum graph at `reviewStatus: proposed`. **No existing objective is modified.** The existing `SPI.MIDDLE.GEO.*` angle objectives and the approved `SPI.MIDDLE.ALG.LINEQ.*` objectives are referenced only as prerequisites / cross-domain links (incoming edges added in this family's `prerequisites`/`crossDomainRelationships` arrays); their own files are untouched and retain `reviewStatus: approved`.

> **Reference-integrity note (corrected from earlier draft).** Not every ID this family wants to point at is an *authored* objective today. Verified against `curriculum/objectives/*`:
> - **Authored & approved (safe targets):** `SPI.MIDDLE.NUM.SIGNED_OPERATIONS.01`; `SPI.MIDDLE.ALG.INVERSE_OPERATIONS.01`, `SPI.MIDDLE.ALG.EXPAND_BRACKETS.01`; the five `SPI.MIDDLE.ALG.LINEQ.*` objectives (`ONESTEP_ADD/MUL`, `TWOSTEP`, `BOTHSIDES`, `BRACKETS`); the five `SPI.MIDDLE.GEO.*` angle objectives.
> - **Referenced-but-undefined (dangling) nodes:** `SPI.MIDDLE.NUM.INTEGERS_NUMBER_LINE.01`, `SPI.MIDDLE.ALG.NOTATION_SUBSTITUTION.01`, and `SPI.MIDDLE.ALG.SUBSTITUTION.01` appear *only* inside other objectives' `prerequisites`/`relatedObjectives` arrays (e.g. `SIGNED_OPERATIONS.01` itself lists `INTEGERS_NUMBER_LINE.01` as a prerequisite; `ALG.FOUNDATIONS` lists `NOTATION_SUBSTITUTION.01`; `ALG.LINEQ` and `IBDPAASL.SEQSER.ARITH` list `SUBSTITUTION.01`). None of the three is an authored `objectiveId`.
>
> This family therefore does **not** depend on any dangling node. Section 2 routes every prerequisite/cross-domain edge to an authored, approved ID (or to the newly-proposed P0). `core/curriculum/graph-check.ts` downgrades an unresolved prerequisite to a *warning* (not an error), so even the pre-existing dangling references elsewhere keep the global DAG check green — but this proposal adds **zero new** unresolved-prerequisite warnings.

---

## 2. Objective wording and prerequisites

Each block below uses `curriculum-objective.schema.json` field names. Shared fields from Section 1 (`academy`, `programme`, `stage`, `course`, `domain`, `strand`, `unit`, `topic`, `calculatorPolicy: calculator-not-required`, `reviewStatus: proposed`, `version: 1.0.0`) are not repeated. `calculatorPolicy` is `calculator-not-required` for all seven (all arithmetic is exact integer / exact-rational, no decimals or roots). `answerTypes` entries are drawn from the platform `answer.type` enum (`question-item.schema.json#/$defs/answerType`); `allowedRepresentations` entries are drawn from the objective-schema enum (`symbolic`, `numeric`, `graphical`, `tabular`, `diagram`, `verbal-context`, ...).

**Proposed new shared prerequisite (P0).** No Cartesian-plane objective exists in the curriculum today. (The only authored directed-number objective is `SPI.MIDDLE.NUM.SIGNED_OPERATIONS.01`; the often-cited `SPI.MIDDLE.NUM.INTEGERS_NUMBER_LINE.01` is a *dangling* reference, not an authored objective — see Section 1's reference-integrity note.) This proposal therefore introduces one foundational objective, authored in the same file and **marked `proposed`**, used as a prerequisite by O1 and O2:

- **P0 (proposed, approved-for-implementation)** `SPI.MIDDLE.GEO.COORD.CARTESIAN_PLANE.01` — *"Identify and use the x-axis, y-axis, origin, and four quadrants of the Cartesian plane, including interpreting positive and negative coordinates."*
  - `prerequisites`: [`SPI.MIDDLE.NUM.SIGNED_OPERATIONS.01`] — the single authored directed-number objective, which transitively subsumes number-line work; **no edge to the unauthored `INTEGERS_NUMBER_LINE.01`.**
  - `answerTypes`: [`coordinate`] — mathematical answer type only; multiple-choice is interaction support and is never listed in `answerTypes`. `difficultyRange` {min:1, max:1}.
  - P0 is the only new prerequisite proposed; every other prerequisite below resolves to an authored, approved objective.

---

**O1 — `SPI.MIDDLE.GEO.COORD.READ_POINT.01`** (task `read_point`)
- `subtopic`: reading coordinates of a plotted point
- `microSkill`: read the ordered pair (x, y) of a single plotted lattice point
- `objectiveWording`: "Read the coordinates of a point plotted on a labelled Cartesian grid and state them as an ordered pair, with the x-coordinate first."
- `prerequisites`: [`SPI.MIDDLE.GEO.COORD.CARTESIAN_PLANE.01` (proposed P0)]
- `successCriteria`: ["Reads the horizontal (x) coordinate before the vertical (y) coordinate.", "Reads negative coordinates correctly in all four quadrants.", "States the answer as an ordered pair (x, y)."]
- `allowedRepresentations`: [`graphical`, `diagram`, `numeric`]
- `answerTypes`: [`coordinate`] — mathematical answer type only (no `multiple-choice`)
- `difficultyRange`: {min:1, max:2}

**O2 — `SPI.MIDDLE.GEO.COORD.PLOT_POINT.01`** (task `plot_point`)
- `subtopic`: plotting/identifying a point from a pair
- `microSkill`: identify the grid position of a point given its ordered pair (x, y)
- `objectiveWording`: "Plot a point accurately on a labelled Cartesian grid from a given ordered pair."
- `prerequisites`: [`SPI.MIDDLE.GEO.COORD.CARTESIAN_PLANE.01` (proposed P0), `SPI.MIDDLE.GEO.COORD.READ_POINT.01`]
- `successCriteria`: ["Moves x units horizontally then y units vertically from the origin, with correct signs.", "Distinguishes (a, b) from (b, a).", "Plots the unique grid point matching the ordered pair."]
- `allowedRepresentations`: [`graphical`, `diagram`, `numeric`]
- `answerTypes`: [`coordinate`] — mathematical answer type only (no `multiple-choice`)
- `difficultyRange`: {min:1, max:2}
- Note: `plot_point` is **free-response only** in v1.0.0 (a point-placement / printable plotting task); no MC plotted-position alternatives are generated, and an MC request is rejected as unsupported (Section 3).

**O3 — `SPI.MIDDLE.GEO.COORD.GRADIENT_TWO_POINTS.01`** (task `gradient_two_points`)
- `subtopic`: gradient between two lattice points
- `microSkill`: compute the gradient between two distinct lattice points as an exact rational
- `objectiveWording`: "Calculate the gradient of the non-vertical line through two lattice points as an exact integer or fraction."
- `prerequisites`: [`SPI.MIDDLE.GEO.COORD.READ_POINT.01`, `SPI.MIDDLE.NUM.SIGNED_OPERATIONS.01`]
- `crossDomainRelationships`: [`SPI.MIDDLE.ALG.LINEQ.TWOSTEP.01`]
- `successCriteria`: ["Computes the change in y and change in x with correct signs (rise over run).", "Expresses the gradient as an exact, fully reduced rational (or integer).", "Handles zero gradient (horizontal line) correctly."]
- `allowedRepresentations`: [`graphical`, `diagram`, `numeric`, `symbolic`]
- `answerTypes`: [`integer`, `exact-rational`] — mathematical answer types only (no `multiple-choice`)
- `difficultyRange`: {min:2, max:4}
- Note: distinct x-values are enforced by the generator (no vertical/undefined-gradient case ever reaches the item; see Section 3). Horizontal (m = 0) gradients **are** assessed, but only in **free-response** mode — a zero-gradient draw cannot field three distinct misconception-backed distractors, so it is emitted free-response (see the O3 MC rationale in Section 3).

**O4 — `SPI.MIDDLE.GEO.COORD.MIDPOINT.01`** (task `midpoint`)
- `subtopic`: midpoint of two points
- `microSkill`: compute the midpoint of two lattice points as an ordered pair
- `objectiveWording`: "Calculate the midpoint of the line segment joining two points and state it as an exact ordered pair."
- `prerequisites`: [`SPI.MIDDLE.GEO.COORD.READ_POINT.01`, `SPI.MIDDLE.NUM.SIGNED_OPERATIONS.01`]
- `successCriteria`: ["Averages the x-coordinates and the y-coordinates independently.", "Gives each coordinate as an exact value (integer or exact-rational half).", "States the midpoint as an ordered pair (x, y)."]
- `allowedRepresentations`: [`graphical`, `diagram`, `numeric`, `symbolic`]
- `answerTypes`: [`ordered-pair`] — mathematical answer type only (no `multiple-choice`)
- `difficultyRange`: {min:2, max:3}

**O5 — `SPI.MIDDLE.GEO.COORD.INTERPRET_MX_C.01`** (task `interpret_mx_c`)
- `subtopic`: reading gradient and y-intercept of y = mx + c
- `microSkill`: read off the gradient m and y-intercept c from an equation in the form y = mx + c
- `objectiveWording`: "Identify the gradient m and y-intercept c in a linear equation written in the form y = mx + c."
- `prerequisites`: [`SPI.MIDDLE.GEO.COORD.GRADIENT_TWO_POINTS.01`]
- `crossDomainRelationships`: [`SPI.MIDDLE.ALG.LINEQ.TWOSTEP.01`]
- `successCriteria`: ["Identifies m as the coefficient of x (including negative and fractional m).", "Identifies c as the constant term (the y-intercept).", "Handles the c = 0 and m = 1/−1 surface forms correctly."]
- `allowedRepresentations`: [`symbolic`, `numeric`]
- `answerTypes`: [`equation`] — mathematical answer type only (no `multiple-choice`)
- `difficultyRange`: {min:2, max:3}
- Note: the canonical answer is a `Line {m, c}` object carried under `answer.type = equation`, with `canonical` y = mx + c and `equivalentForms` exposing m and c. **The student response uses two labelled fields — "Gradient m" and "y-intercept c" — and does NOT require rewriting the full equation unless explicitly asked;** the answer display is `"m = ..., c = ..."`, and a full equivalent equation may be accepted as an optional equivalent response (Section 3, Section 5). Horizontal lines (m = 0) are permitted; vertical lines are not representable in y = mx + c and are excluded by construction (a finite m is always drawn — see Section 3).

**O6 — `SPI.MIDDLE.GEO.COORD.EQUATION_FROM_GRAPH.01`** (task `equation_from_graph`)
- `subtopic`: finding y = mx + c from a graph
- `microSkill`: determine the equation y = mx + c of a non-vertical line shown on a grid
- `objectiveWording`: "Determine the equation y = mx + c of a non-vertical straight line shown on a coordinate grid."
- `prerequisites`: [`SPI.MIDDLE.GEO.COORD.GRADIENT_TWO_POINTS.01`, `SPI.MIDDLE.GEO.COORD.INTERPRET_MX_C.01`]
- `crossDomainRelationships`: [`SPI.MIDDLE.ALG.LINEQ.TWOSTEP.01`]
- `successCriteria`: ["Reads the y-intercept c directly from the graph.", "Computes the gradient m from two clearly identifiable lattice points on the line.", "Writes the equation in the canonical form y = mx + c."]
- `allowedRepresentations`: [`graphical`, `diagram`, `symbolic`]
- `answerTypes`: [`equation`] — mathematical answer type only (no `multiple-choice`)
- `difficultyRange`: {min:3, max:4}
- Note: canonical form is **y = mx + c**; vertical lines x = a are deterministically excluded by structural construction (the line is parameterised by a finite reduced m — see Section 3).

**O7 — `SPI.MIDDLE.GEO.COORD.EQUATION_FROM_2PTS.01`** (task `equation_from_two_points`)
- `subtopic`: equation of a non-vertical line through two points
- `microSkill`: determine the equation y = mx + c of the non-vertical line through two lattice points
- `objectiveWording`: "Determine the equation y = mx + c of the non-vertical line passing through two given points."
- `prerequisites`: [`SPI.MIDDLE.GEO.COORD.GRADIENT_TWO_POINTS.01`, `SPI.MIDDLE.GEO.COORD.INTERPRET_MX_C.01`, `SPI.MIDDLE.ALG.LINEQ.TWOSTEP.01`]
  - *(`SPI.MIDDLE.ALG.LINEQ.TWOSTEP.01` is the authored two-step linear-equation objective that carries the substitute-then-solve work needed to find c; **`BOTHSIDES.01` is deliberately NOT a hard prerequisite** per the owner's prerequisite graph.)*
- `crossDomainRelationships`: [`SPI.MIDDLE.ALG.LINEQ.TWOSTEP.01`]
- `successCriteria`: ["Computes the gradient m from the two points as an exact rational.", "Substitutes one point to find the y-intercept c exactly.", "Writes the equation in the canonical form y = mx + c."]
- `allowedRepresentations`: [`graphical`, `diagram`, `numeric`, `symbolic`]
- `answerTypes`: [`equation`] — mathematical answer type only (no `multiple-choice`)
- `difficultyRange`: {min:3, max:5}
- Note: canonical form is **y = mx + c**; the two defining points are constrained to have distinct x-values (no vertical line), so a gradient always exists (see Section 3).

**Prerequisite DAG edges added by this family** (child --prereq--> parent; "(proposed)" marks the one new node; every other target is an authored, approved objective):

```
P0  SPI.MIDDLE.GEO.COORD.CARTESIAN_PLANE.01 (proposed)
        -> SPI.MIDDLE.NUM.SIGNED_OPERATIONS.01            (authored, approved)
O1  READ_POINT.01            -> P0
O2  PLOT_POINT.01            -> P0 ; O1
O3  GRADIENT_TWO_POINTS.01   -> O1 ; SPI.MIDDLE.NUM.SIGNED_OPERATIONS.01
O4  MIDPOINT.01              -> O1 ; SPI.MIDDLE.NUM.SIGNED_OPERATIONS.01
O5  INTERPRET_MX_C.01        -> O3
O6  EQUATION_FROM_GRAPH.01   -> O3 ; O5
O7  EQUATION_FROM_2PTS.01    -> O3 ; O5 ; SPI.MIDDLE.ALG.LINEQ.TWOSTEP.01
```

Every prerequisite edge above uses an **explicit cross-domain ID** (never a `SPI.MIDDLE.ALG.LINEQ.*` wildcard) and targets either an already-`approved` authored objective (`SPI.MIDDLE.NUM.SIGNED_OPERATIONS.01`, `SPI.MIDDLE.ALG.LINEQ.TWOSTEP.01`) or an earlier objective in this same family; **`SPI.MIDDLE.ALG.LINEQ.BOTHSIDES.01` is deliberately NOT made a hard prerequisite of any objective.** The subgraph is acyclic (a clean topological order is P0, O1, O2, O3, O4, O5, O6, O7). **Before any record is accepted, the full-DAG check and the unresolved-reference check must pass:** `core/curriculum/graph-check.ts` validates the whole curriculum graph as a DAG after these `prerequisites` arrays are merged in (asserting no cycle), and every prerequisite/cross-domain ID must resolve to an authored objective (or to P0, authored in the same file). Introducing these objectives keeps both checks green — every target above is an authored ID or P0, so this family adds **no new unresolved-prerequisite warnings**. The only pre-existing warnings (the dangling `INTEGERS_NUMBER_LINE.01` / `NOTATION_SUBSTITUTION.01` / `SUBSTITUTION.01` references inside *other* files) are untouched by this proposal.

---

## 3. Task-to-objective mapping

The mapping is strictly 1:1 — each `gen.geometry.coordinate-lines` v1.0.0 task realises exactly one objective and each objective is realised by exactly one task. `interactionType` values are from the item-schema enum (`free-response`, `multiple-choice`); `free-response` is the default. **Multiple-choice is an interaction-support mechanism, not an answer type** — the `answer.type` column below lists the underlying mathematical answer type, never `multiple-choice`. **MC is offered only where at least three distinct, misconception-backed distractors are pedagogically defensible** (per the platform misconceptions discipline: each distractor is computed from a registry rule, must be DISTINCT, must not equal the answer, and exactly three are required or the seeded param loop redraws). Where MC cannot field three defensible distinct distractors for a given surface form, the item is emitted `free-response` rather than shipping a weak MC. **An explicitly requested interaction type is never silently changed:** if MC is requested, the generator redraws deterministically until the draw is MC-eligible (it never silently substitutes FR); for `plot_point` an MC request is **rejected as unsupported** in v1.0.0.

| Task | objectiveId | interactionType(s) | answer.type | MC offered? | Rationale (misconception availability) |
|---|---|---|---|---|---|
| `read_point` | O1 `READ_POINT.01` | `free-response`, `multiple-choice` | `coordinate` | Yes | Three distinct distractors: axis-swap (y, x); sign-flip of one coordinate; sign-flip of both (wrong-quadrant). All distinct from the answer in general position. |
| `plot_point` | O2 `PLOT_POINT.01` | `free-response` **only** | `coordinate` | **No (FR only in v1.0.0)** | A graph/point-placement (or printable plotting) task: the learner places a marker rather than choosing from labelled wrong points. **No MC plotted-position alternatives are generated in v1.0.0**, and an explicit MC request is rejected as unsupported (never silently returned as FR). The point misconceptions remain diagnostic only. |
| `gradient_two_points` | O3 `GRADIENT_TWO_POINTS.01` | `free-response`; `multiple-choice` **only when m ≠ 0** | `integer` \| `exact-rational` | **Yes when m ≠ 0 and 3 defensible distractors exist; No (FR only) for m = 0** | Non-zero gradient: three distinct distractors — run/rise inverted (Δx/Δy, guarded off when \|m\|=1), sign dropped on one difference, reciprocal/negation. **Zero gradient (horizontal line) is FR-only in v1.0.0:** at m = 0 the gradient registry cannot field three distinct misconception-backed distractors, so the horizontal draw is always emitted **free-response** (an MC request for this task redraws away from m = 0). |
| `midpoint` | O4 `MIDPOINT.01` | `free-response`, `multiple-choice` | `ordered-pair` | Yes | Three distinct distractors: difference instead of sum (Δ/2); sum without halving (guarded null only when the midpoint is the origin, i.e. x1+x2=0 AND y1+y2=0); one coordinate halved and the other not. |
| `interpret_mx_c` | O5 `INTERPRET_MX_C.01` | `free-response`, `multiple-choice` | `equation` (canonical `Line {m, c}`) | Yes where 3 valid structured distractors exist | Three distinct structured distractors: m and c swapped; c read as the x-coefficient on rearranged surface forms; sign error on c. Student response uses two labelled fields "Gradient m" and "y-intercept c"; answer display `"m = ..., c = ..."`; the full equation need not be rewritten unless asked. |
| `equation_from_graph` | O6 `EQUATION_FROM_GRAPH.01` | `free-response`, `multiple-choice` | `equation` (full `y = mx + c`) | Yes where 3 defensible distractors exist | Three distinct distractors: gradient sign flipped (m → −m); x-intercept misread as the y-intercept (guarded null when m = 0 or c = 0, i.e. no finite x-axis crossing / line through origin); run/rise inverted gradient. Each yields a distinct full equation. |
| `equation_from_two_points` | O7 `EQUATION_FROM_2PTS.01` | `free-response`, `multiple-choice` | `equation` (full `y = mx + c`) | Yes where 3 defensible distractors exist | Three distinct distractors: gradient inverted (Δx/Δy, guarded off when \|m\|=1); c from substituting the wrong point / sign error; m correct but c omitted (c = 0). |

**Canonical-form and exclusion notes.**

- **O6 and O7 canonical form is y = mx + c. Vertical lines x = a are deterministically excluded — but the *predicate* differs by task, because not every line task draws a defining point pair:**
  - **O3 (`gradient_two_points`) and O7 (`equation_from_two_points`)** draw an explicit point pair P1, P2. For these the exclusion is **point-pair-based**: the generator constrains the two governing lattice points to have **distinct x-values (x1 ≠ x2)**; if a draw produces equal x-values the constraint fails and the seeded param loop continues (the RNG advances deterministically and redraws), so no vertical-line item is ever emitted and the same seed always yields the same accepted item.
  - **O5 (`interpret_mx_c`) and O6 (`equation_from_graph`)** draw the line directly as a `Line {m, c}` shape (no defining point pair exists). For these the exclusion is **structural**: a finite, reduced-`Rational` m is drawn, and a `Line {m, c}` shape cannot represent a vertical line. There is no `x1 ≠ x2` predicate to assert. (For O6 the two on-line lattice anchors used to draw the segment necessarily have distinct x, which follows automatically from finite m.)
  - The independent Python+TS verifiers therefore split the `vertical-line-excluded` assertion by task: assert `x1 ≠ x2` on the drawn points for O3/O7; assert the structural invariant (m is a finite reduced `Rational`) for O5/O6. Stated in one line: **"distinct x where a defining point pair exists; finite-m structural exclusion otherwise."**
- **O3 (`gradient_two_points`)** likewise requires distinct x-values (equal x ⇒ undefined gradient ⇒ redraw). **Horizontal lines (m = 0, equal y-values) are permitted and assessed** in O3 (free-response only, per the table above) and in O5/O6/O7. **Vertical lines are excluded ONLY from the tasks that compute or represent a finite gradient** (O3 `gradient_two_points`, O5 `interpret_mx_c`, O6 `equation_from_graph`, O7 `equation_from_two_points`). The point-only tasks `read_point` (O1), `plot_point` (O2) and `midpoint` (O4) **MAY use two points that share an x-coordinate**, because no gradient is computed there; only coincident points are rejected (O4 requires two distinct points).
- Every `answer.type` above is already in the item-schema `answer.type` enum (`coordinate`, `ordered-pair`, `exact-rational`, `integer`, `equation`); **no `answer.type` schema change is required, and `multiple-choice` is never used as an `answer.type` (it is an interaction type only).** Exact-rational answers serialise as `{num,den}` (den ≥ 1, GCD-reduced) and are checked by `core/answer-checking/rational-checker.ts checkExactRational`. The `equation`-typed answer is checked by the new `core/answer-checking/line-equation-checker.ts` (Section 5), which performs a two-variable exact-rational reduction (lhs = rhs over {x, y} → A·y + B·x + C = 0, rejecting A = 0 as a non-finite/undefined gradient); this is new infrastructure, not a reuse of the single-variable `linexpr.ts`. `exact-surd` and distance-with-roots are deferred and never emitted in v1.0.0.
- For every MC item, the validator's `exactly-one-correct`, `distractors-distinct-misconceptions`, `distractor-value-matches-rule`, `distractor-not-answer`, and `distractor-feedback-clean` checks gate emission. **Only tasks/parameter sets that can yield three distinct misconception-backed distractors are MC-eligible.** When the interaction type is the default (unpinned), an item that cannot field three distinct distractors is generated as `free-response` rather than silently shipping a weak MC. When MC is **explicitly requested**, the generator instead **redraws deterministically away from any MC-ineligible sub-case** until it produces a valid three-distractor item (it never silently downgrades to FR); for `plot_point`, which is FR-only, an MC request is rejected as unsupported. The O3 zero-gradient case is the one structurally-forced FR sub-case in v1.0.0 (an MC request for O3 redraws away from m = 0), and the §13.2 coverage cell for "zero gradient" is satisfied by a **free-response** O3 item.


---

## 4. Parameter and coordinate model

This section specifies the `params` object (the schema's *source of truth*: every item is reproducible from `{generatorId, generatorVersion, seed, params}`) for each of the seven tasks of `gen.geometry.coordinate-lines` v1.0.0, the exact-rational coordinate types, the integer-vs-rational ranges per task, the `seed -> params` derivation through `Mulberry32`, and the deterministic bounded redraw loop with its acceptance predicates.

### 4.1 Coordinate value types (exact only)

All coordinates, gradients and intercepts are exact rationals carried as the platform's reduced `{num, den}` shape (`core/exact-math/rational.ts`, `den >= 1`, GCD-reduced, mirrored by `fractions.Fraction` in the oracle). No floating point ever enters a stored value. Three composite shapes are used in `params`:

| Type | Shape | Invariant |
|---|---|---|
| `RatJson` | `{ num: int, den: int }` | `den >= 1`, GCD-reduced, canonical (identical TS/Py byte output) |
| `Point` | `{ x: RatJson, y: RatJson }` | both components exact rationals |
| `Line` | `{ m: RatJson, c: RatJson }` | gradient `m` and y-intercept `c`; the line is `y = m x + c`. **A vertical line is not representable** by this shape (it has no finite `m`), which is the structural guarantee that vertical lines are excluded (see 4.4 P2). |

`Point` and `Line` are the canonical internal carriers; they serialise to exactly these JSON objects in `params` and feed `answer.canonical` (Section 5). Every `Rational` round-trips through `toJSON()` to `{num, den}`; integers carry `den = 1`. Because the `Line` shape can only hold a *finite reduced* `m`, a vertical configuration is structurally unrepresentable for the line-valued tasks (O5, O6) — there is no defining point pair to constrain there, only the drawn `{m, c}` itself (see 4.4 P2).

### 4.2 Per-task parameter ranges

The platform's grid is a lattice with **equal x and y unit scale** (`U` px per unit, viewBox `0 0 1000 700`, `cx-` renderer). Because x and y share a single `U`, the emitted figures are genuinely geometrically faithful, so each item carries `media[].toScale = true` (the §8 diagram-check group asserts this, mirroring the angles family's `not-to-scale` check inverted; no `NOT TO SCALE` label is ever emitted). Coordinates are plotted as integers via `gridRound(num, den)` (round-half-up over the exact Rational, mirroring the angles renderer's `gridRound`); the *mathematical* values remain exact rationals.

**Sampling bounds vs rendered viewport — kept strictly separate.** The committed constants `COORD_MAX_X = 10` and `COORD_MAX_Y = 10` are **sampling-domain limits**: every drawn lattice coordinate satisfies `|x| ≤ COORD_MAX_X` and `|y| ≤ COORD_MAX_Y`. They are **NOT** a fixed `[-10, 10]` render window. The **rendered viewport** is computed per item by the deterministic dynamic-viewport algorithm of §7 (a data window from the drawn points + origin + margin, then the largest equal-scale `U` that fits the `1000 × 700` canvas); the same seed yields the same window, but different items render different windows. Define the **sampling domain** `D = [-COORD_MAX_X, COORD_MAX_X] × [-COORD_MAX_Y, COORD_MAX_Y]` (the set every drawn point lies in); the **render window** `W` is the §7 per-item viewport, never a constant. All integer draws below use `Mulberry32.nextInt(lo, hi)` (inclusive).

| Task (Objective) | Drawn params | Coordinate domain | Gradient/intercept domain |
|---|---|---|---|
| `read_point` (O1 `SPI.MIDDLE.GEO.COORD.READ_POINT.01`) | `P` | **lattice**: `P.x ∈ [-COORD_MAX_X, COORD_MAX_X]`, `P.y ∈ [-COORD_MAX_Y, COORD_MAX_Y]` integers (`den = 1`) | — |
| `plot_point` (O2 `SPI.MIDDLE.GEO.COORD.PLOT_POINT.01`) | `P`, `quadrantTag` | **lattice**: integers as above | — |
| `gradient_two_points` (O3 `SPI.MIDDLE.GEO.COORD.GRADIENT_TWO_POINTS.01`) | `P1`, `P2` | **lattice**: integers in `D`; `P1 != P2` and `P1.x != P2.x` | gradient `m = (y2 - y1)/(x2 - x1)` exact `Rational`, may be non-integer rational; `m = 0` (horizontal) **allowed** — see free-response note in 4.4 P5 |
| `midpoint` (O4 `SPI.MIDDLE.GEO.COORD.MIDPOINT.01`) | `P1`, `P2` | **lattice**: integers in `D`; `P1 != P2` (may share an x-coordinate — no gradient is computed) | midpoint `M = ((x1+x2)/2, (y1+y2)/2)` exact rational (half-integer components allowed) |
| `interpret_mx_c` (O5 `SPI.MIDDLE.GEO.COORD.INTERPRET_MX_C.01`) | `L = {m, c}` (no defining point pair) | line drawn over its render window `W` (§7) | `m` integer or rational with small denominator `∈ {1,2,3,4}`; `c` integer `∈ [-COORD_MAX_Y, COORD_MAX_Y]`; vertical exclusion is structural (4.4 P2) |
| `equation_from_graph` (O6 `SPI.MIDDLE.GEO.COORD.EQUATION_FROM_GRAPH.01`) | `L = {m, c}`, two display lattice anchors `A1, A2` on the line (`A1.x != A2.x`) | line over its render window `W` (§7) | `m` rational small-denominator; `c` integer; **two lattice points exist on the line inside `W`** |
| `equation_from_two_points` (O7 `SPI.MIDDLE.GEO.COORD.EQUATION_FROM_2PTS.01`) | `P1`, `P2` | **lattice**: integers in `D`; `P1.x != P2.x` | derived `L = {m, c}`, `m = (y2-y1)/(x2-x1)`, `c = y1 - m·x1`, both exact rationals |

Pedagogical rationale for lattice-vs-rational choice: O1, O2, O3, O4, O7 read or build from **plotted lattice points**, so their inputs are integers (a student must be able to read each plotted point exactly); rational *outputs* (gradient in O3/O7, midpoint in O4) arise naturally from integer inputs and are retained exactly. O5/O6 are about *reading a drawn line*, so the line is parameterised directly by `{m, c}` with a small-denominator `m` so the gradient is legible from lattice crossings; O6 additionally guarantees two integer-lattice anchor points with distinct x on the line so the gradient/intercept are determinable from the figure without estimation (the distinct-x of the anchors follows automatically once `m` is finite).

`difficultyRange` per objective and the per-task band come from the established difficulty mechanism (Section 10); this section fixes only the parameter geometry. (The difficulty axes emitted in `difficulty.axes` are drawn solely from the schema's closed axis vocabulary in `schemas/question-item.schema.json` `$defs/difficultyProfile.axes`; Section 10 specifies the mapping. No axis name is invented here, and the parameter ranges above feed only those schema-valid axes.)

### 4.3 Seed -> params derivation (Mulberry32)

Derivation is byte-identical TS/Py (`core/seeded-random/mulberry32.ts` + `oracle/spi_oracle/seeded_random.py`, anchored by `oracle/golden/prng_anchors.json`). One `Mulberry32(seed)` instance drives the entire generation; draws occur in a fixed, documented order so the stream is reproducible. The task is selected first (`rng.choice(TASKS)`) unless pinned by config, exactly as the angles generator selects its task. A point is drawn as an ordered pair of `nextInt` calls (x then y); a small-denominator rational gradient is drawn as `numerator = nextInt(...)`, `denominator = rng.choice([1,2,3,4])` then reduced via `new Rational(num, den)`. The RNG advances deterministically on every draw, including rejected draws (4.4), so the same seed always yields the same accepted item.

### 4.4 Deterministic redraw loop and acceptance predicates

The generator uses the platform's bounded redraw pattern (a `for` loop to `MAX_PARAM_ATTEMPTS`, proposed `400`, matching the angles generator): `drawParams` proposes a candidate, `acceptable(params)` returns the accepted artifact or `null`; on `null` the loop *continues* and the RNG advances, so **the same seed yields the same accepted item** (deterministic redraw). If no candidate is accepted within the cap the generator throws (a sweep-detectable hard failure, never a silent skip).

Acceptance is the conjunction of the following predicates. They are *named* so the validator can re-assert each one independently (rebuild-from-params route).

**P1 — distinct points.** For any task drawing `P1, P2`: `P1 != P2` by component-wise exact `Rational` equality. (O3/O4/O7.)

**P2 — gradient defined (vertical-line exclusion), split by task shape.** Vertical lines `x = a` are deterministically excluded, but the *form* of the guarantee differs by task because only some tasks draw a defining point pair:

- **O3, O7 (point-pair tasks).** The canonical line is built from `P1, P2`, so assert `P1.x != P2.x` (equivalently the line has finite `m`). **Two equal x-values give no gradient, so the candidate is rejected and the loop redraws.**
- **O5, O6 (line-valued tasks).** No defining point pair exists; the line is drawn directly as `L = {m, c}` with `m` a finite reduced `Rational` (4.2). The exclusion is therefore **structural**: the `Line` shape cannot represent an infinite gradient, so a vertical configuration can never be emitted. For O6 additionally assert the two display anchors satisfy `A1.x != A2.x` (which follows automatically once `m` is finite). The validator's `vertical-line-excluded` check is correspondingly split: assert `x1 != x2` where a defining point pair exists (O3/O7); assert the finite-`m` structural invariant otherwise (O5/O6).

(Distance-with-roots, parallel/perpendicular, intersections, inequalities, transformations, nonlinear, scatter, 3D are likewise never drawn — they are simply absent from `drawParams`, the strongest form of deterministic exclusion.)

**P3 — within-window, line in scope & integer-realisable.** Every plotted point and every line/axis intersection used by the figure lies within `W` after `gridRound`; the line enters and exits the plot rectangle so a non-degenerate segment is actually drawn. Concretely:

- For every line task, assert `ymin <= c <= ymax` (the y-intercept lies inside the window) **and** the clipped segment is non-empty. This makes the renderer's parallel-edge/clip invariants (the horizontal `m = 0` case clips to full width) a *proven* precondition rather than an assumption, and guarantees a horizontal line `y = c` actually lies within the visible band.
- **Degenerate-clip guard:** after Liang–Barsky clipping, if `t0 >= t1` (a zero-length or empty visible segment, e.g. a non-vertical line that only touches the window at a single corner), reject the candidate and redraw, so a corner-touch line never emits a zero-length `<line>`.
- For O6, **at least two lattice points of the line lie strictly inside `W`** (so gradient and intercept are readable from the figure), and these are the carried anchors `A1, A2`.

**P4 — figure fits the viewport with clearance.** Reusing the angles renderer's clearance discipline (`labelsOk`-style feasibility), all point markers (`cx-pt-core`/`cx-pt-outline`), tick labels (`cx-ticklbl`), and the neutral line label (e.g. `l`; never the equation) must place inside the canvas with the documented minimum clearance and without colliding with axes, gridlines, each other, or the plotted geometry. If placement is infeasible the candidate is rejected (redraw). This guards legibility deterministically rather than at render time.

**P5 — MC has three distinct misconception-backed distractors.** Only for items emitted as `interactionType: multiple-choice`. Using the family misconception registry (`oracle/spi_oracle/coordinate_lines_misconceptions.py` + `domains/geometry/coordinate-lines-misconceptions.ts`, byte-parity), the generator computes each eligible rule's value, **skips a value equal to the answer or already seen (DISTINCT)**, and needs **exactly 3**. If fewer than 3 distinct defensible distractors exist, `acceptable` returns `null` and the param loop redraws (identical contract to the angles `generateDistractors`). Free-response is the default; MC is only emitted where at least 3 such distractors are pedagogically defensible.

> **Zero-gradient gradient_two_points is free-response-only.** When `m = 0` (a horizontal line, `y1 == y2`), the gradient eligibility set yields at most one distinct non-answer value (the inverted-gradient and sign rules go `null` on the `m = 0` guard, and the Δy-only and sum-of-denominators rules both collapse onto the answer `0` and are skipped); only the sum-of-both rule survives. Three distinct distractors therefore cannot be assembled, so a zero-gradient `gradient_two_points` candidate is **always emitted free-response** (never multiple-choice) — analogous to the `plot_point` MC note. The horizontal case is fully supported as a free-response item, which satisfies the §13.2 zero-gradient coverage cell; it is not silently excluded, only steered to free-response. The MC param loop only redraws away from `m = 0` when `interactionType` is pinned to multiple-choice for this task.

**P6 — answer-type well-formed.** The canonical answer for the task is constructible in its declared `answer.type` (Section 5): a reduced `RatJson` for gradient/intercept (`den = 1` exactly when integral), a `Point` for coordinate/ordered-pair answers, a `Line` for `equation` answers.

### 4.5 Worked `params` examples (one per task)

Values below are illustrative reduced rationals in the exact `{num, den}` shape; they show the *shape* an accepted candidate takes (the actual seed -> params mapping is fixed by 4.3 and reproduced by the oracle).

**O1 `read_point`.** Plotted point at `(-3, 4)`.
```
params = { task: "read_point",
           P: { x: {num:-3,den:1}, y: {num:4,den:1} } }
```
Answer (Sec 5): `coordinate` `{ x:{num:-3,den:1}, y:{num:4,den:1} }`, display `"(-3, 4)"`.

**O2 `plot_point`.** Plot the pair `(5, -2)`.
```
params = { task: "plot_point",
           P: { x:{num:5,den:1}, y:{num:-2,den:1} },
           quadrantTag: "IV" }
```
Answer: `coordinate` `{ x:{num:5,den:1}, y:{num:-2,den:1} }`, display `"(5, -2)"`.

**O3 `gradient_two_points`.** Lattice points `(-2, 1)` and `(4, 5)`; `m = (5-1)/(4-(-2)) = 4/6 = 2/3`.
```
params = { task: "gradient_two_points",
           P1:{ x:{num:-2,den:1}, y:{num:1,den:1} },
           P2:{ x:{num:4,den:1},  y:{num:5,den:1} } }
```
Answer: `exact-rational` `{num:2,den:3}`, display `"2/3"`. P2 holds (`x1 != x2`): gradient defined. (Here `|m| != 1` and `m != 0`, so all five gradient distractor rules can field distinct non-answer values; a horizontal draw, e.g. `(-2,1)&(4,1)` with `m = 0`, would instead be emitted free-response per the P5 note.)

**O4 `midpoint`.** Lattice points `(-3, 2)` and `(4, 5)`; `M = (1/2, 7/2)` (half-integer components retained exactly).
```
params = { task: "midpoint",
           P1:{ x:{num:-3,den:1}, y:{num:2,den:1} },
           P2:{ x:{num:4,den:1},  y:{num:5,den:1} } }
```
Answer: `ordered-pair` `{ x:{num:1,den:2}, y:{num:7,den:2} }`, display `"(1/2, 7/2)"`. (Here `x1+x2 = 1 != 0`, so the doubled-sum distractor `[x1+x2, y1+y2] = [1, 7]` is distinct from the answer; a midpoint-at-origin draw would null that rule per its `(x1+x2)==0 AND (y1+y2)==0` guard.)

**O5 `interpret_mx_c`.** Read gradient and intercept of `y = (1/2)x + 3`.
```
params = { task: "interpret_mx_c",
           L:{ m:{num:1,den:2}, c:{num:3,den:1} } }
```
Answer (`equation`, canonical `Line {m,c}`): canonical `{ m:{num:1,den:2}, c:{num:3,den:1} }`, display `"m = 1/2, c = 3"` (the two-field response: "Gradient m" = `1/2`, "y-intercept c" = `3`; a full equivalent equation such as `"y = (1/2)x + 3"` is accepted as an optional equivalent response). Vertical exclusion is structural (no point pair); `m = 1/2` is a finite reduced `Rational`, and `c = 3` lies inside the render window (P3 `ymin <= c <= ymax`).

**O6 `equation_from_graph`.** Graph of `y = -2x + 1` with two integer anchors on the line, e.g. `(0, 1)` and `(2, -3)`, both inside `W` and with distinct x.
```
params = { task: "equation_from_graph",
           L:{ m:{num:-2,den:1}, c:{num:1,den:1} },
           A1:{ x:{num:0,den:1}, y:{num:1,den:1} },
           A2:{ x:{num:2,den:1}, y:{num:-3,den:1} } }
```
Answer (full `y=mx+c`): canonical `{ m:{num:-2,den:1}, c:{num:1,den:1} }`, display `"y = -2x + 1"`. `A1.x != A2.x` holds; `c = 1` is inside the window.

**O7 `equation_from_two_points`.** Non-vertical line through `(-1, 4)` and `(3, -4)`: `m = (-4-4)/(3-(-1)) = -8/4 = -2`, `c = 4 - (-2)(-1) = 2`.
```
params = { task: "equation_from_two_points",
           P1:{ x:{num:-1,den:1}, y:{num:4,den:1} },
           P2:{ x:{num:3,den:1},  y:{num:-4,den:1} } }
```
Answer (full `y=mx+c`): canonical `{ m:{num:-2,den:1}, c:{num:2,den:1} }`, display `"y = -2x + 2"`. P2 holds (`x1 != x2`): gradient defined; a vertical-line draw would have been rejected by P2 and redrawn.

---

## 5. Ordered-pair answer representation and equivalence checker

This section fixes the canonical encodings of the three answer families and specifies their equivalence checkers. All comparisons are **exact** (via the `Rational` type), parse-then-compare in the established `core/answer-checking/rational-checker.ts` style; no floating point enters any decision. The `answer` object uses the schema fields verbatim: `type` (from the platform `answerType` enum), `canonical`, `display`, `accepts`, `equivalentForms`, `units?`.

### 5.1 Canonical encodings

**(A) Coordinate / ordered-pair answers** (O1 `read_point`, O2 `plot_point`, O4 `midpoint`).
- `answer.type`: fixed per task — **`"coordinate"` for O1 `read_point` and O2 `plot_point`** (a single plotted point), and **`"ordered-pair"` for O4 `midpoint`** (a derived pair). (The two enum values share the same `Point` encoding and checker; the per-task assignment is fixed so `answerTypes[]` is unambiguous — owner decision.)
- `answer.canonical`: a `Point` object `{ x: {num,den}, y: {num,den} }`, each component a reduced `Rational` (`den >= 1`).
- `answer.display`: the string `"(x, y)"` where each component is rendered by the rational display rule (integer when `den = 1`, else `"num/den"`); a single comma-space separates them, e.g. `"(-3, 4)"`, `"(1/2, 7/2)"`.

**(B) Gradient / intercept answers** (O3 `gradient_two_points`; the gradient and intercept slots of O5).
- `answer.type`: `"exact-rational"`, or `"integer"` when the value is integral.
- `answer.canonical`: a reduced `RatJson` `{num, den}`. **Integer => `den = 1`** (the schema's `allOf` rule forbids labelling a non-`den-1` value as `integer`, and requires `exact-rational` to carry `{num, den>=1}`; both are honoured).
- `answer.display`: the rational display rule above (`"2/3"`, `"-2"`).
- `answer.accepts`: `{ fraction: true }` by default; `decimal` is enabled only when the value terminates (`terminates(den)` from `core/answer-checking/rational-checker.ts` is true) **and** the objective permits a decimal form; `mixed` only when the objective permits it.

**(C) `y = m x + c` answers** (O5 value-pair; O6, O7 full equation).
- `answer.type`: `"equation"`.
- `answer.canonical`: a `Line` object `{ m: {num,den}, c: {num,den} }` — the *canonical (m, c) pair*, both reduced rationals. This is the single source of truth; any accepted input must normalise to this pair.
- `answer.display`: the normalised string `"y = m x + c"` produced by the **display-normalisation rules** below.

**Display-normalisation rules for `y = m x + c`** (deterministic, applied to the canonical `(m, c)`; the rules are applied in the fixed order 1 -> 2 -> 3 -> 4 so the emitted string is byte-identical in TS and Py):
1. **Gradient coefficient.** If `m = 1`: render `"x"` (drop the `1`, the `x1` rule). If `m = -1`: render `"-x"`. If `m` is a non-unit integer `k`: render `"kx"` (e.g. `"-2x"`). If `m` is a non-integer rational `p/q`: render `"(p/q)x"` with the reduced fraction in parentheses (e.g. `"(1/2)x"`).
2. **Zero gradient (the `x0` rule).** If `m = 0`: **omit the `x` term entirely**, rendering `"y = c"` (e.g. `"y = 3"`). The line is horizontal `y = c` (in scope; it is *not* a vertical line).
3. **Intercept sign / `+0` rule.** If `c = 0`: **omit the constant term**, rendering `"y = m x"` (e.g. `"y = 2x"`) — never `"+ 0"`. If `c > 0`: render `" + c"`. If `c < 0`: render `" - |c|"` (a subtraction, never `"+ -"`), with `c` shown by the rational display rule (the reduced fraction shown as `"num/den"`, e.g. `" - 3/4"`).
4. **Whitespace / case.** Exactly one space around the `+`/`-` joiner; the whole string is lowercase `y`, single spaces, e.g. `"y = -2x + 1"`, `"y = (1/2)x - 3"`, `"y = x"`, `"y = 3"`.

**Precedence for the degenerate line `y = 0` (`m = 0` AND `c = 0`, the x-axis — a legal horizontal through-origin line).** Rule 2 is applied **before** rule 3: when `m = 0` the x-term is omitted first, yielding the partial form `"y = c"`; rule 3 then renders the constant `c`. With `c = 0` this produces exactly the single canonical string **`"y = 0"`** (the `+0` omission of rule 3 does not strip the lone `"0"` constant once the x-term is already gone). Rule 3's `"y = m x"` branch (omit constant) is reachable only when `m != 0`; it is therefore never applied to the `m = 0` case, so `"y = 0x"` can never be produced. This single pinned string guarantees TS and Py agree byte-for-byte under the §5.3 `display re-derives from (m,c)` and `a11y-text-canonical` assertions.

The display string is *presentation only*; equivalence is decided on the canonical `(m, c)` rationals, never on the string.

### 5.2 Equivalence checkers

Three reusable checkers, each parse-then-compare-exact, mirroring `checkExactRational`'s contract (parse the student string into exact rationals, return `false` on any malformed/out-of-domain input, then compare canonical components for exact equality).

**(a) Ordered-pair / coordinate equality — `checkOrderedPair(input, canonical, opts)`.**
- Parse `input` of the form `"(a, b)"` (optional surrounding spaces; comma separator; each of `a`, `b` parsed by the existing `parseRationalInput` honouring the same `accepts` forms — fraction always, decimal/mixed only when enabled per component).
- **Order matters**: the result is `true` iff `a` equals `canonical.x` **and** `b` equals `canonical.y`, each by component-wise exact `Rational` equality (`num` and `den` both equal, on reduced values). `(b, a)` is rejected unless it happens to coincide componentwise.
- Reject: missing parentheses or comma, wrong arity (not exactly two components), empty/`NaN`/zero-denominator components, or any component form not permitted by `opts`.

**(b) Gradient / intercept equality.** Reuse the existing `checkExactRational(input, canonical, accepts)` (`core/answer-checking/rational-checker.ts`) unchanged for the O3 gradient and for each scalar slot of O5. It already accepts any equivalent fraction, the integer form for integral values, and decimal/mixed only when enabled — exactly the equivalence required here. No new infrastructure.

**(c) `y = m x + c` equivalence — `checkLineEquation(input, canonical, opts)`.**
- **Goal:** accept *any* input that normalises to the same canonical `(m, c)` exact rationals.
- **Why new infrastructure is required.** The existing `core/exact-math/linexpr.ts` is strictly **single-variable** (`LinExpr = a·x + b`, `normalize` -> `A·x + B = 0`, `solveLinear` solves for one unknown `x`). It cannot represent or reduce a two-variable `{x, y}` equation, nor extract `(m, c) = (-B/A, -C/A)` from a bivariate form. The bivariate-rearrangement guarantee below is therefore **not** delivered by `solveLinear`; it requires a new bivariate reducer, proposed in 5.3.
- **Reduction.** `checkLineEquation` parses the student's linear equation as `lhs = rhs` over the two variables `{x, y}`, moves it to the bivariate canonical form `A·y + B·x + C = 0` (all coefficients exact `Rational`), and **rejects when the `y`-coefficient `A = 0`** (no unique `y`). When `A != 0` it forms `(m, c) = (-B/A, -C/A)` as exact rationals and compares to `canonical.m`, `canonical.c` by exact `Rational` equality (`num` and `den` both equal). The single-variable `LinExpr` is reused only for parsing each side's per-variable sub-expressions; the two-variable reduction and the unique-`y` solvability are properties of the **new** module (5.3), not of `solveLinear`.
- **Accepted input forms** (all map to identical canonical `(m, c)`):
  - The slope-intercept form `y = m x + c` in any display variant (`"y=2x+1"`, `"y = 2x + 1"`, with `1·x` written as `x`, `+0` omitted or written, coefficient as a reduced or *unreduced* fraction such as `"y = (2/4)x + 1"` which reduces to `1/2`).
  - **Rearranged equivalent forms** that are still linear and solvable for a unique `y`: e.g. `"2x + 1 = y"`, `"y - 1 = 2x"`, `"y - 2x = 1"`, `"y - 2x - 1 = 0"`, and constant-multiple forms like `"2y = 4x + 2"`. Each is parsed as `lhs = rhs` over `{x, y}`, moved to `A·y + B·x + C = 0`, and solved for `y` (requires `A != 0`); the resulting `(m, c) = (-B/A, -C/A)` are exact rationals compared to canonical. **Multiple equivalent `y=mx+c` forms therefore collapse to one canonical `(m, c)`** — this is the core equivalence guarantee (verified on the worked examples: O3 `m = 2/3`, O4 `mid = (1/2, 7/2)`, O7 `m = -2, c = 2`; and `"2y = 4x + 2"` -> `A = 2, B = -4, C = -2` -> `(m, c) = (2, -1)`... i.e. `(-B/A, -C/A) = (2, 1)` for `y = 2x + 1`).
- **Rejected input:**
  - **Vertical / undefined-gradient input** (`"x = 3"`, `"2x = 6"`, or any rearrangement whose `y`-coefficient `A = 0`): the reduction has no unique `y`, the checker reports `A = 0` and returns `false`. Vertical lines are out of scope and are never a correct answer (consistent with P2 in 4.4).
  - Non-linear input (any term of degree > 1 in `x` or `y`) — unrepresentable by the bivariate linear type, rejected by construction.
  - Equations with no `x`/`y`, with a third variable, malformed syntax, or that reduce to `0 = 0` / `0 = k` (degenerate) — rejected.
- For the **O5 value-pair** variant the canonical answer is the same `Line` `{m, c}`; the checker additionally accepts a structured two-field response (gradient and y-intercept entered separately) by comparing each field with `checkExactRational` against `canonical.m` and `canonical.c` respectively.

### 5.3 Proposed reusable infrastructure (flag for Section 15)

Three new modules are proposed as **domain-independent, reusable infrastructure** alongside the existing `core/answer-checking/rational-checker.ts` and `core/exact-math/linexpr.ts` (flagged here for the Section-15 infrastructure inventory; specified, not implemented in this proposal):

- **`core/exact-math/linexpr2.ts`** — a new **bivariate** linear-expression type `BiLinExpr` over `{x, y}` with exact `Rational` coefficients `(A_y, B_x, C)`, plus `parseBiLinear(lhs, rhs)` -> the reduced `A·y + B·x + C = 0` form and `solveForY` that returns `(m, c) = (-B/A, -C/A)` or `null` when `A = 0`. This is the module that actually delivers the rearranged-form collapse and the vertical-line (`A = 0`) rejection; it **extends** the single-variable `LinExpr` discipline (which it reuses for per-side sub-parses) rather than reusing `solveLinear`. Byte-parity Python counterpart `oracle/spi_oracle/linexpr2.py`. (Statistics inherits the `y=mx+c` checker, so this is genuinely shared infrastructure.)
- **`core/answer-checking/ordered-pair-checker.ts`** — `parseOrderedPairInput(input, accepts)` and `checkOrderedPair(input, canonical: Point, accepts)`; component-wise exact `Rational` equality, order-significant; built on the existing `parseRationalInput`. Reusable by any future family with point/coordinate answers (vectors deferred but share the parse shape).
- **`core/answer-checking/line-equation-checker.ts`** — `parseLineEquation(input)` -> normalised `(m, c)` exact rationals or `null`, and `checkLineEquation(input, canonical: Line, accepts)`; built on the new `core/exact-math/linexpr2.ts` so two-variable linearity and unique-`y` solvability are guaranteed by construction and vertical/undefined-gradient input is rejected deterministically (`A = 0 ⇒ false`).

All three carry **TS/Python parity** (oracle counterparts under `oracle/spi_oracle/`) and golden test fixtures, so the family's parity and 10,000-seed stability sweeps cover answer-checking as well as generation. The validator's independent route recomputes each answer from `params` (gradient via `(y2-y1)/(x2-x1)`, midpoint via `((x1+x2)/2,(y1+y2)/2)`, equation via `BiLinExpr`/`linexpr2`) and asserts equality with the stored `answer.canonical` (closure-agreement), and asserts the canonical `display` re-derives from `(m, c)` byte-for-byte (including the pinned `"y = 0"` string from 5.1).


---

## 6. Cartesian SVG renderer contract

This section specifies the **canonical, monochrome-authoritative** Cartesian renderer for `gen.geometry.coordinate-lines` v1.0.0. It mirrors the discipline already shipped in `domains/geometry/angles.ts` / `oracle/spi_oracle/geometry.py` (`canonicalSvg` / `canonical_svg`): a single source of truth (`params`), all coordinates produced as **integers** by `gridRound(num, den)` round-half-up over exact `Rational`/`Fraction`, **no runtime trig and no floats in the emitted geometry**, and a hand-serialised SVG that is **byte-for-byte identical between TypeScript and the Python oracle**. The premium colour layer (the palette tokens `--cx-series-1..N`, `--cx-axis`, `--cx-grid-major`, `--cx-grid-minor`, `--cx-pt-core`, `--cx-pt-outline`, `--cx-halo`, `--cx-bg`) is a **presentation overlay** over this same canonical geometry; colour **never carries meaning alone**.

> **The canonical monochrome SVG is AUTHORITATIVE.** Every downstream gate (parity fixtures, exporters, the independent validator of §8, the bank round-trip) re-derives, re-serialises, and byte-compares **this** string, and the HTML exporters (`exporters/html/{worksheet,answer-key,solutions}.ts`) inline **this** `media[0].svg`. The premium/accessible modes are presentation-time re-renders from the `media[0].spec.premium` style contract over the **identical integer geometry**; they add no new positional information, and the viewer's chosen mode/theme is a preference that never changes the canonical item (§16.1 a.6). See §16 (premium colour layer & token contract) for the token mapping and the `colour-is-presentation-only` / `monochrome-is-authoritative` gates.

### 6.1 Inputs and the single source of truth

The renderer is a pure function `cartesianSvg(model, alt, title, desc) -> string`, where `model` is built **only** from `params` (the same object that feeds the prompt, answer, solution, and accessibility text). `model` carries, per task:

- `points[]` — named lattice points `{name, x, y}` in **math coordinates** (exact **integers** from `params`).
- `lines[]` — at most one straight line per item, given canonically as `y = m·x + c` with `m` an exact `Rational` (**finite**, GCD-reduced) and `c` an exact `Rational` (vertical lines `x = a` are **deterministically excluded** — see §8 and the hard constraints).
- `guides[]` — helper annotations, drawn **only in the scaffolded student variant** and **never** carrying the assessed value: an **optional unlabelled dashed step** for a *scaffolded* `gradient_two_points` (the standard version has no rise/run guide at all; signed rise/run labels appear only in the worked solution); dashed **axis projections** for *lower-band* `read_point` (higher-band questions omit projection guides so the student reads the axes independently); nothing for tasks that need none. The scaffolded-vs-unscaffolded distinction contributes to the difficulty profile (§10).
- `labels[]` — point labels (e.g. `A`, `B`, `P`), a **neutral line label** (such as `l`) for `equation_from_graph` (**never** the equation, the numerical gradient, or the numerical intercept), and answer-free value callouts. **No label ever reveals the assessed answer** (the equation, gradient, intercept, or midpoint); see §6.9 and the no-leakage rules below.

The window (`xmin, xmax, ymin, ymax`), the unit scale `U`, and the integer centering offsets `offX, offY` come from §7 and are part of `model`; the renderer **never recomputes** them, so Py and TS consume one identical integer description.

### 6.2 Canvas, frame, and the single projection of record

- `viewBox` is fixed at **`0 0 1000 700`** (`VIEW_W = 1000`, `VIEW_H = 700`), identical to the angles family.
- A **single unit length `U`** (integer px per math unit) is **EQUAL on both axes** (§7 chooses `U`, the window, and `offX/offY`). The math frame is **+y up**; the SVG frame is **+y down**, so every y is negated on projection.
- **There is exactly one projection of record, defined in §7.2.** It keeps the centering offset and the unit-scaled term **inside one exact `Rational`** and applies a **single** `gridRound` at the end — exactly as `_layout` does in `oracle/spi_oracle/geometry.py` (`nx = Fraction(CX) − Fraction(bw)·s/2 + Fraction(x−minx)·s; out = grid_round(nx.numerator, nx.denominator)`) and as `layout()` does in `domains/geometry/angles.ts`. **This section commits no separate projection formula; see §7.2.** Centering offsets are **never** pre-rounded and re-added (that would be a forbidden second rounding). For integer `(x, y)` and integer `U` the unit-scaled term is already integer, so the only rounding is the single `gridRound` over the combined `Rational`; for fractional values (midpoints, clipped endpoints with fractional `t`) the same single `gridRound` runs over the whole exact sum. No `Math.*`, no `sin`/`cos`, no float division survives into the string.

### 6.3 Style block and the `cx-*` class vocabulary

Exactly as `.gl/.ga/.gx` encode a stroke **hierarchy** in the angles family, the `cx-*` classes encode the Cartesian layer hierarchy. The `<style>` block is a single committed constant string (byte-identical Py/TS), monochrome greys only:

| class | role | stroke / fill | width | dash | rank |
|---|---|---|---|---|---|
| `.cx-axis` | x- and y-axis lines + arrowheads | `#111` | `3` | — | strongest |
| `.cx-tick` | tick marks on axes | `#111` | `2` | — | — |
| `.cx-ticklbl` | numeric tick labels | `#333` text | — | — | — |
| `.cx-grid-major` | integer-unit gridlines | `#888` | `1.25` | — | major |
| `.cx-grid-minor` | sub-unit gridlines | `#bbb` | `0.75` | — | minor (weakest) |
| `.cx-line` | the plotted straight line | `#111` | `3` | — | = axis weight, distinct by being oblique/clipped |
| `.cx-pt-outline` | point halo (drawn first) | `#fff` fill, `#111` stroke | `4` | — | — |
| `.cx-pt-core` | point core (drawn over outline) | `#111` fill | — | — | — |
| `.cx-lbl` | point / equation text labels | `#111` text | — | — | — |
| `.cx-guide` | dashed rise/run + axis projections | `#555` | `1.5` | `5 4`, round-cap | secondary (annotation) |

The **invariant** (asserted by `axes-stronger-than-grid` and `major-grid-stronger-than-minor` in §8): `width(.cx-axis) > width(.cx-grid-major) > width(.cx-grid-minor)` and `.cx-axis` is darker than `.cx-grid-major`, which is darker than `.cx-grid-minor` (distinction by **width and greyscale**, never opacity alone). `.cx-guide` is **strictly thinner than every geometry stroke** and dashed + round-capped, so a guide can never be misread as the line, an axis, or a gridline (the cx- analogue of the `leader-style-distinct-from-geometry` check). The premium layer must preserve this same width-and-dash hierarchy — re-asserted in colour by the §16 `grid-hierarchy-preserved` gate.

### 6.4 Deterministic element order

The serialiser emits elements in **one fixed order** so the byte stream is canonical (matching the angles family's `segs → arcs → ticks → leaders → texts → caption` discipline). Painter's order is also semantic: background-most first, annotations and text last.

1. `<svg …>` root: `xmlns`, `role="img"`, `aria-label="{esc(alt)}"`, `viewBox="0 0 1000 700"`. **No `id` attribute and no `url(#…)` reference anywhere** in the canonical SVG (safe multi-item worksheet export); the premium layer obeys the same rule under the §16 `no-global-ids` gate.
2. `<title>{esc(title)}</title>` then `<desc>{esc(desc)}</desc>`.
3. `<style>{CX_STYLE}</style>` (committed constant).
4. **Minor gridlines** (`.cx-grid-minor`), left→right then bottom→top, ascending integer pixel order.
5. **Major gridlines** (`.cx-grid-major`), same ordering.
6. **Axes** (`.cx-axis`): x-axis, then y-axis, each with an arrowhead `<path>` at its positive end and an origin marker at `(0,0)` (the origin is always inside the window by §7.1).
7. **Ticks** (`.cx-tick`) then **tick labels** (`.cx-ticklbl`), x-axis ascending then y-axis ascending.
8. **Guides** (`.cx-guide`) — clipped/already-integer dashed segments (rise/run; projections).
9. **The line** (`.cx-line`) — a single `<line>` clipped to the viewport per §7.
10. **Points**: for each point, `.cx-pt-outline` then `.cx-pt-core` (halo under core), in `model.points[]` order.
11. **Labels** (`.cx-lbl`): the neutral line label (e.g. `l`) if any — never the equation — then placed point/value labels in `model.labels[]` order.
12. `</svg>`.

This is the **canonical (monochrome) order and it is unchanged in every mode**. The premium mode is purely **additive**: decorative `.cx-halo` elements are emitted **immediately before** the `.cx-line` / `.cx-pt-core` they back (lower z, never carrying geometry semantics); stripping all `.cx-halo` elements yields a byte string **identical** to this canonical SVG (the §16 `glow-outside-stroke` gate). Print/accessible modes emit no halo. All numeric attributes are integers; text is XML-escaped with the same `esc` map as the angles family (`& < > " '`).

### 6.5 Axes, arrowheads, origin, ticks, tick labels

- **Axes** span the full clipped extent of the window (the x-axis is the projection of `y = 0` clipped to the viewport; the y-axis is `x = 0` clipped); the origin is inside the window by construction (§7.1), so both axes always render. Each axis ends in an **arrowhead** at its positive direction — a small filled triangle whose three vertices are computed from the committed integer **direction table** `core/geometry/dir-table.json` (`R = 10000`, the same no-runtime-trig source the angles family uses), so arrowheads are integer polygons, never trig.
- **Origin marker**: a short crisp marker at the projected origin; the tick label `0` is emitted once (on the x-axis) to avoid a doubled `0`.
- **Ticks** sit at **every integer unit** within the window on each axis (length `TICK_LEN` px, centred on the axis). **Tick labels** are the integer unit values; they are always integers (asserted by `tick-labels-integer`). To avoid clutter at high unit counts the renderer thins **labels** (not ticks) by a deterministic **integer-ceil** stride

  ```
  k = floor( (unitsOnAxis + MAX_LABELS_PER_AXIS − 1) / MAX_LABELS_PER_AXIS )   // integer ceil; never Math.ceil(float)
  ```

  with the pinned constant `MAX_LABELS_PER_AXIS = 11` (§7.6), computed in integer arithmetic identically in Py/TS. `0` is **always** labelled and the stride is applied **symmetrically about the origin**, so the emitted label **set** is identical in both languages.

### 6.6 Gridlines (major vs minor)

- **Major** gridlines are drawn at **every integer unit**. **Minor** gridlines are drawn at **half-units only** (`0.5`-unit spacing) — chosen so minor coordinates remain exactly representable; **there is NO quarter-unit grid in v1.0.0**. The half-unit minor grid is shown **only when `U ≥ 32`** and is **suppressed when `U < 32`** (at small unit scales the half-unit lines would crowd the figure, so only the integer major grid renders). This `U ≥ 32` threshold is a committed constant, applied identically in Py/TS. Each minor coordinate projects through the **single §7.2 `gridRound`**, so its pixel is deterministic for any `U` (even or odd). Minors are emitted **before** majors so majors paint over them, and the width/greyscale hierarchy of §6.3 guarantees `axes ≫ major ≫ minor` visually and by the §8 checks.

### 6.7 Points, lines, labels, and guides — distinct treatments

- **Points** use a two-element idiom: a white-filled outline disc (`.cx-pt-outline`) drawn first, then a solid core (`.cx-pt-core`). This gives a crisp dot that stays legible where it crosses a gridline or the line (the halo separates it from the background), exactly analogous to the angles family layering ticks/arcs distinctly.
- **The line** is a single `<line>` **clipped to the viewport rectangle** by §7's exact-rational Liang–Barsky; endpoints are exact then `gridRound`-ed once each, so the drawn segment is integer-valued and provably inside the committed clip box (asserted `line-clipped-within-viewport`, §7.2/§7.4). A clip that collapses to a single point (`t0 ≥ t1`) is rejected and the param loop redraws (§7.5), so a zero-length `<line>` can never be emitted.
- **Guides** are dashed `.cx-guide` segments, present **only in scaffolded student variants** and **never in the standard variant**:
  - For `gradient_two_points`, the **standard** version draws **no rise/run guide**. A **scaffolded** version may draw a single **unlabelled** dashed right-angled step (run leg + rise leg) between the two lattice points — but the **signed integer rise/run lengths are NOT shown in the student figure**; they appear **only in the worked solution**. (The scaffolded-vs-unscaffolded choice raises/lowers difficulty, §10.)
  - For `read_point`, dashed **axis projections** (from the plotted point down to the x-axis and across to the y-axis) appear **only in lower-band** items; **higher-band** `read_point` items **omit the projection guides** so the student reads the axes independently.
  - Guides are visually secondary and never coincide with an axis, gridline, or the line.
- **`plot_point` student figure is a BLANK labelled grid:** the target point is **NOT shown** anywhere in the student SVG (no marker, no label, no guide), and the accessibility text must **not** state that the point is already plotted. The correct point appears **only** in the answer key / worked solution / teacher-validation overlay, derived deterministically from the same `params`.
- **`midpoint` student figure shows the two endpoints only:** the **midpoint is NOT plotted or labelled** in the student figure; it appears only in the answer key / worked solution.
- **`equation_from_graph` student figure never reveals the answer:** the drawn line carries only a **neutral line label such as `l`** (or no label); it **never** shows `y = mx + c`, the numerical gradient, the numerical intercept, or any answer-identifying label. The equation appears **only** in the answer key and worked solution.
- **Labels** carry point names (`A`, `B`, `P`), the neutral line label (`l`) for `equation_from_graph`, and answer-free value callouts. All are placed by §6.8. No label encodes the assessed gradient, intercept, midpoint, or equation.

### 6.8 Deterministic label placement (integer collision-avoidance, finite ladder)

Label placement reuses the **integer collision-avoidance** machinery of the angles family verbatim in spirit (`boxMake`, `boxInCanvas`, `boxesClear`, `ptBoxD2`, `segClearBox`, `ptSegClear`, the `orient`/`segIntersect` predicates) — **no floats**, exact squared-distance comparisons, deterministic candidate scan over a **committed finite ladder**. The contract:

- Each label has an integer bounding box from a committed per-character advance table plus ascent/descent (the cx- analogues of `LBL_CHARW`/`LBL_ASC`/`LBL_DESC`).
- A point label is tried over a **fixed, committed candidate ladder** — the offset directions in the committed order `[NE, NW, SE, SW]`, then radially outward in steps of `LBL_STEP` px up to a committed maximum radius `R_LABEL_MAX` (the cx- analogues of the angles family's `LBL_STEP = 14`, `R_LABEL_MAX = 480`). The scan is **bounded** and accepts the **first** candidate (in this committed order) whose box (a) stays inside the canvas margin `CANVAS_M`, (b) clears every **point** by ≥ `LBL_CLEAR` px, (c) clears the **axes**, (d) clears every **tick label**, (e) clears the **line** and any **guide**, and (f) clears every **already-placed label**. Because the ladder is finite and the order is committed, "accept the first feasible candidate" is fully deterministic and the loop **provably terminates**.
- If the ladder is exhausted for any label (no feasible candidate), the renderer returns `null` and the **param loop redraws** deterministically (the cx- analogue of `labelsOk` gating `guardsOk`). This guarantees the published figure has zero label collisions, enforced independently by the §8 checks `point-label-clearance` and `line-label-clearance`.

### 6.9 Accessibility text (information-equivalent, never the answer)

`title`/`desc`/`aria-label` and `accessibility.{spokenMath, altText, longDescription}` are built from the **displayed givens only** and are information-equivalent to the figure — they state the plotted points / the drawn line's visible features but **never** the gradient, intercept, midpoint, or equation being assessed (the cx- analogue of `a11y-no-answer-in-text`). For `read_point` the only figure-encoded value **is** the given plotted point itself, which is a stated given, not the assessed deduction. **For `plot_point` the student figure is a blank labelled grid: the target point is NOT plotted, so the accessibility text describes only the empty grid and axes and must NOT state that the point is already plotted** (the point appears only in the answer-key/solution overlay). **For `midpoint` the accessibility text states the two endpoints but never the midpoint;** for `equation_from_graph` it describes the drawn line (the neutral label `l`, its visible lattice crossings) but never the gradient, intercept, or equation. `accessibility.nonColorIndicators` is `true` because the canonical layer is monochrome and every distinction (point vs line vs guide vs grid) is carried by **shape, weight, and dash**, not colour. A `media[].dataTableFallback` lists the visible givens (plotted coordinates / two endpoints / the visible line crossings) in the same neutral, answer-free way. The figure is emitted **to scale** by the equal-`U` construction (§7), so **`media[].toScale = true`** and **no "NOT TO SCALE" label is emitted** (the inverse of the angles family's `not-to-scale` discipline); this is asserted by the §8 `figure-to-scale` check.

---

## 7. Viewport and clipping algorithm

This section gives a **fully deterministic** algorithm — identical integers in Python and TypeScript — that (a) chooses a data window, (b) chooses the single equal-scale unit `U` and the centering offsets `offX/offY`, (c) defines the **one projection of record**, and (d) clips the plotted line to the viewport with exact-rational arithmetic. All decisions are functions of `params` only; nothing depends on float rounding, locale, or iteration order, so the **same window and the same projected pixels are guaranteed across Py/TS** (asserted by `equal-axis-scale` and `svg-realises-data` in §8).

### 7.1 Data window from the lattice points and origin (integers only)

Let `S` be the **integer** set on which the window is built: every point in `model.points[]` (all lattice points, exact integers) **plus the origin `(0,0)`**. **The line's clip points never enter `S`** — they are computed only after `U` is fixed (§7.3) and are used solely for drawing. `S` is therefore an integer-valued list in a **deterministic order** (`model.points[]` order, then origin), so `min`/`max` over it agree byte-for-byte in Py and TS (the angles `Math.min(...xs)` / Python `min(xs)` pattern, but here over integers only — no fractional `c` ever reaches `min`/`max`). Compute the raw extent:

```
xmin0 = min over S of x ,  xmax0 = max over S of x
ymin0 = min over S of y ,  ymax0 = max over S of y
```

Since the origin is in `S`, `xmin0 ≤ 0 ≤ xmax0` and `ymin0 ≤ 0 ≤ ymax0` automatically. **Pad by an integer margin `M ≥ 1` unit** (so no required point sits on an edge and the axes always render):

```
xmin = xmin0 − M ,  xmax = xmax0 + M
ymin = ymin0 − M ,  ymax = ymax0 + M
```

All four bounds are integers (lattice points and `M` are integers), guaranteeing integer ticks and integer-unit gridlines. Let

```
Wx = xmax − xmin   (window width in units, ≥ 2)
Wy = ymax − ymin   (window height in units, ≥ 2)
```

### 7.2 Choosing `U`, the centering offsets, and the projection of record

Reserve an integer drawing inset `PAD` px inside the `1000 × 700` viewBox (for arrowheads/labels). The usable pixel box is `Aw = VIEW_W − 2·PAD`, `Ah = VIEW_H − 2·PAD`. Choose the **largest integer `U`** that fits both axes at **equal scale**:

```
U = min( floor(Aw / Wx) , floor(Ah / Wy) )
```

`U` is a pure integer `min`/`floor`, identical in both languages. Centre the window by distributing the **total** pixel slack on each axis as an **exact `Rational`** (never pre-rounded):

```
offX = Rational( VIEW_W − Wx·U , 2 )      // exact half-slack, kept rational
offY = Rational( VIEW_H − Wy·U , 2 )      // exact half-slack, kept rational
```

The **single projection of record** for a math point `(x, y)` with exact `Rational` components is one exact sum, rounded **exactly once**:

```
px = gridRound( ( offX + Rational(x − xmin)·U ).num , ( offX + Rational(x − xmin)·U ).den )
py = gridRound( ( offY + Rational(ymax − y)·U ).num , ( offY + Rational(ymax − y)·U ).den )   // +y-up negated
```

This is the **only** projection; §6.2 commits none of its own and cross-references here. The construction mirrors `_layout` (`oracle/spi_oracle/geometry.py`) and `layout()` (`domains/geometry/angles.ts`): the centering offset stays **inside** the `Rational` and there is **exactly one** `gridRound` over the combined sum, so no second round-half-up can shift a `.5`-boundary pixel. For integer `(x, y)` and integer `U` the `Rational(x − xmin)·U` term is integer and only the half-slack rounds; for the **fractional** clipped endpoints of §7.4 (e.g. `t = 1/4`) the whole sum is fractional and still rounds once. Python `Fraction` and TS `Rational`/BigInt produce the identical byte stream.

**Projection origin and clearance, pinned.** Because `U = min(floor(Aw/Wx), floor(Ah/Wy))` is computed against `Aw = VIEW_W − 2·PAD` (resp. `Ah`), we have `Wx·U ≤ Aw = VIEW_W − 2·PAD`, hence the centered offset `offX = (VIEW_W − Wx·U)/2 ≥ PAD`. The two horizontal window corners therefore project to `px = round(offX) ∈ [PAD, VIEW_W − PAD]` (left, `x = xmin`) and `px = round(offX) + Wx·U ≤ VIEW_W − PAD` (right, `x = xmax`); symmetrically in `y`. So **every** projected window-edge pixel — including a clipped line endpoint at a window edge — lies in the committed clip box **`[PAD, VIEW_W − PAD] × [PAD, VIEW_H − PAD]`**, which is where `PAD`'s arrowhead/label reserve actually lives. The §8 check `line-clipped-within-viewport` asserts endpoints in **this PAD-inset box**, not the raw `[0,1000]×[0,700]`, so the clearance `PAD` reserves is genuinely enforced.

**`U_MIN` reachability (statically safe for v1.0.0).** With the committed sampling domain `COORD_MAX_X = COORD_MAX_Y = 10` (§4.2) and data margin `DATA_MARGIN_UNITS = M = 1`, the largest admissible render window is `[−11, 11]²`, i.e. `Wx = Wy = 22`. Committing `PAD = 40` gives `Aw = 920`, `Ah = 620`, so `U = min(floor(920/22), floor(620/22)) = min(41, 28) = 28 ≥ U_MIN` for **every** admissible spread (smaller spreads only raise `U`). Therefore `U < U_MIN` is **statically unreachable** in v1.0.0 with the pinned `U_MIN = 24` (§7.6): `U = 28 ≥ 24`, so the generator never needs the "redraw on tiny `U`" branch, and the 10,000-seed sweep can never throw on scale. (The redraw branch is retained defensively, but is provably dead for the committed constants.)

### 7.3 Line endpoints feeding the window (no fixed-point loop)

A line `y = m·x + c` is unbounded, so its drawn extent is the **two points where it meets the window rectangle**. There is **no circularity**: the window is computed from the **integer lattice points + origin alone** (§7.1) — these always exist for every task (the two given points for O3/O7; the read-off lattice anchors for O5/O6) — `U` and `offX/offY` are fixed in §7.2, and **then** the line is clipped (§7.4) to that already-final rectangle. The clip endpoints are used **only for drawing** and **never re-enter `S`** or re-expand the window. Thus the window is a pure function of the integer lattice points + origin + `M`, identical Py/TS; no fractional value and no fixed-point iteration is ever involved.

### 7.4 Exact-rational Liang–Barsky clip

The infinite line is expressed through two exact endpoints at the window's left and right math bounds: `P0 = (x0, y0)` with `x0 = xmin`, `P1 = (x1, y1)` with `x1 = xmax`, and `y = m·x + c` as exact `Rational` at each. (`Δx = x1 − x0 = Wx ≠ 0` because vertical lines are excluded — §7.5 / §8 — so the x-bound parameterisation is always well-defined.) Clip to the math rectangle `[xmin, xmax] × [ymin, ymax]` (equivalently the pixel clip box after projection). Let `Δx = x1 − x0`, `Δy = y1 − y0`. For the four edges define `(p, q)`:

```
edge left   : p1 = −Δx , q1 = x0 − xmin
edge right  : p2 = +Δx , q2 = xmax − x0
edge bottom : p3 = −Δy , q3 = y0 − ymin
edge top    : p4 = +Δy , q4 = ymax − y0
```

Initialise `t0 = 0`, `t1 = 1` (exact `Rational`). For each `k`:

- If `p_k = 0`: the segment is **parallel** to that edge — if `q_k < 0` the line is wholly outside (**reject and redraw**); otherwise the edge imposes no bound.
- If `p_k < 0`: `r = q_k / p_k` (exact `Rational`); if `r > t1` reject; else `t0 = max(t0, r)`.
- If `p_k > 0`: `r = q_k / p_k`; if `r < t0` reject; else `t1 = min(t1, r)`.

All comparisons are exact `Rational` cross-multiplications (`cmpAbs`-style), so `t0`, `t1` are exact. **Degenerate-clip guard:** after the four edges, if `t0 ≥ t1` (the visible segment is empty or a single corner point), **reject the candidate and redraw** — the figure has no drawable line segment (asserted as part of P3 / `line-clipped-within-viewport`, so a corner-touch line never emits a zero-length `<line>`). Otherwise the clipped endpoints are

```
Cx0 = x0 + t0·Δx ,  Cy0 = y0 + t0·Δy        (exact Rational)
Cx1 = x0 + t1·Δx ,  Cy1 = y0 + t1·Δy        (exact Rational)
```

Project each with the §7.2 projection of record (a **single** `gridRound` over the combined exact `Rational`), yielding integer pixel endpoints provably within `[PAD, VIEW_W − PAD] × [PAD, VIEW_H − PAD]`.

**Acceptance predicate making the parallel branch a proven invariant.** For a horizontal line (`m = 0`, `Δy = 0`) the bottom/top edges are the parallel case, and `q3 = y0 − ymin = c − ymin`, `q4 = ymax − y0 = ymax − c`. These are `≥ 0` **iff `ymin ≤ c ≤ ymax`**. We therefore make this an explicit acceptance predicate, extending P3 in §4.4: **for every line task, the generator asserts `ymin ≤ c ≤ ymax` AND the clipped segment is non-empty (`t0 < t1`) BEFORE acceptance**; otherwise it redraws. For O5/O6 the lattice anchors lie on the line, so `c` is inside the window by construction; for O3/O7 the predicate is checked directly. With this predicate the §7.5 "horizontal line clips to full width" row is a **theorem**, not an assumption, and the `q < 0` parallel-reject branch is provably unreachable for accepted items.

### 7.5 Edge cases (all handled exactly, no float)

| case | handling |
|---|---|
| **negative / fractional math coords** | window bounds and projection are exact `Rational`; lattice points are integers, fractional values (midpoints, clipped endpoints) round once via the §7.2 `gridRound`. |
| **horizontal line `m = 0`** | `Δy = 0`; left/right edges set `t0,t1` over the full width; top/bottom edges are parallel with `q3 = c − ymin ≥ 0`, `q4 = ymax − c ≥ 0` **guaranteed by the acceptance predicate `ymin ≤ c ≤ ymax`** → clips to the full width. |
| **through-origin (`c = 0`)** | no special case; origin already in window; line passes the origin marker, which paints **under** the line per §6.4 order. |
| **steep line** (large `|m|`) | endpoints taken at `x = xmin, xmax`; if the line exits through top/bottom first, `t0/t1` tighten there; clipped endpoints land on the top/bottom edges exactly. |
| **point on the boundary** | the margin `M ≥ 1` keeps required points off the rectangle edge; a clipped line endpoint **on** an edge is included (Liang–Barsky `≤`/`≥`, exact `Rational`), then projected and `gridRound`-ed onto the integer border pixel of the PAD-inset clip box. |
| **corner-touch / zero-length clip** | if `t0 ≥ t1` after clipping, the visible segment is empty or a single point → **reject and redraw**; no zero-length `<line>` is ever emitted. |
| **vertical line `x = a`** | **excluded by construction** (no `y = mx+c` form; for O5/O6 a finite reduced `m` is drawn, for O3/O7 `x1 ≠ x2` is enforced — §8 `vertical-line-excluded`); the clipper is therefore only ever invoked on non-vertical lines, so `Δx = Wx ≠ 0` and the x-bound parameterisation is always well-defined. |

Because every quantity above is an exact `Rational`/integer and `U`, `xmin`, `ymax`, `offX`, `offY` are shared in `model`, the window and every clipped, projected pixel are **identical in Python and TypeScript**.

### 7.6 Pinned renderer constants

The following renderer constants are **pinned** for v1.0.0 (owner decision). They are committed constants shared byte-identically by the Python oracle and the TypeScript renderer. They are revisable **only before the fixtures freeze**, and only if the visual audit (§13) shows a clear problem; once fixtures freeze they are immutable.

| Constant | Value | Role |
|---|---|---|
| `VIEW_W` | `1000` | viewBox width (px) |
| `VIEW_H` | `700` | viewBox height (px) |
| `PAD` | `40` | drawing inset reserved for arrowheads/labels (px) |
| `U_MIN` | `24` | minimum admissible unit scale (px/unit); statically unreachable in v1.0.0 (§7.2) |
| `DATA_MARGIN_UNITS` (`M`) | `1` | integer unit margin padded around the data extent (§7.1) |
| `MAX_LABELS_PER_AXIS` | `11` | tick-label thinning ceiling per axis (the §6.5 integer-ceil stride; `MAX_LABELS = MAX_LABELS_PER_AXIS`) |
| `LBL_CLEAR` | `8` | minimum label-box clearance (px), used by §6.8 placement and the §8 clearance checks |

These are **render-window / renderer** constants. They are kept conceptually distinct from the **sampling-domain** bounds `COORD_MAX_X = COORD_MAX_Y = 10` of §4.2 (which limit the *drawn coordinates*, not the rendered viewport — see §4.2). The gradient denominator set is likewise pinned at `{1, 2, 3, 4}` and is **not expanded in v1.0.0** (§4.2).

---

## 8. Solver and independent-validator design

### 8.1 Per-task solvers (exact, second-route-friendly)

Each task has a pure `solve(params)` returning the canonical answer in the schema shape, computed with exact `Rational`/`Fraction` (never float). The answer `type` values are drawn from the existing `answer.type` enum (no schema change): `ordered-pair`/`coordinate`, `exact-rational`/`integer`, `equation`.

| task | objective | `solve` (exact) | `answer.type` | `answer.canonical` shape |
|---|---|---|---|---|
| `read_point` (O1) | `SPI.MIDDLE.GEO.COORD.READ_POINT.01` | read plotted `(x, y)` from `params` | `coordinate` | `{x:{num,den}, y:{num,den}}` (den = 1 for lattice) |
| `plot_point` (O2) | `SPI.MIDDLE.GEO.COORD.PLOT_POINT.01` | target `(x, y)` from `params` (overlay-only; student figure blank) | `coordinate` | `{x, y}` integers |
| `gradient_two_points` (O3) | `SPI.MIDDLE.GEO.COORD.GRADIENT_TWO_POINTS.01` | `m = Rational(y2 − y1, x2 − x1)` with **`x2 ≠ x1` enforced** | `integer` (when `den = 1`) \| `exact-rational` | `{num, den}` (den ≥ 1, GCD-reduced) |
| `midpoint` (O4) | `SPI.MIDDLE.GEO.COORD.MIDPOINT.01` | `(( x1+x2)/2, (y1+y2)/2)` exact | `ordered-pair` | `{x:{num,den}, y:{num,den}}` (den ∈ {1,2}) |
| `interpret_mx_c` (O5) | `SPI.MIDDLE.GEO.COORD.INTERPRET_MX_C.01` | read `m` and `c` from `y = m x + c` in `params` | `equation` (canonical `Line {m,c}`; two-field response) | `{m:{num,den}, c:{num,den}}` |
| `equation_from_graph` (O6) | `SPI.MIDDLE.GEO.COORD.EQUATION_FROM_GRAPH.01` | full `y = m x + c` from the drawn line | `equation` | canonical `{m:{num,den}, c:{num,den}}` + `display` `"y = …"` |
| `equation_from_two_points` (O7) | `SPI.MIDDLE.GEO.COORD.EQUATION_FROM_2PTS.01` | `m = Rational(y2−y1, x2−x1)`, `c = y1 − m·x1` (exact) | `equation` | `{m:{num,den}, c:{num,den}}` |

`gradient`/`equation` reductions go through `Rational` so `{num, den}` is GCD-reduced with `den ≥ 1`, byte-identical to the Python `fractions.Fraction` oracle; checking is delegated to `core/answer-checking/rational-checker.ts checkExactRational` for the rational/gradient/intercept components, to the platform ordered-pair checker for coordinates, and to the **new** bivariate `core/answer-checking/line-equation-checker.ts` for `equation` answers (§5.3). `display` is formatted from the **same** canonical values (no parallel formatting path).

**Gradient-defined invariant (the load-bearing exclusion):** every task whose canonical form is `y = m x + c` (`gradient_two_points`, `interpret_mx_c`, `equation_from_graph`, `equation_from_two_points`) has a **finite, GCD-reduced** gradient. For O3/O7 (which draw a point pair) this is enforced by requiring `x1 ≠ x2`: the param loop rejects and **deterministically redraws** any draw with `x1 = x2` (a vertical line has no gradient). For O5/O6 (which draw the line directly as `{m, c}` with no point pair) the exclusion is **structural**: the `Line {m, c}` shape can only carry a finite `m`, so a vertical line is unrepresentable. Vertical lines `x = a` are therefore **never silently included**, mirroring the angles family's `guardsOk` redraw discipline.

**Zero-gradient `gradient_two_points` is free-response-only (stated explicitly).** A horizontal `gradient_two_points` draw (`m = 0`, `y1 = y2`) cannot field three distinct misconception-backed distractors: across the full sampling domain `D = [−10,10]²`, the eligibility list collapses — `GRADIENT_INVERTED` and `GRADIENT_SIGN` go `null` (their `m = 0` guards), and `GRADIENT_DELTA_Y_ONLY` and `GRADIENT_SUM_DENOM` both evaluate to `0`, equal to the answer (skipped by the §9.3 "skip a value equal to the answer" step). The remaining rules are **not** relied on to force MC eligibility (owner decision), so three strong distinct distractors are not assembled. Therefore **a zero-gradient `gradient_two_points` item is always emitted free-response** (`interactionType = free-response`), and the §13.2 "zero gradient exemplified" coverage cell is satisfied by a **free-response** item (not MC). When the interaction type is unpinned the item is simply emitted FR; when MC is **explicitly requested** for O3 the param loop redraws away from `m = 0` until an MC-eligible (`m != 0`) draw is found — it never silently returns FR. This is the cx- analogue of the `plot_point` "free-response-only" note.

### 8.2 Independent validator — `validate(item) → {status, validatorVersion, checks[]}`

`validatorVersion` is **`1.0.0`**. The validator is **independent** in the same two senses the angles validator is, returns the same `{status: "pass"|"fail", validatorVersion, checks: [{name, result, detail}]}` surface (`status = "pass"` iff every check passes), and is implemented with **TS+Py parity**.

1. **`svg-realises-data`** (cx- analogue): rebuild the figure from `params` alone — recompute the window, `U`, and `offX/offY` (§7), re-project through the single projection of record, re-clip, re-place labels (§6) — re-serialise the canonical SVG, and assert it equals `media[0].svg` **byte-for-byte**. This is the renderer's integrity gate; the colour layer is checked separately in §16 against this same canonical string.
2. **`closure-agreement`**: recompute the answer by a **second route** distinct from `solve` and assert it equals `answer.canonical` exactly. Second routes: gradient via `Rational((y2−y1),(x2−x1))` recomputed from the figure's two plotted points (not from a cached `m`); midpoint via summing the two projected lattice points back to math and halving; `equation_from_two_points` via substituting **both** endpoints into the recovered `y = m x + c` and asserting both residuals are exactly zero (`point-on-line-consistency`); `interpret_mx_c`/`equation_from_graph` by reading `m`, `c` off the clipped line geometry and comparing to `answer.canonical`.

### 8.3 Named check list (`{name, result, detail}` each)

Geometry / figure-data checks:

| name | asserts |
|---|---|
| `point-on-line-consistency` | for line tasks, **every** plotted defining/anchor point satisfies `y = m·x + c` exactly (Rational residual = 0). |
| `gradient-defined` | the gradient is finite and GCD-reduced for all line tasks; for O3/O7 additionally `x1 ≠ x2`. fails ⇒ item rejected. |
| `ordered-pair-canonical` | coordinate/ordered-pair answers are `{x:{num,den}, y:{num,den}}` GCD-reduced, `den ≥ 1`. |
| `line-clipped-within-viewport` | the `.cx-line` endpoints lie within `[PAD, VIEW_W−PAD] × [PAD, VIEW_H−PAD]`, equal the §7.4 exact clip then single `gridRound`, and the clip is non-degenerate (`t0 < t1`, no zero-length line). |
| `equal-axis-scale` | the same integer `U` and centering offsets `offX/offY` are used on both axes (recomputed from `params` matches the rendered geometry). |
| `axes-stronger-than-grid` | `width(.cx-axis) > width(.cx-grid-major) > width(.cx-grid-minor)` and the greyscale darkness order matches (no colour-/opacity-only distinction). |
| `major-grid-stronger-than-minor` | `.cx-grid-major` is strictly wider and darker than `.cx-grid-minor` (the minor distinction is width-and-shade, never opacity alone). |
| `tick-labels-integer` | every emitted `.cx-ticklbl` value is an integer; the stride is the deterministic §6.5 **integer-ceil** stride; `0` is present exactly once and the stride is symmetric about the origin. |
| `point-label-clearance` | every `.cx-lbl` box clears all points, axes, tick labels, the line, guides, and other labels by ≥ `LBL_CLEAR` px (recomputed placement over the committed finite ladder matches the SVG). |
| `line-label-clearance` | the neutral line label (e.g. `l`; never the equation) clears the line and axes by ≥ `LBL_CLEAR` px. |
| `guide-distinct-from-line` | every `.cx-guide` is thinner than and dashed-vs-solid relative to `.cx-line`/`.cx-axis`, and no guide is collinear with an axis or the line (cannot be misread as geometry). |
| `no-answer-label-in-student-svg` | the student `media[0].svg` contains **no** label/text encoding the assessed answer — no `y = mx + c` string, no numerical gradient, no numerical intercept, no midpoint coordinate, no answer-identifying label. For `equation_from_graph` the line carries only the neutral label (`l`) or none. |
| `plot-point-target-absent-from-student-svg` | for `plot_point`, the student `media[0].svg` is a **blank labelled grid** — the target point's marker/label is **absent** (it appears only in the answer-key/solution overlay). |
| `solution-overlay-matches-canonical-answer` | the answer-key / worked-solution / teacher-validation overlay point or line is **derived deterministically from the same `params`** and equals `answer.canonical` exactly (e.g. the `plot_point` overlay marker, the `midpoint` overlay point, the `equation_from_graph` overlay line). |
| `equation-label-does-not-reveal-answer` | for `equation_from_graph`, the only line label in the student figure is the neutral label (`l`) or none; the equation/gradient/intercept text appears **only** in the answer key + worked solution. |
| `guides-match-scaffolding-level` | guides match the item's scaffolding band: a **standard** `gradient_two_points` has **no** rise/run guide and a **scaffolded** one has at most an **unlabelled** dashed step (signed lengths only in the solution); `read_point` projection guides appear **only** in lower-band items and are **absent** in higher-band items. |
| `vertical-line-excluded` | **split by task.** For O3/O7 (point-pair tasks): the defining points have distinct `x` (`x1 ≠ x2`). For O5/O6 (line drawn directly as `{m,c}`): the structural invariant — `m` is a **finite, GCD-reduced `Rational`** — holds; for O6 the two read-off lattice anchors additionally have distinct `x` (which follows automatically for a non-vertical line). No `x = a` form is representable. |
| `figure-to-scale` | `media[].toScale === true` (the equal-`U` construction makes the figure geometrically faithful) and **no "NOT TO SCALE" label** is emitted — the inverse of the angles family's `not-to-scale` check. |

Answer / accessibility / provenance checks (mirroring the angles validator):

| name | asserts |
|---|---|
| `no-answer-in-accessibility-text` | `accessibility.longDescription`/`altText`/`spokenMath` and `media[].altText`/`longDescription` contain the visible givens but **not** the gradient, intercept, midpoint, or equation answer (`answer.display` string absent); `nonColorIndicators === true`. (For `read_point` the given plotted point is a stated given, not a withheld deduction. For `plot_point` the point is NOT plotted in the student figure, so the text describes only the blank grid and must NOT say the point is already plotted; for `midpoint` the text states the two endpoints but not the midpoint.) |
| `a11y-text-canonical` | stored accessibility/media text equals the recomputed canonical text byte-for-byte (tamper-evident). |
| `answer-type-consistency` | `answer.type` ∈ {ordered-pair, coordinate, exact-rational, integer, equation} and matches the task; `canonical` shape matches §8.1. |
| `answer-solution-agree` | the final `solution.steps[]` intermediate result contains `answer.display`. |
| `distractors-distinct-misconceptions`, `distractor-value-matches-rule`, `distractor-rationale-matches`, `distractor-feedback-clean`, `distractor-not-answer`, `exactly-one-correct`, `min-three-distractors`, `distractors-unique` | standard misconception-distractor gates; MC is offered **only** where ≥ 3 distinct misconception-backed distractors are pedagogically defensible (else free-response). In particular a zero-gradient `gradient_two_points` draw can field at most one distinct distractor and is therefore **always free-response** (§8.1); the param loop redraws only within MC-eligible sub-cases if fewer than 3 distinct rule values exist. |
| `provenance-complete` | `provenance.origin === "generated"`, `rightsStatus === "academy-owned"`, `originalityNote` present. |
| `version-fields-present` | `generatorId === "gen.geometry.coordinate-lines"`, `generatorVersion === "1.0.0"`, `schemaVersion` present. |
| `difficulty-axes-schema-valid` | `difficulty.axes` uses **only** the schema's closed axis vocabulary (`numericalComplexity`, `reasoningSteps`, `abstraction`, `representation`, …) — the family emits **no** invented axis name — and `difficulty.overallBand` equals `bandFromScore(round3(score))` per `core/difficulty/band.ts`, so every item passes the runtime Ajv boundary check. |
| `lifecycle-machine-validated` | items start `lifecycle.state = "generated"` with `lifecycle.validation.status` from this validator at `validatorVersion 1.0.0`. |

The figure-data checks **parse back** the serialised SVG (regex over the committed `.cx-*` elements, the same technique the angles validator uses on `<path class="ga">` / `<line class="gx">`) so the assertions bind to the **published** bytes, not to in-memory state. Every check carries a human-readable `detail` (e.g. `m=3/2`, `U=28`, `offX=120`, `clip t0=1/4 t1=3/4`). All checks run in both the Python oracle and the TypeScript validator with byte-identical results, and feed the standard parity/sweep harness (golden seeds `1, 42, 123456789, 2147483647`; 150-seed × 2-mode parity; `SPI_SWEEP=10000` stability) on the road to owner approval, with `gen.geometry.coordinate-lines` registered `pending-review` in `core/sdk/sequence-registry.ts` until then.


---

## 9. Misconception registry proposal

The family ships one registry pair, `oracle/spi_oracle/coordinate_lines_misconceptions.py` + `domains/geometry/coordinate-lines.ts`, held at BYTE-PARITY exactly as the angles and sequences families are. Every entry follows the established shape `{ formula, expression, title, description, observableError, feedback }`:

- `formula:(params)->value|null` — recomputed ONLY from displayed givens; returns its wrong value as a `Rational`/`Fraction` (gradient, intercept, `c`), an ordered-pair `[x,y]` (read/midpoint), or a value-pair `(m,c)` (equation tasks); returns `null` when the rule collapses onto the answer or is undefined for this draw. Every guard below is stated as an explicit, decidable predicate over the displayed givens — there is no "distinct by construction" hand-wave.
- `expression` — internal teacher-only symbolic form (may use internal symbols `x1,y1,x2,y2,m,c`); never serialized into a learner-facing field.
- `title` / `description` — technical metadata.
- `observableError` — student rationale, NO internal symbols; serialized verbatim as the distractor `rationale` and checked by `distractor-rationale-matches`.
- `feedback` — item-specific, built from the DISPLAYED values only, NO internal placeholder symbols; checked by `distractor-feedback-clean`.

All entries are namespaced `MISC.COORD.*`. Ordered-pair rules compare componentwise; rational/integer rules compare exactly via the established `{num,den}` equality (`checkExactRational` semantics, `den>=1`, GCD-reduced). Distractor display strings are rendered through the same formatter as the answer so `exactly-one-correct` compares like-for-like (for equation answers, the normalised `y = mx + c` string of §5.1, with the `m==0 & c==0 -> "y = 0"` precedence pinned there).

**Semantic misconception-ID reuse across tasks (approved).** A single semantic misconception ID (e.g. `MISC.COORD.GRADIENT_INVERTED`, `MISC.COORD.READS_X_INTERCEPT`) **may be reused across tasks when the underlying conceptual error is the same**, and the analytics record the task separately for each appearance. The owner has approved this rather than minting duplicate task-scoped IDs for reporting convenience. A reused ID must still carry: (1) **one** defined conceptual error; (2) a **task-specific deterministic value adapter** (its `formula` produces the right wrong-value shape for each task it appears in); (3) **task-appropriate feedback**; and (4) **independent semantic validation** in each task. **Do NOT mint duplicate task-scoped IDs** (e.g. a separate `MISC.COORD.EQN.GRADIENT_INVERTED`) merely for cleaner per-task analytics — analytics already record the task alongside the shared ID.

### 9.1 Registry entries

Axis-swap / sign family (point tasks; displayed point `(x,y)`):

| id | formula (from displayed givens) | expression | title | observableError | feedback (example, from displayed values) |
|---|---|---|---|---|---|
| `MISC.COORD.AXIS_SWAP` | `[y, x]` (null if `x==y`) | `(y, x)` | Reads the pair in the wrong order | Swapped the x- and y-coordinates. | The first number is the horizontal (x) value, the second is the vertical (y). Here the point is right/left then up/down. |
| `MISC.COORD.SIGN_X` | `[-x, y]` (null if `x==0`) | `(-x, y)` | Sign error on the x-coordinate | Took the x-coordinate with the wrong sign. | Count direction along the x-axis: points to the left of the origin have a negative x. |
| `MISC.COORD.SIGN_Y` | `[x, -y]` (null if `y==0`) | `(x, -y)` | Sign error on the y-coordinate | Took the y-coordinate with the wrong sign. | Count direction up the y-axis: points below the origin have a negative y. |
| `MISC.COORD.SIGN_BOTH` | `[-x, -y]` (null if `x==0 && y==0`) | `(-x, -y)` | Sign error on both coordinates | Read both coordinates with the wrong sign. | Reflect across the origin only if both directions are reversed; check left/right and up/down separately. |

Gradient family (`gradient_two_points`, two displayed lattice points `(x1,y1),(x2,y2)`; answer `m=(y2−y1)/(x2−x1)` exact `Rational`):

| id | formula | expression | title | observableError | feedback |
|---|---|---|---|---|---|
| `MISC.COORD.GRADIENT_INVERTED` | `(x2−x1)/(y2−y1)` (null if `y2==y1` **OR** `\|y2−y1\| == \|x2−x1\|`) | `(x2-x1)/(y2-y1)` | Run over rise (inverted) | Divided the horizontal change by the vertical change. | Gradient is rise over run: divide the change in y by the change in x, not the other way round. |
| `MISC.COORD.GRADIENT_SUM_DENOM` | `(y2−y1)/(x2+x1)` (null if `x2+x1==0` or equals answer) | `(y2-y1)/(x2+x1)` | Adds coordinates in the denominator | Added the x-values instead of subtracting them. | Use the difference of the x-values for the run, not their sum. |
| `MISC.COORD.GRADIENT_SUM_BOTH` | `(y2+y1)/(x2+x1)` (null if `x2+x1==0` or equals answer) | `(y2+y1)/(x2+x1)` | Adds in both numerator and denominator | Added the coordinates instead of subtracting them. | Gradient uses differences (change in y over change in x), not sums. |
| `MISC.COORD.GRADIENT_DELTA_Y_ONLY` | `(y2−y1)` (as integer; null if equals answer) | `y2 - y1` | Forgot to divide (rise only) | Gave the rise without dividing by the run. | You found the change in y; now divide it by the change in x to get the gradient. |
| `MISC.COORD.GRADIENT_SIGN` | `(y1−y2)/(x2−x1)` (null if `m==0` or equals answer) | `(y1-y2)/(x2-x1)` | Subtracts in inconsistent order | Subtracted the coordinates in inconsistent orders. | Subtract x and y in the SAME order from both points; mixing the order flips the sign. |
| `MISC.COORD.GRADIENT_RUN_ONLY` | `(x2−x1)` (as integer; null if equals answer) | `x2 - x1` | Used the run as the gradient | Gave the horizontal change instead of the gradient. | The run is the bottom of the fraction; divide the rise by the run to get the gradient. |
| `MISC.COORD.GRADIENT_UNIT_SLIP` | `1` (constant; null if `m==1`) | `1` | Assumed a unit gradient | Assumed the line goes up one for every one across. | Check the actual rise and run on the grid; the line does not always rise one square per square across. |

**Zero-gradient (`m=0`) `gradient_two_points` is FREE-RESPONSE ONLY in v1.0.0 — these rules do NOT make every horizontal item MC-ready.** For a horizontal draw (`y1==y2`, `x1!=x2`, answer `0`): `GRADIENT_INVERTED` and `GRADIENT_SIGN` return `null`, and `GRADIENT_DELTA_Y_ONLY` and `GRADIENT_SUM_DENOM` collapse onto the answer `0` (skipped by §9.3 step 2). `GRADIENT_RUN_ONLY` (`= x2−x1`), `GRADIENT_UNIT_SLIP` (`= 1`), and `GRADIENT_SUM_BOTH` survive, but the owner has decided they must **NOT** be relied on to force MC eligibility for horizontal lines: a zero-gradient `gradient_two_points` item is **always emitted free-response** (an explicit MC request for this task redraws away from `m=0`). `GRADIENT_UNIT_SLIP = 1` **may remain in the registry as a diagnostic rule** (it surfaces in `solution`/analytics feedback), but it does not, on its own, make a horizontal line MC-eligible. This keeps Section 9 consistent with Sections 3, 4, 8, 11 and 13: horizontal lines stay in **free-response** coverage.

Midpoint family (`midpoint`, displayed points `(x1,y1),(x2,y2)`; answer `((x1+x2)/2,(y1+y2)/2)` exact rational ordered pair):

| id | formula | expression | title | observableError | feedback |
|---|---|---|---|---|---|
| `MISC.COORD.MIDPOINT_SUM_NO_HALF` | `[x1+x2, y1+y2]` (null if `(x1+x2)==0 && (y1+y2)==0`, i.e. midpoint is the origin) | `(x1+x2, y1+y2)` | Sum without halving | Added the coordinates but did not divide by 2. | The midpoint averages the coordinates: add each pair and then divide by 2. |
| `MISC.COORD.MIDPOINT_DIFF` | `[(x2−x1)/2, (y2−y1)/2]` (null if equals answer) | `((x2-x1)/2, (y2-y1)/2)` | Difference instead of average | Used the difference of the coordinates instead of their average. | Average means ADD the coordinates then halve; differences give a displacement, not the midpoint. |
| `MISC.COORD.MIDPOINT_AXIS_SWAP` | `[(y1+y2)/2, (x1+x2)/2]` (null if `x1+x2 == y1+y2`) | `((y1+y2)/2, (x1+x2)/2)` | Averages but swaps axes | Averaged correctly but wrote the pair in the wrong order. | Average the x-values for the first coordinate and the y-values for the second; keep x then y. |
| `MISC.COORD.MIDPOINT_HALF_ONE_AXIS` | `[(x1+x2)/2, y1+y2]` (null if `y1+y2 == 0`, else automatically `!= answer`) | `((x1+x2)/2, y1+y2)` | Halves one axis only | Divided only one coordinate by 2. | Divide BOTH the summed x-values and the summed y-values by 2. |

Equation / interpretation family (`interpret_mx_c`, `equation_from_graph`, `equation_from_two_points`; the displayed/derived line has gradient `m` and intercept `c`; answer is the value-pair `(m,c)` or full `y=mx+c` `equation`):

| id | formula | expression | title | observableError | feedback |
|---|---|---|---|---|---|
| `MISC.COORD.MC_SWAPPED` | `(c, m)` (null if `m==c`) | `(c, m)` | Gradient and intercept swapped | Reported the intercept as the gradient and vice versa. | In y = mx + c, the number multiplying x is the gradient; the standalone number is the y-intercept. |
| `MISC.COORD.C_SIGN` | `(m, −c)` (null if `c==0`) | `(m, -c)` | Sign error on the intercept | Took the y-intercept with the wrong sign. | Read where the line crosses the y-axis with its sign: below the origin the intercept is negative. |
| `MISC.COORD.M_SIGN` | `(−m, c)` (null if `m==0`) | `(-m, c)` | Sign error on the gradient | Gave the gradient with the wrong sign. | A line falling left-to-right has a NEGATIVE gradient; rising left-to-right is positive. |
| `MISC.COORD.GRADIENT_INVERTED` (reused) | `(1/m, c)` (null if `m==0` or `\|m\|==1`) | `(1/m, c)` | Inverts the gradient | Inverted the gradient (run over rise). | Gradient is rise over run; do not flip the fraction. |
| `MISC.COORD.READS_X_INTERCEPT` (O6 only) | `(m, −c/m)` (null if `m==0` **OR** `c==0` **OR** `−c/m == c`) | `(m, -c/m)` | Reads the x-intercept as c | Used the x-axis crossing instead of the y-axis crossing. | c is where the line meets the VERTICAL (y) axis, not the horizontal one. |

`READS_X_INTERCEPT` divides by `m`, so it is only meaningful for a sloping line that actually crosses the x-axis at a value distinct from `c`. Its guard returns `null` when `m==0` (a non-degenerate horizontal line `y=c, c!=0` never meets the x-axis — no division by zero is ever attempted), when `c==0` (line through the origin: the x-intercept is `0`, colliding with the intercept region), and when `−c/m == c` (the wrong value would equal the true intercept). This makes the rule total over every admissible O6 draw, including the explicitly-allowed horizontal lines of §11.

For the full-`equation` answer tasks (O6, O7) the distractor `value` is the wrong `(m,c)` pair and its `display` is the corresponding normalised `y = mx + c` string built by the canonical equation formatter (§5.1), so `distractor-value-matches-rule` recomputes the pair and `exactly-one-correct` compares the normalised equation display.

### 9.2 Task -> [ids] eligibility map and MC vs free-response decision

Eligibility mirrors the `ELIGIBILITY: Record<string, string[]>` + `rulesFor(task)` pattern. A task is MC-eligible only where at least three distinct, pedagogically defensible misconception rules can yield three distinct non-answer values for the value type; otherwise it is FREE-RESPONSE-ONLY (the platform default).

```
read_point                  -> [AXIS_SWAP, SIGN_X, SIGN_Y, SIGN_BOTH]              (MC-eligible)
plot_point                  -> []                                                  (free-response only; MC unsupported)
gradient_two_points         -> [GRADIENT_INVERTED, GRADIENT_SUM_DENOM,
                                 GRADIENT_SUM_BOTH, GRADIENT_DELTA_Y_ONLY,
                                 GRADIENT_SIGN, GRADIENT_RUN_ONLY,
                                 GRADIENT_UNIT_SLIP]                                (MC-eligible ONLY when m != 0; m=0 is FR-only)
midpoint                    -> [MIDPOINT_SUM_NO_HALF, MIDPOINT_DIFF,
                                 MIDPOINT_AXIS_SWAP, MIDPOINT_HALF_ONE_AXIS]        (MC-eligible)
interpret_mx_c              -> [MC_SWAPPED, C_SIGN, M_SIGN, GRADIENT_INVERTED]     (MC-eligible where 3 valid structured distractors exist)
equation_from_graph         -> [MC_SWAPPED, C_SIGN, M_SIGN, READS_X_INTERCEPT,
                                 GRADIENT_INVERTED]                                 (MC-eligible where 3 defensible distractors exist)
equation_from_two_points    -> [MC_SWAPPED, C_SIGN, M_SIGN, GRADIENT_INVERTED]     (MC-eligible where 3 defensible distractors exist)
```

Decisions:

- **`plot_point` is FREE-RESPONSE-ONLY (MC unsupported in v1.0.0).** Its `interactionType` is `free-response` with a `graph-response`/`coordinate` interaction; the learner places a marker rather than choosing from labelled wrong points. Surfacing AXIS_SWAP/SIGN_* as four visible alternative dots is pedagogically perverse (it teaches the slip) and the wrong placements are not bankable distractor values. Mark `interactionType: free-response`; the answer checker compares the placed/typed `coordinate` exactly. The four point misconceptions remain DIAGNOSTIC (used in `solution` feedback and analytics) but are excluded from distractor generation, exactly as the diagnostic-only slip in the linear family. An explicit MC request for `plot_point` is **rejected as unsupported** (never silently returned as FR).
- **`gradient_two_points` is MC-eligible ONLY when `m != 0`; the zero gradient is FREE-RESPONSE ONLY.** A horizontal draw (`m=0`) cannot field three distinct misconception-backed distractors: `GRADIENT_INVERTED`/`GRADIENT_SIGN` go `null` and `GRADIENT_DELTA_Y_ONLY`/`GRADIENT_SUM_DENOM` collapse onto the answer `0`. The surviving rules (`GRADIENT_RUN_ONLY`, `GRADIENT_UNIT_SLIP`, `GRADIENT_SUM_BOTH`) are **not** relied on to force MC eligibility at `m=0` (owner decision); `GRADIENT_UNIT_SLIP = 1` stays only as a diagnostic. The §13.2 zero-gradient coverage cell is therefore satisfied by a **free-response** O3 item, and an explicit MC request for O3 deterministically redraws away from `m=0`.
- All MC-eligible tasks **default to `free-response`**; an item is emitted as `multiple-choice` only when the generator succeeds in building exactly three DISTINCT misconception-backed distractors (§9.3). The platform never fabricates a distractor without a rule. An explicitly requested interaction type is never silently changed (MC redraws until eligible; `plot_point` MC is rejected as unsupported).

### 9.3 Guaranteeing three distinct distractors (else deterministic redraw)

The generator reuses the committed build-and-redraw discipline. For an MC draw it iterates the task's eligibility list in fixed order, calls each rule's `formula(params)`, and:

1. skips a `null` return (rule undefined / collapses);
2. skips a value EQUAL to the answer (`distractor-not-answer` / `distractor-value-matches-rule` would otherwise fail) — equality is exact (componentwise for pairs, `{num,den}` for rationals);
3. skips a value already collected (DISTINCT by value and by `misconceptionId`, enforced by `distractors-distinct-misconceptions`);
4. stops once exactly three are collected.

If fewer than three distinct distractors result, the distractor builder returns `null`. When the interaction type is the default (unpinned), the item is emitted **free-response** instead; when MC is **explicitly requested**, the bounded param loop **redraws deterministically** (the seeded RNG has already advanced, so the same seed reproduces the same accepted item — the established redraw contract) until a three-distractor draw is found. The eligibility lists are sized (4–7 rules each) so that, given the parameter constraints in §11 (non-degenerate gradients, magnitude bounds), three distinct distractors are reachable for the overwhelming majority of **non-zero-gradient** draws; the rare shortfall simply costs one redraw. The **zero-gradient `gradient_two_points` sub-case is the one structurally-forced FR-only case** — an MC request for O3 redraws away from `m=0` rather than shipping a weak horizontal MC. Because `plot_point` carries no eligibility, it is never considered for MC and is always emitted `free-response` (an explicit MC request is rejected as unsupported), so its empty list can never trigger a redraw loop.

Validator coverage (all already named in the platform): `distractors-distinct-misconceptions`, `min-three-distractors`, `distractor-misconception-known`, `distractor-value-matches-rule`, `distractor-rationale-matches`, `distractor-feedback-present`, `distractor-feedback-clean`, `distractor-not-answer`, `exactly-one-correct`, `distractors-unique`.

## 10. Difficulty model

The family is OUTPUT-NEUTRAL with respect to the central band function and mirrors the **sequences** generators (`domains/sequences/arithmetic.ts` / `geometric.ts`), which are the approved families that genuinely call `bandFromScore`. (The angles family computes its band by a different `lo + min(factors, hi−lo)` route and is NOT the model for the band step here; it is the model only for the canonical-SVG and a11y discipline.) The generator computes weighted axis values in `[0,1]`, `round3`-rounds each, takes the weighted sum, and calls `bandFromScore(score)` from `core/difficulty/band.ts` (mirrored by `oracle/spi_oracle/difficulty.py`). It NEVER defines its own band mapping.

**Schema-faithful axes (blocker fix).** The emitted `difficulty` object uses ONLY axis names permitted by `schemas/question-item.schema.json` `$defs/difficultyProfile.axes` (`additionalProperties:false`, closed enum). The coordinate-specific quantities are mapped onto the existing closed vocabulary exactly as `angles.ts`/`arithmetic.ts` do — no new axis keys are invented, so every item passes the runtime Ajv boundary check (§14.3). The four axes emitted are `numericalComplexity`, `exactVsApproximate`, `reasoningSteps`, `abstraction`:

| family quantity (old name) | schema axis used |
|---|---|
| coordinate magnitude | folded into `numericalComplexity` |
| sign / negativity | folded into `numericalComplexity` |
| denominator complexity (fraction load) | `exactVsApproximate` |
| step count | `reasoningSteps` |
| reverse / equation load | `abstraction` |

### 10.1 Axis definitions

Each axis is clamped to `[0,1]` then `round3`-rounded.

- `numericalComplexity` — combines coordinate magnitude and sign load (the two former `coordinateMagnitude`/`negativity` quantities), exactly as `arithmetic.ts` folds magnitude and a negative-`d` penalty into one `numericalComplexity` axis. With `M = max |coordinate or rise/run or intercept|` over displayed givens and the answer:
  `numericalComplexity = min(1, M/10 + 0.15*(any negative given/answer) + 0.10*(two or more negatives))`
  (grid runs to ±10 at unit scale `U`; a wholly first-quadrant item floors low, mixed-sign items score higher).
- `exactVsApproximate` — fraction/denominator load after exact GCD reduction (the former `denominatorComplexity`). With `D = max(den)` over rational answer components, `exactVsApproximate = min(1, (D − 1)/5)` (integer answers score 0). The name is apt: an exact reduced rational gradient/midpoint is harder to read and state than an integer, while the platform never produces an approximate value.
- `reasoningSteps` — `STEP_COUNT[task] / 4`, where `STEP_COUNT = { read_point:1, plot_point:1, gradient_two_points:2, midpoint:2, interpret_mx_c:1, equation_from_graph:3, equation_from_two_points:4 }`.
- `abstraction` — reverse/equation load. Forward read/plot tasks score low; finding an equation scores high: `abstraction = { read_point:0.1, plot_point:0.1, gradient_two_points:0.3, midpoint:0.25, interpret_mx_c:0.4, equation_from_graph:0.7, equation_from_two_points:0.8 }`.

### 10.2 Per-task floor (via the axis values) and weights

There is NO separate floor clamp on the band. As in `arithmetic.ts`, the band is **solely** `bandFromScore(round3(score))`; the per-task ordering ("a harder task never bands below an easier one for comparable numbers") is achieved by the per-task base values of `reasoningSteps` and `abstraction`, which rise monotonically with task difficulty and are weighted heavily (combined weight 0.50). This is the same mechanism the sequences family uses (its `steps`/`abstraction` per-task constants), and it does NOT require — nor does the family add — a `max(floor, band)` override that would diverge from the central function. The "typical floor band" column below is therefore a *consequence* of those axis bases under the weights, verified by the worked scores in §10.3 and bounded at emission by the objective's `difficultyRange{min,max}` (the param loop redraws if a draw lands outside the declared range):

| task | typical floor band (emergent) |
|---|---|
| read_point | 1 |
| plot_point | 1 |
| gradient_two_points | 2 |
| midpoint | 2 |
| interpret_mx_c | 2 |
| equation_from_graph | 3 |
| equation_from_two_points | 3 |

Weights `W` (sum to 1), applied to the `round3`-rounded axes (mirroring the `DIFFICULTY_WEIGHTS` constant pattern of `arithmetic.ts`):

```
W = { numericalComplexity: 0.30, exactVsApproximate: 0.20,
      reasoningSteps: 0.25, abstraction: 0.25 }
score = W.numericalComplexity*numericalComplexity
      + W.exactVsApproximate*exactVsApproximate
      + W.reasoningSteps*reasoningSteps
      + W.abstraction*abstraction
overallBand = bandFromScore(round3(score))   // band = min(5, 1 + floor(clamp01(score)*5))
```

### 10.3 Worked score -> band examples (re-derived under the schema axes)

| item | axes (rounded): num / exact / steps / abs | weighted score | band |
|---|---|---|---|
| `read_point`, point (3,4), first quadrant | 0.30 / 0 / 0.25 / 0.1 | .30·.30 + .20·0 + .25·.25 + .25·.1 = 0.178 | **1** |
| `read_point`, point (−7,2) | 0.85 / 0 / 0.25 / 0.1 | .255 + 0 + .0625 + .025 = 0.343 | **2** |
| `gradient_two_points`, (1,2)&(4,8), m=2 | 0.80 / 0 / 0.50 / 0.3 | .24 + 0 + .125 + .075 = 0.440 | **3** |
| `gradient_two_points`, (−3,5)&(2,−4), m=−9/5 | 0.75 / 0.80 / 0.50 / 0.3 | .225 + .16 + .125 + .075 = 0.585 | **3** |
| `midpoint`, (1,1)&(4,6), mid (5/2,7/2) | 0.60 / 0.20 / 0.50 / 0.25 | .18 + .04 + .125 + .0625 = 0.408 | **3** |
| `equation_from_graph`, m=2, c=−3 | 0.45 / 0 / 0.75 / 0.7 | .135 + 0 + .1875 + .175 = 0.498 | **3** |
| `equation_from_two_points`, (−2,1)&(3,−4), m=−1, c=−1 | 0.65 / 0 / 1.0 / 0.8 | .195 + 0 + .25 + .2 = 0.645 | **4** |
| `equation_from_two_points`, (−4,7)&(6,−8), m=−3/2, c=1 | 0.85 / 0.20 / 1.0 / 0.8 | .255 + .04 + .25 + .2 = 0.745 | **4** |

Bands are determined ONLY by `bandFromScore`. The same axis vector feeds `oracle/spi_oracle/difficulty.py`, so TS and Python agree byte-for-byte in the golden/parity fixtures, and the emitted `difficulty.axes` object validates against the schema's closed enum.

The per-objective `difficultyRange` constraints (which clamp emission and trigger a redraw if a draw bands outside the declared range) are, per the owner directive: `CARTESIAN_PLANE` 1; `READ_POINT` 1–2; `PLOT_POINT` 1–2; `GRADIENT_TWO_POINTS` 2–4; `MIDPOINT` 2–3; `INTERPRET_MX_C` 2–3; `EQUATION_FROM_GRAPH` 3–4; `EQUATION_FROM_2PTS` 3–5 (these match the objective `difficultyRange`s of §2). The **scaffolded-vs-unscaffolded** figure choice (§6.7 / §6.1: standard vs scaffolded `gradient_two_points`; lower-band vs higher-band `read_point` with/without projection guides) **contributes to the difficulty profile** — scaffolded/guided variants band lower than their unscaffolded/unguided counterparts.

### 10.4 Required band-distribution report before fixtures freeze

The four-axis weighting `W = { numericalComplexity: 0.30, exactVsApproximate: 0.20, reasoningSteps: 0.25, abstraction: 0.25 }` and the magnitude/denominator scaling divisors (`M/10`, `(D−1)/5`) are **approved only PROVISIONALLY**. Before the golden/parity fixtures freeze, a **≥ 10,000-seed difficulty-distribution report** must be produced (and reproduced in the review pack). Per task, it must report:

- band counts and percentages across the bands;
- any **unreachable bands** within the objective's declared `difficultyRange`;
- any **over-concentrated bands** (a band dominating the distribution);
- the **redraw rate** (fraction of draws rejected before acceptance, including out-of-range-band redraws);
- the **integer-vs-rational answer distribution** (for the gradient/intercept tasks);
- the **positive / negative / zero gradient distribution**.

The weights and divisors above (and the per-task `STEP_COUNT`/`abstraction` bases) are **frozen into the golden fixtures only after this report shows suitable coverage** (every declared band reachable, no pathological over-concentration). Until then they remain provisional calibrations subject to adjustment.

## 11. Edge-case and degeneracy policy

Every case below has a SINGLE deterministic rule, applied inside the seeded param loop; a rejected draw `continue`s and the RNG advances, so the same seed reproduces the same accepted item. Nothing is silently filtered — each rejection is a documented constraint, and deferred features are excluded by construction (they are never sampled), with a guard check that fails loudly if one ever appears.

| case | deterministic rule |
|---|---|
| **Coincident points** (a point task draws `(x1,y1)==(x2,y2)`) | Reject and redraw. Constraint `x2!=x1 OR y2!=y1` enforced for `gradient_two_points`, `midpoint`, `equation_from_two_points`. A coincident pair defines no gradient/line. |
| **Vertical lines** (excluded ONLY from the tasks that compute/represent a finite gradient: O3 gradient_two_points, O5 interpret_mx_c, O6 equation_from_graph, O7 equation_from_two_points) | **DETERMINISTICALLY EXCLUDED from these four tasks**, with the guarantee split by how the task draws its line. **O3/O7** draw a defining point pair `P1,P2`, so the constraint `x2 != x1` is asserted before computing the gradient; equal x-values give an undefined run (division by zero), the draw is rejected, and the bounded loop redraws under the same seed. **O5/O6** draw the line directly as `L={m,c}` (§4.2) and have NO defining point pair, so "`x1 != x2`" has nothing to assert there; for them the exclusion is STRUCTURAL — the `Line{m,c}` shape can only carry a finite reduced `Rational` gradient `m`, and a vertical line `x=a` has no finite `m`, so it cannot be represented at all. For O6 the two on-line lattice anchors `A1,A2` additionally have distinct x (which follows automatically from a finite `m`). The validator guard is therefore split: for O3/O7 `no-vertical-line` asserts `x2 != x1` on the drawn points; for O5/O6 it asserts the structural invariant (`m` is a finite reduced `Rational`; for O6 additionally `A1.x != A2.x`). Vertical `x=a` is a DEFERRED feature and is never emitted. The §13.3 wording reads "distinct x where a defining point pair exists; finite-`m` structural exclusion otherwise." |
| **Points sharing an x-coordinate in point-only tasks** (O1 read_point, O2 plot_point, O4 midpoint) | **ALLOWED.** No gradient is computed in these tasks, so two points (or a plotted point) may share an x-coordinate freely; the vertical-line exclusion does **not** apply here. Only coincident points are rejected, and only where two **distinct** points are required (O4 `midpoint`: `P1 != P2`). |
| **Horizontal lines `y1==y2` (`m=0`)** | ALLOWED and pedagogically valuable, but **FREE-RESPONSE whenever the horizontal case cannot yield three strong distinct MC distractors** — which for `gradient_two_points` is always (owner decision). Gradient is exactly `0` (`m = 0/(x2−x1)`), a valid integer answer; equation is `y = c`. For `gradient_two_points` at `m=0`: `GRADIENT_INVERTED` and `GRADIENT_SIGN` return `null` (their guards fire on `m==0`/`y2==y1`), and `GRADIENT_DELTA_Y_ONLY`/`GRADIENT_SUM_DENOM` collapse onto the answer `0` (skipped by §9.3 step 2). The surviving rules (`GRADIENT_RUN_ONLY`, `GRADIENT_UNIT_SLIP = 1`, `GRADIENT_SUM_BOTH`) are **NOT** relied on to force MC eligibility for horizontal lines, so a zero-gradient `gradient_two_points` item is **always emitted free-response** (an explicit MC request for O3 redraws away from `m=0`). `GRADIENT_UNIT_SLIP = 1` remains only as a diagnostic. Horizontal lines remain fully in **free-response** coverage. `M_SIGN` is NOT in the `gradient_two_points` list (it belongs only to the equation/interpretation family) and is not referenced here. (Horizontal lines in O5/O6/O7 remain MC-eligible where the equation-family rules can still field three distinct distractors.) |
| **Zero gradient** | Same as horizontal: valid answer `m=0`, rendered as a horizontal `cx-line`; the answer is the exact integer `0` (`{num:0,den:1}`); for `gradient_two_points` it is **free-response only**. |
| **Negative gradient** | ALLOWED. `m<0` rendered as a falling line; the equation-family `M_SIGN` distractor is active for O5/O6/O7. Raises `numericalComplexity` (sign load) and hence difficulty per §10. |
| **Fractional gradient** | ALLOWED. `m` is an exact reduced `Rational` (`{num,den}`, `den>=1`); raises `exactVsApproximate`. NO irrational/surd gradients are representable, so distance-with-roots stays correctly deferred. |
| **Reversed point order** | Answer is INVARIANT and the generator guarantees it: gradient `(y2−y1)/(x2−x1) == (y1−y2)/(x1−x2)`, midpoint `((x1+x2)/2,(y1+y2)/2)` is symmetric. The `closure-agreement` check recomputes the answer by the second route; for these tasks the second route uses the reversed order and must agree exactly, locking in order-invariance. |
| **Fractional midpoint** | ALLOWED. Components are exact `Rational`s with `den ∈ {1,2}` (e.g. `(5/2,7/2)`); the answer is an `ordered-pair`/`coordinate` whose components serialize as `{num,den}`. The renderer plots the exact midpoint via `gridRound` only for the figure; the stored answer keeps full exact rational precision. |
| **Lines through the origin** (`c==0`) | ALLOWED. Equation is `y = mx` (the `+ c` term is suppressed in display when `c==0` per the §5.1 normalisation); the value-pair answer is `(m,0)`. `C_SIGN` returns `null` when `c==0` (no sign to flip) and `READS_X_INTERCEPT` returns `null` when `c==0` (x-intercept is `0`); remaining rules supply distractors, redraw if fewer than three. |
| **The line `y=0`** (`m==0 && c==0`, the x-axis) | ALLOWED and unambiguous: per the §5.1 precedence (rule 2 omits the x-term first when `m==0`, then rule 3 applies to `c`), the canonical display is exactly the single string `"y = 0"`; TS and Py cannot diverge, so the `display re-derives from (m,c)` and `a11y-text-canonical` byte assertions hold. |
| **Acceptance predicate for line tasks (`ymin <= c <= ymax`)** | For every line task, before acceptance the param loop asserts `ymin <= c <= ymax` AND that the clipped line segment is non-empty (`t0 < t1` after Liang–Barsky), so the figure always contains a drawable, full-width segment and the parallel-edge `q>=0` condition for a horizontal line is a PROVEN invariant rather than an assumption (extends P3 of §4.4). A degenerate corner-touch clip (`t0 >= t1`) is rejected and redrawn so no zero-length `<line>` is ever emitted. |
| **Labels near axes / viewport boundaries** | Deterministic clamped placement: point and intercept labels use the committed finite candidate ladder (explicit offset list + fixed maximum radius, mirroring the angles family's `R_LABEL_MAX`/`LBL_STEP`), the first feasible candidate is accepted, and on exhaustion the rule returns `null` and the draw is redrawn. `svg-realises-data` rebuilds the figure from params and asserts byte-for-byte SVG equality, so any nondeterministic or overflowing placement fails; a `label-within-viewport` clearance check asserts every label box lies inside `0..1000 x 0..700`. |
| **Multiple equivalent `y=mx+c` forms** | The answer is CANONICAL: `m` and `c` are stored as exact reduced `Rational` value-pairs; the `equation` display is the single normalised `y = mx + c` string per §5.1 (suppress `1x`->`x`, `-1x`->`-x`, the `+ 0`/`x`-omission terms, `+ -c`->`- c`; `m==0 & c==0` -> `"y = 0"`). The new two-variable line-equation checker (§5.3) accepts algebraically-equivalent learner input (e.g. `y − 2x = 1`, `2y = 4x + 2`) by reducing `lhs = rhs` over `{x,y}` to `A·y + B·x + C = 0` and reading `(m,c) = (−B/A, −C/A)`, rejecting `A==0` (vertical/undefined-gradient); the stored `canonical` is the one normalised form, so `closure-agreement` and `exactly-one-correct` compare unambiguously. |

**Deferred-feature exclusions (enforced deterministically, NEVER silently included):** distance with irrational roots; vertical lines `x=a`; parallel/perpendicular; simultaneous/intersection; inequalities/shaded regions; function transformations; nonlinear graphs; scatter/regression; 3D coordinates. None of these is in any task's sampling space; a `deferred-feature-absent` guard check (asserts gradient defined / finite reduced `Rational`, no second line, no inequality operator, 2D only) fails any item that would realise one. The 10,000-seed stability sweep (`SPI_SWEEP=10000`, x2 modes, reproducibility re-check on the first 200 seeds, target 0 invalid) exercises these guards across the whole parameter space; with the **sampling-domain bounds** `COORD_MAX_X=COORD_MAX_Y=10` and data margin `DATA_MARGIN_UNITS=M=1` the worst-case render window is `22x22`, and the pinned `PAD=40`/`U_MIN=24` (§7.6) satisfy `floor((1000−2·PAD)/22) >= U_MIN` and `floor((700−2·PAD)/22) >= U_MIN` for every admissible spread, so the scale-reject branch is statically unreachable in v1.0.0 and the sweep can never throw on scale.

## 12. Accessibility model

The figure carries information three ways — visual SVG, accessible text, and a structured data table — and all THREE render modes (canonical monochrome, premium colour, printable monochrome) are information-equivalent. The accessibility contract mirrors the angles family exactly and is enforced by named validator checks plus the axe-core gate.

**Single stored artifact; modes are presentation-time re-renders.** The item stores ONE `media[0].svg` — the canonical MONOCHROME SVG, which is authoritative. Premium colour and printable monochrome are derived deterministically from the `media[0].spec.premium` style contract at presentation time; the stored item carries the one canonical SVG plus the `spec.premium` style contract, not three baked SVGs. The user's selected viewer mode/theme is a presentation preference and is **not** stored as canonical content (§16.1 a.6), so switching modes does **not** change the item or its `contentHash`. The exporters `exporters/html/{worksheet,answer-key,solutions}.ts` inline the canonical monochrome `media[0].svg`, so the axe-core gate and the stored `contentHash` are unambiguous and reference exactly that authoritative artifact. (`media[0].spec.premium`, the deterministic style contract — palette ID, series/marker/dash assignments, glow limits, legend — DOES fold into `contentHash` like every other item key — there is no hash-exclusion mechanism in core — which makes the presentation spec tamper-evident too; only the non-stored PNG export is outside the hash because it is never written into the item JSON.)

**Figure to scale.** Because the renderer uses an EQUAL x/y unit scale `U` (§7), coordinate figures are geometrically faithful, unlike the angles family (`toScale:false` + a "NOT TO SCALE" mark). The canonical figure sets `media[0].toScale = true` and emits NO "NOT TO SCALE" label. A named validator check `figure-to-scale` asserts `media[0].toScale === true` and that the SVG contains no "NOT TO SCALE" text — the inverse of the angles `not-to-scale` check.

**SVG structure.** The root `<svg>` has `xmlns`, `role="img"`, and `aria-label` (a concise summary), followed by `<title>`, `<desc>`, `<style>`, geometry, caption — the committed canonical ordering. `viewBox` is `0 0 1000 700`; all coordinates are INTEGERS via `gridRound`; classes use the `cx-` prefix (`.cx-axis .cx-tick .cx-ticklbl .cx-grid-major .cx-grid-minor .cx-line .cx-pt-core .cx-pt-outline .cx-lbl .cx-guide`, plus the premium-only decorative `.cx-halo`). TS and Python emit byte-identical SVG, asserted by `svg-realises-data`.

**Data-table fallback.** Each item carries `media[0].dataTableFallback` (the same field the angles family uses) — a `{columns, rows}` table giving the EXACT givens the figure encodes: plotted point coordinates, the two endpoints, tick labels, and, where the task is to interpret (not find) the line, its gradient and intercept. The table never states the value the task asks the learner to produce.

**spokenMath / longDescription, answer-free.** `accessibility.spokenMath`, `accessibility.altText`, and `accessibility.longDescription` are populated; `accessibility.nonColorIndicators` is `true`. The `longDescription` is information-equivalent to the figure but **withholds the answer**: it describes the grid, axes, scale `U`, and the plotted/given objects, and refers to the requested unknown as "the marked point"/"this line" rather than naming its coordinates, gradient, or intercept. This is exactly the `a11y-no-answer-in-text` discipline as implemented in the angles validator — the stored description must contain the word `"unknown"` (the unknown marker) and must NOT contain the answer `display` string — together with `a11y-equivalent-information` (accessible text is equivalent, not easier; no theorem or answer leaked).

**Tamper check.** `a11y-text-canonical` recomputes the canonical accessibility text from params and asserts the STORED `accessibility.longDescription`/`altText`/`spokenMath` and `media[0].longDescription`/`altText` equal it byte-for-byte; a tampered or answer-leaking stored description fails the item. `a11y-fields-present` asserts all three text fields exist.

**No hard-coded DOM ids (safe multi-item export), across BOTH layers.** The canonical SVG uses NO global `id` attributes (no `id`-based `<defs>`/`url(#…)` references that would collide when many items are inlined into one worksheet/answer-key/solutions page). Styling is via the `cx-` classes scoped inside each SVG's own `<style>`; markers/halos are drawn inline, not referenced by id. The PREMIUM layer carries the same prohibition: gradients/halos/legend/series elements are inlined (e.g. fills are direct colour tokens, halos are separate `.cx-halo` elements emitted just before the stroke they back), never `<linearGradient id=…>` + `fill="url(#…)"`. A blocking check `no-global-ids` asserts the SVG (in every mode) contains no `id` attribute and no `url(#…)` reference, so arbitrary multi-item export cannot collide. The JSON exporter round-trip (re-validate + re-generate + byte-compare) confirms it end-to-end.

**Premium-spec parity (committed-constant token tables).** The premium/accessible/print token tables and the `seriesAssignment` ordering are COMMITTED CONSTANTS (analogous to the angles `STYLE` constant), held at Py↔TS byte-parity. A `premium-spec-parity` check asserts the serialized `media[0].spec.premium` (`styleContractVersion`, `paletteId`, `seriesAssignment[]`, marker/dash assignments, `glowLimits`, `legend`) is byte-identical across languages, gating the presentation style contract the same way `svg-realises-data` gates the SVG. The user's selected viewer mode/theme is **not** part of this stored spec (it is a presentation preference, §16.1 a.6).

**No colour-only information, across ALL three modes.**
- *Canonical monochrome* is AUTHORITATIVE: meaning is carried by greys, line style, point core/outline, and text labels — never colour.
- *Premium colour* is a PRESENTATION layer (`--cx-series-1..N`, `--cx-axis`, `--cx-grid-major`, `--cx-grid-minor`, `--cx-pt-core`, `--cx-pt-outline`, `--cx-halo`, `--cx-bg`) over the SAME canonical geometry; every distinction it colours is ALSO encoded by class/shape/label, so removing colour loses no information.
- *Printable monochrome* is the canonical SVG.
For v1.0.0's low-primitive figures (at most one line plus a few points), `distinct-adjacent-series` and the adjacency rule are **vacuously satisfied** (0 or 1 series), and `no-colour-only-meaning` reduces to asserting `accessibility.nonColorIndicators === true` plus the monochrome-authoritative canonical SVG (already covered above). The multi-series machinery is retained as reusable infrastructure but its v1.0.0 applicability is minimal — stated here so the gate set is honest about what actually exercises in this release. A `grid-hierarchy-preserved` check additionally asserts that in every coloured mode the resolved stroke widths satisfy `axis > major grid > minor grid` and that `--cx-grid-minor` differs from `--cx-grid-major` by width AND dash pattern (never opacity/lightness alone), so the coloured layer cannot collapse the hierarchy the monochrome layer guarantees.

**Contrast as committed pass/fail (no runtime float luminance).** WCAG AA contrast is computed ONCE, offline, over the committed finite token table (the fixed light/dark hex pairs), and stored as committed pass/fail booleans per token pair — NOT recomputed per item with a float gamma/luminance pipeline. The runtime/validator `contrast-sufficiency` and `light-dark-readability` checks then merely assert set membership: the item uses only pre-verified token pairs. That makes them exact, deterministic, and cross-language identical (no sRGB float arithmetic in the parity path). All three modes meet WCAG AA (text/line contrast `>= 4.5:1` against `--cx-bg`/paper).

**The axe-core gate.** The a11y gate `apps/generator-studio/a11y.test.ts` (axe-core) must report **0 critical / 0 serious** and AA contrast `>= 4.5:1` for rendered worksheet/answer-key/solutions output; this gate is BLOCKING and runs over the exported STATIC monochrome HTML (the authoritative artifact). Interactive Studio mode (highlight/dim/zoom/pan/live-region) is SCOPED OUT of v1.0.0 as a deferred Studio-only feature touching no learner-facing exported artifact, so no WCAG conformance is asserted for any surface that a gate does not exercise. New families start `approvalStatus: pending-review` in `core/sdk/sequence-registry.ts` and are gated out of Studio/production until the owner approves, so no item reaches a learner until the axe-core gate, the `a11y-*` validator checks, and the byte-parity/sweep gates all pass.


---

## 13. Review-pack plan

The review pack is the single artefact the curriculum owner reads to render the APPROVE/REJECT decision for `gen.geometry.coordinate-lines` v1.0.0. It is built oracle-first by a dedicated, deterministic driver and is byte-reproducible: re-running it on the same commit reproduces every file bit-for-bit. It mirrors `oracle/make_review_pack_geometry.py` exactly in structure, then adds the coordinate-specific premium gallery and the colour/render-mode diagnostics this family introduces.

### 13.1 Files produced

- `oracle/make_review_pack_coordinate_lines.py` — the builder (Python oracle is authoritative).
- `docs/review/coordinate_lines_review_pack.json` — the machine-readable pack (full reproduction metadata per item).
- `docs/review/coordinate_lines_review_pack.md` — the human-readable pack with inline SVG, alt text, long description, data-table fallback, worked solution, MC distractor calculations, per-item validation results, and an `approve / revise / reject` checkbox line per item.
- `docs/review/coordinate_lines_svgs/*.svg` — one saved canonical (monochrome, authoritative) SVG per item, named `{task}__{mode}__{seed}.svg`.
- `docs/review/coordinate_lines_gallery/*` — the premium gallery assets (§13.4): the four render-mode variants per gallery figure, the enlarged zoom proof, and the single high-resolution PNG.
- `docs/review/coordinate_lines_visual_audit.html` — the visual edge-case audit (carries `data-generator-version` and `data-git-commit`, mirroring `geometry_visual_audit.html`).
- `docs/review/coordinate_manifest.json` — the generation manifest (§13.6), schema `spi-math-coordinate-manifest/1`.

Every item in the pack carries `lifecycle.state = generated` and `lifecycle.validation.status = pass` from the independent validator. The pack header states explicitly that **no item is approved or published**; advancing any item or objective beyond machine-validated is the curriculum authority's decision (identical wording discipline to the geometry pack's `note`).

**One stored canonical artefact, presentation re-rendered.** Each item stores exactly one rendered figure: `media[0].svg`, the **canonical monochrome** SVG, which is authoritative. The LIGHT / DARK / accessible-colour variants are *not* stored as additional SVGs in the item; they are presentation-time re-renders derived from the `media[0].spec.premium` style contract (palette ID + series/marker/dash assignment + legend) layered over that same canonical geometry, and the chosen viewer mode/theme is a preference that never changes the stored item or its `contentHash` (§16.1 a.6). Consequently the offline exporters (`exporters/html/{worksheet,answer-key,solutions}.ts`, §12) inline the **canonical monochrome `media[0].svg`** verbatim, the `accessibility.*` text and `contentHash` are computed over the stored item (§13.6), and the axe-core gate (§12) runs against exactly that inlined monochrome SVG. The premium gallery (§13.4) is a *review-pack-only* re-render to evidence the presentation layer; it never changes which artefact production ships.

### 13.2 Item-coverage matrix (what `pick()` must guarantee)

The builder scans seeds deterministically (`SCAN_LIMIT` bounded forward scan from seed 1, same as the geometry builder) and selects a minimal representative set per `(task, mode)` combo such that the union covers every required dimension. Combos are `[(t, m) for t in TASKS for m in modes(t)]`, where `modes(t)` is `["free-response"]` for `plot_point` (FR-only in v1.0.0) and for any other task that is not MC-eligible, and `["free-response", "multiple-choice"]` for every MC-eligible task (`gradient_two_points` is MC-eligible only at `m != 0`).

| Coverage dimension | Requirement enforced by `pick()` |
| --- | --- |
| All 7 tasks | `read_point`, `plot_point`, `gradient_two_points`, `midpoint`, `interpret_mx_c`, `equation_from_graph`, `equation_from_two_points` each present, mapped 1:1 to O1–O7. |
| Every supported interaction type | Free-response for all 7; multiple-choice additionally for every task with ≥3 distinct misconception-backed distractors (gated by the MISC.COORD.* eligibility map, §9). **`plot_point` is FR-only** (no MC; an MC request is unsupported). **`gradient_two_points` MC is exemplified only at `m != 0`** (zero gradient is FR-only). The pack also demonstrates a **deterministic MC redraw** (an MC request landing first on an MC-ineligible sub-case, then redrawing to an eligible draw under the same seed) and demonstrates the **interaction-request-preserved** behaviour. |
| Every supported band | Each task's full `difficulty.overallBand` range (per `TASK_BANDS[task]`) appears. The pack surfaces each item's `difficulty.axes` and `overallBand`; both are reproduced verbatim from the generator (§10) and are **never** re-derived inside the builder. The axes shown are drawn solely from the schema's closed `difficultyProfile.axes` vocabulary (`numericalComplexity`, `reasoningSteps`, `abstraction`, `representation` — see §10), so every reproduced item passes the runtime Ajv boundary check. |
| Integer **and** rational answers | At least one integer-answer and one exact-rational-answer example for the gradient/intercept tasks; `answer.canonical` shown as `{num,den}` with `den≥1`. |
| Gradient sign spread | Positive, negative, **and** zero gradient each exemplified, plus integer and fractional gradients (zero gradient = horizontal line; this is the legal "flat" line, distinct from the deterministically-excluded vertical line). **The zero-gradient coverage cell is satisfied by a free-response item.** For `gradient_two_points` with `m=0` the MISC.COORD.* gradient rules cannot field three strong distinct non-answer distractors (`GRADIENT_INVERTED`/`GRADIENT_SIGN` null on `m=0`; `GRADIENT_DELTA_Y_ONLY`/`GRADIENT_SUM_DENOM` collapse onto the answer `0`; the survivors are not relied on to force MC eligibility — owner decision), so a zero-gradient `gradient_two_points` item is **always emitted free-response** (per the §9.2 note). `pick()` therefore looks for the zero-gradient exemplar in the free-response selection only and never demands a zero-gradient MC item. A zero-gradient *graph* still appears in MC mode via `interpret_mx_c` / `equation_from_graph`, whose distractor families remain ≥3 at `m=0`. Horizontal lines remain in **FR** coverage. |
| Ordered-pair / coordinate answers | `read_point` and `plot_point` exemplified with `answer.type = coordinate`; `midpoint` with `answer.type = ordered-pair`. |
| Equation answers | `interpret_mx_c` (canonical `Line {m, c}`) and `equation_from_graph` / `equation_from_two_points` (full `y=mx+c`) exemplified with `answer.type = equation`. |
| All four quadrants | Points/lines exemplified in **each of the four quadrants**. |
| Points on axes and at the origin | At least one point **on the x-axis**, one **on the y-axis**, and one **at the origin** `(0,0)`. |
| Intercept spread | **Positive and negative y-intercepts** both exemplified, and **lines through the origin** (`c = 0`). |
| Midpoint spread | **Integer midpoints** and **half-integer midpoints** both exemplified. |
| Every misconception rule | **Every MISC.COORD.* rule** is exercised by at least one MC item (with its per-distractor value/rationale/feedback shown). |
| Render / theme modes | Each item's figure shown in **light premium, dark premium, accessible-colour, and monochrome-print** modes (the monochrome print mode is byte-identical to the authoritative canonical SVG); a **multi-line/point synthetic premium stress test** figure (G4/G5). |
| Scaffolding variants | **Scaffolded vs unscaffolded `read_point`** (projection guides present in a lower-band item, absent in a higher-band item) and **scaffolded vs unscaffolded `gradient_two_points`** (unlabelled dashed step vs no guide) both shown. |
| No-answer-leakage evidence | A **`plot_point` student-graph vs answer overlay** pair (target absent from student SVG, present in overlay) and an **`equation_from_graph` figure with no answer label** (neutral `l` only). |
| High-resolution raster | The single **6000×4200 PNG derived from the canonical SVG** (§13.4 G10), plus **zoomed vector evidence** of sharp labels/lines/points (G9). |
| Vertical-line exclusion (negative coverage) | The audit asserts that across the selection sweep **no** `y=mx+c` task ever drew two equal x-values where a defining point pair exists, and that the finite-`m` structural invariant holds where it does not (§13.3); the redraw invariant is exercised and reported (§13.5). |

Each `combos[].items[]` record carries `seed`, `task`, `objectiveIds`, `interactionType`, `answer.type`, `answer.canonical`, `answer.display`, the `params` (source of truth), `difficulty` (schema-valid `axes` + `overallBand` + per-task band range), `generatorVersion`, the prompt text, the inline `media[].svg` (canonical monochrome), `media[].spec.premium` (the deterministic presentation style contract; §13.4/§13.6), `media[].altText`, `media[].longDescription`, the data-table fallback, `media[].toScale` (always `true`; §13.3), the `solution.steps`, the MC `options` order, the per-distractor misconception calculations (value, teacher-only `expression`, `rationale`, item-specific `feedback`), the diagram-validation and accessibility-validation check results, and a `reproduce` block (`generatorId`, `generatorVersion`, `seed`, `config{task, interactionType}`).

### 13.3 Per-item validation surfaced in the pack

For each item the pack reproduces the independent `validate(item)` result (`status` + named `checks[]`). The coordinate-specific diagram and a11y check groups surfaced are:

- **Diagram-to-data:** `svg-realises-data` (rebuild figure from `params`, assert byte-for-byte SVG equality), `closure-agreement` (recompute the answer by a second route), `axes-ticks-labels-correct`, `unit-scale-equal-xy` (the equal-scale invariant U px/unit on both axes), `point-marker-on-lattice`, `line-clipped-to-viewport`, `figure-to-scale` (asserts `media.toScale === true` and that **no** "NOT TO SCALE" label is emitted — the coordinate inverse of the angles `not-to-scale` check; coordinate figures are genuinely to scale by the equal-U construction), `no-answer-leakage` (the assessed quantity — gradient, intercept, midpoint, equation — is not encoded in any label/marker/tick text), `labels-non-overlapping`, `vertical-line-excluded` (task-split, below), `media-present`.
- **Vertical-line-excluded (task-split).** The check asserts the *applicable* invariant per task, because not every task has a defining point pair (§4.2): for **O3 `gradient_two_points`** and **O7 `equation_from_two_points`** (which draw P₁,P₂) it asserts `x₁ ≠ x₂` on the drawn points; for **O5 `interpret_mx_c`** and **O6 `equation_from_graph`** (which draw the line directly as `L = {m,c}` with no point pair) it asserts the **structural invariant** instead — `m` is a finite, GCD-reduced `Rational`, so the `{m,c}` shape cannot represent a vertical line — and for O6 it additionally asserts the two rendered lattice anchors A₁,A₂ have distinct x (which follows automatically for a finite-`m` line). The pack wording reads "distinct x where a defining point pair exists; finite-`m` structural exclusion otherwise."
- **Accessibility:** `a11y-fields-present`, `a11y-no-answer-in-text`, `a11y-equivalent-information`, plus `accessibility.nonColorIndicators` listed (the canonical monochrome figure carries all meaning via shape/label/dash, never colour).
- **No-answer-leakage & scaffolding visual checks (per owner directive).** The pack surfaces these specific named checks per item:
  - `no-answer-label-in-student-svg` — no label/text in the student SVG encodes the assessed answer (no `y=mx+c`, gradient, intercept, or midpoint text).
  - `plot-point-target-absent-from-student-svg` — for `plot_point`, the student SVG is a blank labelled grid with the target marker absent.
  - `solution-overlay-matches-canonical-answer` — the answer-key/solution overlay (plotted point, midpoint, or line) is derived from the same `params` and equals `answer.canonical` exactly.
  - `equation-label-does-not-reveal-answer` — for `equation_from_graph`, the only line label is the neutral `l` (or none); the equation appears only in the answer key + solution.
  - `guides-match-scaffolding-level` — guides present exactly match the item's scaffolding band (standard vs scaffolded `gradient_two_points`; lower-band vs higher-band `read_point`).
  - `interaction-request-preserved` — an explicitly requested interaction type is honoured (MC redrawn to an eligible draw, never silently downgraded to FR; `plot_point` MC rejected as unsupported).
  - `runtime-theme-does-not-change-content-hash` — switching viewer/export mode (premium/accessible/dark/light/print) does not change the canonical item or its `contentHash`.

### 13.4 Required premium gallery

The gallery proves the premium colour/visual-style layer is a faithful *presentation* over the *same* canonical geometry. Every gallery figure is generated from real `params` (no hand-authored SVG) and the colour layer renders strictly on top of the authoritative monochrome canonical SVG; colour never carries meaning alone.

| # | Gallery figure | Demonstrates |
| --- | --- | --- |
| G1 | A simple one-line graph | Baseline single `y=mx+c` line, clean axes/ticks. |
| G2 | Gradient spread | Five figures: positive, negative, **zero** (horizontal), integer-gradient, and exact-rational-gradient lines. Vertical lines are absent by construction. |
| G3 | Several points on one graph | Multiple `cx-pt-core`/`cx-pt-outline` lattice markers, non-overlapping labels. |
| G4 | ≥6 distinct lines on one graph | Six `--cx-series-1..N` series, each distinguishable in monochrome (dash/marker) before colour is added. |
| G5 | Dense stress-test | High line + tick + label density; collision-avoidance under load. |
| G6 | Overlapping / intersecting lines | Lines crossing inside the viewport (intersection point *not* solved/answered — simultaneous intersection is DEFERRED; this is render-only). |
| G7 | Labels near axes / boundaries | Tick labels and point labels at the viewport edges and adjacent to the axes; proves boundary collision logic and clipping. |
| G8 | LIGHT / DARK / accessible-colour / MONOCHROME | The same canonical figure in all four modes; the monochrome version is byte-identical to the authoritative canonical SVG. |
| G9 | Enlarged ZOOM view | A magnified region proving integer-coordinate sharpness (no sub-pixel blur; `gridRound` integers hold under scale). |
| G10 | High-resolution PNG export | One sample PNG **derived from the canonical SVG** by the committed integer-scale transform (§13.5 `pngDerivation`), proving the SVG → high-resolution raster path; the device dimensions are `floor(scale·vbW) × floor(scale·vbH)` for the committed integer `scale`. |

**Mode-equivalence is asserted over GIVENS and visual encodings, never "the answer."** For G8 the pack records, per mode, that the figure's **answer-free displayed givens and encodings are identical across all four modes**, recomputed from `params`: the set of {plotted lattice points, the drawn line's visible lattice crossings, tick positions and tick-label *text*, point-label and equation-label *text*, dash/marker semantics} is byte-identical across LIGHT/DARK/accessible/monochrome; only the presentation layer (palette tokens `--cx-series-1..N`, `--cx-axis`, `--cx-grid-major`, `--cx-grid-minor`, `--cx-pt-core`, `--cx-pt-outline`, `--cx-halo`, `--cx-bg`) differs. There is deliberately **no assessed answer encoded in any figure** (the gradient/intercept/midpoint/equation under test never appears — `no-answer-leakage`, §12); the only figure-encoded value is the *given* point itself, and only for `read_point`/`plot_point`. The monochrome canonical remains AUTHORITATIVE; this is asserted as a check (`render-mode-parity`, §13.5), not a visual judgement.

**v1.0.0 applicability note (honesty about what actually exercises).** Every v1.0.0 figure is monochrome-authoritative with at most one line and a few points. The multi-series colour apparatus (distinct-adjacent-series, the adjacency rule) is therefore **vacuously satisfied** for 0- or 1-series figures, and `no-colour-only-meaning` reduces to asserting `accessibility.nonColorIndicators === true` over the monochrome-authoritative canonical SVG (already covered by §12). The machinery is retained as reusable infrastructure (§15) for Statistics & Data Handling, but its v1.0.0 exercise is minimal; G4 (≥6 series) is the only figure that meaningfully stresses series distinction, and it does so in **monochrome first** (dash/marker), proving distinction survives colour removal.

### 13.5 Collision / parity / monochrome diagnostics

Mirroring the geometry pack's platform-gate summaries (`collisionInvariant`, `toScaleDiagnostic`, `monochrome`), the coordinate pack reports the following. Every diagnostic below is **exact and integer/set-based** — no floats, no rasteriser, no pixels — so it is deterministic and byte-identical across the Python oracle and the TS mirror.

- **Distractor collision / deterministic regeneration** (`collisionInvariant`): over a 10,000-seed MC sweep, the count of MC items with exactly three **distinct** misconception-backed distractors; violations must be `0`. When three distinct distractors cannot be formed, the param loop deterministically redraws (same seed → same accepted item). Zero-gradient `gradient_two_points` is excluded from the MC sweep population by construction (it is free-response-only; §13.2).
- **Label / marker collision diagnostic** (`labelCollisionDiagnostic`): over a sweep, the count of figures where any two `cx-lbl` / tick-label / point-label boxes overlap, or a label collides with an axis; target `0`. Computed with the integer box arithmetic from the angles labels engine (`ptBoxD2`/`boxesClear`). This is the coordinate analogue of the geometry `labels-non-overlapping` gate, exercised especially on G5 (dense) and G7 (boundary).
- **Vertical-line exclusion diagnostic** (`verticalLineExclusion`): over a sweep across all `y=mx+c` tasks, asserts the task-split invariant of §13.3 — for O3/O7, the count of accepted items whose two source x-values were equal must be `0` (the redraw fires before acceptance); for O5/O6, the count of accepted items whose `m` is not a finite reduced `Rational` (or whose O6 anchors share an x) must be `0`. This is the determinism proof for the hard constraint.
- **Equal-scale diagnostic** (`equalScaleDiagnostic`): over a sweep, assert `U_x = U_y` (identical integer px-per-unit on both axes) for every figure; violations `0`.
- **Render-mode parity diagnostic** (`renderModeParity`): over the gallery + a sweep, assert the canonical geometry (path/marker/tick coordinates and the answer-free displayed givens of §13.4) is byte-identical across LIGHT/DARK/accessible/monochrome (presentation-only divergence); violations `0`.
- **Grid-hierarchy-preserved diagnostic** (`gridHierarchyPreserved`): over every coloured mode, assert the resolved stroke widths satisfy `axis > major-grid > minor-grid` and that `--cx-grid-minor` differs from `--cx-grid-major` by **width AND dash pattern** (never opacity/lightness alone), so the coloured layer cannot collapse the monochrome hierarchy committed in §6.3 (`axes-stronger-than-grid` / `major-grid-stronger-than-minor`); violations `0`.
- **Premium-spec parity diagnostic** (`premiumSpecParity`): assert the serialized `media[].spec.premium` (style-contract version, palette ID, `seriesAssignment[]` ordering, marker/dash assignments, glow limits, legend) is **byte-identical** between the Python oracle and the TS mirror, gating the presentation style contract the same way `svg-realises-data` gates the SVG. The token tables and series-assignment ordering are committed constants (analogous to the angles `STYLE` constant) with Py/TS byte-parity. The viewer mode/theme is a presentation preference, not part of the stored spec (§16.1 a.6).
- **No-global-ids diagnostic** (`noGlobalIds`): assert that **every** premium/accessible/print SVG contains **no `id` attribute and no `url(#…)` reference** — halos, legends, series styling, and any panel gradients must be inlined or attribute-scoped, never `<defs>`/`<linearGradient id=…>`/`fill="url(#…)"`. This guarantees multiple premium figures inlined in one exported worksheet cannot collide on DOM ids (the same safety the canonical monochrome layer already has, §12); violations `0`.
- **Contrast / light-dark readability** (`contrastSufficiency`, `lightDarkReadability`): contrast is **not** recomputed per item from float sRGB luminance. It is computed **once, offline**, over the committed finite token table (the fixed LIGHT/DARK/accessible hex pairs), and the WCAG-AA pass/fail result is stored as committed booleans per token pair. The runtime/validator diagnostic then asserts **set membership** — every coloured figure uses only pre-verified token pairs — which is exact, integer/string-comparison-based, and cross-language identical. No item-time gamma-expansion float pipeline runs.
- **Visual-overload diagnostic** (`visualOverload`): over the dense figures, assert two integer-geometry conditions only — (1) min pairwise label-box clearance ≥ `MIN_LABEL_CLEARANCE_px` after the collision pass (exact integer boxes), and (2) marker **box-overlap** stays below `MAX_OCCLUSION`, defined as a box-overlap-area ratio over the committed integer marker bounding boxes (`ptBoxD2`/`boxesClear` arithmetic) — explicitly **not** rasterised "ink coverage." Both are deterministic and parity-safe; violations `0`.
- **Monochrome / no colour-only information** (`monochrome`): over a sweep of the **canonical** SVGs, the set of distinct inks used (greys/near-black only) is enumerated, and `colourOnlyInformation` is `false`. The premium colour layer is excluded from this scan because it is non-authoritative; its colour-independence is instead guaranteed by the monochrome-first distinction proof (dash/marker) of §13.4.
- **PNG-derivation diagnostic** (`pngDerivation`): an **exact analytic** check on the export transform only — no rasteriser, no pixels, no tolerance. With `scale = min(floor(7680/vbW), floor(4320/vbH))` (the committed integer scale; for the `1000×700` viewBox this is `min(floor(7.68), floor(6.171)) = 6`, giving `6000×4200`), assert for every canonical integer SVG coordinate `v` that `pngCoord = scale · v` exactly and that `pngCoord / scale` recovers `v` exactly under integer arithmetic. The diagnostic records the source seed and the SVG-hash → PNG-hash chain, proving the raster is *derived* from the canonical geometry, not independently drawn. An actual rendered-PNG visual spot-check is retained only as a **non-blocking, offline diagnostic** outside the Py/TS parity gate, produced by a single pinned rasteriser; it never gates generation, validation, parity, or the manifest.

All diagnostics are non-interactive, run inside the builder, and their summary values are written into both the `.json` and `.md` packs.

### 13.6 Manifest + artifact-integrity tests (mirroring geometry v1.2.3)

A generation manifest `docs/review/coordinate_manifest.json` is produced by `oracle/make_coordinate_manifest.py`, with the same schema shape as `geometry_manifest.json`:

- `schema: "spi-math-coordinate-manifest/1"`, `generatorId: "gen.geometry.coordinate-lines"`, `generatorVersion: "1.0.0"`, `validatorVersion: "1.0.0"`, `gitCommit`, `generatedAt`.
- `commands[]`: the exact reproduction sequence (`run_coordinate_lines.py` → `make_review_pack_coordinate_lines.py` → `make_visual_audit_coordinate.py` → `build-samples.mjs` (coordinate excluded while pending-review) → `make_coordinate_manifest.py`).
- `sha256{}`: SHA-256 of `reviewPackMd`, `reviewPackJson`, `visualAudit`, `goldenFixture`, `parityFixture`, and (once approved and included in samples) `sampleWorksheet`, `sampleAnswerKey`, `sampleSolutions`, `sampleBankJson`.
- `sha256SvgDir` (hash over the per-item SVG directory) + `svgCount`; an equivalent `sha256GalleryDir` + `galleryCount` for the premium gallery assets.

**`contentHash` and the premium spec — corrected.** `contentHash` is, per `schemas/question-item.schema.json`, the SHA-256 of the canonical serialized item, and `core/serialization/canonicalStringify` hashes the **entire** item object, including **every** key of `media[]` — `svg`, `spec` (and its `premium` style contract), `altText`, etc. There is no hash-exclusion mechanism in `core`. The pack therefore states plainly that **`media[].spec.premium` (the deterministic style contract — palette ID, `seriesAssignment[]`, marker/dash assignments, glow limits, legend) DOES fold into `contentHash`** — which is correct and desirable: it makes the deterministic presentation spec tamper-evident exactly as the canonical SVG is. **The user's selected viewer mode/theme is NOT stored as canonical content (§16.1 a.6), so switching modes does not change `contentHash`** (asserted by `runtime-theme-does-not-change-content-hash`). The earlier wording "only the canonical SVG folds into `contentHash`" is removed. The **PNG** is the only genuinely excluded artefact, and only because it is **never stored in the item JSON in the first place** (it lives under `coordinate_lines_gallery/`, referenced by hash in the `pngDerivation` chain, not embedded in `media[]`); the manifest covers it via `sha256GalleryDir`.

A blocking, TypeScript-side `domains/geometry/coordinate-lines/artifact-integrity.test.ts` mirrors the geometry test exactly:

- `audit-version-matches-generator`: manifest `generatorVersion` == imported `GENERATOR_VERSION` (`1.0.0`); audit `data-generator-version` == `GENERATOR_VERSION`; review pack `.md` states the current version.
- `audit-commit-matches-build`: audit `data-git-commit` == manifest `gitCommit`, and is a real `^[0-9a-f]{7,40}$` hash.
- `no-stale-version-text`: artifacts reference only the current version (no leftover pre-release strings).
- `manifest SHA-256 hashes match the serialized files`: recompute SHA-256 of each listed file and assert equality with `manifest.sha256[key]`. Stale artefacts fail the build.

---

## 14. Versioning and approval plan

### 14.1 Semantic version and scope

The generator is `gen.geometry.coordinate-lines`, **version `1.0.0`**, `validatorVersion` **`1.0.0`** (both verbatim, in `generatorId` / `generatorVersion` on every item and in the manifest). Semantic versioning governs evolution:

- **PATCH** (`1.0.x`): output-neutral fixes that do not change any generated item's bytes — comments, docs, non-emitting refactors. Golden/parity fixtures must remain byte-identical.
- **MINOR** (`1.x.0`): additive, backward-compatible capability that does not alter existing seeds' output (e.g. a new task added behind its own config, or a new render mode). Existing golden/parity bytes unchanged.
- **MAJOR** (`2.0.0`): any change to the bytes a given seed produces (params, solver, SVG geometry, answer canonicalisation). Requires fresh fixtures and a fresh owner approval.

**v1.0.0 scope is exactly the seven tasks** O1–O7 and nothing else. The deferred set is *deterministically excluded*, never silently included: distance with irrational roots; vertical lines `x=a`; parallel/perpendicular; simultaneous intersections; inequalities / shaded regions; function transformations; nonlinear graphs; scatter/regression; 3D coordinates. The vertical-line exclusion is enforced in-generator (for O3/O7, two equal x-values → deterministic redraw; for O5/O6, the finite-`m` `{m,c}` structural invariant) and proven by the task-split `verticalLineExclusion` diagnostic (§13.5).

**No invented schema fields.** v1.0.0 emits only schema-valid keys at every boundary. In particular `difficulty.axes` uses **only** the closed `difficultyProfile.axes` vocabulary (`numericalComplexity`, `reasoningSteps`, `abstraction`, `representation`; see §10), exactly as the approved angles family does; there is **no** schema change, and the §14.3 "Schema validation" gate (runtime Ajv, `additionalProperties:false`) passes for every emitted item. Likewise `answer.type` reuses the existing enum values (`coordinate`/`ordered-pair`, `exact-rational`/`integer`, `equation`) with no additions.

### 14.2 Oracle-first build order

Build proceeds oracle-first, exactly as the prior families:

1. **Python oracle is authoritative.** Implement params/solvers, exact-rational answers (via `fractions.Fraction`, mirroring `core/exact-math/rational.ts`), the canonical Cartesian renderer (`oracle/spi_oracle/cartesian.py` with integer `gridRound`, equal-scale U), and the MISC.COORD.* registry in `oracle/spi_oracle/coordinate_lines_misconceptions.py`.
2. **TypeScript mirrors the oracle** to BYTE-PARITY: `domains/geometry/coordinate-lines/*.ts`, `core/render/cartesian/*.ts`, and `domains/geometry/coordinate-lines/misconceptions.ts` reproduce identical bytes. Seeded RNG reuses `core/seeded-random/mulberry32.ts` ↔ `oracle/spi_oracle/seeded_random.py` (byte-identical streams already anchored). The new bivariate equation reduction (`core/exact-math/linexpr2.ts` ↔ its Python counterpart; §15) is implemented to the same byte-parity discipline.
3. **Driver** `oracle/run_coordinate_lines.py` (modelled on `run_geometry_angles.py`) emits the gate fixtures and runs the sweep.

### 14.3 Gates that must pass before the pack is presented

| Gate | Definition | Pass condition |
| --- | --- | --- |
| Golden (4) | `oracle/golden/coordinate_lines.golden.json` for seeds `1, 42, 123456789, 2147483647`; each item serialized + validated. | All `validate().status == pass`; TS re-serialises to byte-identical. |
| Parity (150 × 2) | `oracle/golden/coordinate_lines.parity.json` over seeds 1..150 × {free-response, multiple-choice}. | TS parity test reads the fixture and re-serialises byte-for-byte. |
| 10k sweep | `SPI_SWEEP=10000` × 2 modes; reproducibility re-check on the first 200 seeds. | `0` invalid items; reproducibility holds (same seed → same item). |
| Schema validation | Runtime Ajv (precompiled, offline) at the item boundary against `schemas/question-item.schema.json`, including the closed `difficulty.axes` enum. | Every emitted item validates. |
| Independent verification | `validate(item)` rebuilds the figure from `params` (`svg-realises-data`) and recomputes the answer by a second route (`closure-agreement`); 40+ checks. | All checks `pass`, TS+Py parity. |
| Accessibility | `apps/generator-studio/a11y.test.ts` (axe-core: 0 critical/serious; WCAG AA ≥ 4.5:1) over exported worksheets, which inline the **canonical monochrome** figures (§13.1). | 0 critical/serious. |
| Coordinate diagnostics | The collision, label-collision, vertical-line-exclusion (task-split), equal-scale, render-mode-parity, grid-hierarchy, premium-spec-parity, no-global-ids, contrast (token-membership), visual-overload (integer), monochrome, and PNG-derivation (integer-scale) diagnostics (§13.5). | All target `0` violations. |

Any non-zero failure writes `oracle/failing_seeds/coordinate_lines.failing.json` and blocks; the pack is not presentable until every gate is green.

### 14.4 Registration: pending-review, gated out

**Status summary (owner directive).** generator `gen.geometry.coordinate-lines`; implementation version `1.0.0`; validator `1.0.0`. **During implementation the objective status is `approved-for-implementation`** (the seven objectives + P0 are cleared to be authored and built), while the **generator registry status stays `pending-review`** until the review-pack decision. The generated-item lifecycle reaches **machine-validated only after all gates pass**, the family is **not exposed in normal Studio or production exports before final review-pack approval**, and there is **no auto-approval/publication of future items**.

The family is registered in `core/sdk/sequence-registry.ts` as a `GeneratorModule` entry with `approvalStatus: "pending-review"`, listing the seven tasks (`value`/`label`/`mc`) and wiring `generate`/`validate`/`serialize`. The `mc` flag is set to reflect §13.2: MC-eligible tasks are `true`; **`plot_point` is `mc: false` (free-response only; MC unsupported in v1.0.0)**; and `gradient_two_points` is registered `mc: true` with the explicit note that its **zero-gradient draws are always emitted free-response** (no three-distinct-distractor set exists at `m=0`, and an explicit MC request redraws away from `m=0`). Per the existing `generatorsForMode` / `approvedGenerators` logic:

- **Normal Studio** and **production exports/samples** do **not** see it (`pending-review` is returned only when `mode === "review"`; `approvedGenerators()` excludes it). `scripts/build-samples.mjs` therefore excludes coordinate-lines while pending-review, exactly as geometry was excluded pre-1.2.3.
- Review/developer mode can exercise it to build the pack.

There is **no auto-publication**: newly generated items begin and remain at `lifecycle.state = generated` (machine-validated); approval of the review pack does **not** auto-approve future items. The `approved-for-implementation` objective status authorises authoring/building the objectives and generator; it does **not** publish any generated item or flip the registry to `approved`.

### 14.5 On approval

When the owner APPROVES the review pack (a logged decision, mirroring `DECISION_LOG.md #40` for geometry):

1. Flip the registry entry to `approvalStatus: "approved"` with an inline comment citing the decision-log entry and date; the family becomes selectable in normal Studio and included in production exports/samples.
2. **Immutable fixtures**: the golden/parity fixtures and the approved `generate`/`validate`/`serialize` implementations are frozen as the approved, immutable artefacts; an **`approved-coordinate-lines-1.0.0`** tag is cut.
3. The **generation manifest** (§13.6) is regenerated for the approval commit, and the blocking `artifact-integrity.test.ts` pins the SHA-256 hashes.
4. Items still start machine-validated; advancing any item or objective to `curriculum-reviewed` / `approved` / `published` remains a per-item curriculum decision (the `reviewStatus` ladder on the objective and the item `lifecycle.state` are separate gates).

If the owner REJECTS, the registry entry's `approvalStatus` is set to `"rejected"` (never returned by any mode), the version is retired in history, and a remediated build proceeds under a new pre-release before re-presentation.

### 14.6 Roadmap note

After this family lands, **Statistics & Data Handling** is the next proposed architecture-proving family. It is chosen deliberately because it reuses this family's premium colour layer and the shared Cartesian renderer (§15), so it validates that the new reusable infrastructure generalises beyond straight-line graphs before further investment.

---

## 15. New reusable infrastructure versus family-specific infrastructure

This family is the first to introduce a Cartesian rendering stack and a premium colour layer. To keep the platform DRY and to de-risk Statistics & Data Handling, the build is split into **reusable** infrastructure (domain-independent, lives in `core/*`, shared by future Cartesian families) and **family-specific** infrastructure (the seven coordinate-line tasks and their bespoke checks, lives under `domains/geometry/coordinate-lines/*` and the family oracle modules).

| Component | Classification | Lives in | Why / reuse justification for Statistics & Data Handling |
| --- | --- | --- | --- |
| Cartesian grid / axes / tick / label renderer core | **Reusable** | `core/render/cartesian/` (+ `oracle/spi_oracle/cartesian.py`, byte-parity) | Scatter plots, line graphs, box plots, cumulative-frequency curves all need axes, ticks, gridlines on a `0 0 1000 700` viewBox with integer `gridRound` coordinates. Built once with the `.gl/.ga/.gx` discipline, generalised as `cx-*`. |
| Viewport + equal-scale algorithm (U px/unit, both axes) | **Reusable** | `core/render/cartesian/` | Computes the data-window → pixel mapping with equal x/y unit scale. Statistics figures that need true geometry (e.g. scatter with a fitted indicator) reuse it directly; those that intentionally use unequal scales call the same module with a per-axis U (an additive, backward-compatible parameter). |
| Clipping (lines/markers to the viewport) | **Reusable** | `core/render/cartesian/` | Any series extending beyond the data window must be clipped identically; shared so clipping is verified once. |
| Premium colour / visual-style layer + LIGHT/DARK/accessible/monochrome render modes | **Reusable shared-core library (NOT a standalone GeneratorModule)** | `core/visual-style/` | A **shared core library**, exercised through `gen.geometry.coordinate-lines`; it is **not** registered as a standalone `GeneratorModule` in `core/sdk/sequence-registry.ts` and has no approval status or lifecycle of its own (owner decision; §16.6). The palette tokens (`--cx-series-1..N`, `--cx-axis`, `--cx-grid-major`, `--cx-grid-minor`, `--cx-pt-core`, `--cx-pt-outline`, `--cx-halo`, `--cx-bg`) and the render modes are a presentation layer over *any* canonical monochrome figure, carried in `media[].spec.premium`. The committed token tables are byte-parity Py/TS constants (analogous to the angles `STYLE` constant), and their WCAG-AA contrast is pre-verified once, offline, as committed pass/fail booleans per token pair — so the runtime contrast check is exact set-membership, not a float luminance computation. Halo elements (`.cx-halo`) are emitted in premium mode only, immediately *before* the stroke/marker they back (lower z), carry a reserved non-geometry class the figure-parser ignores, and contain no `id`/`url(#…)`. **Statistics may reuse it once `gen.geometry.coordinate-lines` is approved**, which is the explicit motivation for sequencing it next. |
| PNG export (canonical SVG → high-resolution raster via committed **integer** scale) | **Reusable** | `core/visual-style/` (or `exporters/` raster path) | The SVG→PNG derivation is content-agnostic and uses an exact integer scale `scale = min(floor(7680/vbW), floor(4320/vbH))` with `pngCoord = scale·svgCoord` (no float rounding), so the `pngDerivation` check is analytic and parity-safe; Statistics figures export identically. |
| Visual-quality checks (equal-scale, render-mode parity, grid-hierarchy, premium-spec-parity, no-global-ids, label/marker collision, integer visual-overload, monochrome, integer-scale PNG-derivation) | **Reusable** | `core/render/cartesian/` + `core/visual-style/` (parity Py/TS) | These assert properties of *any* Cartesian + colour figure, not of straight lines specifically; all are exact integer/set-based (no rasteriser, no float luminance). Statistics inherits them unchanged. |
| Ordered-pair / coordinate answer checker | **Reusable** | `core/answer-checking/` (alongside `rational-checker.ts`) | Comparing `{x,y}` answers (exact, component-wise via `Rational`) is needed by midpoint here and by any coordinate-valued Statistics answer. |
| Bivariate linear-expression type `BiLinExpr` over {x, y} | **Reusable** | `core/exact-math/linexpr2.ts` (+ Python counterpart, byte-parity) | The existing `core/exact-math/linexpr.ts` is strictly **single-variable** (`a·x + b`; `normalize → A·x + B = 0`; `solveLinear` solves one unknown), so it cannot represent or reduce a two-variable form. `linexpr2` adds an exact-`Rational` bivariate type that parses `lhs = rhs` over {x, y} → `A·y + B·x + C = 0` and extracts `(m, c) = (−B/A, −C/A)`, **rejecting** `A = 0` (vertical / undefined-gradient input) as a property of the new module. It extends — does not reuse `solveLinear` — and the single-variable `LinExpr` is reused only for single-variable sub-parses. |
| `y = mx + c` equation answer checker | **Reusable** | `core/answer-checking/line-equation-checker.ts` | Built on `core/exact-math/linexpr2.ts`. Canonicalises and compares linear equations by `(m, c)` with `m, c` as exact `Rational`, collapsing all rearrangements (`y − 2x = 1`, `2y = 4x + 2`, `2x + 1 = y`) to one canonical `(m,c)` and rejecting vertical/undefined-gradient input. Reused by any family that answers with a straight-line equation (e.g. a line-of-best-fit *value*, should a later, in-scope family need it). |
| Label collision-avoidance (placement engine) | **Reusable** | `core/render/cartesian/` | Tick-label and point-label de-confliction over integer label boxes (the angles `boxMake`/`boxesClear`/`ptBoxD2` machinery, with a committed finite candidate ladder and fixed max radius so acceptance is deterministic and termination is guaranteed); every dense Statistics figure needs it. |
| The seven tasks + their params/solvers | **Family-specific** | `domains/geometry/coordinate-lines/` (+ family oracle) | `read_point`, `plot_point`, `gradient_two_points`, `midpoint`, `interpret_mx_c`, `equation_from_graph`, `equation_from_two_points` and their exact-rational solvers (gradient = Δy/Δx as `Rational`; midpoint as component `Rational`; `y=mx+c` recovery). Includes the vertical-line redraw rule and the zero-gradient-is-free-response-only rule for `gradient_two_points`. Not reused by Statistics. |
| MISC.COORD.* misconception registry | **Family-specific** | `oracle/spi_oracle/coordinate_lines_misconceptions.py` + `domains/geometry/coordinate-lines/misconceptions.ts` (byte-parity) | Coordinate-specific error rules (axis-swap, Δx/Δy inversion, sign-of-gradient, midpoint-as-difference, intercept/gradient confusion) with the task→[ids] eligibility map. Statistics has its own registry. |
| Per-task validator checks | **Family-specific** | `domains/geometry/coordinate-lines/validate.ts` (+ oracle parity) | `point-marker-on-lattice`, `line-clipped-to-viewport`, `figure-to-scale`, the task-split `vertical-line-excluded`, `closure-agreement` for each task's answer route, and the equation-canonicalisation check. Built on the reusable `svg-realises-data` mechanism but assert family semantics. |
| The review pack + builder | **Family-specific** | `oracle/make_review_pack_coordinate_lines.py` → `docs/review/coordinate_lines_*` | Selects family-representative seeds, the premium gallery, and the family diagnostics. Statistics writes its own pack with the same *shape*. |

**Net effect.** The straight-line family pays the one-time cost of standing up `core/render/cartesian`, `core/visual-style`, the two `core/answer-checking` checkers (ordered-pair and `y=mx+c`), and the new bivariate `core/exact-math/linexpr2.ts`; only the seven tasks, the MISC.COORD.* registry, the per-task validator checks, and the review pack are family-specific. Statistics & Data Handling then reuses the entire Cartesian renderer, viewport/equal-scale algorithm, clipping, the premium colour layer + render modes + integer-scale PNG export + the (exact, integer/set-based) visual-quality checks, the label collision engine, and the ordered-pair and `linexpr2`-backed equation checkers — which is precisely why it is proposed as the next architecture-proving family.


---

## 16. Premium high-resolution colour graphics

This section specifies the **premium colour graphics layer** for `gen.geometry.coordinate-lines` v1.0.0 (`validatorVersion` 1.0.0). "8K-like" is interpreted as **exceptionally sharp, dense, polished mathematical graphics**, not a large raster: the deliverable is a refined *vector* figure that scales losslessly to any DPI, with an optional raster export bounded inside a `7680×4320` envelope derived **from** the canonical SVG. Throughout, the rule from Section 6 holds without exception: the **monochrome-safe canonical SVG is authoritative**; colour is a presentation skin over the *same* committed integer geometry. Nothing here may change a single coordinate, alter byte-parity, or weaken the accessibility model of Section 12.

> **Layering invariant (CX-PREM-1).** The premium layer is a pure, deterministic function of `(canonicalGeometry, renderMode, theme, seriesAssignment)`. It MUST NOT recompute, refit, re-round, or re-order any geometry. Every `x`/`y` it emits is byte-identical to the value produced by `gridRound` over the exact `Rational` in the canonical builder (the single projection of record is §7.2; §6.2 is cross-referenced to it, not a second formula). The canonical monochrome SVG of Section 6 — `viewBox "0 0 1000 700"`, integer coordinates, equal `U` px/unit on both axes, class prefix `cx-` — is the single source of truth. If the premium layer and the canonical layer ever disagree on geometry, the canonical layer wins and the item fails validation.

> **Scope note for v1.0.0.** Every v1.0.0 figure is **monochrome-authoritative** with at most **one line and a few lattice points** (§16.4 opening). The multi-series apparatus below — series-colour assignment, the adjacency rule, collision-avoidant labelling, the overload metric — is therefore specified primarily as **reusable infrastructure** (§16.6) for Statistics & Data Handling, and several of its checks are **vacuously satisfied** in this release (called out per-check in §16.5). It is specified in full so the contract is fixed once and inherited, not re-derived.

### 16.1 Source-of-truth and export contract (a)

| Artifact | Role | Authority | Notes |
| --- | --- | --- | --- |
| **Canonical SVG** (`media[0].svg`) | The figure | **Authoritative; single source of truth** | Monochrome-safe, `cx-` classes, integers via `gridRound`, byte-parity (Py/TS). The artifact the exporters inline (§16.1 a.5). |
| **Premium style spec** (`media[0].spec.premium`) | Deterministic presentation **style contract** | Derived, but **tamper-evident** | Structured object `{ styleContractVersion, paletteId, seriesAssignment[], markerAssignment[], dashAssignment[], glowLimits, legend }` — the deterministic *style contract* only. It does **NOT** store the user's selected viewer mode or theme (those are presentation/export preferences, §16.1 a.6). Re-renders the premium/accessible/print skins deterministically; parity-checked Py↔TS; **folds into `contentHash`** with the rest of the item (§16.1 a.4, §16.6). |
| **Raster PNG** (optional) | Export-only convenience | Derived from the canonical SVG; **never stored in the item** | Fits inside the `7680×4320` **envelope** at an **integer** scale (`S = 6`, giving `6000×4200`); never an input to any check the SVG can answer; never the basis of an answer. Excluded from `contentHash` solely because it is **never serialised into the item JSON** (§16.1 a.4). |

**(a.1) Authoritative scalable SVG.** The figure is pure vector. The premium render reuses the canonical element list (axes, ticks, tick labels, major/minor grid, line(s), point core, point outline, labels, guides) under the `cx-` classes, recolouring and decorating via CSS custom properties — it adds **no new geometry primitives** and moves **no** coordinate. The committed canonical emission order of §6.4 is **unchanged**; the only premium-mode additions are decorative `.cx-halo` elements at reserved positions the figure-parser ignores (§16.3 c.4). The presentation is fully described by the `media[0].spec.premium` style contract so it regenerates deterministically and is itself parity-checked, never hand-authored.

**(a.2) High-DPI.** Because the figure is vector with no `width`/`height` on the root `<svg>` (physical size from the host stylesheet, mirroring Section 6 / §9 of the angles contract) and `preserveAspectRatio="xMidYMid meet"`, it is **resolution-independent**: crisp at 1×, on a 4K panel, on a 600-dpi print, and at the raster ceiling, with no re-layout. Stroke widths and font sizes are expressed in viewBox units so that at the smallest sanctioned physical size strokes stay ≥ ~0.3 mm and label text ≥ 8 pt (carried from the print contract).

**(a.3) Optional raster PNG export — integer scale only.** A deterministic exporter MAY rasterise the premium render to PNG for hosts that cannot consume SVG. To keep the path exact and reproducible across rasterisers, the scale is the **largest integer** that fits the `7680×4320` envelope:

```
S = min( floor(7680 / vbW), floor(4320 / vbH) )      # integer device-pixel scale
pngW = S * vbW ,  pngH = S * vbH                       # integer dimensions, exact
```

For the committed `viewBox "0 0 1000 700"`: `S = min(floor(7680/1000), floor(4320/700)) = min(7, 6) = 6`, giving a **`6000×4200`** PNG (the `4320` height is the binding constraint; the figure never reaches `7680` wide). Every canonical integer SVG coordinate `v` maps to device pixel `S·v` **exactly, with no rounding**; `pngCoord / S` recovers `v` exactly. Anti-aliased subpixel rendering is mandatory for line and point *edges*; grid and axis hairlines are pixel-snapped at scale `S` so they stay crisp. The exporter records `exportTransform = { scale: S, offsetX: 0, offsetY: 0 }`.

> The earlier float ratio `scale = min(7680/vbW, 4320/vbH)` and the worked figure "7680×5376" are **withdrawn**: a float multiply-and-round is rasteriser/locale/rounding-mode dependent and is exactly the step the platform forbids for canonical geometry. The integer-`S` rule above is the only sanctioned PNG transform.

**(a.4) Exact mathematical-coordinate preservation — analytic, not pixel.** Because `S` is integer and the map is `pngCoord = S · svgCoord`, coordinate preservation is an **exact analytic identity over integers**, checked from `exportTransform` alone (no rasteriser, no pixels, no tolerance): for every plotted point and axis-crossing, `S · v` is the device pixel and `(S·v)/S = v` recovers the canonical viewBox value exactly. This is what `png-coordinate-preservation` asserts (§16.5). **The mathematical SVG — not the PNG — is the single source of truth, and is the authoritative "8K-like" deliverable; the spec does NOT claim 1000×700 exports as 7680×4320.** The PNG is regenerable and is **excluded from `contentHash` because it is never written into the item JSON in the first place** — not because of any spec carve-out. (Contrast `media[0].spec.premium`, which **is** part of the item and therefore **does** fold into `contentHash`; the viewer mode/theme is not stored and never folds in — §16.1 a.6, §16.6.)

**(a.5) One stored artifact; modes are presentation-time re-renders.** The item stores exactly **one** rendered figure: `media[0].svg`, the canonical **monochrome** SVG. The viewer/export modes of §16.2 are not stored SVGs; they are deterministic re-renders from the `media[0].spec.premium` style contract. Consequently:
- The HTML exporters (`exporters/html/{worksheet,answer-key,solutions}.ts`, §12) inline the **canonical monochrome `media[0].svg`** verbatim. That single, authoritative, answer-free artifact is what the axe-core a11y gate exercises and what folds (with the rest of the item, including `spec.premium`) into `contentHash`.
- Premium and accessible colour skins are produced **only** at presentation time (Studio/preview; an opt-in colour worksheet theme) by re-rendering from `spec.premium`; they never replace `media[0].svg` and never become a second stored figure.

This removes any ambiguity about "which mode is stored" and keeps the axe-core gate and the stored `contentHash` unambiguous.

**(a.6) Viewer mode / theme are preferences, NOT canonical content.** The user's **selected mode/theme — premium, accessible, dark, light, print — are viewer/export preferences, NOT stored as canonical item content.** They are never written into `media[0].spec.premium` (which holds only the deterministic style contract: style-contract version, palette ID, series/marker/dash assignments, glow limits, legend config). **Switching modes at view/export time MUST NOT change the canonical item or its `contentHash`** — the canonical monochrome SVG, the answer, and every stored field are identical regardless of which skin a viewer chooses. Canonical student/print defaults remain **accessible + monochrome-safe**. This is asserted by the `runtime-theme-does-not-change-content-hash` check (§13.3, §16.5). **Premium colour export is a REAL selectable export option** (an opt-in colour worksheet/preview theme), not merely a review-gallery demo.

### 16.2 Coordinated viewer / export modes (b)

All modes render the **same** canonical geometry and coordinates from the same `params`; the mode is a **viewer/export preference** selected at presentation time and is **not** stored as canonical content (§16.1 a.6). The mode never changes which point is plotted, which line is drawn, the gradient, the intercept, or any label *value* — only how ink is styled — and never changes the `contentHash`. Per Sections 6.9 / 12 the figure in **every** mode is **answer-free**: it never encodes the gradient, intercept, midpoint, or equation being assessed (only `read_point`/`plot_point` encode a value, and that value is the *given* plotted point — and for `plot_point` not even that, since the student figure is a blank grid).

| Mode | viewer/export preference (not stored) | Palette | Encoding redundancy | Effects | Primary use |
| --- | --- | --- | --- | --- | --- |
| **Premium colour** | `premium` (preference label) | Rich-but-restrained `--cx-series-*`, luminous point cores, refined outline/halo, subtle depth on point markers | Colour **+** marker shape **+** line dash **+** label | Halo strictly **outside** the mathematical stroke (separate lower-z `.cx-halo` element); subtle highlight on `cx-pt-core`; no gradient on any mathematical stroke | On-screen Studio, premium worksheets, slide decks (a real selectable export option) |
| **Accessible colour** | `accessible` (preference label) | **CVD-safe** palette (deuter/prot/tritan-tested), AA-strong contrast | Colour **+** distinct line styles **+** distinct marker **shapes** **+** direct labels — **no colour-only information** | No glow; thicker outlines; larger markers | Default for any learner-facing colour render |
| **Print** | `print` (preference label) | Monochrome (single ink) or strictly limited spot colour | **Dash pattern + marker shape + label only** | **No glow, no gradient, no halo, no depth**; fully-opaque single ink | Canonical student/print default; worksheets, exam papers, monochrome laser |

> **Mode equivalence (CX-PREM-2).** For a fixed item, the three modes MUST all decode to the **same canonical geometry and the same displayed givens** — not "the same answer" (there is no answer in the figure to decode; the figures are answer-free per §6.9/§12). Concretely, `mode-equivalence` (§16.5) re-derives the canonical figure from `params` and asserts that the set of **{plotted lattice points, the drawn line's visible lattice crossings, tick positions and tick-label text, point/equation-label text, dash-pattern semantics, marker-shape semantics}** is **identical** across premium, accessible, and print. For `read_point`/`plot_point` the only figure-encoded value is the **given point** itself, and it must coincide in all three modes. Print mode is the floor: anything that survives only in colour is a defect.

### 16.3 Visual-style contract — tokens (c)

A single committed token table governs every premium render (light and dark). Tokens are **presentation only**; the validator never reads a token to recover a mathematical value. Colour is **always** paired with a non-colour channel (line style, marker shape, label, or pattern) so meaning never depends on hue alone (1.4.1). Gradients are permitted **only** on non-mathematical surfaces (background panel, legend chip backing) — **never** on an axis, grid line, plotted line, or marker — and any such gradient is **inlined/element-scoped** with **no `id`** and **no `url(#…)`** reference (§16.5 `no-global-ids`), so multi-item worksheet export cannot collide.

**(c.1) Palette tokens — contrast pre-verified offline, set-membership at runtime.** Tokens are CSS custom properties with light/dark pairs. WCAG contrast — `(L1+0.05)/(L2+0.05)` over gamma-expanded sRGB luminance — is a **float** computation and is therefore **never** recomputed per item at runtime. Instead it is computed **once, offline**, over the committed finite token table; each light/dark pair is admitted only if it passes, and the result is stored as **committed pass/fail booleans** alongside the token constant (the "pre-validated token pairs" rule). At runtime, `contrast-sufficiency` and `light-dark-readability` (§16.5) reduce to an **exact set-membership assertion** — "the item uses only pre-verified token pairs" — which is deterministic and byte-identical Py↔TS. The gates below are the offline admission criteria, not a runtime float computation:

| Token | Meaning | Offline admission gate |
| --- | --- | --- |
| `--cx-bg` | Figure background (may carry a subtle non-mathematical gradient) | — |
| `--cx-axis` | Axis ink | ≥ 3:1 non-text vs `--cx-bg` (1.4.11) |
| `--cx-grid-major` | Major gridlines | ≥ 3:1 vs `--cx-bg` |
| `--cx-grid-minor` | Minor gridlines | distinct from major by **width AND dash**, not opacity/lightness-only |
| `--cx-series-1 … --cx-series-N` | Line/point series colours | ≥ 3:1 vs `--cx-bg`; **adjacency rule** below |
| `--cx-pt-core` | Point fill | ≥ 3:1 vs `--cx-bg` and vs its line |
| `--cx-pt-outline` | Point contrast ring | resolves overlaps; ≥ 3:1 vs both adjacent fills |
| `--cx-halo` | Glow colour (premium only) | decorative; carries no meaning |
| `--cx-lbl` | Label text | ≥ **4.5:1** vs `--cx-bg` (1.4.3) |

**(c.2) Series-colour assignment.** Colours are assigned **automatically** from a tested high-contrast ordered palette by series index (deterministic; carried in `media[0].spec.premium.seriesAssignment[]` as `{ seriesId, colorToken, markerShape, dashPattern, labelText }`, ordered by `seriesId`). The token table and this assignment ordering are **committed constants with Py/TS byte-parity** (analogous to the angles `STYLE` constant), gated by `premium-spec-parity` (§16.5). The **adjacency rule** (enforced by `distinct-adjacent-series`, §16.5): any two series that are *neighbouring or intersecting* in the plotting box MUST differ in perceptual colour distance **and** in at least one non-colour channel (marker shape **or** dash pattern). The palette ordering is pre-tested so the first N picks are mutually high-contrast; if N exceeds the tested palette length, see §16.4 — the layer never silently recycles confusingly-similar colours. *(v1.0.0: 0 or 1 series per figure, so this is vacuously satisfied — see §16.5.)*

**(c.3) Line/marker/grid/axis hierarchy.**

| Element | Width (viewBox units) | Marker / dash | Hierarchy rule |
| --- | --- | --- | --- |
| Axis (`cx-axis`) | widest non-series | solid | **axes > major grid > minor grid** (visual weight strictly decreasing) |
| Major grid (`cx-grid-major`) | medium | solid or sparse dash | lighter than axis |
| Minor grid (`cx-grid-minor`) | thinnest | finer dash / lighter | distinct from major by width **AND** dash, never opacity-only |
| Line series (`cx-line`) | bold, above grid | per-series dash pattern | sits above grid, below points/labels |
| Point core (`cx-pt-core`) | — | per-series marker shape (circle, square, triangle, diamond, …) | crisp, luminous in premium |
| Point outline (`cx-pt-outline`) | thin ring | contrast halo where lines overlap | always present in accessible/print |

The §6.3 monochrome invariant `width(.cx-axis) > width(.cx-grid-major) > width(.cx-grid-minor)` (plus greyscale-darkness order) is re-asserted **for every coloured mode** by the new `grid-hierarchy-preserved` check (§16.5), so the colour layer cannot collapse the hierarchy the monochrome layer guarantees.

**(c.4) Highlight / glow LIMITS — committed z-order.** Glow/highlight (`--cx-halo`, premium only) is emitted as a **separate decorative element with the reserved class `.cx-halo`**, placed in the deterministic emission order **immediately before** the `.cx-line` / `.cx-pt-core` it backs (lower z), so it sits *behind and outside* the mathematical stroke and **never changes the apparent position or thickness** of the line or marker. `.cx-halo` is the one class the §8 figure-parser is committed to **ignore as geometry**. The canonical (monochrome) emission order of §6.4 is **unchanged**: halos are purely *additive* in premium mode and entirely **absent** in accessible and print modes. The `glow-outside-stroke` check (§16.5) asserts the invariant constructively: **stripping every `.cx-halo` element from the premium SVG yields a byte string identical to the canonical monochrome SVG's geometry stream.**

**(c.5) Typography & legend.** Labels use the platform display/UI stack at sizes fixed in viewBox units (≥ 8 pt at the smallest sanctioned physical size). Legend layout is a committed, deterministic block (`media[0].spec.premium.legend`): one row per series with `{ markerShape swatch, dashPattern swatch, colorToken, labelText }` — the swatch shows **both** the colour and the non-colour channels so the legend itself is colour-independent and **searchable** (entries ordered by `seriesId`).

**(c.6) Light & dark backgrounds; element states.** Every token has a light and a dark value, both contrast-verified offline (c.1). The layer defines four orthogonal element states as presentation modifiers (never geometry changes), used by interactive mode (§16.4):

| State | Visual treatment | Constraint |
| --- | --- | --- |
| `selected` / `focused` | emphasised: thicker stroke, brighter core, optional halo (premium) | underlying coordinates unchanged |
| `muted` | de-emphasised: reduced weight, retains marker shape + label | still ≥ 3:1; meaning still readable |
| `disabled` | greyed, non-interactive | paired with text/label, not colour-only |

### 16.4 Many-line / point handling and interaction (d)

v1.0.0 tasks plot few primitives (a point for `read_point`/`plot_point`/`midpoint`; one line plus up to two lattice points for `gradient_two_points`, `interpret_mx_c`, `equation_from_graph`, `equation_from_two_points`). The premium layer is nonetheless specified for **density**, because it is **reusable infrastructure** (§16.6) and Statistics & Data Handling will plot many series.

**(d.1) Auto colour + style variation.** Series get colour from the tested palette by index (§16.2); marker **shape** and line **dash pattern** vary in lockstep so neighbouring/intersecting series are distinguishable in greyscale and under CVD (the adjacency rule, §16.3).

**(d.2) Legend + direct labels.** A clean, searchable legend (§16.5 `legend-complete`) lists every visible series. Optionally, **direct end-of-line labels** are placed at each line's right-hand exit point; an **automatic label-placement + collision-avoidance** pass shifts labels along a small **committed, finite candidate-offset ladder** (deterministic, ordered, seeded by `seriesId`) until no two label bounding boxes intersect — reusing the exact-integer bounding-box discipline and the bounded candidate ladder from the angles `labels-non-overlapping` guard (finite list + fixed maximum radius; **no unbounded radial scan**; accept the first feasible candidate; on exhaustion fall back to legend-only and emit a `warn`, never an overlapping render).

**(d.3) Overlap halos.** Where lines or points overlap, `cx-pt-outline` contrast halos and point outlines keep markers visible against crossing strokes (enforced by `point-visibility`, §16.5).

**(d.4) Interactive mode — Studio-only, NOT a v1.0.0 a11y-claimed surface.** In Studio/preview **only** (never in print, never in any exported worksheet/answer-key/solutions HTML, never in the canonical artifact), the layer supports **highlight / dim / hide / isolate a series**: hover or keyboard focus emphasises the selected series (`focused`) and de-emphasises others (`muted`), with optional **zoom/pan without distortion** (the affine zoom preserves equal x/y unit scale `U`; it never re-rounds geometry). All interaction is **presentation only**: it preserves the underlying data and coordinates, and hiding a series toggles visibility without deleting it from `media[0].spec.premium.seriesAssignment[]`.

Because **no learner-facing exported artifact** contains the interactive surface (the §12 axe-core gate runs over the static exported HTML, which inlines only the canonical monochrome SVG, §16.1 a.5), v1.0.0 makes **no WCAG-conformance claim for interactive mode** and asserts no interactive-a11y gate it cannot exercise. Interactive mode is scoped as a **deferred Studio-only convenience**. If and when it is promoted to a learner-facing surface, it must first be wired into `apps/generator-studio`'s axe-core/a11y test with explicit blocking checks (keyboard-operable 2.1.1, visible focus 2.4.7, `prefers-reduced-motion` honoured 2.3.3, live-region announcement 4.1.3) — until then those properties are engineering guidance, not gated guarantees.

**(d.5) Overload metric and threshold (REPORT, do not silently render) — exact integer geometry only.** When density is too high to render legibly, the layer **reports `visually-overloaded`** rather than emitting an unreadable figure. Every sub-condition is computed deterministically from the **canonical geometry and committed `spec`**, using the **exact-integer box arithmetic** of the angles labels engine (`ptBoxD2` / `boxesClear` over integer bounding boxes) — **no rasterising, no "ink coverage"**:

```
overload =  ( seriesCount > MAX_SERIES )
        OR  ( min pairwise label-box clearance < MIN_LABEL_CLEARANCE_px  after the collision pass )
        OR  ( markerBoxOverlapRatio > MAX_OCCLUSION )
              # markerBoxOverlapRatio: over committed integer marker bounding boxes,
              # the fraction of marker boxes whose integer box-overlap area with ANY
              # other marker box is >= MAX_OCCLUSION of the box's own area
              # (equivalently: its centre lies inside another marker box).
              # Pure integer-box test; no pixels, no ink.
        OR  ( distinct (colorToken × markerShape × dashPattern) combinations exhausted )
```

with thresholds that are **PROVISIONAL engineering defaults, NOT a permanently approved cross-domain standard** (owner decision): `MAX_SERIES = 12` (the tested palette length); `MIN_LABEL_CLEARANCE_px = 8` (mirroring the angles 8 px clearance); `MAX_OCCLUSION = 0.5` (a **box-overlap-area ratio over integer boxes**). These three values are to be **re-evaluated during the Statistics stress-test pilot** before they are treated as a stable shared-infrastructure standard. On overload the render returns `{ status: "visually-overloaded", reason, metric }`; the orchestrator may down-scope (fewer series per figure), and the item is **not** silently rendered. This is a blocking `visual-overload` outcome (§16.5). *(v1.0.0: ≤ 1 line + few points, so overload is statically unreachable — it stays as reusable infrastructure.)*

### 16.5 Automated visual-quality checks (e)

Every check below is **blocking** (any `fail` ⇒ `validation.status = fail`; the item never reaches `lifecycle.state = machine-validated` and never enters offline export), runs in **both** the Python oracle and the TS mirror with **byte-identical results**, and appears as a named entry in `lifecycle.validation.checks[]` with `{ name, result: pass|fail, detail }` under `validatorVersion 1.0.0`. Crucially, **every check operates on the canonical geometry and the committed premium `spec`, never on rendered pixels** — so they are deterministic and cross-language identical. Contrast and PNG checks are **exact set-membership / integer-identity** assertions (per §16.1 a.4 and §16.3 c.1), never float comparisons or screenshot diffs.

| Check name | Asserts |
| --- | --- |
| `contrast-sufficiency` | The item uses **only token pairs from the committed, offline-contrast-verified table** (set membership) — equivalently every text label ≥ 4.5:1 (1.4.3) and every axis/grid/series/marker ≥ 3:1 non-text (1.4.11) vs `--cx-bg`, by the offline admission booleans, in **both** light and dark themes. No per-item float luminance computation. |
| `distinct-adjacent-series` | Any two neighbouring or intersecting series differ in perceptual colour distance **and** in marker shape or dash pattern (§16.3 adjacency rule). **Vacuous for v1.0.0** (≤ 1 series); reported `pass`. |
| `no-colour-only-meaning` | Every answer-relevant distinction is carried by line style, marker shape, label, or pattern **in addition** to colour (1.4.1); asserts `accessibility.nonColorIndicators === true`. **For v1.0.0's single-series, monochrome-authoritative figures this reduces to** `nonColorIndicators === true` **plus the authoritative monochrome canonical SVG** (already covered by §12) — there is no colour-encoded distinction to pair. |
| `point-visibility` | Every plotted point's `cx-pt-core` + `cx-pt-outline` is visible (not fully occluded) against grid, lines, and crossing series; halos present where overlap occurs (integer-box test). |
| `line-visibility` | Every line is drawn above the grid, meets minimum width, and is not hidden behind another series along its full extent. |
| `label-collision` | No two label bounding boxes intersect after the collision-avoidance pass (exact-integer box test; clearance ≥ `MIN_LABEL_CLEARANCE_px`). |
| `legend-complete` | The legend lists **every** visible series exactly once with marker, dash, colour, and label; ordering deterministic by `seriesId`; no orphan/missing entries. |
| `clipping` | No primitive, marker, halo, or label is clipped by the viewBox or panel edge. |
| `graph-boundary-clearance` | Every point, line endpoint, and label box clears the plotting-box boundary by the committed margin (mirrors the angles `within-canvas` / clearance discipline). |
| `grid-hierarchy-preserved` | **In every coloured mode**, resolved stroke widths satisfy `axis > major grid > minor grid`, and `--cx-grid-minor` differs from `--cx-grid-major` by **width AND dash pattern** (never opacity/lightness alone). Re-asserts the §6.3 invariant on the premium spec, which the §8 monochrome checks do not reach. |
| `high-dpi-rendering` | The render is pure vector with no rasterised mathematical primitive; stroke widths/font sizes in viewBox units satisfy the minimum physical size; no `<image>` for geometry. |
| `svg-scalability` | Root `<svg>` declares `viewBox "0 0 1000 700"`, `preserveAspectRatio="xMidYMid meet"`, no `width`/`height`; scaling 1× → ceiling introduces no re-layout and no coordinate change. |
| `no-global-ids` | The premium SVG (and its `spec`-driven render) contains **no `id` attribute** and **no `url(#…)` reference**; any panel/legend gradient is inlined or element-scoped. Prevents id collisions when multiple items are inlined into one worksheet (Section 12). |
| `premium-spec-parity` | The serialized `media[0].spec.premium` (`styleContractVersion, paletteId, seriesAssignment[]`, marker/dash assignments, `glowLimits, legend`) and the committed token/assignment constants are **byte-identical across the Python oracle and the TS mirror** — gating the presentation style contract exactly as `svg-realises-data` gates the SVG. (The viewer mode/theme is not part of this stored spec, §16.1 a.6.) |
| `png-export-dimensions` | If a PNG is exported, dimensions are **integer** `S·vbW × S·vbH` with `S = min(floor(7680/vbW), floor(4320/vbH))` (`6000×4200` for the committed viewBox); ≤ `7680×4320`. |
| `png-coordinate-preservation` | **Exact integer identity over `exportTransform`, no rasteriser, no pixels, no tolerance:** for every canonical integer SVG coordinate `v`, the PNG device pixel is `S·v` exactly and `(S·v)/S = v` recovers `v`. (An optional rendered-PNG visual audit, if ever wanted, is a **non-blocking offline diagnostic** outside the Py/TS parity gate, produced by one pinned rasteriser; it is not this check.) |
| `light-dark-readability` | All `contrast-sufficiency` and `no-colour-only-meaning` guarantees hold in **both** light and dark themes — by the committed token-pair set membership (both members pre-verified offline), not a runtime float recompute. |
| `monochrome-print-readability` | In `print` mode every **displayed distinction** (the answer-free givens, dash semantics, marker semantics, label text) survives as dash pattern + marker shape + label with **no** glow/gradient/halo/opacity-only encoding; fully-opaque single ink; the print figure **decodes to the same displayed givens** as colour. (No "answer" is decoded — the figure is answer-free per §6.9/§12.) |
| `mode-equivalence` (CX-PREM-2) | premium, accessible, and print renders all decode to the **same canonical geometry and the same displayed givens** — `{plotted points, visible lattice crossings, tick positions/labels, point/equation-label text, dash/marker semantics}` recomputed from `params` and identical across modes. The canonical monochrome SVG is the floor. **No "same answer" language**; the figures carry no answer. |
| `glow-outside-stroke` (CX-PREM-1) | Stripping every `.cx-halo` element from the premium SVG yields a geometry byte-stream **identical** to the canonical monochrome SVG; the halo is a separate lower-z decorative element outside the stroke carrying the reserved non-geometry class. |
| `runtime-theme-does-not-change-content-hash` | Selecting a different viewer/export mode (premium / accessible / dark / light / print) at presentation time **does not change the canonical item or its `contentHash`**; the mode/theme is a preference and is never stored as canonical content (§16.1 a.6). |
| `visual-overload` | The §16.4 overload metric (exact integer-box arithmetic) is below threshold; otherwise the item reports `visually-overloaded` and is blocked from export rather than silently rendered. **Statically unreachable in v1.0.0** (≤ 1 line + few points). |

These run **alongside** (not instead of) the existing geometry gates: the canonical `svg-realises-data` byte-parity check, `closure-agreement` (answer recomputed by a second route), runtime schema validation at the boundary (the premium layer adds **no** new `difficulty.axes` keys and introduces **no** schema change — `media[0].spec.premium` is already a permitted unconstrained `mediaAsset.spec` object), the misconception-distractor checks, the ≥ 10,000-seed `SPI_SWEEP` stability sweep (× 2 modes, 0-invalid target, reproducibility re-check on the first 200 seeds), and the axe-core a11y gate (0 critical/serious, WCAG AA ≥ 4.5:1) over the inlined **canonical monochrome** SVG. The premium layer **adds** checks; it removes none.

### 16.6 Tie-back, accessibility, parity, and reuse

- **Colour is presentation; the canonical SVG is authoritative.** Per Section 6, the monochrome-safe canonical SVG (`viewBox "0 0 1000 700"`, integer coordinates via `gridRound`, equal `U` px/unit, `cx-` classes, byte-identical Py/TS) remains the single source of truth and the only **rendered figure** the exporters inline. The premium layer is a deterministic, parity-checked style contract in `media[0].spec.premium`; it never moves a coordinate, never re-rounds, and never becomes the basis of an answer. The viewer's chosen mode/theme is a presentation preference, never canonical content (§16.1 a.6).
- **`contentHash` covers the whole item, including `media[0].spec.premium`.** `contentHash` is the sha256 of the **canonical serialized item**; `media[0].spec.premium` (the deterministic style contract) is part of the item (`mediaAsset.spec` is a permitted object) and therefore **folds into `contentHash`** along with `media[0].svg`. This is **desirable**: it makes the deterministic presentation spec **tamper-evident** exactly like the SVG. **The user's selected viewer mode/theme is NOT canonical content (§16.1 a.6) and never folds into `contentHash`; switching modes leaves the canonical item and its hash unchanged** (`runtime-theme-does-not-change-content-hash`, §16.5). The earlier wording that "only the canonical SVG folds into `contentHash`" and that the premium spec is "excluded" is **withdrawn**. The **PNG** is genuinely outside `contentHash` for one reason only — it is **never serialised into the item JSON**; there is no spec-level hash carve-out anywhere in `core`, and this section does not invent one.
- **No weakening of byte-parity.** Because the premium render and its `spec` are deterministic functions of the canonical geometry and committed token/assignment constants, they are serialized into canonical JSON and parity-checked Python ↔ TS exactly like the canonical SVG (`premium-spec-parity`, §16.5). One differing byte fails CI. The PNG is regenerable and excluded from parity/hash (it is never stored).
- **No weakening of accessibility (Section 12).** Every premium render keeps `accessibility.{spokenMath, altText, longDescription, nonColorIndicators}`; the figure stays **answer-free** in all modes (no gradient/intercept/midpoint/equation encoded — only `read_point`/`plot_point` show their *given* point). The `no-colour-only-meaning`, `light-dark-readability`, `monochrome-print-readability`, and `grid-hierarchy-preserved` checks make the colour layer *strengthen* rather than dilute the 1.4.1 / 1.4.3 / 1.4.11 guarantees. The interactive surface is **Studio-only and makes no learner-facing WCAG claim** in v1.0.0 (§16.4 d.4); the data-table fallback and long description remain complete substitutes for the figure.
- **Initial lifecycle unchanged.** Items with a premium render still begin at `lifecycle.state = generated` and reach `machine-validated` only after **all** gates (including the §16.5 checks) pass; colour never auto-approves or auto-publishes anything.
- **REUSABLE INFRASTRUCTURE — implemented as a SHARED CORE LIBRARY, not a standalone GeneratorModule (owner decision).** This premium colour layer (committed token table, the coordinated viewer/export modes, series-assignment + adjacency rule, collision-avoidant labelling with a bounded candidate ladder, integer-box overload metric, the integer-`S` PNG transform, and the §16.5 visual-quality checks) is implemented as a **shared core library** — `core/visual-style/` and `core/render/cartesian/` — and is **NOT registered as a standalone `GeneratorModule`** in `core/sdk/sequence-registry.ts`. It is **exercised through `gen.geometry.coordinate-lines`** (which itself stays `pending-review`, gated out of normal Studio and production until owner approval); it has no registry entry, no approval status, and no lifecycle of its own. **Statistics & Data Handling may reuse it once `gen.geometry.coordinate-lines` is approved** — Section 15 records it as a shared-core cross-family dependency so the Statistics proposal inherits the contract (including `premium-spec-parity`, `no-global-ids`, the offline-committed contrast tables, and the integer PNG scale) rather than re-deriving it.


---

## Appendix A — Resolved owner decisions (decision record)

These design choices were surfaced during authoring + adversarial review. **The owner has now RESOLVED every one of them in the APPROVE-WITH-REQUIRED-REVISIONS directive of 2026-06-23**; the resolutions are recorded below and have been applied throughout the body of this spec. This appendix is retained as the decision record (it is no longer a list of open questions).

1. **RESOLVED — APPROVED.** The new prerequisite objective **P0 `SPI.MIDDLE.GEO.COORD.CARTESIAN_PLANE.01`** is approved as the shared foundation, with final wording: *"Identify and use the x-axis, y-axis, origin, and four quadrants of the Cartesian plane, including interpreting positive and negative coordinates."* (§2; canonical answer type `coordinate`.)
2. **RESOLVED.** O5 `interpret_mx_c` carries its `(m, c)` value as a **`Line {m, c}` object under `answer.type = equation`** (canonical `y=mx+c`, `equivalentForms` exposing m and c). The student responds via two labelled fields ("Gradient m", "y-intercept c"); the full equation need not be rewritten unless asked; answer display `"m = ..., c = ..."`; a full equivalent equation may be accepted as an optional equivalent response. (§2, §3, §5.)
3. **RESOLVED.** Per-objective `difficultyRange`s are fixed as: CARTESIAN_PLANE 1; READ_POINT 1–2; PLOT_POINT 1–2; GRADIENT_TWO_POINTS 2–4; MIDPOINT 2–3; INTERPRET_MX_C 2–3; **EQUATION_FROM_GRAPH 3–4**; EQUATION_FROM_2PTS 3–5. (§2, §10.)
4. **RESOLVED.** The constants `COORD_MAX_X = COORD_MAX_Y = 10` are **sampling-domain bounds, NOT a fixed `[-10,10]` render window.** The deterministic dynamic viewport of §7 is retained; the doc no longer conflates SAMPLING bounds with RENDERED viewport bounds (every former `X_MAX`/`Y_MAX` is renamed). Renderer constants are pinned: `VIEW_W=1000`, `VIEW_H=700`, `PAD=40`, `U_MIN=24`, `DATA_MARGIN_UNITS=1`, `MAX_LABELS_PER_AXIS=11`, `LBL_CLEAR=8` (§7.6; revisable only before fixtures freeze if the visual audit shows a clear problem).
5. **RESOLVED.** The gradient denominator set stays `{1, 2, 3, 4}` and is **not expanded in v1.0.0** (§4.2, §7.6).
6. **RESOLVED.** Canonical answer type is fixed per task: `read_point`/`plot_point`/`CARTESIAN_PLANE` → `coordinate`; `midpoint` → `ordered-pair`; `gradient_two_points` → `integer`/`exact-rational`; the equation tasks → `equation`. `answerTypes[]` carries mathematical types only (no `multiple-choice`). (§1, §2, §3.)
7. **RESOLVED.** O5 is delivered as the canonical `Line {m, c}` `equation` answer with the two-field structured response ("Gradient m", "y-intercept c") as the canonical interaction; a full equivalent equation is an accepted optional form. (§2, §3, §5.)
8. **RESOLVED.** Minor grid is **half-units only — NO quarter-unit grid.** The half-unit minor grid is shown only when `U ≥ 32` and suppressed when `U < 32`. (§6.6.)
9. **RESOLVED.** `MAX_LABELS_PER_AXIS = 11`, `PAD = 40`, `U_MIN = 24` (and the rest of the renderer constants) are pinned in §7.6 so the parity fixtures are reproducible.
10. **RESOLVED.** The single `equation` answer.type is acceptable for both the O5 `Line {m, c}` value and the O6/O7 full `y=mx+c`; O5 carries the two-field display contract (`"m = ..., c = ..."`) while the canonical object remains `Line {m, c}`. (§3, §5.)
11. **RESOLVED — PROVISIONAL.** `MAX_SERIES = 12`, `MIN_LABEL_CLEARANCE_px = 8`, `MAX_OCCLUSION = 0.5` are **provisional engineering defaults**, to be **re-evaluated during the Statistics stress-test pilot**; they are NOT a permanently approved cross-domain standard. (§16.4 d.5.)
12. **RESOLVED — APPROVED.** The deterministic premium style is carried under **`media[].spec.premium`** (style-contract version, palette ID, series/marker/dash assignments, glow limits, legend config), with `media[].svg` remaining the authoritative canonical monochrome SVG. The user's selected viewer mode/theme is a presentation preference, not canonical content, and never changes `contentHash`. (§16.1.)
13. **RESOLVED.** The PNG ceiling `7680×4320` is an **ENVELOPE**; the canonical high-res raster uses the largest integer scale that preserves the `1000×700` aspect: `S = min(floor(7680/1000), floor(4320/700)) = 6`, i.e. **`6000×4200`**. The spec does NOT claim `1000×700` exports as `7680×4320`; the SVG is the authoritative "8K-like" deliverable. (§16.1 a.3/a.4.)
14. **RESOLVED.** The premium colour layer is implemented as a **shared core library** (`core/visual-style/`, `core/render/cartesian/`) and is **NOT** registered as a standalone `GeneratorModule`; it is exercised through `gen.geometry.coordinate-lines` while that family is pending review, and Statistics may reuse it once coordinate-lines is approved. (§15, §16.6.)
15. **RESOLVED — APPROVED.** A semantic misconception ID (e.g. `GRADIENT_INVERTED`, `READS_X_INTERCEPT`) **may be reused across tasks** when the underlying error is the same, recording the task separately in analytics; the reused ID must still have one defined conceptual error, a task-specific deterministic value adapter, task-appropriate feedback, and independent semantic validation. **Do NOT mint duplicate task-scoped IDs** for reporting convenience. (§9.)
16. **RESOLVED.** The difficulty model uses the **FOUR-axis weighting** `numericalComplexity 0.30, exactVsApproximate 0.20, reasoningSteps 0.25, abstraction 0.25`. The **stale five-weight reference "0.15/0.20/0.15/0.25/0.25" is removed.** A **≥ 10,000-seed distribution report** (per task: band counts/percentages, unreachable bands, over-concentrated bands, redraw rate, integer-vs-rational distribution, positive/negative/zero gradient distribution) must be produced before fixtures freeze; the weights/divisors are approved only **provisionally** until that report shows suitable coverage. (§10.)
17. **RESOLVED — APPROVED.** Horizontal lines / zero gradient are ALLOWED, including `y=c` lines in `interpret_mx_c` and `equation_from_graph`, but **FREE-RESPONSE is used whenever the horizontal case cannot field three strong distinct MC distractors** — which for `gradient_two_points` is always (zero-gradient O3 is FR-only). (§9, §11, §13.)

## Appendix B — Cross-section consistency notes (for human double-check)

1. **RESOLVED.** Strand naming: this proposal's fixed identifiers set strand = 'coordinate-geometry-straight-line-graphs', distinct from the existing geometry strand 'angles-lines-triangles-quadrilaterals'. The owner has **approved** this as a genuinely new, second geometry strand (§1). A **curriculum-schema test will assert the new strand value 'coordinate-geometry-straight-line-graphs' is accepted** by any strand enum / controlled vocabulary in schemas/curriculum-objective.schema.json.
2. **RESOLVED.** Objective ID depth: O1-O7 use SPI.MIDDLE.GEO.COORD.<MICRO>.NN with **GEO = domain segment, COORD = topic segment, <MICRO> = micro-skill segment** (READ_POINT/.../EQUATION_FROM_2PTS), matching the real example SPI.MIDDLE.ALG.LINEQ.ONESTEP_MUL.01. Section 1 now states this structure explicitly.
3. **RESOLVED.** Cross-domain target precision: crossDomainRelationships and prerequisites now use **explicit approved IDs (e.g. SPI.MIDDLE.ALG.LINEQ.TWOSTEP.01, SPI.MIDDLE.NUM.SIGNED_OPERATIONS.01), never a SPI.MIDDLE.ALG.LINEQ.* wildcard.** BOTHSIDES.01 is deliberately NOT a hard prerequisite. (§1, §2.)
4. **RESOLVED.** DAG/prerequisite check: the owner's prerequisite graph is encoded in §2; the **full-DAG check and the unresolved-reference check must both pass before any record is accepted.** The topological order P0, O1, O2, O3, O4, O5, O6, O7 introduces no cycle with existing LINEQ/GEO objectives.
5. **RESOLVED.** Answer-type per task is fixed (§1, §2, §3): `coordinate` for read_point/plot_point/CARTESIAN_PLANE; `ordered-pair` for midpoint; `integer`/`exact-rational` for gradient; `equation` for the equation tasks. `multiple-choice` is an interaction type, never an answer.type. The equivalence checker and validator emit/compare these consistently (§5, §8).
6. **RESOLVED.** MC eligibility is now resolved per task (§3, §9): `read_point`, `midpoint`, `interpret_mx_c`, `equation_from_graph`, `equation_from_two_points` are FR+MC where ≥3 distinct distractors exist; **`plot_point` is FR-only (MC unsupported)**; **`gradient_two_points` is MC-eligible only at m ≠ 0 (zero gradient is FR-only)**. An explicitly requested interaction type is never silently changed.
7. **RESOLVED.** Renderer determinism: Sections 6/7 specify the single deterministic projection of record, how U is chosen from params (largest equal-scale integer U fitting the per-item window), and exact-rational Liang–Barsky clipping, consistent with the vertical-line exclusion. Constants pinned in §7.6.
8. **RESOLVED.** Vertical-line exclusion scope: x=a is excluded **only from the four tasks that compute/represent a finite gradient** (O3 gradient_two_points, O5 interpret_mx_c, O6 equation_from_graph, O7 equation_from_two_points). **read_point, plot_point and midpoint MAY use points sharing an x-coordinate** (no gradient is computed there; only coincident points are rejected where two distinct points are required). The blanket phrasing has been corrected throughout (§3, §11).
9. Premium colour layer and validation authority: front matter states the monochrome canonical SVG remains authoritative and colour never carries meaning alone. Section 16 must confirm the byte-parity / svg-realises-data validator runs against the canonical monochrome SVG (not the colourised presentation variant), and that no-colour-only-information / WCAG AA contrast checks treat the colour layer as additive, matching the angles family's GREYS-only monochrome gate.

## Appendix C — Authoring & verification provenance

This proposal was authored by a multi-agent workflow: **16 sections drafted in parallel** against a fixed shared-identifier digest of the established platform conventions, then **five adversarial critics** (mathematics correctness, algorithm determinism, platform-fit, premium-graphics consistency, completeness) reviewed the combined draft, then **each section was revised against the consolidated findings**. The critics raised **36 findings (7 blocker-severity, 6 missing items)**; all blocker findings were applied in the revision pass (single projection of record; difficulty axes remapped onto the schema's closed `difficulty.axes` enum + a `difficulty-axes-schema-valid` gate; `contentHash` correctly covers `media[].spec.premium`; `mode-equivalence` compares displayed givens, not 'the answer'; `png-coordinate-preservation` is an exact analytic check, not a pixel/tolerance comparison).

**Owner revision pass (2026-06-23).** This document was subsequently revised in place to apply the owner's **APPROVE-WITH-REQUIRED-REVISIONS** directive: the status moved to approved-with-required-revisions (objective status `approved-for-implementation`, registry status `pending-review`); the curriculum strand, identifier structure, objective wordings, prerequisite DAG (explicit cross-domain IDs, no BOTHSIDES hard prereq), and mathematical-only `answerTypes` were fixed; the interaction matrix was synchronised (plot_point FR-only; zero-gradient gradient_two_points FR-only; explicit MC requests redraw rather than silently downgrade); no-answer-leakage figure rules were added (blank plot_point grid, neutral `l` label on equation_from_graph, hidden midpoint, scaffolded-only guides); sampling bounds were separated from the rendered viewport and renderer constants pinned; the difficulty model was confirmed at four axes with a required ≥10,000-seed distribution report; misconception-ID reuse was approved; and the premium colour layer was confirmed as a shared core library carried under `media[].spec.premium` with the 6000×4200 PNG envelope. The previously-open Appendix A questions are now a resolved-decisions record.
