# Review pack — gen.measurement.mensuration v1.0.1

> PENDING-REVIEW. Free-response only. Required coverage cells are **derived from the distribution report** (every task × supported interaction × reachable band × realised answer shape × base unit × shape kind × decomposition mode × hidden role). The builder fails on any missing reachable cell.

- Required cells: **46**; covered: **46**; full coverage: **True**; all items machine-valid: **True**.
- Items selected (minimal set-cover): **16**.
- Feature proofs: student-vs-answer-key base geometry identical = **True**; answer absent from every student figure = **True**; NOT-TO-SCALE banner on hidden-dimension items = **True**.
- Decomposition (task-specific, owner C1): additive area_composite exemplar = **True**; subtractive = **True**; perimeter items NOT counted toward area-decomposition cells = **True**.
- Quantity checker (owner C3): all seven codes reached = **True** (correct, incorrect-value, malformed-response, missing-unit, wrong-base-unit, wrong-dimension, wrong-exponent); genuinely-different forms accepted = **40**; cross-unit conversion performed = **False**.
- Diagnostics (owner C4): numeric 8, unit 4, pedagogical-only 1; null numeric records = **0**.
- Render modes / 6000×4200 export / label-collision / student-beside-key: see the visual audit.

## Coverage matrix

| cell | covered | #items |
| --- | --- | --- |
| `band:area_composite:3` | ✓ | 1 |
| `band:area_composite:4` | ✓ | 1 |
| `band:area_rectangle:1` | ✓ | 1 |
| `band:area_rectangle:2` | ✓ | 1 |
| `band:area_triangle:2` | ✓ | 1 |
| `band:area_triangle:3` | ✓ | 1 |
| `band:missing_dimension_area:2` | ✓ | 1 |
| `band:missing_dimension_area:3` | ✓ | 1 |
| `band:missing_length_perimeter:2` | ✓ | 1 |
| `band:missing_length_perimeter:3` | ✓ | 1 |
| `band:missing_triangle_base_height:3` | ✓ | 1 |
| `band:missing_triangle_base_height:4` | ✓ | 1 |
| `band:perimeter_composite:2` | ✓ | 1 |
| `band:perimeter_composite:3` | ✓ | 1 |
| `band:perimeter_rectangle:1` | ✓ | 1 |
| `band:perimeter_rectangle:2` | ✓ | 1 |
| `corner:BL` | ✓ | 1 |
| `corner:BR` | ✓ | 1 |
| `corner:TL` | ✓ | 1 |
| `corner:TR` | ✓ | 1 |
| `decomp:area_composite:additive` | ✓ | 1 |
| `decomp:area_composite:subtractive` | ✓ | 1 |
| `dim:area` | ✓ | 6 |
| `dim:length` | ✓ | 10 |
| `hidden:base` | ✓ | 1 |
| `hidden:height` | ✓ | 2 |
| `hidden:width` | ✓ | 3 |
| `kind:rectangle` | ✓ | 8 |
| `kind:rectilinear_composite` | ✓ | 4 |
| `kind:triangle_base_height` | ✓ | 4 |
| `num:integer` | ✓ | 15 |
| `num:rational` | ✓ | 1 |
| `orient:landscape` | ✓ | 5 |
| `orient:portrait` | ✓ | 2 |
| `orient:square` | ✓ | 1 |
| `task:area_composite` | ✓ | 2 |
| `task:area_rectangle` | ✓ | 2 |
| `task:area_triangle` | ✓ | 2 |
| `task:missing_dimension_area` | ✓ | 2 |
| `task:missing_length_perimeter` | ✓ | 2 |
| `task:missing_triangle_base_height` | ✓ | 2 |
| `task:perimeter_composite` | ✓ | 2 |
| `task:perimeter_rectangle` | ✓ | 2 |
| `unit:cm` | ✓ | 3 |
| `unit:m` | ✓ | 6 |
| `unit:mm` | ✓ | 7 |

## Quantity-checker review matrix (seed 6, answer `27/2 cm^2`)

