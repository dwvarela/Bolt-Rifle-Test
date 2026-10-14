"""Generates 16x16 item icons: ammo, magazines. Usage: gen_items.py <resources_dir>"""
import sys, os, json
from PIL import Image, ImageDraw

RES = sys.argv[1]
TEX = os.path.join(RES, "assets/boltrifle/textures/item")
MOD = os.path.join(RES, "assets/boltrifle/models/item")
os.makedirs(TEX, exist_ok=True); os.makedirs(MOD, exist_ok=True)

BRASS = [(122, 88, 28), (190, 142, 48), (232, 190, 84)]
STEEL = [(52, 56, 60), (96, 102, 108), (140, 148, 156)]
NICKEL = [(110, 112, 116), (170, 174, 180), (214, 218, 224)]


def cartridge(d, x0, y0, length, width, case, tip, neck=0, rim=True):
    """Vertical cartridge (tip up) with base at (x0, y0)."""
    top = y0 - length
    for dx in range(width):
        shade = case[2] if dx == 0 else case[0] if dx == width - 1 else case[1]
        for y in range(top + 3, y0 + 1):
            d.point((x0 + dx, y), fill=shade)
    # bullet
    bw = width - 1 if neck else width
    off = 1 if neck else 0
    for dx in range(bw):
        shade = tip[2] if dx == 0 else tip[0] if dx == bw - 1 else tip[1]
        for y in range(top, top + 4):
            if y == top and bw > 2 and (dx == 0 or dx == bw - 1):
                continue
            d.point((x0 + off + dx, y), fill=shade)
    if rim:
        d.line((x0 - 0, y0, x0 + width - 1, y0), fill=case[0])
        d.point((x0, y0), fill=case[2])


def rot(img):
    return img.rotate(-40, resample=Image.NEAREST, expand=False)


# id: (case, tip, length, width, count)
AMMO = {
    "ammo_308_win": (BRASS, [(120, 60, 30), (190, 100, 50), (225, 140, 80)], 12, 3),
    "ammo_762x51_nato": (BRASS, [(30, 30, 34), (60, 62, 66), (90, 92, 98)], 12, 3),
    "ammo_762x39": (STEEL, [(120, 60, 30), (190, 100, 50), (225, 140, 80)], 10, 3),
    "ammo_556x45_nato": (BRASS, [(30, 90, 40), (60, 150, 70), (110, 200, 120)], 11, 2),
    "ammo_223_rem": (BRASS, [(120, 60, 30), (190, 100, 50), (225, 140, 80)], 11, 2),
    "ammo_57x28": (NICKEL, [(30, 60, 120), (60, 100, 190), (110, 150, 230)], 9, 2),
    "ammo_46x30": (NICKEL, [(120, 30, 30), (190, 50, 50), (230, 100, 100)], 9, 2),
    "ammo_9x19": (BRASS, [(110, 70, 30), (170, 110, 50), (210, 150, 90)], 7, 3),
}
for name, (case, tip, length, width) in AMMO.items():
    img = Image.new("RGBA", (16, 16), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    cartridge(d, 5, 13, length, width, case, tip, neck=(1 if width == 2 or name.endswith("x28") else 0))
    cartridge(d, 9, 13, length, width, case, tip, neck=(1 if width == 2 or name.endswith("x28") else 0))
    out = rot(img)
    # darken outline for contrast
    px = out.load()
    edge = []
    for y in range(16):
        for x in range(16):
            if px[x, y][3] == 0:
                for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)):
                    nx, ny = x + dx, y + dy
                    if 0 <= nx < 16 and 0 <= ny < 16 and px[nx, ny][3] > 0:
                        edge.append((x, y)); break
    for e in edge:
        px[e] = (20, 20, 22, 255)
    out.save(os.path.join(TEX, name + ".png"))

BODY = [(40, 42, 46), (70, 74, 80), (104, 110, 118)]
POLY = [(58, 52, 44), (92, 84, 72), (124, 114, 98)]
WOOD = [(86, 56, 30), (124, 82, 44), (160, 112, 66)]


def box(d, x0, y0, x1, y1, c):
    d.rectangle((x0, y0, x1, y1), fill=c[1])
    d.line((x0, y0, x0, y1), fill=c[2]); d.line((x1, y0, x1, y1), fill=c[0])
    d.line((x0, y1, x1, y1), fill=c[0])


def mag(name, style):
    img = Image.new("RGBA", (16, 16), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    lips = (30, 30, 34)
    if style == 0:   # M700 short box
        box(d, 5, 5, 10, 14, BODY); d.rectangle((5, 3, 10, 5), fill=lips); d.line((6, 4, 9, 4), fill=BRASS[1])
    elif style == 1:  # SKS: small box with wood-tone base
        box(d, 5, 3, 10, 13, BODY); box(d, 5, 12, 10, 14, WOOD)
    elif style == 2:  # AK banana
        for i, y in enumerate(range(2, 15)):
            x = 4 + int(i * i / 22)
            box(d, x, y, x + 5, y, STEEL if i % 2 else BODY)
        d.rectangle((4, 1, 9, 2), fill=lips)
    elif style == 3:  # M14 long straight
        box(d, 4, 1, 11, 14, BODY)
        for y in (4, 7, 10): d.line((5, y, 10, y), fill=BODY[0])
    elif style == 4:  # STANAG, slight curve
        for i, y in enumerate(range(2, 15)):
            x = 5 + int(i / 5)
            box(d, x, y, x + 5, y, POLY if i % 2 else BODY)
        d.rectangle((5, 1, 10, 2), fill=lips)
    elif style == 5:  # P90: translucent flat
        box(d, 2, 5, 13, 10, (( 60, 70, 60), (110, 130, 105), (170, 190, 160)))
        d.line((3, 7, 12, 7), fill=BRASS[1]); d.line((3, 8, 12, 8), fill=BRASS[0])
    elif style == 6:  # MP7 long thin
        box(d, 6, 1, 9, 14, BODY); d.line((7, 3, 8, 3), fill=BRASS[1])
    else:            # Glock
        box(d, 5, 3, 10, 14, BODY); d.rectangle((5, 3, 10, 4), fill=lips); d.line((6, 12, 9, 12), fill=BODY[2])
    px = img.load()
    edge = []
    for y in range(16):
        for x in range(16):
            if px[x, y][3] == 0:
                for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)):
                    nx, ny = x + dx, y + dy
                    if 0 <= nx < 16 and 0 <= ny < 16 and px[nx, ny][3] > 0:
                        edge.append((x, y)); break
    for e in edge:
        px[e] = (16, 16, 18, 255)
    img.save(os.path.join(TEX, name + ".png"))


MAGS = {"mag_m700": 0, "mag_sks": 1, "mag_ak": 2, "mag_m14": 3, "mag_stanag": 4, "mag_p90": 5, "mag_mp7": 6, "mag_g45": 7}
for n, s in MAGS.items():
    mag(n, s)

for n in list(AMMO) + list(MAGS):
    with open(os.path.join(MOD, n + ".json"), "w") as f:
        json.dump({"parent": "minecraft:item/generated", "textures": {"layer0": "boltrifle:item/" + n}}, f, indent=1)
print("items:", len(AMMO) + len(MAGS))
