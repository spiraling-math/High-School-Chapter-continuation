# Generator SDK Foundation — Checkpoint

Date: 2026-06-21. Phase: **Foundation Readiness & Generator SDK** (technical, not
curriculum). This checkpoint records what the SDK foundation now provides, what
remains domain-specific, the contracts and policies a new generator must follow,
and whether the foundation is ready to scaffold the first non-sequence family
(linear equations).

This was a **technical** phase. No new mathematics generator was added. Both
approved families — `gen.sequences.arithmetic` v1.1.0 and
`gen.sequences.geometric` v1.1.0 — produce **byte-for-byte identical output**;
every golden and parity fixture is unchanged; both 10,000-seed sweeps remain
0-invalid.

---

## 1. Reusable SDK components completed

| Area | Module | What it provides |
| --- | --- | --- |
| Generator contract | `core/sdk/generator-module.ts` | `GeneratorModule` interface, `GenConfig`, `InteractionType`, `AnswerType`, `CanonicalRational`, `interactionModesFor`. |
| Interaction resolution | `core/sdk/interaction.ts` | `resolveInteractionType` (canonical `interactionType`, legacy `answerType` normalized, **conflicts rejected**), `legacyAnswerType`. |
| Multiple-choice assembly | `core/sdk/multiple-choice.ts` | `assembleMultipleChoice` — deterministic option assembly (single seeded shuffle, A–E labels, preserved IDs/metadata/rationale). Encoding is injected, so integer and exact-rational reuse it. |
| Universal validation predicates | `core/sdk/checks.ts` | Domain-independent boolean checks: answer/solution agreement, prompt-leakage, exactly-one-correct, distractor uniqueness, accessibility field, interaction-type validity, answer-type/value consistency, provenance completeness, version fields. |
| Stability gate | `core/sdk/harness.ts` | `runStabilityGate` — N-seed sweep + reproducibility spot-check; run against both generators. |
| Generator registry | `core/sdk/sequence-registry.ts` | Single source of the available generators; the Studio re-exports it. |
| Runtime schema validation | `core/schema/runtime-validate.ts` + `core/schema/compiled/*.mjs` | `validateItem` / `assertValidItem` against the JSON Schema, via a **build-time precompiled standalone Ajv validator** (no runtime codegen, no network). Rich errors: schema path, field, expected, received, item id, generator id. |
| Difficulty band | `core/difficulty/band.ts` | `round3`, `bandFromScore` (+ Python mirror) shared by both generators. |
| Curriculum-graph integrity | `core/curriculum/graph-check.ts` | Duplicate-ID, acyclicity, prerequisite-resolution checks. |
| Accessibility gate | `apps/generator-studio/a11y.test.ts` | axe-core + jsdom gate (dev/test only); WCAG-AA token-contrast guard. |

## 2. Domain-specific components retained (intentionally NOT centralized)

These stay inside each generator because they encode the family's mathematics:

- **Misconception registries and distractor formulas** — `domains/sequences/misconceptions.ts`, `geometric-misconceptions.ts` (+ oracle mirrors). Distractors are derived from named misconceptions, never random.
- **Independent validators** — `domains/sequences/validate.ts` (arithmetic) and the `validate()` in `geometric.ts`. They compose the universal predicates but keep their own domain checks: arithmetic/geometric **iterative-agreement**, `find_r` real-solution-set **uniqueness**, **term-index uniqueness**, convergence (`|r|<1`), and parameter-domain maths. Each validator keeps its own check IDs, ordering, and messages.
- **Answer encoding** — integer (bare number) vs exact-rational (`{num, den}` normalized) including `answer.accepts` and the exact-rational checker (`core/answer-checking/rational-checker.ts`).
- **Uniqueness helpers** — `domains/sequences/geometric-uniqueness.ts` (+ oracle mirror).
- **Prompt/solution wording** — task phrasing and step-by-step reasoning.

The validation library is deliberately **not one large universal validator**: each
generator owns a `validate()` that calls shared predicates.

## 3. Final generator module contract

A generator family provides (see `core/sdk/generator-module.ts`):

```
id: string                      // e.g. "gen.sequences.geometric"
version: string                 // semver; output-affecting change ⇒ new version
label: string
tasks: { value, label, mc }[]   // selectable tasks; mc = MC-capable
generate(seed: number, config: GenConfig): Item      // deterministic
validate(item): { status, validatorVersion, checks[] } // INDEPENDENT method
serialize(item): string         // canonical JSON (sorted keys, no whitespace)
```

Authoring discipline (unchanged): **oracle-first** (Python reference) → TypeScript
mirror proven **byte-for-byte** against committed golden + parity fixtures →
**≥10,000-seed** stability sweep with 0 invalid + reproducibility + parity.

## 4. Canonical configuration model

```
config.interactionType : "free-response" | "multiple-choice"   // CANONICAL
config.answerType      : legacy input only — normalized at the boundary
item.answer.type       : "integer" | "exact-rational"          // mathematical
item.answer.canonical  : integer (bare) or { num, den } (den ≥ 1)
```

- New code uses `interactionType`. `answerType` remains accepted and is normalized
  by `resolveInteractionType`.
- If **both** are supplied and **agree**, accepted; if they **conflict**, rejected
  (throws).
