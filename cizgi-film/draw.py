# Karakter, nesne ve arka plan çizimleri (pycairo)
import math, random
import cairo

W, H = 1920, 1080
PI = math.pi
OUT = (0.22, 0.15, 0.12)          # çizgi film dış çizgi rengi
FONT = "Baloo 2"
COLORS = [(0.93, 0.22, 0.22), (1.0, 0.56, 0.1), (1.0, 0.84, 0.1), (0.3, 0.75, 0.25),
          (0.25, 0.6, 0.95), (0.16, 0.23, 0.62), (0.6, 0.3, 0.78)]
NAMES = ["KIRMIZI", "TURUNCU", "SARI", "YEŞİL", "MAVİ", "LACİVERT", "MOR"]
NUMS = ["", "BİR", "İKİ", "ÜÇ", "DÖRT", "BEŞ", "ALTI"]


# ---------------------------------------------------------------- yardımcılar
def ell(cr, x, y, rx, ry, rot=0.0):
    cr.save(); cr.translate(x, y); cr.rotate(rot); cr.scale(rx, ry)
    cr.new_sub_path(); cr.arc(0, 0, 1, 0, 2 * PI); cr.restore()


def paint(cr, col, lw=5, out=OUT, alpha=1.0):
    if len(col) == 4:
        cr.set_source_rgba(*col)
    else:
        cr.set_source_rgba(*col, alpha)
    if lw:
        cr.fill_preserve(); cr.set_source_rgb(*out); cr.set_line_width(lw); cr.stroke()
    else:
        cr.fill()


def lighten(c, k=0.35):
    return tuple(min(1, v + (1 - v) * k) for v in c[:3])


def darken(c, k=0.3):
    return tuple(v * (1 - k) for v in c[:3])


def rrect(cr, x, y, w, h, r):
    cr.new_sub_path()
    cr.arc(x + w - r, y + r, r, -PI / 2, 0); cr.arc(x + w - r, y + h - r, r, 0, PI / 2)
    cr.arc(x + r, y + h - r, r, PI / 2, PI); cr.arc(x + r, y + r, r, PI, 1.5 * PI)
    cr.close_path()


def text(cr, s, x, y, size, col=(1, 1, 1), out=(0.25, 0.15, 0.35), lw=None, align="c", alpha=1.0):
    cr.save()
    cr.select_font_face(FONT, cairo.FONT_SLANT_NORMAL, cairo.FONT_WEIGHT_BOLD)
    cr.set_font_size(size)
    ext = cr.text_extents(s)
    if align == "c":
        tx = x - ext.x_advance / 2
    elif align == "l":
        tx = x
    else:
        tx = x - ext.x_advance
    ty = y + size * 0.33
    cr.move_to(tx, ty); cr.text_path(s)
    cr.set_line_join(cairo.LINE_JOIN_ROUND)
    cr.set_source_rgba(*out, alpha); cr.set_line_width(lw if lw else size * 0.16); cr.stroke_preserve()
    cr.set_source_rgba(*col, alpha); cr.fill()
    cr.restore()


def ease_out_back(x):
    x = max(0.0, min(1.0, x)); c1 = 1.70158; c3 = c1 + 1
    return 1 + c3 * (x - 1) ** 3 + c1 * (x - 1) ** 2


def ease_io(x):
    x = max(0.0, min(1.0, x))
    return x * x * (3 - 2 * x)


def star(cr, x, y, r, n=5, inner=0.45, rot=0.0):
    cr.new_sub_path()
    for i in range(n * 2):
        a = rot - PI / 2 + i * PI / n
        rr = r if i % 2 == 0 else r * inner
        cr.line_to(x + math.cos(a) * rr, y + math.sin(a) * rr)
    cr.close_path()


# ---------------------------------------------------------------- karakterler
def eye(cr, x, y, r, blink, look=(0, 0), lid=0.0):
    if blink:
        cr.move_to(x - r, y); cr.curve_to(x - r / 2, y + r * 0.6, x + r / 2, y + r * 0.6, x + r, y)
        cr.set_source_rgb(*OUT); cr.set_line_width(4); cr.stroke(); return
    ell(cr, x, y, r, r * 1.2); paint(cr, (1, 1, 1), 3)
    ell(cr, x + look[0] * r * 0.35 + r * 0.15, y + look[1] * r * 0.35 + r * 0.1, r * 0.62, r * 0.72)
    cr.set_source_rgb(0.12, 0.08, 0.08); cr.fill()
    cr.arc(x + r * 0.32, y - r * 0.2, r * 0.22, 0, 2 * PI); cr.set_source_rgb(1, 1, 1); cr.fill()
    if lid > 0:
        cr.save(); ell(cr, x, y, r * 1.05, r * 1.25); cr.clip()
        cr.rectangle(x - r * 1.2, y - r * 1.3, r * 2.4, r * 2.5 * lid)
        cr.set_source_rgb(0.62, 0.43, 0.28); cr.fill(); cr.restore()


