from OpenGL.GL import *

from robot.visual.shader_program import ShaderProgram

class Entity:
  def __init__(self, shader_program : ShaderProgram = None, color = (1, 1, 1)):
    self.vao = -1 if not bool(glGenVertexArrays) else glGenVertexArrays(1)
    self.vbo = -1 if not bool(glGenBuffers) else glGenBuffers(1)
    self.buffer = []
    self.color = color
    self.shader_program = shader_program

  def use_shader(self, shader_program):
    self.shader_program = shader_program