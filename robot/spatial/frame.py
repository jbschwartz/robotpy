import math

from . import dual, quaternion, vector3

Dual = dual.Dual
Quaternion = quaternion.Quaternion
Vector3 = vector3.Vector3

class Frame:
  def __init__(self, pose : Dual = Dual(Quaternion(1, 0, 0, 0), Quaternion(0, 0, 0, 0))):
    self.pose = pose

  def position(self):
    '''
    Location of frame origin
    '''
    t = 2 * self.pose.d * quaternion.conjugate(self.pose.r)
    return Vector3(t.x, t.y, t.z)
  
  def orientation(self):
    '''
    Frame orientation quaternion
    '''
    return self.pose.r

  def euler(self):
    '''
    Return euler angle representation of frame orientation

    Only implements intrinsic ZYX rotation currently
    '''
    # TODO: Include kwargs for method=[intrinsic, extrinsic] order=[ZYX, ZYZ, ...]
    orientation = self.orientation()
    r = orientation.r
    x = orientation.x
    y = orientation.y
    z = orientation.z

    rSq = r ** 2
    xSq = x ** 2
    ySq = y ** 2
    zSq = z ** 2

    Z = math.atan2(2 * (x * y + r * z), rSq + xSq - ySq - zSq)
    Yp = math.asin(-2 * (x * z - r * y))
    Xpp = math.atan2(2 * (y * z + r * x), rSq - xSq - ySq + zSq)

    return Vector3(Z, Yp, Xpp)

  def _axis(self, **kwargs):
    if 'axis' in kwargs:
      q = Quaternion(0, 0, 0, 0)
      axis = str.lower(kwargs['axis'])
      if axis in ['x', 'y', 'z']:
        setattr(q, axis, 1)
      else:
        # TODO: Handle unknown axis
        pass

      o = self.orientation()
      a = o * q * quaternion.conjugate(o)
      return Vector3(a.x, a.y, a.z)
      

  def x(self):
    '''
    Frame x-axis vector
    '''
    return self._axis(axis = 'x')

  def y(self):
    '''
    Frame y-axis vector
    '''
    return self._axis(axis = 'y')

  def z(self):
    '''
    Frame z-axis vector
    '''
    return self._axis(axis = 'z')
