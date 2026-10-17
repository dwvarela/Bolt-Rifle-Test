"""Signed-distance-field modelling kit.  Units: 1 px = 1/16 block (same as gunlib).  Barrel = -Z, up = +Y.

A Vol is a dense float grid (negative = inside).  Primitives evaluate their distance on a sub-grid and are merged
(add = union, sub = subtract, both optionally smooth).  Material ids are stored per voxel so the baker can colour each part.

Rotation convention (matches gunlib.slope): rot=[('x', a)] tips the TOP of the primitive toward the muzzle (-Z) for a > 0.
"""
import math
import numpy as np
import cv2
from scipy import ndimage


# ------------------------------------------------------------------ helpers
def _rot(axis, deg):
    a = math.radians(deg)
    c, s = math.cos(a), math.sin(a)
    if axis == "x":      # top (+y) toward -z for +deg
        return np.array([[1, 0, 0], [0, c, -s], [0, s, c]], float)
    if axis == "y":      # nose (-z) toward +x(shooter's left) for +deg
        return np.array([[c, 0, s], [0, 1, 0], [-s, 0, c]], float)
    return np.array([[c, -s, 0], [s, c, 0], [0, 0, 1]], float)


def rot_matrix(rot):
    R = np.eye(3)
    for ax, deg in (rot or []):
        R = _rot(ax, deg) @ R
    return R


def _local(X, Y, Z, c, R):
    """World grid -> local coordinates of a primitive centred at c and rotated by R."""
    if R is None:
        return X - c[0], Y - c[1], Z - c[2]
    X, Y, Z = np.broadcast_arrays(X, Y, Z)
    px, py, pz = X - c[0], Y - c[1], Z - c[2]
    # local = R^T p
    return (R[0, 0] * px + R[1, 0] * py + R[2, 0] * pz,
            R[0, 1] * px + R[1, 1] * py + R[2, 1] * pz,
            R[0, 2] * px + R[1, 2] * py + R[2, 2] * pz)


def _aabb(c, half, R):
    c = np.array(c, float)
    half = np.array(half, float)
    if R is None:
        return c - half, c + half
    corners = np.array([[sx, sy, sz] for sx in (-1, 1) for sy in (-1, 1) for sz in (-1, 1)]) * half
    w = corners @ R.T + c
    return w.min(0), w.max(0)


def smin(a, b, k):
    h = np.clip(0.5 + 0.5 * (b - a) / k, 0, 1)
    return b * (1 - h) + a * h - k * h * (1 - h)


def smax(a, b, k):
    return -smin(-a, -b, k)


# ------------------------------------------------------------------ primitives
class Box:
    def __init__(self, c, half, r=0.0, rot=None):
        self.c, self.half, self.r, self.R = np.array(c, float), np.array(half, float), r, (rot_matrix(rot) if rot else None)

    def bounds(self):
        return _aabb(self.c, self.half, self.R)

    def d(self, X, Y, Z):
        x, y, z = _local(X, Y, Z, self.c, self.R)
        r = min(self.r, *self.half)
        qx, qy, qz = np.abs(x) - self.half[0] + r, np.abs(y) - self.half[1] + r, np.abs(z) - self.half[2] + r
        out = np.sqrt(np.maximum(qx, 0) ** 2 + np.maximum(qy, 0) ** 2 + np.maximum(qz, 0) ** 2)
        return out + np.minimum(np.maximum(np.maximum(qx, qy), qz), 0) - r


def box(x0, x1, y0, y1, z0, z1, r=0.0, rot=None):
    """Axis-aligned box from min/max corners (px)."""
    return Box(((x0 + x1) / 2, (y0 + y1) / 2, (z0 + z1) / 2), ((x1 - x0) / 2, (y1 - y0) / 2, (z1 - z0) / 2), r, rot)


