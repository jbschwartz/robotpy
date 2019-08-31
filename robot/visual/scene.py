from OpenGL.GL import *

from .camera             import Camera
from .messaging.listener import listen, listener
from .messaging.event    import Event

@listener
class Scene():
  def __init__(self, camera, light):
    self.camera = camera
    self.light = light

  @listen(Event.DRAW)
  def draw(self):
    self.light.position = self.camera.position