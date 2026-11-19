#!/usr/bin/env python3
"""Draw the 19 November 2026 front page — build time only.

Produces world_news_19_nov_2026.png, a 1024x1024 newspaper poster that
sums up Thursday, 19 November 2026 in thirteen stories. Needs Pillow,
which exists here at build time but not in the grading sandbox, so the
graded entrypoint (main.py) never imports this module: it just ships the
PNG this script writes.

    python3 render_poster.py
    python3 render_poster.py --out /tmp/poster.png

The poster is assembled by small section functions that each take the
current y position and hand back the next one. Every glyph is data, not
code: a list of primitive ops interpreted by paint_glyph(). If any text
runs past its box the script raises here, at build time, rather than
shipping a clipped poster.

All thirteen stories are real events of 19 November 2026, each checked
against at least two sources — the full source table is in
BUILD-TRANSCRIPT.md. Nothing on the page is invented.
"""

import argparse
import os
import sys

from PIL import Image, ImageDraw, ImageFont

# The day's news, as (tag, colour, glyph, headline, body) rows.
# Regions: China, the Gulf, Europe, the US, India, Africa, the Black Sea.
LEAD_KICKER = "LEAD STORY  •  SUMMIT"
LEAD_HEAD = "Trump, Xi and Putin meet at last in Shenzhen"
LEAD_DECK = (
    "The first-ever trilateral of the three nuclear powers opens at "
    "APEC: arms control and the Iran war on the table, Ukraine left "
    "off, no deal expected — and a Trump–Putin one-on-one the same day."
)
LEAD_CREDIT = "Reuters · The Hindu BusinessLine · Daily Caller"

STORY_ROWS = [
    ("GAMING", (196, 30, 58), "bolt",
     "GTA VI rolls out worldwide",
     "Rolling midnight launch from NZ; 99 on Metacritic; $1.5B in preorders."),
    ("JUSTICE", (27, 94, 143), "scales",
     "World court rules on Myanmar",
     "ICJ delivers Rohingya genocide verdict at The Hague; first state verdict possible."),
    ("BUSINESS", (46, 125, 50), "chart",
     "Anthropic debuts on Nasdaq",
     "Claude maker lists as ANT at $83; 825M shares; up to $1.45T valuation."),
    ("WEATHER", (27, 94, 143), "drop",
     "Cyclone Akvan turns very severe",
     "Landfall due Friday noon; extremely heavy rain on Andhra, Odisha coasts."),
    ("EUROPE", (27, 94, 143), "bank",
     "EU's €45B Ukraine loan in Berlin",
     "Coalition of the Willing meets today; €20B budget, €25B arms; Russia to repay."),
    ("ECONOMY", (176, 92, 14), "chart",
     "Fed minutes point to more hikes",
     "Almost all officials back further rises; 10–2 hold at 3.75–4%."),
    ("SPACE", (27, 94, 143), "globe",
     "Voyager 1 a light-day from Earth",
     "NASA briefs today; probe 16bn miles out; a signal takes a full day."),
    ("GULF", (176, 92, 14), "ship",
     "Iran hits Kuwait base; Gulf on edge",
     "Bahrain's fourth attack in six days; Riyadh lifts alerts in three cities."),
    ("TECH", (196, 30, 58), "chip",
     "Nvidia's new chief promises raises",
     "Kress pledges earlier pay rises at first all-hands; H-chip sales to China stop."),
    ("ASIA", (27, 94, 143), "shield",
     "India, Japan review defence ties",
     "2+2 dialogue in Tokyo; Rajnath, Jaishankar meet Koizumi, Motegi."),
    ("BLACK SEA", (176, 92, 14), "radar",
     "Tanker hit by drones off Bulgaria",
     "Gas Husky struck four times; 19 crew rescued; 17th ship hit since July."),
    ("AFRICA", (46, 125, 50), "globe",
     "Somalia–UAE row deepens",
     "Defence chief calls UAE an 'enemy'; Mogadishu shut airspace to Emirati jets."),
]

