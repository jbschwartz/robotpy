import math

from collections import namedtuple
from typing      import Iterable, Optional

from robot.spatial import AABB, Intersection, Mesh, Ray, Transform, Vector3
from .joint        import Joint

PhysicalProperties = namedtuple('PhysicalProperties', 'com moments volume', defaults=(None, None, None))

Moments = namedtuple('Moments', 'ixx iyy izz ixy iyz ixz', defaults=(0,) * 6)

class Link:
  def __init__(self, name: str, joint: Joint, mesh: Mesh, color: Iterable[float]) -> None:
    # TODO: Mass/density
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
  def aabb(self) -> AABB:
    """Return the Link Mesh's AABB in world space."""
    return AABB.from_points([self.to_world(corner) for corner in self.mesh.aabb.corners])

  @property
  def properties(self) -> PhysicalProperties:
    """Return the computed physical Link properties (e.g., center of mass, volume) in world space."""
    if any([value is None for value in self._properties]):
      self.calculate_properties()

    return PhysicalProperties(
      com     = self.to_world(self._properties.com),
      moments = self._properties.moments,
      volume  = self._properties.volume
    )

  def calculate_properties(self) -> None:
    """Calculate the center of mass, moments, and volume of the Mesh.

    The calculations assume a uniform density where relevant (center of mass)."""
    def tetrahedron_volume(facet):
      """Volume of a tetrahedron created by the three facet vertices and origin."""
      a, b, c = facet.vertices
      return (a * (b % c)) / 6

    def tetrahedron_centroid(facet):
      """Volume of a tetrahedron created by the three facet vertices and origin."""
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
      moments = Moments(**moments),
      volume  = mesh_volume
    )

  def intersect(self, world_ray: Ray) -> Intersection:
    """Intersect a ray with Link and return closest found Intersection. Return Intersection.Miss() for no intersection."""
    if not self.aabb.intersect(world_ray):
      return Intersection.Miss()

    world_to_link = self.to_world.inverse()

    facet = self.mesh.intersect(world_ray.transform(world_to_link))
    return Intersection.from_previous(self, facet)