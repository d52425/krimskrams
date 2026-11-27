# -*- coding: utf-8 -*-
"""
Chibi reaper girl — stylized low-poly model built from a 3-view reference sheet.
Run: blender -b --factory-startup -P build_model.py
Outputs (next to this script): chibi-reaper.blend / chibi-reaper.glb / render_*.png
Character faces -Y. Units: metres-ish, total height ~3.0 (incl. scythe ~3.1).
"""
import bpy, math, os
from mathutils import Vector

OUT = os.path.dirname(os.path.abspath(__file__))

# ---------- helpers ----------
def clean():
    bpy.ops.object.select_all(action='SELECT')
    bpy.ops.object.delete()
    for coll in (bpy.data.meshes, bpy.data.curves, bpy.data.cameras, bpy.data.lights):
        pass

def srgb(c):
    return c / 12.92 if c <= 0.04045 else ((c + 0.055) / 1.055) ** 2.4

def mat(name, color, rough=0.75, metallic=0.0):
    m = bpy.data.materials.get(name) or bpy.data.materials.new(name)
    m.use_nodes = True
    bsdf = m.node_tree.nodes["Principled BSDF"]
    bsdf.inputs["Base Color"].default_value = (*[srgb(c) for c in color], 1.0)
    bsdf.inputs["Roughness"].default_value = rough
    bsdf.inputs["Metallic"].default_value = metallic
    return m

MAT = {
    'skin':   mat('skin',   (1.00, 0.85, 0.70)),
    'hair':   mat('hair',   (0.92, 0.26, 0.08)),
    'hair_d': mat('hair_d', (0.80, 0.19, 0.05)),
    'cloak':  mat('cloak',  (0.07, 0.07, 0.10)),
    'purple': mat('purple', (0.38, 0.10, 0.55)),
    'gold':   mat('gold',   (0.85, 0.62, 0.20), rough=0.35, metallic=0.8),
    'bow':    mat('bow',    (0.10, 0.65, 0.90)),
    'eye':    mat('eye',    (0.95, 0.60, 0.05), rough=0.3),
    'eye_d':  mat('eye_d',  (0.25, 0.10, 0.02)),
    'white':  mat('white',  (1.00, 1.00, 1.00), rough=0.25),
    'mouth':  mat('mouth',  (0.55, 0.15, 0.12)),
    'blush':  mat('blush',  (1.00, 0.55, 0.50)),
    'bone':   mat('bone',   (0.85, 0.78, 0.62)),
    'black':  mat('black',  (0.04, 0.04, 0.05), rough=0.5),
    'pole':   mat('pole',   (0.10, 0.08, 0.10), rough=0.45, metallic=0.3),
    'ribbon': mat('ribbon', (0.85, 0.45, 0.65)),
    'bead':   mat('bead',   (0.70, 0.15, 0.15), rough=0.3),
}

def finish(obj, material, smooth=True):
    if material:
        obj.data.materials.append(material)
    if smooth and obj.type == 'MESH':
        for p in obj.data.polygons:
            p.use_smooth = True
    return obj

def sphere(name, loc, scale, material, seg=24, rings=16):
    bpy.ops.mesh.primitive_uv_sphere_add(segments=seg, ring_count=rings, location=loc)
    o = bpy.context.object; o.name = name; o.scale = scale
    bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
    return finish(o, material)

def cone(name, loc, r1, r2, depth, material, rot=(0, 0, 0), verts=16):
    bpy.ops.mesh.primitive_cone_add(vertices=verts, radius1=r1, radius2=r2, depth=depth, location=loc, rotation=rot)
    o = bpy.context.object; o.name = name
    return finish(o, material)

def cyl(name, loc, r, depth, material, rot=(0, 0, 0), verts=20):
    bpy.ops.mesh.primitive_cylinder_add(vertices=verts, radius=r, depth=depth, location=loc, rotation=rot)
    o = bpy.context.object; o.name = name
    return finish(o, material)

def box(name, loc, scale, material, rot=(0, 0, 0)):
    bpy.ops.mesh.primitive_cube_add(location=loc, rotation=rot)
    o = bpy.context.object; o.name = name; o.scale = scale
    bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
    return finish(o, material, smooth=False)

