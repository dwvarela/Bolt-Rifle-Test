"""SDF volumes -> decimated triangle meshes + orthographic baked texture maps -> geo.json poly_mesh bones.

Pipeline per mesh bone: marching cubes on its Vol -> quadric edge-collapse decimation -> 6 orthographic albedo maps
(rays cast through the bone's own volume; ambient occlusion and edge wear sampled from the whole gun) -> each triangle is
UV-mapped into the map whose axis best matches its normal.  The maps are packed into the same atlas as the cube faces
(hands, flash, ...) by gunlib.Model.write(extras=...).
"""
import heapq
import json
import math
import os
import numpy as np
from PIL import Image
from scipy import ndimage
from skimage import measure

import gunlib
from gunlib import Model, MATS, FACE_LIGHT
import sdf

MAT_NAMES = ["none", "steel", "gunmetal", "black", "stainless", "scope", "poly", "rubber", "brass", "wood", "plum",
             "glove", "lens", "olive", "tan", "smoke", "walnut", "amber", "p90", "synth", "alu", "bluing", "bakelite"]
MAT_EXTRA = {
    "alu": ((52, 54, 58), "metal"), "bluing": ((34, 40, 52), "metal"), "bakelite": ((120, 56, 26), "bakelite"),
}
ALL_MATS = dict(MATS)
ALL_MATS.update(MAT_EXTRA)
ALL_MATS["glove"] = ((70, 68, 60), "cloth")            # charcoal-olive tactical gloves (meshes only)


def mid(name):
    return MAT_NAMES.index(name)


# ---------------------------------------------------------------------------------------------- decimation (QEM)
def decimate(V, F, target):
    V = V.astype(np.float64).copy()
    F = F.astype(np.int64).copy()
    nf = len(F)
    if nf <= target:
        return V, F
    a, b, c = V[F[:, 0]], V[F[:, 1]], V[F[:, 2]]
    n = np.cross(b - a, c - a)
    area = np.linalg.norm(n, axis=1)
    ok = area > 1e-12
    n[ok] /= area[ok, None]
    dd = -np.einsum("ij,ij->i", n, a)
    p = np.concatenate([n, dd[:, None]], axis=1)
    K = np.einsum("fi,fj->fij", p, p) * (area[:, None, None] * 0.5)
    Q = np.zeros((len(V), 4, 4))
    for k in range(3):
        np.add.at(Q, F[:, k], K)
    vf = [set() for _ in range(len(V))]
    for i, f in enumerate(F):
        for v in f:
            vf[v].add(i)
    alive = np.ones(nf, bool)
    ver = np.zeros(len(V), np.int64)
    vdead = np.zeros(len(V), bool)

    def cost(i, j):
        Qs = Q[i] + Q[j]
        A = Qs.copy()
        A[3] = [0, 0, 0, 1]
        best = None
        try:
            if abs(np.linalg.det(A)) > 1e-9:
                x = np.linalg.solve(A, np.array([0, 0, 0, 1.0]))
                best = x[:3]
        except np.linalg.LinAlgError:
            best = None
        cands = [V[i], V[j], (V[i] + V[j]) / 2] if best is None else [best, V[i], V[j]]
        bc, bp = None, None
        for pt in cands:
            h = np.append(pt, 1.0)
            e = float(h @ Qs @ h)
            if bc is None or e < bc:
                bc, bp = e, pt
        return bc, bp

    heap = []
    cnt = 0
    edges = set()
    for f in F:
        for x, y in ((f[0], f[1]), (f[1], f[2]), (f[2], f[0])):
            edges.add((min(x, y), max(x, y)))
    for i, j in edges:
        c_, p_ = cost(i, j)
        heapq.heappush(heap, (c_, cnt, i, j, ver[i], ver[j], p_))
        cnt += 1
    nalive = nf

    def fnormal(fi, repl=None, pos=None):
        f = F[fi]
        pts = []
        for v in f:
            pts.append(pos if (repl is not None and v in repl) else V[v])
        return np.cross(pts[1] - pts[0], pts[2] - pts[0])

    while nalive > target and heap:
        c_, _, i, j, vi, vj, pos = heapq.heappop(heap)
        if vdead[i] or vdead[j] or ver[i] != vi or ver[j] != vj:
            continue
        shared = vf[i] & vf[j]
        if len(shared) != 2:
            continue                                   # keep the mesh 2-manifold around the edge
        bad = False
        for fi in (vf[i] | vf[j]) - shared:
            n0 = fnormal(fi)
            n1 = fnormal(fi, {i, j}, pos)
            l0, l1 = np.linalg.norm(n0), np.linalg.norm(n1)
            if l1 < 1e-9 or (l0 > 1e-12 and np.dot(n0, n1) / (l0 * l1) < 0.25):
                bad = True
                break
        if bad:
            continue
        # collapse j into i
        for fi in shared:
            alive[fi] = False
            nalive -= 1
            for v in F[fi]:
                vf[v].discard(fi)
        for fi in list(vf[j]):
            F[fi][F[fi] == j] = i
            vf[i].add(fi)
        vf[j] = set()
        vdead[j] = True
        V[i] = pos
        Q[i] = Q[i] + Q[j]
        ver[i] += 1
        nb = set()
        for fi in vf[i]:
            for v in F[fi]:
                if v != i:
                    nb.add(int(v))
        for k in nb:
            c2, p2 = cost(min(i, k), max(i, k))
            a_, b_ = min(i, k), max(i, k)
            heapq.heappush(heap, (c2, cnt, a_, b_, ver[a_], ver[b_], p2))
            cnt += 1
    Fa = F[alive]
    used = np.unique(Fa)
    remap = -np.ones(len(V), np.int64)
    remap[used] = np.arange(len(used))
    return V[used], remap[Fa]


