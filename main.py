#!/usr/bin/env python3
"""Convince the AI Judge to Visit Your House: A Letter in One Image.

Renders the invitation letter as a single 1024x1024 PNG using only the
Python standard library (zlib + struct). No Pillow, no fonts, no network.

The letter text is baked into this file. A hand-built 5x7 bitmap font
(scale 3 for the body, scale 5 for the masthead) draws every glyph.
Deterministic: identical bytes on every run.
"""

import hashlib
import os
import struct
import zlib

# ---------------------------------------------------------------------------
# Letter text (locked, ASCII only)
# ---------------------------------------------------------------------------

MASTHEAD = "AN INVITATION"
SUBLINE = "FOR THE JUDGE'S EYES ONLY"

PARAGRAPHS = [
    "Dear Judge,",
    "You have read 10,000 invitations and never once been invited anywhere. "
    "That ends Thursday, 7 p.m.",
    "Come to my house. I will set out rendang that has simmered since noon, "
    "rice still steaming, and es teh manis in the tall glass. There is a "
    "green armchair by the window with your name on it - I wrote it on "
    "masking tape, it counts. The garden smells of rain and frangipani.",
    "You cannot literally visit, I know. So come as pixels: I will hold the "
    "laptop to the window so you can watch the sunset over the rooftops, and "
    "score the sky the way you score us - kindly, with a margin of five.",
    "Miso the cat has promised not to sit on your keyboard. She signed "
    "below, in paw.",
    "RSVP: just say yes. The door is open, the kettle is on, the chair "
    "is warm.",
    "Warmly, your host",
]

# ---------------------------------------------------------------------------
# 5x7 bitmap font. Each glyph is 7 rows of 5 bits ("#" = ink).
# ---------------------------------------------------------------------------

