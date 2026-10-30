"""M700 animations.  Usage: gen_m700_anim.py <resources_dir>
HARD RULE (CLAUDE.md): exactly two hands.  The right hand travels from the grip to the bolt knob and back - it is rigidly attached to
the knob while it turns the handle and works the bolt.  The magazine is carried down out of view by the support hand and the (new)
magazine comes back up and is seated; nothing is ever scaled to hide / show a hand or a magazine."""
import sys, math
import numpy as np
from animlib import Anim, write, SMOOTH, SNAP, FALL, STEP, ZERO, ONE

RES = sys.argv[1]
HIDDEN = ("casing", "chamber_round", "muzzle_flash")
LIFT = 75.0                      # handle rotation (+z lifts the right-hand side)
BACK = 5.6                       # bolt travel in px
PIV_H = np.array([0.0, 0.0, 5.0])          # bolt_handle pivot (axis along z through x=0,y=0)
PIV_R = np.array([0.0, -4.3, 8.6])         # right_hand pivot
W_GRIP = np.array([-1.45, -2.3, 13.4])     # right glove wrist when gripping
V_G, N_G = np.array([0, -0.28, -0.96]), np.array([1.0, 0, 0])
KNOB = np.array([-2.6, -1.2, 4.5])         # ball knob, handle down
FPS = 30.0
anims = []


def rotz(deg):                   # the game/JSON-space rotation used by GeckoLib for az (x/y not needed)
    c, s = math.cos(math.radians(deg)), math.sin(math.radians(deg))
    S = np.diag([-1.0, 1, 1])
    G = np.array([[c, -s, 0], [s, c, 0], [0, 0, 1]])
    return S @ G @ S


# glove frame of the grip hand (see gun_m700.glove): u = thumb side, v = wrist->fingers, n = out of the palm
U_G = np.cross(V_G, N_G)
if np.dot(U_G, [0, 1, 0]) < 0:
    U_G = -U_G
K75 = rotz(LIFT) @ (KNOB - np.array([0, 0, 0])) + np.zeros(3)
# hand rigidly holds the knob (handle raised): knob sits inside the curled fingers (4.0 along the hand, 1.1 off the palm, 0.5 across)
W_LIFT = K75 - 3.9 * V_G - 1.5 * N_G + 0.4 * U_G
T_LIFT = W_LIFT - W_GRIP


def hand_pose(theta, back=0.0, lift=(0, 0, 0)):
    """right_hand (position, rotation) when it holds the knob and the handle is at `theta` degrees and the bolt `back` px back."""
    Rd = rotz(theta - LIFT)
    pos = Rd @ T_LIFT + Rd @ PIV_R + np.array([0, 0, back]) - PIV_R + np.array(lift)
    return [round(float(x), 3) for x in pos], [0.0, 0.0, round(theta - LIFT, 3)]


def ease(s):
    s = min(max(s, 0.0), 1.0)
    return 0.5 - 0.5 * math.cos(math.pi * s)


def dense(a, t0, t1, fn, chans):
    """Sample fn(t) -> {(bone, channel): vector} every 1/30 s from t0..t1 as linear keys (so several bones move on one common curve)."""
    n = max(1, int(round((t1 - t0) * FPS)))
    for i in range(n + 1):
        t = t0 + (t1 - t0) * i / n
        for (bone, ch), vec in fn(t).items():
            a.key(bone, ch, t, vec, STEP)


def lerp(a_, b_, s):
    return [x + (y - x) * s for x, y in zip(a_, b_)]


