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

  def contains(self, v : Vector3):
    for low, value, high in zip(self.min, v, self.max):
      if not low <= value <= high:
        return False
    return True 

  def sphere_radius(self):
    largest = 0
    for corner in self.corners:
      radius = self.center - corner
      largest = max(radius.length(), largest)
    
    return largest

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
      self.max - x - y,
      self.max - y,
      self.min,
      self.min + x,
      self.min + x + y,
      self.min + y,
    ]