#!/usr/bin/env python3
"""Replace every printed brand logo of one ink colour (e.g. a green icon + wordmark printed on boxes)
in an AI-generated clip with your own mark + wordmark, without regenerating the video.

usage: logo_swap.py --in clip.mp4 --out clip_swapped.mp4 --mark mark.png --font Inter.ttf --text "Brand"
       [--hsv-lo 28,35,20 --hsv-hi 55,255,255] [--skin-lo 0,50,130 --skin-hi 25,180,255] [--ink 1a1a1a]
Tune the HSV range on sampled frames of YOUR clip first (probe a few frames, view the mask).

Pipeline per frame:
  1. HSV threshold for the print colour -> connected components, closed/dilated
     just enough to fuse the eye icon with the word below it into one blob
     per print (verify on sampled frames of your clip).
  2. minAreaRect per blob -> greedy IoU tracking across frames + EMA smoothing
     of (center, size, angle) so the label doesn't jitter frame to frame.
  3. cv2.inpaint (TELEA) removes the green print, reconstructing cardboard
     from the surrounding pixels.
  4. The replacement label is perspective-warped onto the same rotated rect and
     multiply-blended using the local (post-inpaint) brightness, so box
     shading/lighting carries through, then softened with a light blur.
  5. Pixels flagged as skin (bright, warm, saturated - a hand/arm) inside the
     rect are excluded from both inpaint-copy and label paint, so hands are
     never painted over.

ponytail: per-frame color threshold + simple IoU tracker, not a learned
detector/optical-flow tracker - the clip has one consistent print color
and mostly-static boxes, verified directly against sampled frames before
committing to this approach. Upgrade to a real tracker only if a future clip
has moving/rotating boxes this approach visibly fails on.
"""
import subprocess
import sys

import cv2
import numpy as np
from PIL import Image, ImageDraw, ImageFont

import argparse
ap = argparse.ArgumentParser()
ap.add_argument("--in", dest="inp", required=True); ap.add_argument("--out", required=True)
ap.add_argument("--mark", required=True, help="RGBA PNG of the new logo mark (alpha used as shape)")
ap.add_argument("--font", required=True); ap.add_argument("--text", required=True)
ap.add_argument("--hsv-lo", default="28,35,20"); ap.add_argument("--hsv-hi", default="55,255,255")
ap.add_argument("--skin-lo", default="0,50,130"); ap.add_argument("--skin-hi", default="25,180,255")
ap.add_argument("--ink", default="1a1a1a", help="hex colour of the printed label")
ARGS = ap.parse_args()
IN_PATH, OUT_PATH, MARK_PATH, FONT_PATH, LABEL_TEXT = ARGS.inp, ARGS.out, ARGS.mark, ARGS.font, ARGS.text
def _t(v): return tuple(int(x) for x in v.split(","))

# Print colour range (defaults = a saturated green print), tuned per clip on sampled frames.
GREEN_LO = _t(ARGS.hsv_lo)
GREEN_HI = _t(ARGS.hsv_hi)
# Warm, bright, saturated = skin under warm lighting; hands are never painted over.
SKIN_LO = _t(ARGS.skin_lo)
SKIN_HI = _t(ARGS.skin_hi)

MIN_AREA = 800          # drop noise blobs smaller than this (px^2 @ 1920x1080)
PAD_FRAC = 0.14          # pad detected rect so the label fully covers the print
IOU_MATCH = 0.2
EMA_ALPHA = 0.45         # smoothing weight for new detections
MAX_MISSED_RENDER = 1    # keep painting a track for this many missed frames
MAX_MISSED_DROP = 4      # drop the track entirely after this many misses
LABEL_COLOR = tuple(int(ARGS.ink[i:i + 2], 16) for i in (0, 2, 4))  # near-black "printed on cardboard" ink


