#!/usr/bin/env python3
"""Find where a clean song (or clean scene audio) sits inside a reference edit's mix, sample-accurately.

  align_audio.py coarse --ref edit.mp4 --src song.m4a [--at 13.3 16.5 7.5] [--len 3] [--speeds 0.90:1.36:0.01]
      8 kHz NCC search per ref window over a speed sweep -> song time + speed (editors often speed songs up).
  align_audio.py fine --ref edit.mp4 --src song.m4a --offset 14.326 --a 13.2 --b 20.4 [--radius 0.005]
      44.1 kHz refine around a coarse offset: prints offset_samples (src_sample = ref_sample + offset).
  align_audio.py series --ref edit.mp4 --src song.m4a --offset 14.326 --from 13.2 --to 19.2
      1 s windows: per-window offset + NCC + linear fit -> speed ratio. A step in the series = an edit/splice.
Needs ffmpeg, numpy, scipy.
"""
import argparse, subprocess, numpy as np
from scipy.signal import fftconvolve

def load(f, sr):
    return np.frombuffer(subprocess.run(['ffmpeg', '-v', 'error', '-i', f, '-ac', '1', '-ar', str(sr), '-f', 'f32le', '-'],
                                        capture_output=True, check=True).stdout, np.float32).astype(np.float64)

def ncc_search(chunk, song):
    c = chunk - chunk.mean(); num = fftconvolve(song, c[::-1], 'valid')
    e = np.sqrt(fftconvolve(song ** 2, np.ones(len(c)), 'valid')) * np.linalg.norm(c) + 1e-9
    r = num / e; i = int(np.argmax(r)); return float(r[i]), i

def refine(ref, song, sr, offset, a, b, radius):
    x = ref[round(a * sr):round(b * sr)]; lo = max(0, round((a + offset - radius) * sr)); y = song[lo:round((b + offset + radius) * sr)]
    r, i = ncc_search(x, y); return lo + i - round(a * sr), r

if __name__ == '__main__':
    ap = argparse.ArgumentParser(); ap.add_argument('mode', choices=['coarse', 'fine', 'series'])
    ap.add_argument('--ref', required=True); ap.add_argument('--src', required=True)
    ap.add_argument('--at', type=float, nargs='+', default=[0.5]); ap.add_argument('--len', type=float, default=3.0)
    ap.add_argument('--speeds', default='0.90:1.36:0.01'); ap.add_argument('--offset', type=float)
    ap.add_argument('--a', type=float); ap.add_argument('--b', type=float); ap.add_argument('--radius', type=float, default=.005)
    ap.add_argument('--from', dest='t0', type=float); ap.add_argument('--to', dest='t1', type=float)
    a = ap.parse_args()
    if a.mode == 'coarse':
        SR = 8000; ref, song = load(a.ref, SR), load(a.src, SR); lo, hi, st = map(float, a.speeds.split(':'))
        for t in a.at:
            ch = ref[int(t * SR):int((t + a.len) * SR)]; best = (-1, 1, 0)
            for sp in np.arange(lo, hi, st):     # ref played at speed sp -> resample the chunk back to song speed
                n = int(len(ch) * sp); r, i = ncc_search(np.interp(np.linspace(0, len(ch) - 1, n), np.arange(len(ch)), ch), song)
                best = max(best, (r, sp, i / SR))
            print(f'ref@{t:6.2f}s  ncc={best[0]:.3f} speed={best[1]:.2f} src_t={best[2]:8.3f}s  offset={best[2] - t:.3f}s')
    else:
        SR = 44100; ref, song = load(a.ref, SR), load(a.src, SR)
        if a.mode == 'fine':
            o, r = refine(ref, song, SR, a.offset, a.a, a.b, a.radius); print(f'offset_samples={o} offset_s={o / SR:.6f} ncc={r:.3f}')
        else:
            rows = []
            for t in np.arange(a.t0, a.t1 + 1e-6, 1.0):
                o, r = refine(ref, song, SR, a.offset, t, t + 1, a.radius); rows.append((t, o, r)); print(f'{t:6.2f}s offset={o} ncc={r:.3f}')
            good = [(t, o) for t, o, r in rows if r > .5]
            if len(good) > 1:
                k = np.polyfit([t for t, _ in good], [o / SR for _, o in good], 1)[0]
                print(f'speed ratio ≈ {1 + k:.5f}  offset spread {max(o for _, o in good) - min(o for _, o in good)} samples')
