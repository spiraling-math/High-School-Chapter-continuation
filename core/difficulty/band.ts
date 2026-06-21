/**
 * Shared difficulty helpers (SDK).
 *
 * The platform difficulty band is a single documented function (DIFFICULTY_MODEL.md):
 * a weighted axis score in [0,1] maps to an integer band 1..5. Generators populate
 * their own axis weights but MUST use this band function — never invent their own.
 *
 * `round3` and `bandFromScore` are byte-for-byte identical to the inline versions
 * the two approved generators previously used; centralizing them is output-neutral
 * (guarded by the golden/parity fixtures). Mirrors oracle/spi_oracle/difficulty.py.
 */

/** Round half-up to 3 decimals. (JS serialization drops a trailing .0, matching
 *  the oracle's integer-collapsing round3.) */
export function round3(x: number): number {
  return Math.floor(x * 1000 + 0.5) / 1000;
}

export function clamp01(x: number): number {
  return Math.max(0, Math.min(1, x));
}

/** Map a weighted axis score to an integer band 1..5 (0..0.2→1, …, 0.8..1→5). */
export function bandFromScore(score: number): number {
  return Math.min(5, 1 + Math.floor(clamp01(score) * 5));
}
