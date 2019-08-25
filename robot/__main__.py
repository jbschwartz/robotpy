import json, math, sys

from OpenGL.GL import *

from robot.spatial import vector3
Vector3 = vector3.Vector3

from robot.common          import Bindings, logger, Timer
from robot.mech.serial     import Serial
from robot.spatial.euler   import Axes, Order
from robot.spatial         import Matrix4, Mesh, Transform, Quaternion
from robot.traj.linear_js  import LinearJS
from robot.traj.linear_os  import LinearOS
from robot.visual.opengl.shader_program import ShaderProgram

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

  # with Timer('Initialize Shaders') as t:
  program      = renderer.shaders.get('serial') # ShaderProgram(vertex='serial_v', fragment='serial_f')
  flat_program = renderer.shaders.get('flat') # ShaderProgram('flat')
  grid_program = renderer.shaders.get('grid') # ShaderProgram('grid')
  bill_program = renderer.shaders.get('billboard') # ShaderProgram('billboard')
  com_program  = renderer.shaders.get('com') # ShaderProgram('com')

  program.bind_ubo("Matrices", 1)
  flat_program.bind_ubo("Matrices", 1)
  grid_program.bind_ubo("Matrices", 1)
  bill_program.bind_ubo("Matrices", 1)
  com_program.bind_ubo("Matrices", 1)

  program.bind_ubo("Light", 2)

  ee_frame = entities.FrameEntity(Transform(), flat_program)
  grid = entities.GridEntity(grid_program)
  welder = tool_entity.load('./robot/mech/tools/welder.json')
  welder.shader_program = program

  with Timer('Load Robot and Construct Mesh') as t:
    with open('./robot/mech/robots/abb_irb_120.json') as json_file:
      serial_dictionary = json.load(json_file)

      if 'mesh_file' in serial_dictionary.keys():
        meshes = Mesh.from_file(vis.STLParser(), f'./robot/mech/robots/meshes/{serial_dictionary["mesh_file"]}')

      serials = [Serial.from_dict_meshes(serial_dictionary, meshes or []) for _ in range(2)]

  robot, robot2 = [entities.RobotEntity(serial, program) for serial in serials]
  robot.frame_entity  = ee_frame
  robot2.frame_entity = ee_frame

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
  robot2.color = (0.5, 1, 0)
  robot2.attach(welder)

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


  camera = vis.Camera(Vector3(0, -1250, 375), Vector3(0, 0, 350), Vector3(0, 0, 1))

  world_frame = entities.FrameEntity(Transform(), flat_program)
  light = vis.AmbientLight(Vector3(0, -750, 350), Vector3(1, 1, 1), 0.3)

  scene = vis.Scene(camera, light)

  bindings = Bindings()
  settings = vis.CameraSettings()
  camera_controller = vis.CameraController(camera, settings, bindings, scene, window)
  triangle = entities.TriangleEntity(camera_controller, bill_program)

  scene.entities.append(world_frame)
  scene.entities.append(grid)
  scene.entities.append(robot2)
  scene.entities.append(robot)
  scene.entities.append(triangle)

  for link in robot.serial.links:
    com = entities.COMEntity(link, camera, com_program)
    scene.entities.append(com)

  window.run()