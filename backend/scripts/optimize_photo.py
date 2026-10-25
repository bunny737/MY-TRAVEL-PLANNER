"""Turn one source photo into the web versions the site serves.

Usage (inside the web container, Pillow is a dev-only dependency):
    python scripts/optimize_photo.py SOURCE STEM [--crop X0,Y0,X1,Y1] [--out static/img/photos]

Writes <STEM>-800.webp and <STEM>-1600.webp (a width is skipped if the source is narrower, so nothing is upscaled).
--crop takes fractions of the source (0-1): left, top, right, bottom. Metadata (EXIF, GPS) is never copied.
Prints the pixel size of every file written; put the largest size in apps/core/images.py.
"""
import argparse
import sys
from pathlib import Path

from PIL import Image, ImageOps

WIDTHS = (800, 1600)
QUALITY = 78


def main():
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument('source')
    parser.add_argument('stem')
    parser.add_argument('--crop', help='fractions x0,y0,x1,y1 of the source to keep')
    parser.add_argument('--out', default='static/img/photos')
    args = parser.parse_args()

    image = ImageOps.exif_transpose(Image.open(args.source)).convert('RGB')
    if args.crop:
        x0, y0, x1, y1 = (float(v) for v in args.crop.split(','))
        if not (0 <= x0 < x1 <= 1 and 0 <= y0 < y1 <= 1):
            sys.exit('--crop must be fractions with x0<x1 and y0<y1, all between 0 and 1')
        w, h = image.size
        image = image.crop((round(x0 * w), round(y0 * h), round(x1 * w), round(y1 * h)))

    out = Path(args.out)
    out.mkdir(parents=True, exist_ok=True)
    for width in WIDTHS:
        if image.width < width:
            continue
        height = round(image.height * width / image.width)
        resized = image.resize((width, height), Image.LANCZOS)
        target = out / f'{args.stem}-{width}.webp'
        resized.save(target, 'WEBP', quality=QUALITY, method=6)  # no exif= argument: metadata is dropped
        print(f'{target}  {width}x{height}  {target.stat().st_size // 1024} KB')
    if image.width < WIDTHS[0]:
        sys.exit(f'source is only {image.width}px wide; need at least {WIDTHS[0]}')


if __name__ == '__main__':
    main()
