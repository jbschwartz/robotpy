import numpy as np

from .aabb         import AABB
from .intersection import Intersection
from .kdtree       import KDTree
from .ray          import Ray

class Mesh:
  def __init__(self, name = None, facets = None):
    self.name = name
    self.facets = facets or []
    self.aabb = AABB()

    for f in self.facets:
      self.aabb.expand(f.vertices)

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

  def get_buffer_data(self, index: int = 0) -> np.array:
    """Return a numpy array of flattened, interleaved vertex position and normal floats.

    Index is useful for storing multiple meshes in a single OpenGL buffer.
    This allows the shader program to distinguish between meshes.
    """
    data = [
      ([*vertex, *(facet.normal)], index)
      for facet in self.facets
      for vertex in facet.vertices
    ]

    return np.array(data, dtype=[('', np.float32, 6),('', np.int32)])

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

  def intersect(self, local_ray: Ray) -> Intersection:
    """Intersect a ray with Mesh and return closest found Intersection. Return Intersection.Miss() for no intersection."""
    if self.accelerator:
      return self.accelerator.intersect(local_ray)
    else:
      # Otherwise we brute force the computation
      return local_ray.closest_intersection(self.facets)