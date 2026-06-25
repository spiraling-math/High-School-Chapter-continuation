# Generator Specification Proposal — `gen.geometry.transformations` v1.0.0 (Coordinate Transformations: translation, reflection, rotation, and describing a mapping)

> **STATUS: PROPOSAL ONLY — for the owner to APPROVE / REVISE / REJECT.** This document specifies a *proposed* new SPI-Math Middle School generator family. **No implementation begins until the owner approves the complete proposal** — no code, no fixtures, no curriculum objectives, no schema changes, no SVG assets, no SDK registry entries, and no review artifacts are written before that decision. On approval, the build proceeds **oracle-first** (the independent Python `spi_oracle` transformation engine, parser, canonicalizer, equivalence checker, renderer, and validator are authored and frozen **before** the byte-identical TypeScript mirror), and the family registers `approvalStatus: pending-review` in `core/sdk/sequence-registry.ts` — **gated out of normal Generator Studio and out of production exports/samples** (visible only in `?review` developer mode, labelled "machine-validated — pending curriculum approval") — until a separate review-pack decision advances it to `approved`.
>
> **ALL PLATFORM GATES RETAINED — no exceptions.** Deterministic seeded generation (byte-identical Mulberry32 / Python PRNG; deterministic redraw with call-order parity); **exact integer coordinate arithmetic with no floats, no trigonometry, no tolerances, and no irrational coordinates** (translations, axis/line reflections, and quarter-turn rotations are *integer* coordinate maps — no `sin`/`cos`); independent **Python + TypeScript** with closure-agreement; canonical item **and** canonical SVG **byte-for-byte** Py↔TS parity; runtime Ajv schema validation at every boundary **and** Python schema conformance; **all nine tasks are FREE-RESPONSE ONLY in v1.0.0** — an explicit multiple-choice request returns a clear unsupported-interaction result and is **never** silently downgraded to free-response; misconceptions are deterministic **free-response diagnostics + targeted feedback**, each rule-recomputed by the independent validator; golden(seed) + a **≥ 300-entry task-pinned FREE-RESPONSE parity fixture** + an `SPI_SWEEP` **10,000-seed** stability sweep + reproducibility re-check + a distribution report proving **every declared band is reachable**; a per-item review pack (md + json + per-item SVGs) with a reachability-derived **coverage matrix**; accessibility (axe-core **0 critical/serious**, WCAG AA) with a **data-table fallback for every figure**; offline HTML/JSON exporters (worksheet / answer-key / solutions) with a bank-json round-trip; a **generation manifest + SHA-256 artifact-integrity + artifact-IDENTITY tests** (Py + TS); **immutable approved-family fixtures**; newly generated items begin machine-validated.
>
> **REUSE, NOT REINVENTION.** This family **reuses the approved Cartesian substrate through versioned ADDITIVE extensions** and does **not** alter any approved contract in place. The object-and-image figure is rendered with the APPROVED `gen.geometry.coordinate-lines` v1.0.2 renderer (`domains/geometry/coordinate-lines.ts` + `oracle/spi_oracle/coordinate_lines.py` — axes, grid, ticks, labelled lattice points, the `CARTESIAN_PLANE` model) and the APPROVED `core/visual-style/cartesian-theme.{json,ts}` (per-root `.cx-figure` CSS-custom-property isolation; modes `premium` / `premium-dark` / `accessible` / `print`; `presentationSvg()` / `exportSvg()`; materialised **6000 × 4200** export). Any transformation-specific styling (object vs. image marker shapes / line patterns / fill patterns, the answer-key vector arrow / reflection axis / rotation centre overlay) is an **ADDITIVE versioned theme extension** following the exact pattern of `data-chart-theme` (stats v1.0.2) and `mensuration-theme` (mensuration v1.0.1) — so `coordinate-lines` and every other approved family's output stays **byte-for-byte unchanged**. The student-figure-vs-answer-key separation reuses the APPROVED mensuration **base-geometry + additive-overlay channel** pattern (student figure = root + base geometry + student annotations + close; answer-key = + an additive overlay group; base BYTE-IDENTICAL across channels). The review-pack **COVERAGE-MATRIX machinery** (required cells = every task × supported interaction × reachable band × realised answer shape, DERIVED from the distribution report; the builder FAILS on any missing reachable cell) is reused exactly from mensuration / stats v1.0.x. The **ONE new `answer.type` `"transformation"`** follows the mensuration v1.0.1 `"quantity"` precedent verbatim — an **additive, back-compatible, OWNER-GATED** `question-item.schema.json` extension (new enum value + a structured discriminated-union object, both `additionalProperties:false`, with conditional `if/then`/`const` rules) enforced in **both** the runtime Ajv validator (recompiled via `scripts/compile-schemas.mjs` → `core/schema/compiled/`) **and** the Python conformance checker (`oracle/check_conformance.py`, honouring `const`/`allOf`/`if-then`), with the import/bank/export impact stated. **It is the ONLY schema change this proposal requests** — and §6/§7 confirm that **point-image** tasks reuse the existing `coordinate` / `ordered-pair` answer types and **shape-image** tasks reuse the existing `table-completion` answer type (one row per labelled image vertex, correspondence by vertex LABEL), with no separate polygon-answer schema introduced.

## Overview

`gen.geometry.transformations` is **the next architecture-proving family** because it is the first to demonstrate four platform capabilities together that no approved family has yet exercised. First, it is the **first EXACT integer-coordinate transformation engine**: every image coordinate is produced by an exact integer map — translation `(x,y)→(x+dx,y+dy)`, reflection in `x=a` / `y=b` / `y=x` / `y=-x`, and rotation by 90/180/270° about an *integer lattice-point* centre — with **no trigonometry, no floats, no tolerances, and no irrational coordinates** anywhere in generation, calculation, rendering, or validation. Second, it introduces the **first structured TRANSFORMATION-DESCRIPTOR answer**: a single new `answer.type` `"transformation"`, a discriminated union over `translation` / `reflection` / `rotation`, with **one canonical internal convention** (positive quarter-turns are ANTICLOCKWISE — 90° clockwise canonicalizes to 3 quarter-turns ACW, 270° clockwise to 1, and a 180° rotation has no direction). A finite, deterministic human-text parser normalizes accepted prose ("rotation 90° clockwise about (2, −1)", "reflection in the y-axis", "translation by the column vector [3; −2]") to that canonical descriptor, and a structural equivalence checker awards full correctness only to a descriptor that is genuinely equivalent — never to an ambiguous, incomplete, or contradictory one. Third, it is the **first family with multi-vertex structured coordinate answers**: a transformed triangle or quadrilateral image is answered as a `table-completion` with one row per labelled image vertex (A′, B′, C′, D′), correspondence carried by vertex **label**, not array order alone. Fourth, it renders **object-and-image figures on the APPROVED Cartesian grid**, reusing the coordinate-lines renderer and cartesian-theme, with source and image made distinguishable **without relying on colour** (distinct marker shapes / line patterns / fill patterns + authoritative monochrome print).

The fifth proving capability is **geometric-mapping uniqueness validation**: for every *describe-the-transformation* item the independent validator must, without merely calling the generator forward, **enumerate and reconstruct every allowed candidate descriptor** and prove that **exactly one** canonical transformation maps every labelled source vertex to its corresponding image vertex — rejecting any item where several allowed descriptors fit, none fits, the object is unchanged, symmetry makes the mapping ambiguous, or a fixed point hides the intended transformation. The v1.0.0 scope is deliberately the small, fully-exact core: three transformation types (translation by a **nonzero** integer vector; reflection in `x=a`/`y=b`/`y=x`/`y=-x`; rotation by 90/180/270° about an integer centre), four object types (a labelled point, segment, non-degenerate triangle, simple quadrilateral — all integer-coordinate), and nine one-to-one task↔objective micro-skills. **Every deferred topic — enlargements and scale factors (incl. fractional/negative), compositions, invariant-line/point proofs, arbitrary reflection lines, arbitrary-angle / trig-requiring rotations, fractional translation vectors or rotation centres, transformations of curves or functions, tessellations, matrices as the required student method, and 3-D transformations — is deterministically EXCLUDED**, unreachable from the seeded task loop and rejected (never silently downgraded) if requested. Sections 1–16 develop each decision; this front matter fixes the identifiers, the reuse posture, the headline answer contract, and the PROPOSAL-ONLY approval posture.

## Identifier glossary

| Item | Value (use verbatim) |
| --- | --- |
| Family / generator id | `gen.geometry.transformations` |
| Generator version | `1.0.0` (PROPOSED; oracle-first build on approval) |
| Validator version | `1.0.0` (independent Py + TS, byte-parity) |
| Domain | `geometry` (existing domain; segment `GEO`) |
| Strand | `coordinate-transformations` (new strand within `geometry`) |
| Stage | `middle-school` (stage segment `MIDDLE` — never `MS`) |
| Objective ID pattern | `SPI.MIDDLE.GEO.TRANS.<MICRO>.01` (matches `^SPI\.[A-Z0-9]+(\.[A-Z0-9_]+)+\.[0-9]{2}$`) |
| Misconception ID prefix | `MISC.TRANS.*` (registry-backed, Py + byte-parity TS; deterministic free-response diagnostics + feedback) |
| Headline new contract | **transformation-descriptor answer** — `answer.type="transformation"` + a structured discriminated union `{ translation \| reflection \| rotation }` (see below), beside a derived ASCII `display` |
| The ONE new `answer.type` (OWNER-GATED) | `"transformation"` — an **additive, back-compatible** `question-item.schema.json` extension (new enum value + a structured discriminated-union object, both `additionalProperties:false`, with `if/then`/`const` discriminator rules), **flagged OWNER-GATED**, following the mensuration v1.0.1 `"quantity"` precedent; recompiled into runtime Ajv (`core/schema/compiled/`) **and** honoured by the Python conformance checker. **No other schema change is requested.** |
| Descriptor union (canonical) | `translation { kind:"translation", vector:{dx:int,dy:int} }` · `reflection { kind:"reflection", axis:{kind:"vertical",value:int} \| {kind:"horizontal",value:int} \| {kind:"diagonal",equation:"y=x"} \| {kind:"diagonal",equation:"y=-x"} }` · `rotation { kind:"rotation", centre:{x:int,y:int}, quarterTurnsCCW:1\|2\|3 }` |
| Canonical direction convention | **positive quarter-turns are ANTICLOCKWISE (CCW)**; 90° clockwise → 3 quarter-turns ACW; 270° clockwise → 1 quarter-turn ACW; 180° has no direction distinction |
| Point-image answers (REUSED) | the EXISTING `coordinate` / `ordered-pair` answer type — **no new type** |
| Shape-image answers (REUSED) | the EXISTING `table-completion` answer type — one row per labelled image vertex (A′→coord, B′→coord, …); correspondence by vertex **LABEL**, not array order; **no separate polygon-answer schema** |
| Interaction types used | **`free-response` ONLY** — all nine tasks; **no task offers `multiple-choice`** in v1.0.0; an explicit MC request returns a clear unsupported-interaction result (never silently replaced with FR) |
| Reused renderer (do NOT modify) | `gen.geometry.coordinate-lines` v1.0.2 — `domains/geometry/coordinate-lines.ts` + `oracle/spi_oracle/coordinate_lines.py` (axes/grid/ticks/labelled lattice points, the `CARTESIAN_PLANE` model); REUSED for the object-and-image figure |
| Reused style / export | `core/visual-style/cartesian-theme.{json,ts}` (per-root `.cx-figure` isolation; modes `premium`/`premium-dark`/`accessible`/`print`; `presentationSvg()`/`exportSvg()`; 6000 × 4200) **via a NEW ADDITIVE transformations-theme extension** (`extends: spi-math-cartesian-theme/1`), following the `data-chart-theme` / `mensuration-theme` PATTERN; ADDS object/image marker shapes, line/fill patterns, the answer-key vector arrow / reflection axis / rotation-centre overlay |
| Reused channel pattern | the mensuration v1.0.1 **base-geometry + additive-overlay** channels (base BYTE-IDENTICAL across student and answer-key; overlay additive-only) |
| Reused coverage machinery | the mensuration / stats v1.0.x review-pack COVERAGE-MATRIX (required cells derived from the distribution report; builder FAILS on any missing reachable cell) — reused exactly |
| Natural prerequisites | the APPROVED `gen.geometry.coordinate-lines` `SPI.MIDDLE.GEO.COORD.*` objectives (reading/plotting coordinates on the Cartesian plane), incl. `SPI.MIDDLE.GEO.COORD.CARTESIAN_PLANE.01`, `READ_POINT.01`, `PLOT_POINT.01` |
| Registry status (on approval) | `approvalStatus: pending-review` (gated from normal Studio + production) until the separate review-pack decision |
| Objective lifecycle (on approval) | `reviewStatus: approved-for-implementation` → `approved` only at the later review-pack decision |
| Initial item lifecycle | `lifecycle.state = generated` (machine-validated) |
| Provenance | `origin: generated`, `rightsStatus: academy-owned` |

**The nine v1.0.0 tasks (canonical `task` enum, used verbatim everywhere) ↔ objectives ↔ answer shape:**

| # | Generator task (canonical slug) | objectiveId | Answer shape |
| --- | --- | --- | --- |
| T1 | `translate_point` | `SPI.MIDDLE.GEO.TRANS.TRANSLATE_POINT.01` | `coordinate` / `ordered-pair` |
| T2 | `translate_shape` | `SPI.MIDDLE.GEO.TRANS.TRANSLATE_SHAPE.01` | `table-completion` (one row per image vertex) |
| T3 | `reflect_point` | `SPI.MIDDLE.GEO.TRANS.REFLECT_POINT.01` | `coordinate` / `ordered-pair` |
| T4 | `reflect_shape` | `SPI.MIDDLE.GEO.TRANS.REFLECT_SHAPE.01` | `table-completion` |
| T5 | `rotate_point` | `SPI.MIDDLE.GEO.TRANS.ROTATE_POINT.01` | `coordinate` / `ordered-pair` |
| T6 | `rotate_shape` | `SPI.MIDDLE.GEO.TRANS.ROTATE_SHAPE.01` | `table-completion` |
| T7 | `describe_translation` | `SPI.MIDDLE.GEO.TRANS.DESCRIBE_TRANSLATION.01` | `transformation` (translation) |
| T8 | `describe_reflection` | `SPI.MIDDLE.GEO.TRANS.DESCRIBE_REFLECTION.01` | `transformation` (reflection) |
| T9 | `describe_rotation` | `SPI.MIDDLE.GEO.TRANS.DESCRIBE_ROTATION.01` | `transformation` (rotation) |

There is exactly **one** spelling of each of the nine task slugs and exactly **one** `OBJECTIVE_BY_TASK` map (`core/curriculum/transformations-objective-ids.ts`, mirrored verbatim by `oracle/spi_oracle/transformations.py`), re-used by every spec section, the generator dispatch, the validator, the fixtures, the misconception `RULES_BY_TASK`, the COVERAGE-MATRIX `cell:<task>:…` tokens, and the SDK registry entry; a bespoke graph test (modelled on `core/curriculum/mensuration-graph.test.ts`) asserts the nine IDs are present, the TS and Python maps agree, all key sets are identical, and no alternative slug / `MISC.TRANS.*` spelling appears anywhere.

**v1.0.0 scope (IN) vs DEFERRED (deterministically excluded — unreachable from the seeded task loop):**

| Status | Topic | Note |
| --- | --- | --- |
| IN v1.0.0 | Translation by a **nonzero** integer vector | `(x,y)→(x+dx,y+dy)`; zero vector excluded by construction |
| IN v1.0.0 | Reflection in `x=a`, `y=b`, `y=x`, `y=-x` | exact integer maps; no arbitrary lines |
| IN v1.0.0 | Rotation by 90 / 180 / 270° about an **integer lattice-point** centre | exact quarter-turn maps; canonical positive turns ACW; no trig |
| IN v1.0.0 | Objects: a labelled point; a labelled segment; a non-degenerate triangle; a simple quadrilateral | every vertex integer-coordinate; describe-tasks PREFER non-symmetric figures for a UNIQUE mapping |
| IN v1.0.0 | Nine tasks: perform (point/shape × translate/reflect/rotate) + describe (translation/reflection/rotation) | FREE-RESPONSE only |
| DEFERRED | enlargements + scale factors; fractional / negative scale factors | not a congruence map; later family |
| DEFERRED | compositions of transformations | single-transformation scope only |
| DEFERRED | invariant-line / invariant-point proofs | out of v1.0.0 task scope |
| DEFERRED | arbitrary reflection lines; arbitrary-angle / trig-requiring rotations | violate the exact-integer / no-trig rule |
| DEFERRED | fractional translation vectors; fractional rotation centres | violate integer-coordinate closure |
| DEFERRED | transformations of curves / functions; tessellations | outside the labelled-shape model |
| DEFERRED | matrices as the **required student method** | a later representation; not required in v1.0.0 |
| DEFERRED | 3-D transformations | 2-D Cartesian scope only |

> Each DEFERRED row is **unreachable from the seeded task loop**, not merely undrawn: the task enum, the transformation/object selector, and the redraw loop have no path that produces a deferred topic; a request for one is rejected, never silently downgraded (see §3 task matrix, §4 transformation model, §9 engine, §14 edge-case policy).

## Table of contents

1. Curriculum placement and objective IDs
2. Final objective wording and prerequisites
3. Task and interaction matrix (nine tasks; FREE-RESPONSE only; explicit-MC → unsupported-interaction)
4. Canonical transformation model (the one exact `Transformation` union; positive quarter-turns ACW; no runtime trig)
5. Source / image shape model (labelled-shape union; integer vertices; invariants; congruence; viewport containment)
6. Coordinate-answer representation (point images reuse `coordinate`/`ordered-pair`; shape images reuse `table-completion`, label-keyed)
7. Transformation-descriptor schema (the ONE new OWNER-GATED `answer.type="transformation"` — additive, back-compatible; Ajv + Python conformance + import/bank/export)
8. Parser, canonicalizer, and equivalence checker (finite deterministic prose parser → canonical descriptor; structural equivalence; rejection rules)
9. Exact transformation engine (integer rules for translation / reflection / rotation; integer-coordinate closure; no trig)
10. Backward construction (one guaranteed mapping; perform-task figures hide the image; describe-task figures show object + image; uniqueness)
11. Cartesian SVG rendering contract (REUSED coordinate-lines renderer + cartesian-theme; additive overlay; source/image distinct without colour)
12. Independent validator (the named checks; descriptor uniqueness; inverse-restores-source; byte-SVG; semantic answer-leakage)
13. Misconception and diagnostic registry (`MISC.TRANS.*`; deterministic translation / reflection / rotation / descriptor adapters)
14. Difficulty and edge-case policy (closed-enum axes; `bandFromScore`; every declared band reachable; deterministic exclusion of deferred topics)
15. Accessibility and review-pack plan (data-table fallbacks; coverage matrix; transformation-checker matrix; four render modes; 6000 × 4200 export)
16. Versioning, lifecycle, and reusable infrastructure (PROPOSAL → on-approval oracle-first → `pending-review` registry → later review-pack decision)


---

## 1. Curriculum placement and objective IDs

### 1.1 Domain and strand

`gen.geometry.transformations` sits in the **existing** `geometry` domain and introduces **one new strand**, `coordinate-transformations`, within it — deliberately distinct from the approved `coordinate-geometry-straight-line-graphs` strand (`gen.geometry.coordinate-lines`, lines/gradients/intercepts), which it depends on rather than extends. Both `domain` and `strand` are free-form strings in `schemas/curriculum-objective.schema.json` (not enums), so no schema change is required to add the strand; it follows the lower-case-hyphenated convention already used by `geometry` / `coordinate-geometry-straight-line-graphs`.

| Field | Value (verbatim, every objective in this family) |
| --- | --- |
| `academy` | `SPI-Math` |
| `programme` | `SPI-Math Middle School` |
| `stage` | `middle-school` |
| `course` | `SPI-Math Middle School Mathematics` |
| `domain` | `geometry` |
| `strand` | `coordinate-transformations` |
| `topic` | `coordinate transformations` |

All deferred topics — enlargements / scale factors (fractional, negative), compositions of transformations, invariant-line/point proofs, arbitrary reflection lines, arbitrary-angle / trig-requiring rotations, fractional translation vectors or rotation centres, transformations of curves / functions, tessellations, matrix methods, and 3D transformations — are **out of strand for v1.0.0** and are deterministically excluded by generator construction (§3.3, and the owner brief DEFER list, with named exclusion tests in the §12 validator / §14 difficulty-and-edge-case / §15 review-pack clusters). They are recorded here as future objectives, never silently produced.

### 1.2 Family identity (generatorId / generatorVersion)

The family pins a single registry identity, mirroring the coordinate-lines export pair `GENERATOR_ID = "gen.geometry.coordinate-lines"` / `GENERATOR_VERSION = "1.0.2"` (verified in `domains/geometry/coordinate-lines.ts:22-23`). The transformations module (`domains/geometry/transformations.ts`) exports:

- `GENERATOR_ID = "gen.geometry.transformations"`
- `GENERATOR_VERSION = "1.0.0"`

These exact strings are carried **identically** by every generated `item.generatorId` / `item.generatorVersion`, the `itemId` prefix (`ITEM-gen-geometry-transformations-<seed>-<task>`, matching the coordinate-lines `itemId` recipe at `coordinate-lines.ts:696`), the golden / parity fixtures, the generation manifest, the artifact-identity tests, and the SDK `sequence-registry.ts` entry. The Python oracle (`oracle/spi_oracle/transformations.py`) declares the byte-identical pair. An artifact-identity test asserts the visible-version / commit identity in both Py and TS (the mensuration v1.0.1 precedent).

### 1.3 ID convention and the nine micro-objectives

IDs obey the platform pattern `SPI.<STAGE>.<DOMAIN>.<TOPIC>.<MICRO>.<NN>` and the schema ID regex. The stage segment is `MIDDLE`, the domain segment is `GEO`, and the topic segment is **`TRANS`** (coordinate transformations). There is **one micro-objective per owner task** — the `<MICRO>` segment is the upper-cased task slug — giving **nine objectives, all suffixed `.01`** (the first revision; future revisions bump `.NN`). IDs are **stable** and never reused for a different task.

| # | Owner task slug | Objective ID |
| --- | --- | --- |
| T1 | `translate_point` | `SPI.MIDDLE.GEO.TRANS.TRANSLATE_POINT.01` |
| T2 | `translate_shape` | `SPI.MIDDLE.GEO.TRANS.TRANSLATE_SHAPE.01` |
| T3 | `reflect_point` | `SPI.MIDDLE.GEO.TRANS.REFLECT_POINT.01` |
| T4 | `reflect_shape` | `SPI.MIDDLE.GEO.TRANS.REFLECT_SHAPE.01` |
| T5 | `rotate_point` | `SPI.MIDDLE.GEO.TRANS.ROTATE_POINT.01` |
| T6 | `rotate_shape` | `SPI.MIDDLE.GEO.TRANS.ROTATE_SHAPE.01` |
| T7 | `describe_translation` | `SPI.MIDDLE.GEO.TRANS.DESCRIBE_TRANSLATION.01` |
| T8 | `describe_reflection` | `SPI.MIDDLE.GEO.TRANS.DESCRIBE_REFLECTION.01` |
| T9 | `describe_rotation` | `SPI.MIDDLE.GEO.TRANS.DESCRIBE_ROTATION.01` |

The nine tasks split into three families of three by the three transformation types (translation, reflection, rotation) crossed with three operations (transform a point, transform a labelled shape, describe a shown mapping). The mapping is **one-to-one task → objective** throughout; there is no many-to-one collapsing.

### 1.4 Single-source task slugs and `OBJECTIVE_BY_TASK` map

Mirroring `core/curriculum/mensuration-objective-ids.ts` and `core/curriculum/stats-objective-ids.ts` exactly, the family ships **one** authoritative task-slug set and task → objective map, `core/curriculum/transformations-objective-ids.ts`, re-used **verbatim** by the Python oracle (`oracle/spi_oracle/transformations.py: OBJECTIVE_BY_TASK`), every spec section, the descriptor/parser/equivalence checker, the independent validator, fixtures, review-pack records, the misconception `RULES_BY_TASK`, the COVERAGE-MATRIX `cell:<task>:…` tokens, and the SDK registry entry. **There is exactly one spelling of each of the nine task slugs and one spelling of each objective ID; no section uses any alternative.** A bespoke graph test, `core/curriculum/transformations-graph.test.ts` (modelled directly on `core/curriculum/mensuration-graph.test.ts`), asserts: (a) all nine IDs exist in `curriculum/objectives/SPI.MIDDLE.GEO.TRANS.json`; (b) the TS map and the Python map agree; (c) `OBJECTIVE_BY_TASK`, `RULES_BY_TASK`, the generator dispatch, and the COVERAGE-MATRIX cell tokens share an **identical key set** equal to `TRANSFORMATIONS_TASKS` with **cardinality nine**; (d) no alternative slug spelling and no alternative `MISC.TRANS.*` id spelling appears anywhere in the family (a string-scan assertion over both namespaces, catching id/slug drift before merge); (e) the combined middle-school objective set (loading `SPI.MIDDLE.GEO.TRANS.json` alongside the existing files) is a clean DAG with no duplicate id and no cycle; (f) the **object-type guard** `objectTypeForTask(describe_*) ∈ {triangle, quadrilateral}` holds for all three describe tasks (point and segment are forbidden as describe objects — see §1.5 and §3.2).

The intended shape (no implementation — field names and constants only), exactly paralleling the verified `mensuration-objective-ids.ts` module:

- `TRANSFORMATIONS_TASKS = [ "translate_point", "translate_shape", "reflect_point", "reflect_shape", "rotate_point", "rotate_shape", "describe_translation", "describe_reflection", "describe_rotation" ]` — **the single canonical slug set; these exact nine strings are the keys used everywhere.**
- `OBJECTIVE_BY_TASK: Record<TransformationTask, string>` keyed by those nine slugs to the nine IDs in §1.3.
- `TRANS_OBJECTIVE_IDS = TRANSFORMATIONS_TASKS.map(t => OBJECTIVE_BY_TASK[t])`.
- `SUPPORTED_INTERACTIONS = ["free-response"]` — **all nine tasks are free-response only in v1.0.0**. An explicit multiple-choice request is rejected with a clear unsupported-interaction error (§3.1, §3.3) and is never silently replaced with a free-response item. The misconceptions are deterministic free-response diagnostics + feedback (§13), not multiple-choice distractors.
- `POINT_IMAGE_TASKS = [ "translate_point", "reflect_point", "rotate_point" ]` and `SHAPE_IMAGE_TASKS = [ "translate_shape", "reflect_shape", "rotate_shape" ]` and `DESCRIBE_TASKS = [ "describe_translation", "describe_reflection", "describe_rotation" ]` — the three answer-shape partitions consumed by §3.2 (these three sets are disjoint and their union is `TRANSFORMATIONS_TASKS`; the graph test asserts the partition).
- `DESCRIBE_OBJECT_TYPES = [ "triangle", "quadrilateral" ]` — **the closed set of object types permitted for describe tasks** (§1.5). Consumed by `objectTypeForTask` (§10.2) and the §15 coverage-matrix derivation so that `obj:point` / `obj:segment` are required coverage cells for the perform point/shape tasks **only**, never for describe tasks.

The objective records live in a single file `curriculum/objectives/SPI.MIDDLE.GEO.TRANS.json` (one file per strand within the geometry domain, matching `curriculum/objectives/SPI.MIDDLE.GEO.COORD.json`). Their `reviewStatus` follows the two-stage gated lifecycle established by the coordinate-lines and mensuration families and consistent with the schema enum:

1. **`proposed`** — before the curriculum authority signs off the objective definitions.
2. **`approved-for-implementation`** — once the definitions are curriculum-approved and the generator build is cleared to proceed *while the generator itself remains gated*; this is the status the objective files carry **throughout the gated build**.
3. **`approved`** — flipped only on owner APPROVE of the review pack.

In parallel, the SDK generator registers `approvalStatus: pending-review` in `core/sdk/sequence-registry.ts` (gated from normal Studio + production via `generatorsForMode` / `approvedGenerators`) until owner approval. `core/curriculum/graph-check.ts` enforces the DAG over the combined objective set (duplicate-id and cycle = errors; unresolved prereqs = warnings).

### 1.5 Object-type restriction for the three describe tasks (uniqueness is structural, not a redraw outcome)

The three describe tasks (`describe_translation`, `describe_reflection`, `describe_rotation`) require that **exactly one** allowed transformation maps the labelled source onto the labelled image. This is an **affirmative input restriction**, not merely a downstream redraw filter: the generator restricts describe-task object types to a **non-symmetric labelled triangle or irregular simple quadrilateral**. **Point and segment objects are forbidden for describe tasks** — `objectTypeForTask(describe_*) ∈ {triangle, quadrilateral}` is a hard guard with a named test (§3.3, §10.2, §12.6); they remain valid object types for the six perform tasks only.

**Why points and segments cannot be describe objects (mathematical justification).** Uniqueness of the descriptor needs ≥3 non-collinear labelled vertices:

- **Single point** — a labelled point `A → A′` is realised by one translation **and** infinitely many rotations and reflections (every reflection whose mirror is the perpendicular bisector of `AA′`, every rotation whose centre lies on that bisector). The allowed-descriptor space is therefore infinite; no guard can make it unique.
- **Segment (two collinear points)** — an isometry is pinned by a labelled segment only up to a reflection, so an allowed reflection and an allowed rotation can produce the **identical** labelled image. Concrete proof: source `A = (0,0)`, `B = (1,0)`. Reflection in `y = x` gives `A′ = (0,0)`, `B′ = (0,1)`. Rotation 90° anticlockwise about the origin gives the **same** labelled image `A′ = (0,0)`, `B′ = (0,1)`. Two valid allowed descriptors ⇒ inherent ambiguity that §12.6 `descriptor-unique` must reject — and since the ambiguity is intrinsic to *every* segment instance, a redraw loop would exhaust `MAX_PARAM_ATTEMPTS` and throw.

The root cause is vertex count: distinguishing a 180° rotation from a translation needs ≥2 vertices (a non-constant image−source difference), and distinguishing a reflection from a rotation needs orientation, which a degenerate (collinear) figure cannot pin per label.

**Why a no-symmetry triangle / quadrilateral is provably unique.** A labelled figure with a trivial symmetry group admits **exactly one** direct (orientation-preserving) isometry and **zero** allowed opposite (orientation-reversing) isometries mapping it onto a given image, because any second candidate descriptor would differ from the first by a non-identity symmetry of the labelled source — which does not exist. The generator's **non-symmetry acceptance predicate** (exact integer tests, no floats), enforced at generation and re-checked by the independent validator (§12.6 `no-ambiguous-symmetry`):

- **Triangle** — the three squared side lengths are pairwise distinct (scalene over the integer lattice): `|AB|² , |BC|² , |CA|²` all different. This rules out isosceles/equilateral reflective symmetry.
- **Quadrilateral** — **no** non-identity isometry maps the labelled, oriented vertex sequence `(A,B,C,D)` to itself: the figure is simple, non-self-intersecting, and its symmetry group is trivial (checked by enumerating the finite candidate lattice isometries — the 8 dihedral maps about the centroid restricted to integer images — and confirming none fixes the labelled vertex set). Squares, non-square rectangles, rhombi, isosceles trapezia, kites, and parallelograms are thereby excluded as describe sources.

Orientation (the sign of the signed area of `(A,B,C)`, or of `(A,B,C,D)` traversed in label order) then disambiguates direct vs opposite isometries: a translation/rotation **preserves** the orientation sign; a reflection **flips** it. With the source non-symmetric, the candidate space collapses to a single descriptor, recomputed independently in §12.6 (`descriptor-unique`, `descriptor-maps-complete-shape`). The shape model also guarantees ≥3 labelled vertices for describe tasks, which §9.4 / §12.6 use to select a non-degenerate basis when reconstructing a rotation centre.

---

## 2. Final objective wording and prerequisites

Each objective below gives the verbatim learner-can-do `objectiveWording`, the `prerequisites[]` (citing **only objective IDs verified present and `approved` in `curriculum/objectives/`** — see the verification note), the MATHEMATICAL-only `answerTypes[]`, `allowedRepresentations`, `calculatorPolicy`, `successCriteria[]`, `commonMisconceptions[]` (the specific `MISC.TRANS.*` ids defined in §13), and a **provisional** `difficultyRange`. Per platform convention, **the `answerTypes[]` list is kept MATHEMATICAL-only**, so it never carries an interaction token; the MC/FR decision is recorded in §3. Ranges are provisional until the 10,000-seed distribution report (§14) proves every declared band reachable.

`calculatorPolicy` is **`calculator-not-required`** for all nine objectives (matching every approved `SPI.MIDDLE.GEO.COORD.*` and `SPI.MIDDLE.NUM.SIGNED_OPERATIONS.01` objective; verified value present in the schema enum and in those files): all coordinate rules are exact small-integer arithmetic with sign changes, so no calculator is needed.

`allowedRepresentations` is `["diagram", "graphical", "numeric"]` for the point-image and shape-image tasks (the canonical shape model drives a `diagram` rendered on the approved Cartesian grid; the answer is a `numeric` coordinate / table) and `["diagram", "graphical", "symbolic"]` for the three describe tasks (the answer is a `symbolic` structured transformation descriptor). All four representation values are in the closed `allowedRepresentations` enum. **`verbal-context` is deliberately omitted** in v1.0.0: items carry no worded story context, so listing it would name a representation the generator never exercises; it is reserved for a future revision.

### Prerequisites cited — verification note (stable basis)

Only IDs that exist as a defined `objectiveId` **and** carry `reviewStatus: "approved"` in their named file are cited as prerequisites. This is exactly the basis `core/curriculum/graph-check.ts` and `transformations-graph.test.ts` assert — no brittle line numbers are relied upon. All four external roots below were verified present and `approved`:

