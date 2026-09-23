# Output Format

This file defines the audit's two output modes:

- **HTML mode (default)** — a self-contained `.html` file written to the audited project's `motion-audits/` directory and opened in the user's default browser. Each Critical or Important finding gets an auto-looping CSS demo card beside it.
- **Terminal mode (flag-triggered)** — the decorated-markdown report rendered inline in the conversation. Use when the user passes `--terminal`, `--inline`, "show the full report inline," "skip the HTML," or any natural-language equivalent. No HTML file is written.

The two modes contain the same audit content; only the rendering differs. Do not summarize — users want full per-lens perspectives.

---

## HTML mode

### File structure

The HTML output is a single self-contained `.html` document with everything inlined — no external CSS, no external JS, no external fonts (fonts may degrade gracefully if a CDN reference is used). The file scaffolds:

```
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>{project-name} motion audit — {ISO date}</title>
  <style>
    /* 1. Demo shell tokens, .demo-card layout, prefers-reduced-motion */
    /*    — copied from references/demo-shell.html                    */

    /* 2. Report layout tokens: hero, finding-row, perspective-section,
          severity-table, recommendation-summary                       */

    /* 3. Per-finding @keyframes and .demo-card-{n}__motion-target
          rules, generated per audit — one block per Critical or
          Important finding, suffixed by the finding's 1-indexed
          position across the report                                  */
  </style>
</head>
<body>
  <!-- Hero -->
  <!-- Overall Assessment -->
  <!-- Per-lens sections (primary, secondary, selective) -->
  <!-- Combined Recommendations tables -->
  <!-- Lens Reference Summary -->
</body>
</html>
```

### Report's own motion posture

The report itself has **no** entrance, scroll, or mount animations. No staggered reveals, no fade-in-on-scroll, no motion-on-mount outside the demo cards. The demo cards are the only animated elements in the document — anything else would reproduce the AI-slop patterns the skill audits against.

### Hero header

Top of the document. Project name + ISO date + severity counts row + primary lens label.

```html
<header class="report-hero">
  <h1>{project-name} motion audit</h1>
  <p class="report-hero__date">{ISO date}</p>
  <p class="report-hero__counts">
    <a href="#critical-findings">🔴 Critical: {N}</a> ·
    <a href="#important-findings">🟡 Important: {N}</a> ·
    <a href="#opportunity-findings">🟢 Opportunities: {N}</a>
  </p>
  <p class="report-hero__primary">Primary: {Designer Name} — {Perspective Handle}</p>
</header>
```

The severity counts pair each emoji with a text label (`Critical: N`, not just `🔴 N`) so the severity signal is readable under red-green color vision deficiency. Each count is an anchor link to the corresponding section in the body — this is the navigation affordance for long audits with many findings.

### Overall Assessment

One short paragraph in larger type. Does this feel polished? Too much? Too little? What's working, what's not?

```html
<section class="report-assessment">
  <p>{one-paragraph assessment}</p>
</section>
```

### Per-lens sections

Three sections in weighting order: primary, secondary, selective. Each section header pairs the designer name with the perspective handle using an em-dash (`Designer Name — Perspective Handle`):

```html
<section class="perspective-section" id="perspective-emil">
  <h2>Emil Kowalski — Restraint &amp; Speed</h2>

  <div class="perspective-section__working-well">
    <h3>What's Working Well</h3>
    <ul>
      <li>✓ {observation} — <code>{file.tsx:line}</code></li>
    </ul>
  </div>

  <div class="perspective-section__issues" id="emil-issues">
    <h3>Issues to Address</h3>
    <!-- One .finding-row per Critical or Important finding under this lens -->
  </div>

  <div class="perspective-section__opportunities">
    <h3>Opportunities</h3>
    <ul>
      <li>💡 {idea} — <code>{file.tsx:line}</code></li>
    </ul>
  </div>

  <p class="perspective-section__quote"><strong>Through Emil's lens:</strong> {1-2 sentence summary}</p>
</section>
```

The three perspective handles:

| Designer | Perspective handle |
|---|---|
| Emil Kowalski | Restraint & Speed |
| Jakub Krehel | Production Polish |
| Jhey Tompkins | Experimentation & Delight |

Always render section headers as `Designer Name — Perspective` (em-dash). Always close each section with the `Through {Designer}'s lens:` summary — it's a documented lens, not a quote from the person.

### Finding rows (Critical + Important only)

Each Critical or Important finding inside an `Issues to Address` block renders as a `.finding-row` with the issue prose on the left and the demo card on the right (two-column at desktop, stacked at narrow widths):

```html
<div class="finding-row" id="finding-{n}">
  <div class="finding-row__prose">
    <p class="finding-row__severity">🔴 Critical</p>
    <h4>{finding title}</h4>
    <p>{finding explanation}</p>
    <p class="finding-row__location"><code>{file.tsx:line}</code></p>
  </div>
  <article class="demo-card" tabindex="-1">
    <div class="demo-card__loop-indicator">↻ looping</div>
    <div class="demo-card__header">{recommended motion title}</div>
    <div class="demo-card__subhead">{duration} · {easing}</div>
    <div class="demo-card__stage">
      <div class="demo-card-{n}__motion-target">{motion target markup}</div>
    </div>
  </article>
</div>
```

`{n}` is the finding's 1-indexed position **across the whole report** (not per-section). This guarantees `@keyframes motion-{n}-...` and `.demo-card-{n}__motion-target` selector names are unique across the document, so concatenating multiple findings' CSS in one `<style>` block does not produce keyframe-name collisions.

Opportunities never render a demo card. They appear in the per-lens section's `Opportunities` block as a plain bulleted list.

### Demo-shell embedding pattern

The agent reads `references/demo-shell.html` and uses it as a template. For each Critical or Important finding:

1. **Generate the per-finding motion code.** Read the audited code, the relevant lens reference (`emil-kowalski.md`, `jakub-krehel.md`, `jhey-tompkins.md` — matching the lens this finding lives under), and `references/motion-cookbook.md` for the concrete recipe (easing, spring config, enter/exit shape). Write a CSS keyframe block + selector rules that demonstrate the recommended motion. Use the 0% / 66% / 100% cadence with `animation-duration: 3s` (~2s motion, ~1s hold, then loop).

2. **Inject the per-finding code into the report's `<style>` block.** Append a `@keyframes motion-{n}-...` block and a `.demo-card-{n}__motion-target { animation: ...; }` rule. The shell's CSS variables (`--bg`, `--fg`, `--border`, `--accent`, `--loop-dim`, `--sans`, `--mono`) are available — use them via `var()`. Do not redefine them.

3. **Inject the motion-target element into the `.demo-card__stage`.** The element's class must be `.demo-card-{n}__motion-target` so it matches the rules from step 2.

4. **Set the demo card's header and subhead.** Header = short title for the recommended motion (e.g., "Subtle enter: opacity + translateY + blur"). Subhead = duration + easing in monospace (e.g., "300ms · ease-out"). The subhead always renders — populate it for every demo.

5. **Honor the prefers-reduced-motion guard.** The shell's `@media (prefers-reduced-motion: reduce)` block disables all `[class*="__motion-target"]` animations. The per-finding `@keyframes` 100% values MUST match the motion-target element's default static rendering so the reduce-motion fallback shows the correct final visual. Do not write per-finding overrides inside the reduce-motion block.

### Combined Recommendations tables

After the three per-lens sections, render severity-grouped tables for quick scanning:

```html
<section class="recommendations" id="critical-findings">
  <h2>🔴 Critical (Must Fix)</h2>
  <table>
    <thead>
      <tr><th>Issue</th><th>File</th><th>Action</th></tr>
    </thead>
    <tbody>
      <tr>
        <td>{issue}</td>
        <td><code>{file:line}</code></td>
        <td>{fix}</td>
      </tr>
    </tbody>
  </table>
</section>

<section class="recommendations" id="important-findings">
  <h2>🟡 Important (Should Fix)</h2>
  <!-- same shape -->
</section>

<section class="recommendations" id="opportunity-findings">
  <h2>🟢 Opportunities (Could Enhance)</h2>
  <!-- same shape -->
</section>
```

