### Don't run me directly!
### Load the file demo/tessagon_demo.blend into blender, it will run me
### Run the demo first to create the objects, and I will render them

import math, re, os
import bpy
from importlib import reload
import tessagon
reload(tessagon)

from tessagon.types import *
from tessagon.misc.shapes import *

from tessagon.adaptors.blender_adaptor import BlenderAdaptor

def main():
  classes = [HexTessagon,
             SquareTessagon,
             TriTessagon,
             DissectedSquareTessagon,
             FloretTessagon,
             RhombusTessagon,
             OctoTessagon,
             HexTriTessagon,
             HexSquareTriTessagon,
             PythagoreanTessagon,
             BrickTessagon,
             DodecaTessagon,
             ZigZagTessagon,
             SquareTriTessagon,
             WeaveTessagon,
             HexBigTriTessagon]
  setup_render_scene()
  render_tessagons(classes)
  setup_thumbnail_scene()
  render_thumbnails(classes)

def setup_render_scene():
  scn = bpy.context.scene
  set_layer(scn)
  scn.render.resolution_x = 400
  scn.render.resolution_y = 300
  scn.render.resolution_percentage = 100
  scn.render.use_freestyle = True
  scn.render.line_thickness = 0.5
  scn.render.layers[0].freestyle_settings.linesets[0].select_edge_mark = True

  if 'Camera' not in bpy.data.objects:
    cam_data = bpy.data.cameras.new('Camera')
    camera = bpy.data.objects.new('Camera', cam_data)
  else:
    camera = bpy.data.objects['Camera']
  if 'Camera' not in scn.objects: scn.objects.link(camera)
  set_layer(camera)
  camera.location = [0, -17, 0]
  camera.rotation_euler = [pi/2, 0, 0]
  scn.camera = camera

  for area in bpy.context.screen.areas:
    if area.type == 'VIEW_3D':
      for region in area.regions:
        if region.type == 'WINDOW':
          override = {'area': area, 'region': region}
          bpy.ops.view3d.snap_cursor_to_center(override)
          area.spaces[0].pivot_point = 'CURSOR'
          bpy.ops.view3d.viewnumpad(override, type='CAMERA')
          camera.select = True
          for ob in scn.objects:
            if ob != camera:
              ob.select = False
          scn.objects.active = camera
          bpy.ops.transform.rotate(override, value=-math.pi/6, axis=(1, 0, 0))
          break

  lamps = {}
  for name in ['MainLight', 'FillLight', 'BackLight']:
    if name not in bpy.data.objects:
      lamp_data = bpy.data.lamps.new(name, 'POINT')
      lamps[name] = bpy.data.objects.new(name, lamp_data)
      scn.objects.link(lamps[name])
    else:
      lamps[name] = bpy.data.objects[name]
    if name not in scn.objects: scn.objects.link(lamps[name])
    set_layer(lamps[name])
  lamps['MainLight'].location = [-5, -10, 5]
  lamps['FillLight'].location = [ 10, -30, 5]
  lamps['BackLight'].location = [-10, 50, 5]

  lamps['MainLight'].data.energy = 5.0
  lamps['FillLight'].data.energy = 5.0

  scn.world.horizon_color = [1, 1, 1]

def setup_thumbnail_scene():
  scn = bpy.context.scene
  set_layer(scn)
  scn.render.resolution_x = 100
  scn.render.resolution_y = 75
  camera = bpy.data.objects['Camera']
  camera.location = [0, -17, 0]
  camera.rotation_euler = [pi/2, 0, 0]
  camera.data.lens = 120.0

def set_layer(thing, layer = 1):
  thing.layers[layer] = True
  for i in range(20):
    if i != layer: thing.layers[i] = False

def render_tessagons(classes):
  for cls in classes:
    render_class(cls)

  render_object(['HexTorusIn','WireTorusOut'],
                filename='wire_skin.png', mark_edges=False)

def render_thumbnails(classes):
  for cls in classes:
    render_class(cls, thumbnail = True)

def render_class(cls, **kwargs):
  class_name = cls.__name__
  render_object(class_name, **kwargs)
  if kwargs.get('thumbnail'): return
  for i in range(cls.num_color_patterns()):
    object_name = "%sColor%d" % (class_name, i+1)
    render_object(object_name, **kwargs)

def render_object(name, **kwargs):
  if isinstance(name, list):
    names = name
  else:
    names = [name]
  objects = [get_object(name) for name in names]
  for object in objects:
    if not object: return

  for object in objects:
    prepare_object_for_render(object, **kwargs)
    set_layer(object)

  # Writing PNG to /tmp or DOCUMENTATION_IMAGES_DIR
  dir = os.getenv('DOCUMENTATION_IMAGES_DIR') or '/tmp'
  filename = kwargs.get('filename') or get_filename(names[0])
  if kwargs.get('thumbnail'):
    filename += '_thumb'
  path = "%s/%s" % (dir, filename)

  print("Rendering and writing: %s" % path)
  bpy.context.scene.render.filepath = path
  bpy.ops.render.render(write_still = True)
  for object in objects:
    set_layer(object, 0)

def prepare_object_for_render(object, **kwargs):
  object.location = [0, 0, 0]

  mesh = object.data
  mesh.show_double_sided = True
  mesh.use_auto_smooth = True
  mesh.auto_smooth_angle = math.pi / 6
  mark_edges = kwargs.get('mark_edges')
  if mark_edges == None: mark_edges = True
  if mark_edges:
    for edge in mesh.edges:
      edge.use_freestyle_mark = True
  mesh.update()

def get_filename(name, **kwargs):
  # Convert class name to camelcase
  s1 = re.sub('(.)([A-Z][a-z]+)', r'\1_\2', name)
  return re.sub('([a-z0-9])([A-Z])', r'\1_\2', s1).lower()

def get_object(name):
  if name not in bpy.data.objects:
    print("%s not found, skipping!" % (name))
    return None
  return bpy.data.objects[name]

