# SPI-Math Question Bank Platform: Project Charter

Generated: 2026-06-19 23:24

## Objective

Start Phase 0 for the SPI-Math Question Bank Platform by inspecting the uploaded source material, preserving source traceability, and preparing the audit foundation before full application coding begins.

## Source Evidence Used

- `SPI-Math_Project_Instructions.md`
- `Question engine prompt.txt`
- `spi-math logo.png`
- Uploaded ZIP archives and folders under the project root
- Existing `spi-math-ibdp-aasl` curriculum folder and source inventory

## Working Rules Adopted

- Source files are read only.
- Archive contents are inspected recursively without executing scripts, macros, programs, or binaries.
- Generated audit outputs are placed under `docs/`.
- Rights status is conservative. SPI-Math branded internal material is marked `Academy-owned`; external PDFs and publisher-like materials are marked `Reference only`; other archive content remains `Rights unknown` until confirmed.
- English-only product direction from `Question engine prompt.txt` is treated as current project guidance.

## Preliminary Repository Structure

```text
/apps
  /generator-studio
  /question-bank
  /assessment-builder
  /quality-console
  /student-preview
/core
  /curriculum
  /question-schema
  /seeded-random
  /exact-math
  /difficulty
  /misconceptions
  /answer-checking
  /validation
  /bank
  /blueprints
/domains
/renderers
/exporters
/schemas
/tests
/docs
/scripts
```

## Phase 0 Deliverables Created

- docs/PROJECT_CHARTER.md
- docs/SOURCE_MANIFEST.md
- docs/SOURCE_MANIFEST.csv
- docs/source_manifest.records.json
- docs/CONTENT_AUDIT.md
- docs/CURRICULUM_COVERAGE.md
- docs/QUESTION_PATTERN_CATALOG.md
- docs/SOLUTION_STYLE_GUIDE.md
- docs/VISUAL_STYLE_AUDIT.md
- docs/RISKS_AND_GAPS.md
- docs/DECISION_LOG.md
- docs/CURRENT_STATE.md

## Assumptions

- Broad school-stage ZIP archives are source material, not generated outputs.
- The existing `spi-math-ibdp-aasl` folder is treated as source evidence and prior work, not as the final platform architecture.
- The file named `spi-math logo.png` is the available official logo asset, even though one instruction file mentions `spimath_logo.png`.
- The audit may be refined after deeper document extraction and owner confirmation.

## Blocking Questions

None for Phase 0. Rights confirmation will become blocking before any source-derived content is published or reused beyond analysis.
