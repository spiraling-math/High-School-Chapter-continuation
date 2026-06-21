/**
 * Interaction-type resolution (TD-1, back-compatible).
 *
 * The legacy config key `answerType` conflated interaction mode with the
 * mathematical answer type. The forward standard uses `interactionType`. This
 * resolver maps the legacy values 1:1 and deterministically, so existing seeds,
 * fixtures, and stored bank `genConfig` reproduce byte-for-byte. See TECH_DEBT.md
 * TD-1 and GENERATOR_SDK_DESIGN.md §4.
 */

import type { InteractionType, GenConfig } from "./generator-module.ts";

export function resolveInteractionType(config: GenConfig): InteractionType {
  const fromInteraction =
    config.interactionType === "free-response" || config.interactionType === "multiple-choice"
      ? config.interactionType
      : undefined;
  const fromAnswerType =
    config.answerType === "multiple-choice" ? "multiple-choice"
    : config.answerType === "integer" ? "free-response" // legacy "integer" meant free-response
    : undefined;

  // Reject when both fields are supplied and disagree; accept when they agree.
  if (fromInteraction && fromAnswerType && fromInteraction !== fromAnswerType) {
    throw new Error(
      `conflicting configuration: interactionType='${config.interactionType}' vs answerType='${config.answerType}'`,
    );
  }
  return fromInteraction ?? fromAnswerType ?? "free-response";
}

/** The legacy answerType selector equivalent to a given interaction type, for
 *  generators not yet migrated off the legacy key. */
export function legacyAnswerType(interaction: InteractionType): "integer" | "multiple-choice" {
  return interaction === "multiple-choice" ? "multiple-choice" : "integer";
}
