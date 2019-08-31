from OpenGL.GL import *

from robot.spatial       import AABB
from .camera             import Camera
from .messaging.listener import listen, listener
from .messaging.event    import Event

@listener
class Scene():
  def __init__(self, camera, light):
    self.camera = camera
    self.entities = []
    self.light = light

  @property
  def aabb(self):
    aabb = AABB()
    for entity in self.entities:
      try:
        # TODO: Maybe there's a better way to do this. Or at least I need to put an AABB on all entities (in the entity base class?)
        aabb.expand(entity.aabb)
      except AttributeError:
        pass
    return aabb

  def intersect(self, ray):
    if self.aabb.intersect(ray):
      return ray.closest_intersection(self.entities)
    else:
      return None

  @listen(Event.DRAW)
  def draw(self):
    self.light.position = self.camera.position