"""Parametric animations for rifles and carbines (reciprocating bolt + detachable magazine).

Every number a gun needs is in a cfg dict; see gun_*.py for examples.  Reload timing is expressed as
fractions of the magazine-swap duration so the Java sound cues (Guns.java) can use the same fractions:

    F_RELEASE 0.27  magazine release pressed        F_INSERT 0.80  new magazine reaches the well
    F_PULL    0.40  old magazine pulled clear       F_SEAT   0.86  magazine seats
"""
from animlib import Anim, write, SMOOTH, SNAP, FALL, STEP, ZERO, ONE

# Magazine-swap phase fractions of the reload length.  "legacy" = the original timing (kept for the M14, whose reload awaits video-based
# refinement); "pb" = moved earlier so the mag-out/mag-in land nearer the benchmarks in the Point Blank dossier (28: mag-out 8-11 %, mag-in
# 33-39 % of a median 2.5 s reload; ours cannot go that early because the old magazine has to fall out of view first) and the last quarter is a
# settle.  Java `rifleCues` mirrors RELEASE / PULL / INSERT.
TIMING = {
    "legacy": (0.14, 0.27, 0.40, 0.47, 0.58, 0.70, 0.80, 0.86, 0.91, 1.0, 0.95),
    "pb": (0.08, 0.20, 0.30, 0.36, 0.46, 0.58, 0.68, 0.74, 0.80, 1.0, 0.90),
}
F_REACH, F_RELEASE, F_PULL, F_OUT, F_POUCH, F_APPROACH, F_INSERT, F_SEAT, F_TUG, F_END, F_BACK = TIMING["pb"]


def ease_sine(s):
    import math
    s = min(max(s, 0.0), 1.0)
    return 0.5 - 0.5 * math.cos(math.pi * s)


def v(*a):
    return list(a)


def flash(a, size):
    size = size * 0.55                                  # subtle: it sits right in front of the camera
    a.key("muzzle_flash", "scale", 0.0, ZERO, STEP).key("muzzle_flash", "scale", 0.008, [size * .8] * 3, STEP)
    a.key("muzzle_flash", "scale", 0.025, [size] * 3, STEP).key("muzzle_flash", "scale", 0.05, ZERO, STEP)


def hidden_bones(c):
    return ("casing", "muzzle_flash") + (("chamber_round",) if c.get("round") else ())


def fire(c, last):
    T = c["fire_len"]
    cyc = c["cycle"]
    a = Anim("fire_last" if last else "fire", T, hidden=hidden_bones(c))
    flash(a, c["flash"])
    k, p, y = c["kick_z"], c["kick_pitch"], c["kick_yaw"]
    a.pos("rifle", 0.0, ZERO).pos("rifle", 0.03, v(0, 0.12 * k, k), SNAP).pos("rifle", 0.12, v(0, 0.05 * k, 0.35 * k))
    a.pos("rifle", T, ZERO)
    a.rot("rifle", 0.0, ZERO).rot("rifle", 0.03, v(-p, y, 0.3 * y), SNAP).rot("rifle", 0.13, v(-0.3 * p, 0.3 * y, 0))
    a.rot("rifle", T, ZERO)
    tr = c["bolt_travel"]
    a.pos("bolt", 0.0, ZERO).pos("bolt", cyc * 0.4, v(0, 0, tr), SNAP)
    if last:
        a.pos("bolt", T, v(0, 0, tr), STEP)
    else:
        a.pos("bolt", cyc, ZERO, FALL)
    # ejected case: out of the port, up and back, then falls
    ex = c.get("eject", (-1.0, 1.0, 0.8))
    a.show("casing", 0.02, T - 0.02, fade=0.01)
    a.pos("casing", 0.02, ZERO, SNAP)
    a.pos("casing", 0.06, v(ex[0] * 3.0, ex[1] * 2.4, ex[2] * 2.6), SNAP)
    a.pos("casing", 0.13, v(ex[0] * 6.0, ex[1] * 3.2, ex[2] * 6.0))
    a.pos("casing", T, v(ex[0] * 8.5, ex[1] * c.get("eject_fall", -3.5), ex[2] * 9.0), FALL)
    a.rot("casing", 0.02, ZERO).rot("casing", T, v(0, 0, 420 * ex[0]))
    return a


