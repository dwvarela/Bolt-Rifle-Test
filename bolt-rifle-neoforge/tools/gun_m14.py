"""M14 EBR (Mk14 Mod 0 style), modelled from the reference side views: black aluminium chassis with slotted handguard,
Picatinny rails, slotted birdcage, telescoping stock with cheek riser and perforated side plates, angular grip, 20-rd box mag.
Coordinates are taken straight from the reference image (x,Y in image units) via Z()/Yy() so proportions stay faithful."""
from gunlib import Model

ID = "m14ebr"


def Z(x):
    return 23.5 - (x - 18) / 22.8


def Yy(y):
    return (166 - y) / 22.8


def build():
    m = Model(ID, seed=31)
    for b in ("chassis", "barrel", "receiver"):
        m.bone(b, "rifle", (0, 0, 0))
    m.bone("scope", "rifle", (0, 3.3, -4))

    def sb(bone, mat, x0, x1, Y0, Y1, hw, c=0.5):
        """Side-profile block: image x range -> z, image Y range -> y, symmetric half width."""
        m.rbox(bone, mat, -hw, Yy(Y1), Z(x1), hw, Yy(Y0), Z(x0), c=c)

    # ---------------------------------------------------------------- barrel, collar, gas cylinder, slotted birdcage, front sight
    m.bar("barrel", "steel", 0, 0, Z(1260), Z(640), 0.5, fine=True)
    m.bar("barrel", "black", 0, 0, Z(1385), Z(1255), 0.68, fine=True)                         # birdcage
    for zz in (Z(1300), Z(1335)):
        for sx in (-1, 1):
            m.cube("barrel", "steel", sx * 0.69 - 0.05, -0.18, zz - 0.5, sx * 0.69 + 0.05, 0.18, zz + 0.9)
        m.cube("barrel", "steel", -0.18, 0.67, zz - 0.5, 0.18, 0.74, zz + 0.9)
        m.cube("barrel", "steel", -0.18, -0.74, zz - 0.5, 0.18, -0.67, zz + 0.9)
    m.cube("barrel", "black", -0.3, -0.3, Z(1385) - 0.03, 0.3, 0.3, Z(1385) + 0.05)
    sb("barrel", "steel", 1042, 1100, 150, 190, 0.85, c=0.35)                               # gas lock / collar
    m.bar("barrel", "steel", 0, -1.0, Z(1150), Z(1060), 0.3)                                 # gas cylinder nose
    sb("barrel", "black", 1268, 1300, 160, 182, 0.7, c=0.25)                                 # front sight base
    for sx in (-1, 1):
        m.cube("barrel", "black", sx * 0.62 - 0.1, 0.5, Z(1298), sx * 0.62 + 0.1, 1.95, Z(1270))   # hood ears
    m.cube("barrel", "black", -0.14, 0.5, Z(1294), 0.14, 1.75, Z(1278))                      # post
    # ---------------------------------------------------------------- chassis: smooth rear shell, slotted front handguard, rails
    sb("chassis", "poly", 640, 872, 152, 236, 1.78, c=0.95)                                  # solid upper/lower shell
    sb("chassis", "poly", 872, 1040, 176, 236, 1.78, c=0.8)                                  # lower block
    for i in range(4):                                                                       # oval cut-outs through the upper walls
        x0 = 905 + i * 35
        m.cube("chassis", "black", -1.84, Yy(172), Z(x0 + 26), -1.7, Yy(158), Z(x0))
        m.cube("chassis", "black", 1.7, Yy(172), Z(x0 + 26), 1.84, Yy(158), Z(x0))
    for sx in (-1, 1):                                                                       # thin upper side walls between slots
        m.cube("chassis", "poly", sx * 1.75 - 0.08, Yy(176), Z(1040), sx * 1.75 + 0.08, Yy(152), Z(872))
    m.cube("chassis", "gunmetal", -0.65, Yy(152), Z(1040), 0.65, Yy(130), Z(640))            # top rail base
    for zz in [Z(1040) + 0.8 * i for i in range(int((Z(640) - Z(1040)) / 0.8))]:
        m.cube("chassis", "black", -0.68, Yy(140), zz, 0.68, Yy(132), zz + 0.42)               # rail teeth
    m.cube("chassis", "gunmetal", -0.65, Yy(238), Z(1040), 0.65, Yy(236), Z(872))              # bottom rail
    for zz in [Z(1036) + 0.8 * i for i in range(int((Z(872) - Z(1040)) / 0.8))]:
        m.cube("chassis", "black", -0.68, Yy(246), zz, 0.68, Yy(238), zz + 0.42)
    for sx in (-1, 1):                                                                       # side rails (lower)
        for zz in [Z(1040) + 0.8 * i for i in range(int((Z(872) - Z(1040)) / 0.8))]:
            m.cube("chassis", "black", sx * 1.78 - (0.3 if sx > 0 else 0), Yy(214), zz, sx * 1.78 + (0.3 if sx < 0 else 0), Yy(190), zz + 0.42)
    # chassis body between receiver and handguard, magwell, rear adapter
    sb("chassis", "poly", 440, 645, 196, 238, 1.4, c=0.6)
    sb("chassis", "poly", 385, 445, 184, 228, 1.2, c=0.5)                                    # rear receiver adapter
    m.bar("chassis", "steel", 0, Yy(214), Z(440), Z(100), 0.5, fine=True)                    # telescoping stock tube
    for zz in (Z(330), Z(350)):
        m.cube("chassis", "black", -0.62, Yy(214) + 0.4, zz - 0.3, 0.62, Yy(214) + 0.6, zz + 0.3)  # sling button pads
    # stock: perforated side plates, big buttplate, floating cheek riser
    for sx in (-1, 1):
        m.cube("chassis", "poly", sx * 1.2 - 0.12, Yy(305), Z(118), sx * 1.2 + 0.12, Yy(198), Z(62))
        for i in range(6):
            m.cube("chassis", "black", sx * 1.2 - 0.14, Yy(215 + i * 14) - 0.2, Z(100), sx * 1.2 + 0.14, Yy(215 + i * 14) + 0.2, Z(76))
    m.rbox("chassis", "poly", -1.3, Yy(345), Z(62), 1.3, Yy(195), Z(18), c=0.7)               # buttplate
    m.rbox("chassis", "rubber", -1.3, Yy(340), Z(30), 1.3, Yy(200), Z(18), c=0.6)
    for i in range(5):
        m.cube("chassis", "black", -1.28, Yy(215 + i * 25), Z(60), 1.28, Yy(212 + i * 25), Z(40))
    for sx in (-1, 1):
        m.cube("chassis", "poly", sx * 1.0 - 0.15, Yy(196), Z(112), sx * 1.0 + 0.15, Yy(148), Z(72))   # riser posts
    m.slope("chassis", "poly", -1.35, 1.35, Yy(160), Yy(143), Z(252), Z(62), -3)              # cheek riser plate
    m.slope("chassis", "black", -1.2, 1.2, Yy(147), Yy(143), Z(240), Z(80), -3)
    # pistol grip: angular, rear-raked, textured panels
    m.slope("chassis", "poly", -0.98, 0.98, -8.7, -3.0, 7.6, 10.0, 23)
    m.slope("chassis", "rubber", -1.0, 1.0, -8.3, -3.6, 7.9, 9.9, 23)
    m.cube("chassis", "black", -0.99, -8.95, 9.0, 0.99, -8.7, 11.2)                      # heel cap
    for i in range(5):                                                                    # diamond panel lines
        m.slope("chassis", "black", -1.02, 1.02, -7.8 + i * 0.9, -7.65 + i * 0.9, 8.0, 9.7, 23)
    # trigger guard + trigger
    m.cube("receiver", "steel", -0.25, Yy(270), Z(446), 0.25, Yy(262), Z(398))
    m.cube("receiver", "steel", -0.25, Yy(270), Z(446), 0.25, Yy(215), Z(438))
    m.cube("receiver", "steel", -0.25, Yy(270), Z(400), 0.25, Yy(240), Z(392))
    m.slope("receiver", "black", -0.2, 0.2, Yy(262), Yy(215), Z(436), Z(422), -12)
    # ---------------------------------------------------------------- receiver group
    sb("receiver", "steel", 380, 645, 152, 205, 1.1, c=0.35)
    m.cube("receiver", "black", -1.12, Yy(185), Z(618), -0.4, Yy(150), Z(520))               # ejection port
    m.cube("receiver", "gunmetal", -1.14, Yy(185), Z(522), -1.04, Yy(150), Z(518))
    m.cube("receiver", "gunmetal", -1.14, Yy(185), Z(620), -1.04, Yy(150), Z(616))
    m.cube("receiver", "gunmetal", -0.62, Yy(152), Z(645), 0.62, Yy(130), Z(396))            # rail over the receiver (scope base)
    for zz in [Z(645) + 0.8 * i for i in range(int((Z(396) - Z(645)) / 0.8))]:
        m.cube("receiver", "black", -0.65, Yy(140), zz, 0.65, Yy(132), zz + 0.42)
    # M14 rear aperture sight (ghost ring with windage knobs), under the scope
    m.rbox("receiver", "steel", -0.95, Yy(152), Z(490), 0.95, Yy(140), Z(425), c=0.2)
    m.cube("receiver", "black", -0.75, 0.9, Z(470), -0.45, 1.5, Z(440))
    m.cube("receiver", "black", 0.45, 0.9, Z(470), 0.75, 1.5, Z(440))
    m.cube("receiver", "gunmetal", -1.3, 0.8, Z(458), -0.95, 1.2, Z(442))
    m.cube("receiver", "gunmetal", 0.95, 0.8, Z(458), 1.3, 1.2, Z(442))
    m.bone("bolt", "rifle", (0, 0, 0))
    m.cube("bolt", "stainless", -1.0, -0.3, Z(612), -0.9, 0.55, Z(540))
    m.cube("bolt", "steel", -0.88, 0.0, Z(540), 0.88, 0.6, Z(470))
    m.cube("bolt", "steel", -1.95, -0.6, Z(1030), -1.3, -0.1, Z(660))                       # op rod
    m.bone("bolt_handle", "bolt", (-1.1, 0.3, -1.0))
    m.cube("bolt_handle", "steel", -2.0, -0.15, -1.5, -0.9, 0.65, -0.5)
    m.cube("bolt_handle", "steel", -2.6, -0.5, -1.9, -1.9, 1.0, -0.1)
    m.cube("bolt_handle", "black", -2.9, -0.6, -2.0, -2.55, 1.1, 0.0)
    m.hand_bolt("bolt_handle", -2.7, 0.3, -1.0)

    # ---------------------------------------------------------------- compact scope on the rail (axis 3.3 above bore; eyepiece at z=4)
    m.cube("scope", "gunmetal", -0.9, 1.4, -11.4, 0.9, 2.2, -4.2)                            # mount base
    m.rbox("scope", "scope", -1.2, 1.9, -11.0, 1.2, 4.9, -9.8, c=0.4)                        # rings
    m.rbox("scope", "scope", -1.2, 1.9, -6.0, 1.2, 4.9, -4.8, c=0.4)
    m.bar("scope", "scope", 0, 3.3, -13.0, 0.5, 1.05, fine=True)                             # main tube
    m.bar("scope", "scope", 0, 3.3, -16.6, -13.0, 1.6, fine=True)                            # objective bell
    m.bar("scope", "scope", 0, 3.3, 0.5, 4.0, 1.3, fine=True)                                # eyepiece
    m.cube("scope", "lens", -1.45, 1.85, -16.64, 1.45, 4.75, -16.6)
    m.cube("scope", "lens", -0.95, 2.35, 3.98, 0.95, 4.25, 4.02)
    m.rbox("scope", "scope", -0.55, 4.3, -8.4, 0.55, 5.3, -7.2, c=0.15)                      # elevation turret
    m.cube("scope", "stainless", -0.4, 5.3, -8.2, 0.4, 5.6, -7.4)
    m.rbox("scope", "scope", -1.9, 2.8, -8.4, -1.0, 3.8, -7.2, c=0.15)                       # windage turret
    m.cube("scope", "stainless", -0.9, 2.7, 0.0, 0.9, 3.9, 0.4)                              # power ring

    # ---------------------------------------------------------------- 20-round box magazine
    m.bone("magazine", "rifle", (0, -3.0, -0.95))
    m.rbox("magazine", "black", -0.98, Yy(358), Z(620), 0.98, Yy(228), Z(530), c=0.1)
    m.cube("magazine", "steel", -1.02, Yy(362), Z(624), 1.02, Yy(352), Z(526))               # floorplate
    m.cube("magazine", "steel", -1.0, Yy(300), Z(612), 1.0, Yy(296), Z(538))                 # witness rib
    m.cube("magazine", "steel", -1.0, Yy(270), Z(612), 1.0, Yy(266), Z(538))
    m.cube("magazine", "brass", -0.5, Yy(230), Z(612), 0.5, Yy(228), Z(540))

    m.muzzle_flash(Z(1385) - 0.2, length=5.5, width=3.6)
    m.casing(-1.1, 0.5, -1.0)
    m.hand_left(-4.0, -14.5)
    m.hand_right(-6.0, 8.8, -3.6)

    cfg = dict(
        name=ID, hand_l=(-4.0, -14.5), mag_grip=(-6.8, -0.95), mag_drop=9.0, mag_rock=10,
        charge_hand="right", handle=(-2.7, 0.3, -1.0), bolt_travel=6.5, hold_open=True,
        release_mode="handle",
        fire_len=0.32, cycle=0.12, kick_z=2.8, kick_pitch=4.0, kick_yaw=0.8, flash=1.25,
        reload_len=2.3, charge_len=0.95, release_len=0.7, eject=(-1.1, 0.5, 0.9),
        sight=(3.3, 4.0), butt=23.5,
    )
    return m, cfg
