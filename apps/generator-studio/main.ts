/**
 * SPI-Math Generator Studio — application entry.
 *
 * Composes the controls, preview, edit, and bank panels over a shared Studio
 * context backed by the IndexedDB bank. No network, no CDN: KaTeX is provided
 * by the inlined script (window.katex). The Python oracle is a development
 * reference only and is never loaded here.
 */

import { el } from "./dom.ts";
import type { Studio } from "./context.ts";
import { IndexedDBBankStore } from "../../core/bank/indexeddb-store.ts";
import { GENERATORS } from "./generators.ts";
import { controlsPanel, doGenerate } from "./controls.ts";
import { mountPreview } from "./preview.ts";
import { mountEdit } from "./edit-panel.ts";
import { mountBank } from "./bank-panel.ts";

function main(): void {
  const app = document.getElementById("app")!;
  app.append(
    el("header", { class: "app-header" },
      el("h1", {}, "SPI-Math Generator Studio"),
      el("span", { class: "tag" }, "sequences · offline"),
    ),
  );

  const studio: Studio = {
    store: new IndexedDBBankStore(),
    item: null,
    validation: null,
    record: null,
    mode: "multiple-choice",
    generatorId: GENERATORS[0]!.id,
    genConfig: { answerType: "multiple-choice" },
    filter: { archived: false },
    rerender: () => undefined,
  };

  const previewEl = el("section", { class: "panel", id: "preview", "aria-label": "Item preview" });
  const editEl = el("section", { class: "panel", id: "edit", "aria-label": "Edit item" });
  const bankEl = el("section", { class: "panel", id: "bank", "aria-label": "Question bank" });

  const leftCol = el("div", { class: "col" });
  leftCol.append(controlsPanel(studio), bankEl);
  const rightCol = el("div", { class: "col" });
  rightCol.append(previewEl, editEl);

  const layout = el("div", { class: "layout" });
  layout.append(leftCol, rightCol);

  const mainEl = el("main", { id: "main" });
  mainEl.append(layout);
  app.append(mainEl);
  app.append(el("div", { id: "live", class: "sr-only", role: "status", "aria-live": "polite" }));

  studio.rerender = () => {
    mountPreview(studio, previewEl);
    mountEdit(studio, editEl);
    mountBank(studio, bankEl);
  };

  doGenerate(studio); // initial item
}

main();
