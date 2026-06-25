# Review pack — gen.measurement.mensuration v1.0.0

> PENDING-REVIEW. Free-response only. Required coverage cells are **derived from the distribution report** (every task × supported interaction × reachable band × realised answer shape × base unit × shape kind × decomposition mode × hidden role). The builder fails on any missing reachable cell.

- Required cells: **46**; covered: **46**; full coverage: **True**; all items machine-valid: **True**.
- Items selected (minimal set-cover): **17**.
- Feature proofs: student-vs-answer-key base geometry identical = **True**; answer absent from every student figure = **True**; NOT-TO-SCALE banner on hidden-dimension items = **True**.
- Render modes / 6000×4200 export / label-collision / student-beside-key: see the visual audit.

## Coverage matrix

| cell | covered | #items |
| --- | --- | --- |
| `band:area_composite:3` | ✓ | 1 |
| `band:area_composite:4` | ✓ | 1 |
| `band:area_rectangle:1` | ✓ | 2 |
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
| `decomp:additive` | ✓ | 2 |
| `decomp:subtractive` | ✓ | 2 |
| `dim:area` | ✓ | 7 |
| `dim:length` | ✓ | 10 |
| `hidden:base` | ✓ | 1 |
| `hidden:height` | ✓ | 2 |
| `hidden:width` | ✓ | 3 |
| `kind:rectangle` | ✓ | 9 |
| `kind:rectilinear_composite` | ✓ | 4 |
| `kind:triangle_base_height` | ✓ | 4 |
| `num:integer` | ✓ | 16 |
| `num:rational` | ✓ | 1 |
| `orient:landscape` | ✓ | 5 |
| `orient:portrait` | ✓ | 3 |
| `orient:square` | ✓ | 1 |
| `task:area_composite` | ✓ | 2 |
| `task:area_rectangle` | ✓ | 3 |
| `task:area_triangle` | ✓ | 2 |
| `task:missing_dimension_area` | ✓ | 2 |
| `task:missing_length_perimeter` | ✓ | 2 |
| `task:missing_triangle_base_height` | ✓ | 2 |
| `task:perimeter_composite` | ✓ | 2 |
| `task:perimeter_rectangle` | ✓ | 2 |
| `unit:cm` | ✓ | 5 |
| `unit:m` | ✓ | 5 |
| `unit:mm` | ✓ | 7 |

## Quantity-checker review matrix (representative)

| scenario | student response | expected | actual | ok |
| --- | --- | --- | --- | --- |
| equivalent value + correct unit | `36 m` | `correct` | `correct` | ✓ |
| bare correct value (no unit) | `36` | `missing-unit` | `missing-unit` | ✓ |
| wrong base unit (no conversion) | `36 cm` | `wrong-base-unit` | `wrong-base-unit` | ✓ |
| incorrect value + correct unit | `37 m` | `incorrect-value` | `incorrect-value` | ✓ |
| square units for a length | `36 m^2` | `wrong-exponent` | `wrong-exponent` | ✓ |
| different dimensional quantity | `36 cm^2` | `wrong-dimension` | `wrong-dimension` | ✓ |

## Selected items

### perimeter_composite — seed 1 — band 2 — SPI.MIDDLE.MEAS.PERIM.COMPOSITE_RECTILINEAR.01
- Prompt: Work out the perimeter of the shape shown by adding the lengths around its outside. Give your answer in the correct units.
- Answer: **36 m** (measure: length m^1)
- Not to scale: False
- Worked solution: 1. Find any unlabelled outer edge from the given lengths: use width − part and height − part | 2. Add every edge around the outside once (no inside lines): 36 m
- Diagnostics: MISC.MENS.OMITS_INDENTED_EDGE→`31 m`(incorrect-value), MISC.MENS.COUNTS_INTERNAL_EDGE→`39 m`(incorrect-value), MISC.MENS.USES_AREA_FOR_PERIMETER→`45 m`(incorrect-value), MISC.MENS.SQUARE_UNITS_FOR_PERIMETER→`36 m^2`(wrong-exponent), MISC.MENS.RIGHT_NUMBER_NO_UNIT→`36`(missing-unit)
- Validation: **pass** (21 checks pass)
- Reproduce: `python -c "import sys;sys.path.insert(0,'oracle/spi_oracle');import mensuration as m;print(m.serialize(m.generate(1,task='perimeter_composite')))"`

