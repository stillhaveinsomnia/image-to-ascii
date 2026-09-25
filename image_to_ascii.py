#!/usr/bin/env python3
"""
image_to_ascii.py — превращает фотографию (например, лицо) в ASCII-арт,
похожий на стиль неофетч-баннеров (как в примере README.md).

Использование:
    python image_to_ascii.py photo.jpg
    python image_to_ascii.py photo.jpg --width 100 --output ascii.txt
    python image_to_ascii.py photo.jpg --sharp --output ascii.txt    # более чёткий/контрастный вариант
    python image_to_ascii.py photo.jpg --color            # цветной вывод в терминале
    python image_to_ascii.py photo.jpg --invert            # инвертировать яркость
    python image_to_ascii.py photo.jpg --charset blocks    # набор символов: blocks | classic | binary

Зависимости:
    pip install pillow
"""

import argparse
import sys

try:
    from PIL import Image
except ImportError:
    sys.exit("Нужна библиотека Pillow. Установите: pip install pillow")


# Наборы символов от "пусто" (светлое) к "плотно" (тёмное)
CHARSETS = {
    # похоже на пример со скриншота — блочные градации
    "blocks": " .:-=+*#%@",
    # классический набор для ASCII-арта
    "classic": " .'`^\",:;Il!i><~+_-?][}{1)(|\\/tfjrxnuvczXYUJCLQ0OZmwqpdbkhao*#MW&8%B@$",
    # только два символа — грубый, контрастный стиль
    "binary": " #",
}

# Символы шрифта моноширинные обычно в ~2 раза выше, чем шире —
# поэтому при пересчёте высоты применяем коэффициент коррекции
CHAR_ASPECT_CORRECTION = 0.55


def load_image(path: str) -> Image.Image:
    img = Image.open(path)
    img = img.convert("RGB")
    return img


def resize_image(img: Image.Image, new_width: int) -> Image.Image:
    width, height = img.size
    aspect_ratio = height / width
    new_height = max(1, int(new_width * aspect_ratio * CHAR_ASPECT_CORRECTION))
    return img.resize((new_width, new_height))


def pixel_to_char(brightness: int, charset: str, invert: bool, sharp: bool = False) -> str:
    if invert:
        brightness = 255 - brightness

    if sharp:
        # Увеличиваем контраст: тёмные области становятся темнее,
        # светлые — светлее, чтобы ASCII выглядел более чётко.
        brightness = (brightness / 255.0) ** 1.7 * 255.0

    index = int((brightness / 255) * (len(charset) - 1))
    return charset[index]


def image_to_ascii(
    img: Image.Image,
    width: int = 100,
    charset_name: str = "blocks",
    invert: bool = False,
    color: bool = False,
    sharp: bool = False,
) -> str:
    charset = CHARSETS.get(charset_name, CHARSETS["blocks"])
    small = resize_image(img, width)
    gray = small.convert("L")

    lines = []
    pixels_rgb = small.load()
    pixels_gray = gray.load()
    w, h = small.size

    for y in range(h):
        row_chars = []
        for x in range(w):
            brightness = pixels_gray[x, y]
            char = pixel_to_char(brightness, charset, invert, sharp=sharp)

            if color:
                r, g, b = pixels_rgb[x, y]
                # ANSI truecolor escape-код
                row_chars.append(f"\033[38;2;{r};{g};{b}m{char}\033[0m")
            else:
                row_chars.append(char)
        lines.append("".join(row_chars))

    return "\n".join(lines)


def main():
    parser = argparse.ArgumentParser(description="Конвертирует изображение в ASCII-арт")
    parser.add_argument("image", help="Путь к файлу изображения (jpg, png и т.д.)")
    parser.add_argument("--width", type=int, default=100, help="Ширина результата в символах (по умолчанию 100)")
    parser.add_argument("--charset", choices=CHARSETS.keys(), default="blocks", help="Набор символов")
    parser.add_argument("--invert", action="store_true", help="Инвертировать яркость (для тёмного фона)")
    parser.add_argument("--sharp", action="store_true", help="Более чёткий и контрастный ASCII-вариант")
    parser.add_argument("--color", action="store_true", help="Цветной вывод (только в терминале с поддержкой ANSI)")
    parser.add_argument("--output", help="Сохранить результат в текстовый файл (без цвета)")

    args = parser.parse_args()

    img = load_image(args.image)
    ascii_art = image_to_ascii(
        img,
        width=args.width,
        charset_name=args.charset,
        invert=args.invert,
        color=args.color,
        sharp=args.sharp,
    )

    print(ascii_art)

    if args.output:
        # для файла всегда сохраняем версию без ANSI-цвета
        plain = image_to_ascii(
            img,
            width=args.width,
            charset_name=args.charset,
            invert=args.invert,
            color=False,
            sharp=args.sharp,
        )
        with open(args.output, "w", encoding="utf-8") as f:
            f.write(plain)
        print(f"\nСохранено в файл: {args.output}", file=sys.stderr)


if __name__ == "__main__":
    main()
