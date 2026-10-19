# import os
# from pathlib import Path
#
# # ==========================================
# # ✅ 配置区域：只需要修改这里
# # ==========================================
#
# DATASET_DIR = r"D:/Fire_Project/dataset"  # 数据集根目录
# SUB_FOLDERS = ["RGB", "IR", "Depth", "Labels", "Labels_vis"]
#
# # 需要重命名的主文件夹
# # 格式：("原名", "新名")
# RENAME_TASKS = [
#     ("diningoom_cat_cat_route1_horlook", "diningroom_cat_cat_route1_horlook"),
#     ("diningoom_cat_cat_route1_overlook", "diningroom_cat_cat_route1_overlook"),
#     ("diningoom_cat_cat_route1_overlook2", "diningroom_cat_cat_route1_overlook2"),
#     ("diningoom_cat_route1_child_fall_flat_horlook", "diningroom_cat_route1_child_fall_flat_horlook"),
#     ("diningoom_cat_route1_child_fall_flat_overlook", "diningroom_cat_route1_child_fall_flat_overlook"),
#     # 继续添加
#     ("diningoom_child_fall_flat_horlook", "diningroom_child_fall_flat_horlook"),
#     ("diningoom_child_fall_flat_overlook", "diningroom_child_fall_flat_overlook"),
#     ("diningoom_child_fall_flat_overlook2", "diningroom_child_fall_flat_overlook2"),
#     ("diningoom_dog_route1_man_injured_walk_backwards_horlook", "diningroom_dog_route1_man_injured_walk_backwards_horlook"),
#     ("diningoom_dog_route1_man_injured_walk_backwards_overlook", "diningroom_dog_route1_man_injured_walk_backwards_overlook"),
#     ("diningoom_dog_route1_man_injured_walk_backwards_overlook2", "diningroom_dog_route1_man_injured_walk_backwards_overlook2"),
# ]
#
# # ==========================================
# # 重命名逻辑
# # ==========================================
#
# def rename_folder(dataset_dir, old_name, new_name):
#     old_path = Path(dataset_dir) / old_name
#     new_path = Path(dataset_dir) / new_name
#
#     print(f"\n{'='*60}")
#     print(f"📂 处理: {old_name} → {new_name}")
#
#     # 检查原文件夹是否存在
#     if not old_path.exists():
#         print(f"  ❌ 原文件夹不存在: {old_path}")
#         return False
#
#     # 检查新名字是否已存在
#     if new_path.exists():
#         print(f"  ❌ 新文件夹名已存在: {new_path}")
#         return False
#
#     # ==========================================
#     # 第一步：重命名子文件夹中的文件
#     # ==========================================
#     print(f"  🔄 第一步：重命名子文件夹中的文件...")
#
#     total_renamed  = 0
#     total_skipped  = 0
#     total_errors   = 0
#     sub_stats      = {}
#
#     for sub in SUB_FOLDERS:
#         sub_path = old_path / sub
#         if not sub_path.exists():
#             print(f"  ⚠️ 子文件夹不存在，跳过: {sub}")
#             continue
#
#         files = list(sub_path.iterdir())
#         renamed  = 0
#         skipped  = 0
#         errors   = 0
#
#         for file in files:
#             if not file.is_file():
#                 continue
#
#             old_filename = file.name
#             ext          = file.suffix
#
#             # 判断文件名是否以旧前缀开头
#             if old_filename.startswith(old_name):
#                 # 替换前缀
#                 suffix       = old_filename[len(old_name):]  # 保留前缀后面的部分
#                 new_filename = new_name + suffix
#                 new_file     = sub_path / new_filename
#
#                 try:
#                     file.rename(new_file)
#                     renamed += 1
#                 except Exception as e:
#                     print(f"    ❌ 重命名失败: {old_filename} → {new_filename}: {e}")
#                     errors += 1
#             else:
#                 skipped += 1
#                 print(f"  ⚠️ 文件名不匹配，跳过: {old_filename}")
#
#         sub_stats[sub]  = {"renamed": renamed, "skipped": skipped, "errors": errors}
#         total_renamed  += renamed
#         total_skipped  += skipped
#         total_errors   += errors
#         print(f"  ✅ {sub}/: 重命名 {renamed} 个，跳过 {skipped} 个，错误 {errors} 个")
#
#     # ==========================================
#     # 第二步：重命名主文件夹
#     # ==========================================
#     print(f"\n  🔄 第二步：重命名主文件夹...")
#     try:
#         old_path.rename(new_path)
#         print(f"  ✅ 主文件夹重命名成功: {old_name} → {new_name}")
#     except Exception as e:
#         print(f"  ❌ 主文件夹重命名失败: {e}")
#         return False
#
#     # ==========================================
#     # 第三步：验证
#     # ==========================================
#     print(f"\n  🔍 第三步：验证结果...")
#     all_ok = True
#
#     for sub in SUB_FOLDERS:
#         sub_path = new_path / sub
#         if not sub_path.exists():
#             continue
#
#         files = list(sub_path.iterdir())
#         wrong_files = [f.name for f in files
#                        if f.is_file() and not f.name.startswith(new_name)]
#
#         if wrong_files:
#             print(f"  ❌ {sub}/ 中有文件前缀不正确:")
#             for wf in wrong_files:
#                 print(f"      {wf}")
#             all_ok = False
#         else:
#             print(f"  ✅ {sub}/ 验证通过，共 {len(files)} 个文件")
#
#     if all_ok:
#         print(f"\n  🎉 全部完成且验证通过！")
#         print(f"  📊 总计重命名: {total_renamed} 个文件")
#     else:
#         print(f"\n  ⚠️ 验证发现问题，请检查上方错误信息")
#
#     return all_ok
#
#
# # ==========================================
# # 执行所有重命名任务
# # ==========================================
#
# print(f"🚀 开始批量重命名")
# print(f"📂 数据集目录: {DATASET_DIR}")
# print(f"📋 共 {len(RENAME_TASKS)} 个重命名任务")
#
# success_count = 0
# fail_count    = 0
#
# for old_name, new_name in RENAME_TASKS:
#     result = rename_folder(DATASET_DIR, old_name, new_name)
#     if result:
#         success_count += 1
#     else:
#         fail_count += 1
#
# print(f"\n{'='*60}")
# print(f"🎉 批量重命名完成！成功: {success_count}  失败: {fail_count}")

