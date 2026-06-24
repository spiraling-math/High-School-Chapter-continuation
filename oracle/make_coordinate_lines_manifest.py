"""Tamper-evident generation manifest for the coordinate-lines review package.

Records the git commit, generator id/version/validator, build timestamp, the regeneration
commands, and SHA-256 hashes of the review pack, visual audit, golden/parity fixtures, the
distribution report, the high-resolution SVG sample, and the per-item SVG directory. The
artifact-integrity tests (oracle/tests/test_coordinate_lines.py + the TS counterpart)
re-hash these and confirm they match, that the version equals the live generator version,
and that the audit was built from the same commit.

Run (AFTER regenerating the pack, audit, fixtures): python oracle/make_coordinate_lines_manifest.py
Writes: docs/review/coordinate_lines_manifest.json
"""

from __future__ import annotations

import hashlib
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, HERE)

from spi_oracle import coordinate_lines as cl  # noqa: E402
from build_meta import build_commit, build_timestamp  # noqa: E402

OUT = os.path.join(ROOT, "docs", "review", "coordinate_lines_manifest.json")
SVG_DIR = os.path.join(ROOT, "docs", "review", "coordinate_lines_svgs")

ARTIFACTS = {
    "reviewPackMd": "docs/review/coordinate_lines_review_pack.md",
    "reviewPackJson": "docs/review/coordinate_lines_review_pack.json",
    "visualAudit": "docs/review/coordinate_lines_visual_audit.html",
    "goldenFixture": "oracle/golden/coordinate_lines.golden.json",
    "parityFixture": "oracle/golden/coordinate_lines.parity.json",
    "distributionReport": "docs/review/coordinate_lines_distribution.json",
    "hiresSample": "docs/review/coordinate_lines_8k_sample.svg",
    "browserVerification": "docs/review/coordinate_lines_browser_verification.json",
}

BROWSER_VERIFICATION = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
                                    "docs", "review", "coordinate_lines_browser_verification.json")

COMMANDS = [
    "python oracle/run_coordinate_lines.py                  # golden + parity fixtures + 10k sweep + distribution report",
    "python oracle/make_review_pack_coordinate_lines.py     # review pack (.md/.json) + per-item SVGs",
    "python oracle/make_visual_audit_coordinate_lines.py    # visual audit + premium gallery + 6000x4200 export",
    "python oracle/make_coordinate_lines_manifest.py        # this manifest",
]


def _sha256_file(rel: str):
    path = os.path.join(ROOT, rel.replace("/", os.sep))
    if not os.path.exists(path):
        return None
    h = hashlib.sha256()
    with open(path, "rb") as fh:
        for chunk in iter(lambda: fh.read(65536), b""):
            h.update(chunk)
    return h.hexdigest()


def _sha256_svgs() -> str:
    h = hashlib.sha256()
    for name in sorted(os.listdir(SVG_DIR)) if os.path.isdir(SVG_DIR) else []:
        if name.endswith(".svg"):
            with open(os.path.join(SVG_DIR, name), "rb") as fh:
                h.update(name.encode())
                h.update(fh.read())
    return h.hexdigest()


def _raster_export_hashes():
    if not os.path.exists(BROWSER_VERIFICATION):
        return None
    bv = json.load(open(BROWSER_VERIFICATION, encoding="utf-8"))
    return {m: {"width": e["width"], "height": e["height"], "sha256": e["sha256"]} for m, e in bv.get("exports", {}).items()}


def build() -> None:
    manifest = {
        "schema": "spi-math-coordinate-lines-manifest/1",
        "generatorId": cl.GENERATOR_ID,
        "generatorVersion": cl.GENERATOR_VERSION,
        "validatorVersion": cl.VALIDATOR_VERSION,
        "gitCommit": build_commit(),
        "generatedAt": build_timestamp(),
        "pngExport": cl.png_export_transform(),
        "commands": COMMANDS,
        "sha256": {key: _sha256_file(rel) for key, rel in ARTIFACTS.items()},
        "sha256SvgDir": _sha256_svgs(),
        "svgCount": len([n for n in os.listdir(SVG_DIR) if n.endswith(".svg")]) if os.path.isdir(SVG_DIR) else 0,
        # SHA-256 of the three 6000x4200 colour PNGs rasterised in-browser from the canonical SVG
        # (the SVG is authoritative; PNGs are derived). Recorded for the owner's export-hash deliverable.
        "rasterExports": _raster_export_hashes(),
    }
    with open(OUT, "w", encoding="utf-8") as fh:
        json.dump(manifest, fh, indent=2)
    print(f"Wrote {OUT}: v{manifest['generatorVersion']} commit {manifest['gitCommit'][:10]} "
          f"({sum(1 for v in manifest['sha256'].values() if v)} artifacts + {manifest['svgCount']} svgs).")


if __name__ == "__main__":
    build()