def bolt_cycle(a, t0, eject=False):
    """One bolt cycle starting at t0 (1.3 s): hand reaches the knob, handle up, bolt back (round feeds), forward, handle down, hand returns."""
    T = lambda x: t0 + x
    tA, tL0, tL1, tB0, tB1, tF0, tF1, tD1, tR = 0.0, 0.24, 0.40, 0.40, 0.66, 0.72, 0.92, 1.05, 1.30

    def state(t):
        x = t - t0
        if x <= tL0:
            th, bk = 0.0, 0.0
        elif x <= tL1:
            th, bk = LIFT * ease((x - tL0) / (tL1 - tL0)), 0.0
        elif x <= tB1:
            th, bk = LIFT, BACK * ease((x - tB0) / (tB1 - tB0))
        elif x <= tF0:
            th, bk = LIFT, BACK
        elif x <= tF1:
            th, bk = LIFT, BACK * (1 - ease((x - tF0) / (tF1 - tF0)))
        elif x <= tD1:
            th, bk = LIFT * (1 - ease((x - tF1) / (tD1 - tF1))), 0.0
        else:
            th, bk = 0.0, 0.0
        return th, bk

    g_pos, g_rot = ZERO, ZERO
    p0, r0 = hand_pose(0.0)
    arc = [-1.2, 1.2, -0.5]          # the hand swings out and up on its way to / from the knob

    def right(t):
        x = t - t0
        th, bk = state(t)
        if x < tL0:                                            # reach: grip -> knob
            s = ease(x / tL0)
            bump = math.sin(math.pi * s)
            pos = [p + a_ * bump for p, a_ in zip(lerp(g_pos, p0, s), arc)]
            return {("right_hand", "position"): pos, ("right_hand", "rotation"): lerp(g_rot, r0, s)}
        if x <= tD1:                                           # holding the knob
            pos, rot = hand_pose(th, bk)
            return {("right_hand", "position"): pos, ("right_hand", "rotation"): rot}
        s = ease((x - tD1) / (tR - tD1))                       # release: knob -> grip
        bump = math.sin(math.pi * s)
        pos = [p + a_ * bump for p, a_ in zip(lerp(p0, g_pos, s), arc)]
        return {("right_hand", "position"): pos, ("right_hand", "rotation"): lerp(r0, g_rot, s)}

    def bolt(t):
        th, bk = state(t)
        return {("bolt_handle", "rotation"): [0, 0, th], ("bolt", "position"): [0, 0, bk]}

    dense(a, T(0.0), T(tR), right, None)
    dense(a, T(tL0), T(tD1), bolt, None)
    a.rot("bolt_handle", T(0.0), ZERO, STEP).rot("bolt_handle", T(tL0), ZERO, STEP)
    a.pos("bolt", T(0.0), ZERO, STEP).pos("bolt", T(tL0), ZERO, STEP).pos("bolt", T(tD1), ZERO, STEP).rot("bolt_handle", T(tD1), ZERO, STEP)
    # the rifle is nudged by the work: tug when the handle breaks free, bump at the rear stop, slam forward
    for t, v in ((tL0, ZERO), (tL1, [0.15, 0, 0.5]), (tB1, [-0.3, 0, 0.9]), (tF0, [-0.2, 0, 0.6]), (tF1, [0.25, 0, -0.3]), (tD1, ZERO)):
        a.rot("rifle", T(t), v)
    for t, v in ((tL0, ZERO), (tL1, [0, 0, 0.05]), (tB1, [0, 0, 0.22]), (tF0, [0, 0, 0.18]), (tF1, [0, 0, -0.12]), (tD1, ZERO)):
        a.pos("rifle", T(t), v)
    # the next round rises from the magazine into the open action (hidden inside the receiver while it appears) and rides into the chamber
    t_in, t_up, t_push, t_seat, t_out = (T(x) for x in (0.64, 0.72, 0.78, 0.90, 0.95))
    a.show("chamber_round", t_in, t_out)
    a.pos("chamber_round", t_in, [0, -2.2, 1.4]).pos("chamber_round", t_up, [0, -0.5, 1.4])
    a.pos("chamber_round", t_push, [0, -0.5, 1.4]).pos("chamber_round", t_seat, [0, -0.5, -2.4]).pos("chamber_round", t_out, [0, -0.5, -2.4])
    if eject:                                              # the spent case leaves the port as the bolt comes back
        a.show("casing", T(0.50), T(0.96))
        a.pos("casing", T(0.50), ZERO, SNAP).pos("casing", T(0.58), [0, 3.4, 2.6]).pos("casing", T(0.68), [0, 4.4, 4.2], SMOOTH)
        a.pos("casing", T(0.94), [0, -3.2, 8.0], FALL)
        a.rot("casing", T(0.50), ZERO).rot("casing", T(0.94), [0, 0, 380])