def mouth(cr, x, y, w, open_, smile=True):
    if open_ > 0.08:
        h = 4 + w * 0.9 * open_
        ell(cr, x, y + h * 0.3, w * 0.6, h * 0.6); paint(cr, (0.45, 0.08, 0.1), 3)
        ell(cr, x, y + h * 0.55, w * 0.35, h * 0.25); cr.set_source_rgb(0.95, 0.45, 0.5); cr.fill()
    else:
        cr.move_to(x - w * 0.6, y)
        if smile:
            cr.curve_to(x - w * 0.3, y + w * 0.45, x + w * 0.3, y + w * 0.45, x + w * 0.6, y)
        else:
            cr.curve_to(x - w * 0.3, y - w * 0.25, x + w * 0.3, y - w * 0.25, x + w * 0.6, y)
        cr.set_source_rgb(*OUT); cr.set_line_width(4.5); cr.set_line_cap(cairo.LINE_CAP_ROUND); cr.stroke()


def basket(cr, x, y, s, colors):
    cr.save(); cr.translate(x, y); cr.scale(s, s)
    # renk topları
    for i, c in enumerate(colors):
        bx = -38 + (i % 4) * 25 + (12 if i >= 4 else 0)
        by = -38 - (12 if i >= 4 else 0)
        cr.arc(bx, by, 15, 0, 2 * PI); paint(cr, COLORS[c], 3)
        cr.arc(bx - 5, by - 5, 4, 0, 2 * PI); cr.set_source_rgba(1, 1, 1, 0.8); cr.fill()
    cr.move_to(-55, -35); cr.line_to(55, -35); cr.line_to(42, 20); cr.line_to(-42, 20); cr.close_path()
    paint(cr, (0.83, 0.6, 0.3), 4)
    for yy in (-18, 0):
        cr.move_to(-50 + (yy + 35) * 0.2, yy); cr.line_to(50 - (yy + 35) * 0.2, yy)
        cr.set_source_rgb(0.6, 0.4, 0.2); cr.set_line_width(3); cr.stroke()
    cr.arc(0, -35, 50, PI * 1.05, PI * 1.95); cr.set_source_rgb(0.6, 0.4, 0.2); cr.set_line_width(7); cr.stroke()
    cr.restore()


def hedgehog(cr, x, y, s=1.0, t=0.0, talk=0.0, blink=False, face=1, mood="happy",
             basket_colors=None, wave=0.0, squash=1.0, look=(0, 0)):
    cr.save(); cr.translate(x, y); cr.scale(s * face, s * squash)
    BODY = (0.66, 0.46, 0.3); SPK = (0.42, 0.28, 0.18)
    for fx in (-40, 40):
        ell(cr, fx, -6, 26, 13); paint(cr, (0.45, 0.3, 0.2), 4)
    # dikenler
    cx, cy, rx, ry = -12, -88, 118, 92
    cr.new_path()
    n = 26
    a0, a1 = math.radians(105), math.radians(335)
    for i in range(n + 1):
        a = a0 + (a1 - a0) * i / n
        k = 1.0 if i % 2 == 0 else 1.32
        cr.line_to(cx + math.cos(a) * rx * k, cy + math.sin(a) * ry * k)
    cr.close_path(); paint(cr, SPK, 5)
    ell(cr, 0, -80, 112, 82); paint(cr, BODY, 5)
    # karın + yüz
    ell(cr, 60, -70, 68, 58); paint(cr, (0.98, 0.88, 0.72), 0)
    ell(cr, 112, -66, 44, 30, -0.1); paint(cr, (0.98, 0.88, 0.72), 0)
    cr.arc(156, -72, 14, 0, 2 * PI); paint(cr, (0.15, 0.1, 0.1), 3)
    cr.arc(152, -77, 4, 0, 2 * PI); cr.set_source_rgb(1, 1, 1); cr.fill()
    # kulak
    ell(cr, 18, -150, 18, 20); paint(cr, BODY, 4)
    ell(cr, 18, -148, 9, 11); cr.set_source_rgb(0.95, 0.6, 0.6); cr.fill()
    lid = 0.45 if mood == "tired" else 0.0
    if mood == "sleep":
        blink = True
    eye(cr, 78, -104, 15, blink, look, lid)
    cr.arc(92, -70, 13, 0, 2 * PI); cr.set_source_rgba(1, 0.5, 0.55, 0.55); cr.fill()
    if mood == "surprise":
        ell(cr, 122, -40, 11, 15); paint(cr, (0.45, 0.08, 0.1), 3)
    else:
        mouth(cr, 120, -44, 22, talk, smile=(mood != "tired"))
    # kollar
    ell(cr, 52, -28, 16, 22, 0.4); paint(cr, (0.45, 0.3, 0.2), 4)
    if wave > 0:
        cr.save(); cr.translate(-20, -70); cr.rotate(-1.2 - 0.5 * math.sin(t * 12) * wave)
        ell(cr, 0, -40, 15, 40); paint(cr, (0.45, 0.3, 0.2), 4); cr.restore()
    if basket_colors is not None:
        cr.save(); cr.scale(face, 1); basket(cr, 70 * face, -18, 0.85, basket_colors); cr.restore()
    cr.restore()


