/**
 * Canonical registry of the approved sequence generators as GeneratorModules.
 *
 * The single source of truth for "which generators exist", used by the Studio,
 * exporters, and the stability harness. Adding a family is one entry here. The
 * underlying generate/validate/serialize functions are the approved, immutable
 * implementations — this registry only adapts them to the GeneratorModule shape
 * (output-neutral).
 */

import type { GeneratorModule } from "./generator-module.ts";
import * as arithmetic from "../../domains/sequences/arithmetic.ts";
import { validate as arithmeticValidate } from "../../domains/sequences/validate.ts";
import * as geometric from "../../domains/sequences/geometric.ts";
import * as linear from "../../domains/algebra/linear-equations.ts";

export const GENERATORS: GeneratorModule[] = [
  {
    id: arithmetic.GENERATOR_ID,
    version: arithmetic.GENERATOR_VERSION,
    label: "Arithmetic sequences",
    tasks: [
      { value: "nth_term", label: "nth term", mc: true },
      { value: "sum_n", label: "Sum of first n terms", mc: true },
      { value: "find_d", label: "Find common difference", mc: false },
      { value: "find_n_for_value", label: "Find term index", mc: false },
    ],
    generate: (s, c) => arithmetic.generate(s, c as arithmetic.Config),
    validate: arithmeticValidate,
    serialize: arithmetic.serialize,
  },
  {
    id: geometric.GENERATOR_ID,
    version: geometric.GENERATOR_VERSION,
    label: "Geometric sequences",
    tasks: [
      { value: "nth_term", label: "nth term", mc: true },
      { value: "sum_n", label: "Sum of first n terms", mc: true },
      { value: "find_r", label: "Find common ratio", mc: false },
      { value: "find_n_for_value", label: "Find term index", mc: false },
      { value: "sum_infinite", label: "Sum to infinity", mc: false },
    ],
    generate: (s, c) => geometric.generate(s, c as geometric.Config),
    validate: geometric.validate,
    serialize: geometric.serialize,
  },
  {
    id: linear.GENERATOR_ID,
    version: linear.GENERATOR_VERSION,
    label: "Linear equations (one variable)",
    tasks: [
      { value: "one_step_add", label: "One-step (+/−)", mc: true },
      { value: "one_step_mul", label: "One-step (×)", mc: true },
      { value: "two_step", label: "Two-step (ax+b=c)", mc: true },
      { value: "both_sides", label: "Variables on both sides", mc: true },
      { value: "brackets", label: "One set of brackets", mc: true },
    ],
    generate: (s, c) => linear.generate(s, c as linear.Config),
    validate: linear.validate,
    serialize: linear.serialize,
  },
];

export function getGenerator(id: string): GeneratorModule {
  return GENERATORS.find((g) => g.id === id) ?? GENERATORS[0]!;
}

export function taskIsMc(gen: GeneratorModule, task: string | undefined): boolean {
  if (!task) return true; // "auto" resolves to an MC-capable task in MC mode
  return gen.tasks.find((t) => t.value === task)?.mc ?? false;
}
