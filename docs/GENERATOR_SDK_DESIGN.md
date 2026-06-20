# Generator SDK Design

Status: Phase "Foundation Readiness & Generator SDK" — initial design. Last updated: 2026-06-20.

Two generator families (arithmetic v1.1.0, geometric v1.1.0) are curriculum-approved.
They were hand-built but share a large, repeated structure. The Generator SDK
turns that repeated structure into a small, reusable, well-tested surface so that
**a new generator family is "configuration + mathematics", not boilerplate** —
while keeping every non-negotiable principle (deterministic maths, reproducibility,
independent verification, parity, accessibility, traceability).

This document is the design. It does not change any approved generator's output;
the existing generators are the conformance reference the SDK is validated against.

## 1. Goals and non-goals

**Goals**
- One formal generator contract that the platform, Studio, exporters, and tests
  depend on (not on a specific family).
- Reusable, output-neutral building blocks: seeded RNG, canonical serialization,
  exact rational, misconception registry, distractor selection, difficulty band,
  the parameter-redraw harness, the validation check library, and the standard
  stability gate.
- A single "stability gate" runner that any generator passes before it is called
  stable: ≥10,000-seed sweep with zero invalid items, reproducibility,
  cross-language parity, semantic distractor agreement.
- A clear, repeatable workflow to add and get a generator curriculum-approved.

**Non-goals (now)**
- Re-implementing or changing the approved generators' serialized output.
- Building another generator family (explicitly deferred by the owner).
- A plugin/dynamic-loading system; the registry is static for now.

## 2. The generator contract

A generator is a versioned module implementing:

| Operation | Signature (conceptual) | Pure / deterministic |
| --- | --- | --- |
| `describe()` | `() → GeneratorDescriptor` | yes |
| `generate(seed, config)` | `(uint32, Config) → Item` | yes (seed-deterministic) |
| `solve(params)` | `(Params) → Answer` | yes |
| `validate(item)` | `(Item) → ValidationResult` | yes (independent of solve) |
| `generateDistractors(params)` | `(Params) → Distractor[] | null` | yes |
| `generateSolution(params)` | `(Params) → Solution` | yes |
| `render(item, mode)` | `(Item, RenderMode) → string` | yes |
| `serialize(item)` | `(Item) → canonical JSON` | yes |

The **runtime-facing** surface the SDK formalizes first (and what the Studio,
exporters, and harness consume) is the minimal `GeneratorModule`:

```ts
interface GeneratorModule {
  readonly id: string;            // gen.<domain>.<family>
  readonly version: string;       // semver; output-affecting change ⇒ new version
  readonly label: string;
  readonly tasks: GeneratorTaskInfo[];   // { value, label, mc }
  generate(seed: number, config: GenConfig): Item;
  validate(item: Item): GenValidationResult;
  serialize(item: Item): string;
}
```

Implemented in `core/sdk/generator-module.ts`. Both approved generators satisfy it
(verified by the harness test).

## 3. The canonical answer model (forward standard)

The SDK standard, established by geometric v1.1.0, **separates interaction from
mathematics**:

- `item.interactionType`: `free-response` | `multiple-choice` (how the student answers).
- `item.answer.type`: `integer` | `exact-rational` | … (the mathematical type).
- `item.answer.canonical`: normalized value. For integer/exact-rational it is
  `{ num, den }` with `den ≥ 1` (integers have `den = 1`).
- `item.answer.accepts`: which equivalent input forms the checker accepts
  (`fraction` always; `decimal` when terminating and permitted; `mixed` when enabled).

**Grandfathering.** Arithmetic v1.1.0 predates this model (it uses
`answer.type ∈ {integer, multiple-choice}` with a bare-integer canonical and no
`interactionType`). It is **approved and immutable**; it stays as-is until a future
version bump that would require re-approval. New generators MUST use the forward
model. The shared schema accepts both; the answer-type/value **consistency** rule
only constrains object-encoded canonicals.

## 4. Config and TD-1 (legacy `answerType`)

Today's config selector is `answerType ∈ {"integer", "multiple-choice"}`, where
`"integer"` actually means free-response. The SDK introduces a clear resolver
(`core/sdk/interaction.ts`):

```
resolveInteractionType(config):
  config.interactionType                       if present
  "multiple-choice"   if config.answerType == "multiple-choice"
  "free-response"     otherwise  (answerType "integer" or unset)
```

