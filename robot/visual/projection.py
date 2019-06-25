import abc, enum, math

from robot.spatial.matrix4 import Matrix4
from robot.spatial.vector3 import Vector3

def recalculate():
  def _recalculate(f):
    def wrapper(self, *args):
      value = f(self, *args)
      self.calculate()
      self.calculate_inverse()
      return value
    return wrapper
  return _recalculate

class Projection(abc.ABC):
  def __init__(self):
    self.calculate()
    self.calculate_inverse()

  @abc.abstractmethod
  def project(self, v):
    pass

  # @abc.abstractmethod
  # def unproject(self, ndc):
  #   pass

  @abc.abstractmethod
  def calculate(self):
    pass

  @abc.abstractmethod
  def calculate_inverse(self):
    pass

class OrthoProjection(Projection):
  pass
#   def __init__(self, aspect = 16/9, width = 1):
#     self._aspect = aspect
#     self._width  = width

#     super().__init__()

#   def calculate(self):
#     m11 = 1 / self.width
#     m22 = 1 / (self.width * self.aspect)
#     m33 = -2 / (self.far_clip - self.near_clip)
#     m34 = -(self.far_clip + self.near_clip) / (self.far_clip - self.near_clip)

#     self.matrix = Matrix4([m11,  0.0,  0.0,  0.0,
#                                         0.0,  m22,  0.0,  0.0,
#                                         0.0,  0.0,  m33,  0.0,
#                                         0.0,  0.0,  m34,  1.0])

                                        
#   def calculate_inverse(self):
#     p11 = self.matrix.elements[0]
#     p22 = self.matrix.elements[5]
#     p33 = self.matrix.elements[10]
#     p34 = self.matrix.elements[14]

#     m11 = 1 / p11
#     m22 = 1 / p22
#     m43 = 1 / p34 
#     m44 = p33 / p34

#     # Remember: the elements of the matrix look transposed 
#     self.inverse = Matrix4([m11, 0.0,  0.0, 0.0, 
#                             0.0, m22,  0.0, 0.0, 
#                             0.0, 0.0,  0.0, m43, 
#                             0.0, 0.0, -1.0, m44])

#   def project(self, v):
#     m11 = self.projection.elements[0]
#     m22 = self.projection.elements[5]
#     m33 = self.projection.elements[10]
#     m34 = self.projection.elements[14]

#     return Vector3()

class PerspectiveProjection(Projection):
  def __init__(self, aspect = 16/9, fov = math.radians(60), near_clip = 100, far_clip = 10000):
    self._aspect     = aspect
    self._fov        = fov
    self._near_clip  = near_clip
    self._far_clip   = far_clip
    self.matrix      = Matrix4()

    super().__init__()
  
  @property
  def fov(self):
    '''
    Get the vertical field of view of the camera
    '''
    return self._fov

  @fov.setter
  def fov(self, fov):
    self._fov = fov
    self.calculate()
    self.calculate_inverse()

  @property
  def near_clip(self):
    return self._near_clip

  @near_clip.setter
  def near_clip(self, near_clip):
    self._near_clip = near_clip
    self.calculate()
    self.calculate_inverse()

  @property
  def far_clip(self):
    return self._far_clip

  @far_clip.setter
  def far_clip(self, far_clip):
    self._far_clip = far_clip
    self.calculate()
    self.calculate_inverse()

  @property
  def aspect(self):
    return self._aspect

  @aspect.setter
  def aspect(self, aspect):
    self._aspect = aspect
    self.calculate()
    self.calculate_inverse()

  def calculate(self):
    f = 1.0 / math.tan(self.fov / 2.0)
    z_width = self.far_clip - self.near_clip

    m11 = f / self.aspect
    m22 = f
    m33 = (self.far_clip + self.near_clip) / (-z_width)
    m34 = 2 * self.far_clip * self.near_clip / (-z_width)

    # Remember: the elements of the matrix look transposed 
    self.matrix = Matrix4([m11,  0.0,  0.0,  0.0, 
                           0.0,  m22,  0.0,  0.0, 
                           0.0,  0.0,  m33, -1.0, 
                           0.0,  0.0,  m34,  0.0])

  def calculate_inverse(self):
    p11 = self.matrix.elements[0]
    p22 = self.matrix.elements[5]
    p33 = self.matrix.elements[10]
    p34 = self.matrix.elements[14]

    m11 = 1 / p11
    m22 = 1 / p22
    m43 = 1 / p34 
    m44 = p33 / p34

    # Remember: the elements of the matrix look transposed 
    self.inverse = Matrix4([m11, 0.0,  0.0, 0.0, 
                            0.0, m22,  0.0, 0.0, 
                            0.0, 0.0,  0.0, m43, 
                            0.0, 0.0, -1.0, m44])

  def project(self, v):
    m11 = self.matrix.elements[0]
    m22 = self.matrix.elements[5]
    m33 = self.matrix.elements[10]
    m34 = self.matrix.elements[14]

    return Vector3(m11 * v.x, m22 * v.y, m33 * v.z + m34) / -v.z
