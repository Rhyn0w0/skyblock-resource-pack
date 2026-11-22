#!/usr/bin/env python3
"""
Generates the Hypixel SkyBlock Floor 7 x Fortnite Treasure Hunters resource pack:
- Necron's Handle -> Fortnite Pirate Token (animated 32x32 pixel art OR official 256x256 icon)
- Floor 7 Drops -> Fortnite Treasure Hunters Gizmos & Sprite Dust
- Floor 7 / Dungeon Enchanted Books -> Official Fortnite Sprites
- Full Catharsis config UI (config.catharsis.json + fabric:overlays) + Firmament / CIT Resewn / OptiFine support

Uses only Python standard library (zero external dependencies).
"""

from __future__ import annotations

import json
import math
import shutil
import struct
import zlib
import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
OFFICIAL_DIR = ROOT / "scripts/official_assets"
SPRITES_DIR = OFFICIAL_DIR / "sprites"

RGBA = tuple[int, int, int, int]
Grid = list[list[RGBA]]

T: RGBA = (0, 0, 0, 0)


def write_png(path: Path, width: int, height: int, rgba_rows: list[bytes]) -> None:
    """Write an 8-bit RGBA PNG file from raw row bytes."""
    path.parent.mkdir(parents=True, exist_ok=True)

    def chunk(tag: bytes, data: bytes) -> bytes:
        return (
            struct.pack(">I", len(data))
            + tag
            + data
            + struct.pack(">I", zlib.crc32(tag + data) & 0xFFFFFFFF)
        )

    raw = b"".join(b"\x00" + row for row in rgba_rows)
    ihdr = struct.pack(">IIBBBBB", width, height, 8, 6, 0, 0, 0)
    png = (
        b"\x89PNG\r\n\x1a\n"
        + chunk(b"IHDR", ihdr)
        + chunk(b"IDAT", zlib.compress(raw, level=9))
        + chunk(b"IEND", b"")
    )
    path.write_bytes(png)


def hex_rgba(h: str, a: int = 255) -> RGBA:
    h = h.lstrip("#")
    return (int(h[0:2], 16), int(h[2:4], 16), int(h[4:6], 16), a)


def lerp_color(c1: RGBA, c2: RGBA, t: float) -> RGBA:
    t = max(0.0, min(1.0, t))
    return (
        int(round(c1[0] + (c2[0] - c1[0]) * t)),
        int(round(c1[1] + (c2[1] - c1[1]) * t)),
        int(round(c1[2] + (c2[2] - c1[2]) * t)),
        int(round(c1[3] + (c2[3] - c1[3]) * t)),
    )


def blank_grid(w: int = 32, h: int = 32) -> Grid:
    return [[T for _ in range(w)] for _ in range(h)]


def put(img: Grid, x: int, y: int, col: RGBA) -> None:
    if 0 <= y < len(img) and 0 <= x < len(img[0]):
        img[y][x] = col


def fill_rect(img: Grid, x0: int, y0: int, x1: int, y1: int, col: RGBA) -> None:
    for y in range(y0, y1 + 1):
        for x in range(x0, x1 + 1):
            put(img, x, y, col)


def add_outline(img: Grid, outline_col: RGBA) -> Grid:
    h, w = len(img), len(img[0])
    out = [row[:] for row in img]
    for y in range(h):
        for x in range(w):
            if img[y][x][3] == 0:
                for ox, oy in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
                    nx, ny = x + ox, y + oy
                    if 0 <= nx < w and 0 <= ny < h and img[ny][nx][3] > 0:
                        out[y][x] = outline_col
                        break
    return out


# ---------------------------------------------------------------------------
# 32x32 Pixel-Art Generators
# ---------------------------------------------------------------------------


