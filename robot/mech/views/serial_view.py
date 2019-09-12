from robot.visual.gui import Widget
from robot.visual.opengl.shader_program import ShaderProgram

class SerialView():
  def __init__(self, serial):
    self.serial       = serial
    self.visible      = True
    self.visibilities = []
    self.color        = [1, 0.5, 0]
    self.colors       = []
    self.selected     = None
    self.children     = []
    self.highlighted  = False

  def select(self) -> None:
    self.highlighted = True

  def deselect(self) -> None:
    self.highlighted = False

  def prepare(self, sp: ShaderProgram):
    sp.uniforms.model_matrices  = self.serial.poses()

    if self.highlighted:
      sp.uniforms.link_colors = [[0, 1, 1]] * 7
    else:
      sp.uniforms.link_colors     = [self.color] * 7
