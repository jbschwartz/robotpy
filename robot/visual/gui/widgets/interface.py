from typing import Iterable

from robot.visual.gui.widget import Widget
from .container import Container
from .rectangle import Rectangle
from robot.visual.messaging.listener import listen, listener
from robot.visual.messaging.event    import Event

@listener
class Interface(Container):
  def __init__(self, **options) -> None:
    self.joint_controllers = {}
    self.visible = False

    super().__init__(name="Interface", **options)
    self.add(Rectangle(name='bg', color=[0.85]*3))

  def add_joint_controller(self, joint_index: int, controller: Widget) -> None:
    self.add(controller)
    self.joint_controllers[joint_index] = controller

  def clear_callbacks(self) -> None:
    controllers = self.joint_controllers
    if len(controllers.keys()) > 0:
      for controller in controllers.values():
        controller.callback = None