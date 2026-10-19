from ultralytics import YOLO
from pathlib import Path
import cv2
import numpy as np
import matplotlib.pyplot as plt
import matplotlib as mpl
import shutil

mpl.rcParams['font.family'] = 'Times New Roman'

MODEL_PATH  = r'D:/Fire_Project/scripts/runs/detect/runs/baseline4/yolov8m/weights/best.pt'
REAL_IMGS   = r"D:\Fire_Project\real\images1"   # 你的真实图片目录
OUT_DIR     = Path(r'D:/Fire_Project/sim_to_real5')
OUT_DIR.mkdir(exist_ok=True)

if __name__ == '__main__':
    model = YOLO(MODEL_PATH)

    # ── 第一步：推理所有真实图片 ──────────────────────
    results = model.predict(
        source=REAL_IMGS,
        conf=0.25,          # 置信度阈值
        iou=0.45,
        save=True,
        save_conf=True,     # 在框上显示置信度
        line_width=2,
        project=str(OUT_DIR),
        name='predict',
        exist_ok=True,
    )

    print(f"✅ 推理完成，共 {len(results)} 张图片")
    print(f"结果保存至: {OUT_DIR / 'predict'}")

    # ── 第二步：统计检测结果 ──────────────────────────
    total_imgs    = len(results)
    detected_imgs = sum(1 for r in results if len(r.boxes) > 0)
    total_dets    = sum(len(r.boxes) for r in results)
    all_conf      = [float(c) for r in results for c in r.boxes.conf]

    print(f"\n检测统计:")
    print(f"  图片总数:       {total_imgs}")
    print(f"  有检测框的图:   {detected_imgs} ({detected_imgs/total_imgs*100:.1f}%)")
    print(f"  总检测框数:     {total_dets}")
    if all_conf:
        print(f"  平均置信度:     {np.mean(all_conf):.3f}")
        print(f"  置信度范围:     {min(all_conf):.3f} ~ {max(all_conf):.3f}")

    # ── 第三步：生成论文用拼接图 ──────────────────────
    # 从predict目录找所有结果图
    pred_dir = OUT_DIR / 'predict'
    pred_imgs = sorted(pred_dir.glob('*.jpg')) + sorted(pred_dir.glob('*.png'))

    if not pred_imgs:
        print("⚠️ 未找到结果图片")
        exit()

    # 选取有检测结果的图（文件大小较大通常有内容）
    # 手动筛选：有框的优先
    selected = []
    for r, img_path in zip(results, pred_imgs):
        if len(r.boxes) > 0:
            selected.append((img_path, len(r.boxes),
                             float(r.boxes.conf.mean())))

    # 按检测框数量排序，优先选多框的
    selected.sort(key=lambda x: x[1], reverse=True)

    # 取前6张（论文用2×3排列）
    n_show = min(6, len(selected))
    if n_show == 0:
        # 如果都没检测到，随机取6张
        selected = [(p, 0, 0) for p in pred_imgs[:6]]
        n_show = len(selected)

    print(f"\n选取 {n_show} 张用于论文拼图")

    fig, axes = plt.subplots(2, 3, figsize=(15, 8))
    axes = axes.flatten()

    for i in range(n_show):
        img_path = selected[i][0]
        n_boxes  = selected[i][1]
        avg_conf = selected[i][2]

        img = cv2.imread(str(img_path))
        img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)

        axes[i].imshow(img)
        axes[i].axis('off')

        if n_boxes > 0:
            axes[i].set_title(
                f'Detections: {n_boxes}  |  Avg conf: {avg_conf:.2f}',
                fontsize=10, pad=4
            )
        else:
            axes[i].set_title('No detection', fontsize=10, pad=4,
                               color='gray')

    # 隐藏多余子图
    for j in range(n_show, len(axes)):
        axes[j].axis('off')

    fig.suptitle(
        'Qualitative Sim-to-Real Generalization on Real Indoor Fire Images\n'
        '(YOLOv8m trained solely on synthetic data)',
        fontsize=13, fontweight='bold', y=1.01
    )
    plt.tight_layout(pad=1.0)

    grid_path = OUT_DIR / 'sim_to_real_grid.png'
    plt.savefig(grid_path, dpi=200, bbox_inches='tight',
                facecolor='white')
    plt.close()
    print(f"✅ 拼图已保存: {grid_path}")

    # ── 第四步：单独保存每张结果图 ────────────────────
    single_dir = OUT_DIR / 'selected'
    single_dir.mkdir(exist_ok=True)
    for idx, (img_path, n_boxes, conf) in enumerate(selected[:n_show]):
        dst = single_dir / f'real_{idx+1:02d}_{n_boxes}boxes.png'
        shutil.copy2(img_path, dst)

    print(f"✅ 单张结果图保存至: {single_dir}")
    print(f"\n论文用图: {grid_path}")
