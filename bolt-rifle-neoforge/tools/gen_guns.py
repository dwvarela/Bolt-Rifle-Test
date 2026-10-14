"""Builds model + texture + animations for the guns named on the command line (default: all).
Usage: python3 gen_guns.py <resources_dir> [ak47 sks ...]"""
import importlib, sys
import gunanim

res = sys.argv[1]
names = sys.argv[2:] or ["ak47"]
for n in names:
    mod = importlib.import_module("gun_" + {"ak47": "ak", "m4a1": "m4", "m14ebr": "m14", "m700": "m700"}.get(n, n))
    m, cfg = mod.build()
    m.write(res)
    if cfg is None:
        continue
    gunanim.build(cfg, res, m.ident)
    u = 0.30 / 16
    if "sight" in cfg:
        sy, sz = cfg["sight"]
        relief = 0.0 if n in ("m14ebr",) else 0.05
        print("  JAVA ads=Xf(0.30, -0.56, %.3f, %.3f, 0,0,0) hip=Xf(0.30, -0.20, 0.14, %.3f, 0,0,0)" % (
            0.43 + (4.6 - sy) * u, 0.37 + (8 - sz) * u - relief, -0.05 + (22.4 - cfg["butt"]) * u))
