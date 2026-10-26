"""Search a handle_grip offset that keeps the charging hand out of the gun. Usage: search_handle2.py <gun_module> <geo_res_dir> <anim> t1,t2,..."""
import os, sys, shutil, itertools, importlib
import gunanim, clip_check as K
mod, geo_res, anim, times = sys.argv[1], sys.argv[2], sys.argv[3], [float(x) for x in sys.argv[4].split(",")]
S = "/tmp/hs2"
os.makedirs(S + "/assets/boltrifle/geo/item", exist_ok=True); os.makedirs(S + "/assets/boltrifle/animations/item", exist_ok=True)
m, cfg = importlib.import_module(mod).build()
shutil.copy(geo_res + "/assets/boltrifle/geo/item/%s.geo.json" % m.ident, S + "/assets/boltrifle/geo/item/")
base = list(cfg["handle_grip"]); res = []
for d in itertools.product((0, -0.8, -1.6), (0, 0.8, 1.6, 2.4), (0, 0.8, -0.8)):
    c = dict(cfg); c["handle_grip"] = tuple(b + x for b, x in zip(base, d)); gunanim.build(c, S, m.ident)
    tot = sum(K.count(S, m.ident, anim, t)[0] for t in times)
    res.append((tot, d)); print(tot, d, flush=True)
res.sort(); print("BEST", res[:4])
