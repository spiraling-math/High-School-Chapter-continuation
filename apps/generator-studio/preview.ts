/** Preview panel: metadata, reproduction info, and the four item views. */

import { el, clear, toast } from "./dom.ts";
import type { Studio } from "./context.ts";
import { displayItem } from "./wording.ts";
import {
  renderQuestionTeacher, renderAnswer, renderSolution, renderValidation,
} from "./render/katex-render.ts";
import type { Json } from "../../core/serialization/canonical.ts";

const VIEWS = [
  { id: "question", label: "Question" },
  { id: "answer", label: "Answer" },
  { id: "solution", label: "Worked solution" },
  { id: "validation", label: "Validation" },
] as const;
type ViewId = (typeof VIEWS)[number]["id"];
let activeView: ViewId = "question";

function paramSummary(params: Record<string, unknown>): string {
  return Object.entries(params)
    .filter(([k]) => k !== "task")
    .map(([k, v]) => `${k}=${formatParam(v)}`)
    .join(", ");
}

function formatParam(v: unknown): string {
  if (v && typeof v === "object" && "num" in v && "den" in v) {
    const r = v as { num: number; den: number };
    return r.den === 1 ? String(r.num) : `${r.num}/${r.den}`;
  }
  // Structured params (e.g. a function rule {kind, a, b} or a list of ordered pairs) are shown recursively,
  // never as "[object Object]".
  if (Array.isArray(v)) return `[${v.map(formatParam).join(", ")}]`;
  if (v && typeof v === "object") {
    return `{${Object.entries(v as Record<string, unknown>).map(([k, x]) => `${k}: ${formatParam(x)}`).join(", ")}}`;
  }
  return String(v);
}

function meta(studio: Studio): HTMLElement {
  const item = studio.item!;
  const p = item["params"] as Record<string, unknown> & { task: string };
  const band = (item["difficulty"] as { overallBand: number }).overallBand;
  const lifecycle = studio.record?.lifecycleState ?? (item["lifecycle"] as { state: string }).state;
  const genId = String(item["generatorId"]);
  const genVer = String(item["generatorVersion"]);

  const interaction = String(item["interactionType"] ?? (studio.mode === "multiple-choice" ? "multiple-choice" : "free-response"));
  const answerType = String((item["answer"] as { type?: string }).type ?? "");
  const dl = el("dl", { class: "meta-grid" });
  const rows: [string, string][] = [
    ["Seed", String(item["seed"])],
    ["Task", p.task],
    ["Parameters", paramSummary(p)],
    ["Objective", (item["objectiveIds"] as string[])[0]!],
    ["Difficulty band", String(band)],
    ["Interaction", interaction],
    ["Answer type", answerType],
  ];
  for (const [k, v] of rows) dl.append(el("dt", {}, k), el("dd", {}, v));

  const repro = {
    generatorId: genId,
    generatorVersion: genVer,
    seed: item["seed"],
    config: studio.record?.genConfig ?? studio.genConfig,
  };
  const copyBtn = el("button", { type: "button", class: "ghost", "aria-label": "Copy reproduction details" }, "Copy reproduction");
  copyBtn.addEventListener("click", async () => {
    try { await navigator.clipboard.writeText(JSON.stringify(repro, null, 2)); toast("Reproduction details copied"); }
    catch { toast("Clipboard unavailable"); }
  });

  return el("div", {},
    el("span", { class: "badge state" }, lifecycle),
    el("span", { class: "badge" }, `${genId} v${genVer}`),
    dl,
    el("p", { class: "hint" }, "Reproducible from generator version + seed + config."),
    copyBtn,
  );
}

function viewHtml(studio: Studio, view: ViewId): string {
  const item = studio.item!;
  const shown = displayItem(item, studio.record?.wording);
  switch (view) {
    case "question": return renderQuestionTeacher(shown, window.katex);
    case "answer": return renderAnswer(item as Record<string, Json>);
    case "solution": return renderSolution(item, window.katex);
    case "validation": return renderValidation(studio.validation!);
  }
}

export function mountPreview(studio: Studio, host: HTMLElement): void {
  clear(host);
  host.append(el("h2", {}, "Preview"));
  if (!studio.item) { host.append(el("p", {}, "Generate an item to preview it.")); return; }

  host.append(meta(studio));

  const tablist = el("div", { class: "tabs", role: "tablist", "aria-label": "Item views" });
  for (const v of VIEWS) {
    const selected = v.id === activeView;
    const tab = el("button", {
      class: "tab", role: "tab", id: `tab-${v.id}`, "aria-controls": `panel-${v.id}`,
      "aria-selected": String(selected), tabindex: selected ? "0" : "-1",
    }, v.label);
    tab.addEventListener("click", () => { activeView = v.id; mountPreview(studio, host); document.getElementById(`tab-${v.id}`)?.focus(); });
    tab.addEventListener("keydown", (e) => onTabKey(studio, host, e as KeyboardEvent));
    tablist.append(tab);
  }
  host.append(tablist);

  const panel = el("div", { role: "tabpanel", id: `panel-${activeView}`, "aria-labelledby": `tab-${activeView}`, tabindex: "0" });
  panel.innerHTML = viewHtml(studio, activeView);
  host.append(panel);
}

function onTabKey(studio: Studio, host: HTMLElement, e: KeyboardEvent): void {
  const idx = VIEWS.findIndex((v) => v.id === activeView);
  let next = idx;
  if (e.key === "ArrowRight") next = (idx + 1) % VIEWS.length;
  else if (e.key === "ArrowLeft") next = (idx - 1 + VIEWS.length) % VIEWS.length;
  else if (e.key === "Home") next = 0;
  else if (e.key === "End") next = VIEWS.length - 1;
  else return;
  e.preventDefault();
  activeView = VIEWS[next]!.id;
  mountPreview(studio, host);
  document.getElementById(`tab-${activeView}`)?.focus();
}
