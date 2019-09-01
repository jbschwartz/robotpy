from typing import Iterable

from robot.spatial import Vector3

class Rectangle():
  def __init__(self, name: str, position: Vector3, width: float, height: float, color: Iterable[float]) -> None:
    self.name     = name
    self.position = position # Top left corner of the rectangle
    self.width    = width
    self.height   = height
    self.color    = color