### area_rectangle — seed 2 — band 1 — SPI.MIDDLE.MEAS.AREA.RECTANGLE.01
- Prompt: Work out the area of the rectangle shown. Give your answer in the correct square units.
- Answer: **40 cm^2** (measure: area cm^2)
- Not to scale: False
- Worked solution: 1. Multiply length by width: 8 × 5 | 2. State the area in square units: 40 cm^2
- Diagnostics: MISC.MENS.ADDS_DIMS_FOR_AREA→`13 cm^2`(incorrect-value), MISC.MENS.USES_PERIMETER_FOR_AREA→`26 cm^2`(incorrect-value), MISC.MENS.LINEAR_UNITS_FOR_AREA→`40 cm`(wrong-exponent), MISC.MENS.WRONG_BASE_UNIT→`40 m^2`(wrong-base-unit), MISC.MENS.RIGHT_NUMBER_NO_UNIT→`40`(missing-unit)
- Validation: **pass** (19 checks pass)
- Reproduce: `python -c "import sys;sys.path.insert(0,'oracle/spi_oracle');import mensuration as m;print(m.serialize(m.generate(2,task='area_rectangle')))"`

### area_triangle — seed 34 — band 3 — SPI.MIDDLE.MEAS.AREA.TRIANGLE_BASE_HEIGHT.01
- Prompt: Work out the area of the triangle using its base and the perpendicular height shown. Give your answer in the correct square units.
- Answer: **105/2 mm^2** (measure: area mm^2)
- Not to scale: False
- Worked solution: 1. Multiply base by perpendicular height: 15 × 7 = 105 | 2. Halve the product (½ × base × height): 105/2 mm^2
- Diagnostics: MISC.MENS.FORGETS_TO_HALVE→`105 mm^2`(incorrect-value), MISC.MENS.USES_SLOPING_SIDE→`None`(None), MISC.MENS.LINEAR_UNITS_FOR_AREA→`105/2 mm`(wrong-exponent), MISC.MENS.RIGHT_NUMBER_NO_UNIT→`105/2`(missing-unit)
- Validation: **pass** (20 checks pass)
- Reproduce: `python -c "import sys;sys.path.insert(0,'oracle/spi_oracle');import mensuration as m;print(m.serialize(m.generate(34,task='area_triangle')))"`

### area_composite — seed 2 — band 4 — SPI.MIDDLE.MEAS.AREA.COMPOSITE_DECOMPOSITION.01
- Prompt: Work out the area of the shape shown by splitting it into rectangles. Give your answer in the correct square units.
- Answer: **63 cm^2** (measure: area cm^2)
- Not to scale: False
- Worked solution: 1. Area of the surrounding rectangle: 11 × 8 = 88 | 2. Subtract the missing corner rectangle: 88 − 5 × 5 = 63 cm^2
- Diagnostics: MISC.MENS.SUBTRACTS_WRONG_RECTANGLE→`58 cm^2`(incorrect-value), MISC.MENS.ADDS_DIMS_FOR_AREA→`19 cm^2`(incorrect-value), MISC.MENS.USES_PERIMETER_FOR_AREA→`38 cm^2`(incorrect-value), MISC.MENS.LINEAR_UNITS_FOR_AREA→`63 cm`(wrong-exponent), MISC.MENS.RIGHT_NUMBER_NO_UNIT→`63`(missing-unit)
- Validation: **pass** (21 checks pass)
- Reproduce: `python -c "import sys;sys.path.insert(0,'oracle/spi_oracle');import mensuration as m;print(m.serialize(m.generate(2,task='area_composite')))"`

