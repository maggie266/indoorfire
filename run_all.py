import subprocess
import os
import json

# ==========================================
# ✅ 配置区域：只需要修改这里
# ==========================================

BLENDER_PATH = r"C:\Program Files\Blender Foundation\Blender 5.0\blender.exe"  # 改成你的Blender路径
SCRIPT_PATH  = r"D:/Fire_Project/scripts/render_task.py"
TASK_JSON    = r"D:/Fire_Project/scripts/current_task.json"
ROOT_DIR     = r"D:/Fire_Project/FireDataset/"

# 格式：
# "blend文件路径": {
#     "scene_name": "场景名",
#     "tasks": [
#         (角色, 动作, 位置, 视角, 摄像机名, 人物对象名, 生成数量, 起始序号),
#     ]
# }
ALL_TASKS = {
    # r"D:\Fire_Project\FireDataset\餐厅\位置1场景1.blend": {
    #     "scene_name": "restaurant",
    #     "tasks": [
    #         ("scene1", "loc1", "overlook",  "Camera", ["Ch46", "Ch22_Body", "Ch23_Belt","Ch22_Body.001", "Ch23_Belt.001", "Ch17_Body"], 30, 1),
    #         ("scene1", "loc1", "overlook1",  "摄像机.001", ["Ch46", "Ch22_Body", "Ch23_Belt","Ch22_Body.001", "Ch23_Belt.001", "Ch17_Body"], 30, 1),
    #         ("scene1", "loc1", "overlook2",  "摄像机", ["Ch46", "Ch22_Body", "Ch23_Belt","Ch22_Body.001", "Ch23_Belt.001", "Ch17_Body"], 30, 1),
    #         ("scene1", "loc1", "horlook",  "摄像机.002", ["Ch46", "Ch22_Body", "Ch23_Belt","Ch22_Body.001", "Ch23_Belt.001", "Ch17_Body"], 30, 1),
    #     ]
    # },
    # r"D:\Fire_Project\FireDataset\餐厅\位置2场景2.blend": {
    #     "scene_name": "restaurant",
    #     "tasks": [
    #         ("scene2", "loc2", "overlook", "Camera", ["Ch46", "Ch22_Body", "Ch23_Belt","Ch22_Body.001", "Ch23_Belt.001", "Ch17_Body", "Peasant_Man.001", "Ch17_Body.001", "Ch23_Belt.002","Ch22_Body.002"], 30, 1),
    #         ("scene2", "loc2", "overlook1", "摄像机.001",["Ch46", "Ch22_Body", "Ch23_Belt","Ch22_Body.001", "Ch23_Belt.001", "Ch17_Body", "Peasant_Man.001", "Ch17_Body.001", "Ch23_Belt.002","Ch22_Body.002"], 30, 1),
    #         ("scene2", "loc2", "overlook2", "摄像机", ["Ch46", "Ch22_Body", "Ch23_Belt","Ch22_Body.001", "Ch23_Belt.001", "Ch17_Body", "Peasant_Man.001", "Ch17_Body.001", "Ch23_Belt.002","Ch22_Body.002"], 30, 1),
    #         ("scene2", "loc2", "horlook", "摄像机.002",["Ch46", "Ch22_Body", "Ch23_Belt","Ch22_Body.001", "Ch23_Belt.001", "Ch17_Body", "Peasant_Man.001", "Ch17_Body.001", "Ch23_Belt.002","Ch22_Body.002"], 30, 1),
    #     ]
    # },
    # r"D:\Fire_Project\FireDataset\餐厅\位置3场景3.blend": {
    #     "scene_name": "restaurant",
    #     "tasks": [
    #         ("scene3", "loc3", "overlook",  "Camera", ["Ch46", "Ch22_Body", "Ch23_Belt", "Ch17_Body", "Ch17_Body.001", "Ch23_Belt.001", "Ch22_Body.001", "Peasant_Man"], 30, 1,1,250),
    #         ("scene3", "loc3", "overlook1",  "摄像机.001", ["Ch46", "Ch22_Body", "Ch23_Belt", "Ch17_Body", "Ch17_Body.001", "Ch23_Belt.001", "Ch22_Body.001", "Peasant_Man"], 30, 1,1,250),
    #         ("scene3", "loc3", "overlook2",  "摄像机", ["Ch46", "Ch22_Body", "Ch23_Belt", "Ch17_Body", "Ch17_Body.001", "Ch23_Belt.001", "Ch22_Body.001", "Peasant_Man"], 30, 1,1,250),
    #         ("scene3", "loc3", "horlook",  "摄像机.002", ["Ch46", "Ch22_Body", "Ch23_Belt", "Ch17_Body", "Ch17_Body.001", "Ch23_Belt.001", "Ch22_Body.001", "Peasant_Man"], 30, 1,1,250),
    #     ]
    # },
    # r"D:\Fire_Project\FireDataset\餐厅\位置4场景4.blend": {
    #     "scene_name": "restaurant",
    #     "tasks": [
    #         ("scene4", "loc4", "overlook",  "Camera", ["Ch46", "Peasant_Man", "Ch22_Body", "Ch46.001", "Ch22_Body.001", "Ch17_Body"], 30, 1),
    #         ("scene4", "loc4", "overlook1",  "摄像机.001", ["Ch46", "Peasant_Man", "Ch22_Body", "Ch46.001", "Ch22_Body.001", "Ch17_Body"], 30, 1),
    #         ("scene4", "loc4", "overlook2",  "摄像机", ["Ch46", "Peasant_Man", "Ch22_Body", "Ch46.001", "Ch22_Body.001", "Ch17_Body"], 30, 1),
    #         ("scene4", "loc4", "horlook",  "摄像机.002", ["Ch46", "Peasant_Man", "Ch22_Body", "Ch46.001", "Ch22_Body.001", "Ch17_Body"], 30, 1),
    #     ]
    # },
    # r"D:\Fire_Project\FireDataset\办公室\位置1场景1.blend": {
    #     "scene_name": "office",
    #     "tasks": [
    #         ("scene1", "loc1", "overlook",  "摄像机", ["Ch22_Body", "Ch22_Body.001", "Ch22_Body.002", "Ch23_Belt", "Ch23_Belt.001", "Ch22_Body.003","Ch17_Body", "Ch17_Body.001", "Ch23_Belt.002", "Ch22_Body.004"], 30, 1),
    #         ("scene1", "loc1", "overlook2",  "摄像机.001", ["Ch22_Body", "Ch22_Body.001", "Ch22_Body.002", "Ch23_Belt", "Ch23_Belt.001", "Ch22_Body.003","Ch17_Body", "Ch17_Body.001", "Ch23_Belt.002", "Ch22_Body.004"], 30, 1),
    #         ("scene1", "loc1", "horlook",  "摄像机.002", ["Ch22_Body", "Ch22_Body.001", "Ch22_Body.002", "Ch23_Belt", "Ch23_Belt.001", "Ch22_Body.003","Ch17_Body", "Ch17_Body.001", "Ch23_Belt.002", "Ch22_Body.004"], 30, 1),
    #     ]
    # },
    # r"D:\Fire_Project\FireDataset\办公室\位置2场景2.blend": {
    #     "scene_name": "office",
    #     "tasks": [
    #         ("scene2", "loc2", "overlook",  "摄像机", ["Ch22_Body", "Ch22_Body.001", "Ch17_Body"], 30, 1),
    #         ("scene2", "loc2", "overlook2",  "摄像机.001", ["Ch22_Body", "Ch22_Body.001", "Ch17_Body"], 30, 1),
    #         ("scene2", "loc2", "horlook",  "摄像机.002", ["Ch22_Body", "Ch22_Body.001", "Ch17_Body"], 30, 1),
    #     ]
    # # },
    # r"D:\Fire_Project\FireDataset\办公室\位置3场景3.blend": {
    #     "scene_name": "office",
    #     "tasks": [
    #         # ("scene3", "loc3", "overlook",  "摄像机", ["Ch22_Body", "Ch23_Belt", "Ch23_Belt.001","Ch22_Body.001", "Ch17_Body"], 30, 1),
    #         # ("scene3", "loc3", "overlook2",  "摄像机.001", ["Ch22_Body", "Ch23_Belt", "Ch23_Belt.001","Ch22_Body.001", "Ch17_Body"], 30, 1),
    #         ("scene3", "loc3", "horlook",  "摄像机.002", ["Ch22_Body", "Ch23_Belt", "Ch23_Belt.001","Ch22_Body.001", "Ch17_Body"], 30, 1,1,250),
    #     ]
    # },
    # r"D:\Fire_Project\FireDataset\厨房\cat_loc1.blend": {
    #     "scene_name": "kitchen",
    #     "tasks": [
    #         ("cat", "loc1", "overlook",  "摄像机", ["Ch22_Body", "Object_2"], 60, 1,1,250),
    #         ("cat", "loc1", "overlook2",  "摄像机.001", ["Ch22_Body", "Object_2"], 60, 1,1,250),
    #         ("cat", "loc1", "horlook",  "摄像机.002", ["Ch22_Body", "Object_2"], 60, 1,1,250),
    #     ]
    # },
    # r"D:\Fire_Project\FireDataset\厨房\cat_loc2.blend": {
    #     "scene_name": "kitchen",
    #     "tasks": [
    #         ("cat", "loc2", "overlook",  "摄像机", ["Ch23_Belt", "Object_7"], 60, 1,1,250),
    #         ("cat", "loc2", "overlook2",  "摄像机.001", ["Ch23_Belt", "Object_7"], 60, 1,1,250),
    #         ("cat", "loc2", "horlook",  "摄像机.002", ["Ch23_Belt", "Object_7"], 60, 1,1,250),
    #     ]
    # },
    # r"D:\Fire_Project\FireDataset\厨房\cat_elderly_loc1.blend": {
    #     "scene_name": "kitchen",
    #     "tasks": [
    #         ("cat", "elderly", "overlook",  "摄像机", ["Peasant_Man", "Object_7"], 60, 1,1,250),
    #         ("cat", "elderly", "overlook2",  "摄像机.001", ["Peasant_Man", "Object_7"], 60, 1,1,250),
    #         ("cat", "elderly", "horlook",  "摄像机.002", ["Peasant_Man", "Object_7"], 60, 1,1,250),
    #     ]
    # },

    r"D:\Fire_Project\FireDataset\客厅\pet2_elderly_loc1.blend": {
        "scene_name": "diningroom",
        "tasks": [
            # ("cat", "elderly", "overlook",  "Camera", ["Muchkin1", "Peasant_Man"], 60, 1,1,250),
            ("cat", "elderly", "horlook",  "摄像机", ["Muchkin1", "Peasant_Man"], 60, 1,1,250),
            ("cat", "elderly", "overlook2",  "摄像机.001", ["Muchkin1", "Peasant_Man"], 60, 1,1,250),
        ]
    },
    # r"D:\Fire_Project\FireDataset\客厅\sence1_位置2.blend": {
    #     "scene_name": "diningroom",
    #     "tasks": [
    #         ("sence1", "loc2", "overlook",  "Camera", ["Ch22_Body","Ch46","Ch23_Belt"], 30, 1,1,250),
    #         ("sence1", "loc2", "horlook",  "摄像机", ["Ch22_Body","Ch46","Ch23_Belt"], 30, 1,1,250),
    #         ("sence1", "loc2", "overlook2",  "摄像机.001", ["Ch22_Body","Ch46","Ch23_Belt"], 30, 1,1,250),
    #     ]
    # },
    r"D:\Fire_Project\FireDataset\卧室\cat_elderly_loc2.blend": {
        "scene_name": "bedroom",
        "tasks": [
            ("cat", "elderly", "overlook",  "Cameras", ["Peasant_Man", "Object_7"], 60, 1,1,250),
            ("cat", "elderly", "horlook",  "摄像机", ["Peasant_Man", "Object_7"], 60, 1,1,250),
            # ("pet", "loc2", "horlook",  "摄像机", ["Ch22_Body", "Object_7"], 30, 1,1,100),
        ]
    },
    r"D:\Fire_Project\FireDataset\卧室\dog_elderly_loc1.blend": {
        "scene_name": "bedroom",
        "tasks": [
            ("dog", "elderly", "overlook",  "Cameras", ["Peasant_Man", "mesh_0"], 60, 1,1,250),
            ("dog", "elderly", "horlook",  "摄像机", ["Peasant_Man", "mesh_0"], 60, 1,1,250),
            # ("pet", "loc3", "horlook",  "摄像机", ["Ch23_Belt", "Object_7"], 30, 1,1,100),
        ]
    },
    # r"D:\Fire_Project\FireDataset\走廊\2chacter_位置5.blend": {
    #     "scene_name": "hallway",
    #     "tasks": [
    #         # ("scene1", "loc5", "overlook",  "Camera", ["Peasant_Man", "Ch17_Body"], 30, 1,1,250),
    #         ("scene1", "loc5", "overlook2",  "摄像机", ["Peasant_Man", "Ch17_Body"], 30, 1,1,250),
    #         # ("scene1", "loc5", "horlook",  "摄像机.001", ["Peasant_Man", "Ch17_Body"], 30, 1,1,250),
    #     ]
    # },
    # r"D:\Fire_Project\FireDataset\走廊\cat_位置3.blend": {
    #     "scene_name": "hallway",
    #     "tasks": [
    #         # ("cat", "loc3", "overlook",  "Camera", ["Muchkin1"], 60, 1,1,250),
    #         ("cat", "loc3", "overlook2",  "摄像机", ["Muchkin1"], 60, 1,1,250),
    #         # ("cat", "loc3", "horlook",  "摄像机.001", ["Muchkin1"], 60, 1,1,250),
    #     ]
    # },
    # r"D:\Fire_Project\FireDataset\走廊\dog位置1.blend": {
    #     "scene_name": "hallway",
    #     "tasks": [
    #         ("dog", "loc1", "overlook2",  "摄像机", ["mesh_0","Ch22_Body"], 60, 1,1,250),
    #
    #     ]
    # },

    # r"D:\Fire_Project\FireDataset\客厅\sence1_位置2.blend": {
    #     "scene_name": "diningroom",
    #     "tasks": [
    #         ("chacter2","action2", "loc2", "horlook",  "摄像机", "Ch22_Body", 30, 1),
    #         ("chacter2","action2", "loc2", "overlook2",  "摄像机.001", "Ch22_Body", 30, 1),
    #         ("chacter2","action2", "loc2", "overlook",  "Camera", "Ch22_Body", 30, 1),
    #     ]
    # },
    # r"D:\Fire_Project\FireDataset\客厅\人物3动作3位置1.blend": {
    #     "scene_name": "diningroom",
    #     "tasks": [
    #         ("chacter3","action3", "loc1","horlook", "摄像机", "Ch23_Belt", 30, 1),
    #         ("chacter3","action3", "loc1","overlook2", "摄像机.001", "Ch23_Belt", 30, 1),
    #         ("chacter3","action3", "loc1","overlook", "Camera", "Ch23_Belt", 30, 1),
    #     ]
    # },
    # r"D:\Fire_Project\FireDataset\客厅\人物3动作3位置2.blend": {
    #     "scene_name": "diningroom",
    #     "tasks": [
    #         ("chacter3","action3", "loc2", "horlook", "摄像机", "Ch23_Belt", 30, 1),
    #         ("chacter3","action3", "loc2", "overlook2", "摄像机.001", "Ch23_Belt", 30, 1),
    #         ("chacter3","action3", "loc2", "overlook", "Camera", "Ch23_Belt", 30, 1),
    #     ]
    # },
}

