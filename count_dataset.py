# # import os
# # from pathlib import Path
# # from collections import defaultdict
# #
# # # ==========================================
# # # ✅ 配置区域
# # # ==========================================
# #
# # DATASET_DIR = r"D:/Fire_Project/dataset"
# #
# # # 关键词分类
# # SCENES  = ["kitchen", "bedroom", "diningoom", "diningroom", "corridor", "resturant", "office"]
# # PERSONS = ["child", "woman", "worker", "elder", "man"]
# # ANIMALS = ["dog", "cat", "pet"]
# # VIEWS   = ["horlook", "overlook2", "overlook1", "overlook"]  # overlook2/1 要在overlook前面，避免误匹配
# #
# # # ==========================================
# # # 统计
# # # ==========================================
# #
# # dataset_path  = Path(DATASET_DIR)
# # scene_folders = sorted([f for f in dataset_path.iterdir() if f.is_dir()])
# #
# # print(f"📂 数据集目录: {DATASET_DIR}")
# # print(f"✅ 找到 {len(scene_folders)} 个主文件夹")
# # print(f"{'='*60}")
# #
# # # 统计维度
# # scene_count   = defaultdict(int)
# # person_count  = defaultdict(int)
# # animal_count  = defaultdict(int)
# # view_count    = defaultdict(int)
# #
# # # 组合统计
# # scene_person  = defaultdict(int)
# # scene_animal  = defaultdict(int)
# # scene_view    = defaultdict(int)
# # person_view   = defaultdict(int)
# #
# # total_rgb     = 0
# # total_labeled = 0
# #
# # def match_keywords(name, keywords):
# #     """返回文件名中匹配到的所有关键词"""
# #     matched = []
# #     for kw in keywords:
# #         if kw in name:
# #             matched.append(kw)
# #     return matched if matched else ["none"]
# #
# # for scene_folder in scene_folders:
# #     rgb_dir    = scene_folder / "RGB"
# #     labels_dir = scene_folder / "Labels"
# #
# #     if not rgb_dir.exists() or not labels_dir.exists():
# #         continue
# #
# #     rgb_files = [f for f in rgb_dir.iterdir()
# #                  if f.suffix.lower() in ['.png', '.jpg', '.jpeg']]
# #
# #     for rgb_file in rgb_files:
# #         total_rgb += 1
# #
# #         # 检查是否有标注
# #         stem = rgb_file.stem
# #         if stem.endswith('_'):
# #             base_stem = stem[:-1]
# #         else:
# #             base_stem = stem
# #
# #         label_file = labels_dir / f"{base_stem}.txt"
# #         if not label_file.exists():
# #             continue
# #         with open(label_file, 'r') as f:
# #             lines = [l.strip() for l in f.readlines() if l.strip()]
# #         if not lines:
# #             continue
# #
# #         total_labeled += 1
# #         name = stem.lower()  # 统一小写匹配
# #
# #         # 匹配关键词
# #         scenes  = match_keywords(name, SCENES)
# #         persons = match_keywords(name, PERSONS)
# #         animals = match_keywords(name, ANIMALS)
# #         views   = match_keywords(name, VIEWS)
# #
# #         # 累计（每个文件只取第一个匹配的关键词）
# #         scene  = scenes[0]
# #         person = persons[0]
# #         animal = animals[0]
# #         view   = views[0]
# #
# #         scene_count[scene]                        += 1
# #         person_count[person]                      += 1
# #         animal_count[animal]                      += 1
# #         view_count[view]                          += 1
# #         scene_person[f"{scene} + {person}"]       += 1
# #         scene_animal[f"{scene} + {animal}"]       += 1
# #         scene_view[f"{scene} + {view}"]           += 1
# #         person_view[f"{person} + {view}"]         += 1
# #
# # # ==========================================
# # # 输出结果
# # # ==========================================
# #
# # def print_section(title, data):
# #     print(f"\n{'='*60}")
# #     print(f"📊 {title}")
# #     print(f"{'─'*60}")
# #     items = sorted(data.items(), key=lambda x: -x[1])
# #     max_v = max(data.values()) if data else 1
# #     for k, v in items:
# #         bar = '█' * int(v / max_v * 20)
# #         print(f"  {k:<45} {v:>5} 张  {bar}")
# #     print(f"  {'─'*55}")
# #     print(f"  {'合计':<45} {sum(data.values()):>5} 张")
# #
# # print_section("按场景统计",      scene_count)
# # print_section("按人物统计",      person_count)
# # print_section("按动物统计",      animal_count)
# # print_section("按视角统计",      view_count)
# # print_section("场景 × 人物",     scene_person)
# # print_section("场景 × 动物",     scene_animal)
# # print_section("场景 × 视角",     scene_view)
# # print_section("人物 × 视角",     person_view)
# #
# # print(f"\n{'='*60}")
# # print(f"📊 总体统计")
# # print(f"{'─'*60}")
# # print(f"  RGB总数:            {total_rgb}")
# # print(f"  有标注RGB数量:      {total_labeled}")
# # print(f"  无标注RGB数量:      {total_rgb - total_labeled}")
# # if total_rgb > 0:
# #     print(f"  标注覆盖率:         {total_labeled / total_rgb * 100:.1f}%")
# # print(f"  场景种类:           {[k for k in scene_count if k != 'none']}")
# # print(f"  人物种类:           {[k for k in person_count if k != 'none']}")
# # print(f"  动物种类:           {[k for k in animal_count if k != 'none']}")
# # print(f"  视角种类:           {[k for k in view_count if k != 'none']}")
#
# import os
# from pathlib import Path
# from collections import defaultdict
#
# # ==========================================
# # ✅ 配置区域
# # ==========================================
#
# DATASET_DIR = r"D:/Fire_Project/dataset"
#
# # 关键词分类
# SCENES  = ["kitchen", "bedroom", "diningoom", "diningroom", "livingroom", "corridor", "resturant", "office"]
# PERSONS = ["child", "woman", "worker", "elder", "man"]
# ANIMALS = ["dog", "cat", "pet"]
# VIEWS   = ["horlook", "overlook2", "overlook1", "overlook"]
#
# # ==========================================
# # 统计
# # ==========================================
#
# dataset_path  = Path(DATASET_DIR)
# scene_folders = sorted([f for f in dataset_path.iterdir() if f.is_dir()])
#
# print(f"📂 数据集目录: {DATASET_DIR}")
# print(f"✅ 找到 {len(scene_folders)} 个主文件夹")
# print(f"{'='*60}")
#
# # 统计维度
# scene_count   = defaultdict(int)
# person_count  = defaultdict(int)
# animal_count  = defaultdict(int)
# view_count    = defaultdict(int)
#
# # 组合统计
# scene_person  = defaultdict(int)
# scene_animal  = defaultdict(int)
# scene_view    = defaultdict(int)
# person_view   = defaultdict(int)
#
# total_rgb        = 0   # RGB总数
# total_valid      = 0   # 有对应txt的RGB（有效帧）
# total_labeled    = 0   # txt非空（有人物标注）
# total_unlabeled  = 0   # txt为空（人物不在画面内）
#
# def match_keywords(name, keywords):
#     matched = []
#     for kw in keywords:
#         if kw in name:
#             matched.append(kw)
#     return matched if matched else ["none"]
#
# for scene_folder in scene_folders:
#     rgb_dir    = scene_folder / "RGB"
#     labels_dir = scene_folder / "Labels"
#
#     if not rgb_dir.exists() or not labels_dir.exists():
#         continue
#
#     rgb_files = [f for f in rgb_dir.iterdir()
#                  if f.suffix.lower() in ['.png', '.jpg', '.jpeg']]
#
#     for rgb_file in rgb_files:
#         total_rgb += 1
#
#         stem = rgb_file.stem
#         if stem.endswith('_'):
#             base_stem = stem[:-1]
#         else:
#             base_stem = stem
#
#         # txt存在即为有效帧
#         label_file = labels_dir / f"{base_stem}.txt"
#         if not label_file.exists():
#             continue
#
#         total_valid += 1
#
#         # 检查txt是否有标注内容
#         with open(label_file, 'r') as f:
#             lines = [l.strip() for l in f.readlines() if l.strip()]
#
#         has_label = len(lines) > 0
#         if has_label:
#             total_labeled += 1
#         else:
#             total_unlabeled += 1
#
#         # 关键词匹配（所有有效帧都统计场景/视角等）
#         name = stem.lower()
#
#         scenes  = match_keywords(name, SCENES)
#         persons = match_keywords(name, PERSONS)
#         animals = match_keywords(name, ANIMALS)
#         views   = match_keywords(name, VIEWS)
#
#         scene  = scenes[0]
#         person = persons[0]
#         animal = animals[0]
#         view   = views[0]
#
#         scene_count[scene]                  += 1
#         view_count[view]                    += 1
#         scene_view[f"{scene} + {view}"]     += 1
#
#         # 人物和动物只统计有标注的帧
#         if has_label:
#             person_count[person]                      += 1
#             animal_count[animal]                      += 1
#             scene_person[f"{scene} + {person}"]       += 1
#             scene_animal[f"{scene} + {animal}"]       += 1
#             person_view[f"{person} + {view}"]         += 1
#
# # ==========================================
# # 输出结果
# # ==========================================
#
# def print_section(title, data, note=""):
#     print(f"\n{'='*60}")
#     print(f"📊 {title}{note}")
#     print(f"{'─'*60}")
#     if not data:
#         print(f"  （无数据）")
#         return
#     items = sorted(data.items(), key=lambda x: -x[1])
#     max_v = max(data.values()) if data else 1
#     for k, v in items:
#         bar = '█' * int(v / max_v * 20)
#         print(f"  {k:<45} {v:>5} 张  {bar}")
#     print(f"  {'─'*55}")
#     print(f"  {'合计':<45} {sum(data.values()):>5} 张")
#
# print_section("按场景统计（所有有效帧）",  scene_count)
# print_section("按视角统计（所有有效帧）",  view_count)
# print_section("按人物统计",               person_count, "（仅有标注帧）")
# print_section("按动物统计",               animal_count, "（仅有标注帧）")
# print_section("场景 × 人物",              scene_person, "（仅有标注帧）")
# print_section("场景 × 动物",              scene_animal, "（仅有标注帧）")
# print_section("场景 × 视角",              scene_view,   "（所有有效帧）")
# print_section("人物 × 视角",              person_view,  "（仅有标注帧）")
#
# print(f"\n{'='*60}")
# print(f"📊 总体统计")
# print(f"{'─'*60}")
# print(f"  RGB总数:                {total_rgb}")
# print(f"  有效帧（txt存在）:      {total_valid}")
# print(f"  有人物标注帧:           {total_labeled}")
# print(f"  无人物标注帧（空txt）:  {total_unlabeled}")
# print(f"  无txt帧:                {total_rgb - total_valid}")
# if total_valid > 0:
#     print(f"  标注覆盖率:             {total_labeled / total_valid * 100:.1f}%")
# print(f"\n  场景种类: {sorted([k for k in scene_count if k != 'none'])}")
# print(f"  人物种类: {sorted([k for k in person_count if k != 'none'])}")
# print(f"  动物种类: {sorted([k for k in animal_count if k != 'none'])}")
# print(f"  视角种类: {sorted([k for k in view_count if k != 'none'])}")
import os
from pathlib import Path
from collections import defaultdict

