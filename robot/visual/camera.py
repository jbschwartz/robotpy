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
    '''
    Calcuate look-at transformation.

    Uses a geometrically intuitive method with quaternions.
    (instead of a more efficient computation converting from a matrix directly)
    '''

    # FIXME: Broken up vector (e.g.):
    #   camera = Camera(Vector3(375, -1250, 375), Vector3(0, 0, 350), Vector3(0, 0, 1), 1)

    forward = (position - target).normalize()
    right = (up % forward).normalize()

    angle_z = math.acos(up * forward)
    align_z = Transform(axis=right, angle=angle_z)

    intermediate_x = align_z(Vector3(1, 0, 0), type="vector")
    # TODO: Look into ValueError: math domain error for following parameters:
    #   camera = Camera(Vector3(0, -350, 350), Vector3(0, 0, 350), Vector3(0, 0, 1), 1)
    angle_x = math.acos(right * intermediate_x)
    
    # Check which direction we need to rotate by angle_x (dot product tells us how much, but not which way)
    # See if the calculated normal vector is parallel or anti-parallel with the z vector
    calculated_normal = (right % intermediate_x)
    rotation_direction = 1 if calculated_normal * forward > 0 else -1

    align_x = Transform(axis=(rotation_direction * forward), angle=angle_x, translation=position)

    self.camera_to_world = align_x * align_z 

  @property
  def position(self):
    return self.camera_to_world.translation()



  def zoom(self, direction):
    '''
    Move the camera in or out along its line of sight
    '''
    # FIXME: There is an issue with the target
    movement = self.camera_to_world(Vector3(0, 0, self.ZOOM_SPEED * -direction), type="vector")
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