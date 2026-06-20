# Validation Standard

Status: Phase 1 draft. Last updated: 2026-06-20.

Every generated item must pass automated validation before it can enter the bank. Validation is **independent** of generation (Principle 4) and uses **exact arithmetic** wherever possible; floating-point comparisons require explicit tolerances.

## 1. Validation gate

```
item ──► validate(item) ──► ValidationResult{status, checks[]}
                              status = pass  → eligible for bank
                              status = fail  → rejected, seed logged
                              status = warn  → eligible, flagged for review
```

An item with any `fail` check has `status = fail` and is rejected. The result is stored on `item.lifecycle.validation`.

## 2. General checks (all generators)

| Check | Description | Severity |
| --- | --- | --- |
| `schema-valid` | Item validates against `question-item.schema.json`. | fail |
| `reproducible` | Re-running `generate(seed, config)` yields byte-identical serialization. | fail |
| `params-in-domain` | All params within `parameterSpec` (ranges, nonZero, enums). | fail |
| `defined-domain` | No division by zero, valid dimensions, defined functions over the used domain. | fail |
| `answer-independent-agreement` | Independent method reproduces `answer.canonical` exactly. | fail |
| `unique-correct` | Exactly one correct response (for selected-response). | fail |
| `distractors-unique` | No two distractors equal. | fail |
| `distractor-not-answer` | No distractor equals the answer under any accepted equivalent form. | fail |
| `distractor-misconception` | Each distractor references a misconception where one exists. | warn |
| `answer-solution-agree` | Final solution step result equals `answer.canonical`. | fail |
| `data-diagram-agree` | Any diagram/graph is consistent with `params`/data. | fail |
| `prompt-answertype-agree` | The prompt's command matches the declared answer type. | fail |
| `no-answer-leakage` | The prompt does not contain the answer value/expression. | fail |
| `notation-wellformed` | All LaTeX parses (KaTeX) without error. | fail |
| `html-valid` | Rendered HTML is well-formed and safe. | fail |
| `a11y-fields-present` | Required accessibility fields present (`spokenMath` when notation; alt text when visual). | fail |
| `non-visual-info` | No information is available only visually. | fail |
| `duplicate-structure` | Structural-duplicate rate within the generator's allowed threshold. | warn |
| `rounding-valid` | Rounding instructions are coherent with the answer type. | fail |
| `units-valid` | Units are present and consistent where required. | fail |

## 3. Independent verification (the core check)

`answer-independent-agreement` is the heart of validation. The verification method must be **different** from the generation/solve method:

| Generation/solve method | Independent verification method |
| --- | --- |
| Closed-form nth term `a1+(n-1)d` | Iterative term-by-term construction. |
| Closed-form series sum | Literal summation of constructed terms. |
| Algebraic answer chosen first | Substitute answer into the original equation. |
| Proposed antiderivative | Differentiate and compare to the integrand. |
| Matrix solution constructed | Multiply through and check `A x = b` / `A v = λ v`. |
| Probability via formula | Enumerate the small sample space. |
| Statistic via formula | Recompute from the raw seeded dataset. |
| Geometry from chosen measures | Recompute from coordinates/constraints. |
| Decision-math result | Re-run the algorithm (shortest path, MST, flow, schedule). |

## 4. Exact vs. approximate arithmetic

- Use **exact** arithmetic (integers, `Fraction`/rationals, symbolic where feasible) for all internal verification. The vertical-slice oracle uses Python `fractions.Fraction`; the TS core uses an exact rational type.
- Only when an answer is intrinsically approximate (e.g. a rounded decimal) does the checker use a tolerance, and the tolerance must be explicit (`absolute`, `relative`, `decimalPlaces`, or `significantFigures`). Never compare floats with `==`.

## 5. Domain-specific checks

Generators add checks appropriate to their domain. Examples:

- **Sequences/series:** common difference/ratio consistent; n ≥ 1; sum equals summed terms.
- **Algebra:** answer satisfies the equation; discriminant sign matches the intended root count.
- **Calculus:** derivative/antiderivative relationships hold symbolically.
- **Probability:** probabilities in [0,1]; total sample-space probability = 1.
- **Statistics:** recomputed statistics match; dataset has the intended property.
- **Geometry:** triangle inequality / valid configuration; recomputed lengths/angles match.
- **Graph/decision:** graph well-formed; algorithm output matches claimed result.

## 6. High-volume seed validation

- Before a generator is "stable", run a sweep of **≥ 10,000 seeds** (when computationally reasonable). **Zero** items may be invalid.
- Every failing seed is written to a failing-seeds artifact: `{generatorId, generatorVersion, seed, config, failingChecks[]}` so it can be reproduced exactly. See `TESTING_STRATEGY.md` for the artifact format.

## 7. Validator versioning

The validator records `validatorVersion` on each result. Changes to checks bump the version. Re-validation of stored items is triggered when the validator version advances.

## 8. Output contract

`validate(item)` returns a `validationResult` (see `question-item.schema.json#/$defs/validationResult`): `status`, `validatorVersion`, `checkedAt`, and a `checks[]` array of `{name, result, detail}`. The platform never marks an item `machine-validated` without a stored `pass` result.

## 9. Relationship to review

Machine validation is necessary but not sufficient for publication. After `machine-validated`, items still require `mathematics-reviewed` and `curriculum-reviewed` human steps before `approved`/`published`. Machine validation guarantees mathematical/structural correctness; human review guarantees pedagogical and curriculum fit.
