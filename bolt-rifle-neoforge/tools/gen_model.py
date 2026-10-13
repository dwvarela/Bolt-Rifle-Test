"""Generates the M700-style rifle: geo.json (Bedrock/GeckoLib format) + texture atlas.

Units: 1 px = ~0.5 cm.  Barrel points to -Z.  Shooter's RIGHT side is -X (Bedrock convention).
Run:  python3 gen_model.py <resources_dir>
"""
import json, os, random, sys
import numpy as np
from PIL import Image

RES = sys.argv[1]
TEX_W = TEX_H = 64
CELLS = {"wood": (0, 0), "wood_v": (1, 0), "steel": (2, 0), "black": (3, 0),
         "brass": (0, 1), "lens": (1, 1), "glove": (2, 1), "rubber": (3, 1),
         "scope": (0, 2), "stainless": (1, 2)}


# ------------------------------------------------------------------ texture
def paint_texture(path):
    rng = np.random.default_rng(7)
    img = np.zeros((TEX_H, TEX_W, 4), dtype=np.uint8)
    img[..., 3] = 255
    yy, xx = np.mgrid[0:16, 0:16]

    def put(name, arr):
        cx, cy = CELLS[name]
        img[cy * 16:cy * 16 + 16, cx * 16:cx * 16 + 16, :3] = np.clip(arr, 0, 255).astype(np.uint8)

    def noise(s):
        return rng.normal(0, s, (16, 16, 1))

    streak = np.sin(yy * 1.9 + np.sin(xx * 0.35) * 2.2)[..., None]
    walnut = np.array([112, 70, 40]) + streak * np.array([16, 12, 8]) + noise(4)
    put("wood", walnut)
    streak_v = np.sin(xx * 1.9 + np.sin(yy * 0.35) * 2.2)[..., None]
    put("wood_v", np.array([104, 64, 36]) + streak_v * np.array([16, 12, 8]) + noise(4))
    put("steel", np.array([40, 46, 58]) + noise(3) + (yy[..., None] < 3) * 22)
    put("black", np.array([26, 26, 29]) + noise(2.5))
    shade = (yy[..., None] / 15.0)
    put("brass", np.array([214, 160, 66]) * (1.15 - 0.45 * shade) + noise(3))
    dist = np.sqrt((xx - 6) ** 2 + (yy - 5) ** 2)[..., None]
    lens = np.array([36, 52, 104]) + (dist < 4) * np.array([60, 30, 50]) \
        + (np.abs(dist - 7) < 1) * np.array([30, 40, 20]) + noise(2)
    put("lens", lens)
    put("glove", np.array([54, 58, 50]) + noise(5) + ((xx + yy) % 4 == 0)[..., None] * 6)
    put("rubber", np.array([20, 20, 21]) + noise(2) + ((xx % 3) == 0)[..., None] * 5)
    put("scope", np.array([32, 33, 37]) + noise(2) + (yy[..., None] < 2) * 26)
    put("stainless", np.array([150, 154, 160]) - shade * 40 + noise(4))
    Image.fromarray(img, "RGBA").save(path)


# ------------------------------------------------------------------ geometry
bones = {}      # name -> dict(parent, pivot, cubes)
rnd = random.Random(3)


def bone(name, parent, pivot):
    bones[name] = {"name": name, "pivot": list(pivot), "cubes": []}
    if parent:
        bones[name]["parent"] = parent


def uv_for(mat, size):
    w, h, d = size
    dims = {"north": (w, h), "south": (w, h), "east": (d, h), "west": (d, h),
            "up": (w, d), "down": (w, d)}
    out = {}
    for face, (fw, fh) in dims.items():
        m = mat
        if mat == "wood" and face in ("up", "down"):
            m = "wood_v"
        cx, cy = CELLS[m]
        sw, sh = max(1, min(int(round(fw)), 16)), max(1, min(int(round(fh)), 16))
        ox, oy = rnd.randint(0, 16 - sw), rnd.randint(0, 16 - sh)
        out[face] = {"uv": [cx * 16 + ox, cy * 16 + oy], "uv_size": [sw, sh]}
    return out


def cube(b, mat, x0, y0, z0, x1, y1, z1, rot=None, pivot=None):
    size = [round(x1 - x0, 3), round(y1 - y0, 3), round(z1 - z0, 3)]
    c = {"origin": [x0, y0, z0], "size": size, "uv": uv_for(mat, size)}
    if rot:
        c["rotation"] = rot
        c["pivot"] = pivot
    bones[b]["cubes"].append(c)


def round_bar(b, mat, cx, cy, z0, z1, r):
    """Octagon-ish round bar along Z: one square + one 45-degree rotated square."""
    cube(b, mat, cx - r, cy - r, z0, cx + r, cy + r, z1)
    cube(b, mat, cx - r, cy - r, z0, cx + r, cy + r, z1, rot=[0, 0, 45], pivot=[cx, cy, z0])


# shooter's right = -X
R = -1

bone("rifle", None, (0, 0, 0))

