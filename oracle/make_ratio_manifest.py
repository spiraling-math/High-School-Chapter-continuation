"""gen.proportion.ratio artifact manifest.

Mirror of make_transformations_manifest. approvalStatus is PENDING-REVIEW: implementation is authorized +
machine-validated, but the family is hidden from normal Studio + production exports until the owner's
APPROVE/REVISE/REJECT of the implemented v1.0.0 family. Objectives are approved-for-implementation. The
answer.type 'ratio' (canonical-first) schema extension is recorded as APPROVED. Version tags follow the
established terminology; the approvedTag is null until approval. The manifest is metadata only and does
not alter generator output.

  PYTHONIOENCODING=utf-8 python oracle/make_ratio_manifest.py

Writes docs/review/proportion_ratio_manifest.json (sha256 of every frozen artifact). TS mirror files may
be absent if the TS mirror agent has not finished — they are recorded with present:false in that case.
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

from spi_oracle import ratio as R  # noqa: E402

ARTIFACTS = {
    # Python oracle (frozen sources — never modified by this builder).
    "oracleCore": "oracle/spi_oracle/ratio_core.py",
    "oracleMisconceptions": "oracle/spi_oracle/ratio_misconceptions.py",
    "oracleGenerator": "oracle/spi_oracle/ratio.py",
    "golden": "oracle/golden/ratio.golden.json",
    "parity": "oracle/golden/ratio.parity.json",
    # TypeScript mirror (may be absent until the TS mirror agent finishes).
    "tsCore": "domains/proportion/ratio-core.ts",
    "tsMisconceptions": "domains/proportion/ratio-misconceptions.ts",
    "tsGenerator": "domains/proportion/ratio.ts",
    "tsParityTest": "domains/proportion/ratio.parity.test.ts",
    "tsTheme": "core/visual-style/ratio-theme.ts",
    # Curriculum + schema + compiled validator.
    "objectives": "curriculum/objectives/SPI.MIDDLE.RATIO.json",
    "objectiveIds": "core/curriculum/ratio-objective-ids.ts",
    "schema": "schemas/question-item.schema.json",
    "compiledValidator": "core/schema/compiled/question-item.validator.mjs",
    # Theme.
    "themeJson": "core/visual-style/ratio-theme.json",
    # Review artifacts.
    "distribution": "docs/review/ratio_distribution.json",
    "reviewPackJson": "docs/review/proportion_ratio_review_pack.json",
    "reviewPackMd": "docs/review/proportion_ratio_review_pack.md",
    "visualAudit": "docs/review/proportion_ratio_visual_audit.html",
    "browserVerification": "docs/review/proportion_ratio_browser_verification.json",
    "realBrowserStyles": "docs/review/ratio_real_browser_styles.json",
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
        "generatorId": R.GENERATOR_ID, "generatorVersion": R.GENERATOR_VERSION,
        "validatorVersion": R.VALIDATOR_VERSION,
        "approvalStatus": "pending-review",
        "objectiveReviewStatus": "approved-for-implementation",
        "gitCommit": os.environ.get("SPI_BUILD_COMMIT") or _git_commit(),
        "hiddenFromNormalStudioAndProduction": True,
        # Version tags (established terminology). The approvedTag is null until the owner approves.
        "versionTags": {
            "previousVersionTag": None,
            "currentImplementationTag": "ratio-v1.0.0",
            "approvedTag": None,
        },
        "schemaExtension": {
            "note": "answer.type 'ratio' (canonical-first) — APPROVED",
            "detail": ("The simplest-form ordered integer tuple {parts} IS answer.canonical; answer.display "
                       "('2:3') is derived. The tuple is never stored twice and a formatted string is never "
                       "the canonical value."),
        },
        "objectiveIds": [R.OBJECTIVE_BY_TASK[t] for t in R.RATIO_TASKS],
        "tasks": list(R.RATIO_TASKS),
        "interactionTypes": ["free-response", "multiple-choice"],
        "answerTypes": ["ratio", "exact-rational", "integer", "table-completion", "multiple-choice"],
        "mcPolicy": {
            "mcOnlyTasks": list(R.MC_ONLY_TASKS),
            "mcEligibleTasks": list(R.MC_ELIGIBLE_TASKS),
            "note": "best_buy is multiple-choice only; the other MC-eligible tasks add MC to free-response; "
                    "every other task is free-response only and an explicit MC request raises.",
        },
        "artifacts": artifacts,
    }
    with open(os.path.join(REVIEW_DIR, "proportion_ratio_manifest.json"), "w", encoding="utf-8") as fh:
        json.dump(manifest, fh, indent=2)
    present = sum(1 for a in artifacts.values() if a["present"])
    absent = [name for name, a in artifacts.items() if not a["present"]]
    print(f"Manifest written: {present}/{len(artifacts)} artifacts hashed "
          f"(approvalStatus={manifest['approvalStatus']}).")
    if absent:
        print("  absent (not yet present):", ", ".join(absent))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
