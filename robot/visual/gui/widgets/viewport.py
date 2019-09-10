import glfw

from robot.mech import SerialController
from robot.visual.gui.widget import Widget

class Viewport(Widget):
  def __init__(self, camera_controller = None) -> None:
    self.camera_controller = camera_controller
    self.selected = None
    super().__init__(name='Viewport')

  def click(self, *args) -> None:
    x = self.camera_controller.click(*args)
    if args[1] == glfw.PRESS:
      self.is_clicked = True
      if x.hit and isinstance(x.obj, SerialController):
        self.selected = x
      else:
        self.selected = None
    else:
      self.is_clicked = False

  def drag(self, *args) -> None:
    if self.is_clicked:
      self.camera_controller.drag(*args)