def dry(c):
    a = Anim("dryfire", 0.3, hidden=hidden_bones(c))
    a.pos("rifle", 0.0, ZERO).pos("rifle", 0.04, v(0, 0, 0.35), SNAP).pos("rifle", 0.26, ZERO)
    return a


def dry_open(c):
    a = dry(c)
    a.name = "dryfire_open"
    tr = c["bolt_travel"]
    a.pos("bolt", 0.0, v(0, 0, tr), STEP).pos("bolt", 0.3, v(0, 0, tr), STEP)
    return a


def idle(c):
    a = Anim("idle", 4.0, loop=True, hidden=hidden_bones(c))
    a.pos("rifle", 0.0, ZERO).pos("rifle", 2.0, v(0, 0.08, 0.05)).pos("rifle", 4.0, ZERO)
    a.rot("rifle", 0.0, ZERO).rot("rifle", 1.0, v(0.25, 0, 0.3)).rot("rifle", 3.0, v(-0.25, 0, -0.3)).rot("rifle", 4.0, ZERO)
    return a


def idle_open(c):
    """Bolt locked back on an empty magazine: same breathing as idle, bolt held at full travel (exactly the last pose of fire_last)."""
    a = idle(c)
    a.name = "idle_open"
    tr = c["bolt_travel"]
    a.pos("bolt", 0.0, v(0, 0, tr), STEP).pos("bolt", 4.0, v(0, 0, tr), STEP)
    return a


DRAW_LEN = 0.60
INSPECT_LEN = 4.0


def draw_keys(a):
    """Gun brought up from below and the shooter's right, a small overshoot, then it settles at the rest pose.  Only the root bone moves
    (both hands ride on it), so there are still exactly two hands and nothing is scaled.  Length 0.60 s, inside the 0.57-2.95 s envelope of the
    Point Blank dossier (02; reference only)."""
    T = DRAW_LEN
    # gentle: the game's own re-equip already lifts the gun from below the screen, so this only adds a "bring it to the ready" motion
    a.pos("rifle", 0.0, v(0.8, -4.5, 1.5)).pos("rifle", 0.50 * T, v(-0.1, 0.5, -0.5)).pos("rifle", 0.78 * T, v(0, -0.15, 0.1)).pos("rifle", T, ZERO)
    a.rot("rifle", 0.0, v(12.0, 4.0, -5.0)).rot("rifle", 0.50 * T, v(-2.0, -0.6, 0.8)).rot("rifle", 0.78 * T, v(0.5, 0, -0.2)).rot("rifle", T, ZERO)
    return a


def inspect_keys(a):
    """Showpiece: the gun is brought toward the camera and turned one way, then the other, then settles.  Root bone only (hands ride on it)."""
    P = [(0.0, (0, 0, 0), (0, 0, 0)), (0.6, (-1.5, 1.5, 2.5), (-6, 28, -14)), (1.6, (-1.6, 1.7, 2.6), (-8, 33, -17)),
         (2.2, (0.5, 1.5, 2.5), (-4, -26, 12)), (3.1, (0.6, 1.6, 2.6), (-5, -31, 15)), (3.6, (0, 0.5, 0.5), (-1, 0, 0)), (INSPECT_LEN, (0, 0, 0), (0, 0, 0))]
    for t, pp, rr in P:
        a.pos("rifle", t, v(*pp)).rot("rifle", t, v(*rr))
    return a


