# Linear Equations (one variable) — Generator Proposal v1.0.0

**Status: APPROVED WITH REVISIONS (owner, 2026-06-21).** The owner approved the
pilot subject to revisions. This top section is the **authoritative final v1.0.0
contract**; the sections below it are retained as background and are superseded by
this section wherever they differ. Objectives and this spec become
**curriculum-approved only after** the owner reviews the completed review pack;
generated items begin at `machine-validated` and are never auto-approved/published.

Generator id: `gen.algebra.linear-equations` · version `1.0.0`.

---

## FINAL SPECIFICATION (approved) — implementation contract

### F-A. Placement, objective IDs, wording, prerequisites, task mapping

Placement approved: **SPI-Math Middle School → Algebra → Linear equations in one
variable**. ID scheme approved (D-0): six-segment `SPI.MIDDLE.ALG.LINEQ.<MICRO>.01`.
A **future normalization task** is recorded for the existing shallower
`SPI.MIDDLE.ALG.SUBSTITUTION.01`; do **not** silently rename it.

Five objectives (final approved wording), each `version 1.0.0`,
`reviewStatus: "proposed"` (curriculum-approved only after pack review):

| Task value | Objective ID | Final wording | Hard prerequisites | Related/supporting |
|---|---|---|---|---|
| `one_step_add` | `SPI.MIDDLE.ALG.LINEQ.ONESTEP_ADD.01` | Solve a one-step linear equation of the form `x + b = c`, using the same inverse operation on both sides. | `SPI.MIDDLE.NUM.SIGNED_OPERATIONS.01`, `SPI.MIDDLE.ALG.INVERSE_OPERATIONS.01` (planned) | `SPI.MIDDLE.ALG.SUBSTITUTION.01` |
| `one_step_mul` | `SPI.MIDDLE.ALG.LINEQ.ONESTEP_MUL.01` | Solve a one-step linear equation of the form `ax = c`, where `a ≠ 0`, by dividing both sides by the coefficient of `x`. | `SPI.MIDDLE.NUM.SIGNED_OPERATIONS.01`, `SPI.MIDDLE.ALG.INVERSE_OPERATIONS.01` (planned) | `SPI.MIDDLE.ALG.SUBSTITUTION.01` |
| `two_step` | `SPI.MIDDLE.ALG.LINEQ.TWOSTEP.01` | Solve a two-step linear equation of the form `ax + b = c` by applying inverse operations in an appropriate order. | `…LINEQ.ONESTEP_ADD.01`, `…LINEQ.ONESTEP_MUL.01` | `SPI.MIDDLE.ALG.SUBSTITUTION.01` |
| `both_sides` | `SPI.MIDDLE.ALG.LINEQ.BOTHSIDES.01` | Solve a linear equation of the form `ax + b = cx + d`, where `a ≠ c`, by collecting variable terms on one side and constants on the other. | `…LINEQ.TWOSTEP.01` | `SPI.MIDDLE.ALG.SUBSTITUTION.01` |
| `brackets` | `SPI.MIDDLE.ALG.LINEQ.BRACKETS.01` | Solve a linear equation containing one set of brackets by expanding, simplifying, and then solving the resulting linear equation. | `…LINEQ.TWOSTEP.01`, `SPI.MIDDLE.ALG.EXPAND_BRACKETS.01` (planned) | `SPI.MIDDLE.ALG.SUBSTITUTION.01` |

Planned/unresolved prerequisite IDs remain explicitly marked `planned` until those
objectives are authored (the graph-check will warn; acceptable). Substitution is a
**related/supporting** objective (used for checking solutions), not a hard prereq.

### F-B. Task matrix, guards (approved; D-1 confirmed)

Reduced form `p·x + q = r·x + t`, solution `s = (t − q)/(p − r)`, require `p ≠ r`.
`one_step_mul` = `ax = c` only; **exclude** `x/a = c` and all fraction-bar variable
forms (deferred to a later denominators family/version). Structural-authenticity
guards (reject + deterministically resample otherwise):

