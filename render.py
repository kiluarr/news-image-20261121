# render.py — renders the entry image for news-image-20261121.
# The front page is "THE WORLD IN ONE DAY — Saturday 21 November 2026":
# 38 verified stories from six continents, 8 illustrated panels, a world
# map carrying 12 numbered pins, a day-in-figures strip and a markets line.
# Every story below either happened on Saturday 21 November 2026 or was
# first reported that day (sources: the oneturn.news day page, CNN,
# Reuters/AP, Investors.com, Speedcafe, Jagran Josh, Aju Press — the full
# list is in STORIES.md). The output is deterministic: fonts and data are
# fixed, and there are no timestamps and no randomness anywhere.
# Usage: python3 render.py  ->  entry.png (1024x1024) next to this file.

import math
import os

from PIL import Image, ImageDraw, ImageFont

HERE = os.path.dirname(os.path.abspath(__file__))
W, H = 1024, 1024

# Palette for the whole page: paper, ink, section accents, map colours.
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
# Candidate family names, tried in order until a file is found on disk.
_FONT_FAMILIES = {
    "serif_b": ["DejaVuSerif-Bold", "LiberationSerif-Bold"],
    "serif": ["DejaVuSerif", "LiberationSerif-Regular"],
    "sans": ["DejaVuSans", "LiberationSans-Regular"],
    "sans_b": ["DejaVuSans-Bold", "LiberationSans-Bold"],
}


def _locate_font(name):
    for label in _FONT_FAMILIES[name]:
        for base in ("/usr/share/fonts/truetype/dejavu",
                     "/usr/share/fonts/truetype/liberation"):
            path = os.path.join(base, label + ".ttf")
            if os.path.exists(path):
                return path
    raise FileNotFoundError("no font file for " + name)


_FONT_CACHE = {}


def load_font(name, size):
    key = (name, int(size))
    if key not in _FONT_CACHE:
        _FONT_CACHE[key] = ImageFont.truetype(_locate_font(name), int(size))
    return _FONT_CACHE[key]


# ---------- text helpers ----------
def wrap_text(canvas, text, typeface, width):
    words = text.split()
    lines, current = [], ""
    for word in words:
        candidate = (current + " " + word).strip()
        if canvas.textlength(candidate, font=typeface) <= width:
            current = candidate
        else:
            if current:
                lines.append(current)
            current = word
    if current:
        lines.append(current)
    return lines


def draw_lines(canvas, x, y, text, typeface, width, fill, leading=None):
    advance = leading if leading is not None else typeface.size + 2
    for line in wrap_text(canvas, text, typeface, width):
        canvas.text((x, y), line, font=typeface, fill=fill)
        y += advance
    return y


def shrink_to_fit(canvas, text, name, start_size, width, floor=10):
    point = start_size
    typeface = load_font(name, point)
    while point > floor and canvas.textlength(text, font=typeface) > width:
        point -= 1
        typeface = load_font(name, point)
    return typeface