def make_pirate_token_base() -> Grid:
    """Crisp 32x32 pixel-art gold Fortnite Pirate Token doubloon."""
    W = H = 32
    OUTLINE = hex_rgba("#381904")
    GROOVE = hex_rgba("#6E3606")
    FIELD_HI = hex_rgba("#BD710E")
    FIELD_MID = hex_rgba("#A65D0A")
    FIELD_LO = hex_rgba("#8C4A07")

    RIM_SHAD = hex_rgba("#CC7D0E")
    RIM_MID = hex_rgba("#F0A616")
    RIM_BRIGHT = hex_rgba("#FFCC29")
    RIM_LIGHT = hex_rgba("#FFE973")
    RIM_PALE = hex_rgba("#FFFAD0")

    EMB_SHAD = hex_rgba("#DE8E12")
    EMB_MID = hex_rgba("#FFC826")
    EMB_LIGHT = hex_rgba("#FFE86E")
    EMB_PALE = hex_rgba("#FFF7BF")

    EYE_DARK = hex_rgba("#291204")
    EYE_GLINT = hex_rgba("#522A12")
    BAND_DARK = hex_rgba("#871614")
    BAND_MID = hex_rgba("#C9241E")
    BAND_HI = hex_rgba("#F04635")

    img = blank_grid(W, H)
    cx, cy = 15.5, 15.5

    for y in range(H):
        for x in range(W):
            dx, dy = x - cx, y - cy
            r = math.hypot(dx, dy)
            light = (-dx - dy) / 21.0
            if r > 14.35:
                continue
            elif r > 13.15:
                img[y][x] = OUTLINE
            elif r > 10.65:
                angle = math.atan2(dy, dx)
                notch = math.sin(angle * 16.0)
                if light > 0.42:
                    col = RIM_PALE if (r > 11.7 or notch > 0.4) else RIM_LIGHT
                elif light > 0.08:
                    col = RIM_LIGHT if notch > 0.35 else RIM_BRIGHT
                elif light > -0.28:
                    col = RIM_BRIGHT if notch > 0.45 else RIM_MID
                else:
                    col = RIM_MID if notch > 0.35 else RIM_SHAD
                img[y][x] = col
            elif r > 9.65:
                img[y][x] = GROOVE
            else:
                if light > 0.25:
                    img[y][x] = FIELD_HI
                elif light > -0.25:
                    img[y][x] = FIELD_MID
                else:
                    img[y][x] = FIELD_LO

    emblem = [
        "....................",
        "....................",
        "......gggggggg......",
        "....gghhhbbbbbgg....",
        "...ghhhbbbbbrrrgg...",
        "...gbbbrrrrrrrgbg...",
        "..ggppplllllmmggrg..",
        "..gplgllllllmmssgg..",
        "..ggplleelmmekesg...",
        "...gplleelmmeeesg...",
        "...gglllmmllmmmgg...",
        "....glllmgmmllms....",
        "...ggllllmmmmssgg...",
        "..gplglglglglgmmsg..",
        "..gllggllllllggmmg..",
        "...ggg.gggggg.ggg...",
        "....................",
        "....................",
        "....................",
        "....................",
    ]
    palette = {
        "g": GROOVE,
        "s": EMB_SHAD,
        "m": EMB_MID,
        "l": EMB_LIGHT,
        "p": EMB_PALE,
        "e": EYE_DARK,
        "k": EYE_GLINT,
        "r": BAND_DARK,
        "b": BAND_MID,
        "h": BAND_HI,
    }
    ox0, oy0 = 6, 6
    for row_idx, row in enumerate(emblem):
        for col_idx, ch in enumerate(row):
            if ch != ".":
                px, py = ox0 + col_idx, oy0 + row_idx
                if math.hypot(px - cx, py - cy) <= 9.6:
                    img[py][px] = palette[ch]

    for px, py, col in [
        (14, 12, EYE_DARK), (15, 13, EYE_DARK), (16, 13, EYE_DARK),
        (17, 14, EYE_DARK), (18, 14, EYE_GLINT), (19, 14, EYE_DARK),
        (20, 14, EYE_DARK), (21, 15, EYE_DARK),
    ]:
        img[py][px] = col

    for px, py, col in [
        (8, 11, GROOVE), (9, 10, GROOVE), (10, 10, GROOVE),
        (9, 11, EMB_PALE), (10, 11, EMB_LIGHT), (10, 12, EMB_MID),
        (21, 10, GROOVE), (22, 10, GROOVE), (23, 11, GROOVE),
        (21, 11, EMB_MID), (22, 11, EMB_LIGHT), (21, 12, EMB_SHAD),
        (8, 20, GROOVE), (9, 19, EMB_PALE), (10, 19, EMB_LIGHT),
        (9, 20, EMB_LIGHT), (10, 20, EMB_MID), (9, 21, GROOVE), (10, 21, GROOVE),
        (23, 20, GROOVE), (21, 19, EMB_MID), (22, 19, EMB_MID),
        (21, 20, EMB_SHAD), (22, 20, EMB_MID), (21, 21, GROOVE), (22, 21, GROOVE),
    ]:
        if math.hypot(px - cx, py - cy) <= 9.6:
            img[py][px] = col

    for px, py in [(9, 5), (10, 4), (11, 4), (12, 3), (13, 3), (8, 6), (7, 7), (6, 8), (5, 9), (5, 10), (4, 11)]:
        img[py][px] = RIM_PALE

    return img


def make_golden_firework_pixel() -> Grid:
    """32x32 pixel-art Golden Firework starburst (Implosion Scroll)."""
    img = blank_grid(32, 32)
    OUT = hex_rgba("#5C2D04")
    GOLD_D = hex_rgba("#D9820B")
    GOLD = hex_rgba("#FFC41E")
    GOLD_L = hex_rgba("#FFF07C")
    WHITE = hex_rgba("#FFFDF0")

    cx, cy = 15.5, 14.5
    # Radiant curving golden firework trails
    angles = [i * (2 * math.pi / 12) + 0.15 for i in range(12)]
    for idx, ang in enumerate(angles):
        length = 11.5 if idx % 2 == 0 else 9.0
        for step in range(2, 26):
            t = step / 25.0
            dist = t * length
            # Slight downward droop for authentic firework arc
            px = cx + math.cos(ang) * dist
            py = cy + math.sin(ang) * dist + (t * t) * 2.2
            ix, iy = int(round(px)), int(round(py))
            col = WHITE if t < 0.28 else (GOLD_L if t < 0.62 else (GOLD if t < 0.88 else GOLD_L))
            put(img, ix, iy, col)
            if t < 0.45:
                put(img, ix + 1, iy, GOLD)

    # Wavy rising golden tail from bottom center
    for y in range(16, 30):
        x = 15 + int(round(math.sin((y - 16) * 0.7) * 0.8))
        put(img, x, y, GOLD if y > 22 else GOLD_L)
        put(img, x + 1, y, GOLD_D if y > 24 else GOLD)

    # Bright glowing white-gold core burst
    for y in range(11, 19):
        for x in range(12, 20):
            r = math.hypot(x - cx, y - cy)
            if r < 2.3:
                put(img, x, y, WHITE)
            elif r < 3.6:
                put(img, x, y, GOLD_L)
            elif r < 4.5:
                put(img, x, y, GOLD)

    # Detached golden spark dots around outer ring
    for sx, sy in [(6, 7), (25, 6), (27, 15), (4, 17), (7, 25), (24, 24), (19, 4), (11, 4)]:
        put(img, sx, sy, GOLD_L)

    return add_outline(img, OUT)


