"""AK-47 (Type 3 style, wood furniture): model + animation config."""
from gunlib import Model

ID = "ak47"


def build():
    m = Model(ID, seed=11)
    m.bone("wood", "rifle", (0, 0, 0))
    m.bone("barrel", "rifle", (0, 0, 0))
    m.bone("receiver", "rifle", (0, 0, 0))

    # ---- barrel, brake, front sight with hood, gas block
    m.bar("barrel", "steel", 0, 0, -26.5, -6.0, 0.9)
    m.bar("barrel", "black", 0, 0, -27.6, -26.3, 1.15)                       # muzzle nut / slant
    m.cube("barrel", "black", -0.5, -0.5, -27.65, 0.5, 0.5, -27.55)           # bore
    m.cube("barrel", "gunmetal", -0.9, 0.8, -26.0, 0.9, 2.2, -22.8)           # sight base
    m.cube("barrel", "steel", -0.28, 2.2, -25.3, 0.28, 3.95, -24.7)           # post
    m.cube("barrel", "gunmetal", -1.25, 2.2, -25.9, -0.85, 4.3, -23.9)        # hood (right)
    m.cube("barrel", "gunmetal", 0.85, 2.2, -25.9, 1.25, 4.3, -23.9)          # hood (left)
    m.cube("barrel", "gunmetal", -1.25, 4.0, -25.9, 1.25, 4.4, -23.9)         # hood top
    m.cube("barrel", "gunmetal", -1.2, -0.9, -19.5, 1.2, 1.7, -15.2)          # gas block
    m.cube("barrel", "steel", -0.6, 1.5, -15.2, 0.6, 2.0, -14.4)              # gas tube stub
    m.cube("barrel", "steel", -0.5, -1.6, -16.2, 0.5, -0.8, -15.4)            # cleaning rod ring

    # ---- wood furniture
    m.cube("wood", "plum", -1.45, 0.9, -14.6, 1.45, 3.0, -6.5)                # upper handguard
    m.cube("wood", "plum", -1.9, -3.4, -17.0, 1.9, 0.6, -6.2)                 # lower handguard
    m.cube("wood", "plum", -1.5, -3.0, -18.6, 1.5, 0.2, -17.0)                # taper
    m.cube("wood", "gunmetal", -1.95, -3.7, -9.5, 1.95, -3.3, -9.1)           # handguard ferrule
    m.cube("wood", "plum", -1.5, -4.6, 3.5, 1.5, -2.4, 6.8)                   # grip top
    m.cube("wood", "plum", -1.5, -7.0, 3.8, 1.5, -4.6, 7.3)
    m.cube("wood", "plum", -1.5, -9.6, 4.3, 1.5, -7.0, 7.9)
    m.cube("wood", "rubber", -1.55, -9.9, 4.2, 1.55, -9.6, 8.0)               # grip cap
    m.cube("wood", "plum", -1.6, -3.0, 6.0, 1.6, 1.9, 9.8)                    # stock neck
    m.cube("wood", "plum", -1.7, -7.2, 9.8, 1.7, 1.4, 14.0)
    m.cube("wood", "plum", -1.75, -8.0, 14.0, 1.75, 1.2, 18.2)
    m.cube("wood", "black", -1.8, -8.4, 18.2, 1.8, 1.0, 19.0)                 # butt plate
    m.cube("wood", "gunmetal", -1.8, 1.2, 9.8, 1.8, 1.5, 10.8)                # stock screw plate

    # ---- stamped receiver, dust cover, sights, controls
    m.cube("receiver", "gunmetal", -1.9, -2.6, -6.5, 1.9, 2.6, 6.2)
    m.cube("receiver", "gunmetal", -1.7, 2.6, -4.2, 1.7, 3.4, 6.6)            # dust cover
    m.cube("receiver", "steel", -0.2, 3.4, -3.0, 0.2, 3.7, 6.0)               # cover rib
    m.cube("receiver", "gunmetal", -1.3, 2.4, -8.4, 1.3, 3.6, -4.8)           # rear sight base
    m.cube("receiver", "steel", -0.9, 3.6, -8.4, 0.9, 4.2, -4.4)              # ladder leaf
    m.cube("receiver", "gunmetal", -1.0, 3.6, -5.7, -0.35, 4.7, -4.7)         # notch (right)
    m.cube("receiver", "gunmetal", 0.35, 3.6, -5.7, 1.0, 4.7, -4.7)           # notch (left)
    m.cube("receiver", "black", -2.0, 0.0, -4.6, -1.86, 1.9, 2.2)             # ejection port
    m.cube("receiver", "steel", -2.4, -1.0, -1.8, -1.9, 0.0, 1.4)             # selector lever
    m.cube("receiver", "black", -1.9, -1.6, -6.5, 1.9, -1.4, -6.3)
    m.cube("receiver", "gunmetal", -1.8, -4.8, -6.5, 1.8, -2.6, -1.0)         # magwell
    m.cube("receiver", "steel", -0.4, -4.7, -1.0, 0.4, -4.1, 3.6)             # trigger guard
    m.cube("receiver", "steel", -0.4, -4.7, -1.0, 0.4, -2.6, -0.4)
    m.cube("receiver", "steel", -0.4, -4.7, 3.0, 0.4, -2.6, 3.6)
    m.cube("receiver", "black", -0.25, -4.0, 1.0, 0.25, -2.2, 1.6)            # trigger
    m.cube("receiver", "steel", -1.95, -0.7, 0.2, -1.8, 0.1, 2.2)

    # ---- bolt carrier + reciprocating charging handle (right side)
    m.bone("bolt", "rifle", (0, 0, 0))
    m.cube("bolt", "stainless", -1.99, 0.2, -3.2, -1.9, 1.7, 0.8)             # carrier seen in port
    m.cube("bolt", "steel", -1.9, 0.9, 0.8, 1.9, 2.4, 4.0)                    # carrier body under cover
    m.bone("bolt_handle", "bolt", (-2.4, 1.0, -1.0))
    m.cube("bolt_handle", "steel", -3.6, 0.5, -1.6, -1.9, 1.5, -0.3)
    m.cube("bolt_handle", "black", -4.7, -0.2, -2.1, -3.5, 2.2, 0.3)
    m.hand_bolt("bolt_handle", -4.0, 1.0, -1.0)

    # ---- magazine: banana, curving forward; pivot at the front catch for the rock-in
    m.bone("magazine", "rifle", (0, -2.8, -5.2))
    for i in range(6):
        y1, y0 = -2.6 - 2.0 * i, -2.6 - 2.0 * (i + 1)
        zc = -3.2 - i * i * 0.18 - i * 0.2
        m.cube("magazine", "poly" if i % 2 else "black", -1.3, y0, zc - 2.3, 1.3, y1, zc + 2.3)
        m.cube("magazine", "steel", -1.35, y0 + 0.9, zc - 2.35, 1.35, y0 + 1.1, zc + 2.35)   # ribs
    zc = -3.2 - 25 * 0.18 - 1.0
    m.cube("magazine", "steel", -1.4, -14.9, zc - 2.4, 1.4, -14.5, zc + 2.4)                  # base plate
    m.cube("magazine", "brass", -0.7, -2.7, -4.6, 0.7, -2.5, -1.8)                           # round peeking

    m.muzzle_flash(-27.7)
    m.casing(-2.0, 0.9, -1.0)
    m.hand_left(-4.7, -12.0)
    m.hand_right(-6.4, 5.6, -3.2)

    cfg = dict(
        name=ID, hand_l=(-4.7, -12.0), mag_grip=(-11.5, -7.4), mag_drop=9.0, mag_rock=17,
        charge_hand="right", handle=(-4.0, 1.0, -1.0), bolt_travel=7.0, hold_open=False,
        fire_len=0.28, cycle=0.10, kick_z=2.3, kick_pitch=3.2, kick_yaw=0.8, flash=1.1,
        reload_len=2.3, charge_len=0.95, release_len=0.0, eject=(-1.0, 1.0, 0.9),
        sight=(4.7, -5.2), butt=19.0,
    )
    return m, cfg