def bunny(cr, x, y, s=1.0, t=0.0, talk=0.0, blink=False, face=1, mood="happy", basket_colors=None,
          lean=0.0):
    cr.save(); cr.translate(x, y); cr.rotate(lean); cr.scale(s * face, s)
    WHITE = (0.99, 0.99, 1.0); OUTB = (0.35, 0.33, 0.45)
    ell(cr, -62, -62, 22, 22); paint(cr, WHITE, 4, OUTB)
    ell(cr, 0, -80, 62, 74); paint(cr, WHITE, 5, OUTB)
    ell(cr, -30, -8, 34, 14); paint(cr, WHITE, 4, OUTB)
    ell(cr, 34, -8, 34, 14); paint(cr, WHITE, 4, OUTB)
    wig = math.sin(t * 3) * 0.08
    for ex, rot in ((0, -0.15 + wig), (40, 0.15 - wig)):
        cr.save(); cr.translate(ex + 10, -205); cr.rotate(rot)
        ell(cr, 0, -60, 20, 66); paint(cr, WHITE, 5, OUTB)
        ell(cr, 0, -56, 9, 50); cr.set_source_rgb(1, 0.72, 0.78); cr.fill(); cr.restore()
    cr.arc(25, -175, 62, 0, 2 * PI); paint(cr, WHITE, 5, OUTB)
    eye(cr, 48, -188, 13, blink)
    cr.arc(78, -168, 9, 0, 2 * PI); paint(cr, (1, 0.55, 0.65), 3, OUTB)
    cr.arc(58, -150, 12, 0, 2 * PI); cr.set_source_rgba(1, 0.55, 0.6, 0.45); cr.fill()
    mouth(cr, 74, -146, 16, talk, smile=(mood != "sad"))
    if mood == "sad":
        for i in range(2):
            ph = (t * 1.2 + i * 0.5) % 1.0
            cr.save(); cr.translate(52, -170 + ph * 70)
            cr.move_to(0, -10); cr.curve_to(8, 2, 8, 10, 0, 10); cr.curve_to(-8, 10, -8, 2, 0, -10)
            cr.set_source_rgba(0.45, 0.7, 1, 1 - ph); cr.fill(); cr.restore()
    ell(cr, 50, -70, 16, 24, -0.4); paint(cr, WHITE, 4, OUTB)
    if basket_colors is not None:
        cr.save(); cr.scale(face, 1); basket(cr, 70 * face, -40, 0.8, basket_colors); cr.restore()
    cr.restore()


def bird(cr, x, y, s=1.0, t=0.0, talk=0.0, blink=False, face=1, flap_speed=14.0, perched=False):
    cr.save(); cr.translate(x, y); cr.scale(s * face, s)
    Y = (1.0, 0.84, 0.18)
    if perched:
        for lx in (-10, 12):
            cr.move_to(lx, 30); cr.line_to(lx, 52); cr.set_source_rgb(0.9, 0.5, 0.1); cr.set_line_width(5); cr.stroke()
    cr.move_to(-38, -5); cr.line_to(-70, -22); cr.line_to(-66, 8); cr.close_path(); paint(cr, (0.95, 0.7, 0.1), 4)
    cr.arc(0, 0, 44, 0, 2 * PI); paint(cr, Y, 5)
    ell(cr, 8, 16, 26, 20); cr.set_source_rgb(1, 0.95, 0.7); cr.fill()
    # tepe tüyü
    for a in (-0.3, 0, 0.3):
        cr.save(); cr.translate(-2, -42); cr.rotate(a); ell(cr, 0, -12, 6, 14); paint(cr, (0.95, 0.7, 0.1), 3); cr.restore()
    eye(cr, 16, -12, 10, blink)
    o = 6 * talk
    cr.move_to(38, -6 - o); cr.line_to(64, 0); cr.line_to(38, 4); cr.close_path(); paint(cr, (1, 0.5, 0.1), 3)
    cr.move_to(38, 4); cr.line_to(58, 6 + o); cr.line_to(38, 10 + o); cr.close_path(); paint(cr, (0.95, 0.42, 0.08), 3)
    flap = math.sin(t * flap_speed) if not perched else 0.3
    cr.save(); cr.translate(-8, 4); cr.rotate(-0.4 + flap * 0.7)
    ell(cr, -22, -6, 30, 16); paint(cr, (0.98, 0.74, 0.12), 4); cr.restore()
    cr.arc(26, 8, 7, 0, 2 * PI); cr.set_source_rgba(1, 0.5, 0.5, 0.5); cr.fill()
    cr.restore()


def owl(cr, x, y, s=1.0, t=0.0, talk=0.0, blink=False, wings=0.0):
    cr.save(); cr.translate(x, y); cr.scale(s, s)
    B = (0.55, 0.4, 0.3)
    for side in (-1, 1):
        cr.save(); cr.translate(side * 60, -70); cr.rotate(side * (0.15 + wings * 1.1))
        ell(cr, side * 10, 20, 28, 62); paint(cr, darken(B, 0.15), 5); cr.restore()
    ell(cr, 0, -80, 72, 92); paint(cr, B, 5)
    ell(cr, 0, -55, 48, 58); paint(cr, (0.93, 0.84, 0.66), 0)
    for i in range(3):
        for j in range(2 + i % 2):
            vx = -20 + j * 20 + (10 if i % 2 == 0 else 0) - 10; vy = -70 + i * 22
            cr.move_to(vx - 7, vy); cr.line_to(vx, vy + 7); cr.line_to(vx + 7, vy)
            cr.set_source_rgb(0.7, 0.55, 0.4); cr.set_line_width(3); cr.stroke()
    for side in (-1, 1):
        cr.move_to(side * 30, -158); cr.line_to(side * 62, -192); cr.line_to(side * 60, -140); cr.close_path()
        paint(cr, B, 4)
    for side in (-1, 1):
        cr.arc(side * 30, -128, 30, 0, 2 * PI); paint(cr, (1, 0.93, 0.7), 4)
        eye(cr, side * 30, -128, 19, blink)
        cr.arc(side * 30, -128, 34, 0, 2 * PI); cr.set_source_rgb(0.3, 0.2, 0.15); cr.set_line_width(4); cr.stroke()
    cr.move_to(-4, -128); cr.line_to(4, -128); cr.set_source_rgb(0.3, 0.2, 0.15); cr.set_line_width(4); cr.stroke()
    o = 8 * talk
    cr.move_to(-12, -100); cr.line_to(12, -100); cr.line_to(0, -80 + o); cr.close_path(); paint(cr, (1, 0.62, 0.15), 3)
    for fx in (-22, 22):
        for k in (-8, 0, 8):
            cr.move_to(fx + k, 6); cr.line_to(fx + k * 1.4, 18)
            cr.set_source_rgb(1, 0.62, 0.15); cr.set_line_width(5); cr.set_line_cap(cairo.LINE_CAP_ROUND); cr.stroke()
    cr.restore()