# ---------- the day's stories ----------
# One dict per story: headline, one-line deck, region, accent colour.
# "pictured" flags the 8 stories that also get a drawn panel.
STORIES = [
    # --- pictured (8) ---
    {"head": "Russia's biggest barrage hits Kyiv bridges",
     "deck": "400+ drones, 110+ missiles overnight; 8 killed, power cut.",
     "region": "EUROPE", "color": NAVY2, "pictured": True},
    {"head": "Russian missiles land in Poland",
     "deck": "Tusk calls it a deliberate provocation; NATO jets scrambled.",
     "region": "EUROPE", "color": NAVY2, "pictured": True},
    {"head": "Trump defends Putin and Xi after summit",
     "deck": "Calls Putin a friend; Zelensky answers: \u201cHe's a killer.\u201d",
     "region": "WORLD", "color": GREY, "pictured": True},
    {"head": "World Court: Myanmar committed genocide",
     "deck": "First state found responsible; return and reparations ordered.",
     "region": "WORLD", "color": GREY, "pictured": True},
    {"head": "AI rout: Nasdaq dives 5.3%",
     "deck": "S&P -3.7% into correction; Nvidia -14%, Anthropic -9%.",
     "region": "AMERICAS", "color": GREEN, "pictured": True},
    {"head": "Houthi missiles aimed at Riyadh shot down",
     "deck": "Coalition intercepts three; third night of alerts.",
     "region": "MIDDLE EAST", "color": RED, "pictured": True},
    {"head": "BepiColombo reaches Mercury orbit",
     "deck": "After eight years and 10bn km, only the second to orbit.",
     "region": "SPACE", "color": NAVY2, "pictured": True},
    {"head": "Russell tops dry Las Vegas FP3",
     "deck": "Fastest in final practice; contact with Verstappen at Turn 14.",
     "region": "SPORT", "color": GREEN, "pictured": True},
    # --- columns (22) ---
    {"head": "Israeli strikes kill six in Gaza",
     "deck": "Despite the ceasefire; 1,600+ killed since the truce began.",
     "region": "MIDDLE EAST", "color": RED},
    {"head": "Hormuz attacks go on as talks stall",
     "deck": "Iran says it downed a US MQ-9 drone; US sanctions four trustees.",
     "region": "MIDDLE EAST", "color": RED},
    {"head": "Oil set for third weekly fall",
     "deck": "Brent settles $92.57; Hormuz flows back near pre-war levels.",
     "region": "MIDDLE EAST", "color": RED},
    {"head": "UK and EU sign biggest post-Brexit deals",
     "deck": "Food, carbon, youth mobility; Burnham sees +0.5% growth a year.",
     "region": "EUROPE", "color": NAVY2},
    {"head": "Estonia to shut Russia border crossings",
     "deck": "Five crossings close from 1 December after an arson attempt.",
     "region": "EUROPE", "color": NAVY2},
    {"head": "Denmark expels Russian diplomat",
     "deck": "Alleged plot to kill a US-Ukrainian rapper; two arrested.",
     "region": "EUROPE", "color": NAVY2},
    {"head": "Gen Z protests sweep 25 countries",
     "deck": "Students march on living costs, rearmament and climate.",
     "region": "EUROPE", "color": NAVY2},
    {"head": "Cyclone Akvan crosses Odisha coast",
     "deck": "Strong winds and heavy rain near Gopalpur.",
     "region": "ASIA-PACIFIC", "color": TEAL},
    {"head": "Korea raised at Shenzhen summit",
     "deck": "Trump: North Korea discussed; joint vow to cut nuclear risks.",
     "region": "ASIA-PACIFIC", "color": TEAL},
    {"head": "GTA VI earns $3.8bn on day one",
     "deck": "Beats every game launch and film box-office record.",
     "region": "AMERICAS", "color": GREEN},
    {"head": "Palisades fire arson verdict",
     "deck": "Jury convicts Rinderknecht; fire killed 12, razed 6,800 homes.",
     "region": "AMERICAS", "color": GREEN},
    {"head": "Mamdani: close Rikers by 2032",
     "deck": "New York mayor sets out plan; the 2027 law must change.",
     "region": "AMERICAS", "color": GREEN},
    {"head": "US loses measles elimination status",
     "deck": "7,700 cases and 13 deaths since the start of last year.",
     "region": "AMERICAS", "color": GREEN},
    {"head": "Trump threatens tax on AI data centres abroad",
     "deck": "US firms building overseas face a \u201ctremendous tax\u201d.",
     "region": "AMERICAS", "color": GREEN},
    {"head": "Trump wants ousted Nvidia chief back",
     "deck": "Urges Huang's return; board says it has no such plans.",
     "region": "AMERICAS", "color": GREEN},
    {"head": "Nigeria boat capsizes, 30 feared dead",
     "deck": "Funeral mourners aboard; at least 4 dead, ~300 missing.",
     "region": "AFRICA", "color": GOLD},
    {"head": "Tanzania's Lissu convicted of sedition",
     "deck": "Opposition leader calls it political; UK voices concern.",
     "region": "AFRICA", "color": GOLD},
    {"head": "Uganda curbs gatherings over Ebola",
     "deck": "Limits in 34 districts bordering DR Congo.",
     "region": "AFRICA", "color": GOLD},
    {"head": "COP31 runs past deadline",
     "deck": "Draft has no fossil-fuel mention; EU warns of a fossil summit.",
     "region": "WORLD", "color": GREY},
    {"head": "Riemann proof claimed with AI help",
     "deck": "Anthropic mathematician's claim; verification will take time.",
     "region": "WORLD", "color": GREY},
    {"head": "Cancer pill hailed as breakthrough",
     "deck": "Daraxonrasib trial: tumours undetectable in 1 in 12 patients.",
     "region": "WORLD", "color": GREY},
    {"head": "Voyager 1 now 24 light-hours away",
     "deck": "16.1bn miles out; light takes a full day to reach it.",
     "region": "WORLD", "color": GREY},
]

# --- briefs (8): (bold lead, supporting line) ---
BRIEFS = [
    ("Peru quake 6.7 shakes Andes", "Residents flee in Lima; no casualties at first."),
    ("Iraq retakes militia stronghold", "Forces enter Jurf al-Sakhar, first time in 12 years."),
    ("Haiti: 2 Salvadoran troops killed", "Killed handling explosives in Port-au-Prince."),
    ("Gupta gets 19 years in US plot", "Sentenced over plot to kill Sikh leader Pannun."),
    ("Bayer Roundup deal: $7.25bn", "Judge approves; Bayer admits no fault."),
    ("Bolsonaro in hospital", "Intestinal obstruction; under house arrest."),
    ("Alcaraz stays unbeaten in Turin", "Beats Cobolli at the ATP Finals."),
    ("India fight back in Wellington", "Jaiswal 85; India 159/1, trailing by 209 runs."),
]

