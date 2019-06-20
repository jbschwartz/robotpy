from robot.spatial.aabb  import AABB
from robot.spatial.frame import Frame

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