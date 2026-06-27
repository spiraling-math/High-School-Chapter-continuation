STATUS: PROPOSAL ONLY — no implementation until owner approval (this is the deliverable architecture document, not code; every JSON/TS fragment is labelled "illustrative — not to implement now").

**Executive summary.** As SPI-Math scales past its first nine curriculum-approved generator families, two cross-cutting capabilities are now needed: a **unified objective registry/index** that gives a single query layer over the 70 approved objectives currently living as eleven per-family JSON files under `curriculum/objectives/`, and a **standards-alignment layer** that lets external curriculum frameworks *reference* SPI objectives without ever becoming the foundation of the engine. This document specifies the model, schema, lifecycle, governance, and validation rules for both — and nothing more. It is bound by two non-negotiable principles: external standards map **TO** SPI objective IDs (never the reverse; the SPI objective ID is the stable single source of truth), and Phase 1 is **output-neutral** (no approved generator item bytes, fixtures, golden vectors, review packs, production samples, or objective definition bytes change because this architecture is being designed). The registry is a derived read layer over the existing files; the alignment layer is a new, separate, SPI-keyed store that leaves the already-populated inline `externalAlignments` records and the objective schema byte-frozen. The platform's existing infrastructure — the `reviewStatus` lifecycle enum, the `externalAlignments` hook, `core/curriculum/graph-check.ts`, the per-family task↔objective maps, the SDK registry, and the sha256 manifests — is reused, not reinvented; Phase 1 formalizes the model and governance around it.

---

## 1. Purpose and scope

### 1.1 What this document is

This is the **SPI-Math Objective Registry and Standards Architecture** — a **proposal-only** architecture specification. It defines the *model, schema, lifecycle, governance, and validation rules* for two things the platform now needs as it scales past its first nine generator families:

1. a **unified objective registry / index** — a single query layer over the objective definitions that today live as eleven per-family JSON files under `curriculum/objectives/`; and
2. a **standards-alignment layer** — the schema, lifecycle, governance, and validation rules by which external curriculum frameworks (IGCSE, IB, Singapore, Lebanese official curriculum, Common Core, and others) may *reference* SPI objectives.

It is the deliverable document, **not** an implementation. It contains designs, schemas, data models, controlled vocabularies, and rules. All JSON/TS fragments in this document are labelled **"illustrative — not to implement now"** and exist to make a design decision concrete and reviewable. This document does **not** author production code, migrations, objective rewrites, or any standards-mapping content.

### 1.2 The load-bearing principle (binding)

> **External standards map TO SPI objectives, never the reverse.** The relation modelled here is always *`SPI objectiveId` → optional external standard reference(s)*. The internal SPI objective ID is the **stable single source of truth**. External standards must never replace, rename, re-key, or become the foundation of the engine.

Every design choice in this document is subordinate to that principle. The objective ID is the spine; alignment records hang off it and can be added, revised, or retired without ever touching the objective's identity. This mirrors the constraint already encoded in the schema's `externalAlignments` field, whose description reads *"Reference only; never implies reuse rights"* (`schemas/curriculum-objective.schema.json`, line 88).

### 1.3 Output-neutrality guarantee (binding)

Phase 1 is **output-neutral**. Designing the registry and alignment architecture must change **zero** approved artifacts:

- no approved generator item bytes, golden vectors, parity fixtures, review packs, or production samples change;
- the eleven per-family objective **files remain the source of record**; the registry is a *generated/loaded index over them*, not a replacement store;
- approved objective definitions are **not rewritten** unless a SAFE migration path is explicitly identified and called out as such (this cluster identifies none — all 70 objectives already validate against the existing schema regex, see §3);
- the **30 inline `externalAlignments` records already present across 7 of the 11 files** (§2, §9) are frozen and are not rewritten or migrated into the new alignment store.

This is the same discipline the generator families already follow: the SDK registry `core/sdk/sequence-registry.ts` is explicitly described in-code as *"only adapts them to the GeneratorModule shape (output-neutral)."* The objective registry adopts that posture verbatim.

### 1.4 In scope (this document)

| Area | This cluster (foundations) | Later clusters |
|---|---|---|
| Purpose, scope, principles | §1 | — |
| Current-state inventory of approved objective families | §2 | — |
| Objective ID grammar (formalize the variable-depth grammar already in use) + validation regex | §3 | — |
| Stage / domain / strand / topic controlled vocabulary + governance of new values | §4 | — |
| Unified registry / index model (load model, query surface, integrity) | §5 | — |
| Objective lifecycle and versioning | §6 | — |
| Prerequisite DAG model | §7 | — |
| Generator capability mapping | §8 | — |
| Alignment record schema, lifecycle, governance, validation | §9 | — |
| Coverage and gap analysis | §10 | — |
| Governance / integrity checks; migration; output-neutrality; review workflow; build plan; future phases | §11–§16 | — |
| Full external mapping; university architecture; lessons; analytics | — | future, separately gated (§16) |

### 1.5 Out of scope (Phase 1, binding)

Explicitly **excluded**: authoring many new objectives; rewriting approved objective wording; full IGCSE / IB / Singapore / Lebanese / Common Core mapping (only a tiny pilot to prove the design is permitted, §9.5); university-level objective architecture (reserved as future only); lesson plans and lesson-plan schemas; analytics dashboards; auto-publishing; changing any approved generator output; and starting another generator family. The standards layer is admitted to Phase 1 **as architecture only** — schema, lifecycle, governance, validation — and explicitly **not** as a mapping exercise.

### 1.6 Relationship to existing documents

This document builds on, and must remain consistent with, the existing curriculum and generator specifications. It does **not** restate or supersede them:

| Existing artifact | Role relative to this document |
|---|---|
| `schemas/curriculum-objective.schema.json` | **The objective schema this document builds on.** It already defines `objectiveId`, the `reviewStatus` lifecycle enum, and the `externalAlignments` hook. Phase 1 *formalizes their model and governance; it does not invent these fields.* |
| `curriculum/objectives/*.json` (11 files) | The source of record for the 70 objectives the registry indexes (§2), including 30 already-populated inline `externalAlignments` records. |
| `core/curriculum/graph-check.ts` | The existing graph engine: `checkCurriculumGraph` emits **duplicate-id** and **prerequisite-cycle** as *errors* and **unresolved prerequisites** as *warnings*; `requireObjectives(objectives, expected)` is a distinct presence-check helper. The registry's integrity checks extend this, they do not replace it. |
| `core/curriculum/*-objective-ids.ts` | Per-family single-source task→objective maps (e.g. `OBJECTIVE_BY_TASK`, `RATIO_TASKS`) — the binding evidence for §3/§4 and the join key to generator capability. |
| `core/sdk/sequence-registry.ts` | The generator-side registry (`approvedGenerators()`, `generatorsForMode()`); the objective registry is its curriculum-side counterpart. |
| `docs/GENERATOR_SPEC_*_PROPOSAL.md` | The voice, rigor, and register this document mirrors. |

---

## 2. Current-state inventory of the approved generator objective families

This section is a **factual census** of what exists today. Every figure is drawn directly from `curriculum/objectives/` and the SDK registry; nothing here is aspirational.

### 2.1 Headline counts

| Quantity | Value |
|---|---|
| Curriculum-approved generator families | **9** |
| Per-family objective JSON files | **11** |
| Total objective definitions | **70** |
| Objectives with `reviewStatus: "approved"` | **70 (100%)** |
| Objectives carrying inline `externalAlignments` | **30, across 7 of the 11 files** |
| Distinct inline alignment frameworks | **3** (Cambridge IGCSE 0580 ×21, Singapore Lower Secondary ×14, IB Mathematics AA SL ×9) |
| Distinct `domain` values | **7** (`algebra`, `geometry`, `measurement`, `number`, `proportion`, `sequences-and-series`, `statistics`) |
| Distinct `strand` values | **13** |
| Distinct `stage` field values | **2** (`ibdp-aasl`, `middle-school`) |
| Distinct ID stage segments | **2** (`IBDPAASL`, `MIDDLE`) |

The nine **families** and the eleven **files** are not 1:1: two families (`gen.sequences.arithmetic`, `gen.sequences.geometric`) each own a file; some families' objectives are split across files where a foundations sub-file exists (algebra), and the angles family's objectives sit in the domain-level `SPI.MIDDLE.GEO.json` alongside the coordinate and transformation sub-files. The registry must therefore key on the **objective ID and the generator id**, never on filename — consistent with the schema's stated intent that objectives have *"stable identifiers independent of filenames."*

### 2.2 Family → file → objective census

The nine families and their objective files, with exact counts (sum = 70):

| # | Generator family (`generatorId`) | Domain (ID segment) | Stage segment | Objective file | Count |
|---|---|---|---|---|---|
| 1 | `gen.sequences.arithmetic` | `SEQSER` | `IBDPAASL` | `SPI.IBDPAASL.SEQSER.ARITH.json` | 4 |
| 2 | `gen.sequences.geometric` | `SEQSER` | `IBDPAASL` | `SPI.IBDPAASL.SEQSER.GEO.json` | 5 |
| 3 | `gen.algebra.linear-equations` | `ALG` | `MIDDLE` | `SPI.MIDDLE.ALG.FOUNDATIONS.json` | 2 |
| 3 | `gen.algebra.linear-equations` | `ALG` | `MIDDLE` | `SPI.MIDDLE.ALG.LINEQ.json` | 5 |
| 4 | `gen.geometry.angles-figures` | `GEO` | `MIDDLE` | `SPI.MIDDLE.GEO.json` | 5 |
| 5 | `gen.geometry.coordinate-lines` | `GEO.COORD` | `MIDDLE` | `SPI.MIDDLE.GEO.COORD.json` | 8 |
| 6 | `gen.geometry.transformations` | `GEO.TRANS` | `MIDDLE` | `SPI.MIDDLE.GEO.TRANS.json` | 9 |
| 7 | `gen.stats.data-handling` | `STAT` | `MIDDLE` | `SPI.MIDDLE.STAT.json` | 11 |
| 8 | `gen.measurement.mensuration` | `MEAS` | `MIDDLE` | `SPI.MIDDLE.MEAS.json` | 8 |
| 9 | `gen.proportion.ratio` | `RATIO` | `MIDDLE` | `SPI.MIDDLE.RATIO.json` | 12 |
| — | (no generator family; `number` domain) | `NUM` | `MIDDLE` | `SPI.MIDDLE.NUM.json` | 1 |
| | | | | **Total** | **70** |

**Note on the eleventh file.** `SPI.MIDDLE.NUM.json` holds a single objective `SPI.MIDDLE.NUM.SIGNED_OPERATIONS.01` (`signed-numbers` strand). It is an approved objective but is **not** the anchor of one of the nine generator families; it is referenced as a prerequisite/foundation. The registry must represent objectives that exist *independently of whether a generator family currently targets them* — the index is over objectives, and generator coverage is a *derived join*, not a precondition for an objective to exist.

### 2.3 Inline alignment population (already present, frozen)

Contrary to a clean-slate assumption, the inline `externalAlignments` hook is **already broadly populated**: 30 objectives across 7 of the 11 files carry non-empty alignment arrays today, every entry of the minimal shape `{framework, code, label?}` that the existing schema permits.

| File | Inline-aligned objectives | Frameworks present |
|---|---|---|
| `SPI.IBDPAASL.SEQSER.ARITH.json` | 4 | IB Mathematics AA SL |
| `SPI.IBDPAASL.SEQSER.GEO.json` | 5 | IB Mathematics AA SL |
| `SPI.MIDDLE.ALG.FOUNDATIONS.json` | 2 | IGCSE 0580, Singapore Lower Secondary |
| `SPI.MIDDLE.ALG.LINEQ.json` | 5 | IGCSE 0580, Singapore Lower Secondary |
| `SPI.MIDDLE.GEO.json` | 5 | IGCSE 0580, Singapore Lower Secondary |
| `SPI.MIDDLE.GEO.COORD.json` | 8 | IGCSE 0580, Singapore Lower Secondary |
| `SPI.MIDDLE.NUM.json` | 1 | IGCSE 0580, Singapore Lower Secondary |
| **Total** | **30** | **3 frameworks** (IGCSE 0580 ×21, Singapore ×14, IB AA SL ×9) |

These 30 records are part of approved, **sha256-frozen** objective files (e.g. `SPI.MIDDLE.GEO.COORD.json` is pinned by its family manifest). They are **frozen and untouched in Phase 1** — neither rewritten nor migrated. They are also the empirical precedent that the *richer* alignment model (§9) must coexist with, not replace. Notably, `SPI.MIDDLE.RATIO.json` currently has **zero** inline alignments, which is why a ratio pilot (§9.5) is genuinely net-new for that family while remaining output-neutral for the seven already-aligned files.

### 2.4 Stage distribution

| Stage field value | ID stage segment | Objective count |
|---|---|---|
| `middle-school` | `MIDDLE` | 61 |
| `ibdp-aasl` | `IBDPAASL` | 9 |
| | **Total** | **70** |

The nine IBDP-AASL objectives are the two sequences families (4 + 5); the remaining 61 are all `middle-school`. The schema's `stage` enum already admits seven other stages (`preschool-kg`, `primary`, `high-school`, `ibdp-aahl`, `ibdp-ai`, `university`, `cross-level`) that have **no objectives yet** — reserved capacity, governed by §4.

### 2.5 Domain → strand → family map

The 13 strands, grouped under their 7 domains, with the owning family and example objective:

| Domain (`domain` field) | Strand (`strand` field) | Family | Example objective ID |
|---|---|---|---|
| `sequences-and-series` | `arithmetic-sequences` | arithmetic | `SPI.IBDPAASL.SEQSER.ARITH.NTH_TERM.01` |
| `sequences-and-series` | `arithmetic-series` | arithmetic | `SPI.IBDPAASL.SEQSER.ARITH.SUM_N.01` |
| `sequences-and-series` | `geometric-sequences` | geometric | `SPI.IBDPAASL.SEQSER.GEO.NTH_TERM.01` |
| `sequences-and-series` | `geometric-series` | geometric | `SPI.IBDPAASL.SEQSER.GEO.SUM_INFINITE.01` |
| `algebra` | `algebraic-foundations` | linear-equations | `SPI.MIDDLE.ALG.INVERSE_OPERATIONS.01` |
| `algebra` | `linear-equations-one-variable` | linear-equations | `SPI.MIDDLE.ALG.LINEQ.TWOSTEP.01` |
| `geometry` | `angles-lines-triangles-quadrilaterals` | angles-figures | `SPI.MIDDLE.GEO.TRIANGLE_ANGLE_SUM.01` |
| `geometry` | `coordinate-geometry-straight-line-graphs` | coordinate-lines | `SPI.MIDDLE.GEO.COORD.MIDPOINT.01` |
| `geometry` | `coordinate-transformations` | transformations | `SPI.MIDDLE.GEO.TRANS.REFLECT_SHAPE.01` |
| `measurement` | `mensuration` | mensuration | `SPI.MIDDLE.MEAS.AREA.RECTANGLE.01` |
| `number` | `signed-numbers` | (none) | `SPI.MIDDLE.NUM.SIGNED_OPERATIONS.01` |
| `proportion` | `ratio-and-proportion` | ratio | `SPI.MIDDLE.RATIO.SHARE_THREE_PART.01` |
| `statistics` | `data-handling-and-probability` | data-handling | `SPI.MIDDLE.STAT.AVG.MEAN_FREQ_TABLE.01` |

A single strand may span multiple ID sub-segments (e.g. `mensuration` covers both `MEAS.PERIM.*` and `MEAS.AREA.*`); and within a strand, several objectives share a topic prefix. This is the variable-depth structure that §3 formalizes.

### 2.6 Generator-capability join (the natural alignment key)

Each generator family exposes a per-module `describe()` function (on the **domain module**, e.g. `domains/proportion/ratio.ts` — *not* on the runtime `GeneratorModule` interface, see §8.1) returning `{generatorId, version, tasks[], answerTypes, objectiveIds, approvalStatus}` — the *generator capability* surface — and each task maps **1:1** to an objective through a per-family `OBJECTIVE_BY_TASK` map under `core/curriculum/`. For example, `core/curriculum/ratio-objective-ids.ts` declares `RATIO_TASKS` (12 slugs) and `OBJECTIVE_BY_TASK` (12 ID values), with a parity test asserting all twelve IDs exist in `SPI.MIDDLE.RATIO.json`. This **task↔objective** join is the registry's authoritative bridge between *"which generator can produce this"* and *"which objective it assesses"*; the registry consumes it, it does not invent a parallel mapping.

Four platform-wide **structured, canonical-first answer contracts** back these objectives — `integer / exact-rational {num,den}`, `quantity (+measure)`, `transformation` descriptor, and `ratio {parts}` (four contracts; `integer`/`exact-rational` are one contract pair). These are distinct from the broader platform `answerType` vocabulary (which also includes `table-completion`, `multiple-choice`, `algebraic-expression`, etc., per `question-item.schema.json` `$defs/answerType`); e.g. ratio's approved `answerTypes` are `[ratio, exact-rational, integer, table-completion, multiple-choice]`. The registry surfaces `answerTypes` per objective from the existing definitions; it does not redefine them.

