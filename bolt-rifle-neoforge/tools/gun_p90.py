"""FN P90 (5.7x28), modelled from reference photos: sculpted bullpup body with two openings (trigger loop + thumbhole),
front hood carrying the picatinny rail and flip-up sights, translucent amber magazine lying on top, flat stock with butt cap."""
import math
from gunlib import Model

HW = 1.55
SY, SZ = 6.3, -6.3          # rear aperture centre (height above bore, z)


def build():
    m = Model("p90", seed=71)
    m.bone("body", "rifle", (0, 0, 0))
    m.bone("barrel", "rifle", (0, 0, 0))
    mz = -16.0
    # ---------------------------------------------------------------- barrel + ported muzzle brake
    m.bar("barrel", "steel", 0, 0, mz + 2.6, -11.0, 0.5, fine=True)
    m.bar("barrel", "steel", 0, 0, mz, mz + 2.7, 0.74, fine=True)
    for i in range(2):
        m.cube("barrel", "black", -0.9, -0.2, mz + 0.9 + i * 0.7, 0.9, 0.2, mz + 1.25 + i * 0.7)    # cross ports
    m.cube("barrel", "black", -0.3, -0.3, mz - 0.03, 0.3, 0.3, mz + 0.05)
    m.bar("barrel", "gunmetal", 0, 0, mz + 2.7, mz + 3.3, 0.86, fine=True)                           # brake ring
    # ---------------------------------------------------------------- sculpted core: side-profile slices with two openings
    def bottom(z):
        if z < -11.4: return -3.7
        if z < -5.7: return -3.7 + (z + 11.4) / 5.7 * (-2.1)
        if z < 0.3: return -5.8
        if z < 6.0: return -5.8 + (z - 0.3) / 5.7 * 1.4
        return -4.4

    def top(z):
        return 1.1 if z < 5.4 else 2.5

    holes = [(-7.3, -2.7, 1.6, 1.2), (1.4, -3.0, 3.4, 1.9)]            # trigger loop, thumbhole (cz, cy, az, ay)
    step = 0.6
    z = -13.4
    while z < 15.0 - 1e-6:
        z1 = min(z + step, 15.0)
        zc = (z + z1) / 2
        lo, hi = bottom(zc), top(zc)
        segs = [(lo, hi)]
        for cz, cy, az, ay in holes:
            if abs(zc - cz) < az:
                h = ay * math.sqrt(1 - ((zc - cz) / az) ** 2)
                new = []
                for a, b in segs:
                    if cy + h <= a or cy - h >= b:
                        new.append((a, b)); continue
                    if cy - h > a: new.append((a, cy - h))
                    if cy + h < b: new.append((cy + h, b))
                segs = new
        for a, b in segs:
            if b - a > 0.15:
                m.rbox("body", "p90", -HW, a, z, HW, b, z1 + 0.03, c=min(0.7, (b - a) / 2.3))
        z = z1
    # recessed side panels + moulded details
    m.cube("body", "black", -HW - 0.02, -0.4, -2.6, -HW + 0.05, 0.9, 3.4)
    m.cube("body", "black", HW - 0.05, -0.4, -2.6, HW + 0.02, 0.9, 3.4)
    for sx in (-1, 1):                                                                   # screws along the sides
        for zz, yy in ((-4.0, -3.6), (-0.6, -5.2), (6.4, -3.2), (12.0, -3.6), (13.2, 1.4), (-10.6, -2.0), (-8.6, -4.6)):
            m.cube("body", "gunmetal", sx * (HW + 0.0) - 0.07, yy - 0.2, zz - 0.2, sx * (HW + 0.0) + 0.07, yy + 0.2, zz + 0.2)
    m.cube("body", "black", -1.58, 1.6, 6.2, -1.5, 2.4, 9.6)                              # cocking window / port edge
    m.cube("body", "black", -0.8, -4.55, 7.0, 0.8, -4.4, 11.0)                            # ejection port (underside)
    m.rbox("body", "rubber", -1.5, -4.5, 14.8, 1.5, 2.55, 15.35, c=0.45)                 # butt cap
    m.cube("body", "black", -1.35, -4.1, 14.78, -1.2, -3.9, 15.0)                         # sling slot mark
    # ---------------------------------------------------------------- front hood (rail housing) + picatinny rail + strap
    m.rbox("body", "p90", -1.6, -1.1, -13.3, 1.6, 3.4, -3.0, c=0.55)
    m.cube("body", "black", -1.62, 0.2, -12.2, -1.5, 2.6, -10.0)                           # hood window
    m.cube("body", "black", 1.5, 0.2, -12.2, 1.62, 2.6, -10.0)
    m.cube("body", "gunmetal", -1.3, 3.3, -12.4, 1.3, 3.75, -3.0)                          # rail base
    for zr in [-12.1 + 0.85 * i for i in range(11)]:
        m.cube("body", "black", -1.33, 3.7, zr, 1.33, 4.2, zr + 0.45)                     # rail ribs
    m.cube("body", "black", -1.5, 3.4, -4.6, 1.5, 3.75, -3.4)                              # strap top
    for sx in (-1, 1):
        m.cube("body", "black", sx * 1.65 - 0.12, 1.0, -4.6, sx * 1.65 + 0.12, 3.5, -3.4)  # strap sides
    # flip-up iron sights (raised, as in the photos)
    m.cube("body", "gunmetal", -1.0, 4.1, -7.4, 1.0, 4.6, -5.8)                            # rear base
    for sx in (-1, 1):
        m.cube("body", "black", sx * 0.75 - 0.2, 4.5, -7.0, sx * 0.75 + 0.2, SY + 0.8, -6.0)   # cheeks
    m.cube("body", "black", -0.6, 4.5, -6.8, 0.6, SY - 0.55, -6.1)                        # lower bridge
    m.cube("body", "black", -0.6, SY + 0.5, -6.8, 0.6, SY + 0.9, -6.1)                    # top bar
    m.rbox("body", "black", 0.9, SY - 0.5, -6.9, 1.7, SY + 0.5, -6.0, c=0.3)               # windage / range drum
    m.cube("body", "gunmetal", 1.65, SY - 0.2, -6.6, 1.75, SY + 0.2, -6.3)
    m.cube("body", "gunmetal", -1.0, 4.1, -12.0, 1.0, 4.5, -10.4)                          # front base
    for sx in (-1, 1):
        m.cube("body", "black", sx * 0.78 - 0.2, 4.4, -11.8, sx * 0.78 + 0.2, SY + 0.9, -10.6)   # hood ears
    m.cube("body", "black", -0.18, 4.4, -11.5, 0.18, SY + 0.05, -11.0)                    # post
    m.cube("body", "black", -0.8, SY + 0.6, -11.8, 0.8, SY + 0.9, -10.6)                  # hood bridge
    # ---------------------------------------------------------------- trigger, selector
    m.slope("body", "black", -0.2, 0.2, -4.1, -2.2, -8.1, -7.6, -6)
    m.cube("body", "stainless", -0.3, -4.6, -6.3, 0.3, -4.0, -5.7)
    m.rbox("body", "black", -1.9, -4.8, -6.1, 1.9, -4.2, -5.5, c=0.2)                       # cross-bolt selector
    m.cube("body", "dot", -1.92, -4.6, -5.95, -1.86, -4.4, -5.75)
    # ---------------------------------------------------------------- twin charging handles (hood underside)
    m.bone("charge", "rifle", (0, 0.2, -10.5))
    for sx in (-1, 1):
        x0, x1 = (1.45, 2.7) if sx > 0 else (-2.7, -1.45)
        m.cube("charge", "gunmetal", x0, -0.7, -11.6, x1, 0.8, -9.4)
        xx0, xx1 = (2.3, 2.8) if sx > 0 else (-2.8, -2.3)
        m.cube("charge", "black", xx0, -0.9, -11.8, xx1, 1.0, -9.2)
    m.bone("bolt", "rifle", (0, 0, 0))
    m.cube("bolt", "stainless", -0.4, -4.48, 7.2, 0.4, -4.4, 10.8)
    # ---------------------------------------------------------------- amber translucent magazine on top
    m.bone("magazine", "rifle", (0, 1.8, 0.0))
    m.rbox("magazine", "amber", -1.3, 1.05, -11.4, 1.3, 2.65, 5.8, c=0.4)
    m.cube("magazine", "black", -1.32, 1.0, -11.5, 1.32, 2.7, -10.9)
    m.cube("magazine", "black", -1.32, 1.0, 5.3, 1.32, 2.7, 5.95)
    for i in range(12):
        zz = -10.2 + i * 1.3
        m.cube("magazine", "brass", -1.33, 1.55, zz, -1.27, 2.2, zz + 0.8)
        m.cube("magazine", "brass", 1.27, 1.55, zz, 1.33, 2.2, zz + 0.8)
    m.cube("magazine", "black", -0.9, 2.6, -10.5, 0.9, 2.7, 4.8)                           # top rib
    m.muzzle_flash(mz - 0.2, length=4.4, width=3.0)
    m.casing(0.0, -4.5, 9.0, length=2.0, r=0.38)
    m.hand_left(-4.6, -11.0)
    m.hand_right(-5.2, -3.6, -2.7)
    cfg = dict(
        name="p90", hand_l=(-4.6, -11.0), mag_grip=(2.0, 5.0), mag_drop=0.0, mag_rock=0,
        grip_x=3.6, route_x=3.8, mag_out=(0, 0.0, 13.5), pouch_off=(2.0, -14.0, 17.0),
        charge_hand="left", charge_bone="charge", handle=(2.9, 0.2, -10.5), bolt_travel=4.2,
        hold_open=True, release_mode="press", catch=(0.3, -9.0), catch_x=3.4,
        fire_len=0.2, cycle=0.05, kick_z=0.9, kick_pitch=1.2, kick_yaw=0.35, flash=0.8,
        reload_len=2.4, charge_len=0.95, release_len=0.6, eject=(0.0, -4.5, 0.25), eject_fall=3.0,
        sight=(SY, SZ), butt=15.35,
    )
    return m, cfg
