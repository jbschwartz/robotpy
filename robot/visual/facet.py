import math

from .exceptions import DegenerateTriangleError

from ..spatial import vector3

Vector3 = vector3.Vector3

class Facet:
  def __init__(self):
    self.passed_normal = Vector3()
    self.computed_normal = None
    self.vertices = []

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

  def has_conflicting_normal(self):
    if not self.computed_normal:
      self.compute_normal()

    return not vector3.almost_equal(self.passed_normal, self.computed_normal, 0.0001)

  def compute_normal(self):
    edges = self.compute_edges()
    normal = vector3.cross(edges[0], edges[1])

    if math.isclose(normal.length(), 0.0):
      raise DegenerateTriangleError('Degenerate triangle found')
    
    normal.normalize()

    self.computed_normal = normal 

  def mean_edge_length(self):
    edges = self.compute_edges()
    total_length = sum(list(map(lambda edge: edge.length(), edges)))
    
    return total_length / edges