def torus(name, loc, major, minor, material, rot=(0, 0, 0), arc=None, scale=(1, 1, 1)):
    if arc is not None:
        bpy.ops.mesh.primitive_torus_add(major_radius=major, minor_radius=minor,
                                         major_segments=32, minor_segments=10,
                                         abso_major_rad=major, abso_minor_rad=minor,
                                         location=loc, rotation=rot)
        # torus primitive has no arc param via ops; trim via geometry is skipped (full ring hidden inside head/pole is acceptable only for ahoge) -- not used with arc
    else:
        bpy.ops.mesh.primitive_torus_add(major_radius=major, minor_radius=minor,
                                         major_segments=32, minor_segments=10, location=loc, rotation=rot)
    o = bpy.context.object; o.name = name; o.scale = scale
    bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
    return finish(o, material)

def point_cone(name, base_loc, tip_dir, length, radius, material):
    """Cone whose tip points along tip_dir from base_loc."""
    d = Vector(tip_dir).normalized()
    center = Vector(base_loc) + d * (length / 2)
    q = Vector((0, 0, -1)).rotation_difference(d)  # cone tip is +Z when radius2=0? primitive cone points +Z with radius2 at top
    # primitive_cone: radius1 at bottom (-Z), radius2 at top (+Z). We want tip at +dir => align +Z to d
    q = Vector((0, 0, 1)).rotation_difference(d)
    bpy.ops.mesh.primitive_cone_add(vertices=12, radius1=radius, radius2=0.0, depth=length, location=center)
    o = bpy.context.object; o.name = name; o.rotation_mode = 'QUATERNION'; o.rotation_quaternion = q
    return finish(o, material)

clean()

# ---------- cloak (body) ----------
# main robe: tapered cylinder, black
cyl('cloak', (0, 0, 0.78), 0.52, 1.30, MAT['cloak'], verts=24).scale = (1, 0.92, 1)
bpy.context.object.name = 'cloak'  # keep ref simple
# taper: use cone instead for silhouette
bpy.ops.object.select_all(action='SELECT'); bpy.ops.object.delete()
cone('cloak', (0, 0, 0.80), 0.66, 0.30, 1.35, MAT['cloak'], verts=24)
# shoulders / hood behind head
sphere('hood', (0, 0.10, 1.52), (0.42, 0.38, 0.30), MAT['cloak'])
# purple jagged hem: ring of downward spikes
for i in range(14):
    a = (i / 14) * math.tau
    x, y = math.cos(a) * 0.60, math.sin(a) * 0.55
    ln = 0.30 if i % 2 == 0 else 0.20
    point_cone(f'hem{i}', (x, y, 0.28), (math.cos(a) * 0.25, math.sin(a) * 0.25, -1), ln, 0.11, MAT['purple'])
# inner purple layer peeking at front bottom
cone('cloak_inner', (0, -0.06, 0.42), 0.55, 0.40, 0.55, MAT['purple'], verts=24)

# gold neck clasp + hanging drops (front = -Y)
sphere('clasp', (0, -0.335, 1.38), (0.075, 0.05, 0.075), MAT['gold'])
for i, dz in enumerate((0.10, 0.20)):
    sphere(f'clasp_drop{i}', (0, -0.345, 1.38 - dz), (0.032, 0.025, 0.045), MAT['gold'])
sphere('clasp_drop2', (0, -0.345, 1.06), (0.04, 0.03, 0.06), MAT['gold'])

# ---------- feet / hands ----------
for s, nm in ((-1, 'L'), (1, 'R')):
    sphere(f'foot{nm}', (0.20 * s, -0.40, 0.055), (0.115, 0.21, 0.055), MAT['skin'])
# right hand (scythe side, -X) lower, left hand peeking
sphere('hand_scythe', (-0.60, -0.22, 1.02), (0.085, 0.085, 0.10), MAT['skin'])
cone('sleeve_scythe', (-0.50, -0.14, 1.12), 0.13, 0.09, 0.34, MAT['cloak'], rot=(0, -0.7, 0))
sphere('hand_free', (0.56, -0.18, 0.72), (0.075, 0.075, 0.09), MAT['skin'])
cone('sleeve_free', (0.47, -0.10, 0.84), 0.12, 0.085, 0.32, MAT['cloak'], rot=(0, 0.7, 0))

