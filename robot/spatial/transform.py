import math

import robot.spatial.dual       as     dual
import robot.spatial.quaternion as     quaternion
from robot.spatial.vector3      import Vector3

Quaternion = quaternion.Quaternion
Dual       = dual.Dual

class Transform:
  '''Spatial rigid body transformation in three dimensions.'''
  def __init__(self, dual: Dual = None):
    self.dual = dual or Dual(Quaternion(1, 0, 0, 0), Quaternion(0, 0, 0, 0))

  @classmethod
  def from_axis_angle_translation(cls, axis = None, angle = 0, translation = None):
    '''Create a Transformation from axis, angle, and translation components.'''
    axis        = axis        or Vector3()
    translation = translation or Vector3()

    return cls.from_orientation_translation(Quaternion.from_axis_angle(axis, angle), translation)

  @classmethod
  def from_orientation_translation(cls, orientation: Quaternion, translation: Vector3):
    '''Create a Transformation from orientation and translation.'''
    return cls(Dual(orientation, 0.5 * Quaternion(0, *translation) * orientation))

  def __mul__(self, other):
    '''Compose this Transformation with another Transformation.'''
    if isinstance(other, Transform):
      return Transform(self.dual * other.dual)
    else:
      return NotImplemented

  __rmul__ = __mul__

  def __call__(self, vector: Vector3, as_type="point"):
    '''Apply Transformation to a Vector3 with call syntax.'''
    if isinstance(vector, (list, tuple)):
      return [self.__call__(item) for item in vector]

    if not isinstance(vector, Vector3):
      raise NotImplementedError

    return self.transform(vector, as_type)

  def transform(self, vector: Vector3, as_type) -> Vector3:
    '''
    Apply the transform to the provided Vector3.

    Optionally treat the Vector3 as a point and apply a transformation to its position.
    '''
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
    '''Return the transform's translation Vector3.'''
    # "Undo" what was done in the __init__ function by working backwards
    t = 2 * self.dual.d * quaternion.conjugate(self.dual.r)
    return Vector3(*t.xyz)

  def rotation(self) -> Quaternion:
    '''Return the transform's rotation Quaternion.'''
    return self.dual.r

  def inverse(self) -> 'Transform':
    '''Return a new inverse Transformation.'''
    rstar = quaternion.conjugate(self.dual.r)
    dstar = quaternion.conjugate(self.dual.d)

    return Transform(Dual(rstar, dstar))