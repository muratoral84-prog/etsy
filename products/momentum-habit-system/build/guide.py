#!/usr/bin/env python3
"""Builds the buyer-facing quick-start PDF that ships alongside the workbook."""
import os
import sys

from reportlab.lib.pagesizes import A4
from reportlab.lib.units import mm
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfgen import canvas

HERE = os.path.dirname(os.path.abspath(__file__))
DIST = os.path.join(os.path.dirname(HERE), "dist")
DJV = "/usr/share/fonts/truetype/dejavu"
INK, MUTED, ACCENT, GOLD = "#161D18", "#6E7A72", "#1F6F4A", "#8A6D10"
RULE, PANEL = "#DDE3DE", "#F2F5F2"
W, H = A4
M = 20 * mm


def rgb(c):
    c = c.lstrip("#")
    return tuple(int(c[i:i + 2], 16) / 255 for i in (0, 2, 4))


class Guide:
    def __init__(self, path):
        pdfmetrics.registerFont(TTFont("D", DJV + "/DejaVuSans.ttf"))
        pdfmetrics.registerFont(TTFont("DB", DJV + "/DejaVuSans-Bold.ttf"))
        self.c = canvas.Canvas(path, pagesize=A4)
        self.c.setTitle("Momentum - Quick Start Guide")
        self.c.setAuthor("Momentum")
        self.y = 0
        self.page = 0
        self.new_page()

    # -- primitives -------------------------------------------------------
    def new_page(self):
        if self.page:
            self.footer()
            self.c.showPage()
        self.page += 1
        self.y = H - M
        self.c.setFillColorRGB(*rgb(MUTED))
        self.c.setFont("DB", 7)
        self.c.drawString(M, H - M + 6 * mm, "MOMENTUM  ·  WEEKLY HABIT SYSTEM")

    def footer(self):
        self.c.setFillColorRGB(*rgb(MUTED))
        self.c.setFont("D", 7.5)
        self.c.drawString(M, M - 8 * mm,
                          "Momentum — Weekly Habit System   ·   "
                          "Quick Start Guide")
        self.c.drawRightString(W - M, M - 8 * mm, "%d" % self.page)

    def space(self, mm_):
        self.y -= mm_ * mm

    def need(self, mm_):
        if self.y - mm_ * mm < M + 4 * mm:
            self.new_page()

    def h1(self, text):
        self.need(34)     # a heading must not strand itself above a break
        self.space(4)
        self.c.setFillColorRGB(*rgb(INK))
        self.c.setFont("DB", 21)
        self.c.drawString(M, self.y, text)
        self.space(3)
        self.c.setStrokeColorRGB(*rgb(ACCENT))
        self.c.setLineWidth(1.4)
        self.c.line(M, self.y, M + 26 * mm, self.y)
        self.space(7)

    def h2(self, text):
        self.need(16)
        self.space(3)
        self.c.setFillColorRGB(*rgb(ACCENT))
        self.c.setFont("DB", 11)
        self.c.drawString(M, self.y, text)
        self.space(6)

    def p(self, text, font="D", size=9.6, colour=INK, lead=5.0, indent=0):
        self.c.setFont(font, size)
        self.c.setFillColorRGB(*rgb(colour))
        maxw = W - 2 * M - indent
        words, line = text.split(), ""
        for wd in words:
            trial = (line + " " + wd).strip()
            if self.c.stringWidth(trial, font, size) <= maxw:
                line = trial
            else:
                self.need(8)
                self.c.setFont(font, size)
                self.c.setFillColorRGB(*rgb(colour))
                self.c.drawString(M + indent, self.y, line)
                self.space(lead)
                line = wd
        if line:
            self.need(8)
            self.c.setFont(font, size)
            self.c.setFillColorRGB(*rgb(colour))
            self.c.drawString(M + indent, self.y, line)
            self.space(lead)

    def step(self, n, title, body):
        self.need(22)
        self.space(2)
        self.c.setFillColorRGB(*rgb(ACCENT))
        self.c.circle(M + 2.6 * mm, self.y + 1.1 * mm, 2.9 * mm, fill=1,
                      stroke=0)
        self.c.setFillColorRGB(1, 1, 1)
        self.c.setFont("DB", 9)
        self.c.drawCentredString(M + 2.6 * mm, self.y - 0.4 * mm, str(n))
        self.c.setFillColorRGB(*rgb(INK))
        self.c.setFont("DB", 10.5)
        self.c.drawString(M + 8 * mm, self.y, title)
        self.space(5.2)
        self.p(body, indent=8 * mm, colour=MUTED)
        self.space(1.5)

    def bullet(self, text, mark="—"):
        self.need(10)
        self.c.setFillColorRGB(*rgb(ACCENT))
        self.c.setFont("DB", 9.6)
        self.c.drawString(M + 1 * mm, self.y, mark)
        self.p(text, indent=7 * mm)

    def panel(self, title, lines, tint=PANEL, edge=RULE):
        h = 9 * mm + len(lines) * 5.0 * mm
        self.need(h / mm + 4)
        self.c.setFillColorRGB(*rgb(tint))
        self.c.setStrokeColorRGB(*rgb(edge))
        self.c.setLineWidth(0.6)
        self.c.roundRect(M, self.y - h + 4 * mm, W - 2 * M, h, 2 * mm,
                         fill=1, stroke=1)
        self.space(1)
        self.c.setFillColorRGB(*rgb(ACCENT))
        self.c.setFont("DB", 8)
        self.c.drawString(M + 4 * mm, self.y, title)
        self.space(5)
        for ln in lines:
            self.c.setFillColorRGB(*rgb(INK))
            self.c.setFont("D", 9)
            self.c.drawString(M + 4 * mm, self.y, ln)
            self.space(5)
        self.space(3)

    def save(self):
        self.footer()
        self.c.save()


