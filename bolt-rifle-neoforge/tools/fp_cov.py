"""Screen-coverage audit (rasterised, z-buffered, same camera as fp_render): how many pixels of the first-person frame each part of the gun covers.
Library: coverage(gid, xf, anim=None, t=0.0) -> dict(group -> share of the 960x540 frame) and label image.
Groups: stock (stock + buttstock bones), hands, magazine, rest (barrel, receiver, bolt, sights...).
"""
import json, math, os
import numpy as np
from PIL import Image

HERE = os.path.dirname(os.path.abspath(__file__))
RES = os.path.join(HERE, "..", "src", "main", "resources")
H0 = np.array([0.56, -0.52, -0.72])
W, HH = 960, 540
F = (HH / 2) / math.tan(math.radians(35))
GROUPS = {"stock": ("stock", "buttstock"), "hands": ("left_hand", "right_hand"), "mag": ("magazine",)}
COLORS = {"stock": (200, 60, 60), "hands": (230, 200, 60), "mag": (60, 160, 60), "rest": (90, 110, 200), "sky": (120, 160, 200), "rear": (255, 0, 255)}
HIDE = ("muzzle_flash", "casing", "chamber_round")


def rot(ax, ay, az):
    a, b, c = (math.radians(-ax), math.radians(-ay), math.radians(az))
    Rx = np.array([[1, 0, 0], [0, math.cos(a), -math.sin(a)], [0, math.sin(a), math.cos(a)]])
    Ry = np.array([[math.cos(b), 0, math.sin(b)], [0, 1, 0], [-math.sin(b), 0, math.cos(b)]])
    Rz = np.array([[math.cos(c), -math.sin(c), 0], [math.sin(c), math.cos(c), 0], [0, 0, 1]])
    Sm = np.diag([-1.0, 1, 1])
    return Sm @ (Rz @ Ry @ Rx) @ Sm


def chan_of(an, bone, name, t, default):
    fr = (an or {}).get("bones", {}).get(bone, {}).get(name)
    if not fr:
        return np.array(default, float)
    ks = sorted((float(k), np.array(v["vector"] if isinstance(v, dict) else v, float)) for k, v in fr.items())
    if t <= ks[0][0]:
        return ks[0][1]
    for (t0, v0), (t1, v1) in zip(ks, ks[1:]):
        if t0 <= t <= t1:
            return v0 + (v1 - v0) * ((t - t0) / (t1 - t0) if t1 > t0 else 1.0)
    return ks[-1][1]


_cache = {}


def load(gid, res=RES):
    key = (gid, res)
    if key in _cache:
        return _cache[key]
    geo = json.load(open(os.path.join(res, "assets/boltrifle/geo/item/%s.geo.json" % gid)))["minecraft:geometry"][0]
    bones = {b["name"]: b for b in geo["bones"]}
    tri = {}
    for n, b in bones.items():
        T = []
        pm = b.get("poly_mesh")
        if pm:
            P = np.array(pm["positions"]).reshape(-1, 3)
            for poly in pm["polys"]:
                T.append(P[[poly[0][0], poly[1][0], poly[2][0]]])
        for cu in b.get("cubes", []):
            o, s = np.array(cu["origin"], float), np.array(cu["size"], float)
            c = np.array([[o[0] + dx * s[0], o[1] + dy * s[1], o[2] + dz * s[2]] for dx in (0, 1) for dy in (0, 1) for dz in (0, 1)])
            for f in ((0, 1, 3, 2), (4, 5, 7, 6), (0, 1, 5, 4), (2, 3, 7, 6), (0, 2, 6, 4), (1, 3, 7, 5)):
                q = c[list(f)]
                T += [q[[0, 1, 2]], q[[0, 2, 3]]]
        if T:
            tri[n] = np.array(T)
    ani = None
    p = os.path.join(res, "assets/boltrifle/animations/item/%s.animation.json" % gid)
    if os.path.exists(p):
        ani = json.load(open(p))["animations"]
    _cache[key] = (bones, tri, ani)
    return _cache[key]


def world(bones, an, name, t, memo):
    if name in memo:
        return memo[name]
    b = bones[name]
    M = world(bones, an, b["parent"], t, memo) if b.get("parent") else np.eye(4)
    piv = np.array(b.get("pivot", [0, 0, 0]), float)
    L = np.eye(4); L[:3, 3] = chan_of(an, name, "position", t, [0, 0, 0])
    P = np.eye(4); P[:3, 3] = piv
    Pi = np.eye(4); Pi[:3, 3] = -piv
    R = np.eye(4); R[:3, :3] = rot(*chan_of(an, name, "rotation", t, [0, 0, 0])) @ np.diag(chan_of(an, name, "scale", t, [1, 1, 1]))
    memo[name] = M @ L @ P @ R @ Pi
    return memo[name]


