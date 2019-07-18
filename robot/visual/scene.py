from OpenGL.GL import *

from robot.spatial.aabb    import AABB
from robot.visual.camera   import Camera
from robot.visual.observer import Observer

class Scene(Observer):
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
        aabb.extend(entity.aabb)
      except AttributeError:
        pass
    return aabb

  def intersect(self, ray):
    if self.aabb.intersect(ray):
      return ray.closest_intersection(self.entities)
    else:
      return None

  def window_resize(self, width, height):
    if width and height:
      glViewport(0, 0, width, height)

  def start_renderer(self):
    glClearColor(1, 1, 1, 1)

    glEnable(GL_DEPTH_TEST)
    glEnable(GL_MULTISAMPLE)
    glEnable(GL_BLEND)
    glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)

    glEnable(GL_CULL_FACE)
    glCullFace(GL_BACK)
    glFrontFace(GL_CCW)

    for entity in self.entities:
      entity.load()

  def start_frame(self):
    glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)

  def update(self, delta = 0):
    for entity in self.entities:
      entity.update(delta)

    self.light.position = self.camera.position

  def draw(self):
    for entity in self.entities:
      entity.draw(self.camera, self.light)

      glUseProgram(0)
