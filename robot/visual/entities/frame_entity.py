import math
import numpy as np

from OpenGL.GL import *

from ctypes import c_void_p

from robot.spatial                import Matrix4, Transform, Vector3
from robot.visual.entities.entity import Entity
from robot.visual.opengl.shader_program  import ShaderProgram

class FrameEntity(Entity):
  def __init__(self, frame = Transform(), shader_program : ShaderProgram = None):
    self.buffer = []
    self.frame = frame
    self.scale = 15

    Entity.__init__(self, shader_program)

  def build_buffer(self):
    data_list = [
      # X axis
       8.00, -0.25,  0.25,
       0.25, -0.25,  0.25,
       0.25, -0.25, -0.25,
       0.25, -0.25, -0.25,
       8.00, -0.25, -0.25,
       8.00, -0.25,  0.25,

       0.25,  0.25, -0.25,
       0.25,  0.25,  0.25,
       8.00,  0.25,  0.25,
       8.00,  0.25,  0.25,
       8.00,  0.25, -0.25,
       0.25,  0.25, -0.25,

       8.00,  0.25,  0.25,
       0.25,  0.25,  0.25,
       0.25, -0.25,  0.25,
       0.25, -0.25,  0.25,
       8.00, -0.25,  0.25,
       8.00,  0.25,  0.25,

       0.25, -0.25, -0.25,
       0.25,  0.25, -0.25,
       8.00,  0.25, -0.25,
       8.00,  0.25, -0.25,
       8.00, -0.25, -0.25,
       0.25, -0.25, -0.25,

       8.00,  0.25,  0.25,
       8.00, -0.25,  0.25,
       8.00, -0.25, -0.25,
       8.00, -0.25, -0.25,
       8.00,  0.25, -0.25,
       8.00,  0.25,  0.25,

       0.25, -0.25, -0.25,
       0.25, -0.25,  0.25,
       0.25,  0.25,  0.25,
       0.25,  0.25,  0.25,
       0.25,  0.25, -0.25,
       0.25, -0.25, -0.25,

      # Y axis
      -0.25,  0.25,  0.25,
       0.25,  0.25,  0.25,
       0.25,  8.00,  0.25,
       0.25,  8.00,  0.25,
      -0.25,  8.00,  0.25,
      -0.25,  0.25,  0.25,

       0.25,  8.00, -0.25,
       0.25,  0.25, -0.25,
      -0.25,  0.25, -0.25,
      -0.25,  0.25, -0.25,
      -0.25,  8.00, -0.25,
       0.25,  8.00, -0.25,

       0.25,  0.25,  0.25,
       0.25,  0.25, -0.25,
       0.25,  8.00, -0.25,
       0.25,  8.00, -0.25,
       0.25,  8.00,  0.25,
       0.25,  0.25,  0.25,

      -0.25,  8.00, -0.25,
      -0.25,  0.25, -0.25,
      -0.25,  0.25,  0.25,
      -0.25,  0.25,  0.25,
      -0.25,  8.00,  0.25,
      -0.25,  8.00, -0.25,

      -0.25,  0.25, -0.25,
       0.25,  0.25,  0.25,
      -0.25,  0.25,  0.25,
      -0.25,  0.25, -0.25,
       0.25,  0.25, -0.25,
       0.25,  0.25,  0.25,

      -0.25,  8.00, -0.25,
      -0.25,  8.00,  0.25,
       0.25,  8.00,  0.25,
       0.25,  8.00,  0.25,
       0.25,  8.00, -0.25,
      -0.25,  8.00, -0.25,

      # Z axis
       0.25,  0.25,  8.00,
       0.25,  0.25,  0.25,
      -0.25,  0.25,  0.25,
      -0.25,  0.25,  0.25,
      -0.25,  0.25,  8.00,
       0.25,  0.25,  8.00,

      -0.25, -0.25,  0.25,
       0.25, -0.25,  0.25,
       0.25, -0.25,  8.00,
       0.25, -0.25,  8.00,
      -0.25, -0.25,  8.00,
      -0.25, -0.25,  0.25,

       0.25, -0.25,  8.00,
       0.25, -0.25,  0.25,
       0.25,  0.25,  0.25,
       0.25,  0.25,  0.25,
       0.25,  0.25,  8.00,
       0.25, -0.25,  8.00,

      -0.25,  0.25,  8.00,
      -0.25,  0.25,  0.25,
      -0.25, -0.25,  0.25,
      -0.25, -0.25,  0.25,
      -0.25, -0.25,  8.00,
      -0.25,  0.25,  8.00,

       0.25, -0.25,  0.25,
      -0.25, -0.25,  0.25,
      -0.25,  0.25,  0.25,
      -0.25,  0.25,  0.25,
       0.25,  0.25,  0.25,
       0.25, -0.25,  0.25,

      -0.25,  0.25,  8.00,
      -0.25, -0.25,  8.00,
       0.25, -0.25,  8.00,
       0.25, -0.25,  8.00,
       0.25,  0.25,  8.00,
      -0.25,  0.25,  8.00,

      # Origin
       0.25, -0.25,  0.25,
      -0.25, -0.25,  0.25,
      -0.25, -0.25, -0.25,
      -0.25, -0.25, -0.25,
       0.25, -0.25, -0.25,
       0.25, -0.25,  0.25,

       0.25, -0.25, -0.25,
      -0.25, -0.25, -0.25,
      -0.25,  0.25, -0.25,
      -0.25,  0.25, -0.25,
       0.25,  0.25, -0.25,
       0.25, -0.25, -0.25,

      -0.25, -0.25,  0.25,
      -0.25,  0.25,  0.25,
      -0.25, -0.25, -0.25,
      -0.25, -0.25, -0.25,
      -0.25,  0.25,  0.25,
      -0.25,  0.25, -0.25
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

  def draw(self, camera, light, transform = None):
    if not transform:
      transform = self.frame

    self.shader_program.use()

    self.shader_program.uniforms.model_matrix = transform
    self.shader_program.uniforms.scale_matrix = Matrix4([
      self.scale, 0, 0, 0,
      0, self.scale, 0, 0,
      0, 0, self.scale, 0,
      0, 0, 0, 1
    ])
    self.shader_program.uniforms.in_opacity = 1.

    glBindVertexArray(self.vao)

    # TODO: This is a very hacky way to handle coloring
    self.shader_program.uniforms.color_in     = Vector3(0.5, 0, 0)
    glDrawArrays(GL_TRIANGLES, 0, 36)
    self.shader_program.uniforms.color_in     = Vector3(0, 0.5, 0)
    glDrawArrays(GL_TRIANGLES, 36, 36)
    self.shader_program.uniforms.color_in     = Vector3(0, 0, 0.5)
    glDrawArrays(GL_TRIANGLES, 72, 36)

    self.shader_program.uniforms.color_in     = Vector3(1, 1, 0)
    glDrawArrays(GL_TRIANGLES, 108, 18)

    glBindVertexArray(0)