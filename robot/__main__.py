import math

from robot.spatial import vector3
Vector3 = vector3.Vector3

from robot.common.bindings                 import Bindings
from robot.common.timer                    import Timer
from robot.mech.serial_controller          import SerialController
from robot.spatial.frame                   import Frame
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
from robot.visual.scene                    import Scene
from robot.visual.shader_program           import ShaderProgram
from robot.visual.window                   import Window
from robot.visual.window_event             import WindowEvent

RobotEntity = robot_entity.RobotEntity

if __name__ == "__main__":
  with Timer('Initialize Window') as t:
    window = Window(1550, 900, "robotpy")

  with Timer('Initialize Shaders') as t:
    program = ShaderProgram(vertex='serial_v', fragment='serial_f')
    flat_program = ShaderProgram('flat')
    grid_program = ShaderProgram('grid')
    bill_program = ShaderProgram('billboard')
    com_program = ShaderProgram('com')

  ee_frame = FrameEntity(Frame(), flat_program)
  bb = BoundingEntity(flat_program)
  grid = GridEntity(grid_program)

  with Timer('Initialize Robot') as t:
    robot = robot_entity.load('./robot/mech/robots/abb_irb_120.json')
    robot.shader_program = program
    # robot.frame_entity = ee_frame
    # robot.bounding_entity = bb
    robot.serial.position(Vector3(-800, 0, 0))
    robot.serial.traj = LinearJS([0] * 6, [math.radians(45)] * 6, 6)

  robot2 = robot_entity.load('./robot/mech/robots/abb_irb_120.json')
  robot2.shader_program = program
  robot2.frame_entity = ee_frame

  robot2.color = (0.5, 1, 0)

  robot2.serial.traj = LinearOS(
    robot2.serial,
    [Vector3(374, 320, 630), Vector3(374, -320, 330), Vector3(374, 320, 330), Vector3(374, 320, 630)],
    5)
  sc = SerialController(robot2.serial, robot2.serial.traj)

  target_frame_entity = FrameEntity(sc.target, flat_program)

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

  window.register_observer(sc, [
    WindowEvent.KEY,
  ])

  window.register_observer(triangle, [
    WindowEvent.CLICK
  ])

  scene.entities.append(world_frame)
  # scene.entities.append(target_frame_entity)
  scene.entities.append(grid)
  scene.entities.append(robot2)
  # scene.entities.append(robot)
  scene.entities.append(triangle)

  # for link in robot.serial.links:
  #   com = COMEntity(link, com_program)
  #   scene.entities.append(com)

  window.register_observer(scene)

  window.run()