# ---------- head ----------
sphere('head', (0, -0.02, 1.98), (0.58, 0.54, 0.56), MAT['skin'], seg=32, rings=24)
# hair cap: bigger sphere up/back
sphere('hair_main', (0, 0.07, 2.12), (0.635, 0.60, 0.60), MAT['hair'], seg=32, rings=24)
# hair spikes around the sides/back
spikes = [
    ((-0.55, 0.05, 2.30), (-1.0, 0.1, 0.45), 0.55),
    ((-0.62, 0.10, 1.95), (-1.0, 0.15, -0.25), 0.55),
    ((-0.55, 0.05, 1.62), (-0.9, 0.1, -1.0), 0.50),
    ((0.55, 0.05, 2.30), (1.0, 0.1, 0.45), 0.55),
    ((0.62, 0.10, 1.95), (1.0, 0.15, -0.25), 0.55),
    ((0.55, 0.05, 1.62), (0.9, 0.1, -1.0), 0.50),
    ((0.0, 0.55, 2.25), (0.0, 1.0, 0.35), 0.55),
    ((-0.35, 0.48, 1.95), (-0.4, 1.0, -0.3), 0.52),
    ((0.35, 0.48, 1.95), (0.4, 1.0, -0.3), 0.52),
    ((-0.30, 0.40, 1.60), (-0.35, 0.8, -1.0), 0.48),
    ((0.30, 0.40, 1.60), (0.35, 0.8, -1.0), 0.48),
    ((0.0, 0.58, 1.85), (0.0, 1.0, -0.6), 0.50),
]
for i, (loc, d, ln) in enumerate(spikes):
    point_cone(f'hair_spike{i}', loc, d, ln, 0.17, MAT['hair'] if i % 3 else MAT['hair_d'])
# bangs (front, pointing down over forehead)
for i, (x, ln) in enumerate(((-0.34, 0.42), (-0.12, 0.50), (0.12, 0.46), (0.34, 0.40))):
    point_cone(f'bang{i}', (x, -0.47, 2.28), (x * 0.4, -0.35, -1), ln, 0.15, MAT['hair'])
# ahoge (cowlick on top): two small curved spikes, not a ring
point_cone('ahoge1', (0.04, 0.02, 2.66), (0.35, 0.0, 1.0), 0.26, 0.035, MAT['hair_d'])
point_cone('ahoge2', (0.12, 0.02, 2.86), (0.9, 0.0, 0.55), 0.16, 0.026, MAT['hair_d'])

# ---------- face (front = -Y) ----------
for s, nm in ((-1, 'L'), (1, 'R')):
    sphere(f'eye{nm}', (0.225 * s, -0.525, 2.02), (0.095, 0.045, 0.145), MAT['eye'])
    sphere(f'pupil{nm}', (0.225 * s, -0.562, 1.99), (0.048, 0.02, 0.075), MAT['eye_d'])
    sphere(f'shine{nm}', (0.20 * s, -0.568, 2.09), (0.028, 0.012, 0.028), MAT['white'])
    sphere(f'blush{nm}', (0.335 * s, -0.465, 1.86), (0.07, 0.02, 0.035), MAT['blush'])
sphere('mouth', (0, -0.55, 1.79), (0.055, 0.02, 0.042), MAT['mouth'])

# ---------- big blue bow (character's right = -X, head side) ----------
bow_c = Vector((-0.52, -0.30, 2.38))
for s in (-1, 1):
    loop = sphere(f'bow_loop{s}', tuple(bow_c + Vector((0.17 * s, 0, 0.02 * s))), (0.20, 0.07, 0.13), MAT['bow'])
    loop.rotation_euler = (0, 0, 0.5 * s)
sphere('bow_knot', tuple(bow_c), (0.085, 0.075, 0.085), MAT['gold'])
# hanging bead strings from bow
for i in range(3):
    sphere(f'bow_bead{i}', (-0.52, -0.36, 2.22 - 0.09 * i), (0.028, 0.028, 0.028), MAT['gold'] if i % 2 == 0 else MAT['bead'])
sphere('bow_drop', (-0.52, -0.36, 1.92), (0.035, 0.035, 0.055), MAT['bead'])

# ---------- scythe (at -X, held) ----------
pole_x, pole_y = -0.72, -0.22
cyl('scythe_pole', (pole_x, pole_y, 1.55), 0.038, 3.0, MAT['pole'], rot=(0.03, 0.05, 0))
sphere('scythe_butt', (pole_x - 0.07, pole_y, 0.06), (0.05, 0.05, 0.09), MAT['gold'])
# skull under the blade
sphere('skull', (pole_x, pole_y - 0.02, 2.78), (0.115, 0.11, 0.125), MAT['bone'])
box('skull_jaw', (pole_x, pole_y - 0.03, 2.66), (0.075, 0.07, 0.05), MAT['bone'])
for s in (-1, 1):
    sphere(f'skull_eye{s}', (pole_x + 0.05 * s, pole_y - 0.115, 2.80), (0.028, 0.015, 0.035), MAT['black'])
