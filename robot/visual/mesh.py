import math

from robot.spatial.aabb   import AABB 
from robot.spatial.kdtree import KDTree 
from robot.spatial.ray    import Ray 

class Mesh:
  def __init__(self, name = None):
    self.name = name
    self.facets = []
    self.aabb = AABB()
    
    self._accelerator = None

  @property
  def accelerator(self):
    return self._accelerator

  @accelerator.setter
  def accelerator(self, accelerator):
    self._accelerator = accelerator(self)

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
    
    if self.accelerator:
      self.accelerator.update(self, facet)

  def intersect(self, local_ray : Ray):
    if self.accelerator:
      return self.accelerator.intersect(local_ray)
    else:
      # Otherwise we brute force the computation
      return local_ray.closest_intersection(self.facets)