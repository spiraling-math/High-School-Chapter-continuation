# Geometry (SVG diagrams) — Generator Pilot PROPOSAL

> **STATUS UPDATE (2026-06-22): REVISED to `gen.geometry.angles-figures` v1.2.1 — OBJECTIVE DEFINITIONS APPROVED; GENERATOR PENDING FINAL APPROVE/REJECT.**
> v1.2.1 is a **visual-layout-only** revision (owner REVISE): the mathematics, SVG arc semantics, reflex
> handling, accessibility model, difficulty, worked solutions, misconceptions, validation architecture, and the
> free-response-only VO scope are accepted UNCHANGED. It adds **adaptive small-sector label placement** (labels
> sit inside their sector when they fit, else become a callout in clear space joined by a neutral leader) and
> **nine blocking visual-clearance checks** on the complete label bounding boxes (min clearance 8px). v1.2.0
> (per-angle arc radii + a11y-text guard) and v1.1.0 (reflex/VO/a11y) are preserved as superseded tags. The
> remainder of this banner documents the earlier revision history.
> History: the owner first issued APPROVE-WITH-REQUIRED-REVISIONS (`DECISION_LOG.md` #32) and the family was
> implemented as v1.0.0 with all 12 revisions, split into the **five** `SPI.MIDDLE.GEO.*.01` micro-objectives.
> On review (`DECISION_LOG.md` #34) the owner **curriculum-approved the five objective definitions** but required
> generator corrections (reflex-arc rendering, a neutral vertically-opposite target, and equivalent-not-easier
> accessibility) plus a visual edge-case audit. These were applied as **v1.1.0** (v1.0.0 preserved, tag
> `geometry-v1.0.0-superseded`): the arc renderer is reflex-correct (large-arc-flag = 1 iff measure > 180,
> sweep-flag = 0), nine new SEMANTIC validators parse the SVG arcs against the FigureModel, and the review pack +
> `docs/review/geometry_visual_audit.html` were regenerated. **The objective definitions are curriculum-approved;
> the generator, its SVG rendering contract, and the golden exemplars become approved only on the owner's final
> review of the v1.1.0 pack + visual audit.** The "PROPOSAL / NOT implemented" wording below is the historical
> pre-implementation record; where it differs from the applied revisions, `DECISION_LOG.md` #32 + #34 and the
> review pack govern.

**Status: PROPOSAL — awaiting owner approval. NOT implemented.** Prepared at the owner's request as the
next architecture-proving pilot (a geometry generator using mathematically generated SVG diagrams). It was
produced by an orchestrated design pass (parallel section designers + an adversarial feasibility review +
synthesis), grounded in the uploaded SPI-Math Middle School chapters. **Do not implement until the owner
approves this specification.** Two adversarial-review findings reshaped the scope (see the review note in the
document): integer-degree ray directions are irrational (Niven's theorem) so the drawing uses a committed
fixed-point direction table with an honest bounded tolerance while the angle *measures* stay exact integers;
and the existing answer core is scalar-only, so coordinate-answer (F4) and surd/trig (F5) families are deferred
to their own later proposals. **v1.0.0 scope = F1/F2/F3 integer-degree angle reasoning only.**

---

# Geometry (SVG diagrams) — Generator Proposal v1.0.0

Generator id (canonical, single value across the whole proposal): **`gen.geometry.angles-figures`**
Target version: **1.0.0** · Status: **DRAFT — awaiting curriculum-authority approval**
Scope after adversarial review: **v1.0.0 = families F1, F2, F3 only** (integer-degree angle reasoning). Families F4 (coordinate grid) and F5 (right-triangle measurement) are **removed from v1.0.0** and each becomes its own later proposal; they are described here only as deferred follow-ons.

Conforms to the established SPI-Math SDK (`describe/generate/solve/validate/serialize`), oracle-first Python (`fractions.Fraction`) + byte-for-byte TypeScript mirror, mulberry32 PRNG, canonical JSON (`sort_keys=True, separators=(",", ":")`, `ensure_ascii=False`), precompiled-Ajv boundary validation, and the existing `question-item.schema.json` `mediaAsset`/`accessibility`/`difficulty`/`lifecycle` contracts. Nothing here redesigns those. This is the platform's first *diagram-bearing* generator: **the diagram is the question and the unknown is derived from the same params, never authored independently.**

> **Review note (why the scope shrank).** The adversarial review established two facts that reshaped this proposal and are reflected throughout:
> 1. **Niven's theorem.** A ray drawn at an integer number of degrees has an *irrational* direction except at θ ∈ {0, 30, 45, 60, 90, …} special cases (and even 45°/135° give irrational coordinates). The earlier "exact rational ray direction → exact rational intersection → round once" mechanism is therefore mathematically impossible for the common case (40°, 65°, 75°, …). Section 3 replaces it with a **committed integer fixed-point direction table** and an honest, bounded angular tolerance. The angle *measures* are exact integers; the *coordinates that draw them* are quantized approximations — and we own that distinction explicitly.
> 2. **The answer core is scalar-only.** The mirrored `oracle/spi_oracle/geometric.py` `_answer_obj` emits **only** scalar `integer`/`exact-rational` `{num,den}`; it has no `coordinate`, `exact-surd`, `exact-trig`, `decimal`+`tolerance`, or `units` path, and the schema forbids `tolerance` on exact types. F4 needs a new coordinate checker; F5 needs surd/trig/decimal machinery and transcendental evaluation. Neither rides the integer-angle core, so both leave v1.0.0.

---

## 0. Curriculum placement and objectives

### 0.1 Placement (confirmed)

| Field | Value |
| --- | --- |
| `stage` | `middle-school` |
| `programme` | SPI-Math Middle School |
| `domain` | `geometry` |
| `strand` | `angles-lines-triangles-quadrilaterals` |
| Chapter | **Ch.21 — Angles, Lines, Triangles & Quadrilaterals** (Geometry strand) |
| External alignment (reference only) | IGCSE 0580 C4.x; Singapore Lower Secondary Geometry |

**Why Ch.21 is the v1.0.0 core.** Every derived unknown in the included families is an **integer** by construction: `x = 180 − Σ` (F1), `C = 180 − A − B` and base `= (180 − apex)/2` with even apex (F2), opposite `= θ` / remaining `= 360 − Σ` (F3). Integer *answers* keep the answer pipeline on the proven scalar `{num,den}` core. The diagram coordinates are a separate matter handled in Section 3. Ch.21 is the friendliest ground on which to prove the diagram pipeline — realisability, drawn-to-(approximate-)scale layout, byte-for-byte SVG parity — before any irrational-length or coordinate-answer family is admitted.

### 0.2 House identifier scheme

`curriculum-objective.schema.json` requires `objectiveId` to match `^SPI\.[A-Z0-9]+(\.[A-Z0-9_]+)+\.[0-9]{2}$` — the first segment after `SPI.` must be `[A-Z0-9]+` (no underscore). We use the brief's scheme:

```
SPI.MIDDLE.GEO.<MICRO>.01
```

`MIDDLE` = stage token, `GEO` = domain token, `<MICRO>` = one `[A-Z0-9_]+` micro-skill token, `.01` = two-digit ordinal. All three v1.0.0 IDs validate against the pattern.

### 0.3 Micro-objectives (v1.0.0 = three; two deferred)

| # | Objective ID | Family | Learner can-do statement | `answerType` | v1.0.0 |
| --- | --- | --- | --- | --- | --- |
| O1 | `SPI.MIDDLE.GEO.ANGLES_STRAIGHT_LINE.01` | F1 | Find an unknown angle on a straight line, given the other angles, using the fact that angles on a straight line sum to 180°. | `integer` | **Ship** |
| O2 | `SPI.MIDDLE.GEO.TRIANGLE_ANGLE_SUM.01` | F2 | Find an unknown interior angle of a triangle (including the base angles of an isosceles triangle) using the interior-angle-sum of 180°. | `integer` | **Ship** |
| O3 | `SPI.MIDDLE.GEO.ANGLES_AT_POINT.01` | F3 | Find an unknown angle formed by lines meeting at a point, using vertically-opposite angles and the angles-at-a-point sum of 360°. | `integer` | **Ship** |
| O4 | `SPI.MIDDLE.GEO.COORD_GRID_BASICS.01` | F4 | Find slope, midpoint, or length of a segment between two lattice points. | `exact-rational`,`coordinate`,`integer` | **Deferred → own proposal** |
| O5 | `SPI.MIDDLE.GEO.RIGHT_TRIANGLE_MEASURE.01` | F5 | Find an unknown side of a right-angled triangle via Pythagoras or a basic trig ratio. | `integer`,`exact-surd`/`decimal` | **Deferred → Ch.23/Ch.24** |

On approval the **three** v1.0.0 records move `reviewStatus: proposed → approved` and are written to `curriculum/objectives/`. O4 and O5 remain `proposed` against their own future proposals.

### 0.4 Prerequisites (planned placeholders permitted)

| Objective | Prerequisites |
| --- | --- |
| O1 `ANGLES_STRAIGHT_LINE.01` | `SPI.MIDDLE.GEO.ANGLE_MEASURE_NOTATION.01` *(planned)*; `SPI.MIDDLE.ALG.LINEAR_EQUATION_ONE_STEP.01` *(planned)* |
| O2 `TRIANGLE_ANGLE_SUM.01` | O1; `SPI.MIDDLE.GEO.TRIANGLE_CLASSIFY.01` *(planned)* |
| O3 `ANGLES_AT_POINT.01` | O1 |

Placeholders marked **(planned)** become real records when their own generators land; this does not block v1.0.0.

### 0.5 Task → objective mapping (single source of truth, mirrored byte-identically)

| `task` param | Family | Primary objective | `interactionType` |
| --- | --- | --- | --- |
| `straight_line_missing_angle` | F1 | O1 | `free-response` / `multiple-choice` |
| `triangle_missing_angle` | F2 | O2 | `free-response` / `multiple-choice` |
| `isosceles_base_angle` | F2 | O2 | `free-response` / `multiple-choice` |
| `vertically_opposite_angle` | F3 | O3 | `free-response` / `multiple-choice` |
| `angles_at_point_missing` | F3 | O3 | `free-response` / `multiple-choice` |

### 0.6 Inclusions / exclusions

**Included (v1.0.0):** F1, F2, F3 — pure integer-degree angle reasoning, single answer type (`integer` with `units:"degrees"`), single new subsystem (the SVG serializer). These are the must-ship scope.

**Removed from v1.0.0 (own future proposals):**

| Deferred family / area | Target | Why it leaves v1.0.0 |
| --- | --- | --- |
| **F4 Coordinate grid** | Ch.18 / own proposal | Needs a **new `coordinate`/`ordered-pair` answer encoding and checker** (component-wise rational equality, significant order) absent from the scalar core. Clean exact-integer geometry, genuinely low-risk *once it has its checker*. |
| **F5 Right-triangle measurement** | Ch.23 (Pythagoras), Ch.24 (trig) | Needs `exact-surd`/`exact-trig` encodings + an `equivalentForms` generator + surd checker, **or** a `decimal`+`tolerance` policy (which the schema forbids for exact types and which clashes with the exact-arithmetic ethos); trig requires transcendental `tan θ` evaluation, re-introducing cross-language float disagreement. ~60% of the engineering surface; not a gate to flip. |
| Quadrilateral 360°, parallel-line angles | v1.1.0, still Ch.21 | Larger figure-realisability surface; sequence after F1–F3 gate green. |

**Constant across F1–F3 (non-negotiable):** integer/exact answers; oracle-first byte-for-byte Python↔TS parity on golden + 300-entry parity fixtures (the SVG string is inside the compared canonical JSON); mulberry32 determinism; canonical JSON; ≥10,000-seed stability sweep at 0-invalid + reproducible; Ajv validation at every storage/import/export boundary; axe-core ZERO critical/serious; offline single-file build (no network/CDN); items begin at `lifecycle.state = machine-validated` and are **never** auto-approved or auto-published; misconception-backed MC distractors recomputed independently to guarantee 3 distinct distractors.

---

## 1. Question families

Each family specifies **prompt shape**, **diagram** (the `media[]` SVG asset), **unknown** (the single derived quantity), and **answer** (`type`, `canonical`, `display`, `accepts`). Every figure is computed from the same params so the drawing realises the stated givens; realisability (including label-collision, Section 4) is checked **before** render. The byte-identical parity mechanism is specified once in Section 3 and applies to all three families.

### F1 — Angles on a straight line → O1 `ANGLES_STRAIGHT_LINE.01`

- **Params:** `task = "straight_line_missing_angle"`; a ray fan above a straight line at point `O`; choose `n−1` positive integer angles with `Σ < 175`, each `≥ 10°` (raised from 5° so adjacent arc labels cannot collide — see §4); unknown `x = 180 − Σ` (`≥ 5`, integer). `n ∈ {2,3}`.
- **Prompt:** *"The diagram shows angles on a straight line. Find the value of `x`, in degrees."* Givens also stated in text as a fallback.
- **Diagram:** horizontal baseline through `O`; `n` rays above it at the chosen integer degrees (laid out by the committed direction table, §3); each known region arc-labelled with its value, the unknown region labelled `x` only.
- **Unknown:** `x = 180 − Σ` (derived).
- **Answer:**
  ```json
  { "type": "integer", "canonical": { "num": 75, "den": 1 }, "display": "75",
    "units": "degrees", "accepts": { "fraction": true, "decimal": true, "mixed": false } }
  ```
- **MC distractors:** `MISC.GEOM.LINE.USES_360` (`360 − Σ`), `MISC.GEOM.LINE.BELOW_LINE` (`180 + Σ`), `MISC.GEOM.LINE.FORGOT_ONE` (omits the largest given). Three distinct values guaranteed by deterministic regeneration.

### F2 — Triangle angle sum / isosceles base → O2 `TRIANGLE_ANGLE_SUM.01`

- **Params:** two sub-tasks.
  - `triangle_missing_angle`: integers `A, B` with `A + B < 175` (each `≥ 10`); `C = 180 − A − B`.
  - `isosceles_base_angle`: **even** apex `P` with `20 ≤ P ≤ 160` (single range — see §4.6; the spike cases `P=4` and `P→176` are excluded for legibility); base `= (180 − P)/2` (integer).
- **Prompt:** *"The diagram shows triangle ABC. Find the size of angle BCA, in degrees."* / isosceles: *"Triangle ABC is isosceles with AB = AC. The apex angle is 40°. Find a base angle."*
- **Diagram:** triangle laid out from the committed direction table; known angles arc-labelled; unknown marked `x`; isosceles equal sides carry matching **tick marks**. `toScale: false` with an honest bounded angular tolerance (§3.6, §4.2) — the figure is faithful to roughly protractor precision, not exactly to the integer degree.
- **Unknown:** `C` or base `= (180 − P)/2`.
- **Answer:** `{ "type": "integer", "canonical": { "num": 70, "den": 1 }, "display": "70", "units": "degrees" }`.
- **MC distractors:** `MISC.GEOM.TRI.USES_360` (`360 − A − B`), `MISC.GEOM.TRI.APEX_EQUALS_BASE` (returns apex as base), `MISC.GEOM.TRI.HALVES_WRONG_ANGLE` / `MISC.GEOM.TRI.SUM_THEN_NO_SUBTRACT`.

### F3 — Vertically opposite / angles at a point → O3 `ANGLES_AT_POINT.01`

- **Params:** two sub-tasks.
  - `vertically_opposite_angle`: two lines crossing at `O`; one region given `θ` (`10 ≤ θ ≤ 170`); unknown is its vertically-opposite angle (`= θ`) or an adjacent angle (`= 180 − θ`), set by `targetRegion`.
  - `angles_at_point_missing`: `k` rays (full turn), `k−1` integer angles with `Σ < 355` (each `≥ 10`); unknown `x = 360 − Σ`.
- **Prompt:** *"Two straight lines intersect at O. One angle is 110°. Find the value of `x`."* / *"The angles around point O are shown. Find `x`, in degrees."*
- **Diagram:** lines/rays through `O`; given angle(s) arc-labelled; unknown labelled `x`. **The asked region's arc style is distinct from BOTH its neighbours** (single-arc vs double-arc assignment rule, §1-note below) so the picture is unambiguous.
- **Unknown:** `θ`, `180 − θ`, or `360 − Σ` (derived).
- **Answer:** `{ "type": "integer", "canonical": { "num": 110, "den": 1 }, "display": "110", "units": "degrees" }`.
- **MC distractors:** `MISC.GEOM.POINT.ADJACENT_EQUAL` (`180 − θ` when answer is `θ`, or vice-versa), `MISC.GEOM.POINT.MISLABEL_OPPOSITE`, `MISC.GEOM.POINT.USES_180`.

> **Arc-assignment rule (F3, enforced by `svg-realises-data`).** Vertically-opposite partners share an arc style; the two regions adjacent to the asked region must use a *different* style from the asked region. With a 4-region crossing this gives: asked + its opposite = single arc; the two adjacents = double arc. A solver reading only the diagram can therefore identify which region is `x` and which is its partner. The validator asserts the asked region's style differs from both neighbours.

**Family summary (v1.0.0):**

| Family | Objective | Tasks | Answer type | Status |
| --- | --- | --- | --- | --- |
| F1 Straight-line angles | O1 | 1 | `integer` (degrees) | Ship |
| F2 Triangle / isosceles | O2 | 2 | `integer` (degrees) | Ship |
| F3 Opposite / point angles | O3 | 2 | `integer` (degrees) | Ship |

---

## 2. Coordinate & constraint model

### 2.1 One source of truth, three exact layers

Every item is computed once from `params` and flows through layers that read the **same** values:

1. **Model layer** — `params` (small integers), validated against `parameterSpec`.
2. **Geometry layer** — a deterministic `FigureModel`: integer canvas coordinates produced from `params` via the committed integer direction table (§3). `FigureModel` is **not persisted**; it is recomputed on demand from `params`.
3. **Presentation layer** — the SVG, the prompt givens, and `answer.canonical` are all functions of `params`. The integer degree printed on the diagram and the integer in `answer.canonical`/`display` come from the **same** `_disp` call on the **same** `Fraction`.

> **Invariant ST-1 (single source of truth):** no value is ever typed twice. The diagram, the prompt givens, and the answer are all functions of one `params`. This is the structural guard against diagram-to-data inconsistency. Note ST-1 governs the *measures* (exact integers); the *coordinates* are a separate, quantized rendering of those measures (§3).

### 2.2 Parameter model

```jsonc
{
  "family": "F1" | "F2" | "F3",
  "task":   "straight_line_missing_angle"
          | "triangle_missing_angle" | "isosceles_base_angle"
          | "vertically_opposite_angle" | "angles_at_point_missing",

  // F1
  "angles": [a1, a2, ...],     // n-1 integer angles, each >= 10, sum < 175

  // F2
  "A": 50, "B": 60,            // scalene: integer, A+B < 175  => C derived
  "apex": 40,                  // isosceles: even, 20..160     => base derived
  "kind": "scalene" | "isosceles",

  // F3
  "rotations": [r1, ...],      // integer turn angles of rays from one point
  "targetRegion": "opposite" | "adjacent" | "remaining"
}
```

`{generatorId, generatorVersion, seed, params}` reproduces the item — and therefore the SVG — exactly.

### 2.3 Closure / derivation (the unknown is computed, never authored)

| Family | Closure | Derived unknown |
| --- | --- | --- |
| F1 | `Σ = 180` | `x = 180 − Σ(angles)` — integer ≥ 5 |
| F2 scalene | `A + B + C = 180` | `C = 180 − A − B` — integer ≥ 5 |
| F2 isosceles | `apex + 2·base = 180` | `base = (180 − apex)/2` — integer (apex even) |
| F3 opposite | rotation by 180° | opposite `= θ`; adjacent `= 180 − θ`; remaining `= 360 − Σ` |

`solve(params)` evaluates these with `Fraction`; `validate()` re-derives them by an independent route and compares.

### 2.4 Backward construction

To guarantee a clean unique answer and a realisable figure, construct backwards (mirroring the geometric-sequences "construct-backwards, exact" strategy): for F1 draw the unknown `x ∈ [5,170]` first, partition `180 − x` into `n−1` integer parts each `≥ 10` (seeded rejection sampling); for F2 scalene draw `A,B`, derive `C`; for F2 isosceles draw even `apex ∈ [20,160]`, derive integer base; for F3 draw the rotations, derive the target. The stored `answer.canonical` is correct **by construction**; `validate()` re-derives it as a guard.

### 2.5 Realisability & uniqueness guards (before render)

Checked in `generate()` with deterministic regeneration on failure, re-asserted in `validate()`:

| Guard | Applies | Rejects when |
| --- | --- | --- |
| `angle-positive` | F1–F3 | any authored/derived angle `< 5°` |
| `angle-min-label` | F1–F3 | any *authored* angle `< 10°` (arc-label legibility) |
| `straight-line-sum` | F1 | `Σ ≥ 180` |
| `triangle-angle-sum` | F2 | `A+B ≥ 175` or any angle `≤ 0`; isosceles apex not even or outside `[20,160]` |
| `non-collinear` | F2 | three vertices collinear |
| `at-point-sum` | F3 | `Σ rotations ≥ 360`, coincident rays, or a mislabelled/degenerate pair |
| `arc-style-distinct` | F3 | asked region's arc style equals either neighbour's (ambiguous picture) |
| `labels-non-overlapping` | F1–F3 | any two label bounding boxes intersect (exact integer-box test, §4) |
| `unique-answer` | all | the figure admits more than one value for the asked unknown |
| `within-canvas` | all | any vertex/label box falls outside the plotting box |
| `within-caps` | all | any value exceeds `MAX_NUM/MAX_DEN` |

Uniqueness is structural: each closure equation has exactly one solution for the single unknown; `validate()` re-checks by closed reconstruction.

### 2.6 How exact arithmetic keeps answer and picture in agreement

- **Identical formatting for label and answer.** The integer printed on the diagram and the integer in `answer.canonical` are produced by the **same** `_disp(value: Fraction)` call. There is no second numeric path.
- **No float ever touches an answer.** All closure arithmetic is `Fraction`. The only fixed-point values anywhere are *coordinates* inside the SVG, produced by the committed direction table + one rounding rule (§3); they are cosmetic and never read back to derive the answer.
- **Drawn to bounded scale.** Coordinates are produced from the chosen degrees via the committed table, so the picture is faithful within the table's known angular bound (§3.6). All angle figures are emitted `toScale: false` and carry the structural indicators (arcs/ticks); the *labels* state the exact integer degrees regardless of pixel precision.

---

## 3. SVG rendering contract (incl. the byte-identical-parity mechanism)

### 3.1 Pipeline and the `mediaAsset`

```
params (SSoT) ──▶ FigureModel (integers on a fixed canvas) ──▶ canonicalSvg(FigureModel) ──▶ media[].svg
        │                                                                                       │
        └─────────────────── identical in Python oracle and TS production ──────────────────────┘
```

For each diagram the generator appends one `mediaAsset` to `item.media`:

| Field | Value | Source |
| --- | --- | --- |
| `id` | `"fig-1"`, … (stable ordinal) | generator |
| `kind` | `"svg"` | constant |
| `svg` | `canonicalSvg(FigureModel)` | serializer |
| `toScale` | **`false` for all v1.0.0 angle figures** (coordinates are quantized; faithful only within a stated angular bound). A visible "NOT TO SCALE" banner is emitted. | policy |
| `altText` | one-line summary | `describeFigure(FigureModel).short` |
| `longDescription` | every given + the unknown (answerable without the figure) | `describeFigure(FigureModel).long` |
| `dataTableFallback` | the angles-and-relationships table (§8.3) | `describeFigure(FigureModel).table` |

### 3.2 Canvas and `viewBox` (one canonical size)

- **Single fixed canvas.** `viewBox="0 0 1000 1000"` — a constant string, never computed, never per-item. (The earlier `240` figure is deleted; there is exactly one canvas size in this proposal.)
- **Y convention.** `FigureModel` works in math coordinates (y up); the serializer applies the fixed integer flip `y_svg = 1000 − y_math` once, on integers.
- **No `width`/`height`** on the root `<svg>`; physical size is supplied by the print stylesheet (§9). Root declares only `viewBox`, `xmlns`, `role="img"`, `aria-labelledby`, `preserveAspectRatio="xMidYMid meet"`.
- **Margin.** Fixed integer inset of `80` units → usable plotting box `[80,920]²`.

### 3.3 Element vocabulary (fixed, small, total)

`baseline`, `ray`, `segment`, `vertex` (`<circle r="4">`), `polygon`, `angle arc` (`<path>`, `geo-arc` / `geo-arc-double` to distinguish pairs **without colour**), `tick mark` (1/2/3 hatches), `right-angle square` (unused in v1.0.0 angle families but reserved), `label` (`geo-label`/`geo-measure`/`geo-unknown`), `not-to-scale banner` (`geo-nts`). Fixed z-order: shapes/baseline → rays/sides → arcs/ticks → vertices → labels → banner. Document order is the only SVG z-ordering and is part of the contract.

### 3.4 The byte-identical parity mechanism (the hard problem, solved honestly)

The requirement: `canonicalSvg(FigureModel)` returns the **identical byte string** in Python and TypeScript, validated on golden + 300-entry parity fixtures and the ≥10,000-seed sweep. The mechanism rests on **not computing any transcendental at runtime in either language**.

**Rule 1 — A committed integer direction table; no runtime `sin`/`cos`.**
Because a ray at an integer number of degrees has an irrational direction (Niven's theorem — verified: cos 40° = 0.766044…, cos 65° = 0.422618…, cos 75° = 0.258819… are all irrational), we do **not** attempt an exact rational direction. Instead a single data file
```
DIR[θ] = { "dx": <int>, "dy": <int> }   for θ = 0 .. 359
```
holds pre-rounded direction vectors on a large fixed radius `R = 10000`. The rounding from the true irrational `(R·cos θ, R·sin θ)` to the integer pair is performed **once, offline, by a generator script, and committed as data**. Both Python and TS **read the identical committed table**; neither evaluates a transcendental at item-generation time. A ray endpoint is `O + DIR[θ]` scaled into the plotting box by the integer affine transform of Rule 3, then quantized by the single rounding rule of Rule 2. *Every "exact rational ray direction / exact intersection / round once" sentence from earlier drafts is deleted and replaced by this table.*

**Rule 2 — One rounding rule, integer-only, proven on signed inputs.**
The single quantization is `gridRound(num, den) -> int`, **round-half-up on the exact rational, correct for negatives**, implemented with explicit integer arithmetic in both languages (never a language `round()`, never `//` on a signed operand without the tested helper):
```
gridRound(num, den):   # den > 0
    # round half up toward +infinity on the true rational num/den
    q, r = divmod(num, den)        # Python floor-div semantics, tested mirror in TS
    return q + 1 if 2*r >= den else q
```
The TS mirror implements the same `divmod`-with-floor semantics on `bigint` and is proven equal to Python on a signed-input fixture spanning negatives, exact halves, and zero. **There is exactly one rounding mode in the entire system** — the earlier §11 "round-half-even" reference is removed; the whole pipeline is round-half-up.

**Rule 3 — One integer affine transform, one integer formatter.**
Layout maps `FigureModel` into `[80,920]²` by an **integer** affine map `(x,y) → (OX + SX·x, OY − SY·y)` with integer `OX,OY,SX,SY` chosen from a small committed lookup keyed by the figure's integer bounding box — never a floating fit-to-view. Numbers are emitted only via `fmtInt(n)` (base-10, no `+`, no leading zeros except `"0"`, `-` only for negatives). **No `fmtDecimal` is used in v1.0.0**: there are no half-integer coordinates because all rendered coordinates are integers post-`gridRound`, and all labels are integer degrees. (A decimal formatter is therefore *not* part of v1.0.0; it is specified only when F4/F5 land, with fixed places, half-up, leading zero, `-0→0`, and a proof that the answer `display` uses the same call.)

**Rule 4 — A hand-rolled canonical serializer (no DOM/XML library).**
Fixed element order; fixed attribute order per element (declared in a constant table, e.g. `<line>` emits `class,x1,y1,x2,y2`); all values double-quoted; exactly one `U+0020` between attributes; elements joined by a single `"\n"`; no indentation; void elements emit `<line .../>` with one space before `/>`. A single shared `escapeXml` maps `& < > " '` to the five canonical entities and nothing else; labels are restricted at generation time to a safe set (letters, digits, `°`, parentheses, comma, space, `=`, `−` U+2212). Encoding UTF-8, non-ASCII literal (matching the canonical-JSON `ensure_ascii=False` convention). DOM libraries are banned because they differ in attribute ordering/whitespace/self-closing style between languages.

**Rule 5 — Hashed and parity-checked like everything else.**
`canonicalSvg` output is the `media[].svg` string inside the item's canonical JSON, so it folds into `contentHash`. CI asserts `oracle.canonicalSvg(fm) == ts.canonicalSvg(fm)` byte-for-byte across golden + 300-entry fixtures, and the ≥10,000-seed sweep asserts every figure is byte-identical and stable across runs. One differing byte fails CI.

**Worked micro-example (F1).** `params = {family:"F1", angles:[40,75]}` → unknown `= 180 − 40 − 75 = 65`. Baseline endpoints at integer points `(80,500)`–`(920,500)`; rays at 40° and 75° placed from `DIR[40]`, `DIR[75]` (committed integers), endpoints `gridRound`-quantized. The serializer emits, among others:
```
<line class="geo-baseline" x1="80" y1="500" x2="920" y2="500"/>
```
Every numeric token is an integer from `fmtInt`; there is no path by which the two languages emit different bytes.

### 3.5 Why this is honest about scale

Because `DIR[θ]` is pre-rounded, the *drawn* angle differs from θ by a small bounded error (≤ the angular error of an integer direction at radius 10000, which is well under 0.1°). This is invisible to a reader but is **not exactly** the labelled degree. Therefore **all angle figures are `toScale:false`** with a visible banner, and the to-scale-honesty check (§4.6) uses the bound below — we never claim a protractor on the printed page reads the exact integer degree.

### 3.6 Angular tolerance (defined, not hand-waved)

The to-scale-honesty check compares the angle recovered from the integer ray directions (`atan2` of the committed `DIR` integers, computed only inside the *validator*, never the generator/serializer) against the labelled integer degree and requires agreement within **`±0.5°`** (a protractor reads to ~1°; half a degree is a strict, pedagogically justified bound). The committed `DIR` table is built to satisfy this bound for every θ; a table entry violating it fails a one-time table-construction test. The bound is documented in `describe()` and the review pack.

---

## 4. Diagram-to-data consistency validation

The validator treats `media[].svg`, the prompt text, and `answer.canonical` as three independent encodings of one `params` and proves agreement by **re-deriving each and parsing the SVG back**. Each sub-check is a named entry in `lifecycle.validation.checks[]` with `result: pass|fail|warn`. Any `fail` ⇒ `validation.status = fail`; the item never reaches `machine-validated` and never enters the offline export.

### 4.1 `svg-bytes-reproducible` (regenerate-and-compare)
Re-run `canonicalSvg(buildFigureModel(params))` and assert byte-equality with stored `media[].svg`, in both oracle and production builds (this is also the per-item cross-language parity gate). If the stored SVG is exactly the deterministic output for `params`, it cannot encode anything else.

### 4.2 `svg-realises-data` / `svg-structure-decodes-givens` (parse-back, no rendering)
A small dependency-free parser (a tokenizer over the fixed vocabulary/classes — not general XML) reconstructs a `ParsedFigure` and asserts, per family:
- **F1/F3:** the multiset of `geo-measure` angle labels equals the params givens; exactly one `geo-unknown` label, carrying **no numeric measure**; for F3, the asked region's arc style differs from both neighbours (the §1 arc-assignment rule).
- **F2:** the given interior/base angles appear as measures; isosceles equality is shown by matching tick multiplicities on the two equal sides.
- **Recompute from parsed geometry:** invert the integer affine transform, recover ray directions, recompute the unknown, and assert it equals `answer.canonical`. (For angle families this recovers *quantized* directions, so the recomputed angle is compared within the §3.6 ±0.5° bound; the *label* equality is exact.)

### 4.3 `label-equals-answer-formatter` (no rounding drift)
The unknown is recomputed from `params` in exact arithmetic and formatted once with `_disp`; the validator asserts (a) this string is **not** present as a `geo-measure` on the unknown element (the unknown stays unlabelled), and (b) every given shown in the figure is byte-identical to the same given formatted by `_disp`, which also matches the prompt text. Since v1.0.0 has no decimal labels, there is a single formatter; the earlier "two formatters" ambiguity does not arise.

### 4.4 `derived-unknown-matches-oracle`
Independently `solve(params)` and the oracle reference, asserting both equal `answer.canonical` (`{num,den}`). Combined with §4.2 (the figure encodes the givens) and §4.3 (no drift), this closes the loop givens → derived unknown → stored answer as one chain from one `params`.

### 4.5 `realisability-exact`
Re-run every guard in §2.5 on `params` in exact arithmetic, including the two review-mandated additions:
- **`labels-non-overlapping`** — exact integer bounding-box intersection test on every label anchor box (arc labels, vertex labels, the unknown label). With `n=3` rays and the raised `≥10°` minimum plus radius-`40` arc placement, no two arc labels collide; any residual collision rejects/reseeds. Checkable without rendering because label boxes are integer-positioned.
- (The `non-degenerate-rise-run-triangle` check the review asked for belonged to F4 distance, which is out of v1.0.0; it is recorded against the future F4 proposal.)

### 4.6 `to-scale-honest`
All v1.0.0 angle figures set `toScale:false`; the validator asserts the `geo-nts` banner is present whenever `toScale:false`. Where the parser recovers a drawn angle, it must match the labelled integer degree within the **±0.5°** bound of §3.6 — we do **not** assert exact equality, because grid quantization makes exact impossible. Mismatch beyond the bound is a fail.

### 4.7 `accessibility-text-complete`
Assert `accessibility.longDescription` / `mediaAsset.{altText,longDescription}` were produced by `describeFigure(FigureModel)` (regenerate and compare byte-for-byte), enumerate **every given and name the unknown**, and that `accessibility.nonColorIndicators === true` with at least one non-colour indicator per family (tick marks for equal sides; distinct arc styles for opposite pairs). Feeds the axe-core gate (§8.5).

### 4.8 Result surface
```json
"validation": {
  "status": "pass",
  "validatorVersion": "geo-1.0.0",
  "checks": [
    {"name": "svg-bytes-reproducible", "result": "pass"},
    {"name": "svg-realises-data", "result": "pass"},
    {"name": "label-equals-answer-formatter", "result": "pass"},
    {"name": "derived-unknown-matches-oracle", "result": "pass"},
    {"name": "realisability-exact", "result": "pass"},
    {"name": "labels-non-overlapping", "result": "pass"},
    {"name": "to-scale-honest", "result": "pass"},
    {"name": "accessibility-text-complete", "result": "pass"}
  ]
}
```

---

## 5. Answer types

### 5.1 The canonical answer model (reused verbatim — and it genuinely is, for v1.0.0)

Every v1.0.0 answer is a **single scalar `Fraction`** built by the existing `_answer_obj`/`_disp`/`_terminates` machinery in `oracle/spi_oracle/geometric.py`:
```python
def _answer_obj(value: Fraction) -> Dict[str, Any]:
    num, den = value.numerator, value.denominator
    return {"type": "integer" if den == 1 else "exact-rational",
            "canonical": {"num": num, "den": den},
            "display": _disp(value),
            "accepts": {"fraction": True, "decimal": _terminates(den), "mixed": False}}
```
Because every F1–F3 answer is an **integer number of degrees**, `_answer_obj` produces `type:"integer"`, `canonical:{num,den:1}`, and the existing rational checker governs equivalence. **No new answer encoding is introduced in v1.0.0** — and unlike the earlier draft, this is now a true statement, because the families that *did* need new encodings (F4 `coordinate`; F5 `exact-surd`/`exact-trig`/`decimal`) have been removed. The one addition is a `units:"degrees"` field on the answer object (the schema permits it; the checker treats the unit as advisory and strips a trailing `°` from learner input).

| Family / task | `answer.type` | `canonical` | `display` |
| --- | --- | --- | --- |
| F1 missing angle; F2 third/base angle; F3 opposite/adjacent/remaining | `integer` | `{num, den:1}` | `"75"` (with `units:"degrees"`) |

### 5.2 Accepted forms
```jsonc
"accepts": { "fraction": true, "decimal": true, "mixed": false }
```
For integer-degree answers: `"75"`, `"75.0"`, `"75/1"`, and `"75°"` (unit stripped) are all accepted; `decimal:true` because an integer terminates. The exact-rational checker (`core/answer-checking/rational-checker.ts`) is unchanged.

### 5.3 Free-response vs multiple-choice
| | Free-response | Multiple-choice |
| --- | --- | --- |
| `interactionType` | `"free-response"` | `"multiple-choice"` |
| Offered for | every v1.0.0 task | every v1.0.0 task (each has ≥3 formula-backed distractors) |
| Checking | exact checker + `accepts` | exactly one correct option; post-shuffle `options` stored for reproducibility |

MC options are assembled by the shared `assembleMultipleChoice` SDK helper: correct + 3 distinct distractors, deterministically shuffled with the item's `mulberry32`, labelled A–D, with `value`/`display`/`misconceptionId` preserved byte-for-byte. The encode callback is the existing scalar rational encoder, so no MC maths lives in the helper. (`interactionType` is independent of `answer.type`, exactly as corrected in geometric v1.1.0.)

---

## 6. Misconceptions

### 6.1 Registry pattern (identical to the geometric family)
Each misconception is a registry entry in `geometry_misconceptions.py` with a byte-for-byte TS mirror, keyed `MISC.GEOM.<SUB>.<NAME>` (validates against `misconception.schema.json`; existing entries use `MISC.GEO.<NAME>` and the draft's longer form also validates). Each carries `formula(params) -> Fraction` (the exact wrong value), `expression` (symbolic), `observableError` (serialized into the distractor `rationale`; must match TS byte-for-byte), and `feedback` (placeholder-free, student-facing, complete sentences with no embedded numbers). Distractors are **recomputed independently from the named formula** in `validate()`, never copied from generation; the stored `rationale` must equal the registry `observableError`.

### 6.2 Named rules per family

**F1 — straight line** (correct `x = 180 − Σ`)

| ID | Wrong-value formula | Feedback |
| --- | --- | --- |
| `MISC.GEOM.LINE.USES_360` | `360 − Σ` | Angles on a straight line add up to 180°, not 360°. Subtract the given angles from 180. |
| `MISC.GEOM.LINE.BELOW_LINE` | `180 + Σ` | You only need the angles above the straight line; together they make 180°. |
| `MISC.GEOM.LINE.FORGOT_ONE` | `180 − (Σ − a_max)` | Subtract **every** marked angle from 180°, not just some of them. |

**F2 — triangle / isosceles** (correct scalene `C = 180 − A − B`; base `(180 − apex)/2`)

| ID | Wrong-value formula | Feedback |
| --- | --- | --- |
| `MISC.GEOM.TRI.USES_360` | `360 − A − B` | The three angles of a triangle add up to 180°, not 360°. |
| `MISC.GEOM.TRI.APEX_EQUALS_BASE` | returns `apex` | The two equal angles are the base angles, not the apex. Use base = (180 − apex) ÷ 2. |
| `MISC.GEOM.TRI.HALVES_WRONG_ANGLE` | `(180 − base)/2` | Subtract the apex from 180°, then halve — the apex is the odd one out. |
| `MISC.GEOM.TRI.SUM_THEN_NO_SUBTRACT` | `A + B` | A + B is what you subtract from 180° to find the third angle; it is not the answer itself. |

**F3 — opposite / point** (correct opposite `= θ`, adjacent `= 180 − θ`, remaining `= 360 − Σ`)

| ID | Wrong-value formula | Feedback |
| --- | --- | --- |
| `MISC.GEOM.POINT.ADJACENT_EQUAL` | `180 − θ` when answer is `θ` (and vice-versa) | Vertically opposite angles are equal; the angle next to θ is its supplement (180° − θ). |
| `MISC.GEOM.POINT.MISLABEL_OPPOSITE` | the adjacent rotation value | Opposite angles sit straight across the intersection — follow the line through. |
| `MISC.GEOM.POINT.USES_180` | `180 − Σ(others)` | Angles all the way around a point add up to 360°, not 180°. |

### 6.3 Three-distinct-distractor policy + deterministic regeneration
Reuses the geometric generator's exact mechanism (verified in `geometric.py`: `seen`-set, `MAX_PARAM_ATTEMPTS=256`):
1. `rules_for(task)` returns an **ordered** candidate list (deterministic).
2. Each candidate's `formula(params)` is evaluated with `Fraction`.
3. A `seen` set seeded with the **correct** answer admits a candidate only if within caps and not already in `seen` (no distractor equals the answer or another distractor).
4. Collect until exactly 3; if fewer survive, `generate_distractors` returns `None`.
5. On `None`, `_acceptable` returns `None` and `generate()` advances the **same seeded mulberry32 stream** to the next `params` (bounded). Deterministic and cross-language identical.
6. `validate()` re-verifies independently: `distractors-distinct-misconceptions`, `min-three-distractors`, `distractor-value-matches-rule` (recompute from registry `formula`), `distractor-rationale-matches` (byte-for-byte vs `observableError`), `distractor-feedback-present`, `exactly-one-correct`, `distractors-unique` — all verbatim from `geometric.py`.

---

## 7. Difficulty dimensions

Difficulty is multidimensional and structural, populated into `difficulty.axes` (0..1) with `overallBand` derived by the shared `band_from_score` (never hand-set). Magnitude alone is explicitly not the driver.

### 7.1 Per-family structural floor

| Family / task | Floor band | Why (structural) |
| --- | --- | --- |
| F1 line, 2 given | 1 | one unknown, one step |
| F1 ≥3 given / below-line region | 2 | more givens; region discrimination |
| F2 angle sum, 2 given | 1–2 | one step (180 − A − B) |
| F2 isosceles base | 2 | two-step (equality, then (180 − apex)/2); parity constraint |
| F3 vertically opposite (single pair) | 1 | recognition, one step |
| F3 angles at a point / mixed adjacent+opposite | 2–3 | multi-relationship, multi-step |

### 7.2 Axes populated (pure functions of params, `round3`-normalised)
- **`reasoningSteps`** — derivation depth (1 ≈ 0.15, 2 ≈ 0.4, 3 ≈ 0.6).
- **`numericalComplexity`** — *awkwardness*, not size: non-multiple-of-5 angles raise it; magnitude contributes only a small capped term (a `40-65-75` split and a `40-65-75` scaled split share a floor).
- **`representation`** — labelled-element count, distinct relationships, region-discrimination load (F1 below-line, F3 adjacent-vs-opposite) — the diagram-reading load.
- **`abstraction`** — recognition demand (vertically-opposite / base-angle > direct angle-sum).
- **`requiredConnections`** — `> 0` when two facts chain (F3 mixed: angles-at-a-point *then* vertically-opposite).

`overallBand = band_from_score(Σ w_k·axis_k)` with family-tuned weights. The validator asserts `difficulty-respects-structural-floor` (`overallBand ≥ structuralFloor(family, task)`), so a trivially-numbered isosceles item can never be mislabelled band 1.

### 7.3 Determinism
All axes are exact rational/`round3` outputs; Python `round3` and TS `band.ts` are the byte-for-byte rounding already proven for the algebra generators. `exactVsApproximate` is not used in v1.0.0 (all answers are exact integers).

---

## 8. Accessibility descriptions

The diagram is the question, so the item **must be fully answerable from text alone**. Every accessibility artifact is derived from the *same `FigureModel`* as the SVG and answer — never authored, never transcribed off the rendered figure.

### 8.1 Single source of truth
`params → figureModel →` four parallel pure emitters: `emitSvg`, `emitAltText`, `emitLongDescription`, `emitDataTable`. A label in the SVG cannot disagree with the alt text or the answer.

### 8.2 SVG `<title>`/`<desc>`
First two children, fixed order, `role="img"` + `aria-labelledby="fig-title fig-desc"`. `<title>` = figure class (e.g. *"Angles on a straight line at point O"*, *"Triangle ABC, not to scale"*, *"Two lines crossing at point P"*). `<desc>` = the structured givens + unknown, identical string to `altText`.

### 8.3 Structured alt text (givens + unknown, answerable without the figure)
Deterministic per-family template; givens first, unknown last, each angle/point spoken. Examples:
- **F1:** *"A straight line through point O. On one side, three angles meet at O: angle AOB = 40°, angle BOC = 75°, and angle COD = x. The three angles lie on a straight line. Find x."*
- **F2 (isosceles):** *"Triangle ABC. AB = AC (shown by tick marks on AB and AC). The angle at A is 50°. Angles ABC and ACB are equal, each marked x. Find x."*
- **F3:** *"Lines GH and JK cross at point P. Angle GPJ = 110°. Angle HPK is vertically opposite to angle GPJ and is marked y. Find y."*

`accessibility.spokenMath` carries the same sentence with symbols spoken (`x`, `°` → "degrees"). (No coordinate/surd spoken forms are needed — those belonged to F4/F5.)

### 8.4 Data-table fallback (`media[].dataTableFallback`)
Accessible `<table>` with `<caption>` and row/column headers; for F1–F3, rows = labelled angles, columns = `{label, vertex, raysFromTo, measureDeg | "unknown", relationship}` where `relationship` names the rule slot (*"on straight line with …"*, *"vertically opposite to …"*, *"base angle, equal to …"*). The unknown is a blank cell labelled with its symbol — never the answer.

### 8.5 Non-colour indicators (`accessibility.nonColorIndicators = true`)
All answer-relevant distinctions are structural, not hue, and survive greyscale/print: equal sides → tick marks (1/2/3 strokes); equal/opposite angle pairs → matching arc style (single vs double arc) **plus** arc labels; the unknown → solid arc/segment + symbol. Stroke is a single ink colour resolving to `#000` in print. The validator asserts `nonColorIndicators === true` only when the emitter used no fill-colour-only encoding (it can, because indicators are emitter-chosen, not heuristically detected).

### 8.6 No-leakage rule (review fix)
The no-leakage check targets the **unknown's label slot**, not any occurrence of a numeral: it asserts the `geo-unknown` element carries a symbol, not a value, and the alt text names the unknown without stating its value. The `vertically_opposite` case where **answer = a given** (`x = θ = 110`) is explicitly whitelisted — the numeral "110" legitimately appears as the given even though it equals the answer, and that is correct, not leakage.

### 8.7 axe-core gate
Items render into the offline review/preview harness; **axe-core runs dev/test only** (bundled, no network). The gate over the SVG + surrounding DOM must return **zero `critical` and zero `serious`** violations: `svg-img-alt` (title/desc + `role="img"`), `image-alt`, `aria-*` integrity, `color-contrast` of **text labels** (≥ 4.5:1; see §9.1 for why the contrast claim is scoped to text), and table semantics for the fallback. `moderate`/`minor` findings are recorded as `warn` and do not advance lifecycle backward. A failing a11y gate ⇒ `validation.status = fail`.

---

## 9. Print requirements

The same `media[].svg` bytes that render on screen must print correctly on a monochrome laser printer, embedded in worksheets/exam papers, with no loss of information. Print-first; screen styling is additive.

### 9.1 Greyscale / no colour dependence (review fix applied)
- **All semantic distinctions are conveyed by shape, never colour**, and `nonColorIndicators` must be `true` (checked §4.7): equal sides → tick-mark multiplicity; opposite pairs → single vs double arc; the unknown → the `x`/`?` label.
- **The SVG carries no inline `fill`/`stroke` colour**; every primitive uses a CSS class. A single print stylesheet (in the offline build, no CDN) defines all classes in **fully-opaque black** on transparent.
- **Major vs minor distinctions use stroke-dash or stroke-width, NOT opacity** (review fix): the earlier `opacity:0.25/0.5` gridline scheme is removed because (a) opacity is a luminance-only encoding that `nonColorIndicators` forbids, and (b) 1-bit laser halftoning of partial opacity is printer-dependent. All ink is fully opaque; any major/minor distinction (reserved for future grid families) is by dash pattern or width. (v1.0.0 angle families have no gridlines.)
- **The `color-contrast` claim is scoped to text labels only** (review fix): all text is solid `#000` on transparent → passes ≥4.5:1. We do not claim "the figure is black-on-transparent so contrast passes trivially" as a blanket statement; the gate evaluates rendered text contrast, which is satisfied because every label is opaque black.

### 9.2 Scale and resolution
Pure vector (no `<image>` rasters). Fixed aspect via `viewBox` + `preserveAspectRatio="xMidYMid meet"` and no `width`/`height`; the print stylesheet sets physical size (e.g. `70mm`). `stroke-width` in viewBox units keeps printed strokes ≥ ~0.3 mm at the smallest sanctioned size; label font size in viewBox units stays ≥ 8 pt at 70 mm. Every figure is `toScale:false` and prints the visible `geo-nts` "NOT TO SCALE" banner — so no protractor/ruler reading is implied on the page.

### 9.3 No interactivity, no script, no animation
No `<script>`, no event handlers, no `<a>`, no CSS animation/transition, no `<foreignObject>`. Nothing depends on hover/focus/JS; everything needed to answer is statically present in ink.

### 9.4 Accessibility carried into print
`role="img"` + `<title>`/`<desc>` from `describeFigure`; the build can emit `longDescription` as a caption/answer-key footnote. The item is answerable from text alone (§4.7), making the `dataTableFallback` a complete substitute for the picture.

### 9.5 Print/parity gates
- **axe-core** dev/test gate: zero critical/serious (§8.7).
- **Greyscale legibility check (downgraded to non-blocking lint — review fix):** because 1-bit printer halftoning is printer-dependent and therefore non-deterministic, the earlier "1-bit snapshot CI gate" is **not** a blocking gate. Instead a deterministic check asserts no semantic indicator is encoded by colour/opacity (it inspects the emitter's indicator choices, not rendered pixels); a rendered greyscale preview is provided in the review pack for human inspection but does not block CI.
- Because the printed artifact is exactly the stored `media[].svg` bytes plus a static stylesheet, the §4.1 `svg-bytes-reproducible` check already guarantees the printed figure is the deterministic, parity-proven output for `{generatorId, generatorVersion, seed, params}`.

---

## 10. Independent verification strategy

Oracle-first. An item advances to `machine-validated` only when **all** gates pass; `validation.status=fail` blocks the bank and the offline export.

### 10.1 Byte-for-byte parity (Python ↔ TS)
Independent Python reference (`oracle/spi_oracle/geometry.py`, `fractions.Fraction`) and TS production mirror (`domains/geometry/angles-figures.ts`). Parity is proven on **committed golden fixtures** (golden seeds `[1, 42, 123456789, 2147483647]` per family/task) and a **300-entry parity fixture** spanning every family × task × interaction mode. For each, both implementations run `generate→serialize` and the canonical JSON strings must be `==` (sorted keys, no whitespace, `ensure_ascii=False`). **The serialized item includes `media[].svg`, so SVG parity is JSON parity.**

The SVG byte-for-byte mechanism is §3.4: committed integer `DIR` table (no runtime transcendental), one integer `gridRound` proven on signed inputs, one integer affine transform, one `fmtInt`, a hand-rolled fixed-order serializer, deterministic ids (`fig-title`, `fig-desc`, `el-<n>` from a counter; no hashes/timestamps/RNG). Identical params ⇒ identical `FigureModel` ⇒ identical token stream ⇒ identical bytes.

### 10.2 Diagram-matches-data without rendering (§4.2)
The validator parses the emitted SVG back, inverts the affine transform, recovers ray directions, recomputes each labelled angle and the unknown, and asserts equality with `answer.canonical` (angles within the §3.6 ±0.5° bound; labels exactly). For F2 it checks tick-marked sides are equal by exact squared-length comparison. The unknown's label is a symbol, not the answer.

### 10.3 Realisability checks (§2.5, pre-render + re-asserted)
Every angle `> 0`; sums exactly 180 (F1/F2) or 360 (F3 point); triangle inequality + non-collinear (F2); non-coincident rays + arc-style-distinct (F3); isosceles apex even in `[20,160]`; **`labels-non-overlapping`** (exact integer-box). Failure rejects and retries (bounded), exactly as `_acceptable` does in the algebra generators.

### 10.4 ≥10,000-seed stability sweep
`oracle/run_geometry.py` and the SDK `runStabilityGate` run seeds `1..10000` × each interaction mode through `generate→validate`, requiring **0 invalid** and **reproducible=true** (re-`serialize` equals first serialize, incl. SVG). Accumulates family/task/band coverage. Any invalid or irreproducible seed fails CI.

### 10.5 Schema + a11y + offline-export gates
Schema: every item validated against `question-item.schema.json` (Python `check_conformance.py` here; **precompiled Ajv** at the production storage/import/export boundary); `describe()` validated against `generator-module.schema.json`. a11y: axe-core zero critical/serious (§8.7). Offline export: SVG inline (no `<img src>`, no external fonts/CSS, no network/CDN); an export self-check asserts no external URLs and that re-importing each item reproduces an identical canonical serialization (round-trip parity).

### 10.6 Named validator `checks[]`
`params-in-domain`, `realisable-figure`, `labels-non-overlapping`, `geometry-recompute-agreement`, `svg-realises-data`, `svg-canonical-form`, `svg-bytes-reproducible`, `answer-type-consistency`, `answer-solution-agree`, `no-answer-leakage`, `to-scale-honest`, `difficulty-respects-structural-floor`, `nonColorIndicators-present`, `alt-text-lists-givens-and-unknown`, `data-table-fallback-present`, `a11y-axe-zero-critical-serious`, plus the reused MC checks `distractors-distinct-misconceptions`, `min-three-distractors`, `distractor-value-matches-rule`, `distractor-rationale-matches`, `exactly-one-correct`, `distractors-unique`.

---

## 11. Review-pack plan

`oracle/make_review_pack_geometry.py` → `docs/review/geometry_angles_review_pack.{json,md}`, mirroring the geometric-sequences pack (deterministic seed scan greedily maximising coverage; no item auto-approved).

### 11.1 Coverage matrix (rows selected until every flag is hit, ≥3 per cell)
- **Family × task:** F1 (2-given / 3-given / below-line) · F2 (angle-sum / isosceles) · F3 (vertically-opposite / point / mixed adjacent+opposite).
- **Interaction:** free-response **and** multiple-choice.
- **Awkwardness flags:** non-multiple-of-5 angle present; below-line region; adjacent-vs-opposite discrimination.
- **Difficulty bands:** ≥2 distinct `overallBand` per family; every structural floor demonstrated at the floor and one above.
- **Diagram flags:** every non-colour indicator exercised (tick marks, single/double arc pairing); every figure shown `toScale:false` with banner.
- **Misconception rules:** **every named rule** covered by ≥1 MC example (`USES_360` line, `BELOW_LINE`, `USES_360` triangle, `APEX_EQUALS_BASE`, `HALVES_WRONG_ANGLE`, `SUM_THEN_NO_SUBTRACT`, `ADJACENT_EQUAL`, `MISLABEL_OPPOSITE`, `USES_180`), each with seed · params → distractor value.

### 11.2 Per-item fields
`seed`, `generatorId`, `generatorVersion`, `family`, `task`, `objectiveIds`, `interactionType`, `answerType`, `canonical {num,den}` + `display`, `acceptedEquivalentForms`, `params`, `figureModel` summary, `difficultyProfile {overallBand, axes}` + asserted `structuralFloor`, `calculatorPolicy`, prompt blocks, **inline SVG** (with `toScale:false`), **altText**, **longDescription**, **dataTableFallback**, `nonColorIndicators`, `spokenMath`, worked `solution.steps`, MC `distractorCalculations` (value · misconception · formula · rationale · feedback), `validation.status` + the `checks` list, `a11yResult` (axe critical/serious = 0), and a **reproduce** block `{generatorId, generatorVersion, seed, params}`. Each record ends with `☐ approve ☐ revise ☐ reject — notes: ____`. The pack header restates that **advancing lifecycle beyond `machine-validated` is the curriculum authority's decision**.

### 11.3 Pack also emits
A **misconception coverage table** (rule → example), a **structural-floor table** (family/task → floor band, realised example at floor and above), a **diagram-fidelity appendix** (for 2–3 items, parsed-back geometry next to the stored answer — human-readable `svg-realises-data` evidence), and a **rendered greyscale preview** per family (non-blocking, for human print inspection, §9.5).

---

## 12. Versioning & approval plan

### 12.1 Generator semantic versioning
`generatorVersion` is semver. Any change to the **canonical SVG byte output** (including a regeneration of the committed `DIR` table), the params space, the answer maths, the difficulty mapping, or the accessibility text is **at minimum a minor bump**. A change that alters previously-valid serialized bytes for an existing `(seed, params)` is **breaking**; the prior version's source is **preserved unchanged in git history** (as `geometric.py` v1.0.0→1.1.0 was). Golden + 300-entry parity fixtures **and the committed `DIR` table** are versioned alongside; a deliberate change regenerates and re-commits them in the same reviewed change.

### 12.2 Reproducibility contract
Every item reproduces from `{generatorId, generatorVersion, seed, params}`; `schemaVersion` pins the item schema. Bumping the generator never silently rewrites banked items: re-running an old `(version, seed)` reproduces its bytes (old source retained); new output lands as a **new** item that `supersedes` the old via `lifecycle.supersedes`/`supersededBy`.

### 12.3 Machine-validated lifecycle
States from `question-item.schema.json` (`draft → generated → machine-validated → mathematics-reviewed → curriculum-reviewed → approved → published → revised → retired`):
- **generated** — emitted by `generate()`; no gates asserted yet.
- **machine-validated** — **all** §10 gates pass (validation `pass`, axe zero critical/serious, schema-conformant, in the 0-invalid stability sweep). This is the **only automatic transition** and the **ceiling**: items are never auto-approved or auto-published.
- **mathematics-reviewed → curriculum-reviewed → approved → published** — human transitions only, each appended to `lifecycle.reviewHistory` (`at/by/fromState/toState/note`); the §11 review pack feeds them.
- **revised** — any human edit forces re-entry at `generated` and full re-validation; the edit creates a superseding item rather than mutating an approved one.
- **retired** — terminal; `supersededBy` points to the replacement.

A `validation.status=fail` at any point blocks advancement, demotes to a non-banked state, and excludes the item from the offline export. `validatorVersion` and `validation.checkedAt` are stamped for auditability.

---

## Approval asks

Discrete decisions the owner must make to unblock implementation:

1. **Placement.** Approve / amend / reject **Ch.21 Middle-School Geometry** as the v1.0.0 core.
2. **Scope cut.** Approve shipping **F1+F2+F3 only** in v1.0.0, with **F4 moved to its own coordinate-geometry proposal** and **F5 to its own Pythagoras (Ch.23) / trig (Ch.24) proposals** — explicitly endorsing the review's finding that F4/F5 require new answer encodings/checkers and do not ride the integer-angle core. (Reject this only if you want F4/F5 in v1.0.0, which requires funding the coordinate and surd/trig/decimal-tolerance subsystems first.)
3. **Objective IDs & wording.** Approve the **three** IDs `SPI.MIDDLE.GEO.ANGLES_STRAIGHT_LINE.01`, `…TRIANGLE_ANGLE_SUM.01`, `…ANGLES_AT_POINT.01` and their can-do statements (move `proposed → approved`).
4. **Planned-prerequisite placeholders.** Approve the `(planned)` prerequisite IDs (notation, one-step linear equation, triangle classification) as graph placeholders.
5. **Parity mechanism.** Approve the **committed integer `DIR` direction table + single round-half-up `gridRound`** as the byte-identical-parity mechanism, accepting that it makes the earlier "exact rational ray direction" approach obsolete and that **all angle figures are `toScale:false`**.
6. **Angular tolerance.** Approve the **±0.5°** to-scale-honesty bound (or specify a different one) for the `to-scale-honest` check.
7. **Isosceles apex range.** Approve the single range **apex even, `20 ≤ apex ≤ 160`** (resolving the earlier 4 vs 20 vs 176 inconsistency).
8. **Minimum authored angle.** Approve raising the per-angle minimum from 5° to **10°** for label legibility (the `labels-non-overlapping` + `angle-min-label` guards).
9. **Generator id.** Confirm the single canonical id **`gen.geometry.angles-figures`** (used in the reproducibility tuple).
10. **Print/greyscale gate.** Approve **downgrading the 1-bit greyscale snapshot to a non-blocking lint** (printer-dependent halftoning is non-deterministic) while keeping the deterministic "no colour/opacity-only encoding" check blocking.
11. **MC scope.** Confirm multiple-choice is offered for **all three families** in v1.0.0 (each has ≥3 formula-backed distractors).

On approval of 1–5, the three objective records are written, the oracle (`geometry.py`) + committed `DIR` table are built and proven (≥10,000-seed 0-invalid sweep, golden + 300-entry parity fixtures), then the TS mirror is brought to byte-for-byte parity, and the first review pack is generated for mathematics/curriculum review.
