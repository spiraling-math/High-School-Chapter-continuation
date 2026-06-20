"""SPI-Math verification oracle.

An independent, deterministic reference implementation of the platform's
mathematical core, written in Python because it can be executed and tested in
the current environment. It serves two permanent purposes:

1. Proof: it runs the deterministic mathematics and its tests now, honouring the
   "deterministic mathematics proven by running tests" principle.
2. Independent verification: the production TypeScript generators are
   cross-checked against this oracle's golden JSON vectors (Principle 4).

The oracle and the TypeScript production code share the same named PRNG
(mulberry32) implemented with identical 32-bit semantics, so the same seed
produces byte-identical items in both languages.
"""

__version__ = "1.0.0"
