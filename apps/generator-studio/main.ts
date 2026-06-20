/**
 * SPI-Math Generator Studio — application entry (shell).
 *
 * This file builds the page shell, the generation controls, and the four
 * preview views (Question / Answer / Worked solution / Validation), rendering
 * mathematics with the locally-bundled KaTeX. The IndexedDB bank, difficulty
 * controls, wording editing, lifecycle, and exports are layered in by sibling
 * modules in later increments.
 *
 * No network, no CDN: KaTeX is provided by the inlined script (window.katex).
 */

import { generate, GENERATOR_ID, GENERATOR_VERSION, type Task } from "../../domains/sequences/arithmetic.ts";
import { validate } from "../../domains/sequences/validate.ts";
import {
  renderQuestionTeacher, renderAnswer, renderSolution, renderValidation,
} from "./render/katex-render.ts";
import type { Json } from "../../core/serialization/canonical.ts";

const katex = window.katex;

function el<K extends keyof HTMLElementTagNameMap>(
  tag: K, attrs: Record<string, string> = {}, ...children: (Node | string)[]
): HTMLElementTagNameMap[K] {
  const node = document.createElement(tag);
  for (const [k, v] of Object.entries(attrs)) {
    if (k === "class") node.className = v;
    else node.setAttribute(k, v);
  }
  for (const c of children) node.append(c);
  return node;
}

interface State { item: Record<string, Json>; validation: ReturnType<typeof validate>; }
let state: State | null = null;

const VIEWS = [
  { id: "question", label: "Question" },
  { id: "answer", label: "Answer" },
  { id: "solution", label: "Worked solution" },
  { id: "validation", label: "Validation" },
] as const;
type ViewId = (typeof VIEWS)[number]["id"];
let activeView: ViewId = "question";

function randomSeed(): number {
  // 32-bit seed; crypto when available, else time-free fallback is not needed
  // because the user explicitly requests a fresh random seed here.
  const buf = new Uint32Array(1);
  (globalThis.crypto ?? ({ getRandomValues: (b: Uint32Array) => { b[0] = 0; return b; } } as Crypto)).getRandomValues(buf);
  return buf[0]!;
}

function readControls(): { seed: number; task: Task | undefined; mode: "integer" | "multiple-choice" } {
  const seed = Number((document.getElementById("seed") as HTMLInputElement).value) >>> 0;
  const taskSel = (document.getElementById("task") as HTMLSelectElement).value;
  const mode = (document.getElementById("mode") as HTMLSelectElement).value as "integer" | "multiple-choice";
  const task = taskSel === "auto" ? undefined : (taskSel as Task);
  return { seed, task, mode };
}

function announce(msg: string): void {
  const live = document.getElementById("live")!;
  live.textContent = msg;
}

function doGenerate(): void {
  const { seed, task, mode } = readControls();
  let item: Record<string, Json>;
  try {
    item = generate(seed, task ? { task, answerType: mode } : { answerType: mode });
  } catch (err) {
    announce(`Cannot generate: ${(err as Error).message}`);
    return;
  }
  state = { item, validation: validate(item) };
  renderPreview();
  announce(`Generated ${item["params"] && (item["params"] as { task: string }).task} item from seed ${seed}.`);
}

function renderMeta(item: Record<string, Json>): HTMLElement {
  const p = item["params"] as { task: string; a1: number; d: number; n: number };
  const diff = item["difficulty"] as { overallBand: number };
  const lifecycleState = (item["lifecycle"] as { state: string }).state;
  const dl = el("dl", { class: "meta-grid" });
  const rows: [string, string][] = [
    ["Generator", `${GENERATOR_ID} v${GENERATOR_VERSION}`],
    ["Seed", String(item["seed"])],
    ["Task", p.task],
    ["Parameters", `a1=${p.a1}, d=${p.d}, n=${p.n}`],
    ["Objective", (item["objectiveIds"] as string[])[0]!],
    ["Difficulty band", String(diff.overallBand)],
  ];
  for (const [k, v] of rows) { dl.append(el("dt", {}, k), el("dd", {}, v)); }
  const badge = el("span", { class: "badge state" }, lifecycleState);
  return el("div", {}, badge, dl);
}

