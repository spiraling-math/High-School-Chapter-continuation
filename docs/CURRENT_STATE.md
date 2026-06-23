# Current State

Last updated: 2026-06-22.

## Geometry SVG pilot — v1.2.3 PENDING-REVIEW (gated), family retained (2026-06-23)

**Owner rejected the v1.2.2 review package (`DECISION_LOG.md` #39):** leaders were styled
like rays, some were zero-length, and the audit had stale version text. Confirmed in the
current generator (case B), so the correction shipped as **v1.2.3** (v1.2.2 preserved, tag
`geometry-v1.2.2`):

- **Secondary, non-crossing leaders.** `.gx` is now `#555` / `1.5px` / dashed / round-cap
  — thinner + dashed vs the 3px solid #111 geometry (browser-confirmed). Leaders are
  **radial along the sector bisector, inside the wedge**, so they never cross a ray, side,
  arc, or vertex; they are **non-degenerate** (≥ 26px; 0 zero-length across 6000+ items).
- **Generation manifest** `docs/review/geometry_manifest.json` (git commit, id/version,
  timestamp, commands, SHA-256 of pack/audit/fixtures/samples + 45 svgs) + **blocking
  artifact-integrity tests** (audit-version-matches-generator, audit-commit-matches-build,
  no-stale-version-text, manifest-hashes-match) and SVG-level leader-contract checks
  (leader-style-distinct, non-degenerate, min-length, ray/side/arc/vertex/label/leader
  clearance, route-unambiguous) for seeds 26/73/98/13322, VO-1, straight-1, triangle-1.

The pilot remains behind the **approval-lifecycle visibility gate** (`DECISION_LOG.md` #38):

- Each registered generator now carries an `approvalStatus` (`approved` / `pending-review`
  / `rejected`); helpers `generatorsForMode("normal"|"review")` and `approvedGenerators()`
  enforce it (`core/sdk/generator-module.ts` + `sequence-registry.ts`).
- The three curriculum-approved families are `approved`; **geometry is `pending-review`**.
- The Studio shows only approved generators to normal users; **review/developer mode
  (URL `?review`)** also shows geometry, labelled "machine-validated — pending curriculum
  approval". **Production exports/samples exclude pending-review generators** (geometry is
  absent from the offline samples). Browser-verified: normal mode = 3 generators (no
  geometry); `?review` = 4 (geometry shown, labelled, renders, no console errors).
- v1.2.2's diagram output is the accepted **v1.2.1 adaptive-placement** work (the rejection
  was about exposure/lifecycle, not the diagrams); only the version fields change. Geometry
  remains fully registered + tested for development. The family is **not** deleted/retired.

It becomes visible to normal users only after **final curriculum approval**. The five
`SPI.MIDDLE.GEO.*.01` objective **definitions remain curriculum-approved**.

The remainder of this section is the development record of the geometry pilot.

### (Historical) adaptive-placement revision detail (v1.2.1 / v1.2.2)

