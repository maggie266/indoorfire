# # import os
# # import shutil
# # import random
# # from pathlib import Path
# #
# # # ==========================================
# # # ✅ 配置区域：只需要修改这里
# # # ==========================================
# #
# # SOURCE_DIR  = r"D:/Fire_Project/FireDataset"   # 源数据集根目录
# # OUTPUT_DIR  = r"D:/Fire_Project/SplitDataset"  # 输出目录
# #
# # TRAIN_RATIO = 0.7
# # VAL_RATIO   = 0.2
# # TEST_RATIO  = 0.1
# #
# # RANDOM_SEED = 42
# # SUB_FOLDERS = ["RGB", "IR", "Depth", "Labels", "Labels_vis"]
# #
# # # ==========================================
# # # 初始化
# # # ==========================================
# #
# # random.seed(RANDOM_SEED)
# #
# # for split in ["train", "val", "test"]:
# #     for sub in SUB_FOLDERS:
# #         os.makedirs(os.path.join(OUTPUT_DIR, split, sub), exist_ok=True)
# #
# # print(f"📂 源目录: {SOURCE_DIR}")
# # print(f"📂 输出目录: {OUTPUT_DIR}")
# # print(f"📊 划分比例: train={TRAIN_RATIO} val={VAL_RATIO} test={TEST_RATIO}")
# # print(f"{'='*60}")
# #
# # # ==========================================
# # # 收集所有样本
# # # ==========================================
# #
# # all_samples = []  # 每个元素：(scene_folder, base_stem, rgb_filename)
# #
# # source_path = Path(SOURCE_DIR)
# # scene_folders = sorted([f for f in source_path.iterdir() if f.is_dir()])
# #
# # print(f"✅ 找到 {len(scene_folders)} 个场景文件夹")
# #
# # for scene_folder in scene_folders:
# #     rgb_dir = scene_folder / "RGB"
# #     if not rgb_dir.exists():
# #         print(f"  ⚠️ 跳过（无RGB文件夹）: {scene_folder.name}")
# #         continue
# #
# #     rgb_files = [f for f in rgb_dir.iterdir()
# #                  if f.suffix.lower() in ['.png', '.jpg', '.jpeg']]
# #
# #     for rgb_file in rgb_files:
# #         stem = rgb_file.stem
# #         # RGB文件名末尾有多余的 _ ，去掉得到 base_stem
# #         # 例如：bedroom_xxx_Sample_00001_.png → bedroom_xxx_Sample_00001
# #         if stem.endswith('_'):
# #             base_stem = stem[:-1]
# #         else:
# #             base_stem = stem
# #         all_samples.append((scene_folder, base_stem, rgb_file.name))
# #
# # print(f"✅ 共找到 {len(all_samples)} 个样本")
# #
# # # ==========================================
# # # 划分
# # # ==========================================
# #
# # random.shuffle(all_samples)
# #
# # n_total = len(all_samples)
# # n_train = int(n_total * TRAIN_RATIO)
# # n_val   = int(n_total * VAL_RATIO)
# #
# # train_samples = all_samples[:n_train]
# # val_samples   = all_samples[n_train:n_train + n_val]
# # test_samples  = all_samples[n_train + n_val:]
# #
# # print(f"📊 train: {len(train_samples)}  val: {len(val_samples)}  test: {len(test_samples)}")
# # print(f"{'='*60}")
# #
# # # ==========================================
# # # 复制文件
# # # ==========================================
# #
# # def copy_samples(samples, split_name):
# #     print(f"\n🔄 正在复制 {split_name} 集...")
# #     copied  = 0
# #     missing = 0
# #
# #     for scene_folder, base_stem, rgb_filename in samples:
# #         file_map = {
# #             "RGB":        rgb_filename,
# #             "IR":         f"{base_stem}.png",
# #             "Depth":      f"{base_stem}.png",
# #             "Labels":     f"{base_stem}.txt",
# #             "Labels_vis": f"{base_stem}_vis.png",
# #         }
# #
# #         for sub, filename in file_map.items():
# #             src_file = scene_folder / sub / filename
# #             dst_dir  = Path(OUTPUT_DIR) / split_name / sub
# #             dst_file = dst_dir / filename
# #
# #             if src_file.exists():
# #                 shutil.copy2(src_file, dst_file)
# #                 copied += 1
# #             else:
# #                 missing += 1
# #
# #     print(f"  ✅ 复制完成: {copied} 个文件，{missing} 个缺失")
# #     if missing > 0:
# #         print(f"  ⚠️ 有 {missing} 个文件缺失，可能是部分样本渲染不完整")
# #
# # copy_samples(train_samples, "train")
# # copy_samples(val_samples,   "val")
# # copy_samples(test_samples,  "test")
# #
# # print(f"\n{'='*60}")
# # print(f"🎉 数据集划分完成！")
# # print(f"  train: {len(train_samples)} 个样本")
# # print(f"  val:   {len(val_samples)} 个样本")
# # print(f"  test:  {len(test_samples)} 个样本")
# # print(f"\n📁 输出目录: {OUTPUT_DIR}")
# import shutil
# import random
# from pathlib import Path
#
# # ============ 配置 ============
# SRC_ROOT    = Path('D:/Fire_Project/dataset')
# DST_ROOT    = Path('D:/Fire_Project/FireDataset_new')
# TRAIN_RATIO = 0.70
# VAL_RATIO   = 0.15
# RANDOM_SEED = 42
# # ==============================
#
# random.seed(RANDOM_SEED)
# SKIP_DIRS = {'train', 'val', 'test'}
#
# # ── 第一步：收集有效帧（以RGB为基准）──────────────────
# print("=== 第一步：收集有效帧 ===")
# all_valid       = []   # [(scene_dir, stem, rgb_stem), ...]
# missing_txt     = []   # RGB存在但txt不存在
# missing_ir      = []   # IR缺失（记录但不排除）
# missing_depth   = []   # Depth缺失（记录但不排除）
#
# scene_dirs = sorted(
#     d for d in SRC_ROOT.iterdir()
#     if d.is_dir() and d.name not in SKIP_DIRS
# )
#
# for scene_dir in scene_dirs:
#     rgb_dir = scene_dir / 'RGB'
#     lbl_dir = scene_dir / 'Labels'
#
#     if not rgb_dir.exists():
#         continue
#
#     for rgb_file in sorted(rgb_dir.glob('*.png')):
#         rgb_stem = rgb_file.stem          # e.g. bedroom_..._0001_
#         # 去掉末尾的 _ 得到 base_stem
#         if rgb_stem.endswith('_'):
#             stem = rgb_stem[:-1]
#         else:
#             stem = rgb_stem
#
#         # 检查 txt 是否存在（必须存在）
#         lbl_file = lbl_dir / f'{stem}.txt'
#         if not lbl_file.exists():
#             missing_txt.append(f"{scene_dir.name}/Labels/{stem}.txt")
#             continue  # 没有txt，跳过这张RGB
#
#         # 记录IR/Depth缺失（不排除）
#         if not (scene_dir / 'IR'    / f'{stem}.png').exists():
#             missing_ir.append(f"{scene_dir.name}/IR/{stem}.png")
#         if not (scene_dir / 'Depth' / f'{stem}.png').exists():
#             missing_depth.append(f"{scene_dir.name}/Depth/{stem}.png")
#
#         all_valid.append((scene_dir, stem, rgb_stem))
#
# print(f"有效帧总数: {len(all_valid)}")
#
# # 输出缺失报告
# all_missing = (
#     [f"[缺少txt] {m}" for m in missing_txt] +
#     [f"[缺少IR]  {m}" for m in missing_ir] +
#     [f"[缺少Depth] {m}" for m in missing_depth]
# )
#
# if all_missing:
#     report = SRC_ROOT / 'missing_files.txt'
#     report.write_text('\n'.join(all_missing), encoding='utf-8')
#     print(f"⚠️ 缺失情况:")
#     if missing_txt:
#         print(f"  RGB有但txt缺失: {len(missing_txt)} 个（这些RGB被排除）")
#     if missing_ir:
#         print(f"  IR缺失:         {len(missing_ir)} 个（仍参与划分）")
#     if missing_depth:
#         print(f"  Depth缺失:      {len(missing_depth)} 个（仍参与划分）")
#     print(f"  详见: {report}")
# else:
#     print("所有RGB均有对应txt，三模态完整 ✅")
#
# # ── 第二步：随机划分 ────────────────────────────────
# print("\n=== 第二步：随机划分 ===")
# random.shuffle(all_valid)
# n       = len(all_valid)
# n_train = int(n * TRAIN_RATIO)
# n_val   = int(n * VAL_RATIO)
#
# splits = {
#     'train': all_valid[:n_train],
#     'val':   all_valid[n_train:n_train + n_val],
#     'test':  all_valid[n_train + n_val:],
# }
# for split, items in splits.items():
#     print(f"  {split}: {len(items)} 帧")
#
# # ── 第三步：复制文件（保持原文件名）────────────────
# print("\n=== 第三步：复制文件 ===")
#
# for split, items in splits.items():
#     for dst_name in ['images', 'IR', 'Depth', 'labels', 'Labels_vis']:
#         (DST_ROOT / split / dst_name).mkdir(parents=True, exist_ok=True)
#
#     for scene_dir, stem, rgb_stem in items:
#
#         # RGB → images（保持原文件名含末尾_）
#         src_rgb = scene_dir / 'RGB' / f'{rgb_stem}.png'
#         dst_rgb = DST_ROOT / split / 'images' / f'{rgb_stem}.png'
#         if src_rgb.exists():
#             shutil.copy2(src_rgb, dst_rgb)
#
#         # IR
#         src_ir = scene_dir / 'IR' / f'{stem}.png'
#         dst_ir = DST_ROOT / split / 'IR' / f'{stem}.png'
#         if src_ir.exists():
#             shutil.copy2(src_ir, dst_ir)
#
#         # Depth
#         src_depth = scene_dir / 'Depth' / f'{stem}.png'
#         dst_depth = DST_ROOT / split / 'Depth' / f'{stem}.png'
#         if src_depth.exists():
#             shutil.copy2(src_depth, dst_depth)
#
#         # Labels
#         src_lbl = scene_dir / 'Labels' / f'{stem}.txt'
#         dst_lbl = DST_ROOT / split / 'labels' / f'{stem}.txt'
#         if src_lbl.exists():
#             shutil.copy2(src_lbl, dst_lbl)
#
#         # Labels_vis
#         src_vis = scene_dir / 'Labels_vis' / f'{stem}_vis.png'
#         dst_vis = DST_ROOT / split / 'Labels_vis' / f'{stem}_vis.png'
#         if src_vis.exists():
#             shutil.copy2(src_vis, dst_vis)
#
#     print(f"  {split} 复制完成 ✅")
#
# # ── 第四步：验证 ────────────────────────────────────
# print("\n=== 第四步：验证新数据集 ===")
# all_ok = True
# for split in ['train', 'val', 'test']:
#     n_images = len(list((DST_ROOT / split / 'images').glob('*.png')))
#     n_ir     = len(list((DST_ROOT / split / 'IR').glob('*.png')))
#     n_depth  = len(list((DST_ROOT / split / 'Depth').glob('*.png')))
#     n_labels = len(list((DST_ROOT / split / 'labels').glob('*.txt')))
#     n_vis    = len(list((DST_ROOT / split / 'Labels_vis').glob('*.png')))
#
#     core_ok = (n_images == n_labels)
#     status  = "✅" if core_ok else "❌"
#     print(f"  {split} {status}: images={n_images} IR={n_ir} "
#           f"Depth={n_depth} labels={n_labels} Labels_vis={n_vis}")
#     if not core_ok:
#         all_ok = False
#
# if all_ok:
#     print(f"\n每张RGB都有对应txt，可以开始训练 ✅")
#     print(f"总有效帧: {len(all_valid)}")
# else:
#     print(f"\n存在不对齐，请检查 ❌")
#
# # ── 第五步：生成yaml ────────────────────────────────
# yaml_content = f"""path: {DST_ROOT.as_posix()}
# train: train/images
# val: val/images
# test: test/images
#
# nc: 1
# names: ['victim']
# """
# yaml_path = DST_ROOT / 'dataset.yaml'
# yaml_path.write_text(yaml_content, encoding='utf-8')
# print(f"\ndataset.yaml 已生成: {yaml_path}")
# print(f"训练时使用: DATASET = '{yaml_path.as_posix()}'")

