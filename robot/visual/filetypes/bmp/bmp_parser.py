import struct

from collections import namedtuple

class BMPParserException(Exception):
  pass

class BMPParser():
  def __init__(self) -> None:
    pass

  def parse(self, file_path):
    with open(file_path, 'rb') as f:
      try:
        offset = self.bmp_header(f)

        width, height = self.dib_header(f)
      except BMPParserException as e:
        # Not a bitmap file
        # or some handled DIB header type
        # print(e)
        return False

      # Ignore the second set of header information
      # This is very brittle because it means the parser
      # has no idea what the pixel format is.
      # Assume 24-bit RGB
      values = self.pixel_data(f, offset, width, height)

    return (values, width, height)


  def bmp_header(self, f):
    if f.read(2).decode('ascii') != 'BM':
      raise BMPParserException('Not a bitmap')

    # Unpack this if it needs to be used
    file_size = f.read(4)
    reserved = f.read(4)

    return struct.unpack('<i', f.read(4))[0]

  def dib_header(self, f):
    length = struct.unpack('<i', f.read(4))[0]

    if length != 40:
      raise BMPParserException('DIB header not handled')

    width = struct.unpack('<i', f.read(4))[0]
    height = struct.unpack('<i', f.read(4))[0]
    return (width, height)

  def read_pixel_row(self, f, width, padding_per_row):
    grayscales = []
    for _ in range(width):
      pixel = struct.unpack('<B B B', f.read(3))
      grayscales.append(int(sum(pixel) / 3))

    f.read(padding_per_row)
    return grayscales

  def pixel_data(self, f, offset, width, height):
    f.seek(offset)

    padding_per_row = (width * 3) % 4

    grayscales = []
    for _ in range(height):
      result = self.read_pixel_row(f, width, padding_per_row)
      grayscales = grayscales + result

    assert len(grayscales) == (width * height), f'Wrong number of pixels: {len(grayscales)} (expected: {width * height})'

    return grayscales