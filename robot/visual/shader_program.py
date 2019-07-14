from OpenGL.GL import *

from robot.visual.uniform import Uniform

class ShaderProgram():
  def __init__(self, files):
    self.uniforms = []
    self.program_id = glCreateProgram()

    if isinstance(files, str):
      vs_id, frag_id = self.compile_one_file(files)
    else:
      vs_id = self.add_shader(files[0], GL_VERTEX_SHADER)
      frag_id = self.add_shader(files[1], GL_FRAGMENT_SHADER)

    glAttachShader(self.program_id, vs_id)
    glAttachShader(self.program_id, frag_id)
    glLinkProgram(self.program_id)

    if glGetProgramiv(self.program_id, GL_LINK_STATUS) != GL_TRUE:
      info = glGetProgramInfoLog(self.program_id)
      glDeleteProgram(self.program_id)
      glDeleteShader(vs_id)
      glDeleteShader(frag_id)
      raise RuntimeError('Error linking program: %s' % (info))
    glDeleteShader(vs_id)
    glDeleteShader(frag_id)

    self.get_uniforms()

  def compile_one_file(self, file):
    vs_id = self.add_shader(file, GL_VERTEX_SHADER)
    frag_id = self.add_shader(file, GL_FRAGMENT_SHADER)

    return vs_id, frag_id

  def __getattr__(self, attribute):
    if attribute != 'uniforms' and attribute not in self.uniforms: 
      raise AttributeError

    return self.uniforms[attribute]

  def __setattr__(self, attribute, value):
    if attribute == 'uniforms' or attribute not in self.uniforms: 
      super(ShaderProgram, self).__setattr__(attribute, value)
    else:
      self.uniforms[attribute].value = value

  def get_uniforms(self):
    self.uniforms = {}

    num_uniforms = glGetProgramInterfaceiv(self.program_id, GL_UNIFORM, GL_ACTIVE_RESOURCES)

    for uniform_index in range(0, num_uniforms):
      uniform = Uniform(self.program_id, uniform_index)
    
      self.uniforms[uniform.name] = uniform

    

  def get_attributes(self):
    num_attributes = glGetProgramInterfaceiv(self.program_id, GL_PROGRAM_INPUT, GL_ACTIVE_RESOURCES)

    for attribute_index in range(0, num_attributes):
      attribute_props = [GL_TYPE, GL_NAME_LENGTH, GL_LOCATION, GL_ARRAY_SIZE]
      props_length = len(attribute_props)

      values = glGetProgramResourceiv(self.program_id, GL_PROGRAM_INPUT, attribute_index, props_length, attribute_props, props_length)
      gl_type = values[0]
      name = glGetProgramResourceName(self.program_id, GL_PROGRAM_INPUT, attribute_index, values[1])
      name = ''.join(list(map(chr, name))).strip('\x00').strip('[0]')
      location = values[2]
      array_size = values[3]

  def add_shader(self, filename, shader_type):
    # TODO: Need to handle other types of shaders I'm sure.
    shader_main = 'VERTEX' if shader_type == GL_VERTEX_SHADER else 'FRAGMENT'
    try:
      shader_id = glCreateShader(shader_type)
      with open(filename, 'r') as file:
        source = file.read()
        glShaderSource(shader_id, f'#version 330\n#define {shader_main}\n' + source)
        glCompileShader(shader_id)
        if glGetShaderiv(shader_id, GL_COMPILE_STATUS) != GL_TRUE:
          msg = glGetShaderInfoLog(shader_id).decode('unicode_escape')
          raise RuntimeError(f'Shader compilation failed: {msg}')
        return shader_id
    except:
      glDeleteShader(shader_id)
      raise

  def attribute_location(self, name):
    return glGetAttribLocation(self.program_id, name)