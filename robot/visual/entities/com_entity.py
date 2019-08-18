import glfw

from OpenGL.GL import *

from robot.visual.opengl.shader_program import ShaderProgram

class COMEntity():
  def __init__(self, link, shader_program : ShaderProgram = None):
    self.vao = -1 if not bool(glGenVertexArrays) else glGenVertexArrays(1)

    self.link = link
    self.radius = 25
    self.shader_program = shader_program

  def load(self):
    pass

  def update(self, delta):
    pass

  def draw(self, camera, light):
    center_of_mass = camera.world_to_camera(self.link.to_world(self.link.properties.com))

    # TODO: This maybe could be a decorator to the draw function inside the entity
    self.shader_program.use()

    # TODO: Issue a warning (exception?) if assigning to a uniform that does not exist in the shader
    self.shader_program.radius   = self.radius
    self.shader_program.position = center_of_mass

    glBindVertexArray(self.vao)

    glDrawArrays(GL_TRIANGLE_STRIP, 0, 4)

    glBindVertexArray(0)