#新的划分方式
import shutil
import random
from pathlib import Path

# ============ 配置 ============
SRC_ROOT    = Path('D:/Fire_Project/dataset')
DST_ROOT    = Path('D:/Fire_Project/FireDataset_new2')
TRAIN_RATIO = 0.70
VAL_RATIO   = 0.15
RANDOM_SEED = 42
# ==============================

random.seed(RANDOM_SEED)
SKIP_DIRS = {'train', 'val', 'test'}

# ── 第一步：收集有效帧（以RGB为基准）──────────────────
print("=== 第一步：收集有效帧 ===")

scene_dirs = sorted(
    d for d in SRC_ROOT.iterdir()
    if d.is_dir() and d.name not in SKIP_DIRS
)

# 按场景文件夹收集有效帧
scene_frames = {}   # {scene_dir: [(stem, rgb_stem), ...]}
missing_txt   = []
missing_ir    = []
missing_depth = []

for scene_dir in scene_dirs:
    rgb_dir = scene_dir / 'RGB'
    lbl_dir = scene_dir / 'Labels'
    if not rgb_dir.exists():
        continue

    frames = []
    for rgb_file in sorted(rgb_dir.glob('*.png')):
        rgb_stem = rgb_file.stem
        stem = rgb_stem[:-1] if rgb_stem.endswith('_') else rgb_stem

        lbl_file = lbl_dir / f'{stem}.txt'
        if not lbl_file.exists():
            missing_txt.append(f"{scene_dir.name}/Labels/{stem}.txt")
            continue

        if not (scene_dir / 'IR'    / f'{stem}.png').exists():
            missing_ir.append(f"{scene_dir.name}/IR/{stem}.png")
        if not (scene_dir / 'Depth' / f'{stem}.png').exists():
            missing_depth.append(f"{scene_dir.name}/Depth/{stem}.png")

        frames.append((stem, rgb_stem))

    if frames:
        scene_frames[scene_dir] = frames

