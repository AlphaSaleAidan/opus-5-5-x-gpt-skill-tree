---
name: commercial-production-pipeline
description: Use when producing or fixing a client commercial, TV spot, ad, VSL, fan edit or any client video deliverable end to end — from brief to delivery — or when a video job is looping through revisions, the client is confused about versions, or a delivery email/link is about to go out.
---

# Commercial production pipeline

## Overview
Every expensive miss on client video came from skipping a gate: building before the shot map was
agreed, judging at thumbnail size, piling up versions, or sending before checking the link. The
pipeline is the gates. Specialist steps live in their own skills (linked below).

## The pipeline
1. **Brief.** Goal, deliverables (length, aspect, resolution, fps, loudness), deadline, what the client
   is graded on (often: matching a reference effect one for one), who approves, spend cap. Read the
   client's materials fully — boards are sometimes the IMAGE column of the script PDF.
2. **Reference breakdown.** 2 fps frame extract → SHOTLIST.md (timecode, shot size, effect by its
   market name, what happens). Measure the reference: fps per section, loudness, cuts, captions.
3. **Storyboard + quote → sign-off.** Reference board + remake board (per shot: ref frame, our plan,
   source, status, credits). Send the JPG; wait. No spend before it (`credit-discipline-for-generation`).
4. **Asset order: shoot > license > source free > generate.** Generated interiors and physics (thrown
   objects, stunts, tear-aways) are where "obviously AI" shows first; cut or do them practically.
5. **Audio first, picture to audio.** Lock VO/music, measure durations, then time the cut. Recompute all
   downstream timings with a script — never hand-patch one offset.
6. **Build** with the right skill:
   | Job | Skill |
   |---|---|
   | Recreate a reference's look/motion graphics with our footage | `studio-vfx`, `kinetic-type-physics` |
   | Green-screen talent into a built/generated location | `blender-set-from-storyboard` → `greenscreen-to-ai-plate-comp` |
   | Put a person into a famous scene | `person-into-famous-scene` |
   | Voice / performance / phone VO | `performance-voice-conversion` (+ Fish cloning notes for studio VO) |
   | Lip-sync, gaze, re-syncing a real actor's mouth | `lip-sync-and-gaze-qc` |
   | Fan-edit rebuild, music sync, cadence, grade | `edit-rebuild-from-clean-sources` |
   | Wrong logo on an AI clip | `ai-video-logo-replace` |
   | Beat accents | `beat-synced-overlays` |
   | GPU-heavy passes | `remote-gpu-render` |
   | Which Higgsfield model | `higgsfield-production-routing` |
7. **QC** with a fresh reviewer, frame by frame, at client zoom (`video-qc-reviewer`).
8. **Review round.** One page per round (below). Collect notes by the client's own shot tags.
9. **Deliver** (rules below). Log hours + credits the same session.

## Review loops that worked
- **Side-by-side** (reference left, ours right), shot-matched by a timing-aware render — best format for
  "does it match".
- **Storyboard loop:** client flags shots by number → fix pass → recapture → resend.
- **Isolation test** when the client hears/sees a problem you can't pin: the SAME output processed 3
  ways, one variable changed per take; their pick names the culprit.
- **Two candidates** when auto-ranking is unreliable (e.g. lip-sync takes on a moving shot).
- **Presentation page** for non-technical stakeholders: board → layout → background → raw → key/plate →
  final, one row per stage.
- **Version library** grouped by shot, oldest → newest, once the client starts asking "which one did you
  mean" — but show ONE polished version per structurally distinct option ("19 iterations is not desired").
- Label everything with the client's language, never internal filenames.

## Delivery rules
- **Some clients get no automated email, ever** — you draft, the human sends. Default to draft-only
  for any client until told otherwise; ask before every send.
- Client email = designed HTML with a plain-text fallback, rendered and screenshot-checked at mobile and
  desktop widths; links as labelled buttons; `curl` every link (200/206) before it goes in a draft.
- Links: direct file links, no spaces in filenames, no Drive folder/preview links, no signed CDN URLs,
  no private artifact URLs. Quick tunnels die on restart — long-lived review pages go on durable hosting.
  The review server must support byte-range requests (python `http.server` breaks video on mobile Safari).
- Attachments: ~40 MB API caps include base64 overhead — send a link for anything ~30 MB+.
- Public share pages carry no internal notes or pricing; re-verify after every deploy.
- Log every hour and every credit per client in the same session (the log is the invoice). Never
  fabricate hours; never claim the owner approved something he didn't; never oversell ("a simplified
  version of the style; the full effect is possible with more time").

## What FAILED
- Generating presenter clips before the shot map existed: ~300 credits "wasted".
- Polishing a weak concept with more passes instead of replacing the concept.
- Synthesised music beds (rejected twice) → licensed real tracks with attribution.
- Screenshots in device mockups → live embeds of the real site; the "before" device = a fresh capture.
- Ken Burns on a still for an end card ("dead water", stepping type) → moving plate + static type.
- Full-frame lip-sync on a wide shot (noise everywhere) → mouth-only composite on a tight crop.
- Sequential find/replace on animation timings → broke dependent keyframes; retime line by line.
- Numbers/currency read by TTS from digits → always pass the spoken form ("eight hundred ninety-five").
- Flat delivery folders after ~10 rounds → the client couldn't tell versions apart.
