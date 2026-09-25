---
name: lip-sync-and-gaze-qc
description: Use when a generated or re-synced talking shot looks off — mouth moves before/after the words, lips under-articulate, the eyes side-eye or drift off-lens, or the head angle doesn't match the shot it replaces. Also use when choosing which seconds of an AI video clip to use, or when re-syncing a real actor's mouth to a replaced line.
---

# Lip-sync and gaze QC

## Overview
Measure, don't eyeball. Lip lag is a number (cross-correlation of mouth opening vs voice loudness);
gaze is a number (iris position inside the eye). Fix lag by delaying the picture, fix gaze by picking
a better window or by a gaze edit — never by freezing frames.

## When to use / not
- Use after any i2v clip with `audio_references` lip-sync, after any lip-sync API pass, and before
  cutting any AI clip into a shot where the character addresses someone.
- Full scene replacement recipe → `person-into-famous-scene`. Voice building → `performance-voice-conversion`.

## 1. Lip lag
```bash
python scripts/lip_lag.py --video gen/speaking.mp4 --audio vo/line.wav \
  --model face_landmarker.task --fps 30        # prints lag in frames; + = mouth early
```
Mouth aperture = distance of mediapipe landmarks 13/14 ÷ face height (10/152); voice = per-frame log
RMS; best lag in ±20 frames. Seedance audio-reference clips ran the mouth **5–11 frames AHEAD** of the
voice. Fix: delay the picture by that many frames, easing the delay in over the first second
(`composite_person.py --lag N`) — a hard freeze is visible. Re-measure after the fix (expect 0 ±1).
`corr < 0.2` = wrong face or wrong track; don't trust the number.
`face_landmarker.task`: mediapipe model zoo (face_landmarker/float16). The video must carry the
voice or you pass `--audio` (Higgsfield outputs are often silent).

## 2. Gaze + head angle → pick the window
```bash
python scripts/gaze.py --image refs/actor_frame.jpg --model face_landmarker.task   # target gx/gy/yaw
python scripts/gaze.py --video gen/clip.mp4 --model face_landmarker.task \
  --window 11 --target-yaw 0.6 --csv gaze.csv   # best + second-best window start frames
```
Use the best window for the first appearance and the second-best for a repeat, so a montage cycle
doesn't show the identical frames twice. i2v models love side-eye; generate longer (4–7 s) than the slot
and pick.

## 3. Gaze correction (when no window is good enough)
FaceFusion face editor on the GPU box (`remote-gpu-render`):
```bash
python facefusion.py headless-run -s ref.jpg -t clip.mp4 -o clip_gaze.mp4 \
  --processors face_editor --face-editor-model live_portrait \
  --face-editor-eye-gaze-horizontal -0.45 --output-video-quality 100 --execution-providers cuda
```
−0.4…−0.5 horizontal pulled a side-eye back to the lens. On CPU it took ~30 min for 169 frames
(~11 s/frame), so run it on the GPU. Re-run `gaze.py` on the output to prove it.

## 4. Re-syncing a REAL actor's mouth to a changed line
- Commercial lip-sync API (fal `sync-lipsync` v2 / pro) on a **tight face crop**, never the wide 4K frame
  (full-frame re-encode adds noise everywhere).
- Composite **only the mouth box** (Gaussian-feathered) back over the pristine original, only during the
  changed words; ramp the mouth mask in/out over a few frames so it hands back to the real mouth.
- Cut the source to that person's shot only — the model animates ANY face in frame.
- Under-articulated mouth = quiet driver audio. Denoise + loudnorm the driver to ≈ −15 LUFS, re-roll.
- Box the mouth by hand on a labelled grid zoom; auto-boxing by pixel diff failed.

## What FAILED
| Tried | Result |
|---|---|
| Freezing / dropping frames to re-align lips | Visible stall; delay + ease-in is invisible |
| Auto-ranking takes by mouth-vs-audio correlation on moving full-body shots | Noisy — present both takes to the client |
| Driver audio at −23 LUFS into sync v2/pro | Mouth barely moved |
| Full-shot "re-animate everything" sync tools for a one-word fix | Regenerates the whole mouth track; wrong tool |
| Kling audio-to-video lipsync called with video_url + audio_url | Echoed the input back — wrong schema |
| Trusting a clip because the first frame looked right | Gaze drifts mid-clip; measure every frame |

## Status
`gaze.py` was run on a real clip (121 frames) during authoring. `lip_lag.py` is **untested end to end**
(written from the measurement used on the job; run it on a clip with known lag before relying on it).
