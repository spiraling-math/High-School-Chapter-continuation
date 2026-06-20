# SPI-Math Question Bank Platform

A production-quality, deterministic platform for generating, validating, storing, editing, organizing, and exporting **original** mathematics questions — from preschool through first-year university.

> Status: **Phase 1 — Foundation and First Vertical Slice.** The design foundation (schemas + architecture standards) is in place, and the first generator (arithmetic sequences) is proven end-to-end by a runnable Python verification oracle. The production TypeScript/browser layer is pending a Node.js install. See `docs/CURRENT_STATE.md`.

## Principles (non-negotiable)

Deterministic mathematics · reproducible-by-seed · separation of concerns · independent verification · original generation · modular · offline-capable · no secrets in exports · fully traceable · accessible by design. See `docs/ARCHITECTURE.md`.

## Repository layout

```
schemas/      JSON Schemas — the contracts (objective, item, generator, misconception, blueprint, source)
docs/         Architecture and standards documents, audit reports, decision log, current state
curriculum/   Curriculum objective data (the curriculum graph)
core/         Deterministic, DOM-free building blocks (misconception data lives here now)
domains/      Generator modules per domain (production TypeScript — pending Node.js)
renderers/    Presentation of item data (KaTeX, SVG, print)
exporters/    Output formats (json, csv, html, print)
apps/         The five applications (generator-studio, question-bank, assessment-builder, quality-console, student-preview)
oracle/       Python independent verification oracle + reference implementation of the first slice
tests/        TypeScript test suites (pending Node.js)
scripts/      Audit and utility scripts
```

## The verification oracle (runnable today)

The `oracle/` package is an independent, deterministic reference implementation in Python. It proves the mathematics now and permanently cross-checks the production generators (independent-verification principle). It shares the canonical `mulberry32` PRNG with the future TypeScript code, so the same seed reproduces identical items in both languages.

```bash
python oracle/tests/test_sequences.py     # 18 unit + property tests
python oracle/run_oracle.py               # golden vectors + 10,000-seed validation sweep (0 invalid)
python oracle/check_conformance.py        # schema conformance of data + live generated items
```

## First vertical slice

`gen.sequences.arithmetic` (IBDP AA SL, Chapter 1) — nth term, sum of first n terms, and reverse tasks. Specification: `docs/GENERATOR_SPEC_arithmetic_sequences.md`.

## Key documents

| Area | Document |
| --- | --- |
| System architecture | `docs/ARCHITECTURE.md` |
| Data model | `docs/DATA_MODEL.md` |
| Generator contract | `docs/GENERATOR_STANDARD.md` |
| Validation | `docs/VALIDATION_STANDARD.md` |
| Difficulty | `docs/DIFFICULTY_MODEL.md` |
| Misconceptions | `docs/MISCONCEPTION_MODEL.md` |
| Answer equivalence | `docs/ANSWER_EQUIVALENCE.md` |
| Accessibility | `docs/ACCESSIBILITY_STANDARD.md` |
| Exports | `docs/EXPORT_STANDARD.md` |
| Testing | `docs/TESTING_STRATEGY.md` |
| Security & privacy | `docs/SECURITY_AND_PRIVACY.md` |
| Roadmap | `docs/ROADMAP.md` |
| Decisions | `docs/DECISION_LOG.md` |
| Handover / status | `docs/CURRENT_STATE.md` |

All content is **English only**. Uploaded curriculum and internal documents are confidential; third-party reference materials are not reproduced verbatim.