# --- figures (4): (big number, what it counts) ---
FIGURES = [
    ("400+", "drones fired at Ukraine overnight"),
    ("110+", "missiles in the barrage, 27 ballistic"),
    ("-5.3%", "Nasdaq's Friday fall, gains erased"),
    ("$3.8bn", "GTA VI first-day sales record"),
]

# Map pins: (number, longitude, latitude, label)
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

# Simplified continent outlines as (lon, lat) points, equirectangular.
CONTINENTS = {
    "NA": [(-168, 66), (-150, 70), (-130, 71), (-115, 72),
           (-100, 73), (-85, 70), (-75, 72), (-65, 60),
           (-55, 47), (-65, 44), (-70, 40), (-76, 35),
           (-81, 31), (-84, 30), (-90, 21), (-97, 16),
           (-105, 20), (-112, 24), (-117, 33), (-125, 40),
           (-124, 48), (-135, 58), (-155, 58), (-165, 60)],
    "SA": [(-79, 9), (-77, 4), (-80, -3), (-81, -6),
           (-77, -12), (-72, -18), (-70, -23), (-70, -33),
           (-66, -40), (-68, -52), (-65, -55), (-60, -48),
           (-57, -38), (-52, -32), (-48, -27), (-41, -22),
           (-39, -17), (-35, -9), (-35, -6), (-42, -3),
           (-50, 0), (-53, 4), (-60, 8), (-70, 11)],
    "AF": [(-17, 15), (-16, 21), (-10, 31), (-6, 35),
           (0, 36), (10, 37), (20, 32), (30, 31),
           (33, 28), (36, 27), (39, 21), (41, 15),
           (43, 12), (48, 11), (51, 12), (44, 5),
           (41, 0), (38, -8), (35, -15), (32, -25),
           (28, -33), (20, -35), (17, -32), (14, -22),
           (13, -12), (12, -6), (9, 0), (4, 6),
           (-8, 5), (-13, 8)],
    "EU": [(-10, 36), (-9, 43), (-2, 48), (-4, 50),
           (-1, 51), (3, 53), (7, 54), (8, 57),
           (11, 58), (13, 56), (18, 56), (21, 55),
           (24, 59), (26, 60), (30, 62), (24, 65),
           (20, 70), (14, 68), (10, 63), (5, 58),
           (3, 54), (-2, 50), (-6, 44), (-9, 38)],
    "AS": [(30, 60), (35, 66), (45, 68), (55, 69),
           (65, 70), (75, 72), (85, 74), (95, 76),
           (105, 77), (115, 73), (125, 72), (135, 71),
           (145, 72), (155, 69), (162, 64), (160, 58),
           (155, 55), (150, 60), (142, 53), (140, 47),
           (135, 43), (130, 40), (127, 38), (122, 32),
           (120, 27), (115, 23), (110, 20), (106, 10),
           (101, 7), (97, 12), (92, 20), (88, 22),
           (84, 19), (80, 14), (77, 8), (75, 12),
           (73, 19), (68, 23), (62, 25), (57, 26),
           (53, 27), (50, 30), (48, 29), (44, 29),
           (40, 31), (36, 36), (33, 37), (30, 40),
           (28, 45), (30, 50), (30, 55)],
    "OC": [(113, -22), (114, -30), (115, -35), (120, -34),
           (124, -33), (129, -32), (134, -33), (138, -35),
           (142, -38), (147, -39), (150, -37), (153, -32),
           (153, -27), (150, -22), (146, -19), (142, -15),
           (140, -17), (136, -15), (132, -12), (128, -14),
           (124, -15), (120, -19), (116, -21)],
}

# Label offsets (dx, dy) for each numbered pin, keeping labels off the land.
PIN_NUDGE = {
    1: (20, -20),
    2: (-20, 6),
    3: (-20, 14),
    4: (-26, 2),
    5: (16, 16),
    6: (16, 12),
    7: (-26, -16),
    8: (14, 2),
    9: (16, -16),
    10: (16, 14),
    11: (-16, 6),
    12: (-16, 8),
}


# ---------- map ----------
def _project(lon, lat, left, top, w, h):
    """Equirectangular projection of a lon/lat point into the map box."""
    return (left + (lon + 180) / 360.0 * w,
            top + (85 - lat) / 145.0 * h)


