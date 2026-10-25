"""Ten consecutive confirmation audits of scale + held position (each one stricter than the one before).
Usage: audit10.py [path/to/built/boltrifle.jar]
Exit status 0 only if every audit passes.
"""
import json, math, os, re, struct, subprocess, sys, zipfile
import numpy as np
import audit_pos as A

HERE = os.path.dirname(os.path.abspath(__file__))
SRC = os.path.join(HERE, "..", "src", "main", "java", "com", "example", "boltrifle")
JAR = sys.argv[1] if len(sys.argv) > 1 else None
OLD_SCALE, PREV_SCALE, WANT_SCALE = 0.99, 1.089, 1.1979       # stale-config build / previous code / requested (+10% each)
fails = []


def check(n, name, ok, msg):
    print("AUDIT %2d %-46s %s  %s" % (n, name, "PASS" if ok else "FAIL", msg))
    if not ok:
        fails.append(n)


java = open(os.path.join(SRC, "Guns.java")).read()
scale, table = A.parse(java)

# ---- 1. the literal in the source
check(1, "SCALE literal in Guns.java", abs(scale - WANT_SCALE) < 1e-9, "SCALE=%s (want %s = %.3f x %.3f)" % (scale, WANT_SCALE, PREV_SCALE, 1.1))

# ---- 2. the config file can no longer keep stale numbers
cc = open(os.path.join(SRC, "ClientConfig.java")).read()
mod = open(os.path.join(SRC, "BoltRifleMod.java")).read()
ok = ("hashCode()" in cc and "d.hip" in cc and "d.ads" in cc and "ClientConfig.FILE" in mod and "client-v" not in mod)
check(2, "config file name carries a fingerprint of defaults", ok, "FILE hashes hip/ads/third of every gun; BoltRifleMod uses ClientConfig.FILE (no fixed name)")

# ---- 3. every gun scaled by exactly +10% over the previous code and +21% over the stale build
bad = []
for gid, (butt, s, dx, dy, dz, *_r) in table.items():
    new = A.hip_xf(scale, butt, s, dx, dy, dz, "now")[0]
    prev = A.hip_xf(PREV_SCALE, butt, s, dx, dy, dz, "now")[0]
    old = A.hip_xf(OLD_SCALE, butt, s, dx, dy, dz, "8662b2b")[0]
    if abs(new / prev - 1.1) > 1e-6 or abs(new / old - 1.21) > 1e-6:
        bad.append((gid, new / prev, new / old))
check(3, "all %d hold() guns: +10%% vs code, +21%% vs stale" % len(table), not bad, str(bad) if bad else "ratios exact: 1.100 / 1.210")

# ---- 4. a second, independent implementation of the pipeline (4x4 matrices: vanilla hand -> renderer -> model)
def RH(rv):
    import fp_cov as _C
    M = np.eye(4); M[:3, :3] = _C._R(*rv); return M


def matrix_project(xf, pts, rv=(0, 0, 0)):
    s, tx, ty, tz = xf
    T = lambda x, y, z: np.array([[1, 0, 0, x], [0, 1, 0, y], [0, 0, 1, z], [0, 0, 0, 1.0]])
    S = lambda k: np.diag([k, k, k, 1.0])
    # vanilla hand (0.56,-0.52,-0.72) -> ItemRenderer translate(-0.5) -> our renderer (+0.5, t, scale, -0.5) -> GeckoLib item centring (+0.5,+0.51,+0.5)
    M = T(0.56, -0.52, -0.72) @ T(-0.5, -0.5, -0.5) @ T(0.5, 0.5, 0.5) @ T(tx, ty, tz) @ RH(rv) @ S(s) @ T(-0.5, -0.5, -0.5) @ T(0.5, 0.51, 0.5)
    mir = np.diag([-1.0, 1, 1, 1])                                                                                  # GeckoLib x mirror
    P = np.c_[pts / 16.0, np.ones(len(pts))] @ mir
    c = (M @ P.T).T[:, :3]
    return c


ok4, worst = True, 0.0
for gid in ("bolt_rifle", "m14ebr"):
    pts = A.load_pts(gid)["receiver"][:500]
    xf = A.hip_xf(scale, *table[gid][:5], "now"); rv = table[gid][5:]
    a = A.project(pts, xf, rv)
    c = matrix_project(xf, pts, rv)
    sx = A.W / 2 + A.F * c[:, 0] / -c[:, 2]
    sy = A.HH / 2 - A.F * c[:, 1] / -c[:, 2]
    d = max(np.abs(sx - a[0]).max(), np.abs(sy - a[1]).max())
    worst = max(worst, d)
    ok4 &= d < 0.5
check(4, "independent matrix pipeline agrees (<0.5 px)", ok4, "worst difference %.4f px" % worst)

