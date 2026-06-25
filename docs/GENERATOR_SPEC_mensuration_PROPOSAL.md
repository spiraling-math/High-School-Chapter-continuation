# Generator Specification — `gen.measurement.mensuration` v1.0.0 (Perimeter, Area & Composite Rectilinear Shapes)

> **STATUS: APPROVED WITH REQUIRED REVISIONS (owner, 2026-06-25) — revised; implementation authorized oracle-first after applying decisions A–M. Objectives: approved-for-implementation; generator registry: pending-review (gated) until the implemented review-pack decision; the question-item schema extension (answer.type 'quantity' + measure) is APPROVED.** This document specifies a new SPI-Math Middle School generator family. The owner's REVISE directive (decisions A–M) has been applied throughout; the design below is the authorized build target. Implementation proceeds **oracle-first** (the independent Python `spi_oracle` is authored and frozen before the TypeScript mirror). The eight objectives are authored at `reviewStatus: approved-for-implementation` (curriculum-cleared to build, generator still gated); they advance to `reviewStatus: approved` only at the later review-pack decision. The family registers `approvalStatus: pending-review` — **gated out of normal Generator Studio and out of production exports/samples** (visible only in `?review` developer mode, labelled "machine-validated — pending curriculum approval") — until that separate review-pack decision. The **additive `question-item.schema.json` extension** (new `answer.type` value `"quantity"` plus a structured `answer.measure` object) is **APPROVED and already implemented in `schemas/question-item.schema.json`**; the build is cleared to depend on it.
>
> **HEADLINE NEW ARCHITECTURE — the first UNIT-AWARE answer contract.** Every prior family answers a pure number (`integer` / `exact-rational` / `fraction` / `set`). Mensuration is the platform's first family whose answer is a **dimensional quantity**: a value that is wrong if the *number* is right but the *dimension* is wrong (e.g. `cm` where `cm²` is required, or a bare number with no unit). The family **uses a structured measure model** — `dimension` (`length` | `area`), `baseUnit` (`mm` | `cm` | `m`), `exponent` (1 for length, 2 for area), an exact integer-or-`Rational` value stored as the bare `answer.canonical`, and a canonical `display` form — and a checker that treats unit meaning **structurally, not as an unchecked text suffix**. **APPROVED + ALREADY-IMPLEMENTED SCHEMA EXTENSION (see §4):** the legacy free-form `answer.units` **string** (the very "unchecked suffix" this contract forbids) remains for legacy types, but `schemas/question-item.schema.json` now additionally carries the new `answer.type` value `"quantity"` plus a structured **`answer.measure`** object (`additionalProperties:false`). The extension is minimal, additive, back-compatible, and **already applied** to the schema; §4 states the exact field shapes, the conditional `if/then`/`allOf` rules, and where each obligation is enforced (runtime Ajv, the extended Python/offline conformance checker, import, bank storage, migration, and export assembly).
>
> **ALL PLATFORM GATES RETAINED — no exceptions.** Deterministic seeded generation (byte-identical Mulberry32 / Python PRNG; deterministic redraw, call-order parity); exact `Rational`/integer arithmetic with **no floats and no irrationals** (so areas/perimeters are exact integers or reduced rationals — see the deferral of Pythagoras/surds/circles below); independent **Python + TypeScript** with closure-agreement; canonical item **and** SVG **byte-for-byte** Py↔TS parity; runtime Ajv schema validation at boundaries (including the new `quantity` answer shape); **all eight tasks are FREE-RESPONSE ONLY** — an explicit multiple-choice request returns a clear unsupported-interaction error and is **never** silently replaced with free-response; mathematical misconceptions are deterministic **free-response diagnostics + feedback**, each rule-recomputed by the independent validator; golden (seed) + a **300-entry task-pinned FREE-RESPONSE parity fixture** (plus explicit tests proving an MC request is rejected for every task) + **`SPI_SWEEP` 10,000-seed** stability sweep + reproducibility re-check + a distribution report proving **every declared band is reachable**; accessibility (axe-core **0 critical/serious**, WCAG AA) with a **data-table fallback for every figure**; offline HTML/JSON exporters (worksheet / answer-key / solutions, offline KaTeX) with bank-json round-trip; a **generation manifest + SHA-256 artifact-integrity tests** (Py + TS); **immutable approved-generator fixtures**; newly generated items begin machine-validated (`lifecycle.state = generated`).
>
> **REUSE, NOT REINVENTION.** This family **reuses the approved visual/style/export discipline through a versioned ADDITIVE extension** and does **not** alter any approved contract in place. It builds on the approved `core/visual-style/cartesian-theme.{json,ts}` (`gen.geometry.coordinate-lines` v1.0.2 — per-root `cx-figure` CSS-custom-property isolation; modes `premium` / `premium-dark` / `accessible` / `print`; `presentationSvg()` / `exportSvg()`; materialised **6000 × 4200** export) following exactly the additive pattern of `core/visual-style/data-chart-theme.{json,ts}` (`gen.stats.data-handling` v1.0.2) — adding **mensuration dimension-rendering primitives** (dimension lines, extension lines, arrowheads, right-angle markers, perpendicular-height markers, measurement labels) the same way, so `coordinate-lines` and `stats` output stay **byte-for-byte unchanged**. It reuses the **canonical-SVG discipline** (`viewBox 0 0 1000 700`, integer pixel coords via `gridRound` round-half-up over exact `Rational`/`Fraction`, **no runtime trig**, byte-identical Py↔TS, `role=img` + `<title>`/`<desc>` + data-table fallback + no-colour-only-information) and the **review-pack COVERAGE-MATRIX machinery** (required cells = every task × supported interaction × reachable band × realised answer shape, **derived from the distribution report**, with the pack builder failing on any missing reachable cell). It registers through the existing **SDK approval lifecycle** (`core/sdk/sequence-registry.ts`, `approvalStatus` `pending-review` → `approved`). No parallel renderer, style layer, export path, or coverage machinery is invented.

## Overview

`gen.measurement.mensuration` is **the next architecture-proving family** because it forces the platform to prove two capabilities it has never had to demonstrate together. First, it introduces the **first unit-aware / dimensional-quantity answer contract**: every existing family checks a pure number, but a perimeter and an area can share the same digits yet differ in dimension, so correctness now depends on a *structured* measure — length vs. area, the base unit, and the exponent — that the checker reasons about explicitly. This is the cleanest possible setting to prove that contract, because v1.0.0 deliberately bans **all** cross-unit conversion: each item uses **one declared base unit throughout** (mm, cm, or m), so the checker only ever distinguishes `length` from `area` and the correct base unit from the wrong exponent — never converting cm↔m (that is a later objective and a later contract extension). Second, it is the **first dimensioned-figure renderer**: rather than plotting data, the figure must carry *measurements* — dimension lines distinct from shape edges, extension lines, arrowheads, right-angle and perpendicular-height markers, and labels that may never touch an edge, a leader, or each other — while showing **only the given dimensions** and **never revealing the missing side or the final answer**. A single **canonical shape-model union** — a discriminated union of `RectangleShape`, `RectilinearCompositeShape`, and `TriangleBaseHeightShape`, each defined by exact integer/rational vertices and dimensions (rectangles and composites are orthogonal; triangles are not) — must drive the student diagram, every dimension label, the prompt, the canonical answer, the worked solution, the misconception calculations, the accessibility text and data-table fallback, and the independent validation — one deterministic source of truth, eight task types.

The v1.0.0 scope is the small, fully-exact core of middle-school mensuration, exactly the eight owner-specified tasks: **perimeter of rectangles; perimeter of composite rectilinear (incl. L-) shapes; area of rectangles; area of triangles with an explicitly shown perpendicular base and height; area of composite rectilinear shapes by decomposition; a missing length from a given perimeter; a missing rectangle dimension from a given area; and a missing triangle base or height — only when the exact answer is guaranteed**. Because all values stay exact `Rational`/integer, areas and perimeters are exact integers or reduced rationals, and **every non-rectilinear, irrational, or approximate topic is deferred and deterministically excluded** — circles + π, volume + surface area, general-triangle perimeter (no validated exact construction), trapezia and other non-rectilinear composites, Pythagoras + surds, unit conversion, scale drawings, compound units, approximate measurements, and irregular/curved boundaries are **unreachable from the seeded task loop**, never silently included. **Direct-calculation figures are mathematically to-scale** (using rational/integer coordinates with deterministic regeneration); the three **hidden-dimension tasks** (missing length, missing dimension, missing triangle base/height) ship a normalized **NOT-TO-SCALE** student diagram with a visible "NOT TO SCALE" notice, so a hidden dimension can never be recovered by measuring the SVG. Sections 1–16 develop each decision; this front matter fixes the identifiers, the reuse posture, the headline answer contract, and the approval posture (revisions A–M applied; implementation authorized oracle-first; generator registry pending-review until the later review-pack decision).

## Identifier glossary

| Item | Value (use verbatim) |
| --- | --- |
| Family / generator id | `gen.measurement.mensuration` |
| Generator version | `1.0.0` (authorized; oracle-first build) |
| Validator version | `1.0.0` (independent Py + TS) |
| Domain | `measurement` (curriculum domain segment `MEAS`) |
| Strand | `mensuration` (new strand) |
| Stage | `middle-school` (stage segment `MIDDLE` — never `MS`) |
| Objective ID pattern | `SPI.MIDDLE.MEAS.<TOPIC>.<MICRO>.01` (matches `^SPI\.[A-Z0-9]+(\.[A-Z0-9_]+)+\.[0-9]{2}$`) |
| Misconception ID prefix | `MISC.MENS.*` (registry-backed, Py + byte-parity TS; deterministic free-response diagnostics/feedback) |
| Headline new contract | **dimensional-quantity answer** — `answer.type="quantity"` + structured `answer.measure` `{ dimension: length\|area, baseUnit: mm\|cm\|m, exponent: 1\|2 }` beside the bare-`Rational` `answer.canonical`; `display` derived from canonical + measure |
| New `answer.type` (APPROVED + IMPLEMENTED) | `"quantity"` — the `question-item.schema.json` extension (new enum value + structured `answer.measure` object) is **APPROVED and already implemented** in `schemas/question-item.schema.json`; the `answer` object is `additionalProperties:false` and the `measure` object is `additionalProperties:false` (see §4) |
| Structured unit field name | **`answer.measure`** (NOT `answer.unit`); the legacy free-form `answer.units` **string** still exists for legacy answer types but is **forbidden on `quantity` answers** and never populated by this family |
| Interaction types used | **`free-response` ONLY** — all eight tasks; **no task offers `multiple-choice`** in v1.0.0; an explicit MC request returns a clear unsupported-interaction error (never silently replaced with FR) |
| Reused substrate | `gen.geometry.coordinate-lines` v1.0.2 canonical-SVG discipline (`cx-*`, single `gridRound` projection, integer coords, no runtime trig, byte-identical Py↔TS) |
| Reused style / export | `core/visual-style/cartesian-theme.{json,ts}` (per-root `cx-figure` isolation; modes `premium`/`premium-dark`/`accessible`/`print`; `presentationSvg()`/`exportSvg()`; 6000 × 4200) **via the new ADDITIVE `core/visual-style/mensuration-theme.{json,ts}` extension** (theme id `spi-math-mensuration-theme/1`, `extends: "spi-math-cartesian-theme/1"`), following the `data-chart-theme` additive PATTERN; ADDS dimension lines, extension lines, arrowheads, right-angle + perpendicular-height markers, measurement labels |
| Reused checkers | `core/answer-checking` exact-rational checker shape, **extended** with the structured dimensional-quantity (unit-aware) checker (byte-parity Py/TS) |
| Reused coverage machinery | the stats v1.0.2 review-pack COVERAGE-MATRIX (required cells derived from the distribution report; pack builder fails on any missing reachable cell) — reused exactly |
| Registry status (on build) | `approvalStatus: pending-review` (gated from normal Studio + production) until the implemented review-pack decision |
| Objective lifecycle (on build) | `reviewStatus: approved-for-implementation` → `approved` only at the later review-pack decision |
| Initial item lifecycle | `lifecycle.state = generated` (machine-validated) |
| Provenance | `origin: generated`, `rightsStatus: academy-owned` |

**The eight v1.0.0 tasks (canonical `task` enum, used verbatim everywhere) ↔ objectives:**

| # | Generator task | objectiveId | Answer dimension |
| --- | --- | --- | --- |
| T1 | `perimeter_rectangle` | `SPI.MIDDLE.MEAS.PERIM.RECTANGLE.01` | length (exponent 1) |
| T2 | `perimeter_composite` | `SPI.MIDDLE.MEAS.PERIM.COMPOSITE_RECTILINEAR.01` | length (exponent 1) |
| T3 | `area_rectangle` | `SPI.MIDDLE.MEAS.AREA.RECTANGLE.01` | area (exponent 2) |
| T4 | `area_triangle` | `SPI.MIDDLE.MEAS.AREA.TRIANGLE_BASE_HEIGHT.01` | area (exponent 2) |
| T5 | `area_composite` | `SPI.MIDDLE.MEAS.AREA.COMPOSITE_DECOMPOSITION.01` | area (exponent 2) |
| T6 | `missing_length_perimeter` | `SPI.MIDDLE.MEAS.PERIM.MISSING_LENGTH.01` | length (exponent 1) |
| T7 | `missing_dimension_area` | `SPI.MIDDLE.MEAS.AREA.MISSING_DIMENSION.01` | length (exponent 1) |
| T8 | `missing_triangle_base_height` | `SPI.MIDDLE.MEAS.AREA.TRIANGLE_MISSING_BASE_HEIGHT.01` | length (exponent 1) |

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
4. Dimensional-quantity answer schema (structured measure model; **approved + already-implemented `question-item.schema.json` extension**)
5. Unit parser, formatter, and equivalence checker (anchored, structural — not text-suffix; no cross-unit conversion in v1.0.0)
6. Canonical shape-model union (RectangleShape / RectilinearCompositeShape / TriangleBaseHeightShape; exact vertices + dimensions)
7. Backward construction of valid questions (one guaranteed exact answer; to-scale direct figures, NOT-TO-SCALE hidden-dimension figures)
8. SVG dimension-rendering contract (additive `cx-figure` extension; given dimensions only; answer never revealed)
9. Solver and independent-validator design (closure, orientation, missing-side, perimeter exterior, area shoelace = decomposition; closure-agreement; byte-SVG; semantic answer-leakage)
10. Misconception and free-response diagnostic registry (`MISC.MENS.*`; deterministic adapters; observableError + feedback)
11. Difficulty model (closed-enum axes; `bandFromScore`; every declared band reachable)
12. Edge cases and degeneracy rules (deterministic exclusion of deferred topics; exact-answer guarantees)
13. Accessibility model (spoken math, alt text, long description, data-table fallback, non-colour indicators)
14. Review-pack and visual-audit plan (coverage matrix; student-vs-answer-key overlays; label-collision + print stress; 6000 × 4200 export; answer-absent-from-student-diagram proofs)
15. Versioning and approval lifecycle (authorized oracle-first build → `pending-review` registry → later review-pack decision)
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

The dimensional-quantity answer is delivered through the **`answer.type` value `"quantity"`**, plus the structured `answer.measure` object. This is the **one** answer-type token the family uses; it appears verbatim in every objective's `answerTypes[]` here, in the §3.2 matrix, in the §4 schema definition, in the §9 validator checks, in the §10 adapter `Quantity` shape, and in the §14/§16 headline decision. The token and its structured `answer.measure` sibling are **already present in `schemas/question-item.schema.json`**: the additive extension (new `"quantity"` enum member + `answer.measure` object, `additionalProperties:false`) is **APPROVED and implemented** (designed in §4, cluster B). Because the curriculum-objective schema validates `answerTypes` against `question-item.schema.json#/$defs/answerType` (line 54), these `answerTypes[]` validate against the live enum. The objective records sit at `approved-for-implementation` (§1.3) only because the generator itself is gated pending the review-pack decision — not because of any pending schema change; the schema extension has landed.

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

**v1.0.0 ships exactly one interaction type: `free-response`.** Every one of the eight tasks is **free-response only** (this is `FREE_RESPONSE_ONLY_TASKS = MENSURATION_TASKS` in §1.3), so `supportedInteractionTypes = ["free-response"]` for every task. The `interactionType` carries a single dimensional-quantity entry and `answer.type = "quantity"` (the §4 structured-unit answer, an approved and already-implemented enum addition). **No task offers `multiple-choice` in v1.0.0.** An explicit request for a multiple-choice interaction is **never silently downgraded to free-response**: the generator returns a clear unsupported-interaction error (§3.3), so an MC request fails loudly rather than being answered with an FR item.

**Why every task is free-response.** The dimensional-quantity answer contract (accept mathematically-equivalent numerical forms with the correct unit; distinguish length from area; reject a correct number with the wrong dimension; reject `cm` where `cm²` is required and vice versa; emit targeted feedback for missing/incorrect units) **is the headline feature**, and making every task free-response guarantees that checker is exercised on **all eight** tasks. There is no multiple-choice path anywhere in the family: no task is MC-eligible or MC-enabled, no manufactured "nearby wrong number" distractors are constructed, and no misconception is forced into a four-option question. The mathematical misconceptions remain valuable purely as **deterministic free-response diagnostics and feedback** — when a response matches a known misconception value or shape, the checker emits a targeted hint — and they are surfaced exactly as the owner brief routes them.

The unit-dimension misconceptions named in the brief — `MISC.MENS.LINEAR_UNITS_FOR_AREA`, `MISC.MENS.SQUARE_UNITS_FOR_PERIMETER`, `MISC.MENS.RIGHT_NUMBER_NO_UNIT` — are **free-response feedback only** (the checker emits a targeted hint when a response matches one of these); they are never distractor options because no multiple-choice items exist. The mathematical value diagnostics referenced anywhere in this section use their **canonical §10 registry ids verbatim** — `MISC.MENS.ADDS_TWO_SIDES_RECT`, `MISC.MENS.AREA_WHEN_PERIMETER`, `MISC.MENS.PERIMETER_WHEN_AREA`, `MISC.MENS.ADDS_INSTEAD_OF_MULT_AREA`, `MISC.MENS.OMITS_INDENTED_EDGE`, `MISC.MENS.DOUBLE_COUNTS_INTERNAL_EDGE`, `MISC.MENS.SUBTRACTS_WRONG_RECT`, `MISC.MENS.FORGETS_TO_HALVE_TRIANGLE` — with **no alternative spellings** (the §1.3(d) string-scan test enforces this over the `MISC.MENS.*` namespace). No manufactured "nearby wrong number" rules are registered (there is no MC eligibility to satisfy, so no "third value rule" is invented). The "uses a sloping side instead of the perpendicular height" pitfall is **diagnostic-only**: a sloping side of an axis-aligned-base / perpendicular-height triangle is `√(base² + height²)`, irrational for almost all integer/rational pairs, which violates the no-surds/no-Pythagoras exact-math rule and cannot be a reduced `Rational`. It is therefore carried **only as a free-response pedagogical hint** (`MISC.MENS.USES_SLOPING_SIDE`, no numeric distractor) — see §10. (Full registry, adapters, observableError/feedback in §10, cluster C.)

### 3.2 1:1 task → objective → interaction(s) → answer.shape matrix

`dimension` and `exponent` refer to the §4 structured unit model (length ⇒ `exponent 1`; area ⇒ `exponent 2`); `unit ∈ {mm, cm, m}` is the single declared base unit of the item (no cross-unit conversion in v1.0.0). The "Value form" column lists the exact-arithmetic value type (integer or reduced `Rational{num,den}`); all areas/perimeters are exact integers or reduced rationals, no irrationals.