### missing_length_perimeter — seed 1 — band 2 — SPI.MIDDLE.MEAS.PERIM.MISSING_LENGTH.01
- Prompt: The perimeter of this rectangle is 22 m. The perimeter of the rectangle is given. Work out the missing side length marked “?”. Give your answer in the correct units.
- Answer: **3 m** (measure: length m^1)
- Not to scale: True
- Worked solution: 1. Halve the perimeter to get length + width: 22 ÷ 2 = 11 | 2. Subtract the known side: 11 − 8 = 3 m
- Diagnostics: MISC.MENS.USES_AREA_FOR_PERIMETER→`None`(incorrect-value), MISC.MENS.SQUARE_UNITS_FOR_PERIMETER→`3 m^2`(wrong-exponent), MISC.MENS.WRONG_BASE_UNIT→`3 cm`(wrong-base-unit), MISC.MENS.RIGHT_NUMBER_NO_UNIT→`3`(missing-unit)
- Validation: **pass** (23 checks pass)
- Reproduce: `python -c "import sys;sys.path.insert(0,'oracle/spi_oracle');import mensuration as m;print(m.serialize(m.generate(1,task='missing_length_perimeter')))"`

### missing_dimension_area — seed 3 — band 2 — SPI.MIDDLE.MEAS.AREA.MISSING_DIMENSION.01
- Prompt: The area of this rectangle is 21 m^2. The area of the rectangle is given. Work out the missing side length marked “?”. Give your answer in the correct units.
- Answer: **7 m** (measure: length m^1)
- Not to scale: True
- Worked solution: 1. Divide the area by the known side: 21 ÷ 3 = 7 m
- Diagnostics: MISC.MENS.USES_PERIMETER_FOR_AREA→`None`(incorrect-value), MISC.MENS.SQUARE_UNITS_FOR_PERIMETER→`7 m^2`(wrong-exponent), MISC.MENS.WRONG_BASE_UNIT→`7 cm`(wrong-base-unit), MISC.MENS.RIGHT_NUMBER_NO_UNIT→`7`(missing-unit)
- Validation: **pass** (23 checks pass)
- Reproduce: `python -c "import sys;sys.path.insert(0,'oracle/spi_oracle');import mensuration as m;print(m.serialize(m.generate(3,task='missing_dimension_area')))"`

### missing_triangle_base_height — seed 1 — band 3 — SPI.MIDDLE.MEAS.AREA.TRIANGLE_MISSING_BASE_HEIGHT.01
- Prompt: The area of this triangle is 12 mm^2. The area of the triangle is given. Work out the missing measurement marked “?”. Give your answer in the correct units.
- Answer: **3 mm** (measure: length mm^1)
- Not to scale: True
- Worked solution: 1. Double the area (undo the ½): 2 × 12 = 24 | 2. Divide by the known measurement: 24 ÷ 8 = 3 mm
- Diagnostics: MISC.MENS.FORGETS_TO_HALVE→`3/2 mm`(incorrect-value), MISC.MENS.USES_SLOPING_SIDE→`None`(None), MISC.MENS.SQUARE_UNITS_FOR_PERIMETER→`3 mm^2`(wrong-exponent), MISC.MENS.RIGHT_NUMBER_NO_UNIT→`3`(missing-unit)
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

