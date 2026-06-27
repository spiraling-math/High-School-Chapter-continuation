# Objective Registry & Standards — Phase 1 (CURRICULUM-APPROVED)

Phase 1 of `SPI_MATH_OBJECTIVE_REGISTRY_AND_STANDARDS_PROPOSAL.md` (§15), built as a **pure read layer** over
the existing eleven `curriculum/objectives/*.json` files. It is **output-neutral**: no objective file, golden
fixture, `curriculum-objective.schema.json`, inline `externalAlignments`, or approved-family artifact changes.
Curriculum-APPROVED by the owner (`DECISION_LOG.md` #63): manifest `approvalStatus: approved`, tag
`approved-objective-registry-phase1-v1.0.0` (implementation tag `objective-registry-phase1-v1.0.0`); the
Phase-1 artifacts below are frozen immutable (manifest sha256 + integrity test). This approval covers the
architecture + mechanism only — the pilot alignment records stay `proposed`/design-proof and the known-baseline
5-ID list is a non-blocking backlog for a separately-gated future authoring phase.

## What was built

| Artifact | Role |
|---|---|
| `core/curriculum/objective-registry.ts` | Read-only unified index keyed by `objectiveId` (`loadRegistry/all/byId/byStage/byDomain/byStrand/count`); variable-depth `SPI.STAGE.DOMAIN[.SUB].MICRO.NN` parser (§3). |
| `core/curriculum/registry-graph.ts` | The **global** graph check over all 70 objectives — extends `core/curriculum/graph-check.ts` with the eight buckets (§7.4) and the §11 G1–G13 predicates. `ok = errors.length===0 && newReferencedUndefined.length===0`. |
| `core/curriculum/generator-capability.ts` | The §8/§10 coverage join over the SDK registry + per-module `describe()` + the `*-objective-ids.ts` task→objective maps. |
| `curriculum/registry/known-baseline-referenced-undefined.json` | The **frozen** known-baseline (owner correction A, §7.5) — the 5 pre-existing referenced-but-undefined prerequisite IDs. |
| `schemas/standard-alignment.schema.json` | NEW additive alignment-record schema (§9.4) — direction is always **alignment → SPI**. Does **not** widen `curriculum-objective.schema.json`. |
| `curriculum/alignments/pilot.json` | A 2-record ratio pilot at `status: "proposed"` — design proof only. |
| `docs/review/objective_registry_gap_report.json` | The 8-bucket global graph report. |
| `docs/review/objective_coverage_report.json` | The coverage / gap report (G2/G1/G0 + the ID buckets). |
| `docs/review/objective_registry_manifest.json` | sha256 of every Phase-1 artifact + a frozen record of the 11 objective files' hashes (drift detection). |
| `scripts/build-registry-reports.mjs` | Regenerates the three reports above (offline, deterministic). |
| `core/curriculum/{objective-registry,registry-graph,alignment,coverage,registry-manifest}.test.ts` | 46 tests, incl. adversarial gate cases. |

## Known-baseline referenced-undefined policy (owner correction A, §7.5)

The approved data references 5 prerequisite IDs it does not yet define
(`SPI.MIDDLE.ALG.NOTATION_SUBSTITUTION.01`, `SPI.MIDDLE.ALG.SUBSTITUTION.01`,
`SPI.MIDDLE.GEO.ANGLE_MEASURE_NOTATION.01`, `SPI.MIDDLE.GEO.TRIANGLE_CLASSIFY.01`,
`SPI.MIDDLE.NUM.INTEGERS_NUMBER_LINE.01`). These are **recorded and reported, not gated**. The gate blocks only
on a **new** referenced-undefined introduced after the baseline was frozen. Authoring the missing foundational
objectives is reserved for a separate, owner-gated phase (§16.5); the baseline shrinks by exactly one ID when
the corresponding objective is later authored and its reference resolves.

## How to run

```sh
PATH="$PATH:/c/Program Files/nodejs" node --test core/curriculum/   # the 46 registry tests
node scripts/build-registry-reports.mjs                            # regenerate the 3 reports (deterministic)
```

The CI gate **fails** on: duplicate IDs · prerequisite cycle · live→`retired` dependence · non-empty
`newReferencedUndefined` · unresolved generator / review-pack / standards-alignment references · approved-object
immutability violation · approved-family fixture drift. It **passes** when the only unresolved prerequisite
references are exactly the recorded known-baseline set and no new one is introduced.

## Current results

- Global graph: `ok = true`, `objectiveCount = 70`, `newReferencedUndefined = []`, `knownBaselineReferencedUndefined` = the 5 (count 5).
- Coverage: **G2 covered-approved 66 / G1 pending 0 / G0 no-generator 4** (the foundational ALG/NUM/COORD prerequisite objectives) / `orphanedTasks 0`.
- Pilot: 2 records (IGCSE 0580 → ratio objectives), `status: "proposed"`, SPI links resolve.
- TS 369/369 · 13 Python suites · tsc 0 · registry manifest 0 drift · objective files + golden/parity byte-for-byte unchanged.