total_frames = sum(len(v) for v in scene_frames.values())
print(f"有效场景文件夹数: {len(scene_frames)}")
print(f"有效帧总数:       {total_frames}")

if missing_txt:
    print(f"⚠️  RGB有但txt缺失: {len(missing_txt)} 个（已排除）")
if missing_ir:
    print(f"⚠️  IR缺失:         {len(missing_ir)} 个（仍参与划分）")
if missing_depth:
    print(f"⚠️  Depth缺失:      {len(missing_depth)} 个（仍参与划分）")

# ── 第二步：按场景文件夹划分 ──────────────────────────
print("\n=== 第二步：按场景文件夹划分 ===")

all_scenes = list(scene_frames.keys())
random.shuffle(all_scenes)

n        = len(all_scenes)
n_train  = int(n * TRAIN_RATIO)
n_val    = int(n * VAL_RATIO)

scene_splits = {
    'train': all_scenes[:n_train],
    'val':   all_scenes[n_train:n_train + n_val],
    'test':  all_scenes[n_train + n_val:],
}

# 统计各split的帧数和场景数
for split, scenes in scene_splits.items():
    frame_count = sum(len(scene_frames[s]) for s in scenes)
    print(f"  {split}: {len(scenes)} 个场景文件夹，{frame_count} 帧")
    # 打印场景名（验证是否整体划分）
    for s in scenes[:3]:
        print(f"    └─ {s.name}（{len(scene_frames[s])}帧）")
    if len(scenes) > 3:
        print(f"    └─ ...共{len(scenes)}个")

