from typing import Iterable

from .widget import Widget

class Interface():
  def __init__(self) -> None:
    self.joint_controllers = {}

  def add_joint_controller(self, joint_index: int, controller: Widget) -> None:
    self.joint_controllers[joint_index] = controller