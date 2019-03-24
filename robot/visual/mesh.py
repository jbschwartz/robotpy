import math

from .facet import Facet 

from ..spatial import vector3

class Mesh:
  def __init__(self, name = None):
    self.name = name
    self.buffer = []
    self.count = 0

  def set_color(self, r, g, b):
    pass

  def append_buffer(self, facet):
    for vertex in facet.vertices:
      self.buffer.extend([*vertex, *facet.normal])
      self.count += 1