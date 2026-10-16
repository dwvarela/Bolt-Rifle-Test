"""Optics + muzzle devices as SDF meshes, authored in real centimetres (the game scales them per gun).
Optic origin: centre of the mount base on the rail top, -Z forward.  Muzzle device origin: rear face on the bore axis (y=0), extends to -Z.
Shapes follow the reference sheets (Aimpoint-type red dot, EOTech-type holo, ACOG TA31, 1-6x scope, A2 birdcage, ported brake, can).
Usage: python3 gen_attachments.py <resources_dir> [ids]"""
import sys
from meshbake import MModel, mid
from sdf import *

TX = 14      # texels per cm


def dim(m_id, lo, hi, seed, h=0.11):
    return MModel(m_id, lo=lo, hi=hi, h=h, seed=seed, tx=TX)


def clamp_rail(b, zc, half_len, top, w=1.55, mat="black"):
    """Picatinny quick-release clamp under an optic."""
    b.add(box(-w, w, 0.0, top, zc - half_len, zc + half_len, r=0.2), mat=mid(mat))
    for sx in (-1, 1):
        b.add(box(sx * w - 0.18, sx * w + 0.18, 0.05, top - 0.15, zc - half_len + 0.4, zc + half_len - 0.4, r=0.06), mat=mid("steel"))
    b.add(Cyl((-w - 0.1, top * 0.55, zc), (w + 0.7, top * 0.55, zc), 0.28, rr=0.05), mat=mid("gunmetal"))      # clamp screw


def red_dot():
    m = dim("att_red_dot", (-3.5, -0.2, -6.0), (3.5, 7.0, 6.0), 11)
    ax = 3.4
    b = m.mesh("body", "rifle", (0, 0, 0), tris=5200)
    clamp_rail(b, 0.2, 3.2, 1.7)
    b.add(box(-1.0, 1.0, 1.4, 2.3, -3.2, 3.4, r=0.3), mat=mid("black"), k=0.2)                      # riser
    b.add(cylz(0, ax, -4.2, 4.2, 1.72, rr=0.3), mat=mid("black"), k=0.15)                           # sleeve
    b.add(cylz(0, ax, -4.3, -2.6, 1.98, rr=0.4), mat=mid("black"), k=0.12)                          # objective bell
    b.add(cylz(0, ax, 2.9, 4.3, 1.9, rr=0.4), mat=mid("black"), k=0.12)                             # ocular bell
    b.add(box(-0.8, 0.8, ax + 1.2, ax + 2.1, -0.8, 1.6, r=0.3), mat=mid("black"), k=0.2)            # turret block
    b.add(Cyl((0, ax + 1.5, 0.4), (0, ax + 2.4, 0.4), 0.62, rr=0.12), mat=mid("gunmetal"))          # elevation cap
    b.add(Cyl((0.9, ax, 0.4), (2.4, ax, 0.4), 0.55, rr=0.12), mat=mid("gunmetal"))                  # windage cap
    b.sub(cylz(0, ax, -4.5, -3.3, 1.5))
    b.sub(cylz(0, ax, 3.4, 4.5, 1.58))
    b.add(cylz(0, ax, -3.5, -3.4, 1.5), mat=mid("lens"))                                             # glass
    b.add(cylz(0, ax, 3.55, 3.65, 1.58), mat=mid("lens"))
    b.paint(box(-0.5, 0.5, ax + 1.2, ax + 2.6, -3.0, 0.2), "steel")
    return m


def holo():
    m = dim("att_holo", (-3.6, -0.2, -6.8), (3.6, 8.0, 6.8), 12)
    ax = 3.7
    b = m.mesh("body", "rifle", (0, 0, 0), tris=6000)
    clamp_rail(b, 0.0, 3.4, 1.0)
    b.add(box(-2.9, 2.9, 0.9, 6.5, -5.7, 5.7, r=0.9), mat=mid("black"), k=0.3)                       # housing
    b.add(box(-2.45, 2.45, 5.9, 7.0, -4.6, 3.8, r=0.5), mat=mid("black"), k=0.3)                     # battery / roof hump
    b.sub(box(-2.3, 2.3, ax - 1.75, ax + 1.75, 0.4, 6.4))                                            # rear window opening
    b.sub(box(-2.3, 2.3, ax - 1.75, ax + 1.75, -6.2, -3.9))                                          # front window opening
    b.add(box(-2.28, 2.28, ax - 1.7, ax + 1.7, 0.3, 0.42), mat=mid("lens"))                          # inner glass
    b.add(box(-2.28, 2.28, ax - 1.7, ax + 1.7, -5.0, -4.88), mat=mid("lens"))
    for sx in (-1, 1):
        b.add(Cyl((sx * 2.8, 2.6, -1.2), (sx * 3.3, 2.6, -1.2), 0.55, rr=0.1), mat=mid("gunmetal"))   # brightness knobs
        b.add(box(sx * 2.9 - 0.12, sx * 2.9 + 0.12, 4.9, 5.7, 1.2, 3.1, r=0.05), mat=mid("gunmetal"))
    b.add(box(-0.8, 0.8, 0.9, 2.6, 5.7, 6.6, r=0.3), mat=mid("black"), k=0.2)
    b.paint(box(-2.9, 2.9, 5.55, 5.7, -5.5, 5.5), "gunmetal")
    return m