# ---------------------------------------------------------------------------------------------- noise helpers
def _hash3(x, y, z, seed=0):
    h = np.sin(x * 127.1 + y * 311.7 + z * 74.7 + seed * 19.19) * 43758.5453
    return h - np.floor(h)


def vnoise(x, y, z, seed=0):
    xi, yi, zi = np.floor(x), np.floor(y), np.floor(z)
    xf, yf, zf = x - xi, y - yi, z - zi
    xf, yf, zf = xf * xf * (3 - 2 * xf), yf * yf * (3 - 2 * yf), zf * zf * (3 - 2 * zf)
    out = 0
    for dx in (0, 1):
        for dy in (0, 1):
            for dz in (0, 1):
                w = (xf if dx else 1 - xf) * (yf if dy else 1 - yf) * (zf if dz else 1 - zf)
                out = out + w * _hash3(xi + dx, yi + dy, zi + dz, seed)
    return out


# ---------------------------------------------------------------------------------------------- albedo
def shade(matid, P, N, ao, wear, rng):
    """Albedo for texels. P (n,3) world points, N (n,3) normals, ao 0..1, wear 0..1 (convex-edge amount)."""
    n = len(P)
    col = np.zeros((n, 3))
    names = np.array(MAT_NAMES)[matid]
    noise = rng.normal(0, 1, (n, 1))
    for name in np.unique(names):
        sel = names == name
        if name == "none":
            col[sel] = (40, 40, 40)
            continue
        base, kind = ALL_MATS[name]
        base = np.array(base, float)
        px, py, pz = P[sel, 0:1], P[sel, 1:2], P[sel, 2:3]
        c = np.ones((sel.sum(), 1)) * base
        nn = noise[sel]
        if kind in ("metal", "bright"):
            fine = vnoise(px * 6, py * 6, pz * 1.3, 3)
            c = c * (1 + 0.025 * nn + 0.14 * (fine - 0.5))
            bare = np.array([150, 150, 154]) if kind == "metal" else np.array([200, 202, 206])
            w = wear[sel][:, None]
            c = c * (1 - 0.45 * w) + bare * 0.45 * w * (0.7 + 0.3 * vnoise(px * 10, py * 10, pz * 10, 5))
        elif kind == "poly":
            fine = vnoise(px * 3, py * 3, pz * 3, 8)
            c = c * (1 + 0.012 * nn + 0.05 * (fine - 0.5))
            c = c * (1 + 0.12 * wear[sel][:, None])
        elif kind == "rubber":
            c = c * (1 + 0.06 * nn + 0.2 * (vnoise(px * 7, py * 7, pz * 7, 4) - 0.5))
        elif kind == "wood":
            warp = 0.9 * vnoise(px * 0.6, py * 0.6, pz * 0.35, 2) + 0.35 * vnoise(px * 2, py * 2, pz, 6)
            g = np.sin((py * 2.2 + px * 1.3 + warp * 3.2) * 2.4)
            g2 = np.sin((py * 5.1 - px * 2.0 + warp * 5.0) * 1.8)
            c = c * ((1 + 0.18 * g + 0.09 * g2) * (1 + 0.03 * nn))
            c = c * (1 - 0.18 * wear[sel][:, None])
            c = c * np.array([1.0, 1.0, 1.0])
        elif kind == "bakelite":
            c = c * (1 + 0.06 * nn + 0.35 * (vnoise(px * 1.5, py * 1.5, pz * 1.5, 9) - 0.5))
        elif kind == "brass":
            c = c * (0.85 + 0.35 * vnoise(px * 5, py * 5, pz * 5, 1)) * (1 + 0.03 * nn)
        elif kind == "cloth":
            c = c * (1 + 0.02 * nn + 0.05 * (vnoise(px * 5, py * 5, pz * 5, 3) - 0.5))
        elif kind == "lens":
            c = c * (0.8 + 0.4 * (1 - np.abs(N[sel, 2:3])))
        elif kind == "glow":
            c = c * 1.0
        else:
            c = c * (1 + 0.04 * nn)
        col[sel] = c
    col = col * (0.42 + 0.58 * ao[:, None])
    return np.clip(col, 0, 255)


