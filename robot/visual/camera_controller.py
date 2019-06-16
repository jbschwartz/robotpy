import glfw

from robot.spatial         import vector3
from robot.visual.camera   import Camera
from robot.visual.observer import Observer

Vector3 = vector3.Vector3

# TODO: Mouse picking on all actions
# This is what makes most CAD cameras feel very natural (I think)

class CameraController(Observer):
  ORBIT_SPEED     = 0.05
  TRACK_SPEED     = 1
  TRACK_SPEED_KEY = 20
  DOLLY_SPEED     = 100
  ROLL_SPEED      = 0.005

  def __init__(self, camera : Camera):
    self.camera = camera

    self.start_position = camera.position
    self.start_target   = camera.target

    self.last_cursor_position = None

  def click(self, button, cursor):
    pass
  
  def drag(self, button, cursor_delta, modifiers):
    if button == glfw.MOUSE_BUTTON_MIDDLE:
      if modifiers & glfw.MOD_CONTROL:
        self.request_track(cursor_delta.x, -cursor_delta.y)
      elif modifiers & glfw.MOD_ALT:
        # TODO: Fix this so that direction doesn't reverse at the centerline of the screen
        self.request_roll(-cursor_delta.y + cursor_delta.x)
      else:
        direction = vector3.normalize(cursor_delta)
        self.request_orbit(*direction.yx)
  
  def key(self, key, action, modifiers):
    if key == glfw.KEY_R and action == glfw.RELEASE:
      self.reset()

    if key in [glfw.KEY_RIGHT, glfw.KEY_LEFT, glfw.KEY_UP, glfw.KEY_DOWN]:
      self.arrows(key, action, modifiers)

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

  def request_orbit(self, x, z):
    self.camera.orbit(self.ORBIT_SPEED * x, self.ORBIT_SPEED * z)

  def request_track(self, x, y):
    self.camera.track(self.TRACK_SPEED * x, self.TRACK_SPEED * y)

  def request_roll(self, angle):
    self.camera.roll(self.ROLL_SPEED * angle)

  def reset(self):
    self.camera.look_at(self.start_position, self.start_target, Vector3(0, 0, 1))

  def scroll(self, direction):
    direction.normalize()

    if direction.x:
      self.request_orbit(0, direction.x)
    if direction.y:
      self.camera.dolly(self.DOLLY_SPEED * direction.y)