from OpenGL.GL import *

from .camera        import Camera
from .observer      import Observer
from .window_events import WindowEvents

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
  
  def draw(self):
    for entity in self.entities:
      program = entity.shader_program

      glUseProgram(program.program_id)

      program.uniforms['proj_matrix'].set_value(1, False, self.camera.projection_matrix())
      program.uniforms['view_matrix'].set_value(1, False, self.camera.camera_matrix())

      program.uniforms['light_position'].set_value(1, [*self.light.position])
      program.uniforms['light_color'].set_value(1, [*self.light.color])
      program.uniforms['light_intensity'].set_value(self.light.intensity)
      
      entity.draw()

      glUseProgram(0)
