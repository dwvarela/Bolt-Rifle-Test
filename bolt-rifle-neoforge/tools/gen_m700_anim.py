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


def feed_round(a, t_in, t_up, t_push, t_seat, t_out):
    """A cartridge rises out of the magazine into the open action (visible through the port), then rides forward into the chamber."""
    a.show("chamber_round", t_in, t_out)
    a.pos("chamber_round", t_in, [0, -2.2, 1.4]).pos("chamber_round", t_up, [0, -0.5, 1.4])
    a.pos("chamber_round", t_push, [0, -0.5, 1.4]).pos("chamber_round", t_seat, [0, -0.5, -2.4])
    a.pos("chamber_round", t_out, [0, -0.5, -2.4])


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
feed_round(a, 0.97, 1.08, 1.2, 1.38, 1.42)
a.show("casing", 0.9, 1.32)
a.pos("casing", 0.9, ZERO, SNAP).pos("casing", 0.98, [0, 3.4, 2.6]).pos("casing", 1.08, [0, 4.4, 4.2], SMOOTH)
a.pos("casing", 1.3, [0, -3.2, 8.0], FALL)
a.rot("casing", 0.9, ZERO).rot("casing", 1.3, [0, 0, 380])
anims.append(a)


def reload_mag(a):
    """Cinematic magazine swap, 0 -> 2.9 s: the rifle rolls toward the support hand, mag released and dropped, the hand dips to the
    belt for a fresh mag, brings it up, seats it, slaps the floor plate, then everything settles back."""
    # support hand: palm top flush under the floor plate while it holds a mag (hand y = mag y - 0.9)
    hand = [(0.0, [0, 0, 0]), (0.10, [2.5, -2.5, 6.0]), (0.26, [1.2, -2.2, 15.0]), (0.30, [0, -0.9, 15.0]), (0.34, [0, -1.6, 15.0]),
            (0.72, [0, -11.4, 15.0]), (0.80, [1.5, -12.6, 14.0]), (1.00, [4.2, -15.5, 10.0]), (1.12, [4.4, -16.0, 10.0]),
            (1.20, [1.6, -12.0, 14.0]), (1.40, [0.9, -9.0, 15.0]), (1.65, [0.2, -4.3, 15.0]), (1.80, [0, -0.7, 15.0]),
            (1.90, [0, -1.6, 15.0]), (1.97, [0, -0.4, 15.0]), (2.08, [0, -1.2, 15.0]), (2.30, [1.6, -2.0, 12.0]),
            (2.60, [1.2, -1.0, 4.0]), (2.90, [0, 0, 0])]
    for t, v in hand:
        a.pos("left_hand", t, v)
    # the hand turns slightly with the mag (wrist roll) and flicks it away
    for t, v in ((0.0, [0, 0, 0]), (0.26, [0, 0, 0]), (0.72, [-8, 0, 6]), (1.0, [-25, 0, 14]), (1.2, [-20, 0, 10]), (1.65, [-6, 0, 3]),
                 (1.8, [0, 0, 0]), (2.3, [0, 0, 0]), (2.9, [0, 0, 0])):
        a.rot("left_hand", t, v)
    # old magazine: click out, pulled down, dropped; new one appears in the hand, rises, seats
    a.pos("magazine", 0.0, ZERO).pos("magazine", 0.30, ZERO).pos("magazine", 0.34, [0, -0.7, 0]).pos("magazine", 0.72, [0, -10.5, 0])
    a.pos("magazine", 0.98, [0, -34.0, 0], FALL)
    a.show("magazine", 0.0).key("magazine", "scale", 0.97, ONE, STEP).key("magazine", "scale", 0.98, ZERO, STEP)
    a.key("magazine", "scale", 1.17, ZERO, STEP).key("magazine", "scale", 1.18, ONE, STEP)
    a.pos("magazine", 1.18, [0, -11.1, 0]).pos("magazine", 1.40, [0, -8.1, 0]).pos("magazine", 1.65, [0, -3.4, 0])
    a.pos("magazine", 1.80, [0, 0.2, 0], SNAP).pos("magazine", 1.86, ZERO).pos("magazine", 2.9, ZERO)
    # rifle: rolls toward the support hand and lifts the muzzle, tugs when the mag comes out, bumps when it seats, slaps down, settles
    for t, v in ((0.0, ZERO), (0.28, [0.5, -0.9, 1.6]), (1.70, [0.5, -0.9, 1.6]), (1.80, [0.5, -0.9, 2.1]), (1.86, [0.5, -1.0, 1.6]),
                 (1.97, [0.5, -1.35, 1.6]), (2.08, [0.5, -0.9, 1.6]), (2.9, ZERO)):
        a.pos("rifle", t, v)
    for t, v in ((0.0, ZERO), (0.28, [-9.0, 5.0, -20.0]), (0.34, [-9.5, 5.0, -20.5]), (0.72, [-11.0, 6.0, -22.0]), (0.9, [-10.0, 5.5, -21.0]),
                 (1.2, [-9.0, 5.0, -20.0]), (1.65, [-8.0, 4.5, -19.5]), (1.80, [-5.5, 4.0, -19.0]), (1.97, [-9.5, 5.0, -20.0]), (2.08, [-9.0, 5.0, -20.0]),
                 (2.9, ZERO)):
        a.rot("rifle", t, v)


a = Anim("reload", 2.9, hidden=HIDDEN)
reload_mag(a)
a.key("right_hand", "scale", 0.0, ONE)
anims.append(a)

# ---- reload + chamber a round ----
a = Anim("reload_chamber", 4.0, hidden=HIDDEN)
reload_mag(a)
a.pos("rifle", 4.0, ZERO).rot("rifle", 4.0, ZERO).pos("left_hand", 4.0, ZERO).pos("magazine", 4.0, ZERO)
bolt_cycle(a, lift0=2.92, lift1=3.06, back1=3.2, hold1=3.56, fwd1=3.7, down1=3.84)
a.hand_swap(2.92, 3.86)
feed_round(a, 3.26, 3.4, 3.58, 3.74, 3.8)
anims.append(a)

write(RES, "bolt_rifle", "animation.bolt_rifle.", anims)
