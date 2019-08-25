from typing import Iterable

from robot.common                    import Timer
from robot.visual.messaging.listener import listen, listener
from robot.visual.messaging.event    import Event

from .opengl.shader_program import ShaderProgram
from .opengl.shader         import ShaderType
from .opengl.uniform_buffer import UniformBuffer

@listener
class Renderer():
  def __init__(self):
    self.shaders = {}
    self.ubos    = []

  def initialize_shaders(self, shader_names: Iterable[str]) -> None:
    self.shaders = {}
    with Timer('Initialize Shaders'):
      for shader_name in shader_names:
        try:
          self.shaders[shader_name] = ShaderProgram.from_file_name(shader_name)
        except FileNotFoundError:
          # Single file not found. Instead look for individual files.
          abbreviation = lambda type_name: type_name[0].lower()

          file_names = {
            shader_type: f"{shader_name}_{abbreviation(shader_type.name)}"
            for shader_type in ShaderType
          }

          try:
            self.shaders[shader_name] = ShaderProgram.from_file_names(shader_name, file_names)
          except FileNotFoundError:
            # TODO: Log this and wait to throw until we know it is being used?
            pass

  @listen(Event.START_FRAME)
  def load_buffer_objects(self):
    for ubo in self.ubos:
      ubo.load()

  @listen(Event.START_RENDERER)
  def bind_buffer_objects(self) -> None:
    for ubo in self.ubos:
      for shader in self.shaders.values():
        shader.bind_ubo(ubo)
