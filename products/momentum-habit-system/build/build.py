#!/usr/bin/env python3
"""
Momentum - Weekly Habit System
Generates the sellable .xlsx workbook (light + dark themes).

Design constraints (deliberate):
  * no macros, no VBA          -> opens clean in Excel and Google Sheets
  * no SPARKLINE/QUERY/etc.    -> Sheets-only functions are avoided
  * every cross-sheet formula is written literally (no INDIRECT)
    so nothing is volatile and recalculation stays instant
"""
import os
import sys

from openpyxl import Workbook
from openpyxl.utils import get_column_letter as CL
from openpyxl.styles import (Font, PatternFill, Alignment, Border, Side,
                             NamedStyle)
from openpyxl.worksheet.datavalidation import DataValidation
from openpyxl.worksheet.hyperlink import Hyperlink
from openpyxl.formatting.rule import CellIsRule, ColorScaleRule, FormulaRule
from openpyxl.worksheet.properties import PageSetupProperties

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from theme import THEMES  # noqa: E402

# ---------------------------------------------------------------- geometry --
N_HABITS = 10
N_WEEKS = 52
N_DAYS = N_WEEKS * 7                      # 364
DOW = ["MON", "TUE", "WED", "THU", "FRI", "SAT", "SUN"]

SETUP = "Start Here"
DASH = "Dashboard"
TODAY = "Today"
ENGINE = "Engine"

# --- Start Here sheet
S_HAB_R0 = 11                             # first habit row (C=name, E=goal)
S_START_CELL = "E6"                       # the one date the buyer types
S_START_ABS = "$E$6"

# --- weekly sheet
W_DOW_R, W_DATE_R = 6, 7
W_HAB_R0 = 9                              # habit rows 9..18
W_DAY_C0 = 3                              # C..I
W_DONE_C, W_GOAL_C, W_HIT_C, W_STK_C = 11, 12, 13, 14   # K L M N
W_TOTAL_R = 20
W_SCORE_R = 22
W_FOCUS_R = 24
W_NOTES_R = 26
W_PAINT_R, W_PAINT_C = 30, 15

# --- engine sheet (hidden)
E_SEED_R = 2                              # zero row so streaks can look back
E_R0 = 3                                  # first real day row
E_RN = E_R0 + N_DAYS - 1                  # 366
E_DONE_C0 = 4                             # D..M   (0/1 per habit per day)
E_STK_C0 = 15                             # O..X   (running streak per habit)
E_NAME_C, E_CUR_C, E_BEST_C, E_TOT_C = 26, 27, 28, 29   # Z AA AB AC
E_TDY_C, E_NXT_C, E_GAP_C = 30, 31, 32                  # AD AE AF
E_HELP_R0 = 2                             # helper block rows 2..11

# --- dashboard (uniform 6-wide grid, columns C..S)
D_C0, D_CN = 3, 19
D_HAB_R0 = 13
D_IDX_R0 = 29                             # week index block

DEFAULT_HABITS = [
    ("Move my body 30 min", 5),
    ("Read 10 pages", 6),
    ("Lights out by 23:00", 5),
    ("Drink 2L water", 7),
    ("Plan tomorrow tonight", 5),
]

MILESTONES = [(7, "7"), (30, "30"), (100, "100"), (365, "365")]


def wk(n):
    return "W%02d" % n


# ------------------------------------------------------------------ styles --
class S:
    """Builds every Font/Fill/Border once per theme so the xlsx style table
    stays small even though we touch ~30k cells."""

    def __init__(self, t):
        self.t = t
        F = lambda **k: Font(name="Calibri", **k)
        self.h1 = F(size=26, bold=True, color=t["ink"])
        self.h2 = F(size=15, bold=True, color=t["ink"])
        self.brand = F(size=9, bold=True, color=t["muted"])
        self.brand_a = F(size=9, bold=True, color=t["accent"])
        self.label = F(size=8, bold=True, color=t["muted"])
        self.body = F(size=11, color=t["ink"])
        self.body_b = F(size=11, bold=True, color=t["ink"])
        self.muted = F(size=10, color=t["muted"])
        self.small = F(size=9, color=t["muted"])
        self.accent = F(size=11, bold=True, color=t["accent"])
        self.stat = F(size=22, bold=True, color=t["accent"])
        self.stat_ink = F(size=22, bold=True, color=t["ink"])
        self.link = F(size=10, bold=True, color=t["accent"], underline="single")
        self.idx = F(size=9, bold=True, color=t["accent"], underline="single")
        self.mark = F(size=12, bold=True, color=t["done_fg"])
        self.input = F(size=11, color=t["ink"])
        self.gold = F(size=11, bold=True, color=t["gold"])

        P = lambda c: PatternFill("solid", fgColor=c)
        self.bg = P(t["bg"])
        self.panel = P(t["panel"])
        self.panel2 = P(t["panel2"])
        self.accent_sf = P(t["accent_sf"])
        self.gold_sf = P(t["gold_sf"])
        self.done = P(t["done_bg"])
        self.miss = P(t["miss_bg"])
        self.today = P(t["today_bg"])
        self.grid_f = P(t["grid_soft"])
        # every hyperlink cell sits on a light chip: Excel, Sheets and
        # LibreOffice each force their own link colour over the cell font,
        # so the background is the only thing we actually control
        self.chip = P(t["chip"])
        self.chip_now = P(t["chip_now"])

        thin = Side(style="thin", color=t["grid"])
        hair = Side(style="hair", color=t["grid"])
        self.box = Border(left=thin, right=thin, top=thin, bottom=thin)
        self.cell = Border(left=hair, right=hair, top=hair, bottom=hair)
        self.under = Border(bottom=Side(style="thin", color=t["accent"]))
        self.under_soft = Border(bottom=Side(style="thin", color=t["grid"]))
        self.none = Border()
        self.hidden = F(size=1, color=t["bg"])
        self.cf_chip_now = P(t["chip_now"])
        self.cf_week_now = Font(name="Calibri", size=9, bold=True,
                                color=t["ink"], underline="single")
        gone = Side(style="thin", color=t["bg"])
        self.erase = Border(left=gone, right=gone, top=gone, bottom=gone)

        # conditional-format fonts/fills
        self.cf_done = P(t["done_bg"])
        self.cf_done_f = Font(name="Calibri", size=12, bold=True, color=t["done_fg"])
        self.cf_miss = P(t["miss_bg"])
        self.cf_miss_f = Font(name="Calibri", size=12, bold=True, color=t["miss_fg"])
        self.cf_today = P(t["today_bg"])
        self.cf_today_f = Font(name="Calibri", size=9, bold=True, color=t["today_fg"])
        self.cf_gold = P(t["gold_sf"])
        self.cf_gold_f = Font(name="Calibri", size=12, bold=True, color=t["gold"])


