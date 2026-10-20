"""Synthesises the gun sounds -> assets/boltrifle/sounds/*.ogg + sounds.json.  Usage: gen_sounds.py <resources_dir>
Everything is built from filtered NOISE (no pure tones, no hard clipping): a gunshot is a broadband explosive transient
(crack + blast + low rumble) followed by reflections; mechanical sounds are short noise ticks, thuds and scrapes."""
import sys, os, json, subprocess, wave
import numpy as np

SR = 44100
rng = np.random.default_rng(11)
RES = sys.argv[1]
OUT = os.path.join(RES, "assets", "boltrifle", "sounds")
os.makedirs(OUT, exist_ok=True)


def t(n):
    return np.arange(int(n * SR)) / SR


def noise(n):
    return rng.standard_normal(int(n * SR))


def lp(x, fc, order=2):
    a = 1 - np.exp(-2 * np.pi * fc / SR)
    for _ in range(order):
        y = np.empty_like(x); s = 0.0
        for i, v in enumerate(x):
            s += a * (v - s); y[i] = s
        x = y
    return x


def hp(x, fc):
    return x - lp(x, fc, 1)


def bp(x, lo, hi):
    return hp(lp(x, hi), lo)


def env(n, tau, attack=0.0003):
    tt = t(n)
    return np.exp(-tt / tau) * np.minimum(1, tt / attack)


def place(buf, snd, at, g=1.0):
    i = int(at * SR)
    if i >= len(buf):
        return
    j = min(len(buf), i + len(snd))
    buf[i:j] += g * snd[: j - i]


def master(x, peak=0.95, squash=0.5, tail_fade=0.05, drive=1.0):
    """Gentle upward compression (keeps the tail audible) + soft limiting, then normalise."""
    w = int(0.02 * SR)
    e = np.sqrt(np.convolve(x * x, np.ones(w) / w, mode="same")) + 1e-3
    g = (0.3 / e) ** squash
    g = np.convolve(np.clip(g, 0, 12), np.ones(w) / w, mode="same")
    x = x * g
    x = np.tanh(drive * x / max(1e-9, np.percentile(np.abs(x), 99.5)))
    n = int(tail_fade * SR)
    x[-n:] *= np.linspace(1, 0, n)
    return x / max(1e-9, np.max(np.abs(x))) * peak


def shot(length=1.8, low=1.0, crack_hi=9000, tail=1.0, blast_lo=100):
    b = np.zeros(int(length * SR))
    place(b, hp(noise(0.08), 1200) * env(0.08, 0.005), 0.0, 1.0)                                      # supersonic crack
    place(b, bp(noise(0.12), 400, crack_hi) * env(0.12, 0.018), 0.0, 1.1)                              # sharp edge of the blast
    blast = bp(noise(0.6), blast_lo, 2600) * env(0.6, 0.055)
    rumble = lp(noise(0.9), 170 / low, 2) * env(0.9, 0.16) * 3.0
    place(b, blast, 0.0, 1.3)
    place(b, rumble, 0.0, 1.0)
    body = blast + rumble[: len(blast)]
    for d, g, fc in ((0.045, 0.45, 2200), (0.11, 0.34, 1700), (0.21, 0.25, 1300), (0.36, 0.17, 1000), (0.58, 0.10, 800)):   # terrain reflections
        place(b, lp(body, fc, 1) * np.linspace(1, 0.5, len(body)), d, g * tail)
    place(b, lp(noise(1.5), 600) * env(1.5, 0.45) * 0.6, 0.05, tail)                                 # distant rolling tail
    return master(b, 0.97, 0.85, 0.05, 1.7)


def shot_suppressed(length=0.7):
    b = np.zeros(int(length * SR))
    place(b, lp(noise(0.25), 2400) * env(0.25, 0.028), 0.0, 1.0)                                      # "phut": gas escaping
    place(b, lp(noise(0.3), 420) * env(0.3, 0.06), 0.0, 1.4)                                          # soft thump
    place(b, bp(noise(0.03), 2500, 7000) * env(0.03, 0.004), 0.0, 0.25)                               # tiny residual crack
    place(b, bp(noise(0.02), 1500, 5000) * env(0.02, 0.003), 0.085, 0.5)                              # action clatter
    place(b, lp(noise(0.5), 700) * env(0.5, 0.12), 0.03, 0.35)
    return master(b, 0.6, 0.5, 0.05, 1.2)