**Where rational values arise (resolves the §6 integer-coordinate inconsistency).** Rectangle and composite shapes are constructed from **integer** edge lengths and integer vertex coordinates (§6 keeps shape coordinates integer-valued so the canonical-SVG `gridRound` discipline and shoelace check stay on integers). Consequently **rectangle, composite, and missing-rectangle-dimension tasks (T1, T2, T3, T5, T6, T7) produce integer answers only**; there is no rational-sided rectangle, and `missing_dimension_area` (T7) is constructed so the divisor exactly divides the area (`A` is sampled only as a `k`-multiple), guaranteeing an integer answer. **Rational answers arise only on the two triangle tasks**: triangle area T4 (odd `b · h` ⇒ `…/2`) and missing triangle base/height T8 (`2A / b`, generated only when exact). The required mm/cm/m × integer/rational × length/area review-pack coverage (§14) is therefore satisfied with **integer** cells on T1/T2/T3/T5/T6/T7 and **integer + rational** cells on T4/T8 — every declared cell is reachable, so the §14 band-and-shape reachability gate has no empty `…:rational:*` cell to flag (`…:rational:*` cells exist only for the triangle tasks).

| # | Objective ID | Interaction(s) | `answer.type` / shape | dimension · exponent · `unit` | Value form |
| --- | --- | --- | --- | --- | --- |
| T1 | `SPI.MIDDLE.MEAS.PERIM.RECTANGLE.01` | free-response | `quantity` | length · 1 · {mm,cm,m} | integer |
| T2 | `SPI.MIDDLE.MEAS.PERIM.COMPOSITE_RECTILINEAR.01` | free-response | `quantity` | length · 1 · {mm,cm,m} | integer |
| T3 | `SPI.MIDDLE.MEAS.AREA.RECTANGLE.01` | free-response | `quantity` | area · 2 · {mm,cm,m} | integer |
| T4 | `SPI.MIDDLE.MEAS.AREA.TRIANGLE_BASE_HEIGHT.01` | free-response | `quantity` | area · 2 · {mm,cm,m} | integer or reduced rational (odd `b·h` ⇒ `…/2`) |
| T5 | `SPI.MIDDLE.MEAS.AREA.COMPOSITE_DECOMPOSITION.01` | free-response | `quantity` | area · 2 · {mm,cm,m} | integer |
| T6 | `SPI.MIDDLE.MEAS.PERIM.MISSING_LENGTH.01` | free-response | `quantity` | length · 1 · {mm,cm,m} | integer |
| T7 | `SPI.MIDDLE.MEAS.AREA.MISSING_DIMENSION.01` | free-response | `quantity` | length · 1 · {mm,cm,m} | integer (constructed so the divisor exactly divides the area) |
| T8 | `SPI.MIDDLE.MEAS.AREA.TRIANGLE_MISSING_BASE_HEIGHT.01` | free-response | `quantity` | length · 1 · {mm,cm,m} | integer or reduced rational (`2A/b`), exact only |

**Interaction summary:** every task is **free-response**; **no task offers multiple-choice** in v1.0.0. This single source of truth is consumed by the review-pack **COVERAGE-MATRIX** machinery (re-used by name from stats v1.0.2): required cells = every task × supported interaction × reachable difficulty band × realised answer shape, derived from the distribution report; the pack builder fails on any missing reachable cell. Because every task's answer shape is `quantity`, the matrix's "realised answer shape" axis additionally records `(dimension, exponent, unit, value-kind ∈ {integer, rational})` so that mm/cm/m × length/area × integer/rational coverage (required by the owner review-pack plan) is provably exercised and blocked on if missing — with `rational` cells required for T4/T8 (the triangle tasks) and `integer` cells required for all eight.

### 3.3 Scope guard (exactly the eight tasks)

The task enum `MENSURATION_TASKS` (§1.3) has exactly eight members; the generator dispatch is a **total function** over that enum with no default branch, and the conformance/graph tests assert the objective set, the task set, the `RULES_BY_TASK` key set, and the coverage matrix all have **cardinality eight** and an **identical key set** (§1.3(c)). Because every task declares `supportedInteractionTypes = ["free-response"]`, any request for a `multiple-choice` interaction is rejected with a clear **unsupported-interaction error** (`interaction-not-supported`), never silently satisfied with a free-response item; a named test asserts that an MC request returns this error for **each of the eight tasks** (§5.5). Every deferred topic — circles/pi, volume/surface area, general triangle perimeter (no exact construction in v1.0.0), trapezia/non-rectilinear composites, Pythagoras/surds, unit conversion, scale drawings, compound units, approximate measurements, irregular curved boundaries — is **deterministically excluded by construction**: there is no task slug, objective ID, or generator branch that can emit one, and each exclusion is asserted by a named test (§7/§12/§15), not merely filtered at runtime.


---

## 4. Dimensional-quantity answer schema

### 4.1 The core problem and the design decision

Every answer in the eight mensuration tasks is a *dimensional quantity*: a number that is meaningless without a dimension (length vs. area) and a base unit (mm, cm, m). The platform's current `answer` contract (`schemas/question-item.schema.json` `$defs/answer`) cannot represent this safely:

- Before this extension, `answer.type` was drawn from a closed `$defs/answerType` enum (`integer`, `exact-rational`, `mixed-number`, ... ending `short-explanation`, `extended-response`, `proof`, `rubric-scored`) with **no** unit-bearing type — which is exactly the gap the now-implemented `quantity` type fills.
- The legacy `answer.units` string still exists (`{ "type": "string" }`, e.g. `"cm"`, `"m s^-1"`) but it is **an unchecked text suffix**: a display string, not a structurally checked object. A checker that compared it would be string-matching `"cm"` vs `"cm^2"` vs `"cm²"` vs `"square cm"` — exactly the fragile behaviour the owner brief forbids, so `quantity` answers forbid `answer.units` and carry the structured `answer.measure` object instead.
- `answer.accepts` is `additionalProperties:false` with only `{fraction, decimal, mixed}` booleans, so the structured measure could not be smuggled into `accepts`; it is therefore a top-level sibling `answer.measure` object — the additive shape now realised in the schema.

**Decision (single source of truth): add ONE new answer type, `quantity`, carrying a structured `measure` object, as a minimal, additive, back-compatible extension to `question-item.schema.json`.** The type token is **`quantity`** verbatim everywhere — the `$defs/answerType.enum` member, every objective's `answerTypes[]` (§2), the §3.2 task matrix `answer.type`, the checker-registry routing key, the §9 validator `answer-type-consistency` check, the §14 COVERAGE-MATRIX realised-answer-shape axis, and the §16.3 headline decision. The structured dimensional object that rides alongside it is `answer.measure` (the field name `measure`, not `unit`), matching the implemented schema.

We choose a new `type` over a bare additive `measure` field on `integer`/`exact-rational` because:

1. The answer-type *is* the routing key for the checker registry, the `answerTypes[]` objective field, and the COVERAGE-MATRIX "realised answer shape" axis. A dimensional quantity is a genuinely different *shape* of answer (number + dimension + unit), and giving it a name (`quantity`) lets the COVERAGE-MATRIX require "length answer" and "area answer" cells as first-class realised shapes, exactly as the brief's review-pack plan demands.
2. It keeps the numeric core unchanged: `canonical` reuses the established `{num, den}` rational encoding (`core/exact-math/rational.ts`, `fractions.Fraction`), so all exact-math, parity, and serialization machinery applies unmodified.
3. It avoids overloading `integer`/`exact-rational`, whose checkers are unit-blind and are relied on by five shipped families; those code paths stay byte-for-byte unchanged.

> **SCHEMA CHANGE — APPROVED AND IMPLEMENTED.** This `question-item.schema.json` extension is minimal, additive, and back-compatible (no existing item changes meaning; no field is removed or retyped). It is **owner-approved and already applied to `schemas/question-item.schema.json`**, and it shipped through the same SDK `pending-review -> approved` lifecycle (`core/sdk/sequence-registry.ts`) as the family itself. The exact diff is given in §4.4. The extension is exactly TWO additions: the enum token `quantity`, and a structured sibling `answer.measure` object — the structure is fixed in §4.3 and is the only one realised by the §4.4 schema and the §9 validator. (For `type:"quantity"` a unit is **always** required — it is the defining contract — so there is no opt-out flag.)

### 4.2 The structured unit model

The unit model is a closed, self-contained object. It is the single source of dimensional truth and is referenced by the prompt, the canonical answer, every misconception adapter, the worked solution, the accessibility text, and the independent validator.

```
Measure = {
  dimension:  "length" | "area",        // closed enum
  baseUnit:   "mm" | "cm" | "m",        // closed enum (one declared unit per item)
  exponent:   1 | 2                      // 1 iff dimension="length", 2 iff dimension="area"
}
```

The `measure` object carries **no `display` field**: the display string lives only at the top-level `answer.display` (derived from the canonical value + `measure` by the §5.2 formatter), never duplicated inside `measure`.

