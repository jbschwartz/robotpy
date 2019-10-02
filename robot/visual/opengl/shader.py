import enum

from OpenGL.GL import *

# TODO: Need to handle other types of shaders I'm sure.
class ShaderType(enum.Enum):
  VERTEX   = GL_VERTEX_SHADER
  FRAGMENT = GL_FRAGMENT_SHADER
  # TODO: Add GEOMETRY and see what happens.

class Shader():
  def __init__(self, shader_type: ShaderType, full_source: str, version: int = 430) -> None:
    self.id = glCreateShader(shader_type.value)

    self.compile_shader(shader_type.name, full_source, version)

  def __del__(self):
    glDeleteShader(self.id)

  def compile_shader(self, shader_type: str, full_source: str, version: int) -> None:
    version_str = f'#version {version}'
    define_str  = f'#define {shader_type}'

    glShaderSource(self.id, '\n'.join([version_str, define_str, full_source]))

    glCompileShader(self.id)

    if glGetShaderiv(self.id, GL_COMPILE_STATUS) != GL_TRUE:
      msg = glGetShaderInfoLog(self.id).decode('unicode_escape')
      raise RuntimeError(f'{shader_type.capitalize()} shader compilation failed: {msg}')