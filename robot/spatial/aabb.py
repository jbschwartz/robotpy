import math

from typing import Iterable, Union

from .vector3   import Vector3

class AABB:
  """Axis Aligned Bounding Box."""
  def __init__(self, min_corner: Vector3 = None, max_corner: Vector3 = None) -> None:
    self.min = min_corner or  Vector3(math.inf, math.inf, math.inf)
    self.max = max_corner or -Vector3(math.inf, math.inf, math.inf)

  @classmethod
  def from_points(cls, points: Iterable[Vector3]) -> 'AABB':
    """Construct an AABB from a list of Vector3 points."""
    aabb = cls()
    aabb.expand(points)

    return aabb

  @classmethod
  def from_aabbs(cls, aabbs: Iterable['AABB']) -> 'AABB':
    """Construct an AABB from a list of other AABBs."""
    aabb = cls()
    aabb.expand(aabbs)

    return aabb

  def expand(self, objects: Iterable[Union[Vector3, 'AABB']]) -> None:
    """Expand the bounding box to include the passed objects."""
    # If the passed parameter looks iterable, try to break it up recursively
    if isinstance(objects, (list, tuple)):
      for obj in objects:
        self.expand(obj)
      return None

    if isinstance(objects, AABB):
      # Expand the bounding box with the corner points
      self.expand([objects.min, objects.max])
    elif isinstance(objects, Vector3):
      for index, value in enumerate(objects):
        self.min[index] = min(value, self.min[index])
        self.max[index] = max(value, self.max[index])
    else:
      raise TypeError('Unexpected type passed to AABB.expand()')

  def contains(self, point: Vector3) -> bool:
    """Return True if the AABB contains the point."""
    return all(low <= value <= high for low, value, high in zip(self.min, point, self.max))

  def sphere_radius(self) -> float:
    """Create a bounding sphere for the AABB and return its radius."""
    return max([
      (self.center - corner).length()
      for corner in self.corners
    ])

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

      # Swap if reordering is necessary
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
  def is_empty(self) -> bool:
    # It's enough to check that one component is infinite to determine
    # that all of them are (assuming that the AABB is only manipulated
    # by calls to AABB.expand)
    if not math.isinf(self.min[0]):
      return False

    assert all([
      math.isinf(c)
      for v in (self.min, self.max)
      for c in v
    ]), "If one AABB component is infinite, all components should be infinite"

    return True

  @property
  def center(self):
    if self.is_empty:
      return Vector3(0, 0, 0)

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