class Cyl:
    """Cylinder / frustum from point a to point b, radii r0 -> r1, edge rounding rr."""

    def __init__(self, a, b, r0, r1=None, rr=0.0):
        self.a, self.b = np.array(a, float), np.array(b, float)
        self.r0, self.r1 = r0, (r0 if r1 is None else r1)
        self.rr = rr
        v = self.b - self.a
        self.L = float(np.linalg.norm(v))
        self.w = v / self.L

    def bounds(self):
        r = max(self.r0, self.r1)
        return np.minimum(self.a, self.b) - r, np.maximum(self.a, self.b) + r

    def d(self, X, Y, Z):
        X, Y, Z = np.broadcast_arrays(X, Y, Z)
        m = (self.a + self.b) / 2
        px, py, pz = X - m[0], Y - m[1], Z - m[2]
        t = px * self.w[0] + py * self.w[1] + pz * self.w[2]
        rx, ry, rz = px - t * self.w[0], py - t * self.w[1], pz - t * self.w[2]
        rad = np.sqrt(rx * rx + ry * ry + rz * rz)
        f = t / self.L + 0.5                                     # 0..1 along the axis
        rt = self.r0 + (self.r1 - self.r0) * np.clip(f, 0, 1)
        slope = (self.r1 - self.r0) / self.L
        dr = (rad - rt) / math.sqrt(1 + slope * slope)
        dt = np.abs(t) - self.L / 2
        rr = min(self.rr, self.L / 2, max(self.r0, self.r1))
        qx, qy = dr + rr, dt + rr
        return np.sqrt(np.maximum(qx, 0) ** 2 + np.maximum(qy, 0) ** 2) + np.minimum(np.maximum(qx, qy), 0) - rr


def cylz(cx, cy, z0, z1, r0, r1=None, rr=0.0):
    return Cyl((cx, cy, z0), (cx, cy, z1), r0, r1, rr)


class Ell:
    def __init__(self, c, radii, rot=None):
        self.c, self.rad, self.R = np.array(c, float), np.array(radii, float), (rot_matrix(rot) if rot else None)

    def bounds(self):
        return _aabb(self.c, self.rad, self.R)

    def d(self, X, Y, Z):
        x, y, z = _local(X, Y, Z, self.c, self.R)
        k0 = np.sqrt((x / self.rad[0]) ** 2 + (y / self.rad[1]) ** 2 + (z / self.rad[2]) ** 2)
        k1 = np.sqrt((x / self.rad[0] ** 2) ** 2 + (y / self.rad[1] ** 2) ** 2 + (z / self.rad[2] ** 2) ** 2)
        return k0 * (k0 - 1.0) / np.maximum(k1, 1e-6)


class Sil:
    """2-D signed-distance image built from polygons (outer contours + holes) in a plane (u, v)."""

    def __init__(self, polys, res=0.04, pad=1.5):
        # polys: list of (outer, [holes]) with point lists of (u, v)
        pts = np.array([p for outer, _ in polys for p in outer], float)
        self.u0, self.v0 = pts[:, 0].min() - pad, pts[:, 1].min() - pad
        self.res = res
        w = int((pts[:, 0].max() + pad - self.u0) / res) + 2
        h = int((pts[:, 1].max() + pad - self.v0) / res) + 2
        img = np.zeros((h, w), np.uint8)
        for outer, holes in polys:
            cv2.fillPoly(img, [self._pix(outer)], 255, shift=4)
            for hole in holes:
                cv2.fillPoly(img, [self._pix(hole)], 0, shift=4)
        inside = img > 0
        din = ndimage.distance_transform_edt(inside)
        dout = ndimage.distance_transform_edt(~inside)
        self.sd = (np.where(inside, -(din - 0.5), dout - 0.5) * res).astype(np.float32)
        self.shape = (h, w)
        self.lo = np.array([self.u0, self.v0])
        self.hi = np.array([self.u0 + w * res, self.v0 + h * res])

    def _pix(self, pts):
        a = np.array(pts, float)
        return np.round((a - [self.u0, self.v0]) / self.res * 16).astype(np.int32).reshape(-1, 1, 2)

    def sample(self, U, V):
        U, V = np.broadcast_arrays(U, V)
        cu = (U - self.u0) / self.res - 0.5
        cv = (V - self.v0) / self.res - 0.5
        out = ndimage.map_coordinates(self.sd, [cv.ravel(), cu.ravel()], order=1, mode="nearest").reshape(U.shape)
        # outside the image: grow linearly so the field stays valid
        du = np.maximum(np.maximum(self.u0 - U, U - self.hi[0]), 0)
        dv = np.maximum(np.maximum(self.v0 - V, V - self.hi[1]), 0)
        return out + np.sqrt(du * du + dv * dv)


