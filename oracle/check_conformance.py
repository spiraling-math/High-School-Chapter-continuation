"""Minimal JSON-Schema conformance checker (offline, dependency-free).

Supports the subset of JSON Schema used by the SPI-Math schemas:
required, type, enum, pattern, properties, additionalProperties (bool),
items, minItems, and $ref (local '#/...' and cross-file by $id).

This is a development aid that proves schema/instance agreement in the current
(no-Node) environment. The production TypeScript layer validates with Ajv.

Run:  python oracle/check_conformance.py
"""

from __future__ import annotations

import glob
import json
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
SCHEMA_DIR = os.path.join(ROOT, "schemas")

sys.path.insert(0, HERE)
from spi_oracle import sequences as seq  # noqa: E402
from spi_oracle import geometric as geo  # noqa: E402
from spi_oracle import linear_equations as lin  # noqa: E402
from spi_oracle import geometry as geoang  # noqa: E402
from spi_oracle import coordinate_lines as coord  # noqa: E402
from spi_oracle import data_handling as stats  # noqa: E402
from spi_oracle import transformations as trans  # noqa: E402

_TYPE = {
    "object": dict, "array": list, "string": str, "boolean": bool,
    "integer": int, "number": (int, float),
}


def load_registry() -> dict:
    reg = {}
    for path in glob.glob(os.path.join(SCHEMA_DIR, "*.json")):
        data = json.load(open(path, encoding="utf-8"))
        if "$id" in data:
            reg[data["$id"]] = data
    return reg


def resolve(ref: str, current: dict, registry: dict) -> dict:
    base, _, pointer = ref.partition("#")
    doc = registry.get(base, current) if base else current
    node = doc
    for part in pointer.split("/"):
        if part == "":
            continue
        part = part.replace("~1", "/").replace("~0", "~")
        node = node[part]
    return node


def _validates(instance, schema, registry, root) -> bool:
    """True iff instance validates against schema (used silently by if/then)."""
    tmp: list = []
    check(instance, schema, registry, root, "$", tmp)
    return not tmp


def check(instance, schema, registry, root, path, errors):
    # Boolean schemas: true accepts anything, false rejects anything (e.g. `units: false`).
    if schema is True:
        return
    if schema is False:
        errors.append(f"{path}: property is forbidden here")
        return

    if "$ref" in schema:
        schema = resolve(schema["$ref"], root, registry)

    if "const" in schema and instance != schema["const"]:
        errors.append(f"{path}: value {instance!r} != const {schema['const']!r}")

    # Conditional + combinator keywords (owner B: the conformance checker must NOT silently
    # ignore the quantity answer's if/then/const rules).
    for sub in schema.get("allOf", []):
        check(instance, sub, registry, root, path, errors)
    if "if" in schema:
        branch = "then" if _validates(instance, schema["if"], registry, root) else "else"
        if branch in schema:
            check(instance, schema[branch], registry, root, path, errors)
    if "not" in schema and _validates(instance, schema["not"], registry, root):
        errors.append(f"{path}: must NOT match the forbidden subschema")

    t = schema.get("type")
    if t:
        types = t if isinstance(t, list) else [t]
        if not any(
            (py := _TYPE.get(tt)) and isinstance(instance, py)
            and not (tt in ("integer", "number") and isinstance(instance, bool))
            for tt in types
        ):
            errors.append(f"{path}: expected type {t}, got {type(instance).__name__}")
            return

    if "enum" in schema and instance not in schema["enum"]:
        errors.append(f"{path}: value {instance!r} not in enum")

    if "pattern" in schema and isinstance(instance, str):
        if not re.search(schema["pattern"], instance):
            errors.append(f"{path}: {instance!r} does not match pattern {schema['pattern']}")

    if isinstance(instance, dict):
        for req in schema.get("required", []):
            if req not in instance:
                errors.append(f"{path}: missing required field '{req}'")
        props = schema.get("properties", {})
        if schema.get("additionalProperties") is False:
            for key in instance:
                if key not in props:
                    errors.append(f"{path}: unexpected property '{key}'")
        for key, val in instance.items():
            if key in props:
                check(val, props[key], registry, root, f"{path}.{key}", errors)

    if isinstance(instance, list):
        if "minItems" in schema and len(instance) < schema["minItems"]:
            errors.append(f"{path}: needs >= {schema['minItems']} items")
        if "items" in schema:
            for i, el in enumerate(instance):
                check(el, schema["items"], registry, root, f"{path}[{i}]", errors)


def validate(instance, schema, registry, label) -> bool:
    errors: list = []
    check(instance, schema, registry, schema, label, errors)
    if errors:
        print(f"FAIL  {label}")
        for e in errors[:20]:
            print("        -", e)
        return False
    print(f"PASS  {label}")
    return True


