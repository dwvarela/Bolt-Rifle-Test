"""Shared pieces for building gun models: per-face painted texture atlas, cube/bone builder, shared parts.

Units: 1 px = 1/16 block.  Barrel points to -Z, shooter's RIGHT side is -X, up is +Y, bore axis is y = 0.
Cube rotations follow GeckoLib: the stored x/y are negated at load, so in the .geo.json
  +rx tips the TOP of a cube toward the muzzle (-Z), i.e. a rear-raked pistol grip is +rx.
Every cube face gets its own region of the texture atlas, painted with bevelled edges, grain and wear,
at TEXEL texels per model pixel.
"""
import json, math, os, random
import numpy as np
from PIL import Image

TEXEL = 3          # texels per model pixel

# material -> (base rgb, kind)
MATS = {
    "steel": ((44, 50, 60), "metal"), "gunmetal": ((72, 77, 70), "metal"), "black": ((27, 27, 30), "metal"),
    "stainless": ((156, 160, 166), "bright"), "scope": ((33, 34, 38), "metal"), "poly": ((60, 62, 66), "poly"),
    "rubber": ((22, 22, 23), "rubber"), "brass": ((204, 152, 62), "brass"), "wood": ((112, 70, 40), "wood"),
    "plum": ((128, 60, 32), "wood"), "glove": ((54, 58, 50), "cloth"), "lens": ((40, 58, 112), "lens"),
    "flash": ((255, 235, 170), "glow"), "dot": ((255, 40, 40), "glow"), "olive": ((84, 88, 62), "poly"),
    "tan": ((150, 128, 92), "poly"), "smoke": ((92, 88, 84), "poly"),
}
GLOW = {"flash", "dot"}
# baked light direction: top faces catch light, bottoms are dark
FACE_LIGHT = {"up": 1.14, "north": 1.0, "south": 0.9, "east": 0.84, "west": 0.84, "down": 0.62}


def _paint_face(mat, face, w, h, rng, flat=False):
    base, kind = MATS[mat]
    base = np.array(base, dtype=float)
    yy, xx = np.mgrid[0:h, 0:w]
    img = np.ones((h, w, 3)) * base
    long_axis_x = (w >= h) if face in ("north", "south") else face in ("east", "west")
    # coordinate along / across the long direction of the part
    along = xx if long_axis_x else yy
    across = yy if long_axis_x else xx
    n = rng.normal(0, 1, (h, w, 1))
    if kind in ("metal", "bright"):
        streak = rng.normal(0, 1, (h if long_axis_x else 1, 1 if long_axis_x else w, 1))
        streak = np.repeat(streak, w if long_axis_x else h, axis=1 if long_axis_x else 0)
        img *= 1 + 0.045 * streak + 0.025 * n
    elif kind == "poly":
        img *= 1 + 0.05 * n + 0.03 * (((xx * 5 + yy * 3) % 7) == 0)[..., None]
    elif kind == "rubber":
        img *= 1 + 0.06 * n + 0.18 * ((across % 3) == 0)[..., None]
    elif kind == "wood":
        warp = np.sin(along * 0.31 + across * 0.2) * 1.4
        g = np.sin((across + warp) * (1.7 / max(1.0, TEXEL / 3)) + rng.uniform(0, 6))
        g2 = np.sin((across + warp * 0.6) * 0.55 + rng.uniform(0, 6))
        img *= (1 + 0.13 * g + 0.08 * g2)[..., None] * (1 + 0.025 * n)
    elif kind == "brass":
        t = (xx / max(1, w - 1))[..., None]
        img *= (0.72 + 0.62 * np.sin(t * math.pi)) * (1 + 0.03 * n)
    elif kind == "cloth":
        img *= 1 + 0.07 * n + 0.07 * (((xx + yy) % 3) == 0)[..., None]
    elif kind == "lens":
        d = np.sqrt((xx - w * 0.35) ** 2 + (yy - h * 0.3) ** 2) / max(w, h)
        img = img * (0.8 + 0.5 * (1 - d)[..., None]) + (d < 0.18)[..., None] * 90
    elif kind == "glow":
        d = np.sqrt((xx - w / 2) ** 2 + (yy - h / 2) ** 2) / max(1.0, max(w, h) / 2)
        if mat == "flash":
            img = np.array([255, 245, 190]) * (1 - np.clip(d, 0, 1))[..., None] + np.array([255, 130, 30]) * np.clip(d, 0, 1)[..., None]
        return np.clip(img, 0, 255)       # glow materials are unshaded
    # lighting by orientation + bevelled edges
    img *= FACE_LIGHT[face]
    dist = np.minimum(np.minimum(xx, yy), np.minimum(w - 1 - xx, h - 1 - yy))
    hi = ((xx == 0) | (yy == 0)) & (w > 3) & (h > 3) & (not flat)
    lo = ((xx == w - 1) | (yy == h - 1)) & (w > 3) & (h > 3) & (not flat)
    img = np.where(hi[..., None], img * 1.22, img)
    img = np.where(lo[..., None], img * 0.78, img)
    img *= (0.9 + 0.1 * np.clip(dist / 2.0, 0, 1))[..., None]          # soft edge occlusion
    if kind in ("metal", "bright") and mat != "scope":                   # edge wear
        worn = (dist <= 1) & (rng.random((h, w)) < 0.05)
        img = np.where(worn[..., None], np.minimum(img * 1.7 + 12, 190), img)
    return np.clip(img, 0, 255)


