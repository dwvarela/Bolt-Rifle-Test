"""Glock 17 (internal id glock19): 9x19 full-size pistol, built from the reference G17_Cube.glb (frame, slide, magazine); hands/flash/casing are ours."""
import os
from gunlib import Model

RAKE = 20
P = [0, -4.7, 2.6]


def g(m, bone, mat, x0, y0, z0, x1, y1, z1):
    """Part of the raked grip/magazine column."""
    m.cube(bone, mat, x0, y0, z0, x1, y1, z1, rot=[RAKE, 0, 0], pivot=P)


GLB = os.path.join(os.path.dirname(os.path.abspath(__file__)), "ref", "models", "Fire Arm", "G17_Cube.glb")
S17, Y17, Z17 = 25.938, 0.150, 2.52          # model = (x*S, (y-Y17)*S, Z17 - z*S); muzzle -z, bore ~y 0.2


def build():
    import numpy as np
    import glbsdf
    from meshbake import MModel, mid
    import gun_m700 as g7
    m = MModel("glock19", lo=(-4.0, -12.0, -9.0), hi=(4.0, 3.0, 14.0), h=float(os.environ.get("H", "0.10")), seed=53, tx=9)
    parts, _ = glbsdf.load_parts(GLB)
    body = m.mesh("body", "rifle", (0, 0, 0), tris=3000)
    slide = m.mesh("bolt", "rifle", (0, 0, 0), tris=2200)
    mag = m.mesh("magazine", "rifle", (0, -3.0, 1.8), tris=900)
    for p in parts:
        V = np.stack([p["V"][:, 0] * S17, (p["V"][:, 1] - Y17) * S17, Z17 - p["V"][:, 2] * S17], 1)
        n = p["name"]
        if n == "Object_0":
            glbsdf.add_part(body, V, p["F"], mid("poly"))
        elif n == "Object_1":
            glbsdf.add_part(body, V, p["F"], mid("steel"))
        elif n == "Object_5":
            glbsdf.add_part(mag, V, p["F"], mid("steel"))
        elif n == "Object_2":
            glbsdf.add_part(slide, V, p["F"], mid("black"))
        elif n == "Object_4":
            glbsdf.add_part(slide, V, p["F"], mid("stainless"))
        else:
            glbsdf.add_part(slide, V, p["F"], mid("steel"))
    m.cube("magazine", "brass", -0.4, -0.55, -0.1, 0.4, -0.3, 3.4)                  # top round hint under the slide
    m.muzzle_flash(-6.1, y=0.2, length=3.4, width=2.4)
    m.casing(-0.8, 0.5, -1.6, length=2.0, r=0.38)
    gl = mid("glove")
    # firing hand: wraps the grip from the right, web high on the backstrap
    R = m.mesh("right_hand", "rifle", (0, -3.2, 4.0), tris=1800)
    g7.glove(R, (-1.3, -1.6, 6.2), (0.0, -0.22, -0.975), (1, 0, 0), (0, 1, 0), gl, (80, 62, 45),
             [(1.2, 0.8, 0.3), (1.8, 1.8, 0.8), (1.8, 2.8, 1.4)], (-3.0, -9.0, 14.0), flen=0.95, scale=0.85,
             index_pts=[(-1.2, -1.3, 4.6), (-1.1, -1.0, 2.8), (-0.8, -0.4, 0.9), (-0.5, -0.3, -0.4), (-0.2, -0.3, -1.4)])
    # support hand: from the left, palm on the left of the grip, fingers over the firing fingers, thumb forward on the frame
    L = m.mesh("left_hand", "rifle", (0, -4.6, 3.4), tris=1800)
    g7.glove(L, (1.3, -3.6, 6.0), (0.0, -0.2, -0.98), (-1, 0, 0), (0, 1, 0), gl, (78, 60, 45),
             [(1.2, 0.8, 0.3), (1.8, 1.8, 0.8), (1.8, 2.8, 1.4)], (3.0, -10.0, 14.0), flen=0.95, scale=0.85)
    cfg = dict(
        name="glock19", hand_l=(-4.6, 3.4), mag_grip=(-6.2, 1.8), mag_drop=6.0, mag_rock=0,
        charge_hand="left", charge_bone="bolt", handle=(0.0, 0.3, 3.4), bolt_travel=3.6,
        hold_open=True, release_mode="press", catch=(-0.5, 0.0), catch_x=1.5,
        fire_len=0.26, cycle=0.06, kick_z=1.1, kick_pitch=4.2, kick_yaw=0.6, flash=0.9,
        reload_len=1.7, charge_len=0.9, release_len=0.6, eject=(-1.0, 1.0, 0.6),
        sight=(0.93, 3.5), butt=5.0,
    )
    return m, cfg
