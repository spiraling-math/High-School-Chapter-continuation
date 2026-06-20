# Foundation Readiness Assessment

Status: Phase "Foundation Readiness & Generator SDK". Last updated: 2026-06-21.

An honest assessment of whether the foundation is ready to scale from two
curriculum-approved generators to many, across domains and stages. Marks are:
**Solid** (production-ready), **Partial** (works, needs generalization/hardening),
**Missing** (not yet built).

## Scorecard

| Capability | Status | Evidence / gap |
| --- | --- | --- |
| Deterministic seeded RNG (cross-language) | **Solid** | mulberry32 in core + oracle; parity-tested. |
| Canonical serialization (parity) | **Solid** | `core/serialization`; byte-for-byte Python/TS. |
| Exact arithmetic | **Solid** | `core/exact-math/rational.ts` (Fraction parity); integers throughout arithmetic. |
| Independent verification | **Solid** | iterative/uniqueness checks distinct from solve; enforced in validators. |
| 10,000-seed stability gate | **Solid** | oracle drivers (0 invalid) + SDK `harness.ts` runs any generator. |
| Generator contract (formal) | **Partial → Solid** | `core/sdk/generator-module.ts` now formalizes it; both generators conform. |
| Generator registry (single source) | **Solid** | unified in `core/sdk/sequence-registry.ts`; Studio re-exports it. |
| Misconception model (formula-backed) | **Partial** | per-family registries proven; not yet a generalized SDK helper. |
| Difficulty model | **Partial** | per-generator band functions; should centralize in `core/difficulty`. |
| Answer model (interaction vs maths) | **Partial** | forward model in geometric v1.1.0; arithmetic grandfathered; legacy `answerType` config (TD-1). |
| Answer checking | **Partial** | exact-rational checker built; other types (surd, algebraic, set, …) not yet. |
| Validation check library | **Partial** | rich per-generator checks; common checks not yet extracted to the SDK. |
| Curriculum graph integrity | **Solid (for current set)** | `core/curriculum/graph-check.ts` (no dup ids, acyclic, prereq resolution); tested. |
| Schema conformance (runtime) | **Partial** | Python conformance checker covers items/objectives/misconceptions/descriptors; no TS-side Ajv gate yet. |
| Bank storage + migrations | **Solid** | IndexedDB + versioned migrations; tested via fake-indexeddb. |
| Offline exports | **Solid** | worksheet/answer-key/solutions/JSON; no external loads; tested + browser-verified. |
| Rendering | **Partial** | KaTeX html+MathML; renderers live under `apps/.../render` and should move to `/renderers`. |
| Accessibility | **Partial** | non-color indicators, MathML, keyboard, skip link, reduced-motion, print; no automated `axe-core` gate yet. |
| Versioning & approval workflow | **Solid** | immutable versions, tags, `APPROVED_VERSIONS.md`, machine-validated-first lifecycle. |
| Traceability | **Solid** | every item links objective/generator/version/seed/params/validation/provenance. |
| Security/offline posture | **Solid** | no secrets in bundles/exports; no CDN; build asserts no external loads. |

## Strengths (ready to build on)

- The **deterministic, parity-verified, independently-validated** core is real and
  proven at scale (two families, 10,000-seed sweeps, byte-for-byte parity).
- A **single generator contract and registry** now exist; the Studio, exporters,
  bank, and the stability harness depend only on `GeneratorModule`.
- A **repeatable approval workflow** (propose → oracle-first → parity → review pack
  → approve → tag) is established and documented.

## Gaps to close before broad scale-out

1. **Centralize the repeated generator machinery** into SDK helpers (item builder,
   distractor selection, common validation checks, difficulty band) so new
   families are math + config. (Output-neutral; guarded by golden/parity.)
2. **Answer-model unification (TD-1)**: adopt `interactionType` + `answer.type`
   across the config/SDK surface; migrate arithmetic at a future version bump.
3. **Answer-checking breadth**: add checkers for surd, exact-trig, algebraic,
   set/interval, vector/matrix as those domains arrive.
4. **TS-side runtime schema gate** (e.g. Ajv) to mirror the Python conformance
   checker inside the app/export pipeline.
5. **Automated accessibility gate** (`axe-core`) in the browser verification.
6. **Renderer relocation** to `/renderers` for clean layering.

## Verdict

**Ready to scale with the SDK in place.** The mathematical and reproducibility
foundations are production-grade; the remaining work is generalization and
breadth (SDK helpers, answer-checking, runtime gates), not rebuilding. The
recommended next steps are the SDK helper extraction and TD-1, both output-neutral
and protected by the existing golden/parity/harness gates — no approved output is
at risk.

## Recommended phase order

1. SDK helper extraction (item builder, checks, difficulty) — refactor the two
   approved generators behind them with golden/parity as the guardrail.
2. TD-1 interaction-type migration (back-compatible).
3. TS runtime schema gate + automated a11y gate.
4. Then resume domain growth (a new family) under the SDK, on owner approval.
