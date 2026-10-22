"""SKS carbine: slim milled receiver, full wood stock, hooded front sight, folded spike bayonet."""
from gunlib import Model

ID = "sks"


def build():
    m = Model(ID, seed=21)
    m.bone("wood", "rifle", (0, 0, 0))
    m.bone("barrel", "rifle", (0, 0, 0))
    m.bone("receiver", "rifle", (0, 0, 0))

    # ---------------------------------------------------------------- barrel group
    m.bar("barrel", "steel", 0, 0, -31.2, -9.0, 0.62, fine=True)
    m.bar("barrel", "black", 0, 0, -31.9, -30.6, 0.85)
    m.cube("barrel", "black", -0.3, -0.3, -31.92, 0.3, 0.3, -31.8)
    m.cube("barrel", "steel", -0.9, -0.12, -31.0, 0.9, 0.12, -30.8)
    m.rbox("barrel", "gunmetal", -0.7, 0.3, -30.0, 0.7, 2.0, -27.0, c=0.25)       # sight base
    m.cube("barrel", "steel", -0.2, 2.0, -29.1, 0.2, 3.3, -28.7)                   # post
    m.cube("barrel", "gunmetal", -0.98, 1.7, -29.8, -0.74, 3.8, -27.8)             # hood
    m.cube("barrel", "gunmetal", 0.74, 1.7, -29.8, 0.98, 3.8, -27.8)
    m.cube("barrel", "gunmetal", -0.98, 3.56, -29.8, 0.98, 3.8, -27.8)
    m.rbox("barrel", "gunmetal", -0.8, -0.8, -23.4, 0.8, 1.7, -20.4, c=0.3)        # gas block
    m.bar("barrel", "steel", 0, 1.35, -20.4, -9.6, 0.55)                            # gas tube
    m.cube("barrel", "steel", -0.25, -1.3, -29.8, 0.25, -0.8, -14.6)                # folded bayonet
    m.cube("barrel", "steel", -0.45, -1.6, -14.8, 0.45, -0.8, -14.0)                # pivot lug
    m.cube("barrel", "steel", -0.2, -1.1, -22.0, 0.2, -0.6, -21.4)

    # ---------------------------------------------------------------- wood
    m.rbox("wood", "wood", -1.25, -2.8, -21.6, 1.25, 0.7, -8.0, c=0.5)             # forend
    m.rbox("wood", "wood", -1.0, -2.3, -23.2, 1.0, 0.3, -21.6, c=0.4)
    m.cube("wood", "steel", -1.3, -3.0, -22.4, 1.3, 0.8, -21.8)                     # nose cap
    m.cube("wood", "steel", -0.2, 0.7, -22.4, 0.2, 1.5, -22.0)                      # bayonet lug
    m.rbox("wood", "plum", -1.1, 0.6, -17.4, 1.1, 2.3, -9.4, c=0.45)               # top handguard
    m.cube("wood", "steel", -1.14, 0.55, -17.5, 1.14, 2.35, -17.2)
    for z in (-16.4, -15.6, -14.8, -14.0):
        m.cube("wood", "wood", -1.12, 2.0, z, 1.12, 2.1, z + 0.25)
    m.rbox("wood", "wood", -1.35, -3.5, -8.0, 1.35, 0.2, 3.6, c=0.5)                # stock under receiver
    m.slope("wood", "wood", -1.05, 1.05, -6.4, 0.2, 3.0, 6.9, 14)                    # wrist / grip swell
    for i in range(15):
        z = 6.4 + i * 0.92
        top = 1.2 - i * 0.05
        bot = -4.3 - i * 0.24
        m.cube("wood", "wood", -1.0 - i * 0.005, bot, z, 1.0 + i * 0.005, top, z + 0.94, flat=True)
    m.cube("wood", "steel", -1.05, -8.4, 19.9, 1.05, 0.5, 20.6)                     # butt plate
    m.cube("wood", "stainless", -0.6, -2.2, 20.0, 0.6, -1.4, 20.65)                  # trap door
    m.cube("wood", "steel", -0.2, -5.4, 12.0, 0.2, -4.8, 12.6)                      # sling loop

    # ---------------------------------------------------------------- receiver
    m.rbox("receiver", "gunmetal", -1.0, -1.6, -8.4, 1.0, 2.0, 6.8, c=0.3)
    m.rbox("receiver", "gunmetal", -0.9, 1.9, -3.8, 0.9, 2.7, 6.9, c=0.35)          # dust cover
    m.cube("receiver", "steel", -0.15, 2.7, -3.0, 0.15, 2.95, 6.4)
    m.cube("receiver", "black", -1.02, 0.1, -4.8, -0.92, 1.6, 1.8)                  # ejection port
    m.cube("receiver", "steel", -1.0, -0.6, -8.4, 1.0, -0.4, 6.8)                   # seam
    m.rbox("receiver", "gunmetal", -1.0, 1.9, -10.0, 1.0, 3.0, -4.6, c=0.3)          # rear-sight base
    m.slope("receiver", "steel", -0.7, 0.7, 2.9, 3.25, -10.0, -5.4, 5)
    m.cube("receiver", "gunmetal", -0.75, 3.0, -7.3, -0.28, 3.65, -6.6)              # notch
    m.cube("receiver", "gunmetal", 0.28, 3.0, -7.3, 0.75, 3.65, -6.6)
    m.cube("receiver", "steel", -0.25, -4.6, -0.8, 0.25, -4.05, 3.6)                 # trigger guard
    m.cube("receiver", "steel", -0.25, -4.6, -0.8, 0.25, -1.6, -0.4)
    m.cube("receiver", "steel", -0.25, -4.6, 3.2, 0.25, -1.6, 3.6)
    m.slope("receiver", "black", -0.2, 0.2, -4.0, -1.8, 1.0, 1.55, -10)
    m.cube("receiver", "steel", -0.7, -4.15, 1.9, 0.7, -3.9, 3.0)                    # safety

    # ---------------------------------------------------------------- bolt carrier + handle (right)
    m.bone("bolt", "rifle", (0, 0, 0))
    m.cube("bolt", "stainless", -0.99, 0.3, -4.4, -0.9, 1.5, 0.9)
    m.cube("bolt", "steel", -0.88, 0.8, 0.9, 0.88, 1.9, 4.2)
    m.bone("bolt_handle", "bolt", (-1.0, 1.0, -1.2))
    m.cube("bolt_handle", "steel", -2.0, 0.55, -1.7, -0.9, 1.35, -0.7)
    m.cube("bolt_handle", "steel", -2.6, 0.2, -2.1, -1.9, 1.7, -0.3)
    m.cube("bolt_handle", "black", -2.9, 0.1, -2.2, -2.55, 1.8, -0.2)

    # ---------------------------------------------------------------- detachable 10-round box magazine
    m.bone("magazine", "rifle", (0, -4.4, -6.0))
    m.slope("magazine", "black", -1.0, 1.0, -9.8, -4.0, -8.2, -2.4, -4)
    m.cube("magazine", "steel", -1.02, -10.1, -8.5, 1.02, -9.7, -2.2)                # floor plate
    for y in (-5.6, -7.0, -8.4):
        m.cube("magazine", "steel", -1.02, y, -7.9, 1.02, y + 0.14, -2.6)
    m.cube("magazine", "brass", -0.5, -4.5, -6.9, 0.5, -4.3, -3.2)

    m.muzzle_flash(-32.1)
    m.casing(-1.0, 1.0, -1.2)
    m.hand_left(-4.6, -14.0)
    m.hand_right(-6.2, 6.0, -3.6)

    cfg = dict(
        name=ID, hand_l=(-4.6, -14.0), mag_grip=(-8.4, -5.0), mag_drop=8.0, mag_rock=12,
        charge_hand="right", hand_r=(-6.2, 6.0), handle=(-2.7, 1.0, -1.2), bolt_travel=6.5, hold_open=True,
        release_mode="handle",
        fire_len=0.3, cycle=0.11, kick_z=2.6, kick_pitch=3.8, kick_yaw=0.9, flash=1.2,
        reload_len=2.2, charge_len=0.95, release_len=0.7, eject=(-1.0, 1.0, 0.9),
        sight=(3.35, -6.9), butt=20.6,
    )
    return m, cfg
