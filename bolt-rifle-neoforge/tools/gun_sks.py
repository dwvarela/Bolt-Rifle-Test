"""SKS (Simonov carbine, wood stock, hooded front sight): model + animation config."""
from gunlib import Model

ID = "sks"


def build():
    m = Model(ID, seed=21)
    m.bone("wood", "rifle", (0, 0, 0))
    m.bone("barrel", "rifle", (0, 0, 0))
    m.bone("receiver", "rifle", (0, 0, 0))

    # ---- barrel, muzzle, hooded front sight, gas system, folded spike bayonet
    m.bar("barrel", "steel", 0, 0, -30.5, -8.0, 0.9)
    m.bar("barrel", "black", 0, 0, -31.6, -30.3, 1.1)
    m.cube("barrel", "black", -0.5, -0.5, -31.65, 0.5, 0.5, -31.55)
    m.cube("barrel", "gunmetal", -0.9, 0.8, -30.0, 0.9, 2.2, -26.6)           # sight base
    m.cube("barrel", "steel", -0.28, 2.2, -29.3, 0.28, 3.9, -28.7)            # post
    m.cube("barrel", "gunmetal", -1.25, 2.2, -29.9, -0.85, 4.25, -27.9)       # hood
    m.cube("barrel", "gunmetal", 0.85, 2.2, -29.9, 1.25, 4.25, -27.9)
    m.cube("barrel", "gunmetal", -1.25, 3.95, -29.9, 1.25, 4.35, -27.9)
    m.cube("barrel", "gunmetal", -1.1, -0.9, -23.0, 1.1, 1.5, -20.0)          # gas block
    m.bar("barrel", "steel", 0, 1.9, -20.0, -9.0, 0.8)                        # gas tube
    m.cube("barrel", "steel", -0.35, -1.9, -29.6, 0.35, -1.1, -14.0)          # bayonet (folded)
    m.cube("barrel", "steel", -0.45, -2.4, -14.4, 0.45, -1.1, -13.6)          # bayonet pivot

    # ---- wood: forend + top handguard + stock
    m.cube("wood", "wood", -1.9, -3.3, -21.0, 1.9, 0.6, -8.0)                  # forend
    m.cube("wood", "wood", -1.5, -2.9, -23.0, 1.5, 0.2, -21.0)
    m.cube("wood", "gunmetal", -1.95, -3.6, -22.0, 1.95, -3.2, -21.4)         # nose cap
    m.cube("wood", "wood", -1.5, 0.8, -17.0, 1.5, 3.0, -8.2)                   # top handguard
    m.cube("wood", "wood", -2.0, -4.6, -8.0, 2.0, 0.0, 7.0)                    # stock under receiver
    m.cube("wood", "wood", -1.8, -6.6, 7.0, 1.8, 0.8, 11.0)                    # wrist
    m.cube("wood", "wood", -1.8, -7.0, 11.0, 1.8, 0.8, 15.0)
    m.cube("wood", "wood", -1.8, -8.0, 15.0, 1.8, 0.6, 19.4)                   # butt
    m.cube("wood", "steel", -1.85, -8.4, 19.4, 1.85, 0.4, 20.2)                # butt plate
    m.cube("wood", "wood", -1.85, 0.5, 7.0, 1.85, 1.1, 11.0)

    # ---- receiver: milled, dust cover, tangent rear sight
    m.cube("receiver", "gunmetal", -1.9, 0.0, -8.0, 1.9, 2.4, 7.0)
    m.cube("receiver", "gunmetal", -1.7, 2.4, -3.0, 1.7, 3.0, 6.8)             # dust cover
    m.cube("receiver", "gunmetal", -1.3, 2.4, -9.0, 1.3, 3.5, -5.2)            # rear sight base
    m.cube("receiver", "steel", -0.9, 3.5, -9.0, 0.9, 4.1, -4.8)
    m.cube("receiver", "gunmetal", -1.0, 3.5, -6.2, -0.35, 4.6, -5.2)          # notch
    m.cube("receiver", "gunmetal", 0.35, 3.5, -6.2, 1.0, 4.6, -5.2)
    m.cube("receiver", "black", -2.0, 0.2, -4.4, -1.86, 1.9, 2.0)              # ejection port
    m.cube("receiver", "steel", -1.9, -0.3, -8.0, 1.9, 0.3, 7.0)
    m.cube("receiver", "steel", -0.4, -6.0, -0.6, 0.4, -5.4, 4.0)              # trigger guard
    m.cube("receiver", "steel", -0.4, -6.0, -0.6, 0.4, -4.4, -0.0)
    m.cube("receiver", "steel", -0.4, -6.0, 3.4, 0.4, -4.4, 4.0)
    m.cube("receiver", "black", -0.25, -5.4, 1.2, 0.25, -3.6, 1.8)             # trigger
    m.cube("receiver", "steel", -1.0, -4.9, 1.8, 1.0, -4.5, 3.2)               # safety lever

    # ---- bolt carrier + handle (right side)
    m.bone("bolt", "rifle", (0, 0, 0))
    m.cube("bolt", "stainless", -1.99, 0.4, -3.4, -1.9, 1.7, 1.0)
    m.cube("bolt", "steel", -1.9, 0.9, 1.0, 1.9, 2.2, 4.4)
    m.bone("bolt_handle", "bolt", (-2.4, 1.1, -1.2))
    m.cube("bolt_handle", "steel", -3.5, 0.6, -1.8, -1.9, 1.6, -0.4)
    m.cube("bolt_handle", "steel", -4.5, 0.1, -2.2, -3.4, 2.1, 0.0)
    m.hand_bolt("bolt_handle", -3.9, 1.1, -1.2)

    # ---- detachable box magazine (10 rounds)
    m.bone("magazine", "rifle", (0, -4.4, -6.0))
    m.cube("magazine", "black", -1.5, -5.4, -7.8, 1.5, -4.4, -1.6)
    for i in range(3):
        y1 = -4.4 - 1.9 * i
        zc = -4.7 - i * 0.2
        m.cube("magazine", "poly" if i % 2 else "black", -1.5, y1 - 1.9, zc - 3.0, 1.5, y1, zc + 3.0)
    m.cube("magazine", "steel", -1.55, -10.4, -8.1, 1.55, -10.0, -1.9)
    m.cube("magazine", "brass", -0.7, -4.5, -6.6, 0.7, -4.3, -2.6)

    m.muzzle_flash(-31.8)
    m.casing(-2.0, 1.0, -1.2)
    m.hand_left(-5.0, -14.0)
    m.hand_right(-6.9, 6.4, -4.0)

    cfg = dict(
        name=ID, hand_l=(-5.0, -14.0), mag_grip=(-8.8, -4.8), mag_drop=8.0, mag_rock=12,
        charge_hand="right", handle=(-3.9, 1.1, -1.2), bolt_travel=6.5, hold_open=True,
        release_mode="handle",
        fire_len=0.3, cycle=0.11, kick_z=2.6, kick_pitch=3.8, kick_yaw=0.9, flash=1.2,
        reload_len=2.2, charge_len=0.95, release_len=0.7, eject=(-1.0, 1.0, 0.9),
        sight=(4.6, -5.7), butt=20.2,
    )
    return m, cfg
