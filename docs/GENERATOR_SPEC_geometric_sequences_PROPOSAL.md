# Generator Proposal — Geometric Sequences (next family)

Status: **APPROVED and IMPLEMENTED. Current release: `gen.sequences.geometric`
v1.1.0** (v1.0.0 preserved). This document is retained as the design record.

**v1.1.0 curriculum-review corrections:** interactionType separated from
answer.type (`integer`/`exact-rational`, normalized `{num,den}` canonical with an
`accepts` policy and an exact-rational checker); geometric-**series** wording for
sums; step-by-step `find_n` exponent reasoning; and independent validators for
answer-type/value consistency, find_r real-solution-set uniqueness, and
term-index uniqueness. See `DECISION_LOG.md` #23.

**As-built scope decisions** (within the approved proposal):
- Multiple-choice is offered for `nth_term` and `sum_n`; `find_r`,
  `find_n_for_value`, and `sum_infinite` are **free-response** in v1.0.0. The
  proposed sum-to-infinity distractor misconceptions are documented in the
  library but are reserved for a future MC variant of `sum_infinite`.
- Answers are **exact rationals** (new `core/exact-math/rational.ts`, mirroring
  Python `Fraction`). `find_r` uses term positions k ∈ {2, 4} so the recovered
  ratio is unique (the (k−1)th real root). Parameters are curated and
  deterministically regenerated to keep magnitudes and denominators human-scale.
- Verified: 10,000-seed sweep 0 invalid; byte-for-byte Python/TS parity (golden +
  300-entry fixture); curriculum-review pack `docs/review/geometric_sequences_review_pack.md`.

This document presents the proposed objectives, task coverage, difficulty model,
misconceptions, generator contract, and review plan for the **second** generator
family. No code will be written until you approve (or amend) the items below.
The design deliberately mirrors the approved arithmetic-sequences generator so
the same deterministic, oracle-verified, parity-checked pipeline applies.

## 1. Scope and source

IBDP AA SL Chapter 1 (Oxford ToC 1.2 Arithmetic and geometric sequences, 1.3
Arithmetic and geometric series). Covers finite geometric sequences/series and,
if approved, the **sum to infinity** of a convergent geometric series (an AA SL
topic). Reference-only Oxford notes used for skill structure, not verbatim.

## 2. Proposed objectives (for approval)

| Proposed objective ID | Task | Proposed wording | Prerequisite |
| --- | --- | --- | --- |
| `SPI.IBDPAASL.SEQSER.GEO.NTH_TERM.01` | `nth_term` | Determine the nth term of a geometric sequence given the first term, common ratio, and term position. | `…ARITH.NTH_TERM.01` |
| `SPI.IBDPAASL.SEQSER.GEO.SUM_N.01` | `sum_n` | Determine the sum of the first n terms of a geometric sequence. | `…GEO.NTH_TERM.01` |
| `SPI.IBDPAASL.SEQSER.GEO.COMMON_RATIO.01` | `find_r` | Determine the common ratio of a geometric sequence given the first term and another term's value and position. | `…GEO.NTH_TERM.01` |
| `SPI.IBDPAASL.SEQSER.GEO.TERM_INDEX.01` | `find_n_for_value` | Determine the position n of a specified term value given the first term and common ratio. | `…GEO.NTH_TERM.01` |
| `SPI.IBDPAASL.SEQSER.GEO.SUM_INFINITE.01` *(optional)* | `sum_infinite` | Determine the sum to infinity of a convergent geometric series (|r| < 1). | `…GEO.SUM_N.01` |

**Decision requested:** approve/amend the IDs, wording, prerequisites, and
whether `SUM_INFINITE.01` is in the first release or deferred.

## 3. Task coverage (proposed)

| Task | Answer type(s) | Notes |
| --- | --- | --- |
| `nth_term` | integer or exact fraction | `u_n = u_1 · r^(n-1)`. Integer when r is an integer; exact rational when r is a simple fraction. |
| `sum_n` | integer or exact fraction | `S_n = u_1 (r^n − 1)/(r − 1)`, r ≠ 1. |
| `find_r` | integer or exact fraction | Reverse; constructed so r is recoverable exactly. |
| `find_n_for_value` | integer | Reverse; n recovered exactly (value on the geometric grid). |
| `sum_infinite` *(optional)* | exact fraction | `S_∞ = u_1/(1 − r)`, requires |r| < 1, so r is a proper fraction. |

**Key design change vs arithmetic:** geometric answers are frequently **exact
rationals**, not integers. This requires an **exact rational type** in the TS
core (the Python oracle already uses `fractions.Fraction`). Floating point is
never used for these answers; answer-equivalence uses the rational rules already
specified in `ANSWER_EQUIVALENCE.md`.

**Parameter strategy (construct-backwards, exact):**
- `u_1`: small nonzero integer.
- `r`: drawn from a curated exact set — small integers (±2, ±3, …) for
  integer-valued items, and simple fractions (±1/2, ±1/3, ±2/3, …) for
  fractional and sum-to-infinity items (|r| < 1).
- `n`: small range so `r^(n-1)` stays exact and human-scale.
- For `find_n_for_value`, the target value is placed on the geometric grid so n
  is an exact positive integer (uniqueness holds because |r| ≠ 1).

## 4. Difficulty model (reuses the 16-axis platform vector)

Geometric-specific control → axis mapping:

| Control | Axis effect |
| --- | --- |
| r integer vs proper fraction | ↑ `numericalComplexity`, ↑ `exactVsApproximate` (fractions) |
| r negative (alternating signs) | ↑ `numericalComplexity`, ↑ `reasoningSteps` |
| task nth_term (1 step) → sum_n (2) → reverse (3) → sum_infinite (interpret convergence) | ↑ `reasoningSteps`, ↑ `abstraction` |
| sum_infinite (convergence condition |r|<1) | ↑ `abstraction`, ↑ `interpretationDemand` |
| larger n / larger r^(n-1) | ↑ `numericalComplexity` |

`overallBand` (1–5) derived via the shared band function (`DIFFICULTY_MODEL.md`),
as for arithmetic. Expected: integer-ratio nth_term → band 1–2; fractional sum →
3; sum_infinite → 3–4.

## 5. Proposed misconceptions (distinct, formula-backed)

Each becomes a registry entry (`misconceptions.py`/`.ts`) with formula,
rationale, and feedback, exactly like the arithmetic family. Distinct per item;
parameters regenerate if three distinct ones aren't available.

| Proposed ID | Formula (incorrect) | Description |
| --- | --- | --- |
| `MISC.GEO.OFFBYONE_TERMINDEX` | `u_1 · r^n` | Uses r^n instead of r^(n-1) (off-by-one in the exponent). |
| `MISC.GEO.RATIO_AS_DIFFERENCE` | `u_1 + (n-1)·r` | Treats the common ratio like an arithmetic common difference (adds instead of multiplies). |
| `MISC.GEO.FORGOT_FIRST_TERM` | `r^(n-1)` | Computes r^(n-1) but omits the factor u_1. |
| `MISC.GEO.SIGN_RATIO` | `u_1 · |r|^(n-1)` | Drops the sign of a negative ratio (loses term-to-term alternation). |
| `MISC.SERIES.GEO.SUM_INVERTED_SIGN` | `u_1 (r^n − 1)/(r − 1)` evaluated with the wrong sign convention `u_1 (1 − r^n)/(r − 1)` | Mismatched numerator/denominator sign in the sum formula. |
| `MISC.SERIES.GEO.SUM_FORGOT_RATIO` | `u_1 · n` | Treats the geometric sum like n equal terms (ignores r). |
| `MISC.SERIES.GEO.INFINITE_USES_FINITE` *(if sum_infinite)* | `u_1 (1 − r^n)/(1 − r)` for some n | Applies the finite-sum formula instead of `u_1/(1 − r)`; or ignores the |r| < 1 condition. |

**Decision requested:** approve/amend this misconception set.

## 6. Generator contract (same as the platform standard)

`describe / generate(seed, config) / solve / validate / generateDistractors /
generateSolution / render / serialize`, per `GENERATOR_STANDARD.md`.

- **Canonical method:** closed forms `u_n = u_1 r^(n-1)`, `S_n = u_1(r^n−1)/(r−1)`,
  `S_∞ = u_1/(1−r)` — computed with exact rationals.
- **Independent verification (validate):** iterative **multiplication**
  construction (build terms `u_1, u_1·r, u_1·r², …`) and literal summation,
  compared to the closed forms; for `sum_infinite`, verify `S_∞ − S_n → 0` and
  that `S_∞·(1−r) = u_1` exactly. This is independent of the generation method,
  as required.
- **Distractors:** from the registry, distinct, semantic-agreement validated
  (recompute each from its formula), with deterministic parameter regeneration.
- **Solution structure:** formula → substitution → evaluation (preserved).
- **Notation:** `u_1`, `u_n`, `r`, `S_n`, `S_∞`. **Calculator policy:**
  `calculator-not-required` for exact items.
- **Reproducibility / parity:** mulberry32 seed; Python oracle first, then
  byte-for-byte TypeScript parity (golden + 300-entry fixture).

## 7. Review plan (the same gates that arithmetic passed)

1. Build the Python oracle (exact `Fraction` arithmetic), with unit, property,
   reproducibility, edge-case, invalid-parameter, distractor semantic-agreement,
   and a **10,000-seed sweep with zero invalid items**; record any failing seeds.
2. Generate golden vectors + a 300-entry cross-language parity fixture.
3. Add the exact rational type to the TS core; port the generator and validator;
   prove **byte-for-byte parity** with the oracle.
4. Produce a **curriculum-review pack**: ≥3 examples per (task, answer type),
   covering integer and fractional ratios, positive and negative ratios,
   |r| < 1 and |r| > 1, small and large n, and every misconception rule, with
   full reproducibility metadata and distractor calculations.
5. Integrate into Generator Studio (task/answer-type already generic).
6. **Curriculum review** of the pack → approval → release (curriculum-approved).

Generated items will begin at `machine-validated`; items are never auto-published.

## 8. Open decisions for the owner (please confirm before implementation)

1. Approve/amend the **objective IDs and wording** (§2), including whether
   `SUM_INFINITE.01` is in the first release.
2. Approve the **task coverage and answer types** (§3), in particular admitting
   **exact fractional answers** (and adding an exact rational type to the TS core).
3. Approve the **misconception set** (§5).
4. Confirm **calculator policy** (`calculator-not-required` for exact items) and
   that answers stay **exact** (no approximate/rounded answers in the first
   release).
5. Confirm scope boundary: geometric **sequences and finite series** (+ optional
   sum-to-infinity) only; nothing beyond AA SL Chapter 1 in this family.

**No implementation will begin until you approve or amend the above.**
