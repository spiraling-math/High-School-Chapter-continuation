# Generator Standard

Status: Phase 1 draft. Last updated: 2026-06-20.

Every question generator is a **versioned module** implementing a common contract. This document defines that contract. It applies identically to the Python oracle reference implementation and the TypeScript production implementation.

## 1. The generator contract

A generator exposes these operations:

| Operation | Signature (conceptual) | Must be pure/deterministic? |
| --- | --- | --- |
| `describe()` | `() → GeneratorModuleDescriptor` | Yes |
| `generate(seed, config)` | `(uint32, Config) → QuestionItem` | Yes (seed-deterministic) |
| `solve(params)` | `(Params) → Answer` | Yes |
| `validate(item)` | `(QuestionItem) → ValidationResult` | Yes |
| `generateDistractors(item)` | `(QuestionItem) → Distractor[]` | Yes |
| `generateSolution(item)` | `(QuestionItem) → Solution` | Yes |
| `render(item, mode)` | `(QuestionItem, RenderMode) → string` | Yes (given item) |
| `serialize(item)` | `(QuestionItem) → canonical JSON string` | Yes |

`describe()` returns metadata conforming to `generator-module.schema.json`. All operations except `render` are DOM-free and live in `/domains`. `render` lives in or calls `/renderers`.

## 2. Determinism rules

- The **only** randomness source is the injected `mulberry32` PRNG seeded by `seed`. No `Math.random()`, no wall-clock, no ambient entropy.
- `generate(seed, config)` called twice with identical arguments must produce **byte-identical** `serialize(item)` output.
- Parameter selection order from the PRNG is fixed and documented per generator (so a version bump is required if the draw order changes, since it alters output for a given seed).

## 3. Separation of generate / solve / validate

These three must be **independent computations**, not the same code reused:

- `generate` constructs the question, typically **backwards** from an intended answer or from chosen parameters.
- `solve` computes the canonical answer from `params` by the generator's **canonical method** (e.g. closed form).
- `validate` re-derives the answer by an **independent method** (e.g. iterative construction) and asserts agreement. Reusing `solve` inside `validate` is prohibited for the core correctness check (Principle 4).

The descriptor must state both `canonicalMethod` and `independentValidationMethod`, and they must genuinely differ.

## 4. Construct-backwards strategy

Generators encode mathematical structure and build valid instances, rather than number-swapping copyrighted questions:

| Domain | Strategy |
| --- | --- |
| Arithmetic / number | Constrained exact-number generation within declared ranges. |
| Fractions | Reduced rational arithmetic (exact). |
| Algebra | Choose the solution first, then construct the equation. |
| Simultaneous equations | Choose the intended solution, then form consistent equations. |
| Geometry | Construct valid coordinates/constraints, then derive measures and the diagram. |
| Trigonometry | Control angles/sides/exact values and rounding up front. |
| Probability | Build a complete valid sample space/distribution first. |
| Statistics | Generate a seeded dataset with intended properties, then ask about it. |
| Combinatorics | Enumerate small cases and verify formulas. |
| Calculus | Construct functions from intended derivatives/antiderivatives. |
| Linear algebra | Construct matrices from intended rank/determinant/eigenvalues/solution. |

## 5. Parameter spec and config

- `describe().parameterSpec` declares every tunable parameter with type and constraints (`min`, `max`, `nonZero`, `enumValues`).
- `generate` must only ever emit params inside the spec. `validate` (and a dedicated invalid-parameter test) rejects out-of-spec configs.
- `config` selects the objective, target difficulty band, allowed task(s), ranges, and answer type. It must validate against `parameterSpec`.

## 6. Difficulty

- Generators expose difficulty via `difficultyControls`, mapping config/params to difficulty axes.
- `generate` populates the item's `difficulty.axes` (0..1 per axis) and the derived `overallBand`. Difficulty is multidimensional — never "bigger numbers" alone. See `DIFFICULTY_MODEL.md`.

## 7. Distractors

- `generateDistractors` derives each distractor from a **named misconception** (`distractorRules` in the descriptor).
- Hard requirements (enforced by `validate`): distractors are unique; no distractor equals the canonical answer (across any accepted equivalent form); each distractor carries a `misconceptionId` where one exists.
- If a misconception rule coincidentally yields the correct answer for a given seed, the generator must substitute an alternative rule or the validator fails the item (and the seed is logged).

## 8. Solution

- `generateSolution` returns a **structured** solution (`solution.steps[]`), not an opaque paragraph. Steps carry transformation, explanation, rule/theorem, intermediate result, dependencies, and optional marks and detail level.
- Solutions are derived from the same verified mathematical structure as the answer, but are validated separately (the final step's result must equal `answer.canonical`).

## 9. Rendering

- `render(item, mode)` supports modes: `answer-only`, `concise`, `full`, `hints`, `mark-scheme`, `alternative`, plus presentation modes `student` and `teacher`.
- Math is rendered with KaTeX from LaTeX source; diagrams are SVG generated from `params`. The prompt must never contain the answer (no leakage), checked by `validate`.

## 10. Serialization

- `serialize(item)` emits canonical JSON: UTF-8, stable key ordering, conforming to `question-item.schema.json`. This is the form hashed for `contentHash` and compared in reproducibility tests.

## 11. Versioning rules

- Semantic version in `generatorVersion`.
- **Any change that alters output** for an existing `{seed, config}` — generation logic, parameter draw order, distractor rules, solution wording that is part of serialized data — requires at least a new minor/major version. Bug-fix versions that change output still bump version and require new golden vectors.
- A published version is immutable. Items record the version that produced them.

## 12. Definition of "stable"

A generator may be marked `status: stable` only when:

1. All required operations implemented and DOM-free where specified.
2. Unit, property, reproducibility, edge-case, invalid-parameter, answer-equivalence, distractor, rendering, accessibility, and performance tests pass (see `TESTING_STRATEGY.md`).
3. A **≥10,000-seed sweep** produces **zero** invalid items; any historical failing seeds are recorded and fixed.
4. A reviewed **golden set** (fixed seeds) is checked into version control.
5. The TS implementation's golden JSON vectors match the Python oracle.
6. `describe()` is in sync with the implementation.

## 13. Checklist for a new generator

- [ ] Objective(s) defined and approved in the curriculum graph.
- [ ] Descriptor (`describe()`) authored and schema-valid.
- [ ] `canonicalMethod` and an **independent** `independentValidationMethod` defined and distinct.
- [ ] Parameter spec with ranges/constraints.
- [ ] Distractor rules each mapped to a misconception.
- [ ] Structured solution generator.
- [ ] Difficulty axis mapping.
- [ ] Accessibility fields populated (`spokenMath`, alt text for any visual).
- [ ] Full test suite + 10,000-seed sweep + golden set.
- [ ] Oracle ↔ production cross-check.
