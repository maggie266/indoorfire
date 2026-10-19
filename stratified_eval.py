"""
stratified_eval.py

Stratified test-set evaluation for any trained detector (existing YOLOv8m
weights, or the RGB / RGB-D fusion models):

  1. VICTIM-TYPE strata -- labels are single-class ("victim"), so per-type
     AP is computed by evaluating on filename-defined subsets: frames whose
     filename contains exactly one victim token form that type's stratum;
     frames with 2+ tokens form the "multi" stratum. This mirrors the
     paper's scene/viewpoint stratification.
  2. SMOKE-SEVERITY strata -- test frames are split into quartiles of the
     per-frame depth invalid fraction (invalid_fraction_Depth_clean.csv),
     the scatter-based visibility proxy established in Technical
     Validation. Q4 = heaviest smoke. Comparing RGB vs RGB-D across
     quartiles is the fusion experiment's key table.

Usage (run once per model):
  python stratified_eval.py ^
      --weights "runs/detect/fusion_rgbd/weights/best.pt" ^
      --data-root "D:\\Fire_Project\\FireDataset_rgbd" --channels 4 ^
      --invalid-csv "D:\\Fire_Project\\FireDataset_new2\\test\\invalid_fraction_Depth_clean.csv" ^
      --tag rgbd

For the existing paper model / RGB baseline: --data-root <rgb root>
--channels 3 (test images are .png there; extension is auto-detected).

Output: stratified_<tag>.csv with one row per stratum
        (N, mAP50, mAP50-95, precision, recall).
"""

import argparse
import csv
import shutil
import tempfile
from collections import defaultdict
from pathlib import Path

from ultralytics import YOLO

import re

# Actual filename vocabulary (verified against the dataset):
#   man -> adult male, woman -> adult female; child/elderly/worker/dog/cat
#   literal. Noise tokens like route1/route2 (Follow Path names) are
#   stripped. Frames named only by scene config IDs (scene*_loc*,
#   including the 'sence' typo) carry no victim field -> "multi" stratum
#   (they are multi-character scene renders); resolve exactly via the
#   released metadata.csv if finer grouping is needed.
TOKEN_MAP = {"man": "adult_male", "woman": "adult_female",
             "child": "child", "elderly": "elderly", "worker": "worker",
             "dog": "dog", "cat": "cat"}
SCENE_ID_RE = re.compile(r"s[cen]{3,4}e?\d+_loc\d+")   # scene4_loc4 / sence2_loc1


def victim_types(stem: str):
    """Return the set of victim types for a filename stem.
    Returns {"__sceneid__"} for scene-config-named (multi-character) frames."""
    s = stem.lower()
    if SCENE_ID_RE.search(s):
        return {"__sceneid__"}
    found = set()
    for part in s.split("_"):
        # 'woman' contains 'man': match whole tokens only
        if part in TOKEN_MAP:
            found.add(TOKEN_MAP[part])
    return found


def eval_subset(model, frames, data_root: Path, channels: int, name: str):
    """Build a temp split containing only `frames` and run model.val()."""
    if not frames:
        return None
    tmp = Path(tempfile.mkdtemp(prefix=f"strat_{name}_"))
    (tmp / "images").mkdir()
    (tmp / "labels").mkdir()
    src_img = data_root / "test" / "images"
    src_lbl = data_root / "test" / "labels"
    for f in frames:
        shutil.copy2(src_img / f, tmp / "images" / f)
        lbl = src_lbl / (Path(f).stem + ".txt")
        if lbl.exists():
            shutil.copy2(lbl, tmp / "labels" / lbl.name)
    yaml_path = tmp / "data.yaml"
    lines = [f"path: {tmp.as_posix()}", "train: images", "val: images",
             "names:", "  0: victim"]
    if channels != 3:
        lines.insert(0, f"channels: {channels}")
    yaml_path.write_text("\n".join(lines) + "\n")
    m = model.val(data=str(yaml_path), split="val", verbose=False)
    shutil.rmtree(tmp, ignore_errors=True)
    return dict(N=len(frames), map50=m.box.map50, map=m.box.map,
                p=m.box.mp, r=m.box.mr)


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--weights", required=True)
    ap.add_argument("--data-root", required=True,
                    help="dataset root containing test/images + test/labels")
    ap.add_argument("--channels", type=int, default=3)
    ap.add_argument("--invalid-csv", default=None,
                    help="test invalid_fraction CSV for smoke-severity strata")
    ap.add_argument("--tag", default="model")
    args = ap.parse_args()

    data_root = Path(args.data_root)
    img_dir = data_root / "test" / "images"
    frames = sorted(p.name for p in img_dir.iterdir()
                    if p.suffix.lower() in (".png", ".tiff", ".tif", ".jpg"))
    print(f"{len(frames)} test frames")

    model = YOLO(args.weights)
    rows = []

    # ---- victim-type strata ------------------------------------------------
    groups = defaultdict(list)
    combos = defaultdict(int)
    for f in frames:
        types = victim_types(Path(f).stem)
        combos[",".join(sorted(types)) or "none"] += 1
        if types == {"__sceneid__"}:
            groups["multi"].append(f)          # scene-config-named frames
        elif len(types) == 0:
            groups["none"].append(f)
        elif len(types) == 1:
            groups[next(iter(types))].append(f)
        else:
            groups["multi"].append(f)
    print("token combos found (verify these look right):")
    for k, v in sorted(combos.items(), key=lambda x: -x[1]):
        print(f"  {k}: {v}")

    for name, fs in sorted(groups.items()):
        if name == "none":
            continue
        r = eval_subset(model, fs, data_root, args.channels, name)
        if r:
            rows.append([f"victim:{name}", r["N"], f"{r['map50']:.4f}",
                         f"{r['map']:.4f}", f"{r['p']:.4f}", f"{r['r']:.4f}"])
            print(f"  victim:{name:14s} N={r['N']:4d}  mAP50={r['map50']:.3f}")

    # ---- smoke-severity strata (invalid-fraction quartiles) ----------------
    if args.invalid_csv:
        inv = {}
        with open(args.invalid_csv) as fh:
            for row in csv.DictReader(fh):
                inv[Path(row["filename"]).stem] = float(row["invalid_fraction"])
        scored = [(f, inv[Path(f).stem]) for f in frames if Path(f).stem in inv]
        scored.sort(key=lambda x: x[1])
        n = len(scored)
        print(f"\nsmoke strata from {n} frames with invalid-fraction scores")
        for qi in range(4):
            part = [f for f, _ in scored[qi * n // 4:(qi + 1) * n // 4]]
            lo = scored[qi * n // 4][1]
            hi = scored[min((qi + 1) * n // 4, n) - 1][1]
            r = eval_subset(model, part, data_root, args.channels, f"q{qi+1}")
            if r:
                rows.append([f"smoke:Q{qi+1}[{lo:.3f}-{hi:.3f}]", r["N"],
                             f"{r['map50']:.4f}", f"{r['map']:.4f}",
                             f"{r['p']:.4f}", f"{r['r']:.4f}"])
                print(f"  Q{qi+1} (inv {lo:.3f}-{hi:.3f}) N={r['N']:4d}  "
                      f"mAP50={r['map50']:.3f}  R={r['r']:.3f}")

    out = Path(f"stratified_{args.tag}.csv")
    with open(out, "w", newline="") as fh:
        w = csv.writer(fh)
        w.writerow(["stratum", "N", "mAP50", "mAP50-95", "precision", "recall"])
        w.writerows(rows)
    print(f"\nCSV -> {out}")


if __name__ == "__main__":
    main()