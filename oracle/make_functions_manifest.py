"""gen.functions.foundations artifact manifest (PENDING-REVIEW).

Mirror of make_ratio_manifest. approvalStatus is PENDING-REVIEW (DECISION_LOG.md #65): the family is
machine-validated (10,000-seed oracle sweep, byte parity TS<->Python) but NOT curriculum-approved. It is
visible only in the Studio's review mode and excluded from production exports/samples. The eleven
SPI.IBDPAASL.FUNC.* objectives are `reviewStatus: proposed`. The two canonical-first answer contracts the
family introduces (answer.type 'algebraic-expression' and 'interval') are PROPOSED, not approved. No approved
tag exists; the implementation tag is functions-v1.0.0. The manifest is metadata only and does not alter
generator output.

  PYTHONIOENCODING=utf-8 python oracle/make_functions_manifest.py

Writes docs/review/functions_manifest.json (canonical CRLF->LF sha256 of every frozen artifact; an artifact
that is not yet present is recorded with present:false).
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

from spi_oracle import functions as G  # noqa: E402
from spi_oracle import functions_misconceptions as FM  # noqa: E402

ARTIFACTS = {
    # Python oracle (frozen sources — never modified by this builder).
    "oracleCore": "oracle/spi_oracle/functions_core.py",
    "oracleMisconceptions": "oracle/spi_oracle/functions_misconceptions.py",
    "oracleGenerator": "oracle/spi_oracle/functions.py",
    "oraclePolynomial": "oracle/spi_oracle/polynomial.py",
    "oracleExpressionChecker": "oracle/spi_oracle/expression_checker.py",
    "oracleIntervalChecker": "oracle/spi_oracle/interval_checker.py",
    "oracleRunner": "oracle/run_functions.py",
    "oracleTests": "oracle/tests/test_functions.py",
    "oracleCheckerTests": "oracle/tests/test_functions_checkers.py",
    "golden": "oracle/golden/functions.golden.json",
    "parity": "oracle/golden/functions.parity.json",
    "checkerCorpus": "oracle/golden/functions_checker_corpus.json",
    # TypeScript mirror.
    "tsCore": "domains/functions/functions-core.ts",
    "tsMisconceptions": "domains/functions/functions-misconceptions.ts",
    "tsGenerator": "domains/functions/functions.ts",
    "tsParityTest": "domains/functions/functions.parity.test.ts",
    "tsUnitTest": "domains/functions/functions.test.ts",
    "tsPolynomial": "core/exact-math/polynomial.ts",
    "tsExpressionChecker": "core/answer-checking/expression-checker.ts",
    "tsIntervalChecker": "core/answer-checking/interval-checker.ts",
    "tsCheckerCorpusTest": "core/answer-checking/functions-checker-corpus.test.ts",
    # Curriculum + schema + compiled validator + misconception registry.
    "objectives": "curriculum/objectives/SPI.IBDPAASL.FUNC.json",
    "objectiveIds": "core/curriculum/functions-objective-ids.ts",
    "schema": "schemas/question-item.schema.json",
    "compiledValidator": "core/schema/compiled/question-item.validator.mjs",
    "misconceptionsJson": "core/misconceptions/functions.json",
    # Specification + review artifacts.
    "specificationProposal": "docs/GENERATOR_SPEC_functions_PROPOSAL.md",
    "distribution": "docs/review/functions_distribution.json",
    "reviewPackJson": "docs/review/functions_review_pack.json",
    "reviewPackMd": "docs/review/functions_review_pack.md",
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
        "generatorId": G.GENERATOR_ID, "generatorVersion": G.GENERATOR_VERSION,
        "validatorVersion": G.VALIDATOR_VERSION,
        "approvalStatus": "pending-review",
        "objectiveReviewStatus": "proposed",
        "gitCommit": os.environ.get("SPI_BUILD_COMMIT") or _git_commit(),
        "hiddenFromNormalStudioAndProduction": True,
        "versionTags": {
            "previousVersionTag": None,
            "currentImplementationTag": "functions-v1.0.0",
            "approvedTag": None,
        },
        "review": {
            "decision": "pending-review",
            "decisionLogRef": "DECISION_LOG.md #65",
            "specification": "docs/GENERATOR_SPEC_functions_PROPOSAL.md",
            "reviewPack": "docs/review/functions_review_pack.md",
            "ownerAsked": [
                "approve the eleven proposed SPI.IBDPAASL.FUNC.* objectives and their task mapping",
                "approve the canonical-first answer contracts answer.type 'algebraic-expression' and 'interval' "
                "(+ the ASCII-anchored checkers pinned by oracle/golden/functions_checker_corpus.json)",
                "approve the item mathematics, phrasing, bands, solutions, misconception rules + feedback and the MC policy",
                "ratify the controlled-vocabulary extension FUNC -> functions + strand introducing-functions (registry §4.6)",
            ],
            "sharedInfrastructure": ("answer.type 'algebraic-expression' (canonical polynomial coefficient vector, "
                                     "ascending degree, variable x; derived answer.display) and answer.type 'interval' "
                                     "(real-subset descriptor: reals | ray | bounded | reals-except with exact "
                                     "rational endpoints; derived answer.display) + the two ASCII-anchored "
                                     "parser/canonicalizer/checkers and their 7 + 8 result codes — PROPOSED. Does NOT "
                                     "authorize rational functions, radicals or transcendental expressions as answers, "
                                     "unions of intervals, open rays for domains, or graphs."),
        },
        "schemaExtension": {
            "note": "answer.type 'algebraic-expression' + 'interval' (canonical-first) — PROPOSED, additive (six if/then rules)",
            "detail": ("The coefficient vector / real-subset descriptor IS answer.canonical; answer.display is derived plain "
                       "ASCII text. A formatted string is never the canonical value. Existing approved families' items "
                       "and manifests are unaffected except the schema/compiledValidator digests, re-frozen."),
        },
        "objectiveIds": [G.OBJECTIVE_BY_TASK[t] for t in G.TASKS],
        "tasks": list(G.TASKS),
        "interactionTypes": ["free-response", "multiple-choice"],
        "answerTypes": ["integer", "exact-rational", "algebraic-expression", "interval", "multiple-choice"],
        "mcPolicy": {
            "mcOnlyTasks": list(G.MC_ONLY_TASKS),
            "mcEligibleTasks": list(G.MC_ELIGIBLE_TASKS),
            "note": "identify_function is multiple-choice only (an explicit free-response request raises); every other "
                    "task serves free-response and multiple-choice with three formula-backed misconception distractors. "
                    "The legacy answerType selector is not consulted (ratio v1.0.2 precedent).",
        },
        "misconceptionCount": len(FM.MISCONCEPTIONS),
        "artifacts": artifacts,
    }
    with open(os.path.join(REVIEW_DIR, "functions_manifest.json"), "w", encoding="utf-8", newline="\n") as fh:
        json.dump(manifest, fh, indent=2, ensure_ascii=False)
        fh.write("\n")
    present = sum(1 for a in artifacts.values() if a["present"])
    absent = [name for name, a in artifacts.items() if not a["present"]]
    print(f"Manifest written: {present}/{len(artifacts)} artifacts hashed "
          f"(approvalStatus={manifest['approvalStatus']}).")
    if absent:
        print("  absent (not yet present):", ", ".join(absent))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
