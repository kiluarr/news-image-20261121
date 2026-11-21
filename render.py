# render.py — draws the entry image for news-image-20261121.
# "THE WORLD IN ONE DAY — Saturday 21 November 2026": a newspaper front
# page with 38 verified stories from six continents, 8 illustrated panels,
# a world map with 12 numbered pins, a day-in-figures strip and a markets
# line. Every story below happened, or was first reported, on Saturday
# 21 November 2026 (sources: oneturn.news day page, CNN, Reuters/AP,
# Investors.com, Speedcafe, Jagran Josh, Aju Press — see STORIES.md).
# Deterministic: fixed fonts, fixed data, no timestamps, no randomness.
# Run: python3 render.py  -> writes entry.png (1024x1024) beside this file.

import math
import os

from PIL import Image, ImageDraw, ImageFont

HERE = os.path.dirname(os.path.abspath(__file__))
W, H = 1024, 1024

PAPER = (247, 243, 232)
INK = (18, 22, 30)
NAVY = (14, 42, 71)
NAVY2 = (20, 58, 96)
RED = (178, 34, 34)
GOLD = (176, 141, 58)
GREY = (90, 92, 96)
FAINT = (226, 220, 205)
SEA = (205, 224, 232)
LAND = (196, 182, 148)
EDGE = (120, 108, 82)
TEAL = (14, 110, 110)
GREEN = (34, 110, 60)
BODY = (50, 52, 56)


# ---------- fonts ----------
_FONT_PATHS = {
    "serif_b": ["DejaVuSerif-Bold", "LiberationSerif-Bold"],
    "serif": ["DejaVuSerif", "LiberationSerif-Regular"],
    "sans": ["DejaVuSans", "LiberationSans-Regular"],
    "sans_b": ["DejaVuSans-Bold", "LiberationSans-Bold"],
}


def _find_font_file(name):
    for stem in _FONT_PATHS[name]:
        for base in ("/usr/share/fonts/truetype/dejavu",
                     "/usr/share/fonts/truetype/liberation"):
            cand = os.path.join(base, stem + ".ttf")
            if os.path.exists(cand):
                return cand
    raise FileNotFoundError("no font file for " + name)


_FONTS = {}


def font(name, size):
    key = (name, int(size))
    if key not in _FONTS:
        _FONTS[key] = ImageFont.truetype(_find_font_file(name), int(size))
    return _FONTS[key]


# ---------- text helpers ----------
def wrap_text(draw, text, fnt, width):
    words = text.split()
    lines, cur = [], ""
    for word in words:
        trial = (cur + " " + word).strip()
        if draw.textlength(trial, font=fnt) <= width:
            cur = trial
        else:
            if cur:
                lines.append(cur)
            cur = word
    if cur:
        lines.append(cur)
    return lines


def draw_lines(draw, x, y, text, fnt, width, fill, leading=None):
    step = leading if leading is not None else fnt.size + 2
    for line in wrap_text(draw, text, fnt, width):
        draw.text((x, y), line, font=fnt, fill=fill)
        y += step
    return y


def shrink_to_fit(draw, text, name, start_size, width, floor=10):
    size = start_size
    fnt = font(name, size)
    while size > floor and draw.textlength(text, font=fnt) > width:
        size -= 1
        fnt = font(name, size)
    return fnt


