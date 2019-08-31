from numbers import Number

from robot.spatial                   import AABB
from robot.visual.messaging.listener import listen, listener
from robot.visual.messaging.event    import Event

@listener
class Simulation():
  def __init__(self) -> None:
    self.entities = []

  @property
  def aabb(self):
    aabbs = [
      entity.aabb
      for entity in self.entities
      if hasattr(entity, 'aabb')
    ]

    return AABB.from_aabbs(aabbs)

  def intersect(self, ray):
    if not self.aabb.intersect(ray):
      return None

    return ray.closest_intersection(self.entities)


  @listen(Event.UPDATE)
  def update(self, delta: Number = 0) -> None:
    """Step the simulation forward by a `delta` timestep."""
    for entity in self.entities:
      if entity.traj:
        result = entity.traj.advance(delta)
        entity.angles = result

      if entity.traj.is_done():
        entity.traj.reverse()
        entity.traj.restart()