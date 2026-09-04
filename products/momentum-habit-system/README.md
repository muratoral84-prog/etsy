# Momentum — Weekly Habit System

A 52-week habit tracker sold on Etsy as a digital download. One `.xlsx`
workbook (in two colour themes) that counts consecutive-day streaks
automatically, plus the buyer guide and the listing pack.

Everything in `dist/` and `etsy/mockups/` is generated. Do not hand-edit it —
edit the generators and re-run `build/build_all.sh`.

```
build/          generators and the test suite
dist/           the three files the buyer downloads
etsy/           listing copy + the 8 listing images
```

## Build

```bash
build/build_all.sh
```

Requires `openpyxl`, `reportlab`, `Pillow`, `pymupdf` and `libreoffice-calc`
(LibreOffice is what actually evaluates the formulas during verification).

| script | what it does |
|---|---|
| `build.py` | writes both workbooks |
| `guide.py` | writes the 3-page buyer PDF |
| `demo.py` | fills a workbook with a plausible year-in-progress |
| `verify.py` | the test suite — see below |
| `mockups.py` | renders the 8 Etsy listing images |
| `check_listing.py` | asserts the listing copy fits Etsy's field limits |

## How the streak engine works

The hard part of a formula-only habit tracker is a streak that survives the
jump from one week tab to the next. The approach here:

1. A hidden `Engine` sheet flattens the 52 weekly grids into one column of
   364 days per habit. Every reference is written out literally at build
   time (`=IF(AND(W07!E11<>"",W07!E11<>"✗"),1,0)`) — **no `INDIRECT`**, so
   nothing is volatile and recalculation is instant.
2. Next to it, a running streak walks down that column:
   `=IF(D125=1,O124+1,0)`. A seed row of zeros above the first day means
   day one needs no special case.
3. A helper block reads out current streak, best streak, total and
   done-today per habit. Everything user-facing reads from that block, so
   the Today page, the Dashboard and each week tab can never disagree.

Deliberate constraints, because the file has to open in Excel **and** Google
Sheets: no macros, no `SPARKLINE`/`QUERY`/`ARRAYFORMULA`, no conditional
formatting rule that Sheets drops on import.

## Design decisions worth remembering

**The file opens on `Today`, not on the Dashboard.** A tracker fails at the
moment of daily friction, not at the moment of setup. `Today` states in one
sentence which streaks die tonight, which is the only thing that reliably
gets a file opened on day 40.

**An unticked today does not break your streak.** Current streak is
`MAX(streak as of today, streak as of yesterday)`. Without this the number
would read 0 every morning and the whole mechanic would feel broken.

**Badges come off *best* streak, not current.** A badge you have earned can
never be taken away by one bad week. Punishing a lapse twice is how people
quit.

**Every hyperlink cell sits on a light "chip" background.** Excel, Sheets and
LibreOffice each force their own hyperlink colour over the cell font — a
named `Hyperlink` style with `builtinId=8` does *not* reliably override it
(tested). The background is the only thing we control, so the dark theme's
navigation stays readable whatever the app does.

**Percentages are capped with `MIN(1, …)`.** Beating your weekly goal used to
print "118%", which reads as a bug and broke the heat-map colour scale.

**Unnamed habits leave no trace.** A conditional-format rule keyed on a blank
habit name paints the row's fill and borders in the canvas colour, so the
default file does not look like a half-finished grid.

## Verification

`verify.py` is not a smoke test. It writes a known tick pattern into a
generated workbook, has LibreOffice perform the real recalculation, then
asserts the numbers that come back against streaks computed independently in
plain Python:

- five habits with hand-built patterns (a mid-run gap, an explicit `✗`, a
  100-day run, a live streak, a streak that died two days ago)
- every milestone badge, and all four Dashboard stat cards
- the current week's `STREAK` column must equal the Dashboard's number
  (they disagreed once — that is what this test exists for)
- the Today page's streak and status for every habit
- no cell anywhere may contain a formula error
- no score may read above 100%
- weeks that have not started must be blank, not `0%`
- the filenames promised in the listing copy must exist in `dist/`

Both themes must pass. `build_all.sh` exits non-zero if either does not.
