import numpy as np

from OpenGL.GL import *

from ctypes import c_void_p

from robot.mech.serial                     import Serial
from robot.spatial                         import Matrix4
from robot.visual.entities.entity          import Entity
from robot.visual.opengl.shader_program    import ShaderProgram
from robot.visual.opengl.buffer            import Buffer

class RobotEntity(Entity):
  def __init__(self, serial : Serial, shader_program : ShaderProgram = None, color = (1, 0.5, 0)):
    self.serial = serial
    self.frame_entity = None
    self.tool_entity = None

    Entity.__init__(self, shader_program, color)

    # TODO: Notice that this has to be after the Entity.__init__ call because I am replacing self.buffer
    self.buffer = Buffer.from_meshes(self.meshes)

  @property
  def meshes(self):
    return [link.mesh for link in self.serial.links]

  @property
  def aabb(self):
    return self.serial.aabb

  def attach(self, tool_entity: 'ToolEntity'):
    self.tool_entity = tool_entity
    self.tool_entity.robot_entity = self
    self.serial.attach(tool_entity.tool)

  def intersect(self, ray):
    return self.serial.intersect(ray)

  def load(self):
    if self.tool_entity:
      self.tool_entity.load()

    if self.frame_entity:
      self.frame_entity.load()

    self.buffer.set_attribute_locations(self.shader_program)
    self.buffer.load()

  def update(self, delta):
    # TODO: Move to more "direct" function calls, e.g.:
    # if not self.serial.is_moving():
    #   self.serial.reverse()
    if self.serial.traj:
      self.serial.angles = self.serial.traj.advance(delta)

      if self.serial.traj.is_done():
        self.serial.traj.reverse()
        self.serial.traj.restart()

    if self.tool_entity:
      self.tool_entity.update(delta)

  def draw(self):
    with self.shader_program as sp, self.buffer:
      sp.uniforms.model_matrices  = self.serial.poses()
      sp.uniforms.use_link_colors = False
      sp.uniforms.link_colors     = [link.color for link in self.serial.links]
      sp.uniforms.robot_color     = self.color

      glDrawArrays(GL_TRIANGLES, 0, len(self.buffer))

      if self.tool_entity:
        self.tool_entity.draw()

      if self.frame_entity:
        for link in self.serial.links:
          self.frame_entity.frame = link.to_world
          self.frame_entity.draw()

        if self.serial.tool:
          self.frame_entity.frame = self.serial.tool.tip
          self.frame_entity.draw()