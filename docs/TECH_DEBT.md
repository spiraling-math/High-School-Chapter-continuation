# Technical Debt Register

Recorded items to address in a future phase. Nothing here changes approved
output now.

## TD-1 — Legacy `answerType` config key (Generator SDK migration)

**Status:** in progress. Step 1 done (2026-06-21): both TS generators now accept
`config.interactionType` and map the legacy `answerType` via
`core/sdk/interaction.ts` `resolveInteractionType`. Verified **output-neutral** —
`generate(seed, {interactionType})` is byte-for-byte identical to the legacy
`generate(seed, {answerType})` for every seed (test:
`domains/sequences/interaction-config.test.ts`), and all golden/parity fixtures are
unchanged. Remaining steps (2–5 below) pending. Approved v1.1.0 output is unchanged.

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
