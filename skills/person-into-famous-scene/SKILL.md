---
name: person-into-famous-scene
description: Use when a client wants a real person put into a famous film/TV scene or fan edit (a "me as the movie character" video) — replacing the lead actor's face/body in an existing edit, keeping the edit's cut, grade and music. Also use when local face swaps (inswapper, hyperswap, FaceFusion) look fake, or when Higgsfield returns ip_detected on copyrighted footage.
---

# Person into a famous scene

## Overview
Don't swap faces onto the film. **Generate the person in-scene** (identity-edit of their REAL photos →
image-to-video), then **composite that clip over the edit's own plates** with only the original actor
removed. The edit's cut, grade, softness and grain stay the edit's; only the person changes.

Consent first: the person being inserted must have agreed to their face (and voice) being used.
Never clone a non-consenting third party's voice (the other actors keep their original audio, or are
struck through in subtitles instead).

## When to use / not
- Use: fan edits, "put my client in the Narcos/Godfather scene", reference-edit remakes with a new lead.
- Not for green-screen talent into a generated set → `greenscreen-to-ai-plate-comp`.
- Not for recreating a reference edit's motion graphics → `studio-vfx`, `kinetic-type-physics`.
- Rebuilding the edit itself from clean sources (music sync, cadence, grade) → `edit-rebuild-from-clean-sources`.

## Pipeline
1. **Clean sources.** Find the original scene at the best quality you can (owned episode, else a ≥720p upload
   with original audio) and the clean song(s). Never rebuild from the TikTok's own mixed audio.
   Rebuild cut/cadence/grade first (`edit-rebuild-from-clean-sources`).
2. **Shot map.** Per shot: keep / generate-and-comp / full-frame. Plain dark backgrounds → full-frame;
   anything with crew, set, props in front → comp over the plate.
3. **Identity stills** (`higgsfield-production-routing`): `gpt_image_2_5` EDIT of a real photo of the
   person (high, 2k, ≈2.75 cr) — "same person, same face; add <character's mustache/wardrobe>; <scene
   lighting>; framing matching this reference frame". Use OPEN-EYED references (smiling selfies make
   the result squint). Reject any still where identity drifted — compare side by side with the photo.
4. **Image → video**: `seedance_2_5` omni reference, start image = the approved still, 4 s ≈48 cr,
   7 s ≈84 cr at 1080p. For a speaking shot add the voice as `audio_references` → the model lip-syncs.
5. **Pick the window**: gaze + head angle must match the actor (`lip-sync-and-gaze-qc`, `gaze.py`).
   Measure mouth-vs-voice lag on speaking shots; the mouth ran 5–11 frames AHEAD of the voice.
6. **Composite** (`scripts/composite_person.py`): actor-only mask (person seg ∩ column around his face)
   → LaMa inpaint → fit by face height + eye centre → RVM matte → LAB grade to the actor's region →
   blur until Laplacian variance matches the plate → matched grain. `--fullframe` for plain shots,
   `--lag N` for measured lip lag (eases in, never freezes), `--clean-plate` when you have one.
7. **Gaze fix** if the clip side-eyes: FaceFusion `face_editor` (live_portrait) horizontal gaze −0.4/−0.5
   on the GPU box (`remote-gpu-render`).
8. **Assemble + QC**: fresh-context reviewer, frame by frame (`video-qc-reviewer`), at client zoom.

```bash
python scripts/composite_person.py --plates shot07.mp4 --gen gen/person_07.mp4 \
  --actor-face refs/actor.jpg --out comp/shot07 --gen-start 40 \
  --lama models/lama_fp32.onnx --rvm models/rvm_mobilenetv3_fp32.onnx
python scripts/composite_person.py --plates shot05.mp4 --gen gen/person_05.mp4 \
  --actor-face refs/actor.jpg --out comp/shot05 --fullframe ...
```
Models: LaMa ONNX (`lama_fp32.onnx`, FaceFusion/IOPaint mirrors), RVM `rvm_mobilenetv3_fp32.onnx`
(PeterL1n/RobustVideoMatting releases), insightface `buffalo_l`, rembg `u2net_human_seg`.

## Rules the client cared about
- The character's signature features stay (e.g. the character's mustache on the new person, the
  character's hair and wardrobe). Put them in the identity-edit prompt, not in post.
- The character's stare is direct, head turned to whoever he addresses — never side-eye.
- New lines the other actors say about the character get a hand-drawn marker strike-through in the
  subtitle + the person's name written above (Permanent Marker, red, 6-frame stroke, 3-frame pop),
  rather than cloning those actors' voices.
- Inserts may extend the edit (new generated shots on the beat), graded to the edit's look.

## What FAILED
| Tried | Result | Do instead |
|---|---|---|
| Higgsfield Ad Multiplier / Seedance video_edit on the film footage | status `ip_detected`, refunded | Generate the person, comp locally. **Never** crop/flip/blur/re-grade footage to sneak it past the check. |
| inswapper_128 / hyperswap_1c_256 + GPEN (FaceFusion) on the plates | Client: "really bad" — plastic skin, wrong bone structure, squint, mustache lost | Identity-edit stills + i2v + comp |
| Generating the person from scratch (text prompt / Soul) | Face drifts from the real person | Edit REAL photos with gpt_image_2_5 |
| Smiling/squinting selfies as identity refs | Squinting output | Rank refs by eye openness |
| Pasting the i2v clip unsoftened | AI clip is much sharper than a compressed edit — reads as a sticker | Laplacian-matched blur + measured grain |
| Freezing frames to fix lip lag | Visible stall | Delay picture, ease in over 1 s |

## Budget
Typical shot: 1 still (≈2.75 cr) + one 4 s clip (≈48 cr). A 9-shot montage + one 7 s speaking shot
landed ≈450 cr; a full job with re-rolls ≈875 cr. Quote first (`credit-discipline-for-generation`).

## Status
`composite_person.py` generalizes the job's working comp scripts but is **untested as written** (a smoke
run wrote 7 of 8 frames without errors before it was stopped to free the CPU; output not reviewed). Run it on 8–10 frames first and check a contact sheet.