def build_label(canvas_size=1000):
    """New mark above, wordmark below - mirrors the original icon-over-
    word layout. Returns an RGBA numpy array, tightly cropped to content."""
    mark = Image.open(MARK_PATH).convert("RGBA")
    r, g, b, a = mark.split()
    tint = Image.merge(
        "RGBA",
        (Image.new("L", mark.size, LABEL_COLOR[0]),
         Image.new("L", mark.size, LABEL_COLOR[1]),
         Image.new("L", mark.size, LABEL_COLOR[2]),
         a),
    )
    mark_h = int(canvas_size * 0.56)
    tint = tint.resize((mark_h, mark_h), Image.LANCZOS)

    canvas = Image.new("RGBA", (canvas_size, canvas_size), (0, 0, 0, 0))
    mx = (canvas_size - mark_h) // 2
    my = int(canvas_size * 0.02)
    canvas.alpha_composite(tint, (mx, my))

    # Fit the wordmark width to roughly the mark's width, like the original print.
    target_w = int(mark_h * 1.08)
    font_size = int(canvas_size * 0.22)
    font = ImageFont.truetype(FONT_PATH, font_size)
    try:
        font.set_variation_by_axes([32, 700])  # [Optical size, Weight]
    except Exception:
        pass
    probe = ImageDraw.Draw(Image.new("L", (10, 10)))
    bbox = probe.textbbox((0, 0), LABEL_TEXT, font=font)
    text_w = bbox[2] - bbox[0]
    font_size = max(10, int(font_size * target_w / max(text_w, 1)))
    font = ImageFont.truetype(FONT_PATH, font_size)
    try:
        font.set_variation_by_axes([32, 700])
    except Exception:
        pass

    txt_layer = Image.new("RGBA", (canvas_size, canvas_size), (0, 0, 0, 0))
    d = ImageDraw.Draw(txt_layer)
    bbox = d.textbbox((0, 0), LABEL_TEXT, font=font)
    tw, th = bbox[2] - bbox[0], bbox[3] - bbox[1]
    tx = (canvas_size - tw) // 2 - bbox[0]
    ty = my + mark_h + int(canvas_size * 0.05) - bbox[1]
    d.text((tx, ty), LABEL_TEXT, font=font, fill=(*LABEL_COLOR, 255))
    canvas.alpha_composite(txt_layer)

    arr = np.array(canvas)
    ys, xs = np.where(arr[:, :, 3] > 8)
    y0, y1, x0, x1 = ys.min(), ys.max(), xs.min(), xs.max()
    pad = int(canvas_size * 0.03)
    y0 = max(0, y0 - pad); x0 = max(0, x0 - pad)
    y1 = min(canvas_size, y1 + pad); x1 = min(canvas_size, x1 + pad)
    return arr[y0:y1, x0:x1]


def normalize_rect(rect):
    (cx, cy), (w, h), ang = rect
    if w < h:
        w, h = h, w
        ang += 90
    while ang > 45:
        ang -= 90
    while ang <= -45:
        ang += 90
    return np.array([cx, cy, w, h, ang], dtype=np.float64)


def rect_to_aabb(t):
    cx, cy, w, h, ang = t
    box = cv2.boxPoints(((cx, cy), (w, h), ang))
    x0, y0 = box.min(axis=0)
    x1, y1 = box.max(axis=0)
    return x0, y0, x1, y1


def iou(a, b):
    ax0, ay0, ax1, ay1 = rect_to_aabb(a)
    bx0, by0, bx1, by1 = rect_to_aabb(b)
    ix0, iy0 = max(ax0, bx0), max(ay0, by0)
    ix1, iy1 = min(ax1, bx1), min(ay1, by1)
    iw, ih = max(0, ix1 - ix0), max(0, iy1 - iy0)
    inter = iw * ih
    if inter <= 0:
        return 0.0
    union = (ax1 - ax0) * (ay1 - ay0) + (bx1 - bx0) * (by1 - by0) - inter
    return inter / union if union > 0 else 0.0


