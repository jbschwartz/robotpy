import json, math

import OpenGL.GL as gl

from robot.common          import Bindings, Timer
from robot.mech            import Serial, Simulation
from robot.mech            import tool
from robot.spatial.euler   import Axes, Order
from robot.spatial         import Matrix4, Mesh, Transform, Quaternion, Vector3
from robot.traj.linear_os  import LinearOS
from robot.visual.renderer          import Renderer
from robot.visual.filetypes.stl.stl_parser import STLParser
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
  #   per_instance = pif.grid
  # )

  renderer.register_entity_type(
    name         = 'frame',
    shader_name  = 'frame',
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
  interface = Interface()
  interface.width = 0.1875

  number_of_sliders = 6
  slider_height     = 0.1
  slider_width      = 1
  space_height      = (1 - number_of_sliders * slider_height) / (number_of_sliders + 1)

  sliders = []

  y = space_height
  for joint_index in range(1, number_of_sliders + 1):

    interface.add_joint_controller(joint_index, Slider(
      name     = f'Axis #{joint_index}',
      position = Vector3(0.05, y),
      width    = slider_width - 0.1,
      height   = slider_height
    ))
    y += slider_height + space_height


  rectangle_buffer = Buffer.from_points([
    Vector3( 1,  0),
    Vector3( 0,  0),
    Vector3( 0,  1),
    Vector3( 0,  1),
    Vector3( 1,  1),
    Vector3( 1,  0)
  ])

  renderer.register_entity_type(
    name         = 'serial',
    buffer       = serial_buffer,
  )

  renderer.register_entity_type(
    name         = 'rectangle',
    buffer       = rectangle_buffer,
  )

  controller = SerialController(serial)
  controller1 = SerialController(serial1)
  g = GUI()


  renderer.add('serial', controller.view)
  renderer.add('serial', controller1.view)
  renderer.add('rectangle', interface.children['bg'])
  for slider in interface.joint_controllers.values():
    renderer.add_many('rectangle', slider.children.values())

  sim.controllers.append(controller)
  sim.controllers.append(controller1)

  vp = Viewport(sim, camera_controller)
  g.add(vp)
  g.add(interface)

  window.run(fps_limit = 60)