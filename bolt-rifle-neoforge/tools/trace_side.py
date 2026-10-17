"""Trace the silhouette of a reference side view into model coordinates (px = 1/16 block, muzzle -Z, bore y = 0).
The reference photos themselves are not stored in the repo, only the traced outline (JSON).
Usage: trace_side.py <image> <x0 x1 y0 y1 crop> <bore_y_img> <x_muzzle_img> <x_butt_img> <z_muzzle> <z_butt> <out.json> [thresh] [flip]
The view is expected to have the muzzle on the left (shooter's right side)."""
import sys, json
import numpy as np
import cv2
from PIL import Image

img, x0, x1, y0, y1, bore, xm, xb, zm, zb, out = sys.argv[1:12]
thr = int(sys.argv[12]) if len(sys.argv) > 12 else 24
x0, x1, y0, y1 = int(x0), int(x1), int(y0), int(y1)
bore, xm, xb, zm, zb = float(bore), float(xm), float(xb), float(zm), float(zb)
a = np.array(Image.open(img).convert("RGB")).max(2)[y0:y1, x0:x1]
a = cv2.GaussianBlur(a, (3, 3), 0)
mask = (a > thr).astype(np.uint8) * 255
mask = cv2.morphologyEx(mask, cv2.MORPH_CLOSE, np.ones((3, 3), np.uint8))
k = (zb - zm) / (xb - xm)                   # model px per image px
cnts, hier = cv2.findContours(mask, cv2.RETR_CCOMP, cv2.CHAIN_APPROX_NONE)
res = []
for i, c in enumerate(cnts):
    if cv2.contourArea(c) < 40:
        continue
    ap = cv2.approxPolyDP(c, 1.1, True).reshape(-1, 2)
    pts = [[round(zm + (p[0] + x0 - xm) * k, 3), round((bore - (p[1] + y0)) * k, 3)] for p in ap]
    res.append(dict(hole=bool(hier[0][i][3] >= 0), pts=pts, area=float(cv2.contourArea(c))))
json.dump(res, open(out, "w"))
print(len(res), "contours; px per model px = %.2f" % (1 / k))
cv2.imwrite(out.replace(".json", "_mask.png"), mask)
