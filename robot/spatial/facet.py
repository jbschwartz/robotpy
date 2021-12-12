import math

from typing import Iterable

from .aabb         import AABB
from .exceptions   import DegenerateTriangleError
from .intersection import Intersection
from .ray          import Ray
from .transform    import Transform
from .vector3      import Vector3

class Facet:
  """A piece of surface geometry (typically a triangle)."""
  def __init__(self, vertices: Iterable = None, normal: Vector3 = None) -> None:
    self._aabb            = None
    self._computed_normal = None
    self._edges           = None

    self.vertices = vertices or []
    self.normal   = normal

  @property
  def aabb(self) -> AABB:
    """Lazy return a Facet AABB."""
    if not self._aabb:
      self.compute_aabb()

    return self._aabb

  @property
  def computed_normal(self) -> Vector3:
    """Lazy return a computed Facet normal."""
    if not self._computed_normal:
      self.compute_normal()

    return self._computed_normal

  @property
  def edges(self) -> Iterable:
    """Lazy return a list of Facet edges."""
    if not self._edges:
      self.compute_edges()

    return self._edges

  def transform(self, transform: Transform) -> 'Facet':
    transformed_normal   = self.normal.transform(transform, as_type="vector")
    transformed_vertices = [v.transform(transform, as_type="point") for v in self.vertices]

    return Facet(transformed_vertices, transformed_normal)

  def scale(self, scale: float = 1) -> 'Facet':
    transformed_vertices = [scale * v for v in self.vertices]

    return Facet(transformed_vertices, self.computed_normal)

  def append(self, vertex: Vector3, recompute: bool = True) -> None:
    """Add a vertex to the Facet.

    Choose whether or not to recompute the lazy evaluated properties (e.g. edges, aabb).
    """

    self.vertices.append(vertex)

    if recompute:
      self._aabb.expand(vertex)

      # Remove the last edge as it no longer exists
      # Insert two new edges created by new vertex
      del self._edges[-1]

      self.edges.extend([
        vertex - self.vertices[-1],
        self.vertices[0] - vertex
      ])

  def is_triangle(self) -> bool:
    """Returns True if the Facet has 3 vertices."""
    return len(self.vertices) == 3

  def intersect(self, ray: Ray, check_back_facing: bool = False) -> Intersection:
    """Returns the Intersection with parametric value of ray (or Intersection.Miss() for a miss).

    Returns Intersection.Miss() when the ray origin is in the triangle and the ray points away.
    Returns the ray origin when the ray origin is in the triangle and the ray points towards.

    This function implements the Moller-Trumbore intersection algorithm.
    """

    E1 = self.edges[0]
    E2 = -self.edges[2]
    P = ray.direction % E2

    det = P * E1

    if not check_back_facing and det < 0:
      # The ray intersects the back of the triangle
      return Intersection.Miss()

    try:
      inv_det = 1 / det
    except ZeroDivisionError:
      # The ray is parallel to the triangle
      return Intersection.Miss()

    T = ray.origin - self.vertices[0]
    Q = T % E1

    u = (P * T) * inv_det
    v = Q * ray.direction * inv_det

    # Checking if the point of intersection is outside the bounds of the triangle
    if not (0 <= u <= 1) or (v < 0) or (u + v > 1):
      return Intersection.Miss()

    t = Q * E2 / det

    return Intersection(t, self)

  def compute_edges(self) -> None:
    '''Construct a list of edges from the Facet's current vertices.'''
    self._edges = [v2 - v1 for v1, v2 in zip(self.vertices, self.vertices[1:])]
    self._edges.append(self.vertices[0] - self.vertices[-1])

    assert all([
      isinstance(edge, Vector3)
      for edge in self._edges
    ]), "All edges must be of Vector3 type"

  def compute_aabb(self) -> None:
    '''Construct the AABB bounding the Facet from the Facet's current vertices.'''
    self._aabb = AABB.from_points(self.vertices)

  def compute_normal(self) -> None:
    '''Compute the normal vector from the Facet's current vertices.'''
    try:
      self._computed_normal = (self.edges[0] % self.edges[1]).normalize()
    except ZeroDivisionError:
      raise DegenerateTriangleError('Degenerate triangle found')