import math

from .facet import Facet 

from robot.spatial import vector3

# Big TODO: Make a Buffer class which accepts a mesh in its constructor
# Store Facet objects instead of storing buffer-style floats
# There are too many instances where I want to access the facets as objects

class Mesh:
  # Number of buffer elements per vertex
  VERTEX_SIZE = 6
  # Number of buffer elements per facet
  FACET_SIZE = 3 * VERTEX_SIZE

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

  def window_iterate(self, window_size):
    n = 0
    while n < len(self.buffer):
      yield self.buffer[n : n + window_size]
      n += window_size

  def facets(self):
    '''
    Iterable list of facet data returned in the format of the buffer (v, n, v, n, ...)
    '''
    return self.window_iterate(self.FACET_SIZE)

  def vertices(self):
    '''
    Iterable list of vertex data returned in the format of the buffer (vx, vy, vz, nx, ny, nz)
    '''
    return self.window_iterate(self.VERTEX_SIZE)