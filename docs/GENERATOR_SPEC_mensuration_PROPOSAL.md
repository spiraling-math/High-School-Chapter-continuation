# Generator Specification Proposal — `gen.measurement.mensuration` v1.0.0 (Perimeter, Area & Composite Rectilinear Shapes)

> **STATUS: PROPOSAL ONLY — FOR OWNER `APPROVE` / `REJECT`. NO IMPLEMENTATION BEGINS UNTIL THE OWNER APPROVES.** This document specifies a new SPI-Math Middle School generator family but contains **no code, no oracle, no fixtures, and no curriculum-objective files** — it is the design the owner signs off (or rejects) before any build starts. Approval is requested, as one decision, over the whole package: the **curriculum placement + eight objectives**, the **task/interaction matrix**, the **dimensional-quantity answer contract**, the **structured unit model**, the **canonical polygon + dimension shape model**, the **backward construction**, the **SVG dimension-rendering contract**, the **solver + independent validator**, the **`MISC.MENS.*` misconception/distractor registry**, the **difficulty model + declared ranges**, the **edge-case/degeneracy rules**, the **accessibility model**, and the **review-pack + visual-audit plan**. On approval, implementation proceeds **oracle-first** (the independent Python `spi_oracle` is authored and frozen before the TypeScript mirror) and the family registers `approvalStatus: pending-review` — **gated out of normal Generator Studio and out of production exports/samples** (visible only in `?review` developer mode, labelled "machine-validated — pending curriculum approval") — until a separate, later owner `APPROVE`. The eight objectives would be authored at `reviewStatus: approved-for-implementation` (curriculum-cleared to build, generator still pending), advancing to `reviewStatus: approved` only at that later approval.
>
> **HEADLINE NEW ARCHITECTURE — the first UNIT-AWARE answer contract.** Every prior family answers a pure number (`integer` / `exact-rational` / `fraction` / `set`). Mensuration is the platform's first family whose answer is a **dimensional quantity**: a value that is wrong if the *number* is right but the *dimension* is wrong (e.g. `cm` where `cm²` is required, or a bare number with no unit). The proposal **designs a structured unit model** — `dimension` (`length` | `area`), `baseUnit` (`mm` | `cm` | `m`), `exponent` (1 for length, 2 for area), an exact integer-or-`Rational` `value`, and a canonical `display` form — and a checker that treats unit meaning **structurally, not as an unchecked text suffix**. **OWNER-GATED SCHEMA CHANGE (flagged for explicit decision in §4):** today `schemas/question-item.schema.json` has only a free-form `answer.units` **string** (the very "unchecked suffix" this contract forbids) and **no `quantity`/`measure` answer type**, and the `answer` object is `additionalProperties: false`. A structured contract therefore needs a `question-item.schema.json` extension — a new `answer.type` value (proposed `"quantity"`) plus a structured `answer.measure` object — which **cannot land without owner approval**; §4 states the exact field shapes and the Ajv-validation impact so the owner approves the schema delta deliberately, not as a side effect.
>
> **ALL PLATFORM GATES RETAINED — no exceptions.** Deterministic seeded generation (byte-identical Mulberry32 / Python PRNG; deterministic redraw, call-order parity); exact `Rational`/integer arithmetic with **no floats and no irrationals** (so areas/perimeters are exact integers or reduced rationals — see the deferral of Pythagoras/surds/circles below); independent **Python + TypeScript** with closure-agreement; canonical item **and** SVG **byte-for-byte** Py↔TS parity; runtime Ajv schema validation at boundaries (including the new answer shape); **≥ 3 distinct misconception-backed distractors** per MC-eligible task or deterministic redraw, each rule-recomputed by the independent validator; golden (seed) + parity (150 × 2) + **`SPI_SWEEP` 10,000-seed** stability sweep + reproducibility re-check + a distribution report proving **every declared band is reachable**; accessibility (axe-core **0 critical/serious**, WCAG AA) with a **data-table fallback for every figure**; offline HTML/JSON exporters (worksheet / answer-key / solutions, offline KaTeX) with bank-json round-trip; a **generation manifest + SHA-256 artifact-integrity tests** (Py + TS); **immutable approved-generator fixtures**; newly generated items begin machine-validated (`lifecycle.state = generated`).
>
> **REUSE, NOT REINVENTION.** This family **reuses the approved visual/style/export discipline through a versioned ADDITIVE extension** and does **not** alter any approved contract in place. It builds on the approved `core/visual-style/cartesian-theme.{json,ts}` (`gen.geometry.coordinate-lines` v1.0.2 — per-root `cx-figure` CSS-custom-property isolation; modes `premium` / `premium-dark` / `accessible` / `print`; `presentationSvg()` / `exportSvg()`; materialised **6000 × 4200** export) following exactly the additive pattern of `core/visual-style/data-chart-theme.{json,ts}` (`gen.stats.data-handling` v1.0.2) — adding **mensuration dimension-rendering primitives** (dimension lines, extension lines, arrowheads, right-angle markers, perpendicular-height markers, measurement labels) the same way, so `coordinate-lines` and `stats` output stay **byte-for-byte unchanged**. It reuses the **canonical-SVG discipline** (`viewBox 0 0 1000 700`, integer pixel coords via `gridRound` round-half-up over exact `Rational`/`Fraction`, **no runtime trig**, byte-identical Py↔TS, `role=img` + `<title>`/`<desc>` + data-table fallback + no-colour-only-information) and the **review-pack COVERAGE-MATRIX machinery** (required cells = every task × supported interaction × reachable band × realised answer shape, **derived from the distribution report**, with the pack builder failing on any missing reachable cell). It registers through the existing **SDK approval lifecycle** (`core/sdk/sequence-registry.ts`, `approvalStatus` `pending-review` → `approved`). No parallel renderer, style layer, export path, or coverage machinery is invented.

## Overview

`gen.measurement.mensuration` is proposed as **the next architecture-proving family** because it forces the platform to prove two capabilities it has never had to demonstrate together. First, it introduces the **first unit-aware / dimensional-quantity answer contract**: every existing family checks a pure number, but a perimeter and an area can share the same digits yet differ in dimension, so correctness now depends on a *structured* unit — length vs. area, the base unit, and the exponent — that the checker reasons about explicitly. This is the cleanest possible setting to prove that contract, because v1.0.0 deliberately bans **all** cross-unit conversion: each item uses **one declared base unit throughout** (mm, cm, or m), so the checker only ever distinguishes `length` from `area` and the correct base unit from the wrong exponent — never converting cm↔m (that is a later objective and a later contract extension). Second, it is the **first dimensioned-figure renderer**: rather than plotting data, the figure must carry *measurements* — dimension lines distinct from shape edges, extension lines, arrowheads, right-angle and perpendicular-height markers, and labels that may never touch an edge, a leader, or each other — while showing **only the given dimensions** and **never revealing the missing side or the final answer**. A single **canonical shape model** (a closed, non-self-intersecting, orthogonal polygon defined by exact integer/rational vertices and dimensions) must drive the student diagram, every dimension label, the prompt, the canonical answer, the worked solution, the misconception calculations, the accessibility text and data-table fallback, and the independent validation — one deterministic source of truth, eight task types.

The v1.0.0 scope is the small, fully-exact core of middle-school mensuration, exactly the eight owner-specified tasks: **perimeter of rectangles; perimeter of composite rectilinear (incl. L-) shapes; area of rectangles; area of triangles with an explicitly shown perpendicular base and height; area of composite rectilinear shapes by decomposition; a missing length from a given perimeter; a missing rectangle dimension from a given area; and a missing triangle base or height — only when the exact answer is guaranteed**. Because all values stay exact `Rational`/integer, areas and perimeters are exact integers or reduced rationals, and **every non-rectilinear, irrational, or approximate topic is deferred and deterministically excluded** — circles + π, volume + surface area, general-triangle perimeter (no validated exact construction), trapezia and other non-rectilinear composites, Pythagoras + surds, unit conversion, scale drawings, compound units, approximate measurements, and irregular/curved boundaries are **unreachable from the seeded task loop**, never silently included. Figures are **mathematically to-scale** wherever proportions would otherwise read poorly, using rational/integer coordinates with deterministic regeneration. Sections 1–16 develop each decision; this front matter fixes the identifiers, the reuse posture, the headline answer contract, and the dual approval gate (proposal now; pending-review build; later curriculum approval).

## Identifier glossary

| Item | Value (use verbatim) |
| --- | --- |
| Family / generator id | `gen.measurement.mensuration` |
| Generator version | `1.0.0` (proposed; not yet built) |
| Validator version | `1.0.0` (proposed; independent Py + TS) |
| Domain | `measurement` (new curriculum domain segment `MENS`) |
| Strand | `mensuration` (new strand) |
| Stage | `middle-school` (stage segment `MIDDLE` — never `MS`) |
| Objective ID pattern | `SPI.MIDDLE.MENS.<TOPIC>.<MICRO>.01` (matches `^SPI\.[A-Z0-9]+(\.[A-Z0-9_]+)+\.[0-9]{2}$`) |
| Misconception ID prefix | `MISC.MENS.*` (registry-backed, Py + byte-parity TS; ≥ 3 distinct per MC-eligible task or deterministic redraw) |
| Headline new contract | **dimensional-quantity answer** — structured unit model `{ dimension: length\|area, baseUnit: mm\|cm\|m, exponent: 1\|2, value: integer\|Rational, display }` |
| Proposed `answer.type` (OWNER-GATED) | `"quantity"` — **requires a `question-item.schema.json` extension** (new enum value + structured `answer.measure` object; the `answer` object is `additionalProperties:false`, so this is an explicit schema delta — see §4) |
| Existing field deliberately NOT relied on | the current free-form `answer.units` **string** (treated as an unchecked text suffix; the structured `measure` object replaces its role for this family) |
| Interaction types used (already in enum) | `free-response`; `multiple-choice` only where ≥ 3 genuine-mathematical misconception-backed distractors exist (MC options normally **all carry the correct unit**) |
| Reused substrate | `gen.geometry.coordinate-lines` v1.0.2 canonical-SVG discipline (`cx-*`, single `gridRound` projection, integer coords, no runtime trig, byte-identical Py↔TS) |
| Reused style / export | `core/visual-style/cartesian-theme.{json,ts}` (per-root `cx-figure` isolation; modes `premium`/`premium-dark`/`accessible`/`print`; `presentationSvg()`/`exportSvg()`; 6000 × 4200) **via a new ADDITIVE `data-dimension-theme` extension** modelled on `data-chart-theme.{json,ts}`; ADDS dimension lines, extension lines, arrowheads, right-angle + perpendicular-height markers, measurement labels |
| Reused checkers | `core/answer-checking` exact-rational checker shape, **extended** with the structured dimensional-quantity (unit-aware) checker (byte-parity Py/TS) |
| Reused coverage machinery | the stats v1.0.2 review-pack COVERAGE-MATRIX (required cells derived from the distribution report; pack builder fails on any missing reachable cell) — reused exactly |
| Registry status (on build) | `approvalStatus: pending-review` (gated from normal Studio + production) until a later owner `APPROVE` |
| Objective lifecycle (on build) | `reviewStatus: approved-for-implementation` → `approved` only at later curriculum approval |
| Initial item lifecycle | `lifecycle.state = generated` (machine-validated) |
| Provenance | `origin: generated`, `rightsStatus: academy-owned` |

**The eight v1.0.0 tasks (canonical `task` enum, used verbatim everywhere) ↔ objectives:**

| # | Generator task | objectiveId | Answer dimension |
| --- | --- | --- | --- |
| T1 | `perimeter_rectangle` | `SPI.MIDDLE.MENS.PERIM.RECTANGLE.01` | length (exponent 1) |
| T2 | `perimeter_composite_rectilinear` | `SPI.MIDDLE.MENS.PERIM.COMPOSITE.01` | length (exponent 1) |
| T3 | `area_rectangle` | `SPI.MIDDLE.MENS.AREA.RECTANGLE.01` | area (exponent 2) |
| T4 | `area_triangle_base_height` | `SPI.MIDDLE.MENS.AREA.TRIANGLE.01` | area (exponent 2) |
| T5 | `area_composite_decomposition` | `SPI.MIDDLE.MENS.AREA.COMPOSITE.01` | area (exponent 2) |
| T6 | `missing_length_from_perimeter` | `SPI.MIDDLE.MENS.MISSING.LENGTH_PERIM.01` | length (exponent 1) |
| T7 | `missing_dimension_from_area` | `SPI.MIDDLE.MENS.MISSING.DIM_AREA.01` | length (exponent 1) |
| T8 | `missing_triangle_base_or_height` | `SPI.MIDDLE.MENS.MISSING.TRI_BH.01` | length (exponent 1) |

**v1.0.0 scope (IN) vs DEFERRED (deterministically excluded — unreachable from the seeded task loop):**

| Status | Topic | Note |
| --- | --- | --- |
| IN v1.0.0 | perimeter of rectangles; perimeter of composite rectilinear / L-shapes | exact integer/rational lengths; perimeter from the **complete exterior boundary** |
| IN v1.0.0 | area of rectangles; area of triangles with an **explicitly shown** perpendicular base + height | exact integer/rational; triangle needs a visible perpendicular height marker |
| IN v1.0.0 | area of composite rectilinear shapes **by decomposition** | validated by shoelace **and** by the stated decomposition, with agreement asserted |
| IN v1.0.0 | missing length from a given perimeter; missing rectangle dimension from a given area; missing triangle base/height (**only when the exact answer is guaranteed**) | one mathematically-determined exact answer required by construction |
| DEFERRED | circles + π, arc/sector | needs irrationals + runtime trig the renderer forbids |
| DEFERRED | volume + surface area | out of a 2-D mensuration v1.0.0; later family |
| DEFERRED | general-triangle **perimeter** | unless an exact validated construction is specified — none is in v1.0.0 (sloping sides ⇒ surds) |
| DEFERRED | trapezia + other non-rectilinear composites | non-orthogonal edges fall outside the rectilinear shape model |
| DEFERRED | Pythagoras + surds; approximate measurements; compound units | excluded by the **exact-only** rule (no floats, no irrationals) |
| DEFERRED | unit conversion (cm↔m); scale drawings | each item uses **one declared base unit**; conversion is a later objective + contract extension |
| DEFERRED | irregular / curved boundaries | outside the closed orthogonal-polygon model |

> Each DEFERRED row is **unreachable from the seeded task loop**, not merely undrawn (see §3 task enum, §8 renderer, §12 edge cases): the task enum, the shape/parameter selector, and the redraw loop have no path that produces a deferred topic; a request for one is rejected, never silently downgraded.

## Table of contents

1. Curriculum placement and objective IDs
2. Final objective wording and prerequisites
3. Task and interaction matrix
4. Dimensional-quantity answer schema (structured unit model; **owner-gated `question-item.schema.json` extension**)
5. Unit parser, formatter, and equivalence checker (structural, not text-suffix; no cross-unit conversion in v1.0.0)
6. Canonical polygon and dimension data model (closed, non-self-intersecting, orthogonal; exact vertices + dimensions)
7. Backward construction of valid questions (one guaranteed exact answer; to-scale figures via rational/integer coords)
8. SVG dimension-rendering contract (additive `cx-figure` extension; given dimensions only; answer never revealed)
9. Solver and independent-validator design (closure, orientation, missing-side, perimeter exterior, area shoelace = decomposition; closure-agreement; byte-SVG; semantic answer-leakage)
10. Misconception and distractor registry (`MISC.MENS.*`; deterministic adapters; observableError + feedback)
11. Difficulty model (closed-enum axes; `bandFromScore`; every declared band reachable)
12. Edge cases and degeneracy rules (deterministic exclusion of deferred topics; exact-answer guarantees)
13. Accessibility model (spoken math, alt text, long description, data-table fallback, non-colour indicators)
14. Review-pack and visual-audit plan (coverage matrix; student-vs-answer-key overlays; label-collision + print stress; 6000 × 4200 export; answer-absent-from-student-diagram proofs)
15. Versioning and approval lifecycle (proposal → `pending-review` build → later curriculum approval)
16. Reusable infrastructure versus mensuration-specific code


---

## 1. Curriculum placement and objective IDs

### 1.1 Domain and strand

`gen.measurement.mensuration` introduces a new top-level **Measurement** domain to SPI-Math Middle School and a single new **mensuration** strand within it. Both `domain` and `strand` are free-form strings in `schemas/curriculum-objective.schema.json` (lines 25–26 are `type: string`, not enums), so no schema change is required to add them; they follow the lower-case-hyphenated convention already used by `number` / `signed-numbers`, `statistics` / `data-handling-and-probability`, and `geometry` / `coordinate-geometry-straight-line-graphs`.

| Field | Value (verbatim, every objective in this family) |
| --- | --- |
| `academy` | `SPI-Math` |
| `programme` | `SPI-Math Middle School` |
| `stage` | `middle-school` |
| `course` | `SPI-Math Middle School Mathematics` |
| `domain` | `measurement` |
| `strand` | `mensuration` |

