"""M4A1 carbine (red dot, collapsible stock) and the AR-15 sporter (.223, carry-handle irons, fixed stock)."""
import math
from gunlib import Model


def build_ar(ident, mini14):
    m = Model(ident, seed=41 if not mini14 else 43)
    m.bone("body", "rifle", (0, 0, 0))
    m.bone("barrel", "rifle", (0, 0, 0))
    m.bone("upper", "rifle", (0, 0, 0))
    mz = -29.5 if mini14 else -26.8                                  # muzzle tip

    # ---------------------------------------------------------------- barrel, A2 flash hider, gas block + sight tower
    m.bar("barrel", "steel", 0, 0, mz, -6.0, 0.55, fine=True)
    m.bar("barrel", "black", 0, 0, mz, mz + 2.6, 0.78, fine=True)               # A2 flash hider
    for i in range(4):
        m.cube("barrel", "steel", -0.9, -0.1, mz + 0.35 + i * 0.5, 0.9, 0.1, mz + 0.55 + i * 0.5)
        m.cube("barrel", "steel", -0.1, -0.9, mz + 0.35 + i * 0.5, 0.1, 0.9, mz + 0.55 + i * 0.5)
    m.cube("barrel", "black", -0.3, -0.3, mz - 0.03, 0.3, 0.3, mz + 0.05)
    m.cube("barrel", "gunmetal", -0.65, 0.3, mz + 2.6, 0.65, 0.9, mz + 3.1)       # barrel nut ring
    fz = mz + 9.0 if not mini14 else mz + 10.5                                      # front sight tower position
    m.rbox("barrel", "steel", -0.8, -0.9, fz - 1.6, 0.8, 1.7, fz + 1.6, c=0.3)
    for sx in (-0.5, 0.5):                                                         # A-frame front sight: vertical front edge, sloped rear
        m.cube("barrel", "steel", sx - 0.13, 1.7, fz - 0.9, sx + 0.13, 4.4, fz - 0.55)
        m.slope("barrel", "steel", sx - 0.13, sx + 0.13, 1.7, 4.0, fz - 0.8, fz + 0.9, 32)
    m.cube("barrel", "steel", -0.2, 3.6, fz - 0.95, 0.2, 4.4, fz - 0.5)           # post
    m.cube("barrel", "steel", -0.6, 4.1, fz - 0.95, 0.6, 4.4, fz - 0.55)          # apex bridge
    m.cube("barrel", "gunmetal", -0.35, 1.2, fz + 1.6, 0.35, 1.7, fz + 3.4)        # gas tube peek
    # ---------------------------------------------------------------- quad-rail handguard (RIS) with vent slots
    hg0 = fz + 1.8
    hz1 = -3.6
    m.rbox("body", "black", -1.35, -1.35, hg0, 1.35, 1.35, hz1, c=0.45)                 # rail body
    for z in [hg0 + 0.4 + 0.9 * i for i in range(int((hz1 - hg0 - 0.6) / 0.9))]:
        m.cube("body", "gunmetal", -0.55, 1.3, z, 0.55, 1.62, z + 0.42)                   # top rail teeth
        m.cube("body", "gunmetal", -0.55, -1.62, z, 0.55, -1.3, z + 0.42)                 # bottom
        m.cube("body", "gunmetal", 1.3, -0.55, z, 1.62, 0.55, z + 0.42)                   # left
        m.cube("body", "gunmetal", -1.62, -0.55, z, -1.3, 0.55, z + 0.42)                 # right
    for z in [hg0 + 1.6 + 1.6 * i for i in range(int((hz1 - hg0 - 3.0) / 1.6))]:           # oval vents between the rails
        for sx in (-1, 1):
            m.cube("body", "steel", sx * 1.05 - 0.05, 0.62, z, sx * 1.05 + 0.05, 0.98, z + 0.9)
            m.cube("body", "steel", sx * 1.05 - 0.05, -0.98, z, sx * 1.05 + 0.05, -0.62, z + 0.9)
    m.cube("body", "gunmetal", -1.45, -1.45, hz1 - 0.1, 1.45, 1.45, hz1 + 0.5)             # delta ring
    m.cube("body", "gunmetal", -0.4, -1.8, hg0 + 2.5, 0.4, -1.6, hg0 + 3.6)                # sling swivel
    # ---------------------------------------------------------------- upper receiver
    m.rbox("upper", "steel", -1.0, -0.9, -4.4, 1.0, 1.5, 7.0, c=0.35)
    m.rbox("upper", "steel", -0.75, -0.9, -5.8, 0.75, 0.8, -4.3, c=0.3)         # barrel extension nut area
    m.cube("upper", "black", -1.03, 0.2, -2.4, -0.93, 1.4, 2.2)                     # ejection port (open cover)
    m.slope("upper", "gunmetal", -1.25, -0.95, 0.6, 1.5, -2.6, -1.8, -35)            # dust cover (hinged open)
    m.rbox("upper", "steel", -1.1, 0.0, 2.5, -0.9, 0.9, 3.6, c=0.15)              # forward assist
    m.cube("upper", "gunmetal", 0.93, 0.2, -2.4, 1.03, 1.4, 2.2)
    if mini14:
        m.cube("upper", "gunmetal", -0.75, 1.5, -2.8, 0.75, 2.6, 6.0)
        m.slope("upper", "gunmetal", -0.85, 0.85, 2.6, 3.4, -2.8, 5.2, 0)             # carry handle top
        m.cube("upper", "black", -0.35, 1.5, -1.0, 0.35, 2.6, 3.6)                     # handle window
        m.cube("upper", "gunmetal", -0.9, 3.0, 5.0, -0.5, 4.5, 6.4)                    # aperture block
        m.cube("upper", "gunmetal", 0.5, 3.0, 5.0, 0.9, 4.5, 6.4)
        m.cube("upper", "gunmetal", -0.5, 4.1, 5.0, 0.5, 4.5, 6.4)
        m.cube("upper", "gunmetal", -0.5, 3.0, 5.0, 0.5, 3.4, 6.4)
        sight = (3.95, 5.7)
    else:
        m.cube("upper", "steel", -0.55, 1.5, -5.4, 0.55, 2.0, 7.0)                  # flat-top rail
        for z in [-5.0 + 0.9 * i for i in range(14)]:
            m.cube("upper", "black", -0.6, 1.95, z, 0.6, 2.15, z + 0.4)
        # flip-up rear aperture (BUIS); the A2 front tower + post already on the barrel
        m.cube("upper", "gunmetal", -0.85, 2.15, 3.6, 0.85, 2.9, 5.8)                   # base
        m.cube("upper", "black", -0.8, 2.9, 3.9, -0.45, 4.75, 5.5)                       # left cheek
        m.cube("upper", "black", 0.45, 2.9, 3.9, 0.8, 4.75, 5.5)                         # right cheek
        m.cube("upper", "black", -0.5, 2.9, 4.0, 0.5, 3.75, 5.4)                         # lower bridge
        m.cube("upper", "black", -0.5, 4.5, 4.0, 0.5, 4.75, 5.4)                         # upper bar
        m.cube("upper", "gunmetal", 0.8, 3.1, 4.4, 1.2, 3.5, 5.0)                        # windage knob
        sight = (4.12, 4.7)
    # ---------------------------------------------------------------- lower receiver, magwell, grip, controls
    m.rbox("body", "poly", -1.0, -3.4, -3.0, 1.0, -0.8, 7.0, c=0.3)
    m.rbox("body", "poly", -1.05, -5.4, -3.5, 1.05, -3.2, 0.4, c=0.3)                 # magwell (flared)
    m.cube("body", "gunmetal", -1.08, -3.4, 0.9, 1.08, -2.9, 1.6)                      # takedown pin
    m.slope("body", "poly", -0.9, 0.9, -8.9, -2.8, 2.9, 5.9, 17)                       # A2 pistol grip
    m.cube("body", "rubber", -0.93, -9.2, 3.9, 0.93, -8.9, 7.4)
    for yy in (-5.2, -6.0, -6.8):                                                     # finger grooves
        m.cube("body", "black", -0.92, yy, 2.5, 0.92, yy + 0.15, 3.0)
    m.cube("body", "steel", -0.25, -4.3, 0.2, 0.25, -3.8, 2.6)                          # trigger guard
    m.cube("body", "steel", -0.25, -4.3, 0.2, 0.25, -3.2, 0.6)
    m.slope("body", "black", -0.2, 0.2, -3.9, -2.4, 1.1, 1.6, -8)                      # trigger
    m.cube("body", "gunmetal", -1.3, -2.6, 2.2, -1.0, -2.1, 3.3)                      # selector (right)
    m.cube("body", "gunmetal", 1.0, -3.3, -0.6, 1.5, -2.8, 0.7)                       # bolt catch (left)
    m.cube("body", "gunmetal", 1.0, -3.2, -2.4, 1.5, -2.6, -1.6)                      # mag release
    # buffer tube + stock
    m.bar("body", "poly", 0, -0.45, 7.0, 12.4, 0.95, fine=True)
    if mini14:
        for i in range(10):
            z = 12.2 + i * 1.15
            m.cube("body", "poly", -1.0 - i * 0.006, -3.0 - i * 0.28, z, 1.0 + i * 0.006, 0.7 - i * 0.04, z + 1.18, flat=True)
        m.cube("body", "rubber", -1.1, -6.2, 23.7, 1.1, 0.2, 24.6)
        butt = 24.6
    else:
        for i in range(8):                                                                # collapsible stock, sloping underside
            z = 11.2 + i * 1.0
            m.cube("body", "poly", -1.0 - i * 0.005, -3.1 - i * 0.3, z, 1.0 + i * 0.005, 0.9 - i * 0.06, z + 1.02, flat=True)
        m.cube("body", "black", -1.03, -3.6, 11.4, -0.97, -1.0, 17.4)                      # moulded side ribs
        m.cube("body", "black", 0.97, -3.6, 11.4, 1.03, -1.0, 17.4)
        m.slope("body", "rubber", -1.1, 1.1, -5.6, 0.6, 19.0, 20.0, -6)                   # angled butt pad
        m.cube("body", "gunmetal", -0.6, -3.6, 11.0, 0.6, -3.1, 14.4)                     # adjust lever
        m.cube("body", "steel", -0.2, -4.2, 18.0, 0.2, -3.6, 18.6)
        butt = 20.0
    # ---------------------------------------------------------------- charging handle + bolt carrier
    m.bone("charge", "rifle", (0, 1.7, 6.5))
    m.cube("charge", "black", -0.8, 1.45, 6.5, 0.8, 2.0, 9.2)
    m.rbox("charge", "gunmetal", -1.5, 1.5, 8.3, 1.5, 2.2, 9.5, c=0.2)                   # T-handle
    m.cube("charge", "gunmetal", -1.5, 1.5, 8.2, -0.8, 2.3, 9.6)
    m.bone("bolt", "rifle", (0, 0, 0))
    m.cube("bolt", "stainless", -0.99, 0.4, -2.6, -0.9, 1.4, 1.6)

    # ---------------------------------------------------------------- STANAG magazine (curved)
    m.bone("magazine", "rifle", (0, -5.2, -3.4))
    ey, ez, ang = m.chain("magazine", "poly", -0.95, 0.95, -4.8, -1.7, 1.5, 3.5, 8, 14)
    m.cube("magazine", "steel", -1.0, ey - 0.25, ez - 1.9, 1.0, ey + 0.1, ez + 1.9, rot=[-ang, 0, 0], pivot=[0, ey, ez])
    m.cube("magazine", "gunmetal", -0.98, -6.6, -3.5, 0.98, -6.4, 0.2)
    m.cube("magazine", "gunmetal", -0.98, -9.4, -3.9, 0.98, -9.2, -0.1)
    m.cube("magazine", "brass", -0.5, -4.85, -3.1, 0.5, -4.65, -0.4)

    m.muzzle_flash(mz - 0.2, length=5.0)
    m.casing(-1.0, 1.0, 0.0)
    m.hand_left(-2.9, hg0 + 4.0)
    m.hand_right(-6.4, 4.5, -3.2)

    cfg = dict(
        name=ident, hand_l=(-2.9, hg0 + 4.0), mag_grip=(-9.0, -4.6), mag_drop=8.5, mag_rock=9,
        charge_hand="left", charge_bone="charge", handle=(0, 1.8, 8.0), bolt_travel=4.0,
        hold_open=True, release_mode="press", catch=(-3.0, 0.0), catch_x=3.0,
        fire_len=0.24, cycle=0.075, kick_z=1.7, kick_pitch=2.0, kick_yaw=0.45, flash=1.0,
        reload_len=2.0, charge_len=0.95, release_len=0.6, eject=(-1.0, 1.0, 0.8),
        sight=sight, butt=butt,
    )
    return m, cfg