### perimeter_composite — seed 16 — band 3 — SPI.MIDDLE.MEAS.PERIM.COMPOSITE_RECTILINEAR.01
- Prompt: Work out the perimeter of the shape shown by adding the lengths around its outside. Give your answer in the correct units.
- Answer: **42 cm** (measure: length cm^1)
- Not to scale: False
- Worked solution: 1. Find any unlabelled outer edge from the given lengths: use width − part and height − part | 2. Add every edge around the outside once (no inside lines): 42 cm
- Diagnostics: MISC.MENS.OMITS_INDENTED_EDGE→`39 cm`(incorrect-value), MISC.MENS.COUNTS_INTERNAL_EDGE→`48 cm`(incorrect-value), MISC.MENS.USES_AREA_FOR_PERIMETER→`96 cm`(incorrect-value), MISC.MENS.SQUARE_UNITS_FOR_PERIMETER→`42 cm^2`(wrong-exponent), MISC.MENS.RIGHT_NUMBER_NO_UNIT→`42`(missing-unit)
- Validation: **pass** (21 checks pass)
- Reproduce: `python -c "import sys;sys.path.insert(0,'oracle/spi_oracle');import mensuration as m;print(m.serialize(m.generate(16,task='perimeter_composite')))"`

### area_composite — seed 17 — band 3 — SPI.MIDDLE.MEAS.AREA.COMPOSITE_DECOMPOSITION.01
- Prompt: Work out the area of the shape shown by splitting it into rectangles. Give your answer in the correct square units.
- Answer: **96 cm^2** (measure: area cm^2)
- Not to scale: False
- Worked solution: 1. Area of the surrounding rectangle: 10 × 10 = 100 | 2. Subtract the missing corner rectangle: 100 − 2 × 2 = 96 cm^2
- Diagnostics: MISC.MENS.SUBTRACTS_WRONG_RECTANGLE→`84 cm^2`(incorrect-value), MISC.MENS.ADDS_DIMS_FOR_AREA→`20 cm^2`(incorrect-value), MISC.MENS.USES_PERIMETER_FOR_AREA→`40 cm^2`(incorrect-value), MISC.MENS.LINEAR_UNITS_FOR_AREA→`96 cm`(wrong-exponent), MISC.MENS.RIGHT_NUMBER_NO_UNIT→`96`(missing-unit)
- Validation: **pass** (21 checks pass)
- Reproduce: `python -c "import sys;sys.path.insert(0,'oracle/spi_oracle');import mensuration as m;print(m.serialize(m.generate(17,task='area_composite')))"`

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

### area_rectangle — seed 20 — band 1 — SPI.MIDDLE.MEAS.AREA.RECTANGLE.01
- Prompt: Work out the area of the rectangle shown. Give your answer in the correct square units.
- Answer: **81 mm^2** (measure: area mm^2)
- Not to scale: False
- Worked solution: 1. Multiply length by width: 9 × 9 | 2. State the area in square units: 81 mm^2
- Diagnostics: MISC.MENS.ADDS_DIMS_FOR_AREA→`18 mm^2`(incorrect-value), MISC.MENS.USES_PERIMETER_FOR_AREA→`36 mm^2`(incorrect-value), MISC.MENS.LINEAR_UNITS_FOR_AREA→`81 mm`(wrong-exponent), MISC.MENS.WRONG_BASE_UNIT→`81 cm^2`(wrong-base-unit), MISC.MENS.RIGHT_NUMBER_NO_UNIT→`81`(missing-unit)
- Validation: **pass** (19 checks pass)
- Reproduce: `python -c "import sys;sys.path.insert(0,'oracle/spi_oracle');import mensuration as m;print(m.serialize(m.generate(20,task='area_rectangle')))"`

### area_triangle — seed 1 — band 2 — SPI.MIDDLE.MEAS.AREA.TRIANGLE_BASE_HEIGHT.01
- Prompt: Work out the area of the triangle using its base and the perpendicular height shown. Give your answer in the correct square units.
- Answer: **12 m^2** (measure: area m^2)
- Not to scale: False
- Worked solution: 1. Multiply base by perpendicular height: 3 × 8 = 24 | 2. Halve the product (½ × base × height): 12 m^2
- Diagnostics: MISC.MENS.FORGETS_TO_HALVE→`24 m^2`(incorrect-value), MISC.MENS.USES_SLOPING_SIDE→`None`(None), MISC.MENS.LINEAR_UNITS_FOR_AREA→`12 m`(wrong-exponent), MISC.MENS.RIGHT_NUMBER_NO_UNIT→`12`(missing-unit)
- Validation: **pass** (20 checks pass)
- Reproduce: `python -c "import sys;sys.path.insert(0,'oracle/spi_oracle');import mensuration as m;print(m.serialize(m.generate(1,task='area_triangle')))"`