# ==========================================
# 调度执行
# ==========================================
os.makedirs(ROOT_DIR, exist_ok=True)

total_blends = len(ALL_TASKS)
total_tasks  = sum(len(v["tasks"]) for v in ALL_TASKS.values())
print(f"🚀 共 {total_blends} 个场景，{total_tasks} 个组合，开始批量渲染")
print(f"{'='*60}")

success_count = 0
fail_count    = 0

for blend_idx, (blend_file, config) in enumerate(ALL_TASKS.items(), 1):

    blend_name = os.path.basename(blend_file)
    print(f"\n[{blend_idx}/{total_blends}] 📂 {blend_name}")
    print(f"  场景: {config['scene_name']}  组合数: {len(config['tasks'])}")

    # 检查blend文件是否存在
    if not os.path.exists(blend_file):
        print(f"  ❌ 文件不存在，跳过: {blend_file}")
        fail_count += 1
        continue

    # 把任务写入json传给渲染脚本
    with open(TASK_JSON, 'w', encoding='utf-8') as f:
        json.dump({
            "scene_name": config["scene_name"],
            "tasks": config["tasks"]
        }, f, ensure_ascii=False, indent=2)

    # 调用Blender后台执行
    cmd = [
        BLENDER_PATH,
        "--background",
        blend_file,
        "--python", SCRIPT_PATH
    ]

    print(f"  ⏳ 渲染中...")
    result = subprocess.run(cmd)

    if result.returncode == 0:
        print(f"  ✅ 完成: {blend_name}")
        success_count += 1
    else:
        print(f"  ❌ 失败: {blend_name}（returncode={result.returncode}）")
        fail_count += 1

    # 检查全局停止信号
    stop_file = os.path.join(ROOT_DIR, "STOP.txt")
    if os.path.exists(stop_file):
        print(f"\n⚠️ 检测到停止信号，中止批处理")
        break

