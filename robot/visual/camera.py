import math
import numpy as np

from .observer import Observer

from ..spatial import vector3

Vector3 = vector3.Vector3
normalize = vector3.normalize
cross = vector3.cross

class Camera(Observer):
  ZOOM_SPEED = 15
  '''
  For now a basic wrapper around a lookat function
  '''
  def __init__(self, position : Vector3, target : Vector3, up = Vector3(0, 0, 1), aspect = 16/9):
    self.position = position
    self.target = target
    self.up = up
    self.aspect = aspect
    self.theta = 0

  def orbit(self, direction, center = None):
    if not center:
      center = self.target

    if direction == Vector3(1,0,0):
      self.theta += 10
    elif direction == Vector3(-1,0,0):
      self.theta -= 10

    # ... TODO: Movement along the surface of a sphere

    forward = self.position - self.target
    radius = forward.length()

    x = radius * math.cos(math.radians(self.theta - 90))
    y = radius * math.sin(math.radians(self.theta - 90))

    self.position = Vector3(x, y, 350)

  def zoom(self, direction):
    '''
    Move the camera in or out along its line of sight
    '''
    line_of_sight = vector3.normalize(self.position - self.target)

    self.position += self.ZOOM_SPEED * direction * line_of_sight

  def projection_matrix(self):
    fov = math.radians(60)
    f = 1.0/math.tan(fov/2.0)
    zN, zF = (100, 10000.0)
    a = self.aspect

    matrix = np.array([f/a, 0.0, 0.0,               0.0, 
                       0.0, f,   0.0,               0.0, 
                       0.0, 0.0, (zF+zN)/(zN-zF),  -1.0, 
                       0.0, 0.0, 2.0*zF*zN/(zN-zF), 0.0], np.float32)

    return matrix

  def camera_matrix(self):
    forward = normalize(self.position - self.target)
    right = normalize(cross(self.up, forward))
    up = normalize(cross(forward, right))

    translate = -Vector3(right * self.position, up * self.position, forward * self.position)

    matrix = np.array([[right.x,     up.x,        forward.x,   0.0],
                       [right.y,     up.y,        forward.y,   0.0],
                       [right.z,     up.z,        forward.z,   0.0], 
                       [translate.x, translate.y, translate.z, 1.0]], np.float32)
    
    # Inverse the matrix as the transformation moves from camera space to world space (and not the other way around)
    matrix = np.transpose(matrix).reshape(16, order='F')

    return matrix