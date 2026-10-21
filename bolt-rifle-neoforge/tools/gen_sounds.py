"""Synthesises the gun sounds -> assets/boltrifle/sounds/*.ogg + sounds.json.  Usage: gen_sounds.py <resources_dir>
Cinematic (Battlefield / Call of Duty style) but CLEAN: every sound is built from layered filtered noise, a pitch-dropping sub thump and a
synthetic room impulse response, then mastered with a look-ahead limiter (no hard clipping, no tanh squashing, no upward compression), so
nothing crackles or glitches.  Peaks sit at -1.5 dBFS; the loudness comes from dense, well-shaped layers, not from distortion."""
import sys, os, json, subprocess, wave
import numpy as np
from scipy import signal
from scipy.ndimage import minimum_filter1d, uniform_filter1d, maximum_filter1d

SR = 44100
rng = np.random.default_rng(7)
RES = sys.argv[1]
OUT = os.path.join(RES, "assets", "boltrifle", "sounds")
os.makedirs(OUT, exist_ok=True)


def tt(n):
    return np.arange(int(n * SR)) / SR


def noise(n):
    return rng.standard_normal(int(n * SR))


def _sos(kind, f, order):
    f = np.asarray(f, float)
    return signal.butter(order, float(f) / (SR / 2) if f.ndim == 0 else list(f / (SR / 2)), btype=kind, output="sos")


def lpf(x, fc, order=2):
    return signal.sosfilt(_sos("low", min(fc, SR * 0.45), order), x)


def hpf(x, fc, order=2):
    return signal.sosfilt(_sos("high", fc, order), x)


def bpf(x, lo, hi, order=2):
    return signal.sosfilt(_sos("band", [lo, min(hi, SR * 0.45)], order), x)


def env(n, tau, attack=0.0005):
    t = tt(n)
    return np.exp(-t / tau) * (1 - np.exp(-t / max(attack, 1e-5)))


def place(buf, snd, at, g=1.0):
    i = int(at * SR)
    if i >= len(buf):
        return
    j = min(len(buf), i + len(snd))
    buf[i:j] += g * snd[: j - i]


def limiter(x, thr=0.84, look=0.004):
    """Look-ahead peak limiter: smooth gain reduction, never clips."""
    L = max(1, int(look * SR))
    peak = maximum_filter1d(np.abs(x), 2 * L + 1)
    g = np.minimum(1.0, thr / np.maximum(peak, 1e-9))
    g = minimum_filter1d(g, 2 * L + 1)
    g = uniform_filter1d(g, 2 * L + 1)
    return x * g


def room(x, t60=1.2, pre=0.012, bright=1.0, wet=0.5):
    """Synthetic outdoor/room reverb: three decaying noise bands (airy highs die first, the low boom lingers)."""
    n = int((t60 + pre) * SR)
    ir = np.zeros(n)
    t = np.arange(n) / SR
    for fc, tau, gain in ((6000 * bright, t60 * 0.07, 0.35), (1800, t60 * 0.16, 0.7), (500, t60 * 0.32, 1.0)):
        ir += gain * lpf(rng.standard_normal(n), fc, 1) * np.exp(-np.maximum(t - pre, 0) / tau)
    ir[: int(pre * SR)] = 0
    ir /= np.sqrt(np.sum(ir ** 2)) + 1e-9
    wetsig = signal.fftconvolve(x, ir)[: len(x)]
    wetsig *= np.sqrt(np.sum(x ** 2)) / (np.sqrt(np.sum(wetsig ** 2)) + 1e-9)
    return x * (1 - 0.3 * wet) + wet * wetsig


def finish(x, loud=2.0, thr=0.84, fade=0.04, hi=15000):
    x = lpf(x, hi, 2)
    x = x - np.mean(x)
    x = x / (np.percentile(np.abs(x), 99.0) + 1e-9) * 0.35 * loud
    x = limiter(x, thr)
    n = int(fade * SR)
    x[-n:] *= np.linspace(1, 0, n) ** 2
    return x


def sub_thump(dur, f0, f1, tau, amp):
    t = tt(dur)
    f = f1 + (f0 - f1) * np.exp(-t / 0.035)
    ph = 2 * np.pi * np.cumsum(f) / SR
    return np.sin(ph) * env(dur, tau, 0.002) * amp


def banded_burst(dur, t200, lo=55.0, hi=11000.0, tilt=0.0, nb=14):
    """A burst whose spectrum evolves like a real muzzle blast: every octave-ish band is its own noise burst with its own decay time,
    highs die first (crack -> bark -> boom -> rumble).  t200 = decay time of the 200 Hz band."""
    out = np.zeros(int(dur * SR))
    for fc in np.geomspace(lo, hi, nb):
        tau = t200 * (200.0 / fc) ** 0.55
        g = (fc / 200.0) ** tilt
        band = bpf(noise(dur), fc / 1.35, min(fc * 1.35, SR * 0.45), 2)
        out += g * band * env(dur, tau, 0.0003 if fc > 400 else 0.0012)
    return out


