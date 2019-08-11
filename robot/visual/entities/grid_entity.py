import math
import numpy as np

from OpenGL.GL import *

from ctypes import c_void_p

from robot.spatial                import Vector3, Matrix4
from robot.visual.entities.entity import Entity
from robot.visual.shader_program  import ShaderProgram

class GridEntity(Entity):
  def __init__(self, shader_program : ShaderProgram = None):
    self.buffer = []
    self.scale = 10000

    Entity.__init__(self, shader_program)

  def build_buffer(self):
    data_list = [
       0.5,  0.5,  0,
      -0.5,  0.5,  0,
      -0.5, -0.5,  0,
      -0.5, -0.5,  0,
       0.5, -0.5,  0,
       0.5,  0.5,  0,

      -0.5, -0.5,  0,
      -0.5,  0.5,  0,
       0.5,  0.5,  0,
       0.5,  0.5,  0,
       0.5, -0.5,  0,
      -0.5, -0.5,  0,
    ]

    self.buffer = np.array(data_list, dtype=np.float32)

  def load(self):
    self.build_buffer()

    glBindVertexArray(self.vao)

    glBindBuffer(GL_ARRAY_BUFFER, self.vbo)
    glBufferData(GL_ARRAY_BUFFER, self.buffer.nbytes, self.buffer, GL_STATIC_DRAW)

    glVertexAttribPointer(self.shader_program.attribute_location('vin_position'), 3, GL_FLOAT, GL_FALSE, 0, None)
    glEnableVertexAttribArray(self.shader_program.attribute_location('vin_position'))

    glBindBuffer(GL_ARRAY_BUFFER, 0)
    glBindVertexArray(0)

  def update(self, delta):
    pass

  def draw(self, camera, light):
    self.shader_program.use()

    self.shader_program.proj_matrix = camera.projection.matrix
    self.shader_program.view_matrix = camera.world_to_camera
    # self.shader_program.model_matrix  = Matrix4()
    # self.shader_program.light_position  = light.position
    # self.shader_program.light_color     = light.color
    # self.shader_program.light_intensity = light.intensity
    self.shader_program.step_size = 250.0
    self.shader_program.minor_step_size = 50.0
    self.shader_program.in_grid_color = Vector3(0.5, 0.5, 0.5)
    self.shader_program.in_minor_grid_color = Vector3(0.15, 0.15, 0.15)

    self.shader_program.scale_matrix = Matrix4([
      self.scale, 0, 0, 0,
      0, self.scale, 0, 0,
      0, 0, self.scale, 0,
      0, 0, 0, 1
    ])

    glBindVertexArray(self.vao)

    glDrawArrays(GL_TRIANGLES, 0, 6)

    glBindVertexArray(0)