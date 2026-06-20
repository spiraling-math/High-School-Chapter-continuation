/** Question-bank panel: save, search, filter, open, duplicate, archive, delete. */

import { el, clear, toast, announce } from "./dom.ts";
import type { Studio } from "./context.ts";
import { makeRecord, duplicateRecord } from "../../core/bank/record.ts";
import { validate } from "../../domains/sequences/validate.ts";
import type { BankRecord } from "../../core/bank/types.ts";
import { exportToolbar } from "./exports.ts";

function shortHex(): string {
  const b = new Uint8Array(4);
  globalThis.crypto.getRandomValues(b);
  return Array.from(b, (x) => x.toString(16).padStart(2, "0")).join("");
}

async function save(studio: Studio): Promise<void> {
  if (!studio.item || !studio.validation) return;
  const now = new Date().toISOString();
  const rec: BankRecord = studio.record
    ? { ...studio.record, item: studio.item, modifiedAt: now }
    : makeRecord(studio.item, studio.validation.status, { mode: studio.mode, genConfig: studio.genConfig });
  await studio.store.put(rec);
  studio.record = rec;
  toast("Saved to bank");
  studio.rerender();
}

async function open(studio: Studio, id: string): Promise<void> {
  const rec = await studio.store.get(id);
  if (!rec) return;
  studio.record = rec;
  studio.item = rec.item;
  studio.mode = rec.mode;
  studio.genConfig = rec.genConfig;
  studio.validation = validate(rec.item);
  announce(`Opened item ${id} from the bank.`);
  studio.rerender();
}

async function duplicate(studio: Studio, rec: BankRecord): Promise<void> {
  const copy = duplicateRecord(rec, `${rec.itemId}-c${shortHex()}`);
  await studio.store.put(copy);
  toast("Duplicated as a draft copy");
  studio.rerender();
}

async function toggleArchive(studio: Studio, rec: BankRecord): Promise<void> {
  await studio.store.put({ ...rec, archived: !rec.archived, modifiedAt: new Date().toISOString() });
  studio.rerender();
}

async function remove(studio: Studio, rec: BankRecord): Promise<void> {
  if (!window.confirm(`Delete item ${rec.itemId} permanently? This cannot be undone.`)) return;
  await studio.store.delete(rec.itemId);
  if (studio.record?.itemId === rec.itemId) studio.record = null;
  toast("Deleted");
  studio.rerender();
}

function recordRow(studio: Studio, rec: BankRecord): HTMLElement {
  const title = rec.wording.title || `${rec.task} · seed ${rec.seed}`;
  const sub = `band ${rec.band} · ${rec.lifecycleState} · validation ${rec.validationStatus}` +
    (rec.archived ? " · archived" : "");
  const left = el("div", {},
    el("div", { class: "t" }, title),
    el("div", { class: "s" }, sub),
  );
  const actions = el("div", { class: "row" });
  const openBtn = el("button", { type: "button", class: "ghost" }, "Open");
  openBtn.addEventListener("click", () => void open(studio, rec.itemId));
  const dupBtn = el("button", { type: "button", class: "ghost" }, "Duplicate");
  dupBtn.addEventListener("click", () => void duplicate(studio, rec));
  const arcBtn = el("button", { type: "button", class: "ghost" }, rec.archived ? "Unarchive" : "Archive");
  arcBtn.addEventListener("click", () => void toggleArchive(studio, rec));
  const delBtn = el("button", { type: "button", class: "ghost", "aria-label": `Delete ${rec.itemId}` }, "Delete");
  delBtn.addEventListener("click", () => void remove(studio, rec));
  actions.append(openBtn, dupBtn, arcBtn, delBtn);

  return el("li", { class: "rec" }, left, actions);
}

async function refreshList(studio: Studio, listEl: HTMLElement): Promise<void> {
  const recs = await studio.store.query(studio.filter);
  clear(listEl);
  if (recs.length === 0) {
    listEl.append(el("li", { class: "rec" }, el("div", { class: "s" }, "No items match. Generate and save one.")));
    return;
  }
  for (const r of recs) listEl.append(recordRow(studio, r));
}

export function mountBank(studio: Studio, host: HTMLElement): void {
  clear(host);
  host.append(el("h2", {}, "Question bank"));

  const saveBtn = el("button", { type: "button", class: "primary", id: "save" }, "Save current to bank");
  saveBtn.addEventListener("click", () => void save(studio));
  if (!studio.item) saveBtn.setAttribute("disabled", "true");
  host.append(saveBtn);

  // Filters
  const filters = el("div", { class: "field", role: "group", "aria-label": "Bank filters" });
  const search = el("input", { id: "bank-search", type: "search", placeholder: "Search wording / tags…", "aria-label": "Search the bank" });
  search.value = studio.filter.text ?? "";
  search.addEventListener("input", () => { studio.filter.text = search.value || undefined; void refreshList(studio, list); });

  const taskFilter = el("select", { "aria-label": "Filter by task" });
  taskFilter.append(new Option("All tasks", ""), new Option("nth term", "nth_term"), new Option("Sum", "sum_n"),
    new Option("Find d", "find_d"), new Option("Find n", "find_n_for_value"));
  taskFilter.value = studio.filter.task ?? "";
  taskFilter.addEventListener("change", () => { studio.filter.task = taskFilter.value || undefined; void refreshList(studio, list); });

  const archFilter = el("select", { "aria-label": "Filter by archive status" });
  archFilter.append(new Option("Active", "false"), new Option("Archived", "true"), new Option("All", "all"));
  archFilter.value = studio.filter.archived === undefined ? "all" : String(studio.filter.archived);
  archFilter.addEventListener("change", () => {
    studio.filter.archived = archFilter.value === "all" ? undefined : archFilter.value === "true";
    void refreshList(studio, list);
  });

  const frow = el("div", { class: "row" });
  frow.append(taskFilter, archFilter);
  filters.append(search, frow);
  host.append(filters);

  host.append(exportToolbar(studio));

  const list = el("ul", { class: "list", "aria-label": "Saved items", role: "list" });
  host.append(list);
  void refreshList(studio, list);
}
