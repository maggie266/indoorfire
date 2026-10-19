# import bpy
# import numpy as np
# import os
# import random
# import warnings
# import json
#
# ROOT_DIR  = "D:/Fire_Project/FireDataset/"
# TASK_JSON = "D:/Fire_Project/scripts/current_task.json"
#
# # ==========================================
# # 读取任务配置
# # ==========================================
# with open(TASK_JSON, 'r', encoding='utf-8') as f:
#     task_data = json.load(f)
#
# SCENE_NAME = task_data["scene_name"]
# TASKS      = task_data["tasks"]
#
# # ==========================================
# # 给人物添加体温 Emission
# # ==========================================
# def add_body_heat_emission(human_obj_name, base_dir):
#     obj_names = human_obj_name if isinstance(human_obj_name, list) else [human_obj_name]
#
#     for obj_name in obj_names:
#         human_obj = bpy.data.objects.get(obj_name)
#         if not human_obj:
#             print(f"⚠️ 未找到人物对象: {obj_name}")
#             continue
#
#         added_count = 0
#         skipped_count = 0
#
#         for mat in human_obj.data.materials:
#             if not mat or not mat.node_tree:
#                 continue
#             nodes = mat.node_tree.nodes
#             links = mat.node_tree.links
#
#             if any(n.type == 'EMISSION' for n in nodes):
#                 for n in nodes:
#                     if n.type == 'EMISSION':
#                         if n.inputs['Strength'].default_value > 0.1:
#                             n.inputs['Strength'].default_value = 0.05
#                 skipped_count += 1
#                 continue
#
#             out = next((n for n in nodes if n.type == 'OUTPUT_MATERIAL'), None)
#             if not out or not out.inputs['Surface'].is_linked:
#                 continue
#
#             original = out.inputs['Surface'].links[0].from_node
#             add_shader = nodes.new('ShaderNodeAddShader')
#             emit = nodes.new('ShaderNodeEmission')
#             emit.inputs['Color'].default_value = (1.0, 0.6, 0.3, 1.0)
#             emit.inputs['Strength'].default_value = 0.05
#             links.new(original.outputs[0], add_shader.inputs[0])
#             links.new(emit.outputs[0], add_shader.inputs[1])
#             links.new(add_shader.outputs[0], out.inputs['Surface'])
#             added_count += 1
#
#         print(f"✅ {obj_name}: 新增{added_count}个，跳过{skipped_count}个（已有Emission）")
#
# # ==========================================
# # 工具函数
# # ==========================================
# def reset_tree():
#     scene = bpy.context.scene
#     scene.render.use_compositing = True
#     with warnings.catch_warnings():
#         warnings.simplefilter("ignore")
#         scene.use_nodes = True
#     for ng in list(bpy.data.node_groups):
#         if ng.type == 'COMPOSITING':
#             bpy.data.node_groups.remove(ng)
#     tree = bpy.data.node_groups.new(name="Compositor", type='CompositorNodeTree')
#     scene.compositing_node_group = tree
#     tree.nodes.clear()
#     return tree
#
# def add_out(tree, name, sub, base_dir, color_mode='RGB',
#             file_format='PNG', color_depth='8'):
#     node = tree.nodes.new('CompositorNodeOutputFile')
#     node.name = name
#     node.directory = os.path.join(base_dir, sub) + "\\"
#     node.file_name = ""
#     node.format.media_type = 'IMAGE'
#     node.format.file_format = file_format
#     node.format.color_mode = color_mode
#     node.format.color_depth = color_depth
#     while len(node.file_output_items) > 0:
#         node.file_output_items.remove(node.file_output_items[0])
#     node.file_output_items.new('RGBA', name + "_")
#     return node
#
# def latest_file(base_dir, sub, ext='.png'):
#     d = os.path.join(base_dir, sub)
#     files = [f for f in os.listdir(d) if f.endswith(ext)]
#     return os.path.join(d, max(
#         files, key=lambda f: os.path.getmtime(os.path.join(d, f))
#     )) if files else None
#
# def matte_to_bbox(pixels, width, height):
#     gray = np.flipud(pixels[:, :, 0])
#     binary = (gray > 0.1).astype(np.uint8)
#     if binary.sum() == 0:
#         return None
#     rows = np.any(binary, axis=1)
#     cols = np.any(binary, axis=0)
#     y_min, y_max = np.where(rows)[0][[0, -1]]
#     x_min, x_max = np.where(cols)[0][[0, -1]]
#     cx = (x_min + x_max) / 2 / width
#     cy = (y_min + y_max) / 2 / height
#     bw = (x_max - x_min) / width
#     bh = (y_max - y_min) / height
#     return cx, cy, bw, bh
#
# def apply_jet_colormap(gray):
#     r = np.clip(1.5 - abs(gray * 4 - 3), 0, 1)
#     g = np.clip(1.5 - abs(gray * 4 - 2), 0, 1)
#     b = np.clip(1.5 - abs(gray * 4 - 1), 0, 1)
#     return np.stack([r, g, b], axis=-1)
#
# # ==========================================
# # 烟雾遮挡模拟
# # ==========================================
# def estimate_smoke_mask(rgb_path, width, height):
#     img = bpy.data.images.load(rgb_path)
#     rgb_px = np.flipud(
#         np.array(img.pixels[:]).reshape(height, width, 4)[:, :, :3])
#     bpy.data.images.remove(img)
#     r = rgb_px[:,:,0]
#     g = rgb_px[:,:,1]
#     b = rgb_px[:,:,2]
#     gray = 0.299*r + 0.587*g + 0.114*b
#     saturation = rgb_px.max(axis=-1) - rgb_px.min(axis=-1)
#     gray_bias  = np.abs(r-g) + np.abs(g-b) + np.abs(r-b)
#     gray_smoke = (
#         (saturation < 0.04) &
#         (gray > 0.30) &
#         (gray < 0.70) &
#         (gray_bias < 0.04)
#     ).astype(np.float32)
#     orange_smoke = (
#         (r > 0.65) &
#         (r > g * 1.5) &
#         (r > b * 2.5) &
#         (gray > 0.35) &
#         (gray < 0.92)
#     ).astype(np.float32)
#     fire_core = (
#         (r > 0.90) &
#         (g > 0.4) &
#         (b < 0.25)
#     ).astype(np.float32)
#     smoke_mask = np.clip(gray_smoke + orange_smoke + fire_core, 0, 1)
#     return smoke_mask
#
# def apply_smoke_occlusion(depth_norm, smoke_mask, smoke_strength=0.4):
#     result = depth_norm.copy()
#     valid = depth_norm > 0
#     smoke_depth = 0.85
#     result = result * (1 - smoke_mask * smoke_strength) + \
#              smoke_depth * (smoke_mask * smoke_strength)
#     heavy_smoke = smoke_mask > 0.7
#     missing = heavy_smoke & (np.random.random(result.shape) < 0.6)
#     result[missing] = 0.0
#     tiny_noise = np.random.normal(0, 0.008, result.shape) * smoke_mask
#     result += tiny_noise
#     result[~valid] = 0.0
#     result[valid] = np.clip(result[valid], 0, 1)
#     return result
#
# # ==========================================
# # 渲染1：RGB + Cryptomatte BBox
# # ==========================================
# def render_rgb_and_label(base_name, width, height, base_dir, mask_objects):
#     scene = bpy.context.scene
#     scene.render.engine = 'CYCLES'
#     scene.cycles.samples = 64
#     scene.cycles.use_denoising = True
#     vl = scene.view_layers[0]
#     vl.use_pass_cryptomatte_object = True
#     vl.use_pass_cryptomatte_accurate = True
#
#     tree = reset_tree()
#     links = tree.links
#     rl = tree.nodes.new('CompositorNodeRLayers')
#
#     rgb_out = add_out(tree, base_name, "RGB", base_dir)
#     links.new(rl.outputs['Image'], rgb_out.inputs[0])
#
#     crypto = tree.nodes.new('CompositorNodeCryptomatteV2')
#     crypto.source = 'RENDER'
#     crypto.layer_name = 'ViewLayer.CryptoObject'
#     crypto.matte_id = mask_objects
#     links.new(rl.outputs['Image'], crypto.inputs['Image'])
#
#     matte_out = add_out(tree, base_name + "_matte", "tmp_matte", base_dir, color_mode='BW')
#     links.new(crypto.outputs['Matte'], matte_out.inputs[0])
#
#     bpy.ops.render.render(write_still=False)
#
#     matte_path = latest_file(base_dir, "tmp_matte")
#     bbox = None
#     if matte_path:
#         img = bpy.data.images.load(matte_path)
#         pixels = np.array(img.pixels[:]).reshape(height, width, 4)
#         bpy.data.images.remove(img)
#         os.remove(matte_path)
#         bbox = matte_to_bbox(pixels, width, height)
#
#     txt_path = os.path.join(base_dir, "Labels", base_name + ".txt")
#     if bbox:
#         cx, cy, bw, bh = bbox
#         with open(txt_path, 'w') as f:
#             f.write(f"0 {cx:.6f} {cy:.6f} {bw:.6f} {bh:.6f}\n")
#         print(f"  ✅ RGB + BBox: cx={cx:.3f} cy={cy:.3f} w={bw:.3f} h={bh:.3f}")
#     else:
#         open(txt_path, 'w').close()
#         print(f"  ✅ RGB完成，⚠️ 对象不在画面内")
#
# # ==========================================
# # 渲染2：IR 热力图
# # ==========================================
# def render_ir(base_name, width, height, base_dir):
#     scene = bpy.context.scene
#     scene.render.engine = 'CYCLES'
#     scene.cycles.samples = 32
#     scene.cycles.use_denoising = False
#     scene.view_layers[0].use_pass_emit = True
#
#     tree = reset_tree()
#     links = tree.links
#     rl = tree.nodes.new('CompositorNodeRLayers')
#
#     ir_out = add_out(tree, base_name + "_ir", "IR_exr_temp", base_dir,
#                      file_format='OPEN_EXR', color_mode='RGB', color_depth='32')
#     links.new(rl.outputs['Emission'], ir_out.inputs[0])
#
#     bpy.ops.render.render(write_still=False)
#
#     ir_exr = latest_file(base_dir, "IR_exr_temp", ext='.exr')
#     if not ir_exr:
#         print("  ⚠️ 未找到IR EXR")
#         return
#
#     img = bpy.data.images.load(ir_exr)
#     img.colorspace_settings.name = 'Non-Color'
#     px = np.array(img.pixels[:]).reshape(height, width, 4)[:, :, :3]
#     bpy.data.images.remove(img)
#     os.remove(ir_exr)
#
#     intensity = px.mean(axis=-1)
#     log_intensity = np.log1p(intensity)
#     val_max = np.log1p(100.0)
#     gray = np.clip(log_intensity / val_max, 0, 1)
#     colored = apply_jet_colormap(gray)
#
#     img_out = bpy.data.images.new("IR_tmp", width=width, height=height, alpha=False)
#     img_out.pixels = np.concatenate(
#         [colored, np.ones((height, width, 1))], axis=-1).flatten().tolist()
#     img_out.filepath_raw = os.path.join(base_dir, "IR", base_name + ".png")
#     img_out.file_format = 'PNG'
#     img_out.save()
#     bpy.data.images.remove(img_out)
#     print(f"  ✅ IR完成 | 最大强度={intensity.max():.3f}")
#
# # ==========================================
# # 渲染3：深度图
# # ==========================================
# def render_depth(base_name, width, height, base_dir):
#     scene = bpy.context.scene
#     scene.render.engine = 'BLENDER_EEVEE'
#     scene.view_layers[0].use_pass_z = True
#
#     tree = reset_tree()
#     links = tree.links
#     rl = tree.nodes.new('CompositorNodeRLayers')
#
#     depth_out = add_out(tree, base_name + "_depth", "Depth_exr_temp", base_dir,
#                         file_format='OPEN_EXR', color_mode='RGB', color_depth='32')
#     links.new(rl.outputs['Depth'], depth_out.inputs[0])
#
#     bpy.ops.render.render(write_still=False)
#
#     depth_exr = latest_file(base_dir, "Depth_exr_temp", ext='.exr')
#     if not depth_exr:
#         print("  ⚠️ 未找到深度EXR")
#         return
#
#     img = bpy.data.images.load(depth_exr)
#     img.colorspace_settings.name = 'Non-Color'
#     px = np.array(img.pixels[:]).reshape(height, width, 4)[:, :, 0]
#     bpy.data.images.remove(img)
#     os.remove(depth_exr)
#
#     valid_mask = (px > 0) & (px < 1e10)
#     depth_norm = np.zeros((height, width))
#
#     if valid_mask.any():
#         p2  = np.percentile(px[valid_mask], 2)
#         p98 = np.percentile(px[valid_mask], 98)
#         depth_norm[valid_mask] = np.clip(
#             (px[valid_mask] - p2) / (p98 - p2 + 1e-8), 0, 1)
#         depth_norm = 1.0 - depth_norm
#         depth_norm[~valid_mask] = 0.0
#
#         rgb_path = latest_file(base_dir, "RGB")
#         if rgb_path:
#             smoke_mask = estimate_smoke_mask(rgb_path, width, height)
#             smoke_coverage = smoke_mask.mean() * 100
#             print(f"  烟雾检测覆盖率: {smoke_coverage:.1f}%")
#             if smoke_coverage > 5.0:
#                 depth_norm = apply_smoke_occlusion(
#                     depth_norm, smoke_mask, smoke_strength=0.4)
#                 print(f"  ✅ 深度图完成 | 烟雾覆盖={smoke_coverage:.1f}% | "
#                       f"距离={p2:.2f}m~{p98:.2f}m")
#             else:
#                 print(f"  ✅ 深度图完成（无烟雾）| 距离={p2:.2f}m~{p98:.2f}m")
#         else:
#             print(f"  ✅ 深度图完成 | 距离={p2:.2f}m~{p98:.2f}m")
#     else:
#         print("  ⚠️ 深度图无有效像素")
#
#     img_out = bpy.data.images.new("Depth_tmp", width=width, height=height, alpha=False)
#     img_out.pixels = np.stack(
#         [depth_norm, depth_norm, depth_norm,
#          np.ones_like(depth_norm)], axis=-1).flatten().tolist()
#     img_out.filepath_raw = os.path.join(base_dir, "Depth", base_name + ".png")
#     img_out.file_format = 'PNG'
#     img_out.save()
#     bpy.data.images.remove(img_out)
#
# # ==========================================
# # 可视化 BBox
# # ==========================================
# def visualize_bbox(base_name, width, height, base_dir):
#     rgb_path = latest_file(base_dir, "RGB")
#     txt_path = os.path.join(base_dir, "Labels", base_name + ".txt")
#     if not rgb_path or not os.path.exists(txt_path):
#         return
#     with open(txt_path) as f:
#         lines = [l.strip() for l in f.readlines() if l.strip()]
#     if not lines:
#         print(f"  ⚠️ 空标注，跳过可视化")
#         return
#
#     img = bpy.data.images.load(rgb_path)
#     pixels = np.flipud(
#         np.array(img.pixels[:]).reshape(height, width, 4).copy())
#     bpy.data.images.remove(img)
#     rgb = (pixels[:, :, :3] * 255).astype(np.uint8)
#
#     for line in lines:
#         parts = line.split()
#         if len(parts) < 5:
#             continue
#         cls = int(parts[0])
#         cx, cy, bw, bh = (float(parts[1]), float(parts[2]),
#                            float(parts[3]), float(parts[4]))
#         x1 = max(0,        int((cx - bw/2) * width))
#         y1 = max(0,        int((cy - bh/2) * height))
#         x2 = min(width-1,  int((cx + bw/2) * width))
#         y2 = min(height-1, int((cy + bh/2) * height))
#         color = [0, 255, 0] if cls == 0 else [255, 0, 0]
#         t = 3
#         rgb[y1:y1+t, x1:x2] = color
#         rgb[y2-t:y2, x1:x2] = color
#         rgb[y1:y2, x1:x1+t] = color
#         rgb[y1:y2, x2-t:x2] = color
#
#     out_img = bpy.data.images.new("vis_tmp", width=width, height=height, alpha=False)
#     out_img.pixels = np.flipud(
#         np.concatenate([rgb.astype(np.float32)/255,
#                         np.ones((height, width, 1))],
#                        axis=-1)).flatten().tolist()
#     out_img.filepath_raw = os.path.join(base_dir, "Labels_vis", base_name + "_vis.png")
#     out_img.file_format = 'PNG'
#     out_img.save()
#     bpy.data.images.remove(out_img)
#     print(f"  ✅ 可视化完成")
#
# # ==========================================
# # 随机化灯光
# # ==========================================
# def randomize_lighting():
#     col = bpy.data.collections.get("Lights")
#     if col:
#         for light in col.objects:
#             if light.type == 'LIGHT':
#                 light.hide_render = random.random() < 0.05
#                 if not light.hide_render:
#                     light.data.energy = random.uniform(600.0, 2000.0)
#                     light.data.color = (
#                         1.0,
#                         random.uniform(0.9, 1.0),
#                         random.uniform(0.8, 1.0)
#                     )
#
# # ==========================================
# # 主函数：循环执行所有任务组合
# # ==========================================
# def main():
#     # 强制启用GPU渲染
#     prefs = bpy.context.preferences
#     cycles_prefs = prefs.addons['cycles'].preferences
#     cycles_prefs.compute_device_type = 'CUDA'
#     cycles_prefs.refresh_devices()
#     for device in cycles_prefs.devices:
#         device.use = True
#     bpy.context.scene.cycles.device = 'GPU'
#
#     print(f"✅ GPU设备:")
#     for device in cycles_prefs.devices:
#         print(f"   {device.name} - 启用: {device.use}")
#     print(f"🚀 开始处理场景: {SCENE_NAME}，共 {len(TASKS)} 个组合")
#
#     scene = bpy.context.scene
#     W = scene.render.resolution_x
#     H = scene.render.resolution_y
#
#     orig_engine  = scene.render.engine
#     orig_samples = scene.cycles.samples
#
#     for task in TASKS:
#         chacter, action, loc, view, cam_name, human_obj, num_samples, start_index = task
#
#         # 动态生成该组合的输出目录
#         scene_tag = f"{SCENE_NAME}_{chacter}_{action}_{loc}_{view}"
#         base_dir  = os.path.join(ROOT_DIR, scene_tag)
#
#         # 创建所有子文件夹
#         for sub in ["RGB", "IR", "Depth", "IR_exr_temp", "Depth_exr_temp",
#                     "Labels", "Labels_vis", "tmp_matte"]:
#             os.makedirs(os.path.join(base_dir, sub), exist_ok=True)
#
#         print(f"\n{'='*50}")
#         print(f"🎬 组合: {scene_tag}")
#         print(f"📁 输出: {base_dir}")
#
#         # 设置摄像机
#         target_cam = bpy.data.objects.get(cam_name)
#         if target_cam:
#             scene.camera = target_cam
#             print(f"✅ 摄像机: {cam_name}")
#         else:
#             print(f"❌ 未找到摄像机 '{cam_name}'，跳过此组合")
#             continue
#
#         # 添加体温Emission
#         add_body_heat_emission(human_obj, base_dir)
#
#         # 随机采样帧
#         available_frames = list(range(20, 251))
#         _num = min(num_samples, len(available_frames))
#         selected_frames = random.sample(available_frames, _num)
#         print(f"✅ 已选 {_num} 个不重复帧")
#
#         for i, frame in enumerate(selected_frames, start_index):
#
#             # 中断检测
#             stop_file = os.path.join(ROOT_DIR, "STOP.txt")
#             if os.path.exists(stop_file):
#                 os.remove(stop_file)
#                 print(f"\n⚠️ 检测到停止信号，已完成 {i - start_index} 个样本")
#                 return  # 彻底停止所有任务
#
#             scene.frame_set(frame)
#             randomize_lighting()
#
#             base_name = f"{scene_tag}_{i:04d}"
#             print(f"\n--- {i - start_index + 1}/{_num}: {base_name}  帧={frame}")
#
#             render_rgb_and_label(base_name, W, H, base_dir, human_obj)
#             render_ir(base_name, W, H, base_dir)
#             render_depth(base_name, W, H, base_dir)
#             visualize_bbox(base_name, W, H, base_dir)
#
#         # 清理临时文件夹
#         for tmp in ["tmp_matte", "IR_exr_temp", "Depth_exr_temp"]:
#             d = os.path.join(base_dir, tmp)
#             if os.path.exists(d) and not os.listdir(d):
#                 os.rmdir(d)
#
#         print(f"✅ 组合完成: {scene_tag}")
#
#     scene.render.engine  = orig_engine
#     scene.cycles.samples = orig_samples
#     print(f"\n🎉 场景 {SCENE_NAME} 全部完成")
#
# main()