# ── 第三步：复制文件 ───────────────────────────────────
print("\n=== 第三步：复制文件 ===")

for split, scenes in scene_splits.items():
    for dst_name in ['images', 'IR', 'Depth', 'labels', 'Labels_vis']:
        (DST_ROOT / split / dst_name).mkdir(parents=True, exist_ok=True)

    for scene_dir in scenes:
        for stem, rgb_stem in scene_frames[scene_dir]:

            # RGB → images
            src = scene_dir / 'RGB' / f'{rgb_stem}.png'
            dst = DST_ROOT / split / 'images' / f'{rgb_stem}.png'
            if src.exists():
                shutil.copy2(src, dst)

            # IR
            src = scene_dir / 'IR' / f'{stem}.png'
            dst = DST_ROOT / split / 'IR' / f'{stem}.png'
            if src.exists():
                shutil.copy2(src, dst)

            # Depth
            src = scene_dir / 'Depth' / f'{stem}.png'
            dst = DST_ROOT / split / 'Depth' / f'{stem}.png'
            if src.exists():
                shutil.copy2(src, dst)

            # Labels
            src = scene_dir / 'Labels' / f'{stem}.txt'
            dst = DST_ROOT / split / 'labels' / f'{stem}.txt'
            if src.exists():
                shutil.copy2(src, dst)

            # Labels_vis
            src = scene_dir / 'Labels_vis' / f'{stem}_vis.png'
            dst = DST_ROOT / split / 'Labels_vis' / f'{stem}_vis.png'
            if src.exists():
                shutil.copy2(src, dst)

    frame_count = sum(len(scene_frames[s]) for s in scenes)
    print(f"  {split} 复制完成 ✅（{frame_count} 帧）")