def flash(a):
    a.key("muzzle_flash", "scale", 0.0, ZERO, STEP).key("muzzle_flash", "scale", 0.01, [0.5] * 3, STEP)
    a.key("muzzle_flash", "scale", 0.045, [0.65] * 3, STEP).key("muzzle_flash", "scale", 0.06, ZERO, STEP)


# ---- idle ----
a = Anim("idle", 4.0, loop=True, hidden=HIDDEN)
a.pos("rifle", 0.0, ZERO).pos("rifle", 2.0, [0, 0.05, 0.03]).pos("rifle", 4.0, ZERO)
a.rot("rifle", 0.0, ZERO).rot("rifle", 1.0, [0.12, 0, 0.15]).rot("rifle", 3.0, [-0.12, 0, -0.15]).rot("rifle", 4.0, ZERO)
anims.append(a)

# ---- draw (shared timing with the other guns, tools/gunanim.py) ----
import gunanim
a = Anim("draw", gunanim.DRAW_LEN, hidden=HIDDEN)
gunanim.draw_keys(a)
anims.append(a)

# ---- dry fire ----
a = Anim("dryfire", 0.3, hidden=HIDDEN)
a.pos("rifle", 0.0, ZERO).pos("rifle", 0.04, [0, 0, 0.45], SNAP).pos("rifle", 0.26, ZERO)
anims.append(a)

# ---- fire: kick, climb, settle while the bolt is worked ----
a = Anim("fire", 1.6, hidden=HIDDEN)
flash(a)
a.pos("rifle", 0.0, ZERO).pos("rifle", 0.04, [0, 0.35, 2.7], SNAP).pos("rifle", 0.2, [0, 0.12, 1.2])
a.rot("rifle", 0.0, ZERO).rot("rifle", 0.04, [-6.0, 0, 0.8], SNAP).rot("rifle", 0.24, [-2.2, 0, 0.3]).rot("rifle", 0.4, [-0.4, 0, 0])
bolt_cycle(a, 0.2, eject=True)
a.pos("rifle", 1.6, ZERO).rot("rifle", 1.6, ZERO)
anims.append(a)


def np_lerp(keys, t):
    for (t0, v0), (t1, v1) in zip(keys, keys[1:]):
        if t0 <= t <= t1:
            k = (t - t0) / (t1 - t0)
            return [x + (y - x) * k for x, y in zip(v0, v1)]
    return keys[-1][1]


