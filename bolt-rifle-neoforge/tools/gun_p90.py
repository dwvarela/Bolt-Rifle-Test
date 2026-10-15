"""FN P90 (5.7x28): bullpup PDW. Sculpted body with an almond thumbhole, translucent top magazine between two rails,
ambidextrous charging handles and folding iron sights on the front hood."""
from gunlib import Model


def build():
    m = Model("p90", seed=71)
    m.bone("body", "rifle", (0, 0, 0))
    m.bone("barrel", "rifle", (0, 0, 0))
    mz = -16.0
    m.bar("barrel", "steel", 0, 0, mz, -8.0, 0.5, fine=True)
    m.bar("barrel", "black", 0, 0, mz, mz + 2.4, 0.7, fine=True)                       # flash hider
    for i in range(3):
        m.cube("barrel", "steel", -0.95, -0.1, mz + 0.35 + i * 0.6, 0.95, 0.1, mz + 0.55 + i * 0.6)
    m.cube("barrel", "black", -0.3, -0.3, mz - 0.03, 0.3, 0.3, mz + 0.05)
    m.cube("barrel", "gunmetal", -0.9, -0.9, -9.4, 0.9, 0.9, -8.4)                       # barrel collar

    # ---------------------------------------------------------------- sculpted body: sections with their own heights
    sections = [(-9.0, -5.2, 1.25, 1.5, -1.9), (-5.2, -0.5, 1.45, 2.1, -3.0), (-0.5, 5.2, 1.55, 2.2, -3.2)]
    z = 5.2
    while z < 14.19:                                                                    # stock underside rises toward the butt
        sections.append((z, min(z + 1.0, 14.2), 1.55 - (z - 5.2) * 0.012, 2.2, -8.4 + (z - 5.2) * 0.37))
        z += 1.0
    for z0, z1, hw, top, bot in sections:
        m.rbox("body", "poly", -hw, bot, z0, hw, top, z1 + 0.02, c=0.75)
    m.cube("body", "black", -1.57, -0.6, -7.8, -1.5, 0.8, -3.0)                         # side recess (right)
    m.cube("body", "black", 1.5, -0.6, -7.8, 1.57, 0.8, -3.0)
    m.cube("body", "black", -1.6, -1.2, 6.0, -1.55, 0.2, 8.4)                           # cocking-indicator window
    m.cube("body", "gunmetal", -1.7, -2.0, 9.0, -1.58, -1.4, 11.4)
    for i in range(6):                                                                  # moulded grip ribs
        z = 6.4 + i * 1.0
        m.cube("body", "black", -1.58, -4.8 + i * 0.25, z, -1.52, -3.4, z + 0.3)
        m.cube("body", "black", 1.52, -4.8 + i * 0.25, z, 1.58, -3.4, z + 0.3)
    # ---------------------------------------------------------------- top: full-length picatinny rail over the magazine trough
    for sx in (-1, 1):                                                                   # trough walls
        x0, x1 = (1.3, 1.6) if sx > 0 else (-1.6, -1.3)
        m.cube("body", "poly", x0, 2.1, -8.8, x1, 2.5, 13.4)
    m.cube("body", "gunmetal", -1.3, 3.0, -8.8, 1.3, 3.5, 13.4)                          # rail base
    for z in [-8.5 + 0.9 * i for i in range(24)]:                                        # cross slots
        m.cube("body", "black", -1.31, 3.45, z, 1.31, 3.62, z + 0.42)
        m.cube("body", "black", -1.12, 3.0, z + 0.1, -1.0, 3.5, z + 0.35)
    # flip-up iron sights on the rail: front post near the muzzle, rear aperture over the stock
    m.cube("body", "gunmetal", -0.8, 3.5, -8.8, 0.8, 3.9, -7.6)                          # front base
    m.cube("body", "black", -0.18, 3.9, -8.5, 0.18, 5.0, -8.0)                           # front post
    m.cube("body", "black", -0.75, 3.9, -8.6, -0.5, 5.1, -7.9)                           # post guards
    m.cube("body", "black", 0.5, 3.9, -8.6, 0.75, 5.1, -7.9)
    m.cube("body", "gunmetal", -1.0, 3.5, 9.4, 1.0, 3.9, 11.0)                           # rear base
    m.cube("body", "black", -0.9, 3.9, 9.6, -0.5, 5.6, 10.8)                             # aperture cheeks
    m.cube("body", "black", 0.5, 3.9, 9.6, 0.9, 5.6, 10.8)
    m.cube("body", "black", -0.5, 3.9, 9.7, 0.5, 4.7, 10.7)                              # lower bridge
    m.cube("body", "black", -0.5, 5.3, 9.7, 0.5, 5.6, 10.7)                              # upper bar
    m.cube("body", "gunmetal", 0.9, 4.2, 10.0, 1.3, 4.7, 10.5)                           # windage knob
    # ---------------------------------------------------------------- thumbhole grip, trigger guard, bridge
    m.cube("body", "poly", -1.0, -6.0, -3.6, 1.0, -2.9, -3.0)                            # guard front bar
    m.cube("body", "poly", -1.0, -6.0, -3.6, 1.0, -5.4, -0.5)                            # guard bottom
    m.slope("body", "black", -0.2, 0.2, -3.9, -2.4, -2.0, -1.5, -6)                      # trigger
    m.slope("body", "poly", -1.05, 1.05, -8.6, -3.0, -0.4, 1.8, 9)                       # grip pillar
    m.cube("body", "rubber", -1.1, -8.4, 0.0, 1.1, -3.4, 0.4)
    for i in range(4):
        m.cube("body", "black", -1.11, -7.8 + i * 1.2, 0.4, 1.11, -7.6 + i * 1.2, 0.7)
    m.rbox("body", "poly", -1.05, -8.8, 0.3, 1.05, -7.9, 6.6, c=0.3)                     # bridge under the thumbhole
    m.cube("body", "black", -0.6, -6.2, 8.0, 0.6, -6.05, 11.2)                           # underside ejection port
    m.rbox("body", "rubber", -1.45, -5.2, 14.0, 1.45, 2.2, 14.9, c=0.5)                  # butt pad
    m.cube("body", "gunmetal", -1.8, -1.6, 3.0, -1.5, -0.8, 4.3)                         # fire selector
    m.cube("body", "gunmetal", 1.5, -1.6, 3.0, 1.8, -0.8, 4.3)
    # ---------------------------------------------------------------- twin charging handles
    m.bone("charge", "rifle", (0, 0.9, -2.2))
    for sx in (-1, 1):
        x0, x1 = (1.45, 2.6) if sx > 0 else (-2.6, -1.45)
        m.cube("charge", "gunmetal", x0, 0.4, -3.0, x1, 1.4, -1.4)
        xx0, xx1 = (2.3, 2.7) if sx > 0 else (-2.7, -2.3)
        m.cube("charge", "black", xx0, 0.2, -3.2, xx1, 1.6, -1.2)
    m.bone("bolt", "rifle", (0, 0, 0))
    m.cube("bolt", "stainless", -0.4, -6.18, 8.2, 0.4, -6.1, 10.8)
    # ---------------------------------------------------------------- translucent top magazine
    m.bone("magazine", "rifle", (0, 2.6, 4.0))
    m.rbox("magazine", "smoke", -1.25, 2.25, -3.4, 1.25, 3.0, 9.2, c=0.25)
    m.cube("magazine", "black", -1.27, 2.2, -3.5, 1.27, 3.0, -2.7)
    m.cube("magazine", "black", -1.27, 2.2, 8.6, 1.27, 3.0, 9.3)
    for i in range(10):                                                                 # cartridges seen through the side wall
        z = -2.3 + i * 1.0
        m.cube("magazine", "brass", -1.29, 2.4, z, -1.24, 2.9, z + 0.6)
        m.cube("magazine", "brass", 1.24, 2.4, z, 1.29, 2.9, z + 0.6)
    m.muzzle_flash(mz - 0.2, length=4.4, width=3.0)
    m.casing(0.0, -6.2, 9.6, length=2.0, r=0.38)
    m.hand_left(-3.2, -6.2)
    m.hand_right(-6.0, 0.6, -3.5)
    cfg = dict(
        name="p90", hand_l=(-3.2, -6.2), mag_grip=(2.7, 5.4), mag_drop=0.0, mag_rock=0,
        grip_x=3.6, route_x=3.8, mag_out=(0, 0.0, 13.5), pouch_off=(2.0, -14.0, 17.0),
        charge_hand="left", charge_bone="charge", handle=(2.9, 0.9, -2.2), bolt_travel=4.2,
        hold_open=True, release_mode="press", catch=(0.9, -2.2), catch_x=3.4,
        fire_len=0.2, cycle=0.05, kick_z=0.9, kick_pitch=1.2, kick_yaw=0.35, flash=0.8,
        reload_len=2.4, charge_len=0.95, release_len=0.6, eject=(0.3, -1.0, 0.25), eject_fall=3.0,
        sight=(5.0, 10.2), butt=14.9,
    )
    return m, cfg
