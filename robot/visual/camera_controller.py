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

  VIEWS = {
    'view_top':    { 'position': Vector3(0, 0,  1250), 'up': Vector3(0,  1, 0) },
    'view_bottom': { 'position': Vector3(0, 0, -1250), 'up': Vector3(0, -1, 0) },
    'view_left':   { 'position': Vector3(-1250, 0, 500) },
    'view_right':  { 'position': Vector3( 1250, 0, 500) },
    'view_front':  { 'position': Vector3(0, -1250, 500) },
    'view_back':   { 'position': Vector3(0,  1250, 500) },
    'view_iso':    { 'position': Vector3(750, -750, 1250) },
  }

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
      self.try_scale(self.SCALE_SPEED * cursor_delta.y)
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
      self.try_scale(-self.SCALE_STEP)
    elif command == 'zoom_out':
      self.try_scale(self.SCALE_STEP)

    elif command in ['view_front', 'view_back', 'view_right', 'view_left', 'view_top', 'view_bottom', 'view_iso']:
      self.view(command)

  def scroll(self, horizontal, vertical):
    if horizontal:
      self.camera.orbit(0, self.ORBIT_SPEED * horizontal)
    if vertical:
      self.scale_to_cursor(self.window.get_cursor(), vertical)

  def window_resize(self, width, height):
    self.camera.projection.aspect = width / height

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

      # If the camera is inside the scene, conservatively move it outside (as otherwise there is no way to as an orthogonal camera)
      # This can happen if the user brings the perspective camera inside the scene and then switches to orthogonal
      if self.scene.aabb.contains(self.camera.position):
        # This could cause clipping issues if the size of the scene is large
        # This could be circumvented by a more precise calculation of the distance to the edge of the scene
        self.camera.dolly(2 * self.scene.aabb.sphere_radius()) 
    else:
      width = self.camera.projection.width

      self.camera.projection = PerspectiveProjection(**params)
      current = self.camera.world_to_camera(self.scene.aabb.center, type="point")

      # Calculate the z camera position from the above relation
      desired = - self.camera.projection.matrix.elements[0] * width / 2
      delta = current.z - desired

      if not self.dolly_will_clip(delta):
        self.camera.dolly(delta)

  def dolly_will_clip(self, displacement):
    '''
    Check to see if dollying will begin clipping the scene.
    '''
    # Get the z value of the back of the scene in camera coordinates
    camera_box_points = self.camera.world_to_camera(self.scene.aabb.corners)
    back_of_scene = min(camera_box_points, key = lambda point: point.z)

    # If we're dollying out, don't allow the camera to exceed the clipping plane
    if displacement > 0 and (displacement - back_of_scene.z) > self.camera.projection.far_clip:
      return True

    return False

  def track_cursor(self, cursor, cursor_delta):
    '''
    Move the camera with the cursor.

    That is, calculate the distance in cursor distance in NDC and convert that to camera motion.
    '''
    delta_ndc = self.window.ndc(cursor) - self.window.ndc(cursor + cursor_delta)

    delta = self.camera.camera_space(delta_ndc)

    if isinstance(self.camera.projection, PerspectiveProjection):
      # This approximates the scene moving the same speed as the cursor but it isn't exactly correct for perspective projection.
      # I think perspective projection requires mouse picking to determine the correct z.
      delta *= -self.camera.world_to_camera(self.scene.aabb).center.z

    self.camera.track(v = -delta)

  def scale_to_cursor(self, cursor, direction):
    ndc = self.window.ndc(cursor)

    cursor_camera_point = self.camera.camera_space(ndc)

    # This is delta z for perspective and delta width for orthographic
    delta_scale = direction * self.SCALE_STEP
    delta_camera = -cursor_camera_point * delta_scale

    if isinstance(self.camera.projection, OrthoProjection):
      delta_camera /= self.camera.projection.width

    was_scaled = self.try_scale(delta_scale)

    if was_scaled:
      self.camera.track(delta_camera.x, delta_camera.y)

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

  def try_scale(self, amount):
    '''
    Attempt to scale the scene.

    Scaling is prevented if it causes clipping in the scene. Return True for successful scaling. Return False if no scaling occurs.
    '''
    if isinstance(self.camera.projection, PerspectiveProjection):
      if self.dolly_will_clip(amount):
        return False

      self.camera.dolly(amount)
    else:
      at_minimum = self.camera.projection.width <= self.camera.projection.WIDTH_MIN
      at_maximum = self.camera.projection.width >= self.camera.projection.WIDTH_MAX
      
      if (at_minimum and amount < 0) or (at_maximum and amount > 0):
        return False
      
      self.camera.projection.zoom(amount)
    
    return True

  def view(self, view_name):
    view = self.VIEWS[view_name]

    self.camera.look_at(
      view['position'],
      view.get('target', Vector3(0, 0, 500)),
      view.get('up', Vector3(0, 0, 1))
    )
    self.camera.fit(self.scene.aabb, self.FIT_SCALE)