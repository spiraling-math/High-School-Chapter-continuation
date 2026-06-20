/**
 * The stability gate — one runner every generator passes before it is stable.
 *
 * For each seed and interaction mode: generate then validate (zero invalid items
 * allowed), spot-check reproducibility, and record task/band coverage. The same
 * logic runs at 10,000 seeds in the oracle drivers; this runs a fast in-suite
 * subset against any GeneratorModule, including the approved generators.
 */

import type { GeneratorModule } from "./generator-module.ts";
import { interactionModesFor } from "./generator-module.ts";
import { legacyAnswerType } from "./interaction.ts";

export interface StabilityOptions {
  seeds: number;
  /** How many seeds to re-generate to confirm byte-identical reproducibility. */
  reproducibilitySpotCheck?: number;
}

export interface FailingSeed { seed: number; mode: string; failingChecks: string[]; }

export interface StabilityReport {
  generatorId: string;
  version: string;
  total: number;
  invalid: FailingSeed[];
  reproducible: boolean;
  tasks: Record<string, number>;
  bands: Record<number, number>;
}

export function runStabilityGate(gen: GeneratorModule, opts: StabilityOptions): StabilityReport {
  const modes = interactionModesFor(gen);
  const invalid: FailingSeed[] = [];
  const tasks: Record<string, number> = {};
  const bands: Record<number, number> = {};
  let reproducible = true;
  const spot = opts.reproducibilitySpotCheck ?? Math.min(200, opts.seeds);

  for (let seed = 1; seed <= opts.seeds; seed++) {
    for (const mode of modes) {
      // Use the legacy config selector so this exercises the same paths the
      // approved generators and stored bank records use (TD-1 back-compat).
      const config = { answerType: legacyAnswerType(mode) };
      let item;
      try {
        item = gen.generate(seed, config);
      } catch {
        invalid.push({ seed, mode, failingChecks: ["generate-threw"] });
        continue;
      }
      const v = gen.validate(item);
      if (v.status !== "pass") {
        invalid.push({ seed, mode, failingChecks: v.checks.filter((c) => c.result === "fail").map((c) => c.name) });
      }
      if (mode === modes[0]) {
        const task = String((item["params"] as { task?: string }).task ?? "");
        tasks[task] = (tasks[task] ?? 0) + 1;
        const band = Number((item["difficulty"] as { overallBand?: number }).overallBand ?? 0);
        bands[band] = (bands[band] ?? 0) + 1;
      }
      if (seed <= spot && gen.serialize(gen.generate(seed, config)) !== gen.serialize(item)) {
        reproducible = false;
      }
    }
  }

  return { generatorId: gen.id, version: gen.version, total: opts.seeds * modes.length, invalid, reproducible, tasks, bands };
}