import bpy
import numpy as np
import os
import random
import warnings
import json

ROOT_DIR  = "D:/Fire_Project/FireDataset/"
TASK_JSON = "D:/Fire_Project/scripts/current_task.json"

# ==========================================
# 读取任务配置
# ==========================================
with open(TASK_JSON, 'r', encoding='utf-8') as f:
    task_data = json.load(f)

SCENE_NAME = task_data["scene_name"]
TASKS      = task_data["tasks"]

# ==========================================
# 给人物添加体温 Emission
# ==========================================
def add_body_heat_emission(human_obj_names):
    obj_names = human_obj_names if isinstance(human_obj_names, list) else [human_obj_names]

    for obj_name in obj_names:
        human_obj = bpy.data.objects.get(obj_name)
        if not human_obj:
            print(f"⚠️ 未找到人物对象: {obj_name}")
            continue

        # 跳过没有材质的对象（骨架、空物体、动物根骨骼等）
        if not hasattr(human_obj.data, 'materials'):
            print(f"⚠️ {obj_name} 无材质，跳过Emission添加（仍会参与标注）")
            continue

        added_count = 0
        skipped_count = 0

        for mat in human_obj.data.materials:
            if not mat or not mat.node_tree:
                continue
            nodes = mat.node_tree.nodes
            links = mat.node_tree.links

            if any(n.type == 'EMISSION' for n in nodes):
                for n in nodes:
                    if n.type == 'EMISSION':
                        if n.inputs['Strength'].default_value > 0.1:
                            n.inputs['Strength'].default_value = 0.05
                skipped_count += 1
                continue

            out = next((n for n in nodes if n.type == 'OUTPUT_MATERIAL'), None)
            if not out or not out.inputs['Surface'].is_linked:
                continue

            original = out.inputs['Surface'].links[0].from_node
            add_shader = nodes.new('ShaderNodeAddShader')
            emit = nodes.new('ShaderNodeEmission')
            emit.inputs['Color'].default_value = (1.0, 0.6, 0.3, 1.0)
            emit.inputs['Strength'].default_value = 0.05
            links.new(original.outputs[0], add_shader.inputs[0])
            links.new(emit.outputs[0], add_shader.inputs[1])
            links.new(add_shader.outputs[0], out.inputs['Surface'])
            added_count += 1

        print(f"✅ {obj_name}: 新增{added_count}个，跳过{skipped_count}个（已有Emission）")

