import glfw, math

from typing import Callable, Iterable

from robot.ik.angles                    import solve_angles
from robot.mech                         import Serial
from robot.mech.views                   import SerialView
from robot.spatial                      import Intersection, Ray
from robot.traj                         import LinearJS
from robot.visual.gui                   import Widget
from robot.visual.gui.widgets.interface import Interface
from robot.visual.messaging.listener    import listen, listener
from robot.visual.messaging.event       import Event

@listener
class SerialController():
  def __init__(self, serial: Serial) -> None:
    self.serial = serial
    self.view = SerialView(serial)
    self.trajectory = LinearJS(None, None, 1)
    self.paused = True
    self.interface = None
    self.solve()
    self.index = 0
    self.texts = None

  def solve(self) -> None:
    target = self.serial.pose()
    self.solutions = solve_angles(target, self.serial)

  @property
  def entity(self) -> Serial:
    return self.serial

  def intersect(self, ray: Ray) -> Intersection:
    return Intersection.from_previous(self, self.serial.intersect(ray))

  def update_controllers(self, interface):
    self.interface = interface

    if len(self.texts) > 0:
      for index, text in enumerate(self.texts):
        text.string = "{:.2f}".format(math.degrees(self.serial.angles[index]))
        text.load()

    for joint, controller in zip(self.serial.joints, interface.joint_controllers.values()):
      controller.value = joint.normalized_angle

  def register_callbacks(self, interface) -> None:
    controllers = interface.joint_controllers
    if len(controllers.keys()) > 0:
      for joint_index, controller in controllers.items():
        def callback(name: str, value: float, joint_index: int = joint_index) -> None:
          angle = self.serial.set_joint_angle(joint_index, value, normalized=True)
          if len(self.texts) > 0:
            self.texts[joint_index - 1].string = "{:.2f}".format(math.degrees(angle))
            self.texts[joint_index - 1].load()

          for text in self.texts:
            text.reload_buffer = True

          target = self.serial.pose()
          self.solutions = solve_angles(target, self.serial)
          self.index = 0

        controller.callback = callback
        delta = (self.serial.joints[joint_index-1].home - self.serial.joints[joint_index-1].limits.low) / self.serial.joints[joint_index-1].travel
        controller.set_home(delta)

  def select(self) -> None:
    self.view.select()

  def deselect(self) -> None:
    self.view.deselect()

  def update(self, delta: float) -> None:
    if self.paused:
      return

    if self.trajectory.starts is not None and self.trajectory.ends is not None:
      self.serial.angles = self.trajectory.advance(delta)

      self.update_controllers(self.interface)

    if self.trajectory.is_done():
      self.paused = True

  @listen(Event.KEY)
  def key(self, key, action, modifiers) -> None:
    if action != glfw.PRESS or not self.view.highlighted:
      return

    if glfw.KEY_H == key:
      self.serial.home()
    if glfw.KEY_K == key:
      if self.trajectory.starts is None:
        self.trajectory.starts = self.serial.angles
      elif self.trajectory.ends is None:
        self.trajectory.ends = self.serial.angles
    if glfw.KEY_J == key:
      if (modifiers & glfw.MOD_SHIFT) or self.view.highlighted:
        self.trajectory.restart()
        self.paused = False
    if glfw.KEY_G == key:
      self.trajectory.starts = None
      self.trajectory.ends = None

    if glfw.KEY_M == key:
      self.trajectory.duration += 0.25
    if glfw.KEY_N == key:
      self.trajectory.duration -= 0.25

    if glfw.KEY_C == key:
      self.index += 1
      if self.index == len(self.solutions):
        self.index = 0

      self.serial.angles = self.solutions[self.index]
      self.update_controllers(self.interface)

