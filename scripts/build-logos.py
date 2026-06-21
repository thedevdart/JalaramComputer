"""Build gold full logo + JC-only mark from source artwork."""
from __future__ import annotations

import colorsys
import shutil
from pathlib import Path

from PIL import Image

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "public" / "assets" / "images" / "logo-white-bg.png"
OUT_FULL = ROOT / "public" / "assets" / "images" / "logo.png"
OUT_JC = ROOT / "public" / "assets" / "images" / "logo-jc.png"

GOLD = (212, 175, 55)
GOLD_HLS = colorsys.rgb_to_hls(GOLD[0] / 255, GOLD[1] / 255, GOLD[2] / 255)

WHITE_THRESH = 238
WHITE_FEATHER = 22


def is_background(r: int, g: int, b: int) -> bool:
    spread = max(r, g, b) - min(r, g, b)
    return r >= WHITE_THRESH and g >= WHITE_THRESH and b >= WHITE_THRESH and spread < 18


def background_alpha(r: int, g: int, b: int, a: int) -> int:
    if not is_background(r, g, b):
        return a
    white_dist = 255 - min(r, g, b)
    if white_dist >= WHITE_FEATHER:
        return 0
    return min(a, int(255 * white_dist / WHITE_FEATHER))


def is_red(r: int, g: int, b: int, a: int) -> bool:
    if a < 20:
        return False
    if r < 90:
        return False
    return r > g + 18 and r > b + 18


def red_to_gold(r: int, g: int, b: int) -> tuple[int, int, int]:
    h, lightness, saturation = colorsys.rgb_to_hls(r / 255, g / 255, b / 255)
    if saturation < 0.08:
        return r, g, b
    gold_h, _, _ = GOLD_HLS
    nr, ng, nb = colorsys.hls_to_rgb(gold_h, lightness, min(1.0, saturation * 1.05))
    return int(nr * 255), int(ng * 255), int(nb * 255)


def process_pixel(r: int, g: int, b: int, a: int) -> tuple[int, int, int, int]:
    alpha = background_alpha(r, g, b, a)
    if alpha == 0:
        return r, g, b, 0
    if is_red(r, g, b, alpha):
        r, g, b = red_to_gold(r, g, b)
    return r, g, b, alpha


def build_rgba(src: Path) -> Image.Image:
    img = Image.open(src).convert("RGBA")
    px = img.load()
    w, h = img.size
    for y in range(h):
        for x in range(w):
            px[x, y] = process_pixel(*px[x, y])
    return img


def crop_jc_mark(full: Image.Image) -> Image.Image:
    w, h = full.size
    px = full.load()
    top = h
    bottom = 0
    left = w
    right = 0

    for y in range(h):
        for x in range(w):
            if px[x, y][3] >= 24:
                top = min(top, y)
                bottom = max(bottom, y)
                left = min(left, x)
                right = max(right, x)

    row_counts = [
        sum(1 for x in range(left, right + 1) if px[x, y][3] >= 24)
        for y in range(top, bottom + 1)
    ]

    # Find the horizontal gap between icon and wordmark in the lower half only
    search_start = int(len(row_counts) * 0.45)
    split_offset = len(row_counts)
    quiet = 0
    for i in range(search_start, len(row_counts)):
        count = row_counts[i]
        if count <= 8:
            quiet += 1
            if quiet >= 8:
                split_offset = i - quiet + 1
                break
        else:
            quiet = 0

    if split_offset >= len(row_counts) - 10:
        split_offset = int(len(row_counts) * 0.62)

    jc_bottom = top + split_offset
    jc_top = top
    jc_left = left
    jc_right = right

    for y in range(jc_top, jc_bottom):
        for x in range(left, right + 1):
            if px[x, y][3] >= 24:
                jc_left = min(jc_left, x)
                jc_right = max(jc_right, x)

    pad = int((jc_right - jc_left) * 0.05)
    box = (
        max(0, jc_left - pad),
        max(0, jc_top - pad),
        min(w, jc_right + pad + 1),
        min(h, jc_bottom),
    )
    return full.crop(box)


def main() -> None:
    if not SRC.exists():
        raise SystemExit(f"Missing source artwork: {SRC}")

    full = build_rgba(SRC)
    jc = crop_jc_mark(full)

    full.save(OUT_FULL, optimize=True)
    jc.save(OUT_JC, optimize=True)

    print(f"Wrote full logo: {OUT_FULL} ({full.size[0]}x{full.size[1]})")
    print(f"Wrote JC mark:   {OUT_JC} ({jc.size[0]}x{jc.size[1]})")


if __name__ == "__main__":
    main()
