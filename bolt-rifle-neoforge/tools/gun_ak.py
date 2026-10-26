"""AK-47 (Type 3, wood furniture): slim stamped receiver, curved magazine, ladder rear sight."""
import os
from meshbake import MModel, mid
from sdf import *
import gun_m700 as g7

ID = "ak47"


def hands(m):
    """Glove hands (same builder as the M700/M14): support hand cupping the handguard, firing hand on the pistol grip, three fingers round
    the grip and the index finger on the trigger."""
    g = mid("glove")
    L = m.mesh("left_hand", "rifle", (0, -3.3, -12.4), tris=1800)
    g7.glove(L, (0.46, -2.2, -9.9), (-0.2, 0.0, -0.98), (-0.45, 0.89, 0.0), (1, 0.3, 0), g, (22, 32, 28),
             [(1.3, 0.9, 0.2), (2.0, 2.0, 0.7), (2.0, 3.1, 1.4)], (3.5, -9.0, -3.0))
    R = m.mesh("right_hand", "rifle", (0, -5.0, 5.0), tris=1800)
    g7.glove(R, (-1.5, -5.0, 7.5), (0.0, -0.28, -0.96), (1, 0, 0), (0, 1, 0), g, (80, 55, 40),
             [(1.25, 0.8, 0.3), (1.9, 1.9, 0.9), (1.9, 3.0, 1.7)], (-3.5, -9.5, 17.0), flen=1.1,
             index_pts=[(-1.45, -4.0, 6.0), (-1.4, -3.7, 4.4), (-1.0, -3.45, 3.0), (-0.6, -3.35, 2.4), (-0.2, -3.3, 2.1)])