| Task | Form | Guards |
|---|---|---|
| `one_step_add` | `x + b = c` | `b ≠ 0` |
| `one_step_mul` | `a·x = c` | `a ≠ 0`, `a ≠ 1` |
| `two_step` | `a·x + b = c` | `a ∉ {0,1}`, `b ≠ 0` |
| `both_sides` | `a·x + b = c·x + d` | `a ≠ 0`, `c ≠ 0`, `a ≠ c` |
| `brackets` | `k(p·x + q) = c·x + d` | `k ∉ {0,1}`, `p ≠ 0`, `q ≠ 0`, `kp ≠ c` |

Exact-rational solutions approved. Fractional **coefficients** only at suitable
higher bands, displayed as coefficients (never as `x/den` variable-over-denominator
forms). Backward construction (pick `s` first, set the dependent constant) approved.

### F-C. Misconception rules (final approved set)

Every MC misconception has one unambiguous formula, applicability, rationale, and
feedback. Wrong value `W` over the reduced form; for one-step the displayed form is
`x + q = t` (`p=1, r=0`) or `p·x = t` (`q=0, r=0`).

| ID | Formula `W` | Applicability | Feedback |
|---|---|---|---|
| `MISC.LINEQ.STOPS_BEFORE_DIVIDING` | `t − q` | `|p − r| ≠ 1` | "You have isolated the variable term, but not the variable. Divide both sides by the coefficient of x." |
| `MISC.LINEQ.WRONG_INVERSE` | `(t + q)/(p − r)` | `q ≠ 0` | "Use the inverse operation on the constant term and apply it to both sides." |
| `MISC.LINEQ.VAR_SIGN` | `(t − q)/(p + r)` | `r ≠ 0`, `p + r ≠ 0` | "Subtract rx from both sides. The new variable coefficient is p − r, not p + r." |
| `MISC.LINEQ.CONST_SIGN` | `(q − t)/(p − r)` | a nonzero constant-collection step occurs (`q ≠ 0`) and `W ≠ s`; **not for `one_step_mul`** | "Apply the same subtraction to both sides and check the order of the constants." |
| `MISC.LINEQ.DISTRIBUTE_PARTIAL` | re-solve with `k(px+q) → kp·x + q` | `brackets`, `k ≠ 1`, `q ≠ 0` | "Multiply every term inside the brackets by the factor outside." |
| `MISC.LINEQ.COMBINE_UNLIKE_AS_COEFFICIENT` | `t/(p + q − r)` | `q ≠ 0`, `p + q − r ≠ 0` | "An x-term and a constant are unlike terms. Their coefficients cannot be combined." |
| `MISC.LINEQ.DIVIDE_ONE_TERM` | `t/(p − r) − q` | `q ≠ 0`, `p − r ≠ 0`, `W` distinct | "When dividing an equation, divide every term on the relevant side by the coefficient." |
| `MISC.LINEQ.DIVIDE_BY_CONSTANT` | `(t − q)/q` | `q ≠ 0`, `q ≠ p − r`; **not for `one_step_mul`** | "Divide by the coefficient of x, not by the constant term." |
| `MISC.LINEQ.IGNORE_CONSTANT` | `t` (for `x + q = t`) | `one_step_add`, `q ≠ 0` | "Apply the inverse of the constant to both sides; don't ignore it." |
| `MISC.LINEQ.MULTIPLY_INSTEAD_OF_DIVIDE` | `p × t` (for `p·x = t`) | `one_step_mul`, `p ∉ {−1,1}`, `t ≠ 0` | "To undo multiplication by p, divide both sides by p." |
| `MISC.LINEQ.REVERSES_DIVISION` | `p / t` (for `p·x = t`) | `one_step_mul`, `t ≠ 0` | "The equation gives x = t/p, not p/t." |

`MISC.LINEQ.SIGNED_ARITH_SLIP` is a **diagnostic category only** — excluded from MC
generation (D-2). `MISC.LINEQ.DISTRIBUTE_NONE` is **deferred** (not in v1.0.0, D-3):
only one bracket-distribution rule (`DISTRIBUTE_PARTIAL`) is used, at most once/item.