# ---------- the day's stories ----------
# Each story: region, accent colour, headline, one-line deck.
# "pictured" marks the 8 stories that also get a drawn panel.
STORIES = [
    # --- pictured (8) ---
    {"region": "EUROPE", "color": NAVY2,
     "head": "Russia's biggest barrage hits Kyiv bridges",
     "deck": "400+ drones, 110+ missiles overnight; 8 killed, power cut.",
     "pictured": True},
    {"region": "EUROPE", "color": NAVY2,
     "head": "Russian missiles land in Poland",
     "deck": "Tusk calls it a deliberate provocation; NATO jets scrambled.",
     "pictured": True},
    {"region": "WORLD", "color": GREY,
     "head": "Trump defends Putin and Xi after summit",
     "deck": "Calls Putin a friend; Zelensky answers: \u201cHe's a killer.\u201d",
     "pictured": True},
    {"region": "WORLD", "color": GREY,
     "head": "World Court: Myanmar committed genocide",
     "deck": "First state found responsible; return and reparations ordered.",
     "pictured": True},
    {"region": "AMERICAS", "color": GREEN,
     "head": "AI rout: Nasdaq dives 5.3%",
     "deck": "S&P -3.7% into correction; Nvidia -14%, Anthropic -9%.",
     "pictured": True},
    {"region": "MIDDLE EAST", "color": RED,
     "head": "Houthi missiles aimed at Riyadh shot down",
     "deck": "Coalition intercepts three; third night of alerts.",
     "pictured": True},
    {"region": "SPACE", "color": NAVY2,
     "head": "BepiColombo reaches Mercury orbit",
     "deck": "After eight years and 10bn km, only the second to orbit.",
     "pictured": True},
    {"region": "SPORT", "color": GREEN,
     "head": "Russell tops dry Las Vegas FP3",
     "deck": "Fastest in final practice; contact with Verstappen at Turn 14.",
     "pictured": True},
    # --- columns (22) ---
    {"region": "MIDDLE EAST", "color": RED,
     "head": "Israeli strikes kill six in Gaza",
     "deck": "Despite the ceasefire; 1,600+ killed since the truce began."},
    {"region": "MIDDLE EAST", "color": RED,
     "head": "Hormuz attacks go on as talks stall",
     "deck": "Iran says it downed a US MQ-9 drone; US sanctions four trustees."},
    {"region": "MIDDLE EAST", "color": RED,
     "head": "Oil set for third weekly fall",
     "deck": "Brent settles $92.57; Hormuz flows back near pre-war levels."},
    {"region": "EUROPE", "color": NAVY2,
     "head": "UK and EU sign biggest post-Brexit deals",
     "deck": "Food, carbon, youth mobility; Burnham sees +0.5% growth a year."},
    {"region": "EUROPE", "color": NAVY2,
     "head": "Estonia to shut Russia border crossings",
     "deck": "Five crossings close from 1 December after an arson attempt."},
    {"region": "EUROPE", "color": NAVY2,
     "head": "Denmark expels Russian diplomat",
     "deck": "Alleged plot to kill a US-Ukrainian rapper; two arrested."},
    {"region": "EUROPE", "color": NAVY2,
     "head": "Gen Z protests sweep 25 countries",
     "deck": "Students march on living costs, rearmament and climate."},
    {"region": "ASIA-PACIFIC", "color": TEAL,
     "head": "Cyclone Akvan crosses Odisha coast",
     "deck": "Strong winds and heavy rain near Gopalpur."},
    {"region": "ASIA-PACIFIC", "color": TEAL,
     "head": "Korea raised at Shenzhen summit",
     "deck": "Trump: North Korea discussed; joint vow to cut nuclear risks."},
    {"region": "AMERICAS", "color": GREEN,
     "head": "GTA VI earns $3.8bn on day one",
     "deck": "Beats every game launch and film box-office record."},
    {"region": "AMERICAS", "color": GREEN,
     "head": "Palisades fire arson verdict",
     "deck": "Jury convicts Rinderknecht; fire killed 12, razed 6,800 homes."},
    {"region": "AMERICAS", "color": GREEN,
     "head": "Mamdani: close Rikers by 2032",
     "deck": "New York mayor sets out plan; the 2027 law must change."},
    {"region": "AMERICAS", "color": GREEN,
     "head": "US loses measles elimination status",
     "deck": "7,700 cases and 13 deaths since the start of last year."},
    {"region": "AMERICAS", "color": GREEN,
     "head": "Trump threatens tax on AI data centres abroad",
     "deck": "US firms building overseas face a \u201ctremendous tax\u201d."},
    {"region": "AMERICAS", "color": GREEN,
     "head": "Trump wants ousted Nvidia chief back",
     "deck": "Urges Huang's return; board says it has no such plans."},
    {"region": "AFRICA", "color": GOLD,
     "head": "Nigeria boat capsizes, 30 feared dead",
     "deck": "Funeral mourners aboard; at least 4 dead, ~300 missing."},
    {"region": "AFRICA", "color": GOLD,
     "head": "Tanzania's Lissu convicted of sedition",
     "deck": "Opposition leader calls it political; UK voices concern."},
    {"region": "AFRICA", "color": GOLD,
     "head": "Uganda curbs gatherings over Ebola",
     "deck": "Limits in 34 districts bordering DR Congo."},
    {"region": "WORLD", "color": GREY,
     "head": "COP31 runs past deadline",
     "deck": "Draft has no fossil-fuel mention; EU warns of a fossil summit."},
    {"region": "WORLD", "color": GREY,
     "head": "Riemann proof claimed with AI help",
     "deck": "Anthropic mathematician's claim; verification will take time."},
    {"region": "WORLD", "color": GREY,
     "head": "Cancer pill hailed as breakthrough",
     "deck": "Daraxonrasib trial: tumours undetectable in 1 in 12 patients."},
    {"region": "WORLD", "color": GREY,
     "head": "Voyager 1 now 24 light-hours away",
     "deck": "16.1bn miles out; light takes a full day to reach it."},
]

