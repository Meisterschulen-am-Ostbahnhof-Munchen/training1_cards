"""Beauty scoring for the logiBUS training cards (final).

Combines metrics.csv and clip.csv into a per-card score and grade.

Usage:
    python score.py [--dir <work folder>]
"""
import argparse, csv, math, collections
from pathlib import Path

SELF_DIR = Path(__file__).resolve().parent


def parse_args():
    ap = argparse.ArgumentParser(description="Score the measured card metrics.")
    ap.add_argument("--dir", default=str(SELF_DIR),
                    help="folder holding metrics.csv/clip.csv (default: this script's folder)")
    return ap.parse_args()


WORK = Path(parse_args().dir)
METRICS_CSV = WORK / "metrics.csv"
CLIP_CSV = WORK / "clip.csv"
SCORES_CSV = WORK / "scores.csv"

rows = list(csv.DictReader(open(METRICS_CSV, encoding='utf-8')))

clip = {}
for c in csv.DictReader(open(CLIP_CSV, encoding='utf-8')):
    if c['file'] == 'file':
        continue
    clip[c['file']] = c
for r in rows:
    c = clip.get(r['file'], {})
    r['clip_left'] = c.get('left', '0')
    r['clip_bottom'] = c.get('bottom', '0')
    r['clip_worst_l'] = c.get('worst_l', '0')
    r['clip_worst_b'] = c.get('worst_b', '0')

def f(r, k, d=0.0):
    try:
        return float(r[k])
    except Exception:
        return d

def blank_as(r, k, fallback, csv_r):
    """Handle cards whose centre strip contains no ink at all."""
    if r.get('centre_top_gap_pct', '') == '':
        return fallback
    return f(r, k)

def cl(x, a=0.0, b=100.0):
    return max(a, min(b, x))

def score(r):
    nw = max(1.0, f(r, 'n_wires'))
    cross_rate = f(r, 'crossings') / nw

    # 1) Linienfuehrung / Kreuzungen -------------------------------------
    routing = 100.0 * math.exp(-cross_rate / 2.0)
    routing -= cl((f(r, 'wire_len_pt') / nw - 190.0) / 10.0, 0, 30)

    # 2) Flaechennutzung / Ausgewogenheit --------------------------------
    top, bot = f(r, 'centre_top_gap_pct'), f(r, 'centre_bottom_gap_pct')
    vspan = f(r, 'centre_vspan_norm')
    if r.get('centre_top_gap_pct', '') == '':
        # no ink at all in the centre strip of the card area
        top, bot, vspan = 100.0, 0.0, 0.0
    empty = max(top, bot)
    balance = 100.0
    if empty > 18:
        balance -= (empty - 18) * 1.5
    balance -= abs(top - bot) * 0.3
    if vspan < 0.22:
        balance -= (0.22 - vspan) * 150

    # 3) Dichte / Aufraeumtheit ------------------------------------------
    ink = f(r, 'ink_pct_canvas')
    density = 100.0
    if ink < 2.5:
        density -= (2.5 - ink) * 14
    if ink > 9.0:
        density -= (ink - 9.0) * 11
    density -= cl((f(r, 'clutter_max') - 0.32) * 280, 0, 45)
    density -= f(r, 'n_block_overlaps') * 15

    # 4) Beschriftung / Textblock ----------------------------------------
    lines = f(r, 'n_body_lines')
    txt = 100.0
    if lines > 9:
        txt -= (lines - 9) * 3.5
    bb = f(r, 'body_bottom_norm')
    if bb > 0.97:
        txt -= (bb - 0.97) * 1000
    txt -= f(r, 'text_block_collision') * 3.5
    txt -= f(r, 'text_overlap_pairs') * 7.0
    txt -= f(r, 'clip_left') * 3.0            # port labels running off the left card edge
    txt -= f(r, 'clip_bottom') * 8.0          # text running past the bottom card edge

    # 5) Blockverteilung --------------------------------------------------
    bv = f(r, 'block_vspan_norm')
    layout = 100.0
    if f(r, 'n_blocks') >= 2 and bv < 0.35:
        layout -= (0.35 - bv) * 70

    routing, balance, density, txt, layout = (cl(routing), cl(balance), cl(density), cl(txt), cl(layout))
    total = 0.42 * routing + 0.20 * balance + 0.20 * density + 0.13 * txt + 0.05 * layout
    return dict(routing=round(routing, 1), balance=round(balance, 1), density=round(density, 1),
                textblock=round(txt, 1), layout=round(layout, 1), total=round(total, 2))

