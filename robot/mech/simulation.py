from numbers import Number

from robot.visual.messaging.listener import listen, listener
from robot.visual.messaging.event    import Event

@listener
class Simulation():
  def __init__(self) -> None:
    self.entities = []

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