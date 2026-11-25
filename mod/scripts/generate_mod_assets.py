#!/usr/bin/env python3
"""
Generates the Pirate Token Drop Mod's GUI textures (sunburst, glow, token variants, icon)
and synthesizes the triumphant pirate-treasure jackpot fanfare OGG sound effect.
"""

from __future__ import annotations

import json
import math
import shutil
import struct
import subprocess
import wave
import zlib
from pathlib import Path

MOD_ROOT = Path(__file__).resolve().parent.parent
REPO_ROOT = MOD_ROOT.parent
RES_ROOT = MOD_ROOT / "src/main/resources/assets/piratetoken"


def write_png(path: Path, width: int, height: int, rgba_rows: list[bytes]) -> None:
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


def make_sunburst(size: int = 256) -> list[bytes]:
    """256x256 smooth 12-ray golden Fortnite-style sunburst with soft radial falloff."""
    cx = cy = (size - 1) / 2.0
    max_r = size * 0.49
    rows: list[bytes] = []
    for y in range(size):
        row = bytearray()
        for x in range(size):
            dx, dy = x - cx, y - cy
            r = math.hypot(dx, dy)
            if r >= max_r:
                row.extend((255, 215, 70, 0))
                continue
            nr = r / max_r
            ang = math.atan2(dy, dx)
            # 12 crisp alternating wide/narrow golden rays
            ray1 = (math.sin(ang * 12.0) + 1.0) * 0.5
            ray2 = (math.sin(ang * 24.0 + 0.7) + 1.0) * 0.5
            ray = pow(ray1, 1.8) * 0.8 + pow(ray2, 2.5) * 0.25

            # Soft radial envelope: bright core, gentle feather to transparent edge
            radial = pow(max(0.0, 1.0 - nr), 1.35)
            core_boost = math.exp(-(nr * nr) / 0.08) * 0.85
            alpha = min(1.0, (ray * radial * 0.95) + core_boost)

            # Warm white-gold center transitioning to rich Fortnite amber-gold tips
            t = min(1.0, nr * 1.15)
            cr = int(round(255))
            cg = int(round(248 * (1.0 - t) + 195 * t))
            cb = int(round(200 * (1.0 - t) + 35 * t))
            ca = int(round(alpha * 255))
            row.extend((cr, cg, cb, ca))
        rows.append(bytes(row))
    return rows


def make_glow(size: int = 256) -> list[bytes]:
    """256x256 warm golden radial treasure bloom halo."""
    cx = cy = (size - 1) / 2.0
    max_r = size * 0.49
    rows: list[bytes] = []
    for y in range(size):
        row = bytearray()
        for x in range(size):
            r = math.hypot(x - cx, y - cy)
            if r >= max_r:
                row.extend((255, 200, 40, 0))
                continue
            nr = r / max_r
            a = pow(max(0.0, 1.0 - nr), 2.2)
            cr = 255
            cg = int(round(245 * (1.0 - nr) + 170 * nr))
            cb = int(round(180 * (1.0 - nr) + 20 * nr))
            row.extend((cr, cg, cb, int(round(a * 255))))
        rows.append(bytes(row))
    return rows