| scenario | student response | expected | actual | genuinely different | ok |
| --- | --- | --- | --- | --- | --- |
| canonical form | `27/2 cm^2` | `correct` | `correct` | — | ✓ |
| no-space unit form | `27/2cm^2` | `correct` | `correct` | yes | ✓ |
| extra-space form | `27/2  cm^2` | `correct` | `correct` | yes | ✓ |
| unreduced fraction form | `54/4 cm^2` | `correct` | `correct` | yes | ✓ |
| terminating decimal form | `13.5 cm^2` | `correct` | `correct` | yes | ✓ |
| Unicode superscript form | `27/2 cm²` | `correct` | `correct` | yes | ✓ |
| bare number (no unit) | `27/2` | `missing-unit` | `missing-unit` | — | ✓ |
| wrong base unit (no conversion) | `27/2 m^2` | `wrong-base-unit` | `wrong-base-unit` | — | ✓ |
| incorrect value, correct unit | `29/2 cm^2` | `incorrect-value` | `incorrect-value` | — | ✓ |
| linear units for an area | `27/2 cm` | `wrong-exponent` | `wrong-exponent` | — | ✓ |
| different dimensional quantity | `27/2 m` | `wrong-dimension` | `wrong-dimension` | — | ✓ |
| scientific notation | `27/2e2 cm^2` | `malformed-response` | `malformed-response` | — | ✓ |
| trailing unparsed text | `27/2 cm^2 long` | `malformed-response` | `malformed-response` | — | ✓ |
| conflicting unit tokens | `27/2 cm m` | `malformed-response` | `malformed-response` | — | ✓ |
| malformed fraction | `27/ cm^2` | `malformed-response` | `malformed-response` | — | ✓ |
| malformed exponent | `27/2 cm^3` | `malformed-response` | `malformed-response` | — | ✓ |
| unsupported compound unit | `27/2 cm/s` | `malformed-response` | `malformed-response` | — | ✓ |
| empty response | `` | `malformed-response` | `malformed-response` | — | ✓ |
| multiple numerical expressions | `27/2 cm^2 27/2 cm^2` | `malformed-response` | `malformed-response` | — | ✓ |

### Cross-unit non-conversion proofs

| scenario | response | expected | actual |
| --- | --- | --- | --- |
| 100 cm must not be accepted for 1 m | `100 cm` | `wrong-base-unit` | `wrong-base-unit` |
| 10000 cm^2 must not be accepted for 1 m^2 | `10000 cm^2` | `wrong-base-unit` | `wrong-base-unit` |

## Selected items

### area_composite — seed 1 — band 3 — SPI.MIDDLE.MEAS.AREA.COMPOSITE_DECOMPOSITION.01
- Prompt: Work out the area of the shape shown by splitting it into rectangles. Give your answer in the correct square units.
- Answer: **45 m^2** (measure: area m^2); decomposition: **additive**
- Not to scale: False
- Worked solution: 1. Split into two rectangles: 8 × 3 and 3 × 7 | 2. Find each rectangle's area: 8 × 3 = 24 and 3 × 7 = 21 | 3. Add the two rectangle areas: 24 + 21 = 45 m^2
- Diagnostics: MISC.MENS.SUBTRACTS_WRONG_RECTANGLE→`59 m^2`(incorrect-value), MISC.MENS.ADDS_DIMS_FOR_AREA→`18 m^2`(incorrect-value), MISC.MENS.USES_PERIMETER_FOR_AREA→`36 m^2`(incorrect-value), MISC.MENS.LINEAR_UNITS_FOR_AREA→`45 m`(wrong-exponent), MISC.MENS.RIGHT_NUMBER_NO_UNIT→`45`(missing-unit)
- Validation: **pass** (22 checks pass)
- Reproduce: `python -c "import sys;sys.path.insert(0,'oracle/spi_oracle');import mensuration as m;print(m.serialize(m.generate(1,task='area_composite')))"`

### missing_length_perimeter — seed 4 — band 2 — SPI.MIDDLE.MEAS.PERIM.MISSING_LENGTH.01
- Prompt: This rectangle has a perimeter of 24 mm. Work out the missing side length marked “?”. Give your answer in the correct units.
- Answer: **4 mm** (measure: length mm^1)
- Not to scale: True
- Worked solution: 1. Halve the perimeter to get length + width: 24 ÷ 2 = 12 | 2. Subtract the known side: 12 − 8 = 4 mm
- Diagnostics: MISC.MENS.SQUARE_UNITS_FOR_PERIMETER→`4 mm^2`(wrong-exponent), MISC.MENS.WRONG_BASE_UNIT→`4 cm`(wrong-base-unit), MISC.MENS.RIGHT_NUMBER_NO_UNIT→`4`(missing-unit)
- Validation: **pass** (23 checks pass)
- Reproduce: `python -c "import sys;sys.path.insert(0,'oracle/spi_oracle');import mensuration as m;print(m.serialize(m.generate(4,task='missing_length_perimeter')))"`