# # from ultralytics import YOLO
# # import pandas as pd
# # import shutil
# # import yaml
# # import random
# # from pathlib import Path
# #
# # DATASET_ROOT = Path('D:/Fire_Project/FireDataset_new2')
# # BASE_DIR     = Path('D:/Fire_Project/runs/scaling')
# # DATASET_YAML = r'D:/Fire_Project/FireDataset_new2/dataset.yaml'
# #
# # # 使用10%/25%/50%/75%/100%的训练数据
# # RATIOS = [0.1, 0.25, 0.5, 0.75, 1.0]
# #
# # train_imgs = list((DATASET_ROOT / 'train' / 'images').glob('*.png'))
# # train_lbls = DATASET_ROOT / 'train' / 'labels'
# #
# # random.seed(42)
# # results = []
# #
# # if __name__ == '__main__':
# #     for ratio in RATIOS:
# #         n = int(len(train_imgs) * ratio)
# #         sampled = random.sample(train_imgs, n)
# #         print(f"\n训练数据量: {n} 张 ({ratio*100:.0f}%)")
# #
# #         # 建临时训练集
# #         tmp = Path(f'D:/Fire_Project/scaling_tmp_{int(ratio*100)}')
# #         (tmp / 'train' / 'images').mkdir(parents=True, exist_ok=True)
# #         (tmp / 'train' / 'labels').mkdir(parents=True, exist_ok=True)
# #         (tmp / 'val'   / 'images').mkdir(parents=True, exist_ok=True)
# #         (tmp / 'val'   / 'labels').mkdir(parents=True, exist_ok=True)
# #
# #         for img in sampled:
# #             shutil.copy2(img, tmp / 'train' / 'images' / img.name)
# #             lbl = train_lbls / (img.stem + '.txt')
# #             if lbl.exists():
# #                 shutil.copy2(lbl, tmp / 'train' / 'labels' / lbl.name)
# #
# #         # 复制val集
# #         for img in (DATASET_ROOT / 'val' / 'images').glob('*.png'):
# #             shutil.copy2(img, tmp / 'val' / 'images' / img.name)
# #         for lbl in (DATASET_ROOT / 'val' / 'labels').glob('*.txt'):
# #             shutil.copy2(lbl, tmp / 'val' / 'labels' / lbl.name)
# #
# #         # 生成yaml
# #         tmp_yaml = tmp / 'dataset.yaml'
# #         tmp_yaml.write_text(yaml.dump({
# #             'path': str(tmp),
# #             'train': 'train/images',
# #             'val':   'val/images',
# #             'test':  str(DATASET_ROOT / 'test' / 'images'),
# #             'nc': 1, 'names': ['victim']
# #         }), encoding='utf-8')
# #
# #         # 训练
# #         model = YOLO('yolov8m.pt')
# #         model.train(
# #             data=str(tmp_yaml),
# #             epochs=60,
# #             imgsz=640,
# #             batch=8,
# #             device=0,
# #             project=str(BASE_DIR),
# #             name=f'ratio_{int(ratio*100)}',
# #             exist_ok=True,
# #             patience=15,
# #             workers=4,
# #             amp=True,
# #             verbose=False,
# #         )
# #
# #         # 在完整test集评估
# #         best = YOLO(BASE_DIR / f'ratio_{int(ratio*100)}' / 'weights' / 'best.pt')
# #         metrics = best.val(
# #             data=DATASET_YAML,
# #             split='test',
# #             device=0,
# #             batch=8,
# #             verbose=False,
# #             workers=0,
# #         )
# #
# #         results.append({
# #             'Ratio(%)':     int(ratio * 100),
# #             'N_train':      n,
# #             'mAP@0.5':      round(metrics.box.map50, 3),
# #             'mAP@0.5:0.95': round(metrics.box.map, 3),
# #             'Recall':       round(float(metrics.box.r.mean()), 3),
# #         })
# #         print(f"  mAP50={results[-1]['mAP@0.5']}")
# #
# #         shutil.rmtree(tmp)
# #
# #     df = pd.DataFrame(results)
# #     print("\n" + "="*55)
# #     print("Data Scaling结果")
# #     print("="*55)
# #     print(df.to_string(index=False))
# #     df.to_csv(r'D:/Fire_Project/data_scaling.csv',
# #               index=False, encoding='utf-8-sig')
# #     print("✅ 已保存: data_scaling.csv")
# from ultralytics import YOLO
# import pandas as pd
# import numpy as np
# import shutil
# import yaml
# import random
# from pathlib import Path
#
# DATASET_ROOT = Path('D:/Fire_Project/FireDataset_new2')
# BASE_DIR     = Path('D:/Fire_Project/runs/scaling_repeat')
# DATASET_YAML = r'D:/Fire_Project/FireDataset_new2/dataset.yaml'
#
# RATIOS   = [0.1, 0.25, 0.5, 0.75, 1.0]
# N_REPEAT = 3      # 每个ratio重复3次
# SEEDS    = [42, 123, 456]
#
# train_imgs = list((DATASET_ROOT / 'train' / 'images').glob('*.png'))
# train_lbls = DATASET_ROOT / 'train' / 'labels'
#
# all_results = []
#
# if __name__ == '__main__':
#     for ratio in RATIOS:
#         n = int(len(train_imgs) * ratio)
#         ratio_maps = []
#
#         for seed in SEEDS:
#             random.seed(seed)
#             sampled = random.sample(train_imgs, n)
#             run_name = f'ratio_{int(ratio*100)}_seed{seed}'
#             print(f"\n训练: {run_name} ({n}张)")
#
#             # 建临时目录
#             tmp = Path(f'D:/Fire_Project/scaling_tmp')
#             (tmp / 'train' / 'images').mkdir(parents=True, exist_ok=True)
#             (tmp / 'train' / 'labels').mkdir(parents=True, exist_ok=True)
#             (tmp / 'val'   / 'images').mkdir(parents=True, exist_ok=True)
#             (tmp / 'val'   / 'labels').mkdir(parents=True, exist_ok=True)
#
#             for img in sampled:
#                 shutil.copy2(img, tmp / 'train' / 'images' / img.name)
#                 lbl = train_lbls / (img.stem + '.txt')
#                 if lbl.exists():
#                     shutil.copy2(lbl, tmp / 'train' / 'labels' / lbl.name)
#
#             for img in (DATASET_ROOT / 'val' / 'images').glob('*.png'):
#                 shutil.copy2(img, tmp / 'val' / 'images' / img.name)
#             for lbl in (DATASET_ROOT / 'val' / 'labels').glob('*.txt'):
#                 shutil.copy2(lbl, tmp / 'val' / 'labels' / lbl.name)
#
#             tmp_yaml = tmp / 'dataset.yaml'
#             tmp_yaml.write_text(yaml.dump({
#                 'path': str(tmp),
#                 'train': 'train/images',
#                 'val':   'val/images',
#                 'test':  str(DATASET_ROOT / 'test' / 'images'),
#                 'nc': 1, 'names': ['victim']
#             }), encoding='utf-8')
#
#             model = YOLO('yolov8m.pt')
#             model.train(
#                 data=str(tmp_yaml),
#                 epochs=60,
#                 imgsz=640,
#                 batch=8,
#                 device=0,
#                 project=str(BASE_DIR),
#                 name=run_name,
#                 exist_ok=True,
#                 patience=15,
#                 workers=4,
#                 amp=True,
#                 verbose=False,
#                 seed=seed,
#             )
#
#             best = YOLO(BASE_DIR / run_name / 'weights' / 'best.pt')
#             metrics = best.val(
#                 data=DATASET_YAML,
#                 split='test',
#                 device=0,
#                 batch=8,
#                 verbose=False,
#                 workers=0,
#             )
#
#             map50 = round(metrics.box.map50, 4)
#             ratio_maps.append(map50)
#             print(f"  seed={seed}: mAP50={map50}")
#
#             all_results.append({
#                 'Ratio_pct': int(ratio * 100),
#                 'N_train':   n,
#                 'Seed':      seed,
#                 'mAP50':     map50,
#             })
#
#             shutil.rmtree(tmp)
#
#         mean = round(np.mean(ratio_maps), 4)
#         std  = round(np.std(ratio_maps), 4)
#         print(f"  均值={mean}, 标准差={std}")
#
#     # 保存原始数据
#     df_raw = pd.DataFrame(all_results)
#     df_raw.to_csv(r'D:/Fire_Project/scaling_raw.csv',
#                   index=False, encoding='utf-8-sig')
#
#     # 汇总均值和标准差
#     df_summary = df_raw.groupby(['Ratio_pct', 'N_train'])['mAP50'].agg(
#         mean='mean', std='std'
#     ).reset_index()
#     df_summary['mean'] = df_summary['mean'].round(4)
#     df_summary['std']  = df_summary['std'].round(4)
#
#     print("\n" + "="*50)
#     print("汇总结果（均值±标准差）")
#     print("="*50)
#     print(df_summary.to_string(index=False))
#
#     df_summary.to_csv(r'D:/Fire_Project/scaling_summary.csv',
#                       index=False, encoding='utf-8-sig')
#     print("✅ 已保存: scaling_summary.csv")
#
# from ultralytics import YOLO
# import pandas as pd
# import numpy as np
# import shutil
# import yaml
# import random
# from pathlib import Path
#
# DATASET_ROOT = Path('D:/Fire_Project/FireDataset_new2')
# BASE_DIR     = Path('D:/Fire_Project/runs/scaling_repeat')
# DATASET_YAML = r'D:/Fire_Project/FireDataset_new2/dataset.yaml'
# RAW_CSV      = Path('D:/Fire_Project/scaling_raw.csv')
#
# RATIOS = [0.1, 0.25, 0.5, 0.75, 1.0]
# SEEDS  = [42, 123, 456]
#
# train_imgs = list((DATASET_ROOT / 'train' / 'images').glob('*.png'))
# train_lbls = DATASET_ROOT / 'train' / 'labels'
#
# if __name__ == '__main__':
#
#     # ── 读取已有结果（断点续跑）────────────────────────
#     if RAW_CSV.exists():
#         df_existing = pd.read_csv(RAW_CSV)
#         all_results = df_existing.to_dict('records')
#         done_keys = set(
#             zip(df_existing['Ratio_pct'].astype(int),
#                 df_existing['Seed'].astype(int))
#         )
#         print(f"已有 {len(all_results)} 条记录，跳过已完成的组合")
#         print(f"已完成: {sorted(done_keys)}")
#     else:
#         all_results = []
#         done_keys   = set()
#
#     # ── 主循环 ──────────────────────────────────────
#     for ratio in RATIOS:
#         n = int(len(train_imgs) * ratio)
#
#         for seed in SEEDS:
#             key = (int(ratio * 100), seed)
#
#             # 已完成则跳过
#             if key in done_keys:
#                 print(f"跳过 ratio={int(ratio*100)}% seed={seed}（已完成）")
#                 continue
#
#             run_name = f'ratio_{int(ratio*100)}_seed{seed}'
#             print(f"\n{'='*50}")
#             print(f"训练: {run_name} ({n}张)")
#
#             # 检查weights是否已存在（训练完但评估中断）
#             best_pt = BASE_DIR / run_name / 'weights' / 'best.pt'
#
#             if not best_pt.exists():
#                 # 需要重新训练
#                 random.seed(seed)
#                 sampled = random.sample(train_imgs, n)
#
#                 tmp = Path('D:/Fire_Project/scaling_tmp')
#                 # 清空并重建临时目录
#                 if tmp.exists():
#                     shutil.rmtree(tmp)
#                 (tmp / 'train' / 'images').mkdir(parents=True)
#                 (tmp / 'train' / 'labels').mkdir(parents=True)
#                 (tmp / 'val'   / 'images').mkdir(parents=True)
#                 (tmp / 'val'   / 'labels').mkdir(parents=True)
#
#                 for img in sampled:
#                     shutil.copy2(img, tmp / 'train' / 'images' / img.name)
#                     lbl = train_lbls / (img.stem + '.txt')
#                     if lbl.exists():
#                         shutil.copy2(lbl, tmp / 'train' / 'labels' / lbl.name)
#
#                 for img in (DATASET_ROOT / 'val' / 'images').glob('*.png'):
#                     shutil.copy2(img, tmp / 'val' / 'images' / img.name)
#                 for lbl in (DATASET_ROOT / 'val' / 'labels').glob('*.txt'):
#                     shutil.copy2(lbl, tmp / 'val' / 'labels' / lbl.name)
#
#                 tmp_yaml = tmp / 'dataset.yaml'
#                 tmp_yaml.write_text(yaml.dump({
#                     'path':  str(tmp),
#                     'train': 'train/images',
#                     'val':   'val/images',
#                     'test':  str(DATASET_ROOT / 'test' / 'images'),
#                     'nc': 1, 'names': ['victim']
#                 }), encoding='utf-8')
#
#                 model = YOLO('yolov8m.pt')
#                 model.train(
#                     data=str(tmp_yaml),
#                     epochs=60,
#                     imgsz=640,
#                     batch=8,
#                     device=0,
#                     project=str(BASE_DIR),
#                     name=run_name,
#                     exist_ok=True,
#                     patience=15,
#                     workers=4,
#                     amp=True,
#                     verbose=False,
#                     seed=seed,
#                 )
#
#                 if tmp.exists():
#                     shutil.rmtree(tmp)
#             else:
#                 print(f"  weights已存在，直接评估")
#
#             # 评估
#             print(f"  评估中...")
#             best_model = YOLO(best_pt)
#             metrics = best_model.val(
#                 data=DATASET_YAML,
#                 split='test',
#                 device=0,
#                 batch=8,
#                 verbose=False,
#                 workers=0,
#             )
#
#             map50 = round(float(metrics.box.map50), 4)
#             print(f"  ✅ ratio={int(ratio*100)}% seed={seed}: mAP50={map50}")
#
#             all_results.append({
#                 'Ratio_pct': int(ratio * 100),
#                 'N_train':   n,
#                 'Seed':      seed,
#                 'mAP50':     map50,
#             })
#
#             # 每完成一个就保存一次，防止再次中断丢失
#             pd.DataFrame(all_results).to_csv(
#                 RAW_CSV, index=False, encoding='utf-8-sig')
#
#     # ── 汇总结果 ────────────────────────────────────
#     df_raw = pd.DataFrame(all_results)
#
#     df_summary = df_raw.groupby(
#         ['Ratio_pct', 'N_train'])['mAP50'].agg(
#         mean='mean', std='std'
#     ).reset_index()
#     df_summary['mean'] = df_summary['mean'].round(4)
#     df_summary['std']  = df_summary['std'].round(4)
#
#     print("\n" + "="*55)
#     print("汇总结果（均值 ± 标准差）")
#     print("="*55)
#     print(df_summary.to_string(index=False))
#
#     df_summary.to_csv(r'D:/Fire_Project/scaling_summary.csv',
#                       index=False, encoding='utf-8-sig')
#     print("\n✅ scaling_raw.csv     → 每次训练的原始结果")
#     print("✅ scaling_summary.csv → 均值和标准差（Origin导入用）")