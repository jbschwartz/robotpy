import math
import numpy as np

from OpenGL.GL import *

from ctypes import c_void_p

from robot.spatial                         import Matrix4, Mesh, Transform, Vector3
from robot.visual.entities.entity          import Entity
from robot.visual.filetypes.stl.stl_parser import STLParser
from robot.visual.opengl.buffer            import Buffer
from robot.visual.opengl.shader_program    import ShaderProgram

class FrameEntity(Entity):
  def __init__(self, frame = Transform(), shader_program : ShaderProgram = None):
    self.buffer = []
    self.frame = frame
    self.scale = 15

    Entity.__init__(self, shader_program)

    # TODO: Notice that this has to be after the Entity.__init__ call because I am replacing self.buffer
    p = STLParser()
    mesh = Mesh.from_file(p, './robot/visual/meshes/frame.stl')
    self.buffer = Buffer.from_meshes(mesh)

  def load(self):
    self.buffer.set_attribute_locations(self.shader_program)
    self.buffer.load()

  def update(self, delta):
    pass

  def draw(self):
    with self.shader_program as sp, self.buffer:
      sp.uniforms.model_matrix = self.frame
      sp.uniforms.scale_matrix = Matrix4([
        self.scale, 0, 0, 0,
        0, self.scale, 0, 0,
        0, 0, self.scale, 0,
        0, 0, 0, 1
      ])
      sp.uniforms.in_opacity = 1.

      # TODO: This is a very hacky way to handle coloring
      sp.uniforms.color_in     = Vector3(0.5, 0, 0)
      glDrawArrays(GL_TRIANGLES, 0, 36)
      sp.uniforms.color_in     = Vector3(0, 0.5, 0)
      glDrawArrays(GL_TRIANGLES, 36, 36)
      sp.uniforms.color_in     = Vector3(0, 0, 0.5)
      glDrawArrays(GL_TRIANGLES, 72, 36)

      sp.uniforms.color_in     = Vector3(1, 1, 0)
      glDrawArrays(GL_TRIANGLES, 108, 18)