import sys, numpy as np, audit_pos as A, fp_proxy as Pz
sc, t = A.parse(open(A.JAVA).read())
gid = sys.argv[1]; coreZ = float(sys.argv[2]); yawmax = float(sys.argv[3]) if len(sys.argv) > 3 else 0.0
MZX = float(sys.argv[4]) if len(sys.argv) > 4 else 0.0
butt, s0 = t[gid][:2]
tr = Pz.load_tris(gid, ("stock", "buttstock")); P, N, a = Pz.prep(tr, 40000)
pts = A.load_pts(gid)
rh = pts["right_hand"]; core = rh[rh[:, 2] < coreZ]
lh = pts["left_hand"]
front = np.concatenate([v for k, v in pts.items() if k not in ("muzzle_flash", "casing", "chamber_round", "magazine", "left_hand", "right_hand", "buttstock", "stock")])
zmin = front[:, 2].min()
rng = np.random.default_rng(5)
best = None
def ev(dx, dy, dz, ry):
    xf = A.hip_xf(sc, butt, s0, dx, dy, dz, "now")
    rv = (0, ry, 0)
    if not Pz.inframe(core, xf, rv)[0].mean() >= 0.995: return None
    if not Pz.inframe(lh, xf, rv)[0].mean() >= 0.98: return None
    if not Pz.inframe(front, xf, rv)[0].mean() >= 0.99: return None
    mzx = Pz.inframe(np.array([[0, 0, zmin]]), xf, rv)
    if not mzx[0][0] or mzx[1][0] < MZX: return None
    return Pz.share(P, N, a, xf, rv)[0], mzx[1][0], mzx[2][0]
cands = []
for _ in range(6000):
    dx = rng.uniform(-1.0, 0.2); dy = rng.uniform(-0.3, 0.4); dz = rng.uniform(-0.3, 0.8); ry = rng.uniform(-yawmax, yawmax) if yawmax else 0.0
    r = ev(dx, dy, dz, ry)
    if r: cands.append((r[0], dx, dy, dz, ry, r[1], r[2]))
cands.sort()
print(len(cands), "feasible")
for c in cands[:8]: print("share %.3f dx %+.2f dy %+.2f dz %+.2f yaw %+.1f muzzle (%d,%d)" % c)
