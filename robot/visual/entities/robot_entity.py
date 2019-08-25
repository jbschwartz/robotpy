import numpy as np

from OpenGL.GL import *

from ctypes import c_void_p

from robot.mech.serial                     import Serial
from robot.spatial                         import Matrix4
from robot.visual.entities.entity          import Entity
from robot.visual.opengl.shader_program           import ShaderProgram

class RobotEntity(Entity):
  def __init__(self, serial : Serial, shader_program : ShaderProgram = None, color = (1, 0.5, 0)):
    self.serial = serial
    self.frame_entity = None
    self.tool_entity = None

    Entity.__init__(self, shader_program, color)

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

  def build_buffer(self):
    data_list = []
    for index, mesh in enumerate(self.meshes):
      for facet in mesh.facets:
        for vertex in facet.vertices:
          float_data = [*vertex, *(facet.normal)]

          data_list.append((float_data, index))

    self.buffer = np.array(data_list, dtype=[('', np.float32, 6),('', np.int32, 1)])

  def load(self):
    if self.tool_entity:
      self.tool_entity.load()

    if self.frame_entity:
      self.frame_entity.load()

    self.build_buffer()

    glBindVertexArray(self.vao)

    glBindBuffer(GL_ARRAY_BUFFER, self.vbo)
    glBufferData(GL_ARRAY_BUFFER, self.buffer.nbytes, self.buffer, GL_STATIC_DRAW)

    glVertexAttribPointer(self.shader_program.attribute_location('vin_position'), 3, GL_FLOAT, GL_FALSE, 28, None)
    glEnableVertexAttribArray(self.shader_program.attribute_location('vin_position'))

    glVertexAttribPointer(self.shader_program.attribute_location('vin_normal'), 3, GL_FLOAT, GL_FALSE, 28, c_void_p(12))
    glEnableVertexAttribArray(self.shader_program.attribute_location('vin_normal'))

    glVertexAttribIPointer(self.shader_program.attribute_location('vin_mesh_index'), 1, GL_INT, 28, c_void_p(24))
    glEnableVertexAttribArray(self.shader_program.attribute_location('vin_mesh_index'))

    glBindBuffer(GL_ARRAY_BUFFER, 0)
    glBindVertexArray(0)

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
    with self.shader_program as sp:
      sp.uniforms.model_matrices  = self.serial.poses()
      sp.uniforms.use_link_colors = False
      sp.uniforms.link_colors     = [link.color for link in self.serial.links]
      sp.uniforms.robot_color     = self.color

      glBindVertexArray(self.vao)

      glDrawArrays(GL_TRIANGLES, 0, self.buffer.size)

      glBindVertexArray(0)

      if self.tool_entity:
        self.tool_entity.draw()

      if self.frame_entity:
        for link in self.serial.links:
          self.frame_entity.frame = link.to_world
          self.frame_entity.draw()

        if self.serial.tool:
          self.frame_entity.frame = self.serial.tool.tip
          self.frame_entity.draw()