### area_triangle — seed 6 — band 2 — SPI.MIDDLE.MEAS.AREA.TRIANGLE_BASE_HEIGHT.01
- Prompt: Work out the area of the triangle using its base and the perpendicular height shown. Give your answer in the correct square units.
- Answer: **27/2 cm^2** (measure: area cm^2)
- Not to scale: False
- Worked solution: 1. Multiply base by perpendicular height: 3 × 9 = 27 | 2. Halve the product (½ × base × height): 27/2 cm^2
- Diagnostics: MISC.MENS.FORGETS_TO_HALVE→`27 cm^2`(incorrect-value), MISC.MENS.USES_SLOPING_SIDE(pedagogical-only), MISC.MENS.LINEAR_UNITS_FOR_AREA→`27/2 cm`(wrong-exponent), MISC.MENS.RIGHT_NUMBER_NO_UNIT→`27/2`(missing-unit)
- Validation: **pass** (20 checks pass)
- Reproduce: `python -c "import sys;sys.path.insert(0,'oracle/spi_oracle');import mensuration as m;print(m.serialize(m.generate(6,task='area_triangle')))"`

### missing_dimension_area — seed 1 — band 2 — SPI.MIDDLE.MEAS.AREA.MISSING_DIMENSION.01
- Prompt: This rectangle has an area of 24 m^2. Work out the missing side length marked “?”. Give your answer in the correct units.
- Answer: **3 m** (measure: length m^1)
- Not to scale: True
- Worked solution: 1. Divide the area by the known side: 24 ÷ 8 = 3 m
- Diagnostics: MISC.MENS.SQUARE_UNITS_FOR_PERIMETER→`3 m^2`(wrong-exponent), MISC.MENS.WRONG_BASE_UNIT→`3 cm`(wrong-base-unit), MISC.MENS.RIGHT_NUMBER_NO_UNIT→`3`(missing-unit)
- Validation: **pass** (23 checks pass)
- Reproduce: `python -c "import sys;sys.path.insert(0,'oracle/spi_oracle');import mensuration as m;print(m.serialize(m.generate(1,task='missing_dimension_area')))"`

### perimeter_composite — seed 2 — band 2 — SPI.MIDDLE.MEAS.PERIM.COMPOSITE_RECTILINEAR.01
- Prompt: Work out the perimeter of the shape shown by adding the lengths around its outside. Give your answer in the correct units.
- Answer: **38 cm** (measure: length cm^1)
- Not to scale: False
- Worked solution: 1. Find the missing horizontal length: 11 − 5 = 6 cm | 2. Find the missing vertical length: 8 − 5 = 3 cm | 3. Trace the outside boundary, adding every exterior edge once (no inside lines): 6 + 5 + 5 + 3 + 11 + 8 = 38 cm
- Diagnostics: MISC.MENS.OMITS_INDENTED_EDGE→`33 cm`(incorrect-value), MISC.MENS.COUNTS_INTERNAL_EDGE→`44 cm`(incorrect-value), MISC.MENS.USES_AREA_FOR_PERIMETER→`63 cm`(incorrect-value), MISC.MENS.SQUARE_UNITS_FOR_PERIMETER→`38 cm^2`(wrong-exponent), MISC.MENS.RIGHT_NUMBER_NO_UNIT→`38`(missing-unit)
- Validation: **pass** (26 checks pass)
- Reproduce: `python -c "import sys;sys.path.insert(0,'oracle/spi_oracle');import mensuration as m;print(m.serialize(m.generate(2,task='perimeter_composite')))"`

