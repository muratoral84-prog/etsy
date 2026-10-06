# Pıtırcık çizgi filmi — kare kare render (pycairo -> ffmpeg)
# Kullanım: python3 render.py            (tam video, paralel)
#           python3 render.py --png 12.5 100 300   (belirli saniyelerden önizleme)
import json, math, os, subprocess, sys, random
from multiprocessing import Pool
import numpy as np
import cairo
from draw import *

FPS = 24
HERE = os.path.dirname(os.path.abspath(__file__))
BUILD = os.path.join(HERE, "build")
T = json.load(open(os.path.join(BUILD, "timeline.json")))
TOTAL = T["total"]
SCENES = T["scenes"]
EVENTS = T["events"]
CHAR_SPK = {"pitircik", "pamuk", "civil", "baykus", "virak"}


def load_env():
    raw = subprocess.run(["ffmpeg", "-v", "error", "-i", os.path.join(BUILD, "narration.wav"),
                          "-ac", "1", "-ar", "24000", "-f", "f32le", "-"], capture_output=True, check=True).stdout
    x = np.frombuffer(raw, np.float32)
    n = 24000 // FPS
    fr = x[: len(x) // n * n].reshape(-1, n)
    rms = np.sqrt((fr ** 2).mean(1))
    rms = rms / (np.percentile(rms, 98) + 1e-6)
    return np.clip(rms * 1.3, 0, 1)


ENV = None


def evs(prefix, scene=None):
    return [e for e in EVENTS if e["ev"].startswith(prefix) and (scene is None or e["scene"] == scene)]


def ev_time(prefix, scene=None, default=1e9):
    l = evs(prefix, scene)
    return l[0]["t"] if l else default


def scene_at(t):
    for s in SCENES:
        if s["start"] <= t < s["end"]:
            return s
    return None


def speaker_at(sc, t):
    for s in sc["sentences"]:
        if s["start"] - 0.05 <= t <= s["end"] + 0.05:
            return s["speaker"]
    return None


def collected(t):
    return [int(e["ev"].split(":")[1]) for e in evs("collect:") if e["t"] + 1.6 <= t]


def blink(t, off):
    return ((t + off) % 3.7) < 0.13


def walk_x(sc, t, target, delay=0.0):
    """Sahne başında soldan yürüyerek giriş."""
    dur = 3.2
    k = ease_io((t - sc["start"] - 0.2 - delay) / dur)
    return -380 + (target + 380) * k, (0 < k < 1)


LAYERS = {}


def layers(bg):
    if bg not in LAYERS:
        LAYERS[bg] = make_layers(bg)
    return LAYERS[bg]


CLOUDS = [(random.Random(i).uniform(0, W), random.Random(i + 50).uniform(80, 330),
           random.Random(i + 99).uniform(0.6, 1.2)) for i in range(6)]


def draw_clouds(cr, t, alpha=1.0, col=(1, 1, 1)):
    for x, y, s in CLOUDS:
        xx = (x + t * 12 * s) % (W + 400) - 200
        cloud(cr, xx, y, s, 0.9 * alpha, col)


# ---------------------------------------------------------------- HUD / efektler
def hud(cr, t, glow_idx=None):
    got = collected(t)
    cr.save()
    rrect(cr, 30, 24, 7 * 66 + 26, 86, 40); cr.set_source_rgba(1, 1, 1, 0.85); cr.fill_preserve()
    cr.set_source_rgb(0.4, 0.3, 0.5); cr.set_line_width(4); cr.stroke()
    for i in range(7):
        x, y = 76 + i * 66, 67
        if i in got:
            pulse = 1.0
            for e in evs("collect:%d" % i):
                d = t - (e["t"] + 1.6)
                if 0 <= d < 0.5:
                    pulse = 1 + 0.5 * math.sin(d / 0.5 * PI)
            cr.arc(x, y, 24 * pulse, 0, 2 * PI); paint(cr, COLORS[i], 4)
            cr.arc(x - 7, y - 8, 6, 0, 2 * PI); cr.set_source_rgba(1, 1, 1, 0.8); cr.fill()
        else:
            cr.arc(x, y, 22, 0, 2 * PI); cr.set_source_rgba(0.8, 0.8, 0.85, 0.6); cr.fill_preserve()
            cr.set_dash([6, 6]); cr.set_source_rgb(0.55, 0.55, 0.6); cr.set_line_width(3); cr.stroke(); cr.set_dash([])
    cr.restore()


def hud_slot(i):
    return 76 + i * 66, 67


def color_banner(cr, t):
    """collect olayında: ortada büyük renk dairesi + adı, sonra HUD'a uçuş."""
    for e in evs("collect:"):
        i = int(e["ev"].split(":")[1]); d = t - e["t"]
        if 0 <= d < 2.6:
            if d < 1.6:
                s = ease_out_back(d / 0.45)
                x, y, r = W / 2, 430, 120 * s
                g = cairo.RadialGradient(x, y, r * 0.3, x, y, r * 2.2)
                g.add_color_stop_rgba(0, *lighten(COLORS[i], 0.5), 0.7); g.add_color_stop_rgba(1, 1, 1, 1, 0)
                cr.set_source(g); cr.arc(x, y, r * 2.2, 0, 2 * PI); cr.fill()
                for k in range(10):
                    a = k * PI / 5 + d * 2
                    star(cr, x + math.cos(a) * r * 1.5, y + math.sin(a) * r * 1.5, 18 * s, 5, 0.45, d)
                    cr.set_source_rgb(1, 0.95, 0.5); cr.fill()
                cr.arc(x, y, r, 0, 2 * PI); paint(cr, COLORS[i], 7, (1, 1, 1))
                cr.arc(x - r * 0.3, y - r * 0.35, r * 0.2, 0, 2 * PI); cr.set_source_rgba(1, 1, 1, 0.7); cr.fill()
                text(cr, NAMES[i], x, y + 200, 110 * min(1, s), COLORS[i], (1, 1, 1), 16)
            else:
                k = ease_io((d - 1.6) / 1.0)
                sx, sy = hud_slot(i)
                x = W / 2 + (sx - W / 2) * k; y = 430 + (sy - 430) * k - math.sin(k * PI) * 120
                r = 120 * (1 - k) + 24 * k
                for j in range(6):
                    kk = max(0, k - j * 0.04)
                    xx = W / 2 + (sx - W / 2) * kk; yy = 430 + (sy - 430) * kk - math.sin(kk * PI) * 120
                    star(cr, xx, yy, 12, 5, 0.45); cr.set_source_rgba(1, 0.95, 0.5, 0.8 - j * 0.12); cr.fill()
                cr.arc(x, y, r, 0, 2 * PI); paint(cr, COLORS[i], 5, (1, 1, 1))


def count_badge(cr, t, sc_id):
    """count olayları: üst ortada büyük rakam + Türkçe sözcük."""
    cur = None
    for e in evs("count:", sc_id) + evs("hop:", sc_id) + evs("carrot:", sc_id):
        if e["t"] <= t < e["t"] + 1.3:
            cur = e
    if not cur:
        return
    n = int(cur["ev"].split(":")[1]); d = t - cur["t"]
    s = ease_out_back(d / 0.35); a = 1 if d < 1.0 else max(0, 1 - (d - 1.0) / 0.3)
    cr.save(); cr.translate(W / 2 + 350, 250); cr.scale(s, s)
    cr.arc(0, 0, 110, 0, 2 * PI); cr.set_source_rgba(1, 1, 1, 0.9 * a); cr.fill_preserve()
    cr.set_source_rgba(0.95, 0.45, 0.6, a); cr.set_line_width(10); cr.stroke()
    text(cr, str(n), 0, -12, 150, (0.95, 0.4, 0.55), (1, 1, 1), 10, alpha=a)
    text(cr, NUMS[n], 0, 150, 70, (1, 1, 1), (0.95, 0.4, 0.55), 14, alpha=a)
    cr.restore()


def num_tag(cr, x, y, n, a=1.0):
    cr.arc(x, y, 30, 0, 2 * PI); cr.set_source_rgba(1, 1, 1, a); cr.fill_preserve()
    cr.set_source_rgba(0.95, 0.4, 0.55, a); cr.set_line_width(5); cr.stroke()
    text(cr, str(n), x, y - 4, 42, (0.95, 0.4, 0.55), (1, 1, 1), 4, alpha=a)


def counted(sc_id, prefix, t):
    """kaç tane sayıldı (o ana kadar)"""
    return [int(e["ev"].split(":")[1]) for e in evs(prefix, sc_id) if e["t"] <= t]


def items_panel(cr, t, sc_id):
    for e in evs("items:", sc_id):
        names = e["ev"].split(":")[1].split(",")
        if not (e["t"] - 0.1 <= t < e["end"] + 1.5):
            continue
        fade = min(1, (e["end"] + 1.5 - t) / 0.4)
        n = len(names)
        span = 3.0
        for i, nm in enumerate(names):
            ti = e["t"] + i * span / n
            d = t - ti
            if d < 0:
                continue
            s = ease_out_back(d / 0.4) * fade
            x = W / 2 - (n - 1) * 170 + i * 340; y = 300
            cr.save(); cr.translate(x, y); cr.scale(s, s)
            rrect(cr, -140, -130, 280, 290, 40); cr.set_source_rgba(1, 1, 1, 0.92); cr.fill_preserve()
            cr.set_source_rgb(0.95, 0.75, 0.3); cr.set_line_width(6); cr.stroke()
            icon(cr, nm, 0, -20, 1.4, t)
            text(cr, ITEM_NAMES[nm], 0, 110, 46, (0.35, 0.25, 0.5), (1, 1, 1), 6)
            cr.restore()


def sparkles(cr, t, x, y, t0, dur=1.5, col=(1, 0.95, 0.5)):
    d = t - t0
    if not (0 <= d < dur):
        return
    rnd = random.Random(int(t0 * 100))
    for k in range(18):
        a = rnd.uniform(0, 2 * PI); sp = rnd.uniform(120, 320)
        r = sp * (d / dur) ** 0.6
        star(cr, x + math.cos(a) * r, y + math.sin(a) * r - 60 * d, 14 * (1 - d / dur) + 4, 5, 0.45, d * 3)
        cr.set_source_rgba(*col, 1 - d / dur); cr.fill()


def confetti(cr, t, t0):
    d = t - t0
    if d < 0:
        return
    rnd = random.Random(7)
    for k in range(120):
        x0 = rnd.uniform(0, W); sp = rnd.uniform(120, 260); ph = rnd.uniform(0, 6)
        c = COLORS[k % 7]
        y = -40 + ((d * sp + rnd.uniform(0, H)) % (H + 80))
        x = x0 + math.sin(d * 2 + ph) * 40
        cr.save(); cr.translate(x, y); cr.rotate(d * 3 + ph); cr.rectangle(-8, -5, 16, 10)
        cr.set_source_rgb(*c); cr.fill(); cr.restore()


# ---------------------------------------------------------------- sahneler
def talk_of(sc, t, who, f):
    return ENV[min(f, len(ENV) - 1)] if speaker_at(sc, t) == who else 0.0


def scene_common_party(cr, sc, t, f, show_pamuk, show_civil, px=640, carry=None, mood="happy",
                       pamuk_x=380, civil_pos=(830, 520), basket_on="pit"):
    got = collected(t)
    celebrate = ev_time("celebrate", sc["id"])
    jump = lambda ph: abs(math.sin((t + ph) * 5)) * 50 if t >= celebrate else 0
    if show_pamuk:
        x, walking = walk_x(sc, t, pamuk_x, 0.3)
        b = abs(math.sin(t * 9)) * 14 if walking else 0
        bunny(cr, x, 930 - b - jump(0.3), 0.95, t, talk_of(sc, t, "pamuk", f), blink(t, 1.1),
              basket_colors=got if basket_on == "pamuk" else None)
    if show_civil:
        x, walking = walk_x(sc, t, civil_pos[0], 0.1)
        bird(cr, x, civil_pos[1] + math.sin(t * 2.5) * 18, 0.95, t, talk_of(sc, t, "civil", f), blink(t, 2.3))
    x, walking = walk_x(sc, t, px)
    b = abs(math.sin(t * 9)) * 14 if walking else 0
    hedgehog(cr, x, 935 - b - jump(0), 1.0, t, talk_of(sc, t, "pitircik", f), blink(t, 0),
             mood=mood, basket_colors=got if basket_on == "pit" else None)


def s_orman(cr, t, f, sc, final=False):
    back, front = layers("orman" if not final else "final")
    cr.set_source_surface(back); cr.paint()
    sid = sc["id"]
    if not final:
        st, calm = ev_time("storm", sid), ev_time("calm", sid)
        storm = 1.0 if st <= t < calm else 0.0
        if st <= t < st + 0.8:
            storm = (t - st) / 0.8
        if calm <= t < calm + 1.2:
            storm = 1 - (t - calm) / 1.2
    else:
        storm = 0.0
    if not final:
        sun(cr, 1650, 170, 70, t)
    else:
        sun(cr, 1650, 170, 70, t)
    # gökkuşağı
    if final:
        fills = []
        for i in range(7):
            e = evs("rainbow:%d" % i, sid)
            fills.append(min(1, max(0, (t - e[0]["t"]) / 0.5)) if e else 0)
        rainbow(cr, 1150, 840, 620, 44, fills, 1.0, t)
    else:
        calm = ev_time("calm", sid)
        if t >= calm or t < ev_time("storm", sid):
            rainbow(cr, 1150, 840, 620, 44, [0] * 7, 1.0, t)
    draw_clouds(cr, t)
    cr.set_source_surface(front); cr.paint()
    # baykuş
    be = ev_time("enter:baykus", sid)
    if t >= be - 0.01:
        k = ease_io((t - be) / 1.2)
        ox, oy = 360 + (1 - k) * -300, 590 - (1 - k) * 300
        wings = (1 - k) * abs(math.sin(t * 10))
        sp = speaker_at(sc, t)
        if sp == "baykus" and final:
            wings = max(wings, 0.3 + 0.2 * math.sin(t * 3))
        owl(cr, ox, oy, 0.9, t, talk_of(sc, t, "baykus", f), blink(t, 0.7), wings)
    if not final:
        got = []
        en = ev_time("enter:pitircik", sid)
        hide = 1.0
        if t >= en:
            hide = 1 - ease_io((t - en) / 0.8)
        st, calm = ev_time("storm", sid), ev_time("calm", sid)
        if st <= t < calm + 0.6:
            hide = 1.0 if t < calm else 1 - ease_io((t - calm) / 0.6)
        mood = "happy"
        if ev_time("surprise", sid) <= t < ev_time("enter:baykus", sid):
            mood = "surprise"
        jump = 0
        sp_t = ev_time("surprise", sid)
        if sp_t <= t < sp_t + 0.6:
            jump = math.sin((t - sp_t) / 0.6 * PI) * 60
        look = (0.3, -1) if t >= ev_time("look_up", sid) and t < ev_time("enter:baykus", sid) else (0, 0)
        cr.save(); cr.rectangle(0, 0, W, 925); cr.clip()
        if hide < 1:
            hedgehog(cr, 820, 930 + hide * 230 - jump, 0.95, t, talk_of(sc, t, "pitircik", f), blink(t, 0),
                     mood=mood, basket_colors=[] if t >= ev_time("basket", sid) else None,
                     wave=1.0 if en <= t < en + 3 else 0.0, look=look)
        cr.restore()
        if storm > 0:
            cr.set_source_rgba(0.12, 0.13, 0.25, 0.6 * storm); cr.paint()
            rnd = random.Random(int(t * 24))
            cr.set_source_rgba(0.75, 0.85, 1, 0.6 * storm); cr.set_line_width(3)
            for k in range(140):
                x = rnd.uniform(0, W); y = rnd.uniform(0, H)
                cr.move_to(x, y); cr.line_to(x - 12, y + 40)
            cr.stroke()
            if (t % 2.3) < 0.12:
                cr.set_source_rgba(1, 1, 1, 0.55 * storm); cr.paint()
            for x, y, s in CLOUDS[:4]:
                cloud(cr, (x + t * 30) % W, y - 40, s * 1.4, 0.9 * storm, (0.45, 0.47, 0.55))
        # renkler tanıtımı
        sc_t = ev_time("show_colors", sid)
        sent = [s for s in sc["sentences"] if "show_colors" in s["events"]]
        if sent and sc_t <= t < sent[0]["wait_end"] + 1.2:
            dur = sent[0]["end"] - sent[0]["start"]
            for i in range(7):
                ti = sc_t + dur * (0.3 + 0.68 * i / 7)
                d = t - ti
                if d < 0:
                    continue
                s = ease_out_back(d / 0.4)
                x = 360 + i * 200
                cr.arc(x, 330, 70 * s, 0, 2 * PI); paint(cr, COLORS[i], 6, (1, 1, 1))
                text(cr, NAMES[i], x, 450, 40 * s, COLORS[i], (1, 1, 1), 8)
    else:
        night = ev_time("night", sid)
        sent = [s for s in sc["sentences"] if "night" in s["events"]]
        nk = 0.0
        if t >= night:
            nk = min(1, (t - night) / 1.2)
        scene_common_party(cr, sc, t, f, True, True, px=760, pamuk_x=520, civil_pos=(980, 470),
                           mood="sleep" if nk > 0.8 else "happy")
        we = ev_time("wave", sid)
        if t >= ev_time("celebrate", sid) and t < night:
            confetti(cr, t, ev_time("celebrate", sid))
        if nk > 0:
            cr.set_source_rgba(0.05, 0.07, 0.25, 0.65 * nk); cr.paint()
            rnd = random.Random(3)
            for k in range(60):
                x = rnd.uniform(0, W); y = rnd.uniform(0, 600); tw = 0.5 + 0.5 * math.sin(t * 3 + k)
                star(cr, x, y, 6 + 4 * tw, 5, 0.45); cr.set_source_rgba(1, 1, 0.8, nk * tw); cr.fill()
            cr.arc(1500, 180, 70, 0, 2 * PI); cr.set_source_rgba(1, 0.97, 0.8, nk); cr.fill()
            cr.arc(1530, 160, 62, 0, 2 * PI); cr.set_source_rgba(0.1, 0.12, 0.33, nk); cr.fill()
            if nk >= 1:
                for k in range(3):
                    ph = (t * 0.6 + k / 3) % 1
                    text(cr, "z", 900 + ph * 80, 760 - ph * 140, 40 + ph * 30, (1, 1, 1), (0.3, 0.3, 0.6), 6, alpha=1 - ph)
        if t >= we:
            k = min(1, (t - we) / 0.6)
            text(cr, "Hoşça kal!", W / 2, 260, 150 * ease_out_back(k), (1, 0.85, 0.3), (0.55, 0.25, 0.5), 22)


def s_bahce(cr, t, f, sc):
    back, front = layers("bahce")
    cr.set_source_surface(back); cr.paint(); sun(cr, 1650, 160, 70, t); draw_clouds(cr, t)
    cr.set_source_surface(front); cr.paint()
    sid = sc["id"]
    cnt = counted(sid, "count:", t)
    sp_t = ev_time("sparkle", sid)
    xs = [1050, 1220, 1390, 1560, 1730]
    for i, x in enumerate(xs):
        up = 0
        for e in evs("count:%d" % (i + 1), sid):
            up = ease_out_back((t - e["t"]) / 0.45) if t >= e["t"] else 0
        y = 960 - up * 110
        gl = 0.5 + 0.5 * math.sin(t * 6 + i) if t >= sp_t and t < sp_t + 4 else 0
        if gl:
            cr.arc(x, y, 70, 0, 2 * PI); cr.set_source_rgba(1, 0.6, 0.6, 0.4 * gl); cr.fill()
        strawberry(cr, x, y, 1.0)
        leaf(cr, x - 70, 985, 0.75, -0.25); leaf(cr, x + 70, 985, 0.75, PI + 0.25)
        if (i + 1) in cnt:
            num_tag(cr, x, y - 90, i + 1)
    sparkles(cr, t, 1390, 830, sp_t)
    scene_common_party(cr, sc, t, f, False, False, px=620)


def s_tarla(cr, t, f, sc):
    back, front = layers("tarla")
    cr.set_source_surface(back); cr.paint(); sun(cr, 1650, 160, 70, t); draw_clouds(cr, t)
    cr.set_source_surface(front); cr.paint()
    sid = sc["id"]
    xs = [1300, 1500, 1700]
    for i, x in enumerate(xs):
        e = evs("carrot:%d" % (i + 1), sid)
        if e and t >= e[0]["t"]:
            k = min(1, (t - e[0]["t"]) / 0.7)
            px = x + (1100 + i * 70 - x) * ease_io(k)
            py = 900 - math.sin(k * PI) * 220 + k * 70
            carrot(cr, px, py, 0.9, k * 1.4)
            if k >= 1:
                num_tag(cr, px + 30, py - 110, i + 1)
        else:
            pull = ev_time("pull", sid)
            wob = math.sin(t * 20) * 0.05 if t >= pull else 0
            cr.save(); cr.rectangle(0, 0, W, 905); cr.clip(); carrot(cr, x, 985, 0.9, wob); cr.restore()
            ell(cr, x, 905, 45, 12); cr.set_source_rgb(0.45, 0.3, 0.18); cr.fill()
    sp_t = ev_time("sparkle", sid)
    sparkles(cr, t, 1170, 880, sp_t, col=(1, 0.75, 0.3))
    join = ev_time("collect:1", sid) + 2.5
    pull = ev_time("pull", sid)
    pull_end = ev_time("carrot:3", sid) + 0.8
    lean = -0.18 * abs(math.sin(t * 4)) if pull <= t < pull_end else 0
    # Pamuk: önce havuçların yanında üzgün, sonra gruba katılır
    if t < join:
        sad = t < ev_time("carrot:1", sid)
        bunny(cr, 1080, 930, 0.95, t, talk_of(sc, t, "pamuk", f), blink(t, 1.1), face=-1,
              mood="sad" if sad else "happy", lean=-lean)
    else:
        k = ease_io((t - join) / 1.5)
        bunny(cr, 1080 + (380 - 1080) * k, 930 - abs(math.sin(t * 9)) * 14 * (0 < k < 1), 0.95, t,
              talk_of(sc, t, "pamuk", f), blink(t, 1.1), face=-1 if k < 0.5 else 1)
    cr.save()
    if lean:
        cr.translate(640, 935); cr.rotate(lean); cr.translate(-640, -935)
    scene_common_party(cr, sc, t, f, False, False, px=640)
    cr.restore()


def s_aycicegi(cr, t, f, sc):
    back, front = layers("aycicegi")
    cr.set_source_surface(back); cr.paint(); sun(cr, 1600, 170, 75, t); draw_clouds(cr, t)
    cr.set_source_surface(front); cr.paint()
    sid = sc["id"]
    sp_t = ev_time("sparkle", sid)
    cnt = counted(sid, "count:", t)
    flw = [(1060, 430, 0.85), (1260, 520, 0.95), (1480, 620, 1.1), (1700, 470, 0.9)]
    for i, (x, h, s) in enumerate(flw):
        glow = (0.5 + 0.5 * math.sin(t * 6)) if (i == 2 and sp_t <= t < sp_t + 3) else 0
        sunflower(cr, x, 960, h, s, t, i, glow)
        if (i + 1) in cnt:
            num_tag(cr, x + 80 * s, 960 - h - 80 * s, i + 1)
    sparkles(cr, t, 1480, 340, sp_t)
    join = ev_time("collect:2", sid) + 2.4
    # Cıvıl: en büyük ayçiçeğinin tepesinde, sonra gruba uçar
    hx, hy = 1480, 960 - 620 - 120
    if t < join:
        bird(cr, hx, hy, 0.95, t, talk_of(sc, t, "civil", f), blink(t, 2.3), face=-1, perched=True)
    else:
        k = ease_io((t - join) / 1.6)
        flap = ev_time("flap", sid)
        bird(cr, hx + (850 - hx) * k, hy + (520 - hy) * k - math.sin(k * PI) * 80 + math.sin(t * 2.5) * 15, 0.95,
             t, talk_of(sc, t, "civil", f), blink(t, 2.3), face=1, flap_speed=26 if t >= flap else 14)
    scene_common_party(cr, sc, t, f, True, False, px=680, pamuk_x=380)


def s_gol(cr, t, f, sc):
    back, front = layers("gol")
    cr.set_source_surface(back); cr.paint(); sun(cr, 1650, 160, 70, t); draw_clouds(cr, t)
    cr.set_source_surface(front); cr.paint()
    sid = sc["id"]
    # ördekler
    dx = 1950 - ((t - sc["start"]) * 40) % 1400
    duck(cr, dx, 830, 0.8, t)
    for k in range(3):
        duck(cr, dx + 90 + k * 60, 835, 0.45, t + k)
    pads = [(1060, 940), (1300, 930), (1540, 945), (1760, 905)]
    sp_t = ev_time("sparkle", sid)
    for i, (x, y) in enumerate(pads):
        lily(cr, x, y, 0.95, (0.5 + 0.5 * math.sin(t * 6)) if (i == 2 and sp_t <= t < sp_t + 3) else 0)
    # kurbağa: 3. yapraktan başlar (index 3), hop:i ile yaprak i-1'e zıplar
    pos = 3; hop_t = None; prev = 3
    for e in evs("hop:", sid):
        if t >= e["t"]:
            prev = pos; pos = int(e["ev"].split(":")[1]) - 1; hop_t = e["t"]
    fx, fy = pads[pos]; stretch = 1.0
    if hop_t is not None and t - hop_t < 0.6:
        k = (t - hop_t) / 0.6
        ax, ay = pads[prev]
        fx = ax + (fx - ax) * k; fy = ay + (fy - ay) * k - math.sin(k * PI) * 200; stretch = 1.15
    frog(cr, fx, fy - 5, 0.9, t, talk_of(sc, t, "virak", f), blink(t, 1.7), face=-1, stretch=stretch)
    for n in counted(sid, "hop:", t):
        x, y = pads[n - 1]; num_tag(cr, x, y + 70, n)
    sparkles(cr, t, pads[2][0], pads[2][1] - 60, sp_t, col=(0.7, 1, 0.5))
    # Pıtırcık da zıplar
    sc2 = dict(sc)
    jump = 0
    for e in evs("hop:", sid):
        if 0 <= t - e["t"] < 0.6:
            jump = math.sin((t - e["t"]) / 0.6 * PI) * 90
    cr.save(); cr.translate(0, -jump)
    scene_common_party(cr, sc2, t, f, True, True, px=680, pamuk_x=380, civil_pos=(820, 500))
    cr.restore()


def s_dere(cr, t, f, sc):
    back, front = layers("dere")
    cr.set_source_surface(back); cr.paint(); sun(cr, 1650, 160, 70, t); draw_clouds(cr, t)
    cr.set_source_surface(front); cr.paint()
    sid = sc["id"]
    # akan su çizgileri
    cr.set_source_rgba(1, 1, 1, 0.6); cr.set_line_width(4); cr.set_line_cap(cairo.LINE_CAP_ROUND)
    for k in range(14):
        x = (k * 160 + t * 90) % (W + 100) - 50; y = 800 + (k % 4) * 20
        cr.move_to(x, y); cr.line_to(x + 50, y)
    cr.stroke()
    # taşlar
    stn = ev_time("stones", sid)
    for k, x in enumerate((1180, 1260, 1340, 1430)):
        ell(cr, x, 868, 34, 14); paint(cr, COLORS[5], 3)
        if t >= stn and k == 1:
            g = 0.5 + 0.5 * math.sin(t * 6)
            ell(cr, x, 868, 60, 30); cr.set_source_rgba(0.5, 0.6, 1, 0.4 * g); cr.fill()
    # balıklar
    fcols = [(1, 0.55, 0.2), (1, 0.4, 0.5), (0.95, 0.8, 0.2), (0.6, 0.45, 0.9), (0.3, 0.8, 0.6), (1, 0.6, 0.3)]
    cnt = counted(sid, "count:", t)
    sp_t = ev_time("sparkle", sid)
    for i in range(6):
        bx = 900 + i * 150
        e = evs("count:%d" % (i + 1), sid)
        jumping = e and 0 <= t - e[0]["t"] < 1.0
        if jumping:
            k = (t - e[0]["t"]) / 1.0
            fish(cr, bx + k * 80, 820 - math.sin(k * PI) * 230, 0.8, fcols[i], -0.9 + k * 1.8)
        elif sp_t <= t < sp_t + 1.2:
            k = (t - sp_t) / 1.2
            fish(cr, bx + k * 60, 820 - math.sin(k * PI) * 160, 0.7, fcols[i], -0.9 + k * 1.8)
        else:
            cr.save(); cr.rectangle(0, 770, W, 110); cr.clip()
            fish(cr, bx + math.sin(t * 1.5 + i) * 30, 840 + math.sin(t * 2 + i) * 8, 0.6, fcols[i])
            cr.restore()
        if (i + 1) in cnt:
            num_tag(cr, bx + 40, 720, i + 1)
    bub = ev_time("bubbles", sid)
    if bub <= t < bub + 5:
        rnd = random.Random(9)
        for k in range(16):
            x = rnd.uniform(950, 1800); ph = rnd.uniform(0, 1)
            y = 860 - ((t - bub) * 70 + ph * 200) % 250
            cr.arc(x, y, 10 + k % 3 * 4, 0, 2 * PI); cr.set_source_rgba(1, 1, 1, 0.8); cr.set_line_width(3); cr.stroke()
    sparkles(cr, t, 1300, 760, sp_t, col=(0.6, 0.85, 1))
    sparkles(cr, t, 1260, 860, ev_time("sparkle", sid) if len(evs("sparkle", sid)) < 2 else evs("sparkle", sid)[1]["t"], col=(0.5, 0.6, 1))
    laugh = ev_time("laugh", sid)
    shake = math.sin(t * 25) * 6 if laugh <= t < laugh + 2.5 else 0
    cr.save(); cr.translate(0, shake)
    scene_common_party(cr, sc, t, f, True, True, px=600, pamuk_x=340, civil_pos=(820, 520))
    cr.restore()


def s_lavanta(cr, t, f, sc):
    back, front = layers("lavanta")
    cr.set_source_surface(back); cr.paint(); draw_clouds(cr, t, 0.6, (1, 0.85, 0.9))
    cr.set_source_surface(front); cr.paint()
    sid = sc["id"]
    cnt = counted(sid, "count:", t)
    sp_t = ev_time("sparkle", sid)
    bcols = [(1, 0.5, 0.7), (0.4, 0.75, 1), (1, 0.8, 0.3)]
    for i in range(3):
        cx, cy = 1150 + i * 230, 520 + i * 40
        if sp_t <= t:
            a = (t - sp_t) * 2.5 + i * 2.1; r = 160
            x, y = 1380 + math.cos(a) * r, 500 + math.sin(a) * r * 0.6
        else:
            x = cx + math.sin(t * 0.9 + i * 2) * 90; y = cy + math.sin(t * 1.7 + i) * 50
        butterfly(cr, x, y, 1.0, t + i, bcols[i])
        if (i + 1) in cnt:
            num_tag(cr, x, y - 75, i + 1)
    sparkles(cr, t, 1380, 500, sp_t, col=(0.85, 0.6, 1))
    tired, rested = ev_time("tired", sid), ev_time("rested", sid)
    helped = ev_time("help", sid)
    mood = "tired" if tired <= t < rested else "happy"
    sq = 0.9 if mood == "tired" else 1.0
    cr.save()
    if sq != 1:
        cr.translate(0, 935 * (1 - sq)); cr.scale(1, sq)
    scene_common_party(cr, sc, t, f, True, True, px=680, pamuk_x=380, civil_pos=(830, 520),
                       mood=mood, basket_on="pamuk" if t >= helped else "pit")
    cr.restore()


def title_card(cr, t):
    back, front = layers("intro")
    cr.set_source_surface(back); cr.paint(); sun(cr, 1650, 170, 70, t)
    rainbow(cr, 960, 900, 700, 46, [1] * 7, 1, t)
    draw_clouds(cr, t); cr.set_source_surface(front); cr.paint()
    k = ease_out_back(t / 0.8)
    text(cr, "Pıtırcık", W / 2, 230, 200 * k, (1, 0.6, 0.25), (0.45, 0.2, 0.45), 26)
    k2 = ease_out_back((t - 0.6) / 0.8)
    if k2 > 0:
        text(cr, "ve Gökkuşağının Kayıp Renkleri", W / 2, 390, 84 * k2, (1, 1, 1), (0.45, 0.2, 0.45), 16)
    for i, (fn, x) in enumerate((("b", 620), ("h", 900), ("c", 1180), ("o", 1420))):
        d = t - 1.2 - i * 0.25
        if d < 0:
            continue
        y = 940 - abs(math.sin(t * 4 + i)) * 30
        s = ease_out_back(d / 0.5)
        cr.save(); cr.translate(x, y); cr.scale(s, s); cr.translate(-x, -y)
        if fn == "b": bunny(cr, x, y, 0.9, t)
        if fn == "h": hedgehog(cr, x, y, 1.0, t, wave=1.0)
        if fn == "c": bird(cr, x, y - 300, 0.9, t)
        if fn == "o": frog(cr, x, y, 0.9, t)
        cr.restore()
    if t > 5.8:
        cr.set_source_rgba(1, 1, 1, min(1, (t - 5.8) / 1.2)); cr.paint()


def end_card(cr, t, d):
    back, front = layers("intro")
    cr.set_source_surface(back); cr.paint(); sun(cr, 1650, 170, 70, t)
    rainbow(cr, 960, 900, 700, 46, [1] * 7, 1, t)
    draw_clouds(cr, t); cr.set_source_surface(front); cr.paint()
    confetti(cr, t, 0)
    k = ease_out_back(d / 0.8)
    text(cr, "Hoşça kal!", 520, 230, 150 * k, (1, 0.85, 0.3), (0.55, 0.25, 0.5), 24)
    k2 = ease_out_back((d - 0.6) / 0.8)
    if k2 > 0:
        text(cr, "Yeni maceralar için", 520, 400, 64 * k2, (1, 1, 1), (0.45, 0.2, 0.45), 14)
        text(cr, "ABONE OL!", 520, 490, 96 * k2, (1, 0.35, 0.35), (1, 1, 1), 16)
    bunny(cr, 300, 940 - abs(math.sin(t * 4)) * 30, 0.9, t)
    hedgehog(cr, 560, 945 - abs(math.sin(t * 4 + 1)) * 30, 1.0, t, wave=1.0)
    bird(cr, 820, 560 + math.sin(t * 3) * 20, 0.9, t)
    if d < 0.8:
        cr.set_source_rgba(1, 1, 1, 1 - d / 0.8); cr.paint()


SCENE_FN = dict(orman=lambda cr, t, f, sc: s_orman(cr, t, f, sc), final=lambda cr, t, f, sc: s_orman(cr, t, f, sc, True),
                bahce=s_bahce, tarla=s_tarla, aycicegi=s_aycicegi, gol=s_gol, dere=s_dere, lavanta=s_lavanta)


def frame(cr, f):
    t = f / FPS
    if t < T["title"]:
        title_card(cr, t); return
    sc = scene_at(t)
    if sc is None:
        end_card(cr, t, t - SCENES[-1]["end"]); return
    SCENE_FN[sc["bg"]](cr, t, f, sc)
    if sc["id"] != "s1" or t >= ev_time("show_colors", "s1"):
        hud(cr, t)
    count_badge(cr, t, sc["id"])
    items_panel(cr, t, sc["id"])
    color_banner(cr, t)
    # geçişler (iris)
    r = None
    if t < sc["start"] + 0.7:
        r = ease_io((t - sc["start"]) / 0.7) * 1200
    elif t > sc["end"] - 0.7:
        r = ease_io((sc["end"] - t) / 0.7) * 1200
    if r is not None and sc["id"] != "s1" or (r is not None and t > sc["end"] - 0.7):
        cr.save(); cr.set_fill_rule(cairo.FILL_RULE_EVEN_ODD)
        cr.rectangle(0, 0, W, H); cr.arc(W / 2, H / 2, max(r, 0.1), 0, 2 * PI)
        cr.set_source_rgb(0.12, 0.08, 0.2); cr.fill(); cr.restore()
    if sc["id"] == "s1" and t < sc["start"] + 0.8:
        cr.set_source_rgba(1, 1, 1, 1 - (t - sc["start"]) / 0.8); cr.paint()


def render_range(args):
    a, b, out = args
    global ENV
    ENV = load_env()
    surf = cairo.ImageSurface(cairo.FORMAT_ARGB32, W, H)
    p = subprocess.Popen(["ffmpeg", "-y", "-v", "error", "-f", "rawvideo", "-pix_fmt", "bgra", "-s", f"{W}x{H}",
                          "-r", str(FPS), "-i", "-", "-c:v", "libx264", "-preset", "medium", "-crf", "20",
                          "-pix_fmt", "yuv420p", out], stdin=subprocess.PIPE)
    for f in range(a, b):
        cr = cairo.Context(surf)
        cr.set_source_rgb(1, 1, 1); cr.paint()
        frame(cr, f)
        surf.flush()
        p.stdin.write(surf.get_data())
    p.stdin.close(); p.wait()
    return out


def main():
    if "--png" in sys.argv:
        global ENV
        ENV = load_env()
        os.makedirs(os.path.join(BUILD, "preview"), exist_ok=True)
        for s in sys.argv[sys.argv.index("--png") + 1:]:
            f = int(float(s) * FPS)
            surf = cairo.ImageSurface(cairo.FORMAT_ARGB32, W, H)
            cr = cairo.Context(surf); cr.set_source_rgb(1, 1, 1); cr.paint(); frame(cr, f)
            surf.write_to_png(os.path.join(BUILD, "preview", f"t{float(s):07.1f}.png"))
        return
    n = int(TOTAL * FPS)
    workers = os.cpu_count() or 4
    parts = 16
    step = math.ceil(n / parts)
    jobs = [(i * step, min(n, (i + 1) * step), os.path.join(BUILD, f"part{i:02d}.mp4")) for i in range(parts)]
    with Pool(workers) as pool:
        for o in pool.imap_unordered(render_range, jobs):
            print("bitti:", o, flush=True)
    with open(os.path.join(BUILD, "parts.txt"), "w") as fh:
        for _, _, o in jobs:
            fh.write(f"file '{o}'\n")


if __name__ == "__main__":
    main()
