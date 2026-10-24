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


def cap(a, b, r0, r1=None):
    """Rounded limb segment."""
    r1 = r0 if r1 is None else r1
    return Cyl(a, b, r0, r1, rr=min(r0, r1) * 0.97)


def _rot(v, axis, deg):
    import numpy as np
    v, axis = np.array(v, float), np.array(axis, float)
    axis = axis / np.linalg.norm(axis)
    t = np.radians(deg)
    return v * np.cos(t) + np.cross(axis, v) * np.sin(t) + axis * np.dot(axis, v) * (1 - np.cos(t))


def digit(h, base, d0, bend_axis, curls, lens, radii, mat, k=0.4):
    """A finger / thumb as three phalanges with anatomically sized lengths, bending about bend_axis by the cumulative curls (deg).
    Radii taper from knuckle to tip; the segments blend smoothly (no ball joints)."""
    import numpy as np
    p = np.array(base, float)
    ang = 0.0
    pts = [p.copy()]
    for c, L in zip(curls, lens):
        ang += c
        p = p + _rot(d0, bend_axis, ang) * L * 0.92
        pts.append(p.copy())
    for i in range(3):
        h.add(cap(tuple(pts[i]), tuple(pts[i + 1]), radii[i], radii[i + 1]), mat=mat, k=k)
    return pts


def sleeve(h, a, b, r_glove, r_sleeve, glove_len=0.35):
    """Glove cuff and a rolled olive sleeve running back along a -> b (the arm leaves the picture quickly)."""
    import numpy as np
    a, b = np.array(a, float), np.array(b, float)
    w = (b - a) / np.linalg.norm(b - a)
    c1 = a + w * glove_len * np.linalg.norm(b - a)
    h.add(cap(a, c1, r_glove, r_glove * 1.08), mat=mid("glove"), k=0.2)
    h.add(Cyl(c1 - w * 0.1, b, r_sleeve, r_sleeve * 1.06, rr=0.15), mat=mid("olive"), k=0.1)


