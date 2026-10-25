"""Hand-vs-gun clipping audit. Usage: clip_check.py <res_dir> <gun> <anim> t0 t1 [dt]
Voxelises the gun (all bones except hands + magazine, posed at each time), flood-fills the outside, and counts hand-surface samples that lie
inside the solid (>= `depth` voxels under the surface). Prints per-time counts; a clean animation prints 0 everywhere."""
import sys, numpy as np
from scipy import ndimage
import fp_cov as C

VOX = 0.35
HANDS = ("left_hand", "right_hand"); SKIP = HANDS + ("magazine", "muzzle_flash", "casing", "chamber_round")


def posed(bones, tri, an, name, t, memo):
    M = C.world(bones, an, name, t, memo)
    return ((M[:3, :3] @ tri[name].reshape(-1, 3).T).T + M[:3, 3]).reshape(-1, 3, 3)


def sample(T, step):
    a, b, c = T[:, 0], T[:, 1], T[:, 2]
    area = np.linalg.norm(np.cross(b - a, c - a), axis=1) / 2
    out = [a, b, c, (a + b + c) / 3]
    k = np.maximum(1, np.ceil(np.sqrt(area) / step)).astype(int)
    for kk in range(2, int(min(k.max(), 40)) + 1):
        sel = k >= kk
        if not sel.any():
            continue
        for i in range(kk + 1):
            for j in range(kk + 1 - i):
                u, v = i / kk, j / kk
                out.append(a[sel] + (b[sel] - a[sel]) * u + (c[sel] - a[sel]) * v)
    return np.concatenate(out)


def count(res, gid, anim, t, bones=None):
    C._cache.clear()
    bones, tri, ani = C.load(gid, res)
    an = ani["animation.%s.%s" % (gid, anim)]
    memo = {}
    gun = np.concatenate([sample(posed(bones, tri, an, n, t, memo), VOX * 0.6) for n in tri if n not in SKIP])
    hand = np.concatenate([sample(posed(bones, tri, an, n, t, memo), 0.5) for n in HANDS if n in tri])
    lo = np.minimum(gun.min(0), hand.min(0)) - 2; hi = np.maximum(gun.max(0), hand.max(0)) + 2
    shape = np.ceil((hi - lo) / VOX).astype(int)
    G = np.zeros(shape, bool)
    idx = np.floor((gun - lo) / VOX).astype(int)
    G[idx[:, 0], idx[:, 1], idx[:, 2]] = True
    Gc = ndimage.binary_closing(G, iterations=1)
    solid = ndimage.binary_fill_holes(Gc)
    core = ndimage.binary_erosion(solid, iterations=2)
    hi_ = np.floor((hand - lo) / VOX).astype(int)
    inside = core[hi_[:, 0], hi_[:, 1], hi_[:, 2]]
    return int(inside.sum()), len(hand), (hand[inside].mean(0) if inside.any() else None)


if __name__ == "__main__":
    res, gid, anim = sys.argv[1:4]
    t0, t1 = float(sys.argv[4]), float(sys.argv[5]); dt = float(sys.argv[6]) if len(sys.argv) > 6 else 0.1
    t = t0
    while t <= t1 + 1e-9:
        n, tot, m = count(res, gid, anim, t)
        print("t=%.2f  hand samples deep inside the gun: %d / %d%s" % (t, n, tot, ("   at mean (%.1f,%.1f,%.1f)" % tuple(m)) if m is not None else ""))
        t += dt