# ==========================================
# 工具函数
# ==========================================
def reset_tree():
    scene = bpy.context.scene
    scene.render.use_compositing = True
    with warnings.catch_warnings():
        warnings.simplefilter("ignore")
        scene.use_nodes = True
    for ng in list(bpy.data.node_groups):
        if ng.type == 'COMPOSITING':
            bpy.data.node_groups.remove(ng)
    tree = bpy.data.node_groups.new(name="Compositor", type='CompositorNodeTree')
    scene.compositing_node_group = tree
    tree.nodes.clear()
    return tree

def add_out(tree, name, sub, base_dir, color_mode='RGB',
            file_format='PNG', color_depth='8'):
    node = tree.nodes.new('CompositorNodeOutputFile')
    node.name = name
    node.directory = os.path.join(base_dir, sub) + "\\"
    node.file_name = ""
    node.format.media_type = 'IMAGE'
    node.format.file_format = file_format
    node.format.color_mode = color_mode
    node.format.color_depth = color_depth
    while len(node.file_output_items) > 0:
        node.file_output_items.remove(node.file_output_items[0])
    node.file_output_items.new('RGBA', name + "_")
    return node

def latest_file(base_dir, sub, ext='.png'):
    d = os.path.join(base_dir, sub)
    files = [f for f in os.listdir(d) if f.endswith(ext)]
    return os.path.join(d, max(
        files, key=lambda f: os.path.getmtime(os.path.join(d, f))
    )) if files else None

