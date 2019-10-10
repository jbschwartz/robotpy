import glfw, math

from robot.visual.messaging.listener import listen, listener
from robot.visual.messaging.event    import Event
from .widget    import Widget

@listener
class GUI(Widget):
  def __init__(self):
    super().__init__()

  @listen(Event.CLICK)
  def click(self, button, action, cursor, mods):
    if button == glfw.MOUSE_BUTTON_LEFT and action == glfw.PRESS and self.children['Viewport'].contains(cursor):
      if self.children['Interface'].contains(cursor):
        self.children['Interface'].click(button, action, cursor, mods)
        return

      self.propagate(Event.CLICK, button, action, cursor, mods)

      interface = self.children['Interface']
      x = self.children['Viewport'].selected
      if x is not None:
        serial_controller = x.obj
        if serial_controller is not None:
          self.show_panel()
          serial_controller.register_callbacks(interface)
          serial_controller.update_controllers(interface)
        else:
          interface.clear_callbacks()
      else:
        self.hide_panel()
        interface.clear_callbacks()

  def show_panel(self):
    self.children['Interface'].visible = True

  def hide_panel(self):
    self.children['Interface'].visible = False

  @listen(Event.WINDOW_RESIZE)
  def resize_window(self, width, height) -> None:
    self.propagate(Event.WINDOW_RESIZE, width, height)

  @listen(Event.DRAG, Event.CURSOR)
  def pass_through(self, event, *args, **kwargs):
    self.propagate(event, *args, **kwargs)

  @listen(Event.UPDATE)
  def update(self, delta: float = 0) -> None:
    update_fn = getattr(self.children['Interface'], 'update', None)
    if update_fn is not None:
      update_fn(delta)