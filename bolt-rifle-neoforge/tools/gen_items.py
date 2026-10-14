"""Item icons (32x32, drawn at 8x and shaded): cartridges and magazines. Usage: gen_items.py <resources_dir>"""
import sys, os, json, math
import numpy as np
from PIL import Image, ImageDraw, ImageFilter

RES = sys.argv[1]
TEX = os.path.join(RES, "assets/boltrifle/textures/item")
MOD = os.path.join(RES, "assets/boltrifle/models/item")
os.makedirs(TEX, exist_ok=True); os.makedirs(MOD, exist_ok=True)
N, SS = 32, 8
S = N * SS
LIGHT = np.array([-0.55, 0.83])           # light from upper-left (x, y-up)


def rgb(c): return np.array(c, dtype=float)


def finish(canvas, name, outline=(18, 18, 22)):
    """canvas: float RGBA (S,S,4) -> downsample, add a thin dark outline, save."""
    a = canvas[..., 3]
    img = Image.fromarray(np.clip(canvas, 0, 255).astype(np.uint8), "RGBA").resize((N, N), Image.BOX)
    arr = np.array(img).astype(float)
    alpha = arr[..., 3] > 90
    pad = np.pad(alpha, 1)
    nb = pad[:-2, 1:-1] | pad[2:, 1:-1] | pad[1:-1, :-2] | pad[1:-1, 2:]
    edge = nb & ~alpha
    arr[edge] = [*outline, 255]
    arr[~alpha & ~edge, 3] = 0
    arr[alpha, 3] = 255
    Image.fromarray(arr.astype(np.uint8), "RGBA").save(os.path.join(TEX, name + ".png"))


def blank():
    return np.zeros((S, S, 4))


def put(canvas, mask, color_fn):
    ys, xs = np.nonzero(mask)
    col = color_fn(xs, ys)
    canvas[ys, xs, :3] = col
    canvas[ys, xs, 3] = 255


YY, XX = np.mgrid[0:S, 0:S]


def rotated_coords(cx, cy, ang):
    """local (s along axis, t across) for every pixel of a shape rotated by ang (deg, 0 = pointing up)."""
    a = math.radians(ang)
    dx, dy = XX - cx, -(YY - cy)
    s = dx * math.sin(a) + dy * math.cos(a)
    t = dx * math.cos(a) - dy * math.sin(a)
    return s, t


# ------------------------------------------------------------------ cartridges
def cartridge(canvas, cx, cy, ang, mm_scale, spec):
    """Draw one cartridge. spec: dict(len, case_len, case_d, neck_d, bullet_d, case, jacket, tip, rim_d)"""
    k = mm_scale * SS
    s, t = rotated_coords(cx, cy, ang)
    s = s / k; t = t / k                          # now in millimetres, base at s=0 (shifted below)
    L = spec["len"]
    s = s + L / 2                                 # centre the cartridge on (cx, cy)
    cl, cd, nd, bd = spec["case_len"], spec["case_d"], spec["neck_d"], spec["bullet_d"]
    # radius profile along the axis
    shoulder = spec.get("shoulder", 4.0)
    r = np.zeros_like(s)
    inside = (s >= 0) & (s <= L)
    body = (s >= 0) & (s <= cl - shoulder)
    r = np.where(body, cd / 2, r)
    sh = (s > cl - shoulder) & (s <= cl)
    f = np.clip((s - (cl - shoulder)) / shoulder, 0, 1)
    r = np.where(sh, cd / 2 + (nd / 2 - cd / 2) * f, r)
    bl = (s > cl) & (s <= L)
    # bullet ogive: radius tapers to the tip
    g = np.clip((s - cl) / max(L - cl, 1e-6), 0, 1)
    bullet_r = bd / 2 * np.sqrt(np.clip(1 - np.where(g > spec.get("ogive_start", 0.45), ((g - spec.get("ogive_start", 0.45)) / (1 - spec.get("ogive_start", 0.45))) ** 1.6, 0), 0, 1)) * (1 - 0.0 * g)
    bullet_r = np.where(g >= 1, 0, np.maximum(bullet_r, 0.25 * (1 - g) * 0 + 0.0))
    r = np.where(bl, np.maximum(bullet_r, bd * 0.12), r)
    rim = spec.get("rim_d", cd + 0.7)
    r = np.where((s >= 0) & (s <= 1.1), rim / 2, r)
    r = np.where((s > 1.1) & (s <= 1.9), cd / 2 - 0.45, r)        # extractor groove
    mask = inside & (np.abs(t) <= r) & (r > 0)
    if not mask.any():
        return
    u = np.clip(t / np.maximum(r, 1e-6), -1, 1)
    nz = np.sqrt(1 - u * u)
    # rotate the light into the cartridge frame
    a = math.radians(ang)
    lx = LIGHT[0] * math.cos(a) + LIGHT[1] * math.sin(a) * -1
    lam = np.clip(u * lx * -1 * 0 + (u * (-LIGHT[0] * math.cos(a) + LIGHT[1] * math.sin(a))) * -1 + nz * 0.55, 0, 1)
    spec_hi = np.exp(-((u + 0.45) ** 2) / 0.012) * 0.55
    shade = 0.42 + 0.78 * lam + spec_hi

    def colour(xs, ys):
        ss = s[ys, xs]
        out = np.zeros((len(xs), 3))
        case = rgb(spec["case"]); jac = rgb(spec["jacket"]); tip = rgb(spec["tip"])
        c = np.where((ss <= cl)[:, None], case, jac)
        if spec.get("tip_len"):
            c = np.where((ss > L - spec["tip_len"])[:, None], tip, c)
        if spec.get("seal"):                                      # red/black primer annulus + crimp ring at the neck
            c = np.where(((ss > cl - 0.6) & (ss <= cl + 0.5))[:, None], rgb(spec["seal"]), c)
        base = (ss <= 1.1)[:, None]
        c = np.where(base, case * 0.85, c)
        # primer at the very base
        return c * shade[ys, xs][:, None]
    put(canvas, mask, colour)
    # primer disc: a lighter circle seen end-on is not visible from the side; add a small highlight band instead
    return


