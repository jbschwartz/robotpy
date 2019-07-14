import enum

from OpenGL.GL import *

from robot.visual.uniform import Uniform

# TODO: Need to handle other types of shaders I'm sure.
class ShaderTypes(enum.Enum):
  VERTEX   = GL_VERTEX_SHADER
  FRAGMENT = GL_FRAGMENT_SHADER

class Shader():
  def __init__(self, shader_type, path, version = 430):
    self.id          = None
    self.path        = path
    self.shader_type = shader_type
    self.version     = version

    self.load()

  def __del__(self):
    glDeleteShader(self.id)

  def create(self):
    self.id = glCreateShader(self.shader_type.value)

  def source(self):
    with open(self.path) as file:
      source = file.read()

    version_str = f'#version {self.version}'
    define_str  = f'#define {self.shader_type.name}'

    glShaderSource(self.id, '\n'.join([version_str, define_str, source]))

  def load(self):
    self.create()
    self.source()

    glCompileShader(self.id)

    if glGetShaderiv(self.id, GL_COMPILE_STATUS) != GL_TRUE:
      msg = glGetShaderInfoLog(self.id).decode('unicode_escape')
      raise RuntimeError(f'Shader compilation failed: {msg}')

class ShaderProgram():
  DEFAULT_FOLDER = './robot/visual/glsl/'
  DEFAULT_EXTENSION = '.glsl'

  def __init__(self, name=None, **names):
    self.uniforms = []
    self.program_id = glCreateProgram()

    # Use `name` for all shaders by default, replacing any specifically passed in
    # Also re-key the dictionary with ShaderType enum objects
    self.shader_names = {
      **{k: name for k in ShaderTypes}, 
      **{ShaderTypes[k.upper()]: name for k, name in names.items()}
    }

    shaders = self.create_shaders(self.shader_names)

    [glAttachShader(self.program_id, shader.id) for shader in shaders] 

    glLinkProgram(self.program_id)

    if glGetProgramiv(self.program_id, GL_LINK_STATUS) != GL_TRUE:
      info = glGetProgramInfoLog(self.program_id)
      glDeleteProgram(self.program_id)
      [shader.delete() for shader in shaders] 

      raise RuntimeError('Error linking program: %s' % (info))
    
    [shader.delete() for shader in shaders] 

    self.get_uniforms()

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

  def create_shaders(self, shaders : dict):
    get_path = lambda name: self.DEFAULT_FOLDER + name + self.DEFAULT_EXTENSION

    files = {k: get_path(name) for k, name in shaders.items()}

    return (Shader(shader_type, file_path) for shader_type, file_path in files.items())

  def attribute_location(self, name):
    return glGetAttribLocation(self.program_id, name)