C_MID = Alignment(horizontal="center", vertical="center")
C_L = Alignment(horizontal="left", vertical="center")
C_R = Alignment(horizontal="right", vertical="center")
C_WRAP = Alignment(horizontal="left", vertical="top", wrap_text=True)


def paint(ws, nrows, ncols, st):
    """Flood the visible canvas so the dark theme is actually dark."""
    for r in range(1, nrows + 1):
        for c in range(1, ncols + 1):
            ws.cell(row=r, column=c).fill = st.bg


def put(ws, coord, value, font=None, align=None, fill=None,
        border=None, fmt=None):
    c = ws[coord]
    c.value = value
    if font:
        c.font = font
    if align:
        c.alignment = align
    if fill:
        c.fill = fill
    if border:
        c.border = border
    if fmt:
        c.number_format = fmt
    return c


def printable(ws, area):
    """One sheet = one clean landscape page. Buyers print a week and stick it
    on the fridge; this is also what the listing mock-ups are rendered from."""
    ws.print_area = area
    ws.page_setup.orientation = "landscape"
    ws.page_setup.fitToWidth = 1
    ws.page_setup.fitToHeight = 1
    ws.sheet_properties.pageSetUpPr = PageSetupProperties(fitToPage=True)
    ws.print_options.horizontalCentered = True
    for side in ("left", "right", "top", "bottom"):
        setattr(ws.page_margins, side, 0.3)


def link(ws, coord, target, label, font):
    c = ws[coord]
    c.value = label
    c.hyperlink = Hyperlink(ref=coord, location="'%s'!A1" % target)
    c.font = font
    c.alignment = C_MID
    return c


# ------------------------------------------------------------- Start Here --
def build_setup(wb, st, t):
    ws = wb.create_sheet(SETUP)
    ws.sheet_view.showGridLines = False
    ws.sheet_properties.tabColor = t["tab"]
    paint(ws, 34, 13, st)

    for col, w in zip("ABCDEFGHIJKLM",
                      [2, 3, 38, 3, 12, 3, 14, 3, 3, 30, 3, 3, 3]):
        ws.column_dimensions[col].width = w
    ws.row_dimensions[2].height = 30
    ws.row_dimensions[3].height = 20

    put(ws, "B2", "MOMENTUM", st.h1, C_L)
    put(ws, "B3", "WEEKLY HABIT SYSTEM  ·  52 WEEKS  ·  10 HABITS",
        st.brand_a, C_L)

    # -- step 1 -----------------------------------------------------------
    put(ws, "B5", "1  ·  SET YOUR START DATE", st.h2, C_L)
    ws["B5"].border = st.under
    put(ws, "C6", "Pick the Monday you want Week 01 to begin", st.muted, C_L)
    c = put(ws, S_START_CELL, "=DATE(2026,1,5)", st.body_b, C_MID,
            st.accent_sf, st.box, "yyyy-mm-dd")
    put(ws, "G6", "◀ type here", st.small, C_L)

    # -- step 2 -----------------------------------------------------------
    put(ws, "B8", "2  ·  NAME YOUR HABITS", st.h2, C_L)
    ws["B8"].border = st.under
    put(ws, "C9", "Anything you leave blank simply disappears from the "
                  "tracker.", st.muted, C_L)

    hdr = [("C", "HABIT"), ("E", "GOAL / WEEK"), ("G", "CURRENT STREAK")]
    for col, label in hdr:
        put(ws, "%s10" % col, label, st.label,
            C_L if col == "C" else C_MID)
        ws["%s10" % col].border = st.under_soft

    for h in range(1, N_HABITS + 1):
        r = S_HAB_R0 + h - 1
        ws.row_dimensions[r].height = 20
        put(ws, "B%d" % r, h, st.small, C_MID)
        name, goal = (DEFAULT_HABITS[h - 1] if h <= len(DEFAULT_HABITS)
                      else ("", ""))
        put(ws, "C%d" % r, name, st.input, C_L, st.panel, st.cell)
        put(ws, "E%d" % r, goal, st.input, C_MID, st.panel, st.cell)
        put(ws, "G%d" % r,
            "=IF($C%d=\"\",\"\",%s!$%s$%d)" % (r, ENGINE, CL(E_CUR_C),
                                               E_HELP_R0 + h - 1),
            st.accent, C_MID, None, st.cell)

    dv = DataValidation(type="whole", operator="between",
                        formula1=1, formula2=7, allow_blank=True,
                        showErrorMessage=True,
                        errorTitle="Goal must be 1-7",
                        error="How many days a week do you want to hit this "
                              "habit? Enter a number from 1 to 7.")
    ws.add_data_validation(dv)
    dv.add("E%d:E%d" % (S_HAB_R0, S_HAB_R0 + N_HABITS - 1))

    # -- step 3 -----------------------------------------------------------
    put(ws, "B22", "3  ·  START TRACKING", st.h2, C_L)
    ws["B22"].border = st.under
    put(ws, "C23", "Open your week, pick ✓ from the dropdown, done. "
                   "Takes 20 seconds.", st.muted, C_L)
    link(ws, "C24", DASH, "◆  OPEN DASHBOARD", st.link)
    ws["C24"].fill = st.chip
    ws["C24"].border = st.box
    ws["C24"].alignment = C_MID
    ws.merge_cells("E24:G24")
    link(ws, "E24", wk(1), "▶  GO TO WEEK 01", st.link)
    for col in "EFG":
        ws["%s24" % col].fill = st.chip
        ws["%s24" % col].border = st.box

    # -- side panel: how it works ----------------------------------------
    put(ws, "J5", "HOW IT WORKS", st.label, C_L)
    ws["J5"].border = st.under_soft
    notes = [
        "Every week has its own tab: W01 → W52.",
        "",
        "In a week tab, click a day cell and choose:",
        "   ✓   did it",
        "   ✗   missed it on purpose",
        "Leaving it blank also counts as a miss.",
        "",
        "STREAK counts consecutive ✓ days and rolls",
        "straight across week tabs — miss one day and",
        "it resets to zero. That is the whole game.",
        "",
        "Badges unlock automatically at 7, 30, 100 and",
        "365 days. They are based on your best streak,",
        "so a badge once earned is yours for good.",
        "",
        "Nothing here needs the internet, an account or",
        "a subscription. The file is yours.",
    ]
    for i, line in enumerate(notes):
        put(ws, "J%d" % (6 + i), line, st.small, C_L)

    put(ws, "J26", "TIP", st.label, C_L)
    put(ws, "J27", "Track 3 habits, not 10. Streaks die of ambition.",
        st.muted, C_L)
    printable(ws, "A1:M29")
    return ws


