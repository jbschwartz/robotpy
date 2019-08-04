import json, math

from robot.spatial import vector3
Vector3 = vector3.Vector3

from robot.common.bindings                 import Bindings
from robot.common.timer                    import Timer
from robot.mech.serial                     import Serial
from robot.spatial.euler                   import Axes, Order
from robot.spatial                         import Frame, Transform, Quaternion
from robot.traj.linear_js                  import LinearJS
from robot.traj.linear_os                  import LinearOS
from robot.visual.ambient_light            import AmbientLight
from robot.visual.camera                   import Camera
from robot.visual.camera_controller        import CameraController, CameraSettings
from robot.visual.entities                 import robot_entity
from robot.visual.entities.triangle_entity import TriangleEntity
from robot.visual.entities.com_entity      import COMEntity
from robot.visual.entities.frame_entity    import FrameEntity
from robot.visual.entities.bounding_entity import BoundingEntity
from robot.visual.entities.grid_entity     import GridEntity
from robot.visual.entities                 import tool_entity
from robot.visual.scene                    import Scene
from robot.visual.shader_program           import ShaderProgram
from robot.visual.window                   import Window
from robot.visual.window_event             import WindowEvent
from robot.visual.filetypes.stl.stl_parser import STLParser
from robot.visual.mesh                     import Mesh

RobotEntity = robot_entity.RobotEntity

if __name__ == "__main__":
  with Timer('Initialize Window') as t:
    window = Window(750, 750, "robotpy")

  with Timer('Initialize Shaders') as t:
    program = ShaderProgram(vertex='serial_v', fragment='serial_f')
    flat_program = ShaderProgram('flat')
    grid_program = ShaderProgram('grid')
    bill_program = ShaderProgram('billboard')
    com_program = ShaderProgram('com')

  ee_frame = FrameEntity(Frame(), flat_program)
  bb = BoundingEntity(flat_program)
  grid = GridEntity(grid_program)
  welder = tool_entity.load('./robot/mech/tools/welder.json')
  welder.shader_program = program

  with Timer('Load Robot JSON') as t:
    with open('./robot/mech/robots/abb_irb_120.json') as json_file:
      serial_dictionary = json.load(json_file)

      if 'mesh_file' in serial_dictionary.keys():
        meshes = Mesh.from_file(STLParser(), f'./robot/mech/robots/meshes/{serial_dictionary["mesh_file"]}')

      serials = [Serial.from_dict_meshes(serial_dictionary, meshes or []) for _ in range(2)]

  robot, robot2 = [RobotEntity(serial, program) for serial in serials]
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

  triangle = TriangleEntity(bill_program)

  camera = Camera(Vector3(0, -1250, 375), Vector3(0, 0, 350), Vector3(0, 0, 1))

  world_frame = FrameEntity(Frame(), flat_program)
  light = AmbientLight(Vector3(0, -750, 350), Vector3(1, 1, 1), 0.3)

  scene = Scene(camera, light)

  bindings = Bindings()
  settings = CameraSettings()
  camera_controller = CameraController(camera, settings, bindings, scene, window)

  window.register_observer(camera_controller, [
    WindowEvent.CLICK,
    WindowEvent.DRAG,
    WindowEvent.KEY,
    WindowEvent.RESET,
    WindowEvent.SCROLL,
    WindowEvent.WINDOW_RESIZE
  ])

  window.register_observer(triangle, [
    WindowEvent.CLICK
  ])

  scene.entities.append(world_frame)
  scene.entities.append(grid)
  scene.entities.append(robot2)
  scene.entities.append(robot)
  scene.entities.append(triangle)

  for link in robot.serial.links:
    com = COMEntity(link, com_program)
    scene.entities.append(com)

  window.register_observer(scene)

  window.run()