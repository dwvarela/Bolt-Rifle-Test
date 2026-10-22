"""Poses a baked gun at a given animation time and renders it (orthographic, z-buffered, textured) - a preview of what the game draws.
Usage: pose_render.py <res_dir> <gun_id> <animation_name> <t1,t2,...> <out.png> [view=side|top|behind|front|3q] [scale] [hide,bones]
Conventions (verified against GeckoLib): JSON-space position offsets apply as given; rotations are the game rotation Rz(az)*Ry(-ay)*Rx(-ax)
conjugated by the x mirror (game x = -json x); every bone rotates about its pivot after being translated; children inherit.
Screen x is drawn as -json_x so the picture matches what the player sees (game right = json -x)."""
import sys, json, math
import numpy as np
from PIL import Image, ImageDraw

res, gid, anim, times, out = sys.argv[1:6]
view = sys.argv[6] if len(sys.argv) > 6 else "side"
SC = float(sys.argv[7]) if len(sys.argv) > 7 else 12.0
hide = set(sys.argv[8].split(",")) if len(sys.argv) > 8 else set()
geo = json.load(open(f"{res}/assets/boltrifle/geo/item/{gid}.geo.json"))["minecraft:geometry"][0]
ani = json.load(open(f"{res}/assets/boltrifle/animations/item/{gid}.animation.json"))["animations"][f"animation.{gid}.{anim}"]
tex = np.array(Image.open(f"{res}/assets/boltrifle/textures/item/{gid}.png").convert("RGB"))
TH, TW = tex.shape[:2]
bones = {b["name"]: b for b in geo["bones"]}


def chan(bone, name, t, default):
    fr = ani.get("bones", {}).get(bone, {}).get(name)
    if not fr:
        return np.array(default, float)
    ks = sorted((float(k), np.array(v["vector"] if isinstance(v, dict) else v, float)) for k, v in fr.items())
    if t <= ks[0][0]:
        return ks[0][1]
    for (t0, v0), (t1, v1) in zip(ks, ks[1:]):
        if t0 <= t <= t1:
            return v0 + (v1 - v0) * ((t - t0) / (t1 - t0) if t1 > t0 else 1.0)
    return ks[-1][1]


def rot(ax, ay, az):
    a, b, c = (math.radians(-ax), math.radians(-ay), math.radians(az))      # game angles
    Rx = np.array([[1, 0, 0], [0, math.cos(a), -math.sin(a)], [0, math.sin(a), math.cos(a)]])
    Ry = np.array([[math.cos(b), 0, math.sin(b)], [0, 1, 0], [-math.sin(b), 0, math.cos(b)]])
    Rz = np.array([[math.cos(c), -math.sin(c), 0], [math.sin(c), math.cos(c), 0], [0, 0, 1]])
    G = Rz @ Ry @ Rx
    S = np.diag([-1.0, 1, 1])
    return S @ G @ S


def world(name, t, cache):
    if name in cache:
        return cache[name]
    b = bones[name]
    M = np.eye(4)
    if b.get("parent"):
        M = world(b["parent"], t, cache)
    piv = np.array(b.get("pivot", [0, 0, 0]), float)
    pos = chan(name, "position", t, [0, 0, 0])
    r = rot(*chan(name, "rotation", t, [0, 0, 0]))
    sc = chan(name, "scale", t, [1, 1, 1])
    L = np.eye(4)
    L[:3, 3] = pos
    P = np.eye(4); P[:3, 3] = piv
    Pi = np.eye(4); Pi[:3, 3] = -piv
    R = np.eye(4); R[:3, :3] = r @ np.diag(sc)
    cache[name] = M @ L @ P @ R @ Pi
    return cache[name]


