from collections import namedtuple
from OpenGL.GL   import *
from typing      import Iterable

import numpy as np

from spatial import Matrix4, Transform, Vector3

Mapping = namedtuple('Mapping', 'object fields')
Field   = namedtuple('Field', 'underlying_type alignment size_in_bytes')

alignments = {
  float:      4,
  int:        4,
  Matrix4:   16,
  Transform: 16,
  Vector3:   16
}

sizes = {
  float:      4,
  int:        4,
  Matrix4:   64,
  Transform: 64,
  Vector3:   12
}

class UniformBuffer():
  """OpenGL Uniform Buffer Object."""
  def __init__(self, name: str, binding_index: int) -> None:
    self.id            = glGenBuffers(1)  # OpenGL buffer ID
    self.name          = name
    self.binding_index = binding_index

    glBindBufferBase(GL_UNIFORM_BUFFER, self.binding_index, self.id)

  def resolve_dot_notation(self, start_object, field):
    current = start_object
    for attr in field.split('.'):
      current = getattr(current, attr)

    return current

  def fields(self, mapping: Mapping):
    fields = []
    for field in mapping.fields:
      underlying_type = type(self.resolve_dot_notation(mapping.object, field))
      fields.append(Field(underlying_type, alignments[underlying_type], sizes[underlying_type]))

      assert fields[-1].size_in_bytes % 4 == 0, "Field size must be divisible by 4 since we're only padding with 4-byte floats"

    return fields

  def calculate_padding(self, fields: Iterable[Field]) -> Iterable[float]:
    """Return padding in bytes per field based on alignment requirements."""
    paddings = []
    current = 0

    for field in fields:
      offset_to_boundary = current % field.alignment
      current += field.size_in_bytes

      if offset_to_boundary == 0:
        paddings.append(0)
      else:
        padding_bytes = field.alignment - offset_to_boundary
        paddings.append(padding_bytes)
        current += padding_bytes

    return paddings

  def bind(self, mapping: Mapping):
    def fetcher():
      return [self.resolve_dot_notation(mapping.object, field) for field in mapping.fields]

    paddings = self.calculate_padding(self.fields(mapping))

    def builder():
      values = []
      for padding, value in zip(paddings, fetcher()):
        values += [0] * (padding // 4)
        if isinstance(value, Vector3):
          values += [*value]
        elif isinstance(value, Matrix4):
          values += [*(value.elements)]
        elif isinstance(value, Transform):
          matrix = Matrix4.from_transform(value)
          values += [*(matrix.elements)]
        elif isinstance(value, (int, float)):
          values += [value]
      return values

    self.builder = builder

  def load(self):
    data_buffer = np.array(self.builder(), dtype=np.float32)

    glBindBuffer(GL_UNIFORM_BUFFER, self.id)
    glBufferData(GL_UNIFORM_BUFFER, data_buffer.nbytes, data_buffer, GL_DYNAMIC_DRAW)
    glBindBuffer(GL_UNIFORM_BUFFER, 0)
