from .visual import Facet 

class Mesh:
  def __init__(self, name):
    self.name = name
    self.vertices = []
    self.vertex_normals = []
    self.indices = [] # Indices that make up facets
    pass

  def set_color(self, r, g, b):
    pass

  def add_facet(self, facet : Facet):
    pass