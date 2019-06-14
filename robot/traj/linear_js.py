from robot.traj.trajectory_js import TrajectoryJS

def interpolate(start, end, t):
  '''
  Interpolate between start and end with 0 <= t <= 1
  '''
  slope = end - start
  return slope * t + start

class LinearJS(TrajectoryJS):
  '''
  Linear trajectory in robot joint space
  '''
  def __init__(self, starts, ends, duration = 1):
    self.starts = starts
    self.ends = ends
    self.duration = duration

    self.position = 0
    self.direction = 1

  def is_done(self):
    return self.position <= 0.0 or self.position >= 1.0 

  def restart(self):
    self.position = 0

  def reverse(self):
    self.direction *= -1

  def advance(self, delta):
    assert delta >= 0

    self.position += self.direction * (delta / self.duration)

    self.position = min(max(self.position, 0), 1)

    return [interpolate(start, end, self.position) for start, end in zip(self.starts, self.ends)]