### 2.7 Inventory invariants (the registry must preserve)

The current state satisfies these invariants, which become **registry load-time assertions** (§5, §11), extending `checkCurriculumGraph`:

1. **70 objectives, all `approved`.** Any drift in count or status is a load-time error to be surfaced, not silently absorbed.
2. **Every objective ID is globally unique** (already enforced by `checkCurriculumGraph` duplicate-id detection).
3. **Every `OBJECTIVE_BY_TASK` value resolves** to a defined objective (already asserted by per-family parity tests).
4. **Every objective validates** against `schemas/curriculum-objective.schema.json` (verified: all 70 match the schema's `objectiveId` regex; all 30 inline alignment entries validate against the existing `{framework, code, label?}` item shape).
5. **No filename dependency:** identity is the `objectiveId`, never the file it lives in.

---

## 3. Objective ID grammar

This section **formalizes the ID grammar that is already in production** and proposes how to validate and govern it. It does **not** introduce a new identifier scheme; all 70 existing IDs already conform and must continue to.

### 3.1 The grammar in use is variable-depth

Empirically (census of all 70 IDs), the identifier is a dot-separated path of **5 or 6 segments**:

| Segment count | Number of IDs | Shape |
|---|---|---|
| 5 | 20 | `SPI . STAGE . DOMAIN . MICRO . NN` |
| 6 | 50 | `SPI . STAGE . DOMAIN . SUB . MICRO . NN` |

The canonical grammar, in EBNF (illustrative — documents existing structure, not to re-implement):

```
objectiveId   = "SPI" , "." , stage , "." , domain , { "." , subsegment } , "." , micro , "." , revision ;
stage         = upperToken ;                 (* e.g. MIDDLE, IBDPAASL *)
domain        = upperToken ;                 (* e.g. RATIO, GEO, SEQSER, MEAS, ALG, STAT, NUM *)
subsegment    = upperToken ;                 (* 0..n; e.g. COORD, TRANS, LINEQ, PERIM, AREA, READ, AVG, ARITH *)
micro         = upperToken ;                 (* smallest assessable skill; e.g. MIDPOINT, NTH_TERM, MEAN_LIST *)
revision      = digit , digit ;              (* the .NN micro-version suffix, two digits, e.g. 01 *)
upperToken    = ucChar , { ucChar } ;
ucChar        = "A".."Z" | "0".."9" | "_" ;
digit         = "0".."9" ;
```

In platform shorthand: **`SPI.<STAGE>.<DOMAIN>[.<SUBSEGMENT(S)>].<MICRO>.<NN>`** — the `[.<SUBSEGMENT(S)>]` being the variable-depth element (zero or more sub-segments between the domain and the micro-skill). Depth is chosen per family by how much intermediate structure the strand needs: `RATIO` is shallow (`SPI.MIDDLE.RATIO.SIMPLIFY.01`); mensuration interposes a perimeter/area sub-segment (`SPI.MIDDLE.MEAS.PERIM.RECTANGLE.01`); the sequences families interpose `ARITH`/`GEO` (`SPI.IBDPAASL.SEQSER.ARITH.NTH_TERM.01`).

### 3.2 Segment semantics

| Position | Role | Fixed? | Allowed values today | Governs |
|---|---|---|---|---|
| 1 | Literal namespace prefix | Yes — always `SPI` | `SPI` | platform identity |
| 2 | **Stage segment** | Controlled (§4) | `MIDDLE`, `IBDPAASL` | maps to `stage` field (`middle-school`, `ibdp-aasl`) |
| 3 | **Domain segment** | Controlled (§4) | `SEQSER`, `ALG`, `GEO`, `MEAS`, `NUM`, `RATIO`, `STAT` | terse key for the `domain` field |
| 4..(n−2) | **Sub-segment(s)** | Controlled (§4), 0..n | `COORD`, `TRANS`, `LINEQ`, `PERIM`, `AREA`, `READ`, `FREQ`, `AVG`, `PROB`, `ARITH`, `GEO` | strand/topic structure |
| n−1 | **Micro-skill** | Per-family, single spelling | e.g. `MIDPOINT`, `TWOSTEP`, `SUM_INFINITE`, `MEAN_FREQ_TABLE` | the 1:1 task target |
| n | **Revision suffix `.NN`** | Two digits | `01` (all 70 today) | objective-definition micro-version |

The algebra foundations objectives are `SPI.MIDDLE.ALG.INVERSE_OPERATIONS.01` and `SPI.MIDDLE.ALG.EXPAND_BRACKETS.01` — five-segment IDs with **no** sub-segment, *not* `SPI.MIDDLE.ALG.FOUNDATIONS.*`. `FOUNDATIONS` is a **file** name and logical grouping, never part of the grammar — an important reminder that the file name is not part of the ID (§2.1).

**Stage-token register.** The ID stage segment (`MIDDLE`, `IBDPAASL`) is the **terse, upper-case key**; the `stage` *field* uses the schema-enum spelling (`middle-school`, `ibdp-aasl`). These are intentionally distinct registers — exactly the pattern the ratio spec already adopts for domain (`RATIO` segment vs. `proportion` field). §4 owns the 1:1 **mapping table** between segment and field spelling.

### 3.3 Allowed character set

Per segment (segments 2..n−1): `A`–`Z`, `0`–`9`, underscore `_`. **No** lower-case, no hyphen, no spaces. Segment separator is the dot `.`. The revision segment is exactly two decimal digits. This is the character set the existing schema regex already enforces; it is restated here so the controlled vocabulary in §4 inherits it as a naming constraint for any *new* segment value. Underscore is the **intra-segment** word separator (`NTH_TERM`); the dot is the **inter-segment** separator. The two are never interchangeable, and a segment never contains a dot.

### 3.4 The `.NN` micro-version suffix

The trailing `.NN` is the **objective-definition revision**, not a question or generator version:

- All 70 objectives are currently at `.01` — the first definition.
- The suffix increments (`.02`, …) **only** if an objective's identity changes such that a new stable ID is warranted, distinct from a `version` semver bump (which handles in-place definition edits).
- IDs are **stable and never reused**: a given `<...MICRO>.NN` always denotes the same skill. Splitting one skill creates two *new* IDs (the arithmetic-sequences split precedent: `find_d`→`COMMON_DIFF.01`, `find_n_for_value`→`TERM_INDEX.01`), it does not re-point an existing one.

**Governance rule (proposal):** bumping `.NN` is a curriculum-authority action recorded in `docs/DECISION_LOG.md`; the prior ID is marked `retired` in the registry rather than deleted, so historical references resolve. (Field-level lifecycle uses the existing `reviewStatus` enum — see §6.)

### 3.5 Validation regex (formalize what exists)

The schema **already** carries a regex, and **all 70 IDs validate against it** (verified):

```
^SPI\.[A-Z0-9]+(\.[A-Z0-9_]+)+\.[0-9]{2}$
```

We **adopt it unchanged** as the normative pattern. Two observations for the registry's validator layer:

1. **The stage segment currently disallows `_`** (it is `[A-Z0-9]+`), while interior segments allow `_`. Both current stage segments satisfy this. If a controlled stage value ever needs an underscore (none does today), that is a schema change requiring §4 governance, not a silent regex relaxation.
2. **The regex enforces structure but not vocabulary.** It accepts any upper-case tokens; it cannot tell that `MIDDLE`/`IBDPAASL` are the only *valid* stages. The registry therefore layers a **three-stage validation**:

| Layer | Check | Enforced by | Failure |
|---|---|---|---|
| L1 — structural | Matches the schema regex; 5–6 segments; `.NN` suffix | `schemas/curriculum-objective.schema.json` (existing) | schema-invalid (hard) |
| L2 — vocabulary | Stage/domain/sub-segments are members of the §4 controlled vocabulary; stage segment ↔ `stage` field consistent | registry validator (proposal, extends `graph-check.ts`) | registry-invalid (hard) |
| L3 — graph | Unique ID; prerequisites resolve; no cycles | `core/curriculum/graph-check.ts` (existing) | error/warning |

Illustrative L2 validator shape (illustrative — not to implement now):

```ts
// Proposal sketch only. Extends the spirit of core/curriculum/graph-check.ts.
interface IdParts { stage: string; domain: string; sub: string[]; micro: string; nn: string; }
function parseObjectiveId(id: string): IdParts | null { /* split on '.', validate L1 shape */ }
function checkIdVocabulary(p: IdParts, vocab: ControlledVocabulary, stageField: string): string[] {
  const errs: string[] = [];
  if (!vocab.stages.has(p.stage)) errs.push(`unknown stage segment '${p.stage}'`);
  if (vocab.stageFieldOf(p.stage) !== stageField) errs.push(`stage segment '${p.stage}' != stage field '${stageField}'`);
  if (!vocab.domains.has(p.domain)) errs.push(`unknown domain segment '${p.domain}'`);
  for (const s of p.sub) if (!vocab.subsegments.has(s)) errs.push(`unknown sub-segment '${s}'`);
  return errs;
}
```

### 3.6 What this formalization explicitly does **not** do

- It does **not** flatten the variable depth to a fixed shape — the 50 six-segment IDs would break, violating output-neutrality.
- It does **not** rename, re-key, or re-spell any existing segment.
- It does **not** widen the character set or change the separator.
- It does **not** change the existing schema regex.

The only *new* artifact proposed is the **L2 vocabulary check** layered on top of the existing structural regex and graph check — a validation addition that touches no objective bytes.

---

## 4. Stage / domain / strand / topic taxonomy

The grammar (§3) fixes the *shape* of an ID; this section fixes the *vocabulary* — the controlled set of values each segment and field may take — and the **governance** by which that set grows. The taxonomy is **derived from current state**, not invented: every value below exists in the 70 objectives today, plus the reserved-but-unused values the schema already admits.

### 4.1 Why a controlled vocabulary

Because L1 (the regex) accepts any upper-case token, two failure modes must be foreclosed:

- **Spelling drift** — `PROP` vs `RATIO`, `TRANSFORM` vs `TRANS`. The platform already forbids competing spellings (the ratio spec's §1.3 string-scan test is the precedent). The registry generalizes this: **one spelling per concept, registered once.**
- **Silent stage/domain proliferation** — a new family inventing `SPI.MS.…` instead of `SPI.MIDDLE.…`. The controlled vocabulary makes the stage segment a *closed set* that only curriculum governance can extend.

The controlled vocabulary is a single registered artifact (proposal: a governed JSON/TS table the registry loads), holding four coordinated tables — **stages, domains, sub-segments, and the field-spelling map** — plus the human-readable **strand** and **topic** vocabularies.

### 4.2 Stage vocabulary (closed set; governance-gated)

| Stage segment (ID) | `stage` field (schema enum) | Status | Objectives |
|---|---|---|---|
| `MIDDLE` | `middle-school` | **in use** | 61 |
| `IBDPAASL` | `ibdp-aasl` | **in use** | 9 |
| *(reserved)* | `preschool-kg` | reserved (schema-admitted, no segment yet) | 0 |
| *(reserved)* | `primary` | reserved | 0 |
| *(reserved)* | `high-school` | reserved | 0 |
| *(reserved)* | `ibdp-aahl` | reserved | 0 |
| *(reserved)* | `ibdp-ai` | reserved | 0 |
| *(reserved)* | `university` | reserved (Phase 1 OUT OF SCOPE) | 0 |
| *(reserved)* | `cross-level` | reserved | 0 |

The seven reserved stages exist in the schema enum but have **no ID stage-segment spelling yet**. Defining a segment for any of them (e.g. choosing `PRIMARY` for `primary`) is a **governance action** (§4.6). University-stage objective architecture is explicitly **out of scope** for Phase 1 and reserved as future only.

### 4.3 Domain vocabulary (closed set)

| Domain segment (ID) | `domain` field | Strands under it | Objectives |
|---|---|---|---|
| `SEQSER` | `sequences-and-series` | arithmetic-sequences, arithmetic-series, geometric-sequences, geometric-series | 9 |
| `ALG` | `algebra` | algebraic-foundations, linear-equations-one-variable | 7 |
| `GEO` | `geometry` | angles-lines-triangles-quadrilaterals, coordinate-geometry-straight-line-graphs, coordinate-transformations | 22 |
| `MEAS` | `measurement` | mensuration | 8 |
| `NUM` | `number` | signed-numbers | 1 |
| `RATIO` | `proportion` | ratio-and-proportion | 12 |
| `STAT` | `statistics` | data-handling-and-probability | 11 |

Note the deliberate **segment ≠ field** register: domain segment `RATIO` ↔ `domain` field `proportion` (the established ratio precedent). The field-spelling map (§4.5) is the single source for these correspondences.

### 4.4 Sub-segment, strand, and topic vocabularies

The **sub-segment** vocabulary (the variable-depth interior tokens) observed today:

| Domain | Sub-segments in use | Example |
|---|---|---|
| `SEQSER` | `ARITH`, `GEO` | `SPI.IBDPAASL.SEQSER.GEO.COMMON_RATIO.01` |
| `ALG` | `LINEQ` (and depth-0 foundations) | `SPI.MIDDLE.ALG.LINEQ.BOTHSIDES.01` |
| `GEO` | `COORD`, `TRANS` (and depth-0 angles) | `SPI.MIDDLE.GEO.COORD.GRADIENT_TWO_POINTS.01` |
| `MEAS` | `PERIM`, `AREA` | `SPI.MIDDLE.MEAS.AREA.TRIANGLE_BASE_HEIGHT.01` |
| `STAT` | `READ`, `FREQ`, `AVG`, `PROB` | `SPI.MIDDLE.STAT.AVG.MEDIAN_LIST.01` |

The **13 strands** (the human-readable `strand` field, §2.5) form the controlled `strand` vocabulary; they follow the **lower-case-hyphenated** convention. **`strand` is schema-optional** (it is not in the objective schema's `required[]`), although all 70 objectives carry it today. The **topic / subtopic / microSkill** fields are free-form descriptive strings — *descriptive*, not *key-bearing* — so a controlled vocabulary is **recommended but not mandatory** for them, whereas the stage / domain / sub-segment vocabularies are **mandatory closed sets** because they participate in the ID key, and the strand vocabulary is a governed closed set applied **present-or-valid** (see §4.5).

Register summary:

| Vocabulary | Casing convention | Closed set? | Key-bearing? | Schema status |
|---|---|---|---|---|
| Stage segment | UPPER, `_`-free | Yes | Yes (ID) | part of `objectiveId` (required) |
| Domain segment | UPPER | Yes | Yes (ID) | part of `objectiveId` (required) |
| Sub-segment | UPPER, `_` allowed | Yes | Yes (ID) | part of `objectiveId` (required) |
| Micro-skill | UPPER, `_` allowed | Per-family, one spelling each | Yes (ID, task join) | part of `objectiveId` (required) |
| `stage` field | lower-hyphen (schema enum) | Yes (schema) | No (display/filter) | required |
| `domain` field | lower-hyphen | Yes | No | required |
| `strand` field | lower-hyphen | Yes (governed, present-or-valid) | No (grouping) | **optional** |
| `topic`/`subtopic`/`microSkill` | free-form English | No (recommended controlled) | No (descriptive) | optional |

### 4.5 The field-spelling map (single source for segment ↔ field)

Because the same concept appears as a terse ID segment *and* a human-readable field with deliberately different spelling, a **single registered map** must own every correspondence so no second spelling can drift in. Illustrative shape (illustrative — not to implement now):

```ts
// Proposal sketch. One registered table; the registry validates IDs and fields against it.
const STAGE_MAP = { MIDDLE: "middle-school", IBDPAASL: "ibdp-aasl" } as const;     // closed
const DOMAIN_MAP = {
  SEQSER: "sequences-and-series", ALG: "algebra", GEO: "geometry",
  MEAS: "measurement", NUM: "number", RATIO: "proportion", STAT: "statistics",
} as const;                                                                          // closed
// strand list is a flat governed set of 13 lower-hyphen tokens; sub-segments a flat governed set.
```

A registry integrity test (extending the per-family parity-test pattern in `core/curriculum/*-objective-ids.ts`) asserts that **for every objective**: `STAGE_MAP[idStageSegment] === stage` and `DOMAIN_MAP[idDomainSegment] === domain`, and — phrased as **present-or-valid** — *if* `strand` is present it must be a registered value, and no objective uses a stage/domain/sub-segment value absent from the registered vocabulary. (Making `strand` mandatory would be a separate, additive, owner-gated schema change; this document does not assume it.)

### 4.6 Governance — how new values are admitted

Adding a value to any **closed set** (stage segment, domain segment, sub-segment, strand) is a **curriculum-authority governance action**, not an incidental side effect of building a generator. The proposed gate:

| Action | Who decides | Recorded in | Constraint |
|---|---|---|---|
| New **strand** under an existing domain | Curriculum authority | `DECISION_LOG.md` + vocabulary table | lower-hyphen, unique, no synonym of an existing strand |
| New **sub-segment** | Curriculum authority | `DECISION_LOG.md` + vocabulary table | UPPER, unique within its domain, one spelling |
| New **domain** (segment + field) | Curriculum authority | `DECISION_LOG.md` + `DOMAIN_MAP` | both spellings registered together; segment ≠ existing |
| New **stage** (segment + field) | Curriculum authority; field must already be in the schema `stage` enum (else schema change first) | `DECISION_LOG.md` + `STAGE_MAP` | schema-enum-backed; segment `_`-free |
| **Reuse / re-spell** an existing value | **Forbidden** | — | one spelling per concept, ever |

Three standing rules:

1. **One spelling per concept, registered once.** A new value may not be a synonym, abbreviation, or case-variant of an existing one. (Generalizes the ratio spec's no-`_UNITARY`, no-`PROP` discipline platform-wide.)
2. **Closed sets are append-only.** Values are added, and may be marked `retired` in the registry, but are never silently removed or repointed — historical IDs must keep resolving (consistent with §3.4).
3. **Schema-enum precedence for stages.** A stage segment may only be introduced for a `stage` field value the schema's `stage` enum already lists; introducing a genuinely new stage is a *schema* change that precedes the vocabulary change.

### 4.7 Output-neutrality of the taxonomy

Establishing this controlled vocabulary changes **no objective bytes**: every value in §4.2–§4.4 is *read off the existing 70 objectives*. The vocabulary table and its consistency test are *new validation artifacts*, not edits to approved content — consistent with §1.3. The taxonomy's first job is simply to *describe and lock* what is already true, so the tenth family and the alignment layer cannot introduce drift.

---

## 5. Unified objective registry model

### 5.1 Purpose and the load-bearing constraint

The platform today can answer questions about a *single* family — "what does `gen.proportion.ratio` assess?" — by reading `core/curriculum/ratio-objective-ids.ts` and `curriculum/objectives/SPI.MIDDLE.RATIO.json`. It cannot yet answer cross-family questions in one place: *what objectives exist platform-wide; where does each belong; which generator and task assess it; what answer types and difficulty bands are reachable.* The **unified objective registry** is the single query layer that answers exactly these questions, and nothing more.

> **The per-family JSON files under `curriculum/objectives/` remain the single source of truth for objective *definitions*. The registry is a derived, read-only aggregate. It never holds an authoritative copy of an objective; it indexes the files.**

This is the SAFE architecture, output-neutral by construction: building a loader/index changes no approved objective bytes, generator output, fixture, or review pack. The 70 approved objectives across 11 files keep their current shape; the registry is a *view* over them.

### 5.2 Layered architecture

```
  curriculum/objectives/*.json   ← SOURCE OF TRUTH (11 files, 70 objectives, all approved)
            │  (schema: schemas/curriculum-objective.schema.json)
            ▼
  Objective LOADER               ← validates each record against the schema, asserts
            │                       filename/stage/domain coherence, fails closed on drift
            ▼
  Objective REGISTRY (in-memory)  ← one aggregated, indexed, queryable collection
            │
            ├── joins core/sdk/sequence-registry.ts  (generator id/version/tasks/approvalStatus — §8)
            ├── joins per-module describe()           (objectiveIds/answerTypes — §8)
            ├── joins core/curriculum/*-objective-ids.ts (task↔objective maps — §8)
            └── feeds core/curriculum/graph-check.ts  (prerequisite DAG — §7)
```

The loader and registry are **new infrastructure** (`core/curriculum/`); they sit *above* the existing files and *beside* `graph-check.ts` and the `*-objective-ids.ts` maps, reusing them rather than replacing them. No existing file is rewritten to stand the registry up. This mirrors the generator side: `core/sdk/sequence-registry.ts` is already "the single source of truth for *which generators exist*" — a thin registry that *adapts* immutable, approved implementations to a common shape without owning them. The objective registry is its curriculum-side twin.

### 5.3 The registry record shape

Each registry entry is a **projection** of one curriculum-objective record plus *derived* join fields. It introduces no new authoritative fields; every authoritative value is copied verbatim from the source JSON (validated against the schema), and the derived block is computed at load time from the generator registry, the per-module `describe()`, and the task maps.

*Illustrative — not to implement now:*

```ts
// RegistryEntry: a read-only projection. Authoritative fields mirror the
// source JSON 1:1; `derived` is computed by the loader and is never persisted
// back into curriculum/objectives/*.json.
interface RegistryEntry {
  // ----- authoritative (verbatim from the source objective record) -----
  objectiveId: string;            // e.g. "SPI.MIDDLE.RATIO.SIMPLIFY.01"
  stage: string;                  // "middle-school" | "ibdp-aasl" | ...
  domain: string;                 // "proportion" | "sequences-and-series" | ...
  strand?: string;                // optional in schema; "ratio-and-proportion" | ...
  topic?: string; subtopic?: string; microSkill?: string;
  objectiveWording: string;
  answerTypes: string[];          // declared answer types for the objective
  difficultyRange?: { min: number; max: number };
  prerequisites?: string[];
  relatedObjectives?: string[];
  crossDomainRelationships?: string[];
  externalAlignments?: { framework: string; code: string; label?: string }[];  // existing inline hook (§9)
  reviewStatus: "draft" | "proposed" | "curriculum-reviewed" | "approved"
              | "approved-for-implementation" | "published" | "revised" | "retired";
  version: string;

  // ----- provenance (computed by the loader) -----
  sourceFile: string;             // "SPI.MIDDLE.RATIO.json" — for traceability

  // ----- derived (computed; the JOIN layer, see §8) -----
  derived: {
    generatorId?: string;         // e.g. "gen.proportion.ratio" (undefined ⇒ no generator yet)
    generatorVersion?: string;
    tasks: string[];              // task slugs that assess this objective (usually one)
    reachableAnswerTypes: string[];   // answer types actually produced via those tasks
    supportedInteractions: string[];  // free-response / multiple-choice, from the task maps
    coverageTier: "G2_approved" | "G1_pendingOnly" | "G0_noGenerator";  // §8/§10 unified vocabulary
    approvalStatus?: "approved" | "pending-review" | "rejected";
  };
}
```

The split is deliberate and is itself a governance rule: **authoritative fields are read-only mirrors; `derived` is recomputed on every load and is never written back.** A reviewer reading the registry can always tell which values are owned by the curriculum file and which are joins. The `coverageTier` enum here is the single coverage vocabulary used by §8 and §10 (`G2_approved` ≡ "covered & approved", `G1_pendingOnly` ≡ "covered, generator pending", `G0_noGenerator` ≡ "defined, uncovered").

### 5.4 Query API surface (conceptual)

The registry exposes a small, stable, read-only query surface — enough to power coverage reports, Studio pickers, blueprint authoring, and the graph checks, and no more. This is the *only* sanctioned way for the rest of the platform to ask cross-family curriculum questions.

| Query | Conceptual signature | Answers |
|---|---|---|
| Lookup | `get(objectiveId) → RegistryEntry?` | "What is this objective, and what assesses it?" |
| Existence | `has(objectiveId) → boolean` | Used by graph checks and alignment validation (§7, §9) |
| By placement | `find({ stage?, domain?, strand?, topic? }) → RegistryEntry[]` | "What objectives live in RATIO / proportion / middle-school?" |
| By generator | `byGenerator(generatorId) → RegistryEntry[]` | "Which objectives does `gen.proportion.ratio` assess?" |
| By task | `byTask(generatorId, task) → RegistryEntry?` | The 1:1 task→objective resolution (§8) |
| By answer type | `byAnswerType(type) → RegistryEntry[]` | "Which objectives are assessable as `ratio` / `quantity` / `transformation`?" |
| By difficulty | `inBand(min, max) → RegistryEntry[]` | Blueprint/coverage queries over difficulty bands |
| By status | `byReviewStatus(status) → RegistryEntry[]` | "What is still `revised` / `retired`?" (§6) |
| Coverage | `coverage() → CoverageReport` | The objective↔generator join, incl. *uncovered* objectives (§8/§10) |
| Integrity | `graph() → GlobalGraphReport` | Delegates to `checkCurriculumGraph` over the *global* set (§7) |

All queries return **copies or read-only views**; the registry is immutable after load. There is no `set`, `update`, or `delete` — definition changes happen by editing the source JSON files under curriculum governance (§6) and reloading.

### 5.5 Load-time invariants (fail-closed)

The loader enforces these invariants when aggregating the 11 files; any violation fails the load (and CI), exactly as the per-family graph tests fail today:

1. **Schema validity** — every record validates against `schemas/curriculum-objective.schema.json` (incl. the `objectiveId` pattern and the existing inline `externalAlignments` item shape).
2. **Global ID uniqueness** — no `objectiveId` appears in two files. (Today `graph-check.ts` checks duplicates *within* a passed list; the registry passes the *global* list, lifting this to a platform-wide guarantee.)
3. **Filename ↔ content coherence** — a record's `stage`/`domain` is consistent with its file's intended placement, so the file layout stays a faithful partition of the ID space.
4. **Task-map parity** — for every objective referenced by a `*-objective-ids.ts` map (`OBJECTIVE_BY_TASK`), the registry contains that objective; for every family, its `OBJECTIVE_*_IDS` all resolve. This is the registry-level statement of the parity tests that already gate the families.
5. **Derived determinism** — the `derived` block is a pure function of (source files + generator registry + describe() + task maps); two loads of the same inputs yield byte-identical projections, so the registry can be snapshot-tested without flakiness.

The registry therefore *adds* a global integrity guarantee while *removing* nothing.

---

## 6. Objective lifecycle and versioning model

### 6.1 Reuse the existing lifecycle — do not invent one

The objective lifecycle is **already defined** by the `reviewStatus` enum in `schemas/curriculum-objective.schema.json`:

`draft → proposed → curriculum-reviewed → approved → approved-for-implementation → published → revised → retired`

Phase 1 does not add, rename, or reorder these states. It **formalizes their meaning and governance** so the curriculum lifecycle mirrors the generator-approval lifecycle that already governs `core/sdk/generator-module.ts` (`approved` / `pending-review` / `rejected`). The two lifecycles run in parallel on the two sides of the same item. Crucially, the **production-visible curriculum tier is `approved`** — matching the real state, where all 70 objectives are `reviewStatus: "approved"` and all nine families' generators are `approvalStatus: "approved"` and selectable in normal Studio + production:

| Curriculum side (`reviewStatus`) | Generator side (`approvalStatus`) | Meaning |
|---|---|---|
| `approved` | `approved` | **The live production state of all nine families today:** definition is locked and the generator is production-visible. |
| `approved` / `approved-for-implementation` | `pending-review` | Definition is locked; generator is being built and machine-validated but is not yet production-visible (review mode only). |
| `revised` | (new generator version under `pending-review`) | A change is in flight; old artifacts stay frozen until re-approval. |
| `published` | `approved` | An **optional, later** state for content explicitly promoted past `approved`; *not* required for production visibility. |
| `retired` | family/version unregistered | Definition withdrawn; no new items. |

The schema documents that `approved-for-implementation` means "definition is curriculum-approved and cleared for generator build while the generator itself remains pending-review (gated from production)." `published` is reserved for an optional future promotion and is **not** a precondition for an objective being in production. Phase 1 takes these documented states and makes them the governing contract for the whole family fleet.

### 6.2 Immutability of approved definitions

The central rule, inherited from the generator side ("the approved, immutable implementations"):

> **Once an objective record reaches `approved` (or `approved-for-implementation` / `published`), its identity-bearing fields are frozen for that `(objectiveId, version)`.** The frozen fields are at minimum: `objectiveId`, `objectiveWording`, `answerTypes`, `stage`, `domain`, the placement fields a generator and its fixtures depend on, and any existing inline `externalAlignments` entries.

Freezing is what makes the nine approved families safe. Each approved generator's outputs, golden vectors, review packs, and `docs/review/*_manifest.json` (with their `sha256` artifact-identity) were produced against a *specific* objective wording and ID. If an approved wording could be edited in place, every dependent artifact's provenance would silently rot. Immutability of approved definitions is therefore the precondition for the manifest/sha256 identity model to mean anything.

### 6.3 Wording change → new version; identity change → new ID

The decisive design question: *when does a change produce a new `version` of the same `objectiveId`, and when a new `objectiveId`?*

- **Same `objectiveId`, bump `version`** when the change is a *refinement that preserves the assessable claim*: clarified phrasing, tightened success criteria, added vocabulary/notation, corrected typo, narrowed difficulty band — such that an item generated under the old wording is still valid under the new. The objective passes through `revised` and back to `approved`; the prior version is preserved in history (git tags + the record's `version`/`modifiedAt`), exactly as generator versions `v1.0.0`/`v1.0.1` are preserved.

- **Mint a NEW `objectiveId`** when the change *alters the assessable skill itself*: a different answer type, a different micro-skill, a split, a merge, or any change that would invalidate previously generated items. The old ID is **not** edited; it moves toward `retired`/superseded and the new ID takes over. This preserves the load-bearing invariant that **the SPI objective ID is the stable single source of truth** — IDs are never repurposed.

A compact decision rule:

> *Would an item correctly generated against the OLD definition still be correct and on-objective under the NEW definition?*
> **Yes → new `version`. No → new `objectiveId`.**

### 6.4 Retired and superseded behavior

`retired` is a terminal state. A retired objective:

- is **never deleted** — its record and ID remain in the source file so historical items, manifests, and external alignments that reference it stay resolvable;
- is excluded from *new* item generation and Studio pickers (the registry's `byReviewStatus`/coverage queries treat it as out-of-production);
- when replaced, carries an explicit supersession link to its successor ID.

**Successor-link carrier (committed).** A supersession is expressed through a thin, clearly-labelled additive **`supersededBy`** convention — a single optional field carrying the successor `objectiveId` — so §7.4's retired-dependence check and §10's mapping logic have one defined field to read. (`supersededBy` is preferred over overloading `relatedObjectives` precisely because it is *typed*: it states "succession", not mere relatedness. Introducing it is an additive, owner-gated schema change handled like any other; until then no objective is retired, so no live data depends on it.) *Illustrative — not to implement now:* `"supersededBy": "SPI.MIDDLE.RATIO.SIMPLIFY.02"`.

### 6.5 How approved generators and review packs freeze IDs and wording

This enforcement mechanism already exists — Phase 1 only names it as the curriculum-side rule:

1. An approved family in `core/sdk/sequence-registry.ts` pins exact task slugs, and each slug maps 1:1 to an `objectiveId` through `*-objective-ids.ts` (`OBJECTIVE_BY_TASK`). The parity test asserts those IDs **exist in the curriculum file**.
2. The family's review pack and `docs/review/*_manifest.json` capture the artifact identity (`versionTags` + `sha256`) of outputs generated against a specific wording.
3. Therefore: **an approved objective's ID and wording cannot move without breaking a parity test and invalidating a manifest hash.** The freeze is mechanical, not procedural.

The registry makes this freeze *legible*: `byReviewStatus("approved")` joined with `byGenerator(...)` yields exactly the set of `(objectiveId, version)` pairs under manifest lock — the set Phase 1 must not perturb. This is the operational meaning of "Phase 1 is output-neutral."

---

## 7. Prerequisite DAG model

### 7.1 From per-family graphs to one global graph

Each family already has a graph test (`coordinate-lines-graph.test.ts`, `mensuration-graph.test.ts`, `ratio-graph.test.ts`, `stats-graph.test.ts`, `transformations-graph.test.ts`, plus `graph-check.test.ts`), all running `checkCurriculumGraph(objectives)` over a *family-scoped* list. That function detects **duplicate IDs** (error), **prerequisite cycles** (error; DFS white/gray/black colouring), and **unresolved prerequisites** (warning).

The Phase-1 model runs that same checker over the **global union of all 70 objectives** (sourced through the registry of §5) and extends its edge set and diagnostic classification. This is an *extension* of a trusted component, not a rewrite. The global graph is built from three real schema fields:

- `prerequisites[]` — directed "must-master-first" edges (the DAG proper);
- `relatedObjectives[]` — lateral, non-prerequisite links (informational; **excluded from cycle detection**, since lateral links are legitimately symmetric);
- `crossDomainRelationships[]` — synoptic links across domains (validated for resolvability, but not treated as ordering edges).

Only `prerequisites[]` forms the acyclic ordering. This matches the current `graph-check.ts`, which builds its adjacency solely from `prerequisites`.

### 7.2 The grounded reason this matters now

The current data already contains cross-family/cross-stage prerequisite references that are **not defined** in the present 70-objective set, e.g.:

- `SPI.MIDDLE.ALG.SUBSTITUTION.01`
- `SPI.MIDDLE.NUM.INTEGERS_NUMBER_LINE.01` (referenced by `SPI.MIDDLE.NUM.SIGNED_OPERATIONS.01`)
- `SPI.MIDDLE.GEO.TRIANGLE_CLASSIFY.01`
- `SPI.MIDDLE.GEO.ANGLE_MEASURE_NOTATION.01`
- `SPI.MIDDLE.ALG.NOTATION_SUBSTITUTION.01`

Today `graph-check.ts` classifies every such reference as a **warning** — "unresolved prerequisite … (may be defined in another stage not yet loaded)" — the correct conservative behavior *when only one family is in scope*. But once the **global** registry is the input, "defined in another stage not yet loaded" is no longer valid: the whole curriculum *is* loaded. These are **referenced-but-undefined** IDs (distinct from objectives that exist but lack a generator — see §10.3). The global DAG model re-classifies them with more precision than a single warning bucket.

### 7.3 Diagnostic taxonomy for the global DAG

| Diagnostic | Severity | Definition | Source of truth |
|---|---|---|---|
| Duplicate ID | **error** | Same `objectiveId` in two records | already in `graph-check.ts` |
| Prerequisite cycle | **error** | Directed cycle over `prerequisites[]` | already in `graph-check.ts` |
| **Known-baseline referenced-undefined** | **non-blocking (recorded)** | A `prerequisites[]` target that exists in **no** file AND is in the committed known-baseline set (§7.5) | the existing approved data's referenced-but-undefined IDs, frozen as a baseline |
| **New referenced-undefined** | **error** (global) | A `prerequisites[]` target that exists in **no** file AND is **not** in the known-baseline set | a regression: a reference introduced after the baseline was frozen |
| Retired-objective dependence | **error** | A *live* objective whose prerequisite resolves to a `retired` record | new (depends on §6 status) |
| Unapproved/placeholder dependence | **warning** | An approved/published objective whose prerequisite resolves to a `draft`/`proposed` record | new (governance signal) |
| Invalid cross-domain link | **warning** | A `crossDomainRelationships[]` target that does not resolve, or points within the *same* domain | new |
| Dangling lateral link | **warning** | A `relatedObjectives[]` target that does not resolve | new |

**This resolves the errors-vs-output-neutrality contradiction (owner correction A).** Promoting *every* referenced-undefined to a blocking error would be self-contradictory: the proposal also forbids authoring the missing foundational objectives in Phase 1 and requires output-neutrality, so the gate could never pass without doing out-of-scope work. The resolution is the **known-baseline policy** (§7.5): the referenced-undefined IDs that *already exist* in the approved data (the five in §7.2 and any siblings) are recorded once in a committed baseline and reported as `knownBaselineReferencedUndefined` (non-blocking, stable, visible) — Phase 1 neither blocks on them nor authors them. Only a **new** referenced-undefined introduced *after* the baseline is frozen is a blocking error. The registry's job is to *report the gap precisely and stop the gap from growing*, not to fill it.

### 7.4 Approval-aware layering

Because the DAG is built over the global set, the checker can reason about *approval consistency*, which the per-family checker cannot:

> **An `approved`/`published` objective must not depend (via `prerequisites[]`) on an objective still `draft`/`proposed`, nor on a `retired` one.** A solid foundation cannot rest on a planned placeholder or a withdrawn skill.

This makes the prerequisite graph a *governance* instrument, not merely structural. The check is a pure function of the registry's status fields (§6), the `supersededBy` carrier (§6.4), and the prerequisite edges, composing cleanly with the existing `GraphReport`:

*Illustrative — not to implement now:*

```ts
// Global report extends the existing GraphReport with the eight owner-specified buckets (correction A).
interface GlobalGraphReport extends GraphReport {           // ok, objectiveCount, errors, warnings
  knownBaselineReferencedUndefined: string[]; // referenced-undefined IDs in the committed baseline (non-blocking)
  newReferencedUndefined: string[];           // referenced-undefined IDs NOT in the baseline (BLOCKING error)
  retiredDependence: Edge[];                   // live → retired (error)
  placeholderDependence: Edge[];               // approved/published → draft/proposed (warning)
  invalidCrossDomain: Edge[];                  // unresolved or same-domain cross-links (warning)
  danglingRelated: Edge[];                     // unresolved relatedObjectives links (warning)
}
```

`ok` is now `errors.length === 0 && newReferencedUndefined.length === 0` — `knownBaselineReferencedUndefined` does NOT affect `ok`. A single CI gate — the registry's `graph()` query (§5.4) — guards the whole curriculum.

### 7.5 Known-baseline referenced-undefined policy (final, binding — owner correction A)

The platform's existing approved objective data already references prerequisite IDs that are not (yet) defined as objectives (§7.2). Because Phase 1 must be **output-neutral** and **must not author new objectives**, these pre-existing gaps cannot be treated as blocking errors without making the gate unsatisfiable. The final rule:

1. **Record the baseline.** Every referenced-but-undefined prerequisite ID present in the *current approved objective set* is enumerated once and written to a committed **registry gap report** plus a committed **known-baseline set** (an explicit, sorted ID list — illustrative location `curriculum/registry/known-baseline-referenced-undefined.json`, committed with the Phase 1 implementation).
2. **The baseline does not block Phase 1.** Authoring the missing foundational objectives is explicitly out of scope; the known baseline is reported, not gated.
3. **New gaps block.** Any referenced-but-undefined prerequisite introduced *after* the baseline is frozen is a **blocking error** (`newReferencedUndefined`).
4. **No artifact may grow the gap.** Any generator, objective, review pack, or alignment artifact introduced after Phase 1 must not create a new unresolved prerequisite reference.
5. **Eight report buckets.** The global graph report contains, separately: `errors`, `warnings`, `knownBaselineReferencedUndefined`, `newReferencedUndefined`, `retiredDependence`, `placeholderDependence`, `invalidCrossDomain`, `danglingRelated`.
6. **The CI gate FAILS when** any of: duplicate IDs exist; a prerequisite cycle exists; a live objective depends on a `retired` objective; `newReferencedUndefined` is non-empty; a generator's objective references do not resolve; a review-pack's objective references do not resolve; a standards-alignment SPI reference does not resolve; approved-objective immutability is violated; or approved-family fixture drift occurs.
7. **The CI gate PASSES when** the only unresolved prerequisite references are *exactly* the approved known-baseline set, the known-baseline set is explicitly reported, and no new unresolved references are introduced.
8. **Coverage distinguishes three kinds** (§10): `G0_noGenerator` — objectives that **exist** but have no generator; `knownBaselineReferencedUndefined` — IDs that **do not yet exist** as objectives (recorded baseline); `newReferencedUndefined` — IDs that do not exist and are **not** baseline (blocking errors).
9. **Phase 1 exit criterion (revised wording).** Not "zero referencedUndefined", but: **"zero NEW referenced-undefined IDs; the known-baseline referenced-undefined set is recorded, stable, and separately reported."**
10. **Future phase (reserved, separately gated).** The known-baseline list is the authoritative backlog that should drive a later **foundational objective-authoring phase** — explicitly out of this registry phase and gated by a separate owner approval (§16).

A baseline entry is *retired from the baseline* only when the corresponding objective is later authored (the reference then resolves) — never by silently re-classifying it; the baseline file shrinks only as real objectives are added in that future, separately-approved phase.

---

## 8. Generator capability mapping

### 8.1 The join that powers coverage

Coverage — "which approved objectives are assessable, by which generator, through which task, producing which answer types, in which difficulty bands" — is a **join** across four sources that all already exist. A precise note on *where* each piece lives, because it determines implementability:

| Source | Provides | Real artifact |
|---|---|---|
| Generator **registry** | `generatorId`, `version`, `tasks[]`, `approvalStatus`, family `label` | `core/sdk/sequence-registry.ts` (`GENERATORS`, `approvedGenerators()`); these are the fields on the runtime `GeneratorModule` interface (`core/sdk/generator-module.ts`: `{id, version, label, tasks, approvalStatus?, generate, validate, serialize}`) |
| Per-module **`describe()`** | `objectiveIds`, `answerTypes`, richer `tasks` | the **domain generator modules** (`domains/<area>/<family>.ts`, e.g. `domains/proportion/ratio.ts`). **`describe()` is NOT on `GeneratorModule`** — the runtime interface deliberately omits it (documented in `GENERATOR_STANDARD.md`); it is an exported function on each domain module, joined to the registry entry by `generatorId`. |
| Task→objective map | 1:1 `task → objectiveId` | `core/curriculum/*-objective-ids.ts` (`OBJECTIVE_BY_TASK`) |
| Objective **registry** | objective placement, declared `answerTypes`, `difficultyRange`, `reviewStatus` | §5 registry over `curriculum/objectives/*.json` |

**Authoritative join key.** Because `describe()` is not reachable through the registry, the registry's `derived` block (§5.3) is built primarily from the **`OBJECTIVE_BY_TASK` maps plus the manifest `objectiveIds[]`** — both of which the registry already has or can read — with `describe().objectiveIds` used as a **cross-check** rather than the primary source. Wiring `describe()` into the registry/index is then a small, additive step (importing each domain module's exported `describe()` and keying it by `generatorId`); it is not required for the core join, which the task maps already make total and unambiguous. Either way, because every task maps **1:1** to an objective via `OBJECTIVE_BY_TASK`, the join is total in both directions — no fuzzy matching anywhere.

### 8.2 The capability chain, concretely

Worked through the ratio family (all values real):

```
generator   gen.proportion.ratio  (registry: approvalStatus "approved", v1.0.2)
   task     "simplify"            ──OBJECTIVE_BY_TASK──▶  SPI.MIDDLE.RATIO.SIMPLIFY.01
                                                          │ objective answerTypes: ["ratio", ...]
                                                          │ difficultyRange: { min: 1, max: 3 }
   interaction  free-response + multiple-choice  (SUPPORTED_INTERACTIONS_BY_TASK)
   answer-type  "ratio"  (ANSWER_TYPES_BY_TASK)          (cross-checked vs describe() in domains/proportion/ratio.ts)
```

The chain is closed and *cross-checkable*: the answer type the generator's task produces (`ANSWER_TYPES_BY_TASK`) must be a member of the objective's declared `answerTypes` in `SPI.MIDDLE.RATIO.json`. The registry can therefore assert **answer-type consistency** as a load invariant — a generator task may not claim to assess an objective via an answer type the objective does not declare. This is a free, mechanical correctness check falling directly out of the join.

### 8.3 Answer types and difficulty bands as reachable sets

Two derived sets are especially load-bearing for blueprint authoring and coverage:

- **Reachable answer types** for an objective = the union of answer types across all generator tasks mapping to it (constrained to be a subset of the objective's declared `answerTypes`). The four structured/canonical-first contracts — `integer / exact-rational {num,den}`, `quantity (+measure)`, `transformation` descriptor, `ratio {parts}` — plus the broader vocabulary (`table-completion`, `multiple-choice`, `algebraic-expression`, etc., per `question-item.schema.json`) flow through here. The registry's `byAnswerType(type)` query is the inverse index.
- **Difficulty bands** come from the objective's `difficultyRange {min,max}` (platform scale 1–5). The registry's `inBand(min,max)` query answers "which objectives can a blueprint draw on for a given difficulty target," and the join tells the author *which generator/task actually produces* items in that band.

These per-family interaction/answer-type maps (`SUPPORTED_INTERACTIONS_BY_TASK`, `MC_ELIGIBLE_TASKS`, `MC_ONLY_TASKS`, `ANSWER_TYPES_BY_TASK`) live in `core/curriculum/*-objective-ids.ts` alongside `OBJECTIVE_BY_TASK`, family by family; where a family does not yet expose a given map, the coverage report (§10) treats that signal as absent rather than failing, so the model is grounded family-wide rather than inferred from ratio alone.

### 8.4 The coverage report

The capstone query, `coverage()`, partitions the global objective set against the generator fleet, using the **single coverage vocabulary** shared with §5.3 and §10.3:

| Bucket (CoverageReport key) | Tier (§5.3/§10.3) | Definition |
|---|---|---|
| `coveredApproved` | **G2_approved** | objective is `approved`/`published` AND reached by an `approved` generator task — the production-ready core |
| `coveredPending` | **G1_pendingOnly** | reached only by a `pending-review` generator — in flight, review-mode only |
| `definedUncovered` | **G0_noGenerator** | objective **exists** but no generator task maps to it — a real curriculum gap (e.g. the foundational `NUM`/`ALG` objectives) |
| `knownBaselineReferencedUndefined` | (not a tier) | an ID referenced (as prereq) that has **no record** AND is in the committed baseline (§7.5) — recorded, non-blocking |
| `newReferencedUndefined` | (not a tier) | an ID referenced that has **no record** AND is **not** baseline — a §7 **blocking error**, surfaced here too |
| `orphanedTasks` | (not a tier) | a generator task whose `OBJECTIVE_BY_TASK` target is missing/retired — a parity failure; must never occur for an approved family |

The three tiers `G2/G1/G0` and the three bucket names `coveredApproved/coveredPending/definedUncovered` are **synonyms** for the same partition over objectives that *exist*. The owner's correction-A distinction is explicit here (§7.5): **`G0_noGenerator`** = an objective that **exists** but is uncovered; **`knownBaselineReferencedUndefined`** = an ID that **does not yet exist** as an objective but is a recorded baseline gap (non-blocking); **`newReferencedUndefined`** = an ID that does not exist and is **not** baseline (a blocking error). `*ReferencedUndefined` and `orphanedTasks` are *not* coverage tiers (they name ID/task conditions, not classifications of existing objectives).

*Illustrative — not to implement now:*

```ts
interface CoverageReport {
  coveredApproved: string[];                    // G2 — production core
  coveredPending: string[];                     // G1 — review-mode only
  definedUncovered: string[];                   // G0_noGenerator — objective EXISTS, no generator yet
  knownBaselineReferencedUndefined: string[];   // referenced ID, no record, in the committed baseline (non-blocking)
  newReferencedUndefined: string[];             // referenced ID, no record, NOT baseline (§7 BLOCKING error)
  orphanedTasks: { generatorId: string; task: string; objectiveId: string }[];
  byGenerator: Record<string, string[]>;        // generatorId → objectiveIds assessed
}
```

### 8.5 Why this is safe and output-neutral

The capability mapping reads the generator registry, the per-module `describe()`, the task maps, and the objective files — and **writes nothing back**. It introduces no new authoritative state: every value in the coverage report is a projection of data that already gates the nine approved families by test. The join is output-neutral by the same argument as §5: no generator output, fixture, golden vector, review pack, or manifest changes because the platform learned to *describe* its own coverage in one place — in the same spirit as `core/sdk/sequence-registry.ts` being "the single source of truth for which generators exist."

---

## 9. Standards / alignment mapping model

### 9.1 The load-bearing principle

The SPI objective ID is the single, stable source of truth. The alignment layer expresses exactly one relation:

> **SPI `objectiveId` → optional external standard reference(s).**

The relation is unidirectional and the SPI side is always the anchor. External standards (IGCSE, IB, Singapore, Lebanese official curriculum, Common Core, others) are *referenced by* SPI objectives; they never replace or rename an SPI objective, become a foreign key the engine resolves *from* (a reverse lookup is a derived, read-only index, never the authority), or gate generator/objective approval.

Concretely: the 70 approved objectives remain the spine that `core/curriculum/graph-check.ts` validates (`checkCurriculumGraph` — duplicate-id and cycle as errors, unresolved prerequisites as warnings; `requireObjectives` as a presence-check helper), the spine that `OBJECTIVE_BY_TASK` maps generator tasks onto, and the spine that the manifests pin by sha256. An alignment is **annotation about** an objective, not part of its identity. Removing every alignment record must leave the engine fully functional — the design invariant.

### 9.2 What already exists (build on, do not reinvent)

`schemas/curriculum-objective.schema.json` already carries an optional `externalAlignments` array on each objective:

```jsonc
// EXISTING schema (curriculum-objective.schema.json, lines ~86–99) — already in place
"externalAlignments": {
  "type": "array",
  "items": {
    "type": "object",
    "additionalProperties": false,            // ← note: forbids extra keys
    "properties": {
      "framework": { "type": "string" },
      "code":      { "type": "string" },
      "label":     { "type": "string" }
    },
    "required": ["framework", "code"]          // ← framework + code mandatory
  }
}
```

This is a real, deliberate, and **broadly used** hook. **30 of the 70 objectives already populate it**, across 7 of the 11 files, referencing **three frameworks**: Cambridge IGCSE Mathematics 0580 (×21), Singapore Lower Secondary Mathematics (×14), and IB Mathematics AA SL (×9). The four arithmetic-sequences objectives in `SPI.IBDPAASL.SEQSER.ARITH.json` are representative — each carries `{framework: "IB Mathematics AA SL", code: "Topic 1", label: "Number and algebra"}`. These 30 records are inside approved, **sha256-frozen** files. Phase 1 **formalizes the model and governance around this hook; it does not invent the field, and it does not touch the 30 existing entries.** The decision below is where the *rich, governed* alignment record should live relative to this minimal inline hook.

### 9.3 Decision: a separate alignment store keyed by SPI id

**Recommendation: the rich, owner-mandated alignment record lives in a dedicated, append-friendly alignment store keyed by SPI objective id — physically separate from the objective definition files — and the existing inline `externalAlignments` array is left UNCHANGED (it cannot carry the rich fields anyway, being `additionalProperties: false` with only `{framework, code, label?}`).**

| Option | Where alignments live | Verdict |
|---|---|---|
| A. Inline only | Widen `externalAlignments` on each objective record | **Rejected as primary.** The existing inline item is `additionalProperties: false` / `required: [framework, code]`; carrying `standardSet`/`standardVersion`/`alignmentType`/`status`/`notes`/`source`/`date`/`version` would **fail the existing validator** and require changing `curriculum-objective.schema.json` bytes (and the compiled-validator sha256). Worse, the inline hook is **already populated on 30 approved, sha256-frozen objectives**, so alignment churn (a new framework version, a confidence change, a reviewer note) would rewrite frozen approved files and break output-neutrality. This coupling risk is *real and current*, not hypothetical. |
| B. Separate store, SPI-keyed (**chosen**) | New files under `curriculum/alignments/` (one file per framework; records keyed by `linkedSpiObjectiveIds`) | **Chosen.** Alignments evolve independently; approved objective bytes never change because an external framework changed; the objective schema and compiled validator stay byte-frozen. The SPI id remains the join key, preserving directionality. |
| C. Inside generator manifests | Add alignment to `docs/review/*_manifest.json` | **Rejected.** Manifests are sha256 artifact-identity snapshots of a *generator version*; alignments are curriculum facts about *objectives* and outlive any one generator version. |

Rationale, in priority order:

1. **Output-neutrality (binding).** No approved objective file, fixture, golden vector, or manifest may change because the alignment layer is being designed. A separate store guarantees this structurally — the alignment files are new artifacts, never in the existing manifests' sha256 set. The 30 existing inline entries are likewise frozen.
2. **Schema/validator stay frozen.** Because the rich record lives in a **new** schema (`schemas/standard-alignment.schema.json`), `curriculum-objective.schema.json` gains no property; its bytes and the compiled validator's sha256 are unchanged.
3. **Independent lifecycle.** External frameworks version on their own cadence (IGCSE 0580 syllabus revisions, Common Core editions). Alignments must be re-reviewable and re-versionable without reopening curriculum review of the objective.
4. **Directionality preserved physically.** The store is keyed *by SPI id*; the framework is a value inside the record. A reverse lookup (framework code → SPI ids) is a *derived, regenerable, read-only index* — never the source of truth.

**Reconciliation of the two stores.** The 30 existing inline `{framework, code, label?}` records remain valid and in place; the separate store is **additive**, and Phase 1 does **not** migrate, denormalize, or delete them — preserving the byte-stability of those 7 files. The inline hook may, in a clearly-separate future step, serve as an *optional read-cache* (a generated denormalization of `alignmentType: "exact", status: "approved"` records back onto an objective). Such denormalization is a generated output, would require its own separately-gated additive schema change and manifest re-freeze, and is **explicitly deferred** — Phase 1 performs none of it, keeping approved files byte-stable.

### 9.4 The alignment record schema (illustrative — not to implement now)

The record carries exactly the owner-mandated fields. Proposed as a new schema `schemas/standard-alignment.schema.json`. The single SPI-anchor key is **`linkedSpiObjectiveIds`** (named to encode the directionality principle; this is the one canonical field name used platform-wide — §11, §14, §15 use it verbatim):

```jsonc
// ILLUSTRATIVE DESIGN — not to implement now. Proposed schemas/standard-alignment.schema.json
{
  "standardSet":      "IGCSE-0580",            // framework/syllabus family
  "standardVersion":  "2025",                  // edition/year of that framework
  "standardId":       "0580/C1.11",            // the external code within the set
  "statement":        "Demonstrate an understanding of ratio and proportion.", // full statement (reference only)
  "label":            "Ratio & proportion",    // short human label
  "framework":        "IGCSE-0580",            // RETAINED legacy key (mirrors standardSet) for inline-cache compatibility
  "code":             "0580/C1.11",            // RETAINED legacy key (mirrors standardId) for inline-cache compatibility
  "linkedSpiObjectiveIds": [                    // SPI is the anchor; one external standard may map to several SPI objectives
    "SPI.MIDDLE.RATIO.SIMPLIFY.01",
    "SPI.MIDDLE.RATIO.DIRECT_PROPORTION.01"
  ],
  "alignmentType":    "partial",               // exact | partial | prerequisite | extension | enrichment
  "status":           "proposed",              // proposed | reviewed | approved  (the single confidence/status axis)
  "notes":            "0580 statement is broader than either SPI micro-skill; mapped as partial.",
  "source":           { "by": "curriculum-team", "ref": "IGCSE 0580 syllabus 2023–2025, C1.11", "method": "manual" },
  "date":     "2026-06-27",                     // record date
  "version":  "1.0.0"                           // semantic version of THIS alignment record
}
```

Field-by-field, mapped to the owner's required set:

| Owner-required field | Schema key | Notes |
|---|---|---|
| standardSet | `standardSet` | The framework/syllabus family. `standardSet` is an **open** controlled vocabulary in Phase 1 (§9.6). |
| standardVersion | `standardVersion` | Edition/year. Required — a code is meaningless without its edition. |
| standardId | `standardId` | External code as printed by the framework. Opaque string; never parsed for meaning. |
| statement / label | `statement`, `label` | `statement` = verbatim wording (reference only, no reuse implied); `label` = short UI tag. |
| linked SPI objective IDs | `linkedSpiObjectiveIds[]` | **The anchor.** Must reference IDs present in the objective graph (validated, §9.7, §11). |
| alignmentType | `alignmentType` | Enum `exact \| partial \| prerequisite \| extension \| enrichment`. |
| confidence / status | `status` | **Single axis.** The owner's "confidence/status" is intentionally modelled as the one review-status enum `proposed \| reviewed \| approved` (see decision note below); separate from the objective's own `reviewStatus`. |
| notes | `notes` | Free text for reasoning, scope caveats. |
| source / provenance | `source { by, ref, method }` | Who/what asserted the mapping and how (`method: manual \| imported \| suggested`). |
| date / version | `date`, `version` | Record-level audit + semantic version of the alignment itself. |
| (compatibility) | `framework`, `code` | **Retained** legacy keys mirroring `standardSet`/`standardId`, so a future inline read-cache (§9.3) can be generated without a lossy transform. |

**Decision note — confidence vs. status (deliberate, not an omission).** The owner's "confidence/status" axis is modelled as the **single `status` enum** (`proposed → reviewed → approved`); there is **no separate `confidence` field**. Rationale: in this design confidence *is* expressed by how far a record has advanced through review (a `proposed` import is low-confidence; an `approved` record is high-confidence), so a parallel free-form `confidence` field would duplicate and could contradict `status`. All illustrative records in this document carry `status` only.

**`alignmentType` semantics** (so the five values are not interchangeable):

| Value | Meaning |
|---|---|
| `exact` | The external standard and the SPI objective(s) cover the same assessable skill at the same grain. |
| `partial` | Overlap, but one side is broader/narrower; `notes` records which. |
| `prerequisite` | The SPI objective is a prerequisite *for*, not a peer of, the external standard. |
| `extension` | The SPI objective goes beyond the external standard (harder/further). |
| `enrichment` | Related but off the main progression — synoptic/cultural/applied breadth. |

### 9.5 Pilot sample mapping (pilot-only — proves the design, not a deliverable)

To validate the schema end-to-end, Phase 1 authors **one or two pilot records only**, clearly marked pilot, against existing approved **ratio** objectives (chosen because `SPI.MIDDLE.RATIO.json` currently has **zero** inline alignments, so a ratio pilot is net-new for that family and touches none of the 30 frozen inline records). This is design proof, **not** the IGCSE/IB/Singapore/Lebanese mapping (out of scope).

```jsonc
// PILOT-ONLY — two sample records to prove the schema. NOT a mapping deliverable.
// Proposed file: curriculum/alignments/igcse-0580.sample.json  (sample, not authoritative)
[
  {
    "standardSet": "IGCSE-0580", "standardVersion": "2025", "standardId": "0580/C1.11",
    "framework": "IGCSE-0580", "code": "0580/C1.11", "label": "Ratio & proportion",
    "statement": "Use ratios and proportion in given situations (reference only).",
    "linkedSpiObjectiveIds": ["SPI.MIDDLE.RATIO.SIMPLIFY.01"],
    "alignmentType": "partial", "status": "proposed",
    "notes": "PILOT. 0580 statement broader than the SIMPLIFY micro-skill.",
    "source": { "by": "phase1-pilot", "ref": "IGCSE 0580 C1.11", "method": "manual" },
    "date": "2026-06-27", "version": "0.1.0"
  },
  {
    "standardSet": "IGCSE-0580", "standardVersion": "2025", "standardId": "0580/C1.13",
    "framework": "IGCSE-0580", "code": "0580/C1.13", "label": "Direct & inverse proportion",
    "statement": "Direct and inverse proportion (reference only).",
    "linkedSpiObjectiveIds": [
      "SPI.MIDDLE.RATIO.DIRECT_PROPORTION.01",
      "SPI.MIDDLE.RATIO.INVERSE_PROPORTION.01"
    ],
    "alignmentType": "exact", "status": "proposed",
    "notes": "PILOT. Two SPI objectives jointly cover the one external statement.",
    "source": { "by": "phase1-pilot", "ref": "IGCSE 0580 C1.13", "method": "manual" },
    "date": "2026-06-27", "version": "0.1.0"
  }
]
```

This pilot demonstrates the two structural cases the design must handle: one external standard → one SPI objective (`partial`), and one external standard → several SPI objectives (`exact`, joint coverage). `SPI.MIDDLE.RATIO.json` is **not edited** to produce this; the records live only in the separate sample file.

### 9.6 Supportable-frameworks vocabulary (some already present inline; none mapped at scale)

The design records the frameworks as a controlled, **open** `standardSet` vocabulary. The Phase-1 status distinguishes **frameworks already present inline today** (IGCSE 0580, Singapore Lower Secondary, IB AA SL — on the 30 objectives of §9.2) from frameworks **not yet mapped at all** (Lebanese, Common Core):

| `standardSet` (proposed token) | Framework | Inline today? | Phase-1 status |
|---|---|---|---|
| `IGCSE-0580` | Cambridge IGCSE Mathematics 0580 | **Yes (×21)** | already present inline; separate-store pilot sample added (ratio) |
| `SG-LOWER-SEC` | Singapore Lower Secondary Mathematics | **Yes (×14)** | already present inline; not extended in Phase 1 |
| `IB-DP-AA-SL` | IB Mathematics AA SL | **Yes (×9)** | already present inline; not extended in Phase 1 |
| `IB-MYP`, `IB-DP-AA-HL`, … | Other IB programmes | No | reserved, not mapped |
| `SG-MOE` | Singapore MOE (other levels) | No | reserved, not mapped |
| `LB-NCERD` | Lebanese official curriculum | **No** | reserved, **not yet mapped at all** |
| `CCSSM` | Common Core State Standards – Math | **No** | reserved, **not yet mapped at all** |

The Phase-1 *novelty* is not "introducing these frameworks" (three already exist inline) but **(a)** the separate-store schema, **(b)** the directionality + lifecycle model, and **(c)** a net-new ratio pilot. The token set is open (the schema does not hard-enum `standardSet`), so a new framework is added by introducing a token + a store file, with no engine change.

### 9.7 Lifecycle, governance, and validation rules

**Alignment lifecycle** (independent of the objective's own `reviewStatus`):

```
proposed ──review──▶ reviewed ──approve──▶ approved
   │                                         │
   └──────────────── retire/supersede ◀──────┘   (a framework re-version supersedes, never deletes)
```

Governance rules:

1. **An alignment never changes an objective.** Authoring, reviewing, or approving an alignment must not modify any `curriculum/objectives/*.json` file (including the 30 existing inline records) or any manifest sha256. (Enforced by keeping the store separate; checkable in CI by asserting the approved-objective sha256 set is unchanged.)
2. **Mapping is not mandatory.** **Not every objective needs an alignment** — many of the 70 will have none beyond their existing inline entry, and that is a valid, expected state, not a gap that blocks anything. Coverage of alignments is *reported* (§10.6), never *required*.
3. **Approved objective definitions are never altered to fit a framework.** If an external standard does not match, the record is `alignmentType: "partial"` (or omitted) — the SPI wording is not bent. The directionality principle restated as governance.
4. **Confidence rises by review, not by import.** `method: "imported"` / `"suggested"` records may only enter at `status: "proposed"`; promotion to `reviewed`/`approved` requires a human curriculum decision, logged like generator approvals (a `DECISION_LOG.md` entry).
5. **Versioned, not overwritten.** When a framework re-versions (e.g. IGCSE 0580 2025→2027), a new record at the new `standardVersion` is added and the old one is `superseded`, preserving history.

**Validation rules** (extend the existing graph-check pattern; illustrative API, not to implement now):

```ts
// ILLUSTRATIVE — proposed companion to checkCurriculumGraph(); not to implement now.
interface AlignmentReport { ok: boolean; errors: string[]; warnings: string[]; }

function checkAlignments(objectives: ObjectiveLike[], alignments: AlignmentRecord[]): AlignmentReport;
//  ERROR  — linkedSpiObjectiveIds references an id absent from the objective graph (dangling), or a retired one
//  ERROR  — missing required field (standardSet / standardVersion / standardId / linkedSpiObjectiveIds /
//           alignmentType / status)
//  ERROR  — alignmentType or status outside its enum
//  ERROR  — status:"approved" without a source.ref + a decision-log reference
//  WARN   — duplicate (standardSet, standardVersion, standardId) → same SPI id mapped twice
//  WARN   — a record whose objective definition was modifiedAt AFTER the alignment's date (re-review prompt)
```

These reuse the curriculum graph checker's established vocabulary (dangling refs, duplicates) so alignment integrity is enforced by the same kind of per-family test that already gates the objective graph (`*-graph.test.ts`).

---

## 10. Coverage and gap-analysis model

### 10.1 Purpose: the readiness map

After being the single query layer over objectives (§5), the registry's second job is to answer one operational question: **where is the platform strong, where is it thin, and what is the best next family to build?** This section defines a *report model* — a deterministic, derivable readiness map computed from artifacts that already exist. It introduces **no new authored content**; every signal is read from the objective files, the generator registry (`core/sdk/sequence-registry.ts`), the task→objective maps, the manifests (`docs/review/*_manifest.json`), and the alignment store (§9). The report is regenerable and output-neutral.

### 10.2 The join the report is built on

Coverage is a left-join from **every objective** (the 70) onto the **generator capability** of §8. The capability source is the registry entry's `derived` block: registry-side `id/version/tasks/approvalStatus`, the per-module `describe()` cross-check (§8.1), and the 1:1 `OBJECTIVE_BY_TASK` resolution.

```
objective (curriculum/objectives/*.json)
   ⟵ OBJECTIVE_BY_TASK (core/curriculum/*-objective-ids.ts) ⟵ task (registry/describe()) ⟵ generator → approvalStatus
   ⟶ alignments (curriculum/alignments/*, §9)
   ⟶ manifest (docs/review/*_manifest.json) → review-pack exemplars, sha256 identity
```

Because the join key on both sides is the SPI objective id, the readiness map inherits the directionality and stability of §9 — no objective is defined or renamed by the report.

### 10.3 Generator-coverage tiers (per objective)

Each *existing* objective is classified into exactly one generator-coverage tier — the **same vocabulary** as §5.3/§8.4:

| Tier | Synonym (§8.4 bucket) | Definition |
|---|---|---|
| **G2_approved** | `coveredApproved` | Some task maps to this objective in a generator whose effective `approvalStatus = "approved"` (returned by `approvedGenerators()`). |
| **G1_pendingOnly** | `coveredPending` | Mapped only by generator versions that are `pending-review` (in `generatorsForMode("review")` only). |
| **G0_noGenerator** | `definedUncovered` | No task in any registered generator resolves to this **existing** objective. |

Today, with all nine families approved, most generator-backed objectives are **G2_approved**; **G0_noGenerator** objectives are those defined ahead of any generator (e.g. the objective in `SPI.MIDDLE.NUM.json` and the two in `SPI.MIDDLE.ALG.FOUNDATIONS.json` that exist but are not themselves generated). **G0 is not a defect** — it is precisely the signal the readiness map surfaces.

**Distinction from §7 referenced-undefined (important).** The G-tiers classify objectives that **exist**. A *referenced-but-undefined* prerequisite (e.g. `SPI.MIDDLE.NUM.INTEGERS_NUMBER_LINE.01`, referenced by `SPI.MIDDLE.NUM.SIGNED_OPERATIONS.01` but defined in no file) is **NOT G0** — it has no record to classify. It belongs to §8.4's `referencedUndefined` bucket and is a §7 global **error**. The readiness map reports it under `referencedUndefined`, separate from the G0 objectives, so the two are never conflated.

### 10.4 Difficulty-band reachability

Each objective declares an intended `difficultyRange {min, max}` (1–5). The report flags **unreachable bands**: difficulty levels inside an objective's declared range that the approved generator is not known to produce.

```jsonc
// ILLUSTRATIVE report fragment — not to implement now.
{
  "objectiveId": "SPI.MIDDLE.RATIO.DIRECT_PROPORTION.01",
  "declaredDifficulty": { "min": 2, "max": 4 },
  "generatorReachableDifficulty": [2, 3],      // derived from the family's distribution artifact
  "unreachableBands": [4],                      // FLAG: declared but not observed
  "source": "docs/review/ratio_distribution.json"
}
```

The reachable set is derived from the family's existing distribution artifact (`docs/review/*_distribution.json`) — no new sweep is mandated. An empty `unreachableBands` is healthy; a non-empty one is a build-priority signal, not a correctness error.

### 10.5 Interaction-type and exemplar coverage

Two further per-objective signals, both read from artifacts that exist:

- **Missing interaction types.** Each objective's `answerTypes[]` and the family's interaction policy (`SUPPORTED_INTERACTIONS_BY_TASK`, `MC_ELIGIBLE_TASKS`, `MC_ONLY_TASKS` in the `*-objective-ids.ts` maps; mirrored in the manifest `mcPolicy`) declare which of `free-response` / `multiple-choice` an objective *can* be assessed in. These per-family interaction maps live alongside `OBJECTIVE_BY_TASK` in `core/curriculum/*-objective-ids.ts`; where a family does not yet expose a given map, the report records the signal as absent rather than failing (§8.3). The report flags an objective whose policy admits an interaction the approved generator does not yet emit. Example basis: ratio's `best_buy` is MC-only, several tasks MC-eligible, the rest free-response only.
- **No review-pack exemplars.** The manifests and review packs (`*_review_pack.json`) carry curated exemplars and the sha256 artifact identity for each approved family. An objective with no exemplar in any review pack is flagged `noExemplar`. Because the manifest pins each artifact's `sha256` and `present` flag, the report can additionally flag **identity drift** (a referenced artifact whose hash no longer matches) and **missing artifacts** (`present: false`) — reusing the integrity guarantee the manifests already provide.

### 10.6 Standards-mapping coverage (incomplete-mapping signal)

Using the alignment store (§9), the report classifies each objective's standards coverage. Per §9.7 rule 2, **absence of an alignment is not a defect** — it is reported as informational, never as a blocker. (The 30 existing inline `externalAlignments` entries also count toward `proposed`/de-facto mapped state for their objectives.)

| Mapping state | Meaning |
|---|---|
| `unmapped` | No alignment record (inline or store) links this objective. Expected for many objectives; informational only. |
| `proposed-only` | Linked alignments exist but none has reached `status: "approved"`. |
| `approved` | At least one `status: "approved"` alignment links this objective. |
| `conflicting` | Multiple `exact` alignments to *different* standard sets at incompatible grain — a curation review prompt, not an engine error. |

The report summarizes mapping coverage per domain/strand (e.g. "RATIO: 2/12 objectives have a proposed pilot alignment; 10 unmapped") purely to inform future work — it never forces a mapping to be authored.

### 10.7 Domain / strand whitespace

Rolling the per-objective tiers up to the 7 domains and 13 strands, the report surfaces **whitespace**: domains or strands with *no approved generator coverage at all*, and stages with thin coverage (61 MIDDLE vs. 9 IBDPAASL — a stage-level imbalance). This is the strand-level analogue of the per-objective G0 tier and the primary input to "what family next".

### 10.8 The consolidated readiness map (illustrative shape)

```jsonc
// ILLUSTRATIVE — the report the registry emits; not to implement now.
{
  "generatedAt": "2026-06-27",
  "objectiveTotal": 70,
  "byGeneratorTier": { "G2_approved": 0, "G1_pendingOnly": 0, "G0_noGenerator": 0 },  // counts filled at runtime
  "referencedUndefined": [],          // §7 errors (NOT a tier) — e.g. INTEGERS_NUMBER_LINE.01
  "perObjective": [
    {
      "objectiveId": "SPI.MIDDLE.RATIO.BEST_BUY.01",
      "generatorTier": "G2_approved",
      "generator": { "id": "gen.proportion.ratio", "version": "1.0.2", "task": "best_buy" },
      "declaredDifficulty": { "min": 3, "max": 4 }, "unreachableBands": [],
      "declaredInteractions": ["multiple-choice"], "missingInteractions": [],
      "hasReviewPackExemplar": true,
      "mappingState": "unmapped"          // informational, not a gap
    }
  ],
  "perStrand": [
    { "strand": "ratio-and-proportion", "objectives": 12, "g2": 12, "g0": 0, "approvedAlignments": 0 }
  ],
  "whitespace": {
    "domainsWithNoApprovedGenerator": [],     // filled at runtime
    "strandsWithNoApprovedGenerator": [],
    "stagesThin": ["ibdp-aasl (9 objectives)"]
  },
  "nextFamilyCandidates": []                  // ranked; see 10.9
}
```

### 10.9 From map to decision: choosing the next family

The readiness map feeds a simple, transparent priority ordering — a ranking input, not an auto-decision:

1. **Unblock referenced-undefined prerequisites first.** A `referencedUndefined` id (a §7 global error, §10.3) that many G2 objectives depend on ranks highest — authoring it strengthens existing families. (Authoring is **out of Phase-1 scope** — the map reports the gap; building the objective is a separately-gated decision.)
2. **Fill strand whitespace.** Strands with zero approved coverage, weighted by how many objectives they already contain.
3. **Complete partially-covered families.** Families with G1-only or unreachable-band objectives — cheaper than a new family.
4. **Balance stages.** Thin stages (e.g. IBDPAASL) when the roadmap calls for breadth.

Every input is derived from existing artifacts; the map is reproducible and reviewable, and — like the alignment layer — it changes no approved generator output, objective definition, fixture, or manifest. It is a read-only lens over the registry, consistent with the Phase-1 output-neutrality constraint.

---

## 11. Governance and integrity checks

This section specifies the **CI-style integrity gate** for the Objective Registry and the standards-alignment layer. It is, by design, an *extension* of two disciplines the platform already runs and trusts:

1. the **curriculum-graph check** — `core/curriculum/graph-check.ts` (`checkCurriculumGraph(objectives) -> GraphReport`; `requireObjectives(objectives, expected)`), exercised by the per-family graph tests; and
2. the **manifest / artifact-identity discipline** — `docs/review/*_manifest.json` (sha256 per artifact + `versionTags` + `approvalCommit`) enforced by `domains/geometry/artifact-integrity.test.ts` and `domains/geometry/coordinate-lines-integrity.test.ts`.

The proposal introduces no new validation philosophy. It promotes the existing per-family checks to a **single global registry gate** and adds a small number of new *rules* — never new infrastructure — covering ID grammar, lifecycle, approved-objective immutability, and the new alignment references. Every rule is a pure, offline, DOM-free predicate returning errors/warnings in the existing `GraphReport` shape, slotting into `node --test` exactly like today's family tests.

### 11.1 Design principle — one report shape, additive checks

All new checks **extend** the existing `GraphReport` contract:

```ts
// illustrative — not to implement now
export interface GraphReport {
  ok: boolean;
  objectiveCount: number;
  errors: string[];      // gate FAILS (CI red)
  warnings: string[];    // surfaced, non-blocking (e.g. cross-stage prerequisite)
}
```

The current `checkCurriculumGraph` already distinguishes hard errors (duplicate id, prerequisite cycle) from warnings (an unresolved prerequisite). The registry gate keeps that split and adds the §7.5 baseline buckets: the global gate's pass/fail follows the `GlobalGraphReport` (§7.4), where **`ok = errors.length === 0 && newReferencedUndefined.length === 0`** — the `knownBaselineReferencedUndefined` bucket is reported but never gates. Concretely, the **gate FAILS** when any of {duplicate IDs; prerequisite cycle; live→`retired` dependence; `newReferencedUndefined` non-empty; unresolved generator objective reference; unresolved review-pack objective reference; unresolved standards-alignment SPI reference; approved-objective immutability violation; approved-family fixture drift}; the **gate PASSES** when the only unresolved prerequisite references are exactly the recorded known-baseline set and no new one is introduced (owner correction A, §7.5 points 6–7). No check ever mutates an objective, artifact, or manifest — the gate is **read-only**, consistent with output-neutrality.

### 11.2 The integrity-check catalogue

| # | Check | What it asserts | Today | Phase 1 delta |
|---|---|---|---|---|
| G1 | **Objective ID grammar** | every `objectiveId` matches `SPI.<STAGE>.<DOMAIN>[.<SUBSEGMENT(S)>].<MICRO>.<NN>` (variable-depth; `NN` two digits) | partial (per-family string asserts) | **new global regex rule** (error) over all 70 ids |
| G2 | **Duplicate IDs** | no two objectives share an `objectiveId` | yes (`checkCurriculumGraph`) | run over the **global** set |
| G3 | **Invalid stage** | `stage ∈` schema enum | schema validation only | **new graph-level rule** (error) so a bad stage fails CI even if a file bypasses Ajv |
| G4 | **Invalid domain / strand** | `domain` ∈ closed vocab; `strand` **present-or-valid** (if present, ∈ registered set) | partial (per-family literal asserts) | **new global enum rule** (error) sourced from the §4 vocabulary |
| G5 | **Broken prerequisite links (baseline-aware, §7.5)** | every `prerequisites[]` entry resolves to a loaded objective, **or** is in the committed known-baseline set | yes (resolves→edge; else warning; cycle→error) | a referenced-undefined ID in the baseline → `knownBaselineReferencedUndefined` (**non-blocking, recorded**); one NOT in the baseline → `newReferencedUndefined` (**error**). This is correction A: the gate never blocks on the frozen baseline, only on regressions. |
| G6 | **Prerequisite cycles** | the resolved prerequisite graph is a DAG | yes (DFS three-colour) | unchanged |
| G7 | **Lifecycle violations** | `reviewStatus ∈` enum; transitions follow §6/§14.5; no `approved`-referenced objective sits below `approved` | schema enum only | **new rule** (error on illegal value/back-transition; warning on draft objective referenced by a pending-review generator) |
| G8 | **Approved-objective immutability** | the bytes of every objective file with `approved` objectives match the sha256 in its family manifest | yes for ratio (manifest records `SPI.MIDDLE.RATIO.json` sha256) | **generalise** the manifest sha256 check to *every* family (error on drift) |
| G9 | **Generator objective references resolve** | every `objectiveId` in each `describe().objectiveIds` and each `OBJECTIVE_BY_TASK` map exists and is `approved` | partial (per-family) | **new global rule** (error) over `approvedGenerators()` joined to per-module `describe()` |
| G10 | **Review-pack objective references resolve** | every `objectiveId` in each `*_review_pack.json` / `*_manifest.json` `objectiveIds[]` resolves and is `approved` | partial (manifest lists ids) | **new rule** (error) joining manifest ids to the registry |
| G11 | **Standards-mapping references resolve** | every `linkedSpiObjectiveIds[]` in an alignment record points to a real, non-`retired` SPI objective; `alignmentType`/`status` in-enum | none (alignment layer is new) | **new rule** (error on dangling SPI id; warning on `proposed` alignment) |
| G12 | **Manifest identity** | each manifest's versions equal the live versions, `gitCommit` is real, artifacts present, no stale strings | yes (`artifact-integrity.test.ts`) | unchanged; the gate simply *runs* it |
| G13 | **No approved generator output drift** | golden + parity fixtures and their manifest sha256 are unchanged; building the registry produces **zero** byte changes | yes (per-family parity + manifest sha256) | unchanged; declared a **hard precondition** (§13) |

### 11.3 ID-grammar rule (G1) — illustrative

The grammar is *variable-depth*, so the rule validates structure, not a fixed segment count. Real ids it must accept: `SPI.MIDDLE.RATIO.SIMPLIFY.01`, `SPI.IBDPAASL.SEQSER.ARITH.NTH_TERM.01`, `SPI.MIDDLE.GEO.COORD.CARTESIAN_PLANE.01`, `SPI.MIDDLE.MEAS.PERIM.RECTANGLE.01`, `SPI.MIDDLE.ALG.LINEQ.ONESTEP_ADD.01`.

```ts
// illustrative — not to implement now
const STAGE  = "(MIDDLE|IBDPAASL|...)";              // sourced from the registry stage vocabulary (§4)
const DOMAIN = "(SEQSER|ALG|GEO|MEAS|NUM|RATIO|STAT)";
const SEG    = "[A-Z][A-Z0-9_]*";                    // one micro/subsegment token
const ID = new RegExp(`^SPI\\.${STAGE}\\.${DOMAIN}(\\.${SEG})+\\.\\d{2}$`);
// error if !ID.test(o.objectiveId)
// note: trailing \d{2} is the <NN>; (\.${SEG})+ is the >=1 micro/subsegment chain
```

The stage and domain alternations are **not hardcoded in the regex** — they are pulled from the registry's single vocabulary source (§4), so adding a stage is a one-line vocabulary change, never a check rewrite. This mirrors how `sequence-registry.ts` makes "add a family" a single-entry change.

### 11.4 Approved-objective immutability (G8) — hash/byte check

The platform already proves *generator artifacts* immutable via manifest sha256 (`artifact-integrity.test.ts`, `createHash("sha256").update(readFileSync(...))`). G8 extends the **identical mechanism** to objective definitions: the ratio manifest already records

```json
// docs/review/proportion_ratio_manifest.json (real excerpt, shape)
"objectives":   { "path": "curriculum/objectives/SPI.MIDDLE.RATIO.json", "sha256": "d3513…", "present": true },
"objectiveIds": { "path": "core/curriculum/ratio-objective-ids.ts",      "sha256": "aa16e…", "present": true }
```

G8 asserts, for **every** family with approved objectives, that the on-disk file digest equals the manifest's recorded digest — **including the 7 files carrying the 30 inline alignment records**, which therefore cannot be silently edited. Any edit to an approved objective's bytes — even whitespace — fails CI until either (a) reverted, or (b) a **revision** runs through the governed lifecycle (§6, §14), re-freezing the manifest at a new `approvalCommit`/`versionTags`. This is the mechanical enforcement that "no approved objective definition is rewritten."

### 11.5 Standards-mapping reference resolution (G11)

The alignment layer maps **SPI `objectiveId` → external standard**, never the reverse. G11 is a one-directional resolve: each record's `linkedSpiObjectiveIds[]` (the single canonical key, §9.4) must hit a real SPI objective; the external `standardSet`/`standardVersion`/`standardId` are treated as *opaque references* and are **not** required to resolve against any internal source (the platform owns no external framework data in Phase 1). The rule:

- **error** — a `linkedSpiObjectiveIds[]` entry matching no registry objective, or matching a `retired` one;
- **error** — `alignmentType ∉ {exact, partial, prerequisite, extension, enrichment}` or `status ∉ {proposed, reviewed, approved}`;
- **warning** — an alignment in `proposed` status (surfaced for review), or a `standardVersion` not yet seen.

Because the relation is SPI → external, a dangling *external* code can never break an SPI objective or a generator; it is contained entirely within the alignment record — exactly the containment the owner requires.

### 11.6 Wiring into CI

The gate is one new aggregating test that loads the **whole** registry (all 11 files via the index, §12), runs G1–G13, and asserts `report.errors == []`. The existing per-family tests are retained verbatim as fast, local guardrails. The suite stays `node --test` over `core/curriculum/*.test.ts` plus the new `registry-graph.test.ts`; no new runner, no network, no DOM. The output-drift guarantee (G13) is *not* re-implemented — the registry test runs alongside the existing parity/integrity tests; if any go red, the registry work is blocked by definition.

---

## 12. Migration plan from current per-family files

The migration is deliberately **conservative**: the 11 per-family JSON files remain the **source of truth for objective definitions**. Phase 1 adds an *aggregating read layer* (a unified registry/index + a global graph check) **on top of** those files, and edits **none** of the 70 approved objective records (nor the 30 inline alignment entries within them). This is the "READ-OVER, not rewrite" path.

### 12.1 What exists today (the starting point)

| Asset | Role | Count / detail |
|---|---|---|
| `curriculum/objectives/SPI.*.json` (11 files) | **source of truth** for definitions | 70 objectives, all `approved`; 30 inline `externalAlignments` |
| `core/curriculum/*-objective-ids.ts` | per-family task→objective maps | `OBJECTIVE_BY_TASK`, `RATIO_TASKS`, `RATIO_OBJECTIVE_IDS`, interaction/answer-type maps |
| `core/curriculum/graph-check.ts` | DAG / duplicate / unresolved-ref engine | `checkCurriculumGraph`, `requireObjectives` |
| `core/curriculum/*-graph.test.ts` | per-family graph + metadata gates | load a *subset* of files, then check |
| `core/sdk/sequence-registry.ts` | generator registry + approval gating | `approvedGenerators()` |
| `domains/<area>/<family>.ts` | per-module `describe()` (capability) | `objectiveIds`, `answerTypes` |
| `docs/review/*_manifest.json` | artifact identity (sha256 + versionTags) | per family, incl. `artifacts.objectives` |

The existing per-family graph tests already *manually* spread several files together (e.g. `ratio-graph.test.ts` loads `SPI.MIDDLE.NUM.json` + `…ALG.FOUNDATIONS.json` + … + `SPI.MIDDLE.RATIO.json`). The migration generalises this ad-hoc spreading into **one canonical loader**.

### 12.2 The SAFE path — add an index, edit no definitions

```
Phase 1 migration, in one sentence:
  introduce ONE registry loader + ONE global graph check that read all 11 files,
  WITHOUT changing the bytes of any objective definition or any generator output.
```

The new layer has two pieces, both **read-only over the existing files**:

1. **A registry/index loader** that enumerates the 11 files, parses them, and exposes a single queryable collection — the curriculum analogue of how `sequence-registry.ts` is the single place that knows "which generators exist."
2. **A global graph check** that runs G1–G13 (§11) over the loaded set.

```ts
// illustrative — not to implement now
// core/curriculum/objective-registry.ts
export const OBJECTIVE_FILES = [
  "SPI.IBDPAASL.SEQSER.ARITH.json", "SPI.IBDPAASL.SEQSER.GEO.json",
  "SPI.MIDDLE.ALG.FOUNDATIONS.json", "SPI.MIDDLE.ALG.LINEQ.json",
  "SPI.MIDDLE.GEO.COORD.json", "SPI.MIDDLE.GEO.TRANS.json", "SPI.MIDDLE.GEO.json",
  "SPI.MIDDLE.MEAS.json", "SPI.MIDDLE.NUM.json", "SPI.MIDDLE.RATIO.json",
  "SPI.MIDDLE.STAT.json",
] as const;                                  // the ONLY hand-maintained list

export function loadObjectives(): ObjectiveRecord[] { /* read+parse all files, no mutation */ }
export function objectiveById(id: string): ObjectiveRecord | undefined { /* index lookup */ }
```

The loader returns objects **structurally identical** to the file contents — it does not normalise field order, re-serialize, or rewrite anything. It is a parse-and-concatenate, exactly what the per-family tests already do inline.

### 12.3 Normalization is gated, not assumed

The current files are already consistent enough to query (every record carries `objectiveId`, `stage`, `domain`, `reviewStatus`, `version`; `strand` present on all 70 though schema-optional). **No normalization is required for Phase 1**, and the plan performs none by default. If a future normalization need is ever identified, it is a separate, owner-gated change governed by three conditions, all of which must hold:

1. **Output-neutral** — proven by G13 (golden/parity sha256 unchanged) and the manifest objective-sha256 re-freeze running green.
2. **Owner-approved** — recorded in `DECISION_LOG.md` with a decision number, exactly like every prior family approval.
3. **Lifecycle-correct** — any touched objective transitions through `revised` and back to `approved`, never silently edited in place; the manifest re-frozen at the new commit.

Absent all three, the migration touches **zero** objective bytes — the hard guarantee the owner asked for.

### 12.4 Phased rollout

Each step is independently verifiable and reversible, and the gate is *additive* — at every step the existing per-family tests keep passing untouched.

| Phase | Action | Verification | Reversible? |
|---|---|---|---|
| **M0 — baseline** | record the sha256 of all 11 objective files + all golden/parity fixtures as the immutable baseline | all existing per-family graph + parity + integrity tests green | n/a (read-only snapshot) |
| **M1 — loader** | add the read-only `objective-registry.ts` loader; change **no** file | unit test: loader returns 70 objectives; bytes unmodified | yes |
| **M2 — global graph check** | add `registry-graph.test.ts` running G1–G13 | global `checkCurriculumGraph(...).errors == []`; G8 objective-sha256 matches manifests | yes |
| **M3 — generator/review-pack joins** | wire G9/G10 to per-module `describe().objectiveIds` + manifest `objectiveIds[]` | every generator + review-pack id resolves to an `approved` objective | yes |
| **M4 — alignment hook** | enable G11 over the (initially empty / tiny-pilot) alignment store | dangling-SPI-id error path proven by a negative fixture | yes |
| **M5 — supersede inline spreads** | optionally have per-family tests *call the shared loader* instead of re-listing files inline | per-family tests still green, now sourcing the canonical list | yes |

M5 is optional and cosmetic; even if skipped, the per-family tests and the global gate coexist. Nothing in M0–M5 changes an objective definition or a generator byte, so each phase lands as its own commit (mirroring the project's `(n/n)` cadence) and reverts in isolation.

### 12.5 What the migration explicitly does *not* do

- It does **not** merge the 11 files into one mega-file. The per-family files stay; the index is a *view*, not a replacement store.
- It does **not** migrate, denormalize, or delete the 30 existing inline `externalAlignments` records — they remain valid and in place; the new store (§9) is additive, preserving output-neutrality of those 7 files.
- It does **not** author new objectives, rewrite wording, or change `reviewStatus` values.
- It does **not** touch `sequence-registry.ts` generator entries or any `generate/validate/serialize` function.
- It does **not** introduce a database, service, or runtime dependency — the registry is a compile-time/test-time read of local JSON, exactly like today.

---

## 13. Backward-compatibility and output-neutrality plan

Phase 1 is **output-neutral by mandate**: not one byte of any approved generator item, fixture, golden vector, review pack, production sample, or objective definition may change because the registry/standards architecture is being *designed*. This section proves *how* that holds — as a set of pre-existing mechanical guardrails the registry work must leave green.

### 13.1 The core claim — the registry is READ-OVER, not a rewrite

The registry/index and the alignment layer are **pure readers** of two things that already exist and are frozen:

- the **objective definition files** (`curriculum/objectives/*.json`, including the 30 inline alignment records), and
- the **generator outputs** (`oracle/golden/<family>.golden.json`, `*.parity.json`, the review packs, the production samples).

Nothing in the registry *produces* a generator item, *serializes* an objective, or *re-emits* an artifact. The data path that creates approved bytes — the Python oracle authority + its byte-for-byte TypeScript mirror, gated by golden/parity fixtures — is **not on the registry's call graph at all**. The registry therefore *cannot* change those bytes; the most it can do is fail CI by *reporting* an inconsistency.

### 13.2 The guardrails that prove neutrality (already in the repo)

Output-neutrality is enforced by tests that already exist and pass. The registry work inherits them as **acceptance criteria**: if any go red, the registry change is rejected.

| Guardrail | Mechanism | What it locks |
|---|---|---|
| **Golden fixtures** | `oracle/golden/<family>.golden.json` | the exact serialized bytes of canonical generated items |
| **Parity fixtures** | `oracle/golden/<family>.parity.json` + `*.parity.test.ts` | Python-oracle ↔ TypeScript-mirror byte identity |
| **Manifest sha256 / identity** | `docs/review/*_manifest.json` + `artifact-integrity.test.ts`, `coordinate-lines-integrity.test.ts` | review packs, golden + parity fixtures, **objective files (incl. inline alignments)**, theme files — frozen to recorded digests at a real `gitCommit` |
| **Per-family graph tests** | `core/curriculum/*-graph.test.ts` | the objective DAG, exact id set, per-task answer types, `reviewStatus: "approved"` |
| **Compiled-validator hash** | `core/schema/compiled/question-item.validator.mjs` sha256 in the manifest | the schema-validation code path itself |

The registry never writes any of these paths, so all recorded digests remain valid by construction.

### 13.3 Proving each protected asset stays unchanged

| Protected asset | Why the registry leaves it byte-identical | Proof |
|---|---|---|
| **Approved generator item bytes** | the registry never calls `generate`/`serialize`; it only *reads* fixtures | golden + parity tests green |
| **Golden vectors** | not written by any registry path | manifest `golden` sha256 unchanged |
| **Parity fixtures** | Py↔TS mirror untouched | `*.parity.test.ts` + manifest `parity` sha256 |
| **Review packs** | the registry *references* their `objectiveIds[]` (read), never regenerates | manifest `reviewPackJson`/`reviewPackMd` sha256 |
| **Production samples / exports** | exporters consume `approvedGenerators()` output, unchanged; the registry adds no generator and changes no `approvalStatus` | `exporters.test.ts` + unchanged registry entries |
| **Objective definitions (incl. 30 inline alignments)** | edited by nobody in Phase 1; the index is a read-only view; the rich alignment record lives in a **separate** store | G8 objective-sha256 == manifest digest |
| **Objective schema / compiled validator** | **no property is added to `curriculum-objective.schema.json`** | compiled-validator sha256 unchanged |

The last two rows are load-bearing and resolve a potential contradiction precisely:

> **The existing inline `externalAlignments` item (`{framework, code, label?}`, `additionalProperties: false`, `required: [framework, code]`) and the `reviewStatus` enum are UNCHANGED in Phase 1.** The owner-mandated rich alignment fields (`standardSet`, `standardVersion`, `standardId`, `alignmentType`, `status`, `notes`, `source`, `date`, `version`, `linkedSpiObjectiveIds`) are modelled in a **new standalone schema** `schemas/standard-alignment.schema.json` and a **separate store** (`curriculum/alignments/*`, §9.3–§9.4) — **not** embedded in an `externalAlignments` item. Because no property is added to the objective schema, `curriculum-objective.schema.json` and its compiled validator stay **byte-frozen**.

Any *future* inline denormalization (already deferred in §9.3) — folding an `exact`/`approved` alignment back onto an objective as a read-cache — would itself require a **separately-gated additive schema change** to widen the inline item, with its own manifest re-freeze, handled the same way the platform added the `quantity`, `transformation`, and `ratio` answer contracts: additive, canonical-first, existing items byte-for-byte unchanged. Phase 1 does none of this.

### 13.4 The neutrality test contract

The single mechanical statement of output-neutrality for the whole effort:

```
For every approved family F:
  sha256(oracle/golden/F.golden.json)    == manifest[F].artifacts.golden.sha256
  sha256(oracle/golden/F.parity.json)    == manifest[F].artifacts.parity.sha256
  sha256(curriculum/objectives/<F>.json) == manifest[F].artifacts.objectives.sha256
  sha256(curriculum-objective.schema.json) and the compiled validator        UNCHANGED
  AND every per-family *-graph.test.ts and *.parity.test.ts is green
  BEFORE and AFTER the registry/index/alignment change.
```

If the *before* and *after* digest sets are identical (they must be — the registry writes none of these files), output-neutrality is proven. This is the same equality `artifact-integrity.test.ts` already checks; the registry effort commits to never invalidating it.

### 13.5 Compatibility for downstream consumers

Existing consumers of the per-family maps (e.g. `OBJECTIVE_BY_TASK` in `ratio-objective-ids.ts`, the per-module `describe().objectiveIds`) continue to import the **same** modules and see the **same** values — the index is additive and sits *beside* them. No call site is forced to migrate; M5 (§12.4) re-pointing per-family tests at the shared loader is optional. The change is backward-compatible at the API level (no signature changes, no removed exports) and the byte level (no artifact rewrites) simultaneously.

### 13.6 Failure mode and rollback

If a global check (§11) surfaces a real inconsistency — a generator referencing an absent objective id, or an objective file's bytes drifting from its manifest digest — the **correct** outcome is a **red CI gate**, not a silent fix. The registry never auto-repairs. Resolution is reverting the offending change or running the proper governed lifecycle revision (re-freezing the manifest). Because each phase (M1–M5) lands as an isolated, reversible commit and changes no protected asset, rollback is a single `git revert` with zero risk to approved outputs.

---

## 14. Review and approval workflow

This section defines how the curriculum authority (the project owner) reviews and decides on **registry-layer** changes: new or amended objectives, lifecycle transitions, registry/index regenerations, and external-standard alignments. It does **not** invent a new governance regime — it extends the discipline already proven across the project's approved decisions in `docs/DECISION_LOG.md`: **propose → review pack → owner decision (APPROVE / REVISE / REJECT) → immutable-on-approval → manifest + DECISION_LOG + `APPROVED_VERSIONS.md`**. The novelty in Phase 1 is only the *artifact under review* (objective definitions, the unified registry/index, and alignment records) — the decision machinery is unchanged. This is a proposal; no workflow tooling is built until the owner approves §15.

### 14.1 What is governed, and by whom

The curriculum authority is the sole approver of every item below. Machine gates (graph check, schema validation, integrity hashes) are **necessary but never sufficient**: a green CI run produces a *reviewable* pack, not an approval.

| Governed change | Examples | Decision authority | Machine pre-gate |
|---|---|---|---|
| New objective definition | adding a `SPI.<STAGE>.<DOMAIN>…<MICRO>.NN` record | owner | schema + graph check |
| Objective wording / metadata amendment | tightening `objectiveWording`, `successCriteria`, `prerequisites` | owner | schema + graph check |
| Lifecycle transition | `proposed → approved-for-implementation`; `approved → revised → approved` | owner | transition-legality test |
| Registry / index regeneration | rebuilding the unified read-only index | owner (sign-off on the report) | integrity hash + drift gate |
| External-standard alignment record | attaching a `linkedSpiObjectiveIds[]` alignment to an SPI objective | owner | alignment-schema + linkage check |
| Alignment lifecycle transition | `proposed → reviewed → approved` for a single alignment | owner | transition-legality test |

The **load-bearing invariant** is enforced at this layer: alignments map **TO** SPI objectives. A review pack may never present an external standard as the thing being approved; it presents an **SPI objectiveId** and the alignment(s) proposed *for* it (linked via `linkedSpiObjectiveIds`). The reviewable unit is always the SPI objective.

### 14.2 The review pack (registry edition)

Every governed change ships a self-contained **review pack**, mirroring `docs/review/*_review_pack.{md,json}` and gated by a `*_manifest.json` exactly as the nine generator families are (`gitCommit`, `versionTags`, `approval{decision,approvedTag,approvalDate,decisionLogRef}`, per-artifact `sha256` map). For a registry change the pack contains:

- **The diff under review** — added/changed objective records or proposed alignment records, as JSON and prose. Approved generator bytes are **never** in this diff (output-neutrality, §13).
- **The graph report** — `checkCurriculumGraph(objectives)` output: `objectiveCount`, zero `errors`, and any `warnings` explicitly acknowledged.
- **The coverage report** (§10) — covered/uncovered objectives and alignments per framework.
- **The integrity result** — a sha256 manifest proving the pack's artifacts match the named commit, with the explicit assertion **"all nine approved families byte-for-byte UNCHANGED."**
- **A decision block** — `decision`, `approvedTag`, `approvalDate`, `decisionLogRef`, initialized empty; the owner fills it on APPROVE.

> **Illustrative — not to implement now.** Registry-change manifest skeleton (extends the existing generator-manifest shape):
> ```json
> {
>   "changeKind": "objective-amendment | alignment | lifecycle | index-regen",
>   "gitCommit": "…",
>   "objectivesTouched": ["SPI.MIDDLE.RATIO.SIMPLIFY.01"],
>   "graphReport": { "ok": true, "objectiveCount": 70, "errors": [], "warnings": [] },
>   "outputNeutral": { "approvedFamiliesUnchanged": true, "fixtureDrift": 0 },
>   "approval": { "decision": null, "approvedTag": null, "approvalDate": null, "decisionLogRef": null },
>   "artifacts": { "objectivesFile": { "path": "curriculum/objectives/SPI.MIDDLE.RATIO.json", "sha256": "…" } }
> }
> ```

### 14.3 The three decisions

The owner returns exactly one of three decisions per pack, identical in meaning to the generator workflow:

| Decision | Meaning | Consequence |
|---|---|---|
| **APPROVE** | Curriculum-correct and complete. | Touched records advance to their target lifecycle state; an `approvedTag` is cut; a DECISION_LOG row + `APPROVED_VERSIONS.md` row are written; records become **immutable at that version**. |
| **REVISE** | Accept in principle; specific named corrections required. | Apply only the named corrections; **bump the objective/alignment `version`** if any reviewable byte changes; re-pack; resubmit. Prior version preserved at its tag. Scope is not reopened. |
| **REJECT** | Must not be used. | Proposed records do **not** advance; nothing is deleted (preserved at a `*-rejected` tag, as geometry v1.2.1 was); next step awaits owner direction. |

REVISE is the common path and is **narrowly scoped** by the owner's named corrections. A REVISE that changes reviewable bytes forces a version bump and preservation of the prior version at its tag, never an in-place mutation.

### 14.4 Immutable-on-approval discipline

Once APPROVED at a version, an objective record, alignment record, or registry snapshot is **frozen**. This mirrors the generator rule "v1.0.0 is immutable; output changes require a new version" and is why objectives carry a `version` field and a `revised` state:

- A correction to an approved objective is a **new objective version** (`approved → revised → approved`), not an edit-in-place. The prior version is preserved at its tag and recorded as superseded in `APPROVED_VERSIONS.md`.
- The sha256 manifest is the enforcement mechanism: an integrity test recomputes each approved objective file's hash and asserts **zero drift** against the frozen manifest.
- The **internal SPI objectiveId is the stable single source of truth** and is *never* renamed by an approval, revision, or alignment. External standard codes change framework-side; the SPI ID does not move.

### 14.5 Lifecycle transition legality

Objective definitions already carry the full lifecycle enum: `draft → proposed → curriculum-reviewed → approved` / `approved-for-implementation → published → revised → retired`. Phase 1 **formalizes which transitions are legal**; it adds no states. A transition-legality table (validated by a test, §15) rejects e.g. `retired → approved` and `draft → published`, while permitting `approved → revised → approved` and `approved-for-implementation → approved`.

| From | Permitted next | Owner-gated? |
|---|---|---|
| `draft` | `proposed` | no (authoring) |
| `proposed` | `curriculum-reviewed`, `approved`, `approved-for-implementation` | **yes** |
| `curriculum-reviewed` | `approved`, `approved-for-implementation`, `revised` | **yes** |
| `approved` / `approved-for-implementation` | `revised`, `published`, `retired` | **yes** |
| `revised` | `approved`, `approved-for-implementation` | **yes** |
| `published` | `revised`, `retired` | **yes** |
| `retired` | (terminal) | — |

The two-phase semantics in the schema are honored: `approved-for-implementation` means the **definition** is curriculum-approved and cleared for a generator build while the **generator** remains `pending-review` and gated from production. Note (consistent with §6.1) that **`approved` is itself a production-visible curriculum tier** — `published` is an optional later promotion, not a prerequisite for production. Approving a definition never auto-approves the generator that consumes it.

### 14.6 Alignment review and provenance

External-standard alignments are reviewed as **attachments to an already-approved SPI objective**, never as standalone artifacts. Each alignment record carries its own status (`proposed → reviewed → approved`) and its own provenance, so an unreviewed alignment can coexist with an approved objective without contaminating it. The owner reviews:

- **Direction** — the record links `standardId → SPI objectiveId` via `linkedSpiObjectiveIds`; rejected if it tries to make the SPI objective subordinate.
- **`alignmentType`** correctness — `exact` / `partial` / `prerequisite` / `extension` / `enrichment` is a curriculum judgement.
- **Provenance** — `source`, `standardVersion`, `date` present and credible; an alignment with no provenance cannot reach `approved`.
- **Rights neutrality** — consistent with the schema note "Reference only; never implies reuse rights," an alignment records a *correspondence*, not a license to reproduce external material.

### 14.7 Recording the decision

Every APPROVE / REVISE / REJECT is recorded in the same three places used today, so the registry's history is auditable end-to-end:

1. **`docs/DECISION_LOG.md`** — a new ADR row at **the next available DECISION_LOG index** (the log already runs well past the early family approvals), with date, decision, rationale, and `Accepted (owner)` status, cross-referencing the pack and tag.
2. **`docs/APPROVED_VERSIONS.md`** — the approved objective/alignment version, its tag, and reference commit; superseded versions marked "preserved (superseded; never approved)".
3. **`docs/CURRENT_STATE.md`** — the running snapshot updated to reflect the new approved counts.

No registry change is "silently changed" — superseded rows are marked and a new row added, exactly as the DECISION_LOG header mandates.

---

## 15. Phase 1 implementation plan (after approval)

This is the **ordered, output-neutral build plan** the team executes *only after the owner approves this architecture document*. No code is written now. Every step is sequenced so an earlier step's guardrail protects the next, and every step carries the same non-negotiable guardrail: **no approved generator item bytes, fixtures, golden vectors, review packs, production samples, or objective definition bytes change** because the registry is being built. The eleven per-family objective files remain the **source of record**; the registry is a *derived read layer*.

### 15.0 Standing guardrails (apply to every step)

- **Output-neutral.** After each step, the full battery must re-confirm "all nine approved families byte-for-byte UNCHANGED" and "fixture drift 0." Any drift fails the step.
- **Source-of-truth preserved.** The 11 objective files (incl. their 30 inline alignment records) are not rewritten. The registry **loads/indexes** them.
- **Additive schema only — and not to the objective schema.** `schemas/curriculum-objective.schema.json` stays byte-frozen; any new schema is the **separate** `schemas/standard-alignment.schema.json`, which re-validates nothing in the objective files.
- **Oracle-parity untouched.** No step touches `oracle/`, `domains/` generator code, golden/parity fixtures, or `sequence-registry.ts` entries except read-only consumption of `describe()`/`OBJECTIVE_BY_TASK`.

### 15.1 Step 1 — Unified registry loader + index (read-only)

Build a loader that reads all eleven `curriculum/objectives/*.json` files into one in-memory **Objective Registry**, keyed by `objectiveId`, exposing query methods (by stage, domain, strand, micro-skill, lifecycle state, generator/task). It is a *projection*, not a new store.
- **Deliverable:** a single query layer (`core/curriculum/objective-registry.ts`, illustrative) returning typed `ObjectiveLike` records; plus a generated index artifact for the review pack.
- **Guardrail:** **pure read** — a test asserts the round-trip `load → serialize` is byte-identical to the source files (no reformatting drift).

### 15.2 Step 2 — Global curriculum graph check

Promote the per-family graph tests to a **single whole-registry check** running `checkCurriculumGraph(allObjectives)` across all 70 objectives at once.
- **Deliverable:** a global graph test asserting `ok: true`, `objectiveCount: 70`, zero duplicate IDs, zero cycles, **`newReferencedUndefined: []`**, and the `knownBaselineReferencedUndefined` set equal to the committed baseline file (§7.5). Step 2 also **writes the committed baseline** (`curriculum/registry/known-baseline-referenced-undefined.json`) + the **registry gap report** (`docs/review/objective_registry_gap_report.json`) enumerating the eight buckets (§7.4). Per correction A the exit criterion is **"zero NEW referenced-undefined IDs; the known-baseline referenced-undefined set is recorded, stable, and separately reported"** — NOT "zero referencedUndefined".
- **Guardrail:** the global check **subsumes but does not delete** the per-family checks; its `ok` (errors empty AND `newReferencedUndefined` empty, §11.1) must be true *before any other Phase 1 step proceeds* — the integrity baseline. The baseline file is authored ONCE from the current approved data; thereafter it is frozen (it shrinks only when a future, separately-gated authoring phase defines a missing objective, §16).

### 15.3 Step 3 — Lifecycle + governance tests

Encode §14.5's transition-legality table and §14.1's authority rules as executable tests over the registry.
- **Deliverable:** a lifecycle-legality test (rejects illegal transitions like `retired → approved`), an `approved-for-implementation` two-phase test (definition-approved must not imply generator-approved), and a governance test asserting every `approved` objective has a DECISION_LOG/`APPROVED_VERSIONS.md` reference.
- **Guardrail:** tests are **assertions over existing data**, not migrations — all 70 current objectives (all `approved`) must pass unchanged; no `reviewStatus` is rewritten.

### 15.4 Step 4 — Alignment schema (separate) + tiny pilot

Formalize the alignment **model** in the **new standalone** `schemas/standard-alignment.schema.json` and a **separate store** (`curriculum/alignments/*`) — **schema only**, plus a *tiny* pilot. The existing inline `externalAlignments` item is **left UNCHANGED** (it cannot carry these fields, being `additionalProperties: false`); the rich record lives in the new store, never embedded in an objective record.

> **Illustrative — not to implement now.** Standalone alignment record (in the separate store; uses the single canonical key `linkedSpiObjectiveIds`; retains `framework`/`code` only as inline-cache-compatible mirrors of `standardSet`/`standardId`):
> ```json
> {
>   "standardSet": "IGCSE-0580",
>   "standardVersion": "2025",
>   "standardId": "0580/C8.1",
>   "framework": "IGCSE-0580",
>   "code": "0580/C8.1",
>   "label": "Understand and use ratio and proportion",
>   "statement": "Use ratio and proportion (reference only).",
>   "linkedSpiObjectiveIds": ["SPI.MIDDLE.RATIO.SIMPLIFY.01"],
>   "alignmentType": "exact",
>   "status": "proposed",
>   "notes": "Direction is standardId -> SPI objective; SPI ID is authoritative.",
>   "source": { "by": "phase1-pilot", "ref": "IGCSE 0580 syllabus 2025", "method": "manual" },
>   "date": "2026-06-27",
>   "version": "1.0.0"
> }
> ```
> *(Note: confidence is modelled by `status` alone, per §9.4 — there is no separate `confidence` field.)*

- **Deliverable:** the standalone alignment schema, an alignment-direction validator (G11: link must point *to* an existing SPI `objectiveId`), an alignment-lifecycle test (`proposed → reviewed → approved`), and **one or two sample alignments** on already-approved **ratio** objectives (which currently have zero inline alignments) attached at `status: "proposed"` to prove the record carries every required field.
- **Guardrail:** the pilot is **proof-of-design only** — no framework mapped at scale; samples enter at `proposed`; **zero** generator output changes; the existing 70 objectives and their 30 inline alignment records validate unchanged, and `curriculum-objective.schema.json` and the compiled validator stay byte-frozen.

### 15.5 Step 5 — Coverage report

Generate a **coverage report** joining the registry to generator capability via the registry-side `id/version/tasks/approvalStatus`, the per-module `describe()` (`objectiveIds`, `answerTypes`) cross-check, and the per-family `OBJECTIVE_BY_TASK` maps.
- **Deliverable:** a report classifying each objective into the single coverage vocabulary (`G2_approved`/`G1_pendingOnly`/`G0_noGenerator`), listing `referencedUndefined` ids separately, and summarizing alignment coverage per framework.
- **Guardrail:** read-only join over `approvedGenerators()` and the objective files; it **reports** gaps, it never authors objectives to "fill" them (out of scope, §16).

### 15.6 Step 6 — Integrity gates

Extend the sha256 manifest discipline to the registry artifacts: the unified index, the alignment file(s), and the coverage report.
- **Deliverable:** a registry manifest with per-artifact `sha256` and a drift test asserting zero drift, plus the explicit cross-check **"all nine approved families byte-for-byte UNCHANGED"** and "fixture drift 0" run in the same battery that already produces those assertions.
- **Guardrail:** the integrity gate is the **immutable-on-approval enforcer** (§14.4); it must be green before any registry artifact is offered for owner review.

### 15.7 Step 7 — Documentation

Produce the registry's authoritative docs and wire them into the existing trio.
- **Deliverable:** the finalized registry/alignment architecture doc (this document, post-approval), updates to `docs/DECISION_LOG.md` (next available index), `docs/APPROVED_VERSIONS.md` (registry version + tag), and `docs/CURRENT_STATE.md` (snapshot: 70 objectives, registry index version, pilot alignment count).
- **Guardrail:** docs are **metadata only** — like `APPROVED_VERSIONS.md` they "never mutate generator output or the committed golden/parity fixtures."

### 15.8 Sequencing and exit criteria

| Step | Output | Hard gate before proceeding |
|---|---|---|
| 1 Loader + index | read-only registry | round-trip byte-identical to source files |
| 2 Global graph check | whole-registry report | `ok:true`, 70 objectives, 0 errors (referenced-undefined triaged) |
| 3 Lifecycle/governance tests | legality assertions | all 70 approved objectives pass unchanged |
| 4 Alignment schema + pilot | separate schema + 1–2 samples | objective schema byte-frozen; 70 objectives + 30 inline records validate unchanged; samples `proposed` |
| 5 Coverage report | objective↔generator↔alignment join | read-only; no new objectives authored |
| 6 Integrity gates | registry manifest + drift test | 9 families unchanged; drift 0 |
| 7 Docs | finalized doc + log/registry rows | metadata only; no fixture change |

**Phase 1 exit criterion:** the registry loads all 70 objectives, the global graph is green, lifecycle/governance/alignment tests pass, the coverage report and registry manifest are produced, the alignment design is proven by a tiny pilot — and the nine approved generator families, their fixtures, production samples, the 30 inline alignment records, and `curriculum-objective.schema.json` are **byte-for-byte identical** to their pre-Phase-1 state. Then the owner runs the §14 review for the registry itself.

---

## 16. Future phases (reserved — deferred, separately gated)

Everything below is **explicitly out of Phase 1 scope** (owner decision) and is recorded here only so the architecture has documented seams. Nothing here is built, scheduled, or implied to be approved by approving §14–§15. Each item is **gated on its own separate owner approval**, following the same propose → review pack → APPROVE/REVISE/REJECT workflow (§14). This mirrors the platform's standing rule (the DECISION_LOG entry on university work; the "no new generator family without owner direction" discipline) of reserving capacity without activating it.

### 16.1 Full external standards mapping — RESERVED

Phase 1 delivers the alignment **schema, lifecycle, governance, and a tiny pilot** (§15.4) — **not** a mapping. Three frameworks (IGCSE 0580, Singapore Lower Secondary, IB AA SL) already appear inline on 30 objectives; mapping SPI objectives to **IGCSE, IB, Singapore, the Lebanese official curriculum, Common Core, and others** at scale — including migrating those inline records into the governed store and adding the not-yet-mapped frameworks (Lebanese, Common Core) — is a future phase.
- **Architectural seam already in place:** the separate-store schema (§9.4), the direction invariant (alignment → SPI), and the per-alignment `proposed → reviewed → approved` lifecycle.
- **Deferred:** authoring alignment records for whole frameworks; any framework-wide coverage commitment; importing external syllabus documents; denormalizing back to the inline cache.
- **Gate:** each framework is a *separate* owner-approved sub-phase with its own review pack; the **load-bearing principle holds permanently** — external standards never replace, rename, or become the foundation of the engine; the SPI objectiveId remains the single source of truth in every future mapping.

### 16.2 University-level objective architecture — RESERVED

University-level mathematics stays **reserved in the curriculum graph with no active objective architecture or generators**, exactly as the DECISION_LOG already records ("University source material currently is worksheet images only — insufficient").
- **Architectural seam already in place:** the variable-depth ID grammar accommodates a future `UNIVERSITY` (or programme-specific) stage segment with no grammar change; the lifecycle and registry are stage-agnostic.
- **Deferred:** designing university domains/strands; authoring university objectives; any university generator family.
- **Gate:** blocked until fuller university curriculum documents are provided **and** the owner approves a dedicated university sub-phase.

### 16.3 Lesson-plan integration — RESERVED

Lesson plans and **lesson-plan schemas** are explicitly out of scope.
- **Architectural seam already in place:** objectives carry `successCriteria`, `prerequisites`, `vocabulary`, and `relatedObjectives` — sufficient anchors for a future lesson layer to *reference* objective IDs without the registry needing to know about lessons.
- **Deferred:** any lesson-plan schema, authoring, sequencing model, or lesson↔objective binding.
- **Gate:** a separate future phase with its own proposal and owner approval; the objective registry must remain usable with **zero** lesson-plan concepts present.

### 16.4 Analytics — RESERVED

Analytics dashboards, coverage analytics beyond the static Phase-1 coverage report (§10), auto-publishing, and any reporting UI are deferred.
- **Architectural seam already in place:** the §10 coverage report is a static, read-only artifact — a future analytics layer can consume the registry and coverage data without new engine instrumentation.
- **Deferred:** dashboards, live metrics, auto-publishing pipelines, telemetry; nothing auto-advances items past `machine-validated` or auto-publishes.
- **Gate:** a separate future phase, separately approved; analytics may **read** the registry but never **mutate** approved objectives, generator output, or fixtures.

### 16.5 Foundational objective authoring (driven by the known-baseline list) — RESERVED

The `knownBaselineReferencedUndefined` set (§7.5) — the prerequisite IDs the approved data references but does not yet define (e.g. `SPI.MIDDLE.ALG.SUBSTITUTION.01`, `SPI.MIDDLE.NUM.INTEGERS_NUMBER_LINE.01`, `SPI.MIDDLE.GEO.TRIANGLE_CLASSIFY.01`, `SPI.MIDDLE.GEO.ANGLE_MEASURE_NOTATION.01`, `SPI.MIDDLE.ALG.NOTATION_SUBSTITUTION.01`) — is the **authoritative backlog** for a later phase that *authors those foundational objectives*. This is the owner-directed correction-A future recommendation (§7.5 point 10).
- **Architectural seam already in place:** the committed baseline file + the registry gap report make the backlog explicit, sorted, and machine-readable; as each missing objective is authored its reference resolves and the baseline shrinks by exactly that ID (§7.5).
- **Deferred:** authoring any of the baseline objectives; this registry phase only *records and freezes* the list, it never fills it.
- **Gate:** a **separate** owner-approved sub-phase (propose → review → APPROVE/REVISE/REJECT), explicitly **not part of this registry implementation**. When it runs, each newly-authored objective is itself output-neutral with respect to all approved generator families (it only *adds* a definition that an existing reference already points at).

### 16.6 Summary of the Phase-1 boundary

| Capability | Phase 1 | Future (separately gated) |
|---|---|---|
| Objective registry loader + global graph + lifecycle/governance | **Yes** | — |
| Alignment **separate-store schema + lifecycle + tiny pilot** | **Yes** | — |
| Coverage report + integrity gates + docs | **Yes** | — |
| Full IGCSE/IB/Singapore/Lebanese/Common Core mapping; migrate inline records into the store | No | §16.1 |
| University-level objective architecture | No | §16.2 |
| Lesson-plan integration + schemas | No | §16.3 |
| Analytics / dashboards / auto-publishing | No | §16.4 |
| Authoring many new objectives; rewriting approved wording; new generator family; changing approved output; widening the inline `externalAlignments` item | **No (forbidden)** | only via the §14 workflow with explicit owner approval |

Approving this document approves the **architecture** of §14–§15 only. Every reserved item in §16 requires its own proposal and its own owner decision before any work begins.