def tick(f0, dur=0.03, tau=0.004):
    return bp(noise(dur), f0, f0 * 2.4) * env(dur, tau, 0.0002)


def thud(fc, dur=0.12, tau=0.025):
    return lp(noise(dur), fc, 2) * env(dur, tau, 0.0004) * 2.2


def slide(dur, lo=1400, hi=6500):
    n = noise(dur)
    r = np.sin(np.linspace(0, np.pi, len(n))) ** 1.5
    return bp(n, lo, hi) * r * 0.5


def mix(parts, length, peak=0.9):
    b = np.zeros(int(length * SR))
    for snd, at, g in parts:
        place(b, snd, at, g)
    return master(b, peak, 0.6, 0.03, 1.5)


sounds = {
    "shot_heavy": shot(2.0, 0.85, 8000, 1.1, 80),
    "shot": shot(1.7, 1.0, 9000, 1.0, 100),
    "shot_light": shot(1.1, 1.3, 11000, 0.8, 140),
    "shot_supp": shot_suppressed(),
    "click": mix([(tick(3000), 0.0, 1.0), (thud(700), 0.0, 0.5), (tick(2400), 0.07, 0.8), (thud(600), 0.07, 0.35)], 0.2, 0.8),
    "click_dry": mix([(tick(2600), 0.0, 1.0), (thud(520), 0.0, 0.6)], 0.12, 0.75),
    "bolt_open": mix([(slide(0.09), 0.0, 0.6), (tick(2800), 0.09, 1.0), (thud(900), 0.09, 1.0), (tick(3600), 0.15, 0.6)], 0.34, 0.85),
    "bolt_close": mix([(slide(0.08), 0.0, 0.5), (thud(480, 0.14, 0.03), 0.08, 1.4), (tick(2500), 0.08, 1.0), (tick(3800), 0.125, 0.55)], 0.34, 0.9),
    "mag_out": mix([(tick(1800), 0.0, 1.0), (thud(420, 0.14, 0.03), 0.0, 1.0), (slide(0.07, 900, 4500), 0.04, 0.6)], 0.28, 0.85),
    "mag_in": mix([(slide(0.1, 900, 4500), 0.0, 0.55), (thud(460, 0.14, 0.03), 0.1, 1.3), (tick(3000), 0.105, 0.9), (tick(2200), 0.16, 0.5)], 0.3, 0.88),
    "rack": mix([(tick(2400), 0.0, 1.0), (thud(800), 0.0, 0.8), (slide(0.14, 1200, 5500), 0.05, 0.55), (thud(600, 0.14, 0.03), 0.24, 1.2), (tick(2800), 0.24, 0.8)], 0.44, 0.88),
    "shell": mix([(bp(noise(0.12), 4200, 8500) * env(0.12, 0.03), 0.0, 1.0), (bp(noise(0.1), 4000, 8000) * env(0.1, 0.025), 0.11, 0.6), (bp(noise(0.08), 4500, 8500) * env(0.08, 0.02), 0.19, 0.35)], 0.36, 0.7),
}
events = {}
for name, x in sounds.items():
    wav = os.path.join(OUT, name + ".wav")
    with wave.open(wav, "wb") as w:
        w.setnchannels(1); w.setsampwidth(2); w.setframerate(SR)
        w.writeframes((np.clip(x, -1, 1) * 32767).astype("<i2").tobytes())
    subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-i", wav, "-c:a", "libvorbis", "-q:a", "7", os.path.join(OUT, name + ".ogg")], check=True)
    os.remove(wav)
    events[name] = {"sounds": [{"name": "boltrifle:" + name, "stream": False}], "subtitle": "boltrifle.sound." + name}
json.dump(events, open(os.path.join(RES, "assets", "boltrifle", "sounds.json"), "w"), indent=1)
print("sounds:", list(sounds))
