"""FN P90 (5.7x28) - SDF mesh model traced from the reference side/top photos.
Body outline, trigger loop and thumbhole come from the photo (image coords -> px via P()); everything else is
rounded solids merged smoothly, then meshed + texture-baked by meshbake."""
import math
from meshbake import MModel, mid
from sdf import *

SY, SZ = 6.3, -6.3          # rear aperture centre (height above bore, z)
HW = 1.55


def P(x, Y):
    """Reference image (P90-2, 900px) -> (z, y) in model px."""
    return (-16 + (x - 12) / 28.0, (437 - Y) / 28.0)


def build():
    m = MModel("p90", lo=(-3.2, -7.0, -17.0), hi=(3.2, 8.2, 16.4), h=0.16, seed=71, tx=10)

    # ---------------------------------------------------------------- body: traced side outline, two openings
    outer = [P(*p) for p in [
        (88, 455), (88, 515), (112, 548), (140, 578), (190, 592), (235, 602), (300, 607), (360, 609), (430, 607),
        (500, 599), (560, 585), (610, 567), (655, 563), (856, 567), (876, 558), (881, 540), (881, 382), (872, 368),
        (625, 368), (618, 396), (560, 404), (88, 404)]]
    guard = [P(255 + 45 * math.cos(a), 512 + 33 * math.sin(a)) for a in [i * math.pi / 12 for i in range(24)]]
    thumb = [P(*p) for p in [(415, 515), (424, 488), (452, 467), (500, 460), (550, 468), (588, 492), (596, 530),
                             (584, 556), (540, 566), (480, 562), (440, 550), (418, 534)]]
    sil = Sil([(outer, [guard, thumb])], res=0.03)
    body = m.mesh("body", "rifle", (0, 0, 0), tris=14000)
    body.add(Ext(sil, "zy", -HW, HW, r=0.85), mat=mid("p90"))
    # front hood (rail housing) with side windows
    body.add(box(-1.62, 1.62, -1.2, 3.3, -12.2, -3.0, r=0.5), mat=mid("p90"))
    body.sub(box(-1.9, -1.42, 0.3, 2.5, -11.7, -9.4, r=0.2))
    body.sub(box(1.42, 1.9, 0.3, 2.5, -11.7, -9.4, r=0.2))
    # trough walls the magazine sits in
    body.add(box(-1.58, -1.22, 1.0, 1.9, -11.4, 5.4, r=0.1), mat=mid("p90"))
    body.add(box(1.22, 1.58, 1.0, 1.9, -11.4, 5.4, r=0.1), mat=mid("p90"))
    # rail base + teeth
    body.add(box(-1.3, 1.3, 3.2, 3.75, -12.4, -3.0, r=0.08), mat=mid("black"))
    for i in range(11):
        z0 = -12.1 + i * 0.85
        body.add(box(-1.32, 1.32, 3.7, 4.2, z0, z0 + 0.46, r=0.06), mat=mid("black"))
    # strap over the magazine
    body.add(box(-1.5, 1.5, 3.3, 3.8, -4.7, -3.4, r=0.1), mat=mid("black"))
    for sx in (-1, 1):
        body.add(box(sx * 1.66 - 0.13, sx * 1.66 + 0.13, 0.9, 3.6, -4.7, -3.4, r=0.1), mat=mid("black"))
    # flip-up iron sights (raised)
    body.add(box(-1.0, 1.0, 4.1, 4.6, -7.5, -5.8, r=0.1), mat=mid("gunmetal"))
    for sx in (-1, 1):
        body.add(box(sx * 0.78 - 0.28, sx * 0.78 + 0.28, 4.5, SY + 0.85, -7.1, -6.0, r=0.12), mat=mid("black"))
    body.add(box(-0.62, 0.62, 4.5, SY - 0.55, -6.9, -6.1, r=0.1), mat=mid("black"))
    body.add(box(-0.62, 0.62, SY + 0.45, SY + 0.9, -6.9, -6.1, r=0.1), mat=mid("black"))
    body.add(Cyl((0.85, SY, -6.45), (1.75, SY, -6.45), 0.5, rr=0.08), mat=mid("black"))              # windage drum
    body.add(box(-1.0, 1.0, 4.1, 4.5, -12.0, -10.4, r=0.1), mat=mid("gunmetal"))
    for sx in (-1, 1):
        body.add(box(sx * 0.8 - 0.28, sx * 0.8 + 0.28, 4.4, SY + 0.9, -11.9, -10.6, r=0.12), mat=mid("black"))
    body.add(box(-0.26, 0.26, 4.4, SY + 0.05, -11.6, -10.9, r=0.08), mat=mid("black"))
    body.add(box(-0.85, 0.85, SY + 0.6, SY + 0.9, -11.8, -10.6, r=0.05), mat=mid("black"))
    # butt cap
    body.add(box(-1.5, 1.5, -4.55, 2.55, 14.8, 15.4, r=0.35), mat=mid("rubber"))
    # trigger loop details + cross-bolt selector
    body.add(Cyl((-1.9, -4.5, -5.8), (1.9, -4.5, -5.8), 0.28, rr=0.05), mat=mid("black"))
    # screws (painted)
    for zz, yy in ((-4.0, -3.6), (-0.6, -5.4), (6.4, -3.3), (12.0, -3.6), (13.2, 1.4), (-10.6, -2.2), (-8.4, -4.7), (2.6, 1.6)):
        body.paint(Cyl((-2.0, yy, zz), (2.0, yy, zz), 0.22), "stainless")
    # moulded panel lines / markings
    body.paint(box(-2, 2, -0.2, -0.1, -9.0, 4.5), "black")
    body.paint(box(-2, 2, -1.4, -1.25, 5.8, 13.4), "black")

    # ---------------------------------------------------------------- barrel + ported brake
    bar = m.mesh("barrel", "rifle", (0, 0, 0), tris=2200)
    bar.add(cylz(0, 0, -16.0, -11.0, 0.5), mat=mid("steel"))
    bar.add(cylz(0, 0, -16.0, -13.3, 0.74, rr=0.1), mat=mid("steel"))
    bar.add(cylz(0, 0, -13.5, -12.9, 0.86, rr=0.1), mat=mid("gunmetal"))
    for i in range(2):
        bar.sub(box(-1.0, 1.0, -0.2, 0.2, -15.1 + i * 0.7, -14.75 + i * 0.7))
    bar.sub(cylz(0, 0, -16.2, -15.4, 0.32))

    # ---------------------------------------------------------------- twin charging handles
    ch = m.mesh("charge", "rifle", (0, 0.2, -10.5), tris=1200)
    for sx in (-1, 1):
        ch.add(box(sx * 1.45 - 0.0, sx * 2.7, -0.7, 0.8, -11.6, -9.4, r=0.3), mat=mid("gunmetal"))
        ch.add(box(sx * 2.3, sx * 2.8, -0.9, 1.0, -11.8, -9.2, r=0.2), mat=mid("black"))

    # ---------------------------------------------------------------- amber translucent magazine
    mg = m.mesh("magazine", "rifle", (0, 1.8, 0.0), tris=2600)
    mg.add(box(-1.3, 1.3, 1.05, 2.65, -11.4, 5.8, r=0.4), mat=mid("amber"))
    mg.add(box(-1.34, 1.34, 1.0, 2.7, -11.5, -10.9, r=0.15), mat=mid("black"))
    mg.add(box(-1.34, 1.34, 1.0, 2.7, 5.3, 5.95, r=0.15), mat=mid("black"))
    for i in range(13):
        zz = -10.4 + i * 1.25
        mg.paint(box(-1.5, 1.5, 1.55, 2.2, zz, zz + 0.75), "brass")
    mg.paint(box(-0.9, 0.9, 2.5, 2.8, -10.5, 4.8), "black")

    # ---------------------------------------------------------------- bolt (underside ejection) + cube parts kept from before
    m.bone("bolt", "rifle", (0, 0, 0))
    m.cube("bolt", "stainless", -0.4, -4.48, 7.2, 0.4, -4.4, 10.8)
    m.muzzle_flash(-16.2, length=4.4, width=3.0)
    m.casing(0.0, -4.5, 9.0, length=2.0, r=0.38)
    m.hand_left(-4.6, -11.0)
    m.hand_right(-5.2, -3.6, -2.7)

    cfg = dict(
        name="p90", hand_l=(-4.6, -11.0), mag_grip=(2.0, 5.0), mag_drop=0.0, mag_rock=0,
        grip_x=3.6, route_x=3.8, mag_out=(0, 0.0, 13.5), pouch_off=(2.0, -14.0, 17.0),
        charge_hand="left", charge_bone="charge", handle=(2.9, 0.2, -10.5), bolt_travel=4.2,
        hold_open=True, release_mode="press", catch=(0.3, -9.0), catch_x=3.4,
        fire_len=0.2, cycle=0.05, kick_z=0.9, kick_pitch=1.2, kick_yaw=0.35, flash=0.8,
        reload_len=2.4, charge_len=0.95, release_len=0.6, eject=(0.0, -4.5, 0.25), eject_fall=3.0,
        sight=(SY, SZ), butt=15.35,
    )
    return m, cfg
