from collections import namedtuple
from typing      import Callable

import enum, glfw

from robot.common                    import logger
from robot.spatial                   import Vector3
from robot.visual.gui.widget         import Widget
from robot.visual.messaging.event    import Event
from robot.visual.messaging.listener import listener, listen

from .rectangle import Rectangle

SliderInterval = namedtuple('SliderInterval', 'min max')

class SliderType(enum.Enum):
  VERTICAL   = 0
  HORIZONTAL = 1

@listener
class Slider(Widget):
  def __init__(
    self,
    callback: Callable = None,
    value: float = None,
    slider_type: SliderType = None,
    **options: dict
  ) -> None:
    super().__init__(**options)

    self._value      = value       or 0.5
    self.slider_type = slider_type or SliderType.HORIZONTAL
    self.callback    = callback    or None

    self.add(Rectangle('Range', position=Vector3(0, 0.45), width=1, height=0.1, color=[0.65] * 3))
    self.add(Rectangle('Button', position=Vector3(0.5-0.125, 0.5-0.125), width=0.25, height=0.25, color=[0.25] * 3))

  @property
  def value(self) -> float:
    return self.children['Button']._position.x / (1 - self.children['Button']._width)

  @value.setter
  def value(self, new_value: float) -> None:
    self._value = new_value

    assert 0 <= self._value <= 1

    self.children['Button']._position.x = self._value * (1 - self.children['Button']._width)

  def screen_cursor(self, cursor: Vector3) -> Vector3:
    return Vector3(cursor.x / self.window_width, cursor.y / self.window_height)

  @listen(Event.WINDOW_RESIZE)
  def window_size(self, width, height):
    self.window_width  = width
    self.window_height = height

  @listen(Event.CURSOR)
  def on_mouse(self, button, cursor, cursor_delta, modifiers):
    self.children['Button'].hover = self.children['Button'].contains(self.screen_cursor(cursor))

  @listen(Event.DRAG)
  def on_drag(self, button, cursor, cursor_delta, modifiers):
    if button == glfw.MOUSE_BUTTON_LEFT and self.children['Button'].hover:
      cursor_delta[self.slider_type.value] = 0

      delta = self.screen_cursor(cursor_delta)
      self.children['Button']._position.x -= delta.x / self.width
      if self.children['Button']._position.x < 0:
        self.children['Button']._position.x = 0
      elif self.children['Button']._position.x > 1 - self.children['Button']._width:
        self.children['Button']._position.x = 1 - self.children['Button']._width

      self.callback(self.name, self.value)