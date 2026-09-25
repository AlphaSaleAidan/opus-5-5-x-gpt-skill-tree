---
name: edit-rebuild-from-clean-sources
description: Use when remaking or upgrading a social-media fan edit (TikTok/Reels/Shorts) from its original clean sources — matching the editor's cut, frame cadence, grade and music timing exactly — or when a rebuilt clip drifts out of sync with the music, jitters like camera shake, or looks choppy after a frame-rate change.
---

# Edit rebuild from clean sources

## Overview
A viral edit is a low-bitrate copy of clean material. Rebuild it from the clean film + clean songs,
reproducing every editorial decision **by measurement**: where each song sits (to the sample), how each
output frame maps to source frames (dup / blend / motion-interpolated), and the grade per section.
Never build from the edit's own split audio.

## Pipeline
1. **Probe the reference.** `ffprobe` fps per section (outros are often a different rate), loudness
   (`loudnorm print_format=json`: I, LRA, TP), cut list (scene score + frame diff), subtitle boxes.
   Check whether a montage cycle repeats frame-identically (per-shot SSIM ≥ 0.99 → reuse).
2. **Identify songs.** TikTok metadata first (`yt-dlp -J <url>` → `track`, `artists`, `album`; library
   sounds are named there), then Shazam-style fingerprinting on 5 s music-only windows. Get the clean
   track (bought file or official upload). The attached TikTok library sound (`yt-dlp -f audio`) is
   clean only if it has NO dialogue in it — listen.
3. **Place songs sample-accurately** (`scripts/align_audio.py`):
   ```bash
   python scripts/align_audio.py coarse --ref ref.mp4 --src song.m4a --at 13.3 16.5 --len 3
   python scripts/align_audio.py fine   --ref ref.mp4 --src song.m4a --offset 14.326 --a 13.2 --b 20.4
   python scripts/align_audio.py series --ref ref.mp4 --src song.m4a --offset 14.326 --from 13.2 --to 19.2
   ```
   Coarse sweeps speed 0.90–1.36 (edits often speed songs up); `series` fits speed ratio and exposes
   splices as offset steps. Then **re-measure the lag on the decoded AAC you actually mix**: AAC encoder
   priming shifted our songs by **+334…341 samples** (~7.6 ms) — cross-correlate a music-only window of the
   final decode against the ref and shift by the peak, every time.
4. **Levels.** Gain per stem = RMS(ref window where that stem dominates) / RMS(stem). Dialogue gain =
   residual after subtracting the fitted music. Reproduce ducks and tail envelopes from 20 ms
   least-squares windows. Finish with two-pass `loudnorm` to the ref's I/LRA/TP.
5. **Cadence map.** For each edit frame find the source frame by SSIM (source scaled to edit size, ECC
   for framing): exact dup, two-frame blend (α by least squares), or flow. Reproduce with
   `fps=30` (dups), `minterpolate=fps=30:mi_mode=blend` (blends), `mi_mode=mci` (motion-interpolated).
6. **Framing matrices — smooth them.** Per-frame ECC/affine alignment jitters by a pixel or two; at full
   clean-source sharpness it reads as **camera shake**. Smooth within each shot, never across cuts:
   ```python
   from scipy.ndimage import uniform_filter1d
   for a, b in shots:  # frame ranges between cuts
       M[a:b] = uniform_filter1d(M[a:b], size=min(15, b - a), axis=0, mode='nearest')
   ```
7. **Grade per section.** Paired frames (≈30/section) → input curves + 3×3 matrix + offset + output
   curves (or a .cube). Verify with `signalstats` on 10 matched frames: YAVG ±3, YMIN/YMAX ±5, SATAVG ±1,
   HUEAVG ±3. Reproduce exposure dips through dissolves by matching per-frame mean luma.
8. **Upgrade, don't degrade.** Once matched at the edit's size, re-conform from the clean source at
   1080p with the same maps and grade, WITHOUT the blur you added to match the TikTok.
9. **Captions.** Re-set subtitles clean (measure line boxes; free stand-in fonts if the original is
   proprietary) and verify by 50 % overlay on the ref frame; check legibility at phone size.

## Quick reference
| Symptom | Cause | Fix |
|---|---|---|
| Music flams / phasey against the ref | AAC priming / resample offset | re-xcorr the decoded file; shift by peak |
| Clean rebuild shakes | per-frame alignment jitter | smooth matrices per shot |
| Choppy after 24→30 | plain frame dup where the editor blended | `minterpolate` blend/mci per the cadence map |
| Grade "close but off" | one global LUT | per-section models, verify with signalstats |
| Random-seek thumbnails wrong | OpenCV seeking on long-GOP files | decode sequentially |

## What FAILED
- Building from the TikTok's own audio (split stems): muddy, and the client ruled it out outright.
- Trusting a fingerprint ID: the service named a bed song that cross-correlation later had to confirm;
  correlation (NCC ≥ 0.8 with dialogue present, ≥ 0.9 music-only) is the arbiter.
- Declaring a splice point from the "best sharp switch" fit: often not unique; say "unresolved".
- Random seeks (`CAP_PROP_POS_MSEC`) for storyboard frames: wrong frames on long-GOP H.264.

## Status
`align_audio.py` is generalized from the job's working xcorr/refine scripts; **untested as written**.
