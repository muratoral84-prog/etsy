#!/usr/bin/env python3
"""Builds the Etsy listing images from real renders of the real workbook.
Nothing here is a drawing of a spreadsheet - every screenshot is the file
the buyer receives, filled with the demo year and rendered through
LibreOffice, so the listing cannot promise something the file does not do.
"""
import os
import subprocess
import sys

import pymupdf
from PIL import Image, ImageDraw, ImageFont

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
OUT = os.path.join(ROOT, "etsy", "mockups")
TMP = os.environ.get("MOCK_TMP", "/tmp/momentum-mockups")
DJV = "/usr/share/fonts/truetype/dejavu"

S = 2000                                    # Etsy square
INK, MUTED = "#161D18", "#6E7A72"
ACCENT, GOLD = "#1F6F4A", "#B8860B"
CREAM, PANEL, RULE = "#FBFAF7", "#EFF2EE", "#DCE2DD"
NIGHT, NIGHT2, NIGHT_INK = "#12151A", "#1C2129", "#ECEFF3"
MINT = "#4ADE80"

# page index inside the rendered demo PDF
PAGES = dict(today=0, starthere=1, dashboard=2, week=37)

# crop windows as fractions of the page (left, top, right, bottom)
CROPS = dict(
    dash_full=(0.115, 0.045, 0.885, 0.955),
    dash_stats=(0.125, 0.135, 0.845, 0.235),
    dash_habits=(0.125, 0.254, 0.858, 0.518),
    dash_year=(0.142, 0.655, 0.726, 0.925),
    today_full=(0.095, 0.045, 0.900, 0.640),
    week_full=(0.020, 0.040, 0.980, 0.830),
)


def font(size, bold=True):
    return ImageFont.truetype(
        DJV + ("/DejaVuSans-Bold.ttf" if bold else "/DejaVuSans.ttf"), size)


# ------------------------------------------------------------- rendering --
def render_pages():
    os.makedirs(TMP, exist_ok=True)
    sys.path.insert(0, HERE)
    import demo
    shots = {}
    for theme in ("Light", "Dark"):
        src = os.path.join(ROOT, "dist",
                           "Momentum-Habit-System-%s.xlsx" % theme)
        xlsx = os.path.join(TMP, "demo-%s.xlsx" % theme)
        demo.fill(src, xlsx)
        pdf = xlsx[:-5] + ".pdf"
        if not os.path.exists(pdf):
            subprocess.run(
                ["soffice", "--headless", "--norestore",
                 "-env:UserInstallation=file:///tmp/lo-profile",
                 "--convert-to", "pdf", "--outdir", TMP, xlsx],
                check=True, capture_output=True, timeout=900)
        doc = pymupdf.open(pdf)
        for name, idx in PAGES.items():
            px = doc[idx].get_pixmap(matrix=pymupdf.Matrix(4, 4))
            shots[(theme, name)] = Image.frombytes(
                "RGB", (px.width, px.height), px.samples)
    return shots


def crop(img, box):
    w, h = img.size
    l, t, r, b = box
    return img.crop((int(l * w), int(t * h), int(r * w), int(b * h)))


def fit(img, w, h=None):
    """Scale to width, optionally trimming the bottom to an exact height."""
    ratio = w / img.width
    img = img.resize((w, int(img.height * ratio)), Image.LANCZOS)
    return img.crop((0, 0, w, h)) if h and img.height > h else img


# ------------------------------------------------------------- drawing ----
def card(base, img, xy, pad=0, shadow=26, bg="#FFFFFF", radius=0):
    """Drops a screenshot on the canvas with a soft drop shadow."""
    x, y = xy
    w, h = img.size
    sh = Image.new("RGBA", (w + shadow * 2, h + shadow * 2), (0, 0, 0, 0))
    ImageDraw.Draw(sh).rectangle(
        (shadow, shadow + 6, shadow + w, shadow + h + 6), fill=(0, 0, 0, 46))
    from PIL import ImageFilter
    sh = sh.filter(ImageFilter.GaussianBlur(shadow / 2.2))
    base.paste(sh, (x - shadow, y - shadow), sh)
    if pad:
        ImageDraw.Draw(base).rectangle(
            (x - pad, y - pad, x + w + pad, y + h + pad), fill=bg)
    base.paste(img, (x, y))


