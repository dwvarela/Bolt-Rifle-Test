"""Shared pieces for building gun models: palette texture, cube/bone builder, muzzle flash, casing, hands.

Units: 1 px = 1/16 block.  Barrel points to -Z, shooter's RIGHT side is -X, up is +Y, bore axis is y = 0.
"""
import json, os, random
import numpy as np
from PIL import Image

TEX_W = TEX_H = 64
CELLS = {"wood": (0, 0), "wood_v": (1, 0), "steel": (2, 0), "black": (3, 0),
         "brass": (0, 1), "lens": (1, 1), "glove": (2, 1), "rubber": (3, 1),
         "scope": (0, 2), "stainless": (1, 2), "flash": (2, 2),
         "poly": (3, 2), "gunmetal": (0, 3), "plum": (1, 3), "plum_v": (2, 3), "dot": (3, 3)}


def paint_texture(path, seed=7):
    rng = np.random.default_rng(seed)
    img = np.zeros((TEX_H, TEX_W, 4), dtype=np.uint8)
    img[..., 3] = 255
    yy, xx = np.mgrid[0:16, 0:16]

    def put(name, arr):
        cx, cy = CELLS[name]
        img[cy * 16:cy * 16 + 16, cx * 16:cx * 16 + 16, :3] = np.clip(arr, 0, 255).astype(np.uint8)

    def noise(s):
        return rng.normal(0, s, (16, 16, 1))

    streak = np.sin(yy * 1.9 + np.sin(xx * 0.35) * 2.2)[..., None]
    put("wood", np.array([112, 70, 40]) + streak * np.array([16, 12, 8]) + noise(4))
    streak_v = np.sin(xx * 1.9 + np.sin(yy * 0.35) * 2.2)[..., None]
    put("wood_v", np.array([104, 64, 36]) + streak_v * np.array([16, 12, 8]) + noise(4))
    put("steel", np.array([40, 46, 58]) + noise(3) + (yy[..., None] < 3) * 22)
    put("black", np.array([26, 26, 29]) + noise(2.5))
    shade = (yy[..., None] / 15.0)
    put("brass", np.array([214, 160, 66]) * (1.15 - 0.45 * shade) + noise(3))
    dist = np.sqrt((xx - 6) ** 2 + (yy - 5) ** 2)[..., None]
    put("lens", np.array([36, 52, 104]) + (dist < 4) * np.array([60, 30, 50])
        + (np.abs(dist - 7) < 1) * np.array([30, 40, 20]) + noise(2))
    put("glove", np.array([54, 58, 50]) + noise(5) + ((xx + yy) % 4 == 0)[..., None] * 6)
    put("rubber", np.array([20, 20, 21]) + noise(2) + ((xx % 3) == 0)[..., None] * 5)
    put("scope", np.array([32, 33, 37]) + noise(2) + (yy[..., None] < 2) * 26)
    put("stainless", np.array([150, 154, 160]) - shade * 40 + noise(4))
    fd = np.sqrt((xx - 7.5) ** 2 + (yy - 7.5) ** 2)[..., None] / 10.6
    put("flash", np.array([255, 245, 190]) * (1 - fd) + np.array([255, 130, 30]) * fd)
    put("poly", np.array([44, 45, 48]) + noise(2.5) + ((xx * 7 + yy * 3) % 5 == 0)[..., None] * 5)
    put("gunmetal", np.array([66, 70, 66]) + noise(3) + (yy[..., None] < 3) * 16)
    put("plum", np.array([132, 62, 34]) + streak * np.array([22, 10, 6]) + noise(4))
    put("plum_v", np.array([124, 56, 30]) + streak_v * np.array([22, 10, 6]) + noise(4))
    put("dot", np.array([255, 40, 40]))
    Image.fromarray(img, "RGBA").save(path)
    glow = np.zeros_like(img)                    # flash + red dot glow at full brightness
    for cell in ("flash", "dot"):
        fx, fy = CELLS[cell]
        glow[fy * 16:fy * 16 + 16, fx * 16:fx * 16 + 16] = img[fy * 16:fy * 16 + 16, fx * 16:fx * 16 + 16]
    Image.fromarray(glow, "RGBA").save(path.replace(".png", "_glowmask.png"))


