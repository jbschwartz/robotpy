import math

from robot.spatial.vector3 import Vector3

class AABB:
  def __init__(self):
    self.min = Vector3(math.inf, math.inf, math.inf)
    self.max = Vector3(-math.inf, -math.inf, -math.inf)

  def extend(self, v : Vector3):
    for index, value in enumerate(v):
      if value < self.min[index]:
        self.min[index] = value
      if value > self.max[index]:
        self.max[index] = value

  @property
  def center(self):
    return self.size / 2

  @property
  def size(self):
    return self.max - self.min