def frog(cr, x, y, s=1.0, t=0.0, talk=0.0, blink=False, face=1, stretch=1.0):
    cr.save(); cr.translate(x, y); cr.scale(s * face, s * stretch)
    G = (0.42, 0.8, 0.3)
    for fx in (-50, 50):
        ell(cr, fx, -14, 34, 16); paint(cr, darken(G, 0.15), 4)
    ell(cr, 0, -55, 78, 52); paint(cr, G, 5)
    ell(cr, 0, -42, 48, 30); cr.set_source_rgb(0.82, 0.95, 0.6); cr.fill()
    for ex in (-36, 36):
        cr.arc(ex, -105, 26, 0, 2 * PI); paint(cr, G, 5)
        eye(cr, ex, -107, 15, blink)
    if talk > 0.08:
        ell(cr, 0, -62, 40, 8 + 18 * talk); paint(cr, (0.5, 0.1, 0.12), 3)
    else:
        cr.move_to(-46, -70); cr.curve_to(-20, -46, 20, -46, 46, -70)
        cr.set_source_rgb(*OUT); cr.set_line_width(5); cr.stroke()
    for ex in (-52, 52):
        cr.arc(ex, -66, 11, 0, 2 * PI); cr.set_source_rgba(1, 0.5, 0.5, 0.5); cr.fill()
    cr.restore()


def duck(cr, x, y, s, t):
    cr.save(); cr.translate(x, y + math.sin(t * 3) * 3); cr.scale(s, s)
    ell(cr, 0, 0, 45, 26); paint(cr, (1, 0.93, 0.4), 4)
    cr.arc(36, -32, 22, 0, 2 * PI); paint(cr, (1, 0.93, 0.4), 4)
    cr.move_to(54, -36); cr.line_to(76, -30); cr.line_to(54, -24); cr.close_path(); paint(cr, (1, 0.55, 0.1), 3)
    cr.arc(42, -38, 4, 0, 2 * PI); cr.set_source_rgb(0.1, 0.1, 0.1); cr.fill()
    cr.restore()


def fish(cr, x, y, s, col, rot=0.0, num=None):
    cr.save(); cr.translate(x, y); cr.rotate(rot); cr.scale(s, s)
    cr.move_to(-40, 0); cr.line_to(-70, -24); cr.line_to(-70, 24); cr.close_path(); paint(cr, darken(col, 0.15), 4)
    ell(cr, 0, 0, 48, 28); paint(cr, col, 4)
    cr.arc(24, -6, 8, 0, 2 * PI); paint(cr, (1, 1, 1), 2)
    cr.arc(26, -6, 4, 0, 2 * PI); cr.set_source_rgb(0, 0, 0); cr.fill()
    cr.restore()


def butterfly(cr, x, y, s, t, col):
    cr.save(); cr.translate(x, y); cr.scale(s, s)
    f = abs(math.sin(t * 12)) * 0.75 + 0.25
    for side in (-1, 1):
        cr.save(); cr.scale(side * f, 1)
        ell(cr, 26, -16, 28, 22, -0.4); paint(cr, col, 4)
        ell(cr, 20, 16, 18, 15, 0.4); paint(cr, lighten(col, 0.3), 4)
        cr.restore()
    ell(cr, 0, 0, 6, 26); paint(cr, (0.25, 0.15, 0.2), 0)
    cr.restore()


# ---------------------------------------------------------------- nesneler
def strawberry(cr, x, y, s):
    cr.save(); cr.translate(x, y); cr.scale(s, s)
    cr.move_to(0, 40); cr.curve_to(-45, 10, -40, -38, 0, -32); cr.curve_to(40, -38, 45, 10, 0, 40)
    paint(cr, (0.92, 0.15, 0.2), 4)
    for sx, sy in ((-14, -14), (10, -18), (-4, 2), (16, 2), (-18, 8), (4, 18)):
        ell(cr, sx, sy, 2.5, 4); cr.set_source_rgb(1, 0.95, 0.5); cr.fill()
    for a in range(5):
        cr.save(); cr.translate(0, -32); cr.rotate(-PI / 2 + (a - 2) * 0.55)
        ell(cr, 14, 0, 16, 6); paint(cr, (0.25, 0.65, 0.2), 3); cr.restore()
    cr.restore()


