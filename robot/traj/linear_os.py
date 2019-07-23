import math

from robot.ik.angles          import solve_angles
from robot.spatial.frame      import Frame
from robot.spatial.quaternion import Quaternion
from robot.spatial.transform  import Transform
from robot.spatial.dual       import Dual
from robot.traj.trajectory_js import TrajectoryJS
from robot.traj.utils         import interpolate

class LinearOS():
  '''
  Linear trajectory in operational space
  '''
  def __init__(self, robot, starts, ends, duration = 1):
    self.starts = starts
    self.ends = ends
    self.duration = duration

    self.interval = 1 / len(self.starts)

    self.t = 0
    self.direction = 1

    self.robot = robot
    self.robot.angles = [0] * 6

    self.f = self.robot.pose()

  def is_done(self):
    return self.t <= 0.0 or self.t >= 1.0

  def restart(self):
    self.t = 0

  def reverse(self):
    self.direction *= -1
    # pass

  def advance(self, delta):
    assert delta >= 0

    self.t += self.direction * (delta / self.duration)

    self.t = min(max(self.t, 0), 1)

    index = math.floor(self.t / self.interval)
    if index == len(self.starts):
      os_position = self.ends[-1]
    else:
      transformed_t = (self.t - index * self.interval) / self.interval

      os_position = interpolate(self.starts[index], self.ends[index], transformed_t)

    t = Quaternion(0, *os_position)
    r = self.f.transform.rotation()
    dual = Dual(r, 0.5 * t * r)

    new_frame = Frame(Transform(dual = dual))

    results = solve_angles(new_frame, self.robot)
    current = self.robot.angles

    least = math.inf
    best = None
    weights = [1, 0.9, 0.8, 0.7, 0.6, 0.5]
    for result in results:
      total = 0
      for a, b, w in zip(result, current, weights):
        total += w * (a - b) ** 2

      if total < least:
        least = total
        best = result

    return best
