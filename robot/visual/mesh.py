import math

from robot.spatial.aabb import AABB 
from robot.spatial.ray  import Ray 
from robot.visual.facet import Facet 

class Mesh:
  def __init__(self, name = None):
    self.name = name
    self.facets = []
    self.aabb = AABB()

  def vertices(self):
    '''
    Iterable list of vertex data returned in the format (vx, vy, vz)
    '''
    for facet in self.facets:
      yield facet.vertices[0]
      yield facet.vertices[1]
      yield facet.vertices[2]

  def append(self, facet):
    for vertex in facet.vertices:
      self.aabb.extend(vertex)
      
    self.facets.append(facet)

  def intersect(self, local_ray : Ray):
    closest = None

    # TODO: This would be the place to look into using a KD Tree
    for triangle in self.facets:
      t = triangle.intersect(local_ray)
      if t and (closest is None or t < closest):
        closest = t

    return closest