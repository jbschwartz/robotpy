import math

from robot.spatial         import Vector3
from robot.traj            import LinearJS
from robot.visual          import AmbientLight, Camera, Scene, ShaderProgram, Window, WindowEvents
from robot.visual.entities import robot_entity, RobotEntity

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