def build():
    m = MModel(ID, lo=(-5.0, -11.5, -20.0), hi=(5.0, 3.0, 25.0), h=float(os.environ.get("H", "0.10")), seed=11, tx=9)
    m.bone("barrel", "rifle", (0, 0, 0))
    m.bone("receiver", "rifle", (0, 0, 0))

    # ---------------------------------------------------------------- barrel group
    m.bar("barrel", "steel", 0, 0, -27.0, -7.0, 0.62, fine=True)
    m.bar("barrel", "black", 0, 0, -27.7, -26.4, 0.9)                           # muzzle nut
    m.cube("barrel", "black", -0.3, -0.3, -27.72, 0.3, 0.3, -27.6)             # bore
    m.cube("barrel", "steel", -0.95, -0.15, -26.8, 0.95, 0.15, -26.6)          # nut groove
    m.slope("barrel", "black", -0.92, 0.92, 0.35, 1.25, -28.0, -26.2, -40)      # slant brake cut
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

    # ---------------------------------------------------------------- wood furniture (SDF meshes shaped after the reference photos)
    # Proportions follow the photos / the real rifle: long stock that drops from the receiver to a tall butt, raked pistol grip,
    # lower handguard with the finger scoop, short upper handguard with the gas tube sitting in it.
    plum = mid("plum")
    wd = m.mesh("wood", "rifle", (0, 0, 0), tris=3200)
    stock = Sil([([(9.2, 2.1), (11.4, 2.0), (13.0, 1.6), (15.0, 0.5), (17.6, -0.5), (20.2, -1.3), (22.5, -2.1),
                   (23.1, -8.6), (20.4, -6.9), (17.2, -5.0), (14.2, -3.7), (11.6, -3.2), (9.2, -3.0)], [])], res=0.04)
    wd.add(Ext(stock, "zy", -1.05, 1.05, r=0.45), mat=plum)
    grip = Sil([([(2.9, -1.6), (6.4, -1.6), (6.9, -3.3), (7.6, -6.2), (8.3, -9.2), (8.1, -10.3), (6.2, -10.5), (5.0, -9.6),
                  (4.2, -6.4), (3.4, -3.6)], [])], res=0.04)
    wd.add(Ext(grip, "zy", -0.88, 0.88, r=0.4), mat=plum)
    low = Sil([([(-7.2, 0.7), (-17.4, 0.7), (-18.9, 0.2), (-18.9, -1.7), (-17.4, -2.3), (-14.0, -2.6), (-11.0, -3.0), (-8.6, -3.1),
                 (-7.2, -2.9)], [])], res=0.04)
    wd.add(Ext(low, "zy", -1.3, 1.3, r=0.5), mat=plum)
    up = Sil([([(-7.4, 0.5), (-7.4, 2.4), (-13.0, 2.55), (-15.0, 2.1), (-15.0, 0.5)], [])], res=0.04)
    wd.add(Ext(up, "zy", -1.2, 1.2, r=0.45), mat=plum)
    fr = m.bone("furniture", "rifle", (0, 0, 0))
    for z in (-14.2, -13.4, -12.6, -11.8):
        m.cube("furniture", "wood", -1.22, 2.0, z, 1.22, 2.1, z + 0.25)          # grip lines on the upper handguard
    m.cube("furniture", "gunmetal", -1.34, -2.8, -17.3, 1.34, 0.8, -17.0)         # front ferrule
    m.cube("furniture", "gunmetal", -1.34, -2.9, -9.9, 1.34, 0.7, -9.6)           # rear ferrule
    m.cube("furniture", "black", -0.5, -2.82, -14.0, 0.5, -2.7, -10.0)            # heat-vent shadow
    m.cube("furniture", "rubber", -0.95, -10.55, 4.9, 0.95, -10.3, 8.2)           # grip cap
    m.cube("furniture", "gunmetal", -0.3, -9.9, 5.4, 0.3, -2.6, 5.9)              # grip screw
    m.rbox("furniture", "black", -1.12, -8.7, 22.45, 1.12, -1.7, 23.25, c=0.3)    # butt plate
    m.cube("furniture", "steel", -0.7, -2.2, 23.2, 0.7, -2.0, 23.3)
    m.cube("furniture", "gunmetal", -0.85, 1.7, 9.2, 0.85, 2.3, 11.2)             # stock screw plate / tang
    m.cube("furniture", "steel", -0.2, -4.4, 15.2, 0.2, -3.7, 15.8)               # sling loop

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

    # ---------------------------------------------------------------- curved 30-round magazine
    m.bone("magazine", "rifle", (0, -2.6, -5.2))
    ey, ez, ang = m.chain("magazine", "black", -0.92, 0.92, -2.5, -3.8, 1.45, 3.6, 12, 54, thick_taper=0.0)
    m.cube("magazine", "steel", -1.0, ey - 0.2, ez - 2.0, 1.0, ey + 0.1, ez + 2.0, rot=[-ang, 0, 0], pivot=[0, ey, ez])
    m.cube("magazine", "brass", -0.85, -2.7, -5.0, -0.05, -2.3, -2.5)            # top rounds (zig-zag), bullets forward
    m.cube("magazine", "steel", -0.8, -2.65, -6.0, -0.1, -2.35, -5.0)
    m.cube("magazine", "brass", 0.05, -2.7, -4.6, 0.85, -2.3, -2.1)
    m.cube("magazine", "steel", 0.1, -2.65, -5.6, 0.8, -2.35, -4.6)
    m.cube("magazine", "steel", -0.96, -3.0, -6.2, 0.96, -2.6, -5.7)              # front lug

    m.muzzle_flash(-27.9)
    m.casing(-1.0, 0.9, -1.0)
    hands(m)

    cfg = dict(
        name=ID, hand_l=(-3.3, -12.4), mag_grip=(-18.2, -10.8), grip_x=-0.3, mag_drop=9.0, mag_rock=17, lift_px=9.0,
        charge_hand="right", hand_r=(-5.0, 7.0), handle=(-2.8, 1.0, -1.0), bolt_travel=7.0, charge_roll=True,
        hand_frame=((-1.5, -5.0, 7.5), (0.0, -0.28, -0.96), (1, 0, 0)), hand_piv=(0, -5.0, 5.0), handle_grip=(-3.5, 2.6, -0.2), hold_open=False,
        fire_len=0.28, cycle=0.10, kick_z=2.3, kick_pitch=3.2, kick_yaw=0.8, flash=1.1,
        reload_len=2.3, charge_len=1.1, release_len=0.0, eject=(-1.0, 1.0, 0.9),
        sight=(3.35, -5.7), butt=22.6,
    )
    return m, cfg
