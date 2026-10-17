"""M14 EBR (Mk14 Mod 0 in the Sage chassis) - SDF mesh model.
The whole side silhouette (handguard with its slots, rails, grip, stock plates, trigger guard, magazine) is TRACED from the
reference side photo (tools/trace/m14_side.json, made with trace_side.py) and extruded to a width per component; barrel, flash hider,
sights and details are placed at positions measured from the same photo.  It has iron sights and a top rail: no built-in scope."""
import math
from meshbake import MModel, mid
from sdf import *

ID = "m14ebr"
import os
SIL = os.path.join(os.path.dirname(os.path.abspath(__file__)), "trace", "m14_side.json")
SY, SZ = 1.95, 4.4          # rear aperture centre (iron sights)
RAIL_TOP, RAIL_Z = 1.38, -9.0   # optic mount on the top rail


def build():
    m = MModel(ID, lo=(-3.2, -9.6, -38.0), hi=(3.2, 3.2, 24.8), h=0.14, seed=31, tx=9)
    def real_hole(c, size):
        z, y = c
        if z < -3.0:                      # handguard slots, gaps around the gas block
            return True
        if z > 19.4:                      # stock plate holes
            return True
        return abs(z - 5.4) < 0.3 and abs(y + 3.2) < 0.3 or (abs(z - 6.4) < 0.3 and abs(y + 2.4) < 0.3)   # trigger guard opening, grip gap

    sil = Traced.load(SIL, res=0.03, keep=real_hole)

    def side(vol, mat, hw, r, z0, z1, y0, y1, k=0.0):
        vol.add(Clip(Ext(sil, "zy", -hw, hw, r=r), z0=z0, z1=z1, y0=y0, y1=y1), mat=mat, k=k)

    # ------------------------------------------------------------------ chassis: handguard, grip, buffer tube, stock, magazine well
    ch = m.mesh("chassis", "rifle", (0, 0, 0), tris=11500)
    alu, blk, poly = mid("alu"), mid("black"), mid("poly")
    side(ch, alu, 1.45, 0.6, -21.7, -3.5, -3.05, 1.12)            # slotted handguard body
    side(ch, alu, 0.55, 0.08, -21.7, -3.5, 1.05, 1.45)            # top Picatinny rail (teeth come from the traced outline)
    side(ch, alu, 1.2, 0.3, -3.6, 6.9, -3.2, 1.0)                 # receiver shoulders / magwell
    side(ch, poly, 0.98, 0.4, 6.5, 11.9, -9.0, -2.6)              # pistol grip
    side(ch, alu, 0.42, 0.1, 3.7, 6.8, -5.0, -2.8)                # trigger guard
    side(ch, alu, 0.8, 0.2, 3.9, 17.8, -2.9, -0.15)               # stock adapter + rail block
    side(ch, alu, 1.3, 0.45, 17.6, 21.6, -7.4, -0.3)              # perforated side plates
    side(ch, mid("rubber"), 1.38, 0.7, 21.2, 23.7, -7.4, -0.3)    # butt pad
    side(ch, alu, 1.38, 0.45, 12.6, 21.4, -0.3, 1.4)              # cheek riser
    ch.add(cylz(0, -1.9, 4.2, 18.4, 0.62, rr=0.15), mat=alu)      # buffer tube
    for zz in (13.1, 15.9):                                       # riser posts
        ch.add(box(-0.95, 0.95, -0.6, 0.1, zz, zz + 0.5, r=0.1), mat=alu)
    ch.paint(box(-1.3, 1.3, -6.9, -2.9, 7.6, 10.7), "black")      # grip texture panel
    # ------------------------------------------------------------------ receiver + rear aperture sight
    rc = m.mesh("receiver", "rifle", (0, 0, 0), tris=3600)
    gm = mid("gunmetal")
    side(rc, gm, 1.1, 0.3, -3.7, 6.7, -3.0, 1.02)
    rc.add(box(-0.95, 0.95, 0.9, 1.5, 2.0, 5.9, r=0.1), mat=gm)                   # sight base
    rc.add(Cyl((0.0, 1.55, 4.35), (0.0, 1.55, 4.35), 0.0), mat=gm) if False else None
    rc.add(cylz(0, 1.75, 3.9, 4.9, 0.5, rr=0.12), mat=gm)                          # aperture housing
    rc.sub(cylz(0, 1.75, 3.7, 5.1, 0.24))                                           # aperture
    for sx in (-1, 1):
        rc.add(Cyl((sx * 0.85, 1.15, 4.7), (sx * 1.45, 1.15, 4.7), 0.52, rr=0.1), mat=gm)   # windage / elevation knobs
        rc.paint(Cyl((sx * 1.3, 1.15, 4.7), (sx * 1.5, 1.15, 4.7), 0.3), "black")
    rc.add(box(-0.5, 0.5, 1.2, 2.0, 2.4, 3.6, r=0.1), mat=gm)                      # sight cover
    rc.sub(box(-1.4, -1.0, -2.6, -0.4, -2.6, 3.0))                                  # ejection port groove (right side)
    # ------------------------------------------------------------------ barrel, birdcage flash hider, gas cylinder, front sight
    ba = m.mesh("barrel", "rifle", (0, 0, 0), tris=2800)
    stl = mid("gunmetal")
    ba.add(cylz(0, 0, -36.3, -21.0, 0.45, rr=0.05), mat=mid("steel"))
    ba.add(cylz(0, 0, -36.6, -32.5, 0.6, rr=0.08), mat=stl)                         # slotted birdcage
    ba.sub(cylz(0, 0, -36.8, -33.0, 0.34))
    for ang in (0, 90):
        ba.sub(Box((0, 0, -34.7), (0.9, 0.09, 1.55), 0.03, rot=[("z", ang)]))
    ba.add(box(-0.55, 0.55, -0.4, 0.65, -32.5, -31.3, r=0.1), mat=stl)              # sight base
    for sx in (-1, 1):
        ba.add(box(sx * 0.5 - 0.09, sx * 0.5 + 0.09, 0.5, 2.0, -32.3, -31.6, r=0.05), mat=stl)   # hood ears
    ba.add(box(-0.1, 0.1, 0.5, 1.8, -32.1, -31.8, r=0.03), mat=stl)                 # post
    ba.add(box(-0.5, 0.5, -1.1, 0.6, -25.1, -23.4, r=0.15), mat=stl)                # gas lock / clamp
    ba.add(cylz(0, -0.9, -27.3, -23.3, 0.34, rr=0.06), mat=stl)                     # gas cylinder nose
    # ------------------------------------------------------------------ 20-round magazine (own bone so it can drop)
    mg = m.mesh("magazine", "rifle", (0, -3.0, -0.95), tris=1400)
    mg.add(Clip(Ext(sil, "zy", -0.93, 0.93, r=0.12), z0=-3.2, z1=1.1, y0=-8.3, y1=-2.95), mat=mid("steel"))
    mg.paint(box(-1.2, 1.2, -6.2, -5.9, -3.2, 1.1), "black")
    mg.paint(box(-1.2, 1.2, -4.5, -4.3, -3.2, 1.1), "black")

    m.bone("bolt", "rifle", (0, 0, 0))
    m.cube("bolt", "steel", -1.0, -0.3, -2.9, -0.9, 0.55, -0.7)
    m.cube("bolt", "steel", -0.88, 0.0, -0.7, 0.88, 0.6, 1.5)
    m.cube("bolt", "steel", -1.95, -0.6, -22.0, -1.3, -0.1, -4.0)                    # op rod
    m.bone("bolt_handle", "bolt", (-1.1, 0.3, -1.0))
    m.cube("bolt_handle", "steel", -2.0, -0.15, -1.5, -0.9, 0.65, -0.5)
    m.cube("bolt_handle", "steel", -2.6, -0.5, -1.9, -1.9, 1.0, -0.1)
    m.cube("bolt_handle", "black", -2.9, -0.6, -2.0, -2.55, 1.1, 0.0)
    m.hand_bolt("bolt_handle", -2.7, 0.3, -1.0)
    m.muzzle_flash(-36.8, length=5.5, width=3.6)
    m.casing(-1.1, 0.5, -1.0)
    m.hand_left(-4.0, -14.5)
    m.hand_right(-6.0, 8.8, -3.6)

    cfg = dict(
        name=ID, hand_l=(-4.0, -14.5), mag_grip=(-6.8, -0.95), mag_drop=9.0, mag_rock=10,
        charge_hand="right", handle=(-2.7, 0.3, -1.0), bolt_travel=6.5, hold_open=True,
        release_mode="handle",
        fire_len=0.32, cycle=0.12, kick_z=2.8, kick_pitch=4.0, kick_yaw=0.8, flash=1.25,
        reload_len=2.3, charge_len=0.95, release_len=0.7, eject=(-1.1, 0.5, 0.9),
        sight=(SY, SZ), butt=23.6,
    )
    return m, cfg
