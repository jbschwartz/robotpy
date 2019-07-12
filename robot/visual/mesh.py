import math

from robot.spatial.aabb   import AABB 
from robot.spatial.kdtree import KDTree 
from robot.spatial.ray    import Ray 
from robot.visual.facet   import Facet 

class Mesh:
  def __init__(self, name = None):
    self.name = name
    self.facets = []
    self.kd_tree = None
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
    return local_ray.closest_intersection(self.facets)
    # TODO: Need to handle case where there is no KD_Tree
    # return self.kd_tree.traverse(local_ray)

  def construct_kd_tree(self):
    self.kd_tree = KDTree(self)