# Generator Specification — gen.functions.foundations v1.0.0 (Introducing Functions: notation, domain & range, composition, inverses) — PROPOSAL

**Status: PROPOSAL, implemented oracle-first as `pending-review` (NOT curriculum-approved).** The owner
delegated the choice of the tenth generator family ("you decide; best is to go through the largest") on
2026-09-26 while unable to review interactively. Under the project's governance (`GENERATOR_SDK_DESIGN.md`
§7) a family is normally proposed → approved → built; here the proposal and the build are delivered
together and the family is registered `approvalStatus: "pending-review"` — visible only in the Studio's
review mode, excluded from production samples/exports, its eleven objectives at `reviewStatus:
"proposed"` — until the owner reviews the pack and decides **APPROVE / REVISE / REJECT**. Nothing in this
family is auto-approved; every generated item begins at `machine-validated`.

Generator id: **`gen.functions.foundations`** · version **`1.0.0`** · validator `1.0.0` · stage
**IB Mathematics: Analysis and Approaches SL** · Oxford chapter 2 *Representing Relationships:
Introducing Functions* (Oxford ToC 2.1, 2.2, 2.4, 2.5, 2.6; 2.3 *Drawing graphs of functions* is
GDC/graph-window work and is excluded, §12). IB AA guide alignment: **SL 2.2** (concept of a function,
domain, range, function notation, informal inverse) and **SL 2.5** (composite functions, finding the
inverse function). The tenth generator family; the third IBDP AASL family (after the two sequence
families); the first family since the Objective Registry Phase-1 freeze (§13 records the registry impact).

### Table of contents

1. Curriculum placement and objective IDs
2. Objective wording and prerequisites
3. Task and interaction matrix
4. The exact function model and the parameter draws
5. Answer contracts — two NEW canonical-first answer types (`algebraic-expression`, `interval`)
6. Parsers, canonicalizers, equivalence checkers and result codes
7. Solver and independent-validator design
8. Misconception and diagnostic registry (`MISC.FUNC.*`)
9. Worked-solution structure
10. Difficulty model
11. Rendering, accessibility and leakage policy
12. Scope guard and exclusions
13. Registry, schema and manifest impact (the first post-freeze family)
14. Review package, versioning and the owner decision

---

## 1. Curriculum placement and objective IDs

### 1.1 Domain, strand, and segment

| Field | Value | Note |
| --- | --- | --- |
| `stage` | `ibdp-aasl` | ID segment `IBDPAASL` (existing vocabulary) |
| `domain` | **`functions`** | ID segment **`FUNC`** — a NEW entry in the closed §4 controlled vocabulary (`registry-graph.ts` `domainMap`); adding it is a governance action recorded in `DECISION_LOG.md` #65 |
| `strand` | **`introducing-functions`** | NEW strand vocabulary entry (same governance action) |
| `programme` / `course` | `IB Diploma Programme` / `IB Mathematics: Analysis and Approaches SL` | as the sequence families |
| ID scheme | `SPI.IBDPAASL.FUNC.<MICRO>.01` | five segments (no sub-segment): stage · domain · micro · NN — parses under the variable-depth grammar |

### 1.2 The eleven micro-objectives (single-source task slugs)

| Task slug | Objective ID | Oxford ToC | Bands |
| --- | --- | --- | --- |
| `identify_function` | `SPI.IBDPAASL.FUNC.IDENTIFY_FUNCTION.01` | 2.1 What is a function? | 1–2 |
| `evaluate_function` | `SPI.IBDPAASL.FUNC.EVALUATE.01` | 2.2 Functional notation | 1–3 |
| `solve_for_input` | `SPI.IBDPAASL.FUNC.SOLVE_FOR_INPUT.01` | 2.2 Functional notation | 2–3 |
| `domain_of_function` | `SPI.IBDPAASL.FUNC.DOMAIN.01` | 2.4 Domain and range | 2–4 |
| `range_of_function` | `SPI.IBDPAASL.FUNC.RANGE.01` | 2.4 Domain and range | 3–5 |
| `composite_value` | `SPI.IBDPAASL.FUNC.COMPOSITE_VALUE.01` | 2.5 Composite functions | 2–3 |
| `composite_expression` | `SPI.IBDPAASL.FUNC.COMPOSITE_EXPRESSION.01` | 2.5 Composite functions | 3–5 |
| `function_from_composite` | `SPI.IBDPAASL.FUNC.FUNCTION_FROM_COMPOSITE.01` | 2.5 Composite functions | 4–5 |
| `inverse_value` | `SPI.IBDPAASL.FUNC.INVERSE_VALUE.01` | 2.6 Inverse functions | 2–4 |
| `inverse_expression` | `SPI.IBDPAASL.FUNC.INVERSE_EXPRESSION.01` | 2.6 Inverse functions | 3–4 |
| `one_to_one_restriction` | `SPI.IBDPAASL.FUNC.ONE_TO_ONE_RESTRICTION.01` | 2.6 Inverse functions | 4–5 |

The task → objective map is single-sourced in `core/curriculum/functions-objective-ids.ts`
(`OBJECTIVE_BY_TASK`) and mirrored verbatim by `oracle/spi_oracle/functions.py`; a parity test asserts
the two agree and that all eleven IDs exist in `curriculum/objectives/SPI.IBDPAASL.FUNC.json`.

