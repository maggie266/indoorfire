# # # import pandas as pd
# # # from pathlib import Path
# # #
# # # # YOLOv8m的训练结果
# # # RUNS_DIR = Path(r'D:/Fire_Project/scripts/runs/detect/runs/baseline3/yolov8m')
# # # csv_path = RUNS_DIR / 'results.csv'
# # #
# # # df = pd.read_csv(csv_path)
# # #
# # # # 清理列名（YOLOv8生成的列名有空格）
# # # df.columns = df.columns.str.strip()
# # # print("所有列名：")
# # # print(df.columns.tolist())
# # #
# # # # 提取需要的列
# # # out = pd.DataFrame({
# # #     'epoch':              df['epoch'],
# # #     'train_box_loss':     df['train/box_loss'],
# # #     'train_cls_loss':     df['train/cls_loss'],
# # #     'val_box_loss':       df['val/box_loss'],
# # #     'val_cls_loss':       df['val/cls_loss'],
# # #     'mAP50':              df['metrics/mAP50(B)'],
# # #     'mAP50_95':           df['metrics/mAP50-95(B)'],
# # #     'precision':          df['metrics/precision(B)'],
# # #     'recall':             df['metrics/recall(B)'],
# # # })
# # #
# # # save_path = r'D:/Fire_Project/training_curves_yolov8m.csv'
# # # out.to_csv(save_path, index=False, encoding='utf-8-sig')
# # # print(f"\n✅ 训练曲线数据已保存: {save_path}")
# # # print(f"共 {len(out)} 个epoch")
# # # print(out.tail(3).to_string())
# # # 备用方案：直接用runs目录下已生成的PR_curve.png
# # # Origin可以直接导入图片描图，或用以下方式从图像读取近似数据
# #
# # import cv2
# # import numpy as np
# # import pandas as pd
# #
# # PR_IMG = r'D:/Fire_Project/scripts/runs/detect/runs/baseline3/yolov8m/BoxPR_curve.png'
# #
# # img = cv2.imread(PR_IMG)
# # img_rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
# #
# # r = img_rgb[:, :, 0].astype(int)
# # g = img_rgb[:, :, 1].astype(int)
# # b = img_rgb[:, :, 2].astype(int)
# #
# # # 蓝色曲线掩膜
# # curve_mask = (b > 150) & (r < 80) & (g < 80)
# #
# # # ── 根据调试结果设定绘图区域 ──────────────────────
# # # 图像2250x1500，曲线像素范围 col:178~1634, row:99~1347
# # # 坐标轴边界比曲线略宽，根据图像比例估算
# # plot_left   = 178    # recall = 0.0
# # plot_right  = 1634   # recall = 1.0
# # plot_top    = 99     # precision = 1.0
# # plot_bottom = 1347   # precision = 0.0
# #
# # # ── 逐列提取曲线最高点 ────────────────────────────
# # data_points = []
# #
# # for col in range(plot_left, plot_right + 1):
# #     col_mask = curve_mask[:, col]
# #     curve_rows = np.where(col_mask)[0]
# #     curve_rows = curve_rows[
# #         (curve_rows >= plot_top) & (curve_rows <= plot_bottom)
# #     ]
# #     if len(curve_rows) == 0:
# #         continue
# #
# #     row = curve_rows.min()  # 最上方像素 = 最高precision
# #
# #     recall    = (col - plot_left) / (plot_right - plot_left)
# #     precision = 1.0 - (row - plot_top) / (plot_bottom - plot_top)
# #
# #     data_points.append({
# #         'recall':    round(float(recall), 4),
# #         'precision': round(float(np.clip(precision, 0, 1)), 4),
# #     })
# #
# # df = pd.DataFrame(data_points)
# # df = df.sort_values('recall').drop_duplicates(subset='recall')
# # df = df[(df['recall'] >= 0) & (df['recall'] <= 1) &
# #         (df['precision'] >= 0) & (df['precision'] <= 1)]
# #
# # # ── 降采样到100个点（Origin画图够用）────────────────
# # df_sampled = df.iloc[::max(1, len(df)//100)].reset_index(drop=True)
# #
# # print(f"提取到 {len(df)} 个原始点，降采样到 {len(df_sampled)} 个点")
# # print("\n前10个数据点:")
# # print(df_sampled.head(10).to_string(index=False))
# # print("\n最后5个数据点:")
# # print(df_sampled.tail(5).to_string(index=False))
# #
# # # 验证：recall=0时precision应接近1.0
# # first = df_sampled.iloc[0]
# # print(f"\n验证: recall={first['recall']}, precision={first['precision']}")
# # print("期望: recall≈0, precision≈1.0")
# #
# # # 保存完整数据和降采样数据
# # df.to_csv(r'D:/Fire_Project/PR_curve_full.csv',
# #           index=False, encoding='utf-8-sig')
# # df_sampled.to_csv(r'D:/Fire_Project/PR_curve_sampled.csv',
# #                   index=False, encoding='utf-8-sig')
# # print("\n✅ 已保存:")
# # print("  完整数据: PR_curve_full.csv")
# # print("  降采样:   PR_curve_sampled.csv（Origin导入用这个）")
#
# import numpy as np
# import pandas as pd
# from pathlib import Path
#
# DATASET_ROOT = Path('D:/Fire_Project/FireDataset_new')
# SPLITS = ['train', 'val', 'test']
# SAVE_DIR = Path('D:/Fire_Project/annotation_analysis/origin_data')
# SAVE_DIR.mkdir(parents=True, exist_ok=True)
#
# # ── 收集所有数据 ──────────────────────────────────────
# all_data = {}
# for split in SPLITS:
#     lbl_dir = DATASET_ROOT / split / 'labels'
#     areas, aspects, instances_per_img = [], [], []
#
#     for lbl_file in lbl_dir.glob('*.txt'):
#         lines = lbl_file.read_text().strip().splitlines()
#         count = 0
#         for line in lines:
#             parts = line.strip().split()
#             if len(parts) != 5:
#                 continue
#             _, cx, cy, bw, bh = map(float, parts)
#             areas.append(bw * bh * 100)
#             aspects.append(bw / bh if bh > 0 else 0)
#             count += 1
#         instances_per_img.append(count)
#
#     all_data[split] = {
#         'areas':     np.array(areas),
#         'aspects':   np.array(aspects),
#         'instances': np.array(instances_per_img),
#     }
#
# # ══════════════════════════════════════════════════════
# # 图1：bbox面积分布直方图原始数据
# # Origin：三列分别对应train/val/test，每列是面积值
# # 导入后：Plot → Statistics → Histogram，三列叠加对比
# # ══════════════════════════════════════════════════════
# print("生成图1数据（bbox面积分布）...")
#
# # 截断到5%以内，与Python图保持一致
# for split in SPLITS:
#     areas = all_data[split]['areas']
#     clipped = areas[areas <= 5]
#     pd.DataFrame({
#         f'area_pct_{split}': clipped
#     }).to_csv(SAVE_DIR / f'fig1_bbox_area_{split}.csv',
#               index=False, encoding='utf-8-sig')
#
# # 合并为一个文件（三列长度不同，用NaN填充）
# max_len = max(len(all_data[s]['areas'][all_data[s]['areas'] <= 5])
#               for s in SPLITS)
# fig1_df = pd.DataFrame()
# for split in SPLITS:
#     areas = all_data[split]['areas']
#     clipped = areas[areas <= 5]
#     col = np.full(max_len, np.nan)
#     col[:len(clipped)] = clipped
#     fig1_df[f'area_pct_{split}'] = col
#
#     # 同时输出统计量供Origin标注参考线
#     median = np.median(areas)
#     small_ratio = (areas < 1.0).mean() * 100
#     print(f"  {split}: median={median:.4f}%, small_ratio={small_ratio:.1f}%")
#
# fig1_df.to_csv(SAVE_DIR / 'fig1_bbox_area_all.csv',
#                index=False, encoding='utf-8-sig')
#
# # 输出参考线数据（中位数和1%阈值）
# ref_df = pd.DataFrame({
#     'split':       SPLITS,
#     'median_pct':  [round(np.median(all_data[s]['areas']), 4) for s in SPLITS],
#     'small_ratio': [round((all_data[s]['areas'] < 1.0).mean() * 100, 1)
#                     for s in SPLITS],
#     'threshold':   [1.0, 1.0, 1.0],
# })
# ref_df.to_csv(SAVE_DIR / 'fig1_reference_lines.csv',
#               index=False, encoding='utf-8-sig')
# print("✅ 图1数据保存完成\n")
#
# # ══════════════════════════════════════════════════════
# # 图2：宽高比分布直方图原始数据
# # Origin：三列分别对应train/val/test
# # 导入后：Plot → Statistics → Histogram，三列叠加对比
# # ══════════════════════════════════════════════════════
# print("生成图2数据（宽高比分布）...")
#
# max_len2 = max(
#     len(all_data[s]['aspects'][
#         (all_data[s]['aspects'] > 0) & (all_data[s]['aspects'] < 3)
#     ]) for s in SPLITS
# )
# fig2_df = pd.DataFrame()
# for split in SPLITS:
#     asp = all_data[split]['aspects']
#     asp = asp[(asp > 0) & (asp < 3)]
#     col = np.full(max_len2, np.nan)
#     col[:len(asp)] = asp
#     fig2_df[f'aspect_ratio_{split}'] = col
#     print(f"  {split}: mean={asp.mean():.4f}, "
#           f"median={np.median(asp):.4f}, n={len(asp)}")
#
# fig2_df.to_csv(SAVE_DIR / 'fig2_aspect_ratio_all.csv',
#                index=False, encoding='utf-8-sig')
# print("✅ 图2数据保存完成\n")
#
# # ══════════════════════════════════════════════════════
# # 图3：每图实例数分布直方图原始数据
# # Origin：三列分别对应train/val/test
# # 导入后：Plot → Statistics → Histogram，bins设为整数
# # ══════════════════════════════════════════════════════
# print("生成图3数据（每图实例数）...")
#
# max_len3 = max(len(all_data[s]['instances']) for s in SPLITS)
# fig3_df = pd.DataFrame()
# for split in SPLITS:
#     inst = all_data[split]['instances']
#     col = np.full(max_len3, np.nan)
#     col[:len(inst)] = inst
#     fig3_df[f'instances_{split}'] = col
#     print(f"  {split}: mean={inst.mean():.2f}, "
#           f"max={inst.max()}, n={len(inst)}")
#
# fig3_df.to_csv(SAVE_DIR / 'fig3_instances_per_image.csv',
#                index=False, encoding='utf-8-sig')
#
# # 额外输出频次统计表（Origin可直接用柱状图）
# print("\n  频次统计表:")
# for split in SPLITS:
#     inst = all_data[split]['instances'].astype(int)
#     counts = pd.Series(inst).value_counts().sort_index()
#     freq_df = pd.DataFrame({
#         'instances': counts.index,
#         f'count_{split}': counts.values
#     })
#     freq_df.to_csv(SAVE_DIR / f'fig3_frequency_{split}.csv',
#                    index=False, encoding='utf-8-sig')
#
# # 合并频次表
# all_vals = sorted(set(
#     int(v) for s in SPLITS
#     for v in all_data[s]['instances']
# ))
# freq_all = pd.DataFrame({'instances': all_vals})
# for split in SPLITS:
#     inst = all_data[split]['instances'].astype(int)
#     counts = pd.Series(inst).value_counts()
#     freq_all[f'count_{split}'] = freq_all['instances'].map(counts).fillna(0).astype(int)
#
# freq_all.to_csv(SAVE_DIR / 'fig3_frequency_all.csv',
#                 index=False, encoding='utf-8-sig')
# print("✅ 图3数据保存完成\n")
#
# # ══════════════════════════════════════════════════════
# # 图4：小目标vs正常目标饼图原始数据
# # Origin：直接用数值绘制饼图
# # ══════════════════════════════════════════════════════
# print("生成图4数据（小目标比例）...")
#
# fig4_rows = []
# for split in SPLITS:
#     areas = all_data[split]['areas']
#     small  = int((areas < 1.0).sum())
#     normal = int((areas >= 1.0).sum())
#     total  = len(areas)
#     fig4_rows.append({
#         'split':        split,
#         'small_count':  small,
#         'normal_count': normal,
#         'total':        total,
#         'small_pct':    round(small / total * 100, 1),
#         'normal_pct':   round(normal / total * 100, 1),
#     })
#     print(f"  {split}: small={small}({small/total*100:.1f}%), "
#           f"normal={normal}({normal/total*100:.1f}%)")
#
# fig4_df = pd.DataFrame(fig4_rows)
# fig4_df.to_csv(SAVE_DIR / 'fig4_small_target_ratio.csv',
#                index=False, encoding='utf-8-sig')
# print("✅ 图4数据保存完成\n")
#
# # ══════════════════════════════════════════════════════
# # 汇总统计表
# # ══════════════════════════════════════════════════════
# print("生成汇总统计表...")
# summary_rows = []
# for split in SPLITS:
#     d = all_data[split]
#     summary_rows.append({
#         'Split':               split,
#         'Total_instances':     len(d['areas']),
#         'Avg_instances_image': round(d['instances'].mean(), 2),
#         'Median_BBox_area_pct':round(float(np.median(d['areas'])), 4),
#         'P10_BBox_area_pct':   round(float(np.percentile(d['areas'], 10)), 4),
#         'P90_BBox_area_pct':   round(float(np.percentile(d['areas'], 90)), 4),
#         'Small_target_ratio_pct': round(float((d['areas'] < 1.0).mean() * 100), 1),
#         'Mean_aspect_ratio':   round(float(d['aspects'].mean()), 4),
#     })
#
# summary_df = pd.DataFrame(summary_rows)
# summary_df.to_csv(SAVE_DIR / 'summary_statistics.csv',
#                   index=False, encoding='utf-8-sig')
#
# print("\n" + "=" * 65)
# print(summary_df.to_string(index=False))
# print(f"\n✅ 所有原始数据已保存至: {SAVE_DIR}")
# print("\n各文件说明:")
# print("  fig1_bbox_area_all.csv     → 图1：bbox面积分布（Origin Histogram）")
# print("  fig1_reference_lines.csv   → 图1：中位数和阈值参考线数据")
# print("  fig2_aspect_ratio_all.csv  → 图2：宽高比分布（Origin Histogram）")
# print("  fig3_frequency_all.csv     → 图3：每图实例数频次（Origin Bar Chart）")
# print("  fig4_small_target_ratio.csv→ 图4：小目标比例（Origin Pie Chart）")
# print("  summary_statistics.csv     → 汇总统计表（论文直接引用）")