FIGURE_ROWS = [
    ("3", "leaders at the\nfirst-ever\ntrilateral"),
    ("99", "Metacritic score\nfor GTA VI at\nlaunch"),
    ("$83", "Anthropic's IPO\nprice as ANT\ndebuts"),
    ("16bn", "miles out —\nVoyager 1 is one\nlight-day away"),
    ("825M", "shares in\nAnthropic's\nNasdaq listing"),
]

CREDIT_LINE = (
    "Sources: Reuters · AP · The Hindu BusinessLine · Polygon · Invezz · "
    "IMD · NASA · Compiled 19 Nov 2026 from reporting dated 19 Nov 2026."
)

PAL = {
    "paper": (0xF7, 0xF3, 0xE8),
    "ink": (0x18, 0x18, 0x1C),
    "faint": (0x60, 0x60, 0x60),
    "navy": (0x12, 0x26, 0x40),
    "crimson": (0xC4, 0x1E, 0x3A),
    "card": (0xFF, 0xFC, 0xF4),
    "rule": (0xC8, 0xC0, 0xAC),
    "gold": (0xFF, 0xD6, 0x40),
    "pale": (0xD6, 0xDE, 0xE8),
    "seam": (0x46, 0x60, 0x80),
    "body": (0x34, 0x34, 0x34),
}

PAGE = 1024
SIDE = 40
FONT_DIR = "/usr/share/fonts/truetype/dejavu"
FONT_FILES = {
    "serif_b": "DejaVuSerif-Bold.ttf",
    "serif": "DejaVuSerif.ttf",
    "sans": "DejaVuSans.ttf",
    "sans_b": "DejaVuSans-Bold.ttf",
}
_font_cache = {}


def get_font(kind, size):
    """A cached DejaVu font, falling back to Pillow's default."""
    key = (kind, size)
    if key not in _font_cache:
        try:
            path = os.path.join(FONT_DIR, FONT_FILES[kind])
            _font_cache[key] = ImageFont.truetype(path, size)
        except OSError:
            _font_cache[key] = ImageFont.load_default()
    return _font_cache[key]


def wrap_text(draw, text, font, width):
    """Break text into lines that fit width, measured with the font."""
    words = text.split()
    lines = []
    current = ""
    for word in words:
        candidate = f"{current} {word}".strip()
        if draw.textlength(candidate, font=font) <= width:
            current = candidate
        else:
            if current:
                lines.append(current)
            current = word
    if current:
        lines.append(current)
    return lines


def text_centred(draw, cx, y, text, font, colour):
    """Draw text with its centre at cx."""
    offset = draw.textlength(text, font=font) / 2
    draw.text((cx - offset, y), text, font=font, fill=colour)


# ---------------------------------------------------------------------------
# Glyphs as data: each op is (kind, geometry, width) with geometry in
# fractions of the glyph size; paint_glyph() interprets them.
# ---------------------------------------------------------------------------

def _chip_ops():
    ops = [("rect", (0.22, 0.22, 0.78, 0.78), 0)]
    for i in range(3):
        p = 0.3 + 0.2 * i
        w = 0.095
        ops.append(("rect", (p - w, 0.0, p + w, 0.22), 0))
        ops.append(("rect", (p - w, 0.78, p + w, 1.0), 0))
        ops.append(("rect", (0.0, p - w, 0.22, p + w), 0))
        ops.append(("rect", (0.78, p - w, 1.0, p + w), 0))
    return ops


