import math

from typing  import Union
from numbers import Number

from robot     import utils
from .swizzler import Swizzler

VECTOR_X = 0
VECTOR_Y = 1
VECTOR_Z = 2

class Vector3(Swizzler):
  def __init__(self, x: float = 0, y: float = 0, z: float = 0) -> None:
    self.x = x
    self.y = y
    self.z = z

  @classmethod
  def X(cls) -> 'Vector3':
    return cls(1, 0, 0)

  @classmethod
  def Y(cls) -> 'Vector3':
    return cls(0, 1, 0)

  @classmethod
  def Z(cls) -> 'Vector3':
    return cls(0, 0, 1)

  def __abs__(self) -> 'Vector3':
    return Vector3(abs(self.x), abs(self.y), abs(self.z))

  def __round__(self, n: int) -> 'Vector3':
    return Vector3(round(self.x, n), round(self.y, n), round(self.z, n))

  def __add__(self, other: 'Vector3') -> 'Vector3':
    if isinstance(other, Vector3):
      return Vector3(self.x + other.x, self.y + other.y, self.z + other.z)
    else:
      return NotImplemented

  def __sub__(self, other: 'Vector3') -> 'Vector3':
    if isinstance(other, Vector3):
      return Vector3(self.x - other.x, self.y - other.y, self.z - other.z)
    else:
      return NotImplemented

  def __neg__(self) -> 'Vector3':
    return Vector3(-self.x, -self.y, -self.z)

  def __mul__(self, other: Union['Vector3', int, float]) -> Union['Vector3', float]:
    if isinstance(other, Number):
      return Vector3(other * self.x, other * self.y, other * self.z)
    elif isinstance(other, Vector3):
      # Dot product
      return self.x * other.x + self.y * other.y + self.z * other.z
    else:
      return NotImplemented

  __rmul__ = __mul__

  def __mod__(self, other: 'Vector3') -> 'Vector3':
    """Vector3 cross product."""
    return cross(self, other)

  def __truediv__(self, other: Union[int, float]) -> 'Vector3':
    if isinstance(other, Number):
      return Vector3(self.x / other, self.y / other, self.z / other)
    else:
      return NotImplemented

  def __eq__(self, other: Union['Vector3', int]) -> bool:
    if isinstance(other, Vector3):
      return self.x == other.x and self.y == other.y and self.z == other.z
    elif isinstance(other, int):
      if other == 0:
        # Used to check Vector3 == 0 (i.e. check if Vector3 is the zero vector)
        # This is useful for unittest.assertAlmostEqual
        return self.x == 0 and self.y == 0 and self.z == 0
    else:
      return NotImplemented

  def __str__(self) -> str:
    return f'({self.x}, {self.y}, {self.z})'

  def __getitem__(self, index: int) -> float:
    components = ['x', 'y', 'z']
    return getattr(self, components[index])

  def __setitem__(self, index: int, value: float) -> None:
    components = ['x', 'y', 'z']
    setattr(self, components[index], value)

  def __len__(self) -> int:
    return 3

  def transform(self, transform, as_type: str = "point") -> 'Vector3':
    return transform(self, as_type=as_type)

  def length(self) -> float:
    return math.sqrt(self.length_sq())

  def length_sq(self) -> float:
    return self.x**2 + self.y**2 + self.z**2

  def is_unit(self) -> bool:
    # TODO: We really should a library global control over these tolerance values
    # They shouldn't be hardcoded here.
    return math.isclose(self.length_sq(), 1.0, abs_tol=0.00001)

  def normalize(self) -> 'Vector3':
    length = self.length()
    self.x /= length
    self.y /= length
    self.z /= length
    return self

def angle_between(v1: Vector3, v2: Vector3) -> float:
  dot = v1 * v2
  lengths = (v1.length() * v2.length())

  return utils.safe_acos(dot / lengths)

def normalize(v: Vector3) -> Vector3:
  # TODO: Make sure that length is non-zero before dividing
  length = v.length()
  return Vector3(v.x / length, v.y / length, v.z / length)

def cross(a: Vector3, b: Vector3) -> Vector3:
  """Vector3 cross product."""
  return Vector3(
    a.y * b.z - a.z * b.y,
    a.z * b.x - a.x * b.z,
    a.x * b.y - a.y * b.x
  )

def almost_equal(v1: Vector3, v2: Vector3, tol = 0.00001) -> bool:
  difference = v1 - v2

  return math.isclose(difference.length_sq(), 0.0, abs_tol=tol)