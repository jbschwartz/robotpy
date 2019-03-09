import math

class Vector3:
  def __init__(self, x = 0, y = 0, z = 0):
    self.x = x
    self.y = y
    self.z = z

  def __abs__(self):
    return Vector3(abs(self.x), abs(self.y), abs(self.z))
  
  def __round__(self, n):
    return Vector3(round(self.x, n), round(self.y, n), round(self.z, n))

  def __add__(self, other):
    if isinstance(other, Vector3):
      return Vector3(self.x + other.x, self.y + other.y, self.z + other.z)

  def __sub__(self, other):
    if isinstance(other, Vector3):
      return Vector3(self.x - other.x, self.y - other.y, self.z - other.z)

  def __neg__(self):
    return Vector3(-self.x, -self.y, -self.z)

  def __mul__(self, other):
    if isinstance(other, (int, float)):
      return Vector3(other * self.x, other * self.y, other * self.z)
    if isinstance(other, Vector3):
      # Dot product
      return self.x * other.x + self.y * other.y + self.z * other.z

  __rmul__ = __mul__

  def __truediv__(self, other):
    if isinstance(other, (int, float)):
      return Vector3(self.x / other, self.y / other, self.z / other)

  def __eq__(self, other):
    if isinstance(other, Vector3):
      return self.x == other.x and self.y == other.y and self.z == other.z
    elif isinstance(other, int):
      if other == 0:
        # Used to check Vector3 == 0 (i.e. check if Vector3 is the zero vector)
        # This is useful for unittest.assertAlmostEqual
        return self.x == 0 and self.y == 0 and self.z == 0

  def __str__(self):
    return f'({self.x}, {self.y}, {self.z})'

  def __getitem__(self, key):
    if key == 0:
        return self.x
    elif key == 1:
        return self.y
    elif key == 2:
        return self.z
    else:
        raise IndexError()

  def length(self):
    return math.sqrt(self.length_sq())

  def length_sq(self):
    return self.x**2 + self.y**2 + self.z**2

  def is_unit(self):
    return math.isclose(self.length_sq(), 1.0)
  
  def normalize(self):
    length = self.length()
    self.x /= length
    self.y /= length
    self.z /= length

def angle_between(v1, v2):
  dot = v1 * v2
  return math.acos(dot / (v1.length() * v2.length()))

def normalize(v):
  # TODO: Make sure that length is non-zero before dividing
  length = v.length()
  return Vector3(v.x / length, v.y / length, v.z / length)

def cross(a, b):
  '''
  Vector cross product
  '''
  return Vector3(
    a.y * b.z - a.z * b.y,
    a.z * b.x - a.x * b.z,
    a.x * b.y - a.y * b.x
  )

def almost_equal(v1, v2):
  difference = v1 - v2

  return math.isclose(difference.length(), 0.0)