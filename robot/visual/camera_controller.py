import enum, json, math, glfw

from robot.common        import Timer
from robot.spatial       import AABB, Ray, Transform, vector3
from .camera             import Camera, OrbitType
from .messaging.listener import listen, listener
from .messaging.event    import Event
from .projection         import OrthoProjection, PerspectiveProjection

Vector3 = vector3.Vector3

# TODO: Mouse picking on all actions
# This is what makes most CAD cameras feel very natural (I think)

class CameraSettings():
  class Defaults(enum.Enum):
    FILE_PATH    = './robot/settings.json'
    ORBIT_SPEED  = 0.05
    ROLL_SPEED   = 0.005
    SCALE_SPEED  = 5
    ORBIT_STEP   = math.radians(5)
    ROLL_STEP    = math.radians(5)
    SCALE_STEP   = 100
    TRACK_STEP   = 20
    SCALE_IN     = 1
    FIT_SCALE    = 0.75

  def __init__(self, path = Defaults.FILE_PATH.value):
    self.get_settings(path)

    self.needs_write = {}

  def __getattr__(self, attribute):
    if attribute == 'needs_write':
      self.needs_write = {}
      return self.needs_write

    return getattr(self.Defaults, str.upper(attribute)).value

  def __setattr__(self, attribute, value):
    self.__dict__[attribute] = value
    if attribute != 'needs_write':
      self.needs_write[attribute] = value

  def get_settings(self, path):
    settings = self.load(path)
    for name, value in settings['camera'].items():
      setattr(self, str.upper(name), value)

  def load(self, path):
    with open(path) as f:
      return json.load(f)

  def write(self, path = Defaults.FILE_PATH.value):
    settings = self.load(path)
    with open(path, 'w') as f:
      for name, value in self.needs_write.items():
        settings['camera'][name] = value
      json.dump(settings, f, indent=2)

