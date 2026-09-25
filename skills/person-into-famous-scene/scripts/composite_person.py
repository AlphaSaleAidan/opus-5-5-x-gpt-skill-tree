#!/usr/bin/env python3
"""Composite a generated clip of a person over an edit's own plates, replacing the original actor.

Per frame: find the original actor (face embedding vs --actor-face), mask ONLY him (person seg ∩ a column
around his face, so crew/bystanders stay), LaMa-inpaint him out (or use --clean-plate), fit the generated
person to his face (scale by face height, translate by eye centre), RVM matte, LAB grade to his region,
then match softness (Laplacian variance) and grain to the plate. --fullframe skips the comp and just grades
the generated clip to the plate (use for dark/plain-background shots).

usage:
  composite_person.py --plates shot.mp4 --gen person.mp4 --actor-face actor.jpg --out frames/ \
      --lama lama_fp32.onnx --rvm rvm_mobilenetv3_fp32.onnx [--gen-start 40] [--lag 0] [--fullframe]
      [--clean-plate plate.png] [--size 1920x1080] [--fps 30]
Writes PNG frames 00000.png... (one per plate frame).
Deps: opencv-python, numpy, onnxruntime, insightface, rembg, pillow, ffmpeg on PATH.
"""
import argparse, os, subprocess, cv2, numpy as np, onnxruntime as ort

ap = argparse.ArgumentParser()
ap.add_argument('--plates', required=True); ap.add_argument('--gen', required=True)
ap.add_argument('--actor-face', required=True, help='still of the ORIGINAL actor, to pick him among faces')
ap.add_argument('--out', required=True); ap.add_argument('--lama', required=True); ap.add_argument('--rvm', required=True)
ap.add_argument('--gen-start', type=int, default=0, help='first frame of the generated clip to use (gaze window)')
ap.add_argument('--lag', type=int, default=0, help='delay picture N frames vs voice (eased in over 1 s, never a freeze)')
ap.add_argument('--fullframe', action='store_true'); ap.add_argument('--clean-plate')
ap.add_argument('--size', default='1920x1080'); ap.add_argument('--fps', type=float, default=30)
ap.add_argument('--grain-gain', type=float, default=1.2)
a = ap.parse_args(); os.makedirs(a.out, exist_ok=True)
W, H = map(int, a.size.split('x'))

def read(path, vf=''):
    raw = subprocess.run(['ffmpeg', '-v', 'error', '-i', path, '-vf', f'fps={a.fps},scale={W}:{H}:flags=lanczos' + vf,
                          '-pix_fmt', 'bgr24', '-f', 'rawvideo', '-'], capture_output=True, check=True).stdout
    return np.frombuffer(raw, np.uint8).reshape(-1, H, W, 3)

plates, gen = read(a.plates), read(a.gen)
n = len(plates); print('plates', n, 'gen', len(gen))

def lab_match(img, tgt, mask=None, pw=(.6, .9, .9)):
    """Move img's LAB mean/std toward tgt [(mean,std)]x3; luminance only 70 % so the new face keeps some life."""
    lab = cv2.cvtColor(img, cv2.COLOR_BGR2LAB).astype(np.float32); m = mask if mask is not None else np.ones(img.shape[:2], bool)
    for c in range(3):
        mu, sd = lab[..., c][m].mean(), lab[..., c][m].std() + 1e-3
        lab[..., c] = (lab[..., c] - mu) * (tgt[c][1] / sd) ** pw[c] + (tgt[c][0] if c else .7 * tgt[c][0] + .3 * mu)
    return cv2.cvtColor(np.clip(lab, 0, 255).astype(np.uint8), cv2.COLOR_LAB2BGR).astype(np.float32)

def grain_of(gray, mask): return float((gray - cv2.GaussianBlur(gray, (0, 0), 1.0))[mask].std())
def add_grain(img, sigma): return img + cv2.GaussianBlur(np.random.normal(0, 1, img.shape[:2]).astype(np.float32), (0, 0), .7)[..., None] * sigma
def gray(x): return cv2.cvtColor(np.clip(x, 0, 255).astype(np.uint8), cv2.COLOR_BGR2GRAY).astype(np.float32)
def soft_sigma(img, mask, target):
    """Smallest Gaussian sigma that brings the region's Laplacian variance down to the plate's (AI clips are too sharp)."""
    g = gray(img)
    for s in [0.0, 0.4, 0.6, 0.9, 1.2, 1.5, 2.0, 2.6, 3.2]:
        if cv2.Laplacian(g if s == 0 else cv2.GaussianBlur(g, (0, 0), s), cv2.CV_32F)[mask].var() <= target: return s
    return 3.2

