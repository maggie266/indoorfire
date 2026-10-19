from ultralytics import YOLO
from multiprocessing import freeze_support


def main():

    model = YOLO(
        r"D:\Fire_Project\runs\detect\depth_only_scratch\weights\best.pt"
    )

    metrics = model.val(
        data=r"D:\Fire_Project\scripts\data_depth.yaml",  # 改成你的yaml
        split="test",
        imgsz=640,
        batch=16,       # 和你的实验一致
        device=0,
        workers=4,      # 也可以8
        plots=True
    )

    print("\n==============================")
    print("Depth-only TEST results")
    print("==============================")

    print(f"Precision   : {metrics.box.mp * 100:.2f}%")
    print(f"Recall      : {metrics.box.mr * 100:.2f}%")
    print(f"mAP@0.5     : {metrics.box.map50 * 100:.2f}%")
    print(f"mAP@0.5:0.95: {metrics.box.map * 100:.2f}%")

    inference_ms = metrics.speed["inference"]

    print(f"Inference   : {inference_ms:.3f} ms/image")
    print(f"FPS         : {1000 / inference_ms:.2f}")


if __name__ == "__main__":
    freeze_support()
    main()
