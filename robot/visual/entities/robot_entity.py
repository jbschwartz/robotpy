import json, math
import numpy as np

from OpenGL.GL import *

from ctypes import c_void_p

from ..mesh           import Mesh
from ..shader_program import ShaderProgram

from robot.mech              import Joint, Link, Serial
from robot.spatial           import Matrix4
from robot.visual.exceptions import ParserError
from robot.visual.filetypes  import STLParser

def load(filename):
  joints = []
  links = []
  with open(filename) as json_file:  
    data = json.load(json_file)

    for joint_params in data['joints']:
      for param, value in joint_params.items():
        if param == 'limits':
          value['low'] = math.radians(value['low'])
          value['high'] = math.radians(value['high'])
        elif param in ['alpha', 'theta']:
          joint_params[param] = math.radians(value)

      joints.append(Joint(**joint_params))

    for link_parameters in data['links']:
      link_parameters['mesh_file'] = data['mesh_file']
      links.append(Link(**link_parameters))

    p = STLParser()

    try:
      meshes = p.parse(f'robot/mech/robots/meshes/{data["mesh_file"]}')
    except ParserError as error:
      print('\033[91m' + f'Parsing error on line {error.line}: {error}' + '\033[0m')
      quit()

  return RobotEntity(Serial(joints, links), meshes)

class RobotEntity():
  def __init__(self, serial : Serial, meshes, shader_program : ShaderProgram = None):
    self.vao = -1 if not bool(glGenVertexArrays) else glGenVertexArrays(1)
    self.vbo = -1 if not bool(glGenBuffers) else glGenBuffers(1)
    self.buffer = []
    self.shader_program = shader_program

    self.serial = serial
    self.meshes = meshes

    self.link_colors = [
      (0.5, 0.15, 0.85),
      (0.25, 0.25, 1),
      (0.5, 0.25, 1),
      (1, 1, 0),
      (1, 0, 1),
      (0, 1, 1),
      (0.5, 1, 0.25)
    ]

    self.link_matricies = np.array([], dtype=np.float32)

  def use_shader(self, shader_program):
    self.shader_program = shader_program

  def build_buffer(self):
    data_list = []
    for index, mesh in enumerate(self.meshes):
      for facet in mesh.facets:
        for vertex in facet.vertices:
          float_data = [*vertex, *(facet.normal)]

          data_list.append((float_data, index))

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
    if self.serial.traj.is_done():
      self.serial.traj.reverse()

    self.serial.qs = self.serial.traj.advance(delta)
    
    transforms = self.serial.current_transforms()

    matrix_floats = []
    for transform in transforms:
      matrix = Matrix4(transform)
      matrix_floats.extend(matrix.elements)

    self.link_matricies = np.array(matrix_floats, dtype=np.float32)

  def draw(self):
    self.shader_program.uniforms['model_matrices'].set_value(7, GL_FALSE, self.link_matricies)

    self.shader_program.uniforms['use_link_colors'].set_value(GL_FALSE)
    self.shader_program.uniforms['link_colors'].set_value(7, self.link_colors)
    self.shader_program.uniforms['robot_color'].set_value(1, 0.5, 0, 0.5)

    glBindVertexArray(self.vao)

    glDrawArrays(GL_TRIANGLES, 0, self.buffer.size)

    glBindVertexArray(0)