def latest_file_prefix(base_dir, sub, prefix, ext='.png'):
    """找到指定前缀的最新文件"""
    d = os.path.join(base_dir, sub)
    files = [f for f in os.listdir(d) if f.startswith(prefix) and f.endswith(ext)]
    return os.path.join(d, max(
        files, key=lambda f: os.path.getmtime(os.path.join(d, f))
    )) if files else None

def matte_to_bbox(pixels, width, height):
    gray = np.flipud(pixels[:, :, 0])
    binary = (gray > 0.1).astype(np.uint8)
    if binary.sum() == 0:
        return None
    rows = np.any(binary, axis=1)
    cols = np.any(binary, axis=0)
    y_min, y_max = np.where(rows)[0][[0, -1]]
    x_min, x_max = np.where(cols)[0][[0, -1]]
    cx = (x_min + x_max) / 2 / width
    cy = (y_min + y_max) / 2 / height
    bw = (x_max - x_min) / width
    bh = (y_max - y_min) / height
    return cx, cy, bw, bh

def apply_jet_colormap(gray):
    r = np.clip(1.5 - abs(gray * 4 - 3), 0, 1)
    g = np.clip(1.5 - abs(gray * 4 - 2), 0, 1)
    b = np.clip(1.5 - abs(gray * 4 - 1), 0, 1)
    return np.stack([r, g, b], axis=-1)

