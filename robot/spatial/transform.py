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
    if all(params in kwargs for params in ['axis', 'angle']):
      translation = Vector3()
      if 'translation' in kwargs:
        translation = kwargs['translation']

      # kwargs['angle'] expected in radians
      c = math.cos(kwargs['angle'] / 2)
      s = math.sin(kwargs['angle'] / 2)

      r = Quaternion(c, axis = s * kwargs['axis'])
      t = Quaternion(0, axis = translation)

      self.dual = Dual(r, 0.5 * t * r)
    elif 'translation' in kwargs:
      t = Quaternion(0, axis = kwargs['translation'])
      self.dual = Dual(Quaternion(), 0.5 * t)
    elif 'dual' in kwargs:
      self.dual = kwargs['dual']

  def __mul__(self, other):
    '''
    Composition of transformations
    '''
    if isinstance(other, Transform):
      return Transform(dual = self.dual * other.dual)

  __rmul__ = __mul__

  def apply(self, p):
    d = Dual(Quaternion(), Quaternion(0, p.x, p.y, p.z))
    q = self.dual * d * dual.conjugate(self.dual)

    return Vector3(q.d.x, q.d.y, q.d.z)