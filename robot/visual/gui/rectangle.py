from robot.spatial import Vector3

class Rectangle():
  def __init__(self, position: Vector3, width: float, height: float) -> None:
    self.position = position
    self.width  = width
    self.height = height
