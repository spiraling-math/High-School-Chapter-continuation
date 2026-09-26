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

import json
import os
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
REVIEW_DIR = os.path.join(ROOT, "docs", "review")
sys.path.insert(0, os.path.join(HERE, "spi_oracle"))
sys.path.insert(0, HERE)

from build_meta import sha256_canonical  # noqa: E402

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
    # canonical (CRLF->LF) hash — see build_meta.sha256_canonical: the frozen digest is the same on a
    # Windows working tree (CRLF copies) and on the LF bytes git stores under .gitattributes eol=lf.
    return sha256_canonical(os.path.join(ROOT, path))


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
        "approvalStatus": "approved",
        "objectiveReviewStatus": "approved",
        "gitCommit": os.environ.get("SPI_BUILD_COMMIT") or _git_commit(),
        # Version tags (owner final APPROVE): the approved reference tag is created on approval; the
        # superseded implementation tags are recorded as historical, never as the approval tag.
        "versionTags": {
            "previousVersionTag": "transformations-v1.0.1",
            "currentImplementationTag": "transformations-v1.0.2",
            "approvedTag": "approved-transformations-v1.0.2",
        },
        # Approval housekeeping (owner final APPROVE) — metadata only; does NOT alter canonical output.
        "approval": {
            "decision": "curriculum-approved",
            "approvedTag": "approved-transformations-v1.0.2",
            "approvedAt": os.environ.get("SPI_APPROVAL_DATE", "2026-06-26"),
            "approvalCommit": os.environ.get("SPI_APPROVAL_COMMIT", ""),
            "decisionLog": "DECISION_LOG.md #57",
            "sharedInfrastructure": ("answer.type 'transformation' (canonical-first descriptor in "
                                     "answer.canonical) + translation/reflection/rotation descriptor union + "
                                     "parser/canonicalizer/formatter/equivalence checker + the 14 result codes "
                                     "— APPROVED. Does NOT authorize enlargements, compositions, arbitrary-angle "
                                     "rotations, arbitrary reflection lines, fractional vectors/centres, matrices, "
                                     "transformations of functions, tessellations, or 3D."),
        },
        "objectiveIds": [T.OBJECTIVE_BY_TASK[t] for t in T.TASKS],
        "tasks": list(T.TASKS),
        "interactionTypes": ["free-response"],
        "answerTypes": ["coordinate", "table-completion", "transformation"],
        "artifacts": artifacts,
    }
    with open(os.path.join(REVIEW_DIR, "transformations_manifest.json"), "w", encoding="utf-8") as fh:
        json.dump(manifest, fh, indent=2)
    present = sum(1 for a in artifacts.values() if a["present"])
    print(f"Manifest written: {present}/{len(artifacts)} artifacts hashed (approvalStatus={manifest['approvalStatus']}).")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
