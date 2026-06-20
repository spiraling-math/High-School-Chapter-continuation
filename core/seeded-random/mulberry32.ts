/**
 * Deterministic, cross-language seeded PRNG (mulberry32).
 *
 * This is the canonical production implementation. It is the byte-for-byte
 * counterpart of `oracle/spi_oracle/seeded_random.py`: for any seed, both
 * produce identical `nextUint32()` streams, so the same seed reproduces the
 * same item in the Python oracle and in production (Decision #10).
 *
 * The derived helpers (nextInt, choice, shuffle) are part of the cross-language
 * contract and must match the Python oracle exactly.
 */

const UINT32 = 0xffffffff;

export class Mulberry32 {
  private state: number;

  constructor(seed: number) {
    // Normalise to a 32-bit unsigned integer.
    this.state = seed >>> 0;
  }

  /** Next raw 32-bit unsigned integer. */
  nextUint32(): number {
    this.state = (this.state + 0x6d2b79f5) >>> 0;
    let t = this.state;
    t = Math.imul(t ^ (t >>> 15), 1 | t);
    t = (t + Math.imul(t ^ (t >>> 7), 61 | t)) ^ t;
    return (t ^ (t >>> 14)) >>> 0;
  }

  /** Next float in the half-open interval [0, 1). */
  nextFloat(): number {
    return this.nextUint32() / 4294967296;
  }

  /** Deterministic integer in the inclusive range [lo, hi]. */
  nextInt(lo: number, hi: number): number {
    if (hi < lo) throw new Error("nextInt requires lo <= hi");
    const span = hi - lo + 1;
    return lo + Math.floor(this.nextFloat() * span);
  }

  /** Deterministic element from a non-empty array. */
  choice<T>(items: readonly T[]): T {
    if (items.length === 0) throw new Error("choice requires a non-empty array");
    return items[this.nextInt(0, items.length - 1)] as T;
  }

  /** New array, Fisher-Yates shuffled deterministically (matches the oracle). */
  shuffle<T>(items: readonly T[]): T[] {
    const result = items.slice();
    for (let i = result.length - 1; i > 0; i--) {
      const j = this.nextInt(0, i);
      const tmp = result[i] as T;
      result[i] = result[j] as T;
      result[j] = tmp;
    }
    return result;
  }
}
