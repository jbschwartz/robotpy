import math
import numpy as np

from ..spatial import vector3

Vector3 = vector3.Vector3
normalize = vector3.normalize
cross = vector3.cross

class Camera:
  '''
  For now a basic wrapper around a lookat function
  '''
  def __init__(self, position : Vector3, target : Vector3, up = Vector3(0, 1, 0), aspect = 16/9):
    self.position = position
    self.target = target
    self.up = up
    self.aspect = aspect

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