def inspect(c, opened=False):
    a = Anim("inspect_open" if opened else "inspect", INSPECT_LEN, hidden=hidden_bones(c))
    inspect_keys(a)
    tr = c["bolt_travel"]
    if opened:
        a.pos("bolt", 0.0, v(0, 0, tr), STEP).pos("bolt", INSPECT_LEN, v(0, 0, tr), STEP)
    else:                                              # press-check: the bolt is eased back a little and let go
        a.pos("bolt", 0.0, ZERO).pos("bolt", 2.4, ZERO).pos("bolt", 2.7, v(0, 0, tr * 0.4)).pos("bolt", 3.0, v(0, 0, tr * 0.4)).pos("bolt", 3.12, ZERO, SNAP)
        a.pos("bolt", INSPECT_LEN, ZERO)
    return a


def draw(c, opened=False):
    a = Anim("draw_open" if opened else "draw", DRAW_LEN, hidden=hidden_bones(c))
    draw_keys(a)
    if opened:                                        # bolt locked back (empty magazine): stays at full travel through the draw
        tr = c["bolt_travel"]
        a.pos("bolt", 0.0, v(0, 0, tr), STEP).pos("bolt", DRAW_LEN, v(0, 0, tr), STEP)
    return a


def mag_swap(a, c, D, end_hand):
    """Magazine change over D seconds. `end_hand` is the support-hand offset to finish on (rest = ZERO).
    The hand swings out to the gun's left side (route_x) so it never passes through the receiver."""
    F_REACH, F_RELEASE, F_PULL, F_OUT, F_POUCH, F_APPROACH, F_INSERT, F_SEAT, F_TUG, F_END, F_BACK = TIMING[c.get("swap", "pb")]
    t = lambda f: round(D * f, 3)
    hy, hz = c["hand_l"]
    gy, gz = c["mag_grip"]
    gx = c.get("grip_x", 0.0)
    rx = c.get("route_x", 3.4)
    d = v(gx, gy - hy, gz - hz)                     # support hand on the magazine
    pull = list(c.get("mag_out", v(0, -c["mag_drop"], 0)))
    L = max(1e-6, sum(p * p for p in pull) ** 0.5)
    u = [p / L for p in pull]
    add = lambda p, q: [p[i] + q[i] for i in range(3)]
    sub = lambda p, q: [p[i] - q[i] for i in range(3)]
    sc = lambda p, k: [p[i] * k for i in range(3)]
    out = add(add(d, pull), add(sc(u, 3.5), v(0.6, 0, 1.0)))
    pouch = v(c.get("pouch_x", 3.0), d[1] + pull[1] - 30, d[2] + 3)
    if "pouch_off" in c:
        pouch = add(d, [c["pouch_off"][0], c["pouch_off"][1] - 16, c["pouch_off"][2]])
    app = add(d, sc(u, L + 2.5))
    seat0 = add(d, sc(u, 1.2))
    swing = v(rx, d[1] * 0.5, d[2] * 0.5)
    H = [(0.0, ZERO, SMOOTH), (F_REACH * 0.55, swing, SMOOTH), (F_RELEASE - 0.06, add(d, v(0, -1.0 if u[1] < -0.5 else 0.0, 0)), SMOOTH),
         (F_RELEASE - 0.01, d, SMOOTH), (F_PULL, add(d, pull), SMOOTH), (F_OUT, out, SMOOTH),
         (F_POUCH, pouch, SMOOTH), (F_APPROACH, app, SMOOTH), (F_INSERT, seat0, SMOOTH),
         (F_SEAT, sub(d, sc(u, 0.3)), SNAP), (F_TUG, sub(d, sc(u, -0.5)), SMOOTH)]
    for f, vec, e in H:
        a.pos("left_hand", t(f), vec, e)
    back = v(rx, d[1] * 0.5, d[2] * 0.5)
    a.pos("left_hand", t(F_BACK), back, SMOOTH)
    a.pos("left_hand", t(0.995), end_hand, SMOOTH)
    # old magazine: with the hand until it is pulled clear, then gone
    # the magazine rides in the support hand all the way down out of view and back up (never hidden / shown)
    # old magazine: drawn out with the hand, then DROPPED / flipped away - it falls (tumbling) fully out of the bottom of the view.  While it is
    # far out of view the same bone is moved to the belt, and the hand brings it back up as the new magazine (never toggled in view).
    t_drop = t(F_PULL)
    DUR = 0.52
    t_tele = max(t_drop + DUR + 0.04, t(F_POUCH))
    vx, vy, vz, grav = -14.0, -60.0, -8.0, 900.0                       # flicked clear of the hand (right / forward), then gravity
    a.pos("magazine", 0.0, ZERO).pos("magazine", t(F_RELEASE), ZERO)
    a.pos("magazine", t_drop, pull, SMOOTH)
    n = int(round(DUR * 30))
    for i in range(1, n + 1):
        tau = DUR * i / n
        p = [pull[0] + vx * tau * 0.6, pull[1] + vy * tau - 0.5 * grav * tau * tau, pull[2] + vz * tau * 0.6 + c.get("drop_z", 0.0)]
        a.pos("magazine", t_drop + tau, p, STEP)
        r = ease_sine(tau / DUR)
        a.rot("magazine", t_drop + tau, v(-540.0 * r, 25.0 * r, 160.0 * r), STEP)
    last = [pull[0] + vx * DUR * 0.6, pull[1] + vy * DUR - 0.5 * grav * DUR * DUR, pull[2] + vz * DUR * 0.6]
    a.pos("magazine", t_tele - 0.001, last, STEP)
    a.rot("magazine", t_tele - 0.001, v(-540.0, 25.0, 160.0), STEP).rot("magazine", t_tele, ZERO, STEP)
    a.pos("magazine", t_tele, sub(pouch, d), STEP)
    a.pos("magazine", t(F_APPROACH), sub(app, d))
    a.pos("magazine", t(F_INSERT), sub(seat0, d)).pos("magazine", t(F_SEAT), sc(u, -0.3), SNAP)
    a.pos("magazine", t(F_TUG), ZERO).pos("magazine", D, ZERO)
    rock = c.get("mag_rock", 0)
    a.rot("magazine", 0.0, ZERO).rot("magazine", t(F_RELEASE), ZERO).rot("magazine", t_drop, ZERO, SMOOTH)
    if rock:                                         # front catch first, then rock the back in
        a.rot("magazine", t(F_APPROACH), v(-rock, 0, 0))
        a.rot("magazine", t(F_INSERT), v(-rock, 0, 0)).rot("magazine", t(F_SEAT), ZERO, SNAP)
    a.rot("magazine", D, ZERO)
    # weight shift and cant while the support hand is busy
    # the gun is lifted into view for the swap (otherwise the magazine well and both hands sit below the bottom edge of the screen and the
    # magazine seems to vanish): raise = px that bring the magazine well to the lower middle of the first-person view
    rz = c.get("lift_px", 11.0)
    a.pos("rifle", 0.0, ZERO).pos("rifle", t(0.14), v(0, rz - 0.4, 0.3)).pos("rifle", t(0.9), v(0, rz - 0.4, 0.3)).pos("rifle", D, ZERO)
    a.rot("rifle", 0.0, ZERO).rot("rifle", t(0.18), v(0.8, 0, -6.0)).rot("rifle", t(0.88), v(0.8, 0, -6.0)).rot("rifle", D, ZERO)
    return d


