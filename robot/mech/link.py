import math

from robot.spatial.aabb  import AABB
from robot.spatial.frame import Frame
from robot.spatial.ray   import Ray

class Link:
  def __init__(self, name, mesh, color):
    # TODO: Mass, Moments of Inertia
    self.frame = Frame()
    self.name = name
    self.mesh = mesh
    self.com = mesh.center_of_mass
    self.volume = mesh.volume
    self.color = color

  @property
  def aabb(self):
    return AABB(*[self.frame.transform(corner) for corner in self.mesh.aabb.corners])

  def intersect(self, world_ray : Ray):
    if self.aabb.intersect(world_ray):
      world_to_link = self.frame.transform.inverse()

      return self.mesh.intersect(world_to_link(world_ray))

    return None
