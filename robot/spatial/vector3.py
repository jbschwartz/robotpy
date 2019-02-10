import math

class Vector3:
  def __init__(self, x = 0, y = 0, z = 0):
    self.x = x
    self.y = y
    self.z = z

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

  def __str__(self):
    return f'({self.x}, {self.y}, {self.z})'

  def length(self):
    return math.sqrt(self.lengthSq())

  def lengthSq(self):
    return self.x**2 + self.y**2 + self.z**2
  
  def normalize(self):
    length = self.length()
    self.x /= length
    self.y /= length
    self.z /= length

def angleBetween(v1, v2):
  dot = v1 * v2
  return math.acos(dot / (v1.length() * v2.length()))

def normalize(v):
  length = v.length()
  return Vector3(v.x / length, v.y / length, v.z / length)