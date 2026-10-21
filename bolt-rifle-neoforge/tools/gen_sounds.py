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


def shot(length, f0, f1, crack, tail, t60, boom=1.0):
    b = np.zeros(int(length * SR))
    place(b, hpf(noise(0.06), 1500) * env(0.06, 0.0028, 0.0001), 0.0, 1.9 * crack)                 # supersonic crack
    place(b, bpf(noise(0.12), 900, 7500) * env(0.12, 0.008, 0.0002), 0.0, 1.5 * crack)             # sharp edge of the blast
    place(b, bpf(noise(0.5), 140, 3200) * env(0.5, 0.05, 0.0008), 0.0, 2.0)                         # the blast itself
    place(b, bpf(noise(0.3), 380, 1700) * env(0.3, 0.075, 0.001), 0.001, 1.3)                      # mid bark
    place(b, sub_thump(0.7, f0, f1, 0.16, 0.9 * boom), 0.0, 1.0)                                    # chest-thumping boom
    place(b, lpf(noise(0.9), 260, 2) * env(0.9, 0.28, 0.003) * 1.1 * boom, 0.003, 0.9)             # low rumble
    dry = b
    wet = room(dry, t60=t60, pre=0.014, wet=1.0)
    out = dry * 0.75 + wet * 0.7 * tail
    return finish(out, loud=2.1, thr=0.86, fade=0.12)


# ------------------------------------------------------------------------- mechanical handling sounds
def metal_hit(f, tau=0.012, amp=1.0, dur=0.12, low=420):
    """A real-sounding metal impact: noise transient + a few quickly damped resonant modes + a body thud."""
    n = int(dur * SR)
    t = np.arange(n) / SR
    x = bpf(noise(dur), f * 0.6, f * 3.2) * env(dur, 0.0022, 0.00008) * 1.4
    for m, g, ts in ((1.0, 0.30, tau), (1.62, 0.20, tau * 0.7), (2.71, 0.12, tau * 0.5), (4.1, 0.07, tau * 0.35)):
        x += g * np.sin(2 * np.pi * f * m * t + rng.uniform(0, 6.28)) * np.exp(-t / ts)
    x += lpf(noise(dur), low, 2) * env(dur, 0.014, 0.0004) * 1.6
    return x * amp


def scrape(dur, lo=1200, hi=6500, amp=0.5, swell=1.4):
    n = noise(dur)
    r = np.sin(np.linspace(0, np.pi, len(n))) ** swell
    return bpf(n, lo, hi) * r * amp * (0.7 + 0.3 * np.sin(np.linspace(0, 40, len(n))))


def mech(parts, length, loud=1.9, t60=0.22, wet=0.35):
    b = np.zeros(int(length * SR))
    for snd, at, g in parts:
        place(b, snd, at, g)
    return finish(room(b, t60=t60, pre=0.004, wet=wet), loud=loud, thr=0.82, fade=0.03)


