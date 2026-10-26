"""AK-47 (Type 3, wood furniture): slim stamped receiver, curved magazine, ladder rear sight."""
import os
from meshbake import MModel, mid
from sdf import *
import gun_m700 as g7

ID = "ak47"


def hands(m):
    """Glove hands (same builder as the M700/M14): support hand cupping the handguard, firing hand on the pistol grip, three fingers round
    the grip and the index finger on the trigger."""
    g = mid("glove")
    L = m.mesh("left_hand", "rifle", (0, -3.3, -12.4), tris=1800)
    g7.glove(L, (0.46, -2.2, -9.9), (-0.2, 0.0, -0.98), (-0.45, 0.89, 0.0), (1, 0.3, 0), g, (22, 32, 28),
             [(1.3, 0.9, 0.2), (2.0, 2.0, 0.7), (2.0, 3.1, 1.4)], (3.5, -9.0, -3.0))
    R = m.mesh("right_hand", "rifle", (0, -5.0, 5.0), tris=1800)
    g7.glove(R, (-1.5, -5.0, 7.5), (0.0, -0.28, -0.96), (1, 0, 0), (0, 1, 0), g, (80, 55, 40),
             [(1.25, 0.8, 0.3), (1.9, 1.9, 0.9), (1.9, 3.0, 1.7)], (-3.5, -9.5, 17.0), flen=1.1,
             index_pts=[(-1.45, -4.0, 6.0), (-1.4, -3.7, 4.4), (-1.0, -3.45, 3.0), (-0.6, -3.35, 2.4), (-0.2, -3.3, 2.1)])


GLB = os.path.join(os.path.dirname(os.path.abspath(__file__)), "ref", "ak47_goldbergr.glb")   # AK-47 by GoldbergR (Sketchfab), see CREDITS.md
S_GLB, Z0_GLB, Y0_GLB = 53.6, 4.98, 0.0846                                                     # metres -> model px, muzzle tip at z=-27.9, bore axis y=0


def to_model(V):
    """glTF metres (+z = muzzle, shooter's right = -x) -> model px (muzzle = -z, JSON x as in the other guns)."""
    import numpy as np
    return np.stack([V[:, 0] * S_GLB, (V[:, 1] - Y0_GLB) * S_GLB, Z0_GLB - V[:, 2] * S_GLB], 1)


def build():
    import numpy as np
    import glbsdf
    m = MModel(ID, lo=(-5.0, -12.5, -30.5), hi=(5.0, 3.5, 23.0), h=float(os.environ.get("H", "0.10")), seed=11, tx=9)
    parts, _ = glbsdf.load_parts(GLB)
    MAT = {0: "gunmetal", 1: "plum", 2: "black", 3: "black", 4: "brass", 5: "steel", 6: "rubber"}
    bones = {"receiver": m.mesh("receiver", "rifle", (0, 0, 0), tris=6500), "wood": m.mesh("wood", "rifle", (0, 0, 0), tris=2600),
             "buttstock": m.mesh("buttstock", "rifle", (0, 0, 0), tris=1800), "bolt": m.mesh("bolt", "rifle", (0, 0, 0), tris=1500),
             "magazine": m.mesh("magazine", "rifle", (0, -2.6, -5.2), tris=3200)}
    for p in parts:
        path = " / ".join(p["path"])
        if "Bolt" in path: bone = "bolt"
        elif "Magazine 1" in path: bone = "magazine"
        elif "Buttstock" in path: bone = "buttstock"
        elif p["mat"] == 1: bone = "wood"
        else: bone = "receiver"
        glbsdf.add_part(bones[bone], to_model(p["V"]), p["F"], mid(MAT[p["mat"]]))
    m.muzzle_flash(-27.9)
    m.casing(-1.0, 0.9, -1.0)
    hands(m)

    cfg = dict(
        name=ID, hand_l=(-3.3, -12.4), mag_grip=(-18.2, -10.8), grip_x=-0.3, mag_drop=9.0, mag_rock=17, lift_px=9.0,
        charge_hand="right", hand_r=(-5.0, 7.0), handle=(-1.7, 0.7, -6.0), bolt_travel=6.0, charge_roll=True,
        hand_frame=((-1.5, -5.0, 7.5), (0.0, -0.28, -0.96), (1, 0, 0)), hand_piv=(0, -5.0, 5.0), handle_grip=(-2.6, 1.6, -5.2), hold_open=False,
        fire_len=0.28, cycle=0.10, kick_z=2.3, kick_pitch=3.2, kick_yaw=0.8, flash=1.1,
        reload_len=2.3, charge_len=1.1, release_len=0.0, eject=(-1.0, 1.0, 0.9),
        sight=(3.35, -5.7), butt=19.9,
    )
    return m, cfg