# ==========================================
# 烟雾遮挡模拟
# ==========================================
def estimate_smoke_mask(rgb_path, width, height):
    img = bpy.data.images.load(rgb_path)
    rgb_px = np.flipud(
        np.array(img.pixels[:]).reshape(height, width, 4)[:, :, :3])
    bpy.data.images.remove(img)
    r = rgb_px[:,:,0]
    g = rgb_px[:,:,1]
    b = rgb_px[:,:,2]
    gray = 0.299*r + 0.587*g + 0.114*b
    saturation = rgb_px.max(axis=-1) - rgb_px.min(axis=-1)
    gray_bias  = np.abs(r-g) + np.abs(g-b) + np.abs(r-b)
    gray_smoke = (
        (saturation < 0.04) &
        (gray > 0.30) &
        (gray < 0.70) &
        (gray_bias < 0.04)
    ).astype(np.float32)
    orange_smoke = (
        (r > 0.65) &
        (r > g * 1.5) &
        (r > b * 2.5) &
        (gray > 0.35) &
        (gray < 0.92)
    ).astype(np.float32)
    fire_core = (
        (r > 0.90) &
        (g > 0.4) &
        (b < 0.25)
    ).astype(np.float32)
    smoke_mask = np.clip(gray_smoke + orange_smoke + fire_core, 0, 1)
    return smoke_mask

