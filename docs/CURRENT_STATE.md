# Current State

Last updated: 2026-06-20.

## Current phase

Phase 1 — Foundation and First Vertical Slice. Phase 0 (source audit) is complete. **Node.js v24.17.0 is now installed**, the TypeScript production layer has begun, and the deterministic core + first generator are proven to match the Python oracle byte-for-byte.

## TypeScript production layer (this session, post Node.js install)

- Project config: `package.json`, `tsconfig.json`, `vitest.config.ts`, `.gitignore`.
- Ported to TypeScript and **tested with Node's built-in runner (offline, no `npm install`)**:
  - `core/seeded-random/mulberry32.ts` — cross-language PRNG, asserted equal to the oracle's committed anchors.
  - `core/serialization/canonical.ts` — canonical JSON serializer matching the oracle's Python serialization.
  - `domains/sequences/arithmetic.ts` — full generator, asserting **byte-for-byte parity** with `oracle/golden/arithmetic_sequences.golden.json`.
- `npm test` (= `node --test` over `core/**` and `domains/**`) → **16/16 TS tests pass**, including cross-language PRNG parity and golden-vector parity.
- Oracle updated with a portable `_round3` so difficulty floats serialize identically in Python and JS; golden vectors regenerated; Python suite still 18/18, sweep still 0 invalid.

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

## Next recommended task

The TypeScript foundation (PRNG, canonical serializer, first generator) is proven against the oracle. Recommended next increments, in order:
1. **Schema validation + answer-checker in TS** (`core/validation`, `core/answer-checking`) mirroring the oracle's `validate`, so generated items are gated in TypeScript too.
2. **Renderer + Generator Studio MVP**: KaTeX rendering of `prompt`/`solution`, an IndexedDB `BankStore`, and a standalone offline-HTML export of a worksheet + answer key.
3. **Broaden the domain**: geometric sequences, sigma notation, arithmetic/geometric series — each oracle-first then TS, with golden parity.
4. One-time `npm install` (online) to enable `tsc` typecheck and add Vitest for the future DOM/app layer.

See `ROADMAP.md`. The arithmetic-sequences slice still awaits your mathematics/curriculum review to advance items past `machine-validated`.