- `SPI.MIDDLE.GEO.COORD.READ_POINT.01` — **present and `approved`** in `curriculum/objectives/SPI.MIDDLE.GEO.COORD.json`. Reading the coordinates of a plotted point as an ordered pair in any of the four quadrants — the prerequisite for interpreting the source object on the grid. This is the natural approved coordinate-lines anchor named in the platform conventions.
- `SPI.MIDDLE.GEO.COORD.PLOT_POINT.01` — **present and `approved`** in the same file. Plotting a point from a given ordered pair in the correct quadrant — the prerequisite for producing a coordinate / table-completion image answer. It itself depends on `READ_POINT.01` and `CARTESIAN_PLANE.01`, so citing it pulls in the whole reading/plotting chain transitively.
- `SPI.MIDDLE.GEO.COORD.CARTESIAN_PLANE.01` — **present and `approved`** in the same file. Axes, origin, four quadrants, signed coordinates — cited directly on the describe tasks (which require reading both object and image across quadrants) and pulled in transitively elsewhere via `PLOT_POINT.01`.
- `SPI.MIDDLE.NUM.SIGNED_OPERATIONS.01` — **present and `approved`** in `curriculum/objectives/SPI.MIDDLE.NUM.json`. Calculation with positive and negative integers. This is the **signed-arithmetic prerequisite** the owner brief requires: every exact coordinate rule is integer arithmetic with sign changes — `(x, y) → (x + dx, y + dy)`, `2a − x`, `(y, x)`, `(−y, −x)`, `(−(y − k), x − h)` — so signed add/subtract/negate is the arithmetic backbone of the whole family.

No new objective IDs are invented as prerequisites, and no ID is cited that is not a defined and `approved` `objectiveId`; the §1.4 graph test resolves with **zero** unresolved-prerequisite warnings. The approved cartesian-theme / coordinate-lines renderer is **reused** (§11) but the coordinate-lines *gradient / equation* objectives (`GRADIENT_TWO_POINTS`, `INTERPRET_MX_C`, `EQUATION_FROM_GRAPH`, `EQUATION_FROM_2PTS`) are **not** prerequisites — no transformation task requires gradient or line-equation reasoning — and are listed in `relatedObjectives` only.

### Objective → misconception linkage (the `commonMisconceptions[]` arrays, defined in §13)

Each objective record carries `commonMisconceptions[]` populated with the `MISC.TRANS.*` ids whose §13 `applicability` includes that task's slug (the `RULES_BY_TASK[task]` set), so the curriculum graph and the diagnostic registry agree on a single linkage:

| Objective | `commonMisconceptions[]` (ids defined in §13) |
| --- | --- |
| T1 `TRANSLATE_POINT` | `MISC.TRANS.VECTOR_REVERSED`, `MISC.TRANS.SWAP_DX_DY`, `MISC.TRANS.ONE_COMPONENT_ONLY`, `MISC.TRANS.WRONG_SIGN_ONE_COMPONENT` |
| T2 `TRANSLATE_SHAPE` | the four T1 rules **plus** `MISC.TRANS.FROM_ORIGIN_NOT_VERTEX` |
| T3 `REFLECT_POINT` | `MISC.TRANS.WRONG_AXIS_X_FOR_Y`, `MISC.TRANS.WRONG_AXIS_Y_FOR_X`, `MISC.TRANS.NEGATE_WRONG_COORDINATE`, `MISC.TRANS.YX_BOTH_SIGNS`, `MISC.TRANS.YNEGX_SWAP_ONLY`, `MISC.TRANS.LINE_CONSTANT_ZERO` |
| T4 `REFLECT_SHAPE` | the six T3 rules |
| T5 `ROTATE_POINT` | `MISC.TRANS.ROT_WRONG_DIRECTION`, `MISC.TRANS.ROT_ABOUT_ORIGIN`, `MISC.TRANS.ROT_180_FOR_90`, `MISC.TRANS.SWAP_WITHOUT_SIGN`, `MISC.TRANS.ROTATE_THE_CENTRE` |
| T6 `ROTATE_SHAPE` | the five T5 rules **plus** `MISC.TRANS.APPLY_TO_ONE_VERTEX` |
| T7 `DESCRIBE_TRANSLATION` | `MISC.TRANS.DESC_CORRECT_TYPE_WRONG_VECTOR` |
| T8 `DESCRIBE_REFLECTION` | `MISC.TRANS.DESC_CORRECT_TYPE_WRONG_AXIS`, `MISC.TRANS.DESC_NAMES_REFLECTION_FOR_ROTATION` |
| T9 `DESCRIBE_ROTATION` | `MISC.TRANS.DESC_ANGLE_MISSING_CENTRE`, `MISC.TRANS.DESC_CENTRE_WRONG_DIRECTION` |

The §1.4 string-scan assertion confirms every id named here is a defined `MISC.TRANS.*` rule in §13 and that no objective references an undefined id.

### 2.1 T1 — `SPI.MIDDLE.GEO.TRANS.TRANSLATE_POINT.01`
- **Wording:** "Translate a single labelled point on the coordinate grid by a given nonzero integer vector, and state the coordinates of the image point as an ordered pair."
- **prerequisites:** `["SPI.MIDDLE.GEO.COORD.READ_POINT.01", "SPI.MIDDLE.GEO.COORD.PLOT_POINT.01", "SPI.MIDDLE.NUM.SIGNED_OPERATIONS.01"]`
- **answerTypes:** `["coordinate", "ordered-pair"]` (both listed, matching the verified coordinate-lines point-objective precedent and the §6.1 stability argument; the realised answer is a single `coordinate`)
- **allowedRepresentations:** `["diagram", "graphical", "numeric"]`
- **calculatorPolicy:** `"calculator-not-required"`
- **successCriteria:** "Adds the vector to the point's coordinates exactly"; "States the image as an ordered pair `(x′, y′)` with integer components"; "Preserves point label correspondence `A → A′`."
- **commonMisconceptions:** `["MISC.TRANS.VECTOR_REVERSED", "MISC.TRANS.SWAP_DX_DY", "MISC.TRANS.ONE_COMPONENT_ONLY", "MISC.TRANS.WRONG_SIGN_ONE_COMPONENT"]`
- **difficultyRange:** `{ "min": 1, "max": 2 }`

### 2.2 T2 — `SPI.MIDDLE.GEO.TRANS.TRANSLATE_SHAPE.01`
- **Wording:** "Translate a labelled segment, triangle, or simple quadrilateral by a given nonzero integer vector, and state the coordinates of every image vertex by its corresponding label."
- **prerequisites:** `["SPI.MIDDLE.GEO.TRANS.TRANSLATE_POINT.01", "SPI.MIDDLE.GEO.COORD.PLOT_POINT.01", "SPI.MIDDLE.NUM.SIGNED_OPERATIONS.01"]`
- **answerTypes:** `["table-completion"]` (one row per labelled image vertex; correspondence by label)
- **allowedRepresentations:** `["diagram", "graphical", "numeric"]`
- **calculatorPolicy:** `"calculator-not-required"`
- **successCriteria:** "Applies the same vector to every vertex"; "Completes one table row per labelled image vertex `A′…D′`"; "Carries correspondence by vertex label, not row order."
- **commonMisconceptions:** `["MISC.TRANS.VECTOR_REVERSED", "MISC.TRANS.SWAP_DX_DY", "MISC.TRANS.ONE_COMPONENT_ONLY", "MISC.TRANS.WRONG_SIGN_ONE_COMPONENT", "MISC.TRANS.FROM_ORIGIN_NOT_VERTEX"]`
- **difficultyRange:** `{ "min": 2, "max": 3 }`

### 2.3 T3 — `SPI.MIDDLE.GEO.TRANS.REFLECT_POINT.01`
- **Wording:** "Reflect a single labelled point in a given line x = a, y = b, y = x, or y = −x, and state the coordinates of the image point as an ordered pair."
- **prerequisites:** `["SPI.MIDDLE.GEO.COORD.READ_POINT.01", "SPI.MIDDLE.GEO.COORD.PLOT_POINT.01", "SPI.MIDDLE.NUM.SIGNED_OPERATIONS.01"]`
- **answerTypes:** `["coordinate", "ordered-pair"]`
- **allowedRepresentations:** `["diagram", "graphical", "numeric"]`
- **calculatorPolicy:** `"calculator-not-required"`
- **successCriteria:** "Applies the correct mirror rule for the given line"; "States the image as an integer ordered pair"; "Recognises the line constant (`a` or `b`) rather than treating it as zero."
- **commonMisconceptions:** `["MISC.TRANS.WRONG_AXIS_X_FOR_Y", "MISC.TRANS.WRONG_AXIS_Y_FOR_X", "MISC.TRANS.NEGATE_WRONG_COORDINATE", "MISC.TRANS.YX_BOTH_SIGNS", "MISC.TRANS.YNEGX_SWAP_ONLY", "MISC.TRANS.LINE_CONSTANT_ZERO"]`
- **difficultyRange:** `{ "min": 2, "max": 3 }`

### 2.4 T4 — `SPI.MIDDLE.GEO.TRANS.REFLECT_SHAPE.01`
- **Wording:** "Reflect a labelled segment, triangle, or simple quadrilateral in a given line x = a, y = b, y = x, or y = −x, and state the coordinates of every image vertex by its corresponding label."
- **prerequisites:** `["SPI.MIDDLE.GEO.TRANS.REFLECT_POINT.01", "SPI.MIDDLE.GEO.COORD.PLOT_POINT.01", "SPI.MIDDLE.NUM.SIGNED_OPERATIONS.01"]`
- **answerTypes:** `["table-completion"]`
- **allowedRepresentations:** `["diagram", "graphical", "numeric"]`
- **calculatorPolicy:** `"calculator-not-required"`
- **successCriteria:** "Reflects every vertex in the same line"; "Completes one labelled row per image vertex"; "Image is congruent and orientation-reversed."
- **commonMisconceptions:** `["MISC.TRANS.WRONG_AXIS_X_FOR_Y", "MISC.TRANS.WRONG_AXIS_Y_FOR_X", "MISC.TRANS.NEGATE_WRONG_COORDINATE", "MISC.TRANS.YX_BOTH_SIGNS", "MISC.TRANS.YNEGX_SWAP_ONLY", "MISC.TRANS.LINE_CONSTANT_ZERO"]`
- **difficultyRange:** `{ "min": 2, "max": 4 }`

### 2.5 T5 — `SPI.MIDDLE.GEO.TRANS.ROTATE_POINT.01`
- **Wording:** "Rotate a single labelled point by 90°, 180°, or 270° about a given integer lattice-point centre, and state the coordinates of the image point as an ordered pair."
- **prerequisites:** `["SPI.MIDDLE.GEO.COORD.READ_POINT.01", "SPI.MIDDLE.GEO.COORD.PLOT_POINT.01", "SPI.MIDDLE.NUM.SIGNED_OPERATIONS.01"]`
- **answerTypes:** `["coordinate", "ordered-pair"]`
- **allowedRepresentations:** `["diagram", "graphical", "numeric"]`
- **calculatorPolicy:** `"calculator-not-required"`
- **successCriteria:** "Works relative to the stated centre, not the origin"; "Applies the correct quarter-turn sign rule for the given angle/direction"; "States the image as an integer ordered pair."
- **commonMisconceptions:** `["MISC.TRANS.ROT_WRONG_DIRECTION", "MISC.TRANS.ROT_ABOUT_ORIGIN", "MISC.TRANS.ROT_180_FOR_90", "MISC.TRANS.SWAP_WITHOUT_SIGN", "MISC.TRANS.ROTATE_THE_CENTRE"]`
- **difficultyRange:** `{ "min": 2, "max": 4 }`

### 2.6 T6 — `SPI.MIDDLE.GEO.TRANS.ROTATE_SHAPE.01`
- **Wording:** "Rotate a labelled segment, triangle, or simple quadrilateral by 90°, 180°, or 270° about a given integer lattice-point centre, and state the coordinates of every image vertex by its corresponding label."
- **prerequisites:** `["SPI.MIDDLE.GEO.TRANS.ROTATE_POINT.01", "SPI.MIDDLE.GEO.COORD.PLOT_POINT.01", "SPI.MIDDLE.NUM.SIGNED_OPERATIONS.01"]`
- **answerTypes:** `["table-completion"]`
- **allowedRepresentations:** `["diagram", "graphical", "numeric"]`
- **calculatorPolicy:** `"calculator-not-required"`
- **successCriteria:** "Rotates every vertex about the same centre by the same turn"; "Completes one labelled row per image vertex"; "Image is congruent and rotated as declared."
- **commonMisconceptions:** `["MISC.TRANS.ROT_WRONG_DIRECTION", "MISC.TRANS.ROT_ABOUT_ORIGIN", "MISC.TRANS.ROT_180_FOR_90", "MISC.TRANS.SWAP_WITHOUT_SIGN", "MISC.TRANS.ROTATE_THE_CENTRE", "MISC.TRANS.APPLY_TO_ONE_VERTEX"]`
- **difficultyRange:** `{ "min": 3, "max": 5 }`

### 2.7 T7 — `SPI.MIDDLE.GEO.TRANS.DESCRIBE_TRANSLATION.01`
- **Wording:** "Given a labelled non-symmetric triangle or irregular quadrilateral and its translated image on the coordinate grid, describe the single translation that maps the object onto the image, stating it as an exact integer column vector."
- **prerequisites:** `["SPI.MIDDLE.GEO.TRANS.TRANSLATE_SHAPE.01", "SPI.MIDDLE.GEO.COORD.CARTESIAN_PLANE.01", "SPI.MIDDLE.NUM.SIGNED_OPERATIONS.01"]`
- **answerTypes:** `["transformation"]` (the §7 discriminated-union descriptor; `kind: "translation"`)
- **allowedRepresentations:** `["diagram", "graphical", "symbolic"]`
- **calculatorPolicy:** `"calculator-not-required"`
- **successCriteria:** "Identifies the mapping as a translation"; "States the exact integer column vector `(dx, dy)`"; "Vector is nonzero and consistent across every labelled vertex pair." (Object type is restricted to non-symmetric triangle / irregular quadrilateral so the descriptor is unique — §1.5.)
- **commonMisconceptions:** `["MISC.TRANS.DESC_CORRECT_TYPE_WRONG_VECTOR"]`
- **difficultyRange:** `{ "min": 2, "max": 4 }`

### 2.8 T8 — `SPI.MIDDLE.GEO.TRANS.DESCRIBE_REFLECTION.01`
- **Wording:** "Given a labelled non-symmetric triangle or irregular quadrilateral and its reflected image on the coordinate grid, describe the single reflection that maps the object onto the image, stating the mirror line (x = a, y = b, y = x, or y = −x)."
- **prerequisites:** `["SPI.MIDDLE.GEO.TRANS.REFLECT_SHAPE.01", "SPI.MIDDLE.GEO.COORD.CARTESIAN_PLANE.01", "SPI.MIDDLE.NUM.SIGNED_OPERATIONS.01"]`
- **answerTypes:** `["transformation"]` (`kind: "reflection"`)
- **allowedRepresentations:** `["diagram", "graphical", "symbolic"]`
- **calculatorPolicy:** `"calculator-not-required"`
- **successCriteria:** "Identifies the mapping as a reflection (orientation reversed)"; "States the supported mirror line exactly"; "Mirror line is the perpendicular bisector of every labelled vertex pair." (Object type restricted per §1.5.)
- **commonMisconceptions:** `["MISC.TRANS.DESC_CORRECT_TYPE_WRONG_AXIS", "MISC.TRANS.DESC_NAMES_REFLECTION_FOR_ROTATION"]`
- **difficultyRange:** `{ "min": 3, "max": 4 }`

### 2.9 T9 — `SPI.MIDDLE.GEO.TRANS.DESCRIBE_ROTATION.01`
- **Wording:** "Given a labelled non-symmetric triangle or irregular quadrilateral and its rotated image on the coordinate grid, describe the single rotation that maps the object onto the image, stating the centre, the angle, and the direction (or 180°)."
- **prerequisites:** `["SPI.MIDDLE.GEO.TRANS.ROTATE_SHAPE.01", "SPI.MIDDLE.GEO.COORD.CARTESIAN_PLANE.01", "SPI.MIDDLE.NUM.SIGNED_OPERATIONS.01"]`
- **answerTypes:** `["transformation"]` (`kind: "rotation"`; canonical internal convention = quarter-turns anticlockwise, per §7)
- **allowedRepresentations:** `["diagram", "graphical", "symbolic"]`
- **calculatorPolicy:** `"calculator-not-required"`
- **successCriteria:** "Identifies the mapping as a rotation (orientation preserved)"; "States the exact integer centre"; "States the angle/direction (or 180°), canonicalising clockwise wording to anticlockwise quarter-turns." (Object type restricted per §1.5; ≥3 labelled vertices guarantee a non-degenerate basis for centre reconstruction — §9.4.)
- **commonMisconceptions:** `["MISC.TRANS.DESC_ANGLE_MISSING_CENTRE", "MISC.TRANS.DESC_CENTRE_WRONG_DIRECTION"]`
- **difficultyRange:** `{ "min": 3, "max": 5 }`

### 2.10 Prerequisite DAG (intra-family + external edges)

All edges point from prerequisite to dependent; the graph is acyclic and is enforced by `core/curriculum/graph-check.ts`. External (existing, verified-`approved`) roots are shown at the top. Every cited external root resolves (no unresolved-prerequisite warnings). The internal pattern is uniform: each shape task depends on the same-type point task; each describe task depends on the same-type shape task.

```
EXTERNAL ROOTS (existing, approved):
  SPI.MIDDLE.NUM.SIGNED_OPERATIONS.01
  SPI.MIDDLE.GEO.COORD.CARTESIAN_PLANE.01
        │
        ▼
  SPI.MIDDLE.GEO.COORD.READ_POINT.01 ──► SPI.MIDDLE.GEO.COORD.PLOT_POINT.01
        │                                          │
        └──────────────┬───────────────────────────┴───────────────┐
                       ▼                                            ▼ (+ PLOT_POINT, SIGNED_OPERATIONS on every node)

   T1 TRANSLATE_POINT        T3 REFLECT_POINT         T5 ROTATE_POINT
        │                         │                        │
        ▼                         ▼                        ▼
   T2 TRANSLATE_SHAPE        T4 REFLECT_SHAPE         T6 ROTATE_SHAPE
        │                         │                        │
        ▼                         ▼                        ▼
   T7 DESCRIBE_TRANSLATION   T8 DESCRIBE_REFLECTION   T9 DESCRIBE_ROTATION
```

Edges in words: T2←T1; T4←T3; T6←T5; T7←T2; T8←T4; T9←T6. Every node also depends on the relevant external roots as listed per objective: `SIGNED_OPERATIONS.01` and `PLOT_POINT.01` (hence transitively `READ_POINT.01` and `CARTESIAN_PLANE.01`) anchor the point/shape tasks; the describe tasks additionally cite `CARTESIAN_PLANE.01` directly. The graph test asserts these exact six intra-family edges, the four external roots, and that no cycle or duplicate ID is introduced when `SPI.MIDDLE.GEO.TRANS.json` is merged with the existing objective set.

---

## 3. Task and interaction matrix

### 3.1 Interaction and answer-shape decisions

**v1.0.0 ships exactly one interaction type: `free-response`.** Every one of the nine tasks is **free-response only** (`SUPPORTED_INTERACTIONS = ["free-response"]` in §1.4), so `supportedInteractionTypes = ["free-response"]` for every task. **No task offers `multiple-choice` in v1.0.0.** An explicit request for a multiple-choice interaction is **never silently downgraded to free-response**: the generator returns a clear unsupported-interaction error (§3.3) so an MC request fails loudly rather than being answered with an FR item. Multiple-choice is reserved as a possible later version; the misconceptions remain structured free-response diagnostics + feedback in the interim (§13).

**On answer types vs interactions (accurate platform position).** The `answerType` enum in `schemas/question-item.schema.json` **does** contain interaction-shaped tokens (`multiple-choice`, `multiple-select`, `matching`, `ordering`, `classification`) that exist for legacy / other-family uses (verified at the enum). This family deliberately keeps its `answerTypes[]` lists **MATHEMATICAL-only** (`coordinate` / `ordered-pair` / `table-completion` / `transformation`) and models multiple-choice purely as an `interactionType`, which v1.0.0 rejects with `interaction-not-supported`. No item ever places an interaction token in `answerTypes[]`; the schema permits MC tokens there, but this family never uses them — the constraint is a family policy, not a schema prohibition.

**Why free-response, and the answer-shape choices.** The architecture-proving features are (a) exact integer-coordinate image generation, (b) a structured **transformation-descriptor** answer contract, and (c) **multi-vertex structured coordinate** answers — all three are inherently free-response. Three answer shapes are used, each reusing an existing answer type where adequate and following the owner brief's answer-contract decisions verbatim:

- **Point-image tasks (T1, T3, T5)** — the image is a single point, so the answer is the **existing `coordinate`** answer type (an exact integer ordered pair `(x′, y′)`). `coordinate` is the precedent already used by every `gen.geometry.coordinate-lines` reading/plotting objective; the objective records list both `coordinate` and `ordered-pair` (the verified coordinate-lines convention) for schema stability, and the realised item answer is a single `coordinate`.
- **Shape-image tasks (T2, T4, T6)** — the image is a labelled multi-vertex polygon, so the answer is the **existing `table-completion`** answer type: **one row per labelled image vertex** (`A′ → coordinate`, `B′ → coordinate`, `C′ → coordinate`, and `D′ → coordinate` for quadrilaterals), with correspondence carried by the **vertex LABEL**, not by array order alone. This proves existing structured coordinate/table representations are adequate, so **no separate polygon-answer schema is introduced** (the owner brief requires that only if existing structures are proven inadequate — they are not). The `{cells:[{location, value}]}` **container** is reused; the per-cell `value` is a point object and the comparator is the §6 point-aware routine (not the integer-cell checker) — detailed in §6.
- **Describe tasks (T7, T8, T9)** — the answer is the single transformation that maps object to image, so the answer is the **one new `transformation`** answer type: the §7 discriminated union (`translation` / `reflection` / `rotation`). This is the **single** new answer type introduced by the family, flagged **OWNER-GATED**, additive, and back-compatible, following the **mensuration `quantity` precedent** exactly (additive `answerType` enum member + a structured top-level `answer.transformation` sibling, with conditional `if/then/const` discriminant rules — keyed on `kind` — enforced in BOTH the runtime Ajv validator recompiled via `scripts/compile-schemas.mjs` → `core/schema/compiled/` AND the Python conformance checker `oracle/check_conformance.py`). The schema delta, parser, formatter, canonicalizer, equivalence checker, structured feedback, backward-compatibility, Ajv, Python-conformance, and bank import/export impacts are specified in §7–§8 (cluster B). `coordinate`, `ordered-pair`, and `table-completion` are confirmed already present in the `answerType` enum (verified), so only `transformation` is a new token. The §16 build order applies the `transformation` enum extension to `question-item.schema.json` **before** the T7–T9 objective files are validated, so `answerTypes: ["transformation"]` resolves under both Ajv and `check_conformance.py`.

The mathematical misconceptions named in the owner brief (translation reversed/swapped/sign-wrong; reflection in the wrong axis or negating the wrong coordinate; rotation wrong-direction / origin-instead-of-centre / 180-rule-for-90; descriptor correct-type-wrong-parameter) are surfaced **only as deterministic free-response diagnostics + targeted feedback** (kind numeric / structured / pedagogical), each with an independently recomputed predicted response; they are never multiple-choice distractors and no arbitrary "nearby wrong coordinate" is manufactured (§13).

### 3.2 1:1 task → objective → interaction(s) → answer.shape matrix

This is the single source of truth for the per-task interaction and answer shape; it is keyed by the §1.4 slugs and is consumed verbatim by the generator dispatch, the descriptor/validator, the misconception `RULES_BY_TASK`, and the review-pack **COVERAGE-MATRIX** machinery (reused by name from mensuration/stats v1.0.x). "Answer-type token" lists the verbatim `answer.type` value; "Permitted object types" lists `objectTypeForTask`; "Image structure" describes the realised answer shape; "New token?" flags the single owner-gated schema addition.

| # | Task slug | Objective ID | Interaction(s) | Permitted object types | `answer.type` token | Image structure (realised answer shape) | New token? |
| --- | --- | --- | --- | --- | --- | --- | --- |
| T1 | `translate_point` | `SPI.MIDDLE.GEO.TRANS.TRANSLATE_POINT.01` | free-response | point | `coordinate` | single image point `(x′, y′)`, exact integers | no (existing) |
| T2 | `translate_shape` | `SPI.MIDDLE.GEO.TRANS.TRANSLATE_SHAPE.01` | free-response | segment / triangle / quadrilateral | `table-completion` | one labelled row per image vertex (A′…D′); correspondence by label | no (existing) |
| T3 | `reflect_point` | `SPI.MIDDLE.GEO.TRANS.REFLECT_POINT.01` | free-response | point | `coordinate` | single image point `(x′, y′)`, exact integers | no (existing) |
| T4 | `reflect_shape` | `SPI.MIDDLE.GEO.TRANS.REFLECT_SHAPE.01` | free-response | segment / triangle / quadrilateral | `table-completion` | one labelled row per image vertex (A′…D′); correspondence by label | no (existing) |
| T5 | `rotate_point` | `SPI.MIDDLE.GEO.TRANS.ROTATE_POINT.01` | free-response | point | `coordinate` | single image point `(x′, y′)`, exact integers | no (existing) |
| T6 | `rotate_shape` | `SPI.MIDDLE.GEO.TRANS.ROTATE_SHAPE.01` | free-response | segment / triangle / quadrilateral | `table-completion` | one labelled row per image vertex (A′…D′); correspondence by label | no (existing) |
| T7 | `describe_translation` | `SPI.MIDDLE.GEO.TRANS.DESCRIBE_TRANSLATION.01` | free-response | **triangle / quadrilateral only (non-symmetric)** | `transformation` | `{kind:"translation", vector:{dx:int, dy:int}}` (nonzero) | **yes (owner-gated)** |
| T8 | `describe_reflection` | `SPI.MIDDLE.GEO.TRANS.DESCRIBE_REFLECTION.01` | free-response | **triangle / quadrilateral only (non-symmetric)** | `transformation` | `{kind:"reflection", axis:{…}}` (x = a / y = b / y = x / y = −x) | **yes (owner-gated)** |
| T9 | `describe_rotation` | `SPI.MIDDLE.GEO.TRANS.DESCRIBE_ROTATION.01` | free-response | **triangle / quadrilateral only (non-symmetric)** | `transformation` | `{kind:"rotation", centre:{x:int, y:int}, quarterTurnsCCW:1\|2\|3}` | **yes (owner-gated)** |

**Object-type restriction (T7–T9).** Per §1.5, the three describe tasks restrict `objectTypeForTask(describe_*) ∈ {triangle, quadrilateral}` and additionally require non-symmetry (scalene triangle: three distinct squared side lengths; irregular quadrilateral: trivial symmetry group). **Point and segment are excluded for describe tasks** because they admit infinitely many (point) or two (segment) allowed descriptors and can never be made unique. The six perform tasks accept point / segment / triangle / quadrilateral as before. A named test asserts the guard for each describe task.

**Interaction summary:** every task is **free-response**; **no task offers multiple-choice** in v1.0.0. Exactly **one** new `answer.type` token (`transformation`) is introduced, for the three describe tasks only; the six point/shape tasks reuse the existing `coordinate` and `table-completion` types. The COVERAGE-MATRIX required cells = every task × supported interaction (`free-response`) × reachable difficulty band × realised answer shape, derived from the §14 distribution report; the pack builder **fails on any missing reachable cell**. Because the answer shape varies by partition, the matrix's "realised answer shape" axis additionally records the descriptor `kind` for the three describe tasks (`translation` / `reflection.axis-kind` ∈ {vertical, horizontal, diagonal y=x, diagonal y=−x} / `rotation.quarterTurnsCCW` ∈ {1, 2, 3}) and the vertex count (segment = 2, triangle = 3, quadrilateral = 4) for the shape tasks. **Reachability correction:** the `obj:point` and `obj:segment` coverage cells are required **only for the perform point/shape tasks**, never for the describe tasks (whose object types are restricted to triangle / quadrilateral), so the reachability-derived matrix does not demand an unreachable describe cell. With this correction the brief's review-pack coverage (all transformation types, all reflection lines, all 90/180/270 rotations, origin + non-origin centres, points/segments for perform tasks, triangles/quadrilaterals across both perform and describe) is provably exercised and blocked on if missing.

### 3.3 Scope guard (exactly the nine tasks)

The task enum `TRANSFORMATIONS_TASKS` (§1.4) has exactly nine members; the generator dispatch is a **total function** over that enum with no default branch, and the conformance/graph tests assert the objective set, the task set, the `RULES_BY_TASK` key set, and the coverage matrix all have **cardinality nine** and an **identical key set** (§1.4(c)). The `objectTypeForTask` guard (§1.4(f), §3.2) is a second total function: it returns `point` ∪ `{segment, triangle, quadrilateral}` for the perform tasks and **`{triangle, quadrilateral}` only** for the describe tasks, with a named test asserting that a describe task can never be constructed over a point or segment object.

Because every task declares `supportedInteractionTypes = ["free-response"]`, any request for a `multiple-choice` interaction is rejected with a clear **unsupported-interaction error** (`interaction-not-supported`), never silently satisfied with a free-response item; a named test asserts that an MC request returns this error for **each of the nine tasks**.

Every deferred topic — enlargements / scale factors (fractional, negative), compositions of transformations, invariant-line/point proofs, arbitrary reflection lines, arbitrary-angle / trig-requiring rotations, fractional translation vectors, fractional rotation centres, transformations of curves / functions, tessellations, matrices as the required student method, and 3D transformations — is **deterministically excluded by construction**: there is no task slug, objective ID, or generator branch that can emit one, and each exclusion is asserted by a named test (§12 / §14 / §15), not merely filtered at runtime.


---

## 4. Canonical transformation model

### 4.1 One union, every consumer

The family defines exactly **one** exact `Transformation` discriminated union. It is the *single source of truth* threaded through parameter generation, prompt construction, the coordinate calculator, student media, answer generation (point and shape), worked-solution overlays, the misconception/diagnostic registry, accessibility text, and the independent validator. No consumer re-derives a transformation by inspecting source/image coordinates and no consumer carries a private second representation; the descriptor object IS the transformation. This mirrors the mensuration precedent of one `Shape` model feeding every channel, and it is what makes `transformed-coordinate-agreement`, `descriptor-unique`, and `inverse-transformation-restores-source` checkable against a single canonical object rather than against forward-helper output.

The union is also the structured payload of the new `answer.type: "transformation"` (Section 7) for the three `describe_*` tasks; the generation-side `Transformation` and the answer-side descriptor are the **same shape**, so the canonicalizer and equivalence checker (Section 8) operate identically on the generator's intended transformation and on a parsed student response.

### 4.2 Discriminant and field shapes

`Transformation` is discriminated on `kind ∈ {"translation", "reflection", "rotation"}`. Every numeric field is an **integer** (`int`, JSON `integer`); there are no `Rational`, float, angle-in-degrees, or trig fields anywhere in the union — degrees appear only in *display* strings produced by the formatter, never in the stored model.

| `kind` | Fields | Constraints |
|---|---|---|
| `translation` | `vector: { dx: int, dy: int }` | `(dx, dy) ≠ (0, 0)` (nonzero vector; zero vector is an edge-case exclusion, Section 14) |
| `reflection` | `axis: ReflectionAxis` (below) | one of four supported lines only |
| `rotation` | `centre: { x: int, y: int }`, `quarterTurnsCCW: 1 \| 2 \| 3` | integer lattice centre; `0` excluded (identity), `4`≡`0` excluded |

`ReflectionAxis` is itself a closed discriminated union on `kind ∈ {"vertical", "horizontal", "diagonal"}`:

| Axis `kind` | Fields | Line meaning |
|---|---|---|
| `vertical` | `value: int` | the line `x = value` (this is `x = a`) |
| `horizontal` | `value: int` | the line `y = value` (this is `y = b`) |
| `diagonal` | `equation: "y=x" \| "y=-x"` | the line `y = x` or `y = -x` |

This is the **only** axis vocabulary v1.0.0 admits. Any other reflection line (e.g. `y = x + 1`, `y = 2x`, arbitrary lines) is out of scope and is rejected at parse time and excluded at generation time (Sections 8, 14). The `equation` discriminator is a string literal — never a parsed expression — so there is no float or slope arithmetic.

The full union is realised in `if/then/const` discriminant form in the Section 7 schema delta (NOT as `oneOf`, because `oracle/check_conformance.py` honours `const`/`allOf`/`if-then` but has no `oneOf` branch — the exact `measure`-block precedent), so the same `kind`-keyed structure is enforced identically by runtime Ajv and Python conformance.

### 4.3 Canonical rotation-direction convention

There is **one** internal convention: positive quarter-turns are **anticlockwise (ACW / CCW)**. `quarterTurnsCCW` therefore takes exactly `1 | 2 | 3` (90°, 180°, 270° anticlockwise). All human direction wording is normalized into this convention by the canonicalizer (Section 8):

- 90° **clockwise** → `quarterTurnsCCW: 3`
- 270° **clockwise** → `quarterTurnsCCW: 1`
- 180° has **no direction distinction** → always `quarterTurnsCCW: 2`, and any direction word ("clockwise"/"anticlockwise") attached to a 180° rotation is accepted but discarded as canonically irrelevant (it is never treated as a contradiction).

Storing turns rather than signed degrees guarantees `quarterTurnsCCW` is closed over composition-free canonical comparison and removes the only place a sign error could hide.

### 4.4 Exact integer coordinate rules (verbatim, no trigonometry)

The coordinate calculator applies these rules and **only** these rules. Every map below sends integer coordinates to integer coordinates, satisfying `integer-coordinate-closure` by construction — no rounding, no `gridRound` on math (that projection is *rendering only*), no tolerance, no irrational, no `sin`/`cos`.

**Translation** by `(dx, dy)`:
```
(x, y) → (x + dx, y + dy)
```