---

## 2. Objective wording and prerequisites

All prerequisites resolve to existing objectives (approved) or to objectives in this file, except
`SPI.MIDDLE.ALG.SUBSTITUTION.01`, which is already in the frozen known-baseline referenced-undefined set
(referenced by `SPI.IBDPAASL.SEQSER.ARITH.NTH_TERM.01`): citing it again introduces **no new**
referenced-undefined ID (§13). The intra-family prerequisite DAG is acyclic:

```
EVALUATE ──► SOLVE_FOR_INPUT ──► INVERSE_VALUE ──► INVERSE_EXPRESSION ──┐
   │  └────► DOMAIN ──► RANGE ─────────────────────────────────────────┼─► ONE_TO_ONE_RESTRICTION
   └────► COMPOSITE_VALUE ──► COMPOSITE_EXPRESSION ──► FUNCTION_FROM_COMPOSITE
IDENTIFY_FUNCTION (foundational; prerequisite: COORD.CARTESIAN_PLANE)
```

| Objective | Wording (proposed) | Hard prerequisites |
| --- | --- | --- |
| `IDENTIFY_FUNCTION` | Decide whether a relation given as a set of ordered pairs is a function, by checking that each input has exactly one output. | `SPI.MIDDLE.GEO.COORD.CARTESIAN_PLANE.01` |
| `EVALUATE` | Evaluate a function given by a rule (linear, quadratic, reciprocal or square-root) at a stated input, using function notation. | `SPI.MIDDLE.NUM.SIGNED_OPERATIONS.01`, `SPI.MIDDLE.ALG.SUBSTITUTION.01` |
| `SOLVE_FOR_INPUT` | Find the input of a function that produces a stated output, by solving the equation f(x) = k exactly. | `FUNC.EVALUATE.01`, `SPI.MIDDLE.ALG.LINEQ.TWOSTEP.01` |
| `DOMAIN` | State the largest possible domain of a function given by a rule, identifying the inputs excluded by a square root or a denominator. | `FUNC.EVALUATE.01` |
| `RANGE` | State the range of a function given by a rule, including a quadratic, a shifted square-root or reciprocal function, and a linear function on a restricted domain. | `FUNC.DOMAIN.01` |
| `COMPOSITE_VALUE` | Evaluate a composite function at a stated input, applying the inner function first. | `FUNC.EVALUATE.01` |
| `COMPOSITE_EXPRESSION` | Find and simplify an expression for a composite of two functions, one of which may be quadratic. | `FUNC.COMPOSITE_VALUE.01`, `SPI.MIDDLE.ALG.EXPAND_BRACKETS.01` |
| `FUNCTION_FROM_COMPOSITE` | Determine the outer function when the inner function and the composite are given. | `FUNC.COMPOSITE_EXPRESSION.01` |
| `INVERSE_VALUE` | Evaluate the inverse of a linear function at a stated value, and solve equations of the form f⁻¹(k) = c. | `FUNC.SOLVE_FOR_INPUT.01` |
| `INVERSE_EXPRESSION` | Find an expression for the inverse of a linear function. | `FUNC.INVERSE_VALUE.01`, `SPI.MIDDLE.ALG.LINEQ.TWOSTEP.01` |
| `ONE_TO_ONE_RESTRICTION` | Determine the domain restriction at the vertex that makes a quadratic function one-to-one so that its inverse exists. | `FUNC.RANGE.01`, `FUNC.INVERSE_EXPRESSION.01` |

Shared metadata: `academy: "SPI-Math"`, `calculatorPolicy: "calculator-not-required"` (Paper-1 style
exact work), `sourceReferences: [{sourceId: "SRC-aasl-ch02", locator: "Oxford ToC 2.x …"}]`,
`externalAlignments: [{framework: "IB Mathematics AA SL", code: "SL2.2" | "SL2.5", label: "Functions"}]`,
`reviewStatus: "proposed"`, `version: "1.0.0"`. Full records (successCriteria, vocabulary, notation,
misconceptions, related links) are in `curriculum/objectives/SPI.IBDPAASL.FUNC.json`.

---

## 3. Task and interaction matrix

FREE-RESPONSE first; multiple-choice wherever three distinct formula-backed misconception pathways exist
for every drawn item (deterministic parameter redraw otherwise). `identify_function` is
**multiple-choice-only** (its mathematics *is* the selection among relations; precedent: ratio
`best_buy`). An explicit request for an unsupported interaction raises `interaction-not-supported`
(never a silent substitution); a no-task request narrows the draw pool to tasks that serve the requested
interaction, exactly as ratio v1.0.2. Only the forward key `interactionType` is consulted: the legacy
`answerType` selector (TD-1) is ignored, as in ratio v1.0.2, so a legacy sweep exercises every task at its
default interaction (`identify_function` stays multiple-choice) and never raises.

