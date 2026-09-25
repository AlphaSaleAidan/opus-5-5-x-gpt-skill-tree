---
name: higgsfield-production-routing
description: Use when choosing which Higgsfield model or MCP call to use for a production job — identity-preserving stills, image-to-video, lip-synced talking shots, green-screen merges, moving background plates, video harmonization, character/Soul training — or when a Higgsfield job is refused (ip_detected, nsfw), blocked by a preset recommendation, or its upload fails.
---

# Higgsfield production routing

## Overview
Route by job, not by habit, and always through the **MCP** (the CLI's device login is dead; the locally
installed `higgsfield-*` skills are stale — the MCP's live workflow catalog is canonical). Every call
below costs credits → `credit-discipline-for-generation` first.

## Which model for which job (as used in production, 2026)
| Job | Model / tool | Settings that worked | ≈ Credits |
|---|---|---|---|
| Identity-preserving still of a REAL person (new wardrobe, mustache, scene light, framing) | `gpt_image_2_5` edit, real photo as reference | quality high, 2k; open-eyed refs | 2.75 |
| Photoreal background from a layout render; relight a still ("overcast") | `gpt_image_2_5` edit | layout render as the ONLY ref, 3:2 or 16:9, "a real photograph… 35 mm… imperfections" | 3 |
| Image → video of that person | `seedance_2_5` omni reference | start image = approved still; 1080p; 4 s or 7 s | 48 / 4 s, 84 / 7 s |
| Talking shot, lips synced to a voice | `seedance_2_5` + `audio_references` (the voice) | then measure lip lag (`lip-sync-and-gaze-qc`) | 84 / 7 s |
| Green-screen talent into a generated location | `ad_multiplier`, mode `video_edit` | raw cut 4–30 s as `@Video1`, backgrounds `@Image1..N`, compact per-segment prompt + preservation block | 132 / 10 s 1080p |
| Relight / add wind to an existing clip (harmonize) | Seedance `video_edit` | per shot, "camera completely still, do not add any new objects" | 52 / 4 s |
| Moving background plate (foliage, ambient) | `kling3_0` pro image-to-video | SHARP start image, no end image, "camera locked off" | ≈10 / 5 s |
| 4K deliverable | `upscale_video` (Topaz) 2160p | after picture lock only | — |
| Persistent character across many generations | Soul ID / `soul_2` training | only when there's no real photo to edit | — |
Live IDs and parameters: `models_explore`, never a skill file.

## MCP call patterns
1. `balance` → `get_workflow_instructions` (no argument) BEFORE any multi-step job; for multi-edit of one
   clip `get_workflow_instructions(workflow:"ad-multiplier")`; bundled refs via `get_workflow_bundle_file`.
2. Unsure of the model → `models_explore(action:"recommend", …)`, then `models_explore` get for params.
3. Cost: use the cost preflight if the MCP exposes one; otherwise run ONE cheapest-tier job and read the
   `balance` delta before any batch. Log it.
4. Uploads: `media_upload` → PUT the bytes to the returned URL → `media_confirm` → use the media id.
   **Audio uploads must be MP3** (convert WAV first). A previous generation's job id also works as media.
5. Several independent generations → `generate_image_batch` / `generate_video_batch`, then ONE
   `jobs_wait`, then one `show_generation_by_ids`. Don't hand-poll in a loop.
6. A preset recommendation (e.g. "IN THE DARK") blocking a literal job → resubmit with
   `declined_preset_id`. Browsing presets never authorizes running one.
7. Download results immediately and ffprobe them (fps/res can differ from the ask; outputs are often
   silent → mux audio back).

## Refusals
- `ip_detected` on copyrighted film/TV footage (refunded): **stop**. Never crop, flip, blur, re-grade or
  otherwise disguise footage to get past it. Generate the person and composite locally
  (`person-into-famous-scene`).
- `nsfw` false positives on harmless input video (refunded): the filter trips on the input, not the
  prompt; the same prompt passed on another shot. Try a different shot/trim once, then do it locally.

## What FAILED
| Tried | Result | Instead |
|---|---|---|
| Generating a real person from a text prompt / trained character | Face drifts from the real person | `gpt_image_2_5` edit of real photos |
| Using an i2v clip from frame 0 | Side-eye / gaze wander | Generate longer, pick the window by gaze (`lip-sync-and-gaze-qc`) |
| Trusting audio-reference lip-sync as delivered | Mouth led the voice by 5–11 frames | Measure, delay picture with ease-in |
| Prompting aperture/DoF into backgrounds for Ad Multiplier | It re-renders focus | Blur by depth after, on your own plate |
| Animating a pre-blurred still (Kling i2v) | Frozen output | Animate sharp, blur after |
| One video_edit pass over a whole multi-shot cut | Repainted shots | Per-shot jobs |
| Re-rolling a whole clip for a wrong printed logo | Wasted credits | `ai-video-logo-replace` |

## Router rows (for SKILL-ROUTER.md)
- AI media generation (image/video/3D/audio) → `higgsfield-production-routing` (+ `higgsfield-generate`
  basics) — cost-quote first.
- GPU jobs (FaceFusion, ESRGAN 4K, Seed-VC) → the RTX box over the tunnel (`remote-gpu-render`); light
  assembly/mix/captions → the server; big parallel CPU batches (many render variants) → cloud sessions.