def leaf(cr, x, y, s, rot, col=(0.3, 0.68, 0.25)):
    cr.save(); cr.translate(x, y); cr.rotate(rot); cr.scale(s, s)
    cr.move_to(0, 0); cr.curve_to(30, -40, 90, -40, 120, 0); cr.curve_to(90, 40, 30, 40, 0, 0)
    paint(cr, col, 4)
    cr.move_to(0, 0); cr.line_to(110, 0); cr.set_source_rgb(*darken(col, 0.3)); cr.set_line_width(3); cr.stroke()
    cr.restore()


def carrot(cr, x, y, s, rot=0.0, buried=0.0):
    cr.save(); cr.translate(x, y); cr.rotate(rot); cr.scale(s, s)
    for a in (-0.45, 0, 0.45):
        cr.save(); cr.translate(0, -60); cr.rotate(a); ell(cr, 0, -38, 10, 38); paint(cr, (0.3, 0.7, 0.25), 3); cr.restore()
    cr.move_to(-26, -60); cr.curve_to(-24, 0, -6, 60, 0, 80); cr.curve_to(6, 60, 24, 0, 26, -60); cr.close_path()
    paint(cr, (1, 0.55, 0.1), 4)
    for yy in (-30, 0, 30):
        cr.move_to(-14 + yy * 0.1, yy); cr.line_to(-4, yy + 4); cr.set_source_rgb(0.8, 0.4, 0.05); cr.set_line_width(3); cr.stroke()
    cr.restore()


def sunflower(cr, x, y, h, s, t, phase=0.0, glow=0.0):
    sway = math.sin(t * 1.2 + phase) * 0.04
    cr.save(); cr.translate(x, y); cr.rotate(sway)
    cr.move_to(0, 0); cr.curve_to(-10, -h * 0.4, 10, -h * 0.7, 0, -h)
    cr.set_source_rgb(*OUT); cr.set_line_width(16); cr.stroke_preserve()
    cr.set_source_rgb(0.35, 0.68, 0.25); cr.set_line_width(10); cr.stroke()
    leaf(cr, 0, -h * 0.35, 0.7 * s, -0.5); leaf(cr, 0, -h * 0.55, 0.6 * s, PI + 0.5)
    cr.translate(0, -h); cr.scale(s, s)
    if glow > 0:
        g = cairo.RadialGradient(0, 0, 20, 0, 0, 170)
        g.add_color_stop_rgba(0, 1, 1, 0.6, 0.8 * glow); g.add_color_stop_rgba(1, 1, 1, 0.6, 0)
        cr.set_source(g); cr.arc(0, 0, 170, 0, 2 * PI); cr.fill()
    for i in range(16):
        cr.save(); cr.rotate(i * PI / 8 + t * 0.1); ell(cr, 0, -62, 16, 34); paint(cr, (1, 0.82, 0.1), 3); cr.restore()
    cr.arc(0, 0, 44, 0, 2 * PI); paint(cr, (0.45, 0.28, 0.12), 4)
    for i in range(12):
        a = i * 2.4; r = 6 + i * 2.6
        cr.arc(math.cos(a) * r, math.sin(a) * r, 3.5, 0, 2 * PI); cr.set_source_rgb(0.3, 0.18, 0.08); cr.fill()
    cr.restore()


def lily(cr, x, y, s, glow=0.0):
    cr.save(); cr.translate(x, y); cr.scale(s, s * 0.35)
    if glow > 0:
        cr.arc(0, 0, 130, 0, 2 * PI); cr.set_source_rgba(0.6, 1, 0.5, 0.5 * glow); cr.fill()
    cr.move_to(0, 0); cr.arc(0, 0, 90, 0.35, 2 * PI - 0.35); cr.close_path()
    paint(cr, (0.28, 0.66, 0.3), 5)
    cr.restore()


def tree(cr, x, y, s, col=(0.3, 0.68, 0.28)):
    cr.save(); cr.translate(x, y); cr.scale(s, s)
    cr.move_to(-26, 0); cr.line_to(-18, -170); cr.line_to(18, -170); cr.line_to(26, 0); cr.close_path()
    paint(cr, (0.55, 0.36, 0.2), 5)
    for (cx, cy, r) in ((0, -230, 95), (-75, -180, 70), (75, -180, 70), (-40, -300, 70), (45, -295, 70)):
        cr.arc(cx, cy, r, 0, 2 * PI); paint(cr, col, 5)
    for (cx, cy, r) in ((0, -230, 95), (-75, -180, 70), (75, -180, 70), (-40, -300, 70), (45, -295, 70)):
        cr.arc(cx, cy, r - 6, 0, 2 * PI); cr.set_source_rgb(*col); cr.fill()
    cr.arc(-30, -280, 30, 0, 2 * PI); cr.set_source_rgba(1, 1, 1, 0.15); cr.fill()
    cr.restore()


def cloud(cr, x, y, s, alpha=1.0, col=(1, 1, 1)):
    cr.save(); cr.translate(x, y); cr.scale(s, s)
    for (cx, cy, r) in ((0, 0, 50), (55, -20, 60), (115, 0, 50), (60, 15, 50)):
        cr.arc(cx, cy, r, 0, 2 * PI); cr.close_path()
    cr.set_source_rgba(*col, alpha); cr.fill()
    cr.restore()


