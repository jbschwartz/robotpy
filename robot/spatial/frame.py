import math

import robot.spatial.euler as euler
from robot.spatial.vector3   import Vector3
from robot.spatial.transform import Transform

class Frame:
  def __init__(self, transform : Transform = Transform()):
    self.transform = transform

  def __rmul__(self, other):
    '''
    Transformation of a frame
    '''
    if isinstance(other, Transform):
      # TODO: Why does this work?
      #   This behaves intrinsically-- which is what we want
      return Frame(self.transform * other)

  def position(self) -> Vector3:
    '''
    Location of frame origin
    '''
    return self.transform.translation()

  def orientation(self):
    '''
    Frame orientation quaternion
    '''
    return self.transform.rotation()

  def euler(self, **kwargs):
    '''
    Return euler angle representation of frame orientation.

    Defaults to intrinsic ZYX if method and order are not provided
    '''
    method = 'intrinsic' if 'method' not in kwargs else str.lower(kwargs['method'])
    order = 'zyx' if 'order' not in kwargs else str.lower(kwargs['order'])

    if method == 'intrinsic':
      try:
        eulerFunc = getattr(euler, order)

        orientation = self.transform.rotation()
        return eulerFunc(*orientation)
      except AttributeError:
        if order not in euler.allSequences:
          raise KeyError()
        else:
          raise NotImplementedError()
    elif method == 'extrinsic':
      # Take advantage of extrinsic being the reverse order intrinsic solution
      order = order[::-1]
      intrinsic = self.euler(method = "intrinsic", order = order)
      intrinsic.reverse()
      return intrinsic
    else:
      raise KeyError()

  def x(self):
    '''
    Frame x-axis vector
    '''
    return self.transform(Vector3( 1, 0, 0 ), type='vector')

  def y(self):
    '''
    Frame y-axis vector
    '''
    return self.transform(Vector3( 0, 1, 0 ), type='vector')

  def z(self):
    '''
    Frame z-axis vector
    '''
    return self.transform(Vector3( 0, 0, 1 ), type='vector')
