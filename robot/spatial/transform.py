import math
from . import quaternion, dual, vector3

Quaternion = quaternion.Quaternion
Dual = dual.Dual
Vector3 = vector3.Vector3

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
    q = Quaternion(0, other.x, other.y, other.z)

    if 'type' in kwargs and str.lower(kwargs['type']) == 'vector':
      # Transformation of a vector
      d = Dual(q, Quaternion(0, 0, 0, 0))
      a = self.dual * d * dual.conjugate(self.dual)
      return Vector3(a.r.x, a.r.y, a.r.z)
    else:
      # Transformation of a point
      d = Dual(Quaternion(), q)
      a = self.dual * d * dual.conjugate(self.dual)
      return Vector3(a.d.x, a.d.y, a.d.z)
      
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