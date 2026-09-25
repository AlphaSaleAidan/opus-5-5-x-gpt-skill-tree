#!/usr/bin/env python3
"""Thin-lens depth-of-field on a SHARP background (still or frames) from a depth map. UNTESTED rewrite of
the job's layered lens blur. Apply AFTER any AI animation of the plate (animators freeze blurred stills).

  lens_blur.py --img plate.png --depth depth.npy --out plate_f4.png --focus 4.3 --fstop 4 --focal 35 [--inverse]
  lens_blur.py --img frames/ --depth depth.npy --out blurred/ ...   (same depth for every frame of a locked-off plate)
--depth: metres (Blender Z) or, with --inverse, relative inverse depth (Depth Anything V2) scaled so the
focus plane lands at --focus: z = focus * d_focus / d, with d_focus = median depth in --focus-box.
"""
import argparse, glob, os, cv2, numpy as np

ap = argparse.ArgumentParser(); ap.add_argument('--img', required=True); ap.add_argument('--depth', required=True); ap.add_argument('--out', required=True)
ap.add_argument('--focus', type=float, required=True, help='subject distance, m'); ap.add_argument('--fstop', type=float, default=4.0)
ap.add_argument('--focal', type=float, default=35.0, help='mm'); ap.add_argument('--sensor', type=float, default=36.0, help='sensor width mm')
ap.add_argument('--inverse', action='store_true'); ap.add_argument('--focus-box', help='x,y,w,h in image px for the focus sample (default centre)')
ap.add_argument('--layers', type=int, default=12)
a = ap.parse_args()

def coc_px(z, W):
    f = a.focal / 1000; s = a.focus; N = a.fstop
    c = np.abs(f * f * (z - s) / (N * z * (s - f)))          # CoC diameter on the sensor, metres
    return c / (a.sensor / 1000) * W                          # -> pixels

def blur(img, D):
    H, W = img.shape[:2]; D = cv2.resize(D.astype(np.float32), (W, H), interpolation=cv2.INTER_LINEAR)
    if a.inverse:
        x, y, w, h = map(int, a.focus_box.split(',')) if a.focus_box else (W // 2 - W // 20, H // 2 - H // 20, W // 10, H // 10)
        d0 = np.median(D[y:y + h, x:x + w]); z = a.focus * d0 / np.maximum(D, 1e-6)
    else: z = D
    r = coc_px(np.maximum(z, .05), W) / 2; edges = np.linspace(0, r.max() + 1e-6, a.layers + 1)
    out = np.zeros_like(img, np.float32); acc = np.zeros((H, W, 1), np.float32)
    for k in range(a.layers):                                  # far/near layers, each blurred with its own radius
        m = ((r >= edges[k]) & (r < edges[k + 1])).astype(np.float32)[..., None]
        rad = (edges[k] + edges[k + 1]) / 2
        if m.sum() == 0: continue
        if rad < .5: bl, bm = img.astype(np.float32) * m, m
        else:
            ks = int(2 * round(rad) + 1); disk = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (ks, ks)).astype(np.float32); disk /= disk.sum()
            bl = cv2.filter2D(img.astype(np.float32) * m, -1, disk); bm = cv2.filter2D(m, -1, disk)[..., None]
        out += bl; acc += bm
    return np.clip(out / np.maximum(acc, 1e-4), 0, 255).astype(np.uint8)

D = np.load(a.depth)
if os.path.isdir(a.img):
    os.makedirs(a.out, exist_ok=True)
    for f in sorted(glob.glob(f'{a.img}/*.png')): cv2.imwrite(f'{a.out}/{os.path.basename(f)}', blur(cv2.imread(f), D))
else: cv2.imwrite(a.out, blur(cv2.imread(a.img), D))
print('wrote', a.out)
