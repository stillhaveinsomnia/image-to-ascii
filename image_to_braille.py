#!/usr/bin/env python3
"""
image_to_braille.py — превращает изображение в Braille Unicode арт.
Каждый символ Braille содержит 2x4 пикселя, что даёт 8x больше деталей
чем обычный ASCII при том же размере текста.

Использование:
    python image_to_braille.py dym.jpg --width 40 --output dym_braille.txt
    python image_to_braille.py dym.jpg --width 40 --invert --output dym_braille.txt
"""

import argparse
import sys

try:
    from PIL import Image
except ImportError:
    sys.exit("Нужна библиотека Pillow. Установите: pip install pillow")


# Braille Unicode начинается с U+2800
# Каждый символ — матрица 2x4 точек
# Биты соответствуют позициям:
#   0  3
#   1  4
#   2  5
#   6  7
BRAILLE_OFFSET = 0x2800

# Маппинг позиций пикселей (row, col) -> бит
PIXEL_MAP = (
    (0x01, 0x08),
    (0x02, 0x10),
    (0x04, 0x20),
    (0x40, 0x80),
)


def image_to_braille(
    img: Image.Image,
    width: int = 40,
    threshold: int = 128,
    invert: bool = False,
) -> str:
    """Конвертирует изображение в Braille арт."""
    # Braille: каждый символ = 2 пикселя в ширину, 4 пикселя в высоту
    pixel_width = width * 2
    w_orig, h_orig = img.size
    aspect = h_orig / w_orig
    pixel_height = int(pixel_width * aspect)
    # Округляем до кратного 4
    pixel_height = (pixel_height // 4) * 4

    img = img.resize((pixel_width, pixel_height))
    gray = img.convert("L")
    pixels = gray.load()

    lines = []
    for y in range(0, pixel_height, 4):
        row_chars = []
        for x in range(0, pixel_width, 2):
            braille = 0
            for dy in range(4):
                for dx in range(2):
                    py = y + dy
                    px = x + dx
                    if py < pixel_height and px < pixel_width:
                        val = pixels[px, py]
                        if invert:
                            is_on = val > threshold
                        else:
                            is_on = val < threshold
                        if is_on:
                            braille |= PIXEL_MAP[dy][dx]
            row_chars.append(chr(BRAILLE_OFFSET + braille))
        lines.append("".join(row_chars))

    return "\n".join(lines)


def main():
    parser = argparse.ArgumentParser(description="Конвертирует изображение в Braille Unicode арт")
    parser.add_argument("image", help="Путь к изображению")
    parser.add_argument("--width", type=int, default=40, help="Ширина в символах (по умолчанию 40)")
    parser.add_argument("--threshold", type=int, default=128, help="Порог яркости 0-255 (по умолчанию 128)")
    parser.add_argument("--invert", action="store_true", help="Инвертировать (для тёмного фона)")
    parser.add_argument("--output", help="Сохранить в файл")

    args = parser.parse_args()

    img = Image.open(args.image).convert("RGB")
    result = image_to_braille(
        img,
        width=args.width,
        threshold=args.threshold,
        invert=args.invert,
    )

    print(result)

    if args.output:
        with open(args.output, "w", encoding="utf-8") as f:
            f.write(result)
        print(f"\nСохранено: {args.output}", file=sys.stderr)


if __name__ == "__main__":
    main()