def charge_left(a, c, t0, tr, start=None):
    """Left hand goes around the outside of the gun to the handle, pulls the bolt back and lets it fly forward."""
    hy, hz = c["hand_l"]
    hx, hyy, hzz = c["handle"]
    rx = c.get("route_x", 3.4)
    off = v(hx, hyy - hy - c.get("handle_below", 0), hzz - hz)
    back = [off[0], off[1], off[2] + tr]
    s = start or ZERO
    a.pos("left_hand", t0 + 0.05, v(rx, s[1], s[2]), SMOOTH)
    a.pos("left_hand", t0 + 0.16, v(rx, off[1], off[2]), SMOOTH)
    a.pos("left_hand", t0 + 0.22, off, SMOOTH).pos("left_hand", t0 + 0.26, off)
    a.pos("left_hand", t0 + 0.38, back, SNAP).pos("left_hand", t0 + 0.43, back)
    a.pos("left_hand", t0 + 0.5, off, SNAP).pos("left_hand", t0 + 0.56, v(rx, off[1], off[2]), SMOOTH)
    a.pos("left_hand", t0 + 0.68, v(rx, off[1] * 0.3, off[2] * 0.1), SMOOTH)
    a.pos("left_hand", t0 + 0.8, ZERO, SMOOTH)
    bone = c.get("charge_bone", "bolt")
    a.pos(bone, t0 + 0.26, ZERO).pos(bone, t0 + 0.38, v(0, 0, tr), SNAP).pos(bone, t0 + 0.43, v(0, 0, tr))
    a.pos(bone, t0 + 0.5, ZERO, SNAP)
    if bone != "bolt":
        a.pos("bolt", t0 + 0.26, ZERO).pos("bolt", t0 + 0.38, v(0, 0, tr), SNAP).pos("bolt", t0 + 0.43, v(0, 0, tr))
        a.pos("bolt", t0 + 0.5, ZERO, SNAP)
    return t0 + 0.8


