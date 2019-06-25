import enum, math, glfw

from robot.spatial         import vector3
from robot.visual.camera   import Camera, OrbitType
from robot.visual.observer import Observer

Vector3 = vector3.Vector3

class SavedView(enum.Enum):
  FRONT  = glfw.KEY_1
  BACK   = glfw.KEY_2
  RIGHT  = glfw.KEY_3
  LEFT   = glfw.KEY_4
  TOP    = glfw.KEY_5
  BOTTOM = glfw.KEY_6
  ISO    = glfw.KEY_7

# TODO: Mouse picking on all actions
# This is what makes most CAD cameras feel very natural (I think)

class CameraController(Observer):
  # TODO: Make a camera control settings class that can be persisted to disk
  ORBIT_SPEED     = 0.05
  TRACK_SPEED     = 1
  TRACK_SPEED_KEY = 20
  DOLLY_SPEED     = 100
  ROLL_SPEED      = 0.005
  ROLL_SPEED_KEY  = 15
  DOLLY_IN        = 1
  FIT_SCALE       = 0.75

  def __init__(self, camera : Camera, scene, window):
    self.camera = camera
    self.scene = scene
    self.window = window
    self.orbit_type = OrbitType.CONSTRAINED

    self.start_position = camera.position
    self.start_target   = camera.target

    self.last_cursor_position = None

  def click(self, button, action, cursor):
    pass
  
  def drag(self, button, cursor, cursor_delta, modifiers):
    if button == glfw.MOUSE_BUTTON_MIDDLE:
      if modifiers & glfw.MOD_CONTROL:
        self.request_track(cursor_delta.x, -cursor_delta.y)
      elif modifiers & glfw.MOD_ALT:
        angle = self.calculate_roll_angle(cursor, cursor_delta)
        self.roll(angle)
      elif modifiers & glfw.MOD_SHIFT:
        self.dolly(Vector3(0, 0, 3 * cursor_delta.y / self.DOLLY_SPEED))
      else:
        # TODO: Maybe do something with speed scaling. 
        # It's hard to orbit slowly and precisely when the orbit speed is set where it needs to be for general purpose orbiting
        # The steps are too large and it looks choppy.
        direction = vector3.normalize(cursor_delta)
        self.request_orbit(*direction.yx)
  
  def key(self, key, action, modifiers):
    if key == glfw.KEY_R and action == glfw.RELEASE:
      self.reset()

    if key == glfw.KEY_F and action == glfw.RELEASE:
      self.camera.fit(self.scene.aabb, self.FIT_SCALE)

    if key == glfw.KEY_O and action == glfw.RELEASE:
      self.orbit_type = OrbitType.FREE if self.orbit_type is OrbitType.CONSTRAINED else OrbitType.CONSTRAINED

    if key in [glfw.KEY_RIGHT, glfw.KEY_LEFT, glfw.KEY_UP, glfw.KEY_DOWN]:
      self.arrows(key, action, modifiers)

    if key in [glfw.KEY_1, glfw.KEY_2, glfw.KEY_3, glfw.KEY_4, glfw.KEY_5, glfw.KEY_6, glfw.KEY_7]:
      if modifiers & glfw.MOD_CONTROL and action == glfw.PRESS:
        self.saved_views(key)

  def scroll(self, horizontal, vertical):
    if horizontal:
      self.request_orbit(0, horizontal)
    if vertical:
      if vertical == self.DOLLY_IN:
        # Dolly in toward the mouse
        self.dolly(self.ray_to_cursor())
      else:
        # And out in the camera's z axis
        self.dolly(Vector3(0, 0, 1))

  def window_resize(self, width, height):
    self.camera.projection.aspect = width / height

  def arrows(self, key, action, modifiers):
    # TODO: This doesn't handle both keys pressed at once
    direction = {
      glfw.KEY_RIGHT: 1,
      glfw.KEY_LEFT: -1,
      glfw.KEY_UP:    1,
      glfw.KEY_DOWN: -1
    }
    
    if key in [glfw.KEY_RIGHT, glfw.KEY_LEFT] and action in [glfw.PRESS, glfw.REPEAT]:
      if modifiers & glfw.MOD_CONTROL:
        self.request_track(self.TRACK_SPEED_KEY * direction[key], 0)
      elif modifiers & glfw.MOD_ALT:
        direction = 1 if key == glfw.KEY_LEFT else -1
        self.roll(self.ROLL_SPEED_KEY * direction)
      else:
        self.request_orbit(0, direction[key])
    if key in [glfw.KEY_UP, glfw.KEY_DOWN] and action in [glfw.PRESS, glfw.REPEAT]:
      if modifiers & glfw.MOD_CONTROL:
        self.request_track(0, self.TRACK_SPEED_KEY * direction[key])
      else:
        self.request_orbit(direction[key], 0)

  def ray_to_cursor(self):
    return self.camera.cast_ray_to(self.window.ndc(self.window.get_cursor()))

  def dolly(self, direction):
    '''
    Move the camera along the provided direction
    '''
    displacement = self.DOLLY_SPEED * direction

    # Get the z value of the back of the scene in camera coordinates
    camera_box = [self.camera.world_to_camera(corner) for corner in self.scene.aabb.corners]
    back_of_scene = min(camera_box, key = lambda point: point.z)

    # If we're zooming out, don't allow the camera to exceed the clipping plane
    if displacement.z > 0 and (displacement.z - back_of_scene.z) > self.camera.projection.far_clip:
      return

    self.camera.dolly(displacement)

    # TODO: Improvement: track the target toward the mouse pick point so that the target approaches
    #   the correct "camera z" value as we zoom in. This requires scene intersection to work properly

    # Translate target laterally with camera
    if displacement.x != 0 or displacement.y != 0:
      # Remove the z component so the target doesn't move in and out of the scene with the camera
      displacement.z = 0

      self.camera.target += self.camera.camera_to_world(displacement, type="vector")

  def request_orbit(self, x, z):
    self.camera.orbit(self.ORBIT_SPEED * x, self.ORBIT_SPEED * z, self.orbit_type)

  def request_track(self, x, y):
    self.camera.track(self.TRACK_SPEED * x, self.TRACK_SPEED * y)

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
    return cursor_delta * t

  def roll(self, amount):
    self.camera.roll(self.ROLL_SPEED * amount)

  def reset(self):
    self.camera.look_at(self.start_position, self.start_target, Vector3(0, 0, 1))

  def saved_views(self, key):
    radius = 1250
    z_height = 500
    target = Vector3(0, 0, z_height)
    up = Vector3(0, 0, 1)

    if key is SavedView.TOP.value:
      position = Vector3(0, 0, radius)
      up = Vector3(0, 1, 0)
    elif key is SavedView.BOTTOM.value:
      position = Vector3(0, 0, -radius)
      up = Vector3(0, -1, 0)
    elif key is SavedView.LEFT.value:
      position = Vector3(-radius, 0, z_height)
    elif key is SavedView.RIGHT.value:
      position = Vector3(radius, 0, z_height)
    elif key is SavedView.FRONT.value:
      position = Vector3(0, -radius, z_height)
    elif key is SavedView.BACK.value:
      position = Vector3(0, radius, z_height)
    elif key is SavedView.ISO.value:
      position = Vector3(750, -750, 1250)
    else:
      return

    self.camera.look_at(position, target, up)
    self.camera.fit(self.scene.aabb, self.FIT_SCALE)