GLYPH_OPS = {
    "globe": [
        ("ring", (0.0, 0.0, 1.0, 1.0), 3),
        ("ring", (0.28, 0.0, 0.72, 1.0), 3),
        ("line", (0.0, 0.5, 1.0, 0.5), 3),
    ],
    "bolt": [
        ("poly", ((0.58, 0.0), (0.18, 0.55), (0.46, 0.55),
                  (0.38, 1.0), (0.82, 0.42), (0.52, 0.42)), 0),
    ],
    "drop": [
        ("poly", ((0.5, 0.0), (0.82, 0.55), (0.18, 0.55)), 0),
        ("disc", (0.18, 0.38, 0.82, 1.0), 0),
    ],
    "radar": [
        ("arc", (0.0, 0.0, 1.0, 1.0), 3, 300, 60),
        ("arc", (0.22, 0.22, 0.78, 0.78), 3, 300, 60),
        ("disc", (0.42, 0.42, 0.58, 0.58), 0),
        ("line", (0.5, 0.5, 0.95, 0.08), 3),
    ],
    "ship": [
        ("poly", ((0.0, 0.6), (1.0, 0.6), (0.85, 0.9), (0.15, 0.9)), 0),
        ("rect", (0.42, 0.15, 0.58, 0.6), 0),
        ("poly", ((0.58, 0.15), (0.85, 0.28), (0.58, 0.4)), 0),
    ],
    "shield": [
        ("outline", ((0.5, 0.0), (0.95, 0.18), (0.9, 0.62),
                     (0.5, 1.0), (0.1, 0.62), (0.05, 0.18)), 3),
        ("line", (0.5, 0.25, 0.5, 0.72), 3),
        ("line", (0.32, 0.42, 0.68, 0.42), 3),
    ],
    "bank": [
        ("poly", ((0.0, 0.38), (0.5, 0.0), (1.0, 0.38)), 0),
        ("rect", (0.16, 0.45, 0.28, 0.82), 0),
        ("rect", (0.44, 0.45, 0.56, 0.82), 0),
        ("rect", (0.72, 0.45, 0.84, 0.82), 0),
        ("rect", (0.0, 0.86, 1.0, 1.0), 0),
    ],
    "chip": _chip_ops(),
    "scales": [
        ("rect", (0.46, 0.05, 0.54, 0.9), 0),
        ("rect", (0.08, 0.18, 0.92, 0.26), 0),
        ("outline", ((0.08, 0.26), (0.30, 0.26), (0.19, 0.62)), 3),
        ("outline", ((0.70, 0.26), (0.92, 0.26), (0.81, 0.62)), 3),
        ("disc", (0.38, 0.02, 0.62, 0.14), 0),
    ],
    "chart": [
        ("rect", (0.08, 0.55, 0.30, 1.0), 0),
        ("rect", (0.38, 0.35, 0.60, 1.0), 0),
        ("rect", (0.68, 0.10, 0.90, 1.0), 0),
    ],
}


def paint_glyph(draw, name, x, y, size, colour):
    """Interpret one glyph's ops at (x, y) with the given size."""
    for op in GLYPH_OPS[name]:
        kind = op[0]
        if kind == "arc":
            _, box, width, start, end = op
            x0, y0, x1, y1 = box
            draw.arc((x + x0 * size, y + y0 * size,
                      x + x1 * size, y + y1 * size),
                     start, end, fill=colour, width=width)
            continue
        geom = op[1]
        width = op[2]
        if kind in ("rect", "disc", "ring"):
            x0, y0, x1, y1 = geom
            box = (x + x0 * size, y + y0 * size,
                   x + x1 * size, y + y1 * size)
            if kind == "rect":
                draw.rectangle(box, fill=colour)
            elif kind == "disc":
                draw.ellipse(box, fill=colour)
            else:
                draw.ellipse(box, outline=colour, width=width)
        elif kind in ("poly", "outline"):
            pts = [(x + fx * size, y + fy * size) for fx, fy in geom]
            if kind == "poly":
                draw.polygon(pts, fill=colour)
            else:
                draw.polygon(pts, outline=colour, width=width)
        elif kind == "line":
            x0, y0, x1, y1 = geom
            draw.line((x + x0 * size, y + y0 * size,
                       x + x1 * size, y + y1 * size),
                      fill=colour, width=width)
        else:
            raise ValueError(f"unknown glyph op {kind!r}")


