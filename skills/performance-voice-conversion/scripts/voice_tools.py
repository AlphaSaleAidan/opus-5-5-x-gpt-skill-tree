#!/usr/bin/env python3
"""Post tools for re-performed lines: per-word time-warp + energy match to a reference performance,
measured phone/radio EQ, and placement on a timeline. Mono float WAV in/out. Needs ffmpeg (with
librubberband) on PATH, numpy, scipy.

  voice_tools.py warp  --in ours.wav --ours 0,.28 .28,.76 ... --theirs 4.52,4.80 4.80,5.04 ... --ref ref.wav --out warped.wav
      each of OUR words (start,end s) is rubberband-stretched to THEIR word's duration and gained toward
      their per-word energy (which words hit hardest), then joined with 8 ms crossfades.
  voice_tools.py phone --phone ref_phone.wav --clean ref_clean.wav --in line.wav --out line_phone.wav
      builds an FIR from welch(phone)/welch(clean) of the SAME speaker, applies it + mild saturation + band noise.
  voice_tools.py stretch --in x.wav --tempo 0.72 --out y.wav            (tempo<1 = longer; formants kept)
  voice_tools.py spit --in puta.wav --burst 0.09 --tempo 0.74 --out y.wav
      keep the first `burst` s (the plosive) crisp + boost 1.8-7 kHz, hold the rest (tempo<1).
  voice_tools.py place --dur 20.6 --out stem.wav a.wav@3.44 b.wav@7.40 ...
"""
import argparse, subprocess, numpy as np
from scipy.io import wavfile
from scipy.signal import welch, firwin2, lfilter, butter, sosfilt
SR = 44100

def load(f):
    raw = subprocess.run(['ffmpeg', '-v', 'error', '-i', f, '-ac', '1', '-ar', str(SR), '-f', 'f32le', '-'], capture_output=True, check=True).stdout
    return np.frombuffer(raw, np.float32).astype(np.float64)
def save(f, x): wavfile.write(f, SR, (x / (np.abs(x).max() + 1e-9) * 0.9).astype(np.float32))
def rms(x): return float(np.sqrt(np.mean(x ** 2) + 1e-12))
def fade(x, a=.012, b=.03):
    x = x.copy(); ka, kb = int(a * SR), int(b * SR); x[:ka] *= np.linspace(0, 1, ka); x[-kb:] *= np.linspace(1, 0, kb); return x
def stretch(x, tempo):
    """rubberband via ffmpeg: tempo 0.72 = 1/0.72 longer. formant=preserved keeps the timbre."""
    if abs(tempo - 1) < 1e-3: return x
    out = subprocess.run(['ffmpeg', '-v', 'error', '-f', 'f64le', '-ar', str(SR), '-ac', '1', '-i', '-', '-af',
                          f'rubberband=tempo={tempo}:formant=preserved:transients=crisp', '-f', 'f64le', '-'],
                         input=x.astype(np.float64).tobytes(), capture_output=True, check=True).stdout
    return np.frombuffer(out, np.float64).copy()
def pairs(v): return [tuple(map(float, p.split(','))) for p in v]

def warp(x, ours, theirs, ref):
    assert len(ours) == len(theirs), 'same number of words on both sides'
    e_ref = [rms(ref[int(a * SR):int(b * SR)]) for a, b in theirs]; e_our = [rms(x[int(a * SR):int(b * SR)]) for a, b in ours]
    mr, mo = np.mean(e_ref), np.mean(e_our); parts = []
    for (a, b), (c, d), er, eo in zip(ours, theirs, e_ref, e_our):
        seg = stretch(x[int(a * SR):int(b * SR)], (b - a) / max(d - c, 1e-3))
        parts.append(seg * np.clip((er / mr) / (eo / mo + 1e-9), .5, 2.) ** .8)   # capped, softened energy match
    k, out = int(.008 * SR), parts[0]
    for q in parts[1:]:
        out = np.concatenate([out[:-k], out[-k:] * np.linspace(1, 0, k) + q[:k] * np.linspace(0, 1, k), q[k:]]) if min(len(out), len(q)) > k else np.concatenate([out, q])
    return fade(out)

def phone(x, ph, cl):
    f, pp = welch(ph, SR, nperseg=4096); _, pc = welch(cl, SR, nperseg=4096)
    g = np.convolve(np.sqrt(pp / (pc + 1e-18)), np.ones(9) / 9, 'same'); g /= g[(f > 800) & (f < 2000)].mean()
    taps = firwin2(1025, np.r_[0, f[1:-1], SR / 2] / (SR / 2), np.clip(np.r_[g[0], g[1:-1], g[-1]], .02, 3.))
    y = lfilter(taps, 1, x); r = rms(y) * 3.2; y = np.tanh(y / r) * r                       # gritty but not clipped
    noise = sosfilt(butter(2, [300, 3400], btype='band', fs=SR, output='sos'), np.random.randn(len(y))) * rms(y) * .05
    return fade(y + noise)

def spit(x, burst, tempo):
    k = int(burst * SR); on, rest = x[:k], stretch(x[k:], tempo)
    on = on + sosfilt(butter(4, [1800, 7000], btype='band', fs=SR, output='sos'), on) * 2.2
    return fade(np.concatenate([on, rest]))

if __name__ == '__main__':
    ap = argparse.ArgumentParser(); sp = ap.add_subparsers(dest='cmd', required=True)
    w = sp.add_parser('warp'); w.add_argument('--in', dest='inp', required=True); w.add_argument('--ref', required=True)
    w.add_argument('--ours', nargs='+', required=True); w.add_argument('--theirs', nargs='+', required=True); w.add_argument('--out', required=True)
    p = sp.add_parser('phone'); p.add_argument('--phone', required=True); p.add_argument('--clean', required=True)
    p.add_argument('--in', dest='inp', required=True); p.add_argument('--out', required=True)
    s = sp.add_parser('stretch'); s.add_argument('--in', dest='inp', required=True); s.add_argument('--tempo', type=float, required=True); s.add_argument('--out', required=True)
    t = sp.add_parser('spit'); t.add_argument('--in', dest='inp', required=True); t.add_argument('--burst', type=float, default=.09)
    t.add_argument('--tempo', type=float, default=.74); t.add_argument('--out', required=True)
    pl = sp.add_parser('place'); pl.add_argument('--dur', type=float, required=True); pl.add_argument('--out', required=True); pl.add_argument('items', nargs='+')
    a = ap.parse_args()
    if a.cmd == 'warp': save(a.out, warp(load(a.inp), pairs(a.ours), pairs(a.theirs), load(a.ref)))
    elif a.cmd == 'phone': save(a.out, phone(load(a.inp), load(a.phone), load(a.clean)))
    elif a.cmd == 'stretch': save(a.out, stretch(load(a.inp), a.tempo))
    elif a.cmd == 'spit': save(a.out, spit(load(a.inp), a.burst, a.tempo))
    elif a.cmd == 'place':
        out = np.zeros(int(a.dur * SR))
        for it in a.items:
            f, at = it.rsplit('@', 1); x = load(f); s = int(float(at) * SR); out[s:s + len(x)] += x[:len(out) - s]
        save(a.out, out)
    print('wrote', a.out)
