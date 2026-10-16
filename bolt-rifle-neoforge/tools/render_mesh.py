"""Preview renderer for mesh models: python3 render_mesh.py <res> <id> <out.png> [yaw pitch scale] [hidden,bones]
Draws poly_mesh bones (textured, z-buffered, orthographic) and the remaining cube bones as flat boxes."""
import sys, json, math
import numpy as np
from PIL import Image

res, ident, out = sys.argv[1:4]
yaw = float(sys.argv[4]) if len(sys.argv) > 4 else 0.0
pitch = float(sys.argv[5]) if len(sys.argv) > 5 else 6.0
SC = float(sys.argv[6]) if len(sys.argv) > 6 else 14.0
hidden = set(sys.argv[7].split(",")) if len(sys.argv) > 7 else {"bolt_hand", "casing", "chamber_round", "muzzle_flash", "left_hand", "right_hand"}
geo = json.load(open(f"{res}/assets/boltrifle/geo/item/{ident}.geo.json"))["minecraft:geometry"][0]
tex = np.array(Image.open(f"{res}/assets/boltrifle/textures/item/{ident}.png").convert("RGB"))
TH, TW = tex.shape[:2]
ya, pa = math.radians(yaw), math.radians(pitch)
Ry = np.array([[math.cos(ya), 0, math.sin(ya)], [0, 1, 0], [-math.sin(ya), 0, math.cos(ya)]])
Rp = np.array([[1, 0, 0], [0, math.cos(pa), -math.sin(pa)], [0, math.sin(pa), math.cos(pa)]])
R = Rp @ Ry
tris = []   # (3x3 positions, 3x2 uv)
for b in geo["bones"]:
    if b["name"] in hidden:
        continue
    pm = b.get("poly_mesh")
    if pm:
        P = np.array(pm["positions"]).reshape(-1, 3)
        UV = np.array(pm["uvs"]).reshape(-1, 2)
        for poly in pm["polys"]:
            tris.append((P[[poly[0][0], poly[1][0], poly[2][0]]], UV[[poly[0][2], poly[1][2], poly[2][2]]]))
pts = np.concatenate([t[0] for t in tris]) if tris else np.zeros((1, 3))
c = (pts.min(0) + pts.max(0)) / 2
W = H = 0
proj = [((t[0] - c) @ R.T, t[1]) for t in tris]
allp = np.concatenate([p[0] for p in proj])
x0, x1 = allp[:, 0].min(), allp[:, 0].max()
y0, y1 = allp[:, 1].min(), allp[:, 1].max()
W, H = int((x1 - x0) * SC) + 20, int((y1 - y0) * SC) + 20
img = np.full((H, W, 3), 238, np.uint8)
zb = np.full((H, W), -1e9)
L = np.array([-0.4, 0.7, 0.6])
L /= np.linalg.norm(L)
for (p, uv), t in zip(proj, tris):
    sx = (p[:, 0] - x0) * SC + 10
    sy = (y1 - p[:, 1]) * SC + 10
    xs0, xs1 = int(max(sx.min(), 0)), int(min(sx.max() + 1, W - 1))
    ys0, ys1 = int(max(sy.min(), 0)), int(min(sy.max() + 1, H - 1))
    if xs1 < xs0 or ys1 < ys0:
        continue
    gx, gy = np.meshgrid(np.arange(xs0, xs1 + 1), np.arange(ys0, ys1 + 1))
    d = (sy[1] - sy[2]) * (sx[0] - sx[2]) + (sx[2] - sx[1]) * (sy[0] - sy[2])
    if abs(d) < 1e-9:
        continue
    l0 = ((sy[1] - sy[2]) * (gx + .5 - sx[2]) + (sx[2] - sx[1]) * (gy + .5 - sy[2])) / d
    l1 = ((sy[2] - sy[0]) * (gx + .5 - sx[2]) + (sx[0] - sx[2]) * (gy + .5 - sy[2])) / d
    l2 = 1 - l0 - l1
    m = (l0 >= -0.02) & (l1 >= -0.02) & (l2 >= -0.02)
    if not m.any():
        continue
    z = l0 * p[0, 2] + l1 * p[1, 2] + l2 * p[2, 2]
    u = (l0 * uv[0, 0] + l1 * uv[1, 0] + l2 * uv[2, 0]) * TW
    v = (l0 * uv[0, 1] + l1 * uv[1, 1] + l2 * uv[2, 1]) * TH
    col = tex[np.clip(v.astype(int), 0, TH - 1), np.clip(u.astype(int), 0, TW - 1)]
    n = np.cross(t[0][1] - t[0][0], t[0][2] - t[0][0])
    n = R @ (n / max(np.linalg.norm(n), 1e-9))
    lit = 0.62 + 0.38 * abs(float(n @ L))
    upd = m & (z > zb[gy, gx])
    zb[gy[upd], gx[upd]] = z[upd]
    img[gy[upd], gx[upd]] = np.clip(col[upd] * lit, 0, 255).astype(np.uint8)
Image.fromarray(img).save(out.replace(".png", "_0.png"))
print("saved", out.replace(".png", "_0.png"), len(tris), "tris")