def make_canister_gizmo_pixel(
    core_dark: str,
    core_mid: str,
    core_bright: str,
    core_hi: str,
    accent: str,
    trim_gold: bool = False,
) -> Grid:
    """
    32x32 pixel-art angled Fortnite tech canister gizmo:
    - Crimson core -> Portable Extractor (Shadow Warp)
    - Cyan/gold core -> Extraction Site Booster (Wither Shield)
    """
    img = blank_grid(32, 32)
    OUT = hex_rgba("#0E1522")
    NAVY_D = hex_rgba("#1B2840")
    NAVY_M = hex_rgba("#2E466E")
    NAVY_L = hex_rgba("#4C6FA6")
    METAL_D = hex_rgba("#222833")
    METAL_M = hex_rgba("#394252")
    METAL_L = hex_rgba("#637085")
    GOLD_M = hex_rgba("#EBA115")
    GOLD_L = hex_rgba("#FFE566")
    ACC = hex_rgba(accent)
    CD = hex_rgba(core_dark)
    CM = hex_rgba(core_mid)
    CB = hex_rgba(core_bright)
    CH = hex_rgba(core_hi)

    # Draw tilted canister centered at (15.5, 15.5) rotated ~22 degrees
    cx, cy = 15.5, 15.5
    ang = math.radians(-22.0)
    ca, sa = math.cos(ang), math.sin(ang)

    for y in range(2, 30):
        for x in range(2, 30):
            dx, dy = x - cx, y - cy
            # Local coordinates: u = across width, v = along height (-12..12)
            u = dx * ca - dy * sa
            v = dx * sa + dy * ca

            # Top and bottom heavy armored hexagonal end-caps
            if -12.2 <= v <= -6.8 or 6.8 <= v <= 12.2:
                max_u = 5.4 if abs(v) < 10.6 else 4.2
                if abs(u) <= max_u:
                    if trim_gold and (abs(abs(v) - 7.3) < 0.75):
                        col = GOLD_L if u < 0 else GOLD_M
                    elif abs(v) > 10.6:
                        col = NAVY_L if u < -0.5 else (NAVY_M if u < 2.2 else NAVY_D)
                    else:
                        col = METAL_L if u < -2.0 else (METAL_M if u < 2.2 else METAL_D)
                    # Accent LED notches on top cap
                    if -10.0 <= v <= -8.6 and (abs(u - 2.3) < 0.8 or abs(u + 2.3) < 0.8):
                        col = ACC
                    put(img, x, y, col)
            # Middle section: glass energy core + side blue rails
            elif -6.8 < v < 6.8:
                if abs(u) <= 3.7:
                    # Glowing cylindrical glass chamber
                    if -2.3 <= u <= -1.1:
                        col = CH
                    elif u < 0.6:
                        col = CB
                    elif u < 2.3:
                        col = CM
                    else:
                        col = CD
                    # Subtle inner energy rod
                    if abs(u - 0.5) < 0.65:
                        col = lerp_color(col, METAL_D, 0.35)
                    put(img, x, y, col)
                elif 4.4 <= abs(u) <= 6.2:
                    # Armored side stabilizer struts
                    col = NAVY_L if u < 0 else (NAVY_M if abs(u) < 5.4 else NAVY_D)
                    if trim_gold and abs(v) < 1.3:
                        col = GOLD_L if u < 0 else GOLD_M
                    put(img, x, y, col)

    return add_outline(img, OUT)


def make_locator_gizmo_pixel(lucky: bool) -> Grid:
    """
    32x32 pixel-art handheld Fortnite Locator Gizmo:
    - lucky=True  -> Lucky Locator (gold body + glowing emerald/gold clover-star radar -> Auto Recombobulator)
    - lucky=False -> Sprite Locator (steel-blue body + glowing cyan sonar radar -> Precursor Gear)
    """
    img = blank_grid(32, 32)
    OUT = hex_rgba("#12161F") if not lucky else hex_rgba("#381D04")
    if lucky:
        BODY_L = hex_rgba("#FFE566")
        BODY_M = hex_rgba("#F0A516")
        BODY_D = hex_rgba("#A86008")
        TRIM = hex_rgba("#523008")
        SCR_BG = hex_rgba("#0F2B1D")
        SCR_RING = hex_rgba("#22A85A")
        SCR_PING = hex_rgba("#A3FFB8")
        ANT_TIP = hex_rgba("#FFF59D")
    else:
        BODY_L = hex_rgba("#6E8FBF")
        BODY_M = hex_rgba("#3F5B87")
        BODY_D = hex_rgba("#243654")
        TRIM = hex_rgba("#192233")
        SCR_BG = hex_rgba("#0B2436")
        SCR_RING = hex_rgba("#1AA6DB")
        SCR_PING = hex_rgba("#A8F4FF")
        ANT_TIP = hex_rgba("#66F2FF")

    # Top radar antenna & dish beacon
    fill_rect(img, 20, 4, 21, 9, TRIM)
    put(img, 20, 4, BODY_L)
    fill_rect(img, 19, 3, 22, 4, ANT_TIP)
    put(img, 20, 2, hex_rgba("#FFFFFF"))

    # Handheld rugged scanner casing (x=7..24, y=9..27)
    for y in range(9, 28):
        for x in range(7, 25):
            # Rounded corners
            if (x in (7, 24) and y in (9, 27)):
                continue
            if x <= 9 or y == 9:
                col = BODY_L
            elif x >= 22 or y >= 26:
                col = BODY_D
            else:
                col = BODY_M
            put(img, x, y, col)

    # Bottom grip ridges & indicator LEDs
    fill_rect(img, 9, 22, 22, 25, TRIM)
    for gx in range(10, 22, 2):
        put(img, gx, 23, BODY_D)
        put(img, gx, 24, BODY_M)
    put(img, 10, 22, ANT_TIP)
    put(img, 13, 22, SCR_PING)

    # Recessed circular radar screen (centered at 15.5, 15.5, radius 5.3)
    scx, scy = 15.5, 15.5
    for y in range(10, 22):
        for x in range(10, 22):
            r = math.hypot(x - scx, y - scy)
            if r <= 5.5:
                if r > 4.6:
                    put(img, x, y, TRIM)
                elif abs(r - 3.3) < 0.65:
                    put(img, x, y, SCR_RING)
                else:
                    put(img, x, y, SCR_BG)

    # Crosshair lines + glowing sonar ping
    for d in range(-4, 5):
        if d != 0:
            if abs(d) != 3:
                put(img, 15 + d, 15, lerp_color(SCR_BG, SCR_RING, 0.45))
                put(img, 15, 15 + d, lerp_color(SCR_BG, SCR_RING, 0.45))
    # Bright center blip + target star blip
    fill_rect(img, 15, 15, 16, 16, SCR_PING)
    put(img, 15, 15, hex_rgba("#FFFFFF"))
    put(img, 18, 13, hex_rgba("#FFFFFF"))
    put(img, 17, 13, SCR_PING)
    put(img, 18, 14, SCR_PING)

    # Subtle gold clover / sparkle emblem for Lucky Locator
    if lucky:
        for px, py in [(8, 7), (7, 8), (9, 8), (8, 9)]:
            put(img, px, py, SCR_PING)
        put(img, 8, 8, hex_rgba("#FFFFFF"))

    return add_outline(img, OUT)