BRASS = (205, 152, 62)
COPPER = (186, 104, 56)
STEEL_CASE = (96, 102, 96)
NICKEL = (190, 192, 196)
SPECS = {
    "ammo_308_win":    dict(len=71.1, case_len=51.2, case_d=11.9, neck_d=8.6, bullet_d=7.82, case=BRASS, jacket=COPPER, tip=(90, 50, 30), tip_len=7, shoulder=5.5, ogive_start=0.35),
    "ammo_762x51_nato": dict(len=69.9, case_len=51.2, case_d=11.9, neck_d=8.6, bullet_d=7.82, case=BRASS, jacket=(168, 112, 60), tip=(30, 30, 34), tip_len=2.5, shoulder=5.5, ogive_start=0.4, seal=(150, 40, 36)),
    "ammo_762x39":     dict(len=56.0, case_len=38.7, case_d=11.35, neck_d=8.6, bullet_d=7.9, case=STEEL_CASE, jacket=COPPER, tip=(60, 60, 60), tip_len=0, shoulder=4.5, ogive_start=0.4),
    "ammo_556x45_nato": dict(len=57.4, case_len=44.7, case_d=9.5, neck_d=6.4, bullet_d=5.7, case=BRASS, jacket=(180, 118, 70), tip=(46, 128, 60), tip_len=4.5, shoulder=4.5, ogive_start=0.3),
    "ammo_223_rem":    dict(len=57.4, case_len=44.7, case_d=9.5, neck_d=6.4, bullet_d=5.7, case=BRASS, jacket=COPPER, tip=COPPER, tip_len=0, shoulder=4.5, ogive_start=0.35),
    "ammo_57x28":      dict(len=40.5, case_len=28.9, case_d=7.9, neck_d=6.5, bullet_d=5.7, case=(104, 108, 116), jacket=(150, 154, 160), tip=(40, 70, 150), tip_len=4.0, shoulder=3.5, ogive_start=0.3),
    "ammo_46x30":      dict(len=38.0, case_len=30.0, case_d=8.0, neck_d=5.6, bullet_d=4.65, case=BRASS, jacket=(160, 164, 170), tip=(140, 40, 40), tip_len=4.0, shoulder=3.5, ogive_start=0.3),
    "ammo_9x19":       dict(len=29.7, case_len=19.15, case_d=9.9, neck_d=9.65, bullet_d=9.02, case=(214, 168, 80), jacket=(150, 86, 52), tip=COPPER, tip_len=0, shoulder=0.8, ogive_start=0.15),
}
LAYOUT = {   # (scale px/mm in 32 space, count)
    "ammo_308_win": (0.34, 2), "ammo_762x51_nato": (0.34, 2), "ammo_762x39": (0.40, 2),
    "ammo_556x45_nato": (0.40, 2), "ammo_223_rem": (0.40, 2),
    "ammo_57x28": (0.50, 2), "ammo_46x30": (0.56, 3), "ammo_9x19": (0.64, 2),
}
for name, spec in SPECS.items():
    scale, count = LAYOUT[name]
    cv = blank()
    fan = {2: [(-6.0, 3.0, 28), (4.0, -1.0, 24)], 3: [(-7.0, 3.5, 22), (0.0, 0.0, 28), (7.0, -3.0, 34)]}[count]
    order = fan if count == 2 else fan
    for dx, dy, ang in order:
        cartridge(cv, S / 2 + dx * SS, S / 2 + dy * SS, ang, scale, spec)
    finish(cv, name)