**Eligibility per task** (every item must use **three distinct** pathways; on
collision/insufficiency, **deterministically regenerate the parameters**):
- `one_step_add`: IGNORE_CONSTANT, WRONG_INVERSE, CONST_SIGN, COMBINE_UNLIKE_AS_COEFFICIENT (where applicable)
- `one_step_mul`: STOPS_BEFORE_DIVIDING, MULTIPLY_INSTEAD_OF_DIVIDE, REVERSES_DIVISION
- `two_step`: STOPS_BEFORE_DIVIDING, WRONG_INVERSE, DIVIDE_ONE_TERM, DIVIDE_BY_CONSTANT, COMBINE_UNLIKE_AS_COEFFICIENT
- `both_sides`: applicable two-step rules, VAR_SIGN, CONST_SIGN (where applicable)
- `brackets`: applicable both-sides/two-step rules, DISTRIBUTE_PARTIAL

Each distractor is recomputed independently from its rule, deduped against the
answer and each other; deterministic option ordering via the shared
`assembleMultipleChoice`.

### F-D. Difficulty, edge cases, leakage, review pack, versioning

- **Difficulty (multidimensional, with structural floor):** per-task bands —
  `one_step_add` 1–2, `one_step_mul` 1–2, `two_step` 2–3, `both_sides` 3–4,
  `brackets` 3–5. The structural task sets a **minimum floor**; large coefficients
  alone must not push a conceptually simple equation to the top band. Axes fed:
  magnitude, negatives, rationals, number of transformations, variables-both-sides,
  brackets, simplification demand, scaffolding.
- **Uniqueness:** `p ≠ r`; reject no-solution and infinitely-many-solutions; outside
  v1.0.0.
- **Answers:** integer or normalized exact-rational `{num,den}` (den ≥ 1); never
  approximate decimals.
- **`x = 0` is a valid solution** and is included; do not exclude it for distractor
  reasons — regenerate other parameters if three valid distractors can't be formed.
- **Answer leakage (revised):** coincidental numerical equality between a coefficient
  and the solution is **not** leakage. Leakage = the prompt, student-rendered
  metadata, option styling, accessibility text, or export **explicitly reveals**
  the answer. The validator checks for explicit reveal (e.g. a literal `x = …` in the
  prompt), not coincidental equality; coincidence is controlled via difficulty/quality
  rules if needed.
- **Review pack:** ~36–40 items covering all 5 tasks; free-response + MC; integer +
  exact-rational; all supported bands; positive/negative/zero solutions;
  positive/negative coefficients; fractional coefficients at suitable bands;
  variables on both sides; positive/negative bracket multipliers; **every** approved
  misconception rule; collision + deterministic-regeneration tests; full substitution
  verification. Per item show: objective, task, interaction type, canonical answer
  type, seed, parameters, difficulty axes, prompt, canonical answer, structured
  worked solution, substitution check, distractor calculations, misconception IDs,
  validation results.
- **Versioning/lifecycle:** release `gen.algebra.linear-equations v1.0.0`; fixtures
  immutable after approval; any output-affecting change ⇒ new version; items start
  `machine-validated`; no auto-approval/publication; objectives + spec become
  curriculum-approved only after the owner reviews the completed pack.

Retained gates (all): deterministic seeded generation; exact rational arithmetic;
independent Python/TypeScript implementations; byte-for-byte golden + parity
fixtures; ≥10,000-seed stability sweep; semantic distractor validation;
solution-step preservation checks; runtime schema validation; accessibility testing;
offline exports; no external runtime dependencies.

---

## 0. Curriculum placement (grounded in the uploaded SPI-Math curriculum)

This does **not** belong to IBDP. The uploaded curriculum places it in:

- **Academy:** SPI-Math · **Programme/stage:** Middle School.
- **Source chapter:** `Middle school/12-linear-equations-one-variable.html` —
  "Topic 12 / 40 · **Algebra Strand** · code **A3 · Strand A**".
- **Neighbours (source order):** previous A2 = *Simplifying, Expanding &
  Factorising* (ch 11); next A4 = *Linear Inequalities* (ch 13).
- **Stated external alignments (in the source):** IGCSE **0580 C2.5 / E2.5**;
  **Singapore Lower Secondary (Sec 1–2)**, Singapore N(T) exam style.
- **Source terminology to adopt verbatim:** "an equation is a **balance**: whatever
  you do to one side, you do to the other" (the *golden rule*); "**inverse**
  operations" (+↔−, ×↔÷); "**isolate** x"; "**expand** brackets"; "**gather/collect**
  the x-terms on one side, constants on the other"; "**divide by the coefficient**";
  "**check / verify by substituting back**". Variable symbol: **x**. Sides: **LHS /
  RHS**.
