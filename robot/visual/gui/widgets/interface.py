from typing import Iterable

from robot.visual.gui.widget import Widget
from .rectangle import Rectangle
from robot.visual.messaging.listener import listen, listener
from robot.visual.messaging.event    import Event

@listener
class Interface(Widget):
  def __init__(self) -> None:
    super().__init__(name="Interface")
    self.add(Rectangle(name='bg', color=[0.85]*3))
    self.joint_controllers = {}

  def add_joint_controller(self, joint_index: int, controller: Widget) -> None:
    self.add(controller)
    self.joint_controllers[joint_index] = controller

  def clear_callbacks(self) -> None:
    controllers = self.joint_controllers
    if len(controllers.keys()) > 0:
      for controller in controllers.values():
        controller.callback = None