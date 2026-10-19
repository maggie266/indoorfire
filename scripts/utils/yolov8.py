# # from ultralytics import YOLO
# # import pandas as pd
# # import torch
# # import time
# #
# # MODELS = [
# #     # ('yolov8n', 16),
# #     ('yolov8s', 16),
# #     # ('yolov8m', 8),
# #     # ('yolov8l', 4),
# #     # ('yolov8x', 4),
# # ]
# #
# # DATASET = 'D:\Fire_Project\FireDataset_new\dataset.yaml'
# # EPOCHS = 100
# # IMGSZ = 640
# #
# # if __name__ == '__main__':
# #     results_log = []
# #
# #     for model_name, batch in MODELS:
# #         print(f"\n{'='*50}")
# #         print(f"训练中: {model_name}  batch={batch}")
# #         print(f"{'='*50}")
# #
# #         model = YOLO(f'{model_name}.pt')
# #
# #         model.train(
# #             data=DATASET,
# #             epochs=EPOCHS,
# #             imgsz=IMGSZ,
# #             batch=batch,
# #             device=0,
# #             project='runs/baseline',
# #             name=model_name,
# #             exist_ok=True,
# #             patience=20,
# #             save_period=10,
# #             workers=4,
# #             cache=False,
# #             amp=True,
# #         )
# #
# #         best_model = YOLO(f'runs/baseline/{model_name}/weights/best.pt')
# #         metrics = best_model.val(
# #             data=DATASET,
# #             split='test',
# #             device=0,
# #             batch=batch,
# #         )
# #
# #         # FPS测试
# #         dummy = torch.randn(1, 3, IMGSZ, IMGSZ).cuda()
# #         best_model.model.cuda().eval()
# #         with torch.no_grad():
# #             for _ in range(10):
# #                 best_model.model(dummy)
# #             t0 = time.perf_counter()
# #             for _ in range(200):
# #                 best_model.model(dummy)
# #             torch.cuda.synchronize()
# #         fps = round(200 / (time.perf_counter() - t0), 1)
# #
# #         params = round(
# #             sum(p.numel() for p in best_model.model.parameters()) / 1e6, 1
# #         )
# #
# #         results_log.append({
# #             'Model':      model_name,
# #             'mAP@0.5':    round(metrics.box.map50, 3),
# #             'mAP@0.5:95': round(metrics.box.map, 3),
# #             'Precision':  round(float(metrics.box.p.mean()), 3),
# #             'Recall':     round(float(metrics.box.r.mean()), 3),
# #             'FPS':        fps,
# #             'Params(M)':  params,
# #         })
# #
# #         print(f"\n{model_name} 完成: mAP50={results_log[-1]['mAP@0.5']}")
# #
# #     df = pd.DataFrame(results_log)
# #     print("\n" + "="*60)
# #     print("基准性能实验结果")
# #     print("="*60)
# #     print(df.to_string(index=False))
# #     df.to_csv('runs/baseline/baseline_results.csv', index=False)
# #     print("\n结果已保存至 runs/baseline/baseline_results.csv")
# #
# # from ultralytics import YOLO
# # import pandas as pd
# # import torch
# # import time
# #
# # MODELS = [
# #     # ('yolov8n', 16),  # 已完成
# #     # ('yolov8s', 16),  # 已完成
# #     ('yolov8m', 8),
# #     # ('yolov8l', 4),
# #     # ('yolov8x', 4),
# # ]
# #
# # DATASET  = r'D:\Fire_Project\FireDataset_new2\dataset.yaml'
# # EPOCHS   = 100
# # IMGSZ    = 640
# # BASE_DIR = r'D:\Fire_Project\scripts\runs\detect\runs\baseline3'  # 实际保存路径
# #
# # if __name__ == '__main__':
# #     results_log = []
# #
# #     for model_name, batch in MODELS:
# #         print(f"\n{'='*50}\n训练中: {model_name}\n{'='*50}")
# #
# #         model = YOLO(f'{model_name}.pt')
# #         model.train(
# #             data=DATASET,
# #             epochs=EPOCHS,
# #             imgsz=IMGSZ,
# #             batch=batch,
# #             device=0,
# #             project=BASE_DIR,
# #             name=model_name,
# #             exist_ok=True,
# #             patience=20,
# #             workers=4,
# #             amp=True,
# #         )
# #
# #         # 用绝对路径加载
# #         best_pt = rf'{BASE_DIR}\{model_name}\weights\best.pt'
# #         best_model = YOLO(best_pt)
# #
# #         metrics = best_model.val(
# #             data=DATASET,
# #             split='test',
# #             device=0,
# #             batch=batch,
# #         )
# #
# #         # FPS
# #         dummy = torch.randn(1, 3, IMGSZ, IMGSZ).cuda()
# #         best_model.model.cuda().eval()
# #         with torch.no_grad():
# #             for _ in range(10):
# #                 best_model.model(dummy)
# #             t0 = time.perf_counter()
# #             for _ in range(200):
# #                 best_model.model(dummy)
# #             torch.cuda.synchronize()
# #         fps = round(200 / (time.perf_counter() - t0), 1)
# #
# #         params = round(
# #             sum(p.numel() for p in best_model.model.parameters()) / 1e6, 1
# #         )
# #
# #         results_log.append({
# #             'Model':      model_name,
# #             'mAP@0.5':    round(metrics.box.map50, 3),
# #             'mAP@0.5:95': round(metrics.box.map, 3),
# #             'Precision':  round(float(metrics.box.p.mean()), 3),
# #             'Recall':     round(float(metrics.box.r.mean()), 3),
# #             'FPS':        fps,
# #             'Params(M)':  params,
# #         })
# #         print(f"{model_name} 完成: {results_log[-1]}")
# #
# #     # 汇总已完成的结果（包括n和s）
# #     completed = [
# #         # {'Model': 'yolov8n', 'mAP@0.5': 0.989, 'mAP@0.5:95': 0.866,
# #         #  'Precision': 0.990, 'Recall': 0.972, 'FPS': None, 'Params(M)': 3.2},
# #         # {'Model': 'yolov8s', 'mAP@0.5': 0.993, 'mAP@0.5:95': 0.904,
# #         #  'Precision': 0.992, 'Recall': 0.979, 'FPS': None, 'Params(M)': 11.2},
# #         # {'Model': 'yolov8m', 'mAP@0.5': 0.994, 'mAP@0.5:95': 0.930,
# #         #  'Precision': 0.988, 'Recall':  0.985, 'FPS': 43.2, 'Params(M)': 25.8},
# #     ]
# #
# #     all_results = completed + results_log
# #     df = pd.DataFrame(all_results)
# #     print("\n=== 当前基准实验结果 ===")
# #     print(df.to_string(index=False))
# #     df.to_csv(rf'{BASE_DIR}\baseline_results.csv', index=False)
# #     print(f"\n结果已保存")
# #
# from ultralytics import YOLO
# import pandas as pd
# import numpy as np
# import torch
# import time
# from pathlib import Path
#
# MODELS = [
#     ('yolov8m', 8),
# ]
#
# DATASET  = r'D:\Fire_Project\FireDataset_new2\dataset.yaml'
# EPOCHS   = 100
# IMGSZ    = 640
# BASE_DIR = r'D:\Fire_Project\scripts\runs\detect\runs\baseline4'
# PR_SAVE  = r'D:\Fire_Project\PR_curve_data.csv'
#
# def extract_pr_data(metrics, save_path):
#     """从val结果提取PR曲线原始数据并保存"""
#     try:
#         # 获取curves_results
#         cr = metrics.box.curves_results
#         curve_names = metrics.box.curves
#         print(f"  可用曲线: {curve_names}")
#
#         # 遍历找PR曲线
#         for i, name in enumerate(curve_names):
#             if 'pr' in name.lower() or 'precision-recall' in name.lower():
#                 x = np.array(cr[i][0])  # recall
#                 y = np.array(cr[i][1])  # precision
#                 if y.ndim == 2:
#                     y = y[0]
#                 df = pd.DataFrame({
#                     'recall':    np.round(x, 4),
#                     'precision': np.round(y, 4),
#                 })
#                 df.to_csv(save_path, index=False, encoding='utf-8-sig')
#                 print(f"  ✅ PR曲线已保存（方式一）: {save_path}")
#                 print(f"     数据点数: {len(df)}")
#                 return True
#
#         # 如果没找到PR曲线，尝试用P和R曲线合并
#         p_data, r_data = None, None
#         for i, name in enumerate(curve_names):
#             if name.lower() == 'precision':
#                 p_data = np.array(cr[i][1])
#                 x_axis = np.array(cr[i][0])
#             if name.lower() == 'recall':
#                 r_data = np.array(cr[i][1])
#
#         if p_data is not None and r_data is not None:
#             if p_data.ndim == 2:
#                 p_data = p_data[0]
#             if r_data.ndim == 2:
#                 r_data = r_data[0]
#             df = pd.DataFrame({
#                 'confidence': np.round(x_axis, 4),
#                 'precision':  np.round(p_data, 4),
#                 'recall':     np.round(r_data, 4),
#             })
#             df.to_csv(save_path, index=False, encoding='utf-8-sig')
#             print(f"  ✅ P-R数据已保存（方式二）: {save_path}")
#             return True
#
#         print("  ⚠️ 未找到PR曲线数据，请手动从PNG提取")
#         return False
#
#     except Exception as e:
#         print(f"  ⚠️ PR提取失败: {e}")
#         return False
#
#
# if __name__ == '__main__':
#     results_log = []
#
#     for model_name, batch in MODELS:
#         print(f"\n{'='*50}\n训练中: {model_name}\n{'='*50}")
#
#         model = YOLO(f'{model_name}.pt')
#         model.train(
#             data=DATASET,
#             epochs=EPOCHS,
#             imgsz=IMGSZ,
#             batch=batch,
#             device=0,
#             project=BASE_DIR,
#             name=model_name,
#             exist_ok=True,
#             patience=20,
#             workers=4,
#             amp=True,
#         )
#
#         best_pt = rf'{BASE_DIR}\{model_name}\weights\best.pt'
#         best_model = YOLO(best_pt)
#
#         # ── 评估并提取PR数据 ──────────────────────────
#         print(f"\n评估 {model_name} 并提取PR曲线...")
#         metrics = best_model.val(
#             data=DATASET,
#             split='test',
#             device=0,
#             batch=batch,
#             plots=True,   # 确保生成曲线图
#             verbose=False,
#             workers=0,    # 避免Windows multiprocessing问题
#         )
#
#         # 提取PR原始数据
#         extract_pr_data(metrics, PR_SAVE)
#
#         # ── FPS测量 ───────────────────────────────────
#         dummy = torch.randn(1, 3, IMGSZ, IMGSZ).cuda()
#         best_model.model.cuda().eval()
#         with torch.no_grad():
#             for _ in range(10):
#                 best_model.model(dummy)
#             torch.cuda.synchronize()
#             t0 = time.perf_counter()
#             for _ in range(200):
#                 best_model.model(dummy)
#             torch.cuda.synchronize()
#         fps = round(200 / (time.perf_counter() - t0), 1)
#
#         params = round(
#             sum(p.numel() for p in best_model.model.parameters()) / 1e6, 1
#         )
#
#         results_log.append({
#             'Model':      model_name,
#             'mAP@0.5':    round(metrics.box.map50, 3),
#             'mAP@0.5:95': round(metrics.box.map, 3),
#             'Precision':  round(float(metrics.box.p.mean()), 3),
#             'Recall':     round(float(metrics.box.r.mean()), 3),
#             'FPS':        fps,
#             'Params(M)':  params,
#         })
#         print(f"\n{model_name} 完成: {results_log[-1]}")
#
#     df = pd.DataFrame(results_log)
#     print("\n=== 当前基准实验结果 ===")
#     print(df.to_string(index=False))
#     df.to_csv(rf'{BASE_DIR}\baseline_results.csv', index=False)
#     print("结果已保存")
import numpy as np
import pandas as pd

