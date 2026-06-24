"""Generation manifest for gen.stats.data-handling (owner decision O/P).

SHA-256 over every review/parity artifact, plus generator + validator versions and the
eleven approved objective IDs. A blocking artifact-integrity test asserts these hashes,
so a silent regeneration that changes any artifact fails CI.

Writes: docs/review/stats_data_handling_manifest.json
"""

from __future__ import annotations

import hashlib
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, os.path.join(HERE, "spi_oracle"))

from spi_oracle import data_handling as dh  # noqa: E402

REVIEW_DIR = os.path.join(ROOT, "docs", "review")

ARTIFACTS = {
    "golden": "oracle/golden/data_handling.golden.json",
    "parity": "oracle/golden/data_handling.parity.json",
    "distribution": "docs/review/stats_data_handling_distribution.json",
    "reviewPackJson": "docs/review/stats_data_handling_review_pack.json",
    "reviewPackMd": "docs/review/stats_data_handling_review_pack.md",
    "visualAudit": "docs/review/stats_data_handling_visual_audit.html",
    "browserVerification": "docs/review/stats_data_handling_browser_verification.json",
    "objectives": "curriculum/objectives/SPI.MIDDLE.STAT.json",
    "oracle": "oracle/spi_oracle/data_handling.py",
    "misconceptions": "oracle/spi_oracle/data_handling_misconceptions.py",
    "dataChartTheme": "core/visual-style/data-chart-theme.json",
}


def _sha256(path: str) -> str | None:
    full = os.path.join(ROOT, path)
    if not os.path.exists(full):
        return None
    h = hashlib.sha256()
    with open(full, "rb") as fh:
        for chunk in iter(lambda: fh.read(65536), b""):
            h.update(chunk)
    return h.hexdigest()


def main() -> int:
    os.makedirs(REVIEW_DIR, exist_ok=True)
    artifacts = {}
    for name, rel in ARTIFACTS.items():
        digest = _sha256(rel)
        artifacts[name] = {"path": rel, "sha256": digest, "present": digest is not None}

    rasters = {}
    bv_path = os.path.join(ROOT, "docs", "review", "stats_data_handling_browser_verification.json")
    if os.path.exists(bv_path):
        bv = json.load(open(bv_path, encoding="utf-8"))
        for mode, info in (bv.get("exports") or {}).items():
            if isinstance(info, dict) and "sha256" in info:
                rasters[mode] = {"sha256": info["sha256"], "width": info.get("width"), "height": info.get("height")}

    manifest = {
        "generatorId": dh.GENERATOR_ID, "generatorVersion": dh.GENERATOR_VERSION,
        "validatorVersion": dh.VALIDATOR_VERSION, "approvalStatus": "pending-review",
        "objectiveIds": [dh.OBJECTIVE_BY_TASK[t] for t in dh.TASKS],
        "tasks": list(dh.TASKS), "artifacts": artifacts, "rasterExports": rasters,
    }
    with open(os.path.join(REVIEW_DIR, "stats_data_handling_manifest.json"), "w", encoding="utf-8") as fh:
        json.dump(manifest, fh, indent=2)
    present = sum(1 for a in artifacts.values() if a["present"])
    print(f"Manifest written: {present}/{len(artifacts)} artifacts hashed; rasters: {list(rasters)}")
    for name, a in artifacts.items():
        print(f"  {name:22s} {'--' if not a['present'] else a['sha256'][:12]}  {a['path']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
