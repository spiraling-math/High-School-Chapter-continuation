# Curriculum Objective Proposal — Arithmetic Sequences

Status: **PROPOSED — awaiting curriculum-authority approval.** Not finalized; the
generator (v1.0.1) still maps all tasks under the existing two objectives until
you approve this split.

## Why

In v1.0.x the four arithmetic-sequence tasks share two objectives, and the two
reverse tasks (`find_d`, `find_n_for_value`) are mapped to the nth-term objective
`SPI.IBDPAASL.SEQSER.ARITH.NTH_TERM.01`. Per your review, each distinct skill
should have its own micro-objective.

## Proposed micro-objectives

| Proposed objective ID | Task | Learner can-do statement |
| --- | --- | --- |
| `SPI.IBDPAASL.SEQSER.ARITH.NTH_TERM.01` (existing) | `nth_term` | Find the nth term of an arithmetic sequence given the first term and common difference. |
| `SPI.IBDPAASL.SEQSER.ARITH.SUM_N.01` (existing) | `sum_n` | Find the sum of the first n terms of an arithmetic sequence. |
| `SPI.IBDPAASL.SEQSER.ARITH.COMMON_DIFF.01` (new) | `find_d` | Find the common difference of an arithmetic sequence given the first term and a known later term. |
| `SPI.IBDPAASL.SEQSER.ARITH.TERM_INDEX.01` (new) | `find_n_for_value` | Find the position n of the term that has a given value in an arithmetic sequence. |

Prerequisite suggestion: both new objectives list `...NTH_TERM.01` as a
prerequisite (they invert the nth-term relationship).

## What changes on approval

1. Add the two new objective definitions to `curriculum/objectives/` (reviewStatus
   `proposed` → `approved` by you).
2. Remap `find_d → COMMON_DIFF.01` and `find_n_for_value → TERM_INDEX.01` in the
   generator's `OBJECTIVE_BY_TASK`.
3. Because the curriculum objective structure changes, bump the generator to
   **v1.1.0** (per `DECISION_LOG` decision on versioning) and regenerate golden /
   parity fixtures and the review pack.

## What does NOT change

Notation (u_1, u_n, d, S_n), exact integer answers, the
formula → substitution → evaluation solution structure, seeded reproducibility,
independent verification, machine-validated lifecycle status, Python/TypeScript
parity, and accessible rendering are all preserved.

## Decision requested

Please approve, amend, or reject the two proposed IDs and their wording. On
approval I will apply the remap as v1.1.0.
