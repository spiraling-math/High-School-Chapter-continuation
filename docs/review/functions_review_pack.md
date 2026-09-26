# gen.functions.foundations v1.0.0 — Curriculum Review Pack

> **PENDING-REVIEW** (machine-validated; NOT curriculum-approved; DECISION_LOG.md #65). Generator **gen.functions.foundations v1.0.0**, validator v1.0.0. IB Mathematics: Analysis and Approaches SL — Introducing Functions (Oxford chapter 2). The eleven `SPI.IBDPAASL.FUNC.*` objectives are `reviewStatus: proposed`; the family is visible only in the Studio's review mode and excluded from production exports and samples until the owner approves it. Required coverage cells are derived from the 10,000-seed distribution report; every exemplar below carries the full per-item record and a `curriculumReviewDecision` field.

## What the owner is asked to approve

1. The eleven proposed objectives (`curriculum/objectives/SPI.IBDPAASL.FUNC.json`) and their task mapping.
2. The two new canonical-first answer contracts: `answer.type: algebraic-expression` (canonical polynomial coefficient vector in x) and `answer.type: interval` (real-subset descriptor: reals / ray / bounded / reals-except), with the ASCII-anchored checkers pinned by the cross-engine corpus.
3. The item mathematics, phrasing, difficulty bands, worked solutions, misconception rules + feedback, and the MC policy (identify_function multiple-choice only), as evidenced by the exemplars below.
4. The controlled-vocabulary extension `FUNC → functions` + strand `introducing-functions` (registry §4.6).

## Summary

- Representative exemplars: **41** · full coverage: **True** · all machine-valid: **True** · all exemplars complete: **True**.
- 10,000-seed sweep (both interaction pools): invalid items **0**; unreachable declared bands **none**.
- Expression-checker matrix: all-ok **True**; all 7 result codes reached **True**. Interval-checker matrix: all-ok **True**; all 8 result codes reached **True**.
- Misconceptions **68/68** exercised (unexercised: none).
- MC policy ok **True** (identify_function MC-only; every other task serves both interactions).

## Declared difficulty bands

| task | declared bands |
|---|---|
| identify_function | 1–2 |
| evaluate_function | 1–3 |
| solve_for_input | 2–3 |
| domain_of_function | 2–4 |
| range_of_function | 3–5 |
| composite_value | 2–3 |
| composite_expression | 3–5 |
| function_from_composite | 4–5 |
| inverse_value | 2–4 |
| inverse_expression | 3–4 |
| one_to_one_restriction | 4–5 |

## Answer-contract matrix — algebraic-expression

Canonical: `{"variable": "x", "coefficients": [{"num": 1, "den": 1}, {"num": -3, "den": 1}, {"num": 2, "den": 1}]}` (2x^2 - 3x + 1).

| case | response | expected code | actual code | ok |
|---|---|---|---|---|
| the canonical display | `2x^2 - 3x + 1` | correct | correct | True |
| reordered terms with ** power | `1 - 3x + 2x**2` | correct | correct | True |
| unexpanded factored product | `(2x - 1)(x - 1)` | correct | correct | True |
| an f(x) = prefix and spaces removed | `f(x)=2x^2-3x+1` | correct | correct | True |
| wrong variable letter | `2y^2 - 3y + 1` | wrong-variable | wrong-variable | True |
| a dropped term | `2x^2 - 3x` | wrong-coefficients | wrong-coefficients | True |
| wrong degree | `2x^3 - 3x + 1` | wrong-degree | wrong-degree | True |
| division by x is not a polynomial | `1/x + 2` | not-polynomial | not-polynomial | True |
| a known wrong form is diagnosed (square without cross term) | `2x^2 + 1` | misconception | misconception | True |
| dangling operator | `2x^2 - 3x +` | unparseable | unparseable | True |

Codes reached: correct, misconception, not-polynomial, unparseable, wrong-coefficients, wrong-degree, wrong-variable.

## Answer-contract matrix — interval

| case | canonical | response | expected code | actual code | ok |
|---|---|---|---|---|---|
| inequality form | `{"kind": "ray", "variable": "x", "endpoint": {"num": 2, "den": 1}, "inclusive": true, "direction": "ge"}` | `x >= 2` | correct | correct | True |
| interval notation | `{"kind": "ray", "variable": "x", "endpoint": {"num": 2, "den": 1}, "inclusive": true, "direction": "ge"}` | `[2, inf)` | correct | correct | True |
| reversed inequality order | `{"kind": "ray", "variable": "x", "endpoint": {"num": 2, "den": 1}, "inclusive": true, "direction": "ge"}` | `2 <= x` | correct | correct | True |
| unicode >= | `{"kind": "ray", "variable": "x", "endpoint": {"num": 2, "den": 1}, "inclusive": true, "direction": "ge"}` | `x ≥ 2` | correct | correct | True |
| range letter y for a domain | `{"kind": "ray", "variable": "x", "endpoint": {"num": 2, "den": 1}, "inclusive": true, "direction": "ge"}` | `y >= 2` | wrong-variable | wrong-variable | True |
| an exclusion instead of a ray | `{"kind": "ray", "variable": "x", "endpoint": {"num": 2, "den": 1}, "inclusive": true, "direction": "ge"}` | `x != 2` | wrong-kind | wrong-kind | True |
| wrong endpoint | `{"kind": "ray", "variable": "x", "endpoint": {"num": 2, "den": 1}, "inclusive": true, "direction": "ge"}` | `x >= 3` | wrong-endpoint | wrong-endpoint | True |
| strict instead of inclusive | `{"kind": "ray", "variable": "x", "endpoint": {"num": 2, "den": 1}, "inclusive": true, "direction": "ge"}` | `x > 2` | wrong-inclusivity | wrong-inclusivity | True |
| wrong direction without a diagnostic | `{"kind": "ray", "variable": "x", "endpoint": {"num": 2, "den": 1}, "inclusive": true, "direction": "ge"}` | `x <= 2` | wrong-direction | wrong-direction | True |
| wrong direction matching a known misconception | `{"kind": "ray", "variable": "x", "endpoint": {"num": 2, "den": 1}, "inclusive": true, "direction": "ge"}` | `x <= 2` | misconception | misconception | True |
| dangling comparison | `{"kind": "ray", "variable": "x", "endpoint": {"num": 2, "den": 1}, "inclusive": true, "direction": "ge"}` | `x >=` | unparseable | unparseable | True |
| bounded range as a chained inequality | `{"kind": "bounded", "variable": "y", "lo": {"num": -1, "den": 1}, "hi": {"num": 4, "den": 1}, "loInclusive": true, "hiInclusive": true}` | `-1 <= y <= 4` | correct | correct | True |
| bounded range in interval notation | `{"kind": "bounded", "variable": "y", "lo": {"num": -1, "den": 1}, "hi": {"num": 4, "den": 1}, "loInclusive": true, "hiInclusive": true}` | `[-1, 4]` | correct | correct | True |
| range exclusion | `{"kind": "reals-except", "variable": "y", "points": [{"num": 3, "den": 1}]}` | `y != 3` | correct | correct | True |
| all real numbers in words | `{"kind": "reals"}` | `all real numbers` | correct | correct | True |

Codes reached: correct, misconception, unparseable, wrong-direction, wrong-endpoint, wrong-inclusivity, wrong-kind, wrong-variable.

## Misconceptions exercised by task

- **identify_function** (3): MISC.FUNC.CONSTANT_REJECTED, MISC.FUNC.MANY_TO_ONE_REJECTED, MISC.FUNC.PATTERN_REQUIRED
- **evaluate_function** (12): MISC.FUNC.EVAL_CONSTANT_SIGN_FLIPPED, MISC.FUNC.EVAL_DENOMINATOR_NOT_GROUPED, MISC.FUNC.EVAL_DROP_CONSTANT, MISC.FUNC.EVAL_FORGOT_MULTIPLY, MISC.FUNC.EVAL_HALVE_INSTEAD_OF_ROOT, MISC.FUNC.EVAL_NEGATIVE_ROOT, MISC.FUNC.EVAL_RECIPROCAL_INVERTED, MISC.FUNC.EVAL_ROOT_IGNORED, MISC.FUNC.EVAL_SIGN_OF_INPUT, MISC.FUNC.EVAL_SQUARE_AS_DOUBLE, MISC.FUNC.EVAL_SQUARE_COEFFICIENT, MISC.FUNC.EVAL_SQUARE_NEGATIVE
- **solve_for_input** (9): MISC.FUNC.SOLVE_DIVIDE_BY_CONSTANT, MISC.FUNC.SOLVE_EVALUATES_INSTEAD, MISC.FUNC.SOLVE_FORGOT_TO_SQUARE, MISC.FUNC.SOLVE_IGNORES_SHIFT, MISC.FUNC.SOLVE_POLE_SIGN, MISC.FUNC.SOLVE_RECIPROCAL_NOT_INVERTED, MISC.FUNC.SOLVE_SQUARE_BEFORE_ISOLATING, MISC.FUNC.SOLVE_STOPS_BEFORE_DIVIDING, MISC.FUNC.SOLVE_WRONG_INVERSE
- **domain_of_function** (10): MISC.FUNC.DOMAIN_ALL_REALS, MISC.FUNC.DOMAIN_AS_EXCLUDED_POINT, MISC.FUNC.DOMAIN_DIRECTION_FLIPPED, MISC.FUNC.DOMAIN_ENDPOINT_SIGN, MISC.FUNC.DOMAIN_EXCLUDES_CONSTANT, MISC.FUNC.DOMAIN_EXCLUDES_ZERO, MISC.FUNC.DOMAIN_NONNEGATIVE_ONLY, MISC.FUNC.DOMAIN_POLE_AS_INEQUALITY, MISC.FUNC.DOMAIN_POLE_SIGN, MISC.FUNC.DOMAIN_STRICT_ENDPOINT
- **range_of_function** (10): MISC.FUNC.DOMAIN_RANGE_CONFUSED, MISC.FUNC.RANGE_ALL_REALS, MISC.FUNC.RANGE_DIRECTION_FLIPPED, MISC.FUNC.RANGE_IGNORES_SHIFT, MISC.FUNC.RANGE_ONLY_LOWER_BOUND, MISC.FUNC.RANGE_POLE_AS_INEQUALITY, MISC.FUNC.RANGE_STRICT_AT_BOUND, MISC.FUNC.RANGE_STRICT_ENDPOINTS, MISC.FUNC.RANGE_USES_CONSTANT_TERM, MISC.FUNC.RANGE_USES_VERTEX_X
- **composite_value** (5): MISC.FUNC.COMP_AS_PRODUCT, MISC.FUNC.COMP_AS_SUM, MISC.FUNC.COMP_INNER_ONLY, MISC.FUNC.COMP_ORDER_REVERSED, MISC.FUNC.COMP_OUTER_AT_INPUT
- **composite_expression** (4): MISC.FUNC.COMP_AS_PRODUCT, MISC.FUNC.COMP_AS_SUM, MISC.FUNC.COMP_ORDER_REVERSED, MISC.FUNC.COMP_SQUARE_NO_CROSS_TERM
- **function_from_composite** (4): MISC.FUNC.FFC_COMPOSES_INSTEAD, MISC.FUNC.FFC_IGNORES_INNER, MISC.FUNC.FFC_SCALE_NOT_INVERTED, MISC.FUNC.FFC_SHIFT_NOT_INVERTED
- **inverse_value** (6): MISC.FUNC.INVVAL_APPLIES_INVERSE_AGAIN, MISC.FUNC.INVVAL_FORWARD, MISC.FUNC.INVVAL_IDENTITY, MISC.FUNC.INVVAL_RECIPROCAL, MISC.FUNC.INV_SIGN_ERROR, MISC.FUNC.INV_UNDO_ORDER
- **inverse_expression** (5): MISC.FUNC.INV_AS_RECIPROCAL, MISC.FUNC.INV_NEGATES_ONLY, MISC.FUNC.INV_SIGN_ERROR, MISC.FUNC.INV_SWAPS_ROLES, MISC.FUNC.INV_UNDO_ORDER
- **one_to_one_restriction** (5): MISC.FUNC.RESTRICTION_ZERO, MISC.FUNC.VERTEX_X_MISSING_HALF, MISC.FUNC.VERTEX_X_SIGN, MISC.FUNC.VERTEX_X_USES_C, MISC.FUNC.VERTEX_Y_FOR_X

## MC interaction policy

| task | rule | ok | detail |
|---|---|---|---|
| identify_function | mc-only | True | identify_function rejects free-response (InteractionNotSupported) |
| evaluate_function | both-interactions | True | evaluate_function serves free-response and multiple-choice (4 options, 3 misconception-backed distractors) |
| solve_for_input | both-interactions | True | solve_for_input serves free-response and multiple-choice (4 options, 3 misconception-backed distractors) |
| domain_of_function | both-interactions | True | domain_of_function serves free-response and multiple-choice (4 options, 3 misconception-backed distractors) |
| range_of_function | both-interactions | True | range_of_function serves free-response and multiple-choice (4 options, 3 misconception-backed distractors) |
| composite_value | both-interactions | True | composite_value serves free-response and multiple-choice (4 options, 3 misconception-backed distractors) |
| composite_expression | both-interactions | True | composite_expression serves free-response and multiple-choice (4 options, 3 misconception-backed distractors) |
| function_from_composite | both-interactions | True | function_from_composite serves free-response and multiple-choice (4 options, 3 misconception-backed distractors) |
| inverse_value | both-interactions | True | inverse_value serves free-response and multiple-choice (4 options, 3 misconception-backed distractors) |
| inverse_expression | both-interactions | True | inverse_expression serves free-response and multiple-choice (4 options, 3 misconception-backed distractors) |
| one_to_one_restriction | both-interactions | True | one_to_one_restriction serves free-response and multiple-choice (4 options, 3 misconception-backed distractors) |

## Exemplars

Each exemplar is reproducible from its seed; LaTeX prompt blocks are shown between `$ … $`.

### composite_expression — seed 1 — band 3 (algebraic-expression, free-response)

| field | value |
|---|---|
| objective | SPI.IBDPAASL.FUNC.COMPOSITE_EXPRESSION.01 |
| interaction / answer | free-response / algebraic-expression |
| difficulty band | 3 (axes: {"numericalComplexity": 0.25, "algebraicComplexity": 0.75, "reasoningSteps": 0.65, "abstraction": 0.65, "representation": 0.45, "requiredConnections": 0.5, "exactVsApproximate": 0}) |
| prompt | Find the composite: The functions f and g are defined by $ f(x) = 5x + 6, \qquad g(x) = -3x + 1 $ Find an expression for $ (g \circ f)(x) $ Expand and simplify your answer. |
| spoken math | The functions f and g are defined by f(x) = 5x + 6 and g(x) = -3x + 1. Find an expression for (g o f)(x), that is g of f of x. Expand and simplify your answer. |
| params | `{"task": "composite_expression", "f": {"kind": "linear", "a": {"num": 5, "den": 1}, "b": {"num": 6, "den": 1}}, "g": {"kind": "linear", "a": {"num": -3, "den": 1}, "b": {"num": 1, "den": 1}}, "order": "gf"}` |
| canonical answer | `{"variable": "x", "coefficients": [{"num": -17, "den": 1}, {"num": -15, "den": 1}]}` |
| answer display | -15x - 17 |
| accepted form / checker | Algebraic-expression checker (ASCII-anchored recursive-descent parser, exact rationals): any equivalent written form of the polynomial in x is accepted — reordered terms, unexpanded brackets and products, `^` or `**`, implicit multiplication, fractional coefficients as a/b or exact decimals, an optional `f(x) =` / `(f o g)(x) =` / `y =` prefix. Result codes: correct, wrong-variable, not-polynomial (division by x), wrong-degree, wrong-coefficients, misconception (a known wrong form), unparseable. |
| worked solution | 1. Substitute f(x) into g -> g(f(x)) = -3(5x + 6) + 1; 2. Expand and collect like terms -> = -15x - 17; 3. State the composite -> (g o f)(x) = -15x - 17 |
| validation checks | 13/13 pass |
| covers cells | `answerType:algebraic-expression`, `band:composite_expression:3`, `interaction:composite_expression:free-response`, `kind:composite_expression:linear/linear:gf`, `task:composite_expression` |
| reproduction | `python -c "import sys; sys.path.insert(0,'oracle/spi_oracle'); import functions as G; print(G.serialize(G.generate(1, {'task': 'composite_expression', 'interactionType': 'free-response'})))"` |
| curriculum-review decision | ☐ APPROVE ☐ REVISE ☐ REJECT |

### inverse_value — seed 2 — band 2 (integer, free-response)

| field | value |
|---|---|
| objective | SPI.IBDPAASL.FUNC.INVERSE_VALUE.01 |
| interaction / answer | free-response / integer |
| difficulty band | 2 (axes: {"numericalComplexity": 0.25, "algebraicComplexity": 0.5, "reasoningSteps": 0.5, "abstraction": 0.6, "representation": 0.4, "requiredConnections": 0.5, "exactVsApproximate": 0}) |
| prompt | Evaluate the inverse: The function f is defined by $ f(x) = x + 5 $ Find the value of $ f^{-1}(7) $ |
| spoken math | The function f is defined by f(x) = x + 5. Find the value of f inverse of 7. |
| params | `{"task": "inverse_value", "name": "f", "a": {"num": 1, "den": 1}, "b": {"num": 5, "den": 1}, "form": "inverse_at", "k": {"num": 7, "den": 1}}` |
| canonical answer | `{"num": 2, "den": 1}` |
| answer display | 2 |
| accepted form / checker | Exact-rational checker: the exact reduced fraction num/den is the answer; any equivalent fraction is accepted; a decimal is accepted only when it terminates (accepts.decimal=true); mixed numbers are not accepted; no tolerance; integer when den = 1. |
| worked solution | 1. Let f^-1(7) = x, so f(x) = 7 -> x + 5 = 7; 2. Solve for x -> x = 2; 3. State the value -> f^-1(7) = 2 |
| validation checks | 12/12 pass |
| covers cells | `answerType:integer`, `band:inverse_value:2`, `interaction:inverse_value:free-response`, `kind:inverse_value:inverse_at`, `task:inverse_value` |
| reproduction | `python -c "import sys; sys.path.insert(0,'oracle/spi_oracle'); import functions as G; print(G.serialize(G.generate(2, {'task': 'inverse_value', 'interactionType': 'free-response'})))"` |
| curriculum-review decision | ☐ APPROVE ☐ REVISE ☐ REJECT |

### identify_function — seed 7 — band 2 (multiple-choice, multiple-choice)

| field | value |
|---|---|
| objective | SPI.IBDPAASL.FUNC.IDENTIFY_FUNCTION.01 |
| interaction / answer | multiple-choice / multiple-choice |
| difficulty band | 2 (axes: {"numericalComplexity": 0.45, "algebraicComplexity": 0.3, "reasoningSteps": 0.45, "abstraction": 0.7, "representation": 0.6, "requiredConnections": 0.3, "exactVsApproximate": 0}) |
| prompt | Identify: Exactly one of the following relations is not a function. Which one? |
| spoken math | Exactly one of the following relations is not a function. Which one? Option A: the ordered pairs (1, -5); (2, -5); (5, -5); (7, -5). Option B: the ordered pairs (1, -2); (7, -2); (5, 9); (3, -2). Option C: the ordered pairs (9, -6); (5, -4); (6, -1); (8, 0). Option D: the ordered pairs (9, 1); (6, -3); (5, 2); (6, 5). |
| params | `{"task": "identify_function", "nonFunction": [[9, 1], [6, -3], [5, 2], [6, 5]], "functions": [{"pairs": [[1, -2], [7, -2], [5, 9], [3, -2]], "misconceptionId": "MISC.FUNC.MANY_TO_ONE_REJECTED"}, {"pairs": [[1, -5], [2, -5], [5, -5], [7, -5]], "misconceptionId": "MISC.FUNC.CONSTANT_REJECTED"}, {"pairs": [[9, -6], [5, -4], [6, -1], [8, 0]], "misconceptionId": "MISC.FUNC.PATTERN_REQUIRED"}], "negativeInputs": false, "separatedRepeat": true}` |
| canonical answer | `"D"` |
| answer display | D |
| accepted form / checker | Choice checker: the selected option letter is the answer; exactly one of the four relations has an input paired with two different outputs. The three distractors are structurally distinct functions (many-to-one, constant, pattern-free) so each wrong choice diagnoses a named belief. |
| worked solution | 1. List the inputs of each relation; 2. Find the relation with a repeated input and two different outputs -> Relation D: the input 6 is paired with both -3 and 5; 3. State the relation that is not a function -> D |
| MC options | A={(1, -5), (2, -5), (5, -5), (7, -5)}; B={(1, -2), (7, -2), (5, 9), (3, -2)}; C={(9, -6), (5, -4), (6, -1), (8, 0)}; D={(9, 1), (6, -3), (5, 2), (6, 5)} ✓ |
| distractor feedback | MISC.FUNC.MANY_TO_ONE_REJECTED ({(1, -2), (7, -2), (5, 9), (3, -2)}): Two different inputs may share the same output. A relation fails to be a function only when ONE input has two different outputs.; MISC.FUNC.CONSTANT_REJECTED ({(1, -5), (2, -5), (5, -5), (7, -5)}): A constant relation sends every input to the same output; each input still has exactly one output, so it is a function.; MISC.FUNC.PATTERN_REQUIRED ({(9, -6), (5, -4), (6, -1), (8, 0)}): A function does not need a formula or a visible pattern. Check only that no input appears twice with different outputs. |
| validation checks | 17/17 pass |
| covers cells | `answerType:multiple-choice`, `band:identify_function:2`, `interaction:identify_function:multiple-choice`, `kind:identify_function:-`, `task:identify_function` |
| reproduction | `python -c "import sys; sys.path.insert(0,'oracle/spi_oracle'); import functions as G; print(G.serialize(G.generate(7, {'task': 'identify_function', 'interactionType': 'multiple-choice'})))"` |
| curriculum-review decision | ☐ APPROVE ☐ REVISE ☐ REJECT |

### evaluate_function — seed 8 — band 3 (exact-rational, free-response)

| field | value |
|---|---|
| objective | SPI.IBDPAASL.FUNC.EVALUATE.01 |
| interaction / answer | free-response / exact-rational |
| difficulty band | 3 (axes: {"numericalComplexity": 0.45, "algebraicComplexity": 0.5, "reasoningSteps": 0.5, "abstraction": 0.45, "representation": 0.4, "requiredConnections": 0.3, "exactVsApproximate": 0}) |
| prompt | Evaluate: The function f is defined by $ f(x) = \frac{2}{x + 1} + 3 $ Find the value of f(3). |
| spoken math | The function f is defined by f(x) = 2/(x + 1) + 3. Find the value of f(3). |
| params | `{"task": "evaluate_function", "name": "f", "rule": {"kind": "reciprocal", "k": {"num": 2, "den": 1}, "h": {"num": -1, "den": 1}, "v": {"num": 3, "den": 1}}, "p": {"num": 3, "den": 1}}` |
| canonical answer | `{"num": 7, "den": 2}` |
| answer display | 7/2 |
| accepted form / checker | Exact-rational checker: the exact reduced fraction num/den is the answer; any equivalent fraction is accepted; a decimal is accepted only when it terminates (accepts.decimal=true); mixed numbers are not accepted; no tolerance; integer when den = 1. |
| worked solution | 1. Substitute x = 3 into the rule -> f(3) = 2/(3 + 1) + 3; 2. Evaluate the denominator, then divide -> = 2/4 + 3; 3. State the value -> f(3) = 7/2 |
| validation checks | 12/12 pass |
| covers cells | `answerType:exact-rational`, `band:evaluate_function:3`, `interaction:evaluate_function:free-response`, `kind:evaluate_function:reciprocal`, `task:evaluate_function` |
| reproduction | `python -c "import sys; sys.path.insert(0,'oracle/spi_oracle'); import functions as G; print(G.serialize(G.generate(8, {'task': 'evaluate_function', 'interactionType': 'free-response'})))"` |
| curriculum-review decision | ☐ APPROVE ☐ REVISE ☐ REJECT |

### domain_of_function — seed 12 — band 3 (interval, free-response)

| field | value |
|---|---|
| objective | SPI.IBDPAASL.FUNC.DOMAIN.01 |
| interaction / answer | free-response / interval |
| difficulty band | 3 (axes: {"numericalComplexity": 0.35, "algebraicComplexity": 0.5, "reasoningSteps": 0.55, "abstraction": 0.7, "representation": 0.65, "requiredConnections": 0.4, "exactVsApproximate": 0}) |
| prompt | State the domain: The function g is defined by $ g(x) = \sqrt{5x - 5} - 3 $ State the largest possible domain of g. |
| spoken math | The function g is defined by g(x) = sqrt(5x - 5) - 3. State the largest possible domain of g. |
| params | `{"task": "domain_of_function", "name": "g", "rule": {"kind": "sqrt", "a": {"num": 5, "den": 1}, "b": {"num": -5, "den": 1}, "v": {"num": -3, "den": 1}}}` |
| canonical answer | `{"kind": "ray", "variable": "x", "endpoint": {"num": 1, "den": 1}, "inclusive": true, "direction": "ge"}` |
| answer display | x >= 1 |
| accepted form / checker | Interval checker (ASCII-anchored, exact rationals): inequality notation (`x >= 2`, `2 <= x`), interval notation (`[2, inf)`), set-builder, the words `all real numbers`, exclusions (`x != 3`), unicode ≥ ≤ ≠ ∞ ℝ and `infinity`/`oo` are accepted. A domain is stated in x and a range in y (also f(x)/g(x)); the letter is checked (wrong-variable). Result codes: correct, wrong-variable, wrong-kind, wrong-endpoint, wrong-inclusivity, wrong-direction, misconception, unparseable. |
| worked solution | 1. Identify the restriction -> 5x - 5 >= 0; 2. Solve the inequality -> x >= 1; 3. State the domain -> x >= 1 |
| validation checks | 12/12 pass |
| covers cells | `answerType:interval`, `band:domain_of_function:3`, `interaction:domain_of_function:free-response`, `kind:domain_of_function:sqrt`, `task:domain_of_function` |
| reproduction | `python -c "import sys; sys.path.insert(0,'oracle/spi_oracle'); import functions as G; print(G.serialize(G.generate(12, {'task': 'domain_of_function', 'interactionType': 'free-response'})))"` |
| curriculum-review decision | ☐ APPROVE ☐ REVISE ☐ REJECT |

### function_from_composite — seed 3 — band 4 (algebraic-expression, free-response)

| field | value |
|---|---|
| objective | SPI.IBDPAASL.FUNC.FUNCTION_FROM_COMPOSITE.01 |
| interaction / answer | free-response / algebraic-expression |
| difficulty band | 4 (axes: {"numericalComplexity": 0.25, "algebraicComplexity": 0.85, "reasoningSteps": 0.8, "abstraction": 0.85, "representation": 0.5, "requiredConnections": 0.7, "exactVsApproximate": 0}) |
| prompt | Find the outer function: The functions f and g are defined by $ g(x) = x + 4, \qquad (f \circ g)(x) = -5x - 21 $ Find an expression for f(x). |
| spoken math | The functions f and g are defined by g(x) = x + 4 and (f o g)(x) = -5x - 21. Find an expression for f(x). |
| params | `{"task": "function_from_composite", "A": {"num": -5, "den": 1}, "B": {"num": -1, "den": 1}, "m": {"num": 1, "den": 1}, "c": {"num": 4, "den": 1}}` |
| canonical answer | `{"variable": "x", "coefficients": [{"num": -1, "den": 1}, {"num": -5, "den": 1}]}` |
| answer display | -5x - 1 |
| accepted form / checker | Algebraic-expression checker (ASCII-anchored recursive-descent parser, exact rationals): any equivalent written form of the polynomial in x is accepted — reordered terms, unexpanded brackets and products, `^` or `**`, implicit multiplication, fractional coefficients as a/b or exact decimals, an optional `f(x) =` / `(f o g)(x) =` / `y =` prefix. Result codes: correct, wrong-variable, not-polynomial (division by x), wrong-degree, wrong-coefficients, misconception (a known wrong form), unparseable. |
| worked solution | 1. Write f(g(x)) equal to the given composite -> f(x + 4) = -5x - 21; 2. Let u = g(x) and express x in terms of u -> x = u - 4; 3. Substitute and simplify -> f(u) = -5u - 1; 4. State the outer function -> f(x) = -5x - 1 |
| validation checks | 12/12 pass |
| covers cells | `band:function_from_composite:4`, `interaction:function_from_composite:free-response`, `kind:function_from_composite:-`, `task:function_from_composite` |
| reproduction | `python -c "import sys; sys.path.insert(0,'oracle/spi_oracle'); import functions as G; print(G.serialize(G.generate(3, {'task': 'function_from_composite', 'interactionType': 'free-response'})))"` |
| curriculum-review decision | ☐ APPROVE ☐ REVISE ☐ REJECT |

### one_to_one_restriction — seed 4 — band 4 (integer, free-response)

| field | value |
|---|---|
| objective | SPI.IBDPAASL.FUNC.ONE_TO_ONE_RESTRICTION.01 |
| interaction / answer | free-response / integer |
| difficulty band | 4 (axes: {"numericalComplexity": 0.25, "algebraicComplexity": 0.6, "reasoningSteps": 0.7, "abstraction": 0.85, "representation": 0.55, "requiredConnections": 0.8, "exactVsApproximate": 0}) |
| prompt | Find the restriction: The function f is defined by $ f(x) = x^{2} - 6x - 3, \quad x \leq k $ The domain of f is restricted so that the inverse function f^-1 exists. Find the greatest possible value of k. |
| spoken math | The function f is defined by f(x) = x^2 - 6x - 3, for x <= k. The domain of f is restricted so that the inverse function f^-1 exists. Find the greatest possible value of k. |
| params | `{"task": "one_to_one_restriction", "name": "f", "rule": {"kind": "quadratic", "a": {"num": 1, "den": 1}, "b": {"num": -6, "den": 1}, "c": {"num": -3, "den": 1}}, "side": "le"}` |
| canonical answer | `{"num": 3, "den": 1}` |
| answer display | 3 |
| accepted form / checker | Exact-rational checker: the exact reduced fraction num/den is the answer; any equivalent fraction is accepted; a decimal is accepted only when it terminates (accepts.decimal=true); mixed numbers are not accepted; no tolerance; integer when den = 1. |
| worked solution | 1. Find the axis of symmetry -> x = -(-6)/(2(1)) = 3; 2. Restrict the domain at the vertex; 3. State the value of k -> k = 3 |
| validation checks | 12/12 pass |
| covers cells | `band:one_to_one_restriction:4`, `interaction:one_to_one_restriction:free-response`, `kind:one_to_one_restriction:quadratic`, `task:one_to_one_restriction` |
| reproduction | `python -c "import sys; sys.path.insert(0,'oracle/spi_oracle'); import functions as G; print(G.serialize(G.generate(4, {'task': 'one_to_one_restriction', 'interactionType': 'free-response'})))"` |
| curriculum-review decision | ☐ APPROVE ☐ REVISE ☐ REJECT |

### composite_value — seed 6 — band 3 (integer, free-response)

| field | value |
|---|---|
| objective | SPI.IBDPAASL.FUNC.COMPOSITE_VALUE.01 |
| interaction / answer | free-response / integer |
| difficulty band | 3 (axes: {"numericalComplexity": 0.45, "algebraicComplexity": 0.6, "reasoningSteps": 0.65, "abstraction": 0.7, "representation": 0.55, "requiredConnections": 0.6, "exactVsApproximate": 0}) |
| prompt | Evaluate: The functions f and g are defined by $ f(x) = -3x + 1, \qquad g(x) = x^{2} - 3x + 5 $ Find the value of $ (g \circ f)(-3) $ |
| spoken math | The functions f and g are defined by f(x) = -3x + 1 and g(x) = x^2 - 3x + 5. Find the value of (g o f)(-3), that is g of f of -3. |
| params | `{"task": "composite_value", "f": {"kind": "linear", "a": {"num": -3, "den": 1}, "b": {"num": 1, "den": 1}}, "g": {"kind": "quadratic", "a": {"num": 1, "den": 1}, "b": {"num": -3, "den": 1}, "c": {"num": 5, "den": 1}}, "order": "gf", "p": {"num": -3, "den": 1}}` |
| canonical answer | `{"num": 75, "den": 1}` |
| answer display | 75 |
| accepted form / checker | Exact-rational checker: the exact reduced fraction num/den is the answer; any equivalent fraction is accepted; a decimal is accepted only when it terminates (accepts.decimal=true); mixed numbers are not accepted; no tolerance; integer when den = 1. |
| worked solution | 1. Evaluate the inner function f at -3 -> f(-3) = 10; 2. Evaluate the outer function g at 10 -> g(10) = 75; 3. State the value -> (g o f)(-3) = 75 |
| validation checks | 12/12 pass |
| covers cells | `band:composite_value:3`, `interaction:composite_value:free-response`, `kind:composite_value:linear/quadratic:gf`, `task:composite_value` |
| reproduction | `python -c "import sys; sys.path.insert(0,'oracle/spi_oracle'); import functions as G; print(G.serialize(G.generate(6, {'task': 'composite_value', 'interactionType': 'free-response'})))"` |
| curriculum-review decision | ☐ APPROVE ☐ REVISE ☐ REJECT |

### solve_for_input — seed 9 — band 3 (integer, free-response)

| field | value |
|---|---|
| objective | SPI.IBDPAASL.FUNC.SOLVE_FOR_INPUT.01 |
| interaction / answer | free-response / integer |
| difficulty band | 3 (axes: {"numericalComplexity": 0.45, "algebraicComplexity": 0.7, "reasoningSteps": 0.7, "abstraction": 0.55, "representation": 0.45, "requiredConnections": 0.5, "exactVsApproximate": 0}) |
| prompt | Solve: The function f is defined by $ f(x) = \sqrt{2x + 19} - 2 $ Find the value of x for which f(x) = 3. |
| spoken math | The function f is defined by f(x) = sqrt(2x + 19) - 2. Find the value of x for which f(x) = 3. |
| params | `{"task": "solve_for_input", "name": "f", "rule": {"kind": "sqrt", "a": {"num": 2, "den": 1}, "b": {"num": 19, "den": 1}, "v": {"num": -2, "den": 1}}, "target": {"num": 3, "den": 1}, "x0": {"num": 3, "den": 1}}` |
| canonical answer | `{"num": 3, "den": 1}` |
| answer display | 3 |
| accepted form / checker | Exact-rational checker: the exact reduced fraction num/den is the answer; any equivalent fraction is accepted; a decimal is accepted only when it terminates (accepts.decimal=true); mixed numbers are not accepted; no tolerance; integer when den = 1. |
| worked solution | 1. Set up the equation -> sqrt(2x + 19) - 2 = 3; 2. Add 2 to both sides to isolate the root -> sqrt(2x + 19) = 5; 3. Square both sides -> 2x + 19 = 25; 4. Solve the linear equation -> x = 3; 5. State the solution -> x = 3; 6. Verify by substitution -> f(3) = 3 |
| validation checks | 12/12 pass |
| covers cells | `band:solve_for_input:3`, `interaction:solve_for_input:free-response`, `kind:solve_for_input:sqrt`, `task:solve_for_input` |
| reproduction | `python -c "import sys; sys.path.insert(0,'oracle/spi_oracle'); import functions as G; print(G.serialize(G.generate(9, {'task': 'solve_for_input', 'interactionType': 'free-response'})))"` |
| curriculum-review decision | ☐ APPROVE ☐ REVISE ☐ REJECT |

### range_of_function — seed 14 — band 4 (interval, free-response)

| field | value |
|---|---|
| objective | SPI.IBDPAASL.FUNC.RANGE.01 |
| interaction / answer | free-response / interval |
| difficulty band | 4 (axes: {"numericalComplexity": 0.35, "algebraicComplexity": 0.65, "reasoningSteps": 0.7, "abstraction": 0.8, "representation": 0.7, "requiredConnections": 0.6, "exactVsApproximate": 0}) |
| prompt | State the range: The function g is defined by $ g(x) = \sqrt{-4 - 2x} - 1 $ State the range of g. |
| spoken math | The function g is defined by g(x) = sqrt(-4 - 2x) - 1. State the range of g. |
| params | `{"task": "range_of_function", "name": "g", "rule": {"kind": "sqrt", "a": {"num": -2, "den": 1}, "b": {"num": -4, "den": 1}, "v": {"num": -1, "den": 1}}}` |
| canonical answer | `{"kind": "ray", "variable": "y", "endpoint": {"num": -1, "den": 1}, "inclusive": true, "direction": "ge"}` |
| answer display | y >= -1 |
| accepted form / checker | Interval checker (ASCII-anchored, exact rationals): inequality notation (`x >= 2`, `2 <= x`), interval notation (`[2, inf)`), set-builder, the words `all real numbers`, exclusions (`x != 3`), unicode ≥ ≤ ≠ ∞ ℝ and `infinity`/`oo` are accepted. A domain is stated in x and a range in y (also f(x)/g(x)); the letter is checked (wrong-variable). Result codes: correct, wrong-variable, wrong-kind, wrong-endpoint, wrong-inclusivity, wrong-direction, misconception, unparseable. |
| worked solution | 1. Start from the base range -> sqrt(-4 - 2x) >= 0; 2. Apply the vertical shift -> g(x) >= -1; 3. State the range -> y >= -1 |
| validation checks | 12/12 pass |
| covers cells | `band:range_of_function:4`, `interaction:range_of_function:free-response`, `kind:range_of_function:sqrt`, `task:range_of_function` |
| reproduction | `python -c "import sys; sys.path.insert(0,'oracle/spi_oracle'); import functions as G; print(G.serialize(G.generate(14, {'task': 'range_of_function', 'interactionType': 'free-response'})))"` |
| curriculum-review decision | ☐ APPROVE ☐ REVISE ☐ REJECT |

### inverse_expression — seed 30 — band 4 (algebraic-expression, free-response)

| field | value |
|---|---|
| objective | SPI.IBDPAASL.FUNC.INVERSE_EXPRESSION.01 |
| interaction / answer | free-response / algebraic-expression |
| difficulty band | 4 (axes: {"numericalComplexity": 0.45, "algebraicComplexity": 0.9, "reasoningSteps": 0.85, "abstraction": 0.9, "representation": 0.65, "requiredConnections": 0.75, "exactVsApproximate": 0}) |
| prompt | Find the inverse: The function h is defined by $ h(x) = -4x - 4 $ Find an expression for $ h^{-1}(x) $ |
| spoken math | The function h is defined by h(x) = -4x - 4. Find an expression for h inverse of x. |
| params | `{"task": "inverse_expression", "name": "h", "a": {"num": -4, "den": 1}, "b": {"num": -4, "den": 1}}` |
| canonical answer | `{"variable": "x", "coefficients": [{"num": -1, "den": 1}, {"num": -1, "den": 4}]}` |
| answer display | (-1/4)x - 1 |
| accepted form / checker | Algebraic-expression checker (ASCII-anchored recursive-descent parser, exact rationals): any equivalent written form of the polynomial in x is accepted — reordered terms, unexpanded brackets and products, `^` or `**`, implicit multiplication, fractional coefficients as a/b or exact decimals, an optional `f(x) =` / `(f o g)(x) =` / `y =` prefix. Result codes: correct, wrong-variable, not-polynomial (division by x), wrong-degree, wrong-coefficients, misconception (a known wrong form), unparseable. |
| worked solution | 1. Write y = h(x) -> y = -4x - 4; 2. Swap x and y -> x = -4y - 4; 3. Solve for y -> y = (-1/4)x - 1; 4. State the inverse function -> h^-1(x) = (-1/4)x - 1; 5. Verify -> h((-1/4)x - 1) = x |
| validation checks | 12/12 pass |
| covers cells | `band:inverse_expression:4`, `interaction:inverse_expression:free-response`, `kind:inverse_expression:-`, `task:inverse_expression` |
| reproduction | `python -c "import sys; sys.path.insert(0,'oracle/spi_oracle'); import functions as G; print(G.serialize(G.generate(30, {'task': 'inverse_expression', 'interactionType': 'free-response'})))"` |
| curriculum-review decision | ☐ APPROVE ☐ REVISE ☐ REJECT |

### evaluate_function — seed 1 — band 1 (integer, multiple-choice)

| field | value |
|---|---|
| objective | SPI.IBDPAASL.FUNC.EVALUATE.01 |
| interaction / answer | multiple-choice / integer |
| difficulty band | 1 (axes: {"numericalComplexity": 0.25, "algebraicComplexity": 0.3, "reasoningSteps": 0.3, "abstraction": 0.25, "representation": 0.2, "requiredConnections": 0.1, "exactVsApproximate": 0}) |
| prompt | Evaluate: The function f is defined by $ f(x) = -5x - 2 $ Find the value of f(0). |
| spoken math | The function f is defined by f(x) = -5x - 2. Find the value of f(0). |
| params | `{"task": "evaluate_function", "name": "f", "rule": {"kind": "linear", "a": {"num": -5, "den": 1}, "b": {"num": -2, "den": 1}}, "p": {"num": 0, "den": 1}}` |
| canonical answer | `{"num": -2, "den": 1}` |
| answer display | -2 |
| accepted form / checker | Exact-rational checker: the exact reduced fraction num/den is the answer; any equivalent fraction is accepted; a decimal is accepted only when it terminates (accepts.decimal=true); mixed numbers are not accepted; no tolerance; integer when den = 1. |
| worked solution | 1. Substitute x = 0 into the rule -> f(0) = -5(0) - 2; 2. Multiply, then add the constant -> = 0 - 2; 3. State the value -> f(0) = -2 |
| MC options | A=2; B=0; C=-2 ✓; D=-7 |
| distractor feedback | MISC.FUNC.EVAL_FORGOT_MULTIPLY (-7): -5x means -5 multiplied by x, so substitute x = 0 and multiply: -5 × (0).; MISC.FUNC.EVAL_DROP_CONSTANT (0): After multiplying, remember the constant term -2.; MISC.FUNC.EVAL_CONSTANT_SIGN_FLIPPED (2): Keep the sign of the constant term exactly as it appears in the rule. |
| validation checks | 35/35 pass |
| covers cells | `band:evaluate_function:1`, `interaction:evaluate_function:multiple-choice`, `kind:evaluate_function:linear` |
| reproduction | `python -c "import sys; sys.path.insert(0,'oracle/spi_oracle'); import functions as G; print(G.serialize(G.generate(1, {'task': 'evaluate_function', 'interactionType': 'multiple-choice'})))"` |
| curriculum-review decision | ☐ APPROVE ☐ REVISE ☐ REJECT |

### solve_for_input — seed 7 — band 2 (integer, multiple-choice)

| field | value |
|---|---|
| objective | SPI.IBDPAASL.FUNC.SOLVE_FOR_INPUT.01 |
| interaction / answer | multiple-choice / integer |
| difficulty band | 2 (axes: {"numericalComplexity": 0.25, "algebraicComplexity": 0.5, "reasoningSteps": 0.5, "abstraction": 0.35, "representation": 0.25, "requiredConnections": 0.3, "exactVsApproximate": 0}) |
| prompt | Solve: The function g is defined by $ g(x) = -4x + 5 $ Find the value of x for which g(x) = 21. |
| spoken math | The function g is defined by g(x) = -4x + 5. Find the value of x for which g(x) = 21. |
| params | `{"task": "solve_for_input", "name": "g", "rule": {"kind": "linear", "a": {"num": -4, "den": 1}, "b": {"num": 5, "den": 1}}, "target": {"num": 21, "den": 1}, "x0": {"num": -4, "den": 1}}` |
| canonical answer | `{"num": -4, "den": 1}` |
| answer display | -4 |
| accepted form / checker | Exact-rational checker: the exact reduced fraction num/den is the answer; any equivalent fraction is accepted; a decimal is accepted only when it terminates (accepts.decimal=true); mixed numbers are not accepted; no tolerance; integer when den = 1. |
| worked solution | 1. Set up the equation -> -4x + 5 = 21; 2. Subtract 5 from both sides -> -4x = 16; 3. Divide both sides by -4 -> x = -4; 4. State the solution -> x = -4; 5. Verify by substitution -> g(-4) = 21 |
| MC options | A=-13/2; B=16; C=-79; D=-4 ✓ |
| distractor feedback | MISC.FUNC.SOLVE_EVALUATES_INSTEAD (-79): g(x) = 21 asks for the INPUT x whose output is 21; do not substitute 21 into the rule.; MISC.FUNC.SOLVE_WRONG_INVERSE (-13/2): Undo the constant with the inverse operation: a constant that is added must be subtracted from both sides (and vice versa).; MISC.FUNC.SOLVE_STOPS_BEFORE_DIVIDING (16): After isolating the x term, divide both sides by the coefficient -4. |
| validation checks | 35/35 pass |
| covers cells | `band:solve_for_input:2`, `interaction:solve_for_input:multiple-choice`, `kind:solve_for_input:linear` |
| reproduction | `python -c "import sys; sys.path.insert(0,'oracle/spi_oracle'); import functions as G; print(G.serialize(G.generate(7, {'task': 'solve_for_input', 'interactionType': 'multiple-choice'})))"` |
| curriculum-review decision | ☐ APPROVE ☐ REVISE ☐ REJECT |

### domain_of_function — seed 2 — band 2 (interval, multiple-choice)

| field | value |
|---|---|
| objective | SPI.IBDPAASL.FUNC.DOMAIN.01 |
| interaction / answer | multiple-choice / interval |
| difficulty band | 2 (axes: {"numericalComplexity": 0.25, "algebraicComplexity": 0.4, "reasoningSteps": 0.45, "abstraction": 0.6, "representation": 0.55, "requiredConnections": 0.3, "exactVsApproximate": 0}) |
| prompt | State the domain: The function f is defined by $ f(x) = -3x + 1 $ State the largest possible domain of f. |
| spoken math | The function f is defined by f(x) = -3x + 1. State the largest possible domain of f. |
| params | `{"task": "domain_of_function", "name": "f", "rule": {"kind": "linear", "a": {"num": -3, "den": 1}, "b": {"num": 1, "den": 1}}}` |
| canonical answer | `{"kind": "reals"}` |
| answer display | all real numbers |
| accepted form / checker | Interval checker (ASCII-anchored, exact rationals): inequality notation (`x >= 2`, `2 <= x`), interval notation (`[2, inf)`), set-builder, the words `all real numbers`, exclusions (`x != 3`), unicode ≥ ≤ ≠ ∞ ℝ and `infinity`/`oo` are accepted. A domain is stated in x and a range in y (also f(x)/g(x)); the letter is checked (wrong-variable). Result codes: correct, wrong-variable, wrong-kind, wrong-endpoint, wrong-inclusivity, wrong-direction, misconception, unparseable. |
| worked solution | 1. Identify the restriction -> none; 2. State the domain -> all real numbers |
| MC options | A=x != 0; B=all real numbers ✓; C=x >= 0; D=x != 1 |
| distractor feedback | MISC.FUNC.DOMAIN_NONNEGATIVE_ONLY (x >= 0): Negative inputs are allowed: a polynomial can be evaluated at any real number.; MISC.FUNC.DOMAIN_EXCLUDES_CONSTANT (x != 1): The constant term of a polynomial does not restrict the inputs; every real number is allowed.; MISC.FUNC.DOMAIN_EXCLUDES_ZERO (x != 0): A polynomial rule is defined for every real number, including 0. |
| validation checks | 35/35 pass |
| covers cells | `band:domain_of_function:2`, `interaction:domain_of_function:multiple-choice`, `kind:domain_of_function:linear` |
| reproduction | `python -c "import sys; sys.path.insert(0,'oracle/spi_oracle'); import functions as G; print(G.serialize(G.generate(2, {'task': 'domain_of_function', 'interactionType': 'multiple-choice'})))"` |
| curriculum-review decision | ☐ APPROVE ☐ REVISE ☐ REJECT |

### range_of_function — seed 4 — band 3 (interval, multiple-choice)

| field | value |
|---|---|
| objective | SPI.IBDPAASL.FUNC.RANGE.01 |
| interaction / answer | multiple-choice / interval |
| difficulty band | 3 (axes: {"numericalComplexity": 0.25, "algebraicComplexity": 0.55, "reasoningSteps": 0.6, "abstraction": 0.7, "representation": 0.6, "requiredConnections": 0.5, "exactVsApproximate": 0}) |
| prompt | State the range: The function f is defined by $ f(x) = -3x - 5, \quad -3 \leq x \leq 2 $ State the range of f. |
| spoken math | The function f is defined by f(x) = -3x - 5, for -3 <= x <= 2. State the range of f. |
| params | `{"task": "range_of_function", "name": "f", "rule": {"kind": "linear", "a": {"num": -3, "den": 1}, "b": {"num": -5, "den": 1}}, "restricted": {"p": {"num": -3, "den": 1}, "q": {"num": 2, "den": 1}}}` |
| canonical answer | `{"kind": "bounded", "variable": "y", "lo": {"num": -11, "den": 1}, "hi": {"num": 4, "den": 1}, "loInclusive": true, "hiInclusive": true}` |
| answer display | -11 <= y <= 4 |
| accepted form / checker | Interval checker (ASCII-anchored, exact rationals): inequality notation (`x >= 2`, `2 <= x`), interval notation (`[2, inf)`), set-builder, the words `all real numbers`, exclusions (`x != 3`), unicode ≥ ≤ ≠ ∞ ℝ and `infinity`/`oo` are accepted. A domain is stated in x and a range in y (also f(x)/g(x)); the letter is checked (wrong-variable). Result codes: correct, wrong-variable, wrong-kind, wrong-endpoint, wrong-inclusivity, wrong-direction, misconception, unparseable. |
| worked solution | 1. Evaluate at the endpoints of the domain -> f(-3) = 4, f(2) = -11; 2. Order the images -> -11 <= y <= 4; 3. State the range -> -11 <= y <= 4 |
| MC options | A=-11 <= y <= 4 ✓; B=y >= -11; C=-3 <= y <= 2; D=-11 < y < 4 |
| distractor feedback | MISC.FUNC.DOMAIN_RANGE_CONFUSED (-3 <= y <= 2): The range is the set of OUTPUT values (y), not the set of allowed inputs (x).; MISC.FUNC.RANGE_ONLY_LOWER_BOUND (y >= -11): On a closed restricted domain the outputs are bounded on BOTH sides: evaluate the rule at both endpoints.; MISC.FUNC.RANGE_STRICT_ENDPOINTS (-11 < y < 4): The domain includes its endpoints, so their images are attained: use <= at both ends. |
| validation checks | 35/35 pass |
| covers cells | `band:range_of_function:3`, `interaction:range_of_function:multiple-choice`, `kind:range_of_function:linear_restricted` |
| reproduction | `python -c "import sys; sys.path.insert(0,'oracle/spi_oracle'); import functions as G; print(G.serialize(G.generate(4, {'task': 'range_of_function', 'interactionType': 'multiple-choice'})))"` |
| curriculum-review decision | ☐ APPROVE ☐ REVISE ☐ REJECT |

### composite_value — seed 12 — band 2 (integer, multiple-choice)

| field | value |
|---|---|
| objective | SPI.IBDPAASL.FUNC.COMPOSITE_VALUE.01 |
| interaction / answer | multiple-choice / integer |
| difficulty band | 2 (axes: {"numericalComplexity": 0.25, "algebraicComplexity": 0.4, "reasoningSteps": 0.45, "abstraction": 0.5, "representation": 0.35, "requiredConnections": 0.4, "exactVsApproximate": 0}) |
| prompt | Evaluate: The functions f and g are defined by $ f(x) = x + 6, \qquad g(x) = -4x - 6 $ Find the value of $ (g \circ f)(2) $ |
| spoken math | The functions f and g are defined by f(x) = x + 6 and g(x) = -4x - 6. Find the value of (g o f)(2), that is g of f of 2. |
| params | `{"task": "composite_value", "f": {"kind": "linear", "a": {"num": 1, "den": 1}, "b": {"num": 6, "den": 1}}, "g": {"kind": "linear", "a": {"num": -4, "den": 1}, "b": {"num": -6, "den": 1}}, "order": "gf", "p": {"num": 2, "den": 1}}` |
| canonical answer | `{"num": -38, "den": 1}` |
| answer display | -38 |
| accepted form / checker | Exact-rational checker: the exact reduced fraction num/den is the answer; any equivalent fraction is accepted; a decimal is accepted only when it terminates (accepts.decimal=true); mixed numbers are not accepted; no tolerance; integer when den = 1. |
| worked solution | 1. Evaluate the inner function f at 2 -> f(2) = 8; 2. Evaluate the outer function g at 8 -> g(8) = -38; 3. State the value -> (g o f)(2) = -38 |
| MC options | A=-14; B=-6; C=-38 ✓; D=8 |
| distractor feedback | MISC.FUNC.COMP_AS_SUM (-6): (g o f) is composition, not addition: substitute f(x) into g.; MISC.FUNC.COMP_INNER_ONLY (8): After finding f(2), substitute that value into g.; MISC.FUNC.COMP_OUTER_AT_INPUT (-14): Apply f first: the input of g is f(2), not 2. |
| validation checks | 35/35 pass |
| covers cells | `band:composite_value:2`, `interaction:composite_value:multiple-choice`, `kind:composite_value:linear/linear:gf` |
| reproduction | `python -c "import sys; sys.path.insert(0,'oracle/spi_oracle'); import functions as G; print(G.serialize(G.generate(12, {'task': 'composite_value', 'interactionType': 'multiple-choice'})))"` |
| curriculum-review decision | ☐ APPROVE ☐ REVISE ☐ REJECT |

### composite_expression — seed 1 — band 5 (algebraic-expression, multiple-choice)

| field | value |
|---|---|
| objective | SPI.IBDPAASL.FUNC.COMPOSITE_EXPRESSION.01 |
| interaction / answer | multiple-choice / algebraic-expression |
| difficulty band | 5 (axes: {"numericalComplexity": 0.45, "algebraicComplexity": 0.95, "reasoningSteps": 0.85, "abstraction": 0.85, "representation": 0.65, "requiredConnections": 0.7, "exactVsApproximate": 0}) |
| prompt | Find the composite: The functions f and g are defined by $ f(x) = -x^{2} + 3x + 6, \qquad g(x) = -3x + 1 $ Find an expression for $ (f \circ g)(x) $ Expand and simplify your answer. |
| spoken math | The functions f and g are defined by f(x) = -x^2 + 3x + 6 and g(x) = -3x + 1. Find an expression for (f o g)(x), that is f of g of x. Expand and simplify your answer. |
| params | `{"task": "composite_expression", "f": {"kind": "quadratic", "a": {"num": -1, "den": 1}, "b": {"num": 3, "den": 1}, "c": {"num": 6, "den": 1}}, "g": {"kind": "linear", "a": {"num": -3, "den": 1}, "b": {"num": 1, "den": 1}}, "order": "fg"}` |
| canonical answer | `{"variable": "x", "coefficients": [{"num": 8, "den": 1}, {"num": -3, "den": 1}, {"num": -9, "den": 1}]}` |
| answer display | -9x^2 - 3x + 8 |
| accepted form / checker | Algebraic-expression checker (ASCII-anchored recursive-descent parser, exact rationals): any equivalent written form of the polynomial in x is accepted — reordered terms, unexpanded brackets and products, `^` or `**`, implicit multiplication, fractional coefficients as a/b or exact decimals, an optional `f(x) =` / `(f o g)(x) =` / `y =` prefix. Result codes: correct, wrong-variable, not-polynomial (division by x), wrong-degree, wrong-coefficients, misconception (a known wrong form), unparseable. |
| worked solution | 1. Substitute g(x) into f -> f(g(x)) = -(-3x + 1)^2 + 3(-3x + 1) + 6; 2. Expand and collect like terms -> = -9x^2 - 3x + 8; 3. State the composite -> (f o g)(x) = -9x^2 - 3x + 8 |
| MC options | A=3x^2 - 9x - 17; B=-9x^2 - 3x + 8 ✓; C=-x^2 + 7; D=3x^3 - 10x^2 - 15x + 6 |
| distractor feedback | MISC.FUNC.COMP_AS_PRODUCT (3x^3 - 10x^2 - 15x + 6): (f o g) is composition, not multiplication: substitute g(x) into f.; MISC.FUNC.COMP_AS_SUM (-x^2 + 7): (f o g) is composition, not addition: substitute g(x) into f.; MISC.FUNC.COMP_ORDER_REVERSED (3x^2 - 9x - 17): (f o g)(x) means f(g(x)): apply g first, then f. |
| validation checks | 36/36 pass |
| covers cells | `band:composite_expression:5`, `interaction:composite_expression:multiple-choice`, `kind:composite_expression:quadratic/linear:fg` |
| reproduction | `python -c "import sys; sys.path.insert(0,'oracle/spi_oracle'); import functions as G; print(G.serialize(G.generate(1, {'task': 'composite_expression', 'interactionType': 'multiple-choice'})))"` |
| curriculum-review decision | ☐ APPROVE ☐ REVISE ☐ REJECT |

### inverse_value — seed 1 — band 3 (integer, multiple-choice)

| field | value |
|---|---|
| objective | SPI.IBDPAASL.FUNC.INVERSE_VALUE.01 |
| interaction / answer | multiple-choice / integer |
| difficulty band | 3 (axes: {"numericalComplexity": 0.35, "algebraicComplexity": 0.6, "reasoningSteps": 0.6, "abstraction": 0.7, "representation": 0.5, "requiredConnections": 0.6, "exactVsApproximate": 0}) |
| prompt | Solve: The function f is defined by $ f(x) = x + 6 $ Find the value of k for which $ f^{-1}(k) = 6 $ |
| spoken math | The function f is defined by f(x) = x + 6. Find the value of k for which f inverse of k equals 6. |
| params | `{"task": "inverse_value", "name": "f", "a": {"num": 1, "den": 1}, "b": {"num": 6, "den": 1}, "form": "solve_inverse_equation", "x0": {"num": 6, "den": 1}}` |
| canonical answer | `{"num": 12, "den": 1}` |
| answer display | 12 |
| accepted form / checker | Exact-rational checker: the exact reduced fraction num/den is the answer; any equivalent fraction is accepted; a decimal is accepted only when it terminates (accepts.decimal=true); mixed numbers are not accepted; no tolerance; integer when den = 1. |
| worked solution | 1. Rewrite f^-1(k) = 6 as k = f(6); 2. Evaluate f at 6 -> k = 6 + 6 = 12; 3. State the value -> k = 12 |
| MC options | A=1/12; B=12 ✓; C=6; D=0 |
| distractor feedback | MISC.FUNC.INVVAL_RECIPROCAL (1/12): f^-1 means the inverse function, not 1 divided by f.; MISC.FUNC.INVVAL_APPLIES_INVERSE_AGAIN (0): f^-1(k) = 6 means f(6) = k, so evaluate f at 6.; MISC.FUNC.INVVAL_IDENTITY (6): k is not 6: f^-1(k) = 6 means k = f(6). |
| validation checks | 35/35 pass |
| covers cells | `band:inverse_value:3`, `interaction:inverse_value:multiple-choice`, `kind:inverse_value:solve_inverse_equation` |
| reproduction | `python -c "import sys; sys.path.insert(0,'oracle/spi_oracle'); import functions as G; print(G.serialize(G.generate(1, {'task': 'inverse_value', 'interactionType': 'multiple-choice'})))"` |
| curriculum-review decision | ☐ APPROVE ☐ REVISE ☐ REJECT |

### composite_expression — seed 25 — band 4 (algebraic-expression, free-response)

| field | value |
|---|---|
| objective | SPI.IBDPAASL.FUNC.COMPOSITE_EXPRESSION.01 |
| interaction / answer | free-response / algebraic-expression |
| difficulty band | 4 (axes: {"numericalComplexity": 0.35, "algebraicComplexity": 0.85, "reasoningSteps": 0.75, "abstraction": 0.75, "representation": 0.55, "requiredConnections": 0.6, "exactVsApproximate": 0}) |
| prompt | Find the composite: The functions f and g are defined by $ f(x) = -x^{2} - 2x - 5, \qquad g(x) = -x - 1 $ Find an expression for $ (g \circ f)(x) $ Expand and simplify your answer. |
| spoken math | The functions f and g are defined by f(x) = -x^2 - 2x - 5 and g(x) = -x - 1. Find an expression for (g o f)(x), that is g of f of x. Expand and simplify your answer. |
| params | `{"task": "composite_expression", "f": {"kind": "quadratic", "a": {"num": -1, "den": 1}, "b": {"num": -2, "den": 1}, "c": {"num": -5, "den": 1}}, "g": {"kind": "linear", "a": {"num": -1, "den": 1}, "b": {"num": -1, "den": 1}}, "order": "gf"}` |
| canonical answer | `{"variable": "x", "coefficients": [{"num": 4, "den": 1}, {"num": 2, "den": 1}, {"num": 1, "den": 1}]}` |
| answer display | x^2 + 2x + 4 |
| accepted form / checker | Algebraic-expression checker (ASCII-anchored recursive-descent parser, exact rationals): any equivalent written form of the polynomial in x is accepted — reordered terms, unexpanded brackets and products, `^` or `**`, implicit multiplication, fractional coefficients as a/b or exact decimals, an optional `f(x) =` / `(f o g)(x) =` / `y =` prefix. Result codes: correct, wrong-variable, not-polynomial (division by x), wrong-degree, wrong-coefficients, misconception (a known wrong form), unparseable. |
| worked solution | 1. Substitute f(x) into g -> g(f(x)) = -(-x^2 - 2x - 5) - 1; 2. Expand and collect like terms -> = x^2 + 2x + 4; 3. State the composite -> (g o f)(x) = x^2 + 2x + 4 |
| validation checks | 13/13 pass |
| covers cells | `band:composite_expression:4`, `kind:composite_expression:quadratic/linear:gf` |
| reproduction | `python -c "import sys; sys.path.insert(0,'oracle/spi_oracle'); import functions as G; print(G.serialize(G.generate(25, {'task': 'composite_expression', 'interactionType': 'free-response'})))"` |
| curriculum-review decision | ☐ APPROVE ☐ REVISE ☐ REJECT |

### evaluate_function — seed 65 — band 2 (integer, free-response)

| field | value |
|---|---|
| objective | SPI.IBDPAASL.FUNC.EVALUATE.01 |
| interaction / answer | free-response / integer |
| difficulty band | 2 (axes: {"numericalComplexity": 0.35, "algebraicComplexity": 0.4, "reasoningSteps": 0.4, "abstraction": 0.35, "representation": 0.3, "requiredConnections": 0.2, "exactVsApproximate": 0}) |
| prompt | Evaluate: The function g is defined by $ g(x) = 2x^{2} - 4x + 9 $ Find the value of g(3). |
| spoken math | The function g is defined by g(x) = 2x^2 - 4x + 9. Find the value of g(3). |
| params | `{"task": "evaluate_function", "name": "g", "rule": {"kind": "quadratic", "a": {"num": 2, "den": 1}, "b": {"num": -4, "den": 1}, "c": {"num": 9, "den": 1}}, "p": {"num": 3, "den": 1}}` |
| canonical answer | `{"num": 15, "den": 1}` |
| answer display | 15 |
| accepted form / checker | Exact-rational checker: the exact reduced fraction num/den is the answer; any equivalent fraction is accepted; a decimal is accepted only when it terminates (accepts.decimal=true); mixed numbers are not accepted; no tolerance; integer when den = 1. |
| worked solution | 1. Substitute x = 3 into the rule -> g(3) = 2(3^2) - 4(3) + 9; 2. Square first, then multiply and add -> = 18 - 12 + 9; 3. State the value -> g(3) = 15 |
| validation checks | 12/12 pass |
| covers cells | `band:evaluate_function:2`, `kind:evaluate_function:quadratic` |
| reproduction | `python -c "import sys; sys.path.insert(0,'oracle/spi_oracle'); import functions as G; print(G.serialize(G.generate(65, {'task': 'evaluate_function', 'interactionType': 'free-response'})))"` |
| curriculum-review decision | ☐ APPROVE ☐ REVISE ☐ REJECT |

### range_of_function — seed 68 — band 5 (interval, free-response)

| field | value |
|---|---|
| objective | SPI.IBDPAASL.FUNC.RANGE.01 |
| interaction / answer | free-response / interval |
| difficulty band | 5 (axes: {"numericalComplexity": 0.45, "algebraicComplexity": 0.75, "reasoningSteps": 0.8, "abstraction": 0.9, "representation": 0.8, "requiredConnections": 0.7, "exactVsApproximate": 0}) |
| prompt | State the range: The function f is defined by $ f(x) = -3x^{2} - 5x $ State the range of f. |
| spoken math | The function f is defined by f(x) = -3x^2 - 5x. State the range of f. |
| params | `{"task": "range_of_function", "name": "f", "rule": {"kind": "quadratic", "a": {"num": -3, "den": 1}, "b": {"num": -5, "den": 1}, "c": {"num": 0, "den": 1}}}` |
| canonical answer | `{"kind": "ray", "variable": "y", "endpoint": {"num": 25, "den": 12}, "inclusive": true, "direction": "le"}` |
| answer display | y <= 25/12 |
| accepted form / checker | Interval checker (ASCII-anchored, exact rationals): inequality notation (`x >= 2`, `2 <= x`), interval notation (`[2, inf)`), set-builder, the words `all real numbers`, exclusions (`x != 3`), unicode ≥ ≤ ≠ ∞ ℝ and `infinity`/`oo` are accepted. A domain is stated in x and a range in y (also f(x)/g(x)); the letter is checked (wrong-variable). Result codes: correct, wrong-variable, wrong-kind, wrong-endpoint, wrong-inclusivity, wrong-direction, misconception, unparseable. |
| worked solution | 1. Find the axis of symmetry -> x = -(-5)/(2(-3)) = -5/6; 2. Find the value at the vertex -> f(-5/6) = 25/12; 3. Determine the direction of opening -> a = -3 < 0, so the vertex is a maximum; 4. State the range -> y <= 25/12 |
| validation checks | 12/12 pass |
| covers cells | `band:range_of_function:5`, `kind:range_of_function:quadratic` |
| reproduction | `python -c "import sys; sys.path.insert(0,'oracle/spi_oracle'); import functions as G; print(G.serialize(G.generate(68, {'task': 'range_of_function', 'interactionType': 'free-response'})))"` |
| curriculum-review decision | ☐ APPROVE ☐ REVISE ☐ REJECT |

### function_from_composite — seed 1 — band 5 (algebraic-expression, multiple-choice)

| field | value |
|---|---|
| objective | SPI.IBDPAASL.FUNC.FUNCTION_FROM_COMPOSITE.01 |
| interaction / answer | multiple-choice / algebraic-expression |
| difficulty band | 5 (axes: {"numericalComplexity": 0.45, "algebraicComplexity": 1, "reasoningSteps": 1, "abstraction": 1, "representation": 0.7, "requiredConnections": 0.9, "exactVsApproximate": 0}) |
| prompt | Find the outer function: The functions f and g are defined by $ g(x) = 2x + 6, \qquad (f \circ g)(x) = 4x + 6 $ Find an expression for f(x). |
| spoken math | The functions f and g are defined by g(x) = 2x + 6 and (f o g)(x) = 4x + 6. Find an expression for f(x). |
| params | `{"task": "function_from_composite", "A": {"num": 2, "den": 1}, "B": {"num": -6, "den": 1}, "m": {"num": 2, "den": 1}, "c": {"num": 6, "den": 1}}` |
| canonical answer | `{"variable": "x", "coefficients": [{"num": -6, "den": 1}, {"num": 2, "den": 1}]}` |
| answer display | 2x - 6 |
| accepted form / checker | Algebraic-expression checker (ASCII-anchored recursive-descent parser, exact rationals): any equivalent written form of the polynomial in x is accepted — reordered terms, unexpanded brackets and products, `^` or `**`, implicit multiplication, fractional coefficients as a/b or exact decimals, an optional `f(x) =` / `(f o g)(x) =` / `y =` prefix. Result codes: correct, wrong-variable, not-polynomial (division by x), wrong-degree, wrong-coefficients, misconception (a known wrong form), unparseable. |
| worked solution | 1. Write f(g(x)) equal to the given composite -> f(2x + 6) = 4x + 6; 2. Let u = g(x) and express x in terms of u -> x = (1/2)u - 3; 3. Substitute and simplify -> f(u) = 2u - 6; 4. State the outer function -> f(x) = 2x - 6 |
| MC options | A=2x - 6 ✓; B=4x + 6; C=2x + 18; D=8x + 30 |
| distractor feedback | MISC.FUNC.FFC_COMPOSES_INSTEAD (8x + 30): You composed the given expression with g again; instead, work backwards from f(g(x)) to f.; MISC.FUNC.FFC_IGNORES_INNER (4x + 6): The given expression is f(g(x)), not f(x); undo g to recover f.; MISC.FUNC.FFC_SHIFT_NOT_INVERTED (2x + 18): Let u = g(x) = 2x + 6 and express x in terms of u: the shift 6 must be undone, not repeated. |
| validation checks | 35/35 pass |
| covers cells | `band:function_from_composite:5`, `interaction:function_from_composite:multiple-choice` |
| reproduction | `python -c "import sys; sys.path.insert(0,'oracle/spi_oracle'); import functions as G; print(G.serialize(G.generate(1, {'task': 'function_from_composite', 'interactionType': 'multiple-choice'})))"` |
| curriculum-review decision | ☐ APPROVE ☐ REVISE ☐ REJECT |

### inverse_expression — seed 14 — band 3 (algebraic-expression, multiple-choice)

| field | value |
|---|---|
| objective | SPI.IBDPAASL.FUNC.INVERSE_EXPRESSION.01 |
| interaction / answer | multiple-choice / algebraic-expression |
| difficulty band | 3 (axes: {"numericalComplexity": 0.25, "algebraicComplexity": 0.7, "reasoningSteps": 0.65, "abstraction": 0.7, "representation": 0.45, "requiredConnections": 0.55, "exactVsApproximate": 0}) |
| prompt | Find the inverse: The function g is defined by $ g(x) = x - 2 $ Find an expression for $ g^{-1}(x) $ |
| spoken math | The function g is defined by g(x) = x - 2. Find an expression for g inverse of x. |
| params | `{"task": "inverse_expression", "name": "g", "a": {"num": 1, "den": 1}, "b": {"num": -2, "den": 1}}` |
| canonical answer | `{"variable": "x", "coefficients": [{"num": 2, "den": 1}, {"num": 1, "den": 1}]}` |
| answer display | x + 2 |
| accepted form / checker | Algebraic-expression checker (ASCII-anchored recursive-descent parser, exact rationals): any equivalent written form of the polynomial in x is accepted — reordered terms, unexpanded brackets and products, `^` or `**`, implicit multiplication, fractional coefficients as a/b or exact decimals, an optional `f(x) =` / `(f o g)(x) =` / `y =` prefix. Result codes: correct, wrong-variable, not-polynomial (division by x), wrong-degree, wrong-coefficients, misconception (a known wrong form), unparseable. |
| worked solution | 1. Write y = g(x) -> y = x - 2; 2. Swap x and y -> x = y - 2; 3. Solve for y -> y = x + 2; 4. State the inverse function -> g^-1(x) = x + 2; 5. Verify -> g(x + 2) = x |
| MC options | A=(-1/2)x + 1/2; B=x + 2 ✓; C=x - 2; D=1/(x - 2) |
| distractor feedback | MISC.FUNC.INV_AS_RECIPROCAL (1/(x - 2)): g^-1 is the inverse function, not the reciprocal 1/g(x): swap x and y and solve for y.; MISC.FUNC.INV_SIGN_ERROR (x - 2): To undo - 2, apply the opposite operation.; MISC.FUNC.INV_SWAPS_ROLES ((-1/2)x + 1/2): Divide by the coefficient of x (1), not by the constant (-2). |
| validation checks | 35/35 pass |
| covers cells | `band:inverse_expression:3`, `interaction:inverse_expression:multiple-choice` |
| reproduction | `python -c "import sys; sys.path.insert(0,'oracle/spi_oracle'); import functions as G; print(G.serialize(G.generate(14, {'task': 'inverse_expression', 'interactionType': 'multiple-choice'})))"` |
| curriculum-review decision | ☐ APPROVE ☐ REVISE ☐ REJECT |

### one_to_one_restriction — seed 1 — band 5 (exact-rational, multiple-choice)

| field | value |
|---|---|
| objective | SPI.IBDPAASL.FUNC.ONE_TO_ONE_RESTRICTION.01 |
| interaction / answer | multiple-choice / exact-rational |
| difficulty band | 5 (axes: {"numericalComplexity": 0.45, "algebraicComplexity": 0.8, "reasoningSteps": 0.9, "abstraction": 1, "representation": 0.75, "requiredConnections": 1, "exactVsApproximate": 0}) |
| prompt | Find the restriction: The function g is defined by $ g(x) = x^{2} + x + 6, \quad x \leq k $ The domain of g is restricted so that the inverse function g^-1 exists. Find the greatest possible value of k. |
| spoken math | The function g is defined by g(x) = x^2 + x + 6, for x <= k. The domain of g is restricted so that the inverse function g^-1 exists. Find the greatest possible value of k. |
| params | `{"task": "one_to_one_restriction", "name": "g", "rule": {"kind": "quadratic", "a": {"num": 1, "den": 1}, "b": {"num": 1, "den": 1}, "c": {"num": 6, "den": 1}}, "side": "le"}` |
| canonical answer | `{"num": -1, "den": 2}` |
| answer display | -1/2 |
| accepted form / checker | Exact-rational checker: the exact reduced fraction num/den is the answer; any equivalent fraction is accepted; a decimal is accepted only when it terminates (accepts.decimal=true); mixed numbers are not accepted; no tolerance; integer when den = 1. |
| worked solution | 1. Find the axis of symmetry -> x = -(1)/(2(1)) = -1/2; 2. Restrict the domain at the vertex; 3. State the value of k -> k = -1/2 |
| MC options | A=1/2; B=-1/2 ✓; C=0; D=23/4 |
| distractor feedback | MISC.FUNC.VERTEX_X_SIGN (1/2): The axis of symmetry is x = -b/(2a); watch the sign of the x coefficient.; MISC.FUNC.VERTEX_Y_FOR_X (23/4): The restriction is on the INPUT x at the vertex, not on the value of the function there.; MISC.FUNC.RESTRICTION_ZERO (0): The symmetry of this parabola is not about x = 0; find the axis of symmetry from the coefficients. |
| validation checks | 35/35 pass |
| covers cells | `band:one_to_one_restriction:5`, `interaction:one_to_one_restriction:multiple-choice` |
| reproduction | `python -c "import sys; sys.path.insert(0,'oracle/spi_oracle'); import functions as G; print(G.serialize(G.generate(1, {'task': 'one_to_one_restriction', 'interactionType': 'multiple-choice'})))"` |
| curriculum-review decision | ☐ APPROVE ☐ REVISE ☐ REJECT |

### composite_value — seed 10 — band 3 (integer, free-response)

| field | value |
|---|---|
| objective | SPI.IBDPAASL.FUNC.COMPOSITE_VALUE.01 |
| interaction / answer | free-response / integer |
| difficulty band | 3 (axes: {"numericalComplexity": 0.45, "algebraicComplexity": 0.6, "reasoningSteps": 0.65, "abstraction": 0.7, "representation": 0.55, "requiredConnections": 0.6, "exactVsApproximate": 0}) |
| prompt | Evaluate: The functions f and g are defined by $ f(x) = 2x^{2} - 1, \qquad g(x) = x^{2} - 3x - 6 $ Find the value of $ (g \circ f)(5) $ |
| spoken math | The functions f and g are defined by f(x) = 2x^2 - 1 and g(x) = x^2 - 3x - 6. Find the value of (g o f)(5), that is g of f of 5. |
| params | `{"task": "composite_value", "f": {"kind": "quadratic", "a": {"num": 2, "den": 1}, "b": {"num": 0, "den": 1}, "c": {"num": -1, "den": 1}}, "g": {"kind": "quadratic", "a": {"num": 1, "den": 1}, "b": {"num": -3, "den": 1}, "c": {"num": -6, "den": 1}}, "order": "gf", "p": {"num": 5, "den": 1}}` |
| canonical answer | `{"num": 2248, "den": 1}` |
| answer display | 2248 |
| accepted form / checker | Exact-rational checker: the exact reduced fraction num/den is the answer; any equivalent fraction is accepted; a decimal is accepted only when it terminates (accepts.decimal=true); mixed numbers are not accepted; no tolerance; integer when den = 1. |
| worked solution | 1. Evaluate the inner function f at 5 -> f(5) = 49; 2. Evaluate the outer function g at 49 -> g(49) = 2248; 3. State the value -> (g o f)(5) = 2248 |
| validation checks | 12/12 pass |
| covers cells | `kind:composite_value:quadratic/quadratic:gf` |
| reproduction | `python -c "import sys; sys.path.insert(0,'oracle/spi_oracle'); import functions as G; print(G.serialize(G.generate(10, {'task': 'composite_value', 'interactionType': 'free-response'})))"` |
| curriculum-review decision | ☐ APPROVE ☐ REVISE ☐ REJECT |

### composite_value — seed 11 — band 3 (integer, free-response)

| field | value |
|---|---|
| objective | SPI.IBDPAASL.FUNC.COMPOSITE_VALUE.01 |
| interaction / answer | free-response / integer |
| difficulty band | 3 (axes: {"numericalComplexity": 0.45, "algebraicComplexity": 0.6, "reasoningSteps": 0.65, "abstraction": 0.7, "representation": 0.55, "requiredConnections": 0.6, "exactVsApproximate": 0}) |
| prompt | Evaluate: The functions f and g are defined by $ f(x) = -x^{2} + 2x, \qquad g(x) = x^{2} + 1 $ Find the value of $ (f \circ g)(0) $ |
| spoken math | The functions f and g are defined by f(x) = -x^2 + 2x and g(x) = x^2 + 1. Find the value of (f o g)(0), that is f of g of 0. |
| params | `{"task": "composite_value", "f": {"kind": "quadratic", "a": {"num": -1, "den": 1}, "b": {"num": 2, "den": 1}, "c": {"num": 0, "den": 1}}, "g": {"kind": "quadratic", "a": {"num": 1, "den": 1}, "b": {"num": 0, "den": 1}, "c": {"num": 1, "den": 1}}, "order": "fg", "p": {"num": 0, "den": 1}}` |
| canonical answer | `{"num": 1, "den": 1}` |
| answer display | 1 |
| accepted form / checker | Exact-rational checker: the exact reduced fraction num/den is the answer; any equivalent fraction is accepted; a decimal is accepted only when it terminates (accepts.decimal=true); mixed numbers are not accepted; no tolerance; integer when den = 1. |
| worked solution | 1. Evaluate the inner function g at 0 -> g(0) = 1; 2. Evaluate the outer function f at 1 -> f(1) = 1; 3. State the value -> (f o g)(0) = 1 |
| validation checks | 12/12 pass |
| covers cells | `kind:composite_value:quadratic/quadratic:fg` |
| reproduction | `python -c "import sys; sys.path.insert(0,'oracle/spi_oracle'); import functions as G; print(G.serialize(G.generate(11, {'task': 'composite_value', 'interactionType': 'free-response'})))"` |
| curriculum-review decision | ☐ APPROVE ☐ REVISE ☐ REJECT |

### range_of_function — seed 18 — band 4 (interval, free-response)

| field | value |
|---|---|
| objective | SPI.IBDPAASL.FUNC.RANGE.01 |
| interaction / answer | free-response / interval |
| difficulty band | 4 (axes: {"numericalComplexity": 0.35, "algebraicComplexity": 0.65, "reasoningSteps": 0.7, "abstraction": 0.8, "representation": 0.7, "requiredConnections": 0.6, "exactVsApproximate": 0}) |
| prompt | State the range: The function g is defined by $ g(x) = -\frac{4}{x - 4} $ State the range of g. |
| spoken math | The function g is defined by g(x) = -4/(x - 4). State the range of g. |
| params | `{"task": "range_of_function", "name": "g", "rule": {"kind": "reciprocal", "k": {"num": -4, "den": 1}, "h": {"num": 4, "den": 1}, "v": {"num": 0, "den": 1}}}` |
| canonical answer | `{"kind": "reals-except", "variable": "y", "points": [{"num": 0, "den": 1}]}` |
| answer display | y != 0 |
| accepted form / checker | Interval checker (ASCII-anchored, exact rationals): inequality notation (`x >= 2`, `2 <= x`), interval notation (`[2, inf)`), set-builder, the words `all real numbers`, exclusions (`x != 3`), unicode ≥ ≤ ≠ ∞ ℝ and `infinity`/`oo` are accepted. A domain is stated in x and a range in y (also f(x)/g(x)); the letter is checked (wrong-variable). Result codes: correct, wrong-variable, wrong-kind, wrong-endpoint, wrong-inclusivity, wrong-direction, misconception, unparseable. |
| worked solution | 1. Start from the base range -> -4/(x - 4) != 0; 2. Apply the vertical shift -> g(x) != 0; 3. State the range -> y != 0 |
| validation checks | 12/12 pass |
| covers cells | `kind:range_of_function:reciprocal` |
| reproduction | `python -c "import sys; sys.path.insert(0,'oracle/spi_oracle'); import functions as G; print(G.serialize(G.generate(18, {'task': 'range_of_function', 'interactionType': 'free-response'})))"` |
| curriculum-review decision | ☐ APPROVE ☐ REVISE ☐ REJECT |

### composite_expression — seed 22 — band 3 (algebraic-expression, free-response)

| field | value |
|---|---|
| objective | SPI.IBDPAASL.FUNC.COMPOSITE_EXPRESSION.01 |
| interaction / answer | free-response / algebraic-expression |
| difficulty band | 3 (axes: {"numericalComplexity": 0.25, "algebraicComplexity": 0.75, "reasoningSteps": 0.65, "abstraction": 0.65, "representation": 0.45, "requiredConnections": 0.5, "exactVsApproximate": 0}) |
| prompt | Find the composite: The functions f and g are defined by $ f(x) = -3x - 2, \qquad g(x) = 4x - 1 $ Find an expression for $ (f \circ g)(x) $ Expand and simplify your answer. |
| spoken math | The functions f and g are defined by f(x) = -3x - 2 and g(x) = 4x - 1. Find an expression for (f o g)(x), that is f of g of x. Expand and simplify your answer. |
| params | `{"task": "composite_expression", "f": {"kind": "linear", "a": {"num": -3, "den": 1}, "b": {"num": -2, "den": 1}}, "g": {"kind": "linear", "a": {"num": 4, "den": 1}, "b": {"num": -1, "den": 1}}, "order": "fg"}` |
| canonical answer | `{"variable": "x", "coefficients": [{"num": 1, "den": 1}, {"num": -12, "den": 1}]}` |
| answer display | -12x + 1 |
| accepted form / checker | Algebraic-expression checker (ASCII-anchored recursive-descent parser, exact rationals): any equivalent written form of the polynomial in x is accepted — reordered terms, unexpanded brackets and products, `^` or `**`, implicit multiplication, fractional coefficients as a/b or exact decimals, an optional `f(x) =` / `(f o g)(x) =` / `y =` prefix. Result codes: correct, wrong-variable, not-polynomial (division by x), wrong-degree, wrong-coefficients, misconception (a known wrong form), unparseable. |
| worked solution | 1. Substitute g(x) into f -> f(g(x)) = -3(4x - 1) - 2; 2. Expand and collect like terms -> = -12x + 1; 3. State the composite -> (f o g)(x) = -12x + 1 |
| validation checks | 13/13 pass |
| covers cells | `kind:composite_expression:linear/linear:fg` |
| reproduction | `python -c "import sys; sys.path.insert(0,'oracle/spi_oracle'); import functions as G; print(G.serialize(G.generate(22, {'task': 'composite_expression', 'interactionType': 'free-response'})))"` |
| curriculum-review decision | ☐ APPROVE ☐ REVISE ☐ REJECT |

### domain_of_function — seed 24 — band 2 (interval, free-response)

| field | value |
|---|---|
| objective | SPI.IBDPAASL.FUNC.DOMAIN.01 |
| interaction / answer | free-response / interval |
| difficulty band | 2 (axes: {"numericalComplexity": 0.25, "algebraicComplexity": 0.4, "reasoningSteps": 0.45, "abstraction": 0.6, "representation": 0.55, "requiredConnections": 0.3, "exactVsApproximate": 0}) |
| prompt | State the domain: The function f is defined by $ f(x) = x^{2} - 5 $ State the largest possible domain of f. |
| spoken math | The function f is defined by f(x) = x^2 - 5. State the largest possible domain of f. |
| params | `{"task": "domain_of_function", "name": "f", "rule": {"kind": "quadratic", "a": {"num": 1, "den": 1}, "b": {"num": 0, "den": 1}, "c": {"num": -5, "den": 1}}}` |
| canonical answer | `{"kind": "reals"}` |
| answer display | all real numbers |
| accepted form / checker | Interval checker (ASCII-anchored, exact rationals): inequality notation (`x >= 2`, `2 <= x`), interval notation (`[2, inf)`), set-builder, the words `all real numbers`, exclusions (`x != 3`), unicode ≥ ≤ ≠ ∞ ℝ and `infinity`/`oo` are accepted. A domain is stated in x and a range in y (also f(x)/g(x)); the letter is checked (wrong-variable). Result codes: correct, wrong-variable, wrong-kind, wrong-endpoint, wrong-inclusivity, wrong-direction, misconception, unparseable. |
| worked solution | 1. Identify the restriction -> none; 2. State the domain -> all real numbers |
| validation checks | 12/12 pass |
| covers cells | `kind:domain_of_function:quadratic` |
| reproduction | `python -c "import sys; sys.path.insert(0,'oracle/spi_oracle'); import functions as G; print(G.serialize(G.generate(24, {'task': 'domain_of_function', 'interactionType': 'free-response'})))"` |
| curriculum-review decision | ☐ APPROVE ☐ REVISE ☐ REJECT |

### composite_expression — seed 34 — band 4 (algebraic-expression, free-response)

| field | value |
|---|---|
| objective | SPI.IBDPAASL.FUNC.COMPOSITE_EXPRESSION.01 |
| interaction / answer | free-response / algebraic-expression |
| difficulty band | 4 (axes: {"numericalComplexity": 0.35, "algebraicComplexity": 0.85, "reasoningSteps": 0.75, "abstraction": 0.75, "representation": 0.55, "requiredConnections": 0.6, "exactVsApproximate": 0}) |
| prompt | Find the composite: The functions f and g are defined by $ f(x) = -2x - 5, \qquad g(x) = 2x^{2} + 3 $ Find an expression for $ (f \circ g)(x) $ Expand and simplify your answer. |
| spoken math | The functions f and g are defined by f(x) = -2x - 5 and g(x) = 2x^2 + 3. Find an expression for (f o g)(x), that is f of g of x. Expand and simplify your answer. |
| params | `{"task": "composite_expression", "f": {"kind": "linear", "a": {"num": -2, "den": 1}, "b": {"num": -5, "den": 1}}, "g": {"kind": "quadratic", "a": {"num": 2, "den": 1}, "b": {"num": 0, "den": 1}, "c": {"num": 3, "den": 1}}, "order": "fg"}` |
| canonical answer | `{"variable": "x", "coefficients": [{"num": -11, "den": 1}, {"num": 0, "den": 1}, {"num": -4, "den": 1}]}` |
| answer display | -4x^2 - 11 |
| accepted form / checker | Algebraic-expression checker (ASCII-anchored recursive-descent parser, exact rationals): any equivalent written form of the polynomial in x is accepted — reordered terms, unexpanded brackets and products, `^` or `**`, implicit multiplication, fractional coefficients as a/b or exact decimals, an optional `f(x) =` / `(f o g)(x) =` / `y =` prefix. Result codes: correct, wrong-variable, not-polynomial (division by x), wrong-degree, wrong-coefficients, misconception (a known wrong form), unparseable. |
| worked solution | 1. Substitute g(x) into f -> f(g(x)) = -2(2x^2 + 3) - 5; 2. Expand and collect like terms -> = -4x^2 - 11; 3. State the composite -> (f o g)(x) = -4x^2 - 11 |
| validation checks | 13/13 pass |
| covers cells | `kind:composite_expression:linear/quadratic:fg` |
| reproduction | `python -c "import sys; sys.path.insert(0,'oracle/spi_oracle'); import functions as G; print(G.serialize(G.generate(34, {'task': 'composite_expression', 'interactionType': 'free-response'})))"` |
| curriculum-review decision | ☐ APPROVE ☐ REVISE ☐ REJECT |

### composite_value — seed 37 — band 3 (integer, free-response)

| field | value |
|---|---|
| objective | SPI.IBDPAASL.FUNC.COMPOSITE_VALUE.01 |
| interaction / answer | free-response / integer |
| difficulty band | 3 (axes: {"numericalComplexity": 0.45, "algebraicComplexity": 0.6, "reasoningSteps": 0.65, "abstraction": 0.7, "representation": 0.55, "requiredConnections": 0.6, "exactVsApproximate": 0}) |
| prompt | Evaluate: The functions f and g are defined by $ f(x) = -x^{2} - 2x + 1, \qquad g(x) = -4x + 6 $ Find the value of $ (g \circ f)(0) $ |
| spoken math | The functions f and g are defined by f(x) = -x^2 - 2x + 1 and g(x) = -4x + 6. Find the value of (g o f)(0), that is g of f of 0. |
| params | `{"task": "composite_value", "f": {"kind": "quadratic", "a": {"num": -1, "den": 1}, "b": {"num": -2, "den": 1}, "c": {"num": 1, "den": 1}}, "g": {"kind": "linear", "a": {"num": -4, "den": 1}, "b": {"num": 6, "den": 1}}, "order": "gf", "p": {"num": 0, "den": 1}}` |
| canonical answer | `{"num": 2, "den": 1}` |
| answer display | 2 |
| accepted form / checker | Exact-rational checker: the exact reduced fraction num/den is the answer; any equivalent fraction is accepted; a decimal is accepted only when it terminates (accepts.decimal=true); mixed numbers are not accepted; no tolerance; integer when den = 1. |
| worked solution | 1. Evaluate the inner function f at 0 -> f(0) = 1; 2. Evaluate the outer function g at 1 -> g(1) = 2; 3. State the value -> (g o f)(0) = 2 |
| validation checks | 12/12 pass |
| covers cells | `kind:composite_value:quadratic/linear:gf` |
| reproduction | `python -c "import sys; sys.path.insert(0,'oracle/spi_oracle'); import functions as G; print(G.serialize(G.generate(37, {'task': 'composite_value', 'interactionType': 'free-response'})))"` |
| curriculum-review decision | ☐ APPROVE ☐ REVISE ☐ REJECT |

### composite_expression — seed 42 — band 5 (algebraic-expression, free-response)

| field | value |
|---|---|
| objective | SPI.IBDPAASL.FUNC.COMPOSITE_EXPRESSION.01 |
| interaction / answer | free-response / algebraic-expression |
| difficulty band | 5 (axes: {"numericalComplexity": 0.45, "algebraicComplexity": 0.95, "reasoningSteps": 0.85, "abstraction": 0.85, "representation": 0.65, "requiredConnections": 0.7, "exactVsApproximate": 0}) |
| prompt | Find the composite: The functions f and g are defined by $ f(x) = 2x - 4, \qquad g(x) = -x^{2} - 2x + 2 $ Find an expression for $ (g \circ f)(x) $ Expand and simplify your answer. |
| spoken math | The functions f and g are defined by f(x) = 2x - 4 and g(x) = -x^2 - 2x + 2. Find an expression for (g o f)(x), that is g of f of x. Expand and simplify your answer. |
| params | `{"task": "composite_expression", "f": {"kind": "linear", "a": {"num": 2, "den": 1}, "b": {"num": -4, "den": 1}}, "g": {"kind": "quadratic", "a": {"num": -1, "den": 1}, "b": {"num": -2, "den": 1}, "c": {"num": 2, "den": 1}}, "order": "gf"}` |
| canonical answer | `{"variable": "x", "coefficients": [{"num": -6, "den": 1}, {"num": 12, "den": 1}, {"num": -4, "den": 1}]}` |
| answer display | -4x^2 + 12x - 6 |
| accepted form / checker | Algebraic-expression checker (ASCII-anchored recursive-descent parser, exact rationals): any equivalent written form of the polynomial in x is accepted — reordered terms, unexpanded brackets and products, `^` or `**`, implicit multiplication, fractional coefficients as a/b or exact decimals, an optional `f(x) =` / `(f o g)(x) =` / `y =` prefix. Result codes: correct, wrong-variable, not-polynomial (division by x), wrong-degree, wrong-coefficients, misconception (a known wrong form), unparseable. |
| worked solution | 1. Substitute f(x) into g -> g(f(x)) = -(2x - 4)^2 - 2(2x - 4) + 2; 2. Expand and collect like terms -> = -4x^2 + 12x - 6; 3. State the composite -> (g o f)(x) = -4x^2 + 12x - 6 |
| validation checks | 13/13 pass |
| covers cells | `kind:composite_expression:linear/quadratic:gf` |
| reproduction | `python -c "import sys; sys.path.insert(0,'oracle/spi_oracle'); import functions as G; print(G.serialize(G.generate(42, {'task': 'composite_expression', 'interactionType': 'free-response'})))"` |
| curriculum-review decision | ☐ APPROVE ☐ REVISE ☐ REJECT |

### composite_value — seed 50 — band 2 (integer, free-response)

| field | value |
|---|---|
| objective | SPI.IBDPAASL.FUNC.COMPOSITE_VALUE.01 |
| interaction / answer | free-response / integer |
| difficulty band | 2 (axes: {"numericalComplexity": 0.25, "algebraicComplexity": 0.4, "reasoningSteps": 0.45, "abstraction": 0.5, "representation": 0.35, "requiredConnections": 0.4, "exactVsApproximate": 0}) |
| prompt | Evaluate: The functions f and g are defined by $ f(x) = -5x - 5, \qquad g(x) = 5x - 4 $ Find the value of $ (f \circ g)(4) $ |
| spoken math | The functions f and g are defined by f(x) = -5x - 5 and g(x) = 5x - 4. Find the value of (f o g)(4), that is f of g of 4. |
| params | `{"task": "composite_value", "f": {"kind": "linear", "a": {"num": -5, "den": 1}, "b": {"num": -5, "den": 1}}, "g": {"kind": "linear", "a": {"num": 5, "den": 1}, "b": {"num": -4, "den": 1}}, "order": "fg", "p": {"num": 4, "den": 1}}` |
| canonical answer | `{"num": -85, "den": 1}` |
| answer display | -85 |
| accepted form / checker | Exact-rational checker: the exact reduced fraction num/den is the answer; any equivalent fraction is accepted; a decimal is accepted only when it terminates (accepts.decimal=true); mixed numbers are not accepted; no tolerance; integer when den = 1. |
| worked solution | 1. Evaluate the inner function g at 4 -> g(4) = 16; 2. Evaluate the outer function f at 16 -> f(16) = -85; 3. State the value -> (f o g)(4) = -85 |
| validation checks | 12/12 pass |
| covers cells | `kind:composite_value:linear/linear:fg` |
| reproduction | `python -c "import sys; sys.path.insert(0,'oracle/spi_oracle'); import functions as G; print(G.serialize(G.generate(50, {'task': 'composite_value', 'interactionType': 'free-response'})))"` |
| curriculum-review decision | ☐ APPROVE ☐ REVISE ☐ REJECT |

### solve_for_input — seed 54 — band 3 (integer, free-response)

| field | value |
|---|---|
| objective | SPI.IBDPAASL.FUNC.SOLVE_FOR_INPUT.01 |
| interaction / answer | free-response / integer |
| difficulty band | 3 (axes: {"numericalComplexity": 0.45, "algebraicComplexity": 0.7, "reasoningSteps": 0.7, "abstraction": 0.55, "representation": 0.45, "requiredConnections": 0.5, "exactVsApproximate": 0}) |
| prompt | Solve: The function f is defined by $ f(x) = -\frac{1}{x + 2} + 2 $ Find the value of x for which f(x) = 1. |
| spoken math | The function f is defined by f(x) = -1/(x + 2) + 2. Find the value of x for which f(x) = 1. |
| params | `{"task": "solve_for_input", "name": "f", "rule": {"kind": "reciprocal", "k": {"num": -1, "den": 1}, "h": {"num": -2, "den": 1}, "v": {"num": 2, "den": 1}}, "target": {"num": 1, "den": 1}, "x0": {"num": -1, "den": 1}}` |
| canonical answer | `{"num": -1, "den": 1}` |
| answer display | -1 |
| accepted form / checker | Exact-rational checker: the exact reduced fraction num/den is the answer; any equivalent fraction is accepted; a decimal is accepted only when it terminates (accepts.decimal=true); mixed numbers are not accepted; no tolerance; integer when den = 1. |
| worked solution | 1. Set up the equation -> -1/(x + 2) + 2 = 1; 2. Subtract 2 from both sides -> -1/(x + 2) = -1; 3. Multiply both sides by the denominator and divide by the value -> x + 2 = 1; 4. Subtract 2 from both sides -> x = -1; 5. State the solution -> x = -1; 6. Verify by substitution -> f(-1) = 1 |
| validation checks | 12/12 pass |
| covers cells | `kind:solve_for_input:reciprocal` |
| reproduction | `python -c "import sys; sys.path.insert(0,'oracle/spi_oracle'); import functions as G; print(G.serialize(G.generate(54, {'task': 'solve_for_input', 'interactionType': 'free-response'})))"` |
| curriculum-review decision | ☐ APPROVE ☐ REVISE ☐ REJECT |

### inverse_value — seed 73 — band 4 (integer, free-response)

| field | value |
|---|---|
| objective | SPI.IBDPAASL.FUNC.INVERSE_VALUE.01 |
| interaction / answer | free-response / integer |
| difficulty band | 4 (axes: {"numericalComplexity": 0.45, "algebraicComplexity": 0.7, "reasoningSteps": 0.7, "abstraction": 0.8, "representation": 0.6, "requiredConnections": 0.7, "exactVsApproximate": 0}) |
| prompt | Solve: The function h is defined by $ h(x) = -4x + 5 $ Find the value of k for which $ h^{-1}(k) = -6 $ |
| spoken math | The function h is defined by h(x) = -4x + 5. Find the value of k for which h inverse of k equals -6. |
| params | `{"task": "inverse_value", "name": "h", "a": {"num": -4, "den": 1}, "b": {"num": 5, "den": 1}, "form": "solve_inverse_equation", "x0": {"num": -6, "den": 1}}` |
| canonical answer | `{"num": 29, "den": 1}` |
| answer display | 29 |
| accepted form / checker | Exact-rational checker: the exact reduced fraction num/den is the answer; any equivalent fraction is accepted; a decimal is accepted only when it terminates (accepts.decimal=true); mixed numbers are not accepted; no tolerance; integer when den = 1. |
| worked solution | 1. Rewrite h^-1(k) = -6 as k = h(-6); 2. Evaluate h at -6 -> k = -4(-6) + 5 = 29; 3. State the value -> k = 29 |
| validation checks | 12/12 pass |
| covers cells | `band:inverse_value:4` |
| reproduction | `python -c "import sys; sys.path.insert(0,'oracle/spi_oracle'); import functions as G; print(G.serialize(G.generate(73, {'task': 'inverse_value', 'interactionType': 'free-response'})))"` |
| curriculum-review decision | ☐ APPROVE ☐ REVISE ☐ REJECT |

### identify_function — seed 90 — band 1 (multiple-choice, multiple-choice)

| field | value |
|---|---|
| objective | SPI.IBDPAASL.FUNC.IDENTIFY_FUNCTION.01 |
| interaction / answer | multiple-choice / multiple-choice |
| difficulty band | 1 (axes: {"numericalComplexity": 0.25, "algebraicComplexity": 0.1, "reasoningSteps": 0.25, "abstraction": 0.5, "representation": 0.4, "requiredConnections": 0.1, "exactVsApproximate": 0}) |
| prompt | Identify: Exactly one of the following relations is not a function. Which one? |
| spoken math | Exactly one of the following relations is not a function. Which one? Option A: the ordered pairs (4, -4); (5, 2); (2, 8); (1, 6). Option B: the ordered pairs (9, -4); (3, -4); (0, 4); (8, 2). Option C: the ordered pairs (0, 3); (1, 3); (7, 3); (4, 3). Option D: the ordered pairs (2, 2); (3, -6); (7, 7); (7, -3). |
| params | `{"task": "identify_function", "nonFunction": [[2, 2], [3, -6], [7, 7], [7, -3]], "functions": [{"pairs": [[9, -4], [3, -4], [0, 4], [8, 2]], "misconceptionId": "MISC.FUNC.MANY_TO_ONE_REJECTED"}, {"pairs": [[0, 3], [1, 3], [7, 3], [4, 3]], "misconceptionId": "MISC.FUNC.CONSTANT_REJECTED"}, {"pairs": [[4, -4], [5, 2], [2, 8], [1, 6]], "misconceptionId": "MISC.FUNC.PATTERN_REQUIRED"}], "negativeInputs": false, "separatedRepeat": false}` |
| canonical answer | `"D"` |
| answer display | D |
| accepted form / checker | Choice checker: the selected option letter is the answer; exactly one of the four relations has an input paired with two different outputs. The three distractors are structurally distinct functions (many-to-one, constant, pattern-free) so each wrong choice diagnoses a named belief. |
| worked solution | 1. List the inputs of each relation; 2. Find the relation with a repeated input and two different outputs -> Relation D: the input 7 is paired with both 7 and -3; 3. State the relation that is not a function -> D |
| MC options | A={(4, -4), (5, 2), (2, 8), (1, 6)}; B={(9, -4), (3, -4), (0, 4), (8, 2)}; C={(0, 3), (1, 3), (7, 3), (4, 3)}; D={(2, 2), (3, -6), (7, 7), (7, -3)} ✓ |
| distractor feedback | MISC.FUNC.MANY_TO_ONE_REJECTED ({(9, -4), (3, -4), (0, 4), (8, 2)}): Two different inputs may share the same output. A relation fails to be a function only when ONE input has two different outputs.; MISC.FUNC.CONSTANT_REJECTED ({(0, 3), (1, 3), (7, 3), (4, 3)}): A constant relation sends every input to the same output; each input still has exactly one output, so it is a function.; MISC.FUNC.PATTERN_REQUIRED ({(4, -4), (5, 2), (2, 8), (1, 6)}): A function does not need a formula or a visible pattern. Check only that no input appears twice with different outputs. |
| validation checks | 17/17 pass |
| covers cells | `band:identify_function:1` |
| reproduction | `python -c "import sys; sys.path.insert(0,'oracle/spi_oracle'); import functions as G; print(G.serialize(G.generate(90, {'task': 'identify_function', 'interactionType': 'multiple-choice'})))"` |
| curriculum-review decision | ☐ APPROVE ☐ REVISE ☐ REJECT |

### evaluate_function — seed 101 — band 3 (integer, free-response)

| field | value |
|---|---|
| objective | SPI.IBDPAASL.FUNC.EVALUATE.01 |
| interaction / answer | free-response / integer |
| difficulty band | 3 (axes: {"numericalComplexity": 0.45, "algebraicComplexity": 0.5, "reasoningSteps": 0.5, "abstraction": 0.45, "representation": 0.4, "requiredConnections": 0.3, "exactVsApproximate": 0}) |
| prompt | Evaluate: The function g is defined by $ g(x) = \sqrt{2x} + 1 $ Find the value of g(2). |
| spoken math | The function g is defined by g(x) = sqrt(2x) + 1. Find the value of g(2). |
| params | `{"task": "evaluate_function", "name": "g", "rule": {"kind": "sqrt", "a": {"num": 2, "den": 1}, "b": {"num": 0, "den": 1}, "v": {"num": 1, "den": 1}}, "p": {"num": 2, "den": 1}}` |
| canonical answer | `{"num": 3, "den": 1}` |
| answer display | 3 |
| accepted form / checker | Exact-rational checker: the exact reduced fraction num/den is the answer; any equivalent fraction is accepted; a decimal is accepted only when it terminates (accepts.decimal=true); mixed numbers are not accepted; no tolerance; integer when den = 1. |
| worked solution | 1. Substitute x = 2 into the rule -> g(2) = sqrt(2(2)) + 1; 2. Evaluate the radicand, then take the square root -> = sqrt(4) + 1 = 2 + 1; 3. State the value -> g(2) = 3 |
| validation checks | 12/12 pass |
| covers cells | `kind:evaluate_function:sqrt` |
| reproduction | `python -c "import sys; sys.path.insert(0,'oracle/spi_oracle'); import functions as G; print(G.serialize(G.generate(101, {'task': 'evaluate_function', 'interactionType': 'free-response'})))"` |
| curriculum-review decision | ☐ APPROVE ☐ REVISE ☐ REJECT |

### composite_value — seed 126 — band 3 (integer, free-response)

| field | value |
|---|---|
| objective | SPI.IBDPAASL.FUNC.COMPOSITE_VALUE.01 |
| interaction / answer | free-response / integer |
| difficulty band | 3 (axes: {"numericalComplexity": 0.45, "algebraicComplexity": 0.6, "reasoningSteps": 0.65, "abstraction": 0.7, "representation": 0.55, "requiredConnections": 0.6, "exactVsApproximate": 0}) |
| prompt | Evaluate: The functions f and g are defined by $ f(x) = x^{2} - x + 3, \qquad g(x) = 2x + 6 $ Find the value of $ (f \circ g)(-3) $ |
| spoken math | The functions f and g are defined by f(x) = x^2 - x + 3 and g(x) = 2x + 6. Find the value of (f o g)(-3), that is f of g of -3. |
| params | `{"task": "composite_value", "f": {"kind": "quadratic", "a": {"num": 1, "den": 1}, "b": {"num": -1, "den": 1}, "c": {"num": 3, "den": 1}}, "g": {"kind": "linear", "a": {"num": 2, "den": 1}, "b": {"num": 6, "den": 1}}, "order": "fg", "p": {"num": -3, "den": 1}}` |
| canonical answer | `{"num": 3, "den": 1}` |
| answer display | 3 |
| accepted form / checker | Exact-rational checker: the exact reduced fraction num/den is the answer; any equivalent fraction is accepted; a decimal is accepted only when it terminates (accepts.decimal=true); mixed numbers are not accepted; no tolerance; integer when den = 1. |
| worked solution | 1. Evaluate the inner function g at -3 -> g(-3) = 0; 2. Evaluate the outer function f at 0 -> f(0) = 3; 3. State the value -> (f o g)(-3) = 3 |
| validation checks | 12/12 pass |
| covers cells | `kind:composite_value:quadratic/linear:fg` |
| reproduction | `python -c "import sys; sys.path.insert(0,'oracle/spi_oracle'); import functions as G; print(G.serialize(G.generate(126, {'task': 'composite_value', 'interactionType': 'free-response'})))"` |
| curriculum-review decision | ☐ APPROVE ☐ REVISE ☐ REJECT |

### domain_of_function — seed 132 — band 3 (interval, free-response)

| field | value |
|---|---|
| objective | SPI.IBDPAASL.FUNC.DOMAIN.01 |
| interaction / answer | free-response / interval |
| difficulty band | 3 (axes: {"numericalComplexity": 0.35, "algebraicComplexity": 0.5, "reasoningSteps": 0.55, "abstraction": 0.7, "representation": 0.65, "requiredConnections": 0.4, "exactVsApproximate": 0}) |
| prompt | State the domain: The function h is defined by $ h(x) = \frac{4}{x - 3} + 4 $ State the largest possible domain of h. |
| spoken math | The function h is defined by h(x) = 4/(x - 3) + 4. State the largest possible domain of h. |
| params | `{"task": "domain_of_function", "name": "h", "rule": {"kind": "reciprocal", "k": {"num": 4, "den": 1}, "h": {"num": 3, "den": 1}, "v": {"num": 4, "den": 1}}}` |
| canonical answer | `{"kind": "reals-except", "variable": "x", "points": [{"num": 3, "den": 1}]}` |
| answer display | x != 3 |
| accepted form / checker | Interval checker (ASCII-anchored, exact rationals): inequality notation (`x >= 2`, `2 <= x`), interval notation (`[2, inf)`), set-builder, the words `all real numbers`, exclusions (`x != 3`), unicode ≥ ≤ ≠ ∞ ℝ and `infinity`/`oo` are accepted. A domain is stated in x and a range in y (also f(x)/g(x)); the letter is checked (wrong-variable). Result codes: correct, wrong-variable, wrong-kind, wrong-endpoint, wrong-inclusivity, wrong-direction, misconception, unparseable. |
| worked solution | 1. Identify the restriction -> x - 3 != 0; 2. Solve for the excluded input -> x != 3; 3. State the domain -> x != 3 |
| validation checks | 12/12 pass |
| covers cells | `kind:domain_of_function:reciprocal` |
| reproduction | `python -c "import sys; sys.path.insert(0,'oracle/spi_oracle'); import functions as G; print(G.serialize(G.generate(132, {'task': 'domain_of_function', 'interactionType': 'free-response'})))"` |
| curriculum-review decision | ☐ APPROVE ☐ REVISE ☐ REJECT |

### composite_value — seed 149 — band 3 (integer, free-response)

| field | value |
|---|---|
| objective | SPI.IBDPAASL.FUNC.COMPOSITE_VALUE.01 |
| interaction / answer | free-response / integer |
| difficulty band | 3 (axes: {"numericalComplexity": 0.45, "algebraicComplexity": 0.6, "reasoningSteps": 0.65, "abstraction": 0.7, "representation": 0.55, "requiredConnections": 0.6, "exactVsApproximate": 0}) |
| prompt | Evaluate: The functions f and g are defined by $ f(x) = 4x, \qquad g(x) = 2x^{2} - x + 6 $ Find the value of $ (f \circ g)(1) $ |
| spoken math | The functions f and g are defined by f(x) = 4x and g(x) = 2x^2 - x + 6. Find the value of (f o g)(1), that is f of g of 1. |
| params | `{"task": "composite_value", "f": {"kind": "linear", "a": {"num": 4, "den": 1}, "b": {"num": 0, "den": 1}}, "g": {"kind": "quadratic", "a": {"num": 2, "den": 1}, "b": {"num": -1, "den": 1}, "c": {"num": 6, "den": 1}}, "order": "fg", "p": {"num": 1, "den": 1}}` |
| canonical answer | `{"num": 28, "den": 1}` |
| answer display | 28 |
| accepted form / checker | Exact-rational checker: the exact reduced fraction num/den is the answer; any equivalent fraction is accepted; a decimal is accepted only when it terminates (accepts.decimal=true); mixed numbers are not accepted; no tolerance; integer when den = 1. |
| worked solution | 1. Evaluate the inner function g at 1 -> g(1) = 7; 2. Evaluate the outer function f at 7 -> f(7) = 28; 3. State the value -> (f o g)(1) = 28 |
| validation checks | 12/12 pass |
| covers cells | `kind:composite_value:linear/quadratic:fg` |
| reproduction | `python -c "import sys; sys.path.insert(0,'oracle/spi_oracle'); import functions as G; print(G.serialize(G.generate(149, {'task': 'composite_value', 'interactionType': 'free-response'})))"` |
| curriculum-review decision | ☐ APPROVE ☐ REVISE ☐ REJECT |

### domain_of_function — seed 151 — band 4 (interval, free-response)

| field | value |
|---|---|
| objective | SPI.IBDPAASL.FUNC.DOMAIN.01 |
| interaction / answer | free-response / interval |
| difficulty band | 4 (axes: {"numericalComplexity": 0.45, "algebraicComplexity": 0.6, "reasoningSteps": 0.65, "abstraction": 0.8, "representation": 0.75, "requiredConnections": 0.5, "exactVsApproximate": 0}) |
| prompt | State the domain: The function f is defined by $ f(x) = \sqrt{4 - x} $ State the largest possible domain of f. |
| spoken math | The function f is defined by f(x) = sqrt(4 - x). State the largest possible domain of f. |
| params | `{"task": "domain_of_function", "name": "f", "rule": {"kind": "sqrt", "a": {"num": -1, "den": 1}, "b": {"num": 4, "den": 1}, "v": {"num": 0, "den": 1}}}` |
| canonical answer | `{"kind": "ray", "variable": "x", "endpoint": {"num": 4, "den": 1}, "inclusive": true, "direction": "le"}` |
| answer display | x <= 4 |
| accepted form / checker | Interval checker (ASCII-anchored, exact rationals): inequality notation (`x >= 2`, `2 <= x`), interval notation (`[2, inf)`), set-builder, the words `all real numbers`, exclusions (`x != 3`), unicode ≥ ≤ ≠ ∞ ℝ and `infinity`/`oo` are accepted. A domain is stated in x and a range in y (also f(x)/g(x)); the letter is checked (wrong-variable). Result codes: correct, wrong-variable, wrong-kind, wrong-endpoint, wrong-inclusivity, wrong-direction, misconception, unparseable. |
| worked solution | 1. Identify the restriction -> 4 - x >= 0; 2. Solve the inequality -> x <= 4; 3. State the domain -> x <= 4 |
| validation checks | 12/12 pass |
| covers cells | `band:domain_of_function:4` |
| reproduction | `python -c "import sys; sys.path.insert(0,'oracle/spi_oracle'); import functions as G; print(G.serialize(G.generate(151, {'task': 'domain_of_function', 'interactionType': 'free-response'})))"` |
| curriculum-review decision | ☐ APPROVE ☐ REVISE ☐ REJECT |

