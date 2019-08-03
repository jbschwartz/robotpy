import math

from robot.spatial.aabb      import AABB
from robot.spatial.frame     import Frame
from robot.spatial.ray       import Ray
from robot.spatial.transform import Transform
from robot.spatial.vector3   import Vector3

class Link:
  def __init__(self, name, joint, mesh, color):
    # TODO: Mass, Moments of Inertia
    self.to_world = Transform.Identity()
    self.joint = joint
    self.name = name
    self.mesh = mesh
    self.color = color

    self.properties = {
      'com':     None,
      'moments': None,
      'volume':  None
    }

  @property
  def frame(self) -> Frame:
    return Frame(self.to_world)

  @frame.setter
  def frame(self, frame) -> None:
    self.to_world = frame.frame_to_world

  @property
  def aabb(self):
    return AABB(*[self.to_world(corner) for corner in self.mesh.aabb.corners])

  @property
  def center_of_mass(self):
    if not self.properties['com']:
      self.calculate_properties()

    return self.properties['com']

  @property
  def moments(self):
    if not self.properties['moments']:
      self.calculate_properties()

    return self.properties['moments']

  @property
  def volume(self):
    if not self.properties['volume']:
      self.calculate_properties()

    return self.properties['volume']

  def calculate_properties(self):
    '''Calculate the volume, moments, and center of mass (assuming uniform density) of the mesh.'''
    def tetrahedron_volume(facet):
      '''Volume of a tetrahedron created by the three facet vertices and origin.'''
      a, b, c = facet.vertices
      return (a * (b % c)) / 6

    def tetrahedron_centroid(facet):
      '''Volume of a tetrahedron created by the three facet vertices and origin.'''
      return sum(facet.vertices, Vector3()) / 4

    mesh_volume   = 0
    mesh_centroid = Vector3()

    moments = {
      'ixx': 0,
      'iyy': 0,
      'izz': 0,
      'ixy': 0,
      'iyz': 0,
      'ixz': 0
    }

    for facet in self.mesh.facets:
      volume = tetrahedron_volume(facet)
      centroid = tetrahedron_centroid(facet)

      mesh_volume   += volume
      mesh_centroid += volume * centroid

      sq = Vector3(
        centroid.x * centroid.x,
        centroid.y * centroid.y,
        centroid.z * centroid.z
      )

      moments['ixx'] += (sq.y + sq.z) * volume
      moments['iyy'] += (sq.x + sq.z) * volume
      moments['izz'] += (sq.x + sq.y) * volume
      moments['ixy'] -= (centroid.x * centroid.y * volume)
      moments['iyz'] -= (centroid.y * centroid.z * volume)
      moments['ixz'] -= (centroid.x * centroid.z * volume)

    self.properties['com']     = mesh_centroid / mesh_volume
    self.properties['volume']  = mesh_volume
    self.properties['moments'] = moments

  def intersect(self, world_ray : Ray):
    if self.aabb.intersect(world_ray):
      world_to_link = self.to_world.inverse()

      return self.mesh.intersect(world_ray.transform(world_to_link))

    return None

  def update_transform(self, previous_link_transform) -> Transform:
    """Update and return link transform from it's previous neighbor's transform."""
    self.to_world =  previous_link_transform * self.joint.transform
    return self.to_world