import math

from robot.ik.angles          import solve_angles
from robot.spatial.frame      import Frame
from robot.spatial.quaternion import Quaternion
from robot.spatial.transform  import Transform
from robot.spatial.dual       import Dual
from robot.spatial            import vector3
from robot.traj.segment       import ArcSegment, LinearSegment
from robot.traj.trajectory_js import TrajectoryJS
from robot.traj.path          import PiecewisePath
from robot.traj.utils         import interpolate

Vector3 = vector3.Vector3

class LinearOS():
  '''Linear trajectory in operational space.'''
  def __init__(self, robot, waypoints, duration = 1):
    self.path = PiecewisePath.from_waypoints(waypoints)
    self.path.blend(30)

    self.segment_duration = [segment.length / self.path.length * duration for segment in self.path.segments]

    self._segment_index = 0

    self._is_done = False

    self._t = 0

    self.robot = robot
    self.robot.angles = [0] * 6

  @property
  def t(self):
    return self._t

  @t.setter
  def t(self, value):
    self._t = value

  @property
  def segment_index(self):
    return self._segment_index

  @segment_index.setter
  def segment_index(self, value):
    self._segment_index += 1
    if self._segment_index == self.path.number_of_segments:
      self._is_done = True
      self._segment_index = 0

  def is_done(self):
    return self._is_done

  def restart(self):
    self._is_done = False
    self.t = 0

  def reverse(self):
    self.path.reverse()
    self.segment_duration.reverse()

  def get_closest_solution(self, solutions):
    '''Return the closest solution (in joint space) to the current arm position.'''
    current = self.robot.angles

    least    = math.inf
    solution = None

    for angles in solutions:
      joint_space_distance = sum([(new - current) ** 2
                                  for new, current in zip(angles, current)])

      if joint_space_distance < least:
        least    = joint_space_distance
        solution = angles

    return solution

  def advance(self, delta):
    assert delta >= 0

    if self._is_done:
      return self.robot.angles

    self.t += (delta / self.segment_duration[self.segment_index])

    if self.t > 1:
      self.t -= 1
      self.segment_index += 1

    world_position = self.path.evaluate(self.segment_index, self.t)
    target = Frame.from_position_orientation(world_position, self.robot.pose().orientation())

    solutions = solve_angles(target, self.robot)

    return self.get_closest_solution(solutions)