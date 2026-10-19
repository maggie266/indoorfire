from ultralytics import YOLO

# DATASET  = r'D:/Fire_Project/FireDataset_new2/dataset.yaml'
# BASE_DIR = r'D:/Fire_Project/runs/comparison'
# EPOCHS   = 100
# IMGSZ    = 640
#
# # 模型名称对应关系
# # YOLOv5mu：YOLOv5 medium
# # yolov10m：YOLOv10 medium
# # rtdetr-l：RT-DETR large（最接近medium规模）
# MODELS = [
#     ('yolov5mu',  8),
#     ('yolov10m',  8),
#     ('rtdetr-l',  8),
# ]

# if __name__ == '__main__':
#     for model_name, batch in MODELS:
#         print(f"\n{'='*50}\n训练: {model_name}\n{'='*50}")
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
#         print(f"✅ {model_name} 训练完成")
if __name__ == '__main__':
    model = YOLO('rtdetr-l.pt')
    model.train(
        data=r'D:/Fire_Project/FireDataset_new2/dataset.yaml',
        epochs=100,
        imgsz=640,
        batch=4,  # 从8改为4，减少显存压力
        device=0,
        project=r'D:/Fire_Project/runs/comparison',
        name='rtdetr-l2',
        exist_ok=True,
        patience=20,
        workers=4,

        # 关键修改：降低学习率
        lr0=0.0001,  # 默认0.01，降低100倍
        lrf=0.01,
        warmup_epochs=5,  # 增加warmup轮数

        # 关闭amp，避免fp16精度问题导致NaN
        amp=False,
    )