def _R(rx, ry, rz):
    def R(ax, a):
        c, s_ = math.cos(math.radians(a)), math.sin(math.radians(a))
        return {'x': np.array([[1, 0, 0], [0, c, -s_], [0, s_, c]]), 'y': np.array([[c, 0, s_], [0, 1, 0], [-s_, 0, c]]), 'z': np.array([[c, -s_, 0], [s_, c, 0], [0, 0, 1]])}[ax]
    return R('y', ry) @ R('x', rx) @ R('z', rz)


def _clip(tr, zn=-0.05):
    """clip a camera-space triangle against the near plane z = zn (visible side z < zn); returns 0-2 triangles"""
    inside = [p[2] < zn for p in tr]
    n = sum(inside)
    if n == 3:
        return [tr]
    if n == 0:
        return []
    pts = []
    for i in range(3):
        a, b = tr[i], tr[(i + 1) % 3]
        ia, ib = a[2] < zn, b[2] < zn
        if ia:
            pts.append(a)
        if ia != ib:
            k = (zn - a[2]) / (b[2] - a[2])
            pts.append(a + (b - a) * k)
    if len(pts) == 3:
        return [np.array(pts)]
    return [np.array([pts[0], pts[1], pts[2]]), np.array([pts[0], pts[2], pts[3]])]


def coverage(gid, xf, anim=None, t=0.0, res=RES, want_image=False, rv=(0, 0, 0), rear_z=13.0):
    bones, tri, ani = load(gid, res)
    an = ani.get("animation.%s.%s" % (gid, anim)) if (anim and ani) else None
    s, tx, ty, tz = xf
    lab = np.zeros((HH, W), np.int8)
    zb = np.full((HH, W), 1e9)
    names = ["sky", "stock", "hands", "mag", "rest", "rear"]
    memo = {}
    for n, T in tri.items():
        if n in HIDE:
            continue
        sc = chan_of(an, n, "scale", t, [1, 1, 1])
        if np.all(sc == 0):
            continue
        g = "rest"
        for k, v in GROUPS.items():
            if n in v:
                g = k
        gi = names.index(g)
        M = world(bones, an, n, t, memo)
        Pw = (M[:3, :3] @ T.reshape(-1, 3).T).T + M[:3, 3]
        c = (_R(*rv) @ (np.stack([-Pw[:, 0] / 16, Pw[:, 1] / 16 + 0.01, Pw[:, 2] / 16], 1) * s).T).T + H0 + np.array([tx, ty, tz])
        c = c.reshape(-1, 3, 3)
        zc = Pw[:, 2].reshape(-1, 3).mean(1) if g == 'stock' else None
        for ti, tr0 in enumerate(c):
            gi = names.index('rear') if (g == 'stock' and zc[ti] > rear_z) else names.index(g)
            for tr in _clip(tr0):
                sx = W / 2 + F * tr[:, 0] / -tr[:, 2]
                sy = HH / 2 - F * tr[:, 1] / -tr[:, 2]
                x0, x1 = int(max(sx.min(), 0)), int(min(sx.max() + 1, W - 1))
                y0, y1 = int(max(sy.min(), 0)), int(min(sy.max() + 1, HH - 1))
                if x1 < x0 or y1 < y0:
                    continue
                gx, gy = np.meshgrid(np.arange(x0, x1 + 1), np.arange(y0, y1 + 1))
                d = (sy[1] - sy[2]) * (sx[0] - sx[2]) + (sx[2] - sx[1]) * (sy[0] - sy[2])
                if abs(d) < 1e-9:
                    continue
                l0 = ((sy[1] - sy[2]) * (gx + .5 - sx[2]) + (sx[2] - sx[1]) * (gy + .5 - sy[2])) / d
                l1 = ((sy[2] - sy[0]) * (gx + .5 - sx[2]) + (sx[0] - sx[2]) * (gy + .5 - sy[2])) / d
                l2 = 1 - l0 - l1
                m = (l0 >= 0) & (l1 >= 0) & (l2 >= 0)
                if not m.any():
                    continue
                z = l0 * -tr[0, 2] + l1 * -tr[1, 2] + l2 * -tr[2, 2]
                upd = m & (z < zb[gy, gx])
                zb[gy[upd], gx[upd]] = z[upd]
                lab[gy[upd], gx[upd]] = gi
    out = {n: float((lab == i).mean()) for i, n in enumerate(names)}
    if want_image:
        img = np.zeros((HH, W, 3), np.uint8)
        for i, n in enumerate(names):
            img[lab == i] = COLORS[n]
        return out, Image.fromarray(img)
    return out
