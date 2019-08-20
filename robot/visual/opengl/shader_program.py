from OpenGL.GL import *

from .shader  import Shader, ShaderTypes
from .uniform import Uniform

class ShaderProgram():
  DEFAULT_FOLDER = './robot/visual/glsl/'
  DEFAULT_EXTENSION = '.glsl'

  def __init__(self, name:str = None, **names):
    # self.uniforms must be declared before any other properties
    # TODO: Make this not so
    self.uniforms = []

    self.id = glCreateProgram()

    # Use `name` for all shaders by default, replacing any specifically passed in
    # Also re-key the dictionary with ShaderType enum objects
    shader_names = {
      **{k: name for k in ShaderTypes},
      **{ShaderTypes[k.upper()]: name for k, name in names.items()}
    }

    self.link(shader_names)

    self.get_uniforms()

  def __del__(self):
    glDeleteProgram(self.id)

  def __getattr__(self, attribute):
    if attribute != 'uniforms' and attribute not in self.uniforms:
      raise AttributeError

    return self.uniforms[attribute]

  def __setattr__(self, attribute, value) -> None:
    if attribute == 'uniforms' or attribute not in self.uniforms:
      super(ShaderProgram, self).__setattr__(attribute, value)
    else:
      self.uniforms[attribute].value = value

  def link(self, shader_names: dict):
    self.attach_shaders(shader_names)

    glLinkProgram(self.id)

    if glGetProgramiv(self.id, GL_LINK_STATUS) != GL_TRUE:
      msg = glGetProgramInfoLog(self.id).decode('unicode_escape')
      raise RuntimeError(f'Error linking program: {msg}')

  def use(self) -> None:
    glUseProgram(self.id)

  def get_uniforms(self) -> None:
    self.uniforms = {}

    num_uniforms = glGetProgramInterfaceiv(self.id, GL_UNIFORM, GL_ACTIVE_RESOURCES)

    for uniform_index in range(num_uniforms):
      uniform = Uniform.from_program_index(self.id, uniform_index)

      self.uniforms[uniform.name] = uniform

  def get_uniform_block(self, name: str) -> int:
    result = glGetUniformBlockIndex(self.id, name)

    return result if result != GL_INVALID_INDEX else None

  def bind_ubo(self, name: str, binding_index: int) -> None:
    result = self.get_uniform_block(name)

    if result is not None:
      glUniformBlockBinding(self.id, result, binding_index)

  def attach_shaders(self, shaders : dict) -> None:
    get_path = lambda name: self.DEFAULT_FOLDER + name + self.DEFAULT_EXTENSION

    files = {k: get_path(name) for k, name in shaders.items()}

    for shader_type, file_path in files.items():
      shader = Shader(shader_type, file_path)
      glAttachShader(self.id, shader.id)

  def attribute_location(self, name: str) -> int:
    return glGetAttribLocation(self.id, name)