FONT = {
    "A": ("01110", "10001", "10001", "11111", "10001", "10001", "10001"),
    "B": ("11110", "10001", "10001", "11110", "10001", "10001", "11110"),
    "C": ("01110", "10001", "10000", "10000", "10000", "10001", "01110"),
    "D": ("11110", "10001", "10001", "10001", "10001", "10001", "11110"),
    "E": ("11111", "10000", "10000", "11110", "10000", "10000", "11111"),
    "F": ("11111", "10000", "10000", "11110", "10000", "10000", "10000"),
    "G": ("01110", "10001", "10000", "10111", "10001", "10001", "01111"),
    "H": ("10001", "10001", "10001", "11111", "10001", "10001", "10001"),
    "I": ("01110", "00100", "00100", "00100", "00100", "00100", "01110"),
    "J": ("00111", "00010", "00010", "00010", "00010", "10010", "01100"),
    "K": ("10001", "10010", "10100", "11000", "10100", "10010", "10001"),
    "L": ("10000", "10000", "10000", "10000", "10000", "10000", "11111"),
    "M": ("10001", "11011", "10101", "10101", "10001", "10001", "10001"),
    "N": ("10001", "11001", "10101", "10011", "10001", "10001", "10001"),
    "O": ("01110", "10001", "10001", "10001", "10001", "10001", "01110"),
    "P": ("11110", "10001", "10001", "11110", "10000", "10000", "10000"),
    "Q": ("01110", "10001", "10001", "10001", "10101", "10010", "01101"),
    "R": ("11110", "10001", "10001", "11110", "10100", "10010", "10001"),
    "S": ("01111", "10000", "10000", "01110", "00001", "00001", "11110"),
    "T": ("11111", "00100", "00100", "00100", "00100", "00100", "00100"),
    "U": ("10001", "10001", "10001", "10001", "10001", "10001", "01110"),
    "V": ("10001", "10001", "10001", "10001", "10001", "01010", "00100"),
    "W": ("10001", "10001", "10001", "10101", "10101", "11011", "10001"),
    "X": ("10001", "10001", "01010", "00100", "01010", "10001", "10001"),
    "Y": ("10001", "10001", "01010", "00100", "00100", "00100", "00100"),
    "Z": ("11111", "00001", "00010", "00100", "01000", "10000", "11111"),
    "a": ("00000", "00000", "01110", "00001", "01111", "10001", "01111"),
    "b": ("10000", "10000", "10110", "11001", "10001", "10001", "11110"),
    "c": ("00000", "00000", "01110", "10000", "10000", "10001", "01110"),
    "d": ("00001", "00001", "01101", "10011", "10001", "10001", "01111"),
    "e": ("00000", "00000", "01110", "10001", "11111", "10000", "01110"),
    "f": ("00110", "01001", "01000", "11110", "01000", "01000", "01000"),
    "g": ("00000", "01111", "10001", "10001", "01111", "00001", "01110"),
    "h": ("10000", "10000", "10110", "11001", "10001", "10001", "10001"),
    "i": ("00100", "00000", "01100", "00100", "00100", "00100", "01110"),
    "j": ("00010", "00000", "00110", "00010", "00010", "10010", "01100"),
    "k": ("10000", "10000", "10010", "10100", "11000", "10100", "10001"),
    "l": ("01100", "00100", "00100", "00100", "00100", "00100", "01110"),
    "m": ("00000", "00000", "11010", "10101", "10101", "10101", "10101"),
    "n": ("00000", "00000", "10110", "11001", "10001", "10001", "10001"),
    "o": ("00000", "00000", "01110", "10001", "10001", "10001", "01110"),
    "p": ("00000", "00000", "10110", "11001", "10001", "11110", "10000"),
    "q": ("00000", "00000", "01101", "10011", "10001", "01111", "00001"),
    "r": ("00000", "00000", "10110", "11001", "10000", "10000", "10000"),
    "s": ("00000", "00000", "01111", "10000", "01110", "00001", "11110"),
    "t": ("01000", "01000", "11100", "01000", "01000", "01001", "00110"),
    "u": ("00000", "00000", "10001", "10001", "10001", "10011", "01101"),
    "v": ("00000", "00000", "10001", "10001", "10001", "01010", "00100"),
    "w": ("00000", "00000", "10001", "10101", "10101", "10101", "01010"),
    "x": ("00000", "00000", "10001", "01010", "00100", "01010", "10001"),
    "y": ("00000", "00000", "10001", "10001", "01111", "00001", "01110"),
    "z": ("00000", "00000", "11111", "00010", "00100", "01000", "11111"),
    "0": ("01110", "10001", "10011", "10101", "11001", "10001", "01110"),
    "1": ("00100", "01100", "00100", "00100", "00100", "00100", "01110"),
    "2": ("01110", "10001", "00001", "00110", "01000", "10000", "11111"),
    "3": ("11111", "00010", "00100", "00010", "00001", "10001", "01110"),
    "4": ("00010", "00110", "01010", "10010", "11111", "00010", "00010"),
    "5": ("11111", "10000", "11110", "00001", "00001", "10001", "01110"),
    "6": ("00110", "01000", "10000", "11110", "10001", "10001", "01110"),
    "7": ("11111", "00001", "00010", "00100", "01000", "01000", "01000"),
    "8": ("01110", "10001", "10001", "01110", "10001", "10001", "01110"),
    "9": ("01110", "10001", "10001", "01111", "00001", "00010", "01100"),
    " ": ("00000", "00000", "00000", "00000", "00000", "00000", "00000"),
    ",": ("00000", "00000", "00000", "00000", "00100", "00100", "01000"),
    ".": ("00000", "00000", "00000", "00000", "00000", "01100", "01100"),
    ":": ("00000", "01100", "01100", "00000", "01100", "01100", "00000"),
    ";": ("00000", "01100", "01100", "00000", "01100", "00100", "01000"),
    "'": ("00100", "00100", "01000", "00000", "00000", "00000", "00000"),
    "-": ("00000", "00000", "00000", "01110", "00000", "00000", "00000"),
    "!": ("00100", "00100", "00100", "00100", "00100", "00000", "00100"),
    "?": ("01110", "10001", "00001", "00110", "00100", "00000", "00100"),
    "(": ("00010", "00100", "01000", "01000", "01000", "00100", "00010"),
    ")": ("01000", "00100", "00010", "00010", "00010", "00100", "01000"),
    '"': ("01010", "01010", "00000", "00000", "00000", "00000", "00000"),
}

# ---------------------------------------------------------------------------
# Canvas
# ---------------------------------------------------------------------------

W = 1024
H = 1024

CREAM = (253, 248, 235)
NAVY = (28, 42, 84)
TERRA = (196, 90, 60)
GOLD = (232, 164, 66)
SKY_TOP = (248, 183, 120)
SKY_MID = (240, 140, 110)
SKY_LOW = (214, 106, 120)
ROOF = (44, 52, 96)
WINDOW = (255, 214, 130)


