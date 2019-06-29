import abc, enum, math

from robot.spatial.matrix4 import Matrix4
from robot.spatial.vector3 import Vector3

class Projection(abc.ABC):
  def __init__(self, near_clip, far_clip):
    self.near_clip = near_clip
    self.far_clip  = far_clip

    self.update()

  @abc.abstractmethod
  def __setattr__(self, attribute, value, allowed):
    # Watch values in the `allowed` list so that the projection can be recalculated when they change
    if attribute in allowed:
      object.__setattr__(self, attribute, value)
      try:
        self.update()
      except AttributeError:
        # It's possible we're here because the `allowed` values haven't been initialized
        # So if the attribute is in `allowed`, we'll just ignore it
        if attribute not in allowed:
          raise AttributeError
    elif attribute in ['matrix', 'inverse', 'near_clip', 'far_clip']:
      # These are common to all projections
      object.__setattr__(self, attribute, value)
    else:
      raise AttributeError

  def update(self):
    self.calculate()
    self.calculate_inverse()

  @abc.abstractmethod
  def project(self, v):
    pass

  @abc.abstractmethod
  def calculate(self):
    pass

  @abc.abstractmethod
  def calculate_inverse(self):
    pass

  @abc.abstractmethod
  def zoom(self):
    pass

class OrthoProjection(Projection):
  def __init__(self, aspect, width, near_clip = 100, far_clip = 10000):
    self.aspect = aspect
    self.width  = width

    super().__init__(near_clip, far_clip)

  def __setattr__(self, attribute, value):
    super().__setattr__(attribute, value, ['aspect', 'width', 'height'])

  @property
  def height(self):
    return self.width / self.aspect

  @height.setter
  def height(self, height):
    self.width = height * self.aspect

  def calculate(self):
    z_width = self.far_clip - self.near_clip

    m11 =  2 / (self.width)
    m22 =  2 / (self.width / self.aspect)
    m33 = -2 / (z_width)
    m34 = -(self.far_clip + self.near_clip) / (z_width)

    self.matrix = Matrix4([m11, 0.0, 0.0, 0.0,
                           0.0, m22, 0.0, 0.0,
                           0.0, 0.0, m33, 0.0,
                           0.0, 0.0, m34, 1.0])
                                        
  def calculate_inverse(self):
    p11 = self.matrix.elements[0]
    p22 = self.matrix.elements[5]
    p33 = self.matrix.elements[10]
    p34 = self.matrix.elements[14]

    m11 = 1 / p11
    m22 = 1 / p22
    m33 = 1 / p33 
    m43 = -m33 * p34

    # Remember: the elements of the matrix look transposed 
    self.inverse = Matrix4([m11, 0.0, 0.0, 0.0, 
                            0.0, m22, 0.0, 0.0, 
                            0.0, 0.0, m33, m43, 
                            0.0, 0.0, 0.0, 1.0])

  def project(self, v):
    m11 = self.matrix.elements[0]
    m22 = self.matrix.elements[5]
    m33 = self.matrix.elements[10]
    m34 = self.matrix.elements[14]

    # This code assumes that the w component is always 1 (otherwise it would be `+ m34 * v.w` at the end)
    return Vector3(m11 * v.x, m22 * v.y, m33 * v.z + m34)

  def zoom(self, amount):
    self.width += amount

class PerspectiveProjection(Projection):
  def __init__(self, aspect = 16/9, fov = math.radians(60), near_clip = 100, far_clip = 10000):
    self.aspect     = aspect
    self.fov        = fov
    self.matrix      = Matrix4()

    super().__init__(near_clip, far_clip)
  
  def __setattr__(self, attribute, value):
    super().__setattr__(attribute, value, ['aspect', 'fov'])

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

    # This code assumes that the w component is always 1 (thats why m44 is not present)
    return Vector3(m11 * v.x, m22 * v.y, m33 * v.z + m34) / -v.z

  def zoom(self, amount):
    self.fov += amount