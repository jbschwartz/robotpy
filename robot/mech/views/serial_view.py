from robot.visual.gui import Widget
from robot.visual.opengl.shader_program import ShaderProgram

class SerialView():
  def __init__(self, serial):
    self.serial = serial
    self.visible = True
    self.visibilities = []
    self.color = [1, 0.5, 0]
    self.colors = []
    self.selected = None
    self.children = []

  def prepare(self, sp: ShaderProgram):
    sp.uniforms.model_matrices  = self.serial.poses()
    sp.uniforms.link_colors     = [self.color] * 7