def feed(a, c, tA, tB):
    """The next round lifts out of the magazine (hidden inside the receiver while it appears) and rides forward into the chamber with the bolt."""
    if not c.get("round"):
        return
    dz, dy = c["round"]
    a.show("chamber_round", tA, tB + 0.05, fade=0.02)
    a.pos("chamber_round", tA, v(0, dy, dz), SMOOTH).pos("chamber_round", tA + 0.07, v(0, 0, dz), SMOOTH)
    a.pos("chamber_round", tB, ZERO, SNAP).pos("chamber_round", tB + 0.05, ZERO)


def _rotz(deg):
    """JSON-space rotation GeckoLib applies for a z rotation key (x is mirrored)."""
    import math
    import numpy as np
    cs, sn = math.cos(math.radians(deg)), math.sin(math.radians(deg))
    S = np.diag([-1.0, 1, 1])
    return S @ np.array([[cs, -sn, 0], [sn, cs, 0], [0, 0, 1]]) @ S


def charge_right_roll(a, c, t0, tr, start_open=False):
    """Right hand reaches the handle, ROLLS palm-down so the curled fingers close round the handle (the handle passes through the fist), pulls
    the bolt back and lets it go, then returns to the grip.  The same single hand mesh the whole time (hard rule)."""
    import numpy as np
    W, vv, nn = (np.array(x, float) for x in c["hand_frame"])
    vv = vv / np.linalg.norm(vv)
    piv = np.array(c["hand_piv"], float)
    uu = np.cross(vv, nn)
    if uu[1] < 0:
        uu = -uu
    roll = 90.0
    for r in (90.0, -90.0):
        if (_rotz(r) @ nn)[1] < 0:
            roll = r
            break
    R = _rotz(roll)
    uc = 1.0 if (R @ uu)[0] > 0 else -1.0
    uc *= c.get("charge_u", 1.0)
    c0 = W + 3.7 * vv + 1.2 * nn + uc * uu
    Hg = np.array(c["handle_grip"], float)

    def hold(dz, roll_f=1.0):
        Rr = _rotz(roll * roll_f)
        return [round(float(x), 3) for x in (Hg + np.array([0, 0, dz]) - piv - Rr @ (c0 - piv))]

    def rotk(f):
        return [0, 0, round(roll * f, 3)]

    ease = lambda x: ease_sine(x)
    T_reach, T_grab = 0.26, 0.08
    tg = t0 + T_reach                         # hand on the handle
    pull = tr + (0.8 if start_open else 0.0)
    t_pull0 = tg + T_grab
    t_pull1 = t_pull0 + 0.20
    t_hold = t_pull1 + 0.05
    t_rel = t_hold + 0.10                     # bolt flies forward
    t_free = t_rel + 0.06
    t_home = t_free + 0.26
    arc = [-1.0, 1.4, 1.0]
    start_dz = tr if start_open else 0.0
    N = int(round((t_home - t0) * 30))
    from animlib import STEP
    if start_open:
        a.pos("bolt", t0, v(0, 0, tr), STEP)
    for i in range(N + 1):
        t = t0 + (t_home - t0) * i / N
        if t <= tg:                                   # reach (ease), rolling on the way
            s = ease((t - t0) / T_reach)
            p0, p1 = [0, 0, 0], hold(start_dz)
            import math
            bump = math.sin(math.pi * s)
            pos = [p0[k] + (p1[k] - p0[k]) * s + arc[k] * bump for k in range(3)]
            rot = rotk(ease(min(1.0, s * 1.25)))
            bz = start_dz
        elif t <= t_pull0:
            pos, rot, bz = hold(start_dz), rotk(1.0), start_dz
        elif t <= t_pull1:                            # pull back
            s = ease((t - t_pull0) / (t_pull1 - t_pull0))
            bz = start_dz + (pull - start_dz) * s if start_open else tr * s
            pos, rot = hold(bz), rotk(1.0)
        elif t <= t_hold:
            bz = pull if start_open else tr
            pos, rot = hold(bz), rotk(1.0)
        elif t <= t_rel:                              # let it fly forward, hand follows for a moment
            s = min(1.0, (t - t_hold) / (t_rel - t_hold))
            bz = (pull if start_open else tr) * (1 - s * s)
            pos, rot = hold(bz), rotk(1.0)
        elif t <= t_free:
            bz = 0.0
            pos, rot = hold(0.0), rotk(1.0)
        else:                                         # hand lets go and goes back to the grip
            s = ease((t - t_free) / (t_home - t_free))
            import math
            bump = math.sin(math.pi * s)
            p0 = hold(0.0)
            pos = [p0[k] * (1 - s) + arc[k] * bump for k in range(3)]
            rot = rotk(1 - ease(min(1.0, s * 1.4)))
            bz = 0.0
        a.key("right_hand", "position", t, [round(x, 3) for x in pos], STEP)
        a.key("right_hand", "rotation", t, rot, STEP)
        if t0 <= t <= t_free:
            a.key("bolt", "position", t, [0, 0, round(bz, 3)], STEP)
    feed(a, c, (tg + 0.12) if start_open else (t_pull0 + 0.05), t_rel + 0.04)
    return t_home


