# #划分测试数据集
# from pathlib import Path
#
# TEST_IMG_DIR = Path('D:/Fire_Project/FireDataset_new2/test/images')
# SAVE_DIR     = Path('D:/Fire_Project/stratified_eval')
# SAVE_DIR.mkdir(exist_ok=True)
#
# # 按场景类型筛选
# SCENE_KEYWORDS = {
#     'Bedroom':     'bedroom',
#     'Living room': 'livingroom',
#     'Kitchen':     'kitchen',
#     'Office':      'office',
#     'Dining room': 'diningroom',
#     'Corridor':    'corridor',
# }
#
# # 按视角筛选
# VIEW_KEYWORDS = {
#     'Horizontal': 'horlook',
#     'Overhead':   'overlook',
# }
#
# all_keywords = {**SCENE_KEYWORDS, **VIEW_KEYWORDS}
#
# for subset_name, keyword in all_keywords.items():
#     # 找匹配的图片
#     matched = [
#         str(p) for p in TEST_IMG_DIR.glob('*.png')
#         if keyword.lower() in p.name.lower()
#     ]
#
#     # 写入txt文件（YOLO val支持直接读取图片列表）
#     txt_path = SAVE_DIR / f'{subset_name.replace(" ","_")}.txt'
#     txt_path.write_text('\n'.join(matched), encoding='utf-8')
#     print(f"{subset_name}: {len(matched)} 张图片 → {txt_path.name}")

#测试
# from ultralytics import YOLO
# import pandas as pd
# from pathlib import Path
# import shutil
# import yaml
#
# MODEL_PATH   = r'D:/Fire_Project/scripts/runs/detect/runs/baseline3/yolov8m/weights/best.pt'
# DATASET_YAML = r'D:/Fire_Project/FireDataset_new2/dataset.yaml'
# TEST_IMG_DIR = Path('D:/Fire_Project/FireDataset_new2/test/images')
# TEST_LBL_DIR = Path('D:/Fire_Project/FireDataset_new2/test/labels')
# SAVE_DIR     = Path('D:/Fire_Project/stratified_eval')
# TMP_DIR      = Path('D:/Fire_Project/stratified_tmp')
#
# SUBSETS = {
#     'Bedroom':     'bedroom',
#     'Living room': 'livingroom',
#     'Kitchen':     'kitchen',
#     'Office':      'office',
#     'Dining room': 'diningroom',
#     'Corridor':    'corridor',
#     'Horizontal':  'horlook',
#     'Overhead':    'overlook',
# }
#
# if __name__ == '__main__':
#     model = YOLO(MODEL_PATH)
#     results = []
#
#     for subset_name, keyword in SUBSETS.items():
#
#         # 找匹配图片
#         matched_imgs = [
#             p for p in TEST_IMG_DIR.glob('*.png')
#             if keyword.lower() in p.name.lower()
#         ]
#         if not matched_imgs:
#             print(f"⚠️ {subset_name}: 未找到图片")
#             continue
#
#         # 建临时数据集目录
#         tmp_img = TMP_DIR / 'images'
#         tmp_lbl = TMP_DIR / 'labels'
#         tmp_img.mkdir(parents=True, exist_ok=True)
#         tmp_lbl.mkdir(parents=True, exist_ok=True)
#
#         # 复制匹配的图片和标注
#         for img_path in matched_imgs:
#             shutil.copy2(img_path, tmp_img / img_path.name)
#             lbl_path = TEST_LBL_DIR / (img_path.stem + '.txt')
#             if lbl_path.exists():
#                 shutil.copy2(lbl_path, tmp_lbl / lbl_path.name)
#
#         # 生成临时yaml
#         tmp_yaml = TMP_DIR / 'tmp.yaml'
#         yaml_content = {
#             'path': str(TMP_DIR),
#             'train': 'images',
#             'val':   'images',
#             'test':  'images',
#             'nc': 1,
#             'names': ['victim']
#         }
#         tmp_yaml.write_text(
#             yaml.dump(yaml_content, allow_unicode=True),
#             encoding='utf-8'
#         )
#
#         # 评估
#         print(f"\n评估: {subset_name} ({len(matched_imgs)}张)")
#         metrics = model.val(
#             data=str(tmp_yaml),
#             split='test',
#             device=0,
#             batch=8,
#             verbose=False,
#             workers=0,
#         )
#
#         results.append({
#             'Subset':        subset_name,
#             'N':             len(matched_imgs),
#             'mAP@0.5':       round(metrics.box.map50, 3),
#             'mAP@0.5:0.95':  round(metrics.box.map, 3),
#             'Precision':     round(float(metrics.box.p.mean()), 3),
#             'Recall':        round(float(metrics.box.r.mean()), 3),
#         })
#
#         # 清空临时目录
#         shutil.rmtree(TMP_DIR)
#
#     # 输出结果
#     df = pd.DataFrame(results)
#     print("\n" + "="*65)
#     print("分层评估结果")
#     print("="*65)
#     print(df.to_string(index=False))
#
#     save_path = SAVE_DIR / 'stratified_results.csv'
#     df.to_csv(save_path, index=False, encoding='utf-8-sig')
#     print(f"\n✅ 结果已保存: {save_path}")

from ultralytics import YOLO
import pandas as pd
from pathlib import Path
import shutil
import yaml