def apply_smoke_occlusion(depth_norm, smoke_mask, smoke_strength=0.4):
    result = depth_norm.copy()
    valid = depth_norm > 0
    smoke_depth = 0.85
    result = result * (1 - smoke_mask * smoke_strength) + \
             smoke_depth * (smoke_mask * smoke_strength)
    heavy_smoke = smoke_mask > 0.7
    missing = heavy_smoke & (np.random.random(result.shape) < 0.6)
    result[missing] = 0.0
    tiny_noise = np.random.normal(0, 0.008, result.shape) * smoke_mask
    result += tiny_noise
    result[~valid] = 0.0
    result[valid] = np.clip(result[valid], 0, 1)
    return result

# ==========================================
# 渲染1：RGB + 多人物 Cryptomatte BBox
# ==========================================
def render_rgb_and_label(base_name, width, height, base_dir, mask_objects):
    scene = bpy.context.scene
    scene.render.engine = 'CYCLES'
    scene.cycles.samples = 64
    scene.cycles.use_denoising = True
    vl = scene.view_layers[0]
    vl.use_pass_cryptomatte_object = True
    vl.use_pass_cryptomatte_accurate = True

    obj_names = mask_objects if isinstance(mask_objects, list) else [mask_objects]

    tree = reset_tree()
    links = tree.links
    rl = tree.nodes.new('CompositorNodeRLayers')

    # RGB输出
    rgb_out = add_out(tree, base_name, "RGB", base_dir)
    links.new(rl.outputs['Image'], rgb_out.inputs[0])

    # 每个人物单独一个 Cryptomatte 节点
    for obj_name in obj_names:
        safe_name = obj_name.replace(".", "_")
        crypto = tree.nodes.new('CompositorNodeCryptomatteV2')
        crypto.source = 'RENDER'
        crypto.layer_name = 'ViewLayer.CryptoObject'
        crypto.matte_id = obj_name
        links.new(rl.outputs['Image'], crypto.inputs['Image'])

        matte_out = add_out(tree, f"{base_name}_{safe_name}_matte",
                            "tmp_matte", base_dir, color_mode='BW')
        links.new(crypto.outputs['Matte'], matte_out.inputs[0])

    bpy.ops.render.render(write_still=False)

    # 每个人物分别读取 matte 生成 bbox
    txt_path = os.path.join(base_dir, "Labels", base_name + ".txt")
    bbox_count = 0

    with open(txt_path, 'w') as f:
        for obj_name in obj_names:
            safe_name = obj_name.replace(".", "_")
            prefix = f"{base_name}_{safe_name}_matte"
            matte_path = latest_file_prefix(base_dir, "tmp_matte", prefix)

            if not matte_path:
                print(f"  ⚠️ 未找到 {obj_name} 的matte文件")
                continue

            img = bpy.data.images.load(matte_path)
            pixels = np.array(img.pixels[:]).reshape(height, width, 4)
            bpy.data.images.remove(img)
            os.remove(matte_path)

            bbox = matte_to_bbox(pixels, width, height)
            if bbox:
                cx, cy, bw, bh = bbox
                f.write(f"0 {cx:.6f} {cy:.6f} {bw:.6f} {bh:.6f}\n")
                bbox_count += 1
                print(f"  ✅ {obj_name} BBox: cx={cx:.3f} cy={cy:.3f} w={bw:.3f} h={bh:.3f}")
            else:
                print(f"  ⚠️ {obj_name} 不在画面内")

    if bbox_count > 0:
        print(f"  ✅ RGB完成，共标注 {bbox_count}/{len(obj_names)} 个人物")
    else:
        print(f"  ✅ RGB完成，⚠️ 所有人物均不在画面内")