Invariants (enforced by **bundled Ajv** via the §4.4 `if/then` conditionals, by the offline `check_conformance.py` conformance checker now that it supports `allOf/if/then/const` (§4.4), **and** by the independent validator's `quantity-measure-contract` and `quantity-dimension-exponent-lock` checks (§9)):

| Invariant | Rule |
|---|---|
| dimension/exponent lock | `exponent === 1 ⟺ dimension === "length"`; `exponent === 2 ⟺ dimension === "area"`. No other pairing is representable. |
| single base unit (v1.0.0) | `baseUnit` is one of `mm/cm/m`; the SAME `baseUnit` is used by every given dimension in the figure, the canonical answer, and all distractors. **No cross-unit conversion** occurs anywhere in v1.0.0 (see §4.5). |
| display canonicality | The display string (produced by §5.2 and stored only at `answer.display`, not inside `measure`): `baseUnit` for `exponent=1`, `baseUnit + "^2"` for `exponent=2`. It is presentation only; the checker never reads it. The stored `display` uses the ASCII `^2` token, never the Unicode `²` (asserted by the §5.2 `display-is-ascii-caret` check, for byte-stable golden/parity fixtures across encodings/locales). |

The numeric value is an exact reduced `Rational` `{num, den}`:

```
Rational = { num: integer, den: integer >= 1 }   // reduced; den = 1 for integer answers
```

A full dimensional answer is the pair `(value, measure)` used internally by the parser/formatter/checker:

```
QuantityAnswer = {
  value:   Rational    // exact reduced {num, den}; den=1 for integer answers
  measure: Measure
}
```

`value` is the same `Rational`/`Fraction` contract as `exact-rational`; area answers on rectilinear integer/rational figures are exact integers or reduced rationals, never irrationals (consistent with the no-surds constraint).

### 4.3 How it rides on the item `answer` (authoritative encoding)

The item `answer` object uses the new type and stores the structured `measure` as a **separate sibling** of the numeric `canonical`. **`canonical` stays a bare `{num, den}` Rational, unchanged from `exact-rational`; the measure is NOT folded into `canonical`.** (This resolves the §16.3 contradiction: §16.3's `canonical = {dimension, baseUnit, exponent, value:{num,den}}` is superseded — the encoding below is authoritative, because it preserves the exact-rational canonical contract and keeps every existing rational/parity/serialization path byte-identical, which is the design rationale in §4.1.)

```
answer = {
  type:      "quantity",                     // NEW enum member (canonical token)
  canonical: { num, den },                   // exact numeric value (Rational), unchanged encoding — NO unit inside
  measure:   Measure,                         // NEW structured sibling (dimension, baseUnit, exponent)
  display:   string,                          // canonical full display, e.g. "15 cm", "24 cm^2"
  accepts:   { fraction, decimal, mixed }     // existing numeric-equivalence booleans, reused as-is
}
```

- `canonical` stays a `{num, den}` rational — **not** wrapped with the measure — so every existing rational/parity/serialization path treats it identically to an `exact-rational` value. The dimension lives only in `measure`. The §9 `closure-agreement` check therefore compares **two things separately**: the recomputed `value` (Rational, by cross-multiplication) against `answer.canonical`, and the recomputed `(dimension, exponent, baseUnit)` triple against `answer.measure` — not a single merged object.
- `display` is the formatter's full rendering (§5.2): `"<value-display> <unit-display>"`, e.g. `"15 cm"`, `"3/2 m"`, `"24 cm^2"`. It is derived from `canonical` + `measure` and stored **only** here at `answer.display`; it is never duplicated inside `measure`.
- `accepts.fraction/decimal/mixed` keep their existing meaning for the numeric part (e.g. accept `30/2` for `15`, accept the terminating decimal when permitted). There is **no `requireUnit` flag**: for `type:"quantity"` a unit is **always** required — supplying the correct unit is the defining contract of a dimensional quantity, with no opt-out. A numerically-correct, unit-less response is **always** graded incorrect with the targeted "missing unit" feedback (§5.3).

**`measure` vs legacy `units` string (flagged).** The schema also carries a legacy free-text `answer.units` *string* (plural, with the trailing `s`). The new structured object is the singular `answer.measure`. These are different fields: the legacy `answer.units` string is **forbidden on quantity answers** and is **never populated by this family**. Mensuration items populate **only** `answer.measure` and never `answer.units`; the validator's `no-legacy-units-string` check (§9) asserts every mensuration item omits `answer.units`. (We keep the structured object at top level as `answer.measure` rather than nesting it under `canonical`, to preserve the bare-Rational `canonical` contract above.)

### 4.4 Exact schema diff (approved + applied; minimal, additive, back-compatible)

Three additive edits to `schemas/question-item.schema.json`, **already applied**; nothing is removed or retyped.

1. **Add one enum member** to `$defs/answerType.enum`. The real enum (lines 196-204) begins `"integer", "decimal", "fraction", "exact-rational", "mixed-number", ...` and ends `..., "proof", "rubric-scored"`. **Append `"quantity"` at the very end of the enum, after `"rubric-scored"`** (a fixed byte position; appending at the tail minimises churn to the committed golden schema and is unambiguous for the parity diff):
   ```
   ..., "short-explanation", "extended-response", "proof", "rubric-scored", "quantity"
   ```

2. **Add one optional property** — a `measure` object on `$defs/answer.properties`. (No `accepts.requireUnit` key is added: a unit is unconditionally required for `type:"quantity"`, so there is no opt-out boolean.) The `measure` object is `additionalProperties:false` and its `required` list is exactly `["dimension","baseUnit","exponent"]` — **no `display` key inside `measure`** (display lives only at top-level `answer.display`):
   ```jsonc
   "measure": {
     "type": "object",
     "additionalProperties": false,
     "required": ["dimension", "baseUnit", "exponent"],
     "properties": {
       "dimension": { "type": "string", "enum": ["length", "area"] },
       "baseUnit":  { "type": "string", "enum": ["mm", "cm", "m"] },
       "exponent":  { "type": "integer", "enum": [1, 2] }
     }
   }
   ```

3. **Add an `if/then` conditional** to the existing `$defs/answer.allOf` array (lines 241-252) binding the new type to its obligations, mirroring the existing `integer`/`exact-rational` conditionals already in that array:
   ```jsonc
   {
     "$comment": "A 'quantity' answer carries a bare-Rational canonical {num,den>=1} plus a structured measure; dimension and exponent are locked.",
     "if":  { "properties": { "type": { "const": "quantity" } }, "required": ["type"] },
     "then": {
       "required": ["measure"],
       "properties": {
         "canonical": { "type": "object", "required": ["num", "den"],
           "properties": { "num": { "type": "integer" }, "den": { "type": "integer", "minimum": 1 } } },
         "measure": {
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

**Where each obligation is enforced (now machine-checked end to end).** The conditional rules — the `if/then` dimension⇔exponent lock and the `type:"quantity" ⇒ measure` requirement — are enforced everywhere the contract is read: the runtime **production Ajv** gate (which fully supports `allOf/if/then/const`), the offline **`oracle/check_conformance.py`** conformance checker, import, bank storage, migration, and export assembly. The conformance checker was **extended** to support `allOf`, `if`, `then`, and `const`: it previously implemented only `$ref, type, enum, pattern, properties, additionalProperties(bool), items, minItems, required` and silently ignored the pre-existing `integer`/`exact-rational` `allOf` conditionals; it now evaluates those constructs, so the dimension/exponent lock and the `quantity ⇒ measure` requirement **are machine-checked offline**. Existing integer/exact-rational items are unaffected by this extension (their conditionals were already satisfied; the checker now actively verifies what it previously skipped). Therefore:

- **Offline `check_conformance.py` enforces, for the new type:** enum membership of `"quantity"`, `required:["type","canonical"]`, `additionalProperties:false` on `answer` and on `measure`/`accepts`, the `enum`s inside `measure`, the `{num,den}` types — **and**, via the new `allOf/if/then/const` support, the conditional dimension/exponent lock and the `quantity ⇒ measure` requirement. Concretely, offline conformance now *rejects* a malformed `quantity` answer that omits `measure` or pairs `dimension:"area"` with `exponent:1`.
- **The conditional invariants are additionally enforced by the independent validator's named checks** `quantity-measure-contract`, `answer-type-consistency`, and the dedicated `quantity-dimension-exponent-lock` check (§9) — so the invariant holds under Ajv, conformance.py, and the validator alike (defence in depth, not a single point of enforcement).

Back-compatibility: every existing item still validates (no existing item uses `type:"quantity"`; `measure` is optional and absent elsewhere; no `requireUnit` key exists). The legacy `answer.units` *string* remains in the schema for non-mensuration families; mensuration items do **not** use it (§4.3, `no-legacy-units-string`). Live `quantity` items are added to the conformance harness's live-generation block (§5.5) alongside the existing families so the schema/instance shape agreement is exercised on real generator output.

### 4.5 No cross-unit conversion in v1.0.0

A v1.0.0 item declares ONE `baseUnit` and uses it throughout: every given dimension on the figure, the canonical answer, and all distractors share that `baseUnit`. The checker performs **no** mm↔cm↔m conversion. `cm ↔ m` conversion, mixed-unit figures, and compound units are a **later objective plus a contract extension** (a future `unit.scale`/conversion table), explicitly deferred and deterministically excluded here: the generator never emits an item whose figure or answer mixes base units, and the validator's `single-base-unit` check fails any item where the answer `baseUnit` differs from any figure-dimension `baseUnit`.

### 4.6 Worked encodings

Per §6/§7, rectangle and composite edge lengths are **integer-only**, so a rational answer never arises from a rectangle or composite task. **Rational answers are reachable only from the triangle tasks** — `area_triangle` (`b·h÷2` with odd `b·h`) and `missing_triangle_base_height` (`2A÷known`) — so the rational worked example below is a triangle, not a rectangle. The length and area examples are valid for any task of their dimension.

**Length answer** — perimeter of a rectangle, given 5 cm × 10 cm, answer 30 cm:

```jsonc
"answer": {
  "type": "quantity",
  "canonical": { "num": 30, "den": 1 },
  "measure": { "dimension": "length", "baseUnit": "cm", "exponent": 1 },
  "display": "30 cm",
  "accepts": { "fraction": true, "decimal": true, "mixed": false }
}
```
Accepted full-credit inputs: `30 cm`, `60/2 cm`, `30.0 cm` (decimal permitted because den=1 terminates). Rejected: `30` (missing unit → `missing-unit`), `30 cm^2` (square-for-perimeter, the `wrong-exponent` sub-case), `30 m` (`wrong-base-unit`), `15 cm` (wrong number → `incorrect-value`).

**Area answer** — area of a triangle, base 6 cm, perpendicular height 5 cm, answer 15 cm² (½·6·5):

```jsonc
"answer": {
  "type": "quantity",
  "canonical": { "num": 15, "den": 1 },
  "measure": { "dimension": "area", "baseUnit": "cm", "exponent": 2 },
  "display": "15 cm^2",
  "accepts": { "fraction": true, "decimal": true, "mixed": false }
}
```
Accepted: `15 cm^2`, `15 cm²`, `30/2 cm^2`, `15.0 cm^2`. Rejected: `15 cm` (linear-for-area, the `wrong-dimension` sub-case), `15` (`missing-unit`), `30 cm^2` (forgot to halve → `incorrect-value`; a value misconception, `FORGETS_TO_HALVE_TRIANGLE`), `15 m^2` (`wrong-base-unit`).

**Rational area** — triangle, base 3 m, perpendicular height 5 m, answer 15/2 m² (½·3·5; rectangles are integer-only, so this rational case is a triangle):

```jsonc
"answer": {
  "type": "quantity",
  "canonical": { "num": 15, "den": 2 },
  "measure": { "dimension": "area", "baseUnit": "m", "exponent": 2 },
  "display": "15/2 m^2",
  "accepts": { "fraction": true, "decimal": true, "mixed": false }
}
```
Accepted: `15/2 m^2`, `30/4 m^2`, `7.5 m^2` (terminating). Rejected: `7.5 m` (linear-for-area, the `wrong-dimension` sub-case), `7.5` (`missing-unit`).

All eight tasks are **free-response only** (§3); there are no multiple-choice items in v1.0.0, so no answer ever carries a set of option `display` strings or manufactured value distractors. The mathematical misconceptions (§10) and the unit-dimension misconceptions (`LINEAR_UNITS_FOR_AREA`, `SQUARE_UNITS_FOR_PERIMETER`, `RIGHT_NUMBER_NO_UNIT`) are surfaced solely as free-response checker feedback and targeted hints, per the brief — never as four-option distractors.

---

## 5. Unit parser, formatter, and equivalence checker

All three components are authored independently in Python (`spi_oracle/unit_model.py`) first and mirrored byte-identically in TypeScript, following the oracle-first parity discipline. They are pure, deterministic, and unit-tested with golden + parity fixtures.

### 5.1 Parser: `string -> QuantityAnswer | ParseError`

The parser is intentionally narrow: it parses against the item's **single declared** `measure.baseUnit` and `measure.exponent`. It does not normalise across units (none exist in v1.0.0). Signature: `parse(raw: string, declared: Measure, accepts) -> { value: Rational, measure: Measure | null } | { error }`. (There is no `requireUnit` parameter — a unit is always required for `type:"quantity"`; the unit-present decision belongs to gate 1, §5.3.)

Algorithm (deterministic, no locale dependence). The parser is **anchored**: it does not "split at the first alphabetic character". Instead it matches the numeric form, then matches the trailing unit token against a **closed, documented finite alias table** (step 4); anything that is not an exact match of that grammar is rejected. This anchored approach removes the ambiguity of split-at-first-alpha and makes every accept/reject decision a table lookup.

1. Trim; collapse internal whitespace to a single space; **normalize a Unicode minus (U+2212) to ASCII `-`**; lower-case the unit token only.
2. **Anchor the parse against the grammar `<numeric><optional-space><unit-token>`.** The numeric form is matched by the numeric regexes in step 3; the unit token is matched by the closed alias table in step 4. The match must consume the **entire** trimmed input: any **trailing unparsed text** after a valid `<numeric><unit-token>` (e.g. `"15 cm foo"`, `"15 cm cm"`) is rejected as `malformed-response`, and **multiple conflicting unit tokens** (e.g. `"15 cm m"`, `"15 cm^2 cm"`) are likewise rejected as `malformed-response`. Examples of well-formed inputs the grammar accepts: `"15 cm^2"`, `"12cm"`, `"3/2 m"`, `"1.5 mm"`, `"12 cm²"`.
3. **Numeric parse** of the numeric portion into an exact `Rational`:
   - integer `^-?\d+$` → `{num, den:1}`;
   - fraction `^-?\d+/\d+$` → reduced `Rational`;
   - decimal `^-?\d+(\.\d+)?$` → exact `Rational` via `from_decimal` (e.g. `7.5` → `15/2`), accepted only when `accepts.decimal` and the value **terminates**;
   - mixed `^-?\d+ \d+/\d+$` → `whole + fraction` as a reduced `Rational`, accepted only when `accepts.mixed` (off by default). A single internal space for a mixed number is the ONLY internal space the numeric portion may contain. Example: `parse("2 1/2 m", …)` → numeric `2 1/2` = `5/2`, unit `m`.
   - **Scientific notation is rejected** (e.g. `1e3`, `1.5E2`): it never matches the integer/fraction/decimal forms above and yields `error: "malformed-response"`.
   - Any other numeric form → `error: "malformed-response"`.
   - Negative inputs **parse** (the `-?` is intentional) and fall through to gate 4 as `incorrect-value` — every length/area answer is a positive exact value (§12), so a negative is simply numerically wrong; no separate impossible-sign feedback is emitted in v1.0.0 (a `negative-measure-impossible` hint is a possible future tightening, noted but not specified here).
4. **Unit parse** of the trailing unit token into a `Measure` via the closed alias table for the **declared `baseUnit` only**. The table is the single authority for which tokens are accepted; the canonical stored output is always the **abbreviation form** with ASCII `^2`:

   | Accepted unit token (case-insensitive) | Parses to (exponent) |
   |---|---|
   | `cm` | `cm`, exponent 1 |
   | `cm^2`, `cm2`, `cm²`, `sq cm`, `square cm` | `cm`, exponent 2 |
   | `mm`, `mm^2`/`mm2`/`mm²`/`sq mm`/`square mm` | `mm`, exp 1 / exp 2 |
   | `m`, `m^2`/`m2`/`m²`/`sq m`/`square m` | `m`, exp 1 / exp 2 |
   | *(empty / no unit token)* | `measure = null` (NOT a parse error — deferred to gate 1) |
   | *(a recognised unit token whose base ≠ declared `baseUnit`)* | `error: "wrong-base-unit"` |
   | *(unrecognised token)* | `error: "malformed-response"` |

   The alias table accepts the abbreviation forms (`cm`, `cm^2`), the inline-digit forms (`cm2`), the Unicode-superscript forms (`cm²`), and the common English names (`square cm`, `sq cm`); the canonical stored/fixture output is **always** the abbreviation with ASCII `^2` (e.g. `square cm` → stored `cm^2`). The parser returns the *structured* `Measure` it recognised (dimension/exponent derived from the token), **not** the raw text. From here on nothing compares strings.

   **Empty unit owned by gate 1.** An empty unit token yields `measure = null` and is NOT a parse error. Gate 1 (`missing-unit`, §5.3) is the single owner of the missing-unit decision and it is **unconditional** — there is no path that accepts a unit-less numeric, because a unit is always required for `type:"quantity"`. (Only `wrong-base-unit` and `malformed-response` are parser errors.)

### 5.2 Formatter: `QuantityAnswer -> canonical display`

Pure inverse of the canonical token, used for `answer.display`, every option/distractor `display`, solution steps, and the answer-key overlay:

```
formatUnit(m)  = m.exponent === 1 ? m.baseUnit : m.baseUnit + "^2"     // "cm", "cm^2"
formatValue(v) = v.den === 1 ? String(v.num) : `${v.num}/${v.den}`     // reuses Rational.toString
format(a)      = `${formatValue(a.value)} ${formatUnit(a.measure)}`     // "15 cm", "24 cm^2", "15/2 m^2"
```

The formatter is the SOLE producer of `answer.display` (the display string lives only there, never inside `measure`); it is byte-identical Py↔TS so stored displays match the oracle exactly (the parity contract). The stored canonical `display` ALWAYS uses the ASCII `^2` token and NEVER the Unicode `²`, asserted by a named `display-is-ascii-caret` check (no stored `answer.display` may contain `²`), so golden/parity fixtures are byte-stable across encodings/locales — even though the parser *accepts* `cm²` as input. A KaTeX surface form (`24\,\text{cm}^2`) is derived for presentation in prompt/solution blocks, but the stored canonical `display` uses the plain `^2` token shown above.

### 5.3 Equivalence checker contract

`check(raw: string, answer) -> { correct: bool, code, detail }`. The checker treats unit meaning **structurally**: it compares the parsed `Measure`'s `(dimension, exponent, baseUnit)` triple against the canonical `answer.measure`, and never compares raw text suffixes. Every outcome maps to one of the **seven canonical structured result codes**: `correct`, `incorrect-value`, `missing-unit`, `wrong-base-unit`, `wrong-dimension`, `wrong-exponent`, `malformed-response` — each with its own targeted feedback. The `linear-for-area` and `square-for-perimeter` hints are kept as **named sub-cases** of `wrong-dimension`/`wrong-exponent`, narrowing the feedback text without adding new top-level codes. Evaluation order (first failing gate decides the result):

| # | Gate | Condition checked | On failure: result code |
|---|---|---|---|
| 0 | parse | `parse(raw, answer.measure, answer.accepts)` succeeds (no `malformed-response`/`wrong-base-unit` error) | `malformed-response` / `wrong-base-unit` |
| 1 | unit present | parsed `measure !== null` — **unconditional**, a unit is always required | **`missing-unit`** |
| 2 | base unit | `parsed.measure.baseUnit === canonical.measure.baseUnit` | `wrong-base-unit` |
| 3 | dimension | `parsed.measure.dimension === canonical.measure.dimension` | `wrong-dimension` (sub-case **`linear-for-area`**: gave a length where area required) |
| 3b | exponent | `parsed.measure.exponent === canonical.measure.exponent` | `wrong-exponent` (sub-case **`square-for-perimeter`**: gave exp 2 where length required) |
| 4 | value | `parsed.value` equals `canonical` by exact cross-multiplication: `num₁·den₂ === num₂·den₁` (so `30/2 == 15`, `15/2 == 7.5`), subject to `accepts` for the input *form* | `incorrect-value` |
| — | pass | all gates pass | `correct` |

(Note: `wrong-base-unit` surfaces at gate 0 as a parser error when the token is recognised but mismatched; gate 2 is the equivalent structural re-assertion for any path that reaches it. Both map to the same `wrong-base-unit` code. Because dimension and exponent are locked together in `measure`, gates 3 and 3b agree in practice; both canonical codes are listed so each sub-case has an explicit home.)

Key properties, each backed by a named validator check:

- **`equiv-numeric-forms`**: mathematically-equivalent numeric forms with the correct unit are accepted — `30/2 cm`, `15 cm`, `15.0 cm` all pass against canonical `(15, cm¹)`. Equality is exact `Rational` cross-multiplication, never float compare.
- **`distinguish-length-area`**: length and area are separated by the `(dimension, exponent)` pair, not by token text. `15 cm` against an area answer fails with `wrong-dimension` (sub-case `linear-for-area`); `15 cm^2` against a perimeter answer fails with `wrong-exponent` (sub-case `square-for-perimeter`).
- **`reject-correct-number-wrong-dimension`**: a numerically-correct response with the wrong dimension/exponent is rejected at gate 3/3b (it never reaches gate 4).
- **`reject-cross-square`**: `cm` is rejected when `cm^2` is required and vice versa — this is the exponent gate, because `cm` parses to exponent 1 and `cm^2` to exponent 2; the structural triple differs even though the base text `cm` is shared.
- **`targeted-unit-feedback`**: gates 1/3/3b emit *targeted* feedback — `missing-unit`, the `linear-for-area` sub-case of `wrong-dimension`, the `square-for-perimeter` sub-case of `wrong-exponent` — which map to the corresponding `MISC.MENS.*` unit-dimension misconceptions (§10: `RIGHT_NUMBER_NO_UNIT`, `LINEAR_UNITS_FOR_AREA`, `SQUARE_UNITS_FOR_PERIMETER`) and to student-facing hints. Feedback text is built from displayed values only (no internal symbols), consistent with the misconception-feedback contract.
- **`structural-not-textual`**: the checker function literally has no branch that string-compares a unit suffix; the only string handling is in the parser's alias table, after which all logic is over `Measure` fields. A unit test asserts that visually-distinct-but-equivalent unit spellings (`cm^2`, `cm2`, `cm²`, `square cm`) are accepted identically, and that a textually-similar-but-wrong unit (`cm` for `cm^2`) is rejected — proving the suffix string itself is never the comparison key.

### 5.4 No conversion; one declared unit

The checker has no conversion table and never rescales `value`. A recognised non-declared base is rejected outright (`wrong-base-unit`, gate 0/2); there is no path that turns `m` into `cm`. This makes the v1.0.0 contract total and unambiguous and leaves a clean seam for the future `cm↔m` conversion objective (which would add a gate-2.5 conversion step plus a `measure.scale` field — an additive, separately scoped future extension, not a v1.0.0 behaviour).

### 5.5 Parity, registration, and coverage

- **Oracle-first parity.** `unit_model.py` (parser/formatter/checker) is authored and frozen in `spi_oracle` before the TS mirror; golden fixtures (canonical encodings for each `(dimension, baseUnit)`, plus the `display-is-ascii-caret` assertion on every stored display) plus a **300-entry task-pinned free-response parity fixture** (each entry pinned to one of the eight tasks, spanning every gate outcome, including the `cm²`/`cm2`/`cm^2`/`square cm` spellings and the `2 1/2 m` mixed+unit grammar) assert byte-identical Py↔TS results. Because every task is free-response, the fixture is entirely free-response inputs; there are no MC parity rows. The 10,000-seed `SPI_SWEEP` re-runs the checker on every generated item's canonical answer (the independent recomputation), proving the checker agrees with the oracle across the realised distribution.
- **MC requests are rejected (per task).** A named test asserts that requesting a `multiple-choice` interaction returns the `interaction-not-supported` error (§3.3) for **each of the eight tasks** — eight explicit cases — proving no task silently falls back to free-response.
- **Parser/checker test cases (independent, named).** The suite includes a test for each of: equivalent numeric forms with the correct unit (accepted); a correct number with **no unit** (`missing-unit`); a correct number with the **wrong base unit** (`wrong-base-unit`); **linear-for-area** (length given where area required → `wrong-dimension`); **square-for-linear** (area given where length required → `wrong-exponent`); an **incorrect number with the correct unit** (`incorrect-value`); **malformed input** (scientific notation, trailing unparsed text, multiple conflicting unit tokens → `malformed-response`); **canonical ASCII formatting** (every stored `display` uses `^2`, never `²`); and **Unicode-superscript input** (`cm²` accepted, stored canonically as `cm^2`).
- **Schema validation (correct scope).** Live `quantity` items (a length item, an area item, and a rational-area item) are added to `oracle/check_conformance.py`'s live-generation block and to the production Ajv gate. **Both gates now enforce the full contract:** since `check_conformance.py` was extended with `allOf/if/then/const` support (§4.4), it confirms the items' structural shape (enum membership of `quantity`, `required`, `additionalProperties:false`, the `measure` enums) **and** the conditional dimension/exponent lock and the `quantity ⇒ measure` requirement; the production Ajv gate and the validator checks `quantity-measure-contract` / `answer-type-consistency` / `quantity-dimension-exponent-lock` (§4.4, §9) enforce the same invariants in depth.
- **COVERAGE-MATRIX.** The new `quantity` type is a first-class "realised answer shape"; the reachability-derived review-pack COVERAGE-MATRIX (reused exactly from stats v1.0.2) requires cells for length AND area answers, integer AND rational values, and mm/cm/m contexts, and the pack builder FAILS on any missing reachable cell — so §13's accessibility text and the checker's targeted-feedback paths are both exercised by construction.


---

## 6. Canonical polygon and dimension data model

### 6.1 One source of truth

A single immutable record — the **`Figure`** — is the seeded source of truth for every downstream artifact, in the same way the stats family's single seeded dataset is (cf. the stats proposal §6.1 and `core/curriculum/stats-objective-ids.ts`'s single-source pattern, which this family mirrors in `core/curriculum/mensuration-objective-ids.ts`). The `Figure` is a **discriminated shape-model union** over three explicitly named variants — `RectangleShape`, `RectilinearCompositeShape`, and `TriangleBaseHeightShape` — discriminated by `kind` (§6.2). All three variants share a common core (exact vertices, one base unit, dimension annotations, given/hidden roles, shape bounds, rendering metadata, and accessibility metadata) but enforce **shape-specific invariants** (§6.5), and universal/shape validation **dispatches by `kind`** so that, for example, an orthogonal-edge check is never run against a triangle (§6.3). From one `Figure` the generator derives, with no second authoring path: (a) the student diagram (§8 renderer); (b) every dimension label; (c) the prompt text; (d) the canonical dimensional-quantity answer (§4 contract); (e) the worked solution steps; (f) every misconception calculation (§10 adapters); (g) the accessibility `spokenMath` / `media[].altText` / `media[].longDescription` and the `media[].dataTableFallback` object; and (h) the independent validator's recomputation (§9). The validator reconstructs the `Figure` from `params` and asserts the stored SVG **byte-for-byte** (`svg-realises-data`) and the answer **by a second route** (`closure-agreement`), exactly as the canonical-SVG discipline requires. No artifact may read a value that is not a pure function of the `Figure`.

All coordinates and measurements are exact: integers or reduced `core/exact-math/rational.ts` `Rational{num,den≥1,reduced}` values (Python `fractions.Fraction`), serialized as `{num,den}`. There are **no irrationals** anywhere in the model — no surds, no `π`, no sloping-edge lengths that are not rational — a hard inheritance from the EXACT MATH convention that also enforces the brief's deferral of Pythagoras, circles, and general-triangle perimeter. In particular a triangle's hypotenuse, whose length would be `√(b²+h²)` and irrational for almost all integer `b,h`, is **never assigned a length and never measured** (§6.3, §6.5); the model has no field that could hold it.

### 6.2 Coordinate frame and `baseUnit`

Each `Figure` declares exactly one `baseUnit ∈ {mm, cm, m}` (the §4/§5 structural unit; **no cross-unit conversion in v1.0.0**). Vertices live in an abstract **shape-coordinate** plane whose unit is the `baseUnit`; the renderer's `gridRound` projection (§8, reusing the coordinate-lines single-projection-of-record over exact `Rational`) maps shape coordinates to the canonical `viewBox 0 0 1000 700` integer pixel grid.

Shape coordinates are **integer-valued for rectangles and rectilinear composites** (axis-aligned integer edges), which keeps their perimeters and areas exact integers (§6.6). A **triangle** may carry **one rational coordinate** — the foot of the perpendicular height along the base — so that the area `b·h/2` is the only place a reduced `Rational` answer arises in v1.0.0; the base endpoints and the apex remain integer/rational-but-projected exactly via `gridRound`. This resolves the prior internal tension: rational *answers* are reachable only on **`area_triangle`** and the **missing triangle base/height task** (`missing_triangle_base_height`, §6.6) — `missing_dimension_area` is integer-only by construction — while rectangle/composite *side lengths* stay integer, so the §4 worked encodings and the §3.2 value-form column attach "rational only when a side is rational" to **`area_triangle` and `missing_triangle_base_height`**, never to rectangle perimeter/area or to `missing_dimension_area`.

Field shapes below are written as TypeScript-flavoured interfaces for precision; they are the **authoritative** model, authored oracle-first in the Python oracle and mirrored byte-for-byte in TypeScript.

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

// The Figure is a DISCRIMINATED UNION over three named shape-model variants,
// discriminated by `kind`: RectangleShape | RectilinearCompositeShape |
// TriangleBaseHeightShape. The fields below are the shared common core; the
// shape-specific members (decomposition / triangle) are present only on their
// variant. Validation DISPATCHES on `kind` (§6.3, §6.5) — never run an
// orthogonal-edge check against a triangle.
interface Figure {
  kind: "rectangle" | "rectilinear" | "triangle";  // discriminant: RectangleShape | RectilinearCompositeShape | TriangleBaseHeightShape
  baseUnit: BaseUnit;                            // ONE unit throughout (§4/§5)
  vertices: Pt[];                                // ordered CCW; integer for rect/rectilinear
  edges: Edge[];                                 // derived, indexed, with orientation
  dimensions: DimAnnotation[];                   // which segment each GIVEN measurement labels
  decomposition?: RectPiece[];                   // RectilinearCompositeShape only: disjoint rectangles ∪ = shape
  triangle?: TriangleSpec;                        // TriangleBaseHeightShape only: base + perpendicular height
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

For rectangles and rectilinear composites every edge satisfies `orient ∈ {H,V}` — the **orthogonality invariant** (the `edges-orthogonal` construction guard of §7.5/§12.1, re-asserted by the validator's `side-orientation` check, §9/§12.2). This check **dispatches by `kind`**: it runs only for the `RectangleShape` and `RectilinearCompositeShape` variants and is **never applied to `TriangleBaseHeightShape`**, whose hypotenuse is a deliberate non-axis edge. A triangle's base and its perpendicular height are both axis-aligned (the height of a horizontal base is vertical, and vice versa — see §6.5 and §8); the **hypotenuse is the only non-axis edge and carries no `length` and no dimension annotation**. Because the hypotenuse is never measured, a triangle perimeter is structurally unaskable, which is exactly what keeps general-triangle perimeter deferred (§7.7, §12.4).

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

### 6.5 The discriminated shape-model union — three named variants

The shape model is a **discriminated union** over three named variants — `RectangleShape`, `RectilinearCompositeShape`, and `TriangleBaseHeightShape` — sharing the common core of §6.1 (exact vertices, one base unit, dimension annotations, given/hidden roles, shape bounds, rendering metadata, accessibility metadata) but enforcing **variant-specific invariants** that validation **dispatches** on by `kind` (§6.3). The invariants are:

- **`RectangleShape`** — four right angles; opposite sides equal; positive `width` and `height`.
- **`RectilinearCompositeShape`** — closed boundary; non-self-intersecting; no zero-length edges; no duplicate consecutive vertices; every boundary edge horizontal or vertical; positive area; one connected exterior boundary; non-overlapping decomposition rectangles; no internal decomposition edge appears in the exterior perimeter; exact reconstruction from vertices + dimensions.
- **`TriangleBaseHeightShape`** — non-collinear vertices; positive base and positive perpendicular height; base and height correspond (the height is measured to that base); the altitude is explicitly displayed; a right-angle marker is drawn at the altitude foot; the altitude foot lies **on the base segment itself** in v1.0.0; the sloping sides carry **no numerical length**; no Pythagoras or perimeter task is inferable.

**`RectangleShape`.** `kind:"rectangle"`, four vertices `(0,0),(w,0),(w,h),(0,h)`, **integer** `w,h`. Two `given` annotations bind the width edge and a height edge. Perimeter `P = 2(w+h)`, area `A = w·h` — both exact integers (never rational, since both sides are integer). Orientation is varied deterministically (portrait / landscape / square) by swapping the sampled `w,h` roles, satisfying the review-pack "rectangles with different orientations" cell.

**`RectilinearCompositeShape` (incl. L-shapes).** `kind:"rectilinear"`. The polygon is **assembled from non-overlapping axis-aligned rectangles with integer dimensions** whose disjoint union is the shape; `decomposition[]` records exactly those rectangles:

```
interface RectPiece { x: Q; y: Q; w: Q; h: Q; }   // axis-aligned, integer, bottom-left origin
```

The boundary `vertices` are computed from the union outline (the merged exterior walk), guaranteeing **closed, non-self-intersecting, orthogonal, overlap-free** by construction. Two independent area routes must agree (the brief's required cross-check):

- **Shoelace** over the integer vertices: `A_shoelace = ½ |Σ (xᵢ·yᵢ₊₁ − xᵢ₊₁·yᵢ)|` (exact, computed with `Rational`; integer for integer vertices).
- **Decomposition**: `A_decomp = Σ pieceⱼ.w · pieceⱼ.h`.

`area-methods-agree` asserts `A_shoelace == A_decomp` exactly; the worked solution narrates the **decomposition** route while the validator independently confirms via shoelace. Where the template admits it, the **additive** (sum-of-pieces) and **subtractive** (bounding rectangle minus cut-out) routes must also agree, and the decomposition rectangles must be **non-overlapping** with their **union equal to the polygon** (no internal decomposition edge appears in the exterior perimeter). Perimeter is the length of the **complete exterior boundary** `P = Σ exterior edge.length` (every boundary edge, including indented edges) — never a piece-perimeter sum, which would omit indented edges or double-count internal cuts. The full composite math-validation set — polygon closure; non-self-intersection; edge orientation; exact exterior perimeter; missing-edge uniqueness; decomposition rectangles non-overlapping; decomposition union = polygon; shoelace area = decomposition area; subtractive + additive routes agree where applicable — is enumerated as named checks in §7 and §9. These also cover precisely the misconceptions `MISC.MENS.OMITS_INDENTED_EDGE` and `MISC.MENS.DOUBLE_COUNTS_INTERNAL_EDGE` (§10); the canonical perimeter is constructed so the validator can recompute each through its registry adapter.

**`TriangleBaseHeightShape`.** `kind:"triangle"`, with an **explicitly shown perpendicular base and height**:

```
interface TriangleSpec {
  base:   { from: Pt; to: Pt; length: Q; orient: "H"|"V" };  // a true axis edge (integer length)
  height: { foot: Pt; apex: Pt; length: Q };                 // ⟂ to base; axis-aligned; perp marker
  rightAngleAt: Pt;                                          // foot of the height (marker drawn)
}
```

The base is axis-aligned; the height is **perpendicular to it and therefore itself axis-aligned** (vertical for a horizontal base, horizontal for a vertical base). In v1.0.0 the **altitude foot lies on the base segment itself** (acute / right-foot-on-base only); there is no obtuse / extended-base case. A right-angle marker is drawn at `foot` and a perpendicular-height marker along the dashed height segment (§8 primitives). Exact area `A = base·height / 2`, with `base` and `height` perpendicular by construction; the validator independently re-checks perpendicularity and confirms that the **inverse** base/height (recovering one from the area and the other) reproduces the given area (the math-validation triple of §7/§9). When the declared band requires an **integer** area, parities are chosen at construction so that `base·height` is even (§6.6, §7.2); otherwise the area is a reduced `Rational` (e.g. `base=3, height=5 → A = 15/2`), a legitimate exact answer and the family's primary source of rational answers.

The sloping side (hypotenuse) is **never labelled and carries no length** (§6.3). This both keeps triangle perimeter deferred and forces students onto the perpendicular height. The corresponding pitfall — using a sloping side in place of the perpendicular height — is registered as `MISC.MENS.USES_SLOPING_SIDE`. Because all tasks are **free-response only**, every misconception (this one included) is a **free-response diagnostic / feedback rule only**, never a distractor source: `area_triangle` has **no multiple-choice value distractors**. `MISC.MENS.USES_SLOPING_SIDE` is additionally irrational-by-nature — that side's length is irrational for almost all integer `b,h` and cannot be represented as a reduced `Rational` `quantity` — so its adapter returns `null` for any numeric synthesis and the rule never materialises an irrational (or any arbitrary nearby wrong) number, consistent with §10's classification.

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

Rational answers therefore arise only on `area_triangle` and (where the construction yields one) `missing_triangle_base_height`; all six other tasks — including `missing_dimension_area`, whose divisor exactly divides the sampled area — are integer-only. The §14 coverage matrix attaches the `…:rational:…` cells to the two triangle tasks accordingly, so every declared shape×band cell is reachable.

### 6.7 The `hidden` target for missing-value tasks

```
interface HiddenTarget {
  ask: "missing-length" | "missing-dimension" | "missing-base-or-height";
  givenQuantity: { dim: Dim; value: Q; unit: BaseUnit };  // the stated P or A
  recover: DimAnnotation;   // the annotation whose value is hidden (given:false) and asked
}
```

For `missing_length_perimeter`, `missing_dimension_area`, and `missing_triangle_base_height` the asked annotation is `given:false`, so by §6.4 it is **never rendered** — the figure shows the other measurements, and the stated perimeter/area appears only in the prompt, expressed through the §4/§5 dimensional-quantity formatter so its unit is structurally correct (`dim = "length"` for `missing_length_perimeter`; `dim = "area"` for the two missing-area tasks). The student recovers the hidden value. Unique recoverability is a construction invariant (§7.4): the hidden value must be the **unique** solution of the perimeter/area equation given the rendered measurements (`hidden-uniquely-recoverable`). `missing_triangle_base_height` is additionally gated by exactness (`2A / known` must be an exact integer/rational, else deterministic redraw — §7.5), realising the brief's "missing triangle base or height ONLY when the exact answer is guaranteed."

The canonical answer is the §4 contract: `answer = { type: "quantity", canonical: {num,den}, measure: { dimension, baseUnit, exponent }, display, accepts: { fraction, decimal, mixed } }`. The numeric value lives in `canonical` as a bare reduced `Rational` — always a normalized `Rational {num,den}`, integers included (`den` 1) — preserving the existing exact-rational serialization path byte-for-byte; the structured unit is a **separate sibling** `answer.measure`. `display` is **derived** and lives **only** at top-level `answer.display` — it is **not** duplicated inside `measure`. For `type:"quantity"` a unit is **always required**; there is no opt-out, so `accepts` carries no `requireUnit` flag. The validator's `closure-agreement` recomputes the `Rational` value by a second route and independently rebuilds the unit triple `(dimension, baseUnit, exponent)`, comparing the value and the triple — not a merged object (§9).

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

In all three, the stated `givenQuantity` is the dimensional quantity the §4 contract checks (`dim = "length"` for `missing_length_perimeter`, `"area"` for the two missing-area tasks), and the prompt presents it through the §5 formatter so its unit is structurally correct. The missing-dimension math-validation set is uniform: **exactly one unknown**; the displayed givens **determine one positive exact answer**; back-**substitution restores the stated perimeter/area**; and there is **no second valid solution** (§7.5 `unique-answer`, §9).

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

### 7.6 To-scale policy (direct vs. hidden-dimension) and regeneration

The to-scale policy **splits by task family**:

- **Direct-calculation tasks** (`perimeter_rectangle`, `perimeter_composite`, `area_rectangle`, `area_triangle`, `area_composite`) are drawn **mathematically to-scale** from the integer/rational shape coordinates via the §8 `gridRound` projection, and `media[].toScale` is set `true` (as in coordinate-lines), provided the aspect ratio stays clear. When the sampled proportions would render poorly (caught by `well-proportioned`), the **deterministic** response is to redraw with the next seed-draw — never to fudge coordinates. Because the projection is a pure function of exact `Rational` vertices and is byte-identical across Py/TS, "to-scale" costs no parity: the validator recomputes the same integer pixel coordinates and asserts the SVG byte-for-byte (`svg-realises-data`, §9).
- **Hidden-dimension tasks** (`missing_length_perimeter`, `missing_dimension_area`, `missing_triangle_base_height`) use a **normalized NOT-TO-SCALE student diagram** with a visible **"NOT TO SCALE"** banner, and `media[].toScale` is set `false`. The hidden dimension is **not geometrically encoded** and **not recoverable by measuring the SVG or comparing pixel lengths** — the diagram's edge proportions are normalized so that pixel measurement leaks nothing about the unknown.

This split prevents the answer-leakage path where a student recovers a hidden length by measuring the rendered figure rather than reasoning from the stated perimeter/area. The §9/§12 checks enforcing it are: `to-scale-policy-matches-task`, `hidden-dimension-not-geometrically-encoded`, `hidden-dimension-not-measurable-from-svg`, `not-to-scale-banner-present`, `only-given-dimensions-shown`, `no-result-in-student-figure`, and `student-a11y-does-not-state-result`.

### 7.7 Deferred shapes are unreachable, not merely undrawn

The task enum (`MENSURATION_TASKS`), the template set, and the construction pipeline have **no path** that produces a deferred figure: no circle / `π` (no arc primitive, no irrational radius); no volume / surface-area (the model is strictly 2-D, single-polygon); no general-triangle perimeter (the hypotenuse carries no length and no `given` annotation, so a triangle perimeter is unaskable, §6.3); no trapezium / non-rectilinear composite (templates are axis-aligned integer rectangles only; `edges-orthogonal` rejects any oblique edge); no Pythagoras / surds (EXACT MATH forbids irrationals, so even the `USES_SLOPING_SIDE` pitfall is FR-only and never materialises an irrational value, §6.5/§10); no unit conversion (one `baseUnit` per `Figure`, §6.2); no scale drawings, compound units, or approximate measurements (all values are exact; direct tasks render to-scale while hidden-dimension tasks use a normalized not-to-scale diagram, §7.6). A request for any deferred construction is rejected by guard, never silently downgraded — matching the deterministic-exclusion discipline the stats family established and the named exclusion tests in §12.4/§15.1.


---

## 8. SVG dimension-rendering contract

This section specifies the canonical, byte-identical SVG renderer for the mensuration family. It reuses, by name and without modification, the canonical-SVG discipline proven in the shipped geometry/statistics renderers (`domains/geometry/angles.ts`, `domains/geometry/coordinate-lines.ts`, `domains/statistics/data-handling.ts`): a hand-rolled serializer, integer coordinates via `gridRound` over exact `Rational`, byte-for-byte Python↔TypeScript output, a `role="img"` root with `<title>`/`<desc>` children, a per-figure data-table fallback, and no colour-only information. It adds the dimension-rendering primitives the family needs as a **new additive theme extension** (§8.2) exactly the way `core/visual-style/data-chart-theme.{json,ts}` added statistics primitives — the approved `cartesian-theme` and `data-chart-theme` outputs stay byte-for-byte unchanged.

There are **two render channels** built from the same `ShapeModel` (§6): the **student figure** (shown to the learner; only-given dimensions, no answer) and the **answer-key figure** (an additive answer overlay used ONLY in answer-key / solution export channels). Both are pure functions of `params` through the `ShapeModel`; neither is authored independently. Both channels are composed from ONE canonical **base-geometry** fragment plus shared student annotations: the **student SVG** = root + base geometry + student annotations + closing tag; the **answer-key SVG** = root + the **byte-identical** base geometry + the same student annotations + one additive **answer overlay** group + closing tag. The base geometry is byte-identical across channels and the overlay is purely additive (it never alters or reorders any student element), enforced by `answer-key-base-geometry-identical` and `answer-key-overlay-additive-only` (§8.11). The student SVG is **not** required to be a literal byte prefix or suffix of the key SVG (each is a well-formed document with its own closing `</svg>`); the guarantee is structural base-geometry identity plus additive-only overlay, not a prefix/suffix relationship.

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
| Plotting box | fixed integer inset of `80` → drawable region `[80,920] × [80,620]`; a reserved bottom strip `y∈[630,690]` holds the `NOT TO SCALE` banner, which is present **by design** on the three hidden-dimension tasks (§7.6/§8.10) and absent on the direct-calculation tasks |
| Coordinates | every emitted coordinate is an **integer** produced by `gridRound(num, den)` (round-half-up on the exact `Rational`, correct for negatives — the SAME single rounding rule used family-wide, no second mode) over the integer affine layout transform `(x,y) → (OX + SX·x, OY − SY·y)` with integer `OX,OY,SX,SY` chosen from a committed bounding-box-keyed lookup (never a float fit-to-view) |
| Numbers | emitted only via `fmtInt(n)` (base-10, no `+`, no leading zeros except `"0"`, `−` only for negatives). No decimal coordinate formatter exists in v1.0.0 (all rendered coordinates are integers post-`gridRound`; all dimension labels are integer/rational measurements formatted by the shared display helper, not float pixels) |

**To-scale policy splits by task family; deterministic regeneration of poor proportions.** The to-scale decision is keyed off the task slug (§7.6):

- **Direct-calculation tasks** (`perimeter_rectangle`, `perimeter_composite`, `area_rectangle`, `area_triangle`, `area_composite`) are drawn **mathematically to-scale** and set `media[].toScale = true`. Unlike the angle family (whose integer-degree directions are irrational, forcing `toScale:false`), these mensuration shapes are axis-aligned rectilinear polygons (and triangles with an axis-aligned base + perpendicular altitude) whose vertices are exact integers/rationals; the integer affine layout is an exact scaling, so the figures **are** mathematically to-scale, provided the aspect ratio stays clear.
- **Hidden-dimension tasks** (`missing_length_perimeter`, `missing_dimension_area`, `missing_triangle_base_height`) ship a **normalized NOT-TO-SCALE student diagram** with the `NOT TO SCALE` banner present **by design** and set `media[].toScale = false`. The hidden dimension is **not geometrically encoded** and **not recoverable** by measuring the SVG or comparing pixel lengths — edge proportions are deliberately normalized so pixel measurement leaks nothing about the unknown (§8.10).

A `proportion-quality` guard (§8.10) runs in `generate()`: it rejects layouts where (a) the rendered aspect ratio of any rectangle/leg exceeds `8:1`, (b) any drawn edge is shorter than `60` viewBox units, or (c) a composite limb is too thin to host its dimension lines without collision. On rejection the generator advances the **same seeded `mulberry32` stream** to the next `params` (bounded redraw, the parity contract being call order) — it never silently ships a visually poor or mislabelled figure. For direct tasks the redraw seeks clear proportions while keeping `toScale:true`; for hidden-dimension tasks the `toScale:false` normalized diagram is the intended product, not a fallback.

### 8.2 The additive mensuration theme extension (reuse the pattern, do not depend on data-chart-theme)

A new file pair `core/visual-style/mensuration-theme.{json,ts}` is introduced as a **versioned additive extension** with theme id `spi-math-mensuration-theme/1` that `extends: "spi-math-cartesian-theme/1"` **directly** — exactly as `data-chart-theme.json` does (`"extends": "spi-math-cartesian-theme/1"`, confirmed). This is the single canonical theme name for the family; there is no `data-dimension-theme` or other competing theme. It FOLLOWS the `data-chart-theme` additive *pattern* (same mechanism, same `cx-figure` root isolation, same `presentationSvg()`/`exportSvg()` contract) but it does **not** depend on `data-chart-theme`: `presentationSvg`/`exportSvg` compose **cartesian + mensuration** rulesets only, never `+ data-chart`, so none of the chart/pictogram `--cx-bar*`/`--cx-symbol*` variables are pulled in. Concretely, mirroring `data-chart-theme.ts`:

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
| NOT TO SCALE banner | `<text class="cx-nts">` | emitted **by design** on the three hidden-dimension tasks (`missing_length_perimeter`, `missing_dimension_area`, `missing_triangle_base_height`); absent on the to-scale direct-calculation tasks (§7.6/§8.10) |

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

A separate render `canonicalMensSvgOverlay(ShapeModel)` produces the answer-key figure. It is composed from the **same canonical base-geometry fragment and the same student annotations** as the student figure, then adds one additive answer-overlay group before the closing tag, and it is emitted to a distinct `media[]` asset id (`fig-1-key`) used ONLY by the answer-key and solutions exporters — never in the worksheet/student channel.

| Overlay addition | Class | When |
| --- | --- | --- |
| The missing side, labelled with its derived value | `cx-ans` | `perimeter_composite`, `area_composite`, `missing_length_perimeter`, `missing_dimension_area`, `missing_triangle_base_height` |
| The computed perimeter or area total | `cx-ans` (placed in a clear margin) | all tasks |
| Decomposition cut lines (the stated decomposition) | `cx-cut` (dashed) | composite tasks `perimeter_composite`, `area_composite` |
| Per-sub-rectangle / per-triangle area annotations | `cx-ans` | `area_composite`, `area_triangle` |

The overlay reuses the same label-collision engine so overlay annotations do not collide with the student dimensions they sit beside. Because both channels are built from one canonical base-geometry fragment and the overlay only *adds* an answer group, the student and key SVGs share their **base geometry byte-for-byte** and their student annotations unchanged — proven by `answer-key-base-geometry-identical` and `answer-key-overlay-additive-only` (§8.11), which assert (1) the base-geometry bytes are identical between channels, (2) the student-annotation bytes are unchanged between channels, and (3) the only inter-channel difference is the additive overlay group (so a divergent overlay renderer can never silently alter student geometry). The review pack exploits this by showing **student diagram BESIDE answer-key overlay** (§14). `no-answer-in-student-figure` is asserted on the student asset; the inverse `overlay-shows-answer` asserts the key asset DOES carry the `cx-ans` total — and the student/key asset IDs cannot be swapped — so the two channels can never be confused.

### 8.9 Modes, print, and the 6000×4200 export

All four modes (`premium` / `premium-dark` / `accessible` / `print`) are produced via the mensuration-theme `presentationSvg()`; the monochrome `print` mode is the colour-free authoritative rendering and is what the `svg-realises-data` byte parity asserts against (greyscale-authoritative, consistent with the platform canonical-SVG discipline). The materialised self-contained **6000×4200 (S=6)** export reuses the additive theme's `exportSvg(svg, mode, 6000, 4200)` (both rulesets baked inside the clone, `--cx-bg`-filled raster background via `modeBackground`). The same `media[].svg` bytes print correctly on a monochrome laser printer; no inline `fill`/`stroke` colour (all via classes), pure vector (no `<image>`), no `<script>`/animation/`<foreignObject>`, two-column-print safe.

### 8.10 To-scale policy by task family and deterministic regeneration

The to-scale contract splits by task family (§7.6), and the validation checks enforce the split rather than a blanket `toScale:true`:

- **Direct-calculation tasks** (`perimeter_rectangle`, `perimeter_composite`, `area_rectangle`, `area_triangle`, `area_composite`): because the layout is an exact integer scaling of integer/rational vertices, the figure is genuinely to-scale and `toScale:true`. `to-scale-faithful` asserts: each drawn edge length (in viewBox units, recovered from the parsed integer coordinates) is proportional to its true dimension within the single `gridRound` half-unit, with one global scale factor; and the rendered aspect of each rectangle equals its true aspect within that bound.
- **Hidden-dimension tasks** (`missing_length_perimeter`, `missing_dimension_area`, `missing_triangle_base_height`): the student diagram is a **normalized NOT-TO-SCALE** figure with `toScale:false` and the `NOT TO SCALE` banner present **by design**. The hidden dimension is **not geometrically encoded** and **not measurable from the SVG**: the diagram's edge proportions are normalized so that recovering the unknown by measuring pixel lengths or comparing edge ratios is impossible. The named checks `to-scale-policy-matches-task`, `hidden-dimension-not-geometrically-encoded`, `hidden-dimension-not-measurable-from-svg`, and `not-to-scale-banner-present` (§8.11/§9) enforce this; `only-given-dimensions-shown`, `no-result-in-student-figure`, and `student-a11y-does-not-state-result` close the remaining leakage paths.

The `proportion-quality` guard (§8.1) is the *generation-time* gate that triggers deterministic seeded redraw for visually poor proportions; the to-scale checks above are the *validation-time* proof that each shipped figure obeys the policy for its task. The not-to-scale diagram on hidden-dimension tasks is the **intended product, not an exhausted-redraw fallback**.

### 8.11 Blocking SVG / render validators (named `checks[]`)

Every render invariant is an independent, named entry in `lifecycle.validation.checks[]`; any `fail` ⇒ `validation.status = fail`, the item never reaches `machine-validated`, and it is excluded from the offline export. These render-check names are part of the single canonical `checks[]` vocabulary fixed in §9 and referenced verbatim by §12 and §14 (no alternative spellings appear anywhere). The mensuration render checks (additive to the family's geometry/answer checks):

| Check | Asserts |
| --- | --- |
| `svg-realises-data` (byte parity) | `oracle.canonicalMensSvg(buildShapeModel(params)) == ts.canonicalMensSvg(...)` byte-for-byte, and equals stored `media[].svg`; the figure is the deterministic output for `params`, so it can encode nothing else |
| `only-given-dimensions-shown` | the multiset of numeric `cx-measlbl` equals `ShapeModel.givenDimensions[]`; no derived dimension is drawn |
| `no-answer-in-student-figure` | the student asset contains no `cx-ans`/`cx-cut` element and no element carries the missing-side value or the perimeter/area total |
| `overlay-shows-answer` | the answer-key asset DOES carry the derived missing side + total (`cx-ans`) and the stated decomposition (`cx-cut`) |
| `answer-key-base-geometry-identical` | the canonical base-geometry fragment is **byte-identical** between the student and answer-key SVGs, and the student-annotation bytes are unchanged between channels (the answer overlay never alters student geometry) |
| `answer-key-overlay-additive-only` | the **only** inter-channel difference is the additive answer-overlay group; the answer overlay (`cx-ans`/`cx-cut`) is absent from the student export and appears only on the key asset, and student/key asset IDs cannot be swapped |
| `to-scale-policy-matches-task` | `media[].toScale` matches the task family — `true` for the five direct-calculation tasks, `false` for the three hidden-dimension tasks |
| `not-to-scale-banner-present` | the `NOT TO SCALE` banner (`cx-nts`) is present on every hidden-dimension task figure and absent on direct-calculation figures |
| `hidden-dimension-not-geometrically-encoded` | on the three hidden-dimension tasks, the unknown length is not encoded in the integer geometry of the student figure |
| `hidden-dimension-not-measurable-from-svg` | on the three hidden-dimension tasks, the unknown is not recoverable by measuring SVG pixel lengths or comparing edge ratios (normalized not-to-scale proportions) |
| `dimension-line-distinct-from-edge` | no `cx-dim` segment is coincident with a `cx-edge`; every `cx-dim` has two arrowheads and sits at a tier multiple of `OFFSET` off its edge; arrowheads are inward-pointing markers that do not resemble polygon vertices |
| `no-duplicate-svg-ids` | no duplicate SVG `id` attribute across a multi-item export (every asset id is unique in the combined document) |
| `right-angle-marker-present` | one right-angle marker at each rectangle corner / triangle altitude foot |
| `perp-height-marker-present` | every triangle figure has exactly one axis-aligned altitude with a foot right-angle square meeting the base at 90° (height is perpendicular, never a sloping side) |
| `label-no-collision` | every `cx-measlbl` integer box clears all edges, leaders, markers, and other label boxes by ≥ 8 units; leaders do not cross |
| `side-attribution-unambiguous` | each `cx-measlbl` maps to exactly one edge via its anchor/leader midpoint |
| `to-scale-faithful` | **for the five direct-calculation tasks** (where `toScale:true`): parsed edge lengths are proportional to true dimensions under one global scale within the `gridRound` bound. (Not applied to the three hidden-dimension tasks, whose normalized diagram is deliberately not-to-scale, §8.10.) |
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
  type: "quantity",                  // the approved, already-implemented answerType enum member (§4, §16.3)
  canonical: { num, den },           // a normalized reduced Rational (integers as {num, den:1}) — unchanged from exact-rational, byte-identical serialization
  measure: { dimension: "length"|"area", baseUnit: "mm"|"cm"|"m", exponent: 1|2 },  // structured sibling (no display inside)
  display,                           // canonical formatter output (top-level only, derived), e.g. "24 cm" / "15 cm^2" (ASCII "^2", never "²")
  accepts: { fraction, decimal, mixed }
}
```

The numeric value lives in `answer.canonical = {num,den}` — a normalized `Rational` with `den ≥ 1` (an integer is `{num, den:1}`), preserving the exact-rational canonical contract and all existing rational/parity/serialization paths byte-for-byte; the unit is the **separate structured sibling** `answer.measure`, NOT folded into `canonical`, and it carries **no `display`** (the human string is derived and lives only at the top-level `answer.display`). The solver returns a `Quantity = (value: Rational, dimension, baseUnit, exponent, display)`; the validator re-derives a `Quantity` and asserts structural equality of the **value** (as a reduced `Rational`) plus the **measure triple** `(dimension, exponent, baseUnit)` — it does not compare a merged canonical object, because none exists.

### 9.1 Task vocabulary (single source)

Every check, adapter, and review-pack record keys off the eight canonical task slugs defined once in `core/curriculum/mensuration-objective-ids.ts` (`MENSURATION_TASKS`, §1.3) and mirrored verbatim in the Python oracle. Those eight slugs — used **verbatim** below and in `RULES_BY_TASK` (§10.3) — are:

```
perimeter_rectangle, perimeter_composite, area_rectangle, area_triangle,
area_composite, missing_length_perimeter, missing_dimension_area, missing_triangle_base_height
```

**All eight tasks are FREE-RESPONSE ONLY:** `FREE_RESPONSE_ONLY_TASKS = MENSURATION_TASKS` (all eight slugs; cf. stats `FREE_RESPONSE_ONLY_TASKS`). No task is multiple-choice; `supportedInteractionTypes = ["free-response"]`, and an explicit multiple-choice request is **rejected** with a clear unsupported-interaction error (never silently replaced). A bespoke `mensuration-graph.test.ts` asserts `keys(OBJECTIVE_BY_TASK) == keys(RULES_BY_TASK) == MENSURATION_TASKS` and that **no alternative slug spelling appears anywhere** in the family. A task-pinned **free-response parity fixture** (300 entries, task-pinned) plus explicit tests prove an MC request is rejected for **every** task.

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

The solver also emits the **worked `solution.steps[]`** (each `{number, transformation, intermediateResult}`) and the **misconception context** `ctx` (§10) so each free-response misconception diagnostic value is recomputed from the same intermediate values. The final step's `intermediateResult` is the canonical `display`, satisfying the SDK `answerSolutionAgrees` predicate. `solution.steps[]` may also surface the unit-dimension and uses-sloping-side pitfalls (§10.2) as teacher-facing notes and free-response feedback, never as selectable options (the family is free-response only, §9.1).

For tasks `missing_length_perimeter`, `missing_dimension_area`, `missing_triangle_base_height` the unknown is found by `core/exact-math/linexpr.ts` (a single linear equation with one rational unknown); the solver asserts the solution is exact before returning, otherwise the seed is rejected by the **deterministic redraw loop** (call-order preserving) — degeneracy never silently produces an approximate answer (§12).

### 9.3 Independent validator (`validate(item) -> {status, validatorVersion, checks[]}`)

The validator emits an ordered `checks[]` array of `{name, result, detail}`, status `pass` iff every check passes — identical in shape and naming style to the approved `gen.stats.data-handling` validator (`closure-agreement`, `svg-realises-data`, `chart-realises-data`, role-based leakage). It composes the domain-independent SDK predicates in `core/sdk/checks.ts` (`answerSolutionAgrees`, `provenanceComplete`, …) and adds the mensuration-specific checks below. Functional parity (status + check list) is asserted Py↔TS; the result is not serialized, so it need not be byte-identical, but the SVG and item it validates **are** byte-identical across languages.

**Canonical check-name vocabulary.** The names in the tables below are the **single fixed `checks[]` vocabulary** for this family; §8 (render), §12 (degeneracy), §13 (a11y), and §14 (review pack) reference these exact strings verbatim — no alternative spellings (e.g. `polygon-closed`, `area-shoelace`, `missing-side-determined`) appear anywhere. A spec-internal test asserts the documented name set equals the emitted set.

**A. Universal checks (every task)**

| Check name | Assertion |
|---|---|
| `objective-mapping` | `item.objectiveIds == [OBJECTIVE_BY_TASK[task]]` — the single-source map in `core/curriculum/mensuration-objective-ids.ts` (cf. `stats-objective-ids.ts`), cross-checked by `mensuration-graph.test.ts` (cf. `stats-graph.test.ts`). |
| `interaction-type` | **free-response only**: `item.interactionType == "free-response"` and `supportedInteractionTypes == ["free-response"]`. An explicit multiple-choice request is **rejected** with a clear unsupported-interaction error and is **never silently replaced** by a free-response item. |
| `shape-model-wellformed` | the shape is a **discriminated union** (`RectangleShape`, `RectilinearCompositeShape`, `TriangleBaseHeightShape`) and validation **dispatches by `kind`**: for rectangle/composite kinds the polygon is **closed**, **non-self-intersecting**, **orthogonal** (every edge axis-aligned), components **non-overlapping**; for the triangle kind the axis-aligned base + perpendicular height pair is well-formed (the orthogonal-edge check is **not** run against a triangle). Every kind is **exactly reconstructible** from vertices + given dimensions (§9.4). |
| `closure-agreement` | re-solve via the independent route; the rebuilt `Quantity` from `params` equals the stored answer structurally — **value** as a reduced `Rational` equals `answer.canonical` `{num,den}`, AND the **measure triple** `(dimension, exponent, baseUnit)` equals `answer.measure`. (No merged canonical object is compared, per §4.3.) |
| `quantity-measure-contract` | `answer.measure.dimension`/`exponent` are the pair required by the task (length→1, area→2); `answer.measure.baseUnit ∈ {mm,cm,m}`; **one** `baseUnit` is used throughout the item (no cross-unit conversion, §4); the derived top-level `answer.display` is the canonical formatter output for `(value, baseUnit, exponent)` (§5) — byte-for-byte. (`answer.measure` carries no `display` of its own.) |
| `quantity-dimension-exponent-lock` | **independently enforces the `answer.measure` invariant** `dimension=="length" ⇔ exponent==1` and `dimension=="area" ⇔ exponent==2`, and `type=="quantity" ⇒ answer.measure present`. This is the validator/Ajv-side guarantee of the §4 `if/then` conditional, now **also** enforced offline by the extended `oracle/check_conformance.py` (see note below). |
| `quantity-display-is-ascii` | `answer.display` and every feedback/diagnostic `display` use **ASCII `^2`** for area, never the Unicode `²` (U+00B2). Guarantees byte-stable golden/parity fixtures across locales/encodings. (Unicode `²` is accepted on *input* by §5 but never *stored*.) |
| `no-legacy-units-string` | the legacy free-string `answer.units` (plural) is **absent**; the structured `answer.measure` (singular) object is the only unit carrier. Flags the singular/plural footgun: an author must never populate both. |
| `answer-type-consistency` | `answer.type == "quantity"` (the approved, already-implemented `answerType` enum member, §4.4) and `answer` carries the structured `measure` object; `answer.canonical` validates as a normalized rational `{num, den≥1}` (integer when `den==1`). |
| `answer-solution-agrees` | final `solution.steps[]` result == `answer.display` (`answerSolutionAgrees`). |
| `difficulty-in-band` | `overallBand ∈ TASK_BANDS[task]`; axes are the CLOSED schema enum only (`difficulty-axes-valid`); band recomputed from weighted axes via `bandFromScore` (§11). |
| `provenance` / `version-fields` | `provenanceComplete`, `versionFieldsPresent`. |

> **Offline conformance (extended checker).** `oracle/check_conformance.py` was **extended** with `allOf`/`if`/`then`/`const` support (in addition to its existing `required, type, enum, pattern, properties, additionalProperties(bool), items, minItems, $ref`). Therefore the §4.4 schema diff's conditional obligations — `type:"quantity" ⇒ required:["measure"]` and the `dimension`⇔`exponent` lock — **ARE enforced offline**: the checker does **not** silently ignore the conditional dimension/exponent lock or the `type:quantity ⇒ measure-required` rule. The same extension retroactively enforces the pre-existing `integer`/`exact-rational` `allOf` conditionals, and existing integer/exact-rational items are **unaffected** (they already satisfied the conditionals). These conditional invariants are thus enforced in three places: (a) the extended `check_conformance.py` offline gate, (b) the **bundled Ajv** gate in production, and (c) the independent validator's `quantity-measure-contract` + `quantity-dimension-exponent-lock` checks above.

**B. SVG checks (every diagrammed task)**

| Check name | Assertion |
|---|---|
| `svg-realises-data` | recompute the **canonical greyscale SVG** from `params` via the shared renderer (viewBox `0 0 1000 700`, integer coords via `gridRound`, no runtime trig, root attrs exactly `role="img"` + `<title>`/`<desc>` per the shipped canonical-SVG discipline of `coordinate-lines.ts`/`data-handling.ts`) and assert `== media[0].svg` **byte-for-byte**, Py↔TS identical. |
| `figure-realises-shape` | every drawn shape edge maps to a polygon edge and every dimension label's value equals the corresponding given edge length / base / height (the second-route geometry agrees with `params`). |
| `to-scale-policy-matches-task` | `media[].toScale` matches the task family — `true` for the five direct-calculation tasks (rendered pixel lengths proportional to exact edge lengths under the chosen rational scale; deterministic regeneration if proportions are visually poor), `false` for the three hidden-dimension tasks (normalized not-to-scale diagram, §8.10). |
| `hidden-dimension-not-measurable-from-svg` | on `missing_length_perimeter`, `missing_dimension_area`, `missing_triangle_base_height` the unknown is **not** recoverable by measuring SVG pixel lengths or comparing edge ratios, and the `NOT TO SCALE` banner is present (`not-to-scale-banner-present`). |
| `dimension-rendering-contract` | dimension lines are visually distinct from shape edges; extension lines secondary; axis-aligned arrowheads that **do not resemble polygon vertices**; right-angle and perpendicular-height markers present (and visible in print) where the contract requires; **no label collision** (label boxes disjoint from each other and from edges, dimensions, leaders, and other labels — §8 stress test); each label unambiguously attached to one side; **no duplicate SVG `id`** across a multi-item export; no colour-only meaning, `premium-dark` readable, and 6000×4200 exports preserve exact geometry. All dimension lines (base and altitude) are **axis-aligned**, so all arrowheads use the axis-aligned integer template — no runtime trig (§8.4). |
| `interior-primitives-presentation-only` | every interior primitive (dimension/extension `<line>`, arrowhead `<polygon>`, right-angle/perp markers, measurement-label `<text>`) is presentation-only under the **single** `role="img"` root — none carries its own `role`/`aria-*`, so axe-core sees one labelled image, not many unlabelled graphics nodes (§13). |
| `theme-extension-intact` | the figure uses the **mensuration theme** (theme id `spi-math-mensuration-theme/1`), which `extends "spi-math-cartesian-theme/1"` and *follows the `data-chart-theme` ADDITIVE pattern* (same mechanism) but does **not** depend on `data-chart-theme`; `presentationSvg` composes cartesian + mensuration rulesets only. There is no `data-dimension-theme`. Coordinate-lines and stats outputs remain byte-for-byte unchanged (regression-guarded). |

**C. Role-based answer-leakage checks (every task)**

Leakage is judged **semantically by role/intent**, exactly per the canonical-SVG discipline: raw *given* data that happens to equal the answer is **not** leakage; a dedicated answer/solution annotation in the *student* figure **is**.

| Check name | Assertion |
|---|---|
| `only-given-dimensions-shown` | for `perimeter_composite`, `missing_length_perimeter`, `missing_triangle_base_height` (and every task) the student figure shows **only given** dimensions; the missing side is absent (no label, leader, or marker carries its value as a *dimension annotation*). A coincidental equal *given* edge elsewhere is allowed. |
| `no-result-in-student-figure` | no perimeter/area total appears as an answer/solution annotation in the student render (the computed `Quantity.display` is not printed on the student figure). For inverse tasks the **stated** perimeter/area is given data and may appear (role = given); only the **asked** missing quantity must be absent. |
| `student-a11y-does-not-state-result` | accessibility `spokenMath`/`longDescription` and the media-level `dataTableFallback` for the *student* item state given dimensions only, never the computed answer (§13). |
| `fallback-no-answer-leak` | **role/intent based**, consistent with §14.5: `media[].dataTableFallback` encodes the asked-quantity and given-quantity as **distinct typed slots** (`given[]` vs `asked`); the check asserts no slot whose ROLE is the computed *result* is populated with the answer. A *given* slot that numerically coincides with the answer **passes** (no value-equality false positive). |
| `answer-key-overlay-is-keyed` | the answer-key/solution figure (where the result IS shown) is a separate render variant on a distinct asset id, never the student `media`; the answer overlay never appears in a student export. |
| `answer-key-base-geometry-identical` / `answer-key-overlay-additive-only` | the canonical base-geometry fragment is **byte-identical** between the student and answer-key SVGs and the student annotations are unchanged; the **only** inter-channel difference is the additive answer-overlay group (§8.8). Guarantees a divergent overlay renderer can never silently alter student geometry. (The student SVG is **not** required to be a byte prefix/suffix of the key SVG.) |

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

**E. Free-response diagnostic discipline (every task)** — owner rule N adapted to the free-response-only family

| Check name | Assertion |
|---|---|
| `diagnostic-recompute` | each stored misconception **diagnostic value** (the targeted free-response feedback trigger) is re-derived by running the *same* `MISC.MENS.*` adapter on the recomputed `ctx`; the validator independently reproduces every diagnostic value, and each `rationale`/`feedback` is true for the dataset. (Renamed from the former MC-recompute discipline; the family ships no selectable options, §9.1.) |
| `diagnostic-measure-consistent` | every misconception diagnostic carries a well-formed `(dimension, exponent, baseUnit)` consistent with the §10 unit rule; a diagnostic that differs from the answer only in **value** (not a wrong-unit artefact) is recomputed exactly. |

The required-cell space the review pack must cover is **derived from the distribution report** by the approved reachability-driven **COVERAGE-MATRIX** machinery (stats v1.0.2), reused by name in §14: required cells = every task × **free-response** interaction (the only supported type, §9.1) × reachable difficulty band × realised answer shape (length vs area, integer vs rational, mm/cm/m). The validator's `difficulty-in-band` plus the distribution report prove every declared band is reachable.

### 9.4 Reconstruction route (second-route geometry)

`shape-model-wellformed` and `figure-realises-shape` rebuild the polygon from `params` independently of the generator: vertices from the orthogonal edge walk, missing sides from the closure constraints, then assert the rebuilt polygon is congruent to the stored shape and that the stored SVG renders *that* polygon. This makes `svg-realises-data` and `closure-agreement` mutually reinforcing — the figure, the prompt dimensions, the answer, and the solution all trace to one reconstructed shape.

### 9.5 Free-response-only enforcement (no MC machinery)

Every task in this family is **free-response only**; `supportedInteractionTypes = ["free-response"]` and the `interaction-type` check (§9.3) rejects an explicit multiple-choice request with a clear unsupported-interaction error rather than silently substituting a free-response item. There is therefore no MC-eligibility list, no option set, and no distractor-distinctness machinery. The misconception rules (§10) are deterministic **free-response diagnostics + feedback**: each diagnostic value is independently recomputed by the validator (`diagnostic-recompute`, §9.3), but none becomes a selectable option. A task-pinned **free-response parity fixture** (300 entries) plus explicit per-task tests prove the MC-rejection behaviour for all eight tasks (§9.1).

---

## 10. Misconception and free-response diagnostic registry

All eight tasks in this family are **free-response only** (§9.1, §9.5); the registry therefore contains **free-response diagnostics + feedback rules**, never multiple-choice distractors. The registry is `MISC.MENS.*`, authored as a byte-parity pair (`oracle/spi_oracle/mensuration_misconceptions.py` + `domains/measurement/mensuration-misconceptions.ts`), mirroring the approved `MISC.STAT.*` structure exactly. **This registry is the single source of truth** for diagnosed wrong answers across the solver (worked-solution pitfalls), the free-response checker (targeted diagnostic feedback), and the independent validator (independent recomputation); every other section (§3.1, §6, §7, §14) references these ids **verbatim**, and `mensuration-graph.test.ts` asserts no alternative spelling appears anywhere. Each diagnostic defines its **applicability**, its **exact wrong response or pattern**, the **observable error**, **targeted feedback**, **independent recomputation**, and **collision/inapplicability behaviour**, realised as `{ id, title, formula, description, observableError, feedback, adapter, applicability }`:

- **`formula`** — the wrong rule, in words (internal).
- **`description`** — internal note.
- **`observableError`** — what a marker sees, **no internal symbols**.
- **`feedback`** — the **targeted feedback**, phrased from displayed values, **no internal symbols**.
- **`adapter(ctx) -> Quantity | null`** — deterministic; supports **independent recomputation** (the validator re-runs the same adapter to reproduce every diagnostic value) and returns the wrong dimensional-quantity (with its own `dimension`/`exponent`, since dimension-confusion diagnostics deliberately change the unit), or `null` for its **collision/inapplicability behaviour** — when the rule is inapplicable to the task or when the recomputed result would collide with the correct value.
- **`applicability(ctx) -> bool`** — eligibility predicate; combined with `RULES_BY_TASK` (preference-ordered) exactly as in the stats registry to record which diagnostics apply per task.

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

`ctx` deliberately carries **no `slopingSide`**: the sloping edge of an axis-aligned-base / perpendicular-height triangle has length `sqrt(b²+h²)`, which is irrational for almost all integer/rational `(b,h)` and is therefore unrepresentable as a reduced `Rational` and forbidden by the no-surds / no-Pythagoras rule (§6.1, §12). The "uses a sloping side instead of the perpendicular height" diagnostic is consequently **diagnostic-only** (a free-response pedagogical hint, §10.2): no numeric value is manufactured for it and its `adapter` always returns `null`. `Q(value, dim, exp)` builds a `Quantity` in the item's `baseUnit`; for a wrong-dimension diagnostic the adapter sets `exp`/`dim` to the wrong pair.

### 10.1 Mathematical (value) diagnostics

These are the **eight mathematical diagnostics** of decision K, each a free-response diagnostic that recomputes a wrong `Quantity` from the solver's exact `ctx`:

| Id | Title / formula | observableError (marker-facing) | applicability | adapter → wrong `Quantity` |
|---|---|---|---|---|
| `MISC.MENS.ADDS_TWO_SIDES_RECT` | Adds only two sides of a rectangle · `w+h` | Adds one length and one width instead of going round all four sides. | `perimeter_rectangle`; `missing_length_perimeter` (rectangle form) | `Q(w+h, length, 1)` |
| `MISC.MENS.AREA_WHEN_PERIMETER` | Uses area instead of perimeter · `w*h` | Works out the space inside instead of the distance around. | **rectangle** perimeter only: `perimeter_rectangle`, `missing_length_perimeter` (rectangle form). FR-feedback-only on composites (no single `w,h`). | `Q(w*h, length, 1)` — **kept as a length unit** so the diagnostic is a value error, not a unit error |
| `MISC.MENS.PERIMETER_WHEN_AREA` | Uses perimeter instead of area · `2(w+h)` | Works out the distance around instead of the space inside. | area tasks `area_rectangle`, `area_triangle`, `area_composite`, `missing_dimension_area` | `Q(2*(w+h), area, 2)` |
| `MISC.MENS.ADDS_INSTEAD_OF_MULT_AREA` | Adds instead of multiplying for area · `w+h` | Adds the two side lengths instead of multiplying them. | `area_rectangle`, `missing_dimension_area` | `Q(w+h, area, 2)` |
| `MISC.MENS.FORGETS_TO_HALVE_TRIANGLE` | Forgets to halve a triangle area · `b*h` | Uses base times height but forgets to take half. | `area_triangle`, `missing_triangle_base_height` | `Q(b*height, area, 2)` |
| `MISC.MENS.OMITS_INDENTED_EDGE` | Omits an indented exterior edge from a composite perimeter · `P − indent` | Misses an inward step when going round the shape. | `perimeter_composite`, `missing_length_perimeter` (composite) with ≥1 indent edge | `Q(P − Σ indentEdges, length, 1)` |
| `MISC.MENS.DOUBLE_COUNTS_INTERNAL_EDGE` | Counts an internal decomposition edge · `P + cut` / `A + overlap` | Counts a cut line as part of the outside. | `perimeter_composite`, `area_composite` with an internal decomposition cut | `Q(P + Σ internalDecompEdges, length, 1)` (perimeter) / `Q(A_parts_with_overlap, area, 2)` (area) |
| `MISC.MENS.SUBTRACTS_WRONG_RECT` | Subtracts the wrong rectangle · `A_bound − A_otherPart` | Takes away the wrong piece of the shape. | subtractive `area_composite` | `Q(A_bound − A_otherPart, area, 2)` |

This is the **collision/inapplicability behaviour**: every adapter returns `null` (the diagnostic is skipped) when the recomputed result would collide with `correct`, be out of range, or the applicability predicate fails. `MISC.MENS.AREA_WHEN_PERIMETER` is intentionally emitted **with the correct length unit** and `MISC.MENS.PERIMETER_WHEN_AREA` **with the correct area unit** for the asked task, so each is a genuine *value* diagnostic (a wrong number in the right dimension) rather than a unit artefact. No diagnostic manufactures an arbitrary nearby wrong number: every value is forced by the named wrong rule applied to the solver's exact intermediates.

### 10.2 Unit diagnostics and non-numeric pedagogical pitfall (free-response feedback only)

These are the **four unit diagnostics** and the **one non-numeric pedagogical diagnostic** of decision K. Their `adapter` either recomputes a wrong-unit `Quantity` from the student answer or returns `null`; all surface as **targeted free-response feedback** (matched against a student's submitted `Quantity`) and as **worked-solution pitfalls**.

| Id | Title / formula | observableError | Triggered when the student answer has… |
|---|---|---|---|
| `MISC.MENS.RIGHT_NUMBER_NO_UNIT` | Right number, no unit · bare number | The number is correct but no unit is given. | correct `value`, missing `dimension`/`baseUnit` |
| `MISC.MENS.LINEAR_UNITS_FOR_AREA` | Linear units for area · right number, exponent 1 | Right amount but the unit is a length, not a squared length. | correct `value`, `dimension=length`/`exponent=1` on an area task |
| `MISC.MENS.SQUARE_UNITS_FOR_PERIMETER` | Square units for perimeter · right number, exponent 2 | Right amount but the unit is squared when it should be a length. | correct `value`, `dimension=area`/`exponent=2` on a perimeter task |
| `MISC.MENS.WRONG_BASE_UNIT` | Wrong base unit · right number, wrong length scale | Right amount and right dimension but the base unit (mm/cm/m) does not match the item. | correct `value` and `dimension`/`exponent`, but `baseUnit` differs from the item's `baseUnit` |
| `MISC.MENS.USES_SLOPING_SIDE` | Uses a sloping side, not the perpendicular height (**diagnostic-only, no exact numeric value**) | Uses the slanted edge instead of the upright height. | `area_triangle` — surfaced as a hint/solution pitfall only; `adapter` always returns `null` (the slope length is irrational, §10 preamble) |

This registry is exactly decision K's **thirteen** diagnostics, grouped as: the **eight mathematical (value) diagnostics** of §10.1, the **four unit diagnostics** here (`RIGHT_NUMBER_NO_UNIT`, `LINEAR_UNITS_FOR_AREA`, `SQUARE_UNITS_FOR_PERIMETER`, `WRONG_BASE_UNIT`), and the **one non-numeric pedagogical diagnostic** here (`USES_SLOPING_SIDE`, diagnostic-only because it cannot yield an exact `Rational`). Total: 8 + 4 + 1 = **13**.

The §5 **equivalence checker** drives the four unit diagnostics: it accepts mathematically-equivalent numerical forms *with the correct unit*, distinguishes length from area, rejects a correct number with the wrong dimension, rejects cm when cm² is required (and vice-versa), rejects a correct number carried in the wrong base unit (mm/cm/m), and routes each rejection to the matching `MISC.MENS.*` feedback above — treating the unit **structurally**, never as an unchecked text suffix.

### 10.3 Task → applicable-diagnostic map (`RULES_BY_TASK`)

Keyed on the canonical §1.3 slugs. All eight tasks are free-response only (§9.5), so this map simply records **which diagnostics are applicable per task**, preference-ordered for worked-solution pitfalls and free-response feedback. Mathematical (value) diagnostics from §10.1 lead each list; the unit diagnostics and the non-numeric pedagogical pitfall from §10.2 follow in brackets. No list builds options — there is no multiple-choice machinery in this family.

```
perimeter_rectangle           : ADDS_TWO_SIDES_RECT, AREA_WHEN_PERIMETER,
                                 [SQUARE_UNITS_FOR_PERIMETER, WRONG_BASE_UNIT, RIGHT_NUMBER_NO_UNIT]
perimeter_composite           : OMITS_INDENTED_EDGE, DOUBLE_COUNTS_INTERNAL_EDGE,
                                 [SQUARE_UNITS_FOR_PERIMETER, WRONG_BASE_UNIT, RIGHT_NUMBER_NO_UNIT]
area_rectangle                : ADDS_INSTEAD_OF_MULT_AREA, PERIMETER_WHEN_AREA,
                                 [LINEAR_UNITS_FOR_AREA, WRONG_BASE_UNIT, RIGHT_NUMBER_NO_UNIT]
area_triangle                 : FORGETS_TO_HALVE_TRIANGLE, PERIMETER_WHEN_AREA, ADDS_INSTEAD_OF_MULT_AREA,
                                 [USES_SLOPING_SIDE, LINEAR_UNITS_FOR_AREA, WRONG_BASE_UNIT, RIGHT_NUMBER_NO_UNIT]
area_composite                : SUBTRACTS_WRONG_RECT, DOUBLE_COUNTS_INTERNAL_EDGE, PERIMETER_WHEN_AREA,
                                 [LINEAR_UNITS_FOR_AREA, WRONG_BASE_UNIT, RIGHT_NUMBER_NO_UNIT]
missing_length_perimeter      : ADDS_TWO_SIDES_RECT, OMITS_INDENTED_EDGE, AREA_WHEN_PERIMETER,
                                 [WRONG_BASE_UNIT, RIGHT_NUMBER_NO_UNIT]
missing_dimension_area        : ADDS_INSTEAD_OF_MULT_AREA, PERIMETER_WHEN_AREA,
                                 [WRONG_BASE_UNIT, RIGHT_NUMBER_NO_UNIT]
missing_triangle_base_height  : FORGETS_TO_HALVE_TRIANGLE, PERIMETER_WHEN_AREA,
                                 [USES_SLOPING_SIDE, WRONG_BASE_UNIT, RIGHT_NUMBER_NO_UNIT]
```

The list records applicable diagnostics in preference order; the validator independently re-runs each applicable adapter on the recomputed `ctx` and reproduces every diagnostic value (§10.4). `mensuration-graph.test.ts` asserts `keys(RULES_BY_TASK) == MENSURATION_TASKS` and that every referenced id exists in the registry (no dangling / alternative spellings).

### 10.4 Diagnostic invariants enforced by the independent validator

For every item the validator independently re-runs each applicable rule's `adapter` on the recomputed `ctx` (`diagnostic-recompute`, §9.3) and asserts:

1. **Distinct from correct** — no diagnostic `Quantity` equals the canonical answer (value *and* unit); a rule whose recomputed result would collide with the correct value returns `null` (collision/inapplicability behaviour, §10.1).
2. **Reproduced, not copied** — the validator's recomputed diagnostic set equals the stored set (same independent route as `closure-agreement`); independent recomputation, never a copy of the authored values.
3. **Feedback truthful** — each diagnostic's `feedback` states the wrong rule in terms of displayed dimensions and is true for the dataset.
4. **Unit-consistent** — every diagnostic carries a well-formed `(dimension, exponent, baseUnit)` consistent with the §10 unit rule (`diagnostic-measure-consistent`, §9.3); value diagnostics differ from the answer only in **value**, unit diagnostics only in **unit**.

This keeps the registry the single source of truth for diagnosed wrong answers across the solver (worked-solution pitfalls), the free-response checker (targeted diagnostic feedback), and the independent validator (independent recomputation), with full Python↔TypeScript byte parity on the underlying exact values.


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
| `numericalComplexity` | Magnitude/type of dimensions: single- vs double-digit integers; whether the answer is an exact reduced **rational** (the two triangle tasks — `area_triangle` halving and `missing_triangle_base_height`) vs an integer; number of dimension values to combine. |
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

Weights sum to `1.00`. The objective difficulty ranges, the per-task structural floors, these difficulty-axis weights, the supported interactions (**free-response only**), and the answer shapes all derive from **one machine-readable source of truth** (a single versioned descriptor under `core/difficulty` / `core/curriculum`), from which both the spec tables here and the §14 review-pack expectations are generated — so the two can never drift. Indicative landing bands (final ranges fixed by the report); tasks are named by the **canonical §1.3 `MENSURATION_TASKS` slugs** so the band table keys to the same single source as the generator dispatch, `OBJECTIVE_BY_TASK`, and the §14 COVERAGE-MATRIX `cell:<task>:…` tokens:

| Task slug (§1.3) | Typical structural profile | Indicative band |
| --- | --- | --- |
| `perimeter_rectangle` | 1–2 steps, density low | 1–2 |
| `area_rectangle` | 1 step, density low | 1–2 |
| `area_triangle` | 2 steps incl. halving (rational answers ↑) | 2–3 |
| `perimeter_composite` (L-shape) | missing-side derivation, high density | 2–4 |
| `area_composite` | split/sum or subtract, agreement check | 3–4 |
| `missing_length_perimeter` | inverse, interpretation ↑ | 2–3 |
| `missing_dimension_area` | inverse division (exact integer by construction) | 2–3 |
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
- **Missing rectangle dimension from area** (`missing_dimension_area`): the area is sampled only as a `givenSide`-multiple, so the division `area ÷ givenSide` is an **exact integer by construction** (`givenSide ∣ area`); any seed that would not divide exactly is rejected. The answer is integer-only — `missing_dimension_area` never produces a rational.
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

- every **task** (the only supported interaction is **free-response**: `cell:<task>:inter:free-response`),
- every **reachable difficulty band** (`cell:<task>:band:<1..5>`), and
- every **realised answer shape** (`cell:<task>:shape:<token>`),

exactly as stats does — but the mensuration **answer-shape token is the structured dimensional quantity**, not the bare schema `answer.type`. Every item in this family answers with the single new `answer.type = "quantity"` (the one approved enum member of §4; the structured unit lives in the **separate sibling `answer.measure` object** of §4.3, never folded into `answer.canonical`, which stays the bare Rational `{num,den}`). The schema `answer.type` alone therefore cannot distinguish a length from an area or an integer from a rational. The mensuration `_cell_tokens()` composes the shape token from the **dimensional contract** (the `answer.measure` triple plus the `answer.canonical` denominator):

```
shape = "<dimension>:<exponent>:<numberKind>:<baseUnit>"
  dimension  ∈ {length, area}            # answer.measure.dimension
  exponent   ∈ {1, 2}                     # answer.measure.exponent; 1 ⇔ length, 2 ⇔ area (the §4 invariant)
  numberKind ∈ {integer, rational}        # answer.canonical.den == 1 vs den > 1
  baseUnit   ∈ {mm, cm, m}                # answer.measure.baseUnit
```

So `cell:area_rectangle:shape:area:2:rational:cm` and `cell:perimeter_rectangle:shape:length:1:integer:m` are distinct required cells. This makes the owner's "length AND area answers" and "integer AND rational answers" first-class **cells the builder can FAIL on**, not soft qualitative notes. All of these required cells — objective ranges, task structural floors, difficulty-axis weights, supported interactions (**free-response only**), and answer shapes — derive from the **single machine-readable source of truth** of §11/§14 (the same artifact the spec tables are generated from), so the review-pack expectations and the spec never diverge. Per §6.5/§7.2 the *rational-valued* answer shapes are only reachable on the **triangle and missing-dimension tasks** (rectangle and composite edge lengths are integer-valued, so `b×h÷2`, an exact-area missing dimension, or a rational missing length are where `den > 1` genuinely arises); the distribution report records exactly which `(task, dimension, numberKind, baseUnit)` cells exist, and the builder treats a never-realised combination (e.g. `cell:area_rectangle:shape:area:2:rational:*`) as **non-existent — documented in the matrix, not a `MISSING`** (the `note: "unreachable per distribution report (no items)"` convention). The required cell count `requiredCells` is computed as `sum(len(interactions)+len(bands)+len(shapes))` over the reachability map and asserted equal to the matrix-derived count (the `required-token-count-derived-from-matrix` assertion) — it is never a literal.

### 14.2 Greedy set-cover, task-pinned gathering, builder FAILS on any missing reachable cell

Stage 1 gathers candidates task-pinned across a bounded seed window (`GATHER_SEEDS` per task), so rare reachable cells (e.g. a band-1 `area_triangle`, a `missing_triangle_base_height` whose §12 exact-answer gate fires only occasionally) always have candidates. Stage 2 is the same greedy set-cover: repeatedly pick the candidate adding the most still-uncovered **required** tokens, reusing one exemplar across several cells where it is a genuine exemplar. The builder's exit code is `0` only when `required_cells ⊆ covered` **and** every selected item is machine-valid **and** `len(required_cells) == derived_required_cells`; any missing reachable cell prints `MISSING COVERAGE` and returns non-zero.

Every task in this family is **free-response only** in v1.0.0 — there is no multiple-choice task and no MC interaction cell anywhere. The pack proves, per task, that the **free-response diagnostics and feedback** of §10 are realised (the unit-dimension hints and every task-eligible value-rule pitfall surface through the same adapter the validator recomputes), and it additionally proves the **unsupported-MC-request rejection** test passes for every task: a request for a multiple-choice rendering of any mensuration task is rejected, because multiple-choice is not a supported interaction for this family.

### 14.3 Explicit coverage matrix + the five blocking coverage tests (reused by name)

The pack emits the same two coverage structures as stats: a per-task **`coverageMatrix`** (`interactions` / `bands` / `shapes`, each `{reachable, hasExemplar, exemplarSeed, note}`) and a flat **`coverageCells`** list of every realised `(task, interaction, band, answerShape, seed)`. The Markdown renders the matrix as the same `| Task | Interactions | Bands | Answer shapes |` table with `→seed` / `→MISSING` / `=n/a` cells.

The blocking coverage tests are the **stats v1.0.2 set, reused verbatim**, retargeted to the mensuration pack — these are the five named gates the brief requires, plus the two top-level honesty flags they assert against:

| Coverage test | Asserts |
| --- | --- |
| `every-reachable-task-band-covered` | every `cell:<task>:band:<b>` that the distribution report marks reachable has an exemplar seed. |
| `every-supported-interaction-covered` | the only supported interaction is **free-response**; every reachable `cell:<task>:inter:free-response` has an exemplar (there are no MC interaction cells at all). |
| `every-task-answer-shape-covered` | every realised dimensional-quantity shape token (length/area × integer/rational × mm/cm/m, per the §14.1 composition) has an exemplar. |
| `coverage-summary-matches-records` | `summary.coveredCells` / `coverageCells` agree with the actual `records[]` (no double-count, no phantom cell). |
| `no-false-full-coverage-claim` | `summary.allCovered == (missingCoverage == [])` — the honest full-coverage flag can never be `true` while a required cell is missing. |

`summary.allCovered` and `summary.allValid` are the two top-level honesty flags; `requiredCells == derivedRequiredCells` (the reachability-derived count, never a literal) is asserted inside the builder's exit gate and surfaced in the summary. The manifest of §15 hash-attests the resulting pack so a silent regeneration that drops a cell fails CI.

### 14.4 Owner-mandated coverage dimensions (additional tokens beyond the cells)

On top of the systematic cells, `_required_tokens()` adds the explicit owner checklist as additional required tokens, each surfaced by `_features()` and FAIL-on-missing in the same set-cover:

| Owner dimension | Required token(s) | Source feature |
| --- | --- | --- |
| mm / cm / m contexts | `unit:mm`, `unit:cm`, `unit:m` | `dataset.baseUnit` (= `answer.measure.baseUnit`) |
| length AND area answers | `dim:length`, `dim:area` | `answer.measure.dimension` |
| exponent 1 AND 2 | `exp:1`, `exp:2` | `answer.measure.exponent` (1 ⇔ length, 2 ⇔ area) |
| integer AND rational answers | `num:integer`, `num:rational` | `answer.canonical.den` |
| every diagnostic rule realised | `diag:<rule>` for each `MISC.MENS.*` rule of §10 | the rule's adapter/feedback is surfaced on an eligible item |
| all shape kinds | `shapekind:rectangle`, `shapekind:composite`, `shapekind:triangle` | the canonical §6 shape model's kind |
| additive AND subtractive composite decompositions | `decomp:additive`, `decomp:subtractive` | the stated decomposition sums parts vs subtracts a part |
| rectangles in different orientations | `orient:landscape`, `orient:portrait`, `orient:square` | `width` vs `height` of the bounding rectangle |
| several L-shape configurations | `lshape:notch-tl`, `…-tr`, `…-bl`, `…-br` | notch corner of the rectilinear polygon |
| composites with missing exterior lengths | `composite:missing-exterior` | a derived (non-given) exterior edge present |
| triangle areas with visible perpendicular heights | `triangle:visible-height` | the perpendicular-height marker primitive is emitted |
| direct-task to-scale figures | `scale:direct-to-scale` | a direct-calculation task rendered to-scale |
| missing-dimension NOT-TO-SCALE figures | `scale:missing-not-to-scale` | a hidden-dimension task with the "NOT TO SCALE" banner |
| student vs answer-key renderings | `render:student-figure`, `render:answer-key` | the §8 student / answer-key copies |
| label-collision stress tests | `collision:dense-dims`, `collision:short-edge` | many dimension labels / a short edge forcing leader offset |
| monochrome + two-column print | `render:print`, `render:two-column` | the `print` mode export + the worksheet two-column layout |
| premium + premium-dark + accessible modes | `render:premium`, `render:premium-dark`, `render:accessible` | the themed audit copies |
| a 6000×4200 export | `export:6000x4200` | the materialised raster export hash |
| answer ABSENT from student diagram | `answer-free:student-figure` | the §8 student/answer-key split is exercised |
| missing-length / missing-dimension determinacy | `det:unique-answer` | the §12 exact-answer gate fired and is recorded |

The mensuration analogues of stats' endpoint honesty checks are §12's degeneracy gates (no zero/negative derived edge; missing-quantity answers exact-only), each recorded as a covered token so the pack proves the gate is **exercised**, not merely declared.

### 14.5 Student diagram BESIDE answer-key overlay, and the explicit answer-absence tests

The pack and the visual audit render, for every figure-bearing item, the **student figure beside its answer-key overlay** — the two products of the §8 single-shape model: the student `media[0].svg` (given dimensions only, no missing side, no result) and the answer-key copy (the same figure plus the derived edge, the perpendicular-height value, the decomposition split lines, and the final perimeter/area annotation). The answer-key copy shares the student figure's **base geometry identically** and then layers an **additive overlay** of answer-role elements only; §8's `answer-key-base-geometry-identical` check enforces that the base shape geometry is the same in both copies, and `answer-key-overlay-additive-only` enforces that the overlay renderer never alters student geometry, only adds answer-role elements. This is the mensuration analogue of the coordinate-lines student/solution render split and reuses the §8 role-based answer-leakage discipline.

**To-scale vs not-to-scale.** Direct-calculation tasks (`perimeter_rectangle`, `perimeter_composite`, `area_rectangle`, `area_triangle`, `area_composite`) may be rendered **to-scale**. The three hidden-dimension tasks (`missing_length_perimeter`, `missing_dimension_area`, `missing_triangle_base_height`) render a **normalized NOT-TO-SCALE** student diagram carrying a visible "NOT TO SCALE" banner, so the hidden dimension is **not recoverable by measuring the SVG**. The pack therefore covers both direct-task to-scale examples (`scale:direct-to-scale`) and missing-dimension not-to-scale examples (`scale:missing-not-to-scale`), per §14.4.

Two explicit, **blocking** answer-absence tests are recorded per figure item (the owner's "EXPLICIT tests proving the answer is ABSENT from student diagrams"), reusing the semantic role/intent leakage model (raw given data equal to the answer is **not** leakage; a dedicated answer/solution annotation in the student figure **is**):

- `no-result-in-student-figure` — the student SVG carries no element whose render role is the computed perimeter, area, or a missing/derived length: no dimension line on a non-given edge, no area/perimeter label, no perpendicular-height value, no decomposition annotation. A given side that coincidentally equals the answer passes (`raw-data-equality-is-not-leakage`); a dedicated answer-role annotation fails.
- `student-a11y-does-not-state-result` — the student `media[0].longDescription` and the `media[0].dataTableFallback` give the shape, the given dimensions, and the units (per §13, the fallback lives on `media[]`, never on the item-level `accessibility` object), but never the perimeter/area/missing length. The fallback encodes the **asked quantity and each given/stated quantity as distinct role-keyed slots** (§13.2), so the check is role-based: no slot whose role is the *computed result* appears in the student copy; a stated given quantity that numerically coincides with the answer passes. The result text lives only in the answer-key/solution copy.

A pinned positive/negative pair is recorded exactly as stats pins its `no-statistic-in-svg` cases: an L-shape whose given exterior edge numerically equals its (different-role) area value **passes**; a student figure carrying a perimeter label **fails**.

### 14.6 Per-item record contents

Each `records[]` entry (and its Markdown section) shows the full audit trail the owner enumerated:

- **objective** (`objectiveId`), **task**, **interaction** (`interactionType`, always `free-response`), **answer shape + unit** (the `quantity` contract: `answer.measure.{dimension,exponent,baseUnit}` + integer/rational from `answer.canonical.den`), **seed**, **params**;
- the **canonical shape model** — the §6 polygon (ordered integer/rational vertices, edge list with given/derived flags, decomposition rectangles for composites, the triangle base+height with the perpendicular foot) — echoed verbatim as the single source the figure, prompt, answer, solution, misconceptions, a11y, and validation all derive from;
- the **prompt** (`prompt.instruction` + typed `prompt.blocks` with the figure cited via a `media-ref` block);
- the **figure** (canonical student SVG) **beside the answer-key overlay**;
- the **canonical answer** — `answer.display`, `answer.canonical = {num,den}` (the bare Rational, rationals serialised as `{num,den}`), and the sibling `answer.measure = {dimension, baseUnit, exponent}` (display is derived and lives only at top level — `answer.display` — never duplicated inside `measure`);
- the **worked solution** (`solution.steps[{number,transformation,intermediateResult}]`, with the composite area shown by BOTH the shoelace route and the stated decomposition, and their agreement asserted);
- the **misconception calculations** — every eligible `MISC.MENS.*` adapter value with its `observableError`/`feedback` (displayed-value language only). All eight tasks are **free-response**, so every item surfaces **free-response diagnostics and feedback**: the targeted unit-dimension hints of §10.2 (`MISC.MENS.LINEAR_UNITS_FOR_AREA`, `MISC.MENS.SQUARE_UNITS_FOR_PERIMETER`, `MISC.MENS.RIGHT_NUMBER_NO_UNIT`, `MISC.MENS.WRONG_BASE_UNIT`) plus the task-eligible value-rule pitfalls, each recomputed through the same adapter the validator runs. **`MISC.MENS.USES_SLOPING_SIDE` appears only as a free-response pedagogical hint, never as a numeric value** — its `adapter` returns `null` because a perpendicular-height triangle's slant length is `√(b²+h²)`, irrational for almost all integer/rational `(b,h)` and therefore unrepresentable as a reduced Rational under the no-surds rule (§12.4); the canonical mathematical diagnostics are `ADDS_TWO_SIDES_RECT`, `AREA_WHEN_PERIMETER`, `PERIMETER_WHEN_AREA`, `ADDS_INSTEAD_OF_MULT_AREA`, `FORGETS_TO_HALVE_TRIANGLE`, `OMITS_INDENTED_EDGE`, `DOUBLE_COUNTS_INTERNAL_EDGE`, `SUBTRACTS_WRONG_RECT`; the unit diagnostics are `LINEAR_UNITS_FOR_AREA`, `SQUARE_UNITS_FOR_PERIMETER`, `RIGHT_NUMBER_NO_UNIT`, `WRONG_BASE_UNIT`; the pedagogical diagnostic is `USES_SLOPING_SIDE` (FR-hint only, adapter null);
- the **accessibility** representation (`accessibility.spokenMath` + `media[].dataTableFallback` object: the vertex/edge/dimension table);
- the **difficulty axes + band** (`difficulty.axes` over the closed enum, `difficulty.overallBand`);
- the **validation checks** run — the canonical `validate()` `checks[].name` vocabulary fixed in §9.2/§9.3: `shape-model-wellformed`, `polygon-closure`, `side-orientation`, `missing-side-derivation`, `perimeter-from-exterior-boundary`, `area-by-polygon`, `area-by-stated-decomposition`, `area-methods-agree`, the §4/§9 measure-contract checks (`quantity-measure-contract`, `quantity-dimension-exponent-lock`, `answer-type-consistency`, `no-legacy-units-string`, `quantity-display-is-ascii`), the §8 dimension-rendering checks (`svg-realises-data`, `closure-agreement`, `answer-key-base-geometry-identical`, `answer-key-overlay-additive-only`), and the §14.5 answer-absence checks (`no-result-in-student-figure`, `student-a11y-does-not-state-result`) — referenced by the exact same strings the validator emits, no per-section renaming;
- the **reproduction command** (`python -c "import sys;sys.path.insert(0,'oracle/spi_oracle');import mensuration as m;print(m.serialize(m.generate(<seed>, <cfg>)))"`).

### 14.7 Visual audit + browser verification

`docs/review/mensuration_visual_audit.html` reuses the stats audit harness: it renders every pack figure through the **mensuration dimension-rendering theme extension** of §8/§16 — a versioned extension that **`extends: "spi-math-cartesian-theme/1"` and FOLLOWS the `data-chart-theme` additive PATTERN** (same per-root `cx-figure` isolation, same `presentationSvg()`/`exportSvg()` contract, new `--cx-*` variables + one additive ruleset) **but does not depend on `data-chart-theme`** (its chart/pictogram primitives are not pulled in) — in all four modes: **premium**, **premium-dark**, **accessible** (CVD-safe), **print** (monochrome authoritative), via `presentationSvg()`, plus the self-contained **6000×4200** copies via `exportSvg()`. The audit includes the owner's stress galleries: **label-collision** cards (dense dimension stacks, short-edge leader offsets, adjacent-label minimum-gap), the **two-column print** worksheet layout, monochrome legibility of dimension lines vs shape edges vs extension lines, right-angle and perpendicular-height markers under greyscale, and **student-beside-answer-key** pairs. A `mensuration_browser_verification.json` records the live-Chromium re-confirmation (four modes coexist on one page with distinct computed strokes, the dimension-line/edge contrast holds, the 6000×4200 raster hash), exactly as the stats browser verification does. The audit and verification JSON are hash-attested in the manifest (§15).

### 14.8 Quantity-checker review matrix

Beyond the coverage cells, the pack emits a dedicated **quantity-checker review matrix** that proves the shared dimensional-`quantity` checker (`core/answer-checking/quantity.ts` / `oracle/spi_oracle/quantity.py`, §16.3) accepts and rejects exactly as the contract requires. For a representative answer in each `(dimension, exponent, baseUnit)` family, the matrix records a pass/fail outcome for each of the following submissions, and the builder FAILS if any required row is absent:

| Submission | Required outcome |
| --- | --- |
| Equivalent numeric value **with the correct unit** | accepted |
| Bare correct value, **no unit** | rejected (missing-unit) |
| Correct value, **wrong exponent** (e.g. `cm` where `cm^2` is required) | rejected |
| Correct value, **wrong dimension** (length where area required) | rejected |
| Correct value+exponent, **wrong base unit** (e.g. `m` where `cm` declared) | rejected (no cross-unit conversion) |
| **Incorrect value** with the correct unit | rejected |

There is **no cross-unit conversion** in v1.0.0 — a value in a different base unit is rejected, not silently converted. These rows reuse the same equivalence checker the validator runs, so the matrix is a behavioural proof of the checker, not a re-implementation.

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
3. Mirror in **TypeScript** (`domains/measurement/mensuration.ts`) using `core/exact-math/rational.ts`, `core/seeded-random/mulberry32.ts`, `core/difficulty/band.ts`, the shared `core/answer-checking/quantity.ts` unit checker (§16.3), and the additive cartesian-theme-pattern dimension-rendering extension (§16). The canonical SVG and `params`/`answer` (with its free-response diagnostics) are **byte-identical Py↔TS**; the themed/exported copies are TypeScript-only.
4. `validate(item)` recomputes every figure and answer by a second route and runs the §9 composite validators, the §4/§9 measure-contract checks (including `quantity-dimension-exponent-lock`, which enforces the `dimension⇔exponent` lock, and `answer-type-consistency`, which enforces the `type:"quantity" ⇒ measure required` binding), and the §8 dimension-rendering plus §14.5 answer-absence checks. These same conditional rules are also enforced in runtime Ajv and in the extended offline conformance checker (§15.3), so they are never silently skipped on any path.

### 15.3 Gates (all blocking before any approval)

| Gate | Spec |
| --- | --- |
| Golden | frozen `oracle/golden/mensuration.golden.json`, Py-authored, TS-verified byte-identical (canonical item JSON + canonical dimensioned SVG). |
| Parity | a **300-entry task-pinned FREE-RESPONSE parity fixture**, `mensuration.parity.json` (no second interaction — free-response is the only supported interaction); independent Python + TypeScript output **byte-identical** for canonical item JSON + canonical SVG. Plus explicit tests proving an **unsupported multiple-choice request is rejected for every task**. Theme/export copies are TS-only and excluded from parity. |
| Schema | the single additive `schemas/question-item.schema.json` extension — new `answer.type` enum member **`"quantity"`** + the sibling `answer.measure` object — is **approved and already applied** to the schema. It validates under the **bundled Ajv** (which evaluates the `if/then`/`allOf` dimension⇔exponent lock and the `type:"quantity" ⇒ required:["measure"]` binding) **and** under the **extended `oracle/check_conformance.py`**, which now supports `allOf`/`if`/`then`/`const` and therefore **enforces these conditionals offline** (existing integer/exact-rational items unaffected). The conditional rules are thus enforced on every path: runtime Ajv, the extended Python/offline conformance, import, bank storage, migration, and export assembly, plus the independent validator (`quantity-measure-contract`, `quantity-dimension-exponent-lock`, `answer-type-consistency`, §4.2/§9.2). The extension is back-compatible: no existing `answer.type` changes, so every approved family's items stay schema-valid byte-for-byte. |
| Sweep | `SPI_SWEEP = 10000`: `invalid: 0`; **every declared band reachable before fixtures freeze** (the distribution report is the reachability proof); the **free-response diagnostics are realised** (every eligible `MISC.MENS.*` rule surfaces its feedback through the adapter the validator recomputes) and the **unsupported-MC-request rejection test passes for every task**; the §12 exact-answer / non-degeneracy gates fire (no zero/negative derived edge, missing-quantity answers exact only); **reproducibility re-check** (re-running a seed reproduces byte-for-byte). |
| Distribution | `mensuration_distribution.json` emitted + integrity-checked; it is the authoritative reachability artifact the §14 coverage matrix derives from. |
| Composite-validity | §9 polygon closure / non-self-intersection / orthogonality / missing-side derivation / exterior-boundary perimeter / shoelace area / decomposition area / **both-area-methods-agree** all pass on every swept composite. |
| Style-isolation | the per-root `cx-figure` isolation + materialised-export tests pass on the additive dimension-rendering extension; a theme-completeness test (mirroring `data-chart-theme.test.ts`) asserts **every** declared `--cx-*` variable has a value in **all four** modes; **coordinate-lines and stats output stay byte-for-byte unchanged**. |
| a11y | axe gate over rendered items: **0 critical / 0 serious, WCAG AA**; all interior dimension/extension/arrowhead/marker primitives are presentation-only under the **single `role="img"` root** (so axe sees one labelled image, not many unlabelled graphics nodes); `media[].dataTableFallback` + non-colour indicators (greyscale-authoritative dimension lines, right-angle markers) present. |
| Exports | worksheet / answer-key / solutions + offline KaTeX render; **bank-json round-trip lossless**; **6000×4200** colour + print exports self-contained. |
| Integrity + graph | the blocking artifact-integrity tests (manifest + **SHA-256** over every artefact, Py + TS) and the bespoke graph test pass. |
| Coverage | the §14 builder returns `0` (all reachable cells covered, `allCovered: true`, `requiredCells == derivedRequiredCells`) and the **five named coverage tests** of §14.3 pass. |
| Approved-generator regression | arithmetic / geometric / linear / angle-geometry / coordinate-lines / stats output **byte-for-byte UNCHANGED**. |

The build is **authorized oracle-first now** (implementation is not awaiting a further approve/reject), and the full verification list that must pass before the review pack is produced is: schema migration / back-compat; runtime Ajv; the extended Python/offline conformance; quantity parser/checker parity; Py↔TS canonical-item parity; canonical SVG parity; the **300-entry FR parity fixture**; the **unsupported-MC tests per task**; the **10k stability + reproducibility** sweep; shape-specific invariants; decomposition / shoelace agreement; hidden-dimension leakage; overlay-channel isolation; unit-feedback; accessibility + browser; print + premium; the **6000×4200** export; artifact integrity; and approved-family fixture-drift. Each maps onto a blocking gate above.

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
| Canonical-SVG discipline (hand-rolled, `viewBox 0 0 1000 700`, integer coords via `gridRound` over exact `Rational`/`Fraction`, no runtime trig, byte-identical Py↔TS, `role="img"` + `aria-label="<alt>"` with `<title>`/`<desc>` first children — the **shipped** coordinate-lines/stats serializer shape, NOT `aria-labelledby` — data-table fallback, greyscale-authoritative, role-based answer-leakage) | coordinate-lines / stats renderer contract | The polygon + dimension-line figures; the validator recomputes the SVG from `params` byte-for-byte (`svg-realises-data`) and recomputes the answer by a second route (`closure-agreement`); answer-leakage is the §14.5 semantic role/intent check; the answer-key copy shares the student figure's base geometry identically and adds an additive answer-role overlay (`answer-key-base-geometry-identical` + `answer-key-overlay-additive-only`). |
| Per-root style isolation + render modes + export (`cx-figure`, one common ruleset, premium / premium-dark / accessible / print, `presentationSvg()`/`exportSvg()`, materialised **6000×4200** S=6 export) | `core/visual-style/cartesian-theme.{json,ts}` | Every figure + the visual audit. **TypeScript-only** (no Python theme mirror); byte-parity is required of the canonical SVG + params/answer (and its free-response diagnostics), not the themed/export copies. |
| **Additive-extension PATTERN** (REUSE the base contract, ADD family primitives as new `--cx-*` variables + one additive ruleset, base output stays byte-for-byte unchanged) | `core/visual-style/data-chart-theme.{json,ts}` | The mensuration dimension-rendering primitives are added **the same additive way** as data-chart-theme adds its chart primitives (see §16.2) — but the mensuration extension itself `extends "spi-math-cartesian-theme/1"`, exactly as data-chart-theme does, and does **not** depend on data-chart-theme; coordinate-lines + stats figures stay byte-for-byte unchanged. |
| Exact arithmetic | `core/exact-math/rational.ts` + Python `fractions.Fraction` | All perimeters/areas/missing lengths as exact integers or reduced `{num,den}`; `answer.canonical` is the bare Rational; every diagnostic-value-vs-key and distinctness comparison is reduced-Rational equality. |
| Seeded RNG (byte-identical Py/TS, deterministic redraw order) | `core/seeded-random/mulberry32.ts` + `oracle/spi_oracle/seeded_random.py` | The seeded RNG drives the **deterministic shape draw only** (no MC); the call **order** is the parity contract. |
| Difficulty banding | `core/difficulty/band.ts` (`bandFromScore`, `round3`) | Weighted closed-enum axes → band, clamped to each objective's declared range; reachability proven by the distribution report. |
| Misconception engine | `MISC.<PREFIX>.*` registry shape (Py + byte-parity TS), `RULES_BY_TASK` eligibility, adapter `(ctx) -> wrong value | null`, validator independently recomputes each diagnostic value | The `MISC.MENS.*` registry (§10) plugs into this engine unchanged; the validator re-derives every diagnostic value through the same adapter; the adapter returns `null` where a rule is FR-feedback-only (`USES_SLOPING_SIDE`, whose value would be irrational). All eight tasks are free-response, so the diagnostics surface as feedback/hints, not as MC options. |
| **Review-pack reachability COVERAGE-MATRIX machinery** + the five blocking coverage tests | `oracle/make_review_pack_data_handling.py` (stats v1.0.2, `DECISION_LOG.md` #48) | Reused verbatim (§14): required cells derived from the distribution report, greedy set-cover, builder FAILS on any missing reachable cell, explicit matrix + flat cells + honest `allCovered`. |
| Manifest / artifact-integrity / style-isolation tooling | `oracle/make_*_manifest.py` (SHA-256 over every artefact, Py + TS integrity tests), `*-style-isolation.test.ts` | `oracle/make_mensuration_manifest.py` is a direct adaptation; SHA-256 over golden/parity/distribution/review-pack/audit/browser-verification/objectives/oracle/misconceptions/theme + raster export hashes. |
| Offline conformance (extended) | `oracle/check_conformance.py` | Live mensuration items added to the §4f-style loop and asserted to **conform** (enum membership of `"quantity"`, `required`, `additionalProperties:false`). The checker has been **extended with `allOf`/`if`/`then`/`const` support**, so the measure-shape invariants (the `type:"quantity" ⇒ measure required` binding and the `dimension⇔exponent` lock) are **enforced offline here too** — alongside runtime Ajv and the independent validator (§15.3); existing integer/exact-rational items are unaffected. |
| Delivery harness | review-pack/audit generators, offline HTML/JSON exporters (worksheet / answer-key / solutions, offline KaTeX), bank-json round-trip, axe gate, SDK registry + `approvalStatus` lifecycle | Driven family-specifically; mechanism unchanged. |

### 16.2 Mensuration-specific — new, this family only

| New asset | What it is |
| --- | --- |
| **Canonical polygon / dimension data model** (§6) | The single source per item: ordered integer/rational vertices, an edge list with `given`/`derived` flags and orientation, decomposition rectangles for composites, the triangle base + perpendicular height with the foot point, the per-edge dimension-label placement (side, offset, leader). Everything — figure, labels, prompt, answer, solution, misconception calcs, a11y, validation — derives from it. |
| **Dimensional-quantity answer contract + unit checker** (§4/§5) | The `answer.type = "quantity"` shape: `answer.canonical = {num,den}` (the exact Rational, unchanged from the exact-rational contract) plus a **separate sibling** `answer.measure = {dimension: length\|area, baseUnit: mm\|cm\|m, exponent: 1\|2}` (display is derived and lives only at top level, `answer.display`; it is never duplicated inside `measure`). For `type="quantity"` a unit is **always required** — there is no opt-out. The structural equivalence checker accepts equivalent numeric forms with the correct unit; distinguishes length from area; rejects a right number with the wrong dimension; rejects cm where cm² is required; rejects a wrong base unit (no cross-unit conversion); gives targeted missing/incorrect-unit feedback; unit meaning is structural, never an unchecked text suffix. **This is the headline new contract — see §16.3.** |
| **Dimension-rendering theme extension** (§8) | A versioned extension that **`extends "spi-math-cartesian-theme/1"`** and follows the `data-chart-theme` additive pattern, adding mensuration primitives as new `--cx-*` variables (dimension line, extension line, arrowhead, edge, right-angle, perpendicular-height, measurement label, cut/decomposition line, answer-overlay) + one additive `.cx-figure`-scoped ruleset — distinct from shape edges, with collision-avoiding label placement, **each variable defined in all four modes** (theme-completeness test). All dimension lines (base and altitude) are axis-aligned, so every arrowhead uses the axis-aligned integer template and no runtime trig is needed; the only slant edge (a triangle hypotenuse) carries no dimension line. The id-free inline-geometry discipline (no `<pattern>`/`url(#)`) and byte-identical Py↔TS canonical fragment are reused; **coordinate-lines + stats output stay byte-for-byte unchanged.** |
| **Composite-shape validators** (§9) | The family-specific checks under the §9.2 canonical name table: `polygon-closure`, `side-orientation`, `missing-side-derivation`, `perimeter-from-exterior-boundary`, `area-by-polygon` (shoelace over integer/rational vertices), `area-by-stated-decomposition` (the stated split), and `area-methods-agree` (shoelace ≡ decomposition) — plus the §12 degeneracy gates (no zero/negative derived edge; missing-quantity answer exact only). |
| **`MISC.MENS.*` registry** (§10) | The owner-mandated diagnostic rules, each `{misconceptionId, domain:"measurement", description, observableError, feedback, formula, adapter, applicability}` + `RULES_BY_TASK`, byte-parity Py/TS. These are **free-response diagnostics** (there is no MC, so no manufactured value distractors): the canonical mathematical diagnostics are `ADDS_TWO_SIDES_RECT`, `AREA_WHEN_PERIMETER`, `PERIMETER_WHEN_AREA`, `ADDS_INSTEAD_OF_MULT_AREA`, `FORGETS_TO_HALVE_TRIANGLE`, `OMITS_INDENTED_EDGE`, `DOUBLE_COUNTS_INTERNAL_EDGE`, `SUBTRACTS_WRONG_RECT`; the unit diagnostics are `LINEAR_UNITS_FOR_AREA`, `SQUARE_UNITS_FOR_PERIMETER`, `RIGHT_NUMBER_NO_UNIT`, `WRONG_BASE_UNIT`; the pedagogical diagnostic is `USES_SLOPING_SIDE` (FR-hint only; adapter returns `null`). The registry is the **sole** id source, asserted by the graph test ("no alternative spellings appear anywhere"). |
| **Curriculum objectives + strand** | The eight `SPI.MIDDLE.MEAS.*` objective files and the new `mensuration` strand; the single-source `OBJECTIVE_BY_TASK` map keyed by the §1.3 `MENSURATION_TASKS` slugs. |
| **The review pack + audit content** | `oracle/make_review_pack_mensuration.py`, the visual audit, distribution report, browser verification, and manifest of §14 — including the dimensional-quantity shape tokens, the student-beside-answer-key galleries, the label-collision stress cards, and the answer-absence tests. |

### 16.3 The headline decision — where the unit / dimensional-quantity contract lives

**Decision: the dimensional-quantity answer contract and its unit checker are built in SHARED CORE, not family-local** — namely `core/answer-checking/quantity.ts` (+ the Python mirror `oracle/spi_oracle/quantity.py`) and the structured `quantity` value shape — with mensuration as their **first consumer**.

Rationale:

- The contract is a **measurement-domain primitive**, not a mensuration accident. Every future Measurement family (unit conversion, mass/capacity/time, compound units, rate) will answer in dimensioned quantities, and the cm↔m conversion the brief explicitly defers is a **later objective that extends this same contract** — placing it in shared core means that extension is a versioned widening of one checker, not a second parallel implementation.
- It matches the established platform pattern: exact-rational checking, the Mulberry32 stream, and the difficulty banding all live in shared core and are reused by every family; the unit checker belongs in the same tier.
- The v1.0.0 surface is kept deliberately narrow to avoid premature generality: the shared module exposes only what mensuration needs — `dimension ∈ {length, area}`, `exponent ∈ {1, 2}`, `baseUnit ∈ {mm, cm, m}`, exact-rational value, structural equivalence within **one** declared base unit (**no cross-unit conversion in v1.0.0**). The conversion graph, additional dimensions (mass/time/capacity), and compound units are **out of v1.0.0 scope and deferred**, added later as a backward-compatible widening of the shared contract.

**Schema impact — APPROVED AND ALREADY IMPLEMENTED.** The additive extension to `schemas/question-item.schema.json` is **approved and already applied**; the build is cleared to depend on it. The extension is:

1. **add `"quantity"`** as a new member of `$defs/answerType.enum` (appended after the existing tail token so the byte-position of every current member is unchanged);
2. **add a new sibling `answer.measure` object** `{dimension, baseUnit, exponent}` (`additionalProperties:false`) to `answer.properties` — the structured unit is a **separate field, NOT folded into `answer.canonical`**, which stays the bare Rational `{num,den}` so every existing rational/parity/serialization path is byte-identical; `display` is **not** duplicated inside `measure` (it is derived and lives only at top level, `answer.display`);
3. an `if/then` (under `allOf`) binding `type:"quantity"` → `required:["measure"]`, and the `dimension⇔exponent` lock (`length⇔1`, `area⇔2`). For `type="quantity"` a unit is **always required** — there is no `requireUnit` opt-out.

The new structured `answer.measure` sits beside the **pre-existing legacy `answer.units` string** (plural); the two are distinct — mensuration items populate `answer.measure` and **never** `answer.units`, enforced by a `no-legacy-units-string` validator check. The whole `answer.type` token is named **`"quantity"`** consistently across §2 (`answerTypes:["quantity"]`), §3.2, §4, §9.2 (`answer-type-consistency`), §14, and here — one token, since the curriculum-objective records validate `answerTypes[]` against `question-item.schema.json#/$defs/answerType` and a mismatched token would fail validation.

This is the **only** schema change the family needs. It validates under the **bundled Ajv** (which evaluates the `if/then`/`allOf` obligations) and is **accepted** by the **extended `oracle/check_conformance.py`**, which has been extended with `allOf`/`if`/`then`/`const` support and therefore **enforces these conditional obligations offline** (the `type:"quantity" ⇒ measure required` binding and the `dimension⇔exponent` lock) rather than treating them as a no-op. The same conditionals are enforced in runtime Ajv, the extended offline conformance, import, bank storage, migration, export assembly, and the independent validator's `quantity-measure-contract` / `quantity-dimension-exponent-lock` / `answer-type-consistency` checks (§4.2/§9.2). The extension is additive (no existing answer type changes, so approved families' items stay schema-valid byte-for-byte). Placing the contract in shared core is what makes this single, approved extension reusable by every later measurement family instead of being re-litigated per family.


## Appendix B — Cross-section consistency notes (for human double-check)

1. SCHEMA REALITY CHECK — RESOLVED. The additive schema extension (the `answer.type` "quantity" member + the structured sibling `answer.measure` object {dimension, baseUnit, exponent}) is APPROVED and ALREADY IMPLEMENTED in schemas/question-item.schema.json. The structured field is `answer.measure` (the bare legacy `answer.units` string is left untouched and never populated by this family). There is no remaining measure-vs-unit ambiguity: the field is `answer.measure`. (Originally the live enum lacked any quantity/measure type; the approved extension added it without changing any existing member's byte-position, so approved families stay schema-valid byte-for-byte.)
2. Difficulty axes "closed by convention" — NOTE (consistent with §11). The live schema (question-item.schema.json $defs.difficultyProfile.axes) does NOT enforce additionalProperties:false on axes. §11 accordingly uses ONLY the platform-named axes and treats the set as closed by convention/test (the §11.5 documented-subset parity guard), not as schema-enforced closure. Consistent with §11 — no change needed.
3. DECISION_LOG is currently at #49 (gen.stats.data-handling CURRICULUM-APPROVED at v1.0.2). This proposal, once logged, would be the next entry (~#50). No DECISION_LOG entry number is asserted in the front matter to avoid pre-allocating one; §15 should record the actual entry on owner action.
4. Theme name — RESOLVED. Reused themes verified present: core/visual-style/cartesian-theme.{json,ts} (coordinate-lines v1.0.2 per-root cx-figure isolation; modes print/premium/premium-dark/accessible) and core/visual-style/data-chart-theme.{json,ts} (stats v1.0.2 ADDITIVE extension). The mensuration extension is named **`mensuration-theme`** (theme id `spi-math-mensuration-theme/1`), which `extends: "spi-math-cartesian-theme/1"` and FOLLOWS the data-chart-theme additive PATTERN without depending on it. The placeholder 'data-dimension-theme' is retired; the name is pinned in §13.4/§14.7/§16.
5. SDK lifecycle verified: approvalStatus ∈ {approved, pending-review, rejected} on core/sdk/sequence-registry.ts + generator-module.ts (DECISION_LOG #38); objectives during a pending build use reviewStatus 'approved-for-implementation' then 'approved' (stats precedent #45/#46). Front matter mirrors this two-stage gate.
6. exact-surd / exact-trig EXIST in the live answer.type enum but the brief forbids surds/irrationals; the proposal DEFERS them (they are deferred topics: Pythagoras/surds, circles/pi). Front matter lists them under DEFERRED via the no-irrationals rule. Ensure §4/§5 explicitly state the family never emits exact-surd/exact-trig answers despite their availability in the enum.
7. Objective IDs — RESOLVED. The owner pinned the IDs and the domain segment **MEAS** (not MENS). The eight objective IDs are: SPI.MIDDLE.MEAS.PERIM.RECTANGLE.01, SPI.MIDDLE.MEAS.PERIM.COMPOSITE_RECTILINEAR.01, SPI.MIDDLE.MEAS.AREA.RECTANGLE.01, SPI.MIDDLE.MEAS.AREA.TRIANGLE_BASE_HEIGHT.01, SPI.MIDDLE.MEAS.AREA.COMPOSITE_DECOMPOSITION.01, SPI.MIDDLE.MEAS.PERIM.MISSING_LENGTH.01, SPI.MIDDLE.MEAS.AREA.MISSING_DIMENSION.01, SPI.MIDDLE.MEAS.AREA.TRIANGLE_MISSING_BASE_HEIGHT.01. They follow the five-segment precedent depth and the schema regex.
8. Objective file — RESOLVED/updated. The objective file is to be authored at build time as curriculum/objectives/SPI.MIDDLE.MEAS.json (the eight MEAS objectives), with `reviewStatus: "approved-for-implementation"`; the build is authorized (§15). The single-source OBJECTIVE_BY_TASK map and the bespoke family graph test (cf. core/curriculum/stats-graph.test.ts / stats-objective-ids.ts) are authored alongside it.

## Appendix C — Authoring & verification provenance

Authored by a multi-agent workflow: 16 sections drafted in parallel against a fixed platform-conventions digest + the owner brief, reviewed by four adversarial critics (mensuration-math correctness, platform-fit, rendering/unit-contract, completeness), then revised against the consolidated findings and synthesized. The critics raised 38 findings (10 blocker-severity, 16 missing items), applied in the revision pass. The owner's revisions A–M are applied throughout, and implementation is AUTHORIZED oracle-first now (the additive schema extension is approved and already implemented); the generator registry entry remains pending-review until the review-pack decision.
