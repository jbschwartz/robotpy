import OpenGL.GL as gl

from robot.spatial                      import Matrix4, Vector3
from robot.visual.gui                   import Widget
from robot.visual.opengl.shader_program import ShaderProgram

class Rectangle(Widget):
  def __init__(self, **options: dict):
    super().__init__(**options)

  def prepare(self, sp: ShaderProgram):
    gl.glDisable(gl.GL_DEPTH_TEST)

    sp.uniforms.color        = self.color if not self.hover else [0, 1, 1]
    sp.uniforms.position     = self.position
    sp.uniforms.scale_matrix = Matrix4.from_scale(Vector3(self.width, self.height, 1))