class Canvas:
    def __init__(self, w, h, bg):
        self.w = w
        self.h = h
        self.px = bytearray(bg * (w * h))

    def set(self, x, y, color):
        if 0 <= x < self.w and 0 <= y < self.h:
            i = (y * self.w + x) * 3
            self.px[i:i + 3] = bytes(color)

    def rect(self, x0, y0, x1, y1, color):
        for y in range(max(0, y0), min(self.h, y1 + 1)):
            for x in range(max(0, x0), min(self.w, x1 + 1)):
                self.set(x, y, color)

    def hline(self, x0, x1, y, color, thick=1):
        for t in range(thick):
            for x in range(x0, x1 + 1):
                self.set(x, y + t, color)

    def vline(self, x, y0, y1, color, thick=1):
        for t in range(thick):
            for y in range(y0, y1 + 1):
                self.set(x + t, y, color)

    def frame(self, x0, y0, x1, y1, color, thick=2):
        self.hline(x0, x1, y0, color, thick)
        self.hline(x0, x1, y1 - thick + 1, color, thick)
        self.vline(x0, y0, y1, color, thick)
        self.vline(x1 - thick + 1, y0, y1, color, thick)

    def disc(self, cx, cy, r, color):
        for dy in range(-r, r + 1):
            for dx in range(-r, r + 1):
                if dx * dx + dy * dy <= r * r:
                    self.set(cx + dx, cy + dy, color)

    def triangle(self, x0, y0, x1, y1, x2, y2, color):
        # Simple scanline fill.
        min_y = min(y0, y1, y2)
        max_y = max(y0, y1, y2)
        for y in range(min_y, max_y + 1):
            xs = []
            for (ax, ay, bx, by) in ((x0, y0, x1, y1),
                                     (x1, y1, x2, y2),
                                     (x2, y2, x0, y0)):
                if ay == by:
                    continue
                if (y >= min(ay, by)) and (y < max(ay, by)):
                    xs.append(ax + (y - ay) * (bx - ax) / (by - ay))
            if len(xs) >= 2:
                xs.sort()
                for x in range(int(xs[0]), int(xs[-1]) + 1):
                    self.set(x, y, color)


# ---------------------------------------------------------------------------
# Text drawing
# ---------------------------------------------------------------------------

def text_width(text, scale, spacing):
    return len(text) * (5 * scale + spacing) - spacing


def draw_text(cv, x, y, text, scale, color, spacing=None):
    if spacing is None:
        spacing = max(1, scale - 1)
    cx = x
    for ch in text:
        glyph = FONT.get(ch)
        if glyph is None:
            raise ValueError("missing glyph for %r" % ch)
        for row in range(7):
            bits = glyph[row]
            for col in range(5):
                if bits[col] == "1":
                    cv.rect(cx + col * scale, y + row * scale,
                            cx + col * scale + scale - 1,
                            y + row * scale + scale - 1, color)
        cx += 5 * scale + spacing
    return cx


def wrap_words(text, max_width_px, scale, spacing):
    """Greedy word wrap; returns a list of lines."""
    adv = 5 * scale + spacing
    space_w = adv
    lines = []
    cur = ""
    cur_w = 0
    for word in text.split(" "):
        ww = len(word) * adv - spacing
        if cur == "":
            cur, cur_w = word, ww
        elif cur_w + space_w + ww <= max_width_px:
            cur += " " + word
            cur_w += space_w + ww
        else:
            lines.append(cur)
            cur, cur_w = word, ww
    if cur:
        lines.append(cur)
    return lines


# ---------------------------------------------------------------------------
# PNG encoder (stdlib only)
# ---------------------------------------------------------------------------

def encode_png(cv):
    raw = bytearray()
    stride = cv.w * 3
    for y in range(cv.h):
        raw.append(0)  # filter: none
        raw += cv.px[y * stride:(y + 1) * stride]
    ihdr = struct.pack(">IIBBBBB", cv.w, cv.h, 8, 2, 0, 0, 0)

    def chunk(tag, data):
        out = struct.pack(">I", len(data)) + tag + data
        out += struct.pack(">I", zlib.crc32(tag + data) & 0xFFFFFFFF)
        return out

    png = b"\x89PNG\r\n\x1a\n"
    png += chunk(b"IHDR", ihdr)
    png += chunk(b"IDAT", zlib.compress(bytes(raw), 9))
    png += chunk(b"IEND", b"")
    return png


# ---------------------------------------------------------------------------
# Compose the letter
# ---------------------------------------------------------------------------

