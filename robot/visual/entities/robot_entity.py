import json, math
import numpy as np

from OpenGL.GL import *

from ctypes import c_void_p

from robot.common.timer                    import Timer
from robot.mech.joint                      import Joint
from robot.mech.link                       import Link
from robot.mech.serial                     import Serial
from robot.spatial.aabb                    import AABB
from robot.spatial.frame                   import Frame
from robot.spatial.kdtree                  import KDTree
from robot.spatial.matrix4                 import Matrix4
from robot.spatial.ray                     import Ray
from robot.spatial.vector3                 import Vector3
from robot.visual.exceptions               import ParserError
from robot.visual.entities.entity          import Entity
from robot.visual.entities.frame_entity    import FrameEntity
from robot.visual.filetypes.stl.stl_parser import STLParser
from robot.visual.mesh                     import Mesh
from robot.visual.shader_program           import ShaderProgram

loaded_files = {}

def parse_mesh(file_path):
  p = STLParser()

  try:
    meshes = p.parse(file_path)
  except ParserError as error:
    print('\033[91m' + f'Parsing error on line {error.line}: {error}' + '\033[0m')
    # TODO: It's probably no longer appropriate for this to be a quit() here
    quit()

  with Timer(f'Construct KD Trees') as t:
    for mesh in meshes:
      mesh.accelerator = KDTree

  return meshes

def get_joint_params(joint_json):
  for joint_params in joint_json:
    for param, value in joint_params.items():
      if param == 'limits':
        value['low'] = math.radians(value['low'])
        value['high'] = math.radians(value['high'])
      elif param in ['alpha', 'theta']:
        joint_params[param] = math.radians(value)
  
  return joint_json

def load(file_path):
  links = []

  cached_result = loaded_files.get(file_path)

  joints = []
  links = []

  if not cached_result:
    with open(file_path) as json_file:  
      data = json.load(json_file)

    meshes = parse_mesh(f'robot/mech/robots/meshes/{data["mesh_file"]}')
    joint_params = get_joint_params(data['joints'])
    link_params = data['links']

    loaded_files[file_path] = {
      'meshes': meshes,
      'joint_params': joint_params,
      'link_params': link_params
    }
  else:
    meshes = cached_result['meshes']
    joint_params = cached_result['joint_params']
    link_params = cached_result['link_params']

  for joint in joint_params:
    joints.append(Joint(**joint))
  for link, mesh in zip(link_params, meshes):
    links.append(Link(link['name'], mesh, link['color']))

  return RobotEntity(Serial(joints, links))

class RobotEntity(Entity):
  def __init__(self, serial : Serial, shader_program : ShaderProgram = None, color = (1, 0.5, 0)):
    self.serial = serial
    self.frame_entity = None
    self.bounding_entity = None

    Entity.__init__(self, shader_program, color)

  @property
  def meshes(self):
    return [link.mesh for link in self.serial.links]

  @property
  def aabb(self):
    return self.serial.aabb

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
    if self.frame_entity:
      self.frame_entity.load()

    if self.bounding_entity:
      self.bounding_entity.load()

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

  def draw(self, camera, light):
    # TODO: Use Uniform Buffer Objects to remove this duplicate code from each entity
    self.shader_program.use()

    self.shader_program.proj_matrix = camera.projection.matrix
    self.shader_program.view_matrix = camera.world_to_camera

    self.shader_program.light_position  = light.position
    self.shader_program.light_color     = light.color
    self.shader_program.light_intensity = light.intensity


    self.shader_program.model_matrices  = [frame.transform for frame in self.serial.poses()]
    self.shader_program.use_link_colors = False
    self.shader_program.link_colors     = [link.color for link in self.serial.links]
    self.shader_program.robot_color     = self.color

    glBindVertexArray(self.vao)

    glDrawArrays(GL_TRIANGLES, 0, self.buffer.size)

    glBindVertexArray(0)

    if self.frame_entity:
      # for link in self.serial.links:
      self.frame_entity.draw(camera, light, Matrix4(self.serial.links[-1].frame.transform))

    if self.bounding_entity:
      for mesh, link in zip(self.meshes, self.serial.links):
        self.bounding_entity.aabb = mesh.aabb
        self.bounding_entity.draw(camera, light, link.frame.transform)

      self.bounding_entity.aabb = self.serial.aabb
      self.bounding_entity.draw(camera, light)