**Reflection** in the four supported lines:
```
reflect x = a   :  (x, y) → (2a − x,  y)
reflect y = b   :  (x, y) → (x,  2b − y)
reflect y = x   :  (x, y) → (y,  x)
reflect y = −x  :  (x, y) → (−y, −x)
```
(`a` is `axis.value` for `vertical`; `b` is `axis.value` for `horizontal`; the two diagonal forms are coordinate swaps with no parameter.)

**Rotation** about centre `(h, k)` by `quarterTurnsCCW`: translate to centre, apply the exact quarter-turn map to the relative vector `(x − h, y − k)`, translate back by `(h, k)`:

| `quarterTurnsCCW` | Relative map `(x − h, y − k) →` | Net image |
|---|---|---|
| `1` (90° ACW) | `(−(y − k),  x − h)` | `(h − (y − k),  k + (x − h))` |
| `2` (180°) | `(−(x − h), −(y − k))` | `(2h − x,  2k − y)` |
| `3` (270° ACW) | `(y − k,  −(x − h))` | `(h + (y − k),  k − (x − h))` |

Because `h`, `k`, `x`, `y` are all integers, every relative vector and every image coordinate is an exact integer; `2h − x` etc. are exact. **No runtime trigonometry exists in this family** — the same byte-identical rules are implemented in `oracle/spi_oracle/transformations.py` (oracle-first) and the TS mirror, so canonical-item and canonical-SVG parity hold over the transformation output exactly as they do for coordinate-lines.

### 4.5 Forward map, inverse map, and orientation

A single helper `applyTransform(T, point) → point` realises 4.4. The inverse `inverseTransform(T) → T⁻¹` is defined for `inverse-transformation-restores-source`:

| `T` | `T⁻¹` |
|---|---|
| translation `(dx, dy)` | translation `(−dx, −dy)` |
| reflection (any axis) | the **same** reflection (involution) |
| rotation `(h,k), q` | rotation `(h,k), (4 − q)` (so `1↔3`, `2↔2`) |

Reflections reverse orientation (handedness flips); translations and rotations preserve it. This orientation fact is the load-bearing primitive for describe-task uniqueness (4.7 and Section 5.5): a no-symmetry source admits exactly one *direct* isometry (translation or rotation) and at most one *opposite* isometry (reflection), and orientation alone distinguishes the two classes. The validator's `rotation-quarter-turn-agreement` and `reflection-axis-condition` checks consume this orientation fact (Section 12). Applying `applyTransform(inverseTransform(T), ·)` to every image vertex must reproduce the source vertex set with labels intact — checked exactly, never within a tolerance.

### 4.6 Where the model is consumed (single-source contract)

| Consumer | Uses |
|---|---|
| Parameter generation | constructs a `Transformation`, then derives the image via `applyTransform` |
| Prompt construction | the formatter (Section 8) renders `T` to instruction text (perform tasks) |
| Coordinate calculator | `applyTransform` per source vertex → image vertices |
| Student media | reads `T` only to label the instruction (perform) or to omit it (describe) |
| Answer generation | point image → `coordinate`/`ordered-pair`; shape image → `table-completion`; describe → canonical `transformation` descriptor (= `T` itself) |
| Worked solution | additive overlay narrates `T` step-by-step over byte-identical base geometry |
| Diagnostics | each rule perturbs `T` or `applyTransform` deterministically (Section 13); predicted-wrong outputs feed ONLY the checker / worked-solution pitfall notes / validator recompute — they NEVER enter any student or answer-key SVG channel or a11y field (Sections 11, 13) |
| Accessibility | spoken-math/alt text describe `T` and the image in words |
| Independent validator | reconstructs `T` from source+image and asserts uniqueness, never calling the forward helper |

### 4.7 Reconstruction primitive for describe tasks (centre recovery)

Describe-task validation (Section 12) reconstructs `T` from the labelled source/image vertex sets *without* calling `applyTransform`. The two non-trivial recoveries are:

- **Translation candidate.** The single vector `(x′−x, y′−y)` must be *identical* across every corresponding pair and nonzero (`translation-vector-consistent`).
- **Rotation candidate (centre recovery).** The bisector-intersection-of-two-pairs method is **not** the primitive, because it degenerates for 180° (every perpendicular bisector passes through the common midpoint; two chosen bisectors can be parallel/identical and fail to meet at a unique point). Instead:
  1. **180° hypothesis first, via common midpoint.** Compute the midpoint of every corresponding pair `((x+x′)/2, (y+y′)/2)`. If all midpoints coincide AND are integer lattice points, the candidate is `rotation centre = that midpoint, quarterTurnsCCW = 2`. This route never degenerates and needs no bisector intersection.
  2. **90°/270° hypothesis.** Recover the centre as the fixed point of the quarter-turn relation using **at least two corresponding pairs whose connecting directions are non-parallel**, rejecting any collinear/degenerate pair selection; require the recovered centre to be an exact integer lattice point (reject otherwise).

  Because describe tasks are restricted to triangles and quadrilaterals (Section 5.5), **≥3 distinct, non-collinear labelled vertices are always available**, so a non-degenerate non-parallel pair is guaranteed and the centre recovery never stalls on a degenerate basis.

The full named-check wiring (`rotation-centre-condition`, `descriptor-unique`) lives in Section 12; this subsection only fixes the *primitive* so generation and validation agree.

---

## 5. Source/image shape model

### 5.1 One labelled-shape model

A second canonical model, `LabelledShape`, represents every geometric object the family draws and transforms. The **same** `LabelledShape` type carries both the **source** (object) and the **image**; they differ only by their `role` field and (for the image) the application of a `Transformation`. This keeps a single congruence-preserving model feeding generation, rendering, answer construction, and validation, exactly as the mensuration `Shape` model does for its renderer and perimeter/area engine.

### 5.2 Field shapes

```
LabelledShape {
  kind:        "point" | "segment" | "triangle" | "quadrilateral"
  role:        "source" | "image"
  vertices:    LabelledVertex[]        // ordered; 1 / 2 / 3 / 4 entries by kind
  edges:       [int, int][]            // index pairs into vertices (connectivity)
  rendering:   RenderMeta              // marker shape, line pattern, fill pattern, role styling
  accessibility: A11yMeta             // per-vertex spoken label, figure role description
}

LabelledVertex {
  label:      "A" | "B" | "C" | "D"    // source base label (ASCII)
  isImage:    bool                     // false for source; true for image
  coord:      { x: int, y: int }       // EXACT integer coordinates — always
}
```