def charge_right(a, c, t0, tr, start_open=False):
    if c.get("charge_roll"):
        return charge_right_roll(a, c, t0, tr, start_open)
    """The (one) right hand lets go of the grip, travels to the handle, works it and travels back (HARD RULE: no extra hand)."""
    hy, hz = c["hand_r"]
    hx, hyy, hzz = c["handle"]
    off = v(hx - 0.25, hyy - (hy - 0.2), hzz + 0.1 - (hz + 1.15))
    zz = lambda p, dz: v(p[0], p[1], p[2] + dz)
    arc = v(off[0] - 1.2, off[1] + 1.0, off[2] * 0.5)
    t1, t2 = t0 + 0.12, t0 + (0.44 if not start_open else 0.3)
    a.pos("right_hand", t0, ZERO, SMOOTH)
    a.pos("right_hand", t0 + 0.07, arc, SMOOTH)
    if start_open:
        a.pos("bolt", t0, v(0, 0, tr))
        a.pos("right_hand", t0 + 0.14, zz(off, tr), SMOOTH)
        a.pos("bolt", t1 + 0.1, v(0, 0, tr + 0.8), SMOOTH).pos("bolt", t2 - 0.02, v(0, 0, tr + 0.8))
        a.pos("right_hand", t1 + 0.1, zz(off, tr + 0.8), SMOOTH).pos("right_hand", t2 - 0.02, zz(off, tr + 0.8))
        a.pos("bolt", t2 + 0.05, ZERO, SNAP)
        a.pos("right_hand", t2 + 0.05, off, SNAP)
    else:
        a.pos("right_hand", t1, off, SMOOTH)
        a.pos("bolt", t1, ZERO).pos("bolt", t1 + 0.15, v(0, 0, tr), SNAP).pos("bolt", t1 + 0.22, v(0, 0, tr))
        a.pos("right_hand", t1 + 0.15, zz(off, tr), SNAP).pos("right_hand", t1 + 0.22, zz(off, tr))
        a.pos("bolt", t2 + 0.04, ZERO, SNAP)
        a.pos("right_hand", t2 + 0.04, off, SNAP)
    a.pos("right_hand", t2 + 0.1, arc, SMOOTH).pos("right_hand", t2 + 0.2, ZERO, SMOOTH)
    feed(a, c, (t1 + 0.12) if start_open else (t1 + 0.2), t2 + (0.05 if start_open else 0.04))
    return t2 + 0.2


