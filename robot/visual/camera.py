import enum, math

from robot                   import utils
from robot.spatial.matrix4   import Matrix4
from robot.spatial.transform import Transform
from robot.spatial           import vector3

Vector3 = vector3.Vector3

class OrbitType(enum.Enum):
  FREE        = enum.auto()
  CONSTRAINED = enum.auto()

class Camera():
  '''
  Camera model responsible for camera positioning and manipulation.
  '''
  def __init__(self, position : Vector3, target : Vector3, up = Vector3(0, 0, 1), aspect = 16/9):
    self._fov = math.radians(60)
    self._aspect = aspect
    self.near_clip = 100
    self.far_clip = 10000
    self.target = target

    self.calculate_projection()

    self.look_at(position, target, up)

  @property
  def fov(self):
    '''
    Get the vertical field of view of the camera
    '''
    return self._fov

  @fov.setter
  def fov(self, fov):
    self._fov = fov
    self.calculate_projection()

  @property
  def aspect(self):
    return self._aspect
  
  @aspect.setter
  def aspect(self, aspect):
    self._aspect = aspect
    self.calculate_projection()

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

    dot = right * intermediate_x
    angle_x = utils.safe_acos(dot)
    
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

  @property
  def position(self):
    return self.camera_to_world.translation()

  @property
  def distance_to_target(self):
    return (self.target - self.position).length()

  def orbit(self, pitch = 0, yaw = 0, orbit_type : OrbitType = OrbitType.FREE):
    '''
    Orbits the camera around the target point (with pitch and yaw)
    '''

    # Move target to the origin
    self.camera_to_world = Transform(translation = -self.target) * self.camera_to_world

    if pitch != 0:
      # Rotation around camera x axis in world coordinates
      pitch_axis = self.camera_to_world(Vector3(1, 0, 0), type="vector")
      self.camera_to_world = Transform(axis = pitch_axis, angle = pitch) * self.camera_to_world
    if yaw != 0:
      if orbit_type is OrbitType.FREE:
        # Rotation around camera y axis in world coordinates
        yaw_axis = self.camera_to_world(Vector3(0, 1, 0), type="vector")
      elif orbit_type is OrbitType.CONSTRAINED:
        # Rotation around world z axis
        yaw_axis = Vector3(0, 0, 1)

      self.camera_to_world = Transform(axis = yaw_axis, angle = yaw) * self.camera_to_world

    # Move target back to position
    self.camera_to_world = Transform(translation = self.target) * self.camera_to_world

  def dolly(self, displacement):
    # TODO: Update this comment
    '''
    Move the camera in or out along its line of sight (z axis) while tracking as necessary

    For example, the controller may request the camera track toward the mouse location in world space.
    We tend to put the mouse where we're interested in dollying so this is useful.
    '''
    # TODO: Restrict the amount of dollying so that the camera cannot pass through the target
    self.camera_to_world *= Transform(translation = displacement)

  def track(self, x, y):
    '''
    Move the camera vertically and horizontally (with respect to camera coordinate frame)
    '''
    camera_displacement_in_world = self.camera_to_world(Vector3(x, y), type="vector")

    self.target += camera_displacement_in_world

    self.camera_to_world = Transform(translation = camera_displacement_in_world) * self.camera_to_world

  def roll(self, angle):
    self.camera_to_world *= Transform(axis = Vector3(0, 0, 1), angle = angle)

  def fit(self, world_aabb, scale = 1):
    '''
    Dolly and track the camera to fit the provided bounding box in world space. 
    Update the target to the center of the bounding box.
    
    Scale [0, 1] represents the percentage of the frame used (with 1 being full frame)
    '''
    # TODO: This is a work in progress. Some edge cases remain.

    # Convert world bounding box corners to camera space
    camera_box_points = [self.world_to_camera(corner) for corner in world_aabb.corners]

    # Generate NDCs for a point in coordinate (z = 0, y = 1, z = 2)
    def ndc_coordinate(point, coordinate):
      clip = self.project(point)
      return clip[coordinate] / -point.z 

    sorted_points = {}
    sizes = {}
    for coord in [vector3.VECTOR_X, vector3.VECTOR_Y]:
      # Find the points that create the largest width or height in NDC space
      sorted_points[coord] = sorted(camera_box_points, key = lambda point: -ndc_coordinate(point, coord))
      # Calculate the distance between the two extreme points vertically and horizontally
      sizes[coord] = ndc_coordinate(sorted_points[coord][0], coord) - ndc_coordinate(sorted_points[coord][-1], coord)

    # We now want to make the NDC coordinates of the two extreme point (in x or y) equal to 1 and -1 
    # This will mean the bounding box is as big as we can make it on screen without clipping it
    #
    # To do this, both points are shifted equally to center them on the screen. Then both points are made to 1 and -1 by adjusting z 
    # (since NDC.x = x / z and NDC.y = y / z).
    #
    # For the case of y being the limiting direction (but it is analogous for x) we use a system of equations:
    # Two equations and two unknowns (delta_y, delta_z), taken from the projection matrix:
    #   aspect * (y_1 + delta_y) / (z_1 + delta_z) = -1
    #   aspect * (y_2 + delta_y) / (z_2 + delta_z) =  1
    # 
    # Note the coordinates (y and z) are given in camera space
    def solve_deltas(major, v1, v2, v3, v4, fov_factor):
      '''
      Solve the deltas for all three axis.

      If `major` is vector3.VECTOR_X, the fit occurs on the width of the bounding box.
      If `major` is vector3.VECTOR_Y, the fit occurs on the height of the bounding box.
      `v1` and `v2` are the points along the major axis.
      `v3` and `v4` are the points along hte minor axis.
      '''
      delta_major   = (-fov_factor * v1[major] - v1.z - fov_factor * v2[major] + v2.z) / (2 * fov_factor)
      delta_distance = fov_factor * delta_major + fov_factor * v2[major] - v2.z

      minor = vector3.VECTOR_X if major == vector3.VECTOR_Y else vector3.VECTOR_Y

      minor_width = (v3[minor] - v4[minor]) / 2
      delta_minor = minor_width - v3[minor]

      return (delta_major, delta_minor, delta_distance)

    x_min = sorted_points[vector3.VECTOR_X][-1]
    x_max = sorted_points[vector3.VECTOR_X][0]
    y_min = sorted_points[vector3.VECTOR_Y][-1]
    y_max = sorted_points[vector3.VECTOR_Y][0]

    if sizes[vector3.VECTOR_Y] > sizes[vector3.VECTOR_X]:
      # Height is the constraint: Y is the major axis
      fov_factor = self.projection.elements[5] / scale
      delta_y, delta_x, delta_z = solve_deltas(vector3.VECTOR_Y, y_max, y_min, x_max, x_min, fov_factor)
    else:
      # Width is the constraint: X is the major axis
      fov_factor = self.projection.elements[0] / scale
      delta_x, delta_y, delta_z = solve_deltas(vector3.VECTOR_X, x_max, x_min, y_max, y_min, fov_factor)

    # Move the camera, remembering to adjust for the box being shifted off center
    self.camera_to_world *= Transform(translation = Vector3(-delta_x, -delta_y, -delta_z))
    # Set the camera target to the center of the scene without changing it's direction
    self.target = self.camera_to_world(Vector3(0, 0, self.world_to_camera(world_aabb.center).z))

  def cast_ray_to(self, ndc):
    '''
    Cast a ray from the camera through the provided ndc coordinates and return in eye coordinates
    '''
    # TODO: Verify that this is working correctly (with a test?).

    # Manually unproject the ray and normalize
    # Choose the -z direction (so the ray comes out of the camera)

    # TODO: Maybe factor the projection out into a Projection class as this (as well as other things) will be different with orthographic projection.
    #    For example, camera dollying is worthless in orthographic projection. There is no concept of distance as objects are the same size at all distances

    m11 = self.inverse_projection.elements[0]
    m22 = self.inverse_projection.elements[5]

    return Vector3(m11 * ndc.x, m22 * ndc.y, -1).normalize()

  def calculate_projection(self):
    f = 1.0 / math.tan(self.fov / 2.0)
    z_width = self.far_clip - self.near_clip

    m11 = f / self.aspect
    m22 = f
    m33 = (self.far_clip + self.near_clip) / (-z_width)
    m34 = 2 * self.far_clip * self.near_clip / (-z_width)

    # Remember: the elements of the matrix look transposed 
    self.projection = Matrix4([m11,  0.0,  0.0,  0.0, 
                               0.0,  m22,  0.0,  0.0, 
                               0.0,  0.0,  m33, -1.0, 
                               0.0,  0.0,  m34,  0.0])

    self.calculate_inverse_projection()

  def project(self, v):
    m11 = self.projection.elements[0]
    m22 = self.projection.elements[5]
    m33 = self.projection.elements[10]
    m34 = self.projection.elements[14]

    return Vector3(m11 * v.x, m22 * v.y, m33 * v.z + m34)

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