def make_sounds():
    s = {}
    s["shot_heavy"] = shot(2.4, 95, 38, 1.0, 1.0, 1.7, boom=1.15)
    s["shot"] = shot(2.0, 115, 46, 1.0, 0.9, 1.4, boom=1.0)
    s["shot_light"] = shot(1.5, 150, 62, 1.1, 0.8, 1.0, boom=0.8)
    for k in ("shot_heavy", "shot", "shot_light"):                     # suppressed = the same shot, exactly 40% quieter (mild high-cut)
        s[k + "_supp" if k != "shot" else "shot_supp"] = lpf(s[k], 9500, 2) * 0.6
    s["click"] = mech([(metal_hit(3100, 0.008, 1.0), 0.0, 1.0), (metal_hit(2500, 0.010, 0.8), 0.075, 0.9)], 0.25, 2.0)
    s["click_dry"] = mech([(metal_hit(2700, 0.009, 1.0), 0.0, 1.0), (lpf(noise(0.03), 900) * env(0.03, 0.006), 0.012, 0.6)], 0.16, 2.0)
    s["bolt_open"] = mech([(metal_hit(2300, 0.010, 0.8), 0.0, 0.8), (scrape(0.10, 1500, 5500, 0.45), 0.03, 1.0),
                           (metal_hit(1700, 0.016, 1.0, 0.16, 360), 0.14, 1.2), (metal_hit(3400, 0.007, 0.5), 0.152, 0.6)], 0.42, 2.0)
    s["bolt_close"] = mech([(scrape(0.09, 1300, 5200, 0.4), 0.0, 1.0), (metal_hit(1500, 0.018, 1.0, 0.18, 330), 0.085, 1.4),
                            (metal_hit(2800, 0.008, 0.7), 0.1, 0.8), (metal_hit(2200, 0.009, 0.6), 0.17, 0.7)], 0.45, 2.0)
    s["mag_out"] = mech([(metal_hit(2000, 0.008, 0.9), 0.0, 1.0), (scrape(0.09, 900, 4200, 0.5), 0.02, 0.9),
                         (metal_hit(1200, 0.014, 0.7, 0.16, 300), 0.1, 0.8)], 0.34, 2.0)
    s["mag_in"] = mech([(scrape(0.12, 900, 4200, 0.4), 0.0, 0.9), (metal_hit(1400, 0.016, 1.0, 0.18, 320), 0.115, 1.5),
                        (metal_hit(2600, 0.008, 0.7), 0.125, 0.8), (metal_hit(1900, 0.010, 0.5), 0.2, 0.5)], 0.4, 2.0)
    s["rack"] = mech([(metal_hit(2200, 0.010, 0.9), 0.0, 1.0), (scrape(0.16, 1200, 5600, 0.5), 0.04, 1.0),
                      (metal_hit(1500, 0.018, 1.0, 0.18, 330), 0.25, 1.4), (metal_hit(3000, 0.007, 0.6), 0.255, 0.7)], 0.5, 2.0)
    brass = np.zeros(int(0.5 * SR))
    for at, f, g in ((0.0, 5200, 1.0), (0.11, 4700, 0.6), (0.19, 5600, 0.35), (0.25, 5000, 0.2)):
        tn = np.arange(int(0.2 * SR)) / SR
        h = np.sin(2 * np.pi * f * tn) * np.exp(-tn / 0.03) * 0.5 + np.sin(2 * np.pi * f * 1.52 * tn) * np.exp(-tn / 0.018) * 0.3
        h += bpf(noise(0.2), 3000, 9000) * env(0.2, 0.01, 0.0001) * 0.7
        place(brass, h, at, g)
    s["shell"] = finish(room(brass, 0.25, 0.004, 1.2, 0.3), loud=1.5, thr=0.8, fade=0.05)
    return s


sounds = make_sounds()
events = {}
for name, x in sounds.items():
    assert np.max(np.abs(x)) <= 1.0
    wav = os.path.join(OUT, name + ".wav")
    with wave.open(wav, "wb") as w:
        w.setnchannels(1); w.setsampwidth(2); w.setframerate(SR)
        w.writeframes((np.clip(x, -1, 1) * 32000).astype("<i2").tobytes())
    subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-i", wav, "-af", "volume=-0.5dB", "-c:a", "libvorbis", "-q:a", "8", os.path.join(OUT, name + ".ogg")], check=True)
    os.remove(wav)
    events[name] = {"sounds": [{"name": "boltrifle:" + name, "stream": False}], "subtitle": "boltrifle.sound." + name}
    print(f"{name:16s} peak {20*np.log10(np.max(np.abs(x))+1e-9):6.1f} dB  rms300ms {20*np.log10(np.sqrt(np.mean(x[:int(.3*SR)]**2))+1e-9):6.1f} dB")
json.dump(events, open(os.path.join(RES, "assets", "boltrifle", "sounds.json"), "w"), indent=1)
