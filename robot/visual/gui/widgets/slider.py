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

@listener
class Slider(Widget):
  def __init__( self, callback: Callable = None, value: float = None, **options: dict) -> None:
    super().__init__(**options)

    self._value      = value    or 0.5
    self.callback    = callback or None

    self.add(Rectangle(name='Range', position=Vector3(0, 0.45), width=1, height=0.1, color=[0.65] * 3))
    self.add(Rectangle(name='Button', position=Vector3(0.5-0.125, 0.5-0.125), width=0.25, height=0.25, color=[0.25] * 3))

  @property
  def value(self) -> float:
    return self.children['Button']._position.x / (1 - self.children['Button']._width)

  @value.setter
  def value(self, new_value: float) -> None:
    self._value = new_value

    assert 0 <= self._value <= 1

    self.children['Button']._position.x = self._value * (1 - self.children['Button']._width)

  @listen(Event.CURSOR)
  def cursor(self, button, cursor, cursor_delta, modifiers):
    self.children['Button'].hover = self.children['Button'].contains(cursor)

  @listen(Event.DRAG)
  def drag(self, button, cursor, cursor_delta, modifiers):
    if button == glfw.MOUSE_BUTTON_LEFT and self.children['Button'].hover:
      self.children['Button']._position.x -= cursor_delta.x / self.width
      if self.children['Button']._position.x < 0:
        self.children['Button']._position.x = 0
      elif self.children['Button']._position.x > 1 - self.children['Button']._width:
        self.children['Button']._position.x = 1 - self.children['Button']._width

      if self.callback is not None:
        self.callback(self.name, self.value)