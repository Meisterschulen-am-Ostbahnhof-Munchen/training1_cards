"""Aesthetic analysis of logiBUS training-card PDFs (exact_70x90).

Per card it extracts vector data (wire polylines -> crossings, overlaps, length)
and raster data (ink coverage, empty bands, balance) and dumps a CSV.

Usage:
    python analyze.py [--src <card folder>] [--thumbs <png folder>] [--out metrics.csv]
"""
import os, sys, csv, math, json, argparse
from pathlib import Path
import pymupdf
from PIL import Image
import io

REPO_ROOT = Path(__file__).resolve().parents[2]
SELF_DIR = Path(__file__).resolve().parent

SRC = str(REPO_ROOT / "output" / "test_AX" / "exact_70x90")
THUMB = str(SELF_DIR / "thumbs")
OUT = str(SELF_DIR / "metrics.csv")

# wire stroke colours (main, from NetworkSVGRenderer)
WIRE_HEX = {
    "#63B31F": "event",   # 99,179,31
    "#A3B08F": "bool",
    "#82A3A9": "anybit",
    "#18519E": "anyint",
    "#DBB418": "anyreal",
    "#BD8663": "string",
    "#3366FF": "data",
    "#845DAF": "adapter",
}

def hex_of(rgb):
    if rgb is None:
        return None
    return "#%02X%02X%02X" % tuple(round(c * 255) for c in rgb)

def wire_kind(rgb):
    h = hex_of(rgb)
    if h in WIRE_HEX:
        return WIRE_HEX[h]
    # allow slight rounding drift
    if h:
        for k, v in WIRE_HEX.items():
            kr = tuple(int(k[i:i+2], 16) for i in (1, 3, 5))
            rr = tuple(int(h[i:i+2], 16) for i in (1, 3, 5))
            if max(abs(a - b) for a, b in zip(kr, rr)) <= 6:
                return v
    return None

def seg_intersect(p, p2, q, q2):
    """Proper crossing point of segments (p,p2) and (q,q2) or None. Endpoint touches excluded."""
    x1, y1 = p; x2, y2 = p2; x3, y3 = q; x4, y4 = q2
    d = (x2 - x1) * (y4 - y3) - (y2 - y1) * (x4 - x3)
    if abs(d) < 1e-9:
        return None
    t = ((x3 - x1) * (y4 - y3) - (y3 - y1) * (x4 - x3)) / d
    u = ((x3 - x1) * (y2 - y1) - (y3 - y1) * (x2 - x1)) / d
    # strictly interior for both (epsilon relative to page ~0.5pt)
    L1 = math.hypot(x2 - x1, y2 - y1); L2 = math.hypot(x4 - x3, y4 - y3)
    e1 = 0.6 / max(L1, 0.6); e2 = 0.6 / max(L2, 0.6)
    if e1 < t < 1 - e1 and e2 < u < 1 - e2:
        return (x1 + t * (x2 - x1), y1 + t * (y2 - y1))
    return None

def seg_overlap(p, p2, q, q2):
    """Collinear overlapping length between two segments (>=1pt) or 0."""
    dx1, dy1 = p2[0] - p[0], p2[1] - p[1]
    dx2, dy2 = q2[0] - q[0], q2[1] - q[1]
    l1 = math.hypot(dx1, dy1); l2 = math.hypot(dx2, dy2)
    if l1 < 0.5 or l2 < 0.5:
        return 0.0
    cross = (dx1 * dy2 - dy1 * dx2) / (l1 * l2)
    if abs(cross) > 0.02:      # not parallel
        return 0.0
    # distance of q and q2 from line p-p2
    def dist(pt):
        return abs((pt[0] - p[0]) * dy1 - (pt[1] - p[1]) * dx1) / l1
    if dist(q) > 1.2 or dist(q2) > 1.2:
        return 0.0
    ux, uy = dx1 / l1, dy1 / l1
    def proj(pt):
        return (pt[0] - p[0]) * ux + (pt[1] - p[1]) * uy
    a1, a2 = 0.0, l1
    b1, b2 = sorted((proj(q), proj(q2)))
    ov = min(a2, b2) - max(a1, b1)
    return ov if ov > 1.0 else 0.0

