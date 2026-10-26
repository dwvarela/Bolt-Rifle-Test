"""Load a GLB (uncompressed glTF binary) as world-space triangle parts and turn parts into signed-distance volumes for meshbake.
Used for the AK-47 (model by GoldbergR on Sketchfab - see CREDITS.md)."""
import json, struct
import numpy as np
from scipy import ndimage
from scipy.spatial import cKDTree


def load_parts(path):
    d = open(path, "rb").read(); off = 12; js = None; bn = b""
    while off < len(d):
        n, t = struct.unpack_from("<II", d, off); c = d[off + 8:off + 8 + n]; off += 8 + n
        if t == 0x4E4F534A: js = json.loads(c)
        elif t == 0x004E4942: bn = c

    def acc(i):
        a = js["accessors"][i]; bv = js["bufferViews"][a["bufferView"]]
        dt = {5126: np.float32, 5123: np.uint16, 5125: np.uint32, 5121: np.uint8}[a["componentType"]]
        k = {"SCALAR": 1, "VEC3": 3, "VEC2": 2, "VEC4": 4}[a["type"]]
        o = bv.get("byteOffset", 0) + a.get("byteOffset", 0); st = bv.get("byteStride")
        if st and st != k * np.dtype(dt).itemsize:
            return np.ndarray((a["count"], k), dt, bn, o, (st, np.dtype(dt).itemsize)).copy()
        return np.frombuffer(bn, dt, a["count"] * k, o).reshape(-1, k)

    def local(nd):
        if "matrix" in nd: return np.array(nd["matrix"]).reshape(4, 4).T
        M = np.eye(4)
        if "scale" in nd: M = np.diag(list(nd["scale"]) + [1]) @ M
        if "rotation" in nd:
            x, y, z, w = nd["rotation"]
            R = np.array([[1 - 2 * (y * y + z * z), 2 * (x * y - z * w), 2 * (x * z + y * w)], [2 * (x * y + z * w), 1 - 2 * (x * x + z * z), 2 * (y * z - x * w)], [2 * (x * z - y * w), 2 * (y * z + x * w), 1 - 2 * (x * x + y * y)]])
            T = np.eye(4); T[:3, :3] = R; M = T @ M
        if "translation" in nd:
            T = np.eye(4); T[:3, 3] = nd["translation"]; M = T @ M
        return M

    parts = []

    def walk(i, P, path_names):
        nd = js["nodes"][i]; M = P @ local(nd); names = path_names + [nd.get("name", "")]
        if "mesh" in nd:
            for pr in js["meshes"][nd["mesh"]]["primitives"]:
                V = acc(pr["attributes"]["POSITION"]).astype(float); V = (M[:3, :3] @ V.T).T + M[:3, 3]
                F = acc(pr["indices"]).reshape(-1, 3).astype(int)
                parts.append(dict(name=nd.get("name", ""), path=names, V=V, F=F, mat=pr.get("material")))
        for c in nd.get("children", []): walk(c, M, names)

    for r in js["scenes"][js.get("scene", 0)]["nodes"]: walk(r, np.eye(4), [])
    return parts, js


def surface_points(V, F, step):
    a, b, c = V[F[:, 0]], V[F[:, 1]], V[F[:, 2]]
    area = np.linalg.norm(np.cross(b - a, c - a), axis=1) / 2
    out = [a, b, c, (a + b + c) / 3]
    k = np.clip(np.ceil(np.sqrt(area) / step), 1, 60).astype(int)
    for kk in range(2, int(k.max()) + 1):
        sel = k >= kk
        for i in range(kk + 1):
            for j in range(kk + 1 - i):
                u, v = i / kk, j / kk
                if u + v <= 1 + 1e-9:
                    out.append(a[sel] + (b[sel] - a[sel]) * u + (c[sel] - a[sel]) * v)
    return np.concatenate(out)


def add_part(vol, V, F, mat):
    """Write the signed distance of one closed-ish part into the shared grid volume `vol` (meshbake Vol)."""
    h = vol.h
    pts = surface_points(V, F, h * 0.4)
    tree = cKDTree(pts)
    lo = V.min(0) - 3 * h; hi = V.max(0) + 3 * h
    i0 = np.maximum(np.floor((lo - vol.lo) / h).astype(int), 0); i1 = np.minimum(np.ceil((hi - vol.lo) / h).astype(int) + 1, vol.n)
    if np.any(i1 <= i0):
        return
    ax = [vol.lo[k] + np.arange(i0[k], i1[k]) * h for k in range(3)]
    G = np.stack(np.meshgrid(*ax, indexing="ij"), -1).reshape(-1, 3)
    du, _ = tree.query(G)
    du = du.reshape(i1 - i0)
    shell = du < h * 0.8
    solid = ndimage.binary_fill_holes(shell)
    sd = np.where(solid, -np.maximum(du, 0.02 * h), du).astype(np.float32)
    sl = tuple(slice(int(a), int(b)) for a, b in zip(i0, i1))
    cur = vol.d[sl]
    take = sd < cur
    vol.m[sl][take] = mat
    vol.d[sl] = np.minimum(cur, sd)
