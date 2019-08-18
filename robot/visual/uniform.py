import numpy as np

from typing import Callable

from OpenGL.GL import *

from robot.spatial import Matrix4, Transform, Vector3

def scalar_decorator(gl_function):
  def wrapper(location, *args):
    return gl_function(location, *args)

  return wrapper

def vector_decorator(gl_function):
  def wrapper(location, vectors):
    # TODO: Better type/size checking
    # This entire function is actually broken since there are glUniform[1,2,3,4]x functions
    # This assumes it's always 3
    if isinstance(vectors, Vector3):
      return gl_function(location, 1, [*vectors])
    elif isinstance(vectors, (list, tuple)):
      if not any(map(lambda v: isinstance(v, (Vector3, list, tuple)), vectors)):
        return gl_function(location, 1, [*vectors])

    assert isinstance(vectors, (list, tuple))
    assert all(map(lambda v: isinstance(v, (Vector3, list, tuple)), vectors))

    # OpenGL expects a flat list of vector components
    components = [comp for v in vectors for comp in v]
    return gl_function(location, len(vectors), components)

  return wrapper

def matrix_decorator(gl_function):
  def wrapper(location, transforms):
    # TODO: Better type/size checking
    # This entire function is actually broken since there are glUniformMatrix[1,2,3,4]x functions
    # This assumes it's always 4
    if not isinstance(transforms, list):
      if isinstance(transforms, Transform):
        matrix = Matrix4.from_transform(transforms)
      elif isinstance(transforms, Matrix4):
        matrix = transforms

      return gl_function(location, 1, False, np.array(matrix.elements, dtype=np.float32))

    assert all(map(lambda m: isinstance(m, (Transform, Matrix4)), transforms))

    matrices = list(map(lambda t: Matrix4.from_transform(t) if isinstance(t, Transform) else t, transforms))

    # OpenGL expects a flat list of matrix elements
    elements = [elem for m in matrices for elem in m.elements]
    # Matrix4 stores elements column-major so transposing is never necessary for OpenGL
    return gl_function(location, len(matrices), False, elements)

  return wrapper

GL_TYPE_UNIFORM_FN = {
  GL_INT:        scalar_decorator(glUniform1iv),
  GL_FLOAT:      scalar_decorator(glUniform1f),
  GL_BOOL:       scalar_decorator(glUniform1i),
  GL_FLOAT_VEC3: vector_decorator(glUniform3fv),
  GL_FLOAT_MAT4: matrix_decorator(glUniformMatrix4fv),
  GL_SAMPLER_2D: None
}

class Uniform:
  def __init__(self, name: str, location: int, set_function: Callable) -> None:
    self.name         = name
    self.location     = location
    self.set_function = set_function
    self._value       = None

  @classmethod
  def from_program_index(cls, program_id: int, index: int) -> 'Uniform':
    """Construct a Uniform from the shader program id and the Uniform index."""
    properties = [GL_TYPE, GL_NAME_LENGTH, GL_LOCATION]

    gl_type, name_length, location = glGetProgramResourceiv(
      program_id,
      GL_UNIFORM,
      index,
      len(properties),
      properties,
      len(properties)
    )

    # Returns a list of ascii values including NUL terminator and [0] for uniform arrays
    name_ascii = glGetProgramResourceName(program_id, GL_UNIFORM, index, name_length)

    # Format the name as a useful string
    name = ''.join(chr(c) for c in name_ascii).strip('\x00').strip('[0]')

    try:
      set_function = GL_TYPE_UNIFORM_FN[gl_type]
    except KeyError:
      raise KeyError(f'For {name}, unknown uniform type: {gl_type}')

    return cls(name, location, set_function)

  @property
  def value(self):
    return self._value

  @value.setter
  def value(self, *args):
    self._value = args
    self.set_function(self.location, *args)