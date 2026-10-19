import bpy
import numpy as np
import os
import random
import warnings

BASE_DIR = "D:/Fire_Project/FireDataset/"
for sub in ["RGB", "IR", "Depth", "IR_exr_temp", "Depth_exr_temp",
            "Labels", "Labels_vis", "tmp_matte"]:
    os.makedirs(os.path.join(BASE_DIR, sub), exist_ok=True)

MASK_OBJECTS = "Ch46.001"

def add_body_heat_emission():
    human_obj = bpy.data.objects.get('Ch46.001')
    if not human_obj:
        print("⚠️ 未找到人物对象")
        return
    for mat in human_obj.data.materials:
        if not mat or not mat.node_tree:
            continue
        nodes = mat.node_tree.nodes
        links = mat.node_tree.links
        if any(n.type == 'EMISSION' and
               abs(n.inputs['Strength'].default_value - 0.8) < 0.01
               for n in nodes):
            continue
        out = next((n for n in nodes if n.type == 'OUTPUT_MATERIAL'), None)
        if not out or not out.inputs['Surface'].is_linked:
            continue
        original = out.inputs['Surface'].links[0].from_node
        add = nodes.new('ShaderNodeAddShader')
        emit = nodes.new('ShaderNodeEmission')
        emit.inputs['Color'].default_value = (1.0, 0.6, 0.3, 1.0)
        emit.inputs['Strength'].default_value = 0.8
        links.new(original.outputs[0], add.inputs[0])
        links.new(emit.outputs[0], add.inputs[1])
        links.new(add.outputs[0], out.inputs['Surface'])
    print("✅ 人物体温 Emission 已添加")

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

def add_out(tree, name, sub, color_mode='RGB',
            file_format='PNG', color_depth='8'):
    node = tree.nodes.new('CompositorNodeOutputFile')
    node.name = name
    node.directory = BASE_DIR + sub + "\\"
    node.file_name = ""
    node.format.media_type = 'IMAGE'
    node.format.file_format = file_format
    node.format.color_mode = color_mode
    node.format.color_depth = color_depth
    while len(node.file_output_items) > 0:
        node.file_output_items.remove(node.file_output_items[0])
    node.file_output_items.new('RGBA', name + "_")
    return node

def latest_file(sub, ext='.png'):
    d = os.path.join(BASE_DIR, sub)
    files = [f for f in os.listdir(d) if f.endswith(ext)]
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

def render_rgb_and_label(base_name, width, height):
    scene = bpy.context.scene
    scene.render.engine = 'CYCLES'
    scene.cycles.samples = 64
    scene.cycles.use_denoising = True
    vl = scene.view_layers[0]
    vl.use_pass_cryptomatte_object = True
    vl.use_pass_cryptomatte_accurate = True
    tree = reset_tree()
    links = tree.links
    rl = tree.nodes.new('CompositorNodeRLayers')
    rgb_out = add_out(tree, base_name, "RGB")
    links.new(rl.outputs['Image'], rgb_out.inputs[0])
    crypto = tree.nodes.new('CompositorNodeCryptomatteV2')
    crypto.source = 'RENDER'
    crypto.layer_name = 'ViewLayer.CryptoObject'
    crypto.matte_id = MASK_OBJECTS
    links.new(rl.outputs['Image'], crypto.inputs['Image'])
    matte_out = add_out(tree, base_name + "_matte", "tmp_matte", color_mode='BW')
    links.new(crypto.outputs['Matte'], matte_out.inputs[0])
    bpy.ops.render.render(write_still=False)
    matte_path = latest_file("tmp_matte")
    bbox = None
    if matte_path:
        img = bpy.data.images.load(matte_path)
        pixels = np.array(img.pixels[:]).reshape(height, width, 4)
        bpy.data.images.remove(img)
        os.remove(matte_path)
        bbox = matte_to_bbox(pixels, width, height)
    txt_path = os.path.join(BASE_DIR, "Labels", base_name + ".txt")
    if bbox:
        cx, cy, bw, bh = bbox
        with open(txt_path, 'w') as f:
            f.write(f"0 {cx:.6f} {cy:.6f} {bw:.6f} {bh:.6f}\n")
        print(f"  ✅ RGB + BBox: cx={cx:.3f} cy={cy:.3f} w={bw:.3f} h={bh:.3f}")
    else:
        open(txt_path, 'w').close()
        print(f"  ✅ RGB完成，⚠️ 对象不在画面内")

def render_ir(base_name, width, height):
    scene = bpy.context.scene
    scene.render.engine = 'CYCLES'
    scene.cycles.samples = 32
    scene.cycles.use_denoising = False
    scene.view_layers[0].use_pass_emit = True
    tree = reset_tree()
    links = tree.links
    rl = tree.nodes.new('CompositorNodeRLayers')
    ir_out = add_out(tree, base_name + "_ir", "IR_exr_temp",
                     file_format='OPEN_EXR', color_mode='RGB', color_depth='32')
    links.new(rl.outputs['Emission'], ir_out.inputs[0])
    bpy.ops.render.render(write_still=False)
    ir_exr = latest_file("IR_exr_temp", ext='.exr')
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
    img_out.filepath_raw = os.path.join(BASE_DIR, "IR", base_name + ".png")
    img_out.file_format = 'PNG'
    img_out.save()
    bpy.data.images.remove(img_out)
    print(f"  ✅ IR完成 | 最大强度={intensity.max():.3f}")

