import cv2, csv, os, glob

root =r"D:\Fire_Project\FireDataset_new2"

for split in ["train", "val", "test"]:
    rows = []
    files = sorted(glob.glob(os.path.join(root, split, "Depth", "*.png")))
    print(f"[{split}] {len(files)} frames")
    for i, p in enumerate(files):
        d = cv2.imread(p, cv2.IMREAD_UNCHANGED)
        if d is None:
            print("  read failed:", os.path.basename(p)); continue
        if d.ndim == 3:
            d = d[..., 0]
        rows.append((os.path.basename(p), f"{(d == 0).mean():.6f}"))
        if (i + 1) % 1000 == 0:
            print(f"  {i + 1}/{len(files)}")
    out = os.path.join(root, split, "zero_fraction_depth.csv")
    with open(out, "w", newline="") as f:
        w = csv.writer(f)
        w.writerow(["filename", "invalid_fraction"])   # 列名沿用,stratified_eval 无需改
        w.writerows(rows)
    vals = [float(r[1]) for r in rows]
    vals.sort()
    n = len(vals)
    print(f"  -> {out}")
    print(f"  mean={sum(vals)/n:.4f}  median={vals[n//2]:.4f}  max={vals[-1]:.4f}")