def nwave(g=1.0):
    """The sharp supersonic 'snap': a 0.2 ms positive/negative impulse pair, high-passed."""
    x = np.zeros(int(0.01 * SR))
    x[2] = 1.0
    x[2 + int(0.00022 * SR)] = -0.85
    return hpf(x, 1800, 2) * g


def shot(length, t200, f0, f1, crack, tail, t60, boom=1.0, seed=0, tilt=0.35, subamp=0.30):
    global rng
    rng = np.random.default_rng(100 + seed)
    b = np.zeros(int(length * SR))
    body = banded_burst(0.9, t200, tilt=tilt)
    place(b, body, 0.0, 1.0)
    place(b, nwave(5.0 * crack), 0.0, 1.0)
    place(b, bpf(noise(0.04), 2500, 9500) * env(0.04, 0.0025, 0.0001), 0.0, 1.1 * crack)
    place(b, sub_thump(0.7, f0, f1, 0.17, subamp * boom), 0.0, 1.0)
    early = lpf(b[: int(0.3 * SR)].copy(), 3200, 1)
    for k, (d, g, fc) in enumerate(((0.019, 0.50, 3500), (0.034, 0.40, 3000), (0.052, 0.32, 2400), (0.083, 0.25, 1800), (0.121, 0.18, 1400), (0.19, 0.12, 1000))):
        place(b, lpf(early, fc, 1), d + 0.002 * k, g * tail)                     # discrete early reflections (trees, buildings, ground)
    wet = room(b, t60=t60, pre=0.02, wet=1.0)
    return finish(b * 0.8 + wet * 0.75 * tail, loud=2.1, thr=0.86, fade=0.12)


# ------------------------------------------------------------------------- mechanical handling sounds
def ring(x, f0, q):
    b, a = signal.iirpeak(f0 / (SR / 2), q)
    return signal.lfilter(b, a, x)


def metal_hit(f, amp=1.0, dur=0.14, low=420, q=45, body=1.0):
    """Metal on metal: a short noise impact excites high-Q resonators at inharmonic ratios (noise-like ringing, not pure tones),
    plus a dull body thud."""
    n = int(dur * SR)
    exc = hpf(noise(dur), 600, 1) * env(dur, 0.0012, 0.00005)
    x = 0.8 * exc
    for r, g, qq in ((1.0, 1.0, q), (1.47 * rng.uniform(.97, 1.03), 0.8, q * 0.8), (2.31 * rng.uniform(.97, 1.03), 0.55, q * 0.7), (3.4, 0.35, q * 0.6)):
        x += g * 0.12 * ring(exc * 6, f * r, qq)
    x += body * lpf(noise(dur), low, 2) * env(dur, 0.013, 0.0004) * 1.7
    return x * amp


def scrape(dur, lo=1200, hi=6500, amp=0.5, swell=1.4, sweep=0.0):
    """Noise scrape with a bandpass that slides (metal parts sliding on each other)."""
    n = int(dur * SR)
    base = noise(dur)
    out = np.zeros(n)
    win = 8
    seg = n // win
    for i in range(win + 1):
        k = (i / win)
        cf = (lo * hi) ** 0.5 * (1 + sweep * (k - 0.5))
        band = bpf(base, max(200, cf / 1.8), min(cf * 1.8, SR * 0.45), 2)
        w = np.zeros(n)
        c = int(k * n)
        h = np.hanning(2 * seg)
        a0, a1 = max(0, c - seg), min(n, c + seg)
        w[a0:a1] = h[(a0 - (c - seg)): (a0 - (c - seg)) + (a1 - a0)]
        out += band * w
    r = np.sin(np.linspace(0, np.pi, n)) ** swell
    return out * r * amp * (0.75 + 0.25 * np.sin(np.linspace(0, 55, n)))


def mech(parts, length, loud=1.9, t60=0.22, wet=0.35, seed=0):
    global rng
    b = np.zeros(int(length * SR))
    for fn, at, g in parts:
        rng = np.random.default_rng(900 + seed + int(at * 1000))
        place(b, fn(), at, g)
    rng = np.random.default_rng(5 + seed)
    return finish(room(b, t60=t60, pre=0.004, wet=wet), loud=loud, thr=0.82, fade=0.03)