- The mathematical answer classification (`answer.type` / `canonicalAnswer.type`)
  is separate from interaction and is never collapsed into it.

## 5. Compatibility & migration policy

- **Seeds reproduce byte-for-byte.** The legacy→canonical mapping is 1:1 and
  deterministic, so every existing seed, golden/parity fixture, and stored bank
  item reproduces identically. No approved fixtures were regenerated.
- **Bank records.** `BankRecord` now carries canonical `interactionType`;
  `makeRecord` writes it (schemaRev 3). `genConfig` is retained as the **preserved
  original configuration** used for exact reproduction.
- **IndexedDB migration.** `DB_VERSION = 3`. Schema migrations (index creation) are
  separated from a **single idempotent data-backfill** pass that normalizes
  `tags`/`archived`/`interactionType`; running it repeatedly is a no-op. Covered by
  v1→current, v2→v3, idempotency, and canonical-only tests.
- **JSON import** normalizes legacy/imported records via the same idempotent
  `ensureInteractionType`, then runs schema + math + reproduction integrity checks.

## 6. Runtime validation boundaries

Structural schema validation (precompiled Ajv) runs at every boundary where item
data enters or leaves a trust zone. It **never repairs** mathematically meaningful
data — invalid data is surfaced, not silently corrected.

| Boundary | Where |
| --- | --- |
| Generated item → bank storage | `IndexedDBBankStore.put` (`assertValidItem`) |
| JSON import | `importBankJson` (schema + math + reproduction) |
| JSON export | `exportBankJson` |
| Worksheet / answer-key / worked-solution export assembly | each exporter entry |

The IndexedDB structural migration only touches **record metadata** (never item
fields), so `put` and import are the validation boundaries for incoming item data.

Offline guarantee: the validator is **build-time precompiled to a standalone
module** (no `new Function`/eval, no network). Ajv/axe-core/jsdom are
**dev/test-only**; the production bundle reports `external references: none` and
contains no Ajv/axe/jsdom code.

## 7. Accessibility-test coverage

`apps/generator-studio/a11y.test.ts` requires **zero critical/serious** axe
violations on: the Generator Studio shell + **question-bank table** (the real app
mounted in jsdom and driven through generate + save), the question-preview,
worked-solution, and validation views, and the student-worksheet, answer-key, and
worked-solution exports. A deterministic WCAG-AA **token-contrast** guard backs the
one documented exception (see below).

Issues found and fixed by the gate:
- the JSON-import file input had no accessible name → `aria-label` added;
- muted text `--ink-faint` was 4.47:1 on white → darkened to `#67738f` (≥ 4.5:1).

**Documented exception:** `color-contrast` needs layout/canvas and cannot run in
jsdom; it is disabled in the jsdom gates and covered by (a) the token-contrast unit
guard and (b) an in-browser axe pass — verified live with **0 violations of any
impact**.

## 8. Remaining technical debt

- **TD-1 is resolved** for the current scope: `interactionType` is canonical;
  conflicts rejected; bank + migration + import normalized and versioned. Residual:
  the descriptor/schema still list `answerType` as an accepted input for
  backward-compatibility (intentional; read-support retained).
- Only the **question-item** schema is precompiled today. Other schemas
  (assessment-blueprint, etc.) can be added to `scripts/compile-schemas.mjs` when an
  assessment-assembly boundary needs them.
- Renderers still live under `apps/generator-studio/render` rather than a top-level
  `/renderers` (cosmetic; no functional impact).

## 9. Blockers to scaffolding a new generator

**None.** A new family needs only: a Python oracle, a TS module implementing the
contract, its misconception registry + independent validator (composing the shared
predicates), curriculum objectives, and golden/parity fixtures. The shared MC
assembly, universal checks, stability harness, runtime schema validation,
registry, difficulty band, and a11y gates are all reusable as-is.

## 10. Readiness for the linear-equations pilot

**Ready.** The foundation supports a new family as "math + config + fixtures"
without further SDK work. Two non-blocking notes for that pilot:

1. Linear-equation answers may need answer types beyond integer/exact-rational
   (e.g. `algebraic-expression`); the schema already enumerates them and the
   universal `answerTypeConsistent` predicate is permissive for other types, but a
   family-specific checker/validator will be required.
2. Starting the pilot is a **curriculum** decision (objectives + approval), which is
   outside this technical phase and awaits owner direction.

---

### Verification at this checkpoint (executed)

- `npm run typecheck` → clean.
- `npm test` → **121 TS tests pass** (incl. SDK checks, interaction resolver,
  migration v1→v3 + idempotency, JSON round-trip + import normalization, runtime
  schema validation, and the axe-core a11y gates).
- `python oracle/tests/test_sequences.py` → **19 pass**.
- `python oracle/run_oracle.py` / `run_geometric.py` → both **10,000-seed sweeps,
  0 invalid**; arithmetic reproducibility OK.
- Fixture drift (`git status oracle/golden`) → **none**.
- `python oracle/check_conformance.py` → **all conformance checks pass**.
- `npm run build:studio` → **`external references: none`** (1148 KB single file);
  `npm run build:samples` → offline-safe exports.
- Browser smoke → generate/save/tab-switch render; bank persists; **no console
  errors**; live axe **0 violations**.