def make_sprite_dust_pixel() -> Grid:
    """32x32 pixel-art glittering cyan-gold Sprite Dust pile (Wither Catalyst)."""
    img = blank_grid(32, 32)
    OUT = hex_rgba("#1A2340")
    CYAN_D = hex_rgba("#1E7CA8")
    CYAN_M = hex_rgba("#38C8F0")
    CYAN_L = hex_rgba("#A8F6FF")
    GOLD_M = hex_rgba("#F5B822")
    GOLD_L = hex_rgba("#FFF28A")
    WHITE = hex_rgba("#FFFFFF")

    # Sculpted glowing dust mound (y=12..26)
    cx = 15.5
    for y in range(12, 27):
        t = (y - 12) / 14.0
        half_w = 2.5 + 10.5 * math.sin(t * math.pi * 0.78)
        for x in range(4, 28):
            dx = abs(x - cx)
            if dx <= half_w:
                # Organic crystalline sparkle texture
                hval = (x * 17 + y * 31) % 19
                if y >= 24 or dx > half_w - 1.5:
                    col = CYAN_D
                elif hval in (0, 7):
                    col = GOLD_L
                elif hval in (3, 11):
                    col = GOLD_M
                elif hval in (1, 5, 13) or (x < 15 and y < 18):
                    col = CYAN_L
                else:
                    col = CYAN_M
                put(img, x, y, col)

    # Floating magical dust motes & 4-point sparkles rising above the mound
    sparkles = [(10, 8, GOLD_L), (21, 9, CYAN_L), (15, 6, WHITE), (7, 13, CYAN_L), (25, 14, GOLD_L)]
    for sx, sy, col in sparkles:
        put(img, sx, sy, WHITE)
        for ox, oy in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
            put(img, sx + ox, sy + oy, col)

    for px, py, col in [(12, 11, CYAN_M), (19, 12, GOLD_M), (8, 10, CYAN_L), (23, 7, GOLD_M)]:
        put(img, px, py, col)

    return add_outline(img, OUT)


def make_animated_strip(
    base: Grid,
    shine_hex: str = "#FFFCE0",
    sparkle_hex: str = "#FFF9C4",
    sparkle_pos: tuple[int, int] = (24, 7),
    rest_ticks: int = 36,
) -> tuple[int, int, list[bytes], dict]:
    """Generate an 11-frame 32x352 animated strip with diagonal sheen sweep + 4-point sparkle."""
    W = H = 32
    WHITE: RGBA = (255, 255, 255, 255)
    SPARKLE = hex_rgba(sparkle_hex)
    SHINE = hex_rgba(shine_hex)

    frames: list[Grid] = [[row[:] for row in base]]
    num_sweep = 10
    sx, sy = sparkle_pos

    for f in range(1, num_sweep + 1):
        frame = [row[:] for row in base]
        band_pos = 10.0 + (f - 1) * (44.0 / (num_sweep - 1))
        for y in range(H):
            for x in range(W):
                r, g, b, a = frame[y][x]
                if a == 0:
                    continue
                dist = abs((x + y) - band_pos)
                if dist < 3.2:
                    lum = (r + g + b) / (3.0 * 255.0)
                    strength = (1.0 - dist / 3.2) * (0.35 + 0.55 * lum)
                    if r < 60 and g < 60 and b < 60:
                        strength *= 0.25
                    frame[y][x] = lerp_color((r, g, b, a), SHINE, strength)

        if f in (5, 9):
            put(frame, sx, sy, SPARKLE)
        elif f in (6, 8):
            put(frame, sx, sy, WHITE)
            for ox, oy in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
                put(frame, sx + ox, sy + oy, SPARKLE)
        elif f == 7:
            put(frame, sx, sy, WHITE)
            for ox, oy in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
                put(frame, sx + ox, sy + oy, WHITE)
            for ox, oy in [(-2, 0), (2, 0), (0, -2), (0, 2)]:
                put(frame, sx + ox, sy + oy, SPARKLE)

        frames.append(frame)

    rows: list[bytes] = []
    for frame in frames:
        for row in frame:
            rows.append(b"".join(bytes(px) for px in row))

    mcmeta = {
        "animation": {
            "frametime": 2,
            "frames": [{"index": 0, "time": rest_ticks}, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10],
        }
    }
    return W, H * len(frames), rows, mcmeta


