"""M700 animations (eased, flowing).  Usage: gen_m700_anim.py <resources_dir>
Hands never pop or scale: the grip hand slides down out of view while the bolt hand rises to the handle (and back); the magazine swap
uses a separate `drop_mag` bone (a copy of the magazine) so the old magazine visibly falls away while the new one is carried up."""
import sys, os, json, copy
from animlib import Anim, write, SMOOTH, SNAP, FALL, STEP, ZERO, ONE

RES = sys.argv[1]
HIDDEN = ("bolt_hand", "casing", "chamber_round", "muzzle_flash", "drop_mag")
LIFT = 75.0       # handle sits at -x (shooter's right in game); +z rotation lifts it
BACK = 5.6        # bolt travel in px
anims = []

# ---- make sure the geo has the drop_mag bone (an exact copy of the magazine) ----
GEO = os.path.join(RES, "assets/boltrifle/geo/item/bolt_rifle.geo.json")
geo = json.load(open(GEO))
bones = geo["minecraft:geometry"][0]["bones"]
if not any(b["name"] == "drop_mag" for b in bones):
    mag = next(b for b in bones if b["name"] == "magazine")
    d = copy.deepcopy(mag)
    d["name"] = "drop_mag"
    bones.append(d)
    json.dump(geo, open(GEO, "w"), separators=(",", ":"))
    print("added drop_mag bone")

OFF_R = [0.8, -6.0, 4.0]          # grip hand parked below the rifle (out of view)
OFF_B = [1.0, -7.0, 5.0]          # bolt hand parked below the handle


def flash(a):
    a.key("muzzle_flash", "scale", 0.0, ZERO, STEP).key("muzzle_flash", "scale", 0.01, [0.5, 0.5, 0.5], STEP)
    a.key("muzzle_flash", "scale", 0.045, [0.65, 0.65, 0.65], STEP).key("muzzle_flash", "scale", 0.06, ZERO, STEP)


def work_bolt(a, t0, eject=False):
    """Complete bolt cycle starting at t0 (duration 1.25 s): grip hand slides away, bolt hand rises to the handle, handle up, bolt
    drawn back (round feeds up), pushed home, handle down, hands swap back."""
    e = 0.01
    # --- hands travel (no popping): the hidden hand is parked out of view before it is shown / after it is hidden
    a.pos("right_hand", t0, ZERO).pos("right_hand", t0 + 0.15, OFF_R).pos("right_hand", t0 + 1.04, OFF_R).pos("right_hand", t0 + 1.26, ZERO)
    a.key("right_hand", "scale", t0, ONE, STEP).key("right_hand", "scale", t0 + 0.16, ZERO, STEP).key("right_hand", "scale", t0 + 1.03, ONE, STEP)
    a.key("bolt_hand", "scale", t0, ZERO, STEP).key("bolt_hand", "scale", t0 + 0.04, ONE, STEP).key("bolt_hand", "scale", t0 + 1.2, ZERO, STEP)
    a.pos("bolt_hand", t0 + 0.04, OFF_B).pos("bolt_hand", t0 + 0.22, ZERO).pos("bolt_hand", t0 + 1.0, ZERO).pos("bolt_hand", t0 + 1.19, OFF_B)
    # --- bolt
    lift0, lift1, back0, back1, fwd0, fwd1, dn0, dn1 = (t0 + x for x in (0.22, 0.36, 0.38, 0.62, 0.70, 0.90, 0.90, 1.02))
    a.rot("bolt_handle", t0, ZERO).rot("bolt_handle", lift0, ZERO).rot("bolt_handle", lift1, [0, 0, LIFT])
    a.rot("bolt_handle", fwd1, [0, 0, LIFT]).rot("bolt_handle", dn1, ZERO)
    a.pos("bolt", t0, ZERO).pos("bolt", back0, ZERO).pos("bolt", back1, [0, 0, BACK]).pos("bolt", fwd0, [0, 0, BACK]).pos("bolt", fwd1, ZERO)
    # --- the rifle is nudged by the work: small tug when the handle breaks free, bump at the rear stop, slam forward
    for t, v in ((lift0, ZERO), (lift1, [0.15, 0, 0.5]), (back1, [-0.3, 0, 0.9]), (fwd0, [-0.2, 0, 0.6]),
                 (fwd1, [0.25, 0, -0.3]), (dn1, ZERO)):
        a.rot("rifle", t, v)
    for t, v in ((lift0, ZERO), (lift1, [0, 0, 0.05]), (back1, [0, 0, 0.22]), (fwd0, [0, 0, 0.18]), (fwd1, [0, 0, -0.12]), (dn1, ZERO)):
        a.pos("rifle", t, v)
    # --- a round rises from the magazine into the open action and rides forward into the chamber
    t_in, t_up, t_push, t_seat, t_out = (t0 + x for x in (0.64, 0.72, 0.78, 0.90, 0.95))
    a.show("chamber_round", t_in, t_out)
    a.pos("chamber_round", t_in, [0, -2.2, 1.4]).pos("chamber_round", t_up, [0, -0.5, 1.4])
    a.pos("chamber_round", t_push, [0, -0.5, 1.4]).pos("chamber_round", t_seat, [0, -0.5, -2.4]).pos("chamber_round", t_out, [0, -0.5, -2.4])
    if eject:                                             # spent case flips out of the port as the bolt comes back
        a.show("casing", t0 + 0.54, t0 + 0.96)
        a.pos("casing", t0 + 0.54, ZERO, SNAP).pos("casing", t0 + 0.62, [0, 3.4, 2.6]).pos("casing", t0 + 0.72, [0, 4.4, 4.2], SMOOTH)
        a.pos("casing", t0 + 0.94, [0, -3.2, 8.0], FALL)
        a.rot("casing", t0 + 0.54, ZERO).rot("casing", t0 + 0.94, [0, 0, 380])


