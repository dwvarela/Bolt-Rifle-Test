"""M67 grenade icon, 32x32, drawn at 8x and shaded. Usage: gen_grenade.py <resources_dir>"""
import sys, os, math
import numpy as np
from PIL import Image, ImageDraw

N, SS = 32, 8
S = N * SS
YY, XX = np.mgrid[0:S, 0:S]
cv = np.zeros((S, S, 4))


def fill(mask, fn):
    ys, xs = np.nonzero(mask)
    cv[ys, xs, :3] = fn(xs, ys)
    cv[ys, xs, 3] = 255


def poly(pts, fn):
    im = Image.new("L", (S, S), 0)
    ImageDraw.Draw(im).polygon([(x * SS, y * SS) for x, y in pts], fill=255)
    fill(np.array(im) > 127, fn)


# body: olive sphere with a lit upper-left
cx, cy, r = 15.5 * SS, 19 * SS, 9.3 * SS
d2 = (XX - cx) ** 2 + (YY - cy) ** 2
body = d2 < r * r
def body_col(xs, ys):
    nx, ny = (xs - cx) / r, (ys - cy) / r
    nz = np.sqrt(np.clip(1 - nx * nx - ny * ny, 0, 1))
    l = np.clip(-0.5 * nx - 0.6 * ny + 0.62 * nz, 0, 1)
    shade = 0.32 + 0.9 * l
    base = np.array([74, 86, 52], dtype=float)
    col = base[None, :] * shade[:, None]
    col += (np.clip(l - 0.86, 0, 1) * 220)[:, None]                       # specular
    return col
fill(body, body_col)
# segmented fragmentation grid: dark grooves
for k in range(-3, 4):
    t = k / 3.4
    xe = cx + t * r
    im = Image.new("L", (S, S), 0)
    dr = ImageDraw.Draw(im)
    dr.line([(xe, cy - r), (xe + t * 0.0, cy + r)], fill=255, width=int(0.5 * SS))
    m = (np.array(im) > 127) & body
    cv[m, :3] *= 0.62
for k in range(-3, 4):
    ye = cy + k / 3.4 * r
    im = Image.new("L", (S, S), 0)
    ImageDraw.Draw(im).line([(cx - r, ye), (cx + r, ye)], fill=255, width=int(0.5 * SS))
    m = (np.array(im) > 127) & body
    cv[m, :3] *= 0.7
# fuse body (steel), neck
poly([(13, 9.6), (18.2, 9.6), (18.2, 6.2), (13, 6.2)], lambda xs, ys: np.stack([120 + 40 * np.exp(-((xs / SS - 13.8) ** 2) / 1.2)] * 3, 1) * np.array([0.78, 0.82, 0.88]))
poly([(12.4, 6.4), (19.0, 6.4), (19.0, 4.6), (12.4, 4.6)], lambda xs, ys: np.tile(np.array([88.0, 92, 100]), (len(xs), 1)))
# spoon (safety lever): runs along the right side and over the body
poly([(18.2, 5.6), (21.4, 6.2), (25.2, 12.0), (25.8, 21.0), (24.0, 21.4), (23.6, 13.0), (20.4, 8.0), (18.2, 7.6)],
     lambda xs, ys: np.tile(np.array([150.0, 154, 160]), (len(xs), 1)) * (0.8 + 0.3 * np.sin(xs * 0.02)[:, None]))
# pull ring
im = Image.new("L", (S, S), 0)
ImageDraw.Draw(im).ellipse([5 * SS, 1.2 * SS, 13.2 * SS, 7.6 * SS], outline=255, width=int(0.9 * SS))
fill(np.array(im) > 127, lambda xs, ys: np.tile(np.array([186.0, 190, 196]), (len(xs), 1)))
poly([(12.6, 5.0), (14.2, 5.0), (14.2, 5.7), (12.6, 5.7)], lambda xs, ys: np.tile(np.array([186.0, 190, 196]), (len(xs), 1)))

img = Image.fromarray(np.clip(cv, 0, 255).astype(np.uint8), "RGBA").resize((N, N), Image.BOX)
arr = np.array(img).astype(float)
alpha = arr[..., 3] > 90
pad = np.pad(alpha, 1)
nb = pad[:-2, 1:-1] | pad[2:, 1:-1] | pad[1:-1, :-2] | pad[1:-1, 2:]
edge = nb & ~alpha
arr[edge] = [16, 18, 14, 255]
arr[~alpha & ~edge, 3] = 0
arr[alpha, 3] = 255
out = os.path.join(sys.argv[1], "assets/boltrifle/textures/item/grenade.png")
Image.fromarray(arr.astype(np.uint8), "RGBA").save(out)
print("saved", out)
