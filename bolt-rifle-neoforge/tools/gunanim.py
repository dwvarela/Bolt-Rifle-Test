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
    h = ["casing", "muzzle_flash"]
    if c["charge_hand"] == "right":
        h.append("bolt_hand")
    return tuple(h)


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
    """Magazine change over D seconds. `end_hand` is the support-hand offset to finish on (rest = ZERO)."""
    t = lambda f: round(D * f, 3)
    hy, hz = c["hand_l"]
    gy, gz = c["mag_grip"]
    d = v(0, gy - hy, gz - hz)                      # support hand on the magazine
    drop = c["mag_drop"]
    pouch = v(c.get("pouch_x", 3.0), d[1] - drop - 7, d[2] + 3)
    if "pouch_off" in c:
        pouch = [d[i] + c["pouch_off"][i] for i in range(3)]
    app = v(0.0, d[1] - drop - 2.5, d[2])
    add = lambda p, q: [p[i] + q[i] for i in range(3)]
    H = [(0.0, ZERO, SMOOTH), (F_REACH, add(d, v(0, -1.0, 0)), SMOOTH), (F_RELEASE - 0.04, d, SMOOTH),
         (F_PULL, add(d, v(0, -drop, 0)), SMOOTH), (F_OUT, add(d, v(0.6, -drop - 3.5, 1.0)), FALL),
         (F_POUCH, pouch, SMOOTH), (F_APPROACH, app, SMOOTH), (F_INSERT, add(d, v(0, -1.2, 0)), SMOOTH),
         (F_SEAT, add(d, v(0, 0.3, 0)), SNAP), (F_TUG, add(d, v(0, -0.5, 0)), SMOOTH)]
    for f, vec, e in H:
        a.pos("left_hand", t(f), vec, e)
    a.pos("left_hand", t(0.97), end_hand, SMOOTH)
    # old magazine: with the hand until it is pulled clear, then gone
    a.show("magazine", 0.0).key("magazine", "scale", t(F_OUT), ONE, STEP).key("magazine", "scale", t(F_OUT) + 0.01, ZERO, STEP)
    a.key("magazine", "scale", t(F_POUCH) - 0.02, ZERO, STEP).key("magazine", "scale", t(F_POUCH), ONE, STEP)
    sub = lambda p, q: [p[i] - q[i] for i in range(3)]
    a.pos("magazine", 0.0, ZERO).pos("magazine", t(F_RELEASE), ZERO)
    a.pos("magazine", t(F_PULL), v(0, -drop, 0), FALL).pos("magazine", t(F_OUT), v(0.6, -drop - 3.5, 1.0), FALL)
    a.pos("magazine", t(F_POUCH), sub(pouch, d)).pos("magazine", t(F_APPROACH), sub(app, d))
    a.pos("magazine", t(F_INSERT), v(0, -1.2, 0)).pos("magazine", t(F_SEAT), v(0, 0.3, 0), SNAP)
    a.pos("magazine", t(F_TUG), ZERO).pos("magazine", D, ZERO)
    rock = c.get("mag_rock", 0)
    a.rot("magazine", 0.0, ZERO).rot("magazine", t(F_RELEASE), ZERO)
    if rock:                                         # front catch first, then rock the back in
        a.rot("magazine", t(F_POUCH), v(-rock * 0.5, 0, 0)).rot("magazine", t(F_APPROACH), v(-rock, 0, 0))
        a.rot("magazine", t(F_INSERT), v(-rock, 0, 0)).rot("magazine", t(F_SEAT), ZERO, SNAP)
    a.rot("magazine", D, ZERO)
    # weight shift and cant while the support hand is busy
    a.pos("rifle", 0.0, ZERO).pos("rifle", t(0.14), v(0, -0.4, 0.3)).pos("rifle", t(0.9), v(0, -0.4, 0.3))
    a.rot("rifle", 0.0, ZERO).rot("rifle", t(0.18), v(0.8, 0, -6.0)).rot("rifle", t(0.88), v(0.8, 0, -6.0))
    return d


def charge_left(a, c, t0, tr):
    """Left hand reaches to the handle, pulls the bolt back and lets it fly forward. Returns end time."""
    hy, hz = c["hand_l"]
    hx, hyy, hzz = c["handle"]
    off = v(hx, hyy - hy - c.get("handle_below", 0), hzz - hz)
    back = [off[0], off[1], off[2] + tr]
    a.pos("left_hand", t0 + 0.14, off, SMOOTH).pos("left_hand", t0 + 0.2, off)
    a.pos("left_hand", t0 + 0.34, back, SNAP).pos("left_hand", t0 + 0.4, back)
    a.pos("left_hand", t0 + 0.46, off, SNAP).pos("left_hand", t0 + 0.7, ZERO, SMOOTH)
    bone = c.get("charge_bone", "bolt")
    a.pos(bone, t0 + 0.2, ZERO).pos(bone, t0 + 0.34, v(0, 0, tr), SNAP).pos(bone, t0 + 0.4, v(0, 0, tr))
    a.pos(bone, t0 + 0.46, ZERO, SNAP)
    if bone != "bolt":
        a.pos("bolt", t0 + 0.2, ZERO).pos("bolt", t0 + 0.34, v(0, 0, tr), SNAP).pos("bolt", t0 + 0.4, v(0, 0, tr))
        a.pos("bolt", t0 + 0.46, ZERO, SNAP)
    return t0 + 0.7


def charge_right(a, c, t0, tr, start_open=False):
    """Right hand lets go of the grip, works the handle, and returns."""
    t1, t2 = t0 + 0.12, t0 + (0.44 if not start_open else 0.3)
    a.hand_swap(t0 + 0.05, t2 + 0.1)
    if start_open:
        a.pos("bolt", t0, v(0, 0, tr))
        a.pos("bolt", t1 + 0.1, v(0, 0, tr + 0.8), SMOOTH).pos("bolt", t2 - 0.02, v(0, 0, tr + 0.8))
        a.pos("bolt", t2 + 0.05, ZERO, SNAP)
    else:
        a.pos("bolt", t1, ZERO).pos("bolt", t1 + 0.15, v(0, 0, tr), SNAP).pos("bolt", t1 + 0.22, v(0, 0, tr))
        a.pos("bolt", t2 + 0.04, ZERO, SNAP)
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
        if c["charge_hand"] == "right":
            a.key("right_hand", "scale", 0.0, ONE)
        return a
    if kind == "reload_chamber":
        if c["charge_hand"] == "left":
            mag_swap(a, c, D, ZERO)       # placeholder; hand is re-keyed below
            hy, hz = c["hand_l"]
            # replace the final return with the trip to the handle
            gy, gz = c["mag_grip"]
            d = v(0, gy - hy, gz - hz)
            end = a.bones["left_hand"]["position"]
            end.pop(round(D * 0.97, 3), None)
            a.pos("left_hand", round(D * 0.97, 3), v(d[0], d[1] + 0.6, d[2]), SMOOTH)
            charge_left(a, c, D + 0.0, tr)
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
            off = v(c.get("catch_x", 0), cy - hy, cz - hz)
            a.pos("left_hand", D + 0.12, off, SMOOTH).pos("left_hand", D + 0.2, v(off[0], off[1] - 0.5, off[2]), SNAP)
            a.pos("left_hand", D + 0.3, off, SMOOTH).pos("left_hand", D + 0.5, ZERO, SMOOTH)
            a.pos("bolt", D + 0.18, v(0, 0, tr)).pos("bolt", D + 0.24, ZERO, SNAP)
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
