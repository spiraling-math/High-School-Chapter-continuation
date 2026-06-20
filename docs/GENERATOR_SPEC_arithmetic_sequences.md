# Generator Specification — Arithmetic Sequences

Generator: `gen.sequences.arithmetic` · Version: `1.0.0` · Status: in-development
First vertical slice (Decision #7). Last updated: 2026-06-20.

This is the design specification for the first production generator. It is implemented first as the Python oracle (`oracle/spi_oracle/sequences.py`) and will be mirrored in TypeScript. It conforms to `GENERATOR_STANDARD.md`, `VALIDATION_STANDARD.md`, `DIFFICULTY_MODEL.md`, and the JSON schemas.

## 1. Curriculum objectives

| Objective ID | Wording |
| --- | --- |
| `SPI.IBDPAASL.SEQSER.ARITH.NTH_TERM.01` | Find the nth term of an arithmetic sequence given the first term and common difference. |
| `SPI.IBDPAASL.SEQSER.ARITH.SUM_N.01` | Find the sum of the first n terms of an arithmetic sequence. |

Source evidence: IBDP AA SL Chapter 1 (Oxford ToC 1.2 Arithmetic and geometric sequences, 1.3 Arithmetic and geometric series); HS sources `hs-A9-sequences-and-series.html`. Reference-only Oxford teacher notes used for skill structure, not verbatim content.

## 2. Tasks (sub-skills)

| Task | Question | Answer type | Objective |
| --- | --- | --- | --- |
| `nth_term` | Given `a1`, `d`, find the `n`th term. | integer | NTH_TERM.01 |
| `sum_n` | Given `a1`, `d`, find `S_n` (sum of first `n` terms). | integer | SUM_N.01 |
| `find_d` | Given `a1`, the `n`th term, and `n`, find `d`. | integer | NTH_TERM.01 (reverse) |
| `find_n_for_value` | Given `a1`, `d`, and a term value, find which term it is (`n`). | integer | NTH_TERM.01 (reverse) |

All tasks produce integer answers by construction (parameters are chosen so reverse tasks divide exactly), keeping the first slice exact and unambiguous. Fractional/real extensions are deferred to a later version.

## 3. Parameters and constraints

| Param | Type | Range | Notes |
| --- | --- | --- | --- |
| `task` | enum | nth_term \| sum_n \| find_d \| find_n_for_value | Selected by config or uniformly from allowed set. |
| `a1` | integer | −20..20 | First term. |
| `d` | integer | −12..12, ≠ 0 | Common difference (nonzero). |
| `n` | integer | 3..40 | Term index / number of terms. |

Construction guarantees:
- `find_d`: `d = (value − a1)/(n−1)` is integer because `value` is computed as `a1 + (n−1)d` from an integer `d`.
- `find_n_for_value`: `n = (value − a1)/d + 1` is a positive integer ≥ 3 by construction.

## 4. Canonical mathematics (solve)

- nth term: `u_n = a1 + (n − 1)·d`
- sum: `S_n = n/2 · (2·a1 + (n − 1)·d)` (computed with exact rationals; integer for integer inputs)
- find_d: `d = (u_n − a1)/(n − 1)`
- find_n_for_value: `n = (value − a1)/d + 1`

## 5. Independent verification (validate)

The independent method is **iterative construction**, which must be distinct from the closed forms above:

- Build terms `t_1=a1`, `t_{k}=t_{k-1}+d` up to `n`.
- `nth_term`: assert `t_n == solve.nth_term`.
- `sum_n`: assert `sum(t_1..t_n) == solve.sum_n`.
- `find_d`: rebuild with the found `d` and assert the `n`th term equals the given value.
- `find_n_for_value`: rebuild and assert `t_n == value` and `n` is the **first** index achieving it (uniqueness, since `d ≠ 0`).

Exact integer/`Fraction` arithmetic throughout; no floats.

## 6. Distractors (multiple-choice mode) — each maps to a misconception

| Task | Distractor | Misconception |
| --- | --- | --- |
| nth_term | `a1 + n·d` | `MISC.SEQ.OFFBYONE_TERMINDEX` |
| nth_term | `a1 − (n−1)·d` | `MISC.SEQ.SIGN_DIFFERENCE` |
| nth_term | `a1 + (n−1)` | `MISC.SEQ.FORGOT_MULTIPLY` |
| sum_n | `n·(2·a1+(n−1)·d)` (no ÷2) | `MISC.SERIES.FORGOT_HALF` |
| sum_n | `n · u_n` (all terms = last) | `MISC.SERIES.CONSTANT_TERMS` |
| sum_n | `(n/2)(a1 + (a1+n·d))` (off-by-one last term) | `MISC.SEQ.OFFBYONE_TERMINDEX` |

Distractor rules enforced: unique; none equals the correct answer (if a collision occurs for a seed, drop/replace that distractor; require ≥ 3 valid distractors or fail). Reverse tasks reuse analogous sign/▁off-by-one rules.

## 7. Difficulty axis mapping

| Control | Axis | Effect |
| --- | --- | --- |
| `|a1|, |d|, n` magnitude | `numericalComplexity` | ↑ with magnitude |
| `d < 0` | `numericalComplexity`, `reasoningSteps` | small ↑ |
| `task = nth_term` | `reasoningSteps` | low (~1 step) |
| `task = sum_n` | `reasoningSteps` | medium (~2 steps) |
| `task ∈ {find_d, find_n_for_value}` | `reasoningSteps`, `abstraction` | ↑ (reverse reasoning) |

`overallBand` from the shared band function (`DIFFICULTY_MODEL.md`). Expected: forward small-number `nth_term` → band 1; `sum_n` → band 2; negative-`d` reverse tasks → band 3.

## 8. Solution structure

Structured `solution.steps[]`:
1. State the formula (`u_n = u_1 + (n−1)d` or `S_n = n/2(2u_1+(n−1)d)`), `ruleOrTheorem`.
2. Substitute the values (`intermediateResult` in LaTeX).
3. Evaluate to the final result; final step result must equal `answer.canonical` (checked by `answer-solution-agree`).

## 9. Rendering and accessibility

- Notation via KaTeX from LaTeX source. Prompt must not contain the answer (no-leakage check).
- `accessibility.spokenMath` required (plain-English reading). Multiple-choice options labelled A–D; correctness never conveyed by color alone.

## 10. Validation checks (this generator)

All general checks (`VALIDATION_STANDARD.md` §2) plus:
- `params-in-domain`: ranges and `d ≠ 0`.
- `arith-iterative-agreement`: iterative construction agrees with closed form (the independent check).
- `reverse-exact`: reverse tasks produce integer `d`/`n` by construction.
- `unique-n`: `find_n_for_value` has a unique solution (guaranteed by `d ≠ 0`).

## 11. Test plan

- Unit: one fixed example per task with known answer.
- Property (≥10,000 seeds): for every seed, item passes all validation checks; answer equals iterative result; exactly one correct option; no distractor equals the answer; params in domain.
- Reproducibility: same seed → identical serialized item.
- Edge cases: extreme ranges (`a1=±20`, `d=±12`, `n=3`, `n=40`), `d<0`.
- Invalid parameters: `d=0`, `n<3`, out-of-range → generator/validator rejects.
- Golden seeds: `1, 42, 123456789, 2147483647` checked into version control; TS output must match the oracle's golden JSON vectors.

## 12. Versioning

`1.0.0` initial. Any change to draw order, formulas-as-serialized, distractor rules, or solution data bumps the version and regenerates golden vectors.
