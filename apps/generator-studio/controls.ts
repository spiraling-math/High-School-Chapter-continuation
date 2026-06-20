/** Generation controls: seed, random seed, mode, task, target difficulty band. */

import { el, announce } from "./dom.ts";
import type { Studio } from "./context.ts";
import { setWorkspace } from "./context.ts";
import { generate, type Task } from "../../domains/sequences/arithmetic.ts";
import { validate } from "../../domains/sequences/validate.ts";
import type { Mode } from "../../core/bank/types.ts";

function randomSeed(): number {
  const buf = new Uint32Array(1);
  globalThis.crypto.getRandomValues(buf);
  return buf[0]!;
}

function readControls(): { seed: number; task: Task | undefined; mode: Mode; band: number | "any" } {
  const seed = Number((document.getElementById("seed") as HTMLInputElement).value) >>> 0;
  const taskSel = (document.getElementById("task") as HTMLSelectElement).value;
  const mode = (document.getElementById("mode") as HTMLSelectElement).value as Mode;
  const bandSel = (document.getElementById("band") as HTMLSelectElement).value;
  return {
    seed,
    task: taskSel === "auto" ? undefined : (taskSel as Task),
    mode,
    band: bandSel === "any" ? "any" : Number(bandSel),
  };
}

function findSeedForBand(base: number, cfg: { task?: Task; answerType: Mode }, band: number): number | null {
  for (let i = 0; i < 8000; i++) {
    const s = (base + i) >>> 0;
    const item = generate(s, cfg);
    if ((item["difficulty"] as { overallBand: number }).overallBand === band) return s;
  }
  return null;
}

export function doGenerate(studio: Studio): void {
  const { seed, task, mode, band } = readControls();
  studio.mode = mode;
  const cfg = task ? { task, answerType: mode } : { answerType: mode };

  let seedUsed = seed;
  if (band !== "any") {
    const found = findSeedForBand(seed, cfg, band);
    if (found === null) { announce(`No band-${band} item found near seed ${seed} for this configuration.`); return; }
    seedUsed = found;
  }

  let item: Record<string, unknown>;
  try {
    item = generate(seedUsed, cfg) as unknown as Record<string, unknown>;
  } catch (err) {
    announce(`Cannot generate: ${(err as Error).message}`);
    return;
  }
  (document.getElementById("seed") as HTMLInputElement).value = String(seedUsed);
  const it = item as Parameters<typeof validate>[0];
  setWorkspace(studio, it, validate(it), null);
  studio.rerender();
  const p = it["params"] as { task: string };
  announce(`Generated ${p.task} item from seed ${seedUsed}.`);
}

export function controlsPanel(studio: Studio): HTMLElement {
  const panel = el("section", { class: "panel controls", "aria-label": "Generation controls" });
  panel.append(el("h2", {}, "Generate"));

  const seedField = el("div", { class: "field" });
  seedField.append(el("label", { for: "seed" }, "Seed"));
  const seedRow = el("div", { class: "row" });
  const seedInput = el("input", { id: "seed", type: "number", value: "1", min: "0", inputmode: "numeric" });
  const rnd = el("button", { type: "button", class: "ghost", "aria-label": "Use a random seed and generate" }, "🎲 Random");
  rnd.addEventListener("click", () => { seedInput.value = String(randomSeed()); doGenerate(studio); });
  seedRow.append(seedInput, rnd);
  seedField.append(seedRow, el("div", { class: "hint" }, "Same seed + mode + generator version → identical item."));

  const modeField = el("div", { class: "field" });
  modeField.append(el("label", { for: "mode" }, "Mode"));
  const mode = el("select", { id: "mode" });
  mode.append(new Option("Multiple choice", "multiple-choice"), new Option("Integer (free response)", "integer"));
  modeField.append(mode);

  const taskField = el("div", { class: "field" });
  taskField.append(el("label", { for: "task" }, "Task"));
  const task = el("select", { id: "task" });
  task.append(
    new Option("Auto (any supported)", "auto"),
    new Option("nth term", "nth_term"),
    new Option("Sum of first n terms", "sum_n"),
    new Option("Find common difference", "find_d"),
    new Option("Find term index", "find_n_for_value"),
  );
  taskField.append(task, el("div", { class: "hint" }, "Reverse tasks are integer free-response only."));

  const bandField = el("div", { class: "field" });
  bandField.append(el("label", { for: "band" }, "Target difficulty band"));
  const band = el("select", { id: "band" });
  band.append(new Option("Any", "any"), new Option("1", "1"), new Option("2", "2"), new Option("3", "3"), new Option("4", "4"));
  bandField.append(band, el("div", { class: "hint" }, "Searches seeds from the entered seed for a matching band."));

  const gen = el("button", { type: "button", class: "primary", id: "generate" }, "Generate");
  gen.addEventListener("click", () => doGenerate(studio));

  panel.append(seedField, modeField, taskField, bandField, gen);
  return panel;
}