class Ext:
    """Extrude a silhouette between two coordinates along the remaining axis, with edge rounding r.
    plane 'zy': silhouette in (z, y), extruded along x.  'zx': (z, x) along y.  'xy': (x, y) along z."""

    def __init__(self, sil, plane, a0, a1, r=0.0):
        self.sil, self.plane, self.a0, self.a1, self.r = sil, plane, a0, a1, r

    def bounds(self):
        s = self.sil
        lo, hi = s.lo, s.hi
        if self.plane == "zy":
            return np.array([self.a0, lo[1], lo[0]]), np.array([self.a1, hi[1], hi[0]])
        if self.plane == "zx":
            return np.array([lo[1], self.a0, lo[0]]), np.array([hi[1], self.a1, hi[0]])
        return np.array([lo[0], lo[1], self.a0]), np.array([hi[0], hi[1], self.a1])

    def d(self, X, Y, Z):
        if self.plane == "zy":
            d2, e = self.sil.sample(Z, Y), X
        elif self.plane == "zx":
            d2, e = self.sil.sample(Z, X), Y
        else:
            d2, e = self.sil.sample(X, Y), Z
        d2, e = np.broadcast_arrays(d2, e)
        hw = (self.a1 - self.a0) / 2
        r = min(self.r, hw)
        qx = d2 + r
        qy = np.abs(e - (self.a0 + self.a1) / 2) - hw + r
        return np.sqrt(np.maximum(qx, 0) ** 2 + np.maximum(qy, 0) ** 2) + np.minimum(np.maximum(qx, qy), 0) - r


class Loft:
    """Body lofted along Z through cross-sections [(z, y0, y1, half_width, rounding)] (rounded rectangles)."""

    def __init__(self, sections):
        self.s = np.array(sections, float)

    def bounds(self):
        s = self.s
        hw = s[:, 3].max()
        return np.array([-hw, s[:, 1].min(), s[:, 0].min()]), np.array([hw, s[:, 2].max(), s[:, 0].max()])

    def d(self, X, Y, Z):
        X, Y, Z = np.broadcast_arrays(X, Y, Z)
        s = self.s
        zc = np.clip(Z, s[0, 0], s[-1, 0])
        y0 = np.interp(zc, s[:, 0], s[:, 1])
        y1 = np.interp(zc, s[:, 0], s[:, 2])
        hw = np.interp(zc, s[:, 0], s[:, 3])
        rr = np.interp(zc, s[:, 0], s[:, 4])
        hy = (y1 - y0) / 2
        cy = (y1 + y0) / 2
        rr = np.minimum(rr, np.minimum(hw, hy))
        qx, qy = np.abs(X) - hw + rr, np.abs(Y - cy) - hy + rr
        dxy = np.sqrt(np.maximum(qx, 0) ** 2 + np.maximum(qy, 0) ** 2) + np.minimum(np.maximum(qx, qy), 0) - rr
        dz = np.maximum(s[0, 0] - Z, Z - s[-1, 0])
        return np.sqrt(np.maximum(dxy, 0) ** 2 + np.maximum(dz, 0) ** 2) + np.minimum(np.maximum(dxy, dz), 0)


class Clip:
    """Limit a primitive to a window in z / y / x (lets different parts of one traced outline have different widths)."""

    def __init__(self, prim, z0=-99.0, z1=99.0, y0=-99.0, y1=99.0, x0=-99.0, x1=99.0):
        self.p, self.z0, self.z1, self.y0, self.y1, self.x0, self.x1 = prim, z0, z1, y0, y1, x0, x1

    def bounds(self):
        lo, hi = self.p.bounds()
        lo, hi = np.array(lo, float), np.array(hi, float)
        lo[0], hi[0] = max(lo[0], self.x0), min(hi[0], self.x1)
        lo[1], hi[1] = max(lo[1], self.y0), min(hi[1], self.y1)
        lo[2], hi[2] = max(lo[2], self.z0), min(hi[2], self.z1)
        return lo, hi

    def d(self, X, Y, Z):
        d = self.p.d(X, Y, Z)
        z = 0 * d
        return np.maximum.reduce([d, self.z0 - Z + z, Z - self.z1 + z, self.y0 - Y + z, Y - self.y1 + z,
                                  self.x0 - X + z, X - self.x1 + z])


