# Security and Privacy Architecture

**Platform:** SPI-Math Question Bank Platform (international mathematics assessment production)
**Document scope:** Security, privacy, confidentiality, and integrity for an offline-first browser application.
**Status:** Living architecture document. Items the team has not yet decided are marked **Unknown / to be decided**.

---

## 1. Security Principles and Threat Model

### 1.1 Operating model

The platform runs **primarily offline** as standalone HTML applications in a browser. The authoritative question bank lives **client-side in IndexedDB**. A cloud database may be added later behind a storage abstraction (see Section 3). Design accordingly: assume no trusted server is present in the MVP, and never depend on a server to enforce security in the offline build.

### 1.2 Core principles

1. **Offline-first, secret-free client.** No API keys, credentials, or secrets ship in any HTML/export/client bundle (Section 2).
2. **Treat all rendered content as untrusted.** Author-edited content, imported items, and third-party material are sanitized before rendering (Section 4).
3. **Local data is the user's data.** It stays local by default; export and backup are explicit user actions (Section 3, Section 6).
4. **Least dependency.** Prefer few, pinned, vendored dependencies over runtime CDN convenience (Section 5).
5. **Provenance and integrity by default.** Every item is traceable and tamper-evident (Section 8).
6. **Respect rights status.** Confidential and reference-only materials are protected at authoring and export time (Section 7).

### 1.3 Assets

| Asset | Sensitivity | Primary concern |
|---|---|---|
| Question bank (IndexedDB) | High | Loss, corruption, unauthorized redistribution |
| Curriculum IP / uploaded materials | Confidential | Leakage, verbatim reproduction of reference-only sources |
| Generated items | High | Integrity, provenance, rights-status leakage in exports |
| Generator logic / seeds | Medium | Reproducibility, tampering |
| (Future) student preview/practice data | High (personal) | Local-only, minimization (Section 6) |
| (Future) cloud sync tokens | Critical | Never on client beyond short-lived scoped tokens |

### 1.4 Threats

| Threat | Vector | Mitigation (section) |
|---|---|---|
| Secret leakage in exports | Keys/credentials embedded in HTML/JSON exports | §2 |
| XSS via rendered content | Author HTML, imported items, SVG diagrams, KaTeX abuse | §4 |
| Supply-chain compromise | Malicious/altered dependency or CDN script | §5 |
| Data loss | Browser cache clear, profile loss, corruption | §3 |
| Unauthorized redistribution | Reference-only material copied into exports | §7 |
| Tampering | Edited items presented as reviewed/approved | §8 |
| Privacy exposure | Student data, analytics phoning home, data in URLs | §6 |

### 1.5 Out of scope (MVP)

Multi-user authentication, server-side authorization, and network transport security are out of scope until a cloud deployment exists (Section 9). The MVP threat model assumes a single trusted local user on a trusted machine.

---

## 2. Secrets Handling

**Hard rule: NEVER place API keys, database credentials, signing keys, or any secret inside a downloadable HTML file, an exported file, or a client bundle.** Anything shipped to a browser is readable by the user and anyone they share the file with.

### 2.1 Where secrets live

- **MVP (offline):** There are no secrets in the client. The app needs none to function.
- **Future cloud sync:** Secrets live **server-side only**. The client receives **short-lived, scoped tokens** (e.g., per-session, per-collection, time-boxed) issued by the server. Token scope, lifetime, and rotation are **Unknown / to be decided**.
- Never store long-lived credentials in IndexedDB, localStorage, cookies, or source.

### 2.2 Secrets checklist for exports

Run this before any export feature ships and before any individual export is published:

- [ ] No API keys, tokens, or credentials in the exported HTML/JSON/PDF source.
- [ ] No internal endpoint URLs, hostnames, or infrastructure identifiers.
- [ ] No `.env` values, config defaults, or build-time secrets inlined.
- [ ] No source-map references that leak internal paths or secrets.
- [ ] No embedded auth headers in fetch calls baked into exported files.
- [ ] No comments containing credentials, TODO-secrets, or internal links.
- [ ] Export reviewed against the rights-status filter (Section 7).

### 2.3 CI scan recommendation

Add a secret-scanning step to the build/CI pipeline that runs on every commit and blocks merge on findings:

- Use a scanner such as **gitleaks** or **trufflehog** over the repo and over the produced export artifacts.
- Add a custom rule set for project-specific patterns (internal hostnames, token prefixes).
- Fail the build on any high-confidence finding; require explicit allowlist entries (with justification) for false positives.
- Specific tool selection and CI provider are **Unknown / to be decided**.

---

## 3. Offline Data Storage

