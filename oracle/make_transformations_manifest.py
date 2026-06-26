"""gen.geometry.transformations artifact manifest.

approvalStatus is PENDING-REVIEW: implementation is authorized + machine-validated, but the family is
gated from normal Studio + production exports until the owner's APPROVE/REVISE/REJECT of the implemented
v1.0.0 family. Objectives are approved-for-implementation. The approved answer.type 'transformation'
schema extension (canonical-first) is recorded. Version tags follow the established terminology; the
approvedTag is null until approval. The manifest is metadata only and does not alter generator output.

  python oracle/make_transformations_manifest.py

Writes docs/review/transformations_manifest.json (sha256 of every frozen artifact).
"""

from __future__ import annotations

import hashlib
import json
import os
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
REVIEW_DIR = os.path.join(ROOT, "docs", "review")
sys.path.insert(0, os.path.join(HERE, "spi_oracle"))
sys.path.insert(0, HERE)

from spi_oracle import transformations as T  # noqa: E402

ARTIFACTS = {
    "oracleCore": "oracle/spi_oracle/transformations_core.py",
    "oracleShapes": "oracle/spi_oracle/transformations_shapes.py",
    "oracleChecker": "oracle/spi_oracle/transformations_checker.py",
    "oracleGenerator": "oracle/spi_oracle/transformations.py",
    "oracleMisconceptions": "oracle/spi_oracle/transformations_misconceptions.py",
    "tsCore": "domains/geometry/transformations-core.ts",
    "tsShapes": "domains/geometry/transformations-shapes.ts",
    "tsChecker": "domains/geometry/transformations-checker.ts",
    "tsGenerator": "domains/geometry/transformations.ts",
    "tsMisconceptions": "domains/geometry/transformations-misconceptions.ts",
    "tsParityTest": "domains/geometry/transformations.parity.test.ts",
    "golden": "oracle/golden/transformations.golden.json",
    "parity": "oracle/golden/transformations.parity.json",
    "objectives": "curriculum/objectives/SPI.MIDDLE.GEO.TRANS.json",
    "objectiveIds": "core/curriculum/transformations-objective-ids.ts",
    "schema": "schemas/question-item.schema.json",
    "compiledValidator": "core/schema/compiled/question-item.validator.mjs",
    "themeJson": "core/visual-style/transformations-theme.json",
    "themeTs": "core/visual-style/transformations-theme.ts",
    "distribution": "docs/review/transformations_distribution.json",
    "reviewPackJson": "docs/review/transformations_review_pack.json",
    "reviewPackMd": "docs/review/transformations_review_pack.md",
    "visualAudit": "docs/review/transformations_visual_audit.html",
    "browserVerification": "docs/review/transformations_browser_verification.json",
}


def _sha256(path: str):
    full = os.path.join(ROOT, path)
    if not os.path.exists(full):
        return None
    h = hashlib.sha256()
    with open(full, "rb") as fh:
        for chunk in iter(lambda: fh.read(65536), b""):
            h.update(chunk)
    return h.hexdigest()


def _git_commit():
    try:
        return subprocess.check_output(["git", "-C", ROOT, "rev-parse", "HEAD"], text=True).strip()
    except Exception:
        return ""


def main() -> int:
    os.makedirs(REVIEW_DIR, exist_ok=True)
    artifacts = {name: {"path": rel, "sha256": (d := _sha256(rel)), "present": d is not None}
                 for name, rel in ARTIFACTS.items()}

    manifest = {
        "generatorId": T.GENERATOR_ID, "generatorVersion": T.GENERATOR_VERSION,
        "validatorVersion": T.VALIDATOR_VERSION,
        "approvalStatus": "pending-review",
        "objectiveReviewStatus": "approved-for-implementation",
        "gitCommit": os.environ.get("SPI_BUILD_COMMIT") or _git_commit(),
        # v1.0.0 implemented but unapproved (preserved at tag transformations-v1.0.0); v1.0.1 corrects the
        # review-package defects (owner REVISE). The approved tag is created only on owner APPROVE.
        "versionTags": {
            "previousVersionTag": "transformations-v1.0.0",
            "currentImplementationTag": "transformations-v1.0.1",
            "approvedTag": None,
        },
        "schemaExtension": "answer.type 'transformation' (canonical-first: descriptor IS answer.canonical) — APPROVED",
        "objectiveIds": [T.OBJECTIVE_BY_TASK[t] for t in T.TASKS],
        "tasks": list(T.TASKS),
        "interactionTypes": ["free-response"],
        "answerTypes": ["coordinate", "table-completion", "transformation"],
        "hiddenFromNormalStudioAndProduction": True,
        "artifacts": artifacts,
    }
    with open(os.path.join(REVIEW_DIR, "transformations_manifest.json"), "w", encoding="utf-8") as fh:
        json.dump(manifest, fh, indent=2)
    present = sum(1 for a in artifacts.values() if a["present"])
    print(f"Manifest written: {present}/{len(artifacts)} artifacts hashed (approvalStatus={manifest['approvalStatus']}).")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