| Task | Interactions | `answer.type` (free-response) | Answer shape |
| --- | --- | --- | --- |
| `identify_function` | MC only | `multiple-choice` (canonical = correct option label) | 4 relations, each a set of 4 ordered pairs; exactly one is NOT a function |
| `evaluate_function` | FR, MC | `integer` \| `exact-rational` | `{num, den}` |
| `solve_for_input` | FR, MC | `integer` \| `exact-rational` | `{num, den}` |
| `domain_of_function` | FR, MC | **`interval`** (NEW, §5.2) | real-subset descriptor in `x` |
| `range_of_function` | FR, MC | **`interval`** | real-subset descriptor in `y` |
| `composite_value` | FR, MC | `integer` \| `exact-rational` | `{num, den}` |
| `composite_expression` | FR, MC | **`algebraic-expression`** (NEW, §5.1) | polynomial in `x`, degree ≤ 2 |
| `function_from_composite` | FR, MC | **`algebraic-expression`** | polynomial in `x`, degree 1 |
| `inverse_value` | FR, MC | `integer` \| `exact-rational` | `{num, den}` |
| `inverse_expression` | FR, MC | **`algebraic-expression`** | polynomial in `x`, degree 1 |
| `one_to_one_restriction` | FR, MC | `integer` \| `exact-rational` | `{num, den}` |

Scope guard: exactly these eleven tasks; `config.task` outside the list raises `unknown task`.

---

## 4. The exact function model and the parameter draws

### 4.1 One exact engine, no floats

Every coefficient, input and answer is an exact rational `{num, den}` (den ≥ 1, reduced). Four rule
kinds, each a small record (JSON-encoded in `item.params`):

| kind | record | f(x) | display (LaTeX in prompts) |
| --- | --- | --- | --- |
| `linear` | `{kind, a, b}`, a ≠ 0 | a·x + b | `2x - 3`, `-x + 5`, `\frac{1}{2}x + 3` |
| `quadratic` | `{kind, a, b, c}`, a ≠ 0 | a·x² + b·x + c | `x^{2} - 4x + 1`, `-2x^{2} + 3` |
| `reciprocal` | `{kind, k, h, v}`, k ≠ 0 | k/(x − h) + v | `\frac{3}{x - 2} + 1`, `-\frac{2}{x + 1}` |
| `sqrt` | `{kind, a, b, v}`, a ≠ 0 | √(a·x + b) + v | `\sqrt{2x + 5}`, `\sqrt{5 - 2x} - 1` (a < 0 renders `b − |a|x`) |

Polynomials are handled by a purpose-built exact `Polynomial` (dense rational coefficient vector,
ascending degree; add / sub / mul / scale / compose / eval / degree; canonical = trailing zeros stripped,
the zero polynomial is `[0]`) in `core/exact-math/polynomial.ts` and `oracle/spi_oracle/polynomial.py`.
It is NOT a CAS: no factoring, no rational functions, no radicals; square-root and reciprocal rules are
only ever *evaluated* at inputs where the result is exactly rational (perfect-square radicands,
non-pole inputs), which the draws guarantee by backward construction.

### 4.2 Draw pools (defaults; the Python oracle's draw ORDER is normative for parity)

`NZ9 = [−9..9]∖{0}`, `NZ6 = [−6..6]∖{0}`, `NZ5 = [−5..5]∖{0}`, `SMALL = [−3..3]∖{0}`, `INT6 = [−6..6]`,
`ROOT_T = [0..6]` (the square-root value t), function names for single-function tasks drawn from
`["f", "g", "h"]`; composite tasks use `f` (first-defined) and `g`, with `order ∈ {"fg", "gf"}` meaning
`(f ∘ g)` or `(g ∘ f)`. Each task draws, then passes `_acceptable` (structural guards + caps
|num| ≤ 10 000, den ≤ 144) and, in MC mode, must yield three distinct eligible distractors; otherwise the
generator redraws (≤ 256 attempts, deterministic).