def wrap(draw, text, fnt, maxw):
    lines, line = [], ""
    for word in text.split():
        t = (line + " " + word).strip()
        if draw.textlength(t, font=fnt) <= maxw:
            line = t
        else:
            lines.append(line)
            line = word
    if line:
        lines.append(line)
    return lines


def block(draw, text, xy, fnt, fill, maxw, lead=1.24, center=False):
    x, y = xy
    for ln in wrap(draw, text, fnt, maxw):
        w = draw.textlength(ln, font=fnt)
        draw.text((x - w / 2 if center else x, y), ln, font=fnt, fill=fill)
        y += int(fnt.size * lead)
    return y


def eyebrow(draw, text, xy, colour=ACCENT, size=32):
    draw.text(xy, text, font=font(size), fill=colour)


def canvas(bg=CREAM):
    return Image.new("RGB", (S, S), bg)


def badge_row(draw, y, items, colour=ACCENT, dim=MUTED):
    x = 150
    for label, on in items:
        f = font(38)
        w = draw.textlength(label, font=f)
        draw.rounded_rectangle((x, y, x + w + 74, y + 92), 14,
                               fill=colour if on else "#FFFFFF",
                               outline=colour if on else RULE, width=3)
        draw.text((x + 37, y + 24), label, font=f,
                  fill="#FFFFFF" if on else dim)
        x += w + 74 + 26


# --------------------------------------------------------------- images ---
def img_hero(sh):
    c = canvas()
    d = ImageDraw.Draw(c)
    d.rectangle((0, 0, S, 612), fill="#FFFFFF")
    d.line((0, 612, S, 612), fill=RULE, width=3)
    eyebrow(d, "MOMENTUM  ·  WEEKLY HABIT SYSTEM", (150, 118))
    y = block(d, "The habit tracker that", (150, 176), font(100), INK, 1720,
              1.02)
    y = block(d, "counts your streak for you.", (150, y), font(100), ACCENT,
              1720, 1.02)
    block(d, "52 weekly tabs · automatic streaks · Excel + Google Sheets",
          (150, y + 26), font(38, False), MUTED, 1720)
    card(c, fit(crop(sh[("Light", "dashboard")], CROPS["dash_full"]), 1360),
         (320, 672), pad=18)
    return c


def img_today(sh):
    c = canvas(NIGHT)
    d = ImageDraw.Draw(c)
    eyebrow(d, "IT OPENS HERE. EVERY TIME.", (150, 130), MINT)
    y = block(d, "One line tells you what", (150, 192), font(96), NIGHT_INK,
              1720, 1.03)
    y = block(d, "you are about to lose.", (150, y), font(96), MINT, 1720,
              1.03)
    card(c, fit(crop(sh[("Light", "today")], CROPS["today_full"]), 1600),
         (200, y + 90), pad=16)
    block(d, "Miss a day and the streak resets to zero. That is the only "
             "rule the system has — and the reason it works.",
          (150, 1810), font(38, False), "#9AA6B2", 1720)
    return c


def img_week(sh):
    c = canvas()
    d = ImageDraw.Draw(c)
    eyebrow(d, "THE DAILY RITUAL", (150, 130))
    block(d, "Twenty seconds a day.", (150, 190), font(104), INK, 1720)
    block(d, "Today's column is highlighted for you. Pick ✓ from the "
             "dropdown. Close the file.", (150, 330), font(40, False),
          MUTED, 1700)
    card(c, fit(crop(sh[("Light", "week")], CROPS["week_full"]), 1700),
         (150, 520), pad=16)
    return c