# --- briefs (8) ---
BRIEFS = [
    ("Peru quake 6.7 shakes Andes",
     "Residents flee in Lima; no casualties at first."),
    ("Iraq retakes militia stronghold",
     "Forces enter Jurf al-Sakhar, first time in 12 years."),
    ("Haiti: 2 Salvadoran troops killed",
     "Killed handling explosives in Port-au-Prince."),
    ("Gupta gets 19 years in US plot",
     "Sentenced over plot to kill Sikh leader Pannun."),
    ("Bayer Roundup deal: $7.25bn",
     "Judge approves; Bayer admits no fault."),
    ("Bolsonaro in hospital",
     "Intestinal obstruction; under house arrest."),
    ("Alcaraz stays unbeaten in Turin",
     "Beats Cobolli at the ATP Finals."),
    ("India fight back in Wellington",
     "Jaiswal 85; India 159/1, trailing by 209 runs."),
]

# --- figures (4) ---
FIGURES = [
    ("400+", "drones fired at Ukraine overnight"),
    ("110+", "missiles in the barrage, 27 ballistic"),
    ("-5.3%", "Nasdaq's Friday fall, gains erased"),
    ("$3.8bn", "GTA VI first-day sales record"),
]

# (number, lon, lat, label)
PINS = [
    (1, 30.5, 50.4, "Kyiv"),
    (2, 21.8, 50.4, "Nowa Deba"),
    (3, 114.1, 22.5, "Shenzhen"),
    (4, 34.5, 31.5, "Gaza"),
    (5, 46.7, 24.7, "Riyadh"),
    (6, 56.5, 26.5, "Hormuz"),
    (7, 4.3, 52.1, "The Hague"),
    (8, -77.0, 38.9, "Washington"),
    (9, -74.0, 40.7, "New York"),
    (10, 84.9, 19.3, "Gopalpur"),
    (11, -77.0, -12.0, "Lima"),
    (12, 6.3, 4.9, "Bayelsa"),
]

# Simplified continent outlines, (lon, lat) points, equirectangular.
CONTINENTS = {
    "NA": [(-168, 66), (-150, 70), (-130, 71), (-115, 72), (-100, 73),
           (-85, 70), (-75, 72), (-65, 60), (-55, 47), (-65, 44),
           (-70, 40), (-76, 35), (-81, 31), (-84, 30), (-90, 21),
           (-97, 16), (-105, 20), (-112, 24), (-117, 33), (-125, 40),
           (-124, 48), (-135, 58), (-155, 58), (-165, 60)],
    "SA": [(-79, 9), (-77, 4), (-80, -3), (-81, -6), (-77, -12),
           (-72, -18), (-70, -23), (-70, -33), (-66, -40), (-68, -52),
           (-65, -55), (-60, -48), (-57, -38), (-52, -32), (-48, -27),
           (-41, -22), (-39, -17), (-35, -9), (-35, -6), (-42, -3),
           (-50, 0), (-53, 4), (-60, 8), (-70, 11)],
    "AF": [(-17, 15), (-16, 21), (-10, 31), (-6, 35), (0, 36), (10, 37),
           (20, 32), (30, 31), (33, 28), (36, 27), (39, 21), (41, 15),
           (43, 12), (48, 11), (51, 12), (44, 5), (41, 0), (38, -8),
           (35, -15), (32, -25), (28, -33), (20, -35), (17, -32),
           (14, -22), (13, -12), (12, -6), (9, 0), (4, 6), (-8, 5),
           (-13, 8)],
    "EU": [(-10, 36), (-9, 43), (-2, 48), (-4, 50), (-1, 51), (3, 53),
           (7, 54), (8, 57), (11, 58), (13, 56), (18, 56), (21, 55),
           (24, 59), (26, 60), (30, 62), (24, 65), (20, 70), (14, 68),
           (10, 63), (5, 58), (3, 54), (-2, 50), (-6, 44), (-9, 38)],
    "AS": [(30, 60), (35, 66), (45, 68), (55, 69), (65, 70), (75, 72),
           (85, 74), (95, 76), (105, 77), (115, 73), (125, 72),
           (135, 71), (145, 72), (155, 69), (162, 64), (160, 58),
           (155, 55), (150, 60), (142, 53), (140, 47), (135, 43),
           (130, 40), (127, 38), (122, 32), (120, 27), (115, 23),
           (110, 20), (106, 10), (101, 7), (97, 12), (92, 20), (88, 22),
           (84, 19), (80, 14), (77, 8), (75, 12), (73, 19), (68, 23),
           (62, 25), (57, 26), (53, 27), (50, 30), (48, 29), (44, 29),
           (40, 31), (36, 36), (33, 37), (30, 40), (28, 45), (30, 50),
           (30, 55)],
    "OC": [(113, -22), (114, -30), (115, -35), (120, -34), (124, -33),
           (129, -32), (134, -33), (138, -35), (142, -38), (147, -39),
           (150, -37), (153, -32), (153, -27), (150, -22), (146, -19),
           (142, -15), (140, -17), (136, -15), (132, -12), (128, -14),
           (124, -15), (120, -19), (116, -21)],
}

