"""Shared build-identity helpers for the geometry generation manifest + visual audit.

Both the manifest and the audit stamp the SAME git commit (HEAD at build time) and a
build timestamp, so an integrity test can confirm the audit and the manifest were produced
from the same build (audit-commit-matches-build).
"""

from __future__ import annotations

import os
import subprocess

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def build_commit() -> str:
    try:
        return subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=ROOT, text=True).strip()
    except Exception:
        return "unknown"


def build_timestamp() -> str:
    ts = os.environ.get("SPI_BUILD_TS")
    if ts:
        return ts
    from datetime import datetime, timezone
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()
