import math

class Quaternion:
  ''' 
  Class for representing quaternions of the form r + xi + yj + dk
  '''

  def __init__(self, r = 1, x = 0, y = 0, z = 0, **kwargs):
    '''
    Quaternion accepts four parameters or converts an 'axis-angle' input
    '''
    if all(params in kwargs for params in ['axis', 'angle']):
      # Angle expected in radians
      angle = kwargs['angle'] / 2

      axis = math.sin(angle) * kwargs['axis']

      self.r = math.cos(angle)
      self.x = axis.x
      self.y = axis.y
      self.z = axis.z
    else:
      self.r = r
      self.x = x
      self.y = y
      self.z = z

  def __abs__(self):
    return Quaternion(abs(self.r), abs(self.x), abs(self.y), abs(self.z))
  
  def __round__(self, n):
    return Quaternion(round(self.r, n), round(self.x, n), round(self.y, n), round(self.z, n))

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
    elif isinstance(other, int):
      if other == 0:
        # Used to check Quaternion == 0 (i.e. check if Quaternion is the zero vector)
        # This is useful for unittest.assertAlmostEqual
        return self.r == 0 and self.x == 0 and self.y == 0 and self.z == 0

  def __str__(self):
    return f'({self.r}, {self.x}, {self.y}, {self.z})'

  def __getitem__(self, key):
    if key == 0:
        return self.r
    elif key == 1:
        return self.x
    elif key == 2:
        return self.y
    elif key == 3:
        return self.z
    else:
        raise IndexError()

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