# ── 第四步：验证 ───────────────────────────────────────
print("\n=== 第四步：验证新数据集 ===")
all_ok = True
for split in ['train', 'val', 'test']:
    n_img   = len(list((DST_ROOT / split / 'images').glob('*.png')))
    n_ir    = len(list((DST_ROOT / split / 'IR').glob('*.png')))
    n_depth = len(list((DST_ROOT / split / 'Depth').glob('*.png')))
    n_lbl   = len(list((DST_ROOT / split / 'labels').glob('*.txt')))
    n_vis   = len(list((DST_ROOT / split / 'Labels_vis').glob('*.png')))

    core_ok = (n_img == n_lbl)
    status  = "✅" if core_ok else "❌"
    print(f"  {split} {status}: images={n_img} IR={n_ir} "
          f"Depth={n_depth} labels={n_lbl} Labels_vis={n_vis}")
    if not core_ok:
        all_ok = False

if all_ok:
    print(f"\n每张RGB都有对应txt，可以开始训练 ✅")
else:
    print(f"\n存在不对齐，请检查 ❌")

# ── 第五步：输出场景划分记录 ──────────────────────────
record_lines = []
for split, scenes in scene_splits.items():
    for s in scenes:
        record_lines.append(f"{split}\t{s.name}\t{len(scene_frames[s])}帧")

record_path = DST_ROOT / 'scene_split_record.txt'
record_path.write_text('\n'.join(record_lines), encoding='utf-8')
print(f"\n场景划分记录已保存至: {record_path}")

# ── 第六步：生成yaml ───────────────────────────────────
yaml_content = f"""path: {DST_ROOT.as_posix()}
train: train/images
val: val/images
test: test/images

nc: 1
names: ['victim']
"""
yaml_path = DST_ROOT / 'dataset.yaml'
yaml_path.write_text(yaml_content, encoding='utf-8')
print(f"dataset.yaml 已生成: {yaml_path}")