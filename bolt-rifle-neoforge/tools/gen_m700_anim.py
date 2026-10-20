"""M700 animations (eased). Usage: gen_m700_anim.py <resources_dir>"""
import sys
from animlib import Anim, write, SMOOTH, SNAP, FALL, STEP, ZERO, ONE

RES = sys.argv[1]
HIDDEN = ("bolt_hand", "casing", "chamber_round", "muzzle_flash")
LIFT = 75.0       # handle sits at -x (shooter's right in game); +z rotation lifts it
BACK = 5.6        # bolt travel in px
anims = []


def flash(a):
    a.key("muzzle_flash", "scale", 0.0, ZERO, STEP).key("muzzle_flash", "scale", 0.01, [0.5, 0.5, 0.5], STEP)
    a.key("muzzle_flash", "scale", 0.045, [0.65, 0.65, 0.65], STEP).key("muzzle_flash", "scale", 0.06, ZERO, STEP)


def bolt_cycle(a, lift0, lift1, back1, hold1, fwd1, down1):
    a.rot("bolt_handle", 0.0, ZERO).rot("bolt_handle", lift0, ZERO)
    a.rot("bolt_handle", lift1, [0, 0, LIFT]).rot("bolt_handle", fwd1, [0, 0, LIFT]).rot("bolt_handle", down1, ZERO)
    a.pos("bolt", 0.0, ZERO).pos("bolt", lift1, ZERO).pos("bolt", back1, [0, 0, BACK], SNAP)
    a.pos("bolt", hold1, [0, 0, BACK]).pos("bolt", fwd1, ZERO)


# ---- idle: slow breathing, never perfectly still ----
a = Anim("idle", 4.0, loop=True, hidden=HIDDEN)
a.pos("rifle", 0.0, ZERO).pos("rifle", 2.0, [0, 0.08, 0.05]).pos("rifle", 4.0, ZERO)
a.rot("rifle", 0.0, ZERO).rot("rifle", 1.0, [0.25, 0, 0.3]).rot("rifle", 3.0, [-0.25, 0, -0.3]).rot("rifle", 4.0, ZERO)
anims.append(a)

# ---- dry fire click ----
a = Anim("dryfire", 0.3, hidden=HIDDEN)
a.pos("rifle", 0.0, ZERO).pos("rifle", 0.04, [0, 0, 0.45], SNAP).pos("rifle", 0.26, ZERO)
anims.append(a)

# ---- fire: kick, muzzle climb, settle, then work the bolt ----
a = Anim("fire", 1.6, hidden=HIDDEN)
flash(a)
a.pos("rifle", 0.0, ZERO).pos("rifle", 0.04, [0, 0.35, 2.7], SNAP).pos("rifle", 0.2, [0, 0.12, 1.2])
a.pos("rifle", 0.5, [0, -0.15, 0.3]).pos("rifle", 0.9, [0, -0.2, 0.15]).pos("rifle", 1.45, ZERO)
a.rot("rifle", 0.0, ZERO).rot("rifle", 0.04, [-6.0, 0, 0.8], SNAP).rot("rifle", 0.24, [-2.2, 0, 0.3])
a.rot("rifle", 0.6, [-0.4, 0, 0]).rot("rifle", 1.45, ZERO)
bolt_cycle(a, lift0=0.5, lift1=0.72, back1=0.93, hold1=1.02, fwd1=1.18, down1=1.38)
a.hand_swap(0.5, 1.4)
a.show("casing", 0.9, 1.32)
a.pos("casing", 0.9, ZERO, SNAP).pos("casing", 0.98, [0, 3.4, 2.6]).pos("casing", 1.08, [0, 4.4, 4.2], SMOOTH)
a.pos("casing", 1.3, [0, -3.2, 8.0], FALL)
a.rot("casing", 0.9, ZERO).rot("casing", 1.3, [0, 0, 380])
anims.append(a)


def reload_mag(a):
    """Magazine swap: 0 -> 2.9 s."""
    # the support hand cups the magazine floor plate: its palm top sits flush under the plate (mag y + 0.7) the whole time it holds it
    hand = [(0.0, [0, 0, 0]), (0.16, [3.0, -1.2, 5.0]), (0.32, [2.2, -1.6, 15.0]), (0.46, [0, 0.7, 15.0]),
            (0.62, [0, -0.3, 15.0]), (0.95, [0, -9.8, 15.0]), (1.1, [0, -14.0, 15.0]), (1.36, [0, -14.0, 15.0]),
            (1.65, [0, -10.8, 15.0]), (2.05, [0, -2.8, 15.0]), (2.22, [0, 0.9, 15.0]),
            (2.4, [0, 0.7, 15.0]), (2.56, [2.4, -1.6, 13.0]), (2.74, [3.0, -1.0, 4.0]), (2.9, [0, 0, 0])]
    for t, v in hand:
        a.pos("left_hand", t, v)
    a.pos("magazine", 0.0, ZERO).pos("magazine", 0.45, ZERO).pos("magazine", 0.62, [0, -1.0, 0])
    a.pos("magazine", 0.95, [0, -10.5, 0])
    a.show("magazine", 0.0).key("magazine", "scale", 0.96, ONE, STEP).key("magazine", "scale", 0.97, ZERO, STEP)
    a.key("magazine", "scale", 1.34, ZERO, STEP).key("magazine", "scale", 1.36, ONE, STEP)
    a.pos("magazine", 1.36, [0, -14.7, 0]).pos("magazine", 1.65, [0, -11.5, 0]).pos("magazine", 2.05, [0, -3.5, 0])
    a.pos("magazine", 2.22, [0, 0.2, 0], SNAP).pos("magazine", 2.32, ZERO).pos("magazine", 2.9, ZERO)
    # weight shift and cant while the support hand is busy
    a.pos("rifle", 0.0, ZERO).pos("rifle", 0.35, [0, -0.4, 0.3]).pos("rifle", 2.4, [0, -0.4, 0.3]).pos("rifle", 2.9, ZERO)
    a.rot("rifle", 0.0, ZERO).rot("rifle", 0.5, [0.8, 0, -6.0]).rot("rifle", 2.3, [0.8, 0, -6.0]).rot("rifle", 2.9, ZERO)


a = Anim("reload", 2.9, hidden=HIDDEN)
reload_mag(a)
a.key("right_hand", "scale", 0.0, ONE)
anims.append(a)

# ---- reload + chamber a round ----
a = Anim("reload_chamber", 4.0, hidden=HIDDEN)
reload_mag(a)
a.pos("rifle", 4.0, ZERO).rot("rifle", 4.0, ZERO).pos("left_hand", 4.0, ZERO).pos("magazine", 4.0, ZERO)
bolt_cycle(a, lift0=2.92, lift1=3.1, back1=3.3, hold1=3.4, fwd1=3.58, down1=3.76)
a.hand_swap(2.92, 3.8)
a.show("chamber_round", 3.3, 3.6)
a.pos("chamber_round", 3.28, [0, -1.2, 4.0]).pos("chamber_round", 3.38, [0, 0.0, 4.0]).pos("chamber_round", 3.58, [0, 0.0, -1.8])
anims.append(a)

write(RES, "bolt_rifle", "animation.bolt_rifle.", anims)
