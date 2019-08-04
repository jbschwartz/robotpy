import glfw, math

from robot.ik.angles import solve_angles
from robot.visual    import Observer
from robot.spatial   import Dual, Quaternion, Transform, Vector3

class SerialController(Observer):
  def __init__(self, serial, frame_entity):
    self.serial = serial
    self._t = 0
    self.frame_entity = frame_entity
    self.is_reversing = False

  @property
  def t(self):
    return self._t

  @t.setter
  def t(self, value):
    old_value = self._t
    self._t = max(min(1, value), 0)

    step = self._t - old_value
    self.advance(step)

  def advance(self, step):
    self.serial.angles = self.serial.traj.advance(step)
    self.frame_entity.frame = self.serial.tool.tip

  def print_results(self):
    print(self.serial.angles)

  def key(self, key, action, modifiers):
    STEP = 0.1
    if action == glfw.RELEASE or glfw.REPEAT:
      if key == glfw.KEY_KP_ADD:
        self.advance(STEP)
        self.print_results()
        if self.is_reversing:
          self.serial.traj.reverse()
          self.is_reversing = False
      elif key == glfw.KEY_KP_SUBTRACT:
        self.advance(STEP)
        self.print_results()
        if not self.is_reversing:
          self.serial.traj.reverse()
          self.is_reversing = True
      elif key == glfw.KEY_R:
        self.serial.traj.restart()