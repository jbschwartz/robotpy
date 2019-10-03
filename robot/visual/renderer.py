import re

from collections import namedtuple
from typing      import Callable, Iterable, Type

from OpenGL.GL import *

from robot.common                    import logger, Timer
from robot.visual.messaging.listener import listen, listener
from robot.visual.messaging.event    import Event

from .opengl.buffer         import Buffer
from .opengl.shader_program import ShaderProgram
from .opengl.shader         import ShaderType

Entity = namedtuple('Entity', 'shader draw_mode buffer instances')

@listener
class Renderer():
  def __init__(self, camera, light):
    self.camera   = camera
    self.light    = light
    self.entities = {}
    self.shaders  = {}
    self.ubos     = []

  @listen(Event.START_RENDERER)
  def start(self) -> None:
    self.configure_opengl()
    self.bind_buffer_objects()
    self.load_buffers()

  def configure_opengl(self) -> None:
    glClearColor(1, 1, 1, 1)

    capabilities = [GL_DEPTH_TEST, GL_MULTISAMPLE, GL_BLEND, GL_CULL_FACE]
    for capability in capabilities:
      glEnable(capability)

    glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)
    glCullFace(GL_BACK)
    glFrontFace(GL_CCW)

  def bind_buffer_objects(self) -> None:
    for ubo in self.ubos:
      for shader in self.shaders.values():
        shader.bind_ubo(ubo)

  def load_buffers(self):
    for name, entity in self.entities.items():
      if len(entity.instances) == 0:
        logger.warn(f'Entity `{name}` has no instances')

      if not entity.buffer.is_procedural:
        entity.buffer.locate_attributes(entity.shader)
        entity.buffer.load()

  @listen(Event.START_FRAME)
  def frame(self):
    glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)

    self.load_buffer_objects()

  def load_buffer_objects(self):
    for ubo in self.ubos:
      ubo.load()

  @listen(Event.DRAW)
  def draw(self):
    self.update_environment()

    for entity_type, entity in self.entities.items():
      if entity_type.__name__.lower() in ['rectangle']:
        glDisable(GL_DEPTH_TEST)
      else:
        glEnable(GL_DEPTH_TEST)

      with entity.shader as sp, entity.buffer:
        for instance in entity.instances:
          if instance.visible:
            if getattr(instance, 'reload_buffer', False):
              entity.buffer.reload(instance.buffer)
              instance.reload_buffer = False

            instance.prepare(sp)

            glDrawArrays(entity.draw_mode, 0, len(entity.buffer))

  @listen(Event.WINDOW_RESIZE)
  def window_resize(self, width, height):
    if width and height:
      glViewport(0, 0, width, height)

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

  def register_entity_type(self, view_type: Type, buffer: Buffer, shader_name: str = None, draw_mode: int = None) -> None:
    name = view_type.__name__
    if self.entities.get(view_type, None) is not None:
      return logger.warn(f'Entity type `{name}` already registered. Keeping original values')

    # If shader name is not provided, assume it is the same name as the type
    shader_name = shader_name or re.sub('view$', '', name.lower())

    try:
      self.initialize_shader(shader_name)
    except FileNotFoundError:
      return logger.error(f'Entity type `{name}` creation failed')
    except RuntimeError as e:
      return logger.error(f'For `{name}`: {e}')

    self.entities[view_type] = Entity(
      shader       = self.shaders.get(shader_name),
      draw_mode    = draw_mode or GL_TRIANGLES,
      buffer       = buffer,
      instances    = [],
    )

  def add(self, instance) -> None:
    if type(instance) not in self.entities:
      return logger.error(f'No entity type `{type(instance).__name__}` found when adding entity')

    entity = self.entities.get(type(instance))
    entity.instances.append(instance)

    if len(instance.children) > 0:
      for child in instance.children:
        self.add(child)

  def add_many(self, instances: Iterable) -> None:
    for instance in instances:
      self.add(instance)

  def update_environment(self) -> None:
    self.light.position = self.camera.position