- **Source method (matches the required worked-solution structure):** expand →
  collect variables (subtract the **smaller** x-coefficient to keep the leading
  coefficient positive) → collect constants → divide by the coefficient → state →
  verify by substitution.
- **Source "Common errors" list** (used to seed the misconception model): operating
  on one side only; sign mistakes moving terms across `=`; forgetting to expand
  brackets; dividing only one term, not the whole side; skipping verification.

**v1.0.0 deliberately covers source sub-topics 1–5** (golden rule, one-step,
two-step, brackets, x on both sides). Source sub-topic 6 (clearing fractional
**denominators** by LCM) and the word-problem / inequalities / simultaneous /
quadratic material are **out of scope** (see §9), consistent with your exclusions.

> **Decision for review (D-0, ID depth).** I propose 6-segment IDs
> `SPI.MIDDLE.ALG.LINEQ.<MICRO>.01` (domain `ALG`, strand `LINEQ`). The one existing
> Middle reference in the repo is shallower (`SPI.MIDDLE.ALG.SUBSTITUTION.01`,
> 5-segment). Options: **(a)** adopt the deeper, future-proof 6-segment scheme here
> and later normalize the substitution id; **(b)** match the shallower scheme as
> `SPI.MIDDLE.ALG.LINEQ_<MICRO>.01`. Recommendation: **(a)**.

---

## 1. Curriculum objective proposal (5 micro-objectives)

Shared metadata for all five: `academy: "SPI-Math"`, `programme: "SPI-Math Middle
School"`, `stage: "middle"`, `course: "SPI-Math Middle School Mathematics"`,
`domain: "algebra"`, `strand: "linear-equations-one-variable"`,
`calculatorPolicy: "calculator-not-required"`, `allowedRepresentations:
["symbolic","numeric"]`, `notation: ["x for the unknown","LHS/RHS","a, b, c, d for
coefficients/constants"]`, `externalAlignments: [IGCSE 0580 C2.5/E2.5; Singapore
Lower Secondary]`, `reviewStatus: "proposed"`, `version: "1.0.0"`.

**Foundational prerequisites (referenced, defined when those chapters are built):**
`SPI.MIDDLE.ALG.SUBSTITUTION.01` (ch 10 — substitution, needed for the verification
step) and `SPI.MIDDLE.ALG.EXPAND_BRACKETS.01` (ch 11 — expanding a single bracket,
needed only by LINEQ.BRACKETS). These match the existing repo reference style; the
graph-check will warn "unresolved prerequisite" until those objectives are authored
(same status as the current arithmetic prereq).

| # | Objective ID | Wording | Prerequisites | Difficulty | Interaction / answer |
|---|---|---|---|---|---|
| 1 | `SPI.MIDDLE.ALG.LINEQ.ONESTEP_ADD.01` | Solve a one-step linear equation in one variable that uses addition or subtraction (`x + b = c`), by applying the inverse operation to both sides. | `SPI.MIDDLE.ALG.SUBSTITUTION.01` | 1–2 | free-response, multiple-choice · integer, exact-rational |
| 2 | `SPI.MIDDLE.ALG.LINEQ.ONESTEP_MUL.01` | Solve a one-step linear equation in one variable that uses multiplication (`a·x = c`), by dividing both sides by the coefficient. | `SPI.MIDDLE.ALG.SUBSTITUTION.01` | 1–2 | free-response, multiple-choice · integer, exact-rational |
| 3 | `SPI.MIDDLE.ALG.LINEQ.TWOSTEP.01` | Solve a two-step linear equation of the form `a·x + b = c`, undoing the operations in reverse order. | `LINEQ.ONESTEP_ADD.01`, `LINEQ.ONESTEP_MUL.01` | 2–3 | free-response, multiple-choice · integer, exact-rational |
| 4 | `SPI.MIDDLE.ALG.LINEQ.BOTHSIDES.01` | Solve a linear equation with the variable on both sides (`a·x + b = c·x + d`, `a ≠ c`), by collecting variable terms on one side and constants on the other. | `LINEQ.TWOSTEP.01` | 3–4 | free-response, multiple-choice · integer, exact-rational |
| 5 | `SPI.MIDDLE.ALG.LINEQ.BRACKETS.01` | Solve a linear equation containing one set of brackets (one level), reducing it to linear form by expanding before solving. | `LINEQ.TWOSTEP.01`, `SPI.MIDDLE.ALG.EXPAND_BRACKETS.01` | 3–5 | free-response, multiple-choice · integer, exact-rational |

