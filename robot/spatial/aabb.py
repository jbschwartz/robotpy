import math

from robot.spatial.vector3 import Vector3

class AABB:
  def __init__(self, corner_min = None, corner_max = None):
    # TODO: Handle the case where passsed parameters are out of order
    self.min = corner_min if corner_min else Vector3(math.inf, math.inf, math.inf)
    self.max = corner_max if corner_max else Vector3(-math.inf, -math.inf, -math.inf)

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

  def contains(self, element):
    if isinstance(element, Vector3):
      return self.contains_point(element)

  def contains_point(self, point):
    for low, value, high in zip(self.min, point, self.max):
      if not low <= value <= high:
        return False
    return True 

  def sphere_radius(self):
    largest = 0
    for corner in self.corners:
      radius = self.center - corner
      largest = max(radius.length(), largest)
    
    return largest

  def intersect(self, ray, min_t = 0, max_t = math.inf):
    t = [min_t, max_t]

    # Check bounding slab intersections per component (x, y, z)
    for minimum, maximum, origin, direction in zip(self.min, self.max, ray.origin, ray.direction):
      try:
        inv_direction = 1 / direction
      except ZeroDivisionError:
        inv_direction = math.inf

      t_min = (minimum - origin) * inv_direction
      t_max = (maximum - origin) * inv_direction

      # Swap if reording is necessary
      if t_min > t_max:
        t_min, t_max = t_max, t_min

      if t_min > t[0]:
        t[0] = t_min
      if t_max < t[1]:
        t[1] = t_max

      if t[0] > t[1]:
        return False

    return True

  def __str__(self):
    return f"Min: {self.min}, Max: {self.max}"

  def split(self, axis, value):
    # TODO: Instead of passing an integer into axis, consider an Enum maybe.

    # TODO: Handle the case where value is outside the bounding box
    #   Maybe an exception?

    left_max = Vector3(*self.max)
    left_max[axis] = value

    left  = AABB(self.min, left_max)

    right_min = Vector3(*self.min)
    right_min[axis] = value

    right = AABB(right_min, self.max)

    return left, right

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