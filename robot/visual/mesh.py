import math

from .facet import Facet 

from ..spatial import vector3

class Mesh:
  # Number of buffer elements per facet
  FACET_SIZE = 18

  def __init__(self, name = None):
    self.name = name
    # TODO: It would be nice to formally "know" the format of this buffer
    #   so this code is more flexible to changes
    # Buffer holds vertex floats and vertex normals ([vx, vy, vz, nx, ny, nz, vx, ...])
    self.buffer = []
    self.count = 0

  def set_color(self, r, g, b):
    pass

  def append_buffer(self, facet):
    for vertex in facet.vertices:
      self.buffer.extend([*vertex, *facet.normal])
      self.count += 1

  def size(self):
    '''
    Returns the size of the mesh in number of facets
    '''
    # Every six floating points are a facet
    return int(len(self.buffer) / self.FACET_SIZE)

  def facets(self):
    '''
    Iterable list of facet data returned in the format of the buffer (v, n, v, n, ...)
    '''
    n = 0
    while n < len(self.buffer):
      yield self.buffer[n : n+self.FACET_SIZE]
      n += self.FACET_SIZE