This keeps Measurement deliberately distinct from the existing `geometry` domain (angles, coordinate geometry): mensuration is exact-arithmetic length/area work on rectilinear figures, not angle reasoning or the Cartesian-line strand. All circles/pi, volume/surface area, trapezia, Pythagoras/surds, unit conversion, scale drawings, compound and approximate units are **out of domain for v1.0.0** and are deterministically excluded by generator construction (see §3.3 and the owner brief's DEFER list, with named exclusion tests in §7/§12/§15); they are recorded here as future strands/objectives, never silently produced.

### 1.2 ID convention and the eight micro-objectives

IDs obey the platform pattern `SPI.<STAGE>.<DOMAIN>.<TOPIC>.<MICRO>.<NN>` and the schema regex `^SPI\.[A-Z0-9]+(\.[A-Z0-9_]+)+\.[0-9]{2}$`. The stage segment is `MIDDLE` and the domain segment is `MEAS`. There are exactly two topics — `PERIM` (perimeter) and `AREA` — and one micro-objective per owner task, giving **eight objectives, all suffixed `.01`** (the first revision; future revisions bump `.NN`). IDs are **stable** and never reused for a different task.

| # | Owner task | Objective ID |
| --- | --- | --- |
| T1 | Perimeter of rectangles | `SPI.MIDDLE.MEAS.PERIM.RECTANGLE.01` |
| T2 | Perimeter of composite rectilinear shapes (incl. L-shapes) | `SPI.MIDDLE.MEAS.PERIM.COMPOSITE_RECTILINEAR.01` |
| T3 | Area of rectangles | `SPI.MIDDLE.MEAS.AREA.RECTANGLE.01` |
| T4 | Area of triangles (explicitly shown perpendicular base & height) | `SPI.MIDDLE.MEAS.AREA.TRIANGLE_BASE_HEIGHT.01` |
| T5 | Area of composite rectilinear shapes by decomposition | `SPI.MIDDLE.MEAS.AREA.COMPOSITE_DECOMPOSITION.01` |
| T6 | Missing length from a given perimeter | `SPI.MIDDLE.MEAS.PERIM.MISSING_LENGTH.01` |
| T7 | Missing rectangle dimension from a given area | `SPI.MIDDLE.MEAS.AREA.MISSING_DIMENSION.01` |
| T8 | Missing triangle base or height (only when the exact answer is guaranteed) | `SPI.MIDDLE.MEAS.AREA.TRIANGLE_MISSING_BASE_HEIGHT.01` |

### 1.3 Single-source task slugs and `OBJECTIVE_BY_TASK` map

Mirroring `core/curriculum/stats-objective-ids.ts` exactly, the family ships **one** authoritative task-slug set and task→objective map, `core/curriculum/mensuration-objective-ids.ts`, re-used **verbatim** by the Python oracle (`oracle/spi_oracle/mensuration.py: OBJECTIVE_BY_TASK`), every spec section, descriptor, validator, fixture, review-pack record, the misconception `RULES_BY_TASK` (§10.3), the COVERAGE-MATRIX `cell:<task>:…` tokens (§14), the §15 scope list, and the SDK registry entry. **There is exactly one spelling of each of the eight task slugs; no section uses any alternative spelling.** A bespoke graph test (`core/curriculum/mensuration-graph.test.ts`, modelled on `core/curriculum/stats-graph.test.ts`) asserts: (a) all eight IDs exist in `curriculum/objectives/SPI.MIDDLE.MEAS.json`; (b) the TS map and the Python map agree; (c) `OBJECTIVE_BY_TASK`, `RULES_BY_TASK`, the generator dispatch, and the COVERAGE-MATRIX cell tokens share an **identical key set** equal to `MENSURATION_TASKS`; (d) no alternative slug spelling and no alternative `MISC.MENS.*` id spelling appears anywhere in the family (a string-scan assertion over both namespaces, catching id/slug drift before merge).

The intended shape (no implementation — field names and constants only):

- `MENSURATION_TASKS = [ "perimeter_rectangle", "perimeter_composite", "area_rectangle", "area_triangle", "area_composite", "missing_length_perimeter", "missing_dimension_area", "missing_triangle_base_height" ]` — **the single canonical slug set; these exact eight strings are the keys used everywhere** (any earlier draft spellings such as `rect_perimeter`, `composite_perimeter`, `perimeter_composite_rectilinear`, `missing_length_from_perimeter`, etc. are superseded and must not appear).
- `OBJECTIVE_BY_TASK: Record<MensurationTask, string>` keyed by those eight task slugs to the eight IDs above.
- `MENSURATION_OBJECTIVE_IDS = MENSURATION_TASKS.map(t => OBJECTIVE_BY_TASK[t])`.
- `FREE_RESPONSE_ONLY_TASKS: MensurationTask[] = MENSURATION_TASKS` — **all eight tasks are free-response only in v1.0.0** (rationale in §3.1: no task carries a constructive set of ≥ 3 distinct misconception-backed value distractors that all bear the correct unit, so no task offers multiple-choice).

The objective records live in a single file `curriculum/objectives/SPI.MIDDLE.MEAS.json` (one file per domain, matching `curriculum/objectives/SPI.MIDDLE.STAT.json`). Their `reviewStatus` follows a **two-stage gated lifecycle** consistent with the schema enum and the stats precedent:

1. **`proposed`** — before the curriculum authority signs off the objective definitions.
2. **`approved-for-implementation`** — once the definitions are curriculum-approved and the generator build is cleared to proceed *while the generator itself remains gated*; this is the status the objective files carry **throughout the gated build** (matching the schema's own description of `approved-for-implementation`: "curriculum-approved and cleared for generator build while the generator itself remains pending-review", line 102, and the stats family precedent — see §15).
3. **`approved`** — flipped only on owner APPROVE of the review pack.

In parallel, the SDK generator registers `approvalStatus: pending-review` (gated from normal Studio + production) until owner approval (see §15). `core/curriculum/graph-check.ts` enforces the DAG over the combined objective set (duplicate-id and cycle = errors; unresolved prereqs = warnings).

---

## 2. Final objective wording and prerequisites

Each objective below gives the verbatim learner-can-do `objectiveWording`, the `prerequisites[]` (citing **only objective IDs verified present and `approved` in `curriculum/objectives/`** — see the verification note), the MATHEMATICAL-only `answerTypes[]`, and a provisional `difficultyRange`. Per platform convention, **multiple-choice is an INTERACTION, never an answer type**, so it never appears in `answerTypes[]`; the MC/FR decision is recorded in §3.

`allowedRepresentations` is `["diagram", "numeric"]` for every objective (the canonical shape model drives a `diagram`; the dimensional-quantity answer is `numeric`), with `symbolic` added where a formula is stated (T4, T8). **`verbal-context` is deliberately omitted** in v1.0.0: the difficulty model holds `readingDemand` at zero on the basis that v1.0.0 items carry no worded context (see §11), so listing `verbal-context` here would be a representation the generator never exercises. It is reserved for a future revision when worded framings are introduced; until then the objective's allowed-representation set and the generator's emitted representations match exactly.

The dimensional-quantity answer is delivered through a **single new `answer.type` value, the token `"quantity"`**, plus a structured unit object. This is the **one** answer-type token the whole proposal adds; it is used verbatim in every objective's `answerTypes[]` here, in the §3.2 matrix, in the §4 schema diff, in the §9 validator checks, in the §10 adapter `Quantity` shape, and in the §14/§16 headline decision. That value does **not** yet exist in the `question-item.schema.json` `$defs/answerType` enum (verified: the enum, lines 196–204, runs `integer, decimal, fraction, exact-rational, mixed-number, exact-surd, exact-trig, … short-explanation, extended-response, proof, rubric-scored`; there is no `quantity`/`measure` token and no unit concept inside `answer` beyond the legacy free-string `answer.units`, line 237). **Adding `"quantity"` to that enum is an OWNER-GATED `question-item.schema.json` extension**, designed in §4 (cluster B). Until that extension is approved, these `answerTypes[]` reference `"quantity"` as the proposed shared vocabulary token; because the curriculum-objective schema validates `answerTypes` against `question-item.schema.json#/$defs/answerType` (line 54), the objective records **cannot be committed as `approved`** until the enum extension lands — so the objective files sit at `approved-for-implementation` (§1.3) while the enum diff is pending. This dependency is flagged here and again in §4/§15.

### Prerequisites cited — verification note (re-run against the actual `objectiveId` set)

Only IDs that exist as a defined `objectiveId` are cited as prerequisites:

- `SPI.MIDDLE.NUM.SIGNED_OPERATIONS.01` — **verified present and `approved`** in `curriculum/objectives/SPI.MIDDLE.NUM.json`. Covers calculation with positive/negative integers and simple rationals; this is the arithmetic backbone for every task, and (per its own `successCriteria`) it already covers the bracketed/ordered evaluation needed for `b × h ÷ 2` and for decomposition sums and differences. It is the same anchor the stats family uses.
- `SPI.MIDDLE.ALG.INVERSE_OPERATIONS.01` — **verified present and `approved`** in `curriculum/objectives/SPI.MIDDLE.ALG.FOUNDATIONS.json`. Inverse (undo) reasoning for the three "missing" tasks T6–T8.
- `SPI.MIDDLE.ALG.LINEQ.ONESTEP_MUL.01` — **verified present and `approved`** in `curriculum/objectives/SPI.MIDDLE.ALG.LINEQ.json`. Solve `A = b × h` / `A = ½ b h` for one unknown factor (T7, T8).

**Correction (was wrong in the prior draft):** `SPI.MIDDLE.NUM.ORDER_OF_OPERATIONS.01` is **NOT a defined objective** — it appears only inside `relatedObjectives[]` in `SPI.MIDDLE.NUM.json` (line 27) and `SPI.MIDDLE.ALG.FOUNDATIONS.json` (line 27), never as an `objectiveId`. `core/curriculum/graph-check.ts` treats an unresolved prerequisite as a **warning**, not an error, but the earlier "confirmed present/approved" claim was false. It is therefore **dropped as a prerequisite of T4 and T5**; the `b × h ÷ 2` evaluation and the decomposition sums/differences are covered by `SPI.MIDDLE.NUM.SIGNED_OPERATIONS.01` (whose `successCriteria` already include bracketed signed arithmetic), a verified-defined, approved objective. No mensuration objective cites `ORDER_OF_OPERATIONS.01`, so §2.9 and the §15 graph test resolve with **zero** unresolved-prerequisite warnings.

No coordinate-lines objective is cited as a prerequisite: none of the eight tasks requires the student to *read the Cartesian plane*. Composite shapes are presented as dimensioned figures, not as plotted lattice points, so reading coordinates is not a learner prerequisite. (The validator's internal shoelace check uses integer/rational vertices, but that is generator/validator machinery, not a learner skill — so `SPI.MIDDLE.GEO.COORD.READ_POINT.01`, which does exist and is approved, is deliberately **not** a prerequisite; it is listed in `relatedObjectives` only.)

### 2.1 T1 — `SPI.MIDDLE.MEAS.PERIM.RECTANGLE.01`
- **Wording:** "Calculate the perimeter of a rectangle from its given length and width, and state the result as an exact length with the correct unit."
- **prerequisites:** `["SPI.MIDDLE.NUM.SIGNED_OPERATIONS.01"]`
- **answerTypes:** `["quantity"]` (dimension = length)
- **allowedRepresentations:** `["diagram", "numeric"]`
- **difficultyRange:** `{ "min": 1, "max": 2 }`

### 2.2 T2 — `SPI.MIDDLE.MEAS.PERIM.COMPOSITE_RECTILINEAR.01`
- **Wording:** "Calculate the perimeter of a closed composite rectilinear shape, including L-shapes, by summing the lengths of its complete exterior boundary, and state the result as an exact length with the correct unit."
- **prerequisites:** `["SPI.MIDDLE.MEAS.PERIM.RECTANGLE.01", "SPI.MIDDLE.NUM.SIGNED_OPERATIONS.01"]`
- **answerTypes:** `["quantity"]` (dimension = length)
- **allowedRepresentations:** `["diagram", "numeric"]`
- **difficultyRange:** `{ "min": 2, "max": 4 }`

### 2.3 T3 — `SPI.MIDDLE.MEAS.AREA.RECTANGLE.01`
- **Wording:** "Calculate the area of a rectangle from its given length and width, and state the result as an exact area with the correct square unit."
- **prerequisites:** `["SPI.MIDDLE.NUM.SIGNED_OPERATIONS.01"]`
- **answerTypes:** `["quantity"]` (dimension = area)
- **allowedRepresentations:** `["diagram", "numeric"]`
- **difficultyRange:** `{ "min": 1, "max": 2 }`

### 2.4 T4 — `SPI.MIDDLE.MEAS.AREA.TRIANGLE_BASE_HEIGHT.01`
- **Wording:** "Calculate the area of a triangle from an explicitly shown base and its corresponding perpendicular height using area = (base × height) ÷ 2, and state the result as an exact area with the correct square unit."
- **prerequisites:** `["SPI.MIDDLE.MEAS.AREA.RECTANGLE.01", "SPI.MIDDLE.NUM.SIGNED_OPERATIONS.01"]`
- **answerTypes:** `["quantity"]` (dimension = area; value may be an exact reduced rational when `b × h` is odd, giving `…/2`)
- **allowedRepresentations:** `["diagram", "numeric", "symbolic"]` (the halving formula is stated).
- **difficultyRange:** `{ "min": 2, "max": 3 }`

### 2.5 T5 — `SPI.MIDDLE.MEAS.AREA.COMPOSITE_DECOMPOSITION.01`
- **Wording:** "Calculate the area of a closed composite rectilinear shape by decomposing it into non-overlapping rectangles, summing (or subtracting) their areas, and state the result as an exact area with the correct square unit."
- **prerequisites:** `["SPI.MIDDLE.MEAS.AREA.RECTANGLE.01", "SPI.MIDDLE.NUM.SIGNED_OPERATIONS.01"]`
- **answerTypes:** `["quantity"]` (dimension = area)
- **allowedRepresentations:** `["diagram", "numeric"]`
- **difficultyRange:** `{ "min": 2, "max": 4 }`

### 2.6 T6 — `SPI.MIDDLE.MEAS.PERIM.MISSING_LENGTH.01`
- **Wording:** "Find an unknown side length of a rectangle or composite rectilinear shape given its perimeter and its other sides, by inverse reasoning, and state the missing length as an exact length with the correct unit."
- **prerequisites:** `["SPI.MIDDLE.MEAS.PERIM.RECTANGLE.01", "SPI.MIDDLE.ALG.INVERSE_OPERATIONS.01", "SPI.MIDDLE.NUM.SIGNED_OPERATIONS.01"]`
- **answerTypes:** `["quantity"]` (dimension = length)
- **allowedRepresentations:** `["diagram", "numeric"]`
- **difficultyRange:** `{ "min": 2, "max": 4 }`

### 2.7 T7 — `SPI.MIDDLE.MEAS.AREA.MISSING_DIMENSION.01`
- **Wording:** "Find an unknown length or width of a rectangle given its area and the other dimension, by dividing, and state the missing dimension as an exact length with the correct unit (constructed so the answer is exact)."
- **prerequisites:** `["SPI.MIDDLE.MEAS.AREA.RECTANGLE.01", "SPI.MIDDLE.ALG.INVERSE_OPERATIONS.01", "SPI.MIDDLE.ALG.LINEQ.ONESTEP_MUL.01"]`
- **answerTypes:** `["quantity"]` (dimension = length; value may be an exact reduced rational `A / b`)
- **allowedRepresentations:** `["diagram", "numeric", "symbolic"]`
- **difficultyRange:** `{ "min": 2, "max": 4 }`

### 2.8 T8 — `SPI.MIDDLE.MEAS.AREA.TRIANGLE_MISSING_BASE_HEIGHT.01`
- **Wording:** "Find an unknown base or perpendicular height of a triangle given its area and the other measurement, using area = (base × height) ÷ 2 rearranged, and state the missing measurement as an exact length with the correct unit (generated only when the exact answer is guaranteed)."
- **prerequisites:** `["SPI.MIDDLE.MEAS.AREA.TRIANGLE_BASE_HEIGHT.01", "SPI.MIDDLE.ALG.INVERSE_OPERATIONS.01", "SPI.MIDDLE.ALG.LINEQ.ONESTEP_MUL.01"]`
- **answerTypes:** `["quantity"]` (dimension = length; value may be an exact reduced rational `2A / b`, generated only when that value is exact)
- **allowedRepresentations:** `["diagram", "numeric", "symbolic"]`
- **difficultyRange:** `{ "min": 3, "max": 4 }`

### 2.9 Prerequisite DAG (intra-family + external edges)

All edges point from prerequisite to dependent; the graph is acyclic and is enforced by `core/curriculum/graph-check.ts`. External (existing, verified-`approved`) roots are shown at the top. Every cited external root resolves (no unresolved-prerequisite warnings).

```
SPI.MIDDLE.NUM.SIGNED_OPERATIONS.01 ──┬──────────────────────────────┐
SPI.MIDDLE.ALG.INVERSE_OPERATIONS.01  │                              │
SPI.MIDDLE.ALG.LINEQ.ONESTEP_MUL.01   │                              │
                                      ▼                              ▼
                        T1 PERIM.RECTANGLE            T3 AREA.RECTANGLE
                           │          │                 │      │      │
              ┌────────────┘          └──────┐          │      │      └────────────┐
              ▼                              ▼          ▼      ▼                   ▼
   T2 PERIM.COMPOSITE_          T6 PERIM.MISSING_   T4 AREA.    T5 AREA.COMPOSITE_  T7 AREA.MISSING_
      RECTILINEAR                  LENGTH           TRIANGLE_     DECOMPOSITION       DIMENSION
                                                   BASE_HEIGHT
                                                      │
                                                      ▼
                                       T8 AREA.TRIANGLE_MISSING_BASE_HEIGHT
```

Edges in words: T2←T1; T6←T1; T4←T3; T5←T3; T7←T3; T8←T4. Each node also depends on the relevant NUM/ALG roots as listed per objective. `SPI.MIDDLE.NUM.SIGNED_OPERATIONS.01` is a root of every node (directly or via T1/T3/T4). The graph test asserts these exact edges and that no cycle or duplicate ID is introduced when the file is merged with the existing objective set.

---

## 3. Task and interaction matrix

### 3.1 Interaction and answer-shape decisions

**v1.0.0 ships exactly one interaction type: `free-response`.** Every one of the eight tasks is **free-response only** (this is `FREE_RESPONSE_ONLY_TASKS = MENSURATION_TASKS` in §1.3). The `interactionType` carries a single dimensional-quantity entry and `answer.type = "quantity"` (the §4 structured-unit answer, OWNER-GATED enum addition). **No task offers `multiple-choice` in v1.0.0.**

**Why no MC (correction to the prior draft).** The platform rule for MC is ≥ 3 *distinct* misconception-backed **value** distractors, each (a) carrying the **correct** unit, (b) never equal to the correct answer, and (c) recomputed independently by the validator through the misconception adapter (else a deterministic redraw fires). On audit, the only plausibly MC-eligible tasks were T1 (rectangle perimeter) and T3 (rectangle area), and neither yields a *constructive guarantee* of three distinct correct-unit value distractors across the §6 parameter ranges:

- The §10 registry supplies only **two** rectangle value misconceptions per task (T1: `MISC.MENS.ADDS_TWO_SIDES_RECT` → `w + h`, and `MISC.MENS.AREA_WHEN_PERIMETER` → `w · h`; T3: `MISC.MENS.ADDS_INSTEAD_OF_MULT_AREA` → `w + h`, and `MISC.MENS.PERIMETER_WHEN_AREA` → `2(w + h)`). There is **no defined, registered third value rule** with a `MISC.MENS.*` id and adapter — the earlier "a third reachable value misconception" was a placeholder, not a constructive rule.
- The second rule **collides with the correct answer** on a non-trivial set of seeds: a 4×4 square has `P = 16 = w · h` (T1's `AREA_WHEN_PERIMETER` nulls), and `A = 16 = 2(w + h)` (T3's `PERIMETER_WHEN_AREA` nulls); 3×6 and 6×3 give `P = 18 = w · h` likewise. On those seeds only **one** value distractor survives, so the mandatory three can never be guaranteed.

Rather than weaken the guarantee or invent an unbacked third rule, **MC is dropped for v1.0.0 across the whole family.** This is the cleanest outcome: the dimensional-quantity answer contract (accept mathematically-equivalent numerical forms with the correct unit; distinguish length from area; reject a correct number with the wrong dimension; reject `cm` where `cm²` is required and vice versa; emit targeted feedback for missing/incorrect units) **is the headline feature**, and making every task free-response guarantees that checker is exercised on **all eight** tasks. The unit-dimension misconceptions are surfaced as free-response feedback exactly as the owner brief routes them. (Should a constructive third value rule be added in a later revision, T1/T3 MC can be re-introduced as a contract extension; v1.0.0 does not depend on it.)

The unit-dimension misconceptions named in the brief — `MISC.MENS.LINEAR_UNITS_FOR_AREA`, `MISC.MENS.SQUARE_UNITS_FOR_PERIMETER`, `MISC.MENS.RIGHT_NUMBER_NO_UNIT` — are **free-response feedback only** (the checker emits a targeted hint when a response matches one of these), never MC distractor options. The mathematical value misconceptions referenced anywhere in this section use their **canonical §10 registry ids verbatim** — `MISC.MENS.ADDS_TWO_SIDES_RECT`, `MISC.MENS.AREA_WHEN_PERIMETER`, `MISC.MENS.PERIMETER_WHEN_AREA`, `MISC.MENS.ADDS_INSTEAD_OF_MULT_AREA`, `MISC.MENS.OMITS_INDENTED_EDGE`, `MISC.MENS.DOUBLE_COUNTS_INTERNAL_EDGE`, `MISC.MENS.SUBTRACTS_WRONG_RECT`, `MISC.MENS.FORGETS_TO_HALVE_TRIANGLE` — with **no alternative spellings** (the §1.3(d) string-scan test enforces this over the `MISC.MENS.*` namespace). The "uses a sloping side instead of the perpendicular height" pitfall is **not** a numeric value distractor: a sloping side of an axis-aligned-base / perpendicular-height triangle is `√(base² + height²)`, irrational for almost all integer/rational pairs, which violates the no-surds/no-Pythagoras exact-math rule and cannot be a reduced `Rational`. It is therefore carried **only as a free-response pedagogical hint** (`MISC.MENS.USES_SLOPING_SIDE`, adapter returns `null` for distractor purposes) — see §10. (Full registry, adapters, observableError/feedback in §10, cluster C.)

### 3.2 1:1 task → objective → interaction(s) → answer.shape matrix

`dimension` and `exponent` refer to the §4 structured unit model (length ⇒ `exponent 1`; area ⇒ `exponent 2`); `unit ∈ {mm, cm, m}` is the single declared base unit of the item (no cross-unit conversion in v1.0.0). The "Value form" column lists the exact-arithmetic value type (integer or reduced `Rational{num,den}`); all areas/perimeters are exact integers or reduced rationals, no irrationals.

**Where rational values arise (resolves the §6 integer-coordinate inconsistency).** Rectangle and composite shapes are constructed from **integer** edge lengths and integer vertex coordinates (§6 keeps shape coordinates integer-valued so the canonical-SVG `gridRound` discipline and shoelace check stay on integers). Consequently **rectangle and composite tasks (T1, T2, T3, T5, T6) produce integer answers only**; there is no rational-sided rectangle, and any prior "rational rectangle" worked example is removed. **Rational answers arise only where the construction genuinely produces them**: triangle area T4 (odd `b · h` ⇒ `…/2`), missing rectangle dimension T7 (`A / b` need not be integral), and missing triangle base/height T8 (`2A / b`). The required mm/cm/m × integer/rational × length/area review-pack coverage (§14) is therefore satisfied with **integer** cells on T1/T2/T3/T5/T6 and **integer + rational** cells on T4/T7/T8 — every declared cell is reachable, so the §14 band-and-shape reachability gate has no empty `…:rational:*` cell to flag.

| # | Objective ID | Interaction(s) | `answer.type` / shape | dimension · exponent · `unit` | Value form |
| --- | --- | --- | --- | --- | --- |
| T1 | `SPI.MIDDLE.MEAS.PERIM.RECTANGLE.01` | free-response | `quantity` | length · 1 · {mm,cm,m} | integer |
| T2 | `SPI.MIDDLE.MEAS.PERIM.COMPOSITE_RECTILINEAR.01` | free-response | `quantity` | length · 1 · {mm,cm,m} | integer |
| T3 | `SPI.MIDDLE.MEAS.AREA.RECTANGLE.01` | free-response | `quantity` | area · 2 · {mm,cm,m} | integer |
| T4 | `SPI.MIDDLE.MEAS.AREA.TRIANGLE_BASE_HEIGHT.01` | free-response | `quantity` | area · 2 · {mm,cm,m} | integer or reduced rational (odd `b·h` ⇒ `…/2`) |
| T5 | `SPI.MIDDLE.MEAS.AREA.COMPOSITE_DECOMPOSITION.01` | free-response | `quantity` | area · 2 · {mm,cm,m} | integer |
| T6 | `SPI.MIDDLE.MEAS.PERIM.MISSING_LENGTH.01` | free-response | `quantity` | length · 1 · {mm,cm,m} | integer |
| T7 | `SPI.MIDDLE.MEAS.AREA.MISSING_DIMENSION.01` | free-response | `quantity` | length · 1 · {mm,cm,m} | integer or reduced rational (`A/b`) |
| T8 | `SPI.MIDDLE.MEAS.AREA.TRIANGLE_MISSING_BASE_HEIGHT.01` | free-response | `quantity` | length · 1 · {mm,cm,m} | integer or reduced rational (`2A/b`), exact only |

**Interaction summary:** every task is **free-response**; **no task offers multiple-choice** in v1.0.0. This single source of truth is consumed by the review-pack **COVERAGE-MATRIX** machinery (re-used by name from stats v1.0.2): required cells = every task × supported interaction × reachable difficulty band × realised answer shape, derived from the distribution report; the pack builder fails on any missing reachable cell. Because every task's answer shape is `quantity`, the matrix's "realised answer shape" axis additionally records `(dimension, exponent, unit, value-kind ∈ {integer, rational})` so that mm/cm/m × length/area × integer/rational coverage (required by the owner review-pack plan) is provably exercised and blocked on if missing — with `rational` cells required for T4/T7/T8 and `integer` cells required for all eight.

### 3.3 Scope guard (exactly the eight tasks)

The task enum `MENSURATION_TASKS` (§1.3) has exactly eight members; the generator dispatch is a **total function** over that enum with no default branch, and the conformance/graph tests assert the objective set, the task set, the `RULES_BY_TASK` key set, and the coverage matrix all have **cardinality eight** and an **identical key set** (§1.3(c)). Every deferred topic — circles/pi, volume/surface area, general triangle perimeter (no exact construction in v1.0.0), trapezia/non-rectilinear composites, Pythagoras/surds, unit conversion, scale drawings, compound units, approximate measurements, irregular curved boundaries — is **deterministically excluded by construction**: there is no task slug, objective ID, or generator branch that can emit one, and each exclusion is asserted by a named test (§7/§12/§15), not merely filtered at runtime.


---

## 4. Dimensional-quantity answer schema

### 4.1 The core problem and the design decision

Every answer in the eight mensuration tasks is a *dimensional quantity*: a number that is meaningless without a dimension (length vs. area) and a base unit (mm, cm, m). The platform's current `answer` contract (`schemas/question-item.schema.json` `$defs/answer`) cannot represent this safely:

- `answer.type` is drawn from the closed `$defs/answerType` enum (`integer`, `exact-rational`, `mixed-number`, ... ending `short-explanation`, `extended-response`, `proof`, `rubric-scored`). There is **no** unit-bearing type today (verified against lines 196-204).
- `answer.units` exists (`{ "type": "string" }`, e.g. `"cm"`, `"m s^-1"`, line 237) but it is **an unchecked text suffix**: a display string, not a structurally checked object. A checker that compared it would be string-matching `"cm"` vs `"cm^2"` vs `"cm²"` vs `"square cm"` — exactly the fragile behaviour the owner brief forbids.
- `answer.accepts` is `additionalProperties:false` with only `{fraction, decimal, mixed}` booleans (lines 215-224), and the conformance checker (`oracle/check_conformance.py`) enforces `additionalProperties:false` strictly, so a unit object cannot be smuggled into the existing `accepts` shape without a declared property.

**Decision (recommended, single source of truth): add ONE new answer type, `quantity`, carrying a structured `unit` object, as a minimal, additive, back-compatible extension to `question-item.schema.json`.** The token is **`quantity`** verbatim everywhere — the `$defs/answerType.enum` member, every objective's `answerTypes[]` (§2), the §3.2 task matrix `answer.type`, the checker-registry routing key, the §9 validator `answer-type-consistency` check, the §14 COVERAGE-MATRIX realised-answer-shape axis, and the §16.3 headline decision. (Earlier drafts of this section used `measure`; that spelling is superseded — `quantity` is canonical, matching §2/§9/§16.3 and the owner brief.)

We choose a new `type` over a bare additive `unit` field on `integer`/`exact-rational` because:

1. The answer-type *is* the routing key for the checker registry, the `answerTypes[]` objective field, and the COVERAGE-MATRIX "realised answer shape" axis. A dimensional quantity is a genuinely different *shape* of answer (number + dimension + unit), and giving it a name (`quantity`) lets the COVERAGE-MATRIX require "length answer" and "area answer" cells as first-class realised shapes, exactly as the brief's review-pack plan demands.
2. It keeps the numeric core unchanged: `canonical` reuses the established `{num, den}` rational encoding (`core/exact-math/rational.ts`, `fractions.Fraction`), so all exact-math, parity, and serialization machinery applies unmodified.
3. It avoids overloading `integer`/`exact-rational`, whose checkers are unit-blind and are relied on by five shipped families; those code paths stay byte-for-byte unchanged.

> **OWNER-GATED SCHEMA CHANGE.** This proposal requires a `question-item.schema.json` extension. It is minimal, additive, and back-compatible (no existing item changes meaning; no field is removed or retyped). It MUST be owner-approved before any implementation, and it ships through the same SDK `pending-review -> approved` lifecycle (`core/sdk/sequence-registry.ts`) as the family itself. The exact diff is given in §4.4. **The owner is being asked to gate exactly ONE precise diff:** enum token `quantity`, a structured sibling `answer.unit` object, and an `accepts.requireUnit` boolean — the structure is fixed in §4.3 and is the only one realised by the §4.4 schema and the §9 validator.

### 4.2 The structured unit model

The unit model is a closed, self-contained object. It is the single source of dimensional truth and is referenced by the prompt, the canonical answer, every misconception adapter, the worked solution, the accessibility text, and the independent validator.

```
UnitModel = {
  dimension:  "length" | "area",        // closed enum
  baseUnit:   "mm" | "cm" | "m",        // closed enum (one declared unit per item)
  exponent:   1 | 2,                     // 1 iff dimension="length", 2 iff dimension="area"
  display:    string                     // canonical unit token only, e.g. "cm", "cm^2"
}
```

Invariants (enforced by **bundled Ajv** via the §4.4 `if/then` conditionals **and** by the independent validator's `unit-model-wellformed` check (§9); see §4.4 for why these are NOT enforced by the offline `check_conformance.py` subset):

| Invariant | Rule |
|---|---|
| dimension/exponent lock | `exponent === 1 ⟺ dimension === "length"`; `exponent === 2 ⟺ dimension === "area"`. No other pairing is representable. |
| single base unit (v1.0.0) | `baseUnit` is one of `mm/cm/m`; the SAME `baseUnit` is used by every given dimension in the figure, the canonical answer, and all distractors. **No cross-unit conversion** occurs anywhere in v1.0.0 (see §4.5). |
| display canonicality | `display` is the formatter output (§5.2): `baseUnit` for `exponent=1`, `baseUnit + "^2"` for `exponent=2`. It is presentation only; the checker never reads it. The stored `display` uses the ASCII `^2` token, never the Unicode `²` (asserted by the §5.2 `display-is-ascii-caret` check, for byte-stable golden/parity fixtures across encodings/locales). |

The numeric value is an exact reduced `Rational` `{num, den}`:

```
Rational = { num: integer, den: integer >= 1 }   // reduced; den = 1 for integer answers
```

A full dimensional answer is the pair `(value, unit)` used internally by the parser/formatter/checker:

```
QuantityAnswer = {
  value: Rational    // exact reduced {num, den}; den=1 for integer answers
  unit:  UnitModel
}
```

`value` is the same `Rational`/`Fraction` contract as `exact-rational`; area answers on rectilinear integer/rational figures are exact integers or reduced rationals, never irrationals (consistent with the no-surds constraint).

### 4.3 How it rides on the item `answer` (authoritative encoding)

The item `answer` object uses the new type and stores the structured unit as a **separate sibling** of the numeric `canonical`. **`canonical` stays a bare `{num, den}` Rational, unchanged from `exact-rational`; the unit is NOT folded into `canonical`.** (This resolves the §16.3 contradiction: §16.3's `canonical = {dimension, baseUnit, exponent, value:{num,den}}` is superseded — the encoding below is authoritative, because it preserves the exact-rational canonical contract and keeps every existing rational/parity/serialization path byte-identical, which is the design rationale in §4.1.)

```
answer = {
  type:      "quantity",                     // NEW enum member (canonical token)
  canonical: { num, den },                   // exact numeric value (Rational), unchanged encoding — NO unit inside
  unit:      UnitModel,                       // NEW structured sibling (dimension, baseUnit, exponent, display)
  display:   string,                          // canonical full display, e.g. "15 cm", "24 cm^2"
  accepts:   { fraction, decimal, mixed,     // existing numeric-equivalence booleans, reused as-is
               requireUnit }                  // NEW boolean (see below)
}
```

- `canonical` stays a `{num, den}` rational — **not** wrapped with the unit — so every existing rational/parity/serialization path treats it identically to an `exact-rational` value. The dimension lives only in `unit`. The §9 `closure-agreement` check therefore compares **two things separately**: the recomputed `value` (Rational, by cross-multiplication) against `answer.canonical`, and the recomputed `(dimension, exponent, baseUnit)` triple against `answer.unit` — not a single merged object.
- `display` is the formatter's full rendering (§5.2): `"<value-display> <unit-display>"`, e.g. `"15 cm"`, `"3/2 m"`, `"24 cm^2"`.
- `accepts.fraction/decimal/mixed` keep their existing meaning for the numeric part (e.g. accept `30/2` for `15`, accept the terminating decimal when permitted). `accepts.requireUnit` (default `true`) states that a unit MUST be supplied for full credit; when `true`, a numerically-correct, unit-less response is graded incorrect with the targeted "missing unit" feedback (§5.3). When `false`, policy permits a unit-less numeric to pass (the parser yields `unit=null` and gate 1 is satisfied — see §5).

**`unit` vs `units` footgun (flagged).** The schema already carries a legacy free-text `answer.units` *string* (line 237). The new structured object is `answer.unit` (singular). The two keys differ only by a trailing `s`, an error-prone trap for authors and reviewers. Mensuration items populate **only** `answer.unit` and never `answer.units`; the validator's `no-legacy-units-string` check (§9) asserts every mensuration item omits `answer.units`, and authors must never populate both. (We keep the structured object at top level as `answer.unit` rather than nesting it under `canonical`, to preserve the bare-Rational `canonical` contract above.)

### 4.4 Exact owner-gated schema diff (minimal, additive, back-compatible)

Three additive edits to `schemas/question-item.schema.json`; nothing is removed or retyped.

1. **Add one enum member** to `$defs/answerType.enum`. The real enum (lines 196-204) begins `"integer", "decimal", "fraction", "exact-rational", "mixed-number", ...` and ends `..., "proof", "rubric-scored"`. **Append `"quantity"` at the very end of the enum, after `"rubric-scored"`** (a fixed byte position; appending at the tail minimises churn to the committed golden schema and is unambiguous for the parity diff):
   ```
   ..., "short-explanation", "extended-response", "proof", "rubric-scored", "quantity"
   ```

2. **Add two optional properties** — a `unit` object on `$defs/answer.properties`, and a `requireUnit` boolean inside the existing `accepts` sub-object:
   ```jsonc
   "unit": {
     "type": "object",
     "additionalProperties": false,
     "required": ["dimension", "baseUnit", "exponent", "display"],
     "properties": {
       "dimension": { "type": "string", "enum": ["length", "area"] },
       "baseUnit":  { "type": "string", "enum": ["mm", "cm", "m"] },
       "exponent":  { "type": "integer", "enum": [1, 2] },
       "display":   { "type": "string" }
     }
   }
   ```
   and add `"requireUnit": { "type": "boolean", "default": true }` to `$defs/answer.properties.accepts.properties` (that sub-object is `additionalProperties:false` at line 218, so the new key MUST be declared there — otherwise a `quantity` answer carrying `requireUnit` would be rejected as an unexpected property).

3. **Add an `if/then` conditional** to the existing `$defs/answer.allOf` array (lines 241-252) binding the new type to its obligations, mirroring the existing `integer`/`exact-rational` conditionals already in that array:
   ```jsonc
   {
     "$comment": "A 'quantity' answer carries a bare-Rational canonical {num,den>=1} plus a structured unit; dimension and exponent are locked.",
     "if":  { "properties": { "type": { "const": "quantity" } }, "required": ["type"] },
     "then": {
       "required": ["unit"],
       "properties": {
         "canonical": { "type": "object", "required": ["num", "den"],
           "properties": { "num": { "type": "integer" }, "den": { "type": "integer", "minimum": 1 } } },
         "unit": {
           "allOf": [
             { "if": { "properties": { "dimension": { "const": "length" } } },
               "then": { "properties": { "exponent": { "const": 1 } } } },
             { "if": { "properties": { "dimension": { "const": "area" } } },
               "then": { "properties": { "exponent": { "const": 2 } } } }
           ]
         }
       }
     }
   }
   ```

**Where each obligation is actually enforced (corrected — do NOT overstate offline coverage).** `oracle/check_conformance.py` is a deliberately minimal offline subset: its docstring (lines 3-5) and `check()` body (lines 60-100) implement only `$ref, type, enum, pattern, properties, additionalProperties(bool), items, minItems, required`. **It does NOT implement `allOf`, `if`, `then`, or `const`** — so the pre-existing `integer`/`exact-rational` `allOf` conditionals (lines 241-252) are already silently ignored offline today, and the new edit #3 conditional (the `required:[unit]` binding and the dimension⇔exponent lock) is likewise a **no-op under `check_conformance.py`**. Concretely, offline conformance would *not reject* a malformed `quantity` answer that omits `unit` or pairs `dimension:"area"` with `exponent:1`. Therefore:

- **Offline `check_conformance.py` enforces, for the new type:** enum membership of `"quantity"`, `required:["type","canonical"]`, `additionalProperties:false` on `answer` and on `unit`/`accepts`, the `enum`s inside `unit`, and the `{num,den}` types where `properties` reach them — i.e. structural shape, **but not the conditional dimension/exponent lock or the type→`unit` requirement**.
- **The conditional invariants (dimension⇔exponent lock; `quantity ⇒ unit` required) are enforced by (a) the bundled production Ajv gate (which fully supports `allOf/if/then/const`) AND (b) the independent validator's named checks** `unit-model-wellformed`, `unit-contract`, and `answer-type-consistency` (§9), plus a dedicated `quantity-dimension-exponent-lock` check added to §9 so the invariant is provably enforced in the offline pipeline rather than relying on conformance.py.
- **Owner decision flagged:** either accept this known limitation (it already applies to `integer`/`exact-rational` and is covered by Ajv + the validator), OR — as a separately scoped, owner-gated extension of shared tooling — extend `check_conformance.py` with minimal `allOf`+`if/then`+`const` support so the conditional is machine-checked offline too. This proposal recommends the former (accept + validator-enforced) to avoid touching shared tooling for one family; the latter is listed as an optional deliverable. **The claim "the offline subset validates the extension" means "accepts (does not reject) a well-formed `quantity` item", NOT "enforces the conditional".**

Back-compatibility: every existing item still validates (no existing item uses `type:"quantity"`; `unit`/`requireUnit` are optional and absent elsewhere). The legacy `answer.units` *string* remains in the schema for non-mensuration families; mensuration items do **not** use it (§4.3, `no-legacy-units-string`). Live `quantity` items are added to the conformance harness's live-generation block (§5.5) alongside the existing families so the schema/instance shape agreement is exercised on real generator output.

### 4.5 No cross-unit conversion in v1.0.0

A v1.0.0 item declares ONE `baseUnit` and uses it throughout: every given dimension on the figure, the canonical answer, and all distractors share that `baseUnit`. The checker performs **no** mm↔cm↔m conversion. `cm ↔ m` conversion, mixed-unit figures, and compound units are a **later objective plus a contract extension** (a future `unit.scale`/conversion table), explicitly deferred and deterministically excluded here: the generator never emits an item whose figure or answer mixes base units, and the validator's `single-base-unit` check fails any item where the answer `baseUnit` differs from any figure-dimension `baseUnit`.

### 4.6 Worked encodings

The rational-side worked example below depends on §6 allowing reduced-rational rectangle edge lengths (so a rational rectangle area is reachable and the `area_rectangle … rational` coverage cell is non-empty). **If §6/§7 instead restrict rectangle/composite edges to integers, delete the rational-rectangle example here and source all rational coverage from the triangle and missing-dimension tasks** (where `15/2` etc. arise from `b·h÷2` and from inverse division). The length and area examples below are valid either way.

**Length answer** — perimeter of a rectangle, given 5 cm × 10 cm, answer 30 cm:

```jsonc
"answer": {
  "type": "quantity",
  "canonical": { "num": 30, "den": 1 },
  "unit": { "dimension": "length", "baseUnit": "cm", "exponent": 1, "display": "cm" },
  "display": "30 cm",
  "accepts": { "fraction": true, "decimal": true, "mixed": false, "requireUnit": true }
}
```
Accepted full-credit inputs: `30 cm`, `60/2 cm`, `30.0 cm` (decimal permitted because den=1 terminates). Rejected: `30` (missing unit → `missing-unit` feedback), `30 cm^2` (square-for-perimeter → `square-for-perimeter` feedback), `30 m` (wrong base unit), `15 cm` (wrong number → `wrong-value`).

**Area answer** — area of a triangle, base 6 cm, perpendicular height 5 cm, answer 15 cm² (½·6·5):

```jsonc
"answer": {
  "type": "quantity",
  "canonical": { "num": 15, "den": 1 },
  "unit": { "dimension": "area", "baseUnit": "cm", "exponent": 2, "display": "cm^2" },
  "display": "15 cm^2",
  "accepts": { "fraction": true, "decimal": true, "mixed": false, "requireUnit": true }
}
```
Accepted: `15 cm^2`, `15 cm²`, `30/2 cm^2`, `15.0 cm^2`. Rejected: `15 cm` (linear-for-area → `linear-for-area` feedback), `15` (missing unit), `30 cm^2` (forgot to halve — a value misconception, `FORGETS_TO_HALVE_TRIANGLE`), `15 m^2` (wrong base unit).

**Rational area** — rectangle 3/2 m × 5 m, answer 15/2 m² (valid only if §6 permits rational rectangle edges; otherwise use a triangle, e.g. base 3 m × height 5 m ÷ 2 = 15/2 m²):

```jsonc
"answer": {
  "type": "quantity",
  "canonical": { "num": 15, "den": 2 },
  "unit": { "dimension": "area", "baseUnit": "m", "exponent": 2, "display": "m^2" },
  "display": "15/2 m^2",
  "accepts": { "fraction": true, "decimal": true, "mixed": false, "requireUnit": true }
}
```
Accepted: `15/2 m^2`, `30/4 m^2`, `7.5 m^2` (terminating). Rejected: `7.5 m` (linear-for-area), `7.5` (missing unit).

For **MC items** (only T1 rectangle-perimeter and T3 rectangle-area are MC-eligible per §3; all other tasks are free-response only), every option carries the *correct* unit and `display` (e.g. all four show `cm^2`); the three required distractors are genuine MATHEMATICAL-value misconceptions (§10), never an obviously-wrong unit. The unit-dimension misconceptions (`LINEAR_UNITS_FOR_AREA`, `SQUARE_UNITS_FOR_PERIMETER`, `RIGHT_NUMBER_NO_UNIT`) are surfaced primarily as free-response checker feedback and targeted hints, per the brief.

---

## 5. Unit parser, formatter, and equivalence checker

All three components are authored independently in Python (`spi_oracle/unit_model.py`) first and mirrored byte-identically in TypeScript, following the oracle-first parity discipline. They are pure, deterministic, and unit-tested with golden + parity fixtures.

### 5.1 Parser: `string -> QuantityAnswer | ParseError`

The parser is intentionally narrow: it parses against the item's **single declared** `unit.baseUnit` and `unit.exponent`. It does not normalise across units (none exist in v1.0.0). Signature: `parse(raw: string, declared: UnitModel, accepts) -> { value: Rational, unit: UnitModel | null } | { error }`.

Algorithm (deterministic, no locale dependence):

1. Trim; collapse internal whitespace to a single space; lower-case the unit segment only.
2. **Split numeric segment from unit segment at the first alphabetic character.** Everything up to (not including) the first `[a-z]` is the numeric segment; the remainder is the unit segment. The numeric segment may itself contain an internal space for a mixed number (`2 1/2`), which is preserved. Examples: `"15 cm^2"` → `("15 ", "cm^2")`; `"30/2 cm"` → `("30/2 ", "cm")`; `"7.5cm²"` → `("7.5", "cm²")`; `"2 1/2 m"` → `("2 1/2 ", "m")`.
   - **Corrected split rule (consistent with the step-4 token table).** The unit segment is parsed by **one regex over the closed alternation** `{ε, "2", "^2", "²"}` immediately following the base-unit letters, optionally prefixed by `"sq "` or `"square "`. A bare digit `2` is treated as a unit character **whenever it directly follows the base-unit letters** (so `cm2`, `mm2`, `m2` are exponent-2 tokens), not only when bound to `^`. (This removes the earlier draft's contradiction where `15cm2` would have left a dangling `2`.)
3. **Numeric parse** of the numeric segment into an exact `Rational`:
   - integer `^-?\d+$` → `{num, den:1}`;
   - fraction `^-?\d+/\d+$` → reduced `Rational`;
   - decimal `^-?\d+(\.\d+)?$` → exact `Rational` via `from_decimal` (e.g. `7.5` → `15/2`), accepted only when `accepts.decimal` and the value terminates;
   - mixed `^-?\d+ \d+/\d+$` → `whole + fraction` as a reduced `Rational`, accepted only when `accepts.mixed` (off by default). The internal space inside a mixed number is the ONLY internal space allowed in the numeric segment; because the unit split happens at the first *alphabetic* char (step 2), the mixed-number space is never mistaken for the numeric/unit boundary. Example: `parse("2 1/2 m", …)` → numeric `2 1/2` = `5/2`, unit `m`.
   - Any other numeric form → `error: "unparseable-number"`.
   - Negative inputs **parse** (the `-?` is intentional) and fall through to gate 4 as `wrong-value` — every length/area answer is a positive exact value (§12), so a negative is simply numerically wrong; no separate impossible-sign feedback is emitted in v1.0.0 (a `negative-measure-impossible` hint is a possible future tightening, noted but not specified here).
4. **Unit parse** of the unit segment into a `UnitModel` via the canonical token table for the **declared `baseUnit` only**:

   | Accepted unit token (case-insensitive) | Parses to (exponent) |
   |---|---|
   | `cm` | `cm`, exponent 1 |
   | `cm^2`, `cm2`, `cm²`, `sq cm`, `square cm` | `cm`, exponent 2 |
   | `mm`, `mm^2`/`mm2`/`mm²`/`sq mm`/`square mm` | `mm`, exp 1 / exp 2 |
   | `m`, `m^2`/`m2`/`m²`/`sq m`/`square m` | `m`, exp 1 / exp 2 |
   | *(empty / no unit segment)* | `unit = null` (NOT an error — deferred to gate 1) |
   | *(a recognised unit token whose base ≠ declared `baseUnit`)* | `error: "wrong-base-unit"` |
   | *(unrecognised token)* | `error: "unrecognised-unit"` |

   The parser returns the *structured* `UnitModel` it recognised (dimension/exponent derived from the token), **not** the raw text. From here on nothing compares strings.

   **Empty unit owned by gate 1, not gate 0.** An empty unit segment yields `unit = null` and is NOT a parse error. This makes gate 1 (`missing-unit`, honouring `accepts.requireUnit`) the single owner of the missing-unit feedback, and lets `requireUnit:false` legitimately accept a unit-less numeric. (The earlier draft's `missing-unit` row in the parser error table is removed; only `unrecognised-unit` and `wrong-base-unit` remain parser errors.)

### 5.2 Formatter: `QuantityAnswer -> canonical display`

Pure inverse of the canonical token, used for `answer.display`, every option/distractor `display`, solution steps, and the answer-key overlay:

```
formatUnit(u)  = u.exponent === 1 ? u.baseUnit : u.baseUnit + "^2"     // "cm", "cm^2"
formatValue(v) = v.den === 1 ? String(v.num) : `${v.num}/${v.den}`     // reuses Rational.toString
format(a)      = `${formatValue(a.value)} ${formatUnit(a.unit)}`        // "15 cm", "24 cm^2", "15/2 m^2"
```

The formatter is the SOLE producer of `unit.display` and `answer.display`; it is byte-identical Py↔TS so stored displays match the oracle exactly (the parity contract). The stored canonical `display` ALWAYS uses the ASCII `^2` token and NEVER the Unicode `²`, asserted by a named `display-is-ascii-caret` check (no stored `display` or `unit.display` may contain `²`), so golden/parity fixtures are byte-stable across encodings/locales — even though the parser *accepts* `cm²` as input. A KaTeX surface form (`24\,\text{cm}^2`) is derived for presentation in prompt/solution blocks, but the stored canonical `display` uses the plain `^2` token shown above.

### 5.3 Equivalence checker contract

`check(raw: string, answer) -> { correct: bool, feedbackId, detail }`. The checker treats unit meaning **structurally**: it compares the parsed `UnitModel`'s `(dimension, exponent, baseUnit)` triple against the canonical `answer.unit`, and never compares raw text suffixes. Evaluation order (first failing gate decides the targeted feedback):

| # | Gate | Condition checked | On failure: feedbackId |
|---|---|---|---|
| 0 | parse | `parse(raw, answer.unit, answer.accepts)` succeeds (no `unparseable-number`/`unrecognised-unit`/`wrong-base-unit` error) | `unparseable-number` / `unrecognised-unit` / `wrong-base-unit` |
| 1 | unit present | parsed `unit !== null` (when `accepts.requireUnit`; skipped when `false`) | **`missing-unit`** |
| 2 | base unit | `parsed.unit.baseUnit === canonical.unit.baseUnit` | `wrong-base-unit` |
| 3 | dimension | `parsed.unit.dimension === canonical.unit.dimension` **and** `parsed.unit.exponent === canonical.unit.exponent` | **`linear-for-area`** (gave exp 1, area required) / **`square-for-perimeter`** (gave exp 2, length required) / generic `wrong-dimension` |
| 4 | value | `parsed.value` equals `canonical` by exact cross-multiplication: `num₁·den₂ === num₂·den₁` (so `30/2 == 15`, `15/2 == 7.5`), subject to `accepts` for the input *form* | `wrong-value` |
| — | pass | all gates pass | `correct` |

(Note: `wrong-base-unit` surfaces at gate 0 as a parser error when the token is recognised but mismatched; gate 2 is the equivalent structural re-assertion for any path that reaches it. Both map to the same `wrong-base-unit` feedback.)

Key properties, each backed by a named validator check:

- **`equiv-numeric-forms`**: mathematically-equivalent numeric forms with the correct unit are accepted — `30/2 cm`, `15 cm`, `15.0 cm` all pass against canonical `(15, cm¹)`. Equality is exact `Rational` cross-multiplication, never float compare.
- **`distinguish-length-area`**: length and area are separated by the `(dimension, exponent)` pair, not by token text. `15 cm` against an area answer fails gate 3 with `linear-for-area`; `15 cm^2` against a perimeter answer fails gate 3 with `square-for-perimeter`.
- **`reject-correct-number-wrong-dimension`**: a numerically-correct response with the wrong dimension is rejected at gate 3 (it never reaches gate 4).
- **`reject-cross-square`**: `cm` is rejected when `cm^2` is required and vice versa — this is gate 3, because `cm` parses to exponent 1 and `cm^2` to exponent 2; the structural triple differs even though the base text `cm` is shared.
- **`targeted-unit-feedback`**: gates 1/3 emit *targeted* feedback IDs — `missing-unit`, `linear-for-area`, `square-for-perimeter` — which map to the corresponding `MISC.MENS.*` unit-dimension misconceptions (§10: `RIGHT_NUMBER_NO_UNIT`, `LINEAR_UNITS_FOR_AREA`, `SQUARE_UNITS_FOR_PERIMETER`) and to student-facing hints. Feedback text is built from displayed values only (no internal symbols), consistent with the misconception-feedback contract.
- **`structural-not-textual`**: the checker function literally has no branch that string-compares a unit suffix; the only string handling is in the parser's token table, after which all logic is over `UnitModel` fields. A unit test asserts that visually-distinct-but-equivalent unit spellings (`cm^2`, `cm2`, `cm²`, `square cm`) are accepted identically, and that a textually-similar-but-wrong unit (`cm` for `cm^2`) is rejected — proving the suffix string itself is never the comparison key.

### 5.4 No conversion; one declared unit

The checker has no conversion table and never rescales `value`. A recognised non-declared base is rejected outright (`wrong-base-unit`, gate 0/2); there is no path that turns `m` into `cm`. This makes the v1.0.0 contract total and unambiguous and leaves a clean seam for the future `cm↔m` conversion objective (which would add a gate-2.5 conversion step plus a `unit.scale` field — an additive, owner-gated extension, not a v1.0.0 behaviour).

### 5.5 Parity, registration, and coverage

- **Oracle-first parity.** `unit_model.py` (parser/formatter/checker) is authored and frozen in `spi_oracle` before the TS mirror; golden fixtures (canonical encodings for each `(dimension, baseUnit)`, plus the `display-is-ascii-caret` assertion on every stored display) plus a parity suite (150×2 raw inputs spanning every gate outcome, including the `cm²`/`cm2`/`cm^2`/`square cm` spellings and the `2 1/2 m` mixed+unit grammar) assert byte-identical Py↔TS results. The 10,000-seed `SPI_SWEEP` re-runs the checker on every generated item's canonical answer and on each distractor (the independent recomputation), proving no distractor ever equals the correct answer under the checker.
- **Schema validation (correct scope).** Live `quantity` items (a length item, an area item, and a rational-area item) are added to `oracle/check_conformance.py`'s live-generation block and to the production Ajv gate. **What each gate proves differs:** `check_conformance.py` confirms the items' structural shape (enum membership of `quantity`, `required`, `additionalProperties:false`, the `unit` enums) but — because it does not implement `allOf/if/then/const` — does NOT enforce the dimension/exponent lock or the `quantity ⇒ unit` requirement; those are enforced by the production Ajv gate and by the validator checks `unit-model-wellformed` / `unit-contract` / `answer-type-consistency` / `quantity-dimension-exponent-lock` (§4.4, §9).
- **COVERAGE-MATRIX.** The new `quantity` type is a first-class "realised answer shape"; the reachability-derived review-pack COVERAGE-MATRIX (reused exactly from stats v1.0.2) requires cells for length AND area answers, integer AND rational values, and mm/cm/m contexts, and the pack builder FAILS on any missing reachable cell — so §13's accessibility text and the checker's targeted-feedback paths are both exercised by construction.


---

## 6. Canonical polygon and dimension data model

### 6.1 One source of truth

A single immutable record — the **`Figure`** — is the seeded source of truth for every downstream artifact, in the same way the stats family's single seeded dataset is (cf. the stats proposal §6.1 and `core/curriculum/stats-objective-ids.ts`'s single-source pattern, which this family mirrors in `core/curriculum/mensuration-objective-ids.ts`). From one `Figure` the generator derives, with no second authoring path: (a) the student diagram (§8 renderer); (b) every dimension label; (c) the prompt text; (d) the canonical dimensional-quantity answer (§4 contract); (e) the worked solution steps; (f) every misconception calculation (§10 adapters); (g) the accessibility `spokenMath` / `media[].altText` / `media[].longDescription` and the `media[].dataTableFallback` object; and (h) the independent validator's recomputation (§9). The validator reconstructs the `Figure` from `params` and asserts the stored SVG **byte-for-byte** (`svg-realises-data`) and the answer **by a second route** (`closure-agreement`), exactly as the canonical-SVG discipline requires. No artifact may read a value that is not a pure function of the `Figure`.

All coordinates and measurements are exact: integers or reduced `core/exact-math/rational.ts` `Rational{num,den≥1,reduced}` values (Python `fractions.Fraction`), serialized as `{num,den}`. There are **no irrationals** anywhere in the model — no surds, no `π`, no sloping-edge lengths that are not rational — a hard inheritance from the EXACT MATH convention that also enforces the brief's deferral of Pythagoras, circles, and general-triangle perimeter. In particular a triangle's hypotenuse, whose length would be `√(b²+h²)` and irrational for almost all integer `b,h`, is **never assigned a length and never measured** (§6.3, §6.5); the model has no field that could hold it.

### 6.2 Coordinate frame and `baseUnit`

Each `Figure` declares exactly one `baseUnit ∈ {mm, cm, m}` (the §4/§5 structural unit; **no cross-unit conversion in v1.0.0**). Vertices live in an abstract **shape-coordinate** plane whose unit is the `baseUnit`; the renderer's `gridRound` projection (§8, reusing the coordinate-lines single-projection-of-record over exact `Rational`) maps shape coordinates to the canonical `viewBox 0 0 1000 700` integer pixel grid.

Shape coordinates are **integer-valued for rectangles and rectilinear composites** (axis-aligned integer edges), which keeps their perimeters and areas exact integers (§6.6). A **triangle** may carry **one rational coordinate** — the foot of the perpendicular height along the base — so that the area `b·h/2` is the only place a reduced `Rational` answer arises in v1.0.0; the base endpoints and the apex remain integer/rational-but-projected exactly via `gridRound`. This resolves the prior internal tension: rational *answers* are reachable (triangle area and the missing-dimension tasks, §6.6), while rectangle/composite *side lengths* stay integer, so the §4 worked encodings and the §3.2 value-form column attach "rational only when a side is rational" to **triangle and missing-value tasks**, never to rectangle perimeter/area.

Field shapes below are written as TypeScript-flavoured interfaces for precision; they are the **proposed** model, mirrored byte-for-byte in the Python oracle (oracle-first) and not yet implemented.

```
type Q = { num: number; den: number };        // exact Rational JSON, den ≥ 1, reduced
type Pt = { x: Q; y: Q };                       // shape-coordinate vertex (baseUnit units)
type Dim = "length" | "area";
type BaseUnit = "mm" | "cm" | "m";

// The eight canonical task slugs — the §1.3 MENSURATION_TASKS set, verbatim,
// re-used as keys by OBJECTIVE_BY_TASK, RULES_BY_TASK (§10.3), the COVERAGE-MATRIX
// cell tokens (§14), and the generator dispatch. No alternative spellings exist.
type MensTask =
  | "perimeter_rectangle"
  | "perimeter_composite"
  | "area_rectangle"
  | "area_triangle"
  | "area_composite"
  | "missing_length_perimeter"
  | "missing_dimension_area"
  | "missing_triangle_base_height";

interface Figure {
  kind: "rectangle" | "rectilinear" | "triangle";
  baseUnit: BaseUnit;                            // ONE unit throughout (§4/§5)
  vertices: Pt[];                                // ordered CCW; integer for rect/rectilinear
  edges: Edge[];                                 // derived, indexed, with orientation
  dimensions: DimAnnotation[];                   // which segment each GIVEN measurement labels
  decomposition?: RectPiece[];                   // rectilinear only: disjoint rectangles ∪ = shape
  triangle?: TriangleSpec;                        // triangle only: base + perpendicular height
  hidden?: HiddenTarget;                          // missing_* tasks: the unknown to recover
  task: MensTask;                                // §3 task slug (single-source OBJECTIVE_BY_TASK map)
}
```

### 6.3 Edges and orientation

`edges` is derived from `vertices` (consecutive pairs, closing the polygon) so closure is structural, not asserted. Each edge records its orientation, which the renderer and validator both consume:

```
interface Edge {
  index: number;                 // 0..n-1, position in the boundary walk
  a: number; b: number;          // vertex indices (a → b along CCW boundary)
  orient: "H" | "V";             // horizontal | vertical (axis-aligned invariant)
  length: Q;                     // exact |b − a| along its axis
  dir: "N" | "S" | "E" | "W";    // outward boundary-walk direction
}
```

For rectangles and rectilinear composites every edge satisfies `orient ∈ {H,V}` — the **orthogonality invariant** (`edges-orthogonal`, §9/§12). A triangle's base and its perpendicular height are both axis-aligned (the height of a horizontal base is vertical, and vice versa — see §6.5 and §8); the **hypotenuse is the only non-axis edge and carries no `length` and no dimension annotation**. Because the hypotenuse is never measured, a triangle perimeter is structurally unaskable, which is exactly what keeps general-triangle perimeter deferred (§7.7, §12.4).

### 6.4 Dimension annotations — the label-to-segment binding

`dimensions[]` is the explicit, machine-checked binding the brief demands ("make it unambiguous which side each measurement belongs to"). Each annotation names the segment it labels, the exact value, and the placement role the renderer uses to keep labels off edges and off each other (§8):

```
interface DimAnnotation {
  id: string;                    // stable, e.g. "d0"
  target:                        // what the measurement labels:
    | { kind: "edge"; edge: number }                      // a single boundary edge
    | { kind: "span"; from: Pt; to: Pt; axis: "H"|"V" }   // an overall extent (composite width/height)
    | { kind: "height"; foot: Pt; apex: Pt };             // triangle perpendicular height
  value: Q;                      // exact measurement, in baseUnit
  given: boolean;                // true = shown to student; false = hidden/derived (§6.7)
  side: "above" | "below" | "left" | "right";  // leader/label placement role
  role: "edge-length" | "extent" | "perp-height" | "base";
}
```

**Invariants** (validated, §9): every `given` annotation's `value` equals the exact geometric length of its `target` (`dimension-matches-geometry`); no two `given` annotations bind the same segment (`no-duplicate-dimension`); the set of `given` length annotations is exactly **sufficient and minimal** to determine the asked quantity (`givens-determine-answer`, `givens-minimal`); and **no `given:false` annotation is ever rendered** in the student figure (`no-hidden-dimension-shown`, the answer-leakage gate of §8/§9).

### 6.5 The three shape families

**Rectangles.** `kind:"rectangle"`, four vertices `(0,0),(w,0),(w,h),(0,h)`, **integer** `w,h`. Two `given` annotations bind the width edge and a height edge. Perimeter `P = 2(w+h)`, area `A = w·h` — both exact integers (never rational, since both sides are integer). Orientation is varied deterministically (portrait / landscape / square) by swapping the sampled `w,h` roles, satisfying the review-pack "rectangles with different orientations" cell.

**Rectilinear composites (incl. L-shapes).** `kind:"rectilinear"`. The polygon is **assembled from non-overlapping axis-aligned rectangles with integer dimensions** whose disjoint union is the shape; `decomposition[]` records exactly those rectangles:

```
interface RectPiece { x: Q; y: Q; w: Q; h: Q; }   // axis-aligned, integer, bottom-left origin
```

The boundary `vertices` are computed from the union outline (the merged exterior walk), guaranteeing **closed, non-self-intersecting, orthogonal, overlap-free** by construction. Two independent area routes must agree (the brief's required cross-check):

- **Shoelace** over the integer vertices: `A_shoelace = ½ |Σ (xᵢ·yᵢ₊₁ − xᵢ₊₁·yᵢ)|` (exact, computed with `Rational`; integer for integer vertices).
- **Decomposition**: `A_decomp = Σ pieceⱼ.w · pieceⱼ.h`.

`area-methods-agree` asserts `A_shoelace == A_decomp` exactly; the worked solution narrates the **decomposition** route while the validator independently confirms via shoelace. Perimeter is the length of the **complete exterior boundary** `P = Σ exterior edge.length` (every boundary edge, including indented edges) — never a piece-perimeter sum, which would omit indented edges or double-count internal cuts. These are precisely the misconceptions `MISC.MENS.OMITS_INDENTED_EDGE` and `MISC.MENS.DOUBLE_COUNTS_INTERNAL_EDGE` (§10); the canonical perimeter is constructed so the validator can recompute each through its registry adapter.

**Triangles.** `kind:"triangle"`, with an **explicitly shown perpendicular base and height**:

```
interface TriangleSpec {
  base:   { from: Pt; to: Pt; length: Q; orient: "H"|"V" };  // a true axis edge (integer length)
  height: { foot: Pt; apex: Pt; length: Q };                 // ⟂ to base; axis-aligned; perp marker
  rightAngleAt: Pt;                                          // foot of the height (marker drawn)
}
```

The base is axis-aligned; the height is **perpendicular to it and therefore itself axis-aligned** (vertical for a horizontal base, horizontal for a vertical base, including the obtuse case where the foot lies on the extended base). A right-angle marker is drawn at `foot` and a perpendicular-height marker along the dashed height segment (§8 primitives). Exact area `A = base·height / 2`. When the declared band requires an **integer** area, parities are chosen at construction so that `base·height` is even (§6.6, §7.2); otherwise the area is a reduced `Rational` (e.g. `base=3, height=5 → A = 15/2`), a legitimate exact answer and the family's primary source of rational answers.

The sloping side (hypotenuse) is **never labelled and carries no length** (§6.3). This both keeps triangle perimeter deferred and forces students onto the perpendicular height. The corresponding pitfall — using a sloping side in place of the perpendicular height — is registered as `MISC.MENS.USES_SLOPING_SIDE` but, because that side's length is irrational for almost all integer `b,h` and cannot be represented as a reduced `Rational` `quantity`, it is a **free-response feedback / hint rule only** (its adapter returns `null` for distractor synthesis). It never produces a numeric value distractor, consistent with §10's classification and with `area_triangle` drawing its MC value distractors, where eligible, from exact rules only.

### 6.6 Exactness and parity guarantees (per task)

| Task slug | Answer formula | Exactness guarantee |
| --- | --- | --- |
| `perimeter_rectangle` | `2(w+h)` | always integer (integer sides) |
| `perimeter_composite` | `Σ exterior edge.length` | integer (integer edges) |
| `area_rectangle` | `w·h` | always integer (integer sides) |
| `area_triangle` | `b·h/2` | integer if `b·h` even; else reduced `Rational` (both allowed) |
| `area_composite` | `Σ piece w·h` (= shoelace) | integer (integer pieces) |
| `missing_length_perimeter` | `½P − Σ known` or single missing exterior edge | integer by construction (§7.4) |
| `missing_dimension_area` | `A / known` | constructed so `known ∣ A` exactly (integer answer) |
| `missing_triangle_base_height` | `2A / known` | emitted **only when `known ∣ 2A` exactly** (integer or reduced `Rational`), else redraw |

Rational answers therefore arise only on `area_triangle` and (where the construction yields one) `missing_triangle_base_height`; rectangle and composite tasks are integer-only. The §14 coverage matrix attaches the `…:rational:…` cells to these triangle/missing tasks accordingly, so every declared shape×band cell is reachable.

### 6.7 The `hidden` target for missing-value tasks

```
interface HiddenTarget {
  ask: "missing-length" | "missing-dimension" | "missing-base-or-height";
  givenQuantity: { dim: Dim; value: Q; unit: BaseUnit };  // the stated P or A
  recover: DimAnnotation;   // the annotation whose value is hidden (given:false) and asked
}
```

For `missing_length_perimeter`, `missing_dimension_area`, and `missing_triangle_base_height` the asked annotation is `given:false`, so by §6.4 it is **never rendered** — the figure shows the other measurements, and the stated perimeter/area appears only in the prompt, expressed through the §4/§5 dimensional-quantity formatter so its unit is structurally correct (`dim = "length"` for `missing_length_perimeter`; `dim = "area"` for the two missing-area tasks). The student recovers the hidden value. Unique recoverability is a construction invariant (§7.4): the hidden value must be the **unique** solution of the perimeter/area equation given the rendered measurements (`hidden-uniquely-recoverable`). `missing_triangle_base_height` is additionally gated by exactness (`2A / known` must be an exact integer/rational, else deterministic redraw — §7.5), realising the brief's "missing triangle base or height ONLY when the exact answer is guaranteed."

The canonical answer is the §4 contract: `answer = { type: "quantity", canonical: {num,den}, unit: { dimension, baseUnit, exponent, display }, display, accepts: {…, requireUnit} }`. The numeric value lives in `canonical` as a bare reduced `Rational` (preserving the existing exact-rational serialization path byte-for-byte); the structured unit is a **separate sibling** `answer.unit`. The validator's `closure-agreement` recomputes the `Rational` value by a second route and independently rebuilds the unit triple `(dimension, baseUnit, exponent)`, comparing the value and the triple — not a merged object (§9).

### 6.8 Deterministic value ranges per `baseUnit`

To keep figures readable (legible labels, non-degenerate proportions) and answers small enough for exact JS-integer arithmetic, each `baseUnit` pins a sampling range used by §7's backward construction. Ranges are deterministic and frozen (any later change is a versioned, owner-gated revision):

| `baseUnit` | edge-length range (inclusive, integer) | typical area magnitude | rationale |
| --- | --- | --- | --- |
| `mm` | 10..90 | up to ~8100 mm² | whole-mm classroom rulers; avoids 1–2 digit cramping |
| `cm` | 2..30 | up to ~900 cm² | the dominant middle-school context |
| `m` | 2..20 | up to ~400 m² | room/floor contexts; keeps integer m sensible |

All rectangle/composite edge lengths and all triangle bases and heights are sampled as integers from the range for the chosen `baseUnit`; the only rational *answer* arises from the exact halving in `area_triangle` / `missing_triangle_base_height`, not from rational *side lengths*. For composites, each constituent `RectPiece` dimension is sampled from the same range and the overall extent is bounded so the projected figure fills but does not overflow the `viewBox` drawable area (the §8 viewport check, mirroring coordinate-lines' `U_MIN` unit-scale floor). The range is a property of the `Figure`, recorded in `params`, so the oracle and TS sample identically.

---

## 7. Backward construction of valid questions

### 7.1 Deterministic pipeline (parity contract)

Generation is **backward**: rather than drawing a shape and hoping the answer is exact and unique, the generator picks the answer's exactness/uniqueness conditions first and constructs a `Figure` that satisfies them by construction. The pipeline is a fixed call sequence on the byte-identical `core/seeded-random/mulberry32.ts` / `oracle/spi_oracle/seeded_random.py` PRNG; **call order is the parity contract** (the deterministic-redraw loop is identical in both languages, and `nextInt(lo,hi)` is inclusive):

```
seed
  → pick task             (m.choice over the MENSURATION_TASKS roster / weighted §3 schedule)
  → pick baseUnit         (m.choice over {mm,cm,m})
  → sample shape params   (§7.2–7.4, integers from the §6.8 range for that baseUnit)
  → build Figure          (vertices, edges, dimensions, decomposition/triangle, hidden)
  → run GUARD predicates  (§7.5)  — if any fails: REDRAW (re-enter loop, next draw)
  → derive answer + solution + misconception values + accessibility + SVG
```

Every redraw re-enters the **same** loop and consumes the **next** deterministic draws, so the oracle and TS diverge nowhere. `params` records the accepted draw so the item is reproducible and the validator can reconstruct the `Figure` (§9).

### 7.2 Construction by task — direct-answer tasks

| Task slug | Construction | Exact + unique by |
| --- | --- | --- |
| `perimeter_rectangle` | sample integer `w,h` in range; both given | integer `2(w+h)` |
| `area_rectangle` | sample integer `w,h` in range; both given | integer `w·h` |
| `perimeter_composite` | choose a rectilinear template (L-shape / step / T); sample the ≤ 6 integer piece dimensions; emit exterior `vertices`; give a **minimal sufficient** subset of edges (one missing exterior edge always derivable from the others) | integer `Σ exterior edges`; `givens-minimal` |
| `area_composite` | same composite construction; record `decomposition[]`; give the piece-determining edges | `A_shoelace == A_decomp` (§6.5) |
| `area_triangle` | sample integer `base`; sample integer `height`; for the **integer-area** band, resample `height` until `base·height` is even (bounded redraw, §7.5); else accept the reduced-`Rational` area | exact `base·height/2`; perpendicular by construction |

For composites the generator picks from a small, enumerated **rectilinear template set** (L-shape in 4 rotations/reflections, a 2-step staircase, a T/plus — giving the brief's "several L-shape configurations" variety), instantiates integer piece dimensions from the §6.8 range, and computes the merged exterior outline. Because pieces are axis-aligned, integer, and non-overlapping by template, closure / orthogonality / non-self-intersection hold without search.

### 7.3 Choosing which edges are `given` (uniqueness of the question)

A composite must be **exactly reconstructible from its given dimensions + vertices** and have **one** determined answer. The generator marks edges `given` so that:

- the marked set is **sufficient**: every unmarked exterior edge length is forced by the marked ones (axis-aligned closure: opposite horizontal runs sum-match, likewise vertical), so the figure is fully determined (`givens-determine-figure`);
- the marked set is **minimal**: removing any one given makes some edge ambiguous (`givens-minimal`) — this prevents over-labelling and creates the genuine "missing exterior length" reasoning the brief asks for in `perimeter_composite` / `missing_length_perimeter`.

### 7.4 Construction by task — missing-value tasks

These are built **answer-first**: pick the hidden value, derive the stated quantity, then hide the value.

- **`missing_length_perimeter`.** Build a rectangle or composite (integer edges); choose one exterior edge as `recover` (`given:false`); compute `P` from the complete boundary; state `P` in the prompt as a `length` `quantity`; render the remaining edges. Uniqueness: in a rectangle the missing side is `½P − knownSide`; in a composite the missing exterior edge is forced by the parallel-run sum identity. `hidden-uniquely-recoverable` confirms exactly one edge value closes the boundary at the stated `P`. The answer is an integer length.
- **`missing_dimension_area`.** Sample the integer **answer** dimension `d` and the known integer dimension `k` from the range; set `A = k·d`; hide `d`. Recovery `d = A / k` is an exact integer by construction (`A` is sampled only as a `k`-multiple, never freely), so `area-divides-exactly` (the `k ∣ A` guard) always holds. The stated `A` is an `area` `quantity`.
- **`missing_triangle_base_height`.** Sample the integer hidden dimension `x` and the known integer dimension `k`; set `A = k·x/2`. Emit the item **only if** `2A / k` is an exact integer/rational and the perpendicular construction is valid; otherwise **redraw** (§7.5). This guarantee — "ONLY when the exact answer is guaranteed" — is enforced, never assumed; the common trap of an unrecoverable half-integer is structurally excluded. The stated `A` is an `area` `quantity`; the recovered base/height is a `length` `quantity` (integer or reduced rational).

In all three, the stated `givenQuantity` is the dimensional quantity the §4 contract checks (`dim = "length"` for `missing_length_perimeter`, `"area"` for the two missing-area tasks), and the prompt presents it through the §5 formatter so its unit is structurally correct.

### 7.5 Deterministic redraw (guard) conditions

After building a `Figure` the guard predicates run in a fixed order; **any failure triggers a deterministic redraw** (identical in Py/TS), consuming the next draws. The guards encode the brief's degeneracy and quality rules and use the §12 canonical check names:

| Guard | Rejects | Why |
| --- | --- | --- |
| `non-degenerate` | any edge length `≤ 0`; rectangle with `w=0`/`h=0`; triangle with `base=0` or `height=0`; collinear "triangle" | no zero-area / zero-length figures |
| `simple-closed` | self-intersecting or non-closed boundary; overlapping pieces; coincident vertices | rectilinear validity (§6.5) |
| `edges-orthogonal` | any non-axis edge on a rectangle/composite (and on a triangle base/height) | orthogonality invariant; keeps the hypotenuse the only non-axis edge |
| `exact-required` | a band requiring an integer answer but `b·h` odd (`area_triangle`), or `k ∤ 2A` (`missing_triangle_base_height`), or `k ∤ A` (`missing_dimension_area`) | exact-answer guarantee |
| `unique-answer` | hidden value not uniquely recoverable; givens insufficient or non-minimal | one determined answer |
| `well-proportioned` | aspect ratio outside `[1:6 … 6:1]`; any edge projecting to `< MIN_EDGE_PX`; overall extent overflowing the drawable `viewBox` | readable, to-scale figures |
| `label-room` | projected dimension-label boxes that would collide with edges, leaders, or each other after §8 placement | "labels never touch edges/leaders/other labels" |

Redraws are bounded by a fixed cap per item; the cap and the redraw **rate** are reported in the §11/§14 distribution report and review pack (the same reachability-derived COVERAGE-MATRIX machinery the stats family froze), so a pathological task surfaces rather than silently looping.

### 7.6 To-scale preference and regeneration

Per the brief, figures are drawn **mathematically to-scale** from the integer/rational shape coordinates via the §8 `gridRound` projection, and `media[].toScale` is set `true` (as in coordinate-lines). When the sampled proportions would render poorly (caught by `well-proportioned`), the **deterministic** response is to redraw with the next seed-draw — never to fudge coordinates or fall back to a not-to-scale schematic. Because the projection is a pure function of exact `Rational` vertices and is byte-identical across Py/TS, "to-scale" costs no parity: the validator recomputes the same integer pixel coordinates and asserts the SVG byte-for-byte (`svg-realises-data`, §9).

### 7.7 Deferred shapes are unreachable, not merely undrawn

The task enum (`MENSURATION_TASKS`), the template set, and the construction pipeline have **no path** that produces a deferred figure: no circle / `π` (no arc primitive, no irrational radius); no volume / surface-area (the model is strictly 2-D, single-polygon); no general-triangle perimeter (the hypotenuse carries no length and no `given` annotation, so a triangle perimeter is unaskable, §6.3); no trapezium / non-rectilinear composite (templates are axis-aligned integer rectangles only; `edges-orthogonal` rejects any oblique edge); no Pythagoras / surds (EXACT MATH forbids irrationals, so even the `USES_SLOPING_SIDE` pitfall is FR-only and never materialises an irrational value, §6.5/§10); no unit conversion (one `baseUnit` per `Figure`, §6.2); no scale drawings, compound units, or approximate measurements (all values are exact and to-scale). A request for any deferred construction is rejected by guard, never silently downgraded — matching the deterministic-exclusion discipline the stats family established and the named exclusion tests in §12.4/§15.1.


---

## 8. SVG dimension-rendering contract

This section specifies the canonical, byte-identical SVG renderer for the mensuration family. It reuses, by name and without modification, the canonical-SVG discipline proven in the shipped geometry/statistics renderers (`domains/geometry/angles.ts`, `domains/geometry/coordinate-lines.ts`, `domains/statistics/data-handling.ts`): a hand-rolled serializer, integer coordinates via `gridRound` over exact `Rational`, byte-for-byte Python↔TypeScript output, a `role="img"` root with `<title>`/`<desc>` children, a per-figure data-table fallback, and no colour-only information. It adds the dimension-rendering primitives the family needs as a **new additive theme extension** (§8.2) exactly the way `core/visual-style/data-chart-theme.{json,ts}` added statistics primitives — the approved `cartesian-theme` and `data-chart-theme` outputs stay byte-for-byte unchanged.

There are **two render channels** built from the same `ShapeModel` (§6): the **student figure** (shown to the learner; only-given dimensions, no answer) and the **answer-key overlay** (an additive overlay used ONLY in answer-key / solution export channels). Both are pure functions of `params` through the `ShapeModel`; neither is authored independently. The overlay is, byte-for-byte, the student figure followed by strictly-additional trailing elements (§8.8), enforced by `overlay-is-strict-suffix-of-student-geometry` (§8.11).

The eight task slugs used throughout this section are the single canonical set defined in §1.3 `MENSURATION_TASKS` and consumed verbatim by `OBJECTIVE_BY_TASK`, `RULES_BY_TASK`, the §14 coverage cells, and the §15 scope list: `perimeter_rectangle`, `perimeter_composite`, `area_rectangle`, `area_triangle`, `area_composite`, `missing_length_perimeter`, `missing_dimension_area`, `missing_triangle_base_height`. The render distinctions below are keyed off those slugs.

### 8.1 Canvas, coordinate system, and the pipeline

```
params (SSoT) ─▶ ShapeModel (exact Rational vertices + dimension annotations)
              ─▶ layout (integer affine fit into the plotting box)
              ─▶ gridRound (one rounding rule, exact Rational → int)
              ─▶ canonicalMensSvg(...) ─▶ media[].svg     (student)
                                       ─▶ media[].svg     (answer-key overlay; key/solution channels only)
        └──────────── identical bytes in oracle (Python) and production (TypeScript) ────────────┘
```

| Item | Value |
| --- | --- |
| `viewBox` | constant `"0 0 1000 700"` (`VIEW_W=1000, VIEW_H=700`, matching `angles.ts`/`coordinate-lines.ts`/`data-handling.ts`); never computed, never per-item |
| Root element (fixed, byte-identical to the shipped families) | `<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1000 700" role="img" aria-label="{esc(alt)}">` immediately followed by the children `<title>{esc(title)}</title>`, `<desc>{esc(desc)}</desc>`, then the canonical `<style>…</style>` block. No `width`/`height`, no `aria-labelledby`, no `id="fig-title"`/`id="fig-desc"`, no `preserveAspectRatio` — the shipped figures emit none of these, and reusing the discipline *verbatim* means matching that exact attribute sequence (a family-wide migration to `aria-labelledby` or `preserveAspectRatio` would be a separate owner-gated change and is explicitly NOT proposed here). `alt`/`title`/`desc` come from the §13 accessibility model |
| Presentation styling | the canonical `<style>` block is the in-figure default; `presentationSvg()`/`exportSvg()` (§8.2) strip it (regex `<style>…</style>`) and substitute the per-root `cx-figure` custom-property style — identical mechanism to `data-chart-theme.ts` |
| Y convention | `ShapeModel` is math-coordinates (y up); the serializer applies the fixed integer flip `y_svg = 700 − y_math` once, on integers |
| Plotting box | fixed integer inset of `80` → drawable region `[80,920] × [80,620]`; a reserved bottom strip `y∈[630,690]` holds the `NOT TO SCALE` banner when present |
| Coordinates | every emitted coordinate is an **integer** produced by `gridRound(num, den)` (round-half-up on the exact `Rational`, correct for negatives — the SAME single rounding rule used family-wide, no second mode) over the integer affine layout transform `(x,y) → (OX + SX·x, OY − SY·y)` with integer `OX,OY,SX,SY` chosen from a committed bounding-box-keyed lookup (never a float fit-to-view) |
| Numbers | emitted only via `fmtInt(n)` (base-10, no `+`, no leading zeros except `"0"`, `−` only for negatives). No decimal coordinate formatter exists in v1.0.0 (all rendered coordinates are integers post-`gridRound`; all dimension labels are integer/rational measurements formatted by the shared display helper, not float pixels) |

**To-scale by default; deterministic regeneration of poor proportions.** Unlike the angle family (whose integer-degree directions are irrational, forcing `toScale:false`), mensuration shapes are axis-aligned rectilinear polygons (and triangles with an axis-aligned base + perpendicular altitude) whose vertices are exact integers/rationals; the integer affine layout is an exact scaling, so figures **are** mathematically to-scale and `media[].toScale = true`. A `proportion-quality` guard (§8.10) runs in `generate()`: it rejects layouts where (a) the rendered aspect ratio of any rectangle/leg exceeds `8:1`, (b) any drawn edge is shorter than `60` viewBox units, or (c) a composite limb is too thin to host its dimension lines without collision. On rejection the generator advances the **same seeded `mulberry32` stream** to the next `params` (bounded redraw, the parity contract being call order) — it never silently ships a visually poor or mislabelled figure, and it never falls back to `toScale:false` for a shape that should be exact.

### 8.2 The additive mensuration theme extension (reuse the pattern, do not depend on data-chart-theme)

A new file pair `core/visual-style/mensuration-theme.{json,ts}` is introduced as a **versioned additive extension that `extends: "spi-math-cartesian-theme/1"` directly** — exactly as `data-chart-theme.json` does (`"extends": "spi-math-cartesian-theme/1"`, confirmed). It FOLLOWS the `data-chart-theme` additive *pattern* (same mechanism, same `cx-figure` root isolation, same `presentationSvg()`/`exportSvg()` contract) but it does **not** depend on `data-chart-theme`: `presentationSvg`/`exportSvg` compose **cartesian + mensuration** rulesets only, never `+ data-chart`, so none of the chart/pictogram `--cx-bar*`/`--cx-symbol*` variables are pulled in. Concretely, mirroring `data-chart-theme.ts`:

- `modeVars(mode) = { ...cartModeVars(mode), ...MENS_VARS[mode] }`; `COMMON_CSS = CART_COMMON_CSS + theme.commonCss`; `resolveCommonCss(mode)` resolves every `var(--cx-…)` for the export clone (with the same `#000` last-resort fallback the base helper uses).
- It **adds** dimension primitives as new `--cx-*` variables + one additive `commonCss` ruleset, and does NOT touch the base ruleset. New variables (and classes): `--cx-edge`/`.cx-edge` (shape outline — heaviest stroke), `--cx-dim-line`/`.cx-dim` (dimension line), `--cx-ext-line`/`.cx-ext` (extension line), `--cx-arrow`/`.cx-arrow` (arrowhead fill), `--cx-rt`/`.cx-rt` (right-angle marker), `--cx-perp`/`.cx-perp` (perpendicular-height marker), `--cx-measlbl`/`.cx-measlbl` (measurement label), `--cx-cut`/`.cx-cut` (decomposition cut line — overlay only), `--cx-ans`/`.cx-ans` (answer/derived annotation — overlay only).
- **Every one of the nine variables is given an explicit value in all four modes** (table below). This matters because the base cartesian ruleset sets only `.cx-figure text{…fill:var(--cx-text)}`; an unset stroke variable on `.cx-rt`/`.cx-perp`/`.cx-ext` has no base fallback and would resolve to the renderer default rather than the per-mode CVD-safe/dark colour. A `theme-completeness` test (mirroring `data-chart-theme.test.ts`) asserts each declared variable has a value in every mode and that no mensuration variable name collides with a cartesian or data-chart variable name.
- **Visual distinctness is encoded by shape/weight, never colour.** `.cx-edge` is the heaviest solid stroke; `.cx-dim` is a thinner solid stroke terminated by arrowheads and held off the shape by `.cx-ext`; `.cx-cut` is dashed; `.cx-perp`/`.cx-rt` are small fixed glyphs. This survives the monochrome `print` mode (the colour-free authoritative rendering) where every class resolves to opaque greyscale.

| Variable / mode | `print` (authoritative) | `premium` | `premium-dark` | `accessible` (CVD-safe) |
| --- | --- | --- | --- | --- |
| `--cx-edge` | `#111111` | `#1e293b` | `#e5e7eb` | `#000000` |
| `--cx-dim-line` | `#111111` | `#2563eb` | `#60a5fa` | `#0072b2` |
| `--cx-ext-line` | `#111111` | `#2563eb` | `#60a5fa` | `#0072b2` |
| `--cx-arrow` | `#111111` | `#2563eb` | `#60a5fa` | `#0072b2` |
| `--cx-rt` | `#111111` | `#1e293b` | `#e5e7eb` | `#000000` |
| `--cx-perp` | `#111111` | `#1e293b` | `#e5e7eb` | `#000000` |
| `--cx-measlbl` | `#111111` | `#111827` | `#e5e7eb` | `#000000` |
| `--cx-cut` (overlay, dashed) | `#111111` | `#7c3aed` | `#c4b5fd` | `#009e73` |
| `--cx-ans` (overlay) | `#111111` | `#dc2626` | `#f87171` | `#d55e00` |

`presentationSvg(svg, mode)` relies on BOTH document-level rulesets (cartesian + mensuration); `exportSvg(svg, mode, 6000, 4200)` bakes BOTH resolved rulesets inside the clone for the self-contained materialised **6000×4200** (default `width=6000, height=4200`, S=6) PNG/SVG export — identical mechanism to `data-chart-theme.exportSvg`. The coordinate-lines and stats figures continue to render byte-for-byte unchanged because mensuration only *adds* variables in the shared `--cx-*` namespace under the same `cx-figure` root and never modifies the base or the data-chart rulesets.

### 8.3 Element vocabulary and fixed z-order (student figure)

A small, total, fixed vocabulary (hand-rolled serializer, fixed element order, fixed attribute order per element, single `U+0020` between attributes, elements joined by `"\n"`, no indentation, void elements `<line .../>`; a single `escapeXml` over `& < > " '`; UTF-8, non-ASCII literal — identical serializer rules to the shipped families):

| Primitive | Element / class | Role |
| --- | --- | --- |
| Shape outline | `<polygon class="cx-edge">` (or `<line class="cx-edge">` per edge) | the rectilinear/triangle boundary; heaviest stroke |
| Extension line | `<line class="cx-ext">` | thin line projecting a vertex outward to the dimension line; **offset** from the edge |
| Dimension line | `<line class="cx-dim">` | the measured span, parallel to and **offset** from its edge |
| Arrowhead | `<polygon class="cx-arrow">` ×2 | inward-pointing triangles at each end of a dimension line |
| Right-angle marker | `<path class="cx-rt">` (small square) | placed at every rectangle corner and at the foot of every triangle altitude (the base–height right angle) |
| Perpendicular-height marker | `<path class="cx-perp">` (dashed altitude `cx-dim` + foot square) | the triangle altitude from apex to base, with a right-angle foot square where it meets the (possibly extended) base |
| Measurement label | `<text class="cx-measlbl">` | the given dimension value + unit (e.g. `7 cm`), anchored by the label engine (§8.6) |
| Vertex label | `<text class="cx-lbl">` | optional letter labels (A, B, …) reusing the base `.cx-lbl` |
| NOT TO SCALE banner | `<text class="cx-nts">` | emitted ONLY on the rare regeneration-exhausted fallback (normally absent — figures are to-scale) |

Fixed z-order (document order is the only SVG z-ordering and is part of the contract): **outline → extension lines → dimension lines → arrowheads → right-angle/perp markers → vertex labels → measurement labels → banner**. Labels last so the collision engine (§8.6) can place text over a settled geometry. All of these primitives are presentation-only and carry **no per-element `role`/`aria`** — they sit inside the single `role="img"` root, so the axe-core a11y gate (§13) sees exactly one labelled image, not many unlabelled graphics nodes.

### 8.4 Dimension lines, extension lines, and offset (distinct from shape edges)

The core legibility requirement — *dimension lines must be visually distinct from shape edges* — is met structurally, not by colour:

1. **Offset.** Every dimension line is drawn **parallel to its edge but offset outward** by a fixed integer gap `OFFSET = 28` viewBox units (the first dimension tier; nested/stacked dimensions step out by `OFFSET` per tier so composite dimensions never overlap). The offset direction is the outward normal of that edge (computed from the polygon winding, which is canonicalised counter-clockwise in §6).
2. **Extension lines.** Each dimension line is joined to the two vertices it measures by thin `cx-ext` lines that start a small fixed gap (`GAP = 6`) off the vertex and extend `OFFSET + 8` outward, so the dimension line never touches the shape outline.
3. **Arrowheads (all axis-aligned; no runtime trig).** Each dimension line terminates in two inward-pointing `cx-arrow` triangles built from a committed integer template. **Every dimension line in this family is horizontal or vertical** — for rectangles and rectilinear composites all measured edges are axis-aligned, and for triangles both the base (axis-aligned, `orient H|V`) and the perpendicular altitude (perpendicular to an axis-aligned base, hence also axis-aligned, even for an obtuse triangle whose foot lies on the extended base) are axis-aligned. The only slanted segment in any figure is a triangle's hypotenuse/slant side, which by §6 carries **no** dimension line and is never measured. Consequently there is no slanted dimension line, every arrowhead uses the axis-aligned integer template, and no runtime trigonometry is ever required — which strengthens the byte-parity guarantee.
4. **Stroke hierarchy.** `.cx-edge` stroke-width `3`; `.cx-dim`/`.cx-ext` stroke-width `1.5`. Distinct weight + arrowheads + offset together guarantee the dimension annotation reads as separate from the boundary in every mode, including 1-bit print.

The blocking validator `dimension-line-distinct-from-edge` (§8.11) asserts no `cx-dim` segment is collinear-and-coincident with any `cx-edge` segment and that every `cx-dim` line carries two arrowheads and lies at a tier-multiple of `OFFSET` off its edge.

### 8.5 Right-angle and perpendicular-height markers

- **Right-angle markers** are placed at all four corners of every rectangle (and at the foot of every triangle altitude). The marker is a fixed-size integer square path inside the corner. `right-angle-marker-present` asserts one marker per rectangle corner.
- **Perpendicular-height marker (triangles).** For `area_triangle` and `missing_triangle_base_height`, the altitude is drawn as a `cx-perp` dashed segment from the apex perpendicular to the (extended, if necessary) base, terminated at its foot by a right-angle foot-square. This is what makes the height *explicitly shown and perpendicular* — the owner brief's hard requirement (triangle areas use an EXPLICITLY SHOWN perpendicular base and height; a sloping side is never the height). The base dimension is on the base edge; the height dimension is on the altitude (itself axis-aligned per §8.4). `perp-height-marker-present` asserts that every triangle figure carries exactly one altitude with a foot right-angle square, and that the altitude meets the base at 90° in the integer geometry.

### 8.6 Deterministic label-placement and collision policy (adaptive label engine)

The brief requires that dimension labels never collide with edges, leaders, or other labels, and that each measurement is unambiguously attributed to its side. This **reuses the geometry-angles adaptive label engine + leader-rendering contract** (`angles.ts`, `GENERATOR_VERSION = "1.2.3"`: primary geometry solid; callout leaders thinner than every geometry stroke, dashed, round-capped, secondary; non-degenerate; non-crossing; deterministic regeneration when no valid layout exists). The mensuration specialisation:

1. **Candidate anchors (deterministic, ordered).** For each given dimension, the engine computes an ordered list of candidate label positions: (1) centred on its dimension line, just outside it (outward normal), (2) centred but inside the offset gap, (3) shifted to the near third / far third of the span, (4) a **callout** in clear space joined to the dimension-line midpoint by a `cx-ext`-style dashed round-capped leader. The order is fixed so Python and TS choose the identical anchor.
2. **Bounding boxes are exact integers.** Each label's box is computed from a committed per-glyph advance-width table over the restricted label charset (digits, space, `c`,`m`,`²`, `−`, `/`) at the fixed `cx-measlbl` font size — so boxes are integer-positioned and collision is testable **without rendering** and identical cross-language (no font-metrics drift). This mirrors the angle family's integer-box label test.
3. **Collision policy.** A candidate is accepted only if its box clears, by ≥ `8` units (the approved min clearance), every: shape edge, extension line, dimension line, arrowhead, marker, and every already-placed label box. The first clearing candidate in the deterministic order wins. If no candidate clears, the engine escalates to the callout tier; if the callout also fails, `generate()` triggers a bounded seeded redraw of `params` (deterministic regeneration — never a silent overlap).
4. **Side attribution.** Each label is bound to exactly one edge by its anchor geometry: a label is placed on (or leadered to) the midpoint of the dimension line that measures that edge, on the outward side, so "which side does `7 cm` belong to" is positionally unambiguous. For composite limbs where two short collinear edges are near, the engine prefers the callout tier with a non-crossing leader to the correct segment midpoint. `side-attribution-unambiguous` asserts each `cx-measlbl` maps to exactly one edge (its leader/anchor midpoint lies within `GAP` of one and only one dimension-line midpoint, and leaders do not cross).

### 8.7 Only-given dimensions; no answer in the student figure

The student figure is governed by an intent/role-based answer-leakage policy (semantic, not "no numeral appears"):

- **Only given dimensions are drawn.** The renderer iterates the `ShapeModel.givenDimensions[]` set — exactly the measurements the prompt supplies — and emits one dimension line + label per given. It NEVER iterates derived quantities.
- **The missing side is never shown.** For `perimeter_composite`, `area_composite`, `missing_length_perimeter`, `missing_dimension_area`, and `missing_triangle_base_height`, a side/dimension is deliberately unlabelled (and for missing-length tasks, the missing edge carries an unknown marker `?` via a `cx-measlbl` with no numeric value, not its computed length). There is **no** `cx-ans`/`cx-cut` class in the student render at all — those classes exist only in the overlay (§8.8), so "no answer/solution annotation class in the student figure" is a structural invariant a parser can check by class presence.
- **The final perimeter/area is never shown.** No total is annotated on the student figure.
- **Given == answer is NOT leakage.** As in the angle family's whitelist, a given dimension that happens to equal a derived value is legitimate given data; the leakage rule targets *dedicated derived/answer annotations* (the `cx-ans`/`cx-cut` classes and the computed total), not raw given data. The blocking checks are `only-given-dimensions-shown` (the multiset of numeric `cx-measlbl` equals `ShapeModel.givenDimensions`) and `no-answer-in-student-figure` (no `cx-ans`/`cx-cut` element; no element carries the computed missing-side value or the perimeter/area total).

### 8.8 Answer-key overlay variant (key/solution channels ONLY)

A separate render `canonicalMensSvgOverlay(ShapeModel)` produces the answer-key figure. It is **byte-identical to the student figure for its entire leading byte range** and then appends one additive overlay group, and it is emitted to a distinct `media[]` asset id (`fig-1-key`) used ONLY by the answer-key and solutions exporters — never in the worksheet/student channel.

| Overlay addition | Class | When |
| --- | --- | --- |
| The missing side, labelled with its derived value | `cx-ans` | `perimeter_composite`, `area_composite`, `missing_length_perimeter`, `missing_dimension_area`, `missing_triangle_base_height` |
| The computed perimeter or area total | `cx-ans` (placed in a clear margin) | all tasks |
| Decomposition cut lines (the stated decomposition) | `cx-cut` (dashed) | composite tasks `perimeter_composite`, `area_composite` |
| Per-sub-rectangle / per-triangle area annotations | `cx-ans` | `area_composite`, `area_triangle` |

The overlay reuses the same label-collision engine so overlay annotations do not collide with the student dimensions they sit beside. Because the overlay group is strictly appended after the complete student element list, the student and key SVGs share the underlying geometry **byte-for-byte as a prefix** — proven by `overlay-is-strict-suffix-of-student-geometry` (§8.11), which asserts the student SVG bytes are an exact prefix of the key SVG bytes (so a divergent overlay renderer can never silently alter student geometry). The review pack exploits this by showing **student diagram BESIDE answer-key overlay** (§14). `no-answer-in-student-figure` is asserted on the student asset; the inverse `overlay-shows-answer` asserts the key asset DOES carry the `cx-ans` total — so the two channels can never be swapped.

### 8.9 Modes, print, and the 6000×4200 export

All four modes (`premium` / `premium-dark` / `accessible` / `print`) are produced via the mensuration-theme `presentationSvg()`; the monochrome `print` mode is the colour-free authoritative rendering and is what the `svg-realises-data` byte parity asserts against (greyscale-authoritative, consistent with the platform canonical-SVG discipline). The materialised self-contained **6000×4200 (S=6)** export reuses the additive theme's `exportSvg(svg, mode, 6000, 4200)` (both rulesets baked inside the clone, `--cx-bg`-filled raster background via `modeBackground`). The same `media[].svg` bytes print correctly on a monochrome laser printer; no inline `fill`/`stroke` colour (all via classes), pure vector (no `<image>`), no `<script>`/animation/`<foreignObject>`, two-column-print safe.

### 8.10 To-scale fidelity and deterministic regeneration

Because the layout is an exact integer scaling of integer/rational vertices, the figure is genuinely to-scale and `toScale:true`. `to-scale-faithful` asserts: each drawn edge length (in viewBox units, recovered from the parsed integer coordinates) is proportional to its true dimension within the single `gridRound` half-unit, with one global scale factor; and the rendered aspect of each rectangle equals its true aspect within that bound. The `proportion-quality` guard (§8.1) is the *generation-time* gate that triggers deterministic seeded redraw for visually poor proportions; `to-scale-faithful` is the *validation-time* proof that the shipped figure is faithful. (The rare exhausted-redraw fallback to `toScale:false` + banner is recorded but is not expected to occur for the v1.0.0 rectilinear scope.)

### 8.11 Blocking SVG / render validators (named `checks[]`)

Every render invariant is an independent, named entry in `lifecycle.validation.checks[]`; any `fail` ⇒ `validation.status = fail`, the item never reaches `machine-validated`, and it is excluded from the offline export. These render-check names are part of the single canonical `checks[]` vocabulary fixed in §9 and referenced verbatim by §12 and §14 (no alternative spellings appear anywhere). The mensuration render checks (additive to the family's geometry/answer checks):

| Check | Asserts |
| --- | --- |
| `svg-realises-data` (byte parity) | `oracle.canonicalMensSvg(buildShapeModel(params)) == ts.canonicalMensSvg(...)` byte-for-byte, and equals stored `media[].svg`; the figure is the deterministic output for `params`, so it can encode nothing else |
| `only-given-dimensions-shown` | the multiset of numeric `cx-measlbl` equals `ShapeModel.givenDimensions[]`; no derived dimension is drawn |
| `no-answer-in-student-figure` | the student asset contains no `cx-ans`/`cx-cut` element and no element carries the missing-side value or the perimeter/area total |
| `overlay-shows-answer` | the answer-key asset DOES carry the derived missing side + total (`cx-ans`) and the stated decomposition (`cx-cut`) |
| `overlay-is-strict-suffix-of-student-geometry` | the student SVG bytes are an exact prefix of the answer-key SVG bytes (the overlay is strictly appended; student geometry is never altered between channels) |
| `dimension-line-distinct-from-edge` | no `cx-dim` segment is coincident with a `cx-edge`; every `cx-dim` has two arrowheads and sits at a tier multiple of `OFFSET` off its edge |
| `right-angle-marker-present` | one right-angle marker at each rectangle corner / triangle altitude foot |
| `perp-height-marker-present` | every triangle figure has exactly one axis-aligned altitude with a foot right-angle square meeting the base at 90° (height is perpendicular, never a sloping side) |
| `label-no-collision` | every `cx-measlbl` integer box clears all edges, leaders, markers, and other label boxes by ≥ 8 units; leaders do not cross |
| `side-attribution-unambiguous` | each `cx-measlbl` maps to exactly one edge via its anchor/leader midpoint |
| `to-scale-faithful` | parsed edge lengths are proportional to true dimensions under one global scale within the `gridRound` bound; `toScale:true` |
| `readable-in-monochrome/print` | all semantic distinctions are shape/weight encoded (no colour/opacity-only indicator); the `print`-mode greyscale render carries every dimension, marker, and label (deterministic emitter-choice check; a rendered greyscale preview ships in the review pack for human print inspection, non-blocking) |
| `theme-completeness` | each of the nine new `--cx-*` variables resolves to a concrete value in every one of the four modes; no mensuration variable name collides with a cartesian/data-chart variable |
| `svg-canonical-form` | fixed root element + `<title>`/`<desc>` children, fixed element/attribute order, single-space separation, class-only styling, restricted label charset, no `<script>`/external URL, no per-element `aria`/`role` (single `role="img"` root) |

These render checks feed the **reachability-derived review-pack COVERAGE-MATRIX machinery** (reused exactly from stats v1.0.2): the matrix's diagram-flag columns (rectangles in different orientations, several L-shape configurations, composites with missing exterior lengths, triangle areas with visible perpendicular heights, label-collision stress cases, monochrome + two-column print, premium + accessible modes, a 6000×4200 export, and explicit **answer-absent-from-student-diagram** cells) are required cells DERIVED from the distribution report, keyed by the §1.3 task slugs; the pack builder FAILS on any missing reachable diagram cell, and the student-beside-overlay pairing is rendered per selected item.


---

## 9. Solver and independent-validator design

This family follows the platform's **oracle-first, two-route** discipline: an independent Python `spi_oracle` solver is authored and frozen before the TypeScript mirror, and a *separate* independent validator recomputes everything from `params` and asserts the stored item byte-for-byte. The solver and the validator share **no code path** except the exact primitives (`core/exact-math/rational.ts` / `fractions.Fraction`, `core/seeded-random/mulberry32.ts`, `gridRound`); the validator is forbidden from importing the generator's answer/SVG builders so that closure-agreement is a genuine cross-check, not a tautology.

The data structure all of this consumes is the **canonical shape model** (§6: an orthogonal, closed, non-self-intersecting `Polygon` of integer/rational vertices, plus a declared `decomposition` for composites and an explicit `(base, height)` pair for triangles) and the **dimensional-quantity answer contract** (§4). Per §4.3 (authoritative encoding) the stored answer is

```
answer = {
  type: "quantity",                  // the single owner-gated new answerType enum member (§4, §16.3)
  canonical: { num, den },           // a BARE reduced Rational — unchanged from exact-rational, byte-identical serialization
  unit: { dimension: "length"|"area", baseUnit: "mm"|"cm"|"m", exponent: 1|2, display },  // structured sibling
  display,                           // canonical formatter output, e.g. "24 cm" / "15 cm^2" (ASCII "^2", never "²")
  accepts: { fraction, decimal, mixed, requireUnit }
}
```

The numeric value lives in `answer.canonical = {num,den}` (preserving the exact-rational canonical contract and all existing rational/parity/serialization paths byte-for-byte); the unit is the **separate structured sibling** `answer.unit`, NOT folded into `canonical`. The solver returns a `Quantity = (value: Rational, dimension, baseUnit, exponent, display)`; the validator re-derives a `Quantity` and asserts structural equality of the **value** (as a reduced `Rational`) plus the **unit triple** `(dimension, exponent, baseUnit)` — it does not compare a merged canonical object, because none exists.

> **Token note.** The single new `answerType` enum member is `"quantity"` throughout this family (§2 `answerTypes`, §3.2 matrix, the checks below, the §10 adapters' `Quantity` shape, §14 coverage tokens, §16.3 headline). No section uses `"measure"`.

### 9.1 Task vocabulary (single source)

Every check, adapter, and review-pack record keys off the eight canonical task slugs defined once in `core/curriculum/mensuration-objective-ids.ts` (`MENSURATION_TASKS`, §1.3) and mirrored verbatim in the Python oracle. Those eight slugs — used **verbatim** below and in `RULES_BY_TASK` (§10.3) — are:

```
perimeter_rectangle, perimeter_composite, area_rectangle, area_triangle,
area_composite, missing_length_perimeter, missing_dimension_area, missing_triangle_base_height
```

`FREE_RESPONSE_ONLY_TASKS = { perimeter_composite, area_composite, missing_length_perimeter, missing_dimension_area, missing_triangle_base_height }` (cf. stats `FREE_RESPONSE_ONLY_TASKS`); the MC-eligible tasks are exactly `perimeter_rectangle`, `area_rectangle`, and `area_triangle` (§9.5, §10.3). A bespoke `mensuration-graph.test.ts` asserts `keys(OBJECTIVE_BY_TASK) == keys(RULES_BY_TASK) == MENSURATION_TASKS` and that **no alternative slug spelling appears anywhere** in the family.

### 9.2 Solver (`spi_oracle/mensuration.py`, mirrored in `domains/measurement/mensuration.ts`)

`solve(task, params) -> Quantity`. All arithmetic is exact `Rational`; `exponent` and `dimension` are set by the task, never inferred from a string. There are no irrationals (no surds, no Pythagoras, no π) by construction, so every answer is an exact integer or reduced rational in the item's single declared `baseUnit`.

| Task slug | Closed-form solver rule (exact) | `dimension` / `exponent` |
|---|---|---|
| `perimeter_rectangle` | `P = 2*(w + h)` | length / 1 |
| `perimeter_composite` | `P = sum(|e|)` over the complete EXTERIOR boundary edges of the polygon (axis-aligned, so each `|e|` is a coordinate difference) | length / 1 |
| `area_rectangle` | `A = w*h` | area / 2 |
| `area_triangle` | `A = (b*h)/2` on the EXPLICIT perpendicular base/height pair | area / 2 |
| `area_composite` | `A = sum(A_k)` over the stated non-overlapping rectangular parts; `A_k = w_k*h_k` (or subtractive `A = A_bound - sum(A_hole_k)` when the decomposition is declared subtractive) | area / 2 |
| `missing_length_perimeter` | solve `2*(w+h)=P` or `sum(|e|)=P` for the one free edge (one linear unknown, exact) | length / 1 |
| `missing_dimension_area` | `w = A/h` (or `h = A/w`); construction guarantees exact division (§7) | length / 1 |
| `missing_triangle_base_height` | `b = 2A/h` (or `h = 2A/b`); construction guarantees `2A` divisible (§7) | length / 1 |

The solver also emits the **worked `solution.steps[]`** (each `{number, transformation, intermediateResult}`) and the **misconception context** `ctx` (§10) so distractors are recomputed from the same intermediate values. The final step's `intermediateResult` is the canonical `display`, satisfying the SDK `answerSolutionAgrees` predicate. `solution.steps[]` may also surface the unit-dimension and uses-sloping-side pitfalls (§10.2) as teacher-facing notes, never as numeric distractors.

For tasks `missing_length_perimeter`, `missing_dimension_area`, `missing_triangle_base_height` the unknown is found by `core/exact-math/linexpr.ts` (a single linear equation with one rational unknown); the solver asserts the solution is exact before returning, otherwise the seed is rejected by the **deterministic redraw loop** (call-order preserving) — degeneracy never silently produces an approximate answer (§12).

### 9.3 Independent validator (`validate(item) -> {status, validatorVersion, checks[]}`)

The validator emits an ordered `checks[]` array of `{name, result, detail}`, status `pass` iff every check passes — identical in shape and naming style to the approved `gen.stats.data-handling` validator (`closure-agreement`, `svg-realises-data`, `chart-realises-data`, role-based leakage). It composes the domain-independent SDK predicates in `core/sdk/checks.ts` (`exactlyOneCorrectByDisplay`, `wrongOptionsUniqueByDisplay`, `answerSolutionAgrees`, `provenanceComplete`, …) and adds the mensuration-specific checks below. Functional parity (status + check list) is asserted Py↔TS; the result is not serialized, so it need not be byte-identical, but the SVG and item it validates **are** byte-identical across languages.

**Canonical check-name vocabulary.** The names in the tables below are the **single fixed `checks[]` vocabulary** for this family; §8 (render), §12 (degeneracy), §13 (a11y), and §14 (review pack) reference these exact strings verbatim — no alternative spellings (e.g. `polygon-closed`, `area-shoelace`, `missing-side-determined`) appear anywhere. A spec-internal test asserts the documented name set equals the emitted set.

**A. Universal checks (every task)**

| Check name | Assertion |
|---|---|
| `objective-mapping` | `item.objectiveIds == [OBJECTIVE_BY_TASK[task]]` — the single-source map in `core/curriculum/mensuration-objective-ids.ts` (cf. `stats-objective-ids.ts`), cross-checked by `mensuration-graph.test.ts` (cf. `stats-graph.test.ts`). |
| `interaction-type` | `free-response` or `multiple-choice` only (`interactionTypeValid`); `multiple-choice` only when `task ∈ {perimeter_rectangle, area_rectangle, area_triangle}` (§9.5). |
| `shape-model-wellformed` | polygon is **closed**, **non-self-intersecting**, **orthogonal** (every edge axis-aligned), components **non-overlapping**, and **exactly reconstructible** from vertices + given dimensions (§9.4). |
| `closure-agreement` | re-solve via the independent route; the rebuilt `Quantity` from `params` equals the stored answer structurally — **value** as a reduced `Rational` equals `answer.canonical` `{num,den}`, AND the **unit triple** `(dimension, exponent, baseUnit)` equals `answer.unit`. (No merged canonical object is compared, per §4.3.) |
| `quantity-unit-contract` | `answer.unit.dimension`/`exponent` are the pair required by the task (length→1, area→2); `answer.unit.baseUnit ∈ {mm,cm,m}`; **one** `baseUnit` is used throughout the item (no cross-unit conversion, §4); `answer.unit.display` and `answer.display` are the canonical formatter output for `(value, baseUnit, exponent)` (§5) — byte-for-byte. |
| `quantity-dimension-exponent-lock` | **independently enforces the `answer.unit` invariant** `dimension=="length" ⇔ exponent==1` and `dimension=="area" ⇔ exponent==2`, and `type=="quantity" ⇒ answer.unit present`. This is the validator/Ajv-side guarantee of the §4 `if/then` conditional. **It is NOT enforced by `oracle/check_conformance.py`** (see note below), so this check is the offline pipeline's sole structural guard for the lock. |
| `quantity-display-is-ascii` | `answer.display` and `answer.unit.display` and every distractor/option `display` use **ASCII `^2`** for area, never the Unicode `²` (U+00B2). Guarantees byte-stable golden/parity fixtures across locales/encodings. (Unicode `²` is accepted on *input* by §5 but never *stored*.) |
| `no-legacy-units-string` | the legacy free-string `answer.units` (plural) is **absent**; the structured `answer.unit` (singular) object is the only unit carrier. Flags the singular/plural footgun: an author must never populate both. |
| `answer-type-consistency` | `answer.type == "quantity"` (the owner-gated new `answerType` enum member, §4.4) and `answer` carries the structured `unit` object; `answer.canonical` validates as a normalized rational `{num, den≥1}` (integer when `den==1`). |
| `answer-solution-agrees` | final `solution.steps[]` result == `answer.display` (`answerSolutionAgrees`). |
| `difficulty-in-band` | `overallBand ∈ TASK_BANDS[task]`; axes are the CLOSED schema enum only (`difficulty-axes-valid`); band recomputed from weighted axes via `bandFromScore` (§11). |
| `provenance` / `version-fields` | `provenanceComplete`, `versionFieldsPresent`. |

> **Offline conformance caveat (corrects the §4.4/§5.5 claim).** `oracle/check_conformance.py` evaluates only `required, type, enum, pattern, properties, additionalProperties(bool), items, minItems, $ref` — it has **no support for `allOf`/`if`/`then`/`const`**. Therefore the §4.4 schema diff's conditional obligations — `type:"quantity" ⇒ required:["unit"]` and the `dimension`⇔`exponent` lock — are **silently NOT enforced** by the offline conformance subset (exactly as the pre-existing `integer`/`exact-rational` `allOf` conditionals are unenforced there today; this is a known, accepted limitation, not a new gap). The correct statement is: `check_conformance.py` **accepts (does not reject)** a `quantity` answer, verifying only enum membership of `type`, `required:[type,canonical]`, and `additionalProperties:false`; the conditional invariants are enforced (a) by the **bundled Ajv** gate in production and (b) by the independent validator's `quantity-unit-contract` + `quantity-dimension-exponent-lock` checks above. Optionally, extending `check_conformance.py` with minimal `allOf`/`if`/`then`/`const` support is listed as **owner-gated** shared-tooling work (it would also retroactively enforce the existing integer/exact-rational conditionals); the proposal does not assume it.

**B. SVG checks (every diagrammed task)**

| Check name | Assertion |
|---|---|
| `svg-realises-data` | recompute the **canonical greyscale SVG** from `params` via the shared renderer (viewBox `0 0 1000 700`, integer coords via `gridRound`, no runtime trig, root attrs exactly `role="img"` + `<title>`/`<desc>` per the shipped canonical-SVG discipline of `coordinate-lines.ts`/`data-handling.ts`) and assert `== media[0].svg` **byte-for-byte**, Py↔TS identical. |
| `figure-realises-shape` | every drawn shape edge maps to a polygon edge and every dimension label's value equals the corresponding given edge length / base / height (the second-route geometry agrees with `params`). |
| `to-scale-when-required` | when §8 declares a to-scale figure, the rendered pixel lengths are proportional to the exact edge lengths under the chosen rational scale (deterministic regeneration if proportions are visually poor). |
| `dimension-rendering-contract` | dimension lines are visually distinct from shape edges; extension lines, axis-aligned arrowheads, right-angle and perpendicular-height markers present where the contract requires; **no label collision** (label boxes disjoint from each other, from edges, and from leaders — §8 stress test); each label unambiguously attached to one side. All dimension lines (base and altitude) are **axis-aligned**, so all arrowheads use the axis-aligned integer template — no runtime trig (§8.4). |
| `interior-primitives-presentation-only` | every interior primitive (dimension/extension `<line>`, arrowhead `<polygon>`, right-angle/perp markers, measurement-label `<text>`) is presentation-only under the **single** `role="img"` root — none carries its own `role`/`aria-*`, so axe-core sees one labelled image, not many unlabelled graphics nodes (§13). |
| `theme-extension-intact` | the figure uses the **mensuration theme**, which `extends "spi-math-cartesian-theme/1"` and *follows the `data-chart-theme` ADDITIVE pattern* (same mechanism) but does **not** depend on `data-chart-theme`; `presentationSvg` composes cartesian + mensuration rulesets only. Coordinate-lines and stats outputs remain byte-for-byte unchanged (regression-guarded). |

**C. Role-based answer-leakage checks (every task)**

Leakage is judged **semantically by role/intent**, exactly per the canonical-SVG discipline: raw *given* data that happens to equal the answer is **not** leakage; a dedicated answer/solution annotation in the *student* figure **is**.

| Check name | Assertion |
|---|---|
| `no-missing-side-revealed` | for `perimeter_composite`, `missing_length_perimeter`, `missing_triangle_base_height` the student figure shows **only given** dimensions; the missing side is absent (no label, leader, or marker carries its value as a *dimension annotation*). A coincidental equal *given* edge elsewhere is allowed. |
| `no-result-annotation-in-student` | no perimeter/area total appears as an answer/solution annotation in the student render (the computed `Quantity.display` is not printed on the student figure). For inverse tasks the **stated** perimeter/area is given data and may appear (role = given); only the **asked** missing quantity must be absent. |
| `student-a11y-omits-result` | accessibility `spokenMath`/`longDescription` and the media-level `dataTableFallback` for the *student* item state given dimensions only, never the computed answer (§13). |
| `fallback-no-answer-leak` | **role/intent based**, consistent with §14.5: `media[].dataTableFallback` encodes the asked-quantity and given-quantity as **distinct typed slots** (`given[]` vs `asked`); the check asserts no slot whose ROLE is the computed *result* is populated with the answer. A *given* slot that numerically coincides with the answer **passes** (no value-equality false positive). |
| `answer-key-overlay-is-keyed` | the answer-key/solution overlay (where the result IS shown) is a separate render variant, never the student `media`. |
| `overlay-is-strict-suffix-of-student` | the answer-key overlay SVG's leading bytes are **byte-identical** to the entire student SVG up to its final closing element; the overlay adds only *strictly additive trailing elements* (§8.8). Guarantees a divergent overlay renderer can never silently alter student geometry. |

**D. Composite-shape checks (`perimeter_composite` and `area_composite`)** — the owner-mandated independent battery

| Check name | Assertion |
|---|---|
| `polygon-closure` | vertex chain returns to the start; consecutive edges share endpoints; edge count even (orthogonal closed polygon). |
| `side-orientation` | edges strictly alternate horizontal/vertical; no zero-length edge; turn at every vertex is ±90°. |
| `missing-side-derivation` | each unlabelled exterior side is forced by the closure constraints `Σ(horizontal signed edges)=0` and `Σ(vertical signed edges)=0`; the derived length is unique and exact (proves the **one mathematically determined answer**). |
| `perimeter-from-exterior-boundary` | `P = Σ|e|` over the **complete exterior** boundary equals the solver's perimeter (for `perimeter_composite`). |
| `area-by-polygon` | the **shoelace formula** on the exact integer/rational vertices, `A = ½·|Σ(x_i·y_{i+1} − x_{i+1}·y_i)|`, computed in exact `Rational`. |
| `area-by-stated-decomposition` | sum of the stated rectangular parts (additive or subtractive, §6) in exact `Rational`. |
| `area-methods-agree` | `area-by-polygon == area-by-stated-decomposition == answer.canonical` value (three-way exact agreement; this is the core composite-area guarantee). |
| `decomposition-non-overlapping` | declared parts tile the interior without overlap or gap (areas sum, and pairwise interiors are disjoint over the rational grid). |

**E. MC distractor discipline (multiple-choice items)** — owner rule N + the mensuration unit rule

| Check name | Assertion |
|---|---|
| `mc-one-correct` | exactly one option flagged correct and it matches `answer.display` (`exactlyOneCorrectByDisplay`). |
| `mc-options-distinct` | all four option values distinct (`wrongOptionsUniqueByDisplay`); no distractor equals the correct `Quantity`. |
| `mc-every-option-correct-unit` | **every** option carries the CORRECT `(dimension, exponent, baseUnit)`; an obviously-wrong-unit foil is forbidden (the rule of §10). The three distractors differ from the answer only in **value**. |
| `mc-distractors-recompute` | each stored distractor is re-derived by running the *same* `MISC.MENS.*` adapter on the recomputed `ctx` (the validator independently reproduces every wrong value); `rationale` is true for the dataset. |
| `mc-min-three-distractors` | ≥3 distinct misconception-backed value distractors exist; if the eligible adapters yield fewer than three distinct, in-range, value-misconception distractors, the item is rejected by the **deterministic redraw loop** — never padded with a unit foil. |

The required-cell space the review pack must cover is **derived from the distribution report** by the approved reachability-driven **COVERAGE-MATRIX** machinery (stats v1.0.2), reused by name in §14: required cells = every task × supported interaction × reachable difficulty band × realised answer shape (length vs area, integer vs rational, mm/cm/m). The validator's `difficulty-in-band` plus the distribution report prove every declared band is reachable.

### 9.4 Reconstruction route (second-route geometry)

`shape-model-wellformed` and `figure-realises-shape` rebuild the polygon from `params` independently of the generator: vertices from the orthogonal edge walk, missing sides from the closure constraints, then assert the rebuilt polygon is congruent to the stored shape and that the stored SVG renders *that* polygon. This makes `svg-realises-data` and `closure-agreement` mutually reinforcing — the figure, the prompt dimensions, the answer, and the solution all trace to one reconstructed shape.

### 9.5 MC-eligibility (constructive ≥3-distinct-value guarantee)

Only `perimeter_rectangle`, `area_rectangle`, and `area_triangle` are offered as multiple-choice (`interaction-type` enforces this); all five remaining tasks are free-response only. For each MC-eligible task §10.3 supplies a preference-ordered list of **≥3 value rules proven to yield distinct, in-range, exact `Rational` results** on every well-formed item over the §6.8 sampling ranges (verified by a small **exhaustive search** at registration time and re-asserted by the distribution sweep). The constructive third rule for the rectangle tasks is named concretely in §10.1 (`MISC.MENS.PERIM_FOUR_TIMES_ONE_SIDE`, `MISC.MENS.ONE_DIMENSION_SQUARED`), so the ≥3-distinct guarantee is not assertional. If for a given seed fewer than three distinct in-range value distractors survive, the **deterministic redraw loop** rejects the seed (preserving call order) rather than introducing a unit foil.

---

## 10. Misconception and distractor registry

The registry is `MISC.MENS.*`, authored as a byte-parity pair (`oracle/spi_oracle/mensuration_misconceptions.py` + `domains/measurement/mensuration-misconceptions.ts`), mirroring the approved `MISC.STAT.*` structure exactly. **This registry is the single source of truth** for wrong answers across the solver (distractor synthesis + solution pitfalls), the free-response checker (targeted unit feedback), and the independent validator (recomputation); every other section (§3.1, §6, §7, §14) references these ids **verbatim**, and `mensuration-graph.test.ts` asserts no alternative spelling appears anywhere. Each rule is `{ id, title, formula, description, observableError, feedback, adapter, applicability }`:

- **`formula`** — the wrong rule, in words (internal).
- **`description`** — internal note.
- **`observableError`** — what a marker sees, **no internal symbols**.
- **`feedback`** — phrased from displayed values, **no internal symbols**.
- **`adapter(ctx) -> Quantity | null`** — deterministic; returns a **distinct wrong dimensional-quantity** (with its own `dimension`/`exponent`, since dimension-confusion misconceptions deliberately change the unit) or `null` when inapplicable.
- **`applicability(ctx) -> bool`** — eligibility predicate; combined with `RULES_BY_TASK` (preference-ordered) exactly as in the stats registry.

The shared `ctx` exposes the solver's exact intermediates so adapters never re-derive geometry:

```
ctx = { correct: Quantity, baseUnit, dimension, exponent,
        w?, h?,                        // rectangle / rectangle-form inverse tasks
        b?, height?,                   // triangle base + PERPENDICULAR height (both exact, axis-aligned)
        exteriorEdges: Rational[],     // composite exterior boundary
        indentEdges: Rational[],       // inward steps of a composite
        internalDecompEdges: Rational[], // declared decomposition cut lines
        parts: {w,h}[],                // additive composite pieces
        subtractedPart?: {w,h}, otherPart?: {w,h} }  // subtractive composite
```

`ctx` deliberately carries **no `slopingSide`**: the sloping edge of an axis-aligned-base / perpendicular-height triangle has length `sqrt(b²+h²)`, which is irrational for almost all integer/rational `(b,h)` and is therefore unrepresentable as a reduced `Rational` and forbidden by the no-surds / no-Pythagoras rule (§6.1, §12). The "uses a sloping side instead of the perpendicular height" pitfall is consequently **free-response only** (§10.2), never a numeric distractor. `Q(value, dim, exp)` builds a `Quantity` in the item's `baseUnit`; for a wrong-dimension misconception the adapter sets `exp`/`dim` to the wrong pair.

### 10.1 Value misconceptions (eligible as MC distractors)

| Id | Title / formula | observableError (marker-facing) | applicability | adapter → wrong `Quantity` |
|---|---|---|---|---|
| `MISC.MENS.ADDS_TWO_SIDES_RECT` | Adds only two sides of a rectangle · `w+h` | Adds one length and one width instead of going round all four sides. | `perimeter_rectangle`; `missing_length_perimeter` (rectangle form) | `Q(w+h, length, 1)` |
| `MISC.MENS.PERIM_FOUR_TIMES_ONE_SIDE` | Treats every side as equal · `4·s` (s = the deterministically chosen longer side, ties → width) | Multiplies one side by four as if the shape were a square. | `perimeter_rectangle` when `w≠h` | `Q(4*s, length, 1)` |
| `MISC.MENS.AREA_WHEN_PERIMETER` | Multiplies when perimeter is wanted · `w*h` | Works out the space inside instead of the distance around. | **rectangle** perimeter only: `perimeter_rectangle`, `missing_length_perimeter` (rectangle form). FR-feedback-only on composites (no single `w,h`). | `Q(w*h, length, 1)` — **kept as a length unit** so the foil is a value error, not a unit error |
| `MISC.MENS.PERIMETER_WHEN_AREA` | Adds round when area is wanted · `2(w+h)` | Works out the distance around instead of the space inside. | area tasks `area_rectangle`, `area_triangle`, `area_composite`, `missing_dimension_area` | `Q(2*(w+h), area, 2)` |
| `MISC.MENS.ADDS_INSTEAD_OF_MULT_AREA` | Adds dimensions for area · `w+h` | Adds the two side lengths instead of multiplying them. | `area_rectangle`, `missing_dimension_area` | `Q(w+h, area, 2)` |
| `MISC.MENS.ONE_DIMENSION_SQUARED` | Squares one side instead of multiplying the two · `s²` (s = the deterministically chosen longer side, ties → width) | Squares a single side instead of multiplying length by width. | `area_rectangle` when `w≠h` | `Q(s*s, area, 2)` |
| `MISC.MENS.FORGETS_TO_HALVE_TRIANGLE` | Forgets to halve · `b*h` | Uses base times height but forgets to take half. | `area_triangle`, `missing_triangle_base_height` | `Q(b*height, area, 2)` |
| `MISC.MENS.OMITS_INDENTED_EDGE` | Omits an indented edge from a composite perimeter · `P − indent` | Misses an inward step when going round the shape. | `perimeter_composite`, `missing_length_perimeter` (composite) with ≥1 indent edge | `Q(P − Σ indentEdges, length, 1)` |
| `MISC.MENS.DOUBLE_COUNTS_INTERNAL_EDGE` | Double-counts an internal decomposition edge · `P + cut` / `A + overlap` | Counts a cut line as part of the outside. | `perimeter_composite`, `area_composite` with an internal decomposition cut | `Q(P + Σ internalDecompEdges, length, 1)` (perimeter) / `Q(A_parts_with_overlap, area, 2)` (area) |
| `MISC.MENS.SUBTRACTS_WRONG_RECT` | Subtracts the wrong rectangle · `A_bound − A_otherPart` | Takes away the wrong piece of the shape. | subtractive `area_composite` | `Q(A_bound − A_otherPart, area, 2)` |

All adapters return `null` (rule skipped) when the result would equal `correct`, be out of range, or the applicability predicate fails. `MISC.MENS.AREA_WHEN_PERIMETER` is intentionally emitted **with the correct length unit** and `MISC.MENS.PERIMETER_WHEN_AREA` **with the correct area unit** for the asked task, so they are genuine *value* misconceptions satisfying `mc-every-option-correct-unit`.

**Constructive third-distractor proof (T1/T3 MC).** For `perimeter_rectangle` the three value rules are `ADDS_TWO_SIDES_RECT` (`w+h`), `PERIM_FOUR_TIMES_ONE_SIDE` (`4·s`), and `AREA_WHEN_PERIMETER` (`w*h`); the correct value is `2(w+h)`. For all in-range `w≠h` these four values are pairwise distinct: `2(w+h)≠w+h` (since `w+h>0`), `4s` lies strictly between `2(w+h)` and `w+h` only when… — concretely, with `s=max(w,h)`, `4s = 2(w+h)` iff `2s = w+h` iff `w=h` (excluded), and `4s = w+h` is impossible for positive sides, and `w*h = 2(w+h)` / `w*h = 4s` / `w*h = w+h` each have only the boundary integer solutions that the §6.8 ranges and the redraw guard exclude. For `area_rectangle` the three rules are `ADDS_INSTEAD_OF_MULT_AREA` (`w+h`), `ONE_DIMENSION_SQUARED` (`s²`), and `PERIMETER_WHEN_AREA` (`2(w+h)`); the correct value is `w*h`. With `s=max(w,h)`, `s² = w*h` iff `w=h` (excluded), and `w+h`, `2(w+h)`, `s²`, `w*h` are pairwise distinct away from the small coincidence set the redraw guard rejects. A **registration-time exhaustive search** over the §6.8 `(w,h)` ranges confirms ≥3 distinct in-range value distractors survive for every sampled pair (so the redraw guard is never forced to abandon MC); the distribution sweep re-asserts it.

`area_triangle` MC draws `FORGETS_TO_HALVE_TRIANGLE` (`b*h`), `PERIMETER_WHEN_AREA` (`2(w+h)` with the triangle's bounding box, defined in `ctx`), and `ADDS_INSTEAD_OF_MULT_AREA`/`ONE_DIMENSION_SQUARED` on `(b,height)` as the third; the same exhaustive search confirms ≥3 distinct values, else the seed redraws.

### 10.2 Unit-dimension and method pitfalls (free-response feedback only)

These never appear as MC distractors (an MC item gives every option the correct unit, §9 E). Their `adapter` returns `null` for distractor purposes; they surface as **targeted free-response feedback** (matched against a student's submitted `Quantity`) and as **worked-solution pitfalls**.

| Id | Title / formula | observableError | Triggered when the student answer has… |
|---|---|---|---|
| `MISC.MENS.LINEAR_UNITS_FOR_AREA` | Gives linear units for area · right number, exponent 1 | Right amount but the unit is a length, not a squared length. | correct `value`, `dimension=length`/`exponent=1` on an area task |
| `MISC.MENS.SQUARE_UNITS_FOR_PERIMETER` | Gives square units for perimeter · right number, exponent 2 | Right amount but the unit is squared when it should be a length. | correct `value`, `dimension=area`/`exponent=2` on a perimeter task |
| `MISC.MENS.RIGHT_NUMBER_NO_UNIT` | Right number, no unit · bare number | The number is correct but no unit is given. | correct `value`, missing `dimension`/`baseUnit` |
| `MISC.MENS.USES_SLOPING_SIDE` | Uses a sloping side, not the perpendicular height (pitfall, **no exact numeric value**) | Uses the slanted edge instead of the upright height. | `area_triangle` — surfaced as a hint/solution pitfall only; `adapter` always returns `null` (the slope length is irrational, §10 preamble) |

This rule set is exactly the brief's **twelve** misconceptions (nine value rules in §10.1 — counting `PERIM_FOUR_TIMES_ONE_SIDE`/`ONE_DIMENSION_SQUARED` as the constructive realisations of the rectangle "double" placeholders — plus the three unit-dimension rules here; `USES_SLOPING_SIDE` is the brief's "uses a sloping side" item recast as an FR-only pitfall because it cannot yield an exact `Rational`).

The §5 **equivalence checker** drives the three unit-dimension rules: it accepts mathematically-equivalent numerical forms *with the correct unit*, distinguishes length from area, rejects a correct number with the wrong dimension, rejects cm when cm² is required (and vice-versa), and routes each rejection to the matching `MISC.MENS.*` feedback above — treating the unit **structurally**, never as an unchecked text suffix.

### 10.3 Task → eligible-misconception map (`RULES_BY_TASK`)

Keyed on the canonical §1.3 slugs. Preference-ordered; the MC builder draws the first three distinct, in-range, correct-unit **value** distractors. Unit-dimension / sloping-side rules are present for free-response feedback/pitfalls only (marked ‡, never drawn for MC). Only `perimeter_rectangle`, `area_rectangle`, `area_triangle` are MC-eligible; the other five tasks list value rules for FR pitfalls and never build options.

```
perimeter_rectangle           : ADDS_TWO_SIDES_RECT, PERIM_FOUR_TIMES_ONE_SIDE, AREA_WHEN_PERIMETER,
                                 [SQUARE_UNITS_FOR_PERIMETER‡, RIGHT_NUMBER_NO_UNIT‡]
perimeter_composite           : OMITS_INDENTED_EDGE, DOUBLE_COUNTS_INTERNAL_EDGE,
                                 [SQUARE_UNITS_FOR_PERIMETER‡, RIGHT_NUMBER_NO_UNIT‡]   (FR-only task)
area_rectangle                : ADDS_INSTEAD_OF_MULT_AREA, ONE_DIMENSION_SQUARED, PERIMETER_WHEN_AREA,
                                 [LINEAR_UNITS_FOR_AREA‡, RIGHT_NUMBER_NO_UNIT‡]
area_triangle                 : FORGETS_TO_HALVE_TRIANGLE, PERIMETER_WHEN_AREA, ADDS_INSTEAD_OF_MULT_AREA,
                                 [USES_SLOPING_SIDE‡, LINEAR_UNITS_FOR_AREA‡, RIGHT_NUMBER_NO_UNIT‡]
area_composite                : SUBTRACTS_WRONG_RECT, DOUBLE_COUNTS_INTERNAL_EDGE, PERIMETER_WHEN_AREA,
                                 [LINEAR_UNITS_FOR_AREA‡, RIGHT_NUMBER_NO_UNIT‡]        (FR-only task)
missing_length_perimeter      : ADDS_TWO_SIDES_RECT, OMITS_INDENTED_EDGE, AREA_WHEN_PERIMETER,
                                 [RIGHT_NUMBER_NO_UNIT‡]                                (FR-only task)
missing_dimension_area        : ADDS_INSTEAD_OF_MULT_AREA, PERIMETER_WHEN_AREA,
                                 [RIGHT_NUMBER_NO_UNIT‡]                                (FR-only task)
missing_triangle_base_height  : FORGETS_TO_HALVE_TRIANGLE, PERIMETER_WHEN_AREA,
                                 [USES_SLOPING_SIDE‡, RIGHT_NUMBER_NO_UNIT‡]            (FR-only task)
```

For each **MC-eligible** task the preference list is constructed to contain **≥3 value rules that yield distinct results on a well-formed item** (proven by the §10.1 exhaustive search). If, for a given seed, fewer than three distinct in-range value-distractors survive, the **deterministic redraw loop** rejects the seed (preserving call order) rather than introducing a unit foil — the same guarantee the stats family makes for thin distractor pools. `mensuration-graph.test.ts` asserts `keys(RULES_BY_TASK) == MENSURATION_TASKS` and that every referenced id exists in the registry (no dangling / alternative spellings).

### 10.4 Distractor invariants enforced by the independent validator

For every MC item the validator independently re-runs each rule's `adapter` on the recomputed `ctx` (`mc-distractors-recompute`) and asserts:

1. **Distinct from correct** — no distractor `Quantity` equals the canonical answer (value *and* unit).
2. **Pairwise distinct** — all distractor values distinct (`mc-options-distinct`).
3. **Correct unit on every option** — `mc-every-option-correct-unit`; the three distractors differ from the answer only in **value**, never in unit (the unit-dimension rules are excluded from MC by construction).
4. **Rationale truthful** — each `distractors[].rationale` states the wrong rule in terms of displayed dimensions and is true for the dataset.
5. **Reproduced, not copied** — the validator's recomputed distractor set equals the stored set (same independent route as `closure-agreement`).

This keeps the registry the single source of truth for wrong answers across the solver (distractor synthesis + solution pitfalls), the free-response checker (targeted unit feedback), and the independent validator (recomputation), with full Python↔TypeScript byte parity on the underlying exact values.


---

## 11. Difficulty model

### 11.1 Mechanism reused, not reinvented

Mensuration difficulty uses the platform difficulty pipeline verbatim. Every generated item computes a vector of **schema closed-enum axes** (`question-item.schema.json#/$defs/difficultyProfile.axes`, a CLOSED 16-member set with `additionalProperties:false`), forms a weighted score in `[0,1]`, and derives `overallBand` through the shared `bandFromScore` in `core/difficulty/band.ts`:

```
score = clamp01( Σ w_axis · axis_value )      # weights sum to 1; scaffolding enters as (1 − scaffolding)
overallBand = bandFromScore(score) = min(5, 1 + floor(clamp01(score) · 5))   # 0–0.2→1 … 0.8–1→5
```

The family **does not define its own band function** and does not invent axes (per `DIFFICULTY_MODEL.md` §2–3 and the schema's `additionalProperties:false`). `round3` (`core/difficulty/band.ts`, round-half-up to 3 dp, int-when-whole) is applied wherever an axis or score is serialized so the integer-collapsing parity contract holds. The Python `spi_oracle/difficulty.py` mirror and the TS `band.ts` produce byte-identical scores (oracle-first; golden + parity fixtures guard it).

### 11.2 Axes actually used by this family

Mensuration is a numeric-procedural family; it deliberately exercises a **subset** of the sixteen axes. Axes outside this subset are emitted as `0` (and several are structurally pinned to `0`, see §11.5) so the vector is fully reproducible. All six driver names and all zeroed names below are confirmed members of the closed `difficultyProfile.axes` enum (no invented axis name appears).

| Axis | Driver in this family |
| --- | --- |
| `numericalComplexity` | Magnitude/type of dimensions: single- vs double-digit integers; whether the answer is an exact reduced **rational** (triangle areas, missing-side divisions) vs an integer; number of dimension values to combine. |
| `reasoningSteps` | 1 step (rectangle area/perimeter) → 2 steps (two-sided multiply-then-double; missing length by inverse) → 3+ steps (composite by decomposition: derive missing exterior side, split, sum/subtract parts). |
| `informationDensity` | Count of given dimension labels the student must track (a rectangle = 2; an L-shape composite = 5–7 labelled edges plus the missing-side derivation). |
| `representation` | Reading quantities off a **dimensioned diagram** with dimension lines/extension lines/perpendicular-height markers vs a bare numeric pair; composites raise this because the boundary must be parsed. |
| `interpretationDemand` | Selecting the correct **dimension** for the answer (length vs area) and the correct operation for the asked quantity; "missing-dimension-from-given-area/perimeter" tasks raise it because the student must invert the relationship. |
| `scaffolding` | Inverse axis `(1 − scaffolding)`: presence of an explicitly shown perpendicular-height marker, a stated decomposition hint, or all exterior sides labelled **lowers** difficulty; requiring a missing side to be inferred **raises** it. |

**Pinned-to-zero axes (v1.0.0).** `readingDemand` is `0`: prompts are terse and templated with **no worded context** in v1.0.0 (consistent with §2, which permits `verbal-context` in `allowedRepresentations` but states the v1.0.0 generator does not exercise it). `algebraicComplexity`, `abstraction`, `familiarity`, `irrelevantInformation`, `requiredConnections`, `exactVsApproximate`, `calculatorDependence`, `proofDemand`, and `modellingDemand` are **not** drivers in v1.0.0 and are emitted as `0`. (`calculatorDependence` = 0 reflects the calculator-not-required policy of these objectives; `exactVsApproximate` = 0 reflects exact-only arithmetic — no approximations exist in this family.) The complete pinned-zero set is therefore: `algebraicComplexity, abstraction, familiarity, readingDemand, irrelevantInformation, requiredConnections, exactVsApproximate, calculatorDependence, proofDemand, modellingDemand` — exactly the ten axes not listed as drivers above.

### 11.3 Provisional weights and per-task band mapping

Weights below are **provisional**, pending the 10k distribution report (§14 reachability machinery), and are versioned in `core/difficulty`. They keep `numericalComplexity` intentionally non-dominant (per `DIFFICULTY_MODEL.md` §2), letting structural demand (steps, density, missing-side inference) carry the band. The **weighted axis set is exactly the six driver axes of §11.2** (no driver appears in §11.2 that is absent here, and vice versa — §11.5 asserts this list equality):

| Axis | Provisional weight |
| --- | --- |
| `reasoningSteps` | 0.30 |
| `informationDensity` | 0.20 |
| `interpretationDemand` | 0.18 |
| `representation` | 0.14 |
| `numericalComplexity` | 0.10 |
| `(1 − scaffolding)` | 0.08 |

Weights sum to `1.00`. Indicative landing bands (final ranges fixed by the report); tasks are named by the **canonical §1.3 `MENSURATION_TASKS` slugs** so the band table keys to the same single source as the generator dispatch, `OBJECTIVE_BY_TASK`, and the §14 COVERAGE-MATRIX `cell:<task>:…` tokens:

| Task slug (§1.3) | Typical structural profile | Indicative band |
| --- | --- | --- |
| `perimeter_rectangle` | 1–2 steps, density low | 1–2 |
| `area_rectangle` | 1 step, density low | 1–2 |
| `area_triangle` | 2 steps incl. halving (rational answers ↑) | 2–3 |
| `perimeter_composite` (L-shape) | missing-side derivation, high density | 2–4 |
| `area_composite` | split/sum or subtract, agreement check | 3–4 |
| `missing_length_perimeter` | inverse, interpretation ↑ | 2–3 |
| `missing_dimension_area` | inverse division (rational ↑) | 2–3 |
| `missing_triangle_base_height` | inverse with halving, interpretation ↑ | 3–4 |

### 11.4 Clamping to objective ranges and reachability

Each objective declares `difficultyRange{min,max}` (1..5). The computed band is **clamped to the owning objective's declared range** before it is written to `overallBand`. The family commits to the platform invariant that **every declared band in every objective's range is reachable**: the **`SPI_SWEEP=10000` distribution report** must show ≥ 1 generated item per (task × declared band) cell, and the **reachability-derived COVERAGE-MATRIX machinery (stats v1.0.2)** is reused exactly to assert it — required cells = every task × supported interaction × **reachable difficulty band** × realised answer shape, derived from the distribution report; the review-pack builder FAILS on any missing reachable cell. Realised answer shapes for the matrix are the **`quantity`** answer.type with an integer or reduced-rational numeric value, split into `integer` / `rational` and `length` / `area` shape tokens (the single new answer.type token is `quantity`, per §4/§16.3). A blocking `mensuration-band-reachability` test (mirroring the stats coverage tests) fails CI if any declared band is empty after the sweep. Provisional weights/ranges that leave a declared band unreachable are corrected (or the range narrowed) before approval — never papered over. (This same gate flags any `…:rational:…` cell that has no items, so the rectangle/triangle rational-answer reachability resolution in §6 is verified here, not asserted.)

### 11.5 Monotonicity and parity guards

A property test (mirroring `DIFFICULTY_MODEL.md` §3) asserts the band is **monotonic in the obvious controls**: enlarging dimensions, adding composite components, switching a task to its inverse (missing-side) form, or moving from integer to rational answers must not *lower* the band. Two parity guards lock the axis vector:

- **Documented-subset equality.** A test asserts the **emitted axis set is exactly the documented subset for each task** — that is, the six weighted driver axes of §11.3 carry the computed values and the ten pinned-zero axes of §11.2 are serialized as `0`, with no other axis present and none of the sixteen omitted. Because the driver list (§11.2/§11.3) and the pinned-zero list (§11.2) together enumerate all sixteen schema axes exactly once, Python and TS cannot silently diverge on which axes fire or serialize.
- **round3 serialization parity.** All axis values and the score pass through `round3`, preserving the int-when-whole serialization parity used by the golden/parity fixtures (a `0`-valued axis serializes as the integer `0`, byte-identically in both engines).

## 12. Edge cases and degeneracy rules

All rules below are enforced **inside the seeded backward-construction loop** (§7): a candidate that violates any rule is **rejected and the seed deterministically redraws** (same redraw discipline as the misconception-distractor loop), so a violating item is *never emitted* and *never drawn*. Every exclusion is **deterministically unreachable from the task loop**, not filtered after the fact and not silently substituted. The independent validator (§9) re-checks each rule as a named gate using the **single canonical `checks[]` name vocabulary defined in §9.2** (referenced verbatim below — no alternative spellings), so a degenerate item cannot pass even if construction were wrong.

### 12.1 Degenerate geometry (rejected → redraw)

| Condition | Rule | Named check (§9.2 vocabulary) |
| --- | --- | --- |
| Zero or negative dimension | Every given/derived length ≥ 1 (exact, in the declared base unit) | `dim-positive` |
| Zero/negative or non-finite area or perimeter | Result is a positive exact integer or reduced rational | `result-positive-exact` |
| Degenerate triangle | base > 0 **and** perpendicular height > 0; the shown height is strictly interior/perpendicular, never coincident with a sloping side | `triangle-nondegenerate` |
| Degenerate rectangle | both sides ≥ 1; squares allowed but flagged in params so orientation/label tests still apply | `rect-nondegenerate` |

### 12.2 Composite well-formedness (rejected → redraw)

Composites must be **closed, non-self-intersecting, orthogonal, overlap-free, and exactly reconstructible from vertices + dimensions with exactly one determined answer** (owner brief). The construction asserts, and the validator independently re-asserts, using the canonical §9.2 check names (these replace the historical §12 spellings; the validator emits this single fixed `checks[]` vocabulary, byte-stable across Python/TS and consumed by the review pack):

| Property | Named check (§9.2 vocabulary) |
| --- | --- |
| Polygon closure (vertex chain returns to origin) | `polygon-closure` |
| All edges axis-aligned (orthogonal) | `side-orientation` |
| Non-self-intersecting boundary | `boundary-simple` |
| No overlapping decomposition components; components tile the interior exactly | `decomposition-non-overlapping` |
| Missing exterior side is **uniquely** determined by the labelled sides (sum of horizontals on one side = sum on the other; same for verticals) | `missing-side-derivation` |
| Perimeter from the **complete exterior boundary** | `perimeter-from-exterior-boundary` |
| Area by **shoelace** on integer/rational vertices = area by the **stated decomposition** | `area-by-polygon`, `area-by-stated-decomposition`, `area-methods-agree` |

If the missing side is **not uniquely determined** (ambiguous missing-side case), `missing-side-derivation` fails: the candidate is rejected and redraws — ambiguous composites are unreachable.

### 12.3 Exactness guarantees (rejected → redraw)

- **Triangle halving** (`area_triangle`, `missing_triangle_base_height`): `base × height` must be **even** (integer answer) or the construction must yield an **exact reduced rational** via `core/exact-math/rational.ts`; a non-exact halving is rejected. The `missing_triangle_base_height` task is constructed **backward from an exact target** so the inverse answer is guaranteed exact; if no exact inverse exists for the drawn seed, it redraws.
- **Missing rectangle dimension from area** (`missing_dimension_area`): the division `area ÷ givenSide` must be an exact integer or reduced rational; otherwise reject.
- **No sloping-side length is ever computed.** The triangle's only slant edge (the hypotenuse) carries no dimension line and is never measured; its length is `sqrt(base² + height²)`, irrational for almost all integer/rational base–height pairs, and would violate the no-surds rule. The "uses a sloping side instead of the perpendicular height" pitfall is therefore handled **as free-response feedback only** (no numeric value path; the §10 adapter returns `null` for distractor purposes), so no irrational ever enters the model from this route.
- No irrational ever arises anywhere: no surds, no π, no Pythagoras (areas/perimeters are exact integers or reduced rationals). This is a structural consequence of §12.4 exclusions, not a post-hoc filter.

### 12.4 Deferred topics — deterministically excluded

Each deferred topic is **structurally absent from the generator's task enum (`MENSURATION_TASKS`, §1.3) and shape vocabulary**, so the seeded loop *cannot* construct it. A named **exclusion test** asserts unreachability for each, and the construction asserts the negative invariant where applicable (e.g. no curved edge primitive exists in the polygon model; no second base unit is introduced within an item):

| Deferred topic | How it is made unreachable | Exclusion test |
| --- | --- | --- |
| Circles + π | No circular/arc primitive in the canonical shape model; no irrational constant exists in exact-math | `excl-no-circle` |
| Volume + surface area | Shape model is strictly 2-D polygons; no 3-D task in the enum | `excl-no-3d` |
| General triangle perimeter | Triangle tasks are area-only; no triangle-perimeter task in the enum (no validated exact sloping-side construction in v1.0.0) | `excl-no-tri-perimeter` |
| Trapezia + non-rectilinear composites | Composites are orthogonal-only (`side-orientation`); no non-axis-aligned edge can be constructed | `excl-orthogonal-only` |
| Pythagoras + surds | No hypotenuse/diagonal/sloping-side computation path; exact-math rejects irrationals | `excl-no-surds` |
| Unit conversion | **Exactly one declared base unit per item, throughout** (§4 contract); the loop never mixes units | `excl-single-unit` |
| Scale drawings | No scale-factor parameter exists; figures are to-scale or deterministically regenerated, never scaled-representation tasks | `excl-no-scale` |
| Compound units | The unit model permits only `length` (exp 1) and `area` (exp 2); no compound dimension representable | `excl-no-compound` |
| Approximate measurements | All values exact integer/rational; `exactVsApproximate` pinned 0; no rounding step exists | `excl-no-approx` |
| Irregular/curved boundaries | Only straight axis-aligned edges in the polygon model | `excl-no-curves` |

### 12.5 Visual degeneracy (poor proportions)

Per the owner brief, the renderer **prefers mathematically to-scale figures** using rational/integer coordinates. When a drawn seed would produce visually poor proportions (extreme aspect ratio, or a label-collision that the dimension-rendering contract §8 cannot resolve), the seed **deterministically regenerates** within the same parity-preserving loop rather than emitting a degraded figure. The threshold (e.g. aspect-ratio bound) is a versioned construction parameter; the regeneration is part of the deterministic call order, so Python/TS SVG parity is preserved.

## 13. Accessibility model

### 13.1 Contract and fields

Every mensuration item populates the item-level `accessibility{ spokenMath, altText, longDescription, nonColorIndicators }` object (`question-item.schema.json#/$defs` item `accessibility`, which is `additionalProperties:false` with **exactly those four fields**). **The data-table fallback is NOT an item-level accessibility field** — the schema forbids it there (`additionalProperties:false`). It lives only on the figure asset: each `media[]` entry carries `media[].altText`, `media[].longDescription`, and **`media[].dataTableFallback` (type `object`, per `mediaAsset`)** — the information-equivalent of the diagram. Every section that references the fallback keys it as `media[].dataTableFallback` (§13.2, §13.5, and the §9 validator), never `accessibility.dataTableFallback`.

The figure root follows the **shipped canonical-SVG discipline verbatim** (as emitted by `coordinate-lines.ts`, `data-handling.ts`, and `angles.ts`): the root `<svg>` carries `role="img"` and `aria-label="<alt>"` (NOT `aria-labelledby`; no `id="fig-title"/"fig-desc"` attributes are introduced — adding them would diverge byte-for-byte from every approved family), with `<title>{esc(title)}</title>` and `<desc>{esc(desc)}</desc>` as the first children. **All interior primitives** — dimension lines, extension lines, arrowheads, edges, right-angle markers, perpendicular-height markers, and measurement-label glyphs — are **presentation-only under the single labelled `role="img"` root** (they carry no individual `role`/`aria`), so axe-core sees one labelled image rather than many unlabelled graphics nodes. `nonColorIndicators` is `true` for every item. Targets: **WCAG AA**, **axe-core 0 critical / 0 serious**, gated in CI exactly as for the approved families.

### 13.2 Data-table fallback — given dimensions only, role-keyed slots

`media[].dataTableFallback` lists **each given dimension** the figure encodes, so a non-visual user has the same input data as a sighted user. Slots are **typed by role** (given vs asked) so the no-leakage check keys on slot role, not on numeric coincidence. Field shape:

```
dataTableFallback = {
  shape: "rectangle" | "triangle" | "composite-rectilinear",
  givenDimensions: [ { label, role: "given", value: {num,den}, unit, exponent, edgeRef } , … ],
  givenQuantity: { role: "given-stated", kind: "perimeter" | "area", value: {num,den}, unit, exponent } | null,   // present ONLY for inverse tasks
  markers: [ "right-angle" | "perpendicular-height" , … ],   // present when shown in the figure
  asked: { role: "asked", quantity: "perimeter" | "area" | "missing-length" | "missing-dimension" }   // NAMES the asked quantity; never carries its value
}
```

For **computed tasks** (`perimeter_rectangle`, `area_rectangle`, `area_triangle`, `perimeter_composite`, `area_composite`) the fallback lists only **given data and what is asked** — it **never** contains the computed perimeter, area, or any derived missing side. For **inverse tasks** (`missing_length_perimeter`, `missing_dimension_area`, `missing_triangle_base_height`) the **stated** perimeter/area is given data and appears in `givenQuantity` (role `given-stated`); the *answer* (the missing length/dimension) is named only in `asked.quantity` and never carries a value. Values are exact `{num,den}` (reduced) so the table is byte-stable and parity-checked.

A named check **`fallback-no-answer-leak`** is **role/intent based** (consistent with the canonical-SVG answer-leakage rule and §14.5 "raw-data-equality-is-not-leakage"): it asserts that **no slot whose ROLE is the computed result** (an `asked`-keyed value, or any `result`/`answer`/solution-annotation entry) is present in `dataTableFallback`, `altText`, `longDescription`, or `spokenMath` of the **student** figure. A given or stated quantity that *numerically coincides* with the hidden answer (e.g. a square whose side equals a derived value) **passes**, because the check keys on slot role, not value-equality. A dedicated answer/solution annotation in the student figure would fail it.

### 13.3 spokenMath — shape + given measurements, units spoken structurally

`spokenMath` describes the **shape and its given measurements**, with **units spoken structurally** from the dimensional-`quantity` model (`dimension` + `exponent`), not as a raw text suffix:

- length (`exponent 1`) → "centimetres" / "millimetres" / "metres"; area (`exponent 2`) → "square centimetres" / "square millimetres" / "square metres" — driven by `dimension` + `exponent`, never string concatenation of a stored suffix.
- Examples (student figure): "A rectangle with width six centimetres and height four centimetres." / "A triangle with base ten centimetres and a perpendicular height of three centimetres, with the right angle marked." / "An L-shaped figure; the labelled edges are eight, five, three, and two metres."

The **student** `spokenMath` and `media[].dataTableFallback` **never state the computed perimeter or area** (and never state a derived missing side); they convey **only given data** — asserted by `fallback-no-answer-leak` and a dedicated `spokenmath-given-only` check. The **answer-key / solution** variants (used only in the answer-key and solutions exports, never in the student item) may speak the result.

**Encoding stability.** The canonical stored `display` for any unit-bearing value uses the ASCII `^2` form (e.g. `cm^2`), never the Unicode superscript `²`, even though the §5 input parser *accepts* `cm²` on input. A named check **`display-ascii-exponent`** asserts the **stored** `answer.display`, `dataTableFallback` units, and figure measurement labels contain no `²` glyph, so golden/parity fixtures are byte-stable across locales and encodings.

### 13.4 No colour-only information, across all modes

Meaning is never carried by colour alone. The family renders through the approved theme stack: `core/visual-style/cartesian-theme` (coordinate-lines v1.0.2) plus a mensuration **`mensuration-theme`** that **`extends: "spi-math-cartesian-theme/1"` directly** and **FOLLOWS the `data-chart-theme` ADDITIVE PATTERN** (the same versioned-extension mechanism) — it does **not** depend on or compose `data-chart-theme` itself (mensuration uses none of `data-chart-theme`'s chart/pictogram primitives). `presentationSvg()` composes the cartesian common ruleset plus the mensuration ruleset only. The mensuration extension adds the dimension-rendering primitives (dimension lines, extension lines, arrowheads, right-angle and perpendicular-height markers, measurement labels) and supports the four modes inherited from cartesian-theme: **premium**, **premium-dark**, **accessible** (CVD-safe), and **print** (monochrome authoritative).

**Theme-variable completeness.** Every new `--cx-*` variable the extension introduces (dimension line, extension line, arrowhead, edge, right-angle marker, perpendicular-height marker, measurement label, cut/decomposition line, answer-overlay) is given an **explicit value in all four modes**. This matters because the base cartesian `commonCss` sets a default text fill (`.cx-figure text{…fill:var(--cx-text)}`), so an unset label variable would harmlessly inherit `--cx-text`, but an unset **stroke-only** marker/extension/dimension variable has **no base fallback** and would render with the SVG default (black) only by luck — defeating the per-mode CVD-safe and premium-dark guarantees. Extension/marker strokes track `--cx-edge` or `--cx-text` per mode; **premium-dark uses light strokes** so markers are visible on the dark `--cx-bg`. A `mensuration-theme.test.ts` theme-completeness check (mirroring `data-chart-theme.test.ts`) asserts **each declared variable has a value in every mode**.

Every dimension is conveyed by an explicit textual measurement label and structural marker, so the **print/monochrome** rendering is fully information-complete and is the colour-free authoritative figure. A named check **`no-color-only`** asserts that removing colour (print mode) loses no answer-relevant or dimension-relevant information; this holds in all five render contexts in the review pack (monochrome, two-column print, premium-light, premium-dark, accessible).

### 13.5 Gates

- `nonColorIndicators === true` on every item (schema-validated).
- **axe-core** run over rendered student items: **0 critical, 0 serious**, WCAG AA — blocking, as in the approved families. Because all interior SVG primitives are presentation-only under one `role="img"`/`aria-label` root (§13.1), axe evaluates a single labelled image.
- `media[].dataTableFallback` present and non-empty for every figure; `fallback-no-answer-leak`, `spokenmath-given-only`, `display-ascii-exponent`, and `no-color-only` are **blocking** review-pack/validator checks.
- The `mensuration-theme.test.ts` theme-completeness check (every `--cx-*` variable valued in all four modes) is blocking.
- Printable **monochrome** and **two-column print** variants are produced and audited in the review pack (§14), alongside the **6000×4200 (S=6) materialised export** and the explicit **answer-absent-from-student-diagram** tests.


---

## 14. Review-pack and visual-audit plan

The mensuration review pack is **not a new artifact type** — it is a direct reuse of the **stats v1.0.2 reachability-derived COVERAGE-MATRIX machinery** (`oracle/make_review_pack_data_handling.py`, the model corrected under `DECISION_LOG.md` #48 and approved in #49). A new builder `oracle/make_review_pack_mensuration.py` instantiates the same three-stage pipeline — *reachability → required cells → greedy set-cover over task-pinned candidates* — against the mensuration distribution report and the `gen.measurement.mensuration` generator. Nothing in the coverage model is reinvented; only the family token vocabulary changes. All task slugs below are the **single canonical `MENSURATION_TASKS` set defined in §1.3** (`core/curriculum/mensuration-objective-ids.ts`) — `perimeter_rectangle`, `perimeter_composite`, `area_rectangle`, `area_triangle`, `area_composite`, `missing_length_perimeter`, `missing_dimension_area`, `missing_triangle_base_height` — used verbatim as the `cell:<task>:…` token prefix, identical to the keys of `OBJECTIVE_BY_TASK`, `RULES_BY_TASK` (§10.3), the generator dispatch, and the §15.1 scope list.

### 14.1 Required cells are DERIVED from the distribution report, never hand-set

The authoritative reachability artifact is `docs/review/mensuration_distribution.json` (the 10,000-seed sweep of §11/§9, same shape as `stats_data_handling_distribution.json`). The builder's `_reachability()` reads, per task, `{interactions, bands, answerShapes}` straight from that report; `_required_tokens()` then emits one **required cell** for:

- every **task × supported interaction** (`cell:<task>:inter:<free-response|multiple-choice>`),
- every **reachable difficulty band** (`cell:<task>:band:<1..5>`), and
- every **realised answer shape** (`cell:<task>:shape:<token>`),

exactly as stats does — but the mensuration **answer-shape token is the structured dimensional quantity**, not the bare schema `answer.type`. Every item in this family answers with the single new `answer.type = "quantity"` (the one owner-gated enum member of §4; the structured unit lives in the **separate sibling `answer.unit` object** of §4.3, never folded into `answer.canonical`, which stays the bare Rational `{num,den}`). The schema `answer.type` alone therefore cannot distinguish a length from an area or an integer from a rational. The mensuration `_cell_tokens()` composes the shape token from the **dimensional contract** (the `answer.unit` triple plus the `answer.canonical` denominator):

```
shape = "<dimension>:<exponent>:<numberKind>:<baseUnit>"
  dimension  ∈ {length, area}            # answer.unit.dimension
  exponent   ∈ {1, 2}                     # answer.unit.exponent; 1 ⇔ length, 2 ⇔ area (the §4 invariant)
  numberKind ∈ {integer, rational}        # answer.canonical.den == 1 vs den > 1
  baseUnit   ∈ {mm, cm, m}                # answer.unit.baseUnit
```

So `cell:area_rectangle:shape:area:2:rational:cm` and `cell:perimeter_rectangle:shape:length:1:integer:m` are distinct required cells. This makes the owner's "length AND area answers" and "integer AND rational answers" first-class **cells the builder can FAIL on**, not soft qualitative notes. Per §6.5/§7.2 the *rational-valued* answer shapes are only reachable on the **triangle and missing-dimension tasks** (rectangle and composite edge lengths are integer-valued, so `b×h÷2`, an exact-area missing dimension, or a rational missing length are where `den > 1` genuinely arises); the distribution report records exactly which `(task, dimension, numberKind, baseUnit)` cells exist, and the builder treats a never-realised combination (e.g. `cell:area_rectangle:shape:area:2:rational:*`) as **non-existent — documented in the matrix, not a `MISSING`** (the `note: "unreachable per distribution report (no items)"` convention). The required cell count `requiredCells` is computed as `sum(len(interactions)+len(bands)+len(shapes))` over the reachability map and asserted equal to the matrix-derived count (the `required-token-count-derived-from-matrix` assertion) — it is never a literal.

### 14.2 Greedy set-cover, task-pinned gathering, builder FAILS on any missing reachable cell

Stage 1 gathers candidates task-pinned over both supported interactions across a bounded seed window (`GATHER_SEEDS` per task per interaction), so rare reachable cells (e.g. a band-1 `area_triangle`, a `missing_triangle_base_height` whose §12 exact-answer gate fires only occasionally) always have candidates. Stage 2 is the same greedy set-cover: repeatedly pick the candidate adding the most still-uncovered **required** tokens, reusing one exemplar across several cells where it is a genuine exemplar. The builder's exit code is `0` only when `required_cells ⊆ covered` **and** every selected item is machine-valid **and** `len(required_cells) == derived_required_cells`; any missing reachable cell prints `MISSING COVERAGE` and returns non-zero.

Per §3, **multiple-choice is offered only by `perimeter_rectangle` (T1) and `area_rectangle` (T3)**; the other six tasks (composites, all three missing-quantity tasks, and `area_triangle`) are in `FREE_RESPONSE_ONLY_TASKS` and have **no** `cell:<task>:inter:multiple-choice` requirement at all. The distribution report drives this directly — a task with zero MC items yields no MC interaction in its reachability set, so its MC cell is `note: "unreachable per distribution report (no items)"`, **documented, not silently omitted**. For the two MC tasks the pack additionally proves the **three distinct misconception-backed value distractors** of §10.3 are realised (T1 from `ADDS_TWO_SIDES_RECT`, `AREA_WHEN_PERIMETER`, and the registered third rectangle-perimeter value rule of §10; T3 from `ADDS_INSTEAD_OF_MULT_AREA`, `PERIMETER_WHEN_AREA`, and the registered third rectangle-area value rule of §10), each recovered through the same adapter the validator recomputes — the redraw guard is never silently relied upon, since §10.3 proves ≥3 distinct in-range values survive across the §6.8 ranges.

### 14.3 Explicit coverage matrix + the five blocking coverage tests (reused by name)

The pack emits the same two coverage structures as stats: a per-task **`coverageMatrix`** (`interactions` / `bands` / `shapes`, each `{reachable, hasExemplar, exemplarSeed, note}`) and a flat **`coverageCells`** list of every realised `(task, interaction, band, answerShape, seed)`. The Markdown renders the matrix as the same `| Task | Interactions | Bands | Answer shapes |` table with `→seed` / `→MISSING` / `=n/a` cells.

The blocking coverage tests are the **stats v1.0.2 set, reused verbatim**, retargeted to the mensuration pack — these are the five named gates the brief requires, plus the two top-level honesty flags they assert against:

| Coverage test | Asserts |
| --- | --- |
| `every-reachable-task-band-covered` | every `cell:<task>:band:<b>` that the distribution report marks reachable has an exemplar seed. |
| `every-supported-interaction-covered` | every reachable `cell:<task>:inter:<i>` has an exemplar; the six FR-only tasks' MC interaction is matrix-documented `n/a`, not `MISSING`. |
| `every-task-answer-shape-covered` | every realised dimensional-quantity shape token (length/area × integer/rational × mm/cm/m, per the §14.1 composition) has an exemplar. |
| `coverage-summary-matches-records` | `summary.coveredCells` / `coverageCells` agree with the actual `records[]` (no double-count, no phantom cell). |
| `no-false-full-coverage-claim` | `summary.allCovered == (missingCoverage == [])` — the honest full-coverage flag can never be `true` while a required cell is missing. |

`summary.allCovered` and `summary.allValid` are the two top-level honesty flags; `requiredCells == derivedRequiredCells` (the reachability-derived count, never a literal) is asserted inside the builder's exit gate and surfaced in the summary. The manifest of §15 hash-attests the resulting pack so a silent regeneration that drops a cell fails CI.

### 14.4 Owner-mandated coverage dimensions (additional tokens beyond the cells)

On top of the systematic cells, `_required_tokens()` adds the explicit owner checklist as additional required tokens, each surfaced by `_features()` and FAIL-on-missing in the same set-cover:

| Owner dimension | Required token(s) | Source feature |
| --- | --- | --- |
| mm / cm / m contexts | `unit:mm`, `unit:cm`, `unit:m` | `dataset.baseUnit` (= `answer.unit.baseUnit`) |
| length AND area answers | `dim:length`, `dim:area` | `answer.unit.dimension` |
| integer AND rational answers | `num:integer`, `num:rational` | `answer.canonical.den` |
| rectangles in different orientations | `orient:landscape`, `orient:portrait`, `orient:square` | `width` vs `height` of the bounding rectangle |
| several L-shape configurations | `lshape:notch-tl`, `…-tr`, `…-bl`, `…-br` | notch corner of the rectilinear polygon |
| composites with missing exterior lengths | `composite:missing-exterior` | a derived (non-given) exterior edge present |
| triangle areas with visible perpendicular heights | `triangle:visible-height` | the perpendicular-height marker primitive is emitted |
| label-collision stress tests | `collision:dense-dims`, `collision:short-edge` | many dimension labels / a short edge forcing leader offset |
| monochrome + two-column print | `render:print`, `render:two-column` | the `print` mode export + the worksheet two-column layout |
| premium + accessible modes | `render:premium`, `render:accessible` | the themed audit copies |
| a 6000×4200 export | `export:6000x4200` | the materialised raster export hash |
| answer ABSENT from student diagram | `answer-free:student-figure` | the §8 student/answer-key split is exercised |
| missing-length / missing-dimension determinacy | `det:unique-answer` | the §12 exact-answer gate fired and is recorded |

The mensuration analogues of stats' endpoint honesty checks are §12's degeneracy gates (no zero/negative derived edge; missing-quantity answers exact-only), each recorded as a covered token so the pack proves the gate is **exercised**, not merely declared.

### 14.5 Student diagram BESIDE answer-key overlay, and the explicit answer-absence tests

The pack and the visual audit render, for every figure-bearing item, the **student figure beside its answer-key overlay** — the two products of the §8 single-shape model: the student `media[0].svg` (given dimensions only, no missing side, no result) and the answer-key copy (the same figure plus the derived edge, the perpendicular-height value, the decomposition split lines, and the final perimeter/area annotation). The overlay is **strictly additive trailing geometry** — the answer-key SVG's leading bytes are the student SVG's bytes; §8's `overlay-is-strict-suffix-of-student-geometry` check enforces that the overlay renderer never alters student geometry, only appends answer-role elements. This is the mensuration analogue of the coordinate-lines student/solution render split and reuses the §8 role-based answer-leakage discipline.

Two explicit, **blocking** answer-absence tests are recorded per figure item (the owner's "EXPLICIT tests proving the answer is ABSENT from student diagrams"), reusing the semantic role/intent leakage model (raw given data equal to the answer is **not** leakage; a dedicated answer/solution annotation in the student figure **is**):

- `no-result-in-student-figure` — the student SVG carries no element whose render role is the computed perimeter, area, or a missing/derived length: no dimension line on a non-given edge, no area/perimeter label, no perpendicular-height value, no decomposition annotation. A given side that coincidentally equals the answer passes (`raw-data-equality-is-not-leakage`); a dedicated answer-role annotation fails.
- `student-a11y-does-not-state-result` — the student `media[0].longDescription` and the `media[0].dataTableFallback` give the shape, the given dimensions, and the units (per §13, the fallback lives on `media[]`, never on the item-level `accessibility` object), but never the perimeter/area/missing length. The fallback encodes the **asked quantity and each given/stated quantity as distinct role-keyed slots** (§13.2), so the check is role-based: no slot whose role is the *computed result* appears in the student copy; a stated given quantity that numerically coincides with the answer passes. The result text lives only in the answer-key/solution copy.

A pinned positive/negative pair is recorded exactly as stats pins its `no-statistic-in-svg` cases: an L-shape whose given exterior edge numerically equals its (different-role) area value **passes**; a student figure carrying a perimeter label **fails**.

### 14.6 Per-item record contents

Each `records[]` entry (and its Markdown section) shows the full audit trail the owner enumerated:

- **objective** (`objectiveId`), **task**, **interaction** (`interactionType`), **answer shape + unit** (the `quantity` contract: `answer.unit.{dimension,exponent,baseUnit}` + integer/rational from `answer.canonical.den`), **seed**, **params**;
- the **canonical shape model** — the §6 polygon (ordered integer/rational vertices, edge list with given/derived flags, decomposition rectangles for composites, the triangle base+height with the perpendicular foot) — echoed verbatim as the single source the figure, prompt, answer, solution, misconceptions, a11y, and validation all derive from;
- the **prompt** (`prompt.instruction` + typed `prompt.blocks` with the figure cited via a `media-ref` block);
- the **figure** (canonical student SVG) **beside the answer-key overlay**;
- the **canonical answer** — `answer.display`, `answer.canonical = {num,den}` (the bare Rational, rationals serialised as `{num,den}`), and the sibling `answer.unit = {dimension, baseUnit, exponent, display}`;
- the **worked solution** (`solution.steps[{number,transformation,intermediateResult}]`, with the composite area shown by BOTH the shoelace route and the stated decomposition, and their agreement asserted);
- the **misconception calculations** — every eligible `MISC.MENS.*` adapter value with its `observableError`/`feedback` (displayed-value language only). For the **MC tasks (T1 `perimeter_rectangle`, T3 `area_rectangle`)** the `distractors[{value,display,misconceptionId,rationale}]` carry the three §10 rectangle value rules (each with the **correct unit**); for the **six free-response tasks** the targeted unit-dimension hints of §10.2 (`MISC.MENS.LINEAR_UNITS_FOR_AREA`, `MISC.MENS.SQUARE_UNITS_FOR_PERIMETER`, `MISC.MENS.RIGHT_NUMBER_NO_UNIT`) plus the task-eligible value-rule pitfalls. **`MISC.MENS.USES_SLOPING_SIDE` appears only as a free-response pedagogical hint, never as a numeric distractor** — its `adapter` returns `null` for distractor synthesis because a perpendicular-height triangle's slant length is `√(b²+h²)`, irrational for almost all integer/rational `(b,h)` and therefore unrepresentable as a reduced Rational under the no-surds rule (§12.4); the §10 registry ids used throughout are the canonical spellings (`ADDS_TWO_SIDES_RECT`, `AREA_WHEN_PERIMETER`, `PERIMETER_WHEN_AREA`, `ADDS_INSTEAD_OF_MULT_AREA`, `FORGETS_TO_HALVE_TRIANGLE`, `USES_SLOPING_SIDE`, `OMITS_INDENTED_EDGE`, `DOUBLE_COUNTS_INTERNAL_EDGE`, `SUBTRACTS_WRONG_RECT`, `LINEAR_UNITS_FOR_AREA`, `SQUARE_UNITS_FOR_PERIMETER`, `RIGHT_NUMBER_NO_UNIT`);
- the **accessibility** representation (`accessibility.spokenMath` + `media[].dataTableFallback` object: the vertex/edge/dimension table);
- the **difficulty axes + band** (`difficulty.axes` over the closed enum, `difficulty.overallBand`);
- the **validation checks** run — the canonical `validate()` `checks[].name` vocabulary fixed in §9.2: `polygon-closed`, `polygon-non-self-intersecting`, `edges-orthogonal`, `missing-side-derivable`, `perimeter-from-exterior-boundary`, `area-by-shoelace`, `area-by-decomposition`, `area-methods-agree`, the §4/§9 unit-contract checks (`unit-model-wellformed`, `measure-dimension-exponent-lock`, `answer-type-consistency`), the §8 dimension-rendering checks (`svg-realises-data`, `closure-agreement`, `overlay-is-strict-suffix-of-student-geometry`), and the §14.5 answer-absence checks (`no-result-in-student-figure`, `student-a11y-does-not-state-result`) — referenced by the exact same strings the validator emits, no per-section renaming;
- the **reproduction command** (`python -c "import sys;sys.path.insert(0,'oracle/spi_oracle');import mensuration as m;print(m.serialize(m.generate(<seed>, <cfg>)))"`).

### 14.7 Visual audit + browser verification

`docs/review/mensuration_visual_audit.html` reuses the stats audit harness: it renders every pack figure through the **mensuration dimension-rendering theme extension** of §8/§16 — a versioned extension that **`extends: "spi-math-cartesian-theme/1"` and FOLLOWS the `data-chart-theme` additive PATTERN** (same per-root `cx-figure` isolation, same `presentationSvg()`/`exportSvg()` contract, new `--cx-*` variables + one additive ruleset) **but does not depend on `data-chart-theme`** (its chart/pictogram primitives are not pulled in) — in all four modes: **premium**, **premium-dark**, **accessible** (CVD-safe), **print** (monochrome authoritative), via `presentationSvg()`, plus the self-contained **6000×4200** copies via `exportSvg()`. The audit includes the owner's stress galleries: **label-collision** cards (dense dimension stacks, short-edge leader offsets, adjacent-label minimum-gap), the **two-column print** worksheet layout, monochrome legibility of dimension lines vs shape edges vs extension lines, right-angle and perpendicular-height markers under greyscale, and **student-beside-answer-key** pairs. A `mensuration_browser_verification.json` records the live-Chromium re-confirmation (four modes coexist on one page with distinct computed strokes, the dimension-line/edge contrast holds, the 6000×4200 raster hash), exactly as the stats browser verification does. The audit and verification JSON are hash-attested in the manifest (§15).

---

## 15. Versioning and approval lifecycle

`gen.measurement.mensuration` follows the **identical lifecycle** the platform has run for coordinate-lines (`DECISION_LOG.md` #44) and stats (#49): oracle-first build, blocking gates, **register `pending-review` (gated)**, owner review of the pack, then approval with immutable fixtures.

### 15.1 v1.0.0 scope — the eight tasks only

v**1.0.0** ships **exactly** the eight tasks of the brief, **1:1** with the authored objectives, over the new **`mensuration`** strand in domain `measurement`, named by the single canonical §1.3 `MENSURATION_TASKS` slugs (the §15.1 list is **not** a third spelling — it is exactly these eight):

`perimeter_rectangle`, `perimeter_composite` (composite rectilinear incl. L-shapes), `area_rectangle`, `area_triangle` (explicit perpendicular base + height), `area_composite` (by decomposition), `missing_length_perimeter`, `missing_dimension_area`, `missing_triangle_base_height` (exact-answer-guaranteed only).

A `mensuration-graph.test.ts` assertion (modelled on `stats-objective-ids.ts`'s "no alternative spellings appear anywhere") enforces that `OBJECTIVE_BY_TASK`, `RULES_BY_TASK` (§10.3), the generator dispatch, the §14 `cell:<task>` tokens, and this scope list all key off the **same eight-member set**, so the §3.3 cardinality-eight dispatch is a total function over a single enum and no legacy slug (`rect_perimeter`, `perimeter_composite_rectilinear`, …) survives anywhere.

**Deferred and DETERMINISTICALLY EXCLUDED** (never silently included): circles + π; volume + surface area; general-triangle perimeter (no exact validated construction); trapezia + non-rectilinear composites; Pythagoras + surds; **unit conversion** (cm↔m is a later objective + a contract extension); scale drawings; compound units; approximate measurements; irregular/curved boundaries. Exclusion is enforced the way stats enforces it: `paramsInDomain` rejects every excluded task id and every excluded shape (non-orthogonal edges, curved boundaries, π in any quantity), the SDK registry exposes **no** task entry for them, and an integration test asserts those ids `generate`-throw and never appear in a 10,000-seed sweep. The exact-rational arithmetic rule independently bars surds/π/Pythagoras (no irrational can be produced), so circles/diagonals/slant lengths are doubly excluded — which is precisely why `USES_SLOPING_SIDE` is free-response-feedback-only (§10/§14.6).

### 15.2 Oracle-first build order

1. Author `curriculum/objectives/SPI.MIDDLE.MEAS.json` (the eight objectives, `prerequisites[]`, `commonMisconceptions[]` → `MISC.MENS.*`) against `schemas/curriculum-objective.schema.json`; `core/curriculum/graph-check.ts` enforces no-duplicate-id + no-prerequisite-cycle as the DAG; the bespoke `core/curriculum/mensuration-graph.test.ts` (modelled on `stats-graph.test.ts`) asserts the eight objectives present, **all cited prerequisites resolve to defined `objectiveId`s** (per §2, the arithmetic anchor is the verified, defined `SPI.MIDDLE.NUM.SIGNED_OPERATIONS.01`, not the undefined `ORDER_OF_OPERATIONS.01`), the single-source `OBJECTIVE_BY_TASK` map (`core/curriculum/mensuration-objective-ids.ts`), and `reviewStatus`. The objective files carry **`reviewStatus: "approved-for-implementation"`** for the gated build (curriculum-approved, generator still gated), matching the schema's documented semantics and the stats/coordinate-lines precedent — not `"proposed"`, which applies only before curriculum sign-off.
2. Write the **Python oracle** first (`oracle/spi_oracle/mensuration*`): the §6 canonical polygon/dimension model, exact `fractions.Fraction` solvers (perimeter, shoelace area, decomposition area, missing-side derivation), the canonical monochrome dimension-annotated SVG, the dimensional-quantity unit checker (`oracle/spi_oracle/quantity.py`, §16.3), and the `MISC.MENS.*` registry. Generate golden + parity fixtures from the oracle.
3. Mirror in **TypeScript** (`domains/measurement/mensuration.ts`) using `core/exact-math/rational.ts`, `core/seeded-random/mulberry32.ts`, `core/difficulty/band.ts`, the shared `core/answer-checking/quantity.ts` unit checker (§16.3), and the additive cartesian-theme-pattern dimension-rendering extension (§16). The canonical SVG and `params`/`answer`/`distractors` are **byte-identical Py↔TS**; the themed/exported copies are TypeScript-only.
4. `validate(item)` recomputes every figure and answer by a second route and runs the §9 composite validators, the §4/§9 unit-contract checks (including `measure-dimension-exponent-lock`, which **independently** enforces the `dimension⇔exponent` lock and the `type:"quantity" ⇒ unit required` binding — see §15.3, because the offline conformance subset does not), and the §8 dimension-rendering plus §14.5 answer-absence checks.

### 15.3 Gates (all blocking before any approval)

| Gate | Spec |
| --- | --- |
| Golden | frozen `oracle/golden/mensuration.golden.json`, Py-authored, TS-verified byte-identical (canonical item JSON + canonical dimensioned SVG). |
| Parity | **150 seeds × 2 interactions**, `mensuration.parity.json`; independent Python + TypeScript output **byte-identical** for canonical item JSON + canonical SVG. Theme/export copies are TS-only and excluded from parity. |
| Schema (owner-gated) | the single additive `schemas/question-item.schema.json` extension — new `answer.type` enum member **`"quantity"`** + the sibling `answer.unit` object + `answer.accepts.requireUnit` — validates under the **bundled Ajv** (which evaluates the `if/then`/`allOf` dimension⇔exponent lock and the `type:"quantity" ⇒ required:["unit"]` binding) **and** is **accepted (not rejected) by `oracle/check_conformance.py`**. NOTE: the offline conformance subset implements only `{required, type, enum, pattern, properties, additionalProperties(bool), items, minItems, $ref}` — it does **not** evaluate `allOf`/`if`/`then`/`const`, so the conditional unit-shape obligations are a **silent no-op there** (as the pre-existing integer/exact-rational `allOf` conditionals already are). The dimension/exponent lock and the required-unit binding are therefore enforced offline by the **independent validator** (`unit-model-wellformed`, `measure-dimension-exponent-lock`, `answer-type-consistency`, §4.2/§9.2) and in production by Ajv — never claimed to be enforced by conformance.py. The extension is back-compatible: no existing `answer.type` changes, so every approved family's items stay schema-valid byte-for-byte. |
| Sweep | `SPI_SWEEP = 10000`: `invalid: 0`; **every declared band reachable before fixtures freeze** (the distribution report is the reachability proof); **for the two MC tasks (T1/T3)** ≥3 distinct in-range misconception value distractors under exact-Rational comparison (the three registered §10 rectangle rules, proven distinct across §6.8 ranges; else deterministic redraw); the §12 exact-answer / non-degeneracy gates fire (no zero/negative derived edge, missing-quantity answers exact only); **reproducibility re-check** (re-running a seed reproduces byte-for-byte). |
| Distribution | `mensuration_distribution.json` emitted + integrity-checked; it is the authoritative reachability artifact the §14 coverage matrix derives from. |
| Composite-validity | §9 polygon closure / non-self-intersection / orthogonality / missing-side derivation / exterior-boundary perimeter / shoelace area / decomposition area / **both-area-methods-agree** all pass on every swept composite. |
| Style-isolation | the per-root `cx-figure` isolation + materialised-export tests pass on the additive dimension-rendering extension; a theme-completeness test (mirroring `data-chart-theme.test.ts`) asserts **every** declared `--cx-*` variable has a value in **all four** modes; **coordinate-lines and stats output stay byte-for-byte unchanged**. |
| a11y | axe gate over rendered items: **0 critical / 0 serious, WCAG AA**; all interior dimension/extension/arrowhead/marker primitives are presentation-only under the **single `role="img"` root** (so axe sees one labelled image, not many unlabelled graphics nodes); `media[].dataTableFallback` + non-colour indicators (greyscale-authoritative dimension lines, right-angle markers) present. |
| Exports | worksheet / answer-key / solutions + offline KaTeX render; **bank-json round-trip lossless**; **6000×4200** colour + print exports self-contained. |
| Integrity + graph | the blocking artifact-integrity tests (manifest + **SHA-256** over every artefact, Py + TS) and the bespoke graph test pass. |
| Coverage | the §14 builder returns `0` (all reachable cells covered, `allCovered: true`, `requiredCells == derivedRequiredCells`) and the **five named coverage tests** of §14.3 pass. |
| Approved-generator regression | arithmetic / geometric / linear / angle-geometry / coordinate-lines / stats output **byte-for-byte UNCHANGED**. |

### 15.4 Registration, approval, immutability

The family registers in `core/sdk/sequence-registry.ts` as a new `GENERATORS[]` entry with an **explicit** `approvalStatus: "pending-review"` during the build. Per `generatorsForMode`/`approvedGenerators`, a `pending-review` family is exposed **only in review mode** and **excluded from `approvedGenerators()`**, so it is gated out of normal Studio and out of production exports/samples (`build-samples.mjs` carries **zero** mensuration records, asserted by the harness approval-lifecycle test) until the owner's review-pack decision. The objective files sit at `reviewStatus: "approved-for-implementation"` during the build (§15.2).

On the **implemented review-pack decision**:

- **APPROVE** → the registry entry flips to `approvalStatus: "approved"` with a `DECISION_LOG` reference (date + decision number); the eight objective files move to `reviewStatus: "approved"`; `build-samples.mjs` emits all eight tasks into `bank.json`; the reviewed representative items are recorded as **approved golden exemplars** (`APPROVED_VERSIONS.md`); and the **golden + parity + canonical-SVG fixtures, review pack (.md/.json) + coverage matrix, visual audit, distribution report, browser verification, generation manifest, and the 6000×4200 export hashes become immutable** — hash-attested by `docs/review/mensuration_manifest.json` and the blocking artifact-integrity tests. A tag `approved-mensuration-v1.0.0` is cut. Any future change ships as a **new version** (v1.0.1+); the approved version is preserved in history (tags), unregistered and unselectable, exactly as v1.0.0/v1.0.1 of coordinate-lines and stats are preserved.
- **REVISE** → a corrected version (v1.0.1) with the prior version preserved unchanged at its tag, only the family's artefacts regenerated (the stats #46/#47 precedent).
- **REJECT** → routes to a revised version; the rejected version is never registered.

Registry approval **does not auto-approve future items**: newly generated items always begin `lifecycle.state = "generated"` → **`machine-validated`**, and there is no auto-publication. The 10,000-seed stability run is the standing cross-version regression guard.

---

## 16. Reusable infrastructure versus mensuration-specific code

The family is built to **maximise reuse** of the approved infrastructure (cited by name) and add only the genuinely mensuration-specific pieces. Nothing in the shared column is reinvented; the dimension-rendering theme **extends `cartesian-theme/1` and follows the `data-chart-theme` additive PATTERN**, it does not depend on or build atop `data-chart-theme`.

### 16.1 Shared — reused as-is, by name

| Shared asset | Source | Reuse in mensuration |
| --- | --- | --- |
| Canonical-SVG discipline (hand-rolled, `viewBox 0 0 1000 700`, integer coords via `gridRound` over exact `Rational`/`Fraction`, no runtime trig, byte-identical Py↔TS, `role="img"` + `aria-label="<alt>"` with `<title>`/`<desc>` first children — the **shipped** coordinate-lines/stats serializer shape, NOT `aria-labelledby` — data-table fallback, greyscale-authoritative, role-based answer-leakage) | coordinate-lines / stats renderer contract | The polygon + dimension-line figures; the validator recomputes the SVG from `params` byte-for-byte (`svg-realises-data`) and recomputes the answer by a second route (`closure-agreement`); answer-leakage is the §14.5 semantic role/intent check; the answer-key overlay is a strict byte-suffix of the student SVG. |
| Per-root style isolation + render modes + export (`cx-figure`, one common ruleset, premium / premium-dark / accessible / print, `presentationSvg()`/`exportSvg()`, materialised **6000×4200** S=6 export) | `core/visual-style/cartesian-theme.{json,ts}` | Every figure + the visual audit. **TypeScript-only** (no Python theme mirror); byte-parity is required of the canonical SVG + params/answer/distractors, not the themed/export copies. |
| **Additive-extension PATTERN** (REUSE the base contract, ADD family primitives as new `--cx-*` variables + one additive ruleset, base output stays byte-for-byte unchanged) | `core/visual-style/data-chart-theme.{json,ts}` | The mensuration dimension-rendering primitives are added **the same additive way** as data-chart-theme adds its chart primitives (see §16.2) — but the mensuration extension itself `extends "spi-math-cartesian-theme/1"`, exactly as data-chart-theme does, and does **not** depend on data-chart-theme; coordinate-lines + stats figures stay byte-for-byte unchanged. |
| Exact arithmetic | `core/exact-math/rational.ts` + Python `fractions.Fraction` | All perimeters/areas/missing lengths as exact integers or reduced `{num,den}`; `answer.canonical` is the bare Rational; every distractor-vs-key and distinctness comparison is reduced-Rational equality. |
| Seeded RNG (byte-identical Py/TS, deterministic redraw order) | `core/seeded-random/mulberry32.ts` + `oracle/spi_oracle/seeded_random.py` | Deterministic shape draw + deterministic MC redraw (T1/T3 only); the call **order** is the parity contract. |
| Difficulty banding | `core/difficulty/band.ts` (`bandFromScore`, `round3`) | Weighted closed-enum axes → band, clamped to each objective's declared range; reachability proven by the distribution report. |
| Misconception engine | `MISC.<PREFIX>.*` registry shape (Py + byte-parity TS), `RULES_BY_TASK` eligibility, adapter `(ctx) -> wrong value | null`, validator independently recomputes each distractor | The `MISC.MENS.*` registry (§10) plugs into this engine unchanged; the validator re-derives every distractor through the same adapter; the adapter returns `null` where a rule is FR-feedback-only (the three unit-dimension rules; and `USES_SLOPING_SIDE`, whose value would be irrational). |
| **Review-pack reachability COVERAGE-MATRIX machinery** + the five blocking coverage tests | `oracle/make_review_pack_data_handling.py` (stats v1.0.2, `DECISION_LOG.md` #48) | Reused verbatim (§14): required cells derived from the distribution report, greedy set-cover, builder FAILS on any missing reachable cell, explicit matrix + flat cells + honest `allCovered`. |
| Manifest / artifact-integrity / style-isolation tooling | `oracle/make_*_manifest.py` (SHA-256 over every artefact, Py + TS integrity tests), `*-style-isolation.test.ts` | `oracle/make_mensuration_manifest.py` is a direct adaptation; SHA-256 over golden/parity/distribution/review-pack/audit/browser-verification/objectives/oracle/misconceptions/theme + raster export hashes. |
| Offline conformance subset | `oracle/check_conformance.py` | Live mensuration items added to the §4f-style loop and asserted to **conform** (enum membership of `"quantity"`, `required`, `additionalProperties:false`). The subset does **not** evaluate `if/then/allOf`, so the unit-shape invariants are enforced by Ajv + the independent validator, not here (§15.3) — stated plainly, never overclaimed. |
| Delivery harness | review-pack/audit generators, offline HTML/JSON exporters (worksheet / answer-key / solutions, offline KaTeX), bank-json round-trip, axe gate, SDK registry + `approvalStatus` lifecycle | Driven family-specifically; mechanism unchanged. |

### 16.2 Mensuration-specific — new, this family only

| New asset | What it is |
| --- | --- |
| **Canonical polygon / dimension data model** (§6) | The single source per item: ordered integer/rational vertices, an edge list with `given`/`derived` flags and orientation, decomposition rectangles for composites, the triangle base + perpendicular height with the foot point, the per-edge dimension-label placement (side, offset, leader). Everything — figure, labels, prompt, answer, solution, misconception calcs, a11y, validation — derives from it. |
| **Dimensional-quantity answer contract + unit checker** (§4/§5) | The `answer.type = "quantity"` shape: `answer.canonical = {num,den}` (the exact Rational, unchanged from the exact-rational contract) plus a **separate sibling** `answer.unit = {dimension: length\|area, baseUnit: mm\|cm\|m, exponent: 1\|2, display}` and `answer.accepts.requireUnit`. The structural equivalence checker accepts equivalent numeric forms with the correct unit; distinguishes length from area; rejects a right number with the wrong dimension; rejects cm where cm² is required; gives targeted missing/incorrect-unit feedback; unit meaning is structural, never an unchecked text suffix. **This is the headline new contract — see §16.3.** |
| **Dimension-rendering theme extension** (§8) | A versioned extension that **`extends "spi-math-cartesian-theme/1"`** and follows the `data-chart-theme` additive pattern, adding mensuration primitives as new `--cx-*` variables (dimension line, extension line, arrowhead, edge, right-angle, perpendicular-height, measurement label, cut/decomposition line, answer-overlay) + one additive `.cx-figure`-scoped ruleset — distinct from shape edges, with collision-avoiding label placement, **each variable defined in all four modes** (theme-completeness test). All dimension lines (base and altitude) are axis-aligned, so every arrowhead uses the axis-aligned integer template and no runtime trig is needed; the only slant edge (a triangle hypotenuse) carries no dimension line. The id-free inline-geometry discipline (no `<pattern>`/`url(#)`) and byte-identical Py↔TS canonical fragment are reused; **coordinate-lines + stats output stay byte-for-byte unchanged.** |
| **Composite-shape validators** (§9) | The family-specific checks under the §9.2 canonical name table: `polygon-closed`, `polygon-non-self-intersecting`, `edges-orthogonal`, `missing-side-derivable`, `perimeter-from-exterior-boundary`, `area-by-shoelace` (over integer/rational vertices), `area-by-decomposition` (the stated split), and `area-methods-agree` (shoelace ≡ decomposition) — plus the §12 degeneracy gates (no zero/negative derived edge; missing-quantity answer exact only). |
| **`MISC.MENS.*` registry** (§10) | The twelve owner-mandated rules, each `{misconceptionId, domain:"measurement", description, observableError, feedback, formula, adapter, applicability}` + `RULES_BY_TASK`, byte-parity Py/TS, in the canonical §10 spellings: `ADDS_TWO_SIDES_RECT`, `AREA_WHEN_PERIMETER`, `PERIMETER_WHEN_AREA`, `ADDS_INSTEAD_OF_MULT_AREA`, `FORGETS_TO_HALVE_TRIANGLE`, `USES_SLOPING_SIDE` (FR-hint only; adapter returns `null` for distractor synthesis), `OMITS_INDENTED_EDGE`, `DOUBLE_COUNTS_INTERNAL_EDGE`, `SUBTRACTS_WRONG_RECT`, plus a registered third rectangle-perimeter value rule and third rectangle-area value rule so T1/T3 reach ≥3 distinct MC value distractors, and the three unit-dimension rules `LINEAR_UNITS_FOR_AREA`, `SQUARE_UNITS_FOR_PERIMETER`, `RIGHT_NUMBER_NO_UNIT` (surfaced as free-response feedback / targeted hints, since MC options normally all carry the correct unit). The registry is the **sole** id source, asserted by the graph test ("no alternative spellings appear anywhere"). |
| **Curriculum objectives + strand** | The eight `SPI.MIDDLE.MEAS.*` objective files and the new `mensuration` strand; the single-source `OBJECTIVE_BY_TASK` map keyed by the §1.3 `MENSURATION_TASKS` slugs. |
| **The review pack + audit content** | `oracle/make_review_pack_mensuration.py`, the visual audit, distribution report, browser verification, and manifest of §14 — including the dimensional-quantity shape tokens, the student-beside-answer-key galleries, the label-collision stress cards, and the answer-absence tests. |

### 16.3 The headline decision — where the unit / dimensional-quantity contract lives

**Decision: the dimensional-quantity answer contract and its unit checker are built in SHARED CORE, not family-local** — namely `core/answer-checking/quantity.ts` (+ the Python mirror `oracle/spi_oracle/quantity.py`) and the structured `quantity` value shape — with mensuration as their **first consumer**.

Rationale:

- The contract is a **measurement-domain primitive**, not a mensuration accident. Every future Measurement family (unit conversion, mass/capacity/time, compound units, rate) will answer in dimensioned quantities, and the cm↔m conversion the brief explicitly defers is a **later objective that extends this same contract** — placing it in shared core means that extension is a versioned widening of one checker, not a second parallel implementation.
- It matches the established platform pattern: exact-rational checking, the Mulberry32 stream, and the difficulty banding all live in shared core and are reused by every family; the unit checker belongs in the same tier.
- The v1.0.0 surface is kept deliberately narrow to avoid premature generality: the shared module exposes only what mensuration needs — `dimension ∈ {length, area}`, `exponent ∈ {1, 2}`, `baseUnit ∈ {mm, cm, m}`, exact-rational value, structural equivalence within **one** declared base unit (**no cross-unit conversion in v1.0.0**). The conversion graph, additional dimensions (mass/time/capacity), and compound units are **out of v1.0.0 scope and deferred**, added later as a backward-compatible widening of the shared contract.

**Schema impact — OWNER-GATED.** `schemas/question-item.schema.json` has **no unit / dimensional-quantity answer type today**: `answer.type` lacks a `quantity` member, and `answer.accepts` allows only `{fraction, decimal, mixed}` booleans. Realising this contract requires a single additive, owner-gated extension:

1. **add `"quantity"`** as a new member of `$defs/answerType.enum` (appended after the existing tail token so the byte-position of every current member is unchanged);
2. **add a new sibling `answer.unit` object** `{dimension, baseUnit, exponent, display}` to `answer.properties` (mandatory because `answer` is `additionalProperties:false`) — the structured unit is a **separate field, NOT folded into `answer.canonical`**, which stays the bare Rational `{num,den}` so every existing rational/parity/serialization path is byte-identical;
3. **add `requireUnit`** to `answer.accepts.properties` (also `additionalProperties:false`, so the add is mandatory);
4. an `if/then` (under `allOf`) binding `type:"quantity"` → `required:["unit"]`, and the `dimension⇔exponent` lock (`length⇔1`, `area⇔2`).

The new structured `answer.unit` (singular) sits beside the **pre-existing legacy `answer.units` string** (plural); the near-collision is flagged explicitly — mensuration items populate `answer.unit` and **never** `answer.units`, enforced by a `no-legacy-units-string` validator check. The whole `answer.type` token is named **`"quantity"`** consistently across §2 (`answerTypes:["quantity"]`), §3.2, §4, §9.2 (`answer-type-consistency`), §14, and here — one token, since the curriculum-objective records validate `answerTypes[]` against `question-item.schema.json#/$defs/answerType` and a mismatched token would fail validation.

This is the **only** schema change the family requests. It must validate under the **bundled Ajv** (which evaluates the `if/then`/`allOf` obligations) and be **accepted** by `oracle/check_conformance.py`; but because that offline subset implements only `{required, type, enum, pattern, properties, additionalProperties(bool), items, minItems, $ref}` and **not** `if/then/allOf/const`, the conditional unit-shape obligations (required-unit binding, dimension⇔exponent lock) are a **no-op there** and are instead enforced offline by the independent validator's `unit-model-wellformed` / `measure-dimension-exponent-lock` / `answer-type-consistency` checks (§4.2/§9.2) — exactly as the pre-existing integer/exact-rational `allOf` conditionals are already unenforced in conformance.py. The extension is additive (no existing answer type changes, so approved families' items stay schema-valid byte-for-byte). Placing the contract in shared core is what makes this single, owner-approved extension reusable by every later measurement family instead of being re-litigated per family.


## Appendix B — Cross-section consistency notes (for human double-check)

1. SCHEMA REALITY CHECK (verified against schemas/question-item.schema.json): the live answer.type enum is BROADER than the owner-brief snapshot — it already contains exact-surd, exact-trig, mixed-number, vector, matrix, complex-number, etc., and does NOT contain quantity/measure. Confirmed: no 'quantity'/'measure'/'dimension' answer type and no structured unit object exist; answer.units is only a free-form STRING (line 237) and the answer object is additionalProperties:false. So the dimensional-quantity contract genuinely requires an owner-gated schema extension (new enum value + structured answer.measure object), exactly as flagged. The front matter cites these facts rather than the brief's narrower enum snapshot to avoid a false 'current enum' claim in §4.
2. The brief's snapshot lists difficulty axes as a CLOSED enum, but the live schema (question-item.schema.json $defs.difficultyProfile.axes) does NOT enforce additionalProperties:false on axes (it lists named 0..1 axes incl. numericalComplexity, abstraction, interpretationDemand). §11 should state it will use ONLY the platform-named axes and treat them as closed by convention/test, not assert the schema enforces closure. Front matter keeps to 'closed-enum axes' as the family's self-imposed contract — flag this so §11 does not over-claim schema enforcement.
3. DECISION_LOG is currently at #49 (gen.stats.data-handling CURRICULUM-APPROVED at v1.0.2). This proposal, once logged, would be the next entry (~#50). No DECISION_LOG entry number is asserted in the front matter to avoid pre-allocating one; §15 should record the actual entry on owner action.
4. Reused themes verified present: core/visual-style/cartesian-theme.{json,ts} (coordinate-lines v1.0.2 per-root cx-figure isolation; modes print/premium/premium-dark/accessible) and core/visual-style/data-chart-theme.{json,ts} (stats v1.0.2 ADDITIVE extension). The mensuration extension is named 'data-dimension-theme' in the glossary as a placeholder; the owner/§7/§16 may prefer a different name (e.g. 'dimension-theme' or 'mensuration-theme') — naming is a §16 decision, flagged as not yet pinned.
5. SDK lifecycle verified: approvalStatus ∈ {approved, pending-review, rejected} on core/sdk/sequence-registry.ts + generator-module.ts (DECISION_LOG #38); objectives during a pending build use reviewStatus 'approved-for-implementation' then 'approved' (stats precedent #45/#46). Front matter mirrors this two-stage gate.
6. exact-surd / exact-trig EXIST in the live answer.type enum but the brief forbids surds/irrationals; the proposal DEFERS them (they are deferred topics: Pythagoras/surds, circles/pi). Front matter lists them under DEFERRED via the no-irrationals rule. Ensure §4/§5 explicitly state the family never emits exact-surd/exact-trig answers despite their availability in the enum.
7. Objective IDs proposed here (SPI.MIDDLE.MENS.*) follow the verified five-segment precedent depth and the schema regex; they are NOT owner-pinned in the brief (unlike the stats IDs, which were owner-pinned). They are this proposal's RECOMMENDATION for owner ratification in §1/§2 — flagged so the owner knows the exact spellings are proposed, not mandated.
8. No curriculum/objectives/SPI.MIDDLE.MENS.json file exists yet (correct — proposal only, no files). The single-source OBJECTIVE_BY_TASK map and the bespoke family graph test (cf. core/curriculum/stats-graph.test.ts / stats-objective-ids.ts) are to be authored at build time; §1/§9 should specify them but no file is created now.

## Appendix C — Authoring & verification provenance

Authored by a multi-agent workflow: 16 sections drafted in parallel against a fixed platform-conventions digest + the owner brief, reviewed by four adversarial critics (mensuration-math correctness, platform-fit, rendering/unit-contract, completeness), then revised against the consolidated findings and synthesized. The critics raised 38 findings (10 blocker-severity, 16 missing items), applied in the revision pass. PROPOSAL ONLY — no implementation, code, fixtures, or registry entry exists until the owner approves.
