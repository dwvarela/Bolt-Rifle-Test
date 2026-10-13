"""Quick software preview of the geo model (not used by the mod). Usage: preview.py <resources_dir> <out.png> [hidden,bones]"""
import json, sys, math
import numpy as np
from PIL import Image
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d.art3d import Poly3DCollection

res, out = sys.argv[1], sys.argv[2]
hidden = set(sys.argv[3].split(",")) if len(sys.argv) > 3 else {"bolt_hand", "casing", "chamber_round"}
geo = json.load(open(f"{res}/assets/boltrifle/geo/item/bolt_rifle.geo.json"))["minecraft:geometry"][0]
tex = np.array(Image.open(f"{res}/assets/boltrifle/textures/item/bolt_rifle.png").convert("RGB"))


def rotz(p, pivot, deg):
    a = math.radians(deg)
    x, y = p[0] - pivot[0], p[1] - pivot[1]
    return (pivot[0] + x * math.cos(a) - y * math.sin(a), pivot[1] + x * math.sin(a) + y * math.cos(a), p[2])


polys, cols = [], []
for b in geo["bones"]:
    if b["name"] in hidden:
        continue
    for c in b["cubes"]:
        ox, oy, oz = c["origin"]
        sx, sy, sz = c["size"]
        P = [(ox + dx * sx, oy + dy * sy, oz + dz * sz) for dx in (0, 1) for dy in (0, 1) for dz in (0, 1)]
        if "rotation" in c:
            P = [rotz(p, c["pivot"], c["rotation"][2]) for p in P]
        idx = lambda dx, dy, dz: dx * 4 + dy * 2 + dz
        faces = {"west": [idx(0, 0, 0), idx(0, 1, 0), idx(0, 1, 1), idx(0, 0, 1)],
                 "east": [idx(1, 0, 0), idx(1, 1, 0), idx(1, 1, 1), idx(1, 0, 1)],
                 "down": [idx(0, 0, 0), idx(1, 0, 0), idx(1, 0, 1), idx(0, 0, 1)],
                 "up": [idx(0, 1, 0), idx(1, 1, 0), idx(1, 1, 1), idx(0, 1, 1)],
                 "north": [idx(0, 0, 0), idx(1, 0, 0), idx(1, 1, 0), idx(0, 1, 0)],
                 "south": [idx(0, 0, 1), idx(1, 0, 1), idx(1, 1, 1), idx(0, 1, 1)]}
        shade = {"up": 1.0, "down": 0.55, "north": 0.8, "south": 0.8, "east": 0.7, "west": 0.7}
        for f, vs in faces.items():
            u = c["uv"][f]
            px = tex[u["uv"][1] + u["uv_size"][1] // 2, u["uv"][0] + u["uv_size"][0] // 2] / 255.0
            polys.append([(P[i][0], P[i][2], P[i][1]) for i in vs])
            cols.append(tuple(np.clip(px * shade[f] * 1.25, 0, 1)) + (1,))

fig = plt.figure(figsize=(18, 6), dpi=110)
views = [("shooter's right side (muzzle to the left)", 0, 180), ("3/4 from behind-right", 22, 215), ("top", 90, -90)]
for i, (name, elev, azim) in enumerate(views):
    ax = fig.add_subplot(1, 3, i + 1, projection="3d")
    ax.add_collection3d(Poly3DCollection(polys, facecolors=cols, edgecolors=(0, 0, 0, 0.25), linewidths=0.2))
    ax.set_xlim(-22, 22); ax.set_ylim(-34, 24); ax.set_zlim(-12, 12); ax.set_box_aspect((44, 58, 24), zoom=1.35)
    # axes: plot x=geo x, y=geo z (length), z=geo y (up)
    ax.view_init(elev=elev, azim=azim)
    ax.set_title(name, fontsize=9); ax.set_axis_off()
fig.tight_layout()
fig.savefig(out)
print("saved", out)
