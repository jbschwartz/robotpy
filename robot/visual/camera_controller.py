import glfw

from robot.spatial.vector3 import Vector3
from robot.visual.camera   import Camera
from robot.visual.observer import Observer

class CameraController(Observer):
  ORBIT_SPEED = 0.1

  def __init__(self, camera : Camera):
    self.camera = camera

  def click(self, cursor, action):
    pass
  
  def cursor(self, cursor):
    pass
  
  def key(self, key, action):
    if key == glfw.KEY_R and action == glfw.RELEASE:
      self.camera.reset()

    if key in [glfw.KEY_RIGHT, glfw.KEY_LEFT, glfw.KEY_UP, glfw.KEY_DOWN]:
      # TODO: This doesn't handle both keys pressed at once
      self.request_orbit(key, action)

  def request_orbit(self, key, action):
    angle = Vector3()
    
    direction = {
      glfw.KEY_RIGHT: 1,
      glfw.KEY_LEFT: -1,
      glfw.KEY_UP: -1,
      glfw.KEY_DOWN: 1
    }

    if key in [glfw.KEY_RIGHT, glfw.KEY_LEFT] and action in [glfw.PRESS, glfw.REPEAT]:
      angle.z = self.ORBIT_SPEED * direction[key]
    if key in [glfw.KEY_UP, glfw.KEY_DOWN] and action in [glfw.PRESS, glfw.REPEAT]:
      angle.x = self.ORBIT_SPEED * direction[key]

    self.camera.orbit(angle.x, angle.z)

  def scroll(self, direction):
    pass