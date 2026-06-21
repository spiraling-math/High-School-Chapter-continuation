# Technical Debt Register

Recorded items to address in a future phase. Nothing here changes approved
output now.

## TD-1 — Legacy `answerType` config key (Generator SDK migration)

**Status: RESOLVED (2026-06-21).** `interactionType` is now the canonical config and
bank field; `answerType` is a legacy compatibility input only.
`resolveInteractionType` normalizes the legacy key, **accepts agreeing** dual fields
and **rejects conflicting** ones. `BankRecord` carries canonical `interactionType`
(schemaRev 3); the IndexedDB **v3** migration backfills it via a single idempotent
data pass; JSON import normalizes legacy/imported records identically; `genConfig`
is retained as the preserved original config for exact reproduction. Tests cover
legacy-only / canonical-only / matching-dual / conflicting-dual / imported-record /
repeated-migration cases. Verified **output-neutral**:
`generate(seed, {interactionType})` is byte-for-byte identical to the legacy form
for every seed, and all golden/parity fixtures are unchanged. Approved v1.1.0 output
is unchanged. Residual (intentional): the descriptor/schema still list `answerType`
as an accepted input for backward compatibility; read-support is retained. See
`docs/SDK_FOUNDATION_CHECKPOINT.md`.

_Original analysis and phased plan retained below for the record._

### Problem

The generator **configuration** key `answerType` carries values such as
`"integer"` and `"multiple-choice"`. These conflate two distinct concepts:

- `"multiple-choice"` is an **interaction mode**, not a mathematical answer type;
- `"integer"` is used to mean "free-response" (interaction), even though for the
  geometric generator the actual mathematical answer may be an exact rational.

The **item** model was already corrected in geometric v1.1.0 (separate
`interactionType` and `answer.type`), but the **config/SDK** surface still uses
the legacy `answerType` selector, and bank records persist it as `genConfig`.

### Target model (future SDK)

```
config.interactionType : "free-response" | "multiple-choice"
item.answer.type       : "integer" | "exact-rational" (already implemented)
```

### Migration plan (phased; back-compatible)

1. **Add, don't replace.** ✅ **Done.** `config.interactionType` is accepted and
   `config.answerType` is mapped via `resolveInteractionType`
   (`answerType "multiple-choice" -> interactionType "multiple-choice"`;
   `answerType "integer" -> interactionType "free-response"`), in both generators,
   output-neutral.
2. **Persisted records.** Keep reading the stored `genConfig.answerType` on bank
   records and golden/parity fixtures unchanged. When reading, normalize to
   `interactionType` in memory; when writing new records, write both keys during
   a transition window.
3. **Reproducibility is preserved.** The seed + generator version + (mapped)
   config must still reproduce identical canonical items. Because the mapping is
   1:1 and deterministic, all existing seeds, fixtures, and bank items reproduce
   byte-for-byte. **No regeneration of approved fixtures is required.**
4. **Deprecation.** Once the SDK and all generators consume `interactionType`,
   mark `answerType` deprecated in the descriptor/schema, retaining read support
   for stored data indefinitely (or until a versioned bank migration removes it).
5. **No version bump for existing generators is triggered by this change alone,**
   provided output bytes are unchanged; only the SDK/config surface evolves. If a
   generator's emitted item bytes change, that requires a new generator version
   per the versioning rule.

### Constraints

- Maintain backward compatibility for stored seeds, fixtures, and existing bank
  items at all times.
- Do not alter approved v1.1.0 output as part of this cleanup.

### When

To be handled in the **Foundation Readiness & Generator SDK design** phase, not
in a sequence-generator phase.

## TD-2 — Middle-School algebra objective-ID normalization & planned prerequisites

**Status: recorded (2026-06-21).** The linear-equations objectives use the
future-proof six-segment scheme `SPI.MIDDLE.ALG.LINEQ.<MICRO>.01` (owner decision
D-0). The pre-existing reference `SPI.MIDDLE.ALG.SUBSTITUTION.01` is shallower
(five-segment). **Do not silently rename a published objective.** When the
Middle-School algebra foundations are authored, normalize the substitution id
under the same scheme (with an alias/redirect if it has been published) and define
the currently-**planned** prerequisites referenced by the LINEQ objectives:
`SPI.MIDDLE.NUM.SIGNED_OPERATIONS.01`, `SPI.MIDDLE.ALG.INVERSE_OPERATIONS.01`, and
`SPI.MIDDLE.ALG.EXPAND_BRACKETS.01`. Until then these remain explicitly marked
`planned`; the curriculum-graph check warns on the unresolved prerequisites, which
is expected and acceptable.
