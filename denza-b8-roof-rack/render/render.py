"""
Photoreal Cycles renders of the roof-rack concepts (Blender >= 4.2 / bpy module).

    python render.py --variant A_AeroGT_closed --hdri aarfontein_dirt_road_4k.hdr \
        --cam front34 --mode day --out ../renders/A_day.png

Meshes come from build/mesh/<variant>/ (written by cad/build.py); the vehicle
proxy is always loaded alongside.
"""
from __future__ import annotations

import argparse
import json
import math
import os
from pathlib import Path

import bpy  # noqa: I001 - must precede bmesh in the pip bpy module
import bmesh
from mathutils import Vector

ROOT = Path(__file__).resolve().parent.parent
MESH = ROOT / "build" / "mesh"


# --------------------------------------------------------------------------
# materials
# --------------------------------------------------------------------------
def principled(name, base, metallic=0.0, rough=0.5, coat=0.0, coat_rough=0.03,
               emit=None, emit_strength=0.0, transmission=0.0, alpha=1.0, ior=1.45):
    m = bpy.data.materials.new(name)
    m.use_nodes = True
    b = m.node_tree.nodes["Principled BSDF"]
    b.inputs["Base Color"].default_value = (*base, 1)
    b.inputs["Metallic"].default_value = metallic
    b.inputs["Roughness"].default_value = rough
    b.inputs["Coat Weight"].default_value = coat
    b.inputs["Coat Roughness"].default_value = coat_rough
    b.inputs["IOR"].default_value = ior
    b.inputs["Transmission Weight"].default_value = transmission
    b.inputs["Alpha"].default_value = alpha
    if emit is not None:
        b.inputs["Emission Color"].default_value = (*emit, 1)
        b.inputs["Emission Strength"].default_value = emit_strength
    return m


def carbon_material():
    m = principled("carbon", (0.02, 0.02, 0.022), rough=0.35, coat=1.0, coat_rough=0.02)
    nt = m.node_tree
    tc = nt.nodes.new("ShaderNodeTexCoord")
    chk = nt.nodes.new("ShaderNodeTexChecker")
    chk.inputs["Scale"].default_value = 180.0
    chk.inputs["Color1"].default_value = (0.012, 0.012, 0.013, 1)
    chk.inputs["Color2"].default_value = (0.045, 0.045, 0.05, 1)
    nt.links.new(tc.outputs["Object"], chk.inputs["Vector"])
    b = nt.nodes["Principled BSDF"]
    nt.links.new(chk.outputs["Color"], b.inputs["Base Color"])
    rmix = nt.nodes.new("ShaderNodeMapRange")
    rmix.inputs["To Min"].default_value = 0.25
    rmix.inputs["To Max"].default_value = 0.45
    nt.links.new(chk.outputs["Fac"], rmix.inputs["Value"])
    nt.links.new(rmix.outputs["Result"], b.inputs["Roughness"])
    return m


def textured_plastic(name, base, rough=0.6, scale=900.0, bump=0.15):
    m = principled(name, base, rough=rough)
    nt = m.node_tree
    n = nt.nodes.new("ShaderNodeTexNoise")
    n.inputs["Scale"].default_value = scale
    bp = nt.nodes.new("ShaderNodeBump")
    bp.inputs["Strength"].default_value = bump
    nt.links.new(n.outputs["Fac"], bp.inputs["Height"])
    nt.links.new(bp.outputs["Normal"], nt.nodes["Principled BSDF"].inputs["Normal"])
    return m


