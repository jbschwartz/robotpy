import glfw, math

from robot.ik.angles          import solve_angles
from robot.visual.observer    import Observer
from robot.spatial.dual       import Dual
from robot.spatial.frame      import Frame
from robot.spatial.quaternion import Quaternion
from robot.spatial.transform  import Transform
from robot.spatial.vector3    import Vector3

class SerialController(Observer):
  def __init__(self, serial, traj):
    self.serial = serial
    self.target = None
    self._t = 0

    self.traj = traj

    self.frame_orientation = Frame(Transform(dual = Dual(Quaternion(0.7071067811865477, -4.3297802811774677e-17, 0.7071067811865477, -4.3297802811774677e-17), 0)))

    self.start = Vector3(374, 320, 630)
    self.end   = Vector3(374, -320, 330)

    # Call all the functions that need to be called
    self.t = 0

  @property
  def t(self):
    return self._t

  @t.setter
  def t(self, value):
    self._t = max(min(1, value), 0)

    self.update_target()
    self.solve()
    self.set_pose()

  def solve(self):
    print(self.target.position())
    self.results = solve_angles(self.target, self.serial)
    print(self.results)
    self.print_results()

  def interpolate(self):
    print(self.t)
    return (self.end - self.start) * self.t + self.start

  def update_target(self):
    ee_position = self.interpolate()
    print(ee_position)

    translation = Quaternion(0, *ee_position)
    rotation = self.frame_orientation.transform.rotation()

    dual = Dual(rotation, 0.5 * translation * rotation)

    self.target = Frame(Transform(dual = dual))

  def print_results(self):
    for result in self.results:
      print([math.degrees(angle) for angle in result])
      print('')

  def key(self, key, action, modifiers):
    if action == glfw.RELEASE or glfw.REPEAT:
      if key == glfw.KEY_KP_ADD:
        self.t += 0.015
      elif key == glfw.KEY_KP_SUBTRACT:
        self.t -= 0.015
      elif key == glfw.KEY_R:
        self.traj.restart()

  def set_pose(self):
    if self.results:
      self.serial.angles = self.results[0]