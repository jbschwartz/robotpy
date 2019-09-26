from robot.spatial import Matrix4
from robot.visual.opengl.shader_program import ShaderProgram

class FrameView():
  def __init__(self, serial) -> None:
    self.serial = serial
    self.scale = 15

    self.children = []
    self.visible = True

  def prepare(self, sp: ShaderProgram):
    sp.uniforms.model_matrix = self.serial.pose()

    # TODO: Make this happen at the buffer level so this does not need to be called per frame
    # Unless we actually want per frame scaling (often times we don't)
    sp.uniforms.scale_matrix = Matrix4([
      self.scale, 0, 0, 0,
      0, self.scale, 0, 0,
      0, 0, self.scale, 0,
      0, 0, 0, 1
    ])