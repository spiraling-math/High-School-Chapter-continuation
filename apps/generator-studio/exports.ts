/** Export/import toolbar: standalone HTML exports and JSON round-trip. */

import { el, toast, announce } from "./dom.ts";
import type { Studio } from "./context.ts";
import type { BankRecord } from "../../core/bank/types.ts";
import { studentWorksheet } from "../../exporters/html/worksheet.ts";
import { answerKey } from "../../exporters/html/answer-key.ts";
import { workedSolutions } from "../../exporters/html/solutions.ts";
import { exportBankJson, importBankJson } from "../../exporters/json/bank-json.ts";

function download(name: string, mime: string, content: string): void {
  const blob = new Blob([content], { type: mime });
  const url = URL.createObjectURL(blob);
  const a = el("a", { href: url, download: name });
  document.body.append(a);
  a.click();
  a.remove();
  URL.revokeObjectURL(url);
}

async function currentRecords(studio: Studio): Promise<BankRecord[]> {
  return studio.store.query(studio.filter);
}

export function exportToolbar(studio: Studio): HTMLElement {
  const bar = el("div", { class: "field", role: "group", "aria-label": "Exports" });
  bar.append(el("label", {}, "Export current view"));

  const row1 = el("div", { class: "row" });
  const ws = el("button", { type: "button", class: "ghost" }, "Worksheet");
  ws.addEventListener("click", async () => {
    const rs = await currentRecords(studio);
    if (!rs.length) { toast("Nothing to export"); return; }
    download("spi-math-worksheet.html", "text/html",
      studentWorksheet(rs, { katex: window.katex, title: "SPI-Math Worksheet", instructions: "Answer all questions. Show your working." }));
  });
  const ak = el("button", { type: "button", class: "ghost" }, "Answer key");
  ak.addEventListener("click", async () => {
    const rs = await currentRecords(studio);
    if (!rs.length) { toast("Nothing to export"); return; }
    download("spi-math-answer-key.html", "text/html", answerKey(rs, { title: "SPI-Math Answer Key" }));
  });
  const sol = el("button", { type: "button", class: "ghost" }, "Solutions");
  sol.addEventListener("click", async () => {
    const rs = await currentRecords(studio);
    if (!rs.length) { toast("Nothing to export"); return; }
    download("spi-math-solutions.html", "text/html",
      workedSolutions(rs, { katex: window.katex, katexCss: __KATEX_CSS__, title: "SPI-Math Worked Solutions" }));
  });
  row1.append(ws, ak, sol);

  const row2 = el("div", { class: "row" });
  const ej = el("button", { type: "button", class: "ghost" }, "Export JSON");
  ej.addEventListener("click", async () => {
    const rs = await currentRecords(studio);
    download("spi-math-bank.json", "application/json", exportBankJson(rs));
  });
  const imp = el("button", { type: "button", class: "ghost" }, "Import JSON");
  const fileInput = el("input", { type: "file", accept: "application/json,.json", class: "sr-only", "aria-label": "Import question-bank JSON file" }) as HTMLInputElement;
  imp.addEventListener("click", () => fileInput.click());
  fileInput.addEventListener("change", async () => {
    const f = fileInput.files?.[0];
    if (!f) return;
    const res = importBankJson(await f.text());
    for (const r of res.records) await studio.store.put(r);
    studio.rerender();
    if (res.integrityOk) toast(`Imported ${res.records.length} item(s) — integrity OK`);
    else { toast(`Imported with ${res.errors.length} issue(s)`); announce(res.errors.slice(0, 3).join("; ")); }
    fileInput.value = "";
  });
  row2.append(ej, imp, fileInput);

  bar.append(row1, row2);
  return bar;
}