def sun(cr, x, y, r, t):
    cr.save(); cr.translate(x, y)
    g = cairo.RadialGradient(0, 0, r * 0.5, 0, 0, r * 2.4)
    g.add_color_stop_rgba(0, 1, 0.95, 0.6, 0.6); g.add_color_stop_rgba(1, 1, 0.95, 0.6, 0)
    cr.set_source(g); cr.arc(0, 0, r * 2.4, 0, 2 * PI); cr.fill()
    cr.rotate(t * 0.2)
    for i in range(12):
        cr.save(); cr.rotate(i * PI / 6); ell(cr, 0, -r * 1.45, r * 0.12, r * 0.3); cr.set_source_rgb(1, 0.8, 0.2); cr.fill(); cr.restore()
    cr.restore()
    cr.arc(x, y, r, 0, 2 * PI); paint(cr, (1, 0.86, 0.25), 5, (0.95, 0.6, 0.15))


def rainbow(cr, cx, cy, r0, bw, fills, gray_alpha=1.0, t=0.0):
    """fills: her bant için 0..1 renklenme oranı"""
    for i in range(7):
        r = r0 - i * bw
        cr.new_path(); cr.arc(cx, cy, r, PI, 2 * PI)
        cr.set_line_width(bw + 1)
        f = fills[i]
        if f < 1:
            g = 0.72 - i * 0.03
            cr.set_source_rgba(g, g, g + 0.02, 0.85 * gray_alpha); cr.stroke_preserve()
        if f > 0:
            cr.set_source_rgba(*COLORS[i], min(1, f)); cr.stroke_preserve()
        cr.new_path()


# küçük ikonlar (renk örnekleri)
def icon(cr, name, x, y, s, t=0.0):
    cr.save(); cr.translate(x, y); cr.scale(s, s)
    R, O, Yl, G, P = COLORS[0], COLORS[1], COLORS[2], COLORS[3], COLORS[6]
    if name == "elma":
        cr.move_to(0, -30); cr.curve_to(-60, -60, -60, 50, 0, 45); cr.curve_to(60, 50, 60, -60, 0, -30); paint(cr, R, 4)
        cr.move_to(0, -30); cr.line_to(4, -52); cr.set_source_rgb(0.4, 0.25, 0.1); cr.set_line_width(5); cr.stroke()
        leaf(cr, 4, -46, 0.28, -0.6)
    elif name == "domates":
        ell(cr, 0, 5, 50, 40); paint(cr, (0.9, 0.18, 0.15), 4)
        star(cr, 0, -32, 22, 5, 0.4); paint(cr, (0.3, 0.65, 0.2), 3)
    elif name == "itfaiye":
        rrect(cr, -60, -30, 120, 50, 8); paint(cr, R, 4)
        rrect(cr, 18, -52, 40, 30, 5); paint(cr, R, 4)
        cr.rectangle(26, -46, 24, 16); paint(cr, (0.75, 0.9, 1), 3)
        cr.rectangle(-55, -48, 65, 10); paint(cr, (0.85, 0.85, 0.85), 3)
        for wx in (-35, 35):
            cr.arc(wx, 22, 15, 0, 2 * PI); paint(cr, (0.2, 0.2, 0.2), 3)
    elif name == "portakal":
        cr.arc(0, 4, 46, 0, 2 * PI); paint(cr, O, 4)
        leaf(cr, 0, -40, 0.3, -0.5)
    elif name == "balkabagi":
        for dx, rx in ((-28, 30), (28, 30), (0, 32)):
            ell(cr, dx, 6, rx, 40); paint(cr, O, 4)
        cr.rectangle(-5, -50, 10, 18); paint(cr, (0.4, 0.3, 0.1), 3)
    elif name == "havuc":
        carrot(cr, 0, 10, 0.55, 0.3)
    elif name == "gunes":
        for i in range(10):
            cr.save(); cr.rotate(i * PI / 5 + t); ell(cr, 0, -52, 7, 14); cr.set_source_rgb(1, 0.75, 0.1); cr.fill(); cr.restore()
        cr.arc(0, 0, 36, 0, 2 * PI); paint(cr, Yl, 4)
    elif name == "muz":
        cr.move_to(-50, -30); cr.curve_to(-40, 40, 40, 50, 55, -20); cr.curve_to(30, 20, -20, 15, -50, -30)
        paint(cr, Yl, 4)
    elif name == "limon":
        ell(cr, 0, 0, 52, 36, -0.2); paint(cr, (1, 0.9, 0.2), 4)
    elif name == "agac":
        tree(cr, 0, 50, 0.3)
    elif name == "cimen":
        for i in range(7):
            bx = -48 + i * 16
            cr.move_to(bx - 7, 40); cr.line_to(bx + math.sin(i) * 8, -30 - (i % 3) * 12); cr.line_to(bx + 7, 40)
            cr.close_path(); paint(cr, G, 3)
    elif name == "kurbaga":
        frog(cr, 0, 45, 0.55, t)
    elif name == "uzum":
        for i, (gx, gy) in enumerate(((-24, -20), (0, -20), (24, -20), (-12, 2), (12, 2), (0, 24))):
            cr.arc(gx, gy, 15, 0, 2 * PI); paint(cr, P, 3)
        leaf(cr, 0, -36, 0.3, -0.7)
    elif name == "patlican":
        ell(cr, 0, 8, 30, 46, 0.4); paint(cr, (0.45, 0.2, 0.55), 4)
        star(cr, -16, -32, 18, 5, 0.4, 0.4); paint(cr, (0.3, 0.65, 0.2), 3)
    elif name == "lavanta":
        for k in (-18, 0, 18):
            cr.move_to(k * 0.3, 50); cr.line_to(k, -20); cr.set_source_rgb(0.3, 0.6, 0.25); cr.set_line_width(5); cr.stroke()
            for j in range(5):
                ell(cr, k, -20 - j * 11, 7, 8); paint(cr, P, 2)
    cr.restore()


