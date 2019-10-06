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
    self.delta = 0
    self._cursor = None
    self.wait_time = 0.5

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

  def move_button(self, amount) -> None:
    self.children['Button']._position.x += amount

    if self.children['Button']._position.x < 0:
      self.children['Button']._position.x = 0
    elif self.children['Button']._position.x > 1 - self.children['Button']._width:
      self.children['Button']._position.x = 1 - self.children['Button']._width

  def seek(self) -> None:
    """Adjust the value of the slider toward the cursor."""
    normalized = (self._cursor.x - self.position.x) / (self.width)
    if normalized > (self.children['Button']._position.x + self.children['Button']._width):
      self.move_button(0.05)
    elif normalized < self.children['Button']._position.x:
      self.move_button(-0.05)

    if self.callback is not None:
      self.callback(self.name, self.value)

    self.delta = 0

  def left_click_down(self, cursor, mods) -> None:
    if self.children['Button'].hover:
      self.is_clicked = True
    else:
      if self.children['Range'].contains(cursor):
        self.is_clicked = True
        self._cursor = cursor
        self.seek()

  def cursor(self, button, cursor, cursor_delta, modifiers):
    self.children['Button'].hover = self.children['Button'].contains(cursor)

  def click(self, button, action, cursor, mods):
    if action == glfw.RELEASE:
      self.delta = 0
      self._cursor = None

    if button == glfw.MOUSE_BUTTON_LEFT and action in [glfw.PRESS, glfw.REPEAT]:
      self.left_click_down(cursor, mods)

    elif button == glfw.MOUSE_BUTTON_LEFT and action == glfw.RELEASE:
      self.is_clicked = False
      if not self.children['Button'].contains(cursor):
        self.children['Button'].hover = False

  def drag(self, button, cursor, cursor_delta, modifiers):
    if button == glfw.MOUSE_BUTTON_LEFT and self.children['Button'].hover:
      self.move_button(-cursor_delta.x / self.width)

      if self.callback is not None:
        self.callback(self.name, self.value)

  def update(self, delta: float) -> None:
    if self._cursor is not None:
      self.delta += delta
      if self.delta > self.wait_time:
        if self.wait_time > 0.0625:
          self.wait_time /= 2
        self.seek()
    else:
      self.wait_time = 0.5
