import math
import numpy as np

from OpenGL.GL import *

from ctypes import c_void_p

from robot.spatial.frame          import Frame
from robot.spatial.matrix4        import Matrix4
from robot.spatial.transform      import Transform
from robot.spatial.vector3        import Vector3
from robot.visual.entities.entity import Entity
from robot.visual.shader_program  import ShaderProgram

class FrameEntity(Entity):
  def __init__(self, frame = Frame(), shader_program : ShaderProgram = None, color = (0.5, 0, 0)):
    self.buffer = []
    self.frame = frame
    self.scale = 15

    Entity.__init__(self, shader_program, color)

  def build_buffer(self):
    # TODO: Something prettier maybe?
    data_list = [
       # X
       8, -0.25, 0.25,
       0.25, -0.25,  0.25,
       0.25, -0.25, -0.25,
       0.25, -0.25, -0.25,
       8, -0.25, -0.25,
       8, -0.25, 0.25,
       
       8, 0.25, 0.25,
       0.25, 0.25,  0.25,
       0.25, 0.25, -0.25,
       0.25, 0.25, -0.25,
       8, 0.25, -0.25,
       8, 0.25, 0.25,

       8, 0.25, 0.25,
       0.25, 0.25,  0.25,
       0.25, -0.25, 0.25,
       0.25, -0.25, 0.25,
       8, -0.25, 0.25,
       8, 0.25, 0.25,

       8, 0.25, -0.25,
       0.25, 0.25,  -0.25,
       0.25, -0.25, -0.25,
       0.25, -0.25, -0.25,
       8, -0.25, -0.25,
       8, 0.25, -0.25,

       8, 0.25, 0.25,
       8, -0.25, 0.25,
       8, -0.25, -0.25,
       8, -0.25, -0.25,
       8, 0.25, -0.25,
       8, 0.25, 0.25,

       0.25, 0.25, 0.25,
       0.25, -0.25, 0.25,
       0.25, -0.25, -0.25,
       0.25, -0.25, -0.25,
       0.25, 0.25, -0.25,
       0.25, 0.25, 0.25,

       # Y
       0.25,  8, 0.25,
       0.25,  0.25, 0.25,
      -0.25,  0.25, 0.25,
      -0.25,  0.25, 0.25,
      -0.25,  8, 0.25,
       0.25, 8, 0.25,

       0.25,  8, -0.25,
       0.25,  0.25, -0.25,
      -0.25,  0.25, -0.25,
      -0.25,  0.25, -0.25,
      -0.25,  8, -0.25,
       0.25, 8, -0.25,

       0.25,  8, -0.25,
       0.25,  0.25, -0.25,
       0.25,  0.25, 0.25,
       0.25,  0.25, 0.25,
       0.25,  8, 0.25,
       0.25, 8, -0.25,

       -0.25,  8, -0.25,
       -0.25,  0.25, -0.25,
       -0.25,  0.25, 0.25,
       -0.25,  0.25, 0.25,
       -0.25,  8, 0.25,
       -0.25, 8, -0.25,
       
       -0.25, 0.25, -0.25,
       -0.25, 0.25, 0.25,
        0.25, 0.25, 0.25,
        0.25, 0.25, 0.25,
       -0.25, 0.25, -0.25,
        0.25, 0.25, -0.25,
        
       -0.25, 8, -0.25,
       -0.25, 8, 0.25,
        0.25, 8, 0.25,
        0.25, 8, 0.25,
       -0.25, 8, -0.25,
        0.25, 8, -0.25,

      # Z
       0.25, 0.25,  8,
       0.25, 0.25,  0.25,
      -0.25, 0.25,  0.25,
      -0.25, 0.25,  0.25,
      -0.25, 0.25,  8,
       0.25, 0.25, 8,

       0.25, -0.25,  8,
       0.25, -0.25,  0.25,
      -0.25, -0.25,  0.25,
      -0.25, -0.25,  0.25,
      -0.25, -0.25,  8,
       0.25, -0.25, 8,

       0.25, -0.25,  8,
       0.25, -0.25,  0.25,
       0.25,  0.25,  0.25,
       0.25,  0.25,  0.25,
       0.25,  0.25,  8,
       0.25, -0.25, 8,

      -0.25,  0.25,  8,
      -0.25,  0.25,  0.25,
      -0.25, -0.25,  0.25,
      -0.25, -0.25,  0.25,
      -0.25, -0.25,  8,
      -0.25,  0.25, 8,

       0.25, -0.25, 0.25,
      -0.25, -0.25, 0.25,
      -0.25,  0.25, 0.25,
      -0.25,  0.25, 0.25,
       0.25,  0.25, 0.25,
       0.25, -0.25, 0.25,

       0.25, -0.25, 8,
      -0.25, -0.25, 8,
      -0.25,  0.25, 8,
      -0.25,  0.25, 8,
       0.25,  0.25, 8,
       0.25, -0.25, 8,

      # Origin
       0.25, -0.25, 0.25,
      -0.25, -0.25, 0.25,
      -0.25, -0.25, -0.25,
      -0.25, -0.25, -0.25,
       0.25, -0.25, -0.25,
       0.25, -0.25, 0.25,

       0.25, -0.25, -0.25,
      -0.25, -0.25, -0.25,
      -0.25,  0.25, -0.25,
      -0.25,  0.25, -0.25,
       0.25,  0.25, -0.25,
       0.25, -0.25, -0.25,

       -0.25, 0.25, 0.25,
       -0.25, -0.25, 0.25,
       -0.25, -0.25, -0.25,
       -0.25, -0.25, -0.25,
       -0.25, 0.25, -0.25,
       -0.25, 0.25, 0.25
    ]
    
    self.buffer = np.array([self.scale * component for component in data_list], dtype=np.float32)

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
      transform = self.frame.transform
      
    glUseProgram(self.shader_program.program_id)

    self.shader_program.proj_matrix = camera.projection
    self.shader_program.view_matrix = camera.world_to_camera

    self.shader_program.light_position  = light.position
    self.shader_program.light_color     = light.color
    self.shader_program.light_intensity = light.intensity
    
    self.shader_program.model_matrix = transform

    glBindVertexArray(self.vao)

    # TODO: This is a very hacky way to handle coloring
    self.shader_program.color_in     = Vector3(0.5, 0, 0)
    glDrawArrays(GL_TRIANGLES, 0, 36)
    self.shader_program.color_in     = Vector3(0, 0.5, 0)
    glDrawArrays(GL_TRIANGLES, 36, 36)
    self.shader_program.color_in     = Vector3(0, 0, 0.5)
    glDrawArrays(GL_TRIANGLES, 72, 36)

    self.shader_program.color_in     = Vector3(1, 1, 0)
    glDrawArrays(GL_TRIANGLES, 108, 18)

    glBindVertexArray(0)