# ------------------------------------------------------------------ magazines
def poly_mask(pts):
    im = Image.new("L", (S, S), 0)
    ImageDraw.Draw(im).polygon([(x * SS, y * SS) for x, y in pts], fill=255)
    return np.array(im) > 127


def shaded(canvas, pts, base, ang=0.0, hi=1.25, lo=0.62, band=None, grain=0.0):
    """Fill a polygon with a left-lit gradient across its width (cylindrical-ish look)."""
    m = poly_mask(pts)
    ys, xs = np.nonzero(m)
    x0, x1 = xs.min(), xs.max() + 1
    u = (xs - x0) / max(1, (x1 - x0 - 1))
    shade = lo + (hi - lo) * np.exp(-((u - 0.25) ** 2) / 0.18)
    if band:
        shade = shade * band(u)
    col = rgb(base)[None, :] * shade[:, None]
    if grain:
        col = col * (1 + grain * np.sin(ys * 0.9 + xs * 0.2)[:, None])
    canvas[ys, xs, :3] = col
    canvas[ys, xs, 3] = 255


def rib_lines(canvas, x0, x1, ys_, color, th=0.5):
    for y in ys_:
        im = Image.new("L", (S, S), 0)
        ImageDraw.Draw(im).rectangle([x0 * SS, y * SS, x1 * SS, (y + th) * SS], fill=255)
        m = np.array(im) > 127
        m &= canvas[..., 3] > 0
        canvas[m, :3] = rgb(color)


def curve(x_top, y_top, y_bot, bend, width, steps=24):
    """Left/right edges of a column that curves toward -x as it goes down (like banana mags)."""
    left, right = [], []
    for i in range(steps + 1):
        f = i / steps
        y = y_top + (y_bot - y_top) * f
        x = x_top - bend * f * f
        left.append((x - width / 2, y)); right.append((x + width / 2, y))
    return left + right[::-1]


