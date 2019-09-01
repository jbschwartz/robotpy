import glfw

from typing import Iterable

from robot.spatial import Vector3
from robot.visual.messaging.event import Event
from robot.visual.messaging.listener import listener, listen

@listener
class Rectangle():
  def __init__(self, name: str, position: Vector3, width: float, height: float, color: Iterable[float]) -> None:
    self.name     = name
    self.position = position # Top left corner of the rectangle
    self.width    = width
    self.height   = height
    self.color    = color

    self.hover    = False

  def ndc(self, cursor):
    return Vector3(2 * cursor.x / self.window_width - 1, 1 - 2 * cursor.y / self.window_height)

  @listen(Event.WINDOW_RESIZE)
  def window_size(self, width, height):
    self.window_width  = width
    self.window_height = height

  @listen(Event.CURSOR)
  def on_mouse(self, button, cursor, cursor_delta, modifiers):
    self.hover = self.contains(self.ndc(cursor))

  @listen(Event.DRAG)
  def on_drag(self, button, cursor, cursor_delta, modifiers):
    if button == glfw.MOUSE_BUTTON_LEFT and self.hover:
      delta = self.ndc(cursor_delta) - Vector3(-1, 1)
      self.position -= delta

  def contains(self, point_ndc: Vector3) -> bool:
    inside_x = self.position.x <= point_ndc.x <= (self.position.x + self.width)
    inside_y =  (self.position.y - self.height) <= point_ndc.y <= self.position.y

    return inside_x and inside_y