def draw_map(canvas, left, top, w, h):
    canvas.rectangle([left, top, left + w, top + h], fill=SEA,
                     outline=EDGE, width=1)
    for gx in range(-150, 181, 30):
        grid_x = left + (gx + 180) / 360.0 * w
        canvas.line([(grid_x, top), (grid_x, top + h)],
                    fill=(185, 208, 220), width=1)
    for gy in range(-60, 86, 30):
        grid_y = top + (85 - gy) / 145.0 * h
        canvas.line([(left, grid_y), (left + w, grid_y)],
                    fill=(185, 208, 220), width=1)
    for pts in CONTINENTS.values():
        outline = [_project(lon, lat, left, top, w, h) for lon, lat in pts]
        canvas.polygon(outline, fill=LAND, outline=EDGE)
    pin_font = load_font("sans_b", 9)
    for num, lon, lat, _label in PINS:
        cx, cy = _project(lon, lat, left, top, w, h)
        dx, dy = PIN_NUDGE.get(num, (0, 0))
        px, py = cx + dx, cy + dy
        if (dx, dy) != (0, 0):
            canvas.line([(cx, cy), (px, py)], fill=RED, width=1)
        canvas.ellipse([px - 7, py - 7, px + 7, py + 7], fill=RED,
                       outline=(255, 255, 255), width=1)
        tw = canvas.textlength(str(num), font=pin_font)
        canvas.text((px - tw / 2, py - 6), str(num), font=pin_font,
                    fill=(255, 255, 255))


