# Approved Versions Registry

Authoritative record of curriculum-approved generators, objectives, specifications,
and golden exemplars. Approval is granted by the curriculum authority (project
owner). This registry is metadata only — it never mutates generator output or the
committed golden/parity fixtures.

## Approved generators

| Generator | Approved version | Status | Spec | Reference commit | Approved |
| --- | --- | --- | --- | --- | --- |
| `gen.sequences.arithmetic` | **1.1.0** | curriculum-approved | `GENERATOR_SPEC_arithmetic_sequences.md` | `6e547ea` | 2026-06-20 |
| `gen.sequences.geometric` | **1.1.0** | curriculum-approved | `GENERATOR_SPEC_geometric_sequences_PROPOSAL.md` | `6efcde6` | 2026-06-20 |
| `gen.sequences.geometric` | 1.0.0 | preserved (superseded by 1.1.0) | — | `af92375` | — |
| `gen.sequences.arithmetic` | 1.0.0, 1.0.1 | preserved (superseded by 1.1.0) | — | `5a962a7`, `4cbb6a1` | — |

Git tags identify the approved reference implementations:
`approved-arith-v1.1.0`, `approved-geo-v1.0.0`, `approved-geo-v1.1.0`.

## Pending curriculum review (NOT approved)

| Generator | Version | Status | Spec | Review pack |
| --- | --- | --- | --- | --- |
| `gen.algebra.linear-equations` | **1.0.1** | **implemented; awaiting curriculum review of the pack** | `GENERATOR_SPEC_linear_equations_proposal.md` (approved-with-revisions) | `docs/review/linear_equations_review_pack.md` |
| `gen.algebra.linear-equations` | 1.0.0 | preserved in git history (superseded by 1.0.1 after curriculum-review REVISE) | — | — |

v1.0.1 applied the owner's curriculum-review REVISE (see `DECISION_LOG.md` #29):
interactionType-first terminology, placeholder-free student feedback, the
positive-coefficient solution strategy, integer-only `ONESTEP_ADD`, and a
recalibrated difficulty model spreading brackets across bands 3–5. The five
`SPI.MIDDLE.ALG.LINEQ.*` objectives are `reviewStatus: proposed`. The generator, its
objectives, and its spec become curriculum-approved **only after the owner reviews
the completed review pack**. Items begin at `machine-validated`; nothing is
auto-approved or published. The linear fixtures
(`oracle/golden/linear_equations.{golden,parity}.json`) become immutable once the
version is approved; arithmetic and geometric outputs are unchanged.

## Approved curriculum objectives

| Objective ID | Generator task | Version | Status |
| --- | --- | --- | --- |
| `SPI.IBDPAASL.SEQSER.ARITH.NTH_TERM.01` | arithmetic nth_term | 1.1.0 | approved |
| `SPI.IBDPAASL.SEQSER.ARITH.SUM_N.01` | arithmetic sum_n | 1.1.0 | approved |
| `SPI.IBDPAASL.SEQSER.ARITH.COMMON_DIFF.01` | arithmetic find_d | 1.0.0 | approved |
| `SPI.IBDPAASL.SEQSER.ARITH.TERM_INDEX.01` | arithmetic find_n | 1.0.0 | approved |
| `SPI.IBDPAASL.SEQSER.GEO.NTH_TERM.01` | geometric nth_term | 1.0.0 | approved |
| `SPI.IBDPAASL.SEQSER.GEO.SUM_N.01` | geometric sum_n | 1.0.0 | approved |
| `SPI.IBDPAASL.SEQSER.GEO.COMMON_RATIO.01` | geometric find_r | 1.0.0 | approved |
| `SPI.IBDPAASL.SEQSER.GEO.TERM_INDEX.01` | geometric find_n | 1.0.0 | approved |
| `SPI.IBDPAASL.SEQSER.GEO.SUM_INFINITE.01` | geometric sum_infinite | 1.0.0 | approved |

## Golden exemplars (curriculum-reviewed and approved)

The representative reviewed examples are approved as **golden exemplars**. The
exemplar items themselves are preserved byte-for-byte in the golden fixtures (not
re-serialized), so their stored `lifecycle.state` remains `generated`; their
approved-exemplar status is recorded here.

| Generator | Golden fixture | Approved exemplar seeds |
| --- | --- | --- |
| `gen.sequences.arithmetic` 1.1.0 | `oracle/golden/arithmetic_sequences.golden.json` | 1, 42, 123456789, 2147483647 |
| `gen.sequences.geometric` 1.1.0 | `oracle/golden/geometric_sequences.golden.json` | 1, 42, 123456789, 2147483647 |
| Review-pack exemplars | `docs/review/arithmetic_sequences_review_pack.md`, `docs/review/geometric_sequences_review_pack.md` | all listed items |

## Lifecycle policy (unchanged)

- **Newly generated items always begin at `machine-validated`.** Approval of a
  generator version and of the golden exemplars does **not** auto-approve or
  publish future generated items.
- Advancing any individual item beyond `machine-validated` remains a per-item
  curriculum-authority decision.

## Preservation guarantees

The following are preserved unchanged and are protected by the test gate:

- arithmetic v1.0.0 / v1.0.1 / v1.1.0 and geometric v1.0.0 / v1.1.0 output;
- all golden and parity fixtures;
- the Python oracle and the TypeScript implementation (kept byte-for-byte in
  parity);
- exact-rational normalization (`{num, den}`, den ≥ 1);
- independent iterative validation;
- the 10,000-seed-sweep testing gate (zero invalid items required).