This is **back-compatible**: the mapping is 1:1 and deterministic, so existing
seeds, fixtures, and bank `genConfig` reproduce byte-for-byte. See `TECH_DEBT.md`
TD-1 for the phased migration. The SDK consumes `resolveInteractionType`; approved
generators are migrated only at a future version bump.

## 5. Reusable building blocks (already present, to be unified under the SDK)

| Block | Location | Notes |
| --- | --- | --- |
| Seeded RNG (mulberry32) | `core/seeded-random` | cross-language; the only randomness source |
| Canonical serialization | `core/serialization` | stable key order; parity-critical |
| Exact rational | `core/exact-math/rational.ts` | mirrors Python `Fraction` |
| Exact-rational checker | `core/answer-checking/rational-checker.ts` | accepts equivalent forms |
| Misconception registry | `domains/sequences/*-misconceptions.ts` | formula-backed; SDK pattern to generalize |
| Uniqueness validators | `domains/sequences/geometric-uniqueness.ts` | reverse-task solution sets |
| Difficulty band function | per-generator | candidate to centralize in `core/difficulty` |
| Parameter-redraw harness | per-generator `generate` loop | candidate to centralize in the SDK |
| Validation check library | per-generator `validate` | candidate to centralize common checks |

The SDK's job over this phase is to lift the bottom four rows into shared,
output-neutral helpers that a new generator composes.

## 6. The stability gate (one runner for every generator)

`core/sdk/harness.ts` provides `runStabilityGate(gen, opts)`, which any
`GeneratorModule` passes before being marked stable:

1. **Sweep**: for each seed in `[1..N]` and each interaction mode, `generate` then
   `validate`; **zero** invalid items allowed; record failing seeds.
2. **Reproducibility**: `serialize(generate(seed))` is identical on a re-run.
3. **Coverage**: every task appears; difficulty bands vary.
4. (Cross-language parity and the full 10,000-seed sweep remain in the oracle
   drivers; the harness runs a fast in-suite subset and the same logic at scale.)

The harness is validated by running **both approved generators** through it in a
test — proving the SDK surface works without changing any output.

## 7. Versioning and the approval workflow

Unchanged from the established gates, now codified as the SDK lifecycle:

1. **Propose**: objectives, task coverage, difficulty model, misconceptions,
   generator contract → owner approval (no code before approval).
2. **Build oracle-first** (Python, exact arithmetic): generate/solve/validate/
   distractors/solution; pass the stability gate (≥10,000 seeds, zero invalid).
3. **Port to TypeScript**; prove **byte-for-byte parity** (golden + fixture).
4. **Curriculum-review pack** → owner review.
5. **Approve & tag**: record in `APPROVED_VERSIONS.md`; git tag the reference
   implementation. Any output-affecting change ⇒ new version + re-approval.
   Items always begin at `machine-validated`; no auto-approval/publication.

## 8. Adding a generator (target developer experience)

```
1. Define objectives (curriculum/objectives/*.json) and get them approved.
2. Define a misconception registry (formula-backed) for the family.
3. Implement the oracle generator using SDK helpers (RNG, rational, redraw,
   check library, band function).
4. runStabilityGate at 10,000 seeds → zero invalid.
5. Port to TS; assert golden + fixture parity.
6. Register in the generator registry; the Studio, exporters, and bank work
   automatically (they depend only on GeneratorModule).
7. Produce the review pack; obtain approval; tag.
```

## 9. Module layout (this phase)

```
/core/sdk
  generator-module.ts   # the formal contract + shared types (this phase)
  interaction.ts        # TD-1 resolver (this phase)
  harness.ts            # stability-gate runner (this phase)
  (future) item-builder.ts, distractors.ts, checks.ts, difficulty.ts
/core/curriculum
  graph-check.ts        # curriculum-graph integrity (this phase)
```

## 10. Risks and mitigations

- **Refactoring approved generators could change output.** Mitigation: do not
  refactor approved generators in this phase; the SDK is validated *against* them.
  Future adoption happens only at a version bump, guarded by the golden/parity
  fixtures.
- **Two answer models coexist (legacy arithmetic vs forward).** Mitigation:
  documented grandfathering; schema accepts both; new generators use the forward
  model only.
- **Centralizing helpers risks subtle drift.** Mitigation: the harness + golden +
  parity fixtures detect any byte change immediately.