sphere('skull_nose', (pole_x, pole_y - 0.125, 2.74), (0.016, 0.012, 0.025), MAT['black'])
# blade: flattened torus arc is approximated by a scaled, rotated torus segment built from a cone sweep --
# use a curved blade from a torus (full ring mostly hidden by scaling is wrong) -> build crescent from cylinder boolean-free:
# crescent = big flattened sphere minus offset sphere is boolean; instead use a bent cone chain (5 segments) for a tapered curve.
import math as _m
blade_pts = []
for i in range(6):
    t = i / 5.0
    ang = _m.radians(5 + 95 * t)           # sweep out and over, tip curling down
    r = 0.58
    x = pole_x - _m.sin(ang) * r           # blade reaches toward -X
    z = 3.02 + (1 - _m.cos(ang)) * r * 0.52 - t * 0.30
    blade_pts.append((x, pole_y, z))
for i in range(5):
    a, b = Vector(blade_pts[i]), Vector(blade_pts[i + 1])
    mid = (a + b) / 2; d = b - a
    seg = cyl(f'blade{i}', tuple(mid), 0.085 - 0.011 * i, d.length + 0.05, MAT['black'], verts=10)
    seg.scale = (1, 0.32, 1)
    seg.rotation_mode = 'QUATERNION'
    seg.rotation_quaternion = Vector((0, 0, 1)).rotation_difference(d.normalized())
    # flatten across pole axis after orient: approximate is fine at this scale
sphere('blade_hub', (pole_x, pole_y, 3.02), (0.09, 0.06, 0.09), MAT['gold'])
# pink ribbons hanging from skull
for i, dx in enumerate((-0.045, 0.05)):
    rib = box(f'ribbon{i}', (pole_x + dx, pole_y - 0.05, 2.36), (0.038, 0.010, 0.26), MAT['ribbon'])
    rib.rotation_euler = (0.22, 0, 0.28 * (i - 0.5))

# ---------- scene: ground, light, cameras ----------
bpy.ops.mesh.primitive_plane_add(size=30, location=(0, 0, 0))
ground = bpy.context.object; ground.name = 'ground'
gm = mat('ground_m', (0.92, 0.90, 0.86)); ground.data.materials.append(gm)
bpy.ops.object.light_add(type='SUN', location=(3, -4, 6))
sun = bpy.context.object; sun.data.energy = 2.2
sun.rotation_euler = (math.radians(50), 0, math.radians(35))
bpy.ops.object.light_add(type='AREA', location=(-3, -3, 3))
fill = bpy.context.object; fill.data.energy = 250; fill.data.size = 4
world = bpy.data.worlds['World']; world.use_nodes = True
world.node_tree.nodes['Background'].inputs[0].default_value = (0.95, 0.94, 0.92, 1)
world.node_tree.nodes['Background'].inputs[1].default_value = 0.7

def add_cam(name, loc, target=(0, 0, 1.45)):
    bpy.ops.object.camera_add(location=loc)
    cam = bpy.context.object; cam.name = name
    d = Vector(target) - Vector(loc)
    cam.rotation_euler = d.to_track_quat('-Z', 'Y').to_euler()
    cam.data.lens = 55
    return cam

scene = bpy.context.scene
scene.render.engine = 'CYCLES'
scene.cycles.samples = 48
scene.cycles.use_denoising = True
scene.render.resolution_x = 560
scene.render.resolution_y = 700
scene.render.film_transparent = False

cams = {
    'front': add_cam('cam_front', (0, -6.6, 1.8), target=(-0.15, 0, 1.55)),
    'side':  add_cam('cam_side', (6.6, 0, 1.8), target=(0, 0, 1.55)),
    'back':  add_cam('cam_back', (0, 6.6, 1.8), target=(0, 0, 1.55)),
    'hero':  add_cam('cam_hero', (-4.4, -5.4, 2.6), target=(-0.15, 0, 1.55)),
}
for key, cam in cams.items():
    scene.camera = cam
    scene.render.filepath = os.path.join(OUT, f'render_{key}.png')
    bpy.ops.render.render(write_still=True)

scene.camera = cams['hero']
bpy.ops.wm.save_as_mainfile(filepath=os.path.join(OUT, 'chibi-reaper.blend'))
bpy.ops.export_scene.gltf(filepath=os.path.join(OUT, 'chibi-reaper.glb'), export_format='GLB')
print('DONE', OUT)
