"""AK-47 (Type 3, wood furniture): slim stamped receiver, curved magazine, ladder rear sight."""
from gunlib import Model

ID = "ak47"


def build():
    m = Model(ID, seed=11)
    m.bone("wood", "rifle", (0, 0, 0))
    m.bone("barrel", "rifle", (0, 0, 0))
    m.bone("receiver", "rifle", (0, 0, 0))

    # ---------------------------------------------------------------- barrel group
    m.bar("barrel", "steel", 0, 0, -27.0, -7.0, 0.62, fine=True)
    m.bar("barrel", "black", 0, 0, -27.7, -26.4, 0.9)                           # muzzle nut
    m.cube("barrel", "black", -0.3, -0.3, -27.72, 0.3, 0.3, -27.6)             # bore
    m.cube("barrel", "steel", -0.95, -0.15, -26.8, 0.95, 0.15, -26.6)          # nut groove
    # front sight base + post + hood
    m.rbox("barrel", "gunmetal", -0.7, 0.3, -25.8, 0.7, 2.0, -22.8, c=0.25)
    m.cube("barrel", "steel", -0.2, 2.0, -24.9, 0.2, 3.35, -24.5)
    m.cube("barrel", "gunmetal", -1.0, 1.7, -25.6, -0.75, 3.9, -23.6)           # hood sides
    m.cube("barrel", "gunmetal", 0.75, 1.7, -25.6, 1.0, 3.9, -23.6)
    m.cube("barrel", "gunmetal", -1.0, 3.65, -25.6, 1.0, 3.9, -23.6)
    # gas block + tube
    m.rbox("barrel", "gunmetal", -0.85, -0.9, -19.6, 0.85, 1.9, -16.4, c=0.3)
    m.cube("barrel", "steel", -0.9, -0.5, -17.6, 0.9, 0.5, -17.3)              # block collar
    m.bar("barrel", "steel", 0, 1.45, -16.6, -8.0, 0.6)                         # gas tube
    m.cube("barrel", "steel", -0.2, -1.2, -24.0, 0.2, -0.5, -17.8)              # cleaning rod
    m.cube("barrel", "steel", -0.35, -1.45, -20.6, 0.35, -0.9, -20.1)
    m.cube("barrel", "steel", -0.3, -1.5, -18.4, 0.3, -0.9, -17.9)

    # ---------------------------------------------------------------- wood furniture
    m.rbox("wood", "plum", -1.2, 0.5, -15.0, 1.2, 2.3, -7.4, c=0.45)            # upper handguard
    for z in (-14.2, -13.4, -12.6, -11.8):
        m.cube("wood", "wood", -1.22, 1.9, z, 1.22, 2.0, z + 0.25)
    m.rbox("wood", "plum", -1.3, -2.7, -17.4, 1.3, 0.7, -7.2, c=0.5)            # lower handguard
    m.rbox("wood", "plum", -1.05, -2.2, -18.8, 1.05, 0.2, -17.4, c=0.45)        # tapered nose
    m.cube("wood", "gunmetal", -1.34, -2.8, -17.3, 1.34, 0.8, -17.0)             # front ferrule
    m.cube("wood", "gunmetal", -1.34, -2.9, -9.9, 1.34, 0.7, -9.6)               # rear ferrule
    m.cube("wood", "black", -0.5, -2.82, -14.0, 0.5, -2.7, -10.0)                # heat-vent shadow
    # pistol grip: raked 17 degrees, slim
    m.slope("wood", "plum", -0.9, 0.9, -9.2, -1.9, 2.9, 6.1, 17)
    m.cube("wood", "rubber", -0.95, -9.9, 4.6, 0.95, -9.4, 8.2)
    m.cube("wood", "gunmetal", -0.3, -9.6, 5.4, 0.3, -2.6, 5.9)                  # grip screw
    # stock: buttstock steps down smoothly
    zs = [9.4 + 0.8 * i for i in range(13)]
    for i, z in enumerate(zs):
        top = 2.0 - i * 0.045
        bot = -3.0 - i * 0.43
        m.cube("wood", "plum", -0.95 - i * 0.004, bot, z, 0.95 + i * 0.004, top, z + 0.82, flat=True)
    m.cube("wood", "black", -1.0, -8.65, 19.1, 1.0, 1.4, 19.9)                   # butt plate
    m.cube("wood", "steel", -0.7, 1.4, 19.9, 0.7, 1.6, 19.95)
    m.cube("wood", "gunmetal", -0.8, 1.9, 9.4, 0.8, 2.3, 11.0)                   # stock screw plate
    m.cube("wood", "steel", -0.2, -3.9, 15.0, 0.2, -3.3, 15.6)                    # sling loop

    # ---------------------------------------------------------------- stamped receiver
    m.rbox("receiver", "gunmetal", -0.95, -2.3, -7.6, 0.95, 2.1, 9.6, c=0.3)
    m.rbox("receiver", "gunmetal", -0.9, 2.0, -5.4, 0.9, 2.9, 8.3, c=0.35)       # dust cover
    m.cube("receiver", "steel", -0.15, 2.9, -3.8, 0.15, 3.15, 7.4)              # cover rib
    m.cube("receiver", "gunmetal", -0.9, 2.1, 8.0, 0.9, 2.6, 9.8)
    for z in (-4.6, -2.0, 0.6, 3.2, 5.8):                                         # stamped ribs
        m.cube("receiver", "steel", -0.97, -1.8, z, 0.97, -1.6, z + 0.25)
    m.cube("receiver", "black", -1.0, 0.1, -4.9, -0.9, 1.7, 1.9)                 # ejection port (right)
    m.cube("receiver", "steel", -1.0, -0.9, 0.3, -0.92, -0.3, 2.6)               # selector detent
    m.slope("receiver", "steel", -1.55, -0.95, -0.35, 1.25, -0.5, 1.3, -12)      # selector lever
    # trunnion block + ladder rear sight
    m.rbox("receiver", "gunmetal", -1.0, -1.0, -8.6, 1.0, 2.3, -5.0, c=0.3)
    m.cube("receiver", "gunmetal", -0.9, 2.2, -9.0, 0.9, 2.7, -5.6)
    m.slope("receiver", "steel", -0.7, 0.7, 2.7, 3.1, -9.0, -4.8, 6)             # ladder leaf (rises to the rear)
    m.cube("receiver", "gunmetal", -0.75, 3.0, -6.1, -0.28, 3.65, -5.4)          # notch (right)
    m.cube("receiver", "gunmetal", 0.28, 3.0, -6.1, 0.75, 3.65, -5.4)
    m.cube("receiver", "steel", -0.5, 2.6, -8.2, 0.5, 2.8, -7.6)
    # magwell + trigger group
    m.rbox("receiver", "gunmetal", -0.95, -4.7, -6.9, 0.95, -2.2, -1.2, c=0.3)
    m.cube("receiver", "steel", -0.96, -4.3, -7.3, 0.96, -3.5, -6.8)             # mag catch hook
    m.cube("receiver", "steel", -0.25, -4.8, -1.0, 0.25, -4.25, 3.7)             # trigger guard bottom
    m.cube("receiver", "steel", -0.25, -4.8, -1.0, 0.25, -2.4, -0.55)
    m.cube("receiver", "steel", -0.25, -4.8, 3.2, 0.25, -2.4, 3.7)
    m.slope("receiver", "black", -0.2, 0.2, -4.2, -2.4, 1.0, 1.55, -10)           # trigger
    m.cube("receiver", "steel", -0.9, -2.45, 2.2, 0.9, -2.3, 4.0)

    # ---------------------------------------------------------------- bolt carrier + charging handle
    m.bone("bolt", "rifle", (0, 0, 0))
    m.cube("bolt", "stainless", -0.98, 0.25, -4.2, -0.9, 1.5, 0.6)               # carrier seen in the port
    m.cube("bolt", "steel", -0.88, 0.8, 0.6, 0.88, 2.0, 3.8)
    m.bone("bolt_handle", "bolt", (-1.0, 1.0, -1.0))
    m.cube("bolt_handle", "steel", -2.1, 0.55, -1.5, -0.9, 1.3, -0.5)
    m.cube("bolt_handle", "steel", -2.8, 0.1, -1.9, -2.0, 1.8, -0.1)             # knob (flat paddle)
    m.cube("bolt_handle", "black", -3.0, 0.0, -2.0, -2.75, 1.9, 0.0)
    m.hand_bolt("bolt_handle", -2.8, 1.0, -1.0)

    # ---------------------------------------------------------------- curved 30-round magazine
    m.bone("magazine", "rifle", (0, -2.6, -5.2))
    ey, ez, ang = m.chain("magazine", "black", -0.92, 0.92, -2.5, -3.8, 1.5, 3.6, 10, 42, thick_taper=0.0)
    m.cube("magazine", "steel", -1.0, ey - 0.2, ez - 2.0, 1.0, ey + 0.1, ez + 2.0, rot=[-ang, 0, 0], pivot=[0, ey, ez])
    m.cube("magazine", "brass", -0.5, -2.65, -5.3, 0.5, -2.45, -2.2)             # top round
    m.cube("magazine", "steel", -0.96, -3.0, -6.2, 0.96, -2.6, -5.7)              # front lug

    m.muzzle_flash(-27.9)
    m.casing(-1.0, 0.9, -1.0)
    m.hand_left(-4.6, -12.5)
    m.hand_right(-6.2, 5.2, -3.6)

    cfg = dict(
        name=ID, hand_l=(-4.6, -12.5), mag_grip=(-10.0, -7.4), mag_drop=9.0, mag_rock=17,
        charge_hand="right", handle=(-2.8, 1.0, -1.0), bolt_travel=7.0, hold_open=False,
        fire_len=0.28, cycle=0.10, kick_z=2.3, kick_pitch=3.2, kick_yaw=0.8, flash=1.1,
        reload_len=2.3, charge_len=0.95, release_len=0.0, eject=(-1.0, 1.0, 0.9),
        sight=(3.35, -5.7), butt=19.9,
    )
    return m, cfg
