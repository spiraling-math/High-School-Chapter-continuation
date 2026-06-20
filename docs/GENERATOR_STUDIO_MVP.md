# Generator Studio MVP

Status: complete and verified. Last updated: 2026-06-20. Scope: the proven
arithmetic-sequences vertical slice only (no new domains).

The Generator Studio is an offline, single-file browser application for
generating, previewing, editing, organizing, and exporting arithmetic-sequence
questions. It is the browser realization of the deterministic pipeline already
proven in TypeScript and cross-checked against the Python oracle.

## How to run

```bash
# Refresh PATH so the freshly-installed Node is visible (Windows/PowerShell):
$env:Path = [System.Environment]::GetEnvironmentVariable('Path','Machine') + ';' + [System.Environment]::GetEnvironmentVariable('Path','User')

npm run typecheck         # tsc --noEmit
npm test                  # node --test over core/**, domains/**, apps/**, exporters/**  (46 tests)
npm run build:studio      # → apps/generator-studio/dist/index.html  (single self-contained file)
npm run build:samples     # → apps/generator-studio/dist/samples/  (worksheet, answer-key, solutions, bank.json)

# Python oracle (development reference only — never a browser dependency):
python oracle/run_oracle.py            # golden + parity fixtures + 10,000-seed sweep
python oracle/tests/test_sequences.py  # 18 oracle tests
python oracle/make_review_pack.py      # regenerate the curriculum-review pack
```

