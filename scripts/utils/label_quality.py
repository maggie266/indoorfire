# # # import os
# # # from pathlib import Path
# # # from collections import defaultdict
# # #
# # # DATASET_ROOT = Path('D:/Fire_Project/FireDataset_new')
# # # SPLITS = ['train', 'val', 'test']
# # #
# # # print("=" * 60)
# # # print("第一步：自动一致性检查")
# # # print("=" * 60)
# # #
# # # total_issues = []
# # # summary = {}
# # #
# # # for split in SPLITS:
# # #     img_dir = DATASET_ROOT / split / 'images'
# # #     lbl_dir = DATASET_ROOT / split / 'labels'
# # #
# # #     img_stems = {p.stem for p in img_dir.glob('*.png')}
# # #     lbl_stems = {p.stem for p in lbl_dir.glob('*.txt')}
# # #
# # #     # 检查①：图像与标注一一对应
# # #     only_img = img_stems - lbl_stems
# # #     only_lbl = lbl_stems - img_stems
# # #
# # #     # 检查②：标注内容合法性
# # #     negative_samples = []
# # #     invalid_coords = []
# # #     invalid_format = []
# # #     valid_count    = 0
# # #
# # #     for lbl_file in lbl_dir.glob('*.txt'):
# # #         lines = lbl_file.read_text().strip().splitlines()
# # #
# # #         if not lines:
# # #             negative_samples.append(lbl_file.name)
# # #             continue  # 正常，不算问题
# # #
# # #         for line in lines:
# # #             parts = line.strip().split()
# # #
# # #             # 格式检查：必须是5列
# # #             if len(parts) != 5:
# # #                 invalid_format.append(f"{lbl_file.name}: '{line}'")
# # #                 continue
# # #
# # #             try:
# # #                 cls = int(parts[0])
# # #                 cx, cy, bw, bh = map(float, parts[1:])
# # #             except ValueError:
# # #                 invalid_format.append(f"{lbl_file.name}: '{line}'")
# # #                 continue
# # #
# # #             # 坐标范围检查：必须在[0,1]
# # #             if not (0 <= cx <= 1 and 0 <= cy <= 1 and
# # #                     0 < bw <= 1 and 0 < bh <= 1):
# # #                 invalid_coords.append(
# # #                     f"{lbl_file.name}: cx={cx:.3f} cy={cy:.3f} "
# # #                     f"w={bw:.3f} h={bh:.3f}"
# # #                 )
# # #
# # #         valid_count += 1
# # #
# # #     issues = {
# # #         '有图无标注': list(only_img)[:5],
# # #         '有标注无图': list(only_lbl)[:5],
# # #         '空标注文件': negative_samples[:5],
# # #         '坐标越界':   invalid_coords[:5],
# # #         '格式错误':   invalid_format[:5],
# # #     }
# # #
# # #     summary[split] = {
# # #         '图像总数':   len(img_stems),
# # #         '标注总数':   len(lbl_stems),
# # #         '完全对齐':   len(only_img) == 0 and len(only_lbl) == 0,
# # #         '空标注数':   len(negative_samples),
# # #         '坐标越界数': len(invalid_coords),
# # #         '格式错误数': len(invalid_format),
# # #     }
# # #
# # #     print(f"\n[{split}]")
# # #     for k, v in summary[split].items():
# # #         print(f"  {k}: {v}")
# # #
# # #     for issue_name, items in issues.items():
# # #         if items:
# # #             print(f"  ⚠️  {issue_name} 示例:")
# # #             for item in items:
# # #                 print(f"      {item}")
# # #
# # # print("\n" + "=" * 60)
# # #
# # # all_ok = all(
# # #     s['完全对齐'] and
# # #     s['坐标越界数'] == 0 and
# # #     s['格式错误数'] == 0
# # #     for s in summary.values()
# # # )
# # #
# # # print("自动一致性检查结果:", "✅ 全部通过" if all_ok else "❌ 存在问题")
# # #
# # # # 单独说明空标注情况
# # # total_negative = sum(s['空标注数'] for s in summary.values())
# # # print(f"负样本（空标注）总数: {total_negative} 个，已作为合法硬负样本保留")
# # # # import os
# # # # import shutil
# # # # from pathlib import Path
# # # #
# # # # DATASET_ROOT = Path('D:/Fire_Project/FireDataset_new')
# # # # SPLITS = ['train', 'val', 'test']
# # # # MIN_BOX_SIZE = 0.005  # bbox宽或高小于此值视为无效
# # # #
# # # # print("=" * 60)
# # # # print("数据集修复脚本")
# # # # print("=" * 60)
# # # #
# # # # for split in SPLITS:
# # # #     img_dir = DATASET_ROOT / split / 'images'
# # # #     lbl_dir = DATASET_ROOT / split / 'labels'
# # # #
# # # #     img_files = {p.stem: p for p in img_dir.glob('*.png')}
# # # #     lbl_files = {p.stem: p for p in lbl_dir.glob('*.txt')}
# # # #
# # # #     fix1_count = 0  # 修复下划线问题
# # # #     fix2_count = 0  # 删除零尺寸bbox
# # # #     kept_empty = 0  # 保留空标注（负样本）
# # # #
# # # #     # ── 修复一：图片文件名末尾有下划线 ──────────────
# # # #     # 找到 stem 末尾带 _ 的图片，且对应去掉_后有标注文件
# # # #     for img_stem, img_path in list(img_files.items()):
# # # #         if img_stem.endswith('_'):
# # # #             clean_stem = img_stem.rstrip('_')
# # # #             if clean_stem in lbl_files:
# # # #                 # 重命名图片，去掉末尾下划线
# # # #                 new_img_path = img_dir / f'{clean_stem}.png'
# # # #                 img_path.rename(new_img_path)
# # # #                 fix1_count += 1
# # # #
# # # #     # ── 修复二：删除零尺寸bbox行 ────────────────────
# # # #     for lbl_stem, lbl_path in lbl_files.items():
# # # #         content = lbl_path.read_text().strip()
# # # #
# # # #         if not content:
# # # #             # 空标注文件 = 负样本，保留不动
# # # #             kept_empty += 1
# # # #             continue
# # # #
# # # #         lines = content.splitlines()
# # # #         valid_lines = []
# # # #         removed = False
# # # #
# # # #         for line in lines:
# # # #             parts = line.strip().split()
# # # #             if len(parts) != 5:
# # # #                 continue
# # # #             try:
# # # #                 _, cx, cy, bw, bh = map(float, parts)
# # # #                 # 过滤零尺寸或极小bbox
# # # #                 if bw < MIN_BOX_SIZE or bh < MIN_BOX_SIZE:
# # # #                     removed = True
# # # #                     continue
# # # #                 # 过滤坐标越界
# # # #                 if not (0 <= cx <= 1 and 0 <= cy <= 1 and
# # # #                         bw <= 1 and bh <= 1):
# # # #                     removed = True
# # # #                     continue
# # # #                 valid_lines.append(line.strip())
# # # #             except ValueError:
# # # #                 continue
# # # #
# # # #         if removed:
# # # #             # 写回有效行（可能变为空文件，即负样本）
# # # #             lbl_path.write_text('\n'.join(valid_lines))
# # # #             fix2_count += 1
# # # #
# # # #     print(f"\n[{split}]")
# # # #     print(f"  修复图片文件名下划线: {fix1_count} 个")
# # # #     print(f"  删除零尺寸bbox: {fix2_count} 个文件受影响")
# # # #     print(f"  保留空标注负样本: {kept_empty} 个")
# # # #
# # # # print("\n修复完成，重新运行检查脚本验证结果")
# # #标注统计分析
# # import numpy as np
# # import json
# # from pathlib import Path
# #
# # DATASET_ROOT = Path('D:/Fire_Project/FireDataset_new')
# # SPLITS = ['train', 'val', 'test']
# #
# # print("=" * 60)
# # print("第二步：标注统计分析")
# # print("=" * 60)
# #
# # all_stats = {}
# #
# # for split in SPLITS:
# #     lbl_dir = DATASET_ROOT / split / 'labels'
# #
# #     box_areas   = []   # bbox面积（归一化）
# #     box_widths  = []
# #     box_heights = []
# #     aspect_ratios = []
# #     instances_per_image = []
# #
# #     for lbl_file in lbl_dir.glob('*.txt'):
# #         lines = lbl_file.read_text().strip().splitlines()
# #         count = 0
# #         for line in lines:
# #             parts = line.strip().split()
# #             if len(parts) != 5:
# #                 continue
# #             _, cx, cy, bw, bh = map(float, parts)
# #             area = bw * bh
# #             box_areas.append(area)
# #             box_widths.append(bw)
# #             box_heights.append(bh)
# #             aspect_ratios.append(bw / bh if bh > 0 else 0)
# #             count += 1
# #         instances_per_image.append(count)
# #
# #     box_areas = np.array(box_areas)
# #     instances_per_image = np.array(instances_per_image)
# #
# #     # 小目标定义：面积 < 0.01（即图像面积1%）
# #     small_target_ratio = (box_areas < 0.01).mean() * 100
# #
# #     stats = {
# #         '总实例数':         len(box_areas),
# #         '每图平均实例数':   round(float(instances_per_image.mean()), 2),
# #         'bbox面积中位数':   round(float(np.median(box_areas)) * 100, 2),
# #         'bbox面积P10(%)':  round(float(np.percentile(box_areas, 10)) * 100, 3),
# #         'bbox面积P90(%)':  round(float(np.percentile(box_areas, 90)) * 100, 3),
# #         '小目标比例(%)':    round(small_target_ratio, 1),
# #         '平均宽高比':       round(float(np.mean(aspect_ratios)), 3),
# #     }
# #
# #     all_stats[split] = stats
# #     print(f"\n[{split}]")
# #     for k, v in stats.items():
# #         print(f"  {k}: {v}")
# #
# # # 保存统计结果
# # with open('annotation_statistics.json', 'w', encoding='utf-8') as f:
# #     json.dump(all_stats, f, ensure_ascii=False, indent=2)
# # print("\n统计结果已保存至 annotation_statistics.json")
#
#
# # 标注质量结果可视化
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from pathlib import Path
import matplotlib.pyplot as plt
import matplotlib as mpl


