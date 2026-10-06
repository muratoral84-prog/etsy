# Arka plan müziği + ses efektleri sentezler, anlatımla karıştırır -> build/final_audio.wav
import json, os, subprocess
import numpy as np

SR = 48000
HERE = os.path.dirname(os.path.abspath(__file__))
BUILD = os.path.join(HERE, "build")
T = json.load(open(os.path.join(BUILD, "timeline.json")))
N = int(T["total"] * SR) + SR
rng = np.random.default_rng(1)


def midi(n):
    return 440.0 * 2 ** ((n - 69) / 12)


def pluck(freq, dur, amp=0.3):
    """Karplus-Strong telli çalgı sesi (ukulele benzeri)"""
    n = int(dur * SR); p = max(2, int(SR / freq))
    buf = rng.uniform(-1, 1, p)
    out = np.empty(n)
    for i in range(n):
        out[i] = buf[i % p]
        buf[i % p] = 0.5 * (buf[i % p] + buf[(i + 1) % p]) * 0.996
    return out * amp


def tone(freq, dur, amp=0.2, kind="sine"):
    t = np.arange(int(dur * SR)) / SR
    if kind == "sine":
        w = np.sin(2 * np.pi * freq * t)
    else:
        w = np.sign(np.sin(2 * np.pi * freq * t)) * 0.4 + np.sin(2 * np.pi * freq * t) * 0.6
    env = np.minimum(1, t / 0.01) * np.exp(-t * 6)
    return w * env * amp


# ---------------------------------------------------------------- müzik döngüsü
BPM = 104; beat = 60 / BPM
prog = [(60, [60, 64, 67]), (55, [55, 59, 62]), (57, [57, 60, 64]), (53, [53, 57, 60])]  # C G Am F
melody = [72, 74, 76, 79, 76, 74, 72, None, 71, 72, 74, 71, 67, None, 69, 71,
          72, 76, 74, 72, 69, None, 67, 69, 65, 67, 69, 72, 69, 67, 65, None]
bars = len(prog) * 2
loop = np.zeros(int(bars * 4 * beat * SR) + SR)
cache = {}


def note(n, d, a):
    k = (n, d)
    if k not in cache:
        cache[k] = pluck(midi(n), d, 1.0)
    return cache[k] * a


for b in range(bars):
    root, ch = prog[b % len(prog)]
    t0 = b * 4 * beat
    for k in range(8):                       # arpej
        n = ch[[0, 1, 2, 1][k % 4]] + (12 if k >= 4 else 0)
        s = int((t0 + k * beat / 2) * SR); w = note(n, 0.8, 0.10)
        loop[s:s + len(w)] += w
    for k in (0, 2):                         # bas
        s = int((t0 + k * beat) * SR); w = tone(midi(root - 12), 0.9, 0.16)
        loop[s:s + len(w)] += w
    for k in range(4):                       # melodi (glockenspiel benzeri)
        n = melody[(b * 4 + k) % len(melody)]
        if n is None:
            continue
        s = int((t0 + k * beat) * SR); w = tone(midi(n), 0.6, 0.07) + tone(midi(n) * 2, 0.6, 0.02)
        loop[s:s + len(w)] += w
L = int(bars * 4 * beat * SR)
loop[:SR] += loop[L:L + SR]; loop = loop[:L]
music = np.tile(loop, N // L + 1)[:N]

# ---------------------------------------------------------------- efektler
sfx = np.zeros(N)


def add(t, w):
    s = int(t * SR)
    if s < 0 or s >= N:
        return
    e = min(N, s + len(w)); sfx[s:e] += w[: e - s]


def pop():
    t = np.arange(int(0.15 * SR)) / SR
    f = 400 + 900 * t / 0.15
    return np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-t * 25) * 0.35


def chime():
    return sum(tone(midi(n), 1.2, 0.12) for n in (84, 88, 91, 96))


def sparkle():
    w = np.zeros(int(1.0 * SR))
    for i, n in enumerate((88, 91, 93, 96, 100)):
        x = tone(midi(n), 0.5, 0.09); s = int(i * 0.07 * SR); w[s:s + len(x)] += x[: len(w) - s]
    return w


