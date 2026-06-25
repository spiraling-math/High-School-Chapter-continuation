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
| `gen.geometry.angles-figures` | **1.2.3** | curriculum-approved | `GENERATOR_SPEC_geometry_svg_proposal.md` | `4c9705c` | 2026-06-23 |
| `gen.geometry.coordinate-lines` | **1.0.2** | curriculum-approved | `GENERATOR_SPEC_coordinate_lines_PROPOSAL.md` | `660b50e` | 2026-06-24 |
| `gen.sequences.geometric` | 1.0.0 | preserved (superseded by 1.1.0) | — | `af92375` | — |
| `gen.sequences.arithmetic` | 1.0.0, 1.0.1 | preserved (superseded by 1.1.0) | — | `5a962a7`, `4cbb6a1` | — |
| `gen.algebra.linear-equations` | 1.0.0 | preserved (superseded by 1.0.1) | — | `1cfc76c` | — |
| `gen.geometry.angles-figures` | 1.2.0 / 1.2.1 / 1.2.2 | preserved (superseded/rejected; never approved) | — | tags below | — |
| `gen.geometry.coordinate-lines` | 1.0.0 / 1.0.1 | preserved (superseded by 1.0.2; never approved) | — | tags `coordinate-lines-v1.0.{0,1}` | — |

Git tags identify the approved reference implementations:
`approved-arith-v1.1.0`, `approved-geo-v1.0.0`, `approved-geo-v1.1.0`,
`approved-linear-v1.0.1`, `approved-geometry-v1.2.3` (= `geometry-v1.2.3`),
`approved-coordinate-lines-v1.0.2` (= `coordinate-lines-v1.0.2`).

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

| `SPI.MIDDLE.GEO.ANGLES_STRAIGHT_LINE.01` | geometry straight_line_missing_angle | 1.2.3 | approved |
| `SPI.MIDDLE.GEO.TRIANGLE_ANGLE_SUM.01` | geometry triangle_missing_angle | 1.2.3 | approved |
| `SPI.MIDDLE.GEO.ISOSCELES_BASE_ANGLES.01` | geometry isosceles_base_angle | 1.2.3 | approved |
| `SPI.MIDDLE.GEO.VERTICALLY_OPPOSITE_ANGLES.01` | geometry vertically_opposite_angle | 1.2.3 | approved |
| `SPI.MIDDLE.GEO.ANGLES_AT_POINT.01` | geometry angles_at_point_missing | 1.2.3 | approved |
| `SPI.MIDDLE.GEO.COORD.CARTESIAN_PLANE.01` | coordinate-lines (foundational) | 1.0.2 | approved |
| `SPI.MIDDLE.GEO.COORD.READ_POINT.01` | coordinate read_point | 1.0.2 | approved |
| `SPI.MIDDLE.GEO.COORD.PLOT_POINT.01` | coordinate plot_point | 1.0.2 | approved |
| `SPI.MIDDLE.GEO.COORD.GRADIENT_TWO_POINTS.01` | coordinate gradient_two_points | 1.0.2 | approved |
| `SPI.MIDDLE.GEO.COORD.MIDPOINT.01` | coordinate midpoint | 1.0.2 | approved |
| `SPI.MIDDLE.GEO.COORD.INTERPRET_MX_C.01` | coordinate interpret_mx_c | 1.0.2 | approved |
| `SPI.MIDDLE.GEO.COORD.EQUATION_FROM_GRAPH.01` | coordinate equation_from_graph | 1.0.2 | approved |
| `SPI.MIDDLE.GEO.COORD.EQUATION_FROM_2PTS.01` | coordinate equation_from_two_points | 1.0.2 | approved |

