import math

from .        import dual, quaternion
from .euler   import Axes, Order
from .vector3 import Vector3

Quaternion = quaternion.Quaternion
Dual       = dual.Dual

class Transform:
  '''Spatial rigid body transformation in three dimensions.'''
  def __init__(self, dual: Dual = None):
    self.dual = dual or Dual(Quaternion(1, 0, 0, 0), Quaternion(0, 0, 0, 0))

  @classmethod
  def from_json(cls, payload) -> 'Transform':
    try:
      axes  = Axes[payload['euler']['axes'].upper()]
      order = Order[payload['euler']['order'].upper()]
      angles_radians = list(map(math.radians, payload['euler']['angles']))
      orientation = Quaternion.from_euler(angles_radians, axes, order)

      translation = Vector3(*payload['translation'])

      return cls.from_orientation_translation(orientation, translation)
    except KeyError:
      # TODO: This is a catchall. Will not provide very useful debugging or handling information
      #   This could be caused by the json file not having those particular keys present. Need to provide defaults
      # TODO: Handle unknown euler angle axes or order
      #   Maybe we can choose a default instead of just erroring out.
      raise

  @classmethod
  def from_axis_angle_translation(cls, axis = None, angle = 0, translation = None):
    '''Create a Transformation from axis, angle, and translation components.'''
    axis        = axis        or Vector3()
    translation = translation or Vector3()

    return cls.from_orientation_translation(Quaternion.from_axis_angle(axis, angle), translation)

  @classmethod
  def from_orientation_translation(cls, orientation: Quaternion, translation: Vector3 = None):
    '''Create a Transformation from orientation and translation.'''
    translation = translation or Vector3()
    return cls(Dual(orientation, 0.5 * Quaternion(0, *translation) * orientation))

  def __mul__(self, other):
    '''Compose this Transformation with another Transformation.'''
    if isinstance(other, Transform):
      return Transform(self.dual * other.dual)
    else:
      return NotImplemented

  @classmethod
  def Identity(cls) -> 'Transform':
    """Construct an identity transformation (i.e., a transform that does not transform)."""
    return cls(Dual(Quaternion(1, 0, 0, 0), Quaternion(0, 0, 0, 0)))

  __rmul__ = __mul__

  def __call__(self, vector: Vector3, as_type="point"):
    '''Apply Transformation to a Vector3 with call syntax.'''
    if isinstance(vector, (list, tuple)):
      return [self.__call__(item, as_type) for item in vector]

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

  # TODO: Make me a property
  def translation(self) -> Vector3:
    '''Return the transform's translation Vector3.'''
    # "Undo" what was done in the __init__ function by working backwards
    t = 2 * self.dual.d * quaternion.conjugate(self.dual.r)
    return Vector3(*t.xyz)

  # TODO: Make me a property
  def rotation(self) -> Quaternion:
    '''Return the transform's rotation Quaternion.'''
    return self.dual.r

  def inverse(self) -> 'Transform':
    '''Return a new inverse Transformation.'''
    rstar = quaternion.conjugate(self.dual.r)
    dstar = quaternion.conjugate(self.dual.d)

    return Transform(Dual(rstar, dstar))