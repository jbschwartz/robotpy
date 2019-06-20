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
  ORBIT_SPEED     = 0.05
  TRACK_SPEED     = 1
  TRACK_SPEED_KEY = 20
  DOLLY_SPEED     = 100
  ROLL_SPEED      = 0.005

  def __init__(self, camera : Camera, scene):
    self.camera = camera
    self.scene = scene
    self.orbit_type = OrbitType.CONSTRAINED

    self.start_position = camera.position
    self.start_target   = camera.target

    self.last_cursor_position = None

    self.window_width  = None
    self.window_height = None

  def click(self, button, action, cursor):
    # EXPERIMENTAL
    #   When we're done orbiting, switch back to constrained mode
    #   But only do so if the camera isn't overly rolled
    if action == glfw.RELEASE:
      # Get projection of the camera's x axis in the world's xy plane
      # Then get the angle (of roll) between the camera's x axis and the projection
      camera_direction_x = self.camera.camera_to_world(Vector3(1, 0, 0), type="vector")
      mutual_perpendicular = vector3.cross(camera_direction_x, Vector3(0, 0, 1))
      vector_in_plane = vector3.cross(Vector3(0, 0, 1), mutual_perpendicular)

      roll_angle = vector3.angle_between(camera_direction_x, vector_in_plane)

      # These thresholds are set empirically
      if roll_angle >= math.radians(15) and roll_angle <= math.radians(165):
        self.orbit_type = OrbitType.FREE
      else:
        self.orbit_type = OrbitType.CONSTRAINED
  
  def drag(self, button, cursor, cursor_delta, modifiers):
    if button == glfw.MOUSE_BUTTON_MIDDLE:
      if modifiers & glfw.MOD_CONTROL:
        self.request_track(cursor_delta.x, -cursor_delta.y)
      elif modifiers & glfw.MOD_ALT:
        self.request_roll(cursor, cursor_delta)
      elif modifiers & glfw.MOD_SHIFT:
        self.request_dolly(3 * cursor_delta.y / self.DOLLY_SPEED)
      else:
        direction = vector3.normalize(cursor_delta)
        self.request_orbit(*direction.yx)
  
  def key(self, key, action, modifiers):
    if key == glfw.KEY_R and action == glfw.RELEASE:
      self.reset()

    if key == glfw.KEY_O and action == glfw.RELEASE:
      self.orbit_type = OrbitType.FREE if self.orbit_type is OrbitType.CONSTRAINED else OrbitType.CONSTRAINED

    if key in [glfw.KEY_RIGHT, glfw.KEY_LEFT, glfw.KEY_UP, glfw.KEY_DOWN]:
      self.arrows(key, action, modifiers)

    if key in [glfw.KEY_1, glfw.KEY_2, glfw.KEY_3, glfw.KEY_4, glfw.KEY_5, glfw.KEY_6, glfw.KEY_7]:
      if modifiers & glfw.MOD_CONTROL and action == glfw.PRESS:
        self.saved_views(key)

  def scroll(self, direction):
    direction.normalize()

    if direction.x:
      self.request_orbit(0, direction.x)
    if direction.y:
      self.request_dolly(direction.y)

  def window_resize(self, width, height):
    self.window_width = width
    self.window_height = height

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
      else:
        self.request_orbit(0, direction[key])
    if key in [glfw.KEY_UP, glfw.KEY_DOWN] and action in [glfw.PRESS, glfw.REPEAT]:
      if modifiers & glfw.MOD_CONTROL:
        self.request_track(0, self.TRACK_SPEED_KEY * direction[key])
      else:
        self.request_orbit(direction[key], 0)

  def request_dolly(self, z):
    self.camera.dolly(self.DOLLY_SPEED * z)

  def request_orbit(self, x, z):
    # EXPERIMENTAL
    #   Check to see if the camera is approaching the "poles"
    #   If it is, turn off constrained orbiting
    camera_direction_z = self.camera.camera_to_world(Vector3(0, 0, -1), type="vector") # In world space
    angle_between_z = vector3.angle_between(camera_direction_z, Vector3(0, 0, 1))

    # These thresholds are set empirically
    if angle_between_z <= math.radians(20) or angle_between_z >= math.radians(160):
      self.orbit_type = OrbitType.FREE

    self.camera.orbit(self.ORBIT_SPEED * x, self.ORBIT_SPEED * z, self.orbit_type)

  def request_track(self, x, y):
    self.camera.track(self.TRACK_SPEED * x, self.TRACK_SPEED * y)

  def request_roll(self, cursor, cursor_delta):
    # Calculate the initial cursor position
    cursor_start_point = cursor - cursor_delta
    # Calculate the radius vector from center screen to initial cursor position
    r = Vector3(cursor_start_point.x - self.window_width / 2, cursor_start_point.y - self.window_height / 2)

    if math.isclose(r.length(), 0):
      return 

    # Calculate the unit tangent vector to the circle at cursor_start_point
    t = Vector3(r.y, -r.x).normalize()
    # The contribution to the roll is the projection of the cursor_delta vector onto the tangent vector
    self.camera.roll(self.ROLL_SPEED * cursor_delta * t)

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
      position = Vector3(750, -750, 750)
    else:
      return

    self.camera.look_at(position, target, up)
    self.camera.fit(self.scene.aabb, 1.1)