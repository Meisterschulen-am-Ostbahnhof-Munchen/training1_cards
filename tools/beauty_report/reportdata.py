"""Aggregates scores.csv into the statistics and ranking tables for the report.

Usage:
    python reportdata.py [--dir <work folder>]
"""
import argparse, csv, collections, statistics as st, json
from pathlib import Path

SELF_DIR = Path(__file__).resolve().parent
ap = argparse.ArgumentParser(description="Build the statistics/ranking data for the report.")
ap.add_argument("--dir", default=str(SELF_DIR),
                help="folder holding scores.csv (default: this script's folder)")
WORK = Path(ap.parse_args().dir)

rows = list(csv.DictReader(open(WORK / 'scores.csv', encoding='utf-8')))
def f(r, k, d=0.0):
    try: return float(r[k])
    except Exception: return d

N = len(rows)
grades = ['A+', 'A', 'B', 'C', 'D', 'F']
cnt = collections.Counter(r['grade'] for r in rows)

out = {}
out['n'] = N
out['grades'] = {g: cnt.get(g, 0) for g in grades}
out['mean_total'] = round(st.mean(f(r, 'total') for r in rows), 1)
out['median_total'] = round(st.median(f(r, 'total') for r in rows), 1)

def pct(n):
    return round(100.0 * n / N, 1)

out['stats'] = {
    'crossings_gt0': pct(sum(1 for r in rows if f(r, 'crossings') > 0)),
    'crossings_ge5': pct(sum(1 for r in rows if f(r, 'crossings') >= 5)),
    'crossings_ge20': pct(sum(1 for r in rows if f(r, 'crossings') >= 20)),
    'text_overlap_gt0': pct(sum(1 for r in rows if f(r, 'text_overlap_pairs') > 0)),
    'text_overlap_ge3': pct(sum(1 for r in rows if f(r, 'text_overlap_pairs') >= 3)),
    'tbc_gt0': pct(sum(1 for r in rows if f(r, 'text_block_collision') > 0)),
    'tbc_ge8': pct(sum(1 for r in rows if f(r, 'text_block_collision') >= 8)),
    'body_bottom_gt099': pct(sum(1 for r in rows if f(r, 'body_bottom_norm') > 0.99)),
    'body_bottom_gt1': pct(sum(1 for r in rows if f(r, 'body_bottom_norm') > 1.0)),
    'bottom_gap_gt40': pct(sum(1 for r in rows if f(r, 'centre_bottom_gap_pct') > 40)),
    'top_gap_gt40': pct(sum(1 for r in rows if f(r, 'centre_top_gap_pct') > 40)),
    'ink_gt9': pct(sum(1 for r in rows if f(r, 'ink_pct_canvas') > 9)),
    'ink_lt2_5': pct(sum(1 for r in rows if f(r, 'ink_pct_canvas') < 2.5)),
    'lines_gt12': pct(sum(1 for r in rows if f(r, 'n_body_lines') > 12)),
    'blocks_ge10': pct(sum(1 for r in rows if f(r, 'n_blocks') >= 10)),
    'nowires': pct(sum(1 for r in rows if f(r, 'n_wires') == 0)),
    'clip_left': pct(sum(1 for r in rows if f(r, 'clip_left') > 0)),
    'clip_bottom': pct(sum(1 for r in rows if f(r, 'clip_bottom') > 0)),
}
for k in out['stats']:
    out['stats'][k] = f"{out['stats'][k]}% ({round(out['stats'][k]*N/100)})"

by_total = sorted(rows, key=lambda r: -f(r, 'total'))
out['best'] = [dict(ex=r['ex'], g=r['grade'], t=r['total'], route=r['routing'], bal=r['balance'],
                    den=r['density'], txt=r['textblock'], cr=r['crossings'], blk=r['n_blocks'],
                    lines=r['n_body_lines']) for r in by_total[:25]]
out['worst'] = [dict(ex=r['ex'], g=r['grade'], t=r['total'], route=r['routing'], bal=r['balance'],
                     den=r['density'], txt=r['textblock'], cr=r['crossings'], blk=r['n_blocks'],
                     lines=r['n_body_lines'], tov=r['text_overlap_pairs'], tbc=r['text_block_collision'])
                for r in by_total[::-1][:25]]

# families (leading exercise number)
fam = collections.defaultdict(list)
for r in rows:
    num = r['ex'].split('_')[1]
    fam[num.rstrip('abcdefghijklmnopqrstuvwxyzAB')].append(f(r, 'total'))
out['weak_families'] = sorted(((k, round(st.mean(v), 1), len(v)) for k, v in fam.items() if len(v) >= 3),
                              key=lambda x: x[1])[:12]
out['strong_families'] = sorted(((k, round(st.mean(v), 1), len(v)) for k, v in fam.items() if len(v) >= 3),
                                key=lambda x: -x[1])[:12]

# full ranking
out['all'] = [(r['ex'], r['grade'], r['total'], r['crossings'], r['text_overlap_pairs'],
               r['centre_bottom_gap_pct'], r['n_body_lines']) for r in by_total]

json.dump(out, open(WORK / 'report_data.json', 'w', encoding='utf-8'), ensure_ascii=False, indent=1)

print('grades', out['grades'])
print('stats')
for k, v in out['stats'].items():
    print('  ', k, v)
print('weak families', out['weak_families'])
print('strong families', out['strong_families'])
print()
print('WORST 25:')
for r in out['worst']:
    print(f"  {r['ex']:22s} {r['g']:>2} {r['t']:>5} cross={r['cr']:>5} blk={r['blk']:>3} lines={r['lines']:>3} tov={r['tov']} tbc={r['tbc']}")
