"""
train_fusion.py

Trains the RGB baseline and the RGB-D early-fusion model under IDENTICAL
hyperparameters, so the only difference is the depth channel.

Requirements: ultralytics >= 8.3 (TIFF + `channels` dataset-YAML support).
  pip install -U ultralytics

Protocol notes (mirror them in the paper):
  - 60 epochs (matches the dataset-scaling protocol), imgsz 640, seed 0.
  - Color-space augmentations (hsv_h/s/v, bgr) are DISABLED for BOTH runs:
    they are undefined for a 4th metric channel, and disabling them for
    both keeps the comparison fair.
  - Both models start from yolov8m.pt; for the 4-channel model the first
    conv is adapted by ultralytics (mismatched weights re-initialized).

Usage:
  python train_fusion.py --rgb-root  "D:\\Fire_Project\\FireDataset_new2" ^
                         --rgbd-root "D:\\Fire_Project\\FireDataset_rgbd" ^
                         --device 0
"""

import argparse
from pathlib import Path

from ultralytics import YOLO

COMMON = dict(
    epochs=60, imgsz=640, seed=0, deterministic=True,
    hsv_h=0.0, hsv_s=0.0, hsv_v=0.0, bgr=0.0,
    patience=0, plots=True,
)


def write_yaml(path: Path, root: Path, channels: int) -> Path:
    lines = [
        f"path: {root.as_posix()}",
        "train: train/images",
        "val: val/images",
        "test: test/images",
        "names:",
        "  0: victim",
    ]
    if channels != 3:
        lines.insert(0, f"channels: {channels}")
    path.write_text("\n".join(lines) + "\n")
    return path


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--rgb-root", required=True)
    ap.add_argument("--rgbd-root", required=True)
    ap.add_argument("--device", default=0)
    ap.add_argument("--batch", type=int, default=16)
    ap.add_argument("--only", choices=["rgb", "rgbd"], default=None,
                    help="run just one of the two trainings")
    args = ap.parse_args()

    rgb_yaml = write_yaml(Path("data_rgb.yaml"), Path(args.rgb_root), 3)
    rgbd_yaml = write_yaml(Path("data_rgbd.yaml"), Path(args.rgbd_root), 4)

    runs = []
    if args.only in (None, "rgb"):
        runs.append(("fusion_rgb_baseline", rgb_yaml))
    if args.only in (None, "rgbd"):
        runs.append(("fusion_rgbd", rgbd_yaml))

    for name, data_yaml in runs:
        print(f"\n===== training {name} =====")
        model = YOLO("yolov8m.pt")
        model.train(data=str(data_yaml), name=name,
                    device=args.device, batch=args.batch, **COMMON)
        metrics = model.val(data=str(data_yaml), split="test")
        print(f"[{name}] test mAP@0.5 = {metrics.box.map50:.4f}  "
              f"mAP@0.5:0.95 = {metrics.box.map:.4f}  "
              f"P = {metrics.box.mp:.4f}  R = {metrics.box.mr:.4f}")

    print("\nWeights under runs/detect/<name>/weights/best.pt")
    print("Next: python stratified_eval.py for per-victim-type and "
          "smoke-severity breakdowns of both models.")


if __name__ == "__main__":
    main()