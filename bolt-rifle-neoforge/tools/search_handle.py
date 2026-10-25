import os, sys, shutil, itertools, numpy as np
import gun_m14, gunanim, clip_check as K
S = "/tmp/claude-0/-home-claude-bolt-rifle-test/f7704eef-62d6-5370-832a-86ddeef93d7b/scratchpad/hs"
os.makedirs(S + "/assets/boltrifle/geo/item", exist_ok=True); os.makedirs(S + "/assets/boltrifle/animations/item", exist_ok=True)
shutil.copy("../src/main/resources/assets/boltrifle/geo/item/m14ebr.geo.json", S + "/assets/boltrifle/geo/item/")
m, cfg = gun_m14.build()
base = list(cfg["handle_grip"])
res = []
for dx, dy, dz in itertools.product((0, -0.8, -1.6), (0, 0.8, 1.6), (0, -0.8)):
    cfg2 = dict(cfg); cfg2["handle_grip"] = (base[0] + dx, base[1] + dy, base[2] + dz)
    gunanim.build(cfg2, S, "m14ebr")
    tot = sum(K.count(S, "m14ebr", "reload_release", t)[0] for t in (2.5, 2.7, 2.9, 3.1))
    res.append((tot, dx, dy, dz)); print(tot, dx, dy, dz, flush=True)
res.sort(); print("BEST", res[:5])
