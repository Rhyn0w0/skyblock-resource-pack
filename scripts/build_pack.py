#!/usr/bin/env python3
"""
Generates the Necron's Handle -> Fortnite Pirate Token Hypixel SkyBlock resource pack.
Uses only Python standard library (zero external dependencies).
"""

from __future__ import annotations

import json
import math
import os
import shutil
import struct
import zlib
import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent


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


def hex_rgba(h: str, a: int = 255) -> tuple[int, int, int, int]:
    h = h.lstrip("#")
    return (int(h[0:2], 16), int(h[2:4], 16), int(h[4:6], 16), a)


def lerp_color(
    c1: tuple[int, int, int, int], c2: tuple[int, int, int, int], t: float
) -> tuple[int, int, int, int]:
    t = max(0.0, min(1.0, t))
    return (
        int(round(c1[0] + (c2[0] - c1[0]) * t)),
        int(round(c1[1] + (c2[1] - c1[1]) * t)),
        int(round(c1[2] + (c2[2] - c1[2]) * t)),
        int(round(c1[3] + (c2[3] - c1[3]) * t)),
    )


def make_pirate_token_base() -> list[list[tuple[int, int, int, int]]]:
    """
    Create a crisp 32x32 pixel-art gold Fortnite Pirate Token
    (beveled gleaming gold doubloon with high-contrast embossed pirate skull,
    eyepatch, crimson bandana, and clean symmetrical crossbones).
    """
    W = H = 32
    T = (0, 0, 0, 0)

    # High-contrast, clean pixel-art gold palette
    OUTLINE = hex_rgba("#381904")       # Crisp dark outer coin outline
    GROOVE = hex_rgba("#6E3606")        # Deep recessed stamp outline / ring groove
    FIELD_HI = hex_rgba("#BD710E")      # Recessed coin field (lit top-left)
    FIELD_MID = hex_rgba("#A65D0A")     # Recessed coin field (center)
    FIELD_LO = hex_rgba("#8C4A07")      # Recessed coin field (shaded bottom-right)

    RIM_SHAD = hex_rgba("#CC7D0E")      # Rim bottom-right (still clearly gold!)
    RIM_MID = hex_rgba("#F0A616")       # Rim midtone gold
    RIM_BRIGHT = hex_rgba("#FFCC29")    # Rim bright gold
    RIM_LIGHT = hex_rgba("#FFE973")     # Rim strong highlight
    RIM_PALE = hex_rgba("#FFFAD0")      # Rim specular peak

    EMB_SHAD = hex_rgba("#DE8E12")      # Embossed skull/bone shadow
    EMB_MID = hex_rgba("#FFC826")       # Embossed skull/bone midtone
    EMB_LIGHT = hex_rgba("#FFE86E")     # Embossed skull/bone bright
    EMB_PALE = hex_rgba("#FFF7BF")      # Embossed skull/bone peak

    EYE_DARK = hex_rgba("#291204")      # Eye socket & eyepatch dark
    EYE_GLINT = hex_rgba("#522A12")     # Subtle eyepatch edge highlight
    BAND_DARK = hex_rgba("#871614")     # Crimson pirate bandana shadow
    BAND_MID = hex_rgba("#C9241E")      # Crimson pirate bandana body
    BAND_HI = hex_rgba("#F04635")       # Crimson pirate bandana highlight

    img = [[T for _ in range(W)] for _ in range(H)]
    cx, cy = 15.5, 15.5

    # 1. Clean circular coin silhouette, continuous beveled gold rim, crisp inner groove, smooth field
    for y in range(H):
        for x in range(W):
            dx = x - cx
            dy = y - cy
            r = math.hypot(dx, dy)
            light = (-dx - dy) / 21.0  # top-left light [-1, 1]

            if r > 14.35:
                continue
            elif r > 13.15:
                img[y][x] = OUTLINE
            elif r > 10.65:
                # Smooth, gleaming metallic beveled gold rim all 360 degrees
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
                # Continuous crisp inner coin groove
                img[y][x] = GROOVE
            else:
                # Smooth recessed gold field for high-contrast embossing
                if light > 0.25:
                    img[y][x] = FIELD_HI
                elif light > -0.25:
                    img[y][x] = FIELD_MID
                else:
                    img[y][x] = FIELD_LO

    # 2. Hand-crafted symmetrical 20x20 center emblem (Crossbones + Centered Pirate Skull)
    # Placed at offset (6, 6) -> covers x=6..25, y=6..25 cleanly inside the inner ring (r <= 9.3)!
    # Legend:
    # . = keep coin field behind
    # g = recessed groove / dark embossed outline
    # s = embossed shadow gold
    # m = embossed mid gold
    # l = embossed light gold
    # p = embossed pale highlight
    # e = dark eye socket / eyepatch
    # k = eyepatch subtle sheen
    # r = bandana shadow red
    # b = bandana mid red
    # h = bandana highlight red
    emblem = [
        "....................",  # y=6
        "....................",  # y=7
        "......gggggggg......",  # y=8
        "....gghhhbbbbbgg....",  # y=9   (crimson pirate bandana)
        "...ghhhbbbbbrrrgg...",  # y=10
        "...gbbbrrrrrrrgbg...",  # y=11  (bandana knot peeking right)
        "..ggppplllllmmggrg..",  # y=12  (skull brow + knot tail)
        "..gplgllllllmmssgg..",  # y=13  (upper crossbone tips tucked cleanly inside!)
        "..ggplleelmmekesg...",  # y=14  (left eye socket + right eyepatch)
        "...gplleelmmeeesg...",  # y=15
        "...gglllmmllmmmgg...",  # y=16  (cheekbones)
        "....glllmgmmllms....",  # y=17  (nose cavity)
        "...ggllllmmmmssgg...",  # y=18  (upper jaw + lower crossbones emerging)
        "..gplglglglglgmmsg..",  # y=19  (3 crisp teeth + lower crossbone shafts)
        "..gllggllllllggmmg..",  # y=20  (jaw bottom + bone knobs)
        "...ggg.gggggg.ggg...",  # y=21  (lower bone knobs inside ring)
        "....................",  # y=22
        "....................",  # y=23
        "....................",  # y=24
        "....................",  # y=25
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
                # Strictly stay inside the inner field so the dark coin groove stays unbroken!
                if math.hypot(px - cx, py - cy) <= 9.6:
                    img[py][px] = palette[ch]

    # Clean diagonal eyepatch strap from left brow down across the right eye socket
    for px, py, col in [
        (14, 12, EYE_DARK),
        (15, 13, EYE_DARK),
        (16, 13, EYE_DARK),
        (17, 14, EYE_DARK),
        (18, 14, EYE_GLINT),
        (19, 14, EYE_DARK),
        (20, 14, EYE_DARK),
        (21, 15, EYE_DARK),
    ]:
        img[py][px] = col

    # Make the 4 diagonal crossbone ends pop crisply inside the inner circle
    # Top-left bone end (x=8..10, y=10..11)
    for px, py, col in [
        (8, 11, GROOVE), (9, 10, GROOVE), (10, 10, GROOVE),
        (9, 11, EMB_PALE), (10, 11, EMB_LIGHT), (10, 12, EMB_MID),
        # Top-right bone end (x=21..23, y=10..11)
        (21, 10, GROOVE), (22, 10, GROOVE), (23, 11, GROOVE),
        (21, 11, EMB_MID), (22, 11, EMB_LIGHT), (21, 12, EMB_SHAD),
        # Bottom-left bone end (x=8..10, y=20..21)
        (8, 20, GROOVE), (9, 19, EMB_PALE), (10, 19, EMB_LIGHT),
        (9, 20, EMB_LIGHT), (10, 20, EMB_MID), (9, 21, GROOVE), (10, 21, GROOVE),
        # Bottom-right bone end (x=21..23, y=20..21)
        (23, 20, GROOVE), (21, 19, EMB_MID), (22, 19, EMB_MID),
        (21, 20, EMB_SHAD), (22, 20, EMB_MID), (21, 21, GROOVE), (22, 21, GROOVE),
    ]:
        if math.hypot(px - cx, py - cy) <= 9.6:
            img[py][px] = col

    # Extra crisp specular shine pixels on the upper-left coin rim
    for px, py in [(9, 5), (10, 4), (11, 4), (12, 3), (13, 3), (8, 6), (7, 7), (6, 8), (5, 9), (5, 10), (4, 11)]:
        img[py][px] = RIM_PALE

    return img


def make_animated_strip(
    base: list[list[tuple[int, int, int, int]]]
) -> tuple[int, int, list[bytes], dict]:
    """
    Generate a 12-frame 32x384 animated PNG strip with a smooth diagonal metallic gold
    sheen sweep and a 4-point star sparkle on the coin's top-right rim.
    """
    W = H = 32
    WHITE = (255, 255, 255, 255)
    SPARKLE_GOLD = hex_rgba("#FFF9C4")
    SHINE_GOLD = hex_rgba("#FFFCE0")

    frames: list[list[list[tuple[int, int, int, int]]]] = []

    # Frame 0: clean resting base frame
    frames.append([row[:] for row in base])

    # Frames 1..10: diagonal metallic shimmer sweeping top-left -> bottom-right
    num_sweep = 10
    for f in range(1, num_sweep + 1):
        frame = [row[:] for row in base]
        # Diagonal band position: x + y moves from 10 to 54
        band_pos = 10.0 + (f - 1) * (44.0 / (num_sweep - 1))
        for y in range(H):
            for x in range(W):
                r, g, b, a = frame[y][x]
                if a == 0:
                    continue
                dist = abs((x + y) - band_pos)
                if dist < 3.2:
                    # Stronger sheen on brighter gold pixels, gentle on dark recesses
                    lum = (r + g + b) / (3.0 * 255.0)
                    strength = (1.0 - dist / 3.2) * (0.35 + 0.55 * lum)
                    # Don't wash out the outer dark outline completely
                    if r < 70 and g < 40:
                        strength *= 0.25
                    frame[y][x] = lerp_color((r, g, b, a), SHINE_GOLD, strength)

        # Crisp 4-point glint star near top-right rim on frames 5..9
        sx, sy = 24, 7
        if f in (5, 9):
            frame[sy][sx] = SPARKLE_GOLD
        elif f in (6, 8):
            frame[sy][sx] = WHITE
            for ox, oy in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
                frame[sy + oy][sx + ox] = SPARKLE_GOLD
        elif f == 7:
            frame[sy][sx] = WHITE
            for ox, oy in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
                frame[sy + oy][sx + ox] = WHITE
            for ox, oy in [(-2, 0), (2, 0), (0, -2), (0, 2)]:
                frame[sy + oy][sx + ox] = SPARKLE_GOLD

        frames.append(frame)

    # Flatten vertical strip into RGBA rows
    rows: list[bytes] = []
    for frame in frames:
        for row in frame:
            rows.append(b"".join(bytes(px) for px in row))

    mcmeta = {
        "animation": {
            "frametime": 2,
            "frames": [
                {"index": 0, "time": 36},
                1,
                2,
                3,
                4,
                5,
                6,
                7,
                8,
                9,
                10,
            ],
        }
    }
    return W, H * len(frames), rows, mcmeta


def make_pack_icon(base: list[list[tuple[int, int, int, int]]]) -> tuple[int, int, list[bytes]]:
    """
    Create a crisp 256x256 pack.png thumbnail: deep pirate-navy/gold radial backdrop
    with the 32x32 Pirate Token nearest-neighbor upscaled 7x (224x224) centered on top.
    """
    SIZE = 256
    SCALE = 7
    PAD = (SIZE - 32 * SCALE) // 2  # 16px padding on each side

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
            # Subtle vignette background + crisp pixel frame
            if x < 4 or x >= SIZE - 4 or y < 4 or y >= SIZE - 4:
                px = BORDER_OUT
            elif x < 8 or x >= SIZE - 8 or y < 8 or y >= SIZE - 8:
                px = BORDER_HI if (x + y) < SIZE else BORDER_GOLD
            elif x < 11 or x >= SIZE - 11 or y < 11 or y >= SIZE - 11:
                px = BORDER_OUT
            else:
                d = math.hypot(x - cx, y - cy) / (SIZE * 0.65)
                px = lerp_color(BG_INNER, BG_OUTER, min(1.0, d))

            # Composite crisp upscaled Pirate Token sprite
            sx = (x - PAD) // SCALE
            sy = (y - PAD) // SCALE
            if 0 <= sx < 32 and 0 <= sy < 32:
                sp = base[sy][sx]
                if sp[3] > 0:
                    px = sp

            row.extend(px)
        rows.append(bytes(row))

    return SIZE, SIZE, rows


def build_all() -> None:
    base = make_pirate_token_base()
    tex_w, tex_h, tex_rows, mcmeta = make_animated_strip(base)
    icon_w, icon_h, icon_rows = make_pack_icon(base)

    # 1. pack.mcmeta (compatible with Catharsis + config overlays, Firmament, CIT Resewn, OptiFine across 1.8.9 - 26.1+)
    pack_id = "necron_handle_pirate_token"
    pack_mcmeta = {
        "pack": {
            "pack_format": 1,
            "supported_formats": [1, 255],
            "min_format": 1,
            "max_format": 255,
            "description": "\u00a76Pirate Token \u00a77- Turns \u00a7dNecron's Handle \u00a77into the Fortnite Pirate Token",
        },
        "catharsis:pack/v1": {
            "id": pack_id,
            "version": "1.1.0",
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
            ]
        },
    }
    (ROOT / "pack.mcmeta").write_text(
        json.dumps(pack_mcmeta, indent=2) + "\n", encoding="utf-8"
    )

    # 1b. config.catharsis.json (Catharsis settings UI accessible via the cog icon or /catharsis config)
    catharsis_config = [
        {
            "type": "separator",
            "title": {
                "text": "Pirate Token Settings",
                "color": "gold",
                "bold": True,
            },
            "description": {
                "text": "Customize Necron's Handle texture and visible display name.",
                "color": "gray",
            },
        },
        {
            "type": "dropdown",
            "id": "texture_style",
            "title": {"text": "Texture Style"},
            "description": {
                "text": "Choose between the custom animated pixel-art coin or the official Fortnite Pirate Token image.",
                "color": "gray",
            },
            "descriptions": {
                "pixel": {
                    "text": "Custom 32x32 animated gold pirate doubloon pixel art.",
                    "color": "gray",
                },
                "official": {
                    "text": "Official Fortnite Treasure Hunters Pirate Token image (256x256).",
                    "color": "gray",
                },
            },
            "options": [
                {
                    "value": "pixel",
                    "text": {"text": "Pixel Art"},
                    "default": True,
                },
                {
                    "value": "official",
                    "text": {"text": "Official Fortnite"},
                },
            ],
        },
        {
            "type": "dropdown",
            "id": "item_name",
            "title": {"text": "Display Name"},
            "description": {
                "text": "Choose the visible name shown for Necron's Handle.",
                "color": "gray",
            },
            "descriptions": {
                "pirate_token": {
                    "text": "Renames Necron's Handle to Pirate Token.",
                    "color": "gold",
                },
                "pirate_shop_access_token": {
                    "text": "Renames Necron's Handle to Pirate Shop Access Token.",
                    "color": "gold",
                },
            },
            "options": [
                {
                    "value": "pirate_token",
                    "text": {"text": "Pirate Token"},
                    "default": True,
                },
                {
                    "value": "pirate_shop_access_token",
                    "text": {"text": "Pirate Shop Access Token"},
                },
            ],
        },
    ]
    (ROOT / "config.catharsis.json").write_text(
        json.dumps(catharsis_config, indent=2) + "\n", encoding="utf-8"
    )

    # 2. pack.png
    write_png(ROOT / "pack.png", icon_w, icon_h, icon_rows)

    # 3. Catharsis (FurfSky Reborn v2.0+ / modern Hypixel SkyBlock: 1.21.4 - 26.1+)
    catharsis_item_def = {
        "model": {
            "type": "minecraft:model",
            "model": "pirate_token:item/necron_handle",
        }
    }
    catharsis_item_def_official = {
        "model": {
            "type": "minecraft:model",
            "model": "pirate_token:item/necron_handle_official",
        }
    }
    catharsis_model = {
        "parent": "minecraft:item/generated",
        "textures": {
            "layer0": "pirate_token:item/necron_handle",
        },
    }
    catharsis_model_official = {
        "parent": "minecraft:item/generated",
        "textures": {
            "layer0": "pirate_token:item/necron_handle_official",
        },
    }

    p = ROOT / "assets/skyblock/items/necron_handle.json"
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(json.dumps(catharsis_item_def, indent=2) + "\n", encoding="utf-8")

    # Also override Hypixel's official server pack namespace (`hypixel_skyblock`)
    p = ROOT / "assets/hypixel_skyblock/items/necron_handle.json"
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(json.dumps(catharsis_item_def, indent=2) + "\n", encoding="utf-8")

    p = ROOT / "assets/pirate_token/models/item/necron_handle.json"
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(json.dumps(catharsis_model, indent=2) + "\n", encoding="utf-8")

    p = ROOT / "assets/pirate_token/models/item/necron_handle_official.json"
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(json.dumps(catharsis_model_official, indent=2) + "\n", encoding="utf-8")

    catharsis_tex = ROOT / "assets/pirate_token/textures/item/necron_handle.png"
    write_png(catharsis_tex, tex_w, tex_h, tex_rows)
    catharsis_tex.with_suffix(".png.mcmeta").write_text(
        json.dumps(mcmeta, indent=2) + "\n", encoding="utf-8"
    )

    official_src = ROOT / "scripts/official_pirate_token.png"
    if not official_src.exists():
        raise FileNotFoundError(f"Missing official Fortnite Pirate Token texture at {official_src}")
    official_dst = ROOT / "assets/pirate_token/textures/item/necron_handle_official.png"
    official_dst.parent.mkdir(parents=True, exist_ok=True)
    shutil.copyfile(official_src, official_dst)

    def write_catharsis_text_replacements(base_dir: Path, display_name: str) -> None:
        rep = {
            "priority": 0,
            "replacer": {
                "type": "catharsis:regex",
                "regex": "Necron's Handle",
                "replacement": {
                    "text": display_name,
                    "color": "gold",
                    "italic": False,
                },
            },
        }
        for target in ("item", "nametag"):
            out = base_dir / f"assets/pirate_token/catharsis/text_replacements/{target}/necron_handle.json"
            out.parent.mkdir(parents=True, exist_ok=True)
            out.write_text(json.dumps(rep, indent=2) + "\n", encoding="utf-8")

    def write_firmament_text_override(base_dir: Path, display_name: str) -> None:
        override = {
            "match": {
                "regex": ".*Necron's Handle.*",
            },
            "replacements": [
                {
                    "match": "Necron's Handle",
                    "replace": {
                        "text": display_name,
                        "color": "gold",
                        "italic": False,
                    },
                }
            ],
        }
        out = base_dir / "assets/firmskyblock/overrides/texts/necron_handle.json"
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text(json.dumps(override, indent=2) + "\n", encoding="utf-8")

    # Default text replacements ("Pirate Token")
    write_catharsis_text_replacements(ROOT, "Pirate Token")

    # Overlay 1: Official Fortnite Pirate Token texture
    for ns in ("skyblock", "hypixel_skyblock", "firmskyblock"):
        out = ROOT / f"texture_official/assets/{ns}/items/necron_handle.json"
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text(
            json.dumps(catharsis_item_def_official, indent=2) + "\n", encoding="utf-8"
        )

    # Overlay 2: "Pirate Shop Access Token" display name
    write_catharsis_text_replacements(
        ROOT / "name_pirate_shop_access_token", "Pirate Shop Access Token"
    )
    write_firmament_text_override(
        ROOT / "name_pirate_shop_access_token", "Pirate Shop Access Token"
    )

    # 4. Firmament (1.20.4 - 1.21.11 - 26.1+)
    firm_item_def = {
        "model": {
            "type": "minecraft:model",
            "model": "firmskyblock:item/necron_handle",
        }
    }
    firm_model = {
        "parent": "minecraft:item/generated",
        "textures": {
            "layer0": "firmskyblock:item/necron_handle",
        },
    }

    p = ROOT / "assets/firmskyblock/items/necron_handle.json"
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(json.dumps(firm_item_def, indent=2) + "\n", encoding="utf-8")

    p = ROOT / "assets/firmskyblock/models/item/necron_handle.json"
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(json.dumps(firm_model, indent=2) + "\n", encoding="utf-8")

    firm_tex = ROOT / "assets/firmskyblock/textures/item/necron_handle.png"
    write_png(firm_tex, tex_w, tex_h, tex_rows)
    firm_tex.with_suffix(".png.mcmeta").write_text(
        json.dumps(mcmeta, indent=2) + "\n", encoding="utf-8"
    )

    write_firmament_text_override(ROOT, "Pirate Token")

    # 5. OptiFine (1.13 - 1.20.4)
    optifine_dir = ROOT / "assets/minecraft/optifine/cit/necron_handle"
    optifine_dir.mkdir(parents=True, exist_ok=True)
    write_png(optifine_dir / "necron_handle.png", tex_w, tex_h, tex_rows)
    (optifine_dir / "necron_handle.png.mcmeta").write_text(
        json.dumps(mcmeta, indent=2) + "\n", encoding="utf-8"
    )
    (optifine_dir / "necron_handle.properties").write_text(
        "type=item\n"
        "items=minecraft:stick\n"
        "texture=necron_handle.png\n"
        "nbt.ExtraAttributes.id=NECRON_HANDLE\n",
        encoding="utf-8",
    )

    # 6. CIT Resewn (1.20.5 - 1.21.1 data components)
    citresewn_dir = ROOT / "assets/minecraft/citresewn/cit/necron_handle"
    citresewn_dir.mkdir(parents=True, exist_ok=True)
    write_png(citresewn_dir / "necron_handle.png", tex_w, tex_h, tex_rows)
    (citresewn_dir / "necron_handle.png.mcmeta").write_text(
        json.dumps(mcmeta, indent=2) + "\n", encoding="utf-8"
    )
    (citresewn_dir / "necron_handle.properties").write_text(
        "type=item\n"
        "items=minecraft:stick\n"
        "texture=necron_handle.png\n"
        "components.custom_data.id=NECRON_HANDLE\n",
        encoding="utf-8",
    )

    # 7. Legacy OptiFine / MCPatcher (1.8.9)
    mcpatcher_dir = ROOT / "assets/minecraft/mcpatcher/cit/necron_handle"
    mcpatcher_dir.mkdir(parents=True, exist_ok=True)
    write_png(mcpatcher_dir / "necron_handle.png", tex_w, tex_h, tex_rows)
    (mcpatcher_dir / "necron_handle.png.mcmeta").write_text(
        json.dumps(mcmeta, indent=2) + "\n", encoding="utf-8"
    )
    (mcpatcher_dir / "necron_handle.properties").write_text(
        "type=item\n"
        "items=minecraft:stick\n"
        "texture=necron_handle.png\n"
        "nbt.ExtraAttributes.id=NECRON_HANDLE\n",
        encoding="utf-8",
    )

    # Also export a static 256x256 transparent preview of the sprite for easy inspection
    preview_rows: list[bytes] = []
    for y in range(32):
        expanded = b"".join(bytes(px) * 8 for px in base[y])
        for _ in range(8):
            preview_rows.append(expanded)
    write_png(ROOT / "dist/preview_token.png", 256, 256, preview_rows)

    # 8. Package a clean ready-to-install .zip in dist/
    zip_path = ROOT / "dist/NecronHandle-PirateToken.zip"
    zip_path.parent.mkdir(parents=True, exist_ok=True)
    include_paths = [
        ROOT / "pack.mcmeta",
        ROOT / "pack.png",
        ROOT / "config.catharsis.json",
    ]
    for ns in ("skyblock", "hypixel_skyblock", "pirate_token", "firmskyblock", "minecraft"):
        ns_dir = ROOT / "assets" / ns
        for f in sorted(ns_dir.rglob("*")):
            if f.is_file():
                include_paths.append(f)
    for overlay in ("texture_official", "name_pirate_shop_access_token"):
        ov_dir = ROOT / overlay
        for f in sorted(ov_dir.rglob("*")):
            if f.is_file():
                include_paths.append(f)

    with zipfile.ZipFile(zip_path, "w", compression=zipfile.ZIP_DEFLATED) as zf:
        for f in include_paths:
            zf.write(f, arcname=f.relative_to(ROOT).as_posix())

    print(f"Built resource pack successfully -> {zip_path} ({zip_path.stat().st_size} bytes)")


if __name__ == "__main__":
    build_all()
