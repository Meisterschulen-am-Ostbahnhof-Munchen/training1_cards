"""Builds contact sheets (20 cards per sheet) for visual spot-checking.

Combines the rendered thumbnails from analyze.py with the scores from score.py
so the highest/lowest ranked cards can be reviewed side by side.

Usage:
    python sheets.py [--dir <work folder>] [--thumbs <png folder>] [--out-dir <png folder>]
"""
import argparse, csv, math, random, os
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont

SELF_DIR = Path(__file__).resolve().parent

ap = argparse.ArgumentParser(description="Render contact sheets of the scored cards.")
ap.add_argument("--dir", default=str(SELF_DIR), help="folder holding scores.csv")
ap.add_argument("--thumbs", default=str(SELF_DIR / "thumbs"), help="folder with the card thumbnails")
ap.add_argument("--out-dir", default=str(SELF_DIR), help="folder for the contact sheets")
args = ap.parse_args()

WORK = Path(args.dir)
TH = Path(args.thumbs)
OUT_DIR = Path(args.out_dir)
OUT_DIR.mkdir(parents=True, exist_ok=True)

rows = list(csv.DictReader(open(WORK / 'scores.csv', encoding='utf-8')))


def f(r, k, d=0.0):
    try:
        return float(r[k])
    except Exception:
        return d


def sheet(names, out, cols=5, title=''):
    cell_w, cell_h = 414, 532
    label_h = 26
    rowsn = math.ceil(len(names) / cols)
    W = cols * cell_w
    H = rowsn * (cell_h + label_h) + (34 if title else 0)
    img = Image.new('RGB', (W, H), 'white')
    d = ImageDraw.Draw(img)
    try:
        font = ImageFont.truetype('arial.ttf', 20)
        tfont = ImageFont.truetype('arialbd.ttf', 26)
    except Exception:
        font = ImageFont.load_default()
        tfont = font
    y0 = 0
    if title:
        d.text((10, 6), title, fill='black', font=tfont)
        y0 = 34
    for i, n in enumerate(names):
        c, rr = i % cols, i // cols
        x = c * cell_w
        y = y0 + rr * (cell_h + label_h)
        p = TH / f"{n}_exact_70x90.png"
        if p.exists():
            img.paste(Image.open(p), (x, y + label_h))
        d.rectangle([x, y + label_h, x + cell_w - 1, y + label_h + cell_h - 1], outline=(200, 200, 200))
        d.text((x + 4, y + 3), n, fill='black', font=font)
    img.save(out)
    print('wrote', out, img.size)


def main():
    by_total_asc = sorted(rows, key=lambda r: f(r, 'total'))
    by_total_desc = sorted(rows, key=lambda r: -f(r, 'total'))
    sheets = [
        ('sheet_worst20.png', [r['ex'] for r in by_total_asc[:20]], 'Schlechteste 20 (Gesamtwert)'),
        ('sheet_best20.png', [r['ex'] for r in by_total_desc[:20]], 'Beste 20 (Gesamtwert)'),
        ('sheet_topheavy.png', [r['ex'] for r in sorted(rows, key=lambda r: -f(r, 'centre_bottom_gap_pct'))[:20]],
         'Groesster Leerraum unten (top-lastig)'),
        ('sheet_text.png', [r['ex'] for r in sorted(rows, key=lambda r: -f(r, 'n_body_lines'))[:20]],
         'Laengste Beschreibungen'),
        ('sheet_textoverlap.png', [r['ex'] for r in sorted(rows, key=lambda r: -f(r, 'text_overlap_pairs'))[:20]],
         'Text-ueber-Text Ueberlappungen'),
        ('sheet_random.png', [r['ex'] for r in random.Random(7).sample(rows, 20)], 'Zufallsstichprobe 20'),
    ]
    for name, names, title in sheets:
        sheet(names, OUT_DIR / name, title=title)


if __name__ == '__main__':
    main()
