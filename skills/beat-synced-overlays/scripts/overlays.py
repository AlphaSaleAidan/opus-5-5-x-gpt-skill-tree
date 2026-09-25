#!/usr/bin/env python3
"""Beat-synced overlay pass for a montage rendered as PNG frames (00000.png ...).

Scores every cut by kick energy (45-140 Hz band-pass, Hilbert envelope) right at/after the cut, picks
the strongest few with a spacing guard, and writes ONLY the changed frames to --out (a separate pass:
your renderer prefers out/NNNNN.png over the base frame when it exists):
  flash      2-frame amber-white flash on the heaviest kicks (0.88 then 0.30 — commit, don't half-blend)
  double     4-frame double exposure: frozen outgoing frame screen-blended over the incoming (scale 1.00->1.04)
  ghost      a static close-up screened at 30 % over a whole target shot (content-picked pairs)

usage: overlays.py --frames comp/ --out overlay/ --audio final_mix.wav --cuts 395:790:11 [--fps 30]
                   [--flash 3] [--double 4] [--min-gap 22] [--keep-clean 395] [--ghost 411:494 619:713]
--cuts: explicit frame list "395,406,417" or start:end:step. --ghost SRC:TARGET_START (TARGET shot = --shot-len frames).
Re-runs are idempotent (always reads the base frames). Writes out/PLAN.md listing every effect.
"""
import argparse, os
import numpy as np
from PIL import Image
from scipy.io import wavfile
from scipy.signal import butter, sosfiltfilt, hilbert

ap = argparse.ArgumentParser()
ap.add_argument('--frames', required=True); ap.add_argument('--out', required=True); ap.add_argument('--audio', required=True)
ap.add_argument('--cuts', required=True); ap.add_argument('--fps', type=float, default=30.0)
ap.add_argument('--flash', type=int, default=3); ap.add_argument('--double', type=int, default=4)
ap.add_argument('--min-gap', type=int, default=22, help='min frames between chosen moments ("not every cut")')
ap.add_argument('--keep-clean', type=int, nargs='*', default=[], help='cut frames that must stay untouched')
ap.add_argument('--ghost', nargs='*', default=[], help='SRC_FRAME:TARGET_START pairs')
ap.add_argument('--shot-len', type=int, default=11); ap.add_argument('--ghost-opacity', type=float, default=.30)
a = ap.parse_args(); os.makedirs(a.out, exist_ok=True)

def load(f): return np.asarray(Image.open(f'{a.frames}/{f:05d}.png').convert('RGB'), np.float32) / 255.
def save(f, x): Image.fromarray((np.clip(x, 0, 1) * 255).astype(np.uint8)).save(f'{a.out}/{f:05d}.png')
def screen(base, top): return 1 - (1 - base) * (1 - top)          # black stays black -> the grade's blacks survive
def zoom(img, s):
    if s <= 1: return img
    h, w = img.shape[:2]; im = Image.fromarray((img * 255).astype(np.uint8)).resize((int(w * s), int(h * s)), Image.LANCZOS)
    l, t = (im.width - w) // 2, (im.height - h) // 2
    return np.asarray(im.crop((l, t, l + w, t + h)), np.float32) / 255.

sr, data = wavfile.read(a.audio)
mono = (data.mean(axis=1) if data.ndim > 1 else data).astype(np.float64)
env = np.abs(hilbert(sosfiltfilt(butter(4, [45, 140], btype='band', fs=sr, output='sos'), mono)))
env = np.convolve(env, np.ones(max(1, int(sr * .005))) / max(1, int(sr * .005)), 'same')
def kick(frame):
    t = frame / a.fps; i0, i1 = max(0, int((t - .04) * sr)), min(len(env), int((t + .12) * sr))
    return float(env[i0:i1].max()) if i1 > i0 else 0.

if ':' in a.cuts: s0, s1, st = map(int, a.cuts.split(':')); cuts = list(range(s0, s1 + 1, st))
else: cuts = [int(c) for c in a.cuts.split(',')]
ghosts = [tuple(map(int, g.split(':'))) for g in a.ghost]
reserved = [(t, t + a.shot_len - 1) for _, t in ghosts]
cand = [f for f in cuts if f not in a.keep_clean and not any(r0 - a.shot_len <= f <= r1 + a.shot_len for r0, r1 in reserved)]
chosen = []
for f in sorted(cand, key=lambda f: -kick(f)):
    if all(abs(f - c) >= a.min_gap for c in chosen): chosen.append(f)
    if len(chosen) >= a.flash + a.double: break
flashes, doubles = chosen[:a.flash], chosen[a.flash:]
plan = ['# Overlay pass plan', f'kick score: 45-140 Hz envelope of {a.audio}', '']

for src, t0 in ghosts:
    g = zoom(load(src), 1.12) * a.ghost_opacity                     # pre-multiplied ghost
    for f in range(t0, t0 + a.shot_len): save(f, screen(load(f), g))
    plan.append(f'- GHOST frames {t0}-{t0 + a.shot_len - 1} from frame {src}, {a.ghost_opacity:.0%} screen')
FLASH = np.array([255, 228, 195], np.float32) / 255.
for f in sorted(flashes):
    for i, al in enumerate([.88, .30]): save(f + i, load(f + i) * (1 - al) + FLASH * al)
    plan.append(f'- FLASH frames {f}-{f + 1} kick={kick(f):.3f}')
for f in sorted(doubles):
    out = load(f - 1)
    for i in range(4):
        t = i / 3; save(f + i, screen(zoom(load(f + i), 1 + .04 * t), out * (1 - t) * .55))
    plan.append(f'- DOUBLE EXPOSURE frames {f}-{f + 3} from outgoing {f - 1}, kick={kick(f):.3f}')
open(f'{a.out}/PLAN.md', 'w').write('\n'.join(plan) + '\n')
print('\n'.join(plan))
