/**
 * Edit panel: protected mathematical parameters (read-only) vs. editable wording,
 * plus lifecycle state. Wording and lifecycle edits never mutate the item's math.
 */

import { el, clear, toast } from "./dom.ts";
import type { Studio } from "./context.ts";
import { wordingTexts } from "./wording.ts";
import { makeRecord, withWording, withLifecycle } from "../../core/bank/record.ts";
import { APP_SETTABLE_STATES, type LifecycleState, type WordingOverlay } from "../../core/bank/types.ts";

function ensureRecord(studio: Studio) {
  if (!studio.record) {
    studio.record = makeRecord(studio.item!, studio.validation!.status, { mode: studio.mode });
  }
  return studio.record;
}

function fmtParam(v: unknown): string {
  if (v && typeof v === "object" && "num" in v && "den" in v) {
    const r = v as { num: number; den: number };
    return r.den === 1 ? String(r.num) : `${r.num}/${r.den}`;
  }
  // Structured params (e.g. a function rule {kind, a, b} or a list of ordered pairs) are shown recursively,
  // never as "[object Object]".
  if (Array.isArray(v)) return `[${v.map(fmtParam).join(", ")}]`;
  if (v && typeof v === "object") {
    return `{${Object.entries(v as Record<string, unknown>).map(([k, x]) => `${k}: ${fmtParam(x)}`).join(", ")}}`;
  }
  return String(v);
}

function protectedSection(studio: Studio): HTMLElement {
  const item = studio.item!;
  const p = item["params"] as Record<string, unknown> & { task: string };
  const answer = (item["answer"] as { display: string }).display;
  const sec = el("div", { class: "field" });
  sec.append(el("label", {}, "Protected mathematics (regenerate to change)"));
  const grid = el("div", { class: "row" });
  for (const [k, v] of Object.entries(p)) {
    if (k === "task") continue;
    const wrap = el("div", {});
    wrap.append(el("label", { for: `prot-${k}` }, k));
    const inp = el("input", { id: `prot-${k}`, class: "protected", value: fmtParam(v), readonly: "true", "aria-readonly": "true", tabindex: "-1" });
    inp.setAttribute("disabled", "true");
    wrap.append(inp);
    grid.append(wrap);
  }
  sec.append(grid);
  sec.append(el("p", { class: "hint" }, `Task ${p.task} · canonical answer ${answer}. These are locked; wording edits below cannot change them.`));
  return sec;
}

function wordingSection(studio: Studio): HTMLElement {
  const item = studio.item!;
  const texts = wordingTexts(item, studio.record?.wording);
  const sec = el("div", { class: "field editable" });
  sec.append(el("label", {}, "Editable wording"));

  const titleInput = el("input", { id: "wording-title", type: "text", placeholder: "Optional item title", "aria-label": "Item title" });
  titleInput.value = studio.record?.wording.title ?? "";
  sec.append(titleInput);

  const areas: HTMLTextAreaElement[] = [];
  texts.forEach((t, i) => {
    const ta = el("textarea", { id: `wording-${i}`, rows: "2", "aria-label": `Prompt line ${i + 1}` }) as HTMLTextAreaElement;
    ta.value = t;
    areas.push(ta);
    sec.append(ta);
  });

  const apply = el("button", { type: "button", class: "primary" }, "Apply wording");
  apply.addEventListener("click", async () => {
    const overlay: WordingOverlay = {
      title: titleInput.value.trim() || undefined,
      blocks: areas.map((a) => a.value),
    };
    const rec = withWording(ensureRecord(studio), overlay);
    await studio.store.put(rec);
    studio.record = rec;
    toast("Wording applied (mathematics unchanged)");
    studio.rerender();
  });
  sec.append(apply);
  sec.append(el("p", { class: "hint" }, "Editing wording updates display text only; the saved item's math is untouched."));
  return sec;
}

function lifecycleSection(studio: Studio): HTMLElement {
  const sec = el("div", { class: "field" });
  sec.append(el("label", { for: "lifecycle" }, "Lifecycle state"));
  const sel = el("select", { id: "lifecycle" });
  const current = studio.record?.lifecycleState ?? "machine-validated";
  for (const s of APP_SETTABLE_STATES) {
    const opt = new Option(s, s);
    if (s === current) opt.selected = true;
    sel.append(opt);
  }
  sel.addEventListener("change", async () => {
    const rec = withLifecycle(ensureRecord(studio), sel.value as LifecycleState);
    await studio.store.put(rec);
    studio.record = rec;
    toast(`Lifecycle set to ${sel.value}`);
    studio.rerender();
  });
  sec.append(sel);
  sec.append(el("p", { class: "hint" }, "Approved / published are reserved for the curriculum authority and are not settable here."));
  return sec;
}

export function mountEdit(studio: Studio, host: HTMLElement): void {
  clear(host);
  host.append(el("h2", {}, "Edit"));
  if (!studio.item) { host.append(el("p", {}, "Generate or open an item to edit it.")); return; }
  host.append(protectedSection(studio), wordingSection(studio), lifecycleSection(studio));
}
