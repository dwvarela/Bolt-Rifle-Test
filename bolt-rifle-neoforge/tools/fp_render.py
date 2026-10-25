"""First-person simulator: renders what the player sees (camera space, vertical FOV 70, 16:9) for a gun/animation/time.
Usage: fp_render.py <res> <gun_id> <anim> <t1,t2,..> <out.png> <hip|ads> <scale> <tx,ty,tz> [hide]
cam = hand(0.56,-0.52,-0.72) + t + s*(-jx/16, jy/16+0.01, jz/16)   (GeckoLib x mirror, verified for ADS centring)"""
import sys, math, os
import numpy as np
from PIL import Image, ImageDraw
res, gid, anim, times, OUTF, mode, S, T = sys.argv[1:9]
hide = sys.argv[9] if len(sys.argv) > 9 else ""
S = float(S); T = np.array([float(x) for x in T.split(",")])
sys.argv = ["pose_render.py", res, gid, anim, times, "/dev/null", "side", "1", hide]
src = open(__file__.replace("fp_render.py", "pose_render.py")).read().split("# one fixed frame")[0]
exec(src)
_chan = chan
POSE = os.environ.get("POSE")
if POSE:
    pv = [float(x) for x in POSE.split(",")]
    def chan(bone, name, t, default):
        if bone == "rifle" and name == "position": return np.array(pv[:3])
        if bone == "rifle" and name == "rotation": return np.array(pv[3:])
        return _chan(bone, name, t, default)
BUTT = os.environ.get("BUTT")
if BUTT:
    _c2 = chan
    bd, bz = [float(x) for x in BUTT.split(",")]
    def chan(bone, name, t, default):
        if bone == "buttstock" and name == "rotation": return np.array([-bd, 0, 0])
        if bone == "buttstock" and name == "position": return np.array([0, bz * math.sin(math.radians(bd)), 0])
        return _c2(bone, name, t, default)
H = np.array([0.56, -0.52, -0.72])
import fp_cov as _C
_RV = _C._R(*[float(x) for x in os.environ.get('RV', '0,0,0').split(',')])
W, Hh = 960, 540
f = (Hh / 2) / math.tan(math.radians(35))
ts = [float(x) for x in times.split(",")]
frames = []
for t in ts:
    img = np.full((Hh, W, 3), (120, 160, 200), np.uint8)
    zb = np.full((Hh, W), 1e9)
    for pw, uv in tris_at(t):
        c = (_RV @ (np.stack([-pw[:, 0] / 16, pw[:, 1] / 16 + 0.01, pw[:, 2] / 16], 1) * S).T).T + H + T
        if (c[:, 2] > -0.05).any():
            continue
        sx = W / 2 + f * c[:, 0] / -c[:, 2]
        sy = Hh / 2 - f * c[:, 1] / -c[:, 2]
        x0, x1 = int(max(sx.min(), 0)), int(min(sx.max() + 1, W - 1)); y0, y1 = int(max(sy.min(), 0)), int(min(sy.max() + 1, Hh - 1))
        if x1 < x0 or y1 < y0:
            continue
        gx, gy = np.meshgrid(np.arange(x0, x1 + 1), np.arange(y0, y1 + 1))
        d = (sy[1] - sy[2]) * (sx[0] - sx[2]) + (sx[2] - sx[1]) * (sy[0] - sy[2])
        if abs(d) < 1e-9:
            continue
        l0 = ((sy[1] - sy[2]) * (gx + .5 - sx[2]) + (sx[2] - sx[1]) * (gy + .5 - sy[2])) / d
        l1 = ((sy[2] - sy[0]) * (gx + .5 - sx[2]) + (sx[0] - sx[2]) * (gy + .5 - sy[2])) / d
        l2 = 1 - l0 - l1
        m = (l0 >= 0) & (l1 >= 0) & (l2 >= 0)
        if not m.any():
            continue
        z = l0 * -c[0, 2] + l1 * -c[1, 2] + l2 * -c[2, 2]
        u = (l0 * uv[0, 0] + l1 * uv[1, 0] + l2 * uv[2, 0]) * TW
        v = (l0 * uv[0, 1] + l1 * uv[1, 1] + l2 * uv[2, 1]) * TH
        col = tex[np.clip(v.astype(int), 0, TH - 1), np.clip(u.astype(int), 0, TW - 1)]
        upd = m & (z < zb[gy, gx])
        zb[gy[upd], gx[upd]] = z[upd]
        img[gy[upd], gx[upd]] = col[upd]
    im = Image.fromarray(img); d = ImageDraw.Draw(im)
    d.line((W / 2 - 8, Hh / 2, W / 2 + 8, Hh / 2), fill=(255, 0, 0)); d.line((W / 2, Hh / 2 - 8, W / 2, Hh / 2 + 8), fill=(255, 0, 0))
    d.text((6, 4), f"{mode} t={t:.2f}", fill=(0, 0, 0))
    frames.append(im.resize((480, 270)) if not os.environ.get("FULL") else im)
cols = min(len(frames), 3); rows = (len(frames) + cols - 1) // cols
FW, FH = (960, 540) if os.environ.get("FULL") else (480, 270)
sheet = Image.new("RGB", (FW * cols, FH * rows))
for i, fr in enumerate(frames):
    sheet.paste(fr, ((i % cols) * FW, (i // cols) * FH))
sheet.save(OUTF); print("saved", OUTF)