def reload(c, kind):
    D = c["reload_len"]
    if kind == "reload":
        T = D
    elif kind == "reload_chamber":
        T = D + c["charge_len"]
    else:
        T = D + c["release_len"]
    a = Anim(kind, round(T, 3), hidden=hidden_bones(c))
    tr = c["bolt_travel"]
    if kind == "reload":
        mag_swap(a, c, D, ZERO)
        return a
    def drop_return(D):                       # the hand goes on from the magazine instead of back to the forend
        pos = a.bones["left_hand"]["position"]
        for f in (0.95, 0.995):
            pos.pop(round(D * f, 3), None)
        gy, gz = c["mag_grip"]
        hy, hz = c["hand_l"]
        return v(c.get("grip_x", 0.0), gy - hy, gz - hz)

    if kind == "reload_chamber":
        if c["charge_hand"] == "left":
            mag_swap(a, c, D, ZERO)
            charge_left(a, c, D, tr, start=drop_return(D))
        else:
            mag_swap(a, c, D, ZERO)
            charge_right(a, c, D + 0.02, tr)
    else:
        a.pos("bolt", 0.0, v(0, 0, tr)).pos("bolt", D, v(0, 0, tr))
        if c["release_mode"] == "handle":
            mag_swap(a, c, D, ZERO)
            charge_right(a, c, D + 0.02, tr, start_open=True)
        else:                                   # press the bolt catch
            mag_swap(a, c, D, ZERO)
            hy, hz = c["hand_l"]
            cy, cz = c["catch"]
            rx = c.get("route_x", 3.4)
            s = drop_return(D)
            off = v(c.get("catch_x", 3.0), cy - hy, cz - hz)
            a.pos("left_hand", D + 0.05, v(rx, s[1], s[2]), SMOOTH)
            a.pos("left_hand", D + 0.14, v(rx, off[1], off[2]), SMOOTH)
            a.pos("left_hand", D + 0.19, off, SMOOTH).pos("left_hand", D + 0.25, v(off[0], off[1] - 0.5, off[2]), SNAP)
            a.pos("left_hand", D + 0.31, off, SMOOTH).pos("left_hand", D + 0.38, v(rx, off[1], off[2]), SMOOTH)
            a.pos("left_hand", D + 0.46, v(rx, off[1] * 0.3, off[2] * 0.1), SMOOTH)
            a.pos("left_hand", D + 0.54, ZERO, SMOOTH)
            a.pos("bolt", D + 0.22, v(0, 0, tr)).pos("bolt", D + 0.27, ZERO, SNAP)
    return a


def build(c, res, model_name):
    anims = [idle(c), dry(c), fire(c, False), draw(c), inspect(c)]
    if c.get("hold_open"):
        anims.append(draw(c, True))
        anims.append(inspect(c, True))
        anims.append(fire(c, True))
        anims.append(idle_open(c))
        anims.append(dry_open(c))
    anims.append(reload(c, "reload"))
    anims.append(reload(c, "reload_chamber"))
    if c.get("hold_open"):
        anims.append(reload(c, "reload_release"))
    write(res, model_name, "animation." + model_name + ".", anims)
    for an in anims:
        print("  %-15s %.2fs  = %d ticks" % (an.name, an.length, -(-an.length * 20 // 1)))
