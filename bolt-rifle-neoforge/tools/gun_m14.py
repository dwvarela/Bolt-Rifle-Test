"""M14 EBR (modular chassis, adjustable stock, compact scope): model + animation config."""
from gunlib import Model

ID = "m14ebr"


def build():
    m = Model(ID, seed=31)
    m.bone("chassis", "rifle", (0, 0, 0))
    m.bone("barrel", "rifle", (0, 0, 0))
    m.bone("receiver", "rifle", (0, 0, 0))
    m.bone("scope", "rifle", (0, 4.6, -4))

    # ---- barrel + flash hider
    m.bar("barrel", "steel", 0, 0, -36.0, -8.0, 0.95)
    m.bar("barrel", "black", 0, 0, -37.2, -34.6, 1.25)                        # flash hider
    for z in (-36.8, -35.6):
        m.cube("barrel", "steel", -1.3, -0.15, z - 0.2, 1.3, 0.15, z + 0.2)
    m.cube("barrel", "black", -0.5, -0.5, -37.25, 0.5, 0.5, -37.15)
    m.cube("barrel", "gunmetal", -1.4, -1.4, -30.0, 1.4, 1.4, -28.0)           # gas block
    m.cube("barrel", "gunmetal", -0.4, -1.8, -29.8, 0.4, -1.4, -28.2)

    # ---- aluminium chassis: forend with rails, pistol grip, folding-style stock
    m.cube("chassis", "poly", -1.9, -2.6, -27.0, 1.9, 1.8, -8.0)               # forend
    m.cube("chassis", "gunmetal", -0.8, 1.8, -27.0, 0.8, 2.3, -8.0)            # top rail
    for z in range(-26, -9, 2):
        m.cube("chassis", "black", -0.9, 2.2, z, 0.9, 2.5, z + 1.0)
    m.cube("chassis", "gunmetal", -2.3, -1.4, -26.0, -1.9, 0.6, -9.0)          # side rail (right)
    m.cube("chassis", "gunmetal", 1.9, -1.4, -26.0, 2.3, 0.6, -9.0)
    m.cube("chassis", "poly", -1.5, -3.2, -20.0, 1.5, -2.6, -9.0)              # forend underside
    m.cube("chassis", "poly", -1.7, -4.6, 3.0, 1.7, -2.4, 7.0)                 # grip top
    m.cube("chassis", "poly", -1.7, -7.2, 3.6, 1.7, -4.6, 7.6)
    m.cube("chassis", "poly", -1.7, -9.8, 4.2, 1.7, -7.2, 8.2)
    m.cube("chassis", "rubber", -1.75, -10.1, 4.1, 1.75, -9.8, 8.3)
    m.cube("chassis", "poly", -2.0, -4.6, -8.0, 2.0, -0.8, 7.0)                # chassis body
    m.cube("chassis", "poly", -1.5, -4.0, 7.0, 1.5, 1.0, 11.0)                 # stock tube
    m.cube("chassis", "poly", -1.6, 1.0, 9.0, 1.6, 2.6, 18.0)                  # cheek riser
    m.cube("chassis", "poly", -1.7, -7.0, 11.0, 1.7, 1.0, 14.0)
    m.cube("chassis", "poly", -1.8, -8.4, 14.0, 1.8, 1.0, 21.0)
    m.cube("chassis", "rubber", -1.9, -8.8, 21.0, 1.9, 0.8, 22.4)              # butt pad
    m.cube("chassis", "gunmetal", -1.0, -3.6, 11.0, 1.0, -3.0, 14.0)           # adjustment lever

    # ---- receiver (steel), trigger group, safety
    m.cube("receiver", "steel", -1.7, -0.6, -8.0, 1.7, 2.0, 7.0)
    m.cube("receiver", "black", -1.8, 0.2, -3.4, -1.66, 1.8, 3.0)              # ejection port
    m.cube("receiver", "steel", -0.5, -6.4, -0.6, 0.5, -5.8, 4.4)              # trigger guard
    m.cube("receiver", "steel", -0.5, -6.4, -0.6, 0.5, -4.6, 0.0)
    m.cube("receiver", "steel", -0.5, -6.4, 3.8, 0.5, -4.6, 4.4)
    m.cube("receiver", "black", -0.3, -5.6, 1.4, 0.3, -3.6, 2.0)
    m.cube("receiver", "steel", -0.9, -4.4, 2.2, 0.9, -3.9, 3.6)
    m.cube("receiver", "gunmetal", -1.5, -4.4, -5.0, 1.5, -2.4, 0.0)           # magwell

    # ---- bolt / op-rod handle
    m.bone("bolt", "rifle", (0, 0, 0))
    m.cube("bolt", "stainless", -1.79, 0.4, -3.0, -1.7, 1.6, 1.4)
    m.cube("bolt", "steel", -1.6, 0.9, 1.4, 1.6, 1.9, 5.0)
    m.bone("bolt_handle", "bolt", (-2.0, 1.2, -1.0))
    m.cube("bolt_handle", "steel", -3.4, 0.6, -1.6, -1.7, 1.8, -0.2)
    m.cube("bolt_handle", "black", -4.4, 0.0, -2.0, -3.2, 2.4, 0.2)
    m.hand_bolt("bolt_handle", -3.8, 1.2, -1.0)

    # ---- compact scope (3-9x), eyepiece ends at z = 8 like the M700's so the aim position matches
    m.cube("scope", "black", -1.7, 2.0, -10.5, 1.7, 4.0, -8.9)
    m.cube("scope", "black", -1.7, 2.0, -1.0, 1.7, 4.0, 0.6)
    m.bar("scope", "scope", 0, 4.6, -11.5, 4.0, 1.4)
    m.bar("scope", "scope", 0, 4.6, -15.0, -11.5, 2.0)
    m.bar("scope", "scope", 0, 4.6, 4.0, 8.0, 1.7)
    m.cube("scope", "lens", -1.7, 3.0, -15.08, 1.7, 6.2, -14.98)
    m.cube("scope", "lens", -1.3, 3.3, 7.98, 1.3, 5.9, 8.08)
    m.cube("scope", "scope", -0.9, 6.0, -6.6, 0.9, 7.0, -4.8)
    m.cube("scope", "stainless", -0.6, 7.0, -6.3, 0.6, 7.4, -5.1)
    m.cube("scope", "scope", -2.9, 4.0, -6.6, -1.4, 5.1, -4.8)
    m.cube("scope", "stainless", -1.4, 4.1, 3.8, 1.4, 5.1, 4.2)

    # ---- 20-round magazine
    m.bone("magazine", "rifle", (0, -2.4, -2.5))
    m.cube("magazine", "black", -1.4, -13.2, -5.0, 1.4, -2.4, 0.0)
    m.cube("magazine", "steel", -1.45, -13.8, -5.1, 1.45, -13.2, 0.1)
    for y in (-6.0, -8.6, -11.2):
        m.cube("magazine", "steel", -1.45, y, -5.1, 1.45, y + 0.2, 0.1)
    m.cube("magazine", "brass", -0.7, -2.5, -4.2, 0.7, -2.3, -0.8)

    m.muzzle_flash(-37.4, length=5.5, width=3.6)
    m.casing(-1.8, 1.0, -0.4)
    m.hand_left(-4.4, -15.0)
    m.hand_right(-7.0, 6.0, -4.2)

    cfg = dict(
        name=ID, hand_l=(-4.4, -15.0), mag_grip=(-10.5, -2.6), mag_drop=9.0, mag_rock=10,
        charge_hand="right", handle=(-3.8, 1.2, -1.0), bolt_travel=6.5, hold_open=True,
        release_mode="handle",
        fire_len=0.32, cycle=0.12, kick_z=2.8, kick_pitch=4.0, kick_yaw=0.8, flash=1.25,
        reload_len=2.3, charge_len=0.95, release_len=0.7, eject=(-1.0, 1.0, 0.9),
        sight=(4.6, 8.0), butt=22.4,
    )
    return m, cfg