def make_pack_icon(base: Grid) -> tuple[int, int, list[bytes]]:
    """256x256 pack.png thumbnail with deep pirate-navy vignette & gold frame."""
    SIZE = 256
    SCALE = 7
    PAD = (SIZE - 32 * SCALE) // 2
    BG_INNER = hex_rgba("#2B1B3D")
    BG_OUTER = hex_rgba("#120A1E")
    BORDER_OUT = hex_rgba("#3D1E04")
    BORDER_GOLD = hex_rgba("#EB9F15")
    BORDER_HI = hex_rgba("#FFE76B")

    rows: list[bytes] = []
    cx = cy = (SIZE - 1) / 2.0
    for y in range(SIZE):
        row = bytearray()
        for x in range(SIZE):
            if x < 4 or x >= SIZE - 4 or y < 4 or y >= SIZE - 4:
                px = BORDER_OUT
            elif x < 8 or x >= SIZE - 8 or y < 8 or y >= SIZE - 8:
                px = BORDER_HI if (x + y) < SIZE else BORDER_GOLD
            elif x < 11 or x >= SIZE - 11 or y < 11 or y >= SIZE - 11:
                px = BORDER_OUT
            else:
                d = math.hypot(x - cx, y - cy) / (SIZE * 0.65)
                px = lerp_color(BG_INNER, BG_OUTER, min(1.0, d))

            sx = (x - PAD) // SCALE
            sy = (y - PAD) // SCALE
            if 0 <= sx < 32 and 0 <= sy < 32:
                sp = base[sy][sx]
                if sp[3] > 0:
                    px = sp
            row.extend(px)
        rows.append(bytes(row))
    return SIZE, SIZE, rows


def write_json(path: Path, data: object) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, indent=2) + "\n", encoding="utf-8")


# ---------------------------------------------------------------------------
# Pack Data Tables
# ---------------------------------------------------------------------------

# Floor 7 drops mapped to Fortnite Treasure Hunters Gizmos & Sprite Dust
F7_GIZMO_DROPS = [
    # (skyblock_id, texture_key, gizmo_name, rename_regex, official_png_name_or_None)
    ("implosion_scroll",    "golden_firework",         "Golden Firework",         r"(?m)^Implosion$",            "golden_firework.png"),
    ("shadow_warp_scroll",  "portable_extractor",      "Portable Extractor",      r"(?m)^Shadow Warp$",          "portable_extractor.png"),
    ("wither_shield_scroll","extraction_site_booster", "Extraction Site Booster", r"(?m)^Wither Shield$",        None),
    ("auto_recombobulator", "lucky_locator",           "Lucky Locator",           r"Auto Recombobulator",          None),
    ("precursor_gear",      "sprite_locator",          "Sprite Locator",          r"Precursor Gear",               None),
    ("wither_catalyst",     "sprite_dust",             "Sprite Dust",             r"Wither Catalyst",              None),
]

# Floor 7 & Dungeon Enchanted Books mapped to official Fortnite Sprites
ENCHANTMENT_SPRITES = [
    "ultimate_one_for_all",
    "ultimate_soul_eater",
    "feather_falling",
    "rejuvenate",
    "infinite_quiver",
    "ultimate_bank",
    "ultimate_wise",
    "ultimate_wisdom",
    "ultimate_jerry",
    "ultimate_combo",
    "ultimate_swarm",
    "ultimate_legion",
    "ultimate_last_stand",
    "ultimate_no_pain_no_gain",
    "overload",
    "thunderlord",
    "lethality",
    "ultimate_rend",
]


