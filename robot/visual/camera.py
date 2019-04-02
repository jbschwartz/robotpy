import math

from robot.spatial.matrix4   import Matrix4
from robot.spatial.transform import Transform
from robot.spatial.vector3   import Vector3
from robot.visual.observer   import Observer

class Camera(Observer):
  ZOOM_SPEED = 15

  def __init__(self, position : Vector3, target : Vector3, up = Vector3(0, 0, 1), aspect = 16/9):
    self.aspect = aspect

    self.calculate_projection(60, 100, 10000, aspect)

    self.look_at(position, target, up)

  def look_at(self, position, target, up):
    forward = (position - target).normalize()
    right = (up % forward).normalize()

    angle = math.acos(up * forward)

    up = (forward % right).normalize()

    self.camera_to_world = Transform(axis=right, angle=angle, translation=position)

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
    self.camera_to_world = Transform(translation=movement) * self.camera_to_world

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

  def calculate_projection(self, fov, z_near, z_far, aspect):
    fov = math.radians(fov)
    f = 1.0 / math.tan(fov / 2.0)
    z_width = z_far - z_near

    m11 = f / aspect
    m22 = f
    m33 = (z_far + z_near) / (-z_width)
    m34 = 2 * z_far * z_near / (-z_width)

    # Remember: the elements of the matrix look transposed 
    self.projection = Matrix4([m11,  0.0,  0.0,  0.0, 
                               0.0,  m22,  0.0,  0.0, 
                               0.0,  0.0,  m33, -1.0, 
                               0.0,  0.0,  m34,  0.0])

    self.calculate_inverse_projection()

  def calculate_inverse_projection(self):
    p11 = self.projection.elements[0]
    p22 = self.projection.elements[5]
    p33 = self.projection.elements[10]
    p34 = self.projection.elements[14]

    m11 = 1 / p11
    m22 = 1 / p22
    m43 = 1 / p34 
    m44 = p33 / p34

    # Remember: the elements of the matrix look transposed 
    self.inverse_projection = Matrix4([m11, 0.0,  0.0, 0.0, 
                                       0.0, m22,  0.0, 0.0, 
                                       0.0, 0.0,  0.0, m43, 
                                       0.0, 0.0, -1.0, m44])

  @property
  def world_to_camera(self):
    return self.camera_to_world.inverse()