def build_materials(mode):
    night = mode == "night"
    led_on = mode in ("night", "dusk")
    led_k = {"night": 80.0, "dusk": 60.0}.get(mode, 0.0)
    cool = (0.85, 0.92, 1.0)
    amber = (1.0, 0.45, 0.05)
    M = {
        "body_paint": principled("body_paint", (0.10, 0.125, 0.115), metallic=0.75, rough=0.32,
                                 coat=1.0, coat_rough=0.02),
        "glass_black": principled("glass_black", (0.004, 0.005, 0.006), rough=0.02, coat=1.0, coat_rough=0.0),
        "gloss_black": principled("gloss_black", (0.006, 0.006, 0.006), rough=0.12, coat=1.0, coat_rough=0.02),
        "rack_black": textured_plastic("rack_black", (0.018, 0.018, 0.02), rough=0.45, scale=1500, bump=0.08),
        "satin_black": textured_plastic("satin_black", (0.022, 0.022, 0.024), rough=0.38, scale=1500, bump=0.06),
        "anodised_grey": principled("anodised_grey", (0.28, 0.29, 0.31), metallic=1.0, rough=0.33),
        "carbon": carbon_material(),
        "rubber": principled("rubber", (0.015, 0.015, 0.015), rough=0.85),
        "hangar_shell": principled("hangar_shell", (0.62, 0.635, 0.65), metallic=0.4, rough=0.28,
                                   coat=1.0, coat_rough=0.04),
        "pad_dark": textured_plastic("pad_dark", (0.03, 0.03, 0.032), rough=0.8, scale=600, bump=0.2),
        "marking": principled("marking", (0.9, 0.7, 0.05), rough=0.5),
        "copper": principled("copper", (0.95, 0.6, 0.35), metallic=1.0, rough=0.25),
        "drone_grey": principled("drone_grey", (0.32, 0.33, 0.34), rough=0.42),
        "drone_dark": principled("drone_dark", (0.03, 0.03, 0.03), rough=0.4),
        "prop_blur": principled("prop_blur", (0.05, 0.05, 0.05), rough=0.5, alpha=0.18),
        "antenna_white": principled("antenna_white", (0.82, 0.82, 0.8), rough=0.35, coat=0.5),
        "antenna_black": principled("antenna_black", (0.02, 0.02, 0.02), rough=0.5),
        "radome_white": principled("radome_white", (0.85, 0.85, 0.84), rough=0.45, coat=0.3),
        "radome_xray": principled("radome_xray", (0.9, 0.93, 0.95), rough=0.08, transmission=1.0,
                                  alpha=0.35, ior=1.3),
        "pcb": principled("pcb", (0.02, 0.18, 0.08), rough=0.35, coat=0.5),
        "cladding": textured_plastic("cladding", (0.02, 0.02, 0.02), rough=0.7, scale=700, bump=0.25),
        "satin_alu": principled("satin_alu", (0.62, 0.63, 0.65), metallic=1.0, rough=0.22),
        "headlamp_lens": principled("headlamp_lens", (0.05, 0.05, 0.06), metallic=0.8, rough=0.05,
                                    coat=1.0, emit=cool, emit_strength=12.0 if led_on else 0.0),
        "headlight": principled("headlight", (0.8, 0.85, 0.9), rough=0.1, emit=cool,
                                emit_strength=25.0 if led_on else 4.0),
        "taillight": principled("taillight", (0.3, 0.01, 0.01), rough=0.1, coat=1.0,
                                emit=(1, 0.02, 0.01), emit_strength=8.0 if led_on else 0.5),
        "tyre": textured_plastic("tyre", (0.012, 0.012, 0.012), rough=0.85, scale=400, bump=0.3),
        "rim": principled("rim", (0.08, 0.085, 0.09), metallic=1.0, rough=0.3, coat=1.0),
        "rotor": principled("rotor", (0.35, 0.35, 0.35), metallic=1.0, rough=0.55),
        # LEDs: polished reflector look by day, high emission at night
        "led_white": principled("led_white", (0.7, 0.72, 0.75), metallic=0.9, rough=0.08, coat=1.0,
                                emit=cool, emit_strength=led_k),
        "led_halo": principled("led_halo", (0.7, 0.72, 0.75), metallic=0.6, rough=0.1, coat=1.0,
                               emit=cool, emit_strength=led_k * 0.6 if led_on else 1.5),
        "led_amber": principled("led_amber", (0.6, 0.35, 0.08), metallic=0.5, rough=0.1, coat=1.0,
                                emit=amber, emit_strength=led_k * 0.4 if led_on else 0.0),
        "led_cyan": principled("led_cyan", (0.1, 0.5, 0.6), rough=0.2, emit=(0.1, 0.8, 1.0),
                               emit_strength=20.0 if led_on else 6.0),
    }
    return M