# ---- idle: slow breathing, never perfectly still ----
a = Anim("idle", 4.0, loop=True, hidden=HIDDEN)
a.pos("rifle", 0.0, ZERO).pos("rifle", 2.0, [0, 0.05, 0.03]).pos("rifle", 4.0, ZERO)
a.rot("rifle", 0.0, ZERO).rot("rifle", 1.0, [0.12, 0, 0.15]).rot("rifle", 3.0, [-0.12, 0, -0.15]).rot("rifle", 4.0, ZERO)
anims.append(a)

# ---- dry fire click ----
a = Anim("dryfire", 0.3, hidden=HIDDEN)
a.pos("rifle", 0.0, ZERO).pos("rifle", 0.04, [0, 0, 0.45], SNAP).pos("rifle", 0.26, ZERO)
anims.append(a)

# ---- fire: kick, muzzle climb, settle while the bolt is worked ----
a = Anim("fire", 1.6, hidden=HIDDEN)
flash(a)
a.pos("rifle", 0.0, ZERO).pos("rifle", 0.04, [0, 0.35, 2.7], SNAP).pos("rifle", 0.2, [0, 0.12, 1.2])
a.pos("rifle", 0.34, [0, -0.1, 0.4])
a.rot("rifle", 0.0, ZERO).rot("rifle", 0.04, [-6.0, 0, 0.8], SNAP).rot("rifle", 0.24, [-2.2, 0, 0.3]).rot("rifle", 0.4, [-0.4, 0, 0])
work_bolt(a, 0.2, eject=True)
# the work_bolt keys above continue the rifle tracks; make sure they end at rest
a.pos("rifle", 1.6, ZERO).rot("rifle", 1.6, ZERO)
anims.append(a)


