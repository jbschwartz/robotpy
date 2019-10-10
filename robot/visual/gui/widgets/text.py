import glfw

import OpenGL.GL as gl

from typing import Iterable

from robot.visual.gui.widget         import Widget
from robot.visual                    import Font
from robot.visual.opengl             import ShaderProgram
from robot.visual.messaging.listener import listen, listener
from robot.visual.messaging.event    import Event
from robot.spatial                   import Matrix4, Vector3

@listener
class Text(Widget):
  def __init__(self, string: str, font: Font, **options: dict) -> None:
    super().__init__(**options)

    self.string = string
    self.font = font
    self.size = 32
    self.scale = self.size / self.font.font_size

  def load(self):
    self.widths = [w * self.scale for w in self.font.widths(self.string)]
    self.total_width = sum(self.widths)
    self.widths = [w / self.total_width for w in self.widths]
    self.uvs = self.font.uvs(self.string)
    self.pixel_height = self.size
    self.reload_buffer = True
    self._width = self.total_width / self.screen_width
    self._height = self.pixel_height / self.screen_height

  @listen(Event.WINDOW_RESIZE)
  def resize(self, width, height):
    self.screen_width = width
    self.screen_height = height
    self.load()

  def character_buffer(self, width, offset, u, v) -> Iterable[float]:
    x_min = offset
    x_max = x_min + width
    pixel_width = width * self.total_width / self.scale
    u_max = u + (pixel_width / 1024)
    v_max = v + (64 / 1024)

    return [
      ([x_max,  0,  0], [u_max, v_max]), # Top Right
      ([x_min,  0,  0], [u,     v_max]), # Top Left
      ([x_min,  1,  0], [u,     v    ]), # Bottom Left
      ([x_min,  1,  0], [u,     v    ]), # Bottom Left
      ([x_max,  1,  0], [u_max, v    ]), # Bottom Right
      ([x_max,  0,  0], [u_max, v_max]), # Top Right
    ]

  @property
  def buffer(self) -> Iterable[float]:
    data = []
    offset = 0
    for width, (u, v) in zip(self.widths, self.uvs):
      data.extend(self.character_buffer(width, offset, u, v))
      offset += width

    return data

  def prepare(self, sp: ShaderProgram):
    gl.glDisable(gl.GL_DEPTH_TEST)

    sp.uniforms.color        = self.color if not self.hover else [0, 1, 1]
    sp.uniforms.position     = self.position
    sp.uniforms.scale_matrix = Matrix4.from_scale(Vector3(self.width, self.height, 1))
