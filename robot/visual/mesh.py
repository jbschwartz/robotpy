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
      
  # def build_vertex_list(self):
  #   for facet in self.facets:
  #     for vertex in facet.vertices:
  #       self.vertices.append(vertex)
  #       if facet.computed_normal:
  #         self.vertex_normals.append(facet.computed_normal)
  #       else:
  #         self.vertex_normals.append([0, 0, 1])
  #       index = len(self.vertices) - 1
  #       self.indices.append(index)