# ---- stock (walnut) ----
bone("stock", "rifle", (0, 0, 0))
cube("stock", "wood", -1.9, -3.4, -23.0, 1.9, -0.5, -6.0)          # forend
cube("stock", "wood", -1.5, -3.2, -24.0, 1.5, -0.7, -23.0)         # forend tip
cube("stock", "black", -1.9, -3.4, -24.6, 1.9, -2.8, -23.6)        # tip cap
cube("stock", "wood", -2.1, -5.0, -6.0, 2.1, -0.5, 8.0)            # action section
cube("stock", "wood", -2.1, -1.6, -6.0, -1.8, 0.2, 7.5)            # side wall (right)
cube("stock", "wood", 1.8, -1.6, -6.0, 2.1, 0.2, 7.5)              # side wall (left)
cube("stock", "wood", -1.9, -7.6, 8.0, 1.9, -0.6, 11.0)            # wrist / grip
cube("stock", "wood", -1.9, -6.6, 11.0, 1.9, -0.6, 14.0)
cube("stock", "wood", -1.9, -7.4, 14.0, 1.9, -0.8, 17.5)           # buttstock
cube("stock", "wood", -1.9, -8.6, 17.5, 1.9, -1.1, 21.0)
cube("stock", "rubber", -2.0, -9.4, 21.0, 2.0, -1.3, 22.4)          # recoil pad
cube("stock", "black", -0.5, -6.2, 8.4, 0.5, -5.4, 9.4)             # grip cap hint
cube("stock", "stainless", -0.6, -4.2, -17.0, 0.6, -3.4, -16.0)     # sling stud

# ---- barrel group ----
bone("barrel", "rifle", (0, 0, 0))
round_bar("barrel", "steel", 0, 0, -26.0, -6.0, 1.15)
round_bar("barrel", "steel", 0, 0, -32.0, -26.0, 0.95)
round_bar("barrel", "black", 0, 0, -33.4, -32.0, 1.2)               # muzzle brake / crown
cube("barrel", "black", -0.5, -0.5, -33.45, 0.5, 0.5, -33.35)       # bore

# ---- receiver ----
bone("receiver", "rifle", (0, 0, 0))
round_bar("receiver", "steel", 0, 0, -6.0, 7.0, 1.8)
cube("receiver", "steel", -1.9, -0.4, -6.0, 1.9, 0.4, -4.4)          # recoil lug
cube("receiver", "black", 1.78, -1.1, -3.6, 1.9, 1.3, 3.8)          # ejection port (left, -x is right)
cube("receiver", "black", -1.9, -1.1, -3.6, -1.78, 1.3, 3.8)        # ejection port (right)
cube("receiver", "steel", -2.0, -0.6, 4.5, -1.8, 0.6, 6.0)          # safety lever
cube("receiver", "black", -2.2, -0.5, 4.8, -1.9, 0.5, 5.6)
cube("receiver", "steel", -0.6, 1.7, 4.0, 0.6, 2.3, 6.4)            # rear base
cube("receiver", "steel", -0.7, 1.6, -5.5, 0.7, 2.5, -3.0)          # front base
# trigger guard + trigger
cube("receiver", "steel", -0.5, -6.8, 3.8, 0.5, -6.2, 8.4)
cube("receiver", "steel", -0.5, -6.8, 3.8, 0.5, -4.8, 4.4)
cube("receiver", "steel", -0.5, -6.8, 7.8, 0.5, -4.8, 8.4)
cube("receiver", "black", -0.3, -6.0, 5.4, 0.3, -3.2, 6.0)          # trigger
cube("receiver", "steel", -2.3, -5.0, -6.2, 2.3, -4.7, -5.8)        # front action screw plate

# ---- scope (4-16x style) ----
bone("scope", "rifle", (0, 4.6, -4))
cube("scope", "black", -1.9, 1.5, -12.0, 1.9, 3.7, -10.2)           # ring front
cube("scope", "black", -1.9, 1.5, -2.8, 1.9, 3.7, -1.0)             # ring rear
round_bar("scope", "scope", 0, 4.6, -13.0, 3.5, 1.5)               # main tube
round_bar("scope", "scope", 0, 4.6, -18.0, -13.0, 2.15)            # objective bell
round_bar("scope", "scope", 0, 4.6, 3.5, 8.0, 1.9)                 # eyepiece
cube("scope", "lens", -1.8, 2.9, -18.08, 1.8, 6.3, -17.98)           # objective lens
cube("scope", "lens", -1.4, 3.2, 7.98, 1.4, 6.0, 8.08)              # ocular lens
cube("scope", "scope", -1.0, 6.0, -8.3, 1.0, 7.1, -6.3)            # elevation turret
cube("scope", "stainless", -0.7, 7.1, -8.0, 0.7, 7.5, -6.6)
cube("scope", "scope", -3.1, 4.0, -8.3, -1.4, 5.2, -6.3)            # windage turret (right)
cube("scope", "scope", -1.0, 3.9, -5.2, 1.0, 4.9, -3.5)            # parallax knob look
cube("scope", "stainless", -1.5, 4.0, -13.2, 1.5, 5.2, -13.0)       # step ring
cube("scope", "stainless", -1.9, 4.1, 3.3, 1.9, 5.1, 3.7)           # power ring

