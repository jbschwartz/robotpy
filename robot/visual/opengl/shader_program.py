from OpenGL.GL import *

from robot.common  import FrozenDict, logger
from .shader       import Shader, ShaderTypes
from .uniform      import Uniform

class UniformDict():
  def __init__(self, d: dict) -> None:
    self.__dict__['_uniforms']       = FrozenDict(d)
    self.__dict__['_already_logged'] = []

  @classmethod
  def from_program(cls, program_id: int) -> 'UniformDict':
    uniforms = {}

    num_uniforms = glGetProgramInterfaceiv(program_id, GL_UNIFORM, GL_ACTIVE_RESOURCES)

    for uniform_index in range(num_uniforms):
      uniform = Uniform.from_program_index(program_id, uniform_index)

      uniforms[uniform.name] = uniform

    return cls(uniforms)

  def __getattr__(self, name):
    return getattr(self._uniforms, name)

  def __setattr__(self, name, value):
    try:
      uniform = getattr(self._uniforms, name)
      uniform.value = value
    except AttributeError:
      if name not in self._already_logged:
        self._already_logged.append(name)
        logger.warning(f'Setting uniform {name} that does not exist')

class ShaderProgram():
  DEFAULT_FOLDER = './robot/visual/glsl/'
  DEFAULT_EXTENSION = '.glsl'

  def __init__(self, name:str = None, **names):
    self.id = glCreateProgram()

    # Use `name` for all shaders by default, replacing any specifically passed in
    # Also re-key the dictionary with ShaderType enum objects
    shader_names = {
      **{k: name for k in ShaderTypes},
      **{ShaderTypes[k.upper()]: name for k, name in names.items()}
    }

    #  Used for warning/error messaging
    self.name = name or '/'.join(shader_names.values())

    self.link(shader_names)

    self.uniforms = UniformDict.from_program(self.id)

  def __del__(self):
    glDeleteProgram(self.id)

  def link(self, shader_names: dict):
    self.attach_shaders(shader_names)

    glLinkProgram(self.id)

    if glGetProgramiv(self.id, GL_LINK_STATUS) != GL_TRUE:
      msg = glGetProgramInfoLog(self.id).decode('unicode_escape')
      raise RuntimeError(f'Error linking program: {msg}')

  def use(self) -> None:
    glUseProgram(self.id)

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