import enum, math

from robot                   import utils
from robot.spatial.transform import Transform
from robot.spatial           import vector3
from robot.visual.projection import OrthoProjection, PerspectiveProjection

Vector3 = vector3.Vector3

class OrbitType(enum.Enum):
  FREE        = enum.auto()
  CONSTRAINED = enum.auto()

class Camera():
  '''
  Camera model responsible for camera positioning and manipulation.
  '''
  def __init__(self, position : Vector3, target : Vector3, up = Vector3(0, 0, 1), projection = PerspectiveProjection()):
    self.projection = projection
    self.target = target
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

  def dolly(self, z):
    '''
    Move the camera in and out along the line of sight (z axis). 
    '''
    self.camera_to_world *= Transform(translation = Vector3(0, 0, z))

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
    
    Scale [0, 1] represents the percentage of the frame used (with 1 being full frame).

    This function is not perfect but performs well overall. There may be some edge cases out there lurking.
    '''

    # Check to see if the camera is in the scene bounding box
    # This function generally doesn't behave well with the camera inside the box
    # This is a bit of a cop-out since there are probably ways to handle those edge cases 
    #   but those are hard to think about... and this works.
    if world_aabb.contains(self.position):
      self.camera_to_world *= Transform(translation = Vector3(0, 0, world_aabb.sphere_radius()))

    # Centering the camera on the world bounding box first helps removes issues caused by 
    # a major point skipping to a different corner as a result of the camera's zoom in movement.
    self.track(*self.world_to_camera(world_aabb.center).xy)

    # Convert world bounding box corners to camera space
    camera_box_points = [self.world_to_camera(corner) for corner in world_aabb.corners]

    # Generate NDCs for a point in coordinate (z = 0, y = 1, z = 2)
    def ndc_coordinate(point, coordinate):
      clip = self.projection.project(point)
      return clip[coordinate] 

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
    def solve_deltas(major, v1, v2, v3, v4, projection_factor):
      '''
      Solve the deltas for all three axis.

      If `major` is vector3.VECTOR_X, the fit occurs on the width of the bounding box.
      If `major` is vector3.VECTOR_Y, the fit occurs on the height of the bounding box.
      `v1` and `v2` are the points along the major axis.
      `v3` and `v4` are the points along hte minor axis.
      '''
      delta_major   = (-projection_factor * v1[major] - v1.z - projection_factor * v2[major] + v2.z) / (2 * projection_factor)
      delta_distance = projection_factor * delta_major + projection_factor * v2[major] - v2.z

      minor = vector3.VECTOR_X if major == vector3.VECTOR_Y else vector3.VECTOR_Y

      delta_minor = (-v4.z * v3[minor] - v3.z * v4[minor]) / (v3.z + v4.z)

      return (delta_major, delta_minor, delta_distance)

    x_min = sorted_points[vector3.VECTOR_X][-1]
    x_max = sorted_points[vector3.VECTOR_X][0]
    y_min = sorted_points[vector3.VECTOR_Y][-1]
    y_max = sorted_points[vector3.VECTOR_Y][0]

    if sizes[vector3.VECTOR_Y] > sizes[vector3.VECTOR_X]:
      # Height is the constraint: Y is the major axis
      if isinstance(self.projection, PerspectiveProjection): 
        projection_factor = self.projection.matrix.elements[5] / scale
        delta_y, delta_x, delta_z = solve_deltas(vector3.VECTOR_Y, y_max, y_min, x_max, x_min, projection_factor)
      elif isinstance(self.projection, OrthoProjection):
        delta_x = -(x_max.x + x_min.x) / 2
        delta_y = -(y_max.y + y_min.y) / 2
        delta_z = 0

        self.projection.height = (y_max.y - y_min.y)
    else:
      # Width is the constraint: X is the major axis
      if isinstance(self.projection, PerspectiveProjection): 
        projection_factor = self.projection.matrix.elements[0] / scale
        delta_x, delta_y, delta_z = solve_deltas(vector3.VECTOR_X, x_max, x_min, y_max, y_min, projection_factor)
      elif isinstance(self.projection, OrthoProjection):
        delta_x = -(x_max.x + x_min.x) / 2
        delta_y = -(y_max.y + y_min.y) / 2
        delta_z = 0

        self.projection.width = (x_max.x - x_min.x)

    # Move the camera, remembering to adjust for the box being shifted off center
    self.camera_to_world *= Transform(translation = Vector3(-delta_x, -delta_y, -delta_z))
    # Set the camera target to the center of the scene without changing it's direction
    self.target = self.camera_to_world(Vector3(0, 0, self.world_to_camera(world_aabb.center).z))

  def camera_space(self, ndc):
    '''
    Transform a point in NDC to camera space. Place all points on the near clipping plane.
    '''
    # TODO: Verify that this is working correctly (with a test?).

    # Partially unproject the position and normalize
    # Choose the -z direction (so the ray comes out of the camera)
    m11 = self.projection.inverse.elements[0]
    m22 = self.projection.inverse.elements[5]

    return Vector3(m11 * ndc.x, m22 * ndc.y, -self.projection.near_clip)

  @property
  def world_to_camera(self):
    return self.camera_to_world.inverse()