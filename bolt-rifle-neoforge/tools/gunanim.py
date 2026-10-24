"""Parametric animations for rifles and carbines (reciprocating bolt + detachable magazine).

Every number a gun needs is in a cfg dict; see gun_*.py for examples.  Reload timing is expressed as
fractions of the magazine-swap duration so the Java sound cues (Guns.java) can use the same fractions:

    F_RELEASE 0.27  magazine release pressed        F_INSERT 0.80  new magazine reaches the well
    F_PULL    0.40  old magazine pulled clear       F_SEAT   0.86  magazine seats
"""
from animlib import Anim, write, SMOOTH, SNAP, FALL, STEP, ZERO, ONE

F_REACH, F_RELEASE, F_PULL, F_OUT, F_POUCH, F_APPROACH, F_INSERT, F_SEAT, F_TUG, F_END = \
    0.14, 0.27, 0.40, 0.47, 0.58, 0.70, 0.80, 0.86, 0.91, 1.0


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


def idle(c):
    a = Anim("idle", 4.0, loop=True, hidden=hidden_bones(c))
    a.pos("rifle", 0.0, ZERO).pos("rifle", 2.0, v(0, 0.08, 0.05)).pos("rifle", 4.0, ZERO)
    a.rot("rifle", 0.0, ZERO).rot("rifle", 1.0, v(0.25, 0, 0.3)).rot("rifle", 3.0, v(-0.25, 0, -0.3)).rot("rifle", 4.0, ZERO)
    return a


def mag_swap(a, c, D, end_hand):
    """Magazine change over D seconds. `end_hand` is the support-hand offset to finish on (rest = ZERO).
    The hand swings out to the gun's left side (route_x) so it never passes through the receiver."""
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
    pouch = v(c.get("pouch_x", 3.0), d[1] + pull[1] - 7, d[2] + 3)
    if "pouch_off" in c:
        pouch = add(d, c["pouch_off"])
    app = add(d, sc(u, L + 2.5))
    seat0 = add(d, sc(u, 1.2))
    swing = v(rx, d[1] * 0.5, d[2] * 0.5)
    H = [(0.0, ZERO, SMOOTH), (F_REACH * 0.55, swing, SMOOTH), (F_RELEASE - 0.06, add(d, v(0, -1.0 if u[1] < -0.5 else 0.0, 0)), SMOOTH),
         (F_RELEASE - 0.01, d, SMOOTH), (F_PULL, add(d, pull), SMOOTH), (F_OUT, out, FALL),
         (F_POUCH, pouch, SMOOTH), (F_APPROACH, app, SMOOTH), (F_INSERT, seat0, SMOOTH),
         (F_SEAT, sub(d, sc(u, 0.3)), SNAP), (F_TUG, sub(d, sc(u, -0.5)), SMOOTH)]
    for f, vec, e in H:
        a.pos("left_hand", t(f), vec, e)
    back = v(rx, d[1] * 0.5, d[2] * 0.5)
    a.pos("left_hand", t(0.95), back, SMOOTH)
    a.pos("left_hand", t(0.995), end_hand, SMOOTH)
    # old magazine: with the hand until it is pulled clear, then gone
    # the magazine rides in the support hand all the way down out of view and back up (never hidden / shown)
    # old magazine: drawn out with the hand, then DROPPED / flipped away - it falls (tumbling) fully out of the bottom of the view.  While it is
    # far out of view the same bone is moved to the belt, and the hand brings it back up as the new magazine (never toggled in view).
    t_drop = t(F_PULL)
    t_gone = t_drop + 0.42
    t_tele = max(t_gone + 0.05, t(F_POUCH))
    fall = add(pull, v(c.get("drop_x", 1.5), -70.0, c.get("drop_z", 4.0)))
    a.pos("magazine", 0.0, ZERO).pos("magazine", t(F_RELEASE), ZERO)
    a.pos("magazine", t_drop, pull, SMOOTH).pos("magazine", t_gone, fall, FALL)
    a.pos("magazine", t_tele - 0.001, fall, STEP)
    pouch_rel = sub(pouch, d)
    a.pos("magazine", t_tele, pouch_rel, STEP)
    a.pos("magazine", t(F_APPROACH), sub(app, d))
    a.pos("magazine", t(F_INSERT), sub(seat0, d)).pos("magazine", t(F_SEAT), sc(u, -0.3), SNAP)
    a.pos("magazine", t(F_TUG), ZERO).pos("magazine", D, ZERO)
    rock = c.get("mag_rock", 0)
    a.rot("magazine", 0.0, ZERO).rot("magazine", t(F_RELEASE), ZERO).rot("magazine", t_drop, ZERO, SMOOTH)
    a.rot("magazine", t_gone, v(-540.0, 25.0, 160.0), FALL)             # flips end over end as it falls
    a.rot("magazine", t_tele - 0.001, v(-540.0, 25.0, 160.0), STEP).rot("magazine", t_tele, ZERO, STEP)
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


def charge_right(a, c, t0, tr, start_open=False):
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
    anims = [idle(c), dry(c), fire(c, False)]
    if c.get("hold_open"):
        anims.append(fire(c, True))
    anims.append(reload(c, "reload"))
    anims.append(reload(c, "reload_chamber"))
    if c.get("hold_open"):
        anims.append(reload(c, "reload_release"))
    write(res, model_name, "animation." + model_name + ".", anims)
    for an in anims:
        print("  %-15s %.2fs  = %d ticks" % (an.name, an.length, -(-an.length * 20 // 1)))