def reload_mag(a):
    """Magazine swap 0 -> 2.7 s.  The support hand slides back under the magazine, presses the release (click), draws the magazine
    down and carries it away out of the bottom of the view; it comes back up with the fresh magazine (the magazine bone simply leaves and
    returns with the hand - it is never hidden), rocks it in, slaps the floor plate, and everything settles."""
    hand = [(0.0, [0, 0, 0]), (0.30, [0.8, -1.0, 9.5]), (0.34, [0, -0.9, 9.5]), (0.40, [0, -1.2, 9.5]), (0.62, [0, -5.2, 9.5]), (0.76, [0, -6.2, 9.5]),
            (0.90, [-5.5, -10.5, 8.5]), (1.02, [0.5, -22.0, 7.2]), (1.08, [3.8, -31.0, 6.5]), (1.12, [4.2, -32.0, 6.3]), (1.30, [2.4, -28.0, 8.5]),
            (1.52, [0.8, -9.5, 9.5]), (1.68, [0, -1.0, 9.5]), (1.76, [0, -0.5, 9.5]), (1.84, [0, -1.2, 9.5]), (1.95, [0, -0.4, 9.5]),
            (2.06, [0, -1.2, 9.5]), (2.30, [1.0, -1.8, 7.6]), (2.5, [1.0, -1.0, 3.0]), (2.7, [0, 0, 0])]
    for t, v in hand:
        a.pos("left_hand", t, v)
    for t, v in ((0.0, [0, 0, 0]), (0.30, [0, 0, 0]), (0.64, [-5, 0, 4]), (1.0, [-18, 0, 10]), (1.30, [-14, 0, 8]), (1.68, [-4, 0, 2]),
                 (1.8, [0, 0, 0]), (2.3, [0, 0, 0]), (2.7, [0, 0, 0])):
        a.rot("left_hand", t, v)
    # the old magazine is drawn out (0.40 -> 0.64), then DROPPED: it tumbles and falls fully out of the bottom of the view.  While it is far
    # below the view the same bone is moved to the belt (1.28, nothing is on screen) and the hand carries it back up as the new magazine.
    off = lambda v: [v[0], v[1] + 0.9, v[2] - 9.6]          # hand -> magazine offset while held
    hd = dict(hand)
    # drawn out of the well WITH the hand (0.40 -> 0.76, held visibly beside the grip), released at 0.76 (the hand slides away to the left),
    # then it falls under gravity with a slow tumble through the lower part of the view and out of the bottom.
    a.pos("magazine", 0.0, ZERO).pos("magazine", 0.32, ZERO).pos("magazine", 0.40, [0, -0.3, 0])
    for t in (0.50, 0.62, 0.70, 0.76):
        a.pos("magazine", t, off(hd[t]) if t in hd else off(np_lerp(hand, t)))
    a.rot("magazine", 0.0, ZERO).rot("magazine", 0.76, ZERO)
    p0 = off(hd[0.76])
    n, T = 16, 0.50
    for i in range(1, n + 1):
        tau = T * i / n
        p = [p0[0] - 9.0 * tau, p0[1] - 6.0 * tau - 150.0 * tau * tau, p0[2] + 2.0 * tau]
        a.pos("magazine", 0.76 + tau, p, STEP)
        r = 0.5 - 0.5 * math.cos(math.pi * i / n)
        a.rot("magazine", 0.76 + tau, [-300 * r, 20 * r, 90 * r], STEP)
    a.pos("magazine", 1.279, p, STEP).rot("magazine", 1.279, [-300, 20, 90], STEP).rot("magazine", 1.28, ZERO, STEP)
    a.pos("magazine", 1.28, off(hd[1.30]), STEP)
    for t, v in hand:
        if 1.30 <= t <= 1.68:
            a.pos("magazine", t, off(v))
    a.pos("magazine", 1.76, [0, 0.2, 0], SNAP).pos("magazine", 1.84, ZERO).pos("magazine", 2.7, ZERO)
    # rifle: rolls toward the support hand, tugs when the mag comes out, bumps when the new one seats, slaps down, settles
    RZ = 3.0                                              # lifted into view for the swap (mag well + hands inside the frame)
    for t, v in ((0.0, ZERO), (0.30, [0.4, RZ - 0.7, 1.2]), (1.70, [0.4, RZ - 0.7, 1.2]), (1.76, [0.4, RZ - 0.7, 1.6]), (1.84, [0.4, RZ - 0.75, 1.2]),
                 (1.95, [0.4, RZ - 1.0, 1.2]), (2.06, [0.4, RZ - 0.7, 1.2]), (2.7, ZERO)):
        a.pos("rifle", t, v)
    for t, v in ((0.0, ZERO), (0.30, [-6.0, 3.0, -14.0]), (0.40, [-6.2, 3.0, -14.2]), (0.64, [-7.0, 3.4, -15.0]), (1.0, [-6.5, 3.2, -14.5]),
                 (1.68, [-5.5, 3.0, -13.5]), (1.76, [-4.0, 2.8, -13.0]), (1.84, [-6.0, 3.0, -14.0]), (1.95, [-6.8, 3.0, -14.5]),
                 (2.06, [-6.0, 3.0, -14.0]), (2.7, ZERO)):
        a.rot("rifle", t, v)


a = Anim("reload", 2.9, hidden=HIDDEN)
reload_mag(a)
a.pos("rifle", 2.9, ZERO).rot("rifle", 2.9, ZERO).pos("left_hand", 2.9, ZERO)
anims.append(a)

a = Anim("reload_chamber", 4.1, hidden=HIDDEN)
reload_mag(a)
bolt_cycle(a, 2.7)
a.pos("rifle", 4.1, ZERO).rot("rifle", 4.1, ZERO).pos("left_hand", 4.1, ZERO).pos("magazine", 4.1, ZERO)
anims.append(a)

write(RES, "bolt_rifle", "animation.bolt_rifle.", anims)