**Owner decisions (`DECISION_LOG.md` #34, #35, #36):** the five `SPI.MIDDLE.GEO.*.01`
objective **definitions are curriculum-approved**; the generator was **revised to v1.1.0**
(reflex arcs / VO marker / accessibility), **v1.2.0** (per-angle arc radii), and **v1.2.1**
(visual-layout-only: adaptive small-sector label placement). v1.0.0/v1.1.0/v1.2.0 are
preserved (tags `geometry-v1.{0,1,2}.0-superseded`). The latest revision:

- **Adaptive label placement (v1.2.1).** Each angle label is placed INSIDE its sector when
  its full bounding box fits with clearance (radius from the sector half-angle via the
  DIR table), otherwise a CALLOUT in clear space joined by a short neutral leader (found
  by a deterministic integer radius×perpendicular search). 10-degree questions are kept.
  **Nine blocking visual-clearance checks** on the COMPLETE label boxes (min clearance
  8px): label-placement-feasible, labels-within-canvas, label-{label,ray,arc,vertex}-
  clearance, leader-does-not-cross-label, small-sector-label-unambiguous,
  label-inside-intended-region. Browser before/after (seeds 98/26/13322) confirms the
  crowded 10°/x labels now separate cleanly with leaders.

The earlier corrected revisions:

- **Per-angle arc radii (v1.2.0).** Arcs that share a vertex (angles on a line / around a
  point) use GRADUATED radii (44, 64, 84, …) so each angle reads as a distinct ring, not
  one continuous circle; triangle/isosceles vertex arcs are scaled to ≤ 30% of the
  shortest adjacent side (capped at 56) so arcs never reach the opposite side or meet.
  Exact-integer radii (pure-integer isqrt); browser-confirmed distinct/bounded.
- **a11y-text-canonical validator (v1.2.0).** The stored accessibility + media long
  description must equal the canonical recomputed text byte-for-byte (catches a tampered
  stored description). A 6-agent adversarial-verification workflow returned **GO**, with
  all six correctness claims holding under exhaustive scrutiny.

- **Reflex-correct arcs.** Arc rendering is now `(vertex, startDir, measure)` with
  large-arc-flag = 1 iff measure > 180 (exactly 180 → 0, a documented semicircle policy)
  and sweep-flag = 0 (the CCW interior sector). This fixes reflex regions (e.g. a 263°
  unknown / 248° given that previously drew the minor complement) AND the triangle /
  isosceles interior arcs, which previously bulged **outside** the angle. The SVG arc
  convention was pinned down empirically and browser-confirmed (arc lengths match the
  measures: 263°→321px, 331°→404px, 248°→303px). Labels sit on the sector bisector,
  inside the intended sector for minor and reflex alike.
- **Neutral vertically-opposite target.** The opposite (x) region is marked by a neutral
  leader, not a matching arc; the diagram no longer announces the equality.
- **Equivalent-not-easier accessibility.** Descriptions convey the same givens and
  configuration as the figure but state no theorem, calculation, or answer.
- **Nine new SEMANTIC validator checks** that PARSE the SVG arc commands and verify them
  against the FigureModel (arc-large-flag-correct, arc-sweep-correct,
  reflex-region-rendered-correctly, label-inside-intended-region,
  no-theorem-revealing-markers, target-region-unambiguous, a11y-equivalent-information,
  …); tamper tests prove they catch a wrong flag or leaked theorem.
- **Visual edge-case audit** `docs/review/geometry_visual_audit.html` (10°…near-max,
  reflex unknown + given, every task family, monochrome print) — **human inspection
  required** before final approval.

The first **diagram-bearing** family, placed at **SPI-Math Middle School → Geometry →
Ch.21 (Angles, Lines, Triangles)**. **The diagram IS the question** — every figure is
computed from the same parameters as the prompt and answer.

- Five tasks one-to-one with five `SPI.MIDDLE.GEO.*.01` objectives: angles on a straight
  line, triangle angle sum, isosceles base angle, vertically opposite (free-response
  only), angles around a point. MC (3 distinct formula-backed distractors) for the other
  four. Integer-degree answers only.
- **No runtime trigonometry**: ray directions come from a committed integer direction
  table (`core/geometry/dir-table.{json,ts}`; offline atan2 audit, worst 0.003°);
  coordinates use one round-half-up rule (BigInt in TS); the SVG is hand-serialized
  canonically. The Python oracle and the TypeScript app produce **byte-identical SVG**
  (golden + 300-entry parity fixture). All figures `toScale:false` with a visible
  **NOT TO SCALE**; the blocking validator rebuilds the figure and asserts the SVG
  byte-for-byte (diagram-to-data consistency, no atan2).
- Realisability guards: every region ≥10°; isosceles apex even 20–160 with **exactly
  equal squared legs**; an integer **label-overlap guard** (0 overlaps / 8,000 items);
  unique answers. Vertically-opposite shows no equality marks (no theorem reveal); the
  unknown is always rendered as `x` (no diagram leakage).
- Accessibility: `role="img"` + `aria-label` + `<title>`/`<desc>` + a data-table
  fallback, **no hard-coded IDs** → multi-item exports have no duplicate DOM ids and no
  answer in any accessibility text. Monochrome (#111/#444 only). SVGs inline into the
  Studio preview and the worksheet/solutions exports with no external/script refs.

Verified: typecheck clean; **168 TS tests** (SVG byte-parity, 2000-seed stability gate,
approval-lifecycle gate, leader-contract + artifact-integrity, reflex/sweep/a11y-text
tamper, adaptive-placement clearances, VO marker, geometry a11y + multi-item export, JSON
round-trip) + **38 geometry oracle tests** (incl. owner seeds 26/73/98/13322 + VO/straight/
triangle-1, narrow 10/11/12/15/20, 3- and 4-region, all leader + visual-clearance checks) (DIR-table audit, round-half-up, exact
isosceles legs, reflex large/sweep flags across 1500 seeds, the ±0.5° + arc-sector
coverage diagnostics, boundary 179/180/181, a11y-equivalence positive+negative, VO
neutral leader, tamper); **geometry 10,000-seed sweep 0 invalid** (all 5 tasks, bands
1–4); **arithmetic + geometric + linear 10k regression sweeps 0 invalid with byte-for-
byte unchanged fixtures**; schema conformance (Python + Ajv); offline build OK; Studio
browser-verified on the visual audit (reflex arc lengths match measures: 263°→321px,
331°→404px, 248°→303px; VO neutral leader; 0 failing chips across all 16 cards). Review
pack: `docs/review/geometry_angles_review_pack.md` (45 items + 45 `.svg`; all five
objectives/tasks; FR + MC; every band; two-/multi-given lines; general + isosceles;
min/max + reflex + non-multiple-of-5 angles; 12/13 misconceptions exemplified; 0
collision violations; monochrome). Visual edge-case audit:
`docs/review/geometry_visual_audit.html`.

**Status:** at **v1.2.3**, `approvalStatus: pending-review` (machine-validated, gated to
review mode; excluded from normal users + production exports). v1.2.1 rejected; v1.2.2
review package rejected; both preserved.
The **five objective definitions are curriculum-approved**; the **generator + exemplars
await final curriculum approval** before exposure to normal users.
Awaiting the owner's final geometry curriculum decision (see "Precise curriculum
decision awaiting the owner" at the end). Nothing here is approved or published.

## Linear equations pilot — CURRICULUM-APPROVED v1.0.1 (2026-06-21)

**Owner-approved** (`DECISION_LOG.md` #30): the generator, the five
`SPI.MIDDLE.ALG.LINEQ.*` objectives (now `reviewStatus: approved`), the
misconceptions, and the spec are curriculum-approved at **v1.0.1**; reviewed items
are approved golden exemplars; v1.0.1 fixtures are frozen immutable; v1.0.0 preserved;
tag `approved-linear-v1.0.1`. `ONESTEP_ADD.01` is integer-only. Newly generated items
remain `machine-validated`; no auto-approval/publication.


First non-sequence family, proving the SDK on new mathematics:
**`gen.algebra.linear-equations` v1.0.1**, placed in the uploaded curriculum at
**SPI-Math Middle School → Algebra → Linear equations in one variable** (Topic 12;
aligned to IGCSE 0580 C2.5/E2.5 and Singapore Lower Secondary). Built from the
owner's APPROVE-WITH-REVISIONS decision (`DECISION_LOG.md` #28), then revised per the
owner's curriculum-review REVISE as **v1.0.1** (`DECISION_LOG.md` #29; v1.0.0
preserved): interactionType-first terminology, placeholder-free student feedback
generated from the actual coefficients, the positive-coefficient solution strategy,
integer-only `ONESTEP_ADD`, and a recalibrated complexity-factor difficulty model
spreading brackets across bands 3–5.

- Tasks: one-step (+/−), one-step (×, `ax=c`), two-step, variables-both-sides, one
  bracket; free-response + multiple-choice; integer + exact-rational answers.
- Minimal `LinExpr` algebra (`core/exact-math/linexpr.ts` + oracle mirror) — no CAS;
  backward construction from a chosen exact solution; uniqueness via `a ≠ c`.
- Independent Python oracle + TypeScript with **byte-for-byte parity** (golden +
  300-entry fixture); approved misconception set with per-task eligibility, dedupe,
  and deterministic regeneration (3 distinct distractors); the approved 6-step
  worked solution with substitution check; revised leakage rule; difficulty floors.
- 5 objectives (`SPI.MIDDLE.ALG.LINEQ.*`, `reviewStatus: proposed`) + misconception
  data; registered in the SDK registry and the Studio.

Verified: typecheck clean; **142 TS tests** (parity + 2000-seed stability gate +
linear a11y + back-compat + feedback-placeholder + band-coverage + interaction/
answer-type consistency); Python linear tests; **linear 10,000-seed sweep 0 invalid**
(all 5 tasks, bands 1–5); **arithmetic + geometric 10k regression sweeps 0 invalid
with no fixture drift** (approved output unchanged); schema conformance (Python +
Ajv); offline build `external references: none`; Studio browser-verified (positive-
coefficient solution, substitution, validation PASS, live axe 0 violations, no
console errors). Review pack: `docs/review/linear_equations_review_pack.md` (60
items; every band per task; all 11 MC rules; 0 collision violations; placeholder-free
feedback). **Items start `machine-validated`; the generator/objectives/spec are
curriculum-approved only after the owner reviews the pack.** No third generator
family started.

## Generator SDK foundation — COMPLETE (2026-06-21)

The technical SDK-foundation milestone is done (5 steps, all **output-neutral**).
Full record: `docs/SDK_FOUNDATION_CHECKPOINT.md`; decision `DECISION_LOG.md` #27.

- **Shared MC assembly** (`core/sdk/multiple-choice.ts`) — deterministic option
  assembly reused by both generators; misconception metadata/order/IDs preserved.
- **Universal validation predicates** (`core/sdk/checks.ts`) — domain-independent
  checks composed by both validators, which keep their domain-specific checks and
  exact IDs/order/messages; provenance/version checks added.
- **TD-1 resolved** — `interactionType` is the canonical config + bank field;
  legacy `answerType` normalized at the boundary; **conflicts rejected**;
  `BankRecord` schemaRev 3; IndexedDB **v3** single idempotent backfill; JSON
  import normalized; all six migration cases tested.
- **Runtime schema validation** (`core/schema/`) — build-time **precompiled
  standalone Ajv** (no codegen/network) gating bank storage, JSON import/export,
  and export assembly with rich errors; never repairs invalid math.
- **Automated a11y gates** (`apps/generator-studio/a11y.test.ts`) — axe-core +
  jsdom (dev/test only), zero critical/serious across the app, views, and exports,
  plus a WCAG-AA token-contrast guard. Fixed an unlabeled file input and a 4.47:1
  muted-text colour.

Verified: typecheck clean; **121 TS tests**; **19 Python tests**; both
**10,000-seed sweeps 0 invalid**; **no golden/parity fixture drift**; conformance
pass; offline build `external references: none`; live browser axe **0 violations**.
Ajv/axe-core/jsdom are dev/test-only (absent from the production bundle). The
foundation is **ready** to scaffold the linear-equations pilot — a curriculum
decision, not yet started. Do not add another mathematics generator until directed.

## Current phase

**Two generator families curriculum-approved.** arithmetic v1.1.0 and **geometric v1.1.0** are curriculum-approved (see `APPROVED_VERSIONS.md`, `DECISION_LOG.md` #24). Generator Studio offers both, with the IndexedDB bank and offline exports. Node.js v24.17.0 installed.

**Phase begun: Foundation Readiness & Generator SDK** (not another sequence family). Delivered this session:
- `docs/GENERATOR_SDK_DESIGN.md` — the SDK contract, answer model, registry, stability gate, versioning/approval workflow, and "add a generator" guide.
- `core/sdk/`: formal `GeneratorModule` contract; TD-1 `interactionType` resolver (back-compatible, tested); a reusable **stability-gate harness** run against BOTH approved generators (0 invalid, reproducible) — proving the SDK works without changing any output; a unified `sequence-registry.ts` (the Studio now re-exports it instead of duplicating).
- `core/curriculum/graph-check.ts` — curriculum-graph integrity (no duplicate IDs, acyclic prerequisites, prereq resolution); tested over the 9 approved objectives.
- `docs/FOUNDATION_READINESS.md` — readiness scorecard and the recommended phase order (SDK helper extraction → TD-1 → runtime schema + a11y gates → resume domain growth).

Output-neutral: all golden/parity fixtures and the two approved generators are unchanged (82 TS tests incl. harness + parity, both 10k sweeps 0 invalid, app browser-verified). Do not implement another sequence family, the sum-to-infinity MC variant, or a third generator family until directed.

**SDK extraction increment (output-neutral, verified byte-for-byte):**
- Centralized the difficulty band function into `core/difficulty/band.ts` (`round3`, `bandFromScore`) + oracle mirror `oracle/spi_oracle/difficulty.py`; both approved generators (TS + Python) now use it.
- **TD-1 step 1**: both TS generators accept `config.interactionType` (mapping the legacy `answerType`) via `core/sdk/interaction.ts`; proven identical output (`domains/sequences/interaction-config.test.ts`).
- Verification: 89 TS tests; oracle regeneration shows **no fixture drift**; TS parity against committed fixtures passes; conformance pass; app browser-verified (no console errors). No approved output changed.

## Generator Studio MVP (this session)

A single self-contained offline browser app: generate (seed/random/mode/task/target band) → preview (Question/Answer/Solution/Validation, KaTeX) → edit (protected params vs editable wording, lifecycle) → bank (IndexedDB: save/search/filter/open/duplicate/archive/delete, tested migrations) → export (standalone worksheet, answer key, worked solutions; JSON round-trip with integrity). KaTeX is bundled locally (fonts inlined); no CDN, no secrets, works from file://. The Python oracle remains a dev/verification reference only. Full details, decisions, gates, and known limitations: `docs/GENERATOR_STUDIO_MVP.md`.

Verified in a browser: no console errors; KaTeX + MathML render; save→reload persists; seed reproduces identically; keyboard tab navigation works; exports offline-safe with answers hidden in the student worksheet.

Tests: **46 TS** (`npm test`) + **18 Python** + 10,000-seed sweep (0 invalid) + conformance — all pass. Typecheck clean. Review pack: `docs/review/arithmetic_sequences_review_pack.md`. Build: `apps/generator-studio/dist/index.html` (via `npm run build:studio`).

## TypeScript production layer (this session, post Node.js install)

- Project config: `package.json`, `tsconfig.json`, `vitest.config.ts`, `.gitignore`.
- Ported to TypeScript and **tested with Node's built-in runner (offline, no `npm install` for tests)**:
  - `core/seeded-random/mulberry32.ts` — cross-language PRNG, asserted equal to the oracle's committed anchors.
  - `core/serialization/canonical.ts` — canonical JSON serializer matching the oracle's Python serialization.
  - `domains/sequences/arithmetic.ts` — full generator, asserting **byte-for-byte parity** with the oracle golden vectors.
  - `domains/sequences/validate.ts` — validator mirroring the oracle's **independent iterative verification**, with tests for valid items, corrupted-answer / out-of-domain catches, and a 4,000-item property sweep.
- Cross-language parity widened from 4 curated seeds to a **300-entry fixture** (`oracle/golden/arithmetic_sequences.parity.json`, 150 seeds × 2 modes); TS asserts byte-for-byte equality across all of them.
- `npm test` (= `node --test` over `core/**` and `domains/**`) → **21/21 TS tests pass**. `npm run typecheck` (tsc --noEmit) passes with `typescript` + `@types/node` (pinned, lockfile committed).
- Oracle updated with a portable `_round3` so difficulty floats serialize identically in Python and JS; golden + parity fixtures regenerated; Python suite still 18/18, sweep still 0 invalid.
- **Version control:** Git initialized on `main`; baseline commit + dependency commit. Source archives, reference collections, secrets, `.env`, local DBs, and `node_modules` are gitignored.

> Node is installed but not on the tool host's inherited PATH; prefix Node commands with a PATH refresh: `$env:Path = [System.Environment]::GetEnvironmentVariable('Path','Machine') + ';' + [System.Environment]::GetEnvironmentVariable('Path','User')`, or call `& "C:\Program Files\nodejs\node.exe"` directly. `npm install` (for `tsc` typecheck / future deps) needs a one-time network connection.

## Completed work

### Phase 0 (prior session)
- Inspected all uploaded archives/files; built hashed source manifest (CSV + JSON).
- Created the Phase 0 audit document set under `docs/`.

### Phase 1 (this session)
- Recorded the three owner decisions (capstone rights, university reserved, first slice = AA SL Ch.1 arithmetic sequences) and the environment/runtime decisions in `DECISION_LOG.md` (now 10 ADRs).
- Authored **6 JSON schemas** (`/schemas`), all valid JSON and cross-referencing a shared `answerType` vocabulary:
  curriculum-objective, question-item, generator-module, misconception, assessment-blueprint, source-record.
- Authored **12 architecture/standard documents** (`/docs`): ARCHITECTURE, DATA_MODEL, GENERATOR_STANDARD, VALIDATION_STANDARD, DIFFICULTY_MODEL, MISCONCEPTION_MODEL, ANSWER_EQUIVALENCE (authored directly), and ACCESSIBILITY_STANDARD, EXPORT_STANDARD, TESTING_STRATEGY, SECURITY_AND_PRIVACY, ROADMAP (drafted by subagents from detailed briefs).
- Wrote the first generator specification: `docs/GENERATOR_SPEC_arithmetic_sequences.md`.
- Created concrete data instances: two curriculum objectives (`curriculum/objectives/SPI.IBDPAASL.SEQSER.ARITH.json`) and five misconceptions (`core/misconceptions/sequences.json`).
- Built the **Python verification oracle** (`/oracle`): cross-language `mulberry32` PRNG, the full `gen.sequences.arithmetic` generator (describe/generate/solve/validate/distractors/solution/render/serialize), a unittest suite, a sweep driver, and a dependency-free schema conformance checker.
- **Ran everything. Real results below.**

## Verified results (executed, not asserted)

- `python oracle/tests/test_sequences.py` → **18 tests pass** (PRNG, known values, reproducibility, invalid-parameter handling, distractor invariants, and a 10,000-seed property sweep).
- `python oracle/run_oracle.py` → **10,000 seeds × 2 modes = 20,000 items, 0 invalid**; 200 reproducibility re-checks identical; all 4 tasks exercised; bands 1–4 observed. Golden vectors and PRNG anchors written under `oracle/golden/`.
- `python oracle/check_conformance.py` → **all schema examples, both objectives, all five misconceptions, four live generated items, and the generator descriptor conform** to their schemas.

## Files created this session

- `schemas/{curriculum-objective,question-item,generator-module,misconception,assessment-blueprint,source-record}.schema.json`
- `docs/{ARCHITECTURE,DATA_MODEL,GENERATOR_STANDARD,VALIDATION_STANDARD,DIFFICULTY_MODEL,MISCONCEPTION_MODEL,ANSWER_EQUIVALENCE,ACCESSIBILITY_STANDARD,EXPORT_STANDARD,TESTING_STRATEGY,SECURITY_AND_PRIVACY,ROADMAP}.md`
- `docs/GENERATOR_SPEC_arithmetic_sequences.md`
- `curriculum/objectives/SPI.IBDPAASL.SEQSER.ARITH.json`
- `core/misconceptions/sequences.json`
- `oracle/spi_oracle/{__init__,seeded_random,sequences}.py`
- `oracle/tests/test_sequences.py`, `oracle/run_oracle.py`, `oracle/check_conformance.py`
- `oracle/golden/{prng_anchors.json,arithmetic_sequences.golden.json}`
- Repository directory scaffold (`apps/`, `core/`, `domains/`, `renderers/`, `exporters/`, `tests/`, etc.)
- `DECISION_LOG.md` updated.

## Files changed

- `docs/DECISION_LOG.md`, `docs/CURRENT_STATE.md`.

## Known problems / constraints

- **No JavaScript runtime installed** (Decision #8). The TypeScript production layer, Vitest suite, bundler, and standalone-HTML apps cannot be built/run until **Node.js LTS** is installed. The Python oracle is the executable proof in the meantime.
- `jsonschema` Python package is not installed; a dependency-free conformance checker is used instead (production uses Ajv in TS).
- Git is available but the workspace is not yet a git repository. No commits made (awaiting owner request). Recommend `git init` with a `.gitignore` excluding the large read-only source archives/PDFs/media.
- Source rights: AA SL slice content is academy-owned/original; Oxford teacher notes remain reference-only.

## Failing tests

None. 18/18 unit/property tests pass; 0/20,000 invalid items in the sweep.

## Pending review (owner)

- Mathematics/curriculum review of the arithmetic-sequences slice (item phrasing, difficulty bands, distractor pedagogy) to advance items past `machine-validated`.
- Confirm the production-runtime direction (see Next).

## Commands

```bash
# Python oracle (from the project root):
python oracle/tests/test_sequences.py     # unit + property tests (18)
python oracle/run_oracle.py               # golden vectors + 10,000-seed sweep
python oracle/check_conformance.py        # schema conformance of instances + live items
# Optional smaller sweep:  SPI_SWEEP=2000 python oracle/run_oracle.py

# TypeScript (PowerShell; refresh PATH first so node is visible):
$env:Path = [System.Environment]::GetEnvironmentVariable('Path','Machine') + ';' + [System.Environment]::GetEnvironmentVariable('Path','User')
npm test                                   # node --test over core/** and domains/** (16 tests)
```

## Geometric generator v1.1.0 (curriculum-review REVISE corrections)

Applied the owner's geometric review. Separated **interactionType** (free-response/multiple-choice) from **answer.type** (`integer`/`exact-rational`); canonical is always normalized `{num,den}`; added `answer.accepts` + an exact-rational checker (`core/answer-checking/rational-checker.ts`). Schema `question-item` gained `interactionType`, `exact-rational`, and an answer-type/value consistency rule. Sum-to-infinity uses geometric **series** wording; `find_n` solutions show step-by-step exponent reasoning. Validator adds answer-type-consistency, **find_r real-solution-set uniqueness**, and **term-index uniqueness** (`domains/sequences/geometric-uniqueness.ts` + oracle mirror) with edge-case tests (odd/even exponents, ± quotients, fractional/negative ratios, no-real / two-real, r=0/1/-1). Released as **v1.1.0** (v1.0.0 preserved); golden/parity/schema fixtures, review pack (new fields), and sample exports regenerated. All tests pass (TS 72, Python geometric 23 + arithmetic 19, both 10k sweeps 0 invalid, conformance). Browser-verified (series wording, 6-step find_n, interaction/answer-type shown, new checks PASS, no console errors).

## Geometric sequences generator v1.0.0 (curriculum-approved, second family)

Built and released `gen.sequences.geometric` v1.0.0 after owner approval. Five curriculum-approved objectives (`SPI.IBDPAASL.SEQSER.GEO.{NTH_TERM,SUM_N,COMMON_RATIO,TERM_INDEX,SUM_INFINITE}.01`). Introduced an exact-rational type `core/exact-math/rational.ts` (mirrors Python `Fraction`) for fractional answers. Tasks: nth_term, sum_n (MC + free-response), find_r, find_n_for_value, sum_infinite (free-response). Misconception registry (oracle + TS) with semantic-agreement validation. Oracle-first then TS with **byte-for-byte parity** (golden + 300-entry fixture); 10,000-seed sweep 0 invalid; curriculum-review pack `docs/review/geometric_sequences_review_pack.md` (38 items, all 7 rules). Studio now has a **generator registry** offering both families; browser-verified (generator switch, fraction answers e.g. 16/5, MC→free-response fallback for sum_infinite, validation PASS, no console errors). All tests pass (TS 57, Python arithmetic 19 + geometric 15, both 10k sweeps 0 invalid, conformance). Generated items begin at `machine-validated`; never auto-published.

## Generator v1.1.0 (curriculum-approved)

Owner approved the objective split (final wording). Added curriculum-approved micro-objectives `SPI.IBDPAASL.SEQSER.ARITH.COMMON_DIFF.01` (find_d) and `...TERM_INDEX.01` (find_n_for_value), prerequisite `...NTH_TERM.01`; updated NTH_TERM.01/SUM_N.01 wording; remapped the reverse tasks. Generator released as **v1.1.0** (v1.0.0 and v1.0.1 preserved unchanged). Golden/parity fixtures + review pack regenerated. The spec `docs/GENERATOR_SPEC_arithmetic_sequences.md` is **curriculum-approved at v1.1.0**. All tests pass (TS 47, Python 19, sweep 0 invalid, conformance, exports); browser-verified (objectives remapped, version 1.1.0, validation PASS, no console errors). Generated items still begin at `machine-validated`; never auto-published.

## Generator v1.0.1 (curriculum-review REVISE corrections)

Applied the owner's review corrections: distractors are now distinct, formula-backed misconceptions from a canonical registry (`domains/sequences/misconceptions.ts` + `oracle/spi_oracle/misconceptions.py`) with deterministic parameter regeneration when a clean set isn't available; new `MISC.SEQ.FORGOT_FIRST_TERM`; renamed `MISC.SERIES.CONSTANT_TERMS`→`CONSTANT_LAST_TERM`; new `MISC.SERIES.CONSTANT_FIRST_TERM`. Validator v1.1.0 adds distractor semantic-agreement (recompute each distractor from its formula; value/rationale/feedback must agree) + distinct-misconception. Clarified `find_n_for_value` wording; calculator policy `calculator-not-required` (schema enum updated). Generator bumped to **v1.0.1**; golden/parity fixtures + review pack regenerated. All tests pass (TS 47, Python 19, sweep 0 invalid, conformance). The objective split for reverse tasks is **proposed** in `docs/CURRICULUM_OBJECTIVE_PROPOSAL.md` (awaiting approval; would be v1.1.0).

## Next recommended task

Both sequence families (arithmetic v1.1.0, geometric v1.1.0) are curriculum-approved. The next phase is **Foundation Readiness & Generator SDK design** — NOT another sequence family. Recommended first steps:
1. **Generator SDK design**: formalize the generator contract (describe/generate/solve/validate/distractors/solution/render/serialize) into a reusable SDK so new families are configuration + math, not boilerplate; carry the oracle-first → byte-for-byte parity → 10,000-seed gate into the SDK.
2. **Resolve TD-1** (`TECH_DEBT.md`): introduce `config.interactionType` + `answer.type`, mapping the legacy `answerType` for full backward compatibility (no fixture regeneration).
3. Foundation hardening: move renderers to `/renderers`, add an `axe-core` browser a11y scan, general JSON-schema validation in TS (Ajv), and a curriculum-graph integrity check (prerequisite acyclicity, objective ID coverage).

Explicitly NOT now (per owner): another sequence family, the `sum_infinite` MC variant, or a third generator family.

See `ROADMAP.md`. The arithmetic-sequences slice still awaits your mathematics/curriculum review to advance items past `machine-validated`.
