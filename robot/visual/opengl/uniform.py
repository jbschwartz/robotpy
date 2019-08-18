from typing  import Callable

from OpenGL.GL import *

from robot.common  import logger
import robot.visual.opengl.decorators as decorators

GL_TYPE_UNIFORM_FN = {
  GL_INT:        decorators.primative(glUniform1iv),
  GL_FLOAT:      decorators.primative(glUniform1fv),
  GL_BOOL:       decorators.primative(glUniform1iv),
  GL_FLOAT_VEC3: decorators.vector(glUniform3fv, 3),
  GL_FLOAT_MAT4: decorators.matrix(glUniformMatrix4fv, 4),
  GL_SAMPLER_2D: None
}

def setter_factory(gl_type: int, array_size: int) -> Callable:
  array_decorator = GL_TYPE_UNIFORM_FN.get(gl_type, None)

  if array_decorator is not None:
    return array_decorator(array_size)
  else:
    return None

class Uniform:
  def __init__(self, name: str, location: int, set_value: Callable) -> None:
    self.name         = name
    self.location     = location
    self.set_value    = set_value
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
    if self.set_value is None:
      return logger.error(f'Setting a value on unsettable Uniform {self.name}')

    self._value = value
    try:
      self.set_value(self.location, value)
    except TypeError:
      logger.error(f'When setting Uniform {self.name}, unknown type {type(value)} given.')