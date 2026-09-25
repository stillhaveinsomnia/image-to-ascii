#!/usr/bin/env python3
"""
ascii_braille_animation.py

Показывает анимацию в терминале в формате ASCII + Braille.

Примеры:
    python ascii_braille_animation.py --folder frames --fps 8 --mode both --loop
    python ascii_braille_animation.py --folder frames --fps 10 --mode ascii --width 100
    python ascii_braille_animation.py --image demo.png --fps 6 --mode braille --loop

Требуется:
    pip install pillow
"""

import argparse
import re
import sys
import time
from pathlib import Path

try:
    from PIL import Image, ImageSequence
except ImportError:
    sys.exit("Нужна библиотека Pillow. Установите: pip install pillow")

try:
    import cv2
except ImportError:
    cv2 = None

from image_to_ascii import image_to_ascii
from image_to_braille import image_to_braille


CLEAR_SEQ = "\033[H\033[2J\033[3J"


def natural_sort_key(value: str):
    return [int(part) if part.isdigit() else part.lower() for part in re.split(r"(\d+)", value)]


def load_frames_from_dir(folder: str):
    folder_path = Path(folder)
    if not folder_path.exists() or not folder_path.is_dir():
        raise FileNotFoundError(f"Папка не найдена: {folder}")

    extensions = {".png", ".jpg", ".jpeg", ".bmp", ".gif", ".webp"}
    files = [p for p in folder_path.iterdir() if p.is_file() and p.suffix.lower() in extensions]
    if not files:
        raise FileNotFoundError(f"В папке нет изображений: {folder}")

    files.sort(key=lambda p: natural_sort_key(p.name))
    frames = []
    for file in files:
        with Image.open(file) as img:
            frames.append(img.convert("RGB"))
    return frames


def load_frames_from_image(path: str):
    image_path = Path(path)
    if not image_path.exists():
        raise FileNotFoundError(f"Файл не найден: {path}")

    with Image.open(image_path) as img:
        frames = []
        if getattr(img, "is_animated", False):
            for frame in ImageSequence.Iterator(img):
                frames.append(frame.convert("RGB"))
        else:
            frames.append(img.convert("RGB"))
    return frames


def render_ascii_frame(img, width: int, invert: bool, sharp: bool, charset: str):
    return image_to_ascii(
        img,
        width=width,
        charset_name=charset,
        invert=invert,
        color=False,
        sharp=sharp,
    )


def apply_float_effect(ascii_text: str, mouse_x: float = 0.5, mouse_y: float = 0.5, strength: int = 2):
    """Сдвигает ASCII по эффекту "плавающего" при наведении/перетаскивании по кадру."""
    lines = ascii_text.splitlines()
    if not lines:
        return ascii_text

    width = max(len(line) for line in lines)
    height = len(lines)
    if width == 0 or height == 0:
        return ascii_text

    x_shift = int((mouse_x - 0.5) * width * strength * 0.8)
    y_shift = int((mouse_y - 0.5) * height * strength * 0.8)

    shifted = []
    for y in range(height):
        row = []
        for x in range(width):
            sx = x - x_shift
            sy = y - y_shift
            if 0 <= sx < width and 0 <= sy < height:
                ch = lines[sy][sx] if sx < len(lines[sy]) else " "
            else:
                ch = " "
            row.append(ch)
        shifted.append("".join(row).rstrip())

    return "\n".join(shifted)


def render_braille_frame(img, width: int, invert: bool, threshold: int):
    return image_to_braille(
        img,
        width=width,
        threshold=threshold,
        invert=invert,
    )


def render_frame(frame, mode: str, width: int, charset: str, invert: bool, sharp: bool,
                braille_width: int, threshold: int, float_mode: bool = False,
                mouse_x: float = 0.5, mouse_y: float = 0.5, float_strength: int = 2):
    if mode == "ascii":
        text = render_ascii_frame(frame, width=width, invert=invert, sharp=sharp, charset=charset)
        if float_mode:
            text = apply_float_effect(text, mouse_x=mouse_x, mouse_y=mouse_y, strength=float_strength)
        return text
    if mode == "braille":
        return render_braille_frame(frame, width=braille_width, invert=invert, threshold=threshold)

    ascii_text = render_ascii_frame(frame, width=width, invert=invert, sharp=sharp, charset=charset)
    if float_mode:
        ascii_text = apply_float_effect(ascii_text, mouse_x=mouse_x, mouse_y=mouse_y, strength=float_strength)
    braille_text = render_braille_frame(frame, width=braille_width, invert=invert, threshold=threshold)
    return combine_ascii_and_braille(ascii_text, braille_text)