# ----------------------------------------------------------- weekly sheet --
def build_week(wb, st, t, w):
    ws = wb.create_sheet(wk(w))
    ws.sheet_view.showGridLines = False
    ws.sheet_properties.tabColor = t["tab"] if w % 4 == 1 else t["tab_alt"]
    paint(ws, W_PAINT_R, W_PAINT_C, st)

    ws.column_dimensions["A"].width = 2
    ws.column_dimensions["B"].width = 32
    for d in range(7):
        ws.column_dimensions[CL(W_DAY_C0 + d)].width = 7.5
    ws.column_dimensions["J"].width = 2
    for col, wd in (("K", 8), ("L", 8), ("M", 6), ("N", 9), ("O", 2)):
        ws.column_dimensions[col].width = wd
    ws.row_dimensions[3].height = 30
    ws.row_dimensions[W_DOW_R].height = 18
    ws.row_dimensions[W_DATE_R].height = 16

    d0, d6 = CL(W_DAY_C0), CL(W_DAY_C0 + 6)
    hab_lo, hab_hi = W_HAB_R0, W_HAB_R0 + N_HABITS - 1
    grid = "%s%d:%s%d" % (d0, hab_lo, d6, hab_hi)
    active = 'SUMPRODUCT(--($B$%d:$B$%d<>""))' % (hab_lo, hab_hi)

    # -- header -----------------------------------------------------------
    put(ws, "B2", "MOMENTUM  ·  WEEKLY HABIT SYSTEM", st.brand, C_L)
    put(ws, "B3", "WEEK %02d" % w, st.h1, C_L)
    ws.merge_cells("K3:N3")
    put(ws, "K3", '=TEXT(%s%d,"d mmm")&"  –  "&TEXT(%s%d,"d mmm yyyy")'
        % (d0, W_DATE_R, d6, W_DATE_R), st.body_b, C_R)

    prev = wk(w - 1) if w > 1 else SETUP
    nxt = wk(w + 1) if w < N_WEEKS else DASH
    link(ws, "B4", prev,
         "◀  %s" % ("WEEK %02d" % (w - 1) if w > 1 else "START HERE"), st.link)
    ws["B4"].alignment = C_L
    ws.merge_cells("K4:L4")
    link(ws, "K4", DASH, "◆ DASHBOARD", st.link)
    ws.merge_cells("M4:N4")
    link(ws, "M4", nxt,
         "%s  ▶" % ("WEEK %02d" % (w + 1) if w < N_WEEKS else "DASHBOARD"),
         st.link)
    for coord in ("B4", "K4", "L4", "M4", "N4"):
        ws[coord].fill = st.chip

    # -- column headers ---------------------------------------------------
    put(ws, "B%d" % W_DOW_R, "HABIT", st.label, C_L, None, st.under_soft)
    for d in range(7):
        col = CL(W_DAY_C0 + d)
        put(ws, "%s%d" % (col, W_DOW_R), DOW[d], st.label, C_MID)
        off = (w - 1) * 7 + d
        put(ws, "%s%d" % (col, W_DATE_R),
            "='%s'!%s%s" % (SETUP, S_START_ABS,
                            "+%d" % off if off else ""),
            st.small, C_MID, None, None, "d mmm")
    for col, label in (("K", "DONE"), ("L", "GOAL"), ("M", "HIT"),
                       ("N", "STREAK")):
        put(ws, "%s%d" % (col, W_DOW_R), label, st.label, C_MID,
            None, st.under_soft)

    # -- habit rows -------------------------------------------------------
    for h in range(1, N_HABITS + 1):
        r = W_HAB_R0 + h - 1
        s_row = S_HAB_R0 + h - 1
        ws.row_dimensions[r].height = 22
        put(ws, "B%d" % r,
            "=IF('%s'!C%d=\"\",\"\",'%s'!C%d)" % (SETUP, s_row, SETUP, s_row),
            st.body, C_L, None, st.under_soft)
        for d in range(7):
            cell = ws.cell(row=r, column=W_DAY_C0 + d)
            cell.font = st.mark
            cell.alignment = C_MID
            cell.border = st.cell
            cell.fill = st.grid_f
        row_rng = "%s%d:%s%d" % (d0, r, d6, r)
        put(ws, "K%d" % r,
            '=IF($B%d="","",COUNTA(%s)-COUNTIF(%s,"✗"))'
            % (r, row_rng, row_rng), st.body_b, C_MID, None, st.cell)
        put(ws, "L%d" % r,
            "=IF('%s'!E%d=\"\",\"\",'%s'!E%d)" % (SETUP, s_row, SETUP, s_row),
            st.muted, C_MID, None, st.cell)
        put(ws, "M%d" % r,
            '=IF(OR($B%d="",$L%d=""),"",IF($K%d>=$L%d,"✓",""))'
            % (r, r, r, r), st.accent, C_MID, None, st.cell)
        stk = CL(E_STK_C0 + h - 1)
        # inside the current week -> the live streak (which forgives an
        # unticked today); a finished week -> the streak as it stood on the
        # Sunday. Same number the Dashboard shows, never a second opinion.
        put(ws, "N%d" % r,
            '=IF($B%d="","",IF($%s$%d>TODAY(),"",'
            'IF(AND($%s$%d<=TODAY(),$%s$%d>=TODAY()),%s!$%s$%d,'
            'IFERROR(LOOKUP(2,1/(%s!$A$%d:$A$%d<=$%s$%d),'
            '%s!$%s$%d:$%s$%d),0))))'
            % (r, d0, W_DATE_R,
               d0, W_DATE_R, d6, W_DATE_R,
               ENGINE, CL(E_CUR_C), E_HELP_R0 + h - 1,
               ENGINE, E_R0, E_RN, d6, W_DATE_R,
               ENGINE, stk, E_R0, stk, E_RN),
            st.gold, C_MID, None, st.cell)

    # -- totals -----------------------------------------------------------
    ws.row_dimensions[W_TOTAL_R].height = 20
    put(ws, "B%d" % W_TOTAL_R, "DAILY TOTAL", st.label, C_L)
    for d in range(7):
        col = CL(W_DAY_C0 + d)
        rng = "%s%d:%s%d" % (col, hab_lo, col, hab_hi)
        put(ws, "%s%d" % (col, W_TOTAL_R),
            '=IF(%s$%d>TODAY(),"",COUNTA(%s)-COUNTIF(%s,"✗"))'
            % (col, W_DATE_R, rng, rng),
            st.small, C_MID, st.panel)
    put(ws, "K%d" % W_TOTAL_R, "=SUM(K%d:K%d)" % (hab_lo, hab_hi),
        st.body_b, C_MID, st.panel)
    put(ws, "L%d" % W_TOTAL_R, "=SUM(L%d:L%d)" % (hab_lo, hab_hi),
        st.small, C_MID, st.panel)

    # -- score strip ------------------------------------------------------
    ws.row_dimensions[W_SCORE_R].height = 34
    put(ws, "B%d" % W_SCORE_R, "WEEK SCORE", st.label, C_L)
    ws.merge_cells("C%d:D%d" % (W_SCORE_R, W_SCORE_R))
    put(ws, "C%d" % W_SCORE_R,
        '=IF($%s$%d>TODAY(),"",IF(SUM($L$%d:$L$%d)=0,"",'
        'MIN(1,SUM($K$%d:$K$%d)/SUM($L$%d:$L$%d))))'
        % (d0, W_DATE_R, hab_lo, hab_hi, hab_lo, hab_hi, hab_lo, hab_hi),
        st.stat, C_L, None, None, "0%")
    put(ws, "F%d" % W_SCORE_R, "PERFECT DAYS", st.label, C_MID)
    put(ws, "H%d" % W_SCORE_R,
        '=IF(OR($%s$%d>TODAY(),%s=0),"",'
        'SUMPRODUCT(--($%s$%d:$%s$%d=%s)))'
        % (d0, W_DATE_R, active, d0, W_TOTAL_R, d6, W_TOTAL_R, active),
        st.stat_ink, C_MID)
    put(ws, "K%d" % W_SCORE_R, "TOP STREAK", st.label, C_MID)
    put(ws, "M%d" % W_SCORE_R,
        '=IF(COUNT($N$%d:$N$%d)=0,"",MAX($N$%d:$N$%d))'
        % (hab_lo, hab_hi, hab_lo, hab_hi), st.stat, C_MID)

    # -- free text --------------------------------------------------------
    for r, label, height in ((W_FOCUS_R, "FOCUS THIS WEEK", 22),
                             (W_NOTES_R, "NOTES", 46)):
        ws.row_dimensions[r].height = height
        put(ws, "B%d" % r, label, st.label, C_L)
        ws.merge_cells("C%d:N%d" % (r, r))
        put(ws, "C%d" % r, "", st.input, C_WRAP, st.panel, st.box)

    # -- data validation --------------------------------------------------
    dv = DataValidation(type="list", formula1='"✓,✗"', allow_blank=True,
                        showDropDown=False, showErrorMessage=False)
    ws.add_data_validation(dv)
    dv.add(grid)

    # -- conditional formatting -------------------------------------------
    # highest priority: a habit you never named leaves no trace at all
    for rng_ in ("B%d:B%d" % (hab_lo, hab_hi), grid,
                 "K%d:N%d" % (hab_lo, hab_hi)):
        ws.conditional_formatting.add(rng_, FormulaRule(
            formula=['$B%d=""' % hab_lo], stopIfTrue=True,
            fill=st.bg, border=st.erase))
    ws.conditional_formatting.add(grid, CellIsRule(
        operator="equal", formula=['"✗"'], stopIfTrue=True,
        fill=st.cf_miss, font=st.cf_miss_f))
    ws.conditional_formatting.add(grid, FormulaRule(
        formula=["LEN(%s%d)>0" % (d0, hab_lo)],
        fill=st.cf_done, font=st.cf_done_f))
    ws.conditional_formatting.add(
        "%s%d:%s%d" % (d0, W_DOW_R, d6, W_DATE_R),
        FormulaRule(formula=["%s$%d=TODAY()" % (d0, W_DATE_R)],
                    fill=st.cf_today, font=st.cf_today_f))
    ws.conditional_formatting.add(
        "M%d:M%d" % (hab_lo, hab_hi),
        CellIsRule(operator="equal", formula=['"✓"'],
                   fill=st.cf_done, font=st.cf_done_f))

    ws.freeze_panes = "C%d" % W_HAB_R0
    printable(ws, "A1:O%d" % (W_NOTES_R + 1))
    return ws