| Task | Construction (backward, exact) | Guards |
| --- | --- | --- |
| `identify_function` | 4 relations of 4 pairs; inputs in `[0..9]` or `[−4..9]` (lever); the correct option repeats one input with two different outputs; distractors: many-to-one (a repeated output, not all equal), constant (all outputs equal), pattern-free (distinct inputs listed unsorted, distinct outputs, not collinear) | all inputs of the three function options distinct; option displays pairwise distinct |
| `evaluate_function` | kind ∈ {linear, quadratic, reciprocal, sqrt}; input p ∈ INT6; sqrt: choose t ∈ ROOT_T, a ∈ SMALL, set b = t² − a·p; reciprocal: p ≠ h and (p − h) \| k not required (rational answers allowed) | answer within caps; reciprocal p ≠ h |
| `solve_for_input` | kind ∈ {linear, reciprocal, sqrt}; choose the intended input x₀ first: linear x₀ ∈ INT6 ∪ {halves, thirds at band 3}, k = a·x₀ + b; reciprocal x₀ ≠ h with (x₀ − h) \| k so the output m is an integer; sqrt t ∈ ROOT_T, b = t² − a·x₀, m = t + v | unique solution by construction; k ≠ v for reciprocal |
| `domain_of_function` | kind pool `[sqrt, sqrt, reciprocal, reciprocal, linear, quadratic]` (weighted so "all reals" is ⅓); sqrt a ∈ NZ5, b ∈ INT6 (endpoint −b/a may be fractional at band 4); reciprocal h ∈ INT6, k ∈ NZ6, v ∈ INT6 | polynomial constant term ≠ 0 (so `DOMAIN_EXCLUDES_CONSTANT` is meaningful) |
| `range_of_function` | kind pool `[quadratic, quadratic, sqrt, reciprocal, linear_restricted]`; quadratic a ∈ {1, 2, −1, −2, 3, −3}, b, c ∈ INT6; sqrt as above with v ∈ INT6; reciprocal with v; linear_restricted: a ∈ NZ5, b ∈ INT6, domain p ≤ x ≤ q with p < q from `[−5..5]` | quadratic b ≠ 0 when a = ±1 is allowed (vertex may be 0) |
| `composite_value` | outer/inner kinds ∈ {linear, quadratic} (any pair), order ∈ {fg, gf}, input p ∈ INT6 | composite value within caps |
| `composite_expression` | kinds with at most ONE quadratic (degree ≤ 2 answer), order ∈ {fg, gf} | the reversed composite must be a genuinely different polynomial when `COMP_ORDER_REVERSED` is used |
| `function_from_composite` | choose the OUTER f = A·x + B first (A ∈ NZ5, B ∈ INT6); inner g = m·x + c with m ∈ {1, 1, 2, −1}, c ∈ NZ6; publish g and (f ∘ g) = A·m·x + (A·c + B); answer f | A·m ≠ 0 |
| `inverse_value` | f = a·x + b linear, a ∈ NZ5 (halves at band 4), b ∈ INT6; form ∈ {`inverse_at` (find f⁻¹(k), k = f(x₀) for x₀ ∈ INT6), `solve_inverse_equation` (find k with f⁻¹(k) = x₀ ⇒ k = f(x₀))} | — |
| `inverse_expression` | f = a·x + b, a ∈ NZ5 ∪ {1/2, −1/2, 1/3} at band 4, b ∈ INT6 | a ≠ 0 |
| `one_to_one_restriction` | quadratic a ∈ {1, 1, −1, 2, −2, 3}, b ∈ NZ6 (b ≠ 0 so the axis is not x = 0), c ∈ INT6; side ∈ {`ge` (x ≥ k, least k), `le` (x ≤ k, greatest k)} | — |

---

## 5. Answer contracts — two NEW canonical-first answer types

Both follow the approved canonical-first precedent (mensuration `quantity`, transformations
`transformation`, ratio `ratio`): the structured object **IS** `answer.canonical`; `answer.display` is a
derived plain-text string (the Studio and exporters render `display` as escaped text, never as LaTeX, so
displays are ASCII: `x^2 - 4x + 1`, `(1/3)x + 2/3`, `x >= 2`, `x != 3`, `-1 <= y <= 4`,
`all real numbers`); a formatted string is never the canonical value. The extension is ADDITIVE to
`schemas/question-item.schema.json` (`if/then` rules keyed on `answer.type`; no approved fixture is
affected; the compiled Ajv validator is regenerated; the Python conformance checker enforces the same
rules). Both enum values already exist in `$defs.answerType`; this proposal gives them a canonical shape.

### 5.1 `algebraic-expression` — polynomial canonical form

```
answer = {
  type: "algebraic-expression",
  canonical: { variable: "x", coefficients: [ {num,den}, {num,den}, ... ] },   // ascending degree, trailing zeros stripped, minItems 1
  display: "4x^2 - 12x + 10"                                                    // derived; descending degree; ±1 coefficients implicit
}
```

Schema rule: `if type == "algebraic-expression" then canonical is an object with required `variable`
(const "x" in v1.0.0) and `coefficients` (array, minItems 1, items `{num: integer, den: integer ≥ 1}`)`.
Equivalence is exact coefficient-vector equality after canonicalisation (§6.1); any equivalent
form the parser can expand (brackets, products, powers, division by a constant) is accepted.

Distractor values for this type are polynomials in the same encoding, except the diagnostic
`MISC.FUNC.INV_AS_RECIPROCAL` whose value is the structured non-polynomial
`{kind: "reciprocal-of", coefficients: [...]}` (display `1/(3x + 2)`); the validator recomputes it from
its rule like every other distractor. Distractor values are never parsed by the checker.

### 5.2 `interval` — real-subset canonical form

```
canonical = { kind: "reals" }
          | { kind: "ray",          variable, endpoint: {num,den}, inclusive: bool, direction: "ge" | "le" }
          | { kind: "bounded",      variable, lo: {num,den}, hi: {num,den}, loInclusive: bool, hiInclusive: bool }   // lo < hi
          | { kind: "reals-except", variable, points: [ {num,den}, ... ] }                                          // sorted ascending, distinct
variable ∈ { "x", "y" }   // x for a domain, y for a range
```

Displays: `all real numbers`, `x >= 2`, `x <= -5/2`, `x > 0`, `y >= -4`, `-1 <= y <= 4`, `x != 3`,
`y != 1`. Schema rule: `if type == "interval" then canonical.kind ∈ enum and the kind-specific fields are
required` (one `if/then` per kind; no `oneOf`, so the offline Python conformance checker enforces it).

---

## 6. Parsers, canonicalizers, equivalence checkers and result codes

Both checkers are ASCII-anchored finite grammars (the ratio lesson: the Python and TS parsers must accept
and reject identically — a cross-engine corpus test pins both), with a handful of unicode conveniences
(`²`, `³`, `×`, `·`, `−`, `≥`, `≤`, `≠`, `∞`, `ℝ`, `∈`) normalised to ASCII before parsing. Digits are
ASCII only. Inputs are trimmed and capped at 200 characters.

