---
name: performance-voice-conversion
description: Use when a consenting person's voice must deliver a line the way an actor originally performed it (dubbing a famous scene, replacing a name in a line, re-voicing a character), when TTS/voice clones sound flat or read the line wrong, or when a line must sound like it comes through a phone or radio.
---

# Performance voice conversion

## Overview
TTS invents a performance; the original actor already gave the right one. **Convert the actor's own
performance into the target voice** (Seed-VC, zero-shot, on a GPU), generate only the NEW words with a
native-accent TTS and convert those too, then re-time every word to the actor's timings and energy.

**Consent rule (hard):** only convert INTO a voice whose owner agreed. Never clone or convert into a
non-consenting person's voice (co-stars, callers, public figures). If a co-star's line mentions the old
name, keep his real audio and fix it on screen (subtitle strike-through) instead.

## When to use / not
- Use: "make him say the line like the character does", name swaps inside a famous line, phone VO.
- For clean studio VO clones of a consenting speaker (Fish Audio training, fuzz, gap hash, run-up trick),
  use the Fish cloning runbook in your memory/notes; this skill covers performance transfer.
- Picture lip-sync to the new audio → `lip-sync-and-gaze-qc`.

## Pipeline
1. **Stems.** Isolate the actor's line from the clean scene audio (stem separation / the scene's
   dialogue-only moments). Word-timestamp it (Deepgram or whisper word timestamps) → `theirs` timings.
2. **Target reference.** 10–30 s of the target speaker, clean, single speaker (DeepFilterNet it if noisy).
3. **Convert the performance** (Seed-VC on the GPU box, see `remote-gpu-render`):
   ```bash
   python inference.py --source actor_line.wav --target target_ref.wav --output vc/ \
     --diffusion-steps 50 --length-adjust 1.0 --inference-cfg-rate 0.7
   ```
   Speech model loads `bigvgan_v2_22khz_80band_256x`; RTF ≈1.7 on an RTX 3080, ~10 s/step on CPU (don't).
4. **New words** (the person's name etc.): generate with a NATIVE-accent TTS voice in the scene's
   language/dialect (e.g. a Colombian Spanish voice, not an American one reading Spanish), then run
   the same Seed-VC conversion into the target voice. Generate each sentence separately so endings fall.
5. **Word warp** — map each new word onto the syllables it replaces and match duration + energy:
   ```bash
   python scripts/voice_tools.py warp --in vc/new_phrase.wav --ref actor_scene.wav \
     --ours 0,.28 .28,.76 .76,1.08 1.08,1.32 1.32,1.88 \
     --theirs 4.52,4.80 4.80,5.04 5.04,5.40 5.40,5.76 5.76,6.40 --out phrase_warped.wav
   ```
   (rubberband `formant=preserved`, gain toward the actor's per-word energy, capped 0.5–2×, 8 ms joins.)
6. **Attitude edits**: hold drawn-out words (`stretch --tempo 0.72`), keep a plosive's burst crisp and
   add spit (`spit --burst 0.09 --tempo 0.74`, +1.8–7 kHz on the burst).
7. **Phone/radio line**: don't guess a band-pass — MEASURE the show's own phone sound. Welch PSD of the
   actor's phone line ÷ his clean line → FIR (1025 taps), + tanh saturation + 300–3400 Hz noise at −26 dB:
   `voice_tools.py phone --phone actor_phone.wav --clean actor_clean.wav --in line.wav --out line_phone.wav`.
   Apply only while the speaker is off-screen; clean once we cut to him.
8. **Place + mix**: `voice_tools.py place --dur 20.6 --out stem.wav a.wav@3.44 b.wav@7.40`; level = the
   reference mix's dialogue RMS minus the music (residual), then two-pass loudnorm to the ref's LUFS.
9. **QC**: transcribe the placed stem (expected words, onsets within 60 ms of the picture); A/B against
   the actor's line; plot both waveforms side by side at full scale and ×12.

## What FAILED
| Tried | Result |
|---|---|
| Fish TTS clone of the target reading the line (v1) | Right voice, but not the actor's delivery — replaced |
| WORLD vocoder stretch + 2-semitone pitch-down of the TTS take (`pyworld`, v2) | Still a TTS performance, just slower; stretching whole phrases smears consonants — replaced by Seed-VC |
| Generic 300–3200 Hz band-pass + bitcrush as "phone" | A filter, not the show's phone — replaced by the measured curve |
| TTS voice with the wrong accent for the new words | Stood out immediately next to converted native speech |
| Converting a co-star's line into the target voice | Not allowed without that co-star's consent — use a subtitle strike instead |

## Quick reference
- Word timings: `theirs` from the actor, `ours` from the converted TTS; same word count.
- Stretch only within ±30 %; beyond that re-generate the TTS slower/faster.
- Keep crossfades ≤10 ms at word joins; 12 ms fade-in / 30 ms fade-out on phrases.
- Deliver the voice stem separately with the mix so the editor can ride it.
