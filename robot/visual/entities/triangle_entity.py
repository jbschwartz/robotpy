import numpy as np
import glfw

from OpenGL.GL import *

from ctypes import c_void_p

from robot.spatial                   import Matrix4, Vector3
from robot.visual.opengl.shader_program     import ShaderProgram
from robot.visual.messaging.listener import listen, listener
from robot.visual.messaging.event    import Event

@listener
class TriangleEntity():
  def __init__(self, camera, shader_program : ShaderProgram = None, color = (0, 0.5, 1)):
    self.vao = -1 if not bool(glGenVertexArrays) else glGenVertexArrays(1)
    self.vbo = -1 if not bool(glGenBuffers) else glGenBuffers(1)
    self.buffer = []
    self.color = color
    self.shader_program = shader_program
    self.scale = 20
    self.link = None
    self.show = False
    self.camera = camera

  def use_shader(self, shader_program):
    self.shader_program = shader_program

  def build_buffer(self):
    data_list = [
       0.5, -0.33, 0,
       0.0,  0.66, 0,
      -0.5, -0.33, 0
    ]

    self.buffer = np.array(data_list, dtype=np.float32)

  def load(self):
    self.build_buffer()

    glBindVertexArray(self.vao)

    glBindBuffer(GL_ARRAY_BUFFER, self.vbo)
    glBufferData(GL_ARRAY_BUFFER, self.buffer.nbytes, self.buffer, GL_STATIC_DRAW)

    glVertexAttribPointer(self.shader_program.attribute_location('vin_position'), 3, GL_FLOAT, GL_FALSE, 12, None)
    glEnableVertexAttribArray(self.shader_program.attribute_location('vin_position'))

    glBindBuffer(GL_ARRAY_BUFFER, 0)
    glBindVertexArray(0)

  def update(self, delta):
    pass

  @listen(Event.CLICK)
  def click(self, button, action, cursor):
    if button == glfw.MOUSE_BUTTON_MIDDLE:
      self.show = action == glfw.PRESS

  def draw(self):
    if not self.show:
      return

    target = Vector3(*self.camera.target)

    self.transform = Matrix4([
      1, 0, 0, 0,
      0, 1, 0, 0,
      0, 0, 1, 0,
      target.x, target.y, target.z, 1
    ])

    # TODO: This maybe could be a decorator to the draw function inside the entity
    self.shader_program.use()

    self.shader_program.uniforms.model_matrix = self.transform
    self.shader_program.uniforms.scale_matrix = Matrix4([
      self.scale, 0, 0, 0,
      0, self.scale, 0, 0,
      0, 0, self.scale, 0,
      0, 0, 0, 1
    ])
    self.shader_program.uniforms.color_in     = self.color
    self.shader_program.uniforms.in_opacity = 0.5

    glBindVertexArray(self.vao)

    glDrawArrays(GL_TRIANGLES, 0, 3)

    glBindVertexArray(0)