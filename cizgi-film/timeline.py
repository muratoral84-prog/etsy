# Seslendirmeleri cümlelere hizalar, duraklamaları ekler ve
# build/timeline.json + build/narration.wav + build/altyazi.srt üretir.
import json, os, subprocess
import numpy as np
from script import SCENES

SR = 48000
TEMPO = 0.94          # çocuklar için biraz yavaşlatılmış anlatım
TITLE = 7.0           # açılış jeneriği
LEAD, TAIL = 0.8, 1.4 # sahne başı / sonu boşluk
END = 16.0            # kapanış kartı (YouTube bitiş ekranı için)
BUILD = os.path.join(os.path.dirname(os.path.abspath(__file__)), "build")
AUDIO = os.path.join(os.path.dirname(os.path.abspath(__file__)), "audio")


def load(path):
    raw = subprocess.run(["ffmpeg", "-v", "error", "-i", path, "-af", f"atempo={TEMPO}",
                          "-ac", "1", "-ar", str(SR), "-f", "f32le", "-"],
                         capture_output=True, check=True).stdout
    return np.frombuffer(raw, np.float32).copy()


def silences(x, win=0.01, min_len=0.12):
    n = int(SR * win)
    fr = x[: len(x) // n * n].reshape(-1, n)
    rms = np.sqrt((fr ** 2).mean(1) + 1e-12)
    thr = max(rms.max() * 0.04, 1e-4)
    quiet = rms < thr
    out, i = [], 0
    while i < len(quiet):
        if quiet[i]:
            j = i
            while j < len(quiet) and quiet[j]:
                j += 1
            if (j - i) * win >= min_len:
                out.append((i * win, j * win))
            i = j
        else:
            i += 1
    return out


def align(x, lines):
    """N cümle için N-1 sınır seç (sessizlik ortaları), DP ile."""
    dur = len(x) / SR
    sil = silences(x)
    s0 = sil[0][1] if sil and sil[0][0] == 0 else 0.0
    e0 = sil[-1][0] if sil and sil[-1][1] >= dur - 0.02 else dur
    inner = [(a, b) for a, b in sil if a > s0 + 0.05 and b < e0 - 0.05]
    w = np.array([len(t) + 6 for t, _, _ in lines], float)
    cum = np.cumsum(w)[:-1] / w.sum()
    exp = s0 + cum * (e0 - s0)
    k, m = len(exp), len(inner)
    mids = np.array([(a + b) / 2 for a, b in inner])
    lens = np.array([b - a for a, b in inner])
    if m >= k and k > 0:
        INF = 1e9
        cost = np.full((k, m), INF)
        back = np.zeros((k, m), int)
        for j in range(m):
            cost[0, j] = abs(mids[j] - exp[0]) - 0.8 * min(lens[j], 0.7)
        for i in range(1, k):
            best, bj = INF, -1
            for j in range(m):
                if j - 1 >= 0 and cost[i - 1, j - 1] < best:
                    best, bj = cost[i - 1, j - 1], j - 1
                if bj >= 0:
                    cost[i, j] = best + abs(mids[j] - exp[i]) - 0.8 * min(lens[j], 0.7)
                    back[i, j] = bj
        j = int(np.argmin(cost[k - 1]))
        pick = [0] * k
        for i in range(k - 1, -1, -1):
            pick[i] = j
            j = back[i, j]
        bounds = [inner[p] for p in pick]
    else:
        bounds = [(e - 0.05, e + 0.05) for e in exp]
    # cümle konuşma aralıkları
    segs, prev = [], s0
    for a, b in bounds:
        segs.append((prev, a))
        prev = b
    segs.append((prev, e0))
    cuts = [0.0] + [(a + b) / 2 for a, b in bounds] + [dur]
    return segs, cuts


def main():
    os.makedirs(BUILD, exist_ok=True)
    out_audio = [np.zeros(int(TITLE * SR), np.float32)]
    t = TITLE
    scenes, srt = [], []
    for sc in SCENES:
        x = load(os.path.join(AUDIO, sc["id"] + ".mp3"))
        segs, cuts = align(x, sc["lines"])
        start = t
        out_audio.append(np.zeros(int(LEAD * SR), np.float32))
        t += LEAD
        sents = []
        for i, (text, spk, ev) in enumerate(sc["lines"]):
            c0, c1 = cuts[i], cuts[i + 1]
            piece = x[int(c0 * SR): int(c1 * SR)]
            s_abs = t + (segs[i][0] - c0)
            e_abs = t + (segs[i][1] - c0)
            out_audio.append(piece)
            t += len(piece) / SR
            pause = sum(float(e.split(":")[1]) for e in ev if e.startswith("pause:"))
            if pause:
                out_audio.append(np.zeros(int(pause * SR), np.float32))
                t += pause
            sents.append(dict(text=text, speaker=spk, start=round(s_abs, 3),
                              end=round(e_abs, 3), wait_end=round(t, 3),
                              events=[e for e in ev if not e.startswith("pause:")]))
        out_audio.append(np.zeros(int(TAIL * SR), np.float32))
        t += TAIL
        scenes.append(dict(id=sc["id"], bg=sc["bg"], start=round(start, 3), end=round(t, 3),
                           sentences=sents))
    out_audio.append(np.zeros(int(END * SR), np.float32))
    t += END
    audio = np.concatenate(out_audio)
    total = len(audio) / SR

    # olayları mutlak zamana çevir
    events = []
    for sc in scenes:
        for s in sc["sentences"]:
            groups = {}
            for e in s["events"]:
                groups.setdefault(e.split(":")[0], []).append(e)
            for kind, evs in groups.items():
                d = max(s["end"] - s["start"], 0.3)
                for i, e in enumerate(evs):
                    if len(evs) > 1:
                        et = s["start"] + d * (i + 0.15) / len(evs)
                    elif kind == "collect":
                        et = s["start"] + d * 0.4
                    else:
                        et = s["start"]
                    events.append(dict(t=round(et, 3), ev=e, scene=sc["id"],
                                       end=s["wait_end"]))
    events.sort(key=lambda e: e["t"])

    with open(os.path.join(BUILD, "timeline.json"), "w") as f:
        json.dump(dict(total=total, title=TITLE, end=END, scenes=scenes, events=events),
                  f, ensure_ascii=False, indent=1)
    subprocess.run(["ffmpeg", "-y", "-v", "error", "-f", "f32le", "-ar", str(SR), "-ac", "1",
                    "-i", "-", os.path.join(BUILD, "narration.wav")],
                   input=audio.tobytes(), check=True)

    def ts(v):
        h, r = divmod(v, 3600); m, s = divmod(r, 60)
        return f"{int(h):02d}:{int(m):02d}:{int(s):02d},{int(round((s % 1) * 1000)) % 1000:03d}"
    n = 1
    for sc in scenes:
        for s in sc["sentences"]:
            srt.append(f"{n}\n{ts(s['start'])} --> {ts(max(s['end'], s['start'] + 0.8))}\n{s['text']}\n")
            n += 1
    with open(os.path.join(BUILD, "altyazi.srt"), "w") as f:
        f.write("\n".join(srt))
    print(f"toplam süre: {total:.1f} sn ({total / 60:.2f} dk)")
    for sc in scenes:
        print(sc["id"], sc["start"], sc["end"])


if __name__ == "__main__":
    main()
