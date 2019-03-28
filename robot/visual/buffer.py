import numpy as np

class Buffer:
  def __init__(self, attributes = None):
    self.attributes = attributes
    self.mesh_count = 0
    self.data_list = []

  def append(self, meshes, adapter):
    for mesh in meshes:
      for facet in mesh.facets:
        for vertex in facet.vertices:
          self.data_list.append(adapter(self.mesh_count, mesh, facet, vertex))

      self.mesh_count += 1

  def data(self):
    return np.array(self.data_list, dtype=[('', np.float32, 6),('', np.int32, 1)])

  def vertex_size(self):
    '''
    Return the number of elements in the data_list for one vertex 
    '''
    # TODO: Determine from attributes
    return 7

  def vertex_count(self):
    return len(self.data_list)