# --------------------------------------------------------------------------
# scene
# --------------------------------------------------------------------------
def import_variant(variant, mats):
    objs = []
    for v in ("vehicle", variant):
        d = MESH / v
        for entry in json.loads((d / "manifest.json").read_text()):
            bpy.ops.wm.stl_import(filepath=str(d / entry["file"]), global_scale=0.001)
            ob = bpy.context.selected_objects[0]
            ob.name = entry["name"]
            bm = bmesh.new()
            bm.from_mesh(ob.data)
            bmesh.ops.remove_doubles(bm, verts=bm.verts, dist=2e-5)
            bm.to_mesh(ob.data)
            bm.free()
            ob.data.materials.clear()
            ob.data.materials.append(mats[entry["material"]])
            ob["material"] = entry["material"]
            objs.append(ob)
    bpy.ops.object.select_all(action="DESELECT")
    for ob in objs:
        ob.select_set(True)
    bpy.context.view_layer.objects.active = objs[0]
    try:
        bpy.ops.object.shade_smooth_by_angle(angle=math.radians(35))
    except Exception:
        bpy.ops.object.shade_auto_smooth(angle=math.radians(35))
    return objs


def world_hdri(path, strength, rot_deg):
    w = bpy.data.worlds.new("hdri")
    bpy.context.scene.world = w
    w.use_nodes = True
    nt = w.node_tree
    bg = nt.nodes["Background"]
    env = nt.nodes.new("ShaderNodeTexEnvironment")
    env.image = bpy.data.images.load(str(path))
    mp = nt.nodes.new("ShaderNodeMapping")
    mp.inputs["Rotation"].default_value[2] = math.radians(rot_deg)
    tc = nt.nodes.new("ShaderNodeTexCoord")
    nt.links.new(tc.outputs["Generated"], mp.inputs["Vector"])
    nt.links.new(mp.outputs["Vector"], env.inputs["Vector"])
    nt.links.new(env.outputs["Color"], bg.inputs["Color"])
    bg.inputs["Strength"].default_value = strength


def ground(mode):
    bpy.ops.mesh.primitive_plane_add(size=400, location=(0, 0, 0))
    g = bpy.context.active_object
    g.name = "ground"
    if mode in ("day", "xray"):
        g.is_shadow_catcher = True
        g.data.materials.append(principled("catcher", (0.2, 0.2, 0.2), rough=0.9))
        return
    m = principled("ground_mat", (0.045, 0.043, 0.04), rough=0.75)
    nt = m.node_tree
    tc = nt.nodes.new("ShaderNodeTexCoord")
    n = nt.nodes.new("ShaderNodeTexNoise")
    n.inputs["Scale"].default_value = 60.0
    n.inputs["Detail"].default_value = 12.0
    nt.links.new(tc.outputs["Object"], n.inputs["Vector"])
    ramp = nt.nodes.new("ShaderNodeValToRGB")
    ramp.color_ramp.elements[0].color = (0.025, 0.024, 0.022, 1)
    ramp.color_ramp.elements[1].color = (0.09, 0.085, 0.08, 1)
    nt.links.new(n.outputs["Fac"], ramp.inputs["Fac"])
    b = nt.nodes["Principled BSDF"]
    nt.links.new(ramp.outputs["Color"], b.inputs["Base Color"])
    bp = nt.nodes.new("ShaderNodeBump")
    bp.inputs["Strength"].default_value = 0.4
    nt.links.new(n.outputs["Fac"], bp.inputs["Height"])
    nt.links.new(bp.outputs["Normal"], b.inputs["Normal"])
    g.data.materials.append(m)


def add_spot(loc, direction, energy, angle_deg, color=(0.85, 0.92, 1.0), blend=0.35, radius=0.05):
    ld = bpy.data.lights.new("spot", "SPOT")
    ld.energy = energy
    ld.spot_size = math.radians(angle_deg)
    ld.spot_blend = blend
    ld.color = color
    ld.shadow_soft_size = radius
    ob = bpy.data.objects.new("spot", ld)
    bpy.context.collection.objects.link(ob)
    ob.location = loc
    ob.rotation_euler = Vector(direction).to_track_quat("-Z", "Y").to_euler()