### 3.1 Primary store

**IndexedDB is the offline question bank.** Do **not** use `localStorage` as the primary database — it is synchronous, small (~5 MB), string-only, and unsuitable for structured records and blobs. `localStorage`/`sessionStorage` may hold only small non-sensitive UI state (e.g., last-opened view).

### 3.2 Backup and export

- Local data is the **user's data**; the user can export and back up at any time.
- Provide a **full export** (entire bank to a single JSON/archive file) and **selective export** (collection/item).
- Provide a **re-import** path that validates schema and integrity hashes before merging.
- Recommend periodic user-initiated backups; browser storage can be cleared by the user or OS.

### 3.3 Integrity (content hashes)

- Each item stores a **content hash** (e.g., SHA-256 over a canonicalized serialization) covering its substantive fields.
- On import/restore, recompute and compare hashes; flag mismatches as **tampered or corrupted**.
- A **bank manifest** records item ids and hashes so missing/altered items are detectable after restore.

### 3.4 Storage abstraction boundary

All persistence goes through a single **storage interface** so a future cloud DB can be added without rewriting generator or UI logic.

```
StorageProvider (interface)
  getItem(id)            putItem(item)        deleteItem(id)
  query(filter)          listCollections()    exportAll()
  importAll(bundle)      getManifest()        verifyIntegrity()
```

- **MVP implementation:** `IndexedDbStorageProvider`.
- **Future:** `CloudStorageProvider` implementing the same interface, plus a sync/conflict layer.
- Generator, review, and export modules depend on the **interface**, never on IndexedDB directly.
- Conflict resolution and sync semantics for the cloud provider are **Unknown / to be decided**.

---

## 4. Content Security

Author-edited content, imported items, and diagrams are **untrusted input**. Render them safely.

### 4.1 Rules

- **Sanitize any author-edited HTML** before rendering, using a vetted sanitizer (e.g., DOMPurify) with a strict allowlist of tags/attributes. Strip `script`, event handlers (`on*`), `javascript:` URLs, `style` where avoidable, and unknown attributes.
- **Avoid injecting raw HTML.** Prefer building DOM nodes or text content; reserve `innerHTML` for sanitized output only.
- **Restrict KaTeX to math mode.** Render math via KaTeX with `trust: false` (no `\href`, no raw HTML macros), `throwOnError: false`, and a confined output container. Do not feed author text to KaTeX as HTML.
- **Sanitize SVG diagrams** before insertion: strip `<script>`, foreign objects, event handlers, and external references (`xlink:href`/`href` to remote or `javascript:` targets). Render inline SVG only after sanitization.
- **No `eval`** or `Function(...)` on content; avoid dynamic code execution entirely.

### 4.2 Content Security Policy for standalone apps

Ship a strict CSP (meta tag for file-served apps; HTTP header when served). Baseline:

| Directive | Value | Rationale |
|---|---|---|
| `default-src` | `'self'` | Deny by default |
| `script-src` | `'self'` | **No remote script**, no inline script |
| `style-src` | `'self' 'unsafe-inline'` | Inline styles often needed; tighten if feasible |
| `img-src` | `'self' data:` | Local images and inline data URIs |
| `connect-src` | `'none'` (offline build) | No network calls in offline build |
| `object-src` | `'none'` | Block plugins |
| `base-uri` | `'self'` | Prevent base-tag hijacking |
| `frame-ancestors` | `'none'` | Prevent embedding |

- Eliminate inline scripts so `'unsafe-inline'` is never needed for `script-src`.
- Removing `'unsafe-inline'` from `style-src` is a goal; feasibility is **Unknown / to be decided**.

---

## 5. Dependency and Supply-Chain Security

- **Pin exact versions.** No floating ranges (`^`, `~`) for production dependencies.
- **Vendor/bundle all assets.** No runtime CDN dependency — KaTeX, fonts, sanitizer, and all libraries are bundled so the app works fully offline and cannot be altered by a compromised CDN.
- **Commit a lockfile** (`package-lock.json` / equivalent) and build only from it.
- **Audit dependencies** regularly (`npm audit` or equivalent) and on each release; track and remediate advisories.
- **Prefer minimal dependencies.** Evaluate each addition for maintenance, size, and transitive footprint; prefer well-maintained, single-purpose libraries.
- **Verify integrity** of vendored assets (record hashes; use Subresource Integrity if any asset is ever served remotely — which the offline build avoids).
- Automated dependency-update policy and tooling are **Unknown / to be decided**.

---

## 6. Privacy

The platform is an **authoring/assessment tool**. Student-facing features (Student Preview app, practice results) are **later-phase**.