# ==========================================
# ✅ 配置区域
# ==========================================

DATASET_DIR = r"D:/Fire_Project/dataset"

# 关键词分类（顺序敏感，长词放前面避免误匹配）
SCENES  = ["kitchen", "bedroom", "livingroom", "diningroom", "corridor", "resturant", "office"]
PERSONS = ["child", "woman", "worker", "elder", "man"]  # woman 在 man 前
ANIMALS = ["dog", "cat", "pet"]
VIEWS   = ["overlook2", "overlook1", "overlook", "horlook"]  # overlook2/1 在 overlook 前

# ==========================================
# 工具函数
# ==========================================

def match_first(name, keywords):
    """返回文件名中第一个匹配的关键词，没有则返回 none"""
    for kw in keywords:
        if kw in name:
            return kw
    return "none"

def print_section(title, data, total, note=""):
    print(f"\n{'='*65}")
    print(f"📊 {title}{note}")
    print(f"{'─'*65}")
    if not data:
        print(f"  （无数据）")
        return
    items = sorted(data.items(), key=lambda x: -x[1])
    max_v = max(data.values()) if data else 1
    for k, v in items:
        pct = v / total * 100 if total > 0 else 0
        bar = '█' * int(v / max_v * 20)
        print(f"  {k:<40} {v:>6} 张  {pct:>5.1f}%  {bar}")
    print(f"  {'─'*60}")
    print(f"  {'合计':<40} {sum(data.values()):>6} 张  100.0%")