def glove(h, wrist, v, n, tdir, mat, curls, thumb_pts, sleeve_to, scale=1.0, index_curls=None, index_pts=None, flen=1.0):
    """A thin leather-style glove after the reference photos: flat palm slab with a thenar pad, four tapering fingers that touch side by
    side (no gaps, no ball joints), a thumb that grows out of the thenar, a snug cuff and a sleeve.  Frame: v wrist->fingers, n out of the
    palm, thumb on the +u side.  All sizes are one rigid hand (nothing is ever scaled while animating)."""
    import numpy as np
    W = np.array(wrist, float)
    v = np.array(v, float); v /= np.linalg.norm(v)
    n = np.array(n, float); n -= v * np.dot(n, v); n /= np.linalg.norm(n)
    u = np.cross(v, n)
    if np.dot(u, np.array(tdir, float)) < 0:
        u = -u
    S = scale

    def P(p):
        return tuple(W + S * (u * p[0] + v * p[1] + n * p[2]))

    def E(c, r, rot_axis=None):
        e = Ell(P(c), tuple(x * S for x in r))
        M = np.stack([u, v, n], axis=1)           # local axes -> world
        e.R = M
        return e

    h.add(E((0, 2.3, 0.0), (1.95, 2.45, 0.80)), mat=mat)                         # palm + back of the hand
    h.add(E((0, 0.5, 0.0), (1.55, 1.7, 0.78)), mat=mat, k=0.5)                    # narrowing towards the wrist
    h.add(E((1.05, 1.5, 0.42), (0.95, 1.7, 0.62)), mat=mat, k=0.5)               # thenar pad
    h.add(E((-1.15, 2.7, 0.3), (0.75, 1.6, 0.55)), mat=mat, k=0.5)               # hypothenar edge
    spec = [(1.42, 4.55, 0.52, (2.0, 1.2, 1.0)), (0.48, 4.75, 0.54, (2.25, 1.3, 1.05)),
            (-0.47, 4.55, 0.52, (2.05, 1.2, 1.0)), (-1.38, 4.1, 0.47, (1.6, 0.95, 0.85))]
    for i, (fu, fv, r, lens) in enumerate(spec):
        cu = curls if (i or index_curls is None) else index_curls
        pts = [np.array([fu, fv, 0.05])]
        ang = 0.0
        for c, L in zip(cu, lens):
            L = L * flen
            ang += np.radians(c)
            d = np.array([0.0, np.cos(ang), np.sin(ang)])
            pts.append(pts[-1] + d * L * 0.93)
        rr = (r * 1.04, r * 0.97, r * 0.92, r * 0.86)
        Q = P
        if i == 0 and index_pts:                      # trigger finger: explicit world-space path, rooted deep inside the palm
            pts = [np.array(q, float) for q in index_pts]
            Q = lambda q: tuple(q)
            rr = (r * 1.2, r * 1.08, r * 1.0, r * 0.93, r * 0.86)
        for j in range(len(pts) - 1):
            h.add(Cyl(Q(pts[j]), Q(pts[j + 1]), rr[j] * S, rr[j + 1] * S), mat=mat, k=0.25)
        h.add(Ell(Q(pts[-1]), (rr[-1] * S,) * 3), mat=mat, k=0.25)                  # rounded fingertip
    tp = [np.array(t, float) for t in thumb_pts]
    tr = (0.70, 0.60, 0.50)
    for j in range(len(tp) - 1):
        h.add(Cyl(P(tp[j]), P(tp[j + 1]), tr[j] * S, tr[j + 1] * S if j + 1 < len(tr) else 0.5 * S), mat=mat, k=0.35)
    h.add(Ell(P(tp[-1]), (0.5 * S,) * 3), mat=mat, k=0.3)
    # cuff (glove) + sleeve (olive) heading to the elbow
    a = np.array(P((0, -0.2, 0)))
    b = np.array(sleeve_to, float)
    w = (b - a) / np.linalg.norm(b - a)
    c1 = a + w * 3.4                                   # glove cuff only (no sleeve): the wrist runs out of view
    h.add(Cyl(tuple(a), tuple(c1), 1.2 * S, 1.34 * S, rr=0.2), mat=mat, k=0.4)


def hands(m):
    g = mid("glove")
    # support hand: palm up under the forend, fingers curl up its right side, thumb forward
    L = m.mesh("left_hand", "rifle", (0, -3.3, -8.5), tris=1800)
    glove(L, (0.46, -2.5, -6.25), (-0.2, 0.0, -0.98), (-0.45, 0.89, 0.0), (1, 0.3, 0), g, (22, 32, 28),
          [(1.3, 0.9, 0.2), (2.0, 2.0, 0.7), (2.0, 3.1, 1.4)], (3.5, -9.0, 1.0))
    # firing hand on the grip: palm on the right side, fingers round the front of the grip, index on the trigger
    R = m.mesh("right_hand", "rifle", (0, -4.3, 8.6), tris=1800)
    glove(R, (-1.45, -2.3, 13.4), (0.0, -0.28, -0.96), (1, 0, 0), (0, 1, 0), g, (80, 55, 40),
          [(1.25, 0.8, 0.3), (1.9, 1.9, 0.9), (1.9, 3.0, 1.7)], (-3.5, -6.5, 24.4), flen=1.1,
          index_pts=[(-1.45, -1.9, 10.6), (-1.4, -2.25, 8.7), (-1.0, -2.7, 7.6), (-0.6, -2.95, 6.6), (-0.3, -3.0, 5.95)])


