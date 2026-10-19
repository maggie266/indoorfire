"""
ir_contrast_check.py

Decision-gate script for the IR modality: quantifies victim-vs-background
thermal contrast in the existing IR renders, before and after camera-style
AGC (percentile stretch), and writes visual comparison montages.

Question it answers: can the existing IR be salvaged by post-processing
(tone mapping), or is a re-render with thermal material override required?

Victim regions are taken from the YOLO label files (class cx cy w h,
normalized), so no Cryptomatte mattes are needed. For each victim instance:

  contrast_raw = (mean_in - mean_ring) / (mean_ring + eps)   [Weber, linear IR]
  contrast_agc = mean_in - mean_ring                          [after AGC, 0-1]

where `ring` is the annulus between the box and a 2x-expanded box.

Outputs:
  <output>/ir_contrast.csv         per-instance stats
  <output>/montage_*.png           [raw-normalized | AGC] side-by-side with boxes
  console summary                  contrast distribution + verdict hints

Usage:
  python ir_contrast_check.py ^
      --ir-dir     "D:\\Fire_Project\\FireDataset_new2\\test\\IR" ^
      --labels-dir "D:\\Fire_Project\\FireDataset_new2\\test\\labels" ^
      --output     "D:\\Fire_Project\\ir_check" ^
      --n-montage 20

Dependencies: numpy, opencv-python
"""

import argparse
import csv
import random
from pathlib import Path

import cv2
import numpy as np

EPS = 1e-6
AGC_PCT = (1.0, 99.5)   # percentile stretch, mirrors the toolkit's AGC step


def load_ir_linear(path: Path):
    """Load IR preserving bit depth; return float32 in [0,1] + a format note."""
    img = cv2.imread(str(path), cv2.IMREAD_UNCHANGED)
    if img is None:
        raise IOError(f"Cannot read {path}")
    note = f"dtype={img.dtype}, ch={1 if img.ndim == 2 else img.shape[2]}"
    if img.ndim == 3:
        # If channels differ, this is a color/colormapped image (e.g. jet):
        # gray conversion is NOT radiometrically meaningful -- flag it.
        if not (np.allclose(img[..., 0], img[..., 1]) and np.allclose(img[..., 1], img[..., 2])):
            note += " [WARNING: color image, likely a colormap render; "
            note += "contrast numbers unreliable -- locate the linear grayscale output]"
        img = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    maxv = 65535.0 if img.dtype == np.uint16 else 255.0
    return img.astype(np.float32) / maxv, note


def agc(ir: np.ndarray) -> np.ndarray:
    lo, hi = np.percentile(ir, AGC_PCT)
    if hi - lo < EPS:
        hi = lo + EPS
    return np.clip((ir - lo) / (hi - lo), 0.0, 1.0)


def read_yolo_boxes(label_path: Path, w: int, h: int):
    """Return list of (cls, x0, y0, x1, y1) in pixel coords."""
    boxes = []
    if not label_path.exists():
        return boxes
    for line in label_path.read_text().strip().splitlines():
        parts = line.split()
        if len(parts) < 5:
            continue
        cls = int(float(parts[0]))
        cx, cy, bw, bh = (float(v) for v in parts[1:5])
        x0 = int(max(0, (cx - bw / 2) * w)); x1 = int(min(w, (cx + bw / 2) * w))
        y0 = int(max(0, (cy - bh / 2) * h)); y1 = int(min(h, (cy + bh / 2) * h))
        if x1 > x0 and y1 > y0:
            boxes.append((cls, x0, y0, x1, y1))
    return boxes


def ring_mask(shape, box, expand=2.0):
    """Annulus between the box and an expanded box (background reference)."""
    h, w = shape
    _, x0, y0, x1, y1 = box
    bw, bh = x1 - x0, y1 - y0
    ex0 = int(max(0, x0 - bw * (expand - 1) / 2)); ex1 = int(min(w, x1 + bw * (expand - 1) / 2))
    ey0 = int(max(0, y0 - bh * (expand - 1) / 2)); ey1 = int(min(h, y1 + bh * (expand - 1) / 2))
    m = np.zeros(shape, bool)
    m[ey0:ey1, ex0:ex1] = True
    m[y0:y1, x0:x1] = False
    return m


