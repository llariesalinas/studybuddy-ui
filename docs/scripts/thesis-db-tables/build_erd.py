# -*- coding: utf-8 -*-
"""Render the StudyBuddy ERD: all 35 tables, every field, for a full-page landscape figure.

Draws directly with Pillow (no Graphviz/Mermaid needed, nothing downloaded). Output is a 300 DPI
PNG sized for a landscape page, so it stays sharp when zoomed on screen.

Layout: boxes are grouped by the same nine modules used in the table section, packed into columns
in that order. Foreign keys are drawn as orthogonal polylines routed through the column gutters,
with crow's-foot notation at the child (many) end and a bar at the parent (one) end.
"""
import re

from PIL import Image, ImageDraw, ImageFont

from tables_data import BLOCKS

OUT = "erd_studybuddy.png"

# --- page geometry ---------------------------------------------------------------------
DPI = 300
PAGE_W_IN, PAGE_H_IN = 9.5, 6.5          # usable area of a landscape Letter page
W, H = int(PAGE_W_IN * DPI), int(PAGE_H_IN * DPI)

MARGIN = 26
COLUMNS = 6
COL_GUTTER = 58
BOX_GAP = 16

FONT_SIZE = 20
HEADER_SIZE = 22
TITLE_SIZE = 46
LEGEND_SIZE = 22

# Tight leading: keeps the text at a legible size while fitting the page height.
ROW_H = int(FONT_SIZE * 1.34)
HEADER_H = int(HEADER_SIZE * 1.62)
PAD_X = 10

FONT_DIR = r"C:\Windows\Fonts"
F_REG = ImageFont.truetype(FONT_DIR + r"\arial.ttf", FONT_SIZE)
F_BOLD = ImageFont.truetype(FONT_DIR + r"\arialbd.ttf", HEADER_SIZE)
F_TITLE = ImageFont.truetype(FONT_DIR + r"\arialbd.ttf", TITLE_SIZE)
F_LEGEND = ImageFont.truetype(FONT_DIR + r"\arial.ttf", LEGEND_SIZE)
F_LEGEND_B = ImageFont.truetype(FONT_DIR + r"\arialbd.ttf", LEGEND_SIZE)

# --- modules ---------------------------------------------------------------------------
# (label, first block index, last block index, header fill, body fill)
MODULES = [
    ("Identity and Authentication", 1, 7,   (196, 214, 240), (243, 247, 253)),
    ("Academic Taxonomy",           8, 10,  (201, 228, 206), (244, 250, 245)),
    ("Tutor Profile",              11, 14,  (214, 205, 234), (248, 246, 253)),
    ("Scheduling",                 15, 16,  (183, 222, 227), (241, 250, 251)),
    ("Bookings and Sessions",      17, 19,  (247, 214, 181), (254, 247, 240)),
    ("Payments and Wallet",        20, 25,  (245, 205, 213), (253, 244, 247)),
    ("Verification",               26, 29,  (226, 219, 191), (251, 249, 242)),
    ("Communication",              30, 33,  (205, 224, 240), (245, 250, 254)),
    ("System Records",             34, 35,  (219, 219, 219), (249, 249, 249)),
]

LINE = (95, 105, 120)
TEXT = (26, 30, 38)
MUTED = (96, 104, 118)
EDGE = (128, 140, 158)
EDGE_HL = (150, 120, 150)

# --- type abbreviations, so boxes stay narrow ------------------------------------------
def abbrev(t):
    t = t.strip()
    pk = "(PK)" in t
    base = t.replace("(PK)", "").strip()
    m = re.match(r"Varchar\((\d+)\)", base)
    if m:
        base = "VC(%s)" % m.group(1)
    else:
        base = {
            "Int": "INT", "Datetime": "DT", "Date": "DATE", "Time": "TIME",
            "Boolean": "BOOL", "Text": "TEXT", "Image": "IMG", "File": "FILE",
            "UUID": "UUID", "Float": "FLOAT", "JSON": "JSON", "FK": "FK",
        }.get(base, base)
        base = re.sub(r"Decimal\(\d+,\d+\)", "DEC", base)
    if pk:
        base = (base + " PK").strip()
    return base


def base_name(n):
    return n.split(" (")[0].strip()


NAME_TO_IDX = {base_name(b["name"]): i for i, b in enumerate(BLOCKS)}


def module_of(i):
    for label, lo, hi, hdr, body in MODULES:
        if lo - 1 <= i <= hi - 1:
            return label, hdr, body
    raise KeyError(i)


# --- measure ---------------------------------------------------------------------------
probe = ImageDraw.Draw(Image.new("RGB", (10, 10)))


def tw(text, font):
    return probe.textlength(text, font=font)


