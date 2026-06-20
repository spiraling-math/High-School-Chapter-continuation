/**
 * Apply an editable wording overlay to an item for DISPLAY only.
 *
 * Returns a shallow clone with prompt block texts replaced where the overlay
 * provides them. The canonical `item` (params, answer, distractors, solution)
 * is never mutated — this is the mechanism that keeps wording edits from
 * corrupting the protected mathematics.
 */

import type { Json } from "../../core/serialization/canonical.ts";
import type { WordingOverlay } from "../../core/bank/types.ts";

export function displayItem(item: Record<string, Json>, wording?: WordingOverlay): Record<string, Json> {
  if (!wording || (!wording.blocks && !wording.title)) return item;
  const prompt = item["prompt"] as { instruction?: string; blocks: Array<{ kind: string; text?: string }> };
  const blocks = prompt.blocks.map((b, i) => {
    const override = wording.blocks?.[i];
    return override != null && b.kind === "text" ? { ...b, text: override } : b;
  });
  return { ...item, prompt: { ...prompt, blocks } };
}

/** The current display texts for the editable prompt blocks (overlay or original). */
export function wordingTexts(item: Record<string, Json>, wording?: WordingOverlay): string[] {
  const prompt = item["prompt"] as { blocks: Array<{ kind: string; text?: string }> };
  return prompt.blocks.map((b, i) => wording?.blocks?.[i] ?? b.text ?? "");
}
