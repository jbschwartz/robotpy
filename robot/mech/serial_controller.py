import glfw, math

from typing import Callable, Iterable

from robot.mech                      import Serial
from robot.mech.views                import SerialView
from robot.spatial                   import Intersection, Ray
from robot.visual.gui                import Widget
from robot.visual.gui.widgets.interface  import Interface
from robot.visual.messaging.listener import listen, listener
from robot.visual.messaging.event    import Event

@listener
class SerialController():
  def __init__(self, serial: Serial) -> None:
    self.serial = serial
    self.view = SerialView(serial)

  @property
  def entity(self) -> Serial:
    return self.serial

  def intersect(self, ray: Ray) -> Intersection:
    return Intersection.from_previous(self, self.serial.intersect(ray))

  def update_controllers(self, interface):
    for joint, controller in zip(self.serial.joints, interface.joint_controllers.values()):
      controller.value = joint.normalized_angle

  def register_callbacks(self, interface) -> None:
    controllers = interface.joint_controllers
    if len(controllers.keys()) > 0:
      for joint_index, controller in controllers.items():
        def callback(name: str, value: float, joint_index: int = joint_index) -> None:
          self.serial.set_joint_angle(joint_index, value, normalized=True)
        controller.callback = callback

  def select(self) -> None:
    self.view.select()

  def deselect(self) -> None:
    self.view.deselect()

  @listen(Event.KEY)
  def key(self, key, action, modifiers) -> None:
    if glfw.KEY_H == key:
      self.serial.home()