def pad_lines(lines, width: int):
    if not lines:
        return []
    return [line.ljust(width)[:width] for line in lines]


def combine_ascii_and_braille(ascii_text: str, braille_text: str, gap: int = 4):
    ascii_lines = ascii_text.splitlines() or [""]
    braille_lines = braille_text.splitlines() or [""]

    ascii_width = max(len(line) for line in ascii_lines)
    braille_width = max(len(line) for line in braille_lines)

    total_lines = max(len(ascii_lines), len(braille_lines))
    combined = []
    for idx in range(total_lines):
        a = ascii_lines[idx] if idx < len(ascii_lines) else " " * ascii_width
        b = braille_lines[idx] if idx < len(braille_lines) else " " * braille_width
        combined.append(f"{a.ljust(ascii_width)}{' ' * gap}{b.ljust(braille_width)}")

    return "\n".join(combined)


def print_frame(rendered: str, clear: bool):
    if clear and sys.stdout.isatty():
        sys.stdout.write(CLEAR_SEQ)
    sys.stdout.write(rendered)
    sys.stdout.write("\n")
    sys.stdout.flush()


def load_frames_from_video(path: str):
    if cv2 is None:
        raise RuntimeError("Для видео нужен OpenCV. Установите: pip install opencv-python-headless")

    capture = cv2.VideoCapture(path)
    if not capture.isOpened():
        raise FileNotFoundError(f"Не удалось открыть видео: {path}")

    frames = []
    while True:
        ok, frame = capture.read()
        if not ok:
            break
        rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        frames.append(Image.fromarray(rgb))

    capture.release()
    if not frames:
        raise ValueError(f"Видео не содержит кадров: {path}")
    return frames


def export_frames_to_file(frames, output_path: str, mode: str, width: int, charset: str,
                         invert: bool, sharp: bool, braille_width: int, threshold: int,
                         export_format: str, float_mode: bool = False,
                         mouse_x: float = 0.5, mouse_y: float = 0.5,
                         float_strength: int = 2):
    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    txt_parts = []
    ansi_parts = []
    for idx, frame in enumerate(frames):
        rendered = render_frame(
            frame,
            mode,
            width,
            charset,
            invert,
            sharp,
            braille_width,
            threshold,
            float_mode=float_mode,
            mouse_x=mouse_x,
            mouse_y=mouse_y,
            float_strength=float_strength,
        )
        txt_parts.append(f"---FRAME {idx + 1}---\n{rendered}\n")
        ansi_parts.append(f"\033[H\033[2J---FRAME {idx + 1}---\n{rendered}\n")

    plain = "\n".join(txt_parts)
    if export_format in {"txt", "both"}:
        txt_file = output_path.with_suffix(".txt") if output_path.suffix.lower() != ".txt" else output_path
        txt_file.write_text(plain, encoding="utf-8")
    if export_format in {"ansi", "both"}:
        ansi_file = output_path.with_suffix(".ansi") if output_path.suffix.lower() != ".ansi" else output_path
        ansi_file.write_text("\n".join(ansi_parts), encoding="utf-8")


def play_ansi_file(path: str, fps: float, loop: bool = False):
    ansi_path = Path(path)
    if not ansi_path.exists():
        raise FileNotFoundError(f"ANSI-файл не найден: {path}")

    text = ansi_path.read_text(encoding="utf-8")
    blocks = [part.strip() for part in re.split(r"\n*---FRAME \d+---\n*", text) if part.strip()]
    if not blocks:
        raise ValueError(f"Файл не содержит кадров ANSI: {path}")

    delay = 1.0 / fps if fps > 0 else 0.1
    while True:
        for block in blocks:
            sys.stdout.write(block)
            sys.stdout.write("\n")
            sys.stdout.flush()
            time.sleep(delay)
        if not loop:
            break


