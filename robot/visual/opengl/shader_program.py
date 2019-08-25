from OpenGL.GL import *

from typing import Iterable

from robot.common  import FrozenDict, logger
from .shader       import Shader, ShaderType
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

  def __init__(self, name, shaders: Iterable[Shader]) -> None:
    self.id = glCreateProgram()

    #  Used for warning/error messaging
    self.name = name

    for shader in shaders:
      glAttachShader(self.id, shader.id)

    self.link()

    self.uniforms = UniformDict.from_program(self.id)

  @classmethod
  def get_shader_file_path(cls, file_name: str) -> str:
    return cls.DEFAULT_FOLDER + file_name + cls.DEFAULT_EXTENSION

  @classmethod
  def from_file_name(cls, file_name: str) -> 'ShaderProgram':
    """Open a glsl file with the given file name and create a ShaderProgram."""
    with open(cls.get_shader_file_path(file_name)) as file:
      source = file.read()

    shaders = [Shader(shader_type, source) for shader_type in ShaderType]

    return cls(file_name, shaders)

  @classmethod
  def from_file_names(cls, shader_name: str, file_names_by_type: dict) -> 'ShaderProgram':
    shaders = []
    for shader_type, file_name in file_names_by_type.items():
      with open(cls.get_shader_file_path(file_name)) as file:
        source = file.read()

      shaders.append(
        Shader(shader_type, source)
      )

    return cls(shader_name, shaders)


  def __del__(self):
    glDeleteProgram(self.id)

  def link(self):
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

  def attribute_location(self, name: str) -> int:
    return glGetAttribLocation(self.id, name)