def make_sounds():
    s = {}
    s["shot_heavy"] = [shot(2.4, 0.075, 95, 38, 1.0, 1.0, 1.7, 1.15, seed=i, tilt=0.38, subamp=0.30) for i in range(3)]
    s["shot"] = [shot(2.0, 0.060, 115, 46, 1.0, 0.9, 1.4, 1.0, seed=10 + i, tilt=0.42, subamp=0.26) for i in range(3)]
    s["shot_light"] = [shot(1.5, 0.040, 150, 62, 1.1, 0.8, 1.0, 0.8, seed=20 + i, tilt=0.55, subamp=0.16) for i in range(3)]
    for k, name in (("shot_heavy", "shot_heavy_supp"), ("shot", "shot_supp"), ("shot_light", "shot_light_supp")):
        s[name] = [lpf(x, 9500, 2) * 0.6 for x in s[k]]          # suppressed = the same shot, exactly 40% quieter (mild high-cut)
    H = lambda f, a=1.0, **k: (lambda: metal_hit(f, a, **k))
    S = lambda *a, **k: (lambda: scrape(*a, **k))
    s["click"] = [mech([(H(3100), 0.0, 1.0), (H(2500, 0.8), 0.075, 0.9)], 0.25, seed=i) for i in range(2)]
    s["click_dry"] = [mech([(H(2700), 0.0, 1.0)], 0.16, seed=i) for i in range(2)]
    s["bolt_open"] = [mech([(H(2300, 0.8), 0.0, 0.8), (S(0.10, 1500, 5500, 0.45, sweep=0.5), 0.03, 1.0),
                            (H(1700, 1.0, dur=0.16, low=360), 0.14, 1.2)], 0.42, seed=i) for i in range(2)]
    s["bolt_close"] = [mech([(S(0.09, 1300, 5200, 0.4, sweep=-0.5), 0.0, 1.0), (H(1500, 1.0, dur=0.18, low=330), 0.085, 1.5),
                             (H(2800, 0.6), 0.1, 0.7), (H(2200, 0.6), 0.17, 0.7)], 0.45, seed=i) for i in range(2)]
    s["mag_out"] = [mech([(H(2000, 0.9), 0.0, 1.0), (S(0.09, 900, 4200, 0.5, sweep=0.6), 0.02, 0.9),
                          (H(1200, 0.7, dur=0.16, low=300), 0.1, 0.8)], 0.34, seed=i) for i in range(2)]
    s["mag_in"] = [mech([(S(0.12, 900, 4200, 0.4, sweep=-0.6), 0.0, 0.9), (H(1400, 1.0, dur=0.18, low=320), 0.115, 1.6),
                         (H(1900, 0.5), 0.2, 0.5)], 0.4, seed=i) for i in range(2)]
    s["rack"] = [mech([(H(2200, 0.9), 0.0, 1.0), (S(0.16, 1200, 5600, 0.5, sweep=0.6), 0.04, 1.0),
                       (H(1500, 1.0, dur=0.18, low=330), 0.25, 1.5)], 0.5, seed=i) for i in range(2)]

    def shell_fn(f):
        def fn():
            n = int(0.2 * SR)
            exc = hpf(noise(0.2), 1500, 1) * env(0.2, 0.0015, 0.00005)
            x = 0.9 * ring(exc * 8, f, 55) + 0.6 * ring(exc * 8, f * 1.52, 40) + 0.3 * ring(exc * 8, f * 2.4, 30)
            return x * 0.25
        return fn
    s["shell"] = [mech([(shell_fn(5200), 0.0, 1.0), (shell_fn(4700), 0.11, 0.6), (shell_fn(5600), 0.19, 0.35), (shell_fn(5000), 0.25, 0.2)],
                       0.5, loud=1.5, t60=0.25, wet=0.3, seed=i) for i in range(2)]
    return s


sounds = make_sounds()
events = {}
for name, variants in sounds.items():
    files = []
    for i, x in enumerate(variants):
        assert np.max(np.abs(x)) <= 1.0
        fn = name if len(variants) == 1 else f"{name}_v{i + 1}"
        wav = os.path.join(OUT, fn + ".wav")
        with wave.open(wav, "wb") as w:
            w.setnchannels(1); w.setsampwidth(2); w.setframerate(SR)
            w.writeframes((np.clip(x, -1, 1) * 32000).astype("<i2").tobytes())
        subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-i", wav, "-af", "volume=-0.5dB", "-c:a", "libvorbis", "-q:a", "8", os.path.join(OUT, fn + ".ogg")], check=True)
        os.remove(wav)
        files.append({"name": "boltrifle:" + fn, "stream": False})
    x = variants[0]
    events[name] = {"sounds": files, "subtitle": "boltrifle.sound." + name}
    print(f"{name:16s} x{len(variants)} peak {20*np.log10(np.max(np.abs(x))+1e-9):6.1f} dB  rms300ms {20*np.log10(np.sqrt(np.mean(x[:int(.3*SR)]**2))+1e-9):6.1f} dB")
json.dump(events, open(os.path.join(RES, "assets", "boltrifle", "sounds.json"), "w"), indent=1)
