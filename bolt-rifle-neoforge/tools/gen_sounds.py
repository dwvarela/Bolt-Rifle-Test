"""Builds the gun sounds from the user's own recordings (Gun_Sound_Effects.zip) -> assets/boltrifle/sounds/*.ogg + sounds.json.
Usage: python3 -I gen_sounds.py <resources_dir> <Gun_Sound_Effects.zip>
The zip is untrusted data: it is only decoded with ffmpeg and cut; nothing in it is executed."""
import sys, os, json, glob, wave, zipfile, tempfile, subprocess
import numpy as np
from scipy import signal

RES, ZIP = sys.argv[1], sys.argv[2]
OUT = os.path.join(RES, "assets", "boltrifle", "sounds")
os.makedirs(OUT, exist_ok=True)
for f in glob.glob(os.path.join(OUT, "*.ogg")):
    os.remove(f)
SR = 44100
tmp = tempfile.mkdtemp()
with zipfile.ZipFile(ZIP) as z:
    for n in z.namelist():
        if n.lower().endswith(".mp3") and "/" in n and ".." not in n:
            z.extract(n, tmp)
SRC = {}
for p in glob.glob(os.path.join(tmp, "**", "*.mp3"), recursive=True):
    wav = p[:-4] + ".wav"
    subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-i", p, "-ac", "1", "-ar", str(SR), wav], check=True)
    with wave.open(wav) as w:
        SRC[os.path.basename(p)[:-4]] = np.frombuffer(w.readframes(w.getnframes()), "<i2").astype(float) / 32768


def cut(name, t0, t1, peak=0.9, fade_in=0.002, fade_out=0.06, pitch=1.0, gain=None):
    """Cut [t0,t1] of a recording, optional pitch/speed change, fade, scale so the loudest sample is `peak` (or fixed gain)."""
    x = SRC[name][int(t0 * SR):int(t1 * SR)].copy()
    if pitch != 1.0:
        x = signal.resample(x, int(len(x) / pitch))
    x = x - np.mean(x)
    a, b = int(fade_in * SR), int(fade_out * SR)
    x[:a] *= np.linspace(0, 1, a)
    x[-b:] *= np.linspace(1, 0, b)
    m = np.max(np.abs(x)) + 1e-9
    return x * (gain if gain is not None else peak / m)


def soft(x, thr=0.8):
    """Gentle tanh-style ceiling so nothing ever hard-clips."""
    return np.where(np.abs(x) > thr, np.sign(x) * (thr + (1 - thr) * np.tanh((np.abs(x) - thr) / (1 - thr))), x)


S = {}
# ONE recording per event (never a mix of different sources); the two variants are the same clip a hair apart in pitch so repeats don't machine-gun.
two = lambda fn: [fn(0.985), fn(1.015)]
S["shot_heavy"] = two(lambda p: cut("Single Gun Shot (2)", 0.0, 3.2, fade_out=0.8, pitch=p))
S["shot"] = two(lambda p: cut("Single Gun Shot (3)", 0.0, 2.8, fade_out=0.6, pitch=p))
S["shot_light"] = two(lambda p: cut("Single Gun Shot (5)", 0.0, 1.45, fade_out=0.4, pitch=p))
# suppressed: the recorded suppressed shot, exactly 60% of the unsuppressed level (40% quieter), same clip for every gun
sup = lambda p: cut("Suppressed Gun Shot", 0.10, 1.5, fade_out=0.35, pitch=p, peak=0.54)
S["shot_heavy_supp"] = two(lambda p: sup(0.95 * p))
S["shot_supp"] = two(sup)
S["shot_light_supp"] = two(lambda p: sup(1.08 * p))
S["click"] = two(lambda p: cut("Empty Magazine Trigger Pull Click (2)", 0.09, 0.36, fade_out=0.08, pitch=p))
S["click_dry"] = two(lambda p: cut("Empty Magazine Trigger Pull Click (2)", 0.09, 0.36, fade_out=0.08, pitch=p))
S["bolt_open"] = two(lambda p: cut("Bolt Action Chambering", 0.33, 0.64, fade_out=0.08, pitch=p))
S["bolt_close"] = two(lambda p: cut("Bolt Action Chambering", 0.66, 1.15, fade_out=0.12, pitch=p))
S["mag_out"] = two(lambda p: cut("Gun Reload (4)", 0.43, 0.85, fade_out=0.1, peak=0.8, pitch=p))
S["mag_in"] = two(lambda p: cut("Magazine Insert", 0.36, 0.95, fade_out=0.15, peak=0.85, pitch=p))
S["rack"] = two(lambda p: cut("Pistol Slide Racking (3)", 0.55, 1.35, fade_out=0.15, peak=0.85, pitch=p))
S["shell"] = two(lambda p: cut("Bouncing Shell Cases", 0.08, 0.75, fade_out=0.25, peak=0.5, pitch=p))

events = {}
for name, variants in S.items():
    files = []
    for i, x in enumerate(variants):
        x = soft(x)
        fn = f"{name}_v{i + 1}"
        wav = os.path.join(tmp, fn + ".o.wav")
        with wave.open(wav, "wb") as w:
            w.setnchannels(1); w.setsampwidth(2); w.setframerate(SR)
            w.writeframes((np.clip(x, -1, 1) * 32000).astype("<i2").tobytes())
        subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-i", wav, "-c:a", "libvorbis", "-q:a", "8", os.path.join(OUT, fn + ".ogg")], check=True)
        files.append({"name": "boltrifle:" + fn, "stream": False})
    events[name] = {"sounds": files, "subtitle": "boltrifle.sound." + name}
    print(f"{name:16s} x{len(variants)} peaks", " ".join(f"{np.max(np.abs(v)):.2f}" for v in variants))
json.dump(events, open(os.path.join(RES, "assets", "boltrifle", "sounds.json"), "w"), indent=1)