def analyse(path, thumb_dir):
    doc = pymupdf.open(path)
    pg = doc[0]
    rec = {}
    W, H = pg.rect.width, pg.rect.height
    rec["w_pt"] = round(W, 2); rec["h_pt"] = round(H, 2)

    drawings = pg.get_drawings()
    wires = []          # list of (kind, [ (x,y), ... ])
    blocks = []         # bbox of block-like shapes
    for dr in drawings:
        col = dr.get("color")
        kind = wire_kind(col)
        items = dr.get("items", [])
        if kind and dr["type"] == "s":
            pts = []
            ok = True
            for it in items:
                if it[0] == "l":
                    a, b = it[1], it[2]
                    if not pts:
                        pts.append((a.x, a.y))
                    pts.append((b.x, b.y))
                else:
                    ok = False
                    break
            if ok and len(pts) >= 2:
                wires.append((kind, pts))
        elif dr["type"] == "fs" and dr.get("fill") == (1.0, 1.0, 1.0):
            r = dr["rect"]
            # exclude the pin badges glued to the left/right card edge
            if r.width > 20 and r.height > 12 and r.x0 > 0.06 * W and r.x1 < 0.94 * W:
                blocks.append(r)

    # crossings between different wires
    crossings = 0
    overlap = 0.0
    segs = []
    for wi, (kind, pts) in enumerate(wires):
        for i in range(len(pts) - 1):
            segs.append((wi, kind, pts[i], pts[i + 1]))
    for i in range(len(segs)):
        for j in range(i + 1, len(segs)):
            if segs[i][0] == segs[j][0]:
                continue
            a = segs[i]; b = segs[j]
            if seg_intersect(a[2], a[3], b[2], b[3]):
                crossings += 1
            else:
                overlap += seg_overlap(a[2], a[3], b[2], b[3])

    total_len = sum(math.hypot(s[3][0] - s[2][0], s[3][1] - s[2][1]) for s in segs)
    bends = sum(max(0, len(pts) - 2) for _, pts in wires)

    rec["n_wires"] = len(wires)
    rec["crossings"] = crossings
    rec["overlap_pt"] = round(overlap, 1)
    rec["wire_len_pt"] = round(total_len, 1)
    rec["bends"] = bends
    rec["n_blocks"] = len(blocks)
    # overlapping block bodies (ugly)
    bo = 0
    for i in range(len(blocks)):
        for j in range(i + 1, len(blocks)):
            a, b = blocks[i], blocks[j]
            if a.x0 < b.x1 - 1 and b.x0 < a.x1 - 1 and a.y0 < b.y1 - 1 and b.y0 < a.y1 - 1:
                bo += 1
    rec["n_block_overlaps"] = bo
    if blocks:
        rec["block_vspan_norm"] = round((max(b.y1 for b in blocks) - min(b.y0 for b in blocks)) / (0.72 * H), 3)
    else:
        rec["block_vspan_norm"] = 0.0

    # wire bounding box (glyph area actually used)
    xs = [p[0] for _, pts in wires for p in pts]
    ys = [p[1] for _, pts in wires for p in pts]
    if xs:
        rec["wire_bbox"] = (round(min(xs), 1), round(min(ys), 1), round(max(xs), 1), round(max(ys), 1))

    # text
    txt = pg.get_text("dict")
    lines = []
    for blk in txt["blocks"]:
        for ln in blk.get("lines", []):
            s = "".join(sp["text"] for sp in ln["spans"]).strip()
            if s:
                lines.append((ln["bbox"], s, max(sp["size"] for sp in ln["spans"])))
    rec["n_text_lines"] = len(lines)
    # body text = below 70% of page
    band_top = 0.70 * H
    body = [(b, s, sz) for b, s, sz in lines if b[1] > band_top]
    rec["n_body_lines"] = len(body)
    # text-on-text collisions (garbled overlapping labels)
    tlines = [b for b, s, sz in lines if b[1] < band_top]
    tops = 0
    for i in range(len(tlines)):
        for j in range(i + 1, len(tlines)):
            a, b = tlines[i], tlines[j]
            ox = min(a[2], b[2]) - max(a[0], b[0])
            oy = min(a[3], b[3]) - max(a[1], b[1])
            if ox > 1.5 and oy > 1.5 and ox * oy > 6.0:
                tops += 1
    rec["text_overlap_pairs"] = tops
    # canvas text lines (labels) that sit on top of a block body
    tb = 0
    for b in tlines:
        for r in blocks:
            ox = min(b[2], r.x1) - max(b[0], r.x0)
            oy = min(b[3], r.y1) - max(b[1], r.y0)
            if ox > 1.0 and oy > 1.0:
                tb += 1
                break
    rec["labels_on_blocks"] = tb
    # collision: do block bodies intrude into the title/description band?
    band_lines = [b for b, s, sz in lines if b[1] > 0.86 * H]
    band_top = min((b[1] for b in band_lines), default=H)
    rec["text_band_top_pt"] = round(band_top, 1)
    coll = 0
    maxdepth = 0.0
    for r0 in blocks:
        if r0.y1 > band_top + 0.5:
            coll += 1
            maxdepth = max(maxdepth, r0.y1 - band_top)
    rec["text_block_collision"] = coll
    rec["text_block_depth_pt"] = round(maxdepth, 1)
    rec["body_bottom_norm"] = round(max((b[3] for b, _, _ in lines), default=0) / H, 3)
    rec["title"] = lines[-1][1] if lines else ""

    # raster metrics
    pix = pg.get_pixmap(dpi=150)
    img = Image.frombytes("RGB", (pix.width, pix.height), pix.samples)
    g = img.convert("L")
    w, h = g.size
    rec["thumb_size"] = (w, h)
    px = g.load()
    M = 3                                # ignore border frame
    draw_h = int(h * 0.72)               # canvas (logic) region above the text band
    ink_cells = 0
    tot_cells = 0
    rows = [0] * h
    cols = [0] * w
    sumx = 0.0; sumy = 0.0; cnt = 0
    for y in range(M, draw_h - M):
        for x in range(M, w - M):
            v = px[x, y]
            tot_cells += 1
            if v < 180:
                ink_cells += 1
                rows[y] += 1
                cols[x] += 1
                sumx += x; sumy += y; cnt += 1
    rec["ink_pct_canvas"] = round(100.0 * ink_cells / max(1, tot_cells), 2)
    if cnt:
        rec["com_x_norm"] = round(sumx / cnt / w, 3)
        rec["com_y_norm"] = round(sumy / cnt / draw_h, 3)

    # centre strip (where the logic lives, without the pin badge columns)
    cs_x0, cs_x1 = int(0.17 * w), int(0.83 * w)
    c_rows = [0] * h
    c_ink = 0; c_tot = 0
    for y in range(M, draw_h - M):
        for x in range(cs_x0, cs_x1):
            c_tot += 1
            if px[x, y] < 180:
                c_ink += 1
                c_rows[y] += 1
    rec["centre_ink_pct"] = round(100.0 * c_ink / max(1, c_tot), 2)
    used = [y for y in range(M, draw_h - M) if c_rows[y] > 0]
    if used:
        rec["centre_top_norm"] = round(used[0] / draw_h, 3)
        rec["centre_bottom_norm"] = round(used[-1] / draw_h, 3)
        rec["centre_vspan_norm"] = round((used[-1] - used[0]) / draw_h, 3)
        rec["centre_top_gap_pct"] = round(100.0 * (used[0] - M) / draw_h, 1)
        rec["centre_bottom_gap_pct"] = round(100.0 * (draw_h - M - used[-1]) / draw_h, 1)
        best = 0; cur = 0
        for y in range(used[0], used[-1] + 1):
            if c_rows[y] == 0:
                cur += 1; best = max(best, cur)
            else:
                cur = 0
        rec["centre_gap_norm"] = round(best / draw_h, 3)
        rec["centre_gap_pct"] = round(100.0 * best / draw_h, 1)
    # full-canvas biggest empty horizontal gap (between pin columns)
    best = 0; cur = 0
    usedx = [x for x in range(M, w - M) if cols[x] > 0]
    if usedx:
        rec["ink_hspan_norm"] = round((usedx[-1] - usedx[0]) / w, 3)
    # clutter hotspot: max ink fraction in a 34x48 px window (~6x8 mm) over the canvas
    worst = 0.0
    win_w, win_h = 34, 48
    for y in range(M, max(M + 1, draw_h - win_h), 16):
        for x in range(M, max(M + 1, w - win_w), 16):
            c = 0
            for yy in range(y, y + win_h, 2):
                for xx in range(x, x + win_w, 2):
                    if px[xx, yy] < 180:
                        c += 1
            frac = c / ((win_h // 2) * (win_w // 2))
            worst = max(worst, frac)
    rec["clutter_max"] = round(worst, 3)

    img.save(os.path.join(thumb_dir, os.path.basename(path).replace(".pdf", ".png")))
    doc.close()
    return rec

def stat_stdev(vals):
    n = len(vals)
    if n == 0:
        return 0.0
    m = sum(vals) / n
    return math.sqrt(sum((v - m) ** 2 for v in vals) / n)

def main():
    ap = argparse.ArgumentParser(description="Measure layout metrics for training-card PDFs.")
    ap.add_argument("--src", default=SRC, help="folder containing the *_exact_70x90.pdf cards")
    ap.add_argument("--thumbs", default=THUMB, help="folder for the rendered card thumbnails")
    ap.add_argument("--out", default=OUT, help="output CSV path")
    args = ap.parse_args()
    src, thumb_dir, out = args.src, args.thumbs, args.out
    os.makedirs(thumb_dir, exist_ok=True)
    files = sorted(f for f in os.listdir(src) if f.lower().endswith(".pdf"))
    print(len(files), "cards")
    rows = []
    for i, f in enumerate(files):
        try:
            r = analyse(os.path.join(src, f), thumb_dir)
        except Exception as e:
            r = {"title": f, "error": str(e)}
            print("ERR", f, e)
        r["file"] = f
        rows.append(r)
        if (i + 1) % 50 == 0:
            print("...", i + 1)
    keys = ["file", "title", "w_pt", "h_pt", "n_wires", "crossings", "overlap_pt", "wire_len_pt",
            "bends", "n_blocks", "n_block_overlaps", "block_vspan_norm",
            "n_text_lines", "n_body_lines", "text_block_collision", "body_bottom_norm",
            "text_band_top_pt", "text_block_depth_pt",
            "text_overlap_pairs", "labels_on_blocks",
            "ink_pct_canvas", "com_x_norm", "com_y_norm",
            "centre_ink_pct", "centre_top_norm", "centre_bottom_norm", "centre_vspan_norm",
            "centre_top_gap_pct", "centre_bottom_gap_pct",
            "centre_gap_norm", "centre_gap_pct", "ink_hspan_norm", "clutter_max", "error"]
    with open(out, "w", newline="", encoding="utf-8") as fh:
        wr = csv.DictWriter(fh, fieldnames=keys, extrasaction="ignore")
        wr.writeheader()
        for r in rows:
            wr.writerow(r)
    print("wrote", out)

if __name__ == "__main__":
    main()
