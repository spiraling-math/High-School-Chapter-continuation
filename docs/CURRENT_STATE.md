# Current State

Last updated: 2026-06-20.

## Current phase

**Two generator families curriculum-approved.** arithmetic v1.1.0 and **geometric v1.1.0** are curriculum-approved (see `APPROVED_VERSIONS.md`, `DECISION_LOG.md` #24). Generator Studio offers both, with the IndexedDB bank and offline exports. Node.js v24.17.0 installed.

**Next phase: Foundation Readiness & Generator SDK design** (not another sequence family). The first SDK task is recorded tech debt TD-1 (`answerType` → `interactionType` / `answer.type`, back-compatible; see `TECH_DEBT.md`). Do not implement another sequence family, the sum-to-infinity MC variant, or a third generator family until directed.

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
