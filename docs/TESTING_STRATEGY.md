# Testing Strategy — SPI-Math Question Bank Platform

**Status:** Active architecture document
**Scope:** Testing and independent-verification strategy for all deterministic, seeded question generators.
**Last updated:** 2026-06-19

---

## 1. Testing Philosophy and the Test Pyramid

The SPI-Math platform produces assessment items whose mathematics is generated and verified **by code, never by a language model**. Testing exists to protect four non-negotiable principles:

- **Deterministic mathematics** — answers, distractors, solutions, and metadata are computed by the generator, then checked by code.
- **Reproducibility** — the same `{generator version, config, seed}` reproduces a byte-identical serialized item.
- **Independent verification** — wherever practical, the method that **verifies** an answer is independent from the method that **generated** it.
- **Schema-and-self-check validity** — no item enters the bank until it passes the JSON schema and the generator's own `validate()`.

Because output is deterministic, **flakiness is treated as a defect, not as noise** (see §7). A test that is non-deterministic is either testing the wrong thing or has leaked an entropy source.

### The pyramid for this platform

| Layer | What it covers | Relative volume | Runner |
|---|---|---|---|
| **Unit** | Single operation of one generator (`generate`, `solve`, `validate`, etc.) | Largest | Vitest |
| **Property-based** | Invariants over ALL seeds (thousands of generated cases) | Large | Vitest (fast-check) |
| **High-volume seed sweeps** | >=10,000 seeds per generator, zero invalid items | Large but slower | Vitest |
| **Golden / snapshot** | Reviewed fixed-seed items checked into VCS | Medium | Vitest |
| **Independent oracle cross-check** | TS golden JSON vectors vs. Python reference oracle | Medium | Python (pytest/unittest) |
| **Rendering / a11y** | HTML/SVG/KaTeX correctness, axe-core | Medium | Vitest + jsdom |
| **Integration / CI validation** | Every produced item vs. JSON schema + self-checks | Gate | Vitest + CI |
| **Performance** | Generation throughput budgets | Small | Vitest bench |

> **Environment note.** The production/browser layer is TypeScript compiled to JavaScript for offline standalone HTML apps, tested with **Vitest**. The current development machine has **no Node.js installed yet** — Node.js LTS must be installed before the TS/Vitest suite can run. **Python 3 is available now** and hosts the independent verification **oracle** (a permanent architectural component, not a throwaway).

---

## 2. Per-Generator Required Test Types

Every generator is a versioned module exposing `describe()`, `generate(seed, config)`, `solve(params)`, `validate(item)`, `generateDistractors(item)`, `generateSolution(item)`, `render(item, mode)`, `serialize(item)`. Each generator MUST ship all of the following test types.

### 2.1 Unit tests
- **Definition:** Test one operation in isolation against hand-specified inputs and expected outputs.
- **Acceptance:** Each operation has at least one explicit example per documented behavior branch; all assertions exact (no tolerance unless the contract defines a numeric tolerance).

### 2.2 Property-based tests (invariants over ALL seeds)
- **Definition:** Properties that must hold for every seed in the generator's seed space, exercised via randomized seed sampling (fast-check) plus the high-volume sweep (§3).
- **Required invariants (minimum set):**
  - The canonical answer **always satisfies** the question as posed.
  - **No distractor equals** the canonical answer (under the answer-equivalence relation).
  - **Exactly one** correct option exists in the option set.
  - All generated **parameters lie within the valid domain** declared by `describe()`/config contract.
  - `solve(params)` recomputed from the serialized item reproduces the stored answer.
- **Acceptance:** Zero counterexamples across the sampled and swept seed sets. Any counterexample is logged as a failing seed (§3).

### 2.3 Reproducibility tests
- **Definition:** For a fixed `{version, config, seed}`, `serialize(generate(seed, config))` is **byte-identical** across runs and machines.
- **Acceptance:** Re-running generation N>=3 times yields identical bytes (hash equality). Serialization is canonical (stable key order, fixed number formatting, no embedded timestamps).

### 2.4 Edge-case tests
- **Definition:** Targeted tests at domain boundaries (minima, maxima, zero, negative, identity values, degenerate geometry, carry/borrow boundaries, coprime/GCD edges, etc.).
- **Acceptance:** Each boundary documented in `describe()` has an explicit case; all pass and produce valid items.

