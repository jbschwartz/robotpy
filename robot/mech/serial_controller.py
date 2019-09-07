import glfw, math

from typing import Callable, Iterable

from robot.mech                      import Serial
from robot.spatial                   import Intersection, Ray
from robot.visual.gui                import Widget, Interface
from robot.visual.messaging.listener import listen, listener
from robot.visual.messaging.event    import Event

@listener
class SerialController():
  def __init__(self, serial: Serial, interface: Interface) -> None:
    self.serial = serial
    self.interface = interface

    self.register_callbacks()
    self.update_controllers()

  @property
  def entity(self) -> Serial:
    return self.serial

  def intersect(self, ray: Ray) -> Intersection:
    return self.serial.intersect(ray)

  def update_controllers(self):
    for joint, controller in zip(self.serial.joints, self.interface.joint_controllers.values()):
      controller.value = joint.normalized_angle

  def register_callbacks(self) -> None:
    controllers = self.interface.joint_controllers
    if len(controllers.keys()) > 0:
      for joint_index, controller in controllers.items():
        def callback(name: str, value: float, joint_index: int = joint_index) -> None:
          self.serial.set_joint_angle(joint_index, value, normalized=True)
        controller.callback = callback

  @listen(Event.KEY)
  def key(self, key, action, modifiers) -> None:
    if glfw.KEY_H == key:
      self.serial.home()
      self.update_controllers()