boxes = []
for i, b in enumerate(BLOCKS):
    label, hdr, body = module_of(i)
    fields = [(r[0], abbrev(r[1])) for r in b["rows"]]
    name_w = max([tw(f, F_REG) for f, _ in fields] + [tw(base_name(b["name"]), F_BOLD)])
    type_w = max(tw(t, F_REG) for _, t in fields)
    w = int(name_w + type_w + PAD_X * 3 + 16)  # +16 leaves room for the key marker
    h = HEADER_H + ROW_H * len(fields) + 6
    boxes.append(dict(idx=i, name=base_name(b["name"]), fields=fields, w=w, h=h,
                      hdr=hdr, body=body, module=label,
                      pk_fields={r[0] for r in b["rows"] if "PK" in r[1]},
                      fk_fields={fk.split("->")[0].strip() for fk in b["fks"]}))

BOX_W = max(b["w"] for b in boxes)
avail_w = W - 2 * MARGIN
BOX_W = min(BOX_W, (avail_w - COL_GUTTER * (COLUMNS - 1)) // COLUMNS)

TOP = MARGIN + TITLE_SIZE + 30
BOTTOM_LEGEND = 58
usable_h = H - TOP - MARGIN - BOTTOM_LEGEND

# --- pack into columns, keeping module order -------------------------------------------
# Linear partition (DP): split the ordered box list into COLUMNS contiguous runs so that the
# tallest column is as short as possible. Greedy left-to-right filling dumps the remainder into
# the last column, which overflows the page; this balances them instead.
def partition(items, k):
    n = len(items)
    hs = [b["h"] + BOX_GAP for b in items]
    pre = [0] * (n + 1)
    for i, v in enumerate(hs):
        pre[i + 1] = pre[i] + v

    INF = float("inf")
    best = [[INF] * (k + 1) for _ in range(n + 1)]
    cut = [[0] * (k + 1) for _ in range(n + 1)]
    best[0][0] = 0
    for i in range(1, n + 1):
        for j in range(1, k + 1):
            for m in range(j - 1, i):
                cost = max(best[m][j - 1], pre[i] - pre[m])
                if cost < best[i][j]:
                    best[i][j] = cost
                    cut[i][j] = m
    groups, i = [], n
    for j in range(k, 0, -1):
        m = cut[i][j]
        groups.append(items[m:i])
        i = m
    return list(reversed(groups))


cols = partition(boxes, COLUMNS)
col_h = [sum(b["h"] + BOX_GAP for b in col) for col in cols]
overflow = [i for i, h in enumerate(col_h) if h > usable_h]

for ci, col in enumerate(cols):
    x = MARGIN + ci * (BOX_W + COL_GUTTER)
    y = TOP
    for b in col:
        b["x"], b["y"] = x, y
        y += b["h"] + BOX_GAP

print("box width=%d  usable_h=%d" % (BOX_W, usable_h))
for ci, h in enumerate(col_h):
    print("  column %d: %2d boxes, height %d%s"
          % (ci + 1, len(cols[ci]), h, "   OVERFLOW" if h > usable_h else ""))

# --- draw ------------------------------------------------------------------------------
img = Image.new("RGB", (W, H), (255, 255, 255))
d = ImageDraw.Draw(img)

# Relationship lines are composited on top of the boxes at partial opacity. Routing them
# underneath hides every edge that has to cross an intervening column, which at six columns is
# most of them; drawing them over the boxes keeps all 58 visible without obscuring field text.
overlay = Image.new("RGBA", (W, H), (0, 0, 0, 0))
od = ImageDraw.Draw(overlay)

d.text((MARGIN, MARGIN - 4), "StudyBuddy \u2014 Entity-Relationship Diagram", font=F_TITLE, fill=TEXT)
sub = "35 tables  \u00b7  PostgreSQL (studybuddy_db)  \u00b7  PK = primary key, FK = foreign key"
d.text((MARGIN, MARGIN + TITLE_SIZE + 2), sub, font=F_LEGEND, fill=MUTED)


def row_y(b, field_name):
    for k, (f, _) in enumerate(b["fields"]):
        if f == field_name:
            return b["y"] + HEADER_H + ROW_H * k + ROW_H // 2
    return b["y"] + b["h"] // 2


MARK_W = 16


def key_marker(dr, cx, cy, filled):
    """Diamond key marker: filled = primary key, hollow = foreign key."""
    s = 5
    pts = [(cx, cy - s), (cx + s, cy), (cx, cy + s), (cx - s, cy)]
    dr.polygon(pts, fill=(60, 72, 94) if filled else (255, 255, 255),
               outline=(60, 72, 94))


def crowfoot(dr, x, y, direction, color):
    """Three prongs opening toward `direction` (-1 left, +1 right)."""
    s = 11
    dr.line([(x, y), (x + direction * s, y - s)], fill=color, width=2)
    dr.line([(x, y), (x + direction * s, y)], fill=color, width=2)
    dr.line([(x, y), (x + direction * s, y + s)], fill=color, width=2)


def onebar(dr, x, y, direction, color):
    s = 8
    dr.line([(x + direction * 5, y - s), (x + direction * 5, y + s)], fill=color, width=2)


# --- relationship edges ----------------------------------------------------------------
edges = []
for i, b in enumerate(BLOCKS):
    for fk in b["fks"]:
        if "->" not in fk:
            continue
        field, target = [p.strip() for p in fk.split("->")]
        j = NAME_TO_IDX.get(target)
        if j is None or j == i:
            continue
        edges.append((i, j, field))

by_idx = {b["idx"]: b for b in boxes}
gutter_use = {}

for i, j, field in edges:
    child, parent = by_idx[i], by_idx[j]
    cy = row_y(child, field)
    py = parent["y"] + HEADER_H // 2

    # exit the child on the side facing the parent
    if parent["x"] + parent["w"] / 2 < child["x"]:
        cx, cdir = child["x"], -1
    else:
        cx, cdir = child["x"] + BOX_W, 1
    if child["x"] < parent["x"]:
        px, pdir = parent["x"], -1
    else:
        px, pdir = parent["x"] + BOX_W, 1

    # route through the gutter next to the child, nudged so parallel edges separate
    gx = cx + cdir * (COL_GUTTER // 2)
    gx = max(MARGIN // 2, min(W - MARGIN // 2, gx))
    key = round(gx / 6)
    gutter_use[key] = gutter_use.get(key, 0) + 1
    gx += (gutter_use[key] % 5 - 2) * 5

    # Colour each edge by the parent's module so a reader can follow one thread among 58.
    base = tuple(int(v * 0.52) for v in parent["hdr"])
    color = base + (235,)
    pts = [(cx + cdir * 12, cy), (gx, cy), (gx, py), (px + pdir * 12, py)]
    od.line(pts, fill=color, width=2, joint="curve")
    crowfoot(od, cx + cdir * 12, cy, cdir, color)
    onebar(od, px + pdir * 12, py, pdir, color)

# --- edges go underneath, so no line ever cuts through field text -----------------------
img = Image.alpha_composite(img.convert("RGBA"), overlay).convert("RGB")
d = ImageDraw.Draw(img)

# --- boxes on top of the edges ---------------------------------------------------------
for b in boxes:
    x, y, h = b["x"], b["y"], b["h"]
    d.rectangle([x, y, x + BOX_W, y + h], fill=b["body"], outline=LINE, width=2)
    d.rectangle([x, y, x + BOX_W, y + HEADER_H], fill=b["hdr"], outline=LINE, width=2)
    d.text((x + PAD_X, y + (HEADER_H - HEADER_SIZE) // 2 - 1), b["name"], font=F_BOLD, fill=TEXT)

    for k, (fname, ftype) in enumerate(b["fields"]):
        ry = y + HEADER_H + ROW_H * k + 2
        is_pk = fname in b["pk_fields"]
        is_fk = fname in b["fk_fields"]
        # Drawn shapes, not glyphs: Arial renders U+25C6/U+25C7 as tofu here.
        if is_pk or is_fk:
            key_marker(d, x + PAD_X + 5, ry + FONT_SIZE // 2, filled=is_pk)
        d.text((x + PAD_X + MARK_W, ry), fname, font=F_REG,
               fill=TEXT if (is_pk or is_fk) else (58, 64, 76))
        d.text((x + BOX_W - PAD_X - tw(ftype, F_REG), ry), ftype, font=F_REG, fill=MUTED)
        if k:
            d.line([(x + 2, ry - 2), (x + BOX_W - 2, ry - 2)], fill=(226, 230, 238), width=1)

# --- legend ----------------------------------------------------------------------------
ly = H - MARGIN - 30
lx = MARGIN
d.text((lx, ly - 4), "Modules:", font=F_LEGEND_B, fill=TEXT)
lx += tw("Modules:", F_LEGEND_B) + 14
for label, lo, hi, hdr, body in MODULES:
    d.rectangle([lx, ly, lx + 20, ly + 20], fill=hdr, outline=LINE, width=1)
    d.text((lx + 26, ly - 1), label, font=F_LEGEND, fill=TEXT)
    lx += 26 + tw(label, F_LEGEND) + 26

ly2 = ly - 32
kx = MARGIN
key_marker(d, kx + 5, ly2 + LEGEND_SIZE // 2, filled=True)
d.text((kx + 18, ly2), "primary key", font=F_LEGEND, fill=MUTED)
kx += 18 + tw("primary key", F_LEGEND) + 26
key_marker(d, kx + 5, ly2 + LEGEND_SIZE // 2, filled=False)
d.text((kx + 18, ly2), "foreign key", font=F_LEGEND, fill=MUTED)
kx += 18 + tw("foreign key", F_LEGEND) + 26
d.text((kx, ly2), "crow's foot = many side, bar = one side", font=F_LEGEND, fill=MUTED)

img.save(OUT, dpi=(DPI, DPI))
print("wrote %s  %dx%d px  (%.2f x %.2f in at %d DPI)"
      % (OUT, W, H, W / DPI, H / DPI, DPI))
print("tables: %d   fields: %d   relationships drawn: %d"
      % (len(boxes), sum(len(b["fields"]) for b in boxes), len(edges)))
if overflow:
    print("WARNING: columns overflowing the page: %s" % [i + 1 for i in overflow])