def play_animation(frames, fps: float, mode: str, width: int, charset: str, invert: bool, sharp: bool,
                  loop: bool, clear: bool, braille_width: int, threshold: int,
                  float_mode: bool = False, mouse_x: float = 0.5, mouse_y: float = 0.5, float_strength: int = 2):
    if not frames:
        raise ValueError("Нет кадров для воспроизведения")

    delay = 1.0 / fps if fps > 0 else 0.1

    while True:
        for frame in frames:
            rendered = render_frame(
                frame,
                mode,
                width,
                charset,
                invert,
                sharp,
                braille_width,
                threshold,
                float_mode=float_mode,
                mouse_x=mouse_x,
                mouse_y=mouse_y,
                float_strength=float_strength,
            )
            print_frame(rendered, clear=clear)
            time.sleep(delay)

        if not loop:
            break


def main():
    parser = argparse.ArgumentParser(description="ASCII + Braille анимация в терминале")
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--folder", help="Папка с изображениями-кадрами")
    group.add_argument("--image", help="Один файл изображения или GIF")
    group.add_argument("--video", help="Видео-файл для показа в реальном времени")

    parser.add_argument("--live", action="store_true", help="Показывать видео в режиме реального времени")
    parser.add_argument("--mode", choices=["ascii", "braille", "both"], default="both", help="Какая версия выводится")
    parser.add_argument("--width", type=int, default=80, help="Ширина ASCII-кадра в символах")
    parser.add_argument("--braille-width", type=int, default=30, help="Ширина блока Braille")
    parser.add_argument("--charset", choices=["blocks", "classic", "binary"], default="blocks", help="Набор ASCII-символов")
    parser.add_argument("--fps", type=float, default=8.0, help="Кадров в секунду. Для видео можно оставить 0, чтобы использовать FPS файла")
    parser.add_argument("--loop", action="store_true", help="Зациклить анимацию")
    parser.add_argument("--no-clear", action="store_true", help="Не очищать терминал перед каждым кадром")
    parser.add_argument("--invert", action="store_true", help="Инвертировать яркость")
    parser.add_argument("--sharp", action="store_true", help="Сделать ASCII более контрастным")
    parser.add_argument("--threshold", type=int, default=128, help="Порог для Braille (0..255)")
    parser.add_argument("--float", action="store_true", help="Включить эффект плавающего ASCII при наведении/перемещении")
    parser.add_argument("--float-strength", type=int, default=2, help="Сила плавающего эффекта")
    parser.add_argument("--mouse-x", type=float, default=0.5, help="Положение ""курсора"" по X в диапазоне 0..1")
    parser.add_argument("--mouse-y", type=float, default=0.5, help="Положение ""курсора"" по Y в диапазоне 0..1")
    parser.add_argument("--export", help="Путь к файлу для экспорта: .txt, .ansi или .txt/.ansi")
    parser.add_argument("--export-format", choices=["txt", "ansi", "both"], default="txt", help="Формат экспорта")
    parser.add_argument("--ansi-player", help="Воспроизвести .ansi-файл в терминале")

    args = parser.parse_args()

    if args.ansi_player:
        play_ansi_file(args.ansi_player, fps=args.fps if args.fps > 0 else 12.0, loop=args.loop)
        return

    try:
        if args.folder:
            frames = load_frames_from_dir(args.folder)
        elif args.video:
            frames = load_frames_from_video(args.video)
        else:
            frames = load_frames_from_image(args.image)
    except Exception as exc:
        parser.exit(1, f"Ошибка: {exc}\n")

    if args.export:
        export_path = Path(args.export)
        export_frames_to_file(
            frames=frames,
            output_path=str(export_path),
            mode=args.mode,
            width=args.width,
            charset=args.charset,
            invert=args.invert,
            sharp=args.sharp,
            braille_width=args.braille_width,
            threshold=args.threshold,
            export_format=args.export_format,
            float_mode=args.float,
            mouse_x=max(0.0, min(1.0, args.mouse_x)),
            mouse_y=max(0.0, min(1.0, args.mouse_y)),
            float_strength=args.float_strength,
        )
        print(f"Экспорт завершён: {export_path}")

    fps = args.fps if args.fps > 0 else 24.0
    play_animation(
        frames=frames,
        fps=fps,
        mode=args.mode,
        width=args.width,
        charset=args.charset,
        invert=args.invert,
        sharp=args.sharp,
        loop=args.loop,
        clear=not args.no_clear,
        braille_width=args.braille_width,
        threshold=args.threshold,
        float_mode=args.float,
        mouse_x=max(0.0, min(1.0, args.mouse_x)),
        mouse_y=max(0.0, min(1.0, args.mouse_y)),
        float_strength=args.float_strength,
    )


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\nОстановка анимации")
        sys.exit(0)
