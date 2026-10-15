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
    mz = -15.4
    m.bar("barrel", "steel", 0, 0, mz, -9.0, 0.5, fine=True)
    m.bar("barrel", "black", 0, 0, mz, mz + 2.2, 0.68, fine=True)                      # flash hider
    for i in range(3):
        m.cube("barrel", "steel", -0.9, -0.1, mz + 0.3 + i * 0.6, 0.9, 0.1, mz + 0.5 + i * 0.6)
    m.cube("barrel", "black", -0.3, -0.3, mz - 0.03, 0.3, 0.3, mz + 0.05)
    # ---------------------------------------------------------------- receiver (polymer housing, steel nose)
    m.rbox("body", "poly", -1.2, -1.7, -12.4, 1.2, 2.5, 3.6, c=0.7)
    m.rbox("body", "poly", -0.9, 2.3, -12.0, 0.9, 2.9, -10.0, c=0.2)
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
    m.rbox("body", "poly", -0.85, -8.4, -9.5, 0.85, -1.6, -7.3, c=0.35)                    # vertical fore-grip (deployed)
    m.cube("body", "rubber", -0.88, -8.5, -9.55, 0.88, -3.6, -7.25)
    for i in range(5):
        m.cube("body", "black", -0.9, -8.0 + i * 0.9, -9.6, 0.9, -7.85 + i * 0.9, -7.2)
    # pistol grip + trigger guard
    g(m, "body", "poly", -1.05, -9.6, 0.1, 1.05, -2.0, 4.1)
    g(m, "body", "black", -0.9, -9.7, 0.5, 0.9, -9.4, 3.7)                                   # magwell mouth
    for i in range(5):
        g(m, "body", "black", -1.07, -8.8 + i * 1.3, -0.05, 1.07, -8.6 + i * 1.3, 0.3)
    g(m, "body", "rubber", -1.1, -9.6, 3.7, 1.1, -3.0, 4.25)
    m.cube("body", "poly", -0.6, -4.9, -3.4, 0.6, -4.3, 0.3)
    m.cube("body", "poly", -0.6, -4.9, -3.4, 0.6, -1.6, -2.9)
    m.cube("body", "stainless", -0.28, -4.3, -1.0, 0.28, -2.0, -0.35)                       # trigger blade
    m.cube("body", "stainless", -0.28, -4.3, -1.5, 0.28, -3.8, -0.35)                       # trigger shoe
    m.cube("body", "gunmetal", -1.25, -2.4, 0.9, -1.0, -1.9, 2.0)                          # selector
    m.cube("body", "gunmetal", 1.0, -3.5, -2.0, 1.4, -3.0, -0.8)                           # mag/bolt catch
    # ---------------------------------------------------------------- folding iron sights on the rail
    m.cube("body", "gunmetal", -0.8, 3.15, -10.6, 0.8, 3.7, -9.4)                         # front base
    m.cube("body", "black", -0.18, 3.7, -10.3, 0.18, 4.55, -9.8)                           # front post
    m.cube("body", "black", -0.75, 3.7, -10.5, -0.5, 4.6, -9.7)                            # protective ears
    m.cube("body", "black", 0.5, 3.7, -10.5, 0.75, 4.6, -9.7)
    m.cube("body", "gunmetal", -0.9, 3.15, -1.4, 0.9, 3.7, 0.4)                            # rear base
    m.cube("body", "black", -0.85, 3.7, -1.2, -0.45, 5.3, 0.2)                             # rear aperture cheeks
    m.cube("body", "black", 0.45, 3.7, -1.2, 0.85, 5.3, 0.2)
    m.cube("body", "black", -0.5, 3.7, -1.1, 0.5, 4.15, 0.1)                               # lower bridge
    m.cube("body", "black", -0.5, 4.85, -1.1, 0.5, 5.3, 0.1)                               # upper bar
    # ---------------------------------------------------------------- telescoping single-rod stock + plate
    m.bar("body", "steel", 0, 0.5, 3.4, 17.0, 0.42, fine=True)
    m.cube("body", "gunmetal", -0.7, -0.2, 3.4, 0.7, 1.2, 4.6)                              # stock sleeve
    m.rbox("body", "poly", -1.15, -4.6, 16.6, 1.15, 1.9, 17.7, c=0.45)                      # butt plate
    m.rbox("body", "rubber", -1.18, -4.4, 17.6, 1.18, 1.7, 18.1, c=0.4)                      # pad
    m.cube("body", "black", -0.5, 1.9, 16.8, 0.5, 2.4, 17.6)                                 # top hook
    for i in range(4):
        m.cube("body", "black", -1.19, -3.8 + i * 1.2, 17.3, 1.19, -3.6 + i * 1.2, 17.6)      # grip ribs
    # ---------------------------------------------------------------- folding charging handle (rear, on top)
    m.bone("charge", "rifle", (0, 2.5, 3.0))
    m.cube("charge", "gunmetal", -0.3, 2.45, 2.6, 0.3, 3.3, 5.6)
    m.rbox("charge", "black", -0.9, 2.5, 4.9, 0.9, 3.6, 6.0, c=0.2)
    m.bone("bolt", "rifle", (0, 0, 0))
    m.cube("bolt", "stainless", -1.26, 0.45, -1.8, -1.1, 1.6, 0.9)
    # ---------------------------------------------------------------- 40-round magazine
    m.bone("magazine", "rifle", (0, -3.4, 1.8))
    g(m, "magazine", "poly", -0.85, -12.6, 0.6, 0.85, -3.0, 3.8)
    g(m, "magazine", "rubber", -0.9, -13.2, 0.45, 0.9, -12.6, 3.95)
    g(m, "magazine", "brass", -0.5, -3.3, 1.0, 0.5, -3.0, 3.4)
    for i in range(4):
        g(m, "magazine", "black", -0.87, -12.0 + i * 0.7, 1.0, -0.8, -11.8 + i * 0.7, 3.4)
    m.muzzle_flash(mz - 0.2, length=4.4, width=3.0)
    m.casing(-1.2, 1.0, -0.4, length=2.2, r=0.4)
    m.hand_left(-8.6, -8.4)
    m.hand_right(-5.8, 2.6, -2.8)
    cfg = dict(
        name="mp7", hand_l=(-8.6, -8.4), mag_grip=(-11.0, 2.8), mag_drop=8.0, mag_rock=3,
        charge_hand="left", charge_bone="charge", handle=(0, 3.0, 5.4), bolt_travel=4.0,
        hold_open=True, release_mode="press", catch=(-3.2, -1.4), catch_x=3.0,
        fire_len=0.2, cycle=0.05, kick_z=1.0, kick_pitch=1.5, kick_yaw=0.4, flash=0.8,
        reload_len=1.9, charge_len=0.95, release_len=0.6, eject=(-1.0, 1.0, 0.7),
        sight=(4.5, -0.5), butt=18.1,
    )
    return m, cfg