DATASET_ROOT = Path('D:/Fire_Project/FireDataset_new2')
SPLITS = ['train', 'val', 'test']
SAVE_DIR = Path('D:/Fire_Project/annotation_analysis3')
SAVE_DIR.mkdir(exist_ok=True)
# 加在所有绘图代码之前
mpl.rcParams['font.family'] = 'Times New Roman'
mpl.rcParams['mathtext.fontset'] = 'stix'  # 数学符号也用新罗马风格
# 收集所有数据
all_data = {}
for split in SPLITS:
    lbl_dir = DATASET_ROOT / split / 'labels'
    areas, widths, heights, aspects = [], [], [], []
    instances_per_img = []

    for lbl_file in lbl_dir.glob('*.txt'):
        lines = lbl_file.read_text().strip().splitlines()
        count = 0
        for line in lines:
            parts = line.strip().split()
            if len(parts) != 5:
                continue
            _, cx, cy, bw, bh = map(float, parts)
            areas.append(bw * bh * 100)       # 转为百分比
            widths.append(bw)
            heights.append(bh)
            aspects.append(bw / bh if bh > 0 else 0)
            count += 1
        instances_per_img.append(count)

    all_data[split] = {
        'areas': np.array(areas),
        'widths': np.array(widths),
        'heights': np.array(heights),
        'aspects': np.array(aspects),
        'instances': np.array(instances_per_img),
    }

