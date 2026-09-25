#!/usr/bin/env python3
"""Measure picture/voice lag: mouth aperture (mediapipe lm 13/14, normalised by face height 10/152) vs voice RMS.

usage: lip_lag.py --video clip.mp4 --model face_landmarker.task [--audio voice.wav] [--fps 30] [--max-lag 20]
Prints the lag in frames. POSITIVE = mouth moves BEFORE the voice -> delay the picture by that many frames
(e.g. composite_person.py --lag N). Negative = mouth late -> delay the audio instead.
"""
import argparse, subprocess, numpy as np, cv2, mediapipe as mp
from mediapipe.tasks.python import vision, BaseOptions

ap = argparse.ArgumentParser(); ap.add_argument('--video', required=True); ap.add_argument('--model', required=True)
ap.add_argument('--audio'); ap.add_argument('--fps', type=float, default=30); ap.add_argument('--max-lag', type=int, default=20)
a = ap.parse_args()

raw = subprocess.run(['ffmpeg', '-v', 'error', '-i', a.video, '-vf', f'fps={a.fps},scale=640:-2', '-pix_fmt', 'rgb24', '-f', 'rawvideo', '-'],
                     capture_output=True, check=True).stdout
w, h = map(int, subprocess.run(['ffprobe', '-v', 'error', '-select_streams', 'v:0', '-show_entries', 'stream=width,height', '-of', 'csv=p=0', a.video],
                               capture_output=True, text=True).stdout.strip().split(',')[:2])
H = int(round(h * 640 / w / 2) * 2); fr = np.frombuffer(raw, np.uint8).reshape(-1, H, 640, 3)
det = vision.FaceLandmarker.create_from_options(vision.FaceLandmarkerOptions(base_options=BaseOptions(model_asset_path=a.model), num_faces=1))
mouth = []
for f in fr:
    r = det.detect(mp.Image(image_format=mp.ImageFormat.SRGB, data=np.ascontiguousarray(f)))
    if not r.face_landmarks: mouth.append(np.nan); continue
    L = r.face_landmarks[0]; d = lambda i, j: np.hypot(L[i].x - L[j].x, L[i].y - L[j].y)
    mouth.append(d(13, 14) / (d(10, 152) + 1e-6))
mouth = np.array(mouth); ok = ~np.isnan(mouth); mouth[~ok] = np.interp(np.flatnonzero(~ok), np.flatnonzero(ok), mouth[ok]) if ok.any() else 0

SR = 16000
au = np.frombuffer(subprocess.run(['ffmpeg', '-v', 'error', '-i', a.audio or a.video, '-ac', '1', '-ar', str(SR), '-f', 'f32le', '-'],
                                  capture_output=True, check=True).stdout, np.float32)
hop = SR / a.fps; n = min(len(mouth), int(len(au) / hop))
rms = np.array([np.sqrt(np.mean(au[int(i * hop):int((i + 1) * hop)] ** 2) + 1e-12) for i in range(n)])
m, v = mouth[:n], np.log(rms)                     # log-RMS: speech onsets, not loud peaks, drive the match
m, v = (m - m.mean()) / (m.std() + 1e-9), (v - v.mean()) / (v.std() + 1e-9)
best = max(range(-a.max_lag, a.max_lag + 1), key=lambda k: np.mean(m[max(0, -k):n - max(0, k)] * v[max(0, k):n - max(0, -k)]))
corr = np.mean(m[max(0, -best):n - max(0, best)] * v[max(0, best):n - max(0, -best)])
print(f'frames={n} lag={best} corr={corr:.3f}  ->', 'delay picture' if best > 0 else 'delay audio' if best < 0 else 'in sync', abs(best), 'frames')
if corr < .2: print('WARN low correlation: check the face tracked / the right voice track; do not trust the lag blindly')