### 2.5 Invalid-parameter tests
- **Definition:** The generator **rejects** out-of-contract config (e.g., max < min, unsupported difficulty, disallowed number ranges).
- **Acceptance:** `generate()` throws a typed, documented error for each invalid configuration class; it never returns a malformed item.

### 2.6 Answer-equivalence tests
- **Definition:** Accepted equivalent forms all check **correct**; near-miss forms check **incorrect**.
- **Examples:** `1/2` == `0.5` == `2/4`; `2x+4` == `4+2x`; unsimplified vs. simplified surds — all accepted. Near-misses (sign error, off-by-one, unreduced when reduction is required) — rejected.
- **Acceptance:** A table of `(form, expected verdict)` pairs per generator; 100% match. The equivalence checker is part of `validate()`/answer-checking and is itself unit-tested.

### 2.7 Distractor tests
- **Definition:** Each distractor maps to a **named misconception**; the distractor set is unique; no distractor equals the answer.
- **Acceptance:**
  - Every distractor carries a non-empty `misconceptionId` resolvable in the misconception registry.
  - Distractors are pairwise unique under answer-equivalence.
  - No distractor equals the canonical answer.
  - Distractor count matches the configured option count.

### 2.8 Rendering tests
- **Definition:** `render(item, mode)` produces valid HTML/SVG; KaTeX parses all math; the **prompt contains no answer leakage**.
- **Acceptance:**
  - Output parses as well-formed HTML/SVG (DOM parse, no errors).
  - Every math span parses under KaTeX in strict mode (no fallback/error nodes).
  - The rendered prompt string does not contain the canonical answer or solution text (leakage scan).

### 2.9 Accessibility checks
- **Definition:** Required a11y fields present in metadata; rendered output passes **axe-core**.
- **Acceptance:**
  - Required a11y fields (alt text for figures, ARIA labels, reading-order hints, MathML/aria for math) present and non-empty.
  - axe-core reports **zero violations** of `serious` or `critical` impact on rendered output.

### 2.10 Performance tests
- **Definition:** Generation throughput budget per generator.
- **Acceptance:** Median `generate()+serialize()` time below the per-generator budget. Default budget: **Unknown / to be decided** per difficulty tier; placeholder target <= 5 ms/item until tiers are fixed.

---

## 3. High-Volume Seed Testing

Every generator runs a **seed sweep** of **at least 10,000 seeds** (more where computationally reasonable), asserting **zero invalid items**.

- Each swept item must pass: JSON-schema validation, `validate(item)` self-checks, all property invariants (§2.2), and the leakage scan (§2.8).
- **Zero tolerance:** a single invalid item across the sweep **fails the suite**.
- Every failing seed is recorded in a **failing-seeds log** so it can be reproduced **exactly**.
- Sweeps use a fixed, deterministic seed range (e.g., `0 .. 9999`) so the set is identical on every machine; optional extended ranges may be enabled in CI nightly jobs.

### Failing-seed artifact format

Stored at `artifacts/failing-seeds/<generatorId>@<version>.jsonl` (one JSON object per line):

```json
{
  "generatorId": "fractions.add.v3",
  "generatorVersion": "3.2.0",
  "seed": 80421,
  "config": { "difficulty": "core", "maxDenominator": 12 },
  "failureType": "invariant" ,
  "failedCheck": "no_distractor_equals_answer",
  "message": "distractor[2] equals canonical answer under equivalence",
  "serializedItemHash": "sha256:1f0c...",
  "capturedAt": "2026-06-19T00:00:00Z",
  "runId": "ci-7741"
}
```

`failureType` is one of: `schema`, `selfcheck`, `invariant`, `leakage`, `render`, `a11y`, `oracle-mismatch`. The triplet `{generatorVersion, seed, config}` is sufficient to reproduce the exact item.

---

## 4. Golden Examples

Each generator ships a set of **reviewed golden items** with **fixed seeds**, checked into version control under `generators/<generatorId>/golden/`.

- Golden items are human-reviewed for mathematical and pedagogical correctness.
- Tests assert that current output **matches golden** byte-for-byte (serialized) and structurally (parsed).
- **Changing golden output requires a generator version bump.** A diff in golden output without a version bump fails CI — this makes any behavioral change explicit and reviewable.