### area_rectangle — seed 20 — band 1 — SPI.MIDDLE.MEAS.AREA.RECTANGLE.01
- Prompt: Work out the area of the rectangle shown. Give your answer in the correct square units.
- Answer: **81 mm^2** (measure: area mm^2)
- Not to scale: False
- Worked solution: 1. Multiply length by width: 9 × 9 | 2. State the area in square units: 81 mm^2
- Diagnostics: MISC.MENS.ADDS_DIMS_FOR_AREA→`18 mm^2`(incorrect-value), MISC.MENS.USES_PERIMETER_FOR_AREA→`36 mm^2`(incorrect-value), MISC.MENS.LINEAR_UNITS_FOR_AREA→`81 mm`(wrong-exponent), MISC.MENS.WRONG_BASE_UNIT→`81 cm^2`(wrong-base-unit), MISC.MENS.RIGHT_NUMBER_NO_UNIT→`81`(missing-unit)
- Validation: **pass** (19 checks pass)
- Reproduce: `python -c "import sys;sys.path.insert(0,'oracle/spi_oracle');import mensuration as m;print(m.serialize(m.generate(20,task='area_rectangle')))"`

### area_composite — seed 6 — band 4 — SPI.MIDDLE.MEAS.AREA.COMPOSITE_DECOMPOSITION.01
- Prompt: Work out the area of the shape shown by splitting it into rectangles. Give your answer in the correct square units.
- Answer: **78 m^2** (measure: area m^2); decomposition: **subtractive**
- Not to scale: False
- Worked solution: 1. Area of the surrounding rectangle: 8 × 11 = 88 | 2. Area of the missing corner rectangle: 2 × 5 = 10 | 3. Subtract the missing rectangle from the surrounding rectangle: 88 − 10 = 78 m^2
- Diagnostics: MISC.MENS.SUBTRACTS_WRONG_RECTANGLE→`58 m^2`(incorrect-value), MISC.MENS.ADDS_DIMS_FOR_AREA→`19 m^2`(incorrect-value), MISC.MENS.USES_PERIMETER_FOR_AREA→`38 m^2`(incorrect-value), MISC.MENS.LINEAR_UNITS_FOR_AREA→`78 m`(wrong-exponent), MISC.MENS.RIGHT_NUMBER_NO_UNIT→`78`(missing-unit)
- Validation: **pass** (22 checks pass)
- Reproduce: `python -c "import sys;sys.path.insert(0,'oracle/spi_oracle');import mensuration as m;print(m.serialize(m.generate(6,task='area_composite')))"`

### missing_triangle_base_height — seed 1 — band 3 — SPI.MIDDLE.MEAS.AREA.TRIANGLE_MISSING_BASE_HEIGHT.01
- Prompt: This triangle has an area of 12 mm^2. Work out the missing measurement marked “?”. Give your answer in the correct units.
- Answer: **3 mm** (measure: length mm^1)
- Not to scale: True
- Worked solution: 1. Double the area (undo the ½): 2 × 12 = 24 | 2. Divide by the known measurement: 24 ÷ 8 = 3 mm
- Diagnostics: MISC.MENS.FORGETS_TO_HALVE→`3/2 mm`(incorrect-value), MISC.MENS.USES_SLOPING_SIDE(pedagogical-only), MISC.MENS.SQUARE_UNITS_FOR_PERIMETER→`3 mm^2`(wrong-exponent), MISC.MENS.RIGHT_NUMBER_NO_UNIT→`3`(missing-unit)
- Validation: **pass** (24 checks pass)
- Reproduce: `python -c "import sys;sys.path.insert(0,'oracle/spi_oracle');import mensuration as m;print(m.serialize(m.generate(1,task='missing_triangle_base_height')))"`

### perimeter_rectangle — seed 1 — band 1 — SPI.MIDDLE.MEAS.PERIM.RECTANGLE.01
- Prompt: Work out the perimeter of the rectangle shown. Give your answer in the correct units.
- Answer: **22 m** (measure: length m^1)
- Not to scale: False
- Worked solution: 1. Add the four side lengths: 3 + 8 + 3 + 8 m | 2. Or use 2 × (length + width): 2 × (3 + 8) = 22 m
- Diagnostics: MISC.MENS.ADDS_TWO_SIDES_RECT→`11 m`(incorrect-value), MISC.MENS.USES_AREA_FOR_PERIMETER→`24 m`(incorrect-value), MISC.MENS.SQUARE_UNITS_FOR_PERIMETER→`22 m^2`(wrong-exponent), MISC.MENS.WRONG_BASE_UNIT→`22 cm`(wrong-base-unit), MISC.MENS.RIGHT_NUMBER_NO_UNIT→`22`(missing-unit)
- Validation: **pass** (19 checks pass)
- Reproduce: `python -c "import sys;sys.path.insert(0,'oracle/spi_oracle');import mensuration as m;print(m.serialize(m.generate(1,task='perimeter_rectangle')))"`

