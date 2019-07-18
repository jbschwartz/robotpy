from robot.spatial import quaternion
Quaternion = quaternion.Quaternion

class Dual:
  '''
  Class for representing dual numbers of the form r + dε
  '''

  def __init__(self, r, d):
    self.r = r
    self.d = d

  def __abs__(self):
    return Dual(abs(self.r), abs(self.d))

  def __round__(self, n):
    return Dual(round(self.r, n), round(self.d, n))

  def __add__(self, other):
    return Dual(self.r + other.r, self.d + other.d)

  def __sub__(self, other):
    return Dual(self.r - other.r, self.d - other.d)

  def __mul__(self, other):
    '''
    Dual quaternion multiplication

    If passed a number, scalar multiplication is performed.
    If passed another dual quaternion, dual quaternion multiplication is performed.
    '''
    if isinstance(other, (int, float)):
      return Dual(other * self.r, other * self.d)
    elif isinstance(other, Dual):
      return Dual(self.r * other.r, self.r * other.d + self.d * other.r)

  __rmul__ = __mul__

  def __truediv__(self, other):
    if isinstance(other, (int, float)):
      reciprocal = 1 / other
      return reciprocal * self

  def __eq__(self, other):
    if isinstance(other, Dual):
      return self.r == other.r and self.d == other.d
    elif isinstance(other, int):
      if other == 0:
        # Used to check Dual == 0 (i.e. check if Dual is the zero vector)
        # This is useful for unittest.assertAlmostEqual
        return self.r == 0 and self.d == 0

  def __str__(self):
    return f'{self.r} + {self.d}' + u"\u03B5"

  def conjugate(self):
    '''
    Conjugates the dual instance
    '''
    if isinstance(self.r, Quaternion) and isinstance(self.d, Quaternion):
      self.r.conjugate()
      self.d = -quaternion.conjugate(self.d)
    elif isinstance(self.r, (int, float)) and isinstance(self.d, (int, float)):
      self.d = -self.d

  def norm(self):
    pass

def conjugate(obj):
  if isinstance(obj.r, Quaternion) and isinstance(obj.d, Quaternion):
    return Dual(quaternion.conjugate(obj.r), -quaternion.conjugate(obj.d))