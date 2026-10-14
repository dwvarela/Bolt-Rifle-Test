"""Textured orthographic software renderer for the geo models (checks shapes AND painted textures).
Usage: GUN=<id> render.py <resources_dir> <out.png> [hidden,bones] [yaw pitch scale]
yaw 0 = looking at the shooter's right side with the muzzle to the right."""
import json, sys, math, os
import numpy as np
from PIL import Image

res, out = sys.argv[1], sys.argv[2]
hidden = set(sys.argv[3].split(",")) if len(sys.argv) > 3 and sys.argv[3] else {"bolt_hand", "casing", "chamber_round", "muzzle_flash", "left_hand", "right_hand"}
views = [(0, 6), (-35, 22)] if len(sys.argv) <= 4 else [(float(sys.argv[4]), float(sys.argv[5]))]
SC = float(sys.argv[6]) if len(sys.argv) > 6 else 14.0
GUN = os.environ.get("GUN", "bolt_rifle")
geo = json.load(open(f"{res}/assets/boltrifle/geo/item/{GUN}.geo.json"))["minecraft:geometry"][0]
tex = np.array(Image.open(f"{res}/assets/boltrifle/textures/item/{GUN}.png").convert("RGB")).astype(float)
TH, TW = tex.shape[:2]


def rot_cube(p, pivot, rot):
    x, y, z = p[0] - pivot[0], p[1] - pivot[1], p[2] - pivot[2]
    ax, ay, az = math.radians(-rot[0]), math.radians(-rot[1]), math.radians(rot[2])
    y, z = y * math.cos(ax) - z * math.sin(ax), y * math.sin(ax) + z * math.cos(ax)
    x, z = x * math.cos(ay) + z * math.sin(ay), -x * math.sin(ay) + z * math.cos(ay)
    x, y = x * math.cos(az) - y * math.sin(az), x * math.sin(az) + y * math.cos(az)
    return np.array([x + pivot[0], y + pivot[1], z + pivot[2]])


quads = []   # (4x3 points, face name, uv rect)
for b in geo["bones"]:
    if b["name"] in hidden:
        continue
    for c in b["cubes"]:
        ox, oy, oz = c["origin"]; sx, sy, sz = c["size"]
        def P(dx, dy, dz):
            p = np.array([ox + dx * sx, oy + dy * sy, oz + dz * sz])
            return rot_cube(p, c["pivot"], c["rotation"]) if "rotation" in c else p
        faces = {"north": [P(0, 0, 0), P(1, 0, 0), P(1, 1, 0), P(0, 1, 0)],
                 "south": [P(1, 0, 1), P(0, 0, 1), P(0, 1, 1), P(1, 1, 1)],
                 "east": [P(1, 0, 0), P(1, 0, 1), P(1, 1, 1), P(1, 1, 0)],
                 "west": [P(0, 0, 1), P(0, 0, 0), P(0, 1, 0), P(0, 1, 1)],
                 "up": [P(0, 1, 0), P(1, 1, 0), P(1, 1, 1), P(0, 1, 1)],
                 "down": [P(0, 0, 1), P(1, 0, 1), P(1, 0, 0), P(0, 0, 0)]}
        for f, pts in faces.items():
            quads.append((np.array(pts), f, c["uv"][f]))

