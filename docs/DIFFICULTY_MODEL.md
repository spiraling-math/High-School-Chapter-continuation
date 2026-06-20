# Difficulty Model

Status: Phase 1 draft. Last updated: 2026-06-20.

Difficulty is **multidimensional**. It is never defined by the size of numbers alone. Each item carries a vector of normalized axes plus a single derived band, so difficulty is data the platform can filter, target, and audit.

## 1. The difficulty vector

Sixteen axes, each normalized to `[0, 1]` (0 = minimal demand, 1 = maximal demand for the relevant stage):

| Axis | Meaning |
| --- | --- |
| `numericalComplexity` | Size/type of numbers, fractions, decimals, negatives. |
| `algebraicComplexity` | Symbolic manipulation required. |
| `reasoningSteps` | Number of distinct reasoning steps. |
| `abstraction` | Concrete → abstract. |
| `representation` | Demand of the representation(s) used. |
| `familiarity` | Routine → novel framing. |
| `readingDemand` | Language/reading load. |
| `informationDensity` | Amount of information to track. |
| `irrelevantInformation` | Presence of distractor information. |
| `requiredConnections` | Linking multiple ideas/topics. |
| `exactVsApproximate` | Exact vs. approximate working demand. |
| `calculatorDependence` | Reliance on a calculator. |
| `scaffolding` | Amount of provided support (inverse: more scaffolding lowers difficulty). |
| `proofDemand` | Degree of formal proof required. |
| `interpretationDemand` | Interpreting results in context. |
| `modellingDemand` | Modelling/abstraction-of-a-situation demand. |

These map 1:1 to `question-item.schema.json#/$defs/difficultyProfile.axes`.

## 2. Derived overall band

`overallBand` is an integer `1..5` derived from the vector by a **documented, deterministic function** — never assigned by intuition.

Default function (platform baseline):

```
weighted = Σ ( w_axis * axis_value )           # weights sum to 1
score    = clamp(weighted, 0, 1)
band     = 1 + floor( score * 5 )  capped at 5  # 0..0.2→1, 0.2..0.4→2, … 0.8..1→5
```

- Default weights emphasize `reasoningSteps`, `abstraction`, `requiredConnections`, and `proofDemand`; `numericalComplexity` is intentionally **not** dominant.
- `scaffolding` enters with a **negative** contribution (more scaffolding → lower band), implemented by using `(1 - scaffolding)` in the sum.
- The exact default weights live in `core/difficulty` and are versioned. Generators may not invent their own band function; they populate axes and call the shared function.

## 3. Generator responsibilities

Each generator:
1. Maps its config/params to axis values (documented in `describe().difficultyControls`).
2. Calls the shared band function to set `overallBand`.
3. Ensures the band is **monotonic** in the obvious controls (e.g. larger `n`, negative `d`, reverse tasks should not lower the band).

A property test asserts monotonicity where it is expected.

## 4. Worked example — arithmetic sequences

| Control | Axis effect |
| --- | --- |
| Larger `|a1|`, `|d|`, `n` | ↑ `numericalComplexity` |
| Negative `d` | ↑ `numericalComplexity`, slight ↑ `reasoningSteps` |
| Task `nth_term` (1 step) | low `reasoningSteps` |
| Task `sum_n` (2 steps) | medium `reasoningSteps` |
| Reverse tasks (`find_d`, `find_n_for_value`) | ↑ `reasoningSteps`, ↑ `abstraction` |
| Context wrapper (word problem) | ↑ `readingDemand`, ↑ `interpretationDemand`, ↑ `modellingDemand` |

So a bare `nth_term` with small positive numbers lands at band 1; a reverse `find_n_for_value` with negative `d` in a worded context lands at band 3–4 — without merely enlarging numbers.

## 5. Platform scale and comparability

- The band is **platform-wide** (1..5 means the same thing across generators and stages, relative to the target stage).
- Difficulty is always interpreted relative to the objective's stage: a band-3 preschool item and a band-3 IB item are both "moderately demanding for their level".
- Blueprints target difficulty distributions over bands; the Quality Console audits realized distributions against targets.

## 6. Calibration and revision

- Initial axis mappings are author-set. As real usage data accrues (future Student Preview/practice), empirical difficulty can be compared to predicted bands and the weights recalibrated.
- The band function and weights are versioned; recalibration bumps the version and may trigger re-banding of stored items (the axes are retained, so re-banding is a pure recomputation).
