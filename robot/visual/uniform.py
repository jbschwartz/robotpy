import numpy as np
from OpenGL.GL import *

from robot.spatial.matrix4   import Matrix4
from robot.spatial.transform import Transform
from robot.spatial.vector3   import Vector3

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
        matrix = Matrix4(transforms)
      elif isinstance(transforms, Matrix4):
        matrix = transforms

      return gl_function(location, 1, False, np.array(matrix.elements, dtype=np.float32))

    assert all(map(lambda m: isinstance(m, (Transform, Matrix4)), transforms))

    matrices = list(map(lambda t: Matrix4(t) if isinstance(t, Transform) else t, transforms))

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
  def __init__(self, program_id, index):
    self.program_id = program_id
    self.index = index

    uniform_props = [GL_TYPE, GL_NAME_LENGTH, GL_LOCATION, GL_ARRAY_SIZE]
    props_length = len(uniform_props)

    values = glGetProgramResourceiv(self.program_id, GL_UNIFORM, self.index, props_length, uniform_props, props_length)
    self.gl_type = values[0]
    self.name = self.get_name(values[1])
    self.location = values[2]
    self.array_size = values[3]

    try:
      self.set_function = GL_TYPE_UNIFORM_FN[self.gl_type]
    except KeyError:
      raise Exception(f'Unknown uniform GL_TYPE value: {self.gl_type} ({self.name})')

  def get_name(self, length):
    return self.ascii_list_to_string(glGetProgramResourceName(self.program_id, GL_UNIFORM, self.index, length))

  def ascii_list_to_string(self, ascii_list):
    return ''.join(list(map(chr, ascii_list))).strip('\x00').strip('[0]')

  def value(self, *args):
    self.set_function(self.location, *args)
  
  # value property has no need for a getter
  value = property(None, value)