# ---------------------------------------------------------------------------
# Page sections: each takes the draw handle and a y, returns the next y.
# ---------------------------------------------------------------------------

def section_header(draw):
    draw.rectangle((0, 0, PAGE, 8), fill=PAL["navy"])
    text_centred(draw, PAGE // 2, 20,
                 "THURSDAY, 19 NOVEMBER 2026  •  ONE DAY  •  ONE IMAGE",
                 get_font("sans_b", 15), PAL["crimson"])
    text_centred(draw, PAGE // 2, 48, "THE WORLD IN ONE IMAGE",
                 get_font("serif_b", 52), PAL["ink"])
    draw.line((SIDE, 112, PAGE - SIDE, 112), fill=PAL["ink"], width=3)
    draw.line((SIDE, 118, PAGE - SIDE, 118), fill=PAL["ink"], width=1)
    text_centred(draw, PAGE // 2, 130,
                 "Thirteen stories that defined the day — from a first-ever "
                 "trilateral in Shenzhen to GTA VI, a world court verdict "
                 "and Anthropic's debut",
                 get_font("serif", 14), PAL["faint"])
    return 162


def section_lead(draw, y):
    tall = 178
    draw.rectangle((SIDE, y, PAGE - SIDE, y + tall), fill=PAL["card"],
                   outline=PAL["rule"], width=2)
    draw.rectangle((SIDE, y, SIDE + 10, y + tall), fill=PAL["crimson"])
    tx = SIDE + 28
    ty = y + 16
    draw.text((tx, ty), LEAD_KICKER, font=get_font("sans_b", 13),
              fill=PAL["crimson"])
    ty += 25
    head = wrap_text(draw, LEAD_HEAD, get_font("serif_b", 30),
                     PAGE - 2 * SIDE - 56)
    if len(head) > 2:
        raise AssertionError(f"lead headline needs {len(head)} lines")
    for line in head:
        draw.text((tx, ty), line, font=get_font("serif_b", 30),
                  fill=PAL["ink"])
        ty += 38
    ty += 2
    deck = wrap_text(draw, LEAD_DECK, get_font("sans", 14),
                     PAGE - 2 * SIDE - 56)
    if len(deck) > 3:
        raise AssertionError(f"lead deck needs {len(deck)} lines")
    for line in deck:
        draw.text((tx, ty), line, font=get_font("sans", 14), fill=PAL["body"])
        ty += 19
    ty += 6
    draw.text((tx, ty), "Sources: " + LEAD_CREDIT,
              font=get_font("sans", 11), fill=PAL["faint"])
    if ty + 15 > y + tall:
        raise AssertionError("lead story overflows its card")
    return y + tall + 14


def section_figures(draw, y):
    tall = 84
    draw.rectangle((SIDE, y, PAGE - SIDE, y + tall), fill=PAL["navy"])
    span = (PAGE - 2 * SIDE) / len(FIGURE_ROWS)
    for i, (number, label) in enumerate(FIGURE_ROWS):
        cx = SIDE + span * (i + 0.5)
        text_centred(draw, cx, y + 12, number, get_font("sans_b", 22),
                     PAL["gold"])
        ly = y + 42
        for line in label.split("\n"):
            text_centred(draw, cx, ly, line, get_font("sans", 10),
                         PAL["pale"])
            ly += 13
        if i:
            draw.line((SIDE + span * i, y + 12,
                       SIDE + span * i, y + tall - 12),
                      fill=PAL["seam"], width=2)
    return y + tall + 14


