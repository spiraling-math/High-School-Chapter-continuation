# Architecture

Status: Phase 1 draft. Last updated: 2026-06-20.

This document describes the system architecture for the SPI-Math Question Bank Platform. It is the top-level technical reference; companion documents (`DATA_MODEL.md`, `GENERATOR_STANDARD.md`, `VALIDATION_STANDARD.md`, etc.) expand individual areas.

## 1. Goals and constraints

The platform generates, validates, stores, edits, organizes, and exports original mathematics questions from preschool through first-year university. The architecture is shaped by ten non-negotiable principles:

1. **Deterministic mathematics** — answers are produced and verified by code, never asserted by a language model.
2. **Reproducibility** — every item is reproducible from `{generatorId, generatorVersion, seed, config}`.
3. **Separation of concerns** — curriculum, generation, solving, validation, rendering, storage, UI, and export are distinct layers.
4. **Independent verification** — the method that verifies an answer is independent of the method that generated it.
5. **Original generation** — generators encode mathematical structure, not number-swaps of copyrighted source questions.
6. **Modular development** — no single monolithic HTML file; a modular source project that builds standalone HTML outputs.
7. **Offline capability** — core generation, validation, bank use, editing, and export work with no internet.
8. **Security** — no secrets in any downloadable artifact.
9. **Traceability** — every item links to objective, generator, version, seed, difficulty, review state, dates, and source evidence.
10. **Accessibility** — built into the architecture, not bolted on.

## 2. Layered architecture

```
┌─────────────────────────────────────────────────────────────────────┐
│  Apps (UI)   generator-studio · question-bank · assessment-builder    │
│              quality-console · student-preview (later)                │
├─────────────────────────────────────────────────────────────────────┤
│  Renderers   mathematics(KaTeX) · svg · graphs · tables · print       │
├─────────────────────────────────────────────────────────────────────┤
│  Exporters   html · json · csv · print · qti(future)                  │
├─────────────────────────────────────────────────────────────────────┤
│  Domains     sequences · arithmetic · algebra · … (generator modules) │
├─────────────────────────────────────────────────────────────────────┤
│  Core        curriculum · question-schema · seeded-random ·           │
│              exact-math · difficulty · misconceptions ·               │
│              answer-checking · validation · bank · blueprints         │
├─────────────────────────────────────────────────────────────────────┤
│  Verification oracle (Python, independent)                            │
└─────────────────────────────────────────────────────────────────────┘
```

Dependencies point **downward only**. The deterministic core has **no DOM dependency** and can run headless. Renderers and apps depend on core; core never depends on them.

### Layer responsibilities

| Layer | Responsibility | DOM? |
| --- | --- | --- |
| Core | Math, RNG, schemas, generators' shared contracts, validation, answer checking, difficulty, misconceptions, bank storage abstraction, blueprint engine | No |
| Domains | Concrete generator modules implementing the generator contract | No |
| Renderers | Turn item DATA into HTML/SVG/print output | Yes |
| Exporters | Serialize items/assessments to JSON/CSV/HTML/print | No (string output) |
| Apps | User-facing applications composing the above | Yes |
| Oracle | Independent Python recomputation of the mathematics for cross-checking | No |

## 3. Key data flow: generate → validate → store → render → export

```
config + seed
   │
   ▼
generate(seed, config) ──► QuestionItem (params, prompt, answer, distractors, solution)
   │                                   │
   │                                   ▼
   │                          solve(params)  ── canonical answer (closed form)
   │                                   │
   ▼                                   ▼
validate(item) ◄───────── independent method (e.g. iterative) must AGREE
   │  (schema + math self-checks + a11y + distractor checks)
   ▼
status = pass  ──► bank.put(item)  (IndexedDB / storage abstraction)
   │
   ▼
render(item, mode)  ──► HTML/SVG (KaTeX)        export(item|assessment, target) ──► file
```

An item that fails validation never enters the bank. Validation is independent of generation (Principle 4).

## 4. Seeded determinism

- The only randomness source is a **named seedable PRNG, `mulberry32`** (Decision #10), implemented with explicit 32-bit unsigned arithmetic so Python (oracle) and TypeScript (production) produce **byte-identical** streams. `Math.random()` and unseeded entropy are forbidden in core/domains.
- A generator receives a single 32-bit seed and derives all parameter choices from it. The same seed always yields the same item, answer, distractors, solution, and metadata.
- Seeds travel with the item into the bank and every export, so any item can be regenerated.

## 5. Implementation languages and the runtime situation

- **Production / browser layer:** TypeScript, compiled to JavaScript, because the deployment target is **offline standalone HTML** that runs in a browser. Bundled with esbuild/Vite into single-file apps with assets inlined (no CDN at runtime). Runtime schema validation with a lightweight validator (e.g. Ajv or a hand-rolled checker); KaTeX for math.
- **Verification oracle:** Python. Independent reference implementation of the deterministic mathematics, used to cross-check generator output via golden JSON vectors. A permanent component supporting Principle 4.
- **Current constraint (Decision #8):** No JavaScript runtime is installed on the development machine yet; Python 3.14 and Git are present. The TypeScript core, Vitest suite, and bundler require installing **Node.js LTS**. Until then, the Python oracle is the executable proof of the mathematics, and the TS layer is authored against it. This is a tooling gap, not a language reversal — browser deployment still requires JS.

## 6. Storage architecture

- **Offline bank:** IndexedDB (not localStorage, which is unsuitable as a primary DB for a large bank).
- **Storage abstraction:** the bank is accessed through a `BankStore` interface (`put`, `get`, `query`, `delete`, `bulk*`). IndexedDB is one implementation; a future cloud database is another. Generator and validation logic depend only on the interface, so a cloud backend can be added without rewriting them.
- **Canonical format:** structured JSON conforming to `question-item.schema.json`. Items store mathematical DATA, never pre-rendered text only.
- **Integrity:** optional `contentHash` (sha256 of canonical serialization) for duplicate detection and tamper-evidence.

## 7. Modules and repository structure

See the repository layout in `CURRENT_STATE.md` / project root. Summary:

- `/core` — deterministic, DOM-free building blocks.
- `/domains/<domain>` — generator modules (one family per folder).
- `/renderers` — presentation of item data.
- `/exporters` — output formats.
- `/apps/<app>` — the five applications.
- `/schemas` — JSON Schemas (the contracts).
- `/oracle` — Python verification oracle and its tests.
- `/tests` — TypeScript test suites (unit, property, golden) — pending Node.js.
- `/docs` — all documentation.
- `/scripts` — audit and utility scripts.

## 8. Versioning model

Curriculum objectives, generator modules, question items, schemas, assessment blueprints, and export formats are all versioned (semantic versioning). **A published generator version is never silently changed**: any logic change that alters output requires a new version. Items record the exact generator version that produced them, so regeneration is unambiguous even as generators evolve.

## 9. Security posture (summary)

No API keys, database credentials, or secrets are ever embedded in client bundles or exports. Offline builds make no network calls. Author-edited content is sanitized before rendering. See `SECURITY_AND_PRIVACY.md`.

## 10. Open architectural items

- Production runtime install (Node.js LTS) to activate the TS/app/bundler/test pipeline.
- Choice of TS runtime schema validator (Ajv vs. minimal custom) — to be decided in Phase 1 implementation.
- Cloud `BankStore` implementation — deferred until a multi-user phase.
