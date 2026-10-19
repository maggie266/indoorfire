# from ultralytics import YOLO
# import pandas as pd
# import torch
# import time
#
# DATASET  = r'D:\Fire_Project\FireDataset_new2\dataset.yaml'
# IMGSZ    = 640
# BASE_DIR = r'D:\Fire_Project\scripts\runs\detect\runs\baseline3'
#
# # 要测试的模型列表，按需增减
# MODELS = [
#     ('yolov8n', 16),
#     ('yolov8s', 16),
#     ('yolov8m', 8),
#     # ('yolov8l', 4),
#     # ('yolov8x', 4),
# ]
#
# if __name__ == '__main__':
#     results_log = []
#
#     for model_name, batch in MODELS:
#         print(f"\n{'='*50}\n测试中: {model_name}\n{'='*50}")
#
#         best_pt = rf'{BASE_DIR}\{model_name}\weights\best.pt'
#         model = YOLO(best_pt)
#
#         # 测试集评估
#         metrics = model.val(
#             data=DATASET,
#             split='test',
#             device=0,
#             batch=batch,
#             imgsz=IMGSZ,
#             verbose=True,
#         )
#
#         # FPS 测试（GPU warmup + 200次平均）
#         dummy = torch.randn(1, 3, IMGSZ, IMGSZ).cuda()
#         model.model.cuda().eval()
#         with torch.no_grad():
#             for _ in range(10):
#                 model.model(dummy)
#             t0 = time.perf_counter()
#             for _ in range(200):
#                 model.model(dummy)
#             torch.cuda.synchronize()
#         fps = round(200 / (time.perf_counter() - t0), 1)
#
#         params = round(
#             sum(p.numel() for p in model.model.parameters()) / 1e6, 1
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
#         print(f"[{model_name}] mAP50={results_log[-1]['mAP@0.5']}  "
#               f"mAP50:95={results_log[-1]['mAP@0.5:95']}  FPS={fps}")
#
#     df = pd.DataFrame(results_log)
#     print("\n" + "="*60)
#     print("测试集最终结果")
#     print("="*60)
#     print(df.to_string(index=False))
#
#     out_csv = rf'{BASE_DIR}\test_results.csv'
#     df.to_csv(out_csv, index=False)
#     print(f"\n结果已保存至 {out_csv}")
from ultralytics import YOLO
import pandas as pd
import torch
import time

DATASET  = r'D:/Fire_Project/FireDataset_new2/dataset.yaml'
BASE_DIR = r'D:/Fire_Project/runs/comparison'
IMGSZ    = 640

# 已有的YOLOv8m结果（基准模型）
COMPLETED = [
    {'Model': 'YOLOv8m', 'Params(M)': 25.8,
     'mAP@0.5': 0.922, 'mAP@0.5:0.95': 0.702,
     'Precision': 0.970, 'Recall': 0.875, 'FPS': 43.2},
]

# 待评估的对比模型
# 注意：rtdetr-l2是降低学习率后重新训练的版本
COMPARE = [
    ('yolov5mu',  8,  21.2, f'{BASE_DIR}/yolov5mu/weights/best.pt'),
    ('yolov10m',  8,  15.9, f'{BASE_DIR}/yolov10m/weights/best.pt'),
    ('rtdetr-l',  4,  32.9, f'{BASE_DIR}/rtdetr-l2/weights/best.pt'),
]

def measure_fps(model, imgsz=640, n_warmup=10, n_test=200):
    dummy = torch.randn(1, 3, imgsz, imgsz).cuda()
    model.model.cuda().eval()
    with torch.no_grad():
        for _ in range(n_warmup):
            model.model(dummy)
        torch.cuda.synchronize()
        t0 = time.perf_counter()
        for _ in range(n_test):
            model.model(dummy)
        torch.cuda.synchronize()
    return round(n_test / (time.perf_counter() - t0), 1)

if __name__ == '__main__':
    results = list(COMPLETED)

    for model_name, batch, params, best_pt in COMPARE:
        print(f"\n{'='*50}\n评估: {model_name}\n{'='*50}")

        try:
            model = YOLO(best_pt)

            # 在test集上评估
            metrics = model.val(
                data=DATASET,
                split='test',
                device=0,
                batch=batch,
                verbose=False,
                workers=0,
            )

            # 测量FPS
            fps = measure_fps(model, IMGSZ)

            results.append({
                'Model':        model_name,
                'Params(M)':    params,
                'mAP@0.5':      round(metrics.box.map50, 3),
                'mAP@0.5:0.95': round(metrics.box.map, 3),
                'Precision':    round(float(metrics.box.p.mean()), 3),
                'Recall':       round(float(metrics.box.r.mean()), 3),
                'FPS':          fps,
            })
            print(f"✅ {model_name}: mAP50={results[-1]['mAP@0.5']}, FPS={fps}")

        except Exception as e:
            print(f"❌ {model_name} 评估失败: {e}")
            results.append({
                'Model':        model_name,
                'Params(M)':    params,
                'mAP@0.5':      None,
                'mAP@0.5:0.95': None,
                'Precision':    None,
                'Recall':       None,
                'FPS':          None,
            })

    # 输出汇总结果
    df = pd.DataFrame(results)
    print("\n" + "="*70)
    print("多模型对比结果")
    print("="*70)
    print(df.to_string(index=False))

    save_path = rf'{BASE_DIR}\comparison_results.csv'
    df.to_csv(save_path, index=False, encoding='utf-8-sig')
    print(f"\n✅ 结果已保存: {save_path}")