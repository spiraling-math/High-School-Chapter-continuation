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
  if (config.interactionType === "free-response" || config.interactionType === "multiple-choice") {
    return config.interactionType;
  }
  if (config.answerType === "multiple-choice") return "multiple-choice";
  // Legacy "integer" (which meant free-response) and unset both map to free-response.
  return "free-response";
}

/** The legacy answerType selector equivalent to a given interaction type, for
 *  generators not yet migrated off the legacy key. */
export function legacyAnswerType(interaction: InteractionType): "integer" | "multiple-choice" {
  return interaction === "multiple-choice" ? "multiple-choice" : "integer";
}
