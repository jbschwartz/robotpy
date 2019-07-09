from robot.spatial.aabb  import AABB
from robot.spatial.frame import Frame
from robot.spatial.ray   import Ray

class Link:
  def __init__(self, name, mesh, color):
    # TODO: Mass, COM, Moments of Inertia
    self.frame = Frame()
    self.name = name
    self.mesh = mesh
    self.color = color

  @property
  def aabb(self):
    aabb = AABB()
    for corner in self.mesh.aabb.corners:
      aabb.extend(self.frame.transform(corner))
    return aabb

  def intersect(self, world_ray : Ray):
    if self.aabb.intersect(world_ray):
      link_to_world = self.frame.transform
      world_to_link = link_to_world.inverse()

      link_ray = world_to_link(world_ray)
      link_point = self.mesh.intersect(link_ray)

      return link_to_world(link_point, type="point")
    
    return None
