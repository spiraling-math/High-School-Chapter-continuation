/** Tiny DOM helpers for the Studio app. */

export function el<K extends keyof HTMLElementTagNameMap>(
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

export function clear(node: HTMLElement): void {
  node.replaceChildren();
}

export function toast(message: string): void {
  const t = el("div", { class: "toast", role: "status" }, message);
  document.body.append(t);
  window.setTimeout(() => t.remove(), 2600);
}

/** Announce to the polite live region (created in main). */
export function announce(message: string): void {
  const live = document.getElementById("live");
  if (live) live.textContent = message;
}
