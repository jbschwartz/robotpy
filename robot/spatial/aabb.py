import math

from robot.spatial.vector3 import Vector3

class AABB:
  def __init__(self):
    self.min = Vector3(math.inf, math.inf, math.inf)
    self.max = Vector3(-math.inf, -math.inf, -math.inf)

  def extend(self, *args):
    for other in args:
      if isinstance(other, Vector3):
        self._extend_vector(other)
      elif isinstance(other, AABB):
        self._extend_vector(other.min)
        self._extend_vector(other.max)

  def _extend_vector(self, v : Vector3):
    for index, value in enumerate(v):
      if value < self.min[index]:
        self.min[index] = value
      if value > self.max[index]:
        self.max[index] = value

  @property
  def center(self):
    return self.min + (self.size / 2)

  @property
  def size(self):
    return self.max - self.min

  @property
  def corners(self):
    size = self.size
    x = Vector3(x = size.x)
    y = Vector3(y = size.y)
    
    return [
      self.max,
      self.max - x,
      self.max - y,
      self.max - x - y,
      self.min,
      self.min + x,
      self.min + y,
      self.min + x + y,
    ]