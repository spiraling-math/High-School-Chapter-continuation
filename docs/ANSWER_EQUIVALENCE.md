# Answer Equivalence

Status: Phase 1 draft. Last updated: 2026-06-20.

This document defines how the platform decides whether a response is correct. Answer checking is **type-aware** and uses **exact arithmetic** wherever possible. It is shared by validation (distractor checks, no-leakage) and by any future student answer-checking.

## 1. Checker interface

```
check(response, answer) → { correct: boolean, equivalentForm?: string, reason?: string }
```

`answer` is the item's `answer` object (`type`, `canonical`, `equivalentForms`, `tolerance`, `units`, `rounding`). The checker dispatches on `answer.type`.

## 2. Equivalence by answer type

| Type | Equivalence rule |
| --- | --- |
| `integer` | Exact integer equality. |
| `fraction` / `mixed-number` | Compare as reduced rationals: `a/b == c/d` iff `a*d == b*c` (exact). `1/2`, `2/4`, `0.5` (if also accepted) are equal. |
| `decimal` | If exact: compare as rationals. If approximate: apply `tolerance` (absolute/relative/decimalPlaces/significantFigures). Never float `==`. |
| `exact-surd` | Normalize to canonical surd form (rationalized, simplified radicand) and compare; e.g. `2√2 == √8`. |
| `exact-trig` | Compare canonical exact values (e.g. `cos 30° == √3/2`). |
| `algebraic-expression` | Structural/CAS equivalence: expand & normalize, or evaluate at multiple random (seeded) sample points over the domain and require agreement, plus symbolic normalization. |
| `equation` | Same solution set (compare normalized form / solution set). |
| `inequality` | Same solution set including boundary/openness. |
| `interval` | Same endpoints and inclusivity. |
| `set` | Set equality (unordered, deduplicated). |
| `ordered-pair` / `coordinate` | Componentwise exact equality. |
| `sequence` | Elementwise equality, order-sensitive. |
| `vector` / `matrix` | Same dimensions and elementwise equality (exact). |
| `complex-number` | Real and imaginary parts equal (exact). |
| `multiple-choice` | Selected option's `correct` flag. |
| `multiple-select` | Selected set equals the correct set. |
| `matching` / `ordering` / `classification` | Exact correspondence/order/partition. |
| `short-explanation` / `extended-response` / `proof` | Not auto-equivalence-checked; rubric-scored (out of scope for exact checking). |

## 3. Exact-first principle

- Internal verification and distractor checks use exact representations (`Fraction`, integer, symbolic). The vertical-slice oracle uses Python `fractions.Fraction`; the TS core uses an exact rational type with the same semantics.
- Floating point is used **only** for intrinsically approximate answers, and then only with an explicit tolerance. A missing tolerance on an approximate answer is a validation `fail`.

## 4. Accepted equivalent forms

- `answer.equivalentForms` lists additional fully-correct forms (e.g. an unsimplified-but-correct fraction, an alternate exact surd form). The checker accepts the canonical form and every listed equivalent.
- For `algebraic-expression`, equivalence is computed, not enumerated, so `equivalentForms` is usually unnecessary; it is reserved for cases where the curriculum authority wants to pin specific accepted forms.

## 5. Tolerance and rounding

- `tolerance.absolute` / `relative`: numeric closeness.
- `tolerance.decimalPlaces` / `significantFigures`: the response must match when both are rounded per the rule. `answer.rounding` states the instruction shown to students (e.g. "to 3 significant figures") and is enforced consistently.
- Rounding is applied **once**, to the final comparison, to avoid compounding.

## 6. Units

- When `answer.units` is set, a response with wrong or missing units is not fully correct (configurable: hard-fail vs. accuracy-mark deduction via the mark scheme).
- Unit normalization (e.g. `m/s` vs `m s^-1`) is handled by a canonical unit form.

## 7. Use in validation

The checker powers three validation checks:
- `distractor-not-answer`: every distractor is checked against the answer; equal ⇒ fail.
- `answer-solution-agree`: the final solution result is checked against `answer.canonical`.
- `answer-independent-agreement`: the independent method's result is checked against `answer.canonical`.

All three use the same type-aware exact checker, guaranteeing consistent equivalence semantics across the platform.

## 8. Versioning

The checker is versioned. Adding/altering equivalence rules bumps the version; items validated under an older checker may be re-checked when the version advances.