def gen_frame(i):
    j = i * (a.fps - a.lag) / a.fps if i < a.fps else i - a.lag      # ease the lag in over the first second
    return gen[min(max(int(round(j)) + a.gen_start, 0), len(gen) - 1)]

if a.fullframe:   # plain/dark background: grade the whole generated frame to the plate, soften, grain
    lp = cv2.cvtColor(plates[0], cv2.COLOR_BGR2LAB).reshape(-1, 3).astype(np.float32)
    tgt = [(lp[:, c].mean(), lp[:, c].std()) for c in range(3)]
    gp = gray(plates[0].astype(np.float32)); gr = grain_of(gp, np.ones_like(gp, bool)); lap = cv2.Laplacian(gp, cv2.CV_32F).var()
    sig = None
    for i in range(n):
        o = lab_match(gen_frame(i), tgt, pw=(.7, .7, .7))
        sig = soft_sigma(o, np.ones(o.shape[:2], bool), lap) if sig is None else sig
        o = cv2.GaussianBlur(o, (0, 0), sig) if sig else o
        cv2.imwrite(f'{a.out}/{i:05d}.png', np.clip(add_grain(o, gr * a.grain_gain), 0, 255).astype(np.uint8))
    raise SystemExit(f'fullframe done {n} frames, softness sigma {sig}')

from insightface.app import FaceAnalysis
from rembg import remove, new_session
from PIL import Image
app = FaceAnalysis(name='buffalo_l', providers=['CPUExecutionProvider']); app.prepare(ctx_id=-1, det_size=(640, 640))
actor = max(app.get(cv2.imread(a.actor_face)), key=lambda f: f.bbox[2] - f.bbox[0]).normed_embedding
seg = new_session('u2net_human_seg')
lama = None if a.clean_plate else ort.InferenceSession(a.lama, providers=['CPUExecutionProvider'])
rvm = ort.InferenceSession(a.rvm, providers=['CPUExecutionProvider'])

def actor_face(img):
    fs = [(float(np.dot(f.normed_embedding, actor)), f) for f in app.get(img)]
    return max(fs, key=lambda t: t[0])[1] if fs and max(t[0] for t in fs) > 0.2 else None

def actor_mask(img, face):
    m = np.array(remove(Image.fromarray(cv2.cvtColor(img, cv2.COLOR_BGR2RGB)), session=seg, only_mask=True)) > 100
    if face is not None:
        _, lab = cv2.connectedComponents(m.astype(np.uint8))
        cx, cy = int((face.bbox[0] + face.bbox[2]) / 2), int((face.bbox[1] + face.bbox[3]) / 2)
        k = lab[min(max(cy, 0), H - 1), min(max(cx, 0), W - 1)]
        if k: m = lab == k
        fw = face.bbox[2] - face.bbox[0]; col = np.zeros_like(m)
        col[max(0, int(face.bbox[1] - 1.2 * fw)):, int(max(0, cx - 1.7 * fw)):int(min(W, cx + 1.7 * fw))] = True
        m &= col                                                    # only the actor; bystanders stay
    return cv2.dilate(m.astype(np.uint8) * 255, np.ones((31, 31), np.uint8))

def inpaint(img, m):
    x = cv2.resize(cv2.cvtColor(img, cv2.COLOR_BGR2RGB), (512, 512)).astype(np.float32) / 255.
    mm = (cv2.resize(m, (512, 512)) > 127).astype(np.float32)
    o = lama.run(None, {'image': x.transpose(2, 0, 1)[None], 'mask': mm[None, None]})[0][0].transpose(1, 2, 0)
    o = o if o.max() > 2 else o * 255
    o = cv2.resize(cv2.cvtColor(np.clip(o, 0, 255).astype(np.uint8), cv2.COLOR_RGB2BGR), (W, H), interpolation=cv2.INTER_CUBIC)
    al = cv2.GaussianBlur(m.astype(np.float32) / 255, (0, 0), 6)[..., None]
    return (o * al + img * (1 - al)).astype(np.uint8)

