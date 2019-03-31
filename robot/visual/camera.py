import math
import numpy as np

from .observer import Observer

import robot.spatial as spatial

Vector3 = spatial.vector3.Vector3

class Camera(Observer):
  ZOOM_SPEED = 15
  '''
  For now a basic wrapper around a lookat function
  '''
  def __init__(self, position : Vector3, target : Vector3, up = Vector3(0, 0, 1), aspect = 16/9):
    self.aspect = aspect

    self.look_at(position, target, up)

  def look_at(self, position, target, up):
    forward = (position - target).normalize()
    right = (up % forward).normalize()

    angle = math.acos(up * forward)

    up = (forward % right).normalize()

    self.camera_to_world = spatial.Transform(axis=right, angle=angle, translation=position)

  def position(self):
    return self.camera_to_world.translation()

  def target(self):
    return -self.camera_to_world.z()

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
    world_to_camera = spatial.Matrix4(self.camera_to_world.inverse())
    
    return np.array(world_to_camera.elements, dtype=np.float32)