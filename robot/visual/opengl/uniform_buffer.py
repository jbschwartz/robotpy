from collections import namedtuple
from OpenGL.GL   import *

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
  def __init__(self):
    self.id = glGenBuffers(1)
    glBindBufferBase(GL_UNIFORM_BUFFER, 2, self.id)

  def bind(self, mapping: Mapping):
    paddings = [0]
    current = sizes[type(getattr(mapping.object, mapping.fields[0]))]
    for field in mapping.fields[1:]:
      value = type(getattr(mapping.object, field))
      alignment = alignments[value]
      mod = current % alignment
      if mod == 0:
        paddings.append(0)
      else:
        paddings.append((alignment - mod) // 4)
      current += sizes[value]

    print(paddings)

    def fetcher():
      return [getattr(mapping.object, field) for field in mapping.fields]

    def builder():
      values = []
      for padding, value in zip(paddings, fetcher()):
        values += [0] * padding
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