# ------------------------------------------------------ engine (hidden) ----
def build_engine(wb, st, t):
    """Flattens the 52 week grids into one 364-day column per habit, then
    walks a running streak down it. Every reference is literal, so this is
    a plain dependency chain - no INDIRECT, no volatility."""
    ws = wb.create_sheet(ENGINE)
    ws.sheet_view.showGridLines = False

    put(ws, "A1", "DATE", st.label)
    put(ws, "B1", "WEEK", st.label)
    put(ws, "C1", "DOW", st.label)
    for h in range(1, N_HABITS + 1):
        put(ws, "%s1" % CL(E_DONE_C0 + h - 1), "DONE%d" % h, st.label)
        put(ws, "%s1" % CL(E_STK_C0 + h - 1), "STREAK%d" % h, st.label)

    # seed row: lets row 3 look back one row without a special case
    put(ws, "A%d" % E_SEED_R, "='%s'!%s-1" % (SETUP, S_START_ABS), st.small)
    for h in range(1, N_HABITS + 1):
        put(ws, "%s%d" % (CL(E_DONE_C0 + h - 1), E_SEED_R), 0, st.small)
        put(ws, "%s%d" % (CL(E_STK_C0 + h - 1), E_SEED_R), 0, st.small)

    for i in range(1, N_DAYS + 1):
        r = E_R0 + i - 1
        w = (i - 1) // 7 + 1
        d = (i - 1) % 7
        off = i - 1
        ws.cell(row=r, column=1,
                value="='%s'!%s%s" % (SETUP, S_START_ABS,
                                      "+%d" % off if off else "")
                ).number_format = "yyyy-mm-dd"
        ws.cell(row=r, column=2, value=w)
        ws.cell(row=r, column=3, value=DOW[d])
        for h in range(1, N_HABITS + 1):
            src = "%s!%s%d" % (wk(w), CL(W_DAY_C0 + d), W_HAB_R0 + h - 1)
            ws.cell(row=r, column=E_DONE_C0 + h - 1,
                    value='=IF(AND(%s<>"",%s<>"✗"),1,0)' % (src, src))
            dc = CL(E_DONE_C0 + h - 1)
            sc = CL(E_STK_C0 + h - 1)
            ws.cell(row=r, column=E_STK_C0 + h - 1,
                    value="=IF(%s%d=1,%s%d+1,0)" % (dc, r, sc, r - 1))

    # helper block: one row per habit, read by Dashboard / Start Here
    for col, label in ((E_NAME_C, "HABIT"), (E_CUR_C, "CURRENT"),
                       (E_BEST_C, "BEST"), (E_TOT_C, "TOTAL"),
                       (E_TDY_C, "TODAY"), (E_NXT_C, "NEXTBADGE"),
                       (E_GAP_C, "TOGO")):
        put(ws, "%s1" % CL(col), label, st.label)
    for h in range(1, N_HABITS + 1):
        r = E_HELP_R0 + h - 1
        s_row = S_HAB_R0 + h - 1
        dc, sc = CL(E_DONE_C0 + h - 1), CL(E_STK_C0 + h - 1)
        put(ws, "%s%d" % (CL(E_NAME_C), r),
            "=IF('%s'!C%d=\"\",\"\",'%s'!C%d)" % (SETUP, s_row, SETUP, s_row),
            st.small)
        # streak as of today; falls back to yesterday so an unticked
        # "today" never looks like a broken streak
        put(ws, "%s%d" % (CL(E_CUR_C), r),
            "=MAX(IFERROR(LOOKUP(2,1/($A$%d:$A$%d<=TODAY()),%s$%d:%s$%d),0),"
            "IFERROR(LOOKUP(2,1/($A$%d:$A$%d<=TODAY()-1),%s$%d:%s$%d),0))"
            % (E_R0, E_RN, sc, E_R0, sc, E_RN,
               E_R0, E_RN, sc, E_R0, sc, E_RN), st.small)
        put(ws, "%s%d" % (CL(E_BEST_C), r),
            "=MAX(%s$%d:%s$%d)" % (sc, E_R0, sc, E_RN), st.small)
        put(ws, "%s%d" % (CL(E_TOT_C), r),
            "=SUM(%s$%d:%s$%d)" % (dc, E_R0, dc, E_RN), st.small)
        put(ws, "%s%d" % (CL(E_TDY_C), r),
            "=IFERROR(INDEX(%s$%d:%s$%d,MATCH(TODAY(),$A$%d:$A$%d,0)),0)"
            % (dc, E_R0, dc, E_RN, E_R0, E_RN), st.small)
        # the next badge you have not earned yet, and the run still needed
        bc = "%s%d" % (CL(E_BEST_C), r)
        nxt = '""'
        for thr in reversed([m[0] for m in MILESTONES]):
            nxt = 'IF(%s>=%d,%s,%d)' % (bc, thr, nxt, thr)
        put(ws, "%s%d" % (CL(E_NXT_C), r), "=" + nxt, st.small)
        put(ws, "%s%d" % (CL(E_GAP_C), r),
            '=IF(%s%d="","",MAX(0,%s%d-%s%d))'
            % (CL(E_NXT_C), r, CL(E_NXT_C), r, CL(E_CUR_C), r), st.small)

    ws.sheet_state = "hidden"
    return ws


