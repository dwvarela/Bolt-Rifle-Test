"""M4A1 carbine (red dot, collapsible stock) and the AR-15 sporter (.223, carry-handle irons, fixed stock)."""
from gunlib import Model


def build_ar(ident, ar15):
    m = Model(ident, seed=41 if not ar15 else 43)
    m.bone("body", "rifle", (0, 0, 0))
    m.bone("barrel", "rifle", (0, 0, 0))
    m.bone("upper", "rifle", (0, 0, 0))
    mz = -30.0 if ar15 else -27.5                               # muzzle (flash hider tip)

    # ---- barrel, A2 flash hider, front sight tower
    m.bar("barrel", "steel", 0, 0, mz, -6.0, 0.8)
    m.bar("barrel", "black", 0, 0, mz - 0.1, mz + 2.4, 1.0)
    for i in range(3):
        m.cube("barrel", "steel", -1.1, -0.15, mz + 0.4 + i * 0.7, 1.1, 0.15, mz + 0.7 + i * 0.7)
    m.cube("barrel", "black", -0.5, -0.5, mz - 0.15, 0.5, 0.5, mz - 0.05)
    fz = mz + 8.5                                               # gas block / front sight
    m.cube("barrel", "gunmetal", -1.1, -1.0, fz - 1.4, 1.1, 2.2, fz + 1.4)
    m.cube("barrel", "steel", -0.25, 2.2, fz - 0.3, 0.25, 4.1, fz + 0.3)       # post
    m.cube("barrel", "gunmetal", -0.8, 2.1, fz - 0.9, 0.8, 2.5, fz + 0.9)
    # ---- handguard (round, two halves)
    hg0 = fz + 1.6
    m.bar("body", "poly", 0, 0, hg0, -4.0, 1.75)
    m.cube("body", "gunmetal", -1.8, -1.0, hg0 + 1.0, 1.8, 1.0, hg0 + 1.6)     # delta ring
    for z in (hg0 + 2.5, hg0 + 3.4, hg0 + 4.3):
        m.cube("body", "black", -1.85, -0.3, z, 1.85, 0.3, z + 0.35)

    # ---- upper receiver
    m.cube("upper", "gunmetal", -1.5, -1.2, -4.5, 1.5, 2.0, 7.2)
    m.cube("upper", "gunmetal", -1.0, -1.2, -6.5, 1.0, 0.6, -4.5)
    m.cube("upper", "black", -1.6, 0.3, -2.2, -1.46, 1.9, 2.4)                  # ejection port (right)
    m.cube("upper", "gunmetal", -1.6, 0.0, 2.6, -1.46, 1.0, 3.6)                # forward assist
    m.cube("upper", "black", 1.46, 0.3, -2.2, 1.6, 1.9, 2.4)
    if ar15:
        # flat top + carry handle with A2 aperture rear sight
        m.cube("upper", "gunmetal", -1.0, 2.0, -3.0, 1.0, 3.4, 6.4)
        m.cube("upper", "gunmetal", -1.1, 3.4, -3.0, 1.1, 4.0, 5.4)             # handle top
        m.cube("upper", "black", -0.5, 2.0, -1.0, 0.5, 3.4, 4.0)                # window
        m.cube("upper", "gunmetal", -1.1, 3.4, 5.4, -0.55, 4.9, 6.6)            # aperture block
        m.cube("upper", "gunmetal", 0.55, 3.4, 5.4, 1.1, 4.9, 6.6)
        m.cube("upper", "gunmetal", -0.6, 4.4, 5.4, 0.6, 4.9, 6.6)
        m.cube("upper", "gunmetal", -0.6, 3.4, 5.4, 0.6, 3.75, 6.6)
    else:
        m.cube("upper", "gunmetal", -0.9, 2.0, -6.0, 0.9, 2.6, 6.8)             # flat-top rail
        for z in [-5.5 + 1.3 * i for i in range(10)]:
            m.cube("upper", "black", -1.0, 2.5, z, 1.0, 2.8, z + 0.6)
    # ---- lower receiver, magwell, grip, trigger guard, selector
    m.cube("body", "poly", -1.5, -4.6, -3.2, 1.5, -1.2, 7.2)
    m.cube("body", "poly", -1.45, -6.4, -3.6, 1.45, -4.6, 0.6)                  # magwell
    m.cube("body", "gunmetal", -1.55, -4.0, 0.8, 1.55, -3.4, 1.4)
    m.cube("body", "poly", -1.4, -6.6, 3.0, 1.4, -4.6, 6.6)                     # pistol grip
    m.cube("body", "poly", -1.4, -8.6, 3.5, 1.4, -6.6, 7.2)
    m.cube("body", "poly", -1.4, -10.4, 4.0, 1.4, -8.6, 7.8)
    m.cube("body", "rubber", -1.45, -10.7, 3.9, 1.45, -10.4, 7.9)
    m.cube("body", "steel", -0.4, -5.2, 0.4, 0.4, -4.6, 3.0)                     # trigger guard
    m.cube("body", "steel", -0.4, -6.0, 0.4, 0.4, -4.6, 1.0)
    m.cube("body", "black", -0.25, -5.4, 1.4, 0.25, -3.6, 2.0)                  # trigger
    m.cube("body", "gunmetal", -1.8, -3.4, 2.0, -1.5, -2.6, 3.4)                # selector (right)
    m.cube("body", "gunmetal", 1.5, -4.4, -0.6, 2.1, -3.8, 0.6)                 # bolt catch (left)
    m.cube("body", "gunmetal", 1.5, -4.2, -2.8, 2.0, -3.4, -1.8)                # mag release (left)
    # ---- buffer tube + stock
    if ar15:
        m.bar("body", "poly", 0, -0.6, 7.2, 12.0, 1.4)
        m.cube("body", "poly", -1.6, -4.2, 12.0, 1.6, 1.0, 16.0)                # A2 fixed stock
        m.cube("body", "poly", -1.7, -6.6, 16.0, 1.7, 0.8, 20.0)
        m.cube("body", "poly", -1.7, -8.2, 20.0, 1.7, 0.4, 23.0)
        m.cube("body", "rubber", -1.8, -8.6, 23.0, 1.8, 0.3, 24.0)
    else:
        m.bar("body", "poly", 0, -0.6, 7.2, 12.0, 1.4)
        m.cube("body", "poly", -1.5, -4.0, 10.0, 1.5, 1.0, 15.0)                # collapsible stock
        m.cube("body", "poly", -1.6, -5.4, 15.0, 1.6, 1.0, 19.0)
        m.cube("body", "rubber", -1.7, -5.8, 19.0, 1.7, 0.8, 19.9)
        m.cube("body", "gunmetal", -1.0, -4.6, 10.0, 1.0, -4.0, 14.0)           # adjust lever
        m.bar("upper", "scope", 0, 3.9, -3.0, 4.6, 1.15)                        # red-dot optic body
        m.cube("upper", "black", -1.5, 2.6, -1.8, 1.5, 3.2, 3.6)                # mount
        m.cube("upper", "scope", -1.5, 3.9, -3.4, 1.5, 5.1, -2.8)               # hood front
        m.cube("upper", "lens", -0.9, 3.2, 4.58, 0.9, 4.9, 4.7)                 # rear lens
        m.cube("upper", "dot", -0.22, 3.7, 4.55, 0.22, 4.1, 4.6)                # the glowing dot
        m.cube("upper", "scope", -0.7, 5.0, 0.2, 0.7, 5.5, 1.6)                 # brightness knob
        m.cube("upper", "scope", -2.2, 3.4, 0.4, -1.1, 4.4, 1.6)
        m.cube("upper", "lens", -1.0, 3.2, -3.4, 1.0, 4.9, -3.35)               # front lens
    butt = 24.0 if ar15 else 19.9

    # ---- charging handle (rear, top) and bolt carrier
    m.bone("charge", "rifle", (0, 2.2, 6.5))
    m.cube("charge", "black", -1.3, 1.8, 6.6, 1.3, 2.6, 9.0)
    m.cube("charge", "gunmetal", -1.6, 1.6, 8.2, 1.6, 2.8, 9.4)
    m.bone("bolt", "rifle", (0, 0, 0))
    m.cube("bolt", "stainless", -1.59, 0.5, -2.4, -1.5, 1.6, 1.4)               # carrier in port
    m.cube("bolt", "steel", -1.3, 0.8, 1.4, 1.3, 1.8, 6.0)

    # ---- STANAG magazine (curves forward)
    m.bone("magazine", "rifle", (0, -6.2, -3.4))
    for i in range(6):
        y1, y0 = -4.6 - 1.9 * i, -4.6 - 1.9 * (i + 1)
        zc = -1.6 - i * i * 0.1 - i * 0.35
        m.cube("magazine", "poly" if i % 2 else "black", -1.3, y0, zc - 2.1, 1.3, y1, zc + 2.1)
    zc = -1.6 - 25 * 0.1 - 6 * 0.35 + 0.5
    m.cube("magazine", "steel", -1.35, -16.2, zc - 2.2, 1.35, -15.9, zc + 2.2)
    m.cube("magazine", "brass", -0.6, -4.7, -3.0, 0.6, -4.5, -0.4)

    m.muzzle_flash(mz - 0.2, length=5.0)
    m.casing(-1.6, 1.1, 0.0)
    m.hand_left(-3.4, hg0 + 4.2)
    m.hand_right(-7.6, 4.9, -4.2)

    sight = (4.0, 5.9) if ar15 else (4.0, 4.6)
    cfg = dict(
        name=ident, hand_l=(-3.4, hg0 + 4.2), mag_grip=(-11.5, -4.4), mag_drop=8.5, mag_rock=9,
        charge_hand="left", charge_bone="charge", handle=(0, 2.2, 7.8), handle_below=0.0, bolt_travel=6.5,
        hold_open=True, release_mode="press", catch=(-3.8, 0.0), catch_x=2.4,
        fire_len=0.24, cycle=0.075, kick_z=1.7, kick_pitch=2.0, kick_yaw=0.45, flash=1.0,
        reload_len=2.0, charge_len=0.95, release_len=0.6, eject=(-1.0, 1.0, 0.8),
        sight=sight, butt=butt,
    )
    return m, cfg


def build():
    return build_ar("m4a1", False)
