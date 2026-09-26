"""Generation manifest for gen.measurement.mensuration v1.0.0 (owner M).

Records SHA-256 hashes of every frozen artifact (oracle source, byte-parity TS mirror, golden +
parity fixtures, curriculum objectives, schema, theme, distribution, review pack, visual audit,
browser verification) so the artifact-integrity tests (Python + TypeScript) can detect any drift.
approvalStatus is PENDING-REVIEW: implementation is authorized + machine-validated, but the family
is gated until the owner's review-pack decision. This is metadata only — it does NOT alter canonical
generator output.

Writes: docs/review/mensuration_manifest.json
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

from spi_oracle import mensuration as M  # noqa: E402

ARTIFACTS = {
    "oracleUnits": "oracle/spi_oracle/mensuration_units.py",
    "oracle": "oracle/spi_oracle/mensuration.py",
    "misconceptions": "oracle/spi_oracle/mensuration_misconceptions.py",
    "tsUnits": "domains/measurement/mensuration-units.ts",
    "tsGenerator": "domains/measurement/mensuration.ts",
    "tsMisconceptions": "domains/measurement/mensuration-misconceptions.ts",
    "golden": "oracle/golden/mensuration.golden.json",
    "parity": "oracle/golden/mensuration.parity.json",
    "objectives": "curriculum/objectives/SPI.MIDDLE.MEAS.json",
    "objectiveIds": "core/curriculum/mensuration-objective-ids.ts",
    "schema": "schemas/question-item.schema.json",
    "theme": "core/visual-style/mensuration-theme.json",
    "themeTs": "core/visual-style/mensuration-theme.ts",
    "distribution": "docs/review/mensuration_distribution.json",
    "reviewPackJson": "docs/review/mensuration_review_pack.json",
    "reviewPackMd": "docs/review/mensuration_review_pack.md",
    "visualAudit": "docs/review/mensuration_visual_audit.html",
    "browserVerification": "docs/review/mensuration_browser_verification.json",
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
    artifacts = {}
    for name, rel in ARTIFACTS.items():
        digest = _sha256(rel)
        artifacts[name] = {"path": rel, "sha256": digest, "present": digest is not None}

    manifest = {
        "generatorId": M.GENERATOR_ID, "generatorVersion": M.GENERATOR_VERSION,
        "validatorVersion": M.VALIDATOR_VERSION,
        "approvalStatus": "approved",
        "objectiveReviewStatus": "approved",
        "gitCommit": os.environ.get("SPI_BUILD_COMMIT") or _git_commit(),
        # Version tags (owner final APPROVE): the approved reference tag is created on approval; the
        # superseded v1.0.0 implementation tag is recorded as previousVersionTag, never as the approval tag.
        "versionTags": {
            "previousVersionTag": "mensuration-v1.0.0",
            "currentImplementationTag": "mensuration-v1.0.1",
            "approvedTag": "approved-mensuration-v1.0.1",
        },
        # Approval housekeeping (owner final APPROVE) — metadata only; does NOT alter canonical output.
        "approval": {"decision": "curriculum-approved",
                     "approvedTag": "approved-mensuration-v1.0.1",
                     "approvedAt": os.environ.get("SPI_APPROVAL_DATE", "2026-06-25"),
                     "approvalCommit": os.environ.get("SPI_APPROVAL_COMMIT", ""),
                     "decisionLog": "DECISION_LOG.md #53",
                     "schemaExtension": "answer.type 'quantity' + answer.measure (APPROVED)"},
        "objectiveIds": [M.OBJECTIVE_BY_TASK[t] for t in M.TASKS],
        "tasks": list(M.TASKS),
        "interactionTypes": ["free-response"],
        "answerTypes": ["quantity"],
        "artifacts": artifacts,
    }
    with open(os.path.join(REVIEW_DIR, "mensuration_manifest.json"), "w", encoding="utf-8") as fh:
        json.dump(manifest, fh, indent=2)
    present = sum(1 for a in artifacts.values() if a["present"])
    print(f"Manifest written: {present}/{len(artifacts)} artifacts hashed (approvalStatus={manifest['approvalStatus']}).")
    for name, a in artifacts.items():
        print(f"  {name:20s} {'--' if not a['present'] else a['sha256'][:12]}  {a['path']}")
    return 0 if present == len(artifacts) else 1


if __name__ == "__main__":
    raise SystemExit(main())