def detect(frame):
    hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
    green = cv2.inRange(hsv, GREEN_LO, GREEN_HI)
    # no MORPH_OPEN here: distant/small prints are thin 1-2px anti-aliased
    # strokes that an open erases almost entirely (verified against a
    # frame where it dropped a print from h=132 to h=49, undershooting the
    # real extent and leaving a leftover fringe). MIN_AREA below still
    # rejects stray single-pixel noise after the merge.
    merged = cv2.morphologyEx(
        green, cv2.MORPH_CLOSE,
        cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (45, 75)),
    )
    merged = cv2.dilate(merged, cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (25, 25)))
    contours, _ = cv2.findContours(merged, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    dets = []
    for c in contours:
        if cv2.contourArea(c) < MIN_AREA:
            continue
        dets.append(normalize_rect(cv2.minAreaRect(c)))
    return dets, green


def order_corners(box):
    """4 boxPoints -> [top-left, top-right, bottom-right, bottom-left].
    Valid for the small rotation angles (<45deg) this clip's boxes show."""
    idx = np.argsort(box[:, 1])
    top2 = box[idx[:2]]
    bot2 = box[idx[2:]]
    tl, tr = top2[np.argsort(top2[:, 0])]
    bl, br = bot2[np.argsort(bot2[:, 0])]
    return np.array([tl, tr, br, bl], dtype=np.float32)


def full_quad(track):
    """The padded, rotated rect (order_corners'd) that a track's print +
    margin occupies - used both to widen the inpaint mask and as the
    cardboard-reconstruction footprint."""
    cx, cy, w, h, ang = track
    pw, ph = w * (1 + 2 * PAD_FRAC), h * (1 + 2 * PAD_FRAC)
    box = cv2.boxPoints(((cx, cy), (pw, ph), ang))
    return order_corners(box), pw, ph


def paint_track(output, clean, frame, label_rgba, track, skin_mask):
    cx, cy, w, h, ang = track
    dst_full, pw, ph = full_quad(track)
    H, W = frame.shape[:2]

    region_mask = np.zeros((H, W), np.uint8)
    cv2.fillConvexPoly(region_mask, dst_full.astype(np.int32), 255)
    paint_mask = (region_mask > 0) & (skin_mask == 0)
    if not paint_mask.any():
        return

    # label placement: fit into the padded rect preserving ITS OWN aspect
    # ratio (object-fit: contain) so the mark never gets stretched into an
    # oval, then perspective-warp that smaller quad onto the same rotation.
    lh, lw = label_rgba.shape[:2]
    label_ar = lw / lh
    box_ar = pw / ph
    if label_ar > box_ar:
        fw, fh = pw, pw / label_ar
    else:
        fh, fw = ph, ph * label_ar
    label_box = cv2.boxPoints(((cx, cy), (fw, fh), ang))
    dst = order_corners(label_box)

    src = np.array([[0, 0], [lw, 0], [lw, lh], [0, lh]], dtype=np.float32)
    M = cv2.getPerspectiveTransform(src, dst)
    warped = cv2.warpPerspective(
        label_rgba, M, (W, H), flags=cv2.INTER_LINEAR, borderMode=cv2.BORDER_CONSTANT
    )
    label_alpha = warped[:, :, 3].astype(np.float32) / 255.0
    label_alpha = cv2.GaussianBlur(label_alpha, (0, 0), 1.0)
    label_shade = warped[:, :, :3].astype(np.float32)  # BGR-ish (values are gray anyway)

    m = paint_mask & (label_alpha > 0.02)
    if not m.any():
        # still reconstruct cardboard under the whole print even if the
        # label warp missed a sliver (rounding at tiny sizes)
        output[paint_mask] = clean[paint_mask]
        return

    # reconstruct cardboard first (removes the original print)
    output[paint_mask] = clean[paint_mask]

    base = output.astype(np.float32)
    a = label_alpha[..., None]
    blend = label_shade / 255.0
    multiplied = base * blend
    out = base * (1 - a) + multiplied * a
    output[m] = np.clip(out[m], 0, 255).astype(np.uint8)


def main():
    cap = cv2.VideoCapture(IN_PATH)
    if not cap.isOpened():
        sys.exit(f"cannot open {IN_PATH}")
    fps = cap.get(cv2.CAP_PROP_FPS) or 30
    W = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    H = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    n_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))

    label_rgba = build_label()

    ffmpeg = subprocess.Popen(
        [
            "ffmpeg", "-y", "-f", "rawvideo", "-pix_fmt", "bgr24",
            "-s", f"{W}x{H}", "-r", str(fps), "-i", "-",
            "-an", "-c:v", "libx264", "-crf", "10", "-pix_fmt", "yuv420p",
            OUT_PATH,
        ],
        stdin=subprocess.PIPE,
    )

    tracks = {}   # id -> [cx,cy,w,h,ang, missed]
    next_id = 0
    stats = []    # detections-per-frame for the report

    fidx = 0
    while True:
        ok, frame = cap.read()
        if not ok:
            break
        dets, green_mask = detect(frame)
        stats.append(len(dets))

        # greedy IoU match: existing tracks vs this frame's detections
        used = set()
        for tid, t in tracks.items():
            best_j, best_iou = -1, 0.0
            for j, d in enumerate(dets):
                if j in used:
                    continue
                v = iou(t[:5], d)
                if v > best_iou:
                    best_iou, best_j = v, j
            if best_iou >= IOU_MATCH:
                used.add(best_j)
                d = dets[best_j]
                t[:5] = EMA_ALPHA * d + (1 - EMA_ALPHA) * t[:5]
                t[5] = 0
            else:
                t[5] += 1
        for j, d in enumerate(dets):
            if j in used:
                continue
            tracks[next_id] = np.append(d, 0.0)
            next_id += 1
        tracks = {k: v for k, v in tracks.items() if v[5] <= MAX_MISSED_DROP}

        # inpaint mask = raw green pixels (dilated) UNION every rendered
        # track's full padded footprint, so a print's antialiased/desaturated
        # fringe pixels that fall just outside the strict green threshold
        # still get cardboard-reconstructed instead of leaking through as a
        # tinted remnant next to the label.
        inpaint_mask = cv2.dilate(green_mask, np.ones((7, 7), np.uint8))
        for t in tracks.values():
            if t[5] > MAX_MISSED_RENDER:
                continue
            quad, _, _ = full_quad(t[:5])
            cv2.fillConvexPoly(inpaint_mask, quad.astype(np.int32), 255)
        clean = cv2.inpaint(frame, inpaint_mask, 5, cv2.INPAINT_TELEA)

        hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
        skin_mask = cv2.inRange(hsv, SKIN_LO, SKIN_HI)

        output = frame.copy()
        for t in tracks.values():
            if t[5] > MAX_MISSED_RENDER:
                continue
            paint_track(output, clean, frame, label_rgba, t[:5], skin_mask)

        ffmpeg.stdin.write(output.tobytes())
        fidx += 1

    cap.release()
    ffmpeg.stdin.close()
    ffmpeg.wait()

    if stats:
        print(f"frames={len(stats)} detections/frame min={min(stats)} "
              f"avg={sum(stats)/len(stats):.2f} max={max(stats)}")
    if fidx != n_frames and n_frames > 0:
        print(f"warning: wrote {fidx} frames, source reported {n_frames}", file=sys.stderr)


if __name__ == "__main__":
    main()