The five `SPI.MIDDLE.GEO.*.01` angle objective **definitions** were curriculum-approved on
2026-06-22 (`DECISION_LOG.md` #34); their **generator** `gen.geometry.angles-figures`
**v1.2.3** was curriculum-approved on 2026-06-23 (`DECISION_LOG.md` #40). The eight
`SPI.MIDDLE.GEO.COORD.*` objective definitions and the generator `gen.geometry.coordinate-lines`
**v1.0.2** were curriculum-approved on 2026-06-24 (`DECISION_LOG.md` #44) — see below.

## Geometry generator — curriculum-approved at v1.2.3 (2026-06-23, `DECISION_LOG.md` #40)

`gen.geometry.angles-figures` **v1.2.3** is curriculum-approved and is now selectable in
normal Generator Studio use and included in production exports/samples (`approvalStatus:
approved`; only v1.2.3 is registered). The owner approved the generator specification, the
SVG rendering contract, the diagram-validation contract, the difficulty model, the
worked-solution structures, the misconception/distractor rules, the accessibility model,
the current F1/F2/F3 scope, the reviewed representative items as golden exemplars, and the
final **leader-rendering contract** (geometry lines solid + primary; callout leaders
thinner, dashed, round-capped, secondary; non-degenerate; no crossings of rays/sides/arcs/
vertices/labels/other leaders; small-sector labels unambiguous; deterministic regeneration
when no valid layout exists).

**Frozen, immutable approval artifacts** (the reviewed v1.2.3 package, hash-attested by the
generation manifest and protected by the artifact-integrity test gate):

| Artifact | Path |
| --- | --- |
| Golden fixture | `oracle/golden/geometry_angles.golden.json` |
| Parity fixture | `oracle/golden/geometry_angles.parity.json` |
| Canonical SVG fixtures | `docs/review/geometry_svgs/` (45 files) |
| Review pack | `docs/review/geometry_angles_review_pack.md` + `.json` |
| Visual audit | `docs/review/geometry_visual_audit.html` |
| Generation manifest (SHA-256 of all the above + samples) | `docs/review/geometry_manifest.json` |

The generation manifest records the build commit (`bffba8c3f0…`), generator id/version
(1.2.3), validator version (1.2.3), timestamp, regeneration commands, and the SHA-256 of
every approval artifact. The blocking artifact-integrity tests (`oracle/tests/test_geometry.py`
`TestArtifactIntegrity` + `domains/geometry/artifact-integrity.test.ts`) re-hash these files
and confirm audit-version-matches-generator, audit-commit-matches-build, no-stale-version-text,
and manifest-hashes-match on every run.

### Rejected / superseded geometry versions (preserved in history; never selectable)

| Generator | Version | Status | Reference |
| --- | --- | --- | --- |
| `gen.geometry.angles-figures` | 1.2.2 | superseded (review package rejected; `DECISION_LOG.md` #39) | tag `geometry-v1.2.2` |
| `gen.geometry.angles-figures` | 1.2.1 | **REJECTED** (owner; `DECISION_LOG.md` #37) | tag `geometry-v1.2.1-rejected` |
| `gen.geometry.angles-figures` | 1.2.0 | superseded (never approved) | tag `geometry-v1.2.0-superseded` |
| `gen.geometry.angles-figures` | 1.1.0 | preserved (superseded by 1.2.0, never approved) | tag `geometry-v1.1.0-superseded` |
| `gen.geometry.angles-figures` | 1.0.0 | preserved (superseded by 1.1.0, never approved) | tag `geometry-v1.0.0-superseded` |

The geometry SVG pilot was revised to **v1.1.0** (`DECISION_LOG.md` #34: reflex-arc,
vertically-opposite-marker, accessibility-equivalence), then **v1.2.0** (#35: per-angle
arc radii + a11y-text tamper guard), then **v1.2.1** (#36: adaptive small-sector label
placement). v1.2.1 was REJECTED (#37); the family was retained and gated as **v1.2.2**
(#38: approval-lifecycle visibility gate). The v1.2.2 review package was then REJECTED
(#39) for an indistinct/zero-length leader style, and corrected as **v1.2.3** (secondary
dashed non-crossing leaders + a generation manifest and blocking artifact-integrity
tests), which was **curriculum-approved** (#40). Each revision preserved its predecessor;
v1.2.0/1.2.1/1.2.2 stay in history (unapproved) and are **not registered/selectable** —
only the approved v1.2.3 is.

## Coordinate-lines generator — curriculum-approved at v1.0.2 (2026-06-24, `DECISION_LOG.md` #44)

`gen.geometry.coordinate-lines` **v1.0.2** is curriculum-approved and is now selectable in
normal Generator Studio use and included in production exports/samples (`approvalStatus:
approved`; only v1.0.2 registered). The owner approved the generator, its specification, the
validator contract, the canonical Cartesian SVG renderer, the exact-rational + ordered-pair
answer models, the `y = mx + c` equivalence checker, the difficulty model, the worked-solution
structures, the misconception/distractor rules, the accessibility model, the four rendering
modes (premium / premium-dark / accessible-colour / monochrome-print), the **per-SVG
style-isolation contract** (per-root CSS custom properties + one common `.cx-figure` ruleset,
`core/visual-style/cartesian-theme`), the **6000×4200 high-resolution export contract**
(materialized, self-contained), the seven-task scope + exclusions, and the reviewed items as
golden exemplars. The eight `SPI.MIDDLE.GEO.COORD.*` objective definitions are
`reviewStatus: approved`. History: implemented #41 → curriculum REVISE #42 → v1.0.1 →
visual/export REJECT #43 → v1.0.2.

**Frozen, immutable approval artifacts** (hash-attested by the generation manifest +
artifact-integrity tests):

| Artifact | Path |
| --- | --- |
| Golden fixture | `oracle/golden/coordinate_lines.golden.json` |
| Parity fixture (Py/TS) | `oracle/golden/coordinate_lines.parity.json` |
| Canonical SVG fixtures | `docs/review/coordinate_lines_svgs/` (25 files) + `coordinate_lines_8k_sample.svg` |
| Review pack | `docs/review/coordinate_lines_review_pack.md` + `.json` |
| Visual audit + premium gallery | `docs/review/coordinate_lines_visual_audit.html` |
| Distribution report | `docs/review/coordinate_lines_distribution.json` |
| Computed-style browser verification | `docs/review/coordinate_lines_browser_verification.json` |
| Generation manifest (SHA-256 of all the above + the 3 export hashes) | `docs/review/coordinate_lines_manifest.json` |

The three 6000×4200 export hashes (premium `424d61c2…`, accessible `45e7d9c8…`, print
`1cc12dce…`) are recorded in the manifest's `rasterExports`. v1.0.0/v1.0.1 are preserved in
history (unapproved, not registered/selectable; tags `coordinate-lines-v1.0.{0,1}`).

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
| `gen.geometry.angles-figures` 1.2.3 | `oracle/golden/geometry_angles.golden.json` | golden seeds + the review-pack items |
| `gen.geometry.coordinate-lines` 1.0.2 | `oracle/golden/coordinate_lines.golden.json` | golden seeds + the 29 review-pack items (25 figures + 4 text-only) |
| Review-pack exemplars | `docs/review/arithmetic_sequences_review_pack.md`, `docs/review/geometric_sequences_review_pack.md`, `docs/review/linear_equations_review_pack.md`, `docs/review/geometry_angles_review_pack.md`, `docs/review/coordinate_lines_review_pack.md` | all listed items |

## Pending-review generators (built, gated, awaiting owner review)

- **`gen.stats.data-handling` 1.0.1 — IMPLEMENTED, `approvalStatus: pending-review`** (`DECISION_LOG.md` #45 spec-approve, #46 REVISE applied).
  Built oracle-first, then corrected to v1.0.1 after the owner's curriculum/semantic REVISE
  (context-domain registry; unique-mode-gated distractors; pictogram exact-symbol policy; blank-kind
  frequency diagnostics; even-median solutions; representation-specific solutions; single-source
  ranges + registry-as-single-source misconceptions; signed-arithmetic display). **v1.0.0 preserved
  unchanged** (tags `stats-data-handling-v1.0.0`; v1.0.1 = `stats-data-handling-v1.0.1`). **Not yet
  curriculum-approved and NOT selectable** in normal Generator Studio or production samples (gated;
  0 stats records in `bank.json`). The eleven `SPI.MIDDLE.STAT.*` objectives are
  `reviewStatus: approved-for-implementation` (curriculum-approved only after the owner reviews the
  implemented generator + review pack). Independent Python oracle + byte-for-byte TS mirror;
  golden(19)+parity(300) byte-identical; 10,000-seed sweep 0 invalid; conformant. Review artifacts:
  `docs/review/stats_data_handling_{review_pack.md,review_pack.json,visual_audit.html,distribution.json,browser_verification.json,manifest.json}`
  (35 misconceptions; SHA-256 attested; Python artifact-integrity test). The additive
  `core/visual-style/data-chart-theme` reuses the approved cartesian-theme (coordinate-lines v1.0.2
  output unchanged). **Next owner decision: APPROVE or REJECT.**

## Lifecycle policy (unchanged)

- **Newly generated items always begin at `machine-validated`.** Approval of a
  generator version and of the golden exemplars does **not** auto-approve or
  publish future generated items.
- Advancing any individual item beyond `machine-validated` remains a per-item
  curriculum-authority decision.

## Preservation guarantees

The following are preserved unchanged and are protected by the test gate:

- arithmetic v1.0.0 / v1.0.1 / v1.1.0, geometric v1.0.0 / v1.1.0,
  **linear-equations v1.0.0 / v1.0.1**, **geometry v1.2.3**, and
  **coordinate-lines v1.0.2** output;
- all golden and parity fixtures, including the frozen-immutable
  `oracle/golden/linear_equations.{golden,parity}.json` (v1.0.1),
  `oracle/golden/geometry_angles.{golden,parity}.json` (v1.2.3, manifest-attested), and
  `oracle/golden/coordinate_lines.{golden,parity}.json` (v1.0.2, manifest-attested);
- the Python oracle and the TypeScript implementation (kept byte-for-byte in
  parity);
- exact-rational normalization (`{num, den}`, den ≥ 1);
- independent iterative validation;
- the 10,000-seed-sweep testing gate (zero invalid items required).
