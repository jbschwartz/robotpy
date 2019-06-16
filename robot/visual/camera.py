import enum, math

from robot.spatial.matrix4   import Matrix4
from robot.spatial.transform import Transform
from robot.spatial.vector3   import Vector3

class OrbitType(enum.Enum):
  FREE        = enum.auto()
  CONSTRAINED = enum.auto()

class Camera():
  '''
  Camera model responsible for camera positioning and manipulation.
  '''
  def __init__(self, position : Vector3, target : Vector3, up = Vector3(0, 0, 1), aspect = 16/9):
    self.aspect = aspect
    self.target = target

    self.calculate_projection(60, 100, 10000, aspect)

    self.look_at(position, target, up)

  def look_at(self, position, target, up):
    '''
    Calcuate look-at transformation.

    Uses a geometrically intuitive method with quaternions.
    (instead of a more efficient computation converting from a matrix directly)

    Steps:
      1.  Start with the base coordinate frame
      2.  We calculate our desired z axis (called forward)
      3.  We calculate the difference between our existing z axis and desired
      4.  We rotate around our desired x axis (called right) 
          to align our existing z axis with our desired z axis
      5.  In the process, we move our existing x axis out of alignment with our desired x axis into an intermediate
      6.  We aim to rotate around our desired z axis (mostly so we don't move our desired z axis)
          to align our intermediate x axis with the desired x axis
      7.  We calculate the difference between our intermediate x axis and desired
      8.  Note, sometimes the intermediate x axis is already positioned correctly. So we just stop there.
      9.  Otherwise, we need to then calculate which direction to rotate the intermediate x to get to desired.
      10. Rotate around our desired z axis to complete the transformation
    '''

    self.target = target

    forward = (position - target).normalize()       # Step 2
    angle_z = math.acos(Vector3(0, 0, 1) * forward) # Step 3
    
    right = (up % forward).normalize()
    align_z = Transform(axis=right, angle=angle_z)  # Step 4

    intermediate_x = align_z(Vector3(1, 0, 0), type="vector") # Step 5

    try:
      dot = right * intermediate_x
      angle_x = math.acos(dot) # Step 7
    except ValueError:
      # Happens if floating point rounding pushes us beyond acos' domain (e.g. 1.00000002)
      if math.isclose(dot, 1):
        angle_x = math.acos(1)
      elif math.isclose(dot, -1):
        angle_x = math.acos(-1)

    if math.isclose(angle_x, 0):
      # Our intermediate x axis is already where it should be. We do no further rotation.
      align_x = Transform(translation=position) # Step 8
    else:
      # Check which direction we need to rotate by angle_x (dot product tells us how much, but not which way)
      # See if the calculated normal vector is parallel or anti-parallel with the z vector
      calculated_normal = (right % intermediate_x)
      rotation_direction = -1 if calculated_normal * forward > 0 else 1 
      align_x = Transform(axis=(rotation_direction * forward), angle=angle_x, translation=position) # Step 9

    self.camera_to_world = align_x * align_z # Step 10

    self.distance_to_target = (self.target - self.position).length()

  @property
  def position(self):
    return self.camera_to_world.translation()

  def orbit(self, pitch = 0, yaw = 0, orbit_type : OrbitType = OrbitType.FREE):
    '''
    Orbits the camera around the target point (with pitch and yaw)
    '''
    # Move camera to the origin
    self.camera_to_world = Transform(translation = -self.position) * self.camera_to_world 

    if pitch != 0:
      # Rotation around camera x axis (camera tilt)
      self.camera_to_world *= Transform(axis = Vector3(1, 0, 0), angle = pitch)
    if yaw != 0:
      if orbit_type is OrbitType.FREE:
        # Rotation around camera y axis
        self.camera_to_world *= Transform(axis = Vector3(0, 1, 0), angle = yaw)
      elif orbit_type is OrbitType.CONSTRAINED:
        # Rotation around world z axis
        self.camera_to_world = Transform(axis = Vector3(0, 0, 1), angle = yaw) * self.camera_to_world

    # Move target to origin
    self.camera_to_world *= Transform(translation = Vector3(0, 0, self.distance_to_target))

    # Move target back to position
    self.camera_to_world = Transform(translation = self.target) * self.camera_to_world

  def dolly(self, displacement):
    '''
    Move the camera in or out along its line of sight (z axis)
    '''
    self.camera_to_world *= Transform(translation = Vector3(0, 0, displacement))
    self.distance_to_target = (self.target - self.position).length()

  def track(self, x, y):
    '''
    Move the camera vertically and horizontally (with respect to camera coordinate frame)
    '''
    camera_displacement_in_world = self.camera_to_world(Vector3(x, y), type="vector")

    self.target += camera_displacement_in_world

    self.camera_to_world = Transform(translation = camera_displacement_in_world) * self.camera_to_world

  def roll(self, angle):
    self.camera_to_world *= Transform(axis = Vector3(0, 0, 1), angle = angle)

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