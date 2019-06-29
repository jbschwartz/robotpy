import math, glfw

from robot.spatial           import vector3
from robot.visual.camera     import Camera, OrbitType
from robot.visual.observer   import Observer
from robot.visual.projection import OrthoProjection, PerspectiveProjection

Vector3 = vector3.Vector3

# TODO: Mouse picking on all actions
# This is what makes most CAD cameras feel very natural (I think)

class CameraController(Observer):
  # TODO: Make a camera control settings class that can be persisted to disk
  ORBIT_SPEED  = 0.05
  TRACK_SPEED  = 1
  ROLL_SPEED   = 0.005
  SCALE_SPEED  = 5
  ROLL_STEP    = math.radians(5)
  SCALE_STEP   = 100
  TRACK_STEP   = 20
  DOLLY_IN     = 1
  FIT_SCALE    = 0.75

  def __init__(self, camera : Camera, bindings, scene, window):
    self.camera = camera
    self.bindings = bindings
    self.scene = scene
    self.window = window
    self.orbit_type = OrbitType.CONSTRAINED

  def click(self, button, action, cursor):
    pass
  
  def drag(self, button, cursor, cursor_delta, modifiers):
    command = self.bindings.get_command((modifiers, button))

    if command == 'track':
      self.track_cursor(cursor, cursor_delta)
    elif command == 'roll':
      angle = self.calculate_roll_angle(cursor, cursor_delta)
      self.camera.roll(angle)
    elif command == 'scale':
      self.scale(self.SCALE_SPEED * cursor_delta.y)
    elif command == 'orbit':
      # TODO: Maybe do something with speed scaling. 
      # It's hard to orbit slowly and precisely when the orbit speed is set where it needs to be for general purpose orbiting
      # The steps are too large and it looks choppy.
      angle = self.ORBIT_SPEED * vector3.normalize(cursor_delta)
      self.camera.orbit(angle.y, angle.x, self.orbit_type)

  def key(self, key, action, modifiers):
    if action == glfw.PRESS:
      return

    command = self.bindings.get_command((modifiers, key))

    if command == 'fit':
      self.camera.fit(self.scene.aabb, self.FIT_SCALE)
    elif command == 'orbit_toggle':
      self.orbit_type = OrbitType.FREE if self.orbit_type is OrbitType.CONSTRAINED else OrbitType.CONSTRAINED
    elif command == 'projection_toggle':
      self.toggle_projection()

    elif command == 'track_left':
      self.camera.track(-self.TRACK_STEP, 0)
    elif command == 'track_right':
      self.camera.track(self.TRACK_STEP, 0)
    elif command == 'track_up':
      self.camera.track(0, self.TRACK_STEP)
    elif command == 'track_down':
      self.camera.track(0, -self.TRACK_STEP)

    elif command == 'roll_cw':
      self.camera.roll(-self.ROLL_STEP)
    elif command == 'roll_ccw':
      self.camera.roll(self.ROLL_STEP)

    elif command == 'zoom_in':
      self.scale(-self.SCALE_STEP)
    elif command == 'zoom_out':
      self.scale(self.SCALE_STEP)

    elif command in ['view_front', 'view_back', 'view_right', 'view_left', 'view_top', 'view_bottom', 'view_iso']:
      self.saved_view(command)

  def scroll(self, horizontal, vertical):
    if horizontal:
      self.camera.orbit(0, self.ORBIT_SPEED * horizontal)
    if vertical:
      self.scale(self.SCALE_STEP * vertical)

  def window_resize(self, width, height):
    self.camera.projection.aspect = width / height

  def cursor_to_camera(self):
    return self.camera.camera_space(self.window.ndc(self.window.get_cursor()))

  def toggle_projection(self):
    '''
    Switch the camera projection while maintaining "scale".

    That is, we try to make ndc_perspective = ndc_orthographic at the scene's center point.
    We use the x coordinate and obtain: m11 * camera_x / - camera_z = 2 / width * camera_x 
      With m11 being the first element in the perspective projection matrix.
    '''
    params = {
      'aspect': self.camera.projection.aspect,
      'near_clip': self.camera.projection.near_clip,
      'far_clip': self.camera.projection.far_clip
    }

    if isinstance(self.camera.projection, PerspectiveProjection):
      point = self.camera.world_to_camera(self.scene.aabb.center, type="point")
      # Calculate the width from the above relation
      params['width'] = -2 * point.z / self.camera.projection.matrix.elements[0]

      self.camera.projection = OrthoProjection(**params)
    else:
      width = self.camera.projection.width

      self.camera.projection = PerspectiveProjection(**params)
      current = self.camera.world_to_camera(self.scene.aabb.center, type="point")
      
      # Calculate the z camera position from the above relation
      desired = - self.camera.projection.matrix.elements[0] * width / 2

      self.camera.dolly(self.clamp_dolly(current.z - desired))

  def clamp_dolly(self, displacement):
    '''
    Check to see if dollying will begin clipping the scene. If so, don't dolly.
    '''
    # Get the z value of the back of the scene in camera coordinates
    camera_box = [self.camera.world_to_camera(corner) for corner in self.scene.aabb.corners]
    back_of_scene = min(camera_box, key = lambda point: point.z)

    # If we're dollying out, don't allow the camera to exceed the clipping plane
    if displacement > 0 and (displacement - back_of_scene.z) > self.camera.projection.far_clip:
      return 0
    else:
      return displacement 

  def track_cursor(self, cursor, cursor_delta):
    '''
    Move the camera with the cursor.

    That is, calculate the distance in cursor distance in NDC and convert that to camera motion.
    '''
    delta_ndc = self.window.ndc(cursor) - self.window.ndc(cursor + cursor_delta)

    delta_x = delta_ndc.x / self.camera.projection.matrix.elements[0]
    delta_y = delta_ndc.y / self.camera.projection.matrix.elements[5]

    if isinstance(self.camera.projection, PerspectiveProjection):
      # This approximates the scene moving the same speed as the cursor but it isn't exactly correct for perspective projection.
      # I think perspective projection requires mouse picking to determine the correct z.
      z = -self.camera.world_to_camera(self.scene.aabb).center.z

      delta_x *= z
      delta_y *= z

    self.camera.track(-delta_x, -delta_y)

  def calculate_roll_angle(self, cursor, cursor_delta):
    # Calculate the initial cursor position
    cursor_start_point = cursor - cursor_delta
    # Calculate the radius vector from center screen to initial cursor position
    r = Vector3(cursor_start_point.x - self.window.width / 2, cursor_start_point.y - self.window.height / 2)

    if math.isclose(r.length(), 0):
      return 

    # Calculate the unit tangent vector to the circle at cursor_start_point
    t = Vector3(r.y, -r.x).normalize()
    # The contribution to the roll is the projection of the cursor_delta vector onto the tangent vector
    return self.ROLL_SPEED * cursor_delta * t

  def scale(self, amount):
    if isinstance(self.camera.projection, PerspectiveProjection):
      delta_z = self.clamp_dolly(amount)
      self.camera.dolly(delta_z)
    else:
      self.camera.projection.zoom(amount)

  def saved_view(self, view):
    radius = 1250
    z_height = 500
    target = Vector3(0, 0, z_height)
    up = Vector3(0, 0, 1)

    if view == 'view_top':
      position = Vector3(0, 0, radius)
      up = Vector3(0, 1, 0)
    elif view == 'view_bottom':
      position = Vector3(0, 0, -radius)
      up = Vector3(0, -1, 0)
    elif view == 'view_left':
      position = Vector3(-radius, 0, z_height)
    elif view == 'view_right':
      position = Vector3(radius, 0, z_height)
    elif view == 'view_front':
      position = Vector3(0, -radius, z_height)
    elif view == 'view_back':
      position = Vector3(0, radius, z_height)
    elif view == 'view_iso':
      position = Vector3(750, -750, 1250)
    else:
      return

    self.camera.look_at(position, target, up)
    self.camera.fit(self.scene.aabb, self.FIT_SCALE)