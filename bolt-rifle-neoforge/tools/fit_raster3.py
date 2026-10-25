import sys, numpy as np, audit_pos as A, fp_proxy as Pz, fp_cov as C
sc, t = A.parse(open(A.JAVA).read())
gid = sys.argv[1]; coreZ = float(sys.argv[2]); ylo, yhi = float(sys.argv[3]), float(sys.argv[4]); MZX = float(sys.argv[5]); N = int(sys.argv[6])
butt, s0 = t[gid][:2]
pts = A.load_pts(gid)
rh = pts["right_hand"]; core = rh[rh[:, 2] < coreZ]; lh = pts["left_hand"]
front = np.concatenate([v for k, v in pts.items() if k not in ("muzzle_flash", "casing", "chamber_round", "magazine", "left_hand", "right_hand", "buttstock", "stock")])
zmin = front[:, 2].min()
rng = np.random.default_rng(int(sys.argv[7]) if len(sys.argv) > 7 else 1)
res = []
tries = 0
while len(res) < N and tries < 200000:
    tries += 1
    dx = rng.uniform(-1.3, 0.2); dy = rng.uniform(-0.3, 0.4); dz = rng.uniform(-0.4, 0.6); ry = rng.uniform(ylo, yhi); rx = rng.uniform(-6, 8); rz = rng.uniform(-6, 6)
    xf = A.hip_xf(sc, butt, s0, dx, dy, dz, "now"); rv = (rx, ry, rz)
    if Pz.inframe(core, xf, rv)[0].mean() < 0.995: continue
    if Pz.inframe(lh, xf, rv)[0].mean() < 0.98: continue
    if Pz.inframe(front, xf, rv)[0].mean() < 0.99: continue
    mz = Pz.inframe(np.array([[0, 0, zmin]]), xf, rv)
    if not mz[0][0] or mz[1][0] < MZX: continue
    r = C.coverage(gid, xf, rv=rv)
    res.append((r["stock"], dx, dy, dz, rx, ry, rz, mz[1][0], mz[2][0]))
res.sort()
for r in res[:8]: print("stock %.3f dx %+.2f dy %+.2f dz %+.2f rx %+.1f ry %+.1f rz %+.1f muzzle (%d,%d)" % r)
