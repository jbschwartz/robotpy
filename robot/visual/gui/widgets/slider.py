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
  # Material design proportions
  RANGE_WIDTH  = 160
  BUTTON_SIZE  = 12
  RANGE_HEIGHT = 2

  def __init__( self, callback: Callable = None, value: float = None, **options: dict) -> None:
    super().__init__(**options)

    self.delta = 0
    self._cursor = None
    self.wait_time = 0.5

    self.callback    = callback or None

    scale = options.get('scale', 1)

    self.fixed_width = scale * Slider.RANGE_WIDTH
    self.fixed_height = scale * Slider.BUTTON_SIZE

    self.home  = Rectangle(
      name='Home',
      fixed_size=True,
      position=Vector3(scale / 2 * (Slider.RANGE_WIDTH - (Slider.BUTTON_SIZE / 2)),  scale * (Slider.BUTTON_SIZE / 2 - Slider.RANGE_HEIGHT)),
      width=scale * Slider.RANGE_HEIGHT / 2,
      height=scale * Slider.RANGE_HEIGHT * 2,
      color=[0.45] * 3
    )
    self.range  = Rectangle(
      name='Range',
      fixed_size=True,
      position=Vector3(0, scale / 2 * (Slider.BUTTON_SIZE - Slider.RANGE_HEIGHT)),
      width=scale * Slider.RANGE_WIDTH,
      height=scale * Slider.RANGE_HEIGHT,
      color=[0.65] * 3
    )
    self.button = Rectangle(
      name='Button',
      fixed_size=True,
      position=Vector3(scale / 2 * (Slider.RANGE_WIDTH - Slider.BUTTON_SIZE), 0),
      width=scale * Slider.BUTTON_SIZE,
      height=scale * Slider.BUTTON_SIZE,
      color=[0.25] * 3
    )

    self.add(self.range, self.home, self.button)

  @property
  def value(self) -> float:
    return self.button._position.x / (1 - self.button._width)

  @value.setter
  def value(self, value: float) -> None:
    assert 0 <= value <= 1

    self.button._position.x = value * (1 - self.button._width)

  def set_home(self, value) -> None:
    self.home._position.x = value - (self.home._width / 2)

  def move_button(self, amount) -> None:
    self.button._position.x += amount

    if self.button._position.x < 0:
      self.button._position.x = 0
    elif self.button._position.x > 1 - self.button._width:
      self.button._position.x = 1 - self.button._width

    if self.callback is not None:
      self.callback(self.name, self.value)

  def seek(self) -> None:
    """Adjust the value of the slider toward the cursor."""
    normalized = (self._cursor.x - self.position.x) / (self.width)
    if normalized > (self.button._position.x + self.button._width):
      self.move_button(0.05)
    elif normalized < self.button._position.x:
      self.move_button(-0.05)

    self.delta = 0

  def left_click_down(self, cursor, mods) -> None:
    if self.button.hover:
      self.is_clicked = True
    else:
      if self.range.contains(cursor):
        self.is_clicked = True
        self._cursor = cursor
        self.seek()

  def cursor(self, button, cursor, cursor_delta, modifiers):
    self.button.hover = self.button.contains(cursor)

  def click(self, button, action, cursor, mods):
    if action == glfw.RELEASE:
      self.delta = 0
      self._cursor = None

    if button == glfw.MOUSE_BUTTON_LEFT and action in [glfw.PRESS, glfw.REPEAT]:
      self.left_click_down(cursor, mods)

    elif button == glfw.MOUSE_BUTTON_LEFT and action == glfw.RELEASE:
      self.is_clicked = False
      if not self.button.contains(cursor):
        self.button.hover = False

  def drag(self, button, cursor, cursor_delta, modifiers):
    if button == glfw.MOUSE_BUTTON_LEFT and self.button.hover:
      self.move_button(-cursor_delta.x / self.width)

  def update(self, delta: float) -> None:
    if self._cursor is not None:
      self.delta += delta
      if self.delta > self.wait_time:
        if self.wait_time > 0.0625:
          self.wait_time /= 2
        self.seek()
    else:
      self.wait_time = 0.5
