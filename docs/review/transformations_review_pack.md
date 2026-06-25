# gen.geometry.transformations — Review Pack

> **PENDING-REVIEW.** Free-response only. Required coverage cells are **derived from the 10,000-seed distribution report** (reachability is the authoritative source); the builder fails on any uncovered reachable cell.

- Generator **gen.geometry.transformations v1.0.0**, validator v1.0.0.
- Representative items: **22**; full coverage: **True**; all machine-valid: **True**.
- Result codes: all 14 reachable **True** (matrix mismatches 0).
- Diagnostics: **24/24** exercised, inapplicable [], recomputation mismatches 0.
- Multiple-choice rejected for **9/9** tasks.
- Owner-O regression invariants: **all pass**.

## Coverage cells

Required: 71 · Covered: 72 · Missing: 0

## Representative items

| item | task | band | answer | valid | covers |
|---|---|---|---|---|---|
| 3189 | rotate_shape | 4 | table-completion | True | 12 cells |
| 212 | rotate_point | 2 | coordinate | True | 6 cells |
| 2 | describe_translation | 3 | transformation | True | 5 cells |
| 4 | describe_rotation | 4 | transformation | True | 4 cells |
| 7 | translate_point | 2 | coordinate | True | 4 cells |
| 8 | translate_shape | 2 | table-completion | True | 4 cells |
| 12 | reflect_point | 3 | coordinate | True | 4 cells |
| 18 | reflect_shape | 2 | table-completion | True | 4 cells |
| 30 | describe_reflection | 3 | transformation | True | 4 cells |
| 150 | describe_translation | 2 | transformation | True | 3 cells |
| 896 | reflect_shape | 3 | table-completion | True | 3 cells |
| 1878 | translate_shape | 3 | table-completion | True | 3 cells |
| 13 | rotate_shape | 3 | table-completion | True | 2 cells |
| 23 | translate_point | 1 | coordinate | True | 2 cells |
| 407 | describe_rotation | 3 | transformation | True | 2 cells |
| 865 | describe_reflection | 4 | transformation | True | 2 cells |
| 1315 | translate_shape | 2 | table-completion | True | 2 cells |
| 11 | rotate_point | 3 | coordinate | True | 1 cells |
| 15 | reflect_point | 2 | coordinate | True | 1 cells |
| 42 | rotate_shape | 3 | table-completion | True | 1 cells |
| 51 | translate_shape | 2 | table-completion | True | 1 cells |
| 1391 | reflect_shape | 3 | table-completion | True | 1 cells |

## Regression invariants (owner O)

- ✓ symmetric_not_auto_ambiguous
- ✓ uniqueness_from_labels
- ✓ fixed_vertex_valid
- ✓ unchanged_rejected
- ✓ permuted_label_rejected
- ✓ quad_distances_preserved
- ✓ rotation_preserves_orientation
- ✓ reflection_reverses_orientation
- ✓ display_derived_from_canonical
- ✓ no_duplicate_descriptor_field
