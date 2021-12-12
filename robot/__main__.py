import json, math

import OpenGL.GL as gl

from robot.common          import Bindings, Timer
from robot.mech            import Serial, Simulation
from robot.mech            import tool
from robot.spatial.euler   import Axes, Order
from robot.spatial         import Mesh, Transform, Quaternion, Vector3
from robot.traj.linear_os  import LinearOS
from robot.visual.filetypes.stl.stl_parser import STLParser
from robot.visual.opengl.buffer            import Buffer
from robot.visual.opengl.uniform_buffer    import Mapping, UniformBuffer

import robot.instance_functions as pif

import robot.visual as vis

if __name__ == "__main__":
  with Timer('Initialize Window') as t:
    window = vis.Window(750, 750, "robotpy")

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

  triangle_buffer = Buffer.from_points([
    Vector3( 0.5, -0.33, 0),
    Vector3( 0.0,  0.66, 0),
    Vector3(-0.5, -0.33, 0)
  ])

  grid_buffer = Buffer.from_points([
    Vector3( 0.5,  0.5,  0,),
    Vector3(-0.5,  0.5,  0,),
    Vector3(-0.5, -0.5,  0,),
    Vector3(-0.5, -0.5,  0,),
    Vector3( 0.5, -0.5,  0,),
    Vector3( 0.5,  0.5,  0,)
  ])

  welder = tool.load('./robot/mech/tools/welder.json')
  tool_buffer = Buffer.from_mesh(welder.mesh)

  camera = vis.Camera(Vector3(0, -1250, 375), Vector3(0, 0, 350), Vector3(0, 0, 1))
  light = vis.AmbientLight(Vector3(0, -750, 350), Vector3(1, 1, 1), 0.3)
  renderer = vis.Renderer(camera, light)

  renderer.register_entity_type(
    name         = 'serial',
    buffer       = serial_buffer,
    per_instance = pif.serial,
    add_children = pif.serial_add_children
  )

  renderer.register_entity_type(
    name         = 'frame',
    shader_name  = 'frame',
    buffer       = frame_buffer,
    per_instance = pif.frame
  )

  renderer.register_entity_type(
    name         = 'com',
    buffer       = Buffer.Procedural(4),
    per_instance = pif.com,
    draw_mode    = gl.GL_TRIANGLE_STRIP
  )

  renderer.register_entity_type(
    name         = 'triangle',
    shader_name  = 'billboard',
    buffer       = triangle_buffer,
    per_instance = pif.triangle
  )

  renderer.register_entity_type(
    name         = 'grid',
    buffer       = grid_buffer,
    per_instance = pif.grid
  )

  renderer.register_entity_type(
    name         = 'tool',
    shader_name  = 'serial',
    buffer       = tool_buffer,
    per_instance = pif.tool
  )

  trajectory_buffer = Buffer.from_points([
    Vector3(150, 320, 630),
    Vector3(374, 160, 430),
    Vector3(374, 0, 630),
    Vector3(275, -320, 330),
    Vector3(500, 320, 330),
    Vector3(150, 320, 630)
  ])

  renderer.register_entity_type(
    name         = 'trajectory',
    shader_name  = 'frame',
    buffer       = trajectory_buffer,
    per_instance = pif.trajectory,
    draw_mode    = gl.GL_LINE_STRIP
  )

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
  serials[1].attach(welder)

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

  renderer.add_many('serial', serials, None, color=([1, 0.5, 0], [0.5, 1, 0]))

  renderer.add('triangle', camera, None, scale=20)

  renderer.add('grid', None, None, scale=10000)

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

  window.run(fps_limit = 60)