class Model:
    def __init__(self, ident, seed=3):
        self.ident = ident
        self.bones = {}
        self.order = []
        self.seed = seed
        self._mats = {}
        self.bone("rifle", None, (0, 0, 0))

    def bone(self, name, parent, pivot):
        self.bones[name] = {"name": name, "pivot": list(pivot), "cubes": []}
        if parent:
            self.bones[name]["parent"] = parent
        self.order.append(name)

    def cube(self, b, mat, x0, y0, z0, x1, y1, z1, rot=None, pivot=None, flat=False):
        if x1 < x0: x0, x1 = x1, x0
        if y1 < y0: y0, y1 = y1, y0
        if z1 < z0: z0, z1 = z1, z0
        size = [round(x1 - x0, 3), round(y1 - y0, 3), round(z1 - z0, 3)]
        c = {"origin": [round(x0, 3), round(y0, 3), round(z0, 3)], "size": size}
        if rot:
            c["rotation"] = list(rot) if len(rot) == 3 else [0, 0, rot]
            c["pivot"] = list(pivot)
        self._mats[id(c)] = (mat, flat)
        self.bones[b]["cubes"].append(c)
        return c

    def bar(self, b, mat, cx, cy, z0, z1, r, fine=False):
        """Round bar along Z (8 sides, or 16 when fine=True)."""
        angs = (0, 22.5, 45, 67.5) if fine else (0, 45)
        for a in angs:
            self.cube(b, mat, cx - r, cy - r, z0, cx + r, cy + r, z1, rot=[0, 0, a] if a else None, pivot=[cx, cy, z0])

    def rbox(self, b, mat, x0, y0, z0, x1, y1, z1, c=0.4):
        """Box with chamfered edges running along Z (cross-section chamfer c)."""
        w, h = x1 - x0, y1 - y0
        c = min(c, w / 2.2, h / 2.2)
        if c < 0.15:
            return self.cube(b, mat, x0, y0, z0, x1, y1, z1)
        self.cube(b, mat, x0, y0 + c, z0, x1, y1 - c, z1)
        self.cube(b, mat, x0 + c, y0, z0, x1 - c, y1, z1)
        s = c * math.sqrt(2) / 1.0
        for cx, cy in ((x0 + c, y0 + c), (x1 - c, y0 + c), (x0 + c, y1 - c), (x1 - c, y1 - c)):
            self.cube(b, mat, cx - s / 2, cy - s / 2, z0, cx + s / 2, cy + s / 2, z1, rot=[0, 0, 45], pivot=[cx, cy, z0])

    def slope(self, b, mat, x0, x1, y0, y1, z0, z1, rake):
        """Box tilted about X (rake > 0 tips the top toward the muzzle), pivoting at its centre."""
        cy, cz = (y0 + y1) / 2, (z0 + z1) / 2
        self.cube(b, mat, x0, y0, z0, x1, y1, z1, rot=[rake, 0, 0], pivot=[0, cy, cz])

    def cubes(self):
        return sum(len(bn["cubes"]) for bn in self.bones.values())

    # ---- shared parts
    def muzzle_flash(self, z, y=0.0, length=5.0, width=3.4):
        self.bone("muzzle_flash", "rifle", (0, y, z))
        for ang in (0, 45, 90, 135):
            self.cube("muzzle_flash", "flash", -width, y - 0.12, z - length, width, y + 0.12, z + 0.1,
                      rot=[0, 0, ang], pivot=[0, y, z])
        self.cube("muzzle_flash", "flash", -1.2, y - 1.2, z - length * 0.6, 1.2, y + 1.2, z + 0.1)
        self.cube("muzzle_flash", "flash", -0.5, y - 0.5, z - length * 1.5, 0.5, y + 0.5, z - length * 0.6)

    def casing(self, x, y, z, length=3.0, r=0.5):
        """Spent case at the ejection port (hidden until the fire animation shows it)."""
        self.bone("casing", "rifle", (x, y, z))
        self.bar("casing", "brass", x, y, z - length / 2, z + length / 2, r)

    def hand_left(self, y, z):
        """Support hand wrapped under the forend: palm below, four fingers up the right side, thumb on the left."""
        self.bone("left_hand", "rifle", (0, y, z))
        self.rbox("left_hand", "glove", -1.35, y - 1.2, z - 2.8, 1.35, y + 0.9, z + 2.8, c=0.4)       # palm
        for i in range(4):                                                                              # fingers
            zf = z - 2.5 + i * 1.35
            self.cube("left_hand", "glove", -2.3, y - 0.9, zf, -1.3, y + 1.9, zf + 1.2)
            self.cube("left_hand", "glove", -2.3, y + 1.6, zf + 0.1, -1.5, y + 2.4, zf + 1.1)
        self.cube("left_hand", "glove", 1.3, y - 0.2, z - 2.0, 1.9, y + 2.1, z + 0.4)                   # thumb
        self.rbox("left_hand", "glove", -1.3, y - 4.4, z + 1.6, 1.3, y - 0.6, z + 9.0, c=0.4)           # wrist + sleeve
        self.cube("left_hand", "olive", -1.45, y - 4.6, z + 5.5, 1.45, y - 0.3, z + 9.2)

    def hand_right(self, y, z, trigger_y):
        """Firing hand around the grip, index finger on the trigger; pivot is at the grip."""
        self.bone("right_hand", "rifle", (0, y, z))
        self.rbox("right_hand", "glove", -1.5, y - 2.6, z - 1.8, 1.4, y + 2.4, z + 1.8, c=0.45)         # palm/back of hand
        for i in range(3):                                                                              # wrapped fingers
            yf = y - 2.3 + i * 1.5
            self.cube("right_hand", "glove", -1.8, yf, z - 2.2, -1.2, yf + 1.4, z + 0.4)
        self.cube("right_hand", "glove", -1.7, trigger_y - 0.6, z - 4.4, -1.0, trigger_y + 0.6, z - 1.8)    # index finger
        self.cube("right_hand", "glove", 1.2, y + 0.4, z - 2.0, 1.8, y + 2.6, z - 0.2)                  # thumb
        self.rbox("right_hand", "glove", -1.2, y - 5.8, z + 0.8, 1.2, y - 0.8, z + 8.0, c=0.4)
        self.cube("right_hand", "olive", -1.35, y - 6.2, z + 4.0, 1.35, y - 0.6, z + 8.2)

    def hand_bolt(self, parent, x, y, z):
        """Glove that grabs the right-hand charging handle (child of the handle so it moves with it)."""
        self.bone("bolt_hand", parent, (x, y, z))
        self.rbox("bolt_hand", "glove", x - 2.0, y - 1.5, z - 1.6, x + 1.2, y + 1.4, z + 1.8, c=0.4)
        self.cube("bolt_hand", "glove", x - 2.4, y - 0.2, z - 1.8, x - 1.9, y + 1.2, z + 0.2)
        self.cube("bolt_hand", "glove", x - 1.6, y - 1.0, z - 2.4, x + 0.8, y + 0.6, z - 1.6)
        self.rbox("bolt_hand", "glove", x - 1.4, y - 5.0, z + 1.2, x + 1.0, y - 1.3, z + 9.0, c=0.4)
        self.cube("bolt_hand", "olive", x - 1.55, y - 5.2, z + 4.5, x + 1.15, y - 1.2, z + 9.2)

    def chain(self, b, mat, x0, x1, start_y, start_z, seg_len, depth, n, bend_deg, thick_taper=0.0):
        """Curved column (magazine body): n segments hanging from (start_y, start_z), each leaning a bit
        more toward the muzzle (bend_deg total).  Returns (end_y, end_z, final_angle_deg)."""
        y, z = start_y, start_z
        ang = 0.0
        for i in range(n):
            ang = bend_deg * (i + 0.5) / n
            a = math.radians(ang)
            cy, cz = y - math.cos(a) * seg_len / 2, z - math.sin(a) * seg_len / 2
            d = depth - thick_taper * i
            self.cube(b, mat, x0, cy - seg_len / 2 - 0.05, cz - d / 2, x1, cy + seg_len / 2 + 0.05, cz + d / 2,
                      rot=[-ang, 0, 0], pivot=[0, cy, cz])
            y, z = y - math.cos(a) * seg_len, z - math.sin(a) * seg_len
        return y, z, ang

    # ---- output: atlas packing + painting
    def _faces(self):
        for bn in self.bones.values():
            for c in bn["cubes"]:
                sx, sy, sz = c["size"]
                dims = {"north": (sx, sy), "south": (sx, sy), "east": (sz, sy), "west": (sz, sy),
                        "up": (sx, sz), "down": (sx, sz)}
                for face, (fw, fh) in dims.items():
                    yield c, face, max(2, int(round(fw * TEXEL))), max(2, int(round(fh * TEXEL)))

    def write(self, res, texture=True):
        rng = np.random.default_rng(self.seed)
        faces = sorted(self._faces(), key=lambda f: -f[3])
        for W in (256, 512, 1024):
            x = y = row_h = 0
            placed, ok = [], True
            for c, face, w, h in faces:
                if x + w > W:
                    x, y, row_h = 0, y + row_h + 1, 0
                if y + h > W:
                    ok = False
                    break
                placed.append((c, face, w, h, x, y))
                x += w + 1
                row_h = max(row_h, h)
            if ok:
                break
        assert ok, "texture atlas overflow"
        atlas = np.zeros((W, W, 4), dtype=np.uint8)
        atlas[..., 3] = 255
        glow = np.zeros_like(atlas)
        for c, face, w, h, px, py in placed:
            mat, flat = self._mats[id(c)]
            tile = _paint_face(mat, face, w, h, rng, flat)
            atlas[py:py + h, px:px + w, :3] = tile.astype(np.uint8)
            if mat in GLOW:
                glow[py:py + h, px:px + w, :3] = tile.astype(np.uint8)
                glow[py:py + h, px:px + w, 3] = 255
            c.setdefault("uv", {})[face] = {"uv": [px, py], "uv_size": [w, h]}
        # break coplanar faces apart (z-fighting shows up as flickering patches): every cube grows by its own tiny amount
        n = 0
        for bn in self.bones.values():
            for c in bn["cubes"]:
                e = 0.004 * (1 + (n * 7) % 29)
                n += 1
                c["origin"] = [round(o - e, 4) for o in c["origin"]]
                c["size"] = [round(sz + 2 * e, 4) for sz in c["size"]]
        geo = {"format_version": "1.12.0", "minecraft:geometry": [{
            "description": {"identifier": "geometry." + self.ident, "texture_width": W,
                            "texture_height": W, "visible_bounds_width": 8,
                            "visible_bounds_height": 6, "visible_bounds_offset": [0, 0, 0]},
            "bones": [self.bones[n] for n in self.order]}]}
        d = os.path.join(res, "assets/boltrifle/geo/item")
        os.makedirs(d, exist_ok=True)
        with open(os.path.join(d, self.ident + ".geo.json"), "w") as f:
            json.dump(geo, f, indent=1)
        t = os.path.join(res, "assets/boltrifle/textures/item")
        os.makedirs(t, exist_ok=True)
        Image.fromarray(atlas, "RGBA").save(os.path.join(t, self.ident + ".png"))
        Image.fromarray(glow, "RGBA").save(os.path.join(t, self.ident + "_glowmask.png"))
        print(self.ident, "cubes:", self.cubes(), "bones:", len(self.bones), "atlas", W)
