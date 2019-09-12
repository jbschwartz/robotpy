import glfw

from robot.mech import SerialController
from robot.visual.gui.widget import Widget

class Viewport(Widget):
  def __init__(self, camera_controller = None) -> None:
    self.camera_controller = camera_controller
    self.selected = None
    super().__init__(name='Viewport')

  def click(self, button, action, cursor, mods) -> None:
    x = self.camera_controller.click(button, action, cursor, mods)

    self.is_clicked = action == glfw.PRESS
    if self.is_clicked and button == glfw.MOUSE_BUTTON_LEFT:
      if self.selected is not None:
        self.selected.obj.deselect()

      if x.hit and isinstance(x.obj, SerialController):
        self.selected = x
        x.obj.select()
      else:
        self.selected = None

  def drag(self, *args) -> None:
    if self.is_clicked:
      self.camera_controller.drag(*args)