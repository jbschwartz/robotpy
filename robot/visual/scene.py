from OpenGL.GL import *

from ctypes import c_void_p

from robot.spatial       import AABB, Matrix4
from .camera             import Camera
from .messaging.listener import listen, listener
from .messaging.event    import Event
from .opengl.uniform_buffer import Mapping, UniformBuffer

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

  @listen(Event.WINDOW_RESIZE)
  def window_resize(self, width, height):
    if width and height:
      glViewport(0, 0, width, height)

  @listen(Event.START_RENDERER)
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

    self.matrix_ub = UniformBuffer("Matrices", 1)

    self.matrix_ub.bind(Mapping(
      self.camera, ['projection.matrix', 'world_to_camera']
    ))

    self.light_ub = UniformBuffer("Light", 2)

    self.light_ub.bind(Mapping(
      self.light, ['position', 'color', 'intensity']
    ))

  @listen(Event.START_FRAME)
  def start_frame(self):
    glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)

  @listen(Event.UPDATE)
  def update(self, delta = 0):
    for entity in self.entities:
      entity.update(delta)

  @listen(Event.DRAW)
  def draw(self):
    self.light.position = self.camera.position

    self.light_ub.load()
    self.matrix_ub.load()

    for entity in self.entities:
      entity.draw(self.camera, self.light)

      glUseProgram(0)
