"""Remington 700 (black synthetic stock, one-piece rail base, no iron sights, no scope) - SDF mesh model.
The side silhouette (stock, forend, comb, grip, butt, trigger guard with trigger, barrel line) is TRACED from the reference side view
(tools/trace/m700_side.json, made with trace_side.py).  Widths (the photos only show the sides) are estimates for a real Model 700:
forend 4.4 cm, wrist 3.6 cm, comb 3.8 cm, butt 4.4 cm.  Optics are mounted on the rail (see Guns.java mount()).
Animations: gen_m700_anim.py."""
import os
from meshbake import MModel, mid
from sdf import *

ID = "bolt_rifle"
SIL = os.path.join(os.path.dirname(os.path.abspath(__file__)), "trace", "m700_side.json")
RAIL_TOP, RAIL_Z = 1.78, -0.2       # optic mount: top of the rail, centre of the rail along z
RAIL_Z0, RAIL_Z1 = -5.0, 4.6


def build():
    m = MModel(ID, lo=(-3.4, -9.0, -34.6), hi=(3.2, 3.0, 24.4), h=0.13, seed=5, tx=9)
    sil = Traced.load(SIL, res=0.03, keep=lambda c, size: False)          # outer outline only (guard opening is built below)
    full = Traced.load(SIL, res=0.03, keep=lambda c, size: abs(c[0] - 5.6) < 1.0 and abs(c[1] + 3.4) < 1.0)   # + trigger-guard opening

    def side(vol, mat, hw, r, z0, z1, y0, y1, s=sil):
        vol.add(Clip(Ext(s, "zy", -hw, hw, r=r), z0=z0, z1=z1, y0=y0, y1=y1), mat=mat, k=0.25)

    syn, blu, rub, stl = mid("synth"), mid("bluing"), mid("rubber"), mid("steel")
    # ------------------------------------------------------------------ stock + trigger guard
    st = m.mesh("stock", "rifle", (0, 0, 0), tris=7500)
    side(st, syn, 1.12, 0.55, -15.2, -5.0, -3.0, 0.10)                   # forend (the barrel sits in the channel)
    side(st, syn, 1.18, 0.45, -5.2, 3.7, -2.6, 0.35)                      # action section
    side(st, syn, 1.10, 0.45, 3.5, 7.4, -2.6, 0.9)                        # tang bridge above the trigger opening
    side(st, syn, 0.92, 0.45, 7.2, 12.0, -9.0, 1.0)                       # wrist / pistol grip
    side(st, syn, 0.98, 0.5, 11.8, 18.0, -9.0, 1.0)                       # comb and buttstock
    side(st, syn, 1.10, 0.55, 17.8, 22.4, -9.0, 1.0)                      # buttstock rear
    side(st, rub, 1.12, 0.5, 22.3, 23.4, -9.0, 1.0)                       # recoil pad
    st.add(Clip(Ext(full, "zy", -0.3, 0.3, r=0.1), z0=4.2, z1=7.5, y0=-4.9, y1=-2.3), mat=blu, k=0.1)   # trigger guard + trigger
    for z, y in ((-13.6, -1.95), (20.5, -7.1)):                            # sling studs
        st.add(Cyl((0, y, z), (0, y - 0.55, z), 0.18), mat=stl)
    # ------------------------------------------------------------------ receiver, rail base
    rc = m.mesh("receiver", "rifle", (0, 0, 0), tris=4200)
    rc.add(cylz(0, 0, -5.2, 6.0, 1.08, rr=0.05), mat=blu)                 # receiver
    rc.add(cylz(0, 0, -6.1, -5.1, 0.98), mat=blu)                         # barrel shoulder
    rc.add(box(-1.0, 1.0, -1.7, -0.8, -5.3, -4.0, r=0.12), mat=blu)       # recoil lug
    rc.add(box(-0.62, 0.62, 0.95, RAIL_TOP - 0.28, RAIL_Z0, RAIL_Z1, r=0.06), mat=blu)    # rail base plate
    z = RAIL_Z0 + 0.15
    while z + 0.5 < RAIL_Z1 - 0.1:                                        # rail teeth
        rc.add(box(-0.62, 0.62, RAIL_TOP - 0.3, RAIL_TOP, z, z + 0.5, r=0.03), mat=blu)
        z += 0.8
    for z in (-4.2, -1.4, 2.0, 4.0):                                      # base screws
        rc.add(Cyl((-0.62, 1.3, z), (-0.72, 1.3, z), 0.14), mat=stl)
    rc.sub(box(-1.5, 1.5, 0.78, 1.18, -1.3, 2.6, r=0.15))                 # ejection port opening / slot under the rail
    rc.sub(box(-1.5, -0.3, 0.1, 1.2, -3.3, 3.2, r=0.15))                  # ejection port (right side)
    rc.add(box(-0.35, 0.35, 0.75, 1.25, 5.3, 6.2, r=0.1), mat=stl)        # safety lever
    # ------------------------------------------------------------------ barrel (sporter taper), recessed crown
    ba = m.mesh("barrel", "rifle", (0, 0, 0), tris=2600)
    ba.add(Cyl((0, 0, -33.7), (0, 0, -17.0), 0.58, 0.60), mat=blu)
    ba.add(Cyl((0, 0, -17.0), (0, 0, -5.0), 0.60, 0.95), mat=blu)
    ba.sub(cylz(0, 0, -33.8, -33.2, 0.25))                                # crown recess / bore
    # ------------------------------------------------------------------ bolt: body shows in the port, rear shroud sticks out behind the receiver
    bo = m.mesh("bolt", "rifle", (0, 0, 0), tris=1800)
    bo.add(cylz(0, 0.1, -3.2, 3.6, 0.70), mat=stl)                        # bolt body
    bo.add(cylz(0, 0.25, 3.6, 6.9, 0.64, rr=0.08), mat=blu)               # bolt shroud
    bo.add(cylz(0, 0.25, 6.7, 7.1, 0.34), mat=stl)                        # cocking piece
    bo.add(cylz(0, 0.55, -1.0, -0.4, 0.2), mat=stl)
    # ------------------------------------------------------------------ bolt handle (right side): stem, swept-down arm, ball knob
    bh = m.mesh("bolt_handle", "bolt", (0, 0, 5.0), tris=900)
    bh.add(Cyl((-0.9, 0.1, 4.1), (-1.9, -0.1, 4.2), 0.26), mat=stl)       # stem out of the bolt
    bh.add(Cyl((-1.9, -0.1, 4.2), (-2.5, -0.95, 4.4), 0.24), mat=stl)     # arm swept down
    bh.add(Ell((-2.6, -1.2, 4.5), (0.5, 0.5, 0.5)), mat=mid("black"))     # ball knob
    m.hand_bolt("bolt_handle", -2.6, -1.2, 4.5)
    # ------------------------------------------------------------------ magazine (floor plate flush with the stock; drops away on reload)
    mg = m.mesh("magazine", "rifle", (0, -2.0, 0.5), tris=500)
    mg.add(box(-0.85, 0.85, -2.45, -1.0, -1.7, 3.3, r=0.08), mat=mid("black"))
    mg.add(box(-0.9, 0.9, -2.6, -2.4, -1.8, 3.4, r=0.05), mat=blu)       # floor plate
    # ------------------------------------------------------------------ muzzle flash, spent case, chambering round
    m.muzzle_flash(-33.9)
    m.casing(-1.5, 0.4, 0.5)
    m.bone("chamber_round", "rifle", (0, 0.4, -3))
    m.bar("chamber_round", "brass", 0, 0.5, -3.2, 0.4, 0.45)
    m.cube("chamber_round", "brass", -0.3, 0.2, -4.4, 0.3, 0.8, -3.2)
    m.hand_left(-3.8, -14.0)
    m.hand_right(-4.3, 8.6, -3.3)
    return m, None
