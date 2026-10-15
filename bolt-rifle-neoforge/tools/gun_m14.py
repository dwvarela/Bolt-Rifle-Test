"""M14 EBR: aluminium chassis with rails, telescoping stock, compact scope, 20-round magazine."""
from gunlib import Model

ID = "m14ebr"


def build():
    m = Model(ID, seed=31)
    m.bone("chassis", "rifle", (0, 0, 0))
    m.bone("barrel", "rifle", (0, 0, 0))
    m.bone("receiver", "rifle", (0, 0, 0))
    m.bone("scope", "rifle", (0, 4.6, -4))

    # ---------------------------------------------------------------- barrel, flash hider, gas cylinder
    m.bar("barrel", "steel", 0, 0, -35.6, -8.0, 0.8, fine=True)
    m.bar("barrel", "black", 0, 0, -36.8, -34.4, 0.95, fine=True)                       # flash hider
    for i in range(4):
        m.cube("barrel", "steel", -1.1, -0.1, -36.5 + i * 0.5, 1.1, 0.1, -36.3 + i * 0.5)
        m.cube("barrel", "steel", -0.1, -1.1, -36.5 + i * 0.5, 0.1, 1.1, -36.3 + i * 0.5)
    m.cube("barrel", "black", -0.35, -0.35, -36.83, 0.35, 0.35, -36.75)
    m.bar("barrel", "gunmetal", 0, -1.25, -28.0, -14.0, 0.55)                            # gas cylinder
    m.cube("barrel", "gunmetal", -0.7, -1.9, -29.0, 0.7, -0.7, -27.4)                    # gas lock / bayonet lug
    m.cube("barrel", "steel", -0.7, -0.7, -14.8, 0.7, 0.7, -13.8)

    # ---------------------------------------------------------------- aluminium chassis
    m.rbox("chassis", "poly", -1.4, -2.3, -30.0, 1.4, 1.5, -8.4, c=0.6)                 # forend
    m.cube("chassis", "gunmetal", -0.6, 1.5, -30.0, 0.6, 2.0, -8.4)                       # top rail
    for z in [-29.6 + 1.0 * i for i in range(22)]:
        m.cube("chassis", "black", -0.65, 1.95, z, 0.65, 2.2, z + 0.45)
    for z0, z1 in ((-25.0, -21.0), (-14.6, -10.6)):                                        # side rails + bottom rail
        m.cube("chassis", "gunmetal", -1.65, -0.4, z0, -1.25, 0.5, z1)
        m.cube("chassis", "gunmetal", 1.25, -0.4, z0, 1.65, 0.5, z1)
    m.cube("chassis", "gunmetal", -0.45, -2.7, -24.0, 0.45, -2.2, -19.0)
    m.cube("chassis", "black", -0.5, -2.75, -23.4, 0.5, -2.65, -19.6)
    for yy in (-1.4, -0.4, 0.6):                                                           # M-LOK style slots
        m.cube("chassis", "black", -1.27, yy, -19.0, -1.2, yy + 0.35, -15.6)
        m.cube("chassis", "black", 1.2, yy, -19.0, 1.27, yy + 0.35, -15.6)
    m.rbox("chassis", "poly", -1.3, -3.7, -8.4, 1.3, 1.2, 3.4, c=0.45)                   # receiver cradle
    m.slope("chassis", "poly", -0.95, 0.95, -9.4, -2.6, 2.6, 6.0, 15)                     # pistol grip
    m.cube("chassis", "rubber", -0.98, -9.8, 3.6, 0.98, -9.4, 7.2)
    m.cube("chassis", "gunmetal", -0.3, -9.3, 4.4, 0.3, -2.8, 4.9)
    m.rbox("chassis", "poly", -1.2, -3.2, 3.2, 1.2, 1.0, 8.0, c=0.4)
    m.bar("chassis", "poly", 0, -0.8, 7.8, 12.4, 1.1, fine=True)                           # buffer-style tube
    m.slope("chassis", "poly", -0.9, 0.9, 0.2, 2.5, 9.0, 18.0, -2)                       # cheek riser
    for i in range(10):                                                                    # stock body
        z = 12.2 + i * 1.02
        m.cube("chassis", "poly", -1.0, -3.0 - i * 0.30, z, 1.0, 1.0 - i * 0.02, z + 1.04, flat=True)
    m.cube("chassis", "rubber", -1.05, -6.0, 22.0, 1.05, 0.8, 22.9)
    m.cube("chassis", "gunmetal", -0.5, -3.7, 11.4, 0.5, -3.2, 15.2)                       # adjustment lever
    m.cube("chassis", "steel", -0.2, -4.4, 6.0, 0.2, -3.8, 6.6)

    # vertical foregrip + folded bipod + sling mount (Mk14 look)
    m.rbox("chassis", "poly", -0.75, -8.4, -21.0, 0.75, -2.6, -18.4, c=0.3)
    for i in range(4):
        m.cube("chassis", "black", -0.78, -7.6 + i * 1.1, -20.9, 0.78, -7.4 + i * 1.1, -18.5)
    m.cube("chassis", "rubber", -0.78, -8.6, -21.1, 0.78, -8.3, -18.3)
    m.cube("chassis", "gunmetal", -1.0, -3.2, -29.0, 1.0, -2.6, -27.0)                      # bipod mount
    for sx in (-0.7, 0.7):
        m.cube("chassis", "steel", sx - 0.22, -3.6, -28.6, sx + 0.22, -3.1, -22.0)         # folded legs
    m.cube("chassis", "steel", -0.4, -3.0, -11.2, 0.4, -2.3, -10.4)                         # QD sling socket
    # ---------------------------------------------------------------- receiver group
    m.rbox("receiver", "steel", -1.0, -0.8, -8.2, 1.0, 1.7, 6.8, c=0.3)
    m.cube("receiver", "black", -1.03, 0.2, -3.6, -0.92, 1.5, 3.0)                         # ejection port
    m.cube("receiver", "steel", -0.25, -5.1, -0.4, 0.25, -4.55, 4.2)                       # trigger guard
    m.cube("receiver", "steel", -0.25, -5.1, -0.4, 0.25, -3.4, 0.05)
    m.cube("receiver", "steel", -0.25, -5.1, 3.7, 0.25, -3.4, 4.2)
    m.slope("receiver", "black", -0.2, 0.2, -4.2, -2.3, 1.4, 1.9, -9)                      # trigger
    m.cube("receiver", "steel", -0.7, -3.4, 2.4, 0.7, -3.15, 3.5)                          # safety
    m.rbox("receiver", "gunmetal", -1.0, -4.6, -5.4, 1.0, -2.2, 0.2, c=0.3)                # magwell

    m.bone("bolt", "rifle", (0, 0, 0))
    m.cube("bolt", "stainless", -0.99, 0.3, -3.4, -0.9, 1.4, 1.6)
    m.cube("bolt", "steel", -0.88, 0.7, 1.6, 0.88, 1.7, 5.0)
    m.cube("bolt", "steel", -1.95, -0.1, -29.0, -1.35, 0.5, -9.0)                           # op rod running to the gas piston
    m.cube("bolt", "gunmetal", -1.8, -0.35, -9.4, -1.1, 0.7, -3.5)
    m.bone("bolt_handle", "bolt", (-1.0, 1.0, -1.0))
    m.cube("bolt_handle", "steel", -2.0, 0.55, -1.5, -0.9, 1.35, -0.5)
    m.cube("bolt_handle", "steel", -2.6, 0.2, -1.9, -1.9, 1.7, -0.1)
    m.cube("bolt_handle", "black", -2.9, 0.1, -2.0, -2.55, 1.8, 0.0)
    m.hand_bolt("bolt_handle", -2.7, 1.0, -1.0)

    # ---------------------------------------------------------------- compact scope; eyepiece ends at z = 8
    m.cube("scope", "gunmetal", -0.9, 1.7, -9.6, 0.9, 2.5, 0.8)                            # mount base
    m.rbox("scope", "scope", -1.2, 1.7, -9.4, 1.2, 5.7, -8.0, c=0.4)                       # rings
    m.rbox("scope", "scope", -1.2, 1.7, -1.2, 1.2, 5.7, 0.2, c=0.4)
    m.bar("scope", "scope", 0, 4.6, -12.2, 4.4, 1.05, fine=True)                           # main tube
    m.bar("scope", "scope", 0, 4.6, -15.4, -12.2, 1.6, fine=True)                          # objective bell
    m.bar("scope", "scope", 0, 4.6, 4.4, 8.0, 1.3, fine=True)                              # eyepiece
    m.cube("scope", "lens", -1.45, 3.15, -15.44, 1.45, 6.05, -15.4)
    m.cube("scope", "lens", -0.95, 3.65, 7.98, 0.95, 5.55, 8.02)
    m.rbox("scope", "scope", -0.55, 5.6, -6.0, 0.55, 6.6, -4.8, c=0.15)                    # elevation turret
    m.cube("scope", "stainless", -0.4, 6.6, -5.8, 0.4, 6.9, -5.0)
    m.rbox("scope", "scope", -1.9, 4.1, -6.0, -1.0, 5.1, -4.8, c=0.15)                     # windage turret
    m.cube("scope", "stainless", -0.9, 4.0, 4.0, 0.9, 5.2, 4.4)                            # power ring

    # ---------------------------------------------------------------- 20-round magazine
    m.bone("magazine", "rifle", (0, -2.4, -2.5))
    ey, ez, ang = m.chain("magazine", "black", -0.98, 0.98, -2.3, -2.6, 1.55, 4.0, 7, 8)
    m.cube("magazine", "steel", -1.02, ey - 0.3, ez - 2.1, 1.02, ey + 0.1, ez + 2.1, rot=[-ang, 0, 0], pivot=[0, ey, ez])
    m.cube("magazine", "brass", -0.5, -2.35, -4.6, 0.5, -2.15, -1.2)
    m.cube("magazine", "steel", -1.03, -6.2, -4.5, 1.03, -6.05, -0.5)
    m.cube("magazine", "steel", -1.03, -9.0, -4.8, 1.03, -8.85, -0.9)

    m.muzzle_flash(-37.0, length=5.5, width=3.6)
    m.casing(-1.0, 1.0, -0.4)
    m.hand_left(-3.8, -15.5)
    m.hand_right(-6.4, 5.2, -3.2)

    cfg = dict(
        name=ID, hand_l=(-3.8, -15.5), mag_grip=(-8.6, -3.6), mag_drop=9.0, mag_rock=10,
        charge_hand="right", handle=(-2.7, 1.0, -1.0), bolt_travel=6.5, hold_open=True,
        release_mode="handle",
        fire_len=0.32, cycle=0.12, kick_z=2.8, kick_pitch=4.0, kick_yaw=0.8, flash=1.25,
        reload_len=2.3, charge_len=0.95, release_len=0.7, eject=(-1.0, 1.0, 0.9),
        sight=(4.6, 8.0), butt=22.9,
    )
    return m, cfg
