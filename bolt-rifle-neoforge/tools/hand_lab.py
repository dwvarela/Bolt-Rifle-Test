"""Preview just the three hands. Usage: hand_lab.py <out_res_dir> [h]"""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from meshbake import MModel
import gun_m700 as g
res = sys.argv[1]; h = float(sys.argv[2]) if len(sys.argv) > 2 else 0.1
m = MModel("bolt_rifle", lo=(-6.0, -10.0, -19.0), hi=(5.0, 3.0, 28.0), h=h, seed=5, tx=9)
m.bone("rifle", None, (0, 0, 0)) if False else None
m.bone("bolt_handle", "rifle", (0, 0, 5.0))
g.hands(m)
m.write(res)