function renderPreview(): void {
  const host = document.getElementById("preview")!;
  host.replaceChildren();
  if (!state) { host.append(el("p", {}, "Generate an item to preview it.")); return; }

  host.append(renderMeta(state.item));

  // Tabs
  const tablist = el("div", { class: "tabs", role: "tablist", "aria-label": "Item views" });
  for (const v of VIEWS) {
    const selected = v.id === activeView;
    const tab = el("button", {
      class: "tab", role: "tab", id: `tab-${v.id}`, "aria-controls": `panel-${v.id}`,
      "aria-selected": String(selected), tabindex: selected ? "0" : "-1",
    }, v.label);
    tab.addEventListener("click", () => { activeView = v.id; renderPreview(); (document.getElementById(`tab-${v.id}`))?.focus(); });
    tab.addEventListener("keydown", (e) => onTabKey(e as KeyboardEvent));
    tablist.append(tab);
  }
  host.append(tablist);

  const panel = el("div", { role: "tabpanel", id: `panel-${activeView}`, "aria-labelledby": `tab-${activeView}`, tabindex: "0" });
  panel.innerHTML = viewHtml(activeView);
  host.append(panel);
}

function viewHtml(view: ViewId): string {
  if (!state) return "";
  switch (view) {
    case "question": return renderQuestionTeacher(state.item, katex);
    case "answer": return renderAnswer(state.item);
    case "solution": return renderSolution(state.item, katex);
    case "validation": return renderValidation(state.validation);
  }
}

function onTabKey(e: KeyboardEvent): void {
  const idx = VIEWS.findIndex((v) => v.id === activeView);
  let next = idx;
  if (e.key === "ArrowRight") next = (idx + 1) % VIEWS.length;
  else if (e.key === "ArrowLeft") next = (idx - 1 + VIEWS.length) % VIEWS.length;
  else if (e.key === "Home") next = 0;
  else if (e.key === "End") next = VIEWS.length - 1;
  else return;
  e.preventDefault();
  activeView = VIEWS[next]!.id;
  renderPreview();
  document.getElementById(`tab-${activeView}`)?.focus();
}

function controlsPanel(): HTMLElement {
  const panel = el("section", { class: "panel controls", "aria-label": "Generation controls" });
  panel.append(el("h2", {}, "Generate"));

  const seedField = el("div", { class: "field" });
  seedField.append(el("label", { for: "seed" }, "Seed"));
  const seedRow = el("div", { class: "row" });
  const seedInput = el("input", { id: "seed", type: "number", value: "1", min: "0", inputmode: "numeric" });
  const rnd = el("button", { type: "button", class: "ghost", id: "random", "aria-label": "Use a random seed" }, "🎲 Random");
  rnd.addEventListener("click", () => { seedInput.value = String(randomSeed()); doGenerate(); });
  seedRow.append(seedInput, rnd);
  seedField.append(seedRow, el("div", { class: "hint" }, "The same seed, mode, and generator version reproduce an identical item."));

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

  const gen = el("button", { type: "button", class: "primary", id: "generate" }, "Generate");
  gen.addEventListener("click", doGenerate);

  panel.append(seedField, modeField, taskField, gen);
  return panel;
}

function main(): void {
  const app = document.getElementById("app")!;
  app.append(
    el("header", { class: "app-header" },
      el("h1", {}, "SPI-Math Generator Studio"),
      el("span", { class: "tag" }, "arithmetic sequences · offline"),
    ),
  );
  const mainEl = el("main", { id: "main" });
  const layout = el("div", { class: "layout" });
  layout.append(controlsPanel(), el("section", { class: "panel", id: "preview", "aria-label": "Item preview", "aria-live": "off" }));
  mainEl.append(layout);
  app.append(mainEl);
  app.append(el("div", { id: "live", class: "sr-only", role: "status", "aria-live": "polite" }));

  doGenerate();
}

main();
