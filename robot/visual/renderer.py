from collections import namedtuple
from typing      import Callable, Iterable

from OpenGL.GL import glDrawArrays, GL_TRIANGLES

from robot.common                    import logger, Timer
from robot.visual.messaging.listener import listen, listener
from robot.visual.messaging.event    import Event

from .opengl.buffer         import Buffer
from .opengl.shader_program import ShaderProgram
from .opengl.shader         import ShaderType
from .opengl.uniform_buffer import UniformBuffer

Entity = namedtuple('Entity', 'name shader buffer instances per_instance')

@listener
class Renderer():
  def __init__(self):
    self.entities = {}
    self.shaders  = {}
    self.ubos     = []

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

  @listen(Event.START_RENDERER)
  def load_buffers(self):
    for entity in self.entities.values():
      entity.buffer.set_attribute_locations(entity.shader)
      entity.buffer.load()

  def add(self, entity_type: str, instance, parent = None, **kwargs) -> None:
    entity = self.entities.get(entity_type, None)
    if entity is None:
      return logger.error(f'No entity type `{entity_type}` found')

    entity.instances.append((
      instance,
      kwargs
    ))

  def register_entity_type(self, name: str, shader_name: str, buffer: Buffer, per_instance: Callable) -> None:
    if self.entities.get(name, None) is not None:
      return logger.warn(f'Entity type `{name}` already registered.')

    shader = self.shaders.get(name, None)
    if shader is None:
      return logger.error(f'Shader program `{shader_name}` not found when registering entity type `{name}`')

    self.entities[name] = Entity(
      name         = name,
      shader       = shader,
      buffer       = buffer,
      instances    = [],
      per_instance = per_instance
    )

  @listen(Event.DRAW)
  def draw(self):
    for entity in self.entities.values():
      with entity.shader as sp, entity.buffer:
        for instance, kwargs in entity.instances:
          entity.per_instance(instance, sp, **kwargs)

          glDrawArrays(GL_TRIANGLES, 0, len(entity.buffer))