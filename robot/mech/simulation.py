import glfw, math, statistics

from collections import deque

from robot.common                    import logger
from spatial                         import AABB, Intersection, Ray
from robot.visual.messaging.listener import listen, listener
from robot.visual.messaging.event    import Event

@listener
class Simulation():
  def __init__(self) -> None:
    self.entities  = []
    self.is_paused = False

    self.tick_samples = deque([], maxlen = 20)

  @property
  def aabb(self) -> AABB:
    """Get the AABB for all simulation entities."""
    aabbs = [
      entity.aabb
      for entity in self.entities
      if hasattr(entity, 'aabb')
    ]

    return AABB(aabbs)

  def intersect(self, ray: Ray) -> Intersection:
    """Intersect a ray with all Simulation entities and return closest found Intersection. Return Intersection.Miss() for no intersection."""
    if not self.aabb.intersect(ray):
      return Intersection.Miss()

    return ray.closest_intersection(self.entities)

  @listen(Event.KEY)
  def pause(self, key, action, modifiers) -> None:
    if key == glfw.KEY_SPACE and action == glfw.PRESS:
      self.is_paused = not self.is_paused
    if key == glfw.KEY_Q and action == glfw.PRESS:
      logger.info(f'Ticks Per Second: {math.floor(statistics.mean(self.tick_samples))}')

  @listen(Event.UPDATE)
  def update(self, delta: float = 0) -> None:
    """Step the simulation forward by a `delta` timestep."""
    if self.is_paused or delta <= 0:
      return

    self.tick_samples.append(1 / delta)

    for entity in self.entities:
      if hasattr(entity, 'traj'):
        result = entity.traj.advance(delta)
        entity.angles = result

        if entity.traj.is_done():
          entity.traj.reverse()
          entity.traj.restart()
