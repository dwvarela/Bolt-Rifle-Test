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
    m = MModel(ID, lo=(-3.4, -9.0, -34.6), hi=(3.2, 3.0, 24.4), h=0.10, seed=5, tx=9)
    sil = Traced.load(SIL, res=0.025, keep=lambda c, size: False, smooth=0.4)          # outer outline only (guard opening is built below)
    full = Traced.load(SIL, res=0.025, keep=lambda c, size: abs(c[0] - 5.6) < 1.0 and abs(c[1] + 3.4) < 1.0, smooth=0.08)   # + trigger-guard opening

    # continuous half-width profile of the stock (z, y0, y1, half width, rounding): forend, action, wrist, comb, butt
    W = Loft([(-15.4, -20, 20, 1.05, 0.5), (-12.0, -20, 20, 1.10, 0.5), (-5.0, -20, 20, 1.14, 0.5), (3.5, -20, 20, 1.17, 0.5),
              (7.5, -20, 20, 0.95, 0.5), (12.0, -20, 20, 0.92, 0.5), (18.0, -20, 20, 1.00, 0.5), (22.4, -20, 20, 1.10, 0.5),
              (23.6, -20, 20, 1.10, 0.5)])

    def side(vol, mat, hw, r, z0, z1, y0, y1, s=sil):
        if s is sil:                                                       # stock windows follow the smooth width profile
            vol.add(Clip(Isect(Ext(sil, "zy", -1.4, 1.4, r=r), W), z0=z0, z1=z1, y0=y0, y1=y1), mat=mat)
        else:
            vol.add(Clip(Ext(s, "zy", -hw, hw, r=r), z0=z0, z1=z1, y0=y0, y1=y1), mat=mat, k=0.25)

    syn, blu, rub, stl = mid("synth"), mid("bluing"), mid("rubber"), mid("steel")
    # ------------------------------------------------------------------ stock + trigger guard
    st = m.mesh("stock", "rifle", (0, 0, 0), tris=12000)
    side(st, syn, 1.12, 0.55, -15.2, -5.2, -3.0, 0.10)                   # forend (the barrel sits in the channel)
    side(st, syn, 1.18, 0.45, -5.2, 3.5, -2.6, 0.35)                      # action section
    side(st, syn, 1.10, 0.45, 3.5, 7.2, -2.6, 0.05)                       # stock flanks behind the receiver: a trough the bolt rides in
    side(st, syn, 0.95, 0.5, 7.2, 22.3, -9.0, 1.0)                        # wrist, comb and buttstock
    side(st, rub, 1.12, 0.5, 22.3, 23.45, -9.0, 1.0)                      # recoil pad
    st.sub(cylz(0, 0.0, 3.8, 9.0, 0.75))                                  # raceway so the retracted bolt never touches the stock
    gd = mid("bluing")                                                     # trigger guard bow and trigger (explicit, so the opening stays clean)
    path = [(4.6, -2.3), (4.6, -3.75), (5.0, -4.25), (6.15, -4.25), (6.55, -3.75), (6.6, -2.3)]
    for (z0, y0), (z1, y1) in zip(path, path[1:]):
        st.add(Cyl((0, y0, z0), (0, y1, z1), 0.21), mat=gd, k=0.08)
    st.add(Cyl((0, -2.3, 5.45), (0, -3.5, 5.15), 0.12), mat=mid("steel"), k=0.05)      # trigger blade
    st.add(Cyl((0, -3.5, 5.15), (0, -3.75, 5.45), 0.12), mat=mid("steel"), k=0.05)     # trigger curl
    for z, y in ((-13.6, -1.4), (20.3, -6.4)):                             # sling studs
        st.add(Cyl((0, y, z), (0, y - 0.95, z), 0.17), mat=stl)
    # ------------------------------------------------------------------ receiver, rail base
    rc = m.mesh("receiver", "rifle", (0, 0, 0), tris=5500)
    rc.add(cylz(0, 0, -5.2, 3.9, 1.08, rr=0.05), mat=blu)                 # receiver (ends at its rear face; the bolt shroud is free behind it)
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
    rc.sub(cylz(0, 0.0, -3.3, 3.9, 0.80))                                   # hollow action: the bolt rides in it and the cartridge is visible through the port
    rc.sub(box(-1.5, -0.3, 0.1, 1.2, -3.3, 3.2, r=0.15))                 # ejection port (right side of the rifle = -x in the model file)
    rc.add(box(-0.95, -0.55, 0.0, 0.55, 4.0, 4.9, r=0.1), mat=stl)       # safety lever, right rear of the receiver
    # ------------------------------------------------------------------ barrel (sporter taper), recessed crown
    ba = m.mesh("barrel", "rifle", (0, 0, 0), tris=2600)
    ba.add(Cyl((0, 0, -33.7), (0, 0, -17.0), 0.58, 0.60), mat=blu)
    ba.add(Cyl((0, 0, -17.0), (0, 0, -5.0), 0.60, 0.95), mat=blu)
    ba.sub(cylz(0, 0, -33.8, -33.2, 0.25))                                # crown recess / bore
    # ------------------------------------------------------------------ bolt: body shows in the port, rear shroud sticks out behind the receiver
    bo = m.mesh("bolt", "rifle", (0, 0, 0), tris=1800)
    bo.add(cylz(0, 0.0, -3.2, 3.9, 0.66), mat=stl)                        # bolt body
    bo.add(cylz(0, 0.0, 3.9, 4.5, 0.76, rr=0.08), mat=blu)                # collar at the handle root
    bo.add(cylz(0, 0.0, 4.5, 5.6, 0.62, rr=0.06), mat=blu)                # bolt shroud
    bo.add(cylz(0, 0.0, 5.6, 5.95, 0.48, rr=0.08), mat=stl)               # cocking piece / end cap
    bo.add(cylz(0, 0.5, -1.0, -0.4, 0.2), mat=stl)
    # ------------------------------------------------------------------ bolt handle (right side): stem, swept-down arm, ball knob
    bh = m.mesh("bolt_handle", "bolt", (0, 0, 5.0), tris=900)
    bh.add(Cyl((-0.9, 0.1, 4.1), (-1.9, -0.1, 4.2), 0.26), mat=stl)       # stem out of the bolt
    bh.add(Cyl((-1.9, -0.1, 4.2), (-2.5, -0.95, 4.4), 0.24), mat=stl)     # arm swept down
    bh.add(Ell((-2.6, -1.2, 4.5), (0.5, 0.5, 0.5)), mat=mid("black"))     # ball knob
    m.hand_bolt("bolt_handle", -2.6, -1.2, 4.5, side=-1)
    # ------------------------------------------------------------------ magazine (floor plate flush with the stock; drops away on reload)
    mg = m.mesh("magazine", "rifle", (0, -2.0, 0.5), tris=500)
    mg.add(box(-0.85, 0.85, -2.45, -1.0, -1.7, 3.3, r=0.08), mat=mid("black"))
    mg.add(box(-0.9, 0.9, -2.6, -2.4, -1.8, 3.4, r=0.05), mat=blu)       # floor plate
    # ------------------------------------------------------------------ iron sights on the rail (hidden by the renderer while an optic is mounted)
    # rear ghost-ring sight at the very back of the rail, blade front sight at the very front (Optics-2 reference set)
    cy = 2.75
    m.bone("irons_rear", "rifle", (0, 0, 0))
    m.cube("irons_rear", "black", -0.55, 1.70, 3.4, 0.55, 2.10, 4.6)                        # low saddle base on the rail
    m.cube("irons_rear", "black", -0.12, 2.10, 3.98, 0.12, 2.30, 4.22)                      # thin post
    for i in range(8):                                                                      # thin aperture ring (octagon, ~0.1 wall)
        m.cube("irons_rear", "black", -0.19, cy + 0.42, 3.98, 0.19, cy + 0.52, 4.22, rot=[0, 0, i * 45], pivot=[0, cy, 4.1])
    m.cube("irons_rear", "steel", -0.42, 1.98, 3.5, -0.28, 2.12, 3.66)                      # windage screw heads
    m.cube("irons_rear", "steel", 0.28, 1.98, 3.5, 0.42, 2.12, 3.66)
    m.bone("irons_front", "rifle", (0, 0, 0))
    m.cube("irons_front", "black", -0.55, 1.70, -5.0, 0.55, 1.95, -3.9)                     # low base
    m.cube("irons_front", "black", -0.07, 1.95, -4.95, 0.07, 2.72, -4.75)                   # thin blade
    m.cube("irons_front", "black", -0.07, 1.95, -4.75, 0.07, 2.42, -4.35)                   # ramp steps
    m.cube("irons_front", "black", -0.07, 1.95, -4.35, 0.07, 2.12, -3.95)
    # ------------------------------------------------------------------ muzzle flash, spent case, chambering round
    m.muzzle_flash(-33.9)
    m.casing(-1.5, 0.4, 0.5)
    m.bone("chamber_round", "rifle", (0, 0.4, -3))
    m.bar("chamber_round", "brass", 0, 0.5, -3.2, 0.4, 0.45)
    m.cube("chamber_round", "brass", -0.3, 0.2, -4.4, 0.3, 0.8, -3.2)
    m.hand_left(-3.8, -14.0)
    m.hand_right(-4.3, 8.6, -3.3)
    return m, None
