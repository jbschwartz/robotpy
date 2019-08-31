from typing import Optional

import glfw

from robot.spatial                   import AABB, Ray
from robot.visual.messaging.listener import listen, listener
from robot.visual.messaging.event    import Event

@listener
class Simulation():
  def __init__(self) -> None:
    self.entities  = []
    self.is_paused = False

  @property
  def aabb(self) -> AABB:
    """Get the AABB for all simulation entities."""
    aabbs = [
      entity.aabb
      for entity in self.entities
      if hasattr(entity, 'aabb')
    ]

    return AABB.from_aabbs(aabbs)

  def intersect(self, ray: Ray) -> Optional[float]:
    """Return the parametric distance along the ray to intersection with the nearest simulation entity, if any."""
    if not self.aabb.intersect(ray):
      return None

    return ray.closest_intersection(self.entities)

  @listen(Event.KEY)
  def pause(self, key, action, modifiers) -> None:
    if key == glfw.KEY_SPACE and action == glfw.PRESS:
      self.is_paused = not self.is_paused

  @listen(Event.START_FRAME)
  def update(self, delta: float = 0) -> None:
    """Step the simulation forward by a `delta` timestep."""
    if self.is_paused:
      return

    for entity in self.entities:
      if entity.traj:
        result = entity.traj.advance(delta)
        entity.angles = result

      if entity.traj.is_done():
        entity.traj.reverse()
        entity.traj.restart()