def build():
    m = MModel(ID, lo=(-7.0, -11.0, -34.6), hi=(7.0, 3.0, 28.0), h=float(os.environ.get("H", "0.10")), seed=5, tx=9)
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
    st = m.mesh("stock", "rifle", (0, 0, 0), tris=2000)
    side(st, syn, 1.12, 0.55, -15.2, -5.2, -3.0, 0.10)                   # forend (the barrel sits in the channel)
    side(st, syn, 1.18, 0.45, -5.2, 3.5, -2.6, 0.35)                      # action section
    side(st, syn, 1.10, 0.45, 3.5, 7.2, -2.6, 0.05)                       # stock flanks behind the receiver: a trough the bolt rides in
    bs = m.mesh("buttstock", "rifle", (0, 0, 0), tris=1500)               # own bone: hidden while aiming so the comb never fills the view
    side(bs, syn, 0.95, 0.5, 7.2, 22.3, -9.0, 1.0)                        # wrist, comb and buttstock
    side(bs, rub, 1.12, 0.5, 22.3, 23.45, -9.0, 1.0)                      # recoil pad
    st.sub(cylz(0, 0.0, 3.8, 9.0, 0.75))                                  # raceway so the retracted bolt never touches the stock
    bs.sub(cylz(0, 0.0, 3.8, 9.0, 0.75))
    gd = mid("bluing")                                                     # trigger guard bow and trigger (explicit, so the opening stays clean)
    path = [(4.6, -2.3), (4.6, -3.75), (5.0, -4.25), (6.15, -4.25), (6.55, -3.75), (6.6, -2.3)]
    for (z0, y0), (z1, y1) in zip(path, path[1:]):
        st.add(Cyl((0, y0, z0), (0, y1, z1), 0.21), mat=gd, k=0.08)
    st.add(Cyl((0, -2.3, 5.65), (0, -2.95, 6.0), 0.12), mat=mid("steel"), k=0.05)      # trigger blade: bulges to the rear (photo), concave to the front
    st.add(Cyl((0, -2.95, 6.0), (0, -3.55, 5.85), 0.12), mat=mid("steel"), k=0.05)     # lower curl comes back forward
    for z, y, vol in ((-13.6, -1.4, st), (20.3, -6.4, bs)):                # sling studs
        vol.add(Cyl((0, y, z), (0, y - 0.95, z), 0.17), mat=stl)
    # ------------------------------------------------------------------ receiver, rail base
    rc = m.mesh("receiver", "rifle", (0, 0, 0), tris=1700)
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
    ba = m.mesh("barrel", "rifle", (0, 0, 0), tris=700)
    ba.add(Cyl((0, 0, -33.7), (0, 0, -17.0), 0.58, 0.60), mat=blu)
    ba.add(Cyl((0, 0, -17.0), (0, 0, -5.0), 0.60, 0.95), mat=blu)
    ba.sub(cylz(0, 0, -33.8, -33.2, 0.25))                                # crown recess / bore
    # ------------------------------------------------------------------ bolt: body shows in the port, rear shroud sticks out behind the receiver
    bo = m.mesh("bolt", "rifle", (0, 0, 0), tris=600)
    bo.add(cylz(0, 0.0, -3.2, 3.9, 0.66), mat=stl)                        # bolt body
    bo.add(cylz(0, 0.0, 3.9, 4.5, 0.76, rr=0.08), mat=blu)                # collar at the handle root
    bo.add(cylz(0, 0.0, 4.5, 5.6, 0.62, rr=0.06), mat=blu)                # bolt shroud
    bo.add(cylz(0, 0.0, 5.6, 5.95, 0.48, rr=0.08), mat=stl)               # cocking piece / end cap
    bo.add(cylz(0, 0.5, -1.0, -0.4, 0.2), mat=stl)
    # ------------------------------------------------------------------ bolt handle (right side): stem, swept-down arm, ball knob
    bh = m.mesh("bolt_handle", "bolt", (0, 0, 5.0), tris=400)
    bh.add(Cyl((-0.9, 0.1, 4.1), (-1.9, -0.1, 4.2), 0.26), mat=stl)       # stem out of the bolt
    bh.add(Cyl((-1.9, -0.1, 4.2), (-2.5, -0.95, 4.4), 0.24), mat=stl)     # arm swept down
    bh.add(Ell((-2.6, -1.2, 4.5), (0.5, 0.5, 0.5)), mat=mid("black"))     # ball knob
    # ------------------------------------------------------------------ magazine (floor plate flush with the stock; drops away on reload)
    mg = m.mesh("magazine", "rifle", (0, -2.0, 0.5), tris=500)
    mg.add(box(-0.85, 0.85, -2.45, -1.0, -1.7, 3.3, r=0.08), mat=mid("black"))
    mg.add(box(-0.9, 0.9, -2.6, -2.4, -1.8, 3.4, r=0.05), mat=blu)       # floor plate
    brs, stm = mid("brass"), mid("steel")
    for x, z0 in ((-0.32, -0.3), (0.32, 0.45), (-0.32, 1.2)):             # the rounds stacked in the magazine (zig-zag), bullets forward
        y = -0.95 if z0 < 1.0 else -0.95
        mg.add(Cyl((x, y, z0), (x, y, z0 + 1.7), 0.25, rr=0.05), mat=brs)
        mg.add(Cyl((x, y, z0 - 0.95), (x, y, z0), 0.2, 0.2, rr=0.05), mat=stm)
    mg.add(box(-0.7, 0.7, -1.25, -0.95, -1.5, 3.1, r=0.05), mat=mid("black"))   # follower / feed lips
    # ------------------------------------------------------------------ iron sights on the rail (hidden by the renderer while an optic is mounted)
    # rear ghost-ring sight at the very back of the rail, blade front sight at the very front (Optics-2 reference set)
    cy = 2.75
    m.bone("irons_rear", "rifle", (0, 0, 0))
    m.cube("irons_rear", "black", -0.42, 1.74, 3.5, 0.42, 2.0, 4.55)                        # low base clamped on the rail
    m.cube("irons_rear", "black", -0.10, 2.0, 3.98, 0.10, 2.36, 4.2)                        # slim post
    for sx in (-1, 1):                                                                      # protective ears
        m.cube("irons_rear", "black", sx * 0.40 - 0.045, 2.0, 3.98, sx * 0.40 + 0.045, cy + 0.12, 4.2)
    for i in range(8):                                                                      # fine aperture ring (octagon, ~0.07 wall)
        m.cube("irons_rear", "black", -0.15, cy + 0.36, 3.99, 0.15, cy + 0.43, 4.19, rot=[0, 0, i * 45], pivot=[0, cy, 4.09])
    m.cube("irons_rear", "steel", -0.34, 1.92, 3.58, -0.22, 2.04, 3.7)                      # windage screw heads
    m.cube("irons_rear", "steel", 0.22, 1.92, 3.58, 0.34, 2.04, 3.7)
    m.bone("irons_front", "rifle", (0, 0, 0))
    m.cube("irons_front", "black", -0.42, 1.74, -4.98, 0.42, 1.92, -4.0)                    # low base
    m.cube("irons_front", "black", -0.045, 1.92, -4.95, 0.045, 2.72, -4.8)                  # thin blade
    m.cube("irons_front", "black", -0.045, 1.92, -4.8, 0.045, 2.4, -4.45)                   # ramp steps
    m.cube("irons_front", "black", -0.045, 1.92, -4.45, 0.045, 2.1, -4.1)
    # ------------------------------------------------------------------ muzzle flash, spent case, chambering round
    m.muzzle_flash(-33.9)
    m.casing(-1.5, 0.4, 0.5)
    m.bone("chamber_round", "rifle", (0, 0.4, -3))
    m.bar("chamber_round", "brass", 0, 0.5, -3.2, 0.4, 0.45)
    m.cube("chamber_round", "brass", -0.3, 0.2, -4.4, 0.3, 0.8, -3.2)
    hands(m)
    return m, None
