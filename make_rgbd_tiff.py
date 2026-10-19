# """
# make_rgbd_tiff.py
#
# Compose RGB (PNG) + cleaned depth (uint16 mm PNG, 0=invalid) into 4-channel
# TIFF files, in a parallel dataset root that ultralytics can consume with
# `channels: 4` in the dataset YAML (PNG alpha is dropped by the ultralytics
# loader; TIFF is the supported multi-channel path).
#
# Layout created:
#   <out_root>/train/images/*.tiff   (BGR + depth as 4th channel, uint8)
#   <out_root>/train/labels/*.txt    (copied from source)
#   ... same for val/test
#
# Depth channel encoding (document in Methods):
#   d8 = clip(depth_mm / Z_MAX_MM, 0, 1) * 255, invalid (0) stays 0.
#
# Usage:
#   python make_rgbd_tiff.py --src "D:\\Fire_Project\\FireDataset_new2" ^
#                            --out "D:\\Fire_Project\\FireDataset_rgbd"
# """
#
# import argparse
# import shutil
# from pathlib import Path
#
# import cv2
# import numpy as np
#
# Z_MAX_MM = 10000.0          # 10 m normalization ceiling; clip beyond
# SPLITS = ("train", "val", "test")
# RGB_DIR, DEPTH_DIR, LABEL_DIR = "images", "Depth", "labels"
#
#
# def compose(rgb_path: Path, depth_path: Path) -> np.ndarray:
#     bgr = cv2.imread(str(rgb_path), cv2.IMREAD_COLOR)
#     d = cv2.imread(str(depth_path), cv2.IMREAD_UNCHANGED)
#     if bgr is None or d is None:
#         raise IOError(f"read failed: {rgb_path.name}")
#     if d.ndim == 3:
#         d = d[..., 0]
#     if d.shape[:2] != bgr.shape[:2]:
#         d = cv2.resize(d, (bgr.shape[1], bgr.shape[0]), interpolation=cv2.INTER_NEAREST)
#     if d.dtype == np.uint16:            # metric mm depth
#         d8 = (np.clip(d.astype(np.float32) / Z_MAX_MM, 0, 1) * 255.0 + 0.5).astype(np.uint8)
#     else:                               # 8-bit normalized relative depth: pass through
#         d8 = d.astype(np.uint8)
#     return np.dstack([bgr, d8])
#
#
# def main() -> None:
#     ap = argparse.ArgumentParser()
#     ap.add_argument("--src", required=True, help="FireDataset_new2 root")
#     ap.add_argument("--out", required=True, help="output RGBD dataset root")
#     args = ap.parse_args()
#     src, out = Path(args.src), Path(args.out)
#
#     for split in SPLITS:
#         img_out = out / split / "images"
#         lbl_out = out / split / "labels"
#         img_out.mkdir(parents=True, exist_ok=True)
#         lbl_out.mkdir(parents=True, exist_ok=True)
#
#         rgb_dir = src / split / RGB_DIR
#         dep_dir = src / split / DEPTH_DIR
#         lbl_dir = src / split / LABEL_DIR
#         files = sorted(rgb_dir.glob("*.png"))
#         print(f"[{split}] {len(files)} frames")
#         missing = 0
#         for i, f in enumerate(files):
#             dp = dep_dir / f.name
#             if not dp.exists():
#                 missing += 1
#                 continue
#             cv2.imwrite(str(img_out / (f.stem + ".tiff")), compose(f, dp))
#             lp = lbl_dir / (f.stem + ".txt")
#             if lp.exists():
#                 shutil.copy2(lp, lbl_out / lp.name)
#             if (i + 1) % 1000 == 0:
#                 print(f"  {i + 1}/{len(files)}")
#         if missing:
#             print(f"  WARNING: {missing} frames skipped (no matching depth)")
#     print(f"Done -> {out}")
#
#
# if __name__ == "__main__":
#     main()


import cv2, glob, numpy as np, os

files = glob.glob(r"D:\Fire_Project\FireDataset_rgbd\test\images\*.tiff")
print("找到", len(files), "个 TIFF")

p = files[0]
img = cv2.imread(p, cv2.IMREAD_UNCHANGED)
print("读取:", os.path.basename(p), "| shape:", img.shape)

out_path = r"D:\Fire_Project\align_check.png"
combo = np.hstack([img[..., :3], cv2.cvtColor(img[..., 3], cv2.COLOR_GRAY2BGR)])
ok = cv2.imwrite(out_path, combo)
print("写入", out_path, "->", "成功" if ok else "失败")

# 多存几帧,优先挑有人物的看
for p in files[1:4]:
    img = cv2.imread(p, cv2.IMREAD_UNCHANGED)
    combo = np.hstack([img[..., :3], cv2.cvtColor(img[..., 3], cv2.COLOR_GRAY2BGR)])
    name = os.path.splitext(os.path.basename(p))[0]
    cv2.imwrite(rf"D:\Fire_Project\align_check_{name}.png", combo)
print("完成,共 4 张对齐检查图")