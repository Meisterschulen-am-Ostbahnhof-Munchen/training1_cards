"""Checks whether card text is cut off at the card edges.

Writes a CSV with the number of text lines crossing each page edge and the
worst overhang in points, per card.

Usage:
    python clipcheck.py [--src <card folder>] [--out clip.csv]
"""
import argparse
import pymupdf, os, csv
from pathlib import Path

SELF_DIR = Path(__file__).resolve().parent
REPO_ROOT = SELF_DIR.parents[1]
DEFAULT_SRC = str(REPO_ROOT / "output" / "test_AX" / "exact_70x90")

ap = argparse.ArgumentParser(description="Find text running over the card edges.")
ap.add_argument("--src", default=DEFAULT_SRC, help="folder containing the card PDFs")
ap.add_argument("--out", default=str(SELF_DIR / "clip.csv"), help="output CSV path")
args = ap.parse_args()
SRC, OUT = args.src, args.out

res = []
for fn in sorted(os.listdir(SRC)):
    if not fn.lower().endswith('.pdf'):
        continue
    d = pymupdf.open(os.path.join(SRC, fn))
    pg = d[0]
    W, H = pg.rect.width, pg.rect.height
    left = right = top = bot = 0
    worst_l = worst_r = worst_b = 0.0
    for blk in pg.get_text('dict')['blocks']:
        for ln in blk.get('lines', []):
            s = ''.join(sp['text'] for sp in ln['spans']).strip()
            if not s:
                continue
            x0, y0, x1, y1 = ln['bbox']
            if x0 < -0.2:
                left += 1; worst_l = min(worst_l, x0)
            if x1 > W + 0.2:
                right += 1; worst_r = max(worst_r, x1 - W)
            if y0 < -0.2:
                top += 1
            if y1 > H + 0.2:
                bot += 1; worst_b = max(worst_b, y1 - H)
    res.append(dict(file=fn, left=left, right=right, top=top, bottom=bot,
                    worst_l=round(worst_l, 1), worst_r=round(worst_r, 1), worst_b=round(worst_b, 1)))
    d.close()
FIELDS = ['file', 'left', 'right', 'top', 'bottom', 'worst_l', 'worst_r', 'worst_b']
with open(OUT, 'w', newline='', encoding='utf-8') as fh:
    wr = csv.DictWriter(fh, fieldnames=FIELDS)
    wr.writeheader()
    wr.writerows(res)
nl = sum(1 for r in res if r['left']); nr = sum(1 for r in res if r['right'])
nb = sum(1 for r in res if r['bottom']); nt = sum(1 for r in res if r['top'])
print(f"{len(res)} cards | clipped left: {nl} | right: {nr} | top: {nt} | bottom: {nb}")
print('worst left:', sorted(res, key=lambda r: r['worst_l'])[:8])
print('worst bottom:', sorted(res, key=lambda r: -r['worst_b'])[:8])
