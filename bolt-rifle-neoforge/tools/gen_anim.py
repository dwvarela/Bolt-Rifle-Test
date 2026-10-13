"""Generates animations/item/bolt_rifle.animation.json (GeckoLib).  Usage: gen_anim.py <resources_dir>

All motion avoids X-axis positions/rotations (their sign conventions are easy to get backwards),
so the only sign worth tuning is HANDLE_LIFT below.
"""
import json, os, sys

RES = sys.argv[1]
PFX = "animation.bolt_rifle."
HANDLE_LIFT = 75.0     # degrees; if the bolt handle swings DOWN in game, change to -75.0
BOLT_BACK = 7.5        # px the bolt slides rearward
HIDDEN_BASE = ("bolt_hand", "casing", "chamber_round")
ZERO, ONE = [0, 0, 0], [1, 1, 1]


class Anim:
    def __init__(self, name, length, loop=False):
        self.name, self.length, self.loop = name, length, loop
        self.bones = {}
        for b in HIDDEN_BASE:                         # hidden unless shown below
            self.key(b, "scale", 0.0, ZERO)

    def key(self, bone, channel, t, vec):
        self.bones.setdefault(bone, {}).setdefault(channel, {})[round(t, 3)] = vec
        return self

    def show(self, bone, t0, t1=None):
        """Visible from t0 until t1 (or the end)."""
        self.key(bone, "scale", max(t0 - 0.001, 0), ZERO).key(bone, "scale", t0, ONE)
        if t1 is not None:
            self.key(bone, "scale", t1, ONE).key(bone, "scale", t1 + 0.001, ZERO)
        return self

    def swap_hands(self, t_to_bolt, t_to_grip):
        """Right grip hand leaves the stock for the bolt handle, then returns."""
        self.key("right_hand", "scale", 0.0, ONE)
        self.key("right_hand", "scale", t_to_bolt, ONE).key("right_hand", "scale", t_to_bolt + 0.001, ZERO)
        self.key("right_hand", "scale", t_to_grip, ZERO).key("right_hand", "scale", t_to_grip + 0.001, ONE)
        self.key("bolt_hand", "scale", 0.0, ZERO)
        self.key("bolt_hand", "scale", t_to_bolt, ZERO).key("bolt_hand", "scale", t_to_bolt + 0.001, ONE)
        self.key("bolt_hand", "scale", t_to_grip, ONE).key("bolt_hand", "scale", t_to_grip + 0.001, ZERO)
        return self

    def bolt_cycle(self, lift0, lift1, back1, hold1, fwd1, down1):
        """lift handle -> pull bolt back -> hold -> push forward -> lower handle."""
        h = [0, 0, HANDLE_LIFT]
        self.key("bolt_handle", "rotation", 0.0, ZERO).key("bolt_handle", "rotation", lift0, ZERO)
        self.key("bolt_handle", "rotation", lift1, h).key("bolt_handle", "rotation", hold1 + (fwd1 - hold1), h)
        self.key("bolt_handle", "rotation", down1, ZERO)
        self.key("bolt", "position", 0.0, ZERO).key("bolt", "position", lift1, ZERO)
        self.key("bolt", "position", back1, [0, 0, BOLT_BACK]).key("bolt", "position", hold1, [0, 0, BOLT_BACK])
        self.key("bolt", "position", fwd1, ZERO)
        return self

    def to_json(self):
        bones = {}
        for b, chans in self.bones.items():
            bones[b] = {c: {f"{t:.3f}": v for t, v in sorted(frames.items())} for c, frames in chans.items()}
        d = {"animation_length": self.length, "bones": bones}
        if self.loop:
            d["loop"] = True
        return d


anims = []

# ---- idle: slow breathing sway ----
a = Anim("idle", 4.0, loop=True)
a.key("rifle", "position", 0.0, ZERO).key("rifle", "position", 2.0, [0, 0.07, 0.05]).key("rifle", "position", 4.0, ZERO)
a.key("right_hand", "scale", 0.0, ONE)
anims.append(a)

# ---- dry fire click ----
a = Anim("dryfire", 0.3)
a.key("rifle", "position", 0.0, ZERO).key("rifle", "position", 0.04, [0, 0, 0.45]).key("rifle", "position", 0.25, ZERO)
a.key("right_hand", "scale", 0.0, ONE)
anims.append(a)

