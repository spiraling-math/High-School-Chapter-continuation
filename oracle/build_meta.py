"""Shared build-identity + artifact-integrity helpers for every generation manifest + visual audit.

Both the manifest and the audit stamp the SAME git commit (HEAD at build time) and a
build timestamp, so an integrity test can confirm the audit and the manifest were produced
from the same build (audit-commit-matches-build).

Canonical hashing: `sha256_canonical` is the ONE digest every frozen manifest and integrity test
uses. The repository stores text with LF endings (.gitattributes `* text=auto eol=lf`), but a
Windows working tree can hold CRLF copies of the same files (git normalises them back on commit).
Line endings are a checkout artefact, not artefact content, so we hash the CANONICAL bytes:
CRLF -> LF for text (a lone CR preserved), binary (a NUL in the first 8000 bytes — git's own
heuristic) untouched. TypeScript mirror: core/integrity/canonical-hash.ts (same contract).
"""

from __future__ import annotations

import hashlib
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


_BINARY_PROBE_BYTES = 8000


def canonical_text_bytes(data: bytes) -> bytes:
    """The canonical (repository) bytes of an artifact: CRLF -> LF for text, untouched for binary."""
    if b"\0" in data[:_BINARY_PROBE_BYTES]:
        return data  # binary: never rewritten
    return data.replace(b"\r\n", b"\n")  # a lone CR is preserved, exactly as git leaves it


def sha256_canonical_bytes(data: bytes) -> str:
    """SHA-256 (hex) of the canonical bytes of `data`."""
    return hashlib.sha256(canonical_text_bytes(data)).hexdigest()


def sha256_canonical(path: str) -> str | None:
    """SHA-256 (hex) of the canonical bytes of the file at `path` (absolute or ROOT-relative); None if missing."""
    full = path if os.path.isabs(path) else os.path.join(ROOT, path)
    if not os.path.exists(full):
        return None
    with open(full, "rb") as fh:
        return sha256_canonical_bytes(fh.read())
