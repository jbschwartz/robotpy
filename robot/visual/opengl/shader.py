import enum

from OpenGL.GL import *

# TODO: Need to handle other types of shaders I'm sure.
class ShaderTypes(enum.Enum):
  VERTEX   = GL_VERTEX_SHADER
  FRAGMENT = GL_FRAGMENT_SHADER

class Shader():
  def __init__(self, shader_type: ShaderTypes, path: str, version: int = 430) -> None:
    self.id          = None
    self.path        = path
    self.shader_type = shader_type
    self.version     = version

    self.load()

  def __del__(self):
    glDeleteShader(self.id)

  def create(self) -> None:
    self.id = glCreateShader(self.shader_type.value)

  def source(self) -> None:
    with open(self.path) as file:
      source = file.read()

    version_str = f'#version {self.version}'
    define_str  = f'#define {self.shader_type.name}'

    glShaderSource(self.id, '\n'.join([version_str, define_str, source]))

  def load(self) -> None:
    self.create()
    self.source()

    glCompileShader(self.id)

    if glGetShaderiv(self.id, GL_COMPILE_STATUS) != GL_TRUE:
      msg = glGetShaderInfoLog(self.id).decode('unicode_escape')
      raise RuntimeError(f'Shader compilation failed: {msg}')