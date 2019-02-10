import math

class Quaternion:
  ''' 
  Class for representing quaternions of the form r + xi + yj + dk
  '''

  def __init__(self, r = 1, x = 0, y = 0, z = 0, **kwargs):
    self.r = r
    if 'axis' in kwargs:
      axis = kwargs['axis']
      self.x = axis.x
      self.y = axis.y
      self.z = axis.z
    else:
      self.x = x
      self.y = y
      self.z = z

  def __add__(self, other):
    if isinstance(other, Quaternion):
      return Quaternion(self.r + other.r, self.x + other.x, self.y + other.y, self.z + other.z)

  def __sub__(self, other):
    if isinstance(other, Quaternion):
      return Quaternion(self.r - other.r, self.x - other.x, self.y - other.y, self.z - other.z)

  def __neg__(self):
    return Quaternion(-self.r, -self.x, -self.y, -self.z)

  def __mul__(self, other):
    '''
    Quaternion multiplication

    If passed a number, scalar multiplication is performed.
    If passed another quaternion, quaternion multiplication is performed.
    '''
    if isinstance(other, (int, float)):
      return Quaternion(self.r * other, self.x * other, self.y * other, self.z * other)
    elif isinstance(other, Quaternion):
      r = self.r * other.r - self.x * other.x - self.y * other.y - self.z * other.z
      x = self.r * other.x + self.x * other.r + self.y * other.z - self.z * other.y
      y = self.r * other.y - self.x * other.z + self.y * other.r + self.z * other.x
      z = self.r * other.z + self.x * other.y - self.y * other.x + self.z * other.r

      return Quaternion(r, x, y, z)

  __rmul__ = __mul__

  def __truediv__(self, other):
    if isinstance(other, (int, float)):
      reciprocal = 1 / other
      return reciprocal * self

  def __eq__(self, other):
    if isinstance(other, Quaternion):
      return self.r == other.r and self.x == other.x and self.y == other.y and self.z == other.z

  def __str__(self):
    return f'({self.r}, {self.x}, {self.y}, {self.z})'

  def conjugate(self):
    '''
    Conjugates the quaternion instance
    '''
    self.x = -self.x
    self.y = -self.y
    self.z = -self.z

  def norm(self):
    return math.sqrt(self.r**2 + self.x**2 + self.y**2 + self.z**2)

  def normalize(self):
    '''
    Normalizes the quaternion instance (i.e. norm of one)
    '''
    norm = self.norm()
    self.r /= norm
    self.x /= norm
    self.y /= norm
    self.z /= norm

def conjugate(q):
  return Quaternion(q.r, -q.x, -q.y, -q.z)