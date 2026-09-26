"""Contract tests for canonical artifact hashing (oracle/build_meta.py) — the Python mirror of
core/integrity/canonical-hash.ts, held to the same vectors: CRLF and LF encodings of one text hash
identically (and equal the plain SHA-256 of the LF bytes git stores); a lone CR is preserved; binary
is never rewritten; the file variant agrees with the bytes variant; a missing file is None.

  python oracle/tests/test_build_meta.py
"""

from __future__ import annotations

import hashlib
import os
import sys
import tempfile
import unittest

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(HERE))

from build_meta import canonical_text_bytes, sha256_canonical, sha256_canonical_bytes  # noqa: E402


def _plain(b: bytes) -> str:
    return hashlib.sha256(b).hexdigest()


class TestCanonicalHash(unittest.TestCase):
    def test_crlf_and_lf_hash_identically_to_the_plain_lf_digest(self):
        lf = b'{\n  "a": 1,\n  "b": "x"\n}\n'
        crlf = lf.replace(b"\n", b"\r\n")
        self.assertEqual(sha256_canonical_bytes(crlf), sha256_canonical_bytes(lf))
        self.assertEqual(sha256_canonical_bytes(lf), _plain(lf))
        self.assertNotEqual(_plain(crlf), _plain(lf), "the raw digests differ — that is the defect being neutralised")

    def test_no_trailing_newline_final_cr_dropped_too(self):
        self.assertEqual(sha256_canonical_bytes(b"a\r\nb"), sha256_canonical_bytes(b"a\nb"))

    def test_lone_cr_preserved_exactly_as_git_leaves_it(self):
        lone = b"a\rb\n"
        self.assertEqual(canonical_text_bytes(lone), lone)
        self.assertEqual(sha256_canonical_bytes(lone), _plain(lone))
        self.assertNotEqual(sha256_canonical_bytes(lone), sha256_canonical_bytes(b"a\nb\n"))

    def test_binary_nul_in_first_8000_bytes_never_rewritten(self):
        bin_ = bytes([0x89, 0x50, 0x4E, 0x47, 0x0D, 0x0A, 0x1A, 0x0A, 0x00]) + b"x\r\ny"
        self.assertEqual(canonical_text_bytes(bin_), bin_)
        self.assertEqual(sha256_canonical_bytes(bin_), _plain(bin_))

    def test_mixed_endings_normalise_fully(self):
        self.assertEqual(sha256_canonical_bytes(b"one\r\ntwo\nthree\r\n"),
                         sha256_canonical_bytes(b"one\ntwo\nthree\n"))

    def test_file_variant_agrees_with_bytes_variant_and_missing_is_none(self):
        with tempfile.TemporaryDirectory() as d:
            p = os.path.join(d, "artifact.json")
            with open(p, "wb") as fh:
                fh.write(b'{\r\n  "k": 1\r\n}\r\n')
            self.assertEqual(sha256_canonical(p), sha256_canonical_bytes(b'{\n  "k": 1\n}\n'))
            self.assertIsNone(sha256_canonical(os.path.join(d, "missing.json")))


if __name__ == "__main__":
    unittest.main(verbosity=2)