- **Local by default.** If student data is ever stored, it stays in local storage (IndexedDB) on the user's device and is not transmitted anywhere by default.
- **Data minimization.** Collect only what a feature needs. Avoid storing names or identifiers where a pseudonymous local id suffices.
- **No analytics phoning home in offline builds.** Offline builds make no telemetry, analytics, or tracking calls. `connect-src 'none'` enforces this at the CSP layer.
- **No personal/sensitive data in URLs or query strings.** Never place identifiers, answers, or student data in URLs, fragments, or query parameters.
- **No third-party tracking** scripts or pixels in any build.
- Retention, consent, and any future cloud handling of student data are **Unknown / to be decided** and must be designed before student-facing features ship.

---

## 7. Confidentiality of Source Materials

- **All uploaded curriculum and internal documents are CONFIDENTIAL.** Treat them as project-confidential IP; do not embed them wholesale in exports or transmit them off-device.
- **Reference-only third-party materials must not be reproduced verbatim.** Concrete example: **Oxford University Press teacher notes** are reference-only — they may inform generated items but must not appear verbatim in any generated item or export.
- **Rights status is a first-class field.** Each source and each item carries a rights status (e.g., `confidential`, `reference-only`, `original`, `cleared-for-export`).
- **Respect rights status at export time.** The exporter filters/blocks items whose rights status forbids inclusion, and flags items derived from reference-only sources for human confirmation that no verbatim text remains.
- Provide an authoring-time warning when content closely matches a reference-only source. The matching method is **Unknown / to be decided**.

---

## 8. Integrity and Provenance

Every item is **traceable** and **tamper-evident**.

### 8.1 Provenance fields (per item)

| Field | Purpose |
|---|---|
| `generatorId` / `generatorVersion` | Which generator and version produced it |
| `seed` | Reproduce the exact item |
| `sourceEvidence` | Source material(s) and rights status used |
| `reviewState` | `draft` / `in-review` / `approved` / `published` |
| `contentHash` | Tamper-evidence over substantive fields |
| `createdAt` / `updatedAt` | Timestamps |

### 8.2 Tamper evidence

- Recompute `contentHash` on load; any mismatch between stored hash and computed hash marks the item **modified** and is surfaced in the UI.
- Approved/published items whose content changes are automatically returned to `draft` (or flagged), preventing silent edits to reviewed content.

### 8.3 Audit trail

- Maintain an append-only **audit log** of review/publication state changes: `{ itemId, fromState, toState, actor, timestamp, reason? }`.
- The log is part of backup/export so provenance survives restore.
- In the offline MVP, `actor` is a local label; authenticated actors arrive with multi-user (Section 9).

---

## 9. Authentication and Authorization

- **Offline MVP has no authentication.** A single local user is assumed; there is no login and no server-enforced authorization.
- **Future multi-user/cloud deployment needs role-based access control.** Proposed roles:

| Role | Capabilities (proposed) |
|---|---|
| Author | Create/edit draft items |
| Reviewer | Move items between review states, comment |
| Publisher | Approve and publish, manage exports |

- Identity provider, session model, token scopes, and per-collection permissions are **Unknown / to be decided**.
- Until then, do not present the MVP as access-controlled; local data security depends on the user's device security.

---

## 10. Security Review Checklists

### 10.1 Per-release checklist

- [ ] Secret scan (Section 2) passed on repo and export artifacts.
- [ ] No new runtime CDN/network dependency introduced; assets vendored.
- [ ] Dependencies pinned; lockfile committed; `audit` clean or advisories triaged.
- [ ] CSP present and unchanged-or-tightened; no new `'unsafe-*'` in `script-src`.
- [ ] Content sanitization path covers all new render surfaces (HTML, SVG, KaTeX).
- [ ] No personal/sensitive data in URLs; no telemetry in offline build.
- [ ] Integrity hashing and audit log intact across export/import.
- [ ] Rights-status filtering verified for all export paths.

### 10.2 Per new exporter/app checklist

- [ ] Export contains no secrets, endpoints, or internal identifiers (Section 2.2).
- [ ] Reference-only material is not reproduced verbatim; rights status enforced (Section 7).
- [ ] Author/imported content is sanitized before rendering in the new surface.
- [ ] CSP applied to the new standalone app; no remote script, no `eval`.
- [ ] Persistence (if any) goes through the storage abstraction, not IndexedDB directly.
- [ ] Provenance and content hashes are preserved in the exported representation.
- [ ] No analytics, tracking, or network calls in the offline build.
- [ ] Manual XSS spot-check with hostile sample content (script tags, `on*`, `javascript:` URLs, malicious SVG).
