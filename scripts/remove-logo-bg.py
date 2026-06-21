"""Remove near-white background from logo.png, preserving logo artwork."""
from __future__ import annotations

import shutil
from pathlib import Path

from PIL import Image

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "public" / "assets" / "images" / "logo.png"
BACKUP = SRC.with_name("logo-white-bg.png")

THRESH = 238
FEATHER = 22


def main() -> None:
    if not SRC.exists():
        raise SystemExit(f"Missing {SRC}")

    if not BACKUP.exists():
        shutil.copy2(SRC, BACKUP)

    img = Image.open(SRC).convert("RGBA")
    px = img.load()
    w, h = img.size
    transparent = 0

    for y in range(h):
        for x in range(w):
            r, g, b, a = px[x, y]
            white_dist = 255 - min(r, g, b)
            spread = max(r, g, b) - min(r, g, b)
            is_bg = r >= THRESH and g >= THRESH and b >= THRESH and spread < 18
            if not is_bg:
                continue
            if white_dist >= FEATHER:
                px[x, y] = (r, g, b, 0)
                transparent += 1
            else:
                alpha = int(255 * white_dist / FEATHER)
                px[x, y] = (r, g, b, min(a, alpha))
                if alpha == 0:
                    transparent += 1

    img.save(SRC, optimize=True)
    print(f"Saved transparent logo: {SRC}")
    print(f"Dimensions: {w}x{h}")
    print(f"Transparent pixels: {transparent} / {w * h}")
    print(f"Backup kept at: {BACKUP}")


if __name__ == "__main__":
    main()
