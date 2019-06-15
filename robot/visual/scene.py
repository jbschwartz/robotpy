from OpenGL.GL import *

from robot.visual.camera        import Camera
from robot.visual.observer      import Observer
from robot.visual.window_events import WindowEvents

class Scene(Observer):
  def __init__(self, camera, light):
    self.camera = camera
    self.entities = []
    self.light = light

  def window_resize(self, window, width, height):
    if width and height:
      self.camera.aspect = width / height
      glViewport(0, 0, width, height)

  def start_renderer(self):  
    glClearColor(0.65, 1.0, 0.50, 1)

    glEnable(GL_DEPTH_TEST)
    glEnable(GL_MULTISAMPLE)
    glEnable(GL_BLEND)
    glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)

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
