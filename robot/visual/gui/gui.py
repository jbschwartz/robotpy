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

    x = self.children['Viewport'].selected

    if x is not None:
      serial_controller = x.obj
      interface = self.children['Interface']
      if serial_controller is not None:
        serial_controller.register_callbacks(interface)
        serial_controller.update_controllers(interface)
      else:
        interface.clear_callbacks()

  @listen(Event.DRAG)
  def drag(self, button, cursor, cursor_delta, modifiers):
    self.propagate('drag', cursor, button, cursor, cursor_delta, modifiers)

  @listen(Event.CURSOR)
  def cursor(self, button, cursor, cursor_delta, modifiers):
    self.propagate('cursor', cursor, button, cursor, cursor_delta, modifiers)