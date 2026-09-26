"""Materialise the MISC.FUNC.* registry as schema-shaped records.

Run:  python oracle/make_functions_misconceptions.py
Writes: core/misconceptions/functions.json (validated by oracle/check_conformance.py against
schemas/misconception.schema.json). The Python registry (oracle/spi_oracle/functions_misconceptions.py)
is the source of the titles/descriptions/rules; oracle/tests/test_functions.py asserts the JSON stays in
sync with it.
"""

from __future__ import annotations

import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, os.path.join(HERE, "spi_oracle"))

import functions_misconceptions as FM  # noqa: E402

OUT = os.path.join(ROOT, "core", "misconceptions", "functions.json")


def main() -> int:
    records = FM.registry_records()
    with open(OUT, "w", encoding="utf-8", newline="\n") as fh:
        json.dump(records, fh, indent=2, ensure_ascii=False)
        fh.write("\n")
    print(f"wrote {len(records)} misconception records -> core/misconceptions/functions.json")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
