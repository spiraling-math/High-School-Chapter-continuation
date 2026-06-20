# Misconception Model

Status: Phase 1 draft. Last updated: 2026-06-20.

Misconceptions are first-class data. They are the source of truth for multiple-choice distractors and for diagnostic feedback, so that wrong answers are **mathematically meaningful** rather than arbitrary nearby values.

## 1. What a misconception record holds

Defined by `misconception.schema.json`. Key fields:

- `misconceptionId` — stable id, `MISC.<DOMAIN>.<NAME>`.
- `domain`, `objectiveRelationships` — where it lives and where it appears.
- `description`, `observableError`, `typicalIncorrectMethod` — the human-readable substance.
- `distractorRule` — the machine-usable transformation (`summary`, optional `expression`) a generator applies to the correct parameters to produce the wrong value.
- `validRange` — levels/stages where the misconception is age-appropriate (so feedback is not shown out of context).
- `feedback`, `remediationHint` — constructive student-facing guidance.
- `reviewStatus` — `draft → proposed → approved → rejected → retired`; only the curriculum authority approves.

## 2. From misconception to distractor

```
correct params ──► distractorRule (from misconception) ──► wrong value ──► distractor{value, misconceptionId, rationale}
```

Rules enforced at generation/validation time (`VALIDATION_STANDARD.md`):
- Each distractor references a misconception where one applies.
- No distractor equals the correct answer under any accepted equivalent form. If a rule coincidentally produces the correct value for a seed, the generator substitutes an alternative rule, or the item fails validation and the seed is logged.
- Distractors are unique.

This makes every option diagnostic: choosing distractor D implies the student likely holds misconception `D.misconceptionId`, and `feedback` can be surfaced.

## 3. Library organization

- Misconceptions are grouped by `domain`. Cross-domain misconceptions (e.g. "treats the equals sign as 'compute'") carry the most relevant primary domain and link others via `relatedMisconceptions`.
- The library grows alongside generators: when a generator is specified, its candidate distractor strategies are recorded as misconception entries first, then referenced by the generator descriptor.

## 4. Seed examples (sequences and series)

| ID | Title | Typical incorrect method |
| --- | --- | --- |
| `MISC.SEQ.OFFBYONE_TERMINDEX` | Off-by-one in term index | `a1 + n*d` instead of `a1 + (n-1)*d` |
| `MISC.SEQ.SIGN_DIFFERENCE` | Sign error on common difference | `a1 - (n-1)*d` |
| `MISC.SEQ.FORGOT_MULTIPLY` | Forgot to multiply by d | `a1 + (n-1)` |
| `MISC.SERIES.FORGOT_HALF` | Omitted the ½ in the sum | `n*(2a1+(n-1)d)` (no ÷2) |
| `MISC.SERIES.CONSTANT_TERMS` | Treats all terms as equal to the last | `n * u_n` |

These are authored as full records in the misconception library and referenced by `gen.sequences.arithmetic`.

## 5. Feedback rendering

- Student Preview (later phase) surfaces `feedback` when a student selects a distractor or submits a recognizable wrong value.
- The Quality Console can report, per generator, which misconceptions are exercised and how often, to ensure coverage and avoid over-reliance on a single distractor type.

## 6. Governance

- New misconceptions start `draft`/`proposed`; only the curriculum authority approves them.
- A misconception used by a published generator is effectively part of that generator's contract: changing its `distractorRule` meaning requires a misconception version bump and a generator version bump.
- Retired misconceptions remain in the library (for historical items) but are not used by new items.
