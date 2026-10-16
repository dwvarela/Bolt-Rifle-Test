"""Inventory icons for the attachment items: renders each att_<id> model from the side (render_mesh), keys out the background,
crops and scales to 64x64.  Usage: python3 gen_att_icons.py <resources_dir> [ids]"""
import subprocess, sys, os, json
import numpy as np
from PIL import Image

res = sys.argv[1]
ids = sys.argv[2:] or ["red_dot", "holo", "acog", "scope", "flash_hider", "muzzle_brake", "suppressor"]
here = os.path.dirname(os.path.abspath(__file__))
tmp = "/tmp/att_icon_tmp"
os.makedirs(tmp, exist_ok=True)
for i in ids:
    out = f"{tmp}/{i}.png"
    subprocess.run([sys.executable, f"{here}/render_mesh.py", res, "att_" + i, out, "62", "18", "40", "none"], check=True,
                   stdout=subprocess.DEVNULL)
    im = np.array(Image.open(f"{tmp}/{i}_0.png").convert("RGB")).astype(int)
    bg = (np.abs(im - 238).sum(2) < 6)
    a = np.where(bg, 0, 255).astype(np.uint8)
    rgba = np.dstack([im.astype(np.uint8), a])
    ys, xs = np.where(a > 0)
    rgba = rgba[ys.min():ys.max() + 1, xs.min():xs.max() + 1]
    h, w = rgba.shape[:2]
    s = max(h, w)
    sq = np.zeros((s, s, 4), np.uint8)
    sq[(s - h) // 2:(s - h) // 2 + h, (s - w) // 2:(s - w) // 2 + w] = rgba
    Image.fromarray(sq).resize((64, 64), Image.LANCZOS).save(f"{res}/assets/boltrifle/textures/item/{i}.png")
    with open(f"{res}/assets/boltrifle/models/item/{i}.json", "w") as f:
        json.dump({"parent": "minecraft:item/generated", "textures": {"layer0": "boltrifle:item/" + i}}, f, indent=1)
    print("icon", i)