| Property | Rule |
|---|---|
| Location | `generators/<generatorId>/golden/*.json` |
| Seeds | Fixed, listed in the golden manifest |
| Review | Required before merge; reviewer recorded in manifest |
| Change policy | Output change => version bump + changelog entry |
| Count | >= 5 golden items per generator covering difficulty tiers (target; **Unknown / to be decided** per subject area) |

---

## 5. Independent Verification via the Python Oracle

The Python **oracle** is a permanent reference implementation that **independently recomputes the mathematics** of each generator. It satisfies the independent-verification principle: the oracle's solving/checking logic is written separately from the TS generator and, where practical, uses a different method (e.g., closed-form vs. iterative, or symbolic vs. numeric).

### The bridge: golden JSON vectors

The TS generators export **golden JSON vectors** — serialized items plus their parameters and canonical answers — which the Python oracle consumes and re-derives.

```
TS generator  --(export golden JSON vectors)-->  vectors/<generatorId>@<version>.json
                                                          |
                                                          v
Python oracle  --(independently recompute)-->  compare answer / distractor-validity / domain
```

**Cross-check procedure per generator:**
1. TS suite emits vectors: for each golden + a deterministic seed subset, write `{seed, config, params, answer, distractors, optionVerdicts}`.
2. The oracle loads each vector and **independently computes** the correct answer from `params` (not from the stored answer).
3. The oracle asserts:
   - Oracle answer **equals** the stored answer under a shared, version-pinned equivalence spec.
   - Every distractor the TS labeled incorrect is **independently incorrect**.
   - The stored answer is **independently correct**.
   - All `params` lie in the declared domain.
4. Any mismatch is recorded as `failureType: "oracle-mismatch"` in the failing-seeds log and **fails CI**.

The equivalence specification (canonical forms, tolerances) is a **shared contract** defined once and referenced by both the TS checker and the Python oracle, so "equivalent" means the same thing on both sides. Divergence in the equivalence spec is itself a defect.

> The oracle is **not** a mirror of generation. It must derive answers by an independent route; copying the TS algorithm into Python defeats the principle and is disallowed in review.

---

## 6. Validation-in-CI

Before any item can **enter the bank**, CI validates it twice:

1. **JSON schema** — the serialized item validates against the platform item schema (`schemas/item.schema.json`).
2. **Generator self-checks** — `validate(item)` passes, including answer-satisfies-question, exactly-one-correct, distractor uniqueness, and a11y-field presence.

CI fails closed: an item that fails either gate is rejected and never published. The seed sweep (§3) and oracle cross-check (§5) run as required CI stages on every change touching a generator.

### Frozen-artifact integrity: canonical hashing

