#!/usr/bin/env python3
"""Contact sheets for a frame-by-frame review: every Nth frame, labelled with frame + timecode, sheets
<= 1400 px wide; optional zoom crops of one region at full resolution.

  sheets.py --video out.mp4 --out qc/ [--every 3] [--cols 6] [--thumb 224] [--start 0 --end 900]
  sheets.py --video out.mp4 --out qc/ --zoom 820,380,560,560 --frames 480,495,510   (x,y,w,h in source px)
Decodes sequentially (random seeks return wrong frames on long-GOP files). Needs ffmpeg + pillow + numpy.
"""
import argparse, os, subprocess, numpy as np
from PIL import Image, ImageDraw

ap = argparse.ArgumentParser(); ap.add_argument('--video', required=True); ap.add_argument('--out', required=True)
ap.add_argument('--every', type=int, default=3); ap.add_argument('--cols', type=int, default=6); ap.add_argument('--thumb', type=int, default=224)
ap.add_argument('--rows', type=int, default=6); ap.add_argument('--start', type=int, default=0); ap.add_argument('--end', type=int, default=10 ** 9)
ap.add_argument('--zoom'); ap.add_argument('--frames')
a = ap.parse_args(); os.makedirs(a.out, exist_ok=True)
w, h, fr = subprocess.run(['ffprobe', '-v', 'error', '-select_streams', 'v:0', '-show_entries', 'stream=width,height,r_frame_rate',
                           '-of', 'csv=p=0', a.video], capture_output=True, text=True).stdout.strip().split(',')[:3]
W, H = int(w), int(h); num, den = map(int, fr.split('/')); fps = num / den
p = subprocess.Popen(['ffmpeg', '-v', 'error', '-i', a.video, '-pix_fmt', 'rgb24', '-f', 'rawvideo', '-'], stdout=subprocess.PIPE)
want = set(int(x) for x in a.frames.split(',')) if a.frames else None
zx, zy, zw, zh = map(int, a.zoom.split(',')) if a.zoom else (0, 0, 0, 0)
th = int(a.thumb * H / W); per = a.cols * a.rows; tiles, sheet_no, i = [], 0, 0

def flush():
    global tiles, sheet_no
    if not tiles: return
    S = Image.new('RGB', (a.cols * a.thumb, ((len(tiles) - 1) // a.cols + 1) * (th + 14)), (20, 20, 20))
    for k, (n, im) in enumerate(tiles):
        x, y = (k % a.cols) * a.thumb, (k // a.cols) * (th + 14); S.paste(im, (x, y + 14))
        ImageDraw.Draw(S).text((x + 3, y + 1), f'f{n} {n / fps:6.2f}s', fill=(255, 220, 90))
    S.save(f'{a.out}/sheet_{sheet_no:03d}.jpg', quality=88); sheet_no += 1; tiles = []

while True:
    buf = p.stdout.read(W * H * 3)
    if len(buf) < W * H * 3 or i > a.end: break
    if i >= a.start:
        if want is not None and i in want:
            Image.frombuffer('RGB', (W, H), buf).crop((zx, zy, zx + zw, zy + zh)).save(f'{a.out}/zoom_f{i:05d}.png')
        elif want is None and (i - a.start) % a.every == 0:
            tiles.append((i, Image.frombuffer('RGB', (W, H), buf).resize((a.thumb, th), Image.BILINEAR)))
            if len(tiles) == per: flush()
    i += 1
flush(); p.stdout.close(); p.wait()
print(f'{i} frames read at {fps:.3f} fps ->', a.out)