LIGHT = np.array([-0.35, 0.8, -0.5]); LIGHT /= np.linalg.norm(LIGHT)
for vi, (yaw, pitch) in enumerate(views):
    W, H = int(70 * SC), int(26 * SC)
    img = np.full((H, W, 3), 238.0)
    zbuf = np.full((H, W), -1e9)
    ya, pa = math.radians(yaw), math.radians(pitch)
    # camera looks along +X from the left of the model's side: screen right = -Z (muzzle right), up = +Y
    def proj(p):
        x, y, z = p
        # rotate around Y by yaw, then tilt by pitch
        x1 = x * math.cos(ya) + z * math.sin(ya)
        z1 = -x * math.sin(ya) + z * math.cos(ya)
        y1 = y * math.cos(pa) - z1 * math.sin(pa)
        d1 = y * math.sin(pa) + z1 * math.cos(pa)
        return np.array([-z1, y1, x1 * 0 + d1 * 0 + (-x1)]), x1
    for pts, f, uv in quads:
        sp, depth = [], []
        for p in pts:
            q, _ = proj(p)
            sp.append(q)
        sp = np.array(sp)
        e1, e2 = sp[1] - sp[0], sp[3] - sp[0]
        nrm = np.cross(np.append(e1[:2], 0), np.append(e2[:2], 0))
        # depth = third component (toward viewer = larger)
        n3 = np.cross(sp[1] - sp[0], sp[3] - sp[0])
        if n3[2] <= 0:
            continue
        shade = 0.62 + 0.45 * max(0.0, float(np.dot(n3 / (np.linalg.norm(n3) + 1e-9), np.array([0.3, 0.6, 0.75]))))
        scr = np.stack([W / 2 + sp[:, 0] * SC, H / 2 - sp[:, 1] * SC - 0 * H], axis=1)
        u0, v0, uw, vh = uv["uv"][0], uv["uv"][1], uv["uv_size"][0], uv["uv_size"][1]
        for tri in ((0, 1, 2), (0, 2, 3)):
            a, b, c = (scr[i] for i in tri)
            minx, maxx = int(max(0, min(a[0], b[0], c[0]))), int(min(W - 1, max(a[0], b[0], c[0]) + 1))
            miny, maxy = int(max(0, min(a[1], b[1], c[1]))), int(min(H - 1, max(a[1], b[1], c[1]) + 1))
            if maxx <= minx or maxy <= miny:
                continue
            xs, ys = np.meshgrid(np.arange(minx, maxx + 1) + 0.5, np.arange(miny, maxy + 1) + 0.5)
            den = (b[1] - c[1]) * (a[0] - c[0]) + (c[0] - b[0]) * (a[1] - c[1])
            if abs(den) < 1e-9:
                continue
            w1 = ((b[1] - c[1]) * (xs - c[0]) + (c[0] - b[0]) * (ys - c[1])) / den
            w2 = ((c[1] - a[1]) * (xs - c[0]) + (a[0] - c[0]) * (ys - c[1])) / den
            w3 = 1 - w1 - w2
            m = (w1 >= -1e-6) & (w2 >= -1e-6) & (w3 >= -1e-6)
            if not m.any():
                continue
            quad_uv = np.array([[0, 0], [1, 0], [1, 1], [0, 1]])
            uu = w1 * quad_uv[tri[0], 0] + w2 * quad_uv[tri[1], 0] + w3 * quad_uv[tri[2], 0]
            vv = w1 * quad_uv[tri[0], 1] + w2 * quad_uv[tri[1], 1] + w3 * quad_uv[tri[2], 1]
            dz = w1 * sp[tri[0], 2] + w2 * sp[tri[1], 2] + w3 * sp[tri[2], 2]
            tx = np.clip((u0 + uu * uw).astype(int), 0, TW - 1)
            ty = np.clip((v0 + (1 - vv) * vh).astype(int), 0, TH - 1)
            col = tex[ty, tx] * shade
            sub = zbuf[miny:maxy + 1, minx:maxx + 1]
            upd = m & (dz > sub)
            sub[upd] = dz[upd]
            region = img[miny:maxy + 1, minx:maxx + 1]
            region[upd] = col[upd]
    ys, xs = np.where(zbuf > -1e8)
    if len(xs):
        img = img[max(0, ys.min() - 8):ys.max() + 9, max(0, xs.min() - 8):xs.max() + 9]
    Image.fromarray(np.clip(img, 0, 255).astype(np.uint8)).save(out.replace(".png", f"_{vi}.png"))
print("saved", out)
