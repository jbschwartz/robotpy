import math

import robot.spatial.dual       as     dual
import robot.spatial.quaternion as     quaternion
from robot.spatial.vector3      import Vector3

Quaternion = quaternion.Quaternion
Dual       = dual.Dual

class Transform:
  '''
  Class representing spatial rigid body transformation in three dimensions
  '''
  def __init__(self, dual: Dual = None):
    self.dual = dual or Dual(Quaternion(1, 0, 0, 0), Quaternion(0, 0, 0, 0))

  @classmethod
  def from_axis_angle_translation(cls, axis = Vector3(), angle = 0, translation = Vector3()):
    r = Quaternion.from_axis_angle(axis, angle)
    t = Quaternion(0, *translation)
    return cls(Dual(r, 0.5 * t * r))

  def __mul__(self, other):
    '''
    Composition of transformations
    '''
    if isinstance(other, Transform):
      return Transform(self.dual * other.dual)
    else:
      # This specifically allows Transform * Frame to find Frame.__rmul__, for example
      return NotImplemented

  __rmul__ = __mul__

  def __call__(self, other, as_type="point"):
    if isinstance(other, (list, tuple)):
      return [self.__call__(item) for item in other]

    if not isinstance(other, Vector3):
      raise NotImplementedError

    return self.transform(other, as_type)

  def transform(self, vector, as_type):
    q = Quaternion(0, *vector.xyz)
    if as_type == 'vector':
      d = Dual(q, Quaternion(0, 0, 0, 0))
      a = self.dual * d * dual.conjugate(self.dual)
      return Vector3(*a.r.xyz)
    elif as_type == 'point':
      d = Dual(Quaternion(), q)
      a = self.dual * d * dual.conjugate(self.dual)
      return Vector3(*a.d.xyz)
    else:
      raise KeyError

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

    return Transform(Dual(rstar, dstar))