import math

from robot.spatial import vector3
Vector3 = vector3.Vector3

from robot.common.timer                      import Timer
from robot.traj.linear_js                    import LinearJS
from robot.visual.ambient_light              import AmbientLight
from robot.visual.camera                     import Camera
from robot.visual.entities                   import robot_entity
from robot.visual.entities.triangle_entity   import TriangleEntity
from robot.visual.entities.frame_entity      import FrameEntity
from robot.visual.scene                      import Scene
from robot.visual.shader_program             import ShaderProgram
from robot.visual.window                     import Window
from robot.visual.window_events              import WindowEvents

RobotEntity = robot_entity.RobotEntity

if __name__ == "__main__":
  with Timer('Initialize Window') as t:
    window = Window(900, 900, "robotpy")

  with Timer('Initialize Shaders') as t:
    program = ShaderProgram('./robot/visual/glsl/vertex.glsl', './robot/visual/glsl/fragment.glsl')
    flat_program = ShaderProgram('./robot/visual/glsl/vertex-flat.glsl', './robot/visual/glsl/fragment-flat.glsl')
    
  ee_frame = FrameEntity(Frame(), flat_program)

  with Timer('Initialize Robot') as t:
    robot = robot_entity.load('./robot/mech/robots/abb_irb_120.json')
    robot.shader_program = program
    robot.frame_entity = ee_frame
    robot.serial.position(Vector3(-500, 0, 0))
    robot.serial.traj = LinearJS([0] * 6, [math.radians(45)] * 6, 6)

  robot2 = robot_entity.load('./robot/mech/robots/abb_irb_120.json')
  robot2.shader_program = program
  robot2.serial.position(Vector3(500, 0, 0))
  robot2.color = (0.5, 1, 0)
  robot2.serial.traj = LinearJS([0] * 6, [math.radians(-45)] * 6, 4)

  triangle = TriangleEntity(flat_program)

  camera = Camera(Vector3(0, -1250, 375), Vector3(0, 0, 350), Vector3(0, 0, 1), 1)
  window.register_observer(camera, [ WindowEvents.ORBIT, WindowEvents.ZOOM, WindowEvents.CLICK, WindowEvents.RESET ])
  light = AmbientLight(Vector3(0, -750, 350), Vector3(1, 1, 1), 0.3)

  scene = Scene(camera, light)
  scene.entities.append(robot)
  scene.entities.append(robot2)
  scene.entities.append(triangle)
  window.register_observer(scene)

  window.run()