@listener
class CameraController():
  VIEWS = {
    'view_top':    { 'position': Vector3(0, 0,  1250), 'up': Vector3(0,  1, 0) },
    'view_bottom': { 'position': Vector3(0, 0, -1250), 'up': Vector3(0, -1, 0) },
    'view_left':   { 'position': Vector3(-1250, 0, 500) },
    'view_right':  { 'position': Vector3( 1250, 0, 500) },
    'view_front':  { 'position': Vector3(0, -1250, 500) },
    'view_back':   { 'position': Vector3(0,  1250, 500) },
    'view_iso':    { 'position': Vector3(750, -750, 1250) },
  }

  def __init__(self, camera : Camera, settings, bindings, scene, window):
    self.camera = camera
    self.settings = settings
    self.bindings = bindings
    self.scene = scene
    self.window = window
    self.target = self.scene.aabb.center
    self.is_selecting = None
    self.orbit_type = OrbitType.CONSTRAINED

  @listen(Event.CLICK)
  def click(self, button, action, cursor):
    if button == glfw.MOUSE_BUTTON_LEFT:
      if action == glfw.PRESS:
        self.is_selecting = self.window.ndc(cursor)
      else:
        end = self.window.ndc(cursor)
        self.is_selecting = None

    if button == glfw.MOUSE_BUTTON_MIDDLE and action == glfw.PRESS:
      r = self.camera.cast_ray(self.window.ndc(cursor))
      with Timer('Ray Intersection') as tim:
        t = self.scene.intersect(r)

      if t is not None:
        self.target = r.evaluate(t)
      else:
        self.target = self.scene.aabb.center

      self.camera.target = self.target

  @listen(Event.DRAG)
  def drag(self, button, cursor, cursor_delta, modifiers):
    command = self.bindings.get_command((modifiers, button))

    if command == 'track':
      self.track_cursor(cursor, cursor_delta)
    elif command == 'roll':
      angle = self.calculate_roll_angle(cursor, cursor_delta)
      self.camera.roll(angle)
    elif command == 'scale':
      self.try_scale(self.settings.SCALE_SPEED * cursor_delta.y)
    elif command == 'orbit':
      # TODO: Maybe do something with speed scaling.
      # It's hard to orbit slowly and precisely when the orbit speed is set where it needs to be for general purpose orbiting
      # The steps are too large and it looks choppy.
      angle = self.settings.ORBIT_SPEED * vector3.normalize(cursor_delta)
      self.camera.orbit(self.target, angle.y, angle.x, self.orbit_type)

  @listen(Event.KEY)
  def key(self, key, action, modifiers):
    if action == glfw.PRESS:
      return

    command = self.bindings.get_command((modifiers, key))

    if command == 'fit':
      self.camera.fit(self.scene.aabb, self.settings.FIT_SCALE)
    elif command == 'orbit_toggle':
      self.orbit_type = OrbitType.FREE if self.orbit_type is OrbitType.CONSTRAINED else OrbitType.CONSTRAINED
    elif command == 'projection_toggle':
      self.toggle_projection()
    elif command == 'normal_to':
      self.normal_to()

    elif command == 'track_left':
      self.camera.track(-self.settings.TRACK_STEP, 0)
    elif command == 'track_right':
      self.camera.track(self.settings.TRACK_STEP, 0)
    elif command == 'track_up':
      self.camera.track(0, self.settings.TRACK_STEP)
    elif command == 'track_down':
      self.camera.track(0, -self.settings.TRACK_STEP)

    elif command == 'orbit_left':
      self.camera.orbit(self.target, 0, -self.settings.ORBIT_STEP, self.orbit_type)
    elif command == 'orbit_right':
      self.camera.orbit(self.target, 0, self.settings.ORBIT_STEP, self.orbit_type)
    elif command == 'orbit_up':
      self.camera.orbit(self.target, -self.settings.ORBIT_STEP, 0, self.orbit_type)
    elif command == 'orbit_down':
      self.camera.orbit(self.target, self.settings.ORBIT_STEP, 0, self.orbit_type)

    elif command == 'roll_cw':
      self.camera.roll(-self.settings.ROLL_STEP)
    elif command == 'roll_ccw':
      self.camera.roll(self.settings.ROLL_STEP)

    elif command == 'zoom_in':
      self.try_scale(-self.settings.SCALE_STEP)
    elif command == 'zoom_out':
      self.try_scale(self.settings.SCALE_STEP)

    elif command in ['view_front', 'view_back', 'view_right', 'view_left', 'view_top', 'view_bottom', 'view_iso']:
      self.view(command)

  @listen(Event.SCROLL)
  def scroll(self, horizontal, vertical):
    if horizontal:
      self.camera.orbit(self.target, 0, self.settings.ORBIT_STEP * horizontal, self.orbit_type)
    if vertical:
      self.scale_to_cursor(self.window.get_cursor(), vertical * self.settings.SCALE_IN)

  @listen(Event.WINDOW_RESIZE)
  def window_resize(self, width, height):
    if not math.isclose(height, 0):
      self.camera.projection.aspect = width / height

  def normal_to(self):
    minimum = math.radians(180)
    direction = Vector3()
    forward = self.camera.camera_to_world(Vector3.Z(), as_type="vector")
    for coordinate in [Vector3.X(), Vector3.Y(), Vector3.Z(), -Vector3.X(), -Vector3.Y(), -Vector3.Z()]:
      angle = vector3.angle_between(coordinate, forward)
      if angle < minimum:
        minimum = angle
        direction = coordinate

    axis = vector3.cross(forward, direction)
    self.camera.camera_to_world = Transform.from_axis_angle_translation(axis = axis, angle = minimum) * self.camera.camera_to_world

    right = self.camera.camera_to_world(Vector3.X(), as_type="vector")

    first_direction = direction
    minimum = math.radians(180)
    for coordinate in [Vector3.X(), Vector3.Y(), Vector3.Z()]:
      if first_direction == coordinate:
        continue

      angle = vector3.angle_between(coordinate, right)
      if angle < minimum:
        minimum = angle
        direction = coordinate

    axis = vector3.cross(right, direction)
    self.camera.camera_to_world = Transform.from_axis_angle_translation(axis = axis, angle = minimum) * self.camera.camera_to_world

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
      point = self.camera.world_to_camera(self.scene.aabb.center, as_type="point")
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
      current = self.camera.world_to_camera(self.scene.aabb.center, as_type="point")

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

    # TODO: Move this calculation out to mouse_down event handler.
    # This does not need to be called per mouse_drag event handler-- It's ruining frame rate.
    if isinstance(self.camera.projection, PerspectiveProjection):
      # This approximates the scene moving the same speed as the cursor but it isn't exactly correct for perspective projection.
      # I think perspective projection requires mouse picking to determine the correct z.
      transformed_aabb = AABB.from_points([
        point.transform(self.camera.world_to_camera, as_type="point")
        for point in self.scene.aabb.corners
      ])

      delta *= -transformed_aabb.center.z

    self.camera.track(v = -delta)

  def scale_to_cursor(self, cursor, direction):
    ndc = self.window.ndc(cursor)

    cursor_camera_point = self.camera.camera_space(ndc)

    # This is delta z for perspective and delta width for orthographic
    delta_scale = direction * self.settings.SCALE_STEP
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
    return self.settings.ROLL_SPEED * cursor_delta * t

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
      view.get('up', Vector3.Z())
    )
    self.camera.fit(self.scene.aabb, self.settings.FIT_SCALE)