class Animation():
  def __init__(self, duration: float) -> None:
    self.start = 0
    self.stop = 0
    self.duration = duration
    self.elapsed = duration

  def interpolate(self, t: float) -> float:
    '''Interpolate between start and end with 0 <= t <= 1.'''
    slope = self.stop - self.start
    return slope * t + self.start

  @property
  def value(self) -> float:
    t = min(self.elapsed / self.duration, 1)
    return self.interpolate(t)

  def set_end_points(self, start: float, stop: float) -> None:
    self.start = start
    self.stop  = stop

  def reset(self) -> None:
    self.elapsed = 0

  @property
  def is_done(self) -> bool:
    return self.elapsed >= self.duration

  def update(self, delta: float) -> None:
    self.elapsed += delta

  def reverse(self) -> None:
    self.start, self.stop = self.stop, self.start