import math

from ..spatial import vector3

Vector3 = vector3.Vector3

class Facet:
  def __init__(self):
    self.passed_normal = Vector3()
    self.computed_normal = None
    self.vertices = []

  def is_complete(self):
    return len(self.vertices) == 3

  def has_conflicting_normal(self):
    if not self.computed_normal:
      self.compute_normal()

    return not vector3.almost_equal(self.passed_normal, self.computed_normal, 0.0001)

  def compute_normal(self):
    if self.is_complete():
      edges = [ self.vertices[1] - self.vertices[0], self.vertices[2] - self.vertices[1]]
      normal = vector3.cross(edges[0], edges[1])

      if math.isclose(normal.length(), 0.0):
        # TODO: Probably should make a specific exception for this
        raise Exception('Degenerate triangle found')
      
      normal.normalize()

      self.computed_normal = normal 
    else:
      # TODO: Figure out what an appropriate action would be here
      pass