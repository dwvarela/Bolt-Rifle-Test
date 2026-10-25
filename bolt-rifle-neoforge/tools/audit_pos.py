"""Position / scale audit with the first-person camera model (verified for ADS centring).

Reads the REAL numbers from src/main/java/.../Guns.java (SCALE, hold(...), aim(...) calls) - nothing is typed in twice - computes the hip
transform exactly like the Java does, then measures with the geo meshes:
  * scale (hip scale factor, and ratio to a reference commit's value)
  * fraction of the rear stock (model z > stock_z) that is inside the 70-degree / 16:9 frame (ignoring occlusion)
  * fraction of grip + hands + action + front end that is inside the frame
  * screen position of the muzzle / receiver / grip / butt (pixels of a 960x540 frame)
Usage: audit_pos.py [gun ...]   (default: bolt_rifle m14ebr)
Camera: c = H + t + s*(-x/16, y/16 + 0.01, z/16), H = (0.56,-0.52,-0.72), looks along -z, vertical FOV 70.
"""
import json, math, os, re, sys
import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
JAVA = os.path.join(HERE, "..", "src", "main", "java", "com", "example", "boltrifle", "Guns.java")
RES = os.path.join(HERE, "..", "src", "main", "resources")
H0 = np.array([0.56, -0.52, -0.72])
W, HH = 960, 540
F = (HH / 2) / math.tan(math.radians(35))


def parse(java_text):
    scale = float(re.search(r"SCALE\s*=\s*([0-9.]+)", java_text).group(1))
    out = {}
    for m in re.finditer(r"private static GunDef (\w+)\(\)\s*\{(.*?)\n\t\}", java_text, re.S):
        body = m.group(2)
        gid = re.search(r'new GunDef\("(\w+)"', body)
        h = re.search(r"\bhold\(d,\s*([0-9.]+),\s*([0-9.]+)(?:,\s*([-0-9.]+),\s*([-0-9.]+),\s*([-0-9.]+)(?:,\s*([-0-9.]+),\s*([-0-9.]+),\s*([-0-9.]+))?)?\)", body)
        if gid and h:
            butt, s = float(h.group(1)), float(h.group(2))
            dx = float(h.group(3) or 0)
            dy = float(h.group(4) or 0)
            dz = float(h.group(5) or 0)
            rv = tuple(float(h.group(i) or 0) for i in (6, 7, 8))
            out[gid.group(1)] = (butt, s, dx, dy, dz) + rv
    return scale, out


def hip_xf(scale, butt, s, dx, dy, dz, ver):
    s *= scale
    if ver == "8662b2b":                      # what the stale v7 config file kept on the player's machine
        return s, -0.40 + 0.5 * s, -0.05 + 0.5 * s, 0.50 - butt * s / 16
    return s, -0.40 + 0.5 * s + dx, -0.06 + 0.5 * s + dy, 0.95 - butt * s / 16 + dz


def load_pts(gid, n=40000, seed=1):
    geo = json.load(open(os.path.join(RES, "assets/boltrifle/geo/item/%s.geo.json" % gid)))["minecraft:geometry"][0]
    rng = np.random.default_rng(seed)
    pts = {}
    for b in geo["bones"]:
        tris = []
        pm = b.get("poly_mesh")
        if pm:
            P = np.array(pm["positions"]).reshape(-1, 3)
            for poly in pm["polys"]:
                tris.append(P[[poly[0][0], poly[1][0], poly[2][0]]])
        for cu in b.get("cubes", []):
            o, s = np.array(cu["origin"], float), np.array(cu["size"], float)
            c = np.array([[o[0] + dx * s[0], o[1] + dy * s[1], o[2] + dz * s[2]] for dx in (0, 1) for dy in (0, 1) for dz in (0, 1)])
            for f in ((0, 1, 3, 2), (4, 5, 7, 6), (0, 1, 5, 4), (2, 3, 7, 6), (0, 2, 6, 4), (1, 3, 7, 5)):
                q = c[list(f)]
                tris += [q[[0, 1, 2]], q[[0, 2, 3]]]
        if not tris:
            continue
        T = np.array(tris)
        area = np.linalg.norm(np.cross(T[:, 1] - T[:, 0], T[:, 2] - T[:, 0]), axis=1) / 2 + 1e-12
        k = max(200, int(n * area.sum() / 2000))
        idx = rng.choice(len(T), size=k, p=area / area.sum())
        r1, r2 = rng.random(k), rng.random(k)
        sw = r1 + r2 > 1
        r1[sw], r2[sw] = 1 - r1[sw], 1 - r2[sw]
        pts[b["name"]] = T[idx, 0] + (T[idx, 1] - T[idx, 0]) * r1[:, None] + (T[idx, 2] - T[idx, 0]) * r2[:, None]
    return pts


