import math

from robot.spatial.vector3   import Vector3
from robot.spatial.ray       import Ray
from robot.visual.exceptions import DegenerateTriangleError

class Facet:
  def __init__(self, vertices = [], normal = Vector3()):
    self.vertices = vertices
    self.normal = normal

  def is_triangle(self):
    return len(self.vertices) == 3

  def intersect(self, ray, check_back_facing = False) -> Vector3:
    '''
    Implementation of the Moller-Trumbore intersection algorithm. Returns the point of intersection (or None for a miss).
    
    Returns `None` when the ray origin is in the triangle and the ray points away
    Returns the ray origin when the ray origin is in the triangle and the ray points towards
    '''
    edges = self.compute_edges()
    P = ray.direction % edges[1]
    
    det = edges[0] * (P)

    if not check_back_facing and det < 0:
      # The ray intersects the back of the triangle
      return None
    elif math.isclose(det, 0):
      # The ray is parallel to the triangle
      return None

    T = ray.origin - self.vertices[0] 
    Q = T % edges[0]

    u = P * T / det
    v = Q * ray.direction / det

    # Checking if the point of intersection is outside the bounds of the triangle
    if not (0 <= u <= 1) or (v < 0) or (u + v > 1):
      return None

    t = Q * edges[1] / det

    return ray.evaluate(t)

  def compute_edges(self):
    # TODO: Consider caching this result
    edges = []

    for v2, v1 in zip(self.vertices[1:], self.vertices):
      edges.append(v2 - v1)

    edges.append(self.vertices[0] - self.vertices[-1])

    return edges

  def computed_normal(self):
    edges = self.compute_edges()
    normal = edges[0] % edges[1]

    if math.isclose(normal.length(), 0.0):
      raise DegenerateTriangleError('Degenerate triangle found')
    
    normal.normalize()

    return normal 