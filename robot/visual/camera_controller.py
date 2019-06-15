import glfw

from robot.visual.camera   import Camera
from robot.visual.observer import Observer

class CameraController(Observer):
  def __init__(self, camera : Camera):
    self.camera = camera

  def click(self, cursor, action):
    pass
  
  def cursor(self, cursor):
    pass
  
  def key(self, key, action):
    if key == glfw.KEY_R and action == glfw.RELEASE:
      self.camera.reset()

  def scroll(self, direction):
    pass