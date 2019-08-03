import math

from collections import namedtuple

from robot.mech.joint        import Joint
from robot.spatial.aabb      import AABB
from robot.spatial.frame     import Frame
from robot.spatial.ray       import Ray
from robot.spatial.transform import Transform
from robot.spatial.vector3   import Vector3
from robot.visual.mesh       import Mesh

PhysicalProperties = namedtuple('PhysicalProperties', 'com moments volume', defaults=(None, None, None))

class Link:
  def __init__(self, name, joint, mesh, color):
    # TODO: Mass, Moments of Inertia
    # Previous links DH frame transformation
    self.previous = Transform.Identity()
    self.joint = joint
    self.name = name
    self.mesh = mesh
    self.color = color

    self._properties = PhysicalProperties()

  @classmethod
  def from_dict_mesh(cls, d: dict, mesh: Mesh) -> 'Link':
    """Construct a Link from a dictionary of parameters."""
    joint = Joint.Immovable() if d.get('joint', None) is None else Joint.from_dict(d['joint'])

    return cls(d.get('name', None), joint, mesh, d.get('color', None))

  @property
  def to_world(self) -> Transform:
    """Return the DH frame transformation.

    That is, the transformation from the previous link's frame to this link's frame.
    """
    return self.previous * self.joint.transform

  @property
  def frame(self) -> Frame:
    return Frame(self.to_world)

  @property
  def aabb(self):
    return AABB(*[self.to_world(corner) for corner in self.mesh.aabb.corners])

  @property
  def properties(self):
    if any([value is None for value in self._properties]):
      self.calculate_properties()

    return self._properties

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

    self._properties = PhysicalProperties(
      com     = mesh_centroid / mesh_volume,
      volume  = mesh_volume,
      moments = moments
    )

  def intersect(self, world_ray : Ray):
    if self.aabb.intersect(world_ray):
      world_to_link = self.to_world.inverse()

      return self.mesh.intersect(world_ray.transform(world_to_link))

    return None