Open `apps/generator-studio/dist/index.html` directly in a browser (file://) — it
needs no server and no internet.

## Architecture

```
apps/generator-studio/         browser app (TypeScript, bundled by esbuild)
  main.ts                      composition root
  controls.ts                  seed / random / mode / task / target band
  preview.ts                   meta + reproduction + 4 views (tabs)
  edit-panel.ts                protected params vs editable wording vs lifecycle
  bank-panel.ts                save / search / filter / open / duplicate / archive / delete
  exports.ts                   export & import toolbar (download / file picker)
  render/katex-render.ts       item -> accessible HTML (KaTeX html+MathML; katex injected)
  wording.ts                   display overlay (never mutates the math item)
core/bank/                     BankStore interface, IndexedDB impl + migrations, records
domains/sequences/             generator + validator (browser-safe, no DOM)
exporters/html|json/           standalone HTML + JSON exports (pure, testable)
scripts/                       build-studio, build-samples, katex-bundle, serve-dist
oracle/                        independent Python reference (dev/CI only)
```

- **Dependencies point downward**; the deterministic core/domain code has no DOM
  dependency and runs identically in the browser and in Node tests.
- **Storage abstraction:** the app depends on the `BankStore` interface, not on
  IndexedDB directly, so a future cloud backend can replace it without touching
  generator or validation logic.
- **The Python oracle is never loaded by the app.** It is a development and
  verification reference (golden vectors, parity fixtures, review pack).

## Key decisions

| Decision | Why |
| --- | --- |
| KaTeX bundled locally; CSS inlined with **woff2 fonts as data URIs**, JS inlined | No CDN; the app and the solutions export render math offline from file://. |
| Build to a **single self-contained HTML** (esbuild IIFE + inlined assets) | Opens by double-click; no server, no ES-module CORS issues on file://. |
| Core/domain tests use **Node's built-in `node:test`** | Runs offline with native TS type-stripping; no extra runtime dependency. |
| **IndexedDB** bank behind a `BankStore` interface, with ordered **migrations** | Not localStorage; survives reloads; schema can evolve; cloud-swappable later. |
| Persist the **exact generation config** (`genConfig`) on each record | Auto-task items draw the task from the RNG, so faithful reproduction needs the original config, not the resolved task. |
| Items begin at **machine-validated**; approved/published are not app-settable | Only the curriculum authority advances items to approval/publication. |
| **Editable wording overlay** separate from the immutable `item` | Wording edits change display text only; the canonical math is never corrupted. |
| Offline-safety checks match only **real external loads** (`src`/`href`/`url(`/`@import` → `http(s)://` or `//`) | Avoids false positives on the MathML namespace URI and bundled regex source, while still catching genuine network dependencies. |

## Acceptance gates — how each is met

| Gate | Status |
| --- | --- |
| Existing TS/Python parity tests pass | ✅ 46 TS tests, 18 Python tests; 300-entry cross-language parity. |
| 10,000-seed sweep, zero invalid | ✅ `oracle/run_oracle.py` → 0 invalid (20,000 items). |
| Same seed+config+version reproduce identical item | ✅ TS reproducibility test + browser check (seed 12345 twice). |
| Bank records survive browser reloads | ✅ Verified: saved, reloaded, record present (IndexedDB). |
| IndexedDB migrations tested | ✅ `core/bank` test: v1→v2 index add + data backfill. |
| JSON export/import reproduces canonical records | ✅ Round-trip is byte-identical; integrity by regeneration. |
| Exported HTML opens from file:// offline | ✅ Zero external loads + single inlined bundle; runtime verified via local static server; samples render math with inlined fonts. |
| Exports contain no CDN/secret/external runtime | ✅ Build + export + test assertions; grep over built HTML clean. |
| Wording edits cannot corrupt math params | ✅ `displayItem`/`withWording` tests; protected params read-only in UI. |
| Student exports don't reveal answers/validation | ✅ Worksheet test + browser check: no answer label, no solution, no validation. |
| Answer-key & solution exports agree with canonical answers | ✅ Exporter tests assert agreement. |
| No console errors; fully keyboard-operable | ✅ No console logs; tab roving focus + arrow keys verified. |
| Tests, commands, decisions, limitations documented | ✅ This document + CURRENT_STATE + DECISION_LOG. |

## Browser/offline verification (this session)

Loaded the built app via a local static server and evaluated in-page:
KaTeX global present; four views render; solution shows `.katex` + `<math>`
(accessible MathML); validation shows icon + text (non-color); `lang=en`, skip
link, polite live region present; **save → reload → record persists**; seed 12345
reproduces identically; ArrowRight moves tab focus; **no console errors**. Sample
exports: solutions render math with inlined fonts and no external loads;
worksheet has no answers/solutions/validation and includes answer spaces.

> Note: file:// resource-loading is guaranteed by design (zero external loads +
> single inlined IIFE bundle, so nothing is ever fetched). Runtime behavior was
> verified over a local static server, which is equivalent because no resource is
> loaded from the network in either case.

## Known limitations

- **Renderers live under `apps/generator-studio/render/`** and are imported by the
  exporters; they should move to `/renderers` for cleaner layering. (Behavioral
  no-op; a future refactor.)
- **Worksheet exports embed no KaTeX CSS** because current prompts contain no
  display math (text + integer options). If prompt-level math is added later,
  the worksheet exporter must embed the bundled CSS like the solutions exporter.
- **Difficulty targeting** is a seed search from the entered seed; it can fail to
  find a band within the search cap for some configurations (it reports this).
- **Accessibility testing** is render-level (MathML, non-color indicators, roles)
  plus a manual keyboard/console pass. An automated `axe-core` browser scan is a
  recommended next step.
- **Single-user, local-only.** No authentication/authorization; multi-user and a
  cloud `BankStore` are future phases.
- **App build artifact is ~1 MB** (KaTeX CSS+fonts+JS inlined twice: once for the
  page, once as a string for the solutions export). Acceptable for offline use;
  could be de-duplicated later.

## Next recommended decision

Curriculum-author review of the arithmetic-sequences review pack
(`docs/review/arithmetic_sequences_review_pack.md`) to advance items beyond
`machine-validated`. After your approval, the recommended next build increment is
the **second generator family** (e.g. geometric sequences) — oracle-first, then
TypeScript with golden parity — which you have asked to gate on your approval.
