"""HK MP7A1 (4.6x30): compact polymer PDW with top rail + red dot, wire stock, extended 40-round magazine."""
from gunlib import Model

RAKE = 12
P = [0, -3.4, 1.8]


def g(m, bone, mat, x0, y0, z0, x1, y1, z1):
    m.cube(bone, mat, x0, y0, z0, x1, y1, z1, rot=[RAKE, 0, 0], pivot=P)


def build():
    m = Model("mp7", seed=61)
    m.bone("body", "rifle", (0, 0, 0))
    m.bone("barrel", "rifle", (0, 0, 0))
    mz = -17.0
    m.bar("barrel", "steel", 0, 0, mz, -9.0, 0.5, fine=True)
    m.bar("barrel", "black", 0, 0, mz, mz + 2.2, 0.68, fine=True)                      # flash hider
    for i in range(3):
        m.cube("barrel", "steel", -0.9, -0.1, mz + 0.3 + i * 0.6, 0.9, 0.1, mz + 0.5 + i * 0.6)
    m.cube("barrel", "black", -0.3, -0.3, mz - 0.03, 0.3, 0.3, mz + 0.05)
    # ---------------------------------------------------------------- receiver (polymer housing, steel nose)
    m.rbox("body", "poly", -1.2, -1.7, -12.4, 1.2, 2.5, 3.6, c=0.4)
    m.rbox("body", "steel", -0.95, -1.0, -13.4, 0.95, 1.5, -12.3, c=0.3)                  # front cap around the barrel
    m.cube("body", "black", -1.22, 0.3, -2.4, -1.12, 1.9, 1.8)                             # ejection port (right)
    m.cube("body", "gunmetal", 1.12, -0.6, -4.0, 1.25, 0.2, -0.8)                          # left side plate
    for i in range(5):                                                                    # side vents
        m.cube("body", "black", -1.22, -0.4, -9.5 + i * 0.9, -1.12, 1.9, -9.2 + i * 0.9)
    m.rbox("body", "poly", -1.2, -4.0, -3.6, 1.2, -1.6, 3.6, c=0.35)                       # lower frame
    m.cube("body", "gunmetal", -1.0, 2.5, -10.0, 1.0, 3.0, 3.4)                            # top rail
    for z in [-9.6 + 0.9 * i for i in range(14)]:
        m.cube("body", "black", -1.05, 2.95, z, 1.05, 3.15, z + 0.4)
    # folded fore-grip
    m.slope("body", "poly", -0.8, 0.8, -5.2, -1.7, -9.2, -7.4, 8)
    m.cube("body", "rubber", -0.85, -5.4, -9.2, 0.85, -4.6, -7.4)
    # pistol grip + trigger guard
    g(m, "body", "poly", -1.0, -8.4, 0.2, 1.0, -2.0, 4.0)
    for i in range(4):
        g(m, "body", "black", -1.02, -7.6 + i * 1.2, 0.0, 1.02, -7.4 + i * 1.2, 0.35)
    g(m, "body", "rubber", -1.05, -8.4, 3.6, 1.05, -3.0, 4.2)
    m.cube("body", "poly", -0.6, -4.9, -3.4, 0.6, -4.3, 0.3)
    m.cube("body", "poly", -0.6, -4.9, -3.4, 0.6, -1.6, -2.9)
    m.slope("body", "black", -0.2, 0.2, -4.0, -2.3, -0.9, -0.4, -6)                       # trigger
    m.cube("body", "gunmetal", -1.25, -2.4, 0.9, -1.0, -1.9, 2.0)                          # selector
    m.cube("body", "gunmetal", 1.0, -3.5, -2.0, 1.4, -3.0, -0.8)                           # mag/bolt catch
    # ---------------------------------------------------------------- red dot
    m.bar("body", "scope", 0, 3.95, -2.3, 1.7, 0.95, fine=True)
    m.rbox("body", "scope", -0.95, 3.1, -1.6, 0.95, 3.5, 1.4, c=0.15)
    m.cube("body", "lens", -0.82, 3.2, -2.32, 0.82, 4.7, -2.28)
    m.cube("body", "lens", -0.82, 3.2, 1.68, 0.82, 4.7, 1.72)
    m.cube("body", "dot", -0.14, 3.75, 1.6, 0.14, 4.05, 1.66)
    # ---------------------------------------------------------------- wire stock
    for sx in (-0.95, 0.95):
        m.cube("body", "steel", sx - 0.2, -0.9, 3.4, sx + 0.2, -0.5, 14.0)
        m.cube("body", "steel", sx - 0.2, -3.9, 13.6, sx + 0.2, -0.5, 14.0)
    m.cube("body", "steel", -0.95, -3.9, 13.6, 0.95, -3.5, 14.0)
    m.rbox("body", "rubber", -1.0, -3.9, 13.9, 1.0, -0.2, 14.8, c=0.3)
    # ---------------------------------------------------------------- folding charging handle (rear, on top)
    m.bone("charge", "rifle", (0, 2.5, 3.0))
    m.cube("charge", "gunmetal", -0.3, 2.45, 2.6, 0.3, 3.3, 5.6)
    m.rbox("charge", "black", -0.9, 2.5, 4.9, 0.9, 3.6, 6.0, c=0.2)
    m.bone("bolt", "rifle", (0, 0, 0))
    m.cube("bolt", "stainless", -1.26, 0.45, -1.8, -1.1, 1.6, 0.9)
    # ---------------------------------------------------------------- 40-round magazine
    m.bone("magazine", "rifle", (0, -3.4, 1.8))
    g(m, "magazine", "smoke", -0.85, -12.6, 0.6, 0.85, -3.0, 3.8)
    g(m, "magazine", "black", -0.9, -13.2, 0.45, 0.9, -12.6, 3.95)
    g(m, "magazine", "brass", -0.5, -3.3, 1.0, 0.5, -3.0, 3.4)
    for i in range(5):
        g(m, "magazine", "brass", -0.86, -11.4 + i * 1.8, 1.3, -0.82, -10.8 + i * 1.8, 3.0)
    m.muzzle_flash(mz - 0.2, length=4.4, width=3.0)
    m.casing(-1.2, 1.0, -0.4, length=2.2, r=0.4)
    m.hand_left(-2.6, -8.2)
    m.hand_right(-5.8, 2.6, -2.8)
    cfg = dict(
        name="mp7", hand_l=(-2.6, -8.2), mag_grip=(-11.0, 2.8), mag_drop=8.0, mag_rock=3,
        charge_hand="left", charge_bone="charge", handle=(0, 3.0, 5.4), bolt_travel=4.0,
        hold_open=True, release_mode="press", catch=(-3.2, -1.4), catch_x=1.6,
        fire_len=0.2, cycle=0.05, kick_z=1.0, kick_pitch=1.5, kick_yaw=0.4, flash=0.8,
        reload_len=1.9, charge_len=0.95, release_len=0.55, eject=(-1.0, 1.0, 0.7),
        sight=(4.2, 1.7), butt=14.8,
    )
    return m, cfg
