import os
import re

# ==================== 配置区 ====================

# 指定要处理的小文件夹路径
TARGET_DIR = r"D:\Fire_Project\FireDataset\卧室\chacter2action2loc2horlook"

# 中文大文件夹名 → 英文映射
FOLDER_NAME_MAP = {
    "卧室": "bedroom",
    # "客厅": "living_room",
    # "厨房": "kitchen",
    # "浴室": "bathroom",
    # "办公室": "office",
}

# 小文件夹名拆分关键词
SPLIT_KEYWORDS = ["chacter", "action", "loc", "horlook", "overlook"]


# ==================== 工具函数 ====================

def split_subfolder_name(name: str) -> str:
    keywords_sorted = sorted(SPLIT_KEYWORDS, key=len, reverse=True)
    pattern = "(" + "|".join(re.escape(k) for k in keywords_sorted) + r")(\d*)"

    parts = re.split(pattern, name)
    tokens = []
    i = 0
    while i < len(parts):
        part = parts[i]
        if part == "":
            i += 1
            continue
        # 检查是否是关键词（下一个是数字部分）
        if i + 1 < len(parts) and re.fullmatch(r"\d*", parts[i + 1]):
            token = part + parts[i + 1]
            tokens.append(token)
            i += 2
        else:
            tokens.append(part)
            i += 1

    return "_".join(t for t in tokens if t)


def get_english_name(chinese_name: str) -> str:
    return FOLDER_NAME_MAP.get(chinese_name, chinese_name)


def rename_files_in_dir(file_dir: str, prefix: str, dry_run: bool = False):
    try:
        entries = os.listdir(file_dir)
    except PermissionError:
        print(f"  [跳过] 无权限访问: {file_dir}")
        return

    for filename in sorted(entries):
        filepath = os.path.join(file_dir, filename)
        if not os.path.isfile(filepath):
            continue

        if filename.startswith(prefix):
            print(f"    [跳过] 已有前缀: {filename}")
            continue

        new_filename = f"{prefix}{filename}"
        new_filepath = os.path.join(file_dir, new_filename)

        if dry_run:
            print(f"    [预览] {filename}  →  {new_filename}")
        else:
            os.rename(filepath, new_filepath)
            print(f"    [完成] {filename}  →  {new_filename}")


def process_single_small_folder(target_dir: str, dry_run: bool = False):
    """
    target_dir 结构：.../<大文件夹>/<小文件夹>
    自动从路径中提取大文件夹名和小文件夹名，处理其下所有子文件夹中的文件。
    """
    target_dir = os.path.normpath(target_dir)

    if not os.path.isdir(target_dir):
        print(f"错误：路径不存在：{target_dir}")
        return

    # 从路径自动提取大文件夹名和小文件夹名
    small_folder = os.path.basename(target_dir)
    big_folder = os.path.basename(os.path.dirname(target_dir))

    big_en = get_english_name(big_folder)
    small_en = split_subfolder_name(small_folder)
    prefix = f"{big_en}_{small_en}_"

    print(f"大文件夹: {big_folder} → {big_en}")
    print(f"小文件夹: {small_folder} → {small_en}")
    print(f"前缀:     {prefix}")
    print("-" * 50)

    # 遍历小文件夹下所有子文件夹（RGB、Depth 等）
    for sub_folder in sorted(os.listdir(target_dir)):
        sub_path = os.path.join(target_dir, sub_folder)
        if not os.path.isdir(sub_path):
            continue

        print(f"\n  [子文件夹] {sub_folder}")
        rename_files_in_dir(sub_path, prefix, dry_run=dry_run)


# ==================== 主程序 ====================

if __name__ == "__main__":
    print("=" * 60)
    print(f"目标路径: {TARGET_DIR}")
    print("=" * 60)

    print("\n>>> 预览模式（不会修改任何文件）\n")
    process_single_small_folder(TARGET_DIR, dry_run=True)

    print("\n" + "=" * 60)
    confirm = input("确认以上重命名操作？输入 yes 执行，其他键退出：").strip().lower()
    if confirm == "yes":
        print("\n>>> 正式执行重命名\n")
        process_single_small_folder(TARGET_DIR, dry_run=False)
        print("\n✅ 完成！")
    else:
        print("已取消，文件未做任何修改。")