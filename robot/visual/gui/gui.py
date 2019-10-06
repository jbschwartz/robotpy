import glfw, math

from robot.visual.messaging.listener import listen, listener
from robot.visual.messaging.event    import Event
from .animation import Animation
from .widget    import Widget

@listener
class GUI(Widget):
  def __init__(self):
    super().__init__()

    self.animations = {
      'panel': Animation(0.25)
    }

  @listen(Event.CLICK)
  def click(self, button, action, cursor, mods):
    self.propagate(Event.CLICK, button, action, cursor, mods)

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
    if (not math.isclose(self.children['Interface']._position.x, 0, abs_tol=0.001)) or (not self.children['Interface'].visible):
      self.children['Interface'].visible = True
      self.animations['panel'].set_end_points(0, self.children['Interface']._width)
      self.animations['panel'].reset()

  def hide_panel(self):
    if math.isclose(self.children['Interface']._position.x, 0, abs_tol=0.001):
      self.animations['panel'].reverse()
      self.animations['panel'].reset()

  def animate_panel(self):
    if self.animations['panel'].is_done:
      return

    value = self.animations['panel'].value
    self.children['Interface']._position.x = -self.children['Interface']._width + value

    self.children['Viewport']._width = 1 - value
    self.children['Viewport']._position.x = value

  @listen(Event.DRAG, Event.CURSOR)
  def pass_through(self, event, *args, **kwargs):
    self.propagate(event, *args, **kwargs)

  @listen(Event.UPDATE)
  def update(self, delta: float = 0) -> None:
    for animation in self.animations.values():
      if not animation.is_done:
        animation.update(delta)

    self.animate_panel()

    update_fn = getattr(self.children['Interface'], 'update', None)
    if update_fn is not None:
      update_fn(delta)