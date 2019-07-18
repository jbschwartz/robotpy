import math

from robot.spatial.aabb import AABB
from robot.spatial.ray  import Ray

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
    '''Iterable list of mesh vertices returned grouped by facet.'''
    for facet in self.facets:
      yield facet.vertices[0]
      yield facet.vertices[1]
      yield facet.vertices[2]

  def append(self, facet):
    '''Add a facet to the mesh.'''
    self.aabb.extend(*facet.vertices)

    self.facets.append(facet)

    if self.accelerator:
      self.accelerator.update(self, facet)

  def intersect(self, local_ray : Ray):
    '''Intersect a ray with mesh and return the ray's t parameter for found intersections. Return None for no intersections.'''
    if self.accelerator:
      return self.accelerator.intersect(local_ray)
    else:
      # Otherwise we brute force the computation
      return local_ray.closest_intersection(self.facets)