COLORS = {'train': '#2B6CB0', 'val': '#C05621', 'test': '#276749'}

# ── 图1：bbox面积分布（三个split对比）────────────────────
fig, axes = plt.subplots(1, 3, figsize=(15, 4))
fig.suptitle('Bounding Box Area Distribution (%)', fontsize=14, fontweight='bold')

for ax, split in zip(axes, SPLITS):
    areas = all_data[split]['areas']
    # 截断到5%以内显示，避免长尾影响
    clipped = areas[areas <= 5]
    ax.hist(clipped, bins=50, color=COLORS[split], alpha=0.85, edgecolor='white')
    ax.axvline(np.median(areas), color='red', linestyle='--',
               linewidth=1.5, label=f'Median: {np.median(areas):.2f}%')
    ax.axvline(1.0, color='orange', linestyle=':',
               linewidth=1.5, label='Small target threshold (1%)')
    small_ratio = (areas < 1.0).mean() * 100
    ax.set_title(f'{split.capitalize()}\n'
                 f'Small targets: {small_ratio:.1f}%',
                 fontsize=11)
    ax.set_xlabel('BBox Area (% of image)', fontsize=10)
    ax.set_ylabel('Count', fontsize=10)
    ax.legend(fontsize=8)
    ax.grid(axis='y', alpha=0.3)