### 6.1 Expression checker (`core/answer-checking/expression-checker.ts`, `oracle/spi_oracle/expression_checker.py`)

Grammar (single variable `x`): `expr := term (('+'|'-') term)*`; `term := factor (( '*' | implicit ) factor | '/' constant-factor)*`;
`factor := ['+'|'-'] base ('^' natural | '**' natural | '²' | '³')?`; `base := number | 'x' | '(' expr ')'`;
`number := integer | integer '/' integer | terminating decimal`. A literal `a/b` immediately followed by `x`
or `(` is a coefficient (`1/3x` = `(1/3)x`, the coordinate-checker convention); otherwise `/` is division,
which is legal only by a constant (degree-0) sub-expression. Degree is capped at 6 during expansion.

| Code | Meaning |
| --- | --- |
| `correct` | parses to a polynomial equal to the canonical coefficient vector |
| `unparseable` | not in the grammar (empty, stray symbols, unbalanced brackets, `=` present) |
| `wrong-variable` | a letter other than `x` appears |
| `not-polynomial` | division by a non-constant, or a negative exponent |
| `wrong-degree` | a polynomial of a different degree |
| `wrong-coefficients` | same degree, different coefficients |
| `misconception` | equals a named wrong form supplied by the item (e.g. the reversed composite); `misconceptionId` returned |

### 6.2 Interval checker (`core/answer-checking/interval-checker.ts`, `oracle/spi_oracle/interval_checker.py`)

Accepted forms: inequalities (`x >= 2`, `2 <= x`, `x > 2`, `-1 < x <= 4`), interval notation (`[2, inf)`,
`(-inf, 2]`, `[-1, 4]`, `(2, 5)`, with `inf` | `infinity` | `oo` | `∞`), exclusions (`x != 3`, `x =/= 3`,
`x != 3, 5`, `all real numbers except 3`, `R \ {3}`), the whole line (`all real numbers`, `all reals`,
`R`, `(-inf, inf)`, `x in R`), and set-builder wrappers (`{x | x >= 2}`, `{x : x != 3}`). The variable
may be `x`, `y`, or `f(x)`/`g(x)`/`h(x)` (read as `y`); interval notation carries no variable and is
accepted for either.

| Code | Meaning |
| --- | --- |
| `correct` | same canonical real subset (endpoint(s), inclusivity, direction/kind) |
| `unparseable` | not in the grammar |
| `wrong-variable` | a domain answer written in `y`, or a range answer written in `x` |
| `wrong-kind` | e.g. `x != 2` for a ray, or a bounded interval for a ray |
| `wrong-endpoint` | right kind/direction/inclusivity, different endpoint(s) |
| `wrong-inclusivity` | right endpoint(s), strict/inclusive boundary differs |
| `wrong-direction` | ray in the opposite direction |
| `misconception` | equals a named wrong form supplied by the item; `misconceptionId` returned |

Both checkers accept `terminating decimal` numbers (parsed exactly as rationals); the numeric answer
types reuse the approved `rational-checker`.

---

## 7. Solver and independent-validator design

`solve` (canonical method) and `validate` (independent method) genuinely differ per task; the validator
never calls the forward solver for its core check:

| Task | Canonical method (`solve`) | Independent confirmation (`validate` check name) |
| --- | --- | --- |
| `identify_function` | the constructed non-function's option label | `exactly-one-non-function`: re-scan every option's pairs for a repeated input with different outputs; `distractor-structure-matches-misconception` (many-to-one / constant / pattern-free re-derived from the pairs) |
| `evaluate_function` | direct substitution through the rule record | `value-recomputed-independently`: Horner evaluation of the polynomial coefficient vector (poly kinds); explicit radicand/denominator arithmetic for sqrt/reciprocal with perfect-square / non-zero checks |
| `solve_for_input` | inverse operations in closed form | `solution-satisfies-equation`: substitute the stored answer into the rule and compare with k exactly |
| `domain_of_function` | rule-type case analysis | `domain-boundary-probe`: probe endpoint, endpoint ± 1 (and ± ½ for fractional endpoints): the radicand/denominator must be admissible exactly where the descriptor says |
| `range_of_function` | vertex formula / shift / monotone endpoints | `range-attained-and-bounded`: quadratic — the bound is attained at h = −b/2a and f(h ± 1), f(h ± 2) lie on the stated side; sqrt/reciprocal — bound attained/excluded by direct evaluation; linear — endpoint images sorted |
| `composite_value` | f(g(p)) via the rule records | `composite-recomputed-stepwise`: inner value first, then outer by Horner on coefficient vectors |
| `composite_expression` | symbolic `Polynomial.compose` | `composite-pointwise-agreement`: agreement at x = −2, −1, 0, 1, 2 (5 points ≥ degree + 1 ⇒ identity) + `degree-bound` |
| `function_from_composite` | f(u) = (p/m)·u + (q − p·c/m) | `recomposes-to-given`: compose the stored f with g and compare to the given composite coefficient-wise |
| `inverse_value` | (k − b)/a or f(x₀) by form | `inverse-value-satisfies-forward`: f(answer) = k (form i) / f⁻¹(answer) = x₀ by re-solving (form ii) |
| `inverse_expression` | (1/a)·x − b/a | `inverse-round-trip`: f ∘ f⁻¹ composes to the identity polynomial `[0, 1]` symbolically |
| `one_to_one_restriction` | h = −b/(2a) | `axis-of-symmetry-probe`: f(h + t) = f(h − t) for t = 1, 2, 3 exactly (no formula reuse) |

