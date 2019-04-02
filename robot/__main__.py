import math

from robot.spatial import vector3
Vector3 = vector3.Vector3

from robot.common.timer          import Timer
from robot.traj.linear_js        import LinearJS
from robot.visual.ambient_light  import AmbientLight
from robot.visual.camera         import Camera
from robot.visual.entities       import robot_entity
from robot.visual.scene          import Scene
from robot.visual.shader_program import ShaderProgram
from robot.visual.window         import Window
from robot.visual.window_events  import WindowEvents

RobotEntity = robot_entity.RobotEntity

if __name__ == "__main__":
  window = Window(900, 900, "robotpy")

  program = ShaderProgram('./robot/visual/glsl/vertex.glsl', './robot/visual/glsl/fragment.glsl')

  robot = robot_entity.load('./robot/mech/robots/abb_irb_120.json')
  robot.use_shader(program)
  robot.load()

  robot.serial.traj = LinearJS([0] * 6, [math.radians(45)] * 6, 2)

  camera = Camera(Vector3(0, -750, 350), Vector3(0, 0, 350), Vector3(0, 0, 1), 1)
  window.register_observer(camera, [ WindowEvents.ORBIT, WindowEvents.ZOOM ])
  light = AmbientLight(Vector3(400, -400, 1200), Vector3(1, 1, 1), 0.3)

  scene = Scene(camera, light)
  scene.entities.append(robot)
  window.register_observer(scene)

  window.run()