PIN_NUDGE = {1: (20, -20), 2: (-20, 6), 3: (-20, 14), 4: (-26, 2),
             5: (16, 16), 6: (16, 12), 7: (-26, -16), 8: (14, 2),
             9: (16, -16), 10: (16, 14), 11: (-16, 6), 12: (-16, 8)}


# ---------- map ----------
def draw_map(draw, x0, y0, w, h):
    draw.rectangle([x0, y0, x0 + w, y0 + h], fill=SEA, outline=EDGE, width=1)
    for gx in range(-150, 181, 30):
        px = x0 + (gx + 180) / 360.0 * w
        draw.line([(px, y0), (px, y0 + h)], fill=(185, 208, 220), width=1)
    for gy in range(-60, 86, 30):
        py = y0 + (85 - gy) / 145.0 * h
        draw.line([(x0, py), (x0 + w, py)], fill=(185, 208, 220), width=1)

    def proj(lon, lat):
        return (x0 + (lon + 180) / 360.0 * w,
                y0 + (85 - lat) / 145.0 * h)

    for pts in CONTINENTS.values():
        xy = [proj(lon, lat) for lon, lat in pts]
        draw.polygon(xy, fill=LAND, outline=EDGE)
    num_f = font("sans_b", 9)
    for num, lon, lat, _label in PINS:
        cx, cy = proj(lon, lat)
        dx, dy = PIN_NUDGE.get(num, (0, 0))
        px, py = cx + dx, cy + dy
        if (dx, dy) != (0, 0):
            draw.line([(cx, cy), (px, py)], fill=RED, width=1)
        draw.ellipse([px - 7, py - 7, px + 7, py + 7], fill=RED,
                     outline=(255, 255, 255), width=1)
        tw = draw.textlength(str(num), font=num_f)
        draw.text((px - tw / 2, py - 6), str(num), font=num_f,
                  fill=(255, 255, 255))


