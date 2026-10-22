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
    m = MModel(ID, lo=(-3.2, -9.6, -38.0), hi=(3.2, 3.2, 24.8), h=0.10, seed=31, tx=9)
    def real_hole(c, size):
        z, y = c
        if min(size) < 0.25 or max(size) / min(size) > 3.2 and z > 12:   # sub-voxel slivers / thin gaps would fragment
            return False
        if z < -3.0:                      # handguard slots, gaps around the gas block
            return True
        if z > 19.4:                      # stock plate holes (the 6+2 round lightening holes), not edge noise
            return y > -5.6
        return abs(z - 5.4) < 0.3 and abs(y + 3.2) < 0.3 or (abs(z - 6.4) < 0.3 and abs(y + 2.4) < 0.3)   # trigger guard opening, grip gap

    sil = Traced.load(SIL, res=0.025, keep=real_hole, smooth=0.07)

    def side(vol, mat, hw, r, z0, z1, y0, y1, k=0.0):
        vol.add(Clip(Ext(sil, "zy", -hw, hw, r=r), z0=z0, z1=z1, y0=y0, y1=y1), mat=mat, k=k)

    # ------------------------------------------------------------------ chassis: handguard, grip, buffer tube, stock, magazine well
    ch = m.mesh("chassis", "rifle", (0, 0, 0), tris=4000)
    bs = m.mesh("buttstock", "rifle", (0, 0, 0), tris=1800)       # rear stock: own bone, hidden while aiming so it never fills the view
    alu, blk, poly = mid("alu"), mid("black"), mid("poly")
    side(ch, alu, 1.45, 0.45, -21.7, -3.5, -2.62, 1.12)           # slotted handguard body (slots come from the traced outline)
    side(ch, alu, 0.55, 0.05, -21.7, -3.5, 1.05, 1.45)            # top Picatinny rail (teeth come from the traced outline)
    ch.add(box(-0.5, 0.5, -3.0, -2.5, -21.3, -3.9, r=0.06), mat=alu)   # bottom rail strip
    z = -21.0
    while z < -4.3:
        ch.sub(box(-0.6, 0.6, -3.1, -2.82, z, z + 0.22))               # its notches
        z += 0.46
    z = -21.2
    while z < -14.2:                                              # side rail ribs between the two slot rows (both sides)
        ch.add(box(-1.72, 1.72, -1.32, -0.4, z, z + 0.26, r=0.05), mat=alu)
        z += 0.46
    side(ch, alu, 1.2, 0.3, -3.6, 6.9, -3.2, 1.0)                 # receiver shoulders / magwell
    side(ch, poly, 0.98, 0.4, 6.5, 11.9, -9.0, -2.6)              # pistol grip
    side(ch, alu, 0.42, 0.1, 3.7, 6.8, -5.0, -2.8)                # trigger guard
    side(ch, alu, 0.8, 0.2, 3.9, 9.5, -2.9, -0.15)                # stock adapter + rail block
    side(bs, alu, 1.3, 0.45, 17.6, 21.6, -7.4, -0.3)              # perforated side plates
    side(bs, mid("rubber"), 1.38, 0.7, 21.2, 23.7, -7.4, -0.3)    # butt pad
    side(bs, poly, 1.2, 0.45, 13.2, 21.5, -0.12, 1.12)            # cheek riser slab (photo: rear post only, front end overhangs)
    bs.add(box(-0.7, 0.7, -1.4, -0.05, 20.7, 21.6, r=0.08), mat=alu)   # its rear post, standing on the side-plate top
    ch.add(cylz(0, -2.1, 4.2, 12.6, 0.40, rr=0.1), mat=alu)       # buffer tube (front part)
    bs.add(cylz(0, -2.1, 12.4, 19.0, 0.40, rr=0.1), mat=alu)      # buffer tube (rear part)
    bs.add(cylz(0, -2.1, 16.6, 19.0, 0.48, rr=0.1), mat=alu)      # tube collar
    bs.add(Ell((-0.62, -2.1, 19.8), (0.3, 0.42, 0.95)), mat=alu)  # oval adjustment lever
    ch.paint(box(-1.3, 1.3, -6.9, -2.9, 7.6, 10.7), "black")      # grip texture panel
    # ------------------------------------------------------------------ receiver + rear aperture sight
    rc = m.mesh("receiver", "rifle", (0, 0, 0), tris=1400)
    gm = mid("gunmetal")
    side(rc, gm, 1.1, 0.3, -3.7, 6.7, -3.0, 1.02)
    rc.add(box(-0.95, 0.95, 0.9, 1.5, 2.0, 5.9, r=0.1), mat=gm)                   # sight base
    rc.add(Cyl((0.0, 1.55, 4.35), (0.0, 1.55, 4.35), 0.0), mat=gm) if False else None
    rc.add(box(-0.3, 0.3, 1.45, SY - 0.4, 4.1, 4.7, r=0.06), mat=gm)                # slim stem up to the ring
    rc.add(cylz(0, SY, 4.15, 4.65, 0.66, rr=0.1), mat=gm)                          # thin aperture ring (outer r .66)
    rc.sub(cylz(0, SY, 3.9, 4.9, 0.46))                                             # large clear aperture (r .46: wall only .2)
    for sx in (-1, 1):                                                              # thin protective wings either side of the ring
        rc.add(box(sx * 0.86 - 0.06, sx * 0.86 + 0.06, 1.45, SY + 0.55, 4.0, 4.8, r=0.04), mat=gm)
    for sx in (-1, 1):
        rc.add(Cyl((sx * 0.85, 1.15, 4.7), (sx * 1.45, 1.15, 4.7), 0.52, rr=0.1), mat=gm)   # windage / elevation knobs
        rc.paint(Cyl((sx * 1.3, 1.15, 4.7), (sx * 1.5, 1.15, 4.7), 0.3), "black")
    rc.add(box(-0.5, 0.5, 1.2, 1.55, 2.4, 3.6, r=0.1), mat=gm)                     # low sight cover (never in the sight line)
    rc.sub(box(-1.5, -0.7, -0.25, 0.65, -2.6, 6.4))                                  # operating-rod slot in the right wall (the handle slides in it)
    # ------------------------------------------------------------------ barrel, birdcage flash hider, gas cylinder, front sight
    ba = m.mesh("barrel", "rifle", (0, 0, 0), tris=800)
    stl = mid("gunmetal")
    ba.add(cylz(0, 0, -36.3, -21.0, 0.45, rr=0.05), mat=mid("steel"))
    ba.add(cylz(0, 0, -36.6, -32.5, 0.6, rr=0.08), mat=stl)                         # slotted birdcage
    ba.sub(cylz(0, 0, -36.8, -33.0, 0.34))
    for ang in (0, 90):
        ba.sub(Box((0, 0, -34.7), (0.9, 0.09, 1.55), 0.03, rot=[("z", ang)]))
    ba.add(box(-0.55, 0.55, -0.4, 0.65, -32.5, -31.3, r=0.1), mat=stl)              # sight base
    for sx in (-1, 1):
        ba.add(box(sx * 0.62 - 0.05, sx * 0.62 + 0.05, 0.5, SY + 0.4, -32.4, -31.5, r=0.03), mat=stl)   # thin hood wings
    ba.add(box(-0.11, 0.11, 0.5, SY, -32.15, -31.8, r=0.03), mat=stl)               # front post, tip exactly on the sight line
    ba.add(box(-0.5, 0.5, -1.1, 0.6, -25.1, -23.4, r=0.15), mat=stl)                # gas lock / clamp
    ba.add(cylz(0, -0.9, -27.3, -23.3, 0.34, rr=0.06), mat=stl)                     # gas cylinder nose
    # ------------------------------------------------------------------ 20-round magazine (own bone so it can drop)
    mg = m.mesh("magazine", "rifle", (0, -3.0, -0.95), tris=1400)
    mg.add(Clip(Ext(sil, "zy", -0.93, 0.93, r=0.12), z0=-3.2, z1=1.1, y0=-8.3, y1=-2.95), mat=mid("steel"))
    mg.paint(box(-1.2, 1.2, -6.2, -5.9, -3.2, 1.1), "black")
    mg.paint(box(-1.2, 1.2, -4.5, -4.3, -3.2, 1.1), "black")

    # ------------------------------------------------------------------ bolt, operating rod and its handle (all smooth parts, no slapped-on cubes)
    stlm, blk = mid("steel"), mid("black")
    bo = m.mesh("bolt", "rifle", (0, 0, 0), tris=700)
    bo.add(box(-0.8, 0.8, 0.05, 0.78, -2.9, 1.5, r=0.12), mat=stlm)                       # bolt body riding in the receiver
    bo.add(box(-0.55, 0.55, 0.7, 0.9, -1.4, 0.4, r=0.08), mat=stlm)                      # raised lug on top of the bolt (ejection window side)
    bo.add(box(-1.45, -0.9, -0.2, 0.55, -4.2, -0.6, r=0.14), mat=stlm)                    # carrier arm through the receiver slot to the rod
    bo.add(Cyl((-1.55, -0.2, -22.0), (-1.55, -0.2, -4.2), 0.33, rr=0.3), mat=stlm)        # operating rod running up under the gas cylinder
    bo.add(box(-1.95, -1.15, -0.55, 0.15, -6.5, -4.2, r=0.14), mat=stlm)                  # rod head / spring-guide block
    bh = m.mesh("bolt_handle", "bolt", (-1.1, 0.3, -1.0), tris=300)
    bh.add(box(-1.0, -1.75, -0.15, 0.62, -1.95, -0.65, r=0.16), mat=stlm)                 # handle lug growing out of the carrier arm
    bh.add(box(-1.65, -2.2, -0.3, 0.75, -2.0, -0.5, r=0.14), mat=blk)                      # flat serrated thumb button at the tip
    m.casing(-0.7, 1.0, -1.0)
    m.bone("chamber_round", "rifle", (0, 0, -4.5))
    m.bar("chamber_round", "brass", 0, 0, -6.1, -3.4, 0.42)
    m.bar("chamber_round", "steel", 0, 0, -7.0, -6.1, 0.3)
    m.muzzle_flash(-36.8, length=5.5, width=3.6)
    m.hand_left(-4.0, -14.5)
    m.hand_right(-6.0, 8.8, -3.6)

    cfg = dict(
        name=ID, hand_l=(-4.0, -14.5), mag_grip=(-6.8, -0.95), mag_drop=9.0, mag_rock=10,
        charge_hand="right", hand_r=(-6.0, 8.8), handle=(-2.7, 0.3, -1.0), bolt_travel=6.5, hold_open=True,
        release_mode="handle",
        fire_len=0.32, cycle=0.12, kick_z=2.8, kick_pitch=4.0, kick_yaw=0.8, flash=1.25,
        reload_len=2.3, charge_len=0.95, release_len=0.7, eject=(-0.9, 1.4, 0.8), round=(4.5, -2.0),
        sight=(SY, SZ), butt=23.6,
    )
    return m, cfg
