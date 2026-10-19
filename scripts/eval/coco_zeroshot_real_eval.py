"""
COCO zero-shot baseline on the 100 real fire images.

Purpose
-------
Table 4 of the paper reports a COCO-pretrained YOLOv8m evaluated zero-shot
on the SYNTHETIC test set (mAP@0.5 = 70.3%), with person/cat/dog predictions
mapped to the single "victim" class.

This script runs the SAME model, under the SAME class-mapping rule, on the
100 REAL fire images used in Section 3.6, so the paper can report a
COCO-only real-world baseline alongside the reference model's 44.7%
zero-shot transfer result (Table 9). This isolates how much of the 44.7%
is attributable to synthetic pretraining versus generic COCO person/animal
detection capability.

No training is performed. This is inference + evaluation only.

Expected data layout
---------------------
real_images/
    img_0001.jpg
    img_0002.jpg
    ...
real_labels/
    img_0001.txt   # YOLO format, single class 0 = "victim", normalized xywh
    img_0002.txt
    ...

Ground-truth label files must follow standard YOLO format:
    <class_id> <x_center> <y_center> <width> <height>   (all normalized 0-1)
For this dataset class_id is always 0 ("victim"), consistent with the
paper's single-class annotation convention.

Requirements
------------
pip install ultralytics pycocotools --break-system-packages

Usage
-----
python coco_zeroshot_real_eval.py \
    --images /path/to/real_images \
    --labels /path/to/real_labels \
    --conf 0.25

Output
------
Prints precision, recall, mAP@0.5, and mAP@0.5:0.95, matching the format
of Table 9. Also writes a coco_zeroshot_real_results.json with per-image
predictions for auditing.
"""

import argparse
import json
import os
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont
from ultralytics import YOLO
from pycocotools.coco import COCO
from pycocotools.cocoeval import COCOeval

# COCO class indices (0-indexed, as used by Ultralytics) that are mapped
# onto the single "victim" class, matching the Table 4 protocol.
COCO_VICTIM_SOURCE_CLASSES = {0: "person", 15: "cat", 16: "dog"}
VICTIM_CATEGORY_ID = 1  # single-class COCO category id used for evaluation


def yolo_txt_to_xyxy(label_path, img_w, img_h):
    """Read a YOLO-format label file and return boxes in absolute xyxy."""
    boxes = []
    if not os.path.exists(label_path):
        return boxes
    with open(label_path, "r") as f:
        for line in f:
            parts = line.strip().split()
            if len(parts) != 5:
                continue
            _, xc, yc, w, h = map(float, parts)
            xc, yc, w, h = xc * img_w, yc * img_h, w * img_w, h * img_h
            x1, y1 = xc - w / 2, yc - h / 2
            boxes.append([x1, y1, w, h])  # COCO format: x, y, width, height
    return boxes


def build_ground_truth_coco(image_dir, label_dir, image_files):
    """Assemble a COCO-format ground-truth dict from YOLO label files."""
    images, annotations = [], []
    ann_id = 1
    for img_id, img_name in enumerate(image_files, start=1):
        img_path = os.path.join(image_dir, img_name)
        with Image.open(img_path) as im:
            w, h = im.size
        images.append({"id": img_id, "file_name": img_name, "width": w, "height": h})

        label_name = os.path.splitext(img_name)[0] + ".txt"
        label_path = os.path.join(label_dir, label_name)
        for box in yolo_txt_to_xyxy(label_path, w, h):
            annotations.append({
                "id": ann_id,
                "image_id": img_id,
                "category_id": VICTIM_CATEGORY_ID,
                "bbox": box,
                "area": box[2] * box[3],
                "iscrowd": 0,
            })
            ann_id += 1

    return {
        "images": images,
        "annotations": annotations,
        "categories": [{"id": VICTIM_CATEGORY_ID, "name": "victim"}],
    }


def save_visualizations(image_dir, image_files, detections, out_dir):
    """Draw only the person/cat/dog -> victim boxes actually used for
    evaluation (not the raw 80-class COCO output) and save one annotated
    image per input file, so the saved images match exactly what the
    metrics were computed from."""
    os.makedirs(out_dir, exist_ok=True)
    dets_by_img = {}
    for det in detections:
        dets_by_img.setdefault(det["image_id"], []).append(det)

    try:
        font = ImageFont.truetype("arial.ttf", 18)
    except Exception:
        font = ImageFont.load_default()

    for img_id, img_name in enumerate(image_files, start=1):
        img_path = os.path.join(image_dir, img_name)
        img = Image.open(img_path).convert("RGB")
        draw = ImageDraw.Draw(img)

        for det in dets_by_img.get(img_id, []):
            x, y, w, h = det["bbox"]
            x1, y1, x2, y2 = x, y, x + w, y + h
            draw.rectangle([x1, y1, x2, y2], outline="red", width=3)
            label = f"victim {det['score']:.2f}"
            text_bbox = draw.textbbox((x1, y1), label, font=font)
            draw.rectangle(text_bbox, fill="red")
            draw.text((x1, y1), label, fill="white", font=font)

        img.save(os.path.join(out_dir, img_name))

    print(f"Saved {len(image_files)} annotated images to '{out_dir}'.")


