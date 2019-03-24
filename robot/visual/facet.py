import math

from .exceptions import DegenerateTriangleError

from ..spatial import vector3

Vector3 = vector3.Vector3

class Facet:
  def __init__(self, facet_floats = None):
    self.vertices = []
    self.normal = Vector3()

    if facet_floats:
      self.normal = Vector3(*facet_floats[0:3])
      self.vertices = [
        Vector3(*facet_floats[3:6]),
        Vector3(*facet_floats[6:9]),
        Vector3(*facet_floats[9:12])
      ]

  def is_triangle(self):
    return self.size() == 3

  def size(self):
    return len(self.vertices)

  def compute_edges(self):
    # TODO: Consider caching this result
    edges = []

    for v2, v1 in zip(self.vertices[1:], self.vertices):
      edges.append(v2 - v1)

    edges.append(self.vertices[0] - self.vertices[-1])

    return edges

  def computed_normal(self):
    edges = self.compute_edges()
    normal = vector3.cross(edges[0], edges[1])

    if math.isclose(normal.length(), 0.0):
      raise DegenerateTriangleError('Degenerate triangle found')
    
    normal.normalize()

    return normal 