def build_all() -> None:
    pack_id = "necron_handle_pirate_token"

    # Clean overlay directories before rebuilding so no stale files linger
    for ov in ("texture_official", "name_pirate_shop_access_token", "f7_gizmos", "f7_gizmos_official", "f7_gizmo_names", "enchantment_sprites"):
        ov_path = ROOT / ov
        if ov_path.exists():
            shutil.rmtree(ov_path)

    # 1. Generate all 32x32 pixel-art base grids
    token_base = make_pirate_token_base()
    gizmo_bases: dict[str, tuple[Grid, str, str, tuple[int, int]]] = {
        "golden_firework": (
            make_golden_firework_pixel(), "#FFFDF0", "#FFE566", (24, 6),
        ),
        "portable_extractor": (
            make_canister_gizmo_pixel("#7D0F18", "#D92332", "#FF4D5A", "#FFB3BA", "#FF3B30", trim_gold=False),
            "#FFD6DA", "#FF8A93", (22, 7),
        ),
        "extraction_site_booster": (
            make_canister_gizmo_pixel("#0B4F75", "#1BA3DB", "#5CE1FF", "#D6FAFF", "#FFE566", trim_gold=True),
            "#E0FCFF", "#7AF0FF", (22, 7),
        ),
        "lucky_locator": (
            make_locator_gizmo_pixel(lucky=True), "#FFFDE0", "#A3FFB8", (22, 6),
        ),
        "sprite_locator": (
            make_locator_gizmo_pixel(lucky=False), "#E0FAFF", "#66F2FF", (22, 6),
        ),
        "sprite_dust": (
            make_sprite_dust_pixel(), "#FFFDE0", "#A8F6FF", (23, 8),
        ),
    }

    tex_w, tex_h, tex_rows, mcmeta = make_animated_strip(token_base)
    icon_w, icon_h, icon_rows = make_pack_icon(token_base)

    # 2. pack.mcmeta
    pack_mcmeta = {
        "pack": {
            "pack_format": 1,
            "supported_formats": [1, 255],
            "min_format": 1,
            "max_format": 255,
            "description": "\u00a76Pirate Token \u00a77- Floor 7 \u00d7 Fortnite Treasure Hunters",
        },
        "catharsis:pack/v1": {
            "id": pack_id,
            "version": "1.2.0",
            "pack_required_for_config": True,
            "override_hypixel_pack": True,
        },
        "fabric:overlays": {
            "entries": [
                {
                    "directory": "texture_official",
                    "condition": {
                        "condition": "catharsis:config",
                        "pack": pack_id,
                        "id": "texture_style",
                        "value": "official",
                    },
                },
                {
                    "directory": "name_pirate_shop_access_token",
                    "condition": {
                        "condition": "catharsis:config",
                        "pack": pack_id,
                        "id": "item_name",
                        "value": "pirate_shop_access_token",
                    },
                },
                {
                    "directory": "f7_gizmos",
                    "condition": {
                        "condition": "catharsis:config",
                        "pack": pack_id,
                        "id": "f7_gizmos",
                    },
                },
                {
                    "directory": "f7_gizmos_official",
                    "condition": {
                        "condition": "fabric:and",
                        "values": [
                            {
                                "condition": "catharsis:config",
                                "pack": pack_id,
                                "id": "f7_gizmos",
                            },
                            {
                                "condition": "catharsis:config",
                                "pack": pack_id,
                                "id": "texture_style",
                                "value": "official",
                            },
                        ],
                    },
                },
                {
                    "directory": "f7_gizmo_names",
                    "condition": {
                        "condition": "catharsis:config",
                        "pack": pack_id,
                        "id": "f7_gizmo_names",
                    },
                },
                {
                    "directory": "enchantment_sprites",
                    "condition": {
                        "condition": "catharsis:config",
                        "pack": pack_id,
                        "id": "enchantment_sprites",
                    },
                },
            ]
        },
    }
    write_json(ROOT / "pack.mcmeta", pack_mcmeta)

    # 3. config.catharsis.json
    catharsis_config = [
        {
            "type": "separator",
            "title": {"text": "Necron's Handle (Pirate Token)", "color": "gold", "bold": True},
            "description": {"text": "Customize the Pirate Token texture and visible name.", "color": "gray"},
        },
        {
            "type": "dropdown",
            "id": "texture_style",
            "title": {"text": "Texture Style"},
            "description": {
                "text": "Choose between custom animated pixel art or official Fortnite Treasure Hunters icons.",
                "color": "gray",
            },
            "descriptions": {
                "pixel": {"text": "Custom 32x32 animated pixel art for Pirate Token & Gizmos.", "color": "gray"},
                "official": {"text": "Official high-res Fortnite Treasure Hunters images where available.", "color": "gray"},
            },
            "options": [
                {"value": "pixel", "text": {"text": "Pixel Art"}, "default": True},
                {"value": "official", "text": {"text": "Official Fortnite"}},
            ],
        },
        {
            "type": "dropdown",
            "id": "item_name",
            "title": {"text": "Handle Display Name"},
            "description": {"text": "Choose the visible name shown for Necron's Handle.", "color": "gray"},
            "descriptions": {
                "pirate_token": {"text": "Displays as Pirate Token.", "color": "gold"},
                "pirate_shop_access_token": {"text": "Displays as Pirate Shop Access Token.", "color": "gold"},
            },
            "options": [
                {"value": "pirate_token", "text": {"text": "Pirate Token"}, "default": True},
                {"value": "pirate_shop_access_token", "text": {"text": "Pirate Shop Access Token"}},
            ],
        },
        {
            "type": "separator",
            "title": {"text": "Floor 7 Gizmos & Sprites", "color": "aqua", "bold": True},
            "description": {"text": "Turn other Floor 7 drops into Fortnite Gizmos and Enchanted Books into Sprites.", "color": "gray"},
        },
        {
            "type": "boolean",
            "id": "f7_gizmos",
            "title": {"text": "Floor 7 Gizmo Drops"},
            "description": {
                "text": "Implosion -> Golden Firework, Shadow Warp -> Portable Extractor, Wither Shield -> Extraction Site Booster, Auto Recomb -> Lucky Locator, Precursor Gear -> Sprite Locator, Wither Catalyst -> Sprite Dust.",
                "color": "gray",
            },
            "default": True,
        },
        {
            "type": "boolean",
            "id": "f7_gizmo_names",
            "title": {"text": "Rename Gizmo Drops"},
            "description": {
                "text": "Also rename those Floor 7 drops to their matching Fortnite Gizmo names.",
                "color": "gray",
            },
            "default": False,
        },
        {
            "type": "boolean",
            "id": "enchantment_sprites",
            "title": {"text": "Enchanted Book Sprites"},
            "description": {
                "text": "Turns Floor 7 & Dungeon Enchanted Books (One For All, Soul Eater, Feather Falling, Rejuvenate, Bank, Ultimate Wise, Wisdom, Ultimate Jerry, Legion, Swarm, Combo, etc.) into matching official Fortnite Sprites.",
                "color": "gray",
            },
            "default": True,
        },
    ]
    write_json(ROOT / "config.catharsis.json", catharsis_config)

    # 4. pack.png
    write_png(ROOT / "pack.png", icon_w, icon_h, icon_rows)

    # 5. Base Pirate Token (Necron's Handle) assets
    def item_def(model_id: str) -> dict:
        return {"model": {"type": "minecraft:model", "model": model_id}}

    def gen_model(tex_id: str) -> dict:
        return {"parent": "minecraft:item/generated", "textures": {"layer0": tex_id}}

    write_json(ROOT / "assets/skyblock/items/necron_handle.json", item_def("pirate_token:item/necron_handle"))
    write_json(ROOT / "assets/hypixel_skyblock/items/necron_handle.json", item_def("pirate_token:item/necron_handle"))
    write_json(ROOT / "assets/pirate_token/models/item/necron_handle.json", gen_model("pirate_token:item/necron_handle"))
    write_json(ROOT / "assets/pirate_token/models/item/necron_handle_official.json", gen_model("pirate_token:item/necron_handle_official"))

    tok_tex = ROOT / "assets/pirate_token/textures/item/necron_handle.png"
    write_png(tok_tex, tex_w, tex_h, tex_rows)
    write_json(tok_tex.with_suffix(".png.mcmeta"), mcmeta)

    official_src = ROOT / "scripts/official_pirate_token.png"
    if not official_src.exists():
        raise FileNotFoundError(f"Missing {official_src}")
    shutil.copyfile(official_src, ROOT / "assets/pirate_token/textures/item/necron_handle_official.png")

    # Helper to write Catharsis & Firmament text replacements
    def write_catharsis_text(base_dir: Path, file_key: str, regex: str, display_name: str, color: str = "gold") -> None:
        rep = {
            "priority": 0,
            "replacer": {
                "type": "catharsis:regex",
                "regex": regex,
                "replacement": {"text": display_name, "color": color, "italic": False},
            },
        }
        for target in ("item", "nametag"):
            write_json(base_dir / f"assets/pirate_token/catharsis/text_replacements/{target}/{file_key}.json", rep)

    def write_firmament_text(base_dir: Path, file_key: str, match_plain: str, display_name: str, color: str = "gold") -> None:
        override = {
            "match": {"regex": f".*{match_plain}.*"},
            "replacements": [
                {
                    "match": match_plain,
                    "replace": {"text": display_name, "color": color, "italic": False},
                }
            ],
        }
        write_json(base_dir / f"assets/firmskyblock/overrides/texts/{file_key}.json", override)

    # Default Necron's Handle text replacement
    write_catharsis_text(ROOT, "necron_handle", "Necron's Handle", "Pirate Token")
    write_firmament_text(ROOT, "necron_handle", "Necron's Handle", "Pirate Token")

    # Overlay: Official Fortnite Pirate Token
    for ns in ("skyblock", "hypixel_skyblock", "firmskyblock"):
        write_json(
            ROOT / f"texture_official/assets/{ns}/items/necron_handle.json",
            item_def("pirate_token:item/necron_handle_official"),
        )

    # Overlay: "Pirate Shop Access Token" display name
    write_catharsis_text(ROOT / "name_pirate_shop_access_token", "necron_handle", "Necron's Handle", "Pirate Shop Access Token")
    write_firmament_text(ROOT / "name_pirate_shop_access_token", "necron_handle", "Necron's Handle", "Pirate Shop Access Token")

    # 6. Floor 7 Gizmo Drops (base models/textures in pirate_token namespace; item bindings in f7_gizmos overlay!)
    for sb_id, tex_key, gizmo_name, rename_regex, official_file in F7_GIZMO_DROPS:
        grid, shine_hex, spark_hex, spark_pos = gizmo_bases[tex_key]
        gw, gh, grows, gmeta = make_animated_strip(grid, shine_hex, spark_hex, spark_pos, rest_ticks=40)

        # Animated pixel-art texture + model
        g_tex = ROOT / f"assets/pirate_token/textures/item/{tex_key}.png"
        write_png(g_tex, gw, gh, grows)
        write_json(g_tex.with_suffix(".png.mcmeta"), gmeta)
        write_json(ROOT / f"assets/pirate_token/models/item/{tex_key}.json", gen_model(f"pirate_token:item/{tex_key}"))

        # Bind inside `f7_gizmos` overlay (default ON in Catharsis)
        for ns in ("skyblock", "hypixel_skyblock", "firmskyblock"):
            write_json(
                ROOT / f"f7_gizmos/assets/{ns}/items/{sb_id}.json",
                item_def(f"pirate_token:item/{tex_key}"),
            )

        # If we also have the official high-res Fortnite render, wire up `f7_gizmos_official` overlay!
        if official_file is not None:
            src_png = OFFICIAL_DIR / official_file
            if not src_png.exists():
                raise FileNotFoundError(f"Missing official gizmo PNG: {src_png}")
            off_key = f"{tex_key}_official"
            dst_png = ROOT / f"assets/pirate_token/textures/item/{off_key}.png"
            dst_png.parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(src_png, dst_png)
            write_json(ROOT / f"assets/pirate_token/models/item/{off_key}.json", gen_model(f"pirate_token:item/{off_key}"))
            for ns in ("skyblock", "hypixel_skyblock", "firmskyblock"):
                write_json(
                    ROOT / f"f7_gizmos_official/assets/{ns}/items/{sb_id}.json",
                    item_def(f"pirate_token:item/{off_key}"),
                )

        # Optional Gizmo rename overlay (`f7_gizmo_names`, default OFF)
        name_color = "aqua" if tex_key == "sprite_dust" else "gold"
        write_catharsis_text(ROOT / "f7_gizmo_names", sb_id, rename_regex, gizmo_name, color=name_color)

    # 7. Floor 7 & Dungeon Enchanted Books -> Official Fortnite Sprites (`enchantment_sprites` overlay, default ON)
    for ench_id in ENCHANTMENT_SPRITES:
        src_sprite = SPRITES_DIR / f"{ench_id}.png"
        if not src_sprite.exists():
            raise FileNotFoundError(f"Missing official sprite PNG: {src_sprite}")
        sprite_key = f"sprite_{ench_id}"
        dst_sprite = ROOT / f"assets/pirate_token/textures/item/{sprite_key}.png"
        dst_sprite.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(src_sprite, dst_sprite)
        write_json(
            ROOT / f"assets/pirate_token/models/item/{sprite_key}.json",
            gen_model(f"pirate_token:item/{sprite_key}"),
        )
        write_json(
            ROOT / f"enchantment_sprites/assets/skyblock/items/enchantments/{ench_id}.json",
            item_def(f"pirate_token:item/{sprite_key}"),
        )

    # 8. Firmament base Necron's Handle (1.20.4 - 26.1+)
    write_json(ROOT / "assets/firmskyblock/items/necron_handle.json", item_def("firmskyblock:item/necron_handle"))
    write_json(ROOT / "assets/firmskyblock/models/item/necron_handle.json", gen_model("firmskyblock:item/necron_handle"))
    firm_tex = ROOT / "assets/firmskyblock/textures/item/necron_handle.png"
    write_png(firm_tex, tex_w, tex_h, tex_rows)
    write_json(firm_tex.with_suffix(".png.mcmeta"), mcmeta)

    # 9. OptiFine / CIT Resewn / MCPatcher legacy CIT for Necron's Handle
    for sub, matcher in [
        ("optifine/cit/necron_handle", "nbt.ExtraAttributes.id=NECRON_HANDLE"),
        ("citresewn/cit/necron_handle", "components.custom_data.id=NECRON_HANDLE"),
        ("mcpatcher/cit/necron_handle", "nbt.ExtraAttributes.id=NECRON_HANDLE"),
    ]:
        d = ROOT / "assets/minecraft" / sub
        d.mkdir(parents=True, exist_ok=True)
        write_png(d / "necron_handle.png", tex_w, tex_h, tex_rows)
        write_json(d / "necron_handle.png.mcmeta", mcmeta)
        (d / "necron_handle.properties").write_text(
            f"type=item\nitems=minecraft:stick\ntexture=necron_handle.png\n{matcher}\n",
            encoding="utf-8",
        )

    # 10. Export preview PNGs (Pirate Token + 3x2 Gizmos preview sheet)
    preview_rows: list[bytes] = []
    for y in range(32):
        expanded = b"".join(bytes(px) * 8 for px in token_base[y])
        for _ in range(8):
            preview_rows.append(expanded)
    write_png(ROOT / "dist/preview_token.png", 256, 256, preview_rows)

    # 3x2 preview sheet of the 6 pixel-art gizmos (each 128x128 = 4x scale, 8px dark padding)
    g_order = [
        gizmo_bases["golden_firework"][0],
        gizmo_bases["portable_extractor"][0],
        gizmo_bases["extraction_site_booster"][0],
        gizmo_bases["lucky_locator"][0],
        gizmo_bases["sprite_locator"][0],
        gizmo_bases["sprite_dust"][0],
    ]
    cell = 128
    pad = 8
    sheet_w = 3 * cell + 4 * pad
    sheet_h = 2 * cell + 3 * pad
    bg = hex_rgba("#181626")
    sheet_rows: list[bytes] = []
    for sy in range(sheet_h):
        row = bytearray()
        for sx in range(sheet_w):
            px = bg
            for idx, grid in enumerate(g_order):
                gx = idx % 3
                gy = idx // 3
                x0 = pad + gx * (cell + pad)
                y0 = pad + gy * (cell + pad)
                if x0 <= sx < x0 + cell and y0 <= sy < y0 + cell:
                    sp = grid[(sy - y0) // 4][(sx - x0) // 4]
                    if sp[3] > 0:
                        px = sp
            row.extend(px)
        sheet_rows.append(bytes(row))
    write_png(ROOT / "dist/preview_gizmos.png", sheet_w, sheet_h, sheet_rows)

    # 11. Package ready-to-install .zip in dist/
    zip_path = ROOT / "dist/NecronHandle-PirateToken.zip"
    zip_path.parent.mkdir(parents=True, exist_ok=True)
    include_paths: list[Path] = [
        ROOT / "pack.mcmeta",
        ROOT / "pack.png",
        ROOT / "config.catharsis.json",
    ]
    for ns in ("skyblock", "hypixel_skyblock", "pirate_token", "firmskyblock", "minecraft"):
        ns_dir = ROOT / "assets" / ns
        if ns_dir.exists():
            include_paths.extend(f for f in sorted(ns_dir.rglob("*")) if f.is_file())
    for ov in (
        "texture_official",
        "name_pirate_shop_access_token",
        "f7_gizmos",
        "f7_gizmos_official",
        "f7_gizmo_names",
        "enchantment_sprites",
    ):
        ov_dir = ROOT / ov
        if ov_dir.exists():
            include_paths.extend(f for f in sorted(ov_dir.rglob("*")) if f.is_file())

    with zipfile.ZipFile(zip_path, "w", compression=zipfile.ZIP_DEFLATED) as zf:
        for f in include_paths:
            zf.write(f, arcname=f.relative_to(ROOT).as_posix())

    print(f"Built resource pack -> {zip_path} ({zip_path.stat().st_size} bytes, {len(include_paths)} files)")


if __name__ == "__main__":
    build_all()
