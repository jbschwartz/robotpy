import glfw

from robot.spatial         import vector3
from robot.visual.camera   import Camera
from robot.visual.observer import Observer

Vector3 = vector3.Vector3

class CameraController(Observer):
  ORBIT_SPEED = 0.05
  ZOOM_SPEED  = 100

  def __init__(self, camera : Camera):
    self.camera = camera
    self.last_cursor_position = None

  def click(self, button, cursor):
    pass
  
  def drag(self, button, cursor_delta, modifiers):
    if button == glfw.MOUSE_BUTTON_MIDDLE:
      if modifiers & glfw.MOD_CONTROL:
        pass
      else:
        direction = vector3.normalize(cursor_delta)
        self.request_orbit(*direction.yx)
  
  def key(self, key, action):
    if key == glfw.KEY_R and action == glfw.RELEASE:
      self.camera.reset()

    if key in [glfw.KEY_RIGHT, glfw.KEY_LEFT, glfw.KEY_UP, glfw.KEY_DOWN]:
      self.arrows(key, action)

  def arrows(self, key, action):
    # TODO: This doesn't handle both keys pressed at once
    direction = {
      glfw.KEY_RIGHT: 1,
      glfw.KEY_LEFT: -1,
      glfw.KEY_UP: -1,
      glfw.KEY_DOWN: 1
    }
    
    if key in [glfw.KEY_RIGHT, glfw.KEY_LEFT] and action in [glfw.PRESS, glfw.REPEAT]:
      self.request_orbit(0, direction[key])
    if key in [glfw.KEY_UP, glfw.KEY_DOWN] and action in [glfw.PRESS, glfw.REPEAT]:
      self.request_orbit(direction[key], 0)

  def request_orbit(self, x, z):
    self.camera.orbit(self.ORBIT_SPEED * x, self.ORBIT_SPEED * z)

  def scroll(self, direction):
    direction.normalize()

    if direction.x:
      self.request_orbit(0, direction.x)
    if direction.y:
      self.camera.zoom(self.ZOOM_SPEED * direction.y)