ITEM_NAMES = dict(elma="Elma", domates="Domates", itfaiye="İtfaiye", portakal="Portakal",
                  balkabagi="Balkabağı", havuc="Havuç", gunes="Güneş", muz="Muz", limon="Limon",
                  agac="Ağaç", cimen="Çimen", kurbaga="Kurbağa", uzum="Üzüm", patlican="Patlıcan",
                  lavanta="Lavanta")


# ---------------------------------------------------------------- arka planlar
def sky(cr, top, bottom, horizon=760):
    g = cairo.LinearGradient(0, 0, 0, horizon)
    g.add_color_stop_rgb(0, *top); g.add_color_stop_rgb(1, *bottom)
    cr.set_source(g); cr.rectangle(0, 0, W, H); cr.fill()


def hills(cr, base, amp, col, seed, lw=5):
    rnd = random.Random(seed)
    ph = [rnd.uniform(0, 6) for _ in range(3)]
    cr.move_to(0, H)
    for x in range(0, W + 21, 20):
        y = base - amp * (0.6 * math.sin(x / 300 + ph[0]) + 0.3 * math.sin(x / 140 + ph[1]) + 0.1 * math.sin(x / 60 + ph[2]))
        cr.line_to(x, y)
    cr.line_to(W, H); cr.close_path(); paint(cr, col, lw)


def flowers(cr, seed, y0, y1, n=40):
    rnd = random.Random(seed)
    for _ in range(n):
        x = rnd.uniform(0, W); y = rnd.uniform(y0, y1)
        c = rnd.choice([(1, 1, 1), (1, 0.85, 0.3), (1, 0.6, 0.75), (0.75, 0.6, 1)])
        for k in range(5):
            a = k * 2 * PI / 5
            cr.arc(x + math.cos(a) * 6, y + math.sin(a) * 6, 5, 0, 2 * PI); cr.set_source_rgb(*c); cr.fill()
        cr.arc(x, y, 4, 0, 2 * PI); cr.set_source_rgb(1, 0.75, 0.2); cr.fill()


def grass_tufts(cr, seed, y0, y1, n=60, col=(0.3, 0.62, 0.22)):
    rnd = random.Random(seed)
    for _ in range(n):
        x = rnd.uniform(0, W); y = rnd.uniform(y0, y1)
        for k in (-1, 0, 1):
            cr.move_to(x + k * 6, y); cr.line_to(x + k * 12, y - 18 - abs(k) * -6)
        cr.set_source_rgb(*col); cr.set_line_width(3); cr.set_line_cap(cairo.LINE_CAP_ROUND); cr.stroke()


