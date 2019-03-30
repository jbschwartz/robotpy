import abc

class TrajectoryJS(abc.ABC):
  @abc.abstractmethod
  def is_done(self):
    pass

  @abc.abstractmethod
  def advance(self, delta):
    pass