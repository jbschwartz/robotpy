import math
import numpy as np

from OpenGL.GL import *

from ctypes import c_void_p

from robot.spatial.aabb           import AABB
from robot.spatial.matrix4        import Matrix4
from robot.spatial.transform      import Transform
from robot.spatial.vector3        import Vector3
from robot.visual.entities.entity import Entity
from robot.visual.shader_program  import ShaderProgram

class BoundingEntity(Entity):
  def __init__(self, shader_program : ShaderProgram = None):
    self.buffer = []
    self.aabb = AABB()

    Entity.__init__(self, shader_program)

  def build_buffer(self):
    data_list = [
      # Right
       0.5,  0.5, -0.5,
       0.5,  0.5,  0.5,
       0.5, -0.5,  0.5,
       0.5, -0.5,  0.5,
       0.5, -0.5, -0.5,
       0.5,  0.5, -0.5,

      # Left
      -0.5,  0.5, -0.5,
      -0.5, -0.5,  0.5,
      -0.5,  0.5,  0.5,
      -0.5, -0.5,  0.5,
      -0.5,  0.5, -0.5,
      -0.5, -0.5, -0.5,

      # Front
       0.5, -0.5, -0.5,
       0.5, -0.5,  0.5,
      -0.5, -0.5,  0.5,
      -0.5, -0.5,  0.5,
      -0.5, -0.5, -0.5,
       0.5, -0.5, -0.5,

      # Back
       0.5,  0.5, -0.5,
      -0.5,  0.5,  0.5,
       0.5,  0.5,  0.5,
       0.5,  0.5, -0.5,
      -0.5,  0.5, -0.5,
      -0.5,  0.5,  0.5,

      # Top
       0.5, -0.5,  0.5,
       0.5,  0.5,  0.5,
      -0.5,  0.5,  0.5,
      -0.5,  0.5,  0.5,
      -0.5, -0.5,  0.5,
       0.5, -0.5,  0.5,

      # Bottom
       0.5,  0.5, -0.5,
       0.5, -0.5, -0.5,
      -0.5,  0.5, -0.5,
      -0.5,  0.5, -0.5,
       0.5, -0.5, -0.5,
      -0.5, -0.5, -0.5
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

  def draw(self, camera, light, transform = Transform()):
    transform *= Transform.from_axis_angle_translation(translation = self.aabb.center)

    self.shader_program.use()

    self.shader_program.proj_matrix = camera.projection.matrix
    self.shader_program.view_matrix = camera.world_to_camera

    self.shader_program.light_position  = light.position
    self.shader_program.light_color     = light.color
    self.shader_program.light_intensity = light.intensity

    self.shader_program.model_matrix = transform

    size = self.aabb.size
    self.shader_program.scale_matrix = Matrix4([
      size.x, 0, 0, 0,
      0, size.y, 0, 0,
      0, 0, size.z, 0,
      0, 0, 0, 1
    ])
    self.shader_program.in_opacity = 0.25

    glBindVertexArray(self.vao)

    self.shader_program.color_in     = Vector3(0.5, 0, 0)
    glDrawArrays(GL_TRIANGLES, 0, 36)

    glBindVertexArray(0)