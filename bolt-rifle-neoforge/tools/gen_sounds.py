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
S["shot_heavy"] = [cut("Single Gun Shot (2)", 0.0, 3.2, fade_out=0.8), cut("Single Gun Shot (3)", 0.0, 2.8, fade_out=0.6, pitch=0.94)]
S["shot"] = [cut("Single Gun Shot (3)", 0.0, 2.8, fade_out=0.6), cut("Single Gun Shot (6)", 0.0, 2.2, fade_out=0.5)]
S["shot_light"] = [cut("Single Gun Shot (5)", 0.0, 1.45, fade_out=0.4), cut("Single Gun Shot (6)", 0.0, 2.2, fade_out=0.5, pitch=1.12)]
# suppressed: the recorded suppressed shot, exactly 60% of the unsuppressed level (40% quieter), pitched per family
sup = lambda p: cut("Suppressed Gun Shot", 0.10, 1.5, fade_out=0.35, pitch=p, peak=0.54)
S["shot_heavy_supp"] = [sup(0.92), sup(0.88)]
S["shot_supp"] = [sup(1.0), sup(0.96)]
S["shot_light_supp"] = [sup(1.1), sup(1.05)]
S["click"] = [cut("Empty Magazine Trigger Pull Click (2)", 0.09, 0.36, fade_out=0.08), cut("Empty Magazine Trigger Pull Click", 0.02, 0.28, fade_out=0.08)]
S["click_dry"] = [cut("Empty Magazine Trigger Pull Click", 0.02, 0.24, fade_out=0.07), cut("Empty Magazine Trigger Pull Click (3)", 0.08, 0.30, fade_out=0.08)]
S["bolt_open"] = [cut("Bolt Action Chambering", 0.33, 0.64, fade_out=0.08), cut("Lever Action Chambering", 0.35, 0.70, fade_out=0.08, pitch=0.95)]
S["bolt_close"] = [cut("Bolt Action Chambering", 0.66, 1.15, fade_out=0.12), cut("Lever Action Chambering", 0.74, 1.10, fade_out=0.1, pitch=0.95)]
S["mag_out"] = [cut("Gun Reload (4)", 0.43, 0.85, fade_out=0.1, peak=0.8), cut("Gun Reload (8)", 0.50, 0.85, fade_out=0.1, peak=0.8)]
S["mag_in"] = [cut("Magazine Insert", 0.36, 0.95, fade_out=0.15, peak=0.85), cut("Gun Reload (3)", 0.52, 1.10, fade_out=0.12, peak=0.85)]
S["rack"] = [cut("Pistol Slide Racking (3)", 0.55, 1.35, fade_out=0.15, peak=0.85), cut("Pistol Slide Racking (2)", 0.82, 1.35, fade_out=0.12, peak=0.85)]
S["shell"] = [cut("Bouncing Shell Cases", 0.08, 0.75, fade_out=0.25, peak=0.5), cut("Bouncing Shell Cases (2)", 0.09, 0.75, fade_out=0.25, peak=0.5)]

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
