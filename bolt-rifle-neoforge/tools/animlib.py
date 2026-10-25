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

    @staticmethod
    def _flow(frames, dt=1.0 / 30.0):
        """Runs of consecutive SMOOTH segments are resampled along a monotone cubic through the keys (continuous velocity, no
        stop at every keyframe - that stop-start was what made the motion feel clunky); impact keys (SNAP/FALL/STEP) stay as written."""
        import numpy as np
        from scipy.interpolate import PchipInterpolator
        ks = sorted(frames.items())
        out = {}
        i = 0
        while i < len(ks):
            j = i
            while j < len(ks) - 1 and ks[j][1][1] == SMOOTH:
                j += 1
            if j - i >= 2:                                    # >= 2 smooth segments in a row: flow through them
                ts = np.array([k[0] for k in ks[i:j + 1]])
                vs = np.array([k[1][0] for k in ks[i:j + 1]], float)
                f = PchipInterpolator(ts, vs, axis=0)
                n = max(2, int(round((ts[-1] - ts[0]) / dt)))
                for tt in np.linspace(ts[0], ts[-1], n + 1)[:-1]:
                    out[round(float(tt), 3)] = ([round(float(x), 4) for x in f(tt)], STEP)
                out[round(ks[j][0], 3)] = ks[j][1]            # the run's last key keeps its own easing (impact etc.)
                i = j + 1
            else:
                out[round(ks[i][0], 3)] = ks[i][1]
                i += 1
        return out

    def to_json(self):
        bones = {}
        for b, chans in self.bones.items():
            bones[b] = {}
            for c, frames in chans.items():
                fr = self._flow(frames) if c in ("position", "rotation") else frames
                bones[b][c] = {f"{t:.3f}": {"vector": v, "easing": e} for t, (v, e) in sorted(fr.items())}
        d = {"animation_length": self.length, "bones": bones}
        if self.loop:
            d["loop"] = True
        return d


def write(res_dir, model_name, prefix, anims, geo_path=None):
    """Writes animations/item/<model>.animation.json and sanity-checks against the geo bones."""
    out = {"format_version": "1.8.0", "animations": {prefix + a.name: a.to_json() for a in anims}}
    # identical twins ("_b") so back-to-back shots can alternate and each one restarts the animation
    for a in anims:
        if a.name in ("fire", "dryfire", "dryfire_open"):
            out["animations"][prefix + a.name + "_b"] = a.to_json()
    d = os.path.join(res_dir, "assets/boltrifle/animations/item")
    os.makedirs(d, exist_ok=True)
    with open(os.path.join(d, f"{model_name}.animation.json"), "w") as f:
        json.dump(out, f, indent=1)
    geo_path = geo_path or os.path.join(res_dir, f"assets/boltrifle/geo/item/{model_name}.geo.json")
    names = {b["name"] for b in json.load(open(geo_path))["minecraft:geometry"][0]["bones"]}
    # ---- HARD RULE (see CLAUDE.md): exactly two hands, never shown/hidden/scaled; magazines never vanish or re-appear in view ----
    hands = sorted(n for n in names if "hand" in n.lower() and n not in ("bolt_handle", "handguard", "charging_handle"))
    assert set(hands) <= {"left_hand", "right_hand"}, ("HARD RULE: more than two hands in the model", hands)
    for a in anims:
        for b, chans in a.bones.items():
            if "hand" in b.lower() and b not in ("bolt_handle", "handguard", "charging_handle"):
                assert "scale" not in chans, ("HARD RULE: a hand must never be scaled / hidden / shown", a.name, b)
            if b.startswith("mag") or b.startswith("drop_mag"):
                assert "scale" not in chans, ("HARD RULE: a magazine must never disappear / re-appear", a.name, b)
    for a in anims:
        for b, chans in a.bones.items():
            assert b in names, (a.name, "unknown bone", b)
            for c, frames in chans.items():
                assert max(frames) <= a.length + 1e-6, (a.name, b, c, max(frames), a.length)
    print(model_name, "animations:", [prefix + a.name for a in anims])
