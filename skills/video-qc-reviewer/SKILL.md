---
name: video-qc-reviewer
description: Use before sending any video, VFX shot, composite or edit to a client or calling it done — and whenever a client says it "looks off", "glitches", or "looks AI" but can't say where. Covers the frame-by-frame review protocol, contact sheets, zoom crops and the findings table.
---

# Video QC reviewer

## Overview
The person who built the shot is the worst judge of it. Review with a **fresh-context reviewer** (a new
Opus subagent that did not build it) that frame-steps the ACTUAL output file and returns a findings
table. Nothing ships with an open S1/S2.

## Protocol
1. **Machine checks first** (the reviewer runs them, doesn't trust the builder's claims):
   - `ffprobe`: width/height, fps (CFR), frame count, duration, codec, pix_fmt, colour tags, audio
     stream present, sample rate, channels.
   - Black/flash scan: per-frame mean luma; flag any frame < 30 % or > 170 % of its neighbours
     (source takes often carry black frames at their ends; AI clips often have a glitch frame at the head).
   - Duplicate-run scan: identical consecutive frames beyond what the cadence explains = a freeze.
   - Audio: loudness (`loudnorm` measure) vs target; transcribe the dialogue and diff against the script.
2. **Contact sheets** — every 3rd frame, labelled frame + timecode, ≤1400 px wide:
   ```bash
   python scripts/sheets.py --video out/final.mp4 --out qc/ --every 3
   ```
   View sheets one at a time. Never view a full-res frame dump or a data: URL.
3. **Zoom crops at client zoom** on every changed region (face, mouth, matte edge, replaced text,
   logo, hair), start / middle / end of each shot, ≥550 px crops from the FINAL file:
   ```bash
   python scripts/sheets.py --video out/final.mp4 --out qc/zoom --zoom 820,380,560,560 --frames 480,495,510
   ```
   Also inventory what else is near each edit (props behind, reflections, a second note, feet, shadows)
   and confirm it's untouched and not crowded.
4. **In context.** Judge the shot as it plays in the cut, at full speed, at the delivery size (and on a
   phone-size frame for social deliverables). An isolated-on-black view is diagnostic only.
5. **Compare to the reference** where there is one: side-by-side frames at identical timecodes.
6. **Findings table** — the only output format:

| # | Time / frames | Shot | What's wrong | Sev | Fix |
|---|---|---|---|---|---|
| 1 | 12.40–12.53 / 372–376 | wide | 5 near-black frames at the take's tail | S1 | hold last clean frame (370) |
| 2 | 3.10 / 93 | CU | hair wisp flickers grey over screen colour | S2 | screen-guard holdout on wisps |

Severity: **S1** broken (black/flash frame, wrong shot, audio missing, identity wrong) · **S2** a client
will notice (edge flicker, lip lag, side-eye, loop visible, text size mismatch) · **S3** polish.

## Reviewer prompt (for the subagent)
"You did not build this. Review `<file>` against `<plan/reference>`. Run the machine checks, make
contact sheets every 3rd frame (≤1400 px), zoom crops on every changed region at start/mid/end, and
return ONLY the findings table (time, frames, shot, problem, S1–S3, concrete fix). Quote measured
numbers. If you didn't check something, list it as not checked."

## Common catches
- Looping a short take to fill a shot: visible repeat ("characters glitching"). Hold or extend instead.
- Replacement text rendered larger than neighbouring lines; edit crowding a nearby prop.
- Green spill on printed green props / skin after a key; hair wisps filled grey by a holdout.
- AI clip head/tail glitch frames with black borders.
- Grade or softness jump between a generated insert and the plates around it.
- Captions: wrong onset vs the spoken word, illegible at phone size.

## What FAILED
- Builder self-review at thumbnail size: shipped a word visibly larger than its neighbours.
- 380 px verification crops: defects only visible at the client's 4K zoom.
- Measuring text with a bare luminance threshold: caught the monitor bezel and shifted the layout —
  colour-mask the prop's surface first.
- Random-seek frame grabs for sheets: wrong frames. Decode sequentially (the script does).

## Status
`sheets.py` is new for this skill and **untested** (written without running video jobs on the box).