def led_beams(objs, scale=1.0):
    """Physical beam throw from each lit LED: spot lights aimed per mount position."""
    for ob in objs:
        mat = ob.get("material", "")
        if mat not in ("led_white", "led_halo", "led_amber", "headlight"):
            continue
        c = sum((ob.matrix_world @ Vector(v) for v in ob.bound_box), Vector()) / 8
        dims = ob.dimensions
        col = (1.0, 0.5, 0.1) if mat == "led_amber" else (0.85, 0.92, 1.0)
        k = 0.25 if mat == "led_amber" else 1.0
        if mat == "headlight":
            add_spot(c + Vector((0.1, 0, 0)), (1, 0, -0.1), 1500 * scale, 70, blend=0.8)
        elif c.x > 0.2:
            n = max(1, int(dims.y / 0.35))
            for i in range(n):
                y = c.y - dims.y / 2 + (i + 0.5) * dims.y / n
                add_spot((c.x + 0.08, y, c.z), (1, 0, -0.07), 14000 * k * scale / n, 70, col, blend=0.8, radius=0.1)
        elif c.x < -2.0:
            add_spot((c.x - 0.08, c.y, c.z), (-1, 0, -0.35), 1200 * k * scale, 110, col, blend=0.9, radius=0.15)
        elif mat == "led_halo":
            for s in (-1, 1):
                add_spot((c.x, s * (dims.y / 2 + 0.05), c.z), (0, s, -0.6), 900 * scale, 130, col, blend=0.95, radius=0.2)
        else:
            s = 1 if c.y > 0 else -1
            add_spot((c.x, c.y + s * 0.08, c.z), (0, s, -0.55), 1200 * k * scale, 120, col, blend=0.9, radius=0.15)


CAMS = {
    #            location (m)              look-at          lens
    "front34":  ((7.6, -5.9, 2.75),        (-0.2, 0.0, 1.45), 42),
    "front34_hi": ((7.4, -6.0, 3.9),       (-0.3, 0.0, 1.6), 50),
    "rear34":   ((-8.4, -6.0, 3.3),        (-1.0, 0.0, 1.7), 40),
    "side":     ((0.4, -11.5, 1.4),        (-0.4, 0.0, 1.2), 50),
    "top34":    ((-3.6, -3.4, 4.6),        (-1.4, 0.0, 2.05), 40),
    "night_front": ((8.6, -5.2, 2.7),      (0.2, 0.0, 1.45), 40),
    "dusk34":   ((-4.2, -8.4, 2.5),        (-0.7, 0.0, 1.35), 38),
}


def camera(preset):
    loc, tgt, lens = CAMS[preset]
    cd = bpy.data.cameras.new("cam")
    cd.lens = lens
    cd.sensor_width = 36
    cd.dof.use_dof = True
    cd.dof.aperture_fstop = 8.0
    ob = bpy.data.objects.new("cam", cd)
    bpy.context.collection.objects.link(ob)
    ob.location = loc
    d = Vector(tgt) - Vector(loc)
    ob.rotation_euler = d.to_track_quat("-Z", "Y").to_euler()
    cd.dof.focus_distance = d.length
    bpy.context.scene.camera = ob


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--variant", required=True)
    ap.add_argument("--hdri", required=True)
    ap.add_argument("--hdri-dir", default=os.environ.get("HDRI_DIR", str(ROOT / "build" / "hdri")))
    ap.add_argument("--hdri-strength", type=float, default=1.0)
    ap.add_argument("--hdri-rot", type=float, default=0.0)
    ap.add_argument("--cam", default="front34")
    ap.add_argument("--mode", default="day", choices=["day", "dusk", "night", "xray"])
    ap.add_argument("--res", default="1920x1080")
    ap.add_argument("--samples", type=int, default=160)
    ap.add_argument("--exposure", type=float, default=0.0)
    ap.add_argument("--out", required=True)
    a = ap.parse_args()

    bpy.ops.wm.read_factory_settings(use_empty=True)
    sc = bpy.context.scene
    sc.render.engine = "CYCLES"
    sc.cycles.device = "CPU"
    sc.cycles.samples = a.samples
    sc.cycles.use_denoising = True
    sc.cycles.max_bounces = 8
    sc.cycles.transparent_max_bounces = 16
    sc.render.resolution_x, sc.render.resolution_y = map(int, a.res.split("x"))
    sc.render.resolution_percentage = 100
    sc.view_settings.view_transform = "AgX"
    try:
        sc.view_settings.look = "AgX - Medium High Contrast"
    except TypeError:
        pass
    sc.view_settings.exposure = a.exposure
    sc.render.image_settings.file_format = "PNG"

    mats = build_materials(a.mode)
    objs = import_variant(a.variant, mats)
    world_hdri(Path(a.hdri_dir) / a.hdri, a.hdri_strength, a.hdri_rot)
    ground(a.mode)
    if a.mode in ("night", "dusk"):
        led_beams(objs, scale=1.0)
    camera(a.cam)
    sc.render.filepath = str(Path(a.out).resolve())
    bpy.ops.render.render(write_still=True)
    print("wrote", sc.render.filepath)


if __name__ == "__main__":
    main()