def main() -> None:
    ap = argparse.ArgumentParser(description="IR victim-contrast verification")
    ap.add_argument("--ir-dir", required=True)
    ap.add_argument("--labels-dir", required=True)
    ap.add_argument("--output", required=True)
    ap.add_argument("--n-montage", type=int, default=20,
                    help="How many comparison montages to save (highest + random)")
    ap.add_argument("--seed", type=int, default=42)
    args = ap.parse_args()

    ir_dir, lb_dir = Path(args.ir_dir), Path(args.labels_dir)
    out_dir = Path(args.output); out_dir.mkdir(parents=True, exist_ok=True)

    files = sorted(ir_dir.glob("*.png"))
    print(f"{len(files)} IR frames")
    fmt_note_printed = False

    rows, per_frame = [], {}
    for f in files:
        ir, note = load_ir_linear(f)
        if not fmt_note_printed:
            print(f"format: {note}")
            fmt_note_printed = True
        h, w = ir.shape
        boxes = read_yolo_boxes(lb_dir / (f.stem + ".txt"), w, h)
        if not boxes:
            continue
        ir_a = agc(ir)
        frame_contrasts = []
        for b in boxes:
            cls, x0, y0, x1, y1 = b
            inside_raw = float(ir[y0:y1, x0:x1].mean())
            inside_agc = float(ir_a[y0:y1, x0:x1].mean())
            rm = ring_mask((h, w), b)
            if rm.sum() < 20:
                continue
            ring_raw = float(ir[rm].mean())
            ring_agc = float(ir_a[rm].mean())
            c_raw = (inside_raw - ring_raw) / (ring_raw + EPS)
            c_agc = inside_agc - ring_agc
            rows.append([f.name, cls, x0, y0, x1, y1,
                         f"{inside_raw:.6f}", f"{ring_raw:.6f}",
                         f"{c_raw:.4f}", f"{c_agc:.4f}"])
            frame_contrasts.append(c_agc)
        if frame_contrasts:
            per_frame[f.name] = float(np.mean(frame_contrasts))

    csv_path = out_dir / "ir_contrast.csv"
    with open(csv_path, "w", newline="") as fh:
        wtr = csv.writer(fh)
        wtr.writerow(["filename", "cls", "x0", "y0", "x1", "y1",
                      "mean_in_raw", "mean_ring_raw",
                      "weber_contrast_raw", "agc_contrast"])
        wtr.writerows(rows)

    if not rows:
        print("No victim boxes found -- check --labels-dir path."); return

    c_agc_all = np.array([float(r[9]) for r in rows])
    c_raw_all = np.array([float(r[8]) for r in rows])
    print(f"\ninstances: {len(rows)}")
    print(f"Weber contrast (raw linear): median={np.median(c_raw_all):.3f} "
          f"p10={np.percentile(c_raw_all, 10):.3f} p90={np.percentile(c_raw_all, 90):.3f}")
    print(f"AGC contrast (0-1 scale):    median={np.median(c_agc_all):.3f} "
          f"p10={np.percentile(c_agc_all, 10):.3f} p90={np.percentile(c_agc_all, 90):.3f}")
    frac_pos = float((c_agc_all > 0.05).mean())
    frac_neg = float((c_agc_all < 0.0).mean())
    print(f"instances with AGC contrast > 0.05 (clearly visible): {100*frac_pos:.1f}%")
    print(f"instances with AGC contrast < 0    (victim darker than bg): {100*frac_neg:.1f}%")
    print("rule of thumb: >70% clearly visible -> post-processing route viable;"
          " <40% -> plan the thermal-override re-render.")

    # Montages: frames with lowest mean contrast (hard cases) + random sample
    rng = random.Random(args.seed)
    ranked = sorted(per_frame, key=per_frame.get)          # worst first
    pick = ranked[: args.n_montage // 2]
    pool = [f for f in per_frame if f not in pick]
    pick += rng.sample(pool, min(args.n_montage - len(pick), len(pool)))
    for name in pick:
        ir, _ = load_ir_linear(ir_dir / name)
        h, w = ir.shape
        raw_vis = cv2.cvtColor((np.clip(ir / (ir.max() + EPS), 0, 1) * 255
                                ).astype(np.uint8), cv2.COLOR_GRAY2BGR)
        agc_vis = cv2.cvtColor((agc(ir) * 255).astype(np.uint8), cv2.COLOR_GRAY2BGR)
        for b in read_yolo_boxes(lb_dir / (Path(name).stem + ".txt"), w, h):
            _, x0, y0, x1, y1 = b
            for vis in (raw_vis, agc_vis):
                cv2.rectangle(vis, (x0, y0), (x1, y1), (0, 255, 0), 2)
        cv2.imwrite(str(out_dir / f"montage_{name}"), np.hstack([raw_vis, agc_vis]))

    print(f"\nCSV -> {csv_path}")
    print(f"{len(pick)} montages (left: raw max-normalized, right: AGC) -> {out_dir}")


if __name__ == "__main__":
    main()