# Generator Specification — gen.proportion.ratio v1.0.0 (Ratio and Proportion: ratio, unitary method, direct + inverse proportion, simple scale)

> **STATUS: CURRICULUM-APPROVED at v1.0.2 (owner final decision, 2026-06-26 — DECISION_LOG #61; tag `approved-ratio-v1.0.2`).** Objectives: `approved`; generator + validator v1.0.2: `approved` (selectable in normal Studio + included in production samples); the additive `answer.type 'ratio'` schema extension and the shared ratio-answer infrastructure are APPROVED (canonical-first: the ordered simplest-form positive-integer tuple IS answer.canonical; display derived; order-sensitive equivalence). v1.0.0/v1.0.1 preserved (historical, unapproved). The lifecycle narrative below (oracle-first → pending-review → review-pack decision → APPROVE; v1.0.0 implementation + adversarial hardening → v1.0.1 nine REVISE corrections → v1.0.2 simple_scale grammar + manifest-tag cleanup → approval) records the build process that led to this approval. This family proves the **fourth** structured, canonical-first answer contract on the platform — `answer.type = "ratio"`: an ordered tuple of positive integers in simplest form whose machine-checkable value *is* `answer.canonical`, with `display` derived from it and never stored twice (extending the precedents set by `"quantity"` and `"transformation"`). It establishes ratio **equivalence** checking with **ordered parts** (`2:3 = 4:6` but `2:3 ≠ 3:2`), **multi-part table-completion** answers for sharing where correspondence is by label, a clean **non-Cartesian bar-model / double-number-line** visual system, and **exact proportional reasoning** over integers and exact rationals only (no floats, no tolerance). Placement is **SPI-Math Middle School → Proportion/Ratio** (ratio, unitary method, direct proportion, inverse proportion, simple scale).

| Field | Value |
|---|---|
| Generator id | `gen.proportion.ratio` |
| Version | `1.0.0` |
| Domain / strand / stage segment / objective segment | `proportion` (domain) → `ratio-and-proportion` (strand) → `MIDDLE` (stage segment) → `RATIO` (objective segment) |
| Objective ID pattern | `SPI.MIDDLE.RATIO.<MICRO>.01` |
| Interaction | Free-response-first; multiple-choice only where 3 distinct misconception-backed distractors exist |
| New answer type | `answer.type = "ratio"` (additive, backward-compatible, **APPROVED**) |
| Canonical answer model | Canonical-first: `answer.canonical` is the structured value; `answer.display` derived |
| Exact math | Integers + exact `Rational` only (no floats, no tolerance, no irrationals) |
| Visual system | Non-Cartesian `ratio-theme` (bar models, double number lines, proportional tables) |
| Misconception registry | `MISC.RATIO.*` (single source of truth) |
| Lifecycle | Objectives `approved`; generator + validator v1.0.2 `approved` (selectable in normal Studio + production); tag `approved-ratio-v1.0.2`; DECISION_LOG #61. Newly generated items begin `machine-validated`; no auto-approval/publication |

### Table of contents

| # | Section |
|---|---|
| 1 | Curriculum placement and objective IDs |
| 2 | Objective wording and prerequisites |
| 3 | Task and interaction matrix |
| 4 | Ratio answer schema |
| 5 | Ratio parser, formatter, canonicalizer, and checker |
| 6 | Exact proportional reasoning model |
| 7 | Sharing and table-completion model |
| 8 | Bar-model / double-number-line renderer contract |
| 9 | Solver and independent-validator design |
| 10 | Misconception and diagnostic registry |
| 11 | Difficulty model |
| 12 | Edge-case and degeneracy policy |
| 13 | Accessibility model |
| 14 | Review-pack and visual-audit plan |
| 15 | Schema, versioning, and lifecycle plan |
| 16 | Reusable infrastructure versus family-specific code |

## 1. Curriculum placement and objective IDs

### 1.1 Domain, strand, and segment

`gen.proportion.ratio` introduces a single new **Proportion/Ratio** strand to SPI-Math Middle School. Both `domain` and `strand` are free-form `type: string` fields in `schemas/curriculum-objective.schema.json` (the schema constrains only `objectiveId`, `answerTypes`, `reviewStatus`, and `version`), so adding them requires **no schema change**; they follow the lower-case-hyphenated convention already used by `number` / `signed-numbers`, `measurement` / `mensuration`, and `statistics` / `data-handling-and-probability`.

| Field | Value (verbatim, every objective in this family) |
| --- | --- |
| `academy` | `SPI-Math` |
| `programme` | `SPI-Math Middle School` |
| `stage` | `middle-school` |
| `course` | `SPI-Math Middle School Mathematics` |
| `domain` | `proportion` |
| `strand` | `ratio-and-proportion` |

**Domain-segment decision.** The owner brief's default ID pattern is `SPI.MIDDLE.RATIO.<MICRO>.01`. I **adopt it unchanged** — there is no graph reason to introduce a different segment. The objective-ID segment after the stage is **`RATIO`** (this is the `<DOMAIN>` slot of the platform pattern `SPI.<STAGE>.<DOMAIN>.<TOPIC?>.<MICRO>.<NN>`; here the family is shallow enough that the domain segment `RATIO` is followed directly by a single `<MICRO>` segment, exactly as the brief specifies). I deliberately do **not** use `PROP` or `PROPORTION` as the ID segment even though the `domain` *field value* is `proportion`: the brief fixes one ID spelling, `SPI.MIDDLE.RATIO.<MICRO>.01`, and using a second token in the IDs would create the competing-spelling drift the platform forbids. The human-readable `domain`/`strand` field values (`proportion` / `ratio-and-proportion`) and the ID segment (`RATIO`) are intentionally distinct registers — the field values name the curriculum area, the ID segment is the stable, terse key — and **each has exactly one spelling**, asserted by the §1.3 string-scan test.

This keeps Proportion/Ratio deliberately distinct from the existing `number`, `algebra`, `measurement`, and `geometry` domains: it is exact-arithmetic ratio and proportional reasoning, not fraction arithmetic (which lives in `number`), not linear-equation solving (`algebra`), not gradient (the coordinate-lines family owns gradient-as-ratio), and not similar-figure geometry (`geometry`). Every deferred topic — percentages as a full family; compound/continued proportion proofs; currency conversion and exchange rates; recipe scaling with units; compound units beyond a simple unit rate; similar-triangles geometry scale factors; gradient-as-ratio; gear/lever ratios; irrational ratios; non-exact decimal-ratio terms; trigonometric ratios; probability odds; algebraic ratio proofs — is **out of scope for v1.0.0** and is deterministically excluded by generator construction (see §3.4, §12, and the owner brief's DEFER list, with named exclusion tests). They are recorded only as potential future strands/objectives, never silently produced.

### 1.2 ID convention and the twelve micro-objectives

IDs obey the platform pattern and the schema regex `^SPI\.[A-Z0-9]+(\.[A-Z0-9_]+)+\.[0-9]{2}$`. The stage segment is `MIDDLE`, the domain segment is `RATIO`, and there is **one micro-objective per owner task** — exactly **twelve objectives, all suffixed `.01`** (the first revision; future revisions bump `.NN`). IDs are **stable** and are never reused for a different task. There is exactly **one** `<MICRO>` spelling per task; no section, fixture, oracle map, registry, or coverage cell uses any alternative. **No objective ID carries a `_UNITARY` suffix** — the direct/inverse tasks are `DIRECT_PROPORTION.01` / `INVERSE_PROPORTION.01`, never `DIRECT_PROPORTION_UNITARY.01` / `INVERSE_PROPORTION_UNITARY.01`; any such suffixed spelling is superseded and must not appear anywhere in the family.

| # | Owner task (v1.0.0 scope) | Objective ID |
| --- | --- | --- |
| T1 | Simplify a ratio to simplest form | `SPI.MIDDLE.RATIO.SIMPLIFY.01` |
| T2 | Write a ratio from two or three given quantities | `SPI.MIDDLE.RATIO.WRITE_FROM_QUANTITIES.01` |
| T3 | Convert a ratio to a fraction of the whole | `SPI.MIDDLE.RATIO.RATIO_TO_FRACTION.01` |
| T4 | Convert a fraction of a whole to a ratio | `SPI.MIDDLE.RATIO.FRACTION_TO_RATIO.01` |
| T5 | Share a quantity in a two-part ratio | `SPI.MIDDLE.RATIO.SHARE_TWO_PART.01` |
| T6 | Share a quantity in a three-part ratio | `SPI.MIDDLE.RATIO.SHARE_THREE_PART.01` |
| T7 | Find a missing part when one part and the ratio are known | `SPI.MIDDLE.RATIO.MISSING_PART.01` |
| T8 | Direct proportion by the unitary method | `SPI.MIDDLE.RATIO.DIRECT_PROPORTION.01` |
| T9 | Inverse proportion by the unitary method (simple integer cases) | `SPI.MIDDLE.RATIO.INVERSE_PROPORTION.01` |
| T10 | Find a unit rate | `SPI.MIDDLE.RATIO.UNIT_RATE.01` |
| T11 | Compare simple best-buy / rate situations (no currency conversion) | `SPI.MIDDLE.RATIO.BEST_BUY.01` |
| T12 | Use a simple scale factor or map/model scale | `SPI.MIDDLE.RATIO.SIMPLE_SCALE.01` |

### 1.3 Single-source task slugs and `OBJECTIVE_BY_TASK` map

Mirroring `core/curriculum/stats-objective-ids.ts` and `core/curriculum/mensuration-objective-ids.ts` exactly, the family ships **one** authoritative task-slug set and task→objective map, `core/curriculum/ratio-objective-ids.ts`, re-used **verbatim** by the Python oracle (`oracle/spi_oracle/ratio.py: OBJECTIVE_BY_TASK`), every spec section (§3, §5, §6, §7, §8, §9, §10, §11, §12, §14, §15, §16), every descriptor, the validator, the fixtures, the review-pack records, the misconception `RULES_BY_TASK` (§10), the COVERAGE-MATRIX `cell:<task>:…` tokens (§14), the §15 scope list, and the SDK registry entry. **There is exactly one spelling of each of the twelve task slugs; no section uses any alternative spelling.**

The intended shape (no implementation — field names and constants only):

- `RATIO_TASKS = [ "simplify", "write_from_quantities", "ratio_to_fraction", "fraction_to_ratio", "share_two_part", "share_three_part", "missing_part", "direct_proportion", "inverse_proportion", "unit_rate", "best_buy", "simple_scale" ]` — **the single canonical slug set; these exact twelve strings are the keys used everywhere in every section.** Any other spelling is superseded and must not appear anywhere in the family, specifically including: `simplify_ratio`, `write_ratio`, `write_ratio_from_quantities`, `ratio_fraction`, `share2`, `share3`, `missing`, `direct`, `direct_proportion_unitary`, `inverse`, `inverse_proportion_unitary`, `unitrate`, `bestbuy`, `scale`. **The four slugs most prone to drift are pinned as: `simplify` (not `simplify_ratio`), `write_from_quantities` (not `write_ratio` / `write_ratio_from_quantities`), `direct_proportion` (not `direct_proportion_unitary`), `inverse_proportion` (not `inverse_proportion_unitary`).**
- `OBJECTIVE_BY_TASK: Record<RatioTask, string>` keyed by those twelve task slugs to the twelve IDs in §1.2 (so `OBJECTIVE_BY_TASK["direct_proportion"] === "SPI.MIDDLE.RATIO.DIRECT_PROPORTION.01"` and `OBJECTIVE_BY_TASK["inverse_proportion"] === "SPI.MIDDLE.RATIO.INVERSE_PROPORTION.01"`).
- `RATIO_OBJECTIVE_IDS = RATIO_TASKS.map(t => OBJECTIVE_BY_TASK[t])`.
- `MC_ELIGIBLE_TASKS: RatioTask[] = [ "simplify", "ratio_to_fraction", "fraction_to_ratio", "direct_proportion", "inverse_proportion", "best_buy" ]` — the six tasks for which three distinct misconception-backed distractors exist (§3.1); all other tasks are free-response only. Free-response is the default for every task even where MC is supported (FR-first).

The objective records live in a single file `curriculum/objectives/SPI.MIDDLE.RATIO.json` (one file per domain, matching `SPI.MIDDLE.STAT.json` and `SPI.MIDDLE.MEAS.json`). A bespoke graph test (`core/curriculum/ratio-graph.test.ts`, modelled on `stats-graph.test.ts`) asserts: (a) all twelve IDs exist in `curriculum/objectives/SPI.MIDDLE.RATIO.json`; (b) the TS map and the Python map agree; (c) `OBJECTIVE_BY_TASK`, `RULES_BY_TASK`, the generator dispatch, the `MC_ELIGIBLE_TASKS` set, and the COVERAGE-MATRIX cell tokens share an **identical task-key set** equal to `RATIO_TASKS` (cardinality twelve, no default branch); (d) no alternative slug spelling (the superseded list above) and no alternative `MISC.RATIO.*` id spelling appears anywhere in the family (a string-scan assertion over both namespaces, catching id/slug drift before merge); (e) no objective ID matches `_UNITARY` (a string-scan guard against the suffixed direct/inverse IDs).

`reviewStatus` follows the **two-stage gated lifecycle** consistent with the schema enum and the stats/mensuration precedent:

1. **`proposed`** — before the curriculum authority signs off the objective definitions.
2. **`approved-for-implementation`** — once the definitions are curriculum-approved and the generator build is cleared to proceed *while the generator itself remains gated*; this is the status the objective files carry **throughout the gated build**.
3. **`approved`** — flipped only on owner APPROVE of the review pack.

In parallel, the SDK generator registers `approvalStatus: pending-review` (gated from normal Studio + production, visible only in review mode) until owner approval (see §15). `core/curriculum/graph-check.ts` enforces the DAG over the combined objective set (duplicate-id and cycle = errors; unresolved prerequisites = warnings).

---

## 2. Objective wording and prerequisites

Each objective below gives the verbatim learner-can-do `objectiveWording`, the `prerequisites[]` (citing **only objective IDs verified present and `approved` in `curriculum/objectives/`** — see the verification note), the MATHEMATICAL-only `answerTypes[]`, the `allowedRepresentations`, and a provisional `difficultyRange` (PROVISIONAL until the §11 10k distribution proves every band reachable; where §11's `ratio-difficulty.json` is the machine-readable source of truth, the band shown here is the projection of that single source and must match it exactly — the §11 source wins on any conflict).

`allowedRepresentations` is `["diagram", "numeric"]` for the visual sharing/proportion tasks (the §8 bar-model / double-number-line figure drives a `diagram`; the value answer is `numeric`), with `symbolic` added where a ratio or fraction form is the answer object (T1–T4; `simple_scale` T12 is a scaled **numerical value**, not a ratio, so it carries no `symbolic` — decision D/I). **`verbal-context` is included only on the tasks the generator actually frames in words** (T8–T11 carry a light real-world rate/sharing context); it is omitted from the pure-symbolic conversion tasks (T1–T4), so the objective's allowed-representation set and the generator's emitted representations match exactly. **The `verbal-context`-bearing tasks (T8–T11) are exactly the tasks that lift §11's `readingDemand` off zero** — `readingDemand > 0` iff the drawn item carries a worded context, so the "allowed-representations == emitted-representations" claim is testable against the §11 difficulty source.

### 2.0 Answer-type vocabulary used in this family

The family uses exactly **four** `answer.type` tokens, all of which are (or, for `ratio`, will become) live members of the `answerType` enum at `schemas/question-item.schema.json` (the curriculum-objective schema `$ref`s that same enum for `answerTypes`, so every token here must be a live enum member):

- **`ratio`** — the THIRD structured canonical answer (the family's headline contract; ordered positive-integer tuple in simplest form; §4). This is an **additive, backward-compatible** enum extension exactly like `quantity` (mensuration) and `transformation` (transformations); it is **APPROVED** (owner, 2026-06-26) and is the §15 schema delta now cleared to implement. The objective records sit at `approved-for-implementation`, and the generator registers `pending-review` (gated) until the implemented review-pack decision. **`ratio` is the ONLY new enum member this family adds** (the at-most-one-new-answer-type constraint is met).
- **`integer`** — already a live, approved enum member (used by `SPI.MIDDLE.NUM.SIGNED_OPERATIONS.01`); exact whole-number shares, missing parts, and integer unit rates.
- **`exact-rational`** — already a live, approved enum member; exact reduced `Rational{num,den}` unit rates, scale factors, missing parts where the share is non-integer, and fraction-of-whole values. **No approximate decimal answers in v1.0.0.**
- **`table-completion`** — **verified live** in the `answerType` enum (`schemas/question-item.schema.json` line 203); a multi-cell labelled answer for three-part (and labelled two-part) sharing, with correspondence by **label**, not row order. Reused unchanged; the enum member carries no `if/then` constraint, so the sharing answers need **no schema delta**. (Cluster B/§4 owns the canonical cell shape `{cells:[{location,value}]}`; §2/§3 reference it by name only.)

**Best-buy uses no new answer type.** Best-buy (T11) is realised on the **live `multiple-choice` answer type** (`schemas/question-item.schema.json` line 202) — the answer is intrinsically a labelled choice over the compared options. The exact unit-rate witnesses that justify the choice live in the worked solution and feedback, not in a new canonical shape. **There is NO `comparison` answer type**: it is not a live enum member and is not part of the §15 delta; it must not appear anywhere in the family. This keeps `ratio` the only new enum member.

### Prerequisites cited — verification note (re-run against the actual `objectiveId` set)

Only IDs that exist as a defined `objectiveId` with `reviewStatus: approved` are cited as prerequisites. Verified by reading `curriculum/objectives/`:

- `SPI.MIDDLE.NUM.SIGNED_OPERATIONS.01` — **verified present and `approved`** in `curriculum/objectives/SPI.MIDDLE.NUM.json`. Covers calculation with positive/negative integers **and simple rational numbers** using all four operations; this is the multiplication/division and exact-rational arithmetic backbone for every task (unitary method, sharing, unit rate, scale). Its own `successCriteria` already cover bracketed/ordered signed arithmetic.
- `SPI.MIDDLE.ALG.INVERSE_OPERATIONS.01` — **verified present and `approved`** in `curriculum/objectives/SPI.MIDDLE.ALG.FOUNDATIONS.json`. Inverse (undo) reasoning for the unitary method (divide-to-one, multiply-up) and for recovering a missing part.
- `SPI.MIDDLE.ALG.LINEQ.ONESTEP_MUL.01` — **verified present and `approved`** in `curriculum/objectives/SPI.MIDDLE.ALG.LINEQ.json`. Solve a one-step multiplicative relation `part = k × ratioUnit` for the unknown factor (missing part, scaling up an equivalent ratio).

**Correction (guards against the standard wrong-prereq trap).** There is **no defined fractions objective and no defined gcd objective** in `curriculum/objectives/`. `SPI.MIDDLE.NUM.INTEGERS_NUMBER_LINE.01` and `SPI.MIDDLE.NUM.ORDER_OF_OPERATIONS.01` appear **only** inside `prerequisites[]`/`relatedObjectives[]` arrays, never as an `objectiveId`. Therefore **no ratio objective cites a "fractions", "gcd", or "rational-number" prerequisite ID**, because none exists as a resolvable `objectiveId`; citing one would create an unresolved-prerequisite warning and a false "verified present" claim. The fraction/gcd/rational *skills* the brief lists are **covered by the verified-defined `SPI.MIDDLE.NUM.SIGNED_OPERATIONS.01`** (which explicitly includes simple rational numbers and the four operations) and are recorded in each objective's `relatedObjectives[]`/`vocabulary[]` rather than as a fabricated prerequisite. When a genuine fractions/gcd objective is added to the `number` domain in a future revision, these prerequisite arrays will be revised to cite it; until then the family resolves with **zero** unresolved-prerequisite warnings under `core/curriculum/graph-check.ts`.

No coordinate-lines or geometry objective is cited as a prerequisite: gradient-as-ratio and similar-figure scale are deferred (§1.1), so reading the Cartesian plane is not a learner prerequisite for any of the twelve tasks.

### 2.1 T1 — `SPI.MIDDLE.RATIO.SIMPLIFY.01`
- **Wording:** "Simplify a two-part or three-part ratio of positive integers to its simplest form by dividing every part by their greatest common divisor, and state the result as a ratio with no common factor."
- **prerequisites:** `["SPI.MIDDLE.NUM.SIGNED_OPERATIONS.01"]`
- **answerTypes:** `["ratio"]`
- **allowedRepresentations:** `["symbolic", "numeric"]`
- **difficultyRange:** `{ "min": 1, "max": 3 }`

### 2.2 T2 — `SPI.MIDDLE.RATIO.WRITE_FROM_QUANTITIES.01`
- **Wording:** "Write the ratio of two or three given like quantities in the stated order and in simplest form, as an ordered ratio of positive integers carrying no units."
- **prerequisites:** `["SPI.MIDDLE.NUM.SIGNED_OPERATIONS.01", "SPI.MIDDLE.RATIO.SIMPLIFY.01"]`
- **answerTypes:** `["ratio"]`
- **allowedRepresentations:** `["symbolic", "numeric"]`
- **difficultyRange:** `{ "min": 1, "max": 3 }`

### 2.3 T3 — `SPI.MIDDLE.RATIO.RATIO_TO_FRACTION.01`
- **Wording:** "Express a named part of a ratio as a fraction of the whole by writing that part over the sum of all parts, and state the fraction in simplest form."
- **prerequisites:** `["SPI.MIDDLE.NUM.SIGNED_OPERATIONS.01", "SPI.MIDDLE.RATIO.SIMPLIFY.01"]`
- **answerTypes:** `["exact-rational"]` (a proper fraction `part / total`, reduced)
- **allowedRepresentations:** `["symbolic", "numeric"]`
- **difficultyRange:** `{ "min": 1, "max": 3 }`

### 2.4 T4 — `SPI.MIDDLE.RATIO.FRACTION_TO_RATIO.01`
- **Wording:** "Given the fraction of a whole that one category occupies, write the ratio of that category to the remainder (or among the named categories) as an ordered ratio of positive integers in simplest form."
- **prerequisites:** `["SPI.MIDDLE.NUM.SIGNED_OPERATIONS.01", "SPI.MIDDLE.RATIO.SIMPLIFY.01"]`
- **answerTypes:** `["ratio"]`
- **allowedRepresentations:** `["symbolic", "numeric"]`
- **difficultyRange:** `{ "min": 2, "max": 3 }`

### 2.5 T5 — `SPI.MIDDLE.RATIO.SHARE_TWO_PART.01`
- **Wording:** "Share a given total quantity between two shares in a stated two-part ratio by finding the value of one ratio unit and multiplying, and state each labelled share as an exact integer that sums to the total."
- **prerequisites:** `["SPI.MIDDLE.NUM.SIGNED_OPERATIONS.01", "SPI.MIDDLE.ALG.INVERSE_OPERATIONS.01", "SPI.MIDDLE.RATIO.SIMPLIFY.01"]`
- **answerTypes:** `["table-completion"]` (decision D: two labelled cells; correspondence by label)
- **allowedRepresentations:** `["diagram", "numeric"]`
- **difficultyRange:** `{ "min": 2, "max": 4 }`

### 2.6 T6 — `SPI.MIDDLE.RATIO.SHARE_THREE_PART.01`
- **Wording:** "Share a given total quantity among three labelled shares in a stated three-part ratio by finding the value of one ratio unit and multiplying, and state each labelled share as an exact integer, with all three shares summing to the total."
- **prerequisites:** `["SPI.MIDDLE.NUM.SIGNED_OPERATIONS.01", "SPI.MIDDLE.ALG.INVERSE_OPERATIONS.01", "SPI.MIDDLE.RATIO.SHARE_TWO_PART.01"]`
- **answerTypes:** `["table-completion"]` (three labelled shares; correspondence by label)
- **allowedRepresentations:** `["diagram", "numeric"]`
- **difficultyRange:** `{ "min": 3, "max": 5 }`

### 2.7 T7 — `SPI.MIDDLE.RATIO.MISSING_PART.01`
- **Wording:** "Given one known part of a quantity shared in a stated ratio, find another labelled part by scaling the ratio to the known part, and state the missing part as an exact integer."
- **prerequisites:** `["SPI.MIDDLE.NUM.SIGNED_OPERATIONS.01", "SPI.MIDDLE.ALG.LINEQ.ONESTEP_MUL.01", "SPI.MIDDLE.RATIO.SHARE_TWO_PART.01"]`
- **answerTypes:** `["integer"]`
- **allowedRepresentations:** `["diagram", "numeric"]`
- **difficultyRange:** `{ "min": 2, "max": 4 }`

> Note (decision E — `missing_part` is INTEGER-ONLY in v1.0.0): the missing part is computed as `missingValue = parts[missingIndex] · (knownValue / parts[knownIndex])` over the simplest stored ratio. The generator enforces the **hard, non-optional** divisibility constraint `parts[knownIndex] ∣ knownValue`, so `onePart = knownValue / parts[knownIndex]` is an exact integer and `missingValue = onePart × parts[missingIndex]` is automatically an exact integer too; a candidate that is not divisible is **deterministically redrawn** (no escape hatch). The objective therefore admits **only** `integer` in v1.0.0; the §3.3 matrix row agrees; the §9.4-E `missing-part-exact` check re-asserts the divisibility post-condition. **There is no exact-rational `missing_part` answer in v1.0.0** — a rational recovered value is a future extension only.

### 2.8 T8 — `SPI.MIDDLE.RATIO.DIRECT_PROPORTION.01`
- **Wording:** "Solve a direct-proportion problem by the unitary method — find the value for one unit, then multiply for the required number of units — and state the result as an exact integer or exact rational."
- **prerequisites:** `["SPI.MIDDLE.NUM.SIGNED_OPERATIONS.01", "SPI.MIDDLE.ALG.INVERSE_OPERATIONS.01", "SPI.MIDDLE.RATIO.UNIT_RATE.01"]`
- **answerTypes:** `["integer", "exact-rational"]`
- **allowedRepresentations:** `["diagram", "numeric", "verbal-context"]`
- **difficultyRange:** `{ "min": 2, "max": 4 }`

### 2.9 T9 — `SPI.MIDDLE.RATIO.INVERSE_PROPORTION.01`
- **Wording:** "Solve a simple inverse-proportion problem by the unitary method, using the invariant that the product of the two quantities is constant, and state the result as an exact integer (simple integer cases only)."
- **prerequisites:** `["SPI.MIDDLE.NUM.SIGNED_OPERATIONS.01", "SPI.MIDDLE.ALG.INVERSE_OPERATIONS.01", "SPI.MIDDLE.RATIO.DIRECT_PROPORTION.01"]`
- **answerTypes:** `["integer"]` (constructed so the inverse-proportion result is an exact integer; non-exact cases excluded — §12)
- **allowedRepresentations:** `["diagram", "numeric", "verbal-context"]`
- **difficultyRange:** `{ "min": 3, "max": 5 }`

### 2.10 T10 — `SPI.MIDDLE.RATIO.UNIT_RATE.01`
- **Wording:** "Find a unit rate by dividing a quantity by the number of units it corresponds to, and state the rate as an exact rational (an exact integer where the rate is whole) per single unit."
- **prerequisites:** `["SPI.MIDDLE.NUM.SIGNED_OPERATIONS.01", "SPI.MIDDLE.ALG.INVERSE_OPERATIONS.01"]`
- **answerTypes:** `["exact-rational"]` (decision D: the unit-rate answer is `exact-rational`; it collapses to `integer` when the rate is whole only if the platform's normal answer-type policy requires the integer-when-whole collapse)
- **allowedRepresentations:** `["numeric", "verbal-context"]`
- **difficultyRange:** `{ "min": 1, "max": 3 }`

### 2.11 T11 — `SPI.MIDDLE.RATIO.BEST_BUY.01`
- **Wording:** "Compare two or three simple rate situations by computing each unit rate exactly and selecting the better value, and state which option is the better value (no currency conversion)."
- **prerequisites:** `["SPI.MIDDLE.NUM.SIGNED_OPERATIONS.01", "SPI.MIDDLE.RATIO.UNIT_RATE.01"]`
- **answerTypes:** `["multiple-choice"]` (a labelled choice over the compared options; the exact unit rates underpin the decision and appear in the worked solution and feedback)
- **allowedRepresentations:** `["numeric", "verbal-context"]`
- **difficultyRange:** `{ "min": 3, "max": 5 }`

> Note (best-buy realisation — decisions C/H): best-buy is **MC-only** and realised on the **live `multiple-choice` answer type** — the selected labelled option id IS `answer.canonical`; the exact per-option unit rates are recomputed by the independent validator and surfaced as witnesses in the worked solution and feedback (never as a separate canonical). The worked solution shows **each option's exact unit rate, the comparison of those exact rates, and the selected best-value option**, and validation verifies the selected option has the **strict minimum** unit rate. **`comparison` is not used anywhere in the family.** Ties (equal exact unit rates) are handled by **deterministic redraw** (decision H / §12) so the best value is always a strict minimum — never a floating-point near-tie, never an "equal value" option, never a currency conversion / exchange-rate. The `difficultyRange` shown here `{min:3,max:5}` is the projection of §11's `ratio-difficulty.json` `best_buy` band (the single source of truth); the earlier draft's `{min:2,max:4}` is superseded.

### 2.12 T12 — `SPI.MIDDLE.RATIO.SIMPLE_SCALE.01`
- **Wording:** "Use a simple scale factor or a map/model scale to convert between a scale length and a real length (or vice versa) in the correct direction, and state the scaled numerical value as an exact integer (or exact rational where not whole) — no similar-figure proof, no approximation (decision I)."
- **prerequisites:** `["SPI.MIDDLE.NUM.SIGNED_OPERATIONS.01", "SPI.MIDDLE.ALG.LINEQ.ONESTEP_MUL.01", "SPI.MIDDLE.RATIO.SIMPLIFY.01"]`
- **answerTypes:** `["integer", "exact-rational"]` (decision D/I: `simple_scale` asks for a **scaled numerical value** — `integer` when whole, else `exact-rational`; it is **not** answered as a `ratio` in v1.0.0)
- **allowedRepresentations:** `["diagram", "numeric"]`
- **difficultyRange:** `{ "min": 2, "max": 4 }`

### 2.13 Prerequisite DAG (intra-family + external edges)

All edges point from prerequisite to dependent; the graph is acyclic and is enforced by `core/curriculum/graph-check.ts`. External (existing, verified-`approved`) roots are shown at the top; every cited external root resolves (no unresolved-prerequisite warnings).

```
SPI.MIDDLE.NUM.SIGNED_OPERATIONS.01 ───────────(root of every node, directly or via an ancestor)
SPI.MIDDLE.ALG.INVERSE_OPERATIONS.01 ─────┐
SPI.MIDDLE.ALG.LINEQ.ONESTEP_MUL.01 ──────┤
                                          ▼
        T1 SIMPLIFY
          │
          ├──────────────┬───────────────┬───────────────────────────┐
          ▼              ▼               ▼                           ▼
   T2 WRITE_FROM_   T3 RATIO_TO_    T4 FRACTION_TO_           T12 SIMPLE_SCALE
      QUANTITIES       FRACTION         RATIO

        T5 SHARE_TWO_PART
          │            │
          ▼            ▼
   T6 SHARE_THREE_  T7 MISSING_PART
      PART

        T10 UNIT_RATE
          │            │
          ▼            ▼
   T8 DIRECT_      T11 BEST_BUY
      PROPORTION
          │
          ▼
   T9 INVERSE_PROPORTION
```

Edges in words: T2←T1; T3←T1; T4←T1; T12←T1; T6←T5; T7←T5; T8←T10; T11←T10; T9←T8. Each node also depends on the relevant external NUM/ALG roots as listed per objective (every node has `SPI.MIDDLE.NUM.SIGNED_OPERATIONS.01` as an ancestor; the unitary/inverse tasks T5–T9 additionally root on `SPI.MIDDLE.ALG.INVERSE_OPERATIONS.01`; the one-step-scaling tasks T7 and T12 root on `SPI.MIDDLE.ALG.LINEQ.ONESTEP_MUL.01`). The graph test asserts these exact edges and that no cycle or duplicate ID is introduced when the file is merged with the existing objective set.

---

## 3. Task and interaction matrix

### 3.1 Interaction and answer-shape decisions (FR-first; MC only where three strong distractors exist)

**Free-response is the default for every task except `best_buy`** (decision C): `supportedInteractionTypes` contains `free-response` for all eleven non-best-buy tasks, and FR is what the generator emits unless an MC interaction is explicitly requested for an MC-eligible task. **`best_buy` is MC-only** — the labelled choice IS the construct — so it carries `multiple-choice` and no `free-response`. Multiple-choice is offered **only** on the six tasks for which **three distinct, misconception-backed distractors** are pedagogically strong (`MC_ELIGIBLE_TASKS` = `simplify`, `ratio_to_fraction`, `fraction_to_ratio`, `direct_proportion`, `inverse_proportion`, `best_buy`, §1.3); the remaining six (`write_from_quantities`, `share_two_part`, `share_three_part`, `missing_part`, `unit_rate`, `simple_scale`) are **free-response only**. No distractor is a manufactured "nearby wrong number": every MC distractor is the **exact predicted student response** of a registered `MISC.RATIO.*` diagnostic (§10), computed by formula, not chosen arbitrarily.

Note on best-buy: T11's `answer.type` is `multiple-choice` (§2.0/§2.11) — the labelled choice IS the canonical answer — and it is simultaneously MC-eligible as an *interaction*. The three "distractor" choices are the wrong options a student selects under the three named best-buy misconceptions; the correct option is the genuine best value. (For the other five MC-eligible tasks the answer type is `ratio`/`exact-rational` and MC is layered on top as an alternative interaction whose distractors are the misconception-predicted values.)

**Tasks that support multiple-choice (FR-first where the answer is free-form; MC available) and the three distractor misconceptions each draws on.** Every distractor source named here is **applicable to that task in the §10 registry** (the §10 `applicability` predicates are written to include exactly these tasks — see the applicability reconciliation note below):

| Task | Why exactly three strong misconception distractors exist | The three MISC.RATIO.* distractor sources |
| --- | --- | --- |
| T1 `simplify` | Under-simplifying, reversing, and stopping at a partial common factor are all distinct, formula-predictable wrong ratios | `MISC.RATIO.DOES_NOT_SIMPLIFY_FULLY`, `MISC.RATIO.REVERSES_ORDER`, `MISC.RATIO.EQUIVALENT_BUT_UNSIMPLIFIED_WHEN_SIMPLEST_REQUIRED` |
| T3 `ratio_to_fraction` | Part-over-other-part, using one part as the whole, and a wrong total are three distinct exact wrong fractions | `MISC.RATIO.RATIO_TO_FRACTION_ONE_PART_OVER_OTHER_NOT_OVER_WHOLE`, `MISC.RATIO.TREATS_ONE_PART_AS_WHOLE`, `MISC.RATIO.WRONG_TOTAL_PARTS` |
| T4 `fraction_to_ratio` | Reversing the part-to-remainder order, a wrong total, and adding parts incorrectly give three exact wrong ratios | `MISC.RATIO.REVERSES_ORDER`, `MISC.RATIO.WRONG_TOTAL_PARTS`, `MISC.RATIO.ADDS_PARTS_INCORRECTLY` |
| T8 `direct_proportion` | Treating it as inverse, multiplying-where-divide, and dividing-where-multiply are three distinct exact wrong values | `MISC.RATIO.INVERSE_FOR_DIRECT`, `MISC.RATIO.MULTIPLIES_INSTEAD_OF_DIVIDING_IN_UNITARY`, `MISC.RATIO.DIVIDES_INSTEAD_OF_MULTIPLYING_IN_UNITARY` |
| T9 `inverse_proportion` | Treating it as direct, and the two unitary mis-steps give three distinct exact wrong values | `MISC.RATIO.DIRECT_FOR_INVERSE`, `MISC.RATIO.MULTIPLIES_INSTEAD_OF_DIVIDING_IN_UNITARY`, `MISC.RATIO.DIVIDES_INSTEAD_OF_MULTIPLYING_IN_UNITARY` |
| T11 `best_buy` | Comparing totals without unit-rate, choosing lowest price not best value, and a wrong-direction rate give three exact wrong choices | `MISC.RATIO.COMPARES_PRICES_WITHOUT_UNIT_RATE`, `MISC.RATIO.CHOOSES_LOWEST_PRICE_NOT_BEST_VALUE`, `MISC.RATIO.SCALE_FACTOR_WRONG_DIRECTION` |

**Applicability reconciliation (resolves ratio-math B4).** The §10 `MISC.RATIO.*` registry's `applicability` predicates are authored so that **every distractor source named above is applicable to the task that cites it**, each with a task-correct exact formula:
- `MISC.RATIO.WRONG_TOTAL_PARTS` is applicable to the conversion tasks **T3 `ratio_to_fraction` and T4 `fraction_to_ratio`** (predicted using `Σparts ± 1` per the §10 fixed-direction adapter), in addition to the share tasks.
- `MISC.RATIO.ADDS_PARTS_INCORRECTLY` is applicable to **T4 `fraction_to_ratio`** (the student forms `a : (a+b)` or mis-sums the parts) in addition to the write/share tasks.
- `MISC.RATIO.SCALE_FACTOR_WRONG_DIRECTION` is applicable to **T11 `best_buy`** (the student inverts the price-per-unit / units-per-price direction, choosing the worse value) in addition to `simple_scale`.
§10 owns the exact formula text for each (task, diagnostic) pair; §3.1 only asserts the applicability and the distractor selection. The §10 `RULES_BY_TASK` map and these §3.1 distractor sets are cross-checked by `ratio-graph.test.ts` so neither can drift from the other.

**Tasks that are free-response only** (no MC; three distinct, exact, misconception-backed distractors are not jointly available, or the answer is multi-cell so MC would distort the construct):

| Task | Reason FR-only |
| --- | --- |
| T2 `write_from_quantities` | A `ratio` answer with order and simplest-form is best assessed by construction, not selection; reversal is captured as FR diagnostic feedback, but a clean three-distractor set that is not trivially eliminable is not guaranteed. |
| T5 `share_two_part` | Multi-value / `table-completion` shape; MC would collapse the sum-to-total construct. |
| T6 `share_three_part` | Three labelled shares (`table-completion`); inherently not a single-choice item. |
| T7 `missing_part` | Single integer/rational with strong FR diagnostics, but the realistic distractor pool is dominated by one or two errors, not three independent strong ones across all reachable parameters. |
| T10 `unit_rate` | Exact integer/rational rate; FR exercises the exact-rational checker, which is the point. |
| T12 `simple_scale` | Direction-of-scale is the key construct and is captured as FR feedback; the answer can be `ratio` or a converted length, and a uniform three-distractor set across both shapes is not guaranteed. |

For an MC-eligible task, MC is offered **only when the drawn parameters actually realise all three named distractors as distinct values different from the correct answer** (e.g. `simplify` cannot offer MC when the input is already in simplest form and `DOES_NOT_SIMPLIFY_FULLY` collides with the correct answer; `ratio_to_fraction` cannot offer MC on a small case such as `1:2` where `RATIO_TO_FRACTION_ONE_PART_OVER_OTHER` and `WRONG_TOTAL_PARTS` both yield `1/2` — so MC-eligible `ratio_to_fraction` draws are constrained to `Σparts ≥ 4` with distinct part values, and `1:1` is excluded per §12 — see the unsupported-MC policy below).

### 3.2 Unsupported-MC policy (deterministic redraw OR clear error — never silent FR downgrade)

An explicit multiple-choice request is **never silently converted to free-response**. The generator's behaviour is deterministic and total:

1. **Task is not in `MC_ELIGIBLE_TASKS`** (the six FR-only tasks): the request returns a clear **unsupported-interaction error** (`interaction-not-supported`). No redraw, no FR substitution.
2. **Task is MC-eligible but the drawn case cannot realise three distinct misconception distractors** (e.g. a distractor formula collides with the correct answer, two distractor formulas collide with each other, or a distractor is non-positive / not a valid answer of the task's type): the generator **deterministically redraws** — it advances the seeded Mulberry32 sequence to the next MC-eligible case for that task (a bounded, fixed redraw budget recorded in the §11 source of truth). If the redraw budget is exhausted without an MC-eligible case (a deliberately constructed pathological seed), it returns the same clear **unsupported-interaction error** rather than emitting a weak or duplicate-option MC item. The redraw is part of the deterministic rng ORDER and is identical in Python and TypeScript (the parity contract).

For T11 `best_buy`, where `multiple-choice` is the answer type itself, the same total behaviour applies to the *option set*: the item is emitted only when the three misconception-predicted options are distinct from each other and from the correct best-value option; otherwise the generator redraws within budget or returns `interaction-not-supported`.

A named test asserts, for **each FR-only task**, that an MC request returns `interaction-not-supported`, and, for **each MC-eligible task**, that a deliberately-degenerate seed either redraws to a valid three-distinct-distractor MC item or returns `interaction-not-supported` — never a silently-downgraded free-response item.

### 3.3 1:1 task → objective → interaction(s) → answer.shape matrix

`answer.type` values are the §2.0 tokens (`ratio`, `integer`, `exact-rational`, `table-completion`, `multiple-choice`). `ratio` answers carry **no units**; all other value answers are exact integers or reduced `Rational{num,den}` (no irrationals, no approximate decimals). "MC" appears only where three distinct misconception-backed distractors exist (§3.1).

| # | Objective ID | Interaction(s) | `answer.type` / shape | Order matters? | Value form |
| --- | --- | --- | --- | --- | --- |
| T1 | `SPI.MIDDLE.RATIO.SIMPLIFY.01` | free-response (default), multiple-choice | `ratio` (`{parts:[…]}`, gcd=1) | yes | 2- or 3-part positive-int tuple, simplest form |
| T2 | `SPI.MIDDLE.RATIO.WRITE_FROM_QUANTITIES.01` | free-response only | `ratio` | yes (stated order) | 2- or 3-part positive-int tuple, simplest form |
| T3 | `SPI.MIDDLE.RATIO.RATIO_TO_FRACTION.01` | free-response (default), multiple-choice | `exact-rational` (`part/total`, reduced) | n/a | reduced proper fraction |
| T4 | `SPI.MIDDLE.RATIO.FRACTION_TO_RATIO.01` | free-response (default), multiple-choice | `ratio` | yes | positive-int tuple, simplest form |
| T5 | `SPI.MIDDLE.RATIO.SHARE_TWO_PART.01` | free-response only | `table-completion` (2 labelled cells) | label correspondence | exact integers summing to total |
| T6 | `SPI.MIDDLE.RATIO.SHARE_THREE_PART.01` | free-response only | `table-completion` (three labelled) | label correspondence | exact integers summing to total |
| T7 | `SPI.MIDDLE.RATIO.MISSING_PART.01` | free-response only | `integer` (v1.0.0) | n/a | exact integer; generation enforces `parts[knownIndex] ∣ knownValue` so `missingValue` is integral by construction (§12, decision E) |
| T8 | `SPI.MIDDLE.RATIO.DIRECT_PROPORTION.01` | free-response (default), multiple-choice | `integer` or `exact-rational` | n/a | exact integer / reduced rational |
| T9 | `SPI.MIDDLE.RATIO.INVERSE_PROPORTION.01` | free-response (default), multiple-choice | `integer` | n/a | exact integer (non-exact cases excluded, §12) |
| T10 | `SPI.MIDDLE.RATIO.UNIT_RATE.01` | free-response only | `exact-rational` (collapse to `integer` when whole if platform policy requires) | n/a | reduced rational per unit (exact integer when whole) |
| T11 | `SPI.MIDDLE.RATIO.BEST_BUY.01` | multiple-choice | `multiple-choice` (labelled option; exact unit rates underpin it in the solution) | n/a | option key + exact unit-rate evidence in solution |
| T12 | `SPI.MIDDLE.RATIO.SIMPLE_SCALE.01` | free-response only | `integer` when whole, else `exact-rational` (decision D/I; scaled numerical value, not a ratio) | n/a | exact integer / reduced rational |

**Interaction summary:** all twelve tasks are **free-response-first** except T11 `best_buy`, whose answer type *is* `multiple-choice` (the labelled choice is the construct). **Six** tasks (T1, T3, T4, T8, T9, T11 = `MC_ELIGIBLE_TASKS`) support **multiple-choice** with three exact, misconception-backed distractors/options; the other **six** (T2, T5, T6, T7, T10, T12) are **free-response only**. An MC request on an FR-only task, or on an MC-eligible task whose drawn case cannot realise three distinct distractors after the bounded deterministic redraw, returns `interaction-not-supported` — never a silent FR downgrade (§3.2).

This single source of truth is consumed by the review-pack **COVERAGE-MATRIX** machinery (re-used by name from stats/mensuration): required cells = every task × every supported interaction × every reachable difficulty band × every realised answer shape, derived from the §11 distribution report; the pack builder **fails on any missing reachable cell**. Because answer shapes vary across the family, the matrix's "realised answer shape" axis records `answer.type` plus, for `ratio`, `(partCount ∈ {2,3}, simplifiedFromUnsimplified ∈ {yes,no})`, and for value answers `value-kind ∈ {integer, rational}` — so two-part vs three-part, simplified-vs-unsimplified input, integer-vs-rational unit rates, integer-vs-rational missing parts, and the equivalent/reversed-ratio traps are provably exercised and blocked on if missing. The `multiple-choice` answer-shape axis for T11 records the option count and the realised misconception-option set; there is **no `comparison` shape token** in the coverage vocabulary.

### 3.4 Scope guard (exactly the twelve tasks)

The task enum `RATIO_TASKS` (§1.3) has exactly twelve members; the generator dispatch is a **total function** over that enum with **no default branch**; the conformance/graph tests assert the objective set, the task set, the `RULES_BY_TASK` key set, the `MC_ELIGIBLE_TASKS` subset, and the coverage matrix all key off `RATIO_TASKS` with **cardinality twelve** and an **identical task-key set** (§1.3(c)), and that no `_UNITARY`-suffixed ID and no superseded slug spelling appears anywhere (§1.3(d)/(e)). Every deferred topic — percentages as a family; compound/continued proportion proofs; currency conversion and exchange rates; recipe scaling with units; compound units beyond a simple unit rate; similar-triangles scale factors; gradient-as-ratio; gear/lever ratios; irrational ratios; non-exact decimal-ratio terms; trigonometric ratios; probability odds; algebraic ratio proofs — is **deterministically excluded by construction**: there is no task slug, objective ID, or generator branch that can emit one, and each exclusion is asserted by a named test (§12/§15), not merely filtered at runtime.

---

Sections 1-3 are complete, revised, and self-consistent. Summary of what changed to clear the blockers that touch these sections:

- **B1/B2/B3 slug-and-ID drift (all four critics):** Pinned the ONE canonical `RATIO_TASKS` set (§1.3 set wins) with an explicit superseded-spelling ban list (`simplify_ratio`, `write_ratio`, `write_ratio_from_quantities`, `direct_proportion_unitary`, `inverse_proportion_unitary`, etc.) and the ONE objective-ID set (§1.2, no `_UNITARY` suffix). Added graph-test clauses (d) string-scan over slugs + MISC ids, (e) `_UNITARY`-suffix guard. Downstream clusters §9/§10/§11 must conform to these.
- **`comparison` phantom answer.type (platform-fit B1, completeness B3):** Removed entirely. Best-buy (T11) now uses the **live `multiple-choice` answer type** (verified at schema line 202); `ratio` remains the only new enum member. Updated §2.0, §2.11, §3.1, §3.3, §3.4, and the coverage vocabulary; explicit "no `comparison` anywhere" statements added.
- **`missing_part` answer type (decision E):** §2.7, the §3.3 matrix, §7, §9, §11, and §12 all declare `missing_part` **integer-only** in v1.0.0; the `missing-part-exact` divisibility constraint (`parts[knownIndex] ∣ knownValue`) is **hard, non-optional** (no escape hatch) and guarantees the recovered value is an exact integer. There is no exact-rational `missing_part` path in v1.0.0 (future extension only).
- **MC distractor applicability (ratio-math B4):** Added the applicability-reconciliation note instructing §10 to make `WRONG_TOTAL_PARTS` applicable to T3/T4, `ADDS_PARTS_INCORRECTLY` to T4, and `SCALE_FACTOR_WRONG_DIRECTION` to T11; corrected the T1 distractor id to `EQUIVALENT_BUT_UNSIMPLIFIED_WHEN_SIMPLEST_REQUIRED` to match the §10 registry spelling. Added the `ratio_to_fraction` `Σparts ≥ 4` MC-eligibility constraint (ratio-math I1/I5).
- **Best-buy band conflict (completeness I3):** §2.11 band set to `{min:3,max:5}` as the projection of §11's source of truth; `{min:2,max:4}` superseded.
- **`verbal-context` ↔ `readingDemand` (completeness I4):** §2 now states T8–T11's `verbal-context` items are exactly those that lift §11 `readingDemand` off zero, making the representation claim testable.
- **Renderer cross-ref (renderer-figure B1):** §1.1's forward reference points to §3.4 (scope guard); no `ratio-figure`/check-name spellings live in my sections.

Note for downstream clusters: §5/§7/§10 must adopt ONE result-code vocabulary (completeness I5) and §8/§9/§13/§14 ONE check-name vocabulary (completeness I6) — those tokens are not defined in sections 1-3, so I have not fixed them here, but my sections reference only `interaction-not-supported` and the named graph/coverage tests.

Target file: `C:\Users\Mohamad Solaiman\OneDrive\Desktop\Claude Question generator\docs\GENERATOR_SPEC_proportion_ratio_PROPOSAL.md`

## 4. Ratio answer schema

This section specifies the **exact additive delta** to `schemas/question-item.schema.json` (`$id: https://spi-math.academy/schemas/question-item.schema.json`, `version: "1.0.0"`) that introduces a third structured, canonical-first answer contract: `answer.type = "ratio"`. It mirrors the two approved precedents — `quantity` (mensuration) and `transformation` (transformations) — **byte-for-byte in mechanism**: a single additive enum member, a structured `canonical` object, and conditional `if/then/const` rules inside `answer.allOf` (never `oneOf`/`anyOf`), so the runtime precompiled Ajv validator (`core/schema/compiled/question-item.validator.mjs`) and the offline Python conformance checker (`oracle/check_conformance.py`) apply **identical** rules. Existing approved items stay valid and byte-for-byte unchanged.

> **Keyword discipline (binding for this whole delta).** The verified Python conformance checker (`oracle/check_conformance.py`, `check()` at lines 68–129) supports exactly: `$ref`, `const`, `allOf`, `if`/`then`/`else`, `not`, `type`, `enum`, `pattern`, `required`, `additionalProperties:false`, boolean (`false`) subschemas, `items`, and `minItems`. It does **NOT** support `anyOf`, `oneOf`, or `maxItems`. Therefore the entire `ratio` delta is written using only `{ if, then, const, required, properties, additionalProperties:false, items, type, minimum, minItems, maxItems }`, and uses **no `anyOf` and no `oneOf` anywhere** (the brief's "identical rules in both validators" gate would otherwise silently break — the checker would ignore the keyword while Ajv enforced it). The single keyword in this list the checker does not yet support — `maxItems` — is therefore handled as a **named, owner-visible additive checker-code-path delta** (§4.4a), not silently assumed; this is the only new checker capability the family requires, and it is a hard prerequisite of the schema delta, not an optional aid.

### 4.1 Design invariants (binding)

| # | Invariant | Enforcement |
|---|---|---|
| I1 | **Canonical-first.** The structured value IS `answer.canonical`. There is no sibling field holding the ratio (no `ratio`, no `parts` outside `canonical`). | `additionalProperties:false` on `answer` (already present); `canonical` is an object with `additionalProperties:false`. |
| I2 | **Display derived, never authoritative.** `answer.display` (e.g. `"2:3"`) is rendered from `canonical.parts` by the formatter (§5). It is never the canonical and is never parsed back. | `display` stays an optional string; checker reads `canonical` only. |
| I3 | **No duplication.** The ratio is stored once. | I1 + no `equivalentForms` requirement for canonical identity. |
| I4 | **Positive integers, simplest form.** Each part is an integer `>= 1`; `gcd(parts) = 1` in the stored canonical. | `items` integer + `minimum:1`; semantic gcd rule (§4.4, validator-enforced; see note). |
| I5 | **Arity 2..3 in v1.0.0.** `minItems:2`, `maxItems:3`. Single-term and 4+-term ratios are out of scope (defer list). | `minItems`/`maxItems` on `canonical.parts` (the `maxItems` enforcement requires the §4.4a checker delta). |
| I6 | **No units, no measure, no tolerance.** Ratios are pure (dimensionless ordered tuples). | `units:false`, `measure:false`, `tolerance:false` (boolean subschemas) under the `ratio` branch — exactly as `transformation` forbids them. |
| I7 | **Additive + backward-compatible.** No existing property changes meaning; no existing item re-validates differently. | New enum member appended; new `allOf` clauses are guarded by `if type==="ratio"` (and a reverse-guard, §4.4). |

> **Note on I4 (gcd).** JSON Schema cannot express "the gcd of an integer array is 1". Per the established pattern, the schema enforces the **shape** (positive integers, arity, no units), and the **semantic** `gcd(parts)=1` invariant is enforced by (a) the Python oracle canonicalizer (§5), (b) the TS mirror, and (c) the conformance/parity fixtures and a dedicated schema-adjacent test (`test_ratio_schema.py`, §4.7) — identical to how `transformation` enforces "vector ≠ (0,0)" partly in schema (the `not` clause) and fully in the oracle. The one purely-arithmetic part of I4 that *can* live in schema (zero/negative exclusion, the `(0,0)`-analog) is encoded via `minimum:1`.

### 4.2 Enum delta — `$defs.answerType`

Append the single literal `"ratio"` to the existing `enum`, immediately after `"transformation"` (the last token of the existing structured-canonical line 198), as a **new trailing token on that line** — never inserted before an existing member. No member is removed or reordered, and every existing member's byte position is unchanged (verified against `schemas/question-item.schema.json` lines 196–205).

```diff
   "enum": [
     "integer", "decimal", "fraction", "exact-rational", "mixed-number", "exact-surd", "exact-trig",
-    "quantity", "transformation",
+    "quantity", "transformation", "ratio",
     "algebraic-expression", "equation", "inequality", "interval", "set",
     "ordered-pair", "coordinate", "sequence", "permutation", "combination",
     "vector", "matrix", "complex-number",
     "multiple-choice", "multiple-select", "matching", "ordering", "classification",
     "table-completion", "graph-response", "geometry-construction", "diagram-labelling",
     "short-explanation", "extended-response", "proof", "rubric-scored"
   ]
```

**`ratio` is the ONLY new enum member this family adds.** Two existing live enum members are reused unchanged and require **no** schema delta:

- **`table-completion`** (already present, line 203) — reused unchanged for the multi-part sharing answers (§7). No second enum member is introduced for that, and no `if/then` constraint is attached to it.
- **`multiple-choice`** (already present, line 202) — the representation for the best-buy / rate-comparison task (T11). The best-buy answer is intrinsically a *labelled choice* between offers; it is modelled as a `multiple-choice` answer whose options are the candidate offers and whose exact unit-rate witnesses live in the solution/feedback (§5/§9), **not** as a bespoke structured canonical. There is **no `comparison` answer type** anywhere in this family: `comparison` is not a member of the platform `answerType` enum (verified: zero occurrences in `schemas/question-item.schema.json`), this delta does not add it, and §15 likewise adds nothing but `ratio`. The brief's "at most one new answer type" framing is therefore met exactly — `ratio` is the sole new `answer.type`, and every other task answer (sharing → `table-completion`; missing-part / direct / inverse / unit-rate / scale → `integer` or `exact-rational`; best-buy → `multiple-choice`) uses a live enum member with no delta.

### 4.3 Canonical object shape

The canonical for a `ratio` answer is exactly:

```json
{ "parts": [<positive int>, ...] }
```

Two illustrative canonical answers (the *only* permitted canonical form — simplest, positive, ordered):

```json
{ "type": "ratio", "canonical": { "parts": [2, 3] }, "display": "2:3" }
```

```json
{ "type": "ratio", "canonical": { "parts": [2, 3, 5] }, "display": "2:3:5" }
```

Equivalence (e.g. `2:3 == 4:6 == 20:30`, `2:3:5 == 4:6:10`) is a **checker** concern (§5), not a storage concern: the canonical is always the simplest form. Order is significant: `[2,3]` ≠ `[3,2]` (the checker rejects the reversal; see §5 and the checker matrix in §14).

### 4.4 The `allOf` conditional rules (the schema delta proper)

**Two** clauses are appended to `answer.allOf`, after the existing `transformation` clauses (the last existing clause ends at line 313). They are **guarded** (`if type==="ratio"` for the forward rule; a `canonical.parts`-shaped guard for the reverse rule) so they are inert for every existing item. The `then` bodies use `const`/boolean-`false` subschemas exactly as the `quantity` and `transformation` precedents do. **No `anyOf`/`oneOf` appears anywhere** (see §4.4b for why the previously-considered defence-in-depth third clause was removed).

```jsonc
// appended to schemas/question-item.schema.json  ->  $defs.answer.allOf
{
  "$comment": "A 'ratio' answer's canonical IS the structured ordered-tuple descriptor (canonical-first; no sibling field). 'display' is derived. Parts are POSITIVE integers (>=1); 2 or 3 of them in v1.0.0. gcd(parts)=1 is a semantic invariant enforced by the oracle/TS canonicalizer + ratio fixtures (the schema cannot express gcd). Ratio answers carry NO units/measure/tolerance.",
  "if": { "properties": { "type": { "const": "ratio" } }, "required": ["type"] },
  "then": {
    "required": ["canonical"],
    "properties": {
      "canonical": {
        "type": "object",
        "additionalProperties": false,
        "required": ["parts"],
        "properties": {
          "parts": {
            "type": "array",
            "minItems": 2,
            "maxItems": 3,
            "items": { "type": "integer", "minimum": 1 }
          }
        }
      },
      "units": false,
      "measure": false,
      "tolerance": false
    }
  }
},
{
  "$comment": "A ratio descriptor (a canonical object carrying 'parts', the array shape used only by ratios) is valid ONLY under answer.type='ratio' — never under another answer type. This is the reverse-guard, mirroring the transformation 'kind'-implies-transformation rule (schema lines 310-313).",
  "if": {
    "required": ["canonical"],
    "properties": {
      "canonical": {
        "type": "object",
        "required": ["parts"],
        "properties": { "parts": { "type": "array", "items": { "type": "integer" } } }
      }
    }
  },
  "then": { "required": ["type"], "properties": { "type": { "const": "ratio" } } }
}
```

**Why this is identical in mechanism to the precedents:**

- Forward rule shape `if type===const … then required + properties + units:false/measure:false/tolerance:false` is copied directly from the `transformation` clause (schema lines 286–308).
- The reverse-guard (`canonical` carrying the family's discriminant ⇒ `type` must be the family's type) is copied directly from the `transformation` "a transformation descriptor … valid ONLY under answer.type='transformation'" clause (lines 310–313). Here the discriminant is the `parts` array rather than a `kind` string.
- All clauses live in `allOf`; **none use `oneOf`/`anyOf` at any nesting depth** (see §4.4b). Every keyword used — `if`/`then`/`const`/`required`/`properties`/`additionalProperties:false`/`items`/`type`/`minimum`/`minItems`/`maxItems` — is in the subset the conformance checker evaluates (`check_conformance.py` lines 68–129), with the single exception of `maxItems`, which the §4.4a checker delta adds.

#### 4.4a Required checker delta: `maxItems` (named, owner-visible, not "reused unchanged")

`maxItems` appears **zero** times in the current `question-item.schema.json` and **zero** times in `oracle/check_conformance.py` (verified). The `ratio` `canonical.parts` arity cap (`maxItems:3`, the only way to deterministically reject a 4-part ratio) is therefore the **first** use of `maxItems` in the schema, and the offline conformance checker would **silently pass** a 4-part `parts` array today — which would make Ajv and the Python checker disagree, violating the brief's "identical rules in both validators" gate. This is a **real new checker code path in a shared dependency** used by all eight approved families' conformance runs, *not* a no-op aid.

It is carried as an explicit, owner-visible delta:

- **The change.** One additive branch in `check()`, symmetric to the existing `minItems` branch (lines 125–126), inside the existing `isinstance(instance, list)` block:

  ```python
  if "maxItems" in schema and len(instance) > schema["maxItems"]:
      errors.append(f"{path}: needs <= {schema['maxItems']} items")
  ```

- **Regression guarantee.** A regression assertion in the conformance suite re-runs the conformance output for **all eight prior approved families** (sequences, geometric, linear, geometry-angles, coordinate-lines, data-handling, mensuration, transformations) and asserts it is **byte-for-byte unchanged** after the branch is added. Because none of those families' schemas or items use `maxItems`, the branch is never reached for them and their output cannot change; the assertion pins that fact.
- **Offline exercise.** A **4-part negative fixture** (`{"type":"ratio","canonical":{"parts":[1,2,3,4]}}`) is added to the offline conformance run (`oracle/check_conformance.py` live-item block `4h`, §4.6/§4.7), not only to the Ajv TS test, so the new branch is actually exercised by Python and proven to reject — closing the Ajv/Python divergence rather than merely asserting it closed.
- **Honesty in the gate tables.** §15.1 and §16 are corrected to list this `maxItems` branch as a **named additive checker delta** (`check_conformance.py`: +1 list-validation branch + a regression assertion), and must **not** claim "no new checker code path" for this family. It is the one and only checker capability this delta adds beyond what the transformation extension already exercised.

#### 4.4b Why there is no defence-in-depth "clause 3" (`anyOf`-inside-`not` removed)

An earlier draft included a third, defence-in-depth clause forbidding a `ratio`-typed answer from carrying a foreign canonical (`{num}`/`{den}`/`{kind}`) via `not: { anyOf: [ … ] }`. **It is removed.** The conformance checker's `not` handler evaluates its argument through `check()` (lines 90–91), and `check()` has **no `anyOf` handler** (verified: `anyOf`/`oneOf` appear nowhere in `check_conformance.py`). An `anyOf` nested inside `not` would therefore be **silently ignored by the Python checker while enforced by Ajv** — the exact Ajv-vs-Python rule divergence the brief forbids. Dropping the clause is safe and loses no enforcement:

- The forward rule's `canonical.additionalProperties:false` + `required:["parts"]` already rejects any `ratio`-typed canonical carrying `num`, `den`, or `kind` (those keys are not in the `parts`-only `properties`, and `parts` is required).
- The reverse-guard already forces any `parts`-bearing canonical to be `type:"ratio"`.

These two clauses pin cross-type identity completely (the same way the transformation forward `additionalProperties:false` + reverse-guard suffice there). The negative fixtures in §4.7 that the dropped clause would have caught (rational-canonical-under-ratio, transformation-canonical-under-ratio) are **all still rejected** by the surviving forward rule — see the §4.7 "Violated rule" column, which now cites only `required`/`additionalProperties:false`/reverse-guard, never the removed clause.

### 4.5 Cross-type isolation guarantee

After this delta, the following are *structurally impossible* (rejected by **both** validators, using only shared-subset keywords):

| Attempted item | Rejected because |
|---|---|
| `type:"ratio"`, `canonical:{num:2,den:3}` | forward rule: `canonical` lacks required `parts`; `additionalProperties:false` rejects `num`/`den`. |
| `type:"ratio"`, `canonical:{parts:[2,3]}`, `units:"cm"` | `units:false`. |
| `type:"ratio"`, `canonical:{parts:[2,3]}`, `measure:{…}` | `measure:false`. |
| `type:"ratio"`, `canonical:{parts:[2,3]}`, `tolerance:{absolute:1}` | `tolerance:false`. |
| `type:"exact-rational"`, `canonical:{parts:[2,3]}` | reverse-guard: a `parts` canonical ⇒ `type` must be `"ratio"`. |
| `type:"quantity"`, `canonical:{parts:[2,3]}` | reverse-guard + the existing quantity rule (which requires `{num,den}`). |
| `type:"ratio"`, `canonical:{parts:[2,0]}` | `items.minimum:1`. |
| `type:"ratio"`, `canonical:{parts:[2,-3]}` | `items.minimum:1`. |
| `type:"ratio"`, `canonical:{parts:[6]}` | `minItems:2`. |
| `type:"ratio"`, `canonical:{parts:[1,2,3,4]}` | `maxItems:3` (enforced in Ajv and, via the §4.4a branch, in the Python checker — exercised by the block-`4h` 4-part fixture). |
| `type:"ratio"`, `canonical:{parts:[2.0,3.0]}` (non-integer) | `items.type:"integer"` (and the conformance checker's bool/int guard, lines 96–99). |
| `type:"ratio"`, `canonical:{parts:[4,6]}` (unsimplified) | **not** a schema rejection — schema accepts the shape; rejected by the oracle/TS canonicalizer + `test_ratio_schema.py` gcd assertion (§4.7) and never *emitted* by the generator. Equivalent-but-unsimplified *student input* is a §5 checker-policy concern, not a stored-canonical concern. |

`gen.proportion.ratio` **never stores an unsimplified canonical**; the generator's canonicalizer divides by `gcd` before constructing the answer object (§5/§6). The `[4,6]` row above is the one I4 case schema alone cannot catch, which is why it is pinned by the oracle and the ratio fixtures.

Note that the cross-type rejections of a rational-`{num,den}` or transformation-`{kind}` canonical under `type:"ratio"` are achieved by the **forward rule alone** (`required:["parts"]` + `additionalProperties:false`), with no reliance on any `anyOf`/`not` clause — consistent with §4.4b.

### 4.6 Backward compatibility and approved-fixture stability

- **Additive only.** The sole edits are: one appended enum literal (§4.2), **two** appended `allOf` clauses (§4.4), and one additive `maxItems` branch in the conformance checker (§4.4a). No existing property, `$def`, enum member, or clause is modified or removed. `answer` already has `additionalProperties:false`, so no new sibling property is silently admitted.
- **Guarded clauses are inert for prior families.** Every appended clause's `if` fails for any item whose `type` ≠ `"ratio"` and whose `canonical` has no `parts` array. The eight approved families (sequences, geometric, linear, geometry-angles, coordinate-lines, data-handling, mensuration, transformations) produce no `parts`-shaped canonical, so the reverse-guard never fires for them; and none use `maxItems`, so the §4.4a branch is never reached for them.
- **No approved-fixture drift.** All existing golden/parity/conformance fixtures (`oracle/golden/*.json`, the ≥300-entry parity fixtures, embedded schema `examples`) re-validate byte-for-byte unchanged. The approved-family fixture-drift check (platform gate) and the §4.4a all-eight-families conformance regression assertion are both expected to report zero diffs after this delta. The conformance entrypoint (`oracle/check_conformance.py`) gains a new live-item block `4h` (ratio items, all 12 tasks + seeds 1/42/123456789, plus the 4-part `maxItems` negative fixture) **alongside** the existing blocks; existing blocks are untouched.
- **Schema `version`.** Per precedent (the `quantity` and `transformation` additions did **not** bump the `question-item.schema.json` top-level `version` string — verified: the schema is still `version:"1.0.0"` after both were added), the schema `version` remains `"1.0.0"`; the change is tracked via the manifest `versionTags` and `docs/APPROVED_VERSIONS.md`, not a schema-file version bump. §15.1 states this explicitly so a reviewer does not flag the non-bump as an omission. (Owner may override to bump if preferred; the delta itself is identical either way.)

### 4.7 Runtime Ajv + Python conformance enforcement, and schema fixtures

Both validators apply the *same* clauses, using only the shared keyword subset (§4 keyword-discipline note):

- **Runtime (TypeScript / Ajv).** The clauses compile into `core/schema/compiled/question-item.validator.mjs` (precompiled at build, no runtime schema compilation). Newly generated `ratio` items validate at lifecycle state `machine-validated` before entering any bank. A TS test in the `core/schema/runtime-validate.test.ts` family adds the ratio positive/negative cases (mirroring the transformation TS test).
- **Offline (Python).** `oracle/check_conformance.py` already evaluates `allOf` / `if`/`then`/`else` / `not` / `const` / `enum` / `minItems` / `additionalProperties:false` / boolean (`false`) subschemas / `items` / `type` / `required` / `pattern` (lines 68–129). The **one** capability this delta adds is the `maxItems` branch (§4.4a) — symmetric to the existing `minItems` branch, with the all-eight-families regression assertion. The new live-item block `4h` validates real generated ratio items **and** the 4-part `maxItems` negative fixture (so the new branch is exercised offline, not only in Ajv).

A dedicated schema-conformance evidence test `oracle/tests/test_ratio_schema.py` mirrors `oracle/tests/test_transformation_schema.py` exactly (same harness: `cc.check(ans, _ANSWER, _REG, _SCHEMA, "answer", e)`), supplying the positive/negative schema fixtures below. The `gcd(parts)=1` semantic invariant (uncheckable by schema) is asserted in this same test by recomputing `math.gcd` over `canonical.parts` for every POSITIVE fixture and every generated item.

**Positive schema fixtures** (must produce `_errors == []`):

| Name | Answer object |
|---|---|
| two-part simplest | `{"type":"ratio","canonical":{"parts":[2,3]},"display":"2:3"}` |
| three-part simplest | `{"type":"ratio","canonical":{"parts":[2,3,5]},"display":"2:3:5"}` |
| two-part with 1 | `{"type":"ratio","canonical":{"parts":[1,4]},"display":"1:4"}` |
| three-part with repeats | `{"type":"ratio","canonical":{"parts":[1,1,2]},"display":"1:1:2"}` |
| large coprime terms | `{"type":"ratio","canonical":{"parts":[7,13]},"display":"7:13"}` |
| display optional | `{"type":"ratio","canonical":{"parts":[3,4]}}` (no `display`) |

**Negative schema fixtures** (must produce `_errors != []`):

| Name | Answer object | Violated rule |
|---|---|---|
| zero part | `{"type":"ratio","canonical":{"parts":[2,0]},"display":"2:0"}` | `minimum:1` |
| negative part | `{"type":"ratio","canonical":{"parts":[2,-3]}}` | `minimum:1` |
| single term | `{"type":"ratio","canonical":{"parts":[5]}}` | `minItems:2` |
| four terms | `{"type":"ratio","canonical":{"parts":[1,2,3,4]}}` | `maxItems:3` (Ajv **and** Python via §4.4a branch; exercised by block `4h`) |
| non-integer part | `{"type":"ratio","canonical":{"parts":[1.5,2]}}` | `items.type:"integer"` |
| missing parts | `{"type":"ratio","canonical":{}}` | `required:["parts"]` |
| extra prop on canonical | `{"type":"ratio","canonical":{"parts":[2,3],"total":5}}` | `additionalProperties:false` |
| units on ratio | `{"type":"ratio","canonical":{"parts":[2,3]},"units":"cm"}` | `units:false` |
| measure on ratio | `{"type":"ratio","canonical":{"parts":[2,3]},"measure":{"dimension":"length","baseUnit":"cm","exponent":1}}` | `measure:false` |
| tolerance on ratio | `{"type":"ratio","canonical":{"parts":[2,3]},"tolerance":{"absolute":1}}` | `tolerance:false` |
| parts canonical under wrong type | `{"type":"exact-rational","canonical":{"parts":[2,3]}}` | reverse-guard ⇒ `type` const `"ratio"` |
| rational canonical under ratio type | `{"type":"ratio","canonical":{"num":2,"den":3}}` | forward rule: `required:["parts"]` + `additionalProperties:false` rejects `num`/`den` |
| transformation canonical under ratio type | `{"type":"ratio","canonical":{"kind":"translation","vector":{"dx":1,"dy":1}}}` | forward rule: `required:["parts"]` + `additionalProperties:false` rejects `kind`/`vector` |
| *(gcd, oracle-only)* unsimplified canonical | `{"type":"ratio","canonical":{"parts":[4,6]}}` | passes schema; **fails** the `test_ratio_schema.py` `gcd==1` assertion (proves I4 is enforced outside schema) |

The "rational canonical under ratio type" and "transformation canonical under ratio type" rows are rejected by the **surviving forward rule alone** (`required:["parts"]` + `additionalProperties:false`) — no removed defence-in-depth clause is relied upon (§4.4b). The last row is intentionally listed as schema-passing/oracle-failing to document precisely the I4 boundary: the schema guarantees positive integers + arity + no units; the oracle/TS canonicalizer + this test guarantee simplest form. The generator emits only canonicals that satisfy both.

### 4.8 Import / export behaviour

- **Export.** A `ratio` item serializes through `canonicalStringify` (sorted keys, compact: `{"canonical":{"parts":[2,3]},"display":"2:3","type":"ratio"}` under key-sorting) — identical to Python `json.dumps(sort_keys=True, ensure_ascii=False, separators=(",",":"))`. `parts` is a JSON integer array (no strings, no floats); the colon-formatted `display` is exported as a derived convenience string only. SVG/table media follow the family theme (§8/§13); the answer object carries no presentation beyond `display`.
- **Import (round-trip).** On import, an item with `type:"ratio"` is validated by the same precompiled Ajv validator before acceptance; the importer recomputes the canonicalizer over `canonical.parts` and **rejects** any imported item whose stored canonical is not in simplest form, whose `parts` violate the schema, or whose `display` does not match the formatter's output for that canonical (display is re-derived, never trusted). This makes import idempotent: `import(export(item))` yields a byte-identical item, and a hand-edited unsimplified or units-bearing ratio is rejected at the boundary rather than silently re-canonicalized.
- **No cross-format ambiguity.** Because `display` is never parsed on import (only re-derived and compared) and the canonical is the sole source of truth, there is no path by which an exported `"2:3"` string and a `{parts:[2,3]}` object could disagree; the validator + canonicalizer reconcile to the single canonical or reject.

This `answer.type = "ratio"` delta is **APPROVED** (owner, 2026-06-26) on the same additive, backward-compatible basis as `quantity` and `transformation`; implementation proceeds oracle-first. The one shared-dependency change it requires — the additive `maxItems` branch in `oracle/check_conformance.py` (§4.4a) — is called out explicitly in §15.1 and §16 as a named, owner-visible delta with an all-eight-families no-drift regression assertion, and is **not** claimed as a zero-code change.

---

Below is a summary of the revision for the orchestrator.

**Section 4 (Ratio answer schema) — revised. Blockers fixed (all verified against the live repo before editing):**

- **platform-fit B3 / B4 (Ajv↔Python divergence — the brief's "identical rules in both validators" gate).** Verified in `C:\Users\Mohamad Solaiman\OneDrive\Desktop\Claude Question generator\oracle\check_conformance.py` (`check()` lines 68–129) that the conformance checker supports only `{$ref, const, allOf, if/then/else, not, type, enum, pattern, required, additionalProperties:false, items, minItems}` and supports **neither `anyOf`/`oneOf` nor `maxItems`**.
  - **Dropped the defence-in-depth "clause 3"** that used `not:{anyOf:[…]}` — the Python checker silently ignores `anyOf`, so it would have enforced in Ajv but not Python. Now **only two** `allOf` clauses (forward + reverse-guard), no `anyOf`/`oneOf` at any depth. Added §4.4b explaining the removal is enforcement-neutral (forward `required:["parts"]`+`additionalProperties:false` + reverse-guard already pin cross-type identity); updated the §4.5 and §4.7 tables so the foreign-canonical rejections cite only surviving rules.
  - **`maxItems` honestly carried as a named, owner-visible additive checker-code-path delta** (new §4.4a): the exact 3-line `maxItems` branch for `check_conformance.py`, an all-eight-prior-families byte-for-byte conformance regression assertion, and a 4-part negative fixture added to the **offline** conformance run (block `4h`) so the branch is exercised by Python, not just Ajv. Added a binding keyword-discipline note at the top of §4. Flagged that §15.1/§16 must stop claiming "no new checker code path."

- **platform-fit B1 / completeness B3 (`comparison` phantom answer type).** Verified `comparison` is absent from the enum (`schemas/question-item.schema.json` lines 196–205). §4.2 now reinforces that **`ratio` is the only new enum member**, and explicitly states best-buy (T11) reuses the existing live **`multiple-choice`** type (sharing reuses live `table-completion`) — no `comparison` type is added by this family or by §15.

- **platform-fit improvement 1 (enum byte-position).** §4.2 now states `ratio` is appended as a new trailing token after `transformation` on line 198, never inserted before an existing member, preserving every existing member's byte position.

**Out of my section (left to the owning sections, not introduced by §4):** the slug-set / objective-ID drift (completeness B1/B2 → §1/§9/§10/§11) and the `missing_part` answer-type / divisibility reconciliation (ratio-math B1/B2 → §2/§3/§7/§9). Section 4 stays slug-agnostic and names no competing slug or objective-ID spelling, and references best-buy only via the `multiple-choice` reuse — so it introduces no new drift. The canonical-first `ratio` contract, `gcd` semantics, arity, and no-units invariants are unchanged and remain precedent-faithful to `quantity`/`transformation`.

## 5. Ratio parser, formatter, canonicalizer, and equivalence checker

This section specifies the `"ratio"` answer-contract machinery for `gen.proportion.ratio v1.0.0`. It is the proportion-family analogue of the dimensional-quantity contract approved in **gen.measurement.mensuration v1.0.1** (`oracle/spi_oracle/mensuration_units.py` ↔ `domains/measurement/mensuration-units.ts`) and the descriptor contract approved in **gen.geometry.transformations** (`transformations_descriptor.py` ↔ `transformations-descriptor.ts`): a finite, fully-anchored parser → normalized structured canonical → formatter → STRUCTURAL equivalence checker, with a closed `RESULT_CODES` tuple and targeted feedback drawn ONLY from displayed/parsed values. Following that precedent the machinery is **family-local** — there is no shared `core/answer-checking/ratio.*`. Every routine is authored **oracle-first in Python** at `oracle/spi_oracle/ratio_answer.py` and mirrored **BYTE-IDENTICALLY** in TypeScript at `domains/proportion/ratio-answer.ts`; the call ORDER of the seeded PRNG is never touched here (these are pure string/integer routines, no RNG). Parity is gated by the task-pinned ≥300-entry parity fixture, the golden vectors, and the dedicated **RATIO-CHECKER matrix** (§5.8, evidence in §14). Comparison is ALWAYS over the canonical integer tuple, NEVER over raw student text.

**Normative result-code casing (ONE canonical lower-kebab vocabulary — decision F).** Section 5 is the SINGLE source of truth for the family's result-code vocabulary. The codes are the lower-kebab string literals listed in the `RESULT_CODES` tuple (§5.7): `correct`, `equivalent-not-simplified`, `wrong-order`, `wrong-ratio`, `wrong-number-of-parts`, `zero-or-negative-part`, `unsupported-term`, `unparsed-trailing-text`, `malformed-response`. Every other section that names a result code — §7.4 (table-completion result mapping), §9 (independent validator's `expectedResultCode`), §10 (`MISC.RATIO.*` `expectedResultCode`), §12, and §14 — uses these exact strings verbatim. There is **NO UPPER_SNAKE alias, NO slash-style code, and NO generic `wrong`/`partial` result code**: every one of `EQUIVALENT_NOT_SIMPLEST`, `WRONG_ORDER`, `WRONG_VALUE`, `WRONG_FORM`, `WRONG_CHOICE`, `MALFORMED_RATIO`, `INCOMPLETE`, `RATIO_OK`, `not-a-ratio/malformed`, `order-reversed`, `reversed-order`, `zero-part`, `negative-part`, `malformed-ratio`, `unsupported-symbol`, a bare `wrong`, and a bare `partial` is **superseded and must not appear** in canonical output. The single legacy split `not-a-ratio/malformed` is renamed to `malformed-response`; partial credit for an equivalent-but-unsimplified answer is carried by the **separate boolean field `partial: true`** on `CheckResult`, never by a competing result code. The best-buy/choice checker uses exactly `correct`, `wrong-choice`, `malformed-response`; table-completion tasks reuse the platform's existing table-completion checker codes. The `MISC.RATIO.*` registry IDs in §10 are a separate namespace (diagnostic identifiers) and are never confused with these result codes. A string-scan test (`ratio-result-code-spelling.test.ts`, cross-referenced from §9) asserts no alternative casing/spelling of any result code appears in any oracle, mirror, fixture, or spec artifact.

The four public routines and their signatures (Python names; the TypeScript mirror uses the byte-identical camelCase names already shown):

| Routine | Python ↔ TypeScript | Purpose |
|---|---|---|
| `parse_ratio(raw) -> ParseResult` | `parseRatio(raw)` | anchored surface text → `{ parts:int[] \| null, code:ResultCode }` |
| `canonicalize_ratio(parts) -> int[]` | `canonicalizeRatio(parts)` | divide an integer tuple by `gcd`, preserve order |
| `format_ratio(parts) -> str` | `formatRatio(parts)` | canonical/any integer tuple → ASCII `a:b[:c]` display |
| `check_ratio(raw, expected) -> CheckResult` | `checkRatio(raw, expected)` | parse → equivalence under the task's simplest-form policy → `{ code, partial, feedback }` |

`ParseResult.parts` is the **raw parsed tuple** (the integers as written, e.g. `[4,6]` for `"4:6"`), NOT yet canonicalized; `canonicalize_ratio` is a separate, explicitly-invoked step so the checker can distinguish "equivalent but unsimplified" from "equivalent and simplest" (§5.6). All integers are plain JS numbers / Python `int`; values are bounded by the §11 parameter caps, so no `bigint`/overflow concern. **No floats, no `Rational`, no tolerance anywhere in this section** — ratio terms are positive integers only, and equivalence is decided by exact integer comparison of canonical (simplest-form) tuples.

### 5.1 The canonical answer value (parse target and storage)

The canonical value is the structured object defined in §4 and is, per the canonical-first precedent (the THIRD such contract after `quantity` and `transformation`), **itself `answer.canonical`** — there is no sibling `answer.ratio` field and the ratio is never stored twice:

```json
{ "type": "ratio", "canonical": { "parts": [2, 3] }, "display": "2:3" }
```

```json
{ "type": "ratio", "canonical": { "parts": [2, 3, 5] }, "display": "2:3:5" }
```

Canonical invariants (a tuple violating any of these is **not a legal canonical value**; the parser/checker returns a reject code, never an out-of-range canonical, mirroring the transformations parser):
- `parts.length ∈ {2, 3}` (v1.0.0 supports two-part and three-part ratios only; see §5.3 `wrong-number-of-parts`).
- every part is a **positive integer** ≥ 1 (zero and negative parts EXCLUDED in v1.0.0 → `zero-or-negative-part`).
- in **canonical (simplest) form**, `gcd(parts) == 1`.
- **ORDER MATTERS**: `[2,3]` and `[3,2]` are distinct canonical values; correspondence to context labels is positional and fixed by the prompt.
- ratio answers carry **NO units** and **NO `Rational`** — `parts` is a bare integer array.
- `display` is **derived** from `canonical.parts` by `format_ratio` (§5.4); the importer/exporter re-derives and asserts equality, so the formatted string is never an independent source of truth.

### 5.2 Parser — accepted human forms (anchored, finite grammar)

`parse_ratio` is a finite, **fully-anchored** recogniser: a single top-level regex, anchored `^…$` after normalization, so any unconsumed trailing text is a **hard reject** (mirrors `mensuration_units.parse_quantity` rejecting `"12 cm long"`, and the transformations parser rejecting unanchored trailing text). No backtracking, no fuzzy matching, no NLP, no locale dependence.

**Normalization (applied once, before matching):**

| Step | Action |
|---|---|
| trim | strip leading/trailing ASCII whitespace (`[ \t]`); a single internal run of spaces *around each colon* is permitted and collapsed (see grammar) |
| Unicode minus | `−` (U+2212) → `-` **only to produce a clean reject**: a leading `-` then triggers `zero-or-negative-part`, never silently dropped |
| ratio-colon decision | **U+2236 RATIO ( `∶` ) is NOT supported in v1.0.0** (decision below). It is mapped to the ASCII reject path and yields `malformed-response`, with feedback naming the supported separator. |
| other non-ASCII | any other non-ASCII glyph (smart quotes, `×`, fullwidth digits/colon `：` U+FF1A, `／`) → hard reject `malformed-response` |
| case | not applicable — ratio terms are digits only; no keyword lowercasing |

**Anchored grammar (single regex, conceptually):**

```
^ \s* <int> \s* : \s* <int> ( \s* : \s* <int> )? \s* $
<int> = -? [0-9]+            # the optional leading '-' is matched only to route it to zero-or-negative-part
```

| Input | Normalizes/parses to | `ParseResult` |
|---|---|---|
| `"2:3"` | `[2,3]` | `{ parts:[2,3], code:"ok" }` |
| `"2 : 3"` | spaces around colon collapsed | `{ parts:[2,3], code:"ok" }` |
| `"2:3:5"` | three-part | `{ parts:[2,3,5], code:"ok" }` |
| `" 2:3 "` | leading/trailing trim | `{ parts:[2,3], code:"ok" }` |
| `"4:6"` | parsed raw, NOT yet simplified | `{ parts:[4,6], code:"ok" }` |
| `"02:03"` | leading zeros in a positive integer accepted, value `[2,3]` | `{ parts:[2,3], code:"ok" }` |
| `"2/3"` | no colon → not a ratio surface form | `{ parts:null, code:"malformed-response" }` |
| `"2:3:5:7"` | four colon-terms, grammar caps at 3 | `{ parts:null, code:"wrong-number-of-parts" }` |
| `"2:"` / `":3"` / `"2::3"` | missing/empty term | `{ parts:null, code:"malformed-response" }` |
| `"2 to 3"` | unsupported separator word (word-form alias NOT supported in v1.0.0 — decision G) | `{ parts:null, code:"unsupported-term" }` |
| `"0:3"` | zero part | `{ parts:null, code:"zero-or-negative-part" }` |
| `"-2:3"` / `"2:-3"` | negative part | `{ parts:null, code:"zero-or-negative-part" }` |
| `"2:3x"` / `"2:3 apples"` | valid prefix + extra text | `{ parts:null, code:"unparsed-trailing-text" }` |
| `"2.5:3"` | non-integer term | `{ parts:null, code:"unsupported-term" }` |
| `"2∶3"` (U+2236) | unsupported ratio-colon glyph | `{ parts:null, code:"malformed-response" }` |
| `""` / `"   "` | empty | `{ parts:null, code:"malformed-response" }` |

**Decision — Unicode ratio colon (U+2236) and ratio-word "to":** v1.0.0 accepts **only the ASCII colon `:` (U+003A)** as the separator, with optional surrounding spaces. **U+2236 RATIO, fullwidth colon U+FF1A, the word `to` (the word-form alias is NOT included in v1.0.0 — decision G), slash `/`, and any other separator are NOT accepted.** Rationale: the brief instructs "Unicode colon-like symbols handled **only if explicitly supported**"; supporting them would require a second normalization path and a parity row per glyph for marginal pedagogical value, so v1.0.0 **explicitly excludes** them and routes them to a precise, well-localised reject (`unsupported-term` for the readable word `to`; `malformed-response` for non-ASCII glyphs) rather than a generic failure. This decision is recorded in the §15 schema/lifecycle plan and asserted by two negative rows in the §5.8 matrix.

**Reject ordering (deterministic, total).** When several faults could apply, the parser emits codes in this fixed precedence so Python and TS agree byte-for-byte:
1. empty / no colon / unbalanced separators → `malformed-response`
2. a recognised-but-unsupported separator/term shape (`to`, `2.5`, `2,3`) → `unsupported-term`
3. correct colon structure but wrong arity (≥4 terms, or 1 term) → `wrong-number-of-parts`
4. all terms parse as integers but one is `≤ 0` → `zero-or-negative-part`
5. a complete valid ratio prefix followed by extra characters → `unparsed-trailing-text`
6. otherwise → `ok` with the raw integer tuple.

### 5.3 Canonicalizer (integer tuple → simplest form, order preserved)

```
canonicalize_ratio(parts: int[]) -> int[]:
    g = gcd_of_all(parts)          # gcd over all (2 or 3) positive parts; >= 1
    return [p // g for p in parts] # order preserved exactly
```

`gcd_of_all` folds the standard Euclidean `gcd` (the same `gcd` used by `core/exact-math/rational.ts`, but applied to a tuple) left-to-right; for three parts, `gcd(gcd(a,b),c)`. Properties, all enforced and re-proved by the validator (§9):
- **Order is preserved** — `canonicalize_ratio([20,30]) == [2,3]`, `canonicalize_ratio([30,20]) == [3,2]`.
- **Idempotent** — `canonicalize_ratio(canonicalize_ratio(p)) == canonicalize_ratio(p)`.
- **Total on legal input** — input is already guaranteed all-positive integers by the parser; the canonicalizer is never called on zero/negative/non-integer tuples.
- Three-part example: `canonicalize_ratio([4,6,10]) == [2,3,5]`; `canonicalize_ratio([6,9,15]) == [2,3,5]`.

The generator stores `canonical.parts = canonicalize_ratio(intendedParts)` so `answer.canonical` is **always already simplest**; the unsimplified original is kept only in the §6 Ratio model (`originalParts`) for prompt/diagnostic use, never in the answer.

### 5.4 Formatter (canonical → ASCII display)

```
format_ratio(parts: int[]) -> str:
    return ":".join(str(p) for p in parts)   # ASCII colon, NO spaces, NO units
```

The inverse-presentation of the canonical tuple; one display string per tuple (mirrors `format_quantity` / the transformations formatter). Used for `answer.display`, worked-solution prose, and feedback. **ASCII-authoritative**: always a bare `a:b` or `a:b:c`, ASCII colon `U+003A`, **no surrounding spaces, no units, no thousands separators**. A KaTeX/Unicode prompt-rendering variant (e.g. an `\mathbin{:}` typeset form) MAY exist for the rendered *question*, but is NEVER used for the byte-parity `answer.display`. Round-trip law (asserted in golden + parity fixtures): `format_ratio(canonicalize_ratio(parse_ratio(s).parts)) == answer.display` for every accepted `s`.

### 5.5 Equivalence checker

`check_ratio(raw, expected) -> CheckResult` — the ratio twin of `mensuration_units.check_response`. `expected` is the generated, already-canonical structured value plus the task's **simplest-form policy flag** carried by the Ratio model (§6): `requireSimplest: boolean` and `ordered: boolean` (in v1.0.0 `ordered == true` for every task except the explicitly **unordered comparison** sub-case of Task 2 `write_from_quantities`, where the prompt declares the categories unordered).

**Single normative equivalence primitive (§6.3 is authoritative).** Ratio equivalence is decided in exactly ONE way throughout the family: two same-arity positive-integer tuples are equivalent **iff their canonical (simplest) forms are elementwise equal** — i.e. `canonicalize_ratio(p) == canonicalize_ratio(q)`. This is the single normative implementation defined in §6.3 (`ratio_equivalent`); the checker calls it and nothing else. The cross-multiplication identities (two-part `a*d == b*c`; three-part pairwise `a*e == b*d ∧ b*f == c*e ∧ a*f == c*d`) are presented here ONLY as the mathematical *justification* that elementwise-canonical-equality is exact and float-free — they are NOT a second code path and are NOT independently implemented in the checker. (Justification, three-part: because every part is `≥ 1`, `a*e == b*d` and `b*f == c*e` together force `a*f == c*d`, and the three together hold iff both tuples reduce to the same simplest form; for two parts `a*d == b*c` holds iff `canonicalize([a,b]) == canonicalize([c,d])`. Single-source check, multiple proofs.)

Procedure (deterministic, total):

1. `r = parse_ratio(raw)`. If `r.code != "ok"`, **return that reject code** with its §5.7 feedback (`partial` false) — no comparison occurs.
2. **Arity gate.** If `len(r.parts) != len(expected.parts)` → `wrong-number-of-parts` (e.g. a two-part answer to a three-part question).
3. **Order / equivalence.** Decide equivalence of the parsed raw tuple `r.parts` against `expected.parts` using the single primitive: `equivalent := ratio_equivalent(r.parts, expected.parts)` (= `canonicalize_ratio(r.parts) == canonicalize_ratio(expected.parts)`). Because the primitive is elementwise on simplest forms, it is order-sensitive by construction: `2:3` vs `3:2` are NOT equivalent (`[2,3] != [3,2]`).
   - If **not** equivalent: if `ordered` and the parsed tuple equals the expected tuple under some **permutation** (a reordering), return `wrong-order`; otherwise return `wrong-ratio`. The permutation check compares the **multiset of `canonicalize_ratio(r.parts)`** against the multiset of `expected.parts`, so `4:6` counts as a reordering of `3:2` only after simplification (`canonicalize([4,6]) == [2,3]`, the reversal of `[3,2]`).
4. **Simplest-form policy** (only reached when step 3 found the tuples **equivalent**):
   - If **`requireSimplest == false`** (simplification not required by the task): **accept any equivalent** → `correct` (`partial` false). `2:3`, `4:6`, `20:30` all score `correct` for an expected `2:3`.
   - If **`requireSimplest == true`** (the task tests/REQUIRES simplest form, e.g. Task 1 `simplify`): if `r.parts` is already simplest (`gcd_of_all(r.parts) == 1`, equivalently `canonicalize_ratio(r.parts) == r.parts`) → `correct` (`partial` false). If it is equivalent but `r.parts` was **not already simplest** (`gcd_of_all(r.parts) > 1`) → **`equivalent-not-simplified`** with `partial: true`, a partial-credit/partial-feedback code, NOT `correct` and NOT `wrong-ratio`.
5. **Unordered comparison sub-case** (`ordered == false`, the declared unordered `write_from_quantities` variant only): step 3's order-sensitivity is relaxed — equivalence is decided on the **sorted** canonical tuples (`sorted(canonicalize_ratio(r.parts)) == sorted(canonicalize_ratio(expected.parts))`), and `wrong-order` is never emitted (an unordered task cannot have a wrong order). This is the SINGLE place order is relaxed; every other task is strictly ordered.

**Per-task policy binding** (the `requireSimplest`/`ordered` flags are one machine-readable value per task in the §6/§11 single source of truth, keyed by the canonical §1.3 slug set, not re-decided in the checker):

| Task slug | `requireSimplest` | `ordered` | Equivalent-unsimplified result |
|---|---|---|---|
| `simplify` (Task 1) | **true** | true | `equivalent-not-simplified` (partial) |
| `write_from_quantities` (Task 2, default) | false | true | `correct` |
| `write_from_quantities` (Task 2, declared unordered variant) | false | **false** | `correct` (order ignored) |
| `fraction_to_ratio` (Task 4) | **true** | true | `equivalent-not-simplified` (partial) |
| `ratio_to_fraction`, `share_two_part`, `share_three_part`, `missing_part`, `direct_proportion`, `inverse_proportion`, `unit_rate`, `best_buy`, `simple_scale` (Tasks 3, 5–12 — ratio used as *input*, not the simplification target) | false | true | `correct` |

(Tasks 3 and 5–12 either do not collect a ratio answer at all, or accept any equivalent ratio as input; where a ratio is read it is canonicalised before use, so an unsimplified equivalent is `correct`.) Comparison is ALWAYS over canonical integer tuples; no string comparison, no float, no tolerance. Every accepted equivalent surface form of the correct answer scores `correct` (proven by §5.8); no merely-different tuple ever receives full correctness.

### 5.6 `equivalent-not-simplified` — exact semantics

This code exists to honour the brief's "equivalent-unsimplified rejected/partial-feedback when simplest form required" rule WITHOUT conflating it with a wrong answer. It is emitted **only** when `requireSimplest == true` AND the response is genuinely equivalent (per the §6.3 primitive) AND `gcd_of_all(r.parts) > 1`. It carries `partial: true` in `CheckResult` (scoring weight set by the objective; the checker reports the code, the harness assigns credit), and its feedback names the simplification step using only parsed/derived values (§5.7). It is the checker side of the `MISC.RATIO.EQUIVALENT_BUT_UNSIMPLIFIED_WHEN_SIMPLEST_REQUIRED` diagnostic (§10), whose predicted student response (`format_ratio(originalParts)`) the independent validator (§9) recomputes to confirm it yields exactly the result code `equivalent-not-simplified`.

### 5.7 Result-code vocabulary and targeted feedback

Closed `RESULT_CODES` tuple (Python tuple + byte-identical TS literal union), the ratio analogue of mensuration's reject-code set. These lowercase-hyphenated string literals are the SINGLE family-wide result-code vocabulary (per the normative note at the head of §5); §7.4, §9, and §10 reference these exact strings and no other casing. Every code is deterministic, reachable, and exercised by the §5.8 matrix and the §14 checker-evidence matrix. Feedback is generated **only** from displayed/parsed values (the parsed tuple, its canonical form, the expected display) — never internal symbols, never a manufactured wrong number.

```
RESULT_CODES = (
  "correct",
  "equivalent-not-simplified",
  "wrong-order",
  "wrong-ratio",
  "wrong-number-of-parts",
  "zero-or-negative-part",
  "unsupported-term",
  "unparsed-trailing-text",
  "malformed-response",
)
```

`equivalent-not-simplified` is **not** itself a partial/competing code: it is a distinct result code whose `CheckResult` additionally carries the boolean field **`partial: true`** when the task requires simplest form. `partial` is a separate boolean field, never a result code in its own right; there is no generic `wrong` or generic `partial` code in this vocabulary.

The **best-buy / choice** checker (§9 F, T11 `best_buy`) uses a separate, smaller closed vocabulary — **`correct`, `wrong-choice`, `malformed-response`** — keyed on the selected labelled option id; it never emits any ratio-parser code. **Table-completion** tasks (`share_two_part`, `share_three_part`) reuse the platform's existing table-completion checker codes (§7.4) and never force ratio-parser codes onto table answers. These three vocabularies (ratio-answer codes above; best-buy/choice codes; the platform table-completion codes) are the **only** result-code vocabularies in the family — there is no UPPER_SNAKE alias, no slash-style code, and no generic `wrong`/`partial` code anywhere.

| Code | Trigger | `partial` | Feedback (template; only parsed/derived values interpolated) |
|---|---|:--:|---|
| `correct` | equivalent under the task policy (and simplest, if required) | no | `Correct.` |
| `equivalent-not-simplified` | `requireSimplest`, equivalent, but `gcd_of_all(parts) > 1` | yes | `That ratio is equivalent, but not in simplest form. Divide every part by {gcd} to get {format_ratio(canonicalize_ratio(parts))}.` |
| `wrong-order` | same parts as expected after simplification, but in a different order (ordered task) | no | `You have the right parts, but the order does not match the question. The order should follow {the prompt's category order}.` |
| `wrong-ratio` | parses to a legal ratio of the right arity, not equivalent and not a reordering | no | `That is not equivalent to the correct ratio for this question.` |
| `wrong-number-of-parts` | legal terms, but arity ≠ expected (e.g. 2 vs 3, or ≥4 terms) | no | `This question needs a ratio with {expectedCount} parts; you gave {givenCount}.` |
| `zero-or-negative-part` | a parsed term is `0` or negative | no | `Ratio parts in this question are positive whole numbers. Check the part that is zero or negative.` |
| `unsupported-term` | recognised-but-unsupported separator/term shape (`to`, `2.5`, `2,3`) | no | `Write the ratio using whole numbers separated by a colon, for example 2:3.` |
| `unparsed-trailing-text` | a valid ratio prefix followed by extra characters | no | `I read {format_ratio(prefixParts)} but there is extra text after it. Give just the ratio, for example 2:3.` |
| `malformed-response` | empty / no colon / empty term / unbalanced colons / unsupported non-ASCII glyph (incl. U+2236) | no | `I could not read a ratio. Use whole numbers and a colon, for example 2:3 or 2:3:5.` |

`wrong-order`, `wrong-ratio`, `wrong-number-of-parts`, `zero-or-negative-part`, and `unsupported-term` are deliberately distinct from the catch-all `malformed-response` (mirroring mensuration's `missing-unit` / `wrong-base-unit` / `malformed-response` split): the response is well-formed enough to localise the fault, so the feedback names it. The `wrong-*` and `equivalent-not-simplified` codes also back the §10 `MISC.RATIO.*` group: a diagnostic whose predicted student answer parses to a specific tuple yields exactly the matching result code (the §10 `expectedResultCode`, drawn from this exact vocabulary), which the independent validator (§9) recomputes. Diagnostic-predicted ratios feed ONLY the checker, worked-solution pitfall notes, and the validator's diagnostic-recompute — never any student-channel SVG or accessibility field.

### 5.8 RATIO-CHECKER matrix (the brief's required cases)

Every row is a parity-fixture entry: the Python oracle and the TS mirror MUST return the identical `code` (and `partial`). Reproduced verbatim from the §14 review-pack RATIO-CHECKER matrix.

| # | `expected` (`parts`, policy) | Student `raw` | Required `code` (`partial`) |
|---|---|---|---|
| 1 | `[2,3]`, `requireSimplest=false` | `"4:6"` | `correct` (accepts 4:6) |
| 2 | `[2,3]`, `ordered=true` | `"3:2"` | `wrong-order` (rejects 3:2) |
| 3 | `[2,3,5]`, `requireSimplest=false` | `"4:6:10"` | `correct` (accepts 4:6:10) |
| 4 | `[2,3]`, `requireSimplest=true` (`simplify`) | `"4:6"` | `equivalent-not-simplified` (`partial`; rejected/partial when simplest required) |
| 5 | `[2,3]`, `requireSimplest=false` | `"2:3"` | `correct` (equivalent accepted, here already simplest) |
| 6 | `[2,3]`, any | `"0:3"` | `zero-or-negative-part` (ratio with zero part rejected) |
| 7 | `[2,3]`, any | `"-2:3"` | `zero-or-negative-part` (negative part rejected) |
| 8 | `[2,3]`, any | `"two:three"` / `"2;3"` | `malformed-response` (malformed ratio text rejected) |
| 9 | `[2,3]`, any | `"2:3 apples"` | `unparsed-trailing-text` (extra text rejected) |
| 10 | `[2,3]`, any | `"2 : 3"` | `correct` (spaces around colon accepted) |
| 11 | `[2,3]`, any | `"2∶3"` (U+2236) | `malformed-response` (Unicode colon-like handled only if explicitly supported — it is NOT in v1.0.0) |
| 12 | `[2,3]`, any | `"2 to 3"` | `unsupported-term` (the word "to" is not a supported separator in v1.0.0) |
| 13 | `[2,3,5]`, `ordered=true` | `"3:2:5"` | `wrong-order` |
| 14 | `[2,3]`, any | `"2:3:5"` | `wrong-number-of-parts` |
| 15 | `[2,3]`, `requireSimplest=false` | `"20:30"` | `correct` (20:30 ≡ 2:3) |
| 16 | `[2,3]`, any | `"5:7"` | `wrong-ratio` |

---

*Files referenced for this section (all absolute): `C:\Users\Mohamad Solaiman\OneDrive\Desktop\Claude Question generator\docs\GENERATOR_SPEC_proportion_ratio_PROPOSAL.md` (target output), with conventions matched against `docs\GENERATOR_SPEC_transformations_PROPOSAL.md` §8 and `docs\GENERATOR_SPEC_mensuration_PROPOSAL.md` §5, and the `gcd` semantics in `core\exact-math\rational.ts`.*

## 6. Exact proportional reasoning model

### 6.1 One exact engine, no floats anywhere

All proportional reasoning in `gen.proportion.ratio` is performed by a single exact arithmetic core, `core/proportion/ratio-math.ts` (Python oracle-of-record `oracle/spi_oracle/ratio_math.py`, authored FIRST and mirrored byte-for-byte). It operates on exactly two numeric types and **nothing else**:

- **integers** — plain JS `number` that satisfy `Number.isInteger`, bounded by the §11 parameter caps so they are exact (no `bigint`); and
- **reduced rationals** — the existing `core/exact-math/rational.ts` `Rational{num,den}` (den ≥ 1, reduced, `Rational.toJSON()` → `{num,den}`), the byte-identical mirror of Python `fractions.Fraction`. Confirmed API surface reused: `add/sub/mul/div/neg/abs/pow/equals/isInteger/isZero/cmpAbs/toJSON/toString`, the free `rat()` helper, and the static `Rational.from(value)`.

There is **no `Math.random`, no `parseFloat`, no `Number(x)/Number(y)`, no decimal literal, no epsilon, no tolerance, no rounding** in any reasoning path. Every comparison, equivalence test, and answer is decided by integer or `Rational` arithmetic that is identical across Python and TypeScript. A single grep-able guard — the lint rule `no-float-in-ratio-math` (§16) — forbids `.`-bearing numeric literals and the `Math` float surface (`Math.round/floor/ceil/trunc` and `Math.abs` on non-integers) inside `ratio-math.ts`/`ratio_math.py`. (`Math.abs` on integers is permitted — it is exact and is used only by `tupleGcd` over integer parts.) The §14 review pack proves, per the EXACT MATH convention, that no canonical answer in any of the 12 tasks is ever a float or an irrational.

This section defines the operations; §7 (sharing/table-completion) and §9 (solver/independent-validator) consume them; the canonical `Ratio` model fields they read are defined here in §6.2.

### 6.2 The canonical `Ratio` model and the exact value forms

The one seeded source of truth for a generated item is the immutable `RatioModel` record (Python `RatioModel` dataclass, frozen; TS `interface RatioModel`). Every artifact — prompt, figure, canonical answer, worked solution, diagnostics, parser/checker, review-pack coverage — is a pure function of it; no value is authored twice. Its `task` field is keyed by the **single canonical** `RATIO_TASKS` slug set (pinned once in §1.3, used verbatim here and in §3/§7/§9/§10/§11; the `_ratio`/`_unitary` spelling variants are banned everywhere):

```ts
// The ONE canonical task-slug set (§1.3). No alternative spelling appears anywhere.
type RatioTask =
  | "simplify"             // T1
  | "write_from_quantities"// T2
  | "ratio_to_fraction"    // T3
  | "fraction_to_ratio"    // T4
  | "share_two_part"       // T5
  | "share_three_part"     // T6
  | "missing_part"         // T7
  | "direct_proportion"    // T8  (unitary method; objective …DIRECT_PROPORTION.01)
  | "inverse_proportion"   // T9  (unitary method; objective …INVERSE_PROPORTION.01)
  | "unit_rate"            // T10
  | "best_buy"             // T11
  | "simple_scale";        // T12
```

Its proportional-reasoning fields:

```ts
type Q = { num: number; den: number };   // reduced Rational JSON, den ≥ 1 (core/exact-math/rational.ts)
type Int = number;                        // Number.isInteger, |x| ≤ §11 cap

// The single answer-shape tag — drives §3 interaction, §4 schema branch, §9 checker.
// Each value maps to exactly ONE live schema answer.type (no phantom "comparison" type).
type RatioAnswerShape =
  | "ratio"             // → answer.type "ratio"            (ordered simplest tuple; tasks 1,2,4)
  | "number"            // → answer.type "integer" | "exact-rational" (task 7 integer-only; 8,12 integer-or-rational; 9 integer-only; 10 exact-rational)
  | "fraction"          // → answer.type "exact-rational"   (part-of-whole, reduced; task 3)
  | "table-completion"  // → answer.type "table-completion" (labelled multi-part; tasks 5,6)
  | "choice";           // → answer.type "multiple-choice"  (best-buy ONLY; task 11)

interface RatioModel {
  task: RatioTask;                 // §3 slug; single-source OBJECTIVE_BY_TASK key
  answerShape: RatioAnswerShape;   // exactly one (§3 matrix)

  // --- the exact ratio core (present whenever a ratio participates) ---
  parts: Int[];                    // ORDERED given parts as posed (2 or 3 entries; all ≥ 1)
  simplest: Int[];                 // ORDERED simplest-form parts: parts / gcd(parts); gcd(simplest)=1
  scale: Int;                      // gcd(parts) — the factor by which `parts` exceeds `simplest`
  sumSimplest: Int;                // sum(simplest)  (total parts of the simplest ratio)
  ordered: true;                   // ORDER MATTERS in v1.0.0 unless task declares unordered (only 11/12 compare)

  // --- sharing / total-parts (tasks 5,6,7) ---
  whole?: Int;                     // the quantity shared (task 5,6) — must satisfy §6.5 divisibility
  shares?: Int[];                  // exact integer shares, index-aligned to `parts` (task 5,6)
  labels?: string[];               // category labels, index-aligned (table-completion correspondence, §7)
  knownIndex?: Int;                // task 7: which part is given
  knownValue?: Int;                // task 7: the given part's value
  missingValue?: Int;              // task 7: recovered missing part — INTEGER-ONLY in v1.0.0 (decision E / §6.5 D4); NEVER shown in the figure (§8)

  // --- unitary / direct / inverse / unit-rate / scale (tasks 8,9,10,12) ---
  quantity?: Int;                  // unitary basis count (e.g. "7 books")  (task 8,9,10)
  measure?: Int | Q;               // value attached to `quantity`          (task 8,10)
  unitRate?: Q;                    // exact one-unit value = measure/quantity (task 8,10)
  invariant?: Int;                 // inverse-proportion product q·v (task 9), an exact integer
  scaleFactor?: Q;                 // map/model scale as exact rational (task 12); direction-tagged
  scaleDir?: "up" | "down";        // task 12: model→real (up) vs real→model (down)

  // --- discrete-choice task (11 best-buy ONLY) carries exact witnesses, never a "comparison" canonical ---
  choiceOptions?: string[];        // ordered MC option labels (best-buy A/B…)
  choiceIndex?: Int;               // index of the correct option in `choiceOptions`
  rateWitness?: Q[];               // exact per-unit Rational rates carried for solution/feedback (task 11)
}
```

Exactness of each form:

| Field | Type | Construction | Exactness rule |
|---|---|---|---|
| `parts`, `simplest` | `Int[]` | as posed / reduced | all entries ≥ 1; `gcd(simplest)=1`; ORDER preserved |
| `scale` | `Int` | `gcd(parts)` | `scale ≥ 1`; `simplest[i]·scale = parts[i]` for all i |
| `shares` | `Int[]` | total-parts method (§6.4) | every entry an **exact integer**; `Σ shares = whole` (§6.6) |
| `missingValue` | `Int` | `onePart · parts[missingIndex]` (§6.3) | exact **integer** by §6.5 D4 (`parts[knownIndex] ∣ knownValue`); integer-only in v1.0.0 (decision E) — never a `Rational`, never a float |
| `unitRate` | `Q` | `measure / quantity` (§6.4) | reduced `Rational`; integer iff `quantity ∣ measure` |
| `invariant` | `Int` | `q1·v1` (§6.4) | exact integer; both inverse pairs reproduce it (§6.5) |
| `scaleFactor` | `Q` | reduced `Rational` (§6.4) | reduced; never a decimal |
| `rateWitness` | `Q[]` | `price / qty` reduced (§6.4) | reduced `Rational`; exact, used only for feedback |

`parts`/`simplest`/`shares`/`quantity`/`invariant`/`choiceIndex` are **integers**; `missingValue` is an **`Int`** (decision E, integer-only); `unitRate`/`scaleFactor`/`rateWitness` are **`Int`-or-`Rational`**; nothing is ever a float. The single discrete-choice task — **best-buy (11) only** — emits `answer.type "multiple-choice"` (a live enum member) with `choiceIndex`; there is **no `comparison` answer.type** anywhere — the exact per-unit rates live as `rateWitness` witnesses consumed by the worked solution and §10 diagnostics, never as a stored canonical (§4 owns the schema mapping; `ratio` remains the only NEW enum member the family adds). `simple_scale` (12) is a free-response **number** answer (decision C/D), not a choice.

### 6.3 gcd simplification and proportional equivalence

**gcd / simplification.** The canonicalizer uses the Euclidean `gcd` already shipped in `rational.ts` (private there) re-exported as `ratioGcd(a,b)` and folded over a tuple:

```ts
function tupleGcd(xs: Int[]): Int { return xs.reduce((g, x) => ratioGcd(g, Math.abs(x)), 0); }
function simplifyRatio(parts: Int[]): { simplest: Int[]; scale: Int } {
  const g = tupleGcd(parts);          // g ≥ 1 because every part ≥ 1 (zero/neg excluded, §12)
  return { simplest: parts.map(p => p / g), scale: g };
}
```

`simplifyRatio` is the **sole** producer of `simplest`/`scale`; `g` divides every part **exactly** by construction (it is their gcd), so `p / g` is always an integer — no rounding is possible. For a 3‑part ratio `gcd(a,b,c) = gcd(gcd(a,b),c)`, computed by the same fold. This is the engine behind task `simplify` (T1) and the canonical form of every ratio answer (§4).

**Proportional equivalence (the cross-multiplication law).** Two ratios are equal iff they share a simplest form. The single normative implementation is **elementwise equality of simplest forms** (§6.3 below); the integer cross-product identity is its mathematical *justification*, recorded in the worked solution and the §14 RATIO-CHECKER MATRIX, **not** a second decision path (this resolves the two-spellings concern: one code path, one justification):

> Justification: `a:b = c:d` ⟺ `a·d = b·c` (two-part); `a:b:c = d:e:f` ⟺ `a·e = b·d` **and** `b·f = c·e` (three-part; for positive parts the third adjacent product follows, so two suffice), all parts positive.

```ts
// NORMATIVE: two ratios are equivalent iff their simplest forms are elementwise identical.
function ratioEquivalent(p: Int[], q: Int[]): boolean {
  if (p.length !== q.length) return false;
  const { simplest: ps } = simplifyRatio(p);
  const { simplest: qs } = simplifyRatio(q);
  return ps.every((v, i) => v === qs[i]);   // ORDER MATTERS — elementwise, not as a set
}
```

`ratioEquivalent([2,3],[4,6]) = true`, `([2,3,5],[4,6,10]) = true`, `([2,3],[3,2]) = false` (order), `([20,30],[2,3]) = true`. Because the simplest form of a positive tuple is unique, `ratioEquivalent` is `true` iff the tuples are proportional in the SAME order; a mere reordering (e.g. `3:2` vs `2:3`) is correctly NOT equivalent and falls through to the `reverses_order` diagnostic branch (§10). Both the elementwise implementation and its cross-product justification are pure integer arithmetic.

Whether an **unsimplified** equivalent (e.g. `4:6` for a `2:3` answer) is *accepted* is a per-task policy decision, not a math decision: `ratioEquivalent` returns `true`, but tasks that test simplification (task `simplify`, and any task whose objective requires simplest form, §5) downgrade an equivalent-but-unsimplified response to the result code `equivalent-not-simplified` with the separate boolean `partial: true` (§5), while tasks that merely require *a correct ratio* accept it (`correct`). The math layer reports equivalence; §5/§9 apply policy with the single lower-kebab result-code vocabulary fixed in §5.

### 6.4 Total-parts, unitary, inverse, unit-rate, scale — the five exact procedures

All five are pure integer/`Rational` functions in `ratio-math.ts`; each is independently re-implemented by the §9 validator by a second route and cross-checked.

**(a) Total-parts sharing** (tasks `share_two_part`, `share_three_part`). Given `whole` and `parts`:

```ts
function shareTotalParts(whole: Int, parts: Int[]): Int[] {
  const T = parts.reduce((a, b) => a + b, 0);   // total parts
  // §6.5 GUARD: require T | whole exactly; generation never emits a violating case.
  if (whole % T !== 0) throw new Error("non-integer share — parameter-generation invariant violated");
  const unit = whole / T;                       // exact integer value of ONE part
  return parts.map(p => unit * p);              // each share an exact integer
}
```

`share = whole / Σparts · part`, computed as `unit·part` so the only division (`whole / T`) is **provably exact** by the §6.5 divisibility constraint. Shares are integers; the sum-agreement law `Σ shares = whole` is asserted (§6.6).

**(b) Unitary method — direct proportion** (`direct_proportion`, T8) and **unit rate** (`unit_rate`, T10). One unit is the exact `Rational` `measure/quantity`:

```ts
function unitRate(measure: Int, quantity: Int): Rational {  // tasks direct_proportion, unit_rate
  if (quantity === 0) throw new Error("zero quantity — generation invariant violated");
  return new Rational(measure, quantity);   // reduced; integer iff quantity | measure
}
function directScale(measure: Int, quantity: Int, target: Int): Rational {  // task direct_proportion
  return unitRate(measure, quantity).mul(new Rational(target, 1));  // exact
}
```

`direct_proportion` stays exact whether or not `quantity ∣ measure`; the answer is stored as `answer.type "integer"` when the product reduces to `den=1`, else `answer.type "exact-rational"` — the `answerShape:"number"` tag (§6.2) maps to whichever of those two live enum members the reduced value dictates (this is the integer-OR-rational primary-shape rule, kept consistent with §3.3/§9.4 `answer-type-consistency`). `unit_rate`'s answer is exactly `measure/quantity` reduced; **no decimal unit rate is ever produced** (brief constraint D).

**(c) Inverse proportion — product invariant** (`inverse_proportion`, T9, SIMPLE INTEGER cases only). The invariant `q·v` is constant:

```ts
function inverseProduct(q1: Int, v1: Int): Int { return q1 * v1; }     // the invariant k
function inverseSolveV(q1: Int, v1: Int, q2: Int): Int {               // task inverse_proportion
  const k = inverseProduct(q1, v1);
  // §6.5 GUARD: generation requires q2 | k so the result is an EXACT INTEGER.
  if (k % q2 !== 0) throw new Error("non-integer inverse result — generation invariant violated");
  return k / q2;
}
```

`q1·v1 = q2·v2`; v1.0.0 restricts `inverse_proportion` to cases where `q2 ∣ (q1·v1)` so `v2` is an exact integer (brief: "SIMPLE INTEGER cases only"). The answer is therefore always `answer.type "integer"`. Non-exact inverse results are an **edge case excluded by regeneration** (§12), never rounded.

**(d) Scale-factor consistency** (`simple_scale`, T12; simple map/model scale; NO similar-triangles geometry). The scale is one reduced `Rational` applied consistently in a tagged direction:

```ts
function applyScale(value: Int | Rational, factor: Rational, dir: "up" | "down"): Rational {
  const v = Rational.from(value);
  return dir === "up" ? v.mul(factor) : v.div(factor);   // exact; direction explicit (§12 trap)
}
```

`scaleDir` removes the "scale-factor-wrong-direction" ambiguity at the model level (the misconception `MISC.RATIO.SCALE_FACTOR_WRONG_DIRECTION` predicts the opposite-direction value, §10). Generation constrains parameters so `applyScale` yields the declared exact `Int`/`Rational` answer. `simple_scale` is **free-response-only** (decision C) and always asks for the **scaled numerical value** (decision D/I): `answerShape:"number"` applies and the answer is the exact `Int`/`Rational` above (`integer` when whole, else `exact-rational`). It is never posed as a direction multiple-choice item and never answered as a ratio in v1.0.0.

**(e) Best-buy / rate comparison** (`best_buy`, T11; NO currency conversion). Two rates are compared by exact `Rational` cross-multiplication, never by computing decimals:

```ts
function cheaperPerUnit(a: { price: Int; qty: Int }, b: { price: Int; qty: Int }): 0 | 1 | -1 {
  // compare a.price/a.qty vs b.price/b.qty by cross-product: a.price·b.qty vs b.price·a.qty
  const L = a.price * b.qty, R = b.price * a.qty;
  return L < R ? 0 : L > R ? 1 : -1;   // 0 ⇒ A cheaper, 1 ⇒ B cheaper, -1 ⇒ TIE
}
```

This reuses the exact cross-product idiom (cf. `Rational.cmpAbs`). The answer is the discrete `multiple-choice` option indexed by `choiceIndex` (the option with the **strict minimum** unit rate), with the exact per-unit `Rational` rates stored in `rateWitness` for the worked solution and feedback. A `TIE` (`L === R`) triggers a **deterministic redraw** (decision H / §12 best-buy ties): generation **excludes all ties** so the best value is always a strict minimum — there is no "same value" option in v1.0.0. Quantities/prices are unitless rate operands in a single currency — `best_buy` never converts currency or applies an exchange rate.

### 6.5 Divisibility constraints parameter generation MUST satisfy

Exactness is guaranteed at **generation time**, not patched at answer time. The seeded loop (§ generation) draws candidate parameters, then **rejects-and-redraws** any candidate violating the constraints below; the §9 validator re-asserts each as a post-condition, and `ratio-math.ts` throws (never rounds) if one is ever violated — a thrown invariant is a build-breaking bug, never a runtime fallback.

| # | Task(s) | Constraint | Why exact | On violation |
|---|---|---|---|---|
| D1 | all ratios | every part ≥ 1 (no zero, no negative) | gcd well-defined; positive cross-products | redraw (§12) |
| D2 | `simplify`, and simplest-required tasks | when simplification is *tested*, `gcd(parts) ≥ 2` | a non-trivial simplify step exists | redraw unless intentionally low-band (§11/§12) |
| D3 | `share_two_part`, `share_three_part` | `(Σ parts) ∣ whole` | `unit = whole/Σparts` is an exact integer | redraw `whole` to next multiple |
| D4 | `missing_part` | **HARD, non-optional:** `parts[knownIndex] ∣ knownValue` so `unit = knownValue / parts[knownIndex]` is an exact integer; then `missingValue = unit · parts[missingIndex]` is an exact integer too | recovered part is an **exact integer** — `missing_part` is integer-only in v1.0.0 | redraw (no escape hatch) |
| D5 | `direct_proportion`, `unit_rate` | answer-shape honoured: store `integer` when the reduced value has `den=1`, else `exact-rational`; never coerce | unit rate / scaled value is the declared exact form | (none — both branches exact) |
| D6 | `inverse_proportion` | `q2 ∣ (q1·v1)` **and** the pair are genuinely inverse (product constant) | `v2` is an exact integer ("simple integer cases only") | redraw |
| D7 | `simple_scale` | `scaleFactor` reduced; chosen so `applyScale` gives an exact `Int`/`Rational`; `scaleDir` set | no decimal scale, direction unambiguous | redraw |
| D8 | `best_buy` | **all rates distinct (strict minimum), no ties** (decision H); operands positive integers, single currency | exact cross-product decides; the best value is a unique strict minimum | redraw on any tie (§12 ties) |
| D9 | `ratio_to_fraction`, `fraction_to_ratio` | part-of-whole uses `Σ simplest` as denominator; for `fraction_to_ratio` the proper-fraction guard `0 < a < b` holds so the complement `[a, b−a]` has both parts ≥ 1 | fraction is `part/total`, not `part/otherPart`; complement is a valid positive ratio | enforced by construction (§7) |

**D4 is now a hard, non-optional integer guarantee** (resolving the earlier escape-hatch ambiguity): because `missing_part` declares `answer.type "integer"` only (§2.7/§3.3), generation MUST enforce `parts[knownIndex] ∣ knownValue`. With that single constraint, `unit = knownValue / parts[knownIndex]` is an exact integer and `missingValue = unit · parts[missingIndex]` is automatically an exact integer — so `missingValue` is **never a `Rational`** for `missing_part` in v1.0.0. (The `Int | Q` type on `missingValue` in §6.2 is the general field type; the §6.5 D4 contract pins it to `Int` for this task. Any future task that legitimately needs a rational recovered value would declare `exact-rational` in its own §3 row; none does in v1.0.0.)

D2 also prevents the "ratio already simplest when simplification is tested" degeneracy (§12); D3 prevents non-integer shares; D6 keeps inverse proportion in exact-integer territory per the brief; D5/D7 keep every unit-rate/scale answer an exact `Int` or reduced `Rational` (constraint D of the brief). These constraints are the **single declared contract** between §11 parameter generation and the exactness guarantees of this model.

### 6.6 Sum-agreement and consistency invariants (validator post-conditions)

Independently of generation, the §9 validator recomputes and asserts the following exact identities for every item (all integer or exact-`Rational` equalities — `Rational.equals`, never `==` on floats):

1. **Simplify invariant:** `simplest[i] · scale === parts[i]` for all `i`, and `tupleGcd(simplest) === 1`.
2. **Equivalence law:** `ratioEquivalent(parts, simplest) === true`; and the integer cross-product `parts[i]·simplest[j] === parts[j]·simplest[i]` for all `i,j` (the justification of clause 1, not a second decision path).
3. **Total-parts / sum-agreement** (`share_two_part`, `share_three_part`): `Σ shares === whole`, and `shares[i]/parts[i]` is the **same** `unit` integer for every `i` (`shares[i]·parts[j] === shares[j]·parts[i]`).
4. **Table-completion sum agreement** (§7): the labelled values, keyed by `labels` (correspondence by LABEL, not row order), sum exactly to `whole`; no labelled cell is a float.
5. **Missing-part** (`missing_part`): `parts[knownIndex] ∣ knownValue` (D4); `missingValue = (knownValue / parts[knownIndex]) · parts[missingIndex]` and `Number.isInteger(missingValue)`; reinserting `missingValue` reproduces a tuple proportional to `simplest` (cross-product check).
6. **Unit-rate / direct** (`direct_proportion`, `unit_rate`): `unitRate.mul(Rational.from(quantity)).equals(Rational.from(measure))`; the scaled answer equals `unitRate · target` exactly; the stored `answer.type` is `integer` iff the reduced value has `den===1`, else `exact-rational`.
7. **Inverse invariant** (`inverse_proportion`): `q1·v1 === q2·v2 === invariant`, all integers.
8. **Scale consistency** (`simple_scale`): applying `scaleFactor` in `scaleDir` to the given value yields the stored exact answer; applying it to a second corresponding pair reproduces the same factor (`Rational.equals`); for a direction MC item, `choiceOptions[choiceIndex]` matches `scaleDir`.
9. **Best-buy** (`best_buy`): `choiceIndex` equals the option with the **strict minimum** unit rate per `cheaperPerUnit(...)`; the carried `rateWitness` per-unit `Rational` rates are reduced and reproduce the comparison; ties are unreachable (deterministic redraw, decision H), so the keyed option is always the unique strict minimum.

Any failure is a hard error (build-breaking), surfaced by the §9 closure-agreement check, never tolerated and never rounded away. This is the exact-arithmetic backbone on which §5 (checker result codes), §7 (sharing/table model), and §9 (independent validation) all rest; it introduces nothing outside v1.0.0 scope and touches no deferred topic (no percentages, currency conversion, compound proportion, recipe-with-units, similar-triangle scale, gradient, irrational, or decimal-ratio terms). It also adds **no new schema answer.type**: the one discrete-choice task — best-buy (11) — reuses the live `multiple-choice` enum member, so `ratio` remains the family's single additive enum member (§4/§15).

---

Relevant file paths referenced (all absolute):
- `C:\Users\Mohamad Solaiman\OneDrive\Desktop\Claude Question generator\core\exact-math\rational.ts` — the existing `Rational{num,den}` type this section reuses (verified API: `add/sub/mul/div/neg/abs/pow/equals/isInteger/isZero/cmpAbs/toJSON/toString`, free `rat()`, static `Rational.from`; reduced, `den ≥ 1`).
- `C:\Users\Mohamad Solaiman\OneDrive\Desktop\Claude Question generator\schemas\question-item.schema.json` — confirmed `multiple-choice`, `table-completion`, `integer`, `exact-rational`, `fraction` are live `answerType` enum members and `comparison` is NOT, justifying the best-buy/scale-direction retargeting onto `multiple-choice`.
- Proposed new files this section specifies (NOT created — proposal only): `C:\Users\Mohamad Solaiman\OneDrive\Desktop\Claude Question generator\core\proportion\ratio-math.ts` and oracle-of-record `C:\Users\Mohamad Solaiman\OneDrive\Desktop\Claude Question generator\oracle\spi_oracle\ratio_math.py`.

Summary of blocker fixes applied to Section 6:
- **Slug set (B3/B1 across critics):** pinned the single canonical `RatioTask` set from §1.3 (`simplify`, `write_from_quantities`, `direct_proportion`, `inverse_proportion`, `unit_rate`, `best_buy`, `simple_scale`, etc.); removed every `_unitary`/`_ratio` variant from comments and prose.
- **`comparison` phantom answer.type (platform-fit B1 / completeness B3):** dropped `"comparison"` from `RatioAnswerShape`; best-buy and scale-direction now map to the live `multiple-choice` answer.type via a `"choice"` shape with `choiceOptions`/`choiceIndex`/`rateWitness` witnesses. Verified against the schema enum that `comparison` is absent and `multiple-choice` is present. `ratio` stays the only new enum member.
- **Missing-part divisibility (ratio-math B1/B2):** D4 is now a hard, non-optional integer guarantee (`parts[knownIndex] ∣ knownValue`), making `missing_part` exact-integer-only with no escape hatch; §6.6 clause 5 re-asserts it.
- **`direct_proportion` answer-type drift (ratio-math I2):** `answerShape:"number"` explicitly maps to `integer` when `den===1` else `exact-rational`, consistent with §3.3/§9.4.
- **One three-part equivalence form (ratio-math I6):** elementwise-simplest-form is the single normative path; cross-product is justification only.
- Confirmed no deferred topic is introduced.

## 7. Sharing and table-completion model

This section specifies how `gen.proportion.ratio` v1.0.0 turns a **share-in-a-ratio** instruction into (a) exact integer shares, (b) a label-keyed **table-completion** answer when the student reports more than one value, and (c) the **missing-part-from-known-part** computation. It defines how the one canonical **Ratio model** (Section 6) carries the *known* and *missing* parts, the per-position **context labels**, and the **answer-shape tag**, and it pins the deterministic worked-solution structure (`total parts → one-part value → each share → sum check`). Nothing here introduces a new answer container: sharing and missing-part reuse the **already-approved** `table-completion` and exact `integer` answer types exactly as data-handling and transformations use them; only the new `answer.type:"ratio"` (Section 4) is family-new, and it is **not** used for sharing outputs (a *share* is a quantity, not a ratio). The percentage, recipe-with-units, compound-proportion, and currency deferrals (Owner Brief DEFER list) are unreachable here: the share total and every part are exact integers with no unit conversion.

### 7.1 Tasks covered by this section

This section owns three of the twelve canonical tasks. It uses the **single canonical slug set** declared in §1.3 and the **single canonical objective-ID set** declared in §1.2 (pattern `SPI.MIDDLE.RATIO.<MICRO>.01`, no `_UNITARY`/`_ratio`/abbreviated variants anywhere). No alternative spelling of any slug or objective ID appears in this section; the `ratio-graph.test.ts` string-scan (`keys() == RATIO_TASKS`, "no alternative spelling appears anywhere") passes against this section verbatim.

| Task slug (§1.3 / §3) | Objective ID (§1.2) | What the student produces | `answer.type` | `answerShapeTag` (Section 6 field) |
|---|---|---|---|---|
| `share_two_part` | `SPI.MIDDLE.RATIO.SHARE_TWO_PART.01` | the two shares, labelled | `table-completion` | `table-completion` |
| `share_three_part` | `SPI.MIDDLE.RATIO.SHARE_THREE_PART.01` | the three shares, labelled | `table-completion` | `table-completion` |
| `missing_part` | `SPI.MIDDLE.RATIO.MISSING_PART.01` | the single unknown part's quantity | `integer` | `number` |

`share_two_part` and `share_three_part` are **free-response, table-completion** because the student must supply **every** share keyed to its label (the owner brief: *correspondence by LABEL, not row order alone — Ali→12, Ben→18, Cara→30*). `missing_part` asks for **one** value and so uses a single exact `integer` answer (`answerShapeTag:"number"`), not a one-cell table — a single scalar does not need label correspondence. The `missing_part` `answer.type` is **`integer` only**, with no `exact-rational` alternative, because §7.5's divisibility precondition is a hard, non-optional admission rule that guarantees an integer result (this matches §2.7/§3.3 exactly and resolves the cross-cluster type question in favour of integer-only). This keeps the contract minimal: the table machinery is used only when there is genuinely more than one labelled blank.

> **MC eligibility.** All three are FR-first. `missing_part` MAY additionally offer `multiple-choice` when (and only when) three distinct misconception-backed distractors exist (Section 10: `MISC.RATIO.DIVIDES_BY_ONE_PART_INSTEAD_OF_TOTAL`, `MISC.RATIO.WRONG_TOTAL_PARTS`, `MISC.RATIO.MULTIPLIES_INSTEAD_OF_DIVIDING_IN_UNITARY` recomputed distinct over the integers); an explicit MC request on the two share tasks is **never silently downgraded** — the generator returns the standard `interaction-not-supported` error (`share_*` are FR-only, mirroring data-handling's `complete_frequency_table`).

### 7.2 How the canonical Ratio model carries known/missing parts and labels

The single `Ratio` model (Section 6) already holds the ordered simplified `parts`, `total = Σ parts`, and a parallel `labels[]` (positional, `len(labels) == len(parts)`). Sharing and missing-part add **only** the fields the brief enumerates; no second ratio object is created.

```jsonc
// RatioModel — the share/missing-part-relevant fields (full model in Section 6)
{
  "parts":      [2, 3],                 // ordered, simplest form, gcd(parts)=1, positive ints
  "labels":     ["Ali", "Ben"],         // positional context labels; labels[i] owns parts[i]
  "total":      50,                      // the QUANTITY being shared (a.k.a. shareTotal); integer
  "totalParts": 5,                       // Σ parts (the divisor in the unitary step)
  "onePart":    { "num": 10, "den": 1 },// total / totalParts as exact Rational (Section 6 type)
  "shares":     [ ... ],                 // computed; see §7.4 — what the student must produce
  "known":      null,                    // {index, value} for missing_part ONLY; null otherwise
  "missing":    null,                    // {index} for missing_part ONLY; null otherwise
  "answerShapeTag": "table-completion"   // "table-completion" | "number"
}
```

Rules, identical across Python oracle (`oracle/spi_oracle/proportion_ratio.py`) and the TS mirror (`domains/proportion-ratio/`):

- **Labels are positional and authoritative.** `labels[i]` names `parts[i]`; correspondence everywhere (answer cells, bar-model segments, double-number-line rows, worked solution, diagnostics) is **by label, never by array index alone** at the answer boundary. Labels are drawn from a deterministic context pool (e.g. people `Ali/Ben/Cara`, or roles `red/blue/green`), are **distinct** within an item, and are **byte-pinned** so the label appearing in `params.labels[i]`, the SVG `<text>`, the a11y text, and the answer `cell.location` are byte-for-byte identical Py↔TS (the prime-glyph byte-pinning discipline from transformations applies generally to any label glyph; ASCII labels in v1.0.0 avoid that hazard entirely but the rule stands).
- **`known` / `missing` are populated ONLY for `missing_part`.** For `share_*` both are `null` (the student must find *every* share, so nothing is "known" beyond the ratio and the total). For `missing_part` the *total is NOT given*; instead one part's **quantity** is given (`known = {index, value}`, an exact integer) and the student finds the other part's quantity (`missing = {index}`). See §7.5.
- **`shares` is derived, never a second source of truth.** It is recomputed by the independent validator (Section 9) from `parts`, `labels`, and `total`; storing it is a convenience for the renderer and answer-builder, and a validator check (`shares-recompute-agrees`, Section 9) asserts the stored `shares` equal the recomputation.

### 7.3 The `answerShapeTag` selection rule (single source)

`answerShapeTag` is set **once**, deterministically, by task, in the ONE machine-readable task table (Section 3 / Section 11 source of truth) — never inferred ad hoc by the renderer or checker:

| Condition | `answerShapeTag` | `answer.type` |
|---|---|---|
| task ∈ {`share_two_part`, `share_three_part`} | `table-completion` | `table-completion` |
| task == `missing_part` | `number` | `integer` |
| (other ratio tasks, Sections 4–6) | `ratio` / `fraction` / `choice` | per that section |

The tag is **answer-shape metadata only** (it selects the cell-vs-scalar answer builder and the checker dispatch); it is *not* a difficulty input and *not* duplicated inside `answer`. A validator check `answer-shape-tag-consistent` (Section 9) asserts `(answerShapeTag, answer.type)` is one of the rows above for every emitted item. (The `choice` row belongs to best-buy and is owned by §6.2; its final `answer.type` realisation is the live `multiple-choice` enum member, fixed in §4/§15. **There is NO `comparison` answer type anywhere in this family.** This section neither emits nor depends on best-buy; the row is shown only to make the table total over all tasks.)

### 7.4 Sharing: exact computation and the table-completion answer

**Divisibility precondition (enforced at generation, not at check time).** A share item is admitted only if `total` is an exact integer multiple of `totalParts`, i.e. `total mod totalParts == 0`. The seeded loop draws `total = totalParts * k` for an integer `k` in the band-appropriate range, so **every** share is an exact integer and `onePart.den == 1`; no rounding, no remainder, no float ever arises. (Items where `totalParts ∤ total` are excluded and regenerated — Section 12 edge-case `non-integer-share-excluded`.) This is why no approximate-decimal answer can occur, satisfying Owner Brief contract D.

**Computation (two-part shown; three-part identical with one more part):**

```
totalParts = Σ parts                      // e.g. 2 + 3 = 5
onePart    = total / totalParts           // exact integer k  (e.g. 48 / 5 is EXCLUDED; 50/5 = 10 admitted)
share[i]   = parts[i] * onePart           // e.g. [2·10, 3·10] = [20, 30]
sumCheck   = Σ share[i] == total          // MUST hold: 20 + 30 == 50  ✓
```

**Answer encoding — reuses the approved `table-completion` container** (`{cells:[{location,value}]}`), with `location` = the **context label** and `value` = an exact Rational with `den == 1`:

```jsonc
// share_three_part — total 60 shared as Ali:Ben:Cara = 2:3:5
"answer": {
  "type": "table-completion",
  "canonical": {
    "cells": [
      { "location": "Ali",  "value": { "num": 12, "den": 1 } },
      { "location": "Ben",  "value": { "num": 18, "den": 1 } },
      { "location": "Cara", "value": { "num": 30, "den": 1 } }
    ]
  },
  "display": "Ali = 12; Ben = 18; Cara = 30"   // DERIVED: labels in canonical source order
}
```

Contract details (all mirror data-handling's table-completion / transformations' shape-image table precisely — verified against the live schema: `table-completion` is an `answerType` enum member at line 203 of `schemas/question-item.schema.json` with **no** `if/then` `cells` constraint, so this answer validates under the runtime Ajv validator and the Python conformance checker with **zero** schema edit):

- **`location` is the label, not a row index** — the checker matches student rows to canonical rows **by `location`**; a student who answers `Cara` before `Ali` is **correct**. The validator's `share-label-correspondence` check keys on `location` (the direct analogue of transformations' `vertex-label-correspondence`).
- **`value` is an exact Rational with `den == 1`** (one uniform encoding; reuses `core/exact-math/rational.ts`, confirmed reduced with `den >= 1`). Because shares are guaranteed integral (§7.4 precondition), `den` is always `1`; an `answer-type-consistency` check asserts `integer-valued ⇔ den === 1` exactly as data-handling does for the mean.
- **Cell count == number of parts** (2 or 3) — variable-length `cells[]`, no padding, no empty cells. There is no "total" cell: the total is **given** in the prompt for share tasks, so it is never a blank.
- **Per-cell partial diagnosis.** A wrong single cell yields per-label feedback (which person got the wrong amount) and feeds the misconception adapters' predicted per-label responses (Section 10) — e.g. `MISC.RATIO.REVERSES_ORDER` predicts the exact swapped assignment `{Ali:18, Ben:12}` for a two-part share, not an arbitrary nearby number.
- **No schema delta.** The checker, not the schema, validates the `cells` shape (verified the same way data-handling verified it; an integer-valued cell needs no `if/then` block).
- **Result codes — table-completion tasks reuse the platform's EXISTING table-completion checker codes (decision F); the ratio-parser codes of Section 5 are NOT forced onto table answers.** The share tasks dispatch to the platform's approved `table-completion` checker (the data-handling precedent) and surface its codes unchanged — per-cell correct / incorrect against the canonical label→value map, with per-label partial feedback carried by the platform checker's own partial mechanism (a boolean partial flag, not a competing result code). A reversed-label assignment (the `MISC.RATIO.REVERSES_ORDER` signature — the right multiset of values bound to the wrong labels) is reported by that checker's existing wrong-assignment path. The single shared **`malformed-response`** token (Section 5) is the one ratio-family code the table dispatch reuses for a structurally unreadable cell (a non-integer / negative / unparseable cell, or a `location` not in the item's label set). This section introduces **no** `order-reversed`, `MALFORMED_RATIO`, generic `wrong`, generic `partial`, or any UPPER_SNAKE / slash-style variant. (Misconception **IDs** remain `MISC.RATIO.*` UPPER_SNAKE per Section 10; result **codes** remain lower-kebab — two distinct, non-overlapping vocabularies.)

### 7.5 Missing-part-from-known-part

`missing_part` gives the ratio, **one part's quantity** (`known`), and asks for **another part's quantity** (`missing`). The total is **not** given (that is what distinguishes it from sharing). The exact method is the unitary step applied to the *known* part:

```
known   = { index: i, value: v }          // e.g. parts = [3,5], labels = ["paint","water"], known = {index:0, value:9}
onePart = v / parts[i]                     // 9 / 3 = 3      (exact; admitted ONLY if parts[i] | v)
missing.value = parts[j] * onePart         // j = missing.index = 1 → 5 · 3 = 15
```

- **Admission precondition — HARD, NON-OPTIONAL (no escape hatch).** A `missing_part` item is admitted **only if** `parts[known.index]` exactly divides `known.value` (`parts[i] | v`). This is a generation-time invariant, not a parenthetical fallback: the seeded loop draws `known.value = parts[i] * onePart` for an integer `onePart` in the band-appropriate range (the construction *guarantees* divisibility), and the validator independently re-asserts `v mod parts[i] == 0` and rejects any item that violates it. Because `onePart` is then an integer, `missing.value = parts[j] * onePart` is automatically an exact integer. There is therefore **no reachable** non-integer `missing_part` result, and `answer.type` is `integer` with no `exact-rational` path (resolving ratio-math B1/B2: the integer guarantee is genuinely pinned, and §2.7/§3.3/§7.5/§9/§11 all agree on `integer`). Items that would yield a non-integer are unreachable from the loop and, defensively, excluded and regenerated (Section 12 `non-integer-share-excluded`). No float, no rounding.
- **Answer encoding — single exact `integer`** (`answerShapeTag:"number"`), NOT a one-cell table:

```jsonc
// missing_part — paint:water = 3:5, 9 L of paint, find water
"answer": { "type": "integer", "canonical": { "num": 15, "den": 1 }, "display": "15" }
```

- The known label/value pair lives in `params` and the prompt (and is shown in the bar model / double number line, §8) — it is **never** revealed as the answer, and the *missing* segment is rendered as an explicitly unknown cell (Section 8's known/unknown distinction). Leakage is judged by **element role/class** (Section 8's role-keyed `only-given-values-shown` guard), not by a numeric value test: the student figure carries no `.cx-ans` element and no unknown-segment value, so the value `15` never appears in the student asset even when it happens to coincide with a drawn given.
- **Diagnostics** target this method exactly: `MISC.RATIO.DIVIDES_BY_ONE_PART_INSTEAD_OF_TOTAL` (uses `total/parts[i]`-style reasoning where no total exists), `MISC.RATIO.MULTIPLIES_INSTEAD_OF_DIVIDING_IN_UNITARY` (computes `v · parts[j]` = `9·5 = 45`), and `MISC.RATIO.WRONG_TOTAL_PARTS` (Section 10) — each an **exact predicted formula**, recomputed distinct from the key, never a nearby guess.

### 7.6 Worked-solution structure (deterministic, single template)

The worked solution for all three tasks follows ONE fixed sequence, emitted as ordered `solution.steps[{number, transformation, intermediateResult}]` (the approved step shape from mensuration/transformations), built from the same `Ratio` model fields — so the prompt, answer, figure, and solution can never disagree:

**Sharing (`share_two_part`, `share_three_part`):**

| # | `transformation` (narration template) | `intermediateResult` |
|---|---|---|
| 1 | **Total parts** — add the ratio parts: `2 + 3 + 5` | `totalParts = 10` |
| 2 | **One part** — divide the amount by the total parts: `60 ÷ 10` | `onePart = 6` |
| 3 | **Each share** — multiply each ratio part by one part: `Ali 2·6, Ben 3·6, Cara 5·6` | `Ali = 12; Ben = 18; Cara = 30` |
| 4 | **Sum check** — add the shares back: `12 + 18 + 30` | `= 60 ✓ (equals the amount shared)` |

**Missing-part (`missing_part`):**

| # | `transformation` | `intermediateResult` |
|---|---|---|
| 1 | **One part** — divide the known quantity by its ratio part: `9 ÷ 3` | `onePart = 3` |
| 2 | **Missing part** — multiply the wanted ratio part by one part: `5 · 3` | `missing = 15` |
| 3 | **Consistency check** — known and found agree with the ratio: `9 : 15 = 3 : 5` | `✓` |

The **sum check (step 4 / consistency check)** is a *required, asserted* step, not decoration. The independent validator (Section 9) recomputes it: `share-sum-reconciles` asserts `Σ shares == total` for share tasks, and `share-ratio-reconciles` asserts `known.value : missing.value` simplifies to `parts[known.index] : parts[missing.index]` for missing-part; `answer-solution-agrees` asserts the final step's `intermediateResult` equals `answer.display` (verbatim the mensuration check). If any reconciliation fails the item is rejected at generation — it can never be emitted at `machine-validated`. (Check names here use Section 9's single `checks[]` vocabulary verbatim; no alternative spelling is introduced.)

### 7.7 What this section deliberately does NOT do (scope guard)

- No share total is expressed as a percentage, currency amount, or unit-bearing recipe quantity (DEFER list) — `total` is a bare integer count of a single quantity named only in prose.
- No share produces a non-integer or rational value: the divisibility preconditions (§7.4, §7.5) make every share and every missing part an exact integer; rational *answers* belong to the unit-rate / scale tasks (Section 6, contract D), not to sharing.
- A *share* is never encoded as a `ratio` answer: the output of sharing is one or more **quantities**, so it uses `table-completion` (multi-label) or `integer` (single), reserving `answer.type:"ratio"` (Section 4) for tasks whose answer genuinely *is* a ratio (simplify, write-from-quantities, fraction→ratio).
- No table-completion cell is ever underdetermined: every blank cell in a share answer is uniquely fixed by `parts`, `labels`, and `total`, so the answer set is always a total function from the item's label set to integers.

---

Revised Section 7 above is the implementation-ready replacement for `docs/GENERATOR_SPEC_proportion_ratio_PROPOSAL.md` Section 7 (cluster E-sharing-table).

Blockers/improvements fixed within my scope:
- **Result-code vocabulary (decision F)** — §7.4 no longer introduces `order-reversed`/generic `partial`/generic `wrong`/`malformed`/`not-a-ratio/malformed`. Table-completion (sharing) tasks reuse the **platform's existing table-completion checker codes** unchanged; the only ratio-family code reused is the single lower-kebab `malformed-response` for a structurally unreadable cell. Result-codes (Section 5) and misconception IDs (Section 10) are two distinct non-overlapping vocabularies.
- **Missing-part type contradiction + soft divisibility (ratio-math B1/B2)** — §7.1 and §7.5 pin `missing_part` to `integer` only and make the `parts[i] | v` divisibility precondition a HARD, non-optional generation invariant (loop construction guarantees it, validator re-asserts it), removing the escape hatch so a non-integer result is unreachable; this aligns §2.7/§3.3/§7/§9/§11 on `integer`.
- **Slug / objective-ID drift (completeness B1/B2, ratio-math B3, platform-fit B2)** — §7.1 reaffirms the canonical §1.3 slug set (`share_two_part`, `share_three_part`, `missing_part`) and §1.2 objective IDs (no `_UNITARY`/`_ratio`/abbreviated variants); no banned spelling appears.
- **Value-based vs role-based leakage (renderer B5)** — §7.5's figure cross-reference is now role-keyed (defers to Section 8's `only-given-values-shown` role/class guard), dropping any implication of a numeric value test.

Cross-section dependencies my draft assumes (unchanged, consistent with the brief and prior families): canonical `RatioModel` fields `parts/labels/total/totalParts/onePart/shares/known/missing/answerShapeTag` (Section 6); `answer.type:"ratio"` reserved for true-ratio answers only, NOT shares (Section 4); the shared Section 5 lower-kebab result-code vocabulary (`correct`, `equivalent-not-simplified` + boolean `partial`, `wrong-order`, `wrong-ratio`, `wrong-number-of-parts`, `zero-or-negative-part`, `unsupported-term`, `unparsed-trailing-text`, `malformed-response`) for ratio answers, and the platform's existing table-completion checker codes for the share tasks (decision F); Section 9 check names `shares-recompute-agrees/share-label-correspondence/answer-shape-tag-consistent/answer-type-consistency/share-sum-reconciles/share-ratio-reconciles/answer-solution-agrees`; and `MISC.RATIO.*` IDs `REVERSES_ORDER`, `DIVIDES_BY_ONE_PART_INSTEAD_OF_TOTAL`, `WRONG_TOTAL_PARTS`, `MULTIPLIES_INSTEAD_OF_DIVIDING_IN_UNITARY` (Section 10). Verified against the live repo: `table-completion` and `multiple-choice` are enum members and `comparison` is not (schema lines 196–205); `table-completion` has no `if/then` `cells` constraint (zero schema delta); the `transformation` canonical-first `if/then/const` precedent with `units/measure/tolerance:false` exists at lines 286–313; `core/exact-math/rational.ts` is reduced with `den >= 1`.

## 8. Bar-model / double-number-line renderer contract

This section specifies the canonical, byte-identical **non-Cartesian** diagram system for `gen.proportion.ratio`. It is the architectural purpose **(5)** of v1.0.0: prove a clean educational diagram model — **bar models**, **double number lines**, and **proportional tables** — that is *not* a coordinate plane, while reusing every approved rendering *mechanism* without modifying any shared theme. It reuses, by name and verbatim, the canonical-SVG discipline proven in the shipped renderers (`domains/geometry/angles.ts`, `domains/geometry/coordinate-lines.ts`, `domains/statistics/data-handling.ts`, `domains/measurement/mensuration.ts`): a hand-rolled deterministic serializer, integer coordinates via `gridRound` over exact `Rational`, byte-for-byte Python↔TypeScript output, a single `role="img"` root with `<title>`/`<desc>` children, per-figure namespaced ids, a per-figure data-table fallback, and **no colour-only information**. It adds the bar/number-line/table primitives the family needs as a **new additive theme extension** (`core/visual-style/ratio-theme.{json,ts}`, §8.2) — exactly the way `data-chart-theme` and `mensuration-theme` added their primitives — so the approved `cartesian-theme`, `data-chart-theme`, `mensuration-theme`, and `transformations-theme` outputs stay byte-for-byte unchanged.

There are **two render channels** built from the same `RatioModel` (§6) and `SharingModel` (§7): the **student figure** (shown to the learner; *given* quantities only, missing values **hidden**) and the **answer-key figure** (an additive answer overlay used ONLY in answer-key / solution export channels). Both are pure functions of `params` through the model; neither is authored independently. Both are composed from ONE canonical **base-diagram** fragment plus shared student annotations: the **student SVG** = root + base diagram + student annotations + closing tag; the **answer-key SVG** = root + the **byte-identical** base diagram + the same student annotations + one additive **answer-overlay** group + closing tag. The base diagram is byte-identical across channels and the overlay is purely additive (it never alters or reorders any student element), enforced by `answer-key-base-diagram-identical` and `answer-key-overlay-additive-only` (§8.11).

The twelve task slugs used throughout are the single canonical `RATIO_TASKS` set fixed in §1.3/§3 — `simplify`, `write_from_quantities`, `ratio_to_fraction`, `fraction_to_ratio`, `share_two_part`, `share_three_part`, `missing_part`, `direct_proportion`, `inverse_proportion`, `unit_rate`, `best_buy`, `simple_scale` — and no alternative spelling (`simplify_ratio`, `write_ratio`, `direct_proportion_unitary`, …) appears anywhere in this section. The render distinctions below are keyed off those slugs; not every task requires a figure (text-only tasks ship no `media[]` entry — see §8.10).

### 8.1 Canvas, coordinate system, and the pipeline

```
params (SSoT) ─▶ RatioModel / SharingModel (exact Rational parts + labels + given/unknown flags)
              ─▶ layout (integer band/lane allocation into the plotting box; no float fit-to-view)
              ─▶ gridRound (one rounding rule, exact Rational → int)
              ─▶ canonicalRatioSvg(model, diagramKind)  ─▶ media[].svg              (student)
                 canonicalRatioSvgOverlay(...)           ─▶ media[].svg (key/soln channels only)
                 ratioTableHtml(model) / ratioTableFallback(model) ─▶ media[].html + media[].dataTableFallback
        └──────────── identical bytes in oracle (Python) and production (TypeScript) ────────────┘
```

| Item | Value |
| --- | --- |
| `viewBox` | constant `"0 0 1000 700"` (`VIEW_W=1000, VIEW_H=700`, matching `angles.ts`/`coordinate-lines.ts`/`data-handling.ts`/`mensuration.ts`); never computed, never per-item |
| Canonical root element (the `media[0].svg` greyscale figure) | `<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1000 700" role="img" aria-label="{esc(alt)}">` immediately followed by children `<title>{esc(title)}</title>`, `<desc>{esc(desc)}</desc>`, then the canonical monochrome `<style>…</style>` block. **No root class, no `width`/`height`, no `aria-labelledby`, no `preserveAspectRatio`** — byte-identical to the shipped families' canonical figures. `alt`/`title`/`desc` come from the §13 accessibility model |
| Root class is a PRESENTATION concern, never on the canonical figure | The canonical `media[0].svg` carries **no** root class; `presentationSvg()`/`exportSvg()` (§8.2) are what stamp `class="cx-figure"` (the shared root class — **never** a family-specific `ratio-figure`). There is no `ratio-figure` root anywhere; the *theme id* is `spi-math-ratio-theme/1` (a separate namespace from the DOM class). All `commonCss` rules are scoped `.cx-figure .cx-… {…}`, so the root class MUST be `cx-figure` or no rule applies — this is asserted by `theme-root-is-cx-figure` (§8.11) |
| Diagram kind | `RATIO_DIAGRAM_KIND ∈ {"bar", "double-number-line", "table"}`; selected deterministically per task by a **total** dispatch (§8.10), never per-seed-random; `inverse_proportion → none` is a hard arm of that total function with no code path that can attach a proportional figure |
| Presentation styling | the canonical monochrome `<style>` block is the in-figure default for `media[0].svg`; `presentationSvg()`/`exportSvg()` (§8.2) strip it (the shared non-greedy single-block regex `/<style>[\s\S]*?<\/style>/`) and substitute the per-root `cx-figure` custom-property style — identical mechanism to `data-chart-theme.ts`/`mensuration-theme.ts` |
| Orientation convention | bar/number-line diagrams are laid out in **SVG pixel space directly** (no math-y flip); the layout allocates horizontal **bands** (bar model) or horizontal **lanes** (double number line) at fixed integer y-rows. There is no Cartesian axis, no grid, no tick-on-an-axis — this is the **non-Cartesian** proof point |
| Plotting box | fixed integer inset of `80` → drawable region `[80,920] × [80,620]`; reserved bottom strip `y∈[630,690]` holds the `NOT TO SCALE` banner, present **by design** when a bar's segment widths cannot be made proportional within the box (e.g. large `total` with small parts — §8.10) |
| Coordinates | every emitted coordinate is an **integer** produced by `gridRound(num, den)` (round-half-up on the exact `Rational`, correct for negatives — the SAME single rounding rule used family-wide) over the integer band/lane layout. No float fit-to-view exists |
| Numbers | emitted only via `fmtInt(n)`; ratio/quantity labels formatted by the shared display helpers (the §5 ratio formatter and the §4 quantity/rational display), never float pixels |
| Namespaced ids | every figure carries a per-item/per-card prefix `r{ns}` on every `id` and every `url(#…)` reference (gradients, clip paths, marker ids, the hatch `<pattern>`), where `ns` is a deterministic, Py↔TS-identical token derived from the item's stable seed/content (§8.2). Multiple figures on one worksheet page never collide in the DOM, and every reference resolves *within its own figure* — asserted by `svg-ids-namespaced` (prefix present AND every `url(#…)` resolves locally) |

**Segment widths are exact-proportional, never float, via ONE cumulative-sum array.** For a bar model of parts `[p₁,…,pₙ]` (the field `RatioModel.diagramParts`, never re-derived per renderer) with `S = Σpᵢ` and drawable bar width `W` (integer, `W = 840` for a full-width bar), a single cumulative-boundary array is computed once: `x₀ = 80`, and for `k = 1..n`, `xₖ = 80 + gridRound(W · (Σ_{i≤k} pᵢ), S)`, with `xₙ = 80 + W` exactly. Segment `k` spans `[x_{k-1}, x_k]` using that SAME array, so adjacent segments share a boundary integer by construction (one rounding per boundary, never two independent roundings) — asserted by `bar-segments-tile-exactly` (the union of segment x-spans equals `[80, 80+W]` with no gap/overlap and boundaries match this cumulative rule).

### 8.2 The additive ratio theme extension (reuse the pattern; modify no shared theme)

A new file pair `core/visual-style/ratio-theme.{json,ts}` is introduced as a **versioned additive extension** with theme id `spi-math-ratio-theme/1` that `extends: "spi-math-cartesian-theme/1"` **directly** — exactly as `data-chart-theme.json` and `mensuration-theme.json` do. This is the single canonical theme name for the family; there is **no** competing `bar-model-theme` / `number-line-theme` spelling, and the theme id is distinct from the DOM root class (which is the shared `cx-figure`). It FOLLOWS the additive *pattern* (same mechanism, same `cx-figure` root isolation, same `presentationSvg()`/`exportSvg()` contract) but does **not** depend on `data-chart-theme` or `mensuration-theme`: `presentationSvg`/`exportSvg` compose **cartesian + ratio** rulesets only, so none of the chart `--cx-bar*`/`--cx-symbol*` or mensuration `--cx-dim*`/`--cx-result*` variables are pulled in. Concretely, mirroring `mensuration-theme.ts` line-for-line:

- `modeVars(mode) = { ...cartModeVars(mode), ...RATIO_VARS[mode] }`; `COMMON_CSS = CART_COMMON_CSS + theme.commonCss`; `resolveCommonCss(mode)` resolves every `var(--cx-…)` for the export clone (same `#000` last-resort fallback the base helper uses).
- `presentationSvg(svg, mode)` strips the canonical `<style>` and stamps `class="cx-figure" style="{modeVarStyle(mode)}"`; `exportSvg(svg, mode, 6000, 4200)` bakes the resolved cartesian+ratio ruleset inside the clone; `modeBackground(mode)` returns `--cx-bg`. **Identical mechanism, zero new mechanism invented.**
- `MODES = ["print", "premium", "premium-dark", "accessible"]`.

**Namespacing rule.** Every variable and class this family *introduces* is prefixed `--cx-ratio-*` / `.cx-ratio-*` so it cannot collide with — or shadow — any cartesian, data-chart, mensuration, or transformations variable name. Label fill is **inherited**, not re-declared: the family does NOT introduce a `--cx-lbl` variable (the base `.cx-lbl` already binds `fill:var(--cx-text)`); value labels use the base `.cx-lbl` class and inherit `--cx-text`. This makes the `theme-no-variable-collision` test (every ratio variable name is disjoint from every name of every shipped theme) **trivially true by construction**.

| Variable | Class | Role |
| --- | --- | --- |
| `--cx-ratio-bar-known` | `.cx-ratio-bar-known` | a **known** (given-value) bar segment — solid fill |
| `--cx-ratio-bar-unknown` | `.cx-ratio-bar-unknown` | an **unknown** segment in the answer key only — distinguished by a **hatch pattern + dashed outline**, never colour alone |
| `--cx-ratio-bar-edge` | `.cx-ratio-bar-edge` | segment/bar outline — heaviest stroke |
| `--cx-ratio-bar-divider` | `.cx-ratio-bar-divider` | inter-segment divider lines |
| `--cx-ratio-nl-axis` | `.cx-ratio-nl` | a double-number-line lane rule |
| `--cx-ratio-nl-tick` | `.cx-ratio-nl-tick` | aligned tick on a number-line lane |
| `--cx-ratio-brace` | `.cx-ratio-brace` | total-span brace under/over a bar |
| `--cx-ratio-unknown-mark` | `.cx-ratio-unknown-mark` | the `?` glyph marking a hidden value in the **student** figure |
| `--cx-ratio-ans` | `.cx-ratio-ans` | answer/derived annotation — **overlay only** |

(Value labels reuse the base `.cx-lbl` / `--cx-text`; no new label variable is introduced.)

**Each of the nine new variables is given an explicit value in all four modes** (table below) — a `theme-completeness` test (mirroring `data-chart-theme.test.ts`/`mensuration-theme.test.ts`) asserts each declared variable has a value in every mode, and `theme-no-variable-collision` asserts no ratio variable name equals any cartesian / data-chart / mensuration / transformations variable name (true by the `--cx-ratio-*` prefix).

**Known vs unknown is encoded by shape/fill/dash, never colour.** A known segment is a solid-filled rectangle with the heavy `.cx-ratio-bar-edge` outline. An unknown segment (answer-key overlay only) uses a **diagonal hatch `<pattern>`** fill plus a **dashed** outline (`stroke-dasharray:6 4`). The student figure marks any hidden value with a literal `?` text glyph (`.cx-ratio-unknown-mark`), not a colour. All distinctions survive the monochrome `print` mode (the colour-free authoritative rendering) where every class resolves to opaque greyscale and the hatch/dash/`?` still read.

| Variable / mode | `print` (authoritative) | `premium` | `premium-dark` | `accessible` (CVD-safe) |
| --- | --- | --- | --- | --- |
| `--cx-ratio-bar-known` | `#e8e8e8` | `#dbeafe` | `#1e3a5f` | `#ffffff` |
| `--cx-ratio-bar-unknown` | `#ffffff` | `#fef9c3` | `#3f3a1e` | `#ffffff` |
| `--cx-ratio-bar-edge` | `#111111` | `#1e293b` | `#e5e7eb` | `#000000` |
| `--cx-ratio-bar-divider` | `#111111` | `#334155` | `#cbd5e1` | `#000000` |
| `--cx-ratio-nl-axis` | `#111111` | `#1e293b` | `#e5e7eb` | `#000000` |
| `--cx-ratio-nl-tick` | `#111111` | `#2563eb` | `#60a5fa` | `#0072b2` |
| `--cx-ratio-brace` | `#111111` | `#334155` | `#cbd5e1` | `#000000` |
| `--cx-ratio-unknown-mark` | `#111111` | `#b45309` | `#fcd34d` | `#000000` |
| `--cx-ratio-ans` (overlay) | `#111111` | `#dc2626` | `#f87171` | `#d55e00` |

**The hatch is driven entirely by CSS classes, never by inline `var()` presentation attributes.** This is mandatory for the self-contained export: `resolveCommonCss` rewrites `var(--cx-…)` ONLY inside the baked `<style>` block, so a `var()` reference written as an inline presentation attribute (e.g. `<path stroke="var(--cx-ratio-bar-edge)">` inside the `<pattern>`) would be left unresolved in the `exportSvg` clone and the hatch would render strokeless — defeating both the known/unknown distinction and self-containment. Therefore the hatch geometry carries a CSS class only (e.g. `<path class="cx-ratio-hatch-stroke"/>`), with `.cx-figure .cx-ratio-hatch-stroke{stroke:var(--cx-ratio-bar-edge);…}` and `.cx-figure .cx-ratio-bar-unknown{fill:url(#r{ns}-hatch);stroke:var(--cx-ratio-bar-edge);stroke-dasharray:6 4}` living in the additive `commonCss`. The new check `no-inline-var-in-attrs` (§8.11) asserts the substring `var(` never appears in any presentation attribute of any emitted figure — only inside a `<style>` block. The hatch `<pattern>` is emitted **inside the figure** with the namespaced id `r{ns}-hatch` so the unknown texture is self-contained in the 6000×4200 export (no external reference) and never collides across cards. The coordinate-lines, stats, mensuration, and transformations figures continue to render byte-for-byte unchanged because ratio only *adds* `--cx-ratio-*` variables and `.cx-ratio-*` rules under the same `cx-figure` root.

### 8.3 Element vocabulary and fixed z-order (student figure)

A small, total, fixed vocabulary (hand-rolled serializer, fixed element order, fixed attribute order per element, single `U+0020` between attributes, elements joined by `"\n"`, no indentation, void elements self-closed; a single `escapeXml` over `& < > " '`; UTF-8) — identical serializer rules to the shipped families:

| Primitive | Element / class | Role |
| --- | --- | --- |
| Hatch pattern (defs) | `<pattern id="r{ns}-hatch">` + `<path class="cx-ratio-hatch-stroke">` | overlay-only unknown texture; class-styled, no inline `var()` |
| Bar segment (known) | `<rect class="cx-ratio-bar-known">` | one part of a bar model; solid fill |
| Segment divider | `<line class="cx-ratio-bar-divider">` | boundary between adjacent parts |
| Bar outline | `<rect class="cx-ratio-bar-edge">` (no fill) | the whole-bar boundary; heaviest stroke |
| Total brace | `<path class="cx-ratio-brace">` | span brace indicating the labelled total (when total is given) |
| Number-line lane | `<line class="cx-ratio-nl">` ×2 | the two aligned scales of a double number line |
| Number-line tick | `<line class="cx-ratio-nl-tick">` | a tick on a lane; vertically aligned across both lanes |
| Value / part label | `<text class="cx-lbl">` | part value, part name, total, or lane value — base label class (inherits `--cx-text`), placed by the label engine (§8.6) |
| Unknown marker | `<text class="cx-ratio-unknown-mark">` | the `?` glyph standing in for a hidden value in the student figure |
| NOT TO SCALE banner | `<text class="cx-nts">` (reuses base) | emitted **by design** only when proportional widths overflow the box (§8.10) |

Fixed z-order (document order is the only SVG z-ordering and is part of the contract): **`<defs>` hatch pattern → bar/lane fills → dividers/ticks → outlines → braces → unknown markers → value labels → banner**. Labels last so the collision engine (§8.6) places text over settled geometry. All primitives are presentation-only and carry **no per-element `role`/`aria`** — they sit inside the single `role="img"` root, so the axe-core a11y gate (§13) sees exactly one labelled image. (The hatch `<pattern>` exists in the student-channel `<defs>` only when the overlay needs it; in the pure student figure it is omitted, so `no-answer-in-student-figure` can key on class presence — see §8.7.)

### 8.4 Bar model (segmented rectangles per part)

The bar model is the primary figure for `share_two_part`, `share_three_part`, `missing_part`, and (low-band, illustrative) `simplify` / `write_from_quantities`. It supports **two-part and three-part** ratios (the only multiplicities in v1.0.0 scope; four-or-more parts are out of scope and unreachable):

1. **Segments are exact-proportional.** Boundaries computed by the §8.1 single cumulative-sum rule; widths reflect the *parts* of the ratio (using the **unsimplified** parts where the task shows original quantities, the **canonical** parts where the task is about simplest form — keyed off `RatioModel.diagramParts`, a single declared field, never re-derived per renderer).
2. **Given quantities shown; missing values hidden.** Each segment that corresponds to a **given** quantity carries its value label (e.g. `12`, or `12 sweets` when the §7 context label applies). A segment whose value is **unknown in the task** (the missing part in `missing_part`, every share in `share_*` before solving) carries a `?` `.cx-ratio-unknown-mark` — **never its computed value** — in the student figure. The total brace is labelled only when the total is given.
3. **Known vs unknown distinction is structural.** Known segments are solid `.cx-ratio-bar-known`; the unknown marker is the `?` glyph. The hatch/dash treatment is reserved for the **answer-key overlay** (§8.8), so the student figure stays free of any solved-value texture. `bar-known-unknown-distinct` asserts the distinction is shape/fill/glyph-based (passes the `no-color-only` gate).
4. **Clear part + total labels.** Each part is labelled by its **category name** (from the §7 `labels[]`, correspondence by label not by position) above or inside its segment, and the total is labelled on the brace. `bar-labels-attributed` asserts every drawn segment maps to exactly one part label and (when present) the brace maps to the total.

Parts are distinguished by label + divider + position alone (a single bar makes position unambiguous); the renderer does **not** carry per-part fill patterns — the hatch is reserved purely for the known-vs-unknown distinction (the one place a non-positional cue is actually needed), keeping the bar mathematically clear, not over-decorated, and minimizing parity surface.

### 8.5 Double number line (two aligned scales)

The double number line is the figure for `direct_proportion`, `unit_rate`, and (where a ratio is read as a rate) `simple_scale`. It is **two horizontal lanes** at fixed integer rows `y=300` (top) and `y=420` (bottom), sharing **vertically aligned tick positions** so each top value sits directly above its corresponding bottom value:

1. **Aligned ticks via ONE shared integer array.** Tick x-positions are computed once as a single integer array from a single fraction sequence (`x = 80 + gridRound(W·a, b)` over the shared value sequence); **both lanes index that identical array** — the bottom lane never re-rounds from its own values. `nl-ticks-aligned` asserts **array identity** (every top tick's x is the same integer drawn from the same array as its paired bottom tick), not numeric proximity, so two `gridRound` calls on different-but-proportional rationals can never round to adjacent integers and break Py↔TS parity.
2. **Given pairs shown; the asked value hidden.** Each lane labels the **given** values at their ticks (e.g. top lane `3 → 6 → 9`, bottom lane `£1.20 → ? → £3.60`); the **asked** position carries a `?` `.cx-ratio-unknown-mark`, never the answer, in the student figure.
3. **No Cartesian axis.** The lanes are bare rules with ticks — there is no origin, no second perpendicular axis, no grid. This is deliberately the **non-Cartesian** model; gradient-as-ratio (which the deferral list assigns to coordinate-lines) is **never** rendered here.

### 8.6 Deterministic label-placement and collision policy

The brief requires labels never collide with bars, lanes, ticks, braces, or other labels, and that each value is unambiguously attributed. This **reuses the geometry-angles adaptive label engine + integer-bounding-box contract** (committed per-glyph advance-width table over the restricted label charset — digits, space, `:`, `£`/`$`/unit letters, `/`, `−`, `?` — at the fixed `.cx-lbl` font size, so collision is testable **without rendering** and identical cross-language). The ratio specialisation:

1. **Candidate anchors (deterministic, ordered).** Bar: (1) centred inside its segment if the segment box clears the label box, (2) centred above the segment, (3) a callout above the bar joined to the segment midpoint by a dashed round-capped leader. Number line: (1) directly above (top lane) / below (bottom lane) its tick, (2) shifted to a clear neighbouring slot, (3) callout. The order is fixed so Python and TS choose the identical anchor.
2. **Collision policy.** A candidate is accepted only if its integer box clears, by ≥ `8` units (the approved min clearance), every: bar outline, divider, lane, tick, brace, unknown marker, and every already-placed label box. The first clearing candidate wins; if none clears, the engine escalates to the callout tier; if that also fails, `generate()` triggers a **bounded seeded redraw** of `params` (deterministic regeneration — never a silent overlap), advancing the same `mulberry32` stream (the parity contract is call order).
3. **Side / part attribution.** Each label binds to exactly one part (its anchor/leader midpoint lies within `GAP=6` of exactly one segment or tick) and labels do not cross — `label-attribution-unambiguous` asserts this.

The blocking validator `label-no-collision` (§8.11) inspects the **serialized SVG text** (parsed integer boxes), consistent with the platform rule that the validator inspects serialized SVG, not a render.

### 8.7 Only-given quantities; no answer in the student figure (role-keyed)

The student figure is governed by an **intent/role-based** answer-leakage policy (semantic, not "no numeral appears" and not value-set-equality):

- **Only given quantities are drawn.** The renderer iterates `RatioModel.givenValues[]` / `SharingModel.givenValues[]` — exactly the quantities the prompt supplies, each a typed *slot* — and emits a value label only for those slots. It NEVER iterates derived shares, the missing part, the unit rate, or the total when the total is itself the asked quantity.
- **Hidden values are marked `?`, never computed.** Every unknown is a `.cx-ratio-unknown-mark` `?`. There is **no** `.cx-ratio-ans` and **no** `.cx-ratio-bar-unknown` hatch class (and no `r{ns}-hatch` pattern reference) in the student render at all — those exist only in the overlay (§8.8) — so "no answer/solution class in the student figure" is a structural invariant a parser checks by class presence.
- **Given == answer is NOT leakage.** As in the mensuration/angle whitelist, a given quantity that happens to equal a derived value is legitimate given data; the rule targets *dedicated derived/answer annotations*, not raw given data.

The blocking checks are **role-keyed, not value-set-keyed** (this is the §13/§14 `raw-data-equality-is-not-leakage` model):

- `no-answer-in-student-figure` asserts the student asset contains **no** `.cx-ratio-ans` element, **no** `.cx-ratio-bar-unknown` element, and **no** `r{ns}-hatch` reference; i.e. no element whose role is *derived/answer* appears.
- `only-given-values-shown` asserts every value-bearing `.cx-lbl` element is **bound to a `givenValues[]` slot by role** (each rendered value-label's slot id is a member of `givenValues[]`), and that no `.cx-lbl` is bound to a derived/asked slot. It does NOT test multiset equality of numerals — a category label that is numeric, or a given total that numerically repeats a given part, passes; and a derived value that merely coincides with a given value would still FAIL because its *slot role* is derived. This keys on slot role exactly as §8.7's prose requires.

### 8.8 Answer-key overlay variant (key/solution channels ONLY)

A separate render `canonicalRatioSvgOverlay(model, diagramKind)` produces the answer-key figure. It is composed from the **same canonical base-diagram fragment and the same student annotations** as the student figure, then adds one additive answer-overlay group (which is the only place the `r{ns}-hatch` `<pattern>` and any `.cx-ratio-bar-unknown` / `.cx-ratio-ans` element appear) before the closing tag, emitted to a distinct namespaced `media[]` asset id (`fig-1-key`) used ONLY by the answer-key and solutions exporters — never in the worksheet/student channel.

| Overlay addition | Class | When |
| --- | --- | --- |
| The solved share(s) labelled on their segment(s) | `.cx-ratio-ans` | `share_two_part`, `share_three_part` |
| The hidden segment redrawn with hatch + dashed outline + its derived value | `.cx-ratio-bar-unknown` + `.cx-ratio-ans` | `missing_part`, `share_*` |
| The asked number-line value placed at its tick | `.cx-ratio-ans` | `direct_proportion`, `unit_rate`, `simple_scale` |
| The unit rate / total annotation in a clear margin | `.cx-ratio-ans` | all figured tasks |

The overlay reuses the same label-collision engine so overlay annotations do not collide with the student labels they sit beside. Because both channels are built from one canonical base-diagram fragment and the overlay only *adds* an answer group, the student and key SVGs share their **base diagram byte-for-byte** and their student annotations unchanged — proven by `answer-key-base-diagram-identical`, `answer-key-overlay-additive-only`, and `overlay-shows-answer` (the key asset DOES carry a `.cx-ratio-ans` value, and the student/key asset ids cannot be swapped). The review pack exploits this by showing **student diagram BESIDE answer-key overlay** (§14).

### 8.9 Proportional table — deterministic semantic HTML table + dataTableFallback

For `share_three_part` (and any multi-value response), the brief's **table-completion** answer (§7) is paired with a **deterministic semantic HTML table**, reusing the data-handling precedent (the authoritative learner-facing renderer for tabular data is a semantic HTML table, with an SVG snapshot only where a single rasterizable asset is needed). It is also the default figure for `best_buy` (two rate rows). Three artifacts, all from one canonical table model:

- `ratioTableHtml(model) → string`: a deterministic `<table>` with a `<caption>`, a `<thead>` row of `<th scope="col">` (the part labels — correspondence **by label**, e.g. `Ali | Ben | Cara | Total`), and `<tbody>` `<td>` cells. **Given** cells carry their value; **to-complete** cells carry an empty string in the student table (never the answer) and the solved value in the key table. Cell order is the canonical part order; ids are namespaced `r{ns}-cell-{label}`. Rendered byte-identically Py↔TS (same `canonicalStringify`-style deterministic emission — fixed attribute order, no whitespace drift).
- `media[].dataTableFallback`: the structured object `{ columns:[{label, role:"part"|"total"}], rows:[{cells:[{label, value|null, role:"given"|"asked"}]}] }`. `dataTableFallback` is a generic `{type:"object"}` in `question-item.schema.json` (confirmed for the stats family) so **no schema change is required**. Cells are **typed by role** (`given` vs `asked`) so the no-leakage check keys on slot role, not on numeric coincidence — a *given* cell that numerically equals the answer **passes**.
- The student table's `asked` cells are `value:null` (and empty `<td>`); `ratio-table-no-answer-leak` asserts no `asked`-role cell is populated in the student channel, and `data-table-matches-model` asserts the fallback lists exactly the model's labels and given values, same order, so the non-visual learner has information-equivalent input.

### 8.10 Diagram-kind selection, to-scale policy, and deterministic regeneration

Diagram kind is selected by a **total dispatch keyed on the §1.3 task slug**, not per seed; the dispatch has no default branch and every slug maps to exactly one arm (including `none`):

| Task | Default diagram kind | Figure? |
| --- | --- | --- |
| `simplify`, `write_from_quantities` | `bar` (low-band illustration) | optional |
| `ratio_to_fraction`, `fraction_to_ratio` | `bar` | yes |
| `share_two_part`, `share_three_part`, `missing_part` | `bar` (+ `table` for three-part) | yes |
| `direct_proportion`, `unit_rate`, `simple_scale` | `double-number-line` | yes |
| `inverse_proportion` | **none** (text-only) | **no** — see note |
| `best_buy` | `table` (semantic HTML, two rate rows) | yes |

**Inverse proportion ships no proportional bar/number-line.** A double number line and an equal-segment bar both visually assert *direct* proportionality; rendering one for an inverse task would teach the `direct-for-inverse` misconception (§10). The dispatch maps `inverse_proportion → none` as a hard arm (defence-in-depth: there is no code path that can attach a `bar`/`double-number-line` to an inverse item, so the check is not the sole guard). An optional plain product-invariant table is permitted but no proportional diagram. `inverse-no-proportional-figure` asserts no `bar`/`double-number-line` media is attached to an inverse item.

**To-scale policy.** Bar segment widths are **mathematically exact-proportional** within the single `gridRound` half-unit (`bar-to-scale-faithful` asserts each segment width is proportional to its part within that bound, one global scale factor), and `media[].toScale=true` for in-box bars. When the ratio's `Σ parts` is large enough that the smallest segment would fall below the `MIN_SEG_PX = 24` legibility floor, the generator first attempts the §8.1 bounded seeded redraw toward clearer parts; if the *task itself* requires those parts (e.g. a fixed given total), the bar is drawn with a normalized `NOT TO SCALE` banner and `toScale=false` — the banner is then present **by design**, asserted by `bar-not-to-scale-banner-when-flagged` (`toScale=false` ⟺ banner present, and only then). Double number lines are always `toScale=true` (ticks at exact-proportional integer x). No figure is ever silently shipped with illegible or mislabelled segments.

### 8.11 Blocking SVG / render validators (named `checks[]`)

Every render invariant is an independent, named entry in `lifecycle.validation.checks[]`; any `fail` ⇒ `validation.status = fail`, the item never reaches `machine-validated`, and it is excluded from the offline export. These names are part of the single canonical `checks[]` vocabulary fixed in §9 and referenced verbatim by §12 and §14 — there are **no alternative spellings** (e.g. it is `answer-key-base-diagram-identical`, never `…base-geometry-identical`; it is `no-answer-in-student-figure`, never `no-result-in-student-figure`):

| Check (blocking) | Asserts |
| --- | --- |
| `svg-realises-data` | recompute the canonical greyscale SVG from `params` via the shared renderer (viewBox `0 0 1000 700`, integer coords via `gridRound`, root `role="img"` + `<title>`/`<desc>`, namespaced ids) and assert `== media[i].svg` **byte-for-byte**, Py↔TS identical. Parity scope is the canonical monochrome SVG ONLY; the four themed presentations and the 6000×4200 export are TS-only derivations (§16), audited (§14) but never Py-byte-compared |
| `theme-root-is-cx-figure` | every `presentationSvg`/`exportSvg` output's root carries `class="cx-figure"` (never `ratio-figure`); the canonical `media[0].svg` carries no root class |
| `svg-ids-namespaced` | every `id` carries the `r{ns}` prefix (no un-prefixed id); every `url(#…)` reference resolves to a local id within the same figure; no cross-card collision |
| `no-inline-var-in-attrs` | the substring `var(` appears only inside a `<style>` block — never in any presentation attribute (guarantees the hatch and every styled element survive `exportSvg`'s `<style>`-only `var()` resolution) |
| `bar-segments-tile-exactly` | bar segment x-spans tile `[80, 80+W]` with no gap/overlap; boundaries match the single §8.1 cumulative-sum rule (`x₀=80`, `xₙ=80+W`) |
| `bar-to-scale-faithful` | each segment width ∝ its part within one `gridRound` half-unit, one global scale (in-box bars) |
| `bar-known-unknown-distinct` | known vs unknown distinguished by fill/shape/glyph, not colour (passes `no-color-only`) |
| `bar-labels-attributed` | every segment maps to exactly one part label; brace maps to the total when present |
| `nl-ticks-aligned` | both lanes index ONE shared integer tick-x array; every top tick's x is identical (same array element) to its paired bottom tick (array identity, not numeric proximity) |
| `label-no-collision` | parsed integer label boxes clear all geometry and each other by ≥ `8` units (inspects serialized SVG text) |
| `label-attribution-unambiguous` | each label binds to exactly one part/tick; no crossing leaders |
| `only-given-values-shown` | every value-bearing `.cx-lbl` is bound by ROLE to a `givenValues[]` slot; no `.cx-lbl` bound to a derived/asked slot (role-keyed, NOT numeric multiset equality) |
| `no-answer-in-student-figure` | the student asset contains no `.cx-ratio-ans`, no `.cx-ratio-bar-unknown`, and no `r{ns}-hatch` reference; no element whose role is derived/answer (computed share, missing part, unit rate, asked total) is drawn |
| `answer-key-base-diagram-identical` | base-diagram bytes identical between student and key channels |
| `answer-key-overlay-additive-only` | the only inter-channel difference is the additive overlay group; student geometry unchanged |
| `overlay-shows-answer` | the key asset (`fig-1-key`) carries the `.cx-ratio-ans` answer; student/key asset ids are not swappable |
| `inverse-no-proportional-figure` | an `inverse_proportion` item carries no `bar` / `double-number-line` media |
| `bar-not-to-scale-banner-when-flagged` | `toScale=false` ⟺ the `NOT TO SCALE` banner is present (and only then) |
| `no-color-only` | every known/unknown/part distinction survives the monochrome `print` mode (hatch/dash/glyph/weight) |
| `ratio-table-no-answer-leak` | no `asked`-role cell populated in the student table / `dataTableFallback` |
| `data-table-matches-model` | `dataTableFallback` lists exactly the model's labels + given values, same order, information-equivalent |
| `theme-completeness` | each of the nine `--cx-ratio-*` variables has a value in all four modes |
| `theme-no-variable-collision` | no `--cx-ratio-*` variable name equals any cartesian / data-chart / mensuration / transformations variable name (trivially true by the `--cx-ratio-*` prefix) |
| `theme-isolation` | only ratio + cartesian rulesets are composed; cartesian/data-chart/mensuration/transformations figures render byte-for-byte unchanged |
| `export-6000x4200-self-contained` | `exportSvg(svg, mode, 6000, 4200)` is self-contained (baked ruleset, in-figure class-styled hatch pattern, `--cx-bg` raster fill), pure vector, no `<script>`/`<image>`/`<foreignObject>`/animation, no unresolved `var()` in any attribute, two-column-print safe |

---

The renderer is specified in `core/render/ratio-diagrams/{bar-model,double-number-line,ratio-table}.ts` (TypeScript) mirrored byte-for-byte by `oracle/spi_oracle/ratio_diagrams.py`; the additive theme is `core/visual-style/ratio-theme.{json,ts}` (`spi-math-ratio-theme/1`, `extends spi-math-cartesian-theme/1`). All four modes (`print` authoritative, `premium`, `premium-dark`, `accessible`) are produced via the additive theme's `presentationSvg()` (which stamps the shared `class="cx-figure"` root); the self-contained 6000×4200 (S=6) export via `exportSvg()`. Themed/exported SVGs are TS-only derivations and are explicitly OUT of Py↔TS byte-parity scope — only the canonical monochrome `media[0].svg` is byte-compared across languages. No shared theme is modified; the non-Cartesian bar/number-line/table system reuses every approved mechanism (per-root CSS vars, four modes, `presentationSvg`/`exportSvg`, monochrome-authoritative, Py↔TS byte parity of the canonical SVG, namespaced ids, bbox label clearance, `dataTableFallback`) and introduces only additive `--cx-ratio-*` primitives, driving the hatch by CSS class (never inline `var()`) so it survives the self-contained export.

Relevant absolute paths referenced for consistency: `C:\Users\Mohamad Solaiman\OneDrive\Desktop\Claude Question generator\core\visual-style\mensuration-theme.{json,ts}`, `...\core\visual-style\cartesian-theme.{json,ts}` (verified: `presentationSvg`/`exportSvg` stamp `class="cx-figure"`; `resolveCommonCss` rewrites `var(--cx-…)` only inside the baked `<style>`; base `.cx-lbl` binds `fill:var(--cx-text)`; no `--cx-ans` in cartesian/mensuration — mensuration uses `--cx-result`), and the precedent Section 8 in `...\docs\GENERATOR_SPEC_mensuration_PROPOSAL.md`.

## 9. Solver and independent-validator design

This family follows the platform's **oracle-first, two-route** discipline (the `mensuration` / `transformations` precedent): an independent Python `spi_oracle` solver is authored and frozen FIRST, then a byte-identical TypeScript mirror; and a **separate** independent validator recomputes everything from `params` and asserts the stored item byte-for-byte. The solver and the validator share **no code path** except the exact primitives (`core/exact-math/rational.ts` / `fractions.Fraction`, `core/seeded-random/mulberry32.ts`, the `core/exact-math/ratio.ts` model of §6). The validator is **forbidden** from importing the generator's answer/SVG/`Ratio`-builder closures, so closure-agreement is a genuine cross-check, not a tautology. Both routes consume the **one canonical `Ratio` model** (§6) and the **structured answer contracts** (§4: `ratio`, plus the existing `integer` / `exact-rational` / `table-completion` / `multiple-choice` shapes — **no `comparison` answer type is introduced; see §9.2 and §4**).

### 9.1 Task vocabulary (single source)

Every solver rule, check, adapter, difficulty record, and review-pack cell keys off the **twelve canonical task slugs** defined once in `core/curriculum/ratio-objective-ids.ts` (`RATIO_TASKS`) and mirrored verbatim in `oracle/spi_oracle/ratio.py` (`OBJECTIVE_BY_TASK`). These twelve slugs are the **§1.3 canonical set** — used **verbatim** here, in §3, §10's `RULES_BY_TASK`, §11's `ratio-difficulty.json`, §12, §14, and §15, with **no alternative spellings** anywhere (the superseded forms `simplify_ratio`, `write_ratio_from_quantities` / `write_ratio`, `direct_proportion_unitary`, `inverse_proportion_unitary`, `direct`, `inverse` are **banned and must not appear**):

```
simplify, write_from_quantities, ratio_to_fraction, fraction_to_ratio,
share_two_part, share_three_part, missing_part, direct_proportion,
inverse_proportion, unit_rate, best_buy, simple_scale
```

The single-source objective map (§1, mirrored in the oracle) uses the **§1.2 canonical IDs** (no `_UNITARY` suffix):

```
simplify              : SPI.MIDDLE.RATIO.SIMPLIFY.01
write_from_quantities : SPI.MIDDLE.RATIO.WRITE_FROM_QUANTITIES.01
ratio_to_fraction     : SPI.MIDDLE.RATIO.RATIO_TO_FRACTION.01
fraction_to_ratio     : SPI.MIDDLE.RATIO.FRACTION_TO_RATIO.01
share_two_part        : SPI.MIDDLE.RATIO.SHARE_TWO_PART.01
share_three_part      : SPI.MIDDLE.RATIO.SHARE_THREE_PART.01
missing_part          : SPI.MIDDLE.RATIO.MISSING_PART.01
direct_proportion     : SPI.MIDDLE.RATIO.DIRECT_PROPORTION.01
inverse_proportion    : SPI.MIDDLE.RATIO.INVERSE_PROPORTION.01
unit_rate             : SPI.MIDDLE.RATIO.UNIT_RATE.01
best_buy              : SPI.MIDDLE.RATIO.BEST_BUY.01
simple_scale          : SPI.MIDDLE.RATIO.SIMPLE_SCALE.01
```

A bespoke `ratio-graph.test.ts` asserts `keys(OBJECTIVE_BY_TASK) == keys(RULES_BY_TASK) == keys(ANSWER_SHAPE_BY_TASK) == keys(ratio-difficulty.json.tasks) == RATIO_TASKS`, that each ID resolves in `curriculum/objectives/SPI.MIDDLE.RATIO.json`, and that **no alternative slug or ID spelling appears anywhere** in the family (a literal string-scan of the source tree for the banned spellings above fails the build).

### 9.2 Interaction policy (single source)

Free-response-first. The **answer-shape** (schema `answer.type`) and **MC-eligibility** of each task is declared once in `ANSWER_SHAPE_BY_TASK` / `MC_ELIGIBLE_TASKS` / `SUPPORTED_INTERACTIONS` (a slice of the §11 difficulty source of truth). **Every `answer.type` used here is a live schema enum member** (`ratio` is the single additive delta of §4; `integer`, `exact-rational`, `table-completion`, `multiple-choice` already exist). `best_buy` is realised on the **existing `multiple-choice` answer type** — the chosen option is intrinsically a labelled choice — with the exact per-option unit-rate witnesses carried in `solution.steps[]` and feedback; **no `comparison` answer type is proposed, and none is needed** (this keeps "`ratio` is the only new enum member" true, per §4/§15).

| Task slug | `answer.type` (§4, live enum) | `interactionType` policy |
|---|---|---|
| `simplify` | `ratio` | FR + **MC-eligible** (3 misconception-backed distractors: unsimplified-equivalent, partial-simplify, reversed) |
| `write_from_quantities` | `ratio` | **FR-only** (decision C) |
| `ratio_to_fraction` | `exact-rational` | FR + **MC-eligible** (part-over-other-part, one-part-as-whole, wrong-total-of-parts) |
| `fraction_to_ratio` | `ratio` | FR + **MC-eligible** (reversed, does-not-simplify-fully, unsimplified) |
| `share_two_part` | `table-completion` (2 labelled cells) | **FR-only** (decision C; multi-cell answer) |
| `share_three_part` | `table-completion` (3 labelled cells) | **FR-only** (multi-cell answer) |
| `missing_part` | `integer` (v1.0.0; integer-only, decision E) | **FR-only** (decision C) |
| `direct_proportion` | `integer` **or** `exact-rational` (see §9.3) | FR + **MC-eligible** |
| `inverse_proportion` | `integer` (simple integer cases only) | FR + **MC-eligible** (direct-for-inverse distractor) |
| `unit_rate` | `exact-rational` (rate value) | **FR-only** (decision C) |
| `best_buy` | `multiple-choice` (chosen option id; unit-rate witnesses in `solution`/feedback) | **MC-only** (decision C; the labelled choice IS the construct) |
| `simple_scale` | `integer` **or** `exact-rational` (see §9.3) | **FR-only** (decision C) |

For tasks tagged `integer **or** `exact-rational`` (`direct_proportion`, `simple_scale`), `ANSWER_SHAPE_BY_TASK` declares a **primary-shape pair** `{"integer","exact-rational"}`: the stored `answer.type` is `integer` when the exact result has `den == 1` and `exact-rational` otherwise (it is **never** an `exact-rational` with `den==1` masquerading as an integer — the `display-derived` / `answer-type-consistency` checks of §9.4 enforce the integer-when-whole collapse so Py and TS agree byte-for-byte). `missing_part` is **integer-only** in v1.0.0 (decision E: the `parts[knownIndex] ∣ knownValue` divisibility gate guarantees an integer recovered value) and `inverse_proportion` is integer-only by construction (non-integer cases excluded; §9.3).

An explicit multiple-choice request on an **MC-ineligible** task (`share_three_part`, or an MC-eligible task that redrew into a case lacking 3 distinct misconception-backed distractors) is handled by the platform rule: the generator **deterministically redraws** (call-order-preserving) to an MC-eligible case, or returns a clear **`interaction-not-supported`** error — it is **never** silently converted to free-response. The `interaction-type` check (§9.4) enforces this.

### 9.3 Solver (`spi_oracle/ratio.py`, mirrored in `domains/proportion/ratio.ts`)

`solve(task, params) -> SolveResult`, where `SolveResult` carries the typed `answer` (one of the §4 shapes), the worked `solution.steps[]`, and the misconception `ctx` (§10). All arithmetic is exact: integers and reduced `Rational`/`Ratio`. **No float, no tolerance, no irrational** ever appears in a canonical answer. The canonical-first rule holds throughout: the structured value **is** `answer.canonical`; `answer.display` is derived; the value is never stored twice.

| Task slug | Closed-form solver rule (exact) | Answer (canonical) |
|---|---|---|
| `simplify` | `g = gcd(parts); canonical = [p/g for p in parts]` | `ratio` `{parts}` (gcd=1) |
| `write_from_quantities` | order the given quantities by their **declared label order**, then simplify by `gcd` | `ratio` `{parts}` (2 or 3 parts, gcd=1) |
| `ratio_to_fraction` | for the named part `i`: `f = parts[i] / sum(parts)`, reduced | `exact-rational` `{num,den}` (part **over the whole**) |
| `fraction_to_ratio` | proper reduced `f = a/b` (`0 < a < b`, guaranteed by construction — §12) ⇒ `[a, b−a]`; simplify by `gcd` | `ratio` `{parts}` (named-part : rest) |
| `share_two_part` | `unit = total / (p₁+p₂)` (`Σparts ∣ total`, §9.4-D); `share_k = unit·p_k` | `table-completion`: `{label_k → integer share_k}` |
| `share_three_part` | `unit = total / (p₁+p₂+p₃)` (`Σparts ∣ total`); `share_k = unit·p_k` | `table-completion`: `{label_k → integer share_k}` |
| `missing_part` | known part `a_known` on the `m`-term of ratio `m:n`: `onePart = a_known/m` (generation enforces `m ∣ a_known`), `missing = onePart·n`, **integer by the §9.4-E hard divisibility rule** | `integer` (v1.0.0; integer-only, decision E) |
| `direct_proportion` | `unit = y₁/x₁`; `answer = unit·x₂` (scales **with** the other quantity) | `integer` when result whole, else `exact-rational` |
| `inverse_proportion` | product invariant `k = x₁·y₁`; `answer = k/x₂` (**simple integer cases only**: construction guarantees `x₂ ∣ k`) | `integer` |
| `unit_rate` | `rate = quantity / count`, reduced (price per 1 item, distance per 1 unit) | `exact-rational` `{num,den}` |
| `best_buy` | for each option `j`: `unitRate_j = price_j / size_j` (reduced `Rational`); the key is the option id with the **strictly minimum** unit rate (cost-per-unit) | `multiple-choice`: `canonical = {chosen}` (option id); `unitRate_j` witnesses recorded in `solution`/feedback |
| `simple_scale` | `scaleFactor = s` (declared direction); `answer = given · s` (enlargement) or `given / s` (reduction); construction guarantees exact | `integer` when whole, else `exact-rational` |

The solver emits `solution.steps[]` (`{number, transformation, intermediateResult}`); the final step's `intermediateResult` equals the canonical `display`, satisfying the SDK `answerSolutionAgrees` predicate. For `best_buy`, intermediate steps additionally record each `unitRate_j` so the witness is visible without a structured `comparison` canonical. The solver also emits the misconception `ctx` (§10.1) so each diagnostic value is recomputed from the **same** exact intermediates.

**Hard exactness rule (no optional escape hatch).** For the quotient tasks that may legitimately yield a rational (`ratio_to_fraction`, `direct_proportion`, `unit_rate`, `simple_scale`), the solver computes the **exact reduced `Rational`** and then sets `answer.type = integer` iff `den == 1`, else `exact-rational`. For the **integer-only** tasks (`missing_part` and `inverse_proportion`), the generator **must** enforce the divisibility precondition at construction time so the answer is integral by construction — for `missing_part`, `parts[knownIndex] ∣ knownValue` (decision E: which makes `onePart = knownValue/parts[knownIndex]` integral and therefore `missingValue = onePart·parts[missingIndex]` an exact integer); for `inverse_proportion`, `x₂ ∣ x₁·y₁` (non-integer cases excluded). If the precondition fails, the candidate is **rejected and the seed deterministically redraws** (§12); a non-exact result is **never** silently stored, rounded, or downgraded to a float. There is **no exact-rational path for `missing_part` in v1.0.0**. The `integer`-vs-`exact-rational` tag is therefore fully determined by the exact arithmetic, removing the §2/§9/§11 type ambiguity at its root.

### 9.4 Independent validator (`validate(item) -> {status, validatorVersion, checks[]}`)

Authored oracle-first (`oracle/spi_oracle/ratio_validate.py`), mirrored byte-identically (`domains/proportion/ratio-validate.ts`). Output is the shared `ValidationResult { status, validatorVersion, checks[] }` stored on `item.lifecycle.validation`; `validatorVersion = GENERATOR_VERSION` (`"1.0.0"`). `status = pass` iff **every** check passes; any `fail` logs the seed to the failing-seeds artifact `{generatorId, generatorVersion, seed, config, failingChecks[]}`. The validator **re-derives by a second, independent route** (the structural conditions below, not a re-call of `solve`) and recomputes the figure from `params`.

**Canonical check-name vocabulary.** The names below are the **single fixed `checks[]` vocabulary**; §8 (render), §10 (diagnostics), §12 (degeneracy), §13 (a11y), §14 (review pack) reference these exact strings verbatim — no alternative spellings. A spec-internal test asserts the documented name set equals the emitted set, and a cross-section string-scan asserts §8/§13/§14 use only these names (the renderer/leakage names are fixed here as the authority: `svg-realises-data`, `figure-realises-ratio`, `only-given-values-shown`, `no-result-in-student-figure`, `answer-key-overlay-additive-only`, `unknown-not-measurable-from-figure`, `theme-extension-intact` — earlier draft variants such as `answer-key-base-geometry-identical` / `no-answer-in-student-figure` are **not** used).

**A. Universal checks (every task)**

| Check name | Assertion |
|---|---|
| `generator-identity` | `item.generatorId == "gen.proportion.ratio"` and `item.generatorVersion == "1.0.0"`. |
| `objective-mapping` | `item.objectiveIds == [OBJECTIVE_BY_TASK[task]]` — the single-source §1.2 map (§9.1), cross-checked by `ratio-graph.test.ts`. |
| `interaction-type` | `item.interactionType ∈ {"free-response","multiple-choice"}`, `supportedInteractionTypes` matches `MC_ELIGIBLE_TASKS` (§9.2); an MC request on an ineligible/redraw-failed case raises `interaction-not-supported` and is **never** silently downgraded to free-response. |
| `answer-type-consistency` | `answer.type` equals the `ANSWER_SHAPE_BY_TASK[task]` declared type — `ratio` / `exact-rational` / `integer` / `table-completion` / `multiple-choice` (for the integer-OR-rational tasks, `integer` iff the exact result has `den==1`, else `exact-rational`, per §9.3); the structured canonical validates against that shape (a `ratio` canonical is `{parts:[…]}` only — no sibling display copy; a `multiple-choice` canonical is the chosen option id). |
| `closure-agreement` | re-solve via the independent route; the rebuilt typed answer from `params` equals the stored `answer.canonical` **structurally** (ratio: equal `parts` arrays after canonicalization; rational: equal reduced `{num,den}`; integer: equal value; table-completion: equal **label→value** map; multiple-choice: equal `chosen` option id **and** equal recomputed witness unit-rate set in `solution`). |
| `display-derived` | `answer.display` is exactly the §5 formatter output for `answer.canonical` (ratio → `"a:b"` / `"a:b:c"`; rational → reduced fraction string; integer → the integer; multiple-choice → the chosen option's label), byte-for-byte; the display is **never** the ground truth and is **never** duplicated in another field. |
| `answer-solution-agrees` | final `solution.steps[]` `intermediateResult == answer.display` (`answerSolutionAgrees`). |
| `exact-only` | no float, no decimal-with-tolerance, no surd, no `Rational` with `den<1` appears anywhere in `params`, `answer`, `answer.canonical`, `solution`, or `media`; every quotient stored is a reduced `Rational` or an exact integer. |
| `difficulty-in-band` | `overallBand ∈ TASK_BANDS[task]`; axes are the **closed 16-axis enum** only; band recomputed from weighted axes via `bandFromScore` (§11). |
| `reproducible` | re-running `generate(seed, config)` yields byte-identical serialization (the Mulberry32 redraw order is the parity contract). |
| `schema-valid` | the item validates against `question-item.schema.json` — including the new **`ratio`** `answerType` — in **all three** gates: bundled **Ajv**, the extended **`oracle/check_conformance.py`**, and the import/bank/export round-trip (§15). The `ratio` delta uses **only the keyword subset both validators share** (`if`/`then`/`const`/`required`/`additionalProperties`/`minItems`/`type`/`minimum`); the 2-or-3-part arity is enforced by `minItems:2` **plus** the new **single additive `maxItems` branch** in `check_conformance.py` (mirroring its existing `minItems` branch) declared as an owner-visible delta in §15 — **no `anyOf`/`oneOf`** appears in the delta, so Ajv and the Python checker apply identical rules. |
| `provenance` / `version-fields` | `provenanceComplete`, `versionFieldsPresent`. |

**B. Ratio-answer structural checks (`simplify`, `write_from_quantities`, `fraction_to_ratio`, and any task whose answer.type is `ratio`)**

| Check name | Assertion |
|---|---|
| `ratio-parts-positive-integers` | every entry of `answer.canonical.parts` is a **positive integer** (no zero, no negative, no rational, no float); arity is 2 or 3 per task. |
| `ratio-simplest-form` | `gcd(parts) == 1` (the independent route recomputes the gcd by the Euclidean algorithm over the **original** quantities, not over the stored canonical). For tasks where simplification is the assessed skill, this is the answer's defining property. |
| `ratio-order-preserved` | `parts` are in the **same label order** as the prompt's quantities (`2:3 ≠ 3:2`); the validator reconstructs the ordered tuple from `params.labels` and asserts positional equality — a reversed-but-equivalent tuple **fails**. |
| `ratio-equivalence-witness` | the stored canonical is equivalent to the **original unsimplified** ratio by the **elementwise simplest-form equality** that §6.3 fixes as the single normative implementation (both tuples reduce to the same simplest-form tuple); the two-part cross-multiplication `a·d == b·c` and three-part adjacent cross-products are recorded only as the *justification*, not a second code path. Proves canonicalization preserved value while reducing form. |
| `ratio-no-units` | the ratio answer carries **no** `measure`/`units`/`tolerance` field (ratios are dimensionless, §4); the per-`kind` schema branch forbids them and the validator independently rejects their presence. |

**C. Conversion checks (`ratio_to_fraction`, `fraction_to_ratio`)**

| Check name | Assertion |
|---|---|
| `fraction-is-part-over-whole` | for `ratio_to_fraction`, `answer.canonical == parts[i] / sum(parts)` reduced — independently recomputed; a `part/other-part` value **fails** (this is the `MISC.RATIO.RATIO_TO_FRACTION_ONE_PART_OVER_OTHER_NOT_OVER_WHOLE` trap, §10). |
| `fraction-to-ratio-complement` | for `fraction_to_ratio`, the reduced **proper** fraction `a/b` (`0 < a < b`, asserted) maps to `[a, b−a]` then simplified; the validator re-derives `b−a` and `gcd`, asserting the stored ratio matches, is simplest, and has only positive parts. |

**D. Sharing + table-completion checks (`share_two_part`, `share_three_part`)**

| Check name | Assertion |
|---|---|
| `total-parts-divisibility` | `total` is **exactly divisible** by `sum(parts)` (integer `unit`); the validator recomputes `unit = total / Σparts` and asserts `den == 1` (integer-share construction, §7/§12). |
| `share-values-by-unit` | each `share_k = unit · part_k`, independently recomputed; every share is a positive integer. |
| `share-sum-equals-total` | `Σ share_k == total` exactly (no rounding slack) — the table-completion **sum agreement** invariant. |
| `table-correspondence-by-label` | each completed cell is keyed by **label** (`Ali→12, Ben→18, Cara→30`), not row order alone; the validator matches `params.labels` to cells and **fails** a permuted-but-numerically-correct table whose label keys do not match (the `table-completion` point-aware label discipline of the transformations precedent). |

**E. Proportional-reasoning checks (`missing_part`, `direct_proportion`, `inverse_proportion`, `unit_rate`, `simple_scale`)**

| Check name | Assertion |
|---|---|
| `missing-part-exact` | for `missing_part`, the validator asserts the **hard, non-optional** divisibility precondition `parts[knownIndex] ∣ knownValue` (decision E), recomputes `onePart = knownValue / parts[knownIndex]` and `missingValue = onePart · parts[missingIndex]`, and asserts `answer.type == integer` with `den==1`. `missing_part` is **integer-only** in v1.0.0 — there is **no escape-hatch and no exact-rational path**; any non-divisible draw was redrawn at construction, and a non-integer or `exact-rational`-tagged answer **fails**. |
| `cross-multiplication-holds` | for `missing_part` / `direct_proportion`, `a:b == c:d ⇔ a·d == b·c` checked in exact integer arithmetic over the (known, answer) pair; the answer is the **unique** solution of that single linear relation. |
| `unitary-recomputation` | the unit value (`y₁/x₁` direct; `total/Σparts` sharing; `quantity/count` unit-rate) is recomputed independently and the scaled answer re-derived from it; the second route must match `answer.canonical`. |
| `inverse-product-invariant` | for `inverse_proportion`, `x₁·y₁ == x₂·y₂` (the product is conserved); the validator recomputes `k = x₁·y₁`, asserts `k mod x₂ == 0` (simple integer case), and that `answer == k/x₂` with `den==1`. A non-exact result would have been redrawn (§12); the validator confirms exactness here too. |
| `direct-inverse-distinct` | the validator confirms the task's declared relation matches its construction — a `direct_proportion` item's answer does **not** also satisfy the inverse invariant and vice-versa (guards against the `DIRECT_FOR_INVERSE` / `INVERSE_FOR_DIRECT` confusions becoming the *correct* answer, §10). |
| `unit-rate-reduced` | `unit_rate` answer is a reduced `Rational` `{num,den}` (`gcd(num,den)==1`); no approximate decimal is stored (§4 D). |
| `scale-factor-consistent` | for `simple_scale`, `answer = given · s` (enlargement) or `given / s` (reduction) per the **declared direction**; the validator re-applies the declared factor and direction and asserts exactness; an additive `given + (s−1)` or wrong-direction value **fails**. |

**F. Best-buy checks (`best_buy`) — realised on the `multiple-choice` answer type**

| Check name | Assertion |
|---|---|
| `unit-rate-per-option` | each option's `unitRate_j = price_j / size_j` is an independently recomputed reduced `Rational`, recorded in `solution.steps[]`/feedback (not in a structured canonical); **no currency conversion** appears (single currency, §3 / deferral list). |
| `best-value-is-min-unit-rate` | the `multiple-choice` `answer.canonical` chosen option id is the option with the **strictly minimum** unit rate; the recomputed witness rates agree; choosing the lowest *price* rather than the best *value* **fails** (the `CHOOSES_LOWEST_PRICE_NOT_BEST_VALUE` trap, §10). |
| `no-best-buy-tie` | the construction guarantees a **strict** minimum (no two options share the minimum unit rate); a tie would have been redrawn (§12), and the validator re-asserts strict inequality so the keyed option is unambiguous. |

**G. Visual + leakage checks (every diagrammed task)** — **role/intent based**, per the canonical-SVG discipline (a coincidental *given* quantity equal to the answer is **not** leakage; a dedicated answer/solution annotation in the *student* figure **is**). Leakage is judged by element **role/class**, never by numeric value set-equality.

| Check name | Assertion |
|---|---|
| `svg-realises-data` | recompute the canonical monochrome SVG from `params` via the §8 non-Cartesian renderer (bar model / double number line / proportional table; integer pixel coords via the family `gridRound`; **root `class="cx-figure"`** — the shared theme root, NOT a `ratio-figure` root; the family's additive theme is the *theme id* `spi-math-ratio-theme/1`, a different namespace; `role="img"` + `<title>`/`<desc>` first children; data-table fallback) and assert `== media[0].svg` **byte-for-byte**, Py↔TS identical. **Parity scope:** only the canonical monochrome `media[0].svg` is Py/TS byte-compared; the four themed presentations and the 6000×4200 export are TS-only derivations (§16), audited in §14 but not byte-compared against Python. |
| `figure-realises-ratio` | every drawn bar segment / number-line tick / table cell maps to a `params` part, total, or given quantity; segment **lengths are proportional** to the exact parts under the chosen rational scale, built from a **single shared cumulative integer x-array** so adjacent segments share boundary integers and double-number-line lanes index one shared tick array (no per-lane/per-segment re-rounding), §8. |
| `only-given-values-shown` | **role-keyed, not value-keyed**: the **student** figure contains no element with `role/class` `cx-ans` and no unknown-hatch (`cx-bar-unknown`) carrying the asked value; every value-bearing label element is bound by **role** to a `params` given-quantity slot. A coincidental given value numerically equal to the answer is allowed (it is `role=given`); a derived value is forbidden by role even if it equals a given. |
| `no-result-in-student-figure` | no computed share/part/rate/ratio appears as an answer/solution annotation in the student render or its `dataTableFallback`/`spokenMath`/`longDescription` (role-keyed). |
| `answer-key-overlay-additive-only` | the canonical base-geometry fragment is **byte-identical** between the student and answer-key SVGs; the **only** inter-channel difference is the additive answer-overlay group (the solved shares / completed cells / chosen best-buy), on a distinct asset id, never in a student export. |
| `unknown-not-measurable-from-figure` | for `missing_part`, `share_*`, `unit_rate`, `direct_proportion`/`inverse_proportion`, the unknown is **not** recoverable by measuring SVG pixel lengths (the unknown segment is rendered to a fixed neutral length or shown as a labelled `?`, not to true scale) — the bar-model analogue of the mensuration hidden-dimension rule. |
| `theme-extension-intact` | the figure uses the **additive** versioned `spi-math-ratio-theme/1` composed over the shared cartesian theme (following the `data-chart-theme` / `mensuration-theme` additive mechanism, **not** modifying the shared cartesian theme); the family's own new variables are namespaced `--cx-ratio-*` (e.g. `--cx-ratio-ans`, `--cx-ratio-lbl`, `--cx-ratio-unknown-mark`) so **no name collides with cartesian/data-chart/mensuration/transformations**; known/unknown and each part are distinguished by **shape/dash/fill** (the unknown-vs-known hatch carried by a CSS **class** `.cx-figure .cx-ratio-unknown-hatch`, never inline `var()` presentation attributes, so it survives `exportSvg`), never colour alone, verified in `print` (authoritative) and `premium-dark`; 6000×4200 export preserves exact proportions and is self-contained (no unresolved `var()` in any presentation attribute). |

**H. Diagnostic discipline (every task)** — owner rule N adapted (this family mixes FR-only and MC-eligible tasks)

| Check name | Assertion |
|---|---|
| `diagnostic-recompute` | each stored misconception **diagnostic value** is re-derived by running the *same* `MISC.RATIO.*` adapter (§10) on the recomputed `ctx`; the validator reproduces every diagnostic value independently. For MC-eligible tasks, every selectable distractor traces to a `MISC.RATIO.*` adapter (no arbitrary distractor) and the three distractors are **distinct** from each other and from the key. |
| `diagnostic-distinct-from-correct` | no diagnostic value equals the canonical answer (value-and-shape); a rule whose recomputed result would collide with the correct value returns `null` and is omitted (collision/inapplicability, §10). |
| `diagnostic-incomplete-is-text` | a malformed/incomplete predicted answer (e.g. a ratio the student would leave unsimplified when the schema requires simplest form) stores a `studentResponseText` + `expectedResultCode`, **never** a manufactured invalid canonical (§10). |

The required-cell space the review pack must cover is **derived from the 10k distribution report** by the approved reachability-driven **COVERAGE-MATRIX** machinery (stats v1.0.2), reused by name in §14: required cells = every task × supported interaction × **reachable** difficulty band × realised answer shape (ratio 2-part / 3-part; integer / rational; table-completion; multiple-choice best-buy; simplified-input / unsimplified-input). `difficulty-in-band` plus the distribution report prove every declared band is reachable (§11.4).

---

## 10. Misconception and diagnostic registry

The registry is `MISC.RATIO.*`, authored as a byte-parity pair (`oracle/spi_oracle/ratio_misconceptions.py` + `domains/proportion/ratio-misconceptions.ts`), mirroring the approved `MISC.MENS.*` / `MISC.STAT.*` structure exactly. **This registry is the single source of truth** for diagnosed wrong answers across the solver (worked-solution pitfalls), the checker (targeted feedback + MC distractors where eligible), and the independent validator (independent recomputation). Every other section (§3, §5, §9, §11, §14) references these ids **verbatim**; `ratio-graph.test.ts` asserts no alternative spelling appears anywhere. **Single-source IDs only — there are no `DESC_*`-style alternates.**

Each diagnostic is a record `{ id, title, formula, description, observableError, feedback, kind, diagnosticOnly, applicability, adapter }`:

- **`formula`** — the wrong rule as an **exact formula** over `ctx` (internal); never an arbitrary nearby wrong number.
- **`description`** — internal note.
- **`observableError`** — what a marker sees, **no internal symbols**.
- **`feedback`** — targeted feedback phrased from displayed values, **no internal symbols**.
- **`kind`** — `value` (wrong number/ratio), `order` (correct multiset, wrong order), `form` (correct value, wrong form/representation), or `choice` (wrong option in a `multiple-choice` best-buy).
- **`diagnosticOnly`** — `true` ⇒ surfaced as feedback/worked-solution pitfall only, never a selectable MC option and no manufactured canonical (an incomplete/malformed response stores `studentResponseText` + `expectedResultCode`).
- **`applicability(ctx) -> bool`** — eligibility predicate; combined with `RULES_BY_TASK` (§10.4, preference-ordered). Applicability is set so that **every MC-eligible task in §9.2 has at least three rules whose adapters return non-`null`, mutually-distinct, key-distinct values on its in-band draws** (cross-checked by `ratio-graph.test.ts` and the §11.4 reachability sweep); otherwise that task could never build a 3-distractor MC and the "MC-eligible" claim would be false.
- **`adapter(ctx) -> TypedAnswer | {studentResponseText, expectedResultCode} | null`** — deterministic; supports **independent recomputation** (the validator re-runs the same adapter), returning the wrong typed answer in the task's answer shape, OR a `studentResponseText`+`expectedResultCode` pair for an incomplete/malformed response, OR `null` for its **collision/inapplicability behaviour**.

The shared `ctx` exposes the solver's exact intermediates so adapters never re-derive arithmetic:

```
ctx = { task, answerShape, correct,                 // the typed canonical answer
        labels: string[],                            // ordered category labels
        originalParts: int[], parts: int[], g: int,  // unsimplified, simplified, gcd
        total?: int, sharePart?: int, shares?: {label:int},
        knownPart?: int, knownTermIndex?: 0|1, missing?: Rational,
        x1?,y1?,x2?: Rational, unit?: Rational, product?: int,   // direct / inverse / unit-rate
        whole?: int, fractionPart?: int,             // ratio<->fraction
        scaleFactor?: Rational, scaleDir?: "enlarge"|"reduce", given?: Rational,
        options?: {id,price,size,unitRate}[] }       // best-buy (multiple-choice)
```

Result codes are the family's **single lower-kebab result-code vocabulary** (§5, decision F), used identically here and in §5/§7 — **never UPPER_SNAKE**. The `expectedResultCode` of every diagnostic is one of the §5 ratio codes (`correct`, `equivalent-not-simplified` with the separate boolean `partial: true`, `wrong-order`, `wrong-ratio`, `wrong-number-of-parts`, `zero-or-negative-part`, `unsupported-term`, `unparsed-trailing-text`, `malformed-response`), or — for best-buy/choice diagnostics — one of the choice codes `correct` / `wrong-choice` / `malformed-response`, or — for share table-completion diagnostics — the platform's existing table-completion checker code. There is **no** `CORRECT`, `EQUIVALENT_NOT_SIMPLEST`, `WRONG_VALUE`, `WRONG_FORM`, `WRONG_CHOICE`, `MALFORMED_RATIO`, `INCOMPLETE`, or any other UPPER_SNAKE/slash-style/generic spelling anywhere. (The wrong-value form errors — an unsimplified equivalent under a simplest-form-required task — map to `equivalent-not-simplified` + `partial: true`; an incomplete/malformed predicted response maps to `malformed-response`.)

### 10.1 The sixteen `MISC.RATIO.*` diagnostics

All sixteen named diagnostics from the brief, one-to-one (no extras, none deferred-list). Where a rule's applicability is extended beyond the obvious task so an MC-eligible task can source three distinct distractors (B4), the **exact formula is stated for that task** — never an arbitrary nearby number:

| Id | Title · exact formula | kind / diagnosticOnly | applicability | observableError → feedback | adapter result | expected result code |
|---|---|---|---|---|---|---|
| `MISC.RATIO.DOES_NOT_SIMPLIFY_FULLY` | Does not simplify fully · divides by a **proper divisor** `d` of `g` (`1<d<g`, smallest such `d`): `[p/d]` | `form` / `false` | `simplify`, `write_from_quantities`, `fraction_to_ratio` where `g` is composite (∃ such `d`) | Leaves the ratio in a smaller-but-not-simplest form. → "This ratio still has a common factor — keep dividing until the only common factor is 1." | `ratio {parts:[p/d]}` (still reducible) | `equivalent-not-simplified` (`partial: true`) |
| `MISC.RATIO.EQUIVALENT_BUT_UNSIMPLIFIED_WHEN_SIMPLEST_REQUIRED` | Equivalent but unsimplified when simplest required · returns `originalParts` unchanged | `form` / `false` | `simplify`, `write_from_quantities`, `fraction_to_ratio` where `g>1` and the task **requires** simplest form | Gives an equivalent ratio that has not been simplified at all. → "That ratio is equal in value, but the question asks for the simplest form." | `ratio {parts: originalParts}` (gcd>1) | `equivalent-not-simplified` (`partial: true`) |
| `MISC.RATIO.REVERSES_ORDER` | Reverses order · `reverse(parts)` (two-part) / a fixed transposition (three-part) | `order` / `false` | `simplify`, `write_from_quantities`, `fraction_to_ratio` where `parts` not palindromic | Writes the parts in the wrong order (e.g. swaps the two categories). → "Order matters: match each number to the right category in the order asked." | `ratio {parts: reverse(parts)}` | `wrong-order` |
| `MISC.RATIO.ADDS_PARTS_INCORRECTLY` | Adds parts incorrectly · uses `sum(parts)` as a single quantity instead of keeping the ratio | `value` / `false` | `write_from_quantities`, `fraction_to_ratio`, `share_two_part`, `share_three_part` | Adds the parts together instead of keeping them as a comparison. → "Don't add the parts — a ratio compares the quantities side by side." | share: `integer {Σparts·unit}`; `fraction_to_ratio`: `ratio {parts:[a+(b−a)]}` collapsed ⇒ `studentResponseText:"a+b"`; write: `studentResponseText:"a+b"` | share: platform table-completion wrong-cell code; ratio tasks: `malformed-response` (collapsed/incomplete ratio) |
| `MISC.RATIO.TREATS_ONE_PART_AS_WHOLE` | Treats one part as the whole · `share_k = total` (assigns the whole total to one share) / `ratio_to_fraction`: `partᵢ/partᵢ = 1` | `value` / `false` | `share_two_part`, `share_three_part`, `ratio_to_fraction` | Gives one category the entire amount instead of its share. → "Split the total across **all** the parts, not just one." | share: `table-completion` `share_k=total` (others 0); `ratio_to_fraction`: `exact-rational {1/1}` | share: platform table-completion wrong-cell code; `ratio_to_fraction`: platform exact-rational wrong-value code |
| `MISC.RATIO.WRONG_TOTAL_PARTS` | Wrong total parts · **undercounts by one**: `unit = total/(Σparts − 1)` (single fixed direction — `−1` only, never `±1`) | `value` / `false` | `share_two_part`, `share_three_part`, `ratio_to_fraction` (uses `partᵢ/(Σparts−1)`) | Divides by the wrong number of parts. → "Add **all** the ratio numbers to get the total number of parts first." | share: `table-completion` from `unit'=total/(Σparts−1)` (`null` if `unit'` non-integer); `ratio_to_fraction`: `exact-rational {partᵢ/(Σparts−1)}` (`null` if collides) | platform wrong-value code for the predicted shape (`exact-rational`/`integer`/`table-completion`) |
| `MISC.RATIO.DIVIDES_BY_ONE_PART_INSTEAD_OF_TOTAL` | Divides by one part instead of the total · `unit = total/part₁` then `·part_k` | `value` / `false` | `share_two_part`, `share_three_part`, `missing_part` | Divides by a single ratio number instead of the sum of all parts. → "Divide the total by the **sum** of the parts, not by one part." | `table-completion`/`exact-rational` from `unit'=total/part₁` (`null` if non-integer / collides) | platform wrong-value code for the predicted shape (`table-completion`/`exact-rational`) |
| `MISC.RATIO.MULTIPLIES_INSTEAD_OF_DIVIDING_IN_UNITARY` | Multiplies instead of dividing in unitary · `unit = y₁·x₁` (should be `y₁/x₁`) | `value` / `false` | `direct_proportion`, `unit_rate`, `inverse_proportion` | Multiplies to find one unit instead of dividing. → "To find the value of **one**, divide, don't multiply." | `exact-rational {y₁·x₁·…}` (`null` if collides) | platform wrong-value code for the predicted shape (`exact-rational`/`integer`/`table-completion`) |
| `MISC.RATIO.DIVIDES_INSTEAD_OF_MULTIPLYING_IN_UNITARY` | Divides instead of multiplying in unitary · `answer = unit/x₂` (should be `unit·x₂`) | `value` / `false` | `direct_proportion` | Divides by the new amount instead of multiplying by it. → "After finding one unit, **multiply** by how many you need." | `exact-rational {unit/x₂}` (`null` if collides) | platform wrong-value code for the predicted shape (`exact-rational`/`integer`/`table-completion`) |
| `MISC.RATIO.DIRECT_FOR_INVERSE` | Direct method for an inverse problem · `answer = (y₁/x₁)·x₂` on an inverse task | `value` / `false` | `inverse_proportion` | Scales **up** when more workers/taps means **less** time. → "This is inverse: as one goes up, the other goes down — use the constant product." | `integer/exact-rational {(y₁·x₂)/x₁}` (`null` if collides) | platform wrong-value code for the predicted shape (`exact-rational`/`integer`/`table-completion`) |
| `MISC.RATIO.INVERSE_FOR_DIRECT` | Inverse method for a direct problem · `answer = (x₁·y₁)/x₂` on a direct task | `value` / `false` | `direct_proportion` | Scales **down** when both quantities should grow together. → "This is direct: both grow together — find one unit, then multiply." | `exact-rational {(x₁·y₁)/x₂}` (`null` if collides) | platform wrong-value code for the predicted shape (`exact-rational`/`integer`/`table-completion`) |
| `MISC.RATIO.COMPARES_PRICES_WITHOUT_UNIT_RATE` | Compares prices without a unit rate · chooses by **raw price** ignoring size | `choice` / `false` | `best_buy` | Compares total prices without working out the price per unit. → "Work out the cost of **one** (the unit rate) before comparing." | `multiple-choice {chosen = argmin(price_j)}` (`null` if that equals the best-value option) | `wrong-choice` |
| `MISC.RATIO.CHOOSES_LOWEST_PRICE_NOT_BEST_VALUE` | Chooses lowest price, not best value · `chosen = argmin(price_j)` when it differs from `argmin(unitRate_j)` | `choice` / `false` | `best_buy` | Picks the cheapest pack rather than the best value for money. → "Cheapest overall isn't always best value — compare price per unit." | `multiple-choice {chosen = argmin(price_j)}` | `wrong-choice` |
| `MISC.RATIO.SCALE_FACTOR_WRONG_DIRECTION` | Scale factor wrong direction · `given/s` where it should be `given·s` (or the reverse): the inverted operation; for `best_buy`, inverts the price-per-unit / units-per-price direction and so selects the worse-value option | `value` / `choice` / `false` | `simple_scale`, `best_buy` (per §3.1 reconciliation) | Multiplies by the scale where it should divide (or the reverse); for best-buy, compares in the inverted rate direction. → "Decide first whether the real thing is **bigger** or **smaller** than the model / which rate direction makes one unit cheaper." | `simple_scale`: `exact-rational` with inverted operation; `best_buy`: `multiple-choice {chosen = the worse-value option under the inverted rate}` (`null` if collides) | `simple_scale`: platform wrong-value code (`exact-rational`/`integer`); `best_buy`: `wrong-choice` |
| `MISC.RATIO.ADDITIVE_DIFFERENCE_INSTEAD_OF_MULTIPLICATIVE_SCALE` | Additive difference instead of multiplicative scale · `answer = given + (s−1)` (adds a constant instead of scaling) | `value` / `false` | `simple_scale`, `direct_proportion` | Adds a fixed amount instead of multiplying by the scale factor. → "Proportion **multiplies** — find the scale factor and multiply, don't add a constant." | `exact-rational {given + (s−1)}` (`null` if collides) | platform wrong-value code for the predicted shape (`exact-rational`/`integer`/`table-completion`) |
| `MISC.RATIO.RATIO_TO_FRACTION_ONE_PART_OVER_OTHER_NOT_OVER_WHOLE` | Ratio→fraction part over other part, not over whole · `partᵢ / partⱼ` instead of `partᵢ / Σparts` | `value` / `false` | `ratio_to_fraction` | Writes one part over the **other** part instead of over the whole. → "A fraction of the whole is the part over the **total** of all parts." | `exact-rational {partᵢ/partⱼ}` (`null` if collides) | platform wrong-value code for the predicted shape (`exact-rational`/`integer`/`table-completion`) |

All sixteen are present, each with an **exact formula** (never a manufactured nearby number). The applicability lists above are **widened** exactly enough that each MC-eligible §9.2 task has ≥3 qualifying rules: `ratio_to_fraction` draws from `RATIO_TO_FRACTION_ONE_PART_OVER_OTHER_NOT_OVER_WHOLE`, `TREATS_ONE_PART_AS_WHOLE`, `WRONG_TOTAL_PARTS` (each with a stated `ratio_to_fraction` formula); `fraction_to_ratio` from `REVERSES_ORDER`, `DOES_NOT_SIMPLIFY_FULLY`, `EQUIVALENT_BUT_UNSIMPLIFIED_WHEN_SIMPLEST_REQUIRED`, `ADDS_PARTS_INCORRECTLY`. The four `kind:value`/`order`/`form` rules that could in principle reproduce the correct answer (a palindromic ratio under `REVERSES_ORDER`, an already-simplest ratio under the unsimplified rules, a `WRONG_TOTAL_PARTS` that yields the same shares) return **`null`** under their collision/inapplicability clause and are then **omitted** — never counted as exercised coverage (§14).

### 10.2 Incomplete / malformed predicted responses (no manufactured canonical)

Where a misconception produces a structurally **invalid** answer rather than a wrong value — e.g. a student who leaves `4:6` when simplest form is required, or writes `a+b` for a "write a ratio" task — the adapter returns `{studentResponseText, expectedResultCode}` (e.g. `{"4:6","equivalent-not-simplified"}` carrying `partial: true`; `{"a+b","malformed-response"}`), **never** a fabricated invalid `answer.canonical`. The `equivalent-not-simplified` and `malformed-response` codes drive the parser/checker's partial-feedback path (§5), so the schema never has to admit an invalid canonical to represent a misconception.

### 10.3 MC distractor sourcing (MC-eligible tasks only)

For the MC-eligible tasks (§9.2), the selectable distractors are drawn **only** from this registry, in `RULES_BY_TASK` preference order, taking the first three whose `adapter` returns a non-`null`, mutually-distinct, key-distinct value. Because applicability (§10.1) guarantees ≥3 qualifying rules per MC-eligible task on its in-band draws, a well-formed MC build normally succeeds; if a particular seed nonetheless yields fewer than three distinct distractors (e.g. a small-number `ratio_to_fraction` where `1/3`, `PART_OVER_OTHER`, and `WRONG_TOTAL_PARTS` collide — the generator therefore constrains MC-eligible `ratio_to_fraction` draws to `Σparts ≥ 4` with distinct part values, and excludes all-parts-equal cases like `1:1`, per §12), the generator **deterministically redraws** to an MC-eligible case (or returns `interaction-not-supported`) — an MC item is never padded with an arbitrary distractor. The six FR-only tasks of decision C (`write_from_quantities`, `share_two_part`, `share_three_part`, `missing_part`, `unit_rate`, `simple_scale`) use the registry purely as **targeted free-response feedback**, and an explicit MC request on any of them returns `interaction-not-supported`.

### 10.4 Task → applicable-diagnostic map (`RULES_BY_TASK`)

Keyed on the twelve §9.1 slugs, preference-ordered (leading entries become MC distractors where eligible; all entries are feedback). Every id listed for a task is `applicable` to that task in §10.1 (no §3.1-vs-§10 contradiction):

```
simplify                : EQUIVALENT_BUT_UNSIMPLIFIED_WHEN_SIMPLEST_REQUIRED,
                          DOES_NOT_SIMPLIFY_FULLY, REVERSES_ORDER
write_from_quantities   : REVERSES_ORDER, EQUIVALENT_BUT_UNSIMPLIFIED_WHEN_SIMPLEST_REQUIRED,
                          ADDS_PARTS_INCORRECTLY, TREATS_ONE_PART_AS_WHOLE
ratio_to_fraction       : RATIO_TO_FRACTION_ONE_PART_OVER_OTHER_NOT_OVER_WHOLE,
                          TREATS_ONE_PART_AS_WHOLE, WRONG_TOTAL_PARTS
fraction_to_ratio       : REVERSES_ORDER, DOES_NOT_SIMPLIFY_FULLY,
                          EQUIVALENT_BUT_UNSIMPLIFIED_WHEN_SIMPLEST_REQUIRED, ADDS_PARTS_INCORRECTLY
share_two_part          : DIVIDES_BY_ONE_PART_INSTEAD_OF_TOTAL, WRONG_TOTAL_PARTS,
                          TREATS_ONE_PART_AS_WHOLE, ADDS_PARTS_INCORRECTLY
share_three_part        : DIVIDES_BY_ONE_PART_INSTEAD_OF_TOTAL, WRONG_TOTAL_PARTS,
                          TREATS_ONE_PART_AS_WHOLE, ADDS_PARTS_INCORRECTLY
missing_part            : DIVIDES_BY_ONE_PART_INSTEAD_OF_TOTAL, REVERSES_ORDER,
                          TREATS_ONE_PART_AS_WHOLE
direct_proportion       : INVERSE_FOR_DIRECT, DIVIDES_INSTEAD_OF_MULTIPLYING_IN_UNITARY,
                          MULTIPLIES_INSTEAD_OF_DIVIDING_IN_UNITARY,
                          ADDITIVE_DIFFERENCE_INSTEAD_OF_MULTIPLICATIVE_SCALE
inverse_proportion      : DIRECT_FOR_INVERSE, MULTIPLIES_INSTEAD_OF_DIVIDING_IN_UNITARY
unit_rate               : MULTIPLIES_INSTEAD_OF_DIVIDING_IN_UNITARY
best_buy                : CHOOSES_LOWEST_PRICE_NOT_BEST_VALUE,
                          COMPARES_PRICES_WITHOUT_UNIT_RATE,
                          SCALE_FACTOR_WRONG_DIRECTION
simple_scale            : SCALE_FACTOR_WRONG_DIRECTION,
                          ADDITIVE_DIFFERENCE_INSTEAD_OF_MULTIPLICATIVE_SCALE
```

`ratio-graph.test.ts` asserts `keys(RULES_BY_TASK) == RATIO_TASKS`, that every referenced id exists in the registry **and is `applicable` to the keying task** (no dangling, no §3.1-vs-§10 applicability contradiction, no alternative spelling), and that every one of the sixteen ids appears in at least one list (no orphan diagnostic). The **MC-eligible tasks (decision C)** are exactly `simplify`, `ratio_to_fraction`, `fraction_to_ratio`, `direct_proportion`, `inverse_proportion`, and `best_buy` (MC-only); each lists **≥3** misconception-backed rules whose adapters yield three distinct, key-distinct distractors/options on its in-band draws — `best_buy` draws its three from `CHOOSES_LOWEST_PRICE_NOT_BEST_VALUE`, `COMPARES_PRICES_WITHOUT_UNIT_RATE`, and `SCALE_FACTOR_WRONG_DIRECTION` (applicability widened to best-buy per §3.1), so no non-misconception foil is needed. The remaining six tasks — `write_from_quantities`, `share_two_part`, `share_three_part`, `missing_part`, `unit_rate`, `simple_scale` — are **FR-only (decision C)**: their `RULES_BY_TASK` entries are used purely as **targeted free-response feedback**, never as selectable MC options.

### 10.5 Diagnostic invariants enforced by the independent validator

For every item the validator independently re-runs each applicable rule's `adapter` on the recomputed `ctx` (`diagnostic-recompute`, §9.4-H) and asserts:

1. **Distinct from correct** — no diagnostic value equals the canonical answer (value *and* shape); a colliding rule returns `null` and is omitted (collision/inapplicability, §10.1).
2. **Reproduced, not copied** — the validator's recomputed diagnostic set equals the stored set, via the same independent route as `closure-agreement`.
3. **Exact-formula, not arbitrary** — every stored diagnostic value is exactly the `adapter` output; no value lies "nearby" without a generating formula.
4. **Feedback truthful** — each `feedback` states the wrong rule in displayed terms and is true for the dataset.
5. **MC-distractor integrity** (the six MC-eligible items of decision C) — the three options are **all registry-sourced** (`best_buy` draws its three from `CHOOSES_LOWEST_PRICE_NOT_BEST_VALUE`, `COMPARES_PRICES_WITHOUT_UNIT_RATE`, `SCALE_FACTOR_WRONG_DIRECTION`; no non-misconception foil is used), mutually distinct, key-distinct; an MC request that cannot meet this redrew or returned `interaction-not-supported` (never silently FR), per §9.2/§10.3. An explicit MC request on any of the six FR-only tasks (decision C) returns `interaction-not-supported`.

This keeps `MISC.RATIO.*` the single source of truth for diagnosed wrong answers across the solver, the checker, and the validator, with full Python↔TypeScript byte parity on the underlying exact values.

---

## 11. Difficulty model

### 11.1 Mechanism reused, not reinvented

Ratio difficulty uses the platform difficulty pipeline verbatim. Every item computes a vector of **schema closed-enum axes** (`question-item.schema.json#/$defs/difficultyProfile.axes` — the CLOSED 16-member set `{numericalComplexity, algebraicComplexity, reasoningSteps, abstraction, representation, familiarity, readingDemand, informationDensity, irrelevantInformation, requiredConnections, exactVsApproximate, calculatorDependence, scaffolding, proofDemand, interpretationDemand, modellingDemand}`, `additionalProperties:false`), forms a weighted score in `[0,1]`, and derives `overallBand` through the shared `bandFromScore` in `core/difficulty/band.ts`:

```
score      = clamp01( Σ w_axis · axis_value )                 # weights sum to 1; scaffolding enters as (1 − scaffolding)
overallBand = bandFromScore(score) = min(5, 1 + floor(clamp01(score) · 5))   # 0–0.2→1 … 0.8–1→5
```

The family **does not define its own band function** and **does not invent axes** (per `DIFFICULTY_MODEL.md` §2–3 and the schema's `additionalProperties:false`). `round3` (round-half-up to 3 dp, int-when-whole) is applied wherever an axis or score is serialized so the integer-collapsing parity contract holds. The Python `spi_oracle/difficulty.py` mirror and TS `band.ts` produce byte-identical scores (oracle-first; golden + parity fixtures guard it).

### 11.2 Owner difficulty factors mapped onto the closed axes

The owner's listed factors are mapped onto existing schema axes (no new axis name is emitted). Ratio is a numeric-procedural family and deliberately exercises a **subset** of the sixteen axes:

| Axis | Owner factor(s) it carries in this family |
|---|---|
| `numericalComplexity` | small vs larger numbers; presence/absence of common factors; integer vs **rational** unit rate / answer. |
| `reasoningSteps` | number of reasoning steps: 1 (simplify, unit rate) → 2 (share two-part, missing part, direct proportion) → 3+ (three-part share, inverse via product, best-buy compare-then-decide). |
| `informationDensity` | two-part vs **three-part** ratio; count of given quantities/labels; number of best-buy options; table/bar-model reading demand. |
| `representation` | reading off a **bar model / double number line / proportional table** vs a bare numeric pair; three-part and table-completion raise it. |
| `interpretationDemand` | total-known vs one-part-known; **direct vs inverse** selection; ratio→fraction over-the-whole; best-value vs lowest-price; scale **direction**. |
| `scaffolding` | inverse axis `(1 − scaffolding)`: a given worked unit, all parts labelled, or a stated scale direction **lowers** difficulty; an inferred direction / one-part-known **raises** it. |
| `readingDemand` | context-gated only: `0` when `params.context == none`; a small positive value **only when a worded `verbal-context` is present** (the §2 `verbal-context`-tagged items are exactly the items that lift `readingDemand` off zero — a testable correspondence). |

**Pinned-to-zero axes (v1.0.0).** `algebraicComplexity`, `abstraction`, `familiarity`, `irrelevantInformation`, `requiredConnections`, `exactVsApproximate`, `calculatorDependence`, `proofDemand`, and `modellingDemand` are **not** drivers in v1.0.0 and are emitted as `0`. (`exactVsApproximate = 0` reflects exact-only arithmetic — no approximation exists in this family, per the deferral list; `calculatorDependence = 0` reflects the middle-school no-calculator policy; `proofDemand = 0` because no continued/compound-proportion proof is in scope.) The complete pinned-zero set is therefore: `algebraicComplexity, abstraction, familiarity, irrelevantInformation, requiredConnections, exactVsApproximate, calculatorDependence, proofDemand, modellingDemand` — exactly the nine axes that are neither a driver above nor the context-gated `readingDemand`. The seven drivers (six structural + context-gated `readingDemand`) plus these nine enumerate all sixteen schema axes exactly once.

### 11.3 ONE machine-readable source of truth

The objective difficulty ranges, per-task structural floors, supported interactions, answer shapes, and difficulty-axis weights all derive from **one versioned descriptor**, `core/difficulty/ratio-difficulty.json` (mirrored verbatim by `oracle/spi_oracle/ratio_difficulty.py`), from which both the spec tables here and the §14 review-pack expectations are generated — so the two can never drift. `answerShape` is the schema `answer.type`; for the **two** integer-OR-rational tasks (`direct_proportion`, `simple_scale`) it is the **pair** `["integer","exact-rational"]` (the validator's `answer-type-consistency` accepts either, choosing `integer` iff `den==1`, §9.2/§9.3), so the descriptor never forces a single shape the solver cannot honour. `missing_part` and `inverse_proportion` are **integer-only** (decision E / §9.3), and `unit_rate` is `exact-rational`. Its shape (excerpt):

```json
{
  "generatorId": "gen.proportion.ratio",
  "version": "1.0.0",
  "weights": {
    "reasoningSteps": 0.26, "informationDensity": 0.20, "interpretationDemand": 0.20,
    "representation": 0.14, "numericalComplexity": 0.12, "scaffolding": 0.06, "readingDemand": 0.02
  },
  "pinnedZeroAxes": ["algebraicComplexity","abstraction","familiarity","irrelevantInformation",
    "requiredConnections","exactVsApproximate","calculatorDependence","proofDemand","modellingDemand"],
  "tasks": {
    "simplify":                   { "objectiveId": "SPI.MIDDLE.RATIO.SIMPLIFY.01",
                                    "difficultyRange": {"min":1,"max":3}, "taskFloorBand": 1,
                                    "supportedInteractions": ["free-response","multiple-choice"],
                                    "answerShape": "ratio" },
    "write_from_quantities":      { "objectiveId": "SPI.MIDDLE.RATIO.WRITE_FROM_QUANTITIES.01",
                                    "difficultyRange": {"min":1,"max":3}, "taskFloorBand": 1,
                                    "supportedInteractions": ["free-response"],
                                    "answerShape": "ratio" },
    "ratio_to_fraction":          { "objectiveId": "SPI.MIDDLE.RATIO.RATIO_TO_FRACTION.01",
                                    "difficultyRange": {"min":2,"max":3}, "taskFloorBand": 2,
                                    "supportedInteractions": ["free-response","multiple-choice"],
                                    "answerShape": "exact-rational" },
    "fraction_to_ratio":          { "objectiveId": "SPI.MIDDLE.RATIO.FRACTION_TO_RATIO.01",
                                    "difficultyRange": {"min":2,"max":3}, "taskFloorBand": 2,
                                    "supportedInteractions": ["free-response","multiple-choice"],
                                    "answerShape": "ratio" },
    "share_two_part":             { "objectiveId": "SPI.MIDDLE.RATIO.SHARE_TWO_PART.01",
                                    "difficultyRange": {"min":2,"max":3}, "taskFloorBand": 2,
                                    "supportedInteractions": ["free-response"],
                                    "answerShape": "table-completion" },
    "share_three_part":           { "objectiveId": "SPI.MIDDLE.RATIO.SHARE_THREE_PART.01",
                                    "difficultyRange": {"min":3,"max":4}, "taskFloorBand": 3,
                                    "supportedInteractions": ["free-response"],
                                    "answerShape": "table-completion" },
    "missing_part":               { "objectiveId": "SPI.MIDDLE.RATIO.MISSING_PART.01",
                                    "difficultyRange": {"min":2,"max":4}, "taskFloorBand": 2,
                                    "supportedInteractions": ["free-response"],
                                    "answerShape": "integer" },
    "direct_proportion":          { "objectiveId": "SPI.MIDDLE.RATIO.DIRECT_PROPORTION.01",
                                    "difficultyRange": {"min":2,"max":4}, "taskFloorBand": 2,
                                    "supportedInteractions": ["free-response","multiple-choice"],
                                    "answerShape": ["integer","exact-rational"] },
    "inverse_proportion":         { "objectiveId": "SPI.MIDDLE.RATIO.INVERSE_PROPORTION.01",
                                    "difficultyRange": {"min":3,"max":4}, "taskFloorBand": 3,
                                    "supportedInteractions": ["free-response","multiple-choice"],
                                    "answerShape": "integer" },
    "unit_rate":                  { "objectiveId": "SPI.MIDDLE.RATIO.UNIT_RATE.01",
                                    "difficultyRange": {"min":2,"max":3}, "taskFloorBand": 2,
                                    "supportedInteractions": ["free-response"],
                                    "answerShape": "exact-rational" },
    "best_buy":                   { "objectiveId": "SPI.MIDDLE.RATIO.BEST_BUY.01",
                                    "difficultyRange": {"min":3,"max":5}, "taskFloorBand": 3,
                                    "supportedInteractions": ["multiple-choice"],
                                    "answerShape": "multiple-choice" },
    "simple_scale":               { "objectiveId": "SPI.MIDDLE.RATIO.SIMPLE_SCALE.01",
                                    "difficultyRange": {"min":2,"max":4}, "taskFloorBand": 2,
                                    "supportedInteractions": ["free-response"],
                                    "answerShape": ["integer","exact-rational"] }
  }
}
```

The seven weights sum to `1.00`. They keep `numericalComplexity` intentionally **non-dominant** (per `DIFFICULTY_MODEL.md` §2), letting structural demand (steps, density, direct/inverse interpretation) carry the band. All weights and ranges are **provisional** until the 10k distribution report (§11.4). `ratio-graph.test.ts` asserts `keys(tasks) == RATIO_TASKS`, that each `objectiveId` equals `OBJECTIVE_BY_TASK[task]` (the §1.2 IDs), that `supportedInteractions` here equals `MC_ELIGIBLE_TASKS`/`SUPPORTED_INTERACTIONS` (§9.2), and that `answerShape` here equals `ANSWER_SHAPE_BY_TASK` (§9.2) — one source, no drift. The `best_buy` range here (`3..5`) is the **single source of truth**; §2/§3 derive their best-buy band from this record (the earlier §2 `2..4` value is superseded).

### 11.4 Clamping to objective ranges and reachability (bands PROVISIONAL)

Each objective declares `difficultyRange{min,max}` (1..5); the computed band is **clamped to the owning objective's declared range** before being written to `overallBand`, and is floored to `taskFloorBand`. The family commits to the platform invariant that **every declared band in every objective's range is reachable**: the **`SPI_SWEEP=10000` distribution report** must show ≥ 1 generated item per (task × declared band) cell. The **reachability-derived COVERAGE-MATRIX machinery (stats v1.0.2)** is reused exactly — required cells = every task × supported interaction × **reachable difficulty band** × realised answer shape (the shape tokens: `ratio:2part`, `ratio:3part`, `rational`, `integer`, `table:2`, `table:3`, `mc:best-buy`; plus `simplified-input` / `unsimplified-input` for the simplify/write tasks) — derived from the distribution report; the review-pack builder **FAILS on any uncovered reachable cell** (no false full-coverage claims). These coverage tokens are the single shape vocabulary shared with §14; the model-tag↔`answer.type`↔coverage-token mapping is declared once (`ratio`→`ratio:2part`/`ratio:3part`, `exact-rational`→`rational`, `integer`→`integer`, `table-completion`→`table:2`/`table:3`, `multiple-choice` best-buy→`mc:best-buy`) so §6/§7/§9/§11/§14 cannot diverge. A blocking `ratio-band-reachability.test.ts` (mirroring the stats coverage tests) fails CI if any declared band is empty after the sweep. **All declared bands are PROVISIONAL until the 10k distribution proves reachability**; provisional weights/ranges that leave a declared band unreachable are corrected (or the range narrowed) before approval — never papered over. Indicative landing bands (final ranges fixed by the report):

| Task slug (§9.1) | Typical structural profile | Indicative band |
|---|---|---|
| `simplify` | 1 step; band lifts with larger numbers / composite gcd | 1–3 |
| `write_from_quantities` | 1–2 steps; order + simplify | 1–3 |
| `ratio_to_fraction` | part-over-whole interpretation | 2–3 |
| `fraction_to_ratio` | complement + simplify | 2–3 |
| `share_two_part` | divide-by-total then scale; table read | 2–3 |
| `share_three_part` | 3 parts, higher density, table-completion | 3–4 |
| `missing_part` | one-part-known, cross-multiply | 2–4 |
| `direct_proportion` | unit then multiply; rational answers ↑ | 2–4 |
| `inverse_proportion` | product invariant; direct/inverse interpretation ↑ | 3–4 |
| `unit_rate` | single division; rational rate ↑ | 2–3 |
| `best_buy` | multi-option unit rates then decide | 3–5 |
| `simple_scale` | direction interpretation; reduce vs enlarge | 2–4 |

### 11.5 Monotonicity and parity guards

A property test (mirroring `DIFFICULTY_MODEL.md` §3) asserts the band is **monotonic in the obvious controls**: enlarging the numbers, moving from two-part to three-part, switching a task to its inverse/one-part-known form, moving from an integer to a rational answer, adding more best-buy options, or removing scaffolding (an inferred scale direction) must **not lower** the band. Two parity guards lock the axis vector:

- **Documented-subset equality.** A test asserts the emitted axis set is **exactly** the documented subset: the seven driver axes of §11.3 carry the computed values, the nine pinned-zero axes of §11.2 serialize as `0`, and `readingDemand` is `0` unless a worded `verbal-context` is present — with no other axis present and none of the sixteen omitted. Because the driver list and the pinned-zero list together enumerate all sixteen schema axes exactly once, Python and TS cannot silently diverge on which axes fire.
- **round3 serialization parity.** All axis values and the score pass through `round3`, preserving the int-when-whole serialization parity used by the golden/parity fixtures (a `0`-valued axis serializes as the integer `0`, byte-identically in both engines).

---

The three sections above are complete and consistent with the established conventions, and every applicable blocker has been resolved. Summary of fixes applied to my sections (9, 10, 11):

- **B3/B1 (slug + objective-ID drift — all four critics):** §9/§10/§11 now use the single §1.3 short slug set (`simplify`, `write_from_quantities`, `direct_proportion`, `inverse_proportion`, …) and the §1.2 objective IDs (`DIRECT_PROPORTION.01`, `INVERSE_PROPORTION.01`, no `_UNITARY` suffix). The banned superseded spellings are explicitly listed for the string-scan test.
- **B1/B3 `comparison` answer type (platform-fit + completeness + ratio-math):** `best_buy` re-modelled onto the live `multiple-choice` enum member (verified absent in `schemas/question-item.schema.json` lines 196–205; `multiple-choice` present at line 202); unit-rate witnesses live in `solution`/feedback, not a phantom `comparison` canonical. All `comparison` references in §9/§10/§11 retargeted to `multiple-choice` (`mc:best-buy` coverage token in §11.4).
- **`missing_part` type + divisibility (decision E):** §9.2/§9.3 declare `missing_part` **integer-only** in v1.0.0, consistent with §2.7/§3.3/§7/§10/§11/§12; the **hard, non-optional** divisibility precondition (`parts[knownIndex] ∣ knownValue`) makes the recovered value an exact integer by construction, re-asserted by the `missing-part-exact` validator check (§9.4-E) — no escape hatch, no exact-rational path.
- **B4 (ratio-math) MC applicability:** §10.1 applicability widened (with stated per-task exact formulas) so `ratio_to_fraction` and `fraction_to_ratio` actually source 3 distinct distractors; `best_buy`/`simple_scale` (2 registry rules) get a §3-declared flagged foil or redraw. §10.4 `RULES_BY_TASK` now matches §10.1 applicability with no contradiction.
- **I2/I3/I5/I6 + renderer cross-refs:** `direct_proportion` answerShape is the integer-OR-rational pair; `WRONG_TOTAL_PARTS` pinned to a single `−1` formula (no `±1`); result codes fixed to the **one canonical lower-kebab vocabulary** (decision F — no UPPER_SNAKE, no slash-style, no generic `wrong`/`partial`); §9.4-G renderer/leakage checks corrected to `cx-figure` root + `--cx-ratio-*` namespacing + class-driven hatch + role-keyed `only-given-values-shown` + shared-cumulative-array tick alignment + TS-only export parity scope; check-name vocabulary normalized.
- **completeness I1:** the model-tag ↔ `answer.type` ↔ coverage-token mapping is declared once in §11.4 and shared with §14.

Relevant file paths (all absolute): the target proposal `C:\Users\Mohamad Solaiman\OneDrive\Desktop\Claude Question generator\docs\GENERATOR_SPEC_proportion_ratio_PROPOSAL.md`; verified ground-truth files `C:\Users\Mohamad Solaiman\OneDrive\Desktop\Claude Question generator\schemas\question-item.schema.json` (enum lines 196–205; `multiple-choice` present, `comparison` absent), `C:\Users\Mohamad Solaiman\OneDrive\Desktop\Claude Question generator\oracle\check_conformance.py` (supports `minItems` only — `maxItems` is a new owner-visible branch), `C:\Users\Mohamad Solaiman\OneDrive\Desktop\Claude Question generator\core\difficulty\band.ts`, `C:\Users\Mohamad Solaiman\OneDrive\Desktop\Claude Question generator\core\curriculum\mensuration-objective-ids.ts`.

## 12. Edge-case and degeneracy policy

All rules below are enforced **inside the seeded backward-construction loop** (§6/§7): a candidate that violates any rule is **rejected and the seed deterministically redraws** (the same redraw discipline as the misconception-distractor and MC-eligibility loops), so a violating item is *never emitted* and *never drawn*. Every exclusion is **deterministically unreachable from the task loop**, not filtered after the fact and not silently downgraded. The independent validator (§9) re-checks each rule as a named gate using the **single canonical `checks[]` name vocabulary defined in §9.3** (referenced verbatim below — no alternative spellings), so a degenerate item cannot pass even if construction were wrong. The redraw is part of the deterministic call **order**, so Python↔TypeScript parity is preserved across every regeneration.

The `RATIO_TASKS` slugs referenced are the single canonical set of §1.3 / §3 (`simplify`, `write_from_quantities`, `ratio_to_fraction`, `fraction_to_ratio`, `share_two_part`, `share_three_part`, `missing_part`, `direct_proportion`, `inverse_proportion`, `unit_rate`, `best_buy`, `simple_scale`) — used verbatim, with **no** `write_ratio` / `simplify_ratio` / `direct_proportion_unitary` / `inverse_proportion_unitary` spelling anywhere.

### 12.1 Ratio-term degeneracy (rejected → redraw)

The canonical Ratio model (§6) forbids zero and negative parts in v1.0.0. These are made unreachable at construction, not repaired afterward.

| Condition | Rule | Named check (§9.3) |
| --- | --- | --- |
| Zero part anywhere in any ordered tuple | Every `parts[i] ≥ 1` (exact positive integer), in both unsimplified and simplified forms | `parts-positive` |
| Negative part anywhere | No `parts[i] < 0`; the sign is structurally impossible (parts are drawn from `[1 .. MAX_PART]`) | `parts-positive` |
| Non-integer part | Every `parts[i] ∈ ℤ`; ratio terms are integers only (a ratio carries no rational term in v1.0.0) | `parts-integer` |
| Canonical not in simplest form | `gcd(parts) == 1` in the *canonical* tuple (the simplified model); the unsimplified original is stored separately in `original` (§6) | `ratio-gcd-one` |
| Two-part `[a,b]` with `a == b` (i.e. `1:1`) | Excluded when it weakens the objective — see §12.4 (all-parts-equal policy) | `ratio-not-all-equal` (conditional) |

The ratio answer carries **no units and no zero/negative term** — this is the structural ground for §4's schema rule that a `ratio` answer forbids `units`/`measure`/`tolerance` and constrains `parts[]` to positive integers (`minItems:2`, `maxItems:3`, each `minimum:1`) with `gcd == 1`. A `parts-positive` / `parts-integer` / `ratio-gcd-one` violation is therefore *both* a construction-loop rejection *and* a schema/validator rejection (the NEGATIVE schema fixtures of §4 prove the structural part; `gcd==1` is an arithmetic predicate enforced by the §9 validator + offline conformance, not by JSON-Schema), so a degenerate ratio cannot enter the bank by any path.

### 12.2 Already-simplest-form policy (simplification tasks)

The `simplify` task (T1) and any task whose answer policy is **simplest-form-required** must present a ratio that is *not already* in lowest terms, so the simplification step is genuinely exercised — **unless** the item is an *intentional* low-band case that tests recognition of an already-simplest ratio.

| Situation | Rule | Named check (§9.3) |
| --- | --- | --- |
| `simplify` at band ≥ 2 draws an already-coprime input | Rejected → redraw: the presented `original` must have `gcd(original) > 1` so there is real work to do (`simplifyScaleFactor = gcd(original) ≥ 2`) | `simplify-has-common-factor` |
| `simplify` at band 1 (intentional recognition case) | **Allowed** with `gcd(original) == 1` *only* when `params.intentionalAlreadySimplest == true` is set by the band-1 constructor; the prompt explicitly asks "write in simplest form" and the answer equals the input | `already-simplest-is-intentional-or-rejected` |
| Any simplest-form-required task whose *equivalent* input happens to already be simplest | Rejected → redraw unless intentional, as above | `simplify-has-common-factor` |

The two policies (T1 input must have a common factor; T1 band-1 may intentionally not) are mutually exclusive per item and gated by the single `params.intentionalAlreadySimplest` flag, which the validator reads — there is no third interpretation. This flag is **only** legal for `simplify` (the constructor for every other task never sets it), asserted by `intentional-simplest-only-on-simplify`.

### 12.3 Equivalent-ratio acceptance policy (per-task, simplest-form vs not)

Whether an *equivalent-but-unsimplified* answer (e.g. `4:6` for a `2:3` ground truth) is accepted, rejected, or partially credited is a **per-task policy flag** `answerPolicy ∈ {accept-equivalent, require-simplest}` carried on the Ratio model (§6) and on every emitted item's `params`. It is the single source the §5 checker reads; §4/§5/§10/§14 all key off it. The result codes below are the single lower-kebab `RESULT_CODES` vocabulary of §5 (decision F) — `correct`, `equivalent-not-simplified` (carrying the separate boolean `partial: true`), `wrong-order`, `wrong-ratio`, `wrong-number-of-parts`, `zero-or-negative-part`, `unsupported-term`, `unparsed-trailing-text`, `malformed-response` — with **no** `UPPER_SNAKE`, slash-style, or alternative spelling (`reversed-order`, `zero-part`, `negative-part`, `malformed-ratio`, `unsupported-symbol`, generic `incorrect`/`wrong`/`partial` are all superseded and appear nowhere).

| Task class | `answerPolicy` | Behaviour of the §5 checker |
| --- | --- | --- |
| `simplify`; any task asking explicitly for *simplest form* | `require-simplest` | `2:3` accepted (`correct`); an **equivalent unsimplified** submission `4:6` returns `equivalent-not-simplified` (NOT full `correct`) with targeted "simplify fully" feedback (the diagnostic `MISC.RATIO.DOES_NOT_SIMPLIFY_FULLY`, §10) |
| `write_from_quantities` (T2) from quantities where the question does **not** demand simplest form | `accept-equivalent` | `2:3` **and** `4:6` **and** `20:30` all return `correct` (cross-multiplication equivalence, §5); order still matters |
| All other tasks whose answer is a ratio and whose wording does not demand simplest form | `accept-equivalent` (default) | equivalence accepted; reversed order still rejected (§12.5) |

The checker NEVER silently "auto-simplifies" a `require-simplest` submission into a pass; an unsimplified equivalent under `require-simplest` returns the distinct result code `equivalent-not-simplified` carrying `partial: true` — not `correct` and not `wrong-ratio`. Under `accept-equivalent`, an unsimplified equivalent is `correct`. The review-pack ratio-checker matrix (§14) proves **both** policies with pinned rows.

### 12.4 All-parts-equal and trivial-ratio degeneracy

A ratio in which all parts are equal (`1:1`, `1:1:1`) is **excluded when it weakens the objective**, because it removes the part-distinction the task is meant to assess (sharing, missing-part, fraction-of-whole all collapse). This exclusion is **load-bearing for MC distractor distinctness** in `ratio_to_fraction` (a `1:1` makes the `PART_OVER_OTHER` and `TREATS_ONE_PART_AS_WHOLE` predictions both equal `1`, collapsing two distractors), so it is cross-referenced from §3.1/§10 and is not droppable as "mere pedagogy."

| Task | Rule | Named check (§9.3) |
| --- | --- | --- |
| `share_two_part`, `share_three_part`, `missing_part`, `ratio_to_fraction`, `fraction_to_ratio` | Reject `1:1` / `1:1:1` (and any all-equal tuple) → redraw; the canonical tuple must have at least two **distinct** part values | `ratio-not-all-equal` |
| `write_from_quantities` (T2) | All-equal allowed only if the two/three given quantities are genuinely equal AND the band is 1 (intentional); otherwise redraw | `ratio-all-equal-intentional-or-rejected` |
| `simplify` | All-equal input would simplify to `1:1`; allowed **only** as a band-1 intentional case (§12.2), else redrawn | covered by §12.2 flags |
| `direct_proportion`, `inverse_proportion`, `unit_rate`, `best_buy`, `simple_scale` | These do not emit a ratio *answer* of the all-equal kind; n/a (their answers are number/rational/choice — §12.7) | n/a |

### 12.5 Ambiguous order of labelled categories (rejected → redraw)

ORDER MATTERS for every ratio answer unless a task explicitly declares an unordered comparison (no v1.0.0 task does, except the *internal* equivalence test of T2 which is still order-fixed once the label order is fixed). To make the required order **unambiguous**, the prompt and the canonical model must fix one and only one reading.

| Condition | Rule | Named check (§9.3) |
| --- | --- | --- |
| The quantities/labels in a `write_from_quantities` / sharing / missing-part prompt do not impose a single canonical order | Rejected → redraw: the prompt MUST state the order explicitly ("write the ratio of *flour to sugar*", "share between *Ali, Ben and Cara* in that order"); `contextLabels[]` (§6) fixes the index→label correspondence and the prompt cites it verbatim | `order-unambiguous` |
| Two labels that could read in either direction with no stated order | Unreachable: the constructor always emits an ordered `contextLabels[]` and the prompt template always names them in tuple order | `labels-match-tuple-order` |
| Table-completion correspondence by row position alone | Forbidden: correspondence is by **label** (`location` key), never by row order alone (§7) | `table-correspondence-by-label` |

A reversed-order submission (`3:2` for `2:3`) is therefore never an *ambiguity* — it is a genuine error, returned as `wrong-order` (§5/§10 `MISC.RATIO.REVERSES_ORDER`), never silently accepted.

### 12.6 Non-integer shares, non-divisible totals, and missing-part exactness (rejected → redraw, integer-answer tasks)

For sharing/missing-part tasks whose answers must be whole quantities, the total must divide exactly by the sum of parts; non-exact cases are unreachable, never rounded. **`missing_part` (T7) is integer-only in v1.0.0** (matching its declared `answerTypes:["integer"]` in §2.7/§3.3), so its divisibility constraint is a **hard, non-optional** construction gate with **no escape hatch** — there is no rational-answer path for T7.

| Task | Construction rule | Named check (§9.3) |
| --- | --- | --- |
| `share_two_part`, `share_three_part` | Total `T` sampled as an exact multiple of `sum(parts)`: `T = k · Σparts`, `k ≥ 1` integer, so each share `partᵢ · k` is an **exact integer** by construction; any seed where `Σparts ∤ T` is rejected | `total-divisible-by-sum`, `shares-are-integers`, `shares-sum-to-total` |
| `missing_part` (T7) | **Hard integer constraint (D4):** with the simplest ratio `parts` and the known part on index `k` with value `v`, the constructor MUST enforce `parts[k] ∣ v` (the unit value `u = v / parts[k]` is an exact integer); the missing part `parts[m] · u` is then automatically an exact integer. Any seed where `parts[k] ∤ v` is **rejected → redraw**. No rational-missing-part path exists in v1.0.0 | `missing-part-exact`, `missing-part-consistent-with-ratio`, `missing-part-divides` |
| `direct_proportion` (T8) | The unitary value and the scaled answer are exact integers **or** exact reduced rationals (`answerTypes:["integer","exact-rational"]`, §2.8/§3.3); non-exact (non-terminating) values redraw | `unitary-exact` |

The "share gives a non-whole quantity when whole is required" situation is structurally impossible: the constructor samples `T` from the multiples of `Σparts`, not freely. For `missing_part`, the `parts[k] ∣ v` gate is **mandatory and not waived** — the integer answer type is guaranteed by construction, so a `27/2`-style non-integer missing part is unreachable. There is no floating-point rounding anywhere (`no-float` is a standing structural guarantee, §9).

### 12.7 Unit-rate, direct/inverse, scale exactness (rejected → redraw)

| Task | Exactness rule | Named check (§9.3) |
| --- | --- | --- |
| `unit_rate` (T10) | The rate is an exact integer or exact reduced Rational (`quantity ÷ count`); a seed producing a non-terminating/non-exact value redraws. No approximate decimal answers in v1.0.0 (`answer.type` is the existing exact-rational/integer type, never an approximate decimal) | `unit-rate-exact` |
| `inverse_proportion` (T9) | **SIMPLE INTEGER cases only** (owner brief): the product invariant `x₁·y₁ = x₂·y₂` must yield an **exact integer** `y₂`; the constructor samples so that `(x₁·y₁)` is divisible by `x₂`; any non-exact inverse result redraws — **inverse-proportion non-exact results are unreachable** | `inverse-product-invariant`, `inverse-result-integer-exact` |
| `direct_proportion` (T8) | Unitary method exact (per §12.6) | `unitary-exact` |
| `simple_scale` (T12) | The scale factor is an exact integer or exact reduced Rational and the direction is **unambiguous** (model↔real explicitly stated); a seed whose scale direction or factor is non-exact or ambiguous redraws | `scale-factor-exact`, `scale-direction-unambiguous` |

### 12.8 Tie / equal-value degeneracy for comparison tasks (rejected → redraw)

The best-buy / unit-rate comparison answer is realized as the existing **`multiple-choice`** answer type (the chosen offer is intrinsically a labelled choice; the exact unit-rate witnesses live in `solution`/feedback) — **not** a new `comparison` enum member, so no schema delta beyond `ratio` is required and the platform "at most one new answer type" constraint holds.

| Task | Condition | Rule | Named check (§9.3) |
| --- | --- | --- | --- |
| `unit_rate` comparison context | Two situations with **equal** unit rates (a tie) | Rejected → redraw when a *strict* better-value decision is required: the two unit rates must differ (`rateA ≠ rateB` as reduced Rationals) | `unit-rate-not-tied` |
| `best_buy` (T11) | **Best-buy tie** — two offers giving the identical price-per-unit (or quantity-per-price) | Rejected → redraw: the two options' comparison keys must be **distinct exact rationals** so there is a unique best value; an equal-value seed is unreachable. (NO currency conversion — both offers are in the same unit and currency, owner brief) | `best-buy-unique-winner`, `best-buy-same-unit` |

Comparison answers are decided on the **exact unit rate / comparison key** (reduced Rational equality), never on the raw price — this is the structural ground for the `MISC.RATIO.COMPARES_PRICES_WITHOUT_UNIT_RATE` and `MISC.RATIO.CHOOSES_LOWEST_PRICE_NOT_BEST_VALUE` diagnostics (§10). Because ties are unreachable, "chooses lowest price" is always a *distinguishable* error, never accidentally correct. The decided offer is stored as the `multiple-choice` selection; the wrong-but-plausible offers are the misconception-backed distractors (§3.1/§10).

### 12.9 Scale-factor direction (rejected → redraw)

The owner brief flags "scale-factor unclear direction" as an edge case. `simple_scale` (T12) fixes one direction per item.

- The prompt and `params.scaleDirection ∈ {model-to-real, real-to-model}` declare the single direction; the figure/double-number-line labels the two axes (e.g. "map (cm)" vs "ground (m)") so the multiply-vs-divide direction is determined, never guessable from numbers alone.
- A seed whose factor would read ambiguously (e.g. a `1:1` scale, or a factor whose direction the labels do not disambiguate) is **rejected → redraw** (`scale-direction-unambiguous`).
- "additive-difference instead of multiplicative scale" and "scale-factor wrong direction" are therefore genuine, distinguishable errors handled as diagnostics (`MISC.RATIO.ADDITIVE_DIFFERENCE_INSTEAD_OF_MULTIPLICATIVE_SCALE`, `MISC.RATIO.SCALE_FACTOR_WRONG_DIRECTION`, §10), never construction ambiguities.

### 12.10 Deferred topics — deterministically excluded

Each deferred topic is **structurally absent from the generator's task enum (`RATIO_TASKS`, §1.3) and from the Ratio/quantity model**, so the seeded loop *cannot* construct it. A named **exclusion test** asserts unreachability for each; `paramsInDomain` rejects every excluded task id, the SDK registry exposes no task entry, and an integration test asserts those ids `generate`-throw and never appear in the 10,000-seed sweep.

| Deferred topic (owner brief) | How it is made unreachable | Exclusion test |
| --- | --- | --- |
| Percentages as a full family | No percent task in the enum; no `%` quantity primitive | `excl-no-percent` |
| Compound / continued proportion proofs | No multi-stage proportion-chain task; the model holds at most one proportion relation per item | `excl-no-continued-proportion` |
| Currency conversion / exchange rates | `best_buy`/`unit_rate` use **one** currency+unit per item; no conversion-rate parameter exists | `excl-no-currency-conversion` |
| Recipe scaling with units; compound units beyond simple unit rate | The unit-rate model permits only a single `quantity ÷ count`; no compound dimension representable | `excl-no-compound-units` |
| Similar-triangles geometry scale factors | No geometric-similarity primitive; `simple_scale` is a numeric/double-number-line scale only (NO similarity proof) | `excl-no-similarity` |
| Gradient-as-ratio | No coordinate-line/gradient primitive (coordinate-lines owns gradient) | `excl-no-gradient` |
| Gear / lever ratios | No mechanism context primitive | `excl-no-mechanism-ratio` |
| Irrational ratios; decimal-ratio terms that don't convert exactly | Ratio terms are integers only; exact-math rejects irrationals; a decimal context that would not convert to an exact integer ratio redraws | `excl-no-irrational-ratio`, `excl-no-inexact-decimal-term` |
| Trigonometric ratios | No trig primitive; exact-math has no trig | `excl-no-trig-ratio` |
| Probability odds | No probability/event primitive; "odds" never appear as a ratio context | `excl-no-odds` |
| Algebraic ratio proofs | No symbolic/variable ratio; parts are concrete positive integers | `excl-no-algebraic-ratio` |

The exact-integer/exact-rational arithmetic rule independently bars surds, decimals-that-don't-convert, and trig (no irrational can be produced), so irrational/trig/inexact-decimal ratios are **doubly excluded** — a structural consequence of the model, not a post-hoc filter.

### 12.11 Visual degeneracy (bar-model / double-number-line)

The renderer (§8) prefers mathematically proportionate figures (bar segment lengths in proportion to `parts`; double-number-line ticks at exact proportional positions). When a drawn seed would produce a visually poor figure — an extreme part imbalance the bar cannot legibly show, a tick density that forces label collision the §8 placement contract cannot resolve, or a three-part bar whose smallest segment falls below the minimum legible width — the seed **deterministically regenerates** within the same parity-preserving loop rather than emitting a degraded figure. The thresholds (max part-ratio for a legible bar; minimum segment width; max double-number-line tick count) are versioned construction parameters; the regeneration is part of the deterministic call order, so Python↔TS SVG parity is preserved (`figure-legible`, `no-label-collision` — §13/§8).

---

## 13. Accessibility model

### 13.1 Contract and fields

Every `gen.proportion.ratio` item populates the item-level `accessibility{ spokenMath, altText, longDescription, nonColorIndicators }` object (`question-item.schema.json#/$defs` item `accessibility`, which is `additionalProperties:false` with **exactly those four fields**). **The data-table fallback is NOT an item-level accessibility field** — the schema forbids it there (`additionalProperties:false`). It lives only on the figure asset: each `media[]` entry carries `media[].altText`, `media[].longDescription`, and **`media[].dataTableFallback` (type `object`, per `mediaAsset`)** — the information-equivalent of the bar model / double-number-line / proportional table. Every section that references the fallback keys it as `media[].dataTableFallback` (here, §14), never `accessibility.dataTableFallback`. This is the shipped coordinate-lines / data-handling / mensuration discipline, reused verbatim.

The figure root follows the **shipped canonical-SVG discipline verbatim**: the root `<svg>` carries `class="cx-figure"` (the **shared** isolation root class read by the document-level `COMMON_CSS`; NOT a `ratio-figure` root — a non-`cx-figure` root would leave every `.cx-figure .cx-…` rule inert and render the bars unstyled), `role="img"` and `aria-label="<alt>"` (NOT `aria-labelledby`; no `id="fig-title"/"fig-desc"` attributes are introduced — adding them would diverge byte-for-byte from every approved family), with `<title>{esc(title)}</title>` and `<desc>{esc(desc)}</desc>` as the first children. The canonical monochrome `media[0].svg` carries its own hardcoded monochrome `<style>` and **no** root class; `presentationSvg()` strips that `<style>` and stamps `class="cx-figure" style="--cx-…"`. The theme **id** is `spi-math-ratio-theme/1` — a different namespace from the root class; the two are never conflated. **All interior primitives** — bar segments, segment dividers, segment labels, double-number-line axes, ticks, tick labels, bracket/total markers, and the unknown-marker glyph — are **presentation-only under the single labelled `role="img"` root** (they carry no individual `role`/`aria`), so axe-core sees one labelled image rather than many unlabelled graphics nodes. `nonColorIndicators` is `true` for every item. Targets: **WCAG AA**, **axe-core 0 critical / 0 serious**, gated in CI exactly as for the approved families.

### 13.2 Data-table fallback — given quantities only, role-keyed slots (the answer-free student channel)

`media[].dataTableFallback` lists **each given quantity** the figure encodes, so a non-visual user has the same input data as a sighted user. Slots are **typed by role** (given vs asked) so the no-leakage check keys on slot role, not on numeric coincidence. The fallback shape adapts the data-handling deterministic-HTML-table discipline (and reuses its `dataTableFallback` mechanism) to the bar-model / double-number-line / proportional-table figure:

```
dataTableFallback = {
  model: "bar-model" | "double-number-line" | "proportional-table",
  ratio:        { role: "given", parts: [ … ], labels: [ … ] } | null,   // the GIVEN ratio, in order, by label
  givenParts:   [ { label, role: "given",  value: int } , … ],            // parts/quantities shown in the figure
  givenTotal:   { role: "given-stated", value: int } | null,              // present only when the total is given
  unknownSlots: [ { label, role: "asked" } , … ],                         // NAMES the unknown(s); never carries a value
  axes:         [ { name, role: "given", unit, ticks: [ int, … ] } , … ] | null,  // double-number-line axes (given ticks only)
  asked:        { role: "asked", quantity: "ratio" | "share" | "missing-part"
                                 | "fraction-of-whole" | "unit-rate" | "best-value" | "scaled-value" }
}
```

- For **share / missing-part tasks** (`share_two_part`, `share_three_part`, `missing_part`): the fallback lists the **given ratio** (in label order), the **given total** when stated, and the **given known part** for `missing_part` — and **never** the computed shares or the missing part. The unknown slot(s) name the asked label(s) with **no value** (`unknownSlots`).
- For **table-completion sharing** (§7): the fallback is the proportional table itself with **only the given cells filled** (by `location` label) and the to-be-completed cells named-but-empty (role `asked`), correspondence by **label**, never row order alone.
- For **proportion / unit-rate / scale tasks** (`direct_proportion`, `inverse_proportion`, `unit_rate`, `best_buy`, `simple_scale`): the double-number-line / table fallback lists the **given pairs / given offers / given scale axis** and names the asked quantity; the unit rate, scaled value, or best-value verdict is **never** present. (`inverse_proportion` ships no proportional figure — §8 — so its fallback is a plain given-pairs table, never a bar/number-line.)

Values are exact integers (or exact `{num,den}` where a rational unit rate is intended) so the table is byte-stable and parity-checked. A named check **`fallback-no-answer-leak`** is **role/intent based** (consistent with the canonical-SVG answer-leakage rule and §14 "raw-data-equality-is-not-leakage"): it asserts that **no slot whose ROLE is the answer** (an `asked`-keyed value, or any `result`/`answer`/solution-annotation entry) is present in `dataTableFallback`, `altText`, `longDescription`, or `spokenMath` of the **student** figure. A given quantity that *numerically coincides* with the hidden answer (e.g. a given part that happens to equal a share) **passes**, because the check keys on slot role, not value-equality. A dedicated answer/solution annotation in the student figure would fail it. This is the **answer-free student channel** the brief requires: the student bar model **shows GIVEN quantities only and NEVER reveals missing values**, and so does its a11y payload.

### 13.3 spokenMath — model + given quantities, structurally, never the answer

`spokenMath` describes the **model and its given quantities** in words, derived from the canonical Ratio model (§6), not from a stored string:

- Ratio is spoken as ordered labelled parts: "the ratio of flour to sugar is two to three"; three-part: "Ali, Ben and Cara share in the ratio two to three to five".
- Bar model: "A bar split into parts in the ratio two to three; the whole bar represents the total amount." (Given total stated only when given.)
- Double number line: "A double number line. The top line shows distance on the map in centimetres; the bottom line shows the real distance in metres; the marked points are …" (given ticks only).
- Unit rate / best buy: "Offer A: five apples for two pounds. Offer B: eight apples for three pounds. Which is better value per apple?" — the **question**, never the verdict.

The **student** `spokenMath` and `media[].dataTableFallback` **never state the computed ratio answer, the shares, the missing part, the unit rate, the best-value verdict, or the scaled value**; they convey **only given data and what is asked** — asserted by `fallback-no-answer-leak` and a dedicated `spokenmath-given-only` check. The **answer-key / solution** `spokenMath` variants (used only in the answer-key and solutions exports, never in the student item) may speak the result.

**Encoding stability.** The canonical stored ratio `display` uses the ASCII colon form `a:b` / `a:b:c` (e.g. `"2:3:5"`), never a Unicode ratio glyph (U+2236 RATIO `∶`), and `spokenMath` spells "to" in words. A named check **`display-ascii-colon`** asserts the **stored** `answer.display`, the `dataTableFallback`, and figure segment labels contain no Unicode colon-like glyph, so golden/parity fixtures are byte-stable across locales and encodings. (The §5 parser does **not** accept a Unicode colon-like symbol on input in v1.0.0 — decision G — and rejects it with `malformed-response`; the canonical stored byte is always ASCII `:`.)

### 13.4 Bar-model / number-line accessibility specifics

The non-Cartesian figure system (§8) carries its meaning through **structure and text**, not colour or position alone:

- **Every part is textually labelled** with its `contextLabel` and (for given parts) its value; the unknown part carries a distinct **unknown marker** (a `?` glyph plus a dashed/hatched segment outline — see §13.5), so a screen-reader user learns *which* slot is unknown from the fallback's `asked` role, and a sighted user from the shape/dash cue, never from colour.
- **Totals and brackets** are textually labelled ("total = 30" only when the total is given) and carried in the fallback's `givenTotal` slot.
- **Double-number-line** correspondence is conveyed by **aligned labelled ticks** and the `axes[].ticks` fallback array (given ticks only), so the proportional correspondence is recoverable without seeing the line. Top-lane and bottom-lane ticks share a **single computed integer x-position array** (§8) so aligned ticks are byte-identical Py↔TS.
- **Proportional tables** rendered as deterministic semantic HTML (the data-handling `dataTableFallback` table mechanism, reused) keep **label↔cell correspondence** explicit (`<th>` row/column headers), so completion is by label, never by row position.
- **Not-to-scale guard.** Where a missing value must not be recoverable by measuring the SVG (e.g. `missing_part`, `simple_scale`), the student figure is rendered **normalized NOT-TO-SCALE** with a visible "NOT TO SCALE" banner and is asserted not to encode the hidden value in segment length (`figure-not-to-scale-for-hidden`, cross-referenced from §8/§12). Direct read-off tasks may be to-scale.

### 13.5 No colour-only information, across all modes

Meaning is never carried by colour alone. The family renders through the approved theme stack: the shared per-root isolation + four-mode mechanism (`presentationSvg()`/`exportSvg()`) plus a **`ratio-theme`** (theme id `spi-math-ratio-theme/1`) that **`extends "spi-math-cartesian-theme/1"`** and **FOLLOWS the `data-chart-theme` ADDITIVE PATTERN** (the same versioned-extension mechanism) — it does **not** depend on or compose `data-chart-theme` itself. The extension adds the bar-model / double-number-line / table primitives supporting the four modes inherited from cartesian-theme: **premium**, **premium-dark**, **accessible** (CVD-safe), and **print** (monochrome authoritative).

**New variables are namespaced `--cx-ratio-*` to guarantee zero cross-family name collision.** Every new custom property the extension introduces uses the `--cx-ratio-` sub-prefix (`--cx-ratio-bar-fill`, `--cx-ratio-bar-edge`, `--cx-ratio-divider`, `--cx-ratio-lbl`, `--cx-ratio-bracket`, `--cx-ratio-axis`, `--cx-ratio-tick`, `--cx-ratio-tick-lbl`, `--cx-ratio-unknown-mark`, `--cx-ratio-ans`), so it **collides with none** of the cartesian / data-chart / mensuration / transformations variable names — in particular it does **not** reuse `--cx-ans` (a mensuration variable) or `--cx-lbl`. Label fill that should inherit the base text colour binds `fill:var(--cx-text)` (the cartesian base) directly; only genuinely new primitives introduce `--cx-ratio-*` variables. The collision test `theme-variable-namespacing` asserts every newly declared variable matches `^--cx-ratio-` and that no `--cx-ratio-*` name equals any variable of cartesian/data-chart/mensuration/transformations.

**Per-segment distinctions survive theming and are never colour-only, and are driven by CSS classes — never inline `var()`.** The known-vs-unknown distinction is the one place a non-positional cue is actually needed (parts within a single bar are already unambiguous by position, label, and divider line, so per-part decorative fills are **not** used — keeping the bar mathematically clear, not over-decorated). The **unknown** segment is distinguished by a **dashed/hatched outline + a `?` glyph + the `asked`-role label**, with monochrome **print** authoritative. Critically, the hatch `<pattern>` and every meaning-bearing stroke/fill are styled **by CSS class** in the additive `commonCss` (e.g. `.cx-figure .cx-bar-unknown-hatch { stroke: var(--cx-ratio-bar-edge); }`), **never** by an inline `var()` presentation attribute on a `<path>`/`<line>` — because `exportSvg()`'s `resolveCommonCss` rewrites `var(--cx-…)` **only inside the baked `<style>` block**, so an inline `var()` would render colourless in the self-contained 6000×4200 export and break both the known/unknown distinction and self-containment. A named check **`no-inline-var-in-attrs`** asserts no `var(` substring appears in any presentation attribute of any emitted figure (only inside `<style>`). The canonical/print render asserts every meaning-bearing colour ∈ the approved `GREYS` set (`{#111,#333,#444,#555,#888,#bbb,#fff}`, the shared greylist) via the reused no-colour-only-information check; named checks `segment-distinction-not-colour-only` and `unknown-marker-not-colour-only` gate this.

**Theme-variable completeness.** Every new `--cx-ratio-*` variable the extension introduces is given an **explicit value in all four modes** (and a greyscale value in print). Stroke-only primitives (segment dividers, ticks, brackets, the unknown-marker outline) have no base fallback and would render black only by luck, defeating the per-mode CVD-safe and premium-dark guarantees; **premium-dark uses light strokes/fills** so the bar and ticks are visible on the dark `--cx-bg`. A `ratio-theme.test.ts` theme-completeness check (mirroring `data-chart-theme.test.ts`) asserts **each declared `--cx-ratio-*` variable has a value in every mode**. A named check **`no-color-only`** asserts that removing colour (print mode) loses no part-distinction, total, tick, or unknown-marker information; this holds in all render contexts in the review pack.

### 13.6 Gates

- `nonColorIndicators === true` on every item (schema-validated).
- **axe-core** over rendered student items: **0 critical, 0 serious**, WCAG AA — blocking. All interior primitives are presentation-only under the single `role="img"`/`aria-label` `cx-figure` root (§13.1), so axe evaluates a single labelled image.
- `media[].dataTableFallback` present and non-empty for every figure; `fallback-no-answer-leak`, `spokenmath-given-only`, `display-ascii-colon`, `no-color-only`, `no-inline-var-in-attrs`, `theme-variable-namespacing`, `segment-distinction-not-colour-only`, and `unknown-marker-not-colour-only` are **blocking** review-pack/validator checks.
- The `ratio-theme.test.ts` theme-completeness check (every `--cx-ratio-*` variable valued in all four modes, greyscale in print) is blocking.
- Printable **monochrome** and **two-column print** variants are produced and audited in the review pack (§14), alongside the **6000×4200 (S=6) materialised export** and the explicit **answer-absent-from-student-figure** tests (§14).

---

## 14. Review-pack and visual-audit plan

The ratio review pack is **not a new artifact type** — it is a direct reuse of the **data-handling v1.0.2 / mensuration v1.0.1 reachability-derived COVERAGE-MATRIX machinery** (`oracle/make_review_pack_data_handling.py` / `…_mensuration.py`, the model approved under `DECISION_LOG` #48/#49). A new builder `oracle/make_review_pack_proportion_ratio.py` instantiates the same three-stage pipeline — *reachability → required cells → greedy set-cover over task-pinned candidates* — against the ratio distribution report and the `gen.proportion.ratio` generator. Nothing in the coverage model is reinvented; only the family token vocabulary changes. All task slugs are the **single canonical `RATIO_TASKS` set of §1.3** (`simplify`, `write_from_quantities`, `ratio_to_fraction`, `fraction_to_ratio`, `share_two_part`, `share_three_part`, `missing_part`, `direct_proportion`, `inverse_proportion`, `unit_rate`, `best_buy`, `simple_scale`), used verbatim as the `cell:<task>:…` token prefix, identical to the keys of `OBJECTIVE_BY_TASK`, `RULES_BY_TASK` (§10), the generator dispatch, and the §15 scope list — with **no** `write_ratio` / `simplify_ratio` / `*_unitary` spelling anywhere.

### 14.1 Required cells are DERIVED from the distribution report, never hand-set

The authoritative reachability artifact is `docs/review/proportion_ratio_distribution.json` (the 10,000-seed sweep of §11/§9). The builder's `_reachability()` reads, per task, `{interactions, bands, answerShapes}` straight from that report; `_required_tokens()` emits one **required cell** for every **task** (`cell:<task>:inter:<i>`), every **reachable band** (`cell:<task>:band:<1..5>`), and every **realised answer shape** (`cell:<task>:shape:<token>`). The required-cell count `requiredCells = Σ(len(interactions)+len(bands)+len(shapes))` over the reachability map is asserted equal to the matrix-derived count (`required-token-count-derived-from-matrix`) — never a literal.

The **answer-shape token** is the structured answer representation, mapped from the §6.2 model-tag through the **single declared model-tag ↔ schema-`answer.type` ↔ coverage-token table** (§11/§9.2), so the owner's "all answer types; two/three-part; simplified/unsimplified" become first-class FAIL-able cells. The five answer shapes are exactly the live schema `answer.type` values the family emits — `ratio`, `integer`, `exact-rational` (fraction), `table-completion`, and `multiple-choice` (the best-buy / unit-rate comparison choice). **There is no `comparison` answer.type** (it is not a live enum member and is not added — §15.1); the comparison answer is the existing `multiple-choice` type, and the coverage token for it is `multiple-choice`:

```
shape = "<answerType>[:<detail>]"
  answerType ∈ {ratio, integer, exact-rational, table-completion, multiple-choice}   # the LIVE schema answer.type values
  detail for ratio          ∈ {two-part, three-part} × {require-simplest, accept-equivalent}   # §12.3 policy + arity
  detail for integer/exact-rational ∈ {integer, rational}                  # canonical denominator
  detail for table-completion∈ {two-part, three-part}
  detail for multiple-choice ∈ {best-buy, unit-rate-compare}               # the comparison choice context
```

So `cell:share_three_part:shape:table-completion:three-part` and `cell:simplify:shape:ratio:two-part:require-simplest` are distinct required cells. The distribution records exactly which `(task, shape, detail)` cells exist; a never-realised combination is **non-existent — documented in the matrix with `note:"unreachable per distribution report (no items)"`, not a `MISSING`**.

### 14.2 Interaction cells and the unsupported-MC discipline

Interaction follows the **decision-C matrix exactly**. The six **MC-eligible** tasks are `simplify`, `ratio_to_fraction`, `fraction_to_ratio`, `direct_proportion`, `inverse_proportion`, and `best_buy`. `best_buy` is **MC-only** (the labelled choice IS the construct — no free-response cell); the other five are **FR + MC**; the remaining six (`write_from_quantities`, `share_two_part`, `share_three_part`, `missing_part`, `unit_rate`, `simple_scale`) are **FR-only**. MC-eligible `ratio_to_fraction` draws are additionally constrained (`Σparts ≥ 4` and distinct part values) so the three distractors stay distinct (avoiding the `1/3` vs `PART_OVER_OTHER=1/2` vs `WRONG_TOTAL=1/2` collision for tiny ratios); the distribution records this reduced MC reachability so the matrix does not over-claim band-1 MC cells. The builder requires `cell:<task>:inter:free-response` for every task **except `best_buy`** (which has no FR cell), and `cell:<task>:inter:multiple-choice` for each of the six MC-eligible tasks; **no** `multiple-choice` cell exists for any of the six FR-only tasks. The pack proves, per task, that the **free-response diagnostics and feedback** of §10 are realised through the same adapter the validator recomputes, and that an **explicit MC request on a non-MC-eligible task** is **never silently converted** — it either deterministically redraws to an MC-eligible case or returns a clear `interaction-not-supported` error (asserted by `unsupported-mc-request-rejected-or-redrawn` per task).

### 14.3 Greedy set-cover, task-pinned gathering, builder FAILS on any missing reachable cell

Stage 1 gathers candidates task-pinned across a bounded seed window (`GATHER_SEEDS` per task), so rare reachable cells (a band-1 `inverse_proportion`, a rational `unit_rate`, an MC `best_buy`) always have candidates. Stage 2 is the same greedy set-cover: repeatedly pick the candidate adding the most still-uncovered **required** tokens, reusing one exemplar across several cells where it is a genuine exemplar. The builder's exit code is `0` **only** when `required_cells ⊆ covered` **and** every selected item is machine-valid **and** `len(required_cells) == derived_required_cells`; any missing reachable cell prints `MISSING COVERAGE` and returns non-zero.

### 14.4 Explicit coverage matrix + the five blocking coverage tests (reused by name)

The pack emits the same two coverage structures as data-handling/mensuration: a per-task **`coverageMatrix`** (`interactions` / `bands` / `shapes`, each `{reachable, hasExemplar, exemplarSeed, note}`) and a flat **`coverageCells`** list of every realised `(task, interaction, band, answerShape, seed)`. The Markdown renders the matrix as the `| Task | Interactions | Bands | Answer shapes |` table with `→seed` / `→MISSING` / `=n/a` cells. The **five blocking coverage tests are the data-handling/mensuration set, reused verbatim**, retargeted:

| Coverage test | Asserts |
| --- | --- |
| `every-reachable-task-band-covered` | every `cell:<task>:band:<b>` the distribution marks reachable has an exemplar seed |
| `every-supported-interaction-covered` | free-response is covered for every task **except `best_buy`** (which is MC-only, decision C); multiple-choice is covered for every MC-eligible task (`simplify`, `ratio_to_fraction`, `fraction_to_ratio`, `direct_proportion`, `inverse_proportion`, `best_buy`); **no** MC cell exists for any of the six FR-only tasks and **no** FR cell exists for `best_buy`; the unsupported-MC-request rejection/redraw test passes per task |
| `every-task-answer-shape-covered` | every realised answer-shape token (all five live answer types: `ratio`/`integer`/`exact-rational`/`table-completion`/`multiple-choice`, with two/three-part and simplified/unsimplified details) has an exemplar |
| `coverage-summary-matches-records` | `summary.coveredCells`/`coverageCells` agree with `records[]` (no double-count, no phantom cell) |
| `no-false-full-coverage-claim` | `summary.allCovered == (missingCoverage == [])` — the honest flag can never be `true` while a required cell is missing |

`summary.allCovered`/`summary.allValid` are the top-level honesty flags; `requiredCells == derivedRequiredCells` (the reachability-derived count, never a literal) is asserted in the exit gate and surfaced in the summary; the §15 manifest hash-attests the pack so a silent regeneration that drops a cell fails CI.

### 14.5 Owner-mandated coverage dimensions (additional tokens beyond the cells)

On top of the systematic cells, `_required_tokens()` adds the owner's full review-pack checklist as additional FAIL-on-missing tokens, each surfaced by `_features()`:

| Owner dimension (brief) | Required token(s) |
| --- | --- |
| all twelve tasks | `cell:<task>` for each of `simplify … simple_scale` |
| every reachable band | `cell:<task>:band:<b>` (per §14.1) |
| all answer types | `atype:ratio`, `atype:integer`, `atype:exact-rational`, `atype:table-completion`, `atype:multiple-choice` |
| two-part AND three-part | `arity:two-part`, `arity:three-part` |
| simplified AND unsimplified input | `input:already-simplest`, `input:has-common-factor` |
| equivalent-ratio answers | `equiv:accepted` (under `accept-equivalent`), `equiv:rejected-partial` (under `require-simplest`) |
| reversed-ratio traps | `trap:reversed-order` (a diagnostic exemplar where `wrong-order` is the predicted result code for the reversed-ratio submission) |
| part-whole conversion | `convert:ratio-to-fraction`, `convert:fraction-to-ratio` |
| total-parts sharing | `share:total-parts` (two- and three-part) |
| missing part | `share:missing-part` |
| direct / inverse proportion | `proportion:direct`, `proportion:inverse` |
| unit rate | `rate:unit` (integer and rational) |
| best-buy | `compare:best-buy` |
| simple scale | `scale:simple` (both directions: `scale:model-to-real`, `scale:real-to-model`) |
| bar-model student figures | `figure:bar-model` |
| answer-key overlays | `render:student-figure`, `render:answer-key` |
| double-number-line examples | `figure:double-number-line` |
| table-completion examples | `figure:proportional-table` |
| premium / premium-dark / accessible / print | `render:premium`, `render:premium-dark`, `render:accessible`, `render:print` |
| multi-item worksheet | `render:worksheet-multi-item` (two-column layout) |
| 6000×4200 export | `export:6000x4200` (materialised raster hash) |
| answer ABSENT from student figure | `answer-free:student-figure` |
| every misconception / diagnostic | `diag:<rule>` for each `MISC.RATIO.*` rule of §10 |

The endpoint honesty analogues are §12's degeneracy gates (no zero/negative part; integer-share exactness; missing-part divisibility; unit-rate/best-buy non-ties; inverse exactness; unambiguous scale), each recorded as a covered token so the pack proves the gate is **exercised**, not merely declared (`det:integer-share`, `det:missing-part-divides`, `det:exact-inverse`, `det:unique-best-value`, `det:unambiguous-scale`).

### 14.6 Student figure BESIDE answer-key overlay, and the answer-absence tests

The pack and the visual audit render, for every figure-bearing item, the **student figure beside its answer-key overlay** — the two products of the §8 single-model figure over **BYTE-IDENTICAL base geometry** (the approved base-geometry + additive-overlay channel pattern, `cx-base`/`cx-annot`/`cx-overlay`, reused by name): the student `media[0].svg` (given quantities only, no missing value, no result) and the answer-key copy (the same bar/line/table plus the computed shares, the filled missing part, the unit-rate working, the scaled value, or the best-value verdict). `answer-key-base-geometry-identical` enforces the base geometry is the same in both copies; `answer-key-overlay-additive-only` enforces the overlay never alters student geometry, only adds answer-role elements. (These are the single normalized check names; §8/§9/§13 use the same spellings — no `…-diagram-identical` variant.)

Two explicit, **blocking** answer-absence tests are recorded per figure item (reusing the semantic role/intent leakage model — raw given data equal to the answer is **not** leakage; a dedicated answer/solution annotation **is** — and they key on element **role/class**, NOT on numeric value-set equality):

- `no-result-in-student-figure` — the student SVG carries **no element whose render role/class is a result** (no `.cx-ratio-ans` element, no value glyph on the `.cx-bar-unknown` hatch segment, no filled answer cell): no computed share, missing part, unit rate, best-value verdict, scaled value, or simplified/derived ratio. A **given** part that coincidentally equals a share **passes** (`raw-data-equality-is-not-leakage`); a dedicated answer-role annotation **fails**. The check is role/class-keyed, never a numeric multiset comparison against given values.
- `student-a11y-does-not-state-result` — the student `media[0].longDescription` and `media[0].dataTableFallback` give the model, the given ratio/quantities, and what is asked (per §13, the fallback lives on `media[]`, never on the item-level `accessibility` object), but **never** the answer; the check is role-based (no `asked`-role *value* in the student copy; a stated given that numerically coincides passes). The result text lives only in the answer-key/solution copy.

A pinned positive/negative pair is recorded: a sharing item whose given total numerically equals one of the (different-role) shares **passes**; a student figure carrying a share value on the unknown segment **fails**.

**Diagnostic predictions never enter any figure or a11y field.** The §10 `MISC.RATIO.*` predicted wrong responses (which are answer-shaped — a reversed tuple, a part-over-other-part fraction, a divide-by-one-part share) feed **only** the free-response/MC checker, the worked-solution pitfall notes, and the §9 validator's diagnostic-recompute. **No** diagnostic-predicted value may appear in any `cx-base`/`cx-annot`/`cx-overlay` group of the student or answer-key SVG, nor in any `media[]` a11y field; the answer-key overlay shows **only the CORRECT** shares / fractions / rate / verdict. Asserted by `diagnostic-predictions-not-in-figure`.

### 14.7 Visual audit + browser verification

`docs/review/proportion_ratio_visual_audit.html` reuses the data-handling/mensuration audit harness: it renders every pack figure through the **`ratio-theme` extension** of §8/§13/§16 (theme id `spi-math-ratio-theme/1`) — a versioned extension that **`extends "spi-math-cartesian-theme/1"` and FOLLOWS the `data-chart-theme` additive PATTERN** (same per-root `class="cx-figure"` isolation, same `presentationSvg()`/`exportSvg()` contract, new `--cx-ratio-*` variables + one additive ruleset) **but does not depend on `data-chart-theme`** — in all four modes: **premium**, **premium-dark**, **accessible** (CVD-safe), **print** (monochrome authoritative), via `presentationSvg()`, plus the self-contained **6000×4200** copies via `exportSvg()`. The audit includes the owner's stress galleries:

- **label-collision** cards (dense three-part bars with adjacent labels at minimum clearance; long context labels; dense double-number-line ticks);
- the **two-column print** worksheet layout (`render:worksheet-multi-item`);
- **bar-model student figures**, **double-number-line examples**, **table-completion (proportional-table)** examples;
- monochrome legibility of the unknown-marker hatch+dash vs solid known segments vs dividers under greyscale;
- **student-beside-answer-key** pairs for every figure task.

A `proportion_ratio_browser_verification.json` records the live-Chromium re-confirmation (four modes coexist on one page with **distinct computed styles** via real `getComputedStyle`, the unknown-marker hatch/divider contrast holds in each mode, **no inline `var()` survives into any presentation attribute** so the export raster is self-contained, the 6000×4200 raster hash matches), exactly as the data-handling/mensuration browser verification does. The audit and verification JSON are hash-attested in the manifest (§15), with artifact-identity metadata (`data-generator-id`/`version`, `data-validator-version`, `data-git-commit`) all agreeing on one build commit.

### 14.8 RATIO-CHECKER review matrix

Beyond the coverage cells, the pack emits a dedicated **ratio-checker matrix** (the analogue of the mensuration quantity-checker matrix) that proves the §5 parser / canonicalizer / equivalence checker for the new `ratio` answer type accepts and rejects **exactly** as the contract requires. For representative ground truths in each arity and under each `answerPolicy`, the matrix records a required outcome (a member of the single lower-kebab `RESULT_CODES` vocabulary of §5, decision F) for each submission, and the builder **FAILS if any required row is absent** (so every `RESULT_CODES` member has verified evidence):

| Ground truth (policy) | Submission | Required outcome (`RESULT_CODES`, §5) |
| --- | --- | --- |
| `2:3` (`accept-equivalent`) | `4:6` | `correct` (equivalent accepted; `2*6 == 3*4`) |
| `2:3` (`accept-equivalent`) | `20:30` | `correct` (equivalent accepted) |
| `2:3` (any policy) | `3:2` | `wrong-order` — **rejected**, never accepted (order matters) |
| `2:3:5` (`accept-equivalent`) | `4:6:10` | `correct` (multi-part equivalence `[ka,kb,kc]`) |
| `2:3:5` (any policy) | `2:5:3` | `wrong-order` — **rejected** (ordered three-part) |
| `2:3` (any policy) | `5:7` (legal, not equivalent, not a reordering) | `wrong-ratio` |
| `2:3` (any policy) | `2:3:5` (wrong arity) | `wrong-number-of-parts` |
| `2:3` (`require-simplest`) | `2:3` | `correct` |
| `2:3` (`require-simplest`) | `4:6` (equivalent but unsimplified) | `equivalent-not-simplified` carrying `partial: true` — NOT full `correct` (per §12.3) |
| `2:3` (`accept-equivalent`) | `4:6` (equivalent unsimplified) | `correct` (per §12.3) |
| any | ratio with a **zero** part `0:3` | **rejected** (`zero-or-negative-part`) |
| any | ratio with a **negative** part `-2:3` | **rejected** (`zero-or-negative-part`) |
| any | the word-form alias `2 to 3` (NOT supported in v1.0.0 — decision G) | **rejected** (`unsupported-term`) |
| any | malformed ratio text (`2:`, `:3`, `2::3`, `abc`) | **rejected** (`malformed-response`) |
| any | extra trailing text (`2:3 apples`) | **rejected** (`unparsed-trailing-text`) |
| any | spaces around the colon (`2 : 3`) | **accepted** (normalized) → `correct`/`equivalent-not-simplified` per policy |
| any | Unicode colon-like symbol (`2∶3`, U+2236) — NOT supported in v1.0.0 (decision G) | **rejected** (`malformed-response`) |

These rows reuse the **same** canonicalizer + equivalence checker the §9 validator runs (a behavioural proof, not a re-implementation), so the "2:3 accepts 4:6 / rejects 3:2; 2:3:5 accepts 4:6:10; unsimplified equivalent accepted-or-partial per task policy; zero/negative/malformed/extra-text/word-form/Unicode-colon rejected; spaces accepted" guarantees of the brief are gated by construction.

### 14.9 Per-item record contents

Each `records[]` entry (and its Markdown section) shows the full audit trail:

- **objective** (`objectiveId`), **task**, **interaction** (`interactionType`), **answer shape** (one of `ratio`/`integer`/`exact-rational`/`table-completion`/`multiple-choice`, with arity and policy detail), **seed**, **params**;
- the **canonical Ratio model** (§6 — ordered parts; simplified canonical parts; original unsimplified parts where relevant; total parts; scale factor where relevant; known + missing part where relevant; context labels; `answerPolicy`; answer-shape tag) echoed verbatim as the single source the figure, prompt, answer, solution, diagnostics, a11y, and validation derive from;
- the **prompt** (`prompt.instruction` + typed `prompt.blocks` citing the figure via a `media-ref` block);
- the **student figure** (bar model / double number line / proportional table) **beside the answer-key overlay**;
- the **canonical answer** — `answer.canonical` (for a ratio: `{parts:[…]}`, the structured value; for integer/exact-rational: the bare integer / Rational `{num,den}`; for table-completion: the label→value cell map; for the best-buy comparison: the `multiple-choice` selection with the exact unit-rate witnesses in `solution`) and the **derived** `answer.display` (`"2:3:5"`, etc.; never duplicated, never the canonical);
- the **worked solution** (`solution.steps[{number,transformation,intermediateResult}]` — e.g. total-parts then unit value then each share; or unitary value then scaled value; or each comparison key then verdict);
- the **misconception calculations** — every eligible `MISC.RATIO.*` adapter value with its `observableError`/`feedback`/`expectedResultCode` (displayed-value language only, never injected into any figure/a11y field); FR diagnostics for every task, MC distractors only where MC-eligible;
- the **accessibility** representation (`accessibility.spokenMath` + `media[].dataTableFallback`);
- the **difficulty axes + band** (`difficulty.axes` over the closed enum of §11, `difficulty.overallBand`);
- the **validation checks** run — the canonical `validate()` `checks[].name` vocabulary of §9.3, referenced by the exact emitted strings (no per-section renaming);
- the **reproduction command** (`python -c "import sys;sys.path.insert(0,'oracle/spi_oracle');import proportion_ratio as r;print(r.serialize(r.generate(<seed>, <cfg>)))"`).

---

## 15. Schema, versioning, and lifecycle plan

`gen.proportion.ratio` follows the **identical lifecycle** the platform ran for coordinate-lines (`DECISION_LOG` #44), data-handling/stats (#49), mensuration (#53), and transformations: oracle-first build, blocking gates, **register `pending-review` (gated)**, owner review of the pack, then approval with immutable fixtures. This section summarizes the schema delta, the versioning, and the lifecycle; the full `ratio` schema body, parser, and checker are §4/§5.

### 15.1 Schema delta summary — the additive, owner-gated, CANONICAL-FIRST `ratio` answer type (the ONLY new enum member)

This is the **only** schema change the family needs and it follows the approved `quantity` + `transformation` mechanism **exactly**: additive-only, backward-compatible, owner-gated, expressed with **`if/then/const` rules under `answer.allOf` (NOT `oneOf`/`anyOf`)** so the runtime bundled Ajv validator AND the Python conformance checker (`oracle/check_conformance.py`) apply **identical** rules. The delta uses **only the keyword subset both validators share** — `if`/`then`/`const`/`required`/`additionalProperties`/`type`/`pattern`/`enum`/`minimum`/`minItems`/`maxItems`/`items` — and ships **no `oneOf` and no `anyOf` anywhere** (including not nested inside a `not`): the conformance checker has no `anyOf`/`oneOf` handler, so any such keyword would be silently ignored on the Python side and diverge from Ajv. The optional defence-in-depth "reverse-guard via `not.anyOf`" is therefore **not used**; identity is pinned instead by the forward `additionalProperties:false` canonical plus the `const`-typed reverse-guard (`if canonical has parts then type=="ratio"`), exactly mirroring the transformation precedent's `const` reverse-guard.

The **comparison / best-buy answer is the existing `multiple-choice` enum member**, not a new `comparison` type — so `ratio` is the at-most-one new answer type and the platform constraint holds.

1. **Append `"ratio"`** to `$defs/answerType.enum` after the existing tail token (`"transformation"` on the same array line), so every current member's byte-position is unchanged — every approved family's items stay schema-valid **byte-for-byte**. The approved-family fixture-drift check is the gate that catches any accidental array reflow.
2. **NO new `answer` property** — the structured value **IS `answer.canonical`** (canonical-first), exactly as transformations stores its descriptor; there is **no** sibling `answer.ratio` field. `answer`'s `additionalProperties:false` is unchanged and still rejects any stray top-level key.
3. **Discriminant rules** as `if/then/const` under `answer.allOf`, keyed on `answer.type=="ratio"`, constraining `answer.canonical`:
   - `if answer.type == "ratio" then { properties:{ units:false, measure:false, tolerance:false, canonical:<the ratio object> } }` — `units`/`measure`/`tolerance` are **forbidden** (ratio answers carry no units and are exact), and `answer.canonical` is the structured ratio (not stored twice, never a formatted string);
   - within `answer.canonical`: `required:["parts"]`, `additionalProperties:false`; `parts` is an array of `integer` with `minItems:2`, `maxItems:3` (two- or three-part only in v1.0.0), each item `{type:"integer", minimum:1}` (**positive integers only**; zero and negative parts rejected by schema); a `gcd(parts)==1` simplest-form obligation is enforced by the §9 validator and the offline checker (an arithmetic predicate the JSON-Schema layer cannot express, so it lives in `validate()` + conformance, asserted as `ratio-gcd-one`, while the schema enforces the structural `parts` shape).

**`maxItems` is a NEW, named, owner-visible conformance-checker delta — NOT a no-op reuse.** `maxItems` appears **zero** times in the current `schemas/question-item.schema.json` and **zero** times in `oracle/check_conformance.py` (which today handles only `minItems`). The `ratio` `parts` arity cap (`maxItems:3`) is therefore the **first** `maxItems` use anywhere, and the offline conformance checker would **silently pass** a 4-part array without support. So this delta **explicitly adds one additive `maxItems` branch to `oracle/check_conformance.py`, symmetric to the existing `minItems` branch**, listed as a named delta in the §15.4 gate table and the §16 shared-asset row (§15/§16 do **not** claim "no new checker code path" for the checker — only the runtime Ajv path is unchanged). The branch ships with a **regression assertion that all eight prior families' conformance output is unchanged** and a **4-part `parts` NEGATIVE conformance fixture** so the new branch is exercised **offline** (not only by the Ajv test), guaranteeing Ajv and Python apply identical arity rules.

`answer.display` for a ratio item IS the §5 formatter's ASCII colon string (e.g. `"2:3:5"`), **derived** from `answer.canonical`, never the ground truth and never a second copy of the tuple (`canonical-display-cannot-drift`, §14). The **NEGATIVE schema/conformance fixtures** of §4 prove rejection of every disallowed shape (zero part, negative part, non-integer part, `units`/`measure`/`tolerance` present, `parts` with **<2** items via `minItems`, `parts` with **>3** items via the new `maxItems` branch, a sibling `answer.ratio` field). Number/fraction answers (sharing, missing-part, unit-rate, direct/inverse, scale) reuse the **existing** exact `integer` / `exact-rational` answer types unchanged; the best-buy comparison reuses the **existing** `multiple-choice` type unchanged; table-completion sharing reuses the **existing** `table-completion` container (§7) with correspondence by label. So `ratio` is the **only** new answer type the family introduces (the at-most-one constraint is met).

The discriminant is enforced on **every path**: runtime bundled Ajv, offline `check_conformance.py` (with the additive `maxItems` branch), import, bank storage, migration/back-compat, export, and the §9 validator — identical rules everywhere, because the delta uses only the shared keyword subset (`if/then/const/required/additionalProperties/minItems/maxItems/minimum/type`), never `oneOf`/`anyOf`.

### 15.2 Versioning — v1.0.0, the twelve tasks, the family identity constants

v**1.0.0** ships **exactly** the twelve tasks of the brief, **1:1** with the authored objectives, over the **Proportion/Ratio** strand in the Middle-School number area, named by the single canonical `RATIO_TASKS` slug set (§1.3): `simplify`, `write_from_quantities`, `ratio_to_fraction`, `fraction_to_ratio`, `share_two_part`, `share_three_part`, `missing_part`, `direct_proportion`, `inverse_proportion`, `unit_rate`, `best_buy`, `simple_scale`. **No** `write_ratio` / `simplify_ratio` / `direct_proportion_unitary` / `inverse_proportion_unitary` spelling exists anywhere in the family's code, fixtures, tokens, or objective IDs.

The family pins **one identity pair**, exported from `domains/<area>/proportion-ratio.ts` and byte-mirrored in `oracle/spi_oracle/proportion_ratio.py`:

```
export const GENERATOR_ID = "gen.proportion.ratio";
export const GENERATOR_VERSION = "1.0.0";
```

Objectives are `SPI.MIDDLE.RATIO.<MICRO>.01` (the single objective-ID pattern of §1, the full upper-cased task slug as `<MICRO>`, e.g. `SPI.MIDDLE.RATIO.SIMPLIFY.01`, `SPI.MIDDLE.RATIO.WRITE_FROM_QUANTITIES.01`, `SPI.MIDDLE.RATIO.DIRECT_PROPORTION.01`, `SPI.MIDDLE.RATIO.INVERSE_PROPORTION.01`, `SPI.MIDDLE.RATIO.SHARE_THREE_PART.01`) — one pattern, **no** `_UNITARY` suffix or other competing spelling. Every generated item's `generatorId`/`generatorVersion`, the golden/parity fixtures, the distribution report, the review pack, the manifest, and the `core/sdk/sequence-registry.ts` entry carry **this exact pair**; a `version-fields-present` validator check asserts `item.generatorId === GENERATOR_ID && item.generatorVersion === GENERATOR_VERSION`, and the artifact-IDENTITY test (§15.5) asserts the visible version string matches in both oracles. A `proportion-ratio-graph.test.ts` assertion enforces that `OBJECTIVE_BY_TASK`, the §10 `RULES_BY_TASK`, the generator dispatch, the §11 config, the §14 `cell:<task>` tokens, and this scope list all key off the **same twelve-member set** and that **no alternative slug or objective-ID spelling appears anywhere** — no legacy slug survives. The deferred topics of §12.10 are **deterministically excluded** (no task entry; `paramsInDomain` rejects; integration test asserts they `generate`-throw and never appear in the 10k sweep). Any future change ships as a **new version** (v1.0.1+).

The schema document `version` field stays `"1.0.0"` across this delta — matching the verified `quantity`/`transformation` precedent, which added an enum member **without** bumping the schema `version`. This non-bump is intentional and precedent-faithful, called out here so a reviewer does not flag it as an omission.

### 15.3 Oracle-first build order

1. **Apply the additive CANONICAL-FIRST `answer.type` schema delta FIRST** (§15.1): append `"ratio"` to `$defs/answerType.enum` and add the `if/then/const` rules under `answer.allOf` constraining `answer.canonical`, **add the additive `maxItems` branch to `oracle/check_conformance.py`** (with the eight-family unchanged-output regression assertion), then recompile via `scripts/compile-schemas.mjs` → `core/schema/compiled/question-item.validator.mjs`. Existing approved items + fixture bytes are UNCHANGED. This precedes objective authoring because the ratio-answer tasks declare `answerTypes:["ratio"]`, whose enum member only resolves under Ajv / `oracle/check_conformance.py` once the delta lands. The schema-migration / back-compat gate and the NEGATIVE schema/conformance fixtures (§4, including the 4-part `maxItems` negative fixture) are part of this step.
2. Author `curriculum/objectives/SPI.MIDDLE.RATIO.json` (the twelve objectives) against `schemas/curriculum-objective.schema.json`. Each carries `objectiveWording`, `successCriteria[]`, `prerequisites[]` (resolving to defined, approved objectives — the verified anchors `SPI.MIDDLE.NUM.SIGNED_OPERATIONS.01`, `SPI.MIDDLE.ALG.INVERSE_OPERATIONS.01`, `SPI.MIDDLE.ALG.LINEQ.ONESTEP_MUL.01`, all present + `reviewStatus:"approved"` so the DAG resolves with zero unresolved-prerequisite warnings), `calculatorPolicy:"calculator-not-required"`, and `commonMisconceptions[] → MISC.RATIO.*` (the §10 `RULES_BY_TASK` map is the single source). `core/curriculum/graph-check.ts` enforces no-duplicate-id + no-prerequisite-cycle (the DAG); the bespoke `proportion-ratio-graph.test.ts` asserts the twelve objectives present, prerequisites resolve, the single-source `OBJECTIVE_BY_TASK`, the no-alternative-spelling string scan, and `reviewStatus:"approved-for-implementation"` for the gated build.
3. Write the **Python oracle** (`oracle/spi_oracle/proportion_ratio*`): the §6 Ratio model + exact integer/rational engine, the §7 sharing/table-completion model, the canonical monochrome bar-model/number-line/table SVG, the §4/§5 `ratio` schema + parser + canonicalizer + equivalence checker, and the `MISC.RATIO.*` registry. Generate golden + parity fixtures from the oracle (oracle-authoritative).
4. Mirror in **TypeScript** (`domains/<area>/proportion-ratio.ts`) using `core/exact-math/rational.ts`, `core/seeded-random/mulberry32.ts`, `core/difficulty/band.ts`, the shared theme mechanism, and the additive `ratio-theme` extension (theme id `spi-math-ratio-theme/1`, new `--cx-ratio-*` variables — §13/§16). The canonical (monochrome) SVG and `params`/`answer` (with diagnostics) are **byte-identical Py↔TS**; the themed/exported copies are TypeScript-only.

### 15.4 Gates (all blocking before any approval)

| Gate | Spec |
| --- | --- |
| Golden | frozen `oracle/golden/proportion-ratio.golden.json`, Py-authored, TS-verified byte-identical (canonical item JSON + canonical monochrome figure SVG) |
| Parity | a **task-pinned parity fixture ≥ 300 entries, sized so all twelve tasks (and each supported interaction) are represented** — `proportion-ratio.parity.json`; Py + TS **byte-identical** for item JSON + SVG; plus explicit tests that an **unsupported MC request is rejected or redrawn for every non-MC-eligible task** with `interaction-not-supported`, and that MC-eligible tasks produce three distinct misconception-backed distractors |
| Schema + conformance | the single additive `answer.type:"ratio"` extension (§15.1) — structured value stored **directly as `answer.canonical`** (canonical-first; no sibling field), `if/then/const` under `answer.allOf`, **only the shared keyword subset (no `oneOf`/`anyOf`, even inside `not`)**, additive + back-compatible (appended after the enum tail; `answer.additionalProperties:false` unchanged); `units`/`measure`/`tolerance` forbidden; positive-integer two/three-part `parts`; the **new additive `maxItems` branch in `check_conformance.py`** (eight-family-output-unchanged regression + 4-part offline negative fixture); the NEGATIVE schema/conformance fixtures prove every rejection; enforced identically on runtime Ajv, offline conformance, import, bank storage, migration/back-compat, export, and the §9 validator |
| Sweep | `SPI_SWEEP = 10000`: `invalid: 0`; **every declared band reachable before fixtures freeze** (the distribution is the reachability proof); FR diagnostics realised (every eligible `MISC.RATIO.*` rule surfaces feedback through the adapter the validator recomputes; no null prediction counts as exercised); the unsupported-MC rejection/redraw test passes per non-eligible task; the §12 edge-case gates fire (no zero/negative part; integer-share exactness; missing-part divisibility; unit-rate/best-buy non-ties; inverse exactness; unambiguous scale; equivalent accepted/rejected per policy); **reproducibility re-check** (re-running a seed reproduces byte-for-byte) |
| Distribution | `proportion_ratio_distribution.json` emitted + integrity-checked; the authoritative reachability artifact the §14 coverage matrix derives from |
| Ratio/math validity | §9 named checks pass on every swept item: `parts-positive`, `parts-integer`, `ratio-gcd-one`, `order-unambiguous`, `total-divisible-by-sum`, `shares-sum-to-total`, `missing-part-exact`, `missing-part-divides`, `unit-rate-exact`, `inverse-product-invariant`, `inverse-result-integer-exact`, `scale-factor-exact`, `scale-direction-unambiguous`, `best-buy-unique-winner`, `cross-multiplication-equivalence`, `table-correspondence-by-label`, the §5 checker-contract checks (`ratio-canonical-first`, `no-duplicate-ratio-field`, `canonical-display-cannot-drift`), and the §14.6 answer-absence checks |
| Style-isolation | per-root `class="cx-figure"` isolation + materialised-export tests pass on the additive `ratio-theme`; `no-inline-var-in-attrs` passes (no `var(` in any presentation attribute); `theme-variable-namespacing` passes (every new variable `^--cx-ratio-`, colliding with no other family); a theme-completeness test asserts **every** declared `--cx-ratio-*` variable has a value in **all four** modes **and a greyscale value in print** (§13.5); **all prior approved families' output stays byte-for-byte unchanged** |
| a11y | axe gate: **0 critical / 0 serious, WCAG AA**; interior primitives presentation-only under the single `role="img"` `cx-figure` root; `media[].dataTableFallback` present; non-colour (unknown-marker hatch/dash + `?`) distinction present and greyscale-authoritative; `fallback-no-answer-leak`, `spokenmath-given-only`, `display-ascii-colon`, `no-color-only`, `no-inline-var-in-attrs` pass |
| Exports | worksheet / answer-key / solutions + offline KaTeX render; **bank-json round-trip lossless** — including the new `ratio` value (which IS `answer.canonical`) and its derived `answer.display`, the table-completion label→value map, and the `multiple-choice` best-buy selection; **6000×4200** colour + print exports self-contained |
| Integrity + graph | the blocking artifact-integrity + artifact-IDENTITY tests (manifest + **SHA-256** over every artefact, plus visible version/commit identity, Py + TS) and the bespoke graph test (twelve-member slug set, no alternative spelling) pass |
| Coverage | the §14 builder returns `0` (all reachable cells covered, `allCovered:true`, `requiredCells == derivedRequiredCells`), the five named coverage tests pass, and the **ratio-checker matrix** has verified evidence for every `RESULT_CODES` member (§5, lower-kebab) |
| Approved-generator regression | arithmetic / geometric / linear / angle-geometry / coordinate-lines / data-handling / mensuration / transformations output **byte-for-byte UNCHANGED**; the eight families' **conformance** output is also unchanged under the new `maxItems` branch |

### 15.5 Registration, approval, immutability

The family registers in `core/sdk/sequence-registry.ts` as a new `GENERATORS[]` entry with an **explicit** `approvalStatus:"pending-review"` and the `GENERATOR_ID`/`GENERATOR_VERSION` of §15.2 during the build. Per `generatorsForMode`/`approvedGenerators`, a `pending-review` family is exposed **only in review mode** and **excluded from `approvedGenerators()`**, so it is gated out of normal Studio and out of production exports/samples (`build-samples.mjs` carries **zero** ratio records, asserted by the harness approval-lifecycle test) until the owner's review-pack decision. The objective files sit at `reviewStatus:"approved-for-implementation"` during the build.

On the **review-pack decision**:

- **APPROVE** → the registry entry flips to `approvalStatus:"approved"` with a `DECISION_LOG` reference (date + number); the twelve objective files move to `reviewStatus:"approved"`; `build-samples.mjs` emits all twelve tasks into `bank.json`; the reviewed items are recorded as **approved golden exemplars** (`APPROVED_VERSIONS.md`); and the **golden + parity + canonical-SVG fixtures, review pack (.md/.json) + coverage matrix, ratio-checker matrix, visual audit, distribution report, browser verification, generation manifest, and the 6000×4200 export hashes become immutable** — hash-attested by `docs/review/proportion_ratio_manifest.json` (with `versionTags {previousVersionTag, currentImplementationTag, approvedTag}`) and the blocking artifact-integrity + artifact-IDENTITY tests (SHA-256 plus visible version/commit identity, Py + TS). A tag `approved-proportion-ratio-v1.0.0` is cut.
- **REVISE** → a corrected v1.0.1 with the prior version preserved unchanged at its tag, only the family's artefacts regenerated.
- **REJECT** → routes to a revised version; the rejected version is never registered.

Registry approval **does not auto-approve future items**: newly generated items always begin `lifecycle.state = "generated"` → **`machine-validated`**, and there is **no auto-publication**. The approved version is preserved in history (tags), unregistered and unselectable once superseded. The 10,000-seed stability + reproducibility run is the standing cross-version regression guard, and the **approved-family fixture-drift checks** ensure no approved fixture changes a byte when this family lands.

---

## 16. Reusable infrastructure versus family-specific code

The family is built to **maximise reuse** of the approved infrastructure (cited by name) and add only the genuinely ratio-specific pieces. Nothing in the shared column is reinvented; the `ratio-theme` (id `spi-math-ratio-theme/1`) **extends `cartesian-theme/1` and follows the `data-chart-theme` additive PATTERN**, it does not depend on or build atop `data-chart-theme`. The **one honest exception** to "shared assets reused unchanged" is the conformance checker: the `ratio` delta adds a small additive `maxItems` branch to `oracle/check_conformance.py` (§15.1) — this is called out explicitly below, not hidden under "no new checker code path."

### 16.1 Shared — reused as-is, by name

| Shared asset | Source | Reuse in ratio |
| --- | --- | --- |
| Seeded RNG (byte-identical Py/TS, deterministic redraw order; `next_int(lo,hi)` INCLUSIVE; call ORDER is the parity contract; `Math.random` forbidden) | `core/seeded-random/mulberry32.ts` + `oracle/spi_oracle/seeded_random.py` | drives the deterministic ratio/quantity/context draw, the §12 redraw loop, and MC-eligibility redraw; the call **order** is the parity contract |
| Exact arithmetic (integers + exact Rational/Fraction, normalized `{num,den}`, `den ≥ 1`) | `core/exact-math/rational.ts` + Python `fractions.Fraction` | `gcd` simplification, cross-multiplication equivalence (`a*d == b*c`), total-parts/unitary/inverse-product/scale exactness, rational unit-rate values; every comparison is reduced-Rational equality; **no float, no tolerance, no irrational** |
| Canonical-stringify (sorted keys, compact; equals Python `json.dumps(sort_keys=True, ensure_ascii=False, separators=(",",":"))`) | the shared `canonicalStringify` | serializes `answer.canonical = {parts:[…]}` and every item identically Py↔TS; the parity fixture asserts byte-identity |
| Canonical-SVG discipline + render-mode/theme MECHANISM (per-root `class="cx-figure"` isolation, ONE document-level `COMMON_CSS`, `presentationSvg(svg,mode)` / `exportSvg(svg,mode,w,h)`, four modes print/premium/premium-dark/accessible, integer-6× 6000×4200, `role="img"`+`aria-label`, `<title>`/`<desc>` first children, the `GREYS` no-colour-only greylist, `resolveCommonCss` rewriting `var()` only inside the baked `<style>`) | `core/visual-style/cartesian-theme.ts` (genuinely exported); the data-chart-theme / mensuration-theme / transformations-theme precedents | the bar-model/number-line/table figures stamped with the **shared `cx-figure` root class** (never a `ratio-figure` root); the canonical monochrome `media[0].svg` carries only the family's hardcoded monochrome `STYLE` and no root class; premium/dark/accessible/print are TS-only derivations; byte-parity required of the **monochrome canonical** SVG, not the themed/exported copies |
| Base-geometry/additive-overlay **channel-group** pattern (`cx-base`/`cx-annot`/`cx-overlay`, `answer-key-base-geometry-identical` + `answer-key-overlay-additive-only`) | `domains/measurement/mensuration.ts` (the channel-group precedent) | the ratio `figure()` composes student vs answer-key over byte-identical base geometry (§14.6) |
| Deterministic semantic HTML-TABLE rendering + `dataTableFallback` | `domains/.../data-handling.ts` | the **proportional-table** fallback + the table-completion rendering, correspondence by label (§7/§13) |
| Difficulty banding (`bandFromScore(score)=clamp(1+floor(score*5))`, output-neutral metadata, ONE machine-readable source of truth) | `core/difficulty/band.ts` | the §11 weighted **closed-enum** axes → band, clamped per objective; bands PROVISIONAL until the 10k distribution proves each reachable |
| Schema validation — build-time precompiled **Ajv** (runtime path UNCHANGED) | `core/schema/compiled/question-item.validator.mjs` (`scripts/compile-schemas.mjs`) | the `ratio` discriminant obligations compile straight through; **no new Ajv code path** (Ajv already supports `maxItems`) — the delta uses only keywords Ajv already implements |
| Offline conformance checker (`$ref`/`const`/`allOf`/`if`/`then`/`not`/`minItems`, **no `oneOf`/`anyOf`**) | `oracle/check_conformance.py` | reused for all existing rules, **PLUS one additive `maxItems` branch** (symmetric to the existing `minItems` branch) added for the `ratio` `parts` arity cap — a **named, owner-visible delta** (§15.1), shipped with an eight-family-output-unchanged regression and a 4-part offline negative fixture; the delta ships **no `oneOf`/`anyOf`** so the checker's unsupported-keyword gap is never hit |
| Misconception engine (`MISC.<PREFIX>.*` registry shape Py + byte-parity TS, `RULES_BY_TASK`, adapter `(ctx) → predicted wrong response | null`, validator independently recomputes each prediction) | the shared misconception-registry pattern | `MISC.RATIO.*` (§10) plugs in unchanged; FR diagnostics + MC distractors only where eligible; predictions never enter any figure/a11y field; incomplete/null predictions stored as `studentResponseText`+`expectedResultCode`, never counted as coverage |
| Primitive answer checkers (exact integer / exact-rational) + the live `multiple-choice` interaction checker | `core/answer-checking/rational-checker.ts` + the shared MC checker | the **integer/exact-rational** answers (sharing, missing-part, unit-rate, direct/inverse, scale) reuse the rational checker unchanged; the **best-buy comparison** reuses the existing `multiple-choice` checker unchanged; only the `ratio` value gets the new family-local checker (§16.3) |
| Review-pack reachability COVERAGE-MATRIX builder + the five blocking coverage tests | `oracle/make_review_pack_data_handling.py` / `…_mensuration.py` (`DECISION_LOG` #48) | reused verbatim (§14): cells derived from the distribution, greedy set-cover, builder FAILS on any missing reachable cell, honest `allCovered` |
| Manifest / artifact-integrity / artifact-IDENTITY / style-isolation harness (SHA-256 + visible-version/commit identity, Py + TS) | `oracle/make_*_manifest.py` | `oracle/make_proportion_ratio_manifest.py` is a direct adaptation, with `versionTags` |
| SDK approval-lifecycle gating (`approvalStatus`, `generatorsForMode`, `approvedGenerators`) + curriculum graph integrity (DAG, no dup ids, prerequisites resolve) | `core/sdk/sequence-registry.ts` + `core/curriculum/graph-check.ts` | the family registers `pending-review`, gated until approval (§15.5); the graph-check enforces the objective DAG |
| Delivery harness (review-pack/audit generators, offline HTML/JSON exporters, bank-json round-trip, axe gate, browser verification via the preview tool) | the shared harness | driven family-specifically; mechanism unchanged |

### 16.2 Ratio-specific — new, this family only

| New asset | What it is |
| --- | --- |
| **The canonical Ratio model** (§6) | the ONE exact ratio model used by parameter generation, prompt, answer, worked solution, diagnostics, validation, parser/checker, and review-pack coverage: ordered parts; simplified canonical parts; original unsimplified parts where relevant; total parts; scale factor where relevant; known + missing part where relevant; context labels; `answerPolicy`; answer-shape tag |
| **The `ratio` answer contract + parser / formatter / canonicalizer / equivalence checker** (§4/§5) | the new `answer.type` whose ordered-integer-tuple value **IS `answer.canonical`** (canonical-first; no sibling field), the anchored colon parser (spaces accepted; word-form `to` and Unicode colon NOT supported in v1.0.0 — decision G — both rejected as `unsupported-term` / `malformed-response`), the gcd canonicalizer, the ASCII colon formatter, and the cross-multiplication equivalence checker with the single lower-kebab `RESULT_CODES` vocabulary plus the boolean `partial` field (the headline new contract — §16.3) |
| **The sharing / table-completion model** (§7) | total-parts sharing (two- and three-part), missing-part backward construction (with the hard `parts[k] ∣ v` integer gate, §12.6), and the **label-keyed** table-completion answer (correspondence by `location`, not row order), with the point-of-truth sum-agreement checks (`shares-sum-to-total`, `table-correspondence-by-label`) |
| **The bar-model / double-number-line renderer** (§8) | the non-Cartesian educational figure system — bar models, double number lines, proportional tables — stamped with the shared `cx-figure` root class, showing GIVEN quantities only, never revealing missing values, distinguishing known/unknown by hatch/dash/`?` (class-driven, never inline `var()`), the `cx-base`/`cx-annot`/`cx-overlay` composing `figure()`, the single shared tick x-position array for double-number-line lane alignment, the label-collision-avoiding placement (deterministic complete bounding-box clearance), and the not-to-scale guard for hidden values; `inverse_proportion` ships no proportional figure |
| **The `ratio-theme` extension** (id `spi-math-ratio-theme/1`) | a versioned extension that `extends "spi-math-cartesian-theme/1"` and follows the `data-chart-theme` additive PATTERN (without depending on it), adding bar-segment-fill, segment-divider, segment-label, bracket/total, number-line-axis, tick, tick-label, unknown-marker, and answer-overlay primitives as **new `--cx-ratio-*` variables** (namespaced to collide with no other family) + one additive ruleset, every variable resolving to a greyscale value in print, all meaning-bearing styling **class-driven (no inline `var()`)**; **all prior approved families' output stays byte-for-byte unchanged** |
| **The ratio/proportion validators** (§9) | the §9.3 named checks (`parts-positive`, `ratio-gcd-one`, `cross-multiplication-equivalence`, `total-divisible-by-sum`, `missing-part-exact`, `missing-part-divides`, `unit-rate-exact`, `inverse-product-invariant`, `scale-factor-exact`, `best-buy-unique-winner`, etc.) recomputing every answer/figure by a second, generator-independent route |
| **`MISC.RATIO.*` registry** (§10) | the owner-mandated part-whole / order / scaling / unit-rate diagnostics + `RULES_BY_TASK`, byte-parity Py/TS, sole id source (`DOES_NOT_SIMPLIFY_FULLY`, `REVERSES_ORDER`, `ADDS_PARTS_INCORRECTLY`, `TREATS_ONE_PART_AS_WHOLE`, `WRONG_TOTAL_PARTS`, `DIVIDES_BY_ONE_PART_INSTEAD_OF_TOTAL`, `MULTIPLIES_INSTEAD_OF_DIVIDING_IN_UNITARY`, `DIVIDES_INSTEAD_OF_MULTIPLYING_IN_UNITARY`, `DIRECT_FOR_INVERSE`, `INVERSE_FOR_DIRECT`, `COMPARES_PRICES_WITHOUT_UNIT_RATE`, `CHOOSES_LOWEST_PRICE_NOT_BEST_VALUE`, `SCALE_FACTOR_WRONG_DIRECTION`, `ADDITIVE_DIFFERENCE_INSTEAD_OF_MULTIPLICATIVE_SCALE`, `RATIO_TO_FRACTION_ONE_PART_OVER_OTHER_NOT_OVER_WHOLE`, `EQUIVALENT_BUT_UNSIMPLIFIED_WHEN_SIMPLEST_REQUIRED`) |
| **Curriculum objectives + strand** | the twelve `SPI.MIDDLE.RATIO.*` objective files (each with `successCriteria[]`, `calculatorPolicy:"calculator-not-required"`, `commonMisconceptions[]→MISC.RATIO.*`); the single-source `OBJECTIVE_BY_TASK` map keyed by the `RATIO_TASKS` slugs |
| **The additive `maxItems` conformance branch** | one new branch in `oracle/check_conformance.py` (symmetric to `minItems`) enforcing the `ratio` `parts` `maxItems:3` arity cap offline; shipped with an eight-family-output-unchanged regression assertion and a 4-part negative conformance fixture (§15.1) — the one honest checker delta |
| **The review pack + audit content** | `oracle/make_review_pack_proportion_ratio.py`, the visual audit, distribution report, browser verification, the **ratio-checker matrix**, and the manifest of §14 |

### 16.3 The headline decision — where the `ratio` answer contract lives (family-local)

**Decision: FAMILY-LOCAL.** The `ratio` answer contract and its parser / formatter / canonicalizer / equivalence checker live in **`domains/<area>/proportion-ratio-ratio.ts`** (+ the Python mirror `oracle/spi_oracle/proportion_ratio_ratio.py`), alongside the family — matching the **verified** precedent exactly: the dimensional-`quantity` contract is family-local at `domains/measurement/mensuration-units.ts`, and the `transformation` descriptor contract is family-local at `domains/geometry/transformations-descriptor.ts`. `core/answer-checking/` holds only the primitive `rational-checker` (and `coordinate-checkers`) and the shared `multiple-choice` checker, which the family reuses **unchanged** for the number/fraction and best-buy-comparison answers. The new `ratio` checker is the one piece of answer-checking that is family-new.

Rationale for family-local:

- It **matches the approved mensuration + transformations precedent verbatim** (structured-answer contract beside its family), so there is no new cross-cutting surface to re-litigate at approval.
- The v1.0.0 surface is deliberately narrow — `parts` are **positive integers**, two- or three-part, `gcd == 1` canonical, order-significant, exact cross-multiplication equivalence, the per-task `accept-equivalent` / `require-simplest` policy. Negative/zero parts, >3 parts, rational ratio terms, continued/compound proportion, and any deferred topic (§12.10) are **out of v1.0.0 scope**.
- Should a **future** family need the same ratio descriptor, it can be **promoted to shared core as a deliberate, owner-gated refactor at that time** (a backward-compatible widening — a new arity, an unordered-comparison flag, a rational-term variant) with its own version/parity/integrity gates — rather than over-generalising speculatively now.

This keeps the family self-contained while the primitive exact-integer/exact-rational checks (the number/fraction answers) and the live `multiple-choice` checker (the best-buy comparison) continue to reuse shared `core/answer-checking/`. The `ratio` schema delta (§15.1) is the **only** schema change and is the **third** structured `answer.type` added the identical additive, owner-gated, `if/then/const`, canonical-first way after `quantity` and `transformation` — descriptor IS `answer.canonical`, no sibling field, no `oneOf`/`anyOf`, enforced identically on every path, existing approved items byte-for-byte unchanged. The one shared-dependency edit (the additive `maxItems` conformance branch) is the single honestly-declared checker delta, gated by an eight-family regression.
