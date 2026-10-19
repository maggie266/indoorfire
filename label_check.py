# import os, glob
# img_dir = r"D:\Fire_Project\real\images"
# lbl_dir = r"D:\Fire_Project\real\labels"
# imgs = {os.path.splitext(f)[0] for f in os.listdir(img_dir)}
# lbls = {os.path.splitext(f)[0] for f in os.listdir(lbl_dir) if f.endswith(".txt")}
# print("图像:", len(imgs), "| 有标注:", len(lbls), "| 无目标帧:", len(imgs - lbls))
# # 补空 txt(归档明确性)
# for stem in imgs - lbls:
#     open(os.path.join(lbl_dir, stem + ".txt"), "w").close()
# # 类别号自检:应全为 0
# bad = [f for f in glob.glob(lbl_dir + r"\*.txt")
#        for line in open(f) if line.strip() and line.split()[0] != "0"]
# print("非0类别行:", len(bad))
#
# # import os, random, shutil
# # random.seed(0)
# # root = r"D:\Fire_Project\real"
# # imgs = sorted(os.listdir(os.path.join(root, "images")))
# # random.shuffle(imgs)
# # test, pool = imgs[:30], imgs[30:]
# # for split, files in [("real_test", test), ("finetune_pool", pool)]:
# #     for sub in ["images", "labels"]:
# #         os.makedirs(os.path.join(root, split, sub), exist_ok=True)
# #     for f in files:
# #         stem = os.path.splitext(f)[0]
# #         shutil.copy2(os.path.join(root, "images", f), os.path.join(root, split, "images", f))
# #         shutil.copy2(os.path.join(root, "labels", stem + ".txt"),
# #                      os.path.join(root, split, "labels", stem + ".txt"))
# # print("test:", len(test), "pool:", len(pool))

import cv2, os, glob
img_dir = r"D:\Fire_Project\real\real_test\images"
lbl_dir = r"D:\Fire_Project\real\real_test\labels"
out = r"D:\Fire_Project\real\gt_check"; os.makedirs(out, exist_ok=True)
for p in glob.glob(img_dir + r"\*")[:10]:
    img = cv2.imread(p); h, w = img.shape[:2]
    stem = os.path.splitext(os.path.basename(p))[0]
    lp = os.path.join(lbl_dir, stem + ".txt")
    if os.path.exists(lp):
        for line in open(lp):
            if not line.strip(): continue
            _, cx, cy, bw, bh = map(float, line.split()[:5])
            x1, y1 = int((cx-bw/2)*w), int((cy-bh/2)*h)
            x2, y2 = int((cx+bw/2)*w), int((cy+bh/2)*h)
            cv2.rectangle(img, (x1,y1), (x2,y2), (0,255,0), 3)
    cv2.imwrite(os.path.join(out, stem + "_gt.jpg"), img)