class Model:
    def __init__(self, ident, seed=3):
        self.ident = ident
        self.bones = {}
        self.order = []
        self.rnd = random.Random(seed)
        self.bone("rifle", None, (0, 0, 0))

    def bone(self, name, parent, pivot):
        self.bones[name] = {"name": name, "pivot": list(pivot), "cubes": []}
        if parent:
            self.bones[name]["parent"] = parent
        self.order.append(name)

    def _uv(self, mat, size):
        w, h, d = size
        dims = {"north": (w, h), "south": (w, h), "east": (d, h), "west": (d, h), "up": (w, d), "down": (w, d)}
        out = {}
        for face, (fw, fh) in dims.items():
            m = mat
            if face in ("up", "down") and mat in ("wood", "plum"):
                m = mat + "_v"
            cx, cy = CELLS[m]
            sw, sh = max(1, min(int(round(fw)), 16)), max(1, min(int(round(fh)), 16))
            ox, oy = self.rnd.randint(0, 16 - sw), self.rnd.randint(0, 16 - sh)
            out[face] = {"uv": [cx * 16 + ox, cy * 16 + oy], "uv_size": [sw, sh]}
        return out

    def cube(self, b, mat, x0, y0, z0, x1, y1, z1, rot=None, pivot=None):
        if x1 < x0: x0, x1 = x1, x0
        if y1 < y0: y0, y1 = y1, y0
        if z1 < z0: z0, z1 = z1, z0
        size = [round(x1 - x0, 3), round(y1 - y0, 3), round(z1 - z0, 3)]
        c = {"origin": [x0, y0, z0], "size": size, "uv": self._uv(mat, size)}
        if rot:
            c["rotation"] = rot
            c["pivot"] = pivot
        self.bones[b]["cubes"].append(c)

    def bar(self, b, mat, cx, cy, z0, z1, r):
        """Octagon-ish round bar along Z."""
        self.cube(b, mat, cx - r, cy - r, z0, cx + r, cy + r, z1)
        self.cube(b, mat, cx - r, cy - r, z0, cx + r, cy + r, z1, rot=[0, 0, 45], pivot=[cx, cy, z0])

    def cubes(self):
        return sum(len(b["cubes"]) for b in self.bones.values())

    # ---- shared parts
    def muzzle_flash(self, z, y=0.0, length=5.0, width=3.4):
        self.bone("muzzle_flash", "rifle", (0, y, z))
        for ang in (0, 45, 90, 135):
            self.cube("muzzle_flash", "flash", -width, y - 0.12, z - length, width, y + 0.12, z + 0.1,
                      rot=[0, 0, ang], pivot=[0, y, z])
        self.cube("muzzle_flash", "flash", -1.2, y - 1.2, z - length * 0.6, 1.2, y + 1.2, z + 0.1)
        self.cube("muzzle_flash", "flash", -0.5, y - 0.5, z - length * 1.5, 0.5, y + 0.5, z - length * 0.6)

    def casing(self, x, y, z, length=3.4, r=0.55):
        """Spent case sitting at the ejection port (hidden until the fire animation shows it)."""
        self.bone("casing", "rifle", (x, y, z))
        self.bar("casing", "brass", x, y, z - length / 2, z + length / 2, r)

    def hand_left(self, y, z, reach_forward=3.0):
        """Support hand wrapped under the forend; pivot is the palm centre."""
        self.bone("left_hand", "rifle", (0, y, z))
        self.cube("left_hand", "glove", -1.9, y - 1.4, z - 3.5, 1.9, y + 1.4, z + 3.5)
        self.cube("left_hand", "glove", -2.8, y - 0.6, z - 3.0, -1.9, y + 2.6, z + 2.4)    # fingers up the side
        self.cube("left_hand", "glove", 1.9, y - 0.4, z - 2.6, 2.6, y + 2.4, z + 0.6)      # thumb
        self.cube("left_hand", "glove", -1.8, y - 4.6, z + 1.0, 1.8, y - 1.2, z + 10.0)    # forearm

    def hand_right(self, y, z, trigger_y):
        """Firing hand on the grip, finger on the trigger; pivot is at the grip."""
        self.bone("right_hand", "rifle", (0, y, z))
        self.cube("right_hand", "glove", -2.8, y - 3.2, z - 2.4, 2.8, y + 3.2, z + 2.6)
        self.cube("right_hand", "glove", -3.0, trigger_y - 1.8, z - 5.8, -2.1, trigger_y + 1.6, z - 2.0)
        self.cube("right_hand", "glove", -1.9, y - 7.0, z + 1.0, 1.9, y - 0.5, z + 12.0)

    def hand_bolt(self, parent, x, y, z):
        """Glove that grabs the right-hand charging handle (child of the handle so it moves with it)."""
        self.bone("bolt_hand", parent, (x, y, z))
        self.cube("bolt_hand", "glove", x - 2.4, y - 2.2, z - 2.2, x + 1.6, y + 1.8, z + 2.4)
        self.cube("bolt_hand", "glove", x - 2.6, y - 0.6, z - 2.4, x - 2.2, y + 1.4, z + 0.4)
        self.cube("bolt_hand", "glove", x - 1.8, y - 6.0, z + 1.6, x + 1.4, y - 1.8, z + 12.0)

    def write(self, res, texture=True):
        geo = {"format_version": "1.12.0", "minecraft:geometry": [{
            "description": {"identifier": "geometry." + self.ident, "texture_width": TEX_W,
                            "texture_height": TEX_H, "visible_bounds_width": 8,
                            "visible_bounds_height": 6, "visible_bounds_offset": [0, 0, 0]},
            "bones": [self.bones[n] for n in self.order]}]}
        d = os.path.join(res, "assets/boltrifle/geo/item")
        os.makedirs(d, exist_ok=True)
        with open(os.path.join(d, self.ident + ".geo.json"), "w") as f:
            json.dump(geo, f, indent=1)
        t = os.path.join(res, "assets/boltrifle/textures/item")
        os.makedirs(t, exist_ok=True)
        if texture:
            paint_texture(os.path.join(t, self.ident + ".png"))
        print(self.ident, "cubes:", self.cubes(), "bones:", len(self.bones))
