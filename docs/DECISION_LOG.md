# Decision Log

Originated: 2026-06-19. Last updated: 2026-06-20.

This log records significant, durable decisions. Each row is an architectural decision record (ADR) in compact form. Decisions are not silently changed; superseded rows are marked and a new row is added.

| # | Date | Decision | Rationale | Status |
| --- | --- | --- | --- | --- |
| 1 | 2026-06-19 | Start with Phase 0 source audit before full application coding. | Required by `Question engine prompt.txt`; prevents generic platform work disconnected from uploaded curriculum. | Accepted |
| 2 | 2026-06-19 | Keep source files read only and place generated audit files under `docs/`. | Preserves provenance and prevents accidental overwrites. | Accepted |
| 3 | 2026-06-19 | Conservative rights handling: SPI-Math branded files = Academy-owned; external PDFs (Oxford) = Reference only; broad archives = Rights unknown until confirmed. | Required before any content reuse. | Accepted |
| 4 | 2026-06-19 | Use a modular TypeScript-first repository structure for the production/browser layer. | Matches architecture instructions; the offline standalone-HTML deployment target requires browser JavaScript (TypeScript compiles to JS). | Accepted (see #8 for runtime caveat) |
| 5 | 2026-06-20 | AI-generated capstones (Claude/Gemini subfolders) are **Academy-owned draft/reference** material. They may be analysed for patterns, coverage, styles, and ideas, but final bank items must be independently validated and regenerated where necessary. | Owner decision. Preserves the deterministic-generation and original-generation principles; AI drafts are not trusted as final mathematical authority. | Accepted (owner) |
| 6 | 2026-06-20 | University-level mathematics is **reserved** in the architecture and curriculum graph, but **no active university generators** are built until fuller curriculum documents and resources are provided. | Owner decision. University source material currently is worksheet images only — insufficient for generator development. | Accepted (owner) |
| 7 | 2026-06-20 | The **first vertical slice** is IBDP AA SL Chapter 1 (Sequences and Series), beginning with **arithmetic sequences**. | Owner decision. Strongest source coverage (full curriculum map, 80 questions, Oxford teacher notes with solutions, HS source cross-references). Ideal to prove the full pipeline. | Accepted (owner) |
| 8 | 2026-06-20 | **Environment constraint recorded:** no JavaScript runtime (Node/Deno/Bun) is installed on the development machine; **Python 3.14 and Git are available**. Production/browser code remains TypeScript→JS (Decision #4), but TypeScript cannot be built or tested here until Node.js LTS is installed. | Verified by inspection (`node`, `deno`, `bun` not found; `python` 3.14.6 and `git` present). The offline standalone-HTML target makes browser JavaScript mandatory; this is a tooling gap, not a language reversal. | Accepted |
| 9 | 2026-06-20 | Build the deterministic vertical-slice mathematics first as a **runnable Python reference implementation** that doubles permanently as the **independent verification oracle**. The TypeScript production generators will mirror it and be cross-checked against its golden JSON vectors. | Honors the "deterministic mathematics proven by running tests" and "independent verification" principles **now**, despite the missing JS runtime. Python is available and runs today; an independent oracle is a required architectural component regardless. | Accepted |
| 10 | 2026-06-20 | Adopt **mulberry32** as the canonical named seeded PRNG, implemented with explicit 32-bit unsigned arithmetic so that Python (oracle) and TypeScript (production) produce **byte-identical** sequences for the same seed. | Cross-language reproducibility is required: the same `{generator, version, seed}` must reproduce identical items in both the oracle and production. A 32-bit integer PRNG ports exactly between Python and JS; `Math.random()` is forbidden. | Accepted |
| 11 | 2026-06-20 | **Node.js v24.17.0 installed** (owner). The TypeScript production layer is unblocked. Core/domain tests use **Node's built-in test runner (`node:test`)** with native TypeScript type-stripping, so the deterministic core runs offline with **no `npm install`**. The TS PRNG, canonical serializer, and arithmetic-sequences generator are proven byte-for-byte against the Python oracle's golden vectors (16 TS tests pass). | Node 24 runs `.ts` directly; using `node:test` keeps the deterministic core dependency-free and offline-capable. Vitest is reserved for the later DOM/app layer. | Accepted |

## Pending / awaiting owner

- **Mathematics/curriculum review** of the arithmetic-sequences slice to advance items past `machine-validated`.
- **One-time `npm install` (online)** to enable `tsc` typecheck and add Vitest for the future DOM/app layer (not needed for the current core tests).
- **Courses not yet present in sources:** IB Mathematics AA HL and IB Mathematics AI (SL/HL) are not in the uploaded materials. Reserved in the curriculum graph; no generators until provided.

## Superseded decisions

_None yet._