### missing_length_perimeter — seed 5 — band 3 — SPI.MIDDLE.MEAS.PERIM.MISSING_LENGTH.01
- Prompt: The perimeter of this rectangle is 38 mm. The perimeter of the rectangle is given. Work out the missing side length marked “?”. Give your answer in the correct units.
- Answer: **15 mm** (measure: length mm^1)
- Not to scale: True
- Worked solution: 1. Halve the perimeter to get length + width: 38 ÷ 2 = 19 | 2. Subtract the known side: 19 − 4 = 15 mm
- Diagnostics: MISC.MENS.USES_AREA_FOR_PERIMETER→`None`(incorrect-value), MISC.MENS.SQUARE_UNITS_FOR_PERIMETER→`15 mm^2`(wrong-exponent), MISC.MENS.WRONG_BASE_UNIT→`15 cm`(wrong-base-unit), MISC.MENS.RIGHT_NUMBER_NO_UNIT→`15`(missing-unit)
- Validation: **pass** (23 checks pass)
- Reproduce: `python -c "import sys;sys.path.insert(0,'oracle/spi_oracle');import mensuration as m;print(m.serialize(m.generate(5,task='missing_length_perimeter')))"`

### missing_dimension_area — seed 5 — band 3 — SPI.MIDDLE.MEAS.AREA.MISSING_DIMENSION.01
- Prompt: The area of this rectangle is 60 mm^2. The area of the rectangle is given. Work out the missing side length marked “?”. Give your answer in the correct units.
- Answer: **15 mm** (measure: length mm^1)
- Not to scale: True
- Worked solution: 1. Divide the area by the known side: 60 ÷ 4 = 15 mm
- Diagnostics: MISC.MENS.USES_PERIMETER_FOR_AREA→`None`(incorrect-value), MISC.MENS.SQUARE_UNITS_FOR_PERIMETER→`15 mm^2`(wrong-exponent), MISC.MENS.WRONG_BASE_UNIT→`15 cm`(wrong-base-unit), MISC.MENS.RIGHT_NUMBER_NO_UNIT→`15`(missing-unit)
- Validation: **pass** (23 checks pass)
- Reproduce: `python -c "import sys;sys.path.insert(0,'oracle/spi_oracle');import mensuration as m;print(m.serialize(m.generate(5,task='missing_dimension_area')))"`

### missing_triangle_base_height — seed 10 — band 4 — SPI.MIDDLE.MEAS.AREA.TRIANGLE_MISSING_BASE_HEIGHT.01
- Prompt: The area of this triangle is 85 cm^2. The area of the triangle is given. Work out the missing measurement marked “?”. Give your answer in the correct units.
- Answer: **10 cm** (measure: length cm^1)
- Not to scale: True
- Worked solution: 1. Double the area (undo the ½): 2 × 85 = 170 | 2. Divide by the known measurement: 170 ÷ 17 = 10 cm
- Diagnostics: MISC.MENS.FORGETS_TO_HALVE→`5 cm`(incorrect-value), MISC.MENS.USES_SLOPING_SIDE→`None`(None), MISC.MENS.SQUARE_UNITS_FOR_PERIMETER→`10 cm^2`(wrong-exponent), MISC.MENS.RIGHT_NUMBER_NO_UNIT→`10`(missing-unit)
- Validation: **pass** (24 checks pass)
- Reproduce: `python -c "import sys;sys.path.insert(0,'oracle/spi_oracle');import mensuration as m;print(m.serialize(m.generate(10,task='missing_triangle_base_height')))"`