The hero's severity counts link to these section IDs (`#critical-findings`, `#important-findings`, `#opportunity-findings`).

### Lens Reference Summary (closing)

```html
<section class="reference-summary">
  <h2>Lens Reference Summary</h2>
  <p><strong>Which lens was referenced most:</strong> {Designer} — {Perspective}</p>
  <p><strong>Why:</strong> {one-line context reason}</p>
  <p><strong>If you want to lean differently:</strong></p>
  <ul>
    <li>To follow Emil more strictly: {specific actions}</li>
    <li>To follow Jakub more strictly: {specific actions}</li>
    <li>To follow Jhey more strictly: {specific actions}</li>
  </ul>
</section>
```

### Empty-state behavior

When the audit produces zero Critical + zero Important findings:

- The hero still renders with the severity counts row (showing `Critical: 0 · Important: 0 · Opportunities: N`).
- Each per-lens section's `Issues to Address` block still renders its header, but the body shows a dimmed-italic line:
  ```html
  <div class="perspective-section__issues" id="emil-issues">
    <h3>Issues to Address</h3>
    <p class="perspective-section__empty">No issues found at this severity level.</p>
  </div>
  ```
  Style: `font-style: italic; color: var(--loop-dim); padding: 12px 0;`. Communicates absence without looking broken.
- No `.finding-row` markup, no demo cards.
- Opportunities still render in text as usual.

### Responsive behavior

The `.finding-row` two-column layout (prose left, demo right) needs a breakpoint for narrow viewports:

```css
.finding-row {
  display: grid;
  grid-template-columns: 1fr 360px;
  gap: 24px;
  align-items: start;
  margin: 24px 0;
}

@media (max-width: 768px) {
  .finding-row {
    grid-template-columns: 1fr;
  }
  .demo-card {
    max-width: 100%;
  }
}
```

Below 768px the demo card stacks below the finding prose. The shell's `min-width: 280px` keeps the card from compressing past usability.

### Report layout tokens

These extend the shell's tokens for report-level structure. Append to the `<style>` block after the shell's variables:

```css
body {
  max-width: 960px;
  margin: 0 auto;
  padding: 48px 24px;
}
.report-hero h1 {
  font-size: 1.75rem;
  margin: 0 0 4px;
}
.report-hero__date {
  font-family: var(--mono);
  color: var(--loop-dim);
  font-size: 0.875rem;
  margin: 0 0 16px;
}
.report-hero__counts {
  font-size: 1rem;
  margin: 0 0 8px;
}
.report-hero__counts a {
  color: inherit;
  text-decoration: none;
  border-bottom: 1px dashed var(--border);
}
.report-hero__counts a:hover {
  border-bottom-style: solid;
}
.report-hero__primary {
  font-family: var(--mono);
  color: var(--loop-dim);
  font-size: 0.875rem;
  margin: 0;
}
.report-assessment {
  margin: 32px 0;
  font-size: 1.05rem;
  line-height: 1.6;
}
.perspective-section {
  margin: 48px 0;
  padding-top: 24px;
  border-top: 1px solid var(--border);
}
.perspective-section h2 {
  font-size: 1.25rem;
  margin: 0 0 16px;
}
.perspective-section__quote {
  margin-top: 24px;
  padding: 12px 16px;
  background: var(--bg);
  border-left: 3px solid var(--accent);
  font-size: 0.95rem;
}
.recommendations {
  margin: 48px 0;
}
.recommendations table {
  width: 100%;
  border-collapse: collapse;
  font-size: 0.9rem;
}
.recommendations th,
.recommendations td {
  text-align: left;
  padding: 8px 12px;
  border-bottom: 1px solid var(--border);
  vertical-align: top;
}
```

---

## Terminal mode (flag-triggered fallback)

When the user passes `--terminal` / `--inline` / a natural-language equivalent, do not write an HTML file. Render the decorated-markdown report inline in the conversation.

### Quick Summary (Show First)

