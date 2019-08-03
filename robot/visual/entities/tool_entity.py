import json, os
import numpy as np

dir_path = os.path.dirname(os.path.realpath(__file__))

from OpenGL.GL import *

from ctypes import c_void_p

from robot.mech.tool                       import Tool
from robot.spatial.transform               import Transform
from robot.visual.entities.entity          import Entity
from robot.visual.filetypes.stl.stl_parser import STLParser
from robot.visual.mesh                     import Mesh

def load(file_path: str) -> Tool:
  with open(file_path) as json_file:
    data = json.load(json_file)

  mesh_transform = Transform.from_json(data['mesh']['transform'])

  stl_parser = STLParser()
  mesh, *_ = Mesh.from_file(stl_parser, f'{dir_path}/../../mech/tools/meshes/{data["mesh"]["file"]}')

  mesh = mesh.scale(data["mesh"]["scale"])

  # Move the mesh onto a useful origin position if the modeler decided to include positional or rotational offsets
  mesh = mesh.transform(mesh_transform)

  tip_transform = Transform.from_json(data['tip_transform'])

  return ToolEntity(Tool(tip_transform, mesh), None, data['color'])

class ToolEntity(Entity):
  def __init__(self, tool : 'Tool', shader_program : 'ShaderProgram' = None, color = (1, 0.0, 0)):
    self.robot_entity = None
    self.tool   = tool
    Entity.__init__(self, shader_program, color)

  def build_buffer(self):
    data_list = []
    for facet in self.tool.mesh.facets:
      for vertex in facet.vertices:
        float_data = [*vertex, *(facet.normal)]

        data_list.append((float_data, 0))

    self.buffer = np.array(data_list, dtype=[('', np.float32, 6),('', np.int32, 1)])

  def load(self):
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
    pass

  def draw(self, camera, light):
    # TODO: Use Uniform Buffer Objects to remove this duplicate code from each entity
    self.shader_program.use()

    self.shader_program.proj_matrix = camera.projection.matrix
    self.shader_program.view_matrix = camera.world_to_camera

    self.shader_program.light_position  = light.position
    self.shader_program.light_color     = light.color
    self.shader_program.light_intensity = light.intensity

    self.shader_program.model_matrices  = self.tool.tool_to_world
    self.shader_program.use_link_colors = False
    self.shader_program.link_colors     = self.color
    self.shader_program.robot_color     = self.color

    glBindVertexArray(self.vao)

    glDrawArrays(GL_TRIANGLES, 0, self.buffer.size)

    glBindVertexArray(0)