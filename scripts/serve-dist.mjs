/** Minimal, dependency-free static server for the built Studio (preview only). */

import { createServer } from "node:http";
import { readFile } from "node:fs/promises";
import { join, dirname, extname } from "node:path";
import { fileURLToPath } from "node:url";

const ROOT = join(dirname(dirname(fileURLToPath(import.meta.url))), "apps", "generator-studio", "dist");
const PORT = Number(process.env.PORT ?? 5173);
const MIME = { ".html": "text/html", ".json": "application/json", ".js": "text/javascript", ".css": "text/css" };

createServer(async (req, res) => {
  try {
    let p = decodeURIComponent((req.url ?? "/").split("?")[0]);
    if (p === "/") p = "/index.html";
    const data = await readFile(join(ROOT, p));
    res.writeHead(200, { "content-type": MIME[extname(p)] ?? "application/octet-stream" });
    res.end(data);
  } catch {
    res.writeHead(404);
    res.end("not found");
  }
}).listen(PORT, () => console.log(`serving ${ROOT} on http://localhost:${PORT}`));