`successCriteria`, `vocabulary`, and `commonMisconceptions` per objective are
specified in §7 (the misconception ids attach here after your review).

---

## 2. Generator contract (SDK `GeneratorModule`)

```
id:      "gen.algebra.linear-equations"
version: "1.0.0"
label:   "Linear equations (one variable)"
tasks: [
  { value: "one_step_add", label: "One-step (+/−)",        mc: true },
  { value: "one_step_mul", label: "One-step (×)",          mc: true },
  { value: "two_step",     label: "Two-step (ax+b=c)",     mc: true },
  { value: "both_sides",   label: "Variables on both sides", mc: true },
  { value: "brackets",     label: "One set of brackets",   mc: true },
]
generate(seed, config): Item       // deterministic (mulberry32), backward-constructed
validate(item): GenValidationResult // INDEPENDENT method (re-derives + re-normalizes)
serialize(item): string             // canonical JSON (sorted keys, no whitespace)
```

`config`: `{ task?: TaskValue, interactionType?: "free-response"|"multiple-choice" }`
(canonical), with legacy `answerType` still normalized by the SDK resolver. Auto
mode (no `task`) draws a task from the RNG. All existing SDK gates apply (schema
validation, stability harness, registry).

---

## 3. Parameter model

All coefficients/constants are **exact rationals** `{num, den}` (normalized, den ≥ 1).
A backward construction picks the solution first, then the parameters.

```
params = {
  task: TaskValue,
  x:    Rational,        // the chosen exact solution (integer or exact-rational)
  // structural coefficients (rationals), per task (see §4):
  a, b, c, d, k, p, q,   // only the subset each task uses is populated
  varSymbol: "x",
}
```

Default sampling pools (for review; tunable per difficulty):
- integer solutions in `[-12, 12] \ {edge cases}`; exact-rational solutions with
  small denominators `den ∈ {2,3,4,5}` and `|num|` bounded.
- non-zero coefficients in `[-9, 9] \ {0}`; brackets multiplier `k ∈ [-6,6]\{0,? }`.
- negatives and rationals gated by difficulty (see §8), not always on.

Backward construction guarantees the chosen `x` is the exact, unique solution; the
independent validator (§6) re-derives it forward and must agree.

---

## 4. Task matrix

Canonical reduced form after any expansion: `p·x + q = r·x + t`, unique solution
`s = (t − q)/(p − r)` provided **`p ≠ r`** (the uniqueness guarantee).

| Task | Displayed form | Construction (given solution `s`) | Uniqueness guard | MC | Answer type |
|---|---|---|---|---|---|
| `one_step_add` | `x + b = c` | pick `b`; `c = s + b` | coeff 1 ≠ 0 (always unique) | yes | integer if `s,b∈ℤ`, else exact-rational |
| `one_step_mul` | `a·x = c` | pick `a≠0`; `c = a·s` | `a ≠ 0` | yes | exact-rational when `a ∤ c` |
| `two_step` | `a·x + b = c` | pick `a≠0, b`; `c = a·s + b` | `a ≠ 0` | yes | integer/exact-rational |
| `both_sides` | `a·x + b = c·x + d` | pick `a≠c, b`; `d = (a−c)·s + b` | **`a ≠ c`** | yes | integer/exact-rational |
| `brackets` | `k(p·x + q) = c·x + d` (one bracket) | pick `k≠0, p≠0, q`; expand `kp·x + kq`; set `c≠kp`, `d = (kp−c)·s + kq` | **`kp ≠ c`** | yes | integer/exact-rational |

`brackets` keeps exactly **one** bracketed group, one level deep, optionally a
linear remainder on the other side (`c·x + d`, with `c` possibly 0 → `k(px+q)=d`).
No nested brackets, no second bracket. `one_step_add` is the `a=1,r=0` case;
`one_step_mul` is the `q=0,r=0` case — but each has its **own objective and own
task** so difficulty/coverage stay clean.

