"""Tiny helper library for writing GeckoLib animations with easing.

Every keyframe is written as {"vector": [...], "easing": "<name>"} (GeckoLib reads `easing`),
so motion accelerates and settles instead of moving at constant speed.

Axis facts learned from testing in game:
  * shooter's RIGHT side is -X in the model.
  * +Z rotation lifts the right-hand side (the bolt handle) UP.
  * negative X rotation lifts the muzzle (muzzle climb), positive dips it.
"""
import json, os

SMOOTH = "easeInOutSine"
SNAP = "easeOutCubic"      # fast start, soft landing (recoil)
FALL = "easeInQuad"        # gravity / dropping a magazine
STEP = "linear"
ZERO, ONE = [0, 0, 0], [1, 1, 1]


class Anim:
    def __init__(self, name, length, loop=False, hidden=()):
        self.name, self.length, self.loop = name, length, loop
        self.bones = {}
        for b in hidden:                       # bones that stay invisible unless shown later
            self.key(b, "scale", 0.0, ZERO, STEP)

    def key(self, bone, channel, t, vec, ease=SMOOTH):
        self.bones.setdefault(bone, {}).setdefault(channel, {})[round(t, 3)] = (list(vec), ease)
        return self

    def pos(self, bone, t, vec, ease=SMOOTH):
        return self.key(bone, "position", t, vec, ease)

    def rot(self, bone, t, vec, ease=SMOOTH):
        return self.key(bone, "rotation", t, vec, ease)

    def show(self, bone, t0, t1=None, fade=0.06):
        """Visible from t0 (growing in over `fade`) until t1 (shrinking out over `fade`)."""
        self.key(bone, "scale", max(t0 - fade, 0.0), ZERO, SMOOTH).key(bone, "scale", t0, ONE, SMOOTH)
        if t1 is not None:
            self.key(bone, "scale", t1, ONE, SMOOTH).key(bone, "scale", t1 + fade, ZERO, SMOOTH)
        return self

    def hand_swap(self, t_to_bolt, t_to_grip, fade=0.12):
        """Grip hand eases out while the bolt hand eases in (and back)."""
        self.key("right_hand", "scale", 0.0, ONE).key("right_hand", "scale", t_to_bolt - fade, ONE)
        self.key("right_hand", "scale", t_to_bolt, ZERO).key("right_hand", "scale", t_to_grip, ZERO)
        self.key("right_hand", "scale", t_to_grip + fade, ONE)
        self.key("bolt_hand", "scale", 0.0, ZERO).key("bolt_hand", "scale", t_to_bolt - fade, ZERO)
        self.key("bolt_hand", "scale", t_to_bolt, ONE).key("bolt_hand", "scale", t_to_grip, ONE)
        self.key("bolt_hand", "scale", t_to_grip + fade, ZERO)
        return self

    def to_json(self):
        bones = {}
        for b, chans in self.bones.items():
            bones[b] = {}
            for c, frames in chans.items():
                bones[b][c] = {f"{t:.3f}": {"vector": v, "easing": e} for t, (v, e) in sorted(frames.items())}
        d = {"animation_length": self.length, "bones": bones}
        if self.loop:
            d["loop"] = True
        return d


def write(res_dir, model_name, prefix, anims, geo_path=None):
    """Writes animations/item/<model>.animation.json and sanity-checks against the geo bones."""
    out = {"format_version": "1.8.0", "animations": {prefix + a.name: a.to_json() for a in anims}}
    d = os.path.join(res_dir, "assets/boltrifle/animations/item")
    os.makedirs(d, exist_ok=True)
    with open(os.path.join(d, f"{model_name}.animation.json"), "w") as f:
        json.dump(out, f, indent=1)
    geo_path = geo_path or os.path.join(res_dir, f"assets/boltrifle/geo/item/{model_name}.geo.json")
    names = {b["name"] for b in json.load(open(geo_path))["minecraft:geometry"][0]["bones"]}
    for a in anims:
        for b, chans in a.bones.items():
            assert b in names, (a.name, "unknown bone", b)
            for c, frames in chans.items():
                assert max(frames) <= a.length + 1e-6, (a.name, b, c, max(frames), a.length)
    print(model_name, "animations:", [prefix + a.name for a in anims])