def acog():
    m = dim("att_acog", (-3.2, -0.2, -9.4), (3.2, 7.6, 9.4), 13)
    ax = 3.3
    b = m.mesh("body", "rifle", (0, 0, 0), tris=8500)
    b.add(box(-1.6, 1.6, 0.0, 1.9, -4.4, 4.2, r=0.3), mat=mid("black"), k=0.2)                      # base
    clamp_rail(b, 0.0, 3.0, 1.2)
    b.add(Cyl((0, ax, 8.4), (0, ax, 3.6), 1.7, 1.95, rr=0.3), mat=mid("black"), k=0.15)             # eyepiece taper
    b.add(cylz(0, ax, 8.0, 8.6, 2.08, rr=0.35), mat=mid("rubber"))                                   # rubber eyecup
    b.add(cylz(0, ax, -3.6, 3.7, 1.95, rr=0.2), mat=mid("black"), k=0.15)                           # main tube
    b.add(Cyl((0, ax, -3.5), (0, ax, -5.6), 1.95, 2.3, rr=0.2), mat=mid("black"), k=0.15)           # flare
    b.add(cylz(0, ax, -9.0, -5.4, 2.42, rr=0.35), mat=mid("black"), k=0.15)                         # objective
    b.add(cylz(0, ax, -9.05, -8.3, 2.5, rr=0.3), mat=mid("rubber"))                                  # lens cap ring
    b.sub(cylz(0, ax, -9.2, -8.2, 2.05))
    b.add(cylz(0, ax, -8.4, -8.3, 2.05), mat=mid("lens"))
    b.add(box(-0.85, 0.85, ax + 1.5, ax + 2.9, -5.2, 2.2, r=0.35), mat=mid("black"), k=0.2)         # fibre housing
    b.sub(box(-0.45, 0.45, ax + 2.2, ax + 3.2, -4.6, 1.6))                                           # fibre slot
    b.add(box(-0.7, 0.7, ax + 1.9, ax + 3.3, 2.2, 3.4, r=0.15), mat=mid("black"))                    # rear V housing
    b.sub(box(-0.34, 0.34, ax + 2.3, ax + 3.4, 2.1, 3.5))
    b.add(Cyl((0, ax + 1.6, -0.6), (0, ax + 2.5, -0.6), 0.68, rr=0.12), mat=mid("gunmetal"))         # turrets
    b.add(Cyl((1.4, ax, -0.6), (2.5, ax, -0.6), 0.68, rr=0.12), mat=mid("gunmetal"))
    b.paint(cylz(0, ax, 5.5, 7.2, 1.98), "steel")
    b.paint(box(-0.9, 0.9, ax + 3.0, ax + 3.2, -3.0, 0.5), "dot")
    return m


def scope():
    m = dim("att_scope", (-3.2, -0.2, -13.6), (3.2, 8.6, 13.6), 14)
    ax = 4.0
    b = m.mesh("body", "rifle", (0, 0, 0), tris=9000)
    b.add(cylz(0, ax, -9.0, 9.0, 1.55, rr=0.2), mat=mid("black"), k=0.15)                           # tube
    b.add(Cyl((0, ax, -8.0), (0, ax, -12.6), 1.6, 2.5, rr=0.3), mat=mid("black"), k=0.2)            # objective bell
    b.add(cylz(0, ax, -12.8, -12.2, 2.62, rr=0.3), mat=mid("steel"))
    b.sub(cylz(0, ax, -13.2, -11.8, 2.2))
    b.add(cylz(0, ax, -12.0, -11.9, 2.2), mat=mid("lens"))
    b.add(Cyl((0, ax, 8.0), (0, ax, 12.4), 1.6, 2.15, rr=0.3), mat=mid("black"), k=0.2)             # eyepiece
    b.add(cylz(0, ax, 11.4, 12.9, 2.2, rr=0.35), mat=mid("rubber"))
    b.add(cylz(0, ax, 8.6, 11.4, 2.2, rr=0.2), mat=mid("black"))                                     # power ring
    for i in range(14):                                                                              # ribs on the power ring
        z0 = 8.7 + i * 0.19
        b.sub(box(-2.5, 2.5, ax + 2.0, ax + 2.6, z0, z0 + 0.07))
    b.add(Cyl((0, ax, 0.6), (0, ax + 2.2, 0.6), 1.2, rr=0.2), mat=mid("black"), k=0.2)               # turret housing
    b.add(Cyl((0, ax + 1.9, 0.6), (0, ax + 3.1, 0.6), 0.95, rr=0.15), mat=mid("gunmetal"))           # elevation turret
    b.add(Cyl((1.2, ax, 0.6), (2.5, ax, 0.6), 0.95, rr=0.15), mat=mid("gunmetal"))                   # windage turret
    for zc in (-4.8, 4.2):                                                                           # rings + bases
        b.add(cylz(0, ax, zc - 0.9, zc + 0.9, 2.05, rr=0.25), mat=mid("steel"), k=0.12)
        b.add(box(-1.7, 1.7, 0.0, ax - 1.0, zc - 1.0, zc + 1.0, r=0.2), mat=mid("steel"), k=0.12)
        b.add(box(-2.2, 2.2, ax + 0.9, ax + 1.4, zc - 0.9, zc + 0.9, r=0.1), mat=mid("steel"))
    b.add(box(-1.3, 1.3, 0.0, 1.0, -6.0, 6.0, r=0.2), mat=mid("black"))
    b.paint(cylz(0, ax, 9.2, 10.7, 2.22), "steel")
    return m


