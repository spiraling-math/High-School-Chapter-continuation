# Data Model

Status: Phase 1 draft. Last updated: 2026-06-20.

This document describes the core data entities and how they relate. The authoritative field-level definitions live in `/schemas/*.json`; this document explains the model and the relationships between entities.

## 1. Entities

| Entity | Schema | Purpose |
| --- | --- | --- |
| Source Record | `source-record.schema.json` | Provenance and rights for each uploaded/derived file. |
| Curriculum Objective | `curriculum-objective.schema.json` | A single learning objective; node in the curriculum graph. |
| Question Item | `question-item.schema.json` | A generated or authored question, with answer, solution, distractors, metadata. |
| Generator Module Descriptor | `generator-module.schema.json` | Self-description of a versioned generator. |
| Misconception | `misconception.schema.json` | A named student misconception driving distractors and feedback. |
| Assessment Blueprint | `assessment-blueprint.schema.json` | A reusable spec for building assessments and variants. |

## 2. Entity-relationship overview

```
SourceRecord ──evidence──► CurriculumObjective ──assessed by──► QuestionItem
                                   ▲                                │
                                   │                                ├─ produced by ─► GeneratorModule
   Misconception ◄── surfaces ─────┘                                │
        ▲                                                           │
        └──────────── referenced by distractors of ────────────────┘

AssessmentBlueprint ──selects/generates──► QuestionItem(s)
```

- A **Source Record** provides *evidence* cited by Curriculum Objectives and Items (`sourceReferences`).
- A **Curriculum Objective** is *assessed by* many Question Items (`objectiveIds`). Objectives link to each other via `prerequisites` (directed) and `relatedObjectives`/`crossDomainRelationships` (lateral).
- A **Question Item** is *produced by* a Generator Module (`generatorId` + `generatorVersion` + `seed`), assesses one or more Objectives, and its distractors reference Misconceptions.
- An **Assessment Blueprint** *selects or generates* Items via slot rules.

## 3. Identifier conventions

Stable, human-readable, filename-independent identifiers:

| Entity | Pattern | Example |
| --- | --- | --- |
| Source | `SRC-<token>` | `SRC-0a1b2c3d` |
| Objective | `SPI.<COURSE/LEVEL>.<DOMAIN>.<TOPIC>[.<SUB>][.<MICRO>].<NN>` | `SPI.IBDPAASL.SEQSER.ARITH.NTH_TERM.01` |
| Item | `ITEM-<token>` | `ITEM-aasl-seq-arith-0001` |
| Generator | `gen.<domain>.<family>` | `gen.sequences.arithmetic` |
| Misconception | `MISC.<DOMAIN>.<NAME>` | `MISC.SEQ.OFFBYONE_TERMINDEX` |
| Blueprint | `BP-<token>` | `BP-aasl-ch01-quiz` |

Objective IDs are designed to read top-down (course → domain → topic → subtopic → micro-skill → ordinal) and to extend without renumbering existing IDs.

## 4. The curriculum graph

Objectives form a directed graph:

- **Prerequisite edges** (`prerequisites`): "must master X before Y". Used for progression, gap analysis, and scaffolding. Must be acyclic; cycle detection runs in validation tooling.
- **Lateral edges** (`relatedObjectives`): non-prerequisite relationships within a domain.
- **Synoptic edges** (`crossDomainRelationships`): connections across domains, enabling cross-domain/synoptic questions.

The graph spans all stages (preschool-kg … university). University nodes are **reserved** (Decision #6): they may exist as objectives but have no active generators yet.

## 5. The Question Item in depth

The item deliberately separates **data** from **presentation**:

- **Mathematical data:** `params`, `answer.canonical`, `answer.equivalentForms`, `solution.steps`, `distractors[].value`. This is the source of truth.
- **Presentation:** `prompt.blocks` (text + LaTeX source), `media` (SVG/graph specs), `*.display` strings. Rendered HTML is produced on demand by renderers and is never the only stored form.

Consequences:
- An item can be re-rendered in light/dark/print without changing its data.
- Diagrams are generated from `params` (Principle: diagram matches the mathematics), not drawn independently.
- Editing wording (`prompt.blocks` text) does not touch the mathematics; editing that changes mathematics must go through regeneration or explicit re-validation.

### Multi-part questions
A parent item holds `parts[]`, each referencing a child item by id with optional `dependsOn`. Follow-through marking is supported via `markScheme.awards[].type = "follow-through"`.

## 6. Answer representation

`answer.type` draws from the shared `answerType` enum (defined once in `question-item.schema.json#/$defs/answerType` and referenced by objectives, generators, and blueprints). Encoding of `answer.canonical` depends on type — e.g. integer for `integer`, `{num, den}` for `fraction`, LaTeX/string for `algebraic-expression`, an array for `sequence`/`vector`. Exact types must not carry `tolerance`; only approximate numeric answers use it. See `ANSWER_EQUIVALENCE.md`.

## 7. Lifecycle and review state

Items move through lifecycle states: `draft → generated → machine-validated → mathematics-reviewed → curriculum-reviewed → approved → published → revised → retired`. Each transition is recorded in `lifecycle.reviewHistory`. Only `machine-validated` (or later) items with `validation.status = pass` are eligible for assessment use; only the curriculum authority advances items to `approved`/`published`.

## 8. Difficulty as data

`difficulty` carries a 16-axis vector (`axes`, each 0..1) plus a derived `overallBand` (1..5). The band is computed from the axes by a documented function (see `DIFFICULTY_MODEL.md`), never assigned by hand-waving. Generators populate the axes from their parameters.

## 9. Traceability chain

For any item, the chain is:
`objectiveIds → generatorId@generatorVersion → seed → params → answer → solution → validation → lifecycle.state → provenance.sourceReferences → dates`.
Every link is stored on the item, satisfying Principle 9.

## 10. Versioning and migration

Each schema has a `version`; items carry `schemaVersion`. When a schema changes in a breaking way, a migration step upgrades stored items and bumps `schemaVersion`. Generator and objective versions are independent of schema versions.