### perimeter_composite — seed 21 — band 3 — SPI.MIDDLE.MEAS.PERIM.COMPOSITE_RECTILINEAR.01
- Prompt: Work out the perimeter of the shape shown by adding the lengths around its outside. Give your answer in the correct units.
- Answer: **40 m** (measure: length m^1)
- Not to scale: False
- Worked solution: 1. Find the missing horizontal length: 12 − 5 = 7 m | 2. Find the missing vertical length: 8 − 3 = 5 m | 3. Trace the outside boundary, adding every exterior edge once (no inside lines): 7 + 8 + 12 + 5 + 5 + 3 = 40 m
- Diagnostics: MISC.MENS.OMITS_INDENTED_EDGE→`35 m`(incorrect-value), MISC.MENS.COUNTS_INTERNAL_EDGE→`47 m`(incorrect-value), MISC.MENS.USES_AREA_FOR_PERIMETER→`81 m`(incorrect-value), MISC.MENS.SQUARE_UNITS_FOR_PERIMETER→`40 m^2`(wrong-exponent), MISC.MENS.RIGHT_NUMBER_NO_UNIT→`40`(missing-unit)
- Validation: **pass** (26 checks pass)
- Reproduce: `python -c "import sys;sys.path.insert(0,'oracle/spi_oracle');import mensuration as m;print(m.serialize(m.generate(21,task='perimeter_composite')))"`

### perimeter_rectangle — seed 9 — band 2 — SPI.MIDDLE.MEAS.PERIM.RECTANGLE.01
- Prompt: Work out the perimeter of the rectangle shown. Give your answer in the correct units.
- Answer: **50 mm** (measure: length mm^1)
- Not to scale: False
- Worked solution: 1. Add the four side lengths: 15 + 10 + 15 + 10 mm | 2. Or use 2 × (length + width): 2 × (15 + 10) = 50 mm
- Diagnostics: MISC.MENS.ADDS_TWO_SIDES_RECT→`25 mm`(incorrect-value), MISC.MENS.USES_AREA_FOR_PERIMETER→`150 mm`(incorrect-value), MISC.MENS.SQUARE_UNITS_FOR_PERIMETER→`50 mm^2`(wrong-exponent), MISC.MENS.WRONG_BASE_UNIT→`50 cm`(wrong-base-unit), MISC.MENS.RIGHT_NUMBER_NO_UNIT→`50`(missing-unit)
- Validation: **pass** (19 checks pass)
- Reproduce: `python -c "import sys;sys.path.insert(0,'oracle/spi_oracle');import mensuration as m;print(m.serialize(m.generate(9,task='perimeter_rectangle')))"`

### area_rectangle — seed 9 — band 2 — SPI.MIDDLE.MEAS.AREA.RECTANGLE.01
- Prompt: Work out the area of the rectangle shown. Give your answer in the correct square units.
- Answer: **140 mm^2** (measure: area mm^2)
- Not to scale: False
- Worked solution: 1. Multiply length by width: 14 × 10 | 2. State the area in square units: 140 mm^2
- Diagnostics: MISC.MENS.ADDS_DIMS_FOR_AREA→`24 mm^2`(incorrect-value), MISC.MENS.USES_PERIMETER_FOR_AREA→`48 mm^2`(incorrect-value), MISC.MENS.LINEAR_UNITS_FOR_AREA→`140 mm`(wrong-exponent), MISC.MENS.WRONG_BASE_UNIT→`140 cm^2`(wrong-base-unit), MISC.MENS.RIGHT_NUMBER_NO_UNIT→`140`(missing-unit)
- Validation: **pass** (19 checks pass)
- Reproduce: `python -c "import sys;sys.path.insert(0,'oracle/spi_oracle');import mensuration as m;print(m.serialize(m.generate(9,task='area_rectangle')))"`