# ---- bolt (slides back on Z) ----
bone("bolt", "rifle", (0, 0, 0))
cube("bolt", "stainless", -2.0, -0.6, -2.2, -1.9, 0.9, 3.2)         # bolt body seen in port (right)
cube("bolt", "stainless", 1.9, -0.6, -2.2, 2.0, 0.9, 3.2)           # bolt body seen in port (left)
round_bar("bolt", "black", 0, 0.1, 7.0, 12.4, 1.15)                # bolt sleeve
cube("bolt", "stainless", -0.55, -0.45, 12.4, 0.55, 0.65, 14.0)     # cocking piece
cube("bolt", "steel", -0.4, 0.55, 8.4, 0.4, 1.5, 9.2)               # cocking indicator

# bolt handle: pivot on the bolt axis so +/-Z rotation lifts it
bone("bolt_handle", "bolt", (0, 0, 5.0))
cube("bolt_handle", "steel", -3.6, -0.7, 4.2, -0.9, 0.3, 5.4)       # stem
cube("bolt_handle", "steel", -4.6, -1.8, 4.2, -3.4, -0.5, 5.4)      # swept-down section
cube("bolt_handle", "black", -6.6, -4.0, 3.6, -4.0, -1.4, 6.0)      # knob

# bolt-working glove (hidden unless animated)
bone("bolt_hand", "bolt_handle", (-5.3, -2.7, 4.8))
cube("bolt_hand", "glove", -7.6, -5.0, 2.8, -3.6, -0.8, 7.0)
cube("bolt_hand", "glove", -7.8, -3.4, 2.6, -7.4, -1.2, 5.6)        # thumb
cube("bolt_hand", "glove", -7.0, -8.5, 6.6, -4.2, -3.2, 17.0)       # forearm

# ---- magazine ----
bone("magazine", "rifle", (0, -1.8, 0.5))
cube("magazine", "black", -1.3, -10.4, -2.4, 1.3, -1.2, 3.4)
cube("magazine", "stainless", -1.4, -10.9, -2.5, 1.4, -10.4, 3.5)   # floorplate
cube("magazine", "brass", -0.7, -1.8, -0.4, 0.7, -1.2, 1.2)         # top round peeking
cube("magazine", "steel", -1.4, -8.0, -2.5, 1.4, -7.8, 3.5)         # mag seam

# ---- casing + chambering round ----
bone("casing", "rifle", (-1.5, 0.4, 0.5))
round_bar("casing", "brass", -1.6, 0.5, -1.5, 1.8, 0.55)
bone("chamber_round", "rifle", (0, 0.4, -3))
round_bar("chamber_round", "brass", 0, 0.7, -3.0, 0.2, 0.5)
cube("chamber_round", "stainless", -0.35, 0.35, -4.4, 0.35, 1.05, -3.0)  # bullet tip

# ---- hands ----
bone("left_hand", "rifle", (0, -3, -14))
cube("left_hand", "glove", -1.9, -5.8, -18.0, 1.9, -3.3, -11.0)    # palm
cube("left_hand", "glove", -2.7, -4.6, -17.0, -1.9, -1.2, -11.5)   # fingers
cube("left_hand", "glove", 1.9, -3.6, -16.0, 2.5, -1.2, -12.5)     # thumb
cube("left_hand", "glove", -1.8, -9.0, -12.0, 1.8, -4.8, -2.0)     # forearm

bone("right_hand", "rifle", (0, -4, 10))
cube("right_hand", "glove", -2.8, -8.4, 7.6, 2.8, -2.0, 12.6)      # grip hand
cube("right_hand", "glove", -3.0, -6.8, 4.2, -2.1, -3.4, 8.0)      # trigger finger
cube("right_hand", "glove", -1.9, -12.5, 11.0, 1.9, -6.0, 22.0)    # forearm

order = ["rifle", "stock", "barrel", "receiver", "scope", "bolt", "bolt_handle", "bolt_hand",
         "magazine", "casing", "chamber_round", "left_hand", "right_hand"]
geo = {
    "format_version": "1.12.0",
    "minecraft:geometry": [{
        "description": {"identifier": "geometry.bolt_rifle", "texture_width": TEX_W,
                        "texture_height": TEX_H, "visible_bounds_width": 8,
                        "visible_bounds_height": 6, "visible_bounds_offset": [0, 0, 0]},
        "bones": [bones[n] for n in order]}]}

os.makedirs(os.path.join(RES, "assets/boltrifle/geo/item"), exist_ok=True)
os.makedirs(os.path.join(RES, "assets/boltrifle/textures/item"), exist_ok=True)
with open(os.path.join(RES, "assets/boltrifle/geo/item/bolt_rifle.geo.json"), "w") as f:
    json.dump(geo, f, indent=1)
paint_texture(os.path.join(RES, "assets/boltrifle/textures/item/bolt_rifle.png"))
print("cubes:", sum(len(b["cubes"]) for b in bones.values()), "bones:", len(bones))