# ==========================================
# 渲染2：IR 热力图
# ==========================================
def render_ir(base_name, width, height, base_dir):
    scene = bpy.context.scene
    scene.render.engine = 'CYCLES'
    scene.cycles.samples = 32
    scene.cycles.use_denoising = False
    scene.view_layers[0].use_pass_emit = True

    tree = reset_tree()
    links = tree.links
    rl = tree.nodes.new('CompositorNodeRLayers')

    ir_out = add_out(tree, base_name + "_ir", "IR_exr_temp", base_dir,
                     file_format='OPEN_EXR', color_mode='RGB', color_depth='32')
    links.new(rl.outputs['Emission'], ir_out.inputs[0])

    bpy.ops.render.render(write_still=False)

    ir_exr = latest_file(base_dir, "IR_exr_temp", ext='.exr')
    if not ir_exr:
        print("  ⚠️ 未找到IR EXR")
        return

    img = bpy.data.images.load(ir_exr)
    img.colorspace_settings.name = 'Non-Color'
    px = np.array(img.pixels[:]).reshape(height, width, 4)[:, :, :3]
    bpy.data.images.remove(img)
    os.remove(ir_exr)

    intensity = px.mean(axis=-1)
    log_intensity = np.log1p(intensity)
    val_max = np.log1p(100.0)
    gray = np.clip(log_intensity / val_max, 0, 1)
    colored = apply_jet_colormap(gray)

    img_out = bpy.data.images.new("IR_tmp", width=width, height=height, alpha=False)
    img_out.pixels = np.concatenate(
        [colored, np.ones((height, width, 1))], axis=-1).flatten().tolist()
    img_out.filepath_raw = os.path.join(base_dir, "IR", base_name + ".png")
    img_out.file_format = 'PNG'
    img_out.save()
    bpy.data.images.remove(img_out)
    print(f"  ✅ IR完成 | 最大强度={intensity.max():.3f}")

# ==========================================
# 渲染3：深度图
# ==========================================
def render_depth(base_name, width, height, base_dir):
    scene = bpy.context.scene
    scene.render.engine = 'BLENDER_EEVEE'
    scene.view_layers[0].use_pass_z = True

    tree = reset_tree()
    links = tree.links
    rl = tree.nodes.new('CompositorNodeRLayers')

    depth_out = add_out(tree, base_name + "_depth", "Depth_exr_temp", base_dir,
                        file_format='OPEN_EXR', color_mode='RGB', color_depth='32')
    links.new(rl.outputs['Depth'], depth_out.inputs[0])

    bpy.ops.render.render(write_still=False)

    depth_exr = latest_file(base_dir, "Depth_exr_temp", ext='.exr')
    if not depth_exr:
        print("  ⚠️ 未找到深度EXR")
        return

    img = bpy.data.images.load(depth_exr)
    img.colorspace_settings.name = 'Non-Color'
    px = np.array(img.pixels[:]).reshape(height, width, 4)[:, :, 0]
    bpy.data.images.remove(img)
    os.remove(depth_exr)

    valid_mask = (px > 0) & (px < 1e10)
    depth_norm = np.zeros((height, width))

    if valid_mask.any():
        p2  = np.percentile(px[valid_mask], 2)
        p98 = np.percentile(px[valid_mask], 98)
        depth_norm[valid_mask] = np.clip(
            (px[valid_mask] - p2) / (p98 - p2 + 1e-8), 0, 1)
        depth_norm = 1.0 - depth_norm
        depth_norm[~valid_mask] = 0.0

        rgb_path = latest_file(base_dir, "RGB")
        if rgb_path:
            smoke_mask = estimate_smoke_mask(rgb_path, width, height)
            smoke_coverage = smoke_mask.mean() * 100
            print(f"  烟雾检测覆盖率: {smoke_coverage:.1f}%")
            if smoke_coverage > 5.0:
                depth_norm = apply_smoke_occlusion(
                    depth_norm, smoke_mask, smoke_strength=0.4)
                print(f"  ✅ 深度图完成 | 烟雾覆盖={smoke_coverage:.1f}% | "
                      f"距离={p2:.2f}m~{p98:.2f}m")
            else:
                print(f"  ✅ 深度图完成（无烟雾）| 距离={p2:.2f}m~{p98:.2f}m")
        else:
            print(f"  ✅ 深度图完成 | 距离={p2:.2f}m~{p98:.2f}m")
    else:
        print("  ⚠️ 深度图无有效像素")

    img_out = bpy.data.images.new("Depth_tmp", width=width, height=height, alpha=False)
    img_out.pixels = np.stack(
        [depth_norm, depth_norm, depth_norm,
         np.ones_like(depth_norm)], axis=-1).flatten().tolist()
    img_out.filepath_raw = os.path.join(base_dir, "Depth", base_name + ".png")
    img_out.file_format = 'PNG'
    img_out.save()
    bpy.data.images.remove(img_out)

