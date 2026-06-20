/**
 * IndexedDB-backed BankStore with versioned schema migrations.
 *
 * Migrations are an ordered list: MIGRATIONS[v] upgrades the database to
 * version v+1. The current DB_VERSION is the list length. The IDBFactory is
 * injectable so the same code runs in the browser (globalThis.indexedDB) and in
 * Node tests (fake-indexeddb). This is a storage adapter behind the BankStore
 * interface — generator/validation logic never depends on it, so a future cloud
 * backend can replace it without changes elsewhere.
 */

import type { BankRecord, BankQuery, BankStore } from "./types.ts";

const STORE = "items";

type Migration = (db: IDBDatabase, tx: IDBTransaction) => void;

/** Ordered migrations. Index v migrates the DB to version v+1. */
export const MIGRATIONS: Migration[] = [
  // v1 — create the object store and the base indexes.
  (db) => {
    const os = db.createObjectStore(STORE, { keyPath: "itemId" });
    os.createIndex("generatorId", "generatorId");
    os.createIndex("objectiveId", "objectiveId");
    os.createIndex("task", "task");
    os.createIndex("band", "band");
    os.createIndex("lifecycleState", "lifecycleState");
    os.createIndex("seed", "seed");
  },
  // v2 — add a multiEntry tags index and backfill existing records.
  (_db, tx) => {
    const os = tx.objectStore(STORE);
    os.createIndex("tags", "tags", { multiEntry: true });
    const cursorReq = os.openCursor();
    cursorReq.onsuccess = () => {
      const cur = cursorReq.result;
      if (!cur) return;
      const v = cur.value as BankRecord;
      let changed = false;
      if (!Array.isArray(v.tags)) { v.tags = []; changed = true; }
      if (typeof v.archived !== "boolean") { v.archived = false; changed = true; }
      if (v.schemaRev !== 2) { v.schemaRev = 2; changed = true; }
      if (changed) cur.update(v);
      cur.continue();
    };
  },
];

export const DB_VERSION = MIGRATIONS.length;

function pr<T>(req: IDBRequest<T>): Promise<T> {
  return new Promise((resolve, reject) => {
    req.onsuccess = () => resolve(req.result);
    req.onerror = () => reject(req.error);
  });
}

function openDb(factory: IDBFactory, name: string, version: number): Promise<IDBDatabase> {
  return new Promise((resolve, reject) => {
    const req = factory.open(name, version);
    req.onupgradeneeded = (e) => {
      const db = req.result;
      const tx = req.transaction!;
      for (let v = e.oldVersion; v < version; v++) MIGRATIONS[v]!(db, tx);
    };
    req.onsuccess = () => resolve(req.result);
    req.onerror = () => reject(req.error);
    req.onblocked = () => reject(new Error("IndexedDB open blocked by another connection"));
  });
}

export interface IndexedDBBankStoreOptions {
  factory?: IDBFactory;
  name?: string;
  /** Override for migration tests; defaults to DB_VERSION. */
  version?: number;
}

export class IndexedDBBankStore implements BankStore {
  private readonly factory: IDBFactory;
  private readonly name: string;
  private readonly version: number;
  private dbPromise: Promise<IDBDatabase> | null = null;

  constructor(opts: IndexedDBBankStoreOptions = {}) {
    const factory = opts.factory ?? (globalThis as { indexedDB?: IDBFactory }).indexedDB;
    if (!factory) throw new Error("No IndexedDB available; provide opts.factory");
    this.factory = factory;
    this.name = opts.name ?? "spi-math-bank";
    this.version = opts.version ?? DB_VERSION;
  }

  private db(): Promise<IDBDatabase> {
    if (!this.dbPromise) this.dbPromise = openDb(this.factory, this.name, this.version);
    return this.dbPromise;
  }

  async put(rec: BankRecord): Promise<void> {
    const db = await this.db();
    const tx = db.transaction(STORE, "readwrite");
    tx.objectStore(STORE).put(rec);
    await txDone(tx);
  }

  async get(id: string): Promise<BankRecord | undefined> {
    const db = await this.db();
    const tx = db.transaction(STORE, "readonly");
    return (await pr(tx.objectStore(STORE).get(id))) as BankRecord | undefined;
  }

  async delete(id: string): Promise<void> {
    const db = await this.db();
    const tx = db.transaction(STORE, "readwrite");
    tx.objectStore(STORE).delete(id);
    await txDone(tx);
  }

  async count(): Promise<number> {
    const db = await this.db();
    const tx = db.transaction(STORE, "readonly");
    return pr(tx.objectStore(STORE).count());
  }

  async clear(): Promise<void> {
    const db = await this.db();
    const tx = db.transaction(STORE, "readwrite");
    tx.objectStore(STORE).clear();
    await txDone(tx);
  }

  async query(q: BankQuery = {}): Promise<BankRecord[]> {
    const db = await this.db();
    const tx = db.transaction(STORE, "readonly");
    const all = (await pr(tx.objectStore(STORE).getAll())) as BankRecord[];
    return all.filter((r) => matches(r, q)).sort((a, b) => (a.modifiedAt < b.modifiedAt ? 1 : -1));
  }

  close(): void {
    if (this.dbPromise) {
      this.dbPromise.then((db) => db.close()).catch(() => undefined);
      this.dbPromise = null;
    }
  }
}

function txDone(tx: IDBTransaction): Promise<void> {
  return new Promise((resolve, reject) => {
    tx.oncomplete = () => resolve();
    tx.onerror = () => reject(tx.error);
    tx.onabort = () => reject(tx.error ?? new Error("transaction aborted"));
  });
}

function matches(r: BankRecord, q: BankQuery): boolean {
  if (q.archived !== undefined && r.archived !== q.archived) return false;
  if (q.generatorId && r.generatorId !== q.generatorId) return false;
  if (q.objectiveId && r.objectiveId !== q.objectiveId) return false;
  if (q.task && r.task !== q.task) return false;
  if (q.band !== undefined && r.band !== q.band) return false;
  if (q.lifecycleState && r.lifecycleState !== q.lifecycleState) return false;
  if (q.tag && !r.tags.includes(q.tag)) return false;
  if (q.text) {
    const hay = searchText(r).toLowerCase();
    if (!hay.includes(q.text.toLowerCase())) return false;
  }
  return true;
}

function searchText(r: BankRecord): string {
  const prompt = r.item["prompt"] as { blocks?: Array<{ text?: string }> } | undefined;
  const promptText = (prompt?.blocks ?? []).map((b) => b.text ?? "").join(" ");
  const wordingText = (r.wording.blocks ?? []).join(" ") + " " + (r.wording.title ?? "");
  return [r.itemId, r.task, promptText, wordingText, r.tags.join(" ")].join(" ");
}