# ----------------------------------------------------------- today page --
def build_today(wb, st, t):
    """The page the file opens on. Its whole job is to make one number
    impossible to ignore: the streak you are about to lose tonight."""
    ws = wb.create_sheet(TODAY)
    ws.sheet_view.showGridLines = False
    ws.sheet_properties.tabColor = t["tab"]
    paint(ws, 30, 10, st)

    for col, wd in zip("ABCDEFGH", [2, 34, 9, 9, 13, 22, 2, 2]):
        ws.column_dimensions[col].width = wd
    for r, hgt in ((3, 30), (7, 26), (9, 8), (11, 18)):
        ws.row_dimensions[r].height = hgt

    E = lambda col, h: "%s!$%s$%d" % (ENGINE, CL(col), E_HELP_R0 + h - 1)
    rng = lambda col: "%s!$%s$%d:$%s$%d" % (ENGINE, CL(col), E_HELP_R0,
                                            CL(col), E_HELP_R0 + N_HABITS - 1)
    named = 'SUMPRODUCT(--(%s<>""))' % rng(E_NAME_C)
    logged = 'SUMPRODUCT(--(%s<>""),--(%s=1))' % (rng(E_NAME_C), rng(E_TDY_C))
    at_risk = 'SUMPRODUCT(--(%s>0),--(%s=0))' % (rng(E_CUR_C), rng(E_TDY_C))

    put(ws, "B2", "MOMENTUM  ·  TODAY", st.brand, C_L)
    put(ws, "B3", '=UPPER(TEXT(TODAY(),"dddd"))', st.h1, C_L)
    put(ws, "E3", '=TEXT(TODAY(),"d mmmm yyyy")', st.body_b, C_L)
    week_now = ('MIN(%d,MAX(1,INT((TODAY()-\'%s\'!%s)/7)+1))'
                % (N_WEEKS, SETUP, S_START_ABS))
    put(ws, "B4",
        '=IF({named}=0,'
        '"Nothing is being tracked yet — open Start Here and name your '
        'habits.",'
        '"You are in week "&TEXT({week},"00")&" of 52.")'
        .format(named=named, week=week_now), st.muted, C_L)

    # the whole product in one sentence, rewritten every morning
    ws.merge_cells("B6:F6")
    put(ws, "B6",
        '=IF(%s=0,"",IF(%s=0,'
        '"Every live streak is already logged today. Nothing to lose '
        'tonight.",%s&IF(%s=1,'
        '" streak ends tonight unless you log it — ",'
        '" streaks end tonight unless you log them — ")'
        '&TEXT(TODAY(),"d mmm")&"."))'
        % (named, at_risk, at_risk, at_risk), st.h2, C_L)
    ws.merge_cells("B7:F7")
    put(ws, "B7",
        '=IF(%s=0,"",TEXT(%s,"0")&" of "&TEXT(%s,"0")&" habits logged today.")'
        % (named, logged, named), st.muted, C_L)
    for col in "BCDEF":
        ws["%s6" % col].fill = st.accent_sf
        ws["%s7" % col].fill = st.accent_sf

    heads = (("B", "HABIT", C_L), ("C", "TODAY", C_MID),
             ("D", "STREAK", C_MID), ("E", "STATUS", C_MID),
             ("F", "NEXT BADGE", C_L))
    for col, label, al in heads:
        put(ws, "%s11" % col, label, st.label, al, None, st.under_soft)

    lo = 12
    for h in range(1, N_HABITS + 1):
        r = lo + h - 1
        ws.row_dimensions[r].height = 22
        s_row = S_HAB_R0 + h - 1
        put(ws, "B%d" % r,
            "=IF('%s'!C%d=\"\",\"\",'%s'!C%d)" % (SETUP, s_row, SETUP, s_row),
            st.body, C_L, None, st.under_soft)
        put(ws, "C%d" % r,
            '=IF($B%d="","",IF(%s=1,"✓","—"))' % (r, E(E_TDY_C, h)),
            st.mark, C_MID, None, st.under_soft)
        put(ws, "D%d" % r,
            '=IF($B%d="","",%s)' % (r, E(E_CUR_C, h)),
            st.accent, C_MID, None, st.under_soft)
        put(ws, "E%d" % r,
            '=IF($B%d="","",IF(%s=1,"logged",IF(%s>0,"AT RISK","not yet")))'
            % (r, E(E_TDY_C, h), E(E_CUR_C, h)),
            st.small, C_MID, None, st.under_soft)
        put(ws, "F%d" % r,
            '=IF($B%d="","",IF(%s="","every badge earned",'
            'TEXT(%s,"0")&"-day badge in "&TEXT(%s,"0")&" days"))'
            % (r, E(E_NXT_C, h), E(E_NXT_C, h), E(E_GAP_C, h)),
            st.small, C_L, None, st.under_soft)

    hi = lo + N_HABITS - 1
    ws.conditional_formatting.add("B%d:F%d" % (lo, hi), FormulaRule(
        formula=['$B%d=""' % lo], stopIfTrue=True,
        fill=st.bg, border=st.erase))
    ws.conditional_formatting.add("E%d:E%d" % (lo, hi), CellIsRule(
        operator="equal", formula=['"AT RISK"'], stopIfTrue=True,
        fill=st.cf_miss, font=st.cf_miss_f))
    ws.conditional_formatting.add("E%d:E%d" % (lo, hi), CellIsRule(
        operator="equal", formula=['"logged"'],
        fill=st.cf_done, font=st.cf_done_f))
    ws.conditional_formatting.add("C%d:C%d" % (lo, hi), CellIsRule(
        operator="equal", formula=['"✓"'],
        fill=st.cf_done, font=st.cf_done_f))

    r = hi + 2
    put(ws, "B%d" % r, "Ticking happens in the week tabs:", st.muted, C_L)
    ws.merge_cells("C%d:D%d" % (r, r))
    link(ws, "C%d" % r, DASH, "◆ DASHBOARD", st.link)
    for col in "CD":
        ws["%s%d" % (col, r)].fill = st.chip
        ws["%s%d" % (col, r)].border = st.box
    link(ws, "E%d" % r, SETUP, "◆ START HERE", st.link)
    ws["E%d" % r].fill = st.chip
    ws["E%d" % r].border = st.box
    put(ws, "B%d" % (r + 2),
        "The Dashboard highlights the week you are in — two taps to today.",
        st.small, C_L)

    printable(ws, "A1:G%d" % (r + 3))
    return ws


