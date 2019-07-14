from OpenGL.GL import *

from robot.visual.uniform import Uniform

class Shader():
  # TODO: Need to handle other types of shaders I'm sure.
  DEFINES = {
    GL_VERTEX_SHADER:   'VERTEX',
    GL_FRAGMENT_SHADER: 'FRAGMENT'
  }

  def __init__(self, path, shader_type, version = 430):
    self.id          = None
    self.path        = path
    self.shader_type = shader_type
    self.version     = version

    self.load()

  def create(self):
    self.id = glCreateShader(self.shader_type)

  def source(self):
    with open(self.path) as file:
      source = file.read()

    version_str = f'#version {self.version}'
    define_str  = f'#define {self.DEFINES[self.shader_type]}'

    glShaderSource(self.id, '\n'.join([version_str, define_str, source]))

  def load(self):
    self.create()
    self.source()

    glCompileShader(self.id)

    if glGetShaderiv(self.id, GL_COMPILE_STATUS) != GL_TRUE:
      msg = glGetShaderInfoLog(self.id).decode('unicode_escape')
      self.delete()
      raise RuntimeError(f'Shader compilation failed: {msg}')

  def delete(self):
    glDeleteShader(self.id)

class ShaderProgram():
  DEFAULT_FOLDER = './robot/visual/glsl/'
  DEFAULT_EXTENSION = '.glsl'

  def __init__(self, files):
    self.uniforms = []
    self.program_id = glCreateProgram()

    if isinstance(files, str):
      vs_id, frag_id = self.compile_one_file(files)
    else:
      vs_id = self.add_shader(files[0], GL_VERTEX_SHADER)
      frag_id = self.add_shader(files[1], GL_FRAGMENT_SHADER)

    shaders = [vs_id, frag_id]

    [glAttachShader(self.program_id, shader.id) for shader in shaders] 

    glLinkProgram(self.program_id)

    if glGetProgramiv(self.program_id, GL_LINK_STATUS) != GL_TRUE:
      info = glGetProgramInfoLog(self.program_id)
      glDeleteProgram(self.program_id)
      [shader.delete() for shader in shaders] 

      raise RuntimeError('Error linking program: %s' % (info))
    
    [shader.delete() for shader in shaders] 

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

  def add_shader(self, name, shader_type):
    path = self.DEFAULT_FOLDER + name + self.DEFAULT_EXTENSION
    return Shader(path, shader_type)

  def attribute_location(self, name):
    return glGetAttribLocation(self.program_id, name)