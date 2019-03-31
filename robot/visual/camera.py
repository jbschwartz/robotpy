import math

from .observer import Observer

import robot.spatial as spatial

Vector3 = spatial.vector3.Vector3
Matrix4 = spatial.matrix4.Matrix4

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

  @property
  def position(self):
    return self.camera_to_world.translation()

  def target(self):
    return -self.camera_to_world.z()

  def orbit(self, direction, center = None):
    if not center:
      center = self.target

    if direction.x > 0:
      theta = +1
    elif direction.x < 0:
      theta = -1
    else:
      theta = 0

    if direction.y > 0:
      phi = 1
    elif direction.y < 0:
      phi = -1
    else:
      phi = 0

    # axis = self.camera_to_world(Vector3(0,0,1), type="vector")
    # axis = Vector3(0,0,1)
    # rotate_z = spatial.Transform(axis=axis, angle=math.radians(theta))
    # rotate_x = spatial.Transform(axis=spatial.Vector3(0,1,0), angle=math.radians(phi))

    # position = -self.camera_to_world.translation()

    # print(spatial.Frame(self.camera_to_world).position())


    # # self.camera_to_world = spatial.Transform(translation=position) * self.camera_to_world
    # self.camera_to_world = rotate_z * self.camera_to_world
    # self.camera_to_world = rotate_x * self.camera_to_world
    # self.camera_to_world = spatial.Transform(axis=axis, angle=math.radians(theta)) * self.camera_to_world
    # self.camera_to_world = spatial.Transform(translation=-position) * self.camera_to_world

    # print(spatial.Frame(self.camera_to_world).orientation())

    # # ... TODO: Movement along the surface of a sphere

    # forward = self.position - self.target
    # radius = forward.length()

    # x = radius * math.cos(math.radians(self.theta - 90))
    # y = radius * math.sin(math.radians(self.theta - 90))

    # self.position = Vector3(x, y, 350)

  def zoom(self, direction):
    '''
    Move the camera in or out along its line of sight
    '''
    movement = Vector3(0, 0, self.ZOOM_SPEED * direction)
    self.camera_to_world = spatial.Transform(translation=movement) * self.camera_to_world

  def click(self, x, y):
    pass
    # fov = math.radians(60)
    # f = 1.0/math.tan(fov/2.0)
    # zN, zF = (100, 10000.0)
    # a = self.aspect

    # p = np.array([f/a, 0.0, 0.0,               0.0, 
    #               0.0, f,   0.0,               0.0, 
    #               0.0, 0.0, (zF+zN)/(zN-zF),  -1.0, 
    #               0.0, 0.0, 2.0*zF*zN/(zN-zF), 0.0], np.float32).reshape((4,4), order='C')

    # pinv = inv(np.matrix(p))
    # point = np.array([x, y, 1, 1], dtype=np.float32)
    # result = np.dot(point, pinv)
    # print(result)

    # forward = normalize(self.position - self.target)
    # right = normalize(cross(self.up, forward))
    # up = normalize(cross(forward, right))

    # translate = -Vector3(right * self.position, up * self.position, forward * self.position)

    # c = np.array([[right.x,     up.x,        forward.x,   0.0],
    #                    [right.y,     up.y,        forward.y,   0.0],
    #                    [right.z,     up.z,        forward.z,   0.0], 
    #                    [translate.x, translate.y, translate.z, 1.0]], np.float32)
    # cmat = np.matrix(c)
    # result = np.dot(point, cmat)
    # print(result)

  def projection_matrix(self):
    fov = math.radians(60)
    f = 1.0/math.tan(fov/2.0)
    zN, zF = (100, 10000.0)
    a = self.aspect

    return Matrix4([f/a, 0.0, 0.0,               0.0, 
                    0.0, f,   0.0,               0.0, 
                    0.0, 0.0, (zF+zN)/(zN-zF),  -1.0, 
                    0.0, 0.0, 2.0*zF*zN/(zN-zF), 0.0])

  @property
  def world_to_camera(self):
    return self.camera_to_world.inverse()