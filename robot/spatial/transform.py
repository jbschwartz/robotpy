import math

import robot.spatial.dual       as     dual
import robot.spatial.quaternion as     quaternion
from robot.spatial.vector3      import Vector3
from robot.visual.facet         import Facet
from robot.visual.mesh          import Mesh

Quaternion = quaternion.Quaternion 
Dual       = dual.Dual 

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
      if 'type' in kwargs and str.lower(kwargs['type']) == 'vector':
        return self.transform_vector(other)
      else:
        return self.transform_point(other)
    elif isinstance(other, Mesh):
      return self.transform_mesh(other)
        
  def transform_vector(self, vector):
    d = Dual(Quaternion(0, *vector.xyz), Quaternion(0, 0, 0, 0))
    a = self.dual * d * dual.conjugate(self.dual)
    return Vector3(*a.r.xyz)

  def transform_point(self, point):
    d = Dual(Quaternion(), Quaternion(0, *point.xyz))
    a = self.dual * d * dual.conjugate(self.dual)
    return Vector3(*a.d.xyz)

  def transform_mesh(self, mesh):
    new_mesh = Mesh()
    new_mesh.facets = list(map(self.transform_facet, mesh.facets))

    return new_mesh

  def transform_facet(self, facet):
    new_normal = self.transform_vector(facet.normal)
    new_vertices = list(map(self.transform_point, facet.vertices))

    return Facet(new_vertices, new_normal)

  def translation(self) -> Vector3:
    # "Undo" what was done in the __init__ function by working backwards
    t = 2 * self.dual.d * quaternion.conjugate(self.dual.r)
    return Vector3(*t.xyz)

  def rotation(self) -> Quaternion:
    return self.dual.r

  def inverse(self):
    '''
    Return a new Transformation that is an inverse to this transformation
    '''
    rstar = quaternion.conjugate(self.dual.r)
    dstar = quaternion.conjugate(self.dual.d)

    return Transform(dual = Dual(rstar, dstar))