---
name: ai-video-logo-replace
description: Use when an AI-generated video clip came back with the wrong logo, brand, or label printed on props (boxes, signs, shirts, packaging) and re-generating would cost credits or lose a good take — or when a label must be swapped on a clip without touching hands and lighting.
---

# AI video logo replace

## Overview
Don't re-roll a good generation for a wrong logo. If the print is one consistent ink colour, you can
detect it per frame (HSV), track it, inpaint it away and print your own mark in its place — shaded by
the surface underneath (multiply blend), hands excluded. Zero credits, minutes of CPU.

Only print marks the client is allowed to use (their own brand or licensed ones).

## When it works / when not
- Works: printed labels on mostly-static or slowly moving props, one saturated print colour that
  appears nowhere else in frame (e.g. green on cardboard).
- Doesn't: logos in the same colour as the scene, heavy motion blur, fast rotation past ~45°, prints
  wrapping around curved surfaces. Then regenerate the still with the right label and re-run i2v.

## Steps
1. **Probe first.** Grab 4–6 frames across the clip (start, middle, end, the frame with the smallest and
   largest print). Threshold in HSV and LOOK at the mask; tune `--hsv-lo/--hsv-hi` until every print is
   one blob and nothing else is.
2. **Assets.** The new mark as an RGBA PNG (alpha = shape; the script re-inks it), the wordmark font
   (the brand's typeface or the closest free one), the wordmark text, the ink colour.
3. **Run**:
   ```bash
   python scripts/logo_swap.py --in gen/boxes.mp4 --out gen/boxes_swapped.mp4 \
     --mark brand/mark.png --font fonts/Inter.ttf --text "Brand" \
     --hsv-lo 28,35,20 --hsv-hi 55,255,255 --ink 1a1a1a
   ```
   Per frame: HSV mask → morph CLOSE (45×75 ellipse, fuses icon + word) + dilate → contours ≥800 px² →
   minAreaRect → greedy IoU tracking + EMA (α 0.45) so the label doesn't jitter → TELEA inpaint of the
   print + its padded footprint → label contain-fit into the rotated rect, perspective-warped,
   multiply-blended over the inpainted surface, 1 px blur → skin-coloured pixels never painted.
4. **Verify** at client zoom (`video-qc-reviewer`): crops ≥550 px of the smallest and largest print at
   start/mid/end; no leftover coloured fringe; hands passing in front stay on top; label doesn't swim.
   It printed detections/frame min/avg/max — a min of 0 on frames that show a print = missed frames.

## Parameters worth knowing
| Knob | Default | Why |
|---|---|---|
| no MORPH_OPEN | — | distant prints are 1–2 px strokes; an open erased them (h 132 → 49 px) and left a fringe |
| `PAD_FRAC` | 0.14 | label must fully cover the old print |
| `MAX_MISSED_RENDER` / `DROP` | 1 / 4 | keep painting through a one-frame detection miss |
| inpaint mask | green px ∪ padded track quad | anti-aliased fringe outside the threshold otherwise leaks a tint |
| label fit | contain, own aspect | stretching the mark into an oval is the first thing a client sees |

## What FAILED / pitfalls
- MORPH_OPEN to clean noise: erased small prints (see table). MIN_AREA does the noise job.
- Inpainting only the thresholded pixels: tinted halo around the new label.
- Stretching the label to the detected rect: oval logos.
- Painting over hands that pass in front of the box: add the skin mask; tune it to the clip's light.
- This is not a learned tracker: fine for static boxes; upgrade (optical flow / a detector) only when a
  clip visibly defeats it.

## Status
Generalized from the script used on the job (where it ran on the full clip); **untested as generalized**.
