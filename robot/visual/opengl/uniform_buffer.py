from collections import namedtuple
from OpenGL.GL   import *
from typing      import Iterable

import numpy as np

from robot.spatial import Matrix4, Vector3

Mapping = namedtuple('Mapping', 'object fields')

alignments = {
  float:    4,
  int:      4,
  Matrix4: 16,
  Vector3: 16
}

sizes = {
  float:    4,
  int:      4,
  Matrix4: 64,
  Vector3: 12
}

class UniformBuffer():
  def __init__(self, name: str, block_index: int):
    self.id = glGenBuffers(1)
    glBindBufferBase(GL_UNIFORM_BUFFER, block_index, self.id)

  def get_types(self, mapping: Mapping):
    return [type(getattr(mapping.object, field)) for field in mapping.fields]

  def calculate_padding(self, mapping: Mapping) -> Iterable[float]:
    """Return padding in bytes per field in Mapping."""
    paddings = []
    current = 0

    for field_type in self.get_types(mapping):
      alignment = alignments[field_type]
      offset_to_boundary = current % alignment

      size_in_bytes = sizes[field_type]
      assert size_in_bytes % 4 == 0, "Field size must be divisible by 4 since we're assuming padding is always in 4-byte chunks"

      if offset_to_boundary == 0:
        paddings.append(0)
        current += size_in_bytes
      else:
        padding_bytes = alignment - offset_to_boundary
        paddings.append(padding_bytes)
        current += size_in_bytes + padding_bytes

    return paddings

  def bind(self, mapping: Mapping):
    def fetcher():
      return [getattr(mapping.object, field) for field in mapping.fields]

    paddings = self.calculate_padding(mapping)

    def builder():
      values = []
      for padding, value in zip(paddings, fetcher()):
        values += [0] * (padding // 4)
        if isinstance(value, Vector3):
          values += [*value]
        elif isinstance(value, Matrix4):
          values += [*(value.elements)]
        elif isinstance(value, (int, float)):
          values += [value]
      return values

    self.builder = builder

  def load(self):
    data_buffer = np.array(self.builder(), dtype=np.float32)

    glBindBuffer(GL_UNIFORM_BUFFER, self.id)
    glBufferData(GL_UNIFORM_BUFFER, data_buffer.nbytes, data_buffer, GL_DYNAMIC_DRAW)
    glBindBuffer(GL_UNIFORM_BUFFER, 0)