def render_depth(base_name, width, height):
    scene = bpy.context.scene
    scene.render.engine = 'BLENDER_EEVEE'
    scene.view_layers[0].use_pass_z = True
    tree = reset_tree()
    links = tree.links
    rl = tree.nodes.new('CompositorNodeRLayers')
    depth_out = add_out(tree, base_name + "_depth", "Depth_exr_temp",
                        file_format='OPEN_EXR', color_mode='RGB', color_depth='32')
    links.new(rl.outputs['Depth'], depth_out.inputs[0])
    bpy.ops.render.render(write_still=False)
    depth_exr = latest_file("Depth_exr_temp", ext='.exr')
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
        print(f"  ✅ 深度图完成 | 有效范围: {p2:.2f}m ~ {p98:.2f}m")
    else:
        print("  ⚠️ 深度图无有效像素")
    img_out = bpy.data.images.new("Depth_tmp", width=width, height=height, alpha=False)
    img_out.pixels = np.stack(
        [depth_norm, depth_norm, depth_norm,
         np.ones_like(depth_norm)], axis=-1).flatten().tolist()
    img_out.filepath_raw = os.path.join(BASE_DIR, "Depth", base_name + ".png")
    img_out.file_format = 'PNG'
    img_out.save()
    bpy.data.images.remove(img_out)

def visualize_bbox(base_name, width, height):
    rgb_path = latest_file("RGB")
    txt_path = os.path.join(BASE_DIR, "Labels", base_name + ".txt")
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
    for line in lines:
        parts = line.split()
        if len(parts) < 5:
            continue
        cls = int(parts[0])
        cx, cy, bw, bh = (float(parts[1]), float(parts[2]),
                           float(parts[3]), float(parts[4]))
        x1 = max(0,        int((cx - bw/2) * width))
        y1 = max(0,        int((cy - bh/2) * height))
        x2 = min(width-1,  int((cx + bw/2) * width))
        y2 = min(height-1, int((cy + bh/2) * height))
        color = [0, 255, 0] if cls == 0 else [255, 0, 0]
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
    out_img.filepath_raw = BASE_DIR + "Labels_vis\\" + base_name + "_vis.png"
    out_img.file_format = 'PNG'
    out_img.save()
    bpy.data.images.remove(out_img)
    print(f"  ✅ 可视化完成")

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

def main():
    print("🚀 开始生成多模态数据集")
    scene = bpy.context.scene
    W = scene.render.resolution_x
    H = scene.render.resolution_y

    orig_engine = scene.render.engine
    orig_samples = scene.cycles.samples

    add_body_heat_emission()

    num_samples = 150  # ← 修改生成数量

    available_frames = list(range(20, 251))
    if num_samples > len(available_frames):
        print(f"⚠️ 请求{num_samples}张但只有{len(available_frames)}帧")
        num_samples = len(available_frames)

    selected_frames = random.sample(available_frames, num_samples)
    print(f"✅ 已选 {len(selected_frames)} 个不重复帧")

    cameras = []
    col = bpy.data.collections.get("Cameras")
    if col:
        cameras = [o for o in col.objects if o.type == 'CAMERA']

    for i, frame in enumerate(selected_frames, 1):
        scene.frame_set(frame)
        if cameras:
            scene.camera = random.choice(cameras)
        randomize_lighting()

        base_name = f"Sample_{i:05d}"
        print(f"\n{'='*40}")
        print(f"🎬 {i}/{num_samples}: {base_name}  帧={frame}")

        render_rgb_and_label(base_name, W, H)
        render_ir(base_name, W, H)
        render_depth(base_name, W, H)
        visualize_bbox(base_name, W, H)

    scene.render.engine = orig_engine
    scene.cycles.samples = orig_samples

    for tmp in ["tmp_matte", "IR_exr_temp", "Depth_exr_temp"]:
        d = os.path.join(BASE_DIR, tmp)
        if os.path.exists(d) and not os.listdir(d):
            os.rmdir(d)

    print(f"\n🎉 完成！共生成 {num_samples} 个样本")
    print(f"  RGB        → {os.path.join(BASE_DIR, 'RGB')}")
    print(f"  IR         → {os.path.join(BASE_DIR, 'IR')}")
    print(f"  Depth      → {os.path.join(BASE_DIR, 'Depth')}")
    print(f"  Labels     → {os.path.join(BASE_DIR, 'Labels')}")
    print(f"  Labels_vis → {os.path.join(BASE_DIR, 'Labels_vis')}")

# ✅ 关键：调用主函数
main()