from robot.spatial.aabb import AABB 
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