Every task also runs: `params-in-domain`, `answer-type-consistency`, `interaction-type`,
`canonical-form-normalized` (reduced rationals; stripped polynomial; sorted distinct exclusion points;
lo < hi), `display-reparses-to-canonical` (the family's own checker parses `answer.display` back to the
canonical value with code `correct` — closing the display/parser loop), `answer-solution-agree`,
`no-answer-leakage`, `a11y-fields-present`, `provenance-complete`, `version-fields-present`; MC items add
`exactly-one-correct`, `distractors-unique`, `min-three-distractors`, `distractors-distinct-misconceptions`,
`distractor-misconception-known`, `distractor-value-matches-rule` (recomputed from the rule),
`distractor-rationale-matches`, `distractor-feedback-present`, `distractor-feedback-clean` (no internal
symbols), `distractor-not-answer`.

---

## 8. Misconception and diagnostic registry (`MISC.FUNC.*`)

Every rule is an independently recomputable wrong value over the item's rule record(s); it returns
`null` when inapplicable or when it would equal the answer. Student feedback is generated from the
displayed coefficients (no internal placeholder symbols). Records live in
`core/misconceptions/functions.json` (schema-validated; `validRange.levels: ["ibdp-aasl"]`) with rule
code in `oracle/spi_oracle/functions_misconceptions.py` ⇄ `domains/functions/functions-misconceptions.ts`.

| Task | Eligible misconception IDs (wrong value) |
| --- | --- |
| `identify_function` | `MANY_TO_ONE_REJECTED` (a function with a repeated output), `CONSTANT_REJECTED` (a constant function), `PATTERN_REQUIRED` (a function with no formula-like pattern) |
| `evaluate_function` | `EVAL_FORGOT_MULTIPLY` (linear: a + p + b), `EVAL_DROP_CONSTANT` (omit b / c / v), `EVAL_SIGN_OF_INPUT` (p < 0: f(\|p\|)), `EVAL_CONSTANT_SIGN_FLIPPED` (a·p − b, a·p² + b·p − c), `EVAL_SQUARE_NEGATIVE` (p < 0: −p² used), `EVAL_SQUARE_COEFFICIENT` ((a·p)² + b·p + c), `EVAL_SQUARE_AS_DOUBLE` (2a·p + b·p + c), `EVAL_DENOMINATOR_NOT_GROUPED` (k/p − h + v), `EVAL_RECIPROCAL_INVERTED` ((p − h)/k + v), `EVAL_ROOT_IGNORED` (a·p + b + v), `EVAL_HALVE_INSTEAD_OF_ROOT` ((a·p + b)/2 + v), `EVAL_NEGATIVE_ROOT` (−t + v) |
| `solve_for_input` | `SOLVE_EVALUATES_INSTEAD` (f(k)), `SOLVE_WRONG_INVERSE` ((k + b)/a; sqrt (t² + b)/a), `SOLVE_STOPS_BEFORE_DIVIDING` (k − b), `SOLVE_DIVIDE_BY_CONSTANT` ((k − b)/b), `SOLVE_RECIPROCAL_NOT_INVERTED` (h + (m − v)/k), `SOLVE_POLE_SIGN` (k/(m − v) − h), `SOLVE_IGNORES_SHIFT` (h + k/m), `SOLVE_FORGOT_TO_SQUARE` ((t − b)/a), `SOLVE_SQUARE_BEFORE_ISOLATING` ((m² − v − b)/a) |
| `domain_of_function` | `DOMAIN_ALL_REALS`, `DOMAIN_DIRECTION_FLIPPED`, `DOMAIN_STRICT_ENDPOINT`, `DOMAIN_ENDPOINT_SIGN` (x ≥ b/a), `DOMAIN_AS_EXCLUDED_POINT` (x ≠ −b/a), `DOMAIN_POLE_SIGN` (x ≠ −h), `DOMAIN_EXCLUDES_ZERO` (x ≠ 0), `DOMAIN_POLE_AS_INEQUALITY` (x > h), `DOMAIN_NONNEGATIVE_ONLY` (x ≥ 0), `DOMAIN_EXCLUDES_CONSTANT` (x ≠ c) |
| `range_of_function` | `RANGE_ALL_REALS`, `RANGE_DIRECTION_FLIPPED`, `RANGE_USES_VERTEX_X` (y ≥ h), `RANGE_STRICT_AT_BOUND`, `RANGE_USES_CONSTANT_TERM` (y ≥ c), `RANGE_IGNORES_SHIFT` (y ≥ 0 / y ≠ 0), `DOMAIN_RANGE_CONFUSED` (the domain restated in y), `RANGE_POLE_AS_INEQUALITY` (y > v), `RANGE_ONLY_LOWER_BOUND` (y ≥ min), `RANGE_STRICT_ENDPOINTS` (open interval) |
| `composite_value` | `COMP_ORDER_REVERSED` (g(f(p))), `COMP_AS_PRODUCT` (f(p)·g(p)), `COMP_AS_SUM` (f(p) + g(p)), `COMP_INNER_ONLY` (g(p)), `COMP_OUTER_AT_INPUT` (f(p)) |
| `composite_expression` | `COMP_ORDER_REVERSED`, `COMP_AS_PRODUCT`, `COMP_AS_SUM`, `COMP_SQUARE_NO_CROSS_TERM` ((mx + n)² → m²x² + n²) |
| `function_from_composite` | `FFC_IGNORES_INNER` (f = the composite), `FFC_SHIFT_NOT_INVERTED` (p·(x + c)/m + q), `FFC_SCALE_NOT_INVERTED` (p·m·(x − c) + q), `FFC_COMPOSES_INSTEAD` (p·(m·x + c) + q) |
| `inverse_value` | `INVVAL_FORWARD` (f(k)), `INVVAL_RECIPROCAL` (1/f(·)), `INVVAL_APPLIES_INVERSE_AGAIN` ((x₀ − b)/a), `INVVAL_IDENTITY` (x₀), `INV_UNDO_ORDER` (k/a − b), `INV_SIGN_ERROR` ((k + b)/a; a·x₀ − b) |
| `inverse_expression` | `INV_AS_RECIPROCAL` (1/(ax + b)), `INV_UNDO_ORDER` (x/a − b), `INV_SIGN_ERROR` ((x + b)/a), `INV_NEGATES_ONLY` (a·x − b), `INV_SWAPS_ROLES` ((x − a)/b) |
| `one_to_one_restriction` | `VERTEX_X_MISSING_HALF` (−b/a), `VERTEX_X_SIGN` (b/2a), `VERTEX_Y_FOR_X` (f(h)), `RESTRICTION_ZERO` (0), `VERTEX_X_USES_C` (−c/2a) |

