---
name: beat-synced-overlays
description: Use when a music-driven montage or fan edit feels flat or "cut, cut, cut" and needs editor-style accents on the beat — flash frames, double exposures, ghost overlays of a close-up over the next shot — or when those accents land off the kick or wash out the blacks.
---

# Beat-synced overlays

## Overview
Accents belong on the kicks, not on every cut. Score each cut by low-end energy at the cut, take the
strongest few with a spacing guard, and apply three effect types as a **separate pass** that writes
only changed frames, so the base render stays untouched and the pass can be re-run or dropped.

## Recipe
1. Render the montage to PNG frames (`00000.png…`) and mix the final audio first — the kicks come from
   the FINAL mix, not the raw song (ducks and edits move them).
2. List the cut frames (cut detection, or `start:end:step` for a fixed-length montage cycle).
3. Pick content pairs for ghosts by eye: a dark, still close-up over a bright/busy shot (fire, cars,
   crowd) reads best. Leave the first frame of the drop clean.
4. Run:
   ```bash
   python scripts/overlays.py --frames comp/ --out overlay/ --audio final_mix.wav \
     --cuts 395:790:11 --flash 3 --double 4 --min-gap 22 --keep-clean 395 --ghost 411:494 619:713
   ```
5. In the renderer, prefer `overlay/NNNNN.png` over the base frame when it exists.
6. Review in motion at full speed AND frame-step the chosen moments (`video-qc-reviewer`).

## Effect specs (what read well)
| Effect | Spec | Why |
|---|---|---|
| Flash frame | 2 frames, warm white (255,228,195), α 0.88 then 0.30 | a 50–70 % half-blend reads muddy/fogged — commit on frame 1 |
| Double exposure | 4 frames, frozen outgoing frame × (1−t)·0.55 **screen**-blended over incoming, incoming zoom 1.00→1.04 | screen keeps blacks black; zoom adds energy |
| Ghost overlay | static close-up zoomed 1.12, pre-multiplied ×0.30, screen over the whole next shot (11 frames) | presence without hiding the shot |
| Spacing | ≥22 frames between accents, ~8–10 per 20 s | "not every cut" |
Kick score: 4th-order band-pass 45–140 Hz → |Hilbert| → 5 ms smoothing → max in [cut−40 ms, cut+120 ms].

## What FAILED
- Normal/alpha blending for ghosts and double exposures: lifted the blacks, washed out the grade.
- Half-strength (50–70 %) flashes: fogged and muddy — neither image nor flash.
- Keep the pass separate from the base frames so it can be A/B'd or dropped without a re-render.

## Status
Generalized from the job's overlay pass (hard-coded frame ranges → CLI flags); **untested as generalized**.
Compare with `kinetic-type-physics` for text accents and `hyperframes:music-to-video` for HTML beat edits.