print(f"\n{'='*60}")
print(f"🎉 批处理完成！成功: {success_count}  失败: {fail_count}")
print(f"📁 输出目录: {ROOT_DIR}")
# "tasks": [
#             ("chacter1", "action1", "loc1", "overlook",  "Camera", "Ch22_Body", 30, 1),
#             ("chacter1", "action1", "loc1", "horlook",  "摄像机.001", "Ch22_Body", 30, 1),
#             ("chacter1", "action1", "loc1", "overlook2",  "摄像机", "Ch22_Body", 30, 1),
#         ]
#     },
#     r"D:\Fire_Project\FireDataset\走廊\人物2动作2位置2.blend": {
#         "scene_name": "hallway",
#         "tasks": [
#             ("chacter2", "action2", "loc2", "overlook",  "Camera", "Ch23_Belt", 30, 1),
#             ("chacter2", "action2", "loc2", "horlook",  "摄像机.001", "Ch23_Belt", 30, 1),
#             ("chacter2", "action2", "loc2", "overlook2",  "摄像机", "Ch23_Belt", 30, 1),
#         ]
#     },
#     r"D:\Fire_Project\FireDataset\走廊\人物3动作3位置3.blend": {
#         "scene_name": "hallway",
#         "tasks": [
#             ("chacter3", "action3", "loc3", "overlook",  "Camera", "Ch17_Pants", 30, 1),
#             ("chacter3", "action3", "loc3", "horlook",  "摄像机.001", "Ch17_Pants", 30, 1),
#             ("chacter3", "action3", "loc3", "overlook2",  "摄像机", "Ch17_Pants", 30, 1),
#         ]
#     },
#     r"D:\Fire_Project\FireDataset\走廊\人物4动作4位置4.blend": {
#         "scene_name": "hallway",
#         "tasks": [
#             ("chacter4", "action4", "loc4", "overlook",  "Camera", "Ch46", 30, 1),
#             ("chacter4", "action4", "loc4", "horlook",  "摄像机.001", "Ch46", 30, 1),
#             ("chacter4", "action4", "loc4", "overlook2",  "摄像机", "Ch46", 30, 1),
#         ]
#     },