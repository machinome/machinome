"""Spike helper, run inside Blender headless:
  blender -b --python blender_check.py -- thor.glb OUT_DIR

Imports the GLB with Blender's own importer, reports what arrived (objects,
hierarchy, actions), renders the Home pose, then poses Park by rotating the
joint objects and renders again.
"""
import bpy, sys, json, math
from mathutils import Vector, Quaternion

argv = sys.argv[sys.argv.index('--') + 1:]
glb, out = argv[0], argv[1]
bpy.ops.wm.read_factory_settings(use_empty=True)
bpy.ops.import_scene.gltf(filepath=glb)
objs = bpy.data.objects
meshes = [o for o in objs if o.type == 'MESH']
report = dict(
    objects=len(objs), meshes=len(meshes), empties=sum(1 for o in objs if o.type == 'EMPTY'),
    triangles=sum(sum(len(p.vertices) - 2 for p in o.data.polygons) for o in meshes),
    actions=sorted(a.name for a in bpy.data.actions),
    top_level=[o.name for o in objs if o.parent is None],
    joint_chain=[],
)
for name in ('shoulder', 'art2', 'art3', 'art4', 'art56', 'output'):
    o = objs.get(name)
    report['joint_chain'].append(dict(name=name, present=o is not None, descendants=len(o.children_recursive) if o else None))

scene = bpy.context.scene
scene.render.engine = 'CYCLES'
scene.cycles.samples = 24
scene.cycles.device = 'CPU'
scene.render.resolution_x, scene.render.resolution_y = 900, 700
scene.render.film_transparent = False
world = bpy.data.worlds.new('w'); scene.world = world; world.use_nodes = True
world.node_tree.nodes['Background'].inputs[0].default_value = (0.96, 0.96, 0.95, 1)
world.node_tree.nodes['Background'].inputs[1].default_value = 1.0
sun = bpy.data.lights.new('sun', 'SUN'); sun.energy = 3.0
sun_o = bpy.data.objects.new('sun', sun); scene.collection.objects.link(sun_o)
sun_o.rotation_euler = (math.radians(50), math.radians(10), math.radians(35))
cam = bpy.data.objects.new('cam', bpy.data.cameras.new('cam')); scene.collection.objects.link(cam); scene.camera = cam
cam.data.lens = 50


def frame_all():
    bpy.context.view_layer.update()
    pts = [o.matrix_world @ Vector(c) for o in meshes for c in o.bound_box]
    lo = Vector((min(p.x for p in pts), min(p.y for p in pts), min(p.z for p in pts)))
    hi = Vector((max(p.x for p in pts), max(p.y for p in pts), max(p.z for p in pts)))
    center, radius = (lo + hi) / 2, (hi - lo).length / 2
    direction = Vector((1.0, -1.15, 0.55)).normalized()
    dist = radius / math.sin(min(cam.data.angle_x, cam.data.angle_y) / 2) * 1.08
    cam.location = center + direction * dist
    cam.rotation_euler = (center - cam.location).to_track_quat('-Z', 'Y').to_euler()


def render(name):
    frame_all()
    scene.render.filepath = f'{out}/blender-{name}.png'
    bpy.ops.render.render(write_still=True)


# Blender's importer binds the first clip's actions to the objects, so frame 1 is the
# start of "Park" (the Home pose) and the clip's last frame is the Park pose.
scene.frame_set(1)
render('home')
bound = [o for o in objs if o.animation_data and o.animation_data.action]
report['objects_with_clip_bound'] = len(bound)
last = max(int(o.animation_data.action.frame_range[1]) for o in bound) if bound else 1
report['park_clip_last_frame'] = last
scene.frame_set(last)
render('park-clip')
# The formula route: clear the clip bindings and set the three joints by rotation.
# The joint's axis is read from the extras Blender imported as a custom property, in glTF
# coordinates; the importer converts every node Y-up -> Z-up as (x, y, z) -> (x, -z, y).
for o in objs:
    if o.animation_data:
        o.animation_data_clear()
scene.frame_set(1)
report['park_axes'] = {}
for name, deg in (('art2', 80), ('art3', -135), ('art56', 80)):
    o = objs[name]
    axis = list(o['machinome']['axis']) if 'machinome' in o.keys() else None
    report['park_axes'][name] = axis
    ax, ay, az = axis
    o.rotation_mode = 'QUATERNION'
    o.rotation_quaternion = Quaternion((ax, -az, ay), math.radians(deg))
render('park-posed')
report['renders'] = ['blender-home.png', 'blender-park-clip.png', 'blender-park-posed.png']
json.dump(report, open(f'{out}/blender-report.json', 'w'), indent=1)
print('BLENDER_REPORT', json.dumps(report))
