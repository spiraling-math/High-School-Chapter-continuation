# Accessibility Standard — SPI-Math Question Bank Platform

**Status:** Active baseline standard
**Conformance target:** WCAG 2.2 Level AA
**Applies to:** Generator Studio, Question Bank Manager, Assessment Builder, Quality Console, Student Preview, and all exported artifacts (offline HTML apps, worksheets, assessments).

---

## 1. Purpose and Scope

This document defines the accessibility requirements every SPI-Math platform component and generated artifact must meet. It is a normative standard: developers, reviewers, and the validation pipeline enforce it. Marketing language is out of scope.

**Conformance target.** WCAG 2.2 Level AA is the baseline. Individual success criteria are cited inline (e.g., 1.4.3, 2.1.1, 2.5.8) so they can be traced during review. Where the platform exceeds AA (e.g., recommending 44×44 px targets) the stronger requirement is marked as a recommendation, not a gate.

**Accessibility is architectural, not bolt-on.** Accessibility constraints live in the data model and the generation pipeline, not in a post-hoc remediation pass:

- The question-item schema carries `accessibility.altText`, `accessibility.longDescription`, and a spoken-math/plain-text alternative field. Items missing required fields **fail validation** (see §12).
- Generated SVG diagrams emit accessible descriptions from the same parameters that drive the visual.
- KaTeX is configured to emit MathML for assistive technology on every render.
- Theming (light/dark) is built on token pairs that are pre-verified for contrast.

**Scope of artifacts.** Output is standalone offline HTML. There is no server round-trip at runtime, so all accessibility affordances (live regions, MathML, alt text, keyboard handlers) must be self-contained in the exported file with no external dependencies beyond the bundled KaTeX assets.

**Out of scope.** This standard is English-only. RTL layouts, localization, and translation of spoken-math output are explicitly excluded.

---

## 2. Keyboard Operability

All functionality must be operable through a keyboard interface (**2.1.1 Keyboard**, **2.1.3 Keyboard No Exception** as a goal where feasible).

### Requirements

| Requirement | Criterion | Acceptance |
|---|---|---|
| Every interactive control reachable and operable by keyboard | 2.1.1 | Tab/Shift+Tab reach all controls; Enter/Space activate; arrow keys operate composite widgets |
| No keyboard trap | 2.1.2 | Focus can always move away from any component using standard keys; modal dialogs trap intentionally but release on Escape |
| Logical focus order | 2.4.3 | DOM order matches visual reading order; no positive `tabindex` |
| Visible focus indicator | 2.4.7, 2.4.11 Focus Not Obscured (Minimum) | Focus ring ≥ 2 px, ≥ 3:1 contrast against adjacent colors (1.4.11); never fully hidden behind sticky headers/toolbars |
| Skip link | 2.4.1 Bypass Blocks | First focusable element is "Skip to main content"; visible on focus |
| Character-key shortcuts are safe | 2.1.4 | Single-character shortcuts can be remapped or are only active on focus |

### Focus indicator (code-level)

Do not remove outlines without replacement. Use a token-driven ring:

```css
:where(a, button, [role="button"], input, select, textarea, [tabindex]):focus-visible {
  outline: 3px solid var(--focus-ring);   /* >= 3:1 vs background and component */
  outline-offset: 2px;
}
```

### Keyboard shortcuts and discoverability

- Each app exposes a shortcut help dialog bound to `?` (and reachable from a menu).
- Shortcuts are listed with their action and key; conflicts across apps are documented in one shared registry.
- Shortcuts must not collide with assistive-technology or browser reserved keys.

### Drag-and-drop alternatives (mandatory)

Per **2.5.7 Dragging Movements**, every drag interaction must have an equivalent that is not a drag. This is load-bearing for ordering, matching, classification, and construction question types.