- **Labels and the prime byte-parity contract.** Source vertices use `A, B, C, D` in vertex order; the corresponding image vertices use the primed labels `A′, B′, C′, D′`. The prime is **NOT** stored as part of a free-form glyph string in the structural model. The base label (`A`…`D`, ASCII) plus the `isImage` boolean is the structural key; the displayed primed glyph is *derived* at render/serialize time by a single shared helper `primeLabel(base)` that emits the prime as **U+2032 PRIME encoded as UTF-8 (bytes `E2 80 B2`)** in BOTH the Python oracle and the TS mirror. Because the structural correspondence key is ASCII and the glyph is emitted by one byte-pinned helper, there is no encoding divergence:
  - the SVG label text, the `answer.canonical.cells[].location` key (Section 6), `accessibility.spokenMath`, and `longDescription` all route through `primeLabel`;
  - `canonicalStringify` (used by `serialize`) must not escape/normalize the U+2032 bytes — a parity-fixture row asserts the location keys and SVG label bytes are **byte-identical Py↔TS**, alongside the existing canonical-item/canonical-SVG parity gates.
  Correspondence is carried by **base label + `isImage`**, never by array position alone — `vertex-label-correspondence` matches student row `A′ → (…)` to source `A` even if rows are reordered (Section 6's table-completion correspondence rule).
- **Vertex count by kind.** `point` 1, `segment` 2, `triangle` 3, `quadrilateral` 4.
- **Edges / connectivity.**
  - `point`: `[]`
  - `segment`: `[[0,1]]`
  - `triangle`: `[[0,1],[1,2],[2,0]]`
  - `quadrilateral`: `[[0,1],[1,2],[2,3],[3,0]]` (the vertex order **is** the simple boundary cycle)
- **`rendering` (`RenderMeta`).** Carries the non-colour distinguishers required by the visual-design brief: a `markerShape` (filled disc for source vs. open square for image), a `linePattern` (solid for source vs. dashed for image), and a `fillPattern` (plain vs. dot/hatch) **per role**, so source and image are distinguishable in **monochrome print where shape/dash/fill is the authoritative cue and colour is redundant only** (Section 5.6). Concrete colours/strokes are NOT stored here — they come from the additive versioned `transformations-theme` extension over `core/visual-style/cartesian-theme.{json,ts}` (the same per-root `cx-figure` CSS-custom-property isolation and `COMMON_CSS`/`modeVars`/`presentationSvg`/`exportSvg`/`MODES`, with modes `print` / `premium` / `premium-dark` / `accessible`). The approved Cartesian renderer contract is **not modified in place**; transformation-specific marker/line/fill styling is an additive theme layer, exactly as `data-chart-theme` and `mensuration-theme` extend `cartesian-theme.ts`.
- **`accessibility` (`A11yMeta`).** Per-vertex spoken coordinate, a figure-level role sentence ("triangle A B C, the object" / "triangle A-prime B-prime C-prime, the image"), and the source/image distinction stated in words (never "the blue one") so `source-image-distinction-not-colour-only` holds in the alt text as well as the figure. For `describe_*` tasks, the a11y payload lists **only** the labelled source and image coordinates and **never** names the transformation, mirror line, rotation centre, vector, or angle (unless the task statement itself supplies a given line/centre) — the describe-task analogue of the perform-task `student-a11y-does-not-state-result` leakage guard (Sections 11, 12).

### 5.3 Deriving the image shape

The image `LabelledShape` is produced from the source by mapping every vertex coordinate through `applyTransform(T, ·)` (Section 4.4), copying `kind`, copying `edges` **unchanged** (connectivity is invariant), setting `isImage: true` on each vertex, and setting `role: "image"`. Because `T` preserves congruence and the edge list is copied verbatim, the image is automatically a congruent, correspondence-preserving copy — no separate "image builder" can drift from the source topology.

### 5.4 Invariants (enforced at generation; re-proved by the validator)

Every generated item must satisfy all of the following. Generation that violates any of these triggers deterministic regeneration via the seeded redraw loop (call-order parity preserved, Section 14); the independent validator (Section 12) re-proves each invariant from params by a second route.

**Structural (per shape, source and image):**

| Invariant | Statement |
|---|---|
| `labels-unique` | the 1–4 base labels within a shape are distinct (`A,B,C,D`) |
| `vertices-distinct` | no two vertices share a coordinate |
| `segment-nonzero` | a `segment`'s two endpoints differ (nonzero length) |
| `triangle-non-collinear` | the three vertices are not collinear — checked by exact integer signed area `(x_B−x_A)(y_C−y_A) − (x_C−x_A)(y_B−y_A) ≠ 0` (no floats) |
| `quadrilateral-simple` | the four edges form a simple, **non-self-intersecting** cycle (exact integer segment-intersection test, the same orientation/`segmentsTouch` style used by the mensuration L-shape simplicity check) |

**Correspondence and congruence (source ↔ image):**

| Invariant | Statement |
|---|---|
| `correspondence-preserved` | image vertex `X′` is exactly `applyTransform(T, X)`; edge `[i,j]` maps to `[i,j]` |
| `image-congruent-to-source` | image is congruent to source — same `kind`, same edge multiset |
| `side-lengths-unchanged` | every corresponding side has equal **squared** length (exact integer `Δx²+Δy²`; no `sqrt`, no float) |
| `internal-angles-unchanged` | corresponding internal angles equal — verified via equal corresponding squared side lengths (SSS congruence over exact integers), never by computing angles |

**Placement (window + viewport):**

| Invariant | Statement |
|---|---|
| `within-supported-window` | every source and image coordinate lies inside the supported coordinate window (a bounded integer range, provisional pending the distribution sweep, e.g. `[−10, 10]²` in the coordinate-lines spirit) |
| `viewport-contains-source-and-image` | the rendered viewport contains every source vertex, every image vertex, and every label — computed by a transformations-local viewport function re-implemented byte-identically from the coordinate-lines `viewport(reqPoints)` logic (see 5.7), fed the **union** of source + image points (and, for answer-key figures, the axis/centre overlay points), with `DATA_MARGIN_UNITS` padding and the `U_MIN` minimum-unit rejection |
| `equal-axis-scale` | one unit scale `U` for both axes (the approved renderer's equal x/y unit invariant) |
| `no-label-collision` | source and image labels (and figures) do not overlap beyond the approved clearance; collisions are an edge-case exclusion (Section 14). Feasibility is decided by a transformations-specific label-feasibility function (5.7) — NOT by the coordinate-lines `labelsFeasible`, which is hard-coded per coordinate-lines task and returns vacuously true for any unknown task |

### 5.5 Describe-task object-type RESTRICTION (not preference) and the non-symmetry predicate

The three `describe_*` tasks are **restricted**, by an affirmative generation rule and a named guard, to object types that can yield a **provably unique** descriptor. They are **not** merely biased toward such objects.

**Hard restriction.** `objectTypeForTask(describe_translation) = objectTypeForTask(describe_reflection) = objectTypeForTask(describe_rotation) ∈ {triangle, quadrilateral}`. **Points and segments are excluded from describe tasks entirely.** A named test `describe-object-type-restricted` asserts every emitted describe item carries `objectType ∈ {triangle, quadrilateral}`; the perform tasks (`*_point`, `*_shape`) are unaffected (point/segment remain valid perform objects). The Section 15 coverage matrix is corrected to require `obj:point`/`obj:segment` cells **only for the perform point/shape tasks**, never for `describe_*`, so the reachability-derived matrix does not demand an unreachable cell and the §10 redraw loop never exhausts `MAX_PARAM_ATTEMPTS` on an inherently-ambiguous point/segment describe instance.

**Why points and segments are inadmissible (mathematical justification).** Descriptor uniqueness needs the labelled vertex set to pin a single allowed isometry.
- A **single labelled point** `A → A′` is mapped by **one** translation but also by **infinitely many** rotations (any centre on the perpendicular bisector of `AA′`, any angle) and reflections — infinitely many allowed descriptors fit, so uniqueness is unachievable for *every* point instance.
- A **labelled segment** (2 points, necessarily collinear as a set) is fixed by an isometry only up to orientation, so a reflection and a rotation can produce the **identical labelled image**. Concretely, source `A=(0,0), B=(1,0)`: reflection in `y=x` gives `A′=(0,0), B′=(0,1)`; rotation 90° ACW about the origin gives the *same* labelled image `A′=(0,0), B′=(0,1)`. Two valid allowed descriptors ⇒ `descriptor-unique` must reject every such instance. The ambiguity is **inherent to the degenerate (collinear) figure**, not to a particular placement, so no redraw can rescue it.
- The root cause is vertex count and orientation: distinguishing 180°-rotation from translation needs ≥2 vertices (a non-constant difference); distinguishing reflection from rotation needs *orientation*, which a collinear figure cannot pin per label.

**Why a no-symmetry triangle/quadrilateral IS provably unique.** A labelled figure with **trivial symmetry group** (no nontrivial isometry maps the labelled vertex set to itself) admits **exactly one direct isometry** (the unique translation-or-rotation) and **at most one opposite isometry** (a reflection); the orientation fact (Section 4.5) selects between the two classes, and the no-symmetry condition forbids a second member within either class. Hence exactly one allowed `Transformation` maps every labelled source vertex to its corresponding image vertex — the descriptor is unique.

**Exact-integer non-symmetry acceptance predicate** (evaluated at generation; re-proved by the validator's `no-ambiguous-symmetry`, all over exact integers, no floats):

| Object | Predicate (all exact integer) |
|---|---|
| `triangle` | **Scalene**: the three squared side lengths `\|AB\|², \|BC\|², \|CA\|²` are pairwise distinct. (Distinct squared lengths ⇒ no nontrivial isometry permutes the labelled vertices ⇒ trivial symmetry group.) |
| `quadrilateral` | **Trivial symmetry group**: no nontrivial isometry maps the labelled cyclic vertex set `(A,B,C,D)` to itself. Implemented as: the multiset of the four edge squared-lengths together with the two diagonal squared-lengths admits **no** rotation/reflection of the label cycle that reproduces the same labelled distance pattern — i.e. for each of the 7 nontrivial dihedral relabelings of `(A,B,C,D)`, at least one corresponding squared distance differs. (Reject if any nontrivial relabeling matches — that would be a symmetry admitting a second allowed descriptor.) |

Symmetric figures — those whose symmetry group would let several allowed descriptors fit, or where a fixed point or unchanged object hides the intended mapping — are deterministically excluded (Section 14) and independently caught by `descriptor-unique` / `no-ambiguous-symmetry` (Section 12). Because describe is restricted to triangles/quadrilaterals, ≥3 distinct non-collinear labelled vertices are always available, which also guarantees the non-degenerate centre-recovery basis required by Section 4.7. The model therefore never emits a describe item whose answer is not a single canonical descriptor.

### 5.6 Non-colour distinction and the monochrome greylist

The source/image distinction is carried by **marker shape + line dash + fill pattern** (filled disc / solid edge / plain fill for source vs. open square / dashed edge / dot-or-hatch fill for image), with colour a **redundant** cue only. In the byte-parity canonical/print render the distinction is therefore shape/pattern-borne, never grey-value-borne, since two greys can be visually close. Every new `--cx-*` colour variable introduced by the `transformations-theme` extension must resolve to a member of the approved print greylist `GREYS = {#111,#333,#444,#555,#888,#bbb,#fff}` (coordinate-lines `no-colour-only-information` check) in the `print` mode, and a theme-completeness assertion (mirroring the §16 style-isolation gate) requires every declared `--cx-*` variable to have a print-mode greyscale value. The same shape/dash/fill distinction is restated in the accessibility text (5.2) so `source-image-distinction-not-colour-only` holds in figure, print, and alt text alike.

### 5.7 Reused vs. re-implemented infrastructure (no in-place edit of the approved renderer)

The shared, exported, reused layer is **`core/visual-style/cartesian-theme.ts`** (`COMMON_CSS`, `modeVars`, `presentationSvg`, `exportSvg`, `MODES`, the 6000×4200 export defaults) — these are genuinely exported and are consumed unchanged. The Cartesian grid/axes/lattice-point **geometry primitives** of `domains/geometry/coordinate-lines.ts` (`viewport`, `projX/projY`, `gridRound`, `labelsFeasible`, `U_MIN`, `DATA_MARGIN_UNITS`) are **module-private** (verified: declared `function`/`const`, not `export`); they CANNOT be imported without adding `export` to the approved module, which would be an in-place modification. They are therefore **re-implemented byte-identically inside the new transformations module** (Python oracle authoritative, TS mirror) — exactly as `domains/measurement/mensuration.ts` defines its **own** `gridRound` and its own `STYLE` constant rather than importing them. The transformations module:

- re-implements `viewport`/`projX`/`projY`/`gridRound` byte-identically and a **transformations-specific** label-feasibility function (modelled on `labelsFeasible`, reusing its `16/30/16/16` canvas-bound and `44`-pixel (`44²` squared) minimum-separation constants) that feeds the **union** of source + image vertices — plus centre/axis overlay points for the answer-key channel — through the projection and asserts every projected label box lies within the canvas with pairwise minimum separation. The coordinate-lines `labelsFeasible` is **not** reused, since it is hard-coded per coordinate-lines task and would return vacuously true for the transformation vertex sets;
- reuses the **mensuration** channel-group pattern by name — `cx-base` / `cx-annot` / `cx-overlay` groups, the `class="cx-figure"` root with `<title>`/`<desc>` as first children, `extractGroup`, `renderSvg(…, channel, …)`, and the `answer-key-base-geometry-identical` / `answer-key-overlay-additive-only` checks (these are the **mensuration** precedent, not coordinate-lines, whose `figure()` emits a flat, ungrouped SVG with no `cx-figure` root). The transformation `figure()` is a **new** composing function modelled on `mensuration.renderSvg`, not a reuse of `coordinate-lines.figure()`;
- bakes a single hardcoded **monochrome** `STYLE` constant (extending the coordinate-lines/mensuration `GREYS` palette) into the canonical `media[0].svg`; the four themed modes (`premium` / `premium-dark` / `accessible` / `print`) are **TS-only post-hoc derivations** via `presentationSvg()`/`exportSvg()` (strip canonical style + inject `modeVars`), exactly as `mensuration-theme.ts`. Byte-parity is asserted over the **monochrome canonical SVG only**.

This reconciles the two contracts: the approved coordinate-lines/cartesian renderer is **not edited in place**, and the only import-level reuse is the genuinely-exported `cartesian-theme.ts` layer.

### 5.8 Role/channel rendering hook

`role` is the hook the SVG contract (Section 11) reads to build the approved base-geometry + additive-overlay channels: the **student** figure renders `role: "source"` always, and `role: "image"` only for `describe_*` tasks (perform tasks hide the image); the **answer-key** figure adds the `role: "image"` shape plus the transformation overlay (vector arrow / reflection axis / rotation centre + quarter-turn arc) as an **additive `cx-overlay` group over byte-identical `cx-base` geometry**, exactly the approved mensuration student-vs-answer-key channel pattern. The answer-key overlay shows only the **correct** image/axis/centre/arc — never any diagnostic-predicted (misconception) marker, which is confined to the checker/solution/validator per Sections 4.6 and 13. No coordinate, marker, or pattern in this model is colour-dependent for meaning.


---

## 6. Coordinate-answer representation

The six **perform** tasks (`translate_point`, `translate_shape`, `reflect_point`, `reflect_shape`, `rotate_point`, `rotate_shape`) reuse answer contracts that already exist in `schemas/question-item.schema.json` and are already exercised by the APPROVED `gen.geometry.coordinate-lines` (v1.0.2) and `gen.statistics.data-handling` families. **No new answer type is introduced for any perform task.** This is the proposal's first economy: every transformation image is, structurally, either one lattice point or a label→lattice-point table, both of which the platform already represents and validates.

A platform note on answer types vs interactions, stated accurately: the `$defs.answerType.enum` (lines 196–205) *does* contain interaction-shaped tokens — `multiple-choice`, `multiple-select`, `matching`, `ordering`, `classification` — present for legacy and other families. This family makes no use of them: it deliberately keeps every objective's `answerTypes[]` **MATHEMATICAL-only** (`coordinate`, `ordered-pair`, `table-completion`, `transformation`) and models multiple-choice purely as an **`interactionType`** that v1.0.0 rejects with an `interaction-not-supported` result (no silent MC→FR conversion, §3). So the family never adds an interaction token to any `answerTypes[]` list; only that policy choice — not the schema enum — bars MC here.

### 6.1 Point-image tasks → existing `coordinate` / `ordered-pair`

`translate_point`, `reflect_point`, and `rotate_point` map a single labelled source point `P` to a single image point `P′`. The answer is exactly one ordered pair of **exact integers**, so the contract is the existing `coordinate` (geometric point on the Cartesian plane) / `ordered-pair` (general ordered pair) answer type — identical to `coordinate-lines` `read_point` / `plot_point` / `midpoint`.

**Canonical encoding** — the byte-identical Py↔TS point object produced by `enc_pt`/`enc_rat` (verified at `oracle/spi_oracle/coordinate_lines.py` lines 117/125; the `{x:{num,den},y:{num,den}}` shape is exactly what those functions emit) and its TS mirror, with the equivalence comparator `_same_value` (line 457) and the display routine `disp_pt` (line 129). These are re-implemented byte-identically inside the new transformations oracle/module (Python authoritative, TS mirror) — they are module-private in `coordinate_lines.py` and are NOT import-coupled, matching the family's no-modification-of-approved-renderer contract.

```
answer.type      = "coordinate"        // point-on-plane tasks (translate_point, reflect_point, rotate_point)
answer.canonical = { "x": {"num": <int>, "den": 1}, "y": {"num": <int>, "den": 1} }
answer.display   = "(x, y)"            // disp_pt: e.g. "(-3, 5)"
```

- `den` is **always 1** — transformations of integer-coordinate objects by V1.0.0 rules (§9) are integer coordinate maps, so the rational invariant `den ≥ 1, reduced` holds trivially with `den = 1`. The independent validator's `integer-coordinate-closure` check (§12) asserts `den === 1` on every component; a non-unit denominator is a generator defect, not a valid item.
- The point micro-objectives (T1/T3/T5) list `answerTypes: ["coordinate", "ordered-pair"]` — **both** — exactly as the approved `coordinate-lines` objectives do (verified: its objective record lists `["coordinate","ordered-pair", …]`). This keeps the objective schema-stable if a later task needs the non-geometric `ordered-pair` form, and resolves the prior §2/§6 inconsistency: **§2's T1/T3/T5 records carry `["coordinate","ordered-pair"]`**, and in v1.0.0 every point item *emits* `coordinate`.

No schema change. No `accepts`/`tolerance` block (exact-only; tolerance is FORBIDDEN on exact types per the schema's own `tolerance` description, line 229). The equivalence check is component-wise integer equality (`_same_value`), reused verbatim.

### 6.2 Shape-image tasks → existing `table-completion` (one row per labelled image vertex)

`translate_shape`, `reflect_shape`, `rotate_shape` map a labelled source polygon (segment = 2 vertices, triangle = 3, simple quadrilateral = 4) to its image. The answer is the set of **image vertices keyed by label** (`A′, B′, C′, D′`). The contract is the existing `table-completion` answer type — the **container type** `gen.statistics.data-handling` already uses — with **one row per labelled image vertex** and **correspondence carried by the vertex label, not by array order**.

**Container reuse vs new value comparator — stated precisely.** Only the `{cells:[{location,value}]}` *container shape* is reused. The verified live precedent (`oracle/spi_oracle/data_handling.py` line 638) emits each cell as `{"location": <str>, "value": <int>}` with a **bare integer** value, and its round-trip (`_table_round_trip`, line 1637) parses `<td>(\d+)</td>` — both **integer-specific**. The transformation value domain is a **point object**, so the data_handling integer cell checker and integer-`<td>` round-trip are **NOT reused**. Instead:

- the per-cell **value comparison** reuses the point-aware `_same_value` (component-wise integer equality on `enc_pt` objects, `coordinate_lines.py:457`),
- the per-cell **display** reuses `disp_pt` (`coordinate_lines.py:129`),
- a **new** byte-parity Py↔TS point-valued-cell comparator and round-trip routine wrap those primitives (the table machinery from data_handling does **not** run unchanged here).

**Canonical encoding:**

```
answer.type      = "table-completion"
answer.canonical = {
  "cells": [
    { "location": "A'", "value": { "x": {"num": <int>, "den": 1}, "y": {"num": <int>, "den": 1} } },
    { "location": "B'", "value": { "x": {"num": <int>, "den": 1}, "y": {"num": <int>, "den": 1} } },
    { "location": "C'", "value": { "x": {"num": <int>, "den": 1}, "y": {"num": <int>, "den": 1} } }
    // + "D'" iff shapeKind == quadrilateral
  ]
}
answer.display   = "A′(2, 5); B′(4, 1); C′(-1, 0)"   // labels in canonical source order, disp_pt per cell
```

- **`location` = the image label** (`A'`, `B'`, `C'`, `D'`), so the checker matches student rows to canonical rows **by label**. Row order in the student response is irrelevant; a student who fills `C′` before `A′` is still correct. The validator's `vertex-label-correspondence` check (§12) keys on `location`.
- **`value`** is the `enc_pt` point object (§6.1), giving one uniform integer-point encoding across point and shape tasks and one reused display routine (`disp_pt`).
- Cell count equals the source shape's vertex count (2/3/4); `duplicate coordinate-answer rows` and `image identical to object` are excluded deterministically by the edge-case policy (§14), so the cell set is always a function with distinct `location` keys and (for non-identity maps) the row set is well-formed.

**Prime-glyph byte-encoding contract (parity hazard, resolved).** The image labels and the `location` keys use the prime mark `′`. Because `answer.canonical` and the canonical SVG must be **byte-identical Py↔TS**, the prime is pinned to a single byte sequence in **both** oracles: **`location` keys are ASCII apostrophe `A'`, `B'`, `C'`, `D'`** (the byte `0x27`) in `answer.canonical.cells[].location`, so the structural key never depends on a multi-byte glyph or runtime Unicode normalisation. The **typeset prime** `′` (U+2032) appears only in human-facing surfaces — `answer.display`, SVG `<text>` label glyphs, and a11y `spokenMath` — where it is always emitted as the fixed UTF-8 sequence `E2 80 B2`. A parity-fixture row asserts (a) the `location` bytes are ASCII `0x27`, (b) the SVG label and `display` prime bytes are `E2 80 B2`, byte-for-byte identical across Py and TS, and (c) `canonicalStringify` (used by `serialize`) neither escapes nor normalises either form differently across runtimes.

**Why `table-completion` is adequate — and why NO polygon-answer schema is added.** The owner brief and the platform precedent both require proving existing structures inadequate before inventing a parallel. They are not inadequate:

| Requirement for a shape-image answer | Met by `table-completion`? |
|---|---|
| One image coordinate per labelled vertex | Yes — one `cell` per vertex. |
| Correspondence by **label**, not position | Yes — `location` carries the label; matching is keyed, order-free. |
| Exact integer coordinates, no floats | Yes — `value` is the `enc_pt` rational-point object, `den = 1`. |
| Variable vertex count (2/3/4) | Yes — variable-length `cells[]`. |
| Per-cell partial diagnosis (which vertex is wrong) | Yes — per-`location` cell comparison drives per-vertex feedback and the misconception adapters' predicted per-vertex responses (§13). |
| Schema-valid today, no Ajv recompile | Yes — `table-completion` is in the enum NOW, and the schema places **no** `allOf`/`canonical`/`cells` constraint on it (verified: no `cells`/`location` keys appear in `question-item.schema.json`), so a point-object `value` validates with **no schema edit**. |

The only genuinely-new surface is therefore **code, not schema**: a point-aware per-cell comparator/round-trip (above). A dedicated `polygon-answer` type would instead add a new enum member, new Ajv conditional rules, a new Python conformance branch, new import/export handling, and a new immutable fixture surface — all to express what `{cells:[{location,value}]}` already expresses losslessly. Edge connectivity, shape kind, and rendering metadata live in the **`params`** (the shape model, §5) and the media asset, **not** in the answer; the answer is purely the assessable image-vertex set. Therefore the proposal **does not** introduce a polygon-answer schema. Side-length / congruence / non-degeneracy are validated against `params` (`shape-congruence-preserved`, §12), not asserted by the answer object, so nothing is lost by keeping the answer a label-keyed coordinate table.

**Blocking acceptance test for the new value domain:** a parity fixture + validator check asserts that point-valued `table-completion` cells (i) round-trip byte-for-byte through the bank-json export/import (the existing integer-`<td>` round-trip does **not** cover point cells and is not relied upon), and (ii) compare **component-wise by label** via `_same_value`, with per-`location` mismatch feeding per-vertex feedback.

### 6.3 Summary — answer type per task

| Task | `answer.type` | `canonical` shape | New type? |
|---|---|---|---|
| `translate_point`, `reflect_point`, `rotate_point` | `coordinate` | `{x:{num,den:1}, y:{num,den:1}}` | No (existing) |
| `translate_shape`, `reflect_shape`, `rotate_shape` | `table-completion` | `{cells:[{location:"A'…", value:{x,y}}]}` | No (existing container; new point-aware comparator) |
| `describe_translation`, `describe_reflection`, `describe_rotation` | `transformation` | discriminated union (§7) | **Yes — the single new type** |

The point and shape contracts add **zero** schema surface. The *only* new answer type in the entire family is `transformation`, specified in §7. (Note the describe tasks are restricted to **non-symmetric triangles / irregular simple quadrilaterals** — never point or segment — so that exactly one allowed descriptor exists; this restriction lives in §5.5/§10.2/§2 and the answer contract here assumes it.)

---

## 7. Transformation-descriptor schema

The three **describe** tasks (`describe_translation`, `describe_reflection`, `describe_rotation`) ask the student to name the single transformation that maps the labelled source to the labelled image. The answer is neither a point nor a coordinate table — it is a *structured description of a mapping*. This is the **one** new answer type the family introduces: **`answer.type = "transformation"`**, carrying a structured **`answer.transformation`** object **as a named sibling of `answer.canonical`** (mirroring how `answer.measure` sits beside `answer.canonical` for `quantity`). It is added to `schemas/question-item.schema.json` **exactly mirroring the OWNER-GATED, additive, back-compatible mensuration `quantity` + `measure` precedent** (the `allOf` `if/then` discriminant rules at lines 253–285 of the current schema) — and is flagged **OWNER-GATED**: no item may set `type:"transformation"` until owner approval, and the `gen.geometry.transformations` family registers `pending-review` in `core/sdk/sequence-registry.ts` until then.

### 7.1 The `transformation` discriminated union (canonical internal form)

A discriminated union on `kind`, with the owner's exact field shapes. All scalars are **exact integers**.

```
// kind = "translation"
{ "kind": "translation",
  "vector": { "dx": <int>, "dy": <int> } }                      // nonzero vector (dx,dy not both 0)

// kind = "reflection"
{ "kind": "reflection",
  "axis": <vertical | horizontal | diagonal> }
//   vertical    : { "kind": "vertical",   "value": <int> }      // line x = value
//   horizontal  : { "kind": "horizontal", "value": <int> }      // line y = value
//   diagonal    : { "kind": "diagonal",   "equation": "y=x" | "y=-x" }

// kind = "rotation"
{ "kind": "rotation",
  "centre": { "x": <int>, "y": <int> },
  "quarterTurnsCCW": 1 | 2 | 3 }                                 // positive = anticlockwise
```

**Canonical convention (single source of truth).** Positive `quarterTurnsCCW` are **anticlockwise**. Direction wording in human input is normalised at parse time (§7.4):

| Human angle + direction | Canonical `quarterTurnsCCW` |
|---|---|
| 90° anticlockwise | 1 |
| 90° clockwise | **3** |
| 180° (either / unspecified direction) | 2 |
| 270° anticlockwise | 3 |
| 270° clockwise | **1** |

A **180°** rotation has **no** direction distinction; `quarterTurnsCCW` is canonically `2` and the formatter never emits "clockwise"/"anticlockwise" for it. `quarterTurnsCCW = 0` (or 4) is impossible — `0°/360°` rotations are excluded by the edge-case policy (§14) before they can reach canonicalisation.

**Reflection axis** is itself a small discriminated sub-object (`vertical`/`horizontal`/`diagonal`) so that `x = a` and `y = b` carry an exact integer `value` while the two diagonals are closed string literals `"y=x"` / `"y=-x"` — the only diagonals in V1.0.0 scope (arbitrary reflection lines are deferred and excluded, §14).

### 7.2 Schema delta to `question-item.schema.json` (additive, back-compatible, OWNER-GATED)

Two edits, both purely additive, **expressed with `if/then/const` discriminant rules — NOT `oneOf`** — mirroring exactly how `quantity` + `measure` were added. This choice is load-bearing for conformance: the Python checker `oracle/check_conformance.py` `check()` handles `$ref`, `const`, `allOf`, `if/then/else`, `type`, `enum`, `pattern`, `required`, `properties`, `additionalProperties`, `minItems`, `items`, but has **no `oneOf`/`anyOf` branch** (verified). A `oneOf`-based union would be **silently ignored** by Python conformance, breaking the guarantee that the descriptor rules are enforced on every path. Discriminant `if/then/const` keyed on `kind` keeps the "no new checker code path" claim true.

**(a) Enum extension** — add one member to `$defs.answerType.enum` (the same enum the mensuration change extended with `"quantity"`):

```
"enum": [ …, "table-completion", "graph-response", …,
          "transformation",        // NEW — owner-gated
          … ]
```

**(b) New optional `answer.transformation` sibling property + conditional discriminant rules.** The `answer` object has `additionalProperties:false` (line 210), so `transformation` must be added by name to `answer.properties` (it cannot arrive as an arbitrary key); that `additionalProperties:false` is also the actual enforcement that no malformed top-level answer key sneaks in. Add a base `transformation` object that fixes only the discriminant and its shared structure, then push the per-`kind` requirements into `allOf` `if/then` clauses keyed on `transformation.kind`:

```
"transformation": {
  "type": "object",
  "description": "Structured transformation descriptor for type='transformation' answers (gen.geometry.transformations). Required when type='transformation'; forbidden otherwise. 'display' is derived from this object, not duplicated here.",
  "additionalProperties": false,
  "required": ["kind"],
  "properties": {
    "kind":   { "enum": ["translation", "reflection", "rotation"] },
    "vector": { "type": "object", "additionalProperties": false, "required": ["dx","dy"],
                "properties": { "dx": {"type":"integer"}, "dy": {"type":"integer"} } },
    "axis":   { "type": "object", "additionalProperties": false, "required": ["kind"],
                "properties": {
                  "kind":     { "enum": ["vertical","horizontal","diagonal"] },
                  "value":    { "type": "integer" },
                  "equation": { "enum": ["y=x","y=-x"] }
                },
                "allOf": [
                  { "if":   { "properties": { "kind": { "const": "vertical" } },   "required": ["kind"] },
                    "then": { "required": ["value"],    "properties": { "equation": false } } },
                  { "if":   { "properties": { "kind": { "const": "horizontal" } }, "required": ["kind"] },
                    "then": { "required": ["value"],    "properties": { "equation": false } } },
                  { "if":   { "properties": { "kind": { "const": "diagonal" } },   "required": ["kind"] },
                    "then": { "required": ["equation"], "properties": { "value": false } } }
                ] },
    "centre": { "type": "object", "additionalProperties": false, "required": ["x","y"],
                "properties": { "x": {"type":"integer"}, "y": {"type":"integer"} } },
    "quarterTurnsCCW": { "type": "integer", "enum": [1,2,3] }
  },
  "allOf": [
    { "$comment": "translation carries a vector; no axis/centre/quarterTurnsCCW.",
      "if":   { "properties": { "kind": { "const": "translation" } }, "required": ["kind"] },
      "then": { "required": ["vector"],
                "properties": { "axis": false, "centre": false, "quarterTurnsCCW": false } } },
    { "$comment": "reflection carries an axis; no vector/centre/quarterTurnsCCW.",
      "if":   { "properties": { "kind": { "const": "reflection" } }, "required": ["kind"] },
      "then": { "required": ["axis"],
                "properties": { "vector": false, "centre": false, "quarterTurnsCCW": false } } },
    { "$comment": "rotation carries a centre + quarterTurnsCCW; no vector/axis.",
      "if":   { "properties": { "kind": { "const": "rotation" } }, "required": ["kind"] },
      "then": { "required": ["centre", "quarterTurnsCCW"],
                "properties": { "vector": false, "axis": false } } }
  ]
}
```

Every clause is `if/then/const`/`required`/boolean-`false` — all keywords the Python `check()` already honours, so the descriptor is enforced identically by runtime Ajv **and** offline conformance with **no new checker code path** (exactly as `measure` required none).

**Binding the descriptor to the type** — append two clauses to the existing top-level `answer.allOf` array (joining the five quantity/integer/exact-rational clauses already there), keyed on `answer.type`, binding the **named sibling** `transformation` (NOT `answer.canonical`):

```
{ "$comment": "A 'transformation' answer carries a structured 'transformation' descriptor and never the legacy free-form 'units' string.",
  "if":   { "properties": { "type": { "const": "transformation" } }, "required": ["type"] },
  "then": { "required": ["transformation"], "properties": { "units": false } } },

{ "$comment": "The structured 'transformation' descriptor is only permitted on type='transformation' answers.",
  "if":   { "required": ["transformation"] },
  "then": { "properties": { "type": { "const": "transformation" } } } }
```

The second clause is the exact dual of the mensuration rule binding `measure` to `quantity`: it forbids a stray `transformation` object on any other answer type, and `additionalProperties:false` on `answer` forbids any other stray key. The `then` clause constrains **`transformation`** (the sibling), **not** `answer.canonical` — resolving the prior §7/§8 contradiction about where the union lives.

**What `answer.canonical` holds for `transformation` items.** `canonical` is a schema-required field on every `answer` (line 211), so it must hold something byte-stable. The chosen rule: **`answer.canonical` holds a verbatim copy of the canonical descriptor object** (the same `{kind, …}` value stored under `answer.transformation`). This keeps `canonical` non-empty and self-describing, makes the bank-json round-trip trivially byte-stable (both fields serialise identically), and means the structural equivalence checker (§7.6) can read from either field. The schema places **no** `allOf` constraint on `canonical` for `transformation` (the binding clauses touch only `transformation`/`units`), so this copy validates without further rules. `answer.display` is derived (§7.5), never the ground truth.

**Back-compatibility — existing items stay valid.** Both edits are additive: a new enum member and new *optional* properties guarded by `if type === "transformation"` / `if transformation present`. Every existing item (`integer`, `coordinate`, `table-completion`, `quantity`, …) is untouched — it never sets `type:"transformation"`, never carries a `transformation` object, so the new `then` clauses are vacuously satisfied, identical to how adding `quantity` left all pre-mensuration items valid. The **immutable approved-family fixtures** (coordinate-lines, mensuration, stats) re-validate byte-for-byte under the extended schema; this is a blocking acceptance test for the schema delta.

### 7.3 Runtime Ajv + Python-conformance + bank import/export impact

Mirrors the mensuration `quantity` rollout one-for-one:

- **Runtime Ajv** — recompile via `scripts/compile-schemas.mjs` → `core/schema/compiled/question-item.validator.mjs`. The compiled validator gains the new enum value, the `transformation` object schema, and the `if/then/const` discriminant clauses. Existing compiled call sites are unchanged; a recompiled validator is a blocking artifact (regenerated, SHA-256 in the manifest).
- **Python conformance** — `oracle/check_conformance.py` already honours `const`/`allOf`/`if-then`/`enum`/`required`/`properties`/`additionalProperties`/boolean schemas (verified), and the §7.2 delta uses **only** those keywords (no `oneOf`), so the descriptor and its conditional binding are checked **with no new checker code path** — exactly as `measure` required none. The conformance suite gains the transformations golden + parity items as inputs.
- **Bank import/export** — `transformation` is a structured object, so the offline HTML/JSON exporters and the **bank-json round-trip** carry `answer.transformation` (and the `answer.canonical` copy) as first-class fields (no string flattening). The exporter's display path uses the formatter (§7.5), never re-derives geometry. Round-trip identity (`import(export(item)) === item`) is a blocking test, mirroring the mensuration `measure` round-trip. Importers that predate the delta reject `type:"transformation"` as an unknown type (correct fail-closed behaviour); the bank version gate records the schema bump.

**Build-order sequencing (one-line clarification).** Because each objective's `answerTypes[]` `$ref`s the shared `answerType` enum, the additive enum extension (`"transformation"`) must be applied to `question-item.schema.json` **before** the T7–T9 objective files are validated, so `answerTypes:["transformation"]` resolves under Ajv + conformance. The §16 build order and schema gate place the schema delta first.

### 7.4 Parser / canonicalizer (accepted human representations → canonical descriptor)

A **finite, deterministic** recogniser — a fixed grammar, no free NLP — that normalises every accepted human string to the §7.1 canonical object, then hands it to the canonicalizer. Accepts exactly the owner's enumerated forms (case-insensitive, whitespace- and unicode-minus tolerant):

| Accepted input (examples) | Canonical result |
|---|---|
| `translation by vector (3, -2)` · `translation by the column vector [3; -2]` | `{kind:"translation", vector:{dx:3, dy:-2}}` |
| `reflection in x = 4` | `{kind:"reflection", axis:{kind:"vertical", value:4}}` |
| `reflection in the y-axis` · `reflection in x = 0` | `{kind:"reflection", axis:{kind:"vertical", value:0}}` |
| `reflection in the x-axis` · `reflection in y = 0` | `{kind:"reflection", axis:{kind:"horizontal", value:0}}` |
| `reflection in y = x` | `{kind:"reflection", axis:{kind:"diagonal", equation:"y=x"}}` |
| `reflection in y = -x` | `{kind:"reflection", axis:{kind:"diagonal", equation:"y=-x"}}` |
| `rotation 90° clockwise about (2, -1)` | `{kind:"rotation", centre:{x:2,y:-1}, quarterTurnsCCW:3}` |
| `rotation 270° anticlockwise about the origin` | `{kind:"rotation", centre:{x:0,y:0}, quarterTurnsCCW:3}` |
| `rotation 180° about (0,0)` (direction absent/either) | `{kind:"rotation", centre:{x:0,y:0}, quarterTurnsCCW:2}` |

**Canonicalizer** (applied after parse, and to the generator's own descriptor):
- direction → `quarterTurnsCCW` via the §7.1 table (clockwise `90°→3`, `270°→1`); strip direction from `180°` (→ `2`).
- `x-axis`/`y=0` → `{horizontal, value:0}`; `y-axis`/`x=0` → `{vertical, value:0}` — alias normalisation so the two members of each alias pair are byte-identical canonical objects.
- vector forms `(dx, dy)` and column `[dx; dy]` → identical `{dx,dy}`.
- `origin` → `centre:{x:0,y:0}`.

**REJECT (deterministic, no partial credit):** ambiguous descriptions; missing rotation centre; missing translation vector; **zero** translation vector; unsupported reflection lines (any axis other than `x=a`/`y=b`/`y=x`/`y=-x`); arbitrary-angle / non-multiple-of-90° rotations; `0°`/`360°`; contradictory direction+angle ("90° clockwise anticlockwise"); any **unparsed trailing text**. Rejection returns *incorrect*, never an exception. An explicit **multiple-choice** request on any describe task returns an `interaction-not-supported` result (no silent MC→FR conversion), per the family interaction policy.

### 7.5 Formatter (canonical → display)

`answer.display` is **derived**, never stored as ground truth:

| Canonical | `display` |
|---|---|
| `{translation, vector:{3,-2}}` | `translation by vector (3, -2)` |
| `{reflection, vertical, value:4}` | `reflection in the line x = 4` (`value:0` → `reflection in the y-axis`) |
| `{reflection, horizontal, value:0}` | `reflection in the x-axis` |
| `{reflection, diagonal, "y=x"}` | `reflection in the line y = x` |
| `{rotation, centre:{2,-1}, qt:3}` | `rotation 270° anticlockwise about (2, -1)` (or the clockwise equivalent `90°` per a presentation flag; canonical object is unchanged) |
| `{rotation, centre:{0,0}, qt:2}` | `rotation 180° about the origin` (no direction word) |

The typeset prime `′` (where any image-label text appears in derived display) is emitted as the fixed UTF-8 sequence `E2 80 B2`, per the §6.2 prime-byte contract.

### 7.6 Equivalence checker (structural, not string)

Two descriptors are equivalent **iff** their canonical objects are deeply equal — never by comparing display strings. Reusing the mensuration `quantity` structural-equivalence pattern (canonicalise both sides, then compare structurally):

- **translation** — equal `dx` and `dy`.
- **reflection** — equal `axis.kind`; for `vertical`/`horizontal` equal integer `value`; for `diagonal` equal `equation` literal.
- **rotation** — equal `centre.x`, `centre.y`, and `quarterTurnsCCW` **after** canonicalisation. Thus "90° clockwise about C" ≡ "270° anticlockwise about C" (both `qt:3`); "180° clockwise" ≡ "180° anticlockwise" (both `qt:2`).

The checker therefore guarantees the **transformation-checker matrix** (reused from the mensuration/stats feature-checker-matrix machinery, by name): clockwise/anticlockwise equivalents normalise identically; `180°` direction wording canonicalises; `x-axis`≡`y=0` and `y-axis`≡`x=0` aliases normalise identically; malformed/incomplete descriptors, missing centres, and unsupported axes/angles are rejected; and — critically — **no ambiguous descriptor ever scores full credit**, because the generator's `descriptor-unique` validation (§12) guarantees exactly one allowed descriptor maps the figure before the item is banked. This uniqueness is achievable only because describe tasks are restricted (§5.5/§10.2/§2) to **non-symmetric triangles / irregular simple quadrilaterals** — never a single point or a (collinear) segment, which admit multiple allowed descriptors and could never yield a unique answer.

### 7.7 Structured feedback (diagnostic, not a numeric code)

Per the free-response family contract, feedback is deterministic and reads from displayed values (never internal symbols). The checker compares the student's canonical descriptor to the answer's and emits targeted feedback driven by the descriptor-misconception adapters (§13), e.g.: correct type but wrong vector → "Your translation direction is right, but check each component: the vector is (3, -2), not (-3, 2)."; correct reflection type, wrong axis → "A reflection, yes — but the mirror line is x = 4, not x = 0."; correct rotation angle, missing centre → "A 90° rotation is right, but a rotation needs a centre: it is about (2, -1)."; a reflection named when the mapping is a rotation → "This mapping reverses orientation about a point — it is a rotation, not a reflection." Every predicted wrong descriptor is independently recomputed by the validator (the misconception adapter must reproduce it), and inapplicable rules are omitted rather than emitting a null prediction.

This keeps the family to **exactly one** new answer type (`transformation`); points reuse `coordinate`, shapes reuse `table-completion`, and the schema grows only by the additive, owner-gated, `if/then/const` delta in §7.2.


---

## 8. Parser, canonicalizer, and equivalence checker

This section specifies the `"transformation"` answer-contract machinery for the three `describe_*` tasks. It is the geometric analogue of the dimensional-quantity answer contract approved in **gen.measurement.mensuration v1.0.1**, whose checker lives **family-local** at `domains/measurement/mensuration-units.ts` ↔ `oracle/spi_oracle/mensuration_units.py` (there is no shared `core/answer-checking/transformation.*`; the precedent is family-local, and this family matches it): a finite, anchored parser → canonical structured descriptor → formatter → STRUCTURAL equivalence checker, with a closed `RESULT_CODES` tuple and targeted feedback drawn only from displayed/parsed values. As there, every routine is authored oracle-first in Python (`oracle/spi_oracle/transformations_descriptor.py`) and mirrored BYTE-IDENTICALLY in TypeScript (`domains/geometry/transformations-descriptor.ts`); parity is gated by the task-pinned ≥300 parity fixtures and the TRANSFORMATION-CHECKER matrix (§15). Comparison is ALWAYS over canonical descriptors, NEVER over raw text.

The `perform_*` tasks (`translate_*`, `reflect_*`, `rotate_*`) do not use this parser — point-image tasks reuse the EXISTING `coordinate` / `ordered-pair` checker, and multi-vertex shape-image tasks reuse the `table-completion` CONTAINER with a point-aware per-cell comparator (§6) keyed by vertex LABEL. This section governs only the descriptor contract used by `describe_translation`, `describe_reflection`, `describe_rotation`.

> **Describe-task object class (cross-reference to §5.5 / §10.2).** The descriptor checker presumes the source object admits exactly one allowed descriptor. That uniqueness is guaranteed UPSTREAM by an affirmative object-type restriction — `objectTypeForTask(describe_*) ∈ {triangle, quadrilateral}` restricted to **non-symmetric** figures (scalene triangle: three distinct squared side lengths; irregular simple quadrilateral with trivial symmetry group) — NOT by this checker. Points and segments are EXCLUDED from describe tasks because their labelled image is mapped by more than one allowed isometry (a single point: one translation plus infinitely many rotations/reflections; a collinear 2-point segment: a reflection and a rotation produce the identical labelled image, e.g. source `A=(0,0),B=(1,0)` → `A'=(0,0),B'=(0,1)` is BOTH reflection in `y=x` AND rotation 90° ACW about the origin). A no-symmetry labelled triangle/quadrilateral admits exactly one direct isometry and zero allowed opposite isometries, so its descriptor is provably unique — see §5.5/§12.6. The parser/checker here therefore never has to disambiguate a structurally ambiguous source.

### 8.1 Canonical descriptor (the parse target)

The single canonical form is the discriminated union defined in §7, restated here as the parser's output type. All integer fields; no floats, no angle-in-degrees stored, no direction word stored.

```
Translation  { kind:"translation", vector:{ dx:int, dy:int } }                       // (dx,dy) ≠ (0,0)
Reflection   { kind:"reflection", axis:
                 { kind:"vertical",   value:int }      // x = a
               | { kind:"horizontal", value:int }      // y = b
               | { kind:"diagonal",   equation:"y=x" }
               | { kind:"diagonal",   equation:"y=-x" } }
Rotation     { kind:"rotation", centre:{ x:int, y:int }, quarterTurnsCCW: 1|2|3 }
```

Canonical invariants enforced at construction (a descriptor that violates any of these is not a legal canonical value; the parser returns a reject code, never an out-of-range canonical):
- `translation.vector` is nonzero.
- `reflection.axis.kind ∈ {vertical, horizontal, diagonal}`; `value` is an integer; `equation ∈ {"y=x","y=-x"}` exactly.
- `rotation.quarterTurnsCCW ∈ {1,2,3}` (the 0/4 turn is excluded by edge-case policy, never produced or accepted).
- The canonical direction convention (§7) is internal and ANTICLOCKWISE-positive: there is exactly one stored representation per geometric mapping.

### 8.2 Parser: accepted human forms (anchored, finite grammar)

The parser is a finite, fully-anchored recogniser — one top-level regex per `kind`, anchored `^…$` after normalization, so any unconsumed trailing text is a hard reject (mirrors `mensuration_units.parse_quantity`, which rejects `"12 cm long"` as `malformed-response`). No backtracking heuristics, no fuzzy matching, no NLP. Normalization, applied once before matching:

| Step | Action |
|---|---|
| Unicode | `−` (U+2212) → `-`; `°` → degree token (see below); any other non-ASCII glyph (`×`, `⟨⟩`, smart quotes) is a hard reject |
| case | lower-case the directive keywords, axis words, origin word, and direction words; numeric literals unaffected |
| whitespace | collapse internal runs to a single space; strip a single leading/trailing space run |
| punctuation | accept point/tuple `(a, b)` or `(a,b)`; column vector `[a; b]` or `[a;b]`; reject mixed/unbalanced brackets |
| degrees | `deg`, `degree`, `degrees`, `°` all normalize to one degree token |

Accepted forms (exactly the owner brief's list; nothing else is accepted):

| Directive | Accepted surface forms | Canonical |
|---|---|---|
| translation | `translation by vector (3, -2)` · `translation by the column vector [3; -2]` · `translate by (3,-2)` | `{kind:"translation", vector:{dx:3,dy:-2}}` |
| reflection (vertical) | `reflection in x = 4` · `reflect in the line x=4` | `{kind:"reflection", axis:{kind:"vertical", value:4}}` |
| reflection (horizontal) | `reflection in y = -1` | `{kind:"reflection", axis:{kind:"horizontal", value:-1}}` |
| reflection (x-axis alias) | `reflection in the x-axis` · `reflection in y = 0` | `{kind:"reflection", axis:{kind:"horizontal", value:0}}` |
| reflection (y-axis alias) | `reflection in the y-axis` · `reflection in x = 0` | `{kind:"reflection", axis:{kind:"vertical", value:0}}` |
| reflection (diagonal) | `reflection in y = x` · `reflection in y = -x` | `{kind:"reflection", axis:{kind:"diagonal", equation:"y=x" \| "y=-x"}}` |
| rotation | `rotation 90 deg clockwise about (2, -1)` · `rotation 270 deg anticlockwise about the origin` · `rotate 180 about (0,0)` | `{kind:"rotation", centre:{x,y}, quarterTurnsCCW}` |

Lexical anchors: `(translation|translate) by (the )?(column )?vector …` introduces a 2-component integer tuple/column; `reflect(ion)? in (the line )?…` introduces an axis spec; `about (the origin | (h,k))` introduces a centre; `clockwise`/`anticlockwise`/`counterclockwise`/`cw`/`acw`/`ccw` are the only direction tokens. `the origin` ⇒ `(0,0)`. The angle keyword is restricted to the literal set `{90, 180, 270}` followed by the degree token; any other integer — including `0` and `360` — is a hard reject (`unsupported-angle`).

### 8.3 Canonicalizer (surface → single internal form)

Run after a successful syntactic parse, before the descriptor is emitted. Deterministic, total:

1. **Direction → ACW quarter-turns.** `90 ACW → 1`, `180 (either/neither) → 2`, `270 ACW → 3`; `90 CW → 3`, `270 CW → 1`, `180 CW/ACW → 2`. For `180` the direction word is accepted but discarded (180 has no orientation distinction).
2. **Axis aliases.** `x-axis ↔ y=0` collapse to `{kind:"horizontal", value:0}`; `y-axis ↔ x=0` collapse to `{kind:"vertical", value:0}`. These two alias pairs MUST normalize identically (asserted by the TRANSFORMATION-CHECKER matrix, §15).
3. **Origin.** `the origin` ⇒ `centre:{x:0,y:0}`.
4. **Sign/format normalization.** `+3`→`3`; coordinates and vector components stored as plain integers; `y=x`/`y=-x` stored as the exact canonical equation strings.

The canonicalizer NEVER alters geometry — `90 CW about (2,-1)` and `270 ACW about (2,-1)` produce the IDENTICAL canonical descriptor because they denote the same mapping, and the formatter (§8.4) then chooses one display.

### 8.4 Formatter (descriptor → canonical display)

The inverse of the canonical convention; one display string per canonical descriptor (mirrors `format_quantity`). Used for `answer.display`, worked-solution prose, and feedback. ASCII-authoritative, with a Unicode display variant only for KaTeX prompt rendering (never for the byte-parity `answer.display`).

| Canonical | `display` (ASCII) |
|---|---|
| translation `{dx,dy}` | `translation by vector (dx, dy)` |
| reflection vertical `value=a` | `reflection in x = a` (a=0 ⇒ `reflection in the y-axis`) |
| reflection horizontal `value=b` | `reflection in y = b` (b=0 ⇒ `reflection in the x-axis`) |
| reflection diagonal | `reflection in y = x` · `reflection in y = -x` |
| rotation `q=1/2/3, centre=(h,k)` | `rotation 90/180/270 deg anticlockwise about (h, k)` ((0,0) ⇒ `about the origin`; q=2 ⇒ `rotation 180 deg about (h, k)`, no direction word) |

### 8.5 Structural equivalence checker

`check_descriptor(responseText, expected: Transformation) -> CheckResult` — the descriptor twin of `mensuration_units.check_response`. Procedure:
1. `parse_descriptor(responseText)` → `{ descriptor | null, code }`. On `code != null` (a parse/reject), return that reject code with feedback (§8.6) — no comparison occurs.
2. Otherwise compare the parsed canonical descriptor to the expected canonical descriptor **STRUCTURALLY** (field-by-field over the canonical objects), never by string. Equality rules:
   - `kind` must match (a reflection response to a rotation question ⇒ `wrong-transformation-type`).
   - translation: `dx==dx ∧ dy==dy`.
   - reflection: same `axis.kind`; vertical/horizontal `value` equal; diagonal `equation` equal.
   - rotation: `centre.x` , `centre.y` equal AND `quarterTurnsCCW` equal.
3. On full match ⇒ `correct`. On `kind` match but a field mismatch ⇒ the targeted code from §8.6. Because comparison is post-canonicalization, every accepted equivalent surface form of the correct answer (`90 CW` vs `270 ACW`, `x-axis` vs `y=0`, `180 cw` vs `180`) scores `correct` (proven by the matrix). No ambiguous or merely-different descriptor ever receives full correctness — a descriptor that parses to a *different* canonical value is simply not equal.

### 8.6 REJECT cases and structured result codes

Closed `RESULT_CODES` tuple (the descriptor analogue of mensuration's reject-code set; Py tuple + byte-identical TS literal union). Each code is deterministic, reachable, and exercised by the checker-evidence matrix (§15). Feedback is generated only from displayed/parsed values — never internal symbols.

| Code | Trigger | Feedback (template) |
|---|---|---|
| `correct` | canonical descriptors equal | `Correct.` |
| `wrong-transformation-type` | parses, but `kind` differs from expected | `You described a {parsedKind}, but this mapping is a {expectedKind}.` |
| `wrong-translation-vector` | translation, `kind` ok, vector differs | `The transformation is a translation, but the vector is not right.` |
| `wrong-reflection-axis` | reflection, `kind` ok, axis differs | `This is a reflection, but not in that line.` |
| `wrong-rotation-centre` | rotation, `kind` + turns ok, centre differs | `The angle and direction are right, but not the centre of rotation.` |
| `wrong-rotation-amount` | rotation, centre ok, `quarterTurnsCCW` differs | `Right centre, but check the angle and direction of turn.` |
| `ambiguous-description` | syntactically valid but underspecified (e.g. `reflection in the diagonal` with no `y=x`/`y=-x`; a rotation angle/direction that does not fix one ACW turn) | `This description could mean more than one transformation. State the exact line/centre/turn.` |
| `missing-rotation-centre` | rotation directive with no `about …` clause | `A rotation needs a centre. Say what point you are rotating about.` |
| `missing-translation-vector` | translation directive with no parseable vector | `A translation needs a vector, for example (3, -2).` |
| `unsupported-reflection-line` | reflection in a line outside `x=a, y=b, y=x, y=-x` (e.g. `y=2x+1`, `x=y+3`) | `Reflections in this family use x = a, y = b, y = x, or y = -x.` |
| `unsupported-angle` | rotation angle ∉ {90,180,270} (incl. 0/45/360) | `Rotations in this family turn 90, 180, or 270 degrees.` |
| `contradictory-description` | conflicting tokens (e.g. `90 deg and 180 deg`, `clockwise anticlockwise`, two `about` clauses) | `Your description gives two different turns. State one angle and one direction.` |
| `unparsed-trailing-text` | a valid prefix followed by unconsumed text | `I read part of your answer but not all of it. Remove the extra words.` |
| `malformed-response` | unanchored / empty / unreadable / unknown non-ASCII glyph | `I could not read your answer. Describe one transformation, e.g. reflection in y = x.` |

`ambiguous-description`, `unsupported-reflection-line`, `unsupported-angle`, and `contradictory-description` are distinct from `malformed-response`: the response is well-formed enough to localise the fault, so the feedback names it (mirrors mensuration's split of `missing-unit` / `wrong-base-unit` / `malformed-response`). These `wrong-*` codes also back the DESCRIPTOR misconception group in §13: a diagnostic rule whose predicted student descriptor parses to a *different* canonical value yields the matching `wrong-*` code, which the independent validator recomputes (§13 / §12). Diagnostic-predicted descriptors feed ONLY the checker, worked-solution pitfall notes, and the validator's diagnostic-recompute — never any student-channel SVG or a11y field (§11/§13).

### 8.7 Schema, runtime, and bank impact (OWNER-GATED, additive, back-compatible)

This adds AT MOST ONE answer type, following the `quantity`/`measure` precedent already in `schemas/question-item.schema.json` — the `if/then/const` discriminant block enforced in BOTH the recompiled Ajv (`core/schema/compiled/`) AND `oracle/check_conformance.py`. **Verified:** `check_conformance.py` honours `allOf`, `if/then/else`, `const`, `enum`, `required`, `properties`, `additionalProperties:false` — but has NO `oneOf`/`anyOf` branch (grep count = 0). Therefore the descriptor schema (§7.2) is expressed with **`if/then/const` discriminants keyed on `kind`**, NOT `oneOf`, so the "no new checker code path" claim stays true (a top-level/nested `oneOf` would be SILENTLY IGNORED by the Python checker and break the cross-path guarantee).

- **`$defs.answerType` enum:** append the single literal `"transformation"`. Additive; no existing item changes; `answerTypes:["transformation"]` on the T7–T9 objectives only resolves once this enum delta lands, so the schema delta MUST be applied BEFORE those objective files are validated (sequencing noted in §16.2 step 1).
- **`$defs.answer` — named sibling property (NOT folded into `canonical`).** Add a structured property `"transformation"` (the §8.1 union) to `answer.properties`, exactly analogous to the existing `measure` property. Because `answer` has `additionalProperties:false` (verified, line 210), the named `transformation` sibling is the ONLY new top-level key permitted; any stray key is rejected by `additionalProperties:false` itself — that is the actual enforcement for malformed top-level answer keys.
- **`answer.transformation` shape (if/then/const on `kind`).** Inside the property, the union is enforced by discriminant rules mirroring the `measure` dimension/exponent rules:
  - `kind ∈ {"translation","reflection","rotation"}` (enum) and `additionalProperties:false`.
  - `if kind=="translation" then required:["vector"]`, `vector` an object `{dx:int, dy:int}`, `additionalProperties:false`.
  - `if kind=="reflection" then required:["axis"]`; `axis.kind ∈ {"vertical","horizontal","diagonal"}`; `if axis.kind=="vertical"|"horizontal" then required:["value"]` (`value:int`); `if axis.kind=="diagonal" then required:["equation"]` with `equation ∈ {"y=x","y=-x"}` (`enum`).
  - `if kind=="rotation" then required:["centre","quarterTurnsCCW"]`; `centre` an object `{x:int,y:int}`; `quarterTurnsCCW ∈ {1,2,3}` (`enum`).
- **Off-type guard (dual `allOf` clause).** `if type=="transformation" then { required:["transformation"], properties:{ units:false } }` (the structured object is required and the legacy free-form `units` string is forbidden, exactly as `units:false` is forbidden on `quantity`); and a dual `if NOT type=="transformation" then { properties:{ transformation:false } }` so the field is forbidden off-type (boolean schema `false`, which `check_conformance.py` honours). **Note:** these clauses bind to `answer.transformation` and do NOT constrain `answer.canonical`.
- **What `answer.canonical` holds for a transformation item.** `canonical` is schema-required on every answer and stays the existing shape so every existing serialization path is byte-identical. For `type=="transformation"` it carries the **canonical display key** — the §8.4 ASCII display string (e.g. `"rotation 90 deg anticlockwise about (2, -1)"`), a deterministic 1:1 function of the structured descriptor. This is byte-stable for the bank round-trip and lets legacy consumers that read only `canonical`/`display` render the answer without understanding the union. (The structured object in `answer.transformation` remains the source of truth for checking.) `interactionType` stays `free-response`.
- **Runtime Ajv:** recompile via `scripts/compile-schemas.mjs` → `core/schema/compiled/`; the new discriminant block rides the existing `answer.allOf`. Ajv natively supports `if/then/const`/`enum`/boolean-`false`, so no Ajv option change.
- **Python conformance:** no engine change — the `if/then/const`/`enum`/`additionalProperties:false`/boolean-`false` keywords are all already handled. Parity of the validator decision across Py/TS is a parity-fixture row (accept a valid descriptor item; reject an off-type `transformation` field; reject a bad `kind`/`quarterTurnsCCW`).
- **Bank import/export:** the offline HTML/JSON exporters + bank-json round-trip carry the structured `answer.transformation` verbatim (plain integer JSON); a round-trip MUST reproduce both the structured descriptor AND `canonical` (the display key) byte-for-byte. Importers reject a `type:"transformation"` item whose `transformation` object fails Ajv (no silent coercion).
- **Lifecycle:** the family registers `approvalStatus: pending-review` in `core/sdk/sequence-registry.ts` (gated from Studio/production) until owner approval, per the SDK approval-lifecycle precedent.

---

## 9. Exact transformation engine

### 9.1 Single forward helper

One pure function is the SINGLE source of the coordinate mathematics for the whole family — parameter generation, prompt construction, student/answer-key media, the canonical answer, the worked solution, and the diagnostic adapters all call it. It is the structural twin of `coordinate-lines`/`mensuration`'s `solve()` forward route. Signature (Py authored first, TS byte-mirror):

```
apply_transform(t: Transformation, p: {x:int, y:int}) -> {x:int, y:int}     # integer in, integer out
```

with the canonical Transformation union from §8.1. There is NO runtime trigonometry, NO float, NO tolerance, NO irrational: every rule below is a closed-form INTEGER coordinate map, so integer-in ⇒ integer-out is total (the `integer-coordinate-closure` check). Shapes are mapped vertex-by-vertex over the labelled-shape model (§5) using `apply_transform`, preserving label correspondence (`A→A′`, `B→B′`, …); edges are re-derived from the same connectivity, never re-mapped independently.

The family pins `generatorId = "gen.geometry.transformations"` and `generatorVersion = "1.0.0"` as exported registry constants (`GENERATOR_ID` / `GENERATOR_VERSION`, parallel to coordinate-lines' `GENERATOR_ID`/`GENERATOR_VERSION="1.0.2"`). Every emitted item, golden fixture, generation manifest, and `sequence-registry.ts` entry carries these identical strings (artifact-IDENTITY gate).

### 9.2 Exact integer coordinate rules

| Transformation | Rule (∀ integer x,y) |
|---|---|
| Translation `(dx,dy)` | `(x, y) → (x + dx, y + dy)` |
| Reflect `x = a` (vertical) | `(x, y) → (2a - x, y)` |
| Reflect `y = b` (horizontal) | `(x, y) → (x, 2b - y)` |
| Reflect `y = x` | `(x, y) → (y, x)` |
| Reflect `y = -x` | `(x, y) → (-y, -x)` |
| Rotation about `(h,k)`, ACW | translate to centre `(x-h, y-k)` → apply the quarter-turn below → translate back `+ (h,k)` |
| └ 1 quarter (90° ACW) | `(x-h, y-k) → (-(y-k), x-h)` |
| └ 2 quarters (180°) | `(x-h, y-k) → (-(x-h), -(y-k))` |
| └ 3 quarters (270° ACW) | `(x-h, y-k) → (y-k, -(x-h))` |

All operations are `+`, `-`, unary `-`, and `2a`/`2b` (a doubling), so results are exact integers under the generator's parameter caps; no `Rational` denominator > 1 ever arises from a transformation (the family stays inside the integer sublattice of the exact-math layer, `core/exact-math/rational.ts`, with `den == 1` throughout). The `2a-x` / `2b-y` reflection forms and the centre-relative rotation forms are written verbatim — never re-derived via `sin`/`cos` — which is the contract that makes Py↔TS byte parity trivial and removes any rounding surface.

### 9.3 Where the engine is used (and the reuse boundary)

- **Generation:** after sampling source vertices (via the BYTE-IDENTICAL Mulberry32 / `seeded_random.py` parity RNG) and a transformation, `apply_transform` produces the image; edge-case policy (§14) then rejects/regenerates (zero vector, 0/360 turn, image ≡ object, fixed-point-hides-transformation, viewport overflow, symmetry-induced descriptor ambiguity).
- **Answer:** point-image tasks encode the image point as `coordinate`/`ordered-pair`; shape-image tasks encode one `table-completion` row per labelled image vertex (correspondence by LABEL, point-aware per-cell value comparator — §6). For `describe_*`, the canonical answer is the §8 descriptor (with `answer.canonical` = its display key, §8.7), and `apply_transform` is what proves it maps every source vertex to its image.
- **Solution:** the worked-solution steps (`solution.steps[]`) quote the exact rule from §9.2 and the per-vertex substitution.
- **Rendering / reuse boundary (reconciled).** The SHARED, exported, reused layer is **`core/visual-style/cartesian-theme.ts`** (`COMMON_CSS`, `modeVars`, `presentationSvg`, `exportSvg`, `MODES` — verified exported, with 6000×4200 export defaults), as used by mensuration. The Cartesian **grid/axes/lattice-point/viewport/`gridRound`/projection** GEOMETRY primitives are **re-implemented byte-identically inside the new transformations module** (Python oracle authoritative, TS mirror) — NOT imported from `coordinate-lines.ts`, whose `viewport`/`gridRound`/`labelsFeasible`/`U_MIN`/`DATA_MARGIN_UNITS` are module-private. This is exactly the mensuration precedent (`mensuration.ts` defines its OWN `gridRound` and reuses only the exported theme layer); importing the private coordinate-lines internals would require adding `export` to the approved module, i.e. modifying it in place, which we do NOT do. The transformation `figure()` is a NEW composing function modelled on `mensuration.renderSvg` (NOT a reuse of `coordinate-lines.figure()`); the named SVG channel groups (`cx-base`/`cx-annot`/`cx-overlay`), `extractGroup`, `renderSvg(…, channel, …)`, the `class="cx-figure"` root, and the `<title>`/`<desc>`-first-children + answer-key-base-geometry-identical / answer-key-overlay-additive-only checks are reused BY NAME from the MENSURATION precedent (`domains/measurement/mensuration.ts`). The answer-key figure overlays the image / axis / centre as an ADDITIVE overlay over BYTE-IDENTICAL base geometry (§11).

### 9.4 The validator MUST NOT call the engine forward

A hard architectural constraint (detailed in §12): the independent validator does NOT call `apply_transform` and assert equality with itself — that would only prove the generator agrees with itself. Instead it **re-derives** each property from the stored source + stored image by INDEPENDENT geometric conditions, then cross-checks against the descriptor and the inverse map:

- **Translation** — every `image_i - source_i` is the SAME vector, and that vector is nonzero (`translation-vector-consistent`). It computes the differences directly; it never re-adds `(dx,dy)`.
- **Reflection** — for each corresponding pair, the axis bisects the segment perpendicularly: the midpoint lies on the axis and the segment is perpendicular to it, i.e. the axis fixes every required midpoint and the two points are equidistant from the axis (`reflection-axis-condition`, `reflection-distance-agreement`) — checked by the exact midpoint/squared-distance conditions, not by re-reflecting.
- **Rotation (non-degenerate centre reconstruction).** The validator first tests the **180° hypothesis via the COMMON-MIDPOINT route**: if every corresponding pair shares the SAME integer midpoint, that midpoint is the centre and `quarterTurnsCCW = 2`. (Perpendicular-bisector intersection is the WRONG primitive for 180°: when two chosen source vertices and the centre are collinear the two bisectors are parallel/coincident and yield no unique point.) For the 90°/270° hypotheses it solves the centre as the fixed point of the exact quarter-turn relation using **at least two corresponding pairs whose connecting directions are non-parallel**, iterating over pairs to select a non-degenerate basis and REJECTING collinear/degenerate selections; it accepts only an INTEGER centre. Because describe sources are restricted to triangles/quadrilaterals (§5.5), ≥3 labelled vertices are guaranteed, which always supply a non-degenerate pair. It then confirms, for every pair, that the centre is fixed, the centre-relative source and image vectors satisfy the exact quarter-turn relation, the squared lengths from the centre are equal, and orientation flips per the declared turn (`rotation-centre-condition`, `rotation-quarter-turn-agreement`).
- **All shape tasks** — corresponding side lengths agree exactly (squared lengths, integers), the shape is non-degenerate, the `coordinate`/`table-completion` answer agrees with the descriptor, and the INVERSE transformation restores the source shape (`shape-congruence-preserved`, `inverse-transformation-restores-source`).
- **Descriptor tasks** — enumerate every allowed candidate descriptor and require EXACTLY ONE canonical descriptor to map every labelled source vertex to its corresponding image vertex (`descriptor-unique`, `descriptor-maps-complete-shape`, `no-ambiguous-symmetry`). This succeeds because the describe source is a no-symmetry triangle/quadrilateral (§5.5/§8 cross-reference), so exactly one direct isometry and zero allowed opposite isometries fit.

Thus the forward engine (§9.1–9.2) and the independent validator (§12) are two SEPARATE routes to the same fact — the "answer recomputed by a second route" discipline of the approved families — and parity, golden, the SPI_SWEEP=10000 stability sweep, and the artifact-identity gates apply to both.


---

## 10. Backward construction

The family is **backward-constructed** in the coordinate-lines / mensuration tradition: a single seeded pass draws a *source* shape, picks a *transformation*, computes the *exact integer image*, and accepts the item only if a closed battery of structural guards passes. The seed is consumed through the byte-identical `core/seeded-random/mulberry32.ts` / `oracle/spi_oracle/seeded_random.py` pair; **the call order below is the parity contract** (Py and TS draw in lock-step, `next_int(lo,hi)` inclusive). On any guard failure the loop performs a **deterministic redraw** (re-enter the loop, consuming the next draws) up to `MAX_PARAM_ATTEMPTS = 800` (the coordinate-lines bound); exhaustion throws — it never silently relaxes a guard. Every deferred topic (owner brief "DEFER FROM V1.0.0") is excluded **at draw time**: the draw functions below can only emit a nonzero integer translation vector, one of the four supported reflection lines, or a 90/180/270 lattice-centre rotation — enlargements, fractional/negative scale factors, compositions, arbitrary lines/angles, trig rotations, fractional vectors/centres, and curve/function/3D/matrix transforms are unreachable because **no draw function constructs them**. Critically, the **input object class is restricted (not merely biased)** so that every describe-task item is provably unique *by construction*, rather than by a redraw filter that could exhaust (§10.2).

### 10.1 Construction window and lattice

One source of truth (the §14 machine-readable `transformations-config.ts`) fixes the **coordinate window** `[-W, W] × [-W, W]` (proposed `W = 8`, a tighter inset than coordinate-lines' `±10` data domain so that a translated/rotated image still lands inside the same `±10` domain). Every emitted vertex, the translation vector, the reflection constant, and the rotation centre are **integers**, so `integer-coordinate-closure` is structural, not checked numerically.

**Renderer-primitive reuse — reconciled (blocker fix).** The genuinely shared, exported layer this family imports is **`core/visual-style/cartesian-theme.ts`** only — `COMMON_CSS`, `modeVars`, `resolveCommonCss`, `presentationSvg`, `exportSvg`, `MODES` (all verified `export`ed, with the 6000×4200 defaults). The Cartesian **geometry primitives** — `viewport()` (equal-scale layout), `gridRound` (round-half-up over exact `Rational`), `projX`/`projY`, the grid/axes/tick element builders, and the label-feasibility test — are **module-private in `domains/geometry/coordinate-lines.ts`** (`function viewport`, `function gridRound`, `function labelsFeasible`, `const U_MIN`/`DATA_MARGIN_UNITS`; only `GENERATOR_ID/VERSION`, `VALIDATOR_VERSION`, `TASKS`, `pngExportTransform`, `generate`, `serialize`, `describe`, `Config`, `validate` are exported). They therefore **cannot be imported without adding `export` to the approved module, which would modify it in place.** This proposal does **not** do that. Instead, **exactly as `mensuration.ts` defines its own `gridRound` (mensuration.ts:61) and reuses only the exported theme layer**, the new `domains/geometry/transformations.ts` (Py oracle `oracle/spi_oracle/transformations.py` authoritative; TS mirror) **re-implements the Cartesian grid/axes/lattice/`viewport`/`gridRound`/`projX`/`projY` primitives byte-identically** to the coordinate-lines definitions, pinned by a parity fixture asserting the two modules project an identical lattice to the same integer pixels. We therefore drop any earlier wording that claimed these primitives are "imported / reused unchanged from coordinate-lines," and we retain the accurate promise: **the approved coordinate-lines and cartesian-theme files are NOT edited.** (True import-level reuse would be a separate refactor — extract the primitives into a shared `core/visual-style/cartesian-render.ts` with its own version / parity / integrity gates and a byte-for-byte regression proof for coordinate-lines / stats / mensuration — and is explicitly *out of scope* for v1.0.0.)

The re-implemented `viewport()` computes the equal-scale layout `Lay` from the union of every source **and** image lattice point (plus the rotation centre, when applicable) — guaranteeing one equal x/y unit `U` and the `viewport-contains-source-and-image` invariant (§11).

### 10.2 Object-type policy — affirmative restriction (blocker fix)

`objectTypeForTask(task, rng)` is **not** a preference; it is a **hard restriction** keyed by task family, declared once in `transformations-config.ts` and enforced by a named test `objectType-restriction-by-task`:

| Task family | Allowed `objectType` | Excluded |
|---|---|---|
| `translate_point`, `reflect_point`, `rotate_point` (perform, point) | `point` | — |
| `translate_shape`, `reflect_shape`, `rotate_shape` (perform, shape) | `segment` \| `triangle` \| `quadrilateral` | — |
| `describe_translation`, `describe_reflection`, `describe_rotation` (describe) | **`triangle` \| `quadrilateral` ONLY, and additionally NON-SYMMETRIC** | **`point` and `segment` are forbidden** |

**Why point and segment are forbidden as describe objects (mathematical justification).** A describe task requires that **exactly one** allowed descriptor (§7 union) maps every labelled source vertex to its corresponding labelled image vertex. This uniqueness is *unachievable* for points and segments, so a redraw filter would exhaust `MAX_PARAM_ATTEMPTS` and throw on every such draw:

* **A single labelled point** `A→A′` is realised by exactly **one** translation **plus infinitely many** rotations and reflections (any axis through the midpoint of `AA′`, any centre on the perpendicular bisector) — infinitely many allowed descriptors; never unique.
* **A labelled segment** (two collinear vertices) is fixed only up to orientation, so a reflection and a rotation give the **identical labelled image**. Concrete proof: source `A=(0,0)`, `B=(1,0)`; reflection in `y=x` gives `A′=(0,0)`, `B′=(0,1)`; rotation 90° ACW about the origin gives the **same labelled image** `A′=(0,0)`, `B′=(0,1)`. Two distinct allowed descriptors fit — inherently ambiguous.

The root cause is vertex count: distinguishing **180°-rotation vs translation** needs ≥2 vertices (a non-constant image−source difference); distinguishing **reflection vs rotation** needs orientation, which a degenerate (collinear) figure cannot pin per label. A **non-symmetric (trivial-symmetry-group) triangle or quadrilateral with distinct labels** admits **exactly one direct isometry** and **zero allowed opposite isometries** mapping the labelled source set onto the labelled image set, so the descriptor is **provably unique**. The restriction is therefore the *affirmative* condition that makes the §10.4 `descriptor-unique` guard a confirmation rather than a search-until-throw.

### 10.3 Non-symmetry acceptance predicate (exact integer tests) (missing-item fix)

For describe-task sources the draw must additionally satisfy `nonSymmetricSource(shape)`, an **exact integer** predicate (no floats; squared lengths only):

* **Triangle** — `nonSymmetricTriangle`: the three squared side lengths `|AB|²`, `|BC|²`, `|CA|²` (each `Δx²+Δy²`, integers) are **pairwise distinct** (scalene). A scalene triangle has trivial symmetry group, so no opposite isometry can reproduce the labelled image.
* **Quadrilateral** — `nonSymmetricQuad`: **no nontrivial isometry of the lattice maps the labelled vertex set to itself.** Concretely, enumerate the finite set of integer-coordinate isometries that could fix the bounding configuration (the 8 dihedral lattice symmetries about the vertex centroid candidates need not be solved analytically; instead test that the multiset of squared edge lengths `{|AB|²,|BC|²,|CD|²,|DA|²}` together with the two squared diagonals `{|AC|²,|BD|²}` admits **no label permutation that preserves all six squared distances except the identity**). This is a finite exact-integer check (constant-size permutation scan over 4 labels) returning `false` if any nontrivial label permutation preserves every squared distance.

`nonSymmetricSource` is computed **before** the transformation is drawn; a source failing it is redrawn deterministically (it is independent of the transformation, so the loop converges quickly). The `not-symmetric-ambiguous` guard in §10.4 then re-confirms uniqueness **through the §12 candidate enumerator**, giving a second independent route.

### 10.4 Deterministic draw order (parity contract)

```
1.  task        = pickTask(rng | config.task)              // 9-slug set, single OBJECTIVE_BY_TASK map
2.  objectType  = objectTypeForTask(task, rng)             // §10.2 hard restriction (describe ⇒ triangle|quad)
3.  source      = drawSource(objectType, rng)              // integer vertices in [-W,W]^2 (§5 Shape model)
                  // for describe tasks: redraw until nonSymmetricSource(source) holds (§10.3)
4.  transform   = drawTransform(task, rng)                 // Transformation union (§4); never identity-capable
5.  transform   = canonicalize(transform)                  // §8 canonicalizer (e.g. CW quarter-turn → ACW=3)
6.  image       = engine.apply(transform, source)          // EXACT integer map (§9)
7.  lay         = viewport(source ∪ image ∪ centre?)       // re-implemented equal-scale layout
8.  accept iff  acceptItem(task, objectType, source, transform, image, lay)   // §10.5 guards
```

`drawSource` draws a point as one `next_int×2`; a segment as two distinct points; a triangle and a simple quadrilateral vertex-by-vertex, then canonicalises to CCW order (so `vertex-label-correspondence` is well-defined). For **describe** tasks `drawSource` additionally loops on `nonSymmetricSource` (§10.3) — this is a restriction, not a bias.

`drawTransform` emits only the v1.0.0 scope and never an identity:

| Task family | Draw rule | Built-in exclusions |
|---|---|---|
| `translate_*` | `(dx,dy) = (next_int(-D,D), next_int(-D,D))`; redraw while `dx==0 && dy==0` | zero vector excluded **in the draw** |
| `reflect_*` | axis ∈ {`x=a`, `y=b`, `y=x`, `y=-x`}; `a,b = next_int(-W,W)` | only the four supported lines are constructible |
| `rotate_*` | `quarterTurnsCCW ∈ {1,2,3}` (never 0); centre `(h,k) = next_int(-W,W)×2` | `0/360°` impossible; only 90/180/270 |

The drawn transform is **canonicalised** by the §8 canonicalizer before use, so any descriptor stored on a describe-task item is already canonical.

### 10.5 Acceptance guards (deterministic; redraw on any failure)

`acceptItem` is a conjunction; **all must hold** or the loop redraws. Guards are grouped by the owner brief "EDGE-CASE POLICY":

| Guard | Condition | Excludes |
|---|---|---|
| `nonzero-effect` | `image ≠ source` as a labelled set | identity image; image-identical-to-object |
| `nonzero-vector` (translate) | `(dx,dy) ≠ (0,0)` | zero translation vector |
| `nondegenerate-source` | segment length > 0; triangle non-collinear; quad simple, non-self-intersecting, CCW | collinear triangle; self-intersecting quad; coincident vertices |
| `nondegenerate-image` | same predicates on the image (congruence makes it redundant but it is asserted) | degenerate image |
| `window-fit` | every source **and** image vertex ∈ `[-W,W]²` | source/image outside viewport |
| `viewport-feasible` | `viewport(...) ≠ null` **and** `labelsFeasibleT(...)` (§11.6, the transformations-specific feasibility function) | label/figure outside canvas |
| `figures-disjoint-enough` (perform) | no image vertex coincides with a source vertex; the image is not drawn under the source after projection; minimum projected label-box clearance (the `44²` squared-separation constant, generalised to all label-box pairs) | image-under-source; label/figure overlap |
| `no-fixed-point-hiding` (perform) | the transformation does not leave the labelled vertex/vertices carrying the intended cue fixed (e.g. reflection axis must not pass through a labelled vertex when that would hide the move) | fixed point hides the intended transformation |
| `describe-source-non-symmetric` (describe) | `nonSymmetricSource(source)` (§10.3) | symmetric describe source |
| `descriptor-unique` (describe) | the §12 candidate enumerator finds **exactly one** allowed descriptor mapping source→image | several / no allowed descriptors fit |
| `not-symmetric-ambiguous` (describe) | no symmetry of the source admits a second allowed descriptor (proven via the same enumerator) | symmetric figure admitting multiple descriptors |
| `distinct-answer-rows` (shape) | the table-completion image rows are pairwise-distinct coordinates | duplicate coordinate-answer rows |
| `point-on-axis-clear` (reflect) | a source point lying **on** the reflection axis is excluded when it would make the task unclear | source point on the reflection axis |

The `describe-source-non-symmetric`, `descriptor-unique`, and `not-symmetric-ambiguous` guards are the load-bearing describe-task guards: the latter two call the **independent** §12 candidate reconstruction (`enumerate/reconstruct every allowed candidate descriptor`), **not** the forward engine, so acceptance and validation share no forward code path. Because §10.2 already restricts describe sources to non-symmetric triangles/quads, these guards normally pass on the first attempt — they are a second independent confirmation, not the mechanism that makes uniqueness achievable.

### 10.6 Outputs of construction

A successful pass yields the frozen tuple `{task, objectType, source, transform (canonical), image, lay}`, from which **every** downstream artefact is derived by the one canonical Transformation model (§4): the prompt, the student media (§11), the answer (coordinate / ordered-pair for a point image; table-completion for a multi-vertex image; the `transformation` descriptor for describe tasks — §§6–7), the worked solution, the diagnostics (§13), the accessibility text, and the independent-validator input (§12). There is no second random source after acceptance, so the item is fully reproducible from `(seed, config.task)` — the property the 10,000-seed stability + reproducibility sweep re-checks.

---

## 11. Cartesian SVG rendering contract

### 11.1 Reused infrastructure — precise attribution (blocker + reattribution fixes)

Figures are drawn on a **re-implemented** Cartesian render layer inside `domains/geometry/transformations.ts` (Py oracle authoritative): a byte-identical re-author of the coordinate-lines `viewport()` / `gridRound` / `projX`/`projY` / grid-axes-tick element builders, with the `0 0 1000 700` viewBox, integer-pixel projection (single `gridRound`, round-half-up over exact `Rational`), and the equal-scale `U`. As established in §10.1, these geometry primitives are **re-implemented, not imported** (the coordinate-lines functions are module-private; the approved coordinate-lines file is **not edited**), exactly as `mensuration.ts` redefines its own `gridRound`.

The **only** layer imported from approved shared code is **`core/visual-style/cartesian-theme.ts`**: `COMMON_CSS`, `modeVars`, `resolveCommonCss`, `MODES`, and the `presentationSvg()` / `exportSvg()` helpers (6000×4200 defaults). **`cartesian-theme.{json,ts}` is NOT edited.** Transformation-specific styling is an **additive versioned theme extension** — `core/visual-style/transformations-theme.{json,ts}`, built **exactly** like `core/visual-style/mensuration-theme.ts`: it imports `COMMON_CSS` / `modeVars` / `resolveCommonCss` from `cartesian-theme`, contributes only *new* `--cx-*` variables and one additional ruleset (source-vs-image marker shapes, dash / fill patterns, vector-arrow, axis line, centre marker, quarter-turn arc, working labels), and re-exports the same `stripCanonicalStyle`-based `presentationSvg()` / `exportSvg()`. Coordinate-lines and stats outputs are unaffected because the extension only adds variables under the shared `cx-figure` root.

**Canonical SVG is monochrome; the four modes are TS-only derivations (parity fix).** The canonical `media[0].svg` — the **byte-identical Py↔TS artifact** over which all parity is asserted — contains **only** the family's hardcoded monochrome `STYLE` constant (extending the coordinate-lines / mensuration `GREYS` palette `{#111,#333,#444,#555,#888,#bbb,#fff}`). The four modes `premium` / `premium-dark` / `accessible` / `print` are **TS-only, after-the-fact derivations** produced by `presentationSvg()` / `exportSvg()`, which **strip** the canonical `<style>` (`stripCanonicalStyle`) and inject `modeVars` (mensuration-theme.ts:58–71). **The mode variables never enter the byte-parity canonical SVG.** Byte-parity is asserted over the monochrome canonical SVG only; `print` is monochrome-authoritative because it is the canonical render with the shared monochrome ruleset resolved.

### 11.2 Three-channel, group-structured figure — MENSURATION precedent (reattribution fix)

The **named-channel-group architecture** — the `class="cx-figure"` root, `<title>`/`<desc>` as first children, the `cx-base` / `cx-annot` / `cx-overlay` group split, `extractGroup`, and a `renderSvg(..., channel, ...)` composing function — is the **mensuration precedent** (`mensuration.ts` `renderSvg`:463, `extractGroup`:701), **not** coordinate-lines: coordinate-lines' `figure()` (coordinate-lines.ts:186) emits a **flat, ungrouped** SVG (`<svg role="img" aria-label=…>` then grid/axes/ticks directly, no `<g class=…>` channels, no `cx-figure` root). The transformation figure builder is therefore a **NEW composing function** modelled on `mensuration.renderSvg` — **not** a reuse of `coordinate-lines.figure()` — that reuses the re-implemented grid/axes/tick/projection primitives and the **mensuration** `extractGroup` / base-identical / overlay-additive checks **by name**:

```
<svg viewBox="0 0 1000 700" role="img" class="cx-figure" aria-label=…>
  <title/> <desc/> <style>…canonical monochrome STYLE…</style>
  <g class="cx-base">    grid + axes + ticks + SOURCE object & labels A..D   (BYTE-IDENTICAL across channels)
  <g class="cx-annot">    student-visible task annotations (per task type, §11.3/11.4)
  <g class="cx-overlay">  answer-key ONLY: image, vector arrow, reflection axis, centre, quarter-turn arc, working
</svg>
```

* **`cx-base`** holds the grid, axes, scale and the **source** object with labels `A,B,C,D`, and is **byte-identical between the student channel and the answer-key channel** (asserted by `base-geometry-identical`: `extractGroup(student,"cx-base") === extractGroup(key,"cx-base")`, the mensuration `answer-key-base-geometry-identical` test, and non-empty).
* **`cx-annot`** holds whatever the student legitimately sees beyond the source (§11.3/11.4); it too is identical across channels (`answer-overlay-additive-only`).
* **`cx-overlay`** exists **only** in the `answer-key` channel; the student channel never contains the string `cx-overlay` (`perform-task-image-hidden` / `student-figure-has-no-overlay`).

The canonical `media[0].svg` is the **student** channel; the answer-key SVG is an additional asset on the worked-solution figure. Both are recomputed by the independent validator and asserted **byte-for-byte**, Py↔TS (§12), exactly as coordinate-lines asserts `svg-realises-data`.

### 11.3 PERFORM tasks (`translate_*`, `reflect_*`, `rotate_*`)

`cx-base` = grid + axes + **source only** with labels `A..D`. `cx-annot` carries **only** the transformation *instruction* as on-figure text where the prompt already states it (e.g. nothing graphical for "translate by (3,−2)") — **never** the image, transformed coordinates, construction arrows, a reflection axis, a rotation centre, or any overlay. The image, the vector arrow, the reflection axis, the rotation centre, the quarter-turn arc, and the coordinate working appear **only** in the `cx-overlay` of the answer-key channel (`construction-cues-solution-only`).

### 11.4 DESCRIBE tasks (`describe_translation`, `describe_reflection`, `describe_rotation`)

`cx-base` = grid + axes + **source** `A..D`; `cx-annot` = the **corresponding image** with labels `A′,B′,C′,D′` (so both figures are present for the student to describe). `cx-annot` must **not** add a translation arrow, a reflection axis (unless the task statement itself gives the line), a rotation centre (unless explicitly given), or any text stating the transformation (`describe-task-both-figures-present` + `construction-cues-solution-only`). The answer-key `cx-overlay` *may* then add the vector arrow / axis / centre / quarter-turn direction and the descriptor working.

**Describe-task a11y leakage is gated too (new check).** Because the describe-task student figure legitimately shows the image, the leakage boundary must be enforced in the **accessibility payload** as well as the SVG. A new check `student-a11y-does-not-name-transformation` (the describe analogue of the perform-only `student-a11y-does-not-state-result`, §15) asserts that for describe tasks the `media[].dataTableFallback`, `accessibility.spokenMath`, and `accessibility.longDescription` list **only** the labelled source and image **coordinates** and **never** name the transformation, mirror line, rotation centre, vector, or angle — **unless** the task statement itself supplies the line/centre. It is cross-referenced from §11.6 and §12 so describe-task a11y leakage is blocking, not just SVG leakage.

### 11.5 Source vs image visual distinction (not colour-only) (greylist fix)

Source and image are distinguished by **marker shape, line dash, and fill pattern in addition to colour**, so the print (monochrome) channel is fully authoritative and the distinction is **shape/pattern-borne**, with colour a redundant cue only:

| Role | Labels | Marker | Edge | Fill |
|---|---|---|---|---|
| Source | `A,B,C,D` | filled disc | solid | clear / hatch-A |
| Image | `A′,B′,C′,D′` | open square | dashed | dot / hatch-B |
| Vector arrow (key) | — | arrowhead `path` | solid, arrow | — |
| Reflection axis (key) | line-equation text | — | long-dash | — |
| Rotation centre (key) | `×` glyph + `(h,k)` | cross marker | — | — |

These are theme variables in `transformations-theme`. In the **monochrome canonical / print STYLE the source/image distinction is carried by MARKER SHAPE + LINE DASH + FILL PATTERN** (disc / solid / clear vs open-square / dashed / dot-or-hatch), never by grey value alone — distinguishing roles by grey band would be fragile within a 7-grey palette. A **theme-completeness assertion** (mirroring the §16 style-isolation gate) requires that **every** declared `--cx-*` variable has a print-mode value resolving into the coordinate-lines `GREYS` set `{#111,#333,#444,#555,#888,#bbb,#fff}`, so the existing `no-colour-only-information` greylist (coordinate-lines.ts:861, reused as the `source-image-distinction-not-colour-only` check) passes on every new primitive (open-square markers, dashed edges, hatch/dot fills, vector arrowhead, long-dash axis, `×` centre glyph). Labels follow the source→image correspondence (`A↔A′`) **by vertex label**, not array order (`labels-match-correspondence`), matching the §6 table-completion correspondence rule.

**No diagnostic-predicted artefact ever enters any figure or a11y payload (new constraint).** The §13 diagnostic adapters produce answer-shaped predicted-wrong responses (e.g. a vector reversal, a collapsed-to-origin shape). A one-line constraint binds them: **diagnostic-predicted coordinates and descriptors feed ONLY the free-response checker, the worked-solution pitfall notes, and the validator's diagnostic-recompute — never any student- or answer-key-channel `cx-base`/`cx-annot`/`cx-overlay` group, and never any `media[].dataTableFallback`/`spokenMath`/`longDescription` field.** The answer-key overlay shows only the **correct** image / axis / centre / arc.

### 11.6 Transformations-specific feasibility function (not `labelsFeasible` unchanged) (feasibility fix)

`labelsFeasible` in coordinate-lines (coordinate-lines.ts:612) is **hard-coded per coordinate-lines task** (`read_point`, `gradient_two_points`, `midpoint`, …) and applies the `44²` separation test only to the 2-point case; for any unknown task it leaves `pts` empty and returns **vacuously true**, testing nothing. It **cannot** be reused unchanged for transformation source+image vertex sets. This family therefore defines a **new** feasibility function `labelsFeasibleT(channel, source, image, overlayPts)` modelled on `labelsFeasible`, reusing its **constants** (the canvas bounds `[16, VIEW_W−16] × [30, VIEW_H−16]` and the `44²` squared-separation minimum):

* feed the **union** of source vertices + image vertices (+ centre / axis-anchor overlay points for the answer-key channel) through `projX`/`projY`;
* assert every projected label box lies in `[16, 1000−16] × [30, 700−16]`;
* generalise the `44*44` minimum-separation test to **all** projected label-box pairs (not just the 2-point case).

`labelsFeasibleT` backs the `viewport-feasible` guard (§10.5) and the `labels-within-canvas` / `no-label-collision` render checks below.

### 11.7 Blocking render checks (recomputed independently, Py + TS)

The independent validator (§12) rebuilds both channel SVGs from `(task, source, transform, image)` and asserts the following named checks, every one **blocking**; the byte-for-byte SVG equality is enforced for both channels in **both** languages over the **monochrome canonical** SVG:

| Check | Asserts |
|---|---|
| `answer-absent-from-student-figure` | no transformed coordinate / descriptor text in the student `media[0].svg` (semantic, role/intent based — like coordinate-lines' `no-answer-label-in-svg`) |
| `perform-task-image-hidden` | perform-task student channel contains no image markers/labels (`A′..D′`) and no `cx-overlay` |
| `describe-task-both-figures-present` | describe-task student channel contains source **and** image (`A..D` and `A′..D′`) |
| `construction-cues-solution-only` | vector arrow / axis / centre / quarter-turn arc / working appear only in `cx-overlay` |
| `student-a11y-does-not-name-transformation` (describe) | describe-task `dataTableFallback` / `spokenMath` / `longDescription` list source + image coordinates only; never name the map, axis, centre, vector, or angle (unless the task states the line/centre) |
| `base-geometry-identical` | `extractGroup(student,"cx-base") === extractGroup(key,"cx-base")` and non-empty (mensuration test, by name) |
| `answer-overlay-additive-only` | `extractGroup(student,"cx-annot") === extractGroup(key,"cx-annot")`; the key adds only `cx-overlay` |
| `source-image-style-distinct` | source and image use different marker / dash / fill tokens |
| `source-image-distinction-not-colour-only` | the distinction survives monochrome `print`; every meaning-bearing colour ∈ the `GREYS` set, reusing coordinate-lines' `no-colour-only-information` greylist; plus the theme-completeness assertion that every `--cx-*` has a print-mode greyscale value |
| `no-diagnostic-artifact-in-figure` | no §13 diagnostic-predicted coordinate/descriptor appears in any channel group or any a11y field |
| `labels-match-correspondence` | `A′` is the image of `A`, etc., by label not order |
| `no-label-collision` | no two projected label boxes overlap beyond the `44²` clearance (`labelsFeasibleT`) |
| `labels-within-canvas` | every label box ∈ `[16, 1000−16] × [30, 700−16]` (`labelsFeasibleT`) |
| `equal-axis-scale` | one equal x/y unit `U` (`viewport() !== null`) |
| `viewport-contains-source-and-image` | every source and image lattice point (and the centre, when shown) projects inside the canvas |

Across all four modes the figure is **self-contained** (the additive theme bakes the resolved ruleset into the export clone via `exportSvg`) and exports to a self-contained **6000×4200** PNG/SVG via the shared `exportSvg(svg, mode, 6000, 4200)`. The review-pack coverage matrix (§15, reusing the mensuration/stats reachability-derived coverage-matrix machinery) requires, as cells, each task × {student, answer-key} channel × {premium, premium-dark, accessible, print} × the label-collision-stress and multi-item-worksheet renderings × the 6000×4200 export — the builder **fails** on any missing reachable cell. Per §10.2, `obj:point` and `obj:segment` cells are required **only** for the perform point/shape tasks, **not** for the describe tasks, so the reachability derivation does not demand the (unreachable) point/segment-describe cells.


---

## 12. Independent validator

The validator is the **independent witness** for every generated `gen.geometry.transformations` item. It is authored oracle-first in Python (`oracle/spi_oracle/transformations_validate.py`) and mirrored byte-identically in TypeScript (`domains/geometry/transformations-validate.ts`), and it obeys the platform rule that an independent method must be **structurally different** from the generator's forward solve (cf. `VALIDATION_STANDARD.md` §3). It **never** calls the generator's forward `Transformation.apply` helper (§9); it re-derives the answer by a **second, independent route** (geometric *conditions*, not re-application of the same map) and re-derives the figure from `params`. The output contract is the shared `ValidationResult { status, validatorVersion, checks[] }` of `validate.ts`, stored on `item.lifecycle.validation`; the validator records `validatorVersion = GENERATOR_VERSION` (`"1.0.0"`, §16); any `fail` check sets `status = fail` and the seed is logged to the failing-seeds artifact.

### 12.1 Independence discipline — two routes, never one

| Quantity | Generator route (§9) | Independent route (validator) |
|---|---|---|
| Point / vertex image | the canonical `Transformation` union applied vertex-by-vertex | the **geometric-condition** route of §12.4: for each declared transformation, re-derive every image coordinate from the midpoint / centre / vector *condition*, not from re-applying the same map. |
| Shape image | forward apply over ordered labelled vertices | reconstruct via the per-family condition **and** verify the **inverse** transformation restores the source (§12.5). |
| Descriptor answer | the descriptor chosen at generation | **enumerate/reconstruct** every allowed candidate descriptor independently from the (source, image) vertex pairs and require exactly one to fit (§12.6). |
| Canonical SVG (both channels) | the family's own Cartesian renderer (the grid/axes/`gridRound`/`viewport` geometry primitives are **re-implemented byte-identically inside the transformations module**, Py oracle authoritative — exactly as `mensuration.ts` defines its own `gridRound` rather than importing the module-private one from `coordinate-lines.ts`; see §12.7) | recompute the figure from `params` through the same `gridRound` projection and assert **byte-for-byte** equality (§12.7). |

Because the two routes share **no** solve code, an error in the forward engine cannot mask itself in validation.

### 12.2 Exactness preconditions (run first; `fail` aborts the item)

| Check | Assertion |
|---|---|
| `integer-coordinate-closure` | every source coordinate, every image coordinate, every translation component `dx,dy`, every reflection line value `a`/`b`, and every rotation centre `(h,k)` is an **exact integer**; no `Rational` with `den≠1`, no float, no surd, no trig value appears anywhere in `params`, `answer`, `answer.transformation`, `solution`, or `media`. (Enforces the EXACT-MATH integer-only mandate; the quarter-turn rules are integer coordinate maps, so closure is total.) |
| `params-in-domain` | translation vector **nonzero**; reflection axis ∈ {`x=a`, `y=b`, `y=x`, `y=-x`}; rotation `quarterTurnsCCW ∈ {1,2,3}` (no `0`/`4`); rotation centre an integer lattice point; every vertex and every label inside the supported coordinate window (`viewport-contains-source-and-image`, §12.8). |
| `describe-object-type-restricted` | for `describe_translation` / `describe_reflection` / `describe_rotation`, `objectTypeForTask(task) ∈ {triangle, quadrilateral}` — a **point or segment object is rejected outright** (not redrawn). Degenerate (collinear / ≤2-vertex) figures cannot pin a unique descriptor: a single point A→A′ is the image of one translation **and** infinitely many rotations/reflections, and a labelled segment is fixed by an isometry only up to reflection (e.g. source A=(0,0),B=(1,0); reflection in `y=x` and rotation 90° ACW about the origin yield the **identical** labelled image A′=(0,0),B′=(0,1) — two valid allowed descriptors). The restriction is an **affirmative input rule** mirrored in §5.5/§10.2 `objectTypeForTask`, so describe-task uniqueness is achievable rather than left to a loop-and-throw. |
| `describe-source-non-symmetric` | for describe tasks the **labelled** source must have a **trivial symmetry group** (exact integer predicate, §12.6): a triangle has **three distinct squared side lengths** (scalene); a quadrilateral admits **no nontrivial isometry** mapping its labelled vertex set to itself. A no-symmetry labelled figure with ≥3 non-collinear vertices admits **exactly one** direct isometry and **zero** allowed opposite isometries, so the descriptor is provably unique. |
| `object-changed` | the transformation actually **moves** the object — image ≠ source as a labelled point set (rejects zero translation, 0/360° rotation, and a transformation whose fixed set swallows the whole figure; cf. the edge-case policy of §14). |

### 12.3 Answer-agreement (second-route recomputation) — every task

| Check | Assertion |
|---|---|
| `transformed-coordinate-agreement` | the validator's **second-route** image coordinate (derived from the geometric condition of §12.4, not from re-applying the forward map) equals `answer.canonical` exactly — `ordered-pair`/`coordinate` for a point image, every `table-completion` row for a shape image. |
| `all-vertices-transformed` | **every** labelled source vertex has a corresponding image entry in the answer (point: 1; segment: 2; triangle: 3; quadrilateral: 4); no vertex is dropped and no extra row is invented. |
| `vertex-label-correspondence` | correspondence is by **label** (`A→A′`, `B→B′`, …), not array order: the row keyed `A′` is the image of the source vertex labelled `A`. A permuted-but-numerically-correct table **fails** unless the label keys also match. The prime in image label keys is the fixed byte `U+2032` encoded **UTF-8** in **both** oracles (the agreed structural encoding of §5.2/§6.2); the check asserts the `location`/SVG-label key bytes are Py↔TS identical and that `canonicalStringify` does not normalise the glyph. |
| `answer-type-consistency` | point-image tasks carry the **existing** `coordinate`/`ordered-pair` contract; shape-image tasks carry the **existing** `table-completion` contract (one label-keyed row per labelled image vertex, **point-object** cell values compared component-wise via the §6 `enc_pt`/`disp_pt`/`_same_value` point-aware comparator — **not** the integer-cell `data_handling` checker); descriptor tasks carry the new owner-gated `transformation` answer object in the **sibling** `answer.transformation` field (§7) — no task introduces a polygon-answer schema. |
| `answer-solution-agree` | the final `solution.steps[].intermediateResult` equals `answer.display` (`answerSolutionAgrees`); the per-vertex working in the solution traces to the same second-route coordinates. |

### 12.4 Per-family geometric-condition checks (the owner battery — condition, not re-application)

**Translation tasks**

| Check | Assertion |
|---|---|
| `translation-vector-consistent` | for **every** corresponding pair, `image − source` is the **same** vector `(dx,dy)`; the common vector is **nonzero**. Computed as a set of integer differences; the check fails if any pair disagrees or if the vector collapses to `(0,0)`. |

**Reflection tasks**

| Check | Assertion |
|---|---|
| `reflection-axis-condition` | for the declared axis, every corresponding pair satisfies the exact mirror condition — `x=a`: midpoint `x = a` and equal `y`; `y=b`: midpoint `y = b` and equal `x`; `y=x`: `(x,y)↔(y,x)`; `y=-x`: `(x,y)↔(-y,-x)`. The **proposed axis fixes the midpoint** of every required source–image pair. |
| `reflection-distance-agreement` | each source and its image are **equidistant** from the axis (signed perpendicular distances are equal and opposite), computed in exact integer arithmetic — for `x=a`/`y=b` a coordinate difference; for `y=x`/`y=-x` an exact integer comparison, never a √2 length. |

**Rotation tasks**

| Check | Assertion |
|---|---|
| `rotation-centre-condition` | the declared centre `(h,k)` is a **fixed point** under the map (it maps to itself), and no source vertex equals the centre in a way that hides the rotation (`every-vertex-at-centre` is rejected, §14). |
| `rotation-quarter-turn-agreement` | for every vertex, the centre-relative vectors satisfy the **exact** quarter-turn rule for the declared `quarterTurnsCCW`: 1 → `(x-h,y-k)↦(-(y-k),x-h)`; 2 → `↦(-(x-h),-(y-k))`; 3 → `↦(y-k,-(x-h))`. No `sin`/`cos`; pure integer sign-and-swap. |
| `rotation-distance-preserved` | each vertex's squared distance from the centre, `(x-h)²+(y-k)²`, is **preserved** exactly (integer equality; squared distance avoids irrational lengths). |
| `rotation-orientation-correct` | the **orientation** is preserved per the declared rotation — the signed area (shoelace) of the image polygon has the **same sign** as the source, distinguishing a genuine rotation from a reflection masquerading as one. |

### 12.5 All-shape-task checks (segment / triangle / quadrilateral)

| Check | Assertion |
|---|---|
| `shape-congruence-preserved` | **corresponding side lengths agree exactly** — compared as squared integer lengths so no √ is taken — and (for triangles/quads) corresponding internal angle measures agree; the transformation changes neither side lengths nor internal angles. |
| `shape-non-degenerate` | image (and source) are non-degenerate: segment has nonzero length; triangle vertices non-collinear (shoelace area ≠ 0); quadrilateral is **simple** and non-self-intersecting; labels unique; vertices distinct. |
| `coordinate-answer-agrees-with-descriptor` | the `table-completion` coordinate answer **agrees with** the transformation descriptor: applying the §12.4 condition for the item's declared transformation to each source vertex reproduces exactly the stored image-vertex row. (Binds the coordinate contract and the descriptor contract together.) |
| `inverse-transformation-restores-source` | the **inverse** transformation — `(−dx,−dy)`; the same reflection (an involution); `4−quarterTurnsCCW` about the same centre — applied to every image vertex restores the **source** shape exactly, vertex-by-vertex and label-by-label. |

### 12.6 Descriptor-task uniqueness checks (`describe_*` tasks)

Describe tasks are restricted to non-symmetric triangles/quadrilaterals (§12.2 `describe-object-type-restricted` + `describe-source-non-symmetric`); on that input class uniqueness is **achievable**, not merely hoped for. The validator does **not** trust the stored descriptor: it independently enumerates/reconstructs every allowed candidate from the (source, image) vertex pairs and admits the item only if **exactly one** canonical descriptor maps the complete shape.

| Check | Assertion |
|---|---|
| `descriptor-maps-complete-shape` | the stored descriptor, applied by the §12.4 condition, maps **every** labelled source vertex to its corresponding labelled image vertex (no partial fit). |
| `descriptor-unique` | enumeration over the allowed v1.0.0 space yields **exactly one** descriptor mapping the complete shape. Reconstruction primitives: **translation** — the constant pairwise difference, accepted iff constant and nonzero. **Reflection** in `x=a`/`y=b`/`y=x`/`y=-x` — each candidate reconstructed from the pairwise midpoint/swap conditions (integer axis value only). **Rotation** — the centre is reconstructed **without** the degenerate "two-bisector-intersection" primitive: first test the **180° hypothesis via the common-midpoint route** (every pair's midpoint equal **and** integer ⇒ that midpoint is the centre, `quarterTurnsCCW=2`); for **90°/270°**, solve the centre as the **fixed point of the quarter-turn relation using at least two corresponding pairs whose connecting directions are non-parallel**, rejecting collinear/degenerate pair selections, and accept **only** an integer centre. A non-symmetric triangle/quad guarantees ≥3 labelled vertices and therefore always supplies a non-degenerate pair. **Zero candidates or ≥2 candidates ⇒ `fail`.** |
| `descriptor-canonical-form` | the stored descriptor is in canonical form (§7/§8): positive quarter-turns are anticlockwise; a 90° clockwise input canonicalizes to `quarterTurnsCCW=3`; 270° clockwise to `1`; a 180° rotation carries no direction; `x=0`/`y-axis` and `y=0`/`x-axis` aliases are stored identically. |
| `no-ambiguous-symmetry` | the reconstruction is rejected when **several** allowed descriptors fit, when a figure's symmetry admits multiple descriptors, when a fixed point hides the intended transformation, or when the object is unchanged. (Realises the owner reject-list; pairs with the affirmative input restriction of §12.2 and the generation-time symmetry exclusion of §14.) |

### 12.7 Canonical-SVG checks (both channels, byte-for-byte)

The shared, exported, reused layer is **`core/visual-style/cartesian-theme.ts`** (`COMMON_CSS` / `modeVars` / `presentationSvg` / `exportSvg` / `MODES`, with 6000×4200 export defaults — verified exported). The Cartesian **grid/axes/lattice-point/viewport/`gridRound` geometry primitives are re-implemented byte-identically inside the transformations module** (Py oracle authoritative, TS mirror), exactly as `mensuration.ts` defines its own `gridRound` rather than importing the module-private `viewport`/`gridRound`/`labelsFeasible`/`U_MIN`/`DATA_MARGIN_UNITS` from `coordinate-lines.ts`. The **base-geometry + additive-overlay** dual-channel architecture (named SVG groups `cx-base`/`cx-annot`/`cx-overlay`, `extractGroup`, `renderSvg(…,channel,…)`, the `class="cx-figure"` root, `<title>`/`<desc>` as first children) is reused **by name from `domains/measurement/mensuration.ts`** (the mensuration precedent — `coordinate-lines.figure()` emits a flat ungrouped SVG and is **not** the source of the channel pattern). The transformation `figure()` is a **new composing function modelled on `mensuration.renderSvg`**, not a reuse of `coordinate-lines.figure()`. The approved `coordinate-lines`/`cartesian` renderer is **not edited**.

| Check | Assertion |
|---|---|
| `svg-realises-data` | recompute the **canonical monochrome SVG** from `params` (family-local grid/axes/lattice-point primitives; viewBox `0 0 1000 700`; integer pixel coords via the family's own `gridRound` over exact `Rational`; **no runtime trig**; the hardcoded family `STYLE` constant extending the `coordinate-lines`/`mensuration` `GREYS` palette; root attrs `class="cx-figure"` + `role="img"` + `<title>`/`<desc>` first children + data-table fallback) and assert `== media[0].svg` **byte-for-byte**, Py↔TS identical. The premium / premium-dark / accessible / print modes are **TS-only** derivations via `presentationSvg()`/`exportSvg()` (strip canonical `STYLE`, inject `modeVars`) and **never** enter the byte-parity canonical artifact. |
| `figure-realises-shape` | every drawn object/image vertex, edge, and label maps to a `params` vertex/edge/label (second-route geometry agrees with `params`); the source uses the A,B,C,D marker/line/fill family and the image uses A′,B′,C′,D′ with a **distinct marker shape / line pattern / fill pattern** (`source-image-style-distinct`). |
| `equal-axis-scale` | the x- and y-axis pixel scales are equal (squares are square) so a rotation/reflection is not visually sheared. |
| `theme-extension-intact` | the figure uses the **additive** versioned transformations theme (`extends "spi-math-cartesian-theme/1"`, following the `data-chart-theme`/`mensuration-theme` additive pattern); `presentationSvg`/`exportSvg` compose cartesian + transformation rulesets only; **theme-completeness** holds — every declared `--cx-*` variable resolves to a value in the print-mode `GREYS` set `{#111,#333,#444,#555,#888,#bbb,#fff}` (so the new primitives — open-square image markers, dashed image edges, hatch/dot fills, vector arrowhead, long-dash axis, × centre glyph — are greyscale in the authoritative print render); the approved coordinate-lines/cartesian renderer is **unchanged** (regression-guarded); the 6000×4200 (S=6) self-contained export preserves exact geometry. |
| `base-geometry-identical` (= `answer-key-base-geometry-identical`) | the canonical base-geometry fragment (root + grid + axes + source object + student annotations, group `cx-base`) is **byte-identical** between the student and answer-key SVGs; the answer overlay never alters student geometry. |
| `answer-overlay-additive-only` (= `answer-key-overlay-additive-only`) | the **only** inter-channel difference is the additive solution-overlay group (`cx-overlay`); the image object, translation-vector arrow, reflection axis, rotation centre, quarter-turn direction, and coordinate working appear **only** on the keyed answer asset, never in a student export, and the asset ids cannot be swapped. |

### 12.8 Role-based figure / answer-leakage checks (from §11)

Leakage is judged **semantically by role/intent** (per the canonical-SVG discipline): given data that happens to equal an answer coordinate is not leakage; a dedicated answer/solution annotation in the *student* figure is.

| Check | Assertion |
|---|---|
| `answer-absent-from-student-figure` | no image coordinate, descriptor, or computed result appears as an answer/solution annotation in the student render or its `dataTableFallback`/`spokenMath`/`longDescription`. |
| `perform-task-image-hidden` | for `translate_*`/`reflect_*`/`rotate_*` the student figure shows **only** the labelled source, grid, axes + scale, and the instruction — **not** the image, transformed coordinates, construction arrows, reflection axis, rotation centre, or a transformation overlay. |
| `describe-task-both-figures-present` | for `describe_*` the student figure shows the labelled source **and** the corresponding labelled image — with **no** translation arrow, **no** reflection axis (unless the task explicitly gives it), **no** rotation centre (unless explicitly given), and **no** wording stating the transformation. |
| `construction-cues-solution-only` | the translation-vector arrow, reflection axis, rotation centre, quarter-turn direction, and coordinate working exist **only** on the answer-key/solution overlay (`cx-overlay`). |
| `student-a11y-does-not-state-result` (perform) | for `translate_*`/`reflect_*`/`rotate_*` the student `dataTableFallback`/`spokenMath`/`longDescription` list only the labelled source coordinates and the instruction — never the image coordinates, the descriptor, or a computed result. |
| `describe-a11y-does-not-state-map` (describe) | for `describe_*` the student `dataTableFallback`/`spokenMath`/`longDescription` list **only** the labelled source **and** image coordinate sets and **never** name the transformation, mirror line, centre, vector, or angle — **unless** the task statement itself supplies the line/centre. (The text-channel analogue of `describe-task-both-figures-present`; closes the describe-task a11y leakage gap.) |
| `source-image-distinction-not-colour-only` | source and image are distinguishable by **marker shape / line pattern / fill pattern** (disc/solid/clear vs open-square/dashed/dot-or-hatch), with colour a redundant cue only, verified against the monochrome `print` mode (authoritative) and `premium-dark`. |
| `labels-match-correspondence` / `no-label-collision` / `labels-within-canvas` | image labels are the primed counterparts of the source labels they correspond to; a **transformations-specific feasibility function** (modelled on `coordinate-lines.labelsFeasible`, **not** reused unchanged) feeds the **union of source + image vertices** (+ centre/axis overlay points on the key channel) through the projection and asserts every projected label box lies in `[16, VIEW_W−16] × [30, VIEW_H−16]`, pairwise disjoint and disjoint from markers/edges, with the `44²` squared minimum-separation test generalised to **all** label-box pairs. |
| `viewport-contains-source-and-image` | the generated viewport contains every source point, every image point, and every label with the approved clearance; an image hidden directly beneath the source is rejected (§14). |
| `no-predicted-misconception-in-figure` | **no** diagnostic-predicted coordinate or descriptor (§13) appears in any student- or answer-key-channel SVG group (`cx-base`/`cx-annot`/`cx-overlay`) or any media a11y field; the answer-key overlay shows only the **correct** image / axis / centre / arc. Diagnostic adapters feed **only** the free-response checker, the worked-solution pitfall notes, and the validator's `diagnostic-recompute`. |

### 12.9 Schema / lifecycle / structural checks (every item)

| Check | Assertion |
|---|---|
| `generator-identity` | `item.generatorId == "gen.geometry.transformations"` and `item.generatorVersion == "1.0.0"` — the family registry constants (§16), carried identically by every item, golden fixture, manifest, and sequence-registry entry (parallel to `coordinate-lines` `GENERATOR_ID`/`GENERATOR_VERSION`). |
| `objective-mapping` | `item.objectiveIds == [OBJECTIVE_BY_TASK[task]]` — the single-source `core/curriculum/transformations-objective-ids.ts` map (cf. `mensuration-objective-ids.ts`), cross-checked by `transformations-graph.test.ts`. |
| `interaction-type` | **free-response only** in v1.0.0: `item.interactionType == "free-response"` and `supportedInteractionTypes == ["free-response"]`; an explicit multiple-choice request is **rejected** with an `interaction-not-supported` error and is **never silently replaced** by a free-response item. |
| `schema-valid` | the item validates against `question-item.schema.json`, including the **owner-gated `transformation`** `answerType` and the sibling `answer.transformation` structured descriptor, in **all three** gates: bundled **Ajv** (recompiled via `scripts/compile-schemas.mjs → core/schema/compiled/`), the extended **`oracle/check_conformance.py`**, and the import/bank/export round-trip. The descriptor's discriminated union is expressed with **`if`/`then`/`const` discriminant rules keyed on `kind`** under `answer.allOf` (exactly as the approved `measure` block at lines 253–268), **not** `oneOf`/`anyOf` — because `check_conformance.py` honours `const`/`allOf`/`if`/`then` but has **no `oneOf` branch**; the `if/then/const` form keeps the "no new checker code path" guarantee true on the Python conformance gate. Malformed top-level keys are caught by `answer`'s `additionalProperties:false` (line 210), and a dual `if not type==transformation then properties:{transformation:false}` clause forbids the descriptor off-type, exactly as `units:false`/`measure` are gated. |
| `descriptor-schema-conformance` | when `answer.type == "transformation"`, `answer.transformation` matches its discriminated union exactly (`translation`/`reflection`/`rotation` with the per-`kind` required fields and integer values), checked **independently of Ajv** by the validator's own structural routine (mirroring the §4.4 quantity precedent). `answer.canonical` holds the byte-stable display-key form of the canonical descriptor (so the schema-required `canonical` field is populated and the bank round-trip is deterministic, §7/§16). |
| `difficulty-in-band` | `overallBand ∈ TASK_BANDS[task]`; band recomputed from weighted axes via `bandFromScore` (§14). **Axis-name guard:** every emitted `difficulty.axes` key is a member of the platform's **closed 16-axis enum** `{numericalComplexity, algebraicComplexity, reasoningSteps, abstraction, representation, familiarity, readingDemand, informationDensity, irrelevantInformation, requiredConnections, exactVsApproximate, calculatorDependence, scaffolding, proofDemand, interpretationDemand, modellingDemand}`. The owner spatial factors are mapped onto existing axes — point-vs-multi-vertex-shape and axis-crossing onto `representation`/`abstraction`, vertex-count and visual-information onto `informationDensity`, perform-vs-describe onto `reasoningSteps`/`interpretationDemand`. **No `spatialReasoning`** is emitted (it is **not** in the schema enum; emitting it would fail Ajv and `check_conformance.py`). |
| `reproducible` | re-running `generate(seed, config)` yields byte-identical serialization (deterministic Mulberry32 redraw order is the parity contract). |
| `provenance` / `version-fields` | `provenanceComplete`, `versionFieldsPresent`. |

### 12.10 Sweep and reproducibility

The full check set runs over the **golden** seeds, the **task-pinned parity** fixture (≥300, free-response), and the **`SPI_SWEEP=10000`** stability + reproducibility re-check. **Zero** items may fail; every failing seed is written to the failing-seeds artifact `{generatorId, generatorVersion, seed, config, failingChecks[]}`. The validator records `validatorVersion`; the distribution report it feeds proves every declared band is reachable (§14), and — because describe tasks exclude point/segment (§12.2) — the §15 coverage matrix requires `obj:point`/`obj:segment` cells **only** for the perform point/shape tasks, so the reachability derivation never demands an unreachable describe-point/segment cell.

---

## 13. Misconception and diagnostic registry

All nine tasks are **free-response only** in v1.0.0, so the registry contains deterministic **free-response diagnostics + feedback rules**, never multiple-choice distractors (a later version may add MC). The registry is `MISC.TRANS.*`, authored as a byte-parity pair — `oracle/spi_oracle/transformations_misconceptions.py` + `domains/geometry/transformations-misconceptions.ts` — mirroring the **approved `MISC.MENS.*` structure** exactly (`{ id, group, title, observableError, feedback, expectedCode|null, adapter }`, with the `GROUP_PEDAGOGICAL` null-adapter discipline). It is the **single source of truth** for diagnosed wrong answers across the solver (worked-solution pitfalls), the free-response checker (targeted diagnostic feedback), and the independent validator (independent recomputation); every other section references these ids **verbatim**, and `transformations-graph.test.ts` asserts `keys(RULES_BY_TASK) == TRANSFORMATIONS_TASKS`, that every referenced id exists (including each objective's `commonMisconceptions[]→MISC.TRANS.*` linkage), and that no alternative spelling appears anywhere.

### 13.1 Rule shape and the shared `ctx`

Each diagnostic is `{ id, group, title, observableError, feedback, adapter, applicability }`, exactly as in `mensuration-misconceptions.ts`:

- **`observableError`** — what a marker sees; **no internal symbols**.
- **`feedback`** — targeted feedback phrased from displayed coordinates/values; **no internal symbols**.
- **`adapter(ctx) → PredictedResponse | null`** — **deterministic**; returns the predicted wrong response in the **same shape as the task's answer** (an `ordered-pair`/`coordinate` for a point task, a full `table-completion` for a shape task, a structured `transformation` descriptor for a `describe_*` task), or `null` for its **collision / inapplicability** behaviour. A rule that is inapplicable to the task, or whose predicted response would **collide** with the correct answer, returns `null` and is **omitted** — never emitted as a null prediction carrying a numeric/structured code.
- **`applicability(ctx) → bool`** — eligibility predicate; combined with `RULES_BY_TASK` (preference-ordered) to record which diagnostics apply per task.

`predictedKind ∈ {numeric, structured, pedagogical}`: `numeric` = a wrong point coordinate; `structured` = a wrong multi-vertex table or wrong descriptor; `pedagogical` = a non-computational hint whose `adapter` always returns `null` (e.g. a generic orientation reminder), surfaced as feedback only. The shared `ctx` exposes the solver's exact intermediates so adapters never re-derive geometry:

```
ctx = { task, transform,                 // canonical Transformation union (§4)
        source: {label,x,y}[],           // ordered labelled source vertices (integers)
        image:  {label,x,y}[],           // correct image vertices (integers)
        dx?, dy?,                         // translation
        axis?,                            // reflection axis descriptor {kind,value|equation}
        centre?: {x,y}, quarterTurnsCCW?, // rotation
        origin: {x:0,y:0} }
```

`Pt(x,y)` builds a point in the answer's shape; `Tbl({label→(x,y)})` builds a `table-completion`; `Desc(...)` builds a structured `transformation` descriptor. **No arbitrary nearby wrong coordinates** are ever manufactured — every predicted response is the exact image of a *named* error rule applied with integer arithmetic.

### 13.2 Translation diagnostics (group `translation`)

| Id | Title / rule | observableError (marker-facing) | applicability | adapter → predicted response |
|---|---|---|---|---|
| `MISC.TRANS.REVERSE_VECTOR` | Reverses the vector · `(x−dx, y−dy)` | Moves the shape the opposite way along the arrow. | `translate_point`, `translate_shape` | each vertex `Pt/Tbl(x−dx, y−dy)`; `null` if it collides with the correct image (vector self-inverse only when `(dx,dy)=(0,0)`, already excluded). |
| `MISC.TRANS.SWAP_DX_DY` | Swaps the components · `(x+dy, y+dx)` | Uses the across-step for the up-step and vice-versa. | both translate tasks | `Pt/Tbl(x+dy, y+dx)`; `null` when `dx==dy` (no observable change). |
| `MISC.TRANS.CHANGE_ONLY_X` | Moves only horizontally · `(x+dx, y)` | Applies only the across-step; forgets the up/down-step. | both translate tasks | `Pt/Tbl(x+dx, y)`; `null` when `dy==0`. |
| `MISC.TRANS.CHANGE_ONLY_Y` | Moves only vertically · `(x, y+dy)` | Applies only the up/down-step; forgets the across-step. | both translate tasks | `Pt/Tbl(x, y+dy)`; `null` when `dx==0`. |
| `MISC.TRANS.WRONG_SIGN_ONE_COMPONENT` | Wrong sign on one component · `(x+dx, y−dy)` | Gets one direction the right size but the wrong way. | both translate tasks | `Pt/Tbl(x+dx, y−dy)`; `null` when `dy==0`. |
| `MISC.TRANS.FROM_ORIGIN_NOT_VERTEX` | Translates from the origin · maps every vertex to `(dx, dy)` | Treats the vector as the destination, sending the whole shape to one point. | both translate tasks | each vertex `Pt/Tbl(dx, dy)` (collapses the shape); `structured` for shapes; `null` if a single source vertex already equals `(dx,dy)`. |

### 13.3 Reflection diagnostics (group `reflection`)

| Id | Title / rule | observableError | applicability | adapter → predicted response |
|---|---|---|---|---|
| `MISC.TRANS.X_AXIS_FOR_Y_AXIS` | Reflects in the x-axis instead of the y-axis · `(x,−y)` | Flips top-to-bottom when it should flip left-to-right. | reflect tasks where `axis = y=b` (horizontal-line family, incl. `y=0`) | apply `(x,−y)`; `null` if it equals the correct image (figure symmetric about the x-axis). |
| `MISC.TRANS.Y_AXIS_FOR_X_AXIS` | Reflects in the y-axis instead of the x-axis · `(−x,y)` | Flips left-to-right when it should flip top-to-bottom. | reflect tasks where `axis = x=a` (incl. `x=0`) | apply `(−x,y)`; `null` on x-axis-symmetric figures. |
| `MISC.TRANS.NEGATE_WRONG_COORDINATE` | Negates the wrong coordinate (applies the line constant to the **wrong** component) | Changes the coordinate that should have stayed the same. | `x=a` and `y=b` reflections | **exact map** — if `axis.kind=='vertical'` (`x=a`, correct image `(2a−x, y)`): `Pt/Tbl(x, 2a−y)`; if `axis.kind=='horizontal'` (`y=b`, correct image `(x, 2b−y)`): `Pt/Tbl(2b−x, y)`; `null` on collision with the correct image. *(Verified distinct: reflect `x=4` of `(1,3)` correct `(7,3)`, misconception `(1,5)`.)* |
| `MISC.TRANS.YEQX_CHANGES_BOTH_SIGNS` | Treats `y=x` as negating both · `(−x,−y)` | Turns a diagonal flip into a half-turn. | `axis = y=x` | apply `(−x,−y)`; `null` if it equals `(y,x)` (only at the centre). |
| `MISC.TRANS.YEQNEGX_ONLY_SWAPS` | Treats `y=−x` as a plain swap · `(y,x)` | Swaps the coordinates but forgets the sign change. | `axis = y=-x` | apply `(y,x)`; `null` if equal to `(−y,−x)`. |
| `MISC.TRANS.XEQ0_FOR_XEQA` | Reflects in `x=0` instead of `x=a` · `(−x,y)` | Mirrors across the y-axis instead of the marked line. | `axis = x=a` with `a≠0` | apply `(−x,y)`; `null` when `a==0` (line is the y-axis). |
| `MISC.TRANS.YEQ0_FOR_YEQB` | Reflects in `y=0` instead of `y=b` · `(x,−y)` | Mirrors across the x-axis instead of the marked line. | `axis = y=b` with `b≠0` | apply `(x,−y)`; `null` when `b==0`. |

### 13.4 Rotation diagnostics (group `rotation`)

| Id | Title / rule | observableError | applicability | adapter → predicted response |
|---|---|---|---|---|
| `MISC.TRANS.WRONG_DIRECTION` | Turns the wrong way · uses `4−q` quarter-turns ACW | Turns clockwise when it should be anticlockwise (or the reverse). | `rotate_point`, `rotate_shape` with `q∈{1,3}` | apply the `4−q` quarter-turn rule about the same centre; `null` when `q==2` (a half-turn has no direction). |
| `MISC.TRANS.ABOUT_ORIGIN_NOT_CENTRE` | Rotates about the origin · centre `(0,0)` not `(h,k)` | Spins around the origin instead of the marked centre. | both rotate tasks with centre `≠ origin` | apply the declared quarter-turn about `(0,0)`; `null` when `(h,k)==(0,0)`. |
| `MISC.TRANS.RULE_180_FOR_90` | Uses the 180° rule for a 90° turn · `(2h−x, 2k−y)` | Turns a quarter-turn into a half-turn. | both rotate tasks with `q∈{1,3}` | apply the 180° map about `(h,k)`; `null` when `q==2`. |
| `MISC.TRANS.SWAP_WITHOUT_SIGN` | Swaps coordinates without the sign change · centre-relative `(x−h,y−k)↦(y−k,x−h)` | Swaps the coordinates but forgets the minus sign the turn needs. | both rotate tasks with `q∈{1,3}` | apply the centre-relative swap `(x−h,y−k)↦(y−k,x−h)`, translate back. **This map is a reflection in the diagonal `y−k=x−h` through the centre, so it FIXES any vertex on that diagonal** (e.g. `(4,1)` about `(2,−1)` → `(4,1)` = the source). Chosen, byte-parity-pinned behaviour: a per-vertex **source-coincidence is a valid structured prediction** (a genuine, observably-wrong student artifact — that row simply equals the source) and is **kept**, not nulled; the adapter returns `null` **only** when the *whole* predicted response equals the *correct* quarter-turn image. *(`numeric` for `rotate_point`; `structured` for `rotate_shape`.)* |
| `MISC.TRANS.ROTATE_THE_CENTRE` | Rotates the centre too · adds the *rotated* centre back instead of the original | Moves the centre point as well, shifting the whole result. | both rotate tasks | apply the correct quarter-turn about `(0,0)`, then add the **rotated** centre offset (a deterministic offset error) instead of `(h,k)`; `null` on collision with the correct image. |
| `MISC.TRANS.APPLY_TO_ONE_VERTEX` | Applies the rule to only one vertex | Transforms one corner and copies the rest unchanged. | `rotate_shape` only | `Tbl` = correct image for the first labelled vertex, **source** coordinates for the rest; `null` for `rotate_point` (single vertex) and `null` if source==image there. |

### 13.5 Descriptor diagnostics (group `descriptor`; `describe_*` tasks — predicted **descriptor**, not coordinates)

These predict a wrong **structured `transformation` descriptor**, exercising the §8 equivalence checker so a near-miss descriptor is graded wrong with targeted feedback. (Describe tasks operate only on non-symmetric triangles/quadrilaterals, §12.2.)

| Id | Title / rule | observableError | applicability | adapter → predicted descriptor |
|---|---|---|---|---|
| `MISC.TRANS.RIGHT_TYPE_WRONG_VECTOR` | Correct type, wrong vector | Names a translation but reads the wrong column vector. | `describe_translation` | `Desc(translation, dx_wrong=dy, dy_wrong=dx)` (swapped) or sign-flipped one component; `null` if it normalizes to the correct descriptor. |
| `MISC.TRANS.RIGHT_REFLECTION_WRONG_AXIS` | Correct reflection type, wrong axis | Says "reflection" but in the wrong line. | `describe_reflection` | `Desc(reflection, axis=sibling)` — `x=a→x=−a` or `x=0`; `y=x→y=−x`; etc.; `null` if equal under §8 alias normalization. |
| `MISC.TRANS.RIGHT_ANGLE_MISSING_CENTRE` | Correct angle, missing centre | Gives the turn but no centre — an **incomplete** description. | `describe_rotation` | structured-but-incomplete `Desc(rotation, quarterTurnsCCW=q, centre=null)`; the checker **rejects** it (`right-angle-missing-centre` ⇒ not full correctness); `predictedKind=structured`. |
| `MISC.TRANS.RIGHT_CENTRE_WRONG_DIRECTION` | Correct centre, wrong direction | Right centre and quarter, turned the wrong way. | `describe_rotation` with `q∈{1,3}` | `Desc(rotation, centre=(h,k), quarterTurnsCCW=4−q)`; `null` when `q==2` (direction-less). |
| `MISC.TRANS.NAMES_REFLECTION_FOR_ROTATION` | Names a reflection for a rotation | Calls a turn a flip (mistakes the 180°/diagonal cases). | `describe_rotation` | `Desc(reflection, axis=plausible)` — e.g. names `reflection in y=x` for a 90° turn; the §8 checker rejects it via `rotation-orientation-correct` (a reflection reverses orientation); `null` if no single reflection even partially fits. |

### 13.6 Task → diagnostics map (`RULES_BY_TASK`, preference-ordered)

| Task | Applicable `MISC.TRANS.*` (preference order) |
|---|---|
| `translate_point` | `REVERSE_VECTOR`, `SWAP_DX_DY`, `WRONG_SIGN_ONE_COMPONENT`, `CHANGE_ONLY_X`, `CHANGE_ONLY_Y`, `FROM_ORIGIN_NOT_VERTEX` |
| `translate_shape` | same six as `translate_point`, all evaluated per-vertex (structured prediction) |
| `reflect_point` | axis-keyed subset: `{x=a: Y_AXIS_FOR_X_AXIS, XEQ0_FOR_XEQA, NEGATE_WRONG_COORDINATE}`, `{y=b: X_AXIS_FOR_Y_AXIS, YEQ0_FOR_YEQB, NEGATE_WRONG_COORDINATE}`, `{y=x: YEQX_CHANGES_BOTH_SIGNS}`, `{y=-x: YEQNEGX_ONLY_SWAPS}` |
| `reflect_shape` | same axis-keyed subset, per-vertex |
| `rotate_point` | `WRONG_DIRECTION`, `RULE_180_FOR_90`, `SWAP_WITHOUT_SIGN`, `ABOUT_ORIGIN_NOT_CENTRE`, `ROTATE_THE_CENTRE` |
| `rotate_shape` | the rotate-point five **plus** `APPLY_TO_ONE_VERTEX` |
| `describe_translation` | `RIGHT_TYPE_WRONG_VECTOR` |
| `describe_reflection` | `RIGHT_REFLECTION_WRONG_AXIS` |
| `describe_rotation` | `RIGHT_ANGLE_MISSING_CENTRE`, `RIGHT_CENTRE_WRONG_DIRECTION`, `NAMES_REFLECTION_FOR_ROTATION` |

Inapplicable rules (e.g. a direction rule on a 180° turn, an `x=0`-for-`x=a` rule when `a==0`) are **omitted**, not emitted with a null code — exactly the mensuration discipline.

### 13.7 Collision, inapplicability, and independent-recomputation discipline

For every item the validator independently re-runs each applicable rule's `adapter` on the **recomputed** `ctx` (`diagnostic-recompute`) and asserts:

1. **Distinct from correct.** No predicted response equals the canonical answer (point coordinate, full table, or descriptor under §8 equivalence). A rule whose recomputed result would collide returns `null` and is omitted — never recorded as a wrong answer that is secretly right. This guards the documented hazards: a self-inverse case, a symmetric figure, a fixed point, a `==0` axis/centre coincidence, or a half-turn with no direction. (Per-vertex source-coincidence inside an otherwise-wrong shape table is **not** a collision and is kept — see `MISC.TRANS.SWAP_WITHOUT_SIGN`, §13.4.)
2. **Reproduced, not copied.** The validator's recomputed diagnostic set equals the stored set (same independent route as `transformed-coordinate-agreement`); diagnostics are independent recomputations, never copies of authored values.
3. **Shape parity.** Each predicted response is the **same answer shape** as the task (`ordered-pair`/`coordinate`, `table-completion`, or structured `transformation`) and, for descriptor predictions, is graded by the §8 equivalence checker so **no ambiguous or near-miss descriptor receives full correctness** (binds to the §15 transformation-checker matrix: malformed/incomplete/missing-centre/unsupported descriptors are rejected).
4. **No arbitrary coordinates.** Every numeric prediction is the exact image of a named error rule under integer arithmetic; the registry never manufactures a nearby wrong coordinate.
5. **Diagnostics never reach the figure.** Predicted responses feed **only** the free-response checker, the worked-solution pitfall notes, and the validator's `diagnostic-recompute`. **No** diagnostic-predicted coordinate or descriptor enters any student- or answer-key-channel SVG group (`cx-base`/`cx-annot`/`cx-overlay`) or any media a11y field (`dataTableFallback`/`spokenMath`/`longDescription`); the answer-key overlay shows only the **correct** image/axis/centre/arc (enforced by `no-predicted-misconception-in-figure`, §12.8).

The review pack's required-cell space is **derived from the distribution report** by the approved reachability-driven **COVERAGE-MATRIX** machinery (reused by name in §15): required cells include **every** `MISC.TRANS.*` rule realised at least once, across all nine tasks, every reachable band, all four reflection axes, 90/180/270 rotations, and origin + non-origin centres — so each diagnostic is proven reachable and independently reproduced.


---

## 14. Difficulty and edge-case policy

### 14.1 One machine-readable source of truth

All difficulty, interaction, and answer-shape facts for the family live in **ONE** machine-readable table, `domains/geometry/transformations-config.ts` (byte-mirrored as `oracle/spi_oracle/transformations_config.py`), keyed by the single canonical task-slug set of §3 (`TRANSFORMATION_TASKS`) and consumed unchanged by parameter generation, difficulty scoring, the SDK registry tasks list, the §12 validator, the §13 diagnostics, and the §15 coverage builder. It is the analogue of the mensuration `mensuration-objective-ids.ts` + config split — no second spelling of any of these facts appears anywhere. Per task it declares:

| Field | Meaning |
| --- | --- |
| `objectiveId` | the §1 `SPI.MIDDLE.GEO.TRANS.<MICRO>.01` id (one-to-one, the §3 `OBJECTIVE_BY_TASK` source) |
| `objectTypes` | the object classes the task may emit: the six perform tasks draw from `{point, segment, triangle, quadrilateral}` per §5; the **three `describe_*` tasks are RESTRICTED to `{triangle, quadrilateral}`** (non-symmetric — see §14.1.1), never `point`/`segment` |
| `supportedInteractions` | **`["free-response"]`** for all nine tasks (v1.0.0); an explicit multiple-choice request raises `interaction-not-supported` (§3, never a silent FR substitution) |
| `answerShape` | `coordinate` \| `ordered-pair` for the three `*_point` tasks; `table-completion` for the three `*_shape` tasks; the new `transformation` type for the three `describe_*` tasks (§6/§7) |
| `objectiveRange` | `{min,max}` ⊆ 1..5, the clamp window for `bandFromScore` per objective (§14.4) |
| `taskFloor` | the minimum reachable band for the task (e.g. `translate_point` floors lower than `rotate_shape`) |
| `transformationTypes` | the subset of `{translation, reflection, rotation}` the task may emit |
| `axisWeights` | the per-task weight vector over the **closed schema-enum** difficulty axes of §14.2 (axis names are a strict subset of the 16-member `difficulty.axes` enum — see §14.2) |

`objectiveRange`/`taskFloor` are **PROVISIONAL** until the §14.4 distribution proves every declared band reachable; the build is blocked from freezing fixtures until that proof passes. Every objective carries `calculatorPolicy: "calculator-not-required"` (matching the approved `SPI.MIDDLE.GEO.COORD.*` and `SPI.MIDDLE.MEAS.*` objectives — exact integer coordinate arithmetic, no calculator), recorded in `transformations-config.ts` so the value is single-sourced into both the objective files (§16.2) and the generated items.

#### 14.1.1 Describe-task object restriction (affirmative rule, not a redraw filter)

Uniqueness of the recovered descriptor is achieved **by restricting the input object class**, not by looping the redraw until a unique instance happens to appear. The `objectTypes` for the three `describe_*` tasks is `{triangle, quadrilateral}` ONLY, and additionally **non-symmetric** (an explicit acceptance predicate, §14.5 `describe-source-asymmetric`), because:

- a single labelled **point** `A→A′` is mapped by one translation **plus infinitely many** rotations/reflections — its allowed-descriptor space is never a singleton;
- a labelled **segment** (two collinear points) is mapped by an isometry only up to reflection, so a reflection AND a rotation can give the **identical labelled image** (e.g. source `A=(0,0), B=(1,0)`: reflection in `y=x` gives `A′=(0,0), B′=(0,1)`; rotation 90° ACW about the origin gives the **same** labelled image), so two allowed descriptors fit and `descriptor-unique` (§12) must reject every instance.

A **non-symmetric labelled triangle or quadrilateral** (trivial symmetry group, distinct vertex labels) admits **exactly one direct isometry and zero allowed opposite isometries** mapping source→image, so the descriptor is **provably unique**. The restriction is enforced by a guard `objectTypeForTask(describe_*) ∈ {triangle, quadrilateral}` (§5/§10) and a named test `describe-object-type-restricted`; correspondingly the §15 coverage matrix demands `obj:point`/`obj:segment` cells **only for the perform `*_point`/`*_shape` tasks**, never for `describe_*`, so the reachability-derived matrix never asks for an unreachable cell.

### 14.2 Weighted CLOSED-enum axes feeding `bandFromScore`

Difficulty reuses `core/difficulty/band.ts` (`round3`, `clamp01`, `bandFromScore` — `1 + floor(clamp01(score) * 5)`, clamped to 5) **unchanged**; the family invents no band function. Each axis is normalised to `[0,1]`, combined as a weighted sum (`round3`), clamped to the objective range, then mapped by `bandFromScore`. Axes are drawn **only** from the existing closed `difficulty.axes` enum — VERIFIED against `schemas/question-item.schema.json` (`additionalProperties:false`, the 16 members `numericalComplexity, algebraicComplexity, reasoningSteps, abstraction, representation, familiarity, readingDemand, informationDensity, irrelevantInformation, requiredConnections, exactVsApproximate, calculatorDependence, scaffolding, proofDemand, interpretationDemand, modellingDemand`). **`spatialReasoning` is NOT a member and is NOT emitted** anywhere in the family — any item carrying it would fail bundled Ajv and `oracle/check_conformance.py` and violate the owner's "no invented axes" rule. The owner spatial factors are re-mapped onto enum-present axes (`representation` for the figure-reading / point-vs-shape demand, `abstraction` for diagonal-axis / coordinate-swap reasoning, `numericalComplexity` for off-origin / negative-coordinate arithmetic, `informationDensity` for plotted/labelled-point count):

| Owner factor | Closed-enum axis | Normalised signal (exact, integer-derived) |
| --- | --- | --- |
| point vs multi-vertex shape | `representation` | 0 for `*_point`; rises with vertex count for `*_shape` (a multi-vertex figure is a richer representation to read) |
| number of vertices | `informationDensity` | segment = 2, triangle = 3, quadrilateral = 4 vertices → density |
| positive vs negative coords | `numericalComplexity` | count of negative source/image components |
| crossing one / both axes | `representation` | object+image bounding box crosses x-axis, y-axis, or both (more of the plane to read) |
| origin vs non-origin rotation centre | `numericalComplexity` | rotation centre `(h,k) = (0,0)` ⇒ low; off-origin ⇒ higher (relative-coordinate arithmetic) |
| diagonal vs orthogonal reflection | `abstraction` | `x=a` / `y=b` low; `y=x` / `y=-x` high (coordinate swap, less concrete) |
| 90/270 vs 180 rotation | `reasoningSteps` | half-turn (sign flip only) low; quarter-turn (swap + sign) high |
| perform vs describe | `interpretationDemand` | `describe_*` (recover + uniquely name the map) > perform |
| amount of visual information | `informationDensity` | total plotted/labelled points (object, and image for describe) |
| scaffolding | `scaffolding` | inverse signal: a prompt-given centre/axis lowers demand |

The axis set is **closed by convention/test** (the platform schema enforces `additionalProperties:false` on `axes`, so a parity guard is belt-and-braces): `axes-in-platform-enum` asserts every emitted axis name is one of the 16 schema members, and `axes-within-declared-weights` asserts the family never emits an axis outside its declared per-task `axisWeights` keys. (This guard is now consistent with the schema — it would have FAILED on `spatialReasoning`.)

### 14.3 Worked axis examples (illustrative, not exhaustive)

- `translate_point`, vector `(3, -1)`, source in quadrant I, image still quadrant I → low `numericalComplexity`, zero `representation`/`informationDensity` contribution (single point), perform → **band 1–2**.
- `rotate_shape`, triangle, 90° about a non-origin centre `(2,-1)`, crossing both axes → high `reasoningSteps` (quarter-turn), high `representation` (multi-vertex + both-axes crossing), high `numericalComplexity` (off-origin, negatives), `informationDensity` for 3 vertices → **band 4–5**.
- `describe_reflection` in `y=-x`, non-symmetric triangle object+image both shown → high `interpretationDemand` (describe), high `abstraction` (diagonal), moderate `informationDensity` → **band 3–4**.

### 14.4 Ranges PROVISIONAL until the 10k distribution proves reachability

Every declared `objectiveRange`/`taskFloor` band must be **reachable** — proven, not asserted — by `docs/review/transformations_distribution.json`, the `SPI_SWEEP = 10000` report (same shape as `coordinate_lines_distribution.json` / `mensuration_distribution.json`). The distribution is the authoritative reachability artifact the §15 coverage matrix derives from. If a declared band is unreached, the build **fails before fixtures freeze**: the owner either widens the sampler (more vertex configs, wider coordinate window, more centre choices) or narrows the declared range — the ranges are not frozen until every declared band has an exemplar seed. Because `describe_*` is restricted to non-symmetric triangles/quads (§14.1.1), the distribution derivation marks `obj:point`/`obj:segment` reachable **only** under the perform `*_point`/`*_shape` tasks, so no describe-task point/segment cell is ever expected.

### 14.5 Edge-case policy — deterministic exclusion / regeneration

Every owner edge case is caught **deterministically at parameter generation** (`paramsInDomain`, the analogue of the mensuration degeneracy gates) and **regenerated under the seeded redraw loop** (`core/seeded-random/mulberry32.ts`; the call ORDER is the parity contract — a rejected draw advances the stream identically Py↔TS, so the redraw is byte-deterministic). No excluded configuration ever reaches an item; the redraw is bounded by a fixed cap (`MAX_PARAM_ATTEMPTS`), and the cap + redraw **rate** are reported in the §14.4 distribution so a pathological task surfaces rather than silently looping. Crucially, the describe-task uniqueness is secured **affirmatively** by the §14.1.1 object-class restriction, so the redraw loop is not the only barrier against ambiguity and cannot exhaust on an inherently-ambiguous point/segment instance. Each gate has a named check (cross-referenced to §12) and is recorded as an **exercised** token in the review pack:

| Edge case | Deterministic rule (reject ⇒ redraw) | Named gate |
| --- | --- | --- |
| zero translation vector | reject `(dx,dy) = (0,0)`; require nonzero integer vector | `translation-vector-nonzero` |
| 0° / 360° rotation | `quarterTurnsCCW ∈ {1,2,3}` only; 0/4 forbidden | `rotation-quarter-turns-in-range` |
| coincident vertices | all source vertices pairwise distinct | `vertices-distinct` |
| identity image (image == object) | reject if the transform fixes every labelled vertex | `image-differs-from-object` |
| source / image outside viewport | object **and** image bounding boxes + labels ⊆ supported window | `viewport-contains-source-and-image` |
| self-intersecting quadrilateral | reject non-simple polygons (exact-integer edge-crossing test) | `quadrilateral-simple` |
| collinear triangle | reject zero signed area (exact integer cross product) | `triangle-non-collinear` |
| describe object is point/segment | reject `describe_*` with `objectType ∈ {point, segment}` (§14.1.1; affirmative restriction, not redraw) | `describe-object-type-restricted` |
| symmetric describe source | reject a triangle/quad whose symmetry group is nontrivial (acceptance predicate below) | `describe-source-asymmetric` |
| reflection / rotation ambiguity | for describe tasks, exactly one allowed descriptor fits (§12 enumeration) | `descriptor-unique` |
| symmetric figure admitting multiple descriptors | reject any object whose symmetry lets a second allowed descriptor map source→image | `no-ambiguous-symmetry` |
| source label overlapping image label | minimum label clearance enforced; reject overlaps beyond approved clearance | `no-label-collision` |
| on-axis point making the task unclear | reject a source point ON the reflection axis (a fixed point hides the map) | `no-fixed-point-hides-transformation` |
| every vertex at the rotation centre | reject (the figure would be its own fixed point) | `not-all-vertices-at-centre` |
| image hidden directly beneath source | reject an image that renders under the source (perform-task occlusion) | `image-not-under-source` |
| duplicate coordinate-answer rows | reject a table-completion answer with two identical image-vertex rows | `no-duplicate-answer-rows` |

**Non-symmetry acceptance predicate (exact integer tests), gate `describe-source-asymmetric`.** A describe-task source is accepted only when its labelled vertex set has a **trivial symmetry group**, proven without floats:
- **Triangle** — the three squared side lengths `|AB|², |BC|², |CA|²` (exact integers) are **pairwise distinct** (scalene). A scalene triangle has no nontrivial isometry fixing its vertex set, so the only isometry mapping it onto its image is the intended one.
- **Quadrilateral** — **no** nontrivial isometry of the eight candidate maps (the 4 rotations + 4 reflections of the dihedral group of the unit square / general quad: identity, the three quarter/half/three-quarter turns, the four mirror axes) sends the labelled, ordered vertex set `(A,B,C,D)` to itself. Concretely: enumerate the eight rigid maps as exact integer coordinate transforms about the figure's integer centroid-doubled reference, apply each to `{A,B,C,D}`, and reject if any non-identity map reproduces the **same labelled** vertex set. (Side-length and diagonal-length integer comparisons are a fast pre-filter; the full eight-map check is authoritative.)

The "fixed point hides the intended transformation" cases (a point on `x=a`/`y=b`/`y=x`/`y=-x`, or a vertex at the rotation centre) are caught by both `no-fixed-point-hides-transformation` and `not-all-vertices-at-centre`, so a describe task always shows a genuinely moved figure. The `describe-source-asymmetric` + `describe-object-type-restricted` gates together guarantee the §12 `descriptor-unique` enumeration finds **exactly one** allowed descriptor (≥3 labelled vertices supply a non-degenerate basis for centre/axis reconstruction; cf. §9/§12), never zero and never two.

### 14.6 Deferred topics — DETERMINISTICALLY EXCLUDED (never silently included)

Every deferred topic is excluded the way mensuration excludes circles/π: `paramsInDomain` rejects the construction, the SDK registry exposes **no** task entry for it, and an integration test asserts each deferred id `generate`-throws and never appears in a 10,000-seed sweep. The exact-integer-coordinate rule (`core/exact-math/rational.ts`; no trig, no irrationals) is an **independent** second barrier for every trig/fractional case:

| Deferred topic | Exclusion mechanism |
| --- | --- |
| enlargements + scale factors | no scale parameter exists in the `Transformation` union (§4); a scaled image is not congruent → `shape-congruence-preserved` rejects it |
| fractional / negative scale factors | same — no scale parameter; congruence gate independently rejects |
| compositions of transformations | the engine applies exactly ONE `Transformation`; no compose path; the descriptor union has no composite kind |
| invariant-line / point proofs | not a task slug; no objective; no answer shape |
| arbitrary reflection lines | reflection axis restricted to `{vertical x=a, horizontal y=b, diagonal y=x, diagonal y=-x}`; any other line is unparsed/rejected |
| arbitrary-angle / trig rotations | `quarterTurnsCCW ∈ {1,2,3}` only; the integer quarter-turn rules use **no** sin/cos; a non-multiple-of-90 angle has no representable exact integer map → barred by the no-trig rule |
| fractional translation vectors | `vector.{dx,dy}` are integers; a fractional vector fails the schema and the exact-integer-closure gate |
| fractional rotation centres | `centre.{x,y}` are integers; `integer-coordinate-closure` rejects non-integer centres |
| transformations of curves / functions | object types are point / segment / triangle / simple quadrilateral only; no curve/function object model exists |
| tessellations | not a task; no repeating-tile model |
| matrices as the required student method | the answer contracts are coordinate / ordered-pair / table-completion / `transformation` descriptor; no matrix answer type is added (matrices may be a later version) |
| 3D transformations | the coordinate model is the 2-D Cartesian plane (§5); a z-component fails the shape schema |

### 14.7 `integer-coordinate-closure` as a standing invariant

Because translations, reflections in the four allowed lines, and quarter-turn rotations about integer centres are **exact integer coordinate maps** (§4/§9), `integer-coordinate-closure` asserts that every source vertex, every image vertex, every centre, and every translation component is an integer — there is no path by which a float, surd, or fraction can enter a coordinate. This is the structural reason the whole deferred-trig/fractional column above is doubly excluded, exactly as the no-irrationals rule doubly excludes circles in mensuration.

---

## 15. Accessibility and review-pack plan

### 15.1 Accessibility contract (reuses the canonical-SVG a11y discipline)

Every figure is one `role="img"` root with `aria-label="<alt>"` and `<title>`/`<desc>` as first children (the shipped coordinate-lines/mensuration serializer shape, NOT `aria-labelledby`), all interior grid/axis/marker/label primitives presentation-only, so axe sees one labelled image rather than many unlabelled graphics nodes. The family adds the transformation-specific a11y payload:

- **`media[].dataTableFallback` (OBJECT, on `media[]`, never on the item-level `accessibility` object).** The figure information-equivalent: a coordinate table of the labelled source vertices (A, B, C, D), the shape kind, the grid range, and the axis scale.
  - **Perform tasks** (`translate_*`, `reflect_*`, `rotate_*`): the fallback lists **only the source** object plus the transformation **instruction** ("Translate by vector (3, −1)", "Reflect in y = x", "Rotate 90° anticlockwise about (2, −1)"). It carries **no image vertices, no transformed coordinates, no constructed result** — the answer-absence discipline of §15.4 applies to the a11y payload exactly as to the SVG.
  - **Describe tasks** (`describe_*`): the fallback lists **both** the source vertices (A, B, C, D) **and** the corresponding image vertices (A′, B′, C′, D′) as coordinates, by **label correspondence**, but states **no transformation** and gives **no axis/centre/vector/angle** unless the task statement itself supplies one. The student must still infer the map; the fallback is information-equivalent to the figure, not to the answer.
- **`accessibility.spokenMath`.** Describes the object, the grid and equal axis scale, and the instruction in words — for perform tasks the transformation instruction; for describe tasks the object and image as two labelled figures with the question ("describe the single transformation that maps ABC onto A′B′C′"), **never** the answer for perform tasks, and **never** naming the mirror line / centre / vector / angle for describe tasks unless the statement gives it.
- **Non-colour distinction (monochrome-authoritative).** Source vs image are distinguished by **different marker SHAPE + line DASH + fill PATTERN IN ADDITION to colour** — object A,B,C,D **solid disc markers / solid edges**; image A′,B′,C′,D′ **open-square markers / dashed edges / dot-or-hatch fill** — with monochrome **print** authoritative. The distinction is carried by shape/dash/pattern, **colour is a redundant cue only**, because in the canonical/print STYLE several greys may be visually close. `accessibility.nonColorIndicators` enumerates the shape/pattern cues. The canonical/print render asserts every meaning-bearing colour ∈ the approved `GREYS` set (`{#111,#333,#444,#555,#888,#bbb,#fff}`, the coordinate-lines/mensuration greylist) via the reused no-colour-only-information check; a **theme-completeness** assertion requires every declared `--cx-*` variable to resolve to a print-mode greyscale value (mirrors the §16.3 style-isolation gate). Named checks `source-image-distinction-not-colour-only` and `source-image-style-distinct` (§ student-figure contract) gate this.
- **WCAG AA + axe.** The axe gate over rendered items requires **0 critical / 0 serious, WCAG AA**, across premium-light, premium-dark, accessible (CVD-safe), and print modes; contrast of object-vs-image strokes, labels, and gridlines holds in greyscale.
- **Prime-glyph byte contract.** The image labels and the `table-completion` `location` keys use the U+2032 PRIME glyph (A′, B′, …). Because the canonical answer JSON and SVG label text must be **byte-identical Py↔TS**, the prime is pinned to **UTF-8 U+2032 (`′`, bytes `E2 80 B2`)** in BOTH oracles, and a parity-fixture row asserts the `location` keys and SVG label bytes are identical across runtimes and that `canonicalStringify`/`serialize` does not escape or normalize the glyph differently. (Settled here so the a11y label text and the §6 answer keys agree byte-for-byte.)

### 15.2 Review pack — reachability-derived COVERAGE-MATRIX (reused by name)

The pack reuses the data-handling v1.0.2 / mensuration v1.0.1 **reachability-derived COVERAGE-MATRIX machinery verbatim** (`oracle/make_review_pack_*.py`, `DECISION_LOG` #48): required cells are **DERIVED from `transformations_distribution.json`**, never hand-set; a greedy task-pinned set-cover gathers exemplars; the builder's exit code is `0` **only** when `required_cells ⊆ covered`, every selected item is machine-valid, and `len(required_cells) == derived_required_cells` — any missing reachable cell prints `MISSING COVERAGE` and returns non-zero. The required-cell composition is the owner's full cross-product, each axis read from the distribution:

| Coverage axis | Required tokens (per reachable combination) |
| --- | --- |
| all nine tasks | `cell:<task>` for each of `translate_point … describe_rotation` |
| interaction | `inter:free-response` only (no MC cell anywhere; the unsupported-MC-request rejection test passes per task) |
| every reachable band | `cell:<task>:band:<b>` for each band the distribution marks reachable |
| answer representation | `shape:coordinate`, `shape:ordered-pair`, `shape:table-completion`, `shape:transformation` |
| transformation type | `tx:translation`, `tx:reflection`, `tx:rotation` |
| translation sign | `tsign:dx+`, `tsign:dx-`, `tsign:dy+`, `tsign:dy-` |
| each reflection line | `refl:x=a`, `refl:y=b`, `refl:y=x`, `refl:y=-x` |
| each rotation angle | `rot:90`, `rot:180`, `rot:270` (quarter-turns 1/2/3 ACW) |
| origin / non-origin centre | `centre:origin`, `centre:non-origin` |
| object type | `obj:point`, `obj:segment`, `obj:triangle`, `obj:quadrilateral` — **`obj:point`/`obj:segment` are required ONLY for the perform `*_point`/`*_shape` tasks; `describe_*` requires `obj:triangle`/`obj:quadrilateral` only** (§14.1.1), so no unreachable describe-point/segment cell is ever demanded |
| quadrant | `quad:I`, `quad:II`, `quad:III`, `quad:IV` (object and image across all four) |
| axes crossing | `cross:x-axis`, `cross:y-axis`, `cross:both` |
| every diagnostic rule | `diag:<rule>` for each `MISC.TRANS.*` rule of §13 |

The two coverage structures (per-task `coverageMatrix` of `{reachable, hasExemplar, exemplarSeed, note}` and the flat `coverageCells` list of every realised `(task, interaction, band, answerShape, objectType, seed)`) and the **five blocking coverage tests reused by name** are retargeted from the mensuration coverage pack:

| Coverage test | Asserts |
| --- | --- |
| `every-reachable-task-band-covered` | every reachable `cell:<task>:band:<b>` has an exemplar seed |
| `every-supported-interaction-covered` | free-response is the only supported interaction; every reachable `inter:free-response` cell has an exemplar; there are no MC cells |
| `every-task-answer-shape-covered` | every realised answer-shape token (`coordinate`/`ordered-pair`/`table-completion`/`transformation`) has an exemplar |
| `coverage-summary-matches-records` | `summary.coveredCells`/`coverageCells` agree with `records[]` (no double-count, no phantom cell) |
| `no-false-full-coverage-claim` | `summary.allCovered == (missingCoverage == [])` — the honest flag can never be `true` while a required cell is missing |

`summary.allCovered`/`summary.allValid` are the top-level honesty flags; `requiredCells == derivedRequiredCells` (the reachability-derived count, never a literal) is asserted in the exit gate and surfaced in the summary; the §16 manifest hash-attests the pack so a silent regeneration that drops a cell fails CI. Because the describe-task object set is restricted (§14.1.1), `derivedRequiredCells` itself excludes describe-point/segment combinations — the derivation accounts for the restriction so the gate never blocks on an inherently-unreachable cell.

### 15.3 Owner-mandated coverage extras (additional tokens beyond the cells)

On top of the systematic cells, `_required_tokens()` adds the owner checklist as additional FAIL-on-missing tokens:

| Owner dimension | Required token(s) |
| --- | --- |
| source-only vs object-and-image figures | `figure:source-only` (perform), `figure:object-and-image` (describe) |
| student vs answer-key overlays | `render:student-figure`, `render:answer-key` |
| premium / premium-dark / accessible / print | `render:premium`, `render:premium-dark`, `render:accessible`, `render:print` |
| label-collision stress | `collision:dense-labels`, `collision:near-axis-label`, `collision:image-adjacent-source` |
| multi-item worksheet | `render:worksheet-multi-item` (two-column worksheet layout) |
| 6000×4200 export | `export:6000x4200` (materialised raster hash) |
| answer ABSENT from perform student figure | `answer-free:student-figure` |
| describe both figures present | `describe:both-figures` |
| construction cues solution-only | `cues:solution-only` (vector arrow / axis / centre appear only in the answer-key copy) |

### 15.4 Student-figure / answer-key audit + answer-absence tests

The pack renders, for every figure item, the **student figure beside its answer-key overlay** (the two products of the student-figure contract over **BYTE-IDENTICAL base geometry**, the approved base-geometry + additive-overlay channel pattern — the `cx-base`/`cx-annot`/`cx-overlay` group channels of §11, reused **by name from `domains/measurement/mensuration.ts`**, not from coordinate-lines, whose figure is flat/ungrouped). Two explicit, **blocking** answer-absence tests are recorded per perform-task item, reusing the semantic role/intent leakage model (raw given object data is not leakage; a dedicated answer/construction annotation is):

- `answer-absent-from-student-figure` — the perform-task student SVG carries **no image object, no transformed coordinates, no construction arrow, no transformation overlay**; a source vertex that coincidentally equals an image coordinate passes (`raw-data-equality-is-not-leakage`); an image-role marker or a translation arrow fails (`perform-task-image-hidden`).
- `student-a11y-does-not-state-result` (perform) — the perform-task `media[].longDescription` and `media[].dataTableFallback` give the source object, grid, and instruction but **never** the image vertices or the descriptor (§15.1).

For describe tasks:
- `describe-task-both-figures-present` asserts object **and** image are shown with **no** translation arrow, reflection axis, or rotation centre unless the task explicitly gives it, and **no** wording stating the transformation.
- `describe-a11y-does-not-state-map` (the describe analogue of the perform a11y guard) asserts the describe-task `media[].dataTableFallback` / `accessibility.spokenMath` / `media[].longDescription` list **only** the labelled source and image **coordinates** and **never** name the transformation, mirror line, centre, vector, or angle — **unless** the task statement itself supplies the line/centre. This closes the a11y leakage path that the SVG check alone (`construction-cues-solution-only`) does not cover; it is cross-referenced from §11 and §12.
- `construction-cues-solution-only` asserts the vector arrow / reflection axis / rotation centre / quarter-turn direction / coordinate working appear **only** in the answer-key copy; `base-geometry-identical` + `answer-overlay-additive-only` assert the answer-key shares the student base geometry byte-for-byte and only adds answer-role elements.

**Diagnostic predictions never enter any figure or a11y field.** The §13 `MISC.TRANS.*` predicted wrong responses (which are answer-shaped — e.g. a vector reversed, a shape collapsed to the origin, a single vertex left at source) feed **only** the free-response checker, the worked-solution pitfall notes, and the §12 validator's diagnostic-recompute. **No** diagnostic-predicted coordinate or descriptor may appear in any `cx-base`/`cx-annot`/`cx-overlay` group of the student or answer-key SVG, nor in any `media[]` a11y field; the answer-key overlay shows **only the CORRECT** image / axis / centre / arc. This is asserted by `diagnostic-predictions-not-in-figure`.

The visual audit (`docs/review/transformations_visual_audit.html`, reusing the mensuration audit harness) renders every pack figure through the §16 object-image theme extension in all four modes via `presentationSvg()` plus the self-contained 6000×4200 copies via `exportSvg()`, with the owner stress galleries: label-collision cards (source/image labels near minimum clearance, near-axis labels), the two-column worksheet, and student-beside-answer-key pairs; `transformations_browser_verification.json` records the live-Chromium re-confirmation (four modes coexist with distinct computed strokes, the source/image pattern contrast holds, the 6000×4200 raster hash). Both are hash-attested in the §16 manifest.

### 15.5 TRANSFORMATION-CHECKER matrix

Beyond the coverage cells, the pack emits a dedicated **transformation-checker matrix** (the analogue of the mensuration quantity-checker matrix) that proves the §8 parser / canonicalizer / equivalence checker for the new `transformation` answer type accepts and rejects exactly as the contract requires. For a representative descriptor in each `kind` family, the matrix records a required outcome for each submission, and the builder **FAILS** if any required row is absent:

| Submission | Required outcome |
| --- | --- |
| equivalent **rotation** wordings ("90° clockwise about (2,−1)" vs "270° anticlockwise about (2,−1)") | both normalize to the **same** canonical `{kind:"rotation", centre:{x:2,y:−1}, quarterTurnsCCW:3}` → accepted-equivalent |
| **CW / ACW** equivalents | recognised as equal after canonicalisation (CW 90 ⇒ 3 quarter-turns ACW; CW 270 ⇒ 1) |
| **180°** direction wording ("180° clockwise" vs "180° anticlockwise" vs "half turn") | all canonicalize identically (a half-turn has no direction distinction) |
| **x-axis ↔ y=0** aliases | "reflection in the x-axis" and "reflection in y = 0" normalize **identically** to `{kind:"reflection", axis:{kind:"horizontal", value:0}}` |
| **y-axis ↔ x=0** aliases | "reflection in the y-axis" and "reflection in x = 0" normalize **identically** to `{kind:"reflection", axis:{kind:"vertical", value:0}}` |
| translation "by vector (3,−2)" vs column "[3; −2]" | normalize identically to `{kind:"translation", vector:{dx:3, dy:−2}}` |
| malformed / incomplete descriptor | rejected (e.g. unparsed trailing text, contradictory direction/angle) |
| **missing rotation centre** | rejected (`missing-centre`) |
| **missing translation vector** | rejected |
| **unsupported axis / angle** (arbitrary line, non-multiple-of-90 angle) | rejected (`unsupported-axis` / `unsupported-angle`) |
| **ambiguous** descriptor (correct type, indeterminate parameter) | **no full correctness** — never accepted as fully correct |

The rows reuse the same canonicalizer + equivalence checker the §12 validator runs (a behavioural proof, not a re-implementation), so "no ambiguous descriptor receives full correctness" and "CW/ACW + 180 + axis-alias equivalents normalize identically" are gated by construction.

### 15.6 Per-item record contents

Each `records[]` entry shows the full audit trail: `objectiveId`, task, `interactionType` (always `free-response`), answer shape (coordinate / ordered-pair / table-completion / `transformation`), seed, params; the **canonical shape model** (§5 — ordered labelled integer vertices, source/image roles, edge connectivity) echoed as the single source the figure, prompt, answer, solution, diagnostics, a11y, and validation derive from; the prompt; the **student figure beside the answer-key overlay**; the canonical answer (`answer.display`, `answer.canonical`, and for describe tasks the structured `answer.transformation` descriptor); the worked solution (`solution.steps[{number,transformation,intermediateResult}]`); the eligible `MISC.TRANS.*` diagnostic values with `observableError`/`feedback` (displayed-value language only, never injected into any figure); the a11y representation (`accessibility.spokenMath` + `media[].dataTableFallback`); the difficulty axes + band (axis names from the §14.2 closed enum only); the §12 validator `checks[].name` run (by the exact emitted strings); and the reproduction command (`python -c "...import transformations as t; print(t.serialize(t.generate(<seed>, <cfg>)))"`).

---

## 16. Versioning, lifecycle, and reusable infrastructure

`gen.geometry.transformations` follows the **identical lifecycle** the platform ran for coordinate-lines (`DECISION_LOG` #44), data-handling/stats (#49), and mensuration (#53): oracle-first build, blocking gates, **register `pending-review` (gated)**, owner review of the pack, then approval with immutable fixtures.

### 16.1 v1.0.0 scope — the nine tasks only; the family identity constants

v**1.0.0** ships **exactly** the nine tasks of the brief, **1:1** with the authored objectives, over the **Coordinate transformations** topic in domain Geometry, named by the single canonical `TRANSFORMATION_TASKS` slug set:

`translate_point`, `translate_shape`, `reflect_point`, `reflect_shape`, `rotate_point`, `rotate_shape`, `describe_translation`, `describe_reflection`, `describe_rotation`.

The family pins **one identity pair**, exported from `domains/geometry/transformations.ts` and byte-mirrored in `oracle/spi_oracle/transformations.py` (parallel to coordinate-lines' `GENERATOR_ID`/`GENERATOR_VERSION`):

```
export const GENERATOR_ID = "gen.geometry.transformations";
export const GENERATOR_VERSION = "1.0.0";
```

Every generated item's `generatorId`/`generatorVersion`, the golden/parity fixtures, the distribution report, the review pack, the manifest, and the `core/sdk/sequence-registry.ts` entry carry **this exact pair**; a `version-fields-present` validator check (cf. coordinate-lines) asserts `item.generatorId === GENERATOR_ID && item.generatorVersion === GENERATOR_VERSION`, and the artifact-IDENTITY test (§16.3) asserts the visible version string matches in both oracles.

A `transformations-graph.test.ts` assertion (modelled on the mensuration/stats graph tests) enforces that `OBJECTIVE_BY_TASK`, the §13 `RULES_BY_TASK`, the generator dispatch, the §14 `transformations-config.ts`, the §15 `cell:<task>` tokens, and this scope list all key off the **same nine-member set** — no legacy slug survives anywhere. Objectives are `SPI.MIDDLE.GEO.TRANS.<MICRO>.01`, with the approved coordinate-lines objectives (`SPI.MIDDLE.GEO.COORD.*`) as prerequisites. The deferred topics of §14.6 are **deterministically excluded** (no task entry, `paramsInDomain` rejects, integration test asserts they `generate`-throw and never appear in the 10k sweep).

### 16.2 Oracle-first build order

1. **Apply the additive `answer.type` schema delta FIRST** (§16.3 Schema gate): append `"transformation"` to `schemas/question-item.schema.json#/$defs/answerType.enum` and add the sibling `answer.transformation` object + the `if/then/const` discriminant rules (§7/§8 / §16.6), then recompile via `scripts/compile-schemas.mjs`. This must precede objective authoring because the T7–T9 (`describe_*`) objective files declare `answerTypes:["transformation"]`, whose enum member only resolves under Ajv / `oracle/check_conformance.py` once the delta lands.
2. Author `curriculum/objectives/SPI.MIDDLE.GEO.TRANS.json` (the nine objectives) against `schemas/curriculum-objective.schema.json`. Each objective carries `objectiveWording`, `successCriteria[]`, `prerequisites[] → SPI.MIDDLE.GEO.COORD.{READ_POINT,PLOT_POINT,CARTESIAN_PLANE}.01` + `SPI.MIDDLE.NUM.SIGNED_OPERATIONS.01` (all present + `reviewStatus:"approved"`, so the DAG resolves with zero unresolved-prerequisite warnings), `calculatorPolicy:"calculator-not-required"`, and `commonMisconceptions[] → MISC.TRANS.*` tabulated one task→its rule ids (the §13 `RULES_BY_TASK` map is the single source). `core/curriculum/graph-check.ts` enforces no-duplicate-id + no-prerequisite-cycle (the DAG); the bespoke `transformations-graph.test.ts` asserts the nine objectives present, prerequisites resolve, the single-source `OBJECTIVE_BY_TASK` map, and `reviewStatus:"approved-for-implementation"` for the gated build.
3. Write the **Python oracle** (`oracle/spi_oracle/transformations*`): the §4 `Transformation` union + exact integer engine, the §5 shape model, the canonical monochrome object/image SVG, the §7/§8 `transformation` descriptor schema + parser + canonicalizer + equivalence checker, and the `MISC.TRANS.*` registry. Generate golden + parity fixtures from the oracle (oracle-authoritative).
4. Mirror in **TypeScript** (`domains/geometry/transformations.ts`) using `core/exact-math/rational.ts` (integer coordinates), `core/seeded-random/mulberry32.ts`, `core/difficulty/band.ts`, the family's **own re-implemented** Cartesian grid/axes/lattice-point/`gridRound`/projection primitives (see §16.5 — re-authored byte-identically, NOT imported from coordinate-lines), the genuinely-exported `core/visual-style/cartesian-theme.ts` theme layer, and the additive object-image theme extension (§16.5). The canonical (monochrome) SVG and `params`/`answer` (with diagnostics) are **byte-identical Py↔TS**; the themed/exported copies are TypeScript-only.

### 16.3 Gates (all blocking before any approval)

| Gate | Spec |
| --- | --- |
| Golden | frozen `oracle/golden/transformations.golden.json`, Py-authored, TS-verified byte-identical (canonical item JSON + canonical monochrome object/image SVG) |
| Parity | a **≥300-entry task-pinned FREE-RESPONSE parity fixture**, `transformations.parity.json` (free-response is the only supported interaction); Py + TS **byte-identical** for item JSON + SVG, including the **U+2032 prime** in image labels / `table-completion` `location` keys (§15.1) and **point-object `table-completion` cell values** (§16.5); plus explicit tests that an **unsupported multiple-choice request is rejected for every task** with `interaction-not-supported` |
| Schema | the single additive `schemas/question-item.schema.json` extension — new `answer.type` enum member **`"transformation"`** + the sibling structured `answer.transformation` object — **OWNER-GATED**, additive, back-compatible (appended after the existing enum tail so no current member's byte-position changes; `answer.transformation` added to `answer.properties`, which has `additionalProperties:false`, so the new property is the only permitted new key and any stray top-level answer key is rejected). The discriminant is expressed with **`if/then/const` rules under `answer.allOf`** keyed on `answer.type`/`kind` — **NOT `oneOf`** — exactly mirroring the approved `quantity`/`measure` block, so the existing `oracle/check_conformance.py` (which handles `$ref`/`const`/`allOf`/`if`/`then`, but has **no `oneOf` branch**) enforces the rules with **no new checker code path**. Enforced on every path: runtime bundled Ajv, offline conformance, import, bank storage, migration, export, and the §12 validator (§7/§8 cross-ref) |
| Sweep | `SPI_SWEEP = 10000`: `invalid: 0`; **every declared band reachable before fixtures freeze** (the distribution is the reachability proof, with describe-point/segment cells excluded by construction per §14.1.1); the FR diagnostics are realised (every eligible `MISC.TRANS.*` rule surfaces feedback through the adapter the validator recomputes); the unsupported-MC-request rejection test passes per task; the §14.5 edge-case gates fire (no zero vector, no ambiguous descriptor, no out-of-viewport, no describe-point/segment, no symmetric describe source); **reproducibility re-check** (re-running a seed reproduces byte-for-byte) |
| Distribution | `transformations_distribution.json` emitted + integrity-checked; the authoritative reachability artifact the §15 coverage matrix derives from |
| Geometric validity | §12 named checks pass on every swept item: `transformed-coordinate-agreement`, `all-vertices-transformed`, `vertex-label-correspondence`, `shape-congruence-preserved`, `inverse-transformation-restores-source`, `translation-vector-consistent`, `reflection-axis-condition`, `reflection-distance-agreement`, `rotation-centre-condition`, `rotation-quarter-turn-agreement`, `descriptor-unique`, `descriptor-maps-complete-shape`, `no-ambiguous-symmetry`, `integer-coordinate-closure` |
| Style-isolation | per-root `cx-figure` isolation + materialised-export tests pass on the additive object-image extension; a theme-completeness test asserts **every** declared `--cx-*` variable has a value in **all four** modes **and a greyscale value in print** (§15.1); **coordinate-lines / data-handling / mensuration output stay byte-for-byte unchanged** (the geometry primitives are re-implemented in-module, so the approved renderers are untouched — §16.5) |
| a11y | axe gate: **0 critical / 0 serious, WCAG AA**; interior primitives presentation-only under the single `role="img"` root; `media[].dataTableFallback` present; non-colour (marker-shape/line-dash/fill-pattern) source/image distinction present and greyscale-authoritative; perform + describe a11y leakage guards pass (§15.4) |
| Exports | worksheet / answer-key / solutions + offline KaTeX render; **bank-json round-trip lossless** — including the new `answer.transformation` descriptor **and** point-object `table-completion` cell values (an explicit acceptance test, since the existing integer-cell round-trip does not cover point cells — §16.5); **6000×4200** colour + print exports self-contained |
| Integrity + graph | the blocking artifact-integrity tests (manifest + **SHA-256** over every artefact, Py + TS) and the bespoke graph test pass |
| Coverage | the §15 builder returns `0` (all reachable cells covered, `allCovered:true`, `requiredCells == derivedRequiredCells`) and the five named coverage tests + the transformation-checker matrix pass |
| Approved-generator regression | arithmetic / geometric / linear / angle-geometry / coordinate-lines / data-handling / mensuration output **byte-for-byte UNCHANGED** |

### 16.4 Registration, approval, immutability

The family registers in `core/sdk/sequence-registry.ts` as a new `GENERATORS[]` entry with an **explicit** `approvalStatus:"pending-review"` and the `GENERATOR_ID`/`GENERATOR_VERSION` of §16.1 during the build. Per `generatorsForMode` / `approvedGenerators`, a `pending-review` family is exposed **only in review mode** and **excluded from `approvedGenerators()`**, so it is gated out of normal Studio and out of production exports/samples (`build-samples.mjs` carries **zero** transformations records, asserted by the harness approval-lifecycle test) until the owner's review-pack decision.

On the **review-pack decision**:

- **APPROVE** → the registry entry flips to `approvalStatus:"approved"` with a `DECISION_LOG` reference (date + number); the nine objective files move to `reviewStatus:"approved"`; `build-samples.mjs` emits all nine tasks into `bank.json`; reviewed items are recorded as **approved golden exemplars** (`APPROVED_VERSIONS.md`); and the **golden + parity + canonical-SVG fixtures, review pack (.md/.json) + coverage matrix, transformation-checker matrix, visual audit, distribution report, browser verification, generation manifest, and the 6000×4200 export hashes become immutable** — hash-attested by `docs/review/transformations_manifest.json` and the blocking artifact-integrity + **artifact-IDENTITY** tests (SHA-256 plus visible version/commit identity, Py + TS). A tag `approved-transformations-v1.0.0` is cut. Any future change ships as a **new version**; the approved version is preserved in history (tags), unregistered and unselectable.
- **REVISE** → a corrected v1.0.1 with the prior version preserved unchanged at its tag, only the family's artefacts regenerated.
- **REJECT** → routes to a revised version; the rejected version is never registered.

Registry approval **does not auto-approve future items**: newly generated items always begin `lifecycle.state = "generated"` → **`machine-validated`**. The 10,000-seed stability + reproducibility run is the standing cross-version regression guard.

### 16.5 Reusable infrastructure versus transformations-specific code

The family **maximises reuse** of the approved infrastructure (cited by name) and adds only the genuinely transformations-specific pieces. **The renderer-reuse contract is reconciled precisely** (resolving the prior draft's contradiction): the SHARED, genuinely-**exported** layer is the **theme** module `core/visual-style/cartesian-theme.ts` (`COMMON_CSS` / `modeVars` / `presentationSvg` / `exportSvg` / `MODES`, with the 6000×4200 defaults). The Cartesian **geometry primitives** (`viewport`, `projX`/`projY`, `gridRound`, lattice-point/label placement, tick stride, label-feasibility) are **module-private** in `domains/geometry/coordinate-lines.ts` (only `generate`/`serialize`/`describe`/`validate`/`TASKS`/`GENERATOR_ID` etc. are exported). They are therefore **re-implemented byte-identically inside the new transformations module** (Python oracle authoritative, TS mirror) — **exactly as `domains/measurement/mensuration.ts` re-defines its own `gridRound` rather than importing one** — so the statement "the approved coordinate-lines renderer is NOT modified in place" holds literally (no `export` is added to it, no edit is made). We do **NOT** assert import-level reuse of those private primitives. (If true import-level sharing were ever wanted, it would be a separate, owner-gated refactor extracting them into a new `core/visual-style/cartesian-render.ts` with its own version/parity/integrity gates and a byte-for-byte regression proof — explicitly **out of v1.0.0 scope**.)

**SHARED — reused as-is, by name:**

| Shared asset | Source | Reuse |
| --- | --- | --- |
| Per-root style isolation + render modes + export (`cx-figure`, premium / premium-dark / accessible / print, `presentationSvg()` / `exportSvg()`, materialised 6000×4200 S=6) | `core/visual-style/cartesian-theme.ts` (**genuinely exported**) | every figure + the visual audit (TypeScript-only; byte-parity required of the **monochrome canonical** SVG, not the themed copies — the canonical `media[0].svg` carries only the family's hardcoded monochrome `STYLE` constant extending the `GREYS` palette; premium/dark/accessible/print are TS-only derivations via `presentationSvg()`/`exportSvg()` stripping that `STYLE` + injecting `modeVars`, exactly as `mensuration-theme.ts` does) |
| Canonical-SVG discipline + base-geometry/additive-overlay **channel-group** pattern (`cx-base`/`cx-annot`/`cx-overlay`, `extractGroup`, `renderSvg(…channel…)`, `cx-figure` root, `<title>`/`<desc>` first children, `answer-key-base-geometry-identical` + `answer-key-overlay-additive-only`) | `domains/measurement/mensuration.ts` (the channel-group precedent — coordinate-lines emits a flat, ungrouped figure) | the transformation `figure()` is a **NEW composing function modelled on `mensuration.renderSvg`**, not a reuse of `coordinate-lines.figure()`; the validator recomputes the SVG byte-for-byte and the answer by a second route |
| Cartesian grid/axes/ticks/projection **algorithm** (`viewport`, `projX`/`projY`, `gridRound`, tick stride, the `CARTESIAN_PLANE` lattice/label logic) and the constants `U_MIN`/`DATA_MARGIN_UNITS` + the 16/30/16/16 canvas bounds + 44px label separation | `domains/geometry/coordinate-lines.ts` (read as the **specification**; the renderer is NOT edited) | **re-implemented byte-identically in the transformations module** (Py authoritative, TS mirror); a transformations-specific feasibility function (modelled on `labelsFeasible`, which is hard-coded per coordinate-lines task and would vacuously pass an unknown task) feeds the **union of source + image vertices** (+ overlay centre/axis points for the answer-key channel) through `projX`/`projY` and asserts every label box ⊆ `[16, VIEW_W−16] × [30, VIEW_H−16]` with the 44²-squared min-separation generalised to all label-box pairs (`labels-within-canvas`, `viewport-contains-source-and-image`) |
| No-colour-only-information greylist | `domains/geometry/coordinate-lines.ts` `GREYS = {#111,#333,#444,#555,#888,#bbb,#fff}` | the canonical/print render asserts every meaning-bearing colour ∈ `GREYS`; the new source/image marker/dash/fill primitives all resolve to greys and stay mutually distinguishable by **shape/dash/pattern** (§15.1) |
| Exact arithmetic | `core/exact-math/rational.ts` + Python `fractions.Fraction` | all coordinates exact **integers**; congruence/distance checks via reduced-`Rational` equality; no float, no trig |
| Seeded RNG (byte-identical Py/TS, deterministic redraw order) | `core/seeded-random/mulberry32.ts` + `oracle/spi_oracle/seeded_random.py` | drives the deterministic shape/transform draw + the §14.5 redraw loop; call ORDER is the parity contract |
| Difficulty banding | `core/difficulty/band.ts` (`bandFromScore`, `round3`, `clamp01`) | weighted **closed-enum** axes (16 schema members only; no `spatialReasoning`) → band, clamped per objective; reachability proven by the distribution |
| Primitive answer checkers | `core/answer-checking/rational-checker.ts`, `core/answer-checking/coordinate-checkers.ts` | the `coordinate`/`ordered-pair` point-image answers reuse the existing coordinate checker unchanged |
| Misconception engine | the `MISC.<PREFIX>.*` registry shape (Py + byte-parity TS), `RULES_BY_TASK`, adapter `(ctx) -> predicted wrong response \| null`, validator independently recomputes each prediction | `MISC.TRANS.*` (§13) plugs in unchanged; FR diagnostics, no manufactured distractors; predictions never enter any figure/a11y field (§15.4) |
| Review-pack reachability COVERAGE-MATRIX + the five blocking coverage tests | `oracle/make_review_pack_data_handling.py` / `…_mensuration.py` (`DECISION_LOG` #48) | reused verbatim (§15): cells derived from the distribution, greedy set-cover, builder FAILS on any missing reachable cell |
| Manifest / artifact-integrity / artifact-IDENTITY / style-isolation tooling | `oracle/make_*_manifest.py` (SHA-256 + visible-version/commit identity, Py + TS) | `oracle/make_transformations_manifest.py` is a direct adaptation |
| Offline conformance | `oracle/check_conformance.py` (`$ref`/`const`/`allOf`/`if`/`then` — **no `oneOf`**) | live transformations items asserted to conform; the `transformation` discriminant obligations enforced offline alongside runtime Ajv and the §12 validator — **with no new checker code path** because the delta uses `if/then/const`, not `oneOf` (§16.3) |
| The `answer.type` extension MECHANISM | the dimensional-`quantity`/`measure` precedent (mensuration v1.0.1): schema delta → parser → canonicalizer → equivalence checker → targeted feedback → Ajv → Python conformance → import/export, additive, owner-gated, back-compatible | the **template** for adding `transformation` (§7/§8); the same eight-step contract, one new answer type only |
| SDK approval-lifecycle gating | `core/sdk/sequence-registry.ts` (`approvalStatus`, `generatorsForMode`, `approvedGenerators`) | the family registers `pending-review`, gated until approval (§16.4) |
| Delivery harness | review-pack/audit generators, offline HTML/JSON exporters, bank-json round-trip, axe gate | driven family-specifically; mechanism unchanged |

**TRANSFORMATIONS-SPECIFIC — new, this family only:**

| New asset | What it is |
| --- | --- |
| **The `Transformation` union + exact integer engine** (§4/§9) | the one canonical translation / reflection / rotation model and its exact integer coordinate rules (no trig), used by every consumer |
| **The source/image labelled-shape model** (§5) | ordered labelled integer vertices, source/image roles, edge connectivity, congruence invariants, **the non-symmetry acceptance predicate for describe sources** (§14.5), rendering + a11y metadata |
| **The `transformation` descriptor answer contract + parser / canonicalizer / equivalence checker** (§7/§8) | the OWNER-GATED new `answer.type` discriminated union + the finite human-text parser, the ACW canonical convention, and the structural equivalence checker (the headline new contract; see §16.6) |
| **The point-aware `table-completion` cell comparator** (§6) | a new byte-parity Py/TS routine that compares/displays **point-object** cell values `{x:{num,den},y:{num,den}}` via `enc_pt`/`disp_pt`/`_same_value`, since the existing `data_handling` table checker/round-trip is **integer-cell only** (`{location,value:int}`, `<td>(\d+)</td>`); the `table-completion` **container** type is reused unchanged (no polygon schema) but its value comparator is new code, gated by a point-cell round-trip acceptance test |
| **The transformations Cartesian renderer** | the in-module re-implementation of grid/axes/ticks/`gridRound`/projection (§16.5) + the `cx-base`/`cx-annot`/`cx-overlay` composing `figure()` (modelled on mensuration) + the transformations label-feasibility function (union of source+image+overlay points) |
| **The object-image theme extension** | a versioned extension that `extends "spi-math-cartesian-theme/1"` and follows the `data-chart-theme` additive PATTERN (without depending on it), adding source/image marker-shape, line-dash, fill-pattern, translation-arrow, reflection-axis, and rotation-centre primitives as new `--cx-*` variables + one additive ruleset, every variable resolving to a greyscale value in print; **coordinate-lines / data-handling / mensuration output stay byte-for-byte unchanged** |
| **The geometric-mapping validators** (§12) | the §12 named checks including **descriptor-uniqueness** (enumerate every allowed candidate descriptor; require exactly one), `shape-congruence-preserved`, and `inverse-transformation-restores-source` — independent of the generator forward helper |
| **`MISC.TRANS.*` registry** (§13) | the owner-mandated translation / reflection / rotation / descriptor diagnostics + `RULES_BY_TASK`, byte-parity Py/TS, sole id source |
| **Curriculum objectives + topic** | the nine `SPI.MIDDLE.GEO.TRANS.*` objective files (each with `successCriteria[]`, `calculatorPolicy:"calculator-not-required"`, `commonMisconceptions[]→MISC.TRANS.*`); the single-source `OBJECTIVE_BY_TASK` map keyed by the `TRANSFORMATION_TASKS` slugs |
| **The review pack + audit content** | `oracle/make_review_pack_transformations.py`, the visual audit, distribution report, browser verification, transformation-checker matrix, and manifest of §15 |

### 16.6 The headline decision — where the `transformation` answer contract lives

**Decision: FAMILY-LOCAL.** The `transformation` answer contract and its parser / canonicalizer / equivalence checker live in **`domains/geometry/transformations-descriptor.ts`** (+ the Python mirror `oracle/spi_oracle/transformations_descriptor.py`), alongside the family — matching the **verified** precedent exactly: the dimensional-`quantity` contract is **family-local** at `domains/measurement/mensuration-units.ts` (+ `oracle/spi_oracle/mensuration_units.py`), **not** in a shared `core/answer-checking/` module. (The earlier draft's claim that the quantity checker "lives in shared core, exactly as we propose" was incorrect — it is family-local, and `core/answer-checking/` holds only the primitive `rational-checker`/`coordinate-checkers`, which we reuse for the point-image answers.) This is the lowest-risk, precedent-matching placement and keeps the family self-contained, while the primitive `coordinate`/`ordered-pair` checks continue to reuse the shared `core/answer-checking/coordinate-checkers.ts`.

Rationale for family-local:

- It **matches the approved mensuration precedent verbatim** (descriptor contract beside its family), so there is no new cross-cutting surface to re-litigate at approval.
- The v1.0.0 surface is deliberately narrow — `kind ∈ {translation, reflection, rotation}`, integer vectors/centres, the four reflection axes, `quarterTurnsCCW ∈ {1,2,3}`, one canonical ACW convention, structural equivalence within that closed union. Enlargements, fractional/negative scale factors, compositions, arbitrary lines/angles, and matrices are **out of v1.0.0 scope and deferred** (§14.6).
- Should a **future** geometry family (compositions, enlargements, vectors, congruence/similarity) need the same descriptor, the contract can be **promoted to shared core as a deliberate, owner-gated refactor at that time** (a backward-compatible widening of the same union — a new `kind`, a new axis form, a `scaleFactor`), with its own version/parity/integrity gates — rather than over-generalising speculatively now. We do not pre-emptively place it in shared core.

**Schema impact — OWNER-GATED additive extension (one new answer type only).** The extension to `schemas/question-item.schema.json` is: (1) **append `"transformation"`** as a new `$defs/answerType.enum` member after the existing tail token, so every current member's byte-position is unchanged — approved families stay schema-valid byte-for-byte; (2) **add a new sibling `answer.transformation` object** to `answer.properties` (the `answer` object is `additionalProperties:false`, VERIFIED, so the named sibling is the only permitted new key and any stray top-level answer field is rejected) — the structured descriptor is a **separate field, NOT folded into `answer.canonical`**; (3) discriminant rules as **`if/then/const` under `answer.allOf`** (NOT `oneOf`), exactly mirroring the `quantity`/`measure` block:
  - `if answer.type == "transformation" then { required:["transformation"], properties:{ units:false } }` (binds the structured object to the named `answer.transformation` property and forbids the legacy `units` string — it does **NOT** constrain `answer.canonical`, which keeps its existing free-form shape so every existing serialization path stays byte-identical);
  - within `answer.transformation`: `if kind=="translation" then required:["vector"]` + `vector:{dx:int, dy:int}`; `if kind=="reflection" then required:["axis"]` + a nested `if/then` on `axis.kind` (`vertical ⇒ value:int`; `horizontal ⇒ value:int`; `diagonal ⇒ equation:const "y=x" | "y=-x"`); `if kind=="rotation" then required:["centre","quarterTurnsCCW"]` + `centre:{x:int,y:int}` + `quarterTurnsCCW:{enum:[1,2,3]}`.

**`answer.canonical` for transformation items** is the **canonical formatted descriptor string** produced by the §8 formatter (e.g. `"rotation 90° anticlockwise about (2, -1)"` for the canonical ACW form) — a single, byte-stable display key that the bank round-trip preserves verbatim; the machine-checkable structured value lives in `answer.transformation`. (Picking the canonical formatted string keeps `canonical` non-empty and stable while the structured object carries the equivalence semantics.) Because all discriminants are `if/then/const`, the existing `oracle/check_conformance.py` (`allOf`/`if`/`then`/`const`) enforces them with **no new checker code path** — the "no `oneOf`" choice is what makes the "enforced on every path with no engine change" guarantee literally true across runtime Ajv, offline conformance, import, bank storage, migration, export, and the §12 validator. The point-image tasks reuse the **existing** `coordinate`/`ordered-pair` types and the shape-image tasks reuse the **existing** `table-completion` container (point-aware value comparator added — §16.5) — **no** second polygon-answer schema is introduced — so `transformation` is the **only** new answer type the family needs (the at-most-one constraint is met).


---

## Appendix A — Open decisions for the owner

Design choices surfaced during authoring + adversarial review. They do not block the APPROVE/REVISE/REJECT of the proposal as a whole; engineering adopts the owner's answers (or the stated defaults) at build time. No implementation begins until the proposal is approved.

1. Single-point image answer type: the proposal standardises point-image tasks (T1/T3/T5) on the existing `coordinate` token to match the approved coordinate-lines families; the owner brief permits either `coordinate` or `ordered-pair`. If the owner prefers `ordered-pair` (as used by the coordinate-lines MIDPOINT objective), swap the token in §2.1/§2.3/§2.5 and the §3.2 matrix — this is a one-token change with no structural impact.
2. Strand naming: this proposal places the family in a new `coordinate-transformations` strand within the existing `geometry` domain (parallel to the existing `coordinate-geometry-straight-line-graphs` strand). Confirm this is preferred over reusing the existing coordinate-geometry strand; the ID/topic segment `GEO.TRANS` is unaffected either way.
3. Micro-segment style: objective IDs use the full upper-cased task slug as the `<MICRO>` segment (e.g. `TRANSLATE_POINT`), giving long but maximally self-documenting IDs consistent with the mensuration precedent (`PERIM.RECTANGLE`, `AREA.TRIANGLE_BASE_HEIGHT`). Confirm the owner is content with the length, or wants an abbreviated form.


## Appendix B — Cross-section consistency notes (for human double-check)

1. DIFFICULTY-AXIS BLOCKER for §14: the platform CLAUDE.md lists 'spatialReasoning?' (with a question mark) as a candidate difficulty axis, but schemas/question-item.schema.json defines difficulty.axes as a CLOSED object (additionalProperties:false) whose enum DOES NOT include spatialReasoning (the closest existing axes are representation, abstraction, reasoningSteps, numericalComplexity, interpretationDemand, informationDensity, scaffolding). The hard constraint says 'use only existing enum axis names — NO invented axes.' Section 14 MUST NOT use a 'spatialReasoning' axis unless the proposal first requests adding it to the schema as a second owner-gated change — which conflicts with the 'AT MOST ONE new answer.type and no other schema change' constraint. RECOMMENDATION: map the spatial/visual difficulty factors onto the existing 'representation' and 'abstraction' axes (plus 'informationDensity' for amount-of-visual-information and 'scaffolding'), and DROP any spatialReasoning axis. I authored the front matter accordingly (it makes no spatialReasoning claim). Flagging so §14 stays consistent.
2. Confirmed against schemas/question-item.schema.json: answer.type enum already contains 'quantity' (mensuration v1.0.1 precedent), 'coordinate', 'ordered-pair', and 'table-completion', but NOT 'transformation'. The front matter's claim that 'transformation' is the ONE new additive enum value, and that point/shape images reuse existing types, is accurate against the live schema.
3. Domain/strand: I placed the family under the EXISTING 'geometry' domain (segment GEO) with a NEW strand 'coordinate-transformations', consistent with the owner brief ('Geometry -> Coordinate transformations') and the objective-ID pattern SPI.MIDDLE.GEO.TRANS.<MICRO>.01. Note this differs from mensuration, which introduced a NEW domain (MEAS). Sections 1-2 should keep using the existing geometry domain and only add the new strand (a free-form string in curriculum-objective.schema.json — no schema change needed), and attach SPI.MIDDLE.GEO.COORD.* as prerequisites.
4. Schema-compilation path: I cited 'scripts/compile-schemas.mjs -> core/schema/compiled/' per CLAUDE.md. I did not independently verify that exact script filename exists in-repo (the mensuration precedent text references it). Sections 7 should confirm the precise compile script path before final wording.
5. Parity-fixture size: CLAUDE.md specifies parity '>=300' and the mensuration precedent shipped 304/300-entry task-pinned fixtures. With NINE tasks (vs mensuration's eight), the task-pinned fixture should be sized so every one of the nine FREE-RESPONSE tasks is represented; I wrote '>= 300' in the status banner — §15/§16 should pin the exact count (likely > 300 to cover nine tasks evenly).
6. Apostrophe/prime convention: the brief uses the prime character (A', B', C', D') for image labels. I used the Unicode prime (U+2032) throughout the glossary/overview for the image labels. Ensure §5/§6/§11 and the table-completion row keys use the SAME prime character consistently (canonical display stays ASCII-safe where required, mirroring the mensuration 'canonical units stay ASCII ^2' decision).

## Appendix C — Authoring & verification provenance

Authored by a multi-agent workflow: 16 sections drafted in parallel against a fixed platform-conventions digest + the owner brief, reviewed by four adversarial critics (transformation-math correctness, platform-fit incl. the new transformation answer.type, rendering/object-image figure contract, completeness), then revised against the consolidated findings and synthesized. The critics raised 23 findings (5 blocker-severity, 9 missing items), applied in the revision pass. PROPOSAL ONLY — no implementation, code, fixtures, objectives, schemas, SVG assets, registry entries, or review artifacts exist until the owner approves.