> **Decision for review (D-1, one-step multiplicative form).** I propose
> `one_step_mul` = `a·x = c` only (solve by ÷a; rational when `a∤c`). The source also
> shows `x/a = c` (solve by ×a). `x/a = c` introduces a fraction-bar term that edges
> toward the excluded "clear-denominators" sub-topic. Recommendation: **exclude
> `x/a = c` from v1.0.0**; revisit in a later version. Please confirm.

---

## 5. Canonical linear-expression representation (no CAS)

A minimal, purpose-built symbolic core — **only** what verified linear-polynomial
work needs, reusing the existing exact `Rational` (`core/exact-math/rational.ts`):

```
LinExpr = { a: Rational, b: Rational }     // represents a·x + b  (degree ≤ 1)
  add(L1,L2)   = { a: a1+a2, b: b1+b2 }
  sub(L1,L2)   = { a: a1−a2, b: b1−b2 }
  scale(k,L)   = { a: k·a, b: k·b }         // bracket expansion k·(a x + b)
  eval(L, x)   = a·x + b                    // for substitution / verification
  isLinear(L)  = true by construction (no x² term is representable)

Equation = { lhs: LinExpr, rhs: LinExpr }
  normalize(eq) → { A: a_lhs − a_rhs, B: b_lhs − b_rhs }   // A·x + B = 0
  solve(eq): require A ≠ 0 ⇒ x = (−B)/A   (exact, normalized)   else REJECT
```

Brackets are represented during construction/rendering as a `scale` of a `LinExpr`;
expansion is `scale`. There is **no general polynomial type, no parser-driven CAS,
no symbolic simplifier beyond linear add/sub/scale/eval**. This keeps the symbolic
surface tiny and fully verifiable.

---

## 6. Solver and independent-validator design (Tier A / oracle-first)

**Python oracle (reference)** and **TypeScript (production)** are written
**independently** — same mathematics, deliberately *not* the same procedure:

- **Oracle solve:** build the equation as two `LinExpr`, expand brackets via
  `scale`, `normalize` to `A·x + B = 0`, require `A ≠ 0`, return `x = −B/A`.
- **TypeScript validate (independent method):** does **not** trust the stored
  answer. It (1) reconstructs `lhs`,`rhs` from `params` symbolically, (2) confirms
  each is linear, (3) `normalize`s and asserts `A ≠ 0` (genuinely linear, unique),
  (4) computes `s = −B/A` and checks it equals the stored canonical answer, (5)
  **substitutes** the stored answer into the *original* (pre-expansion) equation and
  checks `LHS = RHS` exactly, (6) replays each solution step and checks the
  solution-set is preserved (each step maps `(A,B)` to an equivalent `(A',B')` with
  the same root), (7) re-derives every MC distractor from its misconception rule and
  checks agreement, (8) runs the universal SDK predicates (no leakage, exactly-one
  correct, distractor uniqueness, a11y, provenance/version, interaction/answer-type
  consistency). Cross-language **byte-for-byte parity** on golden + parity fixtures
  as for the sequence families.

Required independent confirmations (your list) map to checks: genuinely linear (2),
exactly one solution (3, `A≠0`), canonical satisfies original (5), normalization
yields expected linear form (3), every step preserves the solution set (6), each
distractor matches its rule (7), prompt/answer/solution/metadata agree (8 + leakage),
seeded reproducibility (stability harness + parity).

---

## 7. Misconception proposal (for curriculum review — NOT auto-approved)

Each misconception is an **independently recomputable wrong-answer rule** over the
reduced form `p·x + q = r·x + t` (true `s = (t−q)/(p−r)`). For MC, distractors are
recomputed from these rules, deduped against the answer and each other, and the item
is **regenerated** if three distinct valid distractors cannot be formed (your MC
requirements). Feedback is the student-facing diagnostic.