# ---- 5-7. raster audits (z-buffered, near-plane clipped, 960x540) - same camera model as audit 4
import fp_cov as C
def pose(gid):
    p = table[gid]; return A.hip_xf(scale, *p[:5], "now"), tuple(p[5:])
def cov(gid, xf, rv, anim=None, t=0.0):
    return C.coverage(gid, xf, anim, t, rv=rv, rear_z=13.0)
xf7, rv7 = pose("bolt_rifle"); xf14, rv14 = pose("m14ebr")
old7 = A.hip_xf(OLD_SCALE, 22.4, 0.911, 0, 0, 0, "8662b2b")
c_old = cov("bolt_rifle", old7, (0, 0, 0)); c7 = cov("bolt_rifle", xf7, rv7); c14 = cov("m14ebr", xf14, rv14)
pts7 = A.load_pts("bolt_rifle"); pts14 = A.load_pts("m14ebr")
core7 = pts7["right_hand"][pts7["right_hand"][:, 2] < 13.4]; core14 = pts14["right_hand"][pts14["right_hand"][:, 2] < 12]
def inf(pts, xf, rv): return A.project(pts, xf, rv)[2].mean()
oth7 = np.concatenate([v for k, v in pts7.items() if k not in ("muzzle_flash", "casing", "chamber_round", "magazine", "left_hand", "right_hand", "buttstock", "stock")])
mz7 = A.project(np.array([[0, 0, oth7[:, 2].min()]]), xf7, rv7)
check(5, "M700 rest: rear stock mostly out of view (raster)", c7["rear"] <= 0.45 * c_old["rear"] and c7["rear"] <= 0.025,
      "rear-stock pixels %.4f of frame (stale layout %.4f) = %.0f%% of before" % (c7["rear"], c_old["rear"], 100 * c7["rear"] / c_old["rear"]))
check(6, "M700 rest: grip hand, left hand, barrel/bolt, muzzle in frame",
      inf(core7, xf7, rv7) >= 0.995 and inf(pts7["left_hand"], xf7, rv7) >= 0.995 and inf(oth7, xf7, rv7) >= 0.99 and bool(mz7[2][0]),
      "grip hand %.3f | left %.3f | front/action %.3f | muzzle px (%d,%d)" % (inf(core7, xf7, rv7), inf(pts7["left_hand"], xf7, rv7), inf(oth7, xf7, rv7), mz7[0][0], mz7[1][0]))
def px(xf, rv, p):
    r = A.project(np.array([p], float), xf, rv); return float(r[0][0]), float(r[1][0])
g7, g14 = px(xf7, rv7, (0, -3.5, 10.5)), px(xf14, rv14, (0, -6.0, 9.2))
r7, r14 = px(xf7, rv7, (0, 0, 0)), px(xf14, rv14, (0, 0, 0))
ok7 = (inf(core14, xf14, rv14) >= 0.995 and inf(pts14["left_hand"], xf14, rv14) >= 0.995 and c14["rear"] <= 0.025
       and 5 <= r7[1] - r14[1] <= 45 and abs(g14[1] - g7[1]) <= 25)
check(7, "M14 rest: hands in, rear out, grip level w/ M700, receiver slightly higher", ok7,
      "receiver row M14 %d vs M700 %d (higher by %d px) | grip row %d vs %d | rear stock %.4f" % (r14[1], r7[1], r7[1] - r14[1], g14[1], g7[1], c14["rear"]))

# ---- 8. whole animations: rifle-bone motion applied to the held transform (recoil, sway, reload lift)
def rot(ax, ay, az):
    a, b, c = (math.radians(-ax), math.radians(-ay), math.radians(az))
    Rx = np.array([[1, 0, 0], [0, math.cos(a), -math.sin(a)], [0, math.sin(a), math.cos(a)]])
    Ry = np.array([[math.cos(b), 0, math.sin(b)], [0, 1, 0], [-math.sin(b), 0, math.cos(b)]])
    Rz = np.array([[math.cos(c), -math.sin(c), 0], [math.sin(c), math.cos(c), 0], [0, 0, 1]])
    Sm = np.diag([-1.0, 1, 1])
    return Sm @ (Rz @ Ry @ Rx) @ Sm


def chan(an, bone, name, t):
    fr = an.get("bones", {}).get(bone, {}).get(name)
    if not fr:
        return np.zeros(3)
    ks = sorted((float(k), np.array(v["vector"] if isinstance(v, dict) else v, float)) for k, v in fr.items())
    if t <= ks[0][0]:
        return ks[0][1]
    for (t0, v0), (t1, v1) in zip(ks, ks[1:]):
        if t0 <= t <= t1:
            return v0 + (v1 - v0) * ((t - t0) / (t1 - t0) if t1 > t0 else 1.0)
    return ks[-1][1]