Each MC item uses three DISTINCT pathways; on collision (a rule's value equals the answer or another
distractor) the rule is skipped and, if fewer than three remain, the parameters are redrawn
deterministically. Feedback strings are student-facing and item-specific.

---

## 9. Worked-solution structure

Structured `solution.steps[]` (`number`, `transformation`, `intermediateResult`, `explanation` /
`ruleOrTheorem`, `dependsOn`, `marks` on the final statement), the final step stating the canonical
display (the `answer-solution-agree` gate). Templates: *evaluate* — substitute → arithmetic → state;
*solve* — set f(x) = k → undo each operation → state → verify by substitution; *domain* — identify the
restriction (radicand ≥ 0 / denominator ≠ 0 / none) → solve the restriction → state; *range* — vertex /
shift / monotone endpoints → state; *composite value* — inner value → outer value; *composite
expression* — substitute the inner into the outer → expand → collect like terms → state; *function from
composite* — write f(g(x)) = given → let u = g(x), x = (u − c)/m → simplify → state; *inverse* — y = f(x)
→ swap x and y → solve for y → state (→ verify f(f⁻¹(x)) = x); *inverse value* — f⁻¹(k) = x ⇔ f(x) = k →
solve → state; *one-to-one* — axis of symmetry x = −b/2a → the restriction at the vertex → state;
*identify function* — for each relation, list the inputs; exactly one input repeats with two outputs.

---

## 10. Difficulty model

Per-task declared band ranges (§1.2) with a deterministic **structural lever** mapping onto the FULL
declared range (the ratio v1.0.2 pattern: every declared band reachable per task, gated by a
range-based coverage test), plus transparent descriptive axes computed through the shared
`round3`/`clamp01`: `numericalComplexity`, `algebraicComplexity`, `reasoningSteps`, `abstraction`,
`representation`, `requiredConnections`, and `exactVsApproximate` (always 0 — every answer is exact).

| Task | Lever (tier → band) |
| --- | --- |
| `identify_function` | 1: non-negative inputs and the repeated pairs adjacent; 2: negative inputs or separated repeated pairs |
| `evaluate_function` | kind tier (linear 0, quadratic 1, reciprocal/sqrt 2) + 1 if p < 0 or the answer is a non-integer, capped 2 → band 1 + tier |
| `solve_for_input` | linear with integer solution 2; linear with fractional solution, reciprocal, sqrt 3 |
| `domain_of_function` | polynomial 2; reciprocal h = 0 → 2, h ≠ 0 → 3; sqrt a > 0 with integer endpoint 3; sqrt a < 0 or fractional endpoint 4 |
| `range_of_function` | linear restricted 3; sqrt v = 0 → 3, v ≠ 0 → 4; reciprocal 4; quadratic a > 0 with integer vertex 4, otherwise 5 |
| `composite_value` | both linear and p ≥ 0 → 2; a quadratic or p < 0 → 3 |
| `composite_expression` | linear∘linear 3; a quadratic involved 4; quadratic outer with a negative or non-unit inner coefficient, or non-monic quadratic 5 |
| `function_from_composite` | m = 1 → 4; m ≠ 1 → 5 |
| `inverse_value` | form i integer 2; form i fractional or form ii 3; form ii with \|a\| ≥ 2 and b ≠ 0 → 4 |
| `inverse_expression` | a = ±1 → 3; otherwise 4 |
| `one_to_one_restriction` | a = 1 and b even (integer vertex) → 4; otherwise 5 |

