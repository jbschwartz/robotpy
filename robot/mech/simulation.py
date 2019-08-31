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
    aabb = AABB()
    for entity in self.entities:
      try:
        # TODO: Maybe there's a better way to do this. Or at least I need to put an AABB on all entities (in the entity base class?)
        aabb.expand(entity.aabb)
      except AttributeError:
        pass
    return aabb

  def intersect(self, ray):
    if self.aabb.intersect(ray):
      return ray.closest_intersection(self.entities)
    else:
      return None

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