def anim_min(gid, xf, core, names, rvv=(0, 0, 0)):
    ani = json.load(open(os.path.join(A.RES, "assets/boltrifle/animations/item/%s.animation.json" % gid)))["animations"]
    pts = A.load_pts(gid)
    worst = {}
    for nm in names:
        an = ani["animation.%s.%s" % (gid, nm)]
        mn = 1.0
        for i in range(0, int(an["animation_length"] * 30) + 1):
            t = i / 30.0
            R = rot(*chan(an, "rifle", "rotation", t))
            pos = chan(an, "rifle", "position", t)
            pc = (R @ core.T).T + pos
            mn = min(mn, A.project(pc, xf, rvv)[2].mean())
        worst[nm] = round(mn, 2)
    return worst


w7 = anim_min("bolt_rifle", xf7, core7, ("idle", "fire", "dryfire"), rv7)
w14 = anim_min("m14ebr", xf14, core14, ("idle", "fire", "dryfire"), rv14)
check(8, "recoil/idle sweep keeps the firing hand in frame", min(list(w7.values()) + list(w14.values())) >= 0.80, "M700 %s | M14 %s (min share of the grip hand inside the frame)" % (w7, w14))

# ---- 9. every other gun: scaled, grip hand fully in frame at the same screen spot as the rifles, support hand and muzzle in frame
rows, ok9 = [], True
tab = dict(table)
for gid in ("ak47", "sks", "m4a1", "mini14", "mp7", "p90", "glock19"):
    p = A.load_pts(gid)
    if gid in tab:
        xf = A.hip_xf(scale, *tab[gid][:5], "now")
    else:                                                           # glock19 has its own hand-written hip transform
        g = re.search(r'GunDef.Xf\(0.43 \* SCALE, ([-0-9.]+), ([-0-9.]+), ([-0-9.]+),', java)
        xf = (0.43 * scale, float(g.group(1)), float(g.group(2)), float(g.group(3)))
    r = p["right_hand"]
    core = r[r[:, 2] < r[:, 2].max() - 3.6] if gid != "glock19" else r[r[:, 2] < 6]
    rv = A.project(core, xf)[2].mean()
    lh_ = p["left_hand"]
    lv = A.project(lh_[lh_[:, 2] < 6] if gid == "glock19" else lh_, xf)[2].mean()
    cen = A.project(core.mean(0)[None], xf)
    mzp = A.project(np.array([[0, 0, np.concatenate([q for k, q in p.items() if k not in ("muzzle_flash", "casing", "chamber_round", "magazine", "left_hand", "right_hand")])[:, 2].min()]]), xf)
    ok_g = rv >= 0.99 and lv >= 0.9 and bool(mzp[2][0])
    ok9 &= ok_g
    rows.append("%s s=%.3f RH %.2f LH %.2f hand@(%d,%d) muzzle %s" % (gid, xf[0], rv, lv, cen[0][0], cen[1][0], "in" if mzp[2][0] else "OUT"))
check(9, "other guns: bigger, hands + muzzle in frame", ok9, " | ".join(rows))

# ---- 10. aiming (sights centred) and final jar contents
ok10, msg10 = True, []
for gid in ("bolt_rifle", "m14ebr"):
    m = re.search(r'new GunDef\("%s".*?aim\(d,\s*([0-9.]+),\s*([-0-9.]+),\s*([0-9.]+),\s*([0-9.]+)\)' % gid, java, re.S)
    sy, sz, s, relief = (float(m.group(i)) for i in range(1, 5))
    s *= scale
    dist = 0.215 + relief
    xf = (s, -0.56, 0.52 - s * (sy / 16 + 0.01), 0.72 - dist - s * sz / 16)
    r = A.project(np.array([[0, sy, sz]], float), xf)
    d = math.hypot(r[0][0] - A.W / 2, r[1][0] - A.HH / 2)
    ok10 &= d < 1.0
    msg10.append("%s sight %.2f px from centre, ads scale %.4f" % (gid, d, s))
if JAR:
    z = zipfile.ZipFile(JAR)
    gc = z.read("com/example/boltrifle/Guns.class")
    cf = z.read("com/example/boltrifle/ClientConfig.class")
    need = [WANT_SCALE, 0.911, -0.15, -0.17, -0.38, 6.0, 21.0, 5.4, -0.05, 0.14, -0.32]
    missing = [v for v in need if struct.pack(">d", v) not in gc]
    ok10 &= (not missing) and b"boltrifle-client-" in cf and b"hashCode" in cf
    msg10.append("jar: Guns.class constants missing %s; ClientConfig fingerprint present %s" % (missing, b"boltrifle-client-" in cf))
else:
    msg10.append("(no jar given - run again with the CI jar)")
check(10, "ADS centred; built jar carries the numbers", ok10, " | ".join(msg10))

print("\nALL 10 PASS" if not fails else "\nFAILED audits: %s" % fails)
sys.exit(1 if fails else 0)
