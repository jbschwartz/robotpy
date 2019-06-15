import math

from robot.spatial.matrix4   import Matrix4
from robot.spatial.transform import Transform
from robot.spatial.vector3   import Vector3

class Camera():
  def __init__(self, position : Vector3, target : Vector3, up = Vector3(0, 0, 1), aspect = 16/9):
    self.aspect = aspect
    self.target = target
    self.start_position = position

    self.calculate_projection(60, 100, 10000, aspect)

    self.distance_to_target = (self.target - self.start_position).length()

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

  def orbit(self, angle_x = 0, angle_z = 0):
    # Move camera to target
    self.camera_to_world *= Transform(translation = Vector3(0, 0, -self.distance_to_target))

    if angle_x != 0:
      # Rotation around camera X
      self.camera_to_world *= Transform(axis = Vector3(1, 0, 0), angle = angle_x)
    if angle_z != 0:
      # Rotation around world Z
      self.camera_to_world = Transform(axis = Vector3(0, 0, 1), angle = angle_z) * self.camera_to_world
    
    # Move target to camera
    self.camera_to_world *= Transform(translation = Vector3(0, 0, self.distance_to_target))

  def zoom(self, amount):
    '''
    Move the camera in or out along its line of sight
    '''
    movement = self.camera_to_world(Vector3(0, 0, amount), type="vector")
    self.camera_to_world = Transform(translation=movement) * self.camera_to_world
    self.distance_to_target = (self.target - self.position).length()

  def reset(self):
    self.look_at(self.start_position, self.target, Vector3(0,0,1))

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