"""Blender helpers for a set built to match storyboard panels. Run inside Blender (4.2 LTS tested era):

  blender -b set.blend -P set_tools.py -- camera CAM_01 3.8 -2.4 1.28  -0.8 4.2 1.35  35
      place CAM_01 at (x,y,z) looking at (tx,ty,tz), focal length mm, roll 0 (horizon level); saves the .blend
  blender -b set.blend -P set_tools.py -- continuity CAM_01,CAM_02 Mailbox,Walkway,House Talent
      for each camera: screen-x order of the listed props (must be the same story in every shot),
      plus the angle between consecutive cameras around the subject (30-degree rule)
  blender -b set.blend -P set_tools.py -- depth CAM_01 out/CAM_01_depth.npy [960 640]
      render the Z pass for a camera and save it as float32 .npy (metres) -- done INSIDE Blender because
      OpenCV builds without OpenEXR can't read the EXR
  blender -b COPY.blend -P set_tools.py -- glb out/set.glb
      export a GLB for the browser tour. Always from a COPY of the .blend, never the file a render is using.
UNTESTED as a combined script: generalized from the job's per-round scripts.
"""
import sys, math
import bpy
from mathutils import Vector
from bpy_extras.object_utils import world_to_camera_view

argv = sys.argv[sys.argv.index('--') + 1:] if '--' in sys.argv else []
cmd, args = argv[0], argv[1:]
scene = bpy.context.scene

def look_at(cam, target):
    d = Vector(target) - cam.location
    cam.rotation_euler = d.to_track_quat('-Z', 'Y').to_euler()     # -Z forward, Y up -> roll 0

if cmd == 'camera':
    name, x, y, z, tx, ty, tz, lens = args[0], *map(float, args[1:8])
    cam = bpy.data.objects.get(name) or bpy.data.objects.new(name, bpy.data.cameras.new(name))
    if cam.name not in scene.collection.all_objects: scene.collection.objects.link(cam)
    cam.location = (x, y, z); look_at(cam, (tx, ty, tz)); cam.data.lens = lens
    bpy.ops.wm.save_mainfile(); print(f'{name} at {x,y,z} -> {tx,ty,tz} {lens} mm')

elif cmd == 'continuity':
    cams, props, subject = args[0].split(','), args[1].split(','), args[2]
    prev = None; ok = True
    for c in cams:
        cam = bpy.data.objects[c]
        xs = {p: world_to_camera_view(scene, cam, bpy.data.objects[p].matrix_world.translation).x for p in props}
        order = [p for p, _ in sorted(xs.items(), key=lambda kv: kv[1])]
        vis = {p: 0 <= v <= 1 for p, v in xs.items()}
        print(f'{c}: left->right {order}  in-frame {vis}')
        subj = bpy.data.objects[subject].matrix_world.translation
        v = (cam.location - subj).normalized()
        if prev is not None:
            ang = math.degrees(prev.angle(v)); print(f'  angle vs previous camera around {subject}: {ang:.1f} deg', '' if ang >= 30 else '<30: JUMP-CUT RISK')
            ok &= ang >= 30
        prev = v
    print('CONTINUITY', 'PASS' if ok else 'CHECK', '(compare the left->right orders against the panels by eye)')

elif cmd == 'depth':
    cam, out = bpy.data.objects[args[0]], args[1]
    if len(args) >= 4: scene.render.resolution_x, scene.render.resolution_y = int(args[2]), int(args[3])
    scene.camera = cam; scene.render.resolution_percentage = 100
    scene.view_layers[0].use_pass_z = True; scene.use_nodes = True
    nt = scene.node_tree; rl = nt.nodes.get('Render Layers') or nt.nodes.new('CompositorNodeRLayers')
    viewer = nt.nodes.get('Viewer') or nt.nodes.new('CompositorNodeViewer'); viewer.use_alpha = False
    nt.links.new(rl.outputs['Depth'], viewer.inputs['Image'])
    if scene.render.engine == 'CYCLES': scene.cycles.samples = 1                 # depth doesn't need samples
    bpy.ops.render.render()
    import numpy as np
    img = bpy.data.images['Viewer Node']; w, h = img.size
    z = np.array(img.pixels[:], np.float32).reshape(h, w, 4)[::-1, :, 0]          # flip to image rows
    np.save(out, z); print('depth', out, z.shape, 'range', float(z.min()), float(z[z < 1e5].max()))

elif cmd == 'glb':
    bpy.ops.export_scene.gltf(filepath=args[0], export_format='GLB', export_cameras=True, export_apply=True)
    print('exported', args[0])
