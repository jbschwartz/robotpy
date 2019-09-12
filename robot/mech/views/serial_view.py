from robot.visual.opengl.shader_program import ShaderProgram
from .frame_view                        import FrameView

class SerialView():
  def __init__(self, serial):
    # TODO: Decide if this should also be a Widget
    # Or if there should be a View base class

    self.serial       = serial
    self.visible      = True
    self.visibilities = []
    self.color        = [1, 0.5, 0]
    self.colors       = []
    self.selected     = None
    self.children     = [
      FrameView(self.serial)
    ]
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