import os
from pathlib import Path

# ==========================================
# ✅ 配置区域
# ==========================================

DATASET_DIR = r"D:/Fire_Project/dataset"
SUB_FOLDERS = ["RGB", "IR", "Depth", "Labels", "Labels_vis"]

OLD_WORD = "restaurant"
NEW_WORD = "diningroom"

# ==========================================
# 执行替换
# ==========================================

dataset_path  = Path(DATASET_DIR)
scene_folders = sorted([f for f in dataset_path.iterdir() if f.is_dir()])

# 筛选出含有 diningroom 的主文件夹
target_folders = [f for f in scene_folders if OLD_WORD in f.name]

print(f"🚀 开始批量替换: {OLD_WORD} → {NEW_WORD}")
print(f"📂 数据集目录: {DATASET_DIR}")
print(f"✅ 找到 {len(target_folders)} 个含有 '{OLD_WORD}' 的主文件夹")
print(f"{'='*60}")

total_folder_renamed = 0
total_file_renamed   = 0
total_errors         = 0

for old_folder in target_folders:
    old_name = old_folder.name
    new_name = old_name.replace(OLD_WORD, NEW_WORD)
    new_folder = dataset_path / new_name

    print(f"\n📂 {old_name} → {new_name}")

    # ==========================================
    # 第一步：重命名子文件夹中的文件
    # ==========================================
    file_renamed = 0
    file_errors  = 0

    for sub in SUB_FOLDERS:
        sub_path = old_folder / sub
        if not sub_path.exists():
            continue

        files = [f for f in sub_path.iterdir() if f.is_file()]
        sub_renamed = 0

        for file in files:
            if OLD_WORD in file.name:
                new_filename = file.name.replace(OLD_WORD, NEW_WORD)
                new_file     = sub_path / new_filename
                try:
                    file.rename(new_file)
                    sub_renamed  += 1
                    file_renamed += 1
                except Exception as e:
                    print(f"  ❌ 文件重命名失败: {file.name}: {e}")
                    file_errors += 1

        if sub_renamed > 0:
            print(f"  ✅ {sub}/: 重命名 {sub_renamed} 个文件")

    # ==========================================
    # 第二步：重命名主文件夹
    # ==========================================
    try:
        old_folder.rename(new_folder)
        print(f"  ✅ 主文件夹重命名成功")
        total_folder_renamed += 1
    except Exception as e:
        print(f"  ❌ 主文件夹重命名失败: {e}")
        total_errors += 1
        continue

    # ==========================================
    # 第三步：验证
    # ==========================================
    all_ok = True
    for sub in SUB_FOLDERS:
        sub_path = new_folder / sub
        if not sub_path.exists():
            continue
        wrong = [f.name for f in sub_path.iterdir()
                 if f.is_file() and OLD_WORD in f.name]
        if wrong:
            print(f"  ❌ {sub}/ 仍有未替换的文件:")
            for w in wrong:
                print(f"      {w}")
            all_ok = False

    if all_ok:
        print(f"  ✅ 验证通过，共重命名 {file_renamed} 个文件")
    else:
        print(f"  ⚠️ 验证发现问题，请检查上方错误")

    total_file_renamed += file_renamed
    total_errors       += file_errors

# ==========================================
# 验证是否还有残留的 diningroom
# ==========================================
print(f"\n{'='*60}")
print(f"🔍 全局验证：检查是否还有残留的 '{OLD_WORD}'...")

remaining = [f.name for f in dataset_path.iterdir()
             if f.is_dir() and OLD_WORD in f.name]

if remaining:
    print(f"  ⚠️ 仍有 {len(remaining)} 个文件夹未替换:")
    for r in remaining:
        print(f"    {r}")
else:
    print(f"  ✅ 无残留，全部替换完成！")

print(f"\n{'='*60}")
print(f"🎉 批量替换完成！")
print(f"  主文件夹重命名: {total_folder_renamed} 个")
print(f"  文件重命名:     {total_file_renamed} 个")
print(f"  错误:           {total_errors} 个")