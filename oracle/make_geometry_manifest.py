"""Write a tamper-evident generation manifest for the geometry review package.

Records the git commit, generator id/version, build timestamp, the exact regeneration
commands, and SHA-256 hashes of the review pack, the visual audit, the fixtures, the saved
SVGs, and the sample exports. An integrity test (oracle/tests/test_geometry.py and
domains/geometry/artifact-integrity.test.ts) re-hashes the files and confirms they match
this manifest, that the version equals the live generator version, and that the audit was
built from the same commit.

Run (AFTER regenerating the pack, audit, fixtures, and samples):
  python oracle/make_geometry_manifest.py
Writes: docs/review/geometry_manifest.json
"""

from __future__ import annotations

import hashlib
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, HERE)

from spi_oracle import geometry as geo  # noqa: E402
from build_meta import build_commit, build_timestamp, canonical_text_bytes, sha256_canonical  # noqa: E402

OUT = os.path.join(ROOT, "docs", "review", "geometry_manifest.json")
SVG_DIR = os.path.join(ROOT, "docs", "review", "geometry_svgs")

ARTIFACTS = {
    "reviewPackMd": "docs/review/geometry_angles_review_pack.md",
    "reviewPackJson": "docs/review/geometry_angles_review_pack.json",
    "visualAudit": "docs/review/geometry_visual_audit.html",
    "goldenFixture": "oracle/golden/geometry_angles.golden.json",
    "parityFixture": "oracle/golden/geometry_angles.parity.json",
    "sampleWorksheet": "apps/generator-studio/dist/samples/worksheet.html",
    "sampleAnswerKey": "apps/generator-studio/dist/samples/answer-key.html",
    "sampleSolutions": "apps/generator-studio/dist/samples/solutions.html",
    "sampleBankJson": "apps/generator-studio/dist/samples/bank.json",
}

COMMANDS = [
    "python oracle/run_geometry_angles.py            # golden + parity fixtures + 10k sweep",
    "python oracle/make_review_pack_geometry.py      # review pack (.md/.json) + SVGs",
    "python oracle/make_visual_audit_geometry.py     # visual edge-case audit (before/after)",
    "node scripts/build-samples.mjs                  # offline sample exports (geometry excluded: pending-review)",
    "python oracle/make_geometry_manifest.py         # this manifest",
]


def _sha256_file(rel: str) -> str | None:
    # canonical (CRLF->LF) hash — see build_meta.sha256_canonical: the frozen digest is the same on a
    # Windows working tree (CRLF copies) and on the LF bytes git stores under .gitattributes eol=lf.
    return sha256_canonical(os.path.join(ROOT, rel.replace("/", os.sep)))


def _sha256_svgs() -> str:
    h = hashlib.sha256()
    for name in sorted(os.listdir(SVG_DIR)) if os.path.isdir(SVG_DIR) else []:
        if name.endswith(".svg"):
            with open(os.path.join(SVG_DIR, name), "rb") as fh:
                h.update(name.encode())
                h.update(canonical_text_bytes(fh.read()))  # canonical bytes (CRLF->LF), as for every artifact
    return h.hexdigest()


def build() -> None:
    manifest = {
        "schema": "spi-math-geometry-manifest/1",
        "generatorId": geo.GENERATOR_ID,
        "generatorVersion": geo.GENERATOR_VERSION,
        "validatorVersion": geo.validate(geo.generate(1, {}))["validatorVersion"],
        "gitCommit": build_commit(),
        "generatedAt": build_timestamp(),
        "commands": COMMANDS,
        "sha256": {key: _sha256_file(rel) for key, rel in ARTIFACTS.items()},
        "sha256SvgDir": _sha256_svgs(),
        "svgCount": len([n for n in os.listdir(SVG_DIR) if n.endswith(".svg")]) if os.path.isdir(SVG_DIR) else 0,
    }
    with open(OUT, "w", encoding="utf-8") as fh:
        json.dump(manifest, fh, indent=2)
    print(f"Wrote {OUT}: v{manifest['generatorVersion']} commit {manifest['gitCommit'][:10]} "
          f"({sum(1 for v in manifest['sha256'].values() if v)} artifacts hashed, {manifest['svgCount']} svgs).")


if __name__ == "__main__":
    build()
