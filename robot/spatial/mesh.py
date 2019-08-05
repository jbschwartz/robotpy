import math

from .aabb   import AABB
from .kdtree import KDTree
from .ray    import Ray

class Mesh:
  def __init__(self, name = None, facets = None):
    self.name = name
    self.facets = facets or []
    self.aabb = AABB()

    self._accelerator = None

  @classmethod
  def from_file(cls, file_parser, file_path) -> 'Mesh':
    # TODO: The parsers are responsible for actually constructing the Mesh object
    #   Should this be so? Or should it be here?
    meshes = file_parser.parse(file_path)

    for mesh in meshes:
      mesh.accelerator = KDTree

    return meshes

  @property
  def accelerator(self):
    return self._accelerator

  @accelerator.setter
  def accelerator(self, accelerator):
    self._accelerator = accelerator(self)

  def transform(self, transform: 'Transform') -> 'Mesh':
    transformed_facets = [f.transform(transform) for f in self.facets]

    return Mesh(self.name, transformed_facets)

  def scale(self, scale = 1) -> 'Mesh':
    transformed_facets = [f.scale(scale) for f in self.facets]

    return Mesh(self.name, transformed_facets)

  def vertices(self):
    '''Iterable list of mesh vertices returned grouped by facet.'''
    for facet in self.facets:
      yield facet.vertices[0]
      yield facet.vertices[1]
      yield facet.vertices[2]

  def append(self, facet):
    '''Add a facet to the mesh.'''
    self.aabb.expand(facet.vertices)

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