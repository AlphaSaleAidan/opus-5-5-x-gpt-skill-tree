#!/usr/bin/env python3
"""Per-frame gaze + head-yaw for a clip, and the best window where eyes look into the lens and the head
angle matches a target (e.g. the original actor's yaw measured with --image on his frame).

  gaze.py --video clip.mp4 --model face_landmarker.task --window 11 [--target-yaw 0.0] [--csv out.csv]
  gaze.py --image actor_frame.jpg --model face_landmarker.task          (measure the target)
gx: iris offset inside the eye, -1 = image-left .. +1 = image-right (0 = looking at the lens)
gy: -1 up .. +1 down; yaw: nose vs face centre (0 = frontal). Largest face wins (--pick-x to choose one).
"""
import argparse, subprocess, numpy as np, cv2, mediapipe as mp
from mediapipe.tasks.python import vision, BaseOptions
EYES = [(33, 133, 159, 145, 468), (263, 362, 386, 374, 473)]    # outer, inner, top, bottom, iris centre

def gaze(det, rgb, pick_x=None):
    r = det.detect(mp.Image(image_format=mp.ImageFormat.SRGB, data=np.ascontiguousarray(rgb)))
    if not r.face_landmarks: return None
    fs = sorted(r.face_landmarks, key=(lambda L: abs(np.mean([p.x for p in L]) - pick_x)) if pick_x is not None
                else (lambda L: -(max(p.x for p in L) - min(p.x for p in L))))
    P = np.array([[p.x, p.y] for p in fs[0]]); gx, gy = [], []
    for o, i, t, b, c in EYES:
        mid = (P[o] + P[i]) / 2; half = np.linalg.norm(P[i] - P[o]) / 2
        gx.append((P[c][0] - mid[0]) / half); gy.append((P[c][1] - (P[t][1] + P[b][1]) / 2) / (abs(P[b][1] - P[t][1]) + 1e-6))
    yaw = (P[1][0] - (P[234][0] + P[454][0]) / 2) / (abs(P[454][0] - P[234][0]) + 1e-6)
    return float(np.mean(gx)), float(np.mean(gy)), float(yaw)

if __name__ == '__main__':
    ap = argparse.ArgumentParser(); ap.add_argument('--video'); ap.add_argument('--image'); ap.add_argument('--model', required=True)
    ap.add_argument('--window', type=int, default=11); ap.add_argument('--target-yaw', type=float, default=0.0)
    ap.add_argument('--pick-x', type=float); ap.add_argument('--fps', type=float, default=30); ap.add_argument('--csv')
    a = ap.parse_args()
    det = vision.FaceLandmarker.create_from_options(vision.FaceLandmarkerOptions(base_options=BaseOptions(model_asset_path=a.model), num_faces=4))
    if a.image:
        print('gx gy yaw =', gaze(det, cv2.cvtColor(cv2.imread(a.image), cv2.COLOR_BGR2RGB), a.pick_x)); raise SystemExit
    raw = subprocess.run(['ffmpeg', '-v', 'error', '-i', a.video, '-vf', f'fps={a.fps},scale=960:540', '-pix_fmt', 'rgb24', '-f', 'rawvideo', '-'],
                         capture_output=True, check=True).stdout
    fr = np.frombuffer(raw, np.uint8).reshape(-1, 540, 960, 3)      # ponytail: assumes 16:9 source; aspect only skews yaw slightly
    rows = [gaze(det, f, a.pick_x) for f in fr]
    if a.csv:
        with open(a.csv, 'w') as fh:
            fh.write('frame,gx,gy,yaw\n'); [fh.write(f'{i},' + (','.join(f'{v:.3f}' for v in r) if r else ',,') + '\n') for i, r in enumerate(rows)]
    cost = np.array([abs(r[0]) + .5 * abs(r[1]) + abs(r[2] - a.target_yaw) if r else 9 for r in rows])
    win = np.convolve(cost, np.ones(a.window) / a.window, 'valid')
    order = np.argsort(win)
    best = int(order[0]); second = next((int(k) for k in order if abs(k - best) >= a.window), None)
    print(f'frames={len(rows)} best window start={best} cost={win[best]:.3f}' + (f' | second={second} cost={win[second]:.3f}' if second is not None else ''))
