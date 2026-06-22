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
| `gen.algebra.linear-equations` | **1.0.1** | curriculum-approved | `GENERATOR_SPEC_linear_equations_proposal.md` | `0ebcb96` | 2026-06-21 |
| `gen.sequences.geometric` | 1.0.0 | preserved (superseded by 1.1.0) | — | `af92375` | — |
| `gen.sequences.arithmetic` | 1.0.0, 1.0.1 | preserved (superseded by 1.1.0) | — | `5a962a7`, `4cbb6a1` | — |
| `gen.algebra.linear-equations` | 1.0.0 | preserved (superseded by 1.0.1) | — | `1cfc76c` | — |

Git tags identify the approved reference implementations:
`approved-arith-v1.1.0`, `approved-geo-v1.0.0`, `approved-geo-v1.1.0`,
`approved-linear-v1.0.1`.

`gen.algebra.linear-equations` v1.0.1 was curriculum-approved on 2026-06-21 after the
owner reviewed `docs/review/linear_equations_review_pack.md` (`DECISION_LOG.md` #30).
Approved scope: curriculum placement (SPI-Math Middle School → Algebra), objective
wording + task mapping, integer/exact-rational handling, free-response + MC
interactions, difficulty bands, worked-solution structures, substitution
verification, misconception rules + distractor formulas + feedback, deterministic
collision regeneration, and the v1.0.1 edge-case policy/exclusions.
`SPI.MIDDLE.ALG.LINEQ.ONESTEP_ADD.01` is recorded **integer-only** in v1.0.1
(`answerTypes: ["integer", "multiple-choice"]`) unless rational constants are
explicitly supported in a later version.

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
| `SPI.MIDDLE.ALG.LINEQ.ONESTEP_ADD.01` | linear one_step_add (integer-only) | 1.0.1 | approved |
| `SPI.MIDDLE.ALG.LINEQ.ONESTEP_MUL.01` | linear one_step_mul | 1.0.1 | approved |
| `SPI.MIDDLE.ALG.LINEQ.TWOSTEP.01` | linear two_step | 1.0.1 | approved |
| `SPI.MIDDLE.ALG.LINEQ.BOTHSIDES.01` | linear both_sides | 1.0.1 | approved |
| `SPI.MIDDLE.ALG.LINEQ.BRACKETS.01` | linear brackets | 1.0.1 | approved |
| `SPI.MIDDLE.NUM.SIGNED_OPERATIONS.01` | prerequisite (signed/rational arithmetic) | — | approved |
| `SPI.MIDDLE.ALG.INVERSE_OPERATIONS.01` | prerequisite (inverse operations) | — | approved |
| `SPI.MIDDLE.ALG.EXPAND_BRACKETS.01` | prerequisite (expand `a(bx+c)`) | — | approved |

The three `SPI.MIDDLE.{NUM,ALG}.*` prerequisite objectives were curriculum-approved on
2026-06-21 (`DECISION_LOG.md` #31) with final wording — foundational prerequisites
attached in the curriculum graph where genuine (e.g. of the linear-equations
objectives); they are not themselves bound to a generated task in this version.

| `SPI.MIDDLE.GEO.ANGLES_STRAIGHT_LINE.01` | geometry straight_line_missing_angle | — | approved (definition) |
| `SPI.MIDDLE.GEO.TRIANGLE_ANGLE_SUM.01` | geometry triangle_missing_angle | — | approved (definition) |
| `SPI.MIDDLE.GEO.ISOSCELES_BASE_ANGLES.01` | geometry isosceles_base_angle | — | approved (definition) |
| `SPI.MIDDLE.GEO.VERTICALLY_OPPOSITE_ANGLES.01` | geometry vertically_opposite_angle | — | approved (definition) |
| `SPI.MIDDLE.GEO.ANGLES_AT_POINT.01` | geometry angles_at_point_missing | — | approved (definition) |

The five `SPI.MIDDLE.GEO.*.01` objective **definitions** (IDs, wording, one-to-one task
mappings) were curriculum-approved on 2026-06-22 (`DECISION_LOG.md` #34). Their **generator**
(`gen.geometry.angles-figures`) is NOT yet approved — see the pending section below.

## REJECTED (owner final decision)

| Generator | Version | Status | Reference |
| --- | --- | --- | --- |
| `gen.geometry.angles-figures` | 1.2.1 | **REJECTED (owner, 2026-06-22; `DECISION_LOG.md` #37)** — not approved; not for use/publication | tag `geometry-v1.2.1-rejected` |

The geometry generator and its SVG-diagram rendering are **rejected**. All geometry
versions remain `machine-validated` only and produce **no approved/published** items.
Code and fixtures are preserved in history (nothing deleted). The five
`SPI.MIDDLE.GEO.*.01` objective **definitions remain curriculum-approved** (`DECISION_LOG.md`
#34); the rejection is of the generator/rendering, not the objective definitions.
Forward handling (leave dormant vs. unregister from the platform) is awaiting owner
direction. The earlier geometry versions are below for history only.

| Generator | Version | Status | Reference |
| --- | --- | --- | --- |
| `gen.geometry.angles-figures` | 1.2.0 | preserved (superseded by 1.2.1, never approved) | tag `geometry-v1.2.0-superseded` |
| `gen.geometry.angles-figures` | 1.1.0 | preserved (superseded by 1.2.0, never approved) | tag `geometry-v1.1.0-superseded` |
| `gen.geometry.angles-figures` | 1.0.0 | preserved (superseded by 1.1.0, never approved) | tag `geometry-v1.0.0-superseded` |

The geometry SVG pilot was revised to **v1.1.0** (`DECISION_LOG.md` #34: reflex-arc,
vertically-opposite-marker, accessibility-equivalence), then **v1.2.0** (#35: per-angle
arc radii + a11y-text tamper guard), then **v1.2.1** (#36: visual-layout-only — adaptive
small-sector label placement with leaders + nine blocking visual-clearance checks). Each
revision preserved its predecessor; only the latest is the pending candidate. It is self-verifying (byte-identical
Python/TypeScript SVG parity; semantic arc validators; 10,000-seed sweep 0 invalid;
schema + a11y gates pass). The **generator, its SVG rendering contract, the v1.1.0
representative items, and golden exemplars remain pending** the owner's review of the
revised review pack + the visual edge-case audit. All generated items remain
`machine-validated`. This section moves into "Approved generators" only on that final
decision.

## Golden exemplars (curriculum-reviewed and approved)

The representative reviewed examples are approved as **golden exemplars**. The
exemplar items themselves are preserved byte-for-byte in the golden fixtures (not
re-serialized), so their stored `lifecycle.state` remains `generated`; their
approved-exemplar status is recorded here.

| Generator | Golden fixture | Approved exemplar seeds |
| --- | --- | --- |
| `gen.sequences.arithmetic` 1.1.0 | `oracle/golden/arithmetic_sequences.golden.json` | 1, 42, 123456789, 2147483647 |
| `gen.sequences.geometric` 1.1.0 | `oracle/golden/geometric_sequences.golden.json` | 1, 42, 123456789, 2147483647 |
| `gen.algebra.linear-equations` 1.0.1 | `oracle/golden/linear_equations.golden.json` | 1, 42, 123456789, 2147483647 |
| Review-pack exemplars | `docs/review/arithmetic_sequences_review_pack.md`, `docs/review/geometric_sequences_review_pack.md`, `docs/review/linear_equations_review_pack.md` | all listed items |

## Lifecycle policy (unchanged)

- **Newly generated items always begin at `machine-validated`.** Approval of a
  generator version and of the golden exemplars does **not** auto-approve or
  publish future generated items.
- Advancing any individual item beyond `machine-validated` remains a per-item
  curriculum-authority decision.

## Preservation guarantees

The following are preserved unchanged and are protected by the test gate:

- arithmetic v1.0.0 / v1.0.1 / v1.1.0, geometric v1.0.0 / v1.1.0, and
  **linear-equations v1.0.0 / v1.0.1** output;
- all golden and parity fixtures, including the frozen-immutable
  `oracle/golden/linear_equations.{golden,parity}.json` (v1.0.1);
- the Python oracle and the TypeScript implementation (kept byte-for-byte in
  parity);
- exact-rational normalization (`{num, den}`, den ≥ 1);
- independent iterative validation;
- the 10,000-seed-sweep testing gate (zero invalid items required).
