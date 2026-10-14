"""Glock G45 Gen 7: 9x19 full-size pistol, black nDLC slide, polymer frame with front-strap grooves."""
from gunlib import Model

RAKE = 20
P = [0, -4.7, 2.6]


def g(m, bone, mat, x0, y0, z0, x1, y1, z1):
    """Part of the raked grip/magazine column."""
    m.cube(bone, mat, x0, y0, z0, x1, y1, z1, rot=[RAKE, 0, 0], pivot=P)


def build():
    m = Model("g45", seed=51)
    m.bone("body", "rifle", (0, 0, 0))
    m.bone("barrel", "rifle", (0, 0, 0))
    # ---------------------------------------------------------------- barrel (peeks out the front of the slide)
    m.cube("barrel", "steel", -0.42, -0.42, -7.15, 0.42, 0.42, -6.0)
    m.cube("barrel", "black", -0.2, -0.2, -7.17, 0.2, 0.2, -7.1)
    # ---------------------------------------------------------------- frame
    m.rbox("body", "poly", -0.72, -2.4, -5.6, 0.72, -0.85, 4.3, c=0.3)                  # dust cover + rear frame
    m.cube("body", "black", -0.73, -1.9, -4.8, 0.73, -1.55, -3.8)                        # accessory rail slot
    m.cube("body", "black", -0.73, -1.9, -3.4, 0.73, -1.55, -2.9)
    m.cube("body", "poly", -0.7, -1.4, 2.4, 0.7, -0.85, 4.7)                             # beavertail
    g(m, "body", "poly", -0.85, -8.4, 0.9, 0.85, -1.0, 4.3)                              # grip
    g(m, "body", "rubber", -0.9, -8.0, 0.7, 0.9, -3.4, 1.0)                              # front-strap texture band
    for i in range(4):
        g(m, "body", "black", -0.9, -7.8 + i * 1.1, 0.55, 0.9, -7.65 + i * 1.1, 0.95)    # finger grooves
    g(m, "body", "rubber", -0.9, -8.0, 4.0, 0.9, -3.4, 4.45)                             # backstrap panel
    for i in range(3):
        g(m, "body", "black", -0.88, -7.0 + i * 1.5, 1.6, -0.84, -6.85 + i * 1.5, 3.4)     # side stipple lines (right)
        g(m, "body", "black", 0.84, -7.0 + i * 1.5, 1.6, 0.88, -6.85 + i * 1.5, 3.4)
    # trigger guard + trigger
    m.cube("body", "poly", -0.6, -3.5, -3.9, 0.6, -2.9, -0.3)
    m.cube("body", "poly", -0.6, -3.5, -3.9, 0.6, -0.85, -3.4)
    m.cube("body", "black", -0.2, -2.9, -1.2, 0.2, -1.2, -0.7)                           # trigger
    m.cube("body", "gunmetal", -0.12, -1.9, -1.0, 0.12, -1.5, -0.85)                      # safety blade
    # left-side controls
    m.cube("body", "steel", 0.72, -1.15, -1.0, 0.95, -0.7, 1.9)                           # slide stop lever
    m.cube("body", "steel", 0.72, -1.7, -2.7, 0.9, -1.2, -1.6)                            # takedown lever
    m.cube("body", "black", 0.8, -3.4, 1.6, 1.0, -2.8, 2.3)                               # magazine release
    # ---------------------------------------------------------------- slide
    m.bone("bolt", "rifle", (0, 0, 0))
    m.rbox("bolt", "black", -0.75, -0.9, -6.2, 0.75, 1.1, 4.5, c=0.35)
    m.cube("bolt", "steel", -0.2, 1.1, -6.2, 0.2, 1.25, 4.5)                              # flat top plate
    for i in range(4):                                                                   # rear cocking serrations
        z = 2.7 + i * 0.5
        m.cube("bolt", "steel", -0.78, -0.6, z, -0.7, 0.9, z + 0.2)
        m.cube("bolt", "steel", 0.7, -0.6, z, 0.78, 0.9, z + 0.2)
    for i in range(3):                                                                   # front serrations
        z = -5.7 + i * 0.45
        m.cube("bolt", "steel", -0.78, -0.6, z, -0.7, 0.9, z + 0.18)
        m.cube("bolt", "steel", 0.7, -0.6, z, 0.78, 0.9, z + 0.18)
    m.cube("bolt", "steel", -0.78, 0.05, -2.9, -0.55, 1.0, -0.6)                          # ejection port (right)
    m.cube("bolt", "brass", -0.6, 0.1, -2.5, -0.5, 0.4, -1.0)                              # chambered round glints in the port
    m.cube("bolt", "stainless", 0.78, 0.3, -1.4, 0.83, 0.55, -0.9)                         # loaded-chamber indicator
    m.cube("bolt", "steel", -0.2, 1.25, -6.0, 0.2, 1.75, -5.4)                            # front sight
    m.cube("bolt", "steel", -0.7, 1.25, 3.3, -0.25, 1.75, 4.2)                            # rear sight (notched)
    m.cube("bolt", "steel", 0.25, 1.25, 3.3, 0.7, 1.75, 4.2)
    m.cube("bolt", "white" if False else "stainless", -0.15, 1.3, -5.45, 0.15, 1.7, -5.4)  # sight dot
    # ---------------------------------------------------------------- magazine (steel body shows below the grip)
    m.bone("magazine", "rifle", (0, -4.7, 2.6))
    g(m, "magazine", "steel", -0.62, -9.0, 1.35, 0.62, -2.0, 3.85)
    g(m, "magazine", "poly", -0.64, -9.6, 1.2, 0.64, -9.0, 4.0)                          # polymer floorplate
    g(m, "magazine", "black", -0.66, -9.35, 1.2, 0.66, -9.25, 4.0)
    g(m, "magazine", "brass", -0.4, -2.3, 1.7, 0.4, -2.0, 3.4)
    # ---------------------------------------------------------------- shared parts
    m.muzzle_flash(-7.2, y=0.0, length=4.2, width=2.8)
    m.casing(-0.8, 0.5, -1.6, length=2.0, r=0.38)
    m.hand_left(-8.0, 2.8)
    m.hand_right(-4.4, 3.0, -2.1)
    cfg = dict(
        name="g45", hand_l=(-8.0, 2.8), mag_grip=(-8.8, 3.2), mag_drop=7.0, mag_rock=0,
        charge_hand="left", charge_bone="bolt", handle=(0.0, 0.3, 3.4), bolt_travel=3.6,
        hold_open=True, release_mode="press", catch=(-0.9, 0.2), catch_x=1.5,
        fire_len=0.26, cycle=0.06, kick_z=1.1, kick_pitch=4.2, kick_yaw=0.6, flash=0.9,
        reload_len=1.7, charge_len=0.9, release_len=0.5, eject=(-1.0, 1.0, 0.6),
        sight=(1.75, 3.8), butt=5.0,
    )
    return m, cfg
