from OpenGL.GL import *

GL_TYPE_UNIFORM_FN = {
  GL_INT:        glUniform1iv,
  GL_FLOAT:      glUniform1f,
  GL_BOOL:       glUniform1i,
  GL_FLOAT_VEC3: glUniform3fv,
  GL_FLOAT_MAT4: glUniformMatrix4fv,
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

  def set_value(self, *args):
    self.set_function(self.location, *args)