| ID (proposed) | Pathway | Wrong-value formula `W` | Applicability (else not used) | Collision risk | Feedback |
|---|---|---|---|---|---|
| `MISC.LINEQ.ONE_SIDE_ONLY` | Applies the inverse to one side only (e.g. divides the x-side but not the constant side) | `W = (t − q)` (stops at `p'x = …`, never divides) | `|p−r| ≠ 1` | = answer when `|p−r|=1`; gate it | "Whatever you do to one side, do to the **other** side too." |
| `MISC.LINEQ.WRONG_INVERSE` | Uses the wrong inverse (adds the constant instead of subtracting) | `W = (t + q)/(p − r)` | `q ≠ 0` | Low; distinct from answer by `2q/(p−r)` | "To undo `+q`, **subtract** q from both sides (not add)." |
| `MISC.LINEQ.VAR_SIGN` | Moves a variable term with the wrong sign | `W = (t − q)/(p + r)` | `both_sides`/`brackets`, `r ≠ 0`, `p+r ∉ {0}` | Medium vs answer when `r` small; gate `p+r ≠ p−r` | "When moving `r·x` across `=`, its sign **flips**." |
| `MISC.LINEQ.CONST_SIGN` | Changes a constant's sign with no valid operation | `W = (q − t)/(p − r) = −s` | `s ≠ 0` | Low | "Moving a constant across `=` flips its sign — apply it as a real operation." |
| `MISC.LINEQ.DISTRIBUTE_PARTIAL` | Distributes the multiplier to the first bracket term only | re-solve with `k(px+q) → kp·x + q` | `brackets`, `k ≠ 1`, `q ≠ 0` | **High vs DISTRIBUTE_NONE** | "Multiply the bracket by k across **every** term." |
| `MISC.LINEQ.DISTRIBUTE_NONE` | Fails to distribute (drops the multiplier off the constant differently) | re-solve with `k(px+q) → kp·x + kq` mis-signed, OR `k(px+q) → px + kq` | `brackets`, `k ≠ 1` | **High vs DISTRIBUTE_PARTIAL** | "Expand the bracket fully before solving." |
| `MISC.LINEQ.COMBINE_UNLIKE` | Combines unlike terms (adds an x-term to a constant) | `W` from treating `p·x + q` as `(p+q)x` or `(p+q)` | `q ≠ 0`, `p ≠ 0` | Medium | "`x`-terms and constants are **unlike** — don't combine them." |
| `MISC.LINEQ.DIVIDE_ONE_TERM` | Divides only one term, not the whole side | `W = t/(p−r) − q` (divides `t` by coeff, not `q`) | `two_step`/`both_sides`, `q ≠ 0`, `(p−r) ∤ t` cleanly | Medium vs ONE_SIDE_ONLY | "Divide the **entire** side by the coefficient, every term." |
| `MISC.LINEQ.DIVIDE_BY_CONSTANT` | Divides by the constant instead of the variable coefficient | `W = (t − q)/q` (divides by `q`, not `p−r`) | `q ≠ 0`, `q ≠ (p−r)` | Low–Medium | "Divide by the **coefficient of x**, not the constant." |
| `MISC.LINEQ.SIGNED_ARITH_SLIP` | Generic signed-number arithmetic slip | none (non-deterministic pathway) | — | **Very high (non-unique)** | "Re-check the signed arithmetic." |