def grade(t):
    if t >= 92: return 'A+'
    if t >= 84: return 'A'
    if t >= 74: return 'B'
    if t >= 64: return 'C'
    if t >= 54: return 'D'
    return 'F'

out = []
for r in rows:
    s = score(r)
    r.update({k: str(v) for k, v in s.items()})
    r['grade'] = grade(s['total'])
    r['ex'] = r['file'].replace('_exact_70x90.pdf', '')
    out.append(r)

key = ['ex', 'grade', 'total', 'routing', 'balance', 'density', 'textblock', 'layout',
       'crossings', 'n_wires', 'wire_len_pt', 'bends', 'n_blocks', 'n_block_overlaps',
       'ink_pct_canvas', 'clutter_max', 'centre_top_gap_pct', 'centre_bottom_gap_pct',
       'centre_vspan_norm', 'n_body_lines', 'body_bottom_norm', 'text_block_collision',
       'text_overlap_pairs', 'clip_left', 'clip_bottom', 'clip_worst_l', 'clip_worst_b', 'file']
with open(SCORES_CSV, 'w', newline='', encoding='utf-8') as fh:
    wr = csv.DictWriter(fh, fieldnames=key, extrasaction='ignore')
    wr.writeheader()
    wr.writerows(out)

c = collections.Counter(r['grade'] for r in out)
print('Notenverteilung:', {g: c.get(g, 0) for g in ['A+', 'A', 'B', 'C', 'D', 'F']})
tot = sorted(float(r['total']) for r in out)
print('Median total %.1f  P10 %.1f  P90 %.1f' % (tot[len(tot)//2], tot[len(tot)//10], tot[9*len(tot)//10]))
print()
print('--- Beste 12 ---')
for r in sorted(out, key=lambda r: -float(r['total']))[:12]:
    print(f"{r['ex']:24s} {r['grade']:>2} tot={r['total']:>5} route={r['routing']:>5} bal={r['balance']:>5} den={r['density']:>5} txt={r['textblock']:>5} cross={r['crossings']}")
print()
print('--- Schlechteste 20 ---')
for r in sorted(out, key=lambda r: float(r['total']))[:20]:
    print(f"{r['ex']:24s} {r['grade']:>2} tot={r['total']:>5} route={r['routing']:>5} bal={r['balance']:>5} den={r['density']:>5} txt={r['textblock']:>5} cross={r['crossings']} lines={r['n_body_lines']} tov={r['text_overlap_pairs']}")
print()
print('--- Kontrollkarten ---')
for name in ['Uebung_002a_AX','Uebung_002b3_AX','Uebung_172_AX','Uebung_003f_AX','Uebung_010a_AX',
             'Uebung_001c_AX','Uebung_004a_AX','Uebung_009a_AX','Uebung_014_AX','Uebung_033_AX',
             'Uebung_006_SAFE_AX','Uebung_011b4_AX','Uebung_103c2','Uebung_028_AX','Uebung_034_AX']:
    for r in out:
        if r['ex'] == name:
            print(f"{name:20s} {r['grade']:>2} tot={r['total']:>5} route={r['routing']:>5} bal={r['balance']:>5} den={r['density']:>5} txt={r['textblock']:>5} cross={r['crossings']} gapT={r['centre_top_gap_pct']} gapB={r['centre_bottom_gap_pct']} lines={r['n_body_lines']} tov={r['text_overlap_pairs']} tbc={r['text_block_collision']}")