def draw_pin_key(canvas, left, top, w):
    key_font = load_font("sans", 10)
    column_width = w // 3
    for i, (num, _lon, _lat, label) in enumerate(PINS):
        cell_x = left + (i % 3) * column_width
        cell_y = top + (i // 3) * 12
        canvas.text((cell_x, cell_y), "%d %s" % (num, label),
                    font=key_font, fill=INK)


# ---------- story blocks ----------
def story_block_height(canvas, story, width):
    headline_font = shrink_to_fit(canvas, story["head"], "serif_b", 12,
                                  width)
    total = 11  # kicker
    total += len(wrap_text(canvas, story["head"], headline_font, width)) * 13
    total += 1 + len(wrap_text(canvas, story["deck"],
                               load_font("sans", 9), width)) * 11
    return total + 4


def draw_story(canvas, x, y, story, width):
    canvas.text((x, y), story["region"], font=load_font("sans_b", 9),
                fill=story["color"])
    y += 11
    headline_font = shrink_to_fit(canvas, story["head"], "serif_b", 12,
                                  width)
    y = draw_lines(canvas, x, y, story["head"], headline_font, width, INK,
                   leading=13)
    y = draw_lines(canvas, x, y + 1, story["deck"], load_font("sans", 9),
                   width, BODY, leading=11)
    return y + 4


# ---------- picture panels: 8 flat pictograms ----------
def _burst(canvas, cx, cy, r, fill):
    points = []
    for i in range(12):
        angle = i * math.pi / 6
        radius = r if i % 2 == 0 else r * 0.45
        points.append((cx + radius * math.cos(angle),
                       cy + radius * math.sin(angle)))
    canvas.polygon(points, fill=fill)


def panel_kyiv_bridge(canvas, x, y, w, h):
    # Kyiv at night: river, three bridge spans with the middle one down, smoke
    canvas.rectangle([x, y, x + w, y + h], fill=(28, 42, 66))
    canvas.rectangle([x, y + h * 0.66, x + w, y + h], fill=(64, 98, 132))
    canvas.rectangle([x, y + h * 0.46, x + w * 0.36, y + h * 0.53],
                     fill=(40, 40, 46))
    canvas.rectangle([x + w * 0.64, y + h * 0.46, x + w, y + h * 0.53],
                     fill=(40, 40, 46))
    canvas.polygon([(x + w * 0.38, y + h * 0.53), (x + w * 0.50, y + h * 0.68),
                    (x + w * 0.62, y + h * 0.53)], fill=(40, 40, 46))
    for tower_x in (0.16, 0.84):
        canvas.rectangle([x + w * tower_x - 2, y + h * 0.22,
                          x + w * tower_x + 2, y + h * 0.53],
                         fill=(40, 40, 46))
    for puff_x, puff_y, puff_r in ((0.50, 0.30, 8), (0.44, 0.22, 6),
                                   (0.57, 0.25, 5)):
        canvas.ellipse([x + w * puff_x - puff_r, y + h * puff_y - puff_r,
                        x + w * puff_x + puff_r, y + h * puff_y + puff_r],
                       fill=(130, 132, 136))
    _burst(canvas, x + w * 0.50, y + h * 0.40, 9, (232, 160, 40))
    canvas.line([(x + w * 0.30, y + h * 0.12), (x + w * 0.44, y + h * 0.30)],
                fill=(255, 220, 120), width=2)


def panel_poland_patrol(canvas, x, y, w, h):
    # Pale sky, two jets on patrol, a falling missile trail, a red pin
    canvas.rectangle([x, y, x + w, y + h], fill=(222, 232, 240))
    for cloud_x, cloud_y, cloud_r in ((0.22, 0.20, 10), (0.45, 0.14, 12),
                                      (0.70, 0.22, 9)):
        canvas.ellipse([x + w * cloud_x - cloud_r, y + h * cloud_y - cloud_r,
                        x + w * cloud_x + cloud_r, y + h * cloud_y + cloud_r],
                       fill=(255, 255, 255))
    canvas.line([(x + w * 0.78, y + h * 0.10), (x + w * 0.55, y + h * 0.55)],
                fill=(178, 34, 34), width=2)
    _burst(canvas, x + w * 0.55, y + h * 0.55, 8, (232, 160, 40))
    for jet_x, jet_y in ((0.18, 0.55), (0.38, 0.68)):
        canvas.polygon([(x + w * jet_x, y + h * jet_y - 6),
                        (x + w * jet_x + 16, y + h * jet_y),
                        (x + w * jet_x, y + h * jet_y + 6),
                        (x + w * jet_x + 4, y + h * jet_y)],
                       fill=(60, 60, 66))
    canvas.rectangle([x, y + h * 0.82, x + w, y + h], fill=(150, 170, 120))
    canvas.ellipse([x + w * 0.55 - 6, y + h * 0.78 - 6, x + w * 0.55 + 6,
                    y + h * 0.78 + 6], fill=RED, outline=(255, 255, 255),
                   width=1)


def panel_summit_table(canvas, x, y, w, h):
    # A round table, three chairs, three small flags above it
    canvas.rectangle([x, y, x + w, y + h], fill=(238, 232, 214))
    canvas.ellipse([x + w * 0.20, y + h * 0.42, x + w * 0.80, y + h * 0.88],
                   fill=(150, 120, 80))
    canvas.ellipse([x + w * 0.28, y + h * 0.48, x + w * 0.72, y + h * 0.72],
                   fill=(196, 164, 120))
    for i, flag in enumerate(((178, 34, 34), (30, 80, 160), (222, 40, 40))):
        flag_x = x + w * (0.20 + i * 0.30)
        canvas.line([(flag_x, y + h * 0.10), (flag_x, y + h * 0.42)],
                    fill=(90, 90, 90), width=2)
        canvas.rectangle([flag_x + 1, y + h * 0.10, flag_x + w * 0.20,
                          y + h * 0.26], fill=flag)
    canvas.ellipse([x + w * 0.44, y + h * 0.52, x + w * 0.56, y + h * 0.64],
                   fill=(232, 196, 90))


def panel_scales_court(canvas, x, y, w, h):
    # Scales of justice standing on a plinth
    canvas.rectangle([x, y, x + w, y + h], fill=(226, 232, 240))
    canvas.rectangle([x + w * 0.14, y + h * 0.82, x + w * 0.86, y + h * 0.90],
                     fill=(90, 90, 96))
    canvas.line([(x + w * 0.50, y + h * 0.16), (x + w * 0.50, y + h * 0.82)],
                fill=(60, 60, 66), width=3)
    canvas.line([(x + w * 0.24, y + h * 0.20), (x + w * 0.76, y + h * 0.20)],
                fill=(60, 60, 66), width=3)
    for pan_x in (0.24, 0.76):
        pan_cx = x + w * pan_x
        canvas.line([(pan_cx, y + h * 0.20), (pan_cx, y + h * 0.46)],
                    fill=(60, 60, 66), width=2)
        canvas.polygon([(pan_cx - 13, y + h * 0.46), (pan_cx + 13, y + h * 0.46),
                        (pan_cx, y + h * 0.66)], fill=(176, 141, 58))
    _burst(canvas, x + w * 0.50, y + h * 0.12, 5, (232, 196, 90))


def panel_fall_chart(canvas, x, y, w, h):
    # A falling chart line with red candles underneath
    canvas.rectangle([x, y, x + w, y + h], fill=(248, 232, 228))
    trace = [(x + w * 0.08, y + h * 0.18), (x + w * 0.26, y + h * 0.30),
             (x + w * 0.44, y + h * 0.28), (x + w * 0.62, y + h * 0.52),
             (x + w * 0.80, y + h * 0.62), (x + w * 0.92, y + h * 0.80)]
    canvas.line(trace, fill=(178, 34, 34), width=3)
    canvas.polygon([(x + w * 0.92, y + h * 0.80), (x + w * 0.84, y + h * 0.80),
                    (x + w * 0.92, y + h * 0.70)], fill=(178, 34, 34))
    for bar_x, bar_top, bar_bot in ((0.16, 0.30, 0.48), (0.38, 0.26, 0.44),
                                    (0.60, 0.44, 0.66), (0.80, 0.58, 0.78)):
        candle_x = x + w * bar_x
        canvas.rectangle([candle_x - 5, y + h * bar_top, candle_x + 5,
                          y + h * bar_bot], fill=(198, 60, 60))
        canvas.line([(candle_x, y + h * (bar_top - 0.06)),
                     (candle_x, y + h * (bar_bot + 0.06))],
                    fill=(198, 60, 60), width=2)


def panel_riyadh_skyline(canvas, x, y, w, h):
    # Night skyline with towers, an interceptor burst above it
    canvas.rectangle([x, y, x + w, y + h], fill=(30, 32, 52))
    for tower_x, tower_h in ((0.08, 0.55), (0.26, 0.72), (0.46, 0.48),
                             (0.64, 0.62), (0.82, 0.42)):
        canvas.rectangle([x + w * tower_x, y + h * (1 - tower_h),
                          x + w * (tower_x + 0.14), y + h],
                         fill=(70, 74, 96))
        for floor in range(4):
            canvas.rectangle(
                [x + w * (tower_x + 0.03),
                 y + h * (1 - tower_h + 0.08 + floor * 0.12),
                 x + w * (tower_x + 0.06),
                 y + h * (1 - tower_h + 0.14 + floor * 0.12)],
                fill=(232, 196, 90))
    _burst(canvas, x + w * 0.50, y + h * 0.22, 10, (232, 160, 40))
    canvas.line([(x + w * 0.20, y + h * 0.55), (x + w * 0.46, y + h * 0.26)],
                fill=(255, 255, 255), width=2)
    canvas.line([(x + w * 0.80, y + h * 0.55), (x + w * 0.54, y + h * 0.26)],
                fill=(255, 255, 255), width=2)


def panel_mercury_orbit(canvas, x, y, w, h):
    # Black space, cratered Mercury, a small probe with solar panels
    canvas.rectangle([x, y, x + w, y + h], fill=(12, 14, 24))
    for star_x, star_y in ((0.12, 0.15), (0.30, 0.08), (0.85, 0.12),
                           (0.92, 0.35), (0.08, 0.45), (0.70, 0.06)):
        canvas.ellipse([x + w * star_x - 1, y + h * star_y - 1,
                        x + w * star_x + 1, y + h * star_y + 1],
                       fill=(255, 255, 255))
    cx, cy, r = x + w * 0.42, y + h * 0.55, h * 0.30
    canvas.ellipse([cx - r, cy - r, cx + r, cy + r], fill=(178, 164, 142))
    for crater_x, crater_y, crater_r in ((0.36, 0.45, 5), (0.48, 0.62, 4),
                                         (0.34, 0.62, 3), (0.50, 0.42, 3)):
        canvas.ellipse([x + w * crater_x - crater_r,
                        y + h * crater_y - crater_r,
                        x + w * crater_x + crater_r,
                        y + h * crater_y + crater_r],
                       fill=(140, 126, 106))
    canvas.rectangle([x + w * 0.72, y + h * 0.18, x + w * 0.80, y + h * 0.26],
                     fill=(200, 200, 210))
    canvas.rectangle([x + w * 0.64, y + h * 0.20, x + w * 0.72, y + h * 0.24],
                     fill=(40, 90, 160))
    canvas.rectangle([x + w * 0.80, y + h * 0.20, x + w * 0.88, y + h * 0.24],
                     fill=(40, 90, 160))
    canvas.line([(x + w * 0.72, y + h * 0.26), (cx + r * 0.6, cy - r * 0.6)],
                fill=(255, 255, 255), width=1)


def panel_race_circuit(canvas, x, y, w, h):
    # Night street circuit in neon, a small race car on a curve
    canvas.rectangle([x, y, x + w, y + h], fill=(20, 20, 34))
    for light_x, light_y, light_col in (
            (0.15, 0.18, (232, 196, 90)), (0.45, 0.10, (255, 120, 160)),
            (0.75, 0.20, (120, 200, 255)), (0.90, 0.35, (232, 196, 90))):
        canvas.ellipse([x + w * light_x - 3, y + h * light_y - 3,
                        x + w * light_x + 3, y + h * light_y + 3],
                       fill=light_col)
    canvas.arc([x - w * 0.10, y + h * 0.52, x + w * 0.70, y + h * 1.10],
               300, 60, fill=(200, 200, 210), width=4)
    canvas.rectangle([x + w * 0.58, y + h * 0.74, x + w * 0.86, y + h * 0.84],
                     fill=(178, 34, 34))
    canvas.ellipse([x + w * 0.62, y + h * 0.84, x + w * 0.68, y + h * 0.90],
                   fill=(18, 22, 30))
    canvas.ellipse([x + w * 0.78, y + h * 0.84, x + w * 0.84, y + h * 0.90],
                   fill=(18, 22, 30))
    canvas.rectangle([x + w * 0.60, y + h * 0.70, x + w * 0.72, y + h * 0.75],
                     fill=(120, 160, 200))


PANELS = [
    (panel_kyiv_bridge, "Kyiv bridges hit in the overnight barrage"),
    (panel_poland_patrol, "Russian missiles land in Poland"),
    (panel_summit_table, "Trump defends Putin and Xi after summit"),
    (panel_scales_court, "World Court finds Myanmar guilty"),
    (panel_fall_chart, "AI rout: Nasdaq dives 5.3%"),
    (panel_riyadh_skyline, "Houthi missiles aimed at Riyadh shot down"),
    (panel_mercury_orbit, "BepiColombo reaches Mercury orbit"),
    (panel_race_circuit, "Russell tops dry Las Vegas FP3"),
]

PANEL_BG = [
    (222, 232, 240), (240, 226, 216), (226, 238, 226), (238, 228, 240),
    (232, 238, 240), (240, 236, 214), (236, 226, 232), (224, 234, 232),
]


# ---------- page assembly ----------
MARGIN = 28
COL_W = 304
COL_GAP = 16
COL_X = [MARGIN, MARGIN + COL_W + COL_GAP, MARGIN + 2 * (COL_W + COL_GAP)]
COL_TOP = 478
COL_BOTTOM = 826


def draw_masthead(canvas):
    canvas.rectangle([0, 0, W, 88], fill=NAVY)
    canvas.text((MARGIN, 14), "THE WORLD IN ONE DAY",
                font=load_font("serif_b", 44), fill=(255, 255, 255))
    for row_y, label, typeface, colour in (
            (20, "SATURDAY", load_font("sans_b", 20), (255, 255, 255)),
            (46, "21 NOVEMBER 2026", load_font("sans_b", 20),
             (232, 196, 90))):
        tw = canvas.textlength(label, font=typeface)
        canvas.text((W - MARGIN - tw, row_y), label, font=typeface,
                    fill=colour)
    canvas.rectangle([0, 88, W, 92], fill=RED)
    canvas.text((MARGIN, 98),
                "38 verified stories from six continents \u2014 8 illustrated \u2014 "
                "every headline below happened, or was first reported, on "
                "Saturday 21 November 2026.",
                font=load_font("serif", 12), fill=INK)


def draw_lead(canvas):
    lead_x, lead_y = MARGIN, 128
    lead_w = 568
    canvas.text((lead_x, lead_y), "LEAD \u2014 EUROPE",
                font=load_font("sans_b", 11), fill=RED)
    lead_y += 17
    lead_y = draw_lines(canvas, lead_x, lead_y,
                        "RUSSIA'S BIGGEST BARRAGE HITS KYIV \u2014 "
                        "AND LANDS IN POLAND",
                        load_font("serif_b", 34), lead_w, INK, leading=36)
    lead_y = draw_lines(canvas, lead_x, lead_y + 2,
                        "More than 400 drones and 110 missiles pound Ukraine "
                        "overnight; three Kyiv bridges hit, eight killed. Two "
                        "missiles fall in Poland as NATO jets scramble.",
                        load_font("sans", 13), lead_w, BODY, leading=16)
    lead_y += 6
    canvas.line([(lead_x, lead_y), (lead_x + lead_w, lead_y)], fill=FAINT,
                width=1)
    lead_y += 8
    lead_y = draw_lines(canvas, lead_x, lead_y, "AI ROUT: NASDAQ DIVES 5.3%",
                        load_font("serif_b", 21), lead_w, INK, leading=23)
    draw_lines(canvas, lead_x, lead_y + 1,
               "S&P 500 falls 3.7% into correction; Nvidia -14% and "
               "Anthropic -9% a day after its record debut.",
               load_font("sans", 11), lead_w, BODY, leading=13)


def draw_map_section(canvas):
    map_x, map_y = 612, 128
    map_w = W - MARGIN - map_x
    canvas.text((map_x, map_y), "THE WORLD \u2014 12 STORIES ON THE MAP",
                font=load_font("sans_b", 11), fill=NAVY2)
    draw_map(canvas, map_x, map_y + 18, map_w, 140)
    draw_pin_key(canvas, map_x, map_y + 166, map_w)


def draw_picture_strip(canvas):
    strip_y = 350
    canvas.text((MARGIN, strip_y),
                "THE DAY IN PICTURES \u2014 8 STORIES, DRAWN",
                font=load_font("sans_b", 11), fill=NAVY2)
    canvas.line([(MARGIN + 300, strip_y + 7), (W - MARGIN, strip_y + 7)],
                fill=FAINT, width=1)
    panel_w = (W - 2 * MARGIN - 7 * 8) // 8
    for i, (painter, cap) in enumerate(PANELS):
        panel_x = MARGIN + i * (panel_w + 8)
        canvas.rectangle([panel_x, strip_y + 18, panel_x + panel_w,
                          strip_y + 18 + 70], fill=PANEL_BG[i],
                         outline=(180, 178, 170), width=1)
        painter(canvas, panel_x + 1, strip_y + 19, panel_w - 2, 68)
        draw_lines(canvas, panel_x, strip_y + 92, cap,
                   load_font("sans", 8), panel_w, INK, leading=10)


def draw_story_columns(canvas, cols, total):
    drawn = 0
    for i, stories in enumerate(cols):
        x = COL_X[i]
        y = COL_TOP
        for story in stories:
            y = draw_story(canvas, x, y, story, COL_W)
            drawn += 1
            assert y <= COL_BOTTOM, "column %d overflow at %s" % (i, story["head"])
        if i < 2:
            canvas.line([(x + COL_W + 8, COL_TOP),
                         (x + COL_W + 8, COL_BOTTOM)], fill=FAINT, width=1)
    assert drawn == total, "drew %d of %d" % (drawn, total)


def draw_briefs(canvas):
    brief_y = 836
    canvas.text((MARGIN, brief_y), "ALSO IN BRIEF",
                font=load_font("sans_b", 10), fill=NAVY2)
    canvas.line([(MARGIN + 110, brief_y + 7), (W - MARGIN, brief_y + 7)],
                fill=FAINT, width=1)
    brief_w = (W - 2 * MARGIN - 3 * 24) // 4
    for i, (lead, text) in enumerate(BRIEFS):
        cell_x = MARGIN + (i % 4) * (brief_w + 24)
        cell_y = brief_y + 16 + (i // 4) * 38
        cell_y = draw_lines(canvas, cell_x, cell_y, lead,
                            load_font("sans_b", 10), brief_w, INK, leading=12)
        draw_lines(canvas, cell_x, cell_y + 1, text, load_font("sans", 9),
                   brief_w, BODY, leading=11)


def draw_figures(canvas):
    figures_y = 924
    canvas.rectangle([MARGIN, figures_y, W - MARGIN, figures_y + 48],
                     fill=NAVY)
    figure_w = (W - 2 * MARGIN) // 4
    for i, (num, label) in enumerate(FIGURES):
        x = MARGIN + i * figure_w + 12
        canvas.text((x, figures_y + 5), num, font=load_font("serif_b", 18),
                    fill=(232, 196, 90))
        canvas.text((x, figures_y + 28), label, font=load_font("sans", 10),
                    fill=(255, 255, 255))
        if i:
            canvas.line([(MARGIN + i * figure_w, figures_y + 8),
                         (MARGIN + i * figure_w, figures_y + 40)],
                        fill=(60, 90, 130), width=1)


def draw_footer(canvas):
    canvas.text((MARGIN, 984),
                "THE WORLD IN ONE DAY \u2014 Saturday 21 November 2026 \u00b7 "
                "38 stories \u00b7 six continents \u00b7 markets: Nasdaq -5.3%, "
                "S&P -3.7% into correction; Brent settles $92.57; GTA VI "
                "takes $3.8bn on day one",
                font=load_font("sans", 10), fill=GREY)


def main():
    hero_stories = [s for s in STORIES if s.get("pictured")]
    column_stories = [s for s in STORIES if not s.get("pictured")]
    assert len(hero_stories) == 8, len(hero_stories)
    assert len(column_stories) == 22, len(column_stories)
    assert len(BRIEFS) == 8 and len(FIGURES) == 4

    img = Image.new("RGB", (W, H), PAPER)
    canvas = ImageDraw.Draw(img)

    # ---- masthead ----
    draw_masthead(canvas)
    # ---- lead (left) ----
    draw_lead(canvas)
    # ---- map (right) ----
    draw_map_section(canvas)
    # ---- the day in pictures ----
    draw_picture_strip(canvas)

    # ---- story columns, balanced by measured height ----
    heights = [story_block_height(canvas, s, COL_W) for s in column_stories]
    cols, col_h = [[], [], []], [0, 0, 0]
    for story, h in zip(column_stories, heights):
        i = min(range(3), key=lambda k: col_h[k])
        cols[i].append(story)
        col_h[i] += h
    draw_story_columns(canvas, cols, len(column_stories))

    # ---- also in brief ----
    draw_briefs(canvas)
    # ---- day in figures ----
    draw_figures(canvas)
    # ---- footer ----
    draw_footer(canvas)

    out = os.path.join(HERE, "entry.png")
    img.save(out, "PNG", optimize=True)
    size = os.path.getsize(out)
    print("wrote %s %d bytes (limit 1048576)" % (out, size))
    assert size <= 1048576, "entry.png over 1 MiB"


if __name__ == "__main__":
    main()
