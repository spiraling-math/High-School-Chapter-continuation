/**
 * gen.geometry.transformations — describe-task answer checker (owner I, J).
 *
 * Byte-for-byte TypeScript mirror of oracle/spi_oracle/transformations_checker.py.
 */

import { descriptorsEqual, parseDescriptor, deepEqual } from "./transformations-core.ts";

// eslint-disable-next-line @typescript-eslint/no-explicit-any
type Json = any;

export function checkDescription(expected: Json, studentText: string | null | undefined): string {
  const pr = parseDescriptor(studentText);
  if (pr.code !== null) {
    return pr.code;
  }
  const got = pr.descriptor as Json;
  if (got.kind !== expected.kind) {
    return "wrong-transformation-type";
  }
  if (descriptorsEqual(got, expected)) {
    return "correct";
  }
  if (got.kind === "translation") {
    return "wrong-translation-vector";
  }
  if (got.kind === "reflection") {
    return "wrong-reflection-axis";
  }
  // rotation: distinguish a wrong centre from a wrong amount (centre takes priority).
  if (!deepEqual(got.centre, expected.centre)) {
    return "wrong-rotation-centre";
  }
  return "wrong-rotation-amount";
}