def tris_at(t):
    cache = {}
    out_t = []
    for name, b in bones.items():
        if name in hide:
            continue
        sc = chan(name, "scale", t, [1, 1, 1])
        if np.all(sc == 0):
            continue
        M = world(name, t, cache)
        pm = b.get("poly_mesh")
        if pm:
            P = np.array(pm["positions"]).reshape(-1, 3)
            UV = np.array(pm["uvs"]).reshape(-1, 2)
            Pw = (M[:3, :3] @ P.T).T + M[:3, 3]
            for poly in pm["polys"]:
                out_t.append((Pw[[poly[0][0], poly[1][0], poly[2][0]]], UV[[poly[0][2], poly[1][2], poly[2][2]]]))
        for cu in b.get("cubes", []):
            o, s = np.array(cu["origin"], float), np.array(cu["size"], float)
            corners = np.array([[o[0] + dx * s[0], o[1] + dy * s[1], o[2] + dz * s[2]] for dx in (0, 1) for dy in (0, 1) for dz in (0, 1)])
            cw = (M[:3, :3] @ corners.T).T + M[:3, 3]
            for f in ((0, 1, 3, 2), (4, 5, 7, 6), (0, 1, 5, 4), (2, 3, 7, 6), (0, 2, 6, 4), (1, 3, 7, 5)):
                q = cw[list(f)]
                for tri in ((0, 1, 2), (0, 2, 3)):
                    out_t.append((q[list(tri)], np.array([[0.02, 0.02]] * 3)))
    return out_t


VIEWS = {"side": (90, 4), "top": (90, 85), "behind": (180, 10), "front": (0, 10), "3q": (140, 28)}
yaw, pitch = VIEWS.get(view, (90, 4))
ya, pa = math.radians(yaw), math.radians(pitch)
Ry = np.array([[math.cos(ya), 0, math.sin(ya)], [0, 1, 0], [-math.sin(ya), 0, math.cos(ya)]])
Rp = np.array([[1, 0, 0], [0, math.cos(pa), -math.sin(pa)], [0, math.sin(pa), math.cos(pa)]])
Rv = Rp @ Ry @ np.diag([-1.0, 1, 1])      # draw as the player sees it (x mirrored)
L = np.array([-0.4, 0.7, 0.6]); L /= np.linalg.norm(L)


def render(t, bounds=None):
    tr = tris_at(t)
    proj = [((p) @ Rv.T, uv) for p, uv in tr]
    allp = np.concatenate([p for p, _ in proj])
    if bounds is None:
        bounds = (allp[:, 0].min(), allp[:, 0].max(), allp[:, 1].min(), allp[:, 1].max())
    x0, x1, y0, y1 = bounds
    W, H = int((x1 - x0) * SC) + 20, int((y1 - y0) * SC) + 20
    img = np.full((H, W, 3), 238, np.uint8)
    zb = np.full((H, W), -1e9)
    for (p, uv), (pw, _) in zip(proj, tr):
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
        n = np.cross(pw[1] - pw[0], pw[2] - pw[0])
        n = Rv @ (n / max(np.linalg.norm(n), 1e-9))
        lit = 0.62 + 0.38 * abs(float(n @ L))
        upd = m & (z > zb[gy, gx])
        zb[gy[upd], gx[upd]] = z[upd]
        img[gy[upd], gx[upd]] = np.clip(col[upd] * lit, 0, 255).astype(np.uint8)
    return img, bounds


# one fixed frame for all times so motion is comparable
ts = [float(x) for x in times.split(",")]
first = tris_at(ts[0])
b0 = None
frames = []
allb = []
for t in ts:
    tr = tris_at(t)
    proj = np.concatenate([(p @ Rv.T) for p, _ in tr])
    allb.append((proj[:, 0].min(), proj[:, 0].max(), proj[:, 1].min(), proj[:, 1].max()))
bb = (min(b[0] for b in allb), max(b[1] for b in allb), min(b[2] for b in allb), max(b[3] for b in allb))
for t in ts:
    img, _ = render(t, bb)
    im = Image.fromarray(img)
    ImageDraw.Draw(im).text((6, 4), f"t={t:.2f}s", fill=(0, 0, 0))
    frames.append(im)
cols = min(len(frames), 3)
rows = (len(frames) + cols - 1) // cols
w, h = frames[0].size
sheet = Image.new("RGB", (w * cols, h * rows), (238, 238, 238))
for i, f in enumerate(frames):
    sheet.paste(f, ((i % cols) * w, (i // cols) * h))
sheet.save(out)
print("saved", out, sheet.size)
