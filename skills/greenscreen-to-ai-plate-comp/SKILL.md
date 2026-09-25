---
name: greenscreen-to-ai-plate-comp
description: Use when green-screen talent must be placed into a generated or built environment for a commercial — the composite looks pasted, talent floats, lighting or focus doesn't match the background, the background is a dead still, or edges/hair/props glitch green. Covers the Higgsfield Ad Multiplier merge and the raw-key-over-animated-plate chain.
---

# Green screen → AI plate composite

## Overview
Two working routes, pick by lighting:
- **A. Ad Multiplier merge** (Higgsfield `ad_multiplier`, `video_edit`): the model renders the people INTO
  the scene — bokeh, sun, shadows. Fastest route to "one real shot" when the set light doesn't match
  the background. Costs: talent gets an AI pass (waxy after several), props move, the model redoes focus.
- **B. Raw key over an animated photoreal plate** (the version the client finally shipped): generate the
  background to MATCH the set light (overcast for flat studio light), animate the SHARP still, blur by
  depth after, key the raw 4K take. Talent stays 100 % real.

Rule of thumb: if you can make the plate's light match the set, B wins; otherwise A.

## Shared front end
1. Layout per shot from boards / a Blender set (`blender-set-from-storyboard`), 16:9 window, camera
   height + lens matched to the take.
2. **Photoreal background** — `gpt_image_2_5` edit (≈3 cr, 2k, high) with ONLY the layout render as
   reference (adding the painted board made it look painted): "a real photograph … 35 mm f/2.8, plain
   sky, no HDR, imperfections: parked car, power line, garden hose, patchy lawn, wet paving".
   To match flat studio light: "relight this exact photograph … overcast" with the sharp still as the
   only ref — layout held perfectly. Keep the background SHARP here.
3. Never loop a short take to fill a shot (visible repeat). Scan every source take for black/foreign
   frames at its ends (a cropped take carried black frames 0–1 and 71–75 plus a foreign close-up at 76).

## Route A — Ad Multiplier
`get_workflow_instructions(workflow:"ad-multiplier")` first. Source = raw green-screen cut (4–30 s) as
`@Video1`; backgrounds as `@Image1..N` (generation job ids work as media); a COMPACT prompt per time
segment ("Replace only the green-screen studio background in @Video1 with the location from @Image1,
lit by that sun…") + the mandatory preservation block; name every key prop per segment or it's dropped;
`declined_preset_id` when the "IN THE DARK" preset nag blocks the literal job. ≈132 cr / 10 s at 1080p,
≈12 min, output is SILENT → mux the take's audio back. Crop the output to lose feet if the model
regenerated full bodies.

## Route B — raw key over a moving plate (0 cr except the plate animation)
1. **Moving plate:** `kling3_0` pro image-to-video from the SHARP 16:9 still, no end image, "steady
   autumn wind… canopy sways visibly… hedges rustle… camera locked off" (≈10 cr / 5 s). Check locked
   regions drift < 0.4 px (`cv2.phaseCorrelate` on a static patch) and that foliage actually moves.
2. **Depth + focus AFTER animation:** Depth Anything V2 **Small** (Apache; Base/Large are
   non-commercial) → `scripts/lens_blur.py --inverse --focus 4.3 --fstop 4 --focal 35` per frame.
   The client picks the f-stop; "focus proportional", not evenly soft.
3. **Key the raw 4K take:** colour-difference key with the high threshold taken from the MEASURED screen
   colour (a fixed hi .16 below the screen's .25 chopped hair and paper edges); despill `g ≤ avg(r,b)`
   (`max` greened skin; gate paper despill to bright AND g>max(r,b)); eroded RVM core as holdout; hole
   fill; a screen-guard for hair wisps over shaded green (holes near screen colour + dark neighbourhood
   → alpha 0, 1 px soft rim). ffmpeg alternative: `format=rgba,chromakey=0x<screen>:0.045–0.055:0.02,
   despill=mix=0.35`; decode alpha webm with `-c:v libvpx-vp9` or the alpha is lost.
4. **Match:** measure whites/median of talent vs plate and map 75 % of the way; light wrap 0.2;
   0.55 px blur on close-ups; measured grain; subtle "breathe" camera move only if the client wants it;
   ambience bed (wind/leaves at −24/−36 dB) under the take audio.

## What FAILED (in order of cost)
| Tried | Why it failed |
|---|---|
| 14 rounds of key + numpy comp over Blender plates (defocus, relight, wrap, moving plates) | Scored 0–4/10: flat frontal set light vs warm side sun; pasted look |
| Prompting apertures into Ad Multiplier backgrounds | It re-renders focus itself (house sharpness 61 → 6); refocusing after with the Blender depth failed because it MOVES objects |
| Ad Multiplier + Seedance wind + RVM re-matte on talent | Three AI passes = waxy, over-sharpened face; newspaper morphed |
| Seedance `video_edit` wind over the whole cut | Repainted the wide (new trees, house gone) — per shot only, "do not add any new objects" |
| Seedance `video_edit` on some shots | Status `nsfw` false positive on the INPUT (refunded); same prompt passed on another shot |
| FLUX video edit / Kling Omni Edit for foliage motion | Shimmer on the house / frozen |
| Kling i2v from a pre-blurred still | Frozen — animators need a sharp start frame |
| Warping the still (hand sway masks, Blender optical flow) for wind | Rubber-sheet wobble — "the screen is moving the bushes" |
| Ad Multiplier with black padding around a reframed wide | Left the black bars; do the reframe as its own ≥4 s job from a padded comp |
| Chroma key with a fixed high threshold | Ate hair/paper edges; printed green props lost to the key |

## Deliver
Upscale the final to 4K with Topaz (`upscale_video` 2160p) only after picture lock; host a download page
that stays up (not a quick tunnel); per-version folders; see `commercial-production-pipeline`.

## Status
`lens_blur.py` is an **untested rewrite** of the job's layered thin-lens blur; the key/despill/match steps
are documented from the shipped version, not packaged as a script.
