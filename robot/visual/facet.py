import math

from typing import Tuple

from robot.spatial.aabb      import AABB
from robot.spatial.vector3   import Vector3
from robot.visual.exceptions import DegenerateTriangleError

class Facet:
  def __init__(self, vertices = [], normal = Vector3()):
    self._aabb  = None
    self._edges = None

    self.normal   = normal
    self.vertices = vertices

  @property
  def aabb(self):
    '''Lazy return an AABB bounding the Facet.'''
    if not self._aabb:
      self.compute_aabb()

    return self._aabb

  @property
  def edges(self):
    '''Lazy return a list of Facet edges.'''
    if not self._edges:
      self.compute_edges()

    return self._edges

  def append(self, vertex, recompute=True):
    '''
    Add a vertex to the Facet.

    Choose whether or not to recompute the lazy evaluated properties (e.g. edges, aabb).
    '''

    self.vertices.append(vertex)

    if recompute:
      self._aabb.extend(vertex)

      # Remove the last edge as it no longer exists
      # Insert two new edges created by new vertex
      del self._edges[-1]
    
      self.edges.extend([
        vertex - self.vertices[-1],
        self.vertices[0] - vertex
      ])

  def is_triangle(self):
    '''Returns True if the Facet has 3 vertices.'''
    return len(self.vertices) == 3

  def intersect(self, ray, check_back_facing = False) -> Tuple[Vector3, float]:
    '''
    Returns the point of ray intersection (or None for a miss).

    Returns `None` when the ray origin is in the triangle and the ray points away.
    Returns the ray origin when the ray origin is in the triangle and the ray points towards.

    This function implements the Moller-Trumbore intersection algorithm. 
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
    '''Construct a list of edges from the Facet's current vertices.'''
    self._edges =  [(v2 - v1) for v1, v2 in zip(self.vertices, self.vertices[1:])]
    self._edges.append(self.vertices[0] - self.vertices[-1])

  def compute_aabb(self):
    '''Construct the AABB bounding the Facet from the Facet's current vertices.'''
    self._aabb = AABB(elements=self.vertices)

  def computed_normal(self):
    '''Return the normal vector computed from the Facet's current vertices.'''
    normal = self.edges[0] % self.edges[1]

    if math.isclose(normal.length(), 0.0):
      raise DegenerateTriangleError('Degenerate triangle found')
    
    normal.normalize()

    return normal 