> **Decision for review (D-2, MC distractor pool).** I recommend **excluding
> `SIGNED_ARITH_SLIP` from the MC distractor generator** (it is not a unique,
> documented rule — it would collide unpredictably and violate "each distractor from
> a **distinct** documented pathway"). Keep it only as a *diagnostic tag* for
> free-response feedback. Please confirm.
>
> **Decision for review (D-3, bracket-distribution pair).** `DISTRIBUTE_PARTIAL`
> and `DISTRIBUTE_NONE` are pedagogically distinct but can collide numerically. I
> recommend using **at most one** bracket-distribution distractor per item (chosen
> by seed), with the dedupe/regenerate rule as backstop. Please confirm the exact
> mis-expansion formula you want for each.
>
> **Per-task eligibility (proposed).** one-step: ONE_SIDE_ONLY, WRONG_INVERSE,
> CONST_SIGN, DIVIDE_BY_CONSTANT (mul). two-step: + DIVIDE_ONE_TERM, COMBINE_UNLIKE.
> both_sides: + VAR_SIGN. brackets: + one of DISTRIBUTE_*. This keeps ≥3 eligible,
> distinct pathways per task; the generator dedupes and regenerates parameters
> otherwise.

You asked us **not** to auto-approve these. Please review each formula,
applicability, feedback string, and the collision flags, and mark approve / revise.

---

## 8. Difficulty model (multidimensional — not coefficient size alone)

Reuses the SDK difficulty axes; `overallBand (1–5)` is derived from the weighted
axes via the existing `bandFromScore`, never hand-set. Signals feeding the axes:

| Signal | Axis it feeds |
|---|---|
| number magnitude of coefficients/constants | `numericalComplexity` |
| negative coefficients / constants present | `numericalComplexity`, `representation` |
| fractional (rational) coefficients present | `numericalComplexity`, `abstraction` |
| number of transformations (solution steps) | `reasoningSteps` |
| variables on both sides | `reasoningSteps`, `algebraicComplexity` |
| presence of brackets (expansion required) | `algebraicComplexity` |
| required simplification (collect like terms) | `algebraicComplexity` |
| degree of scaffolding (hints/step prompts) | `scaffolding` |

Coefficient size feeds only **one** axis; band reflects structure + steps + form,
satisfying "do not classify difficulty solely by coefficient size."

## 9. Edge-case policy

- **Uniqueness:** require `p ≠ r` (i.e. `a ≠ c`; for brackets `kp ≠ c`). Reject and
  resample otherwise. **No** no-solution or infinitely-many-solutions items.
- **Excluded forms:** word problems; inequalities; simultaneous; quadratic;
  absolute-value; literal/changing-the-subject; graphical; nested brackets; second
  bracket; fraction-bar terms (`(2x−1)/3`, `x/a`); approximate decimal answers.
- **Answers:** integer or exact-rational only, normalized `{num,den}`, `den ≥ 1`;
  decimals never used as the canonical answer.
- **Degenerate coefficients:** no zero coefficient where it would collapse the task
  (e.g. `a≠0`); `b`/`d` may be 0 only where the task still matches its objective.
- **Leakage:** the solution value must not appear among the prompt's integers unless
  it legitimately equals a coefficient (validator checks).
- **MC:** reject distractors equal to the answer or to each other; regenerate
  parameters when three distinct valid distractors cannot be formed; deterministic
  option ordering via the shared `assembleMultipleChoice`.

## 10. Review-pack plan

A curriculum review pack (HTML + JSON, like the sequence packs) covering:
- 5 tasks × {free-response, MC} × {integer, exact-rational} representative items.
- Each MC item shows every distractor with its **named misconception** and the
  recomputed value, for pedagogy review.
- Worked solutions printed in the required 6-step structure with the substitution
  check shown.
- A coverage table (task × difficulty band) and the objective→task→misconception
  map. ~36–40 items. Generated items begin at **`machine-validated`**; the pack is
  for your sign-off — nothing is auto-approved or published.

## 11. Versioning and approval plan

1. On approval of this proposal: author the 5 objectives (`reviewStatus: proposed`),
   the misconception registry (oracle + TS), and the oracle-first generator.
2. Prove **byte-for-byte** TS↔Python parity (golden + 300-entry parity fixture);
   **≥10,000-seed** stability sweep (0 invalid) + reproducibility; schema
   conformance; runtime schema validation at boundaries; axe-core gates; offline
   exports. Release as **v1.0.0**.
3. Produce the review pack and present for **curriculum approval**. Only after your
   approval are objectives marked `approved` and the spec `curriculum-approved`.
4. No generated item is auto-approved or published; all start at `machine-validated`.
5. Any later output-affecting change ⇒ new generator version; v1.0.0 fixtures
   preserved immutably.

---

## Approval asks (please mark each)

- **A. Curriculum placement & IDs** — Middle School / Algebra / `LINEQ`; the five
  6-segment objective IDs, wording, prerequisites, and task mapping (§0–§1). Decision
  **D-0** (ID depth).
- **B. Task matrix** (§4) and decision **D-1** (`one_step_mul` = `ax=c` only;
  exclude `x/a=c`).
- **C. Misconception rules** (§7) — each formula/applicability/feedback, plus
  decisions **D-2** (exclude `SIGNED_ARITH_SLIP` from MC) and **D-3** (one
  bracket-distribution distractor; confirm mis-expansion formulas).
- **D. Difficulty model** (§8), **edge-case policy** (§9), **review-pack plan**
  (§10), **versioning/approval plan** (§11).

On your approval (with any revisions), I will scaffold the generator through the SDK,
retaining every gate: schema validation, reproducibility, golden fixtures,
Python/TypeScript parity, ≥10,000-seed testing, runtime validation, accessibility
testing, offline export, and `machine-validated` initial lifecycle — with no
automatic curriculum approval or publication.