def make_layers(bg):
    """(arka katman, ön katman) ImageSurface döndürür. Arada gökkuşağı/bulut çizilir."""
    back = cairo.ImageSurface(cairo.FORMAT_ARGB32, W, H)
    front = cairo.ImageSurface(cairo.FORMAT_ARGB32, W, H)
    cb, cf = cairo.Context(back), cairo.Context(front)
    if bg == "lavanta":
        sky(cb, (0.55, 0.45, 0.85), (1.0, 0.7, 0.55))
    elif bg == "gol":
        sky(cb, (0.45, 0.75, 0.98), (0.85, 0.95, 1.0))
    else:
        sky(cb, (0.38, 0.72, 0.98), (0.82, 0.94, 1.0))
    if bg in ("orman", "final", "intro"):
        hills(cf, 700, 60, (0.55, 0.82, 0.45), 1)
        hills(cf, 780, 40, (0.42, 0.74, 0.35), 2)
        for tx, ts in ((1500, 0.75), (1700, 0.9), (1880, 0.7), (1100, 0.55)):
            tree(cf, tx, 790, ts, (0.28, 0.6, 0.26))
        cf.rectangle(0, 840, W, H - 840); cf.set_source_rgb(0.45, 0.78, 0.33); cf.fill()
        hills(cf, 860, 12, (0.48, 0.8, 0.35), 3, 0)
        grass_tufts(cf, 4, 880, 1060); flowers(cf, 5, 870, 1070, 35)
        # büyük meşe ağacı (baykuşun evi)
        tree(cf, 230, 900, 1.45, (0.3, 0.64, 0.27))
        cf.save(); cf.move_to(250, 640); cf.line_to(470, 600); cf.line_to(470, 625); cf.line_to(250, 680); cf.close_path()
        paint(cf, (0.55, 0.36, 0.2), 5); cf.restore()
        if bg == "orman":
            ell(cf, 820, 925, 140, 60); paint(cf, (0.5, 0.36, 0.22), 5)
            ell(cf, 820, 935, 90, 38); cf.set_source_rgb(0.2, 0.12, 0.08); cf.fill()
    elif bg == "bahce":
        hills(cf, 720, 50, (0.55, 0.82, 0.45), 11)
        for tx in (120, 1820):
            tree(cf, tx, 800, 0.8)
        # çit
        for fx in range(0, W, 70):
            cf.move_to(fx, 820); cf.line_to(fx, 700); cf.line_to(fx + 25, 680); cf.line_to(fx + 50, 700); cf.line_to(fx + 50, 820)
            cf.close_path(); paint(cf, (0.98, 0.95, 0.88), 4)
        cf.rectangle(0, 730, W, 18); paint(cf, (0.98, 0.95, 0.88), 4)
        cf.rectangle(0, 780, W, 18); paint(cf, (0.98, 0.95, 0.88), 4)
        cf.rectangle(0, 820, W, H - 820); cf.set_source_rgb(0.47, 0.78, 0.34); cf.fill()
        ell(cf, 1340, 960, 520, 70); paint(cf, (0.55, 0.38, 0.22), 0)
        grass_tufts(cf, 12, 840, 1070); flowers(cf, 13, 840, 900, 25)
    elif bg == "tarla":
        hills(cf, 700, 50, (0.6, 0.83, 0.45), 21)
        tree(cf, 1820, 780, 0.7); tree(cf, 140, 760, 0.6)
        cf.rectangle(0, 800, W, H - 800); cf.set_source_rgb(0.47, 0.78, 0.34); cf.fill()
        for i in range(4):
            y = 860 + i * 55
            ell(cf, 1400, y, 560, 22); paint(cf, (0.58, 0.4, 0.24), 3)
        grass_tufts(cf, 22, 820, 1070, 30)
    elif bg == "aycicegi":
        hills(cf, 690, 50, (0.6, 0.83, 0.45), 31)
        rnd = random.Random(32)
        for _ in range(55):
            x = rnd.uniform(0, W); y = rnd.uniform(700, 790)
            cf.move_to(x, y + 40); cf.line_to(x, y); cf.set_source_rgb(0.3, 0.6, 0.2); cf.set_line_width(4); cf.stroke()
            for k in range(8):
                a = k * PI / 4
                cf.arc(x + math.cos(a) * 12, y + math.sin(a) * 12, 7, 0, 2 * PI)
            cf.set_source_rgb(1, 0.82, 0.15); cf.fill()
            cf.arc(x, y, 8, 0, 2 * PI); cf.set_source_rgb(0.45, 0.28, 0.1); cf.fill()
        cf.rectangle(0, 820, W, H - 820); cf.set_source_rgb(0.5, 0.8, 0.35); cf.fill()
        grass_tufts(cf, 33, 840, 1070); flowers(cf, 34, 850, 1070, 20)
    elif bg == "gol":
        hills(cf, 690, 55, (0.5, 0.8, 0.42), 41)
        for tx, ts in ((150, 0.9), (330, 0.7), (1850, 0.85)):
            tree(cf, tx, 800, ts, (0.26, 0.58, 0.25))
        cf.rectangle(0, 790, W, H - 790); cf.set_source_rgb(0.45, 0.78, 0.33); cf.fill()
        ell(cf, 1380, 900, 560, 120); paint(cf, (0.35, 0.65, 0.92), 6, (0.25, 0.45, 0.3))
        ell(cf, 1380, 905, 520, 100); cf.set_source_rgba(0.5, 0.78, 1, 0.5); cf.fill()
        for rx in (850, 1910):
            for k in range(6):
                cf.move_to(rx + k * 9 - 25, 860); cf.line_to(rx + k * 9 - 28, 700 + k * 9)
                cf.set_source_rgb(0.35, 0.55, 0.2); cf.set_line_width(5); cf.stroke()
            ell(cf, rx - 2, 700, 8, 26); paint(cf, (0.5, 0.33, 0.2), 3)
        grass_tufts(cf, 42, 1000, 1070, 25)
    elif bg == "dere":
        hills(cf, 670, 60, (0.55, 0.82, 0.45), 51)
        for tx, ts in ((120, 0.8), (1780, 0.9), (1550, 0.6)):
            tree(cf, tx, 740, ts)
        cf.rectangle(0, 730, W, 60); cf.set_source_rgb(0.47, 0.78, 0.34); cf.fill()
        cf.move_to(0, 770)
        for x in range(0, W + 1, 40):
            cf.line_to(x, 770 + 8 * math.sin(x / 90))
        cf.line_to(W, 880); cf.line_to(0, 880); cf.close_path(); paint(cf, (0.3, 0.6, 0.95), 5, (0.2, 0.35, 0.55))
        cf.rectangle(0, 880, W, H - 880); cf.set_source_rgb(0.47, 0.78, 0.34); cf.fill()
        cf.move_to(0, 880); cf.line_to(W, 880); cf.set_source_rgb(0.3, 0.5, 0.25); cf.set_line_width(5); cf.stroke()
        grass_tufts(cf, 52, 900, 1070); flowers(cf, 53, 900, 1070, 25)
    elif bg == "lavanta":
        sun(cb, 1500, 640, 90, 0)
        hills(cf, 700, 50, (0.55, 0.55, 0.75), 61)
        cf.rectangle(0, 760, W, H - 760); cf.set_source_rgb(0.42, 0.62, 0.32); cf.fill()
        for row in range(6):
            y = 780 + row * 52
            for x in range(-20, W + 40, 34):
                xx = x + (17 if row % 2 else 0)
                for j in range(4):
                    ell(cf, xx, y - j * 9, 8 + row, 6 + row * 0.6)
                cf.set_source_rgb(0.55 + row * 0.02, 0.38, 0.78); cf.fill()
    return back, front