def run_inference(model, image_dir, image_files, conf):
    """Run COCO-pretrained YOLOv8m, keep person/cat/dog, remap to victim."""
    detections = []
    name_to_id = {name: idx + 1 for idx, name in enumerate(image_files)}

    for img_id, img_name in enumerate(image_files, start=1):
        img_path = os.path.join(image_dir, img_name)
        results = model.predict(img_path, conf=conf, verbose=False)[0]

        for box, cls_id, score in zip(
            results.boxes.xyxy.cpu().numpy(),
            results.boxes.cls.cpu().numpy().astype(int),
            results.boxes.conf.cpu().numpy(),
        ):
            if cls_id not in COCO_VICTIM_SOURCE_CLASSES:
                continue  # discard anything that is not person/cat/dog
            x1, y1, x2, y2 = box
            detections.append({
                "image_id": img_id,
                "category_id": VICTIM_CATEGORY_ID,
                "bbox": [float(x1), float(y1), float(x2 - x1), float(y2 - y1)],
                "score": float(score),
            })

    return detections


def compute_precision_recall_at_50(gt_coco, detections, iou_thresh=0.5):
    """Simple greedy single-class precision/recall at a fixed IoU threshold,
    matching the operating-point convention used elsewhere in the paper
    (Table 4 / Table 9 report precision and recall at the default
    confidence operating point, not just mAP)."""
    from collections import defaultdict

    gt_by_img = defaultdict(list)
    for ann in gt_coco["annotations"]:
        gt_by_img[ann["image_id"]].append(ann["bbox"])

    dets_sorted = sorted(detections, key=lambda d: -d["score"])
    matched_gt = defaultdict(set)
    tp, fp = 0, 0

    def iou(box_a, box_b):
        ax1, ay1, aw, ah = box_a
        bx1, by1, bw, bh = box_b
        ax2, ay2 = ax1 + aw, ay1 + ah
        bx2, by2 = bx1 + bw, by1 + bh
        ix1, iy1 = max(ax1, bx1), max(ay1, by1)
        ix2, iy2 = min(ax2, bx2), min(ay2, by2)
        iw, ih = max(0, ix2 - ix1), max(0, iy2 - iy1)
        inter = iw * ih
        union = aw * ah + bw * bh - inter
        return inter / union if union > 0 else 0

    for det in dets_sorted:
        img_id = det["image_id"]
        best_iou, best_idx = 0, -1
        for idx, gt_box in enumerate(gt_by_img[img_id]):
            if idx in matched_gt[img_id]:
                continue
            cur_iou = iou(det["bbox"], gt_box)
            if cur_iou > best_iou:
                best_iou, best_idx = cur_iou, idx
        if best_iou >= iou_thresh:
            tp += 1
            matched_gt[img_id].add(best_idx)
        else:
            fp += 1

    total_gt = sum(len(v) for v in gt_by_img.values())
    precision = tp / (tp + fp) if (tp + fp) > 0 else 0.0
    recall = tp / total_gt if total_gt > 0 else 0.0
    return precision, recall


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--images", required=True, help="Path to the 100 real fire images")
    parser.add_argument("--labels", required=True, help="Path to YOLO-format ground-truth labels")
    parser.add_argument("--conf", type=float, default=0.25, help="Confidence threshold (default: 0.25)")
    parser.add_argument("--weights", default="yolov8m.pt", help="Original COCO-pretrained weights (not fine-tuned)")
    parser.add_argument("--out", default="coco_zeroshot_real_results.json")
    parser.add_argument("--save_vis", default=None,
                         help="If set, save annotated detection images to this directory")
    args = parser.parse_args()

    image_files = sorted([
        f for f in os.listdir(args.images)
        if f.lower().endswith((".jpg", ".jpeg", ".png"))
    ])
    print(f"Found {len(image_files)} real images.")

    print("Loading original COCO-pretrained YOLOv8m (no fine-tuning)...")
    model = YOLO(args.weights)

    print("Building ground-truth annotations...")
    gt_coco = build_ground_truth_coco(args.images, args.labels, image_files)

    print(f"Running zero-shot inference at conf={args.conf}...")
    detections = run_inference(model, args.images, image_files, args.conf)
    print(f"Kept {len(detections)} person/cat/dog detections mapped to 'victim'.")

    if args.save_vis:
        save_visualizations(args.images, image_files, detections, args.save_vis)

    with open(args.out, "w") as f:
        json.dump({"ground_truth": gt_coco, "detections": detections}, f)

    # --- mAP@0.5 and mAP@0.5:0.95 via pycocotools ---
    gt_json_path = "_tmp_gt.json"
    with open(gt_json_path, "w") as f:
        json.dump(gt_coco, f)
    coco_gt = COCO(gt_json_path)
    coco_dt = coco_gt.loadRes(detections) if detections else None

    if coco_dt is not None:
        coco_eval = COCOeval(coco_gt, coco_dt, iouType="bbox")
        coco_eval.evaluate()
        coco_eval.accumulate()
        coco_eval.summarize()
        map_5095 = coco_eval.stats[0]
        map_50 = coco_eval.stats[1]
    else:
        map_5095, map_50 = 0.0, 0.0

    # --- Precision / recall at the default operating point ---
    precision, recall = compute_precision_recall_at_50(gt_coco, detections, iou_thresh=0.5)

    print("\n=== COCO zero-shot baseline on 100 real fire images ===")
    print(f"{'Setting':<12}{'Images':<10}{'Precision':<12}{'Recall':<10}{'mAP@0.5':<10}{'mAP@0.5:0.95':<12}")
    print(f"{'COCO-only':<12}{len(image_files):<10}"
          f"{precision*100:<12.1f}{recall*100:<10.1f}{map_50*100:<10.1f}{map_5095*100:<12.1f}")

    os.remove(gt_json_path)


if __name__ == "__main__":
    main()