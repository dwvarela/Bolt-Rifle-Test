"""Flat inventory icons for the guns: a clean side view rendered from the real model, outlined, 64x64.
Usage: gen_gun_icons.py <resources_dir>"""
import os, subprocess, sys, tempfile
import numpy as np
from PIL import Image, ImageFilter

RES = sys.argv[1]
HERE = os.path.dirname(os.path.abspath(__file__))
IDS = ["bolt_rifle", "sks", "ak47", "m14ebr", "m4a1", "mini14", "mp7", "p90", "glock19"]
HIDE = "bolt_hand,casing,muzzle_flash,left_hand,right_hand,chamber_round"
out_dir = os.path.join(RES, "assets/boltrifle/textures/item")
tmp = tempfile.mkdtemp()
for gid in IDS:
    png = os.path.join(tmp, gid + ".png")
    env = dict(os.environ, GUN=gid)
    subprocess.run([sys.executable, os.path.join(HERE, "render.py"), RES, png, HIDE, "0", "0", "30"], env=env, check=True,
                   stdout=subprocess.DEVNULL)
    im = Image.open(os.path.join(tmp, gid + "_0.png")).convert("RGB")
    a = np.array(im)
    bg = a[0, 0]
    mask = np.any(np.abs(a.astype(int) - bg.astype(int)) > 2, axis=2)
    ys, xs = np.where(mask)
    box = (xs.min(), ys.min(), xs.max() + 1, ys.max() + 1)
    rgba = np.dstack([a, (mask * 255).astype(np.uint8)])
    img = Image.fromarray(rgba, "RGBA").crop(box)
    w, h = img.size
    k = min(58 / w, 44 / h)
    img = img.resize((max(1, round(w * k)), max(1, round(h * k))), Image.LANCZOS)
    # contrast + saturation so wood/steel/polymer read apart at a glance
    arr = np.array(img).astype(float)
    lum = arr[..., :3].mean(axis=2, keepdims=True)
    arr[..., :3] = np.clip((arr[..., :3] - lum) * 1.35 + lum * 1.0, 0, 255)
    arr[..., :3] = np.clip((arr[..., :3] - 110) * 1.25 + 120, 0, 255)
    arr[..., 3] = (arr[..., 3] > 100) * 255
    img = Image.fromarray(arr.astype(np.uint8), "RGBA")
    canvas = Image.new("RGBA", (64, 64), (0, 0, 0, 0))
    ox, oy = (64 - img.width) // 2, (64 - img.height) // 2
    alpha = np.array(img)[..., 3]
    grown = Image.fromarray(alpha, "L").filter(ImageFilter.MaxFilter(3))
    outline = Image.new("RGBA", img.size, (14, 14, 18, 255))
    canvas.paste(outline, (ox, oy), grown)
    canvas.paste(img, (ox, oy), img)
    canvas.save(os.path.join(out_dir, "icon_%s.png" % gid))
    print("icon", gid, img.size)