def build(path):
    g = Guide(path)

    # ---------------------------------------------------------------- p1 --
    g.space(6)
    g.c.setFillColorRGB(*rgb(INK))
    g.c.setFont("DB", 34)
    g.c.drawString(M, g.y, "MOMENTUM")
    g.space(9)
    g.c.setFillColorRGB(*rgb(ACCENT))
    g.c.setFont("DB", 11)
    g.c.drawString(M, g.y, "WEEKLY HABIT SYSTEM  ·  QUICK START")
    g.space(12)
    g.p("Thank you for buying Momentum. This guide takes about three "
        "minutes, and you only ever need to read it once. Everything after "
        "setup is one tap a day.", size=10.5)
    g.space(4)

    g.h1("Set up in 3 steps")
    g.step(1, "Open the file",
           "You received two workbooks — a Light one and a Dark one. They are "
           "identical apart from colour. Pick one and ignore the other, or "
           "keep both and switch when the season changes. Open it in "
           "Microsoft Excel, or upload it to Google Sheets (File → Import → "
           "Upload → Replace spreadsheet).")
    g.step(2, "Set your start date",
           "Go to the Start Here tab and type the Monday you want Week 01 to "
           "begin into the green box. Every one of the 52 week tabs re-dates "
           "itself from that single cell. You do not have to start in "
           "January — starting on the Monday coming up is the better idea.")
    g.step(3, "Name your habits",
           "Still on Start Here, type up to ten habits and how many days a "
           "week you want each one. Anything you leave blank disappears "
           "everywhere else in the file. Then click Open Dashboard, or just "
           "go to the Today tab.")

    g.panel("ONE PIECE OF ADVICE", [
        "Start with three habits. Not ten.",
        "Ten habits is how a tracker becomes a chore you quietly abandon in",
        "March. Three is how a streak survives a bad week. You can always",
        "add more once the first three feel automatic.",
    ])

    g.h1("The daily loop")
    g.p("The file opens on the Today tab. That is deliberate. It shows you "
        "one thing before anything else: which streaks die tonight if you "
        "do nothing.")
    g.space(2)
    g.bullet("Open the file. Read the line at the top.")
    g.bullet("Click through to this week's tab (the Dashboard highlights "
             "the week you are in).")
    g.bullet("In today's column, pick ✓ from the dropdown for each habit "
             "you did.")
    g.bullet("Close the file. That is the whole ritual — about twenty "
             "seconds.")

    g.h1("How the marks work")
    g.p("Click any day cell in a week tab and a small dropdown appears with "
        "two options:")
    g.space(2)
    g.bullet("✓  — you did it. This is the only mark that feeds a streak.",
             mark="")
    g.bullet("✗  — you deliberately missed it. Use this when you want the "
             "record to show you chose to skip, not that you forgot to log.",
             mark="")
    g.space(2)
    g.p("A cell you leave blank counts exactly the same as ✗ for your "
        "streak. The difference is only for you, when you look back and try "
        "to work out what went wrong in March.")
    g.p("If the dropdown ever gets in your way, you can type any letter into "
        "a day cell and it will count as done. Only ✗ counts as a miss.",
        colour=MUTED)

    g.h1("What counts as a streak")
    g.p("A streak is the number of consecutive days you marked a habit ✓. "
        "It runs straight across week tabs — Sunday to Monday is not a "
        "reset. Miss one day and it drops to zero. That is the only rule "
        "the system has, and it is the reason the thing works.")
    g.space(2)
    g.panel("TODAY IS FORGIVEN UNTIL MIDNIGHT", [
        "An unticked today never shows as a broken streak. Until you mark",
        "it, your streak keeps yesterday's number and the Today tab flags",
        "the habit as AT RISK. The moment you tick it, the number moves.",
    ], tint="#FBF6E6", edge="#E6D9A8")

    g.h1("Badges")
    g.p("Four badges unlock automatically at 7, 30, 100 and 365 consecutive "
        "days: on the Dashboard, in the MILESTONES columns. They are based "
        "on your best streak ever, not your current one — so a badge you "
        "have earned is yours for good, even after a bad week. The Today "
        "tab tells you how many days of unbroken run stand between you and "
        "the next one.")

    g.h1("Reading the Dashboard")
    g.bullet("TOTAL CHECK-INS — every ✓ you have ever made in this file.")
    g.bullet("BEST STREAK — your longest run across all habits.")
    g.bullet("STREAKS ALIVE — how many habits are currently running.")
    g.bullet("THE YEAR AT A GLANCE — all 52 weeks. The week you are in is "
             "highlighted; click any week to jump to it. The percentage is "
             "that week's ticks measured against the weekly goals you set.")

    g.h1("Using it on your phone")
    g.p("This is where most trackers quietly die, so it is worth ninety "
        "seconds of setup.")
    g.space(2)
    g.step(1, "Put the file somewhere your phone can reach it",
           "Google Drive, OneDrive, iCloud Drive or Dropbox — whichever you "
           "already use. Editing it on your phone and on your laptop keeps "
           "the same file in sync as long as it lives in cloud storage and "
           "not in your downloads folder.")
    g.step(2, "Install the matching app",
           "Google Sheets or Microsoft Excel, both free on iOS and Android. "
           "Open the file once from inside the app so it appears in your "
           "recent files.")
    g.step(3, "Add it to your home screen",
           "In Google Sheets on Android: open the file, tap ⋮ → Add to Home "
           "screen. On iPhone, add the Sheets or Excel app to your dock and "
           "the file will be the first item in Recents. One tap to open, "
           "one tap to tick.")

    g.h1("If something looks wrong")
    g.panel("THE DATES ARE NOT WHAT I EXPECTED", [
        "Every date in the file is calculated from the one cell on Start",
        "Here. Change that cell and all 52 weeks follow. Make sure it is a",
        "Monday — the columns are labelled Mon to Sun.",
    ])
    g.panel("MY STREAK SAYS 0 BUT I TICKED TODAY", [
        "Check that the tick landed in the right week tab, and that the",
        "start date is correct. If the start date is in the future, no day",
        "has happened yet as far as the file is concerned.",
    ])
    g.panel("THE ✓ CHARACTER LOOKS ODD", [
        "A few older Excel versions render the tick in a different font.",
        "It still counts. If it bothers you, type an x instead — anything",
        "that is not ✗ counts as done.",
    ])
    g.panel("I WANT MORE THAN TEN HABITS", [
        "Ten is the ceiling by design, and honestly ten is already too",
        "many. If you genuinely need more, keep a second copy of the file",
        "for the second set — the streak engine is per file.",
    ])

    g.h1("Two things worth knowing")
    g.bullet("There are no macros in this file. Nothing runs, nothing "
             "phones home, and no security warning should ever appear. If "
             "your spreadsheet app asks to enable content, it is not asking "
             "about this workbook.")
    g.bullet("There is a hidden tab called Engine. It does the streak "
             "arithmetic. You never need to open it — but please do not "
             "delete it, because everything else reads from it.")
    g.space(4)
    g.p("That is everything. Go and tick something.", font="DB", size=11,
        colour=ACCENT)

    g.save()
    return path


if __name__ == "__main__":
    out = os.path.join(DIST, "Momentum-Quick-Start-Guide.pdf")
    build(out)
    print("  %-46s %7.1f KB" % (os.path.basename(out),
                                os.path.getsize(out) / 1024))
