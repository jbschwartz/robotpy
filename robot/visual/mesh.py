import math

from .facet import Facet 

class Mesh:
  def __init__(self, name = None):
    self.name = name
    self.facets = []

  def set_color(self, r, g, b):
    pass

  def vertices(self):
    '''
    Iterable list of vertex data returned in the format of the buffer (vx, vy, vz, nx, ny, nz)
    '''
    for facet in self.facets:
      yield facet.vertices[0]
      yield facet.vertices[1]
      yield facet.vertices[2]