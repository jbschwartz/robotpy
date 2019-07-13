import math

from typing import Tuple

from robot.spatial.aabb      import AABB
from robot.spatial.vector3   import Vector3
from robot.visual.exceptions import DegenerateTriangleError

class Facet:
  def __init__(self, vertices = [], normal = Vector3()):
    self._aabb = None
    self.vertices = vertices
    self._edges = None
    self.normal = normal

  @property
  def edges(self):
    if not self._edges:
      self.compute_edges()

    return self._edges

  @property
  def aabb(self):
    if not self._aabb:
      self.compute_aabb()

    return self._aabb

  def compute_aabb(self):
    self._aabb = AABB(elements=self.vertices)

  def is_triangle(self):
    return len(self.vertices) == 3

  def intersect(self, ray, check_back_facing = False) -> Tuple[Vector3, float]:
    '''
    Implementation of the Moller-Trumbore intersection algorithm. Returns the point of intersection (or None for a miss).
    
    Returns `None` when the ray origin is in the triangle and the ray points away
    Returns the ray origin when the ray origin is in the triangle and the ray points towards
    '''

    E1 = self.edges[0]
    E2 = -self.edges[2]
    P = ray.direction % E2
    
    det = P * E1

    if not check_back_facing and det < 0:
      # The ray intersects the back of the triangle
      return None
    elif math.isclose(det, 0):
      # The ray is parallel to the triangle
      return None

    T = ray.origin - self.vertices[0] 
    Q = T % E1

    u = (P * T) / det
    v = Q * ray.direction / det

    # Checking if the point of intersection is outside the bounds of the triangle
    if not (0 <= u <= 1) or (v < 0) or (u + v > 1):
      return None

    t = Q * E2 / det

    return t

  def compute_edges(self):
    self._edges =  [(v2 - v1) for v1, v2 in zip(self.vertices, self.vertices[1:])]
    self._edges.append(self.vertices[0] - self.vertices[-1])

  def computed_normal(self):
    normal = self.edges[0] % self.edges[1]

    if math.isclose(normal.length(), 0.0):
      raise DegenerateTriangleError('Degenerate triangle found')
    
    normal.normalize()

    return normal 