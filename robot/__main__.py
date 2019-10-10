import json, math

import OpenGL.GL as gl

from robot.common          import Bindings, Timer
from robot.mech            import Serial, Simulation
from robot.mech            import tool
from robot.mech.views      import SerialView, FrameView
from robot.spatial.euler   import Axes, Order
from robot.spatial         import Matrix4, Mesh, Transform, Quaternion, Vector3
from robot.traj.linear_os  import LinearOS
from robot.visual.renderer          import Renderer
from robot.visual.filetypes.stl.stl_parser import STLParser
from robot.visual.messaging.listener       import listen, listener
from robot.visual.messaging.event          import Event
from robot.visual.gui.widgets.rectangle    import Rectangle
from robot.visual.gui.widgets.text         import Text
from robot.visual.opengl.buffer            import Buffer
from robot.visual.opengl.shader_program    import ShaderProgram
from robot.visual.opengl.uniform_buffer    import Mapping, UniformBuffer

import robot.instance_functions as pif

import robot.visual as vis

def setup():
  with Timer('Initialize Window') as t:
    window = vis.Window(1500, 750, "robotpy")

  sim = Simulation()

  grid_buffer = Buffer.from_points([
    Vector3( 0.5,  0.5,  0,),
    Vector3(-0.5,  0.5,  0,),
    Vector3(-0.5, -0.5,  0,),
    Vector3(-0.5, -0.5,  0,),
    Vector3( 0.5, -0.5,  0,),
    Vector3( 0.5,  0.5,  0,)
  ])

  p = STLParser()
  mesh = Mesh.from_file(p, './robot/visual/meshes/frame.stl')
  frame_buffer = Buffer.from_meshes(mesh)

  camera = vis.Camera(Vector3(0, -1250, 375), Vector3(0, 0, 350), Vector3(0, 0, 1))
  light = vis.AmbientLight(Vector3(0, -750, 350), Vector3(1, 1, 1), 0.3)
  renderer = vis.Renderer(camera, light)

  # renderer.register_entity_type(
  #   name         = 'grid',
  #   buffer       = grid_buffer,
  # )

  renderer.register_entity_type(
    view_type    = FrameView,
    buffer       = frame_buffer,
  )

  # renderer.add('grid', None, None, scale=10000)

  renderer.add('trajectory', serials[0], None)

  bindings = Bindings()
  settings = vis.CameraSettings()
  camera_controller = vis.CameraController(camera, settings, bindings, sim, window)

  matrix_ub = UniformBuffer("Matrices", 1)

  matrix_ub.bind(Mapping(
    camera, ['projection.matrix', 'world_to_camera']
  ))

  light_ub = UniformBuffer("Light", 2)

  light_ub.bind(Mapping(
    light, ['position', 'color', 'intensity']
  ))

  renderer.ubos = [matrix_ub, light_ub]

  return window, sim, renderer, camera_controller

def load_serial(load_mesh: bool = True) -> Serial:
  with Timer('Load Robot and Construct Mesh') as t:
    with open('./robot/mech/robots/abb_irb_120.json') as json_file:
      serial_dictionary = json.load(json_file)

    if load_mesh and 'mesh_file' in serial_dictionary.keys():
      meshes = Mesh.from_file(vis.STLParser(), f'./robot/mech/robots/meshes/{serial_dictionary["mesh_file"]}')
    else:
      meshes = []

    return [Serial.from_dict_meshes(serial_dictionary, meshes) for _ in range(2)]

from robot.visual.gui import GUI, Widget
from robot.visual.gui.widgets.interface import Interface
from robot.visual.gui.widgets.viewport import Viewport
from robot.visual.gui.widgets.slider import Slider

if __name__ == "__main__":
  window, sim, renderer, camera_controller = setup()

  serials = load_serial()
  serial  = serials[0]
  serial1 = serials[1]
  serial1.to_world = Transform.from_axis_angle_translation(
    translation=Vector3(500, 500, 0)
  )
  serial_buffer = Buffer.from_meshes(serial.meshes)

  interface = Interface(fixed_size=True)

  sliders = []
  for joint_index in range(1, 7):
    interface.add_joint_controller(joint_index, Slider(
      name     = f'Axis #{joint_index}',
      fixed_size = True,
      scale     = 2,
    ))

  interface.layout(5, 10, 15, 20)

  rectangle_buffer = Buffer.from_points([
    Vector3( 1,  0),
    Vector3( 0,  0),
    Vector3( 0,  1),
    Vector3( 0,  1),
    Vector3( 1,  1),
    Vector3( 1,  0)
  ])

  f = Font(32, 16, [])
  u, v = f.uvs('?')[0]
  width = 0.0625

  text_buffer = Buffer.from_points_textured([
    ([1,  0,  0],  [u+width,  v+width]), # Top Right
    ([0,  0,  0],  [u,  v+width]), # Top Left
    ([0,  1,  0],  [u,  v]), # Bottom Left
    ([0,  1,  0],  [u,  v]), # Bottom Left
    ([1,  1,  0],  [u+width,  v]), # Bottom Right
    ([1,  0,  0],  [u+width,  v+width]), # Top Right
  ])

  renderer.register_entity_type(
    view_type    = SerialView,
    buffer       = serial_buffer,
  )

  renderer.register_entity_type(
    view_type    = Rectangle,
    buffer       = rectangle_buffer,
  )

  renderer.register_entity_type(
    view_type    = Text,
    shader_name  = 'character',
    buffer       = text_buffer,
  )

  controller = SerialController(serial)
  controller1 = SerialController(serial1)

  renderer.add(controller.view)
  renderer.add(controller1.view)
  renderer.add(interface.children['bg'])
  for slider in interface.joint_controllers.values():
    renderer.add_many(slider.children.values())

  t1 = Text("", f, position=Vector3(0.25, 0.25), color=[0]*3)
  t2 = Text("", f, position=Vector3(0.25, 0.35), color=[0]*3)
  t3 = Text("", f, position=Vector3(0.25, 0.45), color=[0]*3)
  t4 = Text("", f, position=Vector3(0.25, 0.55), color=[0]*3)
  t5 = Text("", f, position=Vector3(0.25, 0.65), color=[0]*3)
  t6 = Text("", f, position=Vector3(0.25, 0.75), color=[0]*3)
  controller.texts = [t1, t2, t3, t4, t5, t6]

  renderer.add_many(controller.texts)
  sim.controllers.append(controller)
  sim.controllers.append(controller1)

  vp = Viewport(sim, camera_controller)
  g = GUI()
  g.add(vp)
  g.add(interface)

  window.run(fps_limit = 60)