from collections import namedtuple
from typing      import Callable, Iterable

from OpenGL.GL import *

from robot.common                    import logger, Timer
from robot.visual.messaging.listener import listen, listener
from robot.visual.messaging.event    import Event

from .opengl.buffer         import Buffer
from .opengl.shader_program import ShaderProgram
from .opengl.shader         import ShaderType
from .opengl.uniform_buffer import UniformBuffer

Entity = namedtuple('Entity', 'name shader draw_mode buffer instances per_instance')

@listener
class Renderer():
  def __init__(self):
    self.entities = {}
    self.shaders  = {}
    self.ubos     = []

  def initialize_shader(self, shader_name: str) -> None:
    if shader_name in self.shaders:
      return

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
        logger.error(f'Shader program `{shader_name}` not found')
        raise

  @listen(Event.START_FRAME)
  def start_frame(self):
    glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)

  @listen(Event.START_FRAME)
  def load_buffer_objects(self):
    for ubo in self.ubos:
      ubo.load()

  @listen(Event.START_RENDERER)
  def start_renderer(self):
    glClearColor(1, 1, 1, 1)

    capabilities = [GL_DEPTH_TEST, GL_MULTISAMPLE, GL_BLEND, GL_CULL_FACE]
    for capability in capabilities:
      glEnable(capability)

    glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)
    glCullFace(GL_BACK)
    glFrontFace(GL_CCW)

  @listen(Event.START_RENDERER)
  def bind_buffer_objects(self) -> None:
    for ubo in self.ubos:
      for shader in self.shaders.values():
        shader.bind_ubo(ubo)

  @listen(Event.START_RENDERER)
  def load_buffers(self):
    for entity in self.entities.values():
      if len(entity.instances) == 0:
        logger.warn(f'Entity `{entity.name}` has no instances')

      if not entity.buffer.is_procedural:
        entity.buffer.set_attribute_locations(entity.shader)
        entity.buffer.load()

  def add(self, entity_type: str, instance, parent = None, **kwargs) -> None:
    entity = self.entities.get(entity_type, None)
    if entity is None:
      return logger.error(f'No entity type `{entity_type}` found when adding entity')

    entity.instances.append((
      instance,
      kwargs
    ))

  def register_entity_type(self, name: str, buffer: Buffer, per_instance: Callable, shader_name: str = None, draw_mode: int = None) -> None:
    if self.entities.get(name, None) is not None:
      return logger.warn(f'Entity type `{name}` already registered. Keeping original values')

    # If shader name is not provided, assume it is the same name as the entity
    shader_name = shader_name or name

    try:
      self.initialize_shader(shader_name)
    except FileNotFoundError:
      return logger.error(f'Entity type `{name}` creation failed')

    self.entities[name] = Entity(
      name         = name,
      shader       = self.shaders.get(shader_name),
      draw_mode    = draw_mode or GL_TRIANGLES,
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

          glDrawArrays(entity.draw_mode, 0, len(entity.buffer))

  @listen(Event.WINDOW_RESIZE)
  def window_resize(self, width, height):
    if width and height:
      glViewport(0, 0, width, height)