def reload_mag(a):
    """Cinematic magazine swap, 0 -> 2.7 s: the rifle rolls toward the support hand; the hand slides back under the magazine, presses
    the release (click), draws the old magazine down and lets go (it visibly tumbles away as `drop_mag`), swings to the belt, comes back
    up with the new magazine, rocks it in, slaps the floor plate, and everything settles."""
    # support hand: offsets from its resting place under the forend. The palm top sits flush under the floor plate while it holds a mag.
    hand = [(0.0, [0, 0, 0]), (0.30, [0.8, -1.0, 9.5]), (0.34, [0, -0.9, 9.5]), (0.40, [0, -1.2, 9.5]), (0.64, [0, -7.0, 9.5]),
            (0.80, [2.0, -9.5, 8.0]), (1.00, [3.8, -13.5, 6.5]), (1.06, [4.2, -14.5, 6.3]), (1.30, [2.4, -11.5, 8.5]),
            (1.52, [0.8, -6.5, 9.5]), (1.68, [0, -1.0, 9.5]), (1.76, [0, -0.5, 9.5]), (1.84, [0, -1.2, 9.5]), (1.95, [0, -0.4, 9.5]),
            (2.06, [0, -1.2, 9.5]), (2.30, [1.0, -1.8, 7.6]), (2.5, [1.0, -1.0, 3.0]), (2.7, [0, 0, 0])]
    for t, v in hand:
        a.pos("left_hand", t, v)
    for t, v in ((0.0, [0, 0, 0]), (0.30, [0, 0, 0]), (0.64, [-5, 0, 4]), (1.0, [-18, 0, 10]), (1.30, [-14, 0, 8]), (1.68, [-4, 0, 2]),
                 (1.8, [0, 0, 0]), (2.3, [0, 0, 0]), (2.7, [0, 0, 0])):
        a.rot("left_hand", t, v)
    # magazine in the rifle: releases (click at 0.30), pulled down by the hand, then hidden as the dropped copy takes over
    a.key("magazine", "scale", 0.0, ONE, STEP).key("magazine", "scale", 0.64, ZERO, STEP).key("magazine", "scale", 1.0, ONE, STEP)
    for t, v in ((0.0, ZERO), (0.32, ZERO), (0.40, [0, -0.3, 0]), (0.64, [0, -6.1, 0]),
                 (1.0, [3.8, -12.6, -3.2]), (1.30, [2.4, -10.6, -1.0]), (1.52, [0.8, -5.6, 0]), (1.68, [0, -0.1, 0])):
        a.pos("magazine", t, v)
    a.pos("magazine", 1.76, [0, 0.2, 0], SNAP).pos("magazine", 1.84, ZERO).pos("magazine", 2.7, ZERO)
    # the dropped magazine: continues from where the old one was held, tumbles away and falls out of view
    a.key("drop_mag", "scale", 0.0, ZERO, STEP).key("drop_mag", "scale", 0.64, ONE, STEP).key("drop_mag", "scale", 1.35, ZERO, STEP)
    a.pos("drop_mag", 0.64, [0, -6.1, 0]).pos("drop_mag", 0.74, [0.8, -8.2, 0], SMOOTH).pos("drop_mag", 1.3, [3.5, -48.0, -2.0], FALL)
    a.rot("drop_mag", 0.64, ZERO).rot("drop_mag", 0.74, [0, 0, 18]).rot("drop_mag", 1.3, [35, 0, 90], SMOOTH)
    # rifle: rolls toward the support hand, tugs when the mag comes out, bumps when the new one seats, slaps down, settles
    for t, v in ((0.0, ZERO), (0.30, [0.4, -0.7, 1.2]), (1.70, [0.4, -0.7, 1.2]), (1.76, [0.4, -0.7, 1.6]), (1.84, [0.4, -0.75, 1.2]),
                 (1.95, [0.4, -1.0, 1.2]), (2.06, [0.4, -0.7, 1.2]), (2.7, ZERO)):
        a.pos("rifle", t, v)
    for t, v in ((0.0, ZERO), (0.30, [-6.0, 3.0, -14.0]), (0.40, [-6.2, 3.0, -14.2]), (0.64, [-7.0, 3.4, -15.0]), (1.0, [-6.5, 3.2, -14.5]),
                 (1.68, [-5.5, 3.0, -13.5]), (1.76, [-4.0, 2.8, -13.0]), (1.84, [-6.0, 3.0, -14.0]), (1.95, [-6.8, 3.0, -14.5]),
                 (2.06, [-6.0, 3.0, -14.0]), (2.7, ZERO)):
        a.rot("rifle", t, v)


a = Anim("reload", 2.9, hidden=HIDDEN)
reload_mag(a)
a.pos("rifle", 2.9, ZERO).rot("rifle", 2.9, ZERO).pos("left_hand", 2.9, ZERO)
anims.append(a)

# ---- reload + chamber a round ----
a = Anim("reload_chamber", 4.0, hidden=HIDDEN)
reload_mag(a)
work_bolt(a, 2.7)
a.pos("rifle", 4.0, ZERO).rot("rifle", 4.0, ZERO).pos("left_hand", 4.0, ZERO).pos("magazine", 4.0, ZERO)
anims.append(a)

write(RES, "bolt_rifle", "animation.bolt_rifle.", anims)