# ==========================================
# 可视化 BBox（多人物不同颜色）
# ==========================================
def visualize_bbox(base_name, width, height, base_dir):
    rgb_path = latest_file(base_dir, "RGB")
    txt_path = os.path.join(base_dir, "Labels", base_name + ".txt")
    if not rgb_path or not os.path.exists(txt_path):
        return
    with open(txt_path) as f:
        lines = [l.strip() for l in f.readlines() if l.strip()]
    if not lines:
        print(f"  ⚠️ 空标注，跳过可视化")
        return

    img = bpy.data.images.load(rgb_path)
    pixels = np.flipud(
        np.array(img.pixels[:]).reshape(height, width, 4).copy())
    bpy.data.images.remove(img)
    rgb = (pixels[:, :, :3] * 255).astype(np.uint8)

    # 多人物用不同颜色区分
    colors = [
        [0, 255, 0],    # 绿色
        [0, 0, 255],    # 蓝色
        [255, 255, 0],  # 黄色
        [255, 0, 255],  # 紫色
        [0, 255, 255],  # 青色
    ]

    for idx, line in enumerate(lines):
        parts = line.split()
        if len(parts) < 5:
            continue
        cx, cy, bw, bh = (float(parts[1]), float(parts[2]),
                           float(parts[3]), float(parts[4]))
        x1 = max(0,        int((cx - bw/2) * width))
        y1 = max(0,        int((cy - bh/2) * height))
        x2 = min(width-1,  int((cx + bw/2) * width))
        y2 = min(height-1, int((cy + bh/2) * height))
        color = colors[idx % len(colors)]
        t = 3
        rgb[y1:y1+t, x1:x2] = color
        rgb[y2-t:y2, x1:x2] = color
        rgb[y1:y2, x1:x1+t] = color
        rgb[y1:y2, x2-t:x2] = color

    out_img = bpy.data.images.new("vis_tmp", width=width, height=height, alpha=False)
    out_img.pixels = np.flipud(
        np.concatenate([rgb.astype(np.float32)/255,
                        np.ones((height, width, 1))],
                       axis=-1)).flatten().tolist()
    out_img.filepath_raw = os.path.join(base_dir, "Labels_vis", base_name + "_vis.png")
    out_img.file_format = 'PNG'
    out_img.save()
    bpy.data.images.remove(out_img)
    print(f"  ✅ 可视化完成，共 {len(lines)} 个框")

# ==========================================
# 随机化灯光
# ==========================================
def randomize_lighting():
    col = bpy.data.collections.get("Lights")
    if col:
        for light in col.objects:
            if light.type == 'LIGHT':
                light.hide_render = random.random() < 0.05
                if not light.hide_render:
                    light.data.energy = random.uniform(600.0, 2000.0)
                    light.data.color = (
                        1.0,
                        random.uniform(0.9, 1.0),
                        random.uniform(0.8, 1.0)
                    )

# ==========================================
# 主函数
# ==========================================
def main():
    # 强制启用GPU渲染
    prefs = bpy.context.preferences
    cycles_prefs = prefs.addons['cycles'].preferences
    cycles_prefs.compute_device_type = 'CUDA'
    cycles_prefs.refresh_devices()
    for device in cycles_prefs.devices:
        device.use = True
    bpy.context.scene.cycles.device = 'GPU'

    print(f"✅ GPU设备:")
    for device in cycles_prefs.devices:
        print(f"   {device.name} - 启用: {device.use}")
    print(f"🚀 开始处理场景: {SCENE_NAME}，共 {len(TASKS)} 个组合")

    scene = bpy.context.scene
    W = scene.render.resolution_x
    H = scene.render.resolution_y

    orig_engine  = scene.render.engine
    orig_samples = scene.cycles.samples

    for task in TASKS:
        # scene_id, loc, view, cam_name, human_obj, num_samples, start_index = task
        scene_id, loc, view, cam_name, human_obj, num_samples, start_index, frame_start, frame_end = task

        # 统一转为列表
        obj_names = human_obj if isinstance(human_obj, list) else [human_obj]

        scene_tag = f"{SCENE_NAME}_{scene_id}_{loc}_{view}"
        base_dir  = os.path.join(ROOT_DIR, scene_tag)

        for sub in ["RGB", "IR", "Depth", "IR_exr_temp", "Depth_exr_temp",
                    "Labels", "Labels_vis", "tmp_matte"]:
            os.makedirs(os.path.join(base_dir, sub), exist_ok=True)

        print(f"\n{'='*50}")
        print(f"🎬 组合: {scene_tag}")
        print(f"📁 输出: {base_dir}")
        print(f"👥 人物: {obj_names}")

        target_cam = bpy.data.objects.get(cam_name)
        if target_cam:
            scene.camera = target_cam
            print(f"✅ 摄像机: {cam_name}")
        else:
            print(f"❌ 未找到摄像机 '{cam_name}'，跳过此组合")
            continue

        add_body_heat_emission(obj_names)

        # available_frames = list(range(20, 251))
        available_frames = list(range(frame_start, frame_end + 1))
        _num = min(num_samples, len(available_frames))
        selected_frames = random.sample(available_frames, _num)
        print(f"✅ 已选 {_num} 个不重复帧")

        for i, frame in enumerate(selected_frames, start_index):

            stop_file = os.path.join(ROOT_DIR, "STOP.txt")
            if os.path.exists(stop_file):
                os.remove(stop_file)
                print(f"\n⚠️ 检测到停止信号，已完成 {i - start_index} 个样本")
                return

            scene.frame_set(frame)
            randomize_lighting()

            base_name = f"{scene_tag}_{i:04d}"
            print(f"\n--- {i - start_index + 1}/{_num}: {base_name}  帧={frame}")

            render_rgb_and_label(base_name, W, H, base_dir, obj_names)
            render_ir(base_name, W, H, base_dir)
            render_depth(base_name, W, H, base_dir)
            visualize_bbox(base_name, W, H, base_dir)

        for tmp in ["tmp_matte", "IR_exr_temp", "Depth_exr_temp"]:
            d = os.path.join(base_dir, tmp)
            if os.path.exists(d) and not os.listdir(d):
                os.rmdir(d)

        print(f"✅ 组合完成: {scene_tag}")

    scene.render.engine  = orig_engine
    scene.cycles.samples = orig_samples
    print(f"\n🎉 场景 {SCENE_NAME} 全部完成")

main()