def project(p, xf, rv=(0, 0, 0)):
    import fp_cov as _C
    s, tx, ty, tz = xf
    c = (_C._R(*rv) @ (np.stack([-p[:, 0] / 16, p[:, 1] / 16 + 0.01, p[:, 2] / 16], 1) * s).T).T + H0 + np.array([tx, ty, tz])
    front = c[:, 2] < -0.05
    z = np.where(front, -c[:, 2], 1.0)
    sx = W / 2 + F * c[:, 0] / z
    sy = HH / 2 - F * c[:, 1] / z
    inside = front & (sx >= 0) & (sx <= W) & (sy >= 0) & (sy <= HH)
    return sx, sy, inside, front


def report(gid, scale, par, ver, stock_z, label):
    butt, s, dx, dy, dz = par[:5]
    xf = hip_xf(scale, butt, s, dx, dy, dz, ver)
    pts = load_pts(gid)
    res = {"label": label, "xf": tuple(round(x, 4) for x in xf)}
    rear = []
    front_ = []
    for name, p in pts.items():
        if name in ("muzzle_flash", "casing", "chamber_round", "left_hand", "right_hand", "magazine"):
            continue
        sx, sy, ins, fr = project(p, xf)
        sel_rear = p[:, 2] > stock_z
        if sel_rear.any():
            rear.append(ins[sel_rear])
        if (~sel_rear).any():
            front_.append(ins[~sel_rear])
    rear = np.concatenate(rear) if rear else np.zeros(1, bool)
    front_ = np.concatenate(front_)
    res["rear_stock_visible"] = round(float(rear.mean()), 3)
    res["front_part_visible"] = round(float(front_.mean()), 3)
    hv = {}
    for nm in ("left_hand", "right_hand"):
        if nm in pts:
            hv[nm] = round(float(project(pts[nm], xf)[2].mean()), 3)
    res["hands_visible"] = hv
    # key points (model coords -> pixels)
    kp = {}
    for nm, pt in (("muzzle", (0, 0, -34)), ("receiver", (0, 0, 0)), ("grip", (0, -4, 10)), ("butt", (0, -2, butt))):
        sx, sy, ins, fr = project(np.array([pt], float), xf)
        kp[nm] = (int(sx[0]), int(sy[0]), bool(ins[0]))
    res["pixels"] = kp
    return res


if __name__ == "__main__":
    txt = open(JAVA).read()
    scale, table = parse(txt)
    ids = sys.argv[1:] or ["bolt_rifle", "m14ebr"]
    STOCK_Z = {"bolt_rifle": 13.0, "m14ebr": 13.0}
    print("SCALE in Guns.java =", scale)
    for gid in ids:
        par = table[gid]
        for ver, label in (("8662b2b", "OLD (what the stale config kept)"), ("now", "NEW (Guns.java)")):
            sc = 0.99 if ver == "8662b2b" else scale
            r = report(gid, sc, par, ver, STOCK_Z.get(gid, 13.0), label)
            print(gid, json.dumps(r))
        old = hip_xf(0.99, *par[:5], "8662b2b")
        new = hip_xf(scale, *par[:5], "now")
        print("   scale ratio new/old = %.3f   y %+.3f   z %+.3f (bigger z = closer to the player)" % (new[0] / old[0], new[2] - old[2], new[3] - old[3]))