MODEL_PATH   = r'D:/Fire_Project/scripts/runs/detect/runs/baseline3/yolov8m/weights/best.pt'
DATASET_YAML = r'D:/Fire_Project/FireDataset_new2/dataset.yaml'
TEST_IMG_DIR = Path('D:/Fire_Project/FireDataset_new2/test/images')
TEST_LBL_DIR = Path('D:/Fire_Project/FireDataset_new2/test/labels')
SAVE_DIR     = Path('D:/Fire_Project/stratified_eval')
TMP_DIR      = Path('D:/Fire_Project/stratified_tmp')

SAVE_DIR.mkdir(exist_ok=True)

# 场景和视角子集
SCENE_VIEW_SUBSETS = {
    'Bedroom':     'bedroom',
    'Living room': 'livingroom',
    'Kitchen':     'kitchen',
    'Office':      'office',
    'Dining room': 'diningroom',
    'Corridor':    'corridor',
    'Horizontal':  'horlook',
    'Overhead':    'overlook',
}

# 动作子集（关键词对应文件名中的动作字段）
POSE_SUBSETS = {
    'Crawling':               'crawling',
    'Fall flat':              'fall_flat',
    'Hit to side of body':    'hit_to_side_of_body',
    'Injured run':            'injured_run',
    'Injured walk backwards': 'injured_walk_backwards',
    'Sit to stand':           'sit_to_stand',
    'Sitting':                'sitting',
    'Slow run':               'slow_run',
    'Standing idle':          'standing_idle',
    'Standing yell':          'standing_yell',
}

def run_eval(model, subset_name, keyword, category):
    """对一个子集运行评估，返回结果dict"""
    matched_imgs = [
        p for p in TEST_IMG_DIR.glob('*.png')
        if keyword.lower() in p.name.lower()
    ]
    if not matched_imgs:
        print(f"⚠️  {subset_name}: 未找到图片，跳过")
        return None

    # 建临时目录
    tmp_img = TMP_DIR / 'images'
    tmp_lbl = TMP_DIR / 'labels'
    tmp_img.mkdir(parents=True, exist_ok=True)
    tmp_lbl.mkdir(parents=True, exist_ok=True)

    for img_path in matched_imgs:
        shutil.copy2(img_path, tmp_img / img_path.name)
        lbl_path = TEST_LBL_DIR / (img_path.stem + '.txt')
        if lbl_path.exists():
            shutil.copy2(lbl_path, tmp_lbl / lbl_path.name)

    tmp_yaml = TMP_DIR / 'tmp.yaml'
    tmp_yaml.write_text(
        yaml.dump({
            'path': str(TMP_DIR),
            'train': 'images', 'val': 'images', 'test': 'images',
            'nc': 1, 'names': ['victim']
        }, allow_unicode=True),
        encoding='utf-8'
    )

    print(f"  评估: {subset_name} ({len(matched_imgs)}张)")
    metrics = model.val(
        data=str(tmp_yaml),
        split='test',
        device=0,
        batch=8,
        verbose=False,
        workers=0,
    )

    shutil.rmtree(TMP_DIR)

    return {
        'Category':      category,
        'Subset':        subset_name,
        'N':             len(matched_imgs),
        'mAP@0.5':       round(metrics.box.map50, 3),
        'mAP@0.5:0.95':  round(metrics.box.map, 3),
        'Precision':     round(float(metrics.box.p.mean()), 3),
        'Recall':        round(float(metrics.box.r.mean()), 3),
    }


if __name__ == '__main__':
    model = YOLO(MODEL_PATH)
    results = []

    # ── 场景和视角评估 ────────────────────────────────
    print("\n" + "="*60)
    print("场景和视角分层评估")
    print("="*60)
    for subset_name, keyword in SCENE_VIEW_SUBSETS.items():
        r = run_eval(model, subset_name, keyword, 'Scene/Viewpoint')
        if r:
            results.append(r)

    # ── 动作姿势评估 ──────────────────────────────────
    print("\n" + "="*60)
    print("动作姿势分层评估")
    print("="*60)
    for subset_name, keyword in POSE_SUBSETS.items():
        r = run_eval(model, subset_name, keyword, 'Pose')
        if r:
            results.append(r)

    # ── 输出汇总 ──────────────────────────────────────
    df = pd.DataFrame(results)

    print("\n" + "="*70)
    print("完整分层评估结果")
    print("="*70)

    for cat in ['Scene/Viewpoint', 'Pose']:
        sub = df[df['Category'] == cat]
        print(f"\n[{cat}]")
        print(sub.drop(columns='Category').to_string(index=False))

    save_path = SAVE_DIR / 'stratified_results_full.csv'
    df.to_csv(save_path, index=False, encoding='utf-8-sig')
    print(f"\n✅ 完整结果已保存: {save_path}")

    # ── 单独保存两个子表 ──────────────────────────────
    df[df['Category'] == 'Scene/Viewpoint'].drop(columns='Category').to_csv(
        SAVE_DIR / 'stratified_scene_view.csv', index=False, encoding='utf-8-sig')
    df[df['Category'] == 'Pose'].drop(columns='Category').to_csv(
        SAVE_DIR / 'stratified_pose.csv', index=False, encoding='utf-8-sig')
    print("✅ 子表已分别保存")