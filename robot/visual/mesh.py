from .facet import Facet 

from ..spatial import vector3

class Mesh:
  def __init__(self, name):
    self.name = name
    self.vertices = []
    self.vertex_normals = []
    self.indices = [] # Indices that make up facets
    pass

  def set_color(self, r, g, b):
    pass

  def check_duplicate(self, new_vertex):
    for index, stored_vertex in enumerate(self.vertices):
      if vector3.almost_equal(stored_vertex, new_vertex):
        return index
    
    return -1

  def add_facet(self, facet : Facet):
    # TODO: Spatial hashing to remove duplicates!
    # TODO: Assert that the facet has three verticies
    for new_vertex in facet.vertices:
      duplicate_index = self.check_duplicate(new_vertex)
      if duplicate_index >= 0:
        self.indices.append(duplicate_index)
      else:
        self.vertices.append(new_vertex)
        self.vertex_normals.append(facet.computed_normal)
        self.indices.append(len(self.vertices) - 1)