Every approved family freezes its review package behind a generation manifest of SHA-256 digests (`docs/review/*_manifest.json`), and blocking integrity tests (TS + Python) re-hash the artifacts on every run. Those digests are computed over the **canonical bytes** of each artifact — CRLF normalised to LF for text, binary left untouched (git's NUL-probe heuristic) — by the ONE shared helper in each language: `core/integrity/canonical-hash.ts` (`sha256CanonicalFile`) and `oracle/build_meta.py` (`sha256_canonical`), each pinned by its own contract test. Rationale: the repository stores text as LF (`.gitattributes`: `* text=auto eol=lf`) while a Windows working tree may hold CRLF copies that git silently normalises on commit; line endings are a checkout artefact, not artefact content, so a frozen digest must be identical on both. **Never hash raw bytes** for a manifest or an integrity test (`DECISION_LOG.md` #64).

---

## 7. Test Data Management, Determinism Rules, and Flakiness Policy

### Determinism rules (enforced in tests)
- **No wall-clock time.** No `Date.now()`, `new Date()` without a fixed injected clock; serialized items contain no generation timestamp.
- **No `Math.random()`** anywhere in generators or tests. All randomness flows from the **seed** through the injected seeded PRNG.
- **Seeded only.** Property-based and sweep tests derive their cases from fixed seed ranges, not from the global RNG.
- **No environment dependence.** No locale-, timezone-, or filesystem-order-dependent behavior in serialized output.

### Test data management
- Golden items and golden JSON vectors are version-controlled and reviewed.
- Failing-seed artifacts are written to `artifacts/` and uploaded by CI for reproduction.
- Large sweeps stream results; only failures are retained in detail.

### Flakiness policy — zero tolerance
Because output is deterministic, **there is no legitimate source of flakiness**. A test that passes and fails on identical inputs indicates a leaked entropy source (clock, RNG, iteration order, floating-point nondeterminism). Such a test is **quarantined and fixed immediately**; retries are **not** used to paper over flakiness. A flaky test blocks release until root-caused.

---

## 8. Coverage Expectations and Definition of "Stable"

### Coverage
| Metric | Target |
|---|---|
| Line coverage (per generator module) | >= 90% |
| Branch coverage (per generator module) | >= 85% |
| Documented behavior branches with explicit unit test | 100% |
| Invariants from §2.2 implemented | 100% |

Coverage is **necessary but not sufficient** — the property and oracle checks carry the correctness guarantee.

### Definition of done — a generator is **stable** when:
- [ ] All test types in §2 implemented and passing.
- [ ] Seed sweep of >= 10,000 seeds passes with **zero** invalid items.
- [ ] Reproducibility verified (byte-identical serialization across runs).
- [ ] Golden items reviewed and committed; golden-match tests pass.
- [ ] Golden JSON vectors cross-checked against the Python oracle with zero mismatches.
- [ ] Every distractor maps to a registered misconception.
- [ ] Rendering passes KaTeX-strict and leakage scan; axe-core reports zero serious/critical violations.
- [ ] Performance within budget.
- [ ] Coverage targets met.
- [ ] `describe()` contract documented, including valid domains and rejected configs.

A generator not meeting **all** of the above is marked `experimental`, not `stable`.

---

## 9. Tooling and How to Run

| Concern | Tool |
|---|---|
| TS/JS production suite | **Vitest** (with fast-check for property tests, jsdom for rendering) |
| Python reference oracle | **pytest** (or `unittest`) |
| Accessibility | **axe-core** on rendered output |
| Math rendering check | **KaTeX** strict parse |
| Schema validation | JSON Schema validator (e.g., Ajv) |

> **Node.js prerequisite.** The TS/Vitest suite requires Node.js LTS, which is **not yet installed** on this machine. Install Node.js LTS before running any `npm`/`vitest` command below.

### Example commands

Install and run the TypeScript suite (requires Node.js LTS):
```bash
# one-time, after installing Node.js LTS
npm install

# full unit + property + golden + rendering suite
npx vitest run

# only the high-volume seed sweep
npx vitest run --testNamePattern "seed sweep"

# performance benchmarks
npx vitest bench
```

Run the Python oracle cross-check (works now; Python 3 is available):
```bash
# from the repo root
python -m pytest oracle/ -v

# or with unittest
python -m unittest discover -s oracle -p "test_*.py"
```

Accessibility (runs within the Vitest rendering tests via axe-core; requires Node.js):
```bash
npx vitest run --testNamePattern "a11y"
```

---

## 10. Release Gate Checklist

A generator (or a release containing generator changes) may ship **only when every box is checked**:

- [ ] All Vitest suites pass (unit, property, edge, invalid-param, equivalence, distractor, rendering, a11y, reproducibility).
- [ ] Seed sweep >= 10,000 seeds: **zero** invalid items; failing-seeds log empty for this version.
- [ ] Serialization is byte-identical across >= 3 runs (reproducibility confirmed).
- [ ] Golden items and golden JSON vectors committed and reviewed; golden-match tests pass.
- [ ] Python oracle cross-check passes with **zero** `oracle-mismatch` entries.
- [ ] Every produced item validates against the JSON schema **and** `validate()` self-checks in CI.
- [ ] Each distractor maps to a named, registered misconception; uniqueness and no-equals-answer confirmed.
- [ ] KaTeX strict parse passes; prompt leakage scan clean.
- [ ] axe-core: zero serious/critical violations.
- [ ] Performance within budget (or budget recorded as **Unknown / to be decided** and explicitly accepted by reviewer).
- [ ] Coverage targets met (§8).
- [ ] If golden output changed, generator **version was bumped** and changelog updated.
- [ ] No flaky/quarantined tests outstanding.
- [ ] Node.js LTS present in the CI runner so the TS suite actually executed (not skipped).

---

*End of document.*