df = pd.read_csv(r'D:/Fire_Project/PR_curve_data.csv')

recall    = df['recall'].values
precision = df['precision'].values

# ── YOLOv8内部绘图逻辑：从右到左取precision的累积最大值 ──
# 这就是为什么图1的曲线在高recall区域precision能保持平稳
precision_envelope = np.maximum.accumulate(precision[::-1])[::-1]

# ── 降采样到200点，去掉末尾precision=0的冗余点 ──────────
# 找到precision开始持续为0的位置
nonzero_mask = precision_envelope > 0.001
last_nonzero = np.where(nonzero_mask)[0][-1]

recall_clean    = recall[:last_nonzero + 2]
precision_clean = precision_envelope[:last_nonzero + 2]

# 每隔几个点取一个，保留200点
step = max(1, len(recall_clean) // 200)
recall_sampled    = recall_clean[::step]
precision_sampled = precision_clean[::step]

# 确保末尾有(1.0, 0.0)这个点
if recall_sampled[-1] < 1.0:
    recall_sampled    = np.append(recall_sampled, 1.0)
    precision_sampled = np.append(precision_sampled, 0.0)

df_out = pd.DataFrame({
    'recall':    np.round(recall_sampled, 4),
    'precision': np.round(precision_sampled, 4),
})

print(f"处理后数据点数: {len(df_out)}")
print("\n前10行:")
print(df_out.head(10).to_string(index=False))
print("\n后5行:")
print(df_out.tail(5).to_string(index=False))

# 验证形状：recall从小到大，precision应该先高后低
print(f"\n验证:")
print(f"  recall范围: {df_out['recall'].min():.3f} ~ {df_out['recall'].max():.3f}")
print(f"  precision起点: {df_out['precision'].iloc[0]:.3f}")
print(f"  precision末点: {df_out['precision'].iloc[-1]:.3f}")

df_out.to_csv(r'D:/Fire_Project/PR_curve_origin.csv',
              index=False, encoding='utf-8-sig')
print("\n✅ 已保存: PR_curve_origin.csv")