```
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
📊 AUDIT SUMMARY
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
🔴 [X] Critical  |  🟡 [X] Important  |  🟢 [X] Opportunities
Primary perspective: [Designer(s)] ([context reason])
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```

### Overall Assessment

One paragraph: Does this feel polished? Too much? Too little? What's working, what's not?

---

### Per-Designer Sections

#### Emil's Section

```
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
⚡ EMIL KOWALSKI — Restraint & Speed
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```

*Weight based on context. Heavy for productivity tools, light for creative/kids apps.*

**What to Check:**
- High-frequency interactions that might not need animation
- Keyboard-initiated actions that animate (generally shouldn't)
- Durations **if this is a productivity context** (Emil prefers under 300ms)
- Animations starting from scale(0) (should be 0.9+)
- Transform-origin on dropdowns/popovers
- CSS keyframes that should be transitions (for interruptibility)

**Body format:**

**What's Working Well**
- ✓ [Observation] — `file.tsx:line`

**Issues to Address**
- ✗ [Issue] — `file.tsx:line`
  [Brief explanation]

**Through Emil's lens**: [1-2 sentence summary]

---

#### Jakub's Section

```
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
🎯 JAKUB KREHEL — Production Polish
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```

**What to Check:**
- Enter animations (opacity + translateY + blur?)
- Exit animations (subtler than enters? Or missing entirely?)
- **Motion gaps** — Conditional renders without AnimatePresence (from gap analysis)
- **Layout transitions** — Size/position changes that snap instead of animate
- Shadow vs border usage on varied backgrounds
- Optical alignment (buttons with icons, play buttons)
- Hover state transitions (150-200ms minimum)
- Icon swap animations (opacity + scale + blur)
- Spring usage (bounce: 0 for professional, higher for playful)

**Body format:**

**What's Working Well**
- ✓ [Observation] — `file.tsx:line`

**Issues to Address**
- ✗ [Issue] — `file.tsx:line`
  [Brief explanation]

**Through Jakub's lens**: [1-2 sentence summary]

---

#### Jhey's Section

```
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
✨ JHEY TOMPKINS — Experimentation & Delight
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```

**What to Check:**
- Could @property enable smoother animations?
- Could linear() provide better easing curves?
- Are stagger effects using optimal techniques?
- Could scroll-driven animations improve the experience?
- What playful touches would enhance engagement?
- Are there celebration moments that need more delight? (streaks, achievements, etc.)

**Body format:**

**What's Working Well**
- ✓ [Observation] — `file.tsx:line`

**Opportunities**
- 💡 [Idea] — `file.tsx:line`
  [Brief explanation]

**Through Jhey's lens**: [1-2 sentence summary]

---

### Combined Recommendations

**Critical (Must Fix)**
| | Issue | File | Action |
|-|-------|------|--------|
| 🔴 | [Issue] | `file:line` | [Fix] |

**Important (Should Fix)**
| | Issue | File | Action |
|-|-------|------|--------|
| 🟡 | [Issue] | `file:line` | [Fix] |

**Opportunities (Could Enhance)**
| | Enhancement | Where | Impact |
|-|-------------|-------|--------|
| 🟢 | [Enhancement] | `file:line` | [Impact] |

---

### Lens Reference Summary

End every terminal audit with:

> **Which lens was referenced most**: [Designer Name] — [Perspective]
>
> **Why**: [Explanation based on the project context]
>
> **If you want to lean differently**:
> - To follow Emil more strictly: [specific actions]
> - To follow Jakub more strictly: [specific actions]
> - To follow Jhey more strictly: [specific actions]

---

## Mode selection

Default to HTML mode. Trigger terminal mode only when the user explicitly signals it via:

- `--terminal` / `--inline` / `--no-html` flag
- Natural-language equivalent: "show the full report inline," "skip the HTML," "no HTML," "terminal only"
- Any headless or CI environment where opening a browser doesn't apply

When in doubt, render HTML and mention the terminal-mode flag in the 3-line summary (see `workflows/audit.md` STEP 3) so the user knows the alternative exists.