def synthesize_fanfare_ogg(out_ogg: Path) -> None:
    """
    Synthesize a punchy, triumphant ~2.7s Fortnite-style golden pirate treasure jackpot fanfare:
    - Sparkly ascending golden chime arpeggio (0.00s - 0.36s)
    - Big triumphant brass/bell major-9th treasure chord swell (0.30s - 2.20s)
    - Shimmering high gold-coin sparkle pings (0.35s - 2.40s)
    """
    sr = 44100
    duration = 2.75
    n_samples = int(sr * duration)
    buf = [0.0] * n_samples

    def add_tone(
        start: float,
        dur: float,
        freq: float,
        amp: float,
        attack: float = 0.012,
        decay: float = 0.35,
        harmonics: list[tuple[float, float]] | None = None,
    ) -> None:
        if harmonics is None:
            harmonics = [(1.0, 1.0), (2.0, 0.35), (3.0, 0.14)]
        i0 = max(0, int(start * sr))
        i1 = min(n_samples, int((start + dur) * sr))
        for i in range(i0, i1):
            t = (i - i0) / sr
            env = (t / attack) if t < attack else math.exp(-(t - attack) / decay)
            # Smooth fade-out tail
            rem = (i1 - i) / sr
            if rem < 0.04:
                env *= rem / 0.04
            val = 0.0
            for mult, h_amp in harmonics:
                val += math.sin(2.0 * math.pi * freq * mult * t) * h_amp
            buf[i] += val * amp * env

    # 1. Chest burst low impact thump (0.00s)
    i_end = int(0.28 * sr)
    for i in range(i_end):
        t = i / sr
        f = 130.0 * math.exp(-t * 9.0) + 48.0
        env = math.exp(-t * 10.5)
        buf[i] += math.sin(2.0 * math.pi * f * t) * 0.36 * env

    # 2. Fast sparkling golden arpeggio leading into the jackpot chord (D5 -> F#5 -> A5 -> C#6 -> D6)
    arp_notes = [
        (0.02, 587.33),   # D5
        (0.08, 739.99),   # F#5
        (0.14, 880.00),   # A5
        (0.20, 1108.73),  # C#6
        (0.26, 1174.66),  # D6
    ]
    bell_harm = [(1.0, 1.0), (2.0, 0.42), (3.0, 0.22), (4.0, 0.10)]
    for t0, f in arp_notes:
        add_tone(t0, 0.75, f, 0.16, attack=0.006, decay=0.22, harmonics=bell_harm)

    # 3. Triumphant pirate brass/chime D-major-9 jackpot chord swell (0.28s)
    brass_harm = [(1.0, 1.0), (2.0, 0.55), (3.0, 0.30), (4.0, 0.18), (5.0, 0.08)]
    chord = [
        (146.83, 0.18, 0.95),  # D3 bass
        (293.66, 0.22, 0.85),  # D4
        (440.00, 0.18, 0.80),  # A4
        (587.33, 0.20, 0.80),  # D5
        (739.99, 0.17, 0.75),  # F#5
        (880.00, 0.14, 0.70),  # A5
        (1318.51, 0.09, 0.65), # E6 (bright major-9th sparkle!)
    ]
    for freq, amp, dec in chord:
        add_tone(0.28, 2.35, freq, amp, attack=0.045, decay=dec, harmonics=brass_harm)

    # 4. Second heroic brass accent hit at 0.56s (gives that iconic "TA-DAAA!" pirate fanfare bounce)
    accent = [
        (293.66, 0.16, 1.05),
        (587.33, 0.18, 1.00),
        (739.99, 0.16, 0.95),
        (880.00, 0.15, 0.90),
        (1174.66, 0.15, 0.85),
    ]
    for freq, amp, dec in accent:
        add_tone(0.56, 2.10, freq, amp, attack=0.025, decay=dec, harmonics=brass_harm)

    # 5. Sparkling gold coin chimes cascading down the tail
    coins = [
        (0.38, 2349.32), (0.48, 2959.96), (0.62, 3520.00),
        (0.76, 2637.02), (0.92, 3135.96), (1.10, 3520.00),
        (1.30, 4186.01),
    ]
    coin_harm = [(1.0, 1.0), (2.76, 0.28)]
    for t0, f in coins:
        add_tone(t0, 0.55, f, 0.065, attack=0.003, decay=0.14, harmonics=coin_harm)

    # Normalize safely to -1.5 dBFS peak
    peak = max(abs(s) for s in buf) or 1.0
    scale = 0.84 / peak
    pcm = bytearray()
    for s in buf:
        v = max(-32767, min(32767, int(round(s * scale * 32767.0))))
        pcm.extend(struct.pack("<h", v))

    out_ogg.parent.mkdir(parents=True, exist_ok=True)
    tmp_wav = out_ogg.with_suffix(".tmp.wav")
    with wave.open(str(tmp_wav), "wb") as wf:
        wf.setnchannels(1)
        wf.setsampwidth(2)
        wf.setframerate(sr)
        wf.writeframes(bytes(pcm))

    subprocess.check_call(
        ["ffmpeg", "-y", "-i", str(tmp_wav), "-ac", "2", "-c:a", "vorbis", "-strict", "-2", "-b:a", "128k", str(out_ogg)],
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    )
    tmp_wav.unlink()


def main() -> None:
    RES_ROOT.mkdir(parents=True, exist_ok=True)

    # Copy icons & token textures from the resource pack
    shutil.copyfile(REPO_ROOT / "pack.png", RES_ROOT / "icon.png")
    gui_dir = RES_ROOT / "textures/gui"
    gui_dir.mkdir(parents=True, exist_ok=True)
    shutil.copyfile(REPO_ROOT / "scripts/official_pirate_token.png", gui_dir / "token_official.png")
    shutil.copyfile(REPO_ROOT / "dist/preview_token.png", gui_dir / "token_pixel.png")

    # Generate sunburst & glow overlays
    write_png(gui_dir / "sunburst.png", 256, 256, make_sunburst(256))
    write_png(gui_dir / "glow.png", 256, 256, make_glow(256))

    # Synthesize pirate treasure fanfare .ogg + sounds.json
    synthesize_fanfare_ogg(RES_ROOT / "sounds/pirate_token_drop.ogg")
    sounds_json = {
        "pirate_token_drop": {
            "subtitle": "Pirate Token Drop Fanfare",
            "sounds": [
                {
                    "name": "piratetoken:pirate_token_drop",
                    "stream": False,
                }
            ],
        }
    }
    (RES_ROOT / "sounds.json").write_text(json.dumps(sounds_json, indent=2) + "\n", encoding="utf-8")
    print("Generated all Pirate Token mod assets successfully!")


if __name__ == "__main__":
    main()