plt.tight_layout()
plt.savefig(SAVE_DIR / 'fig1_bbox_area_distribution.png', dpi=200, bbox_inches='tight')
plt.close()
print("✅ 图1 保存完成")

# ── 图2：宽高比分布 ──────────────────────────────────────
fig, ax = plt.subplots(figsize=(8, 4))
for split in SPLITS:
    aspects = all_data[split]['aspects']
    aspects = aspects[(aspects > 0) & (aspects < 3)]
    ax.hist(aspects, bins=60, alpha=0.6, color=COLORS[split],
            label=split.capitalize(), edgecolor='white')

ax.axvline(1.0, color='black', linestyle='--', linewidth=1.2, label='Square (AR=1)')
ax.set_xlabel('Aspect Ratio (Width / Height)', fontsize=11)
ax.set_ylabel('Count', fontsize=11)
ax.set_title('Bounding Box Aspect Ratio Distribution', fontsize=13, fontweight='bold')
ax.legend(fontsize=10)
ax.grid(axis='y', alpha=0.3)
plt.tight_layout()
plt.savefig(SAVE_DIR / 'fig2_aspect_ratio_distribution.png', dpi=200, bbox_inches='tight')
plt.close()
print("✅ 图2 保存完成")

# ── 图3：每图实例数分布 ──────────────────────────────────
fig, ax = plt.subplots(figsize=(8, 4))
max_inst = max(all_data[s]['instances'].max() for s in SPLITS)
bins = np.arange(0, int(max_inst) + 2) - 0.5

for split in SPLITS:
    inst = all_data[split]['instances']
    ax.hist(inst, bins=bins, alpha=0.6, color=COLORS[split],
            label=f"{split.capitalize()} (mean={inst.mean():.1f})",
            edgecolor='white')

ax.set_xlabel('Instances per Image', fontsize=11)
ax.set_ylabel('Count', fontsize=11)
ax.set_title('Number of Victim Instances per Image', fontsize=13, fontweight='bold')
ax.set_xticks(range(0, int(max_inst) + 2))
ax.legend(fontsize=10)
ax.grid(axis='y', alpha=0.3)
plt.tight_layout()
plt.savefig(SAVE_DIR / 'fig3_instances_per_image.png', dpi=200, bbox_inches='tight')
plt.close()
print("✅ 图3 保存完成")

# ── 图4：小目标 vs 正常目标比例饼图 ─────────────────────
fig, axes = plt.subplots(1, 3, figsize=(12, 4))
fig.suptitle('Small Target vs Normal Target Distribution', fontsize=13, fontweight='bold')

for ax, split in zip(axes, SPLITS):
    areas = all_data[split]['areas']
    small = (areas < 1.0).sum()
    normal = (areas >= 1.0).sum()
    ax.pie(
        [small, normal],
        labels=[f'Small\n(<1%)\n{small/len(areas)*100:.1f}%',
                f'Normal\n(≥1%)\n{normal/len(areas)*100:.1f}%'],
        colors=['#E53E3E', '#3182CE'],
        startangle=90,
        textprops={'fontsize': 10},
        wedgeprops={'edgecolor': 'white', 'linewidth': 1.5}
    )
    ax.set_title(split.capitalize(), fontsize=11)

plt.tight_layout()
plt.savefig(SAVE_DIR / 'fig4_small_target_ratio.png', dpi=200, bbox_inches='tight')
plt.close()
print("✅ 图4 保存完成")

# ── 图5：综合统计汇总表（直接输出论文用数据）────────────
print("\n" + "=" * 55)
print("论文用统计数据汇总")
print("=" * 55)
print(f"{'指标':<25} {'Train':>10} {'Val':>10} {'Test':>10}")
print("-" * 55)

metrics = [
    ('Total instances',      lambda d: len(d['areas'])),
    ('Avg instances/image',  lambda d: round(d['instances'].mean(), 2)),
    ('Median BBox area (%)', lambda d: round(np.median(d['areas']), 3)),
    ('P10 BBox area (%)',    lambda d: round(np.percentile(d['areas'], 10), 3)),
    ('P90 BBox area (%)',    lambda d: round(np.percentile(d['areas'], 90), 3)),
    ('Small target ratio(%)',lambda d: round((d['areas'] < 1.0).mean()*100, 1)),
    ('Mean aspect ratio',    lambda d: round(d['aspects'].mean(), 3)),
]