def mag(name):
    cv = blank()
    if name == "mag_m700":                      # short steel/polymer box
        shaded(cv, [(11, 8), (21, 8), (21, 27), (11, 27)], (46, 48, 54), grain=0.02)
        shaded(cv, [(11, 5), (21, 5), (21, 8.5), (11, 8.5)], (150, 154, 160))
        shaded(cv, [(10.5, 27), (21.5, 27), (21.5, 29), (10.5, 29)], (120, 124, 130))
        rib_lines(cv, 11, 21, (12, 17, 22), (20, 20, 24))
        rib_lines(cv, 12, 20, (6.2,), (200, 150, 60), 0.9)
    elif name == "mag_sks":                     # steel box with a wood-brown floorplate
        shaded(cv, [(10, 6), (22, 6), (22, 26), (10, 26)], (66, 70, 76), grain=0.02)
        shaded(cv, [(10, 4), (22, 4), (22, 6.5), (10, 6.5)], (150, 154, 160))
        shaded(cv, [(9.5, 26), (22.5, 26), (22.5, 29), (9.5, 29)], (112, 70, 40), grain=0.15)
        rib_lines(cv, 10, 22, (10, 14, 18, 22), (30, 32, 36))
        rib_lines(cv, 11, 21, (5,), (200, 150, 60), 0.9)
    elif name == "mag_ak":                      # orange bakelite banana
        pts = curve(18, 3, 29, 8, 9)
        shaded(cv, pts, (150, 70, 30), hi=1.3, lo=0.55, grain=0.03)
        for f in (0.15, 0.28, 0.41, 0.54, 0.67, 0.80):
            y = 3 + 26 * f; x = 18 - 8 * f * f
            rib_lines(cv, x - 4.5, x + 4.5, (y,), (92, 40, 18), 0.5)
        shaded(cv, [(18 - 8 - 5.2, 28.5), (18 - 8 + 4.2, 28.5), (18 - 8 + 4.2, 30.5), (18 - 8 - 5.2, 30.5)], (60, 60, 64))
        shaded(cv, [(13.5, 1.5), (22.5, 1.5), (22.5, 3.6), (13.5, 3.6)], (80, 84, 90))
    elif name == "mag_m14":                     # long straight blued steel
        shaded(cv, [(10, 3), (22, 3), (22, 28), (10, 28)], (58, 66, 84), grain=0.02)
        shaded(cv, [(10, 1.5), (22, 1.5), (22, 3.4), (10, 3.4)], (150, 154, 160))
        shaded(cv, [(9.5, 28), (22.5, 28), (22.5, 30), (9.5, 30)], (110, 114, 120))
        rib_lines(cv, 10, 22, (6, 9, 12, 15, 18, 21, 24), (30, 36, 50), 0.4)
        rib_lines(cv, 11, 21, (2.6,), (200, 150, 60), 0.8)
    elif name == "mag_stanag":                  # black polymer with ribbed face
        pts = curve(18, 3, 29, 3.5, 9)
        shaded(cv, pts, (52, 54, 58), hi=1.3, lo=0.6, grain=0.04)
        for f in (0.12, 0.2, 0.28, 0.36, 0.44, 0.52, 0.60, 0.68, 0.76, 0.84):
            y = 3 + 26 * f; x = 18 - 3.5 * f * f
            rib_lines(cv, x - 3.4, x + 3.4, (y,), (24, 25, 28), 0.35)
        shaded(cv, [(18 - 3.5 - 5.2, 28.6), (18 - 3.5 + 4.4, 28.6), (18 - 3.5 + 4.4, 30.4), (18 - 3.5 - 5.2, 30.4)], (86, 88, 92))
        shaded(cv, [(13.5, 1.6), (22.5, 1.6), (22.5, 3.4), (13.5, 3.4)], (140, 144, 150))
    elif name == "mag_p90":                     # flat translucent smoke polymer, rounds visible
        shaded(cv, [(3, 11), (29, 11), (29, 21), (3, 21)], (70, 82, 74), hi=1.2, lo=0.8)
        for i in range(8):
            x = 5 + i * 3.1
            shaded(cv, [(x, 13), (x + 2.2, 13), (x + 2.2, 19), (x, 19)], (180, 134, 56), hi=1.2, lo=0.7)
        shaded(cv, [(2, 10), (30, 10), (30, 11.4), (2, 11.4)], (30, 32, 34))
        shaded(cv, [(2, 20.6), (30, 20.6), (30, 22), (2, 22)], (30, 32, 34))
    elif name == "mag_mp7":                     # long thin black stick with extended floorplate
        shaded(cv, [(12, 2), (20, 2), (20, 27), (12, 27)], (36, 38, 42), hi=1.35, grain=0.03)
        shaded(cv, [(11, 27), (21, 27), (21, 30), (11, 30)], (70, 72, 78))
        rib_lines(cv, 12, 20, (6, 10, 14, 18, 22), (18, 18, 20), 0.35)
        shaded(cv, [(12, 1), (20, 1), (20, 2.6), (12, 2.6)], (150, 154, 160))
        rib_lines(cv, 13, 19, (4,), (200, 150, 60), 0.9)
    elif name == "mag_g45":                     # pistol mag: steel body, polymer floorplate, round witness holes
        shaded(cv, [(11, 5), (21, 5), (21, 25), (11, 25)], (78, 82, 90), grain=0.02)
        shaded(cv, [(11, 3), (21, 3), (21, 5.4), (11, 5.4)], (30, 32, 36))
        shaded(cv, [(10, 25), (22.5, 25), (22.5, 28.5), (10, 28.5)], (40, 42, 46), hi=1.3)
        for i, y in enumerate((8, 11, 14, 17, 20, 23)):
            sz = 1.0
            rib_lines(cv, 15.2, 16.8, (y,), (14, 14, 16), 0.9)
        rib_lines(cv, 12, 20, (6.0,), (200, 150, 60), 0.8)
    finish(cv, name)


MAGS = ["mag_m700", "mag_sks", "mag_ak", "mag_m14", "mag_stanag", "mag_p90", "mag_mp7", "mag_g45"]
for n in MAGS:
    mag(n)
for n in list(SPECS) + MAGS:
    with open(os.path.join(MOD, n + ".json"), "w") as f:
        json.dump({"parent": "minecraft:item/generated", "textures": {"layer0": "boltrifle:item/" + n}}, f, indent=1)
print("items:", len(SPECS) + len(MAGS))
