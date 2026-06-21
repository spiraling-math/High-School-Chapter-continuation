/**
 * IndexedDB BankStore tests (Node built-in test runner + fake-indexeddb).
 *
 * Covers CRUD, query/filter, archive, duplicate, persistence across reconnect,
 * and versioned schema MIGRATIONS (including a data backfill).
 *
 * Run:  node --test core/bank/indexeddb-store.test.ts
 */

import { test } from "node:test";
import assert from "node:assert/strict";
import { IDBFactory } from "fake-indexeddb";
import { generate } from "../../domains/sequences/arithmetic.ts";
import { validate } from "../../domains/sequences/validate.ts";
import { makeRecord, duplicateRecord } from "./record.ts";
import { IndexedDBBankStore, DB_VERSION } from "./indexeddb-store.ts";
import type { BankRecord } from "./types.ts";

let dbCounter = 0;
function freshStore(version?: number) {
  const factory = new IDBFactory();
  const name = `bank-test-${dbCounter++}`;
  const store = new IndexedDBBankStore(version ? { factory, name, version } : { factory, name });
  return { factory, name, store };
}

function record(seed: number, mode: "integer" | "multiple-choice", tags: string[] = []): BankRecord {
  const item = generate(seed, { answerType: mode });
  return makeRecord(item, validate(item).status, { mode, tags });
}

test("put / get / count / delete", async () => {
  const { store } = freshStore();
  const r = record(1, "multiple-choice", ["quiz"]);
  await store.put(r);
  assert.equal(await store.count(), 1);
  const got = await store.get(r.itemId);
  assert.equal(got?.itemId, r.itemId);
  assert.equal(got?.lifecycleState, "machine-validated");
  await store.delete(r.itemId);
  assert.equal(await store.count(), 0);
  store.close();
});

test("query filters: task, band, lifecycle, tag, archived, and text search", async () => {
  const { store } = freshStore();
  const a = record(1, "multiple-choice", ["alpha"]);   // some task/band
  const b = record(2, "integer", ["beta"]);
  const c = record(3, "multiple-choice", ["alpha", "gamma"]);
  c.archived = true;
  await store.put(a); await store.put(b); await store.put(c);

  assert.equal((await store.query()).length, 3);
  assert.equal((await store.query({ archived: false })).length, 2);
  assert.equal((await store.query({ archived: true })).length, 1);
  assert.equal((await store.query({ tag: "alpha" })).length, 2);
  assert.equal((await store.query({ task: a.task, archived: false })).every((r) => r.task === a.task), true);
  assert.equal((await store.query({ lifecycleState: "machine-validated" })).length, 3);
  const textHits = await store.query({ text: "arithmetic sequence" });
  assert.ok(textHits.length >= 1, "prompt text is searchable");
  store.close();
});

test("archive and duplicate operations", async () => {
  const { store } = freshStore();
  const r = record(10, "multiple-choice");
  await store.put(r);
  // Archive
  await store.put({ ...r, archived: true });
  assert.equal((await store.get(r.itemId))?.archived, true);
  // Duplicate as an editable draft copy
  const copy = duplicateRecord(r, r.itemId + "-copy");
  await store.put(copy);
  assert.equal(await store.count(), 2);
  assert.equal((await store.get(copy.itemId))?.lifecycleState, "draft");
  store.close();
});

test("records survive a reconnect (simulated browser reload)", async () => {
  const factory = new IDBFactory();
  const name = `bank-reload-${dbCounter++}`;
  const s1 = new IndexedDBBankStore({ factory, name });
  await s1.put(record(1, "integer"));
  await s1.put(record(2, "multiple-choice"));
  s1.close();
  // New connection, same backing store.
  const s2 = new IndexedDBBankStore({ factory, name });
  assert.equal(await s2.count(), 2);
  s2.close();
});

async function indexNames(factory: IDBFactory, name: string): Promise<string[]> {
  return new Promise((resolve, reject) => {
    const req = factory.open(name);
    req.onsuccess = () => {
      const db = req.result;
      const tx = db.transaction("items", "readonly");
      const names = Array.from(tx.objectStore("items").indexNames);
      db.close();
      resolve(names);
    };
    req.onerror = () => reject(req.error);
  });
}

test("schema migration v1 -> current backfills tags/archived and the canonical interactionType", async () => {
  const factory = new IDBFactory();
  const name = `bank-migrate-${dbCounter++}`;
  assert.equal(DB_VERSION, 3);

  // Open at v1 and write a pre-tags, pre-interactionType record.
  const v1 = new IndexedDBBankStore({ factory, name, version: 1 });
  const old = record(5, "multiple-choice");
  const oldShape = { ...old } as Partial<BankRecord> as BankRecord;
  delete (oldShape as { tags?: unknown }).tags;
  delete (oldShape as { archived?: unknown }).archived;
  delete (oldShape as { schemaRev?: unknown }).schemaRev;
  delete (oldShape as { interactionType?: unknown }).interactionType;
  await v1.put(oldShape);
  v1.close();
  assert.ok(!(await indexNames(factory, name)).includes("tags"), "no tags index at v1");

  // Reopen at current version -> runs the v2 + v3 migrations.
  const cur = new IndexedDBBankStore({ factory, name });
  await cur.count();
  const migrated = await cur.get(old.itemId);
  assert.deepEqual(migrated?.tags, [], "tags backfilled to []");
  assert.equal(migrated?.archived, false, "archived backfilled to false");
  assert.equal(migrated?.interactionType, "multiple-choice", "interactionType backfilled from mode");
  assert.equal(migrated?.schemaRev, 3, "schemaRev set to 3");
  assert.ok((await indexNames(factory, name)).includes("tags"), "tags index present");
  cur.close();

  // Repeated migration is idempotent: reopening again changes nothing.
  const again = new IndexedDBBankStore({ factory, name });
  const m2 = await again.get(old.itemId);
  assert.equal(m2?.interactionType, "multiple-choice");
  assert.equal(m2?.schemaRev, 3);
  again.close();
});

test("v2 -> v3 migration backfills interactionType for a free-response record", async () => {
  const factory = new IDBFactory();
  const name = `bank-v2v3-${dbCounter++}`;
  // Seed a record at v2 (no interactionType).
  const v2 = new IndexedDBBankStore({ factory, name, version: 2 });
  const r = record(2, "integer");
  const v2shape = { ...r } as Partial<BankRecord> as BankRecord;
  delete (v2shape as { interactionType?: unknown }).interactionType;
  await v2.put(v2shape);
  v2.close();
  // Reopen at v3.
  const v3 = new IndexedDBBankStore({ factory, name });
  const migrated = await v3.get(r.itemId);
  assert.equal(migrated?.interactionType, "free-response");
  assert.equal(migrated?.schemaRev, 3);
  v3.close();
});

test("a canonical-only record (already interactionType) round-trips unchanged", async () => {
  const { store } = freshStore();
  const r = record(9, "multiple-choice"); // makeRecord already sets interactionType + schemaRev 3
  assert.equal(r.interactionType, "multiple-choice");
  await store.put(r);
  const got = await store.get(r.itemId);
  assert.equal(got?.interactionType, "multiple-choice");
  assert.equal(got?.schemaRev, 3);
  store.close();
});
