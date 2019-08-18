import numpy as np

from numbers import Number
from typing  import Callable, Iterable, Union

from OpenGL.GL import *

from robot.common  import logger
from robot.spatial import Matrix4, Transform, Vector3

def vector_decorator(gl_function: int, vector_size: int) -> Callable:
  # TODO: Implement glUniform[1,2,4]xv functions
  assert vector_size == 3, "Only vectors of size 3 are implemented"

  def wrapper(location: int, values: Union[Vector3, Iterable]):
    if isinstance(values, Vector3):
      return gl_function(location, 1, values.xyz)
    elif isinstance(values, (list, tuple)):
      # See if we have a list of "vectors" or a list of numerical values
      if all([isinstance(v, (Vector3, list, tuple)) for v in values]):
        assert all(len(iterable) == vector_size for iterable in values), "All elements must be of size {vector_size}"
        # OpenGL expects a flat list of vector components
        components = [component for v in values for component in v]
        assert all([isinstance(component, Number) for component in components]), "All components must be numeric"

        return gl_function(location, len(values), components)
      elif all([isinstance(v, Number) for v in values]):
        assert len(values) == vector_size
        return gl_function(location, 1, values)
    else:
      raise TypeError(f'Unknown type {type(vectors)} given to Uniform setter')

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
  GL_INT:        glUniform1i,
  GL_FLOAT:      glUniform1f,
  GL_BOOL:       glUniform1i,
  GL_FLOAT_VEC3: vector_decorator(glUniform3fv, 3),
  GL_FLOAT_MAT4: matrix_decorator(glUniformMatrix4fv),
  GL_SAMPLER_2D: None
}

def setter_factory(gl_type: int, array_size: int) -> Callable:
  return GL_TYPE_UNIFORM_FN[gl_type]

class Uniform:
  def __init__(self, name: str, location: int, set_value: Callable) -> None:
    self.name         = name
    self.location     = location
    self.set_value = set_value
    self._value       = None

  @classmethod
  def from_program_index(cls, program_id: int, index: int) -> 'Uniform':
    """Construct a Uniform from the shader program id and the Uniform index."""
    properties = [GL_TYPE, GL_NAME_LENGTH, GL_LOCATION, GL_ARRAY_SIZE]

    gl_type, name_length, location, array_size = glGetProgramResourceiv(
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
      set_value = setter_factory(gl_type, array_size)
    except KeyError:
      raise KeyError(f'For {name}, unknown uniform type: {gl_type}')

    return cls(name, location, set_value)

  @property
  def value(self):
    return self._value

  @value.setter
  def value(self, value):
    self._value = value
    try:
      self.set_value(self.location, value)
    except TypeError:
      logger.error(f'When setting Uniform {self.name}, unknown type {type(value)} given.')