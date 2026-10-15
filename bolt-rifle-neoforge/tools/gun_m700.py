"""Remington 700 (walnut stock, 4-16x scope, detachable box magazine). Animations: gen_m700_anim.py."""
from gunlib import Model

ID = "bolt_rifle"


def build():
    m = Model(ID, seed=5)
    m.bone("stock", "rifle", (0, 0, 0))
    m.bone("barrel", "rifle", (0, 0, 0))
    m.bone("receiver", "rifle", (0, 0, 0))
    m.bone("scope", "rifle", (0, 4.6, -4))
    m.bone("bolt", "rifle", (0, 0, 0))
    m.bone("bolt_handle", "bolt", (0, 0, 5.0))
    m.hand_bolt("bolt_handle", -4.4, -3.0, 4.8)

    # ---------------------------------------------------------------- black synthetic stock (SPS profile)
    m.rbox("stock", "synth", -1.3, -3.0, -23.2, 1.3, -0.5, -6.0, c=0.5)                   # forend
    m.rbox("stock", "synth", -1.05, -2.7, -24.4, 1.05, -0.9, -23.1, c=0.4)                 # forend tip
    m.cube("stock", "black", -1.1, -3.0, -25.2, 1.1, -2.4, -24.3)                          # tip cap
    m.cube("stock", "black", -1.1, -2.4, -24.6, 1.1, -0.6, -24.35)
    m.rbox("stock", "synth", -1.35, -4.2, -6.0, 1.35, -1.0, 3.6, c=0.5)                    # action section (open behind the magazine for the trigger)
    m.rbox("stock", "synth", -1.35, -1.9, 3.6, 1.35, -1.0, 7.6, c=0.3)                     # tang bridge above the trigger opening
    m.cube("stock", "synth", -1.37, -1.4, -6.0, -1.3, -0.5, 3.4)                           # bedding walls
    m.cube("stock", "synth", 1.3, -1.4, -6.0, 1.37, -0.5, 3.4)
    m.rbox("stock", "synth", -1.2, -6.7, 7.4, 1.2, -1.0, 11.6, c=0.6)                      # wrist / pistol grip (compact, full-bodied)
    m.cube("stock", "black", -1.22, -6.9, 7.6, 1.22, -6.65, 11.4)                           # grip cap
    for i in range(14):                                                                    # buttstock: rising comb, dropped heel
        z = 9.6 + i * 0.92
        top = -1.15 + min(i, 5) * 0.05 - max(0, i - 9) * 0.12
        bot = -5.6 - i * 0.2
        m.cube("stock", "synth", -1.15 - i * 0.004, bot, z, 1.15 + i * 0.004, top, z + 0.94, flat=True)
    m.rbox("stock", "rubber", -1.25, -7.9, 22.4, 1.25, 0.6, 23.4, c=0.3)                  # recoil pad
    m.cube("stock", "stainless", -0.2, -3.7, -16.4, 0.2, -3.0, -15.8)                      # sling stud
    m.cube("stock", "stainless", -0.2, -6.2, 15.5, 0.2, -5.6, 16.1)

    # ---------------------------------------------------------------- barrel
    m.bar("barrel", "steel", 0, 0, -26.0, -6.0, 0.8, fine=True)
    m.bar("barrel", "steel", 0, 0, -33.0, -26.0, 0.62, fine=True)
    m.bar("barrel", "black", 0, 0, -33.6, -32.9, 0.82, fine=True)                          # recessed crown / thread cap
    m.cube("barrel", "black", -0.3, -0.3, -33.62, 0.3, 0.3, -33.5)
    m.cube("barrel", "steel", -0.95, -0.95, -6.6, 0.95, 0.95, -5.8)                        # recoil lug

    # ---------------------------------------------------------------- receiver
    m.bar("receiver", "steel", 0, 0, -6.0, 7.0, 1.2, fine=True)
    m.cube("receiver", "black", -1.25, 0.0, -3.4, -1.05, 1.0, 3.4)                         # ejection port (right)
    m.cube("receiver", "steel", -1.3, -0.5, 4.2, -1.1, 0.4, 5.6)                           # bolt release
    m.slope("receiver", "steel", -1.7, -1.1, -0.1, 0.8, 5.0, 6.6, -10)                      # safety lever
    m.cube("receiver", "black", -0.55, 1.0, -5.6, 0.55, 1.45, 6.6)                         # Picatinny rail base
    for z in [-5.3 + 0.8 * i for i in range(15)]:
        m.cube("receiver", "black", -0.6, 1.4, z, 0.6, 1.65, z + 0.42)                     # rail teeth
    m.rbox("receiver", "steel", -0.9, -5.1, 3.8, 0.9, -4.5, 8.6, c=0.2)                    # trigger guard
    m.cube("receiver", "steel", -0.25, -5.1, 3.8, 0.25, -3.4, 4.35)
    m.cube("receiver", "steel", -0.25, -5.1, 8.0, 0.25, -3.4, 8.6)
    m.cube("receiver", "stainless", -0.3, -4.7, 5.35, 0.3, -2.0, 6.0)                      # trigger blade
    m.cube("receiver", "stainless", -0.3, -4.7, 4.95, 0.3, -4.2, 6.0)                      # trigger shoe
    m.cube("receiver", "gunmetal", -0.4, -2.2, 5.0, 0.4, -1.8, 6.3)                         # trigger housing
    m.cube("receiver", "gunmetal", -1.0, -4.5, -3.6, 1.0, -3.9, 3.8)                       # floor-plate housing

    # ---------------------------------------------------------------- scope (4-16x), eyepiece ends at z = 8
    m.rbox("scope", "scope", -1.25, 1.4, -12.2, 1.25, 5.7, -10.6, c=0.4)                     # rings
    m.rbox("scope", "scope", -1.25, 1.4, -2.8, 1.25, 5.7, -1.2, c=0.4)
    m.cube("scope", "stainless", -0.2, 3.4, -11.9, 0.2, 3.7, -10.9)
    m.bar("scope", "scope", 0, 4.6, -13.0, 3.5, 0.98, fine=True)                            # main tube
    m.bar("scope", "scope", 0, 4.6, -18.2, -13.0, 1.5, fine=True)                           # objective bell
    m.bar("scope", "scope", 0, 4.6, 3.5, 8.0, 1.3, fine=True)                               # eyepiece
    m.cube("scope", "lens", -1.45, 3.15, -18.24, 1.45, 6.05, -18.2)
    m.cube("scope", "lens", -0.95, 3.65, 7.98, 0.95, 5.55, 8.02)
    m.rbox("scope", "scope", -0.55, 5.6, -8.4, 0.55, 6.5, -7.2, c=0.15)                     # elevation turret
    m.cube("scope", "stainless", -0.4, 6.5, -8.2, 0.4, 6.8, -7.4)
    m.rbox("scope", "scope", -2.0, 4.1, -8.4, -0.95, 5.1, -7.2, c=0.15)                     # windage turret
    m.cube("scope", "stainless", -2.3, 4.2, -8.1, -2.0, 5.0, -7.5)
    m.rbox("scope", "scope", -0.55, 4.0, -5.4, 0.55, 5.0, -4.0, c=0.15)                     # parallax knob
    m.cube("scope", "stainless", -1.4, 4.0, -13.15, 1.4, 5.2, -13.0)                         # step ring
    m.cube("scope", "stainless", -1.35, 4.1, 3.2, 1.35, 5.1, 3.6)                            # power ring
    m.cube("scope", "black", -1.5, 3.2, -18.5, 1.5, 6.0, -18.2)                              # sunshade stub

    # ---------------------------------------------------------------- bolt + bolt handle
    m.cube("bolt", "stainless", -1.25, -0.4, -2.4, -1.2, 0.8, 3.0)                          # bolt body seen in the port
    m.cube("bolt", "stainless", 1.2, -0.4, -2.4, 1.25, 0.8, 3.0)
    m.bar("bolt", "black", 0, 0.1, 7.0, 12.0, 0.95, fine=True)                              # bolt shroud
    m.cube("bolt", "stainless", -0.45, -0.35, 12.0, 0.45, 0.55, 13.4)                        # cocking piece
    m.cube("bolt", "steel", -0.3, 0.5, 8.4, 0.3, 1.2, 9.0)                                   # cocking indicator
    m.cube("bolt_handle", "steel", -3.2, -0.45, 4.4, -0.9, 0.35, 5.4)                        # stem
    m.rbox("bolt_handle", "steel", -3.7, -2.4, 4.5, -2.9, 0.1, 5.3, c=0.15)                  # swept-down section
    m.rbox("bolt_handle", "black", -5.0, -4.1, 4.0, -3.0, -2.1, 5.8, c=0.5)                  # knob

    # ---------------------------------------------------------------- detachable box magazine
    m.bone("magazine", "rifle", (0, -1.8, 0.5))
    m.rbox("magazine", "black", -1.0, -10.2, -1.9, 1.0, -1.4, 2.9, c=0.3)
    m.cube("magazine", "stainless", -1.05, -10.7, -2.0, 1.05, -10.2, 3.0)                    # floor plate
    m.cube("magazine", "steel", -1.05, -8.0, -1.95, 1.05, -7.85, 2.95)
    m.cube("magazine", "steel", -1.05, -5.4, -1.95, 1.05, -5.25, 2.95)
    m.cube("magazine", "brass", -0.5, -1.7, -0.9, 0.5, -1.4, 1.9)                            # top round

    # ---------------------------------------------------------------- muzzle flash, spent case, chambering round
    m.muzzle_flash(-33.8)
    m.casing(-1.5, 0.4, 0.5)
    m.bone("chamber_round", "rifle", (0, 0.4, -3))
    m.bar("chamber_round", "brass", 0, 0.5, -3.2, 0.4, 0.45)
    m.cube("chamber_round", "brass", -0.3, 0.2, -4.4, 0.3, 0.8, -3.2)

    m.hand_left(-3.8, -14.0)
    m.hand_right(-4.3, 8.6, -3.3)
    return m, None