- **Ordering / ranking:** each item exposes "Move up" / "Move down" buttons and supports arrow-key reordering when focused; position is announced.
- **Matching:** keyboard flow is "select source (Enter) → move to target (Tab/arrows) → confirm (Enter)"; a click-to-pair fallback is also available.
- **Classification / sort-into-bins:** focus an item, press Enter, choose a bin from a menu/radio list.
- **Geometry construction:** points/handles are placeable and nudgeable by keyboard (arrow keys = fine nudge, Shift+arrow = coarse); a numeric coordinate entry fallback is provided.

Acceptance: any task completable by mouse drag is completable using keyboard only, with equivalent outcome and feedback.

---

## 3. Accessible Mathematics

Mathematical notation is rendered with KaTeX. Notation is the highest-risk content for assistive technology, so the platform enforces three layers.

### Requirements

1. **MathML output is mandatory.** KaTeX runs with `output: "htmlAndMathml"` so every formula carries a MathML tree for screen readers alongside the visual HTML. The visual layer is hidden from AT (`aria-hidden`), and the MathML is exposed.
2. **No notation as image-only.** Formulas are never baked into images without a text/MathML equivalent. If a formula must appear inside an SVG diagram (e.g., a labeled axis), the label text is also present in the diagram's accessible description (§4).
3. **Required spoken-math alternative per item.** Every item that contains notation **must** populate `accessibility.spokenMath` (plain-text/spoken form, e.g., "x squared plus three x minus four"). This is a validation gate, not optional. It serves as the authoritative reading and as a fallback where MathML support is weak.

### Code-level guidance

```js
katex.render(latex, el, {
  output: "htmlAndMathml",
  throwOnError: false,
  strict: "warn",
});
```

- Wrap rendered math in a container with an accessible name drawn from `accessibility.spokenMath` when present:
  `<span role="math" aria-label="{spokenMath}">…KaTeX HTML…<math>…</math></span>` — choose one exposure path (aria-label OR MathML) per item to avoid double-reading; default to MathML, fall back to `aria-label` only when MathML is suppressed.
- Inline vs. display math must both render MathML; do not disable MathML for performance.

**Unknown / to be decided:** whether to ship an optional MathJax-based reader profile for environments with poor native MathML support. Default remains KaTeX + MathML + `spokenMath`.

---

## 4. Diagrams, Graphs, and Visuals

Diagrams are SVG generated from the same parameters as the question. Every **meaningful** diagram, graph, or figure must be described in text.

### Requirements

| Requirement | Criterion | Acceptance |
|---|---|---|
| Short alternative text on every meaningful figure | 1.1.1 Non-text Content | `accessibility.altText` is populated; rendered as `<title>` / `aria-labelledby` on the `<svg>` |
| Long description where the figure encodes structure or data | 1.1.1 | `accessibility.longDescription` populated for graphs, geometric figures, multi-element diagrams; exposed via `aria-describedby` |
| Decorative-only graphics hidden from AT | 1.1.1 | `aria-hidden="true"` + empty `alt`; never given a misleading description |
| Status/validation not by color alone | 1.4.1 Use of Color | Every state pairs color with an icon and a text label |
| Data-bearing graphs also available as a table | 1.1.1, 1.3.1 | Where a graph encodes data points, an accessible HTML table of the same data is provided (§9) |

### SVG pattern

```html
<svg role="img" aria-labelledby="d1-title d1-desc" viewBox="0 0 400 300">
  <title id="d1-title">{accessibility.altText}</title>
  <desc id="d1-desc">{accessibility.longDescription}</desc>
  …generated shapes…
</svg>
```

- `altText` is a concise name ("Bar chart of test scores by class").
- `longDescription` conveys the information needed to answer without seeing the figure (axes, ranges, plotted values, geometric relationships). It is generated from the same parameters as the visual so it cannot drift.

### Non-color status indicators (1.4.1, 1.4.11)

Validation/quality states in Generator Studio and Quality Console must not rely on hue alone:

| State | Color | Icon | Text |
|---|---|---|---|
| Valid | green | ✓ check | "Valid" |
| Warning | amber | ▲ triangle | "Warning" |
| Error | red | ✕ cross | "Error" |

Icon strokes/fills must meet 3:1 non-text contrast (1.4.11).

---

## 5. Color and Contrast

### Requirements

| Content | Minimum ratio | Criterion |
|---|---|---|
| Body text, math, labels | 4.5:1 | 1.4.3 Contrast (Minimum) |
| Large text (≥ 24 px, or ≥ 18.66 px bold) | 3:1 | 1.4.3 |
| UI components, icons, focus rings, graph lines/markers | 3:1 | 1.4.11 Non-text Contrast |

### Rules

- **Both themes must pass.** Light and dark themes are each verified against 1.4.3 and 1.4.11. Theme tokens ship as pre-validated pairs; a token that fails contrast in either theme is rejected in review.
- **Never encode answer-relevant information by color alone** (1.4.1). A correct option, a highlighted region, a matched pair, or a graphed series must also be distinguishable by text, shape, pattern, marker, or label. This applies to Student Preview and exported assessments.
- Graph series use distinct markers/line styles in addition to color so they remain distinguishable in grayscale and for color-vision deficiencies.
- Do not rely on link color alone; underline or otherwise mark links in running text.

**Unknown / to be decided:** whether a dedicated high-contrast theme beyond light/dark is shipped. Baseline requires both default themes to pass AA.

---

## 6. Motion and Preference

### Requirements

- **Honor `prefers-reduced-motion`** (2.3.3 Animation from Interactions). Non-essential animation (transitions, reveal effects, drag ghosts, celebratory feedback) is reduced or removed when the user requests it.
- **No essential information conveyed only through animation** (1.4.13 where applicable). State changes are also expressed in static text/markup.
- **No flashing** above three flashes per second (2.3.1).
- Animations triggered by interaction can be disabled globally via a setting and via the OS preference.

```css
@media (prefers-reduced-motion: reduce) {
  *, *::before, *::after {
    animation-duration: 0.001ms !important;
    animation-iteration-count: 1 !important;
    transition-duration: 0.001ms !important;
    scroll-behavior: auto !important;
  }
}
```

---

## 7. Zoom and Reflow

### Requirements

| Requirement | Criterion | Acceptance |
|---|---|---|
| Usable at 400% zoom | 1.4.10 Reflow | Content reflows to a single column at 320 CSS px width equivalent; no loss of content or function; no two-dimensional scrolling except where intrinsic (data tables, complex diagrams) |
| Text resize to 200% | 1.4.4 Resize Text | No clipping or overlap; no fixed-height text containers that truncate |
| Text spacing override tolerated | 1.4.12 Text Spacing | Layout survives increased line/letter/word spacing |
| Minimum target size | 2.5.8 Target Size (Minimum) | Interactive targets ≥ 24×24 CSS px, or have adequate spacing; **recommended 44×44** for primary controls and touch |

### Guidance

- Use relative units (`rem`, `%`, `ch`, `fr`) for layout; avoid fixed pixel widths on containers that hold text or math.
- Diagrams and data tables may scroll within a labeled, focusable region rather than forcing page-level horizontal scroll.
- Toolbar icon buttons in the five apps must meet ≥ 24×24 px with ≥ 24 px spacing; primary actions target 44×44.

---

## 8. Forms and Validation Messages

Generator Studio, Assessment Builder, and Question Bank Manager are form-heavy. They must meet:

| Requirement | Criterion | Acceptance |
|---|---|---|
| Programmatic labels | 1.3.1, 3.3.2 Labels or Instructions, 4.1.2 | Every field has a `<label for>` or `aria-labelledby`; placeholder is never the only label |
| Error identification | 3.3.1 Error Identification | Errors named in text and associated to the field via `aria-describedby`; `aria-invalid="true"` set |
| Error suggestion | 3.3.3 Error Suggestion | Where the fix is known, suggest it |
| Required-field consistency | 3.3.7 Redundant Entry (where applicable) | Do not force re-entry of already-provided information within a flow |
| Status announcements | 4.1.3 Status Messages | Generation, validation, save, and export outcomes are announced via live regions without moving focus |

