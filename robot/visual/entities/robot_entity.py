import json, math
import numpy as np

from OpenGL.GL import *

from ctypes import c_void_p

from robot.mech.joint                      import Joint
from robot.mech.link                       import Link
from robot.mech.serial                     import Serial
from robot.spatial.frame                   import Frame
from robot.spatial.matrix4                 import Matrix4
from robot.spatial.vector3                 import Vector3
from robot.visual.exceptions               import ParserError
from robot.visual.filetypes.stl.stl_parser import STLParser
from robot.visual.mesh                     import Mesh
from robot.visual.shader_program           import ShaderProgram

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
  def __init__(self, serial : Serial, meshes, shader_program : ShaderProgram = None, color = (1, 0.5, 0)):
    self.vao = -1 if not bool(glGenVertexArrays) else glGenVertexArrays(1)
    self.vbo = -1 if not bool(glGenBuffers) else glGenBuffers(1)
    self.buffer = []
    self.color = color
    self.shader_program = shader_program

    self.serial = serial
    self.meshes = meshes

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
    # TODO: Move to more "direct" function calls, e.g.:
    # if not self.serial.is_moving():
    #   self.serial.reverse()
    if self.serial.traj:
      if self.serial.traj.is_done():
        self.serial.traj.reverse()

      self.serial.angles = self.serial.traj.advance(delta)

  def draw(self):
    self.shader_program.model_matrices  = [frame.transform for frame in self.serial.poses()]
    self.shader_program.use_link_colors = False
    self.shader_program.link_colors     = [link.color for link in self.serial.links]
    self.shader_program.robot_color     = self.color

    glBindVertexArray(self.vao)

    glDrawArrays(GL_TRIANGLES, 0, self.buffer.size)

    glBindVertexArray(0)