# ------------------------------------------------------------- dashboard --
def build_dash(wb, st, t):
    ws = wb.create_sheet(DASH)
    ws.sheet_view.showGridLines = False
    ws.sheet_properties.tabColor = t["tab"]
    paint(ws, 46, 21, st)

    ws.column_dimensions["A"].width = 2
    ws.column_dimensions["B"].width = 2
    for c in range(D_C0, D_CN + 1):
        ws.column_dimensions[CL(c)].width = 6.2
    ws.column_dimensions["T"].width = 2
    for r, hgt in ((3, 34), (7, 32), (12, 18)):
        ws.row_dimensions[r].height = hgt

    put(ws, "C2", "MOMENTUM  ·  WEEKLY HABIT SYSTEM", st.brand, C_L)
    ws.merge_cells("C3:J3")
    put(ws, "C3", "DASHBOARD", st.h1, C_L)
    ws.merge_cells("C4:L4")
    put(ws, "C4", "Everything on this page fills itself in. "
                  "You only ever tick boxes in the week tabs.", st.muted, C_L)
    ws.merge_cells("P3:S3")
    link(ws, "P3", SETUP, "◆  START HERE", st.link)
    ws["P3"].fill = st.chip
    ws["P3"].border = st.box
    ws.merge_cells("P4:S4")
    link(ws, "P4", wk(1), "▶  WEEK 01", st.link)
    ws["P4"].fill = st.chip
    ws["P4"].border = st.box

    # -- stat cards -------------------------------------------------------
    eng = lambda col: "%s!$%s$%d:$%s$%d" % (ENGINE, CL(col), E_HELP_R0,
                                            CL(col), E_HELP_R0 + N_HABITS - 1)
    cards = [
        ("C", "F", "TOTAL CHECK-INS", "=SUM(%s)" % eng(E_TOT_C),
         "days ticked since day one", "0", st.stat_ink),
        ("G", "J", "BEST STREAK", "=MAX(%s)" % eng(E_BEST_C),
         "your longest unbroken run", "0", st.stat),
        ("K", "N", "STREAKS ALIVE", "=SUMPRODUCT(--(%s>0))" % eng(E_CUR_C),
         "habits still running today", "0", st.stat),
        ("O", "R", "YEAR PROGRESS",
         "=IFERROR(MAX(0,MIN(1,(TODAY()-'%s'!%s+1)/%d)),\"\")"
         % (SETUP, S_START_ABS, N_DAYS),
         "of your 52 weeks", "0%", st.stat_ink),
    ]
    for c0, c1, label, formula, sub, fmt, font in cards:
        for r, val, fnt, al, f in ((6, label, st.label, C_MID, st.panel),
                                   (7, formula, font, C_MID, st.panel),
                                   (8, sub, st.small, C_MID, st.panel)):
            ws.merge_cells("%s%d:%s%d" % (c0, r, c1, r))
            cell = put(ws, "%s%d" % (c0, r), val, fnt, al, f, None,
                       fmt if r == 7 else None)
        for r in (6, 7, 8):
            for c in range(ws[c0 + "1"].column, ws[c1 + "1"].column + 1):
                ws.cell(row=r, column=c).border = st.box

    # -- habit table ------------------------------------------------------
    ws.merge_cells("C11:H11")
    put(ws, "C11", "YOUR HABITS", st.h2, C_L)
    ws.merge_cells("O11:R11")
    put(ws, "O11", "MILESTONES  (best streak)", st.label, C_MID)

    heads = [("C", "H", "HABIT", C_L), ("I", "J", "DONE", C_MID),
             ("K", "L", "CURRENT", C_MID), ("M", "N", "BEST", C_MID)]
    for c0, c1, label, al in heads:
        ws.merge_cells("%s12:%s12" % (c0, c1))
        put(ws, "%s12" % c0, label, st.label, al, None, st.under_soft)
    for i, (thr, lab) in enumerate(MILESTONES):
        put(ws, "%s12" % CL(15 + i), lab, st.label, C_MID, None, st.under_soft)

    for h in range(1, N_HABITS + 1):
        r = D_HAB_R0 + h - 1
        er = E_HELP_R0 + h - 1
        s_row = S_HAB_R0 + h - 1
        ws.row_dimensions[r].height = 21
        ws.merge_cells("C%d:H%d" % (r, r))
        put(ws, "C%d" % r,
            "=IF('%s'!C%d=\"\",\"\",'%s'!C%d)" % (SETUP, s_row, SETUP, s_row),
            st.body, C_L, None, st.under_soft)
        for c0, c1, col, fnt in (("I", "J", E_TOT_C, st.body),
                                 ("K", "L", E_CUR_C, st.accent),
                                 ("M", "N", E_BEST_C, st.gold)):
            ws.merge_cells("%s%d:%s%d" % (c0, r, c1, r))
            put(ws, "%s%d" % (c0, r),
                '=IF($C%d="","",%s!$%s$%d)' % (r, ENGINE, CL(col), er),
                fnt, C_MID, None, st.under_soft)
        for i, (thr, lab) in enumerate(MILESTONES):
            put(ws, "%s%d" % (CL(15 + i), r),
                '=IF($C%d="","",IF(%s!$%s$%d>=%d,"✔","·"))'
                % (r, ENGINE, CL(E_BEST_C), er, thr),
                st.muted, C_MID, None, st.under_soft)

    ws.conditional_formatting.add(
        "C%d:R%d" % (D_HAB_R0, D_HAB_R0 + N_HABITS - 1),
        FormulaRule(formula=['$C%d=""' % D_HAB_R0], stopIfTrue=True,
                    fill=st.bg, border=st.erase))
    ws.conditional_formatting.add(
        "O%d:R%d" % (D_HAB_R0, D_HAB_R0 + N_HABITS - 1),
        CellIsRule(operator="equal", formula=['"✔"'],
                   fill=st.cf_gold, font=st.cf_gold_f))
    ws.conditional_formatting.add(
        "K%d:L%d" % (D_HAB_R0, D_HAB_R0 + N_HABITS - 1),
        CellIsRule(operator="greaterThanOrEqual", formula=["1"],
                   fill=st.accent_sf, font=st.cf_done_f))

    # -- 52 week index ----------------------------------------------------
    ws.merge_cells("C%d:J%d" % (D_IDX_R0 - 4, D_IDX_R0 - 4))
    put(ws, "C%d" % (D_IDX_R0 - 4), "THE YEAR AT A GLANCE", st.h2, C_L)
    ws.merge_cells("C%d:R%d" % (D_IDX_R0 - 3, D_IDX_R0 - 3))
    put(ws, "C%d" % (D_IDX_R0 - 3),
        "Click a week to jump straight to it. The week you are in is "
        "highlighted; the number underneath is that week's score against "
        "your goals.", st.muted, C_L)

    goal_sum = "SUM('%s'!$E$%d:$E$%d)" % (SETUP, S_HAB_R0,
                                          S_HAB_R0 + N_HABITS - 1)
    d0, d6 = CL(W_DAY_C0), CL(W_DAY_C0 + 6)
    for n in range(1, N_WEEKS + 1):
        b, idx = (n - 1) // 13, (n - 1) % 13
        r_lab = D_IDX_R0 + b * 4
        col = CL(D_C0 + idx)
        link(ws, "%s%d" % (col, r_lab), wk(n), "%02d" % n, st.idx)
        ws["%s%d" % (col, r_lab)].fill = st.chip
        rng = "%s!$%s$%d:$%s$%d" % (wk(n), d0, W_HAB_R0, d6,
                                    W_HAB_R0 + N_HABITS - 1)
        put(ws, "%s%d" % (col, r_lab + 1),
            '=IF(OR(%s!$%s$%d>TODAY(),%s=0),"",'
            'MIN(1,(COUNTA(%s)-COUNTIF(%s,"✗"))/%s))'
            % (wk(n), d0, W_DATE_R, goal_sum, rng, rng, goal_sum),
            st.small, C_MID, None, st.cell, "0%")
        # invisible helper: this week's Monday, so one relative CF rule per
        # block can find "the week you are in" instead of 52 separate rules
        put(ws, "%s%d" % (col, r_lab + 2),
            "=%s!$%s$%d" % (wk(n), d0, W_DATE_R), st.hidden, C_MID)

    for b in range(4):
        r_lab = D_IDX_R0 + b * 4
        ws.row_dimensions[r_lab].height = 17
        ws.row_dimensions[r_lab + 1].height = 15
        ws.row_dimensions[r_lab + 2].height = 3
        ws.conditional_formatting.add(
            "C%d:O%d" % (r_lab, r_lab),
            FormulaRule(formula=["AND(C%d<=TODAY(),C%d+6>=TODAY())"
                                 % (r_lab + 2, r_lab + 2)],
                        fill=st.cf_chip_now, font=st.cf_week_now))
        ws.conditional_formatting.add(
            "C%d:O%d" % (r_lab + 1, r_lab + 1),
            ColorScaleRule(start_type="num", start_value=0,
                           start_color=t["scale_lo"],
                           mid_type="num", mid_value=0.5,
                           mid_color=t["scale_mid"],
                           end_type="num", end_value=1,
                           end_color=t["scale_hi"]))

    put(ws, "C%d" % (D_IDX_R0 + 17),
        "Miss a day and the streak resets. That is the point — "
        "it is the only rule the system has.", st.small, C_L)
    printable(ws, "A1:T47")
    return ws


