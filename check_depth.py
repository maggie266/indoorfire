# import cv2, csv, numpy as np, os, random
#
# root = r"D:\Fire_Project\FireDataset_new2"
# out_dir = os.path.join(root, "depth_check")
# os.makedirs(out_dir, exist_ok=True)
#
# for split in ["test", "val"]:
#     csv_path = os.path.join(root, split, "invalid_fraction_Depth_clean.csv")
#     rows = list(csv.DictReader(open(csv_path)))
#     rows.sort(key=lambda r: -float(r["invalid_fraction"]))
#     picks = rows[:6]                                   # 失效比例最高的 6 帧
#     picks += random.Random(0).sample(rows[len(rows)//2:], 3)  # 中低段随机 3 帧做对照
#
#
#     for r in picks:
#         name = r["filename"]
#         raw = cv2.imread(os.path.join(root, split, "Depth", name), cv2.IMREAD_UNCHANGED)
#         cln = cv2.imread(os.path.join(root, split, "Depth_clean", name), cv2.IMREAD_UNCHANGED)
#         if raw.ndim == 3: raw = raw[..., 0]  # 三通道灰度 -> 取单通道
#         if cln.ndim == 3: cln = cln[..., 0]
#         raw = raw.astype(np.float32);
#         cln = cln.astype(np.float32)
#         vis_raw = cv2.cvtColor(cv2.normalize(raw, None, 0, 255, cv2.NORM_MINMAX).astype(np.uint8), cv2.COLOR_GRAY2BGR)
#         vis_cln = cv2.cvtColor(cv2.normalize(cln, None, 0, 255, cv2.NORM_MINMAX).astype(np.uint8), cv2.COLOR_GRAY2BGR)
#         vis_cln[cln == 0] = (0, 0, 255)
#         combo = np.hstack([vis_raw, vis_cln])
#         tag = f"{float(r['invalid_fraction']):.3f}"
#         cv2.imwrite(os.path.join(out_dir, f"{split}_{tag}_{name}"), combo)
#         print(split, tag, name)
#
# print(f"\n拼图输出 -> {out_dir}")

import cv2, glob

files = glob.glob(r"D:\Fire_Project\FireDataset_new2\test\Depth\*.png")
print("共", len(files), "个文件")
for p in files[:3]:                      # 抽前 3 个
    img = cv2.imread(p, cv2.IMREAD_UNCHANGED)
    print(p.split("\\")[-1],
          "| dtype:", img.dtype, "| shape:", img.shape,
          "| min:", img.min(), "| max:", img.max())

# 顺便查 Depth_clean 的格式
p = glob.glob(r"D:\Fire_Project\FireDataset_new2\test\Depth_clean\*.png")[0]
img = cv2.imread(p, cv2.IMREAD_UNCHANGED)
print("Depth_clean:", "| dtype:", img.dtype, "| shape:", img.shape, "| max:", img.max())