# ==========================================
# 收集数据
# ==========================================

dataset_path  = Path(DATASET_DIR)
scene_folders = sorted([f for f in dataset_path.iterdir() if f.is_dir()])

print(f"📂 数据集目录: {DATASET_DIR}")
print(f"✅ 找到 {len(scene_folders)} 个主文件夹")

# 统计维度
scene_count  = defaultdict(int)
person_count = defaultdict(int)
animal_count = defaultdict(int)
view_count   = defaultdict(int)

# 组合统计
scene_person = defaultdict(int)
scene_animal = defaultdict(int)
scene_view   = defaultdict(int)
person_view  = defaultdict(int)

total_rgb       = 0   # RGB总数
total_valid     = 0   # 有对应txt的RGB（有效帧）
total_labeled   = 0   # txt非空（有人物标注）
total_unlabeled = 0   # txt为空（人物不在画面内）
total_no_txt    = 0   # 无对应txt

for scene_folder in scene_folders:
    rgb_dir    = scene_folder / "RGB"
    labels_dir = scene_folder / "Labels"

    if not rgb_dir.exists():
        continue

    rgb_files = sorted([f for f in rgb_dir.iterdir()
                        if f.suffix.lower() in ['.png', '.jpg', '.jpeg']])

    for rgb_file in rgb_files:
        total_rgb += 1

        stem = rgb_file.stem
        if stem.endswith('_'):
            base_stem = stem[:-1]
        else:
            base_stem = stem

        # 检查 txt 是否存在
        label_file = labels_dir / f"{base_stem}.txt" if labels_dir.exists() else None
        if label_file is None or not label_file.exists():
            total_no_txt += 1
            continue

        total_valid += 1

        # 检查 txt 是否非空
        with open(label_file, 'r', encoding='utf-8') as f:
            lines = [l.strip() for l in f.readlines() if l.strip()]

        has_label = len(lines) > 0
        if has_label:
            total_labeled += 1
        else:
            total_unlabeled += 1

        # 关键词匹配
        name   = base_stem.lower()
        scene  = match_first(name, SCENES)
        person = match_first(name, PERSONS)
        animal = match_first(name, ANIMALS)
        view   = match_first(name, VIEWS)

        # 所有有效帧统计场景和视角
        scene_count[scene]              += 1
        view_count[view]                += 1
        scene_view[f"{scene}|{view}"]   += 1

        # 有标注帧统计人物和动物
        if has_label:
            person_count[person]                    += 1
            animal_count[animal]                    += 1
            scene_person[f"{scene}|{person}"]       += 1
            scene_animal[f"{scene}|{animal}"]       += 1
            person_view[f"{person}|{view}"]         += 1

