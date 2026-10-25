"""Fast screen-share estimate (no occlusion) of the stock, hands etc. for a hold transform with optional yaw/pitch/roll."""
import json, math, os
import numpy as np
import audit_pos as A

W, HH, F, H0 = A.W, A.HH, A.F, A.H0


def rotm(rx, ry, rz):
    def R(ax, a):
        c, s = math.cos(math.radians(a)), math.sin(math.radians(a))
        return {"x": np.array([[1, 0, 0], [0, c, -s], [0, s, c]]), "y": np.array([[c, 0, s], [0, 1, 0], [-s, 0, c]]), "z": np.array([[c, -s, 0], [s, c, 0], [0, 0, 1]])}[ax]
    return R("y", ry) @ R("x", rx) @ R("z", rz)        # same order as the renderer: Y, X, Z


def load_tris(gid, bones):
    geo = json.load(open(os.path.join(A.RES, "assets/boltrifle/geo/item/%s.geo.json" % gid)))["minecraft:geometry"][0]
    out = []
    for b in geo["bones"]:
        if b["name"] not in bones:
            continue
        pm = b.get("poly_mesh")
        if pm:
            P = np.array(pm["positions"]).reshape(-1, 3)
            for poly in pm["polys"]:
                out.append(P[[poly[0][0], poly[1][0], poly[2][0]]])
        for cu in b.get("cubes", []):
            o, s = np.array(cu["origin"], float), np.array(cu["size"], float)
            c = np.array([[o[0] + dx * s[0], o[1] + dy * s[1], o[2] + dz * s[2]] for dx in (0, 1) for dy in (0, 1) for dz in (0, 1)])
            for f in ((0, 1, 3, 2), (4, 5, 7, 6), (0, 1, 5, 4), (2, 3, 7, 6), (0, 2, 6, 4), (1, 3, 7, 5)):
                q = c[list(f)]
                out += [q[[0, 1, 2]], q[[0, 2, 3]]]
    return np.array(out)


def prep(tris, n=60000, seed=2):
    """area-weighted surface samples with normals (model space)"""
    rng = np.random.default_rng(seed)
    nrm = np.cross(tris[:, 1] - tris[:, 0], tris[:, 2] - tris[:, 0])
    ar = np.linalg.norm(nrm, axis=1) / 2 + 1e-12
    nrm = nrm / (2 * ar[:, None])
    idx = rng.choice(len(tris), size=n, p=ar / ar.sum())
    r1, r2 = rng.random(n), rng.random(n)
    sw = r1 + r2 > 1
    r1[sw], r2[sw] = 1 - r1[sw], 1 - r2[sw]
    P = tris[idx, 0] + (tris[idx, 1] - tris[idx, 0]) * r1[:, None] + (tris[idx, 2] - tris[idx, 0]) * r2[:, None]
    return P, nrm[idx], ar.sum() / n          # points, normals, area per sample (px^2 model)


def share(P, N, area, xf, rv=(0, 0, 0)):
    """fraction of the frame the surface would cover (front-facing, in front of the near plane, inside the frame, no occlusion)"""
    s, tx, ty, tz = xf
    R = rotm(*rv)
    q = np.stack([-P[:, 0] / 16, P[:, 1] / 16 + 0.01, P[:, 2] / 16], 1) * s
    c = (R @ q.T).T + H0 + np.array([tx, ty, tz])
    nq = np.stack([-N[:, 0], N[:, 1], N[:, 2]], 1)          # mirrored normal
    nc = (R @ nq.T).T
    d = -c[:, 2]
    ok = d > 0.05
    dirv = c / np.maximum(np.linalg.norm(c, axis=1, keepdims=True), 1e-9)
    facing = -(nc * dirv).sum(1)                            # >0 when the surface faces the eye
    ok &= facing > 0
    sx = W / 2 + F * c[:, 0] / np.where(ok, d, 1)
    sy = HH / 2 - F * c[:, 1] / np.where(ok, d, 1)
    ok &= (sx >= 0) & (sx < W) & (sy >= 0) & (sy < HH)
    a_world = area / 256.0 * s * s                         # px^2 -> blocks^2, scaled
    proj = a_world * facing / np.maximum(np.linalg.norm(c, axis=1), 1e-9) ** 2 * (F * F)   # pixels^2 on screen
    return float((proj * ok).sum() / (W * HH)), ok


def inframe(Pts, xf, rv=(0, 0, 0)):
    s, tx, ty, tz = xf
    R = rotm(*rv)
    q = np.stack([-Pts[:, 0] / 16, Pts[:, 1] / 16 + 0.01, Pts[:, 2] / 16], 1) * s
    c = (R @ q.T).T + H0 + np.array([tx, ty, tz])
    d = -c[:, 2]
    ok = d > 0.05
    sx = W / 2 + F * c[:, 0] / np.where(ok, d, 1)
    sy = HH / 2 - F * c[:, 1] / np.where(ok, d, 1)
    return ok & (sx >= 0) & (sx < W) & (sy >= 0) & (sy < HH), sx, sy