def main() -> int:
    registry = load_registry()
    SID = "https://spi-math.academy/schemas/{}.schema.json".format
    ok = True

    # 1. Each schema's own embedded examples.
    for path in sorted(glob.glob(os.path.join(SCHEMA_DIR, "*.json"))):
        schema = json.load(open(path, encoding="utf-8"))
        name = os.path.basename(path)
        for i, ex in enumerate(schema.get("examples", [])):
            ok &= validate(ex, schema, registry, f"{name} example[{i}]")

    # 2. Curriculum objective data instances.
    obj_schema = registry[SID("curriculum-objective")]
    for path in glob.glob(os.path.join(ROOT, "curriculum", "objectives", "*.json")):
        for i, obj in enumerate(json.load(open(path, encoding="utf-8"))):
            ok &= validate(obj, obj_schema, registry, f"objective {obj['objectiveId']}")

    # 3. Misconception library instances.
    misc_schema = registry[SID("misconception")]
    for path in glob.glob(os.path.join(ROOT, "core", "misconceptions", "*.json")):
        for m in json.load(open(path, encoding="utf-8")):
            ok &= validate(m, misc_schema, registry, f"misconception {m['misconceptionId']}")

    # 4. Live generated items (the real proof: code output conforms to the item schema).
    item_schema = registry[SID("question-item")]
    for seed in (1, 42, 123456789):
        item = seq.generate(seed, {"answerType": "multiple-choice"})
        ok &= validate(item, item_schema, registry, f"generated item seed={seed} (MC)")
    item = seq.generate(7, {"answerType": "integer"})
    ok &= validate(item, item_schema, registry, "generated item seed=7 (integer)")

    # 4b. Live geometric items (exact-rational answers).
    for seed in (1, 42, 123456789):
        ok &= validate(geo.generate(seed, {"answerType": "multiple-choice"}), item_schema, registry, f"geometric item seed={seed} (MC)")
    ok &= validate(geo.generate(7, {"answerType": "integer"}), item_schema, registry, "geometric item seed=7 (free-response)")

    # 4c. Live linear-equations items (integer + exact-rational answers, all tasks).
    for seed in (1, 42, 123456789):
        ok &= validate(lin.generate(seed, {"answerType": "multiple-choice"}), item_schema, registry, f"linear item seed={seed} (MC)")
    ok &= validate(lin.generate(7, {"answerType": "integer"}), item_schema, registry, "linear item seed=7 (free-response)")
    for task in ("one_step_add", "one_step_mul", "two_step", "both_sides", "brackets"):
        ok &= validate(lin.generate(5, {"answerType": "multiple-choice", "task": task}), item_schema, registry, f"linear item task={task}")

    # 4d. Live geometry-angles items (SVG diagrams; all five tasks).
    for seed in (1, 42, 123456789):
        ok &= validate(geoang.generate(seed, {"interactionType": "multiple-choice"}), item_schema, registry, f"geometry item seed={seed} (MC)")
    for task in ("straight_line_missing_angle", "triangle_missing_angle", "isosceles_base_angle", "vertically_opposite_angle", "angles_at_point_missing"):
        mode = "free-response" if task == "vertically_opposite_angle" else "multiple-choice"
        ok &= validate(geoang.generate(5, {"interactionType": mode, "task": task}), item_schema, registry, f"geometry item task={task}")

    # 4e. Live coordinate-lines items (coordinate/ordered-pair/equation answers; 7 tasks).
    for seed in (1, 42, 123456789):
        ok &= validate(coord.generate(seed, {"interactionType": "multiple-choice"}), item_schema, registry, f"coordinate item seed={seed} (MC)")
    for task in coord.TASKS:
        mode = "free-response" if task == "plot_point" else "multiple-choice"
        ok &= validate(coord.generate(7, {"interactionType": mode, "task": task}), item_schema, registry, f"coordinate item task={task}")

    # 4f. Live stats data-handling items (charts + semantic tables; 11 tasks).
    for seed in (1, 42, 123456789):
        ok &= validate(stats.generate(seed, {"interactionType": "multiple-choice"}), item_schema, registry, f"stats item seed={seed} (MC)")
    for task in stats.TASKS:
        mode = "free-response" if task in stats.FREE_RESPONSE_ONLY else "multiple-choice"
        ok &= validate(stats.generate(7, {"interactionType": mode, "task": task}), item_schema, registry, f"stats item task={task}")

    # 4g. Live transformations items (coordinate / table-completion / transformation answers; 9 tasks).
    for task in trans.TASKS:
        ok &= validate(trans.generate(7, {"task": task}), item_schema, registry, f"transformation item task={task}")
    for seed in (1, 42, 123456789):
        ok &= validate(trans.generate(seed), item_schema, registry, f"transformation item seed={seed}")

    # 5. The generator descriptors.
    gen_schema = registry[SID("generator-module")]
    ok &= validate(seq.describe(), gen_schema, registry, "gen.sequences.arithmetic describe()")
    ok &= validate(geo.describe(), gen_schema, registry, "gen.sequences.geometric describe()")
    ok &= validate(lin.describe(), gen_schema, registry, "gen.algebra.linear-equations describe()")
    ok &= validate(geoang.describe(), gen_schema, registry, "gen.geometry.angles-figures describe()")

    print("\n" + ("ALL CONFORMANCE CHECKS PASSED" if ok else "CONFORMANCE FAILURES PRESENT"))
    return 0 if ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