### Live-region pattern

Generation and validation are asynchronous; results must reach screen-reader users without a focus jump:

```html
<div role="status" aria-live="polite" id="gen-status"></div>   <!-- success/progress -->
<div role="alert"  aria-live="assertive" id="gen-error"></div> <!-- blocking errors -->
```

- Use `role="status"` (polite) for "12 items generated", "Saved", "Validation passed".
- Use `role="alert"` (assertive) for blocking failures ("Generation failed: missing spoken-math on 3 items").
- Do not steal focus on completion; let the user choose to navigate to results.

---

## 9. Tables

Accessible data tables (1.3.1):

- Use real `<table>` with `<caption>`, `<thead>`, `<th scope="col">` / `<th scope="row">`.
- Do not use tables for layout; do not use ASCII or `<div>` grids for tabular data.
- Complex tables use `headers`/`id` association where scope is insufficient.
- For any graph that encodes data, the equivalent table (§4) follows this structure.

```html
<table>
  <caption>Test scores by class</caption>
  <thead><tr><th scope="col">Class</th><th scope="col">Mean score</th></tr></thead>
  <tbody>
    <tr><th scope="row">A</th><td>78</td></tr>
    <tr><th scope="row">B</th><td>85</td></tr>
  </tbody>
</table>
```

---

## 10. Print Readability

Exported worksheets/assessments must remain legible on paper and must not depend on color (1.4.1 carried into print):

- Provide a `@media print` stylesheet: black text on white, remove dark-theme backgrounds, ensure KaTeX renders at legible size.
- Answer keys, correct options, and status are distinguished by text/markers (e.g., "(correct)", checkmark glyph), never by color fill alone.
- Diagrams print with sufficient stroke weight and rely on patterns/labels, not hue.
- Avoid clipping: no fixed heights; allow content to paginate. Ensure `page-break` rules keep a question and its figure together where feasible.
- Alt text and long descriptions need not print, but the printed figure must be self-explanatory through visible labels.

---

## 11. Per-Question-Type Accessibility Requirements

Every question type maps to specific requirements and, where it involves dragging, a mandatory non-drag alternative (§2).

| Question type | Key a11y requirements | Non-drag / keyboard alternative |
|---|---|---|
| Multiple choice (single) | Radio-group semantics (`role="radiogroup"`, arrow-key selection); options not distinguished by color alone; math options carry `spokenMath` | N/A — already keyboard-native |
| Multiple select | Checkbox-group semantics; clear "select all that apply" instruction; state announced | N/A — keyboard-native |
| Matching | Pairs announced; current selection announced; both members text/labelled | Select source (Enter) → choose target from list (Enter); no drag required |
| Ordering / ranking | Position announced on move; instructions on reorder keys | "Move up/down" buttons + arrow-key reorder |
| Classification / sort | Each item and each bin labelled; bin membership announced | Focus item → Enter → pick bin from menu/radio list |
| Table completion | Cells are labelled inputs with row/col context; `scope` headers; per-cell error association | Tab between cells; type values; no drag |
| Graph response | Data also given as accessible table; plotted points keyboard-placeable and nudgeable; current coordinates announced | Arrow-key plotting + numeric coordinate entry |
| Geometry construction | Handles keyboard-focusable; fine/coarse nudge; relationships described in `longDescription` | Keyboard nudge + numeric coordinate fallback |
| Diagram labelling | Each label target named; available labels in a list; placement announced | Select label (Enter) → select target (Enter); no drag |
| Short response | Programmatically labelled text input; math entry produces `spokenMath`; error/format guidance | Keyboard-native |
| Extended response | Labelled multiline input; resize/zoom tolerant; spacing override tolerant | Keyboard-native |

