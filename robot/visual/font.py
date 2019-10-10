from typing import Iterable

from robot.spatial       import Matrix4, Vector3
from robot.visual.opengl import ShaderProgram

class Font:
  def __init__(self, start_char: int, grid_size: int, widths: Iterable[int]) -> None:
    self.visible = True
    self.color = [0] * 3
    self.buffer = []

    self.strings = []

    self.start_char = start_char
    self.grid_size = grid_size # The number of characters in a row on the texture
    self.char_widths = [
      22, 30, 26, 30, 30, 30, 30, 30, 30, 30, 30, 30, 30,  5, 30, 30,
      30, 30, 30, 30, 30, 30, 30, 30, 30, 30, 30, 30, 30, 30, 30, 30,
      13, 13, 18, 28, 25, 38, 38, 11, 14, 14, 20, 32, 10, 19, 10, 18,
      25, 25, 25, 25, 25, 25, 25, 25, 25, 25, 10, 10, 32, 32, 32, 21,
      45, 30, 27, 29, 33, 24, 23, 32, 33, 13, 17, 27, 22, 42, 35, 35,
      26, 35, 28, 25, 25, 32, 29, 44, 28, 26, 27, 14, 18, 14, 32, 20,
      13, 24, 28, 22, 28, 25, 15, 28, 27, 11, 11, 23, 11, 40, 27, 28,
      28, 28, 16, 20, 16, 27, 23, 34, 22, 23, 21, 14, 11, 14, 32, 14,
      25, 30, 11, 25, 18, 34, 18, 18, 17, 57, 25, 15, 44, 30, 27, 30,
      30, 11, 11, 18, 18, 19, 24, 47, 16, 36, 20, 15, 44, 30, 21, 26,
      13, 13, 25, 25, 26, 25, 11, 21, 19, 42, 18, 24, 32, 19, 42, 20,
      18, 32, 17, 17, 13, 27, 22, 10, 10, 17, 20, 24, 43, 44, 45, 21,
      30, 30, 30, 30, 30, 30, 40, 29, 24, 24, 24, 24, 13, 13, 13, 13,
      33, 35, 35, 35, 35, 35, 35, 32, 35, 32, 32, 32, 32, 26, 26, 26,
      24, 24, 24, 24, 24, 24, 39, 22, 25, 25, 25, 25, 11, 11, 11, 11,
      26, 27, 28, 28, 28, 28, 28, 32, 28, 27, 27, 27, 27, 23, 28, 23]

    self.cell_size = 64
    self.font_size = 64

    assert len(self.char_widths) == 256, "Not the correct number of widths"

  def widths(self, string: str):
    ascii_codes = self.ascii(string)
    return [self.char_widths[code] for code in ascii_codes]

  def ascii(self, string):
    return [ord(c) for c in string]

  def uvs(self, string):
    uvs = []
    for char in string:
      position = self.ascii(char)[0] - self.start_char
      row = position // self.grid_size
      column = position - (row * self.grid_size)

      u = column / self.grid_size
      v = (row + 1) / self.grid_size

      uvs.append((u, 1 - v))

    return uvs