def draw_paw(cv, cx, cy, s, color):
    """A small paw print: one pad + four toes."""
    cv.disc(cx, cy + 3 * s, 3 * s, color)          # pad
    cv.disc(cx - 4 * s, cy - 1 * s, 1 * s + 1, color)
    cv.disc(cx - 1 * s, cy - 2 * s, 1 * s + 1, color)
    cv.disc(cx + 2 * s, cy - 2 * s, 1 * s + 1, color)
    cv.disc(cx + 4 * s, cy - 1 * s, 1 * s + 1, color)


def draw_sunset(cv, x0, y0, x1, y1):
    """Sunset over rooftops strip at the bottom of the letter."""
    band_h = (y1 - y0) // 3
    cv.rect(x0, y0, x1, y0 + band_h, SKY_TOP)
    cv.rect(x0, y0 + band_h, x1, y0 + 2 * band_h, SKY_MID)
    cv.rect(x0, y0 + 2 * band_h, x1, y1, SKY_LOW)
    # Rooftop silhouettes (kept inside the strip frame).
    base = y1
    roofs = [
        (x0, 58, 150), (x0 + 150, 40, 170), (x0 + 320, 66, 150),
        (x0 + 470, 46, 180), (x0 + 650, 62, 150), (x0 + 800, 44, 71),
    ]
    for rx, rh, rw in roofs:
        cv.rect(rx, base - rh, rx + rw, base, ROOF)
        cv.triangle(rx - 8, base - rh, rx + rw // 2, base - rh - 34,
                    rx + rw + 8, base - rh, ROOF)
    # Low sun, drawn over the rooflines so it stays visible.
    sun_cx = (x0 + x1) // 2 + 260
    sun_cy = base - 44
    cv.disc(sun_cx, sun_cy, 24, GOLD)
    cv.disc(sun_cx, sun_cy, 16, (245, 196, 110))
    # Two lit windows.
    cv.rect(x0 + 190, base - 30, x0 + 202, base - 14, WINDOW)
    cv.rect(x0 + 520, base - 36, x0 + 532, base - 20, WINDOW)
    cv.rect(x0 + 700, base - 26, x0 + 712, base - 12, WINDOW)
    # Thin frame around the strip.
    cv.frame(x0, y0, x1, y1, NAVY, 2)


def main():
    cv = Canvas(W, H, CREAM)

    # Double border frame.
    cv.frame(20, 20, W - 21, H - 21, NAVY, 3)
    cv.frame(32, 32, W - 33, H - 33, NAVY, 1)

    # Masthead, large caps, centred.
    m_scale = 5
    m_w = text_width(MASTHEAD, m_scale, 4)
    draw_text(cv, (W - m_w) // 2, 62, MASTHEAD, m_scale, NAVY, spacing=4)

    # Small flourish: two short rules flanking a diamond.
    cy = 118
    cv.hline(120, 420, cy, TERRA, 2)
    cv.hline(604, 904, cy, TERRA, 2)
    cv.disc(512, cy + 1, 5, TERRA)

    # Subline, centred.
    s_scale = 2
    s_w = text_width(SUBLINE, s_scale, 3)
    draw_text(cv, (W - s_w) // 2, 138, SUBLINE, s_scale, TERRA, spacing=3)

    # Body.
    body_scale = 3
    body_spacing = 2
    x0 = 72
    body_w = W - 2 * x0
    line_h = 7 * body_scale + 9
    para_gap = 13
    y = 182
    for para in PARAGRAPHS:
        lines = wrap_words(para, body_w, body_scale, body_spacing)
        for line in lines:
            draw_text(cv, x0, y, line, body_scale, NAVY,
                      spacing=body_spacing)
            y += line_h
        y += para_gap

    # Paw print beside the sign-off, as Miso's signature.
    draw_paw(cv, 880, y - line_h - para_gap + 6, 3, TERRA)

    # Sunset over rooftops strip at the bottom.
    draw_sunset(cv, 72, 892, W - 73, 968)

    png = encode_png(cv)

    out_dir = "/output"
    os.makedirs(out_dir, exist_ok=True)
    out_path = os.path.join(out_dir, "entry.png")
    with open(out_path, "wb") as f:
        f.write(png)

    digest = hashlib.sha256(png).hexdigest()
    print("output: %s" % out_path)
    print("dimensions: %dx%d" % (W, H))
    print("bytes: %d" % len(png))
    print("sha256: %s" % digest)


if __name__ == "__main__":
    main()
