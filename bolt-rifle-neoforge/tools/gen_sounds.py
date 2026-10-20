"""Synthesises the gun sounds (full-scale, compressed) -> assets/boltrifle/sounds/*.ogg + sounds.json.  Usage: gen_sounds.py <resources_dir>"""
import sys, os, json, subprocess, wave
import numpy as np

SR = 44100
rng = np.random.default_rng(7)
RES = sys.argv[1]
OUT = os.path.join(RES, "assets", "boltrifle", "sounds")
os.makedirs(OUT, exist_ok=True)


def t(n):
    return np.arange(int(n * SR)) / SR


def noise(n):
    return rng.standard_normal(int(n * SR))


def lp(x, fc):
    a = 1 - np.exp(-2 * np.pi * fc / SR)
    y = np.empty_like(x); s = 0.0
    for i, v in enumerate(x):
        s += a * (v - s); y[i] = s
    return y


def hp(x, fc):
    return x - lp(x, fc)


def bp(x, lo, hi):
    return hp(lp(x, hi), lo)


def env(n, tau, attack=0.0005):
    tt = t(n)
    e = np.exp(-tt / tau)
    if attack:
        e *= np.minimum(1, tt / attack)
    return e


def place(buf, snd, at):
    i = int(at * SR)
    if i >= len(buf):
        return
    j = min(len(buf), i + len(snd))
    buf[i:j] += snd[: j - i]


def drive(x, k=2.4):
    x = np.tanh(k * x) / np.tanh(k)
    return x / max(1e-9, np.max(np.abs(x))) * 0.97


def reverb(x, taps):
    y = x.copy()
    for d, g in taps:
        sh = int(d * SR)
        y[sh:] += g * x[: len(x) - sh]
    return y


def shot(low=1.0, length=1.3, crack=1.0):
    n = length
    b = np.zeros(int(n * SR))
    place(b, hp(noise(0.12), 900) * env(0.12, 0.012) * 1.3 * crack, 0.0)          # supersonic crack
    place(b, lp(noise(0.5), 1800) * env(0.5, 0.09) * 1.0, 0.0)                    # muzzle blast
    f = 150 * low * np.exp(-t(0.45) / 0.10) + 40 * low
    place(b, np.sin(2 * np.pi * np.cumsum(f) / SR) * env(0.45, 0.13) * 1.4, 0.0)  # body thump
    place(b, lp(noise(1.2), 700) * env(1.2, 0.33) * 0.55, 0.02)                   # rolling tail
    b = reverb(b, [(0.043, 0.35), (0.091, 0.25), (0.167, 0.15)])
    return drive(b, 2.6)


def clack(freq, dur=0.06, amp=1.0, grit=0.6):
    tt = t(dur)
    s = np.sin(2 * np.pi * freq * tt) * np.exp(-tt / (dur / 4)) + grit * hp(noise(dur), 1500) * np.exp(-tt / (dur / 6))
    return s * amp


def mix(parts, length):
    b = np.zeros(int(length * SR))
    for snd, at in parts:
        place(b, snd, at)
    return drive(b, 2.0)


sounds = {
    "shot": shot(1.0, 1.3, 1.0),
    "shot_light": shot(1.6, 0.8, 1.2),
    "click": mix([(clack(2600, 0.04, 1.0), 0.0), (clack(2000, 0.05, 0.8), 0.07)], 0.2),
    "click_dry": mix([(clack(1900, 0.05, 1.0), 0.0)], 0.12),
    "bolt_open": mix([(bp(noise(0.12), 800, 5000) * env(0.12, 0.05) * 0.7, 0.0), (clack(900, 0.09, 1.0), 0.1), (clack(1500, 0.05, 0.6), 0.16)], 0.35),
    "bolt_close": mix([(bp(noise(0.1), 600, 4000) * env(0.1, 0.04) * 0.6, 0.0), (clack(650, 0.1, 1.1), 0.08), (clack(160, 0.12, 1.0, 0.0), 0.08), (clack(1100, 0.05, 0.6), 0.14)], 0.35),
    "mag_out": mix([(clack(300, 0.1, 1.0, 0.3), 0.0), (bp(noise(0.15), 500, 3500) * env(0.15, 0.06) * 0.6, 0.04)], 0.3),
    "mag_in": mix([(bp(noise(0.12), 500, 3500) * env(0.12, 0.05) * 0.5, 0.0), (clack(420, 0.09, 1.1, 0.4), 0.09), (clack(1800, 0.04, 0.7), 0.15)], 0.32),
    "rack": mix([(clack(800, 0.08, 1.0), 0.0), (bp(noise(0.14), 700, 4500) * env(0.14, 0.05) * 0.5, 0.05), (clack(600, 0.09, 1.0), 0.22)], 0.45),
    "shell": mix([(clack(4600, 0.16, 0.9, 0.2), 0.0), (clack(4200, 0.12, 0.6, 0.2), 0.11), (clack(4800, 0.08, 0.35, 0.2), 0.19)], 0.4),
}
events = {}
for name, x in sounds.items():
    wav = os.path.join(OUT, name + ".wav")
    with wave.open(wav, "wb") as w:
        w.setnchannels(1); w.setsampwidth(2); w.setframerate(SR)
        w.writeframes((np.clip(x, -1, 1) * 32767).astype("<i2").tobytes())
    subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-i", wav, "-c:a", "libvorbis", "-q:a", "6", os.path.join(OUT, name + ".ogg")], check=True)
    os.remove(wav)
    events[name] = {"sounds": [{"name": "boltrifle:" + name, "stream": False}], "subtitle": "boltrifle.sound." + name}
json.dump(events, open(os.path.join(RES, "assets", "boltrifle", "sounds.json"), "w"), indent=1)
print("sounds:", list(sounds))
