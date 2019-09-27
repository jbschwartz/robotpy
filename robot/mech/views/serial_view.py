import glfw

from robot.visual.messaging.listener    import listen, listener
from robot.visual.messaging.event       import Event
from robot.visual.opengl.shader_program import ShaderProgram
from .frame_view                        import FrameView

@listener
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

    # Pass a lambda so that the transformation updates as the robot moves
    # Passing the transformation directly does not work since the robot reassigns
    # its link transformations every frame.
    self.children     = [
      *[FrameView(lambda l=link: l.to_world) for link in self.serial.links]
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

  @listen(Event.KEY)
  def key(self, key, action, modifiers):
    if action == glfw.PRESS and self.highlighted:
      for key_number in range(1, 8):
        if key == getattr(glfw, f'KEY_{key_number}'):
          self.children[key_number - 1].visible = not self.children[key_number - 1].visible
          return
