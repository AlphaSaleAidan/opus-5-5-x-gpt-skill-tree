---
name: blender-set-from-storyboard
description: Use when a commercial or VFX job needs a 3D set built from storyboard panels (painted or sketched boards) — to place cameras that match the boards, keep prop continuity between shots, render plates and depth passes for compositing, or give the client a walkable browser preview of the set.
---

# Blender set from storyboard

## Overview
Boards are drawings: they give **blocking, shot size, wardrobe and season — not photoreal light or
exact perspective.** Build the set in Blender to the boards' layout, solve cameras "relatively close",
enforce continuity with a script, then use the renders as **layout references** for photoreal
backgrounds (see `greenscreen-to-ai-plate-comp`). Blender is the layout tool, not the final look.

## Acceptance bar (set by the client — don't exceed it)
A camera matches a board when the key props (the hero prop, house, fence) sit roughly where the board
has them (≤ ~10 % of frame width), the horizon is level (roll 0), and the lens feels similar. Do NOT
run more solve rounds chasing pixel error on painted boards.

## Pipeline
1. **Read the boards** (often the script PDF's IMAGE column — text extraction drops it; render the PDF
   pages to images). List per panel: props, their left/right order, shot size, who stands where.
2. **Block the set** (Blender 4.2 LTS; Bonsai/BIM for architecture). One instance of every hero prop —
   its position is a **ruling** derived from where the panels put it, written down, never a guess.
3. **Cameras.** Solve each to board landmarks with the hero prop fixed, then level it. When a board
   implies an impossible camera (long lens far back → inside street geometry), drop it or reframe.
   Owner fix-path: the browser tour (below) — they frame by eye with the board overlay on and press C;
   paste the numbers:
   ```bash
   blender -b set.blend -P scripts/set_tools.py -- camera CAM_01 3.8 -2.4 1.28 -0.8 4.2 1.35 35
   ```
4. **Continuity check** every round (prop order per camera + 30° rule between consecutive cameras):
   ```bash
   blender -b set.blend -P scripts/set_tools.py -- continuity CAM_01,CAM_02 Mailbox,Walkway,House Talent
   ```
   Write the result to `renders/CONTINUITY-rNN.md`. Every exterior camera stays on one side of the
   action line.
5. **Plates + depth.** Render plates per camera; export depth INSIDE Blender to .npy (OpenCV without
   OpenEXR can't read the EXR):
   ```bash
   blender -b set.blend -P scripts/set_tools.py -- depth CAM_01 renders/depth/CAM_01.npy
   ```
6. **Browser tour** for the client: GLB from a COPY of the .blend
   (`-- glb out/set.glb`), three.js walk page: WASD, number keys = cameras at real lens, B = board
   overlay + wipe, M = marks, C = print camera numbers. Re-export after every round. A GPU-less
   server can't render WebGL headless — the owner checks it on their machine.
7. **Hand off** plates to the background/comp stage; the set's job ends at layout.

## Budget
256 spp on all cameras ran ~5 h in one agent round; a GPT/Codex Blender round cost ≈$7–10 of usage
and one agent died on credits mid-round. Render finals LOCALLY with a script
(render → marks → animatic → tour export), low spp for previews.

## What FAILED
| Tried | Result |
|---|---|
| OpenCV free camera solve to painted boards | Rolled the cameras (tilted horizon) |
| Level solve chasing pixel error | Showed the set layout itself differs from the boards — more rounds won't converge |
| Guessing the hero prop's position between rounds | Continuity broke across shots; client: "she has to stay by the mailbox" |
| Stretching a 3:2 plate crop to 16:9 | "Compressed" shot — crop a 16:9 window instead |
| Blender plate used directly as the background | Reads CG; use it only as the layout ref for a photoreal generation |
| Blender wind on foliage → optical flow → warp the photoreal still | Rubber-sheet wobble; flow doesn't register to the AI photo. Rejected. |
| Blender trees to stand in for the AI photo's trees | Different trees; never matches |
| Exporting GLB from the .blend a render was using | Risky — always export from a copy |

## Status
`set_tools.py` combines the job's camera/continuity/depth/export steps into one file; **untested as
combined** (no Blender runs during authoring).