# fit: median face height ratio + eye-centre translation (actor in plates -> person in generated clip)
pf = [f for f in (actor_face(p) for p in plates[::max(1, n // 8)]) if f is not None]
gf = [max(x, key=lambda f: f.bbox[2] - f.bbox[0]) for x in (app.get(gen_frame(i)) for i in range(0, min(n, 9), 3)) if x]
if pf and gf:
    sc = np.median([f.bbox[3] - f.bbox[1] for f in pf]) / np.median([f.bbox[3] - f.bbox[1] for f in gf])
    tx, ty = np.median([(f.kps[0] + f.kps[1]) / 2 for f in pf], 0) - sc * np.median([(f.kps[0] + f.kps[1]) / 2 for f in gf], 0)
else: sc, tx, ty = 1.0, 0.0, 0.0; print('WARN no faces for fit; identity placement')
if sc < 1: ty = max(ty, H - H * sc)                                # never lift the body off the bottom edge
M = np.float32([[sc, 0, tx], [0, sc, ty]]); print(f'fit scale {sc:.3f} t=({tx:.0f},{ty:.0f})')

f0 = actor_face(plates[0]); m0 = actor_mask(plates[0], f0) > 127
lab0 = cv2.cvtColor(plates[0], cv2.COLOR_BGR2LAB).astype(np.float32)
tgt = [(lab0[..., c][m0].mean(), lab0[..., c][m0].std()) for c in range(3)] if m0.sum() > 500 else None
g0 = gray(plates[0].astype(np.float32)); grain = grain_of(g0, ~m0); lap_t = cv2.Laplacian(g0, cv2.CV_32F)[m0].var() if m0.sum() > 500 else None
clean_plate = cv2.resize(cv2.imread(a.clean_plate), (W, H)) if a.clean_plate else None
rec = [np.zeros((1, 1, 1, 1), np.float32)] * 4; sig = None
for i in range(a.gen_start):                                      # warm RVM's recurrent state before the window
    x = cv2.cvtColor(gen[i], cv2.COLOR_BGR2RGB).astype(np.float32).transpose(2, 0, 1)[None] / 255.
    _, _, *rec = rvm.run(None, {'src': x, 'r1i': rec[0], 'r2i': rec[1], 'r3i': rec[2], 'r4i': rec[3], 'downsample_ratio': np.array([.4], np.float32)})
for i in range(n):
    p = plates[i]
    bg = clean_plate if clean_plate is not None else inpaint(p, actor_mask(p, actor_face(p)))
    t = gen_frame(i)
    x = cv2.cvtColor(t, cv2.COLOR_BGR2RGB).astype(np.float32).transpose(2, 0, 1)[None] / 255.
    _, pha, *rec = rvm.run(None, {'src': x, 'r1i': rec[0], 'r2i': rec[1], 'r3i': rec[2], 'r4i': rec[3], 'downsample_ratio': np.array([.4], np.float32)})
    al = cv2.GaussianBlur(cv2.erode(pha[0, 0], np.ones((3, 3), np.uint8)), (0, 0), .8)
    t = cv2.warpAffine(t, M, (W, H), flags=cv2.INTER_LANCZOS4, borderMode=cv2.BORDER_REPLICATE)
    al = cv2.warpAffine(al, M, (W, H))[..., None]; mk = al[..., 0] > .5
    fg = lab_match(t, tgt, mk) if tgt and mk.sum() > 500 else t.astype(np.float32)
    edge = np.clip(al - cv2.erode(al, np.ones((9, 9), np.uint8))[..., None], 0, 1)          # light wrap
    fg = fg * (1 - .35 * edge) + cv2.GaussianBlur(bg.astype(np.float32), (0, 0), 12) * .35 * edge
    if sig is None: sig = soft_sigma(fg * al + bg * (1 - al), mk, lap_t) if lap_t else 0.0; print('softness sigma', sig)
    fgs = cv2.GaussianBlur(fg, (0, 0), sig) if sig else fg
    comp = add_grain(fgs * al + bg.astype(np.float32) * (1 - al), grain * a.grain_gain)
    cv2.imwrite(f'{a.out}/{i:05d}.png', np.clip(comp, 0, 255).astype(np.uint8))
print('done', n, 'frames ->', a.out)