# ---- fire: recoil, then the shooter works the bolt (eject + chamber next round) ----
a = Anim("fire", 1.55)
a.key("rifle", "position", 0.0, ZERO)
a.key("rifle", "position", 0.03, [0, 0.4, 2.4]).key("rifle", "position", 0.14, [0, 0.2, 1.1])
a.key("rifle", "position", 0.45, [0, 0.0, 0.25]).key("rifle", "position", 0.6, ZERO)
a.bolt_cycle(lift0=0.55, lift1=0.72, back1=0.92, hold1=1.0, fwd1=1.16, down1=1.34)
a.swap_hands(0.52, 1.38)
a.show("casing", 0.84, 1.3)                                   # spent case flies out of the port
a.key("casing", "position", 0.84, ZERO).key("casing", "position", 0.93, [0, 3.6, 2.6])
a.key("casing", "position", 1.03, [0, 4.4, 4.4]).key("casing", "position", 1.28, [0, -3.0, 8.0])
a.key("casing", "rotation", 0.84, ZERO).key("casing", "rotation", 1.28, [0, 0, 360])
anims.append(a)


def reload_mag(a):
    """Mag swap, 0 -> 2.8 s.  Hand y offsets and mag y offsets share keys (mag rides in hand)."""
    a.key("right_hand", "scale", 0.0, ONE)
    hand = {0.0: [0, 0, 0], 0.28: [0, -2.5, 15.0], 0.42: [0, -2.5, 15.0], 0.58: [0, -3.5, 15.0],
            0.88: [0, -13.0, 15.0], 1.0: [0, -16.0, 15.0], 1.28: [0, -16.0, 15.0], 1.55: [0, -13.5, 15.0],
            1.95: [0, -6.0, 15.0], 2.14: [0, -2.5, 15.0], 2.34: [0, -2.5, 15.0], 2.8: [0, 0, 0]}
    for t, v in hand.items():
        a.key("left_hand", "position", t, v)
    mag = {0.0: [0, 0, 0], 0.42: [0, 0, 0], 0.58: [0, -1.0, 0], 0.88: [0, -10.5, 0]}
    for t, v in mag.items():
        a.key("magazine", "position", t, v)
    a.key("magazine", "scale", 0.0, ONE).key("magazine", "scale", 0.96, ONE).key("magazine", "scale", 0.961, ZERO)
    a.key("magazine", "scale", 1.28, ZERO).key("magazine", "scale", 1.281, ONE)    # fresh magazine
    a.key("magazine", "position", 1.281, [0, -13.5, 0])
    for t, v in {1.55: [0, -11.0, 0], 1.95: [0, -3.5, 0], 2.14: [0, 0.0, 0], 2.8: [0, 0, 0]}.items():
        a.key("magazine", "position", t, v)
    # a little muzzle dip while the support hand lets go of the forend
    a.key("rifle", "position", 0.0, ZERO).key("rifle", "position", 0.35, [0, -0.4, 0.3])
    a.key("rifle", "position", 2.3, [0, -0.4, 0.3]).key("rifle", "position", 2.8, ZERO)


# ---- reload (magazine only; round already chambered) ----
a = Anim("reload", 2.8)
reload_mag(a)
anims.append(a)

# ---- reload + chamber a round (chamber was empty) ----
a = Anim("reload_chamber", 3.8)
reload_mag(a)
a.key("rifle", "position", 2.8, ZERO).key("rifle", "position", 3.8, ZERO)
a.key("left_hand", "position", 3.8, ZERO)
a.key("magazine", "position", 3.8, ZERO)
a.bolt_cycle(lift0=2.86, lift1=3.04, back1=3.24, hold1=3.34, fwd1=3.52, down1=3.7)
a.swap_hands(2.82, 3.74)
a.show("chamber_round", 3.26, 3.54)                              # round rises into the port, bolt strips it forward
for t, v in {3.26: [0, -1.2, 4.0], 3.34: [0, 0.0, 4.0], 3.52: [0, 0.0, -1.8]}.items():
    a.key("chamber_round", "position", t, v)
anims.append(a)

out = {"format_version": "1.8.0", "animations": {PFX + a.name: a.to_json() for a in anims}}
path = os.path.join(RES, "assets/boltrifle/animations/item")
os.makedirs(path, exist_ok=True)
with open(os.path.join(path, "bolt_rifle.animation.json"), "w") as f:
    json.dump(out, f, indent=1)

# sanity checks: keys inside the animation length, bones exist in geo
geo = json.load(open(os.path.join(RES, "assets/boltrifle/geo/item/bolt_rifle.geo.json")))
names = {b["name"] for b in geo["minecraft:geometry"][0]["bones"]}
for a in anims:
    for b, chans in a.bones.items():
        assert b in names, (a.name, "unknown bone", b)
        for c, frames in chans.items():
            assert max(frames) <= a.length + 1e-6, (a.name, b, c, max(frames), a.length)
print("animations:", [PFX + a.name for a in anims])