# ------------------------------------------------------------------ main --
def build_workbook(t, out_path):
    st = S(t)
    wb = Workbook()
    wb.remove(wb.active)

    # apps apply their own built-in Hyperlink style over the cell font, and
    # they find it by builtinId (8 / 9), not by name - so claim those ids.
    for nm, bid in (("Hyperlink", 8), ("Followed Hyperlink", 9)):
        wb.add_named_style(NamedStyle(name=nm, builtinId=bid, font=Font(
            name="Calibri", size=10, bold=True, color=t["accent"],
            underline="single")))
    # empty cells inherit "Normal", so this is what makes the dark theme
    # dark everywhere instead of only where we painted
    for ns in wb._named_styles:
        if ns.name == "Normal":
            ns.fill = PatternFill("solid", fgColor=t["bg"])
            ns.font = Font(name="Calibri", size=11, color=t["ink"])

    build_today(wb, st, t)
    build_setup(wb, st, t)
    build_dash(wb, st, t)
    for w in range(1, N_WEEKS + 1):
        build_week(wb, st, t, w)
    build_engine(wb, st, t)

    wb.active = wb.sheetnames.index(TODAY)
    wb.properties.title = "Momentum - Weekly Habit System (%s)" % t["key"]
    wb.properties.creator = "Momentum"
    wb.properties.description = (
        "52-week habit tracker with an automatic streak engine. "
        "Works in Microsoft Excel and Google Sheets. No macros.")
    wb.save(out_path)
    return out_path


def main():
    here = os.path.dirname(os.path.abspath(__file__))
    dist = os.path.join(os.path.dirname(here), "dist")
    os.makedirs(dist, exist_ok=True)
    for t in THEMES:
        out = os.path.join(dist, "Momentum-Habit-System-%s.xlsx" % t["key"])
        build_workbook(t, out)
        print("  %-46s %7.1f KB"
              % (os.path.basename(out), os.path.getsize(out) / 1024))


if __name__ == "__main__":
    main()
