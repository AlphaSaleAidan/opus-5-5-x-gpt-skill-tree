---
name: credit-discipline-for-generation
description: Use before spending any paid generation credits or metered API calls (Higgsfield, fal, Fish Audio, Kling, Seedance, Topaz, Codex runs) on a video, image or audio job — especially reference-driven remakes, client commercials, or batches of clips — and whenever a job has a credit cap.
---

# Credit discipline for generation

## Overview
Generation is real money and the client notices waste. **Plan → quote → sign-off → cheapest probe →
batch.** A first cut that skipped the storyboard burned ~300 credits on clips that were all rebuilt.

**Violating the letter of these rules is violating the spirit.** "It's only a few credits" is how 300
went.

## The gates
1. **Storyboard before spend.** Frame-extract the reference (2 fps) → SHOTLIST.md → a board with the
   reference frame, timecode, what happens, and our plan per shot (keep / generate / comp / full-frame,
   source, est. credits). Send it; wait for sign-off. Only an explicit waiver from the person paying
   ("rip it end to end") skips this — log the waiver with the cap.
2. **Quote.** Per step: jobs × unit cost, retries at +30 %, total, and the hard cap. The MCP has no
   price list: measure the balance delta of ONE cheapest-tier job, or use a cost preflight tool, before a
   batch. State credits in every update.
3. **Source before generate.** Free/CC0/public-domain (Met Open Access, Wikimedia Commons,
   ambientCG), the client's own photos, local edits (mirror, re-letter, inpaint, logo swap) → only then
   generate what can't be sourced. Reuse/mirror one generation instead of paying for pairs.
4. **Stills before video.** Approve the still (≈2.75 cr) before the i2v clip (≈48 cr / 4 s). A bad
   still guarantees a bad clip.
5. **Cheapest probe first.** One shot, shortest billable duration, lowest tier that answers the question.
   Gate on it before submitting the rest.
6. **Log every job** the moment it's submitted — including refunded/refused ones:

   ```markdown
   # Credit log — <job>
   Approval <date> (<who>, <channel>): <scope>; HARD CAP <n> credits (balance at approval <n>)
   | time | tool/model | job | credits | running total |
   |---|---|---|---|---|
   | 23:58 | gpt_image_2_5 high 2k | identity still #1 | 2.75 | 2.75 |
   | 00:02 | ad_multiplier 1080p | swap — REJECTED ip_detected, refunded | 0 | 2.75 |
   ```
   Client work: the log doubles as the invoice line — log hours alongside.
7. **Stop at the cap.** At 80 % of the cap, tell the person what's left and what it buys. Never top up
   or exceed without a fresh, numbers-quoted OK.

## Red flags — stop and quote
- "Let me just try one more variant" after two misses on the same symptom → change the method.
- Re-rolling a whole clip for a local defect (wrong logo, side-eye, lip lag) → fix locally
  (`ai-video-logo-replace`, `lip-sync-and-gaze-qc`).
- Generating a background the model will re-render anyway (e.g. aperture prompts under a video-edit
  model that re-does the bokeh).
- A loop reporting "cap hit, completed 0" → it's looping; stop.
- Polishing a weak concept with more generations instead of changing the concept.

## Reference costs we paid (Higgsfield, 2026)
gpt_image_2_5 high 2k ≈2.75–3 cr · seedance_2_5 1080p 4 s ≈48 cr, 7 s ≈84 cr · Seedance video_edit
≈52 cr / 4 s · Ad Multiplier video_edit 1080p ≈132 cr / 10 s (≈55 cr for a ≥4 s single shot) ·
kling i2v 5 s 1080p ≈10 cr. Refused jobs (`ip_detected`, `nsfw`) were refunded. Prices change —
re-measure. Model routing → `higgsfield-production-routing`.
