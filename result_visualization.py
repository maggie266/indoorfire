from ultralytics import YOLO
from pathlib import Path
import random
import re

DATASET_ROOT = Path('D:/Fire_Project/FireDataset_new2')
MODEL_PATH   = r'D:/Fire_Project/scripts/runs/detect/runs/baseline3/yolov8m/weights/best.pt'
OUT_DIR      = Path('D:/Fire_Project/detection_examples')
OUT_DIR.mkdir(exist_ok=True)

model = YOLO(MODEL_PATH)

test_imgs = list((DATASET_ROOT / 'test' / 'images').glob('*.png'))

# 每个类别选取的图片数量
N_PER_CATEGORY = 3  # 改这个数字控制每类选几张

categories = {
    'bedroom_horlook':    r'bedroom_.*horlook',
    'bedroom_overlook':   r'bedroom_.*overlook',
    'kitchen_horlook':    r'kitchen_.*horlook',
    'kitchen_overlook':   r'kitchen_.*overlook',
    'corridor_horlook':   r'corridor_.*horlook',
    'corridor_overlook':  r'corridor_.*overlook',
    'livingroom_horlook': r'livingroom_.*horlook',
    'livingroom_overlook':r'livingroom_.*overlook',
    'office_horlook':     r'office_.*horlook',
    'office_overlook':    r'office_.*overlook',
    'diningroom_horlook': r'diningroom_.*horlook',
    'diningroom_overlook':r'diningroom_.*overlook',
}

random.seed(42)
selected = []

for name, pattern in categories.items():
    matches = [f for f in test_imgs
               if re.search(pattern, f.name, re.IGNORECASE)]

    if not matches:
        print(f"⚠️  未找到: {name}")
        continue

    # 优先选有标注的图（文件大小>30KB说明有内容）
    valid = [f for f in matches if f.stat().st_size > 30 * 1024]
    pool  = valid if valid else matches

    n = min(N_PER_CATEGORY, len(pool))
    chosen = random.sample(pool, n)
    selected.extend(chosen)
    print(f"✅ {name}: 选取 {n} 张")

print(f"\n共选取 {len(selected)} 张图片，开始推理...")

# 批量推理
results = model.predict(
    source=selected,
    conf=0.25,
    iou=0.45,
    save=True,
    save_conf=True,
    project=str(OUT_DIR),
    name='predict',
    line_width=2,
)

print(f"\n✅ 检测结果已保存至: {OUT_DIR / 'predict'}/")
print(f"共生成 {len(results)} 张检测图")