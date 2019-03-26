import math

from . import quaternion
from . import dual
from .quaternion import Quaternion
from .dual       import Dual
from .vector3    import Vector3

from robot.visual.facet import Facet
from robot.visual.mesh  import Mesh

class Transform:
  '''
  Class representing spatial rigid body transformation in three dimensions
  '''
  def __init__(self, **kwargs):
    translation = Vector3() if 'translation' not in kwargs else kwargs['translation']
    t = Quaternion(0, *translation)
    if all(params in kwargs for params in ['axis', 'angle']):
      r = Quaternion(axis = kwargs['axis'], angle = kwargs['angle'])

      self.dual = Dual(r, 0.5 * t * r)
    elif 'translation' in kwargs:
      self.dual = Dual(Quaternion(), 0.5 * t)
    elif 'dual' in kwargs:
      self.dual = kwargs['dual']
    else:
      self.dual = Dual(Quaternion(1, 0, 0, 0), Quaternion(0, 0, 0, 0))

  def __mul__(self, other):
    '''
    Composition of transformations
    '''
    if isinstance(other, Transform):
      return Transform(dual = self.dual * other.dual)
    else:
      # This specifically allows Transform * Frame to find Frame.__rmul__, for example
      return NotImplemented

  __rmul__ = __mul__

  def __call__(self, other, **kwargs):
    if isinstance(other, Vector3):
      q = Quaternion(0, other.x, other.y, other.z)
      if 'type' in kwargs and str.lower(kwargs['type']) == 'vector':
        return self.transform_vector(q)
      else:
        return self.transform_point(q)
    elif isinstance(other, Mesh):
      return self.transform_mesh(other)
        
  def transform_vector(self, vector):
    d = Dual(vector, Quaternion(0, 0, 0, 0))
    a = self.dual * d * dual.conjugate(self.dual)
    return Vector3(a.r.x, a.r.y, a.r.z)

  def transform_point(self, point):
    d = Dual(Quaternion(), point)
    a = self.dual * d * dual.conjugate(self.dual)
    return Vector3(a.d.x, a.d.y, a.d.z)

  def transform_mesh(self, mesh):
    new_mesh = Mesh()

    for index, facet_floats in enumerate(mesh.facets()):
      vectors = [
        Vector3(*facet_floats[3:6]),  # Normal
        Vector3(*facet_floats[0:3]),  # Vertex 1
        Vector3(*facet_floats[6:9]),  # Vertex 2
        Vector3(*facet_floats[12:15]) # Vertex 3
      ]

      buffer = []
      for index, vector in enumerate(vectors):
        vectors[index] = self.__call__(vector, type = 'vector' if index == 0 else 'point')
        buffer.extend([*vectors[index]])

      new_facet = Facet(buffer)
      new_mesh.append_buffer(new_facet)

    return new_mesh

  def translation(self) -> Vector3:
    # "Undo" what was done in the __init__ function by working backwards
    t = 2 * self.dual.d * quaternion.conjugate(self.dual.r)
    return Vector3(t.x, t.y, t.z)

  def rotation(self) -> Quaternion:
    return self.dual.r

  def inverse(self):
    '''
    Return a new Transformation that is an inverse to this transformation
    '''
    rstar = quaternion.conjugate(self.dual.r)
    dstar = quaternion.conjugate(self.dual.d)

    return Transform(dual = Dual(rstar, dstar))