def img_year(sh):
    c = canvas()
    d = ImageDraw.Draw(c)
    eyebrow(d, "THE YEAR AT A GLANCE", (150, 130))
    block(d, "All 52 weeks. One screen.", (150, 190), font(100), INK, 1720)
    block(d, "Every week scored against your goals and colour-coded. The "
             "week you are in is highlighted. Click any week to jump "
             "straight to it.", (150, 322), font(38, False), MUTED, 1700)
    card(c, fit(crop(sh[("Light", "dash_year")], (0, 0, 1, 1)), 1700),
         (150, 620), pad=18)
    card(c, fit(crop(sh[("Dark", "dash_year")], (0, 0, 1, 1)), 1700),
         (150, 1320), pad=18, bg=NIGHT2)
    return c


def img_themes(sh):
    c = canvas()
    d = ImageDraw.Draw(c)
    d.rectangle((S // 2, 0, S, S), fill=NIGHT)
    eyebrow(d, "BOTH INCLUDED", (110, 120))
    block(d, "Light.", (110, 178), font(96), INK, 820)
    eyebrow(d, "SAME FILE, NIGHT COLOURS", (S // 2 + 110, 120), MINT)
    block(d, "Dark.", (S // 2 + 110, 178), font(96), NIGHT_INK, 820)
    card(c, fit(crop(sh[("Light", "today")], CROPS["today_full"]), 860),
         (70, 420), pad=14)
    card(c, fit(crop(sh[("Dark", "today")], CROPS["today_full"]), 860),
         (S // 2 + 70, 420), pad=14, bg=NIGHT2)
    card(c, fit(crop(sh[("Light", "dash_habits")], (0, 0, 1, 1)), 860),
         (70, 1180), pad=14)
    card(c, fit(crop(sh[("Dark", "dash_habits")], (0, 0, 1, 1)), 860),
         (S // 2 + 70, 1180), pad=14, bg=NIGHT2)
    block(d, "Two workbooks in the download. Pick one, or keep both.",
          (110, 1700), font(36, False), MUTED, 780)
    block(d, "Identical formulas, identical streak engine.",
          (S // 2 + 110, 1700), font(36, False), "#9AA6B2", 780)
    return c


def img_badges(sh):
    c = canvas()
    d = ImageDraw.Draw(c)
    eyebrow(d, "MILESTONES", (150, 130))
    y = block(d, "Badges you cannot", (150, 190), font(100), INK, 1720, 1.03)
    y = block(d, "un-earn.", (150, y), font(100), GOLD, 1720, 1.03)
    block(d, "7, 30, 100 and 365 consecutive days. They unlock from your "
             "best streak ever — so one bad week never takes a badge back.",
          (150, y + 40), font(38, False), MUTED, 1700)
    badge_row(d, 900, [("7 DAYS", True), ("30 DAYS", True),
                       ("100 DAYS", False), ("365 DAYS", False)], GOLD)
    card(c, fit(crop(sh[("Light", "dash_habits")], (0, 0, 1, 1)), 1700),
         (150, 1120), pad=16)
    block(d, "The Today tab counts down the days to your next one.",
          (150, 1800), font(36, False), MUTED, 1700)
    return c


def img_compat(sh):
    c = canvas("#FFFFFF")
    d = ImageDraw.Draw(c)
    eyebrow(d, "COMPATIBILITY", (150, 130))
    block(d, "Opens everywhere.", (150, 190), font(100), INK, 1720)
    block(d, "Built with ordinary formulas only — no macros, nothing to "
             "enable, nothing to install.", (150, 330), font(38, False),
          MUTED, 1700)
    rows = [("Microsoft Excel", "Windows · Mac · iPad · iPhone · Android"),
            ("Google Sheets", "Upload once. Streaks and all."),
            ("LibreOffice / Numbers", "Opens and calculates fine."),
            ("Your phone", "One tap from the home screen. The guide "
                           "shows you how.")]
    y = 500
    for t, s_ in rows:
        d.rounded_rectangle((150, y, 1850, y + 190), 16, fill=PANEL)
        d.rounded_rectangle((150, y, 162, y + 190), 6, fill=ACCENT)
        d.text((210, y + 44), t, font=font(52), fill=INK)
        d.text((210, y + 116), s_, font=font(34, False), fill=MUTED)
        y += 214
    y += 34
    for line in ("No macros. No security warnings, ever.",
                 "No account, no subscription, no internet.",
                 "No monthly fee. You buy a file and it is yours."):
        d.text((150, y), "✕", font=font(44), fill=ACCENT)
        d.text((222, y + 4), line, font=font(40, False), fill=INK)
        y += 82
    return c


def img_included(sh):
    c = canvas()
    d = ImageDraw.Draw(c)
    eyebrow(d, "INSTANT DOWNLOAD", (150, 130))
    block(d, "Three files. No waiting.", (150, 190), font(100), INK, 1720)
    files = [("Momentum-Habit-System-Light.xlsx",
              "The light theme · 55 tabs · Excel + Google Sheets"),
             ("Momentum-Habit-System-Dark.xlsx",
              "The dark theme · identical formulas"),
             ("Momentum-Quick-Start-Guide.pdf",
              "3 pages · set up in three minutes")]
    y = 480
    for name, sub in files:
        d.rounded_rectangle((150, y, 1850, y + 250), 18, fill="#FFFFFF",
                            outline=RULE, width=3)
        d.rounded_rectangle((196, y + 56, 300, y + 194), 12, fill=ACCENT)
        ext = name.rsplit(".", 1)[1].upper()
        w = d.textlength(ext, font=font(40))
        d.text((248 - w / 2, y + 104), ext, font=font(40), fill="#FFFFFF")
        d.text((352, y + 76), name, font=font(42), fill=INK)
        d.text((352, y + 142), sub, font=font(32, False), fill=MUTED)
        y += 286
    y += 30
    d.line((150, y, 1850, y), fill=RULE, width=3)
    y += 56
    eyebrow(d, "INSIDE EACH WORKBOOK", (150, y))
    y += 66
    inside = [("Today", "opens here · what is at risk tonight"),
              ("Start Here", "one date, up to ten habits"),
              ("Dashboard", "streaks, badges, the 52-week map"),
              ("W01 – W52", "one tab per week · Mon to Sun")]
    for name, sub in inside:
        d.text((150, y), "—", font=font(34), fill=ACCENT)
        d.text((210, y), name, font=font(36), fill=INK)
        d.text((530, y + 2), sub, font=font(32, False), fill=MUTED)
        y += 62
    block(d, "Files appear the moment payment clears — Etsy emails them and "
             "they sit under Purchases. Nothing is posted to you.",
          (150, y + 34), font(34, False), MUTED, 1700)
    return c


BUILDERS = [("01-hero", img_hero), ("02-today", img_today),
            ("03-week", img_week), ("04-year", img_year),
            ("05-themes", img_themes), ("06-badges", img_badges),
            ("07-compatibility", img_compat), ("08-included", img_included)]


def main():
    os.makedirs(OUT, exist_ok=True)
    shots = render_pages()
    # pre-crop the dashboard regions the layouts reuse
    for theme in ("Light", "Dark"):
        for key in ("dash_stats", "dash_habits", "dash_year"):
            shots[(theme, key)] = crop(shots[(theme, "dashboard")],
                                       CROPS[key])
    for name, fn in BUILDERS:
        path = os.path.join(OUT, "%s.png" % name)
        fn(shots).save(path, optimize=True)
        print("  %-28s %6.0f KB" % (name + ".png",
                                    os.path.getsize(path) / 1024))


if __name__ == "__main__":
    main()