---

## 11. Rendering, accessibility and leakage policy

No SVG in v1.0.0 (mapping diagrams and graphs are excluded, §12), so there is no visual audit or browser
verification in the review package. Prompts are content blocks: `text` + `math` (KaTeX LaTeX) as the
linear family; sets of ordered pairs and MC option displays are plain text (`{(1, 3), (2, 5), (3, 3),
(4, 8)}`). Every item carries `accessibility.spokenMath` reading the rule in words ("f of x equals the
square root of 5 minus 2x, minus 1"; "f composed with g, of 4"; "the set of ordered pairs one three, two
five, …"). Leakage: the prompt, options and spoken text never contain the canonical answer as an
explicit statement; the validator checks `no-answer-leakage` (an explicit `= <answer>` / `f^{-1}(x) =`
reveal). Coincidental numeric equality with a coefficient is not leakage (linear precedent).

---

## 12. Scope guard and exclusions

Excluded from v1.0.0 (deferred to later versions / families): drawing or reading graphs and GDC graph
windows (Oxford 2.3); mapping diagrams and the vertical-line test on a picture; rational functions of the
form (ax + b)/(cx + d) and their inverses (Oxford chapter 4); inverses of quadratics on restricted domains
(square-root answers); composites of two quadratics (degree 4) or of reciprocal/square-root rules; the
identity function as an explicit object; piecewise, absolute-value, exponential and logarithmic rules;
modelling contexts (the taxi-fare gradient/intercept item belongs to chapter 3); decimal, approximate or
calculator-dependent answers; proofs of one-to-one-ness; even/odd functions.

---

## 13. Registry, schema and manifest impact (the first post-freeze family)

1. **Controlled vocabulary (governance action):** `registry-graph.ts` `CONTROLLED_VOCABULARY.domainMap`
   gains `FUNC: "functions"`; `strands` gains `"introducing-functions"`. No existing entry changes.
2. **Objective files:** `curriculum/objectives/SPI.IBDPAASL.FUNC.json` is the twelfth file
   (`OBJECTIVE_FILES` in `objective-registry.ts` and `build-registry-reports.mjs`). The registry now
   indexes **81 objectives = 70 approved (the frozen Phase-1 set, byte-for-byte unchanged) + 11
   proposed**. The graph stays `ok` (no new referenced-undefined; the known-baseline set remains exactly
   the five); the eleven new objectives are `G1_pendingOnly` in the coverage report.
3. **Frozen Phase-1 record preserved:** `objective_registry_manifest.json` keeps `frozenObjectiveFiles`
   (the 11 approved files, unchanged digests) and gains `proposedObjectiveFiles`,
   `approvedObjectiveCount: 70`, `proposedObjectiveCount: 11`; `objectiveCount` becomes 81; reporter
   version 1.0.0 → 1.1.0; the Phase-1 `approval` block and tags are untouched. The registry reports
   (index / gap / coverage) are regenerated by the same builder; the registry tests pin the split
   explicitly (70 approved + 11 proposed) instead of a bare 70.
4. **Capability join:** `generator-capability.ts` gains `"gen.functions.foundations"` →
   `OBJECTIVE_BY_TASK` from `functions-objective-ids.ts`; `orphanedTasks` stays 0.
5. **Schema (additive):** the two `if/then` canonical-shape rules of §5; `question-item.schema.json` and
   the compiled validator change bytes, so the `schema` + `compiledValidator` digests recorded in the
   ratio, transformations and mensuration manifests are re-frozen (the ratio v1.0.0 precedent); no other
   digest in any approved manifest changes; all nine approved families' golden/parity fixtures stay
   byte-for-byte identical.
6. **SDK registry:** one `GENERATORS` entry with `approvalStatus: "pending-review"` (review-mode Studio
   only; `approvedGenerators()` excludes it; `scripts/build-samples.mjs` does not import it).

---

## 14. Review package, versioning and the owner decision

Delivered with the implementation: `oracle/golden/functions.golden.json` (golden seeds 1, 42, 123456789,
2147483647 × default interaction) and `functions.parity.json` (task-pinned, both interactions);
`docs/review/functions_review_pack.{md,json}` (every task × interaction, every declared band, every
misconception rule exemplified, parser/checker corpora, the collision/regeneration invariant);
`docs/review/functions_distribution.json` (10,000-seed task × band × kind distribution);
`docs/review/functions_manifest.json` (canonical SHA-256 of every frozen artifact; `approvalStatus:
"pending-review"`; `hiddenFromNormalStudioAndProduction: true`) with TS + Python integrity tests.

Release **v1.0.0** as pending-review. **Next owner decision: APPROVE / REVISE / REJECT** after reviewing
the pack — in particular §2 wording and prerequisites, §5 the two canonical-first answer types, §8 the
misconception formulas and feedback, §10 the band levers, and §12 the exclusions. On APPROVE: objectives
→ `approved`, registry entry → `approved`, tag `approved-functions-v1.0.0`, the family enters production
samples; any output-affecting revision ⇒ v1.0.1+ with regenerated fixtures (v1.0.0 preserved at tag
`functions-v1.0.0`). Generated items are never auto-approved or published.