### area_triangle — seed 5 — band 3 — SPI.MIDDLE.MEAS.AREA.TRIANGLE_BASE_HEIGHT.01
- Prompt: Work out the area of the triangle using its base and the perpendicular height shown. Give your answer in the correct square units.
- Answer: **60 m^2** (measure: area m^2)
- Not to scale: False
- Worked solution: 1. Multiply base by perpendicular height: 12 × 10 = 120 | 2. Halve the product (½ × base × height): 60 m^2
- Diagnostics: MISC.MENS.FORGETS_TO_HALVE→`120 m^2`(incorrect-value), MISC.MENS.USES_SLOPING_SIDE(pedagogical-only), MISC.MENS.LINEAR_UNITS_FOR_AREA→`60 m`(wrong-exponent), MISC.MENS.RIGHT_NUMBER_NO_UNIT→`60`(missing-unit)
- Validation: **pass** (20 checks pass)
- Reproduce: `python -c "import sys;sys.path.insert(0,'oracle/spi_oracle');import mensuration as m;print(m.serialize(m.generate(5,task='area_triangle')))"`

### missing_length_perimeter — seed 5 — band 3 — SPI.MIDDLE.MEAS.PERIM.MISSING_LENGTH.01
- Prompt: This rectangle has a perimeter of 38 mm. Work out the missing side length marked “?”. Give your answer in the correct units.
- Answer: **15 mm** (measure: length mm^1)
- Not to scale: True
- Worked solution: 1. Halve the perimeter to get length + width: 38 ÷ 2 = 19 | 2. Subtract the known side: 19 − 4 = 15 mm
- Diagnostics: MISC.MENS.SQUARE_UNITS_FOR_PERIMETER→`15 mm^2`(wrong-exponent), MISC.MENS.WRONG_BASE_UNIT→`15 cm`(wrong-base-unit), MISC.MENS.RIGHT_NUMBER_NO_UNIT→`15`(missing-unit)
- Validation: **pass** (23 checks pass)
- Reproduce: `python -c "import sys;sys.path.insert(0,'oracle/spi_oracle');import mensuration as m;print(m.serialize(m.generate(5,task='missing_length_perimeter')))"`

### missing_dimension_area — seed 5 — band 3 — SPI.MIDDLE.MEAS.AREA.MISSING_DIMENSION.01
- Prompt: This rectangle has an area of 60 mm^2. Work out the missing side length marked “?”. Give your answer in the correct units.
- Answer: **15 mm** (measure: length mm^1)
- Not to scale: True
- Worked solution: 1. Divide the area by the known side: 60 ÷ 4 = 15 mm
- Diagnostics: MISC.MENS.SQUARE_UNITS_FOR_PERIMETER→`15 mm^2`(wrong-exponent), MISC.MENS.WRONG_BASE_UNIT→`15 cm`(wrong-base-unit), MISC.MENS.RIGHT_NUMBER_NO_UNIT→`15`(missing-unit)
- Validation: **pass** (23 checks pass)
- Reproduce: `python -c "import sys;sys.path.insert(0,'oracle/spi_oracle');import mensuration as m;print(m.serialize(m.generate(5,task='missing_dimension_area')))"`

### missing_triangle_base_height — seed 10 — band 4 — SPI.MIDDLE.MEAS.AREA.TRIANGLE_MISSING_BASE_HEIGHT.01
- Prompt: This triangle has an area of 85 cm^2. Work out the missing measurement marked “?”. Give your answer in the correct units.
- Answer: **10 cm** (measure: length cm^1)
- Not to scale: True
- Worked solution: 1. Double the area (undo the ½): 2 × 85 = 170 | 2. Divide by the known measurement: 170 ÷ 17 = 10 cm
- Diagnostics: MISC.MENS.FORGETS_TO_HALVE→`5 cm`(incorrect-value), MISC.MENS.USES_SLOPING_SIDE(pedagogical-only), MISC.MENS.SQUARE_UNITS_FOR_PERIMETER→`10 cm^2`(wrong-exponent), MISC.MENS.RIGHT_NUMBER_NO_UNIT→`10`(missing-unit)
- Validation: **pass** (24 checks pass)
- Reproduce: `python -c "import sys;sys.path.insert(0,'oracle/spi_oracle');import mensuration as m;print(m.serialize(m.generate(10,task='missing_triangle_base_height')))"`