for name, fn in metrics:
    vals = [fn(all_data[s]) for s in SPLITS]
    print(f"{name:<25} {vals[0]:>10} {vals[1]:>10} {vals[2]:>10}")

print(f"\n所有图表已保存至: {SAVE_DIR}")
# import re
# import random
# import shutil
# from pathlib import Path
# from PIL import Image, ImageDraw, ImageFont
# import matplotlib.pyplot as plt
# import matplotlib as mpl
# import matplotlib.gridspec as gridspec
#
# mpl.rcParams['font.family'] = 'Times New Roman'
#
# # ── 配置路径 ──────────────────────────────────────
# VIS_DIR  = Path('D:/Fire_Project/FireDataset_new/train/Labels_vis')
# OUT_DIR  = Path('D:/Fire_Project/annotation_vis_samples2')
# OUT_DIR.mkdir(exist_ok=True)
#
# random.seed(42)
#
# # ── 第一步：按类别挑选代表性样本 ─────────────────
# # 每个类别的关键词 → 显示标题
# CATEGORIES = {
#     'Bedroom\n(Horizontal)':  r'bedroom_.*horlook',
#     'Bedroom\n(Overhead)':    r'bedroom_.*overlook',
#     'Kitchen\n(Horizontal)':  r'kitchen_.*horlook',
#     'Kitchen\n(Overhead)':    r'kitchen_.*overlook',
#     'Corridor\n(Horizontal)': r'corridor_.*horlook',
#     'Corridor\n(Overhead)':   r'corridor_.*overlook',
#     'Crawling\nPose':         r'.*crawling.*',
#     'Fall Flat\nPose':        r'.*fall_flat.*',
# }
#
# all_vis = list(VIS_DIR.glob('*.png'))
# selected = {}  # label -> Path
#
# for label, pattern in CATEGORIES.items():
#     matches = [f for f in all_vis if re.search(pattern, f.name, re.IGNORECASE)]
#     # 优先选有bbox的图（文件大小>50KB通常有内容）
#     valid = [f for f in matches if f.stat().st_size > 30 * 1024]
#     pool = valid if valid else matches
#     if pool:
#         selected[label] = random.choice(pool)
#         print(f"✅ {label.replace(chr(10),' ')}: {selected[label].name}")
#     else:
#         print(f"⚠️  未找到: {label.replace(chr(10),' ')}")
#
# if not selected:
#     print("❌ 未找到任何图片，请检查VIS_DIR路径")
#     exit()
#
# # ── 第二步：拼接为 4×2 网格图 ────────────────────
# labels = list(selected.keys())
# paths  = list(selected.values())
# n      = len(labels)
# ncols  = 4
# nrows  = (n + ncols - 1) // ncols
#
# fig, axes = plt.subplots(nrows, ncols,
#                          figsize=(ncols * 4, nrows * 3.2))
# axes = axes.flatten()
#
# for i, (label, img_path) in enumerate(zip(labels, paths)):
#     img = Image.open(img_path).convert('RGB')
#
#     # 等比缩放到固定高度，避免图片比例失真
#     target_h = 400
#     ratio = target_h / img.height
#     new_w = int(img.width * ratio)
#     img = img.resize((new_w, target_h), Image.LANCZOS)
#
#     axes[i].imshow(img)
#     axes[i].set_title(label, fontsize=11,
#                       fontfamily='Times New Roman', pad=6)
#     axes[i].axis('off')
#
# # 隐藏多余的子图格
# for j in range(i + 1, len(axes)):
#     axes[j].axis('off')
#
# fig.suptitle('Representative Annotation Visualization',
#              fontsize=14, fontweight='bold',
#              fontfamily='Times New Roman', y=1.01)
#
# plt.tight_layout(pad=1.0, h_pad=1.5, w_pad=0.5)
#
# out_path = OUT_DIR / 'annotation_visualization_grid.png'
# plt.savefig(out_path, dpi=200, bbox_inches='tight',
#             facecolor='white')
# plt.close()
#
# print(f"\n✅ 拼接图已保存至: {out_path}")