# import numpy as np
# import pandas as pd
# from pathlib import Path
#
# DATASET_ROOT = Path('D:/Fire_Project/FireDataset_new2')
# SPLITS = ['train', 'val', 'test']
# SAVE_DIR = Path('D:/Fire_Project/annotation_analysis/origin_data')
# SAVE_DIR.mkdir(parents=True, exist_ok=True)
#
# # 收集面积数据
# all_areas = {}
# for split in SPLITS:
#     lbl_dir = DATASET_ROOT / split / 'labels'
#     areas = []
#     for lbl_file in lbl_dir.glob('*.txt'):
#         for line in lbl_file.read_text().strip().splitlines():
#             parts = line.strip().split()
#             if len(parts) != 5:
#                 continue
#             _, cx, cy, bw, bh = map(float, parts)
#             areas.append(bw * bh * 100)
#     all_areas[split] = np.array(areas)
#
# # ── 计算频次表（50个bin，范围0~5）────────────────────
# bin_edges = np.linspace(0, 5, 51)          # 50个bin
# bin_centers = (bin_edges[:-1] + bin_edges[1:]) / 2  # 每个bin的中心值
#
# freq_df = pd.DataFrame({'bin_center': np.round(bin_centers, 3)})
#
# for split in SPLITS:
#     areas = all_areas[split]
#     clipped = areas[areas <= 5]
#     counts, _ = np.histogram(clipped, bins=bin_edges)
#     freq_df[f'count_{split}'] = counts
#
#     median = np.median(areas)
#     small_ratio = (areas < 1.0).mean() * 100
#     print(f"{split}: median={median:.4f}%, small_ratio={small_ratio:.1f}%,"
#           f" total_instances={len(areas)}")
#
# freq_df.to_csv(SAVE_DIR / 'fig1_histogram_counts.csv',
#                index=False, encoding='utf-8-sig')
#
# print(f"\n✅ 频次表已保存: fig1_histogram_counts.csv")
# print(f"共 {len(freq_df)} 行，每行对应一个bin")
# print(f"\n前5行预览:")
# print(freq_df.head().to_string(index=False))
# print(f"\n说明:")
# print(f"  bin_center: X轴坐标（bbox面积%），间隔0.1")
# print(f"  count_train/val/test: 对应Y轴计数")
import numpy as np
import pandas as pd
from pathlib import Path

DATASET_ROOT = Path('D:/Fire_Project/FireDataset_new2')
SAVE_DIR = Path('D:/Fire_Project/annotation_analysis3')
SAVE_DIR.mkdir(exist_ok=True)

# 只提取train集的cx/cy（左下图对应train集）
cx_list, cy_list = [], []

lbl_dir = DATASET_ROOT / 'train' / 'labels'
for lbl_file in lbl_dir.glob('*.txt'):
    for line in lbl_file.read_text().strip().splitlines():
        parts = line.strip().split()
        if len(parts) != 5:
            continue
        _, cx, cy, bw, bh = map(float, parts)
        cx_list.append(round(cx, 4))
        cy_list.append(round(cy, 4))

df = pd.DataFrame({'cx': cx_list, 'cy': cy_list})
save_path = SAVE_DIR / 'bbox_center_train.csv'
df.to_csv(save_path, index=False, encoding='utf-8-sig')

print(f"✅ 中心点数据已保存: {save_path}")
print(f"共 {len(df)} 个数据点")
print(f"cx范围: {df['cx'].min():.3f} ~ {df['cx'].max():.3f}")
print(f"cy范围: {df['cy'].min():.3f} ~ {df['cy'].max():.3f}")