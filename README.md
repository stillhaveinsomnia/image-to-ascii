# ASCII + Braille Animation

Небольшой Python-скрипт для показа анимации в терминале в формате ASCII, Braille или обоих сразу.

## Что умеет

- показывать анимацию из папки с изображениями
- проигрывать GIF или видео
- выводить ASCII, Braille или оба режима одновременно
- поддерживать “плавающий” эффект ASCII при смещении по координатам
- экспортировать результат в `.txt` и `.ansi`
- воспроизводить `.ansi`-файлы в терминале

## Установка

```powershell
python -m pip install pillow
```

Для видео также можно установить OpenCV:

```powershell
python -m pip install opencv-python-headless
```

## Быстрый старт

### 1) Папка с кадрами

```powershell
python .\ascii_braille_animation.py --folder .\frames --fps 8 --mode both --loop
```

### 2) GIF или изображение

```powershell
python .\ascii_braille_animation.py --image .\demo.gif --fps 12 --mode ascii --sharp --loop
```

### 3) Видео

```powershell
python .\ascii_braille_animation.py --video .\input.mp4 --fps 20 --mode both --loop
```

## Параметры

### Основные

- `--folder` — папка с изображениями-кадрами
- `--image` — изображение или GIF
- `--video` — видео-файл
- `--mode ascii|braille|both` — режим вывода
- `--fps` — кадров в секунду
- `--loop` — повторять анимацию по кругу
- `--width` — ширина ASCII-арта
- `--braille-width` — ширина Braille-блока
- `--charset blocks|classic|binary` — набор ASCII-символов
- `--sharp` — сделать ASCII более контрастным
- `--invert` — инвертировать яркость
- `--threshold` — порог для Braille

### “Плавающий” ASCII

```powershell
python .\ascii_braille_animation.py --image .\demo.gif --mode ascii --float --mouse-x 0.7 --mouse-y 0.3 --float-strength 3 --loop
```

- `--float` — включить эффект смещения
- `--mouse-x` — смещение по X, от 0 до 1
- `--mouse-y` — смещение по Y, от 0 до 1
- `--float-strength` — сила эффекта

### Экспорт

```powershell
python .\ascii_braille_animation.py --video .\input.mp4 --mode both --export .\out\video --export-format both
```

- `--export` — путь к выходному файлу без расширения
- `--export-format txt|ansi|both` — формат экспорта

### ANSI-плейер

```powershell
python .\ascii_braille_animation.py --ansi-player .\out\video.ansi --fps 12 --loop
```

## Чистый терминальный вывод

Чтобы убрать лишний мусор в консоли и оставить только анимацию, используйте:

```powershell
python .\ascii_braille_animation.py --video .\input.mp4 --mode ascii --fps 15 --loop --no-clear
```

Параметр `--no-clear` выключает очистку терминала перед каждым кадром. Это удобно для:

- более стабильного логирования
- смешивания терминального текста и анимации
- работы в окружениях, где ANSI-очистка вызывает артефакты

Для более “чистого” режима можно использовать и обычный `--mode ascii` без цветовых/дополнительных эффектов.

## Пример полного запуска

```powershell
python .\ascii_braille_animation.py --video .\input.mp4 --mode both --fps 18 --width 90 --braille-width 35 --charset blocks --sharp --loop --no-clear --export .\out\demo --export-format both
```

## Примечание

Если терминал не поддерживает ANSI-перемещение курсора, эффект очистки может выглядеть не так, как ожидается. В этом случае лучше использовать `--no-clear` или запускать скрипт в обычной консоли/PowerShell.