class Traced:
    """A silhouette traced from a reference photo (tools/trace_side.py JSON) as a Sil with its holes."""

    @staticmethod
    def load(path, res=0.03, min_area=60, keep=None):
        import json
        data = json.load(open(path))
        outers = [(np.array(c["pts"], np.float32), c) for c in data if not c["hole"] and c["area"] >= min_area]
        holes = [np.array(c["pts"], np.float32) for c in data if c["hole"]]
        if keep is not None:      # drop dark-but-not-see-through patches the tracer mistook for holes
            holes = [h for h in holes if keep(h.mean(0), np.ptp(h, axis=0))]
        polys = []
        for pts, c in outers:
            hs = []
            for h in holes:
                if cv2.pointPolygonTest(pts.reshape(-1, 1, 2), (float(h[0][0]), float(h[0][1])), False) > 0:
                    hs.append([tuple(p) for p in h])
            polys.append(([tuple(p) for p in pts], hs))
        return Sil(polys, res=res)


# ------------------------------------------------------------------ volume
class Vol:
    def __init__(self, lo, hi, h):
        self.lo = np.array(lo, float)
        self.h = float(h)
        self.n = np.ceil((np.array(hi, float) - self.lo) / self.h).astype(int) + 1
        self.d = np.full(tuple(self.n), 4.0, np.float32)
        self.m = np.zeros(tuple(self.n), np.uint8)
        self.decals = []          # (prim, mat): colour overrides evaluated per texel (screws, markings, stripes)

    def paint(self, prim, mat):
        self.decals.append((prim, mat))
        return self

    def _slice(self, bmin, bmax, pad):
        i0 = np.maximum(np.floor((np.array(bmin) - pad - self.lo) / self.h).astype(int), 0)
        i1 = np.minimum(np.ceil((np.array(bmax) + pad - self.lo) / self.h).astype(int) + 1, self.n)
        if np.any(i1 <= i0):
            return None
        ax = [self.lo[k] + np.arange(i0[k], i1[k]) * self.h for k in range(3)]
        sl = tuple(slice(int(a), int(b)) for a, b in zip(i0, i1))
        return sl, ax[0][:, None, None], ax[1][None, :, None], ax[2][None, None, :]

    def add(self, prim, mat=1, k=0.0):
        bmin, bmax = prim.bounds()
        s = self._slice(bmin, bmax, k + 2 * self.h)
        if s is None:
            return self
        sl, X, Y, Z = s
        d = np.broadcast_to(prim.d(X, Y, Z), self.d[sl].shape).astype(np.float32)
        cur = self.d[sl]
        new = smin(cur, d, k) if k > 0 else np.minimum(cur, d)
        take = d < cur + (k * 0.25 if k > 0 else 0)
        mm = self.m[sl]
        mm[take] = mat
        self.m[sl] = mm
        self.d[sl] = new.astype(np.float32)
        return self

    def sub(self, prim, k=0.0):
        bmin, bmax = prim.bounds()
        s = self._slice(bmin, bmax, k + 2 * self.h)
        if s is None:
            return self
        sl, X, Y, Z = s
        d = np.broadcast_to(prim.d(X, Y, Z), self.d[sl].shape).astype(np.float32)
        cur = self.d[sl]
        self.d[sl] = (smax(cur, -d, k) if k > 0 else np.maximum(cur, -d)).astype(np.float32)
        return self

    def intersect_box(self, prim):
        """Keep only the part inside prim (used to trim lofts etc.)."""
        s = self._slice(*prim.bounds(), 0)
        sl, X, Y, Z = s
        d = np.broadcast_to(prim.d(X, Y, Z), self.d[sl].shape).astype(np.float32)
        self.d[sl] = np.maximum(self.d[sl], d)
        return self

    def sample(self, pts):
        """Trilinear sample at world points (N,3)."""
        idx = (np.asarray(pts, float) - self.lo) / self.h
        return ndimage.map_coordinates(self.d, idx.T, order=1, mode="nearest")

    def empty(self):
        return not np.any(self.d < 0)
