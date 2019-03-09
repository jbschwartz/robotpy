import math

from ..spatial import vector3

Vector3 = vector3.Vector3

class Facet:
  def __init__(self):
    self.passed_normal = Vector3()
    self.vertices = []

  def is_complete(self):
    return len(self.vertices) == 3

  def has_conflicting_normal(self):
    # TODO: Probably need to fix this later: make math.isclose work on Vector3
    difference = self.passed_normal - self.computed_normal()

    return not math.isclose(difference.length(), 0.0)

  def computed_normal(self):
    if self.is_complete():
      edges = [ self.vertices[1] - self.vertices[0], self.vertices[2] - self.vertices[1]]
      normal = vector3.cross(edges[0], edges[1])

      if math.isclose(normal.length(), 0.0):
        raise Exception('Degenerate triangle found')
      
      normal.normalize()

      return normal 
    else:
      # TODO: Figure out what an appropriate action would be here
      pass