Acceptance: for each type above, the Student Preview app must complete a representative item using keyboard only and expose all answer-relevant information without color.

---

## 12. Testing and Acceptance

Accessibility is verified by automated checks, manual passes, and a release checklist. **Validation gating** is part of the generation pipeline, not just review.

### Validation gate (build/generation time)

Every generated item is validated before it enters the bank. An item **fails validation** if:

- It contains notation but `accessibility.spokenMath` is empty.
- It contains a meaningful diagram/graph but `accessibility.altText` is empty, or a data/structure-bearing figure lacks `accessibility.longDescription`.
- A graph encodes data but no equivalent data table is generated.
- Any interactive (drag-based) question type ships without its keyboard/click alternative.

These checks run in the same pipeline that emits the HTML, so a non-conformant item cannot be exported.

### Automated testing

- **axe-core** runs in CI against each app and against rendered sample items per question type. Zero critical/serious violations is the gate.
- Contrast tokens are checked programmatically for both themes (1.4.3, 1.4.11).
- Lint rule: no positive `tabindex`; no `outline: none` without `:focus-visible` replacement.

Automated tools catch an estimated subset of issues; they do not replace manual testing.

### Manual testing

- **Keyboard pass:** complete every primary task in each of the five apps with keyboard only — no trap (2.1.2), visible focus throughout (2.4.7), logical order (2.4.3), all drag tasks completable via alternative (2.5.7).
- **Screen-reader pass:** test with **NVDA** (Windows) and **VoiceOver** (macOS). Verify math reads via MathML/`spokenMath`, diagrams read via alt/long description, validation/generation outcomes announce via live regions (4.1.3), and tables read with header context.
- **Zoom/reflow pass:** verify 400% zoom and 320 px reflow (1.4.10), 200% text resize (1.4.4).
- **Reduced-motion pass:** verify animations honor the OS preference (2.3.3).

### Per-release accessibility checklist

| # | Check | Criterion | Pass/Fail |
|---|---|---|---|
| 1 | axe-core: zero critical/serious across all apps and sample items | — | |
| 2 | Keyboard-only completion of all primary tasks; no traps | 2.1.1, 2.1.2 | |
| 3 | Visible focus on every control; not obscured | 2.4.7, 2.4.11 | |
| 4 | Skip link present and functional | 2.4.1 | |
| 5 | Every drag interaction has a working non-drag alternative | 2.5.7 | |
| 6 | Math reads correctly in NVDA and VoiceOver | 1.1.1 | |
| 7 | All meaningful diagrams have alt/long description; data graphs have tables | 1.1.1, 1.3.1 | |
| 8 | Contrast passes in light and dark themes | 1.4.3, 1.4.11 | |
| 9 | No answer-relevant info by color alone | 1.4.1 | |
| 10 | Status/validation states pair color with icon + text | 1.4.1 | |
| 11 | 400% zoom / 320 px reflow usable | 1.4.10 | |
| 12 | Targets ≥ 24×24 px (44×44 for primary) | 2.5.8 | |
| 13 | Live regions announce generation/validation outcomes | 4.1.3 | |
| 14 | Forms: labels, error identification, error association | 1.3.1, 3.3.1, 4.1.2 | |
| 15 | prefers-reduced-motion honored | 2.3.3 | |
| 16 | Print stylesheet legible and color-independent | 1.4.1 | |
| 17 | Validation gate: no item missing required accessibility fields was exported | — | |

A release ships only when all 17 checks pass or each exception is documented and approved.

---

**Unknown / to be decided:**
- Optional MathJax reader profile for weak-MathML environments (§3).
- Dedicated high-contrast theme beyond light/dark (§5).
- Final shortcut registry contents and conflict resolution across the five apps (§2).