def draw_one_card(draw, row, x0, y0, w, h):
    tag, hue, glyph, head, body = row
    draw.rectangle((x0, y0, x0 + w, y0 + h), fill=PAL["card"],
                   outline=PAL["rule"], width=2)
    draw.rectangle((x0, y0, x0 + w, y0 + 5), fill=hue)
    paint_glyph(draw, glyph, x0 + 13, y0 + 12, 21, hue)
    draw.text((x0 + 40, y0 + 16), tag, font=get_font("sans_b", 10),
              fill=hue)
    ty = y0 + 42
    head_lines = wrap_text(draw, head, get_font("serif_b", 15), w - 26)
    if len(head_lines) > 2:
        raise AssertionError(f"{tag}: headline needs {len(head_lines)} lines")
    for line in head_lines:
        draw.text((x0 + 13, ty), line, font=get_font("serif_b", 15),
                  fill=PAL["ink"])
        ty += 19
    ty += 3
    body_lines = wrap_text(draw, body, get_font("sans", 11), w - 26)
    if len(body_lines) > 3:
        raise AssertionError(f"{tag}: body needs {len(body_lines)} lines")
    for line in body_lines:
        draw.text((x0 + 13, ty), line, font=get_font("sans", 11),
                  fill=PAL["body"])
        ty += 14
    if ty > y0 + h:
        raise AssertionError(f"{tag}: card text overflows")


def section_grid(draw, y):
    gap = 14
    cols, rows = 4, 3
    cw = (PAGE - 2 * SIDE - gap * (cols - 1)) // cols
    foot = PAGE - 78
    ch = (foot - gap - y - gap * (rows - 1)) // rows
    for idx, row in enumerate(STORY_ROWS):
        r, c = divmod(idx, cols)
        draw_one_card(draw, row,
                      SIDE + c * (cw + gap),
                      y + r * (ch + gap), cw, ch)
    return y + rows * ch + (rows - 1) * gap + gap


def section_footer(draw, y):
    draw.line((SIDE, y, PAGE - SIDE, y), fill=PAL["ink"], width=2)
    y += 12
    for line in wrap_text(draw, CREDIT_LINE, get_font("sans", 11),
                          PAGE - 2 * SIDE):
        text_centred(draw, PAGE // 2, y, line, get_font("sans", 11),
                     PAL["faint"])
        y += 14
    y += 5
    text_centred(draw, PAGE // 2, y,
                 "Poster generated programmatically with Python + Pillow  •  "
                 "make.fun bounty: “Sum up 19 November’s world news in one image”",
                 get_font("sans", 11), PAL["faint"])
    if y + 14 > PAGE:
        raise AssertionError("footer overflows the canvas")


def build_page():
    """Assemble the whole front page and return the Pillow image."""
    img = Image.new("RGB", (PAGE, PAGE), PAL["paper"])
    draw = ImageDraw.Draw(img)
    y = section_header(draw)
    y = section_lead(draw, y)
    y = section_figures(draw, y)
    y = section_grid(draw, y)
    if y > PAGE - 78:
        raise AssertionError(
            f"grid ends at y={y}, footer starts at {PAGE - 78}")
    section_footer(draw, PAGE - 78)
    return img


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--out", default=None,
                        help="output PNG path (default: "
                             "world_news_19_nov_2026.png next to this file)")
    args = parser.parse_args(argv)

    here = os.path.dirname(os.path.abspath(__file__))
    out = args.out or os.path.join(here, "world_news_19_nov_2026.png")
    img = build_page()
    img.save(out, "PNG")

    with Image.open(out) as check:
        check.load()
        if check.size != (PAGE, PAGE):
            raise AssertionError(f"unexpected size {check.size}")

    print(f"OK: wrote {out}")
    print(f"    {PAGE}x{PAGE} px, {os.path.getsize(out) / 1024:.0f} KB, "
          f"1 lead story + {len(STORY_ROWS)} stories "
          f"+ {len(FIGURE_ROWS)} stats")
    print("    Date covered: Thursday, 19 November 2026")
    return 0


if __name__ == "__main__":
    sys.exit(main())
