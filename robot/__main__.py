import json, math, sys

from OpenGL.GL import *

from robot.spatial import vector3
Vector3 = vector3.Vector3

from robot.common          import Bindings, logger, Timer
from robot.mech.serial     import Serial
from robot.mech.simulation import Simulation
from robot.spatial.euler   import Axes, Order
from robot.spatial         import Matrix4, Mesh, Transform, Quaternion
from robot.traj.linear_js  import LinearJS
from robot.traj.linear_os  import LinearOS
from robot.visual.filetypes.stl.stl_parser import STLParser
from robot.visual.opengl.buffer            import Buffer
from robot.visual.opengl.shader_program    import ShaderProgram
from robot.visual.opengl.uniform_buffer    import Mapping, UniformBuffer

import robot.visual as vis

import robot.visual.entities as entities

from robot.visual.entities import tool_entity

if __name__ == "__main__":
  with Timer('Initialize Window') as t:
    window = vis.Window(750, 750, "robotpy")

  renderer = vis.Renderer()
  renderer.initialize_shaders([
    'serial', 'flat', 'grid', 'billboard', 'com'
  ])

  grid = entities.GridEntity(renderer.shaders.get('grid'))
  welder = tool_entity.load('./robot/mech/tools/welder.json')
  welder.shader_program = renderer.shaders.get('serial')

  with Timer('Load Robot and Construct Mesh') as t:
    with open('./robot/mech/robots/abb_irb_120.json') as json_file:
      serial_dictionary = json.load(json_file)

      if 'mesh_file' in serial_dictionary.keys():
        meshes = Mesh.from_file(vis.STLParser(), f'./robot/mech/robots/meshes/{serial_dictionary["mesh_file"]}')

      serials = [Serial.from_dict_meshes(serial_dictionary, meshes or []) for _ in range(2)]

  sim = Simulation()
  sim.entities.append(serials[0])
  sim.entities.append(serials[1])

  serial_buffer = Buffer.from_meshes(meshes)

  p = STLParser()
  mesh = Mesh.from_file(p, './robot/visual/meshes/frame.stl')
  frame_buffer = Buffer.from_meshes(mesh)

  def serial_per_instance(serial: Serial, sp: ShaderProgram, color = None):
    color = color or [1, 1, 1]

    sp.uniforms.model_matrices  = serial.poses()
    sp.uniforms.use_link_colors = False
    sp.uniforms.link_colors     = [link.color for link in serial.links]
    sp.uniforms.robot_color     = color

  def frame_per_instance(serial: Serial, sp: ShaderProgram, scale: float = 1., opacity: float = 1.):
    sp.uniforms.model_matrix = serial.pose()
    sp.uniforms.scale_matrix = Matrix4([
      scale, 0, 0, 0,
      0, scale, 0, 0,
      0, 0, scale, 0,
      0, 0, 0, 1
    ])
    sp.uniforms.in_opacity = opacity

  renderer.register_entity_type(
    name         = 'serial',
    shader_name  = 'serial',
    buffer       = serial_buffer,
    per_instance = serial_per_instance
    # adder        = adder_function
  )

  renderer.register_entity_type(
    name         = 'frame',
    shader_name  = 'flat',
    buffer       = frame_buffer,
    per_instance = frame_per_instance
    # adder        = adder_function
  )

  # buffer_instance.set_attribute_locations(sp)


  # robot_1 = renderer.add_many('serial', serial, parent)
  # coms = renderer.add_many('com', serials[0].links, robot_1)
  # frames = renderer.add_many('frames', serials.links, robot_1)

  serials[0].to_world = Transform.from_orientation_translation(
    Quaternion.from_euler([math.radians(0), 0, 0], Axes.ZYZ, Order.INTRINSIC),
    Vector3(-400, 400, 0))

  serials[0].traj = LinearOS(
    serials[0],
    [
      Vector3(150, 320, 630),
      Vector3(374, 160, 430),
      Vector3(374, 0, 630),
      Vector3(275, -320, 330),
      Vector3(500, 320, 330),
      Vector3(150, 320, 630)],
    8)

  serials[1].to_world = Transform.from_orientation_translation(
    Quaternion.from_euler([math.radians(0), 0, 0], Axes.ZYZ, Order.INTRINSIC),
    Vector3(0, 0, 0))
  serials[1].attach(welder.tool)

  serials[1].traj = LinearOS(
    serials[1],
    [
      Vector3(644, 0, 588.2),
      Vector3(644, 0, 430),
      Vector3(444, 120, 430),
      Vector3(744, 10, 330),
      Vector3(644, 0, 588.2)
    ],
    3)

  renderer.add('serial', serials[0], None, color=[1, 0.5, 0])
  renderer.add('serial', serials[1], None, color=[0.5, 1, 0])

  renderer.add('frame', serials[0], None, scale=15)
  renderer.add('frame', serials[1], None, scale=15)

  camera = vis.Camera(Vector3(0, -1250, 375), Vector3(0, 0, 350), Vector3(0, 0, 1))

  # world_frame = entities.FrameEntity(Transform(), renderer.shaders.get('flat'))
  light = vis.AmbientLight(Vector3(0, -750, 350), Vector3(1, 1, 1), 0.3)

  scene = vis.Scene(camera, light)

  bindings = Bindings()
  settings = vis.CameraSettings()
  camera_controller = vis.CameraController(camera, settings, bindings, scene, window)
  triangle = entities.TriangleEntity(camera_controller, renderer.shaders.get('billboard'))

  scene.entities.append(grid)
  scene.entities.append(serials[0])
  scene.entities.append(serials[1])
  scene.entities.append(triangle)

  for link in serials[0].links:
    com = entities.COMEntity(link, renderer.shaders.get('com'))
    scene.entities.append(com)

  matrix_ub = UniformBuffer("Matrices", 1)

  matrix_ub.bind(Mapping(
    camera, ['projection.matrix', 'world_to_camera']
  ))

  light_ub = UniformBuffer("Light", 2)

  light_ub.bind(Mapping(
    light, ['position', 'color', 'intensity']
  ))

  renderer.ubos = [matrix_ub, light_ub]

  window.run()