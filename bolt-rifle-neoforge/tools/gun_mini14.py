"""Ruger Mini-14 (.223): blued steel receiver, walnut stock with ventilated top-railed handguard,
raked synthetic pistol grip, side-folding skeleton stock, ghost-ring rear, ear-guarded front blade, 20-round box mag."""
import math
from gunlib import Model

ID = "mini14"
SY = 3.3          # sight line height above the bore
RZ = 7.0          # rear aperture position


def build():
    m = Model(ID, seed=43)
    m.bone("body", "rifle", (0, 0, 0))
    m.bone("barrel", "rifle", (0, 0, 0))
    m.bone("receiver", "rifle", (0, 0, 0))
    MZ = -29.5

    # ---------------------------------------------------------------- barrel + flash hider + front sight
    m.bar("barrel", "steel", 0, 0, MZ + 2.4, -8.0, 0.52, fine=True)
    m.bar("barrel", "black", 0, 0, MZ, MZ + 2.8, 0.66, fine=True)                           # birdcage flash hider
    for i in range(3):
        m.cube("barrel", "steel", -0.82, -0.12, MZ + 0.35 + i * 0.7, 0.82, 0.12, MZ + 0.6 + i * 0.7)
        m.cube("barrel", "steel", -0.12, -0.82, MZ + 0.35 + i * 0.7, 0.12, 0.82, MZ + 0.6 + i * 0.7)
    m.cube("barrel", "black", -0.28, -0.28, MZ - 0.03, 0.28, 0.28, MZ + 0.05)
    fz = -24.5
    m.rbox("barrel", "black", -0.95, -0.95, fz - 1.3, 0.95, 0.95, fz + 1.3, c=0.3)         # sight base collar
    m.cube("barrel", "black", -0.45, 0.8, fz - 1.1, 0.45, 1.5, fz + 1.1)
    m.cube("barrel", "black", -0.18, 1.4, fz - 0.4, 0.18, SY + 0.1, fz + 0.3)               # blade
    m.cube("barrel", "stainless", -0.1, SY - 0.4, fz - 0.4, 0.1, SY + 0.1, fz - 0.36)        # blade face highlight
    for sx in (-1, 1):                                                                       # protective ears
        m.cube("barrel", "black", sx * 0.62 - 0.12, 1.0, fz - 0.9, sx * 0.62 + 0.12, SY - 0.2, fz + 0.9)
        m.cube("barrel", "black", sx * 0.42 - 0.2, 1.4, fz - 0.9, sx * 0.62 + 0.2, 1.6, fz + 0.9)
    m.cube("barrel", "black", -0.3, -1.2, fz + 1.3, 0.3, -0.9, fz + 2.2)                    # bayonet lug

    # ---------------------------------------------------------------- stock: forend, receiver bed, vented top handguard
    m.rbox("body", "walnut", -1.35, -2.4, -22.0, 1.35, 0.5, -5.8, c=0.5)                    # forend
    m.rbox("body", "walnut", -1.25, -3.5, -7.0, 1.25, 0.6, 8.6, c=0.45)                     # receiver bed / belly
    m.cube("body", "black", -1.2, -3.55, -6.4, 1.2, -3.35, -0.2)                            # mag cut
    m.rbox("body", "black", -1.3, 0.4, -22.3, 1.3, 1.25, -5.6, c=0.3)                       # ventilated heat-shield handguard
    m.cube("body", "gunmetal", -0.55, 1.2, -22.3, 0.55, 1.5, -5.6)                          # top rail base
    for z in [-21.8 + 0.9 * i for i in range(18)]:
        m.cube("body", "black", -0.6, 1.45, z, 0.6, 1.7, z + 0.42)                           # rail teeth
    for z in (-19.6, -17.0, -14.4):                                                         # vent slots
        m.cube("body", "walnut", -1.34, 0.55, z, -1.2, 1.1, z + 1.3)
        m.cube("body", "walnut", 1.2, 0.55, z, 1.34, 1.1, z + 1.3)
    m.cube("body", "gunmetal", -1.38, -2.3, -22.4, 1.38, -2.0, -21.7)                       # forend cap
    # sling loop on the forend nose
    m.cube("body", "stainless", -0.9, -3.6, -21.8, -0.6, -2.0, -21.4)
    m.cube("body", "stainless", 0.6, -3.6, -21.8, 0.9, -2.0, -21.4)
    m.cube("body", "stainless", -0.9, -3.9, -21.8, 0.9, -3.6, -21.4)
    # grip + hinge + folding skeleton stock
    m.slope("body", "rubber", -0.95, 0.95, -9.2, -3.0, 5.4, 8.6, 16)                        # raked pistol grip
    m.cube("body", "black", -0.98, -9.4, 6.0, 0.98, -9.2, 9.2)                             # grip cap
    for yy in (-5.0, -6.2, -7.4):
        m.cube("body", "rubber", -0.99, yy, 5.2, 0.99, yy + 0.15, 5.8)
    m.rbox("body", "black", -1.2, -2.4, 8.6, 1.2, 0.8, 12.2, c=0.35)                        # hinge block
    m.cube("body", "stainless", -1.28, -0.9, 9.6, -1.2, -0.2, 10.4)                         # hinge pin head
    m.bar("body", "steel", 0, -0.5, 12.0, 28.0, 0.5, fine=True)                             # stock tube
    m.cube("body", "black", -0.65, -1.7, 12.0, 0.65, -0.9, 14.0)                            # latch
    m.slope("body", "black", -1.25, 1.25, -6.6, 1.8, 27.8, 28.9, -6)                        # buttplate (angled)
    m.cube("body", "rubber", -1.27, -6.4, 28.8, 1.27, 1.6, 29.1)                            # pad
    m.cube("body", "black", -0.5, 1.7, 26.2, 0.5, 2.4, 28.6)                                # cheek wedge
    m.cube("body", "black", -0.3, -6.6, 27.0, 0.3, -5.9, 28.7)                              # toe
    # trigger group
    m.cube("body", "steel", -0.25, -4.7, 0.0, 0.25, -4.3, 4.6)
    m.cube("body", "steel", -0.25, -4.7, 0.0, 0.25, -2.0, 0.4)
    m.cube("body", "steel", -0.25, -4.7, 4.2, 0.25, -2.0, 4.6)
    m.slope("body", "black", -0.2, 0.2, -4.0, -2.3, 1.5, 2.2, -8)                           # trigger
    m.cube("body", "black", -0.3, -2.4, 3.6, 0.3, -1.7, 5.4)                                # safety lever
    m.cube("body", "black", -1.12, -1.6, -0.2, -0.9, -0.9, 1.8)                             # mag catch (right)

    # ---------------------------------------------------------------- receiver (blued steel), port, rear sight
    m.rbox("receiver", "steel", -1.05, -1.1, -8.0, 1.05, 1.5, 9.0, c=0.35)
    m.cube("receiver", "black", -1.1, 0.0, -4.4, -0.4, 1.55, 2.6)                           # ejection port
    m.cube("receiver", "gunmetal", -1.12, 0.0, -4.5, -1.04, 1.6, -4.4)
    m.cube("receiver", "gunmetal", -1.12, 0.0, 2.6, -1.04, 1.6, 2.7)
    m.cube("receiver", "gunmetal", -0.55, 1.4, -8.0, 0.55, 1.65, 9.0)                       # rail continues over the receiver
    for z in [-7.6 + 0.95 * i for i in range(17)]:
        m.cube("receiver", "black", -0.6, 1.6, z, 0.6, 1.85, z + 0.42)
    m.rbox("receiver", "black", -1.1, 1.8, RZ - 1.9, 1.1, 2.7, RZ + 1.2, c=0.2)             # rear sight base
    m.cube("receiver", "black", -1.12, 2.6, RZ - 0.9, -0.75, SY + 1.3, RZ + 0.9)             # protective wings
    m.cube("receiver", "black", 0.75, 2.6, RZ - 0.9, 1.12, SY + 1.3, RZ + 0.9)
    m.cube("receiver", "black", -0.75, SY + 0.8, RZ - 0.45, 0.75, SY + 1.3, RZ + 0.45)      # aperture upper
    m.cube("receiver", "black", -0.75, 2.5, RZ - 0.45, 0.75, SY - 0.8, RZ + 0.45)           # aperture lower
    m.cube("receiver", "gunmetal", -1.35, 2.3, RZ - 0.4, -1.1, 2.9, RZ + 0.3)               # windage knob
    m.cube("receiver", "steel", -0.7, -0.9, 6.5, 0.7, -0.3, 8.6)                            # tang bump

    m.bone("bolt", "rifle", (0, 0, 0))
    m.cube("bolt", "stainless", -0.99, 0.3, -4.0, -0.9, 1.4, 1.4)
    m.cube("bolt", "steel", -0.88, 0.7, 1.4, 0.88, 1.5, 4.0)
    m.cube("bolt", "steel", -1.4, -0.1, -8.0, -0.8, 0.5, 0.0)                               # op rod stub
    m.bone("bolt_handle", "bolt", (-1.0, 1.0, -1.0))
    m.cube("bolt_handle", "steel", -2.0, 0.55, -1.5, -0.9, 1.35, -0.5)
    m.cube("bolt_handle", "steel", -2.6, 0.2, -1.9, -1.9, 1.7, -0.1)
    m.cube("bolt_handle", "black", -2.9, 0.1, -2.0, -2.55, 1.8, 0.0)

    # ---------------------------------------------------------------- 20-round box magazine (blocky, slight curve)
    m.bone("magazine", "rifle", (0, -4.3, -3.0))
    ey, ez, ang = m.chain("magazine", "black", -0.95, 0.95, -4.3, -3.0, 1.4, 3.2, 6, 7)
    m.cube("magazine", "steel", -1.0, ey - 0.3, ez - 1.7, 1.0, ey + 0.1, ez + 1.7, rot=[-ang, 0, 0], pivot=[0, ey, ez])
    for i in range(4):                                                                       # witness ribs
        m.cube("magazine", "steel", -0.97, -5.4 - i * 1.5, -4.8, -0.9, -5.0 - i * 1.5, -1.6)
    m.cube("magazine", "brass", -0.5, -4.35, -4.2, 0.5, -4.15, -1.6)

    m.muzzle_flash(MZ - 0.2, length=5.0)
    m.casing(-1.1, 1.0, -1.2, length=3.0, r=0.5)
    m.hand_left(-3.0, -14.0)
    m.hand_right(-6.4, 6.4, -3.2)

    cfg = dict(
        name=ID, hand_l=(-3.0, -14.0), mag_grip=(-9.2, -4.4), mag_drop=8.5, mag_rock=8,
        charge_hand="right", hand_r=(-6.4, 6.4), handle=(-2.7, 1.0, -1.0), bolt_travel=5.0, hold_open=True,
        release_mode="handle",
        fire_len=0.26, cycle=0.1, kick_z=1.8, kick_pitch=2.2, kick_yaw=0.5, flash=1.0,
        reload_len=2.0, charge_len=0.95, release_len=0.6, eject=(-1.1, 1.0, 0.8),
        sight=(SY, RZ), butt=29.1,
    )
    return m, cfg
