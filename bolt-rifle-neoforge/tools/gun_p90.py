"""FN P90 (5.7x28): bullpup PDW with a top-mounted translucent 50-round magazine and integrated sight hood."""
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
    # ---------------------------------------------------------------- body (forward shroud + stock mass)
    m.rbox("body", "poly", -1.3, -2.8, -9.0, 1.3, 2.4, -1.0, c=0.55)
    m.rbox("body", "poly", -1.5, -3.4, -1.2, 1.5, 2.4, 14.2, c=0.8)
    m.cube("body", "black", -1.52, -1.0, -8.2, -1.42, 0.6, -2.2)                        # side recess
    m.cube("body", "black", 1.42, -1.0, -8.2, 1.52, 0.6, -2.2)
    m.cube("body", "gunmetal", -1.0, -3.1, -9.2, 1.0, -2.4, -8.0)                       # muzzle collar
    # sight hood on the front half of the top
    m.rbox("body", "black", -1.3, 2.4, -9.2, 1.3, 4.9, -1.0, c=0.55)
    m.cube("body", "lens", -0.95, 3.1, -9.22, 0.95, 4.5, -9.18)
    m.cube("body", "lens", -0.95, 3.1, -1.02, 0.95, 4.5, -0.98)
    m.cube("body", "dot", -0.14, 3.65, -1.05, 0.14, 3.95, -1.0)
    m.cube("body", "gunmetal", -1.0, 4.9, -8.0, 1.0, 5.2, -2.0)                          # hood top rail
    # thumbhole grip: front bar + trigger guard, grip pillar, bridge, stock mass
    m.cube("body", "poly", -1.0, -6.2, -2.6, 1.0, -3.0, -1.9)
    m.cube("body", "poly", -1.0, -6.2, -2.6, 1.0, -5.5, 0.3)
    m.slope("body", "black", -0.2, 0.2, -4.0, -2.4, -1.1, -0.6, -6)                    # trigger
    m.slope("body", "poly", -1.0, 1.0, -9.0, -3.0, 0.1, 2.5, 8)                         # grip pillar
    m.cube("body", "rubber", -1.05, -8.8, 0.3, 1.05, -3.6, 0.7)
    for i in range(4):
        m.cube("body", "black", -1.06, -8.2 + i * 1.3, 0.8, 1.06, -8.0 + i * 1.3, 1.1)
    m.cube("body", "poly", -1.0, -9.2, 0.2, 1.0, -8.2, 6.6)                              # bridge under the thumbhole
    for i in range(9):                                                                   # stock underside sweeps up to the butt
        z0 = 4.6 + i * 1.08
        bot = -8.8 + (i ** 1.5) * 0.17
        m.cube("body", "poly", -1.4 + i * 0.01, bot, z0, 1.4 - i * 0.01, -3.0, z0 + 1.1, flat=True)
    for i in range(6):                                                                   # moulded grip ribs on the stock sides
        z = 6.0 + i * 1.1
        m.cube("body", "black", -1.52, -6.0 + i * 0.3, z, -1.46, -4.0, z + 0.3)
        m.cube("body", "black", 1.46, -6.0 + i * 0.3, z, 1.52, -4.0, z + 0.3)
    m.rbox("body", "rubber", -1.5, -6.6, 14.0, 1.5, 2.4, 14.9, c=0.5)                           # butt pad
    m.cube("body", "black", -0.55, -8.85, 6.2, 0.55, -8.75, 9.4)                          # underside ejection port
    m.cube("body", "gunmetal", 1.5, -0.6, 3.0, 1.75, 0.4, 5.0)                            # cocking indicator
    m.cube("body", "gunmetal", -1.8, -1.6, 2.4, -1.5, -0.8, 3.8)                          # fire selector (cross-bolt)
    m.cube("body", "gunmetal", 1.5, -1.6, 2.4, 1.8, -0.8, 3.8)
    # ---------------------------------------------------------------- twin charging handles
    m.bone("charge", "rifle", (0, 1.2, -3.0))
    for sx in (-1, 1):
        x0, x1 = (1.45, 2.4) if sx > 0 else (-2.4, -1.45)
        m.cube("charge", "gunmetal", x0, 0.7, -3.8, x1, 1.8, -1.6)
        m.cube("charge", "black", x0 + (0.5 if sx > 0 else -0.4), 0.5, -3.7, x1 + (0.1 if sx > 0 else -0.1) - (0.5 if sx > 0 else -0.4), 2.0, -1.7)
    m.bone("bolt", "rifle", (0, 0, 0))
    m.cube("bolt", "stainless", -0.4, -8.74, 6.4, 0.4, -8.6, 8.8)
    # ---------------------------------------------------------------- translucent top magazine
    m.bone("magazine", "rifle", (0, 3.0, 5.0))
    m.rbox("magazine", "smoke", -1.15, 2.4, -0.6, 1.15, 3.6, 11.8, c=0.3)
    m.cube("magazine", "black", -1.2, 3.55, -0.7, 1.2, 3.75, 0.4)                          # lip + catch
    m.cube("magazine", "black", -1.2, 3.55, 11.2, 1.2, 3.75, 11.9)
    for i in range(10):                                                                 # visible cartridges
        z = -0.1 + i * 1.12
        m.cube("magazine", "brass", -0.7, 3.58, z, 0.7, 3.66, z + 0.7)
    m.muzzle_flash(mz - 0.2, length=4.4, width=3.0)
    m.casing(0.0, -8.7, 7.6, length=2.0, r=0.38)
    m.hand_left(-3.2, -6.2)
    m.hand_right(-6.2, 1.4, -3.6)
    cfg = dict(
        name="p90", hand_l=(-3.2, -6.2), mag_grip=(4.0, 5.4), mag_drop=-9.0, mag_rock=0,
        pouch_off=(3.0, -16.0, 3.0),
        charge_hand="left", charge_bone="charge", handle=(1.9, 1.2, -2.8), bolt_travel=4.2,
        hold_open=True, release_mode="press", catch=(1.0, -3.0), catch_x=1.7,
        fire_len=0.2, cycle=0.05, kick_z=0.9, kick_pitch=1.2, kick_yaw=0.35, flash=0.8,
        reload_len=2.2, charge_len=0.95, release_len=0.55, eject=(0.3, -1.0, 0.25), eject_fall=3.0,
        sight=(3.8, -1.0), butt=14.9,
    )
    return m, cfg
