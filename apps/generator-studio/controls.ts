/** Generation controls: generator, seed, random seed, mode, task, target band. */

import { el, announce } from "./dom.ts";
import type { Studio } from "./context.ts";
import { setWorkspace } from "./context.ts";
import { getGenerator, taskIsMc, generatorsForMode, approvalStatusOf, studioMode } from "./generators.ts";
import type { Mode } from "../../core/bank/types.ts";

function randomSeed(): number {
  const buf = new Uint32Array(1);
  globalThis.crypto.getRandomValues(buf);
  return buf[0]!;
}

function readControls(): { generatorId: string; seed: number; task: string | undefined; mode: Mode; band: number | "any" } {
  const generatorId = (document.getElementById("generator") as HTMLSelectElement).value;
  const seed = Number((document.getElementById("seed") as HTMLInputElement).value) >>> 0;
  const taskSel = (document.getElementById("task") as HTMLSelectElement).value;
  const mode = (document.getElementById("mode") as HTMLSelectElement).value as Mode;
  const bandSel = (document.getElementById("band") as HTMLSelectElement).value;
  return { generatorId, seed, task: taskSel === "auto" ? undefined : taskSel, mode, band: bandSel === "any" ? "any" : Number(bandSel) };
}

function findSeedForBand(genId: string, base: number, cfg: { task?: string; answerType: string; interactionType: string }, band: number): number | null {
  const gen = getGenerator(genId);
  for (let i = 0; i < 8000; i++) {
    const s = (base + i) >>> 0;
    const item = gen.generate(s, cfg);
    if ((item["difficulty"] as { overallBand: number }).overallBand === band) return s;
  }
  return null;
}

export function doGenerate(studio: Studio): void {
  const { generatorId, seed, task, mode, band } = readControls();
  const gen = getGenerator(generatorId);
  studio.generatorId = generatorId;
  // Reverse tasks have no multiple-choice variant: fall back to free-response.
  const effectiveMode: Mode = mode === "multiple-choice" && !taskIsMc(gen, task) ? "integer" : mode;
  // Pass BOTH the legacy selector (answerType) and the forward key (interactionType, TD-1): the older families
  // read answerType, the newer ones (ratio, functions) read interactionType only. The two always agree here.
  const interactionType = effectiveMode === "multiple-choice" ? "multiple-choice" : "free-response";
  const cfg = task ? { task, answerType: effectiveMode, interactionType } : { answerType: effectiveMode, interactionType };
  studio.mode = effectiveMode;
  studio.genConfig = task ? { answerType: effectiveMode, interactionType, task } : { answerType: effectiveMode, interactionType };

  let seedUsed = seed;
  if (band !== "any") {
    const found = findSeedForBand(generatorId, seed, cfg, band);
    if (found === null) { announce(`No band-${band} item found near seed ${seed} for this configuration.`); return; }
    seedUsed = found;
  }
  let item: Record<string, unknown>;
  try {
    item = gen.generate(seedUsed, cfg) as unknown as Record<string, unknown>;
  } catch (err) {
    announce(`Cannot generate: ${(err as Error).message}`);
    return;
  }
  (document.getElementById("seed") as HTMLInputElement).value = String(seedUsed);
  const it = item as Parameters<typeof gen.validate>[0];
  setWorkspace(studio, it, gen.validate(it), null);
  if (effectiveMode !== mode) (document.getElementById("mode") as HTMLSelectElement).value = effectiveMode;
  studio.rerender();
  announce(`Generated ${(it["params"] as { task: string }).task} item from seed ${seedUsed}.`);
}

function populateTasks(task: HTMLSelectElement, gen: ReturnType<typeof getGenerator>): void {
  task.replaceChildren();
  task.append(new Option("Auto (any supported)", "auto"));
  for (const t of gen.tasks) task.append(new Option(t.label, t.value));
}

export function controlsPanel(studio: Studio): HTMLElement {
  const panel = el("section", { class: "panel controls", "aria-label": "Generation controls" });
  panel.append(el("h2", {}, "Generate"));

  const mode0 = studioMode();
  const visible = generatorsForMode(mode0);
  // A pending generator must never be the default selection for normal users.
  if (!visible.some((g) => g.id === studio.generatorId)) studio.generatorId = visible[0]!.id;
  const genField = el("div", { class: "field" });
  genField.append(el("label", { for: "generator" }, "Generator"));
  const generator = el("select", { id: "generator" });
  for (const g of visible) {
    const pending = approvalStatusOf(g) === "pending-review";
    generator.append(new Option(pending ? `${g.label} (v${g.version}) — machine-validated, pending curriculum approval` : `${g.label} (v${g.version})`, g.id));
  }
  generator.value = studio.generatorId;
  genField.append(generator);
  if (mode0 === "review") {
    genField.append(el("div", { class: "hint" }, "Review/developer mode: pending-approval generators are shown for inspection only and are not exposed to normal users or production exports."));
  }

  const seedField = el("div", { class: "field" });
  seedField.append(el("label", { for: "seed" }, "Seed"));
  const seedRow = el("div", { class: "row" });
  const seedInput = el("input", { id: "seed", type: "number", value: "1", min: "0", inputmode: "numeric" });
  const rnd = el("button", { type: "button", class: "ghost", "aria-label": "Use a random seed and generate" }, "🎲 Random");
  rnd.addEventListener("click", () => { seedInput.value = String(randomSeed()); doGenerate(studio); });
  seedRow.append(seedInput, rnd);
  seedField.append(seedRow, el("div", { class: "hint" }, "Same generator + seed + config → identical item."));

  const modeField = el("div", { class: "field" });
  modeField.append(el("label", { for: "mode" }, "Mode"));
  const mode = el("select", { id: "mode" });
  mode.append(new Option("Multiple choice", "multiple-choice"), new Option("Free response", "integer"));
  modeField.append(mode);

  const taskField = el("div", { class: "field" });
  taskField.append(el("label", { for: "task" }, "Task"));
  const task = el("select", { id: "task" });
  taskField.append(task, el("div", { class: "hint" }, "Reverse tasks (and sum to infinity) are free-response only."));

  const bandField = el("div", { class: "field" });
  bandField.append(el("label", { for: "band" }, "Target difficulty band"));
  const band = el("select", { id: "band" });
  band.append(new Option("Any", "any"), new Option("1", "1"), new Option("2", "2"), new Option("3", "3"), new Option("4", "4"), new Option("5", "5"));
  bandField.append(band, el("div", { class: "hint" }, "Searches seeds from the entered seed for a matching band."));

  const gen = el("button", { type: "button", class: "primary", id: "generate" }, "Generate");
  gen.addEventListener("click", () => doGenerate(studio));

  // Order: generator, seed, mode, task, band, generate.
  panel.append(genField, seedField, modeField, taskField, bandField, gen);
  populateTasks(task, getGenerator(studio.generatorId));

  generator.addEventListener("change", () => {
    studio.generatorId = generator.value;
    populateTasks(task, getGenerator(generator.value));
  });
  return panel;
}