def flash_hider():
    m = dim("att_flash_hider", (-1.8, -1.8, -9.6), (1.8, 1.8, 0.4), 15, h=0.06)
    b = m.mesh("body", "rifle", (0, 0, 0), tris=5400)
    b.add(cylz(0, 0, -1.6, 0, 1.12, rr=0.1), mat=mid("black"))
    b.add(cylz(0, 0, -9.0, -1.4, 1.02, rr=0.12), mat=mid("black"), k=0.1)
    b.add(cylz(0, 0, -9.0, -8.1, 1.16, rr=0.1), mat=mid("black"))                                    # crown ring
    b.sub(cylz(0, 0, -9.3, 0.2, 0.46))                                                               # bore
    for ang in (0, 60, 120):                                                                         # six prongs: 3 through-slots
        b.sub(Box((0, 0, -5.3), (1.7, 0.2, 3.3), 0.05, rot=[("z", ang)]))
    b.sub(cylz(0, 0, -9.3, -7.4, 0.72))
    return m


def brake():
    m = dim("att_muzzle_brake", (-1.8, -1.8, -8.6), (1.8, 1.8, 0.4), 16, h=0.06)
    b = m.mesh("body", "rifle", (0, 0, 0), tris=6000)
    b.add(cylz(0, 0, -1.2, 0, 1.28, rr=0.1), mat=mid("black"))
    b.add(cylz(0, 0, -8.0, -1.0, 1.2, rr=0.2), mat=mid("black"), k=0.1)
    b.sub(cylz(0, 0, -8.4, 0.2, 0.44))
    for zc in (-2.6, -4.4, -6.2):                                                                    # side + top/bottom ports
        b.sub(Cyl((-2.0, 0, zc), (2.0, 0, zc), 0.45))
    for zc in (-3.5, -5.3, -7.1):
        b.sub(Cyl((0, -2.0, zc), (0, 2.0, zc), 0.4))
    b.paint(cylz(0, 0, -1.2, -0.9, 1.3), "gunmetal")
    return m


def suppressor():
    m = dim("att_suppressor", (-2.8, -2.8, -20.8), (2.8, 2.8, 0.4), 17, h=0.1)
    b = m.mesh("body", "rifle", (0, 0, 0), tris=7500)
    b.add(cylz(0, 0, -3.0, 0, 1.45, rr=0.15), mat=mid("gunmetal"))                                   # mount collar
    b.add(Cyl((0, 0, -3.5), (0, 0, -5.2), 1.45, 2.1, rr=0.1), mat=mid("black"), k=0.2)               # taper
    b.add(cylz(0, 0, -19.2, -5.0, 2.12, rr=0.35), mat=mid("black"), k=0.1)                            # tube
    b.add(cylz(0, 0, -20.0, -19.0, 1.95, rr=0.3), mat=mid("black"))                                   # end cap
    b.sub(cylz(0, 0, -20.4, -19.4, 0.55))
    b.add(cylz(0, 0, -3.2, -2.6, 1.7, rr=0.15), mat=mid("gunmetal"))
    for zc in (-8.0, -11.0, -14.0, -17.0):                                                            # weld lines
        b.sub(cylz(0, 0, zc, zc + 0.08, 2.5))
    b.paint(cylz(0, 0, -6.0, -6.6, 2.2), "stainless")
    return m


BUILD = dict(red_dot=red_dot, holo=holo, acog=acog, scope=scope, flash_hider=flash_hider, muzzle_brake=brake, suppressor=suppressor)

if __name__ == "__main__":
    res = sys.argv[1]
    for n in (sys.argv[2:] or list(BUILD)):
        BUILD[n]().write(res)