def boing():
    t = np.arange(int(0.4 * SR)) / SR
    f = 180 + 120 * np.sin(t * 40) * np.exp(-t * 4) + 200 * t
    return np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-t * 6) * 0.35


def thunder():
    n = int(2.5 * SR); x = rng.normal(0, 1, n)
    for _ in range(3):
        x = np.convolve(x, np.ones(40) / 40, "same")
    t = np.arange(n) / SR
    return x * np.exp(-t * 1.5) * 2.0


def rain(d):
    n = int(d * SR); x = rng.normal(0, 1, n)
    x = x - np.convolve(x, np.ones(8) / 8, "same")
    env = np.minimum(1, np.arange(n) / SR / 0.8) * np.minimum(1, (n - np.arange(n)) / SR / 0.8)
    return x * env * 0.06


def tada():
    w = np.zeros(int(2.0 * SR))
    for i, n in enumerate((72, 76, 79, 84)):
        x = pluck(midi(n), 1.6, 0.35); s = int(i * 0.09 * SR); w[s:s + len(x)] += x[: len(w) - s]
    return w


def whoosh():
    n = int(0.7 * SR); x = rng.normal(0, 1, n)
    x = np.convolve(x, np.ones(20) / 20, "same"); t = np.arange(n) / SR
    return x * np.sin(np.pi * t / 0.7) * 0.5


storm_on = None
for e in T["events"]:
    k = e["ev"].split(":")[0]; t = e["t"]
    if k in ("count", "carrot"):
        add(t, pop())
    elif k == "hop":
        add(t, boing())
    elif k == "collect":
        add(t, chime())
    elif k == "sparkle":
        add(t, sparkle())
    elif k == "rainbow":
        add(t, tone(midi(72 + [0, 2, 4, 5, 7, 9, 11][int(e["ev"][-1])]), 0.8, 0.18))
    elif k == "items":
        for i in range(3):
            add(t + i, pop() * 0.7)
    elif k == "storm" and storm_on is None:
        storm_on = t
    elif k == "calm" and storm_on is not None:
        add(storm_on, rain(t - storm_on + 1))
        for m in range(int(np.ceil(storm_on / 2.3)), int(t / 2.3) + 1):
            add(m * 2.3 + 0.1, thunder())
    elif k == "celebrate":
        add(t, tada())
for sc in T["scenes"][1:]:
    add(sc["start"] - 0.4, whoosh())
add(T["scenes"][-1]["end"], tada())

# ---------------------------------------------------------------- karıştırma
raw = subprocess.run(["ffmpeg", "-v", "error", "-i", os.path.join(BUILD, "narration.wav"),
                      "-ac", "1", "-ar", str(SR), "-f", "f32le", "-"], capture_output=True, check=True).stdout
voice = np.zeros(N); v = np.frombuffer(raw, np.float32); voice[: len(v)] = v[:N]
# müzik kısma (ducking)
win = int(0.05 * SR)
env = np.sqrt(np.convolve(voice ** 2, np.ones(win) / win, "same"))
active = (env > 0.01).astype(float)
k = int(0.4 * SR)
active = np.convolve(active, np.ones(k) / k, "same")
active = np.clip(active * 3, 0, 1)
mlevel = 0.55 - 0.40 * active
music *= mlevel / (np.abs(music).max() + 1e-6) * 0.5
# başlık/kapanışta müzik yüksek, sonda yavaşça kıs
t = np.arange(N) / SR
fade = np.clip((T["total"] - t) / 3.0, 0, 1) * np.clip(t / 1.0, 0, 1)
mix = voice * 1.0 + music * fade + sfx * 0.6
mix /= max(1.0, np.abs(mix).max() / 0.95)
stereo = np.stack([mix, mix], 1).astype(np.float32)
subprocess.run(["ffmpeg", "-y", "-v", "error", "-f", "f32le", "-ar", str(SR), "-ac", "2", "-i", "-",
                "-af", "loudnorm=I=-16:TP=-1.5:LRA=11", "-ar", str(SR), os.path.join(BUILD, "final_audio.wav")],
               input=stereo.tobytes(), check=True)
print("ses hazır")
