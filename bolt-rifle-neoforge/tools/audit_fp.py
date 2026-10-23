"""Audits every animation of a gun in the first-person view: reports hand / magazine popping (appearing, vanishing or jumping while on screen).
Usage: audit_fp.py <res> <gun_id> <scale> <tx,ty,tz>"""
import sys, math, json, os
import numpy as np
res, gid, S, T = sys.argv[1:5]
S = float(S); T = np.array([float(x) for x in T.split(",")])
anims = json.load(open(f"{res}/assets/boltrifle/animations/item/{gid}.animation.json"))["animations"]
H = np.array([0.56, -0.52, -0.72]); W, Hh = 960, 540
f = (Hh / 2) / math.tan(math.radians(35))
bad = 0
for an in anims:
    name = an.split(".")[-1]
    if name.endswith("_b"):
        continue
    sys.argv = ["pose_render.py", res, gid, name, "0", "/dev/null", "side", "1", ""]
    src = open(os.path.join(os.path.dirname(os.path.abspath(__file__)), "pose_render.py")).read().split("# one fixed frame")[0]
    g = {}
    exec(src, g)
    length = g["ani"]["animation_length"]
    watch = [b for b in g["bones"] if b.startswith("mag") or "hand" in b and b not in ("bolt_handle",)]
    prev = {}
    t = 0.0
    while t <= length + 1e-9:
        cache = {}
        for b in watch:
            bone = g["bones"][b]
            if "poly_mesh" not in bone and not bone.get("cubes"):
                continue
            sc = g["chan"](b, "scale", t, [1, 1, 1])
            if np.all(sc == 0):
                st = ("hidden", None)
            else:
                M = g["world"](b, t, cache)
                pts = []
                pm = bone.get("poly_mesh")
                if pm:
                    pts = np.array(pm["positions"]).reshape(-1, 3)
                else:
                    for cu in bone["cubes"]:
                        o, s = np.array(cu["origin"]), np.array(cu["size"])
                        pts += [o, o + s]
                    pts = np.array(pts)
                pw = (M[:3, :3] @ pts.T).T + M[:3, 3]
                c = np.stack([-pw[:, 0] / 16, pw[:, 1] / 16 + 0.01, pw[:, 2] / 16], 1) * S + H + T
                ok = c[:, 2] < -0.05
                if not ok.any():
                    st = ("out", None)
                else:
                    sx = W / 2 + f * c[ok, 0] / -c[ok, 2]; sy = Hh / 2 - f * c[ok, 1] / -c[ok, 2]
                    inside = (sx > 0) & (sx < W) & (sy > 0) & (sy < Hh)
                    frac = inside.mean()
                    st = ("in" if frac > 0 else "out", (float(sx.mean()), float(sy.mean()), frac))
            if b in prev:
                p0, p1 = prev[b], st
                # vanishing / appearing while mostly on screen
                if p0[0] == "hidden" and p1[0] != "hidden" or p0[0] != "hidden" and p1[0] == "hidden":
                    print(f"  !! {gid}.{name} t={t:.2f} {b}: scale-toggle ({p0[0]}->{p1[0]})"); bad += 1
                elif p0[1] and p1[1] and math.hypot(p0[1][0] - p1[1][0], p0[1][1] - p1[1][1]) > 90:
                    print(f"  !! {gid}.{name} t={t:.2f} {b}: jump {math.hypot(p0[1][0]-p1[1][0], p0[1][1]-p1[1][1]):.0f}px"); bad += 1
                elif p0[0] != p1[0] and p0[1] and p1[1] and 0.0 < min(p0[1][2], p1[1][2]) and max(p0[1][2], p1[1][2]) > 0.9:
                    print(f"  !! {gid}.{name} t={t:.2f} {b}: pops {p0[0]}->{p1[0]} while {max(p0[1][2], p1[1][2]):.2f} on screen"); bad += 1
            prev[b] = st
        t += 1 / 30
print(gid, "audit issues:", bad)