import os
GLB_M4 = os.path.join(os.path.dirname(os.path.abspath(__file__)), "ref", "models", "Fire Arm", "M4A1_Cube.glb")   # GoldbergR (Sketchfab), see CREDITS.md
S4, Z04, Y04 = 25.938, 4.9427, 0.217                      # GLB units -> model px (muzzle tip z=-26.8, bore y=0)


def build():
    """M4A1 from the 'Cube' reference model (hull, grip, magazine, ejection cover); moving parts, flash and gloves are ours."""
    import numpy as np
    import glbsdf
    from meshbake import MModel, mid
    import gun_m700 as g7
    m = MModel("m4a1", lo=(-4.5, -12.0, -30.0), hi=(4.5, 6.0, 23.0), h=float(os.environ.get("H", "0.10")), seed=41, tx=9)
    parts, _ = glbsdf.load_parts(GLB_M4)
    body = m.mesh("body", "rifle", (0, 0, 0), tris=7000)
    mag = m.mesh("magazine", "rifle", (0, -5.2, -3.4), tris=2200)

    def region(X, Y, Z):                                        # materials by region of the one big hull
        mt = np.full(X.shape, mid("gunmetal"))
        mt[Z > 7.2] = mid("poly")                                # buffer tube + stock
        mt[(Y < -0.9) & (Z > -4.5)] = mid("poly")                # lower receiver
        mt[Z < -6.0] = mid("black")                              # handguard
        mt[(Z < -20.0)] = mid("steel")                           # barrel
        mt[(Z < -22.5) & (Z > -26.9)] = mid("black")             # flash hider
        return mt

    for p in parts:
        V = np.stack([p["V"][:, 0] * S4, (p["V"][:, 1] - Y04) * S4, Z04 - p["V"][:, 2] * S4], 1)
        if p["mat"] == 1:
            glbsdf.add_part(mag, V, p["F"], mid("poly"))
        elif p["mat"] == 0:
            glbsdf.add_part(body, V, p["F"], mid("poly"))
        elif p["mat"] == 3:
            glbsdf.add_part(body, V, p["F"], mid("gunmetal"))
        else:
            glbsdf.add_part(body, V, p["F"], 0, matfn=region)
    m.cube("magazine", "brass", -0.5, -1.15, -4.3, 0.5, -0.9, -1.4)                 # top round
    m.bone("charge", "rifle", (0, 0.3, 6.5))
    m.cube("charge", "black", -0.6, -0.3, 6.0, 0.6, 0.5, 9.0)
    m.rbox("charge", "gunmetal", -1.5, 0.4, 8.3, 1.5, 1.2, 9.5, c=0.2)               # T-handle
    m.cube("charge", "gunmetal", -1.5, 0.3, 8.2, -0.8, 1.4, 9.6)
    m.bone("bolt", "rifle", (0, 0, 0))
    m.cube("bolt", "stainless", -0.99, 0.4, -2.6, -0.9, 1.4, 1.6)
    m.muzzle_flash(-27.0, length=5.0)
    m.casing(-1.0, 1.0, 0.0)
    gl = mid("glove")
    L = m.mesh("left_hand", "rifle", (0, -2.9, -12.0), tris=1800)
    g7.glove(L, (0.46, -1.8, -9.5), (-0.2, 0.0, -0.98), (-0.45, 0.89, 0.0), (1, 0.3, 0), gl, (22, 32, 28),
             [(1.3, 0.9, 0.2), (2.0, 2.0, 0.7), (2.0, 3.1, 1.4)], (3.5, -8.6, -2.6))
    R = m.mesh("right_hand", "rifle", (0, -6.4, 4.5), tris=1800)
    g7.glove(R, (-1.5, -5.0, 7.5), (0.0, -0.28, -0.96), (1, 0, 0), (0, 1, 0), gl, (80, 55, 40),
             [(1.25, 0.8, 0.3), (1.9, 1.9, 0.9), (1.9, 3.0, 1.7)], (-3.5, -9.5, 17.0), flen=1.1,
             index_pts=[(-1.45, -4.0, 6.0), (-1.4, -3.7, 4.4), (-1.0, -3.45, 3.0), (-0.6, -3.35, 2.4), (-0.2, -3.3, 2.1)])
    cfg = dict(
        name="m4a1", hand_l=(-2.9, -12.0), mag_grip=(-9.0, -4.6), mag_drop=8.5, mag_rock=9,
        charge_hand="left", charge_bone="charge", handle=(0, 0.9, 8.8), bolt_travel=4.0,
        hold_open=True, release_mode="press", catch=(-3.0, 0.0), catch_x=3.0,
        fire_len=0.24, cycle=0.075, kick_z=1.7, kick_pitch=2.0, kick_yaw=0.45, flash=1.0,
        reload_len=2.0, charge_len=0.95, release_len=0.6, eject=(-1.0, 1.0, 0.8),
        sight=(4.1, 3.5), butt=20.0,
    )
    return m, cfg
