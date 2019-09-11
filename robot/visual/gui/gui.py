import glfw

from robot.visual.messaging.listener import listen, listener
from robot.visual.messaging.event    import Event
from .widget import Widget

@listener
class GUI(Widget):
  def __init__(self):
    super().__init__()

  @listen(Event.CLICK)
  def click(self, button, action, cursor, mods):
    self.propagate('click', cursor, button, action, cursor, mods)

    if button == glfw.MOUSE_BUTTON_LEFT and action == glfw.PRESS:
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
    self.children['Viewport']._width = 1 - self.children['Interface']._width
    self.children['Viewport']._position.x = self.children['Interface']._width

  def hide_panel(self):
    self.children['Interface'].visible = False
    self.children['Viewport']._width = 1
    self.children['Viewport']._position.x = 0

  @listen(Event.DRAG)
  def drag(self, button, cursor, cursor_delta, modifiers):
    self.propagate('drag', cursor, button, cursor, cursor_delta, modifiers)

  @listen(Event.CURSOR)
  def cursor(self, button, cursor, cursor_delta, modifiers):
    self.propagate('cursor', cursor, button, cursor, cursor_delta, modifiers)

  @listen(Event.UPDATE)
  def update(self, delta: float = 0) -> None:
    update_fn = getattr(self.children['Interface'], 'update', None)
    if update_fn is not None:
      update_fn(delta)