def draw_pin_key(draw, x0, y0, w):
    fnt = font("sans", 10)
    col_w = w // 3
    for i, (num, _lon, _lat, label) in enumerate(PINS):
        cx = x0 + (i % 3) * col_w
        cy = y0 + (i // 3) * 12
        draw.text((cx, cy), "%d %s" % (num, label), font=fnt, fill=INK)


# ---------- story blocks ----------
def story_block_height(draw, story, width):
    head_f = shrink_to_fit(draw, story["head"], "serif_b", 12, width)
    h = 11  # kicker
    h += len(wrap_text(draw, story["head"], head_f, width)) * 13
    h += 1 + len(wrap_text(draw, story["deck"], font("sans", 9), width)) * 11
    return h + 4


def draw_story(draw, x, y, story, width):
    draw.text((x, y), story["region"], font=font("sans_b", 9),
              fill=story["color"])
    y += 11
    head_f = shrink_to_fit(draw, story["head"], "serif_b", 12, width)
    y = draw_lines(draw, x, y, story["head"], head_f, width, INK, leading=13)
    y = draw_lines(draw, x, y + 1, story["deck"], font("sans", 9), width,
                   BODY, leading=11)
    return y + 4


# ---------- picture panels: 8 flat pictograms ----------
def _burst(d, cx, cy, r, fill):
    pts = []
    for i in range(12):
        ang = i * math.pi / 6
        rr = r if i % 2 == 0 else r * 0.45
        pts.append((cx + rr * math.cos(ang), cy + rr * math.sin(ang)))
    d.polygon(pts, fill=fill)


def panel_kyiv(d, x, y, w, h):
    # night river, three bridge spans, middle span down, smoke
    d.rectangle([x, y, x + w, y + h], fill=(28, 42, 66))
    d.rectangle([x, y + h * 0.66, x + w, y + h], fill=(64, 98, 132))
    d.rectangle([x, y + h * 0.46, x + w * 0.36, y + h * 0.53], fill=(40, 40, 46))
    d.rectangle([x + w * 0.64, y + h * 0.46, x + w, y + h * 0.53], fill=(40, 40, 46))
    d.polygon([(x + w * 0.38, y + h * 0.53), (x + w * 0.50, y + h * 0.68),
               (x + w * 0.62, y + h * 0.53)], fill=(40, 40, 46))
    for bx in (0.16, 0.84):
        d.rectangle([x + w * bx - 2, y + h * 0.22, x + w * bx + 2,
                     y + h * 0.53], fill=(40, 40, 46))
    for cx, cy, r in ((0.50, 0.30, 8), (0.44, 0.22, 6), (0.57, 0.25, 5)):
        d.ellipse([x + w * cx - r, y + h * cy - r, x + w * cx + r,
                   y + h * cy + r], fill=(130, 132, 136))
    _burst(d, x + w * 0.50, y + h * 0.40, 9, (232, 160, 40))
    d.line([(x + w * 0.30, y + h * 0.12), (x + w * 0.44, y + h * 0.30)],
           fill=(255, 220, 120), width=2)


def panel_poland(d, x, y, w, h):
    # pale sky, two jets on patrol, a falling missile trail, a red pin
    d.rectangle([x, y, x + w, y + h], fill=(222, 232, 240))
    for cx, cy, r in ((0.22, 0.20, 10), (0.45, 0.14, 12), (0.70, 0.22, 9)):
        d.ellipse([x + w * cx - r, y + h * cy - r, x + w * cx + r,
                   y + h * cy + r], fill=(255, 255, 255))
    d.line([(x + w * 0.78, y + h * 0.10), (x + w * 0.55, y + h * 0.55)],
           fill=(178, 34, 34), width=2)
    _burst(d, x + w * 0.55, y + h * 0.55, 8, (232, 160, 40))
    for jx, jy in ((0.18, 0.55), (0.38, 0.68)):
        d.polygon([(x + w * jx, y + h * jy - 6), (x + w * jx + 16, y + h * jy),
                   (x + w * jx, y + h * jy + 6), (x + w * jx + 4, y + h * jy)],
                  fill=(60, 60, 66))
    d.rectangle([x, y + h * 0.82, x + w, y + h], fill=(150, 170, 120))
    d.ellipse([x + w * 0.55 - 6, y + h * 0.78 - 6, x + w * 0.55 + 6,
               y + h * 0.78 + 6], fill=RED, outline=(255, 255, 255), width=1)


def panel_summit(d, x, y, w, h):
    # round table, three chairs, three small flags
    d.rectangle([x, y, x + w, y + h], fill=(238, 232, 214))
    d.ellipse([x + w * 0.20, y + h * 0.42, x + w * 0.80, y + h * 0.88],
              fill=(150, 120, 80))
    d.ellipse([x + w * 0.28, y + h * 0.48, x + w * 0.72, y + h * 0.72],
              fill=(196, 164, 120))
    for i, col in enumerate(((178, 34, 34), (30, 80, 160), (222, 40, 40))):
        px = x + w * (0.20 + i * 0.30)
        d.line([(px, y + h * 0.10), (px, y + h * 0.42)], fill=(90, 90, 90),
               width=2)
        d.rectangle([px + 1, y + h * 0.10, px + w * 0.20, y + h * 0.26],
                    fill=col)
    d.ellipse([x + w * 0.44, y + h * 0.52, x + w * 0.56, y + h * 0.64],
              fill=(232, 196, 90))


def panel_scales(d, x, y, w, h):
    # scales of justice on a plinth
    d.rectangle([x, y, x + w, y + h], fill=(226, 232, 240))
    d.rectangle([x + w * 0.14, y + h * 0.82, x + w * 0.86, y + h * 0.90],
                fill=(90, 90, 96))
    d.line([(x + w * 0.50, y + h * 0.16), (x + w * 0.50, y + h * 0.82)],
           fill=(60, 60, 66), width=3)
    d.line([(x + w * 0.24, y + h * 0.20), (x + w * 0.76, y + h * 0.20)],
           fill=(60, 60, 66), width=3)
    for bx in (0.24, 0.76):
        cx = x + w * bx
        d.line([(cx, y + h * 0.20), (cx, y + h * 0.46)], fill=(60, 60, 66),
               width=2)
        d.polygon([(cx - 13, y + h * 0.46), (cx + 13, y + h * 0.46),
                   (cx, y + h * 0.66)], fill=(176, 141, 58))
    _burst(d, x + w * 0.50, y + h * 0.12, 5, (232, 196, 90))


def panel_fall(d, x, y, w, h):
    # falling chart, red candles
    d.rectangle([x, y, x + w, y + h], fill=(248, 232, 228))
    pts = [(x + w * 0.08, y + h * 0.18), (x + w * 0.26, y + h * 0.30),
           (x + w * 0.44, y + h * 0.28), (x + w * 0.62, y + h * 0.52),
           (x + w * 0.80, y + h * 0.62), (x + w * 0.92, y + h * 0.80)]
    d.line(pts, fill=(178, 34, 34), width=3)
    d.polygon([(x + w * 0.92, y + h * 0.80), (x + w * 0.84, y + h * 0.80),
               (x + w * 0.92, y + h * 0.70)], fill=(178, 34, 34))
    for bx, top, bot in ((0.16, 0.30, 0.48), (0.38, 0.26, 0.44),
                         (0.60, 0.44, 0.66), (0.80, 0.58, 0.78)):
        cx = x + w * bx
        d.rectangle([cx - 5, y + h * top, cx + 5, y + h * bot],
                    fill=(198, 60, 60))
        d.line([(cx, y + h * (top - 0.06)), (cx, y + h * (bot + 0.06))],
               fill=(198, 60, 60), width=2)


def panel_riyadh(d, x, y, w, h):
    # night skyline, towers, interceptor burst above
    d.rectangle([x, y, x + w, y + h], fill=(30, 32, 52))
    for bx, bh in ((0.08, 0.55), (0.26, 0.72), (0.46, 0.48), (0.64, 0.62),
                   (0.82, 0.42)):
        d.rectangle([x + w * bx, y + h * (1 - bh), x + w * (bx + 0.14),
                     y + h], fill=(70, 74, 96))
        for wy in range(4):
            d.rectangle([x + w * (bx + 0.03), y + h * (1 - bh + 0.08 + wy * 0.12),
                         x + w * (bx + 0.06), y + h * (1 - bh + 0.14 + wy * 0.12)],
                        fill=(232, 196, 90))
    _burst(d, x + w * 0.50, y + h * 0.22, 10, (232, 160, 40))
    d.line([(x + w * 0.20, y + h * 0.55), (x + w * 0.46, y + h * 0.26)],
           fill=(255, 255, 255), width=2)
    d.line([(x + w * 0.80, y + h * 0.55), (x + w * 0.54, y + h * 0.26)],
           fill=(255, 255, 255), width=2)


def panel_mercury(d, x, y, w, h):
    # black space, cratered Mercury, small probe with panels
    d.rectangle([x, y, x + w, y + h], fill=(12, 14, 24))
    for sx, sy in ((0.12, 0.15), (0.30, 0.08), (0.85, 0.12), (0.92, 0.35),
                   (0.08, 0.45), (0.70, 0.06)):
        d.ellipse([x + w * sx - 1, y + h * sy - 1, x + w * sx + 1,
                   y + h * sy + 1], fill=(255, 255, 255))
    cx, cy, r = x + w * 0.42, y + h * 0.55, h * 0.30
    d.ellipse([cx - r, cy - r, cx + r, cy + r], fill=(178, 164, 142))
    for kx, ky, kr in ((0.36, 0.45, 5), (0.48, 0.62, 4), (0.34, 0.62, 3),
                       (0.50, 0.42, 3)):
        d.ellipse([x + w * kx - kr, y + h * ky - kr, x + w * kx + kr,
                   y + h * ky + kr], fill=(140, 126, 106))
    d.rectangle([x + w * 0.72, y + h * 0.18, x + w * 0.80, y + h * 0.26],
                fill=(200, 200, 210))
    d.rectangle([x + w * 0.64, y + h * 0.20, x + w * 0.72, y + h * 0.24],
                fill=(40, 90, 160))
    d.rectangle([x + w * 0.80, y + h * 0.20, x + w * 0.88, y + h * 0.24],
                fill=(40, 90, 160))
    d.line([(x + w * 0.72, y + h * 0.26), (cx + r * 0.6, cy - r * 0.6)],
           fill=(255, 255, 255), width=1)


def panel_race(d, x, y, w, h):
    # night street circuit, neon, small race car on a curve
    d.rectangle([x, y, x + w, y + h], fill=(20, 20, 34))
    for cx, cy, col in ((0.15, 0.18, (232, 196, 90)), (0.45, 0.10, (255, 120, 160)),
                        (0.75, 0.20, (120, 200, 255)), (0.90, 0.35, (232, 196, 90))):
        d.ellipse([x + w * cx - 3, y + h * cy - 3, x + w * cx + 3,
                   y + h * cy + 3], fill=col)
    d.arc([x - w * 0.10, y + h * 0.52, x + w * 0.70, y + h * 1.10],
          300, 60, fill=(200, 200, 210), width=4)
    d.rectangle([x + w * 0.58, y + h * 0.74, x + w * 0.86, y + h * 0.84],
                fill=(178, 34, 34))
    d.ellipse([x + w * 0.62, y + h * 0.84, x + w * 0.68, y + h * 0.90],
              fill=(18, 22, 30))
    d.ellipse([x + w * 0.78, y + h * 0.84, x + w * 0.84, y + h * 0.90],
              fill=(18, 22, 30))
    d.rectangle([x + w * 0.60, y + h * 0.70, x + w * 0.72, y + h * 0.75],
                fill=(120, 160, 200))


PANELS = [
    (panel_kyiv, "Kyiv bridges hit in the overnight barrage"),
    (panel_poland, "Russian missiles land in Poland"),
    (panel_summit, "Trump defends Putin and Xi after summit"),
    (panel_scales, "World Court finds Myanmar guilty"),
    (panel_fall, "AI rout: Nasdaq dives 5.3%"),
    (panel_riyadh, "Houthi missiles aimed at Riyadh shot down"),
    (panel_mercury, "BepiColombo reaches Mercury orbit"),
    (panel_race, "Russell tops dry Las Vegas FP3"),
]

PANEL_BG = [(222, 232, 240), (240, 226, 216), (226, 238, 226), (238, 228, 240),
            (232, 238, 240), (240, 236, 214), (236, 226, 232), (224, 234, 232)]


# ---------- page assembly ----------
MARGIN = 28
COL_W = 304
COL_GAP = 16
COL_X = [MARGIN, MARGIN + COL_W + COL_GAP, MARGIN + 2 * (COL_W + COL_GAP)]
COL_TOP = 478
COL_BOTTOM = 826


def main():
    pictured = [s for s in STORIES if s.get("pictured")]
    columns = [s for s in STORIES if not s.get("pictured")]
    assert len(pictured) == 8, len(pictured)
    assert len(columns) == 22, len(columns)
    assert len(BRIEFS) == 8 and len(FIGURES) == 4

    img = Image.new("RGB", (W, H), PAPER)
    d = ImageDraw.Draw(img)

    # ---- masthead ----
    d.rectangle([0, 0, W, 88], fill=NAVY)
    d.text((MARGIN, 14), "THE WORLD IN ONE DAY",
           font=font("serif_b", 44), fill=(255, 255, 255))
    for yy, txt, fnt, col in (
            (20, "SATURDAY", font("sans_b", 20), (255, 255, 255)),
            (46, "21 NOVEMBER 2026", font("sans_b", 20), (232, 196, 90))):
        tw = d.textlength(txt, font=fnt)
        d.text((W - MARGIN - tw, yy), txt, font=fnt, fill=col)
    d.rectangle([0, 88, W, 92], fill=RED)
    d.text((MARGIN, 98),
           "38 verified stories from six continents \u2014 8 illustrated \u2014 "
           "every headline below happened, or was first reported, on "
           "Saturday 21 November 2026.",
           font=font("serif", 12), fill=INK)

    # ---- lead (left) ----
    lx, ly = MARGIN, 128
    lw = 568
    d.text((lx, ly), "LEAD \u2014 EUROPE", font=font("sans_b", 11), fill=RED)
    ly += 17
    ly = draw_lines(d, lx, ly, "RUSSIA'S BIGGEST BARRAGE HITS KYIV \u2014 "
                    "AND LANDS IN POLAND",
                    font("serif_b", 34), lw, INK, leading=36)
    ly = draw_lines(d, lx, ly + 2,
                    "More than 400 drones and 110 missiles pound Ukraine "
                    "overnight; three Kyiv bridges hit, eight killed. Two "
                    "missiles fall in Poland as NATO jets scramble.",
                    font("sans", 13), lw, BODY, leading=16)
    ly += 6
    d.line([(lx, ly), (lx + lw, ly)], fill=FAINT, width=1)
    ly += 8
    ly = draw_lines(d, lx, ly, "AI ROUT: NASDAQ DIVES 5.3%",
                    font("serif_b", 21), lw, INK, leading=23)
    draw_lines(d, lx, ly + 1,
               "S&P 500 falls 3.7% into correction; Nvidia -14% and "
               "Anthropic -9% a day after its record debut.",
               font("sans", 11), lw, BODY, leading=13)

    # ---- map (right) ----
    mx, my = 612, 128
    mw = W - MARGIN - mx
    d.text((mx, my), "THE WORLD \u2014 12 STORIES ON THE MAP",
           font=font("sans_b", 11), fill=NAVY2)
    draw_map(d, mx, my + 18, mw, 140)
    draw_pin_key(d, mx, my + 166, mw)

    # ---- the day in pictures ----
    py = 350
    d.text((MARGIN, py), "THE DAY IN PICTURES \u2014 8 STORIES, DRAWN",
           font=font("sans_b", 11), fill=NAVY2)
    d.line([(MARGIN + 300, py + 7), (W - MARGIN, py + 7)], fill=FAINT,
           width=1)
    pw = (W - 2 * MARGIN - 7 * 8) // 8
    for i, (painter, cap) in enumerate(PANELS):
        px = MARGIN + i * (pw + 8)
        d.rectangle([px, py + 18, px + pw, py + 18 + 70], fill=PANEL_BG[i],
                    outline=(180, 178, 170), width=1)
        painter(d, px + 1, py + 19, pw - 2, 68)
        draw_lines(d, px, py + 92, cap, font("sans", 8), pw, INK, leading=10)

    # ---- story columns, balanced by measured height ----
    heights = [story_block_height(d, s, COL_W) for s in columns]
    cols, col_h = [[], [], []], [0, 0, 0]
    for story, h in zip(columns, heights):
        i = min(range(3), key=lambda k: col_h[k])
        cols[i].append(story)
        col_h[i] += h
    drawn = 0
    for i, stories in enumerate(cols):
        x = COL_X[i]
        y = COL_TOP
        for story in stories:
            y = draw_story(d, x, y, story, COL_W)
            drawn += 1
            assert y <= COL_BOTTOM, "column %d overflow at %s" % (i, story["head"])
        if i < 2:
            d.line([(x + COL_W + 8, COL_TOP),
                    (x + COL_W + 8, COL_BOTTOM)], fill=FAINT, width=1)
    assert drawn == len(columns), "drew %d of %d" % (drawn, len(columns))

    # ---- also in brief ----
    by = 836
    d.text((MARGIN, by), "ALSO IN BRIEF", font=font("sans_b", 10), fill=NAVY2)
    d.line([(MARGIN + 110, by + 7), (W - MARGIN, by + 7)], fill=FAINT, width=1)
    bw = (W - 2 * MARGIN - 3 * 24) // 4
    for i, (lead, text) in enumerate(BRIEFS):
        bx = MARGIN + (i % 4) * (bw + 24)
        byy = by + 16 + (i // 4) * 38
        byy = draw_lines(d, bx, byy, lead, font("sans_b", 10), bw, INK,
                         leading=12)
        draw_lines(d, bx, byy + 1, text, font("sans", 9), bw, BODY,
                   leading=11)

    # ---- day in figures ----
    fy = 924
    d.rectangle([MARGIN, fy, W - MARGIN, fy + 48], fill=NAVY)
    fw = (W - 2 * MARGIN) // 4
    for i, (num, label) in enumerate(FIGURES):
        x = MARGIN + i * fw + 12
        d.text((x, fy + 5), num, font=font("serif_b", 18), fill=(232, 196, 90))
        d.text((x, fy + 28), label, font=font("sans", 10),
               fill=(255, 255, 255))
        if i:
            d.line([(MARGIN + i * fw, fy + 8),
                    (MARGIN + i * fw, fy + 40)], fill=(60, 90, 130), width=1)

    # ---- footer ----
    d.text((MARGIN, 984),
           "THE WORLD IN ONE DAY \u2014 Saturday 21 November 2026 \u00b7 "
           "38 stories \u00b7 six continents \u00b7 markets: Nasdaq -5.3%, "
           "S&P -3.7% into correction; Brent settles $92.57; GTA VI "
           "takes $3.8bn on day one",
           font=font("sans", 10), fill=GREY)

    out = os.path.join(HERE, "entry.png")
    img.save(out, "PNG", optimize=True)
    size = os.path.getsize(out)
    print("wrote %s %d bytes (limit 1048576)" % (out, size))
    assert size <= 1048576, "entry.png over 1 MiB"


if __name__ == "__main__":
    main()