# ==========================================
# 输出结果
# ==========================================

print_section("按场景统计",         scene_count,  total_valid,   "（所有有效帧）")
print_section("按视角统计",         view_count,   total_valid,   "（所有有效帧）")
print_section("按人物统计",         person_count, total_labeled, "（仅有标注帧）")
print_section("按动物统计",         animal_count, total_labeled, "（仅有标注帧）")
print_section("场景 × 人物",        scene_person, total_labeled, "（仅有标注帧）")
print_section("场景 × 动物",        scene_animal, total_labeled, "（仅有标注帧）")
print_section("场景 × 视角",        scene_view,   total_valid,   "（所有有效帧）")
print_section("人物 × 视角",        person_view,  total_labeled, "（仅有标注帧）")

# ==========================================
# 总体统计
# ==========================================

print(f"\n{'='*65}")
print(f"📊 总体统计")
print(f"{'─'*65}")
print(f"  {'RGB总数:':<35} {total_rgb:>6} 张  100.0%")
print(f"  {'有效帧（txt存在）:':<35} {total_valid:>6} 张  {total_valid/total_rgb*100:>5.1f}%")
print(f"  {'  ├─ 有人物标注（txt非空）:':<35} {total_labeled:>6} 张  {total_labeled/total_rgb*100:>5.1f}%")
print(f"  {'  └─ 无人物标注（txt为空）:':<35} {total_unlabeled:>6} 张  {total_unlabeled/total_rgb*100:>5.1f}%")
print(f"  {'无txt帧:':<35} {total_no_txt:>6} 张  {total_no_txt/total_rgb*100:>5.1f}%")

print(f"\n{'─'*65}")
print(f"  场景种类: {sorted([k for k in scene_count if k != 'none'])}")
print(f"  人物种类: {sorted([k for k in person_count if k != 'none'])}")
print(f"  动物种类: {sorted([k for k in animal_count if k != 'none'])}")
print(f"  视角种类: {sorted([k for k in view_count if k != 'none'])}")