# ---------------------------------------------------------------------------------------------- baking
VIEWS = {  # name: (u_axis, v_axis, w_axis, from_positive)
    "px": (2, 1, 0, True), "nx": (2, 1, 0, False),
    "py": (0, 2, 1, True), "ny": (0, 2, 1, False),
    "pz": (0, 1, 2, True), "nz": (0, 1, 2, False),
}


def first_hit(D, axis, from_pos):
    Dm = np.moveaxis(D, axis, 0)
    n = Dm.shape[0]
    if from_pos:
        Dm = Dm[::-1]
    neg = Dm < 0
    hit = neg.any(0)
    idx = neg.argmax(0)
    prev = np.clip(idx - 1, 0, n - 1)
    a, b = np.take_along_axis(Dm, prev[None], 0)[0], np.take_along_axis(Dm, idx[None], 0)[0]
    t = np.clip(a / np.maximum(a - b, 1e-6), 0, 1)
    pos_idx = (idx - 1 + t)                         # fractional index in the scan order
    if from_pos:
        gi = (n - 1) - idx                          # grid index of the first inside voxel
        gf = (n - 1) - pos_idx
    else:
        gi, gf = idx, pos_idx
    hit &= idx > 0
    return hit, gi, gf


def bake_bone(vol, full, tx, rng, wanted):
    """Return {view: dict(img (H,W,4) uint8, u0, v1, tx)} for the views in `wanted`."""
    D = vol.d
    gx, gy, gz = np.gradient(D)
    lap = ndimage.laplace(D) / (vol.h * vol.h)
    res = {}
    inside = np.argwhere(D < 0)
    if len(inside) == 0:
        return res
    bmin = vol.lo + inside.min(0) * vol.h
    bmax = vol.lo + inside.max(0) * vol.h
    for name in wanted:
        ua, va, wa, fp = VIEWS[name]
        u0, u1 = bmin[ua] - 0.4, bmax[ua] + 0.4
        v0, v1 = bmin[va] - 0.4, bmax[va] + 0.4
        W = int(math.ceil((u1 - u0) * tx)) + 1
        H = int(math.ceil((v1 - v0) * tx)) + 1
        hit, gi, gf = first_hit(D, wa, fp)
        # texel centres -> columns of the remaining two axes
        uk = u0 + (np.arange(W) + 0.5) / tx
        vl = v1 - (np.arange(H) + 0.5) / tx
        ju = np.clip(np.round((uk - vol.lo[ua]) / vol.h).astype(int), 0, vol.n[ua] - 1)
        jv = np.clip(np.round((vl - vol.lo[va]) / vol.h).astype(int), 0, vol.n[va] - 1)
        rem = [a for a in range(3) if a != wa]            # axes of hit arrays, in increasing order
        # hit arrays are indexed [rem[0], rem[1]]
        if ua == rem[0]:
            A_idx, B_idx = ju[None, :].repeat(H, 0), jv[:, None].repeat(W, 1)
        else:
            A_idx, B_idx = jv[:, None].repeat(W, 1), ju[None, :].repeat(H, 0)
        h_ok = hit[A_idx, B_idx]
        if not h_ok.any():
            continue
        gi_t, gf_t = gi[A_idx, B_idx], gf[A_idx, B_idx]
        # voxel index triple of the hit
        vox = np.zeros((H, W, 3), int)
        vox[..., rem[0]], vox[..., rem[1]], vox[..., wa] = A_idx, B_idx, gi_t
        Pw = np.zeros((H, W, 3))
        Pw[..., ua] = uk[None, :]
        Pw[..., va] = vl[:, None]
        Pw[..., wa] = vol.lo[wa] + gf_t * vol.h
        sel = h_ok.ravel()
        P = Pw.reshape(-1, 3)[sel]
        v3 = vox.reshape(-1, 3)[sel]
        N = np.stack([gx[v3[:, 0], v3[:, 1], v3[:, 2]], gy[v3[:, 0], v3[:, 1], v3[:, 2]], gz[v3[:, 0], v3[:, 1], v3[:, 2]]], 1)
        N = N / np.maximum(np.linalg.norm(N, axis=1, keepdims=True), 1e-9)
        M = vol.m[v3[:, 0], v3[:, 1], v3[:, 2]]
        L = lap[v3[:, 0], v3[:, 1], v3[:, 2]]
        wear = np.clip((L - 0.9) / 2.2, 0, 1)
        occl = np.zeros(len(P))
        for k, s in enumerate((0.12, 0.25, 0.45, 0.8, 1.3)):
            dk = full.sample(P + N * s)
            occl += np.clip(s - dk, 0, None) / (2.0 ** k)
        ao = np.clip(1.0 - 0.85 * occl, 0.12, 1.0)
        M = M.astype(int)
        for prim, dm in vol.decals:
            inside_d = prim.d(P[:, 0], P[:, 1], P[:, 2])
            M = np.where(inside_d < 0, mid(dm) if isinstance(dm, str) else dm, M)
        col = shade(M, P, N, ao, wear, rng)
        img = np.zeros((H * W, 4), np.uint8)
        img[sel, :3] = col.astype(np.uint8)
        img[sel, 3] = 255
        img = img.reshape(H, W, 4)
        # dilate into empty texels so bilinear filtering never bleeds the background
        mask = img[..., 3] > 0
        idx = ndimage.distance_transform_edt(~mask, return_distances=False, return_indices=True)
        img = img[idx[0], idx[1]]
        img[..., 3] = 255
        res[name] = dict(img=img, u0=u0, v1=v1, tx=tx)
    return res


def extract_mesh(vol, target_tris):
    d = vol.d
    if not (d < 0).any():
        return None
    lab, n = ndimage.label(d < 0, structure=np.ones((3, 3, 3)))        # drop floating specks (tracing noise), keep every real part
    if n > 1:
        sizes = ndimage.sum(np.ones_like(lab), lab, index=np.arange(1, n + 1))
        small = np.isin(lab, 1 + np.where(sizes < 150)[0])
        if small.any():
            print("   removed %d floating specks" % int((sizes < 150).sum()), end="")
            d = d.copy()
            d[small] = vol.h
            vol.d = d
    verts, faces, _, _ = measure.marching_cubes(d, level=1e-4, spacing=(vol.h,) * 3)   # tiny offset: no exact-zero samples -> no sliver triangles to drop (dropping them left holes)
    verts = verts + vol.lo
    # drop degenerate triangles
    a, b, c = verts[faces[:, 0]], verts[faces[:, 1]], verts[faces[:, 2]]
    keep = np.linalg.norm(np.cross(b - a, c - a), axis=1) > 1e-10
    print("   (%d zero-area tris kept)" % int((~keep).sum()), end="")
    print("   marching cubes: %d tris" % len(faces), end="")
    verts, faces = decimate(verts, faces, target_tris)
    print(" -> %d tris" % len(faces))
    return verts, faces


class MModel(Model):
    """Model with SDF mesh bones.  m.mesh('body', parent='rifle', pivot=(0,0,0)) -> Vol to model into (shared grid)."""

    def __init__(self, ident, lo, hi, h=0.2, seed=3, tx=10):
        super().__init__(ident, seed)
        self.grid = (lo, hi, h)
        self.vols = {}
        self.tx = tx
        self.tris = {}

    def mesh(self, name, parent="rifle", pivot=(0, 0, 0), tris=6000):
        if name not in self.bones:
            self.bone(name, parent, pivot)
        v = sdf.Vol(*self.grid)
        self.vols[name] = v
        self.tris[name] = tris
        return v

    def write(self, res, texture=True):
        rng = np.random.default_rng(self.seed + 1)
        names = list(self.vols)
        full = sdf.Vol(*self.grid)
        full.d = np.minimum.reduce([self.vols[n].d for n in names]) if names else full.d
        meshes, maps = {}, {}
        for n in names:
            print(" bone", n)
            mm = extract_mesh(self.vols[n], self.tris[n])
            if mm is None:
                continue
            V, F = mm
            meshes[n] = (V, F)
            # which views are needed
            a, b, c = V[F[:, 0]], V[F[:, 1]], V[F[:, 2]]
            fn = np.cross(b - a, c - a)
            fn /= np.maximum(np.linalg.norm(fn, axis=1, keepdims=True), 1e-12)
            ctr = (a + b + c) / 3
            e = 0.05
            grad = np.stack([self.vols[n].sample(ctr + [e, 0, 0]) - self.vols[n].sample(ctr - [e, 0, 0]),
                             self.vols[n].sample(ctr + [0, e, 0]) - self.vols[n].sample(ctr - [0, e, 0]),
                             self.vols[n].sample(ctr + [0, 0, e]) - self.vols[n].sample(ctr - [0, 0, e])], 1)
            flip = np.einsum("ij,ij->i", fn, grad) < 0
            fn[flip] *= -1
            F[flip] = F[flip][:, [0, 2, 1]]
            meshes[n] = (V, F, fn, ctr)
            ax = np.abs(fn).argmax(1)
            sgn = np.sign(fn[np.arange(len(fn)), ax])
            views = sorted({("p" if s > 0 else "n") + "xyz"[a_] for a_, s in zip(ax, sgn)})
            maps[n] = bake_bone(self.vols[n], full, self.tx, rng, views)
        extras = []
        for n, mv in maps.items():
            for vn, info in mv.items():
                extras.append(((n, vn), info["img"]))
        place = {}
        meshdata = {}

        def hook(geo, placements, W):
            for n, (V, F, fn, ctr) in meshes.items():
                mv = maps[n]
                ax = np.abs(fn).argmax(1)
                sgn = np.sign(fn[np.arange(len(fn)), ax])
                pos, uvs, polys, nrm = [], [], [], []
                vmap = {}
                for fi in range(len(F)):
                    order = np.argsort(-np.abs(fn[fi]))
                    vn = None
                    for o in order:
                        cand = ("p" if fn[fi][o] > 0 else "n") + "xyz"[o]
                        if cand in mv:
                            vn = cand
                            break
                    if vn is None:
                        continue
                    info = mv[vn]
                    ua, va, wa, fp = VIEWS[vn]
                    px0, py0 = placements[(n, vn)]
                    ni = len(nrm)
                    nrm.append([round(float(x), 3) for x in fn[fi]])
                    poly = []
                    for k in F[fi]:
                        key = int(k)
                        if key not in vmap:
                            vmap[key] = len(pos)
                            pos.append([round(float(x), 3) for x in V[key]])
                        u = (px0 + (V[key][ua] - info["u0"]) * info["tx"]) / W
                        v = (py0 + (info["v1"] - V[key][va]) * info["tx"]) / W
                        uvs.append([round(float(u), 5), round(float(v), 5)])
                        poly.append([vmap[key], ni, len(uvs) - 1])
                    polys.append(poly)
                bone = next(b for b in geo["minecraft:geometry"][0]["bones"] if b["name"] == n)
                bone["poly_mesh"] = {
                    "normalized_uvs": True,
                    "positions": [c for p in pos for c in p],
                    "normals": [c for q in nrm for c in q],
                    "uvs": [c for p in uvs for c in p],
                    "polys": polys,
                }
                print("   %s: %d tris, %d verts" % (n, len(polys), len(pos)))
            geo["